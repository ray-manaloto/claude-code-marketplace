"""Prepare or install the reviewed private LLVM build; runtime acceptance is separate."""

import argparse
import ast
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_math_apply import FILES as MATH_FILES
from p2996_sdk_compat import FILES as SDK_FILES
from vcpkg_register import install_entries


def prefix_inventory(prefix):
    assert prefix.is_dir() and prefix == prefix.resolve()
    result = []
    for path in sorted(prefix.rglob("*")):
        assert path.resolve(strict=True).is_relative_to(prefix), str(path)
        row = {"path": str(path.relative_to(prefix)), "mode": oct(path.lstat().st_mode & 0o777)}
        if path.is_symlink():
            row.update(kind="symlink", target=os.readlink(path))
        elif path.is_dir():
            row.update(kind="directory")
        else:
            assert path.is_file(), str(path)
            row.update(kind="file", sha256=digest(path), bytes=path.stat().st_size)
        result.append(row)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    directory = args.run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.is_relative_to(ROOT):
        parser.error("use a new normalized absolute private directory outside this worktree")
    load = lambda p: json.loads(p.read_text())
    evidence = ROOT / "evidence/p2996-install"
    built = ROOT / "evidence/p2996-math-resume"
    qualified = load(built / "operation/qualification.json")
    configuration = qualified["proposal"]["configuration"]
    workspace, source = Path(qualified["proposal"]["workspace"]), Path(configuration["source"])
    build, prefix = workspace / "build", workspace / "prefix"
    if directory.is_relative_to(workspace) or directory.is_relative_to(source):
        parser.error("run directory must not modify source, build or install trees")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    baseline = load(built / "independent-build/post-state.json")
    inventory = load(built / "independent-build/post-build-inventory.json")
    contract = load(evidence / "static-contract.json")
    manifests = [build / "install_manifest.txt", *[build / "runtimes" / child / "install_manifest.txt"
                 for child in ("builtins-bins", "runtimes-bins")]]
    report = {"state": "running", "install_requested": args.install, "installation_started": False,
              "helper_sha256": digest(Path(__file__)), "commands": []}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}
    cleared = ("DESTDIR", "CMAKE_INSTALL_MODE", "CMAKE_INSTALL_PARALLEL_LEVEL")
    for name in cleared:
        env.pop(name, None)

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    helper = built / "operation/p2996_build.py.source"
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
            if p == prefix or p in manifests:
                continue
            assert os.path.lexists(p) == row["lexists"] and p.exists() == row["exists"], str(p)
            if "sha256" in row:
                assert digest(p) == row["sha256"] and str(p.resolve()) == row["resolved_path"], str(p)
            assert (os.readlink(p) if p.is_symlink() else None) == row.get("symlink_target"), str(p)

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        review = load(built / "build-review.json")
        assert qualified["state"] == "PASS: build only; artifacts require review"
        assert qualified["protected_state_unchanged"] and qualified["lease"]["released_after_operation"]
        assert len(qualified["commands"]) == 22 and all(r["returncode"] == 0 for r in qualified["commands"])
        assert review["result"].startswith("PASS") and not review["findings"]
        assert review["operation_sha256"] == digest(built / "operation/qualification.json")
        assert review["helper_sha256"] == qualified["helper_sha256"] == digest(helper)
        for name in ("post-state.json", "post-build-inventory.json"):
            expected = next(r["sha256"] for r in review["supporting_receipts"] if Path(r["path"]).name == name)
            assert digest(built / "independent-build" / name) == expected
        assert workspace == workspace.resolve() and source == source.resolve() and build == build.resolve()
        assert contract["roots"] == {"build": str(build), "configured_prefix": str(prefix), "source": str(source)}
        assert contract["expected_ordinary_manifests"] == list(map(str, manifests))
        assert not contract["unclassified_generated_command_names"]
        assert all(not r["Parallel"] for r in contract["generated_install_controls"])
        assert not os.path.lexists(prefix) and all(not os.path.lexists(p) for p in manifests)
        patches = [r for kind in ("sdk_adaptation", "math_adaptation")
                   for r in qualified["proposal"][kind]["patch"]["files"]]
        assert tuple(r["path"] for r in patches) == (*SDK_FILES, *MATH_FILES)
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]

        def source_state(stage):
            assert run(stage + "-head", git + ["rev-parse", "HEAD"]).strip() == configuration["pin"]
            assert run(stage + "-tree", git + ["rev-parse", "HEAD^{tree}"]).strip() == configuration["tree"]
            assert run(stage + "-status", git + ["status", "--porcelain", "--untracked-files=all"]).splitlines() == sorted(" M " + r["path"] for r in patches)
            assert all(digest(source / r["path"]) == r["after_sha256"] for r in patches)
            run(stage + "-diff", git + ["diff", "--no-ext-diff", "--binary"])
            assert digest(directory / (stage + "-diff.stdout")) == review["source_diff_sha256"]

        inputs = {str(build / r["relative_to_build"]): r["sha256"] for r in contract["generated_script_hash_manifest"]}
        inputs.update({r["path"]: r["sha256"] for r in contract["relevant_script_and_documentation_refs"] + contract["generated_install_controls"]})
        tools = [Path(r["executable"]) for r in contract["executable_side_effects"] if r["executable"].startswith("/")]
        inputs.update({str(p): digest(p) for p in tools})
        inputs.update({str(Path(r.get("resolved_path", r.get("path")))): r["sha256"]
                       for r in qualified["proposal"]["inputs"].values()})
        receipts = [built / "operation/qualification.json", built / "build-review.json", helper,
                    built / "independent-build/post-state.json", built / "independent-build/post-build-inventory.json",
                    evidence / "static-contract.json"]
        bindings = {str(p): digest(p) for p in receipts} | inputs

        def inputs_unchanged():
            assert all(digest(Path(p)) == sha for p, sha in bindings.items())
            assert prefix.parent == prefix.parent.resolve() and build == build.resolve()

        inputs_unchanged()
        source_state("source")
        base = [configuration["mise"]["path"], "--no-hooks", "-C", directory / "cwd", "-E", "cpp-build",
                "exec", "--fresh-env", "--no-deps", "--", "/usr/bin/env",
                *[part for name in cleared for part in ("-u", name)]]
        native = contract["intended_commands_not_executed"]
        assert native == [[configuration["cmake"]["resolved_path"], "--install", str(p.parent),
                           "--config", "Release", "--prefix", str(prefix)] for p in manifests]
        normal = run("default-before", normal_argv)
        keys = ["CC", "CXX", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "MARKETPLACE_CPP_LANE", *cleared]
        probe = "import os,json,sys;print(json.dumps({k:os.environ.get(k,'') for k in sys.argv[1:]}))"
        observed = json.loads(run("install-environment", base + [sys.executable, "-B", "-c", probe, *keys]))
        assert observed == dict.fromkeys(keys, "") | {"MARKETPLACE_CPP_LANE": "tools-only"}
        proposal = {"workspace": str(workspace), "prefix": str(prefix), "bindings": bindings,
                    "source_diff_sha256": review["source_diff_sha256"], "commands": native,
                    "manifest_paths": list(map(str, manifests)), "aliases": contract["aliases"],
                    "timeout_per_install_seconds": 300, "minimum_start_free_bytes": 32 * 1024**3,
                    "disk_reserve_bytes": 8 * 1024**3, "host_lock_sha256": LOCK_SHA,
                    "helpers": {name: digest(Path(__file__).with_name(name)) for name in
                                ("gcc_install.py", "gcc_bottles.py", "mise_link_probe.py", "vcpkg_register.py",
                                 "p2996_configure.py", "p2996_sdk_compat.py", "p2996_math_apply.py")}}
        report.update(proposal=proposal, observed_environment=observed)
        protected()
        if args.install:
            admission = load(evidence / "admission.json")
            prepared = load(evidence / "preparation-review.json")
            assert admission["helper_sha256"] == digest(Path(__file__)) == prepared["helper_sha256"]
            assert admission["proposal"] == proposal == prepared["proposal"]
            assert admission["run_directory"] == str(directory)
            assert admission["review_sha256"] == digest(evidence / "preparation-review.json")
            assert prepared["result"].startswith("PASS") and not prepared["findings"]
            assert digest(LOCK_MODULE) == LOCK_SHA
            spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
            lease = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lease)
            assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
            assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
            with lease.held(lease.HEAVY_GATE, "marketplace-p2996-install", wait_s=0, out=io.StringIO()) as fd:
                assert fd is not None
                processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
                assert not any(Path(line.split(maxsplit=2)[-1]).name in {"ninja", "cmake", "make", "gmake", "clang", "clang++", "clang-21", "gcc-16", "g++-16", "cc1", "cc1plus", "ld"} for line in processes.splitlines())
                assert directory.stat().st_dev == build.stat().st_dev
                assert shutil.disk_usage(directory).free >= proposal["minimum_start_free_bytes"]
                expected = lease.lock_path(lease.HEAVY_GATE).stat()
                fd_probe = "import os,json,sys;s=os.fstat(int(sys.argv[1]));print(json.dumps([s.st_dev,s.st_ino]))"
                assert json.loads(run("lease-descriptor", base + [sys.executable, "-B", "-c", fd_probe, str(fd)], descriptor=fd)) == [expected.st_dev, expected.st_ino]
                protected()
                inputs_unchanged()
                source_state("source-immediate")
                assert not os.path.lexists(prefix) and all(not os.path.lexists(p) for p in manifests)
                report["installation_started"] = True
                for label, argv in zip(("install-outer", "install-builtins", "install-runtimes"), native, strict=True):
                    run(label, base + argv, timeout=proposal["timeout_per_install_seconds"], descriptor=fd, monitor=True)
                source_state("source-after")
                inputs_unchanged()
                installed = prefix_inventory(prefix)
                installed_paths = {str(prefix / r["path"]) for r in installed if r["kind"] != "directory"}
                listed = set()
                for index, manifest in enumerate(manifests):
                    assert manifest.is_file() and not manifest.is_symlink()
                    text = manifest.read_text()
                    (directory / ("install-manifest-" + str(index) + ".txt")).write_text(text)
                    for name in text.splitlines():
                        p = Path(os.path.normpath(name))
                        assert p.is_absolute() and p.is_relative_to(prefix) and p.resolve(strict=True).is_relative_to(prefix)
                        listed.add(str(p))
                for row in contract["aliases"]:
                    p = Path(row["destination"])
                    assert p.is_symlink() and os.readlink(p) == row["target_text"]
                    assert p.resolve(strict=True) == Path(row["target_resolved_relative_to_destination"]).resolve(strict=True)
                    listed.add(str(p))
                assert listed == installed_paths, (sorted(listed - installed_paths), sorted(installed_paths - listed))
                out = directory / "prefix-inventory.json"
                out.write_text(json.dumps(installed, indent=2) + "\n")
                report["prefix_inventory"] = {"path": str(out), "sha256": digest(out), "entries": len(installed)}
            report["lease_released"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: installation only; artifact and runtime review pending" if args.install else "PASS: preparation only"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            report["build_and_protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            report["prefix_exists"] = os.path.lexists(prefix)
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
