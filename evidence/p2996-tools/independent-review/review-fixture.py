import ast, hashlib, importlib.util, io, json, os, re, shutil, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
directory=Path(__file__).resolve().parent
os.umask(0o077)
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import digest, preserved, read
from mise_link_probe import snapshot
from vcpkg_register import install_entries
load=lambda p:json.loads(p.read_text())
def write(name,value):
 p=directory/name;p.write_text(json.dumps(value,indent=2)+'\n');return p
def record(p):return {'path':str(p),'sha256':digest(p),'bytes':p.stat().st_size}
evidence=ROOT/'evidence/p2996-install'
E=ROOT/'evidence/p2996-tools'
registered=ROOT/'evidence/p2996-registration'
helper=ROOT/'dev/toolchains/p2996_tools.py'
assert digest(helper)=='4d2e14df01f09ffaff7f1f0009828c72c56f3aa01dfa94aac4bc057a728d9a6d'
parent=load(E/'operation/qualification.json')
assert digest(E/'operation/qualification.json')=='c13fe337ddca4b0bd4cc99047838c2dda9243e5d004a0d53ba51c4cf76f9d15b'
registration=load(registered/'operation/qualification.json')
review=load(registered/'registration-review.json')
assert digest(registered/'registration-review.json')=='9b8e92ac14d9304d7055fa00a3348612251e8bd27247db0ead946179bc835437'
assert review['result'].startswith('PASS') and not review['findings'] and review['all_protected_state_unchanged']
assert digest(registered/'operation/qualification.json')==review['operation_sha256']
baseline=load(registered/'independent-registration/post-state.json')
assert digest(registered/'independent-registration/post-state.json')==review['post_state']['sha256']=='8a5f11975efc9a953d8b57bde87467af5460cd48a3f695224dcaa9148a205317'
inventory=load(evidence/'independent-installation/post-install-inventory.json')
assert digest(evidence/'independent-installation/post-install-inventory.json')==review['retained_source_build_inventory']['inventory_sha256']
assert digest(evidence/'operation/prefix-inventory.json')==review['prefix_inventory']['inventory_sha256']
for path,sha in registration['proposal']['bindings'].items():assert digest(Path(path))==sha,path
for name,sha in registration['proposal']['helpers'].items():assert digest(helper.with_name(name))==sha,name
assert digest(helper.with_name('p2996_register.py'))==review['helper_sha256']
runtime=load(ROOT/'evidence/p2996-reflection/operation/qualification.json')
configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
prefix=Path(inventory['prefix']);source=Path(configuration['source'])
assert prefix==Path(review['proposal']['prefix'])
assert len(inventory['records'])==159 and len(load(evidence/'operation/prefix-inventory.json'))==6411
witness=helper.with_name('p2996_reflection.cpp')
assert digest(witness)==runtime['witness_sha256']==parent['witness_sha256']=='23cf7f270bdda566d002bacce165ac202165f85065092dcb8b742dfad81e3a41'
assert digest(helper.with_name('p2996_reflection.py'))==runtime['helper_sha256']
normal_argv=read('install-preimages.json')['normal_environment']['argv']
normal_env=load(Path(normal_argv[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0'}
env=normal_env|{'MARKETPLACE_P2996_PREFIX':str(prefix)}
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'helper_sha256':digest(helper),'operation_sha256':digest(E/'operation/qualification.json'),'witness_sha256':digest(witness)}
def save():write('native-checks.json',report)
def extract(path,name,scope):
 node=next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
 return scope[name]
extract(helper.with_name('p2996_install.py'),'prefix_inventory',globals())
protected=extract(helper.with_name('p2996_reflection.py'),'protected',globals())
runner=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source'
assert digest(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
run_scope=globals()|{'directory':directory,'report':report,'env':env,'save':save}
native=extract(runner,'run',run_scope)
# Reuse the frozen expected-exit adapter too; no full helper or admission is executed.
run=extract(helper,'run',globals())
parent_dir=Path(load(E/'admission.json')['run_directory'])
parent_commands={c['case']:c for c in parent['commands']}
def command(name):return [a.replace(str(parent_dir),str(directory)) for a in parent_commands[name]['argv']]
maintained=['dev/toolchains/p2996_tools.py','docs/llvm-tools.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
maintained_hashes={p:digest(ROOT/p) for p in maintained}
control_paths=[E/'admission.json',E/'operation-manifest.json',E/'source-contract.json',E/'pre-run-review.json',E/'preflight.json',witness]
control_hashes={str(p):digest(p) for p in control_paths}
LOCK_MODULE=Path('/Users/rmanaloto/dev/github/ray-manaloto/dotfiles/python/src/dotfiles_setup/host_lock.py')
LOCK_SHA='b20e5d969e7534b9a93a61c1ca1669483300aa8949f682be9ee90cda34d72d20'
assert digest(LOCK_MODULE)==LOCK_SHA
spec=importlib.util.spec_from_file_location('marketplace_host_lock',LOCK_MODULE)
lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease)
lock_path=lease.lock_path(lease.HEAVY_GATE)
assert lock_path==Path.home()/'.local/state/dotfiles/heavy-gate.lock'
assert not os.environ.get(lease.holder_env_name(lease.HEAVY_GATE)) and not os.environ.get(lease.LOCK_FD_ENV)
(cwd:=directory/'cwd').mkdir()
lease_info={'module':str(LOCK_MODULE),'module_sha256':LOCK_SHA,'path':str(lock_path),'wait_seconds':0,'acquired':False,'released':False}
write('lease.json',lease_info)
try:
 protected()
 report['preservation_before_passed']=True;save()
 assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
 assert digest(Path(configuration['sdk']['path'])/'SDKSettings.json')==configuration['sdk']['settings_sha256']
 selected=json.loads(run('named-profile',command('named-profile')))
 assert selected==runtime['selected_environment']==load(E/'operation/named-profile.stdout')
 report['selected_environment']=selected;save()
 with lease.held(lease.HEAVY_GATE,'marketplace-p2996-tools-cold-review',wait_s=0,out=io.StringIO()) as fd:
  assert fd is not None
  lease_info.update(acquired=True,acquired_at=datetime.now(timezone.utc).isoformat(),descriptor=fd,holder=lease.read_holder(lease.HEAVY_GATE).strip())
  write('lease.json',lease_info)
  processes=run('capacity-processes',command('capacity-processes'))
  blocker_pattern=r'(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd'
  blockers=[line for line in processes.splitlines() if re.fullmatch(blocker_pattern,Path(line.split(maxsplit=2)[-1]).name)]
  free_bytes=shutil.disk_usage(directory).free
  write('capacity.json',{'observed_at':datetime.now(timezone.utc).isoformat(),'blockers':blockers,'free_disk_bytes':free_bytes,'required_free_disk_bytes':8*1024**3,'native_process_check_returncode':report['commands'][-1]['returncode']})
  assert not blockers and free_bytes>=8*1024**3
  assert all(digest(prefix/'bin'/n)==sha for n,sha in parent['tool_hashes'].items())
  copied,formatted,unformatted=directory/'input.cpp',directory/'formatted.cpp',directory/'unformatted.cpp'
  copied.write_bytes(witness.read_bytes())
  text=run('format-copy',command('format-copy'),descriptor=fd)
  assert text.strip()
  formatted.write_bytes((directory/'format-copy.stdout').read_bytes())
  text=run('format-idempotence',command('format-idempotence'),descriptor=fd)
  assert text.strip() and (directory/'format-idempotence.stdout').read_bytes()==formatted.read_bytes()
  run('format-check',command('format-check'),descriptor=fd)
  unformatted.write_text('int main(){return 0;}\n')
  run('format-negative',command('format-negative'),descriptor=fd,expected=1)
  assert 'code should be clang-formatted' in (directory/'format-negative.stderr').read_text()
  assert digest(formatted)==parent['artifacts']['formatted.cpp']['sha256']
  before_compile_sha=digest(formatted)
  compile_argv=command('compile-formatted');native_compile=compile_argv[compile_argv.index('--')+1:]
  assert native_compile==[str(prefix/'bin/clang++'),*runtime['flags'],'-c',str(formatted),'-o',str(directory/'reflection.o')]
  run('compile-formatted',compile_argv,timeout=60,descriptor=fd)
  assert digest(formatted)==before_compile_sha
  assert not (directory/'libreflection.a').exists()
  run('archive-create',command('archive-create'),descriptor=fd)
  assert run('archive-list',command('archive-list'),descriptor=fd)=='reflection.o\n'
  run('archive-link',command('archive-link'),timeout=60,descriptor=fd)
  output=run('archive-run',command('archive-run'),descriptor=fd)
  assert output==runtime['witness']['output']=='reflection value=43 exception=ok\n'
  loaded=[line[line.find(str(prefix)):].strip() for line in (directory/'archive-run.stderr').read_text().splitlines() if str(prefix) in line]
  libraries=[prefix/'lib'/n for n in ['libc++.dylib','libc++abi.dylib','libunwind.dylib']]
  assert loaded==parent['loaded_private_images'] and all(any(Path(p).resolve()==lib.resolve() for p in loaded) for lib in libraries)
  database=write('compile_commands.json',[{'directory':str(directory),'file':str(formatted),'arguments':native_compile}])
  empty=directory/'empty-path';empty.mkdir()
  clangd_env={k:v for k,v in env.items() if k not in ['CLANGD_FLAGS','CLANGD_TRACE','CLANGD_METRICS']}|{'PATH':str(empty)}
  assert not list(empty.iterdir())
  run('clangd-check',command('clangd-check'),timeout=60,descriptor=fd,environment=clangd_env)
  diagnostics=(directory/'clangd-check.stderr').read_text()
  required=['Entering check mode (no LSP server)','Compile command from CDB','All checks completed, 0 errors',str(prefix/'bin/clang++'),'-freflection',str(prefix/'include/c++/v1'),"Couldn't find xcrun"]
  assert all(s in diagnostics for s in required)
  assert all(s not in diagnostics for s in ['Generic fallback command','Compile command inferred'])
  assert digest(formatted)==before_compile_sha and copied.read_bytes()==witness.read_bytes()
  report['artifacts']={p.name:record(p) for p in [copied,formatted,unformatted,directory/'reflection.o',directory/'libreflection.a',directory/'reflection',database]}
  report['loaded_private_images']=loaded
  report['clangd_check']={'zero_errors':True,'explicit_cdb':True,'fallback_or_inferred':False,'server_started':False,'private_empty_PATH':str(empty),'removed_environment_keys':['CLANGD_FLAGS','CLANGD_TRACE','CLANGD_METRICS'],'expected_missing_xcrun_diagnostic':True}
  save()
 lease_info.update(released=True,released_at=datetime.now(timezone.utc).isoformat(),free_after_release=lease._probe_free(lock_path))
 assert lease_info['free_after_release']
 write('lease.json',lease_info)
 default=run('default-consumer',normal_argv,environment=normal_env)
 assert default==(E/'operation/default-after.stdout').read_text()==(registered/'operation/default-after.stdout').read_text()
 git_env=normal_env|{'GIT_OPTIONAL_LOCKS':'0'}
 for label,args in [('head',['rev-parse','HEAD']),('tree',['rev-parse','HEAD^{tree}']),('status',['status','--porcelain','--untracked-files=all']),('diff',['diff','--no-ext-diff','--binary'])]:
  text=run('source-'+label,['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',source,*args],environment=git_env)
  assert text==(E/('operation/source-after-'+label+'.stdout')).read_text()
 # Read-only development gate, using explicit installed binaries and normal ignore rules.
 static_env=normal_env.copy()
 for key in ['GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:static_env.pop(key,None)
 static_env.update(MARKETPLACE_MISE_BIN=configuration['mise']['path'],MARKETPLACE_PYTHON='/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3',PYTHONDONTWRITEBYTECODE='1')
 run('tasks-validate',[ROOT/'dev/mise','tasks','validate'],environment=static_env)
 text=run('acceptance-baseline',[ROOT/'dev/mise','run','check:acceptance-baseline'],environment=static_env)
 static=json.loads(next(line for line in text.splitlines() if line.startswith('{')))
 assert static['status']=='pass' and static['checks']['baseline']==19
 report['static_counts']=static['checks']
 rg=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',ROOT]
 ids=run('root-identity',rg+['rev-parse','--show-toplevel','--git-common-dir','HEAD'],environment=static_env).splitlines()
 branch=run('root-branch',rg+['symbolic-ref','--short','HEAD'],environment=static_env).strip()
 assert ids==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git','0e023aa0cb70f7980fb2010ad4e2cf861aeb8802']
 assert branch=='codex/marketplace-native-onboarding'
 run('root-status',rg+['status','--porcelain','--untracked-files=normal'],environment=static_env)
 report['identity']={'root':ids[0],'common_git_directory':ids[1],'head':ids[2],'branch':branch}
 assert {p:digest(ROOT/p) for p in maintained}==maintained_hashes
 assert {p:digest(Path(p)) for p in control_hashes}==control_hashes
 assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
 assert digest(Path(configuration['sdk']['path'])/'SDKSettings.json')==configuration['sdk']['settings_sha256']
 report['maintained_file_hashes']=maintained_hashes
 report['control_file_hashes']=control_hashes
 report['state']='PASS: independent bounded LLVM tools fixture'
except BaseException as error:
 report.update(state='FAIL',error=repr(error))
 raise
finally:
 try:
  protected()
  report['all_protected_state_unchanged']=True
 except BaseException as error:
  report.update(state='FAIL',preservation_error=repr(error))
  raise
 finally:
  report['finished_at']=datetime.now(timezone.utc).isoformat()
  save()
print(json.dumps({'state':report['state'],'directory':str(directory),'native_commands':len(report['commands']),'exits':{c['case']:c['returncode'] for c in report['commands']},'static_counts':report['static_counts']}),flush=True)
