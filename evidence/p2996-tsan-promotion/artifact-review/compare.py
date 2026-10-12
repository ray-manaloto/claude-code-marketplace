import datetime,errno,fcntl,hashlib,json,os,re,stat,struct,subprocess,time,uuid
from pathlib import Path
R=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace');E=R/'evidence/p2996-tsan-promotion';O=E/'operation';D=Path(__file__).parent;HEAD='a3de6bc78da3d5717c5c1367585f396908977e9d';cache={};watched={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p,h=None):
 p=Path(p);p=p if p.is_absolute() else R/p
 if p not in cache:cache[p]=p.read_bytes();cache[p].decode();watched[str(p)]=sha(cache[p])
 if h:assert sha(cache[p])==h,str(p)
 return cache[p]
def js(p,h=None):return json.loads(read(p,h))
C=js(E/'contract.json','f9188f06abf5735196e08775c5e84285b0e4139831d053e41b5a3a376ab4bf53');A=js(E/'admission.json','253133f5c0a69f99910c8da26132bb892876f0a7bc94f7e25e370c4cc7ece290');V=js(E/'pre-run-review.json','b609196ce838799c2ef7fa2ae0faec245a45bd5d0a38b453f0f3b1fab32730c2')
assert read(E/'pre-run-review.json')==read('/private/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-tsan-promotion-retry-review-wcp4dvpy/review.json')
K=js(E/'candidate.json','3746939ef7ca9af3286dc4cf46648eee8244c4c74aa36ea6696018fc43095cc1');X=js(E/'native-execution.json','8d43fd95f82dbf0bd82d56e35582c6a15f23da709ec2de8cd4874190c3d157b9');L=js(E/'native-launch.json','b8e05e24ab4324d786e686338d0549b105bfd30a4345c868921fb4973db84c7c')
Q=js(O/'qualification.json','2dd4ad9fc23367888d762d993bb7becf67aacc3bb33fe2dc112c72ab070b6964');Z=js(O/'closure.json','5987952d6b7f652239835d14d91bc526baf1a2c4d1349126e581495662ab9bf7');I=js(E/'artifact-inventory.json','00c7e8e40f3be826b0a6c2486596ad38f8d051fbeff8d0c2af6c850fd3f06ce0');T=js(O/'text-receipts.json','dc2df71cd71b9255b5032734c90f09f1af9dc2c11f8b6adc8e53056b7533706b');copies=js(O/'copy-manifest.json')['files']
op=Path(A['run_directory']);launch=Path(X['private_launch_directory']);helper=R/'dev/toolchains/p2996_tsan_promote.py'
read(helper,A['helper_sha256']);assert A['helper_sha256']==V['helper_sha256']==X['helper_sha256']==Q['helper_sha256']=='e0a72e001c56d0c756c0ef1b3b74a9f25e783955221ab659f4df199e8772c728'
assert C['base_head']==A['base_head']==K['base_head']==V['head']==HEAD
assert A['contract_sha256']==V['contract_sha256']==sha(cache[E/'contract.json']) and A['candidate_sha256']==V['candidate_sha256']==sha(cache[E/'candidate.json'])
assert A['review_sha256']==sha(cache[E/'pre-run-review.json']) and X['admission_sha256']==Q['admission_sha256']==sha(cache[E/'admission.json'])
assert V['result'].startswith('PASS') and V['findings']==[] and A['installed_write_allowlist']==[C['target']]
assert X['returncode']==Z['native_returncode']==0 and X['elapsed_seconds']>0 and all(X[k]==v for k,v in L.items())
assert X['argv']==[X['argv'][0],'-E','-B',str(helper),'--run-dir',str(op),'--promote']
parse=datetime.datetime.fromisoformat;assert parse(V['recorded_at'])<parse(A['admitted_at'])<parse(X['started_at'])<parse(X['finished_at'])<parse(Z['recorded_at'])
assert Q['state']=='PASS: installed TSan promotion and five sanitizer witnesses' and Q['mutation_started'] and Q['lease_released'] and Q['protected_state_matches_expected']
assert not any(Q.get(k) for k in ('error','recovery','recovery_error','preservation_error'))
assert Q['installed_identity']==Z['installed_identity']==C['after'] and {k:Q['backup'][k] for k in ('sha256','bytes','mode')}==C['before']
assert Z['native_execution_sha256']==sha(cache[E/'native-execution.json']) and Z['qualification_sha256']==I['qualification_sha256']==sha(cache[O/'qualification.json']) and Z['text_receipts_sha256']==sha(cache[O/'text-receipts.json'])
assert len(copies)==8
for row in copies:assert read(row['source'],row['sha256'])==read(row['destination'],row['sha256'])
assert len(T['files'])==Z['retained_text_files']==55 and len({row['source'] for row in T['files']})==55
for row in T['files']:
 b=read(row['source'],row['sha256']);assert len(b)==row['bytes'] and b==row['text'].encode()
