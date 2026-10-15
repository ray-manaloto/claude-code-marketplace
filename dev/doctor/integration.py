"""Class C: an unfinished merge and index content no parent explains (C3 §C). Session-start only.

A staged blob is foreign when it matches neither HEAD, MERGE_HEAD nor Git's own merge of the two
(`git merge-tree --write-tree`); a `parent hunk: <path>` line in MERGE_MSG declares it.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

SURFACES = {"session-start"}
CONTEXT_RANK = 0


def blobs(ctx, *args) -> dict[str, str]:
    """{path: object id} from `ls-tree -r -z` or stage-0 `ls-files -s -z` output."""
    entries = (entry.split("\t", 1) for entry in (ctx.git(*args) or "").split("\0") if "\t" in entry)
    return {path: meta.split()[1 if args[0] == "ls-files" else 2] for meta, path in entries
            if args[0] != "ls-files" or meta.split()[2] == "0"}


def lane_unit(ctx, branch: str) -> str | None:
    for record in sorted((ctx.plan / "lanes").glob("*.json")):
        try:
            data = json.loads(record.read_text())
        except (OSError, ValueError):
            continue
        if isinstance(data, dict) and data.get("branch") == branch:
            return data.get("unit") or record.stem
    return None


def run(ctx):
    merge_head = (ctx.git("rev-parse", "-q", "--verify", "MERGE_HEAD") or "").strip()
    if not merge_head:
        return []
    head_file, msg_file = (Path(ctx.repo, p) for p in ctx.git("rev-parse", "--git-path", "MERGE_HEAD",
                                                               "--git-path", "MERGE_MSG").splitlines())
    branch = ((ctx.git("for-each-ref", "--points-at", merge_head, "--format=%(refname:short)", "refs/heads")
               or "").split() or [merge_head[:7]])[0]
    unit = lane_unit(ctx, branch)
    staged = [p for p in (ctx.git("diff", "--cached", "--name-only", "-z") or "").split("\0") if p]
    merged = (ctx.git("merge-tree", "--write-tree", "--no-messages", "HEAD", merge_head, codes=(0, 1)) or "").split()
    known = [blobs(ctx, "ls-tree", "-r", "-z", tree, "--", *staged) for tree in ("HEAD", merge_head, *merged[:1])]
    message = msg_file.read_text(errors="replace") if msg_file.is_file() else ""
    foreign = [path for path, blob in blobs(ctx, "ls-files", "-s", "-z", "--", *staged).items()
               if all(tree.get(path) != blob for tree in known) and f"parent hunk: {path}" not in message]
    since = datetime.fromtimestamp(head_file.stat().st_mtime, timezone.utc)
    found = [ctx.finding("C.merge-in-progress", "P1", f"MERGE_HEAD {merge_head[:7]} = {branch}"
                         + (f" (lane {unit})" if unit else ""),
                         (f"since {since:%Y-%m-%dT%H:%M:%SZ}", f"{len(staged)} staged paths",
                          f"{len(foreign)} foreign hunks" + (f": {', '.join(foreign)}" if foreign else "")),
                         "finish it with `git commit --no-edit` once the gates pass on the staged bytes, or "
                         "`git merge --abort`; nothing else touches the index first")]
    return found + [ctx.finding("C.foreign-hunk", "P2", path, ("index blob is in neither parent nor their merge",),
                                f"git diff --cached {merge_head[:7]} -- {path}; declare it with a "
                                f"`parent hunk: {path}` line in MERGE_MSG") for path in foreign]


def context_lines(ctx):
    merge = [f for f in ctx.findings if f.id == "C.merge-in-progress"]
    return [line for f in merge for line in (f"MERGE IN PROGRESS: {f.subject} · " + " · ".join(f.evidence),
                                             f"  resume: {f.fix_hint}")]
