import ast
import builtins
import copy
from datetime import datetime, timezone
import difflib
import dis
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import struct
import subprocess
import sys
import types
import uuid

ROOT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
E = ROOT / "evidence/p2996-lsan"
OUT = Path(__file__).resolve().parent
HEAD = "6b31a44455de2da2e204a3d02040b21bb7dc72c1"
BRANCH = "codex/marketplace-native-onboarding"
COMMON = "/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git"
watched = {}
contents = {}
checks = {}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def binding(path, expected=None):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    key = str(path)
    if key not in contents:
        before = path.stat()
        assert stat.S_ISREG(before.st_mode) and before.st_size <= 2 * 1024 * 1024, key
        raw = path.read_bytes()
        after = path.stat()
        assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), key
        raw.decode("utf-8")
        contents[key] = raw
        watched[key] = {"path": key, "sha256": sha(raw), "bytes": len(raw)}
    if expected is not None:
        assert watched[key]["sha256"] == expected, key
    return contents[key]

def parsed(path, expected=None):
    return json.loads(binding(path, expected))

candidate = parsed(E / "candidate.json", "3d0dc82922af5f8bd83cabdf8bcf5f1880bb58d2d53016eb30b358a28b6e0364")
assert candidate["base_head"] == HEAD and candidate["unit"] == "14c"
assert candidate["state"] == "prepared for bounded review; no native build or witness"
assert candidate["files"] == [
    "dev/toolchains/p2996_lsan.py",
    "dev/toolchains/lsan_witness.cpp",
    "docs/sanitizers.md",
    ".planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md",
    ".planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md",
]
for name, expected in candidate["evidence"].items():
    binding(E / name, expected)
frozen = parsed(E / "candidate-inputs.json")
assert set(frozen) == set(candidate["files"]) and len(frozen) == 5
for path, expected in frozen.items():
    binding(path, expected)
C = parsed(E / "contract.json", "7a354f2fadd869349a9acb04fbdf12ed527312e63eab689bc2c68461362e2c74")
P = parsed("evidence/p2996-tsan-promotion/contract.json", "f9188f06abf5735196e08775c5e84285b0e4139831d053e41b5a3a376ab4bf53")
previous_review = parsed("evidence/p2996-tsan-promotion/artifact-review/review.json", candidate["prior_installed_tsan_review"])
assert previous_review["result"].startswith("PASS") and previous_review["findings"] == []
assert previous_review["contract_sha256"] == sha(binding("evidence/p2996-tsan-promotion/contract.json"))
assert [len(P[k]) for k in ("inputs", "source_inputs", "tools")] == [190, 881, 28]
assert [len(C[k]) for k in ("inputs", "source_inputs", "tools")] == [191, 881, 29]
witness = "dev/toolchains/lsan_witness.cpp"
target = P["target"]
lsan_path = C["lsan_runtime"]["path"]
assert C["inputs"] == P["inputs"] | {witness: frozen[witness]}
assert C["source_inputs"] == P["source_inputs"]
assert C["tools"] == P["tools"] | {target: P["after"]["sha256"], lsan_path: C["lsan_runtime"]["sha256"]}
assert P["tools"][target] == P["before"]["sha256"]
expected = copy.deepcopy(P)
for name in ("target", "before", "after", "replacement", "replacement_identity", "witnesses"):
    del expected[name]
