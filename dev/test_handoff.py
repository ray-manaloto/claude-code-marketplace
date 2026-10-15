#!/usr/bin/env python3
"""Tests for dev/handoff.py (CT-29): state, the zero-loss check, write, owner and start-command.

Every fixture is a scratch Git repository with its own bare `origin`, a lane worktree and a small
plan directory; the pwf injection probe is replaced by `fake_probe`, which builds the same frames
the plugin would (plan head-50 or the smart keep-sections, progress tail-20). One live test runs the
real plugin when its cache is installed.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
DEV = Path(__file__).resolve().parent
ROOT = DEV.parent
sys.path.insert(0, str(DEV))
import handoff  # noqa: E402

PLAN_ID = "2026-10-10-test-plan"
BRANCH = "codex/test-branch"
RV = "reviews/ccm-test"


def git(repo: Path, *args: str) -> str:
    return subprocess.run([handoff.GIT, "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def plan_text(head: str, beta_sha: str, alpha_claim: str = "integrated", ops: str = "DL-1",
              receipt: str = f"{RV}/phase3/receipt.md") -> str:
    return f"""# Test plan

PLAN_ID `{PLAN_ID}`; `PWF_PLAN_ROOT` (absolute):
`/tmp/x`. Owner: session
`old-session` (`11111111-2222-3333-4444-555555555555`) owns this plan and the branch
`{BRANCH}` since 2026-10-13; dead session `older` (`00000000`)
is closed. Pin `PWF_PLAN_ROOT` and `PLAN_ID` in the host env.

## Next Step
Integrate beta, then fan out.
Session handoff (2026-10-14 rev 1, for the session after /clear):
- HEAD `{head}` = remote. Integrated: alpha (`{head}`), {alpha_claim} record.
- beta allocated at `{beta_sha}` (review PASS); receipt `{receipt}`.
- Pending operations: {ops}.
- Pending user: D1, D2.
- Agents running at /clear: none. Owner: start as `next-session`. Runbook: `{RV}/phase3/HANDOFF-2026-10-14.md`.

## Goal
Ship it.

## Current Phase
Phase 1: test

## Phases

### Phase 1: test
- [ ] item
- **Status:** in_progress
"""


def progress_text(next_last: bool = True) -> str:
    entry = "- 2026-10-13 (setup): fixture created.\n"
    nxt = ("- NEXT (2026-10-14 rev 1, owner: next session `next-session`; rewrite in place, keep last):\n"
           "  integrate beta; pending user D1, D2.\n")
    body = "# Progress\n\n" + entry + "\n" + nxt if next_last else "# Progress\n\n" + nxt + "\n" + entry
    return body


def handoff_text(head: str, beta_sha: str) -> str:
    return f"""# Handoff 2026-10-14: test

Intro paragraph.

## 1. State at /clear

| Item | Value |
|---|---|
| Branch | `{BRANCH}` |
| HEAD | `{head}` "fixture" |
| Remote | `origin/{BRANCH}` = `{head}` |

Worktrees:

| Worktree | HEAD | State |
|---|---|---|
| `beta` | `{beta_sha}` | allocated |

## 2. Runbook for the next session (in order)

(a) Orient: run the doctor.
(j) User-typed stages: type `/one`, then `/two`.

## 3. Deferred hunks

none

## 4. Trailer lines

Co-Authored-By: test

## 5. Decisions

D1 pending.

## 6. What this session learned

nothing yet

## 7. Pre-clear check

manual list

## 8. Start command

```sh
claude -n old
```

## 9. Research corpus

none

## 10. Legacy removals

none
"""


TEMPLATE = """# Handoff template

## action
Integrate beta, then fan out the parallel table.

## owner
Owner: start as `next-session` (HANDOFF §8).

## runbook
Runbook: `reviews/ccm-test/phase3/HANDOFF-2026-10-14.md`.

## notes
- Then in parallel: gamma,
  delta.

