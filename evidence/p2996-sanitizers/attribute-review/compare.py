from pathlib import Path
import hashlib,json,subprocess
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=ROOT/'evidence/p2996-sanitizers';HERE=Path(__file__).parent
j=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=j(Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-sanitizer-failure-review-5lqlqejl/comparison.json'))
c=j(E/'closure-candidate.json');f=j(E/'failure-candidate.json')
assert sha(E/'closure-candidate.json')=='1815771c6d73cf7d9fafd3b9e5b606c40598f63524e769aa33a55022cd01d093'
assert c['head']=='ad2880bf4fedf9222cdcdff52cc4ec49d412b95e' and len(c['files'])==6
assert c['prior_failure_candidate_sha256']==sha(E/'failure-candidate.json')==prior['candidate_sha256']
assert c['prior_failure_review_sha256']==sha(E/'failure-review.json')=='896a6cfd378b404755b9f9e8458d6f9c3e2a5b80836a6fb5c0147a209c1590f2'
assert sha(E/'contract.json')==prior['contract_sha256']
for p,h in c['files'].items():assert sha(ROOT/p)==h
for p in ['dev/toolchains/p2996_sanitizers.py','dev/toolchains/sanitizer_witness.cpp']:assert c['files'][p]==f['files'][p]
old=j(E/'failure-inputs.json')['files']
assert sha(E/'failure-inputs.json')==prior['watched_text_sha256'][str(E/'failure-inputs.json')]
changed=[row['path'] for row in old if row['path'] in f['files'] and row['text'].encode()!=(ROOT/row['path']).read_bytes()]
assert set(changed)=={'docs/sanitizers.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md'}
argv=['/usr/bin/git','-c','core.fsmonitor=false','show','HEAD:.gitattributes']
base=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=10);assert base.returncode==0 and base.stderr==''
line='evidence/p2996-sanitizers/startup-sample.txt.source whitespace=-blank-at-eof\n'
assert (ROOT/'.gitattributes').read_text()==base.stdout+line
sample=E/'startup-sample.txt.source';assert sha(sample)==c['original_sample_sha256']=='8d9612febf700db855fce0c6456629e1f6852e7512c0611ea372c9acf1c76840' and sample.read_bytes().endswith(b'\n\n')
checks=j(E/'closure-attribute-static.json')['commands'];assert [q['returncode'] for q in checks]==[0,0]
assert checks[0]['argv']==['/usr/bin/git','diff','--cached','--check'] and checks[0]['stdout']==checks[0]['stderr']==''
baseline=json.loads(checks[1]['stdout']);assert baseline['status']=='pass' and baseline['checks']['baseline']==19
scan=j(E/'closure-attribute-secret-scan.json');oldscan=j(E/'failure-secret-scan.json')
assert len(scan['files'])==220 and scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[] and len(scan['dispositions'])==48
assert sha(Path(scan['script']))==scan['script_sha256']=='783d78da0457886523d3b4cf837e38ee1f948b9e626b63b2a59e4c1837d04252'
assert sha(Path(oldscan['script']))==oldscan['script_sha256']
a=Path(oldscan['script']).read_text();assert a.count("EV/'candidate.json'")==1
assert Path(scan['script']).read_text()==a.replace("EV/'candidate.json'","EV/'closure-candidate.json'")
for row in scan['dispositions']:
 assert row['reason']=='Verified exact file-content digest'
 assert prior['watched_text_sha256'][row['path']]==row['sha256']
paths=[*(ROOT/p for p in c['files']),E/'closure-candidate.json',E/'closure-attribute-static.json',E/'failure-review.json',E/'failure-secret-scan.json',sample]
bindings={str(p.relative_to(ROOT)):sha(p) for p in paths}
for p,h in bindings.items():assert scan['files'][p]==h
bindings['evidence/p2996-sanitizers/closure-attribute-secret-scan.json']=sha(E/'closure-attribute-secret-scan.json')
result={'result':'PASS','findings':[],'candidate_sha256':sha(E/'closure-candidate.json'),'maintained_files':6,'delta':{'attribute_added':line.rstrip(),'changed_prose_files':changed,'helper_fixture_contract_unchanged':True,'sample_sha256':sha(sample)},'parent_recorded_checks':{'returncodes':[0,0],'baseline_original_hashes':19,'scanner_files':220,'raw_returncode':1,'dispositions':48,'transformed_returncode':0,'complete_token_files':[]},'disposition_verification':'All 48 digests match the previously independently verified frozen text hashes; no historical scan graph was replayed.','current_scan_bindings':11,'git_base_attributes':{'argv':argv,'returncode':base.returncode,'stdout':base.stdout,'stderr':base.stderr},'current_text_sha256':bindings}
(HERE/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':'PASS','maintained_files':6,'current_scan_bindings':11,'sample_unchanged':True}))
