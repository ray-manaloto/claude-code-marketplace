import ast,datetime,hashlib,itertools,json,pathlib,shlex,subprocess
ROOT=pathlib.Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/p2996-tsan'
OUT=pathlib.Path(__file__).parent
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
def nested_function(source,name):
    found=[node for node in ast.walk(ast.parse(source)) if isinstance(node,ast.FunctionDef) and node.name==name]
    assert len(found)==1,name
    return ast.dump(found[0],include_attributes=False)
candidate=load(E/'candidate.json','b7df8d3e159caaa181945fab4dae6206e1016ac315412bb72d9e6c4ecf7d38a8')
c=load(E/'contract.json','4bb345582c7253694e37b958c77154b5d98ac522e3e89858eac2fb2c2b828ea5')
assert candidate['contract_sha256']==watched[str(E/'contract.json')]
assert candidate['head']==c['base_head']=='757a72bd22d774d8533b8f831c8ee604ce0109b8'
snap=load(E/'candidate-inputs.json','1b3e9663e0f3c38cafaa4efd62e32e48eca37941022f111191c7e90b41fdad99')
assert len(snap['files'])==9
for row in snap['files']:assert raw(row['source'],row['sha256'],row['bytes'])==row['text'].encode()
allowed={'dev/toolchains/p2996_tsan.py','dev/toolchains/tsan_witness.cpp','docs/sanitizers.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md'}
assert set(candidate['files'])==allowed
for name,sha in candidate['files'].items():assert watched[str(ROOT/name)]==sha
helper=cache[str(ROOT/'dev/toolchains/p2996_tsan.py')].decode();fixture=cache[str(ROOT/'dev/toolchains/tsan_witness.cpp')].decode()
assert len(helper.splitlines())==207 and len(fixture.splitlines())==44
assert candidate['files']['dev/toolchains/p2996_tsan.py']=='529c032a98b31963e2ee218dfe81eb2a250924f7ef984376fc026b30f38683d1'
assert 'CONTRACT_SHA = "'+candidate['contract_sha256']+'"' in helper
checks['candidate']={'exact_snapshots':9,'maintained_files':candidate['files'],'helper_lines':207,'fixture_lines':44}
derivation=load(E/'contract-derivation.json','162cbbda5858d106668e7b35fd774f863887555862215c25ae1cf225ce77aed5')
assert derivation['base_contract']=='evidence/p2996-asan-promotion/contract.json'
old=load(ROOT/derivation['base_contract'],derivation['base_sha256'])
assert derivation['base_sha256']=='982b75c01ceb6daaf87242c54880b74da5c2a12bfc380543ce207f266f5d85d8'
removed={'repair','target','before','after','replacement','replacement_identity','witnesses'}
changed={'base_head','scope','inputs','tools','source_inputs','runtime_environment','runtime_unset','sanitizers'}
assert set(old)-set(c)==removed and set(c)-set(old)==set()
assert set(derivation['removed_fields'])==removed
for key in set(c)-changed:assert c[key]==old[key],key
assert len(old['inputs'])==163 and len(c['inputs'])==derivation['input_count']==172
assert all(c['inputs'][p]==sha for p,sha in old['inputs'].items())
newinputs={p:sha for p,sha in c['inputs'].items() if p not in old['inputs']}
assert set(newinputs)==set(derivation['extra_project_inputs']) and len(newinputs)==9
for p,sha in newinputs.items():raw(ROOT/p,sha)
assert len(old['source_inputs'])==derivation['retained_source_input_count']==841
assert len(c['source_inputs'])==derivation['source_input_count']==846
assert all(c['source_inputs'][p]==sha for p,sha in old['source_inputs'].items())
addedsources={p:sha for p,sha in c['source_inputs'].items() if p not in old['source_inputs']}
expectednew={'CMakeLists.txt','tsan_flags.cpp','tsan_report.cpp','tsan_rtl_report.cpp','tsan_platform_mac.cpp'}
assert len(addedsources)==5 and {pathlib.Path(p).name for p in addedsources}==expectednew
for p,sha in addedsources.items():raw(p,sha)
prereq=load(E/'source-prerequisite.json',c['inputs']['evidence/p2996-tsan/source-prerequisite.json'])
assert prereq['source_commit']==c['source_provenance']['head'] and prereq['source_tree']==c['source_provenance']['tree']
assert len(prereq['references'])==9 and len({r['path'] for r in prereq['references']})==8
assert derivation['source_additions']==[r['path'] for r in prereq['references']]
excerpt_results=[]
for row in prereq['references']:
    p=pathlib.Path(row['path']);assert p.is_relative_to(pathlib.Path(c['source_provenance']['path']))
    assert c['source_inputs'][str(p)]==row['sha256']
    if str(p) in cache:
        actual=''.join(cache[str(p)].decode().splitlines(keepends=True)[row['first_line']-1:row['last_line']]);kind='new small source hash and excerpt'
    else:
        # Read only the requested ranges in three inherited source files; no full-file rehash.
        with p.open() as stream:actual=''.join(itertools.islice(stream,row['first_line']-1,row['last_line']))
        kind='current excerpt with inherited full-file digest'
    assert actual==row['text'],(str(p),row['first_line'])
    excerpt_results.append({'path':str(p),'first_line':row['first_line'],'last_line':row['last_line'],'claim':row['claim'],'verification':kind,'excerpt_sha256':hashlib.sha256(actual.encode()).hexdigest()})
