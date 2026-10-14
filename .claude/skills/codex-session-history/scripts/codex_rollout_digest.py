#!/usr/bin/env python3
"""Digest a Codex rollout JSONL (or thread id) into a bounded markdown brief.

Resolves a thread id through ~/.codex/state_5.sqlite (read-only), streams the
rollout line by line so multi-hundred-MB files stay cheap, and emits only the
parts a takeover needs: session identity, settings timeline, every user prompt,
each turn's final agent message, compaction summaries, write-like tool calls,
spawned agents, git commits and token totals. Raw tool output is never copied.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

CODEX_HOME = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
STATE_DB = os.path.join(CODEX_HOME, "state_5.sqlite")
WRITE_HINT = re.compile(
    r"(apply_patch|git (commit|push|worktree|merge|cherry-pick|rebase|checkout -b|switch -c)|"
    r"\bcat\s*>|\btee\b|write_file|append_to_file|mkdir -p|> *[A-Za-z0-9_./-]+\.(md|json|py|toml|txt|sh)|"
    r"python3? +- *<<|mise run (delivery|issue|checkout):)",
    re.I,
)
COMMIT_RE = re.compile(r"\[([\w./-]+(?: \(root-commit\))?) ([0-9a-f]{7,40})\] (.{0,100})")
SHA_RE = re.compile(r"\b[0-9a-f]{40}\b")
SECRET_RE = re.compile(
    r"ghp_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{16,}|Bearer [A-Za-z0-9._-]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)


def resolve_rollout(spec: str) -> tuple[str, dict]:
    if os.path.isfile(spec):
        return spec, {}
    if not os.path.isfile(STATE_DB):
        raise SystemExit(f"no rollout file at {spec} and no {STATE_DB}")
    con = sqlite3.connect(f"file:{STATE_DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "select id, rollout_path, title, cwd, model, reasoning_effort, git_branch, git_sha, "
        "created_at, updated_at, archived, source, cli_version, tokens_used "
        "from threads where id = ? or id like ? order by id = ? desc, updated_at desc limit 21",
        (spec, f"{spec}%", spec),
    ).fetchall()
    con.close()
    if not rows:
        raise SystemExit(f"thread {spec} not found in {STATE_DB}")
    row = rows[0]
    if row["id"] != spec and len(rows) > 1:
        sys.stderr.write(f"ambiguous thread prefix {spec!r}; candidates:\n")
        sys.stderr.write("".join(f"  {r['id']}\n" for r in rows))
        raise SystemExit(2)
    path = row["rollout_path"]
    if not os.path.isabs(path):
        path = os.path.join(CODEX_HOME, path)
    return path, dict(row)


def ts(epoch: int | None) -> str:
    if not epoch:
        return "?"
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    out = []
    for part in content or []:
        if isinstance(part, dict):
            t = part.get("text")
            if isinstance(t, str):
                out.append(t)
            elif part.get("type") == "encrypted_content":
                out.append("<encrypted>")
    return "\n".join(out)


def mask(s: str) -> str:
    return SECRET_RE.sub("<redacted>", s)


def clip(s: str, n: int) -> str:
    s = mask((s or "").strip())
    return s if len(s) <= n else s[:n] + f" …[+{len(s) - n} chars]"


def digest(path: str, meta: dict, *, user_chars: int, final_chars: int, timeline_chars: int,
           last_n: int, write_cap: int) -> str:
    counts = collections.Counter()
    fn_names = collections.Counter()
    settings = []
    users = []
    assistants = []
    finals = []
    compactions = []
    writes = []
    agents = collections.Counter()
    spawns = []
    commits = []
    first_ts = last_ts = None
    session = {}
    last_usage = None
    turns = 0
    aborted = 0
    pending_call = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                counts["<bad json>"] += 1
                continue
            t = rec.get("timestamp")
            if t:
                first_ts = first_ts or t
                last_ts = t
            typ = rec.get("type")
            p = rec.get("payload") or {}
            counts[typ] += 1
            if typ == "session_meta":
                session = {k: p.get(k) for k in ("id", "forked_from_id", "forked_from_ordinal_exclusive",
                                                  "cwd", "originator", "cli_version", "source", "timestamp")}
                session["workspace_roots"] = p.get("runtime_workspace_roots")
            elif typ == "event_msg":
                et = p.get("type")
                if et == "thread_settings_applied":
                    s = p.get("thread_settings") or {}
                    entry = (s.get("model"), s.get("reasoning_effort"), s.get("cwd"),
                             (s.get("active_permission_profile") or {}).get("id"))
                    if not settings or settings[-1][1] != entry:
                        settings.append((t, entry))
                elif et == "task_started":
                    turns += 1
                elif et == "task_complete":
                    finals.append((t, rec.get("ordinal"), p.get("turn_id"), p.get("duration_ms"), p.get("last_agent_message") or ""))
                elif et == "turn_aborted":
                    aborted += 1
            elif typ == "response_item":
                pt = p.get("type")
                if pt == "message":
                    role = p.get("role")
                    txt = text_of(p.get("content"))
                    if role == "user":
                        users.append((t, rec.get("ordinal"), txt))
                    elif role == "assistant":
                        assistants.append((t, rec.get("ordinal"), txt))
                elif pt == "function_call":
                    name = p.get("name")
                    fn_names[name] += 1
                    args = p.get("arguments")
                    try:
                        a = json.loads(args) if isinstance(args, str) else (args or {})
                    except json.JSONDecodeError:
                        a = {"raw": str(args)[:200]}
                    if name in ("write_file", "append_to_file") and isinstance(a, dict):
                        writes.append((t, name, a.get("path") or a.get("file") or str(a)[:120]))
                    elif name == "spawn_agent" and isinstance(a, dict):
                        spawns.append((t, clip(json.dumps({k: v for k, v in a.items() if k != "message"}), 300),
                                       clip(str(a.get("message", "")), 400)))
                    elif name == "send_message" and isinstance(a, dict):
                        agents[a.get("recipient") or a.get("to") or "?"] += 1
                elif pt == "custom_tool_call":
                    name = p.get("name")
                    fn_names[f"custom:{name}"] += 1
                    inp = p.get("input")
                    if isinstance(inp, str) and WRITE_HINT.search(inp):
                        snippet = clip(inp.replace("\n", " "), 260)
                        writes.append((t, "exec", snippet))
                        pending_call[p.get("call_id")] = snippet
                elif pt == "custom_tool_call_output":
                    out = text_of(p.get("output"))
                    for m in COMMIT_RE.finditer(out):
                        commits.append((t, m.group(1), m.group(2), m.group(3)))
                elif pt == "agent_message":
                    agents[f"{p.get('author')}->{p.get('recipient')}"] += 1
            elif typ == "compacted":
                rh = p.get("replacement_history") or []
                summary = ""
                for item in reversed(rh):
                    if isinstance(item, dict) and item.get("role") != "developer":
                        summary = text_of(item.get("content"))
                        if summary:
                            break
                compactions.append((t, rec.get("ordinal"), clip(summary, 1500)))
            elif typ == "token_usage_record":
                last_usage = p.get("thread_token_usage") or last_usage

    size = os.path.getsize(path)
    out = []
    out.append(f"# Codex rollout digest: {session.get('id') or meta.get('id') or os.path.basename(path)}")
    out.append("")
    out.append(f"- rollout: `{path}` ({size/1e6:.1f} MB, {sum(counts.values())} records)")
    if meta:
        out.append(f"- title: {clip(meta.get('title',''), 160)}")
        out.append(f"- state_5: cwd=`{meta.get('cwd')}` model={meta.get('model')} effort={meta.get('reasoning_effort')} "
                   f"branch={meta.get('git_branch')} sha={meta.get('git_sha')} created={ts(meta.get('created_at'))} "
                   f"updated={ts(meta.get('updated_at'))} archived={meta.get('archived')} cli={meta.get('cli_version')}")
    out.append(f"- session_meta: forked_from=`{session.get('forked_from_id')}`@{session.get('forked_from_ordinal_exclusive')} "
               f"cwd=`{session.get('cwd')}` originator={session.get('originator')} cli={session.get('cli_version')}")
    out.append(f"- workspace_roots: {session.get('workspace_roots')}")
    out.append(f"- span: {first_ts} → {last_ts}; turns={turns} completed={len(finals)} aborted={aborted} compactions={len(compactions)}")
    if last_usage:
        out.append(f"- thread tokens: total={last_usage.get('total_tokens'):,} output={last_usage.get('output_tokens'):,} "
                   f"reasoning={last_usage.get('reasoning_output_tokens'):,}")
    out.append(f"- record types: {dict(counts.most_common())}")
    out.append(f"- tool calls: {dict(fn_names.most_common(25))}")
    out.append("")
    out.append("## Settings timeline (model, effort, cwd, permission)")
    for t, e in settings:
        out.append(f"- {t}: {e}")
    out.append("")
    out.append(f"## User messages ({len(users)})")
    for t, o, txt in users:
        out.append(f"### [{t}] ord={o}")
        out.append(clip(txt, user_chars))
        out.append("")
    out.append(f"## Turn-final agent messages ({len(finals)})")
    for t, o, turn, dur, msg in finals:
        out.append(f"### [{t}] ord={o} turn={turn} duration={round((dur or 0)/60000,1)}min")
        out.append(clip(msg, final_chars))
        out.append("")
    out.append(f"## Compaction summaries ({len(compactions)})")
    for t, o, s in compactions:
        out.append(f"- [{t}] ord={o}: {s}")
    out.append("")
    out.append(f"## Assistant message timeline ({len(assistants)}, clipped)")
    for t, o, txt in assistants:
        out.append(f"- [{t}] ord={o}: {clip(txt.replace(chr(10), ' '), timeline_chars)}")
    out.append("")
    out.append(f"## Last {last_n} assistant messages (fuller)")
    for t, o, txt in assistants[-last_n:]:
        out.append(f"### [{t}] ord={o}")
        out.append(clip(txt, final_chars))
        out.append("")
    out.append(f"## Git commits observed in tool output ({len(commits)})")
    for t, branch, sha, subj in commits:
        out.append(f"- [{t}] {branch} {sha} {subj}")
    out.append("")
    out.append(f"## Write-like tool calls ({len(writes)}; showing up to {write_cap})")
    for t, kind, what in writes[-write_cap:]:
        out.append(f"- [{t}] {kind}: {what}")
    out.append("")
    out.append(f"## Spawned agents ({len(spawns)}) and message traffic")
    for t, cfg, msg in spawns:
        out.append(f"- [{t}] {cfg}\n    first message: {msg}")
    out.append(f"- traffic: {dict(agents.most_common(30))}")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thread", help="thread id (prefix ok) or rollout .jsonl path")
    ap.add_argument("--out", help="write digest here instead of stdout")
    ap.add_argument("--user-chars", type=int, default=2500)
    ap.add_argument("--final-chars", type=int, default=3500)
    ap.add_argument("--timeline-chars", type=int, default=240)
    ap.add_argument("--last-n", type=int, default=15)
    ap.add_argument("--write-cap", type=int, default=400)
    a = ap.parse_args()
    path, meta = resolve_rollout(a.thread)
    md = digest(path, meta, user_chars=a.user_chars, final_chars=a.final_chars,
                timeline_chars=a.timeline_chars, last_n=a.last_n, write_cap=a.write_cap)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"wrote {a.out} ({len(md):,} chars)")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
