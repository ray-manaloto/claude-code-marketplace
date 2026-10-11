"""Install the reviewed pkgconf bottle with exact prefix and shared-state guards."""

import argparse
from datetime import datetime, timezone
import hashlib
import http.server
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
import threading
import time

from gcc_bottles import PREFIX, ROOT, digest, preimage
from gcc_install import census, read
from mise_renovate import protected
from mise_runtime import function, load
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from pkgconf_prepare import inspect

EVIDENCE = ROOT / "evidence/pkgconf-install"
CONTRACT_SHA = "59235e19a0ad51c6e7ca1470fd13540119a42e87ea663e9c66ae8a9cce904d51"


def children(directory):
    return {p.name: preimage(p) for p in sorted(directory.iterdir())}


def validate_macho(path, rule):
    data = path.read_bytes()
    end = rule["signature_offset"]
    assert 0 < end < len(data)
    canonical, values = bytearray(data[:end]), {}
    assert set(rule["masked_fields"]) == {"linkedit_vmsize", "linkedit_filesize", "signature_size"}
    for name, field in rule["masked_fields"].items():
        offset, width = field["offset"], field["width"]
        assert width == (4 if name == "signature_size" else 8) and 0 <= offset < offset + width <= end
        values[name] = int.from_bytes(data[offset:offset + width], "little")
        canonical[offset:offset + width] = bytes(width)
    assert hashlib.sha256(canonical).hexdigest() == rule["canonical_prefix_sha256"]
    assert values["signature_size"] > 0 and end + values["signature_size"] == len(data)
    assert rule["linkedit_fileoff"] + values["linkedit_filesize"] == len(data)
    assert values["linkedit_vmsize"] >= values["linkedit_filesize"]
    return values | {"file_bytes": len(data)}


def validate_prefix(manifest, before, installed):
    states = manifest["parent_preimages"] | manifest["control_preimages"]
    additions = {p for p, row in states.items() if row["kind"] == "absent"}
    additions.update(manifest["prefix_writes"])
    for path, expected in before.items():
        current = children(Path(path))
        allowed = {Path(p).name for p in additions if Path(p).parent == Path(path)} if installed else set()
        assert set(current) == set(expected) | allowed, path
        assert all(current[name] == row for name, row in expected.items()), path
    for path, expected in states.items():
        if expected["kind"] != "absent" or not installed:
            assert preimage(Path(path)) == expected, path
        elif path.endswith(".mise-staging.lock"):
            assert preimage(Path(path)) == {"kind": "file", "sha256": digest(Path("/dev/null"))}
        else:
            assert Path(path).is_dir() and not Path(path).is_symlink(), path
            assert Path(path).stat().st_uid == os.getuid(), path
    for path, row in manifest["prefix_writes"].items():
        p = Path(path)
        if installed:
            assert p.is_symlink() and os.readlink(p) == os.path.relpath(row["target"], p.parent), path
        else:
            assert preimage(p) == row["preimage"] == {"kind": "absent"}, path


