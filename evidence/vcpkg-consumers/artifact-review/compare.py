import ast,hashlib,json,re,shlex,stat
from datetime import datetime
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace'); E=R/'evidence/vcpkg-consumers'; D=Path(__file__).parent
H=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:Path(p).read_bytes()
J=lambda p:json.loads(read(p))
fixed={'artifact-candidate.json':'db3791bc8335c1ce50e0234dd6684ecb89e50c9aebb5aa29ebc13573505bed58','operation/qualification.json':'aa4005ee513a2ad29b058588994f0ba69f88aa32b7298d362c0bc5893e20837e','native-closure.json':'080aaa34bced37b0cf10b4e6ecf0265f414e21d6b69ca74d78dd0fb3e8bfcc63','contract.json':'508d230c9857f0620853f91eab842f0809f387d2ce3b24c7f7c8da91ca3a26a6','pre-run-review.json':'61a943314426354dcb879ab26ab420f6b20d2ef486573940b4d2cd52984b47dd'}
watched={str(E/n):H(read(E/n)) for n in fixed}; assert all(watched[str(E/n)]==s for n,s in fixed.items())
can=J(E/'artifact-candidate.json'); before=J(E/'candidate.json'); c=J(E/'contract.json'); a=J(E/'admission.json'); rev=J(E/'pre-run-review.json'); q=J(E/'operation/qualification.json'); closure=J(E/'native-closure.json'); native=J(E/'native-execution.json'); launch=J(E/'native-launch.json')
g=Path((R/'.git').read_text().strip().removeprefix('gitdir: ')); common=(g/(g/'commondir').read_text().strip()).resolve(); ref=(g/'HEAD').read_text().strip().removeprefix('ref: '); head=(common/ref).read_text().strip()
assert str(common)=='/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git' and ref=='refs/heads/codex/marketplace-native-onboarding'
assert head==can['head']==a['base_head']==c['base_head']=='b3f1adfe6bc634e08b47f1b2912ee94c09f405ba'
assert len(can['files'])==5
for p,s in can['files'].items(): watched[str(R/p)]=H(read(R/p)); assert watched[str(R/p)]==s
for n in ('CMakeLists.txt','dev/toolchains/vcpkg_consumer.py'): assert can['files'][n]==before['files'][n]
for n in ('candidate.json','admission.json','native-execution.json','native-launch.json','candidate-inputs.json','operation/text-receipts.json','artifact-static.json','artifact-secret-scan.json'):watched[str(E/n)]=H(read(E/n))
assert can['prepared_candidate_sha256']==a['candidate_sha256']==rev['candidate_sha256']==watched[str(E/'candidate.json')]
assert can['qualification_sha256']==closure['qualification_sha256']==fixed['operation/qualification.json']
assert can['text_receipts_sha256']==closure['text_receipts_sha256']==watched[str(E/'operation/text-receipts.json')]
assert a['helper_sha256']==rev['helper_sha256']==native['helper_sha256']==q['helper_sha256']==can['files']['dev/toolchains/vcpkg_consumer.py']
assert a['contract_sha256']==rev['contract_sha256']==fixed['contract.json'] and a['review_sha256']==fixed['pre-run-review.json']
assert rev['result'].startswith('PASS') and not rev['findings']
assert q['admission_sha256']==native['admission_sha256']==watched[str(E/'admission.json')]
assert all(native[k]==v for k,v in launch.items()) and closure['native_execution_sha256']==watched[str(E/'native-execution.json')]
assert native['returncode']==closure['native_returncode']==0
op=Path(a['run_directory']); ld=Path(native['private_launch_directory']); assert op.parent==ld.parent==Path.home()/'.local/state/marketplace-tool-foundation'
assert read(op/'qualification.json')==read(E/'operation/qualification.json')
records=J(E/'operation/text-receipts.json')['files']; texts={}; text_rows=[]
assert len(records)==169
for row in records:
 p=Path(row['source']); assert p.is_relative_to(op) or p.is_relative_to(ld)
 b=row['text'].encode('utf-8'); assert len(b)==row['bytes'] and H(b)==row['sha256'] and read(p)==b
 assert str(p) not in texts; texts[str(p)]=row['text']; text_rows.append({k:row[k] for k in ('source','sha256','bytes')})
