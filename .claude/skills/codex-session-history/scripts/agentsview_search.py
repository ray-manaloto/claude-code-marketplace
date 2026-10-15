#!/usr/bin/env python3
"""Search the AgentsView archive (Codex, Claude, Antigravity sessions) compactly.

Wraps `agentsview session search` / `session messages` with the remote-daemon
flags this machine needs, prints one bounded row per match, and reports the
archive's coverage status so a lexical-only answer is never mistaken for a
semantic one. The daemon URL and token file default to the install recorded in
~/.claude/skills/agentsview-finding-history/SKILL.md; override with
AGENTSVIEW_SERVER / AGENTSVIEW_TOKEN_FILE.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

SERVER = os.environ.get("AGENTSVIEW_SERVER", "http://127.0.0.1:8080")
TOKEN = os.environ.get(
    "AGENTSVIEW_TOKEN_FILE",
    os.path.expanduser("~/Library/Application Support/AgentsView-M1-working-b0ae79c5365e-20260915/archive/native-server-token"),
)


def run(args: list[str]) -> tuple[int, str, str]:
    cmd = ["agentsview", *args, "--json", "--server", SERVER, "--server-token-file", TOKEN]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def search(a) -> int:
    base = ["session", "search", a.query, "--limit", str(a.limit), "--include-children",
            "--include-one-shot", "--include-automated"]
    if a.since:
        base += ["--since", a.since]
    if a.agent:
        base += ["--agent", a.agent]
    if a.project:
        base += ["--project", a.project]
    if a.exclude_session:
        base += ["--exclude-session", a.exclude_session]
    mode = "hybrid" if a.hybrid else "lexical"
    rc, out, err = run(base + (["--hybrid"] if a.hybrid else []))
    if rc != 0 and a.hybrid:
        print(f"[semantic unavailable: {err.strip()[:160]}] falling back to lexical", file=sys.stderr)
        mode = "lexical (fallback)"
        rc, out, err = run(base)
    if rc != 0:
        print(err.strip()[:400], file=sys.stderr)
        return rc
    d = json.loads(out)
    cov = d.get("coverage") or {}
    print(f"mode={mode} coverage={json.dumps(cov)[:200]} next_cursor={d.get('next_cursor')}")
    for m in d.get("matches", []):
        sid = m.get("session_id")
        rel = "sub" if m.get("subordinate") else "top"
        snippet = (m.get("snippet") or "").replace("\n", " ")[: a.chars]
        print(f"- {m.get('timestamp','')[:19]} {m.get('agent')} {m.get('project')} {rel} {sid} "
              f"ord={m.get('ordinal')} [{m.get('location')}/{m.get('role')}] {snippet}")
    return 0


def messages(a) -> int:
    args = ["session", "messages", a.session, "--limit", str(a.limit)]
    if a.around is not None:
        args += ["--around", str(a.around), "--before", str(a.before), "--after", str(a.after)]
    if a.role:
        args += ["--role", a.role]
    rc, out, err = run(args)
    if rc != 0:
        print(err.strip()[:400], file=sys.stderr)
        return rc
    d = json.loads(out)
    for m in d.get("messages", []):
        text = (m.get("content") or "").replace("\n", " ")[: a.chars]
        print(f"- ord={m.get('ordinal')} {m.get('timestamp','')[:19]} {m.get('role')} {text}")
    nxt = d.get("next_from") or d.get("next_cursor")
    if nxt is not None:
        print(f"next_from={nxt}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--limit", type=int, default=10)
    p.add_argument("--since", default="30d"); p.add_argument("--agent"); p.add_argument("--project")
    p.add_argument("--exclude-session"); p.add_argument("--hybrid", action="store_true")
    p.add_argument("--chars", type=int, default=180); p.set_defaults(fn=search)
    p = sub.add_parser("messages"); p.add_argument("session", help="e.g. codex:<thread-id> or a Claude session id")
    p.add_argument("--around", type=int); p.add_argument("--before", type=int, default=6); p.add_argument("--after", type=int, default=6)
    p.add_argument("--role"); p.add_argument("--limit", type=int, default=20); p.add_argument("--chars", type=int, default=300)
    p.set_defaults(fn=messages)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
