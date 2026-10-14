"""Acquire the accepted IWYU commit into a new private directory; never build it."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess

PIN = "791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3"
TREE = "b793b517dd7a261da9e574572264b6d59ed4b7c4"
REMOTE = "https://github.com/include-what-you-use/include-what-you-use.git"
ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True, help="new absolute private directory")
    args = parser.parse_args()
    directory = args.directory
    if not directory.is_absolute() or directory != directory.resolve():
        parser.error("directory must be an absolute normalized path")
    if directory.is_relative_to(ROOT):
        parser.error("keep the upstream checkout outside the marketplace worktree")
    primary = json.loads((ROOT / "evidence/iwyu-source/inputs/acquisition.json").read_text())
    if primary["pin"] != PIN or primary["tree"] != TREE:
        parser.error("primary source receipt differs from the accepted identity")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    source = directory / "source"
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_TERMINAL_PROMPT="0")
    report = {"state": "running", "started_at": datetime.now(timezone.utc).isoformat(),
              "source": str(source), "pin": PIN, "tree": TREE, "remote": REMOTE,
              "helper_sha256": digest(Path(__file__)), "commands": []}

    def save():
        (directory / "acquisition.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(label, arguments, timeout=60):
        argv = ["/usr/bin/git", *arguments]
        row = {"case": label, "argv": argv, "started_at": datetime.now(timezone.utc).isoformat()}
        report["commands"].append(row)
        save()
        logs = [directory / (label + suffix) for suffix in (".stdout", ".stderr")]
        with logs[0].open("wb") as out, logs[1].open("wb") as err:
            process = subprocess.Popen(argv, cwd=directory, env=environment, stdin=subprocess.DEVNULL,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                row["interrupted"] = True
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        pass
                    if sig == signal.SIGTERM:
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            pass
                process.wait()
                raise
            finally:
                row.update(returncode=process.returncode,
                           logs=[{"path": str(path), "sha256": digest(path)} for path in logs])
                save()
        print(json.dumps({"case": label, "returncode": process.returncode}), flush=True)
        if process.returncode:
            raise RuntimeError(f"{label} exited {process.returncode}; see private logs")
        return logs[0].read_text()

    try:
        run("git-version", ["--version"])
        run("init", ["init", "--template=", "--initial-branch=source-acquisition", str(source)])
        run("remote", ["-C", str(source), "remote", "add", "origin", REMOTE])
        run("fetch", ["-C", str(source), "-c", "fetch.fsckObjects=true", "-c", "pack.threads=1",
                      "fetch", "--depth=1", "--no-tags", "--no-recurse-submodules", "origin", PIN], 60)
        run("checkout", ["-C", str(source), "-c", "checkout.workers=1",
                         "checkout", "--detach", "FETCH_HEAD"], 60)
        if run("head", ["-C", str(source), "rev-parse", "HEAD"]).strip() != PIN:
            raise RuntimeError("checkout commit differs from the accepted pin")
        if run("tree", ["-C", str(source), "rev-parse", "HEAD^{tree}"]).strip() != TREE:
            raise RuntimeError("checkout tree differs from the primary API receipt")
        if run("status", ["-C", str(source), "status", "--porcelain", "--untracked-files=all"]):
            raise RuntimeError("upstream source checkout is dirty")
        run("connectivity", ["-C", str(source), "fsck", "--connectivity-only", "--no-reflogs"], 60)
        report["verified_inputs"] = []
        for name in ("CMakeLists.txt", "LICENSE.TXT"):
            retained = ROOT / "evidence/p2996-source/inputs/iwyu" / (name + ".source")
            actual = digest(source / name)
            if actual != digest(retained):
                raise RuntimeError(f"checkout differs from pinned HTTP input: {name}")
            report["verified_inputs"].append({"path": name, "sha256": actual})
        report["verified_files"] = []
        tree = run("blob-inventory", ["-C", str(source), "ls-tree", "-r", "--full-tree", "-z", "HEAD"])
        for entry in tree.rstrip("\0").split("\0"):
            info, name = entry.split("\t", 1)
            mode, kind, blob = info.split()
            path = source / name
            if kind != "blob" or mode not in ("100644", "100755", "120000"):
                raise RuntimeError(f"unexpected Git entry: {name}")
            data = os.readlink(path).encode() if mode == "120000" else path.read_bytes()
            actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if actual_blob != blob:
                raise RuntimeError(f"working tree bytes differ from Git blob: {name}")
            report["verified_files"].append({"path": name, "mode": mode, "blob": blob,
                                           "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        report["state"] = "PASS: exact IWYU source only; no configure, build or installation"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        save()
        print(json.dumps({"state": report["state"], "receipt": str(directory / "acquisition.json")}), flush=True)


if __name__ == "__main__":
    main()
