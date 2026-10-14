#!/usr/bin/env python3
"""A08b1: SHA-bound, one-send publication of new-ticket blocker edges."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from githubkit import GitHub

from github_search_one_page import API_VERSION, credential
from issue_amend import OWNER, REPO, Refusal, publish, read, sha, snapshot, wire
from issue_create import manifest

REPOSITORY = f"{OWNER}/{REPO}"
HEX = re.compile(r"[0-9a-f]{64}\Z")
BLOCKERS = {
    "A01": (), "A02": ("A01",), "A03a": ("A04",),
    "A03b": ("A03a",), "A04": ("A02",),
    "A05a": ("A03b", "A04"), "A05b": ("A05a",),
    "A06": ("A05b",), "A07a": ("A04",), "A07b": ("A07a",),
    "A08a": ("A07b",), "A08b": ("A08a",), "A09": ("A01",),
    "A10": ("A09",), "A11": ("A10",),
    "A12a": ("A01", "A02", "A09"),
    "A12b": ("A06", "A08b", "A12a"),
}


def approved(manifest_file: Path, graph_file: Path,
             graph_sha: str) -> tuple[dict[str, dict], str]:
    data, manifest_sha = manifest(manifest_file)
    graph_source = read(graph_file)
    if not HEX.fullmatch(graph_sha) or sha(graph_source) != graph_sha:
        raise Refusal("graph SHA-256 mismatch")
    graph = json.loads(graph_source)
    if isinstance(graph, dict) and graph.get("schema") == "marketplace-edge-graph-v2":
        return approved_graph(graph, graph_file, manifest_file), manifest_sha
    if set(BLOCKERS) != {x["local_id"] for x in data["tickets"]}:
        raise Refusal("ticket set changed")
    for ticket in data["tickets"]:
        declared = ticket["body"].split("Blocked by: ", 1)
        if len(declared) != 2:
            raise Refusal("ticket blocker declaration missing")
        actual = declared[1].split(".", 1)[0]
        expected = ", ".join(BLOCKERS[ticket["local_id"]]) or "none"
        if actual != expected:
            raise Refusal("approved blocker map drifted")
    if (not isinstance(graph, dict) or graph.get("schema") != "a08b-graph-audit-v1"
            or graph.get("status") != "verified" or graph.get("repo") != REPOSITORY
            or graph.get("manifest_sha256") != manifest_sha or graph.get("parent_number") != 11
            or graph.get("child_count", 0) < 17 or not isinstance(graph.get("tickets"), list)):
        raise Refusal("unverified child graph")
    bindings = {x["local_id"]: x for x in graph["tickets"]}
    if (set(bindings) != set(BLOCKERS) or len(graph["tickets"]) != len(bindings)
            or any(set(x) != {"local_id", "intent_sha256", "issue_id", "issue_number"}
                   or type(x["issue_id"]) is not int or x["issue_id"] <= 0
                   or type(x["issue_number"]) is not int or x["issue_number"] <= 11
                   for x in graph["tickets"])
            or len({x["issue_id"] for x in graph["tickets"]}) != len(bindings)
            or len({x["issue_number"] for x in graph["tickets"]}) != len(bindings)):
        raise Refusal("invalid child bindings")
    return bindings, manifest_sha


def approved_graph(graph: dict, graph_file: Path, manifest_file: Path) -> dict[str, dict]:
    """Bind the exact union of creation manifests, including distinct spec parents."""
    if (set(graph) != {"schema", "status", "repo", "manifests", "tickets"}
            or graph["status"] != "verified" or graph["repo"] != REPOSITORY
            or not isinstance(graph["manifests"], list) or not graph["manifests"]
            or not isinstance(graph["tickets"], list)):
        raise Refusal("unverified dependency graph")
    declared, paths, parents = {}, set(), set()
    for ref in graph["manifests"]:
        if (not isinstance(ref, dict) or set(ref) != {"file", "sha256", "parent_number"}
                or not isinstance(ref["file"], str) or not ref["file"]
                or Path(ref["file"]).is_absolute() or ".." in Path(ref["file"]).parts):
            raise Refusal("invalid manifest reference")
        path = graph_file.parent / ref["file"]
        payload, digest = manifest(path)
        if (digest != ref["sha256"] or payload["parent_number"] != ref["parent_number"]
                or payload["parent_number"] is None or path.resolve() in paths):
            raise Refusal("manifest binding drifted")
        paths.add(path.resolve())
        parents.add(payload["parent_number"])
        for ticket in payload["tickets"]:
            if ticket["local_id"] in declared:
                raise Refusal("duplicate manifest local identity")
            declared[ticket["local_id"]] = digest
    if manifest_file.resolve() not in paths:
        raise Refusal("primary manifest absent from graph")
    bindings = {}
    for row in graph["tickets"]:
        if (not isinstance(row, dict)
                or set(row) != {"local_id", "manifest_sha256", "intent_sha256",
                                "issue_id", "issue_number", "blocked_by"}
                or not isinstance(row["local_id"], str) or row["local_id"] in bindings
                or declared.get(row["local_id"]) != row["manifest_sha256"]
                or not isinstance(row["intent_sha256"], str)
                or not HEX.fullmatch(row["intent_sha256"])
                or type(row["issue_id"]) is not int or row["issue_id"] <= 0
                or type(row["issue_number"]) is not int or row["issue_number"] <= 0
                or row["issue_number"] in parents or not isinstance(row["blocked_by"], list)
                or any(not isinstance(key, str) or key not in declared for key in row["blocked_by"])
                or len(set(row["blocked_by"])) != len(row["blocked_by"])):
            raise Refusal("invalid dependency bindings")
        bindings[row["local_id"]] = row
    if (set(bindings) != set(declared)
            or len({row["issue_id"] for row in bindings.values()}) != len(bindings)
            or len({row["issue_number"] for row in bindings.values()}) != len(bindings)):
        raise Refusal("missing or aliased dependency bindings")
    remaining, settled = set(bindings), set()
    while remaining:
        ready = {key for key in remaining if set(bindings[key]["blocked_by"]) <= settled}
        if not ready:
            raise Refusal("cyclic dependency graph")
        settled.update(ready)
        remaining.difference_update(ready)
    return bindings


def blockers(target: str, bindings: dict[str, dict]) -> list[str] | tuple[str, ...]:
    return bindings[target].get("blocked_by", BLOCKERS.get(target, ()))


def issue(client: GitHub, number: int, expected_id: int) -> dict:
    response = client.rest(API_VERSION).issues.get(OWNER, REPO, number)
    if response.status_code != 200:
        raise Refusal("issue GET failed")
    row = snapshot(response.raw_response.json(), number, completion=True)
    # Edge intents predate completion metadata; preserve their literal preimages.
    row.pop("state_reason")
    if row["id"] != expected_id:
        raise Refusal("issue identity drifted")
    return row


def blocked_by(client: GitHub, number: int) -> list[list[int]]:
    result = []
    for page in range(1, 4):
        response = client.rest(API_VERSION).issues.list_dependencies_blocked_by(
            OWNER, REPO, number, per_page=100, page=page)
        if response.status_code != 200:
            raise Refusal("blocked-by listing failed")
        rows = response.raw_response.json()
        if not isinstance(rows, list) or len(rows) > 100:
            raise Refusal("invalid blocked-by page")
        for row in rows:
            if (not isinstance(row, dict) or type(row.get("id")) is not int
                    or type(row.get("number")) is not int):
                raise Refusal("invalid dependency identity")
            result.append([row["id"], row["number"]])
        if len(rows) < 100:
            if len({tuple(row) for row in result}) != len(result):
                raise Refusal("duplicate dependency")
            return sorted(result)
    raise Refusal("blocked-by listing incomplete")


def state(client: GitHub, target_local: str, bindings: dict[str, dict]) -> dict:
    target = bindings[target_local]
    current = issue(client, target["issue_number"], target["issue_id"])
    dependencies = blocked_by(client, target["issue_number"])
    return {"issue": current, "blocked_by": dependencies}


def path_for(journal: Path, target: str, blocker: str,
             bindings: dict[str, dict] | None = None) -> Path:
    if (not isinstance(target, str) or not isinstance(blocker, str)
            or target not in (bindings if bindings is not None else BLOCKERS)
            or blocker not in (blockers(target, bindings) if bindings is not None else BLOCKERS[target])):
        raise Refusal("unapproved blocker edge")
    return journal / f"{target}-by-{blocker}.intent.json"


def attempt_path(path: Path) -> Path:
    return path.with_name(path.name + ".attempt.json")


def intent(path: Path, digest: str, manifest_file: Path,
           graph_file: Path, graph_sha: str) -> tuple[dict, dict[str, dict]]:
    bindings, manifest_sha = approved(manifest_file, graph_file, graph_sha)
    source = read(path)
    if not HEX.fullmatch(digest) or sha(source) != digest:
        raise Refusal("intent SHA-256 mismatch")
    data = json.loads(source)
    if (not isinstance(data, dict)
            or set(data) != {"version", "manifest_sha256", "graph_sha256", "target", "blocker", "preimage"}
            or data["version"] != 1 or data["manifest_sha256"] != manifest_sha
            or data["graph_sha256"] != graph_sha
            or path != path_for(path.parent, data["target"], data["blocker"], bindings)):
        raise Refusal("intent source drifted")
    return data, bindings


def preview(client: GitHub, manifest_file: Path, graph_file: Path, graph_sha: str,
            journal: Path, target: str, blocker_local: str) -> str:
    bindings, manifest_sha = approved(manifest_file, graph_file, graph_sha)
    path = path_for(journal, target, blocker_local, bindings)
    if (path.exists() or path.is_symlink()
            or attempt_path(path).exists() or attempt_path(path).is_symlink()):
        raise Refusal("existing intent or attempt")
    if audit(client, bindings, complete=False) != "NEW_EDGES_VERIFIED":
        raise Refusal("unexpected existing dependency graph")
    before = state(client, target, bindings)
    blocker = bindings[blocker_local]
    issue(client, blocker["issue_number"], blocker["issue_id"])
    if [blocker["issue_id"], blocker["issue_number"]] in before["blocked_by"]:
        raise Refusal("edge already exists")
    encoded = wire({"version": 1, "manifest_sha256": manifest_sha,
                    "graph_sha256": graph_sha, "target": target,
                    "blocker": blocker_local, "preimage": before})
    publish(path, encoded)
    return sha(encoded)


def verify(client: GitHub, path: Path, digest: str, manifest_file: Path,
           graph_file: Path, graph_sha: str) -> str:
    data, bindings = intent(path, digest, manifest_file, graph_file, graph_sha)
    if json.loads(read(attempt_path(path))) != {"version": 1, "intent_sha256": digest}:
        raise Refusal("invalid attempt marker")
    current = state(client, data["target"], bindings)
    before = data["preimage"]
    if any(current["issue"][key] != before["issue"][key]
           for key in ("id", "number", "title", "body", "state")):
        return "UNRESOLVED"
    blocker = bindings[data["blocker"]]
    expected = [blocker["issue_id"], blocker["issue_number"]]
    return "EDGE_VERIFIED" if (all(row in current["blocked_by"] for row in before["blocked_by"] + [expected])
                              and audit(client, bindings, complete=False) == "NEW_EDGES_VERIFIED") else "UNRESOLVED"


def apply(client: GitHub, path: Path, digest: str, manifest_file: Path,
          graph_file: Path, graph_sha: str) -> str:
    args = (manifest_file, graph_file, graph_sha)
    data, bindings = intent(path, digest, *args)
    attempt = attempt_path(path)
    if attempt.exists() or attempt.is_symlink():
        raise Refusal("attempt already recorded; verify only")
    if audit(client, bindings, complete=False) != "NEW_EDGES_VERIFIED":
        raise Refusal("unexpected existing dependency graph")
    if state(client, data["target"], bindings) != data["preimage"]:
        raise Refusal("issue or dependency preimage drifted")
    blocker = bindings[data["blocker"]]
    issue(client, blocker["issue_number"], blocker["issue_id"])
    publish(attempt, wire({"version": 1, "intent_sha256": digest}))
    try:
        api = client.rest(API_VERSION).issues
        target_number = bindings[data["target"]]["issue_number"]
        response = api.add_blocked_by_dependency(
            OWNER, REPO, target_number, data={"issue_id": blocker["issue_id"]})
        if response.status_code not in (200, 201):
            return "UNRESOLVED"
    except Exception:
        return "UNRESOLVED"
    try:
        return verify(client, path, digest, *args)
    except Exception:
        return "UNRESOLVED"


def audit(client: GitHub, bindings: dict[str, dict], *, complete: bool = True) -> str:
    for target, binding in bindings.items():
        issue(client, binding["issue_number"], binding["issue_id"])
        observed = blocked_by(client, binding["issue_number"])
        expected = sorted([[bindings[key]["issue_id"], bindings[key]["issue_number"]]
                           for key in blockers(target, bindings)])
        if (observed != expected if complete else any(row not in expected for row in observed)):
            return "UNRESOLVED"
    return "NEW_EDGES_VERIFIED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preview", "apply", "verify", "audit"))
    parser.add_argument("--manifest-file", type=Path, required=True)
    parser.add_argument("--graph-file", type=Path, required=True)
    parser.add_argument("--graph-sha256", required=True)
    parser.add_argument("--journal-dir", type=Path)
    parser.add_argument("--target")
    parser.add_argument("--blocker")
    parser.add_argument("--intent-file", type=Path)
    parser.add_argument("--intent-sha256")
    args = parser.parse_args()
    try:
        common = (args.manifest_file, args.graph_file, args.graph_sha256)
        bindings, _ = approved(*common)
        if args.mode == "preview" and (args.journal_dir is None or args.target is None
                                       or args.blocker is None):
            raise Refusal("preview requires journal, target and blocker")
        if args.mode in ("apply", "verify") and (not args.intent_sha256 or not args.intent_file):
            raise Refusal("intent SHA-256 required")
        token, _ = credential()
        if not token:
            raise Refusal("GitHub credential unavailable")
        with GitHub(token, auto_retry=False, http_cache=False, follow_redirects=False,
                    trust_env=False, timeout=15) as client:
            if args.mode == "audit":
                result = audit(client, bindings)
                print(result)
                return 0 if result == "NEW_EDGES_VERIFIED" else 2
            if args.mode == "preview":
                result = preview(client, *common, args.journal_dir, args.target, args.blocker)
                print(result)
                return 0
            method = apply if args.mode == "apply" else verify
            result = method(client, args.intent_file, args.intent_sha256, *common)
            print(result)
            return 0 if result == "EDGE_VERIFIED" else 2
    except (Refusal, OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"UNRESOLVED: {type(error).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
