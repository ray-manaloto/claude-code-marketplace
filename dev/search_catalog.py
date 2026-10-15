#!/usr/bin/env python3
"""A04 saved-query validation and append-only GitHubKit run recording."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import time
import tomllib

import httpx
from githubkit import GitHub

from github_search_one_page import API_VERSION, credential, replay_response, search

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
RUN = re.compile(r"([A-Za-z][A-Za-z0-9_-]{0,63})--[0-9]{16,20}--[0-9a-f]{16}\Z")


class CatalogError(ValueError):
    """Invalid local input; live authentication must not have started."""


def encoded(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def confined(path: Path) -> Path:
    candidate = Path(os.path.abspath(path))
    if not candidate.is_relative_to(ROOT):
        raise CatalogError("path must be inside the project")
    for part in (candidate, *candidate.parents):
        if part == ROOT.parent:
            break
        if part.is_symlink():
            raise CatalogError("symlinked project path refused")
    return candidate


def valid_query(value: object) -> bool:
    return (isinstance(value, str) and 1 <= len(value) <= 256
            and value.strip() == value and not any(ord(c) < 32 for c in value)
            and not re.search(r"(?:^|\s)repo:", value, re.IGNORECASE))


def catalog(path: Path) -> tuple[list[dict[str, object]], str]:
    path = confined(path)
    try:
        source = path.read_bytes()
        document = tomllib.loads(source.decode("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise CatalogError("invalid or missing catalog") from error
    if (set(document) != {"version", "search"} or document["version"] != 1
            or type(document["version"]) is not int
            or not isinstance(document["search"], list) or not document["search"]):
        raise CatalogError("invalid catalog envelope")
    seen: set[str] = set()
    rows = []
    for row in document["search"]:
        if (not isinstance(row, dict)
                or set(row) != {"id", "query", "repo", "per_page", "max_pages",
                                    "max_items", "timeout_seconds", "control"}):
            raise CatalogError("invalid search fields")
        name, query, repo = row["id"], row["query"], row["repo"]
        if not isinstance(name, str) or not ID.fullmatch(name) or name.casefold() in seen:
            raise CatalogError("unsafe or case-colliding search ID")
        seen.add(name.casefold())
        if (not valid_query(query) or not isinstance(repo, str)
                or not REPO.fullmatch(repo)
                or any(part in {".", ".."} for part in repo.split("/"))):
            raise CatalogError("invalid query or repository")
        for field, upper in (("per_page", 100), ("max_pages", 10),
                             ("max_items", 1000), ("timeout_seconds", 120)):
            if type(row[field]) is not int or not 1 <= row[field] <= upper:
                raise CatalogError(f"invalid {field}")
        if not isinstance(row["control"], list) or not row["control"]:
            raise CatalogError("a same-scope control definition is required")
        seen_controls: set[str] = set()
        for control in row["control"]:
            if (not isinstance(control, dict) or set(control) != {"query", "expected_min"}
                    or not valid_query(control["query"])
                    or control["query"] == query
                    or control["query"].casefold() in seen_controls
                    or type(control["expected_min"]) is not int
                    or not 1 <= control["expected_min"] <= row["max_items"]):
                raise CatalogError("invalid control definition")
            seen_controls.add(control["query"].casefold())
        effective = f"{query} repo:{repo}"
        criteria = {"endpoint": "GET /search/code", "effective_query": effective,
                    "sort": "default", "order": "default", "api_version": API_VERSION,
                    "normalization_version": 2, "per_page": row["per_page"],
                    "max_pages": row["max_pages"], "max_items": row["max_items"],
                    "timeout_seconds": row["timeout_seconds"]}
        rows.append({**row, "effective_query": effective,
                     "fingerprint": digest(encoded(criteria)), "criteria": criteria})
    return rows, digest(source)


def quarantines(output: Path) -> dict[tuple[str, str], int]:
    exclusions: dict[tuple[str, str], int] = {}
    directory = output / "quarantine"
    if directory.is_symlink():
        raise CatalogError("symlinked quarantine directory refused")
    if not directory.exists():
        return exclusions
    for entry in directory.iterdir():
        if entry.name.startswith(".pending-"):
            try:
                mode = entry.lstat().st_mode
            except FileNotFoundError:
                continue
            if not stat.S_ISREG(mode):
                raise CatalogError("invalid pending quarantine entry")
            continue  # It may disappear after link publication; neither state is a ledger entry.
        if entry.is_symlink() or not entry.is_file() or entry.suffix != ".json":
            raise CatalogError("invalid quarantine entry")
        try:
            source = entry.read_bytes()
            if not entry.stem.endswith(digest(source)):
                raise ValueError("quarantine digest mismatch")
            value = json.loads(source)
            run_id, manifest_hash = value["run_id"], value["manifest_sha256"]
            if (set(value) != {"version", "run_id", "manifest_sha256", "reason", "recorded_at_ns"}
                    or value["version"] != 2 or not RUN.fullmatch(run_id)
                    or not re.fullmatch(r"[0-9a-f]{64}", manifest_hash)
                    or not isinstance(value["reason"], str) or not value["reason"]
                    or type(value["recorded_at_ns"]) is not int
                    or value["recorded_at_ns"] <= 0):
                raise ValueError("invalid exclusion")
        except (OSError, ValueError, TypeError, KeyError) as error:
            raise CatalogError("corrupt quarantine entry") from error
        key = (run_id, manifest_hash)
        exclusions[key] = max(exclusions.get(key, 0), value["recorded_at_ns"])
    return exclusions


def verified_run(entry: Path, match: re.Match[str], data: bytes) -> tuple[dict, dict]:
    """Validate published record bytes before using identity or comparison data."""
    row = json.loads(data)
    if (set(row) != {"version", "run_id", "id", "catalog_sha256",
                     "fingerprint", "criteria", "observed_at_ns",
                     "result_status", "raw_sha256", "normalized_sha256",
                     "source_fixture_sha256"}
            or row["version"] != 1 or row["run_id"] != entry.name
            or row["id"] != match.group(1)
            or type(row["observed_at_ns"]) is not int
            or not re.fullmatch(r"[0-9a-f]{64}", row["catalog_sha256"])
            or row["fingerprint"] != digest(encoded(row["criteria"]))):
        raise ValueError("invalid manifest identity")
    artifacts = {}
    for name in ("raw", "normalized"):
        artifact = entry / f"{name}.json"
        if artifact.is_symlink():
            raise ValueError("symlinked artifact")
        artifacts[name] = artifact.read_bytes()
        if digest(artifacts[name]) != row[f"{name}_sha256"]:
            raise ValueError("artifact digest mismatch")
    normalized = json.loads(artifacts["normalized"])
    if normalized["normalized"]["status"] != row["result_status"]:
        raise ValueError("result status mismatch")
    return row, normalized["normalized"]


def inspect_runs(output: Path, selected_id: str, *, capture_published: bool = False) -> dict[str, object]:
    counts = {"valid": 0, "interrupted": 0, "orphan": 0,
              "active": 0, "corrupt_unselected": 0, "quarantined": 0,
              "latest_valid": None, "baseline_reset": False}
    if capture_published:
        counts["published"] = {}
    latest: tuple[int, str] | None = None
    reset_after_ns: int | None = None
    directory = output / "runs"
    if directory.is_symlink():
        raise CatalogError("symlinked runs directory refused")
    if not directory.exists():
        return counts
    excluded = quarantines(output)
    for entry in sorted(directory.iterdir()):
        match = RUN.fullmatch(entry.name)
        selected = bool(match and match.group(1).casefold() == selected_id.casefold())
        if entry.is_symlink():
            if selected:
                raise CatalogError("symlinked selected run refused")
            counts["orphan"] += 1
            continue
        if not entry.is_dir() or not match:
            counts["orphan"] += 1
            continue
        manifest = entry / "manifest.json"
        if manifest.is_symlink():
            if match.group(1).casefold() == selected_id.casefold():
                raise CatalogError("symlinked selected manifest refused")
            counts["corrupt_unselected"] += 1
            continue
        if not manifest.exists():
            lock = entry / ".writer.lock"
            if lock.is_file() and not lock.is_symlink():
                with lock.open("rb") as handle:
                    try:
                        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        counts["active"] += 1
                        continue
                    finally:
                        try:
                            fcntl.flock(handle, fcntl.LOCK_UN)
                        except OSError:
                            pass
            counts["interrupted"] += 1
            continue
        try:
            data = manifest.read_bytes()
        except OSError as error:
            if selected:
                raise CatalogError("unreadable selected manifest") from error
            counts["corrupt_unselected"] += 1
            continue
        excluded_at = excluded.get((entry.name, digest(data)))
        if excluded_at is not None:
            counts["quarantined"] += 1
            if selected:
                reset_after_ns = max(reset_after_ns or 0, excluded_at)
            continue
        try:
            row, _ = verified_run(entry, match, data)
        except (OSError, ValueError, TypeError, KeyError) as error:
            if selected:
                raise CatalogError("corrupt selected record; quarantine explicitly") from error
            counts["corrupt_unselected"] += 1
            continue
        counts["valid"] += 1
        if selected and capture_published:
            counts["published"][entry.name] = digest(data)
        candidate = (row["observed_at_ns"], entry.name)
        if selected and (latest is None or candidate > latest):
            latest = candidate
            counts["latest_valid"] = entry.name
    if reset_after_ns is not None and (latest is None or latest[0] <= reset_after_ns):
        counts["latest_valid"] = None
        counts["baseline_reset"] = True
    return counts


def exclusive(path: Path, data: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


@contextmanager
def query_lock(output: Path, selected_id: str, *, wait_seconds: float = 30):
    """Serialize one saved query's writers with a bounded lock wait."""
    if not ID.fullmatch(selected_id):
        raise CatalogError("invalid lock identity")
    locks = output / "locks"
    if locks.is_symlink():
        raise CatalogError("symlinked query locks refused")
    locks.mkdir(parents=True, exist_ok=True)
    path = locks / f"{selected_id.casefold()}.lock"
    try:
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    except OSError as error:
        raise CatalogError("query lock unavailable") from error
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise CatalogError("invalid query lock")
        deadline = time.monotonic() + wait_seconds
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError as error:
                if time.monotonic() >= deadline:
                    raise CatalogError("query writer busy") from error
                time.sleep(min(0.05, max(0, deadline - time.monotonic())))
        yield
    finally:
        os.close(fd)


