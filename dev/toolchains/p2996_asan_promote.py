"""Promote one qualified ASan library and verify its installed loader path."""

import argparse
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

from gcc_install import ROOT, census, digest, read
from mise_runtime import function, load
from mise_renovate import protected as original_protected
import p2996_asan_runtime as asan
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_sanitizers import admit_editors
from vcpkg_fmt import build_environment

EVIDENCE = ROOT / "evidence/p2996-asan-promotion"
CONTRACT_SHA = "982b75c01ceb6daaf87242c54880b74da5c2a12bfc380543ce207f266f5d85d8"


def transition(directory, target, replacement, before, after, apply, qualify, report, save):
    """Keep the original backup and restore only a known replacement on failure."""
    backup, staged = directory / "original.dylib", directory / "staged.dylib"
    assert asan.identity(target) == before
    shutil.copyfile(target, backup)
    backup.chmod(0o755)
    assert asan.identity(backup) == before
    shutil.copyfile(replacement, staged)
    staged.chmod(0o755)
    assert asan.identity(staged) == after
    report["backup"] = {"path": str(backup), **before}
    save()
    try:
        report["mutation_started"] = True
        save()
        apply("promote", staged, before, after)
        qualify(True)
    except BaseException:
        handlers = {s: signal.signal(s, signal.SIG_IGN) for s in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)}
        try:
            actual = asan.identity(target)
            assert actual in (before, after), "unknown target identity; backup retained, no overwrite"
            if actual == after:
                assert asan.identity(backup) == before
                restore = directory / "restore.dylib"
                shutil.copyfile(backup, restore)
                restore.chmod(0o755)
                apply("restore", restore, after, before)
            assert asan.identity(target) == before
            report["recovery"] = "original restored" if actual == after else "original already present"
            qualify(False)
        except BaseException as recovery_error:
            report["recovery_error"] = repr(recovery_error)
            raise
        finally:
            for signum, handler in handlers.items():
                signal.signal(signum, handler)
            save()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--promote", action="store_true", required=True)
    directory = parser.parse_args().run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.parent != Path.home() / ".local/state/marketplace-tool-foundation":
        parser.error("use a new normalized directory directly under the private foundation root")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    report = {"state": "running", "helper_sha256": digest(Path(__file__)), "commands": [], "cells": {}, "mutation_started": False}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    base_env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}
    env, promoted = dict(base_env), False

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def guard():
        assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
        data, runtime = load(EVIDENCE / "contract.json"), asan.contract()
        assert all(digest(ROOT / p) == sha for p, sha in data["inputs"].items())
        assert data["target"] == runtime["target"] and data["after"] == runtime["current_asan"]
        assert data["before"] == {k: runtime["previous_record"][k] for k in ("sha256", "bytes", "mode")}
        assert data["replacement"] == runtime["qualified_replacement"]["path"] and data["target"] not in data["source_inputs"]
        assert asan.identity(Path(data["replacement"])) == data["replacement_identity"]
        expected_tools = dict(data["tools"])
        assert expected_tools[data["target"]] == data["before"]["sha256"]
        if promoted:
            expected_tools[data["target"]] = data["after"]["sha256"]
        assert all(digest(Path(p)) == sha for p, sha in (expected_tools | data["source_inputs"]).items())
        assert all(digest(Path(row["path"])) == row["sha256"] for rows in data["abi_inputs"].values() for row in rows)
        assert sys.executable in data["tools"] and digest(LOCK_MODULE) == LOCK_SHA
        assert digest(Path(__file__)) == report["helper_sha256"]
        assert asan.identity(Path(data["target"])) == data["after" if promoted else "before"]
        (asan.protected if promoted else original_protected)()
        return data

    native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                      globals() | {"directory": directory, "report": report, "env": env, "save": save})

    def run(label, argv, timeout=60, descriptor=None, expected=0):
        assert label not in [row["case"] for row in report["commands"]]
        try:
            result = native(label, argv, timeout=timeout, descriptor=descriptor)
        except AssertionError:
            assert expected != 0 and report["commands"][-1]["case"] == label
            assert report["commands"][-1]["returncode"] == expected
            result = (directory / (label + ".stdout")).read_text()
        else:
            assert expected == 0, "negative control unexpectedly passed"
        report["commands"][-1].update(expected_returncode=expected, timeout_seconds=timeout)
        save()
        return result

    def source_state(stage):
        source = contract["source_provenance"]
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source["path"]]
        for name, revision in (("head", "HEAD"), ("tree", "HEAD^{tree}")):
            assert run(stage + "-" + name, git + ["rev-parse", revision]).strip() == source[name]
        run(stage + "-diff", git + ["diff", "--no-ext-diff", "--binary"])
        assert digest(directory / (stage + "-diff.stdout")) == source["diff_sha256"]
        assert run(stage + "-status", git + ["status", "--porcelain", "--untracked-files=all"]) == (ROOT / source["status"]).read_text()

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        contract = guard()
        admission, review = [load(EVIDENCE / name) for name in ("admission.json", "pre-run-review.json")]
        assert admission["helper_sha256"] == review["helper_sha256"] == report["helper_sha256"]
        assert admission["contract_sha256"] == review["contract_sha256"] == CONTRACT_SHA
        assert admission["review_sha256"] == digest(EVIDENCE / "pre-run-review.json")
        assert review["result"].startswith("PASS") and not review["findings"]
        assert admission["run_directory"] == str(directory)
        report["admission_sha256"] = digest(EVIDENCE / "admission.json")
        report["writer_census_before"] = census()
        assert run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip() == contract["base_head"]
        normal = run("default-before", normal_argv)
        assert normal == (ROOT / contract["default_profile"]).read_text()
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-p2996-asan-promotion", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            active = [line for line in processes.splitlines() if re.fullmatch(
                r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use|vcpkg",
                Path(line.split(maxsplit=2)[-1]).name)]
            report["capacity"] = {"active": active, "load": os.getloadavg(), "cpus": os.cpu_count(),
                                  "free_bytes": shutil.disk_usage(directory).free,
                                  "total_cpu_percent": sum(float(line.split()[1]) for line in processes.splitlines())}
            report["capacity"]["admitted_editor_services"] = admit_editors(active, run, contract["editor_services"])
            assert report["capacity"]["free_bytes"] >= contract["disk_reserve_bytes"]
            assert os.getloadavg()[0] <= 2 * os.cpu_count() and report["capacity"]["total_cpu_percent"] <= 75 * os.cpu_count()
            docker = "/Applications/Docker.app/Contents/Resources/bin/docker"
            assert run("docker-context", [docker, "context", "show"], timeout=15).strip() == admission["docker_context"]
            assert run("docker-census", [docker, "ps", "--format", "{{.ID}}\t{{.Image}}"], timeout=15).splitlines() == admission["containers"]
            stats = run("docker-stats", [docker, "stats", "--no-stream", "--format", "{{json .}}"], timeout=20)
            report["capacity"]["container_cpu_percent"] = sum(float(json.loads(line)["CPUPerc"].rstrip("%")) for line in stats.splitlines())
            assert report["capacity"]["container_cpu_percent"] <= 50 * os.cpu_count()
            guard()
            source_state("source-before")
            target = Path(contract["target"])
            for name in ("cwd", "tmp", "cache"):
                (directory / name).mkdir()
            profiles = {}
            for name, extra in (("private", ""), ("mutation", ' (literal ' + json.dumps(str(target)) + ')')):
                path = directory / (name + ".sb")
                path.write_text('(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '
                                + json.dumps(str(directory)) + ') (literal "/dev/null")' + extra + ')\n(deny network*)\n')
                profiles[name] = ["/usr/bin/sandbox-exec", "-f", path]
            report["confinement"] = {name: digest(Path(argv[-1])) for name, argv in profiles.items()}
            env.clear()
            env.update(build_environment(directory, contract, "p2996"))
            for name in contract["runtime_unset"]:
                env.pop(name, None)
            assert not any(name.startswith("DYLD_") for name in env)

            def apply(label, staged, before, after):
                script = "import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from p2996_asan_runtime import replace_exact;replace_exact(Path(sys.argv[2]),Path(sys.argv[3]),json.loads(sys.argv[4]),json.loads(sys.argv[5]))"
                run(label, profiles["mutation"] + [sys.executable, "-E", "-B", "-c", script, ROOT / "dev/toolchains",
                    staged, target, json.dumps(before), json.dumps(after)], descriptor=fd)

            def qualify(current):
                nonlocal promoted
                promoted = current
                guard()
                if current:
                    prefix = Path(contract["prefixes"]["p2996"])
                    libraries = [prefix / "lib" / name for name in ("libc++.dylib", "libc++abi.dylib", "libunwind.dylib")]
                    launcher = profiles["private"] + [sys.executable, "-E", "-B", "-c",
                        "import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));"
                        "os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"]
                    for mode, settings in contract["sanitizers"].items():
                        binary = contract["witnesses"][mode]
                        report["cells"][mode] = {"binary": binary, "runs": {}}
                        for name, expected in {"clean": 0, **{name: 86 for name in settings["errors"]}}.items():
                            label = mode + "-" + name
                            output = run(label, launcher + [binary["path"], name, json.dumps(contract["runtime_environment"])],
                                         timeout=20, descriptor=fd, expected=expected)
                            assert output == "reflection value=43, members=1\n"
                            trace = (directory / (label + ".stderr")).read_text()
                            loaded = {str(Path(line[line.index('/'):]).resolve()) for line in trace.splitlines() if line.startswith("dyld[") and '/' in line}
                            assert all(str(path.resolve()) in loaded for path in libraries)
                            assert {p for p in loaded if Path(p).name.startswith("libclang_rt.")} == {str((prefix / p).resolve()) for p in settings["runtimes"]}
                            assert all(token in trace for token in settings["errors"][name]) if expected else not any(
                                token in trace for token in ("ERROR: AddressSanitizer", "runtime error:", "Sanitizer CHECK failed"))
                            report["cells"][mode]["runs"][name] = {"expected_returncode": expected, "loaded": sorted(loaded)}
                            save()
                    assert set(report["cells"]) == {"asan", "ubsan", "asan-ubsan"}
                env.clear()
                env.update(base_env)
                stage = "after" if current else "recovered"
                source_state("source-" + stage)
                assert run("default-" + stage, normal_argv) == normal
                report["writer_census_" + stage] = census()
                guard()
                if current:
                    report["installed_identity"] = asan.identity(target)

            transition(directory, target, Path(contract["replacement"]), contract["before"], contract["after"], apply, qualify, report, save)
        report["lease_released"] = True
        report["state"] = "PASS: installed ASan promotion and seven sanitizer witnesses"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            guard()
            report["protected_state_matches_expected"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
