import ast,copy,hashlib,json,os,shutil,signal,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=ROOT/'evidence/core-command-preparation';directory=Path(__file__).parent
sys.dont_write_bytecode=True;os.umask(0o077);sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import read
from core_commands import CoreCommands,CONFIGS
PYTHON='/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p):return {'path':str(p),'sha256':digest(p),'bytes':Path(p).stat().st_size}
def load(p):return json.loads(Path(p).read_text())
def write(name,data):(directory/name).write_text(json.dumps(data,indent=2)+'\n')
expected='9c1cdf78f5102a1256a71e965fd3bf9f2b2461f1d6e509fb723301e4b92565d6';helper=ROOT/'dev/toolchains/core_commands.py'
assert digest(helper)==expected and len(helper.read_text().splitlines())==187
old=helper.read_text().replace('            assert args.count("-isystem") == 1\n','')
assert hashlib.sha256(old.encode()).hexdigest()=='68dc847b1ebef3b207f6daec167874605ea0323e4e3dcb2c36ba9d84e5b915f1'
(directory/'initial-core_commands.py.source').write_text(old);(directory/'final-core_commands.py.source').write_bytes(helper.read_bytes())
contract=load(E/'harness-contract.json');parent=load(E/'final-replay/replay.json')
assert digest(E/'harness-contract.json')=='feb0f9700b7ed6828334fb39c6e6d631c87b9be74f4fb9334cdd063b92ecfec8'
assert digest(E/'final-replay/replay.json')=='8fc6ce75860e6478a3865bc300494e9d39f681c1fd6fb1f19a1f1964a76b554f'
refs=contract['prerequisite_references']+contract['selected_recorded_log_references']+parent['inputs']
for row in refs:assert digest(Path(row['path']))==row['sha256']
final_copies=[]
for row in load(E/'final-replay-manifest.json')['files']:
 for key in ['source','path']:
  p=Path(row[key]);assert digest(p)==row['sha256'] and p.stat().st_size==row['bytes'];final_copies.append(record(p))
