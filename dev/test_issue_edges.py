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

    def rf_graph(self):
        tickets, manifests = [], []
        for parent, nodes in ((201, {"RF1": []}), (202, {"RF2": []}),
                              (203, {"RF3a": ["RF1", "RF2"], "RF3b": []}),
                              (204, {"RF4": ["RF1", "RF2", "RF3a", "RF3b"]})):
            path = self.root / f"rf-{parent}.json"
            payload = {"version": 2, "repo": edges.REPOSITORY,
                       "parent_number": parent, "tickets": [
                           {"local_id": key, "title": key, "body": key,
                            "body_sha256": edges.sha(key.encode()), "labels": []}
                           for key in nodes]}
            path.write_bytes(edges.wire(payload))
            digest = edges.sha(path.read_bytes())
            manifests.append({"file": path.name, "sha256": digest, "parent_number": parent})
            for key, blockers in nodes.items():
                number = 301 + len(tickets)
                tickets.append({"local_id": key, "intent_sha256": "0" * 64,
                                "manifest_sha256": digest, "issue_id": 9000 + number,
                                "issue_number": number, "blocked_by": blockers})
        graph = {"schema": "marketplace-edge-graph-v2", "status": "verified",
                 "repo": edges.REPOSITORY, "manifests": manifests, "tickets": tickets}
        self.graph.write_bytes(edges.wire(graph))
        self.common = (self.root / "rf-201.json", self.graph,
                       edges.sha(self.graph.read_bytes()))
        self.client = Fake({row["local_id"]: row for row in tickets})
        return graph

    def test_cross_parent_graph_publishes_only_declared_edges(self):
        self.rf_graph()
        for target, blocker in (("RF3a", "RF1"), ("RF3a", "RF2"),
                                ("RF4", "RF1"), ("RF4", "RF2"),
                                ("RF4", "RF3a"), ("RF4", "RF3b")):
            digest = edges.preview(self.client, *self.common, self.journal, target, blocker)
            path = self.journal / f"{target}-by-{blocker}.intent.json"
            self.assertEqual(edges.apply(self.client, path, digest, *self.common), "EDGE_VERIFIED")
        bindings, _ = edges.approved(*self.common)
        self.assertEqual(edges.audit(self.client, bindings), "NEW_EDGES_VERIFIED")
        with self.assertRaises(edges.Refusal):
            edges.preview(self.client, *self.common, self.journal, "RF3b", "RF1")

    def test_cyclic_graph_refuses_before_journal_or_send(self):
        graph = self.rf_graph()
        graph["tickets"][0]["blocked_by"] = ["RF4"]
        self.graph.write_bytes(edges.wire(graph))
        self.common = (*self.common[:2], edges.sha(self.graph.read_bytes()))
        with self.assertRaises(edges.Refusal):
            edges.preview(self.client, *self.common, self.journal, "RF3a", "RF1")
        self.assertEqual(list(self.journal.iterdir()), [])
        self.assertEqual(self.client.writes, 0)

    def test_foreign_native_edges_block_preview_apply_and_verification(self):
        self.rf_graph()
        foreign = {"id": 9301, "number": 301}
        self.client.deps[304] = [foreign]
        with self.assertRaises(edges.Refusal):
            edges.preview(self.client, *self.common, self.journal, "RF3a", "RF1")
        self.client.deps[304] = []
        digest = edges.preview(self.client, *self.common, self.journal, "RF3a", "RF1")
        path = self.journal / "RF3a-by-RF1.intent.json"
        self.client.deps[304] = [foreign]
        with self.assertRaises(edges.Refusal):
            edges.apply(self.client, path, digest, *self.common)
        self.assertFalse(edges.attempt_path(path).exists())
        self.client.deps[304] = []
        self.assertEqual(edges.apply(self.client, path, digest, *self.common), "EDGE_VERIFIED")
        self.client.deps[303].append({"id": 9304, "number": 304})
        self.assertEqual(edges.verify(self.client, path, digest, *self.common), "UNRESOLVED")
        self.assertEqual(self.client.writes, 1)

    def test_changed_manifest_or_graph_bytes_refuse_saved_intent(self):
        self.rf_graph()
        digest = edges.preview(self.client, *self.common, self.journal, "RF3a", "RF1")
        path = self.journal / "RF3a-by-RF1.intent.json"
        for source in (self.graph, self.root / "rf-202.json", self.common[0]):
            with self.subTest(source=source.name):
                original = source.read_bytes()
                source.write_bytes(original + b"\n")
                with self.assertRaises(edges.Refusal):
                    edges.apply(self.client, path, digest, *self.common)
                source.write_bytes(original)
        self.assertFalse(edges.attempt_path(path).exists())
        self.assertEqual(self.client.writes, 0)

    def test_generic_ambiguous_send_and_crash_are_verify_only(self):
        self.rf_graph()
        digest = edges.preview(self.client, *self.common, self.journal, "RF3a", "RF1")
        path = self.journal / "RF3a-by-RF1.intent.json"
        self.client.ambiguous = True
        self.assertEqual(edges.apply(self.client, path, digest, *self.common), "UNRESOLVED")
        self.assertEqual(edges.verify(self.client, path, digest, *self.common), "EDGE_VERIFIED")
        with self.assertRaises(edges.Refusal):
            edges.apply(self.client, path, digest, *self.common)
        digest = edges.preview(self.client, *self.common, self.journal, "RF3a", "RF2")
        path = self.journal / "RF3a-by-RF2.intent.json"
        edges.publish(edges.attempt_path(path), edges.wire({"version": 1, "intent_sha256": digest}))
        self.assertEqual(edges.verify(self.client, path, digest, *self.common), "UNRESOLVED")
        with self.assertRaises(edges.Refusal):
            edges.apply(self.client, path, digest, *self.common)
        self.assertEqual(self.client.writes, 1)

    def test_bad_generic_bindings_refuse_before_publication(self):
        original = self.rf_graph()
        changes = [
            lambda g: g["tickets"][1].update(issue_id=9301),
            lambda g: g["tickets"][1].update(issue_number=301),
            lambda g: g["tickets"].append(g["tickets"][0]),
            lambda g: g["tickets"].pop(),
            lambda g: g["tickets"][0].update(blocked_by=["UNDECLARED"]),
            lambda g: g["tickets"][2].update(blocked_by=["RF1", "RF1"]),
            lambda g: g["tickets"][0].update(manifest_sha256="f" * 64),
            lambda g: g["tickets"][0].update(issue_number=201),
            lambda g: g["manifests"][0].update(parent_number=202),
            lambda g: g["manifests"].append(g["manifests"][0]),
            lambda g: g["manifests"][0].update(file="../outside.json"),
        ]
        for index, change in enumerate(changes):
            with self.subTest(control=index):
                graph = json.loads(edges.wire(original))
                change(graph)
                self.graph.write_bytes(edges.wire(graph))
                self.common = (*self.common[:2], edges.sha(self.graph.read_bytes()))
                with self.assertRaises(edges.Refusal):
                    edges.preview(self.client, *self.common, self.journal, "RF3a", "RF1")
        self.assertEqual(list(self.journal.iterdir()), [])
        self.assertEqual(self.client.writes, 0)

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

    def test_closed_nodes_retain_edges_and_old_intent_bytes(self):
        digest, path = self.preview_edge()
        self.assertNotIn("state_reason", json.loads(path.read_bytes())["preimage"]["issue"])
        self.assertEqual(edges.apply(self.client, path, digest, *self.common), "EDGE_VERIFIED")
        for row in self.client.rows.values():
            row.update(state="closed", state_reason="completed")
        for target, blockers in edges.BLOCKERS.items():
            self.client.deps[self.bindings[target]["issue_number"]] = [
                {"id": self.bindings[key]["issue_id"], "number": self.bindings[key]["issue_number"]}
                for key in blockers]
        bindings, _ = edges.approved(*self.common)
        self.assertEqual(edges.audit(self.client, bindings), "NEW_EDGES_VERIFIED")
        self.client.deps[63] = []
        self.assertEqual(edges.audit(self.client, bindings), "UNRESOLVED")

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
