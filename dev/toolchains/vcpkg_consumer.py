"""Build eight confined consumers of the real core and retained fmt packages."""

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
from mise_renovate import protected
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from vcpkg_fmt import build_environment

EVIDENCE = ROOT / "evidence/vcpkg-consumers"
CONTRACT_SHA = "950540f9b40fbcd04412b4997bb4b3e68cf72171daa46ac2cb00215b85402493"
CMAKE = '''cmake_minimum_required(VERSION 4.4)
project(FmtParity LANGUAGES CXX)
add_subdirectory("@ROOT@" core EXCLUDE_FROM_ALL)
find_package(fmt 12.2.0 EXACT CONFIG REQUIRED)
if(NOT fmt_DIR STREQUAL "${VCPKG_INSTALLED_DIR}/${VCPKG_TARGET_TRIPLET}/share/fmt")
  message(FATAL_ERROR "fmt must come from the selected retained installation.")
endif()
add_executable(fmt_parity main.cpp)
target_link_libraries(fmt_parity PRIVATE AggregatedResearch::core fmt::fmt)
set_target_properties(fmt_parity PROPERTIES CXX_STANDARD 26 CXX_STANDARD_REQUIRED YES
  CXX_EXTENSIONS NO CXX_SCAN_FOR_MODULES OFF)
file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/parity-$<CONFIG>.txt" CONTENT
"binary=$<TARGET_FILE:fmt_parity>\nfmt=$<TARGET_FILE:fmt::fmt>\nkind=$<TARGET_PROPERTY:fmt::fmt,TYPE>\n")
'''
CPP = '''#include <aggregated_research/core.hpp>
#include <fmt/format.h>
#include <cstdio>
int main() {
  const auto result = aggregated_research::reflection_probe();
  const auto text = fmt::format("reflection value={}, members={}\\n", result.value, result.member_count);
  std::fputs(text.c_str(), stdout);
  return result.value == 43 && result.member_count == 1 ? 0 : 1;
}
'''


