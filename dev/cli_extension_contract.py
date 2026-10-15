"""Offline v2 CLI dispatch contract; run with the pinned #24 Python environment.

This is a reference seam, not a shipped ``issues`` implementation. A future
public dispatcher can use the same additive rule without changing trackers.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Callable

from kb_setup.research import cli, trackers

import legacy_trackers_fixture as legacy


V2_HELP = "aggregated-research <verb> [args...]\n  verbs: trackers issues\n"
LEGACY_HELP = "aggregated-research <verb> [args...]\n  verbs: trackers\n"


def assert_v2_help(value: str) -> None:
    """Versioned successor to the three frozen OCI ``verbs: trackers`` checks."""
    if value != V2_HELP:
        raise AssertionError(f"unexpected v2 help: {value!r}")


def dispatch(argv: list[str], issues: Callable[[list[str]], int]) -> int:
    if argv and argv[0] == "issues":
        return issues(argv[1:])
    if argv and argv[0] in ("--help", "-h"):
        print(V2_HELP, end="")
        return 0
    # The pinned public implementation owns trackers, errors and exit codes.
    return cli.main(argv)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: cli_extension_contract.py RECEIPT_PATH")
    # The installed CLI opens this path even when the fixture emits no events.
    os.environ.pop("KB_EVENTS_JSONL", None)
    receipt = Path(sys.argv[1]).resolve()
    root = Path(__file__).resolve().parents[1]
    frozen = root / "evidence/legacy-trackers"
    require(legacy.PIN == "a872cb016feb5512994b37330ce6a387c5732253", "fixture pin drift")
    capture = json.loads((frozen / "capture.json").read_text())
    require(capture["pinned_commit"] == legacy.PIN, "capture pin drift")
    package = Path(trackers.__file__).resolve().parents[1]
    metadata = next(package.parent.glob("kb_setup-*.dist-info/direct_url.json"))
    direct = json.loads(metadata.read_text())
    require(direct["vcs_info"]["commit_id"] == legacy.PIN, "installed commit drift")
    require(direct["url"] == "https://github.com/ray-manaloto/knowledge-base.git", "installed URL drift")
    require(sha256(metadata) == capture["direct_url_sha256"], "installed metadata drift")
    for name, expected in capture["installed_module_sha256"].items():
        require(sha256(package / name) == expected, f"installed module drift: {name}")

    with contextlib.redirect_stdout(io.StringIO()) as stdout:
        help_rc = cli.main(["--help"])
    require(help_rc == 0 and stdout.getvalue() == LEGACY_HELP, "legacy help drift")
    with contextlib.redirect_stdout(io.StringIO()) as stdout:
        v2_help_rc = dispatch(["--help"], lambda _: 99)
    require(v2_help_rc == 0, "v2 help return code")
    assert_v2_help(stdout.getvalue())

    calls: list[list[str]] = []

    def fixture_issues(args: list[str]) -> int:
        calls.append(args)
        return 17

    require(dispatch(["issues", "example/project", "needle"], fixture_issues) == 17, "issues return code")
    require(calls == [["example/project", "needle"]], "issues argument routing")
    with contextlib.redirect_stderr(io.StringIO()) as stderr:
        unknown_rc = dispatch(["bogus"], fixture_issues)
    require(unknown_rc == 2, "unknown-verb return code")
    require(stderr.getvalue() == "aggregated-research: unknown verb 'bogus'\n", "unknown-verb diagnostic")

    repo = legacy.REPO
    at = legacy.AT
    empty = {"total_count": 0, "items": []}
    cases = {
        "hit": ("needle", {
            ("api", f"repos/{repo}"): {"has_issues": True, "has_discussions": False},
            legacy.search("issue", "needle"): {"total_count": 1, "items": [{
                "html_url": f"https://github.com/{repo}/issues/1",
                "title": "Synthetic issue", "body": "First line\nSecond line",
                "updated_at": at,
            }]},
            legacy.search("pr", "needle"): empty,
        }),
        "null": ("unfindable", {
            ("api", f"repos/{repo}"): {"has_issues": True, "has_discussions": False},
            legacy.search("issue", "unfindable"): empty,
            legacy.search("pr", "unfindable"): empty,
            legacy.search("issue", None): empty,
            legacy.search("pr", None): {"total_count": 2, "items": []},
        }),
    }
    results: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="marketplace-cli-v2-") as tmp:
        for name, (term, replies) in cases.items():
            seen: list[tuple[str, ...]] = []

            def fake_gh(argv: tuple[str, ...]) -> tuple[int, str, str]:
                seen.append(argv)
                if argv not in replies:
                    raise AssertionError(f"unexpected GitHub command: {argv!r}")
                return 0, json.dumps(replies[argv], separators=(",", ":")), ""

            trackers._run_gh = fake_gh
            trackers._ran_at = lambda now=None: at
            output = Path(tmp) / f"{name}.json"
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = dispatch(["trackers", repo, term, "--out", str(output)], fixture_issues)
            require(rc == 0 and stdout.getvalue() == f"[aggregated-research] wrote {output}\n", f"{name} return/output")
            require(seen == list(replies), f"{name} command ordering")
            require(output.read_bytes() == (frozen / f"{name}.json").read_bytes(), f"{name} record drift")
            results[name] = sha256(output)
    require(calls == [["example/project", "needle"]], "trackers crossed into issues handler")
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({
        "contract": "additive-cli-v2-reference", "pinned_legacy_commit": legacy.PIN,
        "pinned_capture_sha256": sha256(frozen / "capture.json"),
        "legacy_help": LEGACY_HELP, "v2_help": V2_HELP,
        "help_rc": help_rc, "v2_help_rc": v2_help_rc, "unknown_rc": unknown_rc,
        "issues_fixture_rc": 17, "trackers_fixture_sha256": results,
        "provider_calls": 0, "public_v2_cli_shipped": False,
    }, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"state": "PASS", "receipt": str(receipt)}))


if __name__ == "__main__":
    main()