maintained=['dev/toolchains/core_commands.py','docs/core-qualification.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
before={p:digest(ROOT/p) for p in maintained}
controls=[ROOT/p for p in ['AGENTS.md','docs/accepted-decisions.md','dev/mise','mise.dev.toml','dev/check.py','evidence/core-p2996-preparation/preparation-review.json','evidence/core-command-preparation/harness-contract.json','evidence/core-command-preparation/final-replay/replay.json','evidence/core-command-preparation/final-replay/replay.py.source','evidence/core-command-preparation/final-replay-manifest.json']]
control_hashes={str(p):digest(p) for p in controls}
normal=read('install-preimages.json')['normal_environment']['argv']
configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
env=load(Path(normal[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','PYTHONDONTWRITEBYTECODE':'1','MARKETPLACE_MISE_BIN':configuration['mise']['path'],'MARKETPLACE_PYTHON':PYTHON}
for key in ['GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:env.pop(key,None)
assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'maintained_hashes_before':before,'control_hashes':control_hashes,'reference_records_verified':len(refs),'unique_references_verified':len({r['path'] for r in refs}),'final_replay_copies':final_copies,'synthetic_archive_cases':[],'focused_rejections':[]}
def save():write('static-checks.json',report)
runner=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source'
assert digest(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
node=next(n for n in ast.walk(ast.parse(runner.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='run')
scope=globals()|{'env':env,'save':save,'directory':directory,'report':report}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(runner),'exec'),scope);run=scope['run']
def interrupted(signum,frame):raise KeyboardInterrupt('received signal '+str(signum))
for signum in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(signum,interrupted)
git=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',ROOT]
def reject(label,operation):
 try:operation()
 except AssertionError:report['focused_rejections'].append(label)
 else:raise AssertionError('mutation accepted: '+label)
try:
 ids=run('identity',git+['rev-parse','--show-toplevel','--git-common-dir','HEAD']).splitlines();branch=run('branch',git+['symbolic-ref','--short','HEAD']).strip()
 assert ids==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git','fd7c9cdf54ddf702c0e48348302d73cc6853346b'] and branch=='codex/marketplace-native-onboarding'
 report['identity']={'root':ids[0],'common_git_directory':ids[1],'head':ids[2],'branch':branch}
 assert set(run('changed-files',git+['diff','--name-only']).splitlines())==set(maintained[2:])
 run('source-diff',git+['diff','--',*maintained])
 replay_dir=directory/'exact-final-replay';replay_dir.mkdir();replay=replay_dir/'replay.py';replay.write_bytes((E/'final-replay/replay.py.source').read_bytes())
 assert digest(replay)=='65e572e5428edbc27150857ce08db4976c8706c9bb781c631d5097d9105a4e2a'
 run('final-replay',[PYTHON,'-B',replay],timeout=30)
 assert digest(replay_dir/'replay.json')=='8fc6ce75860e6478a3865bc300494e9d39f681c1fd6fb1f19a1f1964a76b554f'
 report['exact_final_replay']=record(replay_dir/'replay.json')
 rows=load(directory/'synthetic-baseline-rows.json');mutated=load(directory/'synthetic-mutated-rows.json');spec=contract['lane_specs']['p2996'];q=load(ROOT/'evidence/core-skeleton/qualification.json')
 prefix=Path(spec['prefix']);cmake=q['tools']['cmake']['path'];sdk='/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk';ar='/usr/bin/ar';ranlib=str(prefix/'bin/llvm-ranlib')
 def make():return CoreCommands(ROOT,rows[0]['directory'],'p2996',prefix,sdk,cmake,ar,ranlib,False)
 v=make();assert len(v.compile_database(rows))==8
 reject('duplicate-isystem-consumes-Werror',lambda:make().compile_database(mutated))
 for config in CONFIGS:
  compiles=[]
  for name in ['core','smoke']:
   db=v.database[(config,name)];obj=v.object(config,name);compiles.append(db[:-4]+['-MD','-MT',obj,'-MF',obj+'.d']+db[-4:])
  library=config+'/libresearch_core.a';archive=[cmake,'-E','rm','-f',library,'&&',ar,'qc',library,v.object(config,'core'),'&&',ranlib,library]
  link=[v.cxx,*CONFIGS[config],*[a for a in spec['common_compile_tokens'] if a!='-std=c++26'],*spec['link_only_tokens'],'-Wl,-headerpad_max_install_names',v.object(config,'smoke'),'-o',config+'/research_core_smoke',library]
  for touch in [False,True]:
   chain=[':', '&&',*archive,*(['&&',cmake,'-E','touch',library] if touch else []),'&&',':'];actions=compiles+[chain,link]
   assert v.actions(actions,config)==['compile-core','compile-smoke','archive-core','link-smoke']
   report['synthetic_archive_cases'].append({'config':config,'touch':touch,'actions':actions,'state':'PASS: parser only, no archive/compiler executed'})
  changed=copy.deepcopy(actions);changed[2][changed[2].index('touch')+1]=config+'/unadmitted.a'
  reject('archive-touch-other-output-'+config,lambda:v.actions(changed,config))
 run('tasks-validate',[ROOT/'dev/mise','tasks','validate'],timeout=45)
 text=run('acceptance-baseline',[ROOT/'dev/mise','run','check:acceptance-baseline'],timeout=45)
 checks=json.loads(next(line for line in text.splitlines() if line.startswith('{')));assert checks['status']=='pass' and checks['checks']['baseline']==19
 report['static_counts']=checks['checks']
 status=run('status',git+['status','--porcelain','--untracked-files=normal'])
 assert set(line[3:] for line in status.splitlines())==set(maintained)|{'evidence/core-command-preparation/'}
 report['status']=status
 assert {p:digest(ROOT/p) for p in maintained}==before
 assert {p:digest(Path(p)) for p in control_hashes}==control_hashes
 for row in refs:assert digest(Path(row['path']))==row['sha256']
 report.update(state='PASS: corrected 03b2a command rules, exact replay and lightweight checks',all_candidate_control_and_reference_hashes_unchanged=True,initial_finding_disposition='FIXED: exactly one -isystem; regression rejected')
except BaseException as error:
 report.update(state='FAIL',error=repr(error));raise
finally:
 report['finished_at']=datetime.now(timezone.utc).isoformat();save()
print(json.dumps({'state':report['state'],'commands':len(report['commands']),'exits':{r['case']:r['returncode'] for r in report['commands']},'static_counts':report.get('static_counts'),'synthetic_archive_cases':len(report['synthetic_archive_cases']),'focused_rejections':report['focused_rejections']}),flush=True)
