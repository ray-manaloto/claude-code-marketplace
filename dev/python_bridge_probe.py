"""Compare the pinned trackers router in-process and as a CLI child, offline.

Run with the installed pinned kb-setup Python. A private PATH contains only a
synthetic gh executable; every result is compared with ticket #24's fixture.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

from kb_setup.research import cli


ROOT = Path(__file__).resolve().parents[1]
PIN = "a872cb016feb5512994b37330ce6a387c5732253"
CAPTURE = ROOT / "evidence/legacy-trackers/capture.json"
FIXTURE = ROOT / "evidence/legacy-trackers/hit.json"
ROUNDS = 5
STUB = r'''#!PYTHON
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with Path(os.environ["BRIDGE_GH_CALLS"]).open("a") as log:
    log.write(json.dumps(args) + "\n")
if os.environ.get("BRIDGE_GH_FAIL") == "1":
    print("synthetic gh failure", file=sys.stderr)
    raise SystemExit(42)
if args == ["api", "repos/example/project"]:
    value = {"has_issues": True, "has_discussions": False}
elif args == ["api", "-X", "GET", "search/issues", "-f",
              "q=repo:example/project is:issue needle"]:
    value = {"total_count": 1, "items": [{
        "html_url": "https://github.com/example/project/issues/1",
        "title": "Synthetic issue", "body": "First line\nSecond line",
        "updated_at": "2026-08-28T02:07:38Z"}]}
elif args == ["api", "-X", "GET", "search/issues", "-f",
              "q=repo:example/project is:pr needle"]:
    value = {"total_count": 0, "items": []}
else:
    print("unexpected synthetic gh request", file=sys.stderr)
    raise SystemExit(99)
print(json.dumps(value))
'''


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(record: dict[str, object]) -> dict[str, object]:
    result = dict(record)
    result.pop("ran_at")
    return result


@contextlib.contextmanager
def process_environment(env: dict[str, str]):
    old = os.environ.copy()
    os.environ.clear()
    os.environ.update(env)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python_bridge_probe.py OUTPUT_JSON")
    capture = json.loads(CAPTURE.read_text())
    assert capture["pinned_commit"] == PIN
    assert Path(capture["installed_python"]).resolve() == Path(sys.executable).resolve()
    assert sha(FIXTURE.read_bytes()) == capture["cases"]["hit"]["sha256"]
    cli_executable = Path(capture["installed_cli"])
    assert cli_executable.is_file()
    expected = normalized(json.loads(FIXTURE.read_text()))

    with tempfile.TemporaryDirectory(prefix="bridge-probe-") as work:
        tmp = Path(work)
        stub = tmp / "gh"
        stub.write_text(STUB.replace("#!PYTHON", f"#!{sys.executable}", 1))
        stub.chmod(0o700)
        stub_sha = sha(stub.read_bytes())
        calls = tmp / "calls.jsonl"
        base_env = {"PATH": str(tmp), "BRIDGE_GH_CALLS": str(calls),
                    "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C"}

        def run(mode: str, *, fail: bool = False) -> dict[str, object]:
            calls.write_text("")
            env = dict(base_env)
            if fail:
                env["BRIDGE_GH_FAIL"] = "1"
            args = ["trackers", "example/project", "needle"]
            begin = time.perf_counter_ns()
            if mode == "helper":
                result = subprocess.run([str(cli_executable), *args], env=env,
                                        capture_output=True, text=True, timeout=30)
                rc, stdout, stderr = result.returncode, result.stdout, result.stderr
            else:
                output, errors = io.StringIO(), io.StringIO()
                with process_environment(env), contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    rc = cli.main(args)
                stdout, stderr = output.getvalue(), errors.getvalue()
            elapsed_ms = round((time.perf_counter_ns() - begin) / 1_000_000, 3)
            observed_calls = [json.loads(line) for line in calls.read_text().splitlines()]
            if fail:
                assert rc == 42 and not stdout.strip() and "synthetic gh failure" in stderr
                assert len(observed_calls) == 1
            else:
                assert rc == 0 and not stderr.strip()
                assert normalized(json.loads(stdout)) == expected
                assert len(observed_calls) == 3
            return {"rc": rc, "elapsed_ms": elapsed_ms, "gh_calls": len(observed_calls)}

        samples = {"embedded": [], "helper": []}
        for _ in range(ROUNDS):
            for mode in ("embedded", "helper"):
                samples[mode].append(run(mode))
        failures = {mode: run(mode, fail=True) for mode in ("embedded", "helper")}

    report = {
        "state": "PASS", "kind": "offline synthetic bridge comparison",
        "pinned_commit": PIN, "prerequisite_capture_sha256": sha(CAPTURE.read_bytes()),
        "fixture_sha256": sha(FIXTURE.read_bytes()), "fake_gh_sha256": stub_sha,
        "installed_python": sys.executable, "installed_cli": str(cli_executable),
        "python_version": platform.python_version(), "machine": platform.machine(),
        "rounds_per_mode": ROUNDS, "samples": samples, "failure_controls": failures,
        "median_ms": {mode: statistics.median(row["elapsed_ms"] for row in values)
                      for mode, values in samples.items()},
        "comparison": "records match ticket 24 hit fixture after ignoring generated ran_at",
        "timestamp_normalized": ["ran_at"], "real_gh_calls": 0,
    }
    out = Path(sys.argv[1]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"state": report["state"], "report": str(out)}))


if __name__ == "__main__":
    main()
