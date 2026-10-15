"""Seam tests for the ticket-frontier skill script (stdlib only, hermetic).

Every call runs `python3 -I scripts/frontier.py` as a subprocess against a
temporary repository tree, so the tests see exactly what the parent sees: exit
codes, stdout, and the files written under `.planning/<plan>/frontier/`.
Nothing here reads the real plan directory or the network.
"""

import filecmp
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude/skills/ticket-frontier"
MIRROR = ROOT / ".agents/skills/ticket-frontier"
SCRIPT = SKILL / "scripts/frontier.py"
GRAPH = SKILL / "evals/fixtures/graph-12.json"
CONFIG = ROOT / ".planning/2026-10-10-marketplace-macos-reflection-scaffold/frontier.toml"
PLAN = "test-plan"
SCRUBBED = ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "MARKETPLACE_PYTHON", "PLAN_ID", "PWF_PLAN_ROOT")


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED}
    env.update(extra)
    return env


def lane(unit, tickets, status, retro=None, owned=(), excluded=()):
    record = {"unit": unit, "tickets": list(tickets), "title": unit, "owner": "implementer",
              "writer_model": "opus", "reviewer": "reviewer (fable, cold)",
              "worktree": f".claude/worktrees/{unit}", "branch": f"claude/{unit}-x", "base_sha": "0" * 7,
              "owned_paths": list(owned), "excluded_shared_paths": list(excluded), "required_checks": [],
              "resource_admissions": {}, "status": status, "created_at": "2026-10-13T00:00:00Z"}
    if retro:
        record["retro"] = retro
    return record


class FrontierCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="frontier-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        self.plan = self.repo / ".planning" / PLAN
        (self.plan / "lanes").mkdir(parents=True)
        shutil.copy(CONFIG, self.plan / "frontier.toml")
        shutil.copy(GRAPH, self.plan / "graph.json")

    def run_cli(self, *args, env=None, stdin=None):
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), "--repo", str(self.repo), "--plan-id", PLAN,
                                 *args], cwd=self.tmp, env=env or clean_env(), input=stdin,
                                capture_output=True, text=True, timeout=60, check=False)
        return result.returncode, result.stdout, result.stderr

    def plan_json(self, *args):
        rc, out, err = self.run_cli("plan", "--graph", str(self.plan / "graph.json"), "--json", *args)
        self.assertEqual(rc, 0, out + err)
        return json.loads(out)

    def write_lane(self, record):
        (self.plan / "lanes" / f"{record['unit']}.json").write_text(json.dumps(record), encoding="utf-8")

    def claim(self, unit, ticket, role="implementer", *extra):
        return self.run_cli("claim", unit, "--ticket", ticket, "--role", role, *extra)


