"""Prepare or run one private matching-fork IWYU build and installation."""

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

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from vcpkg_register import install_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    directory = args.run_dir
    load = lambda p: json.loads(p.read_text())
    evidence = ROOT / "evidence/iwyu-build"
    acquired = ROOT / "evidence/iwyu-source"
    installed = ROOT / "evidence/p2996-install"
    registered = ROOT / "evidence/p2996-registration"
    acquisition = load(acquired / "operation/acquisition.json")
    source_modes = load(acquired / "independent-review/source-before.json")
    bootstrap = load(acquired / "native-prerequisite.json")["bootstrap"]
    inventory = load(installed / "independent-installation/post-install-inventory.json")
    baseline = load(registered / "independent-registration/post-state.json")
    configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
    prefix, workspace, source = map(Path, (inventory["prefix"], inventory["workspace"], acquisition["source"]))
    forbidden = (ROOT, workspace, source, Path(configuration["source"]), Path.home() / ".config", Path.home() / ".local/share/mise")
    if not directory.is_absolute() or directory != directory.resolve() or any(directory.is_relative_to(p) for p in forbidden):
        parser.error("use a new normalized private directory outside protected project, source, build and mise roots")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    report = {"state": "running", "execute": args.execute, "commands": [], "helper_sha256": digest(Path(__file__))}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def function(path, name, sha, scope):
        assert digest(path) == sha
        node = next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
        return scope[name]

    run = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                   "7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f",
                   globals() | {"directory": directory, "report": report, "env": env, "save": save})
    protected = function(Path(__file__).with_name("p2996_reflection.py"), "protected",
                         "c917deccc2bde9c71cc81a20a56200187f8da18fd610cedbbbf9712274a072de",
                         globals() | {"baseline": baseline, "inventory": inventory, "prefix": prefix,
                                      "evidence": installed, "load": load})

    def source_state(stage):
        for label, root, expected in (("iwyu", source, acquired / "operation"),
                                      ("llvm", Path(configuration["source"]), registered / "operation")):
            for key, flags in (("head", ["rev-parse", "HEAD"]), ("tree", ["rev-parse", "HEAD^{tree}"]),
                               ("status", ["status", "--porcelain", "--untracked-files=all"]), ("diff", ["diff", "--no-ext-diff", "--binary"])):
                text = run(stage + "-" + label + "-" + key, ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", root, *flags])
                if label == "iwyu" and key == "diff":
                    assert text == ""
                else:
                    name = (key if label == "iwyu" else "source-after-" + key) + ".stdout"
                    assert text == (expected / name).read_text()
        for row in acquisition["verified_files"]:
            path = source / row["path"]
            assert not path.is_symlink() and digest(path) == row["sha256"] and path.stat().st_size == row["bytes"]
            assert oct(path.stat().st_mode & 0o777) == source_modes[row["path"]]["mode"]

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        assert digest(acquired / "preparation-review.json") == "32ddeafc3a80b0aabe2d5c7627ee96c2ed247d4de836bb80cabccde5a4d9acd0"
        assert load(acquired / "preparation-review.json")["result"].startswith("PASS")
        assert not load(acquired / "preparation-review.json")["findings"]
        assert acquisition["state"].startswith("PASS") and len(acquisition["verified_files"]) == 854
        assert all(row["returncode"] == 0 for row in acquisition["commands"])
        protected()
        source_state("before")
        normal = run("default-before", normal_argv)
        assert normal == (registered / "operation/default-after.stdout").read_text()
        mise = configuration["mise"]["path"]
        assert digest(Path(mise)) == configuration["mise"]["sha256"]
        tools = bootstrap["tools"]
        cmake = tools["cmake"]["resolved_path"]
        cc, cxx, ninja = (tools[n]["path"] for n in ("cc", "cxx", "ninja"))
        sdk = bootstrap["sdk"]["path"]
        assert digest(Path(sdk) / "SDKSettings.json") == bootstrap["sdk"]["settings_sha256"]
        base = [mise, "--no-hooks", "-C", directory / "cwd", "-E", "cpp-build", "exec", "--fresh-env", "--no-deps", "--"]
        selected = json.loads(run("named-profile", base + normal_argv[-2:]))
        assert selected["selected"]["MARKETPLACE_CPP_LANE"] == "tools-only"
        assert all(selected["selected"].get(k) in (None, "") for k in ("CC", "CXX", "CFLAGS", "CXXFLAGS", "LDFLAGS", "CPATH", "SDKROOT"))
        paths = [str(p.relative_to(ROOT)) for p in Path(__file__).parent.glob("*.py")]
        paths += ["dev/toolchains/iwyu-bootstrap.cmake", "evidence/iwyu-source/operation/acquisition.json",
                  "evidence/iwyu-source/independent-review/source-before.json",
                  "evidence/iwyu-source/preparation-review.json", "evidence/iwyu-source/native-prerequisite.json",
                  "evidence/p2996-registration/registration-review.json", "evidence/p2996-registration/independent-registration/post-state.json",
                  "evidence/p2996-install/independent-installation/post-install-inventory.json", "evidence/p2996-install/operation/prefix-inventory.json"]
        paths += [r["path"] for r in load(ROOT / "evidence/onboarding/baseline-files.json")["files"]]
        hashes = {p: digest(ROOT / p) for p in sorted(paths)}
        docker = "/Applications/Docker.app/Contents/Resources/bin/docker"
        tool_hashes = {p: digest(Path(p)) for p in (mise, cmake, cc, cxx, ninja, "/usr/bin/git", "/usr/bin/env", "/bin/ps", "/usr/bin/lipo", "/usr/bin/otool", docker)}
        assert all(tool_hashes[t.get("path", t.get("resolved_path"))] == t["sha256"] for t in tools.values())
        proposal = {"helper_sha256": report["helper_sha256"], "inputs": hashes, "tools": tool_hashes, "source": str(source),
                    "llvm_prefix": str(prefix), "sdk": bootstrap["sdk"], "selected_environment": selected,
                    "base_head": run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip(),
                    "timeouts": {"configure": 180, "build": 1800, "install": 120}, "jobs": 1, "disk_reserve_bytes": 8 * 1024**3}
        report["proposal"] = proposal
        if args.execute:
            admission = load(evidence / "admission.json")
            review = load(evidence / "pre-run-review.json")
            assert admission["helper_sha256"] == report["helper_sha256"] and admission["run_directory"] == str(directory)
            assert admission["review_sha256"] == digest(evidence / "pre-run-review.json") and review["result"].startswith("PASS") and not review["findings"]
            assert review["proposal_sha256"] == digest(evidence / "proposal.json") and load(evidence / "proposal.json") == proposal
            report["admission_sha256"] = digest(evidence / "admission.json")
            assert digest(LOCK_MODULE) == LOCK_SHA
            spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
            lease = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lease)
            assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
            assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
            with lease.held(lease.HEAVY_GATE, "marketplace-iwyu-build", wait_s=0, out=io.StringIO()) as fd:
                assert fd is not None
                processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
                active = [line for line in processes.splitlines() if re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy", Path(line.split(maxsplit=2)[-1]).name)]
                report["capacity"] = {"active": active, "load": os.getloadavg(), "cpus": os.cpu_count(), "free_bytes": shutil.disk_usage(directory).free,
                                      "total_cpu_percent": sum(float(line.split()[1]) for line in processes.splitlines())}
                assert not active and report["capacity"]["free_bytes"] >= proposal["disk_reserve_bytes"]
                assert os.getloadavg()[0] <= 2 * os.cpu_count() and report["capacity"]["total_cpu_percent"] <= 75 * os.cpu_count()
                assert run("docker-context", [docker, "context", "show"], timeout=15).strip() == admission["docker_context"]
                containers = run("docker-census", [docker, "ps", "--format", "{{.ID}}\t{{.Image}}"], timeout=15).splitlines()
                assert containers == admission["containers"]
                stats = run("docker-stats", [docker, "stats", "--no-stream", "--format", "{{json .}}"], timeout=20)
                report["capacity"]["container_cpu_percent"] = sum(float(json.loads(line)["CPUPerc"].rstrip("%")) for line in stats.splitlines())
                assert report["capacity"]["container_cpu_percent"] <= 50 * os.cpu_count()
                protected()
                source_state("immediate")
                assert all(digest(ROOT / p) == sha for p, sha in hashes.items())
                build, install = directory / "build", directory / "prefix"
                values = dict(CC=cc, CXX=cxx, SDK=sdk, NINJA=ninja, LLVM_PREFIX=str(prefix), PREFIX=str(install))
                command = base + ["/usr/bin/env", "MAKEFLAGS=-j1", "CMAKE_BUILD_PARALLEL_LEVEL=1",
                                  *["MARKETPLACE_IWYU_" + key + "=" + value for key, value in values.items()]]
                run("configure", command + [cmake, "-S", source, "-B", build, "-G", "Ninja", "-C", ROOT / "dev/toolchains/iwyu-bootstrap.cmake",
                                             "-DGIT_EXECUTABLE=/usr/bin/git"], timeout=180, descriptor=fd, monitor=True)
                database = load(build / "compile_commands.json")
                assert len(database) == 15 and len({r["file"] for r in database}) == 15
                for row in database:
                    argv = shlex.split(row["command"])
                    assert argv[0] == cxx and Path(row["directory"]) == build and Path(row["file"]).parent == source
                    assert all(flag in argv for flag in ("-std=c++17", "-fno-exceptions", "-fno-rtti", "-UNDEBUG", "-I" + str(prefix / "include")))
                    assert argv[argv.index("-isysroot") + 1] == sdk and argv[argv.index("-arch") + 1] == "arm64"
                    assert not any("-freflection" in flag or "include/c++/v1" in flag or flag.startswith("-stdlib=") for flag in argv)
                planned = run("build-commands", base + [ninja, "-C", build, "-t", "commands", "include-what-you-use"], descriptor=fd).splitlines()
                assert len(planned) == 16
                for line, row in zip(planned[:-1], database):
                    argv = shlex.split(line)
                    obj = str(Path(row["output"]).relative_to(build))
                    position = argv.index("-MT") - 1
                    assert argv[position:position + 5] == ["-MD", "-MT", obj, "-MF", obj + ".d"]
                    del argv[position:position + 5]
                    assert argv == shlex.split(row["command"])
                assert str(prefix / "lib/libclang-cpp") in planned[-1] and str(prefix / "lib/libLLVM") in planned[-1]
                run("build", base + [cmake, "--build", build, "--target", "include-what-you-use", "--parallel", "1", "--verbose"], timeout=1800, descriptor=fd, monitor=True)
                actual = [re.sub(r"^\[\d+/\d+\] ", "", line) for line in (directory / "build.stdout").read_text().splitlines() if re.match(r"^\[\d+/\d+\] ", line)]
                assert actual == planned
                run("install", base + [cmake, "--install", build], timeout=120, descriptor=fd, monitor=True)
                manifest = (build / "install_manifest.txt").read_text().splitlines()
                assert manifest and all(Path(p).is_relative_to(install) and Path(p).is_file() for p in manifest)
                notices = install / "share/licenses/include-what-you-use"
                notices.mkdir(parents=True)
                for name in ("LICENSE.TXT", "iwyu_getopt.cc", "iwyu_getopt.h"):
                    shutil.copyfile(source / name, notices / name)
                binary = install / "bin/include-what-you-use"
                assert run("architecture", ["/usr/bin/lipo", "-archs", binary], descriptor=fd).strip() == "arm64"
                run("libraries", ["/usr/bin/otool", "-L", binary], descriptor=fd)
                run("rpaths", ["/usr/bin/otool", "-l", binary], descriptor=fd)
                version = run("version", base + ["/usr/bin/env", "DYLD_PRINT_LIBRARIES=1", binary, "--version"], descriptor=fd)
                assert "791e69e" in version and "clang version 21.0.0" in version
                loaded = (directory / "version.stderr").read_text()
                assert str(prefix / "lib/libclang-cpp") in loaded and str(prefix / "lib/libLLVM") in loaded
                assert "/usr/lib/libc++.1.dylib" in loaded and str(prefix / "lib/libc++") not in loaded
                report["installed"] = {"prefix": str(install), "binary_sha256": digest(binary), "manifest": manifest,
                                       "inventory": prefix_inventory(install), "version": version}
            report["lease_released"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: private IWYU build and installation; semantic qualification pending" if args.execute else "PASS: preparation only"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            source_state("after")
            if "hashes" in locals():
                assert all(digest(ROOT / p) == sha for p, sha in hashes.items())
                assert all(digest(Path(p)) == sha for p, sha in tool_hashes.items())
            assert digest(Path(bootstrap["sdk"]["path"]) / "SDKSettings.json") == bootstrap["sdk"]["settings_sha256"]
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
