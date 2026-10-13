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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--sha", action="append", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), sort_keys=True))
        return 0
    except RequestError:
        print(json.dumps({"status": "unresolved", "reason": "GitHub request failed"}),
              file=sys.stderr)
        return 2
    except (BlobError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "unresolved", "reason": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
