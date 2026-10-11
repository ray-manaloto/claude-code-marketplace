"""Bootstrap the reviewed vcpkg checkout privately; never register a global tool."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess

from gcc_install import ROOT, digest, package_state, preserved, read
from mise_link_probe import isolated, snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.is_relative_to(ROOT):
        parser.error("use a new normalized absolute private directory outside this worktree")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    report = {"state": "running", "started_at": datetime.now(timezone.utc).isoformat(),
              "helper_sha256": digest(Path(__file__)), "commands": []}
    historical = read("install-preimages.json")
    before = {"global_files": {}, "packages": {}, "glib_files": {}}
    for name in historical["global_files"]:
        p = Path.home() / ".config/mise" / name
        assert not p.is_symlink()
        before["global_files"][name] = {"sha256": digest(p), "mode": oct(p.stat().st_mode & 0o777)}
    before["packages"] = {name: package_state(name) for name in historical["packages"]}
    before["glib_files"] = {name: {"sha256": digest(Path(name))} for name in historical["glib_files"]}
    protected_dirs = {str(Path.home() / ".local/share/mise" / name):
                      snapshot(Path.home() / ".local/share/mise" / name)
                      for name in ("shims", "command-wrappers")}
    report["protected_before"] = before

    def save():
        (directory / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(label, argv, env, timeout=45):
        row = {"case": label, "argv": list(map(str, argv)),
               "started_at": datetime.now(timezone.utc).isoformat()}
        report["commands"].append(row)
        save()
        logs = [directory / (label + suffix) for suffix in (".stdout", ".stderr")]
        with logs[0].open("wb") as out, logs[1].open("wb") as err:
            p = subprocess.Popen(argv, env=env, cwd=directory, stdin=subprocess.DEVNULL,
                                 stdout=out, stderr=err, start_new_session=True)
            try:
                p.wait(timeout=timeout)
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
                row.update(returncode=p.returncode,
                           logs=[{"path": str(f), "sha256": digest(f)} for f in logs])
                save()
        print(json.dumps({"case": label, "returncode": p.returncode}), flush=True)
        assert p.returncode == 0, label
        return logs[0].read_text(), logs[1].read_text()

    try:
        assert platform.system() == "Darwin" and platform.machine() == "arm64"
        inputs = ROOT / "evidence/vcpkg-preparation"
        acquisition = json.loads((inputs / "git/acquisition.json").read_text())
        source = Path(acquisition["source"])
        assert source == source.resolve() and not source.is_relative_to(ROOT)
        for row in acquisition["verified_inputs"]:
            assert digest(source / row["path"]) == row["sha256"], row["path"]
        for name in ("vcpkg", "vcpkg.part", "vcpkg.disable-metrics"):
            p = source / name
            assert not p.exists() and not p.is_symlink(), p
        metadata = dict(line.split("=", 1) for line in
                        (source / "scripts/vcpkg-tool-metadata.txt").read_text().splitlines())
        report.update(source=str(source), checkout=acquisition["pin"], tree=acquisition["tree"],
                      executable_release=metadata["VCPKG_TOOL_RELEASE_TAG"])
        for name in ("home", "downloads", "cache", "config", "data", "tmp", "empty-git"):
            (directory / name).mkdir()
        env = {"HOME": str(directory / "home"), "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
               "TMPDIR": str(directory / "tmp"), "GIT_CONFIG_GLOBAL": "/dev/null",
               "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0",
               "GIT_TEMPLATE_DIR": str(directory / "empty-git"), "VCPKG_DISABLE_METRICS": "1",
               "VCPKG_DOWNLOADS": str(directory / "downloads"), "NO_COLOR": "1"}
        for name in ("CACHE", "CONFIG", "DATA"):
            env["XDG_" + name + "_HOME"] = str(directory / name.lower())
        git = ["/usr/bin/git", "-C", str(source)]
        assert run("source-head", git + ["rev-parse", "HEAD"], env)[0].strip() == acquisition["pin"]
        assert run("source-tree", git + ["rev-parse", "HEAD^{tree}"], env)[0].strip() == acquisition["tree"]
        assert run("source-clean-before", git + ["status", "--porcelain", "--untracked-files=all"], env)[0] == ""
        preserved(before)
        report["admission"] = {"scope": "Pinned native macOS download and private smoke only",
                               "shared_writes": [], "new_source_files": ["vcpkg", "vcpkg.disable-metrics"]}
        run("native-bootstrap", ["/bin/sh", source / "bootstrap-vcpkg.sh", "-disableMetrics"], env, 300)
        binary = source / "vcpkg"
        sha512 = hashlib.sha512(binary.read_bytes()).hexdigest()
        assert sha512 == metadata["VCPKG_MACOS_SHA"] and binary.stat().st_mode & 0o111
        assert (source / "vcpkg.disable-metrics").is_file() and not (source / "vcpkg.part").exists()
        report["binary"] = {"path": str(binary), "sha512": sha512,
                            "sha256": digest(binary), "bytes": binary.stat().st_size}
        assert "arm64" in run("architectures", ["/usr/bin/lipo", "-archs", binary], env)[0].split()
        run("file", ["/usr/bin/file", binary], env)
        run("libraries", ["/usr/bin/otool", "-L", binary], env)
        version = run("arm64-version", ["/usr/bin/arch", "-arm64", binary, "version", "--disable-metrics"], env)[0]
        assert metadata["VCPKG_TOOL_RELEASE_TAG"] in version
        prefix = directory / "prefix"
        (prefix / "bin").mkdir(parents=True)
        (prefix / "bin/vcpkg").symlink_to(binary)
        stage = directory / "mise"
        private = isolated(stage) | env
        mise = read("install-proposal.json")["native_mise"]
        assert digest(Path(mise["path"])) == mise["sha256"]
        base = [mise["path"], "--no-config", "--no-hooks", "--no-env", "-C", str(stage / "cwd")]
        tool = "asdf:vcpkg@" + acquisition["pin"]
        run("native-link", base + ["link", tool, str(prefix)], private)
        fresh = base + ["exec", tool, "--no-deps", "--", "vcpkg"]
        out, err = run("fresh-version", fresh + ["version", "--debug", "--disable-metrics"], private)
        assert metadata["VCPKG_TOOL_RELEASE_TAG"] in out and str(source) in out + err
        run("fresh-triplets", fresh + ["help", "triplet", "--disable-metrics"], private)
        assert run("source-clean-after", git + ["status", "--porcelain", "--untracked-files=all"], env)[0] == ""
        report.update(prefix=str(prefix), state="PASS: private native vcpkg bootstrap and discovery only")
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            preserved(before)
            assert all(snapshot(Path(p)) == value for p, value in protected_dirs.items())
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
