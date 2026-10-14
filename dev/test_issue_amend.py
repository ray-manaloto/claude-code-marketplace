"""Offline A07a controls; no GitHub requests or credentials."""

import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from issue_amend import Refusal, apply, intent, main, marker, preview, verify
import issue_amend as amendment
from test_issue_create import private_name_sample, secret_sample


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
        assert set(data) in ({"body", "labels"}, {"state", "state_reason"})
        self.writes.append(data)
        if self.failure == "before":
            raise TimeoutError("before send")
        if "state" in data:
            self.current = {**self.current, **data, "updated_at": "t2"}
        else:
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
        self.requests = 0

    def rest(self, version):
        assert version == "2026-03-10"
        self.requests += 1
        return SimpleNamespace(issues=self.issues)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


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

    def test_retained_v1_intent_and_marker_remain_verify_only(self):
        self.path.write_text('{"version":1,"repo":"ray-manaloto/claude-code-marketplace",'
                             '"number":11,"preimage":{"id":77,"number":11,"title":"Spec",'
                             '"body":"old","state":"open","updated_at":"t1",'
                             '"labels":["ready-for-agent"]},'
                             '"desired":{"body":"retained","labels":["needs-info"]}}\n')
        digest = amendment.sha(self.path.read_bytes())
        marker(self.path).write_text('{"version":1,"intent_sha256":"' + digest +
                                     '","operation":"PATCH body labels"}\n')
        self.client.issues.current = issue("retained", ("needs-info",), "t2")
        self.assertEqual(verify(self.client, self.path, digest), "VERIFIED")
        with self.assertRaisesRegex(Refusal, "verify only"):
            apply(self.client, self.path, digest)
        self.assertEqual(self.client.issues.writes, [])

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

    def test_scan_hit_refuses_preview_before_any_request(self):
        for field, text, rule in (("body", private_name_sample(), "private-tr-project"),
                                  ("labels", secret_sample(), "aws-access-key-id")):
            with self.subTest(field=field):
                self.body.write_text(f"new {text}\n" if field == "body" else "new\n", encoding="utf-8")
                self.labels.write_text(json.dumps([text] if field == "labels" else []), encoding="utf-8")
                client, output = FakeClient(), self.path.with_name(f"preview-{field}.json")
                with self.assertRaises(Refusal) as caught:
                    preview(client, 11, self.body, self.labels, output)
                self.assertFalse(text in str(caught.exception), "fixture text leaked into the refusal")  # bool form: a failure never echoes the sample
                self.assertEqual(str(caught.exception).splitlines(),
                                 [f"secret scan hit: local id #11, field {field}, rule {rule}; nothing sent"])
                self.assertEqual((client.requests, output.exists()), (0, False))

    def test_scan_hit_refuses_apply_on_the_bytes_to_send(self):
        # An intent journaled before the scan existed still reaches the scan at apply.
        for field, text, rule in (("body", secret_sample(), "aws-access-key-id"),
                                  ("labels", private_name_sample(), "private-tr-project")):
            with self.subTest(field=field):
                data = json.loads(self.path.read_text())
                data["desired"] = {"body": f"new {text}\n" if field == "body" else "new\n",
                                   "labels": [text] if field == "labels" else []}
                path = self.path.with_name(f"apply-{field}.json")
                path.write_bytes(amendment.wire(data))
                client = FakeClient()
                with self.assertRaises(Refusal) as caught:
                    apply(client, path, amendment.sha(path.read_bytes()))
                self.assertFalse(text in str(caught.exception), "fixture text leaked into the refusal")  # bool form: a failure never echoes the sample
                self.assertEqual(str(caught.exception).splitlines(),
                                 [f"secret scan hit: local id #11, field {field}, rule {rule}; nothing sent"])
                self.assertEqual((client.requests, len(client.issues.writes), marker(path).exists()), (0, 0, False))

    def test_missing_pinned_scanner_fails_closed_at_preview_and_apply(self):
        with patch.object(amendment, "MISE", self.path.with_name("absent-mise")):
            client = FakeClient()
            with self.assertRaisesRegex(Refusal, "pinned betterleaks .* unavailable"):
                preview(client, 11, self.body, self.labels, self.path.with_name("other.json"))
            with self.assertRaisesRegex(Refusal, "pinned betterleaks .* unavailable"):
                apply(client, self.path, self.digest)
            self.assertEqual((client.requests, len(client.issues.writes), marker(self.path).exists()), (0, 0, False))

    def test_cli_names_each_hit_on_its_own_stderr_line_and_exits_2(self):
        name, key = private_name_sample(), secret_sample()
        self.body.write_text(f"{name}\n{key}\n", encoding="utf-8")
        argv = ["issue_amend.py", "preview", "--issue", "11", "--body-file", str(self.body),
                "--labels-file", str(self.labels), "--intent-file", str(self.path.with_name("cli.json"))]
        client, stderr = FakeClient(), io.StringIO()
        with (patch("sys.argv", argv), patch("issue_amend.credential", return_value=("offline", "test")),
              patch("issue_amend.GitHub", return_value=client), patch("sys.stderr", stderr)):
            self.assertEqual(main(), 2)
        self.assertFalse(name in stderr.getvalue() or key in stderr.getvalue(), "fixture text leaked into stderr")
        self.assertEqual(stderr.getvalue().splitlines(), [
            "REFUSED: secret scan hit: local id #11, field body, rule aws-access-key-id; nothing sent",
            "REFUSED: secret scan hit: local id #11, field body, rule private-tr-project; nothing sent"])
        self.assertEqual(client.requests, 0)

    def test_clean_amendment_is_sent_unchanged(self):
        self.assertEqual(apply(self.client, self.path, self.digest), "VERIFIED")
        self.assertEqual(self.client.issues.writes, [{"body": "new\n", "labels": ["needs-info", "ready-for-agent"]}])

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


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.path = self.base / "completion.json"
        self.client = FakeClient()
        before = {**issue(), "labels": ["ready-for-agent"], "state_reason": None}
        binding = {"repo": "ray-manaloto/claude-code-marketplace", "number": 11,
                   "issue_id": 77, "preimage_sha256": amendment.sha(amendment.wire(before))}
        refs = {}
        for kind, result in (("acceptance", "accepted"), ("review", "approved"),
                             ("retro", "applied"), ("delivery", "delivered")):
            path = self.base / f"{kind}.json"
            path.write_bytes(amendment.wire({"version": 1, **binding, "result": result}))
            refs[kind] = {"path": str(path), "sha256": amendment.sha(path.read_bytes())}
        self.evidence = self.base / "evidence.json"
        self.evidence.write_bytes(amendment.wire({"version": 1, **binding, "references": refs}))

    def prepare(self):
        return amendment.preview_completion(self.client, 11, self.evidence, self.path)

    def test_completion_preserves_content_and_closes_only_bound_issue(self):
        digest = self.prepare()
        self.assertEqual(apply(self.client, self.path, digest), "VERIFIED")
        self.assertEqual(verify(self.client, self.path, digest), "VERIFIED")
        self.assertEqual(self.client.issues.writes, [{"state": "closed", "state_reason": "completed"}])
        self.assertEqual(self.client.issues.current["body"], "old")
        with self.assertRaisesRegex(Refusal, "verify only"):
            apply(self.client, self.path, digest)

    def test_already_completed_is_truthful_no_send(self):
        digest = self.prepare()
        self.client.issues.current.update(state="closed", state_reason="completed", updated_at="t2")
        self.assertEqual(apply(self.client, self.path, digest), "ALREADY_COMPLETED")
        self.assertEqual(apply(self.client, self.path, digest), "ALREADY_COMPLETED")
        self.assertEqual(self.client.issues.writes, [])
        self.assertFalse(marker(self.path).exists())

    def test_stale_evidence_is_refused_before_journal_or_send(self):
        digest = self.prepare()
        (self.base / "review.json").write_text("{}")
        with self.assertRaisesRegex(Refusal, "evidence SHA-256"):
            apply(self.client, self.path, digest)
        self.assertFalse(marker(self.path).exists())
        self.assertEqual(self.client.issues.writes, [])

    def test_wrong_evidence_identity_or_verdict_cannot_prepare_closure(self):
        original = self.evidence.read_bytes()
        for field, value in (("repo", "other/repo"), ("number", 12), ("issue_id", 78),
                             ("preimage_sha256", "0" * 64)):
            with self.subTest(field=field):
                data = json.loads(original)
                data[field] = value
                self.evidence.write_bytes(amendment.wire(data))
                with self.assertRaises(Refusal):
                    self.prepare()
                self.assertFalse(self.path.exists())
        self.evidence.write_bytes(original)
        for kind in ("acceptance", "review", "retro", "delivery"):
            with self.subTest(kind=kind):
                data = json.loads(original)
                del data["references"][kind]
                self.evidence.write_bytes(amendment.wire(data))
                with self.assertRaises(Refusal):
                    self.prepare()
                data = json.loads(original)
                receipt_path = self.base / f"{kind}.json"
                saved = receipt_path.read_bytes()
                receipt = json.loads(saved)
                receipt["result"] = "pending"
                receipt_path.write_bytes(amendment.wire(receipt))
                data["references"][kind]["sha256"] = amendment.sha(receipt_path.read_bytes())
                self.evidence.write_bytes(amendment.wire(data))
                with self.assertRaisesRegex(Refusal, f"{kind} evidence"):
                    self.prepare()
                receipt_path.write_bytes(saved)

    def test_exact_preimage_rejects_drift_and_wrong_issue_id(self):
        digest = self.prepare()
        for field, value in (("updated_at", "stale"), ("id", 78), ("number", 12)):
            with self.subTest(field=field):
                self.client.issues.current = {**issue(), field: value}
                with self.assertRaises(Refusal):
                    apply(self.client, self.path, digest)
                self.assertFalse(marker(self.path).exists())
        self.assertEqual(self.client.issues.writes, [])

    def test_uncertain_closure_is_verify_only(self):
        for failure, result in (("before", "UNRESOLVED"), ("after", "VERIFIED"), ("503", "VERIFIED")):
            with self.subTest(failure=failure):
                self.path = self.base / f"{failure}.json"
                self.client = FakeClient()
                digest = self.prepare()
                self.client.issues.failure = failure
                self.assertEqual(apply(self.client, self.path, digest), "UNRESOLVED")
                self.assertEqual(verify(self.client, self.path, digest), result)
                with self.assertRaisesRegex(Refusal, "verify only"):
                    apply(self.client, self.path, digest)
                self.assertEqual(len(self.client.issues.writes), 1)

    def test_process_death_keeps_completion_marker(self):
        digest = self.prepare()
        self.client.issues.failure = "death"
        with self.assertRaises(KeyboardInterrupt):
            apply(self.client, self.path, digest)
        self.assertEqual(verify(self.client, self.path, digest), "VERIFIED")
        with self.assertRaisesRegex(Refusal, "verify only"):
            apply(self.client, self.path, digest)

    def test_closed_wrong_reason_or_changed_content_does_not_claim_completion(self):
        digest = self.prepare()
        self.client.issues.current.update(state="closed", state_reason="not_planned")
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, self.path, digest)
        with self.assertRaisesRegex(Refusal, "already closed"):
            amendment.preview_completion(self.client, 11, self.evidence, self.base / "closed.json")
        self.client.issues.current.update(state_reason="completed", body="unrelated amendment")
        with self.assertRaisesRegex(Refusal, "drifted"):
            apply(self.client, self.path, digest)
        self.assertEqual(self.client.issues.writes, [])

    def test_completion_verification_preserves_reason_and_content(self):
        digest = self.prepare()
        self.assertEqual(apply(self.client, self.path, digest), "VERIFIED")
        for field, value in (("state_reason", "not_planned"), ("body", "unrelated"), ("id", 78)):
            saved = self.client.issues.current.copy()
            self.client.issues.current[field] = value
            self.assertEqual(verify(self.client, self.path, digest), "UNRESOLVED")
            self.client.issues.current = saved

    def test_typed_evidence_refuses_equal_but_noninteger_identity(self):
        data = json.loads(self.evidence.read_bytes())
        data["issue_id"] = 77.0
        self.evidence.write_bytes(amendment.wire(data))
        with self.assertRaisesRegex(Refusal, "evidence binding"):
            self.prepare()


if __name__ == "__main__":
    unittest.main()
