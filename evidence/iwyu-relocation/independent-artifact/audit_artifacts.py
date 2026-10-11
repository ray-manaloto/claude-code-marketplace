from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import time

D = Path(__file__).resolve().parent
R = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = R / 'evidence/iwyu-relocation'
O = Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/iwyu-relocation-20261011T162018Z')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
read = lambda case, stream='stdout': (E / 'operation' / (case + '.' + stream)).read_text()
def forbidden(*args, **kwargs):
    raise RuntimeError('Native subprocess forbidden in artifact audit')
subprocess.Popen = subprocess.run = forbidden
started = datetime.now(timezone.utc).isoformat()
clock = time.monotonic()
frozen = load(D / 'frozen-inputs.json')
for path, row in frozen['files'].items():
    assert sha(R / path) == row['sha256'], path
assert sha(E / 'operation-copy-manifest.json') == 'cf372ff50837c3cb1a365c8bacde45ccf948d96365cc4f839bf3663f1ff82f72'
assert sha(E / 'operation/qualification.json') == 'b53c74df526fd0a3f4980fd9d6054da6cee6443aad753a40441d7b70948b228e'
manifest = load(E / 'operation-copy-manifest.json')['files']
assert len(manifest) == 70 and len({r['source'] for r in manifest}) == len({r['path'] for r in manifest}) == 70
for row in manifest:
    source, copied = Path(row['source']), R / row['path']
    assert source.is_relative_to(O) or source.is_relative_to(Path(str(O) + '-invocation'))
    assert copied.is_relative_to(E / 'operation') or copied.is_relative_to(E / 'invocation')
    assert source.read_bytes() == copied.read_bytes()
    assert sha(source) == row['sha256'] and source.stat().st_size == row['bytes']
    copied.read_text()
q = load(E / 'operation/qualification.json')
admission, contract, preparation = [load(E / name) for name in ('admission.json','contract.json','pre-run-review.json')]
helper_sha = sha(R / 'dev/toolchains/iwyu_relocation.py')
assert helper_sha == q['helper_sha256'] == admission['helper_sha256'] == preparation['helper_sha256'] == '3ede4efb222e3510fc3e0c9f0644fdbce39bf888c34fefb02ab3afedd786eff4'
assert sha(E / 'contract.json') == admission['contract_sha256'] == preparation['contract_sha256'] == '5b0eb0bb0218c0394d6ac2e56c0b9a6c2709d95e9741d59da417df2887b6262e'
assert sha(E / 'pre-run-review.json') == admission['review_sha256'] == '5fd79e325b2c44a0bab9dc671dde41b879af415666ecf01976ed6b9f7d88f57e'
assert preparation['result'] == 'PASS' and preparation['findings'] == []
assert preparation['executed_checks']['controls']['header_trace_cases'] == preparation['executed_checks']['controls']['mocked_run_cases'] == 12
assert preparation['executed_checks']['controls']['returncode'] == 0
assert sha(E / 'admission.json') == q['admission_sha256'] and admission['run_directory'] == str(O)
assert admission['base_head'] == contract['base_head'] == '374beaa6239b9e2e4ecf2f998285ff64139f8d21'
assert sha(E / 'capacity-preflight.json') == admission['capacity_sha256']
for path, expected in contract['inputs'].items():
    assert sha(R / path) == expected, path
