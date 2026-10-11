from pathlib import Path
from datetime import UTC,datetime
import ast,copy,hashlib,importlib.util,json,os,stat,sys
ROOT=Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E=ROOT/'evidence/mise-runtime';D=Path(__file__).parent
HEAD='eb92a7478186334d31dbfc0c6e0e1da0c6b5abe5'
HELPER=ROOT/'dev/toolchains/mise_runtime.py'
HELPER_SHA='8c22ca727824fa10cd2cf6f7a08b8499c33f0e82245c9d93cd871f1ff26d728f'
CONTRACT_SHA='2a9f8646ae2cc3bd76ddd424eae64c91e0efb4ba6f1eadaeef6c90dbf367b752'
OP_SHA='3f0742db1ce2e6c2b8994cc0c28eab3a2ae0aa3acfd20ec31564cce6745761c8'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(path):return json.loads(Path(path).read_text())
def rec(path):
    p=Path(path);return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def save(name,value):(D/name).write_text(json.dumps(value,indent=2)+'\n')
def bound(row,path=None):
    p=Path(path or row['path']);p=p if p.is_absolute() else ROOT/p
    assert sha(p)==row['sha256'],str(p)
    if 'bytes' in row:assert p.stat().st_size==row['bytes'],str(p)
def identity():
    gd=Path((ROOT/'.git').read_text().strip().removeprefix('gitdir: '));common=(gd/(gd/'commondir').read_text().strip()).resolve()
    assert common==Path('/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')
    assert (gd/'HEAD').read_text()=='ref: refs/heads/codex/marketplace-native-onboarding\n'
    assert (common/'refs/heads/codex/marketplace-native-onboarding').read_text().strip()==HEAD
    return {'checkout':str(ROOT),'branch':'codex/marketplace-native-onboarding','head':HEAD,'common_git_directory':str(common)}
