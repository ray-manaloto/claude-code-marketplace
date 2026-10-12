"""Bounded read-only comparison for the original Task14a2 candidate."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, os, posixpath, stat
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-asan-runtime';D=Path(__file__).parent
watched={};checks={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,h=None):
 p=Path(p);b=p.read_bytes();actual=sha(b)
 if h is not None:assert actual==h,(str(p),actual,h)
 watched[str(p)]=actual;return b
def data(p,h=None):return json.loads(read(p,h))
c=data(E/'candidate.json','5c1131152fa9195a2fc26ff386280bbde34cd193573033b48205bc4d9bf90b9a')
contract=data(E/'contract.json',c['contract_sha256'])
assert contract['base_head']==c['head']=='b452c6d64a125b8c4f3766dcb3093220bf70b7ed'
for rel,h in c['files'].items():read(ROOT/rel,h)
snaps=data(E/'candidate-inputs.json','dd3bd08ce58807a398719e6070d4c927fc79ecb46c9bce6ab5fd1ce29fc2b6c5')['files'];assert len(snaps)==6
for row in snaps:
 b=read(row['source'],row['sha256']);assert b==row['text'].encode() and len(b)==row['bytes']
for name in ('candidate.json','candidate-inputs.json','contract.json','controls-execution.json','pre-review-static.json','pre-review-secret-scan.json'):
 assert read(E/name)==read(D/('original-'+name))
checks['maintained_files']=4;checks['exact_current_snapshots']=6
assert len(contract['inputs'])==19
for rel,h in contract['inputs'].items():read(ROOT/rel,h)
checks['small_project_input_hashes']=19
replacement=contract['qualified_replacement'];inventory=data(ROOT/contract['artifact_inventory']);prefix_members=data(ROOT/contract['prefix_inventory'])
assert inventory['prefix']==contract['prefix']
rows=[r for r in inventory['records'] if r['path']==contract['target'] or r.get('resolved_path')==contract['target']]
assert rows==[contract['previous_record']]
RUNTIME='lib/clang/21/lib/darwin/libclang_rt.asan_osx_dynamic.dylib'
assert [r for r in prefix_members if r['path']==RUNTIME]==[contract['previous_prefix_record']]
links={posixpath.join(contract['prefix'],r['path']):posixpath.normpath(posixpath.join(contract['prefix'],posixpath.dirname(r['path']),r['target'])) for r in prefix_members if r['kind']=='symlink'}
def resolve_recorded(path):
 for _ in range(len(links)+1):
  cursor=path
  while cursor.startswith(contract['prefix']):
   if cursor in links:
    path=posixpath.normpath(links[cursor]+path[len(cursor):]);break
   cursor=posixpath.dirname(cursor)
  else:return path
 raise AssertionError('recorded symlink cycle')
assert not [p for p in links if resolve_recorded(p)==contract['target']]
ti=data(E/'target-inventory.json')
assert ti['artifact_matching_rows']==ti['prefix_matching_rows']==1 and ti['prefix_symlink_aliases']==[] and ti['historical_inventories_unchanged']
topology=[]
for p in [Path(contract['target']),Path(replacement['path'])]:
 s=p.lstat();assert p.is_absolute() and p==p.resolve(strict=True) and stat.S_ISREG(s.st_mode) and s.st_nlink==1 and s.st_uid==os.geteuid()
 topology.append(dict(path=str(p),mode=oct(stat.S_IMODE(s.st_mode)),links=s.st_nlink,bytes=s.st_size,canonical=True,regular=True,content_read=False))
assert [r['mode'] for r in topology]==[ti['target_mode'],ti['replacement_mode']]==['0o755','0o700']
assert topology[0]['bytes']==contract['previous_record']['bytes'] and topology[1]['bytes']==replacement['bytes']
checks['exact_target_inventory_rows_and_no_recorded_aliases']=True
checks['two_target_metadata_only']=topology
r=data(ROOT/'evidence/p2996-sanitizer-repair/artifact-review.json');q=data(ROOT/'evidence/p2996-sanitizer-repair/operation/qualification.json');art=data(ROOT/'evidence/p2996-sanitizer-repair/artifact-inventory.json')
assert r['result'].startswith('PASS') and not r['findings'] and q['state'].startswith('PASS') and q['protected_state_unchanged'] and q['lease_released']
assert r['qualification_sha256']==sha(read(ROOT/'evidence/p2996-sanitizer-repair/operation/qualification.json'))
assert r['artifact_inventory_sha256']==sha(read(ROOT/'evidence/p2996-sanitizer-repair/artifact-inventory.json'))
assert [row for row in art['artifacts'] if row['kind']=='patched-runtime']==[replacement]
assert q['repair']['patched']['sha256']==contract['current_asan']['sha256']==replacement['sha256']
assert replacement['bytes']==contract['current_asan']['bytes']
checks['qualified_replacement_binding_only_no_artifact_rehash']=True
manifest=data(E/'controls-copy-manifest.json')['files'];assert len(manifest)==26
for row in manifest:
 b=read(row['source'],row['sha256']);assert len(b)==row['bytes'] and b==read(ROOT/row['destination'],row['sha256'])
checks['private_exact_text_copy_pairs']=26
report=data(E/'controls/controls.json',c['controls_sha256']);execution=data(E/'controls-execution.json')
assert execution['returncode']==0 and execution['receipt_sha256']==c['controls_sha256']
assert report['helper_sha256']==c['files']['dev/toolchains/p2996_asan_runtime.py'] and report['contract_sha256']==c['contract_sha256']
assert report['script_sha256']==execution['script_sha256']==sha(read(E/'controls/controls.py.source'))
assert execution['stderr']==''
outer=json.loads(execution['stdout']);assert outer['state']==report['state'] and outer['controls']==len(report['controls'])==32 and outer['commands']==len(report['commands'])==11
assert report['original_installed_runtime_unchanged'] and report['historical_inputs_unchanged'] and report['qualified_replacement_executed'] is False
private=Path(execution['argv'][-1]).parent
assert outer['receipt']==str(private/'controls.json')
assert sha(read(private/'controls.py'))==execution['script_sha256']
by_case={r['case']:r for r in report['controls']};assert len(by_case)==32
composition=by_case['real-wrapper-composition']
assert composition=={'case':'real-wrapper-composition','result':'PASS','events':['renovate-semantic-check-called','reflection-guard-reached-with-all-three-overlays'],'mocked_digest_calls':63,'live_shared_guard_executed':False}
expected_labels=['positive-replace','positive-restore','wrong-source','wrong-destination','source-symlink','destination-symlink','source-hardlink','destination-hardlink','source-mode','destination-mode','outside-allowlist']
assert [r['case'] for r in report['commands']]==expected_labels
outcomes=[]
for row in report['commands']:
 name=row['case'];expected=0 if name.startswith('positive-') else 1
 assert row['returncode']==expected and 0<row['elapsed_seconds']<15
 argv=row['argv'];assert argv[:3]==['/usr/bin/sandbox-exec','-f',str(private/'private.sb')]
 assert argv[3:7]==['/Users/rmanaloto/.local/share/mise/installs/python/3.15.0/bin/python3','-E','-B',str(private/'replace.py')]
 assert Path(argv[7]).parent==private/'run' and argv[8]==str(private/'targets'/('forbidden.dylib' if name=='outside-allowlist' else 'allowed.dylib'))
 before,after=[json.loads(v) for v in argv[9:11]];assert before['mode']==after['mode']=='0o755' and before['sha256']!=after['sha256']
 out=read(private/(name+'.stdout'),row['stdout_sha256']);err=read(private/(name+'.stderr'),row['stderr_sha256']);assert out==b''
 if expected==0:assert err==b''
 elif name=='outside-allowlist':assert b'PermissionError' in err and b'os.replace(staged, destination)' in err
 else:assert b'AssertionError' in err and b'p2996_asan_runtime.py' in err
 outcomes.append(dict(case=name,returncode=expected,elapsed_seconds=row['elapsed_seconds']))
checks['recorded_private_subprocess_outcomes']=outcomes
checks['recorded_controls']=dict(total=32,composition_stubbed=True,live_guard_executed=False)
profile=read(E/'controls/private.sb').decode()
expected_profile='(version 1)\n(deny default)\n(allow file-read*)\n(allow process*)\n(allow sysctl-read)\n(allow mach-lookup)\n(deny network*)\n(allow file-write* (subpath '+json.dumps(str(private/'run'))+') (literal '+json.dumps(str(private/'targets/allowed.dylib'))+'))\n'
assert profile==expected_profile
checks['private_write_allowlist_exact']=True
statics=data(E/'pre-review-static.json');assert len(statics['commands'])==3 and all(r['returncode']==0 for r in statics['commands'])
assert json.loads(statics['commands'][1]['stdout'])['checks']['baseline']==19
checks['recorded_static_only']=dict(commands=3,all_returncode_zero=True,original_acceptance_files=19,rerun=False)
scan=data(E/'pre-review-secret-scan.json');assert len(scan['files'])==38 and scan['raw']['returncode']==0 and scan['supplemental_complete_token_files']==[]
for rel,h in scan['files'].items():read(ROOT/rel,h)
read(scan['script'],scan['script_sha256'])
checks['recorded_scan_only']=dict(bound_text_files=38,raw_returncode=0,complete_token_files=[],rerun=False)
mode=data(D/'mode-control.json');mode_exe=data(D/'mode-execution.json');assert mode_exe['returncode']==0
assert mode['helper_sha256']==report['helper_sha256'] and len(mode['cases'])==2 and all(row['replacement_accepted']for row in mode['cases'])
assert mode['cases'][0]['destination_actual_mode']=='0o4755' and mode['cases'][0]['destination_reported_mode']=='0o755'
checks['independent_mode_finding']=mode
for p,h in watched.items():assert sha(Path(p).read_bytes())==h,('text changed during comparison',p)
result=dict(result='PASS: original candidate and receipt bindings; separate R1 mode finding confirmed',recorded_at=datetime.now(timezone.utc).isoformat(),candidate_sha256=sha(read(E/'candidate.json')),checks=checks,watched_text_sha256=watched,not_run=['Current shared protected guard','Compiler, runtime or installed promotion','Capacity, census, lease or PID probes','Scanner or baseline replay','14a1 artifact pass or old binary/source inventory rehash'])
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(result=result['result'],snapshots=6,project_input_hashes=19,exact_private_pairs=26,recorded_controls=32,private_commands=11,mode_finding_cases=2)))
