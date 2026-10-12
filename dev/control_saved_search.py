#!/usr/bin/env python3
"""A03b same-scope controls and conservative collection verdicts."""

from __future__ import annotations

import time

from githubkit import GitHub

from github_search_one_page import search


def evaluate(client: GitHub, route: str, row: dict, raw: dict, metadata: dict,
             *, deadline: float, wall_deadline, clock=time.monotonic) -> tuple[dict, dict]:
    """Control requests share the collection deadline and bounded send budget."""
    result = metadata["normalized"]
    raw["format"] = "githubkit-http-attempts-v2"
    raw["controls"] = []
    budget = 2 * row["max_pages"]
    used = len(raw["attempts"])
    result["request_budget"] = budget
    result["requests_used"] = used
    result["collection_complete_candidate"] = result["complete_candidate"]
    if not result["complete_candidate"]:
        result["control_status"] = "not_run"
        result["control_reason"] = ("main_error" if result["status"] == "error"
                                    else "main_incomplete")
        return raw, metadata

    outcomes = []
    for definition in row["control"]:
        query = definition["query"]
        effective = f"{query} repo:{row['repo']}"
        expected = definition["expected_min"]
        control = {"query": query, "effective_query": effective,
                   "expected_min": expected, "attempts": [],
                   "status": "not_run", "reason": "request_budget",
                   "distinct_count": 0}
        seen: set[str] = set()
        for page in range(1, row["max_pages"] + 1):
            if used >= budget or clock() >= deadline:
                control["reason"] = ("request_budget" if used >= budget else "time_limit")
                if control["attempts"]:
                    control["status"] = "failed"
                break
            remaining = deadline - clock()
            if remaining <= 0:
                control["reason"] = "time_limit"
                if control["attempts"]:
                    control["status"] = "failed"
                break
            with client.get_sync_client() as http_client:
                http_client.timeout = max(0.001, remaining)
            try:
                with wall_deadline(remaining):
                    response, meta = search(client, route, query, effective,
                                            row["per_page"], page)
            except TimeoutError:
                response = {"status": "unavailable"}
                meta = {"normalized": {"status": "error", "error_code": "TIME_LIMIT"}}
            used += 1
            normalized = meta["normalized"]
            control["attempts"].append({
                "page": page, "raw": response, "http_status": meta.get("http_status"),
                "result_status": normalized["status"],
                "error_code": normalized.get("error_code"),
            })
            if clock() >= deadline:
                control["status"] = "failed"
                control["reason"] = "time_limit"
                break
            if normalized["status"] == "error":
                control["status"] = "failed"
                control["reason"] = normalized.get("error_code", "http_error")
                break
            if normalized["incomplete_results"]:
                control["status"] = "failed"
                control["reason"] = "api_incomplete"
                break
            for item in normalized["items"]:
                seen.add(item["identity"])
                if len(seen) >= expected:
                    break
            control["distinct_count"] = len(seen)
            if len(seen) >= expected:
                control["status"] = "passed"
                control["reason"] = "expected_min_met"
                break
            if (normalized["returned_count"] == 0
                    or normalized["returned_count"] < row["per_page"]
                    or normalized["total_count"] <= len(seen)):
                control["status"] = "failed"
                control["reason"] = "expected_min_not_met"
                break
        else:
            control["status"] = "failed"
            control["reason"] = "page_limit"
        raw["controls"].append(control)
        outcomes.append(control["status"])

    result["requests_used"] = used
    result["control_status"] = ("passed" if all(s == "passed" for s in outcomes)
                                else "failed" if "failed" in outcomes else "not_run")
    result["control_reason"] = ("all_expected_min_met" if result["control_status"] == "passed"
                                else "control_failed" if result["control_status"] == "failed"
                                else "control_budget_exhausted")
    result["complete_candidate"] = result["control_status"] == "passed"
    if result["control_status"] == "passed":
        result["status"] = "complete" if result["items"] else "empty_verified"
    else:
        result["reasons"] = sorted(set(result["reasons"]) | {result["control_reason"]})
    return raw, metadata
