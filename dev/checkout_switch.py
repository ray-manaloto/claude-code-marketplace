"""A11b guarded source switch. Never resets, deletes, prepares or publishes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import checkout_apply as admission
import checkout_transfer as transfer


def record(directory: Path, phase: str, **fields: object) -> None:
    data = (json.dumps({"phase": phase, **fields}, sort_keys=True) + "\n").encode()
    fd = os.open(directory / f"{phase}.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    parent_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def new_journal(path: Path, source: Path, old: Path) -> Path:
    parent = path.parent.resolve()
    if not parent.is_dir() or path.is_symlink() or any(
        parent == root.resolve() or root.resolve() in parent.parents for root in (source, old)
    ):
        raise transfer.Refusal("journal must be new and outside both checkouts")
    try:
        path.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise transfer.Refusal("existing journal requires inspected recovery") from exc
    fd = os.open(parent, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return path


def git_change(root: Path, *args: str) -> None:
    command = ["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *args]
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise transfer.Refusal("Git checkout operation unavailable") from exc
    if result.returncode:
        raise transfer.Refusal(f"Git checkout operation returned {result.returncode}")


def read_intent(path: Path, sha: str) -> dict[str, object]:
    return admission.load_plan(path, sha)


def preflight(plan: dict[str, object], plan_sha: str, intent: dict[str, object],
              binding: tuple[Path, Path, str]) -> None:
    if admission.verify(plan, plan_sha, binding) != intent:
        raise transfer.Refusal("A11a intent differs from freshly verified A10 plan")


def preserved_old(old: Path, plan: dict[str, object], branch: str) -> bool:
    ident = transfer.identity(old)
    expected = plan["old_worktree"]
    current = transfer.inventory(old)
    return (ident["branch"] == branch and ident["head"] == expected["head"]
            and ident["common_dir"] == expected["common_dir"]
            and current == {**plan["old_worktree_inventory"], "tracked": current["tracked"]}
            and ident["index_sha256"] == expected["index_sha256"]
            and ident["status_sha256"] == expected["status_sha256"])


def verify_post(source: Path, old: Path, plan: dict[str, object]) -> None:
    branch, commit = plan["old_worktree"]["branch"], plan["published_commit"]
    source_id, old_id = transfer.identity(source), transfer.identity(old)
    if (source_id["branch"], source_id["head"], old_id["branch"], old_id["head"]) != (
        branch, commit, "", commit
    ):
        raise transfer.Refusal("post-switch branch or HEAD mismatch")
    if source_id["common_dir"] != old_id["common_dir"]:
        raise transfer.Refusal("post-switch Git common directory mismatch")
    source_items = transfer.inventory(source)
    before = plan["source_inventory"]
    if (source_items["untracked"], source_items["ignored"]) != (before["untracked"], before["ignored"]):
        raise transfer.Refusal("source retained content changed during switch")
    transfer.require_clean_tracked(source, source_items["tracked"])
    if not preserved_old_detached(old, plan):
        raise transfer.Refusal("retained old worktree changed during switch")


def preserved_old_detached(old: Path, plan: dict[str, object]) -> bool:
    ident = transfer.identity(old)
    expected = plan["old_worktree"]
    current = transfer.inventory(old)
    return (ident["branch"] == "" and ident["head"] == expected["head"]
            and ident["common_dir"] == expected["common_dir"]
            and ident["index_sha256"] == expected["index_sha256"]
            and ident["status_sha256"] == expected["status_sha256"]
            and {key: value for key, value in current.items() if key != "tracked"}
            == plan["old_worktree_inventory"])


def recover_if_safe(source: Path, old: Path, plan: dict[str, object]) -> bool:
    """Only reattach untouched old owner while source is still at its preimage."""
    try:
        source_id = transfer.identity(source)
        if source_id != plan["source"] or transfer.inventory(source) != plan["source_inventory"]:
            return False
        transfer.require_clean_tracked(source, plan["source_inventory"]["tracked"])
        if not preserved_old_detached(old, plan):
            return False
        branch = plan["old_worktree"]["branch"]
        if transfer.git(old, "rev-parse", f"refs/heads/{branch}").decode().strip() != plan["published_commit"]:
            return False
        git_change(old, "switch", "--no-guess", branch)
        return preserved_old(old, plan, branch)
    except (transfer.Refusal, OSError, ValueError, KeyError, TypeError):
        return False


def execute(plan_file: Path, plan_sha: str, intent_file: Path, intent_sha: str,
            journal_path: Path, binding: tuple[Path, Path, str]) -> dict[str, str]:
    plan = admission.load_plan(plan_file, plan_sha)
    intent = read_intent(intent_file, intent_sha)
    source, old, branch = binding
    preflight(plan, plan_sha, intent, binding)
    if (Path(intent["source"]["root"]).resolve(), Path(intent["old_worktree"]["root"]).resolve()) != (source.resolve(), old.resolve()):
        raise transfer.Refusal("intent roots differ from admitted binding")
    journal = new_journal(journal_path, source, old)
    record(journal, "admitted", plan_sha256=plan_sha, intent_sha256=intent_sha,
           source=str(source), old_worktree=str(old), branch=branch,
           published_commit=plan["published_commit"])
    try:
        if (admission.load_plan(plan_file, plan_sha), read_intent(intent_file, intent_sha)) != (plan, intent):
            raise transfer.Refusal("A10 plan or A11a intent changed before mutation")
        preflight(plan, plan_sha, intent, binding)
        record(journal, "detach_started")
        git_change(old, "switch", "--detach", plan["published_commit"])
        if not preserved_old_detached(old, plan):
            raise transfer.Refusal("old worktree drift after detach")
        record(journal, "detached")
        # Revalidate source and the remote after releasing branch ownership.
        if transfer.identity(source) != plan["source"] or transfer.inventory(source) != plan["source_inventory"]:
            raise transfer.Refusal("source drift after detach")
        if admission.remote_head(source, branch) != plan["published_commit"]:
            raise transfer.Refusal("remote drift after detach")
        record(journal, "switch_started")
        git_change(source, "switch", "--no-guess", branch)
        record(journal, "switched")
        verify_post(source, old, plan)
        record(journal, "verified", source_head=transfer.identity(source)["head"])
        return {"status": "SWITCHED", "journal": str(journal.resolve())}
    except (transfer.Refusal, OSError, ValueError, KeyError, TypeError) as exc:
        recovered = recover_if_safe(source, old, plan)
        phase = "recovered" if recovered else "recovery_required"
        record(journal, phase, reason=str(exc), inspected_recovery=not recovered)
        raise transfer.Refusal(f"{exc}; {phase}; inspect {journal.resolve()}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("switch",))
    parser.add_argument("--plan-file", type=Path, required=True)
    parser.add_argument("--plan-sha256", required=True)
    parser.add_argument("--intent-file", type=Path, required=True)
    parser.add_argument("--intent-sha256", required=True)
    parser.add_argument("--journal-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = execute(args.plan_file, args.plan_sha256, args.intent_file,
                         args.intent_sha256, args.journal_dir,
                         (transfer.SOURCE, transfer.OLD, transfer.BRANCH))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (transfer.Refusal, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"A11b refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
