#!/usr/bin/env python3
"""gh:write: scan a gh write's text, then run gh with the same argv (D179, R-174).

`./dev/mise run gh:write -- <gh args>`. Every argument, and every file one names (`--body-file`,
`-F <file>`, `-F key=@file`, `--input`, `--notes-file`, or a bare path), passes the issue route's
scan: the pinned betterleaks with the repository config. A hit exits 2 naming the argument position
and the rule id, never the text, and gh never runs. A `-` argument reads stdin once, scans it and
hands it to gh; otherwise gh gets no stdin, so it cannot prompt for unscanned text.
"""
# D179 (2026-10-14): dated exception to D92/D113 (rule 14) until the D131 C++ port (CT-02b.4).
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from issue_amend import Refusal, refused, scan


def outbound(args: list[str]) -> tuple[dict, bytes | None]:
    """Each argument's text, plus each file or stdin it names, keyed by its 1-based position."""
    fields: dict[str, str] = {}
    data = None
    for index, arg in enumerate(args, 1):
        fields[f"arg {index}"] = arg
        short = arg[2:] if arg[:1] == "-" and arg[1:2] not in ("", "-") else ""
        for candidate in {arg, arg.partition("=")[2], arg.partition("=@")[2], short} - {""}:
            if candidate == "-":
                data = sys.stdin.buffer.read() if data is None else data
                fields[f"arg {index} stdin"] = data.decode("utf-8", "replace")
                continue
            try:
                path = Path(candidate)
                regular, special = path.is_file(), path.exists() and not path.is_dir()
            except (OSError, ValueError):  # not a path (too long, NUL)
                continue
            if regular:
                text = path.read_bytes().decode("utf-8", "replace")
                fields[f"arg {index} file"] = fields.get(f"arg {index} file", "") + text
            elif special:  # a FIFO or device could hand gh unscanned text
                raise Refusal(f"arg {index} names a file the scan cannot read; nothing sent")
    return fields, data


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: ./dev/mise run gh:write -- <gh args>", file=sys.stderr)
        return 1
    try:
        fields, data = outbound(args)
        scan("gh:write", fields)
    except (Refusal, OSError) as error:
        print(refused(error), file=sys.stderr)
        return 2
    stdin = {"input": data} if data is not None else {"stdin": subprocess.DEVNULL}
    try:
        return subprocess.run(["gh", *args], check=False, **stdin).returncode
    except OSError:
        print("REFUSED: gh could not start; nothing sent", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
