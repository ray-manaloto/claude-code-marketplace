from pathlib import Path
from collections import Counter
from datetime import UTC, datetime
import ast
import hashlib
import json
import os
import re
import shlex
import sys
import time
import yaml

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = ROOT / 'evidence/core-p2996'
OP = Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T134510Z')
D = Path(__file__).parent
HELPER_SHA = '417041b6eb21161b0023a48be9962812c16bf2ddb6851ea19319bb837b70a319'
QUALIFICATION_SHA = '71bf14af242c6346fb2a3470d3b57ded19502858730bad0b280e07c5e9e2a5b2'
MANIFEST_SHA = '26f0cc39083c12205d5959488e526dacd104c8e283616887ac0bbdab81d550a5'
ADMISSION_SHA = '663a11836c5552ffe80ffdcafb75c47198ab9e1a495cee414993a0e05d001fea'
CONFIGS = ('Debug','Release','RelWithDebInfo','MinSizeRel')
def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()
def load(path): return json.loads(Path(path).read_text())
def record(path):
    path = Path(path)
    return {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}

report = {'state':'RUNNING','started_at':datetime.now(UTC).isoformat(),'native_subprocesses':0,'new_native_compiler_build_profile_invocations':0}
started = time.monotonic()
try:
    qualification = OP/'qualification.json'
    assert sha(qualification) == sha(E/'operation/qualification.json') == QUALIFICATION_SHA
    assert sha(E/'operation-manifest.json') == MANIFEST_SHA
    assert sha(ROOT/'dev/toolchains/core_matrix.py') == HELPER_SHA
    assert sha(E/'admission.json') == sha(OP/'admission.json') == ADMISSION_SHA
    maintained = [ROOT/'dev/toolchains/core_matrix.py',ROOT/'docs/core-qualification.md',ROOT/'docs/status.md',ROOT/'.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md',ROOT/'.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md']
    maintained_before = [record(p) for p in maintained]
    q = load(qualification)
    assert q['state'] == 'PASS: native core, two compilers, static/shared, sixteen cells and seven controls'
    assert q['helper_sha256'] == HELPER_SHA and q['admission_sha256'] == ADMISSION_SHA
    assert q['lease_released'] is True and q['protected_state_unchanged'] is True
    assert 'error' not in q and 'preservation_error' not in q
    invocation = load(OP/'invocation.json')
    assert invocation['returncode'] == 0 and invocation['helper_sha256'] == HELPER_SHA and invocation['admission_sha256'] == ADMISSION_SHA
    for item in invocation['logs']:
        assert sha(item['path']) == item['sha256'] and Path(item['path']).stat().st_size == item['bytes']
    assert not Path(invocation['logs'][1]['path']).read_bytes()
    emitted = [json.loads(line) for line in Path(invocation['logs'][0]['path']).read_text().splitlines()]
    assert emitted[:-1] == [{'case':c['case'],'returncode':c['returncode']} for c in q['commands']]
    assert emitted[-1] == {'state':q['state'],'receipt':str(qualification)}
    manifest = load(E/'operation-manifest.json')
    assert manifest['qualification_sha256'] == QUALIFICATION_SHA and len(manifest['files']) == 603 and len(manifest['private_artifacts']) == 77
    for item in manifest['files']:
        for path in (Path(item['source']),ROOT/item['path']):
            assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], str(path)
    for item in manifest['private_artifacts']:
        assert sha(item['path']) == item['sha256'] and Path(item['path']).stat().st_size == item['bytes'], item['path']
    refs = {}
    def visit(value):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:
                path = Path(value['path'])
                assert sha(path) == value['sha256'], str(path)
                if 'bytes' in value: assert path.stat().st_size == value['bytes'], str(path)
                assert str(path) not in refs or refs[str(path)]['sha256'] == value['sha256']
                refs[str(path)] = record(path)
            for child in value.values(): visit(child)
        elif isinstance(value,list):
            for child in value: visit(child)
    visit(q)
    commands = {c['case']:c for c in q['commands']}
    assert len(commands) == len(q['commands']) == 207
    assert Counter(c['returncode'] for c in q['commands']) == Counter({0:201,1:5,8:1})
    assert all(len(c['logs']) == 2 and c['elapsed_seconds'] < 60 for c in q['commands'])
    def stdout(label): return Path(commands[label]['logs'][0]['path']).read_text()
    def stderr(label): return Path(commands[label]['logs'][1]['path']).read_text()
    admitted, proposal, pre_review = load(E/'admission.json'),load(E/'proposal.json'),load(E/'pre-run-review.json')
    assert sha(E/'pre-run-review.json') == admitted['pre_run_review_sha256'] == '69b47555923a1b5b514ee1216177d70b42698f526ba92bc627f582425d684d18'
    assert sha(E/'proposal.json') == pre_review['proposal_sha256'] == '93d541a04a69d29b9341d7c4f51a870a9667c1274f75c38d08f2cb3e8f728973'
    assert pre_review['result'].startswith('PASS') and not pre_review['findings']
    assert all(admitted[k] == proposal[k] for k in ('base_head','helper_sha256','inputs','tool_hashes'))
    assert admitted['inputs'] == q['inputs'] and len(q['inputs']) == 72 and len(admitted['tool_hashes']) == 18
    def inputs_match():
        for path, expected in q['inputs'].items(): assert sha(ROOT/path) == expected, path
        for path, expected in admitted['tool_hashes'].items(): assert sha(path) == expected, path
    inputs_match()
    assert sha(ROOT/'dev/toolchains/core_commands.py') == '9c1cdf78f5102a1256a71e965fd3bf9f2b2461f1d6e509fb723301e4b92565d6'
    sys.dont_write_bytecode = True
    sys.path.insert(0,str(ROOT/'dev/toolchains'))
    from core_commands import CoreCommands
    from gcc_install import preserved
    from mise_link_probe import snapshot
    from p2996_install import prefix_inventory
    from vcpkg_register import install_entries
    import subprocess
    def native_forbidden(*args,**kwargs): raise AssertionError('Native subprocess forbidden during artifact audit')
    subprocess.run = native_forbidden
    subprocess.Popen = native_forbidden
    contract = load(ROOT/'evidence/core-command-preparation/harness-contract.json')
    assert sha(ROOT/'evidence/core-command-preparation/harness-contract.json') == 'feb0f9700b7ed6828334fb39c6e6d631c87b9be74f4fb9334cdd063b92ecfec8'
    configuration = load(ROOT/'evidence/p2996-math-resume/operation/qualification.json')['proposal']['configuration']
    sdk = configuration['sdk']['path']
    build_tools = load(ROOT/'evidence/tool-foundation/host-qualification.json')['binaries']
    cmake = build_tools['cmake']['resolved_path']
    assert set(q['trees']) == {lane+'-'+mode for lane in ('p2996','gcc16') for mode in ('static','shared')}
    assert set(q['cells']) == {tree+'-'+config for tree in q['trees'] for config in CONFIGS}
    tree_reviews, validators = {}, {}
    for name, tree in q['trees'].items():
        lane, mode = name.split('-'); build = OP/name; spec = contract['lane_specs'][lane]
        v = CoreCommands(ROOT,build,lane,spec['prefix'],sdk,cmake,'/usr/bin/ar',str(Path(spec['prefix'])/'bin/llvm-ranlib') if lane=='p2996' else '/usr/bin/ranlib',mode=='shared')
        validators[name] = v
        captures = OP/'configured-evidence'/name
        rows = load(captures/'compile_commands.json')
        assert rows == tree['compile_database'] and v.compile_database(rows) == tree['outputs']
        assert len(rows) == len(set(tree['outputs'])) == 8
        generated = stdout(name+'-abi-commands').splitlines()
        assert [shlex.split(line) for line in generated] == tree['probe_commands']
        events = [event for event in yaml.safe_load((captures/'CMakeFiles/CMakeConfigureLog.yaml').read_text())['events'] if event.get('kind') == 'try_compile-v1']
        assert len(events) == 1
        event = events[0]; result = event['buildResult']; child = Path(event['directories']['binary'])
        assert child.is_relative_to(build/'CMakeFiles/CMakeScratch')
        assert result['variable'] == 'CMAKE_CXX_ABI_COMPILED' and result['cached'] is False and result['exitCode'] == 0
        native_lines = [line.split('] ',1)[1] for line in result['stdout'].splitlines() if re.match(r'^\[[12]/2\] ',line)]
        assert native_lines == [line.replace('\\','\\\\') for line in generated]
        assert len(generated) == 2
        for args in tree['probe_commands']:
            unwrapped = v.flags(args,linking='-c' not in args)
            assert unwrapped.count('-o') == 1
            output = (child/unwrapped[unwrapped.index('-o')+1]).resolve()
            assert output.is_relative_to(child)
            kind = 'object' if '-c' in unwrapped else 'executable'
            assert str(output) == tree['probe'][kind]['source']
        assert tree['probe']['executable']['sha256'] == tree['probe']['abi-copy']['sha256']
        compiler = (captures/'CMakeFiles/4.4.4/CMakeCXXCompiler.cmake').read_text()
        assert 'set(CMAKE_CXX_COMPILER_WORKS TRUE)' in compiler and 'set(CMAKE_CXX_ABI_COMPILED TRUE)' in compiler
        assert f'set(CMAKE_CXX_COMPILER_ID "{spec["compiler_id_version"][0]}")' in compiler
        assert f'set(CMAKE_CXX_COMPILER_VERSION "{spec["compiler_id_version"][1]}")' in compiler
        tree_reviews[name] = {'uncached_ABI_native_exit':0,'ABI_command_count':2,'actual_generated_probe_commands_match':True,'retained_ABI_artifacts':3,'compile_database_rows':8,'unique_outputs':8,'configured_text_captures':len(tree['configured_evidence'])}
    cells = {}; symbol = '__ZN19aggregated_research16reflection_probeEv'
    os_images = {Path(p) for p in contract['lane_specs']['gcc16']['allowed_recorded_os_cxx_images']}
    for name, cell in q['cells'].items():
        tree, config = name.rsplit('-',1); lane, mode = tree.split('-'); shared = mode=='shared'
        v = validators[tree]; build = OP/tree; spec = contract['lane_specs'][lane]
        generated = [shlex.split(line) for line in stdout(name+'-generated').splitlines()]
        actual = [shlex.split(line.split('] ',1)[1]) for line in stdout(name+'-build').splitlines() if re.match(r'^\[[0-9]+/[0-9]+\] ',line)]
        v.actions(generated,config); v.actions(actual,config); v.actual_matches(generated,actual)
        assert actual == cell['commands']
        assert len(actual) == (8 if lane=='gcc16' else 4)
        build_argv = commands[name+'-build']['argv']; assert build_argv[build_argv.index('--parallel')+1] == '1'
        assert '100% tests passed' in stdout(name+'-test') and 'out of 1' in stdout(name+'-test')
        assert commands[name+'-test']['returncode'] == 0 and commands[name+'-runtime']['returncode'] == 0
        assert stdout(name+'-runtime') == 'reflection value=43, members=1\n'
        summary = dict(line.split('=',1) for line in (build/('core-'+config+'.txt')).read_text().splitlines())
        assert summary == cell['summary']
        assert Path(summary['binary']) == build/config/'research_core_smoke' and Path(summary['library']) == build/config/('libresearch_core.dylib' if shared else 'libresearch_core.a')
        assert 'Mach-O 64-bit executable arm64' in stdout(name+'-architecture') and stdout(name+'-library-architecture').strip() == 'arm64'
        exports = [line for line in stdout(name+'-exports').splitlines() if line.split()[-1:] == [symbol]]
        assert len(exports) == 1 and '(__TEXT,__text)' in exports[0] and ' external ' in exports[0] and 'private external' not in exports[0]
        for artifact in ('binary','core') if shared else ('binary',):
            deps = stdout(name+'-'+artifact+'-libraries'); paths = stdout(name+'-'+artifact+'-rpaths')
            if lane == 'p2996':
                assert all(lib in deps for lib in ('libc++.','libc++abi.','libunwind.')) and 'libstdc++' not in deps and '/usr/lib/libc++' not in deps
                assert 'path '+str(v.prefix/'lib')+' (offset ' in paths
            else:
                selected = [line.strip().split(' (',1)[0] for line in deps.splitlines()[1:] if 'libstdc++' in line]
                assert len(selected) == 1 and Path(selected[0]).resolve() == Path(spec['runtime_identities']['libstdcxx']['path']).resolve()
                assert 'libc++' not in deps
            if artifact=='binary':
                assert ('@rpath/libresearch_core.dylib' in deps) == shared
                if shared: assert 'path '+str(build/config)+' (offset ' in paths
        if shared:
            assert stdout(name+'-install-name').splitlines()[1:] == ['@rpath/libresearch_core.dylib']
            assert any(symbol in line and re.search(r'\(from libresearch_core(?:\.dylib)?\)$',line) for line in stdout(name+'-consumer-symbol').splitlines())
        diagnostics = stderr(name+'-runtime').splitlines()
        assert diagnostics and all(line.startswith('dyld[') for line in diagnostics)
        loaded = {Path(re.search(r' (/.*)$',line)[1]).resolve() for line in diagnostics}
        required = {p.resolve() for p in v.libraries} if lane=='p2996' else {Path(item['path']).resolve() for item in spec['runtime_identities'].values()}
        assert required <= loaded and sorted(map(str,loaded)) == cell['loaded_images']
        assert {p for p in loaded if p.name.startswith(('libc++','libunwind','libstdc++','libgcc'))} <= required|os_images
        assert {p for p in loaded if p.name=='libresearch_core.dylib'} == ({Path(cell['library']['path']).resolve()} if shared else set())
        cells[name] = {'recorded_commands':len(actual),'independent_CDB_action_and_actual_generated_comparison':'PASS','recorded_build_test_runtime_exit':0,'public_symbol':symbol,'ARM64':True,'runtime_origins':'PASS','shared_consumer_binding_checked':shared}
    expected_controls = [('p2996',control) for control in contract['private_controls'][:4]]+[('gcc16',contract['private_controls'][3])]
    control_results = []
    for actual,(lane,expected) in zip(q['controls'][:5],expected_controls,strict=True):
        label = actual['case']; assert label == lane+'-'+expected['case']
        assert actual['returncode'] == commands[label]['returncode'] == expected['expected_native_returncode']
        assert actual['source']['sha256'] == expected.get('source_sha256',expected.get('candidate_sha256'))
        output = OP/(label+'.o'); assert output.exists() == (actual['returncode']==0)
        if actual['returncode']: assert expected['expected_diagnostic'] in stderr(label)
        control_results.append({'case':label,'returncode':actual['returncode'],'successful_object':output.exists(),'expected_diagnostic_verified':bool(actual['returncode'])})
    assert commands['ctest-control-child']['returncode'] == 1 and stdout('ctest-control-child') == 'reflection value=43, members=1\n'
    for actual,expected in zip(q['controls'][5:],contract['private_controls'][4:],strict=True):
        label = actual['case']; assert label == expected['case']
        assert actual['returncode'] == commands[label]['returncode'] == expected['expected_ctest_returncode']
        definition = Path(actual['definition']['path']).read_text(); last = Path(actual['last_test']['path']).read_text()
        assert definition == expected['private_CTestTestfile_contents']
        assert 'reflection value=43, members=1' in last
        if actual['returncode']==0:
            assert 'Test Pass Reason:\nRequired regular expression found.' in last
        else:
            assert 'Test Failed.' in last
        control_results.append({'case':label,'returncode':actual['returncode'],'exact_private_definition_verified':True,'last_test_log_verified':True})
    assert len(control_results) == 7
    registered = ROOT/'evidence/p2996-registration'
    normal = (registered/'operation/default-after.stdout').read_text()
    assert stdout('default-before') == stdout('default-after') == normal
    for suffix in ('head','tree','status','diff'):
        assert stdout('source-before-'+suffix) == stdout('source-after-'+suffix) == (registered/('operation/source-after-'+suffix+'.stdout')).read_text()
    gcc = load(ROOT/'evidence/gcc-runtime/qualification.json'); runtime = load(ROOT/'evidence/p2996-reflection/operation/qualification.json')
    for lane, expected in [('gcc16',gcc['selected_environment']),('p2996',runtime['selected_environment'])]:
        assert json.loads(stdout(lane+'-profile')) == expected|{'path_sha256':runtime['selected_environment']['path_sha256']}
    for item in gcc['identities'].values(): assert sha(item['path']) == item['sha256']
    assert sha(Path(sdk)/'SDKSettings.json') == configuration['sdk']['settings_sha256']
    baseline = load(registered/'independent-registration/post-state.json')
    installed = ROOT/'evidence/p2996-install'; inventory = load(installed/'independent-installation/post-install-inventory.json'); prefix = Path(inventory['prefix'])
    registration_review = load(registered/'registration-review.json')
    assert sha(registered/'independent-registration/post-state.json') == registration_review['post_state']['sha256']
    assert sha(installed/'independent-installation/post-install-inventory.json') == registration_review['retained_source_build_inventory']['inventory_sha256']
    assert sha(installed/'operation/prefix-inventory.json') == registration_review['prefix_inventory']['inventory_sha256']
    reflection_helper = ROOT/'dev/toolchains/p2996_reflection.py'; assert sha(reflection_helper) == runtime['helper_sha256']
    protected_node = next(n for n in ast.walk(ast.parse(reflection_helper.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='protected')
    protected_scope = {'baseline':baseline,'inventory':inventory,'prefix':prefix,'evidence':installed,'load':load,'preserved':preserved,'snapshot':snapshot,'install_entries':install_entries,'Path':Path,'os':os,'digest':sha,'prefix_inventory':prefix_inventory}
    exec(compile(ast.Module(body=[protected_node],type_ignores=[]),str(reflection_helper),'exec'),protected_scope)
    protected_scope['protected']()
    originals = load(ROOT/'evidence/onboarding/baseline-files.json')['files']; assert len(originals)==19
    for item in originals: assert sha(ROOT/item['path'])==item['sha256'] and (ROOT/item['path']).stat().st_size==item['bytes']
    static = load(E/'post-operation-static-checks.json'); assert static['helper_sha256']==HELPER_SHA and len(static['checks'])==2
    assert all(c['returncode']==0 for c in static['checks']) and json.loads(static['checks'][1]['stdout'])['checks']['baseline']==19
    attempt = load(E/'attempt-1/operation/qualification.json')
    assert sha(E/'attempt-1/operation/qualification.json')=='bd27207192fe6690f2719415b6cea3158ccc9f300b3a00a10c0bf51db6cd7d80' and attempt['state']=='FAIL'
    assert sha(E/'attempt-1/failure-review.json')=='faa0b91c911fe938277f700aa8e5fc9f1a3227c398c5c3e7f0eac4da144025ac'
    assert 'cause remains unproven' in (ROOT/'docs/core-qualification.md').read_text()
    assert 'Independent review is pending' in (ROOT/'docs/core-qualification.md').read_text()
    for match in re.findall(r'\]\(([^)]+)\)',(ROOT/'docs/core-qualification.md').read_text()):
        assert ((ROOT/'docs')/match).resolve().is_file(), match
    inputs_match()
    assert maintained_before == [record(p) for p in maintained]
    report.update(state='PASS: independent completed-native-evidence review; no rebuild',findings=[],qualification=record(qualification),helper_sha256=HELPER_SHA,manifest=record(E/'operation-manifest.json'),admission=record(E/'admission.json'),parent_wrapper={'returncode':0,'elapsed_seconds':invocation['elapsed_seconds'],'receipt':record(OP/'invocation.json')},recorded_native_outcomes={'commands':207,'zero':201,'expected_one':5,'expected_eight':1},hash_verification={'text_copy_pairs':603,'private_artifacts':77,'command_logs':414,'unique_qualification_references':len(refs),'configured_text_captures':sum(len(t['configured_evidence']) for t in q['trees'].values())},trees=tree_reviews,cells=cells,controls=control_results,ctest_failing_child_recorded_exit=1,default_and_source_before_after_match=True,profile_dictionaries_match_reviewed_correction=True,preservation={'independent_current_readonly_inventory':'PASS','global_files':len(baseline['protected']['global_files']),'packages':len(baseline['protected']['packages']),'glib_files':len(baseline['protected']['glib_files']),'directory_entries':{p:len(v) for p,v in baseline['directories'].items()},'install_entries':len(baseline['install_entries']),'retained_source_build_records':len(inventory['records']),'prefix_entries':len(load(installed/'operation/prefix-inventory.json')),'admitted_project_inputs':72,'admitted_tool_hashes':18,'original_Claude_files':19},recorded_post_operation_static_exits=[0,0],static_gates_rerun=False,maintained_files=maintained_before,first_attempt_preserved_as_FAIL=True,earlier_PATH_transition_cause='UNPROVEN',docs_disposition='Accurately distinguish successful native execution, pending independent review, prior failed attempt, and unqualified research/dependencies/packages',limitations=['Recorded compiler/build/test/runtime and metadata commands were not executed again by reviewer.','Independent replay parses completed outputs using the pinned acceptance rules and YAML parser; it is not a new native build.','The small POD/reflection witness does not qualify research-provider behavior, dependency/package linkage, the larger application/dependency matrix, named modules, sanitizers, or OCI acceptance.','No old failure-injection or timeout battery was repeated.'])
    (D/'verified-references.json').write_text(json.dumps({'records':list(refs.values())},indent=2)+'\n')
except BaseException as error:
    report.update(state='REVIEW_AUDIT_FAILED',review_error=repr(error))
    raise
finally:
    report['elapsed_seconds']=time.monotonic()-started
    report['completed_at']=datetime.now(UTC).isoformat()
    (D/'artifact-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'state':report['state'],'retained_copy_pairs':603,'private_artifacts':77,'recorded_commands':207,'parsed_trees':4,'parsed_cells':16,'controls':7,'native_subprocesses':0,'protected_current_state':'PASS'}))
