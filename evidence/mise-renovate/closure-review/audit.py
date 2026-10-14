from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,subprocess
D=Path(__file__).parent
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/mise-renovate'
PRIOR=Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-mise-two-path-review-v2r8tbbl')
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def forbidden(*args,**kwargs):raise AssertionError('artifact-only audit forbids native commands')
for name in ['Popen','run','call','check_call','check_output']:setattr(subprocess,name,forbidden)
os.system=forbidden
F=load(D/'frozen-inputs.json')['files']
def unchanged():
 for name,row in F.items():assert sha(R/name)==row['sha256'] and (R/name).stat().st_size==row['bytes'],name
unchanged()
gd=(R/Path((R/'.git').read_text().strip().removeprefix('gitdir: '))).resolve();common=(gd/(gd/'commondir').read_text().strip()).resolve();ref=(gd/'HEAD').read_text().strip().removeprefix('ref: ');head=(common/ref).read_text().strip()
assert head=='e66a60c3e7fe76be39169986b1eb3aed6bccc2c6' and ref=='refs/heads/codex/marketplace-native-onboarding'
closure=load(E/'closure-candidate.json');data=load(E/'contract.json');q=load(E/'operation/qualification.json');execution=load(E/'native-execution.json');ad=load(E/'admission.json');review=load(E/'pre-run-review.json');legacy=load(R/'evidence/mise-runtime/contract.json')
assert sha(E/'closure-candidate.json')=='7e33a1e6b6934260ae2a8392408310aecf1f0a4b7cdbcbee92a12f09cebb549d'
assert sha(E/'native-execution.json')==closure['native_execution_sha256']=='021d4454727b79735eb99cb07e276167ab70b55830933dde6d618a03bbcfb37e'
assert sha(E/'operation/qualification.json')==execution['qualification_sha256']=='12a3d38e28d84179d2b79f5a2983a146983b2ffc87e078cd3852fafefd5cefcc'
assert (R/'dev/toolchains/mise_renovate.py').read_bytes()==(PRIOR/'frozen-helper.py').read_bytes()==(E/'operation/mise_renovate.py.source').read_bytes()
assert (E/'contract.json').read_bytes()==(PRIOR/'frozen-contract.json').read_bytes()
assert (E/'pre-run-review.json').read_bytes()==(PRIOR/'review.json').read_bytes()
assert (E/'candidate.json').read_bytes()==(PRIOR/'frozen-candidate.json').read_bytes()
assert review['result']=='PASS' and review['findings']==[]
assert q['helper_sha256']==ad['helper_sha256']==execution['helper_sha256']==review['helper_sha256']==sha(R/'dev/toolchains/mise_renovate.py')
assert q['contract_sha256']==ad['contract_sha256']==execution['contract_sha256']==review['contract_sha256']==closure['contract_sha256']==sha(E/'contract.json')
assert q['admission_sha256']==execution['admission_sha256']==sha(E/'admission.json')
assert ad['review_sha256']==execution['pre_run_review_sha256']==sha(E/'pre-run-review.json')
assert ad['candidate_sha256']==sha(E/'candidate.json') and ad['base_head']==closure['head']==data['base_head']==head
for name,h in closure['files'].items():assert sha(R/name)==h,name
for name,h in data['inputs'].items():assert sha(R/name)==h,name
assert execution['returncode']==0 and execution['commands']==15 and execution['command_returncodes']==[0]*15
assert q['state']=='PASS: observed mise metadata and existing profile parity; shared state unchanged'
assert q['protected_state_unchanged'] is True and execution['protected_state_unchanged'] is True
assert 'error' not in q and 'preservation_error' not in q
run_dir=Path(ad['run_directory']);assert run_dir.is_absolute() and run_dir==run_dir.resolve()
assert execution['argv']==[data['python'],'-B','dev/toolchains/mise_renovate.py','--run-dir',str(run_dir)]
copies=load(E/'operation-copy-manifest.json')['files'];assert len(copies)==32
for row in copies:
 source=Path(row['source']);target=R/row['copy']
 assert sha(source)==sha(target)==row['sha256'] and source.read_bytes()==target.read_bytes(),row['copy']
 assert source.parent==run_dir or source==R/'dev/toolchains/mise_renovate.py'
