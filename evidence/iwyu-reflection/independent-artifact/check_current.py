"""One read-only current protected() call and two scoped inventory comparisons."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
D=Path(__file__).resolve().parent
ROOT=Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
E=ROOT/"evidence/iwyu-reflection"
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
frozen=load(D/"frozen-inputs.json")
for rel,row in frozen["files"].items():assert digest(ROOT/rel)==row["sha256"],rel
module_path=ROOT/"dev/toolchains/mise_runtime.py"
assert digest(module_path)=="9220bb5bd18d6af5fc6c6c5a46ae5845b9b1d1687e0212cf66b02bc6d049e92c"
def forbidden(*args,**kwargs):
    raise AssertionError("Native child processes are forbidden in this current-state check")
subprocess.Popen=forbidden
subprocess.run=forbidden
sys.path.insert(0,str(module_path.parent))
spec=importlib.util.spec_from_file_location("current_mise_runtime_for_09c1_review",module_path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
started=datetime.now(timezone.utc).isoformat()
t=time.monotonic()
current=module.protected()
protected_seconds=time.monotonic()-t
built=load(ROOT/"evidence/iwyu-build/operation/qualification.json")
installed=module.prefix_inventory(Path(built["installed"]["prefix"]))
assert len(installed)==27 and installed==built["installed"]["inventory"]
admission=load(E/"admission.json")
operation=load(E/"operation/qualification.json")
fixture=Path(admission["run_directory"])/"fixtures/reflection"
actual=module.prefix_inventory(fixture)
assert len(actual)==23 and actual==operation["final_fixture"]
runtime_review=load(ROOT/"evidence/mise-runtime/runtime-review.json")
assert current==runtime_review["current_mise"]
for rel,row in frozen["files"].items():assert digest(ROOT/rel)==row["sha256"],rel
result={"result":"PASS","started_at":started,"completed_at":datetime.now(timezone.utc).isoformat(),
 "protected_invocations":1,"protected_elapsed_seconds":protected_seconds,"current_mise":current,
 "iwyu_install_inventory_entries":len(installed),"iwyu_install_inventory_matches_committed_operation":True,
 "fixture_inventory_entries":len(actual),"fixture_inventory_matches_current_operation":True,
 "scoped_files_unchanged":True,"native_children":0,"native_profiles":0,"lease_invocations":0,
 "guard_source":{"path":str(module_path),"sha256":digest(module_path)},
 "installation_receipt":{"path":str(ROOT/"evidence/iwyu-build/operation/qualification.json"),"sha256":digest(ROOT/"evidence/iwyu-build/operation/qualification.json")},
 "current_operation_sha256":digest(E/"operation/qualification.json")}
(D/"current-preservation.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))

