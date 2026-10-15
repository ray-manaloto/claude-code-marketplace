"""Class I: project settings composition (C3 §I; W0-1). CT-16 imports project_key_violations().

The pre-commit surface reads the staged bytes, every other surface the working file. A plugin's
marketplace must be declared in the same file, or a fresh clone cannot install it (R5 §B, N1).
"""
from __future__ import annotations

import json

SURFACES = {"session-start", "check", "pre-commit"}
CONTEXT_RANK = 20
BUDGET_MS = {"session-start": 3000, "check": 10000, "pre-commit": 1000}  # pre-commit fails closed on skipped (cli)
PATH, LOCAL = ".claude/settings.json", ".claude/settings.local.json"
PROJECT_KEYS = frozenset({"$schema", "env", "autoCompactEnabled", "autoCompactWindow", "enabledPlugins",
                          "extraKnownMarketplaces", "hooks"})


def project_key_violations(settings: dict) -> list[tuple[str, str, str]]:
    """(finding id, severity, subject): each key outside PROJECT_KEYS, each undeclared plugin marketplace."""
    found = [("I.settings-non-project-key", "P1", key) for key in sorted(set(settings) - PROJECT_KEYS)]
    markets = {plugin.rpartition("@")[2] for plugin in settings.get("enabledPlugins") or {}}
    return found + [("I.settings-plugin-undeclared-marketplace", "P2", market)
                    for market in sorted(markets - set(settings.get("extraKnownMarketplaces") or {}))]


def run(ctx):
    staged = ctx.surface == "pre-commit"
    working = ctx.repo / PATH
    text = ctx.git("show", f":{PATH}") if staged else working.read_text() if working.is_file() else None
    found = [ctx.finding(fid, severity, subject, (PATH + (" (staged)" if staged else ""),),
                         f"move `{subject}` to {LOCAL}" if fid.endswith("non-project-key") else
                         f"declare `{subject}` under extraKnownMarketplaces or drop its plugins")
             for fid, severity, subject in project_key_violations(json.loads(text) if text else {})]
    if (ctx.repo / LOCAL).exists() and ctx.git("check-ignore", "-q", LOCAL) is None:
        found.append(ctx.finding("I.settings-local-not-excluded", "P1", LOCAL, ("git check-ignore: not ignored",),
                                 f"echo {LOCAL} >> \"$(git rev-parse --git-path info/exclude)\""))
    return found


def context_lines(ctx):
    if not ctx.findings:
        return []
    return ["settings: " + " · ".join(f"{f.id.removeprefix('I.settings-')} {f.subject}" for f in ctx.findings)]