assert read(op/'qualification.json')==read(O/'qualification.json') and read(launch/'execution.json')==read(E/'native-execution.json') and read(launch/'launch.json')==read(E/'native-launch.json')
assert read(launch/'stderr',X['stderr_sha256'])==b''
std=[json.loads(line) for line in read(launch/'stdout',X['stdout_sha256']).decode().splitlines()];assert len(std)==25
expected_cases=['project-head','default-before','capacity-processes','editor-identities','editor-cwd','editor-identities-after','docker-context','docker-census','docker-stats','source-before-head','source-before-tree','source-before-diff','source-before-status','promote','tsan-clean','tsan-race','tsan-ubsan-clean','tsan-ubsan-race','tsan-ubsan-overflow','source-after-head','source-after-tree','source-after-diff','source-after-status','default-after']
expected={'tsan-clean':0,'tsan-race':86,'tsan-ubsan-clean':0,'tsan-ubsan-race':86,'tsan-ubsan-overflow':86}
assert [r['case'] for r in Q['commands']]==expected_cases and len(Q['commands'])==Z['command_count']==24
rows={r['case']:r for r in Q['commands']};out={};err={};outcomes=[]
for row in Q['commands']:
 case=row['case'];assert row['returncode']==row['expected_returncode']==expected.get(case,0) and 0<=row['elapsed_seconds']<row['timeout_seconds']
 assert parse(X['started_at'])<=parse(row['started_at'])<parse(X['finished_at']) and len(row['logs'])==2
 for index,suffix in enumerate(('.stdout','.stderr')):
  log=row['logs'][index];assert Path(log['path'])==op/(case+suffix);b=read(log['path'],log['sha256']);(out if index==0 else err)[case]=b
 outcomes.append({'case':case,'returncode':row['returncode'],'expected_returncode':row['expected_returncode'],'elapsed_seconds':row['elapsed_seconds'],'pid':row['pid']})
assert Z['command_outcomes']==[{'case':r['case'],'returncode':r['returncode']} for r in Q['commands']]
assert std[:-1]==[{'case':r['case'],'returncode':r['returncode']} for r in Q['commands']] and std[-1]=={'state':Q['state'],'receipt':str(op/'qualification.json')}
assert out['project-head'].decode().strip()==HEAD
for when in ('before','after'):
 assert out['source-'+when+'-head'].decode().strip()==C['source_provenance']['head'] and out['source-'+when+'-tree'].decode().strip()==C['source_provenance']['tree']
 assert sha(out['source-'+when+'-diff'])==C['source_provenance']['diff_sha256'] and out['source-'+when+'-status']==read(C['source_provenance']['status'])
 assert out['default-'+when]==read(C['default_profile'])
 base=['/usr/bin/git','-c','core.fsmonitor=false','-C',C['source_provenance']['path']]
 for part,args in {'head':['rev-parse','HEAD'],'tree':['rev-parse','HEAD^{tree}'],'diff':['diff','--no-ext-diff','--binary'],'status':['status','--porcelain','--untracked-files=all']}.items():assert rows['source-'+when+'-'+part]['argv']==base+args
