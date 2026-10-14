"""Contract tests for the retro-gate hooks (dev/hooks/*, hk.pkl), hermetic scratch Git only."""

import json
import os
from pathlib import Path
import copy
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock

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
import shlex, subprocess, sys, tomllib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
run = tomllib.loads((root / "mise.dev.toml").read_text())["tasks"][sys.argv[2]]["run"]
for line in [run] if isinstance(run, str) else run:
    argv = shlex.split(line.replace("${{MARKETPLACE_PYTHON:-python3}}", sys.executable))
    code = subprocess.run(argv, cwd=root).returncode
    if code:
        sys.exit(code)
"""


def environment(home):
    # MISE_*: a nested mise in the scratch repo must not inherit the outer dev/mise trust and config.
    env = {k: v for k, v in os.environ.items() if k not in SCRUB and not k.startswith(("GIT_", "HK_", "MISE_"))}
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

    def lane(self, unit="x", branch="claude/x-y", **fields):
        (self.plan / "lanes" / f"{unit}.json").write_text(json.dumps({"unit": unit, "branch": branch, **fields}))

    def retro(self, present=True, unit="x"):
        path = self.plan / "retros" / f"{unit}.md"
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
        self.assertIn(f"retro record missing: .planning/{PLAN}/retros/x.md", output["permissionDecisionReason"])
        self.assertNotIn(self.tmp.name, output["permissionDecisionReason"])

    def assert_allowed(self, command):
        self.assertEqual(self.bash(command), (0, ""), command)

    def test_lane_merge_and_push_denied_until_retro_passes(self):
        for command in ("git merge --no-ff claude/x-y", "git -C . merge -m 'take lane' claude/x-y",
                        "git push origin claude/x-y", "ls && git push -u origin +claude/x-y:claude/x-y",
                        "git \\\npush origin claude/x-y", "git merge \\\n  --no-ff claude/x-y"):
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


class GhWriteGate(unittest.TestCase):
    """D179: the Bash gate refuses raw gh writes and names the scanned route; reads and the route pass."""

    REFUSED = (
        "gh issue comment 12 --body BODYTEXT", "gh issue create -t t -b BODYTEXT", "gh issue new", "gh issue edit 3",
        "gh issue close 3", "gh issue reopen 3", "gh issue delete 3", "gh pr create --fill", "gh pr new",
        "gh pr edit 4 -b BODYTEXT", "gh pr comment 4 -b BODYTEXT", "gh pr review 4 --approve", "gh pr close 4",
        "gh pr reopen 4", "gh pr merge 4 --squash", "gh pr ready 4", "gh release create v1 -n BODYTEXT",
        "gh release edit v1", "gh gist create f.txt", "gh gist edit 1", "gh label create bug", "gh label edit bug",
        "gh repo edit --description BODYTEXT", "gh repo create o/r", "gh repo deploy-key add k.pub",
        "gh repo autolink create x y", "gh issue frobnicate 3", "gh api -X POST repos/o/r/issues",
        "gh api --method PATCH repos/o/r/issues/1", "gh api --method=delete repos/o/r/labels/x",
        "gh api -XPUT repos/o/r/topics", "gh api -iX POST repos/o/r", "gh api repos/o/r/issues -f title=BODYTEXT",
        "gh api repos/o/r/issues/1/comments -F body=@c.md", "gh api repos/o/r/issues --field title=t",
        "gh api repos/o/r/issues --raw-field=title=t", "gh api repos/o/r/issues --input body.json",
        "gh api -X GET -X POST repos/o/r/issues", "gh api --unknown repos/o/r",
        "gh api graphql -f query='mutation { addComment(input: {}) { clientMutationId } }'",
        "gh api graphql -F query=@q.graphql", "gh api graphql --input q.json", "gh api graphql",
        "gh -R owner/repo issue comment 1 -b BODYTEXT", "gh --repo=owner/repo pr create", "gh issue -R o/r close 1",
        "GH_TOKEN=x gh pr comment 1 -b BODYTEXT", "env GH_HOST=h /opt/homebrew/bin/gh issue edit 1",
        "git status && gh issue comment 1 -b BODYTEXT", "ls; gh pr merge 1", "cat c.md | gh issue comment 1 -F -",
        "gh issue comment 1 -F - <<'EOF'\nBODYTEXT\nEOF", "bash -lc 'gh pr comment 1 -b BODYTEXT'",
        "x=$(gh issue create -t t -b BODYTEXT)", "echo `gh pr close 1`", "eval gh issue close 1",
        "sh -c 'gh api graphql -f query=\"mutation { a(x: 1) { id } }\"'",
        # review findings on 27cae68: a continuation is joined before segments split; a substituted query is unreadable
        "gh api \\\n-X POST repos/x/y/issues -f title=BODYTEXT", "gh \\\nissue comment 1 -b BODYTEXT",
        "gh pr create \\\n  --title t \\\n  --body BODYTEXT", 'gh api graphql -f query="$Q"',
        'gh api graphql -f query="$(cat m.graphql)"', "gh api graphql -f query=`cat m.graphql`",
        "gh api graphql -F query='$Q'",
    )
    ALLOWED = (
        "gh issue view 12", "gh issue list --label bug", "gh issue ls", "gh issue status", "gh -R o/r issue view 1",
        "gh issue", "gh pr view 4 --comments", "gh pr list", "gh pr status", "gh pr diff 4", "gh pr checks 4",
        "gh pr checkout 4", "gh release list", "gh release view v1", "gh repo view", "gh repo clone o/r",
        "gh repo deploy-key list", "gh label list", "gh gist list", "gh api repos/o/r/issues",
        "gh api -X GET search/issues -f q=x", "gh api --method get repos/o/r", "gh api -H 'Accept: x' repos/o/r",
        "gh api --paginate repos/o/r/pulls --jq '.[].number'",
        "gh api graphql -f query='query { viewer { login } }'", "gh api graphql -F owner=o -f query='{ viewer { id } }'",
        "gh auth status", "gh help issue create", "gh run list", "gh search issues x", "which gh",
        "./dev/mise run gh:write -- issue comment 12 --body-file c.md",
        "./dev/mise run gh:write -- api -X POST repos/o/r/issues -f title=t && gh issue view 12",
        "git commit -m 'gate: refuse gh issue create'", "grep -rn 'gh pr merge' docs",
    )

    def bash(self, command):
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run([sys.executable, "-I", str(HOOKS / "pretooluse_gate.py")], capture_output=True,
                                    input=json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": cwd,
                                                      "tool_input": {"command": command}}),
                                    env=environment(Path(cwd)), text=True, timeout=10)
        return result.returncode, result.stdout

    def test_raw_gh_writes_are_denied_with_the_scanned_route_named(self):
        for command in self.REFUSED:
            with self.subTest(command=command):
                rc, out = self.bash(command)
                self.assertEqual(rc, 0)
                output = json.loads(out or "{}").get("hookSpecificOutput", {})
                self.assertEqual(output.get("permissionDecision"), "deny", out)
                reason = output["permissionDecisionReason"]
                self.assertIn("./dev/mise run gh:write -- <gh args>", reason)
                self.assertIn("issue:create-preview", reason)
                self.assertNotIn("BODYTEXT", reason)  # the reason names the form, never the text

    def test_gh_reads_and_the_scanned_route_pass(self):
        for command in self.ALLOWED:
            with self.subTest(command=command):
                self.assertEqual(self.bash(command), (0, ""))


class GitGateCli(Scratch):
    def gate(self, mode, **env):
        result = subprocess.run([sys.executable, "-I", str(HOOKS / "git_gate.py"), mode], cwd=self.repo,
                                env={**self.env, **env}, capture_output=True, text=True, timeout=20)
        self.assertNotIn(self.tmp.name, result.stdout)
        return result.returncode, result.stdout

    def commit(self, branch, name):
        self.git("checkout", "-q", branch)
        (self.repo / name).write_text(name)
        self.git("add", name)
        self.git("commit", "-q", "-m", name)

    def test_sync_merge_of_the_integration_tip_is_not_blamed_on_another_lane(self):
        self.git("checkout", "-q", "-b", "claude/a-b")
        self.lane(unit="a", branch="claude/a-b")
        self.commit("claude/a-b", "a1")
        self.commit("main", "m1")
        tip = self.git("rev-parse", "HEAD").stdout.strip()
        self.commit("main", "m2")
        for branch in ("claude/a-b", "claude/x-y"):  # both lanes sync; name-rev calls the tip claude/a-b^2
            self.git("checkout", "-q", branch)
            self.git("merge", "--no-ff", "-m", "sync integration", tip)
        self.retro()
        rc, out = self.gate("push")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("claude/a-b", out)

    def test_push_refuses_only_the_failing_lane(self):
        self.retro()
        self.git("checkout", "-q", "-b", "claude/z-w")
        self.lane(unit="z", branch="claude/z-w")
        self.commit("claude/z-w", "z1")
        self.git("checkout", "-q", "main")
        for branch in ("claude/x-y", "claude/z-w"):
            self.git("merge", "--no-ff", "--no-edit", branch)
        rc, out = self.gate("push")
        self.assertEqual(rc, 2, out)
        self.assertIn(f"retro gate refused claude/z-w:\nRETRO GATE FAILED for .planning/{PLAN}/retros/z.md", out)
        self.assertNotIn("refused claude/x-y", out)

    def test_merge_gate_classifies_the_merge_source(self):
        for action in ("merge main", "merge origin/main", "merge --no-ff codex/marketplace-native-onboarding"):
            self.assertEqual(self.gate("merge", GIT_REFLOG_ACTION=action)[0], 0, action)
        refusals = {"merge claude/x-y": "retro record missing",
                    "merge claude/q-r": "unit could not be derived",  # the retro gate exits 1
                    "merge feature/foo": "no lane branch derivable for feature/foo",
                    None: "merge source unknown"}
        for action, reason in refusals.items():
            rc, out = self.gate("merge", **({"GIT_REFLOG_ACTION": action} if action else {}))
            self.assertEqual(rc, 2, (action, out))
            self.assertIn(reason, out)


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
        self.assertNotIn(self.tmp.name, decision["reason"])
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


def fake_git(directory, marker, name="git"):
    """A stand-in for a mise shim: records each call in `marker`, then runs the real git."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / name).write_text(f'#!/bin/sh\necho "$@" >> "{marker}"\nexec "{Path(GIT_DIR, "git")}" "$@"\n')
    (directory / name).chmod(0o755)
    return directory / name