assert texts[str(ld/'execution.json')].encode()==read(E/'native-execution.json') and texts[str(ld/'launch.json')].encode()==read(E/'native-launch.json')
for n in ('stdout','stderr'):assert H(texts[str(ld/n)].encode())==native[n+'_sha256']
snapshots=J(E/'candidate-inputs.json')['files']; assert len(snapshots)==7
for row in snapshots:
 rel=row['relative_path']; assert row['path']==str(R/rel) and H(row['text'].encode())==row['sha256']
 expected=before['files'].get(rel,watched.get(str(R/rel))); assert row['sha256']==expected
assert {s['relative_path'] for s in snapshots}==set(before['files'])|{'evidence/vcpkg-consumers/candidate.json','evidence/vcpkg-consumers/contract.json'}
commands={r['case']:r for r in q['commands']}; assert len(commands)==len(q['commands'])==35
sequence=['project-head','default-before','capacity-processes','docker-context','docker-census','docker-stats']
for t in q['cells']:
 sequence += [t+'-configure']+[t+'-'+conf+'-'+kind for conf in ('Debug','Release') for kind in ('build','arch','run')]
assert list(commands)==sequence+['default-after']
for row in q['commands']:
 assert row['returncode']==row['expected_returncode']==0 and 0<=row['elapsed_seconds']<row['timeout_seconds']
 assert len(row['logs'])==2 and all(H(texts[log['path']].encode())==log['sha256'] for log in row['logs'])
