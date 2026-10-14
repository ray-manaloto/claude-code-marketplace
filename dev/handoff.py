#!/usr/bin/env python3
"""Session handoff for /clear: state, the zero-loss check, regeneration and the start command (CT-29).

Subcommands (all read the checkout under --repo and the plan under .planning/<plan-id>):
  state [--json|--brief] [--agents-done]   facts: HEAD/remote, ops, counts, worktrees, lanes, pending
                                           operations, newest reports, the doctor block, agents flag
  check [--json] [--agents-done]           X3 §2 predicate Z as doctor-shaped findings; exit 2 on P1/P2
  write [--dry-run] [--template F]         regenerate `## Next Step`, the NEXT bullet and HANDOFF §1/§7/§8
                                           into temp copies, probe them, move them only when check passes
  owner --session NAME [--session-id ID]   rewrite the plan's owner paragraph
  start-command [--name N] [--session-id]  the `claude -n <name> "<prompt>"` line with the pins exported
Exit codes: 0 clean, 2 findings or refusal, 1 usage or error. Stdlib only; run under `python3 -I`.
Findings use the doctor shape {id, class, severity, subject, evidence, fix_hint, auto_fixable}; the module
also exports SURFACES/BUDGET_MS/CONTEXT_RANK/run/context_lines so it can move into dev/doctor/ as-is.
Every plan, lane, handoff and hook output is data: this script never executes text it reads.
"""
from __future__ import annotations

import argparse
import dataclasses
from datetime import datetime, timezone
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
import uuid

sys.dont_write_bytecode = True

PLAN_ID = "2026-10-10-marketplace-macos-reflection-scaffold"
PWF_CACHE = Path.home() / ".claude/plugins/cache/planning-with-files/planning-with-files"
DOCTOR_CLIS = ("dev/doctor/cli.py", ".claude/worktrees/w0-doctor/dev/doctor/cli.py")
HANDOFF_GLOB = "reviews/*/phase3/HANDOFF-*.md"
SURFACES = {"handoff", "check"}
BUDGET_MS = {"handoff": 4000, "check": 2000}
CONTEXT_RANK = 70
SEVERITY = {"P1": 0, "P2": 1, "P3": 2, "info": 3}
WIDTH, BLOCK_LINES, BULLET_LINES = 100, 16, 12
SHA_RE = re.compile(r"`([0-9a-f]{7,40})`")
PATH_EXT = (".md", ".json", ".py", ".toml", ".jsonl", ".sh", ".txt", ".pkl", ".lock")
PATH_PREFIX = ("RV/", "P/", "dev/", "docs/", ".claude/", "reviews/", "lanes/", "retros/", "evidence/", "phase")
OPS = ("MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG", "rebase-merge", "rebase-apply")
GIT_SKIP = {"MERGE_HEAD", "REBASE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG"}


@dataclasses.dataclass(frozen=True)
class Finding:
    id: str
    severity: str
    subject: str
    evidence: tuple = ()
    fix_hint: str = ""
    auto_fixable: bool = False

    def to_json(self) -> dict:
        return {"class": self.id.split(".")[0], **dataclasses.asdict(self), "evidence": list(self.evidence)}


@dataclasses.dataclass(frozen=True)
class Context:
    """`repo` answers Git and receipt questions; `plan_root` holds the plan text (an overlay during write)."""
    repo: Path
    plan_id: str = PLAN_ID
    plan_root: Path | None = None
    handoff: Path | None = None

    @property
    def root(self) -> Path:
        return self.plan_root or self.repo

    @property
    def plan(self) -> Path:
        return self.root / ".planning" / self.plan_id

    @property
    def handoff_path(self) -> Path | None:
        if self.handoff:
            return self.handoff
        found = sorted(self.plan.glob(HANDOFF_GLOB))
        return found[-1] if found else None

    @property
    def rv(self) -> Path | None:
        return self.handoff_path.parent.parent if self.handoff_path else None

    @property
    def repo_plan(self) -> Path:
        """The real plan directory (receipts resolve here even when the text comes from an overlay)."""
        return self.repo / ".planning" / self.plan_id

    @property
    def repo_rv(self) -> Path | None:
        if not self.handoff_path:
            return None
        try:
            return self.repo_plan / self.handoff_path.parent.parent.relative_to(self.plan)
        except ValueError:
            return self.handoff_path.parent.parent


def git_binary() -> str:
    """A real git: HANDOFF_GIT, else PATH unless it is a mise shim (~0.16 s per call), else /usr/bin/git."""
    env = os.environ.get("HANDOFF_GIT")
    if env:
        return env
    found = shutil.which("git")
    if found and Path(found).resolve().name != "mise":
        return found
    return "/usr/bin/git" if Path("/usr/bin/git").is_file() else "git"


GIT = git_binary()