## state-rows
| CI | run 42 success |
"""


@contextlib.contextmanager
def pinned_git_env(home: Path):
    """Scratch HOME and global Git config, no system config, no inherited GIT_*: the caller's global hk
    hooks never run in a fixture, and the request ledger resolves under the scratch HOME (D167)."""
    home.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in ("VIRTUAL_ENV", "HK", "HK_PROFILE")}
    env.update(HOME=str(home), GIT_CONFIG_GLOBAL=str(home / ".gitconfig"), GIT_CONFIG_NOSYSTEM="1",
               GIT_TERMINAL_PROMPT="0")
    with mock.patch.dict(os.environ, env, clear=True):
        yield


def make_repo(tmp: Path) -> dict:
    """Scratch repo with origin, plan dir, two lanes (alpha integrated, beta allocated in a worktree)."""
    repo = tmp / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", BRANCH)
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "Test User")
    plan = repo / ".planning" / PLAN_ID
    (plan / "lanes").mkdir(parents=True)
    (plan / RV / "phase3").mkdir(parents=True)
    (plan / RV / "phase4-prep").mkdir(parents=True)
    (plan / ".mode").write_text("inject-smart\n")
    (plan / "task_plan.md").write_text("# placeholder\n")
    (plan / "progress.md").write_text("# Progress\n")
    (plan / "decisions.jsonl").write_text(
        json.dumps({"id": "DL-1", "kind": "operation", "receipt": None, "source": "x", "subject": "open the PR",
                    "text": "on the user's word", "ts": "2026-10-14T00:00:00Z"}) + "\n"
        + json.dumps({"id": "DL-2", "kind": "decision", "receipt": None, "source": "x", "subject": "D1",
                      "text": "decided", "ts": "2026-10-14T00:00:00Z"}) + "\n"
        # plan_decide.py closes an operation with a separate receipt row whose subject is the op id
        + json.dumps({"id": "DL-3", "kind": "operation", "receipt": None, "source": "x", "subject": "relabel",
                      "text": "done later", "ts": "2026-10-14T00:00:00Z"}) + "\n"
        + json.dumps({"id": "DL-4", "kind": "receipt", "receipt": {"path": "x", "rc": 0, "sha256": "0" * 64},
                      "source": "x", "subject": "DL-3", "text": "", "ts": "2026-10-14T00:00:00Z"}) + "\n")
    (plan / "lanes" / "alpha.json").write_text(json.dumps(
        {"unit": "alpha", "status": "integrated", "review": "PASS", "retro": "passed",
         "worktree": ".claude/worktrees/alpha", "branch": "claude/alpha", "base_sha": "0"}))
    (plan / "lanes" / "beta.json").write_text(json.dumps(
        {"unit": "beta", "status": "allocated", "review": "PASS", "retro": None,
         "worktree": ".claude/worktrees/beta", "branch": "claude/beta", "base_sha": "0"}))
    (plan / "lanes" / "gamma.json").write_text(json.dumps(
        {"unit": "gamma", "status": "allocated (sequenced: not cut)", "review": None, "retro": None,
         "worktree": ".claude/worktrees/gamma", "branch": "claude/gamma", "base_sha": "0"}))
    (plan / RV / "phase3" / "receipt.md").write_text("receipt\n")
    (repo / "README.md").write_text("fixture\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fixture")
    head = git(repo, "rev-parse", "--short=7", "HEAD")
    origin = tmp / "origin.git"
    subprocess.run([handoff.GIT, "clone", "-q", "--bare", str(repo), str(origin)], check=True, capture_output=True)
    git(repo, "remote", "add", "origin", str(origin))
    git(repo, "fetch", "-q", "origin")
    git(repo, "worktree", "add", "-q", str(repo / ".claude/worktrees/beta"), "-b", "claude/beta", "HEAD")
    wt = repo / ".claude/worktrees/beta"
    (wt / "beta.txt").write_text("beta\n")
    git(wt, "add", "-A")
    git(wt, "commit", "-q", "-m", "beta work")
    beta_sha = git(wt, "rev-parse", "--short=7", "HEAD")
    (plan / "task_plan.md").write_text(plan_text(head, beta_sha))
    (plan / "progress.md").write_text(progress_text())
    (plan / RV / "phase3" / "HANDOFF-2026-10-14.md").write_text(handoff_text(head, beta_sha))
    (plan / RV / "phase4-prep" / "newest-report.md").write_text("report\n")
    template = tmp / "template.md"
    template.write_text(TEMPLATE)
    return {"repo": repo, "plan": plan, "head": head, "beta_sha": beta_sha, "template": template}


def fake_probe(plan_root: Path, plan_id: str, context: str, smart: bool) -> dict:
    """Frames as the plugin would emit them: head-50 / smart keep-sections, progress tail-20."""
    plan = (plan_root / ".planning" / plan_id / "task_plan.md").read_text().splitlines()
    if smart:
        keep, on = [], False
        for line in plan:
            if line.startswith("## "):
                on = line in ("## Goal", "## Next Step", "## Current Phase")
            if on or line.startswith("# "):
                keep.append(line)
        keep.append("phases: 0/1 complete")
        plan = keep
    else:
        plan = plan[:30 if context == "pretool" else 50]
    progress = (plan_root / ".planning" / plan_id / "progress.md").read_text().splitlines()[-20:]
    return {"plan": plan, "progress": progress if context != "pretool" else [], "bytes": 1000, "error": None}


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="handoff-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.enterContext(pinned_git_env(self.tmp / "home"))
        self.requests = self.tmp / "home/.local/state/claude-code-marketplace/requests"
        self.fx = make_repo(self.tmp)
        self.ctx = handoff.Context(repo=self.fx["repo"], plan_id=PLAN_ID)
        self._probe = handoff.run_probe
        handoff.run_probe = fake_probe
        self.addCleanup(setattr, handoff, "run_probe", self._probe)

    def ids(self, findings):
        return sorted({f.id for f in findings})

    def check(self, agents_done=True):
        return handoff.check(self.ctx, handoff.state(self.ctx, agents_done=agents_done))


class GitEnvironmentTests(unittest.TestCase):
    def test_global_git_hooks_never_fire_in_fixtures(self):
        tmp = Path(tempfile.mkdtemp(prefix="handoff-gitenv-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        marker, hooks, home = tmp / "hook-fired", tmp / "global-hooks", tmp / "caller-home"
        hooks.mkdir()
        home.mkdir()
        for event in ("pre-commit", "commit-msg", "prepare-commit-msg", "post-commit"):
            (hooks / event).write_text(f"#!/bin/sh\necho {event} >> '{marker}'\n")
            (hooks / event).chmod(0o755)
        config = f"[core]\n\thooksPath = {hooks}\n[hook \"marker\"]\n\tevent = post-commit\n\tcommand = touch '{marker}'\n"
        (home / ".gitconfig").write_text(config)
        (tmp / "global.gitconfig").write_text(config)
        caller = {"HOME": str(home), "GIT_CONFIG_GLOBAL": str(tmp / "global.gitconfig")}
        with mock.patch.dict(os.environ, caller), pinned_git_env(tmp / "scratch-home"):
            make_repo(tmp)
        self.assertFalse(marker.exists(), marker.read_text() if marker.exists() else "")


class StateTests(Fixture):
    def test_state_fields(self):
        st = handoff.state(self.ctx, agents_done=True)
        self.assertEqual(st["head"], self.fx["head"])
        self.assertEqual(st["remote"], self.fx["head"])
        self.assertEqual((st["ahead"], st["behind"]), (0, 0))
        self.assertEqual(st["ops"], [])
        self.assertEqual(st["counts"], {"staged": 0, "unstaged": 2, "untracked": 3})
        beta = next(w for w in st["worktrees"] if w["path"].endswith("beta"))
        self.assertEqual(beta["head"], self.fx["beta_sha"])
        self.assertFalse(beta["in_head"])
        self.assertEqual({lane["unit"]: lane["integrated"] for lane in st["lanes"]},
                         {"alpha": True, "beta": False, "gamma": False})
        self.assertEqual([op["id"] for op in st["pending_operations"]], ["DL-1"])
        self.assertIn("phase4-prep/newest-report.md", st["newest_reports"][0]["path"])
        self.assertTrue(st["agents_done"])
        self.assertIsNone(st["doctor"]["cli"])

    def test_state_dirty_tree_counts(self):
        repo = self.fx["repo"]
        (repo / "README.md").write_text("changed\n")
        (repo / "new.txt").write_text("new\n")
        (repo / "staged.txt").write_text("staged\n")
        git(repo, "add", "staged.txt")
        st = handoff.state(self.ctx, agents_done=False)
        self.assertEqual(st["counts"], {"staged": 1, "unstaged": 3, "untracked": 4})
        self.assertFalse(st["agents_done"])

    def test_finding_shape(self):
        f = handoff.Finding("H.x", "P1", "s", ("e",), "fix")
        self.assertEqual(set(f.to_json()), {"id", "class", "severity", "subject", "evidence", "fix_hint", "auto_fixable"})
        self.assertEqual(f.to_json()["class"], "H")


class CheckTests(Fixture):
    def test_clean_fixture_zero_findings(self):
        self.assertEqual(self.check(), [])

    def test_agents_unconfirmed(self):
        self.assertEqual(self.ids(self.check(agents_done=False)), ["H.agents-unconfirmed"])

    def test_stale_sha(self):
        plan = self.fx["plan"] / "task_plan.md"
        plan.write_text(plan.read_text().replace(f"HEAD `{self.fx['head']}`", "HEAD `abc1234`"))
        found = self.check()
        self.assertIn("H.handoff-stale-sha", self.ids(found))
        self.assertTrue(any(f.severity == "P1" for f in found))

    def test_missing_receipt(self):
        plan = self.fx["plan"] / "task_plan.md"
        plan.write_text(plan_text(self.fx["head"], self.fx["beta_sha"], receipt=f"{RV}/phase3/gone.md"))
        self.assertEqual(self.ids(self.check()), ["H.receipt-missing"])

    def test_lane_worktree_missing(self):
        shutil.rmtree(self.fx["repo"] / ".claude/worktrees/beta")
        git(self.fx["repo"], "worktree", "prune")
        self.assertIn("H.receipt-missing", self.ids(self.check()))

    def test_closed_lane_needs_no_worktree(self):
        (self.fx["plan"] / "lanes" / "delta.json").write_text(json.dumps(
            {"unit": "delta", "status": "closed: cancelled before cut (D97)", "review": None, "retro": None,
             "worktree": ".claude/worktrees/delta", "branch": "claude/delta", "base_sha": "0"}))
        self.assertNotIn("H.receipt-missing", self.ids(self.check()))

    def test_next_not_last(self):
        (self.fx["plan"] / "progress.md").write_text(progress_text(next_last=False))
        found = self.check()
        self.assertIn("H.next-not-last", self.ids(found))
        self.assertTrue(all(f.id in ("H.next-not-last", "H.injection-probe-failed") for f in found))

    def test_head_not_remote(self):
        (self.fx["repo"] / "README.md").write_text("ahead\n")
        git(self.fx["repo"], "commit", "-qam", "ahead")
        found = self.check()
        self.assertIn("H.head-not-remote", self.ids(found))
        self.assertIn("H.handoff-stale-sha", self.ids(found))

    def test_git_op_in_progress(self):
        (self.fx["repo"] / ".git" / "MERGE_HEAD").write_text(git(self.fx["repo"], "rev-parse", "HEAD") + "\n")
        self.assertIn("H.git-op-in-progress", self.ids(self.check()))

    def test_lane_record_mismatch(self):
        plan = self.fx["plan"] / "task_plan.md"
        plan.write_text(plan.read_text().replace("beta allocated at", "beta integrated at"))
        found = [f for f in self.check() if f.id == "H.lane-record-mismatch"]
        self.assertEqual([f.severity for f in found], ["P1"])
        self.assertIn("beta", found[0].subject)

    def test_review_claim_without_record_is_p3(self):
        record = self.fx["plan"] / "lanes" / "beta.json"
        record.write_text(record.read_text().replace('"review": "PASS"', '"review": null'))
        found = [f for f in self.check() if f.id == "H.lane-record-mismatch"]
        self.assertEqual([f.severity for f in found], ["P3"])
        self.assertEqual(handoff.exit_code(found), 0)

    def test_pending_decision_unlisted(self):
        plan = self.fx["plan"] / "task_plan.md"
        plan.write_text(plan_text(self.fx["head"], self.fx["beta_sha"], ops="none"))
        found = [f for f in self.check() if f.id == "H.pending-decision-unlisted"]
        self.assertEqual(len(found), 1)
        self.assertIn("DL-1", found[0].subject)

    def test_mode_not_inject_smart_is_advisory(self):
        (self.fx["plan"] / ".mode").unlink()
        found = self.check()
        self.assertEqual(self.ids(found), ["H.mode-not-inject-smart"])
        self.assertEqual(found[0].severity, "P3")
        self.assertEqual(handoff.exit_code(found), 0)

    def test_injection_probe_failed(self):
        plan = self.fx["plan"] / "task_plan.md"
        filler = "".join(f"filler line {i}\n" for i in range(40))
        plan.write_text(plan.read_text().replace("## Next Step\n", filler + "## Next Step\n"))
        found = [f for f in self.check() if f.id == "H.injection-probe-failed"]
        self.assertTrue(found)
        self.assertEqual(found[0].severity, "P1")

    def test_probe_error_is_p2(self):
        handoff.run_probe = lambda *a, **k: {"plan": [], "progress": [], "bytes": 0, "error": "plugin missing"}
        found = [f for f in self.check() if f.id == "H.injection-probe-failed"]
        self.assertTrue(found)
        self.assertEqual({f.severity for f in found}, {"P2"})

    def test_parse_hook_output(self):
        sample = json.dumps({"hookSpecificOutput": {"additionalContext": (
            "[pwf] ACTIVE PLAN\n===BEGIN-PWF-DATA kind=plan nonce=abc bytes=10 sha256=x truncated=true===\n"
            "# Title\n## Next Step\nSession handoff (rev 1)\n===END-PWF-DATA kind=plan nonce=abc===\n\n"
            "===BEGIN-PWF-DATA kind=progress nonce=def bytes=5 sha256=y truncated=false===\n- NEXT x\n"
            "  more\n===END-PWF-DATA kind=progress nonce=def===\n")}})
        frames = handoff.parse_frames(sample)
        self.assertEqual(frames["plan"], ["# Title", "## Next Step", "Session handoff (rev 1)"])
        self.assertEqual(frames["progress"], ["- NEXT x", "  more"])


class WriteTests(Fixture):
    def render(self):
        st = handoff.state(self.ctx, agents_done=True)
        return handoff.render(self.ctx, st, handoff.load_template(self.fx["template"]))

    def test_rendered_shapes(self):
        out = self.render()
        block = out["next_step"].splitlines()
        self.assertEqual(block[0], "## Next Step")
        self.assertLessEqual(len(block), 16)
        self.assertTrue(all(len(line) <= 100 for line in block), block)
        self.assertNotIn("—", out["next_step"])
        self.assertIn(f"HEAD `{self.fx['head']}` = remote", out["next_step"])
        self.assertIn("DL-1", out["next_step"])
        self.assertIn("Pending user: none;", out["next_step"])
        self.assertIn("- Pending operations (receipt-less `decisions.jsonl` rows, HANDOFF §1): DL-1.", out["next_step"])
        self.assertIn("rev 2", out["next_step"])
        self.assertIn("Then in parallel: gamma, delta.", out["next_step"])
        bullet = out["next_bullet"].splitlines()
        self.assertTrue(bullet[0].startswith("- NEXT ("))
        self.assertLessEqual(len(bullet), 12)
        self.assertTrue(all(len(line) <= 100 for line in bullet), bullet)
        self.assertIn("`next-session`", bullet[0])

    def test_closed_lane_not_listed_as_allocated(self):
        (self.fx["plan"] / "lanes" / "delta.json").write_text(json.dumps(
            {"unit": "delta", "status": "closed: cancelled before cut (D97)", "review": None, "retro": None,
             "worktree": ".claude/worktrees/delta", "branch": "claude/delta", "base_sha": "0"}))
        st = handoff.state(self.ctx, agents_done=True)
        self.assertIn("delta:closed", handoff.brief(st))
        out = self.render()
        self.assertNotIn("delta (not cut)", out["next_step"])
        self.assertIn("closed: delta", out["next_step"])
        self.assertTrue(all(len(line) <= 100 for line in out["next_step"].splitlines()))

    def test_handoff_sections_preserved(self):
        out = self.render()
        before = handoff.split_sections(self.fx["plan"] / RV / "phase3" / "HANDOFF-2026-10-14.md")
        after = handoff.split_sections_text(out["handoff"])
        for num in ("2", "3", "4", "5", "6", "9", "10"):
            self.assertEqual(before[num], after[num], f"section {num} changed")
        self.assertNotEqual(before["1"], after["1"])
        self.assertIn("| CI | run 42 success |", after["1"])
        self.assertIn("dev/handoff.py check", after["7"])
        self.assertIn("claude -n next-session", after["8"])
        self.assertEqual(before["preamble"], after["preamble"])

    def test_write_dry_run_leaves_files(self):
        plan = self.fx["plan"] / "task_plan.md"
        before = plan.read_bytes()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = handoff.write(self.ctx, template=self.fx["template"], agents_done=True, dry_run=True)
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertEqual(plan.read_bytes(), before)
        self.assertIn("--- a/", buf.getvalue())
        self.assertIn("dry-run", buf.getvalue())

    def test_write_applies_and_check_passes(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = handoff.write(self.ctx, template=self.fx["template"], agents_done=True, dry_run=False)
        self.assertEqual(rc, 0, buf.getvalue())
        progress = (self.fx["plan"] / "progress.md").read_text()
        self.assertEqual(progress.count("- NEXT ("), 1)
        self.assertTrue(progress.rstrip().splitlines()[-1].startswith("  ") or "- NEXT (" in progress.rstrip().splitlines()[-1])
        self.assertIn("fixture created", progress)
        self.assertEqual(self.check(), [])
        self.assertIn("rev 2", (self.fx["plan"] / "task_plan.md").read_text())

    def test_write_refuses_on_findings(self):
        (self.fx["repo"] / ".git" / "MERGE_HEAD").write_text("x\n")
        plan = self.fx["plan"] / "task_plan.md"
        before = plan.read_bytes()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = handoff.write(self.ctx, template=self.fx["template"], agents_done=True, dry_run=False)
        self.assertEqual(rc, 2)
        self.assertEqual(plan.read_bytes(), before)
        self.assertIn("H.git-op-in-progress", buf.getvalue())


class OwnerAndStartTests(Fixture):
    def test_owner_rewrite(self):
        new = handoff.owner(self.ctx, session="ccm-new", session_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        text = (self.fx["plan"] / "task_plan.md").read_text()
        self.assertIn("Owner: session `ccm-new` (`aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`)", " ".join(text.split()))
        self.assertIn("previous session `old-session` (`11111111`)", " ".join(text.split()))
        self.assertIn("## Next Step", text)
        self.assertTrue(all(len(line) <= 100 for line in new.splitlines()))

    def test_start_command(self):
        line = handoff.start_command(self.ctx, name="ccm-x", session_id=None)
        self.assertIn(f"export PLAN_ID={PLAN_ID} PWF_PLAN_ROOT={self.fx['repo']}", line)
        self.assertIn("claude -n ccm-x --session-id ", line)  # the id itself: StartCommandCliTests
        self.assertIn("session-resume", line)
        self.assertIn("HANDOFF-2026-10-14.md", line)

    def test_section_start_types_resume_only_after_clear(self):
        text = handoff.section_start(self.ctx, {}, "ccm-20261014T034212.915972000-05")
        after_block = text.split("```", 2)[2]
        self.assertIn("`/clear`", after_block)
        self.assertIn("`/session-resume ccm-20261014T034212.915972000-05`", after_block)
        self.assertIn("never both", after_block)
        self.assertNotIn("type the same prompt", text)
        self.assertTrue(all(len(line) <= 100 for line in after_block.splitlines()), after_block)

    def test_skill_report_types_resume_only_after_clear(self):
        step = (ROOT / ".claude/skills/session-handoff/SKILL.md").read_text().split("5. **Report.**", 1)[1]
        prose = " ".join(step.split())
        self.assertIn("`/session-resume <name>`", prose)
        self.assertIn("never after the start command", prose)
        self.assertNotIn("the next session begins with `/session-resume", prose)


class CliTests(Fixture):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = handoff.main(["--repo", str(self.fx["repo"]), "--plan-id", PLAN_ID, *args])
        return rc, out.getvalue(), err.getvalue()

    def test_check_exit_codes(self):
        rc, out, _ = self.run_cli("check", "--json", "--agents-done")
        self.assertEqual(rc, 0, out)
        self.assertEqual(json.loads(out)["findings"], [])
        rc, out, _ = self.run_cli("check", "--json")
        self.assertEqual(rc, 2)
        self.assertEqual([f["id"] for f in json.loads(out)["findings"]], ["H.agents-unconfirmed"])

    def test_state_json_and_brief(self):
        rc, out, _ = self.run_cli("state", "--json")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["head"], self.fx["head"])
        rc, out, _ = self.run_cli("state", "--brief")
        self.assertEqual(rc, 0)
        self.assertIn(self.fx["head"], out)
        self.assertLessEqual(len(out.splitlines()), 20)

    def test_usage_error_is_1(self):
        with self.assertRaises(SystemExit) as caught:
            self.run_cli("bogus")
        self.assertEqual(caught.exception.code, 1)


NAME_RE = r"ccm-\d{8}T\d{6}\.\d{9}[+-]\d{2}"  # D61: local %Y%m%dT%H%M%S.%N, hour offset
FAKE_STAMP = "20261014T184849.575921000-0500"


def fake_date(bin_dir: Path, stamp: str = FAKE_STAMP, rc: int = 0, stderr: str = "", sleep: float = 0) -> Path:
    """A `date` on PATH that logs its argv, sleeps `sleep` seconds, prints `stamp` (stdout) and `stderr`, and
    exits `rc`; returns the log path."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    log = bin_dir / "date.log"
    (bin_dir / "date").write_text(f"#!/bin/sh\nprintf '%s\\n' \"$*\" >> '{log}'\n" + (f"sleep {sleep}\n" if sleep else "")
                                  + (f"printf '%s\\n' '{stamp}'\n" if stamp else "")
                                  + (f"printf '%s\\n' '{stderr}' >&2\n" if stderr else "") + f"exit {rc}\n")
    (bin_dir / "date").chmod(0o755)
    return log