expected.update({
    "base_head": HEAD,
    "scope": "Private P2996 LSan and LSan+UBSan clean, leak and overflow witnesses",
    "inputs": P["inputs"] | {witness: frozen[witness]},
    "tools": P["tools"] | {target: P["after"]["sha256"], lsan_path: C["lsan_runtime"]["sha256"]},
    "lsan_runtime": C["lsan_runtime"],
    "runtime_environment": {
        "LSAN_OPTIONS": "detect_leaks=1:exitcode=86:symbolize=0",
        "UBSAN_OPTIONS": "exitcode=86:abort_on_error=0:symbolize=0:halt_on_error=1",
    },
    "sanitizers": {
        "lsan": {"flags": ["-fsanitize=leak"], "runtimes": ["lib/clang/21/lib/darwin/libclang_rt.lsan_osx_dynamic.dylib"],
                 "errors": {"leak": ["ERROR: LeakSanitizer: detected memory leaks"]}},
        "lsan-ubsan": {"flags": ["-fsanitize=leak,undefined"], "runtimes": ["lib/clang/21/lib/darwin/libclang_rt.lsan_osx_dynamic.dylib"],
                       "errors": {"leak": ["ERROR: LeakSanitizer: detected memory leaks"],
                                  "overflow": ["runtime error: signed integer overflow: 2147483647 + 1 cannot be represented"]}},
    },
    "driver_probe": {name: candidate["evidence"]["driver-probe/" + name]
                     for name in ("summary.json", "lsan.stderr", "lsan-ubsan.stderr")},
})
assert C == expected
checks["contract_derivation"] = {
    "prior_counts": [190, 881, 28], "current_counts": [191, 881, 29],
    "direct_inputs_added": [witness], "prior_direct_inputs_unchanged": True,
    "all_source_input_entries_unchanged": True, "tool_digests_changed": [target],
    "tool_paths_added": [lsan_path], "remaining_fields_match_exact_derivation": True,
    "full_inventory_files_rehashed": False,
}
assert lsan_path == str(Path(C["prefixes"]["p2996"]) / "lib/clang/21/lib/darwin/libclang_rt.lsan_osx_dynamic.dylib")
old_installed = next(row for row in previous_review["artifact_identities"] if row["kind"] == "installed-runtime")
assert old_installed["path"] == target
assert all(old_installed[key] == P["after"][key] for key in ("sha256", "bytes", "mode"))

dependency_paths = [
    "dev/toolchains/p2996_tsan_runtime.py", "dev/toolchains/p2996_asan_runtime.py",
    "dev/toolchains/mise_runtime.py", "dev/toolchains/vcpkg_fmt.py",
    "dev/toolchains/vcpkg_private.py", "dev/toolchains/p2996_sanitizers.py",
    "evidence/p2996-math-resume/operation/p2996_build.py.source",
    C["baseline_qualification"],
]
for name in dependency_paths:
    binding(name, C["inputs"][name])
old_helper = binding("dev/toolchains/p2996_tsan.py").decode()
helper = binding("dev/toolchains/p2996_lsan.py").decode()
tree = ast.parse(helper)
compile(tree, "p2996_lsan.py", "exec")
compile(ast.parse(binding(E / "derive.py.source").decode()), "derive.py.source", "exec")
assert next(n.value.value for n in tree.body if isinstance(n, ast.Assign) and any(
    isinstance(t, ast.Name) and t.id == "CONTRACT_SHA" for t in n.targets)) == sha(binding(E / "contract.json"))

def named(source, name):
    return next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == name)

identical_functions = []
for name in ("save", "run", "source_state", "interrupted"):
    assert ast.dump(named(old_helper, name), include_attributes=False) == ast.dump(named(helper, name), include_attributes=False)
    identical_functions.append(name)
