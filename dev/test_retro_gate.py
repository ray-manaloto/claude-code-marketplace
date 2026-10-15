"""Public-CLI controls for dev/retro_gate.py (stdlib only, hermetic Git)."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "dev" / "retro_gate.py"
FIXTURES = ROOT / "dev" / "fixtures" / "retros"
CORPUS = ROOT / ".planning" / "2026-10-10-marketplace-macos-reflection-scaffold" / "retros"
SELECTORS = ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "MARKETPLACE_PYTHON")
SCRUBBED = SELECTORS + ("RETRO_UNIT", "CLAUDE_LANE_UNIT", "PLAN_ID", "PWF_PLAN_ROOT")
PLAN = "test-plan"
# The git binary itself, ahead of any version-manager shim.
GIT_DIR = subprocess.run(["git", "--exec-path"], capture_output=True, text=True, check=True).stdout.strip()


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED and not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    env.update(extra)
    return env


def gate(*args, cwd=None, env=None):
    result = subprocess.run([sys.executable, "-I", str(GATE), *args], cwd=cwd or ROOT,
                            env=env or clean_env(), capture_output=True, text=True, timeout=30)
    return result.returncode, result.stdout.splitlines(), result.stderr


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                    "-c", "commit.gpgsign=false", *args], check=True, capture_output=True,
                   env=clean_env(), timeout=30)


def fake_git(directory, marker, name="git"):
    """A stand-in for a mise shim: records each call in `marker`, then runs the real git."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(f'#!/bin/sh\necho "$@" >> "{marker}"\nexec "{Path(GIT_DIR, "git")}" "$@"\n')
    (directory / name).chmod(0o755)
    return directory / name


