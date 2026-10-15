"""Qualify a small generated matrix without configuring or building a project."""
import argparse
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
CONFIGS = ("Debug", "Release", "RelWithDebInfo", "MinSizeRel")
TUPLES = (("p2996", "none"), ("p2996", "tsan"), ("gcc16", "none"))
COMMIT = "f532db0b25843aaad0dd6c481923c6840425485b"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inspect_matrix(doc):
    assert doc["version"] == 12 and "installPresets" not in doc
    groups = {}
    for kind in ("configure", "build", "test", "workflow"):
        rows = doc[kind + "Presets"]
        groups[kind] = {row["name"]: row for row in rows}
        assert len(rows) == len(groups[kind]), (kind, "duplicate names")
    concrete = {n for n, row in groups["configure"].items() if not row.get("hidden")}
    assert concrete == {f"configure-{c}-{s}" for c, s in TUPLES}
    base = groups["configure"]["trial-common"]
    assert base["generator"] == "Ninja Multi-Config"
    assert base["cacheVariables"]["CMAKE_CONFIGURATION_TYPES"] == ";".join(CONFIGS)
    assert base["binaryDir"] == "${sourceDir}/build/${presetName}"
    assert base["installDir"] == "${sourceDir}/install/${presetName}"
    assert all("CMAKE_BUILD_TYPE" not in p.get("cacheVariables", {}) for p in groups["configure"].values())
    for kind in ("build", "test"):
        assert set(groups[kind]) == {f"{kind}-{cfg}-{c}-{s}" for cfg in CONFIGS for c, s in TUPLES}
    assert set(groups["workflow"]) == {f"workflow-{c}-{s}" for c, s in TUPLES}
    for compiler, mode in TUPLES:
        name = f"configure-{compiler}-{mode}"
        assert groups["configure"][name]["inherits"] == ["trial-common", f"configure-compiler-{compiler}", f"configure-instrumentation-{mode}"]
        assert groups["configure"][f"configure-compiler-{compiler}"]["cacheVariables"]["MARKETPLACE_TRIAL_COMPILER"] == compiler
        assert groups["configure"][f"configure-instrumentation-{mode}"]["cacheVariables"]["MARKETPLACE_TRIAL_INSTRUMENTATION"] == mode
        steps = [{"type": "configure", "name": name}]
        for cfg in CONFIGS:
            for kind in ("build", "test"):
                child = groups[kind][f"{kind}-{cfg}-{compiler}-{mode}"]
                assert child["configuration"] == cfg and child["configurePreset"] == name
                steps.append({"type": kind, "name": child["name"]})
        workflow = groups["workflow"][f"workflow-{compiler}-{mode}"]
        assert workflow["steps"] == steps and not ({"inherits", "condition"} & workflow.keys())
    return groups


def main(args):
    args.run_dir.mkdir(parents=True, exist_ok=False)
    report = {"state": "running", "commands": [], "run_directory": str(args.run_dir)}
    template = HERE / "CMakePresetsVendorTemplate.json"

    def run(label, argv, expected=0):
        result = subprocess.run([str(x) for x in argv], text=True, capture_output=True, timeout=30)
        report["commands"].append({"case": label, "argv": [str(x) for x in argv], "returncode": result.returncode,
                                   "stdout_sha256": digest(result.stdout.encode()), "stderr": result.stderr,
                                   "stdout": None if label.startswith("generate") else result.stdout})
        assert result.returncode == expected, (label, result.returncode, result.stderr)
        return result.stdout.encode()

    try:
        direct = json.loads(importlib.metadata.distribution("tcpm").read_text("direct_url.json"))
        assert direct["vcs_info"]["commit_id"] == COMMIT
        assert b"4.4.4" in run("cmake-version", [args.cmake, "--version"])
        assert b"0.3.3" in run("tcpm-version", [args.tcpm, "--version"])
        generated = []
        for index in (1, 2):
            directory = args.run_dir / f"generation-{index}"
            directory.mkdir()
            data = run(f"generate-{index}", [args.tcpm, "--non-interactive", "--no-schema-validation", "--presets-version", "12",
                                            "--template-file", template, "--presets-file", directory / "CMakePresets.json", "--stdout"])
            (directory / "CMakePresets.json").write_bytes(data)
            generated.append(data)
        assert generated[0] == generated[1], "non-deterministic generation"
        document = json.loads(generated[0])
        groups = inspect_matrix(document)
        for kind in groups:
            output = run("native-" + kind, [args.cmake, "-S", args.run_dir / "generation-1", "--list-presets=" + kind])
            names = set(re.findall(r'^\s+"([^"]+)"', output.decode(), re.MULTILINE))
            assert names == {n for n, row in groups[kind].items() if not row.get("hidden")}, kind
        for label in ("workflow-inherits", "workflow-crosses-tree"):
            invalid = copy.deepcopy(document)
            if label == "workflow-inherits":
                invalid["workflowPresets"][0]["inherits"] = "workflow-gcc16-none"
            else:
                invalid["workflowPresets"][0]["steps"][1]["name"] = "build-Debug-gcc16-none"
            directory = args.run_dir / label
            directory.mkdir()
            (directory / "CMakePresets.json").write_text(json.dumps(invalid))
            run(label, [args.cmake, "-S", directory, "--list-presets=all"], expected=1)
        excluded = copy.deepcopy(document)
        excluded["configurePresets"].append({"name": "configure-gcc16-tsan", "inherits": "trial-common"})
        try:
            inspect_matrix(excluded)
        except AssertionError:
            report["excluded_tuple_control_rejected"] = True
        else:
            raise AssertionError("excluded tuple accepted")
        target = HERE / "CMakePresets.json"
        if args.update:
            target.write_bytes(generated[0])
        else:
            assert target.read_bytes() == generated[0], "checked-in preset drift"
        report.update({"state": "PASS", "template_sha256": digest(template.read_bytes()), "generated_sha256": digest(generated[0]),
                       "script_sha256": digest(Path(__file__).read_bytes()), "source_commit": COMMIT, "two_generations_identical": True,
                       "configure_tuples": TUPLES, "configurations": CONFIGS, "build_test_cells": 12, "native_kinds": list(groups),
                       "compiler_or_configure_or_build_executed": False, "updated_project_output": args.update})
    except Exception as error:
        report.update({"state": "FAIL", "error": repr(error)})
        raise
    finally:
        (args.run_dir / "qualification.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"state": report["state"], "receipt": str(args.run_dir / "qualification.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cmake", type=Path, required=True)
    parser.add_argument("--tcpm", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--update", action="store_true", help="Update the project JSON only after all checks pass")
    main(parser.parse_args())
