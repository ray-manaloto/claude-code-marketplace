"""Compose the qualified ASan and TSan inventory guards for installed TSan."""

import copy
from pathlib import Path
import re

import mise_renovate as previous
import p2996_asan_runtime as asan
from gcc_install import ROOT, digest
from mise_runtime import function, load

EVIDENCE = ROOT / "evidence/p2996-tsan-runtime"
CONTRACT_SHA = "3e33503010361fe6d66d4906b3fa3b73c92fce8a191daab86cbc40cde5d7be36"
RUNTIME = "lib/clang/21/lib/darwin/libclang_rt.tsan_osx_dynamic.dylib"
ARTIFACTS = "evidence/p2996-install/independent-installation/post-install-inventory.json"
PREFIX = "evidence/p2996-install/operation/prefix-inventory.json"


def validate(data):
    assert data["target"] == str(Path(data["prefix"]) / RUNTIME)
    assert data["artifact_inventory"] == ARTIFACTS and data["prefix_inventory"] == PREFIX
    old, member, new = data["previous_record"], data["previous_prefix_record"], data["current_tsan"]
    assert old["path"] == old["resolved_path"] == data["target"]
    assert old["lexists"] and old["exists"] and old.get("symlink_target") is None
    assert old["lstat_mode"] == old["mode"] == member["mode"] == new["mode"] == "0o755"
    assert member["path"] == RUNTIME and member["kind"] == "file"
    assert set(new) == {"sha256", "bytes", "mode"}
    for key in ("sha256", "bytes"):
        assert old[key] == member[key]
        assert new[key] == data["qualified_replacement"][key]
        assert new[key] != old[key]
    assert re.fullmatch(r"[a-f0-9]{64}", new["sha256"])
    assert type(new["bytes"]) is int and new["bytes"] > 0


def contract():
    assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
    data = load(EVIDENCE / "contract.json")
    for path, sha in data["inputs"].items():
        assert digest(ROOT / path) == sha, path
    validate(data)
    asan.contract()
    repair = ROOT / "evidence/p2996-tsan-repair"
    review = load(repair / "artifact-review/review.json")
    qualification = load(repair / "operation/qualification.json")
    closure = load(repair / "operation/closure.json")
    assert review["result"].startswith("PASS") and not review["findings"]
    assert review["qualification_sha256"] == digest(repair / "operation/qualification.json")
    assert qualification["state"].startswith("PASS")
    assert qualification["protected_state_unchanged"] and qualification["lease_released"]
    assert closure["state"].startswith("PASS") and closure["native_returncode"] == 0
    assert closure["qualification_sha256"] == review["qualification_sha256"]
    rows = [row for row in load(repair / "artifact-inventory.json")["artifacts"]
            if row["kind"] == "patched-tsan-runtime"]
    assert rows == [data["qualified_replacement"]]
    assert qualification["repair"]["patched"]["sha256"] == data["current_tsan"]["sha256"]
    assert asan.identity(Path(rows[0]["path"])) == data["qualified_replacement_identity"]
    return data


def overlay(path, value, data):
    """Change only the TSan row of each in-memory historical inventory."""
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
    rows[0].update(sha256=data["current_tsan"]["sha256"], bytes=data["current_tsan"]["bytes"])
    assert {key for key in old if rows[0][key] != old[key]} == {"sha256", "bytes"}
    return result


def protected():
    """Require installed ASan and TSan while retaining the prior guard chain."""
    asan_data, data = asan.contract(), contract()
    assert asan.identity(Path(data["target"])) == data["current_tsan"]

    def accepted_load(path):
        value = asan.overlay(path, load(path), asan_data)
        return overlay(path, value, data)

    return function(Path(previous.__file__), "protected", vars(previous) | {"load": accepted_load})()


identity = asan.identity
replace_exact = asan.replace_exact
