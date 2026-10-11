import ast, hashlib, json, os, shutil, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
directory=Path(__file__).resolve().parent
os.umask(0o077);sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import read
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size}
def load(p):return json.loads(p.read_text())
def write(name,data):
    p=directory/name;p.write_text(json.dumps(data,indent=2)+'\n');return p
E=ROOT/'evidence/core-p2996-preparation'
contract=load(E/'source-contract.json')
assert digest(E/'source-contract.json')=='e36c9a1567d6a89249856a49bccc284d63275efa811b96f4a039d8814e790a3e'
assert digest(E/'cmake-postcommit.json')=='6f4187d284f483657d4cb4bd410086e6d563d93a8398eb30a685f1f3b44b2932'
postcommit=load(E/'cmake-postcommit.json')
assert postcommit['head']=='df5c430f6a34da5a565b675a0bc2a42b889ba620' and postcommit['commit']['returncode']==postcommit['baseline']['returncode']==0 and postcommit['status']==''
assert digest(ROOT/'evidence/p2996-cmake/cmake-review.json')=='7f40d3b4e57d3b12760e7bb7a162c3c039ed9a84e2d0c610ae985d0ebc8c985c'
prior=load(ROOT/'evidence/p2996-cmake/cmake-review.json');assert prior['result'].startswith('PASS') and not prior['findings']
for row in load(E/'preparation-static-checks.json')['commands']:assert row['returncode']==0
verification=load(E/'source-verification.json');assert verification['proposal_sha256']==digest(E/'source-contract.json')
originals={c['absolute_path']:c['original_content'] for c in contract['candidates']}
for c in contract['candidates']:
    assert hashlib.sha256(c['original_content'].encode()).hexdigest()==c['original_sha256']
    assert digest(Path(c['absolute_path']))==c['candidate_sha256']
    assert Path(c['absolute_path']).read_text()==c['content'] and len(c['content'].splitlines())==c['candidate_lines']
reference_records=[];source_excerpts=[]
for row in contract['primary_references']:
    text=originals[row['path']] if row['path'] in originals else Path(row['path']).read_text()
    assert hashlib.sha256(text.encode()).hexdigest()==row['sha256']
    lines=text.splitlines();excerpts=['\n'.join(str(n)+': '+lines[n-1] for n in range(a,b+1)) for a,b in row['line_ranges']]
    assert excerpts==row['excerpts']
    reference_records.append({'path':row['path'],'sha256':row['sha256'],'line_ranges':row['line_ranges'],'reference_kind':'preserved original' if row['path'] in originals else 'live file','excerpts_match':True})
    source_excerpts.append(row['path']+'\n'+row['supports']+'\n'+'\n'.join(excerpts))
assert len(reference_records)==19
for row in contract['read_bindings']:
    text=originals[row['path']] if row['path'] in originals else Path(row['path']).read_text()
    assert hashlib.sha256(text.encode()).hexdigest()==row['sha256']
assert len(contract['read_bindings'])==24
(directory/'source-excerpts.txt').write_text('\n\n'.join(source_excerpts)+'\n')
header=ROOT/'include/aggregated_research/core.hpp'
assert digest(header)=='b16a797742ea349d9116a87bc253fb05158c5fc4836d1a2d8058205d085b210a'
maintained=['CMakeLists.txt','src/core.cpp','src/smoke.cpp','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
before={p:digest(ROOT/p) for p in maintained}
controls=[E/n for n in ['source-contract.json','source-verification.json','cmake-postcommit.json','preparation-static-checks.json']]+[header,ROOT/'AGENTS.md']
cmake_docs=Path('/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/share/cmake-4.4/Help')
extras=[cmake_docs/'prop_test/PASS_REGULAR_EXPRESSION.rst',cmake_docs/'prop_tgt/CXX_SCAN_FOR_MODULES.rst',cmake_docs/'command/target_compile_options.rst',ROOT/'cmake/toolchains/gcc16-macos-arm64.cmake',ROOT/'dev/mise']
control_hashes={str(p):digest(p) for p in controls+extras}
normal=read('install-preimages.json')['normal_environment']['argv']
configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
env=load(Path(normal[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','PYTHONDONTWRITEBYTECODE':'1','MARKETPLACE_MISE_BIN':configuration['mise']['path'],'MARKETPLACE_PYTHON':'/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3'}
for key in ['GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:env.pop(key,None)
assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'primary_references':reference_records,'read_bindings_verified':24,'maintained_hashes_before':before,'control_hashes':control_hashes}
def save():write('static-checks.json',report)
runner=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source'
assert digest(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
node=next(n for n in ast.walk(ast.parse(runner.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='run')
scope=globals()|{'env':env,'save':save,'directory':directory,'report':report}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(runner),'exec'),scope);run=scope['run']
def interrupted(signum,frame):raise KeyboardInterrupt('received signal '+str(signum))
for signum in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(signum,interrupted)
git=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',ROOT]
try:
    ids=run('identity',git+['rev-parse','--show-toplevel','--git-common-dir','HEAD']).splitlines()
    branch=run('branch',git+['symbolic-ref','--short','HEAD']).strip()
    assert ids==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git','df5c430f6a34da5a565b675a0bc2a42b889ba620'] and branch=='codex/marketplace-native-onboarding'
    report['identity']={'root':ids[0],'common_git_directory':ids[1],'head':ids[2],'branch':branch}
    for index,c in enumerate(contract['candidates']):
        text=run('original-'+str(index),git+['show','HEAD:'+c['path']])
        assert text==c['original_content']
    report['all_original_source_bytes_match_current_git_head']=True
    assert set(run('changed-files',git+['diff','--name-only']).splitlines())==set(maintained)
    run('source-diff',git+['diff','--',*maintained])
    run('tasks-validate',[ROOT/'dev/mise','tasks','validate'],timeout=45)
    text=run('acceptance-baseline',[ROOT/'dev/mise','run','check:acceptance-baseline'],timeout=45)
    checks=json.loads(next(line for line in text.splitlines() if line.startswith('{')))
    assert checks['status']=='pass' and checks['checks']['baseline']==19
    report['static_counts']=checks['checks']
    status=run('status',git+['status','--porcelain','--untracked-files=normal'])
    assert set(line[3:] for line in status.splitlines() if not line.startswith('?? '))==set(maintained)
    assert [line for line in status.splitlines() if line.startswith('?? ')]==['?? evidence/core-p2996-preparation/']
    report['status']=status
    assert {p:digest(ROOT/p) for p in maintained}==before
    assert {p:digest(Path(p)) for p in control_hashes}==control_hashes
    for row in contract['read_bindings']:
        text=originals[row['path']] if row['path'] in originals else Path(row['path']).read_text()
        assert hashlib.sha256(text.encode()).hexdigest()==row['sha256']
    report.update(state='PASS: 03b1 source bindings and lightweight static checks',all_maintained_control_and_reference_hashes_unchanged=True)
except BaseException as error:
    report.update(state='FAIL',error=repr(error));raise
finally:
    report['finished_at']=datetime.now(timezone.utc).isoformat();save()
print(json.dumps({'state':report['state'],'commands':len(report['commands']),'exits':{r['case']:r['returncode'] for r in report['commands']},'static_counts':report.get('static_counts'),'directory':str(directory)}),flush=True)
