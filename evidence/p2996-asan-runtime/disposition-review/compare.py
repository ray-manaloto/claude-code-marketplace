import ast,datetime,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-asan-runtime'
OLD=pathlib.Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-asan-runtime-review-8lwi3r5h')
OP=pathlib.Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-asan-runtime-mode-repair-_t7l4kfc')
OUT=pathlib.Path(__file__).parent
watched={};cache={};checks={}
def raw(path,sha=None,size=None):
    path=pathlib.Path(path)
    data=path.read_bytes()
    actual=hashlib.sha256(data).hexdigest()
    if sha is not None: assert actual==sha,(str(path),actual,sha)
    if size is not None: assert len(data)==size,(str(path),len(data),size)
    assert len(data)<500000,(str(path),'outside bounded text size')
    data.decode('utf-8')
    watched[str(path)]=actual;cache[str(path)]=data
    return data
def load(path,sha=None): return json.loads(raw(path,sha))
def h(data):return hashlib.sha256(data).hexdigest()
oldreview=load(OLD/'review.json','0f493371a0831d4fa739f18c4a07bbca3d3ee3da7f2708901d8f90aab3a2f933')
oldcmp=load(OLD/'comparison.json','2bfc3a6de67b78dd1016dcc585fd7dc8248f78d55625f557d220bd0783a0f382')
oldwatch=oldcmp['watched_text_sha256']
candidate=load(E/'candidate.json','b4bb62d891a3fefbfa5b4f4cd5a9a1b6341177f95a382eda5f6fa33349482805')
contract=load(E/'contract.json','af5c4bab941b296e953b8b9d3a9018efbc3560957de5667c2c4a7f4559ee771d')
assert candidate['head']=='b452c6d64a125b8c4f3766dcb3093220bf70b7ed'
assert candidate['contract_sha256']==watched[str(E/'contract.json')]
assert candidate['rejected_review_sha256']==watched[str(OLD/'review.json')]
assert candidate['previous_candidate_sha256']==oldreview['candidate_sha256']
assert len(candidate['files'])==4
snap=load(E/'candidate-inputs.json')
assert len(snap['files'])==6
for row in snap['files']:
    actual=raw(row['source'],row['sha256'],row['bytes'])
    assert actual==row['text'].encode('utf-8'),row['source']
for name,sha in candidate['files'].items():assert watched[str(ROOT/name)]==sha
checks['current_six_snapshots_and_four_maintained_files']={'candidate_sha256':watched[str(E/'candidate.json')],'files':candidate['files'],'snapshots':6}
oldsnaps=load(E/'rejected-preparation/candidate-inputs.json','dd3bd08ce58807a398719e6070d4c927fc79ecb46c9bce6ab5fd1ce29fc2b6c5')
oldcode=next(x['text'] for x in oldsnaps['files'] if x['source']==str(ROOT/'dev/toolchains/p2996_asan_runtime.py'))
newcode=cache[str(ROOT/'dev/toolchains/p2996_asan_runtime.py')].decode()
expected=oldcode.replace('    data = contract()\n','    data = contract()\n    assert identity(Path(data["target"])) == data["current_asan"]\n',1).replace('oct(info.st_mode & 0o777)','oct(stat.S_IMODE(info.st_mode))')
assert expected==newcode
ast.parse(newcode)
checks['exact_two_line_correction']={'identity_full_mode_line':87,'target_identity_guard_line':75,'candidate_code_executed':False}
archive=load(E/'rejected-preparation-copy-manifest.json','e10b2e5489767862a1bb1bd80720d1cbed1d645732493215ceb365b228345c84')
assert len(archive['files'])==39
for row in archive['files']:
    assert row['destination'].startswith('evidence/p2996-asan-runtime/rejected-preparation/')
    assert oldwatch[row['source']]==row['sha256'],row['source']
    raw(ROOT/row['destination'],row['sha256'],row['bytes'])
checks['preserved_rejected_preparation']={'files':39,'all_source_digests_bound_to_completed_original_review':True,'changed_live_sources_not_replayed':True}
reviewcopies=load(E/'rejected-review-copy-manifest.json','5a45260d5deaf6367fdfca4dc03490352286c8d72768ad19b790a64c039774b2')
assert len(reviewcopies['files'])==14
allowed={str(OLD/x) for x in ['review.json','supporting-manifest.json']+oldreview['supporting_files']}
assert {x['source'] for x in reviewcopies['files']}==allowed
for row in reviewcopies['files']:
    assert row['destination'].startswith('evidence/p2996-asan-runtime/rejected-review/')
    assert raw(row['source'],row['sha256'],row['bytes'])==raw(ROOT/row['destination'],row['sha256'],row['bytes'])
