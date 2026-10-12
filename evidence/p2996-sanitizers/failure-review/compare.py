from pathlib import Path
from datetime import datetime
import hashlib,json,os,stat
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-sanitizers'
HERE=Path(__file__).parent
HEAD='ad2880bf4fedf9222cdcdff52cc4ec49d412b95e'
cache={};watched={}
def raw(p):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 if str(p) not in cache:
  cache[str(p)]=p.read_bytes();watched[str(p)]=hashlib.sha256(cache[str(p)]).hexdigest()
 return cache[str(p)]
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def obj(p):return json.loads(raw(p))
def moment(s):return datetime.fromisoformat(s)
F='9d63868ccf834f31fcb6f4d81e0c4beaddf638c42fccd68a2914876e950ddcad'
H='15800f647fa9fd39d553a5bc505da63ed41cef55fa53dcfa6569fa1e8f1117e6'
C='4e5e3bc187c0d0f19c71be093c020deb5dd7eb02a12ac93ee198f57cebd249bb'
P='31175bc34f25e5dcd4e84a5f9d6cb4fe4dbd58e4347b97b56243b25b6af6722d'
R='4391b2d2b7de85875b28c7da29bc4bd214a58c779855ed8d612d3560dc2567c2'
D='92be06211b634146c9ab2f9a8253b6a84e5e7440089accceb8ad3ec981eaac73'
assert sha(E/'failure-candidate.json')==F
candidate=obj(E/'failure-candidate.json');assert candidate['head']==HEAD and len(candidate['files'])==5
for path,expected in candidate['files'].items():assert sha(path)==expected,(path,'candidate')
assert sha(ROOT/'dev/toolchains/p2996_sanitizers.py')==H and sha(E/'contract.json')==C
assert sha(E/'candidate.json')==candidate['native_preparation_candidate_sha256']==P
assert sha(E/'pre-run-review.json')==candidate['review_sha256']==R
prior=obj(E/'pre-run-review.json');assert prior['result'].startswith('PASS') and prior['findings']==[]
assert raw(E/'pre-run-review.json')==raw('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-editor-r1-disposition-ps_ctbm0/review.json')
assert sha(E/'startup-diagnosis.json')==candidate['diagnosis_sha256']
contract=obj(E/'contract.json'); snapshots=obj(E/'failure-inputs.json')['files'];assert len(snapshots)==8
for row in snapshots:assert row['text'].encode()==raw(row['path']) and sha(row['path'])==row['sha256']
prep=obj(E/'startup-preparation-copy-manifest.json');assert len(prep)==12
for row in prep:assert sha(row['copy'])==row['sha256']
prepmap={row['source']:row for row in prep}
oldsnaps=obj(E/'startup-preparation/candidate-inputs.json')['files'];assert len(oldsnaps)==8
for row in oldsnaps:
 b=row['text'].encode();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 assert raw(prepmap[row['source']]['copy'])==b
assert sha(E/'startup-preparation/candidate.json')==P and sha(E/'startup-preparation/pre-run-review.json')==R
assert sha(E/'startup-preparation/contract.json')==C
for path in ['dev/toolchains/p2996_sanitizers.py','dev/toolchains/sanitizer_witness.cpp']:
 assert raw(path)==raw(prepmap[str(ROOT/path)]['copy'])
