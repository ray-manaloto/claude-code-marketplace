import ast,datetime,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-asan-promotion'
OP=pathlib.Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-asan-promotion-controls-s325aqrv')
OUT=pathlib.Path(__file__).parent
watched={};cache={};checks={}
def raw(p,sha=None,size=None):
    p=pathlib.Path(p);b=p.read_bytes();actual=hashlib.sha256(b).hexdigest()
    assert len(b)<1000000,(str(p),'outside small text bound')
    b.decode('utf-8')
    if sha is not None:assert actual==sha,(str(p),actual,sha)
    if size is not None:assert len(b)==size,(str(p),len(b),size)
    watched[str(p)]=actual;cache[str(p)]=b;return b
def load(p,sha=None):return json.loads(raw(p,sha))
candidate=load(E/'candidate.json','fe997c50c0ffa8ddd254a75d9b46a00d7a8efe2e2999b8e2cc10482add40d657')
c=load(E/'contract.json','982b75c01ceb6daaf87242c54880b74da5c2a12bfc380543ce207f266f5d85d8')
assert candidate['contract_sha256']==watched[str(E/'contract.json')]
assert candidate['head']==c['base_head']=='5a4062e17089ad2fe2b160fea998dc7954aa5766'
assert len(candidate['files'])==4
snap=load(E/'candidate-inputs.json');assert len(snap['files'])==8
for row in snap['files']:
    assert raw(row['source'],row['sha256'],row['bytes'])==row['text'].encode('utf-8')
for name,sha in candidate['files'].items():assert watched[str(ROOT/name)]==sha
helper=cache[str(ROOT/'dev/toolchains/p2996_asan_promote.py')].decode();tree=ast.parse(helper)
assert watched[str(ROOT/'dev/toolchains/p2996_asan_promote.py')]=='2e8229fa0d0b39552923cd6db80a92da5be56951eac6e3fd696bad97cdf6e01d'
checks['frozen_candidate']={'snapshots':8,'maintained_files':candidate['files'],'helper_lines':len(helper.splitlines())}
old=load(ROOT/'evidence/p2996-sanitizer-repair/contract.json',c['inputs']['evidence/p2996-sanitizer-repair/contract.json'])
for key,value in old.items():
    if key not in {'base_head','scope','inputs','source_inputs'}:assert c[key]==value,key
assert len(old['inputs'])==146 and len(old['source_inputs'])==242 and len(c['tools'])==27
assert all(c['inputs'][k]==v for k,v in old['inputs'].items())
assert all(c['source_inputs'][k]==v for k,v in old['source_inputs'].items())
new_inputs={k:v for k,v in c['inputs'].items() if k not in old['inputs']}
assert len(new_inputs)==17 and len(c['inputs'])==163
for name,sha in new_inputs.items():raw(ROOT/name,sha)
checks['new_project_bindings']={'new_small_text_files':17,'unchanged_prior_project_bindings':146,'unchanged_prior_source_bindings':242,'unchanged_tool_bindings':27,'prior_large_files_rehashed':False}
runtime=load(ROOT/'evidence/p2996-asan-runtime/contract.json',c['inputs']['evidence/p2996-asan-runtime/contract.json'])
assert c['target']==runtime['target']
assert c['after']==runtime['current_asan']
assert c['before']=={k:runtime['previous_record'][k] for k in ('sha256','bytes','mode')}
assert c['replacement']==runtime['qualified_replacement']['path']
assert c['replacement_identity']=={**c['after'],'mode':'0o700'}
assert c['target'] not in c['source_inputs'] and c['tools'][c['target']]==c['before']['sha256']
previousreview=load(ROOT/'evidence/p2996-asan-runtime/preparation-review.json','c45bd56f1fd34ebfaefbb89dde2ad0e614a076581591b542b0eb421726c05d1e')
assert previousreview['result'].startswith('PASS') and previousreview['findings']==[]
assert previousreview['helper_sha256']==c['inputs']['dev/toolchains/p2996_asan_runtime.py']
install=load(ROOT/'evidence/p2996-install/operation/qualification.json',c['inputs']['evidence/p2996-install/operation/qualification.json'])
math=load(ROOT/'evidence/p2996-math-resume/operation/qualification.json',c['inputs']['evidence/p2996-math-resume/operation/qualification.json'])
source=math['proposal']['configuration'];sp=c['source_provenance']
assert sp=={'path':source['source'],'head':source['pin'],'tree':source['tree'],'diff_sha256':install['proposal']['source_diff_sha256'],'status':'evidence/p2996-install/operation/source-status.stdout'}
build=install['proposal']['workspace']+'/build/'
bindings={p:sha for p,sha in install['proposal']['bindings'].items() if p.startswith(build) or p.startswith(sp['path']+'/')}
assert len(bindings)==432
recipepath='evidence/p2996-sanitizer-repair/recipes.json'
recipes=load(ROOT/recipepath,c['inputs'][recipepath])
objects={p:row['sha256'] for p,row in recipes['objects'].items()};assert len(objects)==127
inventory=load(ROOT/'evidence/p2996-sanitizer-repair/artifact-inventory.json',c['inputs']['evidence/p2996-sanitizer-repair/artifact-inventory.json'])
artifacts={row['path']:row['sha256'] for row in inventory['artifacts']};assert len(artifacts)==12
sources=dict(old['source_inputs']);added={}
for label,values in [('installed_source_build',bindings),('asan_objects',objects),('private_artifacts',artifacts),('recorded_dependencies',{row['path']:row['sha256'] for group in inventory['source_dependencies'].values() for row in group['dependencies']})]:
    fresh=set(values)-set(sources)
    for p,sha in values.items():
        if p in sources:assert sources[p]==sha,(label,p)
        sources[p]=sha
    added[label]=len(fresh)
