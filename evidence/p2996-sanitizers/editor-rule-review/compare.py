import ast,hashlib,json
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/p2996-sanitizers';A=E/'editor-preparation-attempt-1';D=Path(__file__).parent
B={}
def read(p):
    p=Path(p)
    if not p.is_absolute():p=R/p
    if p not in B:B[p]=p.read_bytes()
    return B[p]
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def obj(p):return json.loads(read(p))
helper='15800f647fa9fd39d553a5bc505da63ed41cef55fa53dcfa6569fa1e8f1117e6';prior_helper='f9174b0625028b0fd5b5ae4809222a65a4944875878a5c9caa7241a8eebba4f9'
assert sha(E/'candidate.json')=='31175bc34f25e5dcd4e84a5f9d6cb4fe4dbd58e4347b97b56243b25b6af6722d'
assert sha('dev/toolchains/p2996_sanitizers.py')==helper
assert sha(E/'contract.json')=='4e5e3bc187c0d0f19c71be093c020deb5dd7eb02a12ac93ee198f57cebd249bb'
assert sha(E/'capacity-retry.py.source')=='bd0119ad9741bd7d4d3f75c72839bba70e75edf61aecb0355bedd3e6f8645060'
c=obj(E/'candidate.json');assert c['head']=='ad2880bf4fedf9222cdcdff52cc4ec49d412b95e'
assert len(c['files'])==5 and all(sha(name)==value for name,value in c['files'].items())
snap=obj(E/'candidate-inputs.json')['files'];assert len(snap)==8
assert {row['source'] for row in snap}=={str(R/name) for name in c['files']}|{str(E/name) for name in ('candidate.json','contract.json','capacity-retry.py.source')}
for row in snap:
    b=row['text'].encode();assert b==read(row['source']) and len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
rejected=obj(E/'editor-rule-rejected.json');assert sha(E/'editor-rule-rejected.json')==c['rejected_review_sha256']=='7f8d7619499e3d375da4efbfa9c2249f5ae9309c59c04f934eb5078cea4428da'
assert [r['id'] for r in rejected['findings']]==['R1']
previous_hashes=obj(E/'editor-rule-review-rejected/comparison.json')['read_file_hashes']
archive=obj(E/'editor-preparation-attempt-1-copy-manifest.json');assert len(archive)==15
for row in archive:assert sha(row['copy'])==row['sha256']==previous_hashes[row['source']]
for row in obj(E/'editor-rule-rejected-copy-manifest.json'):assert read(row['source'])==read(row['copy']) and sha(row['copy'])==row['sha256']
assert sha(A/'candidate.json')==c['previous_candidate_sha256']=='024cc3a0c6106fc3e0a94e983db284c253e19aea3df231ff8292b6964dc2880b'
assert read(E/'contract.json')==read(A/'contract.json')
old=read(A/'p2996_sanitizers.py.source').decode();new=read('dev/toolchains/p2996_sanitizers.py').decode()
bad='    assert len(lines) == 2 * len(entries)\n    for process, path in zip(lines[::2], lines[1::2]):\n        assert process.startswith("p") and path.startswith("n") and process[1:] not in working_directories\n'
good='    assert len(lines) == 3 * len(entries)\n    for process, descriptor, path in zip(lines[::3], lines[1::3], lines[2::3]):\n        assert process.startswith("p") and descriptor == "fcwd" and path.startswith("n") and process[1:] not in working_directories\n'
assert old.count(bad)==1 and new==old.replace(bad,good)
assert read(E/'capacity-retry.py.source').decode()==read(A/'capacity-retry.py.source').decode().replace(prior_helper,helper)
for current,oldname in [('dev/toolchains/sanitizer_witness.cpp','sanitizer_witness.cpp.source'),('docs/sanitizers.md','sanitizers.md.source'),('.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','task_plan.md.source')]:assert read(current)==read(A/oldname)
progress=read('.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md').decode();prior_progress=read(A/'progress.md.source').decode()
assert progress.startswith(prior_progress) and len(progress[len(prior_progress):].splitlines())==6
controls=obj(E/'editor-controls.json');cx=obj(E/'editor-control-execution.json');control_source=read(E/'editor-controls.py.source').decode();source_ast=ast.parse(control_source)
assert controls['helper_sha256']==helper and controls['script_sha256']==sha(E/'editor-controls.py.source')
assert controls['observed_cwd_source_sha256']==sha(E/'editor-services.json')=='47c13afba4e76e58b84291bfdaa45cedd21e04f4393ee812d2ebf4ef81913b0e'
assert controls['state']=='PASS' and cx['returncode']==0 and cx['stderr']=='' and json.loads(cx['stdout'])=={'state':'PASS','cases':26,'admitted':3}
cases=controls['cases'];assert len(cases)==26 and [r['outcome'] for r in cases].count('admitted')==3
assert cases[:24]==obj(A/'editor-controls.json')['cases']
assert [r['case'] for r in cases[-2:]]==['wrong descriptor','extra cwd field'] and all(r['outcome']=='rejected' and r['error_type']=='AssertionError' for r in cases[-2:])
assert all([c['case'] for c in r['calls']]==['editor-identities','editor-cwd'] for r in cases[-2:])
names=[n.args[0].value for n in ast.walk(source_ast) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='attempt'];assert names==[r['case'] for r in cases]
for snippet in ["cwd_observation = json.loads((E / 'editor-services.json').read_text())", "cwd = ''.join(cwd_blocks[pid] for pid in sorted(observed['policy']['processes']))", "d['editor-cwd'] = cwd_blocks['73356']", "cwd.replace('fcwd', 'fother')", "cwd + 'n/extra\\n'"]:
    assert snippet in control_source,snippet
