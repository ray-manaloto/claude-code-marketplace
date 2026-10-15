import ast, copy, hashlib, json, os, shutil, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
directory=Path(__file__).resolve().parent
os.umask(0o077)
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import digest, preserved, read
from mise_link_probe import isolated, snapshot
from vcpkg_register import census, install_entries
load=lambda p:json.loads(p.read_text())
write=lambda name,value:(directory/name).write_text(json.dumps(value,indent=2)+'\n')
E=ROOT/'evidence/p2996-registration'
installed=ROOT/'evidence/p2996-install'
helper=ROOT/'dev/toolchains/p2996_register.py'
helper_sha='b80d364c30736a407469947b486a8eaf1b8e3ca27a97b4c4675c782a19130542'
operation_sha='28c9be5e8e0325eacc3de0625a31b4ba442b0ecc00f99cd7dbbb40f2ebe9a954'
assert digest(helper)==helper_sha
assert digest(E/'operation/qualification.json')==operation_sha
q=load(E/'operation/qualification.json')
a=load(E/'admission.json')
prep=load(E/'preparation-review.json')
manifest=load(E/'operation-manifest.json')
assert digest(E/'preparation-review.json')==a['review_sha256']=='be0cd08f26d6d78b544811b46cac1bb1924c9e4ca21ca0f0fb392c50bceb071b'
assert digest(E/'writer-census.json')==a['writer_census_sha256']
assert digest(E/'thread-census.json')==a['thread_census_sha256']
assert a['helper_sha256']==q['helper_sha256']==prep['helper_sha256']==helper_sha
assert q['proposal']==a['proposal']==prep['proposal'] and prep['findings']==[]
assert q['state']=='PASS: global namespace promotion' and all(q[k] for k in ['apply_requested','promotion_attempted','promoted','protected_state_unchanged'])
assert a['head']=='38c61dfd9ae46d1f102b38c2dba37fd46714c000' and a['native_command_timeout_seconds']==45
assert manifest['source_directory']==a['run_directory']
assert len(manifest['files'])==29
for row in manifest['files']:
 for path in [Path(row['source']),ROOT/row['copy']]:
  assert path.is_file() and path.stat().st_size==row['bytes'] and digest(path)==row['sha256'],str(path)
assert len(q['commands'])==13 and all(c['returncode']==0 for c in q['commands'])
for c in q['commands']:
 assert len(c['logs'])==2 and 0<=c['elapsed_seconds']<=45
 for log in c['logs']:
  path=Path(log['path']);row=next(r for r in manifest['files'] if r['source']==str(path))
  assert row['sha256']==log['sha256']==digest(path)
invocation=load(E/'operation/invocation.json')
assert invocation['returncode']==0 and invocation['stderr']=='' and invocation['helper_sha256']==helper_sha
assert invocation['admission_sha256']==digest(E/'admission.json')
assert invocation['argv'][-1]=='--apply' and invocation['argv'][-2]==a['run_directory']
for path,sha in q['proposal']['bindings'].items():assert digest(Path(path))==sha,path
for name,sha in q['proposal']['helpers'].items():assert digest(helper.with_name(name))==sha,name
for row in q['global_preimages'].values():
 b=Path(row['backup']);assert digest(b)==row['sha256'] and oct(b.stat().st_mode&0o777)==row['mode']
assert q['census']['blockers']==q['census_immediate']['blockers']==load(E/'writer-census.json')['blockers']==[]
assert datetime.fromisoformat(q['census']['recorded_at'])<datetime.fromisoformat(q['census_immediate']['recorded_at'])<datetime.fromisoformat(next(c['started_at'] for c in q['commands'] if c['case']=='native-where'))
for stage in ['before','after']:
 for suffix in ['head','tree','status','diff']:
  assert (E/f'operation/source-{stage}-{suffix}.stdout').read_bytes()==(E/f'operation/source-before-{suffix}.stdout').read_bytes()