assert 'case ReportTypeRace:\n      return "data race";' in cache[next(p for p in addedsources if p.endswith('/tsan_report.cpp'))].decode()
assert prereq['runtime_environment']==c['runtime_environment']=={'TSAN_OPTIONS':'exitcode=86:abort_on_error=0:symbolize=0:halt_on_error=1','UBSAN_OPTIONS':'exitcode=86:abort_on_error=0:symbolize=0:halt_on_error=1'}
assert c['runtime_unset']==['ASAN_OPTIONS','LSAN_OPTIONS','TSAN_OPTIONS','UBSAN_OPTIONS','ASAN_SYMBOLIZER_PATH','TSAN_SYMBOLIZER_PATH','UBSAN_SYMBOLIZER_PATH']
runtime=prereq['runtime'];tsanpath=runtime['path'];asanpath=old['target']
expectedtools=old['tools']|{asanpath:old['after']['sha256'],tsanpath:runtime['sha256']}
assert c['tools']==expectedtools and len(c['tools'])==28
assert derivation['tool_changes']=={asanpath:{'before':old['before']['sha256'],'after':old['after']['sha256']},tsanpath:{'added':runtime['sha256']}}
original_inventory_path='evidence/p2996-install/independent-installation/post-install-inventory.json'
original=load(ROOT/original_inventory_path,c['inputs'][original_inventory_path])
entries=[]
def search_entries(value):
    if isinstance(value,dict):
        if value.get('path')==tsanpath and 'sha256' in value:entries.append(value)
        for item in value.values():search_entries(item)
    elif isinstance(value,list):
        for item in value:search_entries(item)
