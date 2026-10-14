"""Qualify the private P2996 compiler and runtimes with bounded sequential probes."""

import argparse
import ast
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

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from vcpkg_register import install_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    load = lambda p: json.loads(p.read_text())
    evidence = ROOT / "evidence/p2996-install"
    review = load(evidence / "installation-review.json")
    installed = load(evidence / "operation/qualification.json")
    inventory = load(evidence / "independent-installation/post-install-inventory.json")
    baseline = load(evidence / "independent-installation/post-state.json")
    configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
    prefix, workspace, source = map(Path, (inventory["prefix"], inventory["workspace"], configuration["source"]))
    if (not directory.is_absolute() or directory != directory.resolve()
            or any(directory.is_relative_to(p) for p in (ROOT, workspace, source))):
        parser.error("use a new normalized private directory outside project, source, build and prefix")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    witness = Path(__file__).with_suffix(".cpp")
    report = {"state": "running", "commands": [], "helper_sha256": digest(Path(__file__)),
              "witness_sha256": digest(witness), "prefix": str(prefix)}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    helper = ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source"
    assert digest(helper) == "7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f"
    node = next(n for n in ast.walk(ast.parse(helper.read_text()))
                if isinstance(n, ast.FunctionDef) and n.name == "run")
    scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(helper), "exec"), scope)
    run = scope["run"]

    def protected():
        preserved(baseline["protected"])
        assert all(snapshot(Path(p)) == value for p, value in baseline["directories"].items())
        assert install_entries(Path.home() / ".local/share/mise/installs") == baseline["install_entries"]
        for row in inventory["records"]:
            p = Path(row["path"])
            assert os.path.lexists(p) == row["lexists"] and p.exists() == row["exists"], str(p)
            if row["lexists"]:
                assert oct(p.lstat().st_mode & 0o777) == row["lstat_mode"], str(p)
            if row["exists"]:
                assert str(p.resolve()) == row["resolved_path"] and oct(p.stat().st_mode & 0o777) == row["mode"]
            if "sha256" in row:
                assert digest(p) == row["sha256"] and p.stat().st_size == row["bytes"], str(p)
            assert (os.readlink(p) if p.is_symlink() else None) == row.get("symlink_target"), str(p)
        assert prefix_inventory(prefix) == load(evidence / "operation/prefix-inventory.json")

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        admission = load(ROOT / "evidence/p2996-reflection/admission.json")
        assert admission["helper_sha256"] == report["helper_sha256"]
        assert admission["witness_sha256"] == report["witness_sha256"]
        assert admission["run_directory"] == str(directory) and admission["prefix"] == str(prefix)
        report["admission_sha256"] = digest(ROOT / "evidence/p2996-reflection/admission.json")
        assert digest(evidence / "installation-review.json") == "d9ee10dc202d0de4447393ec2a8391866c541c27ed469d874edd874bc6e81784"
        assert review["result"].startswith("PASS") and not review["findings"]
        assert review["operation_sha256"] == digest(evidence / "operation/qualification.json")
        assert installed["state"].startswith("PASS") and installed["build_and_protected_state_unchanged"]
        assert all(r["returncode"] == 0 for r in installed["commands"])
        for name in ("post-state.json", "post-install-inventory.json"):
            expected = next(r["sha256"] for r in review["supporting_receipts"] if Path(r["path"]).name == name)
            assert digest(evidence / "independent-installation" / name) == expected
        assert digest(evidence / "operation/prefix-inventory.json") == review["prefix_inventory_sha256"]
        assert digest(Path(__file__).with_name("p2996_install.py")) == installed["helper_sha256"]
        assert all(digest(Path(__file__).with_name(n)) == sha for n, sha in installed["proposal"]["helpers"].items())
        assert digest(Path(configuration["mise"]["path"])) == configuration["mise"]["sha256"]
        protected()
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]

        def source_state(stage):
            assert run(stage + "-head", git + ["rev-parse", "HEAD"]).strip() == configuration["pin"]
            assert run(stage + "-tree", git + ["rev-parse", "HEAD^{tree}"]).strip() == configuration["tree"]
            run(stage + "-diff", git + ["diff", "--no-ext-diff", "--binary"])
            assert digest(directory / (stage + "-diff.stdout")) == review["source_diff_sha256"]
            status = run(stage + "-status", git + ["status", "--porcelain", "--untracked-files=all"])
            assert status == (evidence / "operation/source-status.stdout").read_text()

        source_state("source-before")
        normal = run("default-before", normal_argv)
        assert json.loads(normal) == json.loads((evidence / "operation/default-after.stdout").read_text())
        assert "MARKETPLACE_P2996_PREFIX" not in env
        env["MARKETPLACE_P2996_PREFIX"] = str(prefix)
        base = [configuration["mise"]["path"], "--no-hooks", "-C", directory / "cwd", "-E", "p2996",
                "exec", "--fresh-env", "--no-deps", "--"]
        selected = json.loads(run("named-profile", base + normal_argv[-2:]))
        assert selected["selected"]["CC"] == str(prefix / "bin/clang")
        assert selected["selected"]["CXX"] == str(prefix / "bin/clang++")
        assert selected["selected"]["MARKETPLACE_CPP_LANE"] == "p2996"
        keys = ["CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "CPATH", "CPLUS_INCLUDE_PATH", "LIBRARY_PATH",
                "COMPILER_PATH", "SDKROOT", "DYLD_LIBRARY_PATH", "DYLD_FALLBACK_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES"]
        probe = "import os,json,sys;print(json.dumps({k:os.environ.get(k) for k in sys.argv[1:]}))"
        assert json.loads(run("isolated-environment", base + [sys.executable, "-B", "-c", probe, *keys])) == dict.fromkeys(keys)
        report["selected_environment"] = selected
        assert digest(LOCK_MODULE) == LOCK_SHA
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-p2996-reflection", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            assert not any(re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld",
                                       Path(line.split(maxsplit=2)[-1]).name) for line in processes.splitlines())
            assert shutil.disk_usage(directory).free >= 8 * 1024**3
            report["admission"] = {"owner": "/root", "scope": "Sequential private compiler probes, 60 seconds each",
                                   "at": datetime.now(timezone.utc).isoformat(), "load": os.getloadavg(), "lease_fd": fd}
            cxx = prefix / "bin/clang++"
            version = run("compiler-version", base + [cxx, "--no-default-config", "--version"], descriptor=fd)
            assert "clang version 21.0.0git" in version and configuration["pin"] in version
            sdk = Path(run("sdk-path", ["/usr/bin/xcrun", "--sdk", "macosx", "--show-sdk-path"]).strip()).resolve()
            assert str(sdk) == configuration["sdk"]["path"]
            assert digest(sdk / "SDKSettings.json") == configuration["sdk"]["settings_sha256"]
            flags = ["--no-default-config", "-std=c++26", "-freflection", "-fno-blocks", "-arch", "arm64",
                     "-mmacosx-version-min=27.0", "-isysroot", sdk, "-resource-dir", prefix / "lib/clang/21",
                     "-stdlib=libc++", "-nostdinc++", "-isystem", prefix / "include/c++/v1"]
            report["flags"] = list(map(str, flags))
            resource = run("resource-path", base + [cxx, *flags, "-print-resource-dir"], descriptor=fd).strip()
            assert Path(resource) == prefix / "lib/clang/21"
            macros = run("feature-macros", base + [cxx, *flags, "-dM", "-E", witness], timeout=60, descriptor=fd)
            report["feature_macros"] = dict(re.findall(r"^#define (__cplusplus|__clang_major__|_LIBCPP_VERSION) (.+)$", macros, re.M))
            assert report["feature_macros"] == {"__cplusplus": "202400L", "__clang_major__": "21", "_LIBCPP_VERSION": "210000"}
            dependencies = run("header-dependencies", base + [cxx, *flags, "-M", witness], timeout=60, descriptor=fd)
            assert str(prefix / "include/c++/v1/meta") in dependencies
            assert "/opt/homebrew/" not in dependencies and "/usr/include/c++" not in dependencies
            binary = directory / "reflection"
            libraries = [prefix / "lib" / name for name in ("libc++.dylib", "libc++abi.dylib", "libunwind.dylib")]
            run("reflection-build", base + [cxx, *flags, "-nostdlib++", "-O0", "-g", "-v", witness,
                                           *libraries, "-Wl,-rpath," + str(prefix / "lib"), "-o", binary], timeout=60, descriptor=fd)
            output = run("reflection-run", base + ["/usr/bin/env", "DYLD_PRINT_LIBRARIES=1", binary], timeout=60, descriptor=fd)
            assert output == "reflection value=43 exception=ok\n"
            dynamic = (directory / "reflection-run.stderr").read_text()
            loaded = [line[line.find(str(prefix)):].strip() for line in dynamic.splitlines() if str(prefix) in line]
            assert all(any(Path(p).resolve() == lib.resolve() for p in loaded) for lib in libraries), loaded
            direct = run("witness-libraries", ["/usr/bin/otool", "-L", binary]).splitlines()[1:]
            links = [line.strip().split(" (")[0].replace("@rpath/", str(prefix / "lib") + "/") for line in direct]
            assert all(str(lib.resolve()) in [str(Path(p).resolve()) for p in links] for lib in libraries)
            symbols = run("witness-symbols", ["/usr/bin/nm", "-m", "-u", binary])
            assert "___cxa_throw" in symbols and "___cxa_begin_catch" in symbols
            assert any("__ZNSt" in line and "(from libc++" in line for line in symbols.splitlines())
            negative = [f for f in flags if f != "-freflection"]
            try:
                run("without-reflection", base + [cxx, *negative, "-fsyntax-only", witness], timeout=60, descriptor=fd)
            except AssertionError:
                assert report["commands"][-1]["case"] == "without-reflection" and report["commands"][-1]["returncode"] == 1
            else:
                raise AssertionError("negative control unexpectedly compiled")
            assert "P2996 reflection requires -freflection" in (directory / "without-reflection.stderr").read_text()
            report["witness"] = {"path": str(binary), "sha256": digest(binary), "output": output, "loaded_private_images": loaded}
        report["lease_released"] = True
        env.pop("MARKETPLACE_P2996_PREFIX")
        assert json.loads(run("default-after", normal_argv)) == json.loads(normal)
        source_state("source-after")
        report["state"] = "PASS: P2996 reflection compile/link/run with private runtimes"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            report["protected_state_unchanged"] = True
        except Exception as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}))


if __name__ == "__main__":
    main()
