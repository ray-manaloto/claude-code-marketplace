from pathlib import Path
from datetime import UTC, datetime
import ast
import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
import time

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = ROOT / 'evidence/iwyu-source'
D = Path(__file__).parent
SOURCE = Path('/Users/rmanaloto/.local/state/marketplace-tool-foundation/iwyu-source-20261011T140625Z/source')
PIN = '791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3'
TREE = 'b793b517dd7a261da9e574572264b6d59ed4b7c4'
PYTHON = '/Users/rmanaloto/.local/share/mise/installs/python/3.14.8/bin/python3'

def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def load(path):
    return json.loads(Path(path).read_text())

def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': sha(path), 'bytes': path.stat().st_size}

def save(name, value):
    (D / name).write_text(json.dumps(value, indent=2) + '\n')

def bound(item):
    path = Path(item['path'])
    assert sha(path) == item['sha256'], str(path)
    if 'bytes' in item:
        assert path.stat().st_size == item['bytes'], str(path)

def stable_inputs():
    intake = load(D / 'intake.json')
    for path, digest in (intake['maintained'] | intake['evidence']).items():
        assert sha(ROOT / path) == digest, path
    for item in load(ROOT / 'evidence/onboarding/baseline-files.json')['files']:
        assert sha(ROOT / item['path']) == item['sha256']
        assert (ROOT / item['path']).stat().st_size == item['bytes']
    gitdir = Path((ROOT / '.git').read_text().strip().removeprefix('gitdir: '))
    assert (gitdir / 'HEAD').read_text() == 'ref: refs/heads/codex/marketplace-native-onboarding\n'
    common = (gitdir / (gitdir / 'commondir').read_text().strip()).resolve()
    assert common == Path('/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git')
    assert (common / 'refs/heads/codex/marketplace-native-onboarding').read_text().strip() == intake['head']

def source_inventory():
    result = {}
    for p in sorted(SOURCE.rglob('*')):
        item = {'mode': oct(stat.S_IMODE(p.lstat().st_mode))}
        if p.is_symlink():
            item.update(kind='symlink', target=os.readlink(p))
        elif p.is_file():
            item.update(kind='file', sha256=sha(p), bytes=p.stat().st_size)
        else:
            assert p.is_dir()
            item.update(kind='directory')
        result[str(p.relative_to(SOURCE))] = item
    return result

def protected():
    admitted = load(ROOT / 'evidence/core-p2996/admission.json')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT / 'dev/toolchains'))
    for name in ('gcc_install.py', 'gcc_bottles.py', 'mise_link_probe.py', 'p2996_install.py', 'vcpkg_register.py', 'p2996_reflection.py'):
        assert sha(ROOT / 'dev/toolchains' / name) == admitted['inputs']['dev/toolchains/' + name]
    from gcc_install import preserved
    from mise_link_probe import snapshot
    from p2996_install import prefix_inventory
    from vcpkg_register import install_entries
    registered = ROOT / 'evidence/p2996-registration'
    review = load(registered / 'registration-review.json')
    baseline_path = registered / 'independent-registration/post-state.json'
    assert sha(baseline_path) == review['post_state']['sha256']
    baseline = load(baseline_path)
    installed = ROOT / 'evidence/p2996-install'
    inventory_path = installed / 'independent-installation/post-install-inventory.json'
    assert sha(inventory_path) == review['retained_source_build_inventory']['inventory_sha256']
    assert sha(installed / 'operation/prefix-inventory.json') == review['prefix_inventory']['inventory_sha256']
    inventory = load(inventory_path)
    helper = ROOT / 'dev/toolchains/p2996_reflection.py'
    node = next(n for n in ast.walk(ast.parse(helper.read_text())) if isinstance(n, ast.FunctionDef) and n.name == 'protected')
    scope = {'baseline': baseline, 'inventory': inventory, 'prefix': Path(inventory['prefix']), 'evidence': installed,
             'load': load, 'preserved': preserved, 'snapshot': snapshot, 'install_entries': install_entries,
             'Path': Path, 'os': os, 'digest': sha, 'prefix_inventory': prefix_inventory}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(helper), 'exec'), scope)
    scope['protected']()
    return {'global_files': len(baseline['protected']['global_files']), 'packages': len(baseline['protected']['packages']),
            'glib_files': len(baseline['protected']['glib_files']), 'directories': {k: len(v) for k, v in baseline['directories'].items()},
            'install_entries': len(baseline['install_entries']), 'source_build_records': len(inventory['records']),
            'prefix_entries': len(load(installed / 'operation/prefix-inventory.json'))}