class SubprocessCli(Fixture):
    """`python3 -I dev/handoff.py ...` as a child process in the fixture's scrubbed environment."""

    def cli(self, *args, path_first: Path | None = None):
        env = dict(os.environ)
        if path_first:
            env["PATH"] = f"{path_first}{os.pathsep}{env.get('PATH', '')}"
        result = subprocess.run([sys.executable, "-I", str(DEV / "handoff.py"), "--repo", str(self.fx["repo"]),
                                 "--plan-id", PLAN_ID, *args], capture_output=True, text=True, env=env, timeout=60)
        return result.returncode, result.stdout, result.stderr


class NextNameTests(SubprocessCli):
    def test_next_name_is_one_os_date_call_cut_to_the_hour_offset(self):
        log = fake_date(self.tmp / "bin")
        rc, out, err = self.cli("next-name", path_first=self.tmp / "bin")
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(out, "ccm-20261014T184849.575921000-05\n")
        self.assertEqual(log.read_text().splitlines(), ["+%Y%m%dT%H%M%S.%N%z"])

    def test_next_name_from_the_host_date_has_the_d61_shape(self):
        rc, out, err = self.cli("next-name")
        self.assertEqual(rc, 0, err)
        self.assertRegex(out, rf"\A{NAME_RE}\n\Z")

    def test_a_date_without_nanoseconds_is_refused(self):
        fake_date(self.tmp / "bin", stamp="20261014T184849.N-0500")
        rc, out, err = self.cli("next-name", path_first=self.tmp / "bin")
        self.assertEqual((rc, out), (2, ""))
        self.assertIn("date output does not match", err)

    def test_a_date_that_exits_nonzero_is_refused_naming_its_exit_and_stderr(self):
        # P3 (cold review): a stamp on stdout with rc 1 was accepted; rc 1 with no output blamed %N
        for stamp, stderr in ((FAKE_STAMP, "date: illegal option -- N"), ("", "")):
            with self.subTest(stamp=bool(stamp)):
                fake_date(self.tmp / "bin", stamp=stamp, rc=1, stderr=stderr)
                rc, out, err = self.cli("next-name", path_first=self.tmp / "bin")
                self.assertEqual((rc, out), (2, ""), err)
                self.assertIn("date exited 1", err)
                self.assertIn(stderr, err)
                self.assertNotIn("%N?", err)

    def test_a_hung_date_is_refused_not_an_error(self):
        fake_date(self.tmp / "bin", sleep=5)
        with mock.patch.dict(os.environ, {"PATH": f"{self.tmp / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}"}), \
                mock.patch.object(handoff, "DATE_TIMEOUT_S", 0.2):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = handoff.main(["--repo", str(self.fx["repo"]), "--plan-id", PLAN_ID, "next-name"])
        self.assertEqual((rc, out.getvalue()), (2, ""), err.getvalue())
        self.assertIn("date did not answer within 0.2 s", err.getvalue())


