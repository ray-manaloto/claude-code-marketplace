import ast, difflib, hashlib, json, stat
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
D=Path(__file__).parent
E=R/'evidence/vcpkg-private-retry'
H='f61f9035f88e2d5f4b943ed386d2ed404cae6897'
HS='7e1d7cae675be05b70e96c429e38240125be8e9cd88c2ffe007664a10921b60a'
CS='1099e0df49d3a6e022f76297424b0456365333700c086d1d0d7a1905f03bfda5'
KS='75e54fc51d62c68c9147c50c21f0c9eaa33ebe6805e3a4b61eaa3c904f5ec7b1'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_bytes())
def save(name,d): (D/name).write_text(json.dumps(d,indent=2)+'\n')
def record(p):
 p=Path(p); b=p.read_bytes(); s=p.stat()
 return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'mode':stat.S_IMODE(s.st_mode)}
# Only filesystem reads below; no candidate imports or candidate functions.
helper=R/'dev/toolchains/vcpkg_private.py'; oldhelper=R/'evidence/vcpkg-private/native-hold/vcpkg_private.py.source'
old=load(R/'evidence/vcpkg-private/contract.json'); current=load(E/'contract.json'); candidate=load(E/'candidate.json')
assert sha(helper)==HS and sha(E/'contract.json')==CS and sha(E/'candidate.json')==KS
paths=set([helper,oldhelper,E/'contract.json',E/'candidate.json',R/'AGENTS.md',R/'docs/accepted-decisions.md',R/'evidence/onboarding/baseline-files.json'])
paths.update(R/p for p in current['inputs']); paths.update(R/p for p in candidate['files'])
paths.update(E/p for p in ['source-copy-manifest.json','pre-review-static.json','pre-review-scan.json'])
paths.update(R/p for p in ['evidence/mise-renovate/operation/qualification.json','evidence/mise-renovate/operation/default-profile.stdout','evidence/vcpkg-private/native-hold/qualification.json'])
watch={str(p):record(p) for p in sorted(paths)}
save('frozen-inputs.json',watch)
gitdir=Path((R/'.git').read_text().strip().removeprefix('gitdir: ')); common=(gitdir/(gitdir/'commondir').read_text().strip()).resolve()
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
ref=(gitdir/'HEAD').read_text().strip(); assert ref=='ref: refs/heads/codex/marketplace-native-onboarding'
assert (common/ref.removeprefix('ref: ')).read_text().strip()==H
assert candidate['head']==current['base_head']==H and candidate['contract_sha256']==CS and candidate['native_operations']==0
assert len(candidate['files'])==4
for p,h in candidate['files'].items(): assert sha(R/p)==h,p
assert len(old['inputs'])==33 and len(current['inputs'])==45
for p,h in old['inputs'].items(): assert current['inputs'][p]==h,p
for p,h in current['inputs'].items(): assert sha(R/p)==h,p
changed={k for k in set(old)|set(current) if old.get(k)!=current.get(k)}
assert changed=={'base_head','scope','profiles','inputs','default_profile'},changed
assert current['profiles']=={'p2996':'evidence/mise-renovate/operation/p2996-profile.stdout','gcc16':'evidence/mise-renovate/operation/gcc16-profile.stdout'}
assert current['default_profile']=='evidence/mise-renovate/operation/default-after.stdout'
assert candidate['scope']==current['scope']=='Private vcpkg copy, confinement and managed CMake/Ninja selection under reattested shared state; no dependency/compiler build'
for p in list(current['profiles'].values())+[current['default_profile']]: assert p in current['inputs']
for p,h in current['tools'].items(): assert sha(p)==h,p
assert len(current['tools'])==5
for d in current['downloads']: assert hashlib.sha512(Path(d['path']).read_bytes()).hexdigest()==d['sha512'],d['path']
assert len(current['downloads'])==2
before=oldhelper.read_text(); after=helper.read_text()
assert sha(oldhelper)=='85930dd84d8cec27a63445b3f46756214cdfb136765476d1e53248c2af53b6b5'
replacements=[('from mise_runtime import function, load, protected','from mise_runtime import function, load\nfrom mise_renovate import protected'),('EVIDENCE = ROOT / "evidence/vcpkg-private"','EVIDENCE = ROOT / "evidence/vcpkg-private-retry"'),('CONTRACT_SHA = "f0b710d15389ae7091fb2af0aa35207712989a1312510996a6f467c116c02c8d"','CONTRACT_SHA = "'+CS+'"'),('(ROOT / "evidence/mise-runtime/operation/default-after.stdout").read_text()','(ROOT / contract["default_profile"]).read_text()')]
expected=before
for a,b in replacements:
 assert expected.count(a)==1,a
 expected=expected.replace(a,b)