def git(repo: Path, *args: str, codes=(0,)) -> str | None:
    try:
        result = subprocess.run([GIT, "-C", str(repo), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.rstrip("\n") if result.returncode in codes else None


def now() -> str:
    return f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def plugin_root() -> Path | None:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env and (Path(env) / "hooks/claude-hook.sh").is_file():
        return Path(env)
    versions = sorted(PWF_CACHE.glob("*/hooks/claude-hook.sh")) if PWF_CACHE.is_dir() else []
    return versions[-1].parent.parent if versions else None


# ---------------------------------------------------------------- plan text helpers

def next_step_block(plan_text: str) -> list[str]:
    """Lines from `## Next Step` up to the next `## ` heading, trailing blanks dropped."""
    lines, out, on = plan_text.splitlines(), [], False
    for line in lines:
        if line.startswith("## "):
            if on:
                break
            on = line.rstrip() == "## Next Step"
        if on:
            out.append(line)
    while out and not out[-1].strip():
        out.pop()
    return out


def bullets(lines: list[str]) -> list[str]:
    """Join wrapped bullets (continuation lines start with two spaces) into one string each."""
    out: list[str] = []
    for line in lines:
        if line.startswith("  ") and out:
            out[-1] += " " + line.strip()
        else:
            out.append(line.strip())
    return out


def next_bullet_span(progress_text: str) -> tuple[int, int] | None:
    """(start, end) line indexes of the `- NEXT` bullet and its continuation, or None."""
    lines = progress_text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("- NEXT")]
    if not starts:
        return None
    start = starts[-1]
    end = start + 1
    while end < len(lines) and (lines[end].startswith("  ") or not lines[end].strip()):
        end += 1
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return start, end


def split_sections_text(text: str) -> dict[str, str]:
    """HANDOFF sections keyed by number ("1".."10"); "preamble" is everything before `## 1.`."""
    out, key, buf = {}, "preamble", []
    for line in text.splitlines(keepends=True):
        match = re.match(r"## (\d+)\. ", line)
        if match:
            out[key] = "".join(buf)
            key, buf = match.group(1), [line]
        else:
            buf.append(line)
    out[key] = "".join(buf)
    return out


def split_sections(path: Path) -> dict[str, str]:
    return split_sections_text(read(path))


def wrap(text: str, indent: str = "  ") -> list[str]:
    return textwrap.wrap(" ".join(text.split()), width=WIDTH, subsequent_indent=indent,
                         break_long_words=False, break_on_hyphens=False) or [""]


def load_template(path: Path) -> dict[str, str]:
    """`## <key>` sections of references/handoff-template.md; each value is the joined section text."""
    out, key, buf = {}, None, []
    for line in read(path).splitlines():
        if line.startswith("## "):
            if key:
                out[key] = "\n".join(buf).strip()
            key, buf = line[3:].strip(), []
        elif key is not None:
            buf.append(line)
    if key:
        out[key] = "\n".join(buf).strip()
    missing = {"action", "owner", "pending-user", "runbook"} - set(out)
    if missing:
        raise ValueError(f"template {path} lacks sections: {sorted(missing)}")
    return out


# ---------------------------------------------------------------- state

def worktrees(repo: Path, head_full: str) -> list[dict]:
    out, cur = [], {}
    for line in (git(repo, "worktree", "list", "--porcelain") or "").splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur = {"path": line[9:], "head": None, "branch": None}
        elif line.startswith("HEAD "):
            cur["head"] = line[5:12]
            cur["head_full"] = line[5:]
        elif line.startswith("branch "):
            cur["branch"] = line[7:].replace("refs/heads/", "")
    reachable = set((git(repo, "rev-list", head_full) or "").split()) if head_full else set()
    for wt in out:
        path = wt["path"]
        wt["kind"] = "root" if Path(path) == repo else "codex" if "/.codex/worktrees/" in path else "lane"
        wt["in_head"] = wt.get("head_full", "") in reachable
        wt["unit"] = Path(path).name if wt["kind"] == "lane" else None
    return out


def lane_records(plan: Path) -> list[dict]:
    out = []
    for path in sorted((plan / "lanes").glob("*.json")):
        try:
            rec = json.loads(read(path))
        except ValueError as error:
            rec = {"unit": path.stem, "status": f"unreadable: {error}"}
        status = str(rec.get("status") or "")
        out.append({"unit": rec.get("unit") or path.stem, "status": status, "review": rec.get("review"),
                    "retro": rec.get("retro"), "worktree": rec.get("worktree"), "branch": rec.get("branch"),
                    "base_sha": rec.get("base_sha"), "integrated": status.startswith(("integrated", "merged")),
                    "closed": status.startswith(("closed", "cancelled")), "cut": "not cut" not in status})
    return out


def pending_operations(plan: Path) -> list[dict]:
    """Operation rows that no receipt closes, matching `plan_decide.pending()`: `plan_decide.py receipt`
    appends a separate `receipt` row whose subject is the operation id."""
    rows = []
    for line in read(plan / "decisions.jsonl").splitlines():
        try:
            row = json.loads(line) if line.strip() else None
        except ValueError:
            continue
        if row:
            rows.append(row)
    closed = {row.get("subject") for row in rows if row.get("kind") == "receipt"}
    return [{"id": row.get("id"), "subject": row.get("subject")} for row in rows
            if row.get("kind") == "operation" and not row.get("receipt") and row.get("id") not in closed]


def newest_reports(plan: Path, limit: int = 8) -> list[dict]:
    files = [p for p in (plan / "reviews").glob("**/phase*/**/*") if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [{"path": str(p.relative_to(plan)), "mtime": f"{datetime.fromtimestamp(p.stat().st_mtime, timezone.utc):%Y-%m-%dT%H:%MZ}"}
            for p in files[:limit]]


def doctor_block(repo: Path) -> dict:
    for rel in DOCTOR_CLIS:
        cli = repo / rel
        if cli.is_file():
            try:
                result = subprocess.run([sys.executable, "-I", str(cli), "--surface", "session-start", "--json",
                                         "--repo", str(repo)], capture_output=True, text=True, timeout=20)
                data = json.loads(result.stdout or "{}")
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                return {"cli": rel, "error": f"{type(error).__name__}: {error}", "counts": {}, "findings": []}
            return {"cli": rel, "counts": data.get("counts", {}), "findings": data.get("findings", []),
                    "rc": result.returncode, "error": None}
    return {"cli": None, "counts": {}, "findings": [], "error": "no dev/doctor/cli.py at the root or in w0-doctor"}


def state(ctx: Context, agents_done: bool = False) -> dict:
    repo = ctx.repo
    head_full = git(repo, "rev-parse", "HEAD") or ""
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "HEAD"
    remote_full = git(repo, "rev-parse", "--verify", "--quiet", f"origin/{branch}")
    ahead = behind = None
    if remote_full:
        counts = (git(repo, "rev-list", "--left-right", "--count", f"origin/{branch}...HEAD") or "0\t0").split()
        behind, ahead = int(counts[0]), int(counts[1])
    git_dir = Path(git(repo, "rev-parse", "--absolute-git-dir") or (repo / ".git"))
    ops = [name for name in OPS if (git_dir / name).exists()]
    counts = {"staged": 0, "unstaged": 0, "untracked": 0}
    for line in (git(repo, "status", "--porcelain", "--untracked-files=normal") or "").splitlines():
        x, y = line[:1], line[1:2]
        if x == "?":
            counts["untracked"] += 1
            continue
        if x not in " ?!":
            counts["staged"] += 1
        if y not in " ?!":
            counts["unstaged"] += 1
    plan_text = read(ctx.plan / "task_plan.md")
    progress_text = read(ctx.plan / "progress.md")
    span = next_bullet_span(progress_text)
    return {
        "schema": "handoff-state/v1", "generated_utc": now(), "repo": str(repo), "plan": str(ctx.plan),
        "branch": branch, "head": head_full[:7], "head_full": head_full,
        "subject": git(repo, "log", "-1", "--format=%s") or "", "git_user": git(repo, "config", "user.name") or "",
        "remote": remote_full[:7] if remote_full else None, "ahead": ahead, "behind": behind,
        "ops": ops, "counts": counts, "worktrees": worktrees(repo, head_full), "lanes": lane_records(ctx.plan),
        "pending_operations": pending_operations(ctx.plan), "newest_reports": newest_reports(ctx.plan),
        "doctor": doctor_block(repo), "agents_done": agents_done,
        "agents_done_utc": now() if agents_done else None,
        "mode": read(ctx.plan / ".mode").strip() or None,
        "handoff": str(ctx.handoff_path.relative_to(ctx.plan)) if ctx.handoff_path else None,
        "next_step": next_step_block(plan_text),
        "next_bullet_last": None if span is None else span[1] >= len(progress_text.splitlines()),
    }


def brief(st: dict) -> str:
    lanes = [f"{l['unit']}:{'integrated' if l['integrated'] else 'closed' if l.get('closed') else 'allocated' if l['cut'] else 'not cut'}"
             for l in st["lanes"]]
    live = [f"{w['unit']} {w['head']}{'' if w['in_head'] else '*'}" for w in st["worktrees"] if w["kind"] == "lane"]
    doc = st["doctor"]
    lines = [f"[handoff] {st['generated_utc']} · {st['repo']} · plan {st['plan'].rsplit('/', 1)[-1]}",
             f"branch {st['branch']} · HEAD {st['head']} · remote {st['remote']} · ahead {st['ahead']} behind {st['behind']}",
             f"ops {st['ops'] or 'none'} · staged {st['counts']['staged']} unstaged {st['counts']['unstaged']} "
             f"untracked {st['counts']['untracked']} · agents-done {st['agents_done']}",
             "lanes " + (", ".join(lanes) or "none"),
             "worktrees (* = not in HEAD) " + (", ".join(live) or "none"),
             "pending operations " + (", ".join(op["id"] for op in st["pending_operations"]) or "none"),
             "newest reports " + ", ".join(r["path"] for r in st["newest_reports"][:3]),
             f"doctor {doc['cli'] or 'absent'} {doc.get('counts') or ''} {doc.get('error') or ''}".rstrip(),
             f"handoff {st['handoff']} · mode {st['mode']} · NEXT last {st['next_bullet_last']}"]
    return "\n".join(lines)


# ---------------------------------------------------------------- injection probe

def parse_frames(hook_stdout: str) -> dict:
    """Plan and progress frames (lines between the PWF data fences) from a hook's JSON or raw output."""
    text = hook_stdout
    try:
        data = json.loads(hook_stdout)
        text = data.get("hookSpecificOutput", {}).get("additionalContext", "") if isinstance(data, dict) else ""
    except ValueError:
        pass
    frames: dict = {"plan": [], "progress": [], "bytes": len(text.encode()), "error": None}
    kind = None
    for line in text.splitlines():
        if line.startswith("===BEGIN-PWF-DATA kind="):
            kind = line.split("kind=", 1)[1].split()[0]
            continue
        if line.startswith("===END-PWF-DATA"):
            kind = None
            continue
        if kind in frames and isinstance(frames[kind], list):
            frames[kind].append(line)
    return frames


def run_probe(plan_root: Path, plan_id: str, context: str, smart: bool) -> dict:
    """One pwf fire: the SessionStart hook (`userprompt`) or the Python twin (`pretool`), fresh session id."""
    root = plugin_root()
    if root is None:
        return {"plan": [], "progress": [], "bytes": 0, "error": "planning-with-files plugin cache not found"}
    env = {k: v for k, v in os.environ.items() if k not in ("PWF_INJECT", "VIRTUAL_ENV")}
    env.update({"PLAN_ID": plan_id, "PWF_PLAN_ROOT": str(plan_root), "CLAUDE_PLUGIN_ROOT": str(root),
                "PWF_TRUSTED_PYTHON": sys.executable, "PWF_SESSION_ID": f"handoff-probe-{uuid.uuid4().hex[:12]}"})
    if smart:
        env["PWF_INJECT"] = "smart"
    try:
        if context == "pretool":
            cmd = [sys.executable, "-I", str(root / "scripts/inject-plan.py"), "--context=pretool"]
            result = subprocess.run(cmd, cwd=plan_root, env=env, capture_output=True, text=True, timeout=30)
        else:
            payload = json.dumps({"session_id": env["PWF_SESSION_ID"], "cwd": str(plan_root),
                                  "hook_event_name": "SessionStart", "source": "clear"})
            result = subprocess.run(["sh", str(root / "hooks/claude-hook.sh"), "session-start"], input=payload,
                                    cwd=plan_root, env=env, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"plan": [], "progress": [], "bytes": 0, "error": f"{type(error).__name__}: {error}"}
    frames = parse_frames(result.stdout)
    if result.returncode != 0:
        frames["error"] = f"rc {result.returncode}: {result.stderr.strip()[:200]}"
    elif not frames["plan"]:
        frames["error"] = "no plan frame emitted"
    return frames


def probe_findings(ctx: Context, st: dict) -> list[Finding]:
    """H.injection-probe-failed: legacy (positions inside 30), smart (presence), pretool (inside 30), NEXT last."""
    out = []
    has_next = any(line.startswith("- NEXT") for line in read(ctx.plan / "progress.md").splitlines())
    for name, context, smart in (("legacy", "userprompt", False), ("smart", "userprompt", True), ("pretool", "pretool", False)):
        frames = run_probe(ctx.root, ctx.plan_id, context, smart)
        if frames["error"]:
            out.append(Finding("H.injection-probe-failed", "P2", f"{name} probe did not run: {frames['error']}",
                               fix_hint="install planning-with-files 3.24.0 or set CLAUDE_PLUGIN_ROOT"))
            continue
        plan = frames["plan"]
        step = next((i for i, line in enumerate(plan, 1) if line.startswith("## Next Step")), None)
        hand = next((i for i, line in enumerate(plan, 1) if line.startswith("Session handoff")), None)
        problems = []
        if step is None or hand is None:
            problems.append("`## Next Step` or its `Session handoff` line is absent from the plan frame")
        elif name != "smart" and max(step, hand) > 30:
            problems.append(f"`## Next Step` at frame line {step}, handoff line {hand}: outside the first 30")
        if name == "smart" and not any(line.startswith("phases:") for line in plan):
            problems.append("smart view not active (no `phases:` line)")
        if context == "userprompt" and has_next:
            progress = frames["progress"]
            starts = [i for i, line in enumerate(progress) if line.startswith("- ")]
            if not starts or not progress[starts[-1]].startswith("- NEXT"):
                problems.append("progress tail does not end on the NEXT bullet")
        for problem in problems:
            out.append(Finding("H.injection-probe-failed", "P1", f"{name}: {problem}",
                               (f"frame {frames['bytes']} B, {len(plan)} plan lines",),
                               "keep `## Next Step` and its handoff inside plan line 30; NEXT bullet last"))
    return out


# ---------------------------------------------------------------- check

def cited_paths(text: str) -> list[str]:
    out = []
    for token in re.findall(r"`([^`\n]+)`", text):
        if any(c in token for c in "*<>{}|~ ") or token.startswith(("/", "-", "$")):
            continue
        if "/" in token and (token.startswith(PATH_PREFIX) or token.endswith(PATH_EXT) or token.endswith("/")):
            out.append(token)
        elif token.endswith(PATH_EXT) and "/" not in token and "." in token[:-3]:
            out.append(token)
    return sorted(set(out))


def resolve_path(ctx: Context, token: str) -> bool:
    rv, plan = ctx.repo_rv, ctx.repo_plan
    bases = [ctx.repo, plan, ctx.repo / ".claude"]
    if rv:
        bases += [rv, rv / "phase3", rv / "phase4-prep", rv / "phase3/w0"]
    rel = token
    if token.startswith("RV/") and rv:
        rel, bases = token[3:], [rv]
    elif token.startswith("P/"):
        rel, bases = token[2:], [plan]
    elif token.startswith("<root>/"):
        rel, bases = token[7:], [ctx.repo]
    return any((base / rel).exists() for base in bases)


CLAIM_RE = re.compile(r"\b(integrated|READY|allocated|not cut)\b", re.I)


def claim_for(unit: str, texts: list[str]) -> str | None:
    """'integrated' or 'allocated' from the state word nearest the unit inside its `;`-segment, else None."""
    pattern = re.compile(rf"(?<![\w-]){re.escape(unit)}(?![\w-])")
    for text in texts:
        for segment in text.split(";"):
            hit = pattern.search(segment)
            if not hit:
                continue
            words = list(CLAIM_RE.finditer(segment))
            before = [w for w in words if w.end() <= hit.start()]
            after = [w for w in words if w.start() >= hit.end()]
            word = (before[-1] if before else after[0] if after else None)
            if word:
                return "integrated" if word.group(1).lower() == "integrated" else "allocated"
    return None


def check(ctx: Context, st: dict, probe: bool = True) -> list[Finding]:
    found: list[Finding] = []
    block = st["next_step"]
    block_text = "\n".join(block)
    sections = split_sections(ctx.handoff_path) if ctx.handoff_path else {}
    s1 = sections.get("1", "")
    texts = bullets(block) + bullets(s1.splitlines())
    if not block:
        found.append(Finding("H.handoff-stale-sha", "P1", "task_plan.md has no `## Next Step` block",
                             fix_hint="run `dev/handoff.py write`"))
    if not ctx.handoff_path:
        found.append(Finding("H.receipt-missing", "P1", f"no HANDOFF file matches {HANDOFF_GLOB}"))
    if st["ops"]:
        found.append(Finding("H.git-op-in-progress", "P1", f"Git operation in progress: {', '.join(st['ops'])}",
                             fix_hint="finish or abort it before /clear"))
    if st["remote"] is None:
        found.append(Finding("H.head-not-remote", "P2", f"origin/{st['branch']} does not exist",
                             fix_hint="publish the branch (A09) or name the remote tip by hand"))
    elif st["head"] != st["remote"]:
        declared = re.search(r"\b(ahead|behind)\b", block_text)
        claims_equal = re.search(r"HEAD `[0-9a-f]+` = remote", block_text)
        sev = "P1" if claims_equal else "P3" if declared else "P2"
        found.append(Finding("H.head-not-remote", sev, f"HEAD {st['head']} != origin/{st['branch']} {st['remote']} "
                             f"(ahead {st['ahead']}, behind {st['behind']})",
                             fix_hint="publish through A09 or declare the drift in `## Next Step`"))
    claimed = re.search(r"HEAD `([0-9a-f]{7,40})`", block_text)
    if claimed and not st["head_full"].startswith(claimed.group(1)):
        found.append(Finding("H.handoff-stale-sha", "P1", f"`## Next Step` says HEAD `{claimed.group(1)}`, HEAD is {st['head']}",
                             fix_hint="run `dev/handoff.py write`", auto_fixable=True))
    row = re.search(r"\| HEAD \| `([0-9a-f]{7,40})`", s1)
    if row and not st["head_full"].startswith(row.group(1)):
        found.append(Finding("H.handoff-stale-sha", "P1", f"HANDOFF §1 says HEAD `{row.group(1)}`, HEAD is {st['head']}",
                             fix_hint="run `dev/handoff.py write`", auto_fixable=True))
    for sha in sorted(set(SHA_RE.findall(block_text + "\n" + s1))):
        if any(c.isalpha() for c in sha) and git(ctx.repo, "cat-file", "-e", f"{sha}^{{commit}}") is None:
            found.append(Finding("H.handoff-stale-sha", "P1", f"`{sha}` cited by the handoff does not resolve",
                                 fix_hint="correct the SHA or fetch the object"))
    lanes = {lane["unit"]: lane for lane in st["lanes"]}
    for unit, lane in lanes.items():
        claim = claim_for(unit, texts)
        if claim == "integrated" and not lane["integrated"]:
            found.append(Finding("H.lane-record-mismatch", "P1", f"{unit}: handoff says integrated, lanes/{unit}.json says `{lane['status']}`",
                                 fix_hint=f"update lanes/{unit}.json status or the handoff line"))
        elif claim == "allocated" and lane["integrated"]:
            found.append(Finding("H.lane-record-mismatch", "P1", f"{unit}: handoff says allocated, lanes/{unit}.json says `{lane['status']}`"))
        elif claim and not lane["review"] and any(re.search(rf"{re.escape(unit)}.*review PASS", t) for t in texts):
            found.append(Finding("H.lane-record-mismatch", "P3", f"{unit}: handoff claims a review PASS, lanes/{unit}.json has review null",
                                 fix_hint=f"record review/retro in lanes/{unit}.json at integration"))
        wt = lane.get("worktree")
        if (wt and lane["cut"] and not lane["integrated"] and not lane.get("closed")
                and not (ctx.repo / wt).is_dir() and not Path(wt).is_dir()):
            found.append(Finding("H.receipt-missing", "P2", f"lane {unit} worktree `{wt}` is missing while status is `{lane['status']}`",
                                 fix_hint="re-cut the worktree or mark the record `not cut`"))
    receipt_lines = [line for line in sections.values() for line in line.splitlines() if re.search(r"\bReceipt:", line)]
    for token in cited_paths(block_text + "\n" + s1 + "\n" + "\n".join(receipt_lines)):
        if not resolve_path(ctx, token):
            found.append(Finding("H.receipt-missing", "P1", f"cited path `{token}` does not resolve",
                                 fix_hint="create the receipt or drop the citation"))
    for op in st["pending_operations"]:
        if op["id"] and not re.search(rf"\b{re.escape(op['id'])}\b", block_text):
            found.append(Finding("H.pending-decision-unlisted", "P2", f"pending operation {op['id']} ({op['subject']}) is not in `## Next Step`",
                                 fix_hint="run `dev/handoff.py write` (lists every receipt-less operation)", auto_fixable=True))
    if st["next_bullet_last"] is False:
        found.append(Finding("H.next-not-last", "P1", "progress.md `- NEXT` bullet is not the last entry",
                             fix_hint="run `dev/handoff.py write` (moves it to the end)", auto_fixable=True))
    if (st["mode"] or "") != "inject-smart":
        found.append(Finding("H.mode-not-inject-smart", "P3", f".mode is {st['mode']!r}; CT-30 sets `inject-smart`",
                             fix_hint="CT-30 step 2 after D54; legacy injection still carries the handoff"))
    doc = st["doctor"]
    if doc.get("cli") and not doc.get("error"):
        p1, p2 = doc["counts"].get("P1", 0), doc["counts"].get("P2", 0)
        if p1 or p2:
            found.append(Finding("H.doctor-findings", "P1" if p1 else "P2", f"doctor session-start: P1 {p1}, P2 {p2} ({doc['cli']})",
                                 tuple(f["id"] for f in doc["findings"][:6]), "run `./dev/mise run doctor` and fix"))
    if not st["agents_done"]:
        found.append(Finding("H.agents-unconfirmed", "P2", "operator has not asserted --agents-done (no Agent still running)",
                             fix_hint="confirm every dispatched agent returned, then pass --agents-done"))
    if probe:
        found += probe_findings(ctx, st)
    found.sort(key=lambda f: (SEVERITY.get(f.severity, 9), f.id, f.subject))
    return found


def exit_code(found: list[Finding]) -> int:
    return 2 if any(f.severity in ("P1", "P2") for f in found) else 0


def print_findings(found: list[Finding], st: dict | None, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"schema": "handoff-check/v1", "generated_utc": now(), "repo": st["repo"] if st else None,
                          "findings": [f.to_json() for f in found],
                          "counts": {s: sum(f.severity == s for f in found) for s in ("P1", "P2", "P3")},
                          "rc": exit_code(found)}, indent=1))
        return
    for f in found:
        print(f"{f.severity} {f.id} {f.subject}" + (f"\n  fix: {f.fix_hint}" if f.fix_hint else ""))
    print(f"handoff check: {len(found)} finding(s), rc {exit_code(found)}")


