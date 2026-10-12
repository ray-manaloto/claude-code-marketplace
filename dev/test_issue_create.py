"""Offline A08a public-boundary controls; no credentials or GitHub requests."""

import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

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

    @staticmethod
    def response(data):
        return SimpleNamespace(status_code=200, raw_response=SimpleNamespace(json=lambda: data))

    def get(self, owner, repo, number):
        assert (owner, repo, number) == ("ray-manaloto", "claude-code-marketplace", 11)
        return self.response(self.parent)

    def list_for_repo(self, owner, repo, *, state, per_page, page):
        assert state == "all" and per_page == 100
        rows = self.repository if self.visible else self.repository[:1]
        return self.response(rows[(page - 1) * 100:page * 100])

    def list_sub_issues(self, owner, repo, number, *, per_page, page):
        assert number == 11 and per_page == 100
        return self.response(self.children[(page - 1) * 100:page * 100])

    def create(self, owner, repo, *, data):
        assert (owner, repo) == ("ray-manaloto", "claude-code-marketplace")
        assert set(data) == {"title", "body", "labels", "parent_issue_id"}
        assert data["parent_issue_id"] == 101  # database id, never #11
        self.posts.append(data)
        if self.failure == "before":
            raise TimeoutError("before send")
        child = row(62, 1001, data["body"], data["labels"])
        child["title"] = data["title"]
        self.repository.append(child)
        if self.attach:
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
