import ast, hashlib, json, shlex
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
D=Path(__file__).parent
E=R/'evidence/p2996-sanitizers'
blobs={}
def read(p):
    p=Path(p)
    if not p.is_absolute(): p=R/p
    if p not in blobs: blobs[p]=p.read_bytes()
    return blobs[p]
def sha(p): return hashlib.sha256(read(p)).hexdigest()
def obj(p): return json.loads(read(p))
def tree(p): return ast.parse(read(p).decode())
def dump(n): return ast.dump(n,include_attributes=False)
def main(t): return next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='main')
def function(t,name): return next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==name)
def exprs(ns): return [dump(n) for n in ns]
checks={}
expected={'candidate.json':'f55b7ef0bd02259d0bdb048f0b52c46cb01b0e5dbfd1f52f226af77d2a0277d6','contract.json':'29c2f25e6c245d1dfc2399093ca39b9a335286e73d2b169412d5ec0290c2c954','source-prerequisite.json':'f0a8c7c73fc0fa6991873661f9c15b4af81e539520daec374cd7be66fb1d9d32'}
assert all(sha(E/name)==value for name,value in expected.items())
candidate=obj(E/'candidate.json'); contract=obj(E/'contract.json'); prior=obj('evidence/baseline-build/contract.json')
assert candidate['head']==contract['base_head']=='ad2880bf4fedf9222cdcdff52cc4ec49d412b95e'
assert len(candidate['files'])==5
for name,value in candidate['files'].items(): assert sha(name)==value,name
snapshot=obj(E/'candidate-inputs.json')['files']
assert len(snapshot)==7 and {r['path'] for r in snapshot}=={str(R/p) for p in candidate['files']}|{str(E/'candidate.json'),str(E/'contract.json')}
for row in snapshot:
    content=row['text'].encode()
    assert content==read(row['path']) and len(content)==row['bytes'] and hashlib.sha256(content).hexdigest()==row['sha256'],row['path']
checks['frozen_snapshot_byte_pairs']=7
copy=obj(E/'source-copy-manifest.json')
assert read(copy['source'])==read(copy['destination']) and sha(copy['source'])==copy['sha256']==expected['source-prerequisite.json']
checks['source_prerequisite_copy_pair']=True
p=obj(E/'source-prerequisite.json')
assert p['status']=='COMPLETE_SOURCE_PREREQUISITE_RUNTIME_UNEXECUTED'
assert p['identity']['head']==candidate['head']
assert p['scope']['native_commands']==p['scope']['compiler_invocations']==p['scope']['test_or_runtime_invocations']==p['scope']['network_calls']==p['scope']['binary_content_reads_or_hashes']==0
assert {k:v for k,v in p['runtime_environment'].items() if k in ('ASAN_OPTIONS','UBSAN_OPTIONS')}==contract['runtime_environment']
assert p['runtime_environment']['unset']==contract['runtime_unset']
actual_matrix=[]
for mode,s in contract['sanitizers'].items():
    declared=next(row for row in p['compile_link_contract']['modes'] if row['mode']==mode)
    assert s['flags']==[declared['flag']]
    assert [str(Path(contract['prefixes']['p2996'])/name) for name in s['runtimes']]==[declared['expected_sanitizer_library']]
    actual_matrix.append({'mode':mode,'argv':'clean','expected_exit':0})
    for name,tokens in s['errors'].items():
        assert tokens==[p['witnesses'][name]['expected_error_substring']]
        actual_matrix.append({'mode':mode,'argv':name,'expected_exit':p['witnesses'][name]['expected_error_exit']})
assert actual_matrix==p['witnesses']['run_matrix']
assert len(actual_matrix)==7 and sum(row['expected_exit']==86 for row in actual_matrix)==4
checks['sanitizer_matrix']=actual_matrix
changed={k for k in set(prior)|set(contract) if prior.get(k)!=contract.get(k)}
assert changed=={'base_head','baseline_qualification','inputs','runtime_environment','runtime_unset','sanitizers','scope','source_inputs','tools'},changed
for field in ('inputs','tools','source_inputs'):
    assert all(contract[field].get(k)==v for k,v in prior[field].items()),field
    checks[field+'_retained_bindings']=len(prior[field])
    checks[field+'_added_bindings']=len(set(contract[field])-set(prior[field]))
checks['unchanged_abi_lists']=len(contract['abi_inputs'])
assert len(p['source_bindings'])==32
for row in p['source_bindings']:
    path=Path(row['path'])
    if path.is_relative_to(R): assert contract['inputs'][str(path.relative_to(R))]==row['sha256']
    else: assert contract['source_inputs'][str(path)]==row['sha256']
new_sources=set(contract['source_inputs'])-set(prior['source_inputs'])
assert new_sources=={row['path'] for row in p['source_bindings'] if not Path(row['path']).is_relative_to(R)}
new_tools=set(contract['tools'])-set(prior['tools'])
assert new_tools=={row['path'] for row in p['installed_runtime_records']}
for row in p['installed_runtime_records']:
    assert row['regular'] and not row['symlink'] and row['recordedSizeMatches']
    assert contract['tools'][row['path']]==row['recordedSha256']
