import ast,hashlib,json
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
D=Path(__file__).parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
J=lambda p:json.loads(Path(p).read_text())
E=R/'evidence/vcpkg-consumers'
expected={'helper_sha256':'54110064e07f11daa4e22a0347d95146bbfe8bfd98424d645f8f2a2c79aec4f4','contract_sha256':'508d230c9857f0620853f91eab842f0809f387d2ce3b24c7f7c8da91ca3a26a6','candidate_sha256':'7010eebffbb4caf56b25103ce5d875f2b02b3862e690a3b5b7233717c5a87784'}
assert H(R/'dev/toolchains/vcpkg_consumer.py')==expected['helper_sha256']
assert H(E/'contract.json')==expected['contract_sha256']
assert H(E/'candidate.json')==expected['candidate_sha256']
can=J(E/'candidate.json'); c=J(E/'contract.json'); old=J(R/'evidence/vcpkg-fmt-build/contract.json')
gitdir=Path((R/'.git').read_text().strip().removeprefix('gitdir: '))
common=(gitdir/(gitdir/'commondir').read_text().strip()).resolve()
ref=(gitdir/'HEAD').read_text().strip().removeprefix('ref: ')
head=(common/ref).read_text().strip()
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
assert ref=='refs/heads/codex/marketplace-native-onboarding'
assert head==can['head']==c['base_head']=='b3f1adfe6bc634e08b47f1b2912ee94c09f405ba'
assert len(can['files'])==5 and all(H(R/p)==s for p,s in can['files'].items())
assert can['contract_sha256']==expected['contract_sha256']
assert all(c['inputs'].get(p)==s for p,s in old['inputs'].items())
new={p:s for p,s in c['inputs'].items() if p not in old['inputs']}
assert len(new)==11 and all(H(R/p)==s for p,s in new.items())
assert c['tools']==old['tools'] and c['abi_inputs']==old['abi_inputs']
assert all(c['source_inputs'].get(p)==s for p,s in old['source_inputs'].items())
extra={p:s for p,s in c['source_inputs'].items() if p not in old['source_inputs']}
assert extra=={c['public_toolchain']:'f911a8769d07e10b26ce651f3cef6f52f2d5e598e3504d7f19e70bcbd3b3b25b'}
assert all(H(p)==s for p,s in extra.items())
composition=J(E/'composition-prerequisite.json')
root=(R/'CMakeLists.txt').read_text(); lines=root.splitlines(keepends=True)
pre=''.join(lines[:6]+lines[15:]).replace(' OR _research_core_vcpkg','')
pre=pre.replace('(CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/gcc16-macos-arm64.cmake"))','CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/gcc16-macos-arm64.cmake")')
pre=pre.replace('(CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/p2996-macos-arm64.cmake"))','CMAKE_TOOLCHAIN_FILE STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}/cmake/toolchains/p2996-macos-arm64.cmake")')
assert hashlib.sha256(pre.encode()).hexdigest()==composition['root_preimage_sha256']
assert composition['closing_head']==head and composition['public_toolchain_sha256']==extra[c['public_toolchain']]
node=ast.parse((R/'dev/toolchains/vcpkg_consumer.py').read_text())
const={n.targets[0].id:ast.literal_eval(n.value) for n in node.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant)}
assert const['CONTRACT_SHA']==expected['contract_sha256']
q=J(R/c['fmt_qualification']); ar=J(R/'evidence/vcpkg-fmt-build/artifact-review.json'); closure=J(R/'evidence/vcpkg-fmt-build/native-closure.json'); pc=J(E/'fmt-postcommit.json')
assert ar['result'].startswith('PASS') and not ar['findings']
assert ar['qualification_sha256']==closure['qualification_sha256']==H(R/c['fmt_qualification'])
assert ar['helper_sha256']==pc['helper_sha256']==H(R/'dev/toolchains/vcpkg_fmt.py')
assert ar['contract_sha256']==H(R/'evidence/vcpkg-fmt-build/contract.json')
assert pc['review_sha256']==H(R/'evidence/vcpkg-fmt-build/artifact-review.json')
assert pc['head']==head and pc['state']=='PASS' and pc['clean']
assert len(pc['commands'])==6 and all(r['returncode']==0 for r in pc['commands'])
assert pc['commands'][3]['stdout'].strip()==head and pc['commands'][4]['stdout']==''
assert json.loads(pc['commands'][5]['stdout'])['checks']['baseline']==19
assert q['state'].startswith('PASS') and q['lease_released'] and q['protected_state_unchanged']
assert closure['native_returncode']==0 and closure['all_recorded_outcomes_expected'] and closure['default_profiles_equal']
assert set(q['cells'])=={'arm64-osx-'+lane+'-'+link for lane in ('p2996','gcc16') for link in ('static','dynamic')}
assert all({r['configuration'] for r in x['libraries']}=={'Debug','Release'} for x in q['cells'].values())
assert all(str(Path(r['path'])).startswith(c['fmt_root']+'/'+t+'/installed/'+t+'/') for t,x in q['cells'].items() for r in x['libraries'])
static=J(E/'pre-review-static.json')
assert [r['returncode'] for r in static['commands']]==[0,0]
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline']==19
scan=J(E/'pre-review-secret-scan.json')
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0
assert not scan['supplemental_complete_token_files'] and len(scan['dispositions'])==1
assert all(H(R/r['path'])==r['sha256'] for r in scan['dispositions'])
watched={str(R/p):H(R/p) for p in set(can['files'])|set(new)}
watched.update({str(E/p):H(E/p) for p in ('candidate.json','contract.json','pre-review-static.json','pre-review-secret-scan.json')})
watched.update(extra)
report=expected|{'result':'PASS','identity':{'checkout':str(R),'branch':ref.removeprefix('refs/heads/'),'head':head,'common_git_directory':str(common)},'candidate_files_verified':5,'new_input_bindings_verified':11,'new_public_toolchain_verified':1,'prior_binding_tables_preserved':{'inputs':len(old['inputs']),'tools':len(old['tools']),'source_inputs':len(old['source_inputs']),'abi_triplets':len(old['abi_inputs'])},'root_preimage_preserved':True,'prior_fmt_gate':{'state':q['state'],'artifact_review':ar['result'],'native_rc_recorded':closure['native_returncode'],'cells':len(q['cells']),'libraries':sum(len(v['libraries']) for v in q['cells'].values()),'postcommit_rcs':[r['returncode'] for r in pc['commands']]},'parent_static_rcs':[r['returncode'] for r in static['commands']],'baseline_hashes_reported':19,'parent_scan':{'raw_rc':1,'disposition_rc':0,'verified_content_digest_findings':1},'watched_hashes':watched,'no_native_or_candidate_functions_executed':True,'maintained_writes':0,'shared_writes':0}
(D/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='watched_hashes'}))
