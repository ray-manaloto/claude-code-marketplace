"""Capture deterministic public trackers records from the pinned installed CLI.

Run with the Python interpreter inside the existing pinned knowledge-base pipx
environment. GitHub calls are replaced at the single adapter boundary; no
provider request or dependency installation is made.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

from kb_setup.research import cli, trackers


PIN = "a872cb016feb5512994b37330ce6a387c5732253"
AT = "2026-08-28T02:07:38Z"
REPO = "example/project"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def search(kind: str, term: str | None) -> tuple[str, ...]:
    query = f"repo:{REPO} is:{kind}"
    if term is not None:
        query += f" {term}"
    return ("api", "-X", "GET", "search/issues", "-f", f"q={query}")


def run_case(out: Path, term: str, replies: dict[tuple[str, ...], object]) -> dict[str, object]:
    seen: list[tuple[str, ...]] = []

    def fake_gh(argv: tuple[str, ...]) -> tuple[int, str, str]:
        seen.append(argv)
        if argv not in replies:
            raise AssertionError(f"unexpected GitHub command: {argv!r}")
        return 0, json.dumps(replies[argv], separators=(",", ":")), ""

    trackers._run_gh = fake_gh
    trackers._ran_at = lambda now=None: AT
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        rc = cli.main(["trackers", REPO, term, "--out", str(out)])
    assert rc == 0
    assert output.getvalue() == f"[aggregated-research] wrote {out}\n"
    record = json.loads(out.read_text())
    assert record["adapter"] == "trackers"
    assert record["tier"] == "cheap"
    assert record["question"] == f"{REPO} {term}"
    assert record["ran_at"] == AT
    assert seen == list(replies)
    return {"returncode": rc, "commands": [list(row) for row in seen], "sha256": digest(out)}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: legacy_trackers_fixture.py OUTPUT_DIRECTORY")
    out_dir = Path(sys.argv[1]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    os.environ.pop("KB_EVENTS_JSONL", None)

    package = Path(trackers.__file__).resolve().parents[1]
    metadata = next(package.parent.glob("kb_setup-*.dist-info/direct_url.json"))
    direct = json.loads(metadata.read_text())
    assert direct["vcs_info"]["commit_id"] == PIN
    assert direct["url"] == "https://github.com/ray-manaloto/knowledge-base.git"
    executable = Path(sys.executable).parent / "aggregated-research"
    assert executable.is_file()
    controls = {}
    for name, arg, expected_rc in (("help", "--help", 0), ("unknown", "bogus", 2)):
        result = subprocess.run([str(executable), arg], capture_output=True, text=True, timeout=15)
        assert result.returncode == expected_rc
        controls[name] = {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    assert controls["help"]["stdout"] == "aggregated-research <verb> [args...]\n  verbs: trackers\n"
    assert controls["unknown"]["stderr"] == "aggregated-research: unknown verb 'bogus'\n"

    repo_reply = {"has_issues": True, "has_discussions": False}
    empty = {"total_count": 0, "items": []}
    hit_replies = {
        ("api", f"repos/{REPO}"): repo_reply,
        search("issue", "needle"): {"total_count": 1, "items": [{
            "html_url": "https://github.com/example/project/issues/1",
            "title": "Synthetic issue", "body": "First line\nSecond line",
            "updated_at": AT,
        }]},
        search("pr", "needle"): empty,
    }
    hit = run_case(out_dir / "hit.json", "needle", hit_replies)
    hit_record = json.loads((out_dir / "hit.json").read_text())
    assert hit_record["total_count"] == 1
    assert [item["kind"] for item in hit_record["hits"]] == ["issue"]
    assert hit_record["hits"][0]["snippet"] == "First line Second line"
    assert hit_record["null_result"] is None

    null_replies = {
        ("api", f"repos/{REPO}"): repo_reply,
        search("issue", "unfindable"): empty,
        search("pr", "unfindable"): empty,
        search("issue", None): empty,
        search("pr", None): {"total_count": 2, "items": []},
    }
    null = run_case(out_dir / "null.json", "unfindable", null_replies)
    null_record = json.loads((out_dir / "null.json").read_text())
    assert null_record["total_count"] == 0 and null_record["hits"] == []
    assert [(arm["kind"], arm["result"], arm["discriminates"])
            for arm in null_record["null_result"]["arms"]] == [
                ("issue", "total_count=0", False), ("pr", "total_count=2", True)]

    sources = {
        name: digest(package / name)
        for name in ("research/cli.py", "research/trackers.py", "generated/research_record.py", "cli.py")
    }
    receipt = {"pinned_commit": PIN, "installed_python": sys.executable,
               "installed_cli": str(executable), "direct_url_sha256": digest(metadata),
               "installed_module_sha256": sources, "controls": controls,
               "cases": {"hit": hit, "null": null},
               "provider_calls": 0, "source_checkout_access": "none"}
    (out_dir / "capture.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"state": "PASS", "capture": str(out_dir / "capture.json")}))


if __name__ == "__main__":
    main()