class GitResolution(Scratch):
    """The gates run a real git, never a mise shim (a shim costs ~0.18 s per call on the dev host)."""

    def setUp(self):
        super().setUp()
        self.marker = self.tmp / "shim-calls"
        self.shims = fake_git(self.tmp / "data" / "mise" / "shims", self.marker).parent

    def merge_gate(self):
        result = subprocess.run([sys.executable, "-I", str(HOOKS / "git_gate.py"), "merge"], cwd=self.repo,
                                env={**self.env, "GIT_REFLOG_ACTION": "merge claude/x-y"}, capture_output=True,
                                text=True, timeout=20)
        return result.returncode, result.stdout + result.stderr

    def test_gates_skip_a_mise_shims_directory_ahead_of_git(self):
        self.git("checkout", "-q", "claude/x-y")
        self.env["PATH"] = os.pathsep.join([str(self.shims), self.env["PATH"]])
        rc, out = self.hook("pretooluse_gate.py", {"tool_name": "Bash", "cwd": str(self.repo),
                                                   "tool_input": {"command": "git push origin claude/x-y"}})
        self.assertEqual((rc, json.loads(out)["hookSpecificOutput"]["permissionDecision"]), (0, "deny"), out)
        rc, out = self.hook("subagent_stop_gate.py", {"cwd": str(self.repo)})
        self.assertEqual((rc, json.loads(out)["decision"]), (0, "block"), out)
        rc, out = self.merge_gate()
        self.assertEqual(rc, 2, out)
        self.assertIn("retro record missing", out)
        self.assertFalse(self.marker.exists(), "a gate executed the mise shim")

    def test_only_shims_on_path_still_enforce_through_the_shim(self):
        relocated = self.tmp / "custom" / "bin"  # a shims dir under MISE_DATA_DIR: git -> the mise binary
        relocated.mkdir(parents=True)
        (relocated / "git").symlink_to(fake_git(self.tmp / "tool", self.marker, name="mise"))
        self.git("checkout", "-q", "claude/x-y")
        self.env["PATH"] = os.pathsep.join([str(self.shims), str(relocated)])
        rc, out = self.hook("pretooluse_gate.py", {"tool_name": "Bash", "cwd": str(self.repo),
                                                   "tool_input": {"command": "git push origin claude/x-y"}})
        self.assertEqual((rc, json.loads(out)["hookSpecificOutput"]["permissionDecision"]), (0, "deny"), out)
        rc, out = self.hook("subagent_stop_gate.py", {"cwd": str(self.repo)})
        self.assertEqual((rc, json.loads(out)["decision"]), (0, "block"), out)
        rc, out = self.merge_gate()
        self.assertEqual(rc, 2, out)
        self.assertIn("retro record missing", out)
        self.assertTrue(self.marker.exists(), "with no other git the gates run the mise shim")


