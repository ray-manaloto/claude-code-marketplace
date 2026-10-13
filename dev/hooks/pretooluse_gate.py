#!/usr/bin/env python3
"""Claude Code PreToolUse hook: deny `git merge`, `git push` and `delivery:publish` of a failing lane.

Reads the hook JSON on stdin. For each merge/push segment of a Bash command the
lane is the branch `git name-rev MERGE_HEAD` names when a merge is in progress,
else each claude/|codex/ branch the command merges or pushes (the retro gate maps
it through the lane record's `branch`), else the current branch for a bare push.
The integration branch and `main` are never units. `delivery:publish` pushes with
`--no-verify`, so it checks the lane merges not yet on a remote, as hk pre-push
does. A refusal prints the deny JSON; an allow exits 0 with no output.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import shlex
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import git_gate  # noqa: E402

SEGMENT = re.compile(r"&&|\|\||[;|&\n]")
VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def actions(command: str):
    """Yield (verb, args, -C dir) for each git merge/push or delivery:publish segment."""
    for segment in SEGMENT.split(command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if any("delivery:publish" in token for token in tokens):
            yield "publish", [], None
            continue
        if "git" not in tokens:
            continue
        rest, directory = tokens[tokens.index("git") + 1:], None
        while rest and rest[0].startswith("-"):
            option = rest.pop(0)
            if option in VALUE_OPTIONS and rest:
                value = rest.pop(0)
                directory = value if option == "-C" else directory
        if rest and rest[0] in ("merge", "push"):
            yield rest[0], rest[1:], directory


def lanes_for(verb: str, args: list[str], repo: str) -> list[str]:
    if verb == "publish":
        return git_gate.unpublished_lanes(repo)
    if verb == "merge" and {"--abort", "--quit"} & set(args):
        return []
    if verb == "merge" and git_gate.git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD"):
        return git_gate.merging_lanes(repo)
    named = [arg.lstrip("+").split(":", 1)[0] for arg in args if not arg.startswith("-")]
    if verb == "push":  # git push [remote] [refspec...]; no refspec or HEAD means the current branch
        current = git_gate.git(repo, "branch", "--show-current") or ""
        named = [current if name == "HEAD" else name for name in named[1:]] or [current]
    return list(dict.fromkeys(filter(None, map(git_gate.lane_branch, named))))


def main() -> int:
    try:
        event = json.loads(sys.stdin.read(1 << 20) or "{}")
    except ValueError:
        return 0
    if not isinstance(event, dict) or event.get("tool_name") != "Bash":
        return 0
    command = (event.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or not re.search(
            r"\bmerge\b|\bpush\b|delivery:publish", command):
        return 0
    cwd = Path(str(event.get("cwd") or "."))
    refusals: list[str] = []
    for verb, args, directory in actions(command):
        repo = git_gate.git(cwd / directory if directory else cwd, "rev-parse", "--show-toplevel")
        if repo:
            refusals += git_gate.check_lanes(repo, lanes_for(verb, args, repo))
    if refusals:
        reason = "\n".join(refusals) + "\nWrite or fix the lane's retro record (docs/agents/ticket-retro.md)."
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
