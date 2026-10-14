import datetime,hashlib,json,os,pathlib,stat,subprocess
ROOT=pathlib.Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-asan-promotion'
OUT=pathlib.Path(__file__).parent
watched={};cache={};checks={}
def raw(path,sha=None,size=None):
    p=pathlib.Path(path)
    if str(p) in cache:b=cache[str(p)]
    else:
        assert p.stat().st_size<1000000,('outside text bound',str(p))
        b=p.read_bytes();b.decode('utf-8');cache[str(p)]=b;watched[str(p)]=hashlib.sha256(b).hexdigest()
    if sha is not None:assert watched[str(p)]==sha,(str(p),watched[str(p)],sha)
    if size is not None:assert len(b)==size,(str(p),len(b),size)
    return b
def load(path,sha=None):return json.loads(raw(path,sha))
def sha(path):return watched[str(path)]
def dt(s):return datetime.datetime.fromisoformat(s)
candidate=load(E/'closure-candidate.json','81654167954cde148e5ecea54c5222156257550a409a53c95ec34b69ae122e52')
contract=load(E/'contract.json','88b922a84e58f2f9f4aed492aa643c95fd3ed2b460a95b26286e5063a07a094c')
prepared=load(E/'candidate.json',candidate['prepared_candidate_sha256'])
previous=load(E/'pre-run-review.json',candidate['preparation_review_sha256'])
assert previous['findings']==[] and previous['result'].startswith('PASS')
assert previous['candidate_sha256']==sha(E/'candidate.json')
assert previous['contract_sha256']==sha(E/'contract.json')
assert len(contract['source_inputs'])==841 and len(contract['tools'])==27
snap=load(E/'closure-inputs.json','21225389ec0dad46eaf242f5ccf8fac3055ec7763849889ba8eadc077952dac0')
assert len(snap['files'])==8
for row in snap['files']:assert raw(row['source'],row['sha256'],row['bytes'])==row['text'].encode()
assert len(candidate['files'])==4
for name,digest in candidate['files'].items():assert sha(ROOT/name)==digest
helper=ROOT/'dev/toolchains/p2996_asan_promote.py'
assert sha(helper)==previous['helper_sha256']==prepared['files']['dev/toolchains/p2996_asan_promote.py']=='88610fe87f9629504f16b66a39d4af755a5a2efa239eacce9ea8adece3f3ea0c'
assert candidate['head']==prepared['head']==contract['base_head']=='5a4062e17089ad2fe2b160fea998dc7954aa5766'
checks['candidate']={'snapshots':8,'maintained_files':candidate['files'],'helper_and_contract_unchanged_since_preparation':True,'retained_source_inputs':841,'retained_tools':27}
for manifest_name,count in [('operation/copy-manifest.json',9),('capacity-copy-manifest.json',17),('preparation-review-copy-manifest.json',6)]:
    manifest=load(E/manifest_name);assert len(manifest['files'])==count
    for row in manifest['files']:
        assert pathlib.Path(row['destination']).is_relative_to(E)
        assert raw(row['source'],row['sha256'])==raw(row['destination'],row['sha256'])
    checks[manifest_name]={'pairs':count,'all_bytes_equal':True}