assert (E/'operation/default-before.stdout').read_bytes()==(E/'operation/default-after.stdout').read_bytes()
configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
source=Path(configuration['source'])
prefix=Path(q['proposal']['prefix'])
installs=Path.home()/'.local/share/mise/installs'
destination=Path(q['proposal']['destination'])
baseline=load(installed/'independent-installation/post-state.json')
inventory=load(installed/'independent-installation/post-install-inventory.json')
assert len(inventory['records'])==159 and len(load(installed/'operation/prefix-inventory.json'))==6411
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'promoted':True,'proposal':q['proposal']}
def save():write('native-checks.json',report)
# Reuse only the two read-only function bodies and the frozen process wrapper.
pi_source=ROOT/'dev/toolchains/p2996_install.py'
pi_node=next(n for n in ast.walk(ast.parse(pi_source.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='prefix_inventory')
exec(compile(ast.Module(body=[pi_node],type_ignores=[]),str(pi_source),'exec'),globals())
protected_node=next(n for n in ast.walk(ast.parse(helper.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='protected')
exec(compile(ast.Module(body=[protected_node],type_ignores=[]),str(helper),'exec'),globals())
protected()
assert snapshot(destination)==q['proposal']['namespace']
assert set(p.name for p in destination.iterdir())=={configuration['pin']}
assert (destination/configuration['pin']).is_symlink() and (destination/configuration['pin']).resolve()==prefix
assert q['destination_observed']=={'lexists':True,'is_symlink':False,'namespace':snapshot(destination)}
assert all(not os.path.lexists(installs.parent/'plugins'/n) for n in ['clang-p2996','asdf-clang-p2996'])
post_before=copy.deepcopy(baseline);post_before['install_entries']=install_entries(installs)
added={k:v for k,v in post_before['install_entries'].items() if k not in baseline['install_entries']}
assert set(added)=={destination.name,destination.name+'/'+configuration['pin']} and len(post_before['install_entries'])==2200
assert all(post_before['install_entries'][k]==v for k,v in baseline['install_entries'].items())
maintained=['dev/toolchains/p2996_register.py','docs/p2996-toolchain.md','docs/status.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
maintained_hashes={p:digest(ROOT/p) for p in maintained}
runner=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source'
assert digest(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
run_node=next(n for n in ast.walk(ast.parse(runner.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='run')
exec(compile(ast.Module(body=[run_node],type_ignores=[]),str(runner),'exec'),globals())
frozen_run=run
def execute(label,argv,environment):
 globals()['env']=environment
 return frozen_run(label,argv,timeout=45)
current_census=census()
write('current-census.json',current_census)
# Fresh private state/config/cache; only the install directory points at global state.
consumer=isolated(directory/'consumer')
consumer['MISE_INSTALLS_DIR']=str(installs)
consumer.update(GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_TERMINAL_PROMPT='0',GIT_OPTIONAL_LOCKS='0')
mise=configuration['mise']
assert digest(Path(mise['path']))==mise['sha256']
base=[mise['path'],'--no-config','--no-hooks','--no-env','-C',consumer['MISE_CEILING_PATHS']]
where=execute('native-where',base+['where',q['proposal']['tool']],consumer)
assert where==(E/'operation/native-where.stdout').read_text()
assert Path(where.strip()).resolve()==prefix
version=execute('native-version',base+['exec',q['proposal']['tool'],'--no-deps','--','clang++','--no-default-config','--version'],consumer)
assert version==(E/'operation/native-version.stdout').read_text()==q['discovery']['compiler_version']
assert configuration['pin'] in version and 'clang version 21.0.0git ' in version
assert Path(next(s.split(': ',1)[1] for s in version.splitlines() if s.startswith('InstalledDir: '))).resolve()==prefix/'bin'
assert not os.path.lexists(directory/'consumer/data/plugins')
assert not os.path.lexists(directory/'consumer/data/installs')
normal_argv=read('install-preimages.json')['normal_environment']['argv']
normal_env=load(Path(normal_argv[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0'}
default=execute('default-consumer',normal_argv,normal_env)
assert default==(E/'operation/default-after.stdout').read_text()
git=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',source]
for label,args in [('head',['rev-parse','HEAD']),('tree',['rev-parse','HEAD^{tree}']),('status',['status','--porcelain','--untracked-files=all']),('diff',['diff','--no-ext-diff','--binary'])]:
 result=execute('source-'+label,git+args,consumer)
 assert result==(E/('operation/source-after-'+label+'.stdout')).read_text(),label
# Explicit binaries avoid inherited PATH configuration and no tools are installed.
static_env=consumer.copy()
for key in ['MISE_INSTALLS_DIR','GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:static_env.pop(key,None)
static_env.update(MARKETPLACE_MISE_BIN=mise['path'],MARKETPLACE_PYTHON='/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3',PYTHONDONTWRITEBYTECODE='1')
execute('tasks-validate',[ROOT/'dev/mise','tasks','validate'],static_env)
static=execute('acceptance-baseline',[ROOT/'dev/mise','run','check:acceptance-baseline'],static_env)
static_result=json.loads(next(line for line in static.splitlines() if line.startswith('{')))
assert static_result['status']=='pass' and static_result['checks']['baseline']==19
rootgit=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',ROOT]
identity=execute('root-identity',rootgit+['rev-parse','--show-toplevel','--git-common-dir','HEAD'],static_env).splitlines()
branch=execute('root-branch',rootgit+['symbolic-ref','--short','HEAD'],static_env).strip()
assert identity==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git',a['head']]
assert branch=='codex/marketplace-native-onboarding'
root_status=execute('root-status',rootgit+['status','--porcelain','--untracked-files=normal'],static_env)
protected()
post_after=copy.deepcopy(baseline);post_after['install_entries']=install_entries(installs)
assert post_after==post_before
assert {p:digest(ROOT/p) for p in maintained}==maintained_hashes
assert digest(Path(mise['path']))==mise['sha256'] and digest(helper)==helper_sha
for row in manifest['files']:
 assert digest(ROOT/row['copy'])==row['sha256'] and digest(Path(row['source']))==row['sha256']
write('post-state.json',post_after)
write('consumer-environment.json',consumer)
report.update(state='PASS: bounded registration closure checks',finished_at=datetime.now(timezone.utc).isoformat(),protected_state_unchanged=True)
save()
verification={
 'operation_sha256':operation_sha,'helper_sha256':helper_sha,
 'operation_manifest':{'path':str(E/'operation-manifest.json'),'sha256':digest(E/'operation-manifest.json'),'records':len(manifest['files']),'native_commands':len(q['commands']),'logs':26,'all_originals_and_copies_match':True,'all_native_returncodes':0,'invocation_returncode':0},
 'admission':{'path':str(E/'admission.json'),'sha256':digest(E/'admission.json'),'preparation_review_sha256':a['review_sha256'],'writer_census_sha256':a['writer_census_sha256'],'thread_census_sha256':a['thread_census_sha256'],'immediate_census':q['census_immediate']},
 'proposal_bindings_and_helper_hashes_match':True,'backups_verified_by_hash_and_mode':9,'raw_backups_copied':False,
 'prefix':{'path':str(prefix),'records':6411,'inventory_sha256':digest(installed/'operation/prefix-inventory.json'),'exact_before_and_after':True},
 'retained_source_build_records':{'records':159,'inventory_sha256':digest(installed/'independent-installation/post-install-inventory.json'),'exact_before_and_after':True},
 'preservation':{'global_files':9,'packages':8,'glib_files':2,'shims':835,'command_wrappers':0,'previous_install_entries':2198,'post_install_entries':2200,'added_install_entries':added,'all_other_state_unchanged':True},
 'native_discovery':{'where':where.strip(),'resolved':str(Path(where.strip()).resolve()),'compiler_version':version,'exact_parent_output_match':True,'private_mise_config_state_cache':True,'only_global_mise_override':'MISE_INSTALLS_DIR'},
 'source':{'head':configuration['pin'],'tree':configuration['tree'],'status_sha256':digest(directory/'source-status.stdout'),'diff_sha256':digest(directory/'source-diff.stdout'),'all_parent_outputs_match':True},
 'default_consumer':{'sha256':digest(directory/'default-consumer.stdout'),'exact_parent_before_after_output_match':True},
 'static_counts':static_result['checks'],'identity':{'root':identity[0],'common_git_directory':identity[1],'head':identity[2],'branch':branch},'maintained_file_hashes':maintained_hashes,
 'frozen_readonly_protected_function_sha256':hashlib.sha256(ast.get_source_segment(helper.read_text(),protected_node).encode()).hexdigest(),
 'frozen_process_wrapper_source_sha256':digest(runner),
 'reviewer_native_command_count':len(report['commands']),'all_reviewer_native_returncodes':0,
 'post_state':{'path':str(directory/'post-state.json'),'sha256':digest(directory/'post-state.json'),'schema':'same as prior installation post-state; only install_entries updated'},
 'limits':['No preparation guard or interruption suite rerun.','No compilation, formatting, clangd, installation, promotion, profile/shim/global writes, network, containers or model sessions.','Static baseline preserves all 19 original files; full Claude OCI/provider/hook runtime acceptance is not rerun.']}
write('verification.json',verification)
print(json.dumps({'result':'PASS','directory':str(directory),'post_state_sha256':digest(directory/'post-state.json'),'native_commands':len(report['commands']),'static_counts':static_result['checks']}),flush=True)
