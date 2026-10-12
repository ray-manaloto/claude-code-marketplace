#!/usr/bin/env python3
"""Explicit project-only tool and Python dependency lifecycle behind mise tasks."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DEV_CONFIG = ROOT / "mise.dev.toml"
DEV_LOCK = ROOT / "mise.dev.lock"
PY_LOCK = ROOT / "uv.lock"
OCI_FILES = (ROOT / "mise.toml", ROOT / "mise.lock")
TOOL_BACKENDS = {"python": "core:python", "uv": "aqua:astral-sh/uv"}
LOCK_PLATFORMS = {"macos-arm64", "linux-arm64", "linux-x64"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_tool_lock() -> None:
    """Reject stale or incomplete v3 lock data before an install or sync."""
    if not DEV_LOCK.is_file():
        raise RuntimeError("mise.dev.lock is missing; create it through deps:lock first")
    with DEV_CONFIG.open("rb") as source, DEV_LOCK.open("rb") as locked:
        config = tomllib.load(source)
        lock = tomllib.load(locked)
    requested = config.get("tools", {})
    entries = lock.get("tools", {})
    if set(requested) != set(TOOL_BACKENDS) or set(entries) != set(requested):
        raise RuntimeError("mise.dev.lock tools differ from mise.dev.toml")
    if lock.get("lockfile_version") != 3:
        raise RuntimeError("mise.dev.lock format changed; review its binding contract")
    for tool, version in requested.items():
        matches = entries[tool]
        if (not isinstance(version, str) or not isinstance(matches, list)
                or len(matches) != 1 or not isinstance(matches[0], dict)):
            raise RuntimeError(f"mise.dev.lock binding for {tool} is invalid")
        entry = matches[0]
        if (entry.get("version") != version or entry.get("specifiers") != [version]
                or entry.get("backend") != TOOL_BACKENDS[tool]):
            raise RuntimeError(f"mise.dev.lock binding for {tool} differs from mise.dev.toml")
        platforms = {
            key.removeprefix("platforms."): value
            for key, value in entry.items() if key.startswith("platforms.")
        }
        if not isinstance(platforms, dict) or set(platforms) != LOCK_PLATFORMS:
            raise RuntimeError(f"mise.dev.lock platforms for {tool} are incomplete")
        for platform in platforms.values():
            if (not isinstance(platform, dict)
                    or not str(platform.get("checksum", "")).startswith("sha256:")
                    or not platform.get("url")):
                raise RuntimeError(f"mise.dev.lock download for {tool} is incomplete")


def verify_local_tool_data() -> None:
    """Keep installers and lock metadata inside this physical checkout."""
    data = ROOT / ".mise"
    if data.is_symlink() or not data.resolve().is_relative_to(ROOT):
        raise RuntimeError("project mise data resolves outside this checkout")
    with DEV_CONFIG.open("rb") as source:
        requested = tomllib.load(source)["tools"]
    for candidate in (data / "installs", *(data / "installs" / tool / version
                                               for tool, version in requested.items())):
        if candidate.exists() and not candidate.resolve().is_relative_to(data):
            raise RuntimeError("project mise installation resolves outside this checkout")


def context() -> tuple[str, dict[str, str]]:
    if os.environ.get("MISE_OVERRIDE_CONFIG_FILENAMES") != DEV_CONFIG.name:
        raise RuntimeError("use ./dev/mise to select the development config")
    for key in ("MISE_GLOBAL_CONFIG_FILE", "MISE_SYSTEM_CONFIG_FILE"):
        if os.environ.get(key) != str(ROOT / "dev" / "empty-mise.toml"):
            raise RuntimeError(f"{key} must select the empty isolation config")
    if os.environ.get("MISE_DATA_DIR") != str(ROOT / ".mise"):
        raise RuntimeError("mise tool data directory is not project-scoped")
    mise = os.environ.get("MARKETPLACE_MISE_BIN")
    if not mise or not Path(mise).is_file():
        raise RuntimeError("the selected mise executable is missing")
    env = os.environ.copy()
    env["UV_PYTHON_DOWNLOADS"] = "never"
    env["UV_NO_CONFIG"] = "1"
    env["UV_PROJECT_ENVIRONMENT"] = str(ROOT / ".venv")
    env.pop("UV_NO_SYNC", None)
    env.pop("UV_FROZEN", None)
    return mise, env


def execute(argv: list[str], env: dict[str, str]) -> None:
    result = subprocess.run(argv, cwd=ROOT, env=env, check=False)
    if result.returncode:
        raise RuntimeError(f"{Path(argv[0]).name} exited {result.returncode}")


def selected_tool(mise: str, name: str, env: dict[str, str]) -> str:
    result = subprocess.run([mise, "which", name], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    if result.returncode or not Path(result.stdout.strip()).is_file():
        raise RuntimeError(f"project {name} is missing; run tools:prepare")
    return result.stdout.strip()


def self_test() -> None:
    """Exercise public task refusals in an isolated config with real HOME intact."""
    with tempfile.TemporaryDirectory(prefix="marketplace-bootstrap-") as temporary:
        scratch = Path(temporary) / "project"
        (scratch / "dev").mkdir(parents=True)
        for relative in (
            "dev/mise", "dev/bootstrap.py", "dev/empty-mise.toml",
            "mise.dev.toml", "mise.dev.lock", "pyproject.toml", "uv.lock",
            "mise.toml", "mise.lock",
        ):
            shutil.copy2(ROOT / relative, scratch / relative)
        (scratch / ".mise").symlink_to(ROOT / ".mise", target_is_directory=True)
        env = os.environ.copy()
        env["XDG_CONFIG_HOME"] = str(Path(temporary) / "isolated-config")

        def task(name: str, root: Path = scratch) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [str(root / "dev" / "mise"), "run", "--no-deps", "--skip-tools", name],
                cwd=temporary, env=env, capture_output=True, text=True, check=False,
            )

        positive = task("deps:check", ROOT)
        if positive.returncode or '"status": "pass"' not in positive.stdout:
            raise RuntimeError("unrelated-cwd/isolated-config positive task failed")
        env["MISE_TASK_SKIP_DEPENDS"] = "1"
        review = subprocess.run(
            [str(ROOT / "dev" / "mise"), "run", "--dry-run", "test:one-page"],
            cwd=temporary, env=env, capture_output=True, text=True, check=False,
        )
        if review.returncode or "deps:check" not in review.stdout + review.stderr:
            raise RuntimeError("inherited skip-depends bypassed the review prerequisite")
        env.pop("MISE_TASK_SKIP_DEPENDS")
        missing = task("deps:check")
        if missing.returncode == 0 or "project .venv is missing" not in missing.stderr:
            raise RuntimeError("missing-environment task did not refuse")
        (scratch / ".venv").mkdir()
        (scratch / ".venv" / "pyvenv.cfg").write_text("home = invalid\n")
        project = scratch / "pyproject.toml"
        original = project.read_text()
        if "githubkit==0.16.1" not in original:
            raise RuntimeError("expected pinned fixture input is missing")
        project.write_text(original.replace("githubkit==0.16.1", "githubkit==0.16.0"))
        drift = task("deps:check")
        if drift.returncode == 0 or "uv exited" not in drift.stderr:
            raise RuntimeError("lock-drift task did not refuse")
        project.write_text(original)
        config = scratch / "mise.dev.toml"
        config_text = config.read_text()
        config.write_text(config_text.replace('python = "3.15.0"', 'python = "3.14.0"'))
        tool_drift = task("deps:check")
        if tool_drift.returncode == 0 or "mise.dev.lock binding for python differs" not in tool_drift.stderr:
            raise RuntimeError("tool-lock drift task did not refuse")
        (scratch / "mise.dev.lock").unlink()
        no_lock = task("tools:prepare")
        if no_lock.returncode == 0 or "mise.dev.lock is missing" not in no_lock.stderr:
            raise RuntimeError("missing tool lock did not refuse")
        config.write_text(config_text)
        shutil.copy2(ROOT / "mise.dev.lock", scratch / "mise.dev.lock")
        escaped = task("tools:prepare")
        if escaped.returncode == 0 or "project mise data resolves outside" not in escaped.stderr:
            raise RuntimeError("symlinked tool-data directory did not refuse")
        print(json.dumps({"status": "pass", "checks": ["unrelated-cwd-isolated-config", "inherited-skip-depends", "missing-environment", "lock-drift", "tool-lock-drift", "missing-tool-lock", "symlinked-tool-data"]}, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("tools-prepare", "deps-lock", "deps-sync", "deps-check", "test"))
    action = parser.parse_args().action
    if action == "test":
        try:
            self_test()
        except (OSError, RuntimeError) as error:
            print(f"bootstrap test failed: {error}", file=sys.stderr)
            return 1
        return 0
    mise, env = context()
    protected = {path: digest(path) for path in OCI_FILES}
    try:
        if action == "tools-prepare":
            verify_tool_lock()
            verify_local_tool_data()
            data_ignore = ROOT / ".mise" / ".gitignore"
            data_ignore.parent.mkdir(parents=True, exist_ok=True)
            if data_ignore.exists() and data_ignore.read_text() != "*\n":
                raise RuntimeError("project mise data ignore rule differs")
            data_ignore.write_text("*\n")
            execute([mise, "install", "--locked"], env)
        elif action == "deps-lock":
            verify_local_tool_data()
            uv = selected_tool(mise, "uv", env)
            env["UV_PYTHON"] = selected_tool(mise, "python", env)
            execute([mise, "lock", "--platform", "macos-arm64,linux-arm64,linux-x64"], env)
            if not DEV_LOCK.is_file():
                raise RuntimeError("mise did not write mise.dev.lock")
            verify_tool_lock()
            execute([uv, "lock", "--no-python-downloads"], env)
        else:
            if not DEV_LOCK.is_file() or not PY_LOCK.is_file():
                raise RuntimeError("development locks are missing; run deps:lock")
            verify_tool_lock()
            uv = selected_tool(mise, "uv", env)
            env["UV_PYTHON"] = selected_tool(mise, "python", env)
            execute([env["UV_PYTHON"], "-I", "-B", "-c", "import ssl"], env)
            if action == "deps-sync":
                execute([uv, "lock", "--check", "--no-python-downloads"], env)
                execute([uv, "sync", "--locked", "--no-python-downloads"], env)
            elif action == "deps-check":
                if not (ROOT / ".venv" / "pyvenv.cfg").is_file():
                    raise RuntimeError("project .venv is missing; run deps:sync")
                execute([uv, "lock", "--check", "--offline", "--no-python-downloads"], env)
                execute([uv, "sync", "--check", "--locked", "--offline", "--no-python-downloads"], env)
                execute([uv, "run", "--no-sync", "--offline", "python", "-B", "-c", "import githubkit"], env)
        for path, original in protected.items():
            if digest(path) != original:
                raise RuntimeError(f"OCI input changed unexpectedly: {path.name}")
        print(json.dumps({"action": action, "status": "pass", "mise_dev_lock_sha256": digest(DEV_LOCK), "uv_lock_sha256": digest(PY_LOCK)} if PY_LOCK.is_file() else {"action": action, "status": "pass", "mise_dev_lock_sha256": digest(DEV_LOCK)}, sort_keys=True))
        return 0
    except (OSError, RuntimeError) as error:
        print(f"bootstrap failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