q=load(E/'operation/qualification.json',candidate['qualification_sha256'])
closure=load(E/'operation/closure.json',candidate['closure_sha256'])
inventory=load(E/'artifact-inventory.json',candidate['artifact_inventory_sha256'])
texts=load(E/'operation/text-receipts.json',closure['text_receipts_sha256'])
assert len(texts['files'])==closure['retained_text_files']==59
textmap={row['source']:row for row in texts['files']};assert len(textmap)==59
for row in texts['files']:assert raw(row['source'],row['sha256'],row['bytes'])==row['text'].encode()
admission=load(E/'admission.json')
launch=load(E/'native-launch.json')
native=load(E/'native-execution.json',closure['native_execution_sha256'])
OP=pathlib.Path(admission['run_directory']);LP=pathlib.Path(native['private_launch_directory'])
assert q['helper_sha256']==native['helper_sha256']==launch['helper_sha256']==admission['helper_sha256']==sha(helper)
assert q['admission_sha256']==native['admission_sha256']==launch['admission_sha256']==sha(E/'admission.json')
assert admission['base_head']==candidate['head'] and admission['review_sha256']==sha(E/'pre-run-review.json')
assert admission['candidate_sha256']==sha(E/'candidate.json') and admission['contract_sha256']==sha(E/'contract.json')
assert admission['installed_write_allowlist']==[contract['target']]
assert native['argv']==launch['argv'] and native['argv'][1:4]==['-E','-B',str(helper)]
assert native['argv'][4:]==['--run-dir',str(OP),'--promote']
assert native['returncode']==closure['native_returncode']==0
assert q['state']=='PASS: installed ASan promotion and seven sanitizer witnesses'
assert closure['state']=='CLOSED PASS: one installed ASan promotion and seven sanitizer witnesses'
assert all(q[k] is True for k in ['mutation_started','lease_released','protected_state_matches_expected'])
assert not any(k in q for k in ['error','preservation_error','recovery_error','recovered'])
assert raw(LP/'launch.json')==raw(E/'native-launch.json') and raw(LP/'execution.json')==raw(E/'native-execution.json')
assert raw(LP/'stderr',native['stderr_sha256'])==b''
native_stdout=raw(LP/'stdout',native['stdout_sha256']).decode()
assert json.loads(native_stdout.splitlines()[-1])=={'state':q['state'],'receipt':str(OP/'qualification.json')}
assert raw(OP/'qualification.json')==raw(E/'operation/qualification.json')
assert native['dispatch_sha256']==launch['dispatch_sha256']=='3f5013d245039623d9b6543f437574fb28a2ba8456ad90aafb89f3e8f1ceeade'
raw(E/'dispatch.py.source',native['dispatch_sha256'])
commands=q['commands'];assert len(commands)==26
cases={row['case']:row for row in commands};assert len(cases)==26
expected_order=['project-head','default-before','capacity-processes','editor-identities','editor-cwd','editor-identities-after','docker-context','docker-census','docker-stats','source-before-head','source-before-tree','source-before-diff','source-before-status','promote','asan-clean','asan-memory','ubsan-clean','ubsan-overflow','asan-ubsan-clean','asan-ubsan-memory','asan-ubsan-overflow','source-after-head','source-after-tree','source-after-diff','source-after-status','default-after']
assert list(cases)==expected_order
intentional={'asan-memory','ubsan-overflow','asan-ubsan-memory','asan-ubsan-overflow'}
for row in commands:
    expected=86 if row['case'] in intentional else 0
    assert row['returncode']==row['expected_returncode']==expected
    assert 0<=row['elapsed_seconds']<row['timeout_seconds']
    assert dt(native['started_at'])<=dt(row['started_at'])<dt(native['finished_at'])
    assert len(row['logs'])==2
    for suffix,log in zip(['.stdout','.stderr'],row['logs']):
        assert log['path']==str(OP/(row['case']+suffix))
        assert textmap[log['path']]['sha256']==log['sha256'];raw(log['path'],log['sha256'])
def logtext(label,kind='stdout'):return cache[str(OP/(label+'.'+kind))].decode()
assert logtext('project-head').strip()==candidate['head']
for name in ['head','tree','diff','status']:assert logtext('source-before-'+name)==logtext('source-after-'+name)
sp=contract['source_provenance']
assert logtext('source-before-head').strip()==sp['head'] and logtext('source-before-tree').strip()==sp['tree']
assert sha(OP/'source-before-diff.stdout')==sp['diff_sha256']
assert sha(OP/'source-before-status.stdout')==contract['inputs'][sp['status']]
assert logtext('default-before')==logtext('default-after') and sha(OP/'default-before.stdout')==contract['inputs'][contract['default_profile']]
assert 'DYLD_LIBRARY_PATH' not in logtext('default-after')
for label in ['before','after']:
    for kind,args in [('head',['rev-parse','HEAD']),('tree',['rev-parse','HEAD^{tree}']),('diff',['diff','--binary','HEAD']),('status',['status','--porcelain','--untracked-files=all'])]:
        argv=cases['source-'+label+'-'+kind]['argv']
        assert argv[:5]==['/usr/bin/git','-c','core.fsmonitor=false','-C',sp['path']]
        assert argv[5:]==args