normal=load(R/'evidence/gcc-bootstrap/install-preimages.json')['normal_environment']['argv']
profile_tail=normal[-2:];mise=legacy['current_mise']['path'];lanes=list(legacy['profiles'])
assert lanes==['default','cpp-build','p2996','gcc16'] and set(q['path_transitions'])==set(lanes)
labels=['project-head','version']+[lane+suffix for lane in lanes for suffix in ['-profile','-path-transition','-isolation']]+['default-after']
assert [row['case'] for row in q['commands']]==labels
rows={row['case']:row for row in q['commands']};logs=[];timings=[]
for row in q['commands']:
 assert row['returncode']==0 and 0<=row['elapsed_seconds']<35
 assert len(row['logs'])==2 and [Path(x['path']).name for x in row['logs']]==[row['case']+'.stdout',row['case']+'.stderr']
 for entry in row['logs']:
  source=Path(entry['path']);target=E/'operation'/source.name
  assert source.parent==run_dir and source.read_bytes()==target.read_bytes() and sha(source)==entry['sha256']
  logs.append({'name':source.name,'sha256':entry['sha256'],'bytes':target.stat().st_size})
 assert not (E/'operation'/(row['case']+'.stderr')).read_bytes()
 timings.append(datetime.fromisoformat(row['started_at']))
assert timings==sorted(timings) and len({row['pid'] for row in q['commands']})==15
assert rows['project-head']['argv']==['/usr/bin/git','-C',str(R),'rev-parse','HEAD']
assert rows['version']['argv']==[mise,'--version']
assert (E/'operation/project-head.stdout').read_text().strip()==head
assert (E/'operation/version.stdout').read_text().strip()==legacy['current_mise']['version']
program="import json,os,sys;sys.path.insert(0,"+repr(str(R/'dev/toolchains'))+");from mise_renovate import path_transition;print(json.dumps(path_transition(os.environ['PATH'],json.loads(sys.argv[1]))))"
isolation_program='import json,os,sys;print(json.dumps({k:os.environ.get(k) for k in sys.argv[1:]}))'
profiles=[]
for lane in lanes:
 base=[mise,'--no-hooks','-C',str(run_dir/'cwd')]+([] if lane=='default' else ['-E',lane])+['exec','--fresh-env','--no-deps','--']
 assert rows[lane+'-profile']['argv']==base+profile_tail
 assert rows[lane+'-path-transition']['argv']==base+[data['python'],'-B','-c',program,json.dumps(data['path_transition'])]
 assert rows[lane+'-isolation']['argv']==base+[data['python'],'-B','-c',isolation_program,*legacy['isolation_keys']]
 observed=load(E/'operation'/(lane+'-profile.stdout'));expected=load(R/legacy['profiles'][lane]);proof=load(E/'operation'/(lane+'-path-transition.stdout'));isolation=load(E/'operation'/(lane+'-isolation.stdout'))
 assert set(observed)==set(expected) and {k for k in expected if observed[k]!=expected[k]}=={'path_sha256'}
 assert proof==q['path_transitions'][lane]=={'path_sha256':observed['path_sha256'],'previous_path_sha256':expected['path_sha256'],'replacements':2}
 assert type(proof['replacements']) is int
 expected_isolation={k:observed['selected'].get(k) for k in legacy['isolation_keys']}
 assert isolation==expected_isolation
 if lane!='default':assert isolation==dict.fromkeys(legacy['isolation_keys'])
 profiles.append({'lane':lane,'previous_profile':legacy['profiles'][lane],'previous_profile_sha256':sha(R/legacy['profiles'][lane]),'observed_profile_sha256':sha(E/'operation'/(lane+'-profile.stdout')),'only_difference':['path_sha256'],'proof':proof,'isolation_keys':len(isolation),'isolation_pass':True})
assert rows['default-after']['argv']==normal
assert (E/'operation/default-after.stdout').read_bytes()==(E/'operation/default-profile.stdout').read_bytes()
assert len(load(E/'operation/default-profile.stdout')['selected'])==32
for key in ['writer_census_before','writer_census_after']:
 census=q[key];assert census['lock_holder_check_rc']==1 and census['lock_holders']==[]
 assert all(x['known_task'] in ['mcp:graphify','mcp:cbm','mcp:tr'] for x in census['processes'])
