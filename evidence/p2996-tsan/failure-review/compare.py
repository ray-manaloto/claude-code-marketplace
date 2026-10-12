import datetime,hashlib,json,os,pathlib,re,stat,struct,subprocess,uuid
ROOT=pathlib.Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-tsan';OUT=pathlib.Path(__file__).parent
watched={};cache={};checks={}
def raw(path,sha=None,size=None):
    p=pathlib.Path(path)
    if str(p) not in cache:
        assert p.stat().st_size<1000000,(str(p),'outside small text bound')
        b=p.read_bytes();b.decode('utf-8');cache[str(p)]=b;watched[str(p)]=hashlib.sha256(b).hexdigest()
    b=cache[str(p)]
    if sha is not None:assert watched[str(p)]==sha,(str(p),watched[str(p)],sha)
    if size is not None:assert len(b)==size
    return b
def load(path,sha=None):return json.loads(raw(path,sha))
def digest(path):return watched[str(path)]
def stamp(s):return datetime.datetime.fromisoformat(s)
candidate=load(E/'closure-candidate.json','dac6fb8112f2bb5eecf4265eaa82dc4dcf00dff52d13f40c0dfd536444a1e71c')
c=load(E/'contract.json','4bb345582c7253694e37b958c77154b5d98ac522e3e89858eac2fb2c2b828ea5')
prepared=load(E/'candidate.json',candidate['prepared_candidate_sha256'])
review=load(E/'pre-run-review.json',candidate['preparation_review_sha256'])
assert review['result'].startswith('PASS') and review['findings']==[]
assert review['candidate_sha256']==digest(E/'candidate.json') and review['contract_sha256']==digest(E/'contract.json')
assert candidate['head']==prepared['head']==c['base_head']=='757a72bd22d774d8533b8f831c8ee604ce0109b8'
snap=load(E/'closure-inputs.json','2ba276799d3594d5432c63b1325940407b0dc8eeea5f5d88fed279fbd8190cd6')
assert len(snap['files'])==10
for row in snap['files']:assert raw(row['source'],row['sha256'],row['bytes'])==row['text'].encode()
assert set(candidate['files'])==set(prepared['files']) and len(candidate['files'])==5
for name,sha in candidate['files'].items():assert digest(ROOT/name)==sha
helper=ROOT/'dev/toolchains/p2996_tsan.py';fixture=ROOT/'dev/toolchains/tsan_witness.cpp'
assert digest(helper)==review['helper_sha256']==prepared['files']['dev/toolchains/p2996_tsan.py']=='529c032a98b31963e2ee218dfe81eb2a250924f7ef984376fc026b30f38683d1'
assert digest(fixture)==review['fixture_sha256']==prepared['files']['dev/toolchains/tsan_witness.cpp']
assert len(c['source_inputs'])==846
checks['candidate']={'snapshots':10,'maintained_files':candidate['files'],'helper_fixture_contract_unchanged':True,'preparation_proof_reused':True,'source_inputs_rehashed':0}
manifest_names={'capacity-copy-manifest.json':17,'capacity-retry-copy-manifest.json':17,'preparation-review-copy-manifest.json':6,'blocked-writer-preflight/copy-manifest.json':8,'initial-closure-attempt/copy-manifest.json':13,'operation/copy-manifest.json':10}
archived_sources={str(E/name) for name in ['admission.json','native-launch.json','native-execution.json']}
manifest_counts={};archived=[];direct_pairs=0
for name,count in manifest_names.items():
    m=load(E/name);assert len(m['files'])==count
    for row in m['files']:
        assert pathlib.Path(row['destination']).is_relative_to(E)
        value=raw(row['destination'],row['sha256'])
        if name=='blocked-writer-preflight/copy-manifest.json' and row['source'] in archived_sources:
            archived.append(row)
        else:
            assert raw(row['source'],row['sha256'])==value
            direct_pairs+=1
    manifest_counts[name]=count