for name,extra in [('private',''),('mutation',' (literal '+json.dumps(contract['target'])+')')]:
    expected='(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath '+json.dumps(str(OP))+') (literal "/dev/null")'+extra+')\n(deny network*)\n'
    assert raw(OP/(name+'.sb'),q['confinement'][name]).decode()==expected
promote=cases['promote']['argv']
assert promote[:3]==['/usr/bin/sandbox-exec','-f',str(OP/'mutation.sb')]
assert promote[4:7]==['-E','-B','-c'] and promote[8]==str(ROOT/'dev/toolchains')
assert pathlib.Path(promote[9]).is_relative_to(OP) and promote[10]==contract['target']
assert json.loads(promote[11])==contract['before'] and json.loads(promote[12])==contract['after']
assert logtext('promote')==logtext('promote','stderr')==''
assert q['backup']=={'path':str(OP/'original.dylib'),**contract['before']}
assert q['installed_identity']==closure['installed_identity']==contract['after']
witness_checks=[]
launcher="import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"
prefix=contract['prefixes']['p2996']
for mode,spec in contract['sanitizers'].items():
    cell=q['cells'][mode];assert cell['binary']==contract['witnesses'][mode]
    expected_runs={'clean':0,**{key:86 for key in spec['errors']}}
    assert set(cell['runs'])==set(expected_runs)
    for name,rc in expected_runs.items():
        label=mode+'-'+name;row=cases[label];argv=row['argv']
        assert argv==['/usr/bin/sandbox-exec','-f',str(OP/'private.sb'),native['argv'][0],'-E','-B','-c',launcher,cell['binary']['path'],name,json.dumps(contract['runtime_environment'])]
        assert row['timeout_seconds']==20 and logtext(label)=='reflection value=43, members=1\n'
        trace=logtext(label,'stderr')
        loaded={line[line.index('/'): ] for line in trace.splitlines() if line.startswith('dyld[') and '/' in line}
        assert sorted(loaded)==cell['runs'][name]['loaded']
        wanted={prefix+'/'+name for name in spec['runtimes']}
        assert {p for p in loaded if pathlib.PurePosixPath(p).name.startswith('libclang_rt.')}==wanted
        libs={prefix+'/lib/'+lib for lib in ['libc++.1.0.dylib','libc++abi.1.0.dylib','libunwind.1.0.dylib']}
        assert libs<=loaded
        tokens=spec['errors'].get(name,[])
        assert all(token in trace for token in tokens)
        if rc==0:assert not any(token in trace for token in ['ERROR: AddressSanitizer','runtime error:','Sanitizer CHECK failed'])
        assert cell['runs'][name]['expected_returncode']==rc
        witness_checks.append({'case':label,'returncode':rc,'timeout_seconds':20,'elapsed_seconds':row['elapsed_seconds'],'reflection_stdout_exact':True,'diagnostic_tokens':tokens,'installed_runtimes':sorted(wanted),'required_standard_libraries':sorted(libs)})
