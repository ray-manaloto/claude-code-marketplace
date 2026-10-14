"""Append-only decisions ledger: approvals, decisions, operations and receipts (stdlib only).

Rows are JSON lines {id, ts, kind, subject, text, source, receipt}; ids are DL-<n> so that
they never read as a task_plan decision id (D1, D2, ...). Nothing here executes an operation.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

PLAN_ID = os.environ.get("PLAN_ID") or "2026-10-10-marketplace-macos-reflection-scaffold"
DEFAULT = Path(__file__).resolve().parents[1] / ".planning" / PLAN_ID / "decisions.jsonl"


def rows(path=DEFAULT):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def approved(path=DEFAULT):
    """Subjects named by an approval row; operations and receipts never count."""
    return {row["subject"] for row in rows(path) if row["kind"] == "approval"}


def pending(path=DEFAULT):
    """Operation rows that no receipt row closes yet."""
    ledger = rows(path)
    closed = {row["subject"] for row in ledger if row["kind"] == "receipt"}
    return [row for row in ledger if row["kind"] == "operation" and row["id"] not in closed]


def append(path, kind, subject, source, text="", receipt=None):
    row = {"id": f"DL-{len(rows(path)) + 1}",
           "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "kind": kind, "subject": subject, "text": text, "source": source, "receipt": receipt}
    with Path(path).open("a") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return row["id"]


def approval(args):
    done = approved(args.file)
    for subject in args.subject:
        if subject in done:
            print(f"{subject}: already approved (no-op)")
        else:
            done.add(subject)
            print(f"{append(args.file, 'approval', subject, args.source, args.text)} approval {subject}")
    return 0


def record(args):  # one operation (pending until a receipt) or one task_plan decision (no receipt)
    print(f"{append(args.file, args.kind, args.subject, args.source, args.text)} {args.kind} {args.subject}")
    return 0


def receipt(args):
    if args.id not in {row["id"] for row in pending(args.file)}:
        print(f"refused: {args.id} is not an open operation", file=sys.stderr)
        return 2
    if not args.path.is_file():
        print(f"refused: receipt path {args.path} is not a file", file=sys.stderr)
        return 2
    digest = hashlib.sha256(args.path.read_bytes()).hexdigest()
    proof = {"path": str(args.path), "rc": args.rc, "sha256": digest}
    print(f"{append(args.file, 'receipt', args.id, str(args.path), receipt=proof)} receipt {args.id}")
    return 0


class Parser(argparse.ArgumentParser):
    def error(self, message):  # usage errors exit 1; refusals exit 2
        self.print_usage(sys.stderr)
        self.exit(1, f"{self.prog}: error: {message}\n")


def main(argv=None):
    parser = Parser(prog="plan_decide.py")
    parser.add_argument("--file", type=Path, default=DEFAULT)
    sub = parser.add_subparsers(dest="kind", required=True, parser_class=Parser)
    for kind, many in (("approval", "+"), ("operation", None), ("decision", None)):
        command = sub.add_parser(kind)
        command.add_argument("--subject", nargs=many, required=True)
        command.add_argument("--source", required=True)
        command.add_argument("--text", default="")
        command.add_argument("--file", type=Path, default=argparse.SUPPRESS)
    command = sub.add_parser("receipt")
    command.add_argument("id")
    command.add_argument("--path", type=Path, required=True)
    command.add_argument("--rc", type=int)
    command.add_argument("--file", type=Path, default=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    return {"approval": approval, "operation": record, "decision": record, "receipt": receipt}[args.kind](args)


if __name__ == "__main__":
    sys.exit(main())