def maintained():
    paths=['dev/toolchains/mise_runtime.py','docs/iwyu-toolchain.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md','.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
    return {p:sha(ROOT/p) for p in paths}
def ast_function(name):return next(n for n in ast.parse(HELPER.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)

def audit():
    r={'state':'RUNNING','started_at':datetime.now(UTC).isoformat(),'controls':[],'native_subprocesses':0}
    save('checks.json',r)
    try:
        r['git_identity']=identity();before=maintained();assert before['dev/toolchains/mise_runtime.py']==HELPER_SHA
        assert sha(E/'contract.json')==CONTRACT_SHA and sha(E/'operation/qualification.json')==OP_SHA
        data=load(E/'contract.json');admission=load(E/'admission.json');q=load(E/'operation/qualification.json');op=Path(admission['run_directory'])
        assert sha(op/'qualification.json')==OP_SHA
        assert admission['base_head']==HEAD and admission['helper_sha256']==HELPER_SHA and admission['contract_sha256']==CONTRACT_SHA
        for path,h in data['inputs'].items():assert sha(ROOT/path)==h,path
        old=load(ROOT/'evidence/p2996-install/independent-installation/post-install-inventory.json')
        previous=data['previous_record'];current=data['current_mise'];indices=[i for i,v in enumerate(old['records']) if v['path']==current['path']]
        assert len(indices)==1 and old['records'][indices[0]]==previous
        old_proposal=load(ROOT/'evidence/iwyu-build/proposal.json')
        assert old_proposal['tools'][current['path']]==previous['sha256']
        assert sha(ROOT/'dev/toolchains/iwyu_build.py')=='79b573e5096602a8bca131b629617cde021fc5beec8fc4b0ec7d60e96ba7c895'
        assert sha(ROOT/'evidence/iwyu-build/operation/qualification.json')=='b82423af01bcb5a6154b02b0086a1d61895c5c36f69cc3fff12dcc2d7eb0fb80'
        scope={'copy':copy};exec(compile(ast.Module(body=[ast_function('overlay')],type_ignores=[]),str(HELPER),'exec'),scope);overlay=scope['overlay']
        def test_overlay(name,change=None,reject=False,reverse=False):
            inv=copy.deepcopy(old);prev=copy.deepcopy(previous);cur=copy.deepcopy(current)
            if reverse:inv['records'].reverse()
            if change:change(inv,prev,cur)
            saved=copy.deepcopy((inv,prev,cur))
            error=None
            try:result=overlay(inv,prev,cur)
            except (AssertionError,KeyError) as caught:error=type(caught).__name__
            assert (inv,prev,cur)==saved,name+' mutated inputs'
            if reject:assert error is not None,name+' unexpectedly accepted'
            else:
                assert error is None,name
                ix=next(i for i,v in enumerate(inv['records']) if v['path']==current['path'])
                expected=copy.deepcopy(inv);expected['records'][ix].update(sha256=cur['sha256'],bytes=cur['bytes'])
                assert result==expected and result is not inv
                assert {k for k in result['records'][ix] if result['records'][ix][k]!=inv['records'][ix][k]}=={'sha256','bytes'}
                result['records'][ix]['categories'].append('review-only-copy-proof')
                assert inv==saved[0],name+' shared nested storage'
            r['controls'].append({'case':name,'result':'PASS','expected_rejection':reject,'exception':error,'inputs_unmodified':True})
        ix=indices[0]
        test_overlay('unique_exact_record_only_two_fields_changed')
        test_overlay('record_order_independent_deep_copy',reverse=True)
        test_overlay('missing_record',lambda inv,p,c:inv['records'].pop(ix),True)
        test_overlay('duplicate_record',lambda inv,p,c:inv['records'].append(copy.deepcopy(p)),True)
        mutations={'sha256':'0'*64,'bytes':previous['bytes']+1,'mode':'0o777','lstat_mode':'0o777','resolved_path':'/unrelated/mise','path':'/unrelated/mise','exists':False,'lexists':False,'symlink_target':'/unrelated/mise'}
        for key,value in mutations.items():test_overlay('historical_record_changed_'+key,lambda inv,p,c,k=key,v=value:inv['records'][ix].__setitem__(k,v),True)
        test_overlay('previous_hash_mismatch',lambda inv,p,c:p.__setitem__('sha256','0'*64),True)
        test_overlay('current_path_mismatch',lambda inv,p,c:c.__setitem__('path','/unrelated/mise'),True)
        test_overlay('only_hash_changed',lambda inv,p,c:c.__setitem__('bytes',p['bytes']),True)
        test_overlay('only_size_changed',lambda inv,p,c:c.__setitem__('sha256',p['sha256']),True)
        test_overlay('neither_identity_field_changed',lambda inv,p,c:c.update(sha256=p['sha256'],bytes=p['bytes']),True)
        def test_contract(name,bad_contract=False,bad_input=False):
            expected={str(E/'contract.json'):CONTRACT_SHA}|{str(ROOT/p):h for p,h in data['inputs'].items()}
            if bad_contract:expected[str(E/'contract.json')]='0'*64
            if bad_input:expected[str(ROOT/next(iter(data['inputs']))) ]='0'*64
            sample=copy.deepcopy(data)
            scope={'ROOT':ROOT,'CONTRACT':E/'contract.json','CONTRACT_SHA':CONTRACT_SHA,'digest':lambda p:expected[str(p)],'load':lambda p:sample}
            exec(compile(ast.Module(body=[ast_function('contract')],type_ignores=[]),str(HELPER),'exec'),scope)
            rejected=False
            try:out=scope['contract']()
            except AssertionError:rejected=True
            assert rejected==(bad_contract or bad_input) and sample==data
            if not rejected:assert out==data
            r['controls'].append({'case':name,'result':'PASS','expected_rejection':bad_contract or bad_input,'inputs_unmodified':True})
        test_contract('hash_bound_contract_acceptance');test_contract('contract_hash_rejection',bad_contract=True);test_contract('referenced_input_hash_rejection',bad_input=True)
        source_by_attempt={'attempt1':E/'initial-helper.py.source','attempt2':E/'initial-helper.py.source','attempt3':E/'attempt3-helper.py.source','operation':HELPER}
        receipts=[];copies=0;native_logs=0
        for label in ('attempt1','attempt2','attempt3','operation'):
            mf=load(E/(label+'-manifest.json'))
            for row in mf['files']:bound(row,ROOT/row['path']);bound(row,row['source'])
            copies+=len(mf['files'])
            qr=load(E/label/'qualification.json');invname='invocation' if label=='operation' else label+'-invocation'
            inv=load(E/invname/'invocation.json');adm=load(E/('admission.json' if label=='operation' else 'admission-'+label+'.json'))
            assert qr['helper_sha256']==sha(source_by_attempt[label])==adm['helper_sha256'] and qr['contract_sha256']==CONTRACT_SHA==adm['contract_sha256']
            assert adm['base_head']==HEAD and inv['argv'][1:]==['-B',str(HELPER),'--run-dir',adm['run_directory']]
            assert qr['protected_state_unchanged'] and qr['current_mise']==current
            for command in qr['commands']:
                for row in command['logs']:bound(row);native_logs+=1
            for row in inv['logs']:bound(row)
            wrapped=[json.loads(line) for line in Path(inv['logs'][0]['path']).read_text().splitlines()]
            assert wrapped[-1]=={'state':qr['state'],'receipt':str(Path(adm['run_directory'])/'qualification.json')}
            assert [v for v in wrapped if 'case' in v]==[{'case':v['case'],'returncode':v['returncode']} for v in qr['commands']]
            expected_codes={'attempt1':[],'attempt2':[0]*5,'attempt3':[0]*9+[1],'operation':[0]*12}[label]
            assert [v['returncode'] for v in qr['commands']]==expected_codes
            assert inv['returncode']==(0 if label=='operation' else 1)
            assert qr['state'].startswith('PASS')==(label=='operation')
            receipts.append({'attempt':label,'qualification':rec(E/label/'qualification.json'),'manifest':rec(E/(label+'-manifest.json')),'helper':rec(source_by_attempt[label]),'wrapper_returncode':inv['returncode'],'native_returncodes':expected_codes,'protected_state_unchanged':True})
        assert copies==70 and native_logs==54
        attempt1=load(E/'attempt1/qualification.json');assert '51754' in attempt1['error'] and "'known_task': None" in attempt1['error']
        stop=load(E/'attempt1-process-disposition.json');assert stop['argv']==['/bin/ps','-p','51754','-o','pid=,ppid=,comm='] and stop['returncode']==1 and stop['stdout']==stop['stderr']==''
        assert (E/'attempt2/default-profile.stdout').read_bytes()==(ROOT/data['profiles']['default']).read_bytes()
        bad_iso=load(E/'attempt2/default-isolation.stdout');assert bad_iso['CPPFLAGS'] is not None and bad_iso['LDFLAGS'] is not None
        assert 'MARKETPLACE_GCC16_PREFIX' in (E/'attempt3/gcc16-profile.stderr').read_text()
        old_ast=ast.parse((E/'initial-helper.py.source').read_text());third_ast=ast.parse((E/'attempt3-helper.py.source').read_text());current_ast=ast.parse(HELPER.read_text())
        for name in ('overlay','contract','protected','function'):
            definitions=[ast.dump(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False) for tree in (old_ast,third_ast,current_ast)]
            assert len(set(definitions))==1,name
        commands={v['case']:v for v in q['commands']};expected_names=['version','architecture','exec-help','default-profile','default-isolation','cpp-build-profile','cpp-build-isolation','p2996-profile','p2996-isolation','gcc16-profile','gcc16-isolation','default-after']
        assert list(commands)==expected_names
        assert (op/'version.stdout').read_text().strip()==current['version'] and (op/'architecture.stdout').read_text().strip()=='arm64'
        assert all(flag in (op/'exec-help.stdout').read_text() for flag in ('--fresh-env','--no-deps'))
        assert commands['version']['argv']==[current['path'],'--version'] and commands['architecture']['argv']==['/usr/bin/lipo','-archs',current['path']]
        assert commands['exec-help']['argv']==[current['path'],'--no-hooks','exec','--help']
        normal=load(ROOT/'evidence/gcc-bootstrap/install-preimages.json')['normal_environment']['argv']
        profiles={}
        isolation_python=load(E/'invocation/invocation.json')['argv'][0]
        for lane,reference in data['profiles'].items():
            raw=(op/(lane+'-profile.stdout')).read_bytes();assert raw==(ROOT/reference).read_bytes()
            profile=json.loads(raw);assert len(profile['selected'])==32 and profile['homebrew_llvm_on_path'] is True
            iso=load(op/(lane+'-isolation.stdout'));expected={key:profile['selected'].get(key) for key in data['isolation_keys']}
            assert iso==expected and set(iso)==set(data['isolation_keys'])
            if lane!='default':assert set(iso.values())=={None}
            prefix=[current['path'],'--no-hooks','-C',str(op/'cwd')]+([] if lane=='default' else ['-E',lane])+['exec','--fresh-env','--no-deps','--']
            assert commands[lane+'-profile']['argv']==prefix+normal[-2:]
            isolation_argv=commands[lane+'-isolation']['argv'];assert isolation_argv[:len(prefix)]==prefix
            assert isolation_argv[len(prefix):len(prefix)+3]==[isolation_python,'-B','-c']
            assert isolation_argv[-len(data['isolation_keys']):]==data['isolation_keys']
            assert isolation_argv[len(prefix)+3]=='import json,os,sys;print(json.dumps({k:os.environ.get(k) for k in sys.argv[1:]}))'
            profiles[lane]={'stdout':rec(op/(lane+'-profile.stdout')),'reference':rec(ROOT/reference),'profile':profile,'isolation':iso}
        assert commands['default-after']['argv']==normal
        assert (op/'default-after.stdout').read_bytes()==(op/'default-profile.stdout').read_bytes()
        assert all((op/(name+'.stderr')).read_bytes()==b'' for name in expected_names)
        assert profiles['default']['profile']['selected']['CPPFLAGS'] is not None and profiles['default']['profile']['selected']['LDFLAGS'] is not None
        assert profiles['cpp-build']['profile']['selected']['MARKETPLACE_CPP_LANE']=='tools-only'
        assert profiles['p2996']['profile']['selected']['MARKETPLACE_P2996_PREFIX']==data['p2996_prefix'] and profiles['p2996']['profile']['selected']['MARKETPLACE_GCC16_PREFIX'] is None
        assert profiles['gcc16']['profile']['selected']['MARKETPLACE_GCC16_PREFIX']=='/opt/homebrew/Cellar/gcc/16.2.0' and profiles['gcc16']['profile']['selected']['MARKETPLACE_P2996_PREFIX'] is None
        for key in ('writer_census_before','writer_census_after'):
            census=q[key];assert census['lock_holder_check_rc']==1 and census['lock_holders']==[]
            assert len(census['processes'])==3 and {v['known_task'] for v in census['processes']}=={'mcp:graphify','mcp:cbm','mcp:lab-results'}
            assert {v['pid'] for v in census['processes']}=={56524,56526,56528}
        assert q['writer_census_before']['processes']==q['writer_census_after']['processes']
        recipe=load(E/'inspector-recipe.json');assert sha(E/'inspector-recipe.json')=='d0215a0ac5f85dcd319da154f9e10077d617b0cf30301221970c29b4aff6d816'
        for row in recipe['input_bindings']:bound(row)
        for row in recipe['parity']['targets']:bound(row)
        gates=load(E/'pre-review-static.json');assert len(gates)==2 and all(v['returncode']==0 for v in gates)
        assert json.loads(gates[1]['stdout'])['checks']['baseline']==19
        for row in load(ROOT/'evidence/onboarding/baseline-files.json')['files']:bound(row,ROOT/row['path'])
        assert maintained()==before and identity()==r['git_identity']
        r.update(state='PASS',maintained_file_hashes=before,helper=rec(HELPER),contract=rec(E/'contract.json'),operation=rec(E/'operation/qualification.json'),
            admission=rec(E/'admission.json'),original_copy_pairs=copies,final_operation_copy_pairs=28,original_native_log_hashes_verified=native_logs,
            retained_attempts=receipts,profiles=profiles,writer_censuses=[q['writer_census_before'],q['writer_census_after']],
            contract_input_count=len(data['inputs']),old_proposal_input_count=len(old_proposal['inputs']),old_proposal_tool_count=len(old_proposal['tools']),
            inspector_recipe=rec(E/'inspector-recipe.json'),retained_static_gate_returncodes=[0,0],original_Claude_files=19,findings=[],
            runtime_scope='Observed parent native operation; no native profile invocation by reviewer',protected_invocations=0)
    except BaseException as error:r.update(state='FAIL',error=repr(error));raise
    finally:r['completed_at']=datetime.now(UTC).isoformat();save('checks.json',r)
    print(json.dumps({'state':r['state'],'controls':len(r['controls']),'original_copy_pairs':copies,'recorded_native_commands':12,'original_Claude_files':19}))

def protection():
    checks=load(D/'checks.json');assert checks['state']=='PASS'
    assert not (D/'protected-invocation.json').exists(),'protected() already attempted'
    assert sha(HELPER)==HELPER_SHA and sha(E/'contract.json')==CONTRACT_SHA
    proposal=load(ROOT/'evidence/iwyu-build/proposal.json')
    for name in ('gcc_install.py','gcc_bottles.py','mise_link_probe.py','p2996_install.py','vcpkg_register.py'):
        assert sha(ROOT/'dev/toolchains'/name)==proposal['inputs']['dev/toolchains/'+name]
    sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'dev/toolchains'))
    spec=importlib.util.spec_from_file_location('reviewed_mise_runtime',HELPER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    r={'state':'RUNNING','started_at':datetime.now(UTC).isoformat(),'protected_invocations':1,'native_subprocesses':0,'helper':rec(HELPER),'contract':rec(E/'contract.json')}
    save('protected-invocation.json',r)
    try:
        value=module.protected()
        assert value==load(E/'contract.json')['current_mise']
        for path,digest in checks['maintained_file_hashes'].items():assert sha(ROOT/path)==digest,path
        for row in load(ROOT/'evidence/onboarding/baseline-files.json')['files']:bound(row,ROOT/row['path'])
        assert sha(E/'operation/qualification.json')==OP_SHA
        inv=load(ROOT/'evidence/p2996-install/independent-installation/post-install-inventory.json');baseline=load(ROOT/'evidence/p2996-registration/independent-registration/post-state.json')
        assert next(row for row in inv['records'] if row['path']==value['path'])==load(E/'contract.json')['previous_record']
        r.update(state='PASS',current_mise=value,historical_record_unchanged=True,git_identity=identity(),original_Claude_files=19,
            protected_counts={'globals':len(baseline['protected']['global_files']),'packages':len(baseline['protected']['packages']),'glib_files':len(baseline['protected']['glib_files']),
            'directory_entries':{k:len(v) for k,v in baseline['directories'].items()},'mise_install_entries':len(baseline['install_entries']),
            'source_build_records':len(inv['records']),'llvm_prefix_entries':len(load(ROOT/'evidence/p2996-install/operation/prefix-inventory.json')),
            'old_proposal_inputs':len(proposal['inputs']),'old_proposal_tools':len(proposal['tools'])})
    except BaseException as error:r.update(state='FAIL',error=repr(error));raise
    finally:r['completed_at']=datetime.now(UTC).isoformat();save('protected-invocation.json',r)
    print(json.dumps({'state':r['state'],'protected_invocations':1,'native_subprocesses':0,'historical_record_unchanged':True}))

if __name__=='__main__':{'audit':audit,'protection':protection}[sys.argv[1]]()
