from pathlib import Path
import ast
import copy
import errno
import fcntl
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time

ROOT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
EVIDENCE = ROOT / "evidence/vcpkg-fmt-build"
run = Path(json.loads((EVIDENCE / "attempt-1/candidate/admission.json").read_text())["run_directory"])
directory = Path(tempfile.mkdtemp(prefix="fmt-alias-diagnosis-", dir=run.parent))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
record = {"script_sha256": digest(Path(__file__)), "private_directory": str(directory), "native_compiler_build_calls": 0}
try:
    original = json.loads((run / "qualification.json").read_text())
    assert original["state"] == "FAIL" and original["protected_state_unchanged"]
    record["native_failure_sha256"] = digest(run / "qualification.json")
    record["processes"] = []
    for row in original["commands"]:
        assert "returncode" in row
        try:
            os.kill(row["pid"], 0)
        except OSError as error:
            assert error.errno == errno.ESRCH
        else:
            raise AssertionError("a recorded command PID remains active")
        record["processes"].append({"pid": row["pid"], "case": row["case"], "absent": True})
    lock = Path.home() / ".local/state/dotfiles/heavy-gate.lock"
    before = digest(lock)
    with lock.open("rb") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    assert digest(lock) == before
    record["lease_probe"] = {"free": True, "contents_unchanged": True}
    contract = json.loads((EVIDENCE / "attempt-1/candidate/contract.json").read_text())
    argv = original["commands"][1]["argv"]
    assert original["commands"][1]["case"] == "default-before"
    env = json.loads((Path(argv[-1]).parent / "context.json").read_text())["environment"] | {
        "MISE_OFFLINE": "1", "MISE_AUTO_INSTALL": "0", "MISE_EXEC_AUTO_INSTALL": "0", "MISE_TASK_RUN_AUTO_INSTALL": "0"}
    started = time.monotonic()
    process = subprocess.run(argv, env=env, cwd=run, text=True, capture_output=True, timeout=60)
    record["default_after"] = {"argv": argv, "returncode": process.returncode, "elapsed_seconds": time.monotonic() - started}
    for suffix, value in [("stdout", process.stdout), ("stderr", process.stderr)]:
        path = directory / ("default-after." + suffix)
        path.write_text(value)
        record["default_after"][suffix + "_sha256"] = digest(path)
    assert process.returncode == 0 and process.stdout == (ROOT / contract["default_profile"]).read_text()
    proposed = copy.deepcopy(contract)
    proposed["host_compiler"] = {"C": "/Library/Developer/CommandLineTools/usr/bin/cc",
                                 "CXX": "/Library/Developer/CommandLineTools/usr/bin/c++",
                                 "id": "AppleClang", "version": "21.0.0.21000334"}
    record["host_aliases"] = []
    for language in ("C", "CXX"):
        path = Path(proposed["host_compiler"][language])
        assert path.samefile(Path(contract["host_compiler"][language]))
        record["host_aliases"].append({"path": str(path), "link": os.readlink(path), "resolved": str(path.resolve()),
                                       "sha256": digest(path), "sha1": hashlib.sha1(path.read_bytes()).hexdigest()})
    scope = dict(globals())
    for path, name in [(ROOT / "dev/toolchains/p2996_install.py", "prefix_inventory"),
                       (EVIDENCE / "attempt-1/candidate/vcpkg_fmt.py.source", "inspect_cell")]:
        node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
    triplet = "arm64-osx-p2996-static"
    record["diagnostic_cell"] = scope["inspect_cell"](run / triplet, triplet, proposed, original["environments"]["p2996"])
    record.update(state="PASS", inspect_cell_calls=1, proposed_host_compiler=proposed["host_compiler"],
                  limitation="Read-only diagnosis against the failed run; does not change its FAIL result or qualify the remaining cells.")
except BaseException as error:
    record.update(state="FAIL", error=repr(error))
    raise
finally:
    (directory / "diagnosis.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"state": record["state"], "receipt": str(directory / "diagnosis.json")}))
