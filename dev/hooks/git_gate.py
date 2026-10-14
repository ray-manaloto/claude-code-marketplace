#!/usr/bin/env python3
"""Retro gate for Git merges and pushes, plus helpers shared by the Claude Code hooks.

  git_gate.py merge   each ref being merged (hk pre-merge-commit): the arguments in
                      GIT_REFLOG_ACTION ("merge <commits>" or "pull <remote> <refs>"),
                      or MERGE_HEAD after a stopped merge. Fails closed: a source that
                      is neither the integration branch, `main` nor a lane is refused.
  git_gate.py push    each merge in @{upstream}..HEAD, else origin/<branch>..HEAD, else
                      HEAD not on any remote (hk pre-push), attributed by its default
                      subject ("Merge branch '<b>'"), else by refs pointing exactly at
                      its second parent; an unattributable merge is not gated.

A lane branch is `claude/...` or `codex/...`; the integration branch and `main`
are never units. Only exact ref names count (never `name-rev` suffixes such as
`~2` or `^2`, which name any commit reachable from a lane). Each lane runs
`dev/retro_gate.py --branch <lane>` against this checkout. Exit 0 when every
lane passes or none applies, 2 when one fails, 1 for usage. Stdlib, no network.
"""
from __future__ import annotations

import functools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

GATE = Path(__file__).resolve().parents[1] / "retro_gate.py"
PLAN_ID = os.environ.get("PLAN_ID") or "2026-10-10-marketplace-macos-reflection-scaffold"
INTEGRATION = frozenset({"codex/marketplace-native-onboarding", "main"})
REF_PREFIX = re.compile(r"^(?:refs/heads/|refs/remotes/[^/]+/|remotes/[^/]+/)")
LANE = re.compile(r"^(?:claude|codex)/[A-Za-z0-9][\w./-]*$")
MERGE_SUBJECT = re.compile(r"^Merge (?:remote-tracking )?branch '([^']+)'")
GATE_TIMEOUT = 8


@functools.cache
def git_executable() -> str | None:
    """The first git on PATH that is not a mise shim (a `mise/shims` entry, or a link to the mise
    binary; a shim costs ~0.18 s per call). None when there is none, so every git query fails
    closed. dev/retro_gate.py keeps a copy."""
    for entry in os.environ.get("PATH", os.defpath).split(os.pathsep):
        found = None if Path(entry).parts[-2:] == ("mise", "shims") else shutil.which("git", path=entry)
        if found and Path(found).resolve().name != "mise":
            return found
    return None


def git(repo, *args: str) -> str | None:
    executable = git_executable()
    if not executable:
        return None
    try:
        result = subprocess.run([executable, "-C", str(repo), *args], capture_output=True, text=True,
                                timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def ref_kind(name: str) -> tuple[str, str | None]:
    """("integration", None), ("lane", branch) or ("other", None) for an exact ref name,
    also in its `<remote>/<branch>` form."""
    name = REF_PREFIX.sub("", name.strip())
    for candidate in (name, name.split("/", 1)[-1]):
        if candidate in INTEGRATION:
            return "integration", None
        if LANE.match(candidate):
            return "lane", candidate
    return "other", None


def lane_branch(name: str) -> str | None:
    """The lane branch a ref names exactly, or None for the integration branch and other refs."""
    return ref_kind(name)[1]


def kind_at(repo, commit: str) -> tuple[str, str | None]:
    """Classify a commit by the refs pointing exactly at it; the integration branch wins,
    then a lane named by a lane record, then any lane ref."""
    sha = git(repo, "rev-parse", "-q", "--verify", f"{commit}^{{commit}}")
    refs = (git(repo, "for-each-ref", f"--points-at={sha}", "--format=%(refname)", "refs/heads", "refs/remotes")
            or "").split() if sha else []
    kinds = [ref_kind(ref) for ref in refs]
    if ("integration", None) in kinds:
        return "integration", None
    found = [branch for kind, branch in kinds if kind == "lane"]
    recorded = {lane.get("branch") for lane in lanes(repo)} if found else set()
    return next(((("lane", b)) for b in found if b in recorded), ("lane", found[0]) if found else ("other", None))


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
    except subprocess.TimeoutExpired:
        return 1, [f" - retro gate timed out after {GATE_TIMEOUT} s"]
    except OSError:
        return 1, [" - retro gate could not start"]
    lines = [line.replace(f"{repo}/", "") for line in (result.stdout + result.stderr).splitlines()
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


def merge_sources(repo) -> list[str]:
    """Refs being merged. Git writes MERGE_HEAD only after pre-merge-commit succeeds, so the
    hook reads GIT_REFLOG_ACTION, which holds the commit arguments without options."""
    if git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD"):
        msg = Path(repo, git(repo, "rev-parse", "--git-path", "MERGE_MSG") or "MERGE_MSG")
        subject = MERGE_SUBJECT.match(msg.read_text(errors="replace") if msg.is_file() else "")
        return [subject.group(1) if subject else "MERGE_HEAD"]
    verb, *args = os.environ.get("GIT_REFLOG_ACTION", "").split() or [""]
    names = [arg for arg in args if not arg.startswith("-")]
    if verb == "pull":
        return names[1:] or [git(repo, "rev-parse", "--abbrev-ref", "@{upstream}") or "@{upstream}"]
    return names if verb == "merge" else []


def classify(repo, names) -> tuple[list[str], list[str]]:
    """Split merge sources into lane branches and refs with no derivable lane."""
    found, unknown = [], []
    for name in names:
        kind, branch = ref_kind(name)
        if kind == "other":
            kind, branch = kind_at(repo, name)
        if kind == "lane":
            found.append(branch)
        elif kind == "other":
            unknown.append(name)
    return list(dict.fromkeys(found)), unknown


def merged_lane(repo, sha: str) -> str | None:
    subject = MERGE_SUBJECT.match(git(repo, "log", "-1", "--format=%s", sha) or "")
    if subject:
        return lane_branch(subject.group(1))
    return kind_at(repo, f"{sha}^2")[1]


def unpublished_lanes(repo) -> list[str]:
    current = git(repo, "branch", "--show-current")
    if git(repo, "rev-parse", "-q", "--verify", "@{upstream}"):
        span = ["@{upstream}..HEAD"]
    elif current and git(repo, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{current}"):
        span = [f"refs/remotes/origin/{current}..HEAD"]
    else:
        span = ["HEAD", "--not", "--remotes"]
    found = [merged_lane(repo, sha) for sha in (git(repo, "rev-list", "--merges", "--max-count=200", *span)
                                                 or "").split()]
    return list(dict.fromkeys(filter(None, found)))


def main(argv: list[str]) -> int:
    repo = git(Path.cwd(), "rev-parse", "--show-toplevel")
    if len(argv) != 1 or argv[0] not in ("merge", "push") or not repo:
        print("usage: git_gate.py merge|push (inside a Git checkout)", file=sys.stderr)
        return 1
    unknown: list[str] = []
    if argv[0] == "merge":
        sources = merge_sources(repo)
        branches, unknown = classify(repo, sources)
        if not sources:
            unknown = ["merge source unknown (no MERGE_HEAD or GIT_REFLOG_ACTION)"]
    else:
        branches = unpublished_lanes(repo)
    refusals = [f"retro gate refused the merge: no lane branch derivable for {name}" if " " not in name
                else f"retro gate refused the merge: {name}" for name in unknown] + check_lanes(repo, branches)
    print("\n".join(refusals) or f"retro gate passed for: {' '.join(branches) or 'no lane branch'}")
    return 2 if refusals else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
