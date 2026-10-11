"""Recheck the reviewed GCC plan; --apply admits its four native bottle pours."""
import argparse
from datetime import datetime, timezone
import http.server
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import threading

from gcc_bottles import EVIDENCE, PACKAGES, PREFIX, ROOT, digest, preimage

if not __debug__:
    raise RuntimeError("Run without Python optimization; admission assertions are required")


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def package_state(name):
    rack = PREFIX / "Cellar" / name
    return {"versions": {p.name: {"receipt_sha256": digest(p / "INSTALL_RECEIPT.json")}
                         for p in rack.iterdir() if p.is_dir()} if rack.exists() else {},
            "links": {part: os.readlink(p) if p.is_symlink() else None
                      for part in ("opt", "var/homebrew/linked")
                      for p in [PREFIX / part / name]}}


def preserved(before, installed=False):
    for name, row in before["global_files"].items():
        path = Path.home() / ".config/mise" / name
        assert not path.is_symlink() and digest(path) == row["sha256"], path
        assert oct(path.stat().st_mode & 0o777) == row["mode"], path
    for name, state in before["packages"].items():
        if not installed or name not in PACKAGES:
            assert package_state(name) == state, name
    for path, row in before["glib_files"].items():
        assert digest(Path(path)) == row["sha256"], path


def preflight(manifest, before):
    preserved(before)
    for section in ("parent_preimages", "control_preimages"):
        for path, expected in manifest[section].items():
            assert preimage(Path(path)) == expected, path
    for path, row in manifest["prefix_writes"].items():
        assert row["preimage"] == {"kind": "absent"} and preimage(Path(path)) == row["preimage"], path
    for row in manifest["materializations"].values():
        assert preimage(Path(row["staging"])) == row["staging_preimage"]
        for child in row["preserved_children"].values():
            assert preimage(Path(child["source"])) == child["state"]


def census():
    result = subprocess.run(["/bin/ps", "-axo", "pid=,ppid=,comm="], text=True,
                            capture_output=True, check=True, timeout=15)
    rows = []
    for line in result.stdout.splitlines():
        pid, ppid, executable = line.strip().split(None, 2)
        name = Path(executable).name
        if name not in {"mise", "brew", "ruby"}:
            continue
        row = {"pid": int(pid), "ppid": int(ppid), "executable": executable}
        args = subprocess.run(["/bin/ps", "-p", pid, "-o", "args="], text=True,
                              capture_output=True, check=True, timeout=10).stdout
        tokens = args.split()
        row["known_task"] = next((task for task in ("mcp:graphify", "mcp:cbm", "mcp:lab-results")
                                  if tokens[1:] == ["run", "-q", task]), None)
        rows.append(row)
        assert name == "mise" and row["known_task"], row
        assert Path(tokens[0]).name == "mise", row
    locks = subprocess.run(["/usr/sbin/lsof", "-t", "+D", str(PREFIX / "var/homebrew/locks")],
                           text=True, capture_output=True, timeout=15)
    assert locks.returncode in (0, 1) and not locks.stdout.strip() and not locks.stderr.strip()
    return {"at": datetime.now(timezone.utc).isoformat(), "processes": rows,
            "lock_holder_check_rc": locks.returncode, "lock_holders": []}