def record(output: Path, row: dict[str, object], catalog_hash: str, raw: dict,
           metadata: dict, fixture_hash: str | None) -> Path:
    runs = output / "runs"
    if runs.is_symlink():
        raise CatalogError("symlinked runs directory refused")
    runs.mkdir(parents=True, exist_ok=True)
    run_id = f"{row['id']}--{time.time_ns()}--{secrets.token_hex(8)}"
    target = runs / run_id
    target.mkdir(exist_ok=False)
    with (target / ".writer.lock").open("xb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        raw_bytes, normalized_bytes = encoded(raw), encoded(metadata)
        exclusive(target / "raw.json", raw_bytes)
        exclusive(target / "normalized.json", normalized_bytes)
        manifest = {"version": 1, "run_id": run_id, "id": row["id"],
                    "catalog_sha256": catalog_hash, "fingerprint": row["fingerprint"],
                    "criteria": row["criteria"], "observed_at_ns": time.time_ns(),
                    "result_status": metadata["normalized"]["status"],
                    "raw_sha256": digest(raw_bytes), "normalized_sha256": digest(normalized_bytes),
                    "source_fixture_sha256": fixture_hash}
        pending = target / "manifest.pending"
        exclusive(pending, encoded(manifest))
        os.link(pending, target / "manifest.json")
        pending.unlink()
    return target


def quarantine(output: Path, run_id: str, reason: str) -> Path:
    if not RUN.fullmatch(run_id) or not reason.strip() or len(reason) > 500:
        raise CatalogError("invalid quarantine target or reason")
    with query_lock(output, RUN.fullmatch(run_id).group(1)):
        runs = output / "runs"
        run_dir = runs / run_id
        manifest = run_dir / "manifest.json"
        if (runs.is_symlink() or run_dir.is_symlink() or manifest.is_symlink()
                or not manifest.is_file()):
            raise CatalogError("quarantine requires an existing manifest")
        manifest_hash = digest(manifest.read_bytes())
        ledger = output / "quarantine"
        if ledger.is_symlink():
            raise CatalogError("symlinked quarantine directory refused")
        ledger.mkdir(parents=True, exist_ok=True)
        source = encoded({"version": 2, "run_id": run_id,
                          "manifest_sha256": manifest_hash, "reason": reason,
                          "recorded_at_ns": time.time_ns()})
        target = ledger / f"{run_id}--{digest(source)}.json"
        pending = ledger / f".pending-{secrets.token_hex(16)}"
        exclusive(pending, source)
        try:
            os.link(pending, target)
        finally:
            pending.unlink()
        return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("validate", "offline", "live", "quarantine"))
    parser.add_argument("--id")
    parser.add_argument("--fixture", type=Path, default=ROOT / "dev/fixtures/github-code-search-empty.json")
    parser.add_argument("--catalog", type=Path, default=ROOT / "dev/saved-searches.toml")
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/saved-searches")
    parser.add_argument("--run-id")
    parser.add_argument("--reason")
    args = parser.parse_args()
    try:
        output = confined(args.output)
        if args.mode == "quarantine":
            target = quarantine(output, args.run_id or "", args.reason or "")
            print(json.dumps({"quarantine": str(target)}, sort_keys=True))
            return 0
        rows, catalog_hash = catalog(args.catalog)
        selected = next((r for r in rows if r["id"] == args.id), None)
        if selected is None:
            raise CatalogError("selected ID absent from catalog")
        if args.mode == "validate":
            prior = inspect_runs(output, selected["id"])
            print(json.dumps({"id": selected["id"], "fingerprint": selected["fingerprint"],
                              "catalog_sha256": catalog_hash, "prior": prior}, sort_keys=True))
            return 0
        with query_lock(output, selected["id"]):
            prior = inspect_runs(output, selected["id"])
            fixture_hash = None
            if args.mode == "offline":
                fixture = confined(args.fixture)
                payload = fixture.read_bytes()
                status, headers, body = replay_response(
                    payload, selected["effective_query"], selected["per_page"])
                fixture_hash = digest(payload)
                transport = httpx.MockTransport(lambda request: httpx.Response(
                    status, headers=headers, content=body))
                client = GitHub("fixture", transport=transport, auto_retry=False,
                                http_cache=False, follow_redirects=False, trust_env=False, timeout=10)
                route = "fixture"
            else:
                token, route = credential()
                if not token:
                    raise CatalogError("GitHub credential route absent")
                client = GitHub(token, auto_retry=False, http_cache=False,
                                follow_redirects=False, timeout=selected["timeout_seconds"])
            with client:
                raw, metadata = search(client, route, selected["query"],
                                       selected["effective_query"], selected["per_page"])
            target = record(output, selected, catalog_hash, raw, metadata, fixture_hash)
            print(json.dumps({"receipt": str(target), "status": metadata["normalized"]["status"],
                              "prior": prior, "credential_route": route}, sort_keys=True))
            return 2 if metadata["normalized"]["status"] == "error" else 0
    except (CatalogError, OSError, ValueError) as error:
        print(f"saved-search input refused: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