replacements = [
    ('"""Qualify P2996 ThreadSanitizer and combined UBSan reflection witnesses."""',
     '"""Qualify P2996 LeakSanitizer and combined UBSan reflection witnesses."""'),
    ("from p2996_asan_runtime import protected", "from p2996_tsan_runtime import identity, protected"),
    ('EVIDENCE = ROOT / "evidence/p2996-tsan"', 'EVIDENCE = ROOT / "evidence/p2996-lsan"'),
    ('CONTRACT_SHA = "4bb345582c7253694e37b958c77154b5d98ac522e3e89858eac2fb2c2b828ea5"',
     'CONTRACT_SHA = "7a354f2fadd869349a9acb04fbdf12ed527312e63eab689bc2c68461362e2c74"'),
    ('        assert all(digest(Path(row["path"])) == row["sha256"] for rows in data["abi_inputs"].values() for row in rows)\n',
     '        assert all(digest(EVIDENCE / "driver-probe" / name) == sha for name, sha in data["driver_probe"].items())\n'
     '        assert all(digest(Path(row["path"])) == row["sha256"] for rows in data["abi_inputs"].values() for row in rows)\n'
     '        runtime = data["lsan_runtime"]\n'
     '        assert identity(Path(runtime["path"])) == {key: runtime[key] for key in ("sha256", "bytes", "mode")}\n'),
    ('"marketplace-p2996-tsan"', '"marketplace-p2996-lsan"'),
    ('ROOT / "dev/toolchains/tsan_witness.cpp"', 'ROOT / "dev/toolchains/lsan_witness.cpp"'),
    ('("WARNING: ThreadSanitizer", "FATAL: ThreadSanitizer", "runtime error:", "Sanitizer CHECK failed")',
     '("ERROR: LeakSanitizer", "FATAL: LeakSanitizer", "runtime error:", "Sanitizer CHECK failed")'),
    ('assert set(report["cells"]) == {"tsan", "tsan-ubsan"}', 'assert set(report["cells"]) == {"lsan", "lsan-ubsan"}'),
    ('PASS: P2996 TSan and TSan+UBSan clean/error reflection witnesses', 'PASS: P2996 LSan and LSan+UBSan clean/error reflection witnesses'),
]
reconstructed = old_helper
for old, new in replacements:
    assert reconstructed.count(old) == 1, old
    reconstructed = reconstructed.replace(old, new)
assert reconstructed == helper
native_source = binding("evidence/p2996-math-resume/operation/p2996_build.py.source").decode()
native_node = named(native_source, "run")
native_code = compile(ast.Module(body=[native_node], type_ignores=[]), "retained-native-run", "exec")
needed = set()
def code_names(code):
    for ins in dis.get_instructions(code):
        if ins.opname == "LOAD_GLOBAL":
            needed.add(ins.argval)
    for value in code.co_consts:
        if isinstance(value, types.CodeType):
            code_names(value)
code_names(native_code)
imports = set()
for node in tree.body:
    if isinstance(node, ast.Import):
        imports.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        imports.update(alias.asname or alias.name for alias in node.names)
provided = imports | {"directory", "report", "env", "save"} | set(dir(builtins))
assert not needed - provided, sorted(needed - provided)
checks["runner"] = {
    "line_count": len(helper.splitlines()), "witness_line_count": len(binding(witness).decode().splitlines()),
    "python_syntax_compiled_without_execution": True, "parent_functions_executed": [],
    "unchanged_nested_functions": identical_functions, "exact_adaptation_replacements": len(replacements),
    "predecessor_helper_sha256": sha(binding("dev/toolchains/p2996_tsan.py")),
    "native_dynamic_function_nonbuiltin_global_names": sorted(needed - set(dir(builtins))),
    "missing_dynamic_function_globals": [], "native_function_executed": False,
    "diff": "".join(difflib.unified_diff(old_helper.splitlines(True), helper.splitlines(True),
                                        fromfile="p2996_tsan.py", tofile="p2996_lsan.py")),
}

source = Path(C["source_provenance"]["path"])
source_names = [
    "compiler-rt/lib/lsan/lsan.cpp", "compiler-rt/lib/lsan/lsan_common.cpp",
    "compiler-rt/lib/lsan/lsan_flags.inc", "compiler-rt/lib/lsan/lsan_mac.cpp",
    "compiler-rt/lib/lsan/lsan_common_mac.cpp", "compiler-rt/lib/lsan/lsan_common.h",
    "compiler-rt/lib/lsan/lsan_posix.cpp", "compiler-rt/lib/lsan/lsan_interceptors.cpp",
    "compiler-rt/lib/sanitizer_common/sanitizer_flags.inc",
    "compiler-rt/lib/sanitizer_common/sanitizer_termination.cpp",
]
source_metadata = []
for name in source_names:
    path = source / name
    binding(path, C["source_inputs"].get(str(path)))
    source_metadata.append(watched[str(path)] | {"bound_in_contract": str(path) in C["source_inputs"]})
