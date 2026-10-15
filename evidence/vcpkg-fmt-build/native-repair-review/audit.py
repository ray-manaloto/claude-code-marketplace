from pathlib import Path
import ast, hashlib, json, os

R = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = R / 'evidence/vcpkg-fmt-build'
A = E / 'attempt-1'
D = Path(__file__).parent
seen = {}
cache = {}
def read(p):
    p = Path(p)
    if str(p) not in cache:
        data = p.read_bytes()
        cache[str(p)] = data
        seen[str(p)] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return cache[str(p)]
def sha(p):
    read(p)
    return seen[str(Path(p))]['sha256']
def load(p): return json.loads(read(p))
def text(p): return read(p).decode()

expected = dict(head='de913727bd6d41c1d7d2c11b52a384902dbd6eec',
    helper='fcf8aebc632d1e4bc929897b91e0cde44340ace2d59749c5b71b6ee6a9aa98e2',
    contract='aea0d5f2da6df3cdd2cded252e017481e62e81f9b4b128a020b6c41a400fc776',
    candidate='cceff2368c287f197645295dfa80db029f16650c83944c026e7ae8ca696c709c',
    original_helper='1d1f90acbbbd5d9b1bc83d908203efd206f5cba9a191209cbf5fc6c90e4e1843',
    original_contract='3dc53024966ce96e09f3d17252ee978ed7c0254fc784ba9f32cd62acca0905a8',
    original_candidate='75156294bd1efc2ab3a7e0f5a2d3001c39b8e6f1b15fbbe4541ab814a17b13cc',
    original_review='b0f3529f1499b70f336531b1937e953f2ca47136fc0e7aac6a9dc1701dbae7a1')
gd = Path(text(R / '.git').strip().removeprefix('gitdir: '))
cg = (gd / text(gd / 'commondir').strip()).resolve()
ref = text(gd / 'HEAD').strip().removeprefix('ref: ')
assert ref == 'refs/heads/codex/marketplace-native-onboarding'
assert text(cg / ref).strip() == expected['head']
assert str(cg) == '/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'
assert sha(R / 'AGENTS.md') == '451833b3da3a90637e5814a85f3881bc1e7b99e661205284f8039401c8e0402d'
assert sha(R / 'dev/toolchains/vcpkg_fmt.py') == expected['helper']
assert sha(E / 'contract.json') == expected['contract']
assert sha(E / 'candidate.json') == expected['candidate']
c = load(E / 'contract.json'); oc = load(A / 'candidate/contract.json')
candidate = load(E / 'candidate.json'); original = load(A / 'candidate/candidate.json')
assert candidate['head'] == original['head'] == c['base_head'] == expected['head']
assert sha(A / 'candidate/contract.json') == expected['original_contract']
assert sha(A / 'candidate/candidate.json') == expected['original_candidate']
assert sha(A / 'candidate/vcpkg_fmt.py.source') == expected['original_helper']
assert sha(A / 'candidate/pre-run-review.json') == expected['original_review']
assert len(candidate['files']) == len(original['files']) == 4
for p, h in candidate['files'].items(): assert sha(R / p) == h, p
mapping = {'dev/toolchains/vcpkg_fmt.py': 'vcpkg_fmt.py.source', 'docs/vcpkg-toolchains.md': 'vcpkg-toolchains.md',
    '.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md': 'task_plan.md',
    '.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md': 'progress.md'}
for p, name in mapping.items(): assert sha(A / 'candidate' / name) == original['files'][p], p

manifest = load(A / 'copy-manifest.json'); rows = manifest['copies']
assert len(rows) == 68 and len({r['copy'] for r in rows}) == 68
historical = {str(R / p) for p in mapping} | {str(E / 'candidate.json'), str(E / 'contract.json')}
source_to_copy = {}
for row in rows:
    copy = R / row['copy']
    assert sha(copy) == row['sha256'] and len(read(copy)) == row['bytes'], row['copy']
    source_to_copy[row['source']] = copy
    if row['source'] not in historical:
        assert read(row['source']) == read(copy), row['copy']
assert sum(r['source'] in historical for r in rows) == 6