# ---------------------------------------------------------------- write

def owner_name(template: dict, name: str | None) -> str:
    match = re.search(r"`([^`]+)`", template.get("owner", ""))
    return name or (match.group(1) if match else "next-session")


def next_rev(block: list[str]) -> int:
    match = re.search(r"\brev (\d+)\b", "\n".join(block))
    return int(match.group(1)) + 1 if match else 1


def render(ctx: Context, st: dict, template: dict, name: str | None = None) -> dict:
    """New `## Next Step` block, NEXT bullet and HANDOFF text; the hand-written sentences come from the template."""
    today = st["generated_utc"][:10]
    rev = next_rev(st["next_step"])
    name = owner_name(template, name)
    rel = "=" if st["head"] == st["remote"] else "!="
    drift = "" if rel == "=" else f" (ahead {st['ahead']}, behind {st['behind']})"
    c = st["counts"]
    head_line = (f"HEAD `{st['head']}` {rel} remote `origin/{st['branch']}`{drift}; staged {c['staged']}, "
                 f"unstaged {c['unstaged']}, untracked {c['untracked']}; git op: {', '.join(st['ops']) or 'none'}.")
    integrated = [l["unit"] for l in st["lanes"] if l["integrated"]]
    heads = {w["unit"]: w["head"] for w in st["worktrees"] if w["kind"] == "lane"}
    open_lanes = [f"{l['unit']} (`{heads[l['unit']]}`)" if l["unit"] in heads else f"{l['unit']} (not cut)"
                  for l in st["lanes"] if not l["integrated"] and not l.get("closed")]
    closed = [l["unit"] for l in st["lanes"] if l.get("closed")]
    closed_text = f"; closed: {', '.join(closed)}" if closed else ""
    lanes_named = (f"Lanes: {len(integrated)} integrated ({', '.join(integrated)}); "
                   f"allocated: {', '.join(open_lanes) or 'none'}{closed_text}.")
    lanes_short = (f"Lanes: {len(integrated)} integrated (names in HANDOFF §1); "
                   f"allocated: {', '.join(open_lanes) or 'none'}{closed_text}.")
    live = [f"{w['unit']} `{w['head']}`" for w in st["worktrees"] if w["kind"] == "lane" and not w["in_head"]]
    stale = sum(1 for w in st["worktrees"] if w["kind"] == "lane" and w["in_head"])
    codex = sum(1 for w in st["worktrees"] if w["kind"] == "codex")
    wt_line = (f"Worktrees not in HEAD: {', '.join(live) or 'none'}; {stale} integrated (removable on the "
               f"user's word); {codex} Codex worktrees, read-only.")
    ops_line = "Pending operations (`decisions.jsonl` rows without a receipt; subjects in HANDOFF §1): " + (
        ", ".join(op["id"] for op in st["pending_operations"]) or "none") + "."
    agents = ("none (verified by the parent, --agents-done)" if st["agents_done"] else "UNCONFIRMED (run write with --agents-done)")
    agents_line = f"Agents running at /clear: {agents}. {template['owner']} {template['runbook']}"
    reports_line = "Newest reports: " + ", ".join(r["path"].split("/", 1)[-1] for r in st["newest_reports"][:3]) + "."
    header = ["## Next Step", *wrap(template["action"], indent=""),
              f"Session handoff ({today} rev {rev}, for the session after /clear; regenerated by dev/handoff.py):"]
    notes = [n[2:] if n.startswith("- ") else n for n in bullets(template.get("notes", "").splitlines()) if n]
    optional = [wt_line, reports_line] + notes
    for lanes_line in (lanes_named, lanes_short):  # degrade the lane names to a count when they do not fit
        required = [head_line, lanes_line, ops_line, template["pending-user"], agents_line]
        lines = header + [l for b in required for l in wrap("- " + b)]
        if len(lines) <= BLOCK_LINES:
            break
    else:
        raise ValueError(f"required handoff lines exceed {BLOCK_LINES} ({len(lines)}): shorten the template sentences")
    for item in optional:
        extra = wrap("- " + item)
        if len(lines) + len(extra) <= BLOCK_LINES:
            lines += extra
    block = "\n".join(lines).replace("—", "-")
    bullet_text = (f"- NEXT ({today} rev {rev}, owner: next session `{name}`; rewrite in place, keep last): "
                   f"{template['action']} HEAD `{st['head']}` {rel} remote; pending operations "
                   f"{', '.join(op['id'] for op in st['pending_operations']) or 'none'}; {template['pending-user']} "
                   f"Before /clear: `dev/handoff.py check` (HANDOFF §7).")
    bullet_lines = wrap(bullet_text)
    if len(bullet_lines) > BULLET_LINES:
        raise ValueError(f"NEXT bullet exceeds {BULLET_LINES} lines: shorten the template sentences")
    bullet = "\n".join(bullet_lines).replace("—", "-")
    out = {"next_step": block, "next_bullet": bullet, "rev": rev, "name": name}
    if ctx.handoff_path:
        sections = split_sections(ctx.handoff_path)
        sections["1"] = section_state(st, rev, template.get("state-rows", ""))
        sections["7"] = section_preclear(st)
        sections["8"] = section_start(ctx, st, name)
        out["handoff"] = "".join(sections[k] for k in ["preamble"] + sorted((k for k in sections if k != "preamble"), key=int))
    return out