summary=[json.loads(line) for line in texts[str(ld/'stdout')].splitlines()]; assert summary[:-1]==[{'case':r['case'],'returncode':0} for r in q['commands']]
assert summary[-1]=={'state':q['state'],'receipt':str(op/'qualification.json')} and texts[str(ld/'stderr')]==''
assert closure['processes']==[{'case':r['case'],'pid':r['pid'],'absent':True} for r in q['commands']]
assert closure['lease_probe']=={'free':True,'contents_unchanged':True} and closure['default_profiles_equal'] and closure['all_command_outcomes_expected']
assert texts[str(op/'default-before.stdout')]==texts[str(op/'default-after.stdout')] and H(texts[str(op/'default-before.stdout')].encode())==c['inputs'][c['default_profile']]
assert texts[str(op/'project-head.stdout')].strip()==head and q['state'].startswith('PASS') and q['lease_released'] and q['protected_state_unchanged']
assert not q['writer_census_before']['processes'] and not q['writer_census_after']['processes']
profile=texts[str(op/'private.sb')]; assert H(profile.encode())==q['confinement']['profile_sha256'] and '(deny file-write*)' in profile and '(deny network*)' in profile
assert q['confinement']['allowed_inherited_fds']==[0,1,2,3]
const={n.targets[0].id:ast.literal_eval(n.value) for n in ast.parse(read(R/'dev/toolchains/vcpkg_consumer.py')).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Constant)}
assert texts[str(op/'source/CMakeLists.txt')]==const['CMAKE'].replace('@ROOT@',str(R)) and texts[str(op/'source/main.cpp')]==const['CPP']
prior=J(R/c['fmt_qualification']); assert set(q['cells'])==set(prior['cells']) and len(q['cells'])==4
cell_rows=[]; binary_rows=[]
for t,cell in q['cells'].items():
 lane=t.split('-')[2]; compiler=c['compilers'][lane]['CXX']; pref=c['prefixes'][lane]; build=op/t; inherited=prior['cells'][t]
 cache={}
 for line in texts[str(build/'CMakeCache.txt')].splitlines():
  if line and not line.startswith(('#','//')) and ':' in line.split('=',1)[0] and '=' in line:
   k,v=line.split('=',1);cache[k.rsplit(':',1)[0]]=v
 assert cache==cell['cache']
 ids=dict(re.findall(r'^set\((CMAKE_CXX_COMPILER(?:_ID|_VERSION)?) "([^"\n]*)"\)$',texts[str(build/'CMakeFiles/4.4.4/CMakeCXXCompiler.cmake')],re.M))
 assert ids==cell['compiler']
 for conf in ('Debug','Release'):
  assert ids==inherited['configurations'][conf]['compiler']
  for k in ('CMAKE_CXX_FLAGS','CMAKE_OSX_SYSROOT','CMAKE_OSX_DEPLOYMENT_TARGET','CMAKE_OSX_ARCHITECTURES','CMAKE_MAKE_PROGRAM'):
   assert cache[k]==inherited['configurations'][conf]['cache'][k]
 assert cache['CMAKE_OSX_SYSROOT']=='/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk' and cache['CMAKE_OSX_DEPLOYMENT_TARGET']=='27.0' and cache['CMAKE_OSX_ARCHITECTURES']=='arm64'
 assert cache['fmt_DIR']==c['fmt_root']+'/'+t+'/installed/'+t+'/share/fmt'
 for k in ('BUILD_SHARED_LIBS','VCPKG_MANIFEST_MODE','VCPKG_MANIFEST_INSTALL','VCPKG_APPLOCAL_DEPS','CMAKE_FIND_USE_PACKAGE_REGISTRY','CMAKE_FIND_USE_SYSTEM_PACKAGE_REGISTRY'): assert cache[k]=='OFF'
 cc=texts[str(build/'compile_commands.json')]; assert H(cc.encode())==cell['compile_commands_sha256']
 for source in ('core.cpp','main.cpp'):
  selected=[r for r in json.loads(cc) if Path(r['file']).name==source]; assert selected
  assert all('-std=c++26' in r['command'] and ('-freflection' in r['command'])==(source=='core.cpp') for r in selected)
 configure=commands[t+'-configure']; assert configure['timeout_seconds']==120 and configure['argv'][:3]==['/usr/bin/sandbox-exec','-f',str(op/'private.sb')]
 assert '-DCMAKE_TOOLCHAIN_FILE='+c['public_toolchain'] in configure['argv'] and '-DVCPKG_TARGET_TRIPLET='+t in configure['argv'] and '-DVCPKG_INSTALLED_DIR='+c['fmt_root']+'/'+t+'/installed' in configure['argv']
 assert texts[str(op/(t+'-configure.stderr'))]==''
 for conf,run in cell['runs'].items():
  assert conf in ('Debug','Release'); label=t+'-'+conf; selected=dict(line.split('=',1) for line in texts[str(build/('parity-'+conf+'.txt'))].splitlines())
  assert selected=={k:run[k] for k in ('binary','fmt','kind')}
  dep=next(v for v in inherited['libraries'] if v['configuration']==conf)
  assert run['fmt']==dep['path'] and run['kind']==('SHARED_LIBRARY' if t.endswith('dynamic') else 'STATIC_LIBRARY')
  binary=Path(run['binary']); assert binary==build/conf/'fmt_parity' and not binary.is_symlink()
  mode=binary.stat().st_mode; assert stat.S_ISREG(mode) and mode&0o111
  b=read(binary); assert b and H(b)==run['sha256']; binary_rows.append({'path':str(binary),'sha256':H(b),'bytes':len(b),'mode':oct(mode&0o777)})
  buildrow=commands[label+'-build']; assert buildrow['timeout_seconds']==180 and buildrow['argv'][-7:]==['--config',conf,'--target','fmt_parity','--parallel','1','--verbose']
  output=texts[str(op/(label+'-build.stdout'))]; assert ' -v -j 1 -f build-'+conf+'.ninja fmt_parity' in output
  compiles=[shlex.split(line.split('] ',1)[1]) for line in output.splitlines() if re.match(r'^\[\d+/\d+\] ',line) and ' -c ' in line]
  assert len(compiles)==2 and {s[-1] for s in compiles}=={str(R/'src/core.cpp'),str(op/'source/main.cpp')}
  for tok in compiles:
   assert tok[0]==compiler and '-std=c++26' in tok and tok[tok.index('-arch')+1]=='arm64' and tok[tok.index('-isysroot')+1]==cache['CMAKE_OSX_SYSROOT'] and '-mmacosx-version-min=27.0' in tok
   assert ('-freflection' in tok)==(tok[-1]==str(R/'src/core.cpp'))
   assert ('-g' in tok) if conf=='Debug' else ('-O3' in tok and '-DNDEBUG' in tok)
  link=next(line for line in output.splitlines() if re.match(r'^\[\d+/\d+\] : && ',line) and ' -o '+conf+'/fmt_parity ' in line)
  lt=shlex.split(link.split('] ',1)[1]); assert compiler in lt and run['fmt'] in lt and 'core/'+conf+'/libresearch_core.a' in lt
  if lane=='p2996':
   assert '-nostdlib++' in lt and all(pref+'/lib/'+n in lt for n in ('libc++.dylib','libc++abi.dylib','libunwind.dylib'))
   assert all('-nostdinc++' in s and pref+'/include/c++/v1' in s for s in compiles)
  assert texts[str(op/(label+'-build.stderr'))]=='' and texts[str(op/(label+'-arch.stdout'))]=='arm64\n' and texts[str(op/(label+'-arch.stderr'))]==''
  assert texts[str(op/(label+'-run.stdout'))]=='reflection value=43, members=1\n'
  trace=texts[str(op/(label+'-run.stderr'))]; matches=re.findall(r'^dyld\[(\d+)\]: <[^>]+> (/.*)$',trace,re.M)
  assert matches and {int(pid) for pid,p in matches}=={commands[label+'-run']['pid']}
  loaded={str(Path(p).resolve()) for pid,p in matches}; assert sorted(loaded)==run['loaded'] and str(binary) in loaded
  runtime_names=['lib/libc++.dylib','lib/libc++abi.dylib','lib/libunwind.dylib'] if lane=='p2996' else ['lib/gcc/current/libstdc++.6.dylib']
  expected_runtime={str((Path(pref)/n).resolve()) for n in runtime_names}; assert expected_runtime<=loaded
  fmt={p for p in loaded if Path(p).name.startswith('libfmt')}; assert fmt==({str(Path(run['fmt']).resolve())} if t.endswith('dynamic') else set())
  system={p for p in loaded if p in ('/usr/lib/libc++.1.dylib','/usr/lib/libc++abi.dylib','/usr/lib/system/libunwind.dylib')}; assert len(system)==3
  cell_rows.append({'triplet':t,'configuration':conf,'compiler':ids,'sdk':cache['CMAKE_OSX_SYSROOT'],'kind':run['kind'],'fmt':run['fmt'],'binary_sha256':run['sha256'],'run_returncode':commands[label+'-run']['returncode'],'build_elapsed_seconds':buildrow['elapsed_seconds'],'selected_runtimes':sorted(expected_runtime),'system_runtimes_also_loaded':sorted(system),'loaded_fmt':sorted(fmt)})
