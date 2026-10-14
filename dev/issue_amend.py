#!/usr/bin/env python3
"""A07a: one GitHub issue amendment, with a durable single-send boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

from githubkit import GitHub

from github_search_one_page import API_VERSION, credential

OWNER, REPO = "ray-manaloto", "claude-code-marketplace"
HEX = re.compile(r"[0-9a-f]{64}\Z")
COMPLETED = {"state": "closed", "state_reason": "completed"}
VERDICTS = {"acceptance": "accepted", "review": "approved", "retro": "applied", "delivery": "delivered"}


class Refusal(ValueError):
    pass


def wire(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reject_symlinks(path: Path) -> None:
    if ".." in path.parts:
        raise Refusal("parent traversal refused")
    absolute = path if path.is_absolute() else Path.cwd() / path
    if any(part.is_symlink() for part in (absolute, *absolute.parents)):
        raise Refusal("symlinked path component refused")


def read(path: Path) -> bytes:
    reject_symlinks(path)
    if not path.is_file():
        raise Refusal("missing or symlinked input")
    return path.read_bytes()


def publish(path: Path, payload: bytes) -> None:
    reject_symlinks(path)
    if not path.parent.is_dir():
        raise Refusal("output directory missing or symlinked")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)


def labels(value: object) -> list[str]:
    if (not isinstance(value, list) or len(value) > 100 or
            any(not isinstance(x, str) or not x or x.strip() != x or len(x) > 100 for x in value) or
            len({x.casefold() for x in value}) != len(value)):
        raise Refusal("invalid labels")
    return sorted(value)


def snapshot(raw: object, number: int, completion: bool = False) -> dict:
    if not isinstance(raw, dict) or "pull_request" in raw:
        raise Refusal("issue response invalid or is a pull request")
    try:
        names = labels([entry["name"] for entry in raw["labels"]])
        result = {key: raw[key] for key in ("id", "number", "title", "body", "state", "updated_at")}
    except (KeyError, TypeError) as error:
        raise Refusal("incomplete issue response") from error
    if (type(result["id"]) is not int or result["id"] <= 0 or
            result["number"] != number or type(result["number"]) is not int or
            not isinstance(result["title"], str) or
            result["body"] is not None and not isinstance(result["body"], str) or
            result["state"] not in (("open", "closed") if completion else ("open",))
            or not isinstance(result["updated_at"], str)):
        raise Refusal("unexpected issue identity or state")
    if completion:
        result["state_reason"] = raw.get("state_reason")
        if result["state_reason"] not in (None, "completed", "not_planned", "reopened"):
            raise Refusal("unexpected completion reason")
    return {**result, "labels": names}


def fetch(client: GitHub, number: int, completion: bool = False) -> dict:
    response = client.rest(API_VERSION).issues.get(OWNER, REPO, number)
    if response.status_code != 200:
        raise Refusal("issue GET did not succeed")
    return snapshot(response.raw_response.json(), number, completion)


def matches_completion_binding(data: object, binding: dict) -> bool:
    return (isinstance(data, dict) and type(data.get("version")) is int and data["version"] == 1
            and not any(type(data.get(key)) is not type(value) or data[key] != value for key, value in binding.items()))


def completion_evidence(data: object, before: dict) -> None:
    binding = {"repo": f"{OWNER}/{REPO}", "number": before["number"],
               "issue_id": before["id"], "preimage_sha256": sha(wire(before))}
    if (not matches_completion_binding(data, binding)
            or not isinstance(data.get("references"), dict) or set(data["references"]) != set(VERDICTS)):
        raise Refusal("invalid completion evidence binding")
    for kind, verdict in VERDICTS.items():
        ref = data["references"][kind]
        if (not isinstance(ref, dict) or set(ref) != {"path", "sha256"}
                or not isinstance(ref["path"], str) or not Path(ref["path"]).is_absolute()
                or not isinstance(ref["sha256"], str) or not HEX.fullmatch(ref["sha256"])):
            raise Refusal("invalid completion evidence reference")
        source = read(Path(ref["path"]))
        if sha(source) != ref["sha256"]:
            raise Refusal("completion evidence SHA-256 mismatch")
        receipt = json.loads(source)
        if (not matches_completion_binding(receipt, binding)
                or receipt.get("result") != verdict):
            raise Refusal(f"{kind} evidence is not accepted for this preimage")


def intent(path: Path, digest: str) -> dict:
    source = read(path)
    if not HEX.fullmatch(digest) or sha(source) != digest:
        raise Refusal("intent SHA-256 mismatch")
    data = json.loads(source)
    if isinstance(data, dict) and data.get("version") == 2:
        if (type(data["version"]) is not int
                or set(data) != {"version", "repo", "number", "preimage", "desired", "evidence"}
                or data["repo"] != f"{OWNER}/{REPO}" or type(data["number"]) is not int
                or data["number"] <= 0 or data["desired"] != COMPLETED
                or not isinstance(data["preimage"], dict) or data["preimage"].get("state") != "open"
                or snapshot({**data["preimage"], "labels": [{"name": x} for x in data["preimage"].get("labels", [])]},
                            data["number"], True) != data["preimage"]):
            raise Refusal("invalid completion intent")
        completion_evidence(data["evidence"], data["preimage"])
        return data
    if (not isinstance(data, dict) or set(data) != {"version", "repo", "number", "preimage", "desired"}
            or data["version"] != 1 or data["repo"] != f"{OWNER}/{REPO}"
            or type(data["number"]) is not int or data["number"] <= 0
            or not isinstance(data["desired"], dict) or set(data["desired"]) != {"body", "labels"}
            or not isinstance(data["desired"]["body"], str)
            or labels(data["desired"]["labels"]) != data["desired"]["labels"]
            or not isinstance(data["preimage"], dict)
            or snapshot({**data["preimage"], "labels": [{"name": x} for x in data["preimage"].get("labels", [])]}, data["number"]) != data["preimage"]):
        raise Refusal("invalid amendment intent")
    return data


def preview(client: GitHub, number: int, body_file: Path, labels_file: Path, output: Path) -> str:
    if type(number) is not int or number <= 0 or output.exists() or output.is_symlink():
        raise Refusal("invalid issue number or existing intent")
    body = read(body_file).decode("utf-8")
    names = labels(json.loads(read(labels_file)))
    before = fetch(client, number)
    data = {"version": 1, "repo": f"{OWNER}/{REPO}", "number": number,
            "preimage": before, "desired": {"body": body, "labels": names}}
    payload = wire(data)
    publish(output, payload)
    return sha(payload)


def preview_completion(client: GitHub, number: int, evidence_file: Path, output: Path) -> str:
    """Prepare closure using four SHA-bound typed receipts for the exact open preimage."""
    if type(number) is not int or number <= 0 or output.exists() or output.is_symlink():
        raise Refusal("invalid issue number or existing intent")
    before = fetch(client, number, True)
    if before["state"] != "open":
        raise Refusal("issue already closed; no completion intent prepared")
    evidence = json.loads(read(evidence_file))
    completion_evidence(evidence, before)
    payload = wire({"version": 2, "repo": f"{OWNER}/{REPO}", "number": number,
                    "preimage": before, "desired": COMPLETED, "evidence": evidence})
    publish(output, payload)
    return sha(payload)


def marker(path: Path) -> Path:
    return path.with_name(path.name + ".attempt.json")


def verify(client: GitHub, path: Path, digest: str) -> str:
    data = intent(path, digest)
    attempt = json.loads(read(marker(path)))
    operation = "PATCH completed state" if data["version"] == 2 else "PATCH body labels"
    if attempt != {"version": 1, "intent_sha256": digest, "operation": operation}:
        raise Refusal("invalid attempt marker")
    current = fetch(client, data["number"], data["version"] == 2)
    before, desired = data["preimage"], data["desired"]
    if data["version"] == 2:
        return "VERIFIED" if current == {**before, **desired, "updated_at": current["updated_at"]} else "UNRESOLVED"
    if (all(current[key] == before[key] for key in ("id", "number", "title", "state"))
            and current["body"] == desired["body"] and current["labels"] == desired["labels"]):
        return "VERIFIED"
    return "UNRESOLVED"


def apply(client: GitHub, path: Path, digest: str) -> str:
    data = intent(path, digest)
    if marker(path).exists() or marker(path).is_symlink():
        raise Refusal("attempt already recorded; use verify only")
    current = fetch(client, data["number"], data["version"] == 2)
    if (data["version"] == 2
            and current == {**data["preimage"], **COMPLETED, "updated_at": current["updated_at"]}):
        return "ALREADY_COMPLETED"
    if current != data["preimage"]:
        raise Refusal("issue preimage drifted")
    publish(marker(path), wire({"version": 1, "intent_sha256": digest,
                                "operation": "PATCH completed state" if data["version"] == 2 else "PATCH body labels"}))
    try:
        client.rest(API_VERSION).issues.update(OWNER, REPO, data["number"],
                                               data=data["desired"])
    except Exception:
        return "UNRESOLVED"
    try:
        return verify(client, path, digest)
    except Exception:
        return "UNRESOLVED"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("preview")
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--body-file", type=Path, required=True)
    p.add_argument("--labels-file", type=Path, required=True)
    p.add_argument("--intent-file", type=Path, required=True)
    p = sub.add_parser("preview-completion")
    p.add_argument("--issue", type=int, required=True)
    p.add_argument("--evidence-file", type=Path, required=True)
    p.add_argument("--intent-file", type=Path, required=True)
    for name in ("apply", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--intent-file", type=Path, required=True)
        p.add_argument("--intent-sha256", required=True)
    args = parser.parse_args()
    try:
        token, _ = credential()
        if not token:
            raise Refusal("GitHub credential unavailable")
        with GitHub(token, auto_retry=False, http_cache=False, follow_redirects=False,
                    trust_env=False, timeout=15) as client:
            if args.mode == "preview":
                print(preview(client, args.issue, args.body_file, args.labels_file, args.intent_file))
                return 0
            if args.mode == "preview-completion":
                print(preview_completion(client, args.issue, args.evidence_file, args.intent_file))
                return 0
            result = globals()[args.mode](client, args.intent_file, args.intent_sha256)
            print(result)
            return 0 if result in ("VERIFIED", "ALREADY_COMPLETED") else 2
    except (Refusal, OSError, UnicodeError, ValueError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"UNRESOLVED: {type(error).__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