old = text(A / 'candidate/vcpkg_fmt.py.source'); new = text(R / 'dev/toolchains/vcpkg_fmt.py')
old_pattern = r'^([^#/:][^:=]*):[^=]+=(.*)$'
new_pattern = r'^([^#/:\r\n][^:=\r\n]*):[^=\r\n]+=(.*)$'
assert old.count(old_pattern) == old.count(expected['original_contract']) == 1
assert old.replace(expected['original_contract'], expected['contract']).replace(old_pattern, new_pattern) == new
old_ast = ast.parse(old); new_ast = ast.parse(new)
for n in ast.walk(old_ast):
    if isinstance(n, ast.Constant) and n.value == expected['original_contract']: n.value = expected['contract']
    if isinstance(n, ast.Constant) and n.value == old_pattern: n.value = new_pattern
assert ast.dump(old_ast) == ast.dump(new_ast)
changed_keys = sorted(k for k in set(oc) | set(c) if oc.get(k) != c.get(k))
assert changed_keys == ['host_compiler', 'tools']
assert c['host_compiler'] == {'C': '/Library/Developer/CommandLineTools/usr/bin/cc',
    'CXX': '/Library/Developer/CommandLineTools/usr/bin/c++', 'id': 'AppleClang', 'version': '21.0.0.21000334'}
new_tools = {c['host_compiler'][k] for k in ['C', 'CXX']}
assert set(c['tools']) - set(oc['tools']) == new_tools
assert {k: v for k, v in c['tools'].items() if k not in new_tools} == oc['tools']

repair = load(E / 'native-repair-scope.json')
assert sha(E / 'native-repair-scope.json') == candidate['repair_scope_sha256']
assert repair['helper_sha256'] == expected['helper'] and repair['contract_sha256'] == expected['contract']
assert repair['original_helper_sha256'] == expected['original_helper']
assert repair['changed_contract_keys'] == changed_keys and repair['unchanged_helper_ast_except_contract_digest_and_cache_regex']
assert repair['native_rebuilds_since_failure'] == 0
q = load(A / 'operation/qualification.json'); admission = load(A / 'candidate/admission.json')
native = load(A / 'candidate/native-execution.json'); launch = load(A / 'candidate/native-launch.json')
assert sha(A / 'operation/qualification.json') == repair['original_run_sha256']
assert sha(A / 'candidate/native-execution.json') == repair['original_execution_sha256']
assert q['state'] == 'FAIL' and q['error'] == 'AssertionError()' and q['cells'] == {}
assert q['protected_state_unchanged'] and 'preservation_error' not in q
assert q['helper_sha256'] == native['helper_sha256'] == admission['helper_sha256'] == expected['original_helper']
assert native['returncode'] == 1
assert admission['contract_sha256'] == expected['original_contract'] and admission['candidate_sha256'] == expected['original_candidate']
assert admission['review_sha256'] == expected['original_review']
assert q['admission_sha256'] == native['admission_sha256'] == sha(A / 'candidate/admission.json')
assert all(native[k] == v for k, v in launch.items())
assert read(A / 'candidate/native-execution.json') == read(A / 'launch/execution.json')
assert read(A / 'candidate/native-launch.json') == read(A / 'launch/launch.json')
assert sha(A / 'launch/vcpkg_fmt.py.source') == expected['original_helper']
assert 'line 62, in inspect_cell' in text(A / 'launch/stderr')
assert 'assert markers[language + "_PATH"] == identity[language]' in text(A / 'launch/stderr')
run = Path(admission['run_directory']); triplet = 'arm64-osx-p2996-static'
expected_cases = ['project-head', 'default-before', 'capacity-processes', 'docker-context', 'docker-census', 'docker-stats',
    'private-write', 'outside-write', 'symlink-write', 'network-denied', 'p2996-profile', triplet]
assert [r['case'] for r in q['commands']] == expected_cases
assert len({r['pid'] for r in q['commands']}) == 12
for row in q['commands']:
    expected_rc = 73 if row['case'] in ['outside-write', 'symlink-write', 'network-denied'] else 0
    assert row['returncode'] == row['expected_returncode'] == expected_rc
    assert row['elapsed_seconds'] < row['timeout_seconds']
    assert len(row['logs']) == 2
    for item in row['logs']: assert sha(source_to_copy[item['path']]) == item['sha256']
    assert text(A / 'operation' / (row['case'] + '.stderr')) == ''
    if expected_rc == 73: assert text(A / 'operation' / (row['case'] + '.stdout')) == 'DENIED:1\n'