assert added=={'installed_source_build':432,'asan_objects':127,'private_artifacts':12,'recorded_dependencies':28}
assert sources==c['source_inputs'] and len(sources)==841
for mode,entry in c['witnesses'].items():
    rows=[x for x in inventory['artifacts'] if x['kind']==mode+'-binary'];assert len(rows)==1
    assert entry=={k:rows[0][k] for k in ('path','sha256')}
qualified=load(ROOT/'evidence/p2996-sanitizer-repair/operation/qualification.json',c['inputs']['evidence/p2996-sanitizer-repair/operation/qualification.json'])
artifactreview=load(ROOT/'evidence/p2996-sanitizer-repair/artifact-review.json',c['inputs']['evidence/p2996-sanitizer-repair/artifact-review.json'])
assert inventory['qualification_sha256']==artifactreview['qualification_sha256']==watched[str(ROOT/'evidence/p2996-sanitizer-repair/operation/qualification.json')]
assert artifactreview['artifact_inventory_sha256']==watched[str(ROOT/'evidence/p2996-sanitizer-repair/artifact-inventory.json')]
assert artifactreview['result'].startswith('PASS') and artifactreview['findings']==[]
assert qualified['repair']['patched']['path']==c['replacement'] and qualified['repair']['patched']['sha256']==c['after']['sha256']
checks['derivation_only_no_live_source_or_artifact_hashes']={'total_source_inputs':841,'retained_source_inputs':242,'added':added,'three_witnesses_from_qualified_inventory':True,'source_git_identity_from_pinned_receipts':sp}
manifest=load(E/'controls-copy-manifest.json','96ad853862d203f5ca8e8f98c6ee551bc2fbeadb19d0c7ced2a0466f395c7f27')
assert len(manifest['files'])==38
for row in manifest['files']:
    p=pathlib.Path(row['source']);q=pathlib.Path(row['destination'])
    assert p.is_relative_to(OP) and q.is_relative_to(E/'controls')
    assert raw(p,row['sha256'])==raw(q,row['sha256'])
controls=load(E/'controls/controls.json','c21657ef5e782693f5db7000aa0d8b058c3d9be8c30057056fc11c0e092d4a3b')
assert candidate['controls_sha256']==watched[str(E/'controls/controls.json')]
assert controls['helper_sha256']==candidate['files']['dev/toolchains/p2996_asan_promote.py']
assert controls['guard_sha256']==c['inputs']['dev/toolchains/p2996_asan_runtime.py']
assert controls['state']=='PASS: private transaction success, recovery, drift refusal and witness write confinement'
assert controls['shared_guard_executed'] is controls['native_runtime_executed'] is False
assert controls['installed_before_after']==c['before']
assert len(controls['controls'])==10 and len(controls['commands'])==9
bycase={x['case']:x for x in controls['controls']};assert len(bycase)==10
oldid={'sha256':hashlib.sha256(b'original private fixture\n').hexdigest(),'bytes':25,'mode':'0o755'}
newid={'sha256':hashlib.sha256(b'qualified private fixture\n').hexdigest(),'bytes':26,'mode':'0o755'}
unknownid={'sha256':hashlib.sha256(b'unknown private fixture\n').hexdigest(),'bytes':24,'mode':'0o755'}
expected_events={'success':['promote','qualify-True'],'qualification-failure':['promote','qualify-True','restore','qualify-False'],'apply-before-failure':['promote','qualify-False'],'apply-after-failure':['promote','restore','qualify-False'],'unknown-after-failure':['promote'],'backup-drift':['promote','qualify-True'],'source-mismatch':[],'destination-mismatch':[],'restore-failure':['promote','qualify-True','restore']}
for case,events in expected_events.items():
    row=bycase[case];assert row['result']=='PASS' and row['events']==events
    expected=newid if case in ('success','backup-drift','restore-failure') else unknownid if case in ('unknown-after-failure','destination-mismatch') else oldid
    assert row['target']==expected
    assert (row['error'] is None)==(case=='success')
    if case in ('unknown-after-failure','backup-drift','restore-failure'):assert 'recovery_error' in row['state']
    if case in ('qualification-failure','apply-before-failure','apply-after-failure'):assert row['state']['recovery'] in ('original restored','original already present')
    profile=OP/case/'mutation.sb'
    raw(profile,row['profile_sha256'])
    expected_profile='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(OP/case/'work'))+') (literal '+json.dumps(str(OP/case/'target.dylib'))+') (literal "/dev/null"))\n(deny network*)\n'
    assert cache[str(profile)].decode()==expected_profile
    if case not in ('source-mismatch','destination-mismatch'):
        assert load(OP/case/'state.json')==row['state']
