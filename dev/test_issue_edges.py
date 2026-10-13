"""Offline A08b1 intent, drift, ambiguity and new-edge controls."""

import json
from pathlib import Path
import tempfile
import unittest

import issue_edges as edges


class Response:
    def __init__(self, raw, code=200):
        self.status_code = code
        self.raw_response = self
        self.raw = raw

    def json(self):
        return self.raw


class Fake:
    def __init__(self, bindings):
        self.issues = self
        self.rows = {}
        self.deps = {}
        self.writes = 0
        self.ambiguous = False
        for item in bindings.values():
            number = item["issue_number"]
            self.rows[number] = {"id": item["issue_id"], "number": number,
                                 "title": f"issue {number}", "body": "body", "state": "open",
                                 "updated_at": "2026-10-12T00:00:00Z", "labels": []}
            self.deps[number] = []

    def rest(self, _):
        return self

    def get(self, _, __, number):
        return Response(self.rows[number])

    def list_dependencies_blocked_by(self, _, __, number, **kwargs):
        return Response(self.deps[number])

    def add_blocked_by_dependency(self, _, __, number, *, data):
        self.writes += 1
        blocker = next(row for row in self.rows.values() if row["id"] == data["issue_id"])
        self.deps[number].append({"id": blocker["id"], "number": blocker["number"]})
        if self.ambiguous:
            raise TimeoutError("response lost after server apply")
        return Response({}, 201)

class EdgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.journal = self.root / "journal"
        self.journal.mkdir()
        self.manifest = Path(__file__).with_name("issue-tickets.json")
        payload, manifest_sha = edges.manifest(self.manifest)
        tickets = []
        for index, ticket in enumerate(payload["tickets"]):
            tickets.append({"local_id": ticket["local_id"], "intent_sha256": "0" * 64,
                            "issue_id": 1000 + index, "issue_number": 62 + index})
        self.bindings = {x["local_id"]: x for x in tickets}
        self.graph = self.root / "graph.json"
        self.graph.write_bytes(edges.wire({"schema": "a08b-graph-audit-v1",
                                           "status": "verified", "repo": edges.REPOSITORY,
                                           "manifest_sha256": manifest_sha, "parent_number": 11,
                                           "child_count": 67, "tickets": tickets}))
        self.graph_sha = edges.sha(self.graph.read_bytes())
        self.common = (self.manifest, self.graph, self.graph_sha)
        self.client = Fake(self.bindings)

    def preview_edge(self):
        digest = edges.preview(self.client, *self.common, self.journal, "A02", "A01")
        return digest, edges.path_for(self.journal, "A02", "A01")

    def test_ambiguous_send_verifies_without_second_post(self):
        digest, intent = self.preview_edge()
        self.client.ambiguous = True
        self.assertEqual(edges.apply(self.client, intent, digest, *self.common), "UNRESOLVED")
        self.assertEqual(self.client.writes, 1)
        self.assertEqual(edges.verify(self.client, intent, digest, *self.common), "EDGE_VERIFIED")
        with self.assertRaises(edges.Refusal):
            edges.apply(self.client, intent, digest, *self.common)
        self.assertEqual(self.client.writes, 1)

    def test_drift_refuses_before_attempt(self):
        digest, intent = self.preview_edge()
        self.client.rows[63]["updated_at"] = "changed"
        with self.assertRaises(edges.Refusal):
            edges.apply(self.client, intent, digest, *self.common)
        self.assertFalse(edges.attempt_path(intent).exists())
        self.assertEqual(self.client.writes, 0)

    def test_unapproved_edge_and_partial_audit(self):
        with self.assertRaises(edges.Refusal):
            edges.preview(self.client, *self.common, self.journal, "A02", "A09")
        bindings, _ = edges.approved(*self.common)
        self.assertEqual(edges.audit(self.client, bindings), "UNRESOLVED")

    def test_duplicate_preview_refused(self):
        self.preview_edge()
        with self.assertRaises(edges.Refusal):
            self.preview_edge()
        self.assertEqual(self.client.writes, 0)

    def test_full_new_edge_audit_has_scoped_status(self):
        for target, blockers in edges.BLOCKERS.items():
            number = self.bindings[target]["issue_number"]
            self.client.deps[number] = [
                {"id": self.bindings[key]["issue_id"],
                 "number": self.bindings[key]["issue_number"]} for key in blockers]
        bindings, _ = edges.approved(*self.common)
        self.assertEqual(edges.audit(self.client, bindings), "NEW_EDGES_VERIFIED")

    def test_alias_issue_binding_refused(self):
        graph = json.loads(self.graph.read_bytes())
        graph["tickets"][1]["issue_id"] = graph["tickets"][0]["issue_id"]
        self.graph.write_bytes(edges.wire(graph))
        self.graph_sha = edges.sha(self.graph.read_bytes())
        self.common = (self.manifest, self.graph, self.graph_sha)
        with self.assertRaises(edges.Refusal):
            edges.approved(*self.common)
        graph["tickets"][1]["issue_id"] = 1001
        graph["tickets"][1]["issue_number"] = graph["tickets"][0]["issue_number"]
        self.graph.write_bytes(edges.wire(graph))
        self.graph_sha = edges.sha(self.graph.read_bytes())
        self.common = (self.manifest, self.graph, self.graph_sha)
        with self.assertRaises(edges.Refusal):
            edges.approved(*self.common)

    def test_crash_after_marker_is_verify_only(self):
        digest, intent = self.preview_edge()
        edges.publish(edges.attempt_path(intent), edges.wire({"version": 1,
                                                               "intent_sha256": digest}))
        self.assertEqual(edges.verify(self.client, intent, digest, *self.common), "UNRESOLVED")
        with self.assertRaises(edges.Refusal):
            edges.apply(self.client, intent, digest, *self.common)
        self.assertEqual(self.client.writes, 0)


if __name__ == "__main__":
    unittest.main()