class Settings(unittest.TestCase):
    def test_project_settings_wire_each_event_to_an_existing_blocking_script(self):
        hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
        wired = {event: [h for entry in entries for h in entry["hooks"]] for event, entries in hooks.items()}
        expected = {"PreToolUse": "pretooluse_gate.py", "SubagentStop": "subagent_stop_gate.py",
                    "Stop": "stop_gate.py"}
        self.assertEqual(hook_map(hooks), EXPECTED_HOOKS)  # the D92 pin: every event, matcher and handler count
        (doctor,) = hooks["SessionStart"][0]["hooks"]  # C3 hook entry: never blocks, so no onFailure
        self.assertEqual(hooks["SessionStart"][0]["matcher"], "startup|resume|clear|compact|fork")
        self.assertEqual((doctor["type"], doctor["timeout"], "onFailure" in doctor), ("command", 15, False))
        self.assertEqual(doctor["command"], 'python3 -I "$CLAUDE_PROJECT_DIR/dev/doctor/cli.py" --surface '
                                            'session-start --format context')
        self.assertTrue((ROOT / "dev" / "doctor" / "cli.py").is_file())
        for event, script in expected.items():
            (handler,) = wired[event]
            self.assertEqual(handler["command"], f'python3 -I "$CLAUDE_PROJECT_DIR/dev/hooks/{script}"')
            self.assertEqual((handler["type"], handler["onFailure"]), ("command", "block"))
            self.assertTrue((HOOKS / script).is_file())
        self.assertEqual(hooks["PreToolUse"][0]["matcher"], "Bash")

    def test_the_pin_refuses_one_more_entry_handler_or_event(self):
        """Rule 15: the pin fails on each way a hook can be added, so an unallocated hook fails test:hooks."""
        hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
        extra = {"type": "command", "command": "true"}
        for name, grow in (("entry", lambda h: h["SessionStart"].append({"matcher": "startup", "hooks": [extra]})),
                           ("handler", lambda h: h["PostToolUse"][0]["hooks"].append(extra)),
                           ("event", lambda h: h.__setitem__("Notification", [{"hooks": [extra]}]))):
            with self.subTest(added=name):
                grown = copy.deepcopy(hooks)
                grow(grown)
                self.assertNotEqual(hook_map(grown), EXPECTED_HOOKS)