search_entries(original)
assert len(entries)==1
assert {k:entries[0][k] for k in ['path','sha256','bytes','mode']}==runtime
priorreview=load(ROOT/'evidence/p2996-asan-promotion/artifact-review.json','1b327c1afe3be795009c4b233fa958bec39705806b801e1f0cea91861c265121')
assert priorreview['result'].startswith('PASS') and priorreview['findings']==[]
assert priorreview['contract_sha256']==derivation['base_sha256']
assert priorreview['helper_sha256']==c['inputs']['dev/toolchains/p2996_asan_promote.py']
priorinv=load(ROOT/'evidence/p2996-asan-promotion/artifact-inventory.json',priorreview['artifact_inventory_sha256'])
installed=[r for r in priorinv['artifacts'] if r['kind']=='installed-runtime'];assert len(installed)==1
assert installed[0]['path']==asanpath and installed[0]['sha256']==c['tools'][asanpath]
checks['contract_derivation']={'retained_project_inputs':163,'new_project_inputs':newinputs,'retained_source_inputs':841,'new_small_source_files':addedsources,'new_small_source_bytes':sum(len(cache[p]) for p in addedsources),'total_source_inputs':846,'tools':28,'tool_changes':derivation['tool_changes'],'removed_promotion_only_fields':sorted(removed),'source_excerpts':excerpt_results,'tsan_matches_original_text_inventory':True,'installed_binaries_hashed':0}
launchers=load(E/'prepared-launchers.json','b4be6794bc6bf6be2ae1954654dfefdcd3ad88c304cff9ed80da64cd101c69a3')
assert launchers['state']=='Prepared, not executed' and len(launchers['files'])==2
for row in launchers['files']:
    assert pathlib.Path(row['copy']).parent==E
    assert raw(row['path'],row['sha256'])==raw(row['copy'],row['sha256'])
    ast.parse(cache[row['copy']].decode())
checks['prepared_launchers']={'copy_pairs':2,'files':launchers['files'],'executed':False}
accepted=raw(ROOT/'dev/toolchains/p2996_sanitizers.py',c['inputs']['dev/toolchains/p2996_sanitizers.py']).decode()
promotion=raw(ROOT/'dev/toolchains/p2996_asan_promote.py',c['inputs']['dev/toolchains/p2996_asan_promote.py']).decode()
for name in ['save','guard','run','interrupted']:assert nested_function(helper,name)==nested_function(accepted,name),name
assert nested_function(helper,'source_state')==nested_function(promotion,'source_state')
imports=[node for node in ast.parse(helper).body if isinstance(node,ast.ImportFrom)]
assert any(node.module=='p2996_asan_runtime' and [x.name for x in node.names]==['protected'] for node in imports)
assert any(node.module=='p2996_sanitizers' and [x.name for x in node.names]==['admit_editors'] for node in imports)
assert c['inputs']['dev/toolchains/p2996_asan_runtime.py']=='ff283bc8542f2faa36e0aa5f7754c983c6735905a12bc16e535741aa2056d7aa'
assert c['jobs_per_build']==1
base=load(ROOT/c['baseline_qualification'],c['inputs'][c['baseline_qualification']])['cells']['p2996-core-static-fmt-static']['cache']
assert '-freflection' not in shlex.split(base['CMAKE_CXX_FLAGS'])
assert '--no-default-config' in shlex.split(base['CMAKE_CXX_FLAGS'])
assert set(c['sanitizers'])=={'tsan','tsan-ubsan'}
expectedruns={}
for mode,settings in c['sanitizers'].items():
    assert settings['flags']==(['-fsanitize=thread'] if mode=='tsan' else ['-fsanitize=thread,undefined'])
    assert settings['runtimes']==['lib/clang/21/lib/darwin/libclang_rt.tsan_osx_dynamic.dylib']
    assert c['prefixes']['p2996']+'/'+settings['runtimes'][0]==tsanpath
    expectederrors={'race':['WARNING: ThreadSanitizer: data race']}
    if mode=='tsan-ubsan':expectederrors['overflow']=['runtime error: signed integer overflow: 2147483647 + 1 cannot be represented']
    assert settings['errors']==expectederrors
    expectedruns[mode]={'clean':0,**{name:86 for name in expectederrors}}
