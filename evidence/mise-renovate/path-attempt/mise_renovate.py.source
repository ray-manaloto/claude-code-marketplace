"""Reattest observed mise metadata changes while retaining all compiler guards."""

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib

import mise_runtime as previous
from gcc_install import ROOT, census, digest, read
from mise_runtime import function, load

EVIDENCE = ROOT / "evidence/mise-renovate"
CONTRACT_SHA = "2c9e47eeccaf07e658b7258d6ec261a76fac7f9b5e29f491333c85349d79cdfa"
BASELINE = "evidence/p2996-registration/independent-registration/post-state.json"


def contract():
    assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
    data = load(EVIDENCE / "contract.json")
    for path, sha in data["inputs"].items():
        assert digest(ROOT / path) == sha, path
    return data


def overlay(baseline, data):
    """Replace two file records and the exact classified installation entries."""
    result = copy.deepcopy(baseline)
    assert set(data["global_updates"]) == {"config.toml", "mise.lock"}
    for name, change in data["global_updates"].items():
        old, new = change["previous"], change["current"]
        assert result["protected"]["global_files"][name] == old
        assert set(old) == set(new) == {"mode", "sha256"}
        assert old["mode"] == new["mode"] == "0o600" and old["sha256"] != new["sha256"]
        result["protected"]["global_files"][name] = copy.deepcopy(new)
    old_link = {"mode": "0o755", "link": "./44.149.3"}
    new_link = {"mode": "0o755", "link": "./44.150.1"}
    expected = {"npm-renovate/" + name: {"previous": old_link, "current": new_link}
                for name in ("44", "latest")}
    expected |= {"npm-renovate/44.150": {"previous": None, "current": new_link},
                 "npm-renovate/44.150.0": {"previous": None, "current": {"mode": "0o755", "link": None}},
                 "npm-renovate/44.150.1": {"previous": None, "current": {"mode": "0o755", "link": None}}}
    assert len(data["global_aliases"]) == 127
    for name, current in data["global_aliases"].items():
        parts, target = name.split("/"), current["link"]
        assert len(parts) == 2 and parts[1] == "global" and parts[0] in baseline["install_entries"]
        assert current["mode"] == "0o755" and target.startswith("./") and "/" not in target[2:]
        target_entry = parts[0] + "/" + target[2:]
        assert target_entry in baseline["install_entries"] or target_entry == "npm-renovate/44.150.1"
        expected[name] = {"previous": None, "current": current}
    assert data["install_updates"] == expected
    for name, change in expected.items():
        assert result["install_entries"].get(name) == change["previous"], name
        result["install_entries"][name] = copy.deepcopy(change["current"])
    return result


def semantic_check(data):
    """Check in memory; never persist or print the global configuration."""
    for name, change in data["global_updates"].items():
        old_path, new_path = Path(change["backup"]), Path.home() / ".config/mise" / name
        assert not old_path.is_symlink() and not new_path.is_symlink()
        assert digest(old_path) == change["previous"]["sha256"]
        assert digest(new_path) == change["current"]["sha256"]
        old, new = [tomllib.loads(path.read_text()) for path in (old_path, new_path)]
        if name == "config.toml":
            assert old["tools"]["npm:renovate"]["version"] == "44.149.3"
            old["tools"]["npm:renovate"]["version"] = "44.150.1"
        else:
            entries = old["tools"]["npm:renovate"]
            assert len(entries) == 1 and entries[0]["version"] == "44.149.3"
            assert entries[0]["specifiers"] == ["44.149.3"]
            entries[0].update(version="44.150.1", specifiers=["44.150.1"])
        assert old == new, name


def protected():
    data = contract()
    semantic_check(data)

    def accepted_load(path):
        value = load(path)
        return overlay(value, data) if path == ROOT / BASELINE else value

    return function(Path(previous.__file__), "protected", vars(previous) | {"load": accepted_load})()


def path_transition(value, old, new):
    parts = value.split(os.pathsep)
    assert old != new and parts.count(new) == 1
    prior = os.pathsep.join(old if part == new else part for part in parts)
    return {"path_sha256": hashlib.sha256(value.encode()).hexdigest(),
            "previous_path_sha256": hashlib.sha256(prior.encode()).hexdigest(), "replacements": 1}