def hook_map(hooks):
    """The seam the pin asserts: each event's entries as (matcher, handler count), in file order."""
    return {event: [(entry.get("matcher"), len(entry["hooks"])) for entry in entries] for event, entries in hooks.items()}


EXPECTED_HOOKS = {  # three deny gates (D102), the doctor (C3) and the five D166 entries; nothing else
    "UserPromptSubmit": [(None, 1)],
    "SessionStart": [("startup|resume|clear|compact|fork", 1), ("startup|resume|clear|compact", 1)],
    "PreToolUse": [("Bash", 1)],
    "PostToolUse": [("AskUserQuestion", 1)],
    "PreCompact": [(None, 1)],
    "SubagentStart": [(None, 1)],
    "SubagentStop": [(None, 1)],
    "Stop": [(None, 1)],
}

LEDGER = Path(".local/state/claude-code-marketplace/requests/ledger.jsonl")  # CL4 E1, under $HOME
HEADER = "Open requests (task_plan ## Open requests, D166; keep every line verbatim):\n"
PROMPT = {"session_id": "797fac9e-45f6-4000-bb0b-7a4b6c71a99d", "transcript_path": "/t/797fac9e.jsonl",
          "cwd": "/w", "prompt_id": "ff1c3221-ef20-4940-a382-bf0dadcffa05", "permission_mode": "default",
          "hook_event_name": "UserPromptSubmit", "prompt": "/probe-cmd alpha é \"quoted\""}
