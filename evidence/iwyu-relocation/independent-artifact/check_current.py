from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

D = Path(__file__).resolve().parent
R = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = R / 'evidence/iwyu-relocation'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
record_hash = lambda rows: hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert sha(R/'dev/toolchains/mise_runtime.py') == '8c22ca727824fa10cd2cf6f7a08b8499c33f0e82245c9d93cd871f1ff26d728f'
frozen = load(D/'frozen-inputs.json')
for path,row in frozen['files'].items():
    assert sha(R/path) == row['sha256'],path
def forbidden(*args,**kwargs):
    raise RuntimeError('Native child processes forbidden during preservation check')
subprocess.Popen = subprocess.run = forbidden
sys.path.insert(0,str(R/'dev/toolchains'))
import mise_runtime
started = datetime.now(timezone.utc).isoformat()
clock = time.monotonic()
current = mise_runtime.protected()
q = load(E/'operation/qualification.json')
recipe = load(R/'evidence/iwyu-reflection/source-recipe.json')
built = load(R/'evidence/iwyu-build/operation/qualification.json')['installed']
moved = Path(q['moved_prefix'])
assert str(moved) == '/Users/rmanaloto/.local/state/marketplace-tool-foundation/iwyu-relocation-20261011T162018Z/relocation/moved'
scopes = [(moved,q['moved_inventory'],350),
          (moved/'lib/clang/21',q['original_resource_inventory'],320),
          (moved.parent.parent/'fixtures',q['final_fixture'],5),
          (Path(recipe['bindings']['IWYU_PREFIX']),built['inventory'],27)]
assert recipe['bindings']['IWYU_PREFIX'] == built['prefix']
results = []
for path,expected,count in scopes:
    observed = mise_runtime.prefix_inventory(path)
    assert observed == expected and len(observed) == count,str(path)
    results.append({'path':str(path),'entries':count,'canonical_inventory_sha256':record_hash(observed),'result':'PASS'})
assert not os.path.lexists(moved.parent/'staging')
for path,row in frozen['files'].items():
    assert sha(R/path) == row['sha256'],path
report = {'result':'PASS','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
          'elapsed_seconds':time.monotonic()-clock,'protected_invocations':1,
          'protected_function':{'path':str(R/'dev/toolchains/mise_runtime.py'),'sha256':sha(R/'dev/toolchains/mise_runtime.py')},
          'current_mise':current,'scoped_inventory_comparisons':results,'staging_absent':True,
          'frozen_files_unchanged':len(frozen['files']),'native_child_processes':0,
          'full_protected_snapshot_copied':False,'prior_test_batteries_rerun':False}
(D/'current-preservation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':'PASS','protected_invocations':1,'scoped_inventory_entries':[r['entries'] for r in results],
                  'staging_absent':True,'native_child_processes':0}))