def validate_keg(manifest, contract):
    keg = PREFIX / "Cellar/pkgconf/3.0.8"
    observed = {r["path"]: r for r in prefix_inventory(keg)}
    expected = {str(Path(r["path"]).relative_to("pkgconf/3.0.8")): r for r in manifest["members"]}
    root = expected.pop(".")
    assert root["type"] == "5" and keg.is_dir() and not keg.is_symlink()
    assert oct(keg.stat().st_mode & 0o777) == root["mode"]
    assert set(observed) == set(expected) | {"INSTALL_RECEIPT.json"}
    for path, row in expected.items():
        actual = observed[path]
        assert actual["mode"] == row["mode"] or row["type"] == "2", path
        assert actual["kind"] == {"0": "file", "2": "symlink", "5": "directory"}[row["type"]], path
        if row["type"] == "2":
            assert actual["target"] == row["linkname"], path
        elif row["type"] == "0" and path not in contract["changed_files"]:
            assert actual["sha256"] == row["sha256"], path
        elif row["type"] == "0":
            assert actual["sha256"] != row["sha256"], path
            if path in contract["text_postimages"]:
                assert actual["sha256"] == contract["text_postimages"][path], path
    receipt = load(keg / "INSTALL_RECEIPT.json")
    assert sorted(receipt["changed_files"]) == sorted(contract["changed_files"])
    assert all(receipt[key] == value for key, value in contract["receipt_required"].items())
    assert set(receipt) == set(contract["receipt_required"]) | {"time", "changed_files"}
    assert isinstance(receipt["time"], int) and receipt["time"] > 0
    assert set(p.name for p in keg.parent.iterdir()) == {"3.0.8", ".mise-staging.lock"}
    return observed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--install", action="store_true", required=True)
    directory = parser.parse_args().run_dir
    foundation = Path.home() / ".local/state/marketplace-tool-foundation"
    if not directory.is_absolute() or directory != directory.resolve() or directory.parent != foundation:
        parser.error("use a new normalized directory directly below the private foundation root")
    assert __debug__, "admission assertions require unoptimized Python"
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    report = {"state": "running", "helper_sha256": digest(Path(__file__)), "commands": [], "requests": []}
    server = thread = None
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "MISE_TASK_RUN_AUTO_INSTALL": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
    normal_env = env.copy()

    def save():
        (directory / "installation.json").write_text(json.dumps(report, indent=2) + "\n")

    def guard():
        assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
        contract = load(EVIDENCE / "contract.json")
        assert all(digest(ROOT / p) == sha for p, sha in contract["inputs"].items())
        assert all(digest(Path(p)) == sha for p, sha in contract["tools"].items())
        assert sys.executable in contract["tools"] and digest(LOCK_MODULE) == LOCK_SHA
        assert digest(Path(__file__)) == report["helper_sha256"]
        return contract, protected()

    run = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                   globals() | {"directory": directory, "report": report, "env": env, "save": save})

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        contract, current = guard()
        admission, review = [load(EVIDENCE / p) for p in ("admission.json", "pre-run-review.json")]
        assert admission["helper_sha256"] == review["helper_sha256"] == report["helper_sha256"]
        assert admission["contract_sha256"] == review["contract_sha256"] == CONTRACT_SHA
        assert review["result"].startswith("PASS") and not review["findings"]
        assert admission["review_sha256"] == digest(EVIDENCE / "pre-run-review.json")
        assert admission["run_directory"] == str(directory)
        report["admission_sha256"] = digest(EVIDENCE / "admission.json")
        assert run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip() == contract["base_head"]
        normal = run("default-before", normal_argv)
        assert normal == (ROOT / contract["default_profile"]).read_text()
        report["writer_census_before"] = census()
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-pkgconf-install", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            active = [line for line in processes.splitlines() if re.fullmatch(
                r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use|vcpkg",
                Path(line.split(maxsplit=2)[-1]).name)]
            report["capacity"] = {"active": active, "load": os.getloadavg(), "cpus": os.cpu_count(),
                "free_bytes": shutil.disk_usage(directory).free,
                "total_cpu_percent": sum(float(line.split()[1]) for line in processes.splitlines())}
            assert not active and report["capacity"]["free_bytes"] >= 8 * 1024**3
            assert os.getloadavg()[0] <= 2 * os.cpu_count() and report["capacity"]["total_cpu_percent"] <= 75 * os.cpu_count()
            docker = "/Applications/Docker.app/Contents/Resources/bin/docker"
            assert run("docker-context", [docker, "context", "show"], timeout=15).strip() == admission["docker_context"]
            assert run("docker-census", [docker, "ps", "--format", "{{.ID}}\t{{.Image}}"], timeout=15).splitlines() == admission["containers"]
            stats = run("docker-stats", [docker, "stats", "--no-stream", "--format", "{{json .}}"], timeout=20)
            report["capacity"]["container_cpu_percent"] = sum(float(json.loads(l)["CPUPerc"].rstrip("%")) for l in stats.splitlines())
            assert report["capacity"]["container_cpu_percent"] <= 50 * os.cpu_count()
            prep = load(ROOT / contract["preparation"])
            manifest, archive = prep["manifest"], Path(prep["bottle"]["path"])
            assert digest(archive) == prep["bottle"]["sha256"] and not manifest["materializations"]
            assert inspect(archive, "3.0.8") == manifest
            validate_prefix(manifest, contract["parent_children"], False)
            for name in ("cwd", "system", "state", "data", "cache/system-brew/bottles", "pc"):
                (directory / name).mkdir(parents=True)
            cached = directory / "cache/system-brew/bottles/pkgconf-3.0.8.tar.gz"
            shutil.copyfile(archive, cached)
            assert digest(cached) == prep["bottle"]["sha256"]
            snapshot = (ROOT / contract["formula"]).read_bytes()

            class Handler(http.server.BaseHTTPRequestHandler):
                def log_message(self, *unused):
                    pass

                def do_GET(self):
                    body = snapshot if self.path == "/api/formula/pkgconf.json" else b"{}"
                    status = 200 if body is snapshot else 404
                    report["requests"].append({"path": self.path, "status": status})
                    self.send_response(status)
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
            env.clear()
            env.update({k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "TMPDIR") if k in os.environ})
            env.update({"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "NO_COLOR": "1", "MISE_JOBS": "1",
                "MISE_CONFIG_DIR": str(directory), "MISE_GLOBAL_CONFIG_FILE": str(config),
                "MISE_SYSTEM_CONFIG_DIR": str(directory / "system"), "MISE_SYSTEM_CONFIG_FILE": str(directory / "system/absent.toml"),
                "MISE_CEILING_PATHS": str(directory), "MISE_TRUSTED_CONFIG_PATHS": str(directory),
                "MISE_STATE_DIR": str(directory / "state"), "MISE_DATA_DIR": str(directory / "data"),
                "MISE_CACHE_DIR": str(directory / "cache"), "MISE_AUTO_ENV": "0", "MISE_AUTO_INSTALL": "0",
                "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0"})
            base = [current["path"], "--no-hooks", "-C", directory / "cwd"]
            assert run("version", base + ["version"]).strip() == current["version"]
            apply = base + ["bootstrap", "packages", "apply", "--manager", "brew"]
            assert run("captured-plan", apply + ["--dry-run"], descriptor=fd) == "pour pkgconf/3.0.8 (requested)\n"
            guard()
            validate_prefix(manifest, contract["parent_children"], False)
            report["writer_census_immediate"] = census()
            run("native-apply", apply, timeout=90, descriptor=fd)
            report["keg_inventory"] = validate_keg(manifest, contract)
            validate_prefix(manifest, contract["parent_children"], True)
            report["new_parents"] = {p: preimage(Path(p)) for p, row in manifest["parent_preimages"].items() if row["kind"] == "absent"}
            exe = PREFIX / "bin/pkg-config"
            assert exe.resolve() == PREFIX / "Cellar/pkgconf/3.0.8/bin/pkgconf"
            for path in contract["macho_files"]:
                binary = PREFIX / "Cellar/pkgconf/3.0.8" / path
                label = Path(path).name
                report.setdefault("macho_postimages", {})[path] = validate_macho(binary, contract["macho_files"][path])
                assert run(label + "-arch", ["/usr/bin/lipo", "-archs", binary], descriptor=fd).strip() == "arm64"
                run(label + "-signature", ["/usr/bin/codesign", "--verify", "--strict", binary], descriptor=fd)
                deps = run(label + "-libraries", ["/usr/bin/otool", "-L", binary], descriptor=fd).splitlines()[1:]
                assert {line.strip().split()[0] for line in deps} == set(contract["runtime_libraries"][path])
            assert run("pkg-config-version", [exe, "--version"], descriptor=fd).strip() == "3.0.8"
            (directory / "pc/witness.pc").write_text('Name: witness\nDescription: private fixture\nVersion: 1.2.3\nLibs: -lwitness\n')
            env.update(PKG_CONFIG_LIBDIR=str(directory / "pc"), PKG_CONFIG_PATH="")
            assert run("fixture-version", [exe, "--modversion", "witness"], descriptor=fd).strip() == "1.2.3"
            assert run("fixture-libs", [exe, "--libs", "witness"], descriptor=fd).strip() == "-lwitness"
            assert report["requests"] and all(r == {"path": "/api/formula/pkgconf.json", "status": 200} for r in report["requests"])
        report["lease_released"] = True
        env.clear()
        env.update(normal_env)
        assert run("default-after", normal_argv) == normal
        report["writer_census_after"] = census()
        report["state"] = "PASS: pkgconf installed and native lookup qualified"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        if any(r["case"] == "native-apply" for r in report["commands"]):
            report["partial_links"] = {p: preimage(Path(p)) for p in manifest["prefix_writes"]}
        raise
    finally:
        if server:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        report["loopback_server_stopped"] = thread is None or not thread.is_alive()
        try:
            guard()
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "installation.json")}), flush=True)


if __name__ == "__main__":
    main()
