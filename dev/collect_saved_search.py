#!/usr/bin/env python3
"""A03a bounded GitHubKit collection; every attempted response stays in the receipt."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import signal
import sys
import time
from importlib.metadata import version

import httpx
from githubkit import GitHub

from github_search_one_page import credential, replay_response, search
from search_catalog import (ROOT, CatalogError, catalog, confined, digest,
                            inspect_runs, query_lock, record)
from search_compare import select_baseline
from search_publish import publish


@contextmanager
def wall_deadline(seconds: float):
    """Bound one synchronous SDK call even if a peer drip-feeds response bytes."""
    if signal.getitimer(signal.ITIMER_REAL)[0] > 0:
        raise RuntimeError("another process alarm is active")
    previous = signal.getsignal(signal.SIGALRM)

    def expired(_signum, _frame):
        raise TimeoutError("collection time budget expired")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def collect(client: GitHub, route: str, row: dict, *, clock=time.monotonic,
            pause=time.sleep, deadline: float | None = None) -> tuple[dict, dict]:
    """No full/verified-empty verdict until A03b's control gate."""
    if deadline is None:
        deadline = clock() + row["timeout_seconds"]
    attempts, items, seen, totals, reasons = [], [], set(), [], set()
    exhausted = False
    for page in range(1, row["max_pages"] + 1):
        for ordinal in (1, 2):
            remaining = deadline - clock()
            if remaining <= 0:
                reasons.add("time_limit")
                result = {"status": "error"}
                break
            with client.get_sync_client() as http_client:
                http_client.timeout = max(0.001, remaining)
            try:
                with wall_deadline(remaining):
                    raw, meta = search(client, route, row["query"], row["effective_query"],
                                       row["per_page"], page)
            except TimeoutError:
                raw = {"status": "unavailable"}
                meta = {"normalized": {"status": "error", "error_code": "TIME_LIMIT"}}
                reasons.add("time_limit")
            if clock() > deadline:
                reasons.add("time_limit")
            result = meta["normalized"]
            if result.get("error_code") == "TIME_LIMIT":
                reasons.add("time_limit")
            attempts.append({"page": page, "ordinal": ordinal, "raw": raw,
                             "http_status": meta.get("http_status"),
                             "result_status": result["status"],
                             "error_code": result.get("error_code")})
            if result["status"] != "error":
                break
            if result.get("error_code") == "PRIVATE_RESULT_REFUSED":
                reasons.add("private_result_refused")
                break
            status = meta.get("http_status")
            headers = raw.get("response_headers", {})
            if status in (403, 429):
                if headers.get("x-ratelimit-remaining") == "0":
                    reasons.add("primary_rate_limit")
                elif status == 429 or headers.get("retry-after"):
                    reasons.add("secondary_rate_limit")
                else:
                    reasons.add("http_error")
                break
            if status not in (500, 502, 503, 504) or ordinal == 2:
                reasons.add("http_error" if status is not None else "transport_error")
                break
            reasons.add("retried_transient_error")
            pause(min(0.25, max(0, deadline - clock())))
        else:
            raise AssertionError("bounded retry loop did not exit")
        if "time_limit" in reasons or result["status"] == "error":
            break
        totals.append(result["total_count"])
        if result["incomplete_results"]:
            reasons.add("api_incomplete")
        if result["total_count"] > 1000:
            reasons.add("api_cap")
        if len(set(totals)) > 1:
            reasons.add("total_drift")
        for item in result["items"]:
            identity = item["identity"]
            if identity in seen:
                reasons.add("duplicate_items")
                continue
            seen.add(identity)
            if len(items) == row["max_items"]:
                reasons.add("item_limit")
                break
            items.append(item)
        if len(items) >= row["max_items"]:
            if result["total_count"] <= len(items) and not result["incomplete_results"]:
                exhausted = True
            else:
                reasons.add("item_limit")
            break
        if result["returned_count"] == 0 and result["total_count"] > len(items):
            reasons.add("unexpected_empty_page")
            break
        if result["returned_count"] < row["per_page"] and result["total_count"] > len(items):
            reasons.add("unexpected_short_page")
            break
        if result["returned_count"] < row["per_page"] or result["total_count"] <= len(items):
            exhausted = True
            break
    else:
        if not exhausted:
            reasons.add("page_limit")
    status = ("error" if not items and ("time_limit" in reasons or
              any(a["result_status"] == "error" for a in attempts))
              else "partial" if items else "empty_unverified")
    normalized = {"status": status, "items": items, "returned_count": len(items),
                  "total_counts": totals, "attempt_count": len(attempts),
                  "pages_succeeded": len(totals), "complete_candidate": exhausted and not reasons,
                  "reasons": sorted(reasons), "control_status": "not_run"}
    return {"format": "githubkit-http-attempts-v1", "attempts": attempts}, {
        "query": row["query"], "effective_query": row["effective_query"],
        "credential_route": route, "sdk": "githubkit", "sdk_version": version("githubkit"),
        "normalized": normalized}