for item in native['logs']: assert sha(source_to_copy[item['path']]) == item['sha256']
assert text(A / 'operation/project-head.stdout').strip() == expected['head']
assert sha(A / 'operation/default-before.stdout') == oc['inputs'][oc['default_profile']]
assert sha(A / 'operation/p2996-profile.stdout') == oc['inputs'][oc['profiles']['p2996']]
assert q['confinement']['profile_sha256'] == sha(A / 'operation/private.sb')
assert text(A / 'operation/allowed') == 'private\n'
install = q['commands'][-1]
assert install['timeout_seconds'] == 600 and install['elapsed_seconds'] < 9
assert install['argv'][:4] == ['/usr/bin/sandbox-exec', '-f', str(run / 'private.sb'), str(run / 'vcpkg/vcpkg')]
for arg in ['install', '--triplet='+triplet, '--host-triplet=arm64-osx', '--no-downloads', '--x-wait-for-lock', '--feature-flags=-binarycaching,compilertracking']:
    assert install['argv'].count(arg) == 1
assert 'All requested installations completed successfully' in text(A / 'operation' / (triplet + '.stdout'))

diagnosis = load(A / 'diagnosis.json'); dx = load(A / 'diagnosis-execution.json')
validation = load(A / 'repair-validation.json'); vx = load(A / 'repair-validation-execution.json')
assert sha(A / 'diagnosis.json') == repair['read_only_diagnosis_sha256']
assert sha(A / 'repair-validation.json') == repair['repair_validation_sha256']
assert dx['returncode'] == 1 and diagnosis['state'] == 'FAIL' and diagnosis['error'] == "KeyError('CMAKE_BUILD_TYPE')"
assert diagnosis['script_sha256'] == dx['script_sha256'] == sha(A / 'diagnose.py')
assert diagnosis['native_failure_sha256'] == sha(A / 'operation/qualification.json')
assert diagnosis['processes'] == [{'pid': row['pid'], 'case': row['case'], 'absent': True} for row in q['commands']]
assert diagnosis['lease_probe'] == {'free': True, 'contents_unchanged': True}
assert diagnosis['default_after']['returncode'] == 0 and diagnosis['default_after']['argv'] == q['commands'][1]['argv']
assert read(A / 'default-after.stdout') == read(A / 'operation/default-before.stdout')
for suffix in ['stdout', 'stderr']:
    assert sha(A / ('default-after.'+suffix)) == diagnosis['default_after'][suffix+'_sha256']
for row in load(A / 'diagnosis-copy-manifest.json')['copies']:
    assert sha(R / row['copy']) == row['sha256'] and read(row['source']) == read(R / row['copy'])
aliases = []
for language, row in zip(['C', 'CXX'], diagnosis['host_aliases'], strict=True):
    path = Path(c['host_compiler'][language])
    assert row['path'] == str(path) and path.samefile(Path(oc['host_compiler'][language]))
    assert os.readlink(path) == row['link'] and str(path.resolve()) == row['resolved']
    with path.open('rb') as stream: observed_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    with path.open('rb') as stream: observed_sha1 = hashlib.file_digest(stream, 'sha1').hexdigest()
    assert observed_sha == row['sha256'] == c['tools'][str(path)] == oc['tools'][oc['host_compiler'][language]]
    assert observed_sha1 == row['sha1']
    seen[str(path)] = {'sha256': observed_sha, 'bytes': path.stat().st_size}
    aliases.append({'language': language, 'path': str(path), 'samefile_as_pinned': True, 'sha256': observed_sha, 'sha1': observed_sha1})
assert vx['returncode'] == 0 and vx['stderr'] == '' and validation['state'] == 'PASS'
assert vx['script_sha256'] == validation['script_sha256'] == sha(A / 'validate-repair.py')
assert validation['helper_sha256'] == expected['helper'] and validation['contract_sha256'] == expected['contract']
assert validation['native_commands'] == 0 and validation['original_run_state'] == 'FAIL' and validation['inspect_cell_calls'] == 1
assert validation['crlf_keys_control'] == 'PASS' and len(validation['cache_controls']) == 2
cell = validation['cell']
for selected, identity in [('arm64-osx', c['host_compiler']), (triplet, c['compilers']['p2996'])]:
    p = A / 'buildtrees/detect_compiler' / ('stdout-'+selected+'.log')
    markers = dict(line.removeprefix('#COMPILER_').split('#',1) for line in text(p).splitlines() if line.startswith('#COMPILER_'))
    assert len(markers) == 9 and markers == cell['detectors'][selected]['markers']
    assert sha(p) == cell['detectors'][selected]['log_sha256']
    for language in ['C', 'CXX']:
        assert markers[language+'_PATH'] == identity[language] and markers[language+'_ID'] == identity['id'] and markers[language+'_VERSION'] == identity['version']
    if selected == 'arm64-osx':
        assert markers['C_HASH'] == markers['CXX_HASH'] == aliases[0]['sha1'] == aliases[1]['sha1']
    assert markers['HASH'] == hashlib.sha1((markers['C_HASH']+markers['CXX_HASH']).encode()).hexdigest()
