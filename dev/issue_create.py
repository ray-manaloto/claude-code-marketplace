#!/usr/bin/env python3
"""Create one manifest-approved issue with a durable, single-POST intent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from githubkit import GitHub
from githubkit.exception import RequestFailed

from github_search_one_page import API_VERSION, credential
from issue_amend import OWNER, REPO, Refusal, labels, publish, read, refused, scan, sha, wire

REPOSITORY = f"{OWNER}/{REPO}"
LOCAL_ID = re.compile(r"A\d\d(?:[ab])?\Z")
GENERIC_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
PAGE_SIZE, MAX_REPO_PAGES = 100, 20


def manifest(path: Path) -> tuple[dict, str]:
    source = read(path)
    data = json.loads(source)
    if (not isinstance(data, dict) or set(data) != {"version", "repo", "parent_number", "tickets"}
            or type(data["version"]) is not int or data["version"] not in (1, 2)
            or data["repo"] != REPOSITORY
            or data["parent_number"] is not None and (
                type(data["parent_number"]) is not int or data["parent_number"] <= 0)
            or data["version"] == 1 and data["parent_number"] != 11
            or not isinstance(data["tickets"], list) or not 1 <= len(data["tickets"]) <= 50):
        raise Refusal("invalid ticket manifest")
    seen = set()
    for ticket in data["tickets"]:
        if (not isinstance(ticket, dict) or set(ticket) != {"local_id", "title", "body", "body_sha256", "labels"}
                or not isinstance(ticket["local_id"], str)
                or not (LOCAL_ID if data["version"] == 1 else GENERIC_ID).fullmatch(ticket["local_id"])
                or ticket["local_id"] in seen or not isinstance(ticket["title"], str)
                or not ticket["title"].strip() or not isinstance(ticket["body"], str)
                or not ticket["body"].strip() or sha(ticket["body"].encode()) != ticket["body_sha256"]
                or labels(ticket["labels"]) != ticket["labels"]
                or "ready-for-agent" in ticket["labels"] or "ready-for-human" in ticket["labels"]
                or "<!-- marketplace-ticket:" in ticket["body"]):
            raise Refusal("invalid or unapproved ticket payload")
        seen.add(ticket["local_id"])
    return data, sha(source)


def full_body(ticket: dict) -> str:
    return ticket["body"].rstrip("\n") + "\n\n" + (
        f"<!-- marketplace-ticket:{ticket['local_id']}:{ticket['body_sha256']} -->")


def outbound(ticket: dict) -> dict:
    payload = {"title": ticket["title"], "body": full_body(ticket), "labels": ticket["labels"]}
    scan(ticket["local_id"], payload)  # R-174 (D171): D113 fix to existing Python; scans before any request
    return payload


def issue(raw: object) -> dict | None:
    if not isinstance(raw, dict):
        raise Refusal("issue listing contains invalid issue")
    if "pull_request" in raw:
        return None
    try:
        selected = {key: raw[key] for key in ("id", "number", "title", "body", "state", "updated_at")}
        selected["labels"] = labels([entry["name"] for entry in raw["labels"]])
    except (KeyError, TypeError) as error:
        raise Refusal("incomplete issue listing") from error
    if (type(selected["id"]) is not int or selected["id"] <= 0
            or type(selected["number"]) is not int or selected["number"] <= 0
            or not isinstance(selected["title"], str)
            or selected["body"] is not None and not isinstance(selected["body"], str)
            or selected["state"] not in ("open", "closed")
            or not isinstance(selected["updated_at"], str)):
        raise Refusal("invalid issue identity")
    return selected


def pages(client: GitHub, parent: int | None) -> list[dict]:
    result = []
    limit = 2 if parent is not None else MAX_REPO_PAGES
    for page in range(1, limit + 1):
        api = client.rest(API_VERSION).issues
        response = (api.list_sub_issues(OWNER, REPO, parent, per_page=PAGE_SIZE, page=page)
                    if parent is not None else
                    api.list_for_repo(OWNER, REPO, state="all", per_page=PAGE_SIZE, page=page))
        if response.status_code != 200:
            raise Refusal("issue listing failed")
        raw = response.raw_response.json()
        if not isinstance(raw, list) or len(raw) > PAGE_SIZE:
            raise Refusal("invalid issue listing page")
        result.extend(parsed for row in raw if (parsed := issue(row)) is not None)
        if len(raw) < PAGE_SIZE:
            if len({row["id"] for row in result}) != len(result):
                raise Refusal("duplicate issue in listing")
            return result
    raise Refusal("issue listing incomplete at page limit")


def parent_issue(client: GitHub, number: int) -> dict:
    response = client.rest(API_VERSION).issues.get(OWNER, REPO, number)
    if response.status_code != 200:
        raise Refusal("parent GET failed")
    row = issue(response.raw_response.json())
    if row is None or row["number"] != number or row["state"] != "open":
        raise Refusal("parent identity or state changed")
    return row


def inventory(client: GitHub, parent_number: int | None) -> dict:
    parent = parent_issue(client, parent_number) if parent_number is not None else None
    repository = pages(client, None)
    children = pages(client, parent_number) if parent is not None else []
    if len(children) > 100 or parent is not None and any(row["id"] == parent["id"] for row in children):
        raise Refusal("parent at native 100-child limit or invalid listing")
    return {"parent": parent, "repository": repository, "children": children}


def matches(rows: list[dict], ticket: dict) -> list[dict]:
    tag = f"<!-- marketplace-ticket:{ticket['local_id']}:"
    return [row for row in rows if tag in (row["body"] or "")]


def intent_path(journal: Path, local_id: str) -> Path:
    if not GENERIC_ID.fullmatch(local_id):
        raise Refusal("invalid local ID")
    return journal / f"{local_id}.intent.json"


def attempt_path(path: Path) -> Path:
    return path.with_name(path.name + ".attempt.json")


def binding_path(path: Path) -> Path:
    return path.with_name(path.name + ".binding.json")


def operation(data: dict) -> str:
    return "POST issue" if data["parent_number"] is None else "POST issue with parent_issue_id"


def parent_absent(client: GitHub, number: int) -> bool:
    try:
        return client.rest(API_VERSION).issues.get_parent(OWNER, REPO, number).status_code == 404
    except RequestFailed as error:
        return error.response.status_code == 404
    except Exception:
        return False


def preview(client: GitHub, manifest_file: Path, local_id: str, journal: Path) -> str:
    data, manifest_sha = manifest(manifest_file)
    ticket = next((x for x in data["tickets"] if x["local_id"] == local_id), None)
    if ticket is None:
        raise Refusal("local ID absent from manifest")
    outbound(ticket)
    path = intent_path(journal, local_id)
    if path.exists() or path.is_symlink() or attempt_path(path).exists() or binding_path(path).exists():
        raise Refusal("local ID already has a publication record")
    before = inventory(client, data["parent_number"])
    if len(before["children"]) >= 100:
        raise Refusal("parent at native 100-child limit")
    if matches(before["repository"], ticket) or matches(before["children"], ticket):
        raise Refusal("local ID already appears in GitHub inventory")
    payload = {"version": data["version"], "repo": REPOSITORY, "manifest_sha256": manifest_sha,
               "parent_number": data["parent_number"], "ticket": ticket, "preimage": before}
    encoded = wire(payload)
    publish(path, encoded)
    return sha(encoded)


def load_intent(path: Path, digest: str, manifest_file: Path) -> dict:
    source = read(path)
    if not re.fullmatch(r"[0-9a-f]{64}", digest) or sha(source) != digest:
        raise Refusal("intent SHA-256 mismatch")
    data, actual_manifest_sha = manifest(manifest_file)
    intent = json.loads(source)
    if (not isinstance(intent, dict) or set(intent) != {"version", "repo", "manifest_sha256", "parent_number", "ticket", "preimage"}
            or type(intent["version"]) is not int or intent["version"] != data["version"]
            or intent["repo"] != REPOSITORY
            or intent["manifest_sha256"] != actual_manifest_sha
            or intent["parent_number"] != data["parent_number"]
            or intent["ticket"] not in data["tickets"]
            or path != intent_path(path.parent, intent["ticket"]["local_id"])):
        raise Refusal("intent or approved manifest drifted")
    return intent


def verify(client: GitHub, path: Path, digest: str, manifest_file: Path) -> str:
    data = load_intent(path, digest, manifest_file)
    if json.loads(read(attempt_path(path))) != {"version": 1, "intent_sha256": digest, "operation": operation(data)}:
        raise Refusal("invalid attempt marker")
    ticket = data["ticket"]
    current = inventory(client, data["parent_number"])
    found = matches(current["repository"], ticket)
    if len(found) != 1:
        return "UNRESOLVED"
    child = found[0]
    if (child["body"] != full_body(ticket) or child["title"] != ticket["title"]
            or child["labels"] != ticket["labels"] or child["state"] != "open"
            or data["parent_number"] is None and not parent_absent(client, child["number"])
            or data["parent_number"] is not None and (
                current["parent"]["id"] != data["preimage"]["parent"]["id"]
                or [(x["id"], x["number"]) for x in current["children"]].count((child["id"], child["number"])) != 1)):
        return "UNRESOLVED"
    binding = {"version": 1, "intent_sha256": digest, "local_id": ticket["local_id"],
               "parent_number": data["parent_number"], "issue_id": child["id"], "issue_number": child["number"]}
    target = binding_path(path)
    if target.exists() or target.is_symlink():
        if json.loads(read(target)) != binding:
            raise Refusal("existing binding conflicts with verified issue")
    else:
        publish(target, wire(binding))
    return "VERIFIED"


def apply(client: GitHub, path: Path, digest: str, manifest_file: Path) -> str:
    data = load_intent(path, digest, manifest_file)
    payload = outbound(data["ticket"])
    attempt = attempt_path(path)
    if attempt.exists() or attempt.is_symlink() or binding_path(path).exists():
        raise Refusal("attempt already recorded; use verify only")
    before = inventory(client, data["parent_number"])
    if before != data["preimage"] or len(before["children"]) >= 100 or matches(before["repository"], data["ticket"]):
        raise Refusal("fresh issue preimage drifted")
    publish(attempt, wire({"version": 1, "intent_sha256": digest,
                           "operation": operation(data)}))
    if before["parent"] is not None:
        payload["parent_issue_id"] = before["parent"]["id"]
    try:
        client.rest(API_VERSION).issues.create(OWNER, REPO, data=payload)
    except Exception:
        return "UNRESOLVED"
    try:
        return verify(client, path, digest, manifest_file)
    except Exception:
        return "UNRESOLVED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preview", "apply", "verify"))
    parser.add_argument("--manifest-file", type=Path, required=True)
    parser.add_argument("--journal-dir", type=Path, required=True)
    parser.add_argument("--local-id", required=True)
    parser.add_argument("--intent-sha256")
    args = parser.parse_args()
    try:
        path = intent_path(args.journal_dir, args.local_id)
        if args.mode == "preview":
            data, _ = manifest(args.manifest_file)
            if args.local_id not in {ticket["local_id"] for ticket in data["tickets"]}:
                raise Refusal("local ID absent from manifest")
            if path.exists() or path.is_symlink():
                raise Refusal("local ID already has a publication record")
        else:
            if not args.intent_sha256:
                raise Refusal("intent SHA-256 required")
            load_intent(path, args.intent_sha256, args.manifest_file)
        token, _ = credential()
        if not token:
            raise Refusal("GitHub credential unavailable")
        with GitHub(token, auto_retry=False, http_cache=False, follow_redirects=False,
                    trust_env=False, timeout=15) as client:
            if args.mode == "preview":
                print(preview(client, args.manifest_file, args.local_id, args.journal_dir))
                return 0
            result = (apply if args.mode == "apply" else verify)(
                client, path, args.intent_sha256, args.manifest_file)
            print(result)
            return 0 if result == "VERIFIED" else 2
    except (Refusal, OSError, UnicodeError, ValueError) as error:
        print(refused(error), file=sys.stderr)  # R-174: one line per scan hit
        return 2
    except Exception as error:
        print(f"UNRESOLVED: {type(error).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