class RetroGateCli(unittest.TestCase):
    def check(self, name, *extra):
        return gate("--record", str(FIXTURES / name), *extra)

    def test_complete_record_passes(self):
        rc, out, _ = self.check("complete.md")
        self.assertEqual(rc, 0, out)
        self.assertTrue(out[0].startswith("RETRO GATE PASSED"), out)

    def test_open_finding_with_owner_passes(self):
        rc, out, _ = self.check("open-finding-with-owner.md")
        self.assertEqual(rc, 0, out)

    def test_missing_category_names_it(self):
        rc, out, _ = self.check("missing-category.md")
        self.assertEqual(rc, 2)
        self.assertIn(" - category not addressed: tool economy", out)
        self.assertEqual(sum(line.startswith(" - ") for line in out), 1, out)

    def test_open_finding_without_owner_is_refused(self):
        rc, out, _ = self.check("open-finding-without-owner.md")
        self.assertEqual(rc, 2)
        reasons = [line for line in out if line.startswith(" - ")]
        self.assertEqual(len(reasons), 1, out)
        self.assertTrue(reasons[0].startswith(" - open finding without owner/blocker: | P2 |"), reasons)

    def test_no_evidence_is_refused(self):
        rc, out, _ = self.check("no-evidence.md")
        self.assertEqual(rc, 2)
        self.assertEqual([line for line in out if line.startswith(" - ")],
                         [" - no verification binding (exit code, PASS, SHA-256 or named check) found"])

    def test_wrapped_category_counts_and_prose_pass_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            wrapped = Path(tmp, "wrapped.md")
            wrapped.write_text((FIXTURES / "complete.md").read_text().replace("Tool economy:", "Tool\neconomy:"))
            self.assertEqual(gate("--record", str(wrapped))[0], 0)
            prose = Path(tmp, "prose.md")
            prose.write_text((FIXTURES / "no-evidence.md").read_text() + "Publication must pass named checks.\n")
            rc, out, _ = gate("--record", str(prose))
            self.assertEqual(rc, 2)
            self.assertIn(" - no verification binding (exit code, PASS, SHA-256 or named check) found", out)

    def test_oversized_record_is_refused_before_reading(self):
        with tempfile.TemporaryDirectory() as tmp:
            big = Path(tmp, "big.md")
            big.write_text((FIXTURES / "complete.md").read_text() + "x" * (1 << 20))
            rc, out, _ = gate("--record", str(big))
            self.assertEqual(rc, 2)
            self.assertEqual([line for line in out if line.startswith(" - ")],
                             [" - retro record larger than 1 MiB"])

    def test_stub_reports_every_reason(self):
        rc, out, _ = self.check("stub.md")
        self.assertEqual(rc, 2)
        reasons = [line for line in out if line.startswith(" - ")]
        self.assertIn(" - retro record is shorter than 200 characters", reasons)
        self.assertEqual(sum("category not addressed" in r for r in reasons), 7, reasons)
        self.assertTrue(any("no verification binding" in r for r in reasons), reasons)

    def test_missing_record_and_usage_errors(self):
        rc, out, _ = gate("--record", str(FIXTURES / "absent.md"))
        self.assertEqual(rc, 2)
        self.assertTrue(out[1].startswith(" - retro record missing:"), out)
        with tempfile.TemporaryDirectory() as tmp:
            rc, out, err = gate("--repo", tmp, cwd=tmp)  # not a Git repo, no unit source
            self.assertEqual(rc, 1, (out, err))
            self.assertIn("--unit", err)
        rc, _, err = gate("--no-such-flag")
        self.assertEqual(rc, 1, err)

    def test_selector_names_are_last_line_without_values(self):
        rc, out, _ = gate("--record", str(FIXTURES / "complete.md"),
                          env=clean_env(VIRTUAL_ENV="/secret/venv", MARKETPLACE_PYTHON="/x/python"))
        self.assertEqual(rc, 0)
        self.assertEqual(out[-1], "selectors: VIRTUAL_ENV MARKETPLACE_PYTHON")
        self.assertNotIn("/secret/venv", "\n".join(out))
        _, out, _ = gate("--record", str(FIXTURES / "stub.md"))
        self.assertEqual(out[-1], "selectors: none")
        rc, out, _ = gate("--no-such-flag", env=clean_env(UV_PROJECT_ENVIRONMENT="x"))
        self.assertEqual((rc, out[-1]), (1, "selectors: UV_PROJECT_ENVIRONMENT"))

    def test_all_over_fixtures(self):
        rc, out, _ = gate("--all", str(FIXTURES))
        self.assertEqual(rc, 2)
        verdicts = {line.split()[1]: line.split()[0] for line in out if line.split()[0] in ("PASS", "FAIL")}
        self.assertEqual(verdicts, {
            "complete.md": "PASS", "open-finding-with-owner.md": "PASS", "missing-category.md": "FAIL",
            "open-finding-without-owner.md": "FAIL", "no-evidence.md": "FAIL", "stub.md": "FAIL"})
        self.assertIn("4 failing of 6", out)
        self.assertTrue(out[-1].startswith("selectors: "))

    def test_real_corpus_records_pass(self):
        for name in ("m0-remaining-work-merge.md", "codex-session-history.md", "A01.md"):
            rc, out, _ = gate("--record", str(CORPUS / name))
            self.assertEqual(rc, 0, (name, out))
        # A04 ("scans pending entries ... reviewer PASS") and acceptance-frontier ("| #29 ...") rows are
        # resolved; both records still fail on other reasons (a missing category / no binding).
        for name in ("A04.md", "acceptance-frontier.md"):
            _, out, _ = gate("--record", str(CORPUS / name))
            self.assertFalse([line for line in out if "open finding" in line], (name, out))


