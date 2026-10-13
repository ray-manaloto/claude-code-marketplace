"""A06 public blob-boundary controls; no live credentials or network."""

import base64
import contextlib
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import httpx
from githubkit.exception import RequestError, RequestFailed, RequestTimeout

sys.path.insert(0, str(Path(__file__).resolve().parent))

from codex_examples import BlobError, collect_blobs, decode_blob
import codex_examples
from search_catalog import ROOT, digest, encoded


class BlobTests(unittest.TestCase):
    def test_full_blob_matches_independent_git_identity(self):
        blob = SimpleNamespace(
            sha="f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f",
            size=3,
            encoding="base64",
            content=base64.b64encode(b"abc").decode(),
        )
        self.assertEqual(decode_blob(blob, blob.sha, max_bytes=3), b"abc")

    def test_mismatched_and_oversize_blobs_refuse(self):
        blob = SimpleNamespace(
            sha="f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f",
            size=3,
            encoding="base64",
            content=base64.b64encode(b"abd").decode(),
        )
        with self.assertRaises(BlobError):
            decode_blob(blob, blob.sha, max_bytes=3)
        blob.content = base64.b64encode(b"abc").decode()
        with self.assertRaises(BlobError):
            decode_blob(blob, blob.sha, max_bytes=2)

    def test_duplicate_paths_keep_provenance_but_fetch_once(self):
        sha = "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f"
        blob = SimpleNamespace(sha=sha, size=3, encoding="base64", content="YWJj")
        items = [{"repository": "openai/codex", "path": path, "sha": sha}
                 for path in ("a/config.toml", "b/config.toml")]
        calls = []

        def fetch(repo, requested):
            calls.append((repo, requested))
            return blob

        metadata = {"openai/codex": {"fork": False, "parent": None, "source": None,
                                     "private": False}}
        rows, contents = collect_blobs(items, [sha], fetch, metadata,
                                       max_items=2, max_bytes=3)
        self.assertEqual(calls, [("openai/codex", sha)])
        self.assertEqual(contents, {sha: b"abc"})
        self.assertEqual([row["path"] for row in rows],
                         ["a/config.toml", "b/config.toml"])
        self.assertEqual(rows[1]["duplicate_of"], "a/config.toml")
        self.assertEqual(rows[0]["fork"], False)

    def test_unselected_sha_refuses_before_fetch(self):
        with self.assertRaises(BlobError):
            collect_blobs([], ["f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f"],
                          lambda *_: self.fail("fetch called"), {},
                          max_items=1, max_bytes=3)


class RetrievalCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix=".a06-cli-", dir=ROOT)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.run_id = "examples--1791838915397532000--b666ae4cd38ff2a3"
        self.sha = "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f"
        self.entry = self.root / "evidence/saved-searches/runs" / self.run_id
        self.entry.mkdir(parents=True)
        raw = encoded({"fixture": "synthetic-offline"})
        normalized = encoded({"normalized": {"status": "complete", "items": [
            {"repository": "openai/codex", "path": "config.toml", "sha": self.sha}]}})
        (self.entry / "raw.json").write_bytes(raw)
        (self.entry / "normalized.json").write_bytes(normalized)
        manifest = {"version": 1, "run_id": self.run_id, "id": "examples",
                    "catalog_sha256": "a" * 64, "fingerprint": digest(encoded({})),
                    "criteria": {}, "observed_at_ns": 1791838915397532000,
                    "result_status": "complete", "raw_sha256": digest(raw),
                    "normalized_sha256": digest(normalized), "source_fixture_sha256": None}
        (self.entry / "manifest.json").write_bytes(encoded(manifest))
        self.schema = self.root / "schema.json"
        self.schema.write_bytes(encoded({"title": "SyntheticConfigToml"}))
        self.schema_hash = digest(self.schema.read_bytes())

    def invoke(self):
        stdout, stderr = StringIO(), StringIO()
        with patch.object(sys, "argv", ["examples", self.run_id, "--sha", self.sha]), \
             patch.object(codex_examples, "ROOT", self.root), \
             patch.object(codex_examples, "SCHEMA", self.schema), \
             patch.object(codex_examples, "SCHEMA_SHA256", self.schema_hash), \
             patch.object(codex_examples.subprocess, "run", return_value=SimpleNamespace(
                 returncode=0, stdout="codex-cli 0.162.1\n")), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = codex_examples.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_symlinked_selected_manifest_and_schema_refuse_before_credentials(self):
        for selected in (self.entry / "manifest.json", self.schema):
            with self.subTest(selected=selected.name):
                target = self.root / (selected.name + ".target")
                target.write_bytes(selected.read_bytes())
                selected.unlink()
                selected.symlink_to(target)
                try:
                    with patch.object(codex_examples, "credential",
                                      side_effect=AssertionError("credential lookup")), \
                         patch.object(codex_examples, "GitHub",
                                      side_effect=AssertionError("client construction")):
                        code, stdout, stderr = self.invoke()
                    self.assertEqual(code, 2)
                    self.assertEqual(stdout, "")
                    self.assertEqual(json.loads(stderr), {
                        "status": "unresolved", "reason": "symlinked project path refused"})
                    self.assertFalse((self.root / "evidence/codex-examples").exists())
                finally:
                    selected.unlink()
                    selected.write_bytes(target.read_bytes())

    def client(self):
        client = Mock()
        api = client.rest.return_value
        api.repos.get.return_value.parsed_data = SimpleNamespace(
            full_name="openai/codex", private=False, fork=False)
        api.git.get_blob.return_value = SimpleNamespace(status_code=200, parsed_data=
            SimpleNamespace(sha=self.sha, size=3, encoding="base64", content="YWJj"))
        return client, api

    def test_cli_records_full_verified_fixture_blob(self):
        client, api = self.client()
        with patch.object(codex_examples, "credential", return_value=("synthetic", "fixture")), \
             patch.object(codex_examples, "GitHub", return_value=client):
            code, stdout, stderr = self.invoke()
        self.assertEqual((code, stderr), (0, ""))
        result = json.loads(stdout)
        self.assertEqual((result["status"], result["blobs"], result["example_coverage"]),
                         ("recorded", 1, "bounded"))
        receipt_path = Path(result["receipt"])
        self.assertEqual((receipt_path.parent / "blobs" / self.sha).read_bytes(), b"abc")
        receipt = json.loads(receipt_path.read_bytes())
        self.assertEqual(receipt["saved_manifest_sha256"],
                         digest((self.entry / "manifest.json").read_bytes()))
        api.git.get_blob.assert_called_once_with(owner="openai", repo="codex", file_sha=self.sha)

    def test_sdk_request_failures_are_safe_unresolved_at_both_calls(self):
        marker = "SYNTHETIC_PRIVATE_REQUEST_DETAIL"
        request = httpx.Request("GET", "https://example.invalid/" + marker,
                                headers={"Authorization": marker})
        errors = [RequestError(RuntimeError(marker)),
                  RequestTimeout(httpx.ReadTimeout(marker, request=request)),
                  RequestFailed(SimpleNamespace(raw_request=request,
                      raw_response=httpx.Response(503, request=request, text=marker)))]
        for stage in ("repository", "blob"):
            for error in errors:
                with self.subTest(stage=stage, error=type(error).__name__):
                    client, api = self.client()
                    boundary = api.repos.get if stage == "repository" else api.git.get_blob
                    boundary.side_effect = error
                    with patch.object(codex_examples, "credential",
                                      return_value=("synthetic", "fixture")), \
                         patch.object(codex_examples, "GitHub", return_value=client):
                        code, stdout, stderr = self.invoke()
                    self.assertEqual((code, stdout), (2, ""))
                    self.assertEqual(json.loads(stderr), {
                        "status": "unresolved", "reason": "GitHub request failed"})
                    self.assertNotIn(marker, stderr)
                    self.assertNotIn("Traceback", stderr)
                    self.assertFalse((self.root / "evidence/codex-examples").exists())
                    if stage == "repository":
                        api.git.get_blob.assert_not_called()


if __name__ == "__main__":
    unittest.main()
