import ast,hashlib,json,os,re,shlex,shutil,signal,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
import yaml
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=ROOT/'evidence/core-p2996';directory=Path(__file__).parent
sys.dont_write_bytecode=True;os.umask(0o077);sys.path.insert(0,str(ROOT/'dev/toolchains'))
from gcc_install import read
PYTHON='/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3'
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def record(p):return {'path':str(p),'sha256':digest(p),'bytes':Path(p).stat().st_size}
def load(p):return json.loads(Path(p).read_text())
def write(name,data):(directory/name).write_text(json.dumps(data,indent=2)+'\n')
helper=ROOT/'dev/toolchains/core_matrix.py';proposal=load(E/'proposal.json')
assert digest(helper)==proposal['helper_sha256']=='3a3c06f9f736929d02b6843d344a69380c42962f7eccdff0a0e7b77f150a035c'
assert digest(E/'proposal.json')=='abd022fd8d214e5c174c693f5b9e711af6e41bd0db75fcc99a419726d8a158b4'
assert len(helper.read_text().splitlines())==322 and len(proposal['inputs'])==70 and len(proposal['tool_hashes'])==18
inputs=[];tools=[]
for path,sha in proposal['inputs'].items():
 p=ROOT/path;assert digest(p)==sha;inputs.append(record(p))
for path,sha in proposal['tool_hashes'].items():
 p=Path(path);assert digest(p)==sha;tools.append(record(p)|{'resolved':str(p.resolve())})
baseline=load(ROOT/'evidence/onboarding/baseline-files.json')['files'];assert len(baseline)==19
assert all(proposal['inputs'][r['path']]==r['sha256'] for r in baseline)
prereqs={'core-command-preparation/command-review.json':'4be3d61dcb0bad092ccef79d3805e2ba1afa8c2309116db38dba8ac748184ca9','core-p2996-preparation/preparation-review.json':'066dbb351c09878ef4f6d4a1b8874fc71c6b9ba39e58ef7d39c57f1c0cb92fe9','core-command-preparation/harness-contract.json':'9becd18e6c597a273fa8c4eded3cf5f11bd00c1b3999d78f130797f22ca68dd7','core-p2996/export-tool-prerequisite.json':'4ddad861aefcded3253434211167379b99fcfb277d0d1ca43395dc46bdeee7d4'}
for path,sha in prereqs.items():assert digest(ROOT/'evidence'/path)==sha
for path in list(prereqs)[:2]:
 row=load(ROOT/'evidence'/path);assert row['result'].startswith('PASS') and not row['findings']
export=load(E/'export-tool-prerequisite.json');manual_records=[]
for row in export['tools'].values():assert digest(Path(row['path']))==row['sha256'] and str(Path(row['path']).resolve())==row['resolved']
for row in export['manuals'].values():
 p=Path(row['path']);assert digest(p)==row['sha256'];lines=p.read_text().splitlines();a=min(x[0] for x in row['line_ranges']);b=max(x[1] for x in row['line_ranges'])
 assert '\n'.join(f'{n}: {lines[n-1]}' for n in range(a,b+1))==row['excerpt'];manual_records.append(record(p)|{'line_ranges':row['line_ranges'],'excerpts_match':True})
assert len(export['execution']['commands'])==4 and all(r['returncode']==0 and not r['stderr'] and not r['killed'] and r['signal'] is None for r in export['execution']['commands'])
assert export['observed_known_string']['stdout']=='aggregated_research::reflection_probe()\n'
prep=load(E/'preparation-checks.json');latest=load(E/'pre-run-static-checks.json')
assert all(c['returncode']==0 for c in prep['checks']+latest['checks'])
assert latest['helper_sha256']==digest(helper) and latest['proposal_sha256']==digest(E/'proposal.json')
assert prep['helper_sha256']!=digest(helper)
cmakeq=ROOT/'evidence/p2996-cmake/operation/qualification.json';assert digest(cmakeq)=='e61702be845f1602d267789d8ab78ce5601a59ab9cd78ef0435cbebe365081b6'
old=load(cmakeq);row=next(r for r in old['configured_evidence'] if r['path'].endswith('CMakeConfigureLog.yaml'));logpath=Path(row['path']);assert digest(logpath)==row['sha256'] and logpath.stat().st_size==row['bytes']
text=logpath.read_text();parsed=[e for e in yaml.safe_load(text)['events'] if e['kind']=='try_compile-v1'];assert len(parsed)==3
replays=[]
for name,probe in old['probes'].items():
 event=next(e for e in parsed if e['directories']['binary']==probe['directory']);assert event['buildResult']['exitCode']==0 and event['buildResult']['cached'] is False
 case=next(r for r in old['commands'] if r['case']=='probe-'+name)
 for r in case['logs']:assert digest(Path(r['path']))==r['sha256']
 lines=Path(case['logs'][0]['path']).read_text().splitlines();assert len(lines)==2 and [shlex.split(s) for s in lines]==probe['generated_commands']
 block=next(b for b in text.split('kind: "try_compile-v1"')[1:] if 'binary: "'+probe['directory']+'"' in b).split('\n  -\n',1)[0]
 actual=[s.strip().split('] ',1)[1] for s in block.splitlines() if re.match(r'^\s+\[[12]/2\] ',s)]
 assert actual==[s.replace('\\','\\\\') for s in lines]
 assert actual==[s.split('] ',1)[1] for s in event['buildResult']['stdout'].splitlines() if re.match(r'^\[[12]/2\] ',s)]
 replays.append({'probe':name,'directory':probe['directory'],'commands':2,'native_exit_recorded':event['buildResult']['exitCode'],'cached':event['buildResult']['cached'],'generated_log':record(Path(case['logs'][0]['path'])),'native_encoded_lines':actual,'generated_lines':lines,'match':True})