recipe = load(R / 'evidence/iwyu-reflection/source-recipe.json')
llvm, original = [Path(recipe['bindings'][k]) for k in ('LLVM_PREFIX','IWYU_PREFIX')]
moved = O / 'relocation/moved'
resources = moved / 'lib/clang/21'
binary = moved / 'bin/include-what-you-use'
assert q['moved_prefix'] == str(moved) and not os.path.lexists(O / 'relocation/staging')
assert (O / 'empty-resource').is_dir() and list((O / 'empty-resource').iterdir()) == []
assert sha(binary) == recipe['bindings']['IWYU_BINARY_SHA256']
assert binary.stat().st_ino != (original / 'bin/include-what-you-use').stat().st_ino
assert q['state'].startswith('PASS') and q['lease_released'] is True and q['protected_state_unchanged'] is True
assert 'error' not in q and 'preservation_error' not in q
assert q['staged_inventory'] == q['moved_inventory'] and len(q['moved_inventory']) == 350
assert len(q['original_resource_inventory']) == 320 and len(q['final_fixture']) == 5
built = load(R / 'evidence/iwyu-build/operation/qualification.json')['installed']
expected_inventory = {r['path']: r for r in built['inventory']}
for path in ('lib','lib/clang','lib/clang/21'):
    expected_inventory[path] = {'path':path, 'mode':'0o700', 'kind':'directory'}
for row in q['original_resource_inventory']:
    mapped = row | {'path':'lib/clang/21/' + row['path']}
    expected_inventory[mapped['path']] = mapped
assert {r['path']:r for r in q['moved_inventory']} == expected_inventory
expected_cases = ['project-head','default-before','named-profile','capacity-processes','docker-context','docker-census','docker-stats']
expected_cases += [phase + '-' + domain + '-' + action for phase in ['before'] for domain in ['iwyu','llvm'] for action in ['head','tree','status','diff']]
expected_cases += ['architecture','version','default-resource','explicit-resource','resource-witness','missing-resource','reflection','default-after']
expected_cases += [phase + '-' + domain + '-' + action for phase in ['after'] for domain in ['iwyu','llvm'] for action in ['head','tree','status','diff']]
assert [r['case'] for r in q['commands']] == expected_cases and len(expected_cases) == 31
commands = {r['case']:r for r in q['commands']}
inv = load(E / 'invocation/invocation.json')
assert inv['returncode'] == 0 and inv['helper_sha256'] == helper_sha and inv['admission_sha256'] == q['admission_sha256']
assert inv['cwd'] == str(R) and inv['argv'][1:] == ['-B',str(R/'dev/toolchains/iwyu_relocation.py'),'--run-dir',str(O)]
start_time = datetime.fromisoformat(inv['started_at'])
end_time = start_time + timedelta(seconds=inv['elapsed_seconds'])
previous = start_time
for row in q['commands']:
    expected = 1 if row['case'] in ('default-resource','explicit-resource','missing-resource') else 0
    assert row['returncode'] == row['expected_returncode'] == expected, row['case']
    t = datetime.fromisoformat(row['started_at'])
    assert previous <= t and t + timedelta(seconds=row['elapsed_seconds']) <= end_time
    previous = t
    assert row['pid'] > 0 and row['elapsed_seconds'] < row['timeout_seconds'] <= 60
    assert len(row['logs']) == 2
    for stream, log in zip(('stdout','stderr'), row['logs']):
        assert log['path'] == str(O / (row['case'] + '.' + stream))
        assert sha(Path(log['path'])) == log['sha256']
        assert sha(E / 'operation' / (row['case'] + '.' + stream)) == log['sha256']
for log in inv['logs']:
    assert sha(Path(log['path'])) == log['sha256']
    assert sha(E / 'invocation' / Path(log['path']).name) == log['sha256']