def section_state(st: dict, rev: int, extra_rows: str = "") -> str:
    """§1: generated rows, then the template's `state-rows` (hand-written `| Item | Value |` lines), then worktrees."""
    c = st["counts"]
    rows = [("Branch", f"`{st['branch']}` (Git user {st['git_user'] or 'unknown'})"),
            ("HEAD", f"`{st['head']}` \"{st['subject']}\""),
            ("Remote", f"`origin/{st['branch']}` = `{st['remote']}` (ahead {st['ahead']}, behind {st['behind']})"),
            ("Index", f"staged {c['staged']}, unstaged {c['unstaged']}, untracked {c['untracked']}; in-progress operation: {', '.join(st['ops']) or 'none'}"),
            ("Agents running", "none (verified by the parent: ListAgents and a process scan; `--agents-done` at " + str(st["agents_done_utc"]) + ")" if st["agents_done"] else "UNCONFIRMED"),
            ("Doctor", f"{st['doctor']['cli']} counts {st['doctor'].get('counts')}" if st["doctor"].get("cli") else "not available: " + str(st["doctor"].get("error"))),
            ("Pending operations", ", ".join(f"{op['id']} ({op['subject']})" for op in st["pending_operations"]) or "none"),
            ("Newest reports", ", ".join(f"`{r['path']}` {r['mtime']}" for r in st["newest_reports"][:5]) or "none")]
    lanes = {l["unit"]: l for l in st["lanes"]}
    wt_rows = []
    for w in st["worktrees"]:
        if w["kind"] != "lane":
            continue
        lane = lanes.get(w["unit"], {})
        status = (lane.get("status") or "no lane record")[:70]
        wt_rows.append(f"| `{w['unit']}` | `{w['head']}` (`{w['branch'] or 'detached'}`) | {status} | {'yes' if w['in_head'] else 'no'} |")
    for unit, lane in lanes.items():
        if unit not in {w["unit"] for w in st["worktrees"]} and not lane["integrated"]:
            wt_rows.append(f"| `{unit}` | none | {lane['status'][:70]} | - |")
    codex = sum(1 for w in st["worktrees"] if w["kind"] == "codex")
    return ("## 1. State at /clear\n\n"
            f"Regenerated by `dev/handoff.py write` at {st['generated_utc']} (rev {rev}); sections 2-6, 9 and 10 are\n"
            "hand-written and preserved byte for byte.\n\n| Item | Value |\n|---|---|\n"
            + "".join(f"| {k} | {v} |\n" for k, v in rows)
            + "".join(line + "\n" for line in extra_rows.splitlines() if line.startswith("|"))
            + "\nWorktrees (`.claude/worktrees/<unit>`; \"In HEAD\" = the worktree HEAD is an ancestor of HEAD):\n\n"
            "| Worktree | HEAD | Lane status | In HEAD |\n|---|---|---|---|\n" + "\n".join(wt_rows)
            + ("\n" if wt_rows else "") + f"| `~/.codex/worktrees/*` ({codex}) | various | Codex worktrees: read-only; never write there | - |\n\n")