assert sha('/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-sanitizers-editor-repair-gqjr4k4n/dispatch.py')==D
capacity_names=['retry-capacity','retry-capacity-2','diagnostic-capacity','diagnostic-capacity-2']
expected_cases=['project-head','default-before','capacity-processes','editor-identities','editor-cwd','editor-identities-after','docker-context','docker-census','docker-stats','asan-core','asan-link','asan-arch-object','asan-arch-binary','asan-clean']
expected_counts=[4,33,38,40]
rows_checked=0;copies_checked=12;capacity_copies=0;log_count=0;attempts=[];new_artifacts=[];defaults=set();previous_closure=None
for i in range(1,5):
 adir=E/f'native-attempt-{i}'
 admission=obj(adir/'admission.json');launch=obj(adir/'native-launch.json');execution=obj(adir/'native-execution.json');q=obj(adir/'qualification.json');closure=obj(adir/'closure.json')
 op=Path(admission['run_directory']);lp=Path(execution['private_launch_directory'])
 assert admission['base_head']==HEAD and admission['helper_sha256']==H and admission['contract_sha256']==C and admission['candidate_sha256']==P and admission['review_sha256']==R
 assert execution['returncode']==1 and execution['helper_sha256']==H and execution['dispatch_sha256']==D
 assert execution['argv']==[execution['argv'][0],'-E','-B',str(ROOT/'dev/toolchains/p2996_sanitizers.py'),'--run-dir',str(op),'--build']
 assert execution['argv'][0]=='/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3'
 assert all(execution[k]==v for k,v in launch.items()) and execution['admission_sha256']==sha(adir/'admission.json')
 assert 0<execution['elapsed_seconds']<45 and moment(execution['started_at'])<moment(execution['finished_at'])<moment(closure['recorded_at'])
 assert q['state']=='FAIL' and q['helper_sha256']==H and q['admission_sha256']==sha(adir/'admission.json') and q['protected_state_unchanged'] is True
 assert raw(op/'qualification.json')==raw(adir/'qualification.json')
 assert closure['native_returncode']==1 and closure['protected_state_unchanged'] is True and closure['lease_probe']=={'free':True,'contents_unchanged':True}
 assert sha(adir/'closure.json')==candidate['closures'][str((adir/'closure.json').relative_to(ROOT))]
 copies=obj(adir/'copy-manifest.json')
 for row in copies:
  assert sha(row['copy'])==row['sha256'];copies_checked+=1
  if not Path(row['source']).is_relative_to(ROOT):assert raw(row['source'])==raw(row['copy'])
 tpath=adir/('launch-texts.json' if i==1 else 'text-receipts.json');texts=obj(tpath)['files']
 assert len(texts)==expected_counts[i-1] and len({r['source'] for r in texts})==len(texts)
 tmap={row['source']:row for row in texts}
 for row in texts:
  b=row['text'].encode();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and b==raw(row['source']),(i,row['source'])
  rows_checked+=1
 for name,target in [('launch.json','native-launch.json'),('execution.json','native-execution.json')]:assert raw(lp/name)==raw(adir/target)
 for name in ['stdout','stderr']:assert sha(lp/name)==execution[name+'_sha256']
 stdout=[json.loads(line) for line in raw(lp/'stdout').decode().splitlines()]
 assert stdout[-1]=={'state':'FAIL','receipt':str(op/'qualification.json')}
 capname=capacity_names[i-1];cap=obj(E/capname/'capacity.json');ce=obj(E/capname/'execution.json')
 assert sha(E/capname/'capacity.json')==admission['capacity_sha256'] and cap['state']=='PASS' and ce['returncode']==0
 assert cap['script_sha256']=='bd0119ad9741bd7d4d3f75c72839bba70e75edf61aecb0355bedd3e6f8645060'
 assert cap['held_lease'] is False and cap['native_operation_started'] is False
 assert moment(cap['recorded_at'])<moment(admission['recorded_at'])<=moment(execution['started_at'])
 assert cap['admitted_editor_services']==['73356','73398'] and cap['docker_context']==admission['docker_context'] and cap['containers']==admission['containers']
 cm=obj(E/(capname+'-copy-manifest.json'))
 for row in cm:
  target=row['copy'] if i<=2 else row['destination']
  assert raw(row['source'])==raw(target) and sha(target)==row['sha256'];capacity_copies+=1
 for command in cap['commands']:
  assert command['returncode']==0 and command['elapsed_seconds']<command['timeout_seconds']
  for log in command['logs']:assert sha(log['path'])==log['sha256']
 if i==1:
  assert q['commands']==[] and q['cells']=={} and stdout==[stdout[-1]]
  assert closure['native_commands']==0 and closure['native_cells']==0 and closure['writer_census_error']==q['error']
  probe=closure['process_check'];assert probe['returncode']==1 and probe['stdout']==probe['stderr']=='' and str(execution['pid']) in probe['argv'][2]
  assert '18457' in q['error'] and 'known_task' in q['error'] and 'AssertionError' in raw(lp/'stderr').decode()
 else:
  cmds=q['commands'];assert [c['case'] for c in cmds]==expected_cases and [c['returncode'] for c in cmds]==[0]*13+[-15]
  assert stdout[:-1]==[{'case':c['case'],'returncode':0} for c in cmds[:-1]]
  assert 'TimeoutExpired' in q['error'] and 'timed out after 20 seconds' in raw(lp/'stderr').decode()
  assert set(q['cells'])=={'asan'} and q['cells']['asan']['runs']=={} and len(q['cells']['asan']['artifacts'])==2
  assert closure['native_execution_sha256']==sha(adir/'native-execution.json') and closure['qualification_sha256']==sha(adir/'qualification.json')
  assert closure['retained_text_files']==len(texts) and closure['text_receipts_sha256']==sha(tpath) and closure['command_count']==14 and closure['reflection_stdout_reached'] is False
  statuses=[{'case':c['case'],'pid':c['pid'],'absent':True} for c in cmds]
  if i>=3:
   statuses.insert(0,{'case':'native-helper','pid':execution['pid'],'absent':True})
   assert closure['command_outcomes']==[{'case':c['case'],'returncode':c['returncode']} for c in cmds]
  else:
   assert closure['completed_zero_exit_commands']==13 and closure['runtime_limit_seconds']==20 and closure['terminated_runtime_returncode']==-15 and closure['default_after_executed'] is False
  assert closure['processes']==statuses
  for command in cmds:
   assert moment(execution['started_at'])<=moment(command['started_at'])<moment(execution['finished_at'])
   for log in command['logs']:
    assert log['path'] in tmap and tmap[log['path']]['sha256']==log['sha256'];log_count+=1
   if command['returncode']==0:assert command['elapsed_seconds']<command['timeout_seconds'] and command['expected_returncode']==0
  defaults.add(sha(op/'default-before.stdout'));assert raw(op/'project-head.stdout').decode().strip()==HEAD
  for kind in ['object','binary']:
   row=q['cells']['asan']['artifacts'][kind];assert Path(row['path']).parent==op/'asan';new_artifacts.append(dict(attempt=i,kind=kind,**row))
   assert raw(op/('asan-arch-'+kind+'.stdout')).decode().strip()=='arm64'
  for case in ['asan-core','asan-link']:
   argv=next(c['argv'] for c in cmds if c['case']==case)
   assert argv[:3]==['/usr/bin/sandbox-exec','-f',str(op/'private.sb')]
   assert '-fsanitize=address' in argv and '-std=c++26' in argv and '-fno-blocks' in argv and argv[argv.index('-arch')+1]=='arm64'
   assert ('-freflection' in argv)==(case=='asan-core') and '-O1' in argv and '-g' in argv
  runtime=cmds[-1];assert runtime['interrupted'] is True and 20<=runtime['elapsed_seconds']<22 and raw(op/'asan-clean.stdout')==b''
  assert runtime['argv'][:3]==['/usr/bin/sandbox-exec','-f',str(op/'private.sb')]
  assert runtime['argv'][-3:-1]==[str(op/'asan/witness'),'clean'] and json.loads(runtime['argv'][-1])==contract['runtime_environment']
  trace=raw(op/'asan-clean.stderr').decode();assert any(line.startswith('dyld['+str(runtime['pid'])+']') and line.endswith('/libclang_rt.asan_osx_dynamic.dylib') for line in trace.splitlines())
  if i==2:assert closure['arm64_artifacts']==q['cells']['asan']['artifacts']
 if i>=3:
  diag=obj(adir/'startup-diagnostic.json');assert diag['admission_sha256']==sha(adir/'admission.json') and diag['native_execution_sha256']==sha(adir/'native-execution.json') and diag['native_dispatch_returncode']==1
  driver=next(row for row in texts if row['source'].endswith('/diagnose.py'));assert driver['sha256']==diag['driver_sha256']==admission['diagnostic_driver_sha256']
  assert diag['launch']=={'native_pid':execution['pid'],'directory':str(op),'launch_directory':str(lp)}
  meta=diag['identity'];pid=cmds[-1]['pid'];assert meta['returncode']==0 and meta['stderr']=='' and meta['stdout'].strip().split(maxsplit=3)==[str(pid),str(execution['pid']),str(pid),str(op/'asan/witness')]
  dd=Path(driver['source']).parent;assert obj(dd/'diagnostic.json')==diag and raw(dd/'dispatch.stderr')==b''
  dispatch_lines=[json.loads(line) for line in raw(dd/'dispatch.stdout').decode().splitlines()]
  assert dispatch_lines==[diag['launch'],execution]
  assert admission['previous_attempt_closure_sha256']==previous_closure
  if i==3:
   assert diag['sample_attempted'] is False and 'sample' not in diag and diag['diagnostic_error']=='AssertionError()'
   assert meta['stdout'].split(maxsplit=3)[-1]!=str(op/'asan/witness') and 'meta.stdout.split(maxsplit=3)' in driver['text']
  else:
   assert diag['sample_attempted'] is True and 'diagnostic_error' not in diag and 'meta.stdout.strip().split(maxsplit=3)' in driver['text']
   sample=diag['sample'];assert sample['returncode']==0 and sample['timed_out'] is False and sample['elapsed_seconds']<10
   assert sample['argv']==['/usr/bin/sandbox-exec','-f',str(op/'private.sb'),'/usr/bin/sample',str(pid),'1','1','-mayDie','-file',str(op/'startup.sample.txt')]
   assert sha(op/'startup.sample.txt')==sample['output']['sha256']=='8d9612febf700db855fce0c6456629e1f6852e7512c0611ea372c9acf1c76840'
   for n in ['stdout','stderr']:assert sha(dd/('sample.'+n))==sample[n+'_sha256']
   diagnosis=obj(E/'startup-diagnosis.json');assert diagnosis['diagnostic_sha256']==sha(adir/'startup-diagnostic.json') and diagnosis['sample_returncode']==0 and diagnosis['sample_duration_seconds']==1 and diagnosis['native_runtime_timeout_seconds']==20
   assert raw(diagnosis['copy'])==raw(diagnosis['source'])==raw(op/'startup.sample.txt') and diagnosis['sha256']==sample['output']['sha256']
   sampled=raw(op/'startup.sample.txt').decode()
   for symbol in ['662','AsanInitFromRtl','AsanInitInternal','get_dyld_hdr','dyld_shared_cache_iterate_text_swift','_Block_copy','StaticSpinMutex','wrap_malloc_default_zone']:assert symbol in sampled,symbol
   assert sampled.count('AsanInitFromRtl')>=2
 previous_closure=sha(adir/'closure.json')
 attempts.append(dict(attempt=i,returncode=execution['returncode'],qualification_sha256=sha(adir/'qualification.json'),closure_sha256=previous_closure,commands=len(q['commands']),successful_commands=sum(c['returncode']==0 for c in q['commands']),elapsed_seconds=execution['elapsed_seconds'],text_pairs=len(texts)))