ANSWER = {"session_id": "797fac9e-45f6-4000-bb0b-7a4b6c71a99d", "prompt_id": "ff1c3221-ef20-4940-a382-bf0dadcffa05",
          "hook_event_name": "PostToolUse", "tool_name": "AskUserQuestion",
          "tool_input": {"questions": [{"question": "Which color?", "options": [{"label": "Blue"}]}]},
          "tool_response": {"answers": {"Which color?": "Blue"},
                            "annotations": {"Which color?": {"notes": "free-text note N-7731"}}},
          "tool_use_id": "toolu_01NaR2bfprATUFujrY2dE1Hy"}
PLAN_TEXT = """# Plan

## Next Step
- [ ] not a request (Next Step)

## Open requests (D160)

Intro line.

- [ ] R-119 (D114): claude-agent intake skill; issue: #112
- [x] R-120 (D114): visual artifact; done: abc1234
- [ ] R-127 · p:4462d3b1 · D119 · CT-59 · owner user · build CT-59 now

## Goal
- [ ] not a request (Goal)
"""


class RequestHooks(unittest.TestCase):
    """D166 capture and carry settings hooks, each command run by /bin/sh on fixture stdin (CT-88, CT-89)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)
        self.hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
        self.env = {"HOME": str(self.tmp / "home"), "PATH": "/usr/bin:/bin", "PLAN_ID": PLAN,
                    "CLAUDE_PROJECT_DIR": str(self.tmp / "worktree")}
        (self.tmp / "home").mkdir()

    def handler(self, event, matcher=None):
        (handler,) = [h for entry in self.hooks[event] if entry.get("matcher") == matcher for h in entry["hooks"]]
        self.assertEqual(handler["type"], "command")
        self.assertNotIn("onFailure", handler)  # nothing here may block (D166)
        return handler

    def run_hook(self, event, matcher=None, stdin="{}", **env):
        proc = subprocess.run(["/bin/sh", "-c", self.handler(event, matcher)["command"]], input=stdin,
                              capture_output=True, text=True, env={**self.env, **env}, cwd=self.tmp, timeout=10)
        return proc.returncode, proc.stdout

    def plan(self, root, text=PLAN_TEXT):
        path = Path(root) / ".planning" / PLAN / "task_plan.md"
        path.parent.mkdir(parents=True)
        path.write_text(text)

    def test_capture_hooks_are_async_and_append_the_stdin_row_to_the_untracked_ledger(self):
        (self.tmp / "home" / LEDGER).parent.mkdir(parents=True, mode=0o755)  # a pre-existing wider directory
        for (event, matcher), payload in {("UserPromptSubmit", None): PROMPT,
                                          ("PostToolUse", "AskUserQuestion"): ANSWER}.items():
            with self.subTest(event=event):
                self.assertIs(self.handler(event, matcher)["async"], True)
                ledger = self.tmp / "home" / LEDGER
                before = ledger.read_text().splitlines() if ledger.exists() else []
                self.assertEqual(self.run_hook(event, matcher, json.dumps(payload, indent=2)), (0, ""))
                self.assertEqual(ledger.read_text().splitlines(),
                                 [*before, json.dumps(payload, separators=(",", ":"), ensure_ascii=False)])
        self.assertEqual(oct((self.tmp / "home" / LEDGER).parent.stat().st_mode & 0o777), "0o700")

    def test_capture_of_invalid_stdin_appends_nothing_and_never_exits_2(self):
        rc, out = self.run_hook("UserPromptSubmit", stdin="{not json")
        self.assertEqual((rc, out), (1, ""))
        self.assertEqual((self.tmp / "home" / LEDGER).read_text(), "")

    def test_carry_hooks_print_only_the_open_request_items(self):
        self.plan(self.tmp / "worktree")
        items = HEADER + "- [ ] R-119 (D114): claude-agent intake skill; issue: #112\n" \
                         "- [ ] R-127 · p:4462d3b1 · D119 · CT-59 · owner user · build CT-59 now\n"
        self.assertEqual(self.run_hook("PreCompact"), (0, items))
        self.assertEqual(self.run_hook("SessionStart", "startup|resume|clear|compact"), (0, items))
        rc, out = self.run_hook("SubagentStart")
        self.assertEqual((rc, json.loads(out)), (0, {"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                                                            "additionalContext": items}}))

    def test_carry_reads_the_pinned_plan_root_before_the_project_dir(self):
        self.plan(self.tmp / "worktree", "## Open requests\n- [ ] R-1 stale worktree copy\n")
        self.plan(self.tmp / "main", "## Open requests\n- [ ] R-2 integration copy\n")
        self.assertEqual(self.run_hook("PreCompact", PWF_PLAN_ROOT=str(self.tmp / "main")),
                         (0, HEADER + "- [ ] R-2 integration copy\n"))

    def test_carry_without_a_plan_prints_the_header_and_exits_0(self):
        for event, matcher in (("PreCompact", None), ("SessionStart", "startup|resume|clear|compact")):
            self.assertEqual(self.run_hook(event, matcher), (0, HEADER))
        rc, out = self.run_hook("SubagentStart")
        self.assertEqual((rc, json.loads(out)["hookSpecificOutput"]["additionalContext"]), (0, HEADER))


    def test_requests_tail_keys_answers_by_last_8_of_tool_use_id_and_prompts_by_first_8_of_prompt_id(self):
        """The key rule of the request-catch reader (dev/handoff.py, D167): answers never key on prompt_id."""
        run = tomllib.loads((ROOT / "mise.dev.toml").read_text())["tasks"]["requests:tail"]["run"]
        ledger = self.tmp / "home" / LEDGER
        ledger.parent.mkdir(parents=True)
        ledger.write_text("".join(json.dumps(row) + "\n" for row in (PROMPT, ANSWER, {**ANSWER, "tool_use_id": ""})))
        proc = subprocess.run(["/bin/sh", "-c", run], capture_output=True, text=True, timeout=10,
                              env={**self.env, "usage_count": "3"})
        self.assertEqual((proc.returncode, [json.loads(line)["key"] for line in proc.stdout.splitlines()]),
                         (0, ["p:ff1c3221", "p:rY2dE1Hy", "p:ff1c3221"]))

class ScratchEnvironment(unittest.TestCase):
    def test_outer_mise_trust_and_config_do_not_reach_the_scratch_repo(self):
        outer = {"MISE_TRUSTED_CONFIG_PATHS": "/outer/mise.dev.toml",
                 "MISE_OVERRIDE_CONFIG_FILENAMES": "mise.dev.toml", "MISE_CONFIG_DIR": "/outer/.config/mise"}
        with mock.patch.dict(os.environ, outer):
            env = environment(Path("/scratch/home"))
        self.assertEqual(sorted(k for k in env if k.startswith("MISE_")), [])


@unittest.skipUnless(HK, "hk is not installed")
class HkHooks(Scratch):
    def setUp(self):
        super().setUp()
        (self.repo / "dev" / "hooks").mkdir(parents=True)
        (self.repo / "dev" / "doctor").mkdir()
        for name in ("hk.pkl", "mise.dev.toml", "dev/retro_gate.py", *(f"dev/hooks/{p.name}" for p in
                                                                         HOOKS.glob("*.py")),
                     *(f"dev/doctor/{p.name}" for p in (ROOT / "dev" / "doctor").glob("*.py"))):
            shutil.copyfile(ROOT / name, self.repo / name)
        mise = self.repo / "dev" / "mise"
        mise.write_text(FAKE_MISE.format(python=sys.executable))
        mise.chmod(0o755)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "hooks")
        result = subprocess.run(["dev/mise", "run", "hooks:install"], cwd=self.repo, env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("merge.ff=false", result.stdout)
        self.assertEqual(self.git("config", "--local", "merge.ff").stdout.strip(), "false")
        self.git("init", "-q", "--bare", str(self.tmp / "remote.git"))
        self.git("remote", "add", "origin", str(self.tmp / "remote.git"))

    def test_merge_commit_and_push_refused_then_accepted(self):
        refused = self.git("merge", "--no-edit", "claude/x-y", check=False)  # fast-forwardable
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

    def test_pre_commit_records_step_refuses_non_project_settings_key(self):
        """C2 T-B5 / W0-5: the staged settings file is refused before the commit, then accepted once split."""
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": []}}))
        self.git("add", "-A")
        refused = self.git("commit", "-q", "-m", "settings", check=False)
        self.assertNotEqual(refused.returncode, 0, refused.stdout + refused.stderr)
        self.assertIn("I.settings-non-project-key permissions", refused.stdout + refused.stderr)
        (self.repo / ".claude" / "settings.json").write_text(json.dumps({"env": {"PLAN_ID": PLAN}}))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "settings")


if __name__ == "__main__":
    unittest.main()
