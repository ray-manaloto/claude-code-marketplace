"""Qualify bounded IWYU reflection advice, its restricted fixer and native rebuild."""

import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time
from types import SimpleNamespace

from gcc_install import ROOT, digest, read
from mise_runtime import function, load, protected
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory

EVIDENCE = ROOT / "evidence/iwyu-reflection"
CONTRACT_SHA = "77208a22af95e9ade5ab5301e9dffa83d200366e998b4db5e8ab0ecbf67b6bcf"


def recommendations(text, source):
    """Accept only the declared direct-header edit, retaining the reflection header."""
    assert not re.search(r": (?:fatal )?error:", text)
    pattern = (re.escape(str(source)) + r" should add these lines:\n(.*?)\n"
               + re.escape(str(source)) + r" should remove these lines:\n(.*?)\n"
               + r"The full include-list for " + re.escape(str(source)) + r":\n(.*?)\n---")
    matches = re.findall(pattern, text, re.S)
    assert len(matches) == 1 and "warning:" in text
    sections = [[re.sub(r"\s*//.*", "", line).strip() for line in part.splitlines() if line.strip()]
                for part in matches[0]]
    assert sections[:2] == [['#include "value.h"'], ['- #include "indirect.h"']]
    assert sorted(sections[2]) == sorted(['#include <meta>', '#include "value.h"'])
    assert text.count("should add these lines:") == text.count("should remove these lines:") == 1
    return sections


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
    report = {"state": "running", "helper_sha256": digest(Path(__file__)), "commands": []}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "MISE_TASK_RUN_AUTO_INSTALL": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}

    def run(label, argv, timeout=60, descriptor=None, expected=0, stdin=None, cwd=None):
        assert label not in [row["case"] for row in report["commands"]]
        with stdin.open("rb") if stdin else nullcontext(None) as handle:
            def popen(command, **kwargs):
                kwargs.update(stdin=handle if handle else subprocess.DEVNULL, cwd=cwd or directory)
                report["commands"][-1].update(cwd=str(kwargs["cwd"]), expected_returncode=expected,
                                              timeout_seconds=timeout, stdin=None if stdin is None else
                                              {"path": str(stdin), "sha256": digest(stdin)})
                save()
                return subprocess.Popen(command, **kwargs)
            scope["subprocess"] = SimpleNamespace(Popen=popen, DEVNULL=subprocess.DEVNULL,
                                                   TimeoutExpired=subprocess.TimeoutExpired)
            count = len(report["commands"])
            try:
                result = native(label, argv, timeout=timeout, descriptor=descriptor)
            except AssertionError:
                assert expected != 0 and len(report["commands"]) == count + 1
                assert report["commands"][-1]["case"] == label and report["commands"][-1]["returncode"] == expected
                return (directory / (label + ".stdout")).read_text()
            assert expected == 0, "expected nonzero result unexpectedly passed"
            return result

    def guard():
        assert digest(EVIDENCE / "contract.json") == CONTRACT_SHA
        data = load(EVIDENCE / "contract.json")
        assert all(digest(ROOT / p) == sha for p, sha in data["inputs"].items())
        recipe = load(EVIDENCE / "source-recipe.json")
        assert all(digest(Path(r["path"])) == r["sha256"] for r in recipe["prerequisites"] + recipe["source_bindings"])
        current = protected()
        built = load(ROOT / "evidence/iwyu-build/operation/qualification.json")
        assert prefix_inventory(Path(built["installed"]["prefix"])) == built["installed"]["inventory"]
        bootstrap = load(ROOT / "evidence/iwyu-source/native-prerequisite.json")["bootstrap"]
        assert digest(Path(bootstrap["sdk"]["path"]) / "SDKSettings.json") == bootstrap["sdk"]["settings_sha256"]
        assert digest(Path(__file__)) == report["helper_sha256"] and digest(LOCK_MODULE) == LOCK_SHA
        return data, recipe, current

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        contract, recipe, current = guard()
        admission, review = [load(EVIDENCE / name) for name in ("admission.json", "pre-run-review.json")]
        assert admission["helper_sha256"] == review["helper_sha256"] == report["helper_sha256"]
        assert admission["contract_sha256"] == review["contract_sha256"] == CONTRACT_SHA
        assert admission["review_sha256"] == digest(EVIDENCE / "pre-run-review.json")
        assert review["result"].startswith("PASS") and not review["findings"]
        assert admission["run_directory"] == str(directory)
        report["admission_sha256"] = digest(EVIDENCE / "admission.json")
        runtime_review = load(ROOT / "evidence/mise-runtime/runtime-review.json")
        assert runtime_review["result"].startswith("PASS") and not runtime_review["findings"]
        assert runtime_review["current_mise"] == current
        native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run", scope)
        assert run("project-head", ["/usr/bin/git", "-C", ROOT, "rev-parse", "HEAD"]).strip() == contract["base_head"]
        normal = run("default-before", normal_argv)
        assert normal == (ROOT / "evidence/mise-runtime/operation/default-after.stdout").read_text()
        base = [current["path"], "--no-hooks", "-C", directory / "cwd", "-E", "cpp-build", "exec", "--fresh-env", "--no-deps", "--"]
        assert run("named-profile", base + normal_argv[-2:]) == (ROOT / "evidence/mise-runtime/operation/cpp-build-profile.stdout").read_text()
        acquired, registered = ROOT / "evidence/iwyu-source", ROOT / "evidence/p2996-registration"
        acquisition = load(acquired / "operation/acquisition.json")
        source = Path(acquisition["source"])
        source_modes = load(acquired / "independent-review/source-before.json")
        configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
        source_state = function(Path(__file__).with_name("iwyu_build.py"), "source_state", globals() | locals())
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-iwyu-reflection", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            active = [line for line in processes.splitlines() if re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use", Path(line.split(maxsplit=2)[-1]).name)]
            report["capacity"] = {"active": active, "load": os.getloadavg(), "cpus": os.cpu_count(),
                                  "free_bytes": shutil.disk_usage(directory).free,
                                  "total_cpu_percent": sum(float(line.split()[1]) for line in processes.splitlines())}
            assert not active and report["capacity"]["free_bytes"] >= contract["disk_reserve_bytes"]
            assert os.getloadavg()[0] <= 2 * os.cpu_count() and report["capacity"]["total_cpu_percent"] <= 75 * os.cpu_count()
            docker = "/Applications/Docker.app/Contents/Resources/bin/docker"
            assert run("docker-context", [docker, "context", "show"], timeout=15).strip() == admission["docker_context"]
            assert run("docker-census", [docker, "ps", "--format", "{{.ID}}\t{{.Image}}"], timeout=15).splitlines() == admission["containers"]
            stats = run("docker-stats", [docker, "stats", "--no-stream", "--format", "{{json .}}"], timeout=20)
            report["capacity"]["container_cpu_percent"] = sum(float(json.loads(line)["CPUPerc"].rstrip("%")) for line in stats.splitlines())
            assert report["capacity"]["container_cpu_percent"] <= 50 * os.cpu_count()
            guard()
            source_state("before")
            fixture = directory / "fixtures/reflection"
            fixture.mkdir(parents=True)
            data = recipe["reflection_fixture"]
            for row in data["files"]:
                path = fixture / row["path"]
                path.write_text(row["content"])
                assert digest(path) == row["sha256"]
            report["fixture_before"] = prefix_inventory(fixture)
            main_file = fixture / "main.cc"
            expand = lambda argv: [s.replace("<private-09c-root>", str(directory)) for s in argv]
            build = expand(data["rebuild_and_reanalyze"]["build_argv"])
            build[-1] = str(fixture / "baseline")
            run("baseline-build", base + build, descriptor=fd)
            assert run("baseline-run", base + [build[-1]], descriptor=fd) == ""
            analyze = expand(data["analyze_argv"])
            run("advice", base + analyze, descriptor=fd, expected=23)
            report["recommendations"] = recommendations((directory / "advice.stderr").read_text(), main_file)
            before_fix = prefix_inventory(fixture)
            fixer_base = list(base)
            fixer_base[fixer_base.index("-C") + 1] = fixture
            fixed = run("fixer", fixer_base + expand(data["fixer"]["argv"]), descriptor=fd,
                        stdin=directory / "advice.stderr", cwd=fixture)
            assert "ERROR" not in fixed + (directory / "fixer.stderr").read_text()
            assert fixed.count("IWYU edited 1 files on your behalf.") == 1
            assert main_file.read_text() == data["fixer"]["expected_after"]
            assert digest(main_file) == data["fixer"]["expected_after_sha256"]
            after_fix = prefix_inventory(fixture)
            assert [r for r in before_fix if r["path"] != "main.cc"] == [r for r in after_fix if r["path"] != "main.cc"]
            report["fixture_after_fix"] = after_fix
            build[-1] = str(fixture / "fixed")
            run("fixed-build", base + build, descriptor=fd)
            assert run("fixed-run", base + [build[-1]], descriptor=fd) == ""
            run("clean-analysis", base + analyze, descriptor=fd)
            clean = (directory / "clean-analysis.stderr").read_text()
            assert clean.strip() == "(" + str(main_file) + " has correct #includes/fwd-decls)"
            negative = [s for s in analyze if s != "-freflection"]
            run("missing-reflection", base + negative, descriptor=fd, expected=1)
            assert re.search(r": (?:fatal )?error:", (directory / "missing-reflection.stderr").read_text())
            assert main_file.read_text() == data["fixer"]["expected_after"]
            report["final_fixture"] = prefix_inventory(fixture)
        report["lease_released"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: bounded type-reflection advice, restricted fixer, rebuild/run and clean analysis"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            guard()
            if "source_state" in locals():
                source_state("after")
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
