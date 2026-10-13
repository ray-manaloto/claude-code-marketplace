"""Synthetic offline outcomes through the shared receipt/state seam."""
import copy
import json
import hashlib
import unittest

import research_outcomes as outcomes


class OutcomeChecks(unittest.TestCase):
    def setUp(self):
        self.evidence = {"raw.json": b"synthetic snapshot", "diff.json": b"synthetic comparison",
                         "stderr.txt": b"synthetic diagnostic reference"}
        self.ref = lambda path: {"path": path, "sha256": hashlib.sha256(self.evidence[path]).hexdigest()}
        self.row = {"query_fingerprint": "query-a", "error_code": "NONE", "is_complete": True,
                    "item_count": 1, "issues": [{"html_url": "https://github.com/o/r/issues/1"}]}
        self.evidence["raw.json"] = json.dumps({"q": self.row}).encode()
        self.evidence["diff.json"] = json.dumps({"status": "compared", "baseline": self.ref("raw.json"),
                                               "current": self.ref("raw.json")}).encode()
        self.observation = {"cycle_id": "c1", "provider_invoked": True, "native_exit": 0,
                            "comparison_exit": None, "failed_stage": None, "rows": {"q": self.row},
                            "evidence": {"snapshot": self.ref("raw.json")}}
        self.previous = {"baseline": None, "queries": {}}

    def settle(self, receipt, previous=None):
        event = {"cycle_id": receipt["cycle_id"], "receipt_sha256": outcomes.digest(receipt)}
        pointer = {**event, "event_sha256": outcomes.digest(event)}
        return outcomes.settle_attempt(previous or self.previous, receipt, event, pointer, self.evidence)

    def accept_baseline(self):
        self.previous = self.settle(outcomes.evaluate_attempt(self.previous, self.observation, self.evidence))

    def assert_healthy_recovery(self):
        healthy = {**self.observation, "cycle_id": "recovery", "comparison_exit": 0,
                   "evidence": {**self.observation["evidence"], "comparison": self.ref("diff.json")}}
        receipt = outcomes.evaluate_attempt(self.previous, healthy, self.evidence)
        self.assertEqual((receipt["runner_exit"], receipt["comparison_state"], receipt["baseline_before"]),
                         (0, "compared", self.previous["baseline"]))
        self.assertEqual(self.settle(receipt)["baseline"], self.previous["baseline"])

    def test_runtime_drift_preserves_known_native_failure_and_healthy_recovery(self):
        self.accept_baseline()
        receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
            "failed_stage": "runtime_binding", "native_exit": 17, "rows": None,
            "evidence": {"stderr": self.ref("stderr.txt")}}, self.evidence)
        self.assertEqual((receipt["runner_exit"], receipt["native_exit"], receipt["comparison_state"]),
                         (17, 17, "unresolved"))
        self.assertEqual(self.settle(receipt), self.previous)
        self.assert_healthy_recovery()

    def test_api_error_under_native_zero_freezes_history_before_healthy_recovery(self):
        self.accept_baseline()
        rows = {"q": {**self.row, "error_code": "API_ERROR"}}
        self.evidence["error.json"] = json.dumps(rows).encode()
        receipt = outcomes.evaluate_attempt(self.previous, {**self.observation, "rows": rows,
            "evidence": {"snapshot": self.ref("error.json")}}, self.evidence)
        self.assertEqual((receipt["failed_stage"], receipt["runner_exit"], receipt["comparison_state"]),
                         ("validation", 2, "unresolved"))
        self.assertEqual(self.settle(receipt), self.previous)
        self.assert_healthy_recovery()

    def test_total_count_classifies_cap_independently_of_native_complete(self):
        self.accept_baseline()
        rows = {"q": {**self.row, "total_count": 100}}
        self.evidence["cap-total.json"] = json.dumps(rows).encode()
        current = self.ref("cap-total.json")
        self.evidence["cap-diff.json"] = json.dumps({"status": "compared", "baseline": self.previous["baseline"], "current": current}).encode()
        receipt = outcomes.evaluate_attempt(self.previous, {**self.observation, "rows": rows,
            "comparison_exit": 0, "evidence": {"snapshot": current, "comparison": self.ref("cap-diff.json")}}, self.evidence)
        self.assertEqual((receipt["runner_exit"], receipt["comparison_state"]), (2, "suppressed"))
        warning = self.settle(receipt)
        self.assertEqual(warning["baseline"], self.previous["baseline"])
        self.assertEqual((warning["queries"]["q"]["complete"], warning["queries"]["q"]["native_complete"],
                          warning["queries"]["q"]["capped_streak"]), (False, True, 1))
        self.previous = warning
        self.assert_healthy_recovery()

    def test_compatible_coverage_warning_requires_verified_comparison(self):
        self.accept_baseline()
        rows = {"q": {**self.row, "is_complete": False}}
        self.evidence["warning.json"] = json.dumps(rows).encode()
        for exit_code, ref in ((None, None), (0, None), (0, "malformed.json")):
            self.evidence["malformed.json"] = b"[]"
            refs = {"snapshot": self.ref("warning.json")}
            if ref:
                refs["comparison"] = self.ref(ref)
            receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                "rows": rows, "comparison_exit": exit_code, "evidence": refs}, self.evidence)
            self.assertEqual((receipt["runner_exit"], receipt["failed_stage"], receipt["comparison_state"]),
                             (2, "comparison", "unresolved"))
            self.assertEqual(self.settle(receipt), self.previous)
            self.assert_healthy_recovery()

    def test_nested_private_fields_and_malformed_containers_fail_closed(self):
        self.accept_baseline()
        for case in ("prior_list", "prior_private", "row_private", "item_private", "rows_list",
                     "refs_list", "nonbytes", "baseline_null"):
            previous, observation, evidence = copy.deepcopy((self.previous, self.observation, self.evidence))
            if case == "prior_list": previous["queries"] = []
            if case == "prior_private": previous["queries"]["q"]["private_note"] = "synthetic"
            if case == "row_private": observation["rows"]["q"]["api_key"] = "synthetic"
            if case == "item_private": observation["rows"]["q"]["issues"][0]["api_key"] = "synthetic"
            if case == "rows_list": observation["rows"] = []
            if case == "refs_list": observation["evidence"] = []
            if case == "nonbytes": evidence["raw.json"] = None
            if case == "baseline_null":
                evidence["null.json"] = b"null"
                previous["baseline"] = {"path": "null.json", "sha256": hashlib.sha256(b"null").hexdigest()}
            before = copy.deepcopy((previous, observation, evidence))
            with self.subTest(case=case), self.assertRaises(ValueError):
                outcomes.evaluate_attempt(previous, observation, evidence)
            self.assertEqual((previous, observation, evidence), before)
            self.assert_healthy_recovery()

    def test_stage_invocation_tuples_reject_contradictions_but_allow_unknown_completion(self):
        self.accept_baseline()
        for stage, invoked, native, diff in (("search", False, 17, 0), ("runtime_preflight", False, None, 0),
                ("search", True, 17, 0), (None, True, None, None), ("comparison", True, None, 0), ("runtime_preflight", True, None, None)):
            observation = {**self.observation, "failed_stage": stage, "provider_invoked": invoked,
                           "native_exit": native, "comparison_exit": diff, "rows": None}
            with self.subTest(stage=stage, native=native), self.assertRaises(ValueError):
                outcomes.evaluate_attempt(self.previous, observation, self.evidence)
            self.assert_healthy_recovery()
        for stage, invoked in (("runtime_binding", False), ("incomplete", True)):
            receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                "failed_stage": stage, "provider_invoked": invoked, "native_exit": None,
                "comparison_exit": None, "rows": None}, self.evidence)
            self.assertEqual((receipt["runner_exit"], receipt["comparison_state"], receipt["cooldown_advanced"]),
                             (2, "unresolved", invoked))
            self.assertEqual(self.settle(receipt), self.previous)
            self.assert_healthy_recovery()

    def test_first_baseline_cannot_invent_a_successful_comparison(self):
        before = copy.deepcopy(self.previous)
        receipt = outcomes.evaluate_attempt(self.previous, {**self.observation, "comparison_exit": 0}, self.evidence)
        self.assertEqual((receipt["attempt_status"], receipt["failed_stage"], receipt["runner_exit"], receipt["comparison_state"]),
                         ("failed", "comparison", 2, "unresolved"))
        self.assertEqual(self.settle(receipt), before)
        self.assertEqual(self.previous, before)
        healthy = outcomes.evaluate_attempt(before, {**self.observation, "cycle_id": "healthy-first"}, self.evidence)
        self.assertEqual((healthy["runner_exit"], healthy["comparison_exit"], healthy["comparison_state"]),
                         (0, None, "baseline_established"))
        self.assertEqual(self.settle(healthy)["baseline"], self.ref("raw.json"))

    def test_terminal_receipt_requires_matching_event_and_final_pointer(self):
        receipt = outcomes.evaluate_attempt(self.previous, self.observation, self.evidence)
        self.assertEqual(receipt["comparison_state"], "baseline_established")
        self.assertEqual(outcomes.settle_attempt(self.previous, receipt, None, None, self.evidence), self.previous)
        accepted = self.settle(receipt)
        self.assertEqual(accepted["baseline"], self.ref("raw.json"))
        self.assertEqual(accepted["queries"]["q"]["items"], 1)

    def test_native_failure_preserves_baseline_and_healthy_recovery_uses_it(self):
        self.previous = self.settle(outcomes.evaluate_attempt(self.previous, self.observation, self.evidence))
        failed = {**self.observation, "cycle_id": "c2", "native_exit": 17,
                  "failed_stage": "search", "rows": None,
                  "evidence": {"stderr": self.ref("stderr.txt")}}
        receipt = outcomes.evaluate_attempt(self.previous, failed, self.evidence)
        self.assertEqual((receipt["runner_exit"], receipt["native_exit"], receipt["comparison_state"]),
                         (17, 17, "unresolved"))
        self.assertEqual(self.settle(receipt), self.previous)
        healthy = {**self.observation, "cycle_id": "c3", "comparison_exit": 0,
                   "evidence": {**self.observation["evidence"], "comparison": self.ref("diff.json")}}
        recovered = outcomes.evaluate_attempt(self.previous, healthy, self.evidence)
        self.assertEqual(recovered["comparison_state"], "compared")
        self.assertEqual(recovered["baseline_before"], self.previous["baseline"])

    def test_first_empty_and_repeated_empty_advance_only_coverage_history(self):
        capped = {**self.observation, "rows": {"q": {**self.row, "is_complete": False}}}
        self.evidence["cap.json"] = json.dumps(capped["rows"]).encode()
        capped["evidence"] = {"snapshot": self.ref("cap.json")}
        warning = self.settle(outcomes.evaluate_attempt(self.previous, capped, self.evidence))
        self.assertEqual(outcomes.evaluate_attempt(warning, self.observation, self.evidence)["comparison_state"], "baseline_established")
        empty = {**self.row, "item_count": 0, "issues": []}
        self.evidence["empty.json"] = json.dumps({"q": empty}).encode()
        for baseline in (None, self.ref("raw.json")):
            self.previous = {"baseline": baseline, "queries": {}}
            refs = {"snapshot": self.ref("empty.json")}
            if baseline:
                self.evidence["empty-diff.json"] = json.dumps({"status": "compared", "baseline": baseline, "current": refs["snapshot"]}).encode()
                refs["comparison"] = self.ref("empty-diff.json")
            for cycle in ("empty1", "empty2"):
                receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                    "cycle_id": cycle, "rows": {"q": empty}, "comparison_exit": 0 if baseline else None,
                    "evidence": refs}, self.evidence)
                self.assertEqual((receipt["attempt_status"], receipt["comparison_state"], receipt["runner_exit"]),
                                 ("accepted_with_coverage_warning", "suppressed", 2))
                self.previous = self.settle(receipt)
                self.assertEqual(self.previous["baseline"], baseline)
            self.assertEqual(self.previous["queries"]["q"]["empty_streak"], 2)

    def test_invalid_output_after_native_zero_is_failed_validation(self):
        bad = {**self.observation, "rows": {"q": {**self.row, "item_count": 9}}}
        receipt = outcomes.evaluate_attempt(self.previous, bad, self.evidence)
        self.assertEqual((receipt["failed_stage"], receipt["native_exit"], receipt["runner_exit"]),
                         ("validation", 0, 2))
        self.assertEqual(self.settle(receipt), self.previous)

    def test_comparison_failure_preserves_coverage_and_baseline(self):
        self.previous = self.settle(outcomes.evaluate_attempt(self.previous, self.observation, self.evidence))
        receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
            "cycle_id": "c2", "comparison_exit": 7,
            "evidence": {**self.observation["evidence"], "comparison": self.ref("diff.json")}}, self.evidence)
        self.assertEqual((receipt["failed_stage"], receipt["native_exit"], receipt["comparison_exit"],
                          receipt["runner_exit"]), ("comparison", 0, 7, 2))
        self.assertEqual(self.settle(receipt), self.previous)

    def test_runtime_stages_keep_no_launch_distinct_from_post_native_drift(self):
        for stage, invoked, native in (("runtime_preflight", False, None), ("runtime_binding", True, 0)):
            receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                "failed_stage": stage, "provider_invoked": invoked, "native_exit": native}, self.evidence)
            self.assertEqual((receipt["comparison_state"], receipt["failed_stage"], receipt["native_exit"]),
                             ("unresolved", stage, native))
            self.assertEqual(receipt["cooldown_advanced"], invoked)
            self.assertEqual(self.settle(receipt), self.previous)
        with self.assertRaises(ValueError):
            outcomes.evaluate_attempt(self.previous, {**self.observation,
                "failed_stage": "runtime_preflight"}, self.evidence)

    def test_private_malformed_or_corrupt_evidence_is_rejected(self):
        for path in ("/private/raw.json", "../raw.json", "a/../raw.json", "a//raw.json", "C:\\raw.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                outcomes.evaluate_attempt(self.previous, {**self.observation,
                    "evidence": {"snapshot": {"path": path, "sha256": "a" * 64}}}, self.evidence)
        for change in ({"launch_command": "synthetic"}, {"cycle_id": "../cycle"}):
            with self.assertRaises(ValueError):
                outcomes.evaluate_attempt(self.previous, {**self.observation, **change}, self.evidence)
        with self.assertRaises(ValueError):
            outcomes.evaluate_attempt(self.previous, self.observation, {**self.evidence, "raw.json": b"changed"})

    def test_native_zero_requires_bound_snapshot_and_comparison_evidence(self):
        for content in (b"invalid JSON", b"{}"):
            self.evidence["bad.json"] = content
            receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                "evidence": {"snapshot": self.ref("bad.json")}}, self.evidence)
            self.assertEqual((receipt["failed_stage"], receipt["runner_exit"]), ("validation", 2))
        self.previous = self.settle(outcomes.evaluate_attempt(self.previous, self.observation, self.evidence))
        for comparison in (None, self.ref("bad.json")):
            refs = {**self.observation["evidence"]}
            if comparison:
                refs["comparison"] = comparison
            receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                "comparison_exit": 0, "evidence": refs}, self.evidence)
            self.assertEqual((receipt["failed_stage"], receipt["runner_exit"]), ("comparison", 2))

    def test_incomplete_mismatched_stale_and_corrupt_cycles_do_not_accept(self):
        receipt = outcomes.evaluate_attempt(self.previous, self.observation, self.evidence)
        for event, pointer in ((None, {}), ({}, None)):
            self.assertEqual(outcomes.settle_attempt(self.previous, receipt, event, pointer, self.evidence), self.previous)
        with self.assertRaises(ValueError):
            outcomes.settle_attempt(self.previous, receipt, {"cycle_id": "other"}, {}, self.evidence)
        self.evidence["raw.json"] = b"drift"
        with self.assertRaises(ValueError):
            self.settle(receipt)
        incomplete = outcomes.evaluate_attempt(self.previous, {**self.observation,
            "failed_stage": "incomplete", "evidence": {}}, self.evidence)
        self.assertEqual(incomplete["attempt_status"], "incomplete")
        self.assertEqual(self.settle(incomplete), self.previous)

    def test_private_receipt_fields_and_stale_state_are_rejected(self):
        receipt = outcomes.evaluate_attempt(self.previous, self.observation, self.evidence)
        with self.assertRaises(ValueError):
            self.settle({**receipt, "diagnostics": "synthetic private field"})
        with self.assertRaises(ValueError):
            self.settle(receipt, {"baseline": None, "queries": {"other": {}}})
        with self.assertRaises(ValueError):
            outcomes.evaluate_attempt(self.previous, {**self.observation,
                "rows": {"q": {**self.row, "query_fingerprint": "/private/query"}}}, self.evidence)

    def test_changed_query_identity_cannot_compare_to_old_baseline(self):
        self.previous = self.settle(outcomes.evaluate_attempt(self.previous, self.observation, self.evidence))
        changed = {"q": {**self.row, "query_fingerprint": "query-b"}}
        self.evidence["changed.json"] = json.dumps(changed).encode()
        for cycle in ("changed1", "changed2"):
            receipt = outcomes.evaluate_attempt(self.previous, {**self.observation,
                "cycle_id": cycle, "rows": changed, "evidence": {"snapshot": self.ref("changed.json")}}, self.evidence)
            self.assertEqual(receipt["comparison_state"], "suppressed")
            self.previous = self.settle(receipt)
            self.assertEqual(self.previous["baseline"], self.ref("raw.json"))

    def test_failed_or_warning_receipt_cannot_smuggle_a_new_baseline(self):
        receipt = outcomes.evaluate_attempt(self.previous, {**self.observation, "failed_stage": "validation"}, self.evidence)
        receipt["candidate"]["baseline"] = self.ref("raw.json")
        with self.assertRaises(ValueError):
            self.settle(receipt)
        with self.assertRaises(ValueError):
            outcomes.evaluate_attempt({"baseline": None, "queries": {"q": {"last_nonempty_items": 1}}}, self.observation, self.evidence)


if __name__ == "__main__":
    unittest.main()