class RetroGateUnitDerivation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template_dir = tempfile.TemporaryDirectory()
        cls.template = Path(cls.template_dir.name) / "repo"
        retros = cls.template / ".planning" / PLAN / "retros"
        retros.mkdir(parents=True)
        shutil.copy(FIXTURES / "complete.md", retros / "x.md")
        shutil.copy(FIXTURES / "stub.md", retros / "z.md")
        git(cls.template, "init", "-q", "-b", "main")
        git(cls.template, "add", ".")
        git(cls.template, "commit", "-q", "-m", "base")

    @classmethod
    def tearDownClass(cls):
        cls.template_dir.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "repo"
        shutil.copytree(self.template, self.repo, symlinks=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_gate(self, *args, **env):
        return gate("--plan-id", PLAN, *args, cwd=self.repo, env=clean_env(**env))

    def test_unit_from_branch_name(self):
        git(self.repo, "checkout", "-q", "-b", "claude/x-y")
        rc, out, _ = self.run_gate()
        self.assertEqual(rc, 0, out)
        self.assertTrue(out[0].endswith(str(Path(".planning", PLAN, "retros", "x.md"))), out)

    def test_env_unit_beats_branch(self):
        git(self.repo, "checkout", "-q", "-b", "claude/x-y")
        rc, out, _ = self.run_gate(RETRO_UNIT="z")
        self.assertEqual(rc, 2, out)
        self.assertIn("z.md", out[0])

    def test_underivable_branch_is_usage_error(self):
        git(self.repo, "checkout", "-q", "-b", "codex/q-r")
        rc, _, err = self.run_gate()
        self.assertEqual(rc, 1, err)
        self.assertIn("unit could not be derived; pass --unit or --branch", err)

    def test_explicit_branch_and_name_rev_suffixes(self):
        for branch, expected in (("claude/x-y", 0), ("remotes/origin/claude/x-y~2^2~1", 0), ("claude/z-w^", 2)):
            rc, out, _ = self.run_gate("--repo", str(self.repo), "--branch", branch)
            self.assertEqual(rc, expected, (branch, out))
            self.assertIn("x.md" if expected == 0 else "z.md", out[0])
        for branch in ("main", "codex/q-r"):
            rc, _, err = self.run_gate("--repo", str(self.repo), "--branch", branch)
            self.assertEqual(rc, 1, (branch, err))
            self.assertIn("unit could not be derived; pass --unit or --branch", err)

    def test_lane_record_names_unit_for_branch(self):
        lanes = self.repo / ".planning" / PLAN / "lanes"
        lanes.mkdir()
        (lanes / "q.json").write_text('{"unit": "z", "branch": "codex/q-r"}')
        (lanes / "w.json").write_text('{"unit": "w", "branch": "codex/w-v"}')
        rc, out, _ = self.run_gate("--repo", str(self.repo), "--branch", "codex/q-r")
        self.assertEqual(rc, 2, out)
        self.assertIn("z.md", out[0])
        rc, out, _ = self.run_gate("--repo", str(self.repo), "--branch", "codex/w-v")
        self.assertEqual(rc, 2, out)
        self.assertTrue(out[1].startswith(" - retro record missing:"), out)

    def test_from_merge_head(self):
        rc, _, err = self.run_gate("--from-merge-head")
        self.assertEqual(rc, 1, err)
        self.assertIn("no merge in progress", err)
        git(self.repo, "checkout", "-q", "-b", "claude/x-y")
        (self.repo / "lane.txt").write_text("lane\n")
        git(self.repo, "add", "lane.txt")
        git(self.repo, "commit", "-q", "-m", "lane")
        git(self.repo, "checkout", "-q", "main")
        git(self.repo, "merge", "-q", "--no-ff", "--no-commit", "claude/x-y")
        self.assertTrue((self.repo / ".git" / "MERGE_HEAD").exists())
        rc, out, _ = self.run_gate("--from-merge-head")
        self.assertEqual(rc, 0, out)
        self.assertIn("x.md", out[0])

    def shims(self):
        """A `mise/shims` directory and a relocated one whose git links to the mise binary."""
        marker = Path(self.tmp.name, "shim-calls")
        shims = fake_git(Path(self.tmp.name, "data", "mise", "shims"), marker).parent
        relocated = Path(self.tmp.name, "custom", "bin")
        relocated.mkdir(parents=True)
        (relocated / "git").symlink_to(fake_git(Path(self.tmp.name, "tool"), marker, name="mise"))
        return marker, os.pathsep.join([str(shims), str(relocated)])

    def test_branch_derivation_skips_mise_shims_ahead_of_git(self):
        git(self.repo, "checkout", "-q", "-b", "claude/x-y")
        marker, shims = self.shims()
        rc, out, _ = self.run_gate(PATH=os.pathsep.join([shims, GIT_DIR]))
        self.assertEqual(rc, 0, out)
        self.assertIn("x.md", out[0])
        self.assertFalse(marker.exists(), "the retro gate executed a mise shim")

    def test_git_resolver_matches_the_hook_copy(self):
        """dev/hooks/git_gate.py keeps the same resolver with no shared import; the code after the docstring stays identical."""
        def body(path):
            text = (ROOT / path).read_text()
            start = text.index("def git_executable()")
            return text[text.index('"""', text.index('"""', start) + 3) + 3:text.index("\ndef git(", start)]
        self.assertEqual(body("dev/retro_gate.py"), body("dev/hooks/git_gate.py"))

    def test_only_shims_on_path_still_derive_the_unit_through_the_shim(self):
        git(self.repo, "checkout", "-q", "-b", "claude/z-w")
        marker, shims = self.shims()
        rc, out, _ = self.run_gate(PATH=shims)
        self.assertEqual(rc, 2, out)
        self.assertIn("z.md", out[0])
        self.assertTrue(marker.exists(), "with no other git the retro gate runs the mise shim")


if __name__ == "__main__":
    unittest.main()