loaded_records=[];contract=load(ROOT/'evidence/core-command-preparation/harness-contract.json');os_images=set(contract['lane_specs']['gcc16']['allowed_recorded_os_cxx_images'])
for qpath,case_name in [(cmakeq,'runtime-Debug'),(ROOT/'evidence/core-skeleton/qualification.json','runtime-shared-Debug')]:
 q=load(qpath);case=next(r for r in q['commands'] if r['case']==case_name);r=case['logs'][1];p=Path(r['path']);assert digest(p)==r['sha256']
 loaded={re.search(r' (/.*)$',s)[1] for s in p.read_text().splitlines()};assert os_images<=loaded;loaded_records.append({'case':case_name,'receipt':record(p),'allowed_os_cpp_images_observed':sorted(os_images)})
maintained=['dev/toolchains/core_matrix.py','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md'];before={p:digest(ROOT/p) for p in maintained}
controls=[ROOT/'AGENTS.md',ROOT/'docs/accepted-decisions.md',ROOT/'docs/core-qualification.md',ROOT/'docs/status.md',ROOT/'dev/mise',E/'proposal.json',E/'export-tool-prerequisite.json',E/'preparation-checks.json',E/'pre-run-static-checks.json']
control_hashes={str(p):digest(p) for p in controls}
normal=read('install-preimages.json')['normal_environment']['argv'];configuration=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
env=load(Path(normal[-1]).parent/'context.json')['environment']|{'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','PYTHONDONTWRITEBYTECODE':'1','MARKETPLACE_MISE_BIN':configuration['mise']['path'],'MARKETPLACE_PYTHON':PYTHON}
for key in ['GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM']:env.pop(key,None)
assert digest(Path(configuration['mise']['path']))==configuration['mise']['sha256']
report={'state':'running','started_at':datetime.now(timezone.utc).isoformat(),'commands':[],'helper_sha256':digest(helper),'proposal_sha256':digest(E/'proposal.json'),'input_bindings':inputs,'tool_bindings':tools,'manuals':manual_records,'abi_log_replay':{'configured_log':record(logpath),'events':replays,'commands':6,'new_native_builds':0},'old_os_runtime_evidence':loaded_records,'maintained_hashes_before':before,'control_hashes':control_hashes,'prior_help_receipt_scope':'preparation-checks.json help ran earlier 319-line e1873100 candidate; own --help below runs the current 322-line helper.'}
def save():write('static-checks.json',report)
runner=ROOT/'evidence/p2996-math-resume/operation/p2996_build.py.source';assert digest(runner)=='7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
node=next(n for n in ast.walk(ast.parse(runner.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='run');scope=globals()|{'env':env,'save':save,'directory':directory,'report':report}
exec(compile(ast.Module(body=[node],type_ignores=[]),str(runner),'exec'),scope);run=scope['run']
def interrupted(signum,frame):raise KeyboardInterrupt('received signal '+str(signum))
for signum in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(signum,interrupted)
git=['/usr/bin/git','--no-optional-locks','-c','core.fsmonitor=false','-C',ROOT]
try:
 ids=run('identity',git+['rev-parse','--show-toplevel','--git-common-dir','HEAD']).splitlines();branch=run('branch',git+['symbolic-ref','--short','HEAD']).strip()
 assert ids==[str(ROOT),'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git',proposal['base_head']] and branch=='codex/marketplace-native-onboarding'
 report['identity']={'root':ids[0],'common_git_directory':ids[1],'head':ids[2],'branch':branch}
 assert set(run('changed-files',git+['diff','--name-only']).splitlines())==set(maintained[1:]);run('planning-diff',git+['diff','--',*maintained])
 help_text=run('helper-help',[PYTHON,'-B',helper,'--help'],timeout=30);assert 'usage: core_matrix.py [-h] --run-dir RUN_DIR' in help_text
 run('tasks-validate',[ROOT/'dev/mise','tasks','validate'],timeout=45)
 check_text=run('acceptance-baseline',[ROOT/'dev/mise','run','check:acceptance-baseline'],timeout=45);checks=json.loads(next(s for s in check_text.splitlines() if s.startswith('{')))
 assert checks['status']=='pass' and checks['checks']['baseline']==19;report['static_counts']=checks['checks']
 status=run('status',git+['status','--porcelain','--untracked-files=normal']);assert set(s[3:] for s in status.splitlines())==set(maintained)|{'evidence/core-p2996/'};report['status']=status
 assert {p:digest(ROOT/p) for p in maintained}==before and {p:digest(Path(p)) for p in control_hashes}==control_hashes
 assert all(digest(ROOT/p)==s for p,s in proposal['inputs'].items()) and all(digest(Path(p))==s for p,s in proposal['tool_hashes'].items())
 report.update(state='PASS: 03b2b pre-run source bindings, retained ABI replay, help and lightweight checks',all_candidate_control_input_tool_hashes_unchanged=True)
except BaseException as error:report.update(state='FAIL',error=repr(error));raise
finally:report['finished_at']=datetime.now(timezone.utc).isoformat();save()
print(json.dumps({'state':report['state'],'commands':len(report['commands']),'exits':{r['case']:r['returncode'] for r in report['commands']},'static_counts':report.get('static_counts'),'input_bindings':len(inputs),'tool_bindings':len(tools),'old_abi_command_replays':6}),flush=True)
