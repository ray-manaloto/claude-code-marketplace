#!/usr/bin/env python3
"""Read-only checks using Python 3.11+ and the already installed Git/shells."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

if sys.version_info < (3, 11):
    sys.exit("Python 3.11+ is required; set MARKETPLACE_PYTHON to an installed interpreter.")
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "dev/research_refresh"))
from runtime_preflight import scrubbed  # noqa: E402  (single selector list for the CLI and harness)


def run(*args, env=None):
    return subprocess.run(args, cwd=ROOT, env=env, check=True, capture_output=True, text=True)


def check(baseline=False):
    paths = sorted(set(run("git", "ls-files", "--cached", "--others", "--exclude-standard", "-z").stdout.split("\0")) - {""})
    counts = {"json": 0, "toml": 0, "python": 0, "shell": 0, "baseline": 0}
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            continue
        if path.suffix == ".json":
            json.loads(path.read_text())
            counts["json"] += 1
        elif path.suffix == ".toml" or path.name == "mise.lock":
            tomllib.loads(path.read_text())
            counts["toml"] += 1
        elif path.suffix == ".py":
            compile(path.read_bytes(), str(path), "exec")
            counts["python"] += 1
        with path.open("rb") as stream:
            first_line = stream.readline(256).decode("utf-8", errors="replace").strip()
        if first_line in ("#!/bin/sh", "#!/usr/bin/env sh", "#!/bin/bash", "#!/usr/bin/env bash"):
            shell = "bash" if "bash" in first_line else "sh"
            run(shell, "-n", str(path))
            counts["shell"] += 1

    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    allowed = set(marketplace.get("allowCrossMarketplaceDependenciesOn", [])) | {marketplace["name"]}
    for plugin in marketplace["plugins"]:
        source = (ROOT / plugin["source"]).resolve()
        if not source.is_relative_to(ROOT):
            raise ValueError(f"Plugin source escapes repository: {plugin['source']}")
        manifest = json.loads((source / ".claude-plugin/plugin.json").read_text())
        if manifest["name"] != plugin["name"]:
            raise ValueError(f"Plugin identity mismatch: {plugin['name']}")
        for dependency in manifest.get("dependencies", []):
            if dependency["marketplace"] not in allowed:
                raise ValueError(f"Dependency marketplace is not permitted: {dependency['marketplace']}")

    if baseline:
        original = json.loads((ROOT / "evidence/onboarding/baseline-files.json").read_text())
        for entry in original["files"]:
            content = (ROOT / entry["path"]).read_bytes()
            if len(content) != entry["bytes"] or hashlib.sha256(content).hexdigest() != entry["sha256"]:
                raise ValueError(f"Original acceptance file changed: {entry['path']}")
            counts["baseline"] += 1

    run("git", "diff", "--check")
    run("git", "diff", "--cached", "--check")
    for directory, pattern in (("dev", "test_research_*.py"), ("dev/research_refresh", "test_*.py")):
        result = run(sys.executable, "-B", "-m", "unittest", "discover", "-s", directory, "-p", pattern,
                     env=scrubbed(os.environ))
        print(result.stderr, file=sys.stderr, end="")
    print(json.dumps({"status": "pass", "root": str(ROOT), "checks": counts}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Require original onboarding file hashes")
    try:
        check(parser.parse_args().baseline)
    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f"check failed: {error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr, file=sys.stderr, end="")
        sys.exit(1)