for short, configuration in [('dbg', 'Debug'), ('rel', 'Release')]:
    base = A / 'buildtrees/fmt' / (triplet+'-'+short)
    row = cell['configurations'][configuration]
    control = next(r for r in validation['cache_controls'] if r['configuration'] == configuration)
    assert sha(base / 'CMakeCache.txt') == row['cache_sha256'] == control['sha256']
    assert control['path'] == str(run / triplet / 'buildtrees/fmt' / (triplet+'-'+short) / 'CMakeCache.txt')
    assert control['old_missing_exact_key'] and control['new_keys_confined_to_lines']
    lines = text(base / 'CMakeCache.txt').splitlines()
    for name, value in {'CMAKE_BUILD_TYPE': configuration, 'FMT_MODULE': 'OFF', 'BUILD_SHARED_LIBS': 'OFF', 'CMAKE_MAKE_PROGRAM': c['managed_tools']['ninja']['path']}.items():
        matches = [line.split('=',1)[1] for line in lines if line.startswith(name+':')]
        assert matches == [value] and row['cache'][name] == value
    compiler = base / 'CMakeFiles/4.4.4/CMakeCXXCompiler.cmake'
    assert sha(compiler) == row['compiler_sha256']
    for key, value in row['compiler'].items(): assert 'set('+key+' "'+value+'")' in text(compiler)
    assert ' -v -j1 install' in text(A / 'buildtrees/fmt' / ('install-'+triplet+'-'+short+'-out.log'))
    assert text(A / 'buildtrees/fmt' / ('install-'+triplet+'-'+short+'-err.log')) == ''
abi_path = A / 'buildtrees/fmt' / (triplet+'.vcpkg_abi_info.txt')
abi = dict(line.split(' ',1) for line in text(abi_path).splitlines())
assert abi == cell['abi']['entries'] and sha(abi_path) == cell['abi']['sha256']
assert {k:v for k,v in abi.items() if k.startswith('additional_file_')} == {'additional_file_'+str(i):row['sha256'] for i,row in enumerate(c['abi_inputs'][triplet])}
for name in ['MARKETPLACE_CPP_LANE', 'MARKETPLACE_P2996_PREFIX', 'PKG_CONFIG']:
    assert abi['ENV:'+name] == hashlib.sha256(q['environments']['p2996'][name].encode()).hexdigest()
assert abi['triplet_abi'] == '-'.join([c['inputs']['triplets/'+triplet+'.cmake'], c['inputs']['cmake/toolchains/vcpkg-macos-arm64.cmake'], cell['detectors'][triplet]['markers']['HASH']])
assert len(cell['installed']) == 67 and len(cell['libraries']) == 2
for lib in cell['libraries']:
    rel = str(Path(lib['path']).relative_to(run / triplet / 'installed'))
    matches = [r for r in cell['installed'] if r['path'] == rel]
    assert len(matches) == 1 and matches[0]['kind'] == 'file' and matches[0]['bytes'] > 0 and matches[0]['sha256'] == lib['sha256']