assert len(binary_rows)==len(cell_rows)==8
static=J(E/'artifact-static.json'); assert static['returncode']==0 and json.loads(static['stdout'])['checks']['baseline']==19
scan=J(E/'artifact-secret-scan.json'); assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and len(scan['dispositions'])==2 and not scan['supplemental_complete_token_files']
for row in scan['dispositions']:assert H(read(R/row['path']))==row['sha256']
for p,s in watched.items():
 rel=str(Path(p).relative_to(R))
 if rel in scan['files']:assert scan['files'][rel]==s
assert all(H(read(Path(p)))==s for p,s in watched.items())
report={'result':'PASS','identity':{'checkout':str(R),'branch':ref.removeprefix('refs/heads/'),'head':head,'common_git_directory':str(common)},'helper_sha256':can['files']['dev/toolchains/vcpkg_consumer.py'],'contract_sha256':fixed['contract.json'],'candidate_sha256':fixed['artifact-candidate.json'],'qualification_sha256':fixed['operation/qualification.json'],'native_rc':native['returncode'],'native_elapsed_seconds':native['elapsed_seconds'],'command_count':35,'text_source_pairs':len(text_rows),'candidate_snapshots':7,'consumer_executable_reads':len(binary_rows),'cells':cell_rows,'executables':binary_rows,'recorded_closure':{'absent_pids':35,'lease_free_and_unchanged':True,'default_profiles_equal':True,'protected_state_unchanged':True},'parent_baseline_returncode':0,'parent_baseline_hashes_reported':19,'parent_scanner_raw_returncode':1,'parent_scanner_disposition_returncode':0,'verified_content_digest_findings':2,'watched_hashes':watched,'text_receipts':[{'source':x['source'],'sha256':x['sha256'],'bytes':x['bytes']} for x in text_rows],'native_checks_executed_by_reviewer':0,'maintained_writes':0,'shared_writes':0}
(D/'comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('text_receipts','watched_hashes','cells','executables')}))
