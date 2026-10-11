from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import time

ROOT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
DIRECTORY = Path(__file__).parent
EVIDENCE = ROOT / "evidence/vcpkg-abi-inputs"
CM = Path("/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/bin/cmake")
COMMON = ROOT / "triplets/common/macos-arm64.cmake"
ENTRY = "/opt/homebrew/bin/pkg-config"
EXPECTED_CMAKE = "80cbc0d5ee08c9e6166bcc44bf51faf5469e360346f5cefbf36e8f8e4351a4cb"
PREFIXES = {"gcc16": "/opt/homebrew/Cellar/gcc/16.2.0", "p2996": "/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-configure-20261011T051205Z/prefix"}
LOAD = lambda p: json.loads(p.read_text())
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
package = LOAD(ROOT / "evidence/pkgconf-install/qualified-package-inputs.json")
source = LOAD(EVIDENCE / "source-bindings.json")
common_sha = SHA(COMMON)
old_logs = {"gcc16": ROOT / "evidence/vcpkg-gcc16-triplets/script-controls/static-extraction.stdout",
            "p2996": ROOT / "evidence/vcpkg-p2996-triplets/corrected-controls/static-extracted-triplet.stdout"}
old_paths = {lane: [line.removeprefix("-- ABI=").split("|")[0] for line in p.read_text().splitlines() if line.startswith("-- ABI=")]
             for lane, p in old_logs.items()}
assert all(old_paths.values())

def guard():
    assert SHA(CM) == EXPECTED_CMAKE and SHA(COMMON) == common_sha
    assert all(SHA(Path(row["path"])) == row["sha256"] for row in source["source_files"])
    assert all(SHA(ROOT / p) == sha for p, sha in source["receipts"].items())
    for p, row in package["files"].items():
        assert SHA(Path(p)) == row["sha256"] and str(Path(p).resolve()) == row["resolved"]
    assert os.readlink(ENTRY) == package["pkg_config_link"]["target"]
    assert str(Path(ENTRY).resolve()) == package["pkg_config_link"]["resolved"]

report = {"state": "running", "started_at": datetime.now(timezone.utc).isoformat(),
          "helper_sha256": SHA(Path(__file__)), "common_sha256": common_sha,
          "cmake": {"path": str(CM), "sha256": EXPECTED_CMAKE}, "commands": [],
          "prior_abi_lists": {lane: {"path": str(p), "sha256": SHA(p), "inputs": old_paths[lane]} for lane, p in old_logs.items()},
          "scope": "CMake script evaluation only; no project configuration, compiler, dependency, pkg-config execution, network or shared write"}