class StartCommandCliTests(SubprocessCli):
    UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"

    def test_default_name_is_a_fresh_next_name_never_the_owner(self):
        fake_date(self.tmp / "bin")
        rc, out, err = self.cli("start-command", path_first=self.tmp / "bin")
        self.assertEqual(rc, 0, err)
        self.assertIn("claude -n ccm-20261014T184849.575921000-05 ", out)
        self.assertNotIn("old-session", out)

    def test_printed_command_fixes_a_session_id_and_hands_it_to_owner(self):
        rc, out, err = self.cli("start-command", "--name", "ccm-x")
        self.assertEqual(rc, 0, err)
        launch = out.splitlines()[-1]
        sid = re.search(rf"^claude -n ccm-x --session-id ({self.UUID}) \"", launch)
        self.assertTrue(sid, launch)
        self.assertIn(f"dev/handoff.py owner --session ccm-x --session-id {sid[1]}", launch)
        given = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
        rc, out, _ = self.cli("start-command", "--name", "ccm-x", "--session-id", given)
        self.assertIn(f"claude -n ccm-x --session-id {given} \"", out)
        self.assertIn(f"owner --session ccm-x --session-id {given}", out)

    def test_a_session_id_that_is_not_a_uuid_is_a_usage_error(self):
        # P3 (cold review): `claude --session-id <uuid>` (2.1.300 --help) takes only a valid UUID
        before = (self.fx["plan"] / "task_plan.md").read_text()
        for args in (("start-command", "--name", "ccm-x"), ("owner", "--session", "ccm-new")):
            with self.subTest(command=args[0]):
                rc, out, err = self.cli(*args, "--session-id", "abc")
                self.assertEqual((rc, out), (1, ""), err)
                self.assertIn("--session-id: not a UUID: 'abc'", err)
        self.assertEqual((self.fx["plan"] / "task_plan.md").read_text(), before)

    def test_owner_records_the_given_session_id(self):
        rc, out, err = self.cli("owner", "--session", "ccm-new", "--session-id", "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee")
        self.assertEqual(rc, 0, err)
        text = " ".join((self.fx["plan"] / "task_plan.md").read_text().split())
        self.assertIn("Owner: session `ccm-new` (`aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee`)", text)