assert datetime.fromisoformat(q['writer_census_before']['at'])<timings[0]<timings[-1]<datetime.fromisoformat(q['writer_census_after']['at'])
failures=[]
for name,n in [('initial-attempt',3),('path-attempt',4)]:
 oldq=load(E/name/'qualification.json');oldex=load(E/name/'execution.json')
 assert oldq['state']=='FAIL' and oldex['returncode']==1 and len(oldq['commands'])==n and all(x['returncode']==0 for x in oldq['commands'])
 assert oldex['qualification_sha256']==sha(E/name/'qualification.json') and oldq['protected_state_unchanged'] is True
 for row in oldq['commands']:
  for entry in row['logs']:
   source=Path(entry['path']);target=E/name/source.name
   assert sha(source)==sha(target)==entry['sha256'] and source.read_bytes()==target.read_bytes()
 failures.append({'attempt':name,'wrapper_rc':1,'child_count':n,'qualification_sha256':sha(E/name/'qualification.json'),'preserved':True})
closure_copies=load(E/'closure-copy-verification.json')
for row in closure_copies['exact_copies']:assert sha(R/row['path'])==row['sha256'],row['path']
for row in closure_copies['historical_source_versions']:
 assert sha(R/row['retained_copy'])==row['retained_sha256']
 assert data['inputs'][row['retained_copy']]==row['retained_sha256']
assert len(closure_copies['historical_target_aliases'])==1
alias=closure_copies['historical_target_aliases'][0]
assert alias['manifest']=='evidence/mise-renovate/review-copy-manifest.json' and alias['historical_alias']=='evidence/mise-renovate/pre-run-review.json'
assert alias['retained_copy']=='evidence/mise-renovate/initial-attempt/pre-run-review.json'
assert sha(R/alias['retained_copy'])==alias['retained_sha256']=='ad2f3cd2d89327d2ebaa93d0cf7d28d2089b01dbd81503dbad7d7a9350e91d1a'
assert sha(R/alias['historical_alias'])==alias['current_review_sha256']==sha(PRIOR/'review.json')
original_review=(R/alias['retained_copy']).read_bytes()
assert original_review==(E/'pre-run-review/review.json').read_bytes()
alias_record=next(row for row in load(R/alias['manifest'])['files'] if row['copy']==alias['historical_alias'])
assert Path(alias_record['source']).read_bytes()==original_review and alias_record['sha256']==alias['retained_sha256']
assert closure_copies['initial_audit_exit_code']==1
baseline=load(R/'evidence/onboarding/baseline-files.json')['files']
for row in baseline:assert sha(R/row['path'])==row['sha256'] and (R/row['path']).stat().st_size==row['bytes']
unchanged()
result={'result':'PASS','at':datetime.now(timezone.utc).isoformat(),'scope':'Filesystem-only artifact comparisons; no candidate execution','head':head,'common_git_directory':str(common),'helper_sha256':sha(R/'dev/toolchains/mise_renovate.py'),'contract_sha256':sha(E/'contract.json'),'closure_candidate_sha256':sha(E/'closure-candidate.json'),'qualification_sha256':sha(E/'operation/qualification.json'),'native_execution_sha256':sha(E/'native-execution.json'),'admission_sha256':sha(E/'admission.json'),'pre_run_review_sha256':sha(E/'pre-run-review.json'),'native_admitted_candidate_sha256':sha(E/'candidate.json'),'contract_inputs':len(data['inputs']),'closure_files':len(closure['files']),'native_copy_pairs':len(copies),'native_child_count':len(q['commands']),'native_child_rcs':[row['returncode'] for row in q['commands']],'native_log_files':logs,'profiles':profiles,'final_default_byte_equal':True,'retained_wrapper_rc':execution['returncode'],'recorded_full_protection_pass_before_after':True,'protection_replayed':False,'retained_failures':failures,'closure_report_copy_hash_records':len(closure_copies['exact_copies']),'historical_source_versions':len(closure_copies['historical_source_versions']),'historical_target_aliases_verified':[alias],'original_Claude_hashes_and_sizes':len(baseline),'watched_files_unchanged':len(F),'candidate_imports':0,'native_commands_by_reviewer':0,'main_calls':0,'protected_calls':0,'current_global_inventory_checks':0,'unit_tests_rerun':0}
(D/'artifact-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':'PASS','native_copy_pairs':len(copies),'logged_child_commands':len(q['commands']),'exact_profile_comparisons':len(profiles),'retained_failures':len(failures),'historical_aliases':1,'native_replays':0,'watched_files':len(F)}))