def audit():
    report = {'state': 'RUNNING', 'started_at': datetime.now(UTC).isoformat(), 'native_subprocesses': 0}
    try:
        stable_inputs()
        counts = {}
        for name in ('input-manifest.json', 'source-manifest.json', 'preparation-manifest.json'):
            manifest = load(E / name)
            for item in manifest['files']:
                for path in (Path(item['source']), ROOT / item['path']):
                    assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], str(path)
            for item in manifest.get('private_binary_logs', []):
                bound(item)
            counts[name] = len(manifest['files'])
        acquisition = load(E / 'operation/acquisition.json')
        assert acquisition['pin'] == PIN and acquisition['tree'] == TREE and acquisition['source'] == str(SOURCE)
        assert acquisition['helper_sha256'] == sha(ROOT / 'dev/toolchains/iwyu_source.py')
        assert acquisition['state'] == 'PASS: exact IWYU source only; no configure, build or installation'
        assert len(acquisition['commands']) == 10
        assert [c['case'] for c in acquisition['commands']] == ['git-version','init','remote','fetch','checkout','head','tree','status','connectivity','blob-inventory']
        for command in acquisition['commands']:
            assert command['returncode'] == 0 and command['argv'][0] == '/usr/bin/git'
            for item in command['logs']:
                bound(item)
        for name in ('inputs/invocation.json', 'operation/invocation.json'):
            wrapper = load(E / name)
            assert wrapper['returncode'] == 0
            assert wrapper['argv'][1:9] == ['--config','/Users/rmanaloto/.config/fnox/config.toml','--profile','codex_research','--no-defaults','--no-daemon','--non-interactive','exec']
            for item in wrapper['logs']:
                bound(item)
        api = load(E / 'inputs/acquisition.json')
        assert api['pin'] == PIN and api['tree'] == TREE
        for item in api['records']:
            assert item['http_status'] == 200
            bound(item)
        assert load(E / 'inputs/commit.json')['sha'] == PIN
        assert load(E / 'inputs/commit.json')['tree']['sha'] == TREE
        assert load(E / 'inputs/root-tree.json')['sha'] == TREE
        assert (SOURCE / '.git/HEAD').read_text().strip() == PIN
        rows = acquisition['verified_files']
        assert len(rows) == 854 and len({r['path'] for r in rows}) == 854
        bypath = {r['path']: r for r in rows}
        logged = {}
        raw_inventory = Path(acquisition['commands'][-1]['logs'][0]['path']).read_bytes()
        assert raw_inventory.endswith(b'\0')
        for raw in raw_inventory[:-1].split(b'\0'):
            meta, name = raw.split(b'\t', 1)
            mode, kind, blob = meta.decode().split()
            assert kind == 'blob'
            logged[name.decode()] = (mode, blob)
        assert set(logged) == set(bypath)
        nodes = {}
        for item in rows:
            p = SOURCE / item['path']
            assert logged[item['path']] == (item['mode'], item['blob'])
            if item['mode'] == '120000':
                assert p.is_symlink()
                data = os.readlink(p).encode()
            else:
                assert p.is_file() and not p.is_symlink()
                assert bool(p.stat().st_mode & 0o111) == (item['mode'] == '100755')
                data = p.read_bytes()
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
            assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == item['blob']
            cursor = nodes
            parts = item['path'].split('/')
            for part in parts[:-1]:
                cursor = cursor.setdefault(part, {})
            cursor[parts[-1]] = (item['mode'], item['blob'])
        def tree_digest(node):
            ordered = sorted(node.items(), key=lambda row: (row[0] + ('/' if isinstance(row[1], dict) else '')).encode())
            payload = b''
            for name, value in ordered:
                mode, blob = ('40000', tree_digest(value)) if isinstance(value, dict) else value
                payload += mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(blob)
            return hashlib.sha1(b'tree ' + str(len(payload)).encode() + b'\0' + payload).hexdigest()
        assert tree_digest(nodes) == TREE
        actual_files = {str(p.relative_to(SOURCE)) for p in SOURCE.rglob('*') if '.git' not in p.relative_to(SOURCE).parts and (p.is_file() or p.is_symlink())}
        assert actual_files == set(bypath)
        source_before = source_inventory()
        save('source-before.json', source_before)
        references = load(E / 'source-reference-validation.json')['references']
        assert len(references) == 10
        for item in references:
            bound(item)
            lines = Path(item['path']).read_text().splitlines()
            assert all(1 <= a <= b <= len(lines) for a, b in item['line_ranges'])
        prerequisite = load(E / 'native-prerequisite.json')
        for name in ('configuration_receipt','build_receipt','cache'):
            bound(prerequisite['bootstrap'][name])
        for tool in prerequisite['bootstrap']['tools'].values():
            assert sha(tool.get('path', tool.get('resolved_path'))) == tool['sha256']
        sdk = prerequisite['bootstrap']['sdk']
        assert sha(Path(sdk['path']) / 'SDKSettings.json') == sdk['settings_sha256']
        cache_lines = Path(prerequisite['bootstrap']['cache']['path']).read_text().splitlines()
        assert all(cache_lines[row['line'] - 1] == row['text'] for row in prerequisite['bootstrap']['selected_cache_rows'])
        resource = load(E / 'resource-source-contract.json')
        assert resource['acquisition']['sha256'] == sha(E / 'operation/acquisition.json')
        for item in resource['source_bindings']:
            assert all(item[k] == bypath[item['path']][k] for k in ('sha256','blob','bytes'))
        parent_controls = load(E / 'preparation/preparation-controls.json')
        assert parent_controls['cache_sha256'] == sha(ROOT / 'dev/toolchains/iwyu-bootstrap.cmake')
        assert parent_controls['helper_sha256'] == sha(ROOT / 'dev/toolchains/iwyu_source.py')
        assert len(parent_controls['commands']) == 11
        for command in parent_controls['commands']:
            assert command['returncode'] == command['expected_returncode']
            for item in command.get('logs', []):
                bound(item)
            if 'logs' in command:
                output = ''.join(Path(item['path']).read_text() for item in command['logs'])
                assert command['expected_diagnostic'] in output
        gates = load(E / 'pre-review-static-checks.json')
        assert len(gates) == 2 and all(c['returncode'] == 0 for c in gates)
        assert json.loads(gates[1]['stdout'])['checks']['baseline'] == 19
        stable_inputs()
        report.update(state='PASS', source_pin=PIN, source_tree=TREE, verified_blobs=854,
                      independently_reconstructed_tree=TREE, no_extra_source_files=True,
                      original_copy_pairs=counts, original_git_exits=[0]*10, original_fnox_wrapper_exits=[0,0],
                      source_references=len(references), resource_bindings=len(resource['source_bindings']),
                      retained_parent_control_exits=[c['returncode'] for c in parent_controls['commands']],
                      retained_static_gate_exits=[0,0], original_Claude_files=19,
                      source_inventory=record(D / 'source-before.json'), findings=[])
    except BaseException as error:
        report.update(state='FAIL', error=repr(error))
        raise
    finally:
        report['completed_at'] = datetime.now(UTC).isoformat()
        save('input-audit.json', report)
    print(json.dumps({'phase':'audit', 'state':report['state'], 'verified_blobs':854, 'native_subprocesses':0}))

