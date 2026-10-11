import ast, hashlib, importlib.util, io, json, os, math, re, shutil, signal, subprocess, sys, time
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
E=ROOT/'evidence/p2996-coverage'
registered=ROOT/'evidence/p2996-registration'
helper=ROOT/'dev/toolchains/p2996_coverage.py'
assert digest(helper)=='50f4b2f512bb15dd3727cb7551c7aa26b58bd44a395763a9351f7f54d9cd69d9'
parent=load(E/'operation/qualification.json')
assert digest(E/'operation/qualification.json')=='3d1334b2a06ec3d502600c23c380092a7b5b9c0fb91427be9610d3302a9a1882'
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
assert digest(ROOT/'evidence/p2996-analysis/analysis-review.json')=='ef444df5bd6b63d798bde498dafbde147f612dd1ad2d84d86a9482357e293a10'
contract=load(E/'source-contract.json')
assert digest(E/'source-contract.json')=='eaf03d7420cb0075ebfc526554500d1a66cd510d3a9e8ebece446b6c27578c14'
configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
prefix=Path(inventory['prefix']);source=Path(configuration['source'])
assert prefix==Path(review['proposal']['prefix'])
assert len(inventory['records'])==159 and len(load(evidence/'operation/prefix-inventory.json'))==6411
witness=helper.with_name('p2996_reflection.cpp')
assert digest(witness)==runtime['witness_sha256']==parent['witness_sha256']=='23cf7f270bdda566d002bacce165ac202165f85065092dcb8b742dfad81e3a41'
assert digest(helper.with_name('p2996_reflection.py'))==runtime['helper_sha256']
normal_argv=read('install-preimages.json')['normal_environment']['argv']
normal_env=load(Path(normal_argv[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0'}
env=normal_env|{'MARKETPLACE_P2996_PREFIX':str(prefix)}
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'helper_sha256':digest(helper),'operation_sha256':digest(E/'operation/qualification.json'),'witness_sha256':digest(witness)}
def save():write('native-checks.json',report)
def interrupted(signum,frame):raise KeyboardInterrupt('received signal '+str(signum))
for signum in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(signum,interrupted)
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
maintained=['dev/toolchains/p2996_coverage.py','docs/llvm-tools.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
maintained_hashes={p:digest(ROOT/p) for p in maintained}
control_paths=[E/'admission.json',E/'operation-manifest.json',E/'source-contract.json',E/'environment-correction.json',E/'pre-run-review.json',E/'preflight.json',witness]
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
 with lease.held(lease.HEAVY_GATE,'marketplace-p2996-coverage-cold-review',wait_s=0,out=io.StringIO()) as fd:
  assert fd is not None
  lease_info.update(acquired=True,acquired_at=datetime.now(timezone.utc).isoformat(),descriptor=fd,holder=lease.read_holder(lease.HEAVY_GATE).strip())
  write('lease.json',lease_info)
  processes=run('capacity-processes',command('capacity-processes'))
  blocker_pattern=r'(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy'
  blockers=[line for line in processes.splitlines() if re.fullmatch(blocker_pattern,Path(line.split(maxsplit=2)[-1]).name)]
  free_bytes=shutil.disk_usage(directory).free
  write('capacity.json',{'observed_at':datetime.now(timezone.utc).isoformat(),'blockers':blockers,'free_disk_bytes':free_bytes,'required_free_disk_bytes':8*1024**3,'native_process_check_returncode':report['commands'][-1]['returncode']})
  assert not blockers and free_bytes>=8*1024**3
  assert all(digest(prefix/'bin'/n)==sha for n,sha in parent['tool_hashes'].items())
  flags=runtime['flags']
  base=[configuration['mise']['path'],'--no-hooks','-C',str(cwd),'-E','p2996','exec','--fresh-env','--no-deps','--']
  report['tool_hashes']={name:digest(prefix/'bin'/name) for name in parent['tool_hashes']}
  profile_runtime=prefix/'lib/clang/21/lib/darwin/libclang_rt.profile_osx.a'
  assert digest(profile_runtime)==parent['profile_runtime_sha256']=='48dd00286225897919bf6fb6a6630245d9489ac8a6544acb55b9350486f3d31b'
  report['profile_runtime']=record(profile_runtime)
  copied,wrapper=directory/witness.name,directory/'coverage.cpp'
  assert not copied.exists() and not wrapper.exists() and '%' not in str(directory)
  copied.write_bytes(witness.read_bytes());wrapper.write_text(contract['fixture']['wrapper']['text'])
  assert digest(wrapper)==contract['fixture']['wrapper']['sha256']=='1b0a991f9b9c5677d5fb3f82eb6c891856bda81d2095427590171546db9d44e7'
  original_sources={p.name:record(p) for p in [copied,wrapper]};report['fresh_sources_before']=original_sources
  binary,raw,merged=[directory/name for name in ['coverage','coverage.profraw','coverage.profdata']]
  assert not any(p.exists() for p in [binary,raw,merged])
  libraries=[prefix/'lib'/name for name in ['libc++.dylib','libc++abi.dylib','libunwind.dylib']]
  argv=base+[str(prefix/'bin/clang++'),*flags,'-O0','-fprofile-instr-generate','-fcoverage-mapping',str(wrapper),
    '-nostdlib++',*[str(p) for p in libraries],'-Wl,-rpath,'+str(prefix/'lib'),'-o',str(binary)]
  assert argv==command('coverage-compile')
  run('coverage-compile',argv,timeout=60,descriptor=fd)
  assert binary.is_file() and binary.stat().st_size>0 and not raw.exists() and not merged.exists()
  argv=base+['/usr/bin/env','LLVM_PROFILE_FILE='+str(raw),'DYLD_PRINT_LIBRARIES=1',str(binary)]
  assert argv==command('coverage-run')
  output=run('coverage-run',argv,timeout=60,descriptor=fd)
  assert output==contract['fixture']['expected_stdout']=='reflection value=43 exception=ok\n'
  assert raw.is_file() and raw.stat().st_size>0 and not merged.exists()
  loaded=[line[line.find(str(prefix)):].strip() for line in (directory/'coverage-run.stderr').read_text().splitlines() if str(prefix) in line]
  assert loaded==parent['loaded_private_images']==contract['proposed_not_run']['run']['required_loader_images']
  assert all(any(Path(p).resolve()==lib.resolve() for p in loaded) for lib in libraries)
  report['loaded_private_images']=loaded
  argv=base+[str(prefix/'bin/llvm-profdata'),'merge','-sparse','--num-threads=1','--failure-mode=any',str(raw),'-o',str(merged)]
  assert argv==command('coverage-merge')
  run('coverage-merge',argv,timeout=60,descriptor=fd)
  assert merged.is_file() and merged.stat().st_size>0
  export=base+[str(prefix/'bin/llvm-cov'),'export',str(binary),'--format=text','--num-threads=1','--debuginfod=false']
  argv=export+['--instr-profile='+str(merged),str(wrapper),str(copied)]
  assert argv==command('coverage-export')
  exported=run('coverage-export',argv,timeout=60,descriptor=fd)
  diagnostic=(directory/'coverage-export.stderr').read_text()
  assert not any(x in diagnostic for x in ['functions have mismatched data','profile data may be out of date','error:'])
  obj=json.loads(exported)
  assert obj['type']=='llvm.coverage.json.export' and obj['version']=='3.0.0' and len(obj['data'])==1
  data=obj['data'][0]
  matches=[f for f in data['functions'] if f['filenames'] in [[str(wrapper)],[str(copied)]]]
  assert len(matches)==3
  functions={f['name']:f for f in matches}
  assert set(functions)=={'main','coverage_branch','_Z24coverage_reflection_mainv'}
  assert functions['main']['count']==1 and functions['coverage_branch']['count']==2 and functions['_Z24coverage_reflection_mainv']['count']==1
  assert functions['main']['filenames']==functions['coverage_branch']['filenames']==[str(wrapper)]
  assert functions['_Z24coverage_reflection_mainv']['filenames']==[str(copied)]
  assert functions['coverage_branch']['branches']==[[6,7,6,11,1,1,0,0,4]]
  files={f['filename']:f for f in data['files']};assert set(files)=={str(wrapper),str(copied)}
  branches=files[str(wrapper)]['summary']['branches']
  assert branches=={'count':2,'covered':2,'notcovered':0,'percent':100}
  totals=data['totals'];expected={'functions':(3,3),'lines':(22,22),'regions':(15,13),'branches':(6,4)}
  for name,(count,covered) in expected.items():
   item=totals[name];assert type(item['count']) is int and type(item['covered']) is int
   assert (item['count'],item['covered'])==(count,covered) and math.isfinite(item['percent']) and 0<=item['percent']<=100
   if name in ['regions','branches']:assert item['notcovered']==count-covered
  assert totals==parent['coverage']['totals']
  report['coverage']={'functions':functions,'wrapper_branches':branches,'totals':totals,'export_schema':{'type':obj['type'],'version':obj['version'],'data_length':len(obj['data'])}}
  before_negative={p.name:digest(p) for p in [copied,wrapper,binary,raw,merged]}
  absent=directory/'absent.profdata';assert not absent.exists()
  argv=export+['--instr-profile='+str(absent),str(wrapper),str(copied)]
  assert argv==command('coverage-absent-data')
  output=run('coverage-absent-data',argv,timeout=60,descriptor=fd,expected=1)
  diagnostic=(directory/'coverage-absent-data.stderr').read_text()
  assert not output and not absent.exists() and 'could not read profile data!' in diagnostic and str(absent) in diagnostic
  assert before_negative=={p.name:digest(p) for p in [copied,wrapper,binary,raw,merged]}
  assert copied.read_bytes()==witness.read_bytes()
  assert all(digest(directory/name)==r['sha256']==parent['artifacts'][name]['sha256'] for name,r in original_sources.items())
  report['negative_control']={'native_returncode':report['commands'][-1]['returncode'],'stdout_empty':True,'absent_file_remains_absent':True,'intended_profile_read_error':True,'all_positive_artifacts_and_sources_unchanged':True}
  report['artifacts']={p.name:record(p) for p in [copied,wrapper,binary,raw,merged]}
  report['binary_artifacts_kept_private']=[str(p) for p in [binary,raw,merged]]
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
 assert ids==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git','7baee2b880265c5d444e17aeeaf66eb3011f2684']
 assert branch=='codex/marketplace-native-onboarding'
 run('root-status',rg+['status','--porcelain','--untracked-files=normal'],environment=static_env)
 report['identity']={'root':ids[0],'common_git_directory':ids[1],'head':ids[2],'branch':branch}
 assert {p:digest(ROOT/p) for p in maintained}==maintained_hashes
 assert {p:digest(Path(p)) for p in control_hashes}==control_hashes
 assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
 assert digest(Path(configuration['sdk']['path'])/'SDKSettings.json')==configuration['sdk']['settings_sha256']
 report['maintained_file_hashes']=maintained_hashes
 report['control_file_hashes']=control_hashes
 report['state']='PASS: independent bounded LLVM coverage controls'
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
