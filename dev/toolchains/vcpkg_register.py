"""Prepare a native vcpkg namespace; --apply promotes only that reviewed namespace."""

import argparse
import ctypes
from datetime import datetime, timezone
import errno
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess

from gcc_install import ROOT, digest, package_state, preserved, read
from mise_link_probe import isolated, snapshot


def promote(source, destination):
    native = ctypes.CDLL("/usr/lib/libSystem.B.dylib", use_errno=True).renamex_np
    native.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    native.restype = ctypes.c_int
    # macOS SDK sys/stdio.h: RENAME_EXCL | RENAME_NOFOLLOW_ANY.
    if native(os.fsencode(source), os.fsencode(destination), 0x04 | 0x10) != 0:
        raise OSError(ctypes.get_errno(), "exclusive namespace promotion failed")


def census(strict=True):
    p = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,comm="], text=True,
                       capture_output=True, check=True, timeout=15)
    rows = []
    for line in p.stdout.splitlines():
        pid, ppid, executable = line.strip().split(None, 2)
        if Path(executable).name not in {"mise", "brew", "ruby"}:
            continue
        q = subprocess.run(["/bin/ps", "-p", pid, "-o", "args="], text=True,
                           capture_output=True, timeout=10)
        if q.returncode == 1 and not q.stdout.strip():
            continue
        assert q.returncode == 0
        tokens = shlex.split(q.stdout)
        known = next((name for name in ("mcp:graphify", "mcp:cbm", "mcp:lab-results")
                      if tokens[1:] == ["run", "-q", name]), None)
        row = {"pid": int(pid), "ppid": int(ppid), "executable": executable, "known_task": known}
        rows.append(row)
    blockers = [row for row in rows if Path(row["executable"]).name != "mise" or not row["known_task"]]
    if strict:
        assert not blockers, blockers
    return {"recorded_at": datetime.now(timezone.utc).isoformat(), "processes": rows, "blockers": blockers}