def controls():
    assert load(D / 'input-audit.json')['state'] == 'PASS'
    report = {'state':'RUNNING', 'started_at':datetime.now(UTC).isoformat(), 'commands':[]}
    stable_inputs()
    report['preservation_before'] = protected()
    assert source_inventory() == load(D / 'source-before.json')
    config = load(E / 'native-prerequisite.json')['bootstrap']
    cmake = config['tools']['cmake']['resolved_path']
    cache = ROOT / 'dev/toolchains/iwyu-bootstrap.cmake'
    helper = ROOT / 'dev/toolchains/iwyu_source.py'
    llvm_prefix = Path(config['cache']['path']).parent.parent / 'prefix'
    install = D / 'uncreated-install'
    existing = D / 'existing-prefix'
    existing.mkdir()
    temp = D / 'tmp'
    temp.mkdir()
    env = {'PATH':'/usr/bin:/bin:/usr/sbin:/sbin', 'HOME':os.environ['HOME'], 'LANG':'C', 'LC_ALL':'C',
           'TMPDIR':str(temp), 'PYTHONDONTWRITEBYTECODE':'1', 'MARKETPLACE_CPP_LANE':'tools-only',
           'MARKETPLACE_IWYU_CC':config['tools']['cc']['path'], 'MARKETPLACE_IWYU_CXX':config['tools']['cxx']['path'],
           'MARKETPLACE_IWYU_SDK':config['sdk']['path'], 'MARKETPLACE_IWYU_NINJA':config['tools']['ninja']['path'],
           'MARKETPLACE_IWYU_LLVM_PREFIX':str(llvm_prefix), 'MARKETPLACE_IWYU_PREFIX':str(install)}
    expected = {'CMAKE_C_COMPILER':env['MARKETPLACE_IWYU_CC'], 'CMAKE_CXX_COMPILER':env['MARKETPLACE_IWYU_CXX'],
                'CMAKE_OSX_SYSROOT':env['MARKETPLACE_IWYU_SDK'], 'CMAKE_MAKE_PROGRAM':env['MARKETPLACE_IWYU_NINJA'],
                'CMAKE_INSTALL_PREFIX':str(install), 'CMAKE_BUILD_TYPE':'Release', 'CMAKE_OSX_ARCHITECTURES':'arm64',
                'CMAKE_OSX_DEPLOYMENT_TARGET':'27.0', 'CMAKE_EXPORT_COMPILE_COMMANDS':'ON',
                'LLVM_DIR':str(llvm_prefix/'lib/cmake/llvm'), 'Clang_DIR':str(llvm_prefix/'lib/cmake/clang'),
                'LLVM_ENABLE_LIBCXX':'OFF', 'LLVM_STATIC_LINK_CXX_STDLIB':'OFF', 'IWYU_LINK_CLANG_DYLIB':'ON',
                'IWYU_RESOURCE_RELATIVE_TO':'clang', 'LLVM_PARALLEL_COMPILE_JOBS':'1', 'LLVM_PARALLEL_LINK_JOBS':'1',
                'CMAKE_DISABLE_FIND_PACKAGE_Python3':'TRUE', 'CMAKE_INSTALL_RPATH':'', 'CMAKE_BUILD_RPATH':'',
                'CLANG_RESOURCE_DIR':'', 'IWYU_RESOURCE_DIR':''}
    witness = D/'cache-witness.cmake'
    text = f'include("{cache}")\n'
    for name, value in expected.items():
        text += f'if(NOT "${{{name}}}" STREQUAL [==[{value}]==])\n  message(FATAL_ERROR "Unexpected {name}")\nendif()\n'
    text += f'if(EXISTS "{install}")\n  message(FATAL_ERROR "Script mode created install prefix")\nendif()\nmessage(STATUS "IWYU cache values verified without project configure")\n'
    witness.write_text(text)
    save('control-inputs.json', {'cmake':record(cmake), 'helper':record(helper), 'cache':record(cache),
                                'environment':env, 'expected_cache_values':expected, 'witness':record(witness)})
    def run(case, argv, expected_rc, diagnostic, overrides=None):
        row = {'case':case, 'argv':list(map(str,argv)), 'expected_returncode':expected_rc,
               'expected_diagnostic':diagnostic, 'environment_overrides':overrides or {}, 'started_at':datetime.now(UTC).isoformat()}
        report['commands'].append(row)
        logs = [D/(case+suffix) for suffix in ('.stdout','.stderr')]
        with logs[0].open('wb') as out, logs[1].open('wb') as err:
            process = subprocess.Popen(row['argv'], cwd=D, env=env|(overrides or {}), stdin=subprocess.DEVNULL,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                process.wait(timeout=30)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                row['interrupted'] = True
                for sig in (signal.SIGTERM,signal.SIGKILL):
                    try: os.killpg(process.pid,sig)
                    except ProcessLookupError: pass
                    if sig == signal.SIGTERM:
                        try: process.wait(timeout=5)
                        except subprocess.TimeoutExpired: pass
                process.wait()
                raise
            finally:
                row.update(returncode=process.returncode,logs=[record(p) for p in logs],completed_at=datetime.now(UTC).isoformat())
                save('controls.json',report)
        assert process.returncode == expected_rc, (case,process.returncode)
        assert diagnostic in ''.join(p.read_text() for p in logs), case
        print(json.dumps({'case':case,'returncode':process.returncode}),flush=True)
    try:
        run('positive',[cmake,'-P',witness],0,'IWYU cache values verified')
        run('wrong-lane',[cmake,'-P',cache],1,'Select the isolated cpp-build',{'MARKETPLACE_CPP_LANE':'p2996'})
        run('dirty-flags',[cmake,'-P',cache],1,'Inherited CXXFLAGS',{'CXXFLAGS':'-freflection'})
        run('missing-tool',[cmake,'-P',cache],1,'input does not exist: NINJA',{'MARKETPLACE_IWYU_NINJA':str(D/'absent-ninja')})
        run('existing-prefix',[cmake,'-P',cache],1,'new separate private install prefix',{'MARKETPLACE_IWYU_PREFIX':str(existing)})
        run('nested-prefix',[cmake,'-P',cache],1,'new separate private install prefix',{'MARKETPLACE_IWYU_PREFIX':str(llvm_prefix/'uncreated-iwyu-review')})
        run('rpath-override',[cmake,'-DCMAKE_INSTALL_RPATH=/unrelated','-P',cache],1,'unset CMAKE_INSTALL_RPATH')
        run('toolchain-override',[cmake,'-DCMAKE_TOOLCHAIN_FILE=/unrelated','-P',cache],1,'unset CMAKE_TOOLCHAIN_FILE')
        run('help',[PYTHON,'-B',helper,'--help'],0,'--directory DIRECTORY')
        run('relative-source',[PYTHON,'-B',helper,'--directory','relative'],2,'absolute normalized path')
        run('project-source',[PYTHON,'-B',helper,'--directory',ROOT/'iwyu-private-probe'],2,'outside the marketplace worktree')
        assert len(report['commands']) == 11
        assert not install.exists() and not (D/'relative').exists() and not (ROOT/'iwyu-private-probe').exists()
        assert not (llvm_prefix/'uncreated-iwyu-review').exists()
        assert not (D/'CMakeCache.txt').exists() and not (D/'CMakeFiles').exists()
        report.update(state='PASS', install_prefix_absent=True, project_configure_compiler_build_install_count=0)
    except BaseException as error:
        report.update(state='FAIL',error=repr(error))
        raise
    finally:
        try:
            stable_inputs()
            report['preservation_after'] = protected()
            assert report['preservation_before'] == report['preservation_after']
            assert source_inventory() == load(D/'source-before.json')
            report['source_and_existing_state_unchanged'] = True
        except BaseException as error:
            report.update(state='FAIL', preservation_error=repr(error))
            raise
        finally:
            report['completed_at'] = datetime.now(UTC).isoformat()
            save('controls.json',report)
    print(json.dumps({'phase':'controls','state':report['state'],'commands':len(report['commands']),'preserved':True}))

if __name__ == '__main__':
    {'audit':audit,'controls':controls}[sys.argv[1]]()
