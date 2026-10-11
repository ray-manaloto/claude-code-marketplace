"""Prepare or apply the reviewed five-file LLVM SDK comparator adaptation."""

import argparse
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from gcc_install import ROOT, digest, package_state, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from vcpkg_register import install_entries

FILES = (
    "llvm/include/llvm/CodeGen/RDFRegisters.h", "llvm/include/llvm/CodeGen/RDFGraph.h",
    "llvm/lib/CodeGen/RDFLiveness.cpp", "llvm/lib/Target/Hexagon/RDFCopy.h",
    "llvm/lib/Target/Hexagon/RDFCopy.cpp",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    directory = args.run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.is_relative_to(ROOT):
        parser.error("use a new normalized absolute private directory outside this worktree")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    evidence = ROOT / "evidence/p2996-sdk-compatibility"
    load = lambda path: json.loads(path.read_text())
    proposal = load(evidence / "scratch/proposal.json")
    source, patch = Path(proposal["source"]), evidence / "scratch/rdf-comparator.patch"
    report = {"state": "running", "apply_requested": args.apply, "applied": False,
              "helper_sha256": digest(Path(__file__)), "commands": []}
    historical = read("install-preimages.json")
    before = {name: historical[name] for name in ("global_files", "packages", "glib_files")}
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
    normal_argv = historical["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        p = directory / "qualification.json.tmp"
        p.write_text(json.dumps(report, indent=2) + "\n")
        p.replace(directory / "qualification.json")

    def run(label, argv, descriptor=None):
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
                p.wait(timeout=45)
            except BaseException:
                signals = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)
                mask = signal.pthread_sigmask(signal.SIG_BLOCK, signals)
                for signum in signals:
                    signal.signal(signum, signal.SIG_IGN)
                signal.pthread_sigmask(signal.SIG_SETMASK, mask)
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

    def source_files(patched=False):
        for row in proposal["files"]:
            p = source / row["path"]
            assert p == p.resolve() and p.is_relative_to(source)
            assert digest(p) == row["after_sha256" if patched else "before_sha256"], row["path"]

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        configuration = load(ROOT / "evidence/p2996-configure/operation/qualification.json")["proposal"]
        assert source == Path(configuration["source"]) == source.resolve()
        assert proposal["base_commit"] == configuration["pin"]
        assert tuple(row["path"] for row in proposal["files"]) == FILES
        assert digest(patch) == proposal["patch_sha256"]
        probe = load(evidence / "scratch/qualification.json")
        assert probe["state"].startswith("PASS") and probe["proposal"] == proposal
        assert probe["source_and_protected_state_unchanged"] and probe["lease_released"]
        assert [(r["case"], r["returncode"]) for r in probe["commands"]] == [
            ("capacity-processes", 0), ("original-negative", 1), ("patched-graph", 0),
            ("patched-liveness", 0), ("patched-copy", 0)]
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]
        assert run("source-head", git + ["rev-parse", "HEAD"]).strip() == configuration["pin"]
        assert run("source-tree", git + ["rev-parse", "HEAD^{tree}"]).strip() == configuration["tree"]
        assert run("source-clean", git + ["status", "--porcelain", "--untracked-files=all"]) == ""
        source_files()
        run("patch-check", git + ["apply", "--check", patch])
        normal = run("default-before", normal_argv)
        report["proposal"] = {"adaptation": proposal, "probe_sha256": digest(evidence / "scratch/qualification.json"),
                              "lock_sha256": LOCK_SHA, "helpers": {name: digest(Path(__file__).with_name(name)) for name in
                              ("gcc_install.py", "gcc_bottles.py", "mise_link_probe.py", "vcpkg_register.py", "p2996_configure.py")}}
        protected()
        if args.apply:
            admission, review = load(evidence / "admission.json"), evidence / "preparation-review.json"
            assert admission["helper_sha256"] == digest(Path(__file__))
            assert admission["proposal"] == report["proposal"] and admission["run_directory"] == str(directory)
            assert admission["review_sha256"] == digest(review) and load(review)["result"].startswith("PASS")
            assert digest(LOCK_MODULE) == LOCK_SHA
            spec = importlib.util.spec_from_file_location("marketplace_compat_lock", LOCK_MODULE)
            lease = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lease)
            assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
            assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
            with lease.held(lease.HEAVY_GATE, "marketplace-sdk-comparator-apply", wait_s=0, out=io.StringIO()) as fd:
                assert fd is not None
                protected()
                source_files()
                assert digest(patch) == proposal["patch_sha256"]
                assert run("source-clean-immediate", git + ["status", "--porcelain", "--untracked-files=all"]) == ""
                run("patch-apply", git + ["apply", patch], descriptor=fd)
                report["applied"] = True
                source_files(patched=True)
                status = run("source-patched", git + ["status", "--porcelain", "--untracked-files=all"])
                assert status.splitlines() == sorted(" M " + name for name in FILES)
                run("patch-reverse-check", git + ["apply", "--reverse", "--check", patch])
                run("source-diff", git + ["diff", "--no-ext-diff", "--binary"])
                report["diff_sha256"] = digest(directory / "source-diff.stdout")
            report["lease_released"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: exact source adaptation applied" if args.apply else "PASS: preparation only"
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
