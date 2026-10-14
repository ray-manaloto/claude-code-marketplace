"""Pure sanitized outcome contract; callers own launch and durable storage.

Write the receipt, then its cycle event, then the final pointer. A receipt alone
never accepts state. Evidence is a mapping of relative names to retained bytes.
"""
import copy
import hashlib
import json
import re

from research_feedback import metrics


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sanitized(value):
    if isinstance(value, dict):
        if set(value) & {"launch_command", "credentials", "diagnostics", "interpreter", "token"}:
            raise ValueError("Private fields are forbidden")
        for key, item in value.items():
            sanitized(key)
            sanitized(item)
    elif isinstance(value, list):
        for item in value:
            sanitized(item)
    elif isinstance(value, str) and (value.startswith(("/", "~")) or "\\" in value or any(ord(c) < 32 for c in value)):
        raise ValueError("Private paths or diagnostic text are forbidden")


def validate_refs(refs, evidence):
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
            raise ValueError("Malformed evidence reference")
        path = ref["path"]
        if not isinstance(path, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", path) or any(part in (".", "..") for part in path.split("/")):
            raise ValueError("Evidence must be confined relative names")
        if not isinstance(ref["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]) or path not in evidence or type(evidence[path]) is not bytes or hashlib.sha256(evidence[path]).hexdigest() != ref["sha256"]:
            raise ValueError("Evidence digest mismatch")


def fields(value, allowed, required=()):
    if not isinstance(value, dict) or set(value) - set(allowed) or not set(required) <= set(value):
        raise ValueError("Malformed sanitized fields")


def typed(value, kind):
    if type(value) is not kind:
        raise ValueError("Malformed sanitized type")
    if kind is str and not value or kind is int and value < 0:
        raise ValueError("Malformed sanitized value")


def rows_schema(rows):
    typed(rows, dict)
    for sid, row in rows.items():
        typed(sid, str)
        required = {"query_fingerprint", "error_code", "is_complete", "item_count"}
        fields(row, required | {"total_count", "items", "issues", "discussions"}, required)
        for key, kind in (("query_fingerprint", str), ("error_code", str), ("is_complete", bool), ("item_count", int)):
            typed(row[key], kind)
        if row.get("total_count") is not None:
            typed(row["total_count"], int)
        for key in ("items", "issues", "discussions"):
            typed(row.get(key, []), list)
            for item in row.get(key, []):
                fields(item, {"html_url", "repo_name", "path"})
                for value in item.values():
                    typed(value, str)
                if not (item.get("path") and item.get("repo_name") or item.get("html_url")):
                    raise ValueError("Result identity is required")


def state_schema(state):
    fields(state, {"baseline", "queries"}, {"baseline", "queries"})
    typed(state["queries"], dict)
    kinds = {"fingerprint": str, "error_code": str, "items": int, "complete": bool,
             "native_complete": bool, "identities": list, "last_nonempty_items": int,
             "empty_regression": bool, "recovered_from_empty": bool, "capped_streak": int,
             "error_streak": int, "empty_streak": int, "unchanged_streak": int}
    for sid, row in state["queries"].items():
        typed(sid, str)
        fields(row, set(kinds) | {"total"}, set(kinds) | {"total"})
        for key, kind in kinds.items():
            typed(row[key], kind)
        if row["total"] is not None:
            typed(row["total"], int)
        for identity in row["identities"]:
            typed(identity, str)


def evaluate_attempt(previous, observation, evidence):
    state_schema(previous)
    fields(observation, {"cycle_id", "provider_invoked", "native_exit", "comparison_exit", "failed_stage", "rows", "evidence"}, {"cycle_id", "provider_invoked", "native_exit", "comparison_exit", "failed_stage", "rows", "evidence"})
    typed(observation["cycle_id"], str)
    fields(observation["evidence"], {"snapshot", "comparison", "stdout", "stderr"})
    typed(evidence, dict)
    for name, content in evidence.items():
        typed(content, bytes)
        validate_refs([{"path": name, "sha256": hashlib.sha256(content).hexdigest()}], evidence)
    if observation["rows"] is not None:
        rows_schema(observation["rows"])
    sanitized(previous)
    sanitized(observation)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", observation["cycle_id"]):
        raise ValueError("Invalid sanitized observation")
    if type(observation["provider_invoked"]) is not bool or any(value is not None and type(value) is not int for value in (observation["native_exit"], observation["comparison_exit"])):
        raise ValueError("Explicit stage outcomes required")
    if observation["failed_stage"] not in (None, "search", "validation", "comparison", "runtime_preflight", "runtime_binding", "incomplete"):
        raise ValueError("Unknown stage")
    if observation["failed_stage"] == "runtime_preflight" and (observation["provider_invoked"] or observation["native_exit"] is not None):
        raise ValueError("Preflight failure cannot claim native invocation")
    validate_refs(observation["evidence"].values(), evidence)
    if previous["baseline"] is not None:
        validate_refs([previous["baseline"]], evidence)
        try:
            rows_schema(json.loads(evidence[previous["baseline"]["path"]]))
        except (ValueError, TypeError, KeyError):
            raise ValueError("Malformed accepted baseline") from None
    if previous["baseline"] is None and any(row.get("last_nonempty_items", 0) for row in previous["queries"].values()) and all(row.get("complete") is not False for row in previous["queries"].values()):
        raise ValueError("Missing baseline cannot initialize accepted history")
    candidate = copy.deepcopy(previous)
    stage = observation["failed_stage"]
    native, compared = observation["native_exit"], observation["comparison_exit"]
    stage = stage or ("search" if native not in (None, 0) else "comparison" if compared not in (None, 0) else None)
    invoked = observation["provider_invoked"]
    if not invoked and (native is not None or compared is not None or stage not in ("runtime_preflight", "runtime_binding", "incomplete")):
        raise ValueError("Outcomes cannot precede invocation")
    if invoked and stage == "runtime_preflight" or native != 0 and compared is not None:
        raise ValueError("Comparison requires successful native invocation")
    if invoked and native is None and stage not in ("runtime_binding", "incomplete", "search"):
        raise ValueError("Unknown completion requires explicit unresolved stage")
    if stage in ("validation", "comparison") and native != 0 or stage == "search" and native == 0:
        raise ValueError("Stage contradicts native outcome")
    if not stage and previous["baseline"] is None and (compared is not None or "comparison" in observation["evidence"]):
        stage = "comparison"
    state = "unresolved" if stage else "compared" if previous["baseline"] else "baseline_established"
    reason = None
    if not stage and (native != 0 or not observation["provider_invoked"]):
        stage, state = "validation", "unresolved"
    if not stage:
        try:
            snapshot = observation["evidence"]["snapshot"]
            if json.loads(evidence[snapshot["path"]]) != observation["rows"]:
                raise ValueError("Snapshot does not bind observations")
            normalized = {sid: {**row, "is_complete": row["is_complete"] and (row.get("total_count") is None or row["item_count"] >= row["total_count"])} for sid, row in observation["rows"].items()}
            queries = metrics(normalized, previous["queries"])
            for sid, row in queries.items():
                row["native_complete"] = observation["rows"][sid]["is_complete"]
            if any(row["error_code"] != "NONE" for row in queries.values()):
                raise ValueError("Native zero cannot certify errored observations")
        except (ValueError, TypeError, KeyError, AttributeError):
            stage, state, queries = "validation", "unresolved", None
        if queries is not None and (not queries or any(not row["complete"] or not row["identities"] for row in queries.values())):
            state, reason = "suppressed", "unverified_coverage"
        if queries is not None:
            candidate.update(queries=queries)
        if not stage and previous["baseline"] is not None:
            baseline_rows = json.loads(evidence[previous["baseline"]["path"]])
            if {sid: row["query_fingerprint"] for sid, row in baseline_rows.items()} != {sid: row["fingerprint"] for sid, row in queries.items()}:
                state, reason = "suppressed", "incompatible_query_identity"
        if not stage and previous["baseline"] is not None and reason != "incompatible_query_identity":
            try:
                ref = observation["evidence"]["comparison"]
                expected = {"status": "compared", "baseline": previous["baseline"], "current": snapshot}
                if compared != 0 or json.loads(evidence[ref["path"]]) != expected:
                    raise ValueError("Comparison does not bind both snapshots")
            except (ValueError, KeyError, TypeError):
                stage, state, reason, candidate = "comparison", "unresolved", None, copy.deepcopy(previous)
        if not stage and state != "suppressed":
            candidate["baseline"] = observation["evidence"]["snapshot"]
    return {"cycle_id": observation["cycle_id"], "comparison_state": state,
            "attempt_status": "incomplete" if stage == "incomplete" else "failed" if stage else "accepted_with_coverage_warning" if reason else "accepted",
            "runner_exit": native if stage in ("search", "runtime_binding") and native not in (None, 0) else 2 if stage or reason else 0,
            "failed_stage": stage, "native_exit": native, "comparison_exit": compared,
            "provider_invoked": observation["provider_invoked"],
            "cooldown_advanced": observation["provider_invoked"], "coverage_reason": reason,
            "evidence": copy.deepcopy(observation["evidence"]),
            "baseline_before": copy.deepcopy(previous["baseline"]),
            "previous_sha256": digest(previous), "candidate": candidate}


def settle_attempt(previous, receipt, event, pointer, evidence):
    state_schema(previous)
    receipt_fields = {"cycle_id", "comparison_state", "attempt_status", "runner_exit", "failed_stage", "native_exit", "comparison_exit", "provider_invoked", "cooldown_advanced", "coverage_reason", "evidence", "baseline_before", "previous_sha256", "candidate"}
    fields(receipt, receipt_fields, receipt_fields)
    state_schema(receipt["candidate"])
    fields(receipt["evidence"], {"snapshot", "comparison", "stdout", "stderr"})
    typed(evidence, dict)
    sanitized(receipt)
    if event is None or pointer is None:
        return copy.deepcopy(previous)
    validate_refs(receipt["evidence"].values(), evidence)
    if receipt["candidate"]["baseline"] is not None:
        validate_refs([receipt["candidate"]["baseline"]], evidence)
    expected = {"cycle_id": receipt["cycle_id"], "receipt_sha256": digest(receipt)}
    if event != expected or pointer != {**expected, "event_sha256": digest(event)}:
        raise ValueError("Incomplete cycle binding")
    if receipt["previous_sha256"] != digest(previous):
        raise ValueError("Stale acceptance state")
    observed = {key: receipt[key] for key in ("cycle_id", "provider_invoked", "native_exit", "comparison_exit", "failed_stage", "evidence")}
    observed["rows"] = json.loads(evidence[receipt["evidence"]["snapshot"]["path"]]) if receipt["failed_stage"] is None else None
    if evaluate_attempt(previous, observed, evidence) != receipt:
        raise ValueError("Receipt contradicts verified outcomes")
    return copy.deepcopy(receipt["candidate"])
