"""Qualify P2996 LeakSanitizer and combined UBSan reflection witnesses."""

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
import shlex

from gcc_install import ROOT, census, digest, read
from mise_runtime import function, load
from p2996_tsan_runtime import identity, protected
from p2996_sanitizers import admit_editors
from p2996_configure import LOCK_MODULE, LOCK_SHA
from vcpkg_fmt import build_environment

EVIDENCE = ROOT / "evidence/p2996-lsan"
CONTRACT_SHA = "7a354f2fadd869349a9acb04fbdf12ed527312e63eab689bc2c68461362e2c74"




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--build", action="store_true", required=True)
    directory = parser.parse_args().run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.parent != Path.home() / ".local/state/marketplace-tool-foundation":
        parser.error("use a new normalized directory directly under the private foundation root")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    report = {"state": "running", "helper_sha256": digest(Path(__file__)), "commands": [], "cells": {}}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    base_env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}
    env = dict(base_env)

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def guard():
        assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
        data = load(EVIDENCE / "contract.json")
        assert all(digest(ROOT / p) == sha for p, sha in data["inputs"].items())
        assert all(digest(Path(p)) == sha for p, sha in (data["tools"] | data["source_inputs"]).items())
        assert all(digest(EVIDENCE / "driver-probe" / name) == sha for name, sha in data["driver_probe"].items())
        assert all(digest(Path(row["path"])) == row["sha256"] for rows in data["abi_inputs"].values() for row in rows)
        runtime = data["lsan_runtime"]
        assert identity(Path(runtime["path"])) == {key: runtime[key] for key in ("sha256", "bytes", "mode")}
        assert sys.executable in data["tools"] and digest(LOCK_MODULE) == LOCK_SHA
        assert digest(Path(__file__)) == report["helper_sha256"]
        return data, protected()

    scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run", scope)

    def run(label, argv, timeout=60, descriptor=None, monitor=False, expected=0):
        assert label not in [row["case"] for row in report["commands"]]
        try:
            result = native(label, argv, timeout=timeout, descriptor=descriptor, monitor=monitor)
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
        contract, current = guard()
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
        with lease.held(lease.HEAVY_GATE, "marketplace-p2996-lsan", wait_s=0, out=io.StringIO()) as fd:
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
            for name in ("cwd", "tmp", "cache"):
                (directory / name).mkdir()
            profile = directory / "private.sb"
            profile.write_text('(version 1)\n(allow default)\n(deny file-write*)\n'
                               '(allow file-write* (subpath ' + json.dumps(str(directory)) + ') (literal "/dev/null"))\n(deny network*)\n')
            sandbox = ["/usr/bin/sandbox-exec", "-f", profile]
            report["confinement"] = {"profile_sha256": digest(profile), "allowed_inherited_fds": [0, 1, 2, fd]}
            env.clear()
            env.update(build_environment(directory, contract, "p2996"))
            for name in contract["runtime_unset"]:
                env.pop(name, None)
            assert not any(name.startswith("DYLD_") for name in env)
            prefix = Path(contract["prefixes"]["p2996"])
            cache = load(ROOT / contract["baseline_qualification"])["cells"]["p2996-core-static-fmt-static"]["cache"]
            libraries = [prefix / "lib" / name for name in ("libc++.dylib", "libc++abi.dylib", "libunwind.dylib")]
            compiler = sandbox + [contract["compilers"]["p2996"]["CXX"], *shlex.split(cache["CMAKE_CXX_FLAGS"]),
                "-isysroot", cache["CMAKE_OSX_SYSROOT"], "-mmacosx-version-min=" + cache["CMAKE_OSX_DEPLOYMENT_TARGET"],
                "-arch", "arm64", "-std=c++26", "-O1", "-g", "-fno-omit-frame-pointer", "-fno-optimize-sibling-calls",
                "-I", ROOT / "include", "-pedantic-errors", "-Wall", "-Wextra", "-Werror"]
            launcher = sandbox + [sys.executable, "-E", "-B", "-c",
                "import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));"
                "os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"]
            for mode, settings in contract["sanitizers"].items():
                cell = directory / mode
                cell.mkdir()
                obj, binary = cell / "core.o", cell / "witness"
                flags = settings["flags"]
                run(mode + "-core", compiler + flags + ["-freflection", "-c", ROOT / "src/core.cpp", "-o", obj], descriptor=fd, monitor=True)
                run(mode + "-link", compiler + flags + [ROOT / "dev/toolchains/lsan_witness.cpp", obj,
                    "-nostdlib++", *libraries, "-Wl,-rpath," + str(prefix / "lib"), "-o", binary], descriptor=fd, monitor=True)
                artifacts = {}
                for name, path in (("object", obj), ("binary", binary)):
                    assert run(mode + "-arch-" + name, sandbox + ["/usr/bin/lipo", "-archs", path], descriptor=fd).strip() == "arm64"
                    artifacts[name] = {"path": str(path), "sha256": digest(path)}
                report["cells"][mode] = {"artifacts": artifacts, "runs": {}}
                for name, expected in {"clean": 0, **{name: 86 for name in settings["errors"]}}.items():
                    label = mode + "-" + name
                    output = run(label, launcher + [binary, name, json.dumps(contract["runtime_environment"])],
                                 timeout=20, descriptor=fd, expected=expected)
                    assert output == "reflection value=43, members=1\n"
                    trace = (directory / (label + ".stderr")).read_text()
                    loaded = {str(Path(line[line.index('/'):]).resolve()) for line in trace.splitlines() if line.startswith("dyld[") and '/' in line}
                    assert all(str(path.resolve()) in loaded for path in libraries)
                    sanitizer_images = {p for p in loaded if Path(p).name.startswith("libclang_rt.")}
                    assert sanitizer_images == {str((prefix / name).resolve()) for name in settings["runtimes"]}, trace
                    if expected:
                        assert all(token in trace for token in settings["errors"][name]), trace
                    else:
                        assert not any(token in trace for token in ("ERROR: LeakSanitizer", "FATAL: LeakSanitizer", "runtime error:", "Sanitizer CHECK failed")), trace
                    report["cells"][mode]["runs"][name] = {"expected_returncode": expected, "loaded": sorted(loaded)}
                    save()
            assert set(report["cells"]) == {"lsan", "lsan-ubsan"}
            env.clear()
            env.update(base_env)
            source_state("source-after")
            assert run("default-after", normal_argv) == normal
            report["writer_census_after"] = census()
            guard()
        report["lease_released"] = True
        report["state"] = "PASS: P2996 LSan and LSan+UBSan clean/error reflection witnesses"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            guard()
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
