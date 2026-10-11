"""Acquire the accepted LLVM fork into a new private directory; never build it."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess

PIN = "f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e"
TREE = "9899759f9004a7df8442ec57000a17e53e6ad5f6"
REMOTE = "https://github.com/bloomberg/clang-p2996.git"
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
                      "fetch", "--depth=1", "--no-tags", "--no-recurse-submodules", "origin", PIN], 600)
        run("checkout", ["-C", str(source), "-c", "checkout.workers=1",
                         "checkout", "--detach", "FETCH_HEAD"], 180)
        if run("head", ["-C", str(source), "rev-parse", "HEAD"]).strip() != PIN:
            raise RuntimeError("checkout commit differs from the accepted pin")
        if run("tree", ["-C", str(source), "rev-parse", "HEAD^{tree}"]).strip() != TREE:
            raise RuntimeError("checkout tree differs from the primary API receipt")
        if run("status", ["-C", str(source), "status", "--porcelain", "--untracked-files=all"]):
            raise RuntimeError("upstream source checkout is dirty")
        run("connectivity", ["-C", str(source), "fsck", "--connectivity-only", "--no-reflogs"], 180)
        report["verified_inputs"] = []
        inputs = ROOT / "evidence/p2996-source/inputs"
        for path in sorted(inputs.rglob("*.source")):
            name = str(path.relative_to(inputs)).removesuffix(".source")
            if name.startswith("iwyu/"):
                continue
            actual = digest(source / name)
            if actual != digest(path):
                raise RuntimeError(f"checkout differs from pinned HTTP input: {name}")
            report["verified_inputs"].append({"path": name, "sha256": actual})
        report["state"] = "PASS: exact LLVM source only; no configure, build or installation"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        save()
        print(json.dumps({"state": report["state"], "receipt": str(directory / "acquisition.json")}), flush=True)


if __name__ == "__main__":
    main()