# Lane handoff-skills' name-free owner sentence (`claude/handoff-skills` 521b3e7, verbatim) over the scratch
# fixture's other sections: no backticked span, so `write` must generate the next session's name (HS-3).
NAME_FREE_OWNER = """Owner: start with the HANDOFF §8 command (a fresh next-name, D61, D76); rewrite owner line 4 with
dev/handoff.py owner.
"""
NAME_FREE_TEMPLATE = TEMPLATE.replace("Owner: start as `next-session` (HANDOFF §8).\n", NAME_FREE_OWNER)
assert "`" not in NAME_FREE_OWNER and NAME_FREE_TEMPLATE != TEMPLATE


class WriteNameFreeTests(SubprocessCli):
    def dry_run(self, template_text: str):
        template = self.tmp / "name-free-template.md"
        template.write_text(template_text)
        log = fake_date(self.tmp / "bin")
        fake_plugin(self.tmp / "pwf")  # the child runs the real injection probe
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(self.tmp / "pwf")}):
            rc, out, err = self.cli("write", "--dry-run", "--agents-done", "--template", str(template),
                                    path_first=self.tmp / "bin")
        return rc, out, err, log

    def test_a_name_free_template_gets_a_fresh_next_name_in_the_block_bullet_and_start_command(self):
        rc, out, err, log = self.dry_run(NAME_FREE_TEMPLATE)
        self.assertEqual(rc, 0, out + err)
        added = "\n".join(l[1:] for l in out.splitlines() if l.startswith("+") and not l.startswith("+++"))
        self.assertNotIn("next-session", added)
        self.assertIn("owner: next session `ccm-20261014T184849.575921000-05`", added)
        self.assertIn("/session-resume ccm-20261014T184849.575921000-05", added)
        self.assertRegex(added, rf"claude -n ccm-20261014T184849\.575921000-05 --session-id {StartCommandCliTests.UUID} \"")
        self.assertEqual(log.read_text().splitlines(), ["+%Y%m%dT%H%M%S.%N%z"])

    def test_a_backticked_owner_name_is_still_used(self):
        rc, out, err, log = self.dry_run(TEMPLATE)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("owner: next session `next-session`", out)
        self.assertRegex(out, rf"claude -n next-session --session-id {StartCommandCliTests.UUID} \"")
        self.assertFalse(log.exists(), "date was called although the template named the session")


