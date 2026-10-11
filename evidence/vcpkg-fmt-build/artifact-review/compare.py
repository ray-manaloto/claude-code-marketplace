from pathlib import Path
import hashlib, json
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace'); E=R/'evidence/vcpkg-fmt-build'; O=E/'operation'; D=Path(__file__).parent
data={}
def read(p):
 p=Path(p)
 if str(p) not in data: data[str(p)]=p.read_bytes()
 return data[str(p)]
def sha(p): return hashlib.sha256(read(p)).hexdigest()
def load(p): return json.loads(read(p))
a=load(E/'artifact-candidate.json'); c=load(E/'contract.json'); q=load(O/'qualification.json'); n=load(E/'native-execution.json'); admission=load(E/'admission.json'); closure=load(E/'native-closure.json')
assert sha(E/'artifact-candidate.json')=='a7f9ff9beda3406e4c79a7b235b01f1e14aa57fb92b101d977d6bbf3c1d5b96a'
assert a['head']=='de913727bd6d41c1d7d2c11b52a384902dbd6eec'
for p,h in a['files'].items(): assert sha(R/p)==h
assert a['helper_sha256']==sha(R/'dev/toolchains/vcpkg_fmt.py')=='153d6a12eb9158d5b0a61edbeae2c5c3ead411e3815aedbca53181b7fbc109bc'
assert a['contract_sha256']==sha(E/'contract.json')=='6cafe5a5574f49b67289c06c01b98f4e0f8ec71cb9425d4fe79eec9cddef5b2b'
assert a['qualification_sha256']==sha(O/'qualification.json')=='6440588108ee6dd74295290f8b6e2d23fc8f5d8118a883e74cbd6b516441b869'
assert a['native_execution_sha256']==sha(E/'native-execution.json') and a['copy_manifest_sha256']==sha(E/'operation-copy-manifest.json')
copies=load(E/'operation-copy-manifest.json')['copies']; assert len(copies)==len({r['destination'] for r in copies})==162
mapped={r['source']:R/r['destination'] for r in copies}
for r in copies: assert read(r['source'])==read(R/r['destination']) and sha(R/r['destination'])==r['sha256'] and len(read(R/r['destination']))==r['bytes']
snapshots=load(O/'reviewed-candidate/copy-manifest.json')['copies']; assert len(snapshots)==8
for r in snapshots: assert sha(R/r['destination'])==r['sha256']
prior=load(O/'reviewed-candidate/candidate.json'); names={'dev/toolchains/vcpkg_fmt.py':'vcpkg_fmt.py.source','docs/vcpkg-toolchains.md':'vcpkg-toolchains.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md':'task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md':'progress.md'}
for p,name in names.items(): assert sha(O/'reviewed-candidate'/name)==prior['files'][p]
assert admission['candidate_sha256']==sha(O/'reviewed-candidate/candidate.json') and admission['review_sha256']==sha(E/'pre-run-review.json')=='06a75026a0bfafe6d8b1c841c7b71e1567f7018cba78e73ed62a8898566c8500'
for name in ['contract.json','admission.json','pre-run-review.json']: assert read(E/name)==read(O/'reviewed-candidate'/name)
assert admission['helper_sha256']==q['helper_sha256']==n['helper_sha256']==a['helper_sha256'] and admission['contract_sha256']==a['contract_sha256']
assert q['admission_sha256']==n['admission_sha256']==sha(E/'admission.json') and n['returncode']==0
assert all(n[k]==v for k,v in load(E/'native-launch.json').items())
assert read(E/'native-execution.json')==read(O/'launch/execution.json') and read(E/'native-launch.json')==read(O/'launch/launch.json')
assert sha(O/'launch/vcpkg_fmt.py.source')==a['helper_sha256']
for suffix in ['stdout','stderr']: assert sha(O/'launch'/suffix)==n[suffix+'_sha256']
assert q['state'].startswith('PASS: four private fmt installs') and q['protected_state_unchanged'] and q['lease_released'] and 'preservation_error' not in q
assert len(q['commands'])==len({r['case'] for r in q['commands']})==29
for row in q['commands']:
 assert row['returncode']==row['expected_returncode']==(73 if row['case'] in ['outside-write','symlink-write','network-denied'] else 0)
 for log in row['logs']: assert sha(mapped[log['path']])==log['sha256']