checks['source_binding_table_matches']=32
checks['new_runtime_binding_table_matches']=2
oldtree=tree('dev/toolchains/baseline.py'); newtree=tree('dev/toolchains/p2996_sanitizers.py')
assert sha('dev/toolchains/baseline.py')==contract['inputs']['dev/toolchains/baseline.py']
for name in ('save','guard','interrupted'):
    assert dump(function(oldtree,name))==dump(function(newtree,name)),name
checks['identical_nested_functions']=['save','guard','interrupted']
oldmain,newmain=main(oldtree),main(newtree)
oldtry=next(n for n in oldmain.body if isinstance(n,ast.Try));newtry=next(n for n in newmain.body if isinstance(n,ast.Try))
owi=next(i for i,n in enumerate(oldtry.body) if isinstance(n,ast.With));nwi=next(i for i,n in enumerate(newtry.body) if isinstance(n,ast.With))
assert exprs(oldtry.body[:owi])==exprs(newtry.body[:nwi])
oldwith,newwith=oldtry.body[owi],newtry.body[nwi]
assert dump(oldwith.items[0]).replace('marketplace-baseline-build','marketplace-p2996-sanitizers')==dump(newwith.items[0])
def guardend(body):
    return next(i for i,n in enumerate(body) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='guard')+1
assert exprs(oldwith.body[:guardend(oldwith.body)])==exprs(newwith.body[:guardend(newwith.body)])
assert exprs(oldtry.body[owi+1:-1])==exprs(newtry.body[nwi+1:-1])
assert exprs(oldtry.handlers)==exprs(newtry.handlers)
assert len(oldtry.finalbody)==len(newtry.finalbody)==1
oldfinal,newfinal=oldtry.finalbody[0],newtry.finalbody[0]
assert isinstance(oldfinal.body[1],ast.If) and 'source_before' in dump(oldfinal.body[1])
assert exprs([oldfinal.body[0],*oldfinal.body[2:]])==exprs(newfinal.body)
assert exprs(oldfinal.handlers)==exprs(newfinal.handlers) and exprs(oldfinal.finalbody)==exprs(newfinal.finalbody)
checks['unchanged_admission_capacity_census_default_failure_finally_structure']=True
checks['finally_only_removed_retained_fmt_inventory_if']=True
baseline=obj(contract['baseline_qualification'])
assert sha(contract['baseline_qualification'])==contract['inputs'][contract['baseline_qualification']]
assert baseline['state'].startswith('PASS: 32 ARM64 baseline cells')
cache=baseline['cells']['p2996-core-static-fmt-static']['cache']
assert '-freflection' not in shlex.split(cache['CMAKE_CXX_FLAGS'])
assert cache['CMAKE_OSX_DEPLOYMENT_TARGET']=='27.0' and cache['CMAKE_OSX_SYSROOT']=='/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk'
checks['selected_baseline_flags']=shlex.split(cache['CMAKE_CXX_FLAGS'])
static=obj(E/'pre-review-static.json');post=obj(E/'baseline-postcommit.json');scan=obj(E/'pre-review-secret-scan.json')
assert len(static['commands'])==2 and all(c['returncode']==0 for c in static['commands'])
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
assert post['head']==candidate['head'] and post['clean'] and all(c['returncode']==0 for c in post['commands'])
assert post['commands'][-3]['stdout'].strip()==candidate['head'] and post['commands'][-2]['argv']==['git','status','--porcelain'] and post['commands'][-2]['stdout']==''
assert json.loads(post['commands'][-1]['stdout'])['checks']['baseline']==19
assert len(scan['files'])==12 and all(sha(name)==value for name,value in scan['files'].items())
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[]
assert len(scan['dispositions'])==3
for row in scan['dispositions']:
    assert row['rule']=='generic-api-key' and sha(row['path'])==row['sha256']
checks['parent_receipts']={'static_returncodes':[c['returncode'] for c in static['commands']],'baseline_hashes_recorded':19,'postcommit_head':post['head'],'postcommit_all_zero_and_clean':True,'scan_file_bindings':12,'scan_raw_returncode':1,'scan_transformed_returncode':0,'verified_public_digest_dispositions':3,'complete_token_findings':0}
watched={str(path):hashlib.sha256(content).hexdigest() for path,content in blobs.items()}
assert all(hashlib.sha256(Path(path).read_bytes()).hexdigest()==value for path,value in watched.items())
result={'result':'PASS: bounded source and receipt comparison','checks':checks,'read_file_hashes':watched,'candidate_code_imported_or_executed':False,'native_operations_executed':0,'installed_binary_content_reads':0,'source_inventory_reads':0,'limits':['32 prerequisite bindings and two runtime hashes compared as retained metadata; old source and binary graphs not rehashed.','Manual source reasoning remains distinct from native sanitizer execution, which has not run.']}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':result['result'],'read_files':len(watched),'snapshot_pairs':7,'sanitizer_cases':7,'native_operations_executed':0}))