class PlanTests(FrontierCase):
    def test_ready_set_excludes_blocked_and_done(self):
        plan = self.plan_json()
        ready = [t["id"] for t in plan["ready"]]
        self.assertIn("#21", ready)
        self.assertNotIn("#22", ready, "blocked by #21")
        self.assertNotIn("CT-05", ready, "closed in the tracker")
        self.assertNotIn("CT-17", ready, "blocked by CT-15, which is open")
        self.assertEqual(plan["ready_order"], ["CT-15", "#16", "#21", "#17", "#20"])

    def test_priority_rules_are_recorded(self):
        plan = self.plan_json()
        first = plan["ready"][0]
        self.assertEqual(first["id"], "CT-15")
        self.assertEqual(first["critical_path"], 3)
        self.assertEqual(first["unblocks"], 2)
        self.assertEqual(plan["priority_rules"], ["critical_path", "unblocks", "always_active", "wave", "number"])

    def test_integrated_lane_with_passed_retro_unblocks_dependents(self):
        self.write_lane(lane("l21", ["#21"], "integrated", retro="passed"))
        plan = self.plan_json()
        ready = [t["id"] for t in plan["ready"]]
        self.assertNotIn("#21", ready)
        self.assertIn("#22", ready)

    def test_integrated_lane_without_passed_retro_still_holds(self):
        self.write_lane(lane("l21", ["#21"], "integrated", retro="pending"))
        ready = [t["id"] for t in self.plan_json()["ready"]]
        self.assertNotIn("#22", ready)
        self.assertNotIn("#21", ready, "claimed by a lane record, not re-dispatched")

    def test_cxx_slot_without_admission_takes_offline_portion(self):
        plan = self.plan_json()
        slot = plan["cxx_slot"]
        self.assertEqual(slot["ticket"], "#21", "heavy order #21 → #20 → #17 → #16")
        self.assertFalse(slot["admitted"])
        self.assertEqual(slot["split"], "offline-portion")
        self.assertIn("offline-portion of #21; heavy run not admitted", slot["note"])
        self.assertEqual(plan["chosen"][0]["unit"], "21-offline")
        self.assertEqual([c["ticket"] for c in plan["chosen"]], ["#21", "CT-15"],
                         "one heavy run at a time: #16 waits for its own admission")
        skipped = next(s for s in plan["skipped"] if s["ticket"] == "#16")
        self.assertIn("heavy", skipped["reason"])
        self.assertTrue(any("admission" in q for q in plan["questions"]), plan["questions"])

    def test_cxx_slot_with_admission_is_a_full_lane(self):
        plan = self.plan_json("--admitted", "#21")
        self.assertTrue(plan["cxx_slot"]["admitted"])
        self.assertIsNone(plan["cxx_slot"]["split"])
        self.assertEqual(plan["chosen"][0]["unit"], "21")
        self.assertFalse(any("admission" in q for q in plan["questions"]))

    def test_max_parallel_counts_writer_lanes_only(self):
        for unit, ticket in (("a", "CT-11"), ("b", "#17"), ("c", "#20")):
            rc, out, err = self.claim(unit, ticket)
            self.assertEqual(rc, 0, out + err)
        rc, out, err = self.claim("r1", "#17", "reviewer")
        self.assertEqual(rc, 0, out + err)
        plan = self.plan_json()
        self.assertEqual(plan["capacity"]["writers_active"], 3)
        self.assertEqual(plan["capacity"]["writers_free"], 0)
        self.assertEqual(plan["capacity"]["live_agents"], 4)
        self.assertEqual(plan["chosen"], [])
        self.assertIn("saturated", plan["capacity"]["state"])
        rc, out, err = self.run_cli("next", "--graph", str(self.plan / "graph.json"))
        self.assertEqual(rc, 2, out + err)
        self.assertIn("max_parallel", out)

    def test_live_agent_hard_cap_is_five(self):
        """roster-v2 review: CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6 refuses a 7th spawn; 5 leaves a fork slot."""
        for n in range(5):
            rc, out, err = self.claim(f"x{n}", "#17", "reviewer" if n else "implementer")
            self.assertEqual(rc, 0, out + err)
        rc, out, err = self.claim("x5", "#17", "reviewer")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("5 live agents", out)

    def test_plan_receipt_is_written_only_under_frontier_dir(self):
        rc, out, err = self.run_cli("plan", "--graph", str(self.plan / "graph.json"), "--write")
        self.assertEqual(rc, 0, out + err)
        receipts = sorted((self.plan / "frontier").glob("plan-*.json"))
        self.assertEqual(len(receipts), 1)
        receipt = json.loads(receipts[0].read_text())
        self.assertEqual(receipt["ready_order"][0], "CT-15")
        written = {p.relative_to(self.repo).as_posix() for p in self.repo.rglob("*") if p.is_file()}
        self.assertTrue(all(p.startswith(f".planning/{PLAN}/frontier/") for p in written
                            if p.startswith(f".planning/{PLAN}/") and "frontier/" in p))

    def test_threshold_mismatch_with_budget_py_is_refused(self):
        budget = self.repo / "dev/doctor/budget.py"
        budget.parent.mkdir(parents=True)
        budget.write_text('THRESHOLDS = {"warn": 220_000, "checkpoint": 303_000, "fork_deny": 250_000, "hard": 358_000}\n')
        rc, out, err = self.run_cli("plan", "--graph", str(self.plan / "graph.json"))
        self.assertEqual(rc, 2, out + err)
        self.assertIn("threshold mismatch", out)
        self.assertIn("250000", out)
        self.assertIn("275000", out)
        budget.write_text('THRESHOLDS = {"fork_deny": 275_000}\n')
        rc, out, err = self.run_cli("plan", "--graph", str(self.plan / "graph.json"))
        self.assertEqual(rc, 0, out + err)

    def test_conflicting_owned_paths_are_not_chosen(self):
        self.write_lane(lane("hooks", ["CT-11"], "implementing", owned=["dev/hooks/", "dev/test_hooks.py"],
                             excluded=["dev/check.py"]))
        graph = json.loads((self.plan / "graph.json").read_text())
        for t in graph["tickets"]:
            if t["id"] == "CT-15":
                t["owned_paths"] = ["dev/check.py", "dev/plan_records.py"]
        (self.plan / "graph.json").write_text(json.dumps(graph))
        plan = self.plan_json()
        self.assertNotIn("CT-15", [c["ticket"] for c in plan["chosen"]])
        conflict = next(c for c in plan["conflicts"] if c["ticket"] == "CT-15")
        self.assertIn("dev/check.py", conflict["paths"])
        self.assertEqual(conflict["with"], "hooks")