checks['preserved_rejected_review']={'private_copy_pairs':14,'review_sha256':candidate['rejected_review_sha256'],'original_finding_immutable':True}
copies=load(E/'repaired-controls-copy-manifest.json','ddea6b0be427133a2dd8ccc8b20729d0f15cd51a078b114d699749a47dd79980')
assert len(copies['files'])==39
for row in copies['files']:
    assert pathlib.Path(row['source']).parent==OP
    assert row['destination'].startswith('evidence/p2996-asan-runtime/repaired-controls/')
    assert raw(row['source'],row['sha256'],row['bytes'])==raw(ROOT/row['destination'],row['sha256'],row['bytes'])
checks['repaired_controls_private_copy_pairs']=39
controls=load(E/'repaired-controls/controls.json','0a7e459141c708a1ab09e92eb033d2db6091d8a1d92d19040da34b50d1b18364')
assert candidate['controls_path']=='evidence/p2996-asan-runtime/repaired-controls/controls.json'
assert candidate['controls_sha256']==watched[str(E/'repaired-controls/controls.json')]
assert controls['helper_sha256']==candidate['files']['dev/toolchains/p2996_asan_runtime.py']
assert controls['contract_sha256']==candidate['contract_sha256']
assert controls['script_sha256']==watched[str(OP/'controls.py')]
assert controls['state']=='PASS: pure guard composition and private confined replacement/restore controls'
assert controls['original_installed_runtime_unchanged'] and controls['historical_inputs_unchanged']
assert controls['qualified_replacement_executed'] is False
assert len(controls['controls'])==40 and len(controls['commands'])==17
rows={x['case']:x for x in controls['controls']}
assert len(rows)==40
composition=rows['real-wrapper-composition']
assert composition['events']==['target-identity-checked','renovate-semantic-check-called','reflection-guard-reached-with-all-three-overlays']
assert composition['mocked_digest_calls']==63 and composition['live_shared_guard_executed'] is False and composition['target_identity_stubbed'] is True
for case in ['guard-special-mode','guard-wrong-hash']:assert rows[case]['result']=='REJECTED as required'
scripttext=cache[str(OP/'controls.py')].decode()
for exact in ['assert not calls','assert stat.S_IMODE(staged.stat().st_mode) == (0o755 | bits)','assert stat.S_IMODE(destination.stat().st_mode) == (0o755 | bits)','assert target.read_bytes() == snapshot and os.path.lexists(staged)']:
    assert exact in scripttext,exact
outcomes=[]
commands={x['case']:x for x in controls['commands']}
assert len(commands)==17
for case,row in commands.items():
    argv=row['argv']
    assert argv[:3]==['/usr/bin/sandbox-exec','-f',str(OP/'private.sb')]
    assert argv[4:7]==['-E','-B',str(OP/'replace.py')]
    assert len(argv)==11 and pathlib.Path(argv[7]).parent==OP/'run'
    expected_destination=OP/'targets'/('forbidden.dylib' if case=='outside-allowlist' else 'allowed.dylib')
    assert argv[8]==str(expected_destination)
    assert json.loads(argv[9])['mode']==json.loads(argv[10])['mode']=='0o755'
    assert 0<=row['elapsed_seconds']<15
    stdout=raw(OP/(case+'.stdout'),row['stdout_sha256'])
    stderr=raw(OP/(case+'.stderr'),row['stderr_sha256'])
    assert stdout==b''
    if case.startswith('positive-'):
        assert row['returncode']==0 and stderr==b''
    else:
        assert row['returncode']==1 and rows[case]['result']=='REJECTED; target bytes and staged source preserved'
        expected_error=b'PermissionError:' if case=='outside-allowlist' else b'AssertionError\n'
        assert expected_error in stderr
    outcomes.append({'case':case,'returncode':row['returncode'],'preimages':row['preimages'],'stderr_sha256':row['stderr_sha256']})
