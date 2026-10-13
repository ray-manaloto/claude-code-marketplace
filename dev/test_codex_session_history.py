"""Hermetic tests for the codex-session-history skill scripts.

Every script runs in a `python3 -I` subprocess with CODEX_HOME and HOME pointed
at temporary directories, under an audit hook that aborts on any open, listdir
or sqlite connect below the real or the fake ~/.codex. Nothing here reads the
operator's Codex state.
"""

import filecmp
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude/skills/codex-session-history"
MIRROR = ROOT / ".agents/skills/codex-session-history"
SCRIPTS = SKILL / "scripts"
FIXTURE = ROOT / "dev/fixtures/codex-rollout-synthetic.jsonl"
THREAD = "01aaaaaa-0000-7000-8000-000000000001"
TURN = "turn-0001"
REAL_CODEX = os.path.join(os.path.expanduser("~"), ".codex")

# Runs a script as __main__ and exits 97 the moment it touches a forbidden root.
GUARD = r"""
import os, runpy, sys
roots = [os.path.realpath(r) for r in os.environ["CSH_FORBIDDEN"].split(os.pathsep) if r]
def hook(event, args):
    if event not in ("open", "os.listdir", "os.scandir", "sqlite3.connect") or not args:
        return
    target = args[0]
    if isinstance(target, bytes):
        target = os.fsdecode(target)
    if not isinstance(target, str):
        return
    target = target.removeprefix("file:").split("?", 1)[0]
    real = os.path.realpath(target)
    if any(real == r or real.startswith(r + os.sep) for r in roots):
        sys.stderr.write(f"FORBIDDEN {event} {target}\n")
        sys.stderr.flush()
        os._exit(97)
sys.addaudithook(hook)
script = sys.argv[1]
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
"""


def make_state(codex_home: Path, rollout: Path) -> None:
    con = sqlite3.connect(codex_home / "state_5.sqlite")
    con.executescript(
        """
        create table threads (
            id text primary key, rollout_path text, title text, cwd text, model text,
            reasoning_effort text, git_branch text, git_sha text, created_at integer,
            updated_at integer, archived integer, source text, thread_source text,
            cli_version text, tokens_used integer);
        create table thread_spawn_edges (parent_thread_id text, child_thread_id text, status text);
        """
    )
    con.execute(
        "insert into threads values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (THREAD, str(rollout), "SYNTHETIC THREAD TITLE", "/synthetic/worktrees/demo", "synthetic-model",
         "high", "claude/x", "abcdef1", 1790000000, 1790000600, 0, "vscode", "user", "0.0.0-synthetic", 23456),
    )
    con.commit()
    con.close()


def make_receipts(codex_home: Path) -> None:
    run = codex_home / "research-coverage" / THREAD / TURN
    run.mkdir(parents=True)
    (run / "manifest.json").write_text(json.dumps({
        "generated_at": "2026-10-01T10:00:00Z",
        "policy_version": "strict-five-v2",
        "strict_five": True,
        "request_id": TURN,
        "query": "SYNTHETIC RESEARCH QUERY",
        "sources": [{"name": "exa", "status": "ok", "items": 3}],
    }))
    (run / "context7.json").write_text(json.dumps({"status": "error_quota_synthetic"}))


class CodexSessionHistoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.codex_home = base / "codex-home"
        self.fake_home = base / "home"
        self.scratch = base / "scratch"
        for d in (self.codex_home, self.fake_home / ".codex", self.scratch):
            d.mkdir(parents=True)
        self.rollout = self.codex_home / "sessions" / f"rollout-synthetic-{THREAD}.jsonl"
        self.rollout.parent.mkdir(parents=True)
        self.rollout.write_bytes(FIXTURE.read_bytes())
        make_state(self.codex_home, self.rollout)
        make_receipts(self.codex_home)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, name, *args):
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.fake_home),
            "CODEX_HOME": str(self.codex_home),
            "CSH_FORBIDDEN": os.pathsep.join([REAL_CODEX, str(self.fake_home / ".codex")]),
        }
        result = subprocess.run(
            [sys.executable, "-I", "-c", GUARD, str(SCRIPTS / name), *args],
            capture_output=True, text=True, env=env, cwd=self.scratch, timeout=15,
        )
        self.assertNotIn("FORBIDDEN", result.stderr)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_digest_from_fixture_path(self):
        out = self.scratch / "digest.md"
        self.run_script("codex_rollout_digest.py", str(FIXTURE), "--out", str(out))
        digest = out.read_text()
        self.assertIn("SYNTHETIC USER PROMPT: add the widget and commit it", digest)
        self.assertIn("SYNTHETIC TURN FINAL: widget committed as abcdef1", digest)
        self.assertIn("claude/x abcdef1 add synthetic widget", digest)
        self.assertIn("write_file: src/synthetic_widget.py", digest)
        self.assertIn("exec: await shell(\"git add", digest)
        self.assertIn("SYNTHETIC COMPACTION SUMMARY", digest)
        self.assertIn("forked_from=`01aaaaaa-0000-7000-8000-0000000000f0`", digest)
        self.assertIn("turns=2 completed=1 aborted=1 compactions=1", digest)
        self.assertIn("total=23,456", digest)

    def test_digest_resolves_thread_through_state(self):
        digest = self.run_script("codex_rollout_digest.py", THREAD[:12])
        self.assertIn("title: SYNTHETIC THREAD TITLE", digest)
        self.assertIn(str(self.rollout), digest)

    def test_research_receipts(self):
        out = self.run_script("codex_research_receipts.py", THREAD[:8])
        self.assertIn("policy=strict-five-v2 strict_five=True", out)
        self.assertIn("SYNTHETIC RESEARCH QUERY", out)
        self.assertIn('- exa: {"status": "ok", "items": 3', out)
        self.assertIn('- context7: {"file_status": "error_quota_synthetic"}', out)
        listing = self.run_script("codex_research_receipts.py")
        self.assertIn(f"{THREAD}  runs=1", listing)

    def test_threads_list_and_show(self):
        out = self.run_script("codex_threads.py", "list")
        self.assertIn(f"| {THREAD} | synthetic-model | /synthetic/worktrees/demo | SYNTHETIC THREAD TITLE", out)
        shown = json.loads(self.run_script("codex_threads.py", "show", THREAD[:8]))
        self.assertEqual(shown["rollout_path"], str(self.rollout))
        self.assertTrue(shown["rollout_exists"])
        self.assertEqual(shown["research_coverage_dir"], str(self.codex_home / "research-coverage" / THREAD))

    def test_guard_rejects_default_codex_home(self):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.fake_home),
               "CSH_FORBIDDEN": str(self.fake_home / ".codex")}
        (self.fake_home / ".codex" / "research-coverage").mkdir()
        result = subprocess.run(
            [sys.executable, "-I", "-c", GUARD, str(SCRIPTS / "codex_research_receipts.py")],
            capture_output=True, text=True, env=env, cwd=self.scratch, timeout=15,
        )
        self.assertEqual(result.returncode, 97)
        self.assertIn("FORBIDDEN os.listdir", result.stderr)

    def test_mirror_is_byte_identical(self):
        def tree(root):
            return sorted(p.relative_to(root) for p in root.rglob("*")
                          if p.is_file() and "__pycache__" not in p.parts)
        files = tree(SKILL)
        self.assertTrue(files)
        self.assertEqual(files, tree(MIRROR))
        for rel in files:
            self.assertTrue(filecmp.cmp(SKILL / rel, MIRROR / rel, shallow=False), rel)
            self.assertEqual((SKILL / rel).stat().st_mode, (MIRROR / rel).stat().st_mode, rel)


if __name__ == "__main__":
    unittest.main()
