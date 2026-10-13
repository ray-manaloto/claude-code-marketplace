#!/usr/bin/env python3
"""Read-only queries over Codex's native SQLite state.

Subcommands:
  list      threads from state_5.sqlite, newest first (filter by cwd/title/days)
  show      one thread: metadata, rollout path, spawned child threads, turn ledger
  children  child threads spawned by a parent (state_5.thread_spawn_edges)
  turns     per-turn status/duration from thread_history_1.sqlite
  logs      tracing rows for a thread from logs_2.sqlite (bounded)

Every database is opened with SQLite's read-only URI mode, so a live Codex
process is never blocked and nothing is written. Output is compact JSON lines
or a table; pass --json for machine use.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

CODEX_HOME = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))


def ro(name: str) -> sqlite3.Connection:
    path = os.path.join(CODEX_HOME, name)
    if not os.path.isfile(path):
        raise SystemExit(f"missing {path}")
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def iso(epoch) -> str | None:
    if epoch is None:
        return None
    epoch = float(epoch)
    if epoch > 1e12:  # milliseconds
        epoch /= 1000.0
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_id(con: sqlite3.Connection, spec: str) -> str:
    row = con.execute("select id from threads where id = ? or id like ? order by updated_at desc limit 2",
                      (spec, f"{spec}%")).fetchall()
    if not row:
        raise SystemExit(f"thread {spec!r} not found")
    return row[0]["id"]


def emit(rows: list[dict], as_json: bool, cols: list[str]) -> None:
    if as_json:
        for r in rows:
            print(json.dumps(r, default=str))
        return
    for r in rows:
        print(" | ".join(str(r.get(c, ""))[:90] for c in cols))


def cmd_list(a) -> None:
    con = ro("state_5.sqlite")
    q = ("select id, title, cwd, model, reasoning_effort, git_branch, created_at, updated_at, archived, "
         "source, thread_source, cli_version, tokens_used from threads where 1=1")
    params: list = []
    if a.cwd:
        q += " and cwd like ?"; params.append(f"%{a.cwd}%")
    if a.title:
        q += " and title like ?"; params.append(f"%{a.title}%")
    if a.days:
        q += " and updated_at >= ?"; params.append(int(datetime.now(tz=timezone.utc).timestamp()) - a.days * 86400)
    if not a.archived:
        q += " and archived = 0"
    q += " order by updated_at desc limit ?"; params.append(a.limit)
    rows = []
    for r in con.execute(q, params):
        d = dict(r)
        d["created_at"], d["updated_at"] = iso(d["created_at"]), iso(d["updated_at"])
        d["title"] = (d["title"] or "").replace("\n", " ")[:120]
        rows.append(d)
    emit(rows, a.json, ["updated_at", "id", "model", "cwd", "title"])


def cmd_children(a) -> None:
    con = ro("state_5.sqlite")
    pid = resolve_id(con, a.thread)
    rows = []
    for r in con.execute(
        "select e.child_thread_id, e.status, t.title, t.cwd, t.model, t.updated_at from thread_spawn_edges e "
        "left join threads t on t.id = e.child_thread_id where e.parent_thread_id = ? order by t.updated_at", (pid,)):
        d = dict(r); d["updated_at"] = iso(d["updated_at"]); d["title"] = (d["title"] or "")[:100]
        rows.append(d)
    emit(rows, a.json, ["updated_at", "child_thread_id", "status", "model", "title"])


def cmd_turns(a) -> None:
    state = ro("state_5.sqlite")
    tid = resolve_id(state, a.thread)
    con = ro("thread_history_1.sqlite")
    rows = []
    for r in con.execute(
        "select turn_id, status, started_at, completed_at, duration_ms, rollout_ordinal, rollout_end_ordinal, error_json "
        "from thread_turns where thread_id = ? order by rollout_ordinal", (tid,)):
        d = dict(r)
        d["started_at"], d["completed_at"] = iso(d["started_at"]), iso(d["completed_at"])
        d["error_json"] = (d["error_json"] or "")[:160]
        rows.append(d)
    emit(rows, a.json, ["started_at", "status", "duration_ms", "rollout_ordinal", "turn_id", "error_json"])


def cmd_logs(a) -> None:
    con = ro("logs_2.sqlite")
    q = "select ts, level, target, substr(feedback_log_body, 1, ?) as body, file, line from logs where thread_id like ?"
    params: list = [a.chars, f"{a.thread}%"]
    if a.level:
        q += " and level = ?"; params.append(a.level.upper())
    if a.target:
        q += " and target like ?"; params.append(f"%{a.target}%")
    q += " order by ts desc, ts_nanos desc limit ?"; params.append(a.limit)
    rows = []
    for r in con.execute(q, params):
        d = dict(r); d["ts"] = iso(d["ts"]); rows.append(d)
    emit(list(reversed(rows)), a.json, ["ts", "level", "target", "body"])


def cmd_show(a) -> None:
    state = ro("state_5.sqlite")
    tid = resolve_id(state, a.thread)
    t = dict(state.execute("select * from threads where id = ?", (tid,)).fetchone())
    for k in ("created_at", "updated_at", "archived_at", "recency_at"):
        t[k] = iso(t.get(k))
    for k in ("created_at_ms", "updated_at_ms", "recency_at_ms"):
        t.pop(k, None)
    rollout = t.get("rollout_path") or ""
    if rollout and not os.path.isabs(rollout):
        rollout = os.path.join(CODEX_HOME, rollout)
    t["rollout_path"] = rollout
    t["rollout_exists"] = os.path.isfile(rollout)
    t["rollout_bytes"] = os.path.getsize(rollout) if t["rollout_exists"] else None
    kids = [dict(r) for r in state.execute(
        "select child_thread_id, status from thread_spawn_edges where parent_thread_id = ?", (tid,))]
    parent = state.execute("select parent_thread_id, status from thread_spawn_edges where child_thread_id = ?",
                           (tid,)).fetchone()
    t["spawned_children"] = len(kids)
    t["spawn_parent"] = dict(parent) if parent else None
    try:
        hist = ro("thread_history_1.sqlite")
        turns = hist.execute("select count(*) c, sum(status='completed') ok, max(completed_at) last from thread_turns "
                             "where thread_id = ?", (tid,)).fetchone()
        t["turns"] = {"count": turns["c"], "completed": turns["ok"], "last_completed": iso(turns["last"])}
    except SystemExit:
        t["turns"] = None
    coverage = os.path.join(CODEX_HOME, "research-coverage", tid)
    t["research_coverage_dir"] = coverage if os.path.isdir(coverage) else None
    lock = os.path.join(CODEX_HOME, "thread-writer-locks", f"{tid}.lock")
    t["writer_lock_mtime"] = iso(os.path.getmtime(lock)) if os.path.exists(lock) else None
    print(json.dumps(t, indent=2 if not a.json else None, default=str))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="JSON lines instead of a table")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--cwd"); p.add_argument("--title"); p.add_argument("--days", type=int)
    p.add_argument("--limit", type=int, default=30); p.add_argument("--archived", action="store_true"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("show"); p.add_argument("thread"); p.set_defaults(fn=cmd_show)
    p = sub.add_parser("children"); p.add_argument("thread"); p.set_defaults(fn=cmd_children)
    p = sub.add_parser("turns"); p.add_argument("thread"); p.set_defaults(fn=cmd_turns)
    p = sub.add_parser("logs"); p.add_argument("thread"); p.add_argument("--limit", type=int, default=40)
    p.add_argument("--level"); p.add_argument("--target"); p.add_argument("--chars", type=int, default=200); p.set_defaults(fn=cmd_logs)
    a = ap.parse_args()
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
