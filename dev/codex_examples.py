#!/usr/bin/env python3
"""A06 bounded, SHA-checked GitHubKit source blob retrieval."""

from __future__ import annotations

import base64
import binascii
import argparse
import hashlib
import json
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tomllib
from collections.abc import Callable

from githubkit import GitHub
from githubkit.exception import RequestError

from github_search_one_page import API_VERSION, credential
from search_catalog import ROOT, RUN, confined, digest, encoded, verified_run

SCHEMA = ROOT / "evidence/codex-examples/release/config-schema.json"
SCHEMA_SHA256 = "7933a70506e753a6e98c16800d2a76770b2af2b7295491f8f0b8e713e952027e"
RELEASE_COMMIT = "092d3acd6bec3e3a14bdc7e7a2810ab628ab759d"
MAX_BLOB_BYTES = 262144
MAX_SELECTED = 3


class BlobError(ValueError):
    """A requested full blob does not match its pinned Git object identity."""


def decode_blob(blob: object, expected_sha: str, *, max_bytes: int) -> bytes:
    if (not re.fullmatch(r"[0-9a-f]{40}", expected_sha)
            or getattr(blob, "sha", None) != expected_sha
            or getattr(blob, "encoding", None) != "base64"
            or type(getattr(blob, "size", None)) is not int
            or not 0 <= blob.size <= max_bytes
            or not isinstance(getattr(blob, "content", None), str)):
        raise BlobError("invalid blob metadata or size")
    encoded = blob.content
    if re.search(r"[^A-Za-z0-9+/=\r\n]", encoded):
        raise BlobError("invalid blob encoding")
    encoded = encoded.replace("\r", "").replace("\n", "")
    try:
        data = base64.b64decode(encoded, validate=True)
    except binascii.Error as error:
        raise BlobError("invalid blob base64") from error
    if (base64.b64encode(data).decode("ascii") != encoded or len(data) != blob.size
            or len(data) > max_bytes):
        raise BlobError("blob size or encoding mismatch")
    git_sha = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
    if git_sha != expected_sha:
        raise BlobError("Git blob SHA mismatch")
    return data


def collect_blobs(
    items: list[dict[str, str]], selected_shas: list[str],
    fetch: Callable[[str, str], object], metadata: dict[str, dict[str, object]],
    *, max_items: int, max_bytes: int,
) -> tuple[list[dict[str, object]], dict[str, bytes]]:
    if (not 1 <= len(selected_shas) <= max_items or len(set(selected_shas)) != len(selected_shas)
            or any(not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in selected_shas)):
        raise BlobError("invalid selected blob budget or SHA")
    chosen = [item for item in items if item.get("sha") in selected_shas]
    if set(selected_shas) != {item["sha"] for item in chosen} or len(chosen) > max_items:
        raise BlobError("selected SHA missing or too many paths")
    repositories = {item.get("repository") for item in chosen}
    if len(repositories) != 1:
        raise BlobError("one repository per bounded receipt required")
    repo = repositories.pop()
    if (not isinstance(repo, str) or repo not in metadata
            or metadata[repo].get("private") is not False
            or type(metadata[repo].get("fork")) is not bool):
        raise BlobError("unverified or private repository")
    for item in chosen:
        path = item.get("path")
        if (not isinstance(path, str) or not path or path.startswith("/")
                or any(part in ("", ".", "..") for part in path.split("/"))):
            raise BlobError("unsafe source path")
    rows: list[dict[str, object]] = []
    contents: dict[str, bytes] = {}
    first_path: dict[str, str] = {}
    for item in chosen:
        sha = item["sha"]
        if sha not in contents:
            contents[sha] = decode_blob(fetch(repo, sha), sha, max_bytes=max_bytes)
        rows.append({"repository": repo, "path": item["path"], "blob_sha": sha,
                     "sha256": hashlib.sha256(contents[sha]).hexdigest(),
                     "size": len(contents[sha]), "fork": metadata[repo]["fork"],
                     "parent": metadata[repo].get("parent"),
                     "source": metadata[repo].get("source"),
                     "duplicate_of": first_path.get(sha)})
        first_path.setdefault(sha, item["path"])
    return rows, contents


