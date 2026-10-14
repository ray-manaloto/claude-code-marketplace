"""Public-CLI and approved() controls for dev/plan_decide.py (stdlib only, scratch ledger)."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "dev" / "plan_decide.py"
sys.path.insert(0, str(CLI.parent))

import plan_decide  # noqa: E402


class PlanDecideCli(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.dir = Path(scratch.name)
        self.ledger = self.dir / "decisions.jsonl"

    def decide(self, *args):
        result = subprocess.run([sys.executable, "-I", str(CLI), *args, "--file", str(self.ledger)],
                                cwd=self.dir, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout.strip(), result.stderr

    def rows(self):
        return [json.loads(line) for line in self.ledger.read_text().splitlines()]

    def test_duplicate_approval_is_idempotent_and_append_only(self):  # C2 T-E5
        rc, first, _ = self.decide("approval", "--subject", "CT-02", "--source", "D3")
        self.assertEqual(rc, 0)
        before = self.ledger.read_bytes()
        rc, second, _ = self.decide("approval", "--subject", "CT-02", "--source", "D23")
        self.assertEqual(rc, 0)
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertIn("already approved", second)
        rc, _, _ = self.decide("approval", "--subject", "CT-02", "CT-03", "--source", "D23")
        self.assertEqual(rc, 0)
        self.assertTrue(self.ledger.read_bytes().startswith(before))
        self.assertEqual([(r["kind"], r["subject"]) for r in self.rows()],
                         [("approval", "CT-02"), ("approval", "CT-03")])
        self.assertTrue(all(r["id"].startswith("DL-") for r in self.rows()), first)

    def test_operation_then_receipt_closes_it(self):
        rc, out, _ = self.decide("operation", "--subject", "relabel #91", "--source", "D20")
        self.assertEqual(rc, 0)
        op = out.split()[0]
        self.assertEqual([r["id"] for r in plan_decide.pending(self.ledger)], [op])
        evidence = self.dir / "relabel.log"
        evidence.write_text("labels: ready-for-human\n")
        rc, out, _ = self.decide("receipt", op, "--path", str(evidence), "--rc", "0")
        self.assertEqual(rc, 0, out)
        self.assertEqual(plan_decide.pending(self.ledger), [])
        closing = self.rows()[-1]
        self.assertEqual((closing["kind"], closing["subject"]), ("receipt", op))
        self.assertEqual(closing["receipt"], {"path": "relabel.log", "rc": 0, "sha256":  # root-relative
                         "6454e3d9430308f594a66fa910e35610c43d4d63112ee02bd174f811aff2d3c1"})

    def test_approved_lists_only_approval_subjects(self):
        self.assertEqual(plan_decide.approved(self.ledger), set())
        self.decide("approval", "--subject", "CT-01", "--source", "D3")
        rc, out, _ = self.decide("operation", "--subject", "CT-05", "--source", "D23")
        self.assertEqual(rc, 0)
        evidence = self.dir / "done.log"
        evidence.write_text("ok\n")
        self.decide("receipt", out.split()[0], "--path", str(evidence))
        self.decide("operation", "--subject", "CT-06", "--source", "D23")
        rc, _, _ = self.decide("decision", "--subject", "D46", "--source", "parent 2026-10-14",
                               "--text", "wave 0 is exempt from the always-active C++ rule")
        self.assertEqual(rc, 0)
        self.assertEqual(plan_decide.approved(self.ledger), {"CT-01"})

    def test_refuses_unknown_kind_and_receipt_for_missing_id(self):
        self.assertEqual(self.decide("veto", "--subject", "CT-01", "--source", "D3")[0], 1)
        self.assertFalse(self.ledger.exists())
        self.decide("approval", "--subject", "CT-01", "--source", "D3")
        before = self.ledger.read_bytes()
        evidence = self.dir / "done.log"
        evidence.write_text("ok\n")
        rc, _, err = self.decide("receipt", "DL-9", "--path", str(evidence), "--rc", "0")
        self.assertEqual(rc, 2)
        self.assertIn("DL-9", err)
        self.assertEqual(self.decide("receipt", "DL-1", "--path", str(evidence))[0], 2)  # an approval
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_receipt_refuses_a_path_outside_the_ledger_root(self):  # review P3 plan_decide.py:70
        rc, out, _ = self.decide("operation", "--subject", "draft PR", "--source", "D20")
        self.assertEqual(rc, 0)
        before = self.ledger.read_bytes()
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        evidence = Path(outside.name) / "pr.log"
        evidence.write_text("ok\n")
        rc, _, err = self.decide("receipt", out.split()[0], "--path", str(evidence), "--rc", "0")
        self.assertEqual(rc, 2)
        self.assertIn("not a file under", err)
        self.assertEqual(self.ledger.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