assert direct_pairs==68 and len(archived)==3
B=E/'blocked-writer-preflight'
blocked_admission=load(B/'admission.json');blocked_q=load(B/'qualification.json')
blocked_exec=load(B/'execution.json');blocked_launch=load(B/'launch.json');blocked_close=load(B/'closure.json','0d92525c034a5dd04914bdb1c4470404aaf9958514cd9ab94bcfebd8a9d02a9d')
assert raw(B/'native-launch.json')==raw(B/'launch.json') and raw(B/'native-execution.json')==raw(B/'execution.json')
assert blocked_exec['admission_sha256']==blocked_launch['admission_sha256']==blocked_q['admission_sha256']==digest(B/'admission.json')
assert blocked_exec['returncode']==blocked_close['native_returncode']==1
assert blocked_q['state']=='FAIL' and blocked_q['commands']==[] and blocked_q['cells']=={} and blocked_q['protected_state_unchanged'] is True
assert blocked_close['commands']==0 and blocked_close['helper_pid']==blocked_exec['pid']==77091 and blocked_close['helper_absent'] is True
assert blocked_close['qualification_sha256']==digest(B/'qualification.json') and blocked_close['protected_state_unchanged'] is True
assert blocked_close['unknown_process']=={'pid':76980,'name':'mise','terminated_by_this_task':False}
assert '76980' in blocked_q['error'] and 'census()' in raw(B/'stderr',blocked_exec['stderr_sha256']).decode()
raw(B/'stdout',blocked_exec['stdout_sha256'])
assert blocked_exec['helper_sha256']==blocked_q['helper_sha256']==digest(helper)
checks['copy_manifests']={'rows':manifest_counts,'total':71,'direct_source_destination_pairs':68,'historical_entries_bound_to_original_native_records':archived,'note':'The three root admission/launch/execution sources were replaced by the separately admitted retry. Their archived bytes remain bound by original private launch/execution and qualification receipts.'}
checks['blocked_preflight']={'returncode':1,'elapsed_seconds':blocked_exec['elapsed_seconds'],'commands':0,'compiler_or_lease_started':False,'recorded_helper_absent':True,'blocking_mise_pid':76980,'process_terminated_by_task':False,'user_context':'Parent relayed the user clarification that update-all was running; this is legitimate concurrent work, not hostile or unexplained ownership.'}
admission=load(E/'admission.json');launch=load(E/'native-launch.json');native=load(E/'native-execution.json')
q=load(E/'operation/qualification.json',candidate['qualification_sha256'])
closure=load(E/'operation/closure.json',candidate['closure_sha256']);inventory=load(E/'artifact-inventory.json',candidate['artifact_inventory_sha256'])
diagnosis=load(E/'startup-diagnosis.json',candidate['diagnosis_sha256'])
assert admission['previous_preflight_sha256']==digest(B/'closure.json')
OP=pathlib.Path(admission['run_directory']);LP=pathlib.Path(native['private_launch_directory'])
assert native['returncode']==closure['native_returncode']==1 and q['state']=='FAIL'
assert q['helper_sha256']==native['helper_sha256']==launch['helper_sha256']==admission['helper_sha256']==digest(helper)
assert q['admission_sha256']==native['admission_sha256']==launch['admission_sha256']==digest(E/'admission.json')
assert admission['review_sha256']==digest(E/'pre-run-review.json') and admission['candidate_sha256']==digest(E/'candidate.json') and admission['contract_sha256']==digest(E/'contract.json')
assert native['argv']==launch['argv'] and native['argv'][1:]==['-E','-B',str(helper),'--run-dir',str(OP),'--build']
assert native['dispatch_sha256']==launch['dispatch_sha256']=='17a25bf2bd165e4e884d171fabc14ff1b72d4781d55920698c1e450a947d7aed'
assert stamp(blocked_exec['finished_at'])<stamp(admission['admitted_at'])<stamp(native['started_at'])<stamp(native['finished_at'])
assert q['protected_state_unchanged'] is True and not q.get('preservation_error')
assert set(q['cells'])=={'tsan'} and q['cells']['tsan']['runs']=={}
assert not any(key in q for key in ['lease_released','writer_census_after'])
texts=load(E/'operation/text-receipts.json',closure['text_receipts_sha256']);assert len(texts['files'])==52
textmap={row['source']:row for row in texts['files']};assert len(textmap)==52
for row in texts['files']:assert raw(row['source'],row['sha256'],row['bytes'])==row['text'].encode()
assert raw(OP/'qualification.json')==raw(E/'operation/qualification.json')
assert raw(LP/'execution.json')==raw(E/'native-execution.json') and raw(LP/'launch.json')==raw(E/'native-launch.json')
raw(LP/'stdout',native['stdout_sha256']);stderr=raw(LP/'stderr',native['stderr_sha256']).decode()
assert 'AssertionError: tsan-clean' in stderr and 'timeout=20' in stderr
commands=q['commands'];assert len(commands)==18
cases={r['case']:r for r in commands};assert len(cases)==18
expectedcases=['project-head','default-before','capacity-processes','editor-identities','editor-cwd','editor-identities-after','docker-context','docker-census','docker-stats','source-before-head','source-before-tree','source-before-diff','source-before-status','tsan-core','tsan-link','tsan-arch-object','tsan-arch-binary','tsan-clean']
assert list(cases)==expectedcases
for index,row in enumerate(commands):
    assert row['returncode']==(-11 if index==17 else 0)
    if index<17:assert row['expected_returncode']==0 and row['elapsed_seconds']<row['timeout_seconds']
    else:assert row['elapsed_seconds']<20 and 'expected_returncode' not in row and 'timeout_seconds' not in row
    assert stamp(native['started_at'])<=stamp(row['started_at'])<stamp(native['finished_at'])
    assert len(row['logs'])==2
    for suffix,log in zip(['.stdout','.stderr'],row['logs']):
        assert log['path']==str(OP/(row['case']+suffix)) and log['sha256']==textmap[log['path']]['sha256']
        raw(log['path'],log['sha256'])
