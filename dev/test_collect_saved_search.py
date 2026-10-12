"""A03a offline public-task and bounded SDK attempt controls."""

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

from collect_saved_search import collect, fixture_transport, main
from github_search_one_page import capture
from search_catalog import ROOT, catalog

LIVE = ROOT / "evidence/github-search-one-page/20261012T193651Z-cc501ef6/raw.json"


class CollectTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(catalog(ROOT / "dev/saved-searches.toml")[0][0])
        self.row.update(max_pages=2, max_items=10)
        self.template = json.loads(LIVE.read_bytes())

    def envelope(self, page, *, status=200, total=10, duplicate=False,
                 remaining=None, count=None):
        if status == 200:
            body = json.loads(base64.b64decode(self.template["body_base64"]))
            body["total_count"] = total
            if count is not None:
                body["items"] = body["items"][:count]
            if page == 2 and not duplicate:
                for item in body["items"]:
                    item["sha"] = "b" * 40
            content = json.dumps(body).encode()
        else:
            content = b'{"message":"rate or service error"}'
        headers = {"content-type": "application/json"}
        if remaining is not None:
            headers["x-ratelimit-remaining"] = remaining
        return capture(httpx.Response(status, headers=headers, content=content),
                       self.row["effective_query"], self.row["per_page"], page)

    def run_sequence(self, envelopes):
        payload = json.dumps({"format": "githubkit-http-sequence-v1",
                              "responses": envelopes}).encode()
        transport, consumed, decoded, exhausted = fixture_transport(payload, self.row)
        with GitHub("fixture", transport=transport, auto_retry=False,
                    http_cache=False, follow_redirects=False, trust_env=False) as client:
            raw, meta = collect(client, "fixture", self.row, pause=lambda _: None)
        self.assertEqual(len(consumed), len(decoded))
        self.assertFalse(exhausted)
        return raw, meta["normalized"]

    def test_two_pages_keep_envelopes_and_candidate_is_not_full(self):
        raw, result = self.run_sequence([self.envelope(1), self.envelope(2)])
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["complete_candidate"])
        self.assertEqual((result["returned_count"], result["attempt_count"]), (10, 2))
        self.assertEqual([a["raw"]["request"]["page"] for a in raw["attempts"]], [1, 2])
        self.assertEqual(result["control_status"], "not_run")

    def test_retried_503_keeps_both_attempts(self):
        raw, result = self.run_sequence([self.envelope(1, status=503),
                                         self.envelope(1, total=5)])
        self.assertEqual([a["http_status"] for a in raw["attempts"]], [503, 200])
        self.assertEqual(result["reasons"], ["retried_transient_error"])
        self.assertEqual(result["status"], "partial")
        self.assertFalse(result["complete_candidate"])

    def test_rate_limit_and_duplicate_pages_remain_incomplete(self):
        for status, remaining, expected in ((403, "0", "primary_rate_limit"),
                                            (429, "12", "secondary_rate_limit"),
                                            (403, "12", "http_error")):
            with self.subTest(status=status, remaining=remaining):
                raw, result = self.run_sequence([
                    self.envelope(1, status=status, remaining=remaining)])
                self.assertEqual(len(raw["attempts"]), 1)
                self.assertEqual(result["status"], "error")
                self.assertIn(expected, result["reasons"])
        raw, result = self.run_sequence([self.envelope(1),
                                         self.envelope(2, duplicate=True)])
        self.assertIn("duplicate_items", result["reasons"])
        self.assertFalse(result["complete_candidate"])
        self.assertEqual(result["returned_count"], 5)

    def test_short_page_with_more_total_cannot_be_complete_candidate(self):
        _, result = self.run_sequence([self.envelope(1, total=10, count=2)])
        self.assertIn("unexpected_short_page", result["reasons"])
        self.assertFalse(result["complete_candidate"])
        self.assertEqual(result["returned_count"], 2)

    def test_http_200_normalization_error_retains_exact_envelope(self):
        envelope = self.envelope(1, total=1)
        raw, result = self.run_sequence([envelope])
        self.assertEqual(result["status"], "error")
        self.assertEqual(raw["attempts"][0]["raw"], envelope)
        self.assertEqual(raw["attempts"][0]["http_status"], 200)
        malformed = capture(httpx.Response(200, headers={"content-type": "application/json"},
                                           content=b"not-json"),
                            self.row["effective_query"], self.row["per_page"], 1)
        raw, result = self.run_sequence([malformed])
        self.assertEqual(result["status"], "error")
        self.assertEqual(raw["attempts"][0]["raw"], malformed)

    def test_private_repository_result_is_withheld_from_public_receipt(self):
        body = json.loads(base64.b64decode(self.template["body_base64"]))
        body["items"][0]["repository"]["private"] = True
        body["items"][0]["path"] = "private-secret-path"
        envelope = capture(httpx.Response(200, headers={"content-type": "application/json"},
                                          content=json.dumps(body).encode()),
                           self.row["effective_query"], self.row["per_page"], 1)
        raw, result = self.run_sequence([envelope])
        self.assertEqual(result["status"], "error")
        self.assertEqual(raw["attempts"][0]["raw"], {"status": "withheld_private_result"})
        self.assertEqual(raw["attempts"][0]["http_status"], 200)
        self.assertNotIn("private-secret-path", json.dumps(raw))

    def test_timeout_after_completed_response_keeps_envelope(self):
        envelope = self.envelope(1)
        with patch("github_search_one_page.normalize", side_effect=TimeoutError):
            raw, result = self.run_sequence([envelope])
        self.assertEqual(raw["attempts"][0]["raw"], envelope)
        self.assertEqual(raw["attempts"][0]["error_code"], "TIME_LIMIT")
        self.assertIn("time_limit", result["reasons"])

    def test_page_limit_and_total_drift_do_not_claim_complete(self):
        self.row["max_items"] = 20
        _, result = self.run_sequence([self.envelope(1, total=25),
                                       self.envelope(2, total=30)])
        self.assertIn("page_limit", result["reasons"])
        self.assertIn("total_drift", result["reasons"])

    def test_item_and_time_limits_and_redirect_are_explicit(self):
        self.row["max_items"] = 3
        _, result = self.run_sequence([self.envelope(1)])
        self.assertEqual(result["returned_count"], 3)
        self.assertIn("item_limit", result["reasons"])
        self.row["max_items"] = 10
        raw, result = self.run_sequence([self.envelope(1, status=302)])
        self.assertEqual(len(raw["attempts"]), 1)
        self.assertEqual(result["status"], "error")
        self.assertIn("http_error", result["reasons"])
        with GitHub("fixture", transport=httpx.MockTransport(lambda _: self.fail(
                "time-limited collection must not request")), auto_retry=False,
                    http_cache=False, follow_redirects=False, trust_env=False) as client:
            raw, result = collect(client, "fixture", self.row, clock=iter((0, 15)).__next__)
        self.assertEqual(raw["attempts"], [])
        self.assertIn("time_limit", result["normalized"]["reasons"])

    def test_each_sdk_request_uses_remaining_time_budget(self):
        self.row["max_pages"] = 1
        envelope = self.envelope(1, total=5)
        budget_seen = []

        def reply(request):
            budget_seen.append(request.extensions["timeout"]["connect"])
            return httpx.Response(200, headers=envelope["response_headers"],
                                  content=base64.b64decode(envelope["body_base64"]))

        with GitHub("fixture", transport=httpx.MockTransport(reply), auto_retry=False,
                    http_cache=False, follow_redirects=False, trust_env=False) as client:
            _, meta = collect(client, "fixture", self.row,
                              clock=iter((0, 5, 5)).__next__)
        self.assertEqual(budget_seen, [10])
        self.assertTrue(meta["normalized"]["complete_candidate"])

    def test_drip_feed_style_block_hits_wall_deadline(self):
        self.row["timeout_seconds"] = 0.02

        def slow(_request):
            time.sleep(0.1)
            return httpx.Response(200, json={"total_count": 0,
                                             "incomplete_results": False, "items": []})

        with GitHub("fixture", transport=httpx.MockTransport(slow), auto_retry=False,
                    http_cache=False, follow_redirects=False, trust_env=False) as client:
            raw, meta = collect(client, "fixture", self.row)
        self.assertEqual(len(raw["attempts"]), 1)
        self.assertEqual(raw["attempts"][0]["error_code"], "TIME_LIMIT")
        self.assertIn("time_limit", meta["normalized"]["reasons"])

    def test_public_offline_receipt_and_invalid_fixture_before_auth(self):
        with tempfile.TemporaryDirectory(prefix=".a03a-", dir=ROOT) as scratch:
            output = Path(scratch) / "records"
            fixture = Path(scratch) / "sequence.json"
            fixture.write_text(json.dumps({"format": "githubkit-http-sequence-v1",
                                           "responses": [self.envelope(1, total=20),
                                                         self.envelope(2, total=20)]}))
            argv = ["collect", "offline", "--id", "codex-schema", "--fixture",
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
            self.assertEqual(json.loads((target / "raw.json").read_bytes())["format"],
                             "githubkit-http-attempts-v2")
            self.assertEqual(len(json.loads((target / "raw.json").read_bytes())["attempts"]), 2)
            self.assertEqual(json.loads((target / "normalized.json").read_bytes())
                             ["normalized"]["status"], "partial")
            fixture.write_text("{}")
            with patch.object(sys, "argv", argv):
                with patch("collect_saved_search.credential",
                           side_effect=AssertionError("credential lookup")):
                    with contextlib.redirect_stderr(StringIO()):
                        self.assertEqual(main(), 2)


if __name__ == "__main__":
    unittest.main()