def fake_plugin(root: Path, drop_source: str = "") -> Path:
    """A planning-with-files cache stand-in: the session-start hook logs each payload's `source` and emits
    head-50/tail-20 frames unless the source is `drop_source`; the pretool twin emits head-30."""
    log = root / "sources.log"
    (root / "hooks").mkdir(parents=True)
    (root / "scripts").mkdir()
    frames = ('plan="$PWF_PLAN_ROOT/.planning/$PLAN_ID"\n'
              "echo '===BEGIN-PWF-DATA kind=plan nonce=n==='\nhead -50 \"$plan/task_plan.md\"\n"
              '[ "$PWF_INJECT" = smart ] && echo "phases: 0/1 complete"\n'
              "echo '===END-PWF-DATA kind=plan nonce=n==='\necho '===BEGIN-PWF-DATA kind=progress nonce=p==='\n"
              "tail -20 \"$plan/progress.md\"\necho '===END-PWF-DATA kind=progress nonce=p==='\n")
    (root / "hooks/claude-hook.sh").write_text(
        "src=$(sed -n 's/.*\"source\": \"\\([a-z]*\\)\".*/\\1/p')\n"
        f"printf '%s\\n' \"$src\" >> '{log}'\n[ \"$src\" = '{drop_source}' ] && exit 0\n" + frames)
    (root / "scripts/inject-plan.py").write_text(
        "import os\nfrom pathlib import Path\n"
        "plan = Path(os.environ['PWF_PLAN_ROOT']) / '.planning' / os.environ['PLAN_ID'] / 'task_plan.md'\n"
        "print('===BEGIN-PWF-DATA kind=plan nonce=n===')\nprint('\\n'.join(plan.read_text().splitlines()[:30]))\n"
        "print('===END-PWF-DATA kind=plan nonce=n===')\n")
    return log


