"""Prepare native mise registration; --apply promotes one reviewed LLVM namespace."""

import argparse
import ast
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import TOOLS, isolated, snapshot
from p2996_install import prefix_inventory
from vcpkg_register import census, install_entries, promote


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    directory = args.run_dir
    load = lambda p: json.loads(p.read_text())
    installed = ROOT / "evidence/p2996-install"
    reflected = ROOT / "evidence/p2996-reflection"
    evidence = ROOT / "evidence/p2996-registration"
    inventory = load(installed / "independent-installation/post-install-inventory.json")
    baseline = load(installed / "independent-installation/post-state.json")
    prefix, workspace = Path(inventory["prefix"]), Path(inventory["workspace"])
    configuration = load(ROOT / "evidence/p2996-math-resume/operation/qualification.json")["proposal"]["configuration"]
    source = Path(configuration["source"])
    protected_roots = (ROOT, workspace, source, Path.home() / ".config", Path.home() / ".local/share/mise")
    if (not directory.is_absolute() or directory != directory.resolve()
            or any(directory.is_relative_to(p) for p in protected_roots)):
        parser.error("use a new normalized private directory outside project, source, build and global mise")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    data = Path.home() / ".local/share/mise"
    installs = data / "installs"
    destination = installs / "asdf-clang-p2996"
    version = TOOLS["clang-p2996"]
    tool = "asdf:clang-p2996@" + version
    report = {"state": "running", "apply_requested": args.apply, "commands": [],
              "helper_sha256": digest(Path(__file__)), "promotion_attempted": False, "promoted": False}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    helper = ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source"
    assert digest(helper) == "7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f"
    node = next(n for n in ast.walk(ast.parse(helper.read_text()))
                if isinstance(n, ast.FunctionDef) and n.name == "run")
    scope = globals() | {"directory": directory, "report": report, "save": save}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(helper), "exec"), scope)

    def run(label, argv, environment):
        scope["env"] = environment
        return scope["run"](label, argv, timeout=45)

    def protected():
        preserved(baseline["protected"])
        assert all(snapshot(Path(p)) == value for p, value in baseline["directories"].items())
        current = install_entries(installs)
        if report["promoted"]:
            assert destination.is_dir() and not destination.is_symlink()
            assert snapshot(destination) == report["proposal"]["namespace"]
            current = {k: v for k, v in current.items() if k.split("/")[0] != destination.name}
        else:
            assert not os.path.lexists(destination)
        assert current == baseline["install_entries"]
        for row in inventory["records"]:
            p = Path(row["path"])
            assert os.path.lexists(p) == row["lexists"] and p.exists() == row["exists"], str(p)
            if row["lexists"]:
                assert oct(p.lstat().st_mode & 0o777) == row["lstat_mode"]
            if row["exists"]:
                assert str(p.resolve()) == row["resolved_path"] and oct(p.stat().st_mode & 0o777) == row["mode"]
            if "sha256" in row:
                assert digest(p) == row["sha256"] and p.stat().st_size == row["bytes"], str(p)
            assert (os.readlink(p) if p.is_symlink() else None) == row.get("symlink_target"), str(p)
        assert prefix_inventory(prefix) == load(installed / "operation/prefix-inventory.json")

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        assert digest(reflected / "reflection-review.json") == "cb547b67a1848b218e8676f21509e02dc631e68a40864bdb337bd7513d39f094"
        review = load(reflected / "reflection-review.json")
        qualification = load(reflected / "operation/qualification.json")
        assert review["result"].startswith("PASS") and not review["findings"] and review["all_protected_state_unchanged"]
        assert digest(reflected / "operation/qualification.json") == review["operation_sha256"]
        assert qualification["state"].startswith("PASS") and qualification["protected_state_unchanged"] and qualification["lease_released"]
        assert digest(installed / "installation-review.json") == review["installation_review_sha256"]
        installation_review = load(installed / "installation-review.json")
        for name in ("post-state.json", "post-install-inventory.json"):
            expected = next(r["sha256"] for r in installation_review["supporting_receipts"] if Path(r["path"]).name == name)
            assert digest(installed / "independent-installation" / name) == expected
        assert digest(installed / "operation/prefix-inventory.json") == installation_review["prefix_inventory_sha256"]
        dependencies = load(installed / "operation/qualification.json")["proposal"]["helpers"] | {
            "p2996_install.py": installation_review["helper_sha256"]}
        assert all(digest(Path(__file__).with_name(n)) == sha for n, sha in dependencies.items())
        assert version == configuration["pin"] and prefix == Path(qualification["prefix"])
        assert installs.is_dir() and installs == installs.resolve()
        assert all(not os.path.lexists(data / "plugins" / n) for n in ("clang-p2996", "asdf-clang-p2996"))
        protected()
        backups = {}
        for name, row in baseline["protected"]["global_files"].items():
            p = Path.home() / ".config/mise" / name
            backup = directory / "backups" / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, backup)
            assert digest(backup) == row["sha256"]
            backups[name] = row | {"backup": str(backup)}
        report["global_preimages"] = backups
        normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
        normal_env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {"MISE_OFFLINE": "1"}
        normal = run("default-before", normal_argv, normal_env)
        assert json.loads(normal) == json.loads((reflected / "operation/default-after.stdout").read_text())
        env = isolated(directory / "stage")
        env.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null", GIT_TERMINAL_PROMPT="0")
        mise = configuration["mise"]
        assert digest(Path(mise["path"])) == mise["sha256"]
        base = [mise["path"], "--no-config", "--no-hooks", "--no-env", "-C", env["MISE_CEILING_PATHS"]]
        run("native-link", base + ["link", tool, prefix], env)
        namespace = directory / "stage/data/installs" / destination.name
        assert set(p.name for p in namespace.iterdir()) == {version}
        assert (namespace / version).is_symlink() and (namespace / version).resolve() == prefix
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]

        def source_state(stage):
            assert run(stage + "-head", git + ["rev-parse", "HEAD"], env).strip() == version
            assert run(stage + "-tree", git + ["rev-parse", "HEAD^{tree}"], env).strip() == configuration["tree"]
            assert run(stage + "-status", git + ["status", "--porcelain", "--untracked-files=all"], env) == (installed / "operation/source-status.stdout").read_text()
            run(stage + "-diff", git + ["diff", "--no-ext-diff", "--binary"], env)
            assert digest(directory / (stage + "-diff.stdout")) == review["source_diff_sha256"]

        source_state("source-before")
        inputs = [reflected / "reflection-review.json", reflected / "operation/qualification.json",
                  installed / "installation-review.json", installed / "independent-installation/post-state.json",
                  installed / "independent-installation/post-install-inventory.json", installed / "operation/prefix-inventory.json"]
        report["proposal"] = {"destination": str(destination), "preimage": "absent", "tool": tool, "prefix": str(prefix),
                              "namespace": snapshot(namespace), "bindings": {str(p): digest(p) for p in inputs},
                              "helpers": dependencies}
        report["census"] = census(strict=args.apply)
        protected()
        if args.apply:
            admission = load(evidence / "admission.json")
            preparation = load(evidence / "preparation-review.json")
            assert admission["helper_sha256"] == digest(Path(__file__)) == preparation["helper_sha256"]
            assert admission["review_sha256"] == digest(evidence / "preparation-review.json")
            assert preparation["result"].startswith("PASS") and not preparation["findings"]
            assert admission["proposal"] == report["proposal"] == preparation["proposal"]
            assert admission["run_directory"] == str(directory)
            report["census_immediate"] = census()
            protected()
            assert namespace.stat().st_dev == installs.stat().st_dev
            assert snapshot(namespace) == report["proposal"]["namespace"]
            report["promotion_attempted"] = True
            save()
            promote(namespace, destination)
            report["promoted"] = True
            save()
            env["MISE_INSTALLS_DIR"] = str(installs)
        located = Path(run("native-where", base + ["where", tool], env).strip())
        assert located.resolve() == prefix
        compiler = run("native-version", base + ["exec", tool, "--no-deps", "--", "clang++", "--no-default-config", "--version"], env)
        stable_lines = lambda text: [s for s in text.splitlines() if not s.startswith("InstalledDir: ")]
        assert stable_lines(compiler) == stable_lines((reflected / "operation/compiler-version.stdout").read_text())
        compiler_directory = next(s.split(": ", 1)[1] for s in compiler.splitlines() if s.startswith("InstalledDir: "))
        assert Path(compiler_directory).resolve() == prefix / "bin"
        report["discovery"] = {"path": str(located), "resolved_path": str(located.resolve()), "compiler_version": compiler}
        assert json.loads(run("default-after", normal_argv, normal_env)) == json.loads(normal)
        source_state("source-after")
        report["state"] = "PASS: global namespace promotion" if args.apply else "PASS: private registration preparation"
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
            try:
                report["destination_observed"] = {"lexists": os.path.lexists(destination), "is_symlink": destination.is_symlink(),
                                                  "namespace": snapshot(destination) if destination.is_dir()
                                                  and not destination.is_symlink() else None}
            except BaseException as error:
                report["destination_observation_error"] = repr(error)
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
