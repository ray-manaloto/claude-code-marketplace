"""Doctor core contract (C3 §Design constraints, §Doctor task spec), detectors A/C/I and wiring; scratch Git only."""

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "dev" / "doctor" / "cli.py"
FIXTURES = ROOT / "dev" / "fixtures" / "doctor" / "settings"
PLAN = "2026-10-10-marketplace-macos-reflection-scaffold"
GIT_DIR = subprocess.run(["git", "--exec-path"], capture_output=True, text=True, check=True).stdout.strip()


class Scratch(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.home, self.repo = self.tmp / "home", self.tmp / "repo"
        self.home.mkdir()
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith(("GIT_", "MISE_", "CLAUDE_")) and k not in ("PLAN_ID", "VIRTUAL_ENV")}
        self.env.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / ".config"),
                        PATH=os.pathsep.join([GIT_DIR, self.env.get("PATH", "")]),
                        GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t",
                        GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
                        GIT_COMMITTER_EMAIL="t@example.invalid")
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.write("a.txt", "base\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")

    def git(self, *args):
        result = subprocess.run(["git", *args], cwd=self.repo, env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"git {args}: {result.stderr}")
        return result.stdout

    def write(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def settings(self, data, name="settings.json"):
        self.write(f".claude/{name}", data if isinstance(data, str) else json.dumps(data))

    def doctor(self, *args, stdin="", repo=True):
        argv = [sys.executable, "-I", str(CLI), *(["--repo", str(self.repo)] if repo else []), *args]
        result = subprocess.run(argv, input=stdin, cwd=self.tmp, env=self.env, capture_output=True, text=True,
                                timeout=30)
        return result.returncode, result.stdout, result.stderr

    def report(self, surface="check"):
        rc, out, err = self.doctor("--surface", surface, "--json")
        return rc, json.loads(out)

    def ids(self, surface="check"):
        return sorted((f["id"], f["subject"]) for f in self.report(surface)[1]["findings"])


class Contract(Scratch):
    def test_doctor_cli_exit_codes(self):
        """C3 exit codes: 0 clean, 2 on P1/P2, 1 usage, 3 detector raised; the hook form always 0."""
        rc, report = self.report()
        self.assertEqual((rc, report["schema"], report["findings"]), (0, "doctor/v1", []))
        self.assertEqual(self.doctor("--surface", "nowhere")[0], 1)
        self.settings({"permissions": {"allow": ["placeholder"]}})
        self.assertEqual(self.doctor("--surface", "check")[0], 2)
        self.settings({"enabledPlugins": {"x@m": True}})  # a P2 alone (undeclared marketplace) exits 2 too
        rc, report = self.report()
        self.assertEqual((rc, [f["severity"] for f in report["findings"]]), (2, ["P2"]))
        self.settings("{not json")
        rc, report = self.report()
        self.assertEqual(rc, 3)
        self.assertIn("doctor.detector-error", [f["id"] for f in report["findings"]])
        self.assertEqual(self.doctor("--surface", "session-start", "--format", "context")[0], 0)
        rc, out, _ = self.doctor("--surface", "check", "--json", "--budget-ms", "0")
        report = json.loads(out)
        self.assertEqual((rc, report["findings"]), (0, []))
        self.assertTrue(report["skipped"])
        self.assertTrue(all(s["severity"] == "skipped" and "budget" in s["subject"] for s in report["skipped"]))
        rc, _, err = self.doctor("--surface", "pre-commit", "--budget-ms", "0")  # a guard fails closed
        self.assertEqual(rc, 2, err)
        self.assertIn("skipped doctor.skipped settings: budget 0 ms", err)
        self.assertEqual(self.git("status", "--porcelain", "--ignored"), "?? .claude/\n")  # writes nothing


class SettingsComposition(Scratch):
    NON_PROJECT, MARKETPLACE = "I.settings-non-project-key", "I.settings-plugin-undeclared-marketplace"

    def test_settings_personal_keys_flagged(self):
        """C3 I / T-I1: the staged e12cf04 shape -> permissions + one finding per undeclared marketplace."""
        self.settings((FIXTURES / "staged.json").read_text())
        rc, _ = self.report()
        self.assertEqual(rc, 2)
        everyone = ["astral-sh", "brentmitchell25", "claude-community", "mattpocock", "openai-codex",
                    "planning-with-files"]
        self.assertEqual(self.ids(), [(self.NON_PROJECT, "permissions"), *((self.MARKETPLACE, m) for m in everyone)])
        self.settings((FIXTURES / "before-ct02.json").read_text())  # the C3 "8 -> 4 undeclared" count
        personal = ["additionalDirectories", "disableClaudeAiConnectors", "permissions", "prefersReducedMotion",
                    "switchModelsOnFlag", "teammateMode"]
        self.assertEqual(self.ids(), [*((self.NON_PROJECT, k) for k in personal),
                                      *((self.MARKETPLACE, m) for m in everyone[:4])])

    def test_settings_recommended_file_is_clean(self):
        """C3 I: the committed R5 §B project file, with an excluded local file -> no findings."""
        self.settings((ROOT / ".claude" / "settings.json").read_text())
        self.settings({"permissions": {}}, "settings.local.json")
        self.write(".git/info/exclude", ".claude/settings.local.json\n")
        self.assertEqual(self.report()[0], 0)
        self.assertEqual(self.ids(), [])

    def test_settings_local_not_excluded_flagged(self):
        """C3 I: a settings.local.json that Git would add is P1 until .git/info/exclude names it."""
        self.settings({"permissions": {}}, "settings.local.json")
        self.assertEqual(self.ids(), [("I.settings-local-not-excluded", ".claude/settings.local.json")])
        self.write(".git/info/exclude", ".claude/settings.local.json\n")
        self.assertEqual(self.ids(), [])

    def test_live_project_settings_hold_wave0_keys(self):
        """C2 T-A6 / W0-1: the committed project file holds the wave-0 keys and only project keys."""
        live = json.loads((ROOT / ".claude" / "settings.json").read_text())
        self.assertIs(live["autoCompactEnabled"], True)
        self.assertEqual((live["autoCompactWindow"], live["env"]["PLAN_ID"]),
                         (433000, "2026-10-10-marketplace-macos-reflection-scaffold"))
        self.assertLessEqual(set(live), {"$schema", "env", "autoCompactEnabled", "autoCompactWindow",
                                         "enabledPlugins", "extraKnownMarketplaces", "hooks"})


class ContextBudget(Scratch):
    def context(self):
        rc, out, _ = self.doctor("--surface", "session-start", "--format", "context")
        self.assertEqual(rc, 0)
        return out.splitlines()

    def test_thresholds_below_autocompact_window_and_match_frontier_ceiling(self):
        """C4 required change 4 / D29: one threshold dict, all below autoCompactWindow, fork_deny = lane ceiling."""
        spec = importlib.util.spec_from_file_location("doctor_budget", ROOT / "dev" / "doctor" / "budget.py")
        budget = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(budget)
        self.assertEqual(budget.THRESHOLDS, {"warn": 220_000, "checkpoint": 303_000, "fork_deny": 275_000,
                                             "hard": 358_000})
        window = json.loads((ROOT / ".claude" / "settings.json").read_text())["autoCompactWindow"]
        # D190: compaction fires at window - 33K (20K output reserve + 13K buffer; R23 section 1).
        self.assertTrue(all(value < window - 33_000 for value in budget.THRESHOLDS.values()))
        frontier = tomllib.loads((ROOT / ".planning" / "2026-10-10-marketplace-macos-reflection-scaffold" /
                                  "frontier.toml").read_text())
        self.assertEqual(budget.THRESHOLDS["fork_deny"],
                         frontier["context_ceiling_fraction"] * frontier["windows"]["opus"])

    def test_team_guide_budget_table_equals_thresholds(self):
        """w0-docs retro deferral: the claude-team.md Context budget table and budget.THRESHOLDS state one set."""
        spec = importlib.util.spec_from_file_location("doctor_budget", ROOT / "dev" / "doctor" / "budget.py")
        budget = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(budget)
        guide = (ROOT / "docs" / "agents" / "claude-team.md").read_text()
        table = {name: int(k) * 1000 for name, k in re.findall(r"^\| (\w+) \| (\d+)K \|", guide, re.M)}
        self.assertEqual(table, budget.THRESHOLDS)

    def test_autocompact_line_reports_both_booleans(self):
        """C2 T-A5 / D21: user false + project true -> one `auto-compact:` line naming both; the project file rules."""
        (self.home / ".claude").mkdir()
        (self.home / ".claude" / "settings.json").write_text(json.dumps({"autoCompactEnabled": False}))
        self.settings({"autoCompactEnabled": True})
        (line,) = [line for line in self.context() if "auto-compact:" in line]
        self.assertIn("user=false", line)
        self.assertIn("project=true", line)
        self.assertEqual(self.ids("session-start"), [])

    def test_autocompact_off_follows_settings_precedence(self):
        """A.autocompact-off reads the ruling settings file (local > project > personal copies), never a document."""
        (self.home / ".claude").mkdir()
        (self.home / ".claude" / "settings.json").write_text(json.dumps({"autoCompactEnabled": False}))
        self.write("docs/agents/claude-team.md", "Keep `autoCompactEnabled` on: D21.\n")
        self.assertEqual(self.ids("session-start"), [("A.autocompact-off", "autoCompactEnabled=false in user")])
        self.settings({"autoCompactEnabled": True})
        self.settings({"autoCompactEnabled": False}, "settings.local.json")
        self.write(".git/info/exclude", ".claude/settings.local.json\n")
        self.assertEqual(self.ids("session-start"), [("A.autocompact-off", "autoCompactEnabled=false in local")])

    def test_autocompact_line_defaults_on_without_settings(self):
        """C2 T-A5 twin: no settings file sets the key -> `auto-compact: default(on)`."""
        self.assertIn("auto-compact: default(on)", "\n".join(self.context()))
        self.assertEqual(self.ids("session-start"), [])


class LaneMerge(Scratch):
    def setUp(self):
        super().setUp()
        self.write(f".planning/{PLAN}/lanes/x.json", json.dumps({"unit": "x", "branch": "claude/x-y"}))
        self.write("a.txt", "1\n2\n3\n4\n5\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "allocate x")
        self.git("checkout", "-q", "-b", "claude/x-y")
        self.write("lane.txt", "lane work\n")
        self.write("a.txt", "1\n2\n3\n4\nlane\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "lane work")
        self.git("checkout", "-q", "main")
        self.write("a.txt", "main\n2\n3\n4\n5\n")  # a clean auto-merge: its blob is in neither parent
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "main moves")

    def start_merge(self):
        self.git("merge", "--no-ff", "--no-commit", "claude/x-y")


class Integration(LaneMerge):
    def test_integration_clean_checkout_no_findings(self):
        """C3 C: no MERGE_HEAD -> no class C finding on any surface."""
        self.assertEqual(self.ids("session-start"), [])

    def test_integration_merge_in_progress_reported_once(self):
        """C3 C: an uncommitted lane merge -> one P1 naming the lane, no foreign hunk; never on `check`."""
        self.start_merge()
        rc, report = self.report("session-start")
        (merge,) = report["findings"]
        self.assertEqual((rc, merge["id"], merge["severity"]), (2, "C.merge-in-progress", "P1"))
        self.assertIn("claude/x-y (lane x)", merge["subject"])
        self.assertIn("2 staged paths", merge["evidence"])
        self.assertEqual(self.ids("check"), [])

    def test_integration_foreign_hunk_detected_and_declared(self):
        """C3 C: a staged blob in neither parent nor their merge -> C.foreign-hunk until MERGE_MSG declares it."""
        self.start_merge()
        self.write("lane.txt", "a third content\n")
        self.git("add", "lane.txt")
        found = self.report("session-start")[1]["findings"]  # sorted P1 before P2
        self.assertEqual([(f["id"], f["subject"]) for f in found][1:], [("C.foreign-hunk", "lane.txt")])
        self.assertEqual(found[0]["id"], "C.merge-in-progress")
        message = self.repo / ".git" / "MERGE_MSG"
        message.write_text(message.read_text() + "\nparent hunk: lane.txt\n")
        self.assertEqual([i for i, _ in self.ids("session-start")], ["C.merge-in-progress"])


class SessionStartBlock(LaneMerge):
    def block(self):
        payload = json.dumps({"hook_event_name": "SessionStart", "source": "startup", "cwd": str(self.repo)})
        rc, out, err = self.doctor("--surface", "session-start", "--format", "context", stdin=payload, repo=False)
        self.assertEqual((rc, err), (0, ""))
        self.assertLessEqual(len(out.encode()), 2500)
        lines = out.splitlines()
        self.assertLessEqual(len(lines), 30)
        self.assertTrue(lines[0].startswith("[doctor] checkout ") and str(self.repo.resolve()) in lines[0], lines)
        self.assertTrue(lines[1].startswith("branch main · HEAD "), lines)
        self.assertTrue(lines[-1].startswith("findings P1 "), lines)
        return lines

    def test_session_start_context_block_shape(self):
        """C3 §SessionStart context block: <= 30 lines / 2.5 KB, MERGE pair on lines 3-4, ends with findings."""
        self.assertEqual([line.split(":")[0] for line in self.block()[2:-1]], ["context"])  # clean: standing lines
        self.start_merge()
        self.settings({"permissions": {}})
        lines = self.block()
        self.assertTrue(lines[2].startswith("MERGE IN PROGRESS: MERGE_HEAD "), lines)
        self.assertTrue(lines[3].startswith("  resume: "), lines)
        self.assertIn("settings: non-project-key permissions", lines)
        self.assertTrue(lines[-1].startswith("findings P1 2 · P2 0 · P3 0"), lines)


if __name__ == "__main__":
    unittest.main()
