"""A02 bounded SDK and normalization controls; no network or credentials."""

import contextlib
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
from githubkit import GitHub
from githubkit.utils import UNSET

from github_search_one_page import ROOT, capture, credential, main, normalize, replay_response, search


def item(language=UNSET):
    return SimpleNamespace(
        repository=SimpleNamespace(private=False, full_name="openai/codex"),
        path="src/config.rs", sha="a" * 40,
        html_url="https://github.com/openai/codex/blob/main/src/config.rs",
        language=language,
    )


class OnePageTests(unittest.TestCase):
    def test_typed_empty_fixture_one_request(self):
        fixture = Path(__file__).parent / "fixtures" / "github-code-search-empty.json"
        requests = []

        def reply(request):
            requests.append(request)
            status, headers, body = replay_response(fixture.read_bytes())
            return httpx.Response(status, headers=headers, content=body)

        with GitHub("fixture", transport=httpx.MockTransport(reply),
                    auto_retry=False, http_cache=False, follow_redirects=False,
                    trust_env=False) as client:
            raw, meta = search(client, "fixture")
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].url.path, "/search/code")
        self.assertEqual(requests[0].url.params["q"], "schema repo:openai/codex")
        self.assertEqual(meta["normalized"]["status"], "empty_unverified")
        self.assertEqual(raw["body_sha256"],
                         "3e14c51c1e62e3130eaeb10b2b0cbc946c902f6ff2e0587bfc67c256522530d5")

    def test_5xx_is_one_request_and_error(self):
        requests = []

        def reply(request):
            requests.append(request)
            return httpx.Response(503, content=b'{"message":"Unavailable"}')

        with GitHub("fixture", transport=httpx.MockTransport(reply),
                    auto_retry=False, http_cache=False, follow_redirects=False,
                    trust_env=False) as client:
            raw, meta = search(client, "fixture")
        self.assertEqual(len(requests), 1)
        self.assertEqual(raw["http_status"], 503)
        self.assertEqual(replay_response(json.dumps(raw).encode())[2],
                         b'{"message":"Unavailable"}')
        self.assertEqual(meta["normalized"]["status"], "error")

    def test_replay_digest_and_header_allowlist(self):
        envelope = capture(httpx.Response(200, headers={
            "content-type": "application/json", "authorization": "fixture-secret"},
            content=b"{}"))
        self.assertEqual(envelope["response_headers"], {"content-type": "application/json"})
        self.assertEqual(replay_response(json.dumps(envelope).encode())[2], b"{}")
        envelope["body_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            replay_response(json.dumps(envelope).encode())

    def test_redirect_is_not_followed(self):
        requests = []

        def reply(request):
            requests.append(request)
            return httpx.Response(302, headers={"location": "https://elsewhere.example/search"})

        with GitHub("fixture", transport=httpx.MockTransport(reply),
                    auto_retry=False, http_cache=False, follow_redirects=False,
                    trust_env=False) as client:
            _, meta = search(client, "fixture")
        self.assertEqual(len(requests), 1)
        self.assertEqual(meta["normalized"]["status"], "error")

    def test_identity_and_missing_null_value(self):
        for language, state in ((UNSET, "missing"), (None, "null"), ("Rust", "value")):
            with self.subTest(state=state):
                data = SimpleNamespace(items=[item(language)], total_count=2,
                                       incomplete_results=False)
                result = normalize(data)
                self.assertEqual(result["status"], "partial")
                self.assertEqual(result["items"][0]["identity"],
                                 "openai/codex:src/config.rs:" + "a" * 40)
                self.assertEqual(result["items"][0]["language"]["state"], state)

    def test_credential_route_is_presence_only(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "fixture-token", "GH_TOKEN": ""}):
            token, route = credential()
        self.assertEqual(token, "fixture-token")
        self.assertEqual(route, "GITHUB_TOKEN")
        with patch.dict(os.environ, {"GITHUB_TOKEN": "", "GH_TOKEN": "enterprise-token",
                                          "GH_HOST": "enterprise.example"}):
            with patch("github_search_one_page.shutil.which", return_value="/usr/bin/gh"):
                with patch("github_search_one_page.subprocess.run") as run:
                    run.return_value.returncode = 1
                    run.return_value.stdout = ""
                    self.assertEqual(credential(), (None, "absent"))
                    self.assertNotIn("GH_TOKEN", run.call_args.kwargs["env"])
                    self.assertNotIn("GH_HOST", run.call_args.kwargs["env"])

    def test_public_offline_503_receipt_never_authenticates_or_uses_network(self):
        fixture = ROOT / "dev/fixtures/github-code-search-503.json"
        with tempfile.TemporaryDirectory(prefix=".a02-", dir=ROOT) as scratch:
            with patch.object(sys, "argv", ["one-page", "offline", "--fixture",
                                            str(fixture), "--output", scratch]):
                with patch("github_search_one_page.credential",
                           side_effect=AssertionError("offline credential lookup")):
                    with patch("httpx.HTTPTransport.handle_request",
                               side_effect=AssertionError("offline network")):
                        output = StringIO()
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(main(), 2)
            target = Path(json.loads(output.getvalue())["receipt"])
            self.assertEqual(json.loads((target / "raw.json").read_text()),
                             json.loads(fixture.read_text()))
            metadata = json.loads((target / "normalized.json").read_text())
            self.assertEqual(metadata["http_status"], 503)
            self.assertEqual(metadata["normalized"]["error_code"], "HTTP_ERROR")


if __name__ == "__main__":
    unittest.main()
