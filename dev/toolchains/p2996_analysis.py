"""Qualify clang-tidy and the static analyzer with reflection and diagnostic controls."""

import argparse
import ast
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import plistlib
import shutil
import signal
import subprocess
import time

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import isolated, snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_install import prefix_inventory
from vcpkg_register import install_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    directory = parser.parse_args().run_dir
    load = lambda p: json.loads(p.read_text())
    evidence = ROOT / "evidence/p2996-analysis"
    registered = ROOT / "evidence/p2996-registration"
    installed = ROOT / "evidence/p2996-install"
    reflected = ROOT / "evidence/p2996-reflection"
    review = load(registered / "registration-review.json")
    registration = load(registered / "operation/qualification.json")
    runtime = load(reflected / "operation/qualification.json")
    inventory = load(installed / "independent-installation/post-install-inventory.json")
    baseline = load(registered / "independent-registration/post-state.json")
    configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
    prefix, workspace, source = map(Path, (inventory["prefix"], inventory["workspace"], configuration["source"]))
    forbidden = (ROOT, workspace, source, Path.home() / ".config", Path.home() / ".local/share/mise")
    if (not directory.is_absolute() or directory != directory.resolve()
            or any(directory.is_relative_to(p) for p in forbidden)):
        parser.error("use a new normalized private directory outside protected project, source, build and mise roots")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    (directory / "cwd").mkdir()
    witness = Path(__file__).with_name("p2996_reflection.cpp")
    report = {"state": "running", "commands": [], "helper_sha256": digest(Path(__file__)),
              "witness_sha256": digest(witness), "registration_review_sha256": digest(registered / "registration-review.json")}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    def function(path, name, sha, scope):
        assert digest(path) == sha
        node = next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
        return scope[name]

    run_scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    native = function(ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source", "run",
                      "7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f", run_scope)
    protected = function(Path(__file__).with_name("p2996_reflection.py"), "protected", runtime["helper_sha256"],
                         globals() | {"baseline": baseline, "inventory": inventory, "prefix": prefix,
                                      "evidence": installed, "load": load})

    def run(label, argv, timeout=45, descriptor=None, environment=None, expected=0):
        run_scope["env"] = env if environment is None else environment
        try:
            result = native(label, argv, timeout=timeout, descriptor=descriptor)
        except AssertionError:
            assert expected != 0 and report["commands"][-1]["case"] == label
            assert report["commands"][-1]["returncode"] == expected
            return (directory / (label + ".stdout")).read_text()
        assert expected == 0, "negative control unexpectedly passed"
        return result

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        admission = load(evidence / "admission.json")
        assert admission["helper_sha256"] == report["helper_sha256"] and admission["witness_sha256"] == report["witness_sha256"]
        assert admission["run_directory"] == str(directory) and admission["registration_review_sha256"] == report["registration_review_sha256"]
        assert report["registration_review_sha256"] == "c8a131ad9dfcd8657eb51c8ea19b7cbfba473d120aac29d848e198645edb526f"
        assert review["result"].startswith("PASS") and not review["findings"] and review["all_protected_state_unchanged"]
        assert digest(registered / "operation/qualification.json") == review["operation_sha256"]
        assert registration["state"].startswith("PASS") and registration["promoted"] and registration["protected_state_unchanged"]
        assert digest(registered / "independent-registration/post-state.json") == review["post_state"]["sha256"]
        assert digest(installed / "independent-installation/post-install-inventory.json") == review["retained_source_build_inventory"]["inventory_sha256"]
        assert digest(installed / "operation/prefix-inventory.json") == review["prefix_inventory"]["inventory_sha256"]
        assert all(digest(Path(p)) == sha for p, sha in registration["proposal"]["bindings"].items())
        assert all(digest(Path(__file__).with_name(n)) == sha for n, sha in registration["proposal"]["helpers"].items())
        assert digest(Path(__file__).with_name("p2996_register.py")) == review["helper_sha256"]
        assert report["witness_sha256"] == runtime["witness_sha256"] and prefix == Path(review["proposal"]["prefix"])
        report["admission_sha256"] = digest(evidence / "admission.json")
        contract = evidence / "source-contract.json"
        assert digest(contract) == admission["source_contract_sha256"] == "5e9d2c3932914f40da022e87bd89de50e23e9cc613e5c2f432cbfaa4f6be8297"
        assert all(digest(Path(r["path"])) == r["sha256"] for r in load(contract)["references"])
        prerequisite = ROOT / "evidence/p2996-tools/tools-review.json"
        assert digest(prerequisite) == "1721ce016ae695da8467f3e7f1caf5b5611bda6fac08a8cccbf76858031b7aa0"
        assert load(prerequisite)["result"].startswith("PASS") and not load(prerequisite)["findings"]
        report["source_contract_sha256"] = digest(contract)
        protected()
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]

        def source_state(stage):
            for label, arguments in (("head", ["rev-parse", "HEAD"]), ("tree", ["rev-parse", "HEAD^{tree}"]),
                                     ("status", ["status", "--porcelain", "--untracked-files=all"]),
                                     ("diff", ["diff", "--no-ext-diff", "--binary"])):
                run(stage + "-" + label, git + arguments)
                assert (directory / (stage + "-" + label + ".stdout")).read_bytes() == (registered / ("operation/source-after-" + label + ".stdout")).read_bytes()

        source_state("source-before")
        normal = run("default-before", normal_argv)
        assert normal == (registered / "operation/default-after.stdout").read_text()
        mise = configuration["mise"]
        assert digest(Path(mise["path"])) == mise["sha256"]
        stage = isolated(directory / "discovery") | {"MISE_INSTALLS_DIR": str(Path.home() / ".local/share/mise/installs")}
        located = run("native-where", [mise["path"], "--no-config", "--no-hooks", "--no-env", "-C", stage["MISE_CEILING_PATHS"],
                                      "where", review["proposal"]["tool"]], environment=stage).strip()
        assert Path(located).resolve() == prefix
        env["MARKETPLACE_P2996_PREFIX"] = str(prefix)
        base = [mise["path"], "--no-hooks", "-C", directory / "cwd", "-E", "p2996", "exec", "--fresh-env", "--no-deps", "--"]
        selected = json.loads(run("named-profile", base + normal_argv[-2:]))
        assert selected == runtime["selected_environment"]
        assert digest(Path(configuration["sdk"]["path"]) / "SDKSettings.json") == configuration["sdk"]["settings_sha256"]
        assert digest(LOCK_MODULE) == LOCK_SHA
        spec = importlib.util.spec_from_file_location("marketplace_host_lock", LOCK_MODULE)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
        assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
        with lease.held(lease.HEAVY_GATE, "marketplace-p2996-analysis", wait_s=0, out=io.StringIO()) as fd:
            assert fd is not None
            processes = run("capacity-processes", ["/bin/ps", "-axo", "pid=,pcpu=,comm="])
            assert not any(re.fullmatch(r"(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd",
                                       Path(line.split(maxsplit=2)[-1]).name) for line in processes.splitlines())
            assert shutil.disk_usage(directory).free >= 8 * 1024**3
            report["tool_hashes"] = {name: digest(prefix / "bin" / name) for name in ("clang-tidy", "clang++")}
            flags = runtime["flags"]
            bad, clean = directory / "tidy-bad.cpp", directory / "tidy-clean.cpp"
            bad.write_bytes(witness.read_bytes())
            before = "if (std::string(error.what()) != message) return 2;"
            assert bad.read_text().count(before) == 1
            clean.write_text(bad.read_text().replace(before, "if (std::string(error.what()) != message) { return 2; }"))
            fixtures = [bad, clean]
            report["diagnostics"] = {}
            for label, path, expected in (("tidy-bad", bad, 1), ("tidy-clean", clean, 0)):
                original = digest(path)
                run(label, base + [prefix / "bin/clang-tidy", path, '--config={"InheritParentConfig":false}',
                                  "--checks=-*,readability-braces-around-statements",
                                  "--warnings-as-errors=readability-braces-around-statements", "--fix=false",
                                  "--fix-errors=false", "--fix-notes=false", "--", *flags], timeout=60, descriptor=fd, expected=expected)
                assert digest(path) == original
                diagnostic = "".join((directory / (label + suffix)).read_text() for suffix in (".stdout", ".stderr"))
                errors = [line for line in diagnostic.splitlines() if re.search(r": (?:fatal )?error:", line)]
                if expected:
                    assert len(errors) == 1 and str(path) + ":26:" in errors[0]
                    assert "statement should be inside braces" in errors[0] and "readability-braces-around-statements" in errors[0]
                else:
                    assert not errors and "readability-braces-around-statements" not in diagnostic
                assert "[clang-diagnostic-" not in diagnostic
                report["diagnostics"][label] = {"native_returncode": expected, "errors": errors, "source_unchanged": True}
            for label, text in (("analyzer-bad", "int main() {\n  int *p = nullptr;\n  *p = 7;\n  return 0;\n}\n"),
                                ("analyzer-clean", "int main() {\n  int value = 0;\n  int *p = &value;\n  *p = 7;\n  return 0;\n}\n")):
                path = directory / (label + ".cpp")
                path.write_text(text)
                fixtures.append(path)
            analyzer = base + [prefix / "bin/clang++", *flags, "--analyze", "--analyzer-no-default-checks",
                               "-Xclang", "-analyzer-checker=core.NullDereference", "--analyzer-output", "plist"]
            for label, path, expected in (("analyzer-bad", fixtures[2], 1), ("analyzer-clean", fixtures[3], 0),
                                          ("analyzer-reflection", clean, 0)):
                original, output = digest(path), directory / (label + ".plist")
                assert not output.exists()
                errors = [] if expected else ["-Xclang", "-analyzer-werror"]
                run(label, analyzer + errors + [path, "-o", output], timeout=60, descriptor=fd)
                assert digest(path) == original and output.is_file() and output.stat().st_size > 0
                parsed = plistlib.loads(output.read_bytes())
                diagnostics = parsed["diagnostics"]
                if expected:
                    assert len(diagnostics) == 1
                    item = diagnostics[0]
                    assert item["check_name"] == "core.NullDereference" and item["type"] == "Dereference of null pointer"
                    assert item["location"]["line"] == 3 and parsed["files"][item["location"]["file"]] == str(path)
                    assert str(path) + ":3:6: warning: Dereference of null pointer" in (directory / (label + ".stderr")).read_text()
                else:
                    assert diagnostics == [] and not re.search(r": (?:fatal )?error:", (directory / (label + ".stderr")).read_text())
                report["diagnostics"][label] = {"native_returncode": 0, "diagnostic_count": len(diagnostics),
                                              "checks": [item["check_name"] for item in diagnostics], "source_unchanged": True}
            path, output = fixtures[2], directory / "analyzer-error-exit.plist"
            original = digest(path)
            assert not output.exists()
            run("analyzer-error-exit", analyzer + ["-Xclang", "-analyzer-werror", path, "-o", output],
                timeout=60, descriptor=fd, expected=1)
            diagnostic = (directory / "analyzer-error-exit.stderr").read_text()
            errors = [line for line in diagnostic.splitlines() if re.search(r": (?:fatal )?error:", line)]
            assert len(errors) == 1 and str(path) + ":3:6: error: Dereference of null pointer" in errors[0]
            assert "[core.NullDereference]" in errors[0] and not output.exists() and digest(path) == original
            report["diagnostics"]["analyzer-error-exit"] = {"native_returncode": 1, "errors": errors,
                                                          "report_removed_by_driver": True, "source_unchanged": True}
            assert bad.read_bytes() == witness.read_bytes()
            report["artifacts"] = {p.name: {"path": str(p), "sha256": digest(p)} for p in [*fixtures, *directory.glob("*.plist")]}
        report["lease_released"] = True
        env.pop("MARKETPLACE_P2996_PREFIX")
        assert run("default-after", normal_argv) == normal
        source_state("source-after")
        report["state"] = "PASS: clang-tidy and static analyzer reflection controls"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            report["protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}))


if __name__ == "__main__":
    main()