cases = [(lane + "-" + link, lane, link, "", ENTRY, 0) for lane in PREFIXES for link in ("static", "dynamic")]
cases[1] = (*cases[1][:3], 'set(PKGCONFIG "' + ENTRY + '")\n', ENTRY, 0)
cases[2] = (*cases[2][:3], 'set(PKGCONFIG "' + ENTRY + '" CACHE INTERNAL "")\n', ENTRY, 0)
cases.extend([
    ("missing-environment", "gcc16", "static", "", None, 1),
    ("wrong-environment", "gcc16", "static", "", "/invalid/pkg-config", 1),
    ("conflicting-variable", "p2996", "dynamic", 'set(PKGCONFIG "/invalid/pkg-config")\n', ENTRY, 1),
    ("conflicting-shadowed-cache", "p2996", "static", 'set(PKGCONFIG "/invalid/pkg-config" CACHE INTERNAL "")\nset(PKGCONFIG "' + ENTRY + '")\n', ENTRY, 1),
])
try:
    guard()
    for case, lane, linkage, setup, selection, expected in cases:
        triplet = ROOT / ("triplets/arm64-osx-" + lane + "-" + linkage + ".cmake")
        text = 'cmake_minimum_required(VERSION 4.4)\n' + setup + 'include("' + str(triplet) + '")\n'
        text += '''set(before "${VCPKG_HASH_ADDITIONAL_FILES}")
set(before_env "${VCPKG_ENV_PASSTHROUGH}")
'''
        text += 'include("' + str(triplet) + '")\n'
        text += '''if(NOT before STREQUAL VCPKG_HASH_ADDITIONAL_FILES OR NOT before_env STREQUAL VCPKG_ENV_PASSTHROUGH OR DEFINED VCPKG_BUILD_TYPE)
  message(FATAL_ERROR "Reentry changed ABI inputs or both dependency configurations")
endif()
message(STATUS "ABI_LIST=${VCPKG_HASH_ADDITIONAL_FILES}")
message(STATUS "TRACKED_ENV=${VCPKG_ENV_PASSTHROUGH}")
message(STATUS "OPTIONS=${VCPKG_CMAKE_CONFIGURE_OPTIONS}")
message(STATUS "LINKAGE=${VCPKG_LIBRARY_LINKAGE}")
'''
        for p in package["files"]:
            text += 'file(SHA256 "' + p + '" digest)\nmessage(STATUS "PKGCONF_HASH=' + p + '|${digest}")\n'
        text += 'message(STATUS "PKGCONF_ABI_PASS:' + case + '")\n'
        script = DIRECTORY / (case + ".cmake"); script.write_text(text)
        env = {"HOME": str(Path.home()), "PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C", "LC_ALL": "C",
               "TMPDIR": str(DIRECTORY), "MARKETPLACE_CPP_LANE": lane, "MARKETPLACE_" + lane.upper() + "_PREFIX": PREFIXES[lane]}
        if selection is not None:
            env["PKG_CONFIG"] = selection
        argv = [str(CM), "-P", str(script)]; start = time.monotonic()
        process = subprocess.run(argv, text=True, capture_output=True, cwd=DIRECTORY, env=env, timeout=20)
        logs = []
        for suffix, content in (("stdout", process.stdout), ("stderr", process.stderr)):
            path = DIRECTORY / (case + "." + suffix); path.write_text(content); logs.append({"path": str(path), "sha256": SHA(path)})
        row = {"case": case, "argv": argv, "environment": env, "script_sha256": SHA(script), "returncode": process.returncode,
               "expected_returncode": expected, "elapsed_seconds": time.monotonic()-start, "logs": logs}
        report["commands"].append(row)
        assert process.returncode == expected, case
        if expected == 0:
            lines = dict(line[3:].split("=", 1) for line in process.stdout.splitlines() if line.startswith("-- ") and "=" in line and not line.startswith("-- PKGCONF_HASH="))
            observed = lines["ABI_LIST"].split(";")
            assert len(observed) == len(set(observed)) == len(old_paths[lane]) + 2
            assert set(observed) == set(old_paths[lane]) | set(package["files"])
            assert lines["TRACKED_ENV"] == "MARKETPLACE_CPP_LANE;MARKETPLACE_" + lane.upper() + "_PREFIX;PKG_CONFIG"
            assert lines["OPTIONS"] == "-DCMAKE_POLICY_DEFAULT_CMP0210=NEW;-DFMT_MODULE=OFF" and lines["LINKAGE"] == linkage
            hashes = dict(line.removeprefix("-- PKGCONF_HASH=").split("|", 1) for line in process.stdout.splitlines() if line.startswith("-- PKGCONF_HASH="))
            assert hashes == {p: data["sha256"] for p, data in package["files"].items()}
            assert "PKGCONF_ABI_PASS:" + case in process.stdout
            row.update(preserved_abi_inputs=len(old_paths[lane]), total_abi_inputs=len(observed), pkgconf_hashes=hashes)
        else:
            assert "Use the qualified pkgconf entry through PKG_CONFIG" in process.stderr
            assert "PKGCONF_ABI_PASS" not in process.stdout
        row["state"] = "PASS"
    guard()
    report.update(state="PASS", bound_inputs_unchanged=True, qualified_package_unchanged=True)
except BaseException as error:
    report.update(state="FAIL", error=repr(error)); raise
finally:
    (DIRECTORY / "controls.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"state": report["state"], "commands": len(report["commands"]), "receipt": str(DIRECTORY / "controls.json")}), flush=True)
