"""A11a transfer admission: revalidate an A10 plan and freeze a guarded intent.

This module never switches a checkout. The A11b executor must revalidate the
intent and every checkout/remote preimage immediately before mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import checkout_transfer as transfer


def unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise transfer.Refusal("duplicate JSON key")
        result[key] = value
    return result


def load_plan(path: Path, expected_sha: str) -> dict[str, object]:
    if not transfer.SHA.fullmatch(expected_sha):
        raise transfer.Refusal("invalid plan SHA-256")
    if path.is_symlink() or not path.is_file():
        raise transfer.Refusal("plan file missing or symlinked")
    before = path.stat()
    if before.st_size > 4 * 1024 * 1024:
        raise transfer.Refusal("plan file too large")
    data = path.read_bytes()
    after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise transfer.Refusal("plan changed while reading")
    if hashlib.sha256(data).hexdigest() != expected_sha:
        raise transfer.Refusal("plan SHA-256 drift")
    plan = json.loads(data, object_pairs_hook=unique_pairs)
    if not isinstance(plan, dict):
        raise transfer.Refusal("plan must be an object")
    return plan


def remote_head(source: Path, branch: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", branch) or ".." in branch or "//" in branch:
        raise transfer.Refusal("invalid published branch")
    command = ["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
               "ls-remote", "--exit-code", "origin", f"refs/heads/{branch}"]
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run(command, cwd=source, env=env, capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise transfer.Refusal("remote verification unavailable") from exc
    lines = result.stdout.decode("ascii", "replace").splitlines()
    if result.returncode or len(lines) != 1:
        raise transfer.Refusal("remote verification failed")
    fields = lines[0].split("\t")
    if len(fields) != 2 or fields[1] != f"refs/heads/{branch}" or not transfer.OID.fullmatch(fields[0]):
        raise transfer.Refusal("remote branch response invalid")
    return fields[0]


def verify(plan: dict[str, object], plan_sha: str,
           expected_binding: tuple[Path, Path, str] | None = None) -> dict[str, object]:
    if plan.get("schema") != "checkout-transfer-plan-v1" or plan.get("mode") != "dry-run" or plan.get("ready_for_apply") is not True:
        raise transfer.Refusal("A10 plan is not apply-ready")
    if plan.get("collisions") or plan.get("pending_untracked"):
        raise transfer.Refusal("unresolved collision or handoff")
    source_data, old_data = plan["source"], plan["old_worktree"]
    source, old = Path(plan["writer_root_after_apply"]), Path(old_data["root"])
    if not source.is_absolute() or not old.is_absolute() or source == old or source.resolve() != Path(source_data["root"]):
        raise transfer.Refusal("invalid checkout roots")
    branch, commit = old_data["branch"], plan["published_commit"]
    expected_source, expected_old, expected_branch = expected_binding or (transfer.SOURCE, transfer.OLD, transfer.BRANCH)
    if (source.resolve(), old.resolve(), branch) != (expected_source.resolve(), expected_old.resolve(), expected_branch):
        raise transfer.Refusal("A10 plan is outside the admitted checkout binding")
    if not transfer.OID.fullmatch(commit) or commit != old_data["head"]:
        raise transfer.Refusal("published commit binding invalid")
    if old_data["common_dir"] != source_data["common_dir"] or source_data["branch"] != "main":
        raise transfer.Refusal("checkout binding invalid")
    if plan["source_environment"]["decision"] != "admit-source-preparation":
        raise transfer.Refusal("source preparation not admitted")
    inventory = plan["source_inventory"]
    untracked = {item["path"]: item["sha256"] for item in inventory["untracked"]}
    if len(untracked) != len(inventory["untracked"]) or sorted(untracked) != plan["approved_untracked"]:
        raise transfer.Refusal("source untracked handoff lacks exact approval")
    args = argparse.Namespace(source=source, old=old, commit=commit,
                              source_head=source_data["head"], branch=branch,
                              approve_untracked=[f"{name}={sha}" for name, sha in sorted(untracked.items())],
                              approvals_file=None, preparation_decision="admit-source-preparation")
    fresh = transfer.plan(args)
    if fresh != plan:
        changed = sorted(key for key in set(fresh) | set(plan) if fresh.get(key) != plan.get(key))
        raise transfer.Refusal("A10 plan preimages drifted: " + ", ".join(changed))
    if remote_head(source, branch) != commit:
        raise transfer.Refusal("published remote commit drifted")
    if transfer.identity(source) != source_data or transfer.identity(old) != old_data:
        raise transfer.Refusal("checkout changed during remote verification")
    return {
        "schema": "checkout-apply-intent-v1", "mode": "preparation-only",
        "plan_sha256": plan_sha, "source": source_data, "old_worktree": old_data,
        "published_commit": commit, "remote_ref": f"refs/heads/{branch}",
        "approved_untracked": untracked,
        "retained_old_dirty": plan["old_worktree_inventory"]["dirty"],
        "retained_old_ignored": plan["old_worktree_inventory"]["ignored"],
        "required_source_commands": ["tools:prepare", "deps:sync", "deps:check",
                                     "check", "check:acceptance-baseline"],
        "recovery": "A11b must journal each phase, preserve both roots, and restore old branch ownership without reset/delete when safe; otherwise stop for inspected recovery",
    }


def create_intent(path: Path, intent: dict[str, object], roots: tuple[Path, Path]) -> None:
    resolved_parent = path.parent.resolve()
    if not resolved_parent.is_dir() or path.is_symlink() or any(resolved_parent == root.resolve() or root.resolve() in resolved_parent.parents for root in roots):
        raise transfer.Refusal("intent must be a new file outside both checkouts")
    data = (json.dumps(intent, sort_keys=True, indent=2) + "\n").encode()
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    except FileExistsError as exc:
        raise transfer.Refusal("existing intent requires inspection before retry") from exc
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(resolved_parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare",))
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--intent-file", type=Path, required=True)
    args = parser.parse_args()
    try:
        plan = load_plan(args.plan_file, args.plan_sha256)
        intent = verify(plan, args.plan_sha256)
        create_intent(args.intent_file, intent, (Path(intent["source"]["root"]), Path(intent["old_worktree"]["root"])))
        print(json.dumps({"status": "PREPARED_ONLY", "intent_file": str(args.intent_file.resolve()),
                          "intent_sha256": hashlib.sha256(args.intent_file.read_bytes()).hexdigest()}, sort_keys=True))
        return 0
    except (transfer.Refusal, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"A11a refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
