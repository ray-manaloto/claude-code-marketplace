"""Contract tests for the retro-gate hooks (dev/hooks/*, hk.pkl), hermetic scratch Git only."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "dev" / "hooks"
COMPLETE = (ROOT / "dev" / "fixtures" / "retros" / "complete.md").read_text()
PLAN = "test-plan"
HK = shutil.which("hk")
# The git binary itself, ahead of any version-manager shim (a shim costs ~0.15 s per call).
GIT_DIR = subprocess.run(["git", "--exec-path"], capture_output=True, text=True, check=True).stdout.strip()
SCRUB = ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "MARKETPLACE_PYTHON", "RETRO_UNIT", "CLAUDE_LANE_UNIT",
         "PLAN_ID", "PWF_PLAN_ROOT", "HK_MISE", "HK_FILE", "HK")
FAKE_MISE = """#!{python} -I
import os, subprocess, sys, tomllib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
task = tomllib.loads((root / "mise.dev.toml").read_text())["tasks"][sys.argv[2]]
env = dict(os.environ, MARKETPLACE_PYTHON=sys.executable)
sys.exit(subprocess.run(task["run"], shell=True, cwd=root, env=env).returncode)
"""


def environment(home):
    env = {k: v for k, v in os.environ.items() if k not in SCRUB and not k.startswith(("GIT_", "HK_"))}
    env["PATH"] = os.pathsep.join([GIT_DIR, *([str(Path(HK).parent)] if HK else []), env.get("PATH", "")])
    env.update(HOME=str(home), CODEX_HOME=str(Path(home, ".codex")), PLAN_ID=PLAN,
               GIT_CONFIG_GLOBAL=str(Path(home, ".gitconfig")), GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0",
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@example.invalid")
    return env


class Scratch(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        (self.tmp / "home").mkdir()
        (self.tmp / "home" / ".gitconfig").write_text("")
        self.env = environment(self.tmp / "home")
        self.repo = self.tmp / "repo"
        self.plan = self.repo / ".planning" / PLAN
        (self.plan / "lanes").mkdir(parents=True)
        self.lane(status="allocated")
        self.git("init", "-q", "-b", "main", ".")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        self.git("checkout", "-q", "-b", "claude/x-y")
        (self.repo / "lane.txt").write_text("lane work\n")
        self.git("add", "lane.txt")
        self.git("commit", "-q", "-m", "lane work")
        self.git("checkout", "-q", "main")

    def lane(self, **fields):
        record = {"unit": "x", "branch": "claude/x-y", **fields}
        (self.plan / "lanes" / "x.json").write_text(json.dumps(record))

    def retro(self, present=True):
        path = self.plan / "retros" / "x.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(COMPLETE) if present else path.unlink(missing_ok=True)

    def git(self, *args, check=True):
        result = subprocess.run(["git", *args], cwd=self.repo, env=self.env, capture_output=True, text=True,
                                timeout=30)
        if check and result.returncode:
            self.fail(f"git {args} rc {result.returncode}: {result.stderr}")
        return result

    def hook(self, script, event):
        result = subprocess.run([sys.executable, "-I", str(HOOKS / script)], input=json.dumps(event),
                                env=self.env, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout


class PreToolUse(Scratch):
    def bash(self, command, **extra):
        return self.hook("pretooluse_gate.py", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                                "tool_input": {"command": command}, "cwd": str(self.repo),
                                                "session_id": "s", **extra})

    def assert_denied(self, command, branch="claude/x-y"):
        rc, out = self.bash(command)
        self.assertEqual(rc, 0)
        output = json.loads(out)["hookSpecificOutput"]
        self.assertEqual((output["hookEventName"], output["permissionDecision"]), ("PreToolUse", "deny"))
        self.assertTrue(output["permissionDecisionReason"].startswith(f"retro gate refused {branch}:"), output)
        self.assertIn("retro record missing", output["permissionDecisionReason"])

    def assert_allowed(self, command):
        self.assertEqual(self.bash(command), (0, ""), command)

    def test_lane_merge_and_push_denied_until_retro_passes(self):
        for command in ("git merge --no-ff claude/x-y", "git -C . merge -m 'take lane' claude/x-y",
                        "git push origin claude/x-y", "ls && git push -u origin +claude/x-y:claude/x-y"):
            self.assert_denied(command)
        self.retro()
        for command in ("git merge --no-ff claude/x-y", "git push origin claude/x-y"):
            self.assert_allowed(command)

    def test_bare_push_gates_the_current_lane_branch(self):
        self.git("checkout", "-q", "claude/x-y")
        self.assert_denied("git push")
        self.assert_denied("git push origin HEAD")

    def test_integration_branch_unrelated_commands_and_other_tools_allowed(self):
        for command in ("git merge codex/marketplace-native-onboarding", "git merge origin/main", "git push origin main",
                        "git status", "git merge --abort", "echo merge push"):
            self.assert_allowed(command)
        rc, out = self.hook("pretooluse_gate.py", {"tool_name": "Read", "tool_input": {"file_path": "x"}})
        self.assertEqual((rc, out), (0, ""))

    def test_merge_in_progress_uses_merge_head(self):
        self.git("merge", "--no-ff", "--no-commit", "claude/x-y")
        self.assert_denied("git merge --continue")
        self.assert_denied("git commit --no-edit && git merge --continue")
        self.retro()
        self.assert_allowed("git merge --continue")

    def test_delivery_publish_checks_unpublished_lane_merges(self):
        self.git("merge", "--no-ff", "--no-edit", "claude/x-y")
        self.assert_denied("./dev/mise run delivery:publish intent.json abc")
        self.retro()
        self.assert_allowed("./dev/mise run delivery:publish intent.json abc")


class StopHooks(Scratch):
    def stop(self, script, **extra):
        return self.hook(script, {"hook_event_name": "Stop", "cwd": str(self.repo), "session_id": "s", **extra})

    def test_subagent_stop_blocks_lane_worktree_without_retro_once(self):
        self.git("checkout", "-q", "claude/x-y")
        rc, out = self.stop("subagent_stop_gate.py", agent_transcript_path="/dev/null")
        self.assertEqual(rc, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        self.assertIn("retro record missing", decision["reason"])
        self.assertIn(f".planning/{PLAN}/retros/<unit>.md", decision["reason"])
        self.assertEqual(self.stop("subagent_stop_gate.py", stop_hook_active=True), (0, ""))
        self.retro()
        self.assertEqual(self.stop("subagent_stop_gate.py"), (0, ""))

    def test_subagent_stop_ignores_the_integration_checkout(self):
        self.assertEqual(self.stop("subagent_stop_gate.py"), (0, ""))

    def test_parent_stop_blocks_integrated_lane_without_passed_retro(self):
        self.assertEqual(self.stop("stop_gate.py"), (0, ""))
        self.lane(status="integrated into main (review PASS)")
        rc, out = self.stop("stop_gate.py")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["decision"], "block")
        self.assertTrue(json.loads(out)["reason"].startswith("Integrated lanes without a passed retro: x."))
        self.assertEqual(self.stop("stop_gate.py", stop_hook_active=True), (0, ""))
        self.lane(status="integrated into main", retro="passed")
        self.assertEqual(self.stop("stop_gate.py"), (0, ""))


class Settings(unittest.TestCase):
    def test_project_settings_wire_each_event_to_an_existing_blocking_script(self):
        hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
        wired = {event: [h for entry in entries for h in entry["hooks"]] for event, entries in hooks.items()}
        expected = {"PreToolUse": "pretooluse_gate.py", "SubagentStop": "subagent_stop_gate.py",
                    "Stop": "stop_gate.py"}
        self.assertEqual(set(wired), set(expected))
        for event, script in expected.items():
            (handler,) = wired[event]
            self.assertEqual(handler["command"], f'python3 -I "$CLAUDE_PROJECT_DIR/dev/hooks/{script}"')
            self.assertEqual((handler["type"], handler["onFailure"]), ("command", "block"))
            self.assertTrue((HOOKS / script).is_file())
        self.assertEqual(hooks["PreToolUse"][0]["matcher"], "Bash")


@unittest.skipUnless(HK, "hk is not installed")
class HkHooks(Scratch):
    def setUp(self):
        super().setUp()
        (self.repo / "dev" / "hooks").mkdir(parents=True)
        for name in ("hk.pkl", "mise.dev.toml", "dev/retro_gate.py", *(f"dev/hooks/{p.name}" for p in
                                                                         HOOKS.glob("*.py"))):
            shutil.copyfile(ROOT / name, self.repo / name)
        mise = self.repo / "dev" / "mise"
        mise.write_text(FAKE_MISE.format(python=sys.executable))
        mise.chmod(0o755)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "hooks")
        result = subprocess.run(["hk", "install"], cwd=self.repo, env=self.env, capture_output=True, text=True,
                                timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git("init", "-q", "--bare", str(self.tmp / "remote.git"))
        self.git("remote", "add", "origin", str(self.tmp / "remote.git"))

    def test_merge_commit_and_push_refused_then_accepted(self):
        refused = self.git("merge", "--no-ff", "--no-edit", "claude/x-y", check=False)
        self.assertNotEqual(refused.returncode, 0, refused.stdout + refused.stderr)
        self.assertIn("retro gate refused claude/x-y", refused.stdout + refused.stderr)
        self.git("merge", "--abort")
        self.git("merge", "--no-ff", "--no-edit", "--no-verify", "claude/x-y")
        refused = self.git("push", "origin", "main", check=False)
        self.assertNotEqual(refused.returncode, 0, refused.stdout + refused.stderr)
        self.assertIn("retro gate refused claude/x-y", refused.stdout + refused.stderr)
        # Lane-worktree convention: the retro record travels on the lane branch.
        self.git("checkout", "-q", "claude/x-y")
        self.retro()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "retro")
        self.git("checkout", "-q", "main")
        self.git("merge", "--no-ff", "--no-edit", "claude/x-y")
        self.git("push", "origin", "main")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, self.git("rev-parse", "origin/main").stdout)


if __name__ == "__main__":
    unittest.main()
