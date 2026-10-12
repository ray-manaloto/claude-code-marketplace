"""Task14a1 whitespace and current-freeze addendum; no artifact byte reads."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, time
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-sanitizer-repair'
D=Path(__file__).parent
checks={};watched={};commands=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,h=None):
 p=Path(p);b=p.read_bytes();actual=sha(b)
 if h is not None:assert actual==h,(str(p),actual,h)
 watched[str(p)]=actual;return b
def data(p,h=None):return json.loads(read(p,h))
def git(*args):
 argv=['/usr/bin/git','--no-optional-locks','-C',str(ROOT),*args];t=time.monotonic();p=subprocess.run(argv,capture_output=True,text=True,timeout=15)
 commands.append(dict(argv=argv,returncode=p.returncode,elapsed_seconds=time.monotonic()-t,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0
 return p.stdout
prior=data(D/'comparison.json');assert prior['result'].startswith('PASS')
c=data(E/'closure-candidate.json','1a63fa8681f428b84db5a8746fa4596aba2ed27772b7f71a0cc03c9bea7921c6')
o=data(E/'closure-candidate-before-whitespace.json',c['prior_closure_candidate_sha256'])
assert set(c['files'])==set(o['files'])|{'.gitattributes'}
assert [k for k,v in o['files'].items() if c['files'][k]!=v]==['.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
for k,v in o.items():
 if k not in ('files','scope'):assert c[k]==v
snap=data(E/'closure-inputs.json');old=data(E/'closure-inputs-before-whitespace.json')
assert len(snap['files'])==7
for row in snap['files']:
 b=read(row['source'],row['sha256']);assert b==row['text'].encode() and len(b)==row['bytes']
for p,h in c['files'].items():read(ROOT/p,h)
assert c['head']==git('rev-parse','HEAD').strip()=='55a37282b117fca534a86fedcdbd5c8352405e23'
assert git('symbolic-ref','--short','HEAD').strip()=='codex/marketplace-native-onboarding'
assert git('rev-parse','--show-toplevel').strip()==str(ROOT)
assert git('rev-parse','--path-format=absolute','--git-common-dir').strip()=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
attr=read(ROOT/'.gitattributes')
base=git('show','HEAD:.gitattributes').encode()
exception=b'evidence/p2996-sanitizer-repair/object-dependencies.stdout whitespace=-blank-at-eof\n'
assert attr==base+exception
checks['attribute_delta']=dict(exact_line=exception.decode().strip(),only_new_line=True,previous_attributes_preserved=True)
progress_path=str(ROOT/'.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md')
old_progress=next(r['text'] for r in old['files'] if r['source']==progress_path)
new_progress=next(r['text'] for r in snap['files'] if r['source']==progress_path)
append='- The raw Ninja dependency log retains its final blank line. Its whitespace\n  check returned 3; one exact-path attribute preserves those bytes and adds a\n  sixth maintained file containing only that exception. Native inputs are unchanged.\n'
assert new_progress==old_progress+append
checks['progress_delta']=dict(lines=3,exact_append=append)
raw=read(E/'object-dependencies.stdout','a08e058575fe154da43943d73cc9767037d24c98a76fc5fd2e65cf59d16c5dda')
assert raw.endswith(b'\n\n')
checks['raw_dependency_bytes_preserved']=True
for filename,key in [('contract.json','contract_sha256'),('operation/qualification.json','native_qualification_sha256'),('operation/closure.json','native_closure_sha256'),('artifact-inventory.json','artifact_inventory_sha256')]:read(E/filename,c[key])
checks['native_evidence_unchanged']=True
s=data(E/'whitespace-static.json','7a370fc56b4279055075301737dbe31e365b53c8bc58395eaba1f04e5c538dc2')
assert len(s['commands'])==2
assert s['commands'][0]['returncode']==1 and s['commands'][0]['stdout']==s['commands'][0]['stderr']==''
assert s['commands'][1]['returncode']==0 and json.loads(s['commands'][1]['stdout'])['checks']['baseline']==19
checks['recorded_static']=dict(no_index_diff_returncode=1,no_index_output_empty=True,acceptance_baseline_returncode=0,original_files=19,rerun=False)
scan=data(E/'whitespace-secret-scan.json')
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[] and len(scan['dispositions'])==11 and len(scan['files'])==92
old_scan=data(E/'pre-artifact-secret-scan.json')
old_source=read(old_scan['script'],old_scan['script_sha256'])
new_source=read(scan['script'],scan['script_sha256'])
assert old_source.count(b"EV/'candidate.json'")==1
assert new_source==old_source.replace(b"EV/'candidate.json'",b"EV/'closure-candidate.json'")
counts={'current_text_hashes':0,'inherited_base_comparison_hashes':0}
for rel,h in scan['files'].items():
 p=str(ROOT/rel)
 if prior['watched_text_sha256'].get(p)==h:
  counts['inherited_base_comparison_hashes']+=1
 else:
  read(p,h);counts['current_text_hashes']+=1
for row in scan['dispositions']:
 assert row['reason']=='Verified exact file-content digest'
 assert prior['watched_text_sha256'][row['path']]==row['sha256']
checks['recorded_scan']=dict(files=92,raw_returncode=1,verified_digest_dispositions=11,transformed_returncode=0,complete_token_files=[],binding_checks=counts,scanner_only_delta='candidate.json -> closure-candidate.json',rerun=False)
for p,h in watched.items():assert sha(Path(p).read_bytes())==h
result=dict(result='PASS: exact-path whitespace addendum and current six-file freeze',recorded_at=datetime.now(timezone.utc).isoformat(),candidate_sha256=watched[str(E/'closure-candidate.json')],checks=checks,commands=commands,watched_text_sha256=watched,new_artifacts_rehashed=False,native_operations_executed=False)
(D/'addendum-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(result=result['result'],candidate_sha256=result['candidate_sha256'],current_snapshots=7,scan_binding_checks=counts,new_artifacts_rehashed=False)))
