import ast, hashlib, json, os, signal, subprocess, time
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
directory=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
proof=load(directory/'source-verification.json')
runner=R/'evidence/p2996-math-resume/operation/p2996_build.py.source'
assert sha(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
env=os.environ.copy()
for key in ['GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:env.pop(key,None)
env.update(MARKETPLACE_MISE_BIN='/Users/rmanaloto/.local/bin/mise',MARKETPLACE_PYTHON='/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3',PYTHONDONTWRITEBYTECODE='1',MISE_OFFLINE='1',MISE_AUTO_INSTALL='0',MISE_EXEC_AUTO_INSTALL='0',GIT_OPTIONAL_LOCKS='0')
report={'state':'running','commands':[],'scope':'Source/static checks only; no CMake/compiler/configure/build invocation','started_at':datetime.now(timezone.utc).isoformat()}
def save():(directory/'static-checks.json').write_text(json.dumps(report,indent=2)+'\n')
node=next(n for n in ast.walk(ast.parse(runner.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='run')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(runner),'exec'),globals())
(directory/'cwd').mkdir()
def unchanged():
 for name,r in proof['maintained_final_files'].items():assert sha(R/name)==r['sha256'],name
 for r in proof['source_references']+proof['prerequisites']:assert sha(Path(r['path']))==r['sha256'],r['path']
 assert sha(Path(proof['source_contract']['path']))==proof['source_contract']['sha256']
try:
 unchanged()
 run('tasks-validate',[R/'dev/mise','tasks','validate'])
 output=run('acceptance-baseline',[R/'dev/mise','run','check:acceptance-baseline'])
 counts=json.loads(next(line for line in output.splitlines() if line.startswith('{')))
 assert counts['status']=='pass' and counts['checks']['baseline']==19
 report['static_counts']=counts['checks']
 status=run('root-status',['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',R,'status','--porcelain','--untracked-files=normal'])
 allowed={'.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','cmake/toolchains/p2996-macos-arm64.cmake','scratch/p2996-toolchain/','evidence/p2996-cmake-preparation/'}
 assert all(line[3:] in allowed for line in status.splitlines())
 report['root_status_within_unit']=True
 unchanged()
 report['all_maintained_and_referenced_sources_unchanged']=True
 report['state']='PASS: permitted static checks and original acceptance baseline'
except BaseException as error:
 report.update(state='FAIL',error=repr(error));raise
finally:
 report['finished_at']=datetime.now(timezone.utc).isoformat();save()
print(json.dumps({'state':report['state'],'exits':{c['case']:c['returncode'] for c in report['commands']},'counts':report.get('static_counts')}))
