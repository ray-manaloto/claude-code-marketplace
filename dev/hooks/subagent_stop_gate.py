#!/usr/bin/env python3
"""Claude Code SubagentStop hook: a lane subagent stops only with a passing retro record.

When the subagent's `cwd` is a lane worktree (branch `claude/<unit>-<slug>`), the
record `.planning/<PLAN_ID>/retros/<unit>.md` in that worktree must pass
`dev/retro_gate.py`. Blocks once with the gate's reasons; a continuation
(`stop_hook_active`) is allowed so the hook cannot loop.
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
    if not isinstance(event, dict) or event.get("stop_hook_active") or not event.get("cwd"):
        return 0
    repo = git_gate.git(event["cwd"], "rev-parse", "--show-toplevel")
    branch = git_gate.lane_branch(git_gate.git(repo, "branch", "--show-current") or "") if repo else None
    if not branch or not branch.startswith("claude/"):
        return 0
    refusals = git_gate.check_lanes(repo, [branch])
    if refusals:
        reason = (f"{refusals[0]}\nBefore stopping, write the lane retro record at "
                  f".planning/{git_gate.PLAN_ID}/retros/<unit>.md in this worktree (docs/agents/ticket-retro.md) "
                  "and run ./dev/mise run retro:gate -- <unit>.")
        print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
