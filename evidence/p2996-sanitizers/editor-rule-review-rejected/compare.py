import ast, copy, hashlib, json, re
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/p2996-sanitizers';O=E/'original-preparation';D=Path(__file__).parent
B={}
def read(p):
    p=Path(p)
    if not p.is_absolute():p=R/p
    if p not in B:B[p]=p.read_bytes()
    return B[p]
def sha(p):return hashlib.sha256(read(p)).hexdigest()
def obj(p):return json.loads(read(p))
def tree(p):return ast.parse(read(p).decode())
def dump(n):return ast.dump(n,include_attributes=False)
expected={'candidate.json':'024cc3a0c6106fc3e0a94e983db284c253e19aea3df231ff8292b6964dc2880b','contract.json':'4e5e3bc187c0d0f19c71be093c020deb5dd7eb02a12ac93ee198f57cebd249bb','capacity-retry.py.source':'3912859e62ef8d993782095f6faccb6a65154aaa16db2f0c27f74d0043b589a2','editor-services-stable.json':'a7f3e82d8c71fc67cb22abddf6ec0afd18e178b3aaadbba2cecf1d16e58f5948'}
assert all(sha(E/name)==v for name,v in expected.items())
c=obj(E/'candidate.json');contract=obj(E/'contract.json');old=obj(O/'contract.json')
assert c['head']==contract['base_head']=='ad2880bf4fedf9222cdcdff52cc4ec49d412b95e'
assert len(c['files'])==5 and all(sha(name)==value for name,value in c['files'].items())
assert sha('dev/toolchains/p2996_sanitizers.py')=='f9174b0625028b0fd5b5ae4809222a65a4944875878a5c9caa7241a8eebba4f9'
rows=obj(E/'candidate-inputs.json')['files']
assert len(rows)==8 and {row['source'] for row in rows}=={str(R/name) for name in c['files']}|{str(E/name) for name in ('candidate.json','contract.json','capacity-retry.py.source')}
for row in rows:
    b=row['text'].encode();assert b==read(row['source']) and len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
original_review='959a0964dd4fe7099371747994fd383735070da5c6bf72ba512712f3b9c5e1d3'
assert sha(O/'pre-run-review.json')==original_review==c['original_preparation_review_sha256']
assert sha(O/'candidate.json')==c['previous_candidate_sha256']=='d8989375c84699a3a8414acea7d97fb5e9cd5f844f464e98146672eeb29fb8a6'
prior_inputs=obj(E/'preparation-review/comparison.json')['read_file_hashes']
archived=obj(E/'original-preparation-copy-manifest.json');assert len(archived)==11
for row in archived:
    assert sha(row['copy'])==row['sha256']
    if row['source'].endswith('/pre-run-review.json'):assert row['sha256']==original_review
    else:assert prior_inputs[row['source']]==row['sha256']
previous_manifest=obj(E/'preparation-review/supporting-manifest.json')
assert sha(E/'preparation-review/supporting-manifest.json')=='8ebd033d49de2905a9519d05795e43161c78181b8ffaf8624ef636bb9a373970'
assert sha(E/'preparation-review/review.json')==original_review
for row in previous_manifest['support_files']:assert sha(E/'preparation-review'/row['name'])==row['sha256']
assert {k for k in set(old)|set(contract) if old.get(k)!=contract.get(k)}=={'editor_services','inputs','tools'}
assert all(contract['inputs'].get(k)==v for k,v in old['inputs'].items())
added_inputs=set(contract['inputs'])-set(old['inputs']);assert len(added_inputs)==5
for name in added_inputs:assert sha(name)==contract['inputs'][name]
assert all(contract['tools'].get(k)==v for k,v in old['tools'].items())
assert set(contract['tools'])-set(old['tools'])=={'/usr/bin/env','/usr/sbin/lsof'}
oldtree=tree(O/'p2996_sanitizers.py.source');newtree=tree('dev/toolchains/p2996_sanitizers.py')
old_capacity=next(n for n in ast.walk(oldtree) if isinstance(n,ast.Assert) and ast.unparse(n.test).startswith("not active and report['capacity']['free_bytes']"))
class NormalizeDelta(ast.NodeTransformer):
    def visit_FunctionDef(self,node):
        if node.name=='admit_editors':return None
        return self.generic_visit(node)
    def visit_Assign(self,node):
        if any(isinstance(t,ast.Name) and t.id=='CONTRACT_SHA' for t in node.targets):
            node.value=ast.Constant(value='344a72cb7852857b8247d03cc63ce1b8cdb54a007ca54c39e7b7b52320e5d4b4')
        if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='admit_editors':return None
        return self.generic_visit(node)
    def visit_Assert(self,node):
        if ast.unparse(node.test)=="report['capacity']['free_bytes'] >= contract['disk_reserve_bytes']":return copy.deepcopy(old_capacity)
        return self.generic_visit(node)
