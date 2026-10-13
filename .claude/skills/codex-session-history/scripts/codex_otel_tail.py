#!/usr/bin/env python3
"""Summarize the local Codex OpenTelemetry file export.

The local collector (launchd com.opensymphony.codex-otel) receives Codex OTLP
logs on 127.0.0.1:4318 and writes redacted JSON lines (bodies stripped, only
service.name / service.version / deployment.environment.name kept), rotating
at 10 MB. Input: --glob, else $CODEX_OTEL_FILE (one file) when set, else the
$CODEX_OTEL_FILE_GLOB pattern, else the launchd collector's default path. This counts records per service/version
and time window so you can confirm a Codex build was active at a given time;
it cannot recover prompt text, which the collector deliberately drops.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

DEFAULT = os.path.expanduser("~/Library/Application Support/OpenSymphony/codex-otel/codex-otel*.jsonl")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--glob", default=os.environ.get("CODEX_OTEL_FILE") or os.environ.get("CODEX_OTEL_FILE_GLOB", DEFAULT))
    ap.add_argument("--max-bytes", type=int, default=50_000_000, help="read at most this many bytes per file from the end")
    a = ap.parse_args()
    files = sorted(glob.glob(a.glob))
    if not files:
        print(f"no files match {a.glob}")
        return 1
    for path in files:
        size = os.path.getsize(path)
        counts: collections.Counter = collections.Counter()
        first = last = None
        with open(path, "rb") as fh:
            if size > a.max_bytes:
                fh.seek(size - a.max_bytes)
                fh.readline()
            for raw in fh:
                try:
                    rec = json.loads(raw)
                except json.JSONDecodeError:
                    counts["<bad>"] += 1
                    continue
                for rl in rec.get("resourceLogs", []):
                    attrs = {kv.get("key"): list((kv.get("value") or {}).values())[0]
                             for kv in (rl.get("resource") or {}).get("attributes", []) if kv.get("key")}
                    key = f"{attrs.get('service.name')}@{attrs.get('service.version')}/{attrs.get('deployment.environment.name')}"
                    for sl in rl.get("scopeLogs", []):
                        for lr in sl.get("logRecords", []):
                            counts[key] += 1
                            t = lr.get("timeUnixNano") or lr.get("observedTimeUnixNano")
                            if t:
                                first = min(first or t, t)
                                last = max(last or t, t)
        print(f"== {os.path.basename(path)} ({size/1e6:.1f} MB) first={first} last={last}")
        for k, v in counts.most_common(10):
            print(f"   {v:7d}  {k}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