class StartupProbeTests(SubprocessCli):
    def probe_check(self, drop_source: str = ""):
        log = fake_plugin(self.tmp / "pwf", drop_source)
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(self.tmp / "pwf")}):
            rc, out, err = self.cli("check", "--json", "--agents-done")
        return rc, json.loads(out or "{}"), sorted(log.read_text().split()), err

    def test_probe_fires_session_start_for_startup_as_well_as_clear(self):
        rc, data, sources, err = self.probe_check()
        self.assertEqual((rc, data.get("findings")), (0, []), err)
        self.assertEqual(sources, ["clear", "clear", "startup"])

    def test_a_restart_that_injects_no_plan_is_caught(self):
        rc, data, sources, _ = self.probe_check(drop_source="startup")
        self.assertEqual(rc, 2)
        found = [(f["id"], f["subject"]) for f in data["findings"]]
        self.assertEqual(found, [("H.injection-probe-failed", "startup probe did not run: no plan frame emitted")])


class DoctorContextLineTests(Fixture):
    def test_context_line_names_the_quit_and_restart_path(self):
        doctor_ctx = mock.Mock(repo=str(self.fx["repo"]), plan_id=PLAN_ID, findings=())
        [line] = handoff.context_lines(doctor_ctx)
        self.assertIn("handoff: HANDOFF-2026-10-14.md §2 · check PASS (0 H findings)", line)
        self.assertIn("/quit, then the §8 start command", line)
        self.assertIn("/session-resume <name> after /clear", line)
        self.assertNotIn("after /clear only", line)


OWNER_ID = "11111111-2222-3333-4444-555555555555"


