"""Qualify a moved IWYU copy with explicit copied builtin resources and fixed LLVM."""

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
import time

from gcc_install import ROOT, digest, read
from mise_runtime import function, load, protected
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory

EVIDENCE = ROOT / "evidence/iwyu-relocation"
CONTRACT_SHA = "5b0eb0bb0218c0394d6ac2e56c0b9a6c2709d95e9741d59da417df2887b6262e"


def header_trace(text, resources, inventory):
    """Require actual copied builtin headers; reject errors and fallback paths."""
    assert not re.search(r": (?:fatal )?error:", text)
    paths = [Path(p) for p in re.findall(r"^\.+ (.+)$", text, re.M)]
    expected = {r["path"]: r for r in inventory if r["kind"] == "file"}
    assert paths and all(p.is_absolute() and p == p.resolve() and p.is_relative_to(resources) for p in paths)
    assert {resources / "include/stddef.h", resources / "include/__stddef_size_t.h"} <= set(paths)
    rows = []
    for path in paths:
        key = str(path.relative_to(resources))
        assert key in expected and digest(path) == expected[key]["sha256"]
        rows.append({"path": str(path), "sha256": digest(path)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    foundation = Path.home() / ".local/state/marketplace-tool-foundation"
    if not directory.is_absolute() or directory != directory.resolve() or directory.parent != foundation:
        parser.error("use a new normalized directory directly under the private foundation root")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    report = {"state": "running", "helper_sha256": digest(Path(__file__)), "commands": []}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "MISE_TASK_RUN_AUTO_INSTALL": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def run(label, argv, timeout=60, descriptor=None, expected=0):
        assert label not in [row["case"] for row in report["commands"]]
        count = len(report["commands"])
        try:
            result = native(label, argv, timeout=timeout, descriptor=descriptor)
        except AssertionError:
            assert expected != 0 and len(report["commands"]) == count + 1
            assert report["commands"][-1]["case"] == label and report["commands"][-1]["returncode"] == expected
            return (directory / (label + ".stdout")).read_text()
        finally:
            if len(report["commands"]) == count + 1 and report["commands"][-1]["case"] == label:
                report["commands"][-1].update(expected_returncode=expected, timeout_seconds=timeout)
                save()
        assert expected == 0, "expected nonzero result unexpectedly passed"
        return result

    def guard():
        assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
        data = load(EVIDENCE / "contract.json")
        assert all(digest(ROOT / p) == sha for p, sha in data["inputs"].items())
        recipe = load(ROOT / "evidence/iwyu-reflection/source-recipe.json")
        assert all(digest(Path(r["path"])) == r["sha256"] for r in recipe["prerequisites"] + recipe["source_bindings"])
        current = protected()
        built = load(ROOT / "evidence/iwyu-build/operation/qualification.json")
        assert prefix_inventory(Path(built["installed"]["prefix"])) == built["installed"]["inventory"]
        bootstrap = load(ROOT / "evidence/iwyu-source/native-prerequisite.json")["bootstrap"]
        assert digest(Path(bootstrap["sdk"]["path"]) / "SDKSettings.json") == bootstrap["sdk"]["settings_sha256"]
        assert digest(Path(__file__)) == report["helper_sha256"] and digest(LOCK_MODULE) == LOCK_SHA
        return data, recipe, current

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        contract, recipe, current = guard()
        admission, review = [load(EVIDENCE / name) for name in ("admission.json", "pre-run-review.json")]
        assert admission["helper_sha256"] == review["helper_sha256"] == report["helper_sha256"]
        assert admission["contract_sha256"] == review["contract_sha256"] == CONTRACT_SHA
        assert admission["review_sha256"] == digest(EVIDENCE / "pre-run-review.json")
        assert review["result"].startswith("PASS") and not review["findings"]
        assert admission["run_directory"] == str(directory)
        report["admission_sha256"] = digest(EVIDENCE / "admission.json")
        prior_review = load(ROOT / "evidence/iwyu-reflection/artifact-review.json")
        assert prior_review["result"].startswith("PASS") and not prior_review["findings"]
        native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                          globals() | {"directory": directory, "report": report, "env": env, "save": save})
        assert run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip() == contract["base_head"]
        normal = run("default-before", normal_argv)
        assert normal == (ROOT / "evidence/mise-runtime/operation/default-after.stdout").read_text()
        base = [current["path"], "--no-hooks", "-C", directory / "cwd", "-E", "cpp-build", "exec", "--fresh-env", "--no-deps", "--"]
        assert run("named-profile", base + normal_argv[-2:]) == (ROOT / "evidence/mise-runtime/operation/cpp-build-profile.stdout").read_text()
        acquired, registered = ROOT / "evidence/iwyu-source", ROOT / "evidence/p2996-registration"
        acquisition = load(acquired / "operation/acquisition.json")
        source = Path(acquisition["source"])
        source_modes = load(acquired / "independent-review/source-before.json")
        configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
        source_state = function(Path(__file__).with_name("iwyu_build.py"), "source_state", globals() | locals())
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-iwyu-relocation", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            active = [line for line in processes.splitlines() if re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use", Path(line.split(maxsplit=2)[-1]).name)]
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
            source_state("before")
            llvm, install = [Path(recipe["bindings"][key]) for key in ("LLVM_PREFIX", "IWYU_PREFIX")]
            resources = llvm / "lib/clang/21"
            report["original_resource_inventory"] = prefix_inventory(resources)
            staging, moved = [directory / "relocation" / name for name in ("staging", "moved")]
            shutil.copytree(install, staging, symlinks=True)
            assert prefix_inventory(staging) == prefix_inventory(install)
            shutil.copytree(resources, staging / "lib/clang/21", symlinks=True)
            assert prefix_inventory(staging / "lib/clang/21") == report["original_resource_inventory"]
            report["staged_inventory"] = prefix_inventory(staging)
            staging.rename(moved)
            assert not os.path.lexists(staging) and prefix_inventory(moved) == report["staged_inventory"]
            relocated = moved / "lib/clang/21"
            binary = moved / "bin/include-what-you-use"
            assert digest(binary) == recipe["bindings"]["IWYU_BINARY_SHA256"]
            expand = lambda argv: [s.replace("<private-09c-root>", str(directory)) for s in argv]
            assert run("architecture", ["/usr/bin/lipo", "-archs", binary], descriptor=fd).strip() == "arm64"
            version = run("version", base + ["/usr/bin/env", "DYLD_PRINT_LIBRARIES=1", binary, "--version"], descriptor=fd)
            assert version == (ROOT / "evidence/iwyu-build/operation/version.stdout").read_text()
            loaded = (directory / "version.stderr").read_text()
            assert str(binary) in loaded and str(staging) not in loaded and str(install) not in loaded
            assert str(llvm / "lib/libclang-cpp") in loaded and str(llvm / "lib/libLLVM") in loaded
            assert "/usr/lib/libc++.1.dylib" in loaded and str(llvm / "lib/libc++") not in loaded
            for label, key in (("default-resource", "default_print_query"), ("explicit-resource", "override_print_query")):
                query = recipe["relocation"][key]
                assert run(label, base + expand(query["argv"]), descriptor=fd, expected=query["expected_returncode"]) == expand([query["expected_stdout"]])[0]
            fixture = directory / "fixtures/reflection"
            fixture.mkdir(parents=True)
            for name in ("value.h", "indirect.h", "main.cc"):
                path = ROOT / "evidence/iwyu-reflection/operation/fixtures/reflection" / name
                shutil.copyfile(path, fixture / path.name)
            witness = recipe["resource_witness"]
            Path(expand([witness["path"]])[0]).write_text(witness["content"])
            fixture_before = prefix_inventory(directory / "fixtures")
            argv = expand(witness["argv"])
            run("resource-witness", base + argv, descriptor=fd)
            report["header_trace"] = header_trace((directory / "resource-witness.stderr").read_text(), relocated, report["original_resource_inventory"])
            empty = directory / "empty-resource"
            empty.mkdir()
            negative = list(argv)
            negative[negative.index("-resource-dir") + 1] = str(empty)
            run("missing-resource", base + negative, descriptor=fd, expected=1)
            assert "fatal error: 'stddef.h' file not found" in (directory / "missing-resource.stderr").read_text()
            analyze = expand(recipe["reflection_fixture"]["analyze_argv"])
            analyze[0], analyze[analyze.index("-resource-dir") + 1] = str(binary), str(relocated)
            run("reflection", base + analyze, descriptor=fd)
            assert (directory / "reflection.stderr").read_text().strip() == "(" + str(fixture / "main.cc") + " has correct #includes/fwd-decls)"
            assert not os.path.lexists(staging) and prefix_inventory(moved) == report["staged_inventory"]
            assert prefix_inventory(directory / "fixtures") == fixture_before
            report.update(moved_prefix=str(moved), final_fixture=fixture_before, moved_inventory=prefix_inventory(moved))
        report["lease_released"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: moved IWYU copy and explicit copied resources; original LLVM remains fixed"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            guard()
            if "source_state" in locals():
                source_state("after")
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
