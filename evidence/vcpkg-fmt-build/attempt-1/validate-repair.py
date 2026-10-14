from pathlib import Path
import ast
import hashlib
import json
import os
import re

ROOT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
EVIDENCE = ROOT / "evidence/vcpkg-fmt-build"
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
run = Path(json.loads((EVIDENCE / "attempt-1/candidate/admission.json").read_text())["run_directory"])
triplet = "arm64-osx-p2996-static"
contract = json.loads((EVIDENCE / "contract.json").read_text())
original = json.loads((run / "qualification.json").read_text())
record = {"helper_sha256": digest(ROOT / "dev/toolchains/vcpkg_fmt.py"),
          "contract_sha256": digest(EVIDENCE / "contract.json"), "script_sha256": digest(Path(__file__)),
          "native_commands": 0, "original_run_state": original["state"], "cache_controls": []}
try:
    old_tree = ast.parse((EVIDENCE / "attempt-1/candidate/vcpkg_fmt.py.source").read_text())
    new_tree = ast.parse((ROOT / "dev/toolchains/vcpkg_fmt.py").read_text())
    patterns = [next(n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and
                     isinstance(n.value, str) and n.value.startswith("^([^#/:") ) for tree in (old_tree, new_tree)]
    for short, configuration in [("dbg", "Debug"), ("rel", "Release")]:
        path = run / triplet / "buildtrees/fmt" / (triplet + "-" + short) / "CMakeCache.txt"
        old, new = [dict(re.findall(pattern, path.read_text(), re.MULTILINE)) for pattern in patterns]
        assert "CMAKE_BUILD_TYPE" not in old and new["CMAKE_BUILD_TYPE"] == configuration
        assert all("\n" not in key and "\r" not in key for key in new)
        record["cache_controls"].append({"path": str(path), "sha256": digest(path), "configuration": configuration,
                                          "old_missing_exact_key": True, "new_keys_confined_to_lines": True})
    sample = "//Comment\r\n\r\nFIRST:STRING=one\r\nSECOND:FILEPATH=two\r\n"
    parsed = dict(re.findall(patterns[1], sample, re.MULTILINE))
    assert {key: value.rstrip("\r") for key, value in parsed.items()} == {"FIRST": "one", "SECOND": "two"}
    record["crlf_keys_control"] = "PASS"
    scope = dict(globals())
    for path, name in [(ROOT / "dev/toolchains/p2996_install.py", "prefix_inventory"),
                       (ROOT / "dev/toolchains/vcpkg_fmt.py", "inspect_cell")]:
        node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == name)
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
    record["cell"] = scope["inspect_cell"](run / triplet, triplet, contract, original["environments"]["p2996"])
    record.update(state="PASS", inspect_cell_calls=1,
                  limitation="Read-only validation of corrected expectations; original native attempt remains FAIL.")
except BaseException as error:
    record.update(state="FAIL", error=repr(error))
    raise
finally:
    (EVIDENCE / "attempt-1/repair-validation.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"state": record["state"], "native_commands": 0}))