assert rows['default-before']['argv']==rows['default-after']['argv']
assert all(err[c]==b'' for c in expected_cases if c not in expected)
assert out['docker-context'].decode().strip()==A['docker_context'] and out['docker-census'].decode().splitlines()==A['containers']
cap=Q['capacity'];assert cap['free_bytes']>=C['disk_reserve_bytes'] and cap['load'][0]<=2*cap['cpus'] and cap['total_cpu_percent']<=75*cap['cpus'] and cap['container_cpu_percent']<=50*cap['cpus']
ps=out['capacity-processes'].decode().splitlines();assert abs(sum(float(line.split()[1]) for line in ps)-cap['total_cpu_percent'])<0.001
active=[line for line in ps if re.fullmatch(r'(?:clang(?:\+\+)?|gcc|g\+\+)(?:-[0-9]+)?|cc1(?:plus)?|ninja|make|cmake|ld|clangd|clang-tidy|include-what-you-use|vcpkg',Path(line.split(maxsplit=2)[-1]).name)]
assert active==cap['active'] and {line.split()[0] for line in active}==set(cap['admitted_editor_services'])==set(C['editor_services']['processes'])
assert all(float(line.split()[1])<=C['editor_services']['maximum_cpu_percent_per_service'] for line in active) and sum(float(line.split()[1]) for line in active)<=C['editor_services']['maximum_cpu_percent_total']
assert out['editor-identities']==out['editor-identities-after'];ids={}
for line in out['editor-identities'].decode().splitlines():
 parts=line.split(maxsplit=7);assert len(parts)==8;ids[parts[0]]={'ppid':parts[1],'started_at':' '.join(parts[2:7]),'executable':parts[7]}
expected_ids={}
for pid,record in C['editor_services']['processes'].items():expected_ids[pid]=record['identity'];expected_ids.update(record['ancestors'])
assert ids==expected_ids
cwdlines=out['editor-cwd'].decode().splitlines();expected_cwd=[]
for pid,record in C['editor_services']['processes'].items():expected_cwd.extend(['p'+pid,'fcwd','n'+record['cwd']])
assert cwdlines==expected_cwd
assert abs(sum(float(json.loads(line)['CPUPerc'].rstrip('%')) for line in out['docker-stats'].decode().splitlines())-cap['container_cpu_percent'])<0.001
assert Q['writer_census_before']['processes']==Q['writer_census_after']['processes'] and Q['writer_census_before']['lock_holders']==Q['writer_census_after']['lock_holders']==[]
for name,extra in [('private',''),('mutation',' (literal '+json.dumps(C['target'])+')')]:
 wanted='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(op))+') (literal "/dev/null")'+extra+')\n(deny network*)\n'
 assert read(op/(name+'.sb'),Q['confinement'][name]).decode()==wanted