assert dump(NormalizeDelta().visit(copy.deepcopy(newtree)))==dump(oldtree)
retry=read(E/'capacity-retry.py.source').decode()
assert 'admit_editors = function(HELPER, "admit_editors", globals())' in retry
assert "'f9174b0625028b0fd5b5ae4809222a65a4944875878a5c9caa7241a8eebba4f9'" in retry and repr(expected['contract.json']) in retry
assert 'assert __debug__' in retry and 'admit_editors(active, run, editor_policy)' in retry
observed=obj(E/'editor-services.json');stable=obj(E/'editor-services-stable.json');policy=stable['policy']
assert stable['previous_observation_sha256']==sha(E/'editor-services.json')
assert contract['editor_services']==policy==observed['policy']
assert set(policy['processes'])=={'73356','73398'} and policy['maximum_cpu_percent_per_service']==2.0 and policy['maximum_cpu_percent_total']==4.0
assert all(row['returncode']==0 and row['stderr']=='' for row in observed['commands']+stable['commands'])
assert stable['commands'][0]['argv']==['/usr/bin/env','LC_ALL=C','TZ=America/Chicago','/bin/ps','-p','36012,73356,73372,73398','-o','pid=,ppid=,lstart=,comm=']
identities={}
for line in stable['commands'][0]['stdout'].splitlines():
    p=line.split(maxsplit=7);assert len(p)==8;identities[p[0]]={'ppid':p[1],'started_at':' '.join(p[2:7]),'executable':p[7]}
for pid,row in policy['processes'].items():
    assert identities[pid]==row['identity'] and row['cwd']==str(R)
    assert all(identities[p]==v for p,v in row['ancestors'].items())