def run(args: argparse.Namespace) -> dict[str, object]:
    match = RUN.fullmatch(args.run_id)
    if not match:
        raise BlobError("invalid saved-search run ID")
    entry = confined(ROOT / "evidence/saved-searches/runs" / args.run_id)
    if entry.is_symlink() or not entry.is_dir():
        raise BlobError("missing or symlinked saved-search run")
    manifest_bytes = confined(entry / "manifest.json").read_bytes()
    manifest, normalized = verified_run(entry, match, manifest_bytes)
    schema_bytes = confined(SCHEMA).read_bytes()
    if digest(schema_bytes) != SCHEMA_SHA256:
        raise BlobError("release schema digest mismatch")
    if json.loads(schema_bytes).get("title") is None:
        raise BlobError("invalid release schema JSON")
    version = subprocess.run(["codex", "--version"], capture_output=True, text=True,
                             timeout=5, check=False)
    if version.returncode != 0 or version.stdout.strip() != "codex-cli 0.162.1":
        raise BlobError("installed Codex release differs from pinned schema")
    selected = [item for item in normalized["items"] if item.get("sha") in args.sha]
    if not args.sha or len(args.sha) > MAX_SELECTED or set(args.sha) != {x["sha"] for x in selected}:
        raise BlobError("selected SHA not present in verified run")
    repositories = {item["repository"] for item in selected}
    if len(repositories) != 1:
        raise BlobError("one repository per receipt required")
    repo = repositories.pop()
    owner, name = repo.split("/", 1)
    token, route = credential()
    if token is None:
        raise BlobError("GitHub credential unavailable")
    client = GitHub(token)
    remote = client.rest(API_VERSION).repos.get(owner=owner, repo=name).parsed_data
    if remote.full_name != repo or remote.private:
        raise BlobError("repository identity or public status changed")
    metadata = {repo: {"private": remote.private, "fork": remote.fork,
                       "parent": getattr(getattr(remote, "parent", None), "full_name", None),
                       "source": getattr(getattr(remote, "source", None), "full_name", None)}}

    def fetch(repository: str, sha: str) -> object:
        response = client.rest(API_VERSION).git.get_blob(
            owner=owner, repo=name, file_sha=sha)
        if response.status_code != 200:
            raise BlobError("blob retrieval did not return HTTP 200")
        return response.parsed_data

    rows, blobs = collect_blobs(normalized["items"], args.sha, fetch, metadata,
                                max_items=MAX_SELECTED, max_bytes=MAX_BLOB_BYTES)
    root = confined(ROOT / "evidence/codex-examples/runs")
    root.mkdir(parents=True, exist_ok=True)
    target = root / f"{args.run_id}--{secrets.token_hex(8)}"
    target.mkdir()
    blob_dir = target / "blobs"
    blob_dir.mkdir()
    for sha, data in blobs.items():
        (blob_dir / sha).write_bytes(data)
    receipt: dict[str, object] = {
        "version": 1, "saved_run_id": args.run_id,
        "saved_manifest_sha256": digest(manifest_bytes),
        "saved_normalized_sha256": manifest["normalized_sha256"],
        "search_status": normalized["status"],
        "example_coverage": "provisional" if normalized["status"] != "complete" else "bounded",
        "sdk": "githubkit", "sdk_api_version": API_VERSION,
        "credential_route": route, "release_tag": "rust-v0.162.1",
        "release_commit": RELEASE_COMMIT,
        "schema_asset": "config-schema.json", "schema_sha256": SCHEMA_SHA256,
        "installed_cli": version.stdout.strip(), "max_selected": MAX_SELECTED,
        "max_blob_bytes": MAX_BLOB_BYTES, "blobs": rows,
    }
    (target / "receipt.json").write_bytes(encoded(receipt))
    return {"status": "recorded", "receipt": str(target / "receipt.json"),
            "blobs": len(blobs), "source_paths": len(rows),
            "example_coverage": receipt["example_coverage"]}


def inspect_configuration(path: str, data: bytes, schema: dict[str, object]) -> dict[str, object]:
    """Report a bounded method outcome without claiming full validity."""
    if Path(path).name != "config.toml":
        return {"validity": "UNVERIFIED", "kind": "documentation" if Path(path).suffix in
                (".md", ".rst") else "unknown", "method": None, "inspection": "not_inspected",
                "reason": "Selected path is not config.toml; configuration inspection not executed"}
    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return {"validity": "UNVERIFIED", "kind": "configuration",
                "method": "python-stdlib-tomllib.loads", "inspection": "invalid_syntax",
                "reason": "Invalid TOML syntax or UTF-8; input values omitted"}
    properties = schema.get("properties")
    model = properties.get("model") if isinstance(properties, dict) else None
    field: dict[str, object] = {"method": None, "status": "not_inspected",
                              "reason": "Pinned root model:string rule unavailable"}
    if isinstance(model, dict) and model.get("type") == "string":
        field = {"method": "pinned-root-model-type", "rule": "properties.model.type=string",
                 "status": "absent" if "model" not in parsed else
                           ("present_string" if isinstance(parsed["model"], str) else "present_wrong_type"),
                 "schema_sha256": SCHEMA_SHA256, "release_tag": "rust-v0.162.1",
                 "release_commit": RELEASE_COMMIT}
    return {"validity": "UNVERIFIED", "kind": "configuration", "model_field": field,
            "uninspected_fields": sorted(key for key in parsed
                                         if key != "model" or field["status"] == "not_inspected"),
            "method": "python-stdlib-tomllib.loads", "inspection": "parsed",
            "reason": "Model availability, full schema, current release, native and runtime validation not executed"}


