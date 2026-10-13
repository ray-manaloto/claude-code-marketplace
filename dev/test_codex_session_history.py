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
CHILD = "01cccccc-0000-7000-8000-000000000002"
TWINS = ("01bbbbbb-0000-7000-8000-000000000003", "01bbbbbb-0000-7000-8000-000000000004")
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


THREAD_COLS = 15


def thread_row(tid, rollout, title, updated):
    return (tid, str(rollout), title, "/synthetic/worktrees/demo", "synthetic-model", "high", "claude/x",
            "abcdef1", 1790000000, updated, 0, "vscode", "user", "0.0.0-synthetic", 23456)


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
    con.execute(f"insert into threads values ({','.join('?' * THREAD_COLS)})",
                thread_row(THREAD, rollout, "SYNTHETIC THREAD TITLE", 1790000600))
    con.execute(f"insert into threads values ({','.join('?' * THREAD_COLS)})",
                thread_row(CHILD, rollout, "SYNTHETIC CHILD TITLE", 1790000300))
    con.execute("insert into thread_spawn_edges values (?,?,?)", (THREAD, CHILD, "completed"))
    con.commit()
    con.close()


def make_history(codex_home: Path) -> None:
    con = sqlite3.connect(codex_home / "thread_history_1.sqlite")
    con.executescript(
        """
        create table thread_turns (
            thread_id text, turn_id text, status text, started_at integer, completed_at integer,
            duration_ms integer, rollout_ordinal integer, rollout_end_ordinal integer, error_json text);
        create table thread_items (thread_id text, turn_id text, ordinal integer, item_json text);
        """
    )
    con.executemany("insert into thread_turns values (?,?,?,?,?,?,?,?,?)", [
        (THREAD, "turn-0001", "completed", 1790000003, 1790000015, 120000, 3, 16, None),
        (THREAD, "turn-0002", "failed", 1790000302, 1790000305, 3000, 19, 24,
         '{"code":"usage_limit_exceeded","message":"SYNTHETIC usage limit until 2026-10-19"}'),
    ])
    con.commit()
    con.close()