assert (E / 'invocation/stderr.log').read_text() == ''
output = [json.loads(line) for line in (E / 'invocation/stdout.log').read_text().splitlines()]
assert output[:-1] == [{'case':row['case'],'returncode':row['returncode']} for row in q['commands']]
assert output[-1] == {'state':q['state'],'receipt':str(O / 'qualification.json')}
assert read('project-head').strip() == contract['base_head']
assert read('architecture') == 'arm64\n' and read('architecture','stderr') == ''
assert commands['architecture']['argv'] == ['/usr/bin/lipo','-archs',str(binary)]
mise = load(R / 'evidence/mise-runtime/contract.json')['current_mise']['path']
base = [mise,'--no-hooks','-C',str(O/'cwd'),'-E','cpp-build','exec','--fresh-env','--no-deps','--']
assert commands['version']['argv'] == base + ['/usr/bin/env','DYLD_PRINT_LIBRARIES=1',str(binary),'--version']
assert read('version') == (R / 'evidence/iwyu-build/operation/version.stdout').read_text()
loaded = re.findall(r'^dyld\[([0-9]+)\]: <[^>]+> (/.+)$',read('version','stderr'),re.M)
assert loaded and {int(pid) for pid,path in loaded} == {commands['version']['pid']}
origins = [path for pid,path in loaded]
private_origins = [p for p in origins if not p.startswith(('/System/','/usr/lib/'))]
assert private_origins == [str(binary),str(llvm/'lib/libclang-cpp.dylib'),str(llvm/'lib/libLLVM.dylib')]
assert {'/usr/lib/libc++.1.dylib','/usr/lib/libc++abi.dylib','/usr/lib/system/libunwind.dylib'} <= set(origins)
assert str(original) not in read('version','stderr') and str(O/'relocation/staging') not in read('version','stderr')
raw = binary.read_bytes()
header = struct.unpack_from('<IiiIIIII', raw)
assert header[0] == 0xfeedfacf and header[1] == 0x100000c and header[3] == 2
position, dependencies, rpaths = 32, [], []
for index in range(header[4]):
    command, size = struct.unpack_from('<II',raw,position)
    assert size >= 8 and position + size <= len(raw)
    if command in (12,24,0x80000018,0x8000001f,0x80000023,0x8000001c):
        offset = struct.unpack_from('<I',raw,position+8)[0]
        value = raw[position+offset:position+size].split(b'\0',1)[0].decode()
        (rpaths if command == 0x8000001c else dependencies).append(value)
    position += size
assert position == 32 + header[5]
assert dependencies == ['@rpath/libclang-cpp.dylib','@rpath/libLLVM.dylib','/usr/lib/libc++.1.dylib','/usr/lib/libSystem.B.dylib']
assert rpaths == ['@loader_path/../lib',str(llvm/'lib')]
expand = lambda a: [s.replace('<private-09c-root>',str(O)) for s in a]
for case,key in (('default-resource','default_print_query'),('explicit-resource','override_print_query')):
    spec = recipe['relocation'][key]
    assert commands[case]['argv'] == base + expand(spec['argv'])
    assert read(case) == expand([spec['expected_stdout']])[0] and read(case,'stderr') == ''
witness = recipe['resource_witness']
assert commands['resource-witness']['argv'] == base + expand(witness['argv'])
assert (O/'fixtures/resource-witness.cc').read_text() == witness['content'] and read('resource-witness') == ''
trace_text = read('resource-witness','stderr')
assert not re.search(r': (?:fatal )?error:',trace_text)
headers = [Path(p) for p in re.findall(r'^\.+ (.+)$',trace_text,re.M)]
assert len(headers) == 9 and len(set(headers)) == 9
source_inventory = {r['path']:r for r in q['original_resource_inventory'] if r['kind'] == 'file'}
observed = []
for path in headers:
    assert path.is_absolute() and path == path.resolve() and path.is_relative_to(resources)
    expected = source_inventory[str(path.relative_to(resources))]['sha256']
    assert sha(path) == expected
    observed.append({'path':str(path),'sha256':expected})
assert observed == q['header_trace']
assert {resources/'include/stddef.h',resources/'include/__stddef_size_t.h'} <= set(headers)
negative = commands['resource-witness']['argv'].copy()
negative[negative.index('-resource-dir')+1] = str(O/'empty-resource')
assert commands['missing-resource']['argv'] == negative and read('missing-resource') == ''
assert "fatal error: 'stddef.h' file not found" in read('missing-resource','stderr')
analyze = expand(recipe['reflection_fixture']['analyze_argv'])
analyze[0], analyze[analyze.index('-resource-dir')+1] = str(binary),str(resources)
assert commands['reflection']['argv'] == base + analyze and read('reflection') == ''
assert read('reflection','stderr').strip() == '(' + str(O/'fixtures/reflection/main.cc') + ' has correct #includes/fwd-decls)'
for name in ('indirect.h','main.cc','value.h'):
    assert (O/'fixtures/reflection'/name).read_bytes() == (R/'evidence/iwyu-reflection/operation/fixtures/reflection'/name).read_bytes()