def install_entries(directory):
    return {str(p.relative_to(directory)): {"mode": oct(p.lstat().st_mode & 0o777),
            "link": os.readlink(p) if p.is_symlink() else None}
            for tool in sorted(directory.iterdir())
            for p in [tool, *(sorted(tool.iterdir()) if tool.is_dir() and not tool.is_symlink() else [])]}


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
    evidence = ROOT / "evidence/vcpkg-registration"
    report = {"state": "running", "apply_requested": args.apply,
              "helper_sha256": digest(Path(__file__)), "commands": [],
              "promotion_attempted": False, "promoted": False}
    before = read("install-preimages.json")
    for name, row in before["global_files"].items():
        p = Path.home() / ".config/mise" / name
        assert not p.is_symlink()
        backup = directory / "backups" / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, backup)
        row.update(sha256=digest(p), mode=oct(p.stat().st_mode & 0o777), backup=str(backup))
        assert digest(backup) == row["sha256"], "backup/preimage mismatch: " + name
    report["global_preimages"] = before["global_files"]
    before["packages"] = {name: package_state(name) for name in before["packages"]}
    data = Path.home() / ".local/share/mise"
    installs = data / "installs"
    protected_dirs = {str(data / name): snapshot(data / name) for name in ("shims", "command-wrappers")}
    entries = install_entries(installs)
    destination = installs / "asdf-vcpkg"

    def save():
        (directory / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(label, argv, env):
        row = {"case": label, "argv": list(map(str, argv)),
               "started_at": datetime.now(timezone.utc).isoformat()}
        report["commands"].append(row)
        save()
        logs = [directory / (label + suffix) for suffix in (".stdout", ".stderr")]
        with logs[0].open("wb") as out, logs[1].open("wb") as err:
            p = subprocess.Popen(argv, env=env, cwd=directory, stdin=subprocess.DEVNULL,
                                 stdout=out, stderr=err, start_new_session=True)
            try:
                p.wait(timeout=45)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
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
                row.update(returncode=p.returncode, logs=[{"path": str(f), "sha256": digest(f)} for f in logs])
                save()
        print(json.dumps({"case": label, "returncode": p.returncode}), flush=True)
        assert p.returncode == 0, label
        return logs[0].read_text(), logs[1].read_text()

    def protected():
        preserved(before)
        assert all(snapshot(Path(p)) == value for p, value in protected_dirs.items())
        current = install_entries(installs)
        if report["promoted"]:
            assert destination.is_dir() and not destination.is_symlink()
            assert snapshot(destination) == report["proposal"]["namespace"]
            current = {k: v for k, v in current.items() if k.split("/")[0] != "asdf-vcpkg"}
        else:
            assert not destination.exists() and not destination.is_symlink()
        assert current == entries

    try:
        assert installs == installs.resolve() and installs.is_dir()
        assert not destination.exists() and not destination.is_symlink()
        assert all(not (data / "plugins" / name).exists() and not (data / "plugins" / name).is_symlink()
                   for name in ("vcpkg", "asdf-vcpkg"))
        qualified = json.loads((ROOT / "evidence/vcpkg-bootstrap/native/qualification.json").read_text())
        assert qualified["state"].startswith("PASS")
        prefix, source = Path(qualified["prefix"]), Path(qualified["source"])
        binary = Path(qualified["binary"]["path"])
        assert digest(binary) == qualified["binary"]["sha256"]
        assert (prefix / "bin/vcpkg").is_symlink() and (prefix / "bin/vcpkg").resolve() == binary
        version = qualified["checkout"]
        manifest = json.loads((ROOT / "vcpkg.json").read_text())
        assert manifest["builtin-baseline"] == version and manifest["dependencies"] == ["fmt"]
        assert json.loads((source / "versions/baseline.json").read_text())["default"]["fmt"] == {
            "baseline": "12.2.0", "port-version": 1}
        env = isolated(directory / "stage")
        for name in ("home", "downloads"):
            (directory / name).mkdir()
        env.update(HOME=str(directory / "home"), VCPKG_DISABLE_METRICS="1",
                   VCPKG_DOWNLOADS=str(directory / "downloads"),
                   GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
        acquisition = json.loads((ROOT / "evidence/vcpkg-preparation/git/acquisition.json").read_text())
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]
        assert run("source-head", git + ["rev-parse", "HEAD"], env)[0].strip() == version == acquisition["pin"]
        assert run("source-tree", git + ["rev-parse", "HEAD^{tree}"], env)[0].strip() == acquisition["tree"]
        assert run("source-clean", git + ["status", "--porcelain", "--untracked-files=all"], env)[0] == ""
        mise = read("install-proposal.json")["native_mise"]
        assert digest(Path(mise["path"])) == mise["sha256"]
        base = [mise["path"], "--no-config", "--no-hooks", "--no-env", "-C", env["MISE_CEILING_PATHS"]]
        tool = "asdf:vcpkg@" + version
        run("native-link", base + ["link", tool, prefix], env)
        namespace = directory / "stage/data/installs/asdf-vcpkg"
        assert set(p.name for p in namespace.iterdir()) == {version}
        assert (namespace / version).is_symlink() and (namespace / version).resolve() == prefix
        manifest_copy = directory / "vcpkg.json"
        shutil.copyfile(ROOT / "vcpkg.json", manifest_copy)
        run("native-manifest", [binary, "format-manifest", manifest_copy, "--disable-metrics"], env)
        assert manifest_copy.read_bytes() == (ROOT / "vcpkg.json").read_bytes()
        a, b, c = [directory / name for name in ("exclusive-source", "exclusive-existing", "exclusive-new")]
        a.mkdir(); b.mkdir()
        try:
            promote(a, b)
            raise AssertionError("exclusive rename overwrote an existing directory")
        except OSError as error:
            assert error.errno == errno.EEXIST
            report["exclusive_existing_errno"] = error.errno
        assert a.is_dir() and b.is_dir()
        promote(a, c)
        assert c.is_dir() and not a.exists()
        report["exclusive_new_returncode"] = 0
        context_path = Path(before["normal_environment"]["argv"][-1]).parent / "context.json"
        normal_env = json.loads(context_path.read_text())["environment"] | {"MISE_OFFLINE": "1"}
        normal = run("default-before", before["normal_environment"]["argv"], normal_env)[0]
        report["census"] = census(strict=args.apply)
        protected()
        report["proposal"] = {"destination": str(destination), "preimage": "absent",
                              "namespace": snapshot(namespace), "manifest_sha256": digest(ROOT / "vcpkg.json"),
                              "helpers": {name: digest(Path(__file__).with_name(name)) for name in
                                          ("gcc_install.py", "gcc_bottles.py", "mise_link_probe.py")}}
        if args.apply:
            admission = json.loads((evidence / "admission.json").read_text())
            assert admission["helper_sha256"] == digest(Path(__file__))
            assert admission["review_sha256"] == digest(evidence / "preparation-review.json")
            assert admission["proposal"] == report["proposal"]
            assert json.loads((evidence / "preparation-review.json").read_text())["result"].startswith("PASS")
            report["census_immediate"] = census()
            protected()
            assert namespace.stat().st_dev == installs.stat().st_dev
            report["promotion_attempted"] = True
            save()
            promote(namespace, destination)
            report["promoted"] = True
            save()
            assert snapshot(destination) == report["proposal"]["namespace"]
            env["MISE_INSTALLS_DIR"] = str(installs)
        out = run("fresh-version", base + ["exec", tool, "--no-deps", "--", "vcpkg", "version", "--disable-metrics"], env)[0]
        assert "2026-09-26-51bf87ca6e9bf3e622d84ff323bd202ab1ca0c0b" in out
        assert run("default-after", before["normal_environment"]["argv"], normal_env)[0] == normal
        protected()
        report["state"] = "PASS: global namespace promotion" if args.apply else "PASS: preparation only"
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
            try:
                report["destination_observed"] = {"exists": destination.exists(), "symlink": destination.is_symlink(),
                                                  "namespace": snapshot(destination) if destination.is_dir()
                                                  and not destination.is_symlink() else None}
            except BaseException as error:
                report["destination_observation_error"] = repr(error)
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
