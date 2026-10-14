"""Read-only Task14a1 receipt audit; hash only the 12 newly produced artifacts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shlex, stat, sys
ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = ROOT / 'evidence/p2996-sanitizer-repair'
D = Path(__file__).parent
watched = {}
checks = {}
def sha(b):
    return hashlib.sha256(b).hexdigest()
def read(p, expected=None):
    p = Path(p)
    b = p.read_bytes()
    h = sha(b)
    if expected is not None:
        assert h == expected, (str(p), h, expected)
    watched[str(p)] = h
    return b
def data(p, expected=None):
    return json.loads(read(p, expected))
def same(a, b, expected):
    assert read(a, expected) == read(b, expected), (str(a), str(b))
old = data(E / 'closure-candidate-before-whitespace.json', '7fe8ae293294ad409b176c06acbe9043c2e0842795a9f04e2ae65b7423da3a4d')
old_inputs = data(E / 'closure-inputs-before-whitespace.json', '0c560130d11e482facb7be2422e1d0efc2e169b5c5b67814fdf76cdd83515e0c')
same(D / 'original-closure-candidate.json', E / 'closure-candidate-before-whitespace.json', '7fe8ae293294ad409b176c06acbe9043c2e0842795a9f04e2ae65b7423da3a4d')
same(D / 'original-closure-inputs.json', E / 'closure-inputs-before-whitespace.json', '0c560130d11e482facb7be2422e1d0efc2e169b5c5b67814fdf76cdd83515e0c')
frozen = {r['source']: r['text'].encode() for r in old_inputs['files']}
for row in old_inputs['files']:
    assert sha(frozen[row['source']]) == row['sha256'] and len(frozen[row['source']]) == row['bytes']
for rel, h in old['files'].items():
    assert sha(frozen[str(ROOT / rel)]) == h
    if not rel.endswith('progress.md'):
        assert read(ROOT / rel, h) == frozen[str(ROOT / rel)]
checks['original_six_snapshots_and_five_file_freeze'] = True
contract = data(E / 'contract.json', old['contract_sha256'])
prep = data(E / 'candidate.json', old['preparation_candidate_sha256'])
review = data(E / 'pre-run-review.json', old['preparation_review_sha256'])
assert review['result'].startswith('PASS') and not review['findings']
assert contract['base_head'] == old['head'] == prep['head'] == '55a37282b117fca534a86fedcdbd5c8352405e23'
helper = ROOT / 'dev/toolchains/p2996_sanitizer_repair.py'
assert sha(read(helper)) == review['helper_sha256'] == prep['files'][str(helper.relative_to(ROOT))]
assert review['contract_sha256'] == old['contract_sha256']
assert read(ROOT / contract['repair']['patch'], contract['repair']['patch_sha256']) == frozen[str(ROOT / contract['repair']['patch'])]
recipe = data(E / 'recipes.json', contract['inputs']['evidence/p2996-sanitizer-repair/recipes.json'])
q = data(E / 'operation/qualification.json', old['native_qualification_sha256'])
close = data(E / 'operation/closure.json', old['native_closure_sha256'])
inv = data(E / 'artifact-inventory.json', old['artifact_inventory_sha256'])
admit = data(E / 'operation/admission.json', q['admission_sha256'])
execution = data(E / 'operation/native-execution.json', close['native_execution_sha256'])
launch = data(E / 'operation/native-launch.json')
texts = data(E / 'operation/text-receipts.json', close['text_receipts_sha256'])['files']
assert len(texts) == close['retained_text_files'] == 95
by_source = {}
for row in texts:
    b = read(row['source'], row['sha256'])
    assert b == row['text'].encode('utf-8') and len(b) == row['bytes']
    assert row['source'] not in by_source
    by_source[row['source']] = row
checks['exact_private_text_receipts'] = len(texts)
for label, path, target_key in [('operation','operation/copy-manifest.json','copy'), ('capacity','capacity-copy-manifest.json','destination'), ('preparation_review','preparation-review-copy-manifest.json','destination')]:
    manifest = data(E / path)
    rows = manifest if isinstance(manifest, list) else manifest['files']
    for row in rows:
        same(row['source'], ROOT / row[target_key], row['sha256'])
    checks[label + '_exact_copy_pairs'] = len(rows)
cap = data(E / 'capacity/capacity.json', admit['capacity_sha256'])
capexe = data(E / 'capacity/execution.json', admit['capacity_execution_sha256'])
assert cap['state'] == 'PASS' and capexe['returncode'] == 0
assert not cap['held_lease'] and not cap['native_operation_started']
assert capexe['script_sha256'] == cap['script_sha256'] == sha(read(E / 'capacity.py.source'))
same(capexe['argv'][3], E / 'capacity.py.source', capexe['script_sha256'])
assert datetime.fromisoformat(cap['recorded_at']) < datetime.fromisoformat(admit['recorded_at']) < datetime.fromisoformat(execution['started_at']) < datetime.fromisoformat(execution['finished_at']) < datetime.fromisoformat(close['recorded_at'])
for c in cap['commands']:
    assert c['returncode'] == 0 and 0 < c['elapsed_seconds'] < c['timeout_seconds']
    for l in c['logs']:
        read(l['path'], l['sha256'])
assert len(cap['commands']) == 7
checks['recorded_capacity_commands'] = 7
run = Path(admit['run_directory'])
assert run == Path(execution['argv'][-2]) and run.parent == Path.home() / '.local/state/marketplace-tool-foundation'
assert execution['argv'] == launch['argv'] == [sys.executable, '-E', '-B', str(helper), '--run-dir', str(run), '--build']
assert execution['returncode'] == close['native_returncode'] == 0
assert execution['helper_sha256'] == q['helper_sha256'] == admit['helper_sha256'] == review['helper_sha256']
assert admit['contract_sha256'] == old['contract_sha256'] and admit['candidate_sha256'] == old['preparation_candidate_sha256'] and admit['review_sha256'] == old['preparation_review_sha256']
assert execution['admission_sha256'] == q['admission_sha256']
assert {k:v for k,v in execution.items() if k in launch} == launch
lp = Path(execution['private_launch_directory'])
same(lp / 'launch.json', E / 'operation/native-launch.json', sha(read(E / 'operation/native-launch.json')))
same(lp / 'execution.json', E / 'operation/native-execution.json', close['native_execution_sha256'])
assert read(lp / 'stderr', execution['stderr_sha256']) == b''
stdout_lines = [json.loads(line) for line in read(lp / 'stdout', execution['stdout_sha256']).decode().splitlines()]
commands = {c['case']: c for c in q['commands']}
assert len(commands) == len(q['commands']) == close['command_count'] == 43
assert close['command_outcomes'] == [dict(case=c['case'],returncode=c['returncode']) for c in q['commands']]
assert stdout_lines[:-1] == [r for r in close['command_outcomes'] if r['case'] != 'original-clean']
assert stdout_lines[-1] == dict(state=q['state'],receipt=str(run / 'qualification.json'))
assert q['state'].startswith('PASS:') and close['state'] == 'CLOSED ' + q['state'] and close['error'] is None
assert inv['qualification_sha256'] == old['native_qualification_sha256']
assert execution['dispatch_sha256'] == by_source[str(Path(contract['repair']['preparation_directory']) / 'dispatch.py')]['sha256']
for c in q['commands']:
    expected = -15 if c['case'] == 'original-clean' else 86 if c['case'] in ('asan-memory','ubsan-overflow','asan-ubsan-memory','asan-ubsan-overflow') else 0
    assert c['returncode'] == expected
    if c['case'] != 'original-clean':
        assert c['expected_returncode'] == expected and c['elapsed_seconds'] < c['timeout_seconds']
    for l in c['logs']:
        assert l['sha256'] == by_source[l['path']]['sha256']
    if '-arch-' in c['case']:
        assert by_source[c['logs'][0]['path']]['text'] == 'arm64\n'
checks['native_commands_and_exact_log_bindings'] = dict(commands=43, logs=86, arm64_checks=10)
def log(case, stream):
    return by_source[str(run / (case + '.' + stream))]['text']
assert log('project-head','stdout').strip() == old['head']
assert log('default-before','stdout') == log('default-after','stdout') == read(ROOT / contract['default_profile']).decode()
assert not log('default-before','stderr') and not log('default-after','stderr')
checks['recorded_default_environment_parity'] = True
assert q['protected_state_unchanged'] is True and q['lease_released'] is True
assert close['protected_state_unchanged'] is True and close['lease_probe'] == dict(free=True,contents_unchanged=True)
assert close['processes'] == [dict(case=c['case'],pid=c['pid'],absent=True) for c in [dict(case='native-helper',pid=execution['pid']),*q['commands']]]
assert q['writer_census_before']['processes'] == q['writer_census_after']['processes'] == cap['writer_census']['processes']
assert q['writer_census_before']['lock_holders'] == q['writer_census_after']['lock_holders'] == []
checks['recorded_closure_only_no_live_probe'] = dict(owned_pids_absent=44, lease_free_unchanged=True, protected_unchanged=True)
assert cap['containers'] == admit['containers'] == log('docker-census','stdout').splitlines()
assert cap['docker_context'] == admit['docker_context'] == log('docker-context','stdout').strip()
for capacity in (cap, q['capacity']):
    assert capacity['cpus'] == 12 and capacity['free_bytes'] >= contract['disk_reserve_bytes']
    assert capacity['load'][0] <= 2 * capacity['cpus'] and capacity['total_cpu_percent'] <= 75 * capacity['cpus'] and capacity['container_cpu_percent'] <= 50 * capacity['cpus']
    assert capacity['admitted_editor_services'] == list(contract['editor_services']['processes'])
profile = '(version 1)\n(allow default)\n(deny file-write*)\n(allow file-write* (subpath ' + json.dumps(str(run)) + ') (literal "/dev/null"))\n(deny network*)\n'
assert by_source[str(run / 'private.sb')]['text'] == profile
assert sha(profile.encode()) == q['confinement']['profile_sha256']
assert q['confinement']['allowed_inherited_fds'] == [0,1,2,3]
sandbox = ['/usr/bin/sandbox-exec','-f',str(run / 'private.sb')]
objects = {str(Path(p).relative_to(recipe['build'])): str(run / 'objects' / Path(p).relative_to(recipe['build'])) for p in recipe['objects']}
assert len(objects) == 127
for variant in ('original','patched'):
    tree = run / variant
    compile_av = list(recipe['compile_argv'])
    for flag, value in [('-c',tree / contract['repair']['source_relative']),('-o',tree / 'procmaps.o'),('-MT',tree / 'procmaps.o'),('-MF',tree / 'procmaps.o.d')]:
        compile_av[compile_av.index(flag)+1] = str(value)
    compile_av += ['-I',str(Path(contract['repair']['source']).parent)]
    assert commands[variant+'-mapping-object']['argv'] == sandbox + compile_av
    link_av = [str(tree / 'procmaps.o') if x == recipe['mapping_object'] else objects.get(x,x) for x in recipe['link_argv']]
    link_av[link_av.index('-o')+1] = str(tree / 'libclang_rt.asan_osx_dynamic.dylib')
    assert commands[variant+'-runtime-link']['argv'] == sandbox + link_av
    assert commands[variant+'-runtime-sign']['argv'] == sandbox + recipe['codesign_argv'][:-1] + [str(tree / 'libclang_rt.asan_osx_dynamic.dylib')]
    assert sum(x.endswith('.o') for x in link_av) == 127
    assert sum(x == str(tree / 'procmaps.o') for x in link_av) == 1
patch_av = sandbox + ['/usr/bin/git','-C',str(run / 'patched'),'apply','--unidiff-zero']
for name, flags in [('check',['--check']),('apply',[]),('reverse-check',['--reverse','--check'])]:
    assert commands['patch-'+name]['argv'] == patch_av + flags + [str(ROOT / contract['repair']['patch'])]
checks['recorded_repair_argv_matches_prepared_recipes'] = dict(variants=2, unchanged_private_object_inputs_per_link=126, mapping_replacements=1, old_objects_rehashed=False)
prefix = Path(contract['prefixes']['p2996'])
loaded_cpp = {str(prefix / 'lib' / n) for n in ['libc++.1.0.dylib','libc++abi.1.0.dylib','libunwind.1.0.dylib']}
def loaded(case):
    return set(re.findall(r'^dyld\[\d+\]: <[0-9A-F-]+> (.+)$', log(case,'stderr'), re.M))
launcher_code = "import json,os,resource,sys;resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.execve(sys.argv[1],sys.argv[1:3],dict(os.environ,**json.loads(sys.argv[3]),DYLD_PRINT_LIBRARIES='1'))"
launcher = sandbox + [sys.executable,'-E','-B','-c',launcher_code]
original = commands['original-clean']
assert original['returncode'] == -15 and original['interrupted'] is True and original['timeout_seconds'] == 20 and original['expected_outcome'] == 'startup timeout'
assert 20 <= original['elapsed_seconds'] < 27 and log('original-clean','stdout') == ''
assert {p for p in loaded('original-clean') if '/libclang_rt.' in p} == {str(run / 'original/libclang_rt.asan_osx_dynamic.dylib')}
assert original['argv'] == launcher + [str(run / 'asan/witness'),'clean',json.dumps(contract['runtime_environment'] | {'DYLD_LIBRARY_PATH':str(run/'original')})]
checks['original_control'] = dict(returncode=-15,elapsed_seconds=original['elapsed_seconds'],stdout_empty=True,original_runtime_exact=True)
cases = []
for mode, settings in contract['sanitizers'].items():
    cell = run / mode
    core = commands[mode+'-core']['argv']
    link = commands[mode+'-link']['argv']
    assert core[:4] == link[:4] == sandbox + [contract['compilers']['p2996']['CXX']]
    assert core[-7:] == settings['flags'] + ['-freflection','-c',str(ROOT/'src/core.cpp'),'-o',str(cell/'core.o')] or core[-6:] == settings['flags'] + ['-freflection','-c',str(ROOT/'src/core.cpp'),'-o',str(cell/'core.o')]
    assert settings['flags'][0] in link and str(cell/'core.o') in link and str(ROOT/'dev/toolchains/sanitizer_witness.cpp') in link
    assert link[-2:] == ['-o',str(cell/'witness')]
    options = dict(contract['runtime_environment'])
    runtime = prefix / settings['runtimes'][0]
    if mode != 'ubsan':
        options['DYLD_LIBRARY_PATH'] = str(run/'patched')
        runtime = run / 'patched/libclang_rt.asan_osx_dynamic.dylib'
    assert set(q['cells'][mode]['runs']) == {'clean',*settings['errors']}
    for case in ['clean',*settings['errors']]:
        label = mode+'-'+case
        expected = 0 if case == 'clean' else 86
        row = commands[label]
        assert row['argv'] == launcher + [str(cell/'witness'),case,json.dumps(options)]
        assert row['returncode'] == row['expected_returncode'] == q['cells'][mode]['runs'][case]['expected_returncode'] == expected
        assert row['timeout_seconds'] == 20 and row['elapsed_seconds'] < 20
        assert log(label,'stdout') == 'reflection value=43, members=1\n'
        paths = loaded(label)
        assert paths == set(q['cells'][mode]['runs'][case]['loaded'])
        assert loaded_cpp <= paths and str(cell/'witness') in paths
        assert {p for p in paths if '/libclang_rt.' in p} == {str(runtime)}
        if case == 'clean':
            assert not any(t in log(label,'stderr') for t in ['ERROR: AddressSanitizer','runtime error:','SUMMARY:'])
        else:
            assert all(t in log(label,'stderr') for t in settings['errors'][case])
        cases.append(dict(case=label,returncode=expected,runtime=str(runtime),reflection_stdout=True))
checks['seven_runtime_cases'] = cases
artifact_by_kind = {r['kind']:r for r in inv['artifacts']}
assert len(artifact_by_kind) == len(inv['artifacts']) == 12
for variant in ('original','patched'):
    r = q['repair'][variant]
    assert r['path'] == artifact_by_kind[variant+'-runtime']['path'] and r['sha256'] == artifact_by_kind[variant+'-runtime']['sha256']
    assert r['source_sha256'] == artifact_by_kind[variant+'-source']['sha256'] == contract['repair']['before_sha256' if variant=='original' else 'after_sha256']
    assert r['object_sha256'] == artifact_by_kind[variant+'-object']['sha256']
for mode, cell in q['cells'].items():
    for kind, row in cell['artifacts'].items():
        assert row.items() <= artifact_by_kind[mode+'-'+kind].items()
all_dependencies = {}
post_hashes = []
for variant, dep in inv['source_dependencies'].items():
    depfile = by_source[str(run/variant/'procmaps.o.d')]
    assert depfile['sha256'] == dep['depfile_sha256']
    flat = depfile['text'].replace('\\\n',' ')
    target, words = flat.split(': ',1)
    assert target == str(run/variant/'procmaps.o')
    paths = shlex.split(words)
    assert paths == [r['path'] for r in dep['dependencies']]
    assert len(paths) == len(set(paths)) == (195 if variant=='original' else 224)
    new_external = []
    for row in dep['dependencies']:
        p = row['path']
        assert row['prebound'] == (p in contract['source_inputs'])
        assert row['private_source'] == (p == str(run/variant/contract['repair']['source_relative']))
        if row['prebound']:
            assert row['sha256'] == contract['source_inputs'][p]
        elif row['private_source']:
            assert row['sha256'] == artifact_by_kind[variant+'-source']['sha256']
        else:
            assert p.startswith('/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk/')
            new_external.append(p)
            read(p,row['sha256'])
            post_hashes.append(dict(path=p,sha256=row['sha256']))
    assert dep['new_external_paths'] == new_external
    all_dependencies[variant] = set(paths) - {str(run/variant/contract['repair']['source_relative'])}
assert len(post_hashes) == 28 and all_dependencies['original'] <= all_dependencies['patched']
assert len(all_dependencies['patched']-all_dependencies['original']) == 29
checks['dependency_disclosure'] = dict(original=195,patched=224,new_prebound_sdk_headers=1,post_observed_sdk_headers_rehashed=post_hashes,old_source_graph_rehashed=False)
static = data(E/'pre-artifact-static.json','bad8514cf2220daeec0d230d46c8f2cf6c708f04df4ea711b69c22c7acf93a5b')
assert len(static['commands']) == 1 and static['commands'][0]['returncode'] == 0
assert json.loads(static['commands'][0]['stdout'])['checks']['baseline'] == 19
checks['recorded_static_baseline'] = dict(returncode=0,original_files=19,rerun=False)
scan = data(E/'pre-artifact-secret-scan.json','84a4f1d11829da97d992f5ec17c0a440edae226fcc21a41c5971e8fa302c3a1d')
assert scan['raw']['returncode'] == 1 and scan['transformed']['returncode'] == 0 and scan['supplemental_complete_token_files'] == []
assert len(scan['dispositions']) == 10 and len(scan['files']) == 87
for row in scan['dispositions']:
    assert row['reason'] == 'Verified exact file-content digest'
    read(row['path'],row['sha256'])
frozen[str(E/'closure-inputs.json')] = read(E/'closure-inputs-before-whitespace.json')
for rel, h in scan['files'].items():
    path = str(ROOT / rel)
    b = frozen[path] if path in frozen else read(path)
    assert sha(b) == h, rel
read(scan['script'],scan['script_sha256'])
checks['recorded_scan'] = dict(raw_returncode=1,verified_digest_dispositions=10,transformed_returncode=0,complete_token_files=[],bound_text_inputs=87,rerun=False)
checks['retained_nonfatal_warnings'] = {c['case']:log(c['case'],'stderr') for c in q['commands'] if c['case'] in ('original-runtime-link','patched-runtime-link','asan-link')}
# All schema, text, provenance and outcome assertions precede the only new artifact read pass.
artifact_checks = []
for row in inv['artifacts']:
    p = Path(row['path'])
    assert p.is_relative_to(run) and stat.S_ISREG(p.lstat().st_mode)
    h = hashlib.sha256(); size = 0
    with p.open('rb') as f:
        while block := f.read(1024*1024):
            h.update(block); size += len(block)
    assert h.hexdigest() == row['sha256'] and size == row['bytes'], str(p)
    artifact_checks.append(row)
checks['new_artifacts_hashed_once'] = artifact_checks
# Repeat only text stability checks, never artifact bytes or old binary/source inventories.
for path, h in watched.items():
    assert sha(Path(path).read_bytes()) == h, ('text changed during comparison',path)
result = dict(result='PASS: private Task14a1 artifact and closure evidence',recorded_at=datetime.now(timezone.utc).isoformat(),head=old['head'],base_candidate_sha256=sha(read(E/'closure-candidate-before-whitespace.json')),checks=checks,watched_text_sha256=watched,limits=['No runtime/build/compiler/capacity/lease/scanner replay','No old binary or 127 old object rehash','No broad old source inventory replay','No fresh model session or Claude OCI acceptance','Private seven-case runtime witnesses only; no installed promotion, dependency instrumentation, full matrix or generic allocation proof'])
(D/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(result=result['result'],private_text_pairs=95,new_artifacts=12,new_artifact_bytes=sum(r['bytes'] for r in artifact_checks),post_observed_sdk_headers=28,commands=43,runtime_cases=7)))
