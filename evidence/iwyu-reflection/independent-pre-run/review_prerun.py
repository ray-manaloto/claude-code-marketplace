"""09c1 independent data audit and AST-only parser/mock-wrapper controls."""
import ast
from contextlib import nullcontext, redirect_stdout
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

D = Path(__file__).resolve().parent
FROZEN = json.loads((D / "frozen-inputs.json").read_text())
ROOT = Path(FROZEN["root"])
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())
write = lambda p, data: Path(p).write_text(json.dumps(data, indent=2) + "\n")
references = []
def bind(path, expected=None, size=None):
    path = Path(path)
    actual = digest(path)
    if expected is not None:
        assert actual == expected, str(path)
    if size is not None:
        assert path.stat().st_size == size, str(path)
    references.append({"path": str(path), "sha256": actual, "bytes": path.stat().st_size})
    return actual
def frozen():
    for rel, row in FROZEN["files"].items():
        assert digest(ROOT / rel) == row["sha256"] and (ROOT / rel).stat().st_size == row["bytes"], rel
def get_function(path, name, scope):
    parsed = ast.parse(Path(path).read_text())
    node = next(n for n in ast.walk(parsed) if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
    return scope[name]

frozen()
candidate = ROOT / "dev/toolchains/iwyu_reflection.py"
contract_path = ROOT / "evidence/iwyu-reflection/contract.json"
recipe_path = ROOT / "evidence/iwyu-reflection/source-recipe.json"
contract, recipe = load(contract_path), load(recipe_path)
bind(candidate, FROZEN["files"]["dev/toolchains/iwyu_reflection.py"]["sha256"])
bind(contract_path, FROZEN["files"]["evidence/iwyu-reflection/contract.json"]["sha256"])
bind(recipe_path, FROZEN["files"]["evidence/iwyu-reflection/source-recipe.json"]["sha256"])
assert contract["base_head"] == "1ddd107bffe56226ae2a5c115fcb4e2ae6b7b6b9"
for rel, expected in contract["inputs"].items():
    bind(ROOT / rel, expected)
for row in recipe["prerequisites"] + recipe["source_bindings"]:
    bind(row["path"], row["sha256"], row.get("bytes"))

# Resolve only the relevant transitive Python binding; do not call protected().
runtime_source = ROOT / "dev/toolchains/mise_runtime.py"
runtime_ast = ast.parse(runtime_source.read_text())
runtime_expected = next(ast.literal_eval(n.value) for n in runtime_ast.body
                        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CONTRACT_SHA" for t in n.targets))
runtime_path = ROOT / "evidence/mise-runtime/contract.json"
bind(runtime_path, runtime_expected)
runtime_contract = load(runtime_path)
python = recipe["bindings"]["PYTHON"]
python_hash = runtime_contract["inputs"][python]
bind(python, python_hash)
assert str(Path(sys.executable)) == python
assert python_hash == "26425d16b160c10f52f887e317c53b0036d00bf8ff10a171e6fb1e942feebc17"

prerequisite_reviews = {}
for rel in ("evidence/iwyu-build/installation-review.json", "evidence/mise-runtime/runtime-review.json"):
    review = load(ROOT / rel)
    prerequisite_reviews[rel] = {"sha256": digest(ROOT / rel), "result": review["result"], "findings": review["findings"]}
assert prerequisite_reviews["evidence/mise-runtime/runtime-review.json"]["result"].startswith("PASS")
assert not prerequisite_reviews["evidence/mise-runtime/runtime-review.json"]["findings"]
static_path = ROOT / "evidence/iwyu-reflection/pre-review-static.json"
bind(static_path)
static = load(static_path)
assert [r["returncode"] for r in static] == [0, 0]
assert json.loads(static[1]["stdout"])["checks"]["baseline"] == 19
baseline_path = ROOT / "evidence/onboarding/baseline-files.json"
bind(baseline_path)
baseline = load(baseline_path)["files"]
assert len(baseline) == 19
for row in baseline:
    bind(ROOT / row["path"], row["sha256"], row["bytes"])
for name in ("iwyu_globals.cc", "iwyu_output.cc"):
    source_root = Path(next(row["path"] for row in recipe["source_bindings"] if row["id"] == "S7")).parent
    acquired = load(ROOT / "evidence/iwyu-source/operation/acquisition.json")
    row = next(row for row in acquired["verified_files"] if row["path"] == name)
    bind(source_root / name, row["sha256"], row["bytes"])
bind(ROOT / "evidence/mise-runtime/operation/exec-help.stdout")

fixture_data = recipe["reflection_fixture"]
for row in fixture_data["files"]:
    assert Path(row["path"]).name == row["path"]
    assert hashlib.sha256(row["content"].encode()).hexdigest() == row["sha256"]
fixed = fixture_data["fixer"]
assert hashlib.sha256(fixed["expected_after"].encode()).hexdigest() == fixed["expected_after_sha256"]
original = next(r["content"] for r in fixture_data["files"] if r["path"] == "main.cc")
assert original.replace('#include "indirect.h"', '#include "value.h"') == fixed["expected_after"]
assert "^^FixtureValue" in original and "std::meta::is_type" in original
assert fixture_data["analyze_argv"].count("-freflection") == 1
assert fixture_data["analyze_argv"][-5:-1] == ["-Xiwyu", "--verbose=3", "-Xiwyu", "--error=23"]
assert fixed["argv"][0] == python
assert fixed["argv"][-3:] == ["--basedir", "<private-09c-root>/fixtures/reflection", "<private-09c-root>/fixtures/reflection/main.cc"]
write(D / "input-audit.json", {"result": "PASS", "references": references,
    "contract_inputs": len(contract["inputs"]), "recipe_bindings": len(recipe["prerequisites"]) + len(recipe["source_bindings"]),
    "prerequisite_reviews": prerequisite_reviews, "static_receipts": static,
    "python_binding": {"path": python, "sha256": python_hash, "via": str(runtime_path)},
    "original_Claude_files": 19, "full_protected_function_invocations": 0})

recommendations = get_function(candidate, "recommendations", {"re": re})
source = D / "synthetic parser fixture/main.cc"
sample = (f"{source}:4:1: warning: FixtureValue needs a declaration\n\n"
          f"{source} should add these lines:\n#include \"value.h\" // for FixtureValue\n\n"
          f"{source} should remove these lines:\n- #include \"indirect.h\"  // lines 2-2\n\n"
          f"The full include-list for {source}:\n#include <meta> // for is_type\n"
          '#include "value.h" // for FixtureValue\n---\n')
expected_sections = [['#include "value.h"'], ['- #include "indirect.h"'], ['#include <meta>', '#include "value.h"']]
parser_cases = [
    ("canonical", sample, True),
    ("without_comments", re.sub(r" *//[^\n]*", "", sample), True),
    ("frontend_error", f"{source}:1:1: error: bad\n" + sample, False),
    ("frontend_fatal", f"{source}:1:1: fatal error: bad\n" + sample, False),
    ("missing_warning", sample.replace("warning:", "note:"), False),
    ("wrong_source", sample.replace(str(source), str(D / "other.cc")), False),
    ("duplicate_record", sample + sample, False),
    ("extra_add", sample.replace('#include "value.h" // for FixtureValue', '#include "value.h"\n#include "extra.h"', 1), False),
    ("extra_remove", sample.replace('- #include "indirect.h"', '- #include <meta>\n- #include "indirect.h"', 1), False),
    ("missing_meta", sample.replace('#include <meta> // for is_type\n', ""), False),
    ("extra_final_include", sample.replace("---\n", "#include <vector>\n---\n"), False),
    ("duplicate_final_include", sample.replace("---\n", '#include "value.h"\n---\n'), False),
    ("missing_remove_section", sample.replace("should remove these lines:", "removed lines:"), False),
    ("missing_separator", sample.replace("---\n", ""), False),
    ("wrong_direct_header", sample.replace('"value.h"', '"wrong.h"'), False),
]
parser_results = []
for name, value, accept in parser_cases:
    try:
        actual = recommendations(value, source)
    except AssertionError:
        observed = False
    else:
        observed = True
        assert actual == expected_sections
    assert observed == accept, name
    parser_results.append({"case": name, "expected_accept": accept, "observed_accept": observed, "result": "PASS"})
(D / "synthetic-advice.txt").write_text(sample)

# Execute the actual frozen run function with a spy replacing Popen. It creates no children.
native_path = ROOT / "evidence/p2996-math-resume/operation/p2996_build.py.source"
wrapper_results = []
def wrapper_case(name, returncode, expected, error=None, custom_cwd=False, use_stdin=False, duplicate=False):
    directory = D / ("mock-" + name)
    directory.mkdir()
    fixture = directory / "fixtures/reflection"
    fixture.mkdir(parents=True)
    report = {"commands": []}
    calls, handles = [], []
    input_path = directory / "input.iwyu"
    payload = b"synthetic analysis stderr\r\n\x00byte-preservation\n"
    input_path.write_bytes(payload)
    def save():
        write(directory / "record.json", report)
    class Process:
        pid = 987654321
        def __init__(self):
            self.returncode = returncode
        def poll(self):
            return self.returncode
        def wait(self, timeout=None):
            return self.returncode
    def spy(command, **kwargs):
        handle = kwargs["stdin"]
        handles.append(handle)
        got = handle.read() if handle != subprocess.DEVNULL else None
        calls.append({"command": command, "cwd": str(kwargs["cwd"]), "stdin_hex": None if got is None else got.hex(),
                      "pass_fds": list(kwargs["pass_fds"]), "start_new_session": kwargs["start_new_session"],
                      "environment": kwargs["env"]})
        if error is not None:
            raise error
        kwargs["stdout"].write(b"mock stdout\n")
        kwargs["stderr"].write(b"mock stderr\n")
        kwargs["stdout"].flush()
        kwargs["stderr"].flush()
        return Process()
    fake_subprocess = SimpleNamespace(Popen=spy, DEVNULL=subprocess.DEVNULL, TimeoutExpired=subprocess.TimeoutExpired)
    native_scope = {"Path": Path, "datetime": datetime, "timezone": timezone, "json": json, "time": time,
                    "digest": digest, "directory": directory, "report": report, "env": {"SAFE_MOCK": "1"}, "save": save}
    native = get_function(native_path, "run", native_scope)
    wrapper_scope = {"nullcontext": nullcontext, "subprocess": fake_subprocess, "SimpleNamespace": SimpleNamespace,
                     "scope": native_scope, "native": native, "report": report, "directory": directory,
                     "digest": digest, "save": save}
    run = get_function(candidate, "run", wrapper_scope)
    if duplicate:
        report["commands"].append({"case": name})
    failure = None
    captured = io.StringIO()
    output = None
    with redirect_stdout(captured):
        try:
            output = run(name, [Path("/mock/tool"), "argument with spaces"], timeout=17, descriptor=91,
                         expected=expected, stdin=input_path if use_stdin else None, cwd=fixture if custom_cwd else None)
        except BaseException as exc:
            failure = {"type": type(exc).__name__, "text": str(exc)}
    should_accept = error is None and not duplicate and returncode == expected
    assert (failure is None) == should_accept, (name, failure)
    if duplicate:
        assert not calls and failure["type"] == "AssertionError"
    else:
        assert len(calls) == 1
        call = calls[0]
        assert call["command"] == ["/mock/tool", "argument with spaces"]
        assert call["cwd"] == str(fixture if custom_cwd else directory)
        assert call["stdin_hex"] == (payload.hex() if use_stdin else None)
        assert call["pass_fds"] == [91] and call["start_new_session"] is True
        row = report["commands"][0]
        assert row["cwd"] == call["cwd"] and row["expected_returncode"] == expected
        assert row["timeout_seconds"] == 17
        assert row["stdin"] == ({"path": str(input_path), "sha256": digest(input_path)} if use_stdin else None)
        if error is None:
            assert row["returncode"] == returncode and len(row["logs"]) == 2
            assert all(digest(log["path"]) == log["sha256"] for log in row["logs"])
        else:
            assert failure["type"] == type(error).__name__
        if use_stdin:
            assert handles[0].closed
        if should_accept:
            assert output == "mock stdout\n"
    (directory / "captured-print.txt").write_text(captured.getvalue())
    result = {"case": name, "simulated_child_returncode": returncode, "expected_returncode": expected,
              "accepted": failure is None, "failure": failure, "calls": calls,
              "result": "PASS", "actual_children_created": 0}
    wrapper_results.append(result)

wrapper_case("success_default", 0, 0)
wrapper_case("success_stdin_cwd", 0, 0, custom_cwd=True, use_stdin=True)
wrapper_case("expected_advice", 23, 23)
wrapper_case("expected_negative", 1, 1)
wrapper_case("unexpected_failure", 1, 0)
wrapper_case("unexpected_success", 0, 23)
wrapper_case("wrong_nonzero", 1, 23)
wrapper_case("signal_exit", -15, 23)
wrapper_case("popen_oserror", 23, 23, OSError("mock spawn failure"), use_stdin=True)
wrapper_case("popen_timeout", 23, 23, subprocess.TimeoutExpired(["/mock/tool"], 17), use_stdin=True)
wrapper_case("popen_interrupt", 23, 23, KeyboardInterrupt("mock interrupt"), use_stdin=True)
wrapper_case("duplicate_label", 0, 0, duplicate=True)

# Derive the final fixer invocation from candidate AST and recipe without running main().
main = next(n for n in ast.parse(candidate.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "main")
base_assignment = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == "base" for t in n.targets))
case_root = D / "cwd-proof"
case_fixture = case_root / "fixtures/reflection"
base = eval(compile(ast.Expression(body=base_assignment.value), str(candidate), "eval"),
            {"current": runtime_contract["current_mise"], "directory": case_root})
argv = base + [s.replace("<private-09c-root>", str(case_root)) for s in fixed["argv"]]
mise_cd = argv[argv.index("-C") + 1]
assert Path(mise_cd) == case_root / "cwd" and Path(mise_cd) != case_fixture
assert fixed["cwd"].replace("<private-09c-root>", str(case_root)) == str(case_fixture)
cwd_proof = {"result": "FINDING REPRODUCED BY ARGV DERIVATION",
             "argv": list(map(str, argv)), "requested_Popen_cwd": str(case_fixture),
             "mise_C_operand": str(mise_cd), "recipe_cwd": str(case_fixture),
             "native_execution": False,
             "source": {"candidate_lines": [123, 171, 172],
                        "mise_help": str(ROOT / "evidence/mise-runtime/operation/exec-help.stdout"),
                        "mise_help_line": 70},
             "confinement": "Absolute --basedir and file allowlist still identify only main.cc."}
write(D / "cwd-proof.json", cwd_proof)
write(D / "controls.json", {"result": "PASS: parser and mocked-wrapper controls",
    "parser_cases": parser_results, "wrapper_cases": wrapper_results, "cwd_discrepancy": cwd_proof,
    "native_Popen_calls": 0, "helper_main_calls": 0, "protected_calls": 0})
frozen()
for row in baseline:
    assert digest(ROOT / row["path"]) == row["sha256"]
write(D / "final-preservation.json", {"result": "PASS", "frozen_files": FROZEN["files"], "original_Claude_files": 19,
    "note": "Only scoped source/receipt and original-file hashes checked; no full protection or global inventory invocation."})
print(json.dumps({"result": "PASS: bounded review controls; one cwd finding", "parser_cases": len(parser_results),
                  "mock_wrapper_cases": len(wrapper_results), "references": len(references),
                  "unique_reference_paths": len({r["path"] for r in references}), "original_Claude_files": len(baseline),
                  "actual_children_created": 0, "helper_main_calls": 0, "protected_calls": 0}))

