#!/usr/bin/env python3
"""Deterministic retrospective gate for one ticket/unit.

A unit may be integrated or published only when its retro record exists and
binds real evidence. This checks the record mechanically so the gate is the
same for a human, Claude, Codex or CI:

  * the record `.planning/<PLAN_ID>/retros/<unit>.md` exists;
  * every retro category is addressed (a finding row or an explicit
    "none"/"no finding" statement): navigation, automated checks, coding
    standards, steering/global guidance, tool economy, no-ops, information
    access;
  * at least one verification binding is present (an exit code such as
    `rc 0`, `PASS`, a SHA-256, or a named check);
  * no finding is left open: a table row that says pending/TODO/open must name
    a deferral owner, an external blocker, or a separate ticket.

The unit comes from --unit, $RETRO_UNIT, --from-merge-head (the branch that
`git name-rev MERGE_HEAD` names) or the current `claude|codex/<unit>-<slug>`
branch. A branch is matched against a lane record's `branch` field first, then
against existing records by its longest hyphen-separated prefix.

Exit 0 when the gate passes, 2 with one reason per line when it does not,
1 for usage errors. The last stdout line names the runtime selectors present
in the environment (names only). Judgement about the findings themselves stays
with the independent reviewer; this only refuses a missing or unresolved record.
"""
from __future__ import annotations

import argparse
import functools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

DEFAULT_PLAN_ID = "2026-10-10-marketplace-macos-reflection-scaffold"
SELECTORS = ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "MARKETPLACE_PYTHON")
CATEGORIES = {
    "navigation": r"\bnavigation\b",
    "automated checks": r"\bautomated[- ]checks?\b",
    "coding standards": r"\bcoding standards?\b",
    "steering/global guidance": r"\bsteering\b|\bglobal (agents|guidance|instructions)\b|\bAGENTS\.md\b",
    "tool economy": r"\btool economy\b",
    "no-ops": r"\bno-ops?\b",
    "information access": r"\binformation access\b",
}
# PASS is case-sensitive so that prose such as "passes" is not a receipt.
EVIDENCE = re.compile(
    r"\bPASS(ED)?\b|\b[0-9a-f]{64}\b|(?i:\b(rc[ =]?0|exit(ed|s)?( code)?[ =]?0|returned 0)\b|`check`|"
    r"check:acceptance-baseline|tasks validate|19 (original |baseline )?(file )?hash(es)?|"
    r"\btests? pass(ed)?\b|\ball \d+ tests\b)"
)
# Open-state words count only in a row's last (disposition) cell; a trailing
# hyphen marks a compound word ("pending-file race"), not a state.
OPEN = re.compile(r"\b(pending|todo|tbd|open finding|unresolved|not yet applied)\b(?!-)", re.I)
RESOLVED_OPEN = re.compile(
    r"\b(deferred|owner|blocker|held|external|separate (ticket|unit|operation|owner)|future ticket #?\d+|"
    r"A\d{2}[ab]?\b|remains partial|partial)\b|(?<!\w)#\d+",
    re.I,
)
MAX_RECORD_BYTES = 1 << 20
UNDERIVABLE = "unit could not be derived; pass --unit or --branch"
BRANCH = re.compile(r"^(?:claude|codex)/([A-Za-z0-9][A-Za-z0-9-]*)")


class UsageError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError(f"{self.prog}: error: {message}")


@functools.cache
def git_executable() -> str | None:
    """The first git on PATH that is not a mise shim (a `mise/shims` entry, or a link to the mise
    binary; a shim costs ~0.18 s per call). None when there is none, so every git query fails
    closed. A copy of dev/hooks/git_gate.git_executable; the two files import nothing from each other."""
    for entry in os.environ.get("PATH", os.defpath).split(os.pathsep):
        found = None if Path(entry).parts[-2:] == ("mise", "shims") else shutil.which("git", path=entry)
        if found and Path(found).resolve().name != "mise":
            return found
    return None