def optext(label,suffix='stdout'):return cache[str(OP/(label+'.'+suffix))].decode()
assert optext('project-head').strip()==candidate['head']
assert optext('tsan-clean')==''
assert optext('tsan-core')==optext('tsan-core','stderr')==optext('tsan-link')==''
assert 'warning: input verification failed' in optext('tsan-link','stderr')
assert optext('tsan-arch-object')==optext('tsan-arch-binary')=='arm64\n'
profile='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(OP))+') (literal "/dev/null"))\n(deny network*)\n'
assert raw(OP/'private.sb',q['confinement']['profile_sha256']).decode()==profile
assert q['confinement']['allowed_inherited_fds']==[0,1,2,3]
for name in ['tsan-core','tsan-link','tsan-arch-object','tsan-arch-binary','tsan-clean']:
    assert cases[name]['argv'][:3]==['/usr/bin/sandbox-exec','-f',str(OP/'private.sb')]
assert '-freflection' in cases['tsan-core']['argv'] and '-freflection' not in cases['tsan-link']['argv']
assert '-fsanitize=thread' in cases['tsan-core']['argv'] and '-fsanitize=thread' in cases['tsan-link']['argv']
launcher="import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"
assert cases['tsan-clean']['argv'][3:]==[native['argv'][0],'-E','-B','-c',launcher,str(OP/'tsan/witness'),'clean',json.dumps(c['runtime_environment'])]
trace=optext('tsan-clean','stderr');images={}
for line in trace.splitlines():
    m=re.fullmatch(r'dyld\[87786\]: <([0-9A-Fa-f-]+)> (/.+)',line)
    if m:images[m.group(2)]=m.group(1).lower()
prefix=c['prefixes']['p2996'];tsanpath=prefix+'/lib/clang/21/lib/darwin/libclang_rt.tsan_osx_dynamic.dylib'
assert {p for p in images if pathlib.PurePosixPath(p).name.startswith('libclang_rt.')}=={tsanpath}
assert all(prefix+'/lib/'+n in images for n in ['libc++.1.0.dylib','libc++abi.1.0.dylib','libunwind.1.0.dylib'])
assert images[str(OP/'tsan/witness')]==diagnosis['binary_uuid']
assert 'reflection value=' not in trace and 'WARNING: ThreadSanitizer: data race' not in trace
post=load(E/'operation/post-failure-checks.json',closure['post_failure_checks_sha256']);assert len(post['commands'])==5
for row,before in zip(post['commands'],['source-before-head','source-before-tree','source-before-diff','source-before-status','default-before']):
    assert row['case']==before.replace('before','after') and row['argv']==cases[before]['argv']
    assert row['returncode']==0 and row['timeout_seconds']==30 and row['elapsed_seconds']<30
    for log in row['logs']:raw(log['path'],log['sha256']);assert log['sha256']==textmap[log['path']]['sha256']
    assert cache[row['logs'][0]['path']]==cache[str(OP/(before+'.stdout'))] and cache[row['logs'][1]['path']]==b''
