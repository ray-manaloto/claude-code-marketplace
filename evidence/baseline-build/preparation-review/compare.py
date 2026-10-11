from pathlib import Path
from hashlib import sha256
import ast, json
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
D=Path(__file__).parent
watched={}
def H(p):
    p=Path(p); b=p.read_bytes(); h=sha256(b).hexdigest(); watched[str(p)]=h; return h
def J(rel):
    p=R/rel; H(p); return json.loads(p.read_text())
candidate=J('evidence/baseline-build/candidate.json')
assert H(R/'evidence/baseline-build/candidate.json')=='9a20d04cca740f23d7611a94e5607b05f39cd1ec957aa538b60da01ab6f4dcc7'
assert candidate['head']=='1696238f7df32b75834f5738da0cdd7025c98b4d'
assert len(candidate['files'])==5
for path, digest in candidate['files'].items(): assert H(R/path)==digest, path
helper=R/'dev/toolchains/baseline.py'
assert H(helper)=='a5fa5ca1e8d7227593be55a024262d0b27e69bea8cf98c25b06127c816d535ae'
contract=J('evidence/baseline-build/contract.json')
assert H(R/'evidence/baseline-build/contract.json')==candidate['contract_sha256']=='b2e318aca3828b36d23c2496190b74764acff97789c39973cb7331f30195971b'
snapshots=J('evidence/baseline-build/candidate-inputs.json')['files']
assert len(snapshots)==7
expected={str(R/p):h for p,h in candidate['files'].items()}
expected.update({str(R/'evidence/baseline-build/contract.json'):candidate['contract_sha256'],str(R/'evidence/baseline-build/candidate.json'):watched[str(R/'evidence/baseline-build/candidate.json')]})
assert {row['source'] for row in snapshots}==set(expected)
for row in snapshots:
    encoded=row['text'].encode()
    assert len(encoded)==row['bytes'] and sha256(encoded).hexdigest()==row['sha256']==expected[row['source']]
    assert encoded==Path(row['source']).read_bytes()
old=J('evidence/vcpkg-consumers/contract.json')
assert H(R/'dev/toolchains/vcpkg_consumer.py')==contract['inputs']['dev/toolchains/vcpkg_consumer.py']=='0f1e4d90e806d72790ee5a728a5cc7bebf30dd42ef33d57636eef182bf508bca'
changed={k for k in old.keys()|contract.keys() if old.get(k)!=contract.get(k)}
assert changed=={'base_head','configurations','inputs','managed_tools','scope','tools'}
assert contract['base_head']==candidate['head']
assert contract['configurations']==['Debug','Release','RelWithDebInfo','MinSizeRel'] and contract['jobs_per_build']==1
changed_inputs={k for k in old['inputs'] if old['inputs'][k]!=contract['inputs'].get(k)}
assert changed_inputs=={'CMakeLists.txt','src/smoke.cpp'}
added_inputs=set(contract['inputs'])-set(old['inputs'])
assert added_inputs=={'CMakePresets.json','CMakePresetsVendorTemplate.json','dev/toolchains/vcpkg_consumer.py','evidence/baseline-build/presets-postcommit.json','evidence/baseline-presets/review.json','evidence/baseline-presets/generation.json','evidence/baseline-presets/closure-static.json','evidence/baseline-presets/closure-secret-scan.json','evidence/vcpkg-consumers/operation/qualification.json','evidence/vcpkg-consumers/artifact-review.json','evidence/vcpkg-consumers/native-closure.json'}
ctest=contract['managed_tools']['ctest']['path']
assert contract['managed_tools']==old['managed_tools']|{'ctest':{'path':str(Path(old['managed_tools']['cmake']['path']).with_name('ctest')),'version':'4.4.4'}}
assert contract['tools']==old['tools']|{ctest:'3c91499c53345b601504d30f84662dbaa043ecaee8915c66a769c95b7d6fcd88'}
assert contract['source_inputs']==old['source_inputs'] and contract['abi_inputs']==old['abi_inputs']
new_ast=ast.parse(helper.read_text()); old_ast=ast.parse((R/'dev/toolchains/vcpkg_consumer.py').read_text())
def node(tree,name): return next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
newmain=node(new_ast,'main'); oldmain=node(old_ast,'main')
for name in ('save','guard','run','interrupted'):
    assert ast.dump(node(newmain,name))==ast.dump(node(oldmain,name)),name