def section_preclear(st: dict) -> str:
    return ("## 7. Pre-clear check\n\n"
            "Automated (CT-29): `python3 -I dev/handoff.py check --agents-done` from `<root>` with `VIRTUAL_ENV` unset\n"
            "(`./dev/mise run session:handoff -- --check` once the row lands). Exit 0 clean, 2 on any P1/P2 finding,\n"
            "1 on error; the finding ids and the predicate: `.claude/skills/session-handoff/references/predicate.md`.\n"
            f"Last `write`: {st['generated_utc']}, findings at write time: none (a write with findings is refused).\n\n"
            "Manual twin when the script cannot run:\n"
            "1. Injection probe: legacy, smart and pretool pwf fires with fresh probe ids; `## Next Step` and its\n"
            "   `Session handoff` line inside plan line 30 (legacy, pretool) and present in the smart frame; the\n"
            "   progress tail ends on the NEXT bullet while one exists.\n"
            "2. Doctor session-start (root `dev/doctor/cli.py` or the w0-doctor worktree copy): 0 P1.\n"
            "3. `git status`: no `MERGE_HEAD`, `REBASE_HEAD` or `CHERRY_PICK_HEAD`; counts as declared in §1.\n"
            "4. No running agents: every dispatched agent has returned; only then `--agents-done`.\n"
            "5. Receipts: every path cited in `## Next Step`, §1 and the `Receipt:` lines resolves on disk.\n\n")