prior = load(R/'evidence/iwyu-reflection/operation/qualification.json')
prior_commands = {r['case']:r for r in prior['commands']}
for domain in ('iwyu','llvm'):
    for action in ('head','tree','status','diff'):
        reference = prior_commands['after-'+domain+'-'+action]
        for phase in ('before','after'):
            case = phase+'-'+domain+'-'+action
            assert commands[case]['argv'] == reference['argv']
            assert [l['sha256'] for l in commands[case]['logs']] == [l['sha256'] for l in reference['logs']]
for case in ('default-before','default-after'):
    assert read(case) == (R/'evidence/mise-runtime/operation/default-after.stdout').read_text()
    assert read(case,'stderr') == '' and commands[case]['argv'] == prior_commands['default-before']['argv']
assert read('named-profile') == (R/'evidence/mise-runtime/operation/cpp-build-profile.stdout').read_text()
assert read('named-profile','stderr') == ''
assert commands['named-profile']['argv'] == base + commands['default-before']['argv'][-2:]
assert read('docker-context').strip() == admission['docker_context'] and read('docker-census').splitlines() == admission['containers']
capacity = q['capacity']
assert capacity['active'] == [] and capacity['free_bytes'] >= contract['disk_reserve_bytes']
assert capacity['load'][0] <= 2*capacity['cpus'] and capacity['total_cpu_percent'] <= 75*capacity['cpus'] and capacity['container_cpu_percent'] <= 50*capacity['cpus']
statics = load(E/'post-operation-static.json')
assert len(statics) == 2 and all(r['returncode'] == 0 for r in statics)
assert json.loads(statics[1]['stdout'])['checks']['baseline'] == 19
baseline = load(R/'evidence/onboarding/baseline-files.json')['files']
assert len(baseline) == 19
for row in baseline:
    assert sha(R/row['path']) == row['sha256'] and (R/row['path']).stat().st_size == row['bytes']
for path,row in frozen['files'].items():
    assert sha(R/path) == row['sha256'],path
result = {'result':'PASS','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
 'elapsed_seconds':time.monotonic()-clock,'source_copy_pairs':len(manifest),'contract_inputs':len(contract['inputs']),
 'native_wrapper_returncode':inv['returncode'],'native_wrapper_elapsed_seconds':inv['elapsed_seconds'],
 'native_command_count':len(q['commands']),'native_log_hashes':62,'wrapper_log_hashes':2,
 'expected_nonzero_cases':['default-resource','explicit-resource','missing-resource'],
 'macho':{'path':str(binary),'sha256':sha(binary),'bytes':len(raw),'architecture':'arm64','dependencies':dependencies,'rpaths':rpaths},
 'dyld':{'pid':commands['version']['pid'],'image_records':len(loaded),'non_system_paths':private_origins,'system_cxx_runtime':['/usr/lib/libc++.1.dylib','/usr/lib/libc++abi.dylib','/usr/lib/system/libunwind.dylib']},
 'header_trace':observed,'source_parity_commands':16,'default_profile_parity':True,'lease_closure':'Recorded with-context closure plus wrapper exit 0; no current lease probe.',
 'native_capacity':capacity,'Claude_original_files':19,'retained_static_returncodes':[r['returncode'] for r in statics],
 'frozen_files_unchanged':len(frozen['files']),'native_replay_count':0,'protected_calls':0}
(D/'artifact-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':'PASS','source_copy_pairs':70,'native_commands':31,'native_logs':62,'headers':9,'original_files':19,'native_replay_count':0}))