lsan_cpp = binding(source / source_names[0]).decode()
lsan_common = binding(source / "compiler-rt/lib/lsan/lsan_common.cpp").decode()
lsan_interceptors = binding(source / "compiler-rt/lib/lsan/lsan_interceptors.cpp").decode()
lsan_mac = binding(source / "compiler-rt/lib/lsan/lsan_common_mac.cpp").decode()
lsan_posix = binding(source / "compiler-rt/lib/lsan/lsan_posix.cpp").decode()
assert 'RegisterCommonFlags(&parser);' in lsan_cpp
assert 'parser.ParseStringFromEnv("LSAN_OPTIONS");' in lsan_cpp
assert 'cf.detect_leaks = true;' in lsan_cpp and 'cf.exitcode = 23;' in lsan_cpp
assert "void HandleLeaks() {}" in lsan_mac
assert "if (status == 0 && HasReportedLeaks()) status = common_flags()->exitcode;" in lsan_interceptors
assert 'if (common_flags()->detect_leaks && common_flags()->leak_check_at_exit)' in lsan_posix
assert 'Atexit(DoLeakCheck);' in lsan_posix
assert 'has_reported_leaks = CheckForLeaks();' in lsan_common
checks["source_backed_lsan_flags"] = {
    "files": source_metadata,
    "conclusion": "LSAN_OPTIONS registers common flags; enabled at-exit leak check records leaks; Darwin HandleLeaks is empty and _exit interceptor replaces successful exit status with configured exitcode. Runtime behavior remains unexecuted.",
    "source_git_identity_rechecked": False,
    "limit": "These are exact scoped source text observations. Files absent from the inherited 881-entry map were independently hashed here but are not newly added to that contract.",
}

driver_origin = Path("/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-lsan-driver-probe-20261012T043000Z")
driver_pairs = []
for name in ("summary.json", "lsan.stderr", "lsan.stdout", "lsan-ubsan.stderr", "lsan-ubsan.stdout"):
    raw = binding(E / "driver-probe" / name)
    assert binding(driver_origin / name) == raw
    if name.endswith(".stdout"):
        assert raw == b""
    driver_pairs.append({"source": str(driver_origin / name), "copy": str(E / "driver-probe" / name), "sha256": sha(raw)})
probes = parsed(E / "driver-probe/summary.json")
assert [row["case"] for row in probes] == ["lsan", "lsan-ubsan"]
probe_checks = []
for row in probes:
    mode = row["case"]
    expected_argv = [C["compilers"]["p2996"]["CXX"], "-###", "-std=c++26", *C["sanitizers"][mode]["flags"], "-x", "c++", "/dev/null", "-o", "/dev/null"]
    assert row["argv"] == expected_argv and row["returncode"] == 0
    log = binding(E / "driver-probe" / (mode + ".stderr"), row["stderr_sha256"]).decode()
    assert C["source_provenance"]["head"] in log
    command_lines = [shlex.split(line.strip()) for line in log.splitlines() if line.lstrip().startswith('"')]
    assert len(command_lines) == 2
    cc1, link = command_lines
    assert "-cc1" in cc1 and link[0] == "/usr/bin/ld"
    assert lsan_path in link
    dynamic_sanitizers = [arg for arg in link if Path(arg).name.startswith("libclang_rt.") and arg.endswith(".dylib")]
    assert dynamic_sanitizers == [lsan_path]
    sanitizer_flags = next(arg for arg in cc1 if arg.startswith("-fsanitize=")).split("=", 1)[1].split(",")
    assert "leak" in sanitizer_flags
    if mode == "lsan-ubsan":
        assert "signed-integer-overflow" in sanitizer_flags
    assert row["mentions_lsan_runtime"] is True and row["mentions_ubsan_runtime"] is False and row["mentions_asan_runtime"] is False
    probe_checks.append({"case": mode, "reported_returncode": row["returncode"], "dynamic_runtime_paths": dynamic_sanitizers,
                         "cc1_sanitizers": sanitizer_flags, "default_probe_triple": cc1[cc1.index("-triple") + 1]})
