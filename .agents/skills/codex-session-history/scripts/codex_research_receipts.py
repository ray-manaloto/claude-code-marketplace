#!/usr/bin/env python3
"""List the research-fanout receipts a Codex thread produced.

Codex's global hook writes one directory per hook turn under
~/.codex/research-coverage/<thread-id>/<turn-id>/ with manifest.json,
required.json and per-provider <source>.json + .raw files. This prints the
policy, query, strict-five flag and each source's recorded status without
loading raw provider bytes, so a successor can see which research is already
settled and which routes failed (quota, 402, validator rejection) before
spending a new request.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

CODEX_HOME = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
ROOT = os.path.join(CODEX_HOME, "research-coverage")


def load(path: str):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return {"_error": str(exc)[:120]}


def source_status(d: dict) -> str:
    for key in ("status", "outcome", "result", "state"):
        if isinstance(d.get(key), str):
            return d[key]
    if "items" in d and isinstance(d["items"], list):
        return f"items={len(d['items'])}"
    if "count" in d:
        return f"count={d['count']}"
    return ",".join(list(d.keys())[:4])


def describe_run(run_dir: str, verbose: bool) -> dict:
    manifest = load(os.path.join(run_dir, "manifest.json"))
    out = {
        "run": os.path.basename(run_dir),
        "generated_at": manifest.get("generated_at"),
        "policy": manifest.get("policy_version"),
        "strict_five": manifest.get("strict_five"),
        "request_id": manifest.get("request_id"),
        "query": (manifest.get("query") or "")[:140],
        "sources": {},
    }
    srcs = manifest.get("sources")
    if isinstance(srcs, list):
        for s in srcs:
            if isinstance(s, dict):
                name = s.get("name") or s.get("source") or s.get("id") or "?"
                out["sources"][name] = {k: s.get(k) for k in ("status", "sha256", "items", "error", "provisional", "fallback")
                                        if k in s}
    for fn in sorted(os.listdir(run_dir)):
        if fn.endswith(".json") and fn not in ("manifest.json", "required.json"):
            name = fn[:-5]
            d = load(os.path.join(run_dir, fn))
            out["sources"].setdefault(name, {})["file_status"] = source_status(d) if isinstance(d, dict) else type(d).__name__
    if verbose:
        out["required"] = load(os.path.join(run_dir, "required.json"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("thread", nargs="?", help="thread id or prefix; omit to list threads with receipts")
    ap.add_argument("--run", help="only this turn/run id (prefix ok)")
    ap.add_argument("--verbose", action="store_true", help="include required.json")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(ROOT):
        raise SystemExit(f"missing {ROOT}")
    if not a.thread:
        threads = sorted(os.listdir(ROOT), key=lambda t: os.path.getmtime(os.path.join(ROOT, t)), reverse=True)
        for t in threads[:40]:
            p = os.path.join(ROOT, t)
            if os.path.isdir(p):
                runs = [r for r in os.listdir(p) if os.path.isdir(os.path.join(p, r))]
                print(f"{t}  runs={len(runs)}")
        return 0
    matches = [t for t in os.listdir(ROOT) if t.startswith(a.thread)]
    if not matches:
        raise SystemExit(f"no receipts for {a.thread!r}")
    tdir = os.path.join(ROOT, matches[0])
    runs = sorted(r for r in os.listdir(tdir) if os.path.isdir(os.path.join(tdir, r)))
    if a.run:
        runs = [r for r in runs if r.startswith(a.run)]
    for r in runs:
        d = describe_run(os.path.join(tdir, r), a.verbose)
        if a.json:
            print(json.dumps(d))
        else:
            print(f"== {d['run']}  {d['generated_at']}  policy={d['policy']} strict_five={d['strict_five']}")
            print(f"   query: {d['query']}")
            for name, s in d["sources"].items():
                print(f"   - {name}: {json.dumps(s)[:160]}")
    plans = [f for f in os.listdir(tdir) if f.endswith("plan.json")]
    if plans:
        print(f"plans: {plans}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
