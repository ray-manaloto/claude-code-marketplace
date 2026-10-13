"""Offline coverage feedback for compatible GitHub search observations.

Development tooling only: no provider calls, credentials or mutable state.
"""

import argparse
import json
from pathlib import Path


def identity(item):
    if item.get("path"):
        return item["repo_name"] + ":" + item["path"]
    value = item.get("html_url")
    if not isinstance(value, str) or not value:
        raise ValueError("Result requires a canonical identity")
    return value


def metrics(rows, previous):
    """Return feedback; previous is this function's last accepted output.

    A changed fingerprint starts a distinct history. Recovery flags are coverage
    signals, never NEW/GONE decisions; compare to the last compatible nonempty
    snapshot separately before making content-change claims.
    """
    output = {}
    for sid, row in rows.items():
        fingerprint = row.get("query_fingerprint")
        if not isinstance(fingerprint, str) or not fingerprint:
            raise ValueError("Query fingerprint is required")
        if not isinstance(row.get("is_complete"), bool):
            raise ValueError("Native completeness must be explicit")
        if not isinstance(row.get("error_code"), str) or not row["error_code"]:
            raise ValueError("Native error status must be explicit")
        items = row.get("items", []) + row.get("issues", []) + row.get("discussions", [])
        count = row.get("item_count")
        if type(count) is not int or count != len(items):
            raise ValueError("Result count does not match observations")
        keys = sorted({identity(item) for item in items})
        prior = previous.get(sid, {})
        same = fingerprint == prior.get("fingerprint")
        ok = row["error_code"] == "NONE"
        last = prior.get("last_nonempty_items", prior.get("items", 0)) if same else 0
        if ok and keys:
            last = len(keys)
        empty = ok and not keys and last > 0
        output[sid] = {
            "fingerprint": fingerprint, "error_code": row["error_code"],
            "items": count, "total": row.get("total_count"),
            "complete": row["is_complete"] and ok and not empty,
            "native_complete": row["is_complete"], "identities": keys,
            "last_nonempty_items": last, "empty_regression": empty,
            "recovered_from_empty": bool(same and ok and keys and prior.get("empty_regression")),
            "capped_streak": (prior.get("capped_streak", 0) if same else 0) + 1 if ok and not row["is_complete"] else 0,
            "error_streak": (prior.get("error_streak", 0) if same else 0) + 1 if not ok else 0,
            "empty_streak": (prior.get("empty_streak", 0) if same else 0) + 1 if ok and not keys else 0,
            "unchanged_streak": prior.get("unchanged_streak", 0) + 1 if same and ok and not empty and keys == prior.get("identities") else 0,
        }
    return output


def promotion_blockers(feedback):
    """Check all queries, including ones unrelated to the candidate.

    Pagination caps and candidate-specific expectations need separate checks.
    """
    return [sid for sid, row in feedback.items()
            if row["error_code"] != "NONE" or row["empty_regression"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True, help="JSON map: search ID to native observation")
    parser.add_argument("--previous", type=Path, required=True, help="Prior replay output, or search ID to feedback map")
    args = parser.parse_args()
    try:
        previous = json.loads(args.previous.read_text())
        if "queries" in previous and "promotion_blockers" in previous:
            previous = previous["queries"]
        feedback = metrics(json.loads(args.current.read_text()), previous)
        blockers = promotion_blockers(feedback)
        print(json.dumps({"queries": feedback, "promotion_blockers": blockers}, indent=2))
        return 2 if blockers else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        parser.exit(2, f"Invalid replay input: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