sp=c['source_provenance']
assert optext('source-before-head').strip()==sp['head'] and optext('source-before-tree').strip()==sp['tree']
assert digest(OP/'source-before-diff.stdout')==sp['diff_sha256'] and digest(OP/'source-before-status.stdout')==c['inputs'][sp['status']]
assert digest(OP/'default-before.stdout')==c['inputs'][c['default_profile']]
assert all(v is None for k,v in json.loads(optext('default-before'))['selected'].items() if k.startswith('DYLD_'))
assert closure['native_execution_sha256']==digest(E/'native-execution.json') and closure['qualification_sha256']==inventory['qualification_sha256']==digest(E/'operation/qualification.json')
assert closure['command_count']==18 and closure['retained_text_files']==52 and closure['post_failure_read_commands']==5
assert closure['command_outcomes']==[{'case':r['case'],'returncode':r['returncode']} for r in commands]
assert closure['processes']==[{'case':'native-helper','pid':native['pid'],'absent':True}]+[{'case':r['case'],'pid':r['pid'],'absent':True} for r in commands]
assert closure['lease_probe']=={'free':True,'contents_unchanged':True} and closure['protected_state_unchanged'] is closure['source_and_default_outputs_match'] is True
assert closure['state']=='CLOSED FAIL: TSan clean startup signal 11 before main; remaining witnesses unexecuted'
collectexec=load(E/'operation/collection-execution.json');assert collectexec['returncode']==0 and collectexec['stderr']==''
assert collectexec['script_sha256']=='eba568f7cd8d10ce5dae4dfa88a15798bac9dd6ca0ff44eeecb8257b84b47234'
raw(collectexec['argv'][3],collectexec['script_sha256'])
assert stamp(native['finished_at'])<stamp(closure['recorded_at'])
I=E/'initial-closure-attempt';initial_exec=load(I/'execution.json');initial_post=load(I/'post-failure-checks.json')
assert initial_exec['returncode']==1 and 'AssertionError: default-after' in initial_exec['stderr']
assert len(initial_post['commands'])==5 and all(row['returncode']==0 for row in initial_post['commands'])
for row,before in zip(initial_post['commands'],['source-before-head','source-before-tree','source-before-diff','source-before-status','default-before']):
    assert row['argv']==cases[before]['argv']
    for log in row['logs']:raw(log['path'],log['sha256'])
    same=cache[row['logs'][0]['path']]==cache[str(OP/(before+'.stdout'))]
    assert same==(before!='default-before')