assert rows_checked==115 and log_count==84 and len(new_artifacts)==6 and len(defaults)==1
static=obj(E/'failure-static.json');assert [c['returncode'] for c in static['commands']]==[0,0]
baseline=json.loads(static['commands'][1]['stdout']);assert baseline['checks']['baseline']==19 and baseline['status']=='pass'
scan=obj(E/'failure-secret-scan.json');assert len(scan['files'])==204 and scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[] and len(scan['dispositions'])==32
for row in scan['dispositions']:assert sha(row['path'])==row['sha256'] and row['reason']=='Verified exact file-content digest'
scan_bindings=0
for path,expected in scan['files'].items():
 full=str(ROOT/path)
 if full in watched:assert watched[full]==expected;scan_bindings+=1
# Check each newly produced binary once, after all text and receipt assertions.
for row in new_artifacts:
 p=Path(row['path']);s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_size>0
 with p.open('rb') as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
 assert actual==row['sha256'];row['bytes']=s.st_size
 if row['kind']=='binary':assert s.st_mode&0o111
# Freeze only already-read bounded text files; do not read the six binaries again.
for path,expected in watched.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected,(path,'changed during review')
result=dict(result='PASS: honest failed-operation closure only',runtime_qualification='FAIL / INCOMPLETE; zero completed sanitizer runtime cases',findings=[],candidate_sha256=F,helper_sha256=H,contract_sha256=C,review_sha256=R,attempts=attempts,text_copy_pairs=rows_checked,command_logs_bound=log_count,current_snapshots=8,startup_preparation_copies=12,archival_copy_rows=copies_checked,capacity_copy_pairs=capacity_copies,new_artifacts_hashed_once=new_artifacts,default_before_sha256=next(iter(defaults)),default_after_executed=False,static_recorded_returncodes=[0,0],static_baseline_hash_count=19,scan_recorded_files=204,scan_current_scope_bindings_verified=scan_bindings,scan_dispositions_verified=32,watched_text_sha256=watched)
(HERE/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['watched_text_sha256','new_artifacts_hashed_once']}))
