#!/usr/bin/env python3
"""Doctor: report checkout, settings and context drift after the fact (C3 §Doctor task spec).

Exit 0 without P1/P2, 2 with any, 1 usage, 3 when a detector raised; `--surface session-start
--format context` (the SessionStart hook form) always exits 0, and `--surface pre-commit` also exits 2
when a detector was skipped (a commit guard fails closed). A hook payload on stdin supplies `cwd`.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import select
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import core  # noqa: E402

PLAN_ID = "2026-10-10-marketplace-macos-reflection-scaffold"
MAX_LINES, MAX_BYTES = 30, 2500


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(1, f"doctor: {message}\n")


def hook_payload() -> dict:
    if sys.stdin is None or sys.stdin.isatty() or not select.select([sys.stdin], [], [], 0.2)[0]:
        return {}
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def context_block(ctx, findings, lines) -> str:
    head, branch = ((ctx.git("rev-parse", "HEAD", "--abbrev-ref", "HEAD") or "none\n?").split() + ["?"])[:2]
    counts = " · ".join(f"{s} {sum(f.severity == s for f in findings)}" for s in ("P1", "P2", "P3"))
    block = [f"[doctor] checkout {datetime.now(timezone.utc):%Y-%m-%dT%H:%MZ} · {ctx.repo} · plan {ctx.plan_id}",
             f"branch {branch} · HEAD {head[:7]}", *lines][: MAX_LINES - 1]
    tail = f"findings {counts} → ./dev/mise run doctor   (json: ./dev/mise run doctor -- --json)"
    while len(block) > 2 and len("\n".join([*block, tail]).encode()) > MAX_BYTES:
        block.pop()
    return "\n".join([*block, tail])


def main(argv=None) -> int:
    parser = Parser(prog="doctor", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--surface", choices=sorted(core.BUDGET_MS), default="check")
    parser.add_argument("--format", choices=("text", "context"), default="text")
    parser.add_argument("--json", action="store_true", help="print the doctor/v1 report object")
    parser.add_argument("--repo", help="checkout to inspect (default: the payload cwd, else the current directory)")
    parser.add_argument("--plan-id", default=os.environ.get("PLAN_ID") or PLAN_ID)
    parser.add_argument("--budget-ms", type=int, help="override every detector's budget")
    args = parser.parse_args(argv)
    started, payload = time.monotonic(), hook_payload() if args.surface == "session-start" else {}
    start = Path(args.repo or payload.get("cwd") or os.getcwd()).resolve()
    top = next((d for d in (start, *start.parents) if (d / ".git").exists()), None)  # no git call: ~0.17 s each
    if top is None:
        parser.error(f"not a Git checkout: {start}")
    ctx = core.Context(top, args.surface, args.plan_id, Path.home(), payload)
    findings, lines, raised = core.run(ctx, args.budget_ms)
    real = [f for f in findings if f.severity != "skipped"]
    guard = [f for f in findings if f.severity == "skipped"] if args.surface == "pre-commit" else []
    code = 3 if raised else 2 if guard or any(f.severity in ("P1", "P2") for f in real) else 0
    if args.format == "context":
        print(context_block(ctx, real, lines))
        return 0 if args.surface == "session-start" else code
    if args.json:
        print(json.dumps({"schema": "doctor/v1", "generated_utc": f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
                          "surface": ctx.surface, "repo": str(ctx.repo), "findings": [f.to_json() for f in real],
                          "skipped": [f.to_json() for f in findings if f.severity == "skipped"],
                          "counts": {s: sum(f.severity == s for f in real) for s in ("P1", "P2", "P3")},
                          "duration_ms": int((time.monotonic() - started) * 1000)}, indent=1))
    else:
        for f in real + guard:
            print(f"{f.severity} {f.id} {f.subject}" + (f"\n  fix: {f.fix_hint}" if f.fix_hint else ""),
                  file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
