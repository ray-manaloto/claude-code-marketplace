from pathlib import Path
import ast
import hashlib
import json
import os
import sys
from types import SimpleNamespace

os.umask(0o077)
ROOT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
BASE = Path("/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-registration-review-20261011T095924768311Z")
HELPER = ROOT / "dev/toolchains/p2996_register.py"
EXPECTED = "f8bdee61f82f8c598a31c87d86163d3bf6ea97e8beccc810a9aa06b919be6263"
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(HELPER) == EXPECTED
tree = ast.parse(HELPER.read_text())

def at(line, kind):
    return next(n for n in ast.walk(tree) if isinstance(n, kind) and n.lineno == line)

def compile_nodes(nodes, path=HELPER):
    return compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(path), "exec")

protected_node = at(65, ast.FunctionDef)
apply_node = at(153, ast.If)
path_node = at(36, ast.If)
review_node = at(94, ast.Assert)
dependency_node = at(108, ast.Assert)
common = {"Path": Path, "os": os, "digest": digest}
extracted = []
for name, function in [("mise_link_probe.py", "snapshot"), ("vcpkg_register.py", "install_entries"), ("p2996_install.py", "prefix_inventory")]:
    path = ROOT / "dev/toolchains" / name
    node = next(n for n in ast.parse(path.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == function)
    exec(compile_nodes([node], path), common)
    extracted.append({"path": str(path), "file_sha256": digest(path), "function": function, "lines": [node.lineno, node.end_lineno], "ast_sha256": hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()})

class ReachedPromotion(Exception):
    pass

class RunPathRejected(Exception):
    pass

class Parser:
    def error(self, message):
        raise RunPathRejected(message)

fixtures = BASE / "guard-fixtures"
fixtures.mkdir()
cases = []
def fixture(name):
    home = fixtures / name
    home.mkdir()
    source = home / "source"
    source.mkdir()
    source_file = source / "tracked.cpp"
    source_file.write_text("source baseline\n")
    workspace = home / "workspace"
    workspace.mkdir()
    prefix = workspace / "prefix"
    prefix.mkdir()
    payload = prefix / "payload"
    payload.write_text("runtime baseline\n")
    installs = home / "fake-global-installs"
    installs.mkdir()
    destination = installs / "asdf-clang-p2996"
    namespace = home / "stage" / "asdf-clang-p2996"
    namespace.mkdir(parents=True)
    version = "fixture-version"
    (namespace / version).symlink_to(prefix)
    directory = home / "run"
    evidence = home / "evidence"
    evidence.mkdir()
    installed = home / "installed-evidence"
    (installed / "operation").mkdir(parents=True)
    (installed / "operation" / "prefix-inventory.json").write_text(json.dumps(common["prefix_inventory"](prefix)))
    row = {"path": str(source_file), "lexists": True, "exists": True,
           "lstat_mode": oct(source_file.lstat().st_mode & 0o777),
           "resolved_path": str(source_file.resolve()), "mode": oct(source_file.stat().st_mode & 0o777),
           "sha256": digest(source_file), "bytes": source_file.stat().st_size, "symlink_target": None}
    report = {"promoted": False, "promotion_attempted": False,
              "proposal": {"destination": str(destination), "preimage": "absent", "prefix": str(prefix),
                           "namespace": common["snapshot"](namespace)}}
    preparation = {"result": "PASS fixture", "findings": [], "helper_sha256": EXPECTED, "proposal": report["proposal"]}
    preparation_file = evidence / "preparation-review.json"
    preparation_file.write_text(json.dumps(preparation))
    admission = {"helper_sha256": EXPECTED, "review_sha256": digest(preparation_file),
                 "proposal": report["proposal"], "run_directory": str(directory)}
    admission_file = evidence / "admission.json"
    admission_file.write_text(json.dumps(admission))
    events = []
    def load(path):
        assert Path(path).is_relative_to(home), "fixture attempted a nonprivate JSON read"
        return json.loads(Path(path).read_text())
    def census(strict=True):
        events.append({"event": "census", "strict": strict})
        return {"blockers": []}
    def promote(src, dst):
        assert Path(src).is_relative_to(home) and Path(dst).is_relative_to(home)
        events.append({"event": "promotion_stub", "source": str(src), "destination": str(dst)})
        raise ReachedPromotion("promotion boundary reached; no rename performed")
    def preserved(value):
        assert value == {}
    scope = common | {"__file__": str(HELPER), "args": SimpleNamespace(apply=True),
        "directory": directory, "protected_roots": (home / "project", workspace, source, home / "fake-config", installs),
        "parser": Parser(), "baseline": {"protected": {}, "directories": {}, "install_entries": {}},
        "inventory": {"records": [row]}, "installs": installs, "destination": destination, "prefix": prefix,
        "installed": installed, "report": report, "load": load, "evidence": evidence, "namespace": namespace,
        "preserved": preserved, "census": census, "promote": promote, "save": lambda: events.append({"event": "save"}),
        "env": {}, "source_file": source_file, "payload": payload, "version": version,
        "events": events, "preparation_file": preparation_file, "admission_file": admission_file, "home": home}
    exec(compile_nodes([protected_node]), scope)
    return scope

def change_json(path, key, value):
    d = json.loads(path.read_text())
    d[key] = value
    path.write_text(json.dumps(d))

def execute_case(name, node, expected_line, mutate=None, positive=False):
    scope = fixture(name)
    if mutate:
        mutate(scope)
    error = None
    helper_lines = []
    try:
        exec(compile_nodes([node]), scope)
    except (AssertionError, ReachedPromotion, RunPathRejected) as caught:
        error = caught
        tb = caught.__traceback__
        while tb:
            if tb.tb_frame.f_code.co_filename == str(HELPER):
                helper_lines.append(tb.tb_lineno)
            tb = tb.tb_next
    promotions = [e for e in scope["events"] if e["event"] == "promotion_stub"]
    accepted = isinstance(error, ReachedPromotion) if positive else isinstance(error, (AssertionError, RunPathRejected)) and not promotions
    ok = accepted and expected_line in helper_lines
    cases.append({"case": name, "result": "PASS" if ok else "FAIL", "expected_helper_line": expected_line,
                  "observed_helper_lines": helper_lines, "exception_type": type(error).__name__ if error else None,
                  "promotion_stub_calls": len(promotions), "events": scope["events"], "real_promotion_performed": False})

execute_case("valid_admission_reaches_stubbed_boundary", apply_node, 167, positive=True)
execute_case("relative_run_directory_rejected", path_node, 38, lambda s: s.update(directory=Path("relative-run")))
execute_case("protected_run_directory_rejected", path_node, 38, lambda s: s.update(directory=s["prefix"] / "run"))
execute_case("occupied_destination_rejected", apply_node, 74, lambda s: s["destination"].mkdir())
def wrong_reflection(s):
    s["reflected"] = s["home"] / "reflected"
    s["reflected"].mkdir()
    (s["reflected"] / "reflection-review.json").write_text('{"tampered":true}\n')
execute_case("wrong_reflection_review_digest_rejected", review_node, 94, wrong_reflection)
execute_case("dependency_helper_drift_rejected", dependency_node, 108, lambda s: s.update(dependencies={"vcpkg_register.py": "0" * 64}))
execute_case("wrong_admission_helper_rejected", apply_node, 156, lambda s: change_json(s["admission_file"], "helper_sha256", "0" * 64))
execute_case("wrong_preparation_review_binding_rejected", apply_node, 157, lambda s: change_json(s["admission_file"], "review_sha256", "0" * 64))
execute_case("wrong_admission_proposal_rejected", apply_node, 159, lambda s: change_json(s["admission_file"], "proposal", {"wrong": True}))
def wrong_preparation(s):
    change_json(s["preparation_file"], "findings", [{"id": "unresolved-fixture"}])
    change_json(s["admission_file"], "review_sha256", digest(s["preparation_file"]))
execute_case("unresolved_preparation_review_rejected", apply_node, 158, wrong_preparation)
execute_case("wrong_admission_run_directory_rejected", apply_node, 160, lambda s: change_json(s["admission_file"], "run_directory", str(s["home"] / "different-run")))
execute_case("retained_source_drift_before_promotion_rejected", apply_node, 84, lambda s: s["source_file"].write_text("changed source\n"))
execute_case("complete_prefix_drift_before_promotion_rejected", apply_node, 86, lambda s: s["payload"].write_text("changed runtime\n"))
def blocked_census(s):
    def census(strict=True):
        s["events"].append({"event": "census", "strict": strict, "controlled_blocker": True})
        raise AssertionError("controlled concurrent writer")
    s["census"] = census
execute_case("immediate_writer_census_failure_rejected", apply_node, 161, blocked_census)
def namespace_drift(s):
    link = s["namespace"] / s["version"]
    link.unlink()
    link.symlink_to(s["home"] / "wrong-prefix")
execute_case("staged_namespace_drift_before_promotion_rejected", apply_node, 164, namespace_drift)
def unexpected_promoted(s):
    s["report"]["promoted"] = True
    s["destination"].mkdir()
    (s["destination"] / "unexpected-version").symlink_to(s["prefix"])
execute_case("unexpected_promoted_namespace_rejected", apply_node, 71, unexpected_promoted)
assert len(cases) == 16
assert digest(HELPER) == EXPECTED
result = {"result": "PASS" if all(c["result"] == "PASS" for c in cases) else "FAIL",
          "helper": str(HELPER), "helper_sha256": EXPECTED, "case_count": len(cases), "cases": cases,
          "method": "Exact AST nodes/functions from the frozen helper with private filesystem fixtures. A recording promotion stub prevents all rename calls; a controlled census failure checks the new call site's rejection path. Existing generic rename/census/cleanup suites are reused by exact source identity.",
          "extracted_support_functions": extracted,
          "helper_guard_sources": [{"kind": type(n).__name__, "lines": [n.lineno, n.end_lineno],
             "ast_sha256": hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest()}
             for n in [protected_node, apply_node, path_node, review_node, dependency_node]],
          "global_paths_mutated": [], "fixture_root": str(fixtures), "native_commands_executed_by_fixtures": []}
output = BASE / "guard-controls.json"
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"result": result["result"], "case_count": len(cases), "failed_cases": [c for c in cases if c["result"] != "PASS"], "path": str(output), "sha256": digest(output)}))
sys.exit(0 if result["result"] == "PASS" else 1)