assert closure['processes']==[dict(case=r['case'],pid=r['pid'],absent=True) for r in q['commands']]
assert closure['native_execution_sha256']==sha(E/'native-execution.json') and closure['qualification_sha256']==a['qualification_sha256'] and closure['lease_probe']==dict(free=True,contents_unchanged=True)
assert read(O/'default-before.stdout')==read(O/'default-after.stdout') and sha(O/'default-after.stdout')==c['inputs'][c['default_profile']]
triplets=['arm64-osx-'+lane+'-'+linkage for lane in ['p2996','gcc16'] for linkage in ['static','dynamic']]; assert set(q['cells'])==set(triplets)
libraries=[]; metadata=[]
for t in triplets:
 cell=q['cells'][t]; lane=t.split('-')[2]; root=Path(admission['run_directory'])/t; inventory={r['path']:r for r in cell['installed']}
 assert len(cell['libraries'])==2 and set(cell['configurations'])=={'Debug','Release'} and 'All requested installations completed successfully' in read(O/(t+'.stdout')).decode()
 for selected,row in cell['detectors'].items():
  p=O/t/'buildtrees/detect_compiler'/('stdout-'+selected+'.log'); markers=dict(s.removeprefix('#COMPILER_').split('#',1) for s in read(p).decode().splitlines() if s.startswith('#COMPILER_')); identity=c['host_compiler'] if selected=='arm64-osx' else c['compilers'][lane]
  assert sha(p)==row['log_sha256'] and markers==row['markers'] and len(markers)==9
  for language in ['C','CXX']: assert all(markers[language+'_'+key]==identity[value] for key,value in [('PATH',language),('ID','id'),('VERSION','version')])
 for cfg,row in cell['configurations'].items():
  base=O/t/'buildtrees/fmt'/(t+('-dbg' if cfg=='Debug' else '-rel'))
  assert sha(base/'CMakeCache.txt')==row['cache_sha256'] and sha(base/'CMakeFiles/4.4.4/CMakeCXXCompiler.cmake')==row['compiler_sha256']
  assert row['cache']['CMAKE_OSX_SYSROOT']=='/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk' and row['cache']['CMAKE_OSX_DEPLOYMENT_TARGET']=='27.0' and row['cache']['BUILD_SHARED_LIBS']==('ON' if t.endswith('dynamic') else 'OFF')
 abi_path=O/t/'buildtrees/fmt'/(t+'.vcpkg_abi_info.txt'); abi=dict(s.split(' ',1) for s in read(abi_path).decode().splitlines()); assert abi==cell['abi']['entries'] and sha(abi_path)==cell['abi']['sha256']
 assert {k:v for k,v in abi.items() if k.startswith('additional_file_')}=={'additional_file_'+str(i):r['sha256'] for i,r in enumerate(c['abi_inputs'][t])}
 for name in ['MARKETPLACE_CPP_LANE','MARKETPLACE_'+lane.upper()+'_PREFIX','PKG_CONFIG']: assert abi['ENV:'+name]==hashlib.sha256(q['environments'][lane][name].encode()).hexdigest()
 for lib in cell['libraries']:
  p=Path(lib['path']); rel=str(p.relative_to(root/'installed')); row=inventory[rel]; payload=read(p)
  assert p.is_file() and not p.is_symlink() and sha(p)==lib['sha256']==row['sha256'] and len(payload)==row['bytes']>0 and oct(p.stat().st_mode&0o777)==row['mode']
  assert read(O/(t+'-'+lib['configuration']+'-arch.stdout')).decode().strip()=='arm64'
  libraries.append(dict(triplet=t,configuration=lib['configuration'],path=str(p),sha256=lib['sha256'],bytes=len(payload)))
 for name in ['fmt-config.cmake','fmt-targets.cmake','fmt-targets-debug.cmake','fmt-targets-release.cmake']:
  p=root/'installed'/t/'share/fmt'/name; row=inventory[str(p.relative_to(root/'installed'))]; assert sha(p)==row['sha256']; s=read(p).decode(); metadata.append(dict(path=str(p),sha256=row['sha256']))
  if name=='fmt-targets.cmake': assert 'add_library(fmt::fmt '+('SHARED' if t.endswith('dynamic') else 'STATIC')+' IMPORTED)' in s
  if name in ['fmt-targets-debug.cmake','fmt-targets-release.cmake']:
   lib=next(r for r in cell['libraries'] if r['configuration']==('Debug' if 'debug' in name else 'Release')); relative=Path(lib['path']).relative_to(root/'installed'/t); assert '${_IMPORT_PREFIX}/'+str(relative) in s