readonly=raw(OP/'success/private.sb',bycase['witness-write-denied']['profile_sha256']).decode()
assert readonly=='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(OP/'success/work'))+') (literal "/dev/null"))\n(deny network*)\n'
applynode=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='apply')
applyscript=next(n.value.value for n in applynode.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='script' for x in n.targets))
outcomes=[]
for row in controls['commands']:
    argv=row['argv'];assert argv[:2]==['/usr/bin/sandbox-exec','-f'] and argv[4:7]==['-E','-B','-c']
    assert pathlib.Path(argv[2]).is_relative_to(OP) and 0<row['elapsed_seconds']<30
    out,err=[raw(log['path'],log['sha256']) for log in row['logs']]
    assert out==b''
    if row['case']=='witness-write-denied':
        assert row['returncode']==1 and b'PermissionError:' in err and argv[8]==str(OP/'success/target.dylib')
    else:
        assert row['returncode']==0 and err==b'' and argv[7]==applyscript and argv[8]==str(ROOT/'dev/toolchains')
        for p in argv[9:11]:assert pathlib.Path(p).is_relative_to(OP)
        assert json.loads(argv[11]) in (oldid,newid) and json.loads(argv[12]) in (oldid,newid)
    outcomes.append({'case':row['case'],'returncode':row['returncode'],'elapsed_seconds':row['elapsed_seconds']})
execution=load(E/'controls/execution.json')
assert execution['returncode']==0 and execution['stderr']=='' and execution['argv'][1:]==['-E','-B',str(OP/'controls.py')]
assert execution['script_sha256']==watched[str(OP/'controls.py')]=='479bbbc77fce11826e534b691f2d001939fd5205fce7c2167016afc7d48e7baa'
assert json.loads(execution['stdout'])=={'state':controls['state'],'controls':10,'commands':9,'receipt':str(OP/'controls.json')}
checks['recorded_private_controls']={'copy_pairs':38,'controls':10,'subprocesses':9,'outcomes':outcomes,'outer_execution':execution,'parent_injected_postwrite_and_qualification_failures':True,'reviewer_reran_controls':False}
launchers=load(E/'prepared-launchers.json',candidate['prepared_launchers_sha256'])
assert launchers['state']=='Prepared, not executed' and len(launchers['files'])==2
for row in launchers['files']:assert raw(row['path'],row['sha256'])==raw(row['copy'],row['sha256'])
assert CONTRACT_MARKER if False else True
checks['prepared_launchers']={'exact_copy_pairs':2,'state':launchers['state'],'reviewer_executed':False}
static=load(E/'pre-review-static.json')
assert len(static['commands'])==3 and all(x['returncode']==0 for x in static['commands'])
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
scan=load(E/'pre-review-secret-scan.json')
assert len(scan['files'])==52
for name,sha in scan['files'].items():raw(ROOT/name,sha)
raw(scan['script'],scan['script_sha256'])
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0
assert len(scan['dispositions'])==4 and scan['supplemental_complete_token_files']==[]
for row in scan['dispositions']:
    expected=c['source_inputs'].get(row['path'])
    if expected is None:expected=c['inputs'][str(pathlib.Path(row['path']).relative_to(ROOT))]
    assert expected==row['sha256']
checks['recorded_static_and_scan']={'static_returncodes':[0,0,0],'acceptance_baseline_files':19,'scan_current_text_bindings':52,'raw_returncode':1,'recorded_file_digest_dispositions':4,'transformed_returncode':0,'complete_token_files':[],'prior_false_positive_source_files_not_rehashed':True,'reviewer_reran_checks':False}
git=[]
for args,expected in [(['rev-parse','--show-toplevel'],str(ROOT)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],candidate['head']),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
    p=subprocess.run(['/usr/bin/git','-C',str(ROOT),*args],capture_output=True,text=True,timeout=5)
    assert p.returncode==0 and p.stdout.strip()==expected,(args,p.stdout,p.stderr)
    git.append({'argv':['/usr/bin/git','-C',str(ROOT),*args],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
checks['current_git_identity']=git
for p,sha in watched.items():assert hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()==sha,('text changed',p)
report={'result':'PASS: bounded Task 14a3 preparation text comparison','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_sha256':watched[str(E/'candidate.json')],'checks':checks,'watched_text_sha256':watched,'not_run':['New runner, capacity or dispatch','Any candidate function or private fixture replay','Live shared guard or installed runtime','841 live source/build inputs, 127 retained objects, tool or prior artifact hashes','Scanner, baseline, compiler, leases, services, containers, models or network']}
(OUT/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'result':report['result'],'snapshots':8,'control_copy_pairs':38,'launcher_copy_pairs':2,'source_derivation':added,'live_source_artifact_hashes':0,'controls_rerun':False}))