initial_source=raw(I/'collect.py.source',initial_exec['script_sha256']).decode()
corrected_source=raw(E/'operation/collect.py.source',collectexec['script_sha256']).decode()
bad=" env=dict(os.environ,GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_TERMINAL_PROMPT='0',GIT_OPTIONAL_LOCKS='0')\n"
fixed=" normal=next(r for r in q['commands'] if r['case']=='default-before')['argv']\n context=Path(normal[-1]).parent/'context.json'\n env=load(context)['environment'] | {'MISE_OFFLINE':'1','MISE_AUTO_INSTALL':'0','MISE_EXEC_AUTO_INSTALL':'0','MISE_TASK_RUN_AUTO_INSTALL':'0','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_SYSTEM':'/dev/null','GIT_TERMINAL_PROMPT':'0','GIT_OPTIONAL_LOCKS':'0'}\n"
assert bad in initial_source and initial_source.replace(bad,fixed)==corrected_source
checks['native_failure']={'outer_returncode':1,'outer_elapsed_seconds':native['elapsed_seconds'],'command_count':18,'successful_commands':17,'failed_case':'tsan-clean','failed_pid':cases['tsan-clean']['pid'],'failed_returncode':-11,'failed_elapsed_seconds':cases['tsan-clean']['elapsed_seconds'],'expected_clean_returncode_from_reviewed_source':0,'timeout_seconds_from_reviewed_source':20,'reflection_stdout_empty':True,'no_completed_runtime_cases':True,'combined_and_error_cases_unexecuted':True,'loader_trace_installed_tsan':tsanpath,'linker_warning':optext('tsan-link','stderr'),'protected_finally_receipt':True}
checks['failure_closure']={'current_collector_returncode':0,'current_collector_elapsed_seconds':collectexec['elapsed_seconds'],'initial_collector_returncode':1,'initial_collector_elapsed_seconds':initial_exec['elapsed_seconds'],'initial_default_only_mismatch':True,'corrected_collector_only_changes_environment_selection':True,'post_failure_commands':5,'post_failure_returncodes':[0]*5,'source_and_default_match':True,'copied_private_texts':52,'native_log_bindings':36,'post_failure_log_bindings':10,'owned_pids_recorded_absent':19,'lease_recorded_free_unchanged':True,'current_pid_or_lease_probes':False}
capacity_checks=[]
for folder,admit in [('capacity',blocked_admission),('capacity-retry',admission)]:
    cap=load(E/folder/'capacity.json',admit['capacity_sha256']);ce=load(E/folder/'execution.json',admit['capacity_execution_sha256'])
    assert cap['state']=='PASS' and ce['returncode']==0 and ce['stderr']==''
    assert cap['held_lease'] is cap['native_operation_started'] is False
    assert cap['script_sha256']=='cf2fb1ba64fe88b7b8305af706e84942da4a5eeb8148ca8735f831ac28ef6e74'
    assert len(cap['commands'])==7 and cap['docker_context']==admit['docker_context'] and cap['containers']==admit['containers']
    for row in cap['commands']:
        assert row['returncode']==0 and row['elapsed_seconds']<row['timeout_seconds']
        for log in row['logs']:raw(log['path'],log['sha256'])
    assert stamp(cap['recorded_at'])<stamp(admit['admitted_at'])
    capacity_checks.append({'name':folder,'returncode':0,'elapsed_seconds':ce['elapsed_seconds'],'commands':7,'admission_binds_capacity_receipt':True})
for cap in [load(E/'capacity/capacity.json'),load(E/'capacity-retry/capacity.json'),q['capacity']]:
    assert cap['free_bytes']>=c['disk_reserve_bytes'] and cap['load'][0]<=2*cap['cpus']
    assert cap['total_cpu_percent']<=75*cap['cpus'] and cap['container_cpu_percent']<=50*cap['cpus']
    assert cap['admitted_editor_services']==['73356','73398']