assert len(libraries)==8 and len(metadata)==16
attrs=read(R/'.gitattributes').decode().splitlines(keepends=True); assert hashlib.sha256(''.join(attrs[:2]).encode()).hexdigest()=='dca09211326a748b0b60b0aeb4f41d4b4389d02307bf88131ea82500ab79f7c6'
assert attrs[2:]==['# Preserve exact native receipt bytes; maintained sources retain normal checks.\n','evidence/vcpkg-fmt-build/**/CMakeCache.txt whitespace=-blank-at-eof\n','evidence/vcpkg-fmt-build/**/*.ninja whitespace=-blank-at-eol,-blank-at-eof\n','evidence/vcpkg-fmt-build/**/*.stdout whitespace=-blank-at-eol,-blank-at-eof\n']
initial=load(E/'artifact-static-initial.json'); final=load(E/'artifact-static.json'); scan=load(E/'artifact-secret-scan.json')
assert [r['returncode'] for r in initial['commands']]==[0,0,1] and final['prior_sha256']==sha(E/'artifact-static-initial.json') and [r['returncode'] for r in final['commands']]==[0,0]
assert json.loads(final['commands'][-1]['stdout'])['checks']['baseline']==19 and load(E/'initial-whitespace.json')['returncode']==2
assert len(scan['files'])==349 and scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and len(scan['dispositions'])==7 and scan['supplemental_complete_token_files']==[]
for row in scan['dispositions']: assert row['rule']=='generic-api-key' and sha(R/row['path'])==row['sha256']
gd=Path(read(R/'.git').decode().strip().removeprefix('gitdir: ')); cg=(gd/read(gd/'commondir').decode().strip()).resolve(); ref=read(gd/'HEAD').decode().strip().removeprefix('ref: '); assert read(cg/ref).decode().strip()==a['head'] and ref=='refs/heads/codex/marketplace-native-onboarding'
result=dict(result='PASS',findings=[],candidate_sha256=sha(E/'artifact-candidate.json'),helper_sha256=a['helper_sha256'],contract_sha256=a['contract_sha256'],qualification_sha256=a['qualification_sha256'],head=a['head'],branch=ref,common_git_directory=str(cg),copied_text_pairs=162,reviewed_snapshots=8,native_command_outcomes=29,native_returncode=n['returncode'],native_elapsed_seconds=n['elapsed_seconds'],libraries_hashed_once=libraries,config_metadata=metadata,parent_static_initial_returncodes=[0,0,1],parent_static_final_returncodes=[0,0],parent_Claude_baseline=19,scan_digest_dispositions=7,reviewer_native_commands=0,reviewer_controls=0)
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({k:v for k,v in result.items() if k not in ['libraries_hashed_once','config_metadata']}))