promote=rows['promote']['argv'];assert promote[:7]==['/usr/bin/sandbox-exec','-f',str(op/'mutation.sb'),X['argv'][0],'-E','-B','-c']
assert promote[7]=='import json,sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from p2996_tsan_runtime import replace_exact;replace_exact(Path(sys.argv[2]),Path(sys.argv[3]),json.loads(sys.argv[4]),json.loads(sys.argv[5]))'
assert promote[8:11]==[str(R/'dev/toolchains'),str(op/'staged.dylib'),C['target']] and json.loads(promote[11])==C['before'] and json.loads(promote[12])==C['after']
assert out['promote']==b'' and err['promote']==b''
loader="import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"
prefix=Path(C['prefixes']['p2996']);selected={str((prefix/'lib'/n).resolve()) for n in ('libc++.dylib','libc++abi.dylib','libunwind.dylib')};diagnostics=[];runtime_uuids=set()
for mode,settings in C['sanitizers'].items():
 assert Q['cells'][mode]['binary']==C['witnesses'][mode] and set(Q['cells'][mode]['runs'])=={'clean',*settings['errors']}
 for case,wantedrc in {'clean':0,**{n:86 for n in settings['errors']}}.items():
  label=mode+'-'+case;argv=rows[label]['argv'];assert argv[:8]==['/usr/bin/sandbox-exec','-f',str(op/'private.sb'),X['argv'][0],'-E','-B','-c',loader]
  assert argv[8:10]==[C['witnesses'][mode]['path'],case] and len(argv)==11 and json.loads(argv[10])==C['runtime_environment']
  assert out[label]==b'reflection value=43, members=1\n';trace=err[label].decode();lines=trace.splitlines();dyld=[s for s in lines if s.startswith('dyld[') and '/' in s];loaded={str(Path(s[s.index('/'):]).resolve()) for s in dyld}
  assert loaded==set(Q['cells'][mode]['runs'][case]['loaded']) and selected.issubset(loaded) and {p for p in loaded if Path(p).name.startswith('libclang_rt.')}=={C['target']}
  target_lines=[s for s in dyld if s[s.index('/'):] == C['target']];assert len(target_lines)==1;match=re.search(r'<([0-9A-Fa-f-]{36})>',target_lines[0]);assert match;runtime_uuids.add(match.group(1).upper())
  assert Q['cells'][mode]['runs'][case]['expected_returncode']==wantedrc and rows[label]['timeout_seconds']==20
  assert not re.search(r'FATAL: ThreadSanitizer|Sanitizer CHECK failed',trace)
  diagnostic='\n'.join(s for s in lines if not s.startswith('dyld[')).strip();detail={}
  if case=='clean':assert diagnostic==''
  elif case=='race':
   assert trace.count('WARNING: ThreadSanitizer: data race')==1 and 'runtime error:' not in trace
   writes=re.findall(r'[Ww]rite of size 4 at (0x[0-9a-fA-F]+) by (main thread|thread T\d+)',diagnostic);assert len(writes)==2 and writes[0][0]==writes[1][0] and {x[1] for x in writes}=={'main thread','thread T1'}
   assert 'witness:arm64' in diagnostic;detail={'race_reports':1,'same_address_writes':2,'threads':['main thread','T1'],'witness_arm64_frames':True}
  else:
   assert trace.count('runtime error: signed integer overflow: 2147483647 + 1 cannot be represented')==1 and 'tsan_witness.cpp:40:37' in trace and 'WARNING: ThreadSanitizer' not in trace;detail={'signed_overflow_reports':1,'witness_source_line':'tsan_witness.cpp:40:37'}
  diagnostics.append({'case':label,'returncode':wantedrc,'reflection_stdout_exact':True,'runtime':C['target'],'selected_cxx_libraries_present':True,'other_system_libraries_also_loaded':True,'diagnostic':detail})