checks["driver_probe"] = {"copies": driver_pairs, "cases": probe_checks,
                          "reviewer_reexecuted_driver": False,
                          "limit": "Stored -### output and reported rc 0 establish retained driver-selection evidence only; no compile/link/witness execution, timing or PID independently reconstructed."}

cache = parsed(C["baseline_qualification"])["cells"]["p2996-core-static-fmt-static"]["cache"]
prefix = Path(C["prefixes"]["p2996"])
virtual = Path("/REVIEW_STATIC_PATH_ONLY/task14c")
libs = [str(prefix / "lib" / name) for name in ("libc++.dylib", "libc++abi.dylib", "libunwind.dylib")]
sandbox = ["/usr/bin/sandbox-exec", "-f", str(virtual / "private.sb")]
compiler = sandbox + [C["compilers"]["p2996"]["CXX"], *shlex.split(cache["CMAKE_CXX_FLAGS"]),
                      "-isysroot", cache["CMAKE_OSX_SYSROOT"], "-mmacosx-version-min=" + cache["CMAKE_OSX_DEPLOYMENT_TARGET"],
                      "-arch", "arm64", "-std=c++26", "-O1", "-g", "-fno-omit-frame-pointer", "-fno-optimize-sibling-calls",
                      "-I", str(ROOT / "include"), "-pedantic-errors", "-Wall", "-Wextra", "-Werror"]
assert "-freflection" not in compiler
assert "--no-default-config" in compiler and "-nostdinc++" in compiler
plans = {}
for mode, settings in C["sanitizers"].items():
    obj, binary = str(virtual / mode / "core.o"), str(virtual / mode / "witness")
    plans[mode] = {
        "core_argv": compiler + settings["flags"] + ["-freflection", "-c", str(ROOT / "src/core.cpp"), "-o", obj],
        "link_argv": compiler + settings["flags"] + [str(ROOT / witness), obj, "-nostdlib++", *libs, "-Wl,-rpath," + str(prefix / "lib"), "-o", binary],
        "cases": {"clean": 0} | {name: 86 for name in settings["errors"]},
        "runtime_environment": C["runtime_environment"],
    }
    assert "-freflection" not in plans[mode]["link_argv"]
assert sum(len(plan["cases"]) for plan in plans.values()) == 5
checks["static_argument_plans"] = {"virtual_root": str(virtual), "executed": False, "modes": plans}
static = parsed(E / "pre-review-static.json")
assert static["base_head"] == HEAD and len(static["checks"]) == 5
assert all(row["returncode"] == 0 for row in static["checks"])
assert next(row for row in static["checks"] if row["command"].endswith("check:acceptance-baseline"))["original_hashes"] == 19
checks["parent_static_receipt"] = {"sha256": sha(binding(E / "pre-review-static.json")), "reported_checks": static["checks"], "reviewer_reran_checks": False}

scan = parsed(E / "pre-review-secret-scan.json")
assert len(scan["files"]) == 15
for name, expected in scan["files"].items():
    binding(name, expected)
assert set(frozen) <= set(scan["files"])
assert set("evidence/p2996-lsan/" + name for name in candidate["evidence"]) <= set(scan["files"])
assert scan["raw_returncode"] == 1 and scan["transformed_returncode"] == 0 and scan["complete_token_files"] == []
assert scan["transformed_report_sha256"] == sha(b"[]\n")
assert len(scan["dispositions"]) == 6
known_hashes = {str(ROOT / p): h for p, h in C["inputs"].items()} | C["source_inputs"] | C["tools"]
dispositions = []
for row in scan["dispositions"]:
    assert known_hashes.get(row["path"]) == row["sha256"], row["path"]
    assert row["rule"] == "generic-api-key"
    dispositions.append({"path": row["path"], "sha256": row["sha256"], "matches_inherited_contract_entry": True,
                         "disposition_target_read": row["path"] in watched})