assert optext('editor-identities')==optext('editor-identities-after')
assert optext('docker-context').strip()==admission['docker_context'] and optext('docker-census').splitlines()==admission['containers']
checks['recorded_capacity']=capacity_checks
# Read only the explicitly owned crash file; retain no complete crash content in output.
crash_path=pathlib.Path(diagnosis['source'])
assert str(crash_path)=='/Users/rmanaloto/Library/Logs/DiagnosticReports/witness-2026-10-11-210915.ips'
crashtext=raw(crash_path,diagnosis['source_sha256'],diagnosis['source_bytes']).decode()
header,end=json.JSONDecoder().raw_decode(crashtext);body=json.loads(crashtext[end:])
assert body['pid']==diagnosis['pid']==cases['tsan-clean']['pid']==87786
assert body['parentPid']==diagnosis['parent_pid']==native['pid']==86554
assert body['procPath']==diagnosis['reported_path']=='/Users/USER/*/witness'
assert body['captureTime']==diagnosis['capture_time'] and body['exception']==diagnosis['exception'] and body['termination']==diagnosis['termination']
assert body['exception']['signal']=='SIGSEGV' and body['termination']['code']==11
captured=datetime.datetime.strptime(body['captureTime'],'%Y-%m-%d %H:%M:%S.%f %z')
assert stamp(native['started_at'])<captured<stamp(native['finished_at'])
frames=body['threads'][body['faultingThread']]['frames'];curated=[{'image':body['usedImages'][f['imageIndex']].get('name'),**f} for f in frames]
assert curated==diagnosis['faulting_thread_frames'] and len(curated)==36
owned_images={row['name']:row for row in body['usedImages'] if row.get('name') in ['witness','libclang_rt.tsan_osx_dynamic.dylib']}
assert owned_images['witness']['uuid']==diagnosis['binary_uuid']==images[str(OP/'tsan/witness')]
assert owned_images['libclang_rt.tsan_osx_dynamic.dylib']['uuid']==images[tsanpath]
assert diagnosis['private_binary']==str(OP/'tsan/witness') and diagnosis['binary_sha256']==q['cells']['tsan']['artifacts']['binary']['sha256']
symbols=[f.get('symbol','') for f in curated]
for needed in ['__tsan::SlotLock(', '__tsan::Release(', 'wrap_dispatch_once', 'dyld_shared_cache_iterate_text', 'GetDyldImageHeaderViaSharedCache', '__tsan::InitializePlatform', '__tsan::Initialize(', 'libSystem_initializer', 'dyld4::prepare']:
    assert any(needed in s for s in symbols),needed
prereq=load(E/'source-prerequisite.json',c['inputs']['evidence/p2996-tsan/source-prerequisite.json'])
assert all(row in prereq['references'] for row in diagnosis['source_excerpts'])
assert 'untested' in diagnosis['inference']
checks['owned_crash']={'source':str(crash_path),'source_sha256':diagnosis['source_sha256'],'source_bytes':diagnosis['source_bytes'],'pid':87786,'parent_pid':86554,'capture_time':diagnosis['capture_time'],'reported_redacted_path':diagnosis['reported_path'],'binary_uuid':diagnosis['binary_uuid'],'faulting_frames_exact':36,'exception_signal':'SIGSEGV','initialization_stack_verified':True,'patch_effectiveness_tested':False,'whole_crash_copied':False,'source_excerpts_reused_from_preparation':True}
static=load(E/'pre-artifact-static.json');assert len(static['commands'])==3 and all(r['returncode']==0 for r in static['commands'])
baseline=json.loads(static['commands'][1]['stdout']);assert baseline['status']=='pass' and baseline['checks']['baseline']==19
scan=load(E/'pre-artifact-secret-scan.json');assert len(scan['files'])==101
priorcompare=load(E/'preparation-review/comparison.json','c31bc7869eae3aadca0828f66f10289b980772751e9d325a62fc6c4ab4e31d02')
inherited=0;current=0
for name,sha in scan['files'].items():
    p=ROOT/name
    if str(p) not in watched and priorcompare['watched_text_sha256'].get(str(p))==sha:inherited+=1
    else:raw(p,sha);current+=1
raw(scan['script'],scan['script_sha256']);assert scan['script_sha256']=='495cc0f4c804275709c62f26862a7c56642951488d72cd71e11a5af5b6594a0c'
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[] and len(scan['dispositions'])==6
for row in scan['dispositions']:
    p=pathlib.Path(row['path'])
    if p==E/'pre-review-secret-scan.json':assert row['sha256']=='da95e78d17e06cf3939875391ad6a64e79a6c03e6e3aa53525d848fa8898852e'
    else:assert row['sha256']==(c['inputs'][str(p.relative_to(ROOT))] if p.is_relative_to(ROOT) else c['source_inputs'][str(p)])