doc_add = 'The first P2996 static install returned 0, then receipt validation rejected the\nhost compiler alias spelling. The retained artifacts now pass read-only checks\nwith exact Apple `cc`/`c++` aliases and a cache parser confined to individual\nlines. A fresh four-triplet retry awaits independent repair review.\n'
assert text(A / 'candidate/vcpkg-toolchains.md') + doc_add == text(R / 'docs/vcpkg-toolchains.md')
oldplan = text(A / 'candidate/task_plan.md')
assert oldplan.count('| Prepared; review |') == 1
assert oldplan.replace('| Prepared; review |', '| First run failed; repair review |') == text(R / '.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md')
progress_add = '- R1 passed independent delta review. The admitted native run returned 1 after\n  its first fmt install returned 0; the host detector reports Apple `cc`/`c++`\n  aliases rather than `clang`/`clang++`. The other three installs did not run.\n  All 12 child PIDs ended, the lease was free, defaults matched, and shared\n  state/source preservation passed. Original files and logs remain retained.\n- Read-only diagnosis exposed a cache-key parser crossing blank lines. Exact\n  alias/version inputs and a parser limited to individual lines now pass both\n  actual cache controls, a CRLF key control and one complete inspection of the\n  retained static package. The original run remains failed; fresh execution\n  awaits independent repair review and capacity admission.\n'
assert text(A / 'candidate/progress.md') + progress_add == text(R / '.planning/2026-10-10-marketplace-macos-reflection-scaffold/progress.md')
static = load(E / 'native-repair-static.json'); scan = load(E / 'native-repair-secret-scan.json')
assert [r['returncode'] for r in static['commands']] == [0,0]
assert json.loads(static['commands'][1]['stdout'])['checks']['baseline'] == 19
assert len(scan['files']) == 152 and scan['raw']['returncode'] == 1 and scan['transformed']['returncode'] == 0
assert len(scan['dispositions']) == 4 and scan['supplemental_complete_token_files'] == []
for row in scan['dispositions']: assert row['rule'] == 'generic-api-key' and sha(R / row['path']) == row['sha256']
matched_scan = 0
for p,h in scan['files'].items():
    if str(R / p) in seen:
        assert seen[str(R / p)]['sha256'] == h
        matched_scan += 1
report = {'result':'PASS bounded failed-run closure and alias/cache-parser repair', 'findings':[],
    'checkout':str(R), 'branch':ref.removeprefix('refs/heads/'), 'head':expected['head'], 'common_git_directory':str(cg),
    'helper_sha256':expected['helper'], 'contract_sha256':expected['contract'], 'candidate_sha256':expected['candidate'],
    'original_review_sha256':expected['original_review'], 'retained_copies':68, 'historical_candidate_copies':6, 'source_copy_pairs':62,
    'diagnosis_source_copy_pairs':3, 'native_main_returncode':1, 'native_command_cases':expected_cases,
    'native_child_returncodes':[r['returncode'] for r in q['commands']], 'first_install_seconds':install['elapsed_seconds'],
    'main_failure':'Exact host compiler alias assertion; no accepted cells; other three installs and architecture checks never reached.',
    'recorded_final_preservation':True, 'diagnostic_returncode':1, 'diagnostic_failure':'CMAKE_BUILD_TYPE KeyError after 12 PID absence checks, free unchanged lease, default-after rc0 and same-file alias checks.',
    'aliases_verified':aliases, 'helper_changes':['CONTRACT_SHA','One cache regex preventing CR/LF in keys and types'], 'contract_changed_keys':changed_keys,
    'parent_repair_validation_returncode':0, 'recorded_cache_controls':2, 'recorded_crlf_key_control':'PASS', 'recorded_corrected_inspect_cell_calls':1,
    'retained_artifact_checks':{'detector_logs':2,'cache_files':2,'compiler_files':2,'abi_file':1,'abi_additional_entries':15,'recorded_library_rows':2},
    'parent_static_returncodes':[0,0], 'recorded_Claude_baseline_files':19,
    'scan':{'files_recorded':152,'raw_returncode':1,'disposition_returncode':0,'verified_digest_findings':4,'supplemental_complete_token_files':0,'already_scoped_hash_rows_matched':matched_scan},
    'reviewer_execution':'Filesystem hashing, text/JSON comparison and AST comparison only; no candidate functions executed.',
    'reviewer_native_commands':0,'reviewer_control_calls':0,'old_binding_battery_reaudits':0,'maintained_writes':0,'shared_writes':0,
    'limits':['Original native attempt and diagnostic remain FAIL; validation rc0 does not recast either.', 'Fresh retry needs its own admission and capacity; no claim for the other three installs, architecture checks, consumers, fresh model sessions, OCI or Claude runtime acceptance.', 'No current census, lease, profile, installed-package inventory or old source/tool binding battery was run.']}
(D / 'audit.json').write_text(json.dumps(report,indent=2)+'\n')
(D / 'input-hashes.json').write_text(json.dumps(seen,indent=2)+'\n')
print(json.dumps({'result':report['result'],'copy_files':68,'source_copy_pairs':62,'parent_native_returncode':1,'parent_diagnostic_returncode':1,'parent_repair_validation_returncode':0,'reviewer_native_commands':0,'reviewer_control_calls':0,'explicit_files_read':len(seen)}))
