"""Prepare or run the reviewed LLVM build; installation is a separate operation."""

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

from gcc_install import ROOT, digest, package_state, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_math_apply import FILES as MATH_FILES
from p2996_sdk_compat import FILES as SDK_FILES
from vcpkg_register import install_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--sdk-compatibility", action="store_true")
    parser.add_argument("--math-compatibility", action="store_true")
    args = parser.parse_args()
    if args.sdk_compatibility and not args.resume:
        parser.error("--sdk-compatibility requires --resume")
    if args.math_compatibility and not args.sdk_compatibility:
        parser.error("--math-compatibility requires --sdk-compatibility and --resume")
    directory = args.run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.is_relative_to(ROOT):
        parser.error("use a new normalized absolute private directory outside this worktree")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    report = {"state": "running", "build_requested": args.build, "resume": args.resume,
              "helper_sha256": digest(Path(__file__)), "commands": []}
    load = lambda path: json.loads(path.read_text())
    evidence = ROOT / ("evidence/p2996-resume" if args.sdk_compatibility else "evidence/p2996-build")
    if args.math_compatibility:
        evidence = ROOT / "evidence/p2996-math-resume"
    historical = read("install-preimages.json")
    before = {name: historical[name] for name in ("global_files", "packages", "glib_files")}
    normal_argv = historical["normal_environment"]["argv"]
    for name in before["global_files"]:
        p = Path.home() / ".config/mise" / name
        assert not p.is_symlink()
        before["global_files"][name] = {"sha256": digest(p), "mode": oct(p.stat().st_mode & 0o777)}
    before["packages"] = {name: package_state(name) for name in before["packages"]}
    before["glib_files"] = {name: {"sha256": digest(Path(name))} for name in before["glib_files"]}
    report["protected_before"] = before
    data = Path.home() / ".local/share/mise"
    dirs = {str(data / name): snapshot(data / name) for name in ("shims", "command-wrappers")}
    installs = install_entries(data / "installs")
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def run(label, argv, timeout=35, descriptor=None, monitor=False):
        argv = list(map(str, argv))
        row = {"case": label, "argv": argv, "started_at": datetime.now(timezone.utc).isoformat()}
        report["commands"].append(row)
        paths = [directory / (label + suffix) for suffix in (".stdout", ".stderr")]
        save()
        with paths[0].open("wb") as out, paths[1].open("wb") as err:
            started = time.monotonic()
            p = subprocess.Popen(argv, env=env, cwd=directory, stdin=subprocess.DEVNULL,
                                 stdout=out, stderr=err, start_new_session=True,
                                 pass_fds=() if descriptor is None else (descriptor,))
            try:
                row["pid"] = p.pid
                save()
                while p.poll() is None:
                    remaining = timeout - (time.monotonic() - started)
                    if remaining <= 0:
                        raise subprocess.TimeoutExpired(argv, timeout)
                    try:
                        p.wait(timeout=min(15, remaining))
                    except subprocess.TimeoutExpired:
                        if monitor:
                            row["last_monitor"] = {"at": datetime.now(timezone.utc).isoformat(),
                                                   "free_bytes": shutil.disk_usage(directory).free}
                            save()
                            assert row["last_monitor"]["free_bytes"] >= 8 * 1024**3, "disk reserve exhausted"
            except BaseException:
                # Keep repeated termination requests from interrupting cleanup or its failure receipt.
                signals = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)
                previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, signals)
                for signum in signals:
                    signal.signal(signum, signal.SIG_IGN)
                signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
                row["interrupted"] = True
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(p.pid, sig)
                    except ProcessLookupError:
                        pass
                    if sig == signal.SIGTERM:
                        try:
                            p.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            pass
                p.wait()
                raise
            finally:
                row.update(returncode=p.returncode, elapsed_seconds=time.monotonic() - started,
                           logs=[{"path": str(f), "sha256": digest(f)} for f in paths])
                save()
        print(json.dumps({"case": label, "returncode": p.returncode}), flush=True)
        assert p.returncode == 0, label
        return paths[0].read_text()

    def protected():
        preserved(before)
        assert all(snapshot(Path(path)) == value for path, value in dirs.items())
        assert install_entries(data / "installs") == installs

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        configured = ROOT / "evidence/p2996-configure"
        qualification = load(configured / "operation/qualification.json")
        assert qualification["state"].startswith("PASS") and qualification["protected_state_unchanged"]
        assert load(configured / "operation-review.json")["result"].startswith("PASS")
        assert load(configured / "generated-review.json")["disposition"].startswith("PASS")
        configuration = qualification["proposal"]
        workspace = Path(load(configured / "admission.json")["run_directory"])
        build, prefix = workspace / "build", workspace / "prefix"
        assert directory.stat().st_dev == build.stat().st_dev, "disk checks require the build filesystem"
        source = Path(configuration["source"])
        for row in qualification["generated"]:
            assert digest(Path(row["path"])) == row["sha256"], row["path"]
        assert not os.path.lexists(prefix)
        assert args.resume or not (build / ".ninja_log").exists(), "existing build requires --resume"
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]
        adaptation = None
        compat = ROOT / "evidence/p2996-sdk-compatibility"
        if args.sdk_compatibility:
            applied = load(compat / "operation/qualification.json")
            reviewed = load(compat / "application-review.json")
            patch = applied["proposal"]["adaptation"]
            assert applied["state"] == "PASS: exact source adaptation applied"
            assert applied["applied"] and applied["lease_released"] and applied["protected_state_unchanged"]
            assert len(applied["commands"]) == 11 and all(row["returncode"] == 0 for row in applied["commands"])
            assert reviewed["result"].startswith("PASS") and not reviewed["findings"]
            assert reviewed["operation_sha256"] == digest(compat / "operation/qualification.json")
            assert reviewed["helper_sha256"] == applied["helper_sha256"] == digest(Path(__file__).with_name("p2996_sdk_compat.py"))
            assert reviewed["patch_sha256"] == patch["patch_sha256"] == digest(compat / "scratch/rdf-comparator.patch")
            assert reviewed["diff_sha256"] == applied["diff_sha256"]
            assert patch == load(compat / "scratch/proposal.json")
            assert patch["base_commit"] == configuration["pin"] and Path(patch["source"]) == source == source.resolve()
            assert tuple(row["path"] for row in patch["files"]) == SDK_FILES
            adaptation = {"patch": patch, "diff_sha256": applied["diff_sha256"],
                          "receipts": {name: digest(compat / name) for name in
                                       ("operation/qualification.json", "application-review.json",
                                        "scratch/proposal.json", "scratch/rdf-comparator.patch")}}
        history = {str(build / name): digest(build / name) for name in (".ninja_log", ".ninja_deps")} if args.resume else {}
        math_adaptation = None
        math = ROOT / "evidence/p2996-math-application"
        if args.math_compatibility:
            applied = load(math / "operation/qualification.json")
            reviewed = load(math / "application-review.json")
            patch = applied["proposal"]["adaptation"]
            assert applied["state"] == "PASS: exact math adaptation applied" and applied["applied"]
            assert applied["lease_released"] and applied["build_and_protected_state_unchanged"]
            assert len(applied["commands"]) == 18 and all(row["returncode"] == 0 for row in applied["commands"])
            assert reviewed["result"].startswith("PASS") and not reviewed["findings"]
            assert reviewed["operation_sha256"] == digest(math / "operation/qualification.json")
            assert reviewed["helper_sha256"] == applied["helper_sha256"] == digest(Path(__file__).with_name("p2996_math_apply.py"))
            scratch = ROOT / "evidence/p2996-math-compatibility"
            assert reviewed["patch_sha256"] == patch["patch_sha256"] == digest(scratch / "scratch/sdk-math.patch")
            assert reviewed["diff_sha256"] == applied["diff_sha256"]
            assert patch == load(scratch / "scratch/proposal.json")
            assert patch["prior_source_diff_sha256"] == adaptation["diff_sha256"]
            assert patch["base_commit"] == configuration["pin"] and Path(patch["source"]) == source
            assert tuple(row["path"] for row in patch["files"]) == MATH_FILES
            retained = scratch / "independent-scratch/retained-preimages.json"
            closure = ROOT / "evidence/p2996-resume/failure-closure-review.json"
            assert digest(closure) == patch["failure_closure_sha256"]
            assert digest(retained) == applied["proposal"]["receipts"][str(retained.relative_to(ROOT))]
            history = {row["path"]: row["sha256"] for row in load(retained)["inventory_records"]
                       if "sha256" in row and Path(row["path"]).is_relative_to(build)}
            ninja_state = load(closure)["incremental_state"]
            assert len(ninja_state) == 6 and all(history[path] == sha for path, sha in ninja_state.items())
            assert all(str(build / "runtimes" / child / "CMakeCache.txt") in history
                       for child in ("builtins-bins", "runtimes-bins"))
            assert all(digest(Path(path)) == sha for path, sha in history.items())
            receipts = [math / "operation/qualification.json", math / "application-review.json",
                        scratch / "scratch/proposal.json", scratch / "scratch/sdk-math.patch", retained, closure]
            math_adaptation = {"patch": patch, "diff_sha256": applied["diff_sha256"],
                               "receipts": {str(p.relative_to(ROOT)): digest(p) for p in receipts}}

        def source_state(stage):
            assert run(stage + "-head", git + ["rev-parse", "HEAD"]).strip() == configuration["pin"]
            assert run(stage + "-tree", git + ["rev-parse", "HEAD^{tree}"]).strip() == configuration["tree"]
            status = run(stage + "-status", git + ["status", "--porcelain", "--untracked-files=all"])
            if adaptation is None:
                assert status == ""
                return
            source_files = (*SDK_FILES, *(MATH_FILES if math_adaptation else ()))
            assert status.splitlines() == sorted(" M " + name for name in source_files)
            for name, sha in adaptation["receipts"].items():
                assert digest(compat / name) == sha
            patches = adaptation["patch"]["files"]
            if math_adaptation:
                for name, sha in math_adaptation["receipts"].items():
                    assert digest(ROOT / name) == sha
                patches = patches + math_adaptation["patch"]["files"]
            for row in patches:
                p = source / row["path"]
                assert p == p.resolve() and p.is_relative_to(source)
                assert digest(p) == row["after_sha256"], row["path"]
            run(stage + "-diff", git + ["diff", "--no-ext-diff", "--binary"])
            expected_diff = (math_adaptation or adaptation)["diff_sha256"]
            assert digest(directory / (stage + "-diff.stdout")) == expected_diff

        source_state("source")
        inputs = configuration["inputs"] | {"CMAKE": configuration["cmake"], "MISE": configuration["mise"]}
        for row in inputs.values():
            assert digest(Path(row.get("resolved_path", row.get("path")))) == row["sha256"]
        sdk = configuration["sdk"]
        assert digest(Path(sdk["path"]) / "SDKSettings.json") == sdk["settings_sha256"]
        assert digest(ROOT / "dev/toolchains/p2996-bootstrap.cmake") == configuration["cache_sha256"]
        values = {name: row["path"] for name, row in configuration["inputs"].items()}
        values.update(SDK=sdk["path"], PREFIX=str(prefix))
        base = [configuration["mise"]["path"], "--no-hooks", "-C", directory / "cwd", "-E", "cpp-build",
                "exec", "--fresh-env", "--no-deps", "--", "/usr/bin/env", "MAKEFLAGS=-j4",
                "CMAKE_BUILD_PARALLEL_LEVEL=4", "NINJA_STATUS=[%f/%t %es] ",
                *["MARKETPLACE_BOOTSTRAP_" + name + "=" + value for name, value in values.items()]]
        command = base + [configuration["cmake"]["resolved_path"], "--build", build, "--parallel", "4"]
        normal = run("default-before", normal_argv)
        keys = ["CC", "CXX", "CFLAGS", "CXXFLAGS", "CPPFLAGS", "LDFLAGS", "MARKETPLACE_CPP_LANE",
                "MAKEFLAGS", "CMAKE_BUILD_PARALLEL_LEVEL"]
        probe = "import os,json,sys;print(json.dumps({k:os.environ.get(k,'') for k in sys.argv[1:]}))"
        observed = json.loads(run("build-environment", base + [sys.executable, "-B", "-c", probe, *keys]))
        assert observed == dict.fromkeys(keys[:6], "") | {
            "MARKETPLACE_CPP_LANE": "tools-only", "MAKEFLAGS": "-j4", "CMAKE_BUILD_PARALLEL_LEVEL": "4"}
        proposal = {"configuration": configuration, "workspace": str(workspace), "resume": args.resume,
                    "sdk_adaptation": adaptation, "math_adaptation": math_adaptation, "incremental_state": history,
                    "jobs_per_build": 4, "capacity_job_allowance": 8, "timeout_seconds": 21600,
                    "minimum_start_free_bytes": 32 * 1024**3, "disk_reserve_bytes": 8 * 1024**3,
                    "host_lock_sha256": LOCK_SHA, "inputs": inputs,
                    "receipts": {name: digest(configured / name) for name in
                                 ("admission.json", "operation/qualification.json", "operation-review.json", "generated-review.json")},
                    "helpers": {name: digest(Path(__file__).with_name(name)) for name in
                                ("gcc_install.py", "gcc_bottles.py", "mise_link_probe.py", "vcpkg_register.py", "p2996_configure.py", "p2996_sdk_compat.py", "p2996_math_apply.py")}}
        report.update(proposal=proposal, build_argv=list(map(str, command)), observed_environment=observed)
        protected()
        if args.build:
            admission = load(evidence / "admission.json")
            review = evidence / "preparation-review.json"
            assert admission["helper_sha256"] == digest(Path(__file__))
            assert admission["proposal"] == proposal and admission["run_directory"] == str(directory)
            assert admission["review_sha256"] == digest(review) and load(review)["result"].startswith("PASS")
            assert digest(LOCK_MODULE) == LOCK_SHA
            spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
            lease = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lease)
            assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
            assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
            with lease.held(lease.HEAVY_GATE, "marketplace-p2996-build", wait_s=0, out=io.StringIO()) as fd:
                assert fd is not None
                processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
                active = [line for line in processes.splitlines() if Path(line.split(maxsplit=2)[-1]).name
                          in {"ninja", "cmake", "make", "gmake", "clang", "clang++", "clang-21",
                              "gcc-16", "g++-16", "cc", "c++", "cc1", "cc1plus", "ld", "ld.lld"}]
                memory = run("capacity-memory", ["/usr/bin/memory_pressure", "-Q"])
                capacity = {"load": os.getloadavg(), "cpus": os.cpu_count(), "active_builds": active,
                            "free_bytes": shutil.disk_usage(directory).free,
                            "memory_free_percent": int(re.search(r"free percentage: (\d+)%", memory)[1]),
                            "total_cpu_percent": sum(float(line.split()[1]) for line in processes.splitlines())}
                report["capacity"] = capacity
                assert not active and capacity["free_bytes"] >= proposal["minimum_start_free_bytes"]
                assert capacity["memory_free_percent"] >= 50 and capacity["cpus"] >= 8
                assert capacity["load"][0] <= capacity["cpus"] and capacity["total_cpu_percent"] <= 50 * capacity["cpus"]
                docker = "/Applications/Docker.app/Contents/Resources/bin/docker"
                assert run("docker-context", [docker, "context", "show"], timeout=15).strip() == admission["docker_context"]
                running = run("docker-census", [docker, "ps", "--format", "{{.ID}}\t{{.Image}}"], timeout=15)
                assert sorted(running.splitlines()) == admission["containers"]
                if running.strip():
                    stats = [json.loads(line) for line in run("docker-stats", [docker, "stats", "--no-stream", "--format", "{{json .}}"], timeout=20).splitlines()]
                    assert sorted(row["ID"] for row in stats) == sorted(line.split()[0] for line in running.splitlines())
                    capacity["container_cpu_percent"] = sum(float(row["CPUPerc"].removesuffix("%")) for row in stats)
                    assert capacity["container_cpu_percent"] <= 100
                expected = lease.lock_path(lease.HEAVY_GATE).stat()
                fd_probe = "import os,json,sys;s=os.fstat(int(sys.argv[1]));print(json.dumps([s.st_dev,s.st_ino]))"
                assert json.loads(run("lease-descriptor", base + [sys.executable, "-B", "-c", fd_probe, str(fd)], descriptor=fd)) == [expected.st_dev, expected.st_ino]
                protected()
                for row in inputs.values():
                    assert digest(Path(row.get("resolved_path", row.get("path")))) == row["sha256"]
                for row in qualification["generated"]:
                    assert digest(Path(row["path"])) == row["sha256"]
                source_state("source-immediate")
                assert all(digest(Path(path)) == sha for path, sha in history.items())
                assert not os.path.lexists(prefix)
                report["lease"] = {"path": str(lease.lock_path(lease.HEAVY_GATE)), "held": True}
                run("llvm-build", command, timeout=proposal["timeout_seconds"], descriptor=fd, monitor=True)
                source_state("source-after")
                if math_adaptation:
                    copied = (build / "lib/clang/21/include/float.h", build / "include/c++/v1/float.h")
                    assert all(digest(p) == row["after_sha256"] for p, row in zip(copied, math_adaptation["patch"]["files"], strict=True))
                    report["refreshed_math_headers"] = [{"path": str(p), "sha256": digest(p)} for p in copied]
                assert not os.path.lexists(prefix)
                required = [build / "bin" / name for name in ("clang", "clang++", "llvm-config", "clangd", "clang-format", "clang-tidy", "llvm-cov", "llvm-profdata")]
                required += [build / "runtimes" / child / "CMakeCache.txt" for child in ("builtins-bins", "runtimes-bins")]
                report["artifacts"] = [{"path": str(p), "resolved_path": str(p.resolve()), "sha256": digest(p), "bytes": p.stat().st_size} for p in required]
            report["lease"]["released_after_operation"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: build only; artifacts require review" if args.build else "PASS: preparation only"
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
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