observed=obj(E/'editor-services.json');captured=next(row['stdout'] for row in observed['commands'] if row['case']=='editor-cwd').splitlines(keepends=True)
assert len(captured)==9
blocks={captured[i][1:].strip():''.join(captured[i:i+3]) for i in range(0,len(captured),3)}
policy=obj(E/'contract.json')['editor_services']['processes'];selected={pid:blocks[pid] for pid in sorted(policy)}
assert set(selected)=={'73356','73398'}
assert all(block.splitlines()==['p'+pid,'fcwd','n'+str(R)] for pid,block in selected.items())
assert len(''.join(selected.values()).splitlines())==3*len(selected)
for row in obj(E/'editor-control-copy-manifest.json'):assert read(row['source'])==read(row['copy']) and sha(row['copy'])==row['sha256']
static=obj(E/'pre-review-static.json');scan=obj(E/'pre-review-secret-scan.json')
assert len(static['commands'])==2 and all(row['returncode']==0 for row in static['commands']) and json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
assert len(scan['files'])==73 and all(sha(name)==value for name,value in scan['files'].items())
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[] and len(scan['dispositions'])==19
for row in scan['dispositions']:assert sha(row['path'])==row['sha256'] and row['rule']=='generic-api-key'
watch={str(p):hashlib.sha256(b).hexdigest() for p,b in B.items()};assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==value for p,value in watch.items())
result={'result':'PASS: exact R1 repair and receipt disposition comparison','findings':[],'checks':{'snapshot_byte_pairs':8,'retained_attempt_files':15,'rejected_review_copy_pairs':6,'new_control_copy_pairs':3,'helper_delta':'Exactly the three repaired cwd parser lines; remaining bytes identical','contract_bytes_unchanged':True,'retry_source_delta':'Only the helper SHA binding','fixture_docs_task_plan_unchanged':True,'progress_append_lines':6,'captured_cwd_blocks':selected,'recorded_control_returncode':0,'recorded_control_cases':26,'recorded_control_admitted':3,'recorded_control_rejected':23,'prior_24_case_receipts_unchanged':True,'new_descriptor_and_extra_field_rejections':True,'static_returncodes':[0,0],'baseline_hashes_recorded':19,'scan_bindings_checked':73,'scan_raw_returncode':1,'scan_transformed_returncode':0,'verified_public_digest_dispositions':19,'full_token_findings':0},'read_file_hashes':watch,'candidate_code_imported_or_executed':False,'control_reruns':0,'native_probes':0,'binary_hashes':0,'source_inventory_reads':0}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':result['result'],'findings':0,'files_read':len(watch),'snapshot_pairs':8,'control_reruns':0,'native_probes':0}))
