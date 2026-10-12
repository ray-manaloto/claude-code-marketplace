"""Offline A07a controls; no GitHub requests or credentials."""

import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from issue_amend import Refusal, apply, intent, marker, preview, verify


def issue(body="old", labels=("ready-for-agent",), updated="t1"):
    return {"id": 77, "number": 11, "title": "Spec", "body": body,
            "state": "open", "updated_at": updated,
            "labels": [{"name": name} for name in labels]}


class FakeIssues:
    def __init__(self):
        self.current = issue()
        self.writes = []
        self.failure = None

    def get(self, owner, repo, number):
        assert (owner, repo, number) == ("ray-manaloto", "claude-code-marketplace", 11)
        return SimpleNamespace(status_code=200, raw_response=SimpleNamespace(json=lambda: self.current))

    def update(self, owner, repo, number, *, data):
        assert (owner, repo, number) == ("ray-manaloto", "claude-code-marketplace", 11)
        assert set(data) == {"body", "labels"}
        self.writes.append(data)
        if self.failure == "before":
            raise TimeoutError("before send")
        self.current = issue(data["body"], tuple(reversed(data["labels"])), "t2")
        if self.failure == "after":
            raise TimeoutError("after application")
        if self.failure == "503":
            raise RuntimeError("HTTP 503 after application")
        if self.failure == "death":
            raise KeyboardInterrupt
        return SimpleNamespace(status_code=200)


class FakeClient:
    def __init__(self):
        self.issues = FakeIssues()

    def rest(self, version):
        assert version == "2026-03-10"
        return SimpleNamespace(issues=self.issues)


class AmendmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.body = base / "body.md"
        self.body.write_text("new\n", encoding="utf-8")
        self.labels = base / "labels.json"
        self.labels.write_text('["ready-for-agent", "needs-info"]', encoding="utf-8")
        self.path = base / "intent.json"
        self.client = FakeClient()
        self.digest = preview(self.client, 11, self.body, self.labels, self.path)

    def test_single_write_and_exact_normalized_postimage(self):
        self.assertEqual(apply(self.client, self.path, self.digest), "VERIFIED")
        self.assertEqual(verify(self.client, self.path, self.digest), "VERIFIED")
        self.assertEqual(len(self.client.issues.writes), 1)
        with self.assertRaisesRegex(Refusal, "verify only"):
            apply(self.client, self.path, self.digest)
        self.assertEqual(set(self.client.issues.writes[0]), {"body", "labels"})

    def test_drift_prevents_marker_and_write(self):
        self.client.issues.current = issue(updated="t-other")
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, self.path, self.digest)
        self.assertFalse(marker(self.path).exists())
        self.assertEqual(self.client.issues.writes, [])

    def test_after_application_timeout_is_verify_only(self):
        self.client.issues.failure = "after"
        self.assertEqual(apply(self.client, self.path, self.digest), "UNRESOLVED")
        self.assertEqual(verify(self.client, self.path, self.digest), "VERIFIED")
        with self.assertRaises(Refusal):
            apply(self.client, self.path, self.digest)
        self.assertEqual(len(self.client.issues.writes), 1)

    def test_before_send_timeout_is_not_retried(self):
        self.client.issues.failure = "before"
        self.assertEqual(apply(self.client, self.path, self.digest), "UNRESOLVED")
        self.assertEqual(verify(self.client, self.path, self.digest), "UNRESOLVED")
        with self.assertRaises(Refusal):
            apply(self.client, self.path, self.digest)
        self.assertEqual(len(self.client.issues.writes), 1)

    def test_applied_5xx_is_verify_only(self):
        self.client.issues.failure = "503"
        self.assertEqual(apply(self.client, self.path, self.digest), "UNRESOLVED")
        self.assertEqual(verify(self.client, self.path, self.digest), "VERIFIED")
        with self.assertRaises(Refusal):
            apply(self.client, self.path, self.digest)

    def test_postimage_body_is_byte_exact(self):
        self.assertEqual(apply(self.client, self.path, self.digest), "VERIFIED")
        self.client.issues.current["body"] = "new\r\n"
        self.assertEqual(verify(self.client, self.path, self.digest), "UNRESOLVED")

    def test_process_death_after_send_keeps_marker(self):
        self.client.issues.failure = "death"
        with self.assertRaises(KeyboardInterrupt):
            apply(self.client, self.path, self.digest)
        self.assertTrue(marker(self.path).exists())
        self.assertEqual(verify(self.client, self.path, self.digest), "VERIFIED")
        with self.assertRaises(Refusal):
            apply(self.client, self.path, self.digest)

    def test_intent_tamper_and_state_close_are_refused(self):
        with self.assertRaisesRegex(Refusal, "SHA-256"):
            intent(self.path, "0" * 64)
        self.client.issues.current = {**issue(), "state": "closed"}
        with self.assertRaisesRegex(Refusal, "identity or state"):
            apply(self.client, self.path, self.digest)
        self.assertEqual(self.client.issues.writes, [])

    def test_extra_field_and_pull_request_refused(self):
        source = json.loads(self.path.read_text())
        source["desired"]["state"] = "closed"
        self.path.write_text(json.dumps(source))
        from issue_amend import sha
        with self.assertRaisesRegex(Refusal, "invalid amendment"):
            intent(self.path, sha(self.path.read_bytes()))
        self.client.issues.current = {**issue(), "pull_request": {}}
        other = self.path.with_name("other.json")
        with self.assertRaisesRegex(Refusal, "pull request"):
            preview(self.client, 11, self.body, self.labels, other)

    def test_nested_symlink_cannot_redirect_intent_or_marker(self):
        base = Path(self.temp.name)
        outside = base / "outside"
        outside.mkdir()
        link = base / "linked"
        link.symlink_to(outside, target_is_directory=True)
        target = link / "deep" / "intent.json"
        (outside / "deep").mkdir()
        (outside / "deep" / "body.md").write_text("redirected")
        with self.assertRaisesRegex(Refusal, "symlink"):
            preview(self.client, 11, self.body, self.labels, target)
        self.assertFalse((outside / "deep" / "intent.json").exists())
        with self.assertRaisesRegex(Refusal, "symlink"):
            preview(self.client, 11, link / "deep" / "body.md", self.labels, base / "other.json")
        real_intent = outside / "deep" / "intent.json"
        digest = preview(self.client, 11, self.body, self.labels, real_intent)
        with self.assertRaisesRegex(Refusal, "symlink"):
            apply(self.client, target, digest)
        self.assertFalse(marker(real_intent).exists())
        self.assertEqual(self.client.issues.writes, [])


if __name__ == "__main__":
    unittest.main()