assert sum(len(v) for v in expectedruns.values())==5
checks['static_source_assertions']={'inherited_functions_equal':['save','guard','run','interrupted'],'source_state_equal_to_promotion_runner':True,'protected_import':'p2996_asan_runtime.protected','editor_import':'p2996_sanitizers.admit_editors','one_job':1,'public_compile_baseline_has_no_reflection_flag':True,'expected_cases':expectedruns,'candidate_code_imported_or_executed':False}
post=load(E/'promotion-postcommit.json',c['inputs']['evidence/p2996-tsan/promotion-postcommit.json'])
assert post['head']==candidate['head'] and post['clean'] is True and post['review_sha256']==watched[str(ROOT/'evidence/p2996-asan-promotion/artifact-review.json')]
assert len(post['commands'])==14 and all(r['returncode']==0 for r in post['commands'])
assert post['commands'][-1]['argv']==['/usr/bin/git','status','--short'] and post['commands'][-1]['stdout']==''
static=load(E/'pre-review-static.json','976a8c81be2a282b26d9d130ee1f0da833702dcdc6fc38024e567f35a24a4b61')
assert len(static['commands'])==3 and all(r['returncode']==0 for r in static['commands'])
baseline=json.loads(static['commands'][1]['stdout']);assert baseline['status']=='pass' and baseline['checks']['baseline']==19
scan=load(E/'pre-review-secret-scan.json','da95e78d17e06cf3939875391ad6a64e79a6c03e6e3aa53525d848fa8898852e')
assert len(scan['files'])==15
for p,digest in scan['files'].items():raw(ROOT/p,digest)
raw(scan['script'],scan['script_sha256'])
assert scan['script_sha256']=='baa3a4022aced9fea09f1d5d5930ca531a61b4770fd4300ad406f6d4d0f98eda'
assert scan['raw']['returncode']==1 and scan['transformed']['returncode']==0 and scan['supplemental_complete_token_files']==[]
assert len(scan['dispositions'])==4
for row in scan['dispositions']:
    p=pathlib.Path(row['path'])
    assert row['reason']=='Verified exact file-content digest'
    known=c['inputs'][str(p.relative_to(ROOT))] if p.is_relative_to(ROOT) else c['source_inputs'][str(p)]
    assert row['sha256']==known
checks['recorded_checks']={'previous_closure_commands':14,'previous_closure_returncodes':[0]*14,'current_static_returncodes':[0,0,0],'acceptance_baseline_original_hashes':19,'scan_files':15,'raw_returncode':1,'digest_false_positives':4,'transformed_returncode':0,'complete_token_files':[],'static_and_scanner_replayed':False,'historical_false_positive_source_files_rehashed':False}
identity=[]
for args,expected in [(['--show-toplevel'],str(ROOT)),(['--verify','HEAD'],candidate['head']),(['--path-format=absolute','--git-common-dir'],'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')]:
    p=subprocess.run(['/usr/bin/git','-C',str(ROOT),'rev-parse',*args],capture_output=True,text=True,timeout=5)
    assert p.returncode==0 and p.stdout.strip()==expected;identity.append({'argv':p.args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
p=subprocess.run(['/usr/bin/git','-C',str(ROOT),'symbolic-ref','--short','HEAD'],capture_output=True,text=True,timeout=5)
assert p.returncode==0 and p.stdout.strip()=='codex/marketplace-native-onboarding';identity.append({'argv':p.args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
checks['git_identity']=identity
for path,digest in watched.items():assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==digest,('text changed during review',path)
result={'result':'PASS','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_sha256':watched[str(E/'candidate.json')],'helper_sha256':candidate['files']['dev/toolchains/p2996_tsan.py'],'contract_sha256':watched[str(E/'contract.json')],'checks':checks,'watched_text_sha256':watched,'not_run':['candidate execution or import','compiler or sanitizer runtime','capacity or dispatch execution','full guards or 846-source traversal','installed runtime or other binary hashes','lease acquisition or process/service/container probes','network or global changes','source/build/prefix writes','scanner or baseline replay','fresh model session','full OCI/Claude acceptance','dependency instrumentation, coverage or matrix execution']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':'PASS','snapshots':9,'prepared_copy_pairs':2,'new_source_hashes':5,'source_excerpts':9,'retained_source_bindings':841,'new_project_inputs':9,'recorded_static_returncodes':[0,0,0],'native_commands_executed':0}))
