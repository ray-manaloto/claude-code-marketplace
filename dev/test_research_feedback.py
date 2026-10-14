"""Deterministic regression controls; no network or external workflow state."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_feedback as feedback


class CoverageChecks(unittest.TestCase):
    def setUp(self):
        self.row = {"query_fingerprint": "a", "error_code": "NONE", "is_complete": True,
                    "item_count": 1, "total_count": 1,
                    "issues": [{"html_url": "https://github.com/o/r/issues/1"}]}
        self.empty = {**self.row, "issues": [], "item_count": 0, "total_count": 0}

    def test_zero_with_native_success_remains_unverified(self):
        prior = feedback.metrics({"q": self.row}, {})
        for _ in range(3):
            prior = feedback.metrics({"q": self.empty}, prior)
            row = prior["q"]
            self.assertTrue(row["native_complete"])
            self.assertTrue(row["empty_regression"])
            self.assertFalse(row["complete"])
            self.assertEqual(row["last_nonempty_items"], 1)
            self.assertEqual(row["capped_streak"], 0)
            self.assertEqual(row["unchanged_streak"], 0)

    def test_recovery_is_marked_once(self):
        prior = feedback.metrics({"q": self.row}, {})
        prior = feedback.metrics({"q": self.empty}, prior)
        recovered = feedback.metrics({"q": self.row}, prior)
        self.assertTrue(recovered["q"]["recovered_from_empty"])
        self.assertTrue(recovered["q"]["complete"])
        self.assertFalse(feedback.metrics({"q": self.row}, recovered)["q"]["recovered_from_empty"])

    def test_api_error_preserves_nonempty_history(self):
        prior = feedback.metrics({"q": self.row}, {})
        failed = feedback.metrics({"q": {**self.empty, "error_code": "API_ERROR"}}, prior)
        self.assertFalse(failed["q"]["complete"])
        self.assertEqual(failed["q"]["empty_streak"], 0)
        self.assertEqual(failed["q"]["last_nonempty_items"], 1)
        self.assertTrue(feedback.metrics({"q": self.empty}, failed)["q"]["empty_regression"])

    def test_fingerprint_change_starts_distinct_history(self):
        prior = feedback.metrics({"q": self.row}, {})
        changed = feedback.metrics({"q": {**self.empty, "query_fingerprint": "b"}}, prior)["q"]
        self.assertFalse(changed["empty_regression"])
        self.assertEqual(changed["last_nonempty_items"], 0)

    def test_first_empty_is_not_a_regression(self):
        self.assertFalse(feedback.metrics({"q": self.empty}, {})["q"]["empty_regression"])

    def test_unrelated_empty_blocks_candidate_promotion(self):
        prior = feedback.metrics({"discovery": self.row}, {})
        result = feedback.metrics({"candidate": self.row, "discovery": self.empty}, prior)
        self.assertEqual(feedback.promotion_blockers(result), ["discovery"])

    def test_error_blocks_promotion(self):
        rows = feedback.metrics({"q": {**self.empty, "error_code": "API_ERROR"}}, {})
        self.assertEqual(feedback.promotion_blockers(rows), ["q"])

    def test_caps_are_separate_from_empty_and_errors(self):
        result = feedback.metrics({"q": {**self.row, "is_complete": False}}, {})
        self.assertEqual(result["q"]["capped_streak"], 1)
        self.assertFalse(result["q"]["complete"])
        self.assertEqual(feedback.promotion_blockers(result), [])

    def test_code_identity_ignores_commit_churn(self):
        item = {"repo_name": "o/r", "path": "a.cpp", "html_url": "https://github.com/o/r/blob/aaa/a.cpp"}
        self.assertEqual(feedback.identity(item), feedback.identity({**item, "html_url": "changed"}))

    def test_malformed_observations_fail_closed(self):
        for change in ({"query_fingerprint": None}, {"is_complete": None},
                       {"error_code": None}, {"item_count": 0}, {"issues": [{}]}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                feedback.metrics({"q": {**self.row, **change}}, {})

    def test_cli_exit_and_input_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            current, prior = [Path(directory) / name for name in ("current.json", "prior.json")]
            current.write_text(json.dumps({"q": self.empty}))
            prior.write_text(json.dumps(feedback.metrics({"q": self.row}, {})))
            before = (current.read_bytes(), prior.read_bytes())
            with patch("sys.argv", ["replay", "--current", str(current), "--previous", str(prior)]), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(feedback.main(), 2)
            self.assertEqual(json.loads(output.getvalue())["promotion_blockers"], ["q"])
            self.assertEqual((current.read_bytes(), prior.read_bytes()), before)

    def test_cli_output_can_be_replayed_without_losing_history(self):
        with tempfile.TemporaryDirectory() as directory:
            current, prior = [Path(directory) / name for name in ("current.json", "prior.json")]
            prior.write_text("{}")
            for observation, expected in ((self.row, 0), (self.empty, 2), (self.empty, 2)):
                current.write_text(json.dumps({"q": observation}))
                with patch("sys.argv", ["replay", "--current", str(current), "--previous", str(prior)]), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(feedback.main(), expected)
                prior.write_text(output.getvalue())
            self.assertTrue(json.loads(prior.read_text())["queries"]["q"]["empty_regression"])


if __name__ == "__main__":
    unittest.main()
