"""Read-only A10 inventory and transfer plan; never switches a checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

SOURCE = Path("/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace")
OLD = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
BRANCH = "codex/marketplace-native-onboarding"
OID = re.compile(r"[0-9a-f]{40}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_IGNORED_COUNT = 10_000
MAX_IGNORED_BYTES = 256 * 1024 * 1024
MAX_IGNORED_SECONDS = 30


class Refusal(Exception):
    pass


def run(argv: list[str], root: Path) -> bytes:
    try:
        done = subprocess.run(argv, cwd=root, capture_output=True, check=False, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Refusal(f"cannot execute {argv[0]}") from exc
    if done.returncode:
        raise Refusal(f"{argv[0]} returned {done.returncode}")
    return done.stdout


def git(root: Path, *args: str) -> bytes:
    return run(["git", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null", *args], root)


def paths(root: Path, *args: str) -> list[str]:
    return sorted(os.fsdecode(item) for item in git(root, *args).split(b"\0") if item)


def identity(root: Path) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise Refusal("checkout root missing or symlinked")
    top = Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve()
    if top != root.resolve():
        raise Refusal("checkout root mismatch")
    common = Path(os.fsdecode(git(root, "rev-parse", "--git-common-dir")).strip())
    return {
        "root": str(top),
        "head": git(root, "rev-parse", "HEAD").decode("ascii").strip(),
        "branch": git(root, "branch", "--show-current").decode("utf-8").strip(),
        "common_dir": str((root / common).resolve() if not common.is_absolute() else common.resolve()),
        "index_sha256": hashlib.sha256(git(root, "ls-files", "--stage", "-z")).hexdigest(),
        "status_sha256": hashlib.sha256(git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")).hexdigest(),
    }


def entry(root: Path, relative: str, deadline: float | None = None, byte_budget: int | None = None) -> dict[str, object]:
    path = root / relative
    mode = path.lstat().st_mode
    result: dict[str, object] = {"path": relative, "mode": stat.S_IMODE(mode)}
    if stat.S_ISLNK(mode):
        target = os.readlink(path)
        result.update(kind="symlink", sha256=hashlib.sha256(os.fsencode(target)).hexdigest(), target=target)
    elif stat.S_ISREG(mode):
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(descriptor, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise Refusal("file type changed during inventory")
            content_hash = hashlib.sha256()
            read_bytes = 0
            while True:
                if deadline is not None and time.monotonic() > deadline:
                    raise Refusal("ignored content inventory time limit exceeded")
                block = stream.read(1024 * 1024)
                if not block:
                    break
                read_bytes += len(block)
                if byte_budget is not None and read_bytes > byte_budget:
                    raise Refusal("ignored byte limit exceeded during inventory")
                content_hash.update(block)
            digest = content_hash.hexdigest()
            after = os.fstat(stream.fileno())
        current = path.lstat()
        if read_bytes != before.st_size or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) or (before.st_dev, before.st_ino) != (current.st_dev, current.st_ino):
            raise Refusal("file changed during inventory")
        result.update(kind="file", bytes=read_bytes, sha256=digest)
    elif stat.S_ISDIR(mode):
        result["kind"] = "directory"
    else:
        raise Refusal("unsupported filesystem entry")
    return result


def inventory(root: Path) -> dict[str, object]:
    tracked = paths(root, "ls-files", "-z")
    untracked = paths(root, "ls-files", "--others", "--exclude-standard", "-z")
    ignored = paths(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z")
    dirty = paths(root, "diff", "--name-only", "-z", "HEAD")
    # Hash ignored contents only within fixed count, byte and time limits.
    if len(ignored) > MAX_IGNORED_COUNT:
        raise Refusal("ignored entry count limit exceeded")
    ignored_bytes = sum((root / name).lstat().st_size for name in ignored if stat.S_ISREG((root / name).lstat().st_mode))
    if ignored_bytes > MAX_IGNORED_BYTES:
        raise Refusal("ignored byte limit exceeded")
    deadline = time.monotonic() + MAX_IGNORED_SECONDS
    retained: dict[str, dict[str, object]] = {}
    digest = hashlib.sha256()
    consumed_bytes = 0
    for name in ignored:
        if time.monotonic() > deadline:
            raise Refusal("ignored content inventory time limit exceeded")
        node = root / name
        info = node.lstat()
        bucket = name.split("/", 1)[0]
        category = {".mise": "managed-tools-retain", ".venv": "python-environment-retain",
                    ".cache": "cache-retain", "dev": "generated-development-retain",
                    "evidence": "local-evidence-retain"}.get(bucket, "unclassified-retain")
        row = retained.setdefault(bucket, {"count": 0, "bytes": 0, "classification": category})
        row["count"] = int(row["count"]) + 1
        row["bytes"] = int(row["bytes"]) + (info.st_size if stat.S_ISREG(info.st_mode) else 0)
        record = entry(root, name, deadline, MAX_IGNORED_BYTES - consumed_bytes)
        consumed_bytes += int(record.get("bytes", 0))
        digest.update(json.dumps(record, sort_keys=True).encode("utf-8") + b"\0")
    return {
        "tracked_count": len(tracked), "tracked": tracked,
        "untracked": [entry(root, name) for name in untracked],
        "dirty": [entry(root, name) if os.path.lexists(root / name) else {"path": name, "kind": "deleted"} for name in dirty],
        "ignored": {"count": len(ignored), "bytes": ignored_bytes, "content_manifest_sha256": digest.hexdigest(),
                    "limits": {"count": MAX_IGNORED_COUNT, "bytes": MAX_IGNORED_BYTES, "seconds": MAX_IGNORED_SECONDS},
                    "retained_by_root": retained},
    }


def require_clean_tracked(root: Path, tracked: list[str]) -> None:
    """Compare source bytes with HEAD even when Git status flags hide edits."""
    records = git(root, "ls-tree", "-r", "-z", "HEAD").split(b"\0")
    expected: list[bytes] = []
    names: list[str] = []
    deadline = time.monotonic() + 30
    for record in records:
        if not record:
            continue
        meta, raw_name = record.split(b"\t", 1)
        mode, kind, oid = meta.split()
        if kind != b"blob" or mode not in (b"100644", b"100755", b"120000"):
            raise Refusal("unsupported tracked source entry")
        name = os.fsdecode(raw_name)
        names.append(name)
        expected.append(mode + b" " + oid + b" 0\t" + raw_name + b"\0")
        current = entry(root, name, deadline)
        current_mode = b"120000" if current["kind"] == "symlink" else (b"100755" if int(current["mode"]) & 0o111 else b"100644")
        if current_mode != mode:
            raise Refusal("tracked source mode changed")
        original = git(root, "cat-file", "blob", oid.decode("ascii"))
        if current["sha256"] != hashlib.sha256(original).hexdigest():
            raise Refusal("tracked source content changed")
    if sorted(names) != tracked or git(root, "ls-files", "--stage", "-z") != b"".join(expected):
        raise Refusal("tracked source index differs from HEAD")


def probe(source: Path) -> dict[str, str]:
    script = Path(__file__).resolve()
    result = run([sys.executable, "-B", str(script), "probe", "--source", str(source)], source)
    proof = json.loads(result)
    if proof["executing_cwd"] != str(source.resolve()):
        raise Refusal("source-root execution probe failed")
    return proof


def plan(args: argparse.Namespace) -> dict[str, object]:
    source, old = Path(os.path.abspath(args.source)), Path(os.path.abspath(args.old))
    if source == old or not args.commit or not args.source_head or not OID.fullmatch(args.commit) or not OID.fullmatch(args.source_head):
        raise Refusal("invalid transfer binding")
    src_id, old_id = identity(source), identity(old)
    if (src_id["head"], src_id["branch"], old_id["head"], old_id["branch"]) != (args.source_head, "main", args.commit, args.branch):
        raise Refusal("checkout branch or HEAD drift")
    if src_id["common_dir"] != old_id["common_dir"] or git(old, "rev-parse", f"refs/remotes/origin/{args.branch}").decode().strip() != args.commit:
        raise Refusal("common Git directory or published tracking ref drift")
    source_items, old_items = inventory(source), inventory(old)
    if source_items["dirty"]:
        raise Refusal("source tracked files are dirty")
    require_clean_tracked(source, source_items["tracked"])
    target = paths(old, "ls-tree", "-r", "--name-only", "-z", args.commit)
    tracked = set(source_items["tracked"])
    collisions: list[dict[str, str]] = []
    for name in target:
        node = source / name
        if os.path.lexists(node) and name not in tracked:
            collisions.append({"path": name, "reason": "target tracked path occupied outside source index"})
        for parent in Path(name).parents:
            if str(parent) == ".":
                break
            ancestor = source / parent
            if os.path.lexists(ancestor) and not stat.S_ISDIR(ancestor.lstat().st_mode):
                collisions.append({"path": str(parent), "reason": "target parent is not a directory"})
    if collisions:
        raise Refusal("target tracked path collision: " + json.dumps(collisions[:10], sort_keys=True))
    approvals = dict(item.split("=", 1) for item in args.approve_untracked)
    if len(approvals) != len(args.approve_untracked):
        raise Refusal("duplicate untracked approval")
    if args.approvals_file:
        recorded = json.loads(args.approvals_file.read_text())
        if not isinstance(recorded, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in recorded.items()):
            raise Refusal("approval file must map paths to SHA-256 values")
        if set(recorded) & set(approvals):
            raise Refusal("duplicate untracked approval")
        approvals.update(recorded)
    if any(not SHA.fullmatch(value) for value in approvals.values()):
        raise Refusal("invalid untracked approval")
    source_untracked = {item["path"]: item["sha256"] for item in source_items["untracked"]}
    if any(source_untracked.get(path) != sha for path, sha in approvals.items()):
        raise Refusal("untracked approval does not match current source bytes")
    environment = {}
    for name in (".mise", ".venv"):
        location = source / name
        kind = "absent" if not os.path.lexists(location) else ("directory" if stat.S_ISDIR(location.lstat().st_mode) else "unsafe")
        if kind == "unsafe":
            raise Refusal("source environment path is not a directory")
        environment[name] = kind
    if identity(source) != src_id or identity(old) != old_id:
        raise Refusal("checkout changed during inventory")
    execution = probe(source)
    fresh_source = inventory(source)
    if fresh_source != source_items or identity(source) != src_id:
        raise Refusal("source changed during planning")
    require_clean_tracked(source, fresh_source["tracked"])
    return {
        "schema": "checkout-transfer-plan-v1", "mode": "dry-run", "published_commit": args.commit,
        "source": src_id, "old_worktree": old_id, "source_inventory": source_items,
        "old_worktree_inventory": {key: value for key, value in old_items.items() if key != "tracked"},
        "target_tracked_count": len(target), "collisions": collisions,
        "approved_untracked": sorted(approvals),
        "pending_untracked": sorted(set(source_untracked) - approvals.keys()),
        "source_environment": {"observed": environment, "decision": args.preparation_decision,
                               "required_after_switch": ["./dev/mise run tools:prepare", "./dev/mise run deps:sync",
                                                         "./dev/mise run deps:check"],
                               "A11_verification": "recheck source-root tool and dependency identity before checks; presence alone is insufficient"},
        "writer_root_after_apply": str(source), "execution_probe": execution,
        "publication_binding": "local origin tracking ref only; A11 must verify remote again",
        "current_guidance": {"paths": ["AGENTS.md", "docs/onboarding.md", "docs/accepted-decisions.md",
                                        "docs/agents/codex-task-orchestration.md"],
                             "classification": "review live path references after source-root transfer; preserve historical receipts"},
        "apply": ["A11 recheck all identities, inventory digests, approvals and remote commit",
                  "retain ignored artifacts in old worktree; never rebuild implicitly",
                  "detach old branch owner only after review; switch source to published branch",
                  "from source root run admitted tools:prepare, deps:sync and deps:check before later checks",
                  "run named checks and A09 handoff update from source root"],
        "recovery": ["on drift, stop before switching", "if switch fails, preserve both checkouts and old branch binding; re-inventory before retry",
                     "if source preparation fails, preserve old .mise/.venv, stop named checks, repair source environment under A11 admission"],
        "ready_for_apply": not (set(source_untracked) - approvals.keys()) and args.preparation_decision == "admit-source-preparation",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "probe"))
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--old", type=Path, default=OLD)
    parser.add_argument("--commit")
    parser.add_argument("--source-head")
    parser.add_argument("--branch", default=BRANCH)
    parser.add_argument("--approve-untracked", action="append", default=[])
    parser.add_argument("--approvals-file", type=Path)
    parser.add_argument("--preparation-decision", choices=("hold", "admit-source-preparation"), default="hold")
    args = parser.parse_args()
    try:
        if args.action == "probe":
            if Path.cwd().resolve() != args.source.resolve():
                raise Refusal("probe must execute from source checkout")
            output = {"executing_cwd": str(Path.cwd().resolve()), "git_root": os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel")).strip(),
                      "git_head": git(Path.cwd(), "rev-parse", "HEAD").decode("ascii").strip()}
        else:
            output = plan(args)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except (Refusal, OSError, ValueError, KeyError) as exc:
        print(f"A10 refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
