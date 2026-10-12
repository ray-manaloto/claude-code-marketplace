"""Prepare exact ASan promotion guards without changing historical inventories."""

import copy
import os
from pathlib import Path
import re
import stat

import mise_renovate as previous
from gcc_install import ROOT, digest
from mise_runtime import function, load

EVIDENCE = ROOT / "evidence/p2996-asan-runtime"
CONTRACT_SHA = "af5c4bab941b296e953b8b9d3a9018efbc3560957de5667c2c4a7f4559ee771d"
RUNTIME = "lib/clang/21/lib/darwin/libclang_rt.asan_osx_dynamic.dylib"
ARTIFACTS = "evidence/p2996-install/independent-installation/post-install-inventory.json"
PREFIX = "evidence/p2996-install/operation/prefix-inventory.json"


def validate(data):
    assert data["target"] == str(Path(data["prefix"]) / RUNTIME)
    assert data["artifact_inventory"] == ARTIFACTS and data["prefix_inventory"] == PREFIX
    old, member, new = data["previous_record"], data["previous_prefix_record"], data["current_asan"]
    assert old["path"] == old["resolved_path"] == data["target"]
    assert old["lexists"] and old["exists"] and old.get("symlink_target") is None
    assert old["lstat_mode"] == old["mode"] == member["mode"] == new["mode"] == "0o755"
    assert member["path"] == RUNTIME and member["kind"] == "file"
    assert set(new) == {"sha256", "bytes", "mode"}
    for key in ("sha256", "bytes"):
        assert old[key] == member[key] and new[key] == data["qualified_replacement"][key]
        assert new[key] != old[key]
    assert re.fullmatch(r"[a-f0-9]{64}", new["sha256"]) and type(new["bytes"]) is int and new["bytes"] > 0


def contract():
    assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
    data = load(EVIDENCE / "contract.json")
    for path, sha in data["inputs"].items():
        assert digest(ROOT / path) == sha, path
    validate(data)
    repair = ROOT / "evidence/p2996-sanitizer-repair"
    review, qualified = [load(repair / name) for name in ("artifact-review.json", "operation/qualification.json")]
    assert review["result"].startswith("PASS") and not review["findings"]
    assert qualified["state"].startswith("PASS") and qualified["protected_state_unchanged"] and qualified["lease_released"]
    assert review["qualification_sha256"] == digest(repair / "operation/qualification.json")
    assert review["artifact_inventory_sha256"] == digest(repair / "artifact-inventory.json")
    rows = [row for row in load(repair / "artifact-inventory.json")["artifacts"] if row["kind"] == "patched-runtime"]
    assert rows == [data["qualified_replacement"]]
    assert qualified["repair"]["patched"]["sha256"] == data["current_asan"]["sha256"]
    return data


def overlay(path, value, data):
    """Update exactly one row in each of two in-memory historical inventories."""
    if path not in (ROOT / ARTIFACTS, ROOT / PREFIX):
        return value
    validate(data)
    result = copy.deepcopy(value)
    if path == ROOT / ARTIFACTS:
        rows = [row for row in result["records"]
                if row["path"] == data["target"] or row.get("resolved_path") == data["target"]]
        old = data["previous_record"]
    else:
        rows = [row for row in result if row["path"] == RUNTIME]
        old = data["previous_prefix_record"]
    assert rows == [old]
    rows[0].update(sha256=data["current_asan"]["sha256"], bytes=data["current_asan"]["bytes"])
    assert {key for key in old if rows[0][key] != old[key]} == {"sha256", "bytes"}
    return result


def protected():
    """Require the promoted digest while retaining the entire previous guard chain."""
    data = contract()
    assert identity(Path(data["target"])) == data["current_asan"]

    def accepted_load(path):
        return overlay(path, load(path), data)

    return function(Path(previous.__file__), "protected", vars(previous) | {"load": accepted_load})()


def identity(path):
    assert path.is_absolute() and path == path.resolve(strict=True)
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.geteuid()
    return {"sha256": digest(path), "bytes": info.st_size, "mode": oct(stat.S_IMODE(info.st_mode))}


def replace_exact(staged, destination, before, after):
    """Atomically replace one regular file, after exact source/destination checks."""
    assert set(before) == set(after) == {"sha256", "bytes", "mode"}
    assert before["mode"] == after["mode"] == "0o755" and before["sha256"] != after["sha256"]
    assert staged != destination and staged.stat().st_dev == destination.stat().st_dev
    assert identity(staged) == after and identity(destination) == before
    os.replace(staged, destination)
    assert identity(destination) == after
