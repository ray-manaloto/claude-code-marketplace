#!/usr/bin/env python3
"""Claude Code Stop hook for the parent: no integrated lane may stay without a passed retro.

Blocks once when a lane record `.planning/<PLAN_ID>/lanes/*.json` has a `status`
containing "integrated" and a `retro` field other than "passed" (vocabulary in
docs/agents/claude-team.md). A continuation (`stop_hook_active`) is allowed.

One of the three deny gates that stay settings hooks rather than mods (D102); evidence and the
upstream issues to watch: docs/agents/hooks-and-mods.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import git_gate  # noqa: E402


def main() -> int:
    try:
        event = json.loads(sys.stdin.read(1 << 20) or "{}")
    except ValueError:
        return 0
    if not isinstance(event, dict) or event.get("stop_hook_active"):
        return 0
    repo = git_gate.git(event.get("cwd") or ".", "rev-parse", "--show-toplevel")
    pending = [lane["unit"] for lane in (git_gate.lanes(repo) if repo else [])
               if "integrated" in str(lane.get("status", "")) and lane.get("retro") != "passed"]
    if pending:
        print(json.dumps({"decision": "block", "reason": (
            f"Integrated lanes without a passed retro: {', '.join(pending)}. For each, run "
            "./dev/mise run retro:gate -- <unit> on the integrated tree, then set the lane record's "
            '"retro" to "passed" (or record the failure and keep the unit partial).')}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
