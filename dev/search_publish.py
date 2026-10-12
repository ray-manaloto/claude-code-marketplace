#!/usr/bin/env python3
"""Append a hash-bound comparison receipt for one published saved-search run."""

from __future__ import annotations

import os
from pathlib import Path
import secrets
import time

from search_catalog import CatalogError, RUN, digest, encoded, exclusive, verified_run
from search_compare import compare


def publish(output: Path, row: dict, target: Path, prior: dict | None,
            reason: str) -> tuple[Path, dict]:
    match = RUN.fullmatch(target.name)
    if not match or match.group(1) != row["id"] or target.is_symlink():
        raise CatalogError("invalid new observation")
    manifest = target / "manifest.json"
    if manifest.is_symlink() or not manifest.is_file():
        raise CatalogError("new observation manifest unavailable")
    data = manifest.read_bytes()
    try:
        value, normalized = verified_run(target, match, data)
    except (OSError, ValueError, TypeError, KeyError) as error:
        raise CatalogError("new observation changed before comparison") from error
    if value["fingerprint"] != row["fingerprint"]:
        raise CatalogError("new observation fingerprint drift")
    result = compare({"normalized": normalized}, prior, reason)
    source = encoded({"version": 1, "id": row["id"], "run_id": target.name,
                      "manifest_sha256": digest(data),
                      "normalized_sha256": value["normalized_sha256"],
                      "fingerprint": value["fingerprint"],
                      "compared_at_ns": time.time_ns(), "result": result})
    directory = output / "comparisons"
    if directory.is_symlink():
        raise CatalogError("symlinked comparison directory refused")
    directory.mkdir(parents=True, exist_ok=True)
    published = directory / f"{target.name}--{digest(source)}.json"
    pending = directory / f".pending-{secrets.token_hex(16)}"
    exclusive(pending, source)
    try:
        os.link(pending, published)
    finally:
        pending.unlink()
    return published, result