newtry=next(x for x in newmain.body if isinstance(x,ast.Try)); oldtry=next(x for x in oldmain.body if isinstance(x,ast.Try))
assert ast.dump(ast.Module(body=newtry.handlers+newtry.finalbody,type_ignores=[]))==ast.dump(ast.Module(body=oldtry.handlers+oldtry.finalbody,type_ignores=[]))
constants={n.targets[0].id:ast.literal_eval(n.value) for n in new_ast.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant)}
assert constants['CONTRACT_SHA']==candidate['contract_sha256']
root=(R/'CMakeLists.txt').read_text()
prior_root=root.replace('kind=$<TARGET_PROPERTY:research_core,TYPE>\n','').removesuffix('if(RESEARCH_CORE_WITH_FMT)\n  file(GENERATE OUTPUT "${CMAKE_BINARY_DIR}/fmt-$<CONFIG>.txt" CONTENT\n"library=$<TARGET_FILE:fmt::fmt>\nkind=$<TARGET_PROPERTY:fmt::fmt,TYPE>\n")\nendif()\n')
assert sha256(prior_root.encode()).hexdigest()=='5fbc7b9a8570991c3426c642e0b3b794ed9cf53b5c8335091dea697e932d45f0'
presets=J('CMakePresets.json'); assert watched[str(R/'CMakePresets.json')]==contract['inputs']['CMakePresets.json']=='e304882b21be2dc25a6b024dd6a6eadcb240e0b3fcd4eeb87041dfaf9ee043eb'
configure={p['name']:p for p in presets['configurePresets']}; builds={p['name']:p for p in presets['buildPresets']}; tests={p['name']:p for p in presets['testPresets']}
trees=[]; cells=[]
for lane in ('p2996','gcc16'):
    for linkage in ('static','dynamic'):
        for core in ('static','shared'):
            tail=lane+'-core-'+core+'-fmt-'+linkage; name='configure-'+tail
            assert name in configure and not configure[name].get('hidden')
            trees.append(name)
            for configuration in contract['configurations']:
                b=builds['build-'+configuration+'-'+tail]; t=tests['test-'+configuration+'-'+tail]
                assert b['configurePreset']==t['configurePreset']==name and b['configuration']==t['configuration']==configuration
                assert b['jobs']==t['execution']['jobs']==1 and t['execution']['noTestsAction']=='error'
                cells.append({'tail':tail,'configuration':configuration,'dependency_configuration':'Debug' if configuration=='Debug' else 'Release'})
assert len(set(trees))==8 and len(cells)==32
statics=J('evidence/baseline-build/pre-review-static.json'); assert [row['returncode'] for row in statics['commands']]==[0,0]
baseline=json.loads(statics['commands'][1]['stdout']); assert baseline['status']=='pass' and baseline['checks']['baseline']==19
post=J('evidence/baseline-build/presets-postcommit.json'); assert post['head']==candidate['head'] and all(row['returncode']==0 for row in post['commands'])
assert post['commands'][-2]['argv']==['git','status','--porcelain'] and post['commands'][-2]['stdout']==''
scan=J('evidence/baseline-build/pre-review-secret-scan.json'); assert len(scan['files'])==10
for path, digest in scan['files'].items(): assert H(R/path)==digest,path
assert scan['raw']['returncode']==1 and len(scan['dispositions'])==2 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[]
for row in scan['dispositions']:
    assert row['reason']=='Verified exact file-content digest' and H(row['path'])==row['sha256']
    assert row['sha256'] in contract['inputs'].values()
for path, expected_hash in watched.items(): assert sha256(Path(path).read_bytes()).hexdigest()==expected_hash,path
out={'result':'PASS','candidate_sha256':watched[str(R/'evidence/baseline-build/candidate.json')],'helper_sha256':watched[str(helper)],'contract_sha256':candidate['contract_sha256'],'head':candidate['head'],'maintained_bindings':5,'frozen_text_byte_pairs':7,'scan_bindings':10,'unchanged_nested_guard_run_save_interrupt_ast':True,'unchanged_failure_handlers_and_preservation_finally_ast':True,'prior_root_cmake_bytes_reconstructed':True,'contract_added_inputs':sorted(added_inputs),'contract_changed_prior_inputs':sorted(changed_inputs),'old_binding_tables_not_rehashed':{'inputs':len(old['inputs']),'tools':len(old['tools']),'source_inputs':len(old['source_inputs']),'abi_triplets':len(old['abi_inputs'])},'new_ctest_binary_bound_not_rehashed':ctest,'dispatch_configure_trees':trees,'dispatch_cells':32,'intended_architecture_witnesses':64,'parent_static_returncodes':[0,0],'parent_baseline_original_hashes':19,'parent_postcommit_returncodes':[row['returncode'] for row in post['commands']],'parent_scan_raw_returncode':1,'parent_scan_verified_content_digest_dispositions':2,'parent_scan_transformed_returncode':0,'native_acceptance':'UNVERIFIED; requires fresh admission','reviewer_candidate_or_native_execution':False,'watched_hashes':watched}
(D/'comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('watched_hashes','dispatch_configure_trees','contract_added_inputs')}))
