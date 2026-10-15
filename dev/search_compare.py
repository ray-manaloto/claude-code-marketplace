#!/usr/bin/env python3
"""A05 compatible saved-search baseline and conservative NEW/GONE deltas."""

from __future__ import annotations

from pathlib import Path

from search_catalog import CatalogError, RUN, digest, quarantines, verified_run


def eligible(normalized: dict) -> bool:
    status = normalized.get("status")
    items = normalized.get("items")
    if (status not in {"complete", "empty_verified"}
            or normalized.get("control_status") != "passed"
            or normalized.get("complete_candidate") is not True
            or not isinstance(items, list)
            or any(not isinstance(item, dict) or not isinstance(item.get("identity"), str)
                   or not item["identity"]
                   for item in items)):
        return False
    identities = [item["identity"] for item in items]
    return (len(identities) == len(set(identities))
            and bool(items) == (status == "complete"))


def select_baseline(output: Path, row: dict, preflight: dict) -> tuple[dict | None, str]:
    """Recheck the exact published inventory captured by inspect_runs."""
    published = preflight.get("published")
    if not isinstance(published, dict):
        raise CatalogError("baseline requires a published-run preflight")
    excluded = quarantines(output)
    cutoff = max((when for (run_id, _), when in excluded.items()
                  if (match := RUN.fullmatch(run_id))
                  and match.group(1).casefold() == row["id"].casefold()), default=0)
    runs = output / "runs"
    best: tuple[int, str, dict] | None = None
    if runs.is_symlink():
        raise CatalogError("selected baseline changed during comparison")
    for run_id, expected_hash in published.items():
        match = RUN.fullmatch(run_id)
        if not match or match.group(1).casefold() != row["id"].casefold():
            raise CatalogError("invalid published-run preflight")
        entry = runs / run_id
        manifest = entry / "manifest.json"
        if entry.is_symlink() or not entry.is_dir() or manifest.is_symlink():
            raise CatalogError("selected baseline changed during comparison")
        if not manifest.is_file():
            raise CatalogError("selected baseline changed during comparison")
        try:
            manifest_bytes = manifest.read_bytes()
            if digest(manifest_bytes) != expected_hash:
                raise ValueError("published manifest changed")
            if (entry.name, digest(manifest_bytes)) in excluded:
                continue
            value, normalized = verified_run(entry, match, manifest_bytes)
            if value["observed_at_ns"] <= cutoff:
                continue
            if value["fingerprint"] != row["fingerprint"]:
                continue
            if not eligible(normalized):
                continue
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise CatalogError("selected baseline changed during comparison") from error
        candidate = (value["observed_at_ns"], entry.name,
                     {"run_id": entry.name, "identities": sorted(
                         item["identity"] for item in normalized["items"]),
                      "normalized_sha256": value["normalized_sha256"]})
        if best is None or candidate[:2] > best[:2]:
            best = candidate
    if best is None:
        return None, "quarantine_reset" if cutoff else "no_compatible_prior"
    return best[2], "compatible_prior"


def compare(current: dict, prior: dict | None, reason: str) -> dict:
    normalized = current["normalized"]
    if not eligible(normalized):
        return {"status": "suppressed", "reason": "current_ineligible"}
    if prior is None:
        return {"status": "baseline_established", "reason": reason}
    old = set(prior["identities"])
    new = {item["identity"] for item in normalized["items"]}
    return {"status": "compared", "baseline_run_id": prior["run_id"],
            "baseline_normalized_sha256": prior["normalized_sha256"],
            "new": sorted(new - old), "gone": sorted(old - new),
            "new_count": len(new - old), "gone_count": len(old - new)}