assert set(Q['cells'])=={'tsan','tsan-ubsan'} and len(diagnostics)==5
owned=[{'case':'native-helper','pid':X['pid']}]+[{'case':r['case'],'pid':r['pid']} for r in Q['commands']]
assert Z['processes']==[r|{'absent':True} for r in owned] and Z['lease_probe']=={'free':True,'contents_unchanged':True}
expected_artifacts=[{'kind':'installed-runtime','path':C['target'],**C['after']},{'kind':'original-backup','path':str(op/'original.dylib'),**C['before']},{'kind':'qualified-private-runtime','path':C['replacement'],**C['replacement_identity']}]+[{'kind':mode+'-binary',**record} for mode,record in C['witnesses'].items()]
assert I['artifacts']==expected_artifacts
# Complete all text assertions before the exactly-once binary reads.
git=[]
for args,value in [(['rev-parse','--show-toplevel'],str(R)),(['symbolic-ref','--short','HEAD'],'codex/marketplace-native-onboarding'),(['rev-parse','HEAD'],HEAD),(['rev-parse','--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
 argv=['/usr/bin/git','-c','core.fsmonitor=false']+args;p=subprocess.run(argv,cwd=R,capture_output=True,text=True,timeout=10);assert p.returncode==0 and p.stdout.strip()==value;git.append({'argv':argv,'returncode':p.returncode,'stdout':p.stdout})
for p,h in watched.items():assert sha(Path(p).read_bytes())==h,(p,'changed during review')
binaries=[]
for row in expected_artifacts:
 p=Path(row['path']);before=p.lstat();assert p==p.resolve() and stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1
 b=p.read_bytes();after=p.lstat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 assert len(b)==row['bytes']==before.st_size and sha(b)==row['sha256'];mode=oct(stat.S_IMODE(before.st_mode));assert 'mode' not in row or mode==row['mode']
 header=struct.unpack('<8I',b[:32]);assert header[0]==0xfeedfacf and header[1]==0x0100000c and header[3]==(2 if row['kind'].endswith('-binary') else 6)
 at=32;uuids=[]
 for _ in range(header[4]):
  cmd,size=struct.unpack('<II',b[at:at+8]);assert size>=8 and at+size<=len(b)
  if cmd==0x1b:uuids.append(str(uuid.UUID(bytes=b[at+8:at+24])).upper())
  at+=size
 if row['kind'] in ('installed-runtime','qualified-private-runtime'):assert set(uuids)==runtime_uuids
 binaries.append(row|{'mode_observed':mode,'reads':1,'stable_canonical_owned_regular_single_link':True,'mach_o_cpu':'arm64','mach_o_type':header[3],'uuid':uuids})
# Read-only, nonblocking live closure observations; no process termination or lease-file writes.
probe_time=datetime.datetime.now(datetime.UTC).isoformat();process_probes=[]
for row in owned:
 try:os.kill(row['pid'],0);state='exists; ownership or PID reuse unverified'
 except ProcessLookupError:state='absent'
 except PermissionError:state='exists; permission denied'
 process_probes.append(row|{'state':state})
lock=Path('/Users/rmanaloto/.local/state/dotfiles/heavy-gate.lock');lease={'path':str(lock),'probed_at':probe_time,'operation':'O_RDONLY|O_NOFOLLOW and LOCK_EX|LOCK_NB, immediately unlocked; no writes'}
try:
 assert lock==lock.resolve();fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd);assert stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid() and s.st_nlink==1 and s.st_size<=65536
  before=os.read(fd,65537);started=time.monotonic()
  try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:lease['free']=False
  else:
   try:lease['free']=True
   finally:fcntl.flock(fd,fcntl.LOCK_UN)
  lease['elapsed_seconds']=time.monotonic()-started;os.lseek(fd,0,os.SEEK_SET);after=os.read(fd,65537)
  lease.update(contents_unchanged=before==after,contents_sha256=sha(after),inode_unchanged=(s.st_dev,s.st_ino)==(lock.stat().st_dev,lock.stat().st_ino))
 finally:os.close(fd)
except (OSError,AssertionError) as error:lease['probe_unverified']=type(error).__name__
result={'result':'PASS: bounded installed TSan artifact and closure review','findings':[],'head':HEAD,'helper_sha256':A['helper_sha256'],'contract_sha256':A['contract_sha256'],'candidate_sha256':A['candidate_sha256'],'review_sha256':A['review_sha256'],'admission_sha256':sha(cache[E/'admission.json']),'native_execution_sha256':sha(cache[E/'native-execution.json']),'qualification_sha256':sha(cache[O/'qualification.json']),'closure_sha256':sha(cache[O/'closure.json']),'inventory_sha256':sha(cache[E/'artifact-inventory.json']),'native_execution_returncode':X['returncode'],'native_elapsed_seconds':X['elapsed_seconds'],'command_outcomes':outcomes,'text_receipts_checked':55,'command_logs_checked':48,'copy_pairs_checked':8,'diagnostics':diagnostics,'runtime_uuid':sorted(runtime_uuids),'source_default_before_after_verified':True,'capacity_receipt_checks':cap,'binary_reads':len(binaries),'binary_bytes':sum(r['bytes'] for r in binaries),'binary_checks':binaries,'historical_closure_process_count':25,'live_process_probes':process_probes,'live_lease_probe':lease,'git':git,'watched_text_sha256':watched,'limits':['Native commands and sanitizer witnesses were not rerun. Actual native exit claims derive from verified retained execution and command receipts.','No broad 190-input/881-source/28-tool/ABI inventory rehash, installed guard rerun, compiler, build, install, service, container, network, model session or global configuration changes.','Current reads cover exactly five inventory binaries, once each. No staged-runtime, ASan, compiler or other library binary read.','PID zero-signal probes report present/absent at the recorded time; a present PID would need ownership/reuse investigation. Lease probe is nonblocking and read-only; no lease contents were written.','Recovery/rollback was not exercised on this successful run. No larger sanitizer matrix, fresh Claude/Codex session or full OCI acceptance was performed.','No raw diagnostic logs or environment contents are included in this private comparison output.']}
(D/'comparison.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'result':result['result'],'commands':24,'logs':48,'text_receipts':55,'artifacts':len(binaries),'artifact_bytes':result['binary_bytes'],'live_absent_pids':sum(r['state']=='absent' for r in process_probes),'lease_free':lease.get('free'),'lease_unchanged':lease.get('contents_unchanged')}))
