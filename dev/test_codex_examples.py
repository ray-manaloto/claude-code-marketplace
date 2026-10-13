"""A06 public blob-boundary controls; no live credentials or network."""

import base64
import contextlib
import hashlib
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


class OfflineCliTests(unittest.TestCase):
    def setUp(self):
        RetrievalCliTests.setUp(self)
        self.receipt = self.root / "evidence/codex-examples/runs" / (self.run_id + "--" + "1" * 16) / "receipt.json"
        self.receipt.parent.mkdir(parents=True)
        blob_dir = self.receipt.parent / "blobs"
        blob_dir.mkdir()
        (blob_dir / self.sha).write_bytes(b"abc")
        self.row = {"repository": "openai/codex", "path": "config.toml", "blob_sha": self.sha,
                    "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
                    "size": 3, "fork": False, "parent": None, "source": None, "duplicate_of": None}
        self.document = {"version": 1, "saved_run_id": self.run_id,
            "saved_manifest_sha256": hashlib.sha256((self.entry / "manifest.json").read_bytes()).hexdigest(),
            "saved_normalized_sha256": hashlib.sha256((self.entry / "normalized.json").read_bytes()).hexdigest(),
            "search_status": "complete", "example_coverage": "bounded", "sdk": "githubkit",
            "sdk_api_version": "2026-03-10", "credential_route": "gh_cli",
            "release_tag": "rust-v0.162.1", "release_commit": "092d3acd6bec3e3a14bdc7e7a2810ab628ab759d",
            "schema_asset": "config-schema.json", "schema_sha256": self.schema_hash,
            "installed_cli": "codex-cli 0.162.1", "max_selected": 3, "max_blob_bytes": 262144,
            "blobs": [self.row]}
        document = json.loads((self.entry / "normalized.json").read_bytes())
        document["normalized"].update(returned_count=1, request_budget=2, requests_used=1,
            complete_candidate=True, collection_complete_candidate=True, reasons=[],
            control_status="passed", total_counts=[1], attempt_count=1, pages_succeeded=1)
        self.pin = self.rebind_run(document)

    def save_receipt(self):
        data = json.dumps(self.document, sort_keys=True).encode()
        self.receipt.write_bytes(data)
        return hashlib.sha256(data).hexdigest()

    def rebind_run(self, document):
        (self.entry / "normalized.json").write_text(json.dumps(document))
        manifest = json.loads((self.entry / "manifest.json").read_bytes())
        manifest.update(result_status=document["normalized"]["status"], normalized_sha256=hashlib.sha256(
            (self.entry / "normalized.json").read_bytes()).hexdigest())
        (self.entry / "manifest.json").write_text(json.dumps(manifest))
        self.document.update(saved_manifest_sha256=hashlib.sha256((self.entry / "manifest.json").read_bytes()).hexdigest(),
                             saved_normalized_sha256=manifest["normalized_sha256"])
        return self.save_receipt()

    def refused(self, **args):
        before = set(self.root.glob("evidence/codex-examples/classifications/**/receipt.json"))
        code, stdout, stderr = self.invoke(**args)
        self.assertEqual((code, stdout), (2, ""))
        self.assertEqual(json.loads(stderr)["status"], "unresolved")
        self.assertEqual(before, set(self.root.glob("evidence/codex-examples/classifications/**/receipt.json")))

    def test_malformed_receipt_pins_bytes_metadata_and_selection_refuse(self):
        for pin in ("0" * 64, "bad-pin"):
            with self.subTest(pin=pin):
                self.refused(pin=pin)
        mutations = [("version", True), ("saved_run_id", "other"), ("saved_manifest_sha256", "0" * 64),
            ("saved_normalized_sha256", "0" * 64), ("search_status", "partial"),
            ("example_coverage", "complete"), ("sdk", "other"), ("release_tag", "other"),
            ("release_commit", "0" * 40), ("installed_cli", "other"),
            ("schema_sha256", "0" * 64), ("max_selected", 4), ("max_blob_bytes", True),
            ("blobs", []), ("credential_route", []), ("blobs", [None])]
        row_mutations = [("path", "../config.toml"), ("repository", "other/repo"),
            ("blob_sha", "0" * 40), ("sha256", "0" * 64), ("size", True),
            ("size", 262145), ("fork", "false"), ("parent", "other/repo"), ("duplicate_of", "other")]
        for target, changes in ((self.document, mutations), (self.row, row_mutations)):
            for key, value in changes:
                with self.subTest(key=key, value=value):
                    old = target[key]
                    target[key] = value
                    try:
                        self.refused(pin=self.save_receipt())
                    finally:
                        target[key] = old
        self.pin = self.save_receipt()
        for path in (self.receipt, self.entry / "manifest.json", self.entry / "raw.json",
                     self.entry / "normalized.json", self.schema, self.receipt.parent / "blobs" / self.sha):
            with self.subTest(artifact=path.name):
                old = path.read_bytes()
                path.write_bytes(old + b" ")
                try:
                    self.refused()
                finally:
                    path.write_bytes(old)

    def invoke(self, receipt=None, pin=None, shas=None):
        stdout, stderr = StringIO(), StringIO()
        argv = ["examples", self.run_id, "--offline-receipt",
                str(self.receipt.relative_to(self.root)) if receipt is None else receipt,
                "--receipt-sha256", self.pin if pin is None else pin]
        for sha in ([self.sha] if shas is None else shas):
            argv.extend(["--sha", sha])
        with patch.object(sys, "argv", argv), patch.object(codex_examples, "ROOT", self.root), \
             patch.object(codex_examples, "SCHEMA", self.schema), \
             patch.object(codex_examples, "SCHEMA_SHA256", self.schema_hash), \
             patch.object(codex_examples, "credential", side_effect=AssertionError("credential access")), \
             patch.object(codex_examples, "GitHub", side_effect=AssertionError("client/fetch access")), \
             patch.object(codex_examples.subprocess, "run", side_effect=AssertionError("native command")), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = codex_examples.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def test_selected_offline_receipt_is_bound_append_only_and_unverified(self):
        inputs = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        outputs = []
        for _ in range(2):
            code, stdout, stderr = self.invoke()
            self.assertEqual((code, stderr), (0, ""))
            result = json.loads(stdout)
            output = Path(result.pop("receipt"))
            self.assertEqual(result, {"status": "recorded", "blobs": 1,
                                     "source_paths": 1, "example_coverage": "bounded"})
            record = json.loads(output.read_bytes())
            self.assertEqual(record["retrieval_receipt_sha256"], self.pin)
            self.assertEqual(record["inspections"], [{**self.row, "validity": "UNVERIFIED",
                "method": None, "inspection": "not_inspected",
                "reason": "TOML syntax, release-schema, native and runtime validation not executed"}])
            outputs.append(output)
        self.assertNotEqual(*outputs)
        self.assertEqual(inputs, {p: p.read_bytes() for p in inputs})

    def test_partial_duplicate_paths_keep_provisional_coverage_and_recorded_route(self):
        document = json.loads((self.entry / "normalized.json").read_bytes())
        document["normalized"]["status"] = "partial"
        document["normalized"].update(returned_count=2, total_counts=[898], complete_candidate=False, control_status="not_run")
        document["normalized"]["items"].append({"repository": "openai/codex", "path": "docs.md", "sha": self.sha})
        self.document.update(search_status="partial", example_coverage="provisional", credential_route="GH_TOKEN")
        self.document["blobs"].append({**self.row, "path": "docs.md", "duplicate_of": "config.toml"})
        code, stdout, stderr = self.invoke(pin=self.rebind_run(document))
        self.assertEqual((code, stderr), (0, ""))
        result = json.loads(stdout)
        self.assertEqual((result["blobs"], result["source_paths"], result["example_coverage"]), (1, 2, "provisional"))
        self.document["blobs"].pop()
        self.refused(pin=self.save_receipt())

    def test_selected_input_and_output_symlinks_and_escape_refuse(self):
        for path in (self.receipt, self.entry / "manifest.json", self.entry / "raw.json",
                     self.entry / "normalized.json", self.schema, self.receipt.parent / "blobs" / self.sha):
            with self.subTest(symlink=path.name):
                target = self.root / (path.name + ".target")
                target.write_bytes(path.read_bytes())
                path.unlink()
                path.symlink_to(target)
                try:
                    self.refused()
                finally:
                    path.unlink()
                    path.write_bytes(target.read_bytes())
        self.refused(receipt="../outside/receipt.json")
        self.refused(receipt=str(self.receipt))
        output = self.root / "evidence/codex-examples/classifications"
        output.symlink_to(self.root)
        self.refused()

    def test_independently_rebound_normalized_budget_and_status_still_refuse(self):
        document = json.loads((self.entry / "normalized.json").read_bytes())
        for key, value in (("returned_count", 0), ("request_budget", 0), ("requests_used", 99),
                           ("complete_candidate", False), ("items", []), ("status", "failed")):
            with self.subTest(key=key):
                modified = json.loads(json.dumps(document))
                modified["normalized"][key] = value
                self.refused(pin=self.rebind_run(modified))

    def test_empty_offline_arguments_and_invalid_selected_sha_never_enter_retrieval(self):
        self.refused(receipt="", pin="")
        for shas in ([self.sha, self.sha], ["0" * 40], ["bad-sha"]):
            self.refused(shas=shas)

    def test_manifest_observation_can_follow_independent_run_timestamp(self):
        manifest = json.loads((self.entry / "manifest.json").read_bytes())
        manifest["observed_at_ns"] = 1791838915398644000
        (self.entry / "manifest.json").write_text(json.dumps(manifest))
        document = json.loads((self.entry / "normalized.json").read_bytes())
        code, stdout, stderr = self.invoke(pin=self.rebind_run(document))
        self.assertEqual((code, stderr), (0, ""))
        self.assertEqual(json.loads(stdout)["example_coverage"], "bounded")

    def test_all_normalized_identities_validate_before_selection(self):
        document = json.loads((self.entry / "normalized.json").read_bytes())
        for item in ({}, {"repository": "openai/codex", "path": "docs.md", "sha": "bad-sha"},
                     {"repository": None, "path": "docs.md", "sha": "0" * 40},
                     {"repository": "openai/codex", "path": "../docs.md", "sha": "0" * 40},
                     document["normalized"]["items"][0]):
            with self.subTest(item=item):
                changed = json.loads(json.dumps(document))
                changed["normalized"]["items"].append(item)
                changed["normalized"]["returned_count"] = 2
                self.refused(pin=self.rebind_run(changed))

    def test_contradictory_collection_proof_cannot_produce_bounded_coverage(self):
        document = json.loads((self.entry / "normalized.json").read_bytes())
        for key, value in (("collection_complete_candidate", False), ("reasons", ["item_limit"]),
                           ("collection_complete_candidate", "true"), ("reasons", None)):
            with self.subTest(key=key, value=value):
                changed = json.loads(json.dumps(document))
                changed["normalized"][key] = value
                self.refused(pin=self.rebind_run(changed))

    def test_oversize_stored_blob_read_is_capped_at_budget_plus_one(self):
        blob = self.receipt.parent / "blobs" / self.sha
        blob.write_bytes(b"x" * 262145)
        original_open, reads = Path.open, []

        @contextlib.contextmanager
        def artifact_open(path, *args, **kwargs):
            with original_open(path, *args, **kwargs) as stream:
                if path == blob:
                    def read(size=-1):
                        self.assertEqual(size, 262145, "stored blob read exceeded public byte budget")
                        reads.append(size)
                        return stream.read(size)
                    yield SimpleNamespace(read=read)
                else:
                    yield stream

        with patch.object(Path, "open", artifact_open):
            self.refused()
        self.assertEqual(reads, [262145])


if __name__ == "__main__":
    unittest.main()