def make_logs(codex_home: Path) -> None:
    con = sqlite3.connect(codex_home / "logs_2.sqlite")
    con.execute("create table logs (ts integer, ts_nanos integer, level text, target text, "
                "feedback_log_body text, file text, line integer, thread_id text, process_uuid text)")
    con.executemany("insert into logs values (?,?,?,?,?,?,?,?,?)", [
        (1790000010, 1, "INFO", "feedback_tags", "SYNTHETIC FEEDBACK TAG BODY", "tags.rs", 7, THREAD, "p1"),
        (1790000011, 2, "INFO", "codex_core::session::turn", "SYNTHETIC OTHER BODY", "turn.rs", 9, THREAD, "p1"),
    ])
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
        make_history(self.codex_home)
        make_logs(self.codex_home)
        make_receipts(self.codex_home)

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, name, *args, rc=0, env=None, path_prefix=None):
        path = os.environ.get("PATH", "/usr/bin:/bin")
        full_env = {
            "PATH": f"{path_prefix}{os.pathsep}{path}" if path_prefix else path,
            "HOME": str(self.fake_home),
            "CODEX_HOME": str(self.codex_home),
            "CSH_FORBIDDEN": os.pathsep.join([REAL_CODEX, str(self.fake_home / ".codex")]),
            **(env or {}),
        }
        result = subprocess.run(
            [sys.executable, "-I", "-c", GUARD, str(SCRIPTS / name), *args],
            capture_output=True, text=True, env=full_env, cwd=self.scratch, timeout=15,
        )
        self.assertNotIn("FORBIDDEN", result.stderr)
        self.assertEqual(result.returncode, rc, result.stdout + result.stderr)
        return result.stdout if rc == 0 else result.stderr

    def add_twin_threads(self):
        con = sqlite3.connect(self.codex_home / "state_5.sqlite")
        for i, tid in enumerate(TWINS):
            con.execute(f"insert into threads values ({','.join('?' * THREAD_COLS)})",
                        thread_row(tid, self.rollout, f"TWIN {i}", 1790000100 + i))
        con.commit()
        con.close()

    def test_digest_from_fixture_path(self):
        out = self.scratch / "digest.md"
        self.run_script("codex_rollout_digest.py", str(FIXTURE), "--out", str(out))
        digest = out.read_text()
        self.assertIn("SYNTHETIC USER PROMPT: add the widget and commit it", digest)
        self.assertIn("### [2026-10-01T10:00:15.000Z] ord=15 turn=turn-0001", digest)
        self.assertIn("SYNTHETIC TURN FINAL: widget committed as abcdef1", digest)
        self.assertIn("claude/x abcdef1 add synthetic widget", digest)
        self.assertIn("write_file: src/synthetic_widget.py", digest)
        self.assertIn("exec: await shell(\"git add", digest)
        self.assertIn("SYNTHETIC COMPACTION SUMMARY", digest)
        self.assertIn("forked_from=`01aaaaaa-0000-7000-8000-0000000000f0`", digest)
        self.assertIn("turns=2 completed=1 aborted=1 compactions=1", digest)
        self.assertIn("total=23,456", digest)
        self.assertNotIn("ghp_SYNTHETIC", digest)
        self.assertIn("stop here, token <redacted> keep-this-tail", digest)

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

    def test_receipts_oversized_source_is_not_parsed(self):
        run = self.codex_home / "research-coverage" / THREAD / TURN
        (run / "firecrawl.json").write_bytes(b'{"status": "ok", "pad": "' + b"x" * (2 * 1024 * 1024) + b'"}')
        out = self.run_script("codex_research_receipts.py", THREAD[:8])
        self.assertIn('- firecrawl: {"file_status": "oversized"}', out)

    def test_threads_turns_children_logs(self):
        turns = self.run_script("codex_threads.py", "turns", THREAD[:8])
        self.assertIn("| failed |", turns)
        self.assertIn("usage_limit_exceeded", turns)
        self.assertIn("| completed |", turns)
        children = self.run_script("codex_threads.py", "children", THREAD[:8])
        self.assertIn(f"| {CHILD} | completed | synthetic-model | SYNTHETIC CHILD TITLE", children)
        logs = self.run_script("codex_threads.py", "logs", THREAD[:8], "--target", "feedback_tags")
        self.assertIn("| INFO | feedback_tags | SYNTHETIC FEEDBACK TAG BODY", logs)
        self.assertNotIn("SYNTHETIC OTHER BODY", logs)
        shown = json.loads(self.run_script("codex_threads.py", "--json", "show", THREAD[:8]))
        self.assertEqual(shown["turns"]["count"], 2)
        self.assertEqual(shown["turns"]["completed"], 1)
        self.assertEqual(shown["spawned_children"], 1)
        child = json.loads(self.run_script("codex_threads.py", "--json", "show", CHILD[:8]))
        self.assertEqual(child["spawn_parent"]["parent_thread_id"], THREAD)

    def test_ambiguous_prefix_refuses(self):
        self.add_twin_threads()
        for name, args in (("codex_threads.py", ("show", "01bbbbbb")),
                           ("codex_rollout_digest.py", ("01bbbbbb",))):
            err = self.run_script(name, *args, rc=2)
            self.assertIn("ambiguous", err)
            for tid in TWINS:
                self.assertIn(tid, err)
        shown = json.loads(self.run_script("codex_threads.py", "--json", "show", TWINS[1]))
        self.assertEqual(shown["id"], TWINS[1])

    def test_otel_tail_reads_env_file(self):
        record = {"resourceLogs": [{
            "resource": {"attributes": [
                {"key": "service.name", "value": {"stringValue": "codex_synthetic"}},
                {"key": "service.version", "value": {"stringValue": "9.9.9"}},
                {"key": "deployment.environment.name", "value": {"stringValue": "test"}}]},
            "scopeLogs": [{"logRecords": [{"timeUnixNano": "1790000000000000000"},
                                          {"timeUnixNano": "1790000001000000000"}]}]}]}
        otel = self.scratch / "codex-otel-synthetic.jsonl"
        otel.write_text(json.dumps(record) + "\n")
        out = self.run_script("codex_otel_tail.py", env={"CODEX_OTEL_FILE": str(otel)})
        self.assertIn("== codex-otel-synthetic.jsonl", out)
        self.assertIn("      2  codex_synthetic@9.9.9/test", out)
        out = self.run_script("codex_otel_tail.py", env={"CODEX_OTEL_FILE_GLOB": str(self.scratch / "codex-otel*.jsonl")})
        self.assertIn("      2  codex_synthetic@9.9.9/test", out)

    def test_agentsview_search_with_fake_cli(self):
        bin_dir = self.scratch / "bin"
        bin_dir.mkdir()
        args_log = self.scratch / "agentsview-args.txt"
        canned = json.dumps({
            "coverage": {"semantic": {"status": "ready"}},
            "next_cursor": None,
            "matches": [{"timestamp": "2026-10-01T10:00:04.000Z", "agent": "codex", "project": "demo",
                         "session_id": f"codex:{THREAD}", "ordinal": 4, "location": "message", "role": "user",
                         "snippet": "SYNTHETIC SNIPPET\nsecond line", "subordinate": False}],
        })
        fake = bin_dir / "agentsview"
        fake.write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" > '{args_log}'\ncat <<'JSON'\n{canned}\nJSON\n")
        fake.chmod(0o755)
        token = self.scratch / "token"
        out = self.run_script("agentsview_search.py", "search", "widget", "--hybrid", path_prefix=str(bin_dir),
                              env={"AGENTSVIEW_TOKEN_FILE": str(token), "AGENTSVIEW_SERVER": "http://synthetic.invalid"})
        self.assertIn('mode=hybrid coverage={"semantic": {"status": "ready"}}', out)
        self.assertIn(f"- 2026-10-01T10:00:04 codex demo top codex:{THREAD} ord=4 [message/user] "
                      "SYNTHETIC SNIPPET second line", out)
        recorded = args_log.read_text()
        self.assertIn(f"--server-token-file {token}", recorded)
        self.assertIn("--hybrid", recorded)

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
