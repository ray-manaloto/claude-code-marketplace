"""Qualify native mise's read-only GCC plan against captured public metadata."""
import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence/gcc-bootstrap"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main(args):
    args.run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
    records = []
    for name in ("source-acquisition.json", "closure-acquisition.json"):
        receipt = json.loads((EVIDENCE / name).read_text())
        assert receipt["state"] == "PASS"
        records.extend(receipt["records"])
    snapshots = {}
    for record in records:
        if record["url"].startswith("https://formulae.brew.sh/api/formula/"):
            data = (ROOT / record["path"]).read_bytes()
            assert digest(data) == record["sha256"], record["path"]
            snapshots[record["url"].removeprefix("https://formulae.brew.sh")] = data
    assert len(snapshots) == 8
    assert json.loads(snapshots["/api/formula/gcc.json"])["versions"]["stable"] == "16.2.0"
    report = {"state": "running", "commands": [], "requests": [],
              "snapshot_sha256": {path: digest(data) for path, data in snapshots.items()},
              "script_sha256": digest(Path(__file__).read_bytes())}
    omitted = set()

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass

        def do_GET(self):
            self.respond(body=True)

        def do_HEAD(self):
            self.respond(body=False)

        def respond(self, body):
            data = snapshots.get(self.path) if self.path not in omitted else None
            status = 200 if data is not None else 404
            report["requests"].append({"path": self.path, "status": status})
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if body:
                self.wfile.write(data if data is not None else b"{}")

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for name in ("cwd", "system", "state", "data"):
            (args.run_dir / name).mkdir(mode=0o700)
        config = args.run_dir / "config.toml"
        config.write_text('[bootstrap.packages]\n"brew:gcc" = "latest"\n'
                          '[settings.url_replacements]\n"https://formulae.brew.sh/api" = '
                          f'"http://127.0.0.1:{server.server_port}/api"\n')
        environment = {key: os.environ[key] for key in ("HOME", "USER", "LOGNAME", "TMPDIR") if key in os.environ}
        environment.update({"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "NO_COLOR": "1",
                            "MISE_CONFIG_DIR": str(args.run_dir), "MISE_GLOBAL_CONFIG_FILE": str(config),
                            "MISE_SYSTEM_CONFIG_DIR": str(args.run_dir / "system"),
                            "MISE_SYSTEM_CONFIG_FILE": str(args.run_dir / "system/absent.toml"),
                            "MISE_CEILING_PATHS": str(args.run_dir / "cwd"),
                            "MISE_TRUSTED_CONFIG_PATHS": str(args.run_dir),
                            "MISE_STATE_DIR": str(args.run_dir / "state"), "MISE_DATA_DIR": str(args.run_dir / "data"),
                            "MISE_JOBS": "1", "MISE_AUTO_ENV": "0", "MISE_AUTO_INSTALL": "0"})
        base = [str(args.mise), "--no-hooks", "-C", str(args.run_dir / "cwd")]
        version = subprocess.run(base + ["version"], env=environment, text=True, capture_output=True, timeout=15)
        assert version.returncode == 0 and version.stdout.startswith("2026.10.7 ")
        report["native_version"] = version.stdout.strip()
        reference = json.loads((EVIDENCE / "native-dry-run.json").read_text())
        assert reference["state"] == "PASS"
        expected = next(row["stdout"] for row in reference["commands"] if row["case"] == "native-plan")
        for label, expected_rc in (("frozen-plan", 0), ("missing-metadata", 1)):
            if label == "missing-metadata":
                omitted.add("/api/formula/gcc.json")
            cache = args.run_dir / (label + "-cache")
            cache.mkdir(mode=0o700)
            env = dict(environment, MISE_CACHE_DIR=str(cache))
            start = len(report["requests"])
            command = base + ["bootstrap", "packages", "apply", "--manager", "brew", "--dry-run"]
            result = subprocess.run(command, env=env, text=True, capture_output=True, timeout=45)
            requests = report["requests"][start:]
            report["commands"].append({"case": label, "argv": command, "returncode": result.returncode,
                                       "stdout": result.stdout, "stderr": result.stderr, "requests": requests})
            assert result.returncode == expected_rc, (label, result.stderr)
            if label == "frozen-plan":
                assert set(result.stdout.splitlines()) == set(expected.splitlines())
                assert {r["path"] for r in requests} == snapshots.keys()
                assert all(r["status"] == 200 for r in requests)
            else:
                assert any(r == {"path": "/api/formula/gcc.json", "status": 404} for r in requests)
                assert "pour " not in result.stdout and "build " not in result.stdout
        report.update({"state": "PASS", "all_metadata_served_from_verified_snapshots": True,
                       "missing_metadata_failed_closed": True, "install_or_compiler_executed": False})
    except Exception as error:
        report.update({"state": "FAIL", "error": repr(error)})
        raise
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        report["loopback_server_stopped"] = not thread.is_alive()
        (args.run_dir / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"state": report["state"], "receipt": str(args.run_dir / "qualification.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mise", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    main(parser.parse_args())
