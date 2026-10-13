#!/usr/bin/env python3
"""Retro gate for Git merges and pushes, plus helpers shared by the Claude Code hooks.

  git_gate.py merge   the lane branch being merged: `git name-rev MERGE_HEAD`, or the
                      merge arguments in GIT_REFLOG_ACTION (hk pre-merge-commit)
  git_gate.py push    the second parent of each lane merge in @{upstream}..HEAD,
                      else origin/<branch>..HEAD, else HEAD not on any remote (hk pre-push)

A lane branch is `claude/...` or `codex/...`; the integration branch and `main`
are never units, so merging them in is not gated. Each lane runs
`dev/retro_gate.py --branch <lane>` against this checkout. Exit 0 when every
lane passes or none applies, 2 when one fails, 1 for usage. Stdlib, no network.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

GATE = Path(__file__).resolve().parents[1] / "retro_gate.py"
PLAN_ID = os.environ.get("PLAN_ID") or "2026-10-10-marketplace-macos-reflection-scaffold"
INTEGRATION = frozenset({"codex/marketplace-native-onboarding", "main"})
LANE = re.compile(r"^(?:refs/heads/|refs/remotes/[^/]+/|remotes/[^/]+/|[^/\s]+/)?"
                  r"((?:claude|codex)/[A-Za-z0-9][\w./-]*?)(?:[~^]\d*)*$")
MERGE_SUBJECT = re.compile(r"^Merge (?:remote-tracking )?branch '([^']+)'")
GATE_TIMEOUT = 8


def git(repo, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                                timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def lane_branch(name: str) -> str | None:
    """The lane branch a ref names, or None for the integration branch and non-lane refs."""
    match = LANE.match(name.strip())
    return match.group(1) if match and match.group(1) not in INTEGRATION else None


def lanes(repo) -> list[dict]:
    found = []
    for path in sorted((Path(repo) / ".planning" / PLAN_ID / "lanes").glob("*.json")):
        try:
            lane = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(lane, dict) and isinstance(lane.get("unit"), str):
            found.append(lane)
    return found


def run_gate(repo, *args: str) -> tuple[int, list[str]]:
    """Run the retro gate; reasons exclude the selectors line. A timeout fails closed."""
    try:
        result = subprocess.run([sys.executable, "-I", str(GATE), "--repo", str(repo), "--plan-id", PLAN_ID,
                                 *args], capture_output=True, text=True, timeout=GATE_TIMEOUT, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, [f"retro gate did not complete: {exc}"]
    lines = [line for line in (result.stdout + result.stderr).splitlines()
             if line.strip() and not line.startswith("selectors:")]
    return result.returncode, lines


def check_lanes(repo, branches) -> list[str]:
    """Gate each lane branch; return one refusal block per failing lane."""
    refusals = []
    for branch in branches:
        rc, lines = run_gate(repo, "--branch", branch)
        if rc:
            refusals.append("\n".join([f"retro gate refused {branch}:", *lines]))
    return refusals


def merging_lanes(repo) -> list[str]:
    """Lanes being merged. Git writes MERGE_HEAD only after pre-merge-commit succeeds, so the
    hook reads the merge arguments from GIT_REFLOG_ACTION ("merge <args>") instead."""
    if git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD"):
        names = ["MERGE_HEAD"]
    else:
        action = os.environ.get("GIT_REFLOG_ACTION", "").split()
        names = [arg for arg in action[1:] if not arg.startswith("-")] if action[:1] == ["merge"] else []
    found = [lane_branch(name) or lane_branch(git(repo, "name-rev", "--name-only", "--exclude=refs/tags/*", name)
                                              or "") for name in names]
    return list(dict.fromkeys(filter(None, found)))


def unpublished_lanes(repo) -> list[str]:
    current = git(repo, "branch", "--show-current")
    if git(repo, "rev-parse", "-q", "--verify", "@{upstream}"):
        span = ["@{upstream}..HEAD"]
    elif current and git(repo, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{current}"):
        span = [f"refs/remotes/origin/{current}..HEAD"]
    else:
        span = ["HEAD", "--not", "--remotes"]
    found: list[str] = []
    for sha in (git(repo, "rev-list", "--merges", "--max-count=200", *span) or "").split():
        name = git(repo, "name-rev", "--name-only", "--exclude=refs/tags/*", f"{sha}^2") or ""
        subject = MERGE_SUBJECT.match(git(repo, "log", "-1", "--format=%s", sha) or "")
        branch = lane_branch(name) or (lane_branch(subject.group(1)) if subject else None)
        if branch and branch not in found:
            found.append(branch)
    return found


def main(argv: list[str]) -> int:
    repo = git(Path.cwd(), "rev-parse", "--show-toplevel")
    if len(argv) != 1 or argv[0] not in ("merge", "push") or not repo:
        print("usage: git_gate.py merge|push (inside a Git checkout)", file=sys.stderr)
        return 1
    branches = merging_lanes(repo) if argv[0] == "merge" else unpublished_lanes(repo)
    refusals = check_lanes(repo, branches)
    print("\n".join(refusals) or f"retro gate passed for: {' '.join(branches) or 'no lane branch'}")
    return 2 if refusals else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
