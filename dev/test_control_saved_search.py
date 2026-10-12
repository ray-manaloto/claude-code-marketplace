"""A03b same-budget control and completeness controls through the public task."""

import base64
import contextlib
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import httpx
from githubkit import GitHub

from collect_saved_search import collect, fixture_transport, main, wall_deadline
from control_saved_search import evaluate
from github_search_one_page import capture
from search_catalog import ROOT, catalog

LIVE = ROOT / "evidence/github-search-one-page/20261012T193651Z-cc501ef6/raw.json"


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(catalog(ROOT / "dev/saved-searches.toml")[0][0])
        self.template = json.loads(LIVE.read_bytes())

    def envelope(self, query, *, page=1, count=5, total=None, status=200,
                 private=False):
        if status == 200:
            body = json.loads(base64.b64decode(self.template["body_base64"]))
            body["items"] = body["items"][:count]
            body["total_count"] = count if total is None else total
            if private and body["items"]:
                body["items"][0]["repository"]["private"] = True
                body["items"][0]["path"] = "private-secret-path"
            content = json.dumps(body).encode()
        else:
            content = b'{"message":"service unavailable"}'
        return capture(httpx.Response(status, headers={"content-type": "application/json"},
                                      content=content), query, self.row["per_page"], page)

    def sequence(self, envelopes, *, clock_factory=None):
        payload = json.dumps({"format": "githubkit-http-sequence-v1",
                              "responses": envelopes}).encode()
        transport, consumed, decoded, exhausted = fixture_transport(payload, self.row)
        with GitHub("fixture", transport=transport, auto_retry=False, http_cache=False,
                    follow_redirects=False, trust_env=False) as client:
            deadline = time.monotonic() + self.row["timeout_seconds"]
            clock = clock_factory(deadline) if clock_factory else time.monotonic
            raw, meta = collect(client, "fixture", self.row, deadline=deadline,
                                pause=lambda _: None)
            raw, meta = evaluate(client, "fixture", self.row, raw, meta,
                                 deadline=deadline, wall_deadline=wall_deadline,
                                 clock=clock)
        self.assertEqual(len(consumed), len(decoded))
        self.assertFalse(exhausted)
        return raw, meta["normalized"]

    def test_empty_and_nonempty_candidates_require_positive_control(self):
        main_query = self.row["effective_query"]
        control_query = f"README repo:{self.row['repo']}"
        for count, expected in ((0, "empty_verified"), (5, "complete")):
            with self.subTest(count=count):
                raw, result = self.sequence([
                    self.envelope(main_query, count=count),
                    self.envelope(control_query)])
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["control_status"], "passed")
                self.assertTrue(result["complete_candidate"])
                self.assertEqual(result["requests_used"], 2)
                self.assertEqual(raw["controls"][0]["attempts"][0]["raw"]["request"]
                                 ["query"], control_query)

    def test_failed_and_not_run_control_never_promote_candidate(self):
        main_query = self.row["effective_query"]
        control_query = f"README repo:{self.row['repo']}"
        for status in (302, 503):
            with self.subTest(status=status):
                raw, result = self.sequence([
                    self.envelope(main_query, count=0),
                    self.envelope(control_query, status=status)])
                self.assertEqual(result["status"], "empty_unverified")
                self.assertEqual(result["control_status"], "failed")
                self.assertFalse(result["complete_candidate"])
                self.assertEqual(raw["controls"][0]["attempts"][0]["http_status"],
                                 status)
        raw, result = self.sequence([self.envelope(main_query, count=0)],
                                    clock_factory=lambda _: lambda: float("inf"))
        self.assertEqual(result["control_status"], "not_run")
        self.assertEqual(result["status"], "empty_unverified")
        self.assertEqual(raw["controls"][0]["attempts"], [])

    def test_deadline_after_control_response_preserves_raw_and_blocks_promotion(self):
        main_query = self.row["effective_query"]
        control_query = f"README repo:{self.row['repo']}"
        raw, result = self.sequence([
            self.envelope(main_query, count=0), self.envelope(control_query)],
            clock_factory=lambda deadline: iter((deadline - 1, deadline - 1,
                                                 deadline + 1)).__next__)
        self.assertEqual(result["status"], "empty_unverified")
        self.assertEqual(result["control_status"], "failed")
        self.assertEqual(raw["controls"][0]["reason"], "time_limit")
        self.assertEqual(raw["controls"][0]["attempts"][0]["raw"]["request"]["query"],
                         control_query)

    def test_incomplete_main_skips_control_and_private_control_is_withheld(self):
        main_query = self.row["effective_query"]
        control_query = f"README repo:{self.row['repo']}"
        raw, result = self.sequence([self.envelope(main_query, count=5, total=20),
                                     self.envelope(main_query, page=2, count=5, total=20)])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["control_status"], "not_run")
        self.assertEqual(raw["controls"], [])
        raw, result = self.sequence([self.envelope(main_query, count=0),
                                     self.envelope(control_query, private=True)])
        self.assertEqual(result["status"], "empty_unverified")
        self.assertEqual(result["control_status"], "failed")
        self.assertNotIn("private-secret-path", json.dumps(raw))

    def test_second_control_respects_total_request_budget(self):
        self.row["max_pages"] = 1
        self.row["control"] = [{"query": "README", "expected_min": 1},
                               {"query": "LICENSE", "expected_min": 1}]
        main_query = self.row["effective_query"]
        readme_query = f"README repo:{self.row['repo']}"
        raw, result = self.sequence([self.envelope(main_query, count=0),
                                     self.envelope(readme_query)])
        self.assertEqual(result["request_budget"], 2)
        self.assertEqual(result["requests_used"], 2)
        self.assertEqual([c["status"] for c in raw["controls"]], ["passed", "not_run"])
        self.assertEqual(result["status"], "empty_unverified")
        self.assertFalse(result["complete_candidate"])

    def test_public_offline_task_records_verified_empty_without_auth_or_network(self):
        with tempfile.TemporaryDirectory(prefix=".a03b-", dir=ROOT) as scratch:
            output = Path(scratch) / "records"
            fixture = Path(scratch) / "sequence.json"
            main_query = self.row["effective_query"]
            control_query = f"README repo:{self.row['repo']}"
            fixture.write_text(json.dumps({"format": "githubkit-http-sequence-v1",
                                           "responses": [self.envelope(main_query, count=0),
                                                         self.envelope(control_query)]}))
            argv = ["collect", "offline", "--id", self.row["id"], "--fixture",
                    str(fixture), "--output", str(output)]
            with patch.object(sys, "argv", argv):
                with patch("collect_saved_search.credential",
                           side_effect=AssertionError("credential lookup")):
                    with patch("httpx.HTTPTransport.handle_request",
                               side_effect=AssertionError("network")):
                        stdout = StringIO()
                        with contextlib.redirect_stdout(stdout):
                            self.assertEqual(main(), 0)
            target = Path(json.loads(stdout.getvalue())["receipt"])
            normalized = json.loads((target / "normalized.json").read_bytes())
            self.assertEqual(normalized["normalized"]["status"], "empty_verified")
            self.assertEqual(len(json.loads((target / "raw.json").read_bytes())
                                 ["controls"][0]["attempts"]), 1)
            fixture.write_text(json.dumps({"format": "githubkit-http-sequence-v1",
                                           "responses": [self.envelope(main_query, count=0)]}))
            empty_output = Path(scratch) / "missing-control"
            incomplete_argv = ["collect", "offline", "--id", self.row["id"],
                               "--fixture", str(fixture), "--output", str(empty_output)]
            with patch.object(sys, "argv", incomplete_argv):
                with patch("collect_saved_search.credential",
                           side_effect=AssertionError("credential lookup")):
                    with patch("httpx.HTTPTransport.handle_request",
                               side_effect=AssertionError("network")):
                        with contextlib.redirect_stderr(StringIO()):
                            self.assertEqual(main(), 2)
            self.assertFalse((empty_output / "runs").exists())


if __name__ == "__main__":
    unittest.main()
