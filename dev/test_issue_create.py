"""Offline A08a public-boundary controls; no credentials or GitHub requests."""

import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from githubkit import GitHub
import httpx

from issue_create import (Refusal, apply, attempt_path, binding_path, full_body,
                          intent_path, main, manifest, pages, preview, verify)


def row(number, database_id, body="old", labels=()):
    return {"id": database_id, "number": number, "title": "Existing", "body": body,
            "state": "open", "updated_at": "t1", "labels": [{"name": x} for x in labels]}


class FakeIssues:
    def __init__(self):
        self.parent = row(11, 101)
        self.repository = [self.parent]
        self.children = []
        self.posts = []
        self.failure = None
        self.attach = True
        self.visible = True
        self.parent_lookup = 404

    @staticmethod
    def response(data):
        return SimpleNamespace(status_code=200, raw_response=SimpleNamespace(json=lambda: data))

    def get(self, owner, repo, number):
        assert (owner, repo, number) == ("ray-manaloto", "claude-code-marketplace", self.parent["number"])
        return self.response(self.parent)

    def list_for_repo(self, owner, repo, *, state, per_page, page):
        assert state == "all" and per_page == 100
        rows = self.repository if self.visible else self.repository[:1]
        return self.response(rows[(page - 1) * 100:page * 100])

    def list_sub_issues(self, owner, repo, number, *, per_page, page):
        assert number == self.parent["number"] and per_page == 100
        return self.response(self.children[(page - 1) * 100:page * 100])

    def get_parent(self, owner, repo, number):
        assert (owner, repo, number) == ("ray-manaloto", "claude-code-marketplace", 62)
        if self.parent_lookup == "timeout":
            raise TimeoutError("parent lookup")
        response = self.response(self.parent)
        response.status_code = self.parent_lookup
        return response

    def create(self, owner, repo, *, data):
        assert (owner, repo) == ("ray-manaloto", "claude-code-marketplace")
        assert set(data) in ({"title", "body", "labels", "parent_issue_id"}, {"title", "body", "labels"})
        if "parent_issue_id" in data:
            assert data["parent_issue_id"] == self.parent["id"]  # database id, never issue number
        self.posts.append(data)
        if self.failure == "before":
            raise TimeoutError("before send")
        child = row(62, 1001, data["body"], data["labels"])
        child["title"] = data["title"]
        self.repository.append(child)
        if self.attach and "parent_issue_id" in data:
            self.children.append(child)
        if self.failure == "after":
            raise TimeoutError("after send")
        if self.failure == "503":
            raise RuntimeError("HTTP 503 after send")
        if self.failure == "death":
            raise KeyboardInterrupt
        return self.response(child)


class FakeClient:
    def __init__(self):
        self.issues = FakeIssues()

    def rest(self, version):
        assert version == "2026-03-10"
        return SimpleNamespace(issues=self.issues)


class CreationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        self.journal = base / "journal"
        self.journal.mkdir()
        self.manifest = base / "tickets.json"
        body = "Status: planned\n\nApproved body.\n"
        self.ticket = {"local_id": "A01", "title": "A01 — Bootstrap", "body": body,
                       "body_sha256": hashlib.sha256(body.encode()).hexdigest(), "labels": []}
        payload = {"version": 1, "repo": "ray-manaloto/claude-code-marketplace",
                   "parent_number": 11, "tickets": [self.ticket]}
        self.manifest.write_text(json.dumps(payload) + "\n")
        self.client = FakeClient()
        self.digest = preview(self.client, self.manifest, "A01", self.journal)
        self.path = intent_path(self.journal, "A01")

    def generic_manifest(self, parent=77, local_id="T1"):
        self.ticket = dict(self.ticket, local_id=local_id)
        self.client.issues.parent.update(number=77, id=707)
        payload = {"version": 2, "repo": "ray-manaloto/claude-code-marketplace",
                   "parent_number": parent, "tickets": [self.ticket]}
        self.manifest.write_text(json.dumps(payload) + "\n")

    def test_approved_generic_ticket_under_chosen_existing_parent(self):
        self.generic_manifest()
        digest = preview(self.client, self.manifest, "T1", self.journal)
        path = intent_path(self.journal, "T1")
        self.assertEqual(apply(self.client, path, digest, self.manifest), "VERIFIED")
        self.assertEqual(self.client.issues.posts[0]["parent_issue_id"], 707)
        binding = json.loads(binding_path(path).read_text())
        self.assertEqual((binding["local_id"], binding["parent_number"]), ("T1", 77))

    def test_standalone_spec_has_no_parent_and_uncertain_send_is_verify_only(self):
        self.generic_manifest(parent=None, local_id="remaining-spec")
        digest = preview(self.client, self.manifest, "remaining-spec", self.journal)
        path = intent_path(self.journal, "remaining-spec")
        self.client.issues.failure = "after"
        self.assertEqual(apply(self.client, path, digest, self.manifest), "UNRESOLVED")
        self.assertEqual(verify(self.client, path, digest, self.manifest), "VERIFIED")
        self.assertNotIn("parent_issue_id", self.client.issues.posts[0])
        self.assertIsNone(json.loads(binding_path(path).read_text())["parent_number"])
        with self.assertRaisesRegex(Refusal, "verify only"):
            apply(self.client, path, digest, self.manifest)
        self.assertEqual(len(self.client.issues.posts), 1)

    def test_standalone_verification_rejects_attached_or_unverified_parent(self):
        self.generic_manifest(parent=None, local_id="spec")
        digest = preview(self.client, self.manifest, "spec", self.journal)
        path = intent_path(self.journal, "spec")
        self.client.issues.parent_lookup = 200
        self.assertEqual(apply(self.client, path, digest, self.manifest), "UNRESOLVED")
        self.assertFalse(binding_path(path).exists())
        for status in (200, 410, 500, "timeout"):
            with self.subTest(status=status):
                self.client.issues.parent_lookup = status
                self.assertEqual(verify(self.client, path, digest, self.manifest), "UNRESOLVED")
        self.client.issues.parent_lookup = 404
        self.assertEqual(verify(self.client, path, digest, self.manifest), "VERIFIED")
        self.assertEqual(len(self.client.issues.posts), 1)

    def test_standalone_parent_absence_through_installed_sdk_http_boundary(self):
        for parent_status, expected in ((404, "VERIFIED"), (410, "UNRESOLVED"), (500, "UNRESOLVED")):
            with self.subTest(parent_status=parent_status):
                self.setUp()
                self.generic_manifest(parent=None, local_id="spec")
                remote = self.client.issues
                def respond(request):
                    prefix = "/repos/ray-manaloto/claude-code-marketplace/issues"
                    if request.method == "GET" and request.url.path == prefix:
                        return httpx.Response(200, json=remote.repository)
                    if request.method == "POST" and request.url.path == prefix:
                        response = remote.create("ray-manaloto", "claude-code-marketplace",
                                                 data=json.loads(request.content))
                        return httpx.Response(201, json=response.raw_response.json())
                    if request.method == "GET" and request.url.path == prefix + "/62/parent":
                        return httpx.Response(parent_status, json={"message": "parent lookup"})
                    raise AssertionError(f"unexpected offline request: {request.method} {request.url.path}")
                with GitHub("offline-test-token", transport=httpx.MockTransport(respond),
                            auto_retry=False, http_cache=False, trust_env=False) as client:
                    digest = preview(client, self.manifest, "spec", self.journal)
                    path = intent_path(self.journal, "spec")
                    self.assertEqual(apply(client, path, digest, self.manifest), expected)
                    self.assertEqual(verify(client, path, digest, self.manifest), expected)
                self.assertEqual(len(remote.posts), 1)

    def test_generic_publication_refuses_manifest_drift_before_send(self):
        self.generic_manifest()
        original = self.manifest.read_text()
        digest = preview(self.client, self.manifest, "T1", self.journal)
        path = intent_path(self.journal, "T1")
        for key, value in (("parent_number", 78), ("repo", "other/repo"), ("version", 1)):
            with self.subTest(key=key):
                payload = json.loads(original)
                payload[key] = value
                self.manifest.write_text(json.dumps(payload))
                with self.assertRaises(Refusal):
                    apply(self.client, path, digest, self.manifest)
                self.assertFalse(attempt_path(path).exists())
        for key, value in (("local_id", "T2"), ("title", "Changed"), ("body", "Changed"), ("labels", ["bug"])):
            with self.subTest(key=key):
                payload = json.loads(original)
                payload["tickets"][0][key] = value
                self.manifest.write_text(json.dumps(payload))
                with self.assertRaises(Refusal):
                    apply(self.client, path, digest, self.manifest)
        self.assertEqual(self.client.issues.posts, [])

    def test_generic_identifiers_require_approval_and_safe_journal_names(self):
        self.generic_manifest(local_id="RF3a.fix_1")
        preview(self.client, self.manifest, "RF3a.fix_1", self.journal)
        with self.assertRaisesRegex(Refusal, "absent"):
            preview(self.client, self.manifest, "T2", self.journal)
        for local_id in ("../escape", "/absolute", ".", "bad:marker", "bad\\path", "x" * 65):
            with self.subTest(local_id=local_id):
                self.generic_manifest(local_id=local_id)
                with self.assertRaises(Refusal):
                    preview(self.client, self.manifest, local_id, self.journal)
        self.assertEqual(self.client.issues.posts, [])

    def test_legacy_manifest_cannot_select_generic_parent_or_identifier(self):
        original = self.manifest.read_text()
        for parent, local_id in ((77, "A01"), (None, "A01"), (11, "T1")):
            with self.subTest(parent=parent, local_id=local_id):
                payload = json.loads(original)
                payload["parent_number"] = parent
                payload["tickets"][0]["local_id"] = local_id
                self.manifest.write_text(json.dumps(payload))
                with self.assertRaises(Refusal):
                    manifest(self.manifest)

    def test_generic_parent_identity_changes_refuse_send_or_leave_verify_unresolved(self):
        self.generic_manifest()
        digest = preview(self.client, self.manifest, "T1", self.journal)
        path = intent_path(self.journal, "T1")
        self.client.issues.parent["id"] = 808
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, path, digest, self.manifest)
        self.client.issues.parent["id"] = 707
        self.assertEqual(apply(self.client, path, digest, self.manifest), "VERIFIED")
        self.client.issues.parent["id"] = 808
        self.assertEqual(verify(self.client, path, digest, self.manifest), "UNRESOLVED")

    def test_standalone_requires_complete_fresh_inventory_and_unique_marker(self):
        self.generic_manifest(parent=None, local_id="spec")
        self.client.issues.repository = [row(n, n + 1000) for n in range(1, 2001)]
        with self.assertRaisesRegex(Refusal, "incomplete"):
            preview(self.client, self.manifest, "spec", self.journal)
        self.client.issues.repository = [self.client.issues.parent]
        digest = preview(self.client, self.manifest, "spec", self.journal)
        path = intent_path(self.journal, "spec")
        self.client.issues.repository.append(row(78, 808))
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, path, digest, self.manifest)
        self.client.issues.repository.pop()
        self.assertEqual(apply(self.client, path, digest, self.manifest), "VERIFIED")
        duplicate = row(79, 809, full_body(self.ticket))
        duplicate["state"] = "closed"
        self.client.issues.repository.append(duplicate)
        self.assertEqual(verify(self.client, path, digest, self.manifest), "UNRESOLVED")
        with self.assertRaisesRegex(Refusal, "inventory"):
            preview(self.client, self.manifest, "spec", self.journal.parent / "other")

    def test_generic_manifest_refuses_duplicate_ids_and_noninteger_parent(self):
        self.generic_manifest()
        original = self.manifest.read_text()
        for parent in (True, 0, -1, "77"):
            with self.subTest(parent=parent):
                payload = json.loads(original)
                payload["parent_number"] = parent
                self.manifest.write_text(json.dumps(payload))
                with self.assertRaises(Refusal):
                    manifest(self.manifest)
        payload = json.loads(original)
        payload["tickets"].append(payload["tickets"][0])
        self.manifest.write_text(json.dumps(payload))
        with self.assertRaises(Refusal):
            manifest(self.manifest)

    def test_single_create_parent_id_and_durable_binding(self):
        self.assertEqual(apply(self.client, self.path, self.digest, self.manifest), "VERIFIED")
        self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "VERIFIED")
        self.assertEqual(len(self.client.issues.posts), 1)
        binding = json.loads(binding_path(self.path).read_text())
        self.assertEqual((binding["issue_id"], binding["issue_number"]), (1001, 62))
        self.assertEqual(self.client.issues.posts[0]["body"], full_body(self.ticket))
        with self.assertRaisesRegex(Refusal, "verify only"):
            apply(self.client, self.path, self.digest, self.manifest)

    def test_pre_send_timeout_blocks_second_post(self):
        self.client.issues.failure = "before"
        self.assertEqual(apply(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
        self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
        with self.assertRaises(Refusal):
            apply(self.client, self.path, self.digest, self.manifest)
        self.assertEqual(len(self.client.issues.posts), 1)

    def test_post_send_timeout_5xx_and_death_are_verify_only(self):
        for failure in ("after", "503", "death"):
            with self.subTest(failure=failure):
                self.setUp()
                self.client.issues.failure = failure
                if failure == "death":
                    with self.assertRaises(KeyboardInterrupt):
                        apply(self.client, self.path, self.digest, self.manifest)
                else:
                    self.assertEqual(apply(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
                self.assertTrue(attempt_path(self.path).exists())
                self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "VERIFIED")
                with self.assertRaises(Refusal):
                    apply(self.client, self.path, self.digest, self.manifest)
                self.assertEqual(len(self.client.issues.posts), 1)

    def test_created_before_parent_attachment_is_unresolved(self):
        self.client.issues.attach = False
        self.assertEqual(apply(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
        self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
        self.client.issues.children.append(self.client.issues.repository[-1])
        self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "VERIFIED")
        self.assertEqual(len(self.client.issues.posts), 1)

    def test_list_visibility_lag_never_uses_search_or_reposts(self):
        self.client.issues.visible = False
        self.assertEqual(apply(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
        self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "UNRESOLVED")
        self.client.issues.visible = True
        self.assertEqual(verify(self.client, self.path, self.digest, self.manifest), "VERIFIED")
        self.assertEqual(len(self.client.issues.posts), 1)

    def test_fresh_preimage_drift_and_existing_marker_refuse(self):
        self.client.issues.parent["updated_at"] = "t2"
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, self.path, self.digest, self.manifest)
        self.assertFalse(attempt_path(self.path).exists())
        self.client.issues.parent["updated_at"] = "t1"
        existing = row(55, 999, full_body(self.ticket))
        self.client.issues.repository.append(existing)
        with self.assertRaises(Refusal):
            preview(self.client, self.manifest, "A01", self.journal.parent / "other")

    def test_repository_listing_not_search_index_and_limit(self):
        self.client.issues.repository += [row(n, n + 1000) for n in range(100, 199)]
        self.assertEqual(len(pages(self.client, None)), 100)
        self.client.issues.children = [row(n, n + 1000) for n in range(200, 300)]
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, self.path, self.digest, self.manifest)
        self.assertFalse(attempt_path(self.path).exists())

    def test_manifest_hash_and_ready_label_refusal(self):
        data = json.loads(self.manifest.read_text())
        data["tickets"][0]["labels"] = ["ready-for-agent"]
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(Refusal):
            manifest(self.manifest)
        with self.assertRaises(Refusal):
            apply(self.client, self.path, self.digest, self.manifest)

    def test_invalid_local_input_refuses_before_credential_lookup(self):
        argv = ["issue_create.py", "apply", "--manifest-file", str(self.manifest),
                "--local-id", "A01", "--journal-dir", str(self.journal),
                "--intent-sha256", "0" * 64]
        with patch("sys.argv", argv), patch("issue_create.credential") as secret:
            self.assertEqual(main(), 2)
            secret.assert_not_called()


if __name__ == "__main__":
    unittest.main()