def offline(args: argparse.Namespace) -> dict[str, object]:
    """Consume an independently pinned historical receipt; perform no native/provider calls."""
    match = RUN.fullmatch(args.run_id)
    relative = Path(args.offline_receipt)
    if (not match or relative.is_absolute() or not args.receipt_sha256
            or not re.fullmatch(r"[0-9a-f]{64}", args.receipt_sha256)):
        raise BlobError("invalid offline run, receipt path or digest pin")
    receipt_path = confined(ROOT / relative)
    runs = confined(ROOT / "evidence/codex-examples/runs")
    if (receipt_path.name != "receipt.json" or receipt_path.parent.parent != runs
            or not re.fullmatch(re.escape(args.run_id) + r"--[0-9a-f]{16}", receipt_path.parent.name)):
        raise BlobError("offline receipt is not the selected retrieval run")
    receipt_bytes = receipt_path.read_bytes()
    if digest(receipt_bytes) != args.receipt_sha256:
        raise BlobError("retrieval receipt digest mismatch")
    receipt = json.loads(receipt_bytes)
    entry = confined(ROOT / "evidence/saved-searches/runs" / args.run_id)
    manifest_bytes = confined(entry / "manifest.json").read_bytes()
    for name in ("raw.json", "normalized.json"):
        confined(entry / name)
    manifest, normalized = verified_run(entry, match, manifest_bytes)
    if (type(manifest["version"]) is not int or manifest["observed_at_ns"] <= 0
            or normalized["status"] not in ("complete", "partial") or not isinstance(normalized["items"], list)
            or any(type(normalized[k]) is not int or normalized[k] < 0 for k in
                   ("returned_count", "request_budget", "requests_used", "attempt_count", "pages_succeeded"))
            or normalized["returned_count"] != len(normalized["items"])
            or not 1 <= normalized["requests_used"] <= normalized["request_budget"] <= 20
            or not 1 <= normalized["pages_succeeded"] <= normalized["attempt_count"] <= normalized["requests_used"]
            or not isinstance(normalized["total_counts"], list)
            or len(normalized["total_counts"]) != normalized["pages_succeeded"]
            or any(type(n) is not int or n < 0 for n in normalized["total_counts"])
            or type(normalized["complete_candidate"]) is not bool
            or type(normalized["collection_complete_candidate"]) is not bool
            or not isinstance(normalized["reasons"], list) or any(not isinstance(r, str) for r in normalized["reasons"])
            or normalized["control_status"] not in ("passed", "failed", "not_run")
            or not normalized["collection_complete_candidate"] and normalized["control_status"] != "not_run"
            or normalized["status"] == "complete" and (normalized["complete_candidate"] is not True
                or normalized["control_status"] != "passed" or not normalized["collection_complete_candidate"]
                or normalized["reasons"])):
        raise BlobError("invalid offline normalized budget or coverage")
    schema_bytes = confined(SCHEMA).read_bytes()
    schema = json.loads(schema_bytes)
    pinned = {"version": 1, "saved_run_id": args.run_id,
              "saved_manifest_sha256": digest(manifest_bytes),
              "saved_normalized_sha256": manifest["normalized_sha256"],
              "search_status": normalized["status"],
              "example_coverage": "bounded" if normalized["status"] == "complete" else "provisional",
              "sdk": "githubkit", "sdk_api_version": API_VERSION,
              "release_tag": "rust-v0.162.1", "release_commit": RELEASE_COMMIT,
              "schema_asset": "config-schema.json", "schema_sha256": SCHEMA_SHA256,
              "installed_cli": "codex-cli 0.162.1", "max_selected": MAX_SELECTED,
              "max_blob_bytes": MAX_BLOB_BYTES}
    if (not isinstance(receipt, dict) or set(receipt) != set(pinned) | {"credential_route", "blobs"}
            or any(type(receipt[k]) is not type(v) or receipt[k] != v for k, v in pinned.items())
            or receipt["credential_route"] not in ("gh_cli", "GITHUB_TOKEN", "GH_TOKEN", "fixture")
            or digest(schema_bytes) != SCHEMA_SHA256 or not isinstance(schema, dict)):
        raise BlobError("offline receipt metadata or schema mismatch")
    if (not 1 <= len(args.sha) <= MAX_SELECTED or len(set(args.sha)) != len(args.sha)
            or any(not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in args.sha)):
        raise BlobError("invalid selected blob budget or SHA")
    identities = set()
    for item in normalized["items"]:
        if (not isinstance(item, dict) or any(not isinstance(item.get(k), str) for k in ("repository", "path", "sha"))
                or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", item["repository"])
                or not re.fullmatch(r"[0-9a-f]{40}", item["sha"])
                or item["path"].startswith("/") or any(part in ("", ".", "..") for part in item["path"].split("/"))):
            raise BlobError("invalid normalized source identity")
        identity = (item["repository"], item["path"], item["sha"])
        if identity in identities or "identity" in item and item["identity"] != ":".join(identity):
            raise BlobError("duplicate or inconsistent normalized identity")
        identities.add(identity)
    selected = [item for item in normalized["items"] if item["sha"] in args.sha]
    rows = receipt["blobs"]
    if (not isinstance(rows, list) or not 1 <= len(selected) <= MAX_SELECTED
            or set(args.sha) != {item["sha"] for item in selected} or len(rows) != len(selected)
            or len({item["repository"] for item in selected}) != 1):
        raise BlobError("offline selected paths or budget mismatch")
    first, provenance, inspections = {}, None, []
    for item, row in zip(selected, rows):
        repo, path, sha = item["repository"], item["path"], item["sha"]
        if (not isinstance(row, dict) or set(row) != {"repository", "path", "blob_sha", "sha256",
                "size", "fork", "parent", "source", "duplicate_of"}
                or type(row["size"]) is not int or not 0 <= row["size"] <= MAX_BLOB_BYTES
                or type(row["fork"]) is not bool
                or any(value is not None and (not isinstance(value, str) or not re.fullmatch(
                    r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value)) for value in (row["parent"], row["source"]))):
            raise BlobError("invalid offline blob provenance or budget")
        metadata = (row["fork"], row["parent"], row["source"])
        if (provenance is not None and provenance != metadata
                or row["fork"] and (row["parent"] is None or row["source"] is None)
                or not row["fork"] and (row["parent"] is not None or row["source"] is not None)):
            raise BlobError("inconsistent offline repository provenance")
        provenance = metadata
        with confined(receipt_path.parent / "blobs" / sha).open("rb") as stream:
            data = stream.read(MAX_BLOB_BYTES + 1)
        if len(data) > MAX_BLOB_BYTES:
            raise BlobError("offline blob exceeds byte budget")
        expected = {"repository": repo, "path": path, "blob_sha": sha,
                    "sha256": digest(data), "size": len(data), "fork": row["fork"],
                    "parent": row["parent"], "source": row["source"], "duplicate_of": first.get(sha)}
        if (row != expected
                or hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() != sha):
            raise BlobError("offline blob identity, bytes or duplicate mismatch")
        first.setdefault(sha, path)
        inspections.append({**row, **inspect_configuration(path, data, schema)})
    root = confined(ROOT / "evidence/codex-examples/classifications")
    target = confined(root / f"{args.run_id}--{secrets.token_hex(8)}")
    output = confined(target / "receipt.json")
    record = {**pinned, "credential_route": receipt["credential_route"], "retrieval_receipt": str(relative),
              "retrieval_receipt_sha256": args.receipt_sha256, "inspections": inspections}
    root.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    with output.open("xb") as stream:
        stream.write(encoded(record))
    return {"status": "recorded", "receipt": str(output), "blobs": len(first),
            "source_paths": len(rows), "example_coverage": pinned["example_coverage"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--sha", action="append", required=True)
    parser.add_argument("--offline-receipt")
    parser.add_argument("--receipt-sha256")
    args = parser.parse_args()
    try:
        if args.receipt_sha256 is not None and args.offline_receipt is None:
            raise BlobError("receipt digest requires offline mode")
        print(json.dumps(offline(args) if args.offline_receipt is not None else run(args), sort_keys=True))
        return 0
    except RequestError:
        print(json.dumps({"status": "unresolved", "reason": "GitHub request failed"}),
              file=sys.stderr)
        return 2
    except (TypeError, AttributeError, IndexError):
        print(json.dumps({"status": "unresolved", "reason": "malformed artifact shape"}), file=sys.stderr)
        return 2
    except (BlobError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "unresolved", "reason": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