assert len(witness_checks)==7
assert closure['command_count']==26 and closure['command_outcomes']==[{'case':r['case'],'returncode':r['returncode']} for r in commands]
assert closure['processes']==[{'case':'native-helper','pid':native['pid'],'absent':True}]+[{'case':r['case'],'pid':r['pid'],'absent':True} for r in commands]
assert closure['lease_probe']=={'free':True,'contents_unchanged':True}
assert closure['protected_state_matches_expected'] is closure['source_and_default_outputs_match'] is True
collectexec=load(E/'operation/collection-execution.json');assert collectexec['returncode']==0 and collectexec['stderr']==''
raw(collectexec['argv'][3],collectexec['script_sha256'])
assert dt(native['finished_at'])<dt(collectexec['started_at'])<dt(closure['recorded_at'])<dt(collectexec['finished_at'])
assert inventory['qualification_sha256']==closure['qualification_sha256']==sha(E/'operation/qualification.json')
checks['native']={'recorded_returncode':0,'recorded_elapsed_seconds':native['elapsed_seconds'],'command_count':26,'log_bindings':52,'copied_text_sources':59,'no_rollback_reported':True,'source_and_default_preserved':True,'witnesses':witness_checks,'closure_pids_recorded_absent':27,'lease_recorded_free_unchanged':True,'closure_collector_returncode':0,'closure_collector_elapsed_seconds':collectexec['elapsed_seconds']}
cap=load(E/'capacity/capacity.json',admission['capacity_sha256']);capexec=load(E/'capacity/execution.json',admission['capacity_execution_sha256'])
assert cap['state']=='PASS' and capexec['returncode']==0 and capexec['stderr']==''
assert cap['held_lease'] is cap['native_operation_started'] is False
assert cap['script_sha256']==capexec['script_sha256']=='579cb651e4a0b138101a1b1ad87b18198ec49a31a06f455235d2e3b6245328af'
raw(capexec['argv'][3],cap['script_sha256'])
assert dt(capexec['finished_at'])<dt(admission['recorded_at'])<dt(native['started_at'])
assert cap['docker_context']==admission['docker_context'] and cap['containers']==admission['containers']
assert len(cap['commands'])==7
for row in cap['commands']:
    assert row['returncode']==0 and row['elapsed_seconds']<row['timeout_seconds']
    for log in row['logs']:raw(log['path'],log['sha256'])
for recorded in [cap,q['capacity']]:
    assert recorded['free_bytes']>=contract['disk_reserve_bytes'] and recorded['load'][0]<=2*recorded['cpus']
    assert recorded['total_cpu_percent']<=75*recorded['cpus'] and recorded['container_cpu_percent']<=50*recorded['cpus']
    assert recorded['admitted_editor_services']==['73356','73398']
for name in ['before','after']:
    census=q['writer_census_'+name];assert census['lock_holder_check_rc']==1 and census['lock_holders']==[]
    assert {p['known_task'] for p in census['processes']}=={'mcp:tr','mcp:graphify','mcp:cbm'}
assert q['writer_census_before']['processes']==q['writer_census_after']['processes']
assert logtext('editor-identities')==logtext('editor-identities-after')
assert logtext('docker-context').strip()==admission['docker_context']
assert logtext('docker-census').splitlines()==admission['containers']
checks['capacity_and_admission']={'capacity_returncode':0,'elapsed_seconds':capexec['elapsed_seconds'],'commands':7,'admission_after_capacity_before_launch':True,'under_lease_capacity_within_recorded_limits':True,'census_unchanged':True,'exclusive_writer_guarantee':False}
static=load(E/'pre-artifact-static.json');assert len(static['commands'])==3 and all(row['returncode']==0 for row in static['commands'])
baseline=json.loads(static['commands'][1]['stdout']);assert baseline['status']=='pass' and baseline['checks']['baseline']==19
scan=load(E/'pre-artifact-secret-scan.json');assert len(scan['files'])==94
priorcomparison=load(E/'preparation-review/comparison.json','66d7b82e3d6f7a49eeb22bdd9751151ded3cd1954ad6eb1fd56769f3416ed201')
inherited=0;current=0
for name,digest in scan['files'].items():
    p=ROOT/name
    if str(p) not in watched and priorcomparison['watched_text_sha256'].get(str(p))==digest:inherited+=1
    else:raw(p,digest);current+=1
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and len(scan['dispositions'])==5 and scan['supplemental_complete_token_files']==[]
raw(scan['script'],scan['script_sha256'])
assert scan['dispositions'][0]['sha256']==sha(E/'pre-review-secret-scan.json')
for row in scan['dispositions'][1:]:
    rel=str(pathlib.Path(row['path']).relative_to(ROOT)) if pathlib.Path(row['path']).is_relative_to(ROOT) else None
    assert row['sha256']==(contract['inputs'][rel] if rel else contract['source_inputs'][row['path']])