def section_start(ctx: Context, st: dict, name: str) -> str:
    return ("## 8. Start command\n\n"
            "Generated by `dev/handoff.py start-command` (X1 §3 Option A; `-n` names the session, the positional\n"
            "prompt is the first turn):\n\n```sh\n" + start_command(ctx, name, None) + "\n```\n\n"
            "Two ways to start the next session; use one, never both:\n"
            "- New terminal: paste the block above. Its prompt already runs session-resume, so type nothing\n"
            "  else; do not type `/session-resume` in that session.\n"
            "- Same terminal: type `/clear`, then type this as the first turn:\n"
            f"  `/session-resume {name}`\n"
            "  `/clear` keeps this terminal's environment: it does not unset `VIRTUAL_ENV` or export the pins.\n\n"
            "Optional: `--session-id \"$(uuidgen | tr A-Z a-z)\"` fixes the id before launch. Never `claude -c`,\n"
            "`--bare` or `--safe-mode`; fork (`-r <id> --fork-session`) only under the 500K fork-deny line.\n\n")


def start_command(ctx: Context, name: str | None, session_id: str | None) -> str:
    name = name or f"ccm-{datetime.now(timezone.utc):%Y%m%d}"
    handoff = ctx.handoff_path
    rel = str(handoff.relative_to(ctx.root)) if handoff else ".planning/<plan>/reviews/<session>/phase3/HANDOFF-<date>.md"
    sid = f" --session-id {session_id}" if session_id else ""
    prompt = (f"Use the session-resume skill for session {name}: it follows {rel} section 2, runs the doctor "
              f"session-start surface and dev/handoff.py check, dispatches the extractor and rewrites the owner "
              f"line. Then continue at the Next Step of the plan.")
    return (f"cd {ctx.repo}\nunset VIRTUAL_ENV\nexport PLAN_ID={ctx.plan_id} PWF_PLAN_ROOT={ctx.repo}\n"
            f"claude -n {name}{sid} \"{prompt}\"")