def inspect(build, dependency):
    cache = dict(re.findall(r"^([^#/:\r\n][^:=\r\n]*):[^=\r\n]+=(.*)$", (build / "CMakeCache.txt").read_text(), re.MULTILINE))
    compiler_file = build / "CMakeFiles/4.4.4/CMakeCXXCompiler.cmake"
    compiler = dict(re.findall(r'^set\((CMAKE_CXX_COMPILER(?:_ID|_VERSION)?) "([^"\n]*)"\)$', compiler_file.read_text(), re.MULTILINE))
    for configuration in ("Debug", "Release"):
        assert compiler == dependency["configurations"][configuration]["compiler"]
        for name in ("CMAKE_CXX_FLAGS", "CMAKE_OSX_SYSROOT", "CMAKE_OSX_DEPLOYMENT_TARGET", "CMAKE_OSX_ARCHITECTURES", "CMAKE_MAKE_PROGRAM"):
            assert cache[name] == dependency["configurations"][configuration]["cache"][name], name
    assert cache["BUILD_SHARED_LIBS"] == "OFF"
    for name in ("VCPKG_MANIFEST_MODE", "VCPKG_MANIFEST_INSTALL", "VCPKG_APPLOCAL_DEPS",
                 "CMAKE_FIND_USE_PACKAGE_REGISTRY", "CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY"):
        assert cache[name] == "OFF", name
    commands = load(build / "compile_commands.json")
    for source in ("core.cpp", "main.cpp"):
        rows = [row for row in commands if Path(row["file"]).name == source]
        assert rows and all(("-freflection" in row["command"]) == (source == "core.cpp") for row in rows)
        assert all("-std=c++26" in row["command"] for row in rows)
    return {"cache": cache, "compiler": compiler, "compile_commands_sha256": digest(build / "compile_commands.json")}


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
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0"}
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
        assert all(digest(Path(row["path"])) == row["sha256"] for rows in data["abi_inputs"].values() for row in rows)
        assert sys.executable in data["tools"] and digest(LOCK_MODULE) == LOCK_SHA
        assert digest(Path(__file__)) == report["helper_sha256"]
        return data, protected()

    scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run", scope)

    def run(label, argv, timeout=60, descriptor=None, monitor=False):
        assert label not in [row["case"] for row in report["commands"]]
        result = native(label, argv, timeout=timeout, descriptor=descriptor, monitor=monitor)
        report["commands"][-1].update(expected_returncode=0, timeout_seconds=timeout)
        save()
        return result

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
        with lease.held(lease.HEAVY_GATE, "marketplace-vcpkg-consumers", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            active = [line for line in processes.splitlines() if re.fullmatch(
                r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use|vcpkg",
                Path(line.split(maxsplit=2)[-1]).name)]
            report["capacity"] = {"active": active, "load": os.getloadavg(), "cpus": os.cpu_count(),
                                  "free_bytes": shutil.disk_usage(directory).free,
                                  "total_cpu_percent": sum(float(line.split()[1]) for line in processes.splitlines())}
            assert not active and report["capacity"]["free_bytes"] >= contract["disk_reserve_bytes"]
            assert os.getloadavg()[0] <= 2 * os.cpu_count() and report["capacity"]["total_cpu_percent"] <= 75 * os.cpu_count()
            docker = "/Applications/Docker.app/Contents/Resources/bin/docker"
            assert run("docker-context", [docker, "context", "show"], timeout=15).strip() == admission["docker_context"]
            assert run("docker-census", [docker, "ps", "--format", "{{.ID}}\t{{.Image}}"], timeout=15).splitlines() == admission["containers"]
            stats = run("docker-stats", [docker, "stats", "--no-stream", "--format", "{{json .}}"], timeout=20)
            report["capacity"]["container_cpu_percent"] = sum(float(json.loads(line)["CPUPerc"].rstrip("%")) for line in stats.splitlines())
            assert report["capacity"]["container_cpu_percent"] <= 50 * os.cpu_count()
            guard()
            prior = load(ROOT / contract["fmt_qualification"])
            retained = Path(contract["fmt_root"])
            source_before = prefix_inventory(retained / "vcpkg")
            for triplet, dependency in prior["cells"].items():
                assert prefix_inventory(retained / triplet / "installed") == dependency["installed"]
            for name in ("cwd", "tmp", "cache", "source"):
                (directory / name).mkdir()
            (directory / "source/CMakeLists.txt").write_text(CMAKE.replace("@ROOT@", str(ROOT)))
            (directory / "source/main.cpp").write_text(CPP)
            profile = directory / "private.sb"
            profile.write_text('(version 1)\n(allow default)\n(deny file-write*)\n'
                               '(allow file-write* (subpath ' + json.dumps(str(directory)) + ') (literal "/dev/null"))\n(deny network*)\n')
            sandbox = ["/usr/bin/sandbox-exec", "-f", profile]
            report["confinement"] = {"profile_sha256": digest(profile), "allowed_inherited_fds": [0, 1, 2, fd]}
            for triplet, dependency in prior["cells"].items():
                lane = triplet.split("-")[2]
                env.clear()
                env.update(build_environment(directory, contract, lane) | {"VCPKG_ROOT": str(retained / "vcpkg")})
                build = directory / triplet
                cmake = contract["managed_tools"]["cmake"]["path"]
                options = {"CMAKE_TOOLCHAIN_FILE": contract["public_toolchain"],
                    "VCPKG_CHAINLOAD_TOOLCHAIN_FILE": str(ROOT / "cmake/toolchains/vcpkg-macos-arm64.cmake"),
                    "VCPKG_TARGET_TRIPLET": triplet, "VCPKG_INSTALLED_DIR": str(retained / triplet / "installed"),
                    "CMAKE_MAKE_PROGRAM": contract["managed_tools"]["ninja"]["path"], "CMAKE_EXPORT_COMPILE_COMMANDS": "ON",
                    "BUILD_SHARED_LIBS": "OFF", "VCPKG_MANIFEST_MODE": "OFF", "VCPKG_MANIFEST_INSTALL": "OFF",
                    "VCPKG_APPLOCAL_DEPS": "OFF", "CMAKE_FIND_USE_PACKAGE_REGISTRY": "OFF", "CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY": "OFF"}
                guard()
                run(triplet + "-configure", sandbox + [cmake, "-S", directory / "source", "-B", build, "-G", "Ninja Multi-Config"] +
                    ["-D" + key + "=" + value for key, value in options.items()], timeout=120, descriptor=fd, monitor=True)
                cell = inspect(build, dependency)
                report["cells"][triplet] = cell | {"runs": {}}
                for library in dependency["libraries"]:
                    configuration = library["configuration"]
                    label = triplet + "-" + configuration
                    selected = dict(line.split("=", 1) for line in (build / ("parity-" + configuration + ".txt")).read_text().splitlines())
                    assert selected["fmt"] == library["path"] and digest(Path(selected["fmt"])) == library["sha256"]
                    assert selected["kind"] == ("SHARED_LIBRARY" if triplet.endswith("dynamic") else "STATIC_LIBRARY")
                    run(label + "-build", sandbox + [cmake, "--build", build, "--config", configuration,
                        "--target", "fmt_parity", "--parallel", "1", "--verbose"], timeout=180, descriptor=fd, monitor=True)
                    assert run(label + "-arch", sandbox + ["/usr/bin/lipo", "-archs", selected["binary"]], descriptor=fd).strip() == "arm64"
                    output = run(label + "-run", sandbox + [sys.executable, "-B", "-c",
                        "import os,sys;os.execve(sys.argv[1],sys.argv[1:],dict(os.environ,DYLD_PRINT_LIBRARIES='1'))", selected["binary"]],
                        timeout=15, descriptor=fd)
                    assert output == "reflection value=43, members=1\n"
                    trace = (directory / (label + "-run.stderr")).read_text()
                    loaded = {str(Path(line[line.index('/'):]).resolve()) for line in trace.splitlines() if line.startswith("dyld[") and '/' in line}
                    runtimes = (["lib/libc++.dylib", "lib/libc++abi.dylib", "lib/libunwind.dylib"] if lane == "p2996" else ["lib/gcc/current/libstdc++.6.dylib"])
                    assert all(str((Path(contract["prefixes"][lane]) / name).resolve()) in loaded for name in runtimes), trace
                    fmt_loaded = {p for p in loaded if Path(p).name.startswith("libfmt")}
                    assert fmt_loaded == ({str(Path(library["path"]).resolve())} if triplet.endswith("dynamic") else set())
                    report["cells"][triplet]["runs"][configuration] = selected | {"sha256": digest(Path(selected["binary"])), "loaded": sorted(loaded)}
                    save()
        report["lease_released"] = True
        env.clear()
        env.update(base_env)
        assert run("default-after", normal_argv) == normal
        report["writer_census_after"] = census()
        report["state"] = "PASS: eight ARM64 consumers with compiler, SDK, compiled fmt and loaded-runtime parity"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            guard()
            if "source_before" in locals():
                assert prefix_inventory(retained / "vcpkg") == source_before
                for triplet, dependency in prior["cells"].items():
                    assert prefix_inventory(retained / triplet / "installed") == dependency["installed"]
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