checks['recorded_static_and_scan']={'static_returncodes':[0,0,0],'baseline_original_hashes':19,'baseline_not_rerun':True,'scan_files':94,'current_small_text_bindings':current,'unchanged_prior_review_bindings_reused':inherited,'raw_returncode':1,'digest_false_positives':5,'transformed_returncode':0,'complete_token_files':[],'scanner_not_rerun':True}
identity=[]
for args,expected in [(['--show-toplevel'],str(ROOT)),(['--verify','HEAD'],candidate['head']),(['--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
    p=subprocess.run(['/usr/bin/git','-C',str(ROOT),'rev-parse',*args],capture_output=True,text=True,timeout=5)
    assert p.returncode==0 and p.stdout.strip()==expected;identity.append({'argv':p.args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
p=subprocess.run(['/usr/bin/git','-C',str(ROOT),'symbolic-ref','--short','HEAD'],capture_output=True,text=True,timeout=5)
assert p.returncode==0 and p.stdout.strip()=='codex/marketplace-native-onboarding';identity.append({'argv':p.args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
checks['git_identity']=identity
for path,expected in watched.items():assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==expected,('text drift',path)
# Only the six explicitly admitted artifacts are opened; each is hashed once.
artifacts=inventory['artifacts'];assert len(artifacts)==6 and len({x['path'] for x in artifacts})==6
bykind={x['kind']:x for x in artifacts}
for kind,path,expected in [('installed-runtime',contract['target'],contract['after']),('original-backup',str(OP/'original.dylib'),contract['before']),('qualified-private-runtime',contract['replacement'],contract['replacement_identity'])]:
    assert bykind[kind]=={'kind':kind,'path':path,**expected}
for mode,expected in contract['witnesses'].items():
    assert bykind[mode+'-binary']['path']==expected['path'] and bykind[mode+'-binary']['sha256']==expected['sha256']
identities=[]
def file_key(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_mode,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
for row in artifacts:
    p=pathlib.Path(row['path']);before=p.lstat()
    assert p.resolve()==p and stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid()
    assert before.st_size==row['bytes']
    if 'mode' in row:assert oct(stat.S_IMODE(before.st_mode))==row['mode']
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        assert file_key(os.fstat(fd))==file_key(before)
        with os.fdopen(fd,'rb',closefd=False) as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
        assert file_key(os.fstat(fd))==file_key(before)
    finally:os.close(fd)
    assert file_key(p.lstat())==file_key(before) and actual==row['sha256']
    identities.append({**row,'actual_mode':oct(stat.S_IMODE(before.st_mode)),'regular':True,'canonical':True,'links':before.st_nlink,'uid':before.st_uid,'sha256_reads':1})
checks['artifacts']={'count':6,'total_bytes':sum(x['bytes'] for x in identities),'identities':identities,'source_build_or_other_prefix_files_rehashed':False}
result={'result':'PASS','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'closure_candidate_sha256':sha(E/'closure-candidate.json'),'checks':checks,'watched_text_sha256':watched,'not_run':['candidate helper or imported candidate functions','compiler or sanitizer witness execution','capacity or dispatch replay','full guard or 841-source-input rehash','other installed prefix or dependency instrumentation audit','scanner or baseline replay','lease acquisition or current process probes','container or service operations','network access','fresh model sessions','full OCI/Claude acceptance']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':'PASS','candidate_snapshots':8,'copy_pairs':32,'text_sources':59,'command_outcomes':26,'witness_cases':7,'artifact_hashes':6,'artifact_bytes':checks['artifacts']['total_bytes'],'recorded_static_returncodes':[0,0,0]}))