def main(args):
    os.umask(0o077)
    args.run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    report = {"state": "running", "script_sha256": digest(Path(__file__)),
              "apply_requested": args.apply, "commands": [], "requests": []}
    server = thread = None

    def save():
        (args.run_dir / "installation.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(label, command, environment, timeout=45):
        row = {"case": label, "argv": command, "started_at": datetime.now(timezone.utc).isoformat()}
        report["commands"].append(row)
        save()
        paths = [args.run_dir / (label + suffix) for suffix in (".stdout", ".stderr")]
        with paths[0].open("wb") as out, paths[1].open("wb") as err:
            process = subprocess.Popen(command, env=environment, cwd=args.run_dir,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                rc = process.wait(timeout=timeout)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                row["interrupted"] = True
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()
                raise
            finally:
                row.update({"returncode": process.returncode, "logs": [
                    {"path": str(p), "sha256": digest(p)} for p in paths]})
                save()
        print(json.dumps({"case": label, "returncode": rc}), flush=True)
        assert rc == 0, label
        return paths[0].read_text()

    try:
        manifest, before, proposal = read("bottles.json"), read("install-preimages.json"), read("install-proposal.json")
        review = read("bottle-review.json")
        assert review["result"] == "PASS for task 05b preparation only"
        for row in review["reviewed_inputs"]:
            if row["path"].startswith("evidence/") or row["path"].endswith("gcc_bottles.py"):
                assert digest(ROOT / row["path"]) == row["sha256"], row["path"]
        for row in proposal["evidence_receipts"]:
            assert digest(EVIDENCE / row["path"]) == row["sha256"], row["path"]
        mise = proposal["native_mise"]["path"]
        assert digest(Path(mise)) == proposal["native_mise"]["sha256"]
        snapshots = {}
        for name in ("source-acquisition.json", "closure-acquisition.json"):
            for row in read(name)["records"]:
                if row["url"].startswith("https://formulae.brew.sh/api/formula/"):
                    path = ROOT / row["path"]
                    assert digest(path) == row["sha256"]
                    snapshots[row["url"].removeprefix("https://formulae.brew.sh")] = path.read_bytes()
        assert len(snapshots) == 8
        preflight(manifest, before)
        for name in ("cwd", "system", "state", "data", "cache/system-brew/bottles"):
            (args.run_dir / name).mkdir(parents=True, mode=0o700)
        for row in proposal["bottles"]:
            source = Path(row["archive"])
            assert digest(source) == row["sha256"] and source.stat().st_size == row["bytes"]
            destination = args.run_dir / "cache/system-brew/bottles" / source.name
            shutil.copyfile(source, destination)
            assert digest(destination) == row["sha256"]

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *unused):
                pass

            def do_HEAD(self):
                report["requests"].append({"path": self.path, "status": 404})
                self.send_response(404)
                self.end_headers()

            def do_GET(self):
                data = snapshots.get(self.path)
                status = 200 if data is not None else 404
                report["requests"].append({"path": self.path, "status": status})
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data if data is not None else b"{}")

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config = args.run_dir / "config.toml"
        endpoint = f"http://127.0.0.1:{server.server_port}"
        config.write_text('[bootstrap.packages]\n"brew:gcc" = "latest"\n[settings.url_replacements]\n'
                          f'"https://formulae.brew.sh/api" = "{endpoint}/api"\n'
                          f'"https://ghcr.io" = "{endpoint}/blocked"\n'
                          f'"https://github.com" = "{endpoint}/blocked"\n')
        env = {key: os.environ[key] for key in ("HOME", "USER", "LOGNAME", "TMPDIR") if key in os.environ}
        env.update({"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "NO_COLOR": "1", "MISE_JOBS": "1",
                    "MISE_CONFIG_DIR": str(args.run_dir), "MISE_GLOBAL_CONFIG_FILE": str(config),
                    "MISE_SYSTEM_CONFIG_DIR": str(args.run_dir / "system"),
                    "MISE_SYSTEM_CONFIG_FILE": str(args.run_dir / "system/absent.toml"),
                    "MISE_CEILING_PATHS": str(args.run_dir / "cwd"),
                    "MISE_TRUSTED_CONFIG_PATHS": str(args.run_dir),
                    "MISE_STATE_DIR": str(args.run_dir / "state"), "MISE_DATA_DIR": str(args.run_dir / "data"),
                    "MISE_CACHE_DIR": str(args.run_dir / "cache"), "MISE_AUTO_ENV": "0",
                    "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0"})
        base = [mise, "--no-hooks", "-C", str(args.run_dir / "cwd")]
        assert run("version", base + ["version"], env).startswith("2026.10.7 ")
        apply = base + ["bootstrap", "packages", "apply", "--manager", "brew"]
        planned = run("captured-plan", apply + ["--dry-run"], env)
        expected = next(row["stdout"] for row in read("native-dry-run.json")["commands"] if row["case"] == "native-plan")
        assert set(planned.splitlines()) == set(expected.splitlines())
        assert {row["path"] for row in report["requests"]} == snapshots.keys()
        assert all(row["status"] == 200 for row in report["requests"])
        context_path = Path(before["normal_environment"]["argv"][-1]).parent / "context.json"
        context = json.loads(context_path.read_text())
        report["normal_context_sha256"] = digest(context_path)
        normal_env = context["environment"] | {"MISE_OFFLINE": "1"}
        normal = run("default-before", before["normal_environment"]["argv"], normal_env)
        assert json.loads(normal) == before["normal_environment"]["output"]
        preflight(manifest, before)
        report["census"] = census()
        report["admission"] = {"owner": "/root", "authority": proposal["authority"],
                               "scope": "Four reviewed native bottle pours; two reviewed directory materializations",
                               "preflight_passed_at": datetime.now(timezone.utc).isoformat()}
        save()
        if args.apply:
            run("native-apply", apply, env, timeout=600)
            preserved(before, installed=True)
            report["installed_packages"] = {name: package_state(name) for name in PACKAGES}
            for name, version in PACKAGES.items():
                state = report["installed_packages"][name]
                assert set(state["versions"]) == {version}, name
                receipt = json.loads((PREFIX / "Cellar" / name / version / "INSTALL_RECEIPT.json").read_text())
                assert receipt["source"]["versions"]["stable"] == version and receipt["poured_from_bottle"]
                assert receipt["arch"] == "arm64" and receipt["installed_on_request"] == (name == "gcc")
            for path, row in manifest["prefix_writes"].items():
                p = Path(path)
                assert p.is_symlink() and os.path.normpath(p.parent / os.readlink(p)) == row["target"], path
            for path, row in manifest["materializations"].items():
                p = Path(path)
                assert p.is_dir() and not p.is_symlink()
                assert preimage(Path(row["staging"])) == {"kind": "absent"}
                for child, state in row["preserved_children"].items():
                    if str(p / child) not in manifest["materializations"]:
                        assert (p / child).is_symlink() and (p / child).resolve() == Path(state["source"])
            after = run("default-after", before["normal_environment"]["argv"], normal_env)
            assert json.loads(after) == json.loads(normal)
            assert all(row["status"] == 200 and row["path"] in snapshots for row in report["requests"])
        report["state"] = "PASS: installed" if args.apply else "PASS: preparation only"
    except BaseException as error:
        report.update({"state": "FAIL", "error": repr(error)})
        if any(row["case"] == "native-apply" for row in report["commands"]):
            observed = report["partial_state"] = {}
            paths = set(manifest["prefix_writes"]) | set(manifest["control_preimages"])
            paths.update(manifest["materializations"])
            paths.update(row["staging"] for row in manifest["materializations"].values())
            for name, version in PACKAGES.items():
                paths.update(str(PREFIX / "Cellar" / name / suffix)
                             for suffix in ("", version, version + "/INSTALL_RECEIPT.json"))
            for path in sorted(paths):
                try:
                    observed[path] = preimage(Path(path))
                except Exception as observation_error:
                    observed[path] = {"observation_error": repr(observation_error)}
        raise
    finally:
        if server:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        report["loopback_server_stopped"] = thread is None or not thread.is_alive()
        save()
        print(json.dumps({"state": report["state"], "receipt": str(args.run_dir / "installation.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="Perform the admitted native pours after all guards")
    main(parser.parse_args())
