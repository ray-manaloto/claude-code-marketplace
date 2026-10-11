from pathlib import Path
from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
import re
import shlex

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
OP = Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/core-p2996-20261011T132822Z')
HERE = Path(__file__).parent

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}

report = {'started_at': datetime.now(UTC).isoformat(), 'kind': 'read-only receipt and artifact audit; no native subprocesses', 'state': 'RUNNING'}
try:
    qualification = OP / 'qualification.json'
    assert sha(qualification) == 'bd27207192fe6690f2719415b6cea3158ccc9f300b3a00a10c0bf51db6cd7d80'
    q = load(qualification)
    helper = ROOT / 'dev/toolchains/core_matrix.py'
    assert sha(helper) == q['helper_sha256'] == '8def0803981d2bbc8c75b36591224b41ba105164f5d287ff71862a0ca864bea1'
    (HERE / 'core_matrix.py.source').write_bytes(helper.read_bytes())
    assert q['state'] == 'FAIL' and q['error'] == 'AssertionError()'
    assert q['protected_state_unchanged'] is True and 'preservation_error' not in q
    invocation = load(OP / 'invocation.json')
    assert invocation['returncode'] == 1 and invocation['helper_sha256'] == q['helper_sha256']
    assert sha(OP / 'invocation.json') == sha(OP.parent / (OP.name + '-invocation.json'))
    for log in invocation['logs']:
        assert sha(log['path']) == log['sha256'] and Path(log['path']).stat().st_size == log['bytes']
    wrapper_stderr = Path(invocation['logs'][1]['path']).read_text()
    assert 'line 164, in main' in wrapper_stderr and wrapper_stderr.endswith('AssertionError\n')
    emitted = [json.loads(line) for line in Path(invocation['logs'][0]['path']).read_text().splitlines()]
    assert emitted[:-1] == [{'case': c['case'], 'returncode': c['returncode']} for c in q['commands']]
    assert emitted[-1] == {'state': 'FAIL', 'receipt': str(qualification)}
    manifest = ROOT / 'evidence/core-p2996/attempt-1/manifest.json'
    retained = load(manifest)
    assert retained['qualification_sha256'] == sha(qualification) and len(retained['files']) == 306
    for item in retained['files']:
        for path in (Path(item['source']), ROOT / item['path']):
            assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], str(path)
    refs = {}
    def visit(value):
        if isinstance(value, dict):
            if 'path' in value and 'sha256' in value:
                path = Path(value['path'])
                assert sha(path) == value['sha256'], str(path)
                if 'bytes' in value:
                    assert path.stat().st_size == value['bytes'], str(path)
                assert str(path) not in refs or refs[str(path)]['sha256'] == value['sha256']
                refs[str(path)] = record(path)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(q)
    command_map = {c['case']: c for c in q['commands']}
    assert len(command_map) == len(q['commands']) == 106
    assert Counter(c['returncode'] for c in q['commands']) == Counter({0: 103, 1: 3})
    assert all(len(c['logs']) == 2 and c['elapsed_seconds'] < 60 for c in q['commands'])
    assert q['commands'][-1]['case'] == 'gcc16-profile' and q['commands'][-1]['returncode'] == 0
    def stdout(label):
        return Path(command_map[label]['logs'][0]['path']).read_text()
    def stderr(label):
        return Path(command_map[label]['logs'][1]['path']).read_text()
    configs = ('Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel')
    assert set(q['trees']) == {'p2996-static', 'p2996-shared'}
    assert set(q['cells']) == {f'p2996-{mode}-{config}' for mode in ('static', 'shared') for config in configs}
    abi = {}
    for name, tree in q['trees'].items():
        assert len(tree['configured_evidence']) == 40
        capture_root = OP / 'configured-evidence' / name
        assert load(capture_root / 'compile_commands.json') == tree['compile_database']
        assert len(tree['compile_database']) == len(set(tree['outputs'])) == 8
        for row in tree['compile_database']:
            args = shlex.split(row['command'])
            assert args.count('-freflection') == (Path(row['file']).name == 'core.cpp')
            assert args.count('-std=c++26') == 1 and '-Werror' in args
        generated = stdout(name + '-abi-commands').splitlines()
        assert [shlex.split(line) for line in generated] == tree['probe_commands']
        log = (capture_root / 'CMakeFiles/CMakeConfigureLog.yaml').read_text().split('kind: "try_compile-v1"')
        assert len(log) == 2
        event = log[1].split('\n  -\n', 1)[0]
        actual = [line.strip().split('] ', 1)[1] for line in event.splitlines() if re.match(r'^\s+\[[12]/2\] ', line)]
        assert actual == [line.replace('\\', '\\\\') for line in generated]
        assert 'cached: false' in event and 'exitCode: 0' in event and 'variable: "CMAKE_CXX_ABI_COMPILED"' in event
        assert tree['probe']['executable']['sha256'] == tree['probe']['abi-copy']['sha256']
        abi[name] = {'uncached_native_exit': 0, 'generated_and_recorded_native_commands_match': True, 'configured_text_count': 40, 'compile_database_rows': 8, 'retained_probe_artifacts': 3}
    contract = load(ROOT / 'evidence/core-command-preparation/harness-contract.json')
    prefix = Path(contract['lane_specs']['p2996']['prefix'])
    required = {(prefix / 'lib' / name).resolve() for name in ('libc++.dylib', 'libc++abi.dylib', 'libunwind.dylib')}
    os_cxx = {Path(path) for path in contract['lane_specs']['gcc16']['allowed_recorded_os_cxx_images']}
    cells = {}
    symbol = '__ZN19aggregated_research16reflection_probeEv'
    for name, cell in q['cells'].items():
        generated = [shlex.split(line) for line in stdout(name + '-generated').splitlines()]
        actual = [shlex.split(line.split('] ', 1)[1]) for line in stdout(name + '-build').splitlines() if re.match(r'^\[[0-9]+/[0-9]+\] ', line)]
        assert len(generated) == len(actual) == 4 and Counter(map(tuple, generated)) == Counter(map(tuple, actual))
        assert cell['commands'] == actual
        build_argv = command_map[name + '-build']['argv']
        assert build_argv[build_argv.index('--parallel') + 1] == '1'
        assert '100% tests passed' in stdout(name + '-test')
        assert stdout(name + '-runtime') == 'reflection value=43, members=1\n'
        assert 'arm64' in stdout(name + '-architecture') and stdout(name + '-library-architecture').strip() == 'arm64'
        assert sum(line.rstrip().endswith(' external ' + symbol) for line in stdout(name + '-exports').splitlines()) == 1
        loaded = {Path(re.search(r' (/.*)$', line)[1]).resolve() for line in stderr(name + '-runtime').splitlines()}
        assert sorted(map(str, loaded)) == cell['loaded_images'] and required <= loaded
        assert {p for p in loaded if p.name.startswith(('libc++', 'libunwind', 'libstdc++', 'libgcc'))} <= required | os_cxx
        shared = '-shared-' in name
        assert {p for p in loaded if p.name == 'libresearch_core.dylib'} == ({Path(cell['library']['path']).resolve()} if shared else set())
        if shared:
            assert stdout(name + '-install-name').splitlines()[1:] == ['@rpath/libresearch_core.dylib']
            assert '(undefined) external ' + symbol + ' (from libresearch_core)' in stdout(name + '-consumer-symbol')
        cells[name] = {'command_count': 4, 'actual_matches_generated': True, 'compile_build_ctest_architecture_symbols_runtime_returncode': 0, 'private_runtime_images_match': True, 'summary': cell['summary']}
    controls = []
    assert len(q['controls']) == 4
    for actual, expected in zip(q['controls'], contract['private_controls'][:4], strict=True):
        label = actual['case']
        assert label == 'p2996-' + expected['case']
        assert actual['returncode'] == command_map[label]['returncode'] == expected['expected_native_returncode']
        assert actual['source']['sha256'] == expected.get('source_sha256', expected.get('candidate_sha256'))
        obj = OP / (label + '.o')
        assert obj.exists() == (actual['returncode'] == 0)
        if actual['returncode']:
            assert expected['expected_diagnostic'] in stderr(label)
        controls.append({'case': label, 'returncode': actual['returncode'], 'object_exists': obj.exists(), 'expected_diagnostic_verified': 'expected_diagnostic' in expected})
    admitted = load(OP / 'admission.json')
    assert sha(OP / 'admission.json') == q['admission_sha256'] == invocation['admission_sha256']
    assert admitted['inputs'] == q['inputs']
    for path, expected in q['inputs'].items():
        assert sha(ROOT / path) == expected, path
    for path, expected in admitted['tool_hashes'].items():
        assert sha(path) == expected, path
    original = load(ROOT / 'evidence/onboarding/baseline-files.json')['files']
    assert len(original) == 19
    for item in original:
        assert sha(ROOT / item['path']) == item['sha256'] and (ROOT / item['path']).stat().st_size == item['bytes']
    gcc = load(ROOT / 'evidence/gcc-runtime/qualification.json')['selected_environment']
    current = json.loads(stdout('gcc16-profile'))
    difference = {key: {'expected': gcc[key], 'actual': current[key]} for key in gcc if gcc[key] != current[key]}
    assert set(current) == set(gcc) and set(difference) == {'path_sha256'}
    report.update(state='PASS: retained partial-run evidence and failure closure; full matrix remains FAIL', qualification=record(qualification), invocation=record(OP / 'invocation.json'), manifest=record(manifest), helper=record(helper), retained_original_and_copy_pairs=306, command_count=106, native_returncodes={'0':103,'1_expected':3}, command_log_count=212, referenced_artifact_count=len(refs), abi=abi, cells=cells, controls=controls, failure={'wrapper_returncode':1,'last_native_command':'gcc16-profile','last_native_returncode':0,'location':'dev/toolchains/core_matrix.py:164','error':'AssertionError()','comparison_difference':difference,'profile_diagnosis':'owned by configuration inspector; no diagnosis or retry here'}, preservation={'operation_finally_recorded_success':True,'no_recorded_preservation_error':True,'independently_verified_project_inputs':len(q['inputs']),'independently_verified_tool_hashes':len(admitted['tool_hashes']),'independently_verified_original_Claude_files':19,'full_protected_inventory_not_repeated':True}, checks_not_run=['eight GCC matrix cells','GCC macro control','CTest exit-contract controls','default-after and source-after native probes','new compilation or reproduction','old test or mutation batteries','full protected-state inventory','static gates (prior admitted pre-run receipts retained)'], findings=[])
    (HERE / 'verified-artifacts.json').write_text(json.dumps({'records':list(refs.values())},indent=2)+'\n')
except BaseException as error:
    report.update(state='REVIEW_AUDIT_FAILED', review_error=repr(error))
    raise
finally:
    report['completed_at'] = datetime.now(UTC).isoformat()
    (HERE / 'receipt-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'state':report['state'],'commands':106,'retained_copy_pairs':306,'artifact_references':len(refs),'cells':8,'controls':4}))