checks['recorded_static_and_scan']={'static_returncodes':[0,0,0],'baseline_original_hashes':19,'scan_files':101,'current_text_bindings':current,'inherited_preparation_bindings_reused':inherited,'raw_returncode':1,'digest_false_positive_occurrences':6,'transformed_returncode':0,'complete_token_files':[],'scanner_and_baseline_replayed':False,'historical_digest_sources_rehashed':False}
identity=[]
for args,expected in [(['--show-toplevel'],str(ROOT)),(['--verify','HEAD'],candidate['head']),(['--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
    p=subprocess.run(['/usr/bin/git','-C',str(ROOT),'rev-parse',*args],capture_output=True,text=True,timeout=5)
    assert p.returncode==0 and p.stdout.strip()==expected;identity.append({'argv':p.args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
p=subprocess.run(['/usr/bin/git','-C',str(ROOT),'symbolic-ref','--short','HEAD'],capture_output=True,text=True,timeout=5)
assert p.returncode==0 and p.stdout.strip()=='codex/marketplace-native-onboarding';identity.append({'argv':p.args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
checks['git_identity']=identity
for path,sha in watched.items():
    if path!=str(crash_path):assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==sha,('text changed during review',path)
# Exactly one hash pass over the three explicitly authorized artifacts. No tool execution.
assert len(inventory['artifacts'])==3
expected_artifacts={'tsan-object':q['cells']['tsan']['artifacts']['object'],'tsan-binary':q['cells']['tsan']['artifacts']['binary'],'installed-tsan':{'path':tsanpath,'sha256':c['tools'][tsanpath]}}
assert {row['kind'] for row in inventory['artifacts']}==set(expected_artifacts)
observed=[]
def key(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def macho(data):
    magic,cpu,subtype,filetype,ncmds,sizeofcmds,flags,reserved=struct.unpack_from('<8I',data)
    assert magic==0xfeedfacf and cpu==0x0100000c and 32+sizeofcmds<=len(data)
    pos=32;uuids=[]
    for _ in range(ncmds):
        cmd,size=struct.unpack_from('<2I',data,pos);assert size>=8 and pos+size<=32+sizeofcmds
        if cmd==0x1b:assert size==24;uuids.append(str(uuid.UUID(bytes=data[pos+8:pos+24])))
        pos+=size
    assert pos==32+sizeofcmds
    return {'cpu':'arm64','file_type':filetype,'uuids':uuids}
for row in inventory['artifacts']:
    assert {k:row[k] for k in ['path','sha256']}==expected_artifacts[row['kind']]
    path=pathlib.Path(row['path']);before=path.lstat()
    assert path.resolve()==path and stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_nlink==1 and before.st_size==row['bytes']
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        assert key(os.fstat(fd))==key(before)
        with os.fdopen(fd,'rb',closefd=False) as stream:data=stream.read()
        assert key(os.fstat(fd))==key(before)
    finally:os.close(fd)
    assert key(path.lstat())==key(before) and hashlib.sha256(data).hexdigest()==row['sha256']
    identity=macho(data)
    if row['kind']=='tsan-object':assert identity['file_type']==1
    elif row['kind']=='tsan-binary':assert identity['file_type']==2 and identity['uuids']==[diagnosis['binary_uuid']]
    else:assert identity['file_type']==6 and identity['uuids']==[owned_images['libclang_rt.tsan_osx_dynamic.dylib']['uuid']] and oct(stat.S_IMODE(before.st_mode))=='0o755'
    observed.append({**row,'mode':oct(stat.S_IMODE(before.st_mode)),'links':1,'canonical':True,'regular':True,'hash_passes':1,'macho':identity})
checks['artifacts']={'count':3,'total_bytes':sum(row['bytes'] for row in observed),'identities':observed,'compiler_or_full_prefix_hashed':False}
result={'result':'PASS: correctly closed TSan failure','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_sha256':digest(E/'closure-candidate.json'),'helper_sha256':digest(helper),'contract_sha256':digest(E/'contract.json'),'checks':checks,'watched_text_sha256':watched,'not_run':['candidate/helper import or execution','compiler, sanitizer, nm or Ninja','846 source-input traversal or full guards','source tree crawling or additional prefix/tool binary hashes','scanner or baseline replay','capacity or census replay','current PID probes or lease acquisition','services, containers, network or credentials','fresh model sessions','full OCI/Claude acceptance','repair build or effectiveness test']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':result['result'],'snapshots':10,'manifest_rows':71,'direct_copy_pairs':68,'historical_records_bound':3,'private_text_sources':52,'native_commands':18,'post_failure_commands':5,'owned_crash_frames':36,'artifact_hashes':3,'artifact_bytes':checks['artifacts']['total_bytes']}))
