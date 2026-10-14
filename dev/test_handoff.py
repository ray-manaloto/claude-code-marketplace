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
import shutil
import subprocess
import sys
import tempfile
import unittest

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
Owner: start as `next-session` (HANDOFF §8); rewrite the owner line.

## pending-user
Pending user: D1, D2; the typed stages (HANDOFF §2(j)).

## runbook
Runbook: `reviews/ccm-test/phase3/HANDOFF-2026-10-14.md`.

## notes
- Then in parallel: gamma,
  delta.

## state-rows
| CI | run 42 success |
"""


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
        self.fx = make_repo(self.tmp)
        self.ctx = handoff.Context(repo=self.fx["repo"], plan_id=PLAN_ID)
        self._probe = handoff.run_probe
        handoff.run_probe = fake_probe
        self.addCleanup(setattr, handoff, "run_probe", self._probe)

    def ids(self, findings):
        return sorted({f.id for f in findings})

    def check(self, agents_done=True):
        return handoff.check(self.ctx, handoff.state(self.ctx, agents_done=agents_done))


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
        self.assertIn("Pending user: D1, D2", out["next_step"])
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
        self.assertIn('claude -n ccm-x "', line)
        self.assertIn("session-resume", line)
        self.assertIn("HANDOFF-2026-10-14.md", line)
        self.assertNotIn("--session-id", line)
        self.assertIn("--session-id abc", handoff.start_command(self.ctx, name="ccm-x", session_id="abc"))

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
        self.assertEqual(set(template) >= {"action", "owner", "pending-user", "runbook"}, True)


@unittest.skipUnless(handoff.plugin_root(), "planning-with-files cache not installed")
class LiveProbeTests(unittest.TestCase):
    def test_live_probe_emits_frames(self):
        ctx = handoff.Context(repo=ROOT, plan_id=os.environ.get("PLAN_ID") or handoff.PLAN_ID)
        frames = handoff.run_probe(ctx.root, ctx.plan_id, "userprompt", smart=False)
        self.assertIsNone(frames["error"], frames)
        self.assertTrue(any(line.startswith("## Next Step") for line in frames["plan"]))


if __name__ == "__main__":
    unittest.main()
