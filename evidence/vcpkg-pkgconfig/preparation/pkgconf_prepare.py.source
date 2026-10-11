"""Inspect one pinned pkgconf bottle and capture a native mise dry-run only."""

import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import signal
import subprocess
import tarfile
import threading

from gcc_bottles import BOOTSTRAP_DIRS, LINK_DIRS, PREFIX, ROOT, digest, preimage
from gcc_install import census
from mise_renovate import protected
from mise_runtime import load

EVIDENCE = ROOT / "evidence/vcpkg-pkgconfig"
CONTRACT_SHA = "cfaebae853596cd3dcc82b788c79db2271b363ad3e7c11fc6872bc766fa39ea3"


def inspect(archive, version):
    report = {"members": [], "prefix_writes": {}, "parent_preimages": {}, "materializations": {}}
    package = PurePosixPath("pkgconf") / version
    seen = set()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            assert path.is_relative_to(package) and ".." not in path.parts and not path.is_absolute()
            assert member.name not in seen and (member.isdir() or member.isfile() or member.issym())
            seen.add(member.name)
            if member.issym():
                target = PurePosixPath(posixpath.normpath(str(path.parent / member.linkname)))
                assert not PurePosixPath(member.linkname).is_absolute() and target.is_relative_to(package)
            row = {"path": member.name, "type": member.type.decode(), "mode": oct(member.mode),
                   "size": member.size, "linkname": member.linkname}
            if member.isfile():
                row["sha256"] = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
            report["members"].append(row)
            if not member.isdir() and len(path.parts) >= 3 and path.parts[2] in LINK_DIRS:
                dest = PREFIX.joinpath(*path.parts[2:])
                report["prefix_writes"][str(dest)] = {"target": str(PREFIX / "Cellar" / path),
                                                       "preimage": preimage(dest)}
    for part in ("opt", "var/homebrew/linked"):
        dest = PREFIX / part / "pkgconf"
        report["prefix_writes"][str(dest)] = {"target": str(PREFIX / "Cellar" / package),
                                               "preimage": preimage(dest)}
    assert all(row["preimage"] == {"kind": "absent"} for row in report["prefix_writes"].values())
    controls = [PREFIX, *(PREFIX / name for name in BOOTSTRAP_DIRS), PREFIX / "Cellar/pkgconf",
                PREFIX / "Cellar/pkgconf/.mise-staging.lock", PREFIX / "var/homebrew/locks/mise-bootstrap.lock"]
    report["control_preimages"] = {str(p): preimage(p) for p in controls}
    assert report["control_preimages"][str(PREFIX / "Cellar/pkgconf")] == {"kind": "absent"}
    for path in [*(Path(p) for p in report["prefix_writes"]), *controls]:
        for parent in path.parents:
            if not parent.is_relative_to(PREFIX):
                break
            report["parent_preimages"][str(parent)] = preimage(parent)
    links = [Path(p) for p, row in report["parent_preimages"].items() if row["kind"] == "symlink"]
    for link in links:
        for path in (Path(p) for p in report["prefix_writes"]):
            if not path.is_relative_to(link):
                continue
            for parent in reversed(path.parents):
                if not parent.is_relative_to(link):
                    continue
                if not parent.is_dir():
                    break
                target = parent.resolve(strict=True)
                assert target.is_relative_to(PREFIX / "Cellar")
                staging = parent.parent / (".mise-materialize-" + parent.name)
                assert preimage(staging) == {"kind": "absent"}
                report["materializations"][str(parent)] = {
                    "source_directory": str(target), "before": preimage(parent),
                    "staging": str(staging), "staging_preimage": preimage(staging),
                    "preserved_children": {child.name: {"source": str(child), "state": preimage(child)}
                                           for child in sorted(target.iterdir())}}
    report["additional_native_writes"] = ["/opt/homebrew/Cellar/pkgconf/.mise-staging.lock",
        "/opt/homebrew/Cellar/pkgconf/.mise-extract-3.0.8-<random>/", "/opt/homebrew/Cellar/pkgconf/3.0.8/",
        "/opt/homebrew/var/homebrew/locks/mise-bootstrap.lock", "Missing listed parent directories",
        "Listed directory materializations", "Private mise state, data and cache"]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    foundation = Path.home() / ".local/state/marketplace-tool-foundation"
    if not directory.is_absolute() or directory != directory.resolve() or directory.parent != foundation:
        parser.error("use a new normalized directory directly below the private foundation root")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    report = {"state": "running", "helper_sha256": digest(Path(__file__)), "commands": [], "requests": []}
    server = thread = None

    def save():
        (directory / "preparation.json").write_text(json.dumps(report, indent=2) + "\n")

    def guard():
        assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
        contract = load(EVIDENCE / "contract.json")
        assert all(digest(ROOT / p) == sha for p, sha in contract["inputs"].items())
        assert digest(Path(contract["current_mise"]["path"])) == contract["current_mise"]["sha256"]
        assert digest(Path(contract["python"])) == contract["python_sha256"]
        assert digest(Path(__file__)) == report["helper_sha256"]
        return contract, protected()

    def run(label, argv, env, expected=0):
        row = {"case": label, "argv": [str(p) for p in argv], "expected": expected, "timeout_seconds": 45}
        report["commands"].append(row)
        save()
        paths = [directory / (label + "." + suffix) for suffix in ("stdout", "stderr")]
        with paths[0].open("wb") as out, paths[1].open("wb") as err:
            process = subprocess.Popen(row["argv"], env=env, cwd=directory / "cwd",
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                process.wait(timeout=45)
            except BaseException:
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
                raise
            finally:
                row.update(returncode=process.returncode, logs={p.name: digest(p) for p in paths})
                save()
        assert process.returncode == expected, label
        return paths[0].read_text()

    try:
        contract, current = guard()
        assert current == contract["current_mise"]
        formula = load(ROOT / contract["formula"])
        assert formula["name"] == "pkgconf" and formula["versions"]["stable"] == contract["version"]
        assert formula["revision"] == 0 and not formula["dependencies"] and not formula["keg_only"]
        bottle = formula["bottle"]["stable"]["files"]["arm64_tahoe"]
        archive = Path(contract["archive"])
        assert digest(archive) == bottle["sha256"]
        report["bottle"] = {"path": str(archive), "sha256": bottle["sha256"], "bytes": archive.stat().st_size}
        report["manifest"] = inspect(archive, contract["version"])
        report["census_before"] = census()
        for name in ("cwd", "system", "state", "data", "cache"):
            (directory / name).mkdir()
        snapshot = (ROOT / contract["formula"]).read_bytes()
        enabled = True

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *unused):
                pass

            def do_GET(self):
                body = snapshot if enabled and self.path == "/api/formula/pkgconf.json" else b"{}"
                status = 200 if body is snapshot else 404
                report["requests"].append({"path": self.path, "status": status})
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(body)

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        endpoint = "http://127.0.0.1:" + str(server.server_port)
        config = directory / "config.toml"
        config.write_text('[bootstrap.packages]\n"brew:pkgconf" = "latest"\n[settings.url_replacements]\n'
            f'"https://formulae.brew.sh/api" = "{endpoint}/api"\n'
            f'"https://ghcr.io" = "{endpoint}/blocked"\n"https://github.com" = "{endpoint}/blocked"\n')
        env = {k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "TMPDIR") if k in os.environ}
        env.update({"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "NO_COLOR": "1", "MISE_JOBS": "1",
            "MISE_CONFIG_DIR": str(directory), "MISE_GLOBAL_CONFIG_FILE": str(config),
            "MISE_SYSTEM_CONFIG_DIR": str(directory / "system"),
            "MISE_SYSTEM_CONFIG_FILE": str(directory / "system/absent.toml"),
            "MISE_CEILING_PATHS": str(directory / "cwd"), "MISE_TRUSTED_CONFIG_PATHS": str(directory),
            "MISE_STATE_DIR": str(directory / "state"), "MISE_DATA_DIR": str(directory / "data"),
            "MISE_CACHE_DIR": str(directory / "cache"), "MISE_AUTO_ENV": "0", "MISE_AUTO_INSTALL": "0",
            "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0"})
        base = [current["path"], "--no-hooks", "-C", directory / "cwd"]
        assert run("version", base + ["version"], env).strip() == current["version"]
        help_text = run("apply-help", base + ["bootstrap", "packages", "apply", "--help"], env)
        assert "--manager" in help_text and "--dry-run" in help_text
        argv = base + ["bootstrap", "packages", "apply", "--manager", "brew", "--dry-run"]
        assert run("captured-plan", argv, env) == "pour pkgconf/3.0.8 (requested)\n"
        assert report["requests"] and all(r == {"path": "/api/formula/pkgconf.json", "status": 200}
                                          for r in report["requests"])
        enabled = False
        run("missing-metadata", argv, env, expected=1)
        assert "404 Not Found" in (directory / "missing-metadata.stderr").read_text()
        assert report["manifest"] == inspect(archive, contract["version"])
        report.update(state="PASS: native preparation only", prefix_preimages_unchanged=True,
                      archive_extracted=False, installation_executed=False)
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        if server:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        report["loopback_server_stopped"] = thread is None or not thread.is_alive()
        try:
            guard()
            report["census_after"] = census()
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "preparation.json")}), flush=True)


if __name__ == "__main__":
    main()