def fixture_transport(payload: bytes, row: dict) -> tuple[httpx.MockTransport, list, list, list]:
    value = json.loads(payload)
    responses = (value.get("responses") if isinstance(value, dict)
                 and value.get("format") == "githubkit-http-sequence-v1" else [value])
    if not isinstance(responses, list) or not 1 <= len(responses) <= 2 * row["max_pages"]:
        raise CatalogError("invalid bounded response sequence")
    decoded = []
    allowed_queries = {row["effective_query"]}
    allowed_queries.update(f"{control['query']} repo:{row['repo']}"
                           for control in row["control"])
    for envelope in responses:
        if not isinstance(envelope, dict) or not isinstance(envelope.get("request"), dict):
            raise CatalogError("invalid response envelope")
        page = envelope["request"].get("page")
        query = envelope["request"].get("query")
        if type(page) is not int or not 1 <= page <= row["max_pages"]:
            raise CatalogError("invalid fixture page")
        if not isinstance(query, str) or query not in allowed_queries:
            raise CatalogError("invalid fixture query")
        decoded.append((query, page, *replay_response(json.dumps(envelope).encode(),
                        query, row["per_page"], page)))
    consumed: list[int] = []
    exhausted: list[bool] = []

    def reply(request: httpx.Request) -> httpx.Response:
        index = len(consumed)
        if index == len(decoded):
            exhausted.append(True)
            raise RuntimeError("offline response sequence exhausted")
        query, page, status, headers, body = decoded[index]
        if (request.method != "GET" or request.url.path != "/search/code"
                or request.url.params.get("q") != query
                or request.url.params.get("page") != str(page)
                or request.url.params.get("per_page") != str(row["per_page"])):
            raise RuntimeError("offline request differs from response envelope")
        consumed.append(page)
        return httpx.Response(status, headers=headers, content=body)

    return httpx.MockTransport(reply), consumed, decoded, exhausted


def run_one(mode: str, output: Path, row: dict, catalog_hash: str,
            fixture: Path | None) -> tuple[dict, int]:
    with query_lock(output, row["id"], wait_seconds=row["timeout_seconds"] + 5):
        snapshot = inspect_runs(output, row["id"], capture_published=True)
        prior, reason = select_baseline(output, row, snapshot)
        fixture_hash = None
        if mode == "offline":
            payload = confined(fixture).read_bytes()
            fixture_hash = digest(payload)
            transport, consumed, decoded, exhausted = fixture_transport(payload, row)
            client = GitHub("fixture", transport=transport, auto_retry=False,
                            http_cache=False, follow_redirects=False, trust_env=False,
                            timeout=row["timeout_seconds"])
            route = "fixture"
        else:
            token, route = credential()
            if not token:
                raise CatalogError("GitHub credential route absent")
            client = GitHub(token, auto_retry=False, http_cache=False,
                            follow_redirects=False, timeout=row["timeout_seconds"])
        with client:
            deadline = time.monotonic() + row["timeout_seconds"]
            raw, metadata = collect(client, route, row, pause=(lambda _: None)
                                    if mode == "offline" else time.sleep,
                                    deadline=deadline)
            from control_saved_search import evaluate
            raw, metadata = evaluate(client, route, row, raw, metadata,
                                     deadline=deadline, wall_deadline=wall_deadline)
        if mode == "offline":
            if exhausted:
                raise CatalogError("offline response sequence exhausted")
            if len(consumed) != len(decoded):
                raise CatalogError("offline response sequence has unused envelopes")
        target = record(output, row, catalog_hash, raw, metadata, fixture_hash)
        result = {"id": row["id"], "receipt": str(target),
                  "status": metadata["normalized"]["status"],
                  "prior": {key: value for key, value in snapshot.items()
                            if key != "published"}, "credential_route": route}
        try:
            refreshed, refreshed_reason = select_baseline(output, row, snapshot)
            if refreshed != prior or refreshed_reason != reason:
                raise CatalogError("baseline changed during collection")
            comparison_path, comparison = publish(output, row, target, prior, reason)
        except (CatalogError, OSError, ValueError) as error:
            result["comparison"] = {"status": "unresolved", "reason": str(error)}
            return result, 2
        result["comparison"] = comparison
        result["comparison_receipt"] = str(comparison_path)
        return result, 2 if result["status"] == "error" else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("offline", "live"))
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--id")
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--catalog", type=Path, default=ROOT / "dev/saved-searches.toml")
    parser.add_argument("--fixture", type=Path,
                        default=ROOT / "dev/fixtures/github-code-search-empty.json")
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/saved-searches")
    args = parser.parse_args()
    try:
        output = confined(args.output)
        rows, catalog_hash = catalog(args.catalog)
        if args.all:
            selected = rows
            if args.mode == "offline" and args.fixture_dir is None:
                raise CatalogError("offline --all requires --fixture-dir")
        else:
            selected = [row for row in rows if row["id"] == args.id]
            if not selected:
                raise CatalogError("selected ID absent from catalog")
            if args.fixture_dir is not None:
                raise CatalogError("--fixture-dir requires --all")
        fixtures = {}
        if args.mode == "offline":
            for row in selected:
                path = (args.fixture_dir / f"{row['id']}.json" if args.all
                        else args.fixture)
                fixtures[row["id"]] = confined(path)
                if not fixtures[row["id"]].is_file():
                    raise CatalogError("offline fixture unavailable")
        results = []
        status = 0
        for row in selected:
            try:
                result, code = run_one(args.mode, output, row, catalog_hash,
                                       fixtures.get(row["id"]))
            except (CatalogError, OSError, RuntimeError, ValueError) as error:
                result, code = {"id": row["id"], "comparison": {
                    "status": "unresolved", "reason": str(error)}}, 2
            results.append(result)
            status = max(status, code)
        print(json.dumps({"results": results, "status": "unresolved" if status else "recorded"}
                         if args.all else results[0], sort_keys=True))
        return status
    except (CatalogError, OSError, RuntimeError, ValueError) as error:
        print(f"collection input refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