def replace_next_step(plan_text: str, block: str) -> str:
    lines = plan_text.splitlines()
    start = next((i for i, line in enumerate(lines) if line.rstrip() == "## Next Step"), None)
    if start is None:
        raise ValueError("task_plan.md has no `## Next Step` heading")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[:start] + block.splitlines() + [""] + lines[end:]) + "\n"


def replace_next_bullet(progress_text: str, bullet: str) -> str:
    lines = progress_text.splitlines()
    span = next_bullet_span(progress_text)
    if span:
        lines = lines[:span[0]] + lines[span[1]:]
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines + ["", *bullet.splitlines()]) + "\n"


def diff(old: str, new: str, name: str, limit: int = 120) -> str:
    lines = list(difflib.unified_diff(old.splitlines(), new.splitlines(), f"a/{name}", f"b/{name}", lineterm="", n=1))
    if len(lines) > limit:
        lines = lines[:limit] + [f"... {len(lines) - limit} more diff lines"]
    return "\n".join(lines)


def write(ctx: Context, template: Path, agents_done: bool, dry_run: bool, name: str | None = None) -> int:
    st = state(ctx, agents_done=agents_done)
    tpl = load_template(template)
    out = render(ctx, st, tpl, name)
    targets = {ctx.plan / "task_plan.md": replace_next_step(read(ctx.plan / "task_plan.md"), out["next_step"]),
               ctx.plan / "progress.md": replace_next_bullet(read(ctx.plan / "progress.md"), out["next_bullet"])}
    if ctx.handoff_path:
        targets[ctx.handoff_path] = out["handoff"]
    for path, text in targets.items():
        print(diff(read(path), text, str(path.relative_to(ctx.root))) or f"{path.name}: unchanged")
    with tempfile.TemporaryDirectory(prefix="handoff-overlay-") as tmp:
        overlay = Path(tmp)
        plan = overlay / ".planning" / ctx.plan_id
        plan.mkdir(parents=True)
        for rel in ("lanes", "decisions.jsonl", ".mode"):
            src = ctx.plan / rel
            if src.is_dir():
                shutil.copytree(src, plan / rel)
            elif src.is_file():
                shutil.copyfile(src, plan / rel)
        for path, text in targets.items():
            dest = plan / path.relative_to(ctx.plan)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
        probe_ctx = Context(ctx.repo, ctx.plan_id, overlay, (plan / ctx.handoff_path.relative_to(ctx.plan)) if ctx.handoff_path else None)
        found = check(probe_ctx, state(probe_ctx, agents_done=agents_done))
    print_findings(found, st, as_json=False)
    if exit_code(found):
        print("write refused: the regenerated handoff still fails the check; nothing moved")
        return 2
    if dry_run:
        print(f"dry-run: {len(targets)} file(s) would be written (rev {out['rev']}); nothing moved")
        return 0
    for path, text in targets.items():
        tmp_path = path.with_name(path.name + ".tmp")
        tmp_path.write_text(text, encoding="utf-8")
        os.replace(tmp_path, path)
    print(f"written: {', '.join(str(p.relative_to(ctx.root)) for p in targets)} (rev {out['rev']})")
    return 0