def git(repo: Path, *args: str) -> str | None:
    executable = git_executable()
    if not executable:
        return None
    try:
        result = subprocess.run([executable, "-C", str(repo), *args], capture_output=True, text=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def lane_unit(plan_dir: Path, branch: str) -> str | None:
    for path in sorted((plan_dir / "lanes").glob("*.json")):
        try:
            lane = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(lane, dict) and lane.get("branch") == branch and isinstance(lane.get("unit"), str):
            return lane["unit"]
    return None


def unit_from_branch(branch: str, plan_dir: Path) -> str | None:
    """Prefer a lane record naming the branch, then the longest existing record prefix."""
    branch = re.sub(r"([~^]\d*)+$", "", re.sub(r"^(remotes/[^/]+/|heads/)", "", branch.strip()))
    match = BRANCH.match(branch)
    if not match:
        return None
    parts = match.group(1).split("-")
    candidates = ["-".join(parts[:n]) for n in range(len(parts), 0, -1)]
    lane = lane_unit(plan_dir, branch)
    if lane:
        candidates.insert(0, lane)
    for candidate in candidates:
        if (plan_dir / "retros" / f"{candidate}.md").is_file():
            return candidate
    return lane


def derive_unit(args, repo: Path, plan_dir: Path) -> str:
    """Precedence: --unit, --branch, --from-merge-head, $RETRO_UNIT, then the current branch."""
    if args.unit:
        return args.unit
    if args.branch is not None:
        name = args.branch
    elif args.from_merge_head:
        if git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD") is None:
            raise UsageError("--from-merge-head: no merge in progress (MERGE_HEAD is absent)")
        name = git(repo, "name-rev", "--name-only", "MERGE_HEAD") or ""
    else:
        env = os.environ.get("RETRO_UNIT") or os.environ.get("CLAUDE_LANE_UNIT")
        if env:
            return env
        name = git(repo, "branch", "--show-current") or ""
    unit = unit_from_branch(name, plan_dir)
    if not unit:
        raise UsageError(f"{UNDERIVABLE} (branch {name!r} matches no lane record or retro record)")
    return unit


def open_without_owner(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|") if cell.strip()]
    last = cells[-1] if cells else ""
    return bool(OPEN.search(last)) and not RESOLVED_OPEN.search(line) and not EVIDENCE.search(last)


def check_record(path: Path) -> list[str]:
    try:
        if path.stat().st_size > MAX_RECORD_BYTES:
            return ["retro record larger than 1 MiB"]
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"retro record missing: {path} ({exc.strerror or exc})"]
    except UnicodeDecodeError as exc:
        return [f"retro record unreadable: {path} ({exc.reason})"]
    reasons: list[str] = []
    if len(text.strip()) < 200:
        reasons.append("retro record is shorter than 200 characters")
    flat = " ".join(text.split())  # a category or binding may wrap across lines
    for name, pattern in CATEGORIES.items():
        if not re.search(pattern, flat, re.I):
            reasons.append(f"category not addressed: {name}")
    if not EVIDENCE.search(flat):
        reasons.append("no verification binding (exit code, PASS, SHA-256 or named check) found")
    for line in text.splitlines():
        if line.startswith("|") and open_without_owner(line):
            reasons.append(f"open finding without owner/blocker: {line.strip()[:120]}")
    return reasons


def run(argv: list[str]) -> int:
    ap = Parser(prog="retro_gate.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unit", help="unit id; defaults to $RETRO_UNIT or the claude/<unit>-<slug> branch name")
    ap.add_argument("--branch", help="derive the unit from this branch name (hooks without MERGE_HEAD)")
    ap.add_argument("--from-merge-head", action="store_true", help="derive the unit from the branch being merged")
    ap.add_argument("--repo", help="repository root (default: the Git top level of the working directory)")
    ap.add_argument("--plan-id", default=os.environ.get("PLAN_ID") or DEFAULT_PLAN_ID)
    ap.add_argument("--record", help="explicit record path (overrides unit/plan lookup)")
    ap.add_argument("--all", nargs="?", const="", metavar="DIR",
                    help="check every record in DIR or the plan's retros directory (calibration)")
    a = ap.parse_args(argv)
    if a.record:
        return report(Path(a.record))
    if a.all:
        return calibrate(Path(a.all))
    repo = Path(a.repo or git(Path.cwd(), "rev-parse", "--show-toplevel") or Path.cwd())
    if not repo.is_dir():
        raise UsageError(f"--repo is not a directory: {repo}")
    plan_dir = repo / ".planning" / a.plan_id
    if a.all is not None:
        return calibrate(plan_dir / "retros")
    return report(plan_dir / "retros" / f"{derive_unit(a, repo, plan_dir)}.md")


def calibrate(retros: Path) -> int:
    if not retros.is_dir():
        raise UsageError(f"--all: not a directory: {retros}")
    names = sorted(p.name for p in retros.glob("*.md"))
    failed = 0
    for name in names:
        reasons = check_record(retros / name)
        failed += bool(reasons)
        print(f"{'FAIL' if reasons else 'PASS'} {name}")
        for reason in reasons:
            print(f"   - {reason}")
    print(f"{failed} failing of {len(names)}")
    return 2 if failed else 0


def report(record: Path) -> int:
    reasons = check_record(record)
    if reasons:
        print(f"RETRO GATE FAILED for {record}")
        for reason in reasons:
            print(f" - {reason}")
        return 2
    print(f"RETRO GATE PASSED: {record}")
    return 0


def main() -> int:
    try:
        code = run(sys.argv[1:])
    except UsageError as exc:
        print(exc, file=sys.stderr)
        code = 1
    present = [name for name in SELECTORS if name in os.environ]
    print(f"selectors: {' '.join(present) or 'none'}")
    return code


if __name__ == "__main__":
    sys.exit(main())