checks["secret_scan_receipt"] = {
    "sha256": sha(binding(E / "pre-review-secret-scan.json")), "bound_files": 15,
    "reported_raw_returncode": 1, "reported_transformed_returncode": 0,
    "reported_complete_token_files": [], "reported_dispositions": dispositions,
    "script_sha256_recorded": scan["script_sha256"],
    "scan_rerun": False, "raw_or_transformed_report_files_read": False, "scanner_script_read": False,
    "limit": "Only the supplied receipt and its 15 text-file bindings were verified. Six digest dispositions match inherited contract metadata; SDK/object/source disposition targets were not rehashed. Scanner execution and raw reports were not re-audited.",
}

git_results = []
for argv, expected in [
    (["/usr/bin/git", "-C", str(ROOT), "rev-parse", "--show-toplevel"], str(ROOT)),
    (["/usr/bin/git", "-C", str(ROOT), "branch", "--show-current"], BRANCH),
    (["/usr/bin/git", "-C", str(ROOT), "rev-parse", "HEAD"], HEAD),
    (["/usr/bin/git", "-C", str(ROOT), "rev-parse", "--git-common-dir"], COMMON),
]:
    result = subprocess.run(argv, capture_output=True, text=True, timeout=5, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    assert result.returncode == 0 and result.stdout.strip() == expected and not result.stderr
    git_results.append({"argv": argv, "returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr})
checks["final_git_identity"] = git_results
for path, raw in contents.items():
    assert Path(path).read_bytes() == raw, "Frozen text changed: " + path
checks["frozen_texts_stable"] = True

# Exact two named installed runtime reads occur last, once each.
artifacts = []
for kind, path_string, expected_identity in [
    ("installed-lsan", lsan_path, {k: C["lsan_runtime"][k] for k in ("sha256", "bytes", "mode")}),
    ("installed-tsan", target, P["after"]),
]:
    path = Path(path_string)
    assert path.is_absolute() and path == path.resolve(strict=True)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_uid == os.geteuid()
    assert before.st_size == expected_identity["bytes"] and before.st_size <= 2 * 1024 * 1024
    raw = path.read_bytes()
    after = path.lstat()
    fields = ("st_dev", "st_ino", "st_size", "st_mode", "st_nlink", "st_uid", "st_mtime_ns", "st_ctime_ns")
    assert all(getattr(before, field) == getattr(after, field) for field in fields)
    observed = {"sha256": sha(raw), "bytes": len(raw), "mode": oct(stat.S_IMODE(after.st_mode))}
    assert observed == expected_identity
    header = struct.unpack_from("<8I", raw)
    assert header[0] == 0xFEEDFACF and header[1] == 0x0100000C and header[3] == 6
    offset = 32
    uuids = []
    for _ in range(header[4]):
        command, size = struct.unpack_from("<II", raw, offset)
        assert size >= 8 and offset + size <= 32 + header[5]
        if command == 0x1B:
            assert size == 24
            uuids.append(str(uuid.UUID(bytes=raw[offset + 8:offset + 24])).upper())
        offset += size
    assert offset == 32 + header[5]
    artifacts.append({"kind": kind, "path": path_string, **observed, "reads": 1, "mach_o_cpu": "arm64",
                      "mach_o_type": 6, "uuid": uuids, "stable_canonical_owned_regular_single_link": True})
result = {
    "result": "PASS: bounded Task 14c preparation comparisons",
    "recorded_at": datetime.now(timezone.utc).isoformat(),
    "checkout": str(ROOT), "branch": BRANCH, "head": HEAD, "git_common_dir": COMMON,
    "candidate_sha256": sha(binding(E / "candidate.json")),
    "helper_sha256": frozen["dev/toolchains/p2996_lsan.py"],
    "contract_sha256": sha(binding(E / "contract.json")),
    "checks": checks, "watched_text_count": len(watched), "watched_texts": list(watched.values()),
    "artifacts": artifacts, "artifact_bytes_read": sum(row["bytes"] for row in artifacts),
    "reviewer_python": sys.executable, "native_commands_executed": False,
}
(OUT / "comparison.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({"result": result["result"], "watched_texts": len(watched), "artifacts": len(artifacts),
                  "artifact_bytes_read": result["artifact_bytes_read"], "git_returncodes": [r["returncode"] for r in git_results]}))
