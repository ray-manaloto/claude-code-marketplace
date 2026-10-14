"""Class A: the context-budget thresholds (one source; hooks import this file by path) and the
auto-compact line (C3 §A, C2 T-A5, C4 required change 4). Reads key names and booleans only; the
finding follows settings precedence (local > project > the two personal copies, D21), never a document."""
from __future__ import annotations

import json

# All below the project autoCompactWindow (700000); fork_deny = frontier.toml ceiling fraction x window (D29).
THRESHOLDS = {"warn": 400_000, "checkpoint": 550_000, "fork_deny": 500_000, "hard": 650_000}
SURFACES = {"session-start"}
CONTEXT_RANK = 80


def autocompact(ctx) -> dict[str, bool]:
    """{source: autoCompactEnabled} for each settings file that sets the key to a boolean."""
    sources = {"user": ctx.home / ".claude" / "settings.json", "global": ctx.home / ".claude.json",
               "project": ctx.repo / ".claude" / "settings.json", "local": ctx.repo / ".claude" / "settings.local.json"}
    flags = {}
    for name, path in sources.items():
        try:
            value = json.loads(path.read_text()).get("autoCompactEnabled")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(value, bool):
            flags[name] = value
    return flags


def ruling_off(flags: dict[str, bool]) -> list[str]:
    """Sources whose `false` is in force: the local or project file decides first, else both personal copies."""
    for name in ("local", "project"):
        if name in flags:
            return [] if flags[name] else [name]
    return [name for name in ("user", "global") if flags.get(name) is False]


def run(ctx):
    off = ruling_off(autocompact(ctx))
    return [ctx.finding("A.autocompact-off", "P3", f"autoCompactEnabled=false in {', '.join(off)}",
                        fix_hint="set it true there; .claude/settings.json (project) overrides the personal copies")
            ] if off else []


def context_lines(ctx):
    flags = autocompact(ctx)
    state = " ".join(f"{name}={str(value).lower()}" for name, value in flags.items()) or "default(on)"
    limits = " · ".join(f"{name} {value // 1000}K" for name, value in THRESHOLDS.items())
    return [f"context: auto-compact: {state} · {limits}"]