class RequestTests(Fixture):
    """D167 request catch through the CLI seam: ledger rows vs `## Open requests` items."""
    run_cli = CliTests.run_cli

    def check_json(self):
        rc, out, _ = self.run_cli("check", "--json", "--agents-done")
        data = json.loads(out)
        return rc, [(f["id"], f["severity"]) for f in data["findings"]], data

    def capture(self, *rows, name="ledger.jsonl"):
        self.requests.mkdir(parents=True, exist_ok=True)
        with (self.requests / name).open("a") as fh:
            fh.writelines(json.dumps(row) + "\n" for row in rows)

    def project(self, *items):
        plan = self.fx["plan"] / "task_plan.md"
        section = "## Open requests (D160)\n\nIntro.\n\n" + "".join(f"{item}\n" for item in items) + "\n"
        plan.write_text(plan.read_text().replace("## Goal\n", section + "## Goal\n"))

    def test_unprojected_capture_is_p1(self):
        self.capture({"session_id": OWNER_ID, "prompt_id": "4462d3b1-aaaa", "prompt": "build the skill"},
                     {"session_id": "other-session", "prompt_id": "99999999-bbbb", "prompt": "a fork's ask"})
        rc, found, data = self.check_json()
        self.assertEqual((rc, found), (2, [("H.request-unprojected", "P1")]))
        self.assertIn("p:4462d3b1", data["findings"][0]["subject"])
        self.assertNotIn("build the skill", json.dumps(data))  # never the prompt text
        self.assertEqual(data["requests"]["unprojected"], ["p:4462d3b1"])
        self.assertEqual((data["requests"]["captured"], data["requests"]["foreign"]), (1, 1))  # the fork's row: counted, not caught
        self.capture({"session_id": OWNER_ID, "prompt": "a payload without a key field"})
        self.assertEqual(self.check_json()[2]["requests"]["unkeyed"], 1)

    def test_foreign_session_rows_are_counted_not_caught(self):
        # a stale owner line scopes every row out (CL4 §4.5); `foreign` makes the mismatch visible until CT-93a
        self.capture({"session_id": "worktree-session", "prompt_id": "77777777-cccc"},
                     {"session_id": "fork-session", "prompt_id": "88888888-dddd"})
        rc, found, data = self.check_json()
        self.assertEqual((rc, found), (0, []))
        self.assertEqual((data["requests"]["captured"], data["requests"]["foreign"]), (0, 2))
        self.assertEqual(data["requests"]["session"], OWNER_ID)

    def test_answer_row_is_keyed_by_its_tool_use_not_its_turn(self):
        # CT-87 receipt: prompt_id is on every payload of a turn, so an answer row carries both fields
        self.capture({"session_id": OWNER_ID, "prompt_id": "4462d3b1-aaaa", "hook_event_name": "UserPromptSubmit"},
                     *({"session_id": OWNER_ID, "prompt_id": "4462d3b1-aaaa", "tool_use_id": f"toolu_01Xq{tail}",
                        "hook_event_name": "PostToolUse", "tool_name": "AskUserQuestion"} for tail in ("Ab3dEf7h", "Zz9yXx1w")))
        self.project("- [ ] R-1 · p:4462d3b1 · D1 · the prompt's ask; issue: #12",
                     "- [ ] R-2 · p:Ab3dEf7h · D1 · the first answer; issue: #13")
        rc, found, data = self.check_json()
        self.assertEqual((rc, found), (2, [("H.request-unprojected", "P1")]))
        self.assertEqual(data["requests"]["unprojected"], ["p:Zz9yXx1w"])  # answer keys: the last 8 characters

    def test_projection_or_disposition_closes_the_catch(self):
        self.capture({"session_id": OWNER_ID, "prompt_id": "4462d3b1-aaaa"},
                     {"session_id": OWNER_ID, "prompt_id": "4462d3b1-aaaa", "tool_use_id": "toolu_01XqAb3dEf7h",
                      "tool_name": "AskUserQuestion"})
        self.capture({"key": "p:Ab3dEf7h", "disposition": "noted", "ref": "chat", "ts": "x"}, name="dispositions.jsonl")
        self.project("- [ ] R-1 · p:4462d3b1 · D1 · build the skill; issue: #12")
        self.assertEqual(self.check_json()[:2], (0, []))

    def test_open_item_without_issue_link_is_p2(self):
        self.capture({"session_id": OWNER_ID, "prompt_id": "4462d3b1-aaaa"})
        self.project("- [ ] R-119 (D114): claude-agent intake skill (p:4462d3b1); issue: none yet",
                     "- [ ] R-120 (D114): visual artifact, see upstream #102134; issue: none yet",
                     "- [ ] R-121 · p:abcdef12 · D1 · CT-9 · issue: #42 · linked",
                     "- [x] R-100 (D90): done without an issue; done: `abc1234`, rc 0")
        rc, found, data = self.check_json()
        self.assertEqual((rc, found), (2, [("H.request-unlinked", "P2")]))
        self.assertIn("R-119, R-120", data["findings"][0]["subject"])
        self.assertNotIn("R-121", data["findings"][0]["subject"])
        self.assertEqual(data["requests"]["open"], ["R-119", "R-120", "R-121"])
        self.assertEqual(data["requests"]["unlinked"], ["R-119", "R-120"])

    def test_bare_issue_field_links_an_item(self):
        # CL4 §4.2 line shape: `#N` is its own `·` field; a bare number inside prose is not a link
        self.project("- [ ] R-171 · p:4462d3b1 · D114 · CT-86 · #136 · owner parent · blocked by R-127 · text",
                     "- [ ] R-172 · D148 · none · #137",
                     "- [ ] R-173 · D109 · none · pending issue · owner user · see #109 in the republish notes")
        rc, found, data = self.check_json()
        self.assertEqual((rc, found), (2, [("H.request-unlinked", "P2")]))
        self.assertEqual(data["requests"]["unlinked"], ["R-173"])

    def write_dry_run(self):
        rc, out, err = self.run_cli("write", "--dry-run", "--agents-done", "--template", str(self.fx["template"]))
        return rc, " ".join(out.replace("\n+", "\n").split()), err

    def test_write_dry_run_rolls_call_and_generates_pending_user(self):
        self.project("- [ ] R-7 · p:4462d3b1 · D1 · owner user · type /to-tickets; issue: #7",
                     "- [ ] R-8 · D2 · owner parent · build it; issue: #8", "- [x] R-9 · done: rc 0")
        rc, out, err = self.write_dry_run()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("- Open requests: 2 open, 0 unlinked, 0/0 captured unprojected (no ledger); Pending user: R-7; "
                      "ids: R-7, R-8.", out)
        self.assertIn("dry-run: 3 file(s) would be written", out)

    def test_write_refuses_a_hand_written_pending_user_section(self):
        template = self.fx["template"]
        template.write_text(template.read_text() + "\n## pending-user\nPending user: D1.\n")
        rc, _, err = self.write_dry_run()
        self.assertEqual(rc, 1)
        self.assertIn("`pending-user` is generated", err)

    def test_write_refuses_when_the_roll_call_overflows_the_block(self):
        self.project(*(f"- [ ] R-{n} · D1 · item; issue: #{n}" for n in range(1000, 1100)))
        rc, out, err = self.write_dry_run()
        self.assertEqual(rc, 1, out)
        self.assertIn("the open-request roll-call takes", err)

    def test_absent_ledger_is_reported_not_a_finding(self):
        rc, found, data = self.check_json()
        self.assertEqual((rc, found), (0, []))
        self.assertFalse(data["requests"]["ledger_present"])
        self.assertTrue(data["requests"]["ledger"].endswith("claude-code-marketplace/requests/ledger.jsonl"))
        self.assertEqual(data["requests"]["captured"], 0)


class SkillFilesTests(unittest.TestCase):
    SKILLS = ("session-handoff", "session-resume")

    def test_mirrors_identical(self):
        for name in self.SKILLS:
            a, b = ROOT / ".claude/skills" / name, ROOT / ".agents/skills" / name
            self.assertTrue(a.is_dir(), a)
            result = subprocess.run(["diff", "-r", str(a), str(b)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_evals_reference_real_subcommands(self):
        for name in self.SKILLS:
            data = json.loads((ROOT / ".claude/skills" / name / "evals/evals.json").read_text())
            self.assertEqual(data["skill_name"], name)
            self.assertGreaterEqual(len(data["evals"]), 2)
            for item in data["evals"]:
                self.assertTrue(item["prompt"] and item["expected_output"] and item["expectations"])

    def test_template_sections(self):
        template = handoff.load_template(ROOT / ".claude/skills/session-handoff/references/handoff-template.md")
        self.assertEqual(set(template) >= {"action", "owner", "runbook"}, True)


@unittest.skipUnless(handoff.plugin_root(), "planning-with-files cache not installed")
class LiveProbeTests(unittest.TestCase):
    def test_live_probe_emits_frames(self):
        ctx = handoff.Context(repo=ROOT, plan_id=os.environ.get("PLAN_ID") or handoff.PLAN_ID)
        frames = handoff.run_probe(ctx.root, ctx.plan_id, "userprompt", smart=False)
        self.assertIsNone(frames["error"], frames)
        self.assertTrue(any(line.startswith("## Next Step") for line in frames["plan"]))


if __name__ == "__main__":
    unittest.main()