assert after==expected
ast.parse(after)
(D/'helper.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile=str(oldhelper),tofile=str(helper))))
save('contract-delta.json',{'changed_keys':sorted(changed),'retained_input_count':33,'new_input_count':12,'added_inputs':{p:h for p,h in current['inputs'].items() if p not in old['inputs']},'unchanged_other_fields':sorted(set(current)-changed)})
# Bind the new guard and profile files to the already reviewed actual operation.
ren=R/'evidence/mise-renovate'; closure=load(ren/'closure-review.json'); native=load(ren/'native-execution.json'); q=load(ren/'operation/qualification.json'); disposition=load(ren/'closure-disposition.json')
assert closure['result']=='PASS' and closure['findings']==[] and disposition['result']=='PASS'
assert closure['helper_sha256']==native['helper_sha256']==sha(R/'dev/toolchains/mise_renovate.py')
assert closure['contract_sha256']==native['contract_sha256']==sha(ren/'contract.json')
assert closure['qualification_sha256']==native['qualification_sha256']==sha(ren/'operation/qualification.json')
assert closure['native_execution_sha256']==disposition['native_execution_sha256']==sha(ren/'native-execution.json')
assert disposition['review_sha256']==sha(ren/'closure-review.json') and disposition['reviewed_candidate_sha256']==closure['candidate_sha256']
priorreview=Path('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-mise-renovate-closure-review-wx03jdsn/review.json')
assert priorreview.read_bytes()==(ren/'closure-review.json').read_bytes()
assert native['returncode']==0 and native['commands']==15 and native['command_returncodes']==[0]*15
assert q['state'].startswith('PASS') and q['protected_state_unchanged'] is True and len(q['commands'])==15
assert all(c['returncode']==0 for c in q['commands'])
op=Path(native['argv'][-1]); assert (op/'qualification.json').read_bytes()==(ren/'operation/qualification.json').read_bytes()
profile_records=[]
for label,p in [('default-after',current['default_profile']),*[(lane+'-profile',p) for lane,p in current['profiles'].items()]]:
 commands=[c for c in q['commands'] if c['case']==label]; assert len(commands)==1
 c=commands[0]; assert c['returncode']==0 and '--fresh-env' in c['argv'] and '--no-hooks' in c['argv'] and '--no-deps' in c['argv']
 for log in c['logs']:
  source=Path(log['path']); copied=ren/'operation'/source.name
  assert sha(source)==log['sha256'] and source.read_bytes()==copied.read_bytes()
  if source.suffix=='.stderr': assert source.read_bytes()==b''
 stdout=[log for log in c['logs'] if log['path'].endswith('.stdout')][0]
 assert sha(R/p)==stdout['sha256']==current['inputs'][p]
 profile_records.append({'case':label,'profile':p,'sha256':stdout['sha256'],'source':stdout['path'],'native_returncode':0})
assert (R/current['default_profile']).read_bytes()==(ren/'operation/default-profile.stdout').read_bytes()
# Preserve actual failed 12c1 receipt; the retry namespace does not overwrite it.
oldnative=load(R/'evidence/vcpkg-private/native-execution.json'); oldq=load(R/'evidence/vcpkg-private/native-hold/qualification.json'); oldreview=load(R/'evidence/vcpkg-private/closure-review.json')
assert oldnative['returncode']==1 and oldnative['commands_started']==0 and oldnative['copies_started'] is False and oldnative['lease_acquired'] is False
assert oldnative['qualification_sha256']==sha(R/'evidence/vcpkg-private/native-hold/qualification.json')
assert oldnative['helper_sha256']==oldreview['helper_sha256']==sha(oldhelper)
assert oldnative['contract_sha256']==oldreview['contract_sha256']==sha(R/'evidence/vcpkg-private/contract.json')
assert oldq['state']=='FAIL' and oldq['commands']==[] and oldq['error']==oldq['preservation_error']=="AssertionError(PosixPath('/Users/rmanaloto/.config/mise/config.toml'))"
assert (Path(oldnative['argv'][-1])/'qualification.json').read_bytes()==(R/'evidence/vcpkg-private/native-hold/qualification.json').read_bytes()
# Current postcommit and parent static evidence, inspected rather than rerun.
copyrows=load(E/'source-copy-manifest.json')['files']; assert len(copyrows)==1
for row in copyrows:
 source=Path(row['source']); copied=R/row['copy']; assert sha(source)==row['sha256'] and source.read_bytes()==copied.read_bytes()
post=load(E/'reattestation-postcommit.json'); assert post['head']==H and post['exit_code']==0 and post['git_status']==''
assert json.loads(post['stdout'])['checks']['baseline']==19
checks=load(E/'pre-review-static.json'); assert len(checks)==2 and all(c['exit_code']==0 for c in checks)
assert json.loads(checks[1]['stdout'])['checks']['baseline']==19
scan=load(E/'pre-review-scan.json'); assert scan['exit_code']==0 and len(scan['files'])==9
for p,h in scan['files'].items(): assert sha(R/p)==h,p
baseline=load(R/'evidence/onboarding/baseline-files.json')['files']; assert len(baseline)==19
for row in baseline:
 p=R/row['path']; assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],str(p)
for p,rec in watch.items(): assert record(p)==rec,p
result={'result':'PASS','kind':'Filesystem-only audit; no candidate execution','head':H,'contract_input_hashes':45,'retained_old_inputs':33,'new_inputs':12,'tool_file_hashes_only_no_execution':5,'download_sha512_values':2,'candidate_files':4,'exact_helper_replacements':4,'other_helper_text_unchanged':True,'prior_guard_operation_wrapper_rc':0,'prior_guard_operation_child_rcs':[0]*15,'new_profile_provenance':profile_records,'profile_source_copy_log_pairs':6,'prior_guard_qualification_source_copy_pair':True,'default_after_equals_qualified_default_before':True,'retained_native_failure_wrapper_rc':1,'retained_native_failure_child_commands':0,'retained_native_failure_source_copy_pair':True,'new_postcommit_source_copy_pairs':1,'parent_static_exit_codes':[c['exit_code'] for c in checks],'parent_secret_scan_exit_code':0,'scan_file_hashes':9,'original_Claude_file_hashes_and_sizes':19,'frozen_file_count':len(watch),'all_frozen_files_stable':True,'native_replay':False,'shared_writes':0,'candidate_imports':0}
save('audit.json',result)
print(json.dumps(result))