for kind,mode in [('setuid','0o4755'),('setgid','0o2755'),('sticky','0o1755')]:
    for side,key in [('source','staged'),('destination','destination')]:
        row=commands[side+'-'+kind]
        assert row['preimages'][key]=={'mode':mode,'nlink':1,'is_symlink':False}
        other='destination' if key=='staged' else 'staged'
        assert row['preimages'][other]=={'mode':'0o755','nlink':1,'is_symlink':False}
        assert b'line 95, in replace_exact' in cache[str(OP/(side+'-'+kind+'.stderr'))]
checks['recorded_controls']={'controls':40,'sandbox_subprocesses':17,'positive_rc0':2,'rejection_rc1':15,'special_mode_rejections':6,'guard_entry_rejections':2,'composition':composition,'outcomes':outcomes,'reviewer_reran_controls':False}
execution=load(E/'repaired-controls/execution.json')
assert execution['argv'][1:]==['-E','-B',str(OP/'controls.py')]
assert execution['returncode']==0 and execution['stderr']=='' and 0<execution['elapsed_seconds']<30
assert execution['script_sha256']==controls['script_sha256']
reported=json.loads(execution['stdout'])
assert reported=={'state':controls['state'],'controls':40,'commands':17,'receipt':str(OP/'controls.json')}
checks['recorded_parent_control_execution']=execution
static=load(E/'repair-static.json','cea82fe9a67ed03a92e46ec173a6570ef42c03e04de4ef33951bffcad46363d6')
assert len(static['commands'])==3 and all(x['returncode']==0 for x in static['commands'])
baseline=json.loads(static['commands'][1]['stdout'])
assert baseline['checks']['baseline']==19 and baseline['status']=='pass'
checks['recorded_static']={'returncodes':[0,0,0],'acceptance_baseline_files':19,'reviewer_reran':False}
scan=load(E/'repair-secret-scan.json','d62c8ba50671156e0c441e2b43a95a6790e3689230ff8e52d0b7b535c5a18fa4')
assert len(scan['files'])==135
scan_new=[];scan_reused=[]
for name,sha in scan['files'].items():
    path=str(ROOT/name)
    if path in watched:
        assert watched[path]==sha,name
        scan_new.append(name)
    elif oldwatch.get(path)==sha:
        scan_reused.append(name)
    else:
        raw(path,sha);scan_new.append(name)
assert scan['script_sha256']=='d2324c41ce89159d4ea8992572206c5f890588cc663538d6d9e51fd5576dfa43'
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[]
assert len(scan['dispositions'])==2
for row in scan['dispositions']:
    assert row['path']==str(E/'rejected-review/original-pre-review-secret-scan.json')
    assert row['sha256']==watched[row['path']]=='b2eeb8cc1a9b1322be473c559d214acce958ada9531dcd5a2daa0935f5a3afda'
checks['recorded_secret_scan']={'total_text_bindings':135,'verified_current_text':len(scan_new),'reused_prior_verified_text':len(scan_reused),'reused_paths':scan_reused,'digest_false_positive_dispositions':2,'raw_returncode':1,'transformed_returncode':0,'complete_token_files':[],'reviewer_reran_scanner':False}
git=[]
for args,expected in [(['rev-parse','--show-toplevel'],str(ROOT)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],candidate['head']),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
    result=subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,text=True,timeout=5)
    assert result.returncode==0 and result.stdout.strip()==expected,(args,result.stdout,result.stderr)
    git.append({'argv':['git','-C',str(ROOT),*args],'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
checks['current_git_identity']=git
for path,sha in watched.items():assert h(pathlib.Path(path).read_bytes())==sha,('changed during comparison',path)
result={'result':'PASS: bounded R1 correction and preserved receipt comparisons','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_sha256':watched[str(E/'candidate.json')],'checks':checks,'watched_text_sha256':watched,'not_run':['Candidate module import or helper functions','Current installed runtime, complete shared guard, or original 19 input rehash','Previous 14a1 binaries or artifact checks','Parent controls, scanner, baseline, runtime or compiler replay','Capacity, leases, service or container operations, model sessions, or network']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':result['result'],'snapshots':6,'new_control_copy_pairs':39,'rejected_review_copy_pairs':14,'rejected_preparation_copies':39,'commands':17,'scan_new':len(scan_new),'scan_reused':len(scan_reused),'candidate_code_executed':False}))
