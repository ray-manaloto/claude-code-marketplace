"""Qualify LLVM source-based coverage with reflection and exact branch controls."""

import argparse
import ast
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import math
import shutil
import signal
import subprocess
import time

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import isolated, snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from vcpkg_register import install_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    load = lambda p: json.loads(p.read_text())
    evidence = ROOT / "evidence/p2996-coverage"
    registered = ROOT / "evidence/p2996-registration"
    installed = ROOT / "evidence/p2996-install"
    reflected = ROOT / "evidence/p2996-reflection"
    review = load(registered / "registration-review.json")
    registration = load(registered / "operation/qualification.json")
    runtime = load(reflected / "operation/qualification.json")
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
    witness = Path(__file__).with_name("p2996_reflection.cpp")
    report = {"state": "running", "commands": [], "helper_sha256": digest(Path(__file__)),
              "witness_sha256": digest(witness), "registration_review_sha256": digest(registered / "registration-review.json")}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def function(path, name, sha, scope):
        assert digest(path) == sha
        node = next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
        return scope[name]

    run_scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                      "7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f", run_scope)
    protected = function(Path(__file__).with_name("p2996_reflection.py"), "protected", runtime["helper_sha256"],
                         globals() | {"baseline": baseline, "inventory": inventory, "prefix": prefix,
                                      "evidence": installed, "load": load})

    def run(label, argv, timeout=45, descriptor=None, environment=None, expected=0):
        run_scope["env"] = env if environment is None else environment
        try:
            result = native(label, argv, timeout=timeout, descriptor=descriptor)
        except AssertionError:
            assert expected != 0 and report["commands"][-1]["case"] == label
            assert report["commands"][-1]["returncode"] == expected
            return (directory / (label + ".stdout")).read_text()
        assert expected == 0, "negative control unexpectedly passed"
        return result

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        admission = load(evidence / "admission.json")
        assert admission["helper_sha256"] == report["helper_sha256"] and admission["witness_sha256"] == report["witness_sha256"]
        assert admission["run_directory"] == str(directory) and admission["registration_review_sha256"] == report["registration_review_sha256"]
        assert report["registration_review_sha256"] == "9b8e92ac14d9304d7055fa00a3348612251e8bd27247db0ead946179bc835437"
        assert review["result"].startswith("PASS") and not review["findings"] and review["all_protected_state_unchanged"]
        assert digest(registered / "operation/qualification.json") == review["operation_sha256"]
        assert registration["state"].startswith("PASS") and registration["promoted"] and registration["protected_state_unchanged"]
        assert digest(registered / "independent-registration/post-state.json") == review["post_state"]["sha256"]
        assert digest(installed / "independent-installation/post-install-inventory.json") == review["retained_source_build_inventory"]["inventory_sha256"]
        assert digest(installed / "operation/prefix-inventory.json") == review["prefix_inventory"]["inventory_sha256"]
        assert all(digest(Path(p)) == sha for p, sha in registration["proposal"]["bindings"].items())
        assert all(digest(Path(__file__).with_name(n)) == sha for n, sha in registration["proposal"]["helpers"].items())
        assert digest(Path(__file__).with_name("p2996_register.py")) == review["helper_sha256"]
        assert report["witness_sha256"] == runtime["witness_sha256"] and prefix == Path(review["proposal"]["prefix"])
        report["admission_sha256"] = digest(evidence / "admission.json")
        contract = evidence / "source-contract.json"
        assert digest(contract) == admission["source_contract_sha256"] == "eaf03d7420cb0075ebfc526554500d1a66cd510d3a9e8ebece446b6c27578c14"
        assert all(digest(source / r["path"]) == r["sha256"] for r in load(contract)["references"])
        assert all(digest(Path(r["path"])) == r["sha256"] for r in load(contract)["local_receipt_references"])
        prerequisite = ROOT / "evidence/p2996-analysis/analysis-review.json"
        assert digest(prerequisite) == "ef444df5bd6b63d798bde498dafbde147f612dd1ad2d84d86a9482357e293a10"
        assert load(prerequisite)["result"].startswith("PASS") and not load(prerequisite)["findings"]
        report["source_contract_sha256"] = digest(contract)
        protected()
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]

        def source_state(stage):
            for label, arguments in (("head", ["rev-parse", "HEAD"]), ("tree", ["rev-parse", "HEAD^{tree}"]),
                                     ("status", ["status", "--porcelain", "--untracked-files=all"]),
                                     ("diff", ["diff", "--no-ext-diff", "--binary"])):
                run(stage + "-" + label, git + arguments)
                assert (directory / (stage + "-" + label + ".stdout")).read_bytes() == (registered / ("operation/source-after-" + label + ".stdout")).read_bytes()

        source_state("source-before")
        normal = run("default-before", normal_argv)
        assert normal == (registered / "operation/default-after.stdout").read_text()
        mise = configuration["mise"]
        assert digest(Path(mise["path"])) == mise["sha256"]
        stage = isolated(directory / "discovery") | {"MISE_INSTALLS_DIR": str(Path.home() / ".local/share/mise/installs")}
        located = run("native-where", [mise["path"], "--no-config", "--no-hooks", "--no-env", "-C", stage["MISE_CEILING_PATHS"],
                                      "where", review["proposal"]["tool"]], environment=stage).strip()
        assert Path(located).resolve() == prefix
        env["MARKETPLACE_P2996_PREFIX"] = str(prefix)
        base = [mise["path"], "--no-hooks", "-C", directory / "cwd", "-E", "p2996", "exec", "--fresh-env", "--no-deps", "--"]
        selected = json.loads(run("named-profile", base + normal_argv[-2:]))
        assert selected == runtime["selected_environment"]
        assert digest(Path(configuration["sdk"]["path"]) / "SDKSettings.json") == configuration["sdk"]["settings_sha256"]
        assert digest(LOCK_MODULE) == LOCK_SHA
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-p2996-coverage", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            assert not any(re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy",
                                       Path(line.split(maxsplit=2)[-1]).name) for line in processes.splitlines())
            assert shutil.disk_usage(directory).free >= 8 * 1024**3
            report["tool_hashes"] = {name: digest(prefix / "bin" / name) for name in ("clang++", "llvm-profdata", "llvm-cov")}
            profile_runtime = prefix / "lib/clang/21/lib/darwin/libclang_rt.profile_osx.a"
            report["profile_runtime_sha256"] = digest(profile_runtime)
            assert report["profile_runtime_sha256"] == "48dd00286225897919bf6fb6a6630245d9489ac8a6544acb55b9350486f3d31b"
            copied, wrapper = directory / witness.name, directory / "coverage.cpp"
            copied.write_bytes(witness.read_bytes())
            wrapper.write_text(load(contract)["fixture"]["wrapper"]["text"])
            assert digest(wrapper) == "1b0a991f9b9c5677d5fb3f82eb6c891856bda81d2095427590171546db9d44e7"
            original_sources = {p.name: digest(p) for p in (copied, wrapper)}
            binary, raw, merged = (directory / name for name in ("coverage", "coverage.profraw", "coverage.profdata"))
            assert not any(p.exists() for p in (binary, raw, merged))
            libraries = [prefix / "lib" / name for name in ("libc++.dylib", "libc++abi.dylib", "libunwind.dylib")]
            run("coverage-compile", base + [prefix / "bin/clang++", *runtime["flags"], "-O0",
                "-fprofile-instr-generate", "-fcoverage-mapping", wrapper, "-nostdlib++", *libraries,
                "-Wl,-rpath," + str(prefix / "lib"), "-o", binary], timeout=60, descriptor=fd)
            assert binary.is_file() and binary.stat().st_size > 0
            output = run("coverage-run", base + ["/usr/bin/env", "LLVM_PROFILE_FILE=" + str(raw),
                         "DYLD_PRINT_LIBRARIES=1", binary], descriptor=fd)
            assert output == "reflection value=43 exception=ok\n" and raw.is_file() and raw.stat().st_size > 0
            loaded = [line[line.find(str(prefix)):].strip() for line in (directory / "coverage-run.stderr").read_text().splitlines() if str(prefix) in line]
            assert all(any(Path(p).resolve() == lib.resolve() for p in loaded) for lib in libraries)
            report["loaded_private_images"] = loaded
            run("coverage-merge", base + [prefix / "bin/llvm-profdata", "merge", "-sparse", "--num-threads=1",
                "--failure-mode=any", raw, "-o", merged], descriptor=fd)
            assert merged.is_file() and merged.stat().st_size > 0
            export = base + [prefix / "bin/llvm-cov", "export", binary, "--format=text", "--num-threads=1", "--debuginfod=false"]
            output = run("coverage-export", export + ["--instr-profile=" + str(merged), wrapper, copied], descriptor=fd)
            diagnostic = (directory / "coverage-export.stderr").read_text()
            assert not any(text in diagnostic for text in ("functions have mismatched data", "profile data may be out of date", "error:"))
            data = json.loads(output)
            assert data["type"] == "llvm.coverage.json.export" and data["version"] == "3.0.0" and len(data["data"]) == 1
            data = data["data"][0]
            targets = {}
            for name, count in (("main", 1), ("coverage_branch", 2)):
                matches = [f for f in data["functions"] if f["name"] == name and str(wrapper) in f["filenames"]]
                assert len(matches) == 1 and matches[0]["count"] == count
                targets[name] = matches[0]
            branches = targets["coverage_branch"]["branches"]
            assert len(branches) == 1 and len(branches[0]) == 9
            branch = branches[0]
            assert branch[0] == branch[2] == 6 and branch[4:6] == [1, 1]
            assert targets["coverage_branch"]["filenames"][branch[6]] == str(wrapper)
            reflection = [f for f in data["functions"] if str(copied) in f["filenames"] and f["count"] > 0]
            assert reflection
            files = {f["filename"]: f for f in data["files"]}
            assert str(wrapper) in files and str(copied) in files
            summary = files[str(wrapper)]["summary"]["branches"]
            assert summary == {"count": 2, "covered": 2, "notcovered": 0, "percent": 100}
            totals = data["totals"]
            for name in ("lines", "regions", "functions", "branches"):
                item = totals[name]
                assert type(item["count"]) is int and type(item["covered"]) is int and 0 < item["covered"] <= item["count"]
                assert math.isfinite(item["percent"]) and 0 <= item["percent"] <= 100
                if name in ("regions", "branches"):
                    assert item["count"] == item["covered"] + item["notcovered"]
            assert totals["functions"]["covered"] >= 3 and totals["branches"]["covered"] >= 2
            report["coverage"] = {"targets": targets, "executed_reflection_functions": reflection,
                                  "wrapper_branches": summary, "totals": totals}
            absent = directory / "absent.profdata"
            assert not absent.exists()
            output = run("coverage-absent-data", export + ["--instr-profile=" + str(absent), wrapper, copied], descriptor=fd, expected=1)
            diagnostic = (directory / "coverage-absent-data.stderr").read_text()
            assert not output and not absent.exists() and "could not read profile data!" in diagnostic and str(absent) in diagnostic
            assert digest(copied) == digest(witness) == report["witness_sha256"]
            assert all(digest(directory / name) == sha for name, sha in original_sources.items())
            report["artifacts"] = {p.name: {"path": str(p), "sha256": digest(p), "bytes": p.stat().st_size}
                                   for p in (copied, wrapper, binary, raw, merged)}
        report["lease_released"] = True
        env.pop("MARKETPLACE_P2996_PREFIX")
        assert run("default-after", normal_argv) == normal
        source_state("source-after")
        report["state"] = "PASS: LLVM source-based coverage with reflection controls"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}))


if __name__ == "__main__":
    main()