cwd_cmd=next(row for row in observed['commands'] if row['case']=='editor-cwd')
assert cwd_cmd['argv']==['/usr/sbin/lsof','-a','-p','73356,73398,73372','-d','cwd','-Fpn']
lines=cwd_cmd['stdout'].splitlines();assert len(lines)==9
blocks=[lines[i:i+3] for i in range(0,len(lines),3)]
assert all(b[0].startswith('p') and b[1]=='fcwd' and b[2]=='n'+str(R) for b in blocks)
selected=[b for b in blocks if b[0][1:] in policy['processes']]
assert len(selected)==2 and sum(map(len,selected))==6
rule=next(n for n in newtree.body if isinstance(n,ast.FunctionDef) and n.name=='admit_editors')
assert any(isinstance(n,ast.Assert) and ast.unparse(n.test)=='len(lines) == 2 * len(entries)' for n in ast.walk(rule))
control_source=read(E/'editor-controls.py.source').decode();ctree=ast.parse(control_source)
assert "cwd = ''.join('p' + pid + '\\nn' + str(ROOT) + '\\n'" in control_source
control=obj(E/'editor-controls.json');execution=obj(E/'editor-control-execution.json')
assert control['state']=='PASS' and control['helper_sha256']==c['files']['dev/toolchains/p2996_sanitizers.py'] and control['script_sha256']==sha(E/'editor-controls.py.source')
cases=control['cases'];assert len(cases)==24 and [row['outcome'] for row in cases].count('admitted')==3
names=[n.args[0].value for n in ast.walk(ctree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='attempt']
assert names==[row['case'] for row in cases]
assert execution['returncode']==0 and execution['stderr']=='' and json.loads(execution['stdout'])=={'state':'PASS','cases':24,'admitted':3}
assert cases[0]['calls']==cases[-2]['calls'] and cases[1]['calls']==[]
assert all(call['timeout']==15 for row in cases for call in row['calls'])
copy_pairs={}
for manifest in ('editor-control-copy-manifest.json','capacity-copy-manifest.json'):
    pairs=obj(E/manifest);copy_pairs[manifest]=len(pairs)
    for row in pairs:assert read(row['source'])==read(row['copy']) and sha(row['copy'])==row['sha256']
capacity=obj(E/'capacity/capacity.json');cx=obj(E/'capacity/execution.json')
assert cx['returncode']==1 and json.loads(cx['stdout'])['state']=='FAIL' and 'assert not active and' in cx['stderr']
assert capacity['state']=='FAIL' and not capacity['held_lease'] and not capacity['native_operation_started']
assert len(capacity['commands'])==4 and all(row['returncode']==0 for row in capacity['commands'])
assert capacity['script_sha256']==sha(E/'capacity/capacity.py.source')
for cmd in capacity['commands']:
    for row in cmd['logs']:assert sha(row['path'])==row['sha256']
assert capacity['active_build_processes']==['73356   0.0 /opt/homebrew/opt/llvm/bin/clangd','73398   0.0 /Library/Developer/CommandLineTools/usr/bin/clangd']
assert capacity['free_bytes']>=8*1024**3 and capacity['load'][0]<=2*capacity['cpus'] and capacity['total_cpu_percent']<=75*capacity['cpus'] and capacity['container_cpu_percent']<=50*capacity['cpus']
static=obj(E/'pre-review-static.json');scan=obj(E/'pre-review-secret-scan.json')
assert len(static['commands'])==2 and all(row['returncode']==0 for row in static['commands'])
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
assert len(scan['files'])==50 and all(sha(name)==value for name,value in scan['files'].items())
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[] and len(scan['dispositions'])==10
for row in scan['dispositions']:assert sha(row['path'])==row['sha256'] and row['rule']=='generic-api-key'
watch={str(path):hashlib.sha256(b).hexdigest() for path,b in B.items()}
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==v for p,v in watch.items())
result={'comparison_result':'COMPLETE: frozen bindings and R1 evidence verified','findings':[{'id':'R1','path':'dev/toolchains/p2996_sanitizers.py','line':51,'observed_lsof_blocks':selected,'expected_parser_lines_for_two_pids':4,'actual_recorded_lines_for_two_pids':6,'synthetic_controls_omit_fcwd':True,'candidate_function_executed':False}],'checks':{'snapshots':8,'archived_preparation_files':11,'original_preparation_review_unchanged':True,'native_helper_only_editor_admission_delta':True,'new_contract_input_bindings':5,'new_tool_hashes_metadata_only':2,'copy_pairs':copy_pairs,'controls_recorded':24,'controls_admitted':3,'controls_rejected':21,'first_capacity_returncode':1,'first_capacity_child_returncodes':[row['returncode'] for row in capacity['commands']],'first_capacity_lease_and_native_started':False,'static_returncodes':[row['returncode'] for row in static['commands']],'baseline_hashes_recorded':19,'scan_file_bindings':50,'scan_raw_returncode':1,'scan_transformed_returncode':0,'digest_false_positive_records':10,'full_token_findings':0},'read_file_hashes':watch,'candidate_code_imported_or_executed':False,'native_probes_or_control_reruns':0,'binary_content_reads':0,'source_inventory_reads':0}
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'comparison_result':result['comparison_result'],'findings':1,'explicit_files_read':len(watch),'native_probes_or_control_reruns':0}))