class NextTests(FrontierCase):
    def test_next_returns_model_effort_and_ceiling(self):
        rc, out, err = self.run_cli("next", "--graph", str(self.plan / "graph.json"), "--json")
        self.assertEqual(rc, 0, out + err)
        nxt = json.loads(out)
        self.assertEqual(nxt["unit"], "21-offline")
        self.assertEqual(nxt["role"], "implementer")
        self.assertEqual((nxt["model"], nxt["effort"]), ("opus", "high"))
        self.assertEqual(nxt["rule"], "policy.implement")
        self.assertEqual(nxt["ceiling"], 275000)
        self.assertIn("CTX-CEILING: 275000", nxt["brief_lines"][0])
        self.assertEqual(nxt["dispatch"]["subagent_type"], "implementer")
        self.assertTrue(nxt["dispatch"]["run_in_background"])

    def test_shipped_policy_reviews_on_opus(self):
        """D189: frontier.toml [model_policy] review feeds the per-call model that overrides reviewer.md."""
        policy = tomllib.loads(CONFIG.read_text())["model_policy"]
        self.assertEqual((policy["review"]["model"], policy["review"]["effort"]), ("opus", "high"))

    def test_fable_kinds_match_shipped_policy(self):
        """compaction-40 retro: the escalation guard skips exactly the kinds frontier.toml already puts on fable."""
        sys.dont_write_bytecode = True  # keep __pycache__ out of the skill dir so the mirror diff stays clean
        spec = importlib.util.spec_from_file_location("frontier_script", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        policy = tomllib.loads(CONFIG.read_text())["model_policy"]
        fable = {kind for kind, entry in policy.items() if isinstance(entry, dict) and entry.get("model") == "fable"}
        self.assertEqual(set(module.FABLE_KINDS), fable)

    def test_escalation_to_fable_after_one_opus_reasoning_failure(self):
        journal = self.tmp / "21-offline.jsonl"
        journal.write_text(json.dumps({"agent_type": "implementer", "model": "opus", "task_status": "partial",
                                       "reason": "reasoning", "unit": "21-offline"}) + "\n")
        rc, out, err = self.run_cli("next", "--graph", str(self.plan / "graph.json"), "--journal", str(journal), "--json")
        self.assertEqual(rc, 0, out + err)
        nxt = json.loads(out)
        self.assertEqual((nxt["model"], nxt["rule"]), ("fable", "escalation"))

    def test_no_escalation_for_admission_conflict_or_ceiling_reasons(self):
        journal = self.tmp / "21-offline.jsonl"
        lines = [json.dumps({"agent_type": "implementer", "model": "opus", "task_status": "blocked", "reason": r})
                 for r in ("admission", "conflict", "ceiling")]
        journal.write_text("\n".join(lines) + "\n")
        rc, out, err = self.run_cli("next", "--graph", str(self.plan / "graph.json"), "--journal", str(journal), "--json")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(json.loads(out)["model"], "opus")


class ClaimReleaseTests(FrontierCase):
    def test_claim_is_idempotent_and_refuses_double_claim(self):
        rc, out, _ = self.claim("l21", "#21")
        self.assertEqual(rc, 0, out)
        rc, out, _ = self.claim("l21", "#21")
        self.assertEqual(rc, 0, out)
        self.assertIn("already claimed", out)
        rc, out, _ = self.claim("other", "#21")
        self.assertEqual(rc, 2, out)
        self.assertIn("already claimed by l21", out)
        rc, out, _ = self.claim("l21", "#20")
        self.assertEqual(rc, 2, out)
        state = json.loads((self.plan / "frontier/state.json").read_text())
        self.assertEqual(state["claims"]["l21"]["ticket"], "#21")

    def test_claim_validates_owned_paths_against_active_lanes(self):
        self.write_lane(lane("hooks", ["CT-11"], "implementing", owned=["dev/hooks/"]))
        rc, out, _ = self.claim("l15", "CT-15", "implementer", "--owned-paths", "dev/hooks/git_gate.py,dev/x.py")
        self.assertEqual(rc, 2, out)
        self.assertIn("conflict", out)
        rc, out, _ = self.claim("l15", "CT-15", "implementer", "--owned-paths", "dev/plan_records.py")
        self.assertEqual(rc, 0, out)

    def test_release_then_reclaim(self):
        self.claim("l21", "#21")
        rc, out, _ = self.run_cli("release", "l21")
        self.assertEqual(rc, 0, out)
        rc, out, _ = self.run_cli("release", "l21")
        self.assertEqual(rc, 0, "release is idempotent: " + out)
        rc, out, _ = self.claim("l21b", "#21")
        self.assertEqual(rc, 0, out)

    def test_release_resume_over_ceiling_is_split_required(self):
        self.claim("l21", "#21")
        journal = self.tmp / "l21.jsonl"
        journal.write_text("\n".join(json.dumps(x) for x in (
            {"unit": "l21", "usage": {"input": 100, "output": 10, "total": 110}},
            {"unit": "l21", "usage": {"input": 540000, "output": 1000, "total": 541000}})) + "\n")
        rc, out, _ = self.run_cli("release", "l21", "--from-journal", str(journal), "--resume")
        self.assertEqual(rc, 2, out)
        self.assertIn("split-required", out)
        state = json.loads((self.plan / "frontier/state.json").read_text())
        self.assertEqual(state["claims"]["l21"]["status"], "split-required")
        rc, out, _ = self.run_cli("release", "l21", "--from-journal", str(journal))
        self.assertEqual(rc, 0, out)
        self.assertIn("split-required", out)
        state = json.loads((self.plan / "frontier/state.json").read_text())
        self.assertNotIn("l21", state["claims"])
        self.assertEqual(state["continuations"]["l21"]["status"], "split-required")
        plan = self.plan_json()
        self.assertNotIn("#21", plan["ready_order"], "a ticket with a pending continuation is held")
        self.assertIn("l21", plan["continuations"])
        rc, out, _ = self.claim("l21-2", "#21")
        self.assertEqual(rc, 0, out)
        state = json.loads((self.plan / "frontier/state.json").read_text())
        self.assertEqual(state["continuations"], {})


class StatusAndDegradedTests(FrontierCase):
    def test_status_names_missing_blockers_without_crashing(self):
        rc, out, err = self.run_cli("status")
        self.assertEqual(rc, 0, out + err)
        for ticket, artifact in (("CT-05", "ticket-ledger.json"), ("CT-15", "plan_records.py"),
                                 ("CT-17", "lane.py allocate"), ("CT-19", "lane_brief.py"),
                                 ("CT-22", "budget.py"), ("CT-24", "decisions.jsonl")):
            self.assertIn(f"not available yet: {ticket}", out)
            self.assertIn(artifact, out)
        rc, out, err = self.run_cli("status", "--json")
        self.assertEqual(rc, 0, out + err)
        status = json.loads(out)
        self.assertEqual(status["executor"], "native")
        self.assertEqual(status["capacity"]["max_parallel"], 3)
        self.assertEqual(status["degraded"]["CT-05"]["available"], False)

    def test_answer_is_recorded_without_granting_admission(self):
        rc, out, _ = self.run_cli("answer", "--question", "admission: run the heavy portion of #21 now?", "--answer", "no")
        self.assertEqual(rc, 0, out)
        self.assertIn("not an admission", out)
        rows = (self.plan / "frontier/answers.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(rows[0])["answer"], "no")
        self.assertFalse(self.plan_json()["cxx_slot"]["admitted"])

    def test_plan_without_ledger_or_graph_refuses_with_pointer(self):
        rc, out, err = self.run_cli("plan")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("not available yet: CT-05", out)
        self.assertIn("--graph", out)

    def test_plan_prefers_ticket_ledger_json_when_present(self):
        shutil.copy(self.plan / "graph.json", self.plan / "ticket-ledger.json")
        rc, out, err = self.run_cli("plan", "--json")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(json.loads(out)["graph_source"], "ticket-ledger.json")


class ExecutorGateTests(FrontierCase):
    def write_config(self, **items):
        path = self.plan / "frontier/executor-gate.config.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(items))
        return path

    def test_native_is_always_allowed(self):
        rc, out, err = self.run_cli("executor-gate")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("native", out)

    def test_non_native_without_probes_fails_naming_every_item(self):
        rc, out, err = self.run_cli("executor-gate", "--executor", "claude-agent")
        self.assertEqual(rc, 2, out + err)
        for item in ("G1", "G2", "G3", "G4", "G5", "G6"):
            self.assertIn(f"{item}: FAIL", out)
        self.assertIn("G7: SKIP", out, "G7 applies to team mode only")
        self.assertIn("run native", out)

    def test_probe_results_decide_and_write_receipt(self):
        cfg = self.write_config(G1={"rc": 0}, G2={"rc": 0}, G3={"rc": 1, "note": "schemas:check failed"},
                                G4={"path": str(self.repo / "missing")}, G5={"cmd": [sys.executable, "-c", "raise SystemExit(0)"]},
                                G6={"cmd": [sys.executable, "-c", "raise SystemExit(3)"]}, G7={"value": "native_qualified"})
        rc, out, err = self.run_cli("executor-gate", "--executor", "codex-agent", "--team", "--config", str(cfg), "--write")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("G3: FAIL", out)
        self.assertIn("G4: FAIL", out)
        self.assertIn("G6: FAIL", out)
        self.assertIn("G7: PASS", out)
        receipt = json.loads((self.plan / "frontier/executor-gate.json").read_text())
        self.assertEqual(receipt["executor"], "codex-agent")
        self.assertEqual(sorted(receipt["failed"]), ["G3", "G4", "G6"])
        cfg = self.write_config(**{g: {"rc": 0} for g in ("G1", "G2", "G3", "G4", "G5", "G6")})
        rc, out, err = self.run_cli("executor-gate", "--executor", "claude-agent", "--config", str(cfg))
        self.assertEqual(rc, 0, out + err)


class LedgerTests(FrontierCase):
    ROW: ClassVar[dict] = {"ticket": "CT-11", "unit": "hooks", "category": "automated checks", "finding_id": "F1",
           "kind": "mechanical", "destination": "dev/check.py", "mode": "auto",
           "verification": {"cmd": "./dev/mise run check", "rc": 0}, "retro_row": "retros/hooks.md#F1",
           "applied_by": "retro-writer"}

    def test_append_validates_shape_and_lists_by_destination(self):
        rc, out, _ = self.run_cli("ledger", "append", "--row", json.dumps(self.ROW))
        self.assertEqual(rc, 0, out)
        bad = dict(self.ROW, kind="vibes")
        rc, out, _ = self.run_cli("ledger", "append", "--row", json.dumps(bad))
        self.assertEqual(rc, 2, out)
        self.assertIn("kind", out)
        rc, out, _ = self.run_cli("ledger", "append", "--row", json.dumps({"ticket": "x"}))
        self.assertEqual(rc, 2, out)
        self.assertIn("missing", out)
        lines = (self.plan / "frontier/learning-ledger.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("ts", json.loads(lines[0]))
        rc, out, _ = self.run_cli("ledger", "list", "--by", "destination")
        self.assertEqual(rc, 0, out)
        self.assertIn("dev/check.py: 1", out)

    def test_repeat_destination_is_flagged(self):
        for finding in ("F1", "F2"):
            self.run_cli("ledger", "append", "--row", json.dumps(dict(self.ROW, finding_id=finding)))
        rc, out, _ = self.run_cli("ledger", "list", "--by", "destination")
        self.assertEqual(rc, 0, out)
        self.assertIn("repeat", out)


class MirrorTests(unittest.TestCase):
    def test_skill_mirror_is_byte_identical(self):
        self.assertTrue(MIRROR.is_dir(), "mirror under .agents/skills/ticket-frontier")
        diff = filecmp.dircmp(SKILL, MIRROR)
        problems = []

        def walk(cmp):
            problems.extend(cmp.left_only + cmp.right_only + cmp.diff_files + cmp.funny_files)
            for sub in cmp.subdirs.values():
                walk(sub)

        walk(diff)
        self.assertEqual(problems, [])

    def test_skill_md_is_bounded_and_model_invocable(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: ticket-frontier\n"))
        self.assertNotIn("disable-model-invocation: true", text)
        self.assertLessEqual(len(text.splitlines()), 130)


if __name__ == "__main__":
    unittest.main()
