"""Run the admitted two-compiler native core qualification in fresh private trees."""

import argparse
import ast
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import time

from core_commands import CoreCommands, CONFIGS, STRICT, numbered_commands
from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from vcpkg_register import install_entries


def function(path, name, sha, scope):
    assert digest(path) == sha
    node = next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
    return scope[name]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    load = lambda p: json.loads(p.read_text())
    evidence, installed, registered = (ROOT / ("evidence/" + n) for n in ("core-p2996", "p2996-install", "p2996-registration"))
    inventory = load(installed / "independent-installation/post-install-inventory.json")
    baseline = load(registered / "independent-registration/post-state.json")
    configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
    prefix, workspace, source = map(Path, (inventory["prefix"], inventory["workspace"], configuration["source"]))
    forbidden = (ROOT, workspace, source, Path.home() / ".config", Path.home() / ".local/share/mise")
    if (not directory.is_absolute() or directory != directory.resolve() or "%" in str(directory)
            or any(directory.is_relative_to(p) for p in forbidden)):
        parser.error("use a new normalized private directory outside protected project, source, build and mise roots")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    report = {"state": "running", "commands": [], "helper_sha256": digest(Path(__file__)), "trees": {}, "cells": {}, "controls": []}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                      "7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f", scope)
    runtime = load(ROOT / "evidence/p2996-reflection/operation/qualification.json")
    protected = function(Path(__file__).with_name("p2996_reflection.py"), "protected", runtime["helper_sha256"],
                         globals() | {"baseline": baseline, "inventory": inventory, "prefix": prefix, "evidence": installed, "load": load})

    def run(label, argv, descriptor=None, expected=0):
        try:
            result = native(label, argv, timeout=60, descriptor=descriptor)
        except AssertionError:
            assert expected != 0 and report["commands"][-1]["case"] == label
            assert report["commands"][-1]["returncode"] == expected
            return (directory / (label + ".stdout")).read_text()
        assert expected == 0, "negative control unexpectedly passed"
        return result

    def record(path, allow_empty=False):
        assert path.is_file() and (allow_empty or path.stat().st_size > 0)
        return {"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        admission = load(evidence / "admission.json")
        assert admission["helper_sha256"] == report["helper_sha256"] and admission["run_directory"] == str(directory)
        pre_review = load(evidence / "pre-run-review.json")
        assert digest(evidence / "pre-run-review.json") == admission["pre_run_review_sha256"]
        assert pre_review["result"].startswith("PASS") and not pre_review["findings"] and pre_review["helper_sha256"] == report["helper_sha256"]
        proposal = load(evidence / "proposal.json")
        assert digest(evidence / "proposal.json") == pre_review["proposal_sha256"]
        assert all(admission[k] == proposal[k] for k in ("base_head", "helper_sha256", "inputs", "tool_hashes"))
        assert all(digest(ROOT / path) == sha for path, sha in admission["inputs"].items())
        assert run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip() == admission["base_head"]
        report.update(admission_sha256=digest(evidence / "admission.json"), inputs=admission["inputs"])
        contract_path = ROOT / "evidence/core-command-preparation/harness-contract.json"
        assert digest(contract_path) == "feb0f9700b7ed6828334fb39c6e6d631c87b9be74f4fb9334cdd063b92ecfec8"
        contract = load(contract_path)
        assert digest(Path(__file__).with_name("core_commands.py")) == "9c1cdf78f5102a1256a71e965fd3bf9f2b2461f1d6e509fb723301e4b92565d6"
        assert digest(ROOT / "include/aggregated_research/core.hpp") == contract["shared_identity"]["exports"]["public_header_sha256"]
        original = load(ROOT / "evidence/onboarding/baseline-files.json")["files"]
        assert len(original) == 19 and all(admission["inputs"][r["path"]] == r["sha256"] for r in original)
        assert all(digest(Path(r["path"])) == r["sha256"] for r in contract["prerequisite_references"])
        assert all(digest(Path(r["path"])) == r["patched_sha256"] for r in contract["source_input_contract"])
        for path, sha in (("core-command-preparation/command-review.json", "2d6e63dc37ba271ff4174f14731ac5f9208104e3c7a20f3be8454a7166ee8e00"),
                          ("core-p2996-preparation/preparation-review.json", "831a2a6e93d3e45b7a9b520483dd37ffc9970f04ff5f2364b1721cc8fee95f73")):
            p = ROOT / "evidence" / path
            assert digest(p) == sha and load(p)["result"].startswith("PASS") and not load(p)["findings"]
        registration_review = load(registered / "registration-review.json")
        assert digest(registered / "registration-review.json") == "9b8e92ac14d9304d7055fa00a3348612251e8bd27247db0ead946179bc835437"
        assert digest(registered / "independent-registration/post-state.json") == registration_review["post_state"]["sha256"]
        assert digest(installed / "independent-installation/post-install-inventory.json") == registration_review["retained_source_build_inventory"]["inventory_sha256"]
        assert digest(installed / "operation/prefix-inventory.json") == registration_review["prefix_inventory"]["inventory_sha256"]
        gcc = load(ROOT / "evidence/gcc-runtime/qualification.json")
        assert all(digest(Path(r["path"])) == r["sha256"] for r in gcc["identities"].values())
        assert digest(Path(configuration["sdk"]["path"]) / "SDKSettings.json") == configuration["sdk"]["settings_sha256"]
        protected()

        def source_state(stage):
            for name, arguments in (("head", ["rev-parse", "HEAD"]), ("tree", ["rev-parse", "HEAD^{tree}"]),
                                    ("status", ["status", "--porcelain", "--untracked-files=all"]), ("diff", ["diff", "--no-ext-diff", "--binary"])):
                run(stage + "-" + name, ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source, *arguments])
                assert (directory / (stage + "-" + name + ".stdout")).read_bytes() == (registered / ("operation/source-after-" + name + ".stdout")).read_bytes()

        source_state("source-before")
        normal = run("default-before", normal_argv)
        assert normal == (registered / "operation/default-after.stdout").read_text()
        tools = load(ROOT / "evidence/tool-foundation/host-qualification.json")["binaries"]
        cmake, ninja = (tools[n]["resolved_path"] for n in ("cmake", "ninja"))
        ctest, mise, sdk = str(Path(cmake).with_name("ctest")), configuration["mise"]["path"], configuration["sdk"]["path"]
        assert digest(Path(mise)) == configuration["mise"]["sha256"]
        export_tools = load(evidence / "export-tool-prerequisite.json")
        assert digest(evidence / "export-tool-prerequisite.json") == "4ddad861aefcded3253434211167379b99fcfb277d0d1ca43395dc46bdeee7d4"
        for tool in export_tools["tools"].values():
            assert digest(Path(tool["path"])) == tool["sha256"] and str(Path(tool["path"]).resolve()) == tool["resolved"]
        nm, filt = (export_tools["tools"][n]["path"] for n in ("nm", "cxxfilt"))
        assert all(p in admission["tool_hashes"] for p in (mise, "/usr/bin/git", "/bin/ps", "/usr/bin/file", "/usr/bin/lipo", "/usr/bin/otool", "/usr/bin/env", "/bin/sh"))
        assert all(digest(Path(path)) == sha for path, sha in admission["tool_hashes"].items())
        assert all(admission["tool_hashes"][tools[n]["resolved_path"]] == tools[n]["sha256"] for n in ("cmake", "ninja"))
        assert digest(LOCK_MODULE) == LOCK_SHA
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-core-matrix", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            assert not any(re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy",
                                       Path(line.split(maxsplit=2)[-1]).name) for line in processes.splitlines())
            assert shutil.disk_usage(directory).free >= 8 * 1024**3
            symbol = "__ZN19aggregated_research16reflection_probeEv"
            assert run("demangle-public-symbol", [filt, "--strip-underscore", symbol], fd) == "aggregated_research::reflection_probe()\n"
            candidates = {row["path"]: row for row in load(ROOT / "evidence/core-p2996-preparation/source-contract.json")["candidates"]}
            for lane in ("p2996", "gcc16"):
                lane_spec = contract["lane_specs"][lane]
                env.pop("MARKETPLACE_P2996_PREFIX", None)
                env.pop("MARKETPLACE_GCC16_PREFIX", None)
                env["MARKETPLACE_" + lane.upper() + "_PREFIX"] = lane_spec["prefix"]
                base = [mise, "--no-hooks", "-C", directory / "cwd", "-E", lane, "exec", "--fresh-env", "--no-deps", "--"]
                # Both named profiles share the later qualified foundation PATH.
                expected_profile = (runtime if lane == "p2996" else gcc)["selected_environment"] | {
                    "path_sha256": runtime["selected_environment"]["path_sha256"]}
                assert json.loads(run(lane + "-profile", base + normal_argv[-2:], fd)) == expected_profile
                for shared in (False, True):
                    tree = lane + ("-shared" if shared else "-static")
                    build = directory / tree
                    ar, ranlib = "/usr/bin/ar", str(prefix / "bin/llvm-ranlib") if lane == "p2996" else "/usr/bin/ranlib"
                    assert all(p in admission["tool_hashes"] for p in (cmake, ninja, ctest, ar, ranlib, nm, filt))
                    v = CoreCommands(ROOT, build, lane, lane_spec["prefix"], sdk, cmake, ar, ranlib, shared)
                    options = ["-G", "Ninja Multi-Config", "-DCMAKE_MAKE_PROGRAM=" + ninja,
                               "-DCMAKE_TOOLCHAIN_FILE=" + lane_spec["toolchain"], "-DCMAKE_TRY_COMPILE_CONFIGURATION=Debug",
                               "-DBUILD_SHARED_LIBS=" + ("ON" if shared else "OFF"), *lane_spec.get("configure_extra", [])]
                    run(tree + "-configure", base + [cmake, "--debug-trycompile", "-S", ROOT, "-B", build, *options], fd)
                    children = list((build / "CMakeFiles/CMakeScratch").glob("TryCompile-*"))
                    assert len(children) == 1 and "CMakeCXXCompilerABI.cpp" in (children[0] / "CMakeLists.txt").read_text()
                    child = children[0]
                    lines = run(tree + "-abi-commands", base + [ninja, "-C", child, "-f", "build-Debug.ninja", "-t", "commands"], fd).splitlines()
                    probe_commands = [shlex.split(line) for line in lines]
                    assert len(probe_commands) == 2 and sum("-c" in a for a in probe_commands) == 1
                    log = (build / "CMakeFiles/CMakeConfigureLog.yaml").read_text().split('kind: "try_compile-v1"')
                    assert len(log) == 2
                    event = log[1].split("\n  -\n", 1)[0]
                    assert f'binary: "{child}"' in event and 'variable: "CMAKE_CXX_ABI_COMPILED"' in event
                    assert "cached: false" in event and "exitCode: 0" in event
                    native_lines = [line.strip().split("] ", 1)[1] for line in event.splitlines() if re.match(r"^\s+\[[12]/2\] ", line)]
                    assert native_lines == [line.replace("\\", "\\\\") for line in lines]
                    artifacts = {}
                    for args in probe_commands:
                        args = v.flags(args, linking="-c" not in args)
                        assert args.count("-o") == 1
                        path = (child / args[args.index("-o") + 1]).resolve()
                        assert path.is_relative_to(child)
                        kind = "object" if "-c" in args else "executable"
                        copy = directory / "probe-artifacts" / tree / (kind + ".bin")
                        copy.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(path, copy)
                        artifacts[kind] = record(copy) | {"source": str(path)}
                    abi = build / "CMakeFiles/4.4.4/CMakeDetermineCompilerABI_CXX.bin"
                    assert digest(abi) == artifacts["executable"]["sha256"]
                    artifacts["abi-copy"] = record(abi)
                    compiler = (build / "CMakeFiles/4.4.4/CMakeCXXCompiler.cmake").read_text()
                    assert all(text in compiler for text in ('set(CMAKE_CXX_COMPILER_WORKS TRUE)', 'set(CMAKE_CXX_ABI_COMPILED TRUE)',
                                                                           f'set(CMAKE_AR "{ar}")', f'set(CMAKE_RANLIB "{ranlib}")'))
                    captures = []
                    for path in sorted(build.rglob("*")):
                        if path.is_file() and path.suffix in (".txt", ".cmake", ".ninja", ".json", ".yaml", ".cpp", ".log"):
                            path.read_text()
                            copy = directory / "configured-evidence" / tree / path.relative_to(build)
                            copy.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copyfile(path, copy)
                            captures.append(record(copy, allow_empty=True))
                    rows = load(build / "compile_commands.json")
                    outputs = v.compile_database(rows)
                    report["trees"][tree] = {"probe": artifacts, "probe_commands": probe_commands, "probe_actual_matches_generated": True,
                                             "configured_evidence": captures, "compile_database": rows, "outputs": outputs}
                    for config in CONFIGS:
                        cell = tree + "-" + config
                        generated = [shlex.split(line) for line in run(cell + "-generated", base + [ninja, "-C", build, "-f", "build-" + config + ".ninja", "-t", "commands"], fd).splitlines()]
                        v.actions(generated, config)
                        actual = numbered_commands(run(cell + "-build", base + [cmake, "--build", build, "--config", config, "--parallel", "1", "--verbose"], fd))
                        v.actual_matches(generated, actual)
                        test = run(cell + "-test", base + [ctest, "--test-dir", build, "-C", config, "--output-on-failure", "--no-tests=error"], fd)
                        assert "100% tests passed" in test and "out of 1" in test
                        binary, library = build / config / "research_core_smoke", build / config / ("libresearch_core.dylib" if shared else "libresearch_core.a")
                        summary = dict(line.split("=", 1) for line in (build / ("core-" + config + ".txt")).read_text().splitlines())
                        assert summary == {"library": str(library), "binary": str(binary), "configuration": config, "shared": "ON" if shared else "OFF"}
                        assert "Mach-O 64-bit executable arm64" in run(cell + "-architecture", ["/usr/bin/file", "-b", binary], fd)
                        assert run(cell + "-library-architecture", ["/usr/bin/lipo", "-archs", library], fd).strip() == "arm64"
                        symbols = run(cell + "-exports", [nm, "-g", "-U", "-m", "--no-demangle", library], fd)
                        assert any(line.split()[-1:] == [symbol] and "(__TEXT,__text)" in line and " external " in line
                                   and "private external" not in line for line in symbols.splitlines())
                        for name, artifact in [("binary", binary)] + ([("core", library)] if shared else []):
                            deps = run(cell + "-" + name + "-libraries", ["/usr/bin/otool", "-L", artifact], fd)
                            paths = run(cell + "-" + name + "-rpaths", ["/usr/bin/otool", "-l", artifact], fd)
                            if lane == "p2996":
                                assert all(n in deps for n in ("libc++.", "libc++abi.", "libunwind.")) and "libstdc++" not in deps and "/usr/lib/libc++" not in deps
                                assert "path " + str(prefix / "lib") + " (offset " in paths
                            else:
                                selected = [line.strip().split(" (", 1)[0] for line in deps.splitlines()[1:] if "libstdc++" in line]
                                assert len(selected) == 1 and Path(selected[0]).resolve() == Path(lane_spec["runtime_identities"]["libstdcxx"]["path"]).resolve()
                                assert "libc++" not in deps
                            if name == "binary":
                                assert ("@rpath/libresearch_core.dylib" in deps) == shared
                                if shared:
                                    assert "path " + str(build / config) + " (offset " in paths
                        if shared:
                            assert run(cell + "-install-name", ["/usr/bin/otool", "-D", library], fd).splitlines()[1:] == ["@rpath/libresearch_core.dylib"]
                            bindings = run(cell + "-consumer-symbol", [nm, "-g", "-u", "-m", "--no-demangle", binary], fd)
                            assert any(symbol in line and re.search(r"\(from libresearch_core(?:\.dylib)?\)$", line) for line in bindings.splitlines())
                        assert run(cell + "-runtime", base + ["/usr/bin/env", "DYLD_PRINT_LIBRARIES=1", binary], fd) == "reflection value=43, members=1\n"
                        diagnostic = (directory / (cell + "-runtime.stderr")).read_text().splitlines()
                        assert diagnostic and all(line.startswith("dyld[") for line in diagnostic)
                        loaded = {Path(re.search(r" (/.*)$", line)[1]).resolve() for line in diagnostic}
                        required = {p.resolve() for p in v.libraries} if lane == "p2996" else {Path(r["path"]).resolve() for r in lane_spec["runtime_identities"].values()}
                        os_images = {Path(p) for p in contract["lane_specs"]["gcc16"]["allowed_recorded_os_cxx_images"]}
                        assert required <= loaded
                        assert {p for p in loaded if p.name.startswith(("libc++", "libunwind", "libstdc++", "libgcc"))} <= required | os_images
                        assert {p for p in loaded if p.name == "libresearch_core.dylib"} == ({library.resolve()} if shared else set())
                        report["cells"][cell] = {"summary": summary, "binary": record(binary), "library": record(library),
                            "objects": [record(build / v.object(config, n)) for n in ("core", "smoke")], "loaded_images": sorted(map(str, loaded)), "commands": actual}
                        save()
                controls = [("src/core.cpp", "original_content", True), ("src/core.cpp", "content", False),
                            ("src/smoke.cpp", "original_content", True), ("src/smoke.cpp", "content", True)]
                for i, (path, key, reflection) in enumerate(controls):
                    if lane == "gcc16" and i != 3:
                        continue
                    control = contract["private_controls"][i]
                    label = lane + "-" + control["case"]
                    cpp, obj = directory / (label + ".cpp"), directory / (label + ".o")
                    cpp.write_text(candidates[path][key])
                    assert digest(cpp) == candidates[path]["original_sha256" if key == "original_content" else "candidate_sha256"]
                    args = lane_spec["common_compile_tokens" if lane == "p2996" else "compile_common"]
                    expected = control["expected_native_returncode"]
                    run(label, base + [lane_spec["cxx"], *args, *STRICT, "-I" + str(ROOT / "include"), *( ["-freflection"] if reflection else []), "-c", cpp, "-o", obj], fd, expected)
                    assert obj.exists() == (expected == 0)
                    if expected:
                        assert control["expected_diagnostic"] in (directory / (label + ".stderr")).read_text()
                    report["controls"].append({"case": label, "returncode": expected, "source": record(cpp), "object": record(obj) if not expected else None})
            child_command = ["/bin/sh", "-c", "printf 'reflection value=43, members=1\\n'; exit 1"]
            assert run("ctest-control-child", child_command, fd, 1) == "reflection value=43, members=1\n"
            for control in contract["private_controls"][4:]:
                label = control["case"]
                child = directory / label
                child.mkdir()
                definition = child / "CTestTestfile.cmake"
                definition.write_text(control["private_CTestTestfile_contents"])
                run(label, base + [ctest, "--test-dir", child, "--output-on-failure", "--no-tests=error"], fd, control["expected_ctest_returncode"])
                report["controls"].append({"case": label, "returncode": control["expected_ctest_returncode"], "definition": record(definition), "last_test": record(child / "Testing/Temporary/LastTest.log")})
            assert len(report["cells"]) == 16 and len(report["trees"]) == 4 and len(report["controls"]) == 7
        report["lease_released"] = True
        env.pop("MARKETPLACE_GCC16_PREFIX", None)
        env.pop("MARKETPLACE_P2996_PREFIX", None)
        assert run("default-after", normal_argv) == normal
        source_state("source-after")
        assert all(digest(ROOT / path) == sha for path, sha in admission["inputs"].items())
        assert all(digest(Path(path)) == sha for path, sha in admission["tool_hashes"].items())
        assert all(digest(Path(r["path"])) == r["sha256"] for r in gcc["identities"].values())
        report["state"] = "PASS: native core, two compilers, static/shared, sixteen cells and seven controls"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            if "admission" in locals():
                assert all(digest(ROOT / path) == sha for path, sha in admission["inputs"].items())
                assert all(digest(Path(path)) == sha for path, sha in admission["tool_hashes"].items())
            if "gcc" in locals():
                assert all(digest(Path(r["path"])) == r["sha256"] for r in gcc["identities"].values())
            assert digest(Path(configuration["sdk"]["path"]) / "SDKSettings.json") == configuration["sdk"]["settings_sha256"]
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}))


if __name__ == "__main__":
    main()