def compare_profile(observed, expected, proof):
    assert proof == {"path_sha256": observed["path_sha256"],
                     "previous_path_sha256": expected["path_sha256"], "replacements": 1}
    assert observed | {"path_sha256": expected["path_sha256"]} == expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    foundation = Path.home() / ".local/state/marketplace-tool-foundation"
    if not directory.is_absolute() or directory != directory.resolve() or directory.parent != foundation:
        parser.error("use a new normalized directory directly under the private foundation root")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    report = {"state": "running", "helper_sha256": digest(Path(__file__)),
              "contract_sha256": CONTRACT_SHA, "commands": []}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "MISE_TASK_RUN_AUTO_INSTALL": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        data = contract()
        review, admission = [load(EVIDENCE / name) for name in ("pre-run-review.json", "admission.json")]
        assert review["result"].startswith("PASS") and not review["findings"]
        assert review["helper_sha256"] == admission["helper_sha256"] == report["helper_sha256"]
        assert review["contract_sha256"] == admission["contract_sha256"] == CONTRACT_SHA
        assert admission["review_sha256"] == digest(EVIDENCE / "pre-run-review.json")
        assert admission["run_directory"] == str(directory)
        assert sys.executable == data["python"]
        report["admission_sha256"] = digest(EVIDENCE / "admission.json")
        current = protected()
        report["writer_census_before"] = census()
        run = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                       globals() | {"directory": directory, "report": report, "env": env, "save": save})
        assert run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip() == data["base_head"]
        inherited = previous.contract()
        assert run("version", [current["path"], "--version"]).strip() == current["version"]
        probe = "import json,os,sys;print(json.dumps({k:os.environ.get(k) for k in sys.argv[1:]}))"
        path_probe = ("import json,os,sys;sys.path.insert(0," + repr(str(Path(__file__).parent))
                      + ");from mise_renovate import path_transition;"
                      "print(json.dumps(path_transition(os.environ['PATH'],sys.argv[1],sys.argv[2])))")
        report["path_transitions"] = {}
        for lane, expected in inherited["profiles"].items():
            for key in ("MARKETPLACE_P2996_PREFIX", "MARKETPLACE_GCC16_PREFIX"):
                env.pop(key, None)
            if lane == "p2996":
                env["MARKETPLACE_P2996_PREFIX"] = inherited["p2996_prefix"]
            if lane == "gcc16":
                env["MARKETPLACE_GCC16_PREFIX"] = load(ROOT / expected)["selected"]["MARKETPLACE_GCC16_PREFIX"]
            base = [current["path"], "--no-hooks", "-C", directory / "cwd"]
            if lane != "default":
                base += ["-E", lane]
            base += ["exec", "--fresh-env", "--no-deps", "--"]
            observed = run(lane + "-profile", base + normal_argv[-2:])
            proof = json.loads(run(lane + "-path-transition", base + [sys.executable, "-B", "-c", path_probe,
                               data["path_transition"]["previous"], data["path_transition"]["current"]]))
            compare_profile(json.loads(observed), load(ROOT / expected), proof)
            report["path_transitions"][lane] = proof
            if lane == "default":
                default_view = observed
            isolated = run(lane + "-isolation", base + [sys.executable, "-B", "-c", probe, *inherited["isolation_keys"]])
            assert all((directory / (lane + suffix + ".stderr")).read_text() == ""
                       for suffix in ("-profile", "-path-transition", "-isolation"))
            expected_isolation = {key: json.loads(observed)["selected"].get(key) for key in inherited["isolation_keys"]}
            assert json.loads(isolated) == expected_isolation, lane
            if lane != "default":
                assert expected_isolation == dict.fromkeys(inherited["isolation_keys"]), lane
        env.pop("MARKETPLACE_P2996_PREFIX", None)
        env.pop("MARKETPLACE_GCC16_PREFIX", None)
        assert run("default-after", normal_argv) == default_view
        report["writer_census_after"] = census()
        report["state"] = "PASS: observed mise metadata and existing profile parity; shared state unchanged"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            assert digest(Path(__file__)) == report["helper_sha256"]
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