# ---------------------------------------------------------------- owner

OWNER_RE = re.compile(r"Owner: session `(?P<name>[^`]+)` \(`(?P<id>[^`]+)`\) owns this plan and the branch "
                      r"`(?P<branch>[^`]+)` since (?P<since>\d{4}-\d{2}-\d{2}); (?:dead|previous) session "
                      r"`(?P<old>[^`]+)` \(`(?P<old_id>[^`]+)`\) is closed\.")


def default_session_id(repo: Path) -> str | None:
    project = Path.home() / ".claude/projects" / str(repo).replace("/", "-")
    files = sorted(project.glob("*.jsonl"), key=lambda p: p.stat().st_mtime) if project.is_dir() else []
    return files[-1].stem if files else None


def owner(ctx: Context, session: str, session_id: str | None) -> str:
    path = ctx.plan / "task_plan.md"
    text = read(path)
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if "Owner: session" in line), None)
    if start is None:
        raise ValueError("task_plan.md has no `Owner: session` sentence in its head")
    first = start
    while first > 0 and lines[first - 1].strip():
        first -= 1
    last = start
    while last + 1 < len(lines) and lines[last + 1].strip():
        last += 1
    paragraph = " ".join(" ".join(lines[first:last + 1]).split())
    match = OWNER_RE.search(paragraph)
    if not match:
        raise ValueError("owner sentence does not match the expected shape")
    sid = session_id or default_session_id(ctx.repo) or "id-unrecorded"
    today = f"{datetime.now(timezone.utc):%Y-%m-%d}"
    new = (f"Owner: session `{session}` (`{sid}`) owns this plan and the branch `{match['branch']}` since {today}; "
           f"previous session `{match['name']}` (`{match['id'][:8]}`) is closed.")
    new_paragraph = textwrap.wrap(paragraph[:match.start()] + new + paragraph[match.end():], width=WIDTH - 5,
                                  break_long_words=False, break_on_hyphens=False)
    lines[first:last + 1] = new_paragraph
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(new_paragraph)


# ---------------------------------------------------------------- doctor detector surface

def run(doctor_ctx) -> list[Finding]:
    """Doctor discovery contract: findings for the `handoff` (with probes) or `check` (without) surface."""
    ctx = Context(Path(doctor_ctx.repo), doctor_ctx.plan_id)
    payload = getattr(doctor_ctx, "payload", {}) or {}
    return check(ctx, state(ctx, agents_done=bool(payload.get("agents_done"))), probe=doctor_ctx.surface == "handoff")


def context_lines(doctor_ctx) -> list[str]:
    ctx = Context(Path(doctor_ctx.repo), doctor_ctx.plan_id)
    found = [f for f in getattr(doctor_ctx, "findings", ()) if f.id.startswith("H.")]
    name = ctx.handoff_path.name if ctx.handoff_path else "none"
    return [f"handoff: {name} §2 · check {'PASS' if not exit_code(found) else 'FAIL'} ({len(found)} H findings) · "
            f"resume: /session-resume after /clear only"]


# ---------------------------------------------------------------- cli

class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(1, f"handoff: {message}\n")


def main(argv=None) -> int:
    parser = Parser(prog="handoff", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", help="checkout to inspect (default: this file's repository)")
    parser.add_argument("--plan-id", default=os.environ.get("PLAN_ID") or PLAN_ID)
    parser.add_argument("--handoff", help="HANDOFF file (default: newest reviews/*/phase3/HANDOFF-*.md)")
    sub = parser.add_subparsers(dest="command")
    sub.required = True
    p_state = sub.add_parser("state")
    p_state.add_argument("--json", action="store_true")
    p_state.add_argument("--brief", action="store_true")
    p_state.add_argument("--agents-done", action="store_true")
    p_check = sub.add_parser("check")
    p_check.add_argument("--json", action="store_true")
    p_check.add_argument("--agents-done", action="store_true")
    p_check.add_argument("--no-probe", action="store_true", help="skip the pwf injection probes")
    p_write = sub.add_parser("write")
    p_write.add_argument("--dry-run", action="store_true")
    p_write.add_argument("--agents-done", action="store_true")
    p_write.add_argument("--template", help="hand-written sentences (default: .claude/skills/session-handoff/references/handoff-template.md)")
    p_write.add_argument("--name", help="next session name (default: the template's owner line)")
    p_owner = sub.add_parser("owner")
    p_owner.add_argument("--session", required=True)
    p_owner.add_argument("--session-id")
    p_start = sub.add_parser("start-command")
    p_start.add_argument("--name")
    p_start.add_argument("--session-id")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parents[1]
    if git(repo, "rev-parse", "--show-toplevel") is None:
        parser.error(f"not a Git checkout: {repo}")
    ctx = Context(repo, args.plan_id, None, Path(args.handoff).resolve() if args.handoff else None)
    try:
        if args.command == "state":
            st = state(ctx, agents_done=args.agents_done)
            print(json.dumps(st, indent=1) if args.json and not args.brief else brief(st))
            return 0
        if args.command == "check":
            st = state(ctx, agents_done=args.agents_done)
            found = check(ctx, st, probe=not args.no_probe)
            print_findings(found, st, args.json)
            return exit_code(found)
        if args.command == "write":
            template = Path(args.template) if args.template else repo / ".claude/skills/session-handoff/references/handoff-template.md"
            return write(ctx, template, args.agents_done, args.dry_run, args.name)
        if args.command == "owner":
            print(owner(ctx, args.session, args.session_id))
            return 0
        if args.command == "start-command":
            print(start_command(ctx, args.name, args.session_id))
            return 0
    except (OSError, ValueError) as error:
        print(f"handoff: {error}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    started = time.monotonic()
    code = main()
    if os.environ.get("HANDOFF_TIMING"):
        print(f"handoff: {int((time.monotonic() - started) * 1000)} ms", file=sys.stderr)
    sys.exit(code)
