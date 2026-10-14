"""A05a compatible immutable baseline and pure comparison controls."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from search_catalog import (ROOT, CatalogError, catalog, digest, encoded,
                            inspect_runs, quarantine, record)
from search_compare import compare, eligible, select_baseline


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".a05a-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "records"
        self.row = catalog(ROOT / "dev/saved-searches.toml")[0][0]
        self.assertEqual(self.row["criteria"]["normalization_version"], 2)

    def observation(self, status, identities=(), *, control="passed"):
        return {"normalized": {
            "status": status,
            "items": [{"identity": identity} for identity in identities],
            "control_status": control,
            "complete_candidate": status in {"complete", "empty_verified"},
        }}

    def retain(self, status, identities=(), *, control="passed", row=None,
               catalog_hash="a" * 64):
        value = self.observation(status, identities, control=control)
        return record(self.output, row or self.row, catalog_hash,
                      {"format": "scratch-comparison-input"}, value, None)

    def preflight(self):
        return inspect_runs(self.output, self.row["id"], capture_published=True)

    def test_first_observation_establishes_baseline_without_deltas(self):
        prior, reason = select_baseline(self.output, self.row, self.preflight())
        self.assertIsNone(prior)
        result = compare(self.observation("complete", ("A",)), prior, reason)
        self.assertEqual(result["status"], "baseline_established")
        self.assertNotIn("new", result)
        self.assertNotIn("gone", result)

    def test_latest_compatible_complete_and_verified_empty_transitions(self):
        first = self.retain("complete", ("A", "B"))
        prior, reason = select_baseline(self.output, self.row, self.preflight())
        self.assertEqual(prior["run_id"], first.name)
        result = compare(self.observation("complete", ("B", "C")), prior, reason)
        self.assertEqual((result["new"], result["gone"]), (["C"], ["A"]))
        result = compare(self.observation("empty_verified"), prior, reason)
        self.assertEqual((result["new"], result["gone"]), ([], ["A", "B"]))
        self.retain("partial", ("X",))
        later, _ = select_baseline(self.output, self.row, self.preflight())
        self.assertEqual(later["run_id"], first.name)
        self.assertEqual(compare(self.observation("partial", ("X",)), later,
                                 "compatible_prior"),
                         {"status": "suppressed", "reason": "current_ineligible"})

    def test_fingerprint_controls_compatibility_but_catalog_hash_does_not(self):
        other = dict(self.row)
        other["criteria"] = {**self.row["criteria"], "max_items": 9}
        other["fingerprint"] = digest(encoded(other["criteria"]))
        self.retain("complete", ("wrong-limits",), row=other)
        self.assertIsNone(select_baseline(self.output, self.row, self.preflight())[0])
        compatible = self.retain("empty_verified", catalog_hash="b" * 64)
        prior, _ = select_baseline(self.output, self.row, self.preflight())
        self.assertEqual(prior["run_id"], compatible.name)
        self.assertFalse(eligible(self.observation("complete", ("A",),
                                                   control="failed")["normalized"]))

    def test_quarantine_reset_requires_new_observation(self):
        old = self.retain("complete", ("A",))
        quarantine(self.output, old.name, "scratch reset")
        snapshot = self.preflight()
        self.assertTrue(snapshot["baseline_reset"])
        prior, reason = select_baseline(self.output, self.row, snapshot)
        self.assertIsNone(prior)
        self.assertEqual(reason, "quarantine_reset")
        replacement = self.retain("empty_verified")
        prior, _ = select_baseline(self.output, self.row, self.preflight())
        self.assertEqual(prior["run_id"], replacement.name)

    def test_hash_drift_never_becomes_comparable(self):
        target = self.retain("complete", ("A",))
        snapshot = self.preflight()
        (target / "normalized.json").write_text("changed")
        with self.assertRaisesRegex(CatalogError, "corrupt selected"):
            inspect_runs(self.output, self.row["id"])
        with self.assertRaisesRegex(CatalogError, "changed during comparison"):
            select_baseline(self.output, self.row, snapshot)

    def test_post_preflight_corruption_cannot_fall_back_to_older_baseline(self):
        root = self.output
        for case in ("missing", "directory", "symlink", "fingerprint", "status"):
            with self.subTest(case=case):
                self.output = root / case
                self.retain("complete", ("older",))
                latest = self.retain("complete", ("newer",))
                snapshot = self.preflight()
                manifest = latest / "manifest.json"
                if case == "missing":
                    manifest.unlink()
                elif case == "directory":
                    manifest.unlink()
                    manifest.mkdir()
                elif case == "symlink":
                    manifest.rename(latest / "manifest.saved")
                    manifest.symlink_to("manifest.saved")
                else:
                    value = json.loads(manifest.read_bytes())
                    field = "fingerprint" if case == "fingerprint" else "result_status"
                    value[field] = "0" * 64 if case == "fingerprint" else "partial"
                    manifest.write_bytes(encoded(value))
                with self.assertRaisesRegex(CatalogError, "changed during comparison"):
                    select_baseline(self.output, self.row, snapshot)

    def test_comparison_parses_the_normalized_bytes_it_hashed(self):
        target = self.retain("complete", ("checked",))
        snapshot = self.preflight()
        normalized_path = target / "normalized.json"
        original = Path.read_bytes
        reads = 0

        def mutate_after_read(path):
            nonlocal reads
            result = original(path)
            if path == normalized_path:
                reads += 1
                if reads == 1:
                    normalized_path.write_bytes(encoded(
                        self.observation("complete", ("unchecked",))))
            return result

        with patch.object(Path, "read_bytes", mutate_after_read):
            prior, _ = select_baseline(self.output, self.row, snapshot)
        self.assertEqual(reads, 1)
        self.assertEqual(prior["identities"], ["checked"])


if __name__ == "__main__":
    unittest.main()
