"""Prepare or apply the independently tested two-header SDK math adaptation."""

import argparse
import ast
from datetime import datetime, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

from gcc_install import ROOT, digest, preserved, read
from mise_link_probe import snapshot
from p2996_configure import LOCK_MODULE, LOCK_SHA
from p2996_sdk_compat import FILES as SDK_FILES
from vcpkg_register import install_entries

FILES = ("clang/lib/Headers/float.h", "libcxx/include/float.h")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    directory = args.run_dir
    if not directory.is_absolute() or directory != directory.resolve() or directory.is_relative_to(ROOT):
        parser.error("use a new normalized absolute private directory outside this worktree")
    os.umask(0o077)
    directory.mkdir(exist_ok=False)
    load = lambda p: json.loads(p.read_text())
    evidence = ROOT / "evidence/p2996-math-application"
    scratch = ROOT / "evidence/p2996-math-compatibility"
    failed = ROOT / "evidence/p2996-resume/failed-incremental-build"
    probe = load(scratch / "scratch/qualification.json")
    adaptation = probe["proposal"]
    source, patch = Path(adaptation["source"]), scratch / "scratch/sdk-math.patch"
    configuration = load(failed / "qualification.json")["proposal"]["configuration"]
    prior = load(ROOT / "evidence/p2996-sdk-compatibility/operation/qualification.json")
    retained = load(scratch / "independent-scratch/retained-preimages.json")
    baseline = load(ROOT / "evidence/p2996-build/independent-preparation/pre-state.json")
    report = {"state": "running", "apply_requested": args.apply, "applied": False,
              "helper_sha256": digest(Path(__file__)), "commands": []}
    normal_argv = read("install-preimages.json")["normal_environment"]["argv"]
    env = load(Path(normal_argv[-1]).parent / "context.json")["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0",
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"}

    def save():
        temporary = directory / "qualification.json.tmp"
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(directory / "qualification.json")

    helper = failed / "helper.py.source"
    assert digest(helper) == "eb10682c0014e1ba5d8409ef641f46b1037f18b88a5abc68cb6d2c44d6fbfb9f"
    node = next(n for n in ast.walk(ast.parse(helper.read_text()))
                if isinstance(n, ast.FunctionDef) and n.name == "run")
    scope = globals() | {"directory": directory, "report": report, "env": env, "save": save}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(helper), "exec"), scope)
    run = scope["run"]

    def protected():
        preserved(baseline["protected"])
        assert all(snapshot(Path(p)) == value for p, value in baseline["directories"].items())
        assert install_entries(Path.home() / ".local/share/mise/installs") == baseline["install_entries"]
        for path, sha in retained["source_generated"].items():
            if path not in {str(source / name) for name in FILES}:
                assert digest(Path(path)) == sha, path
        for row in retained["inventory_records"]:
            p = Path(row["path"])
            assert os.path.lexists(p) == row["lexists"] and p.exists() == row["exists"], str(p)
            if "sha256" in row:
                assert digest(p) == row["sha256"] and str(p.resolve()) == row["resolved_path"], str(p)
            assert (os.readlink(p) if p.is_symlink() else None) == row.get("symlink_target"), str(p)

    def interrupted(signum, frame):
        raise KeyboardInterrupt("received signal " + str(signum))

    for signum in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT):
        signal.signal(signum, interrupted)
    try:
        reviewed = load(scratch / "preparation-review.json")
        assert reviewed["result"].startswith("PASS") and not reviewed["findings"]
        assert reviewed["helper_sha256"] == probe["helper_sha256"] == digest(scratch / "scratch/helper.py.source")
        assert reviewed["patch_sha256"] == adaptation["patch_sha256"] == digest(patch)
        assert reviewed["proposal_sha256"] == digest(scratch / "scratch/proposal.json")
        assert adaptation == load(scratch / "scratch/proposal.json")
        assert probe["state"].startswith("PASS") and probe["lease_released"]
        assert probe["source_build_and_protected_state_unchanged"]
        assert [(r["case"], r["returncode"]) for r in probe["commands"]] == list(reviewed["expected_exit_codes"].items())
        assert source == source.resolve() == Path(configuration["source"])
        assert adaptation["base_commit"] == configuration["pin"]
        assert tuple(row["path"] for row in adaptation["files"]) == FILES
        assert tuple(row["path"] for row in prior["proposal"]["adaptation"]["files"]) == SDK_FILES
        assert prior["state"] == "PASS: exact source adaptation applied" and prior["applied"]
        assert prior["lease_released"] and prior["protected_state_unchanged"]
        assert prior["diff_sha256"] == adaptation["prior_source_diff_sha256"]
        receipt_paths = [scratch / name for name in (
            "scratch/qualification.json", "scratch/proposal.json", "scratch/sdk-math.patch",
            "preparation-review.json", "independent-scratch/retained-preimages.json")]
        receipt_paths += [ROOT / "evidence/p2996-sdk-compatibility/operation/qualification.json",
                          ROOT / "evidence/p2996-resume/failure-closure-review.json",
                          failed / "qualification.json", helper]
        report["proposal"] = {"adaptation": adaptation,
                              "receipts": {str(p.relative_to(ROOT)): digest(p) for p in receipt_paths},
                              "lock_sha256": LOCK_SHA,
                              "helpers": {name: digest(Path(__file__).with_name(name)) for name in
                                          ("gcc_install.py", "gcc_bottles.py", "mise_link_probe.py", "vcpkg_register.py",
                                           "p2996_configure.py", "p2996_sdk_compat.py")}}
        git = ["/usr/bin/git", "-c", "core.fsmonitor=false", "-C", source]

        def inputs():
            for name, sha in report["proposal"]["receipts"].items():
                assert digest(ROOT / name) == sha, name
            for name, sha in report["proposal"]["helpers"].items():
                assert digest(Path(__file__).with_name(name)) == sha, name
            protected()

        def source_state(label, patched=False):
            assert run(label + "-head", git + ["rev-parse", "HEAD"]).strip() == configuration["pin"]
            assert run(label + "-tree", git + ["rev-parse", "HEAD^{tree}"]).strip() == configuration["tree"]
            status = run(label + "-status", git + ["status", "--porcelain", "--untracked-files=all"])
            assert status.splitlines() == sorted(" M " + name for name in (*SDK_FILES, *(FILES if patched else ())))
            for row in prior["proposal"]["adaptation"]["files"] + adaptation["files"]:
                p = source / row["path"]
                assert p == p.resolve() and p.is_relative_to(source)
                key = "after_sha256" if patched or row["path"] in SDK_FILES else "before_sha256"
                assert digest(p) == row[key], str(p)
            run(label + "-diff", git + ["diff", "--no-ext-diff", "--binary"])
            sha = digest(directory / (label + "-diff.stdout"))
            if not patched:
                assert sha == adaptation["prior_source_diff_sha256"]
            return sha

        inputs()
        source_state("source-before")
        run("patch-check", git + ["apply", "--check", patch])
        normal = run("default-before", normal_argv)
        if args.apply:
            admission = load(evidence / "admission.json")
            review_path = evidence / "preparation-review.json"
            review = load(review_path)
            assert admission["helper_sha256"] == digest(Path(__file__)) == review["helper_sha256"]
            assert admission["proposal"] == report["proposal"] == review["proposal"]
            assert admission["run_directory"] == str(directory)
            assert admission["review_sha256"] == digest(review_path)
            assert review["result"].startswith("PASS") and not review["findings"]
            assert digest(LOCK_MODULE) == LOCK_SHA
            spec = importlib.util.spec_from_file_location("marketplace_math_apply_lock", LOCK_MODULE)
            lease = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lease)
            assert lease.lock_path(lease.HEAVY_GATE) == Path.home() / ".local/state/dotfiles/heavy-gate.lock"
            assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
            with lease.held(lease.HEAVY_GATE, "marketplace-sdk-math-apply", wait_s=0, out=io.StringIO()) as fd:
                assert fd is not None
                inputs()
                source_state("source-immediate")
                run("patch-check-immediate", git + ["apply", "--check", patch])
                run("patch-apply", git + ["apply", patch], descriptor=fd)
                report["applied"] = True
                report["diff_sha256"] = source_state("source-after", patched=True)
                run("patch-reverse-check", git + ["apply", "--reverse", "--check", patch])
                inputs()
            report["lease_released"] = True
        assert run("default-after", normal_argv) == normal
        report["state"] = "PASS: exact math adaptation applied" if args.apply else "PASS: preparation only"
    except BaseException as error:
        report.update(state="FAIL", error=repr(error))
        raise
    finally:
        try:
            protected()
            report["build_and_protected_state_unchanged"] = True
        except BaseException as error:
            report.update(state="FAIL", preservation_error=repr(error))
            raise
        finally:
            save()
            print(json.dumps({"state": report["state"], "receipt": str(directory / "qualification.json")}), flush=True)


if __name__ == "__main__":
    main()
