import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zlib

D = Path(__file__).parent.resolve()
R = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
load = lambda p: json.loads(p.read_text())
def digest(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
frozen = load(D / 'frozen-inputs.json')
def check_frozen():
    for p, row in frozen['files'].items():
        assert digest(R / p) == row['sha256'], p
check_frozen()
def forbidden(*args, **kwargs):
    raise RuntimeError('native subprocess disabled in focused reviewer controls')
subprocess.Popen = subprocess.run = subprocess.call = subprocess.check_call = subprocess.check_output = forbidden
os.system = forbidden
helper_path = R / 'dev/toolchains/vcpkg_private.py'
helper = ast.parse(helper_path.read_text())
contract = load(R / 'evidence/vcpkg-private/contract.json')
inventory_path = R / 'dev/toolchains/p2996_install.py'
assert digest(inventory_path) == contract['inputs']['dev/toolchains/p2996_install.py']
inventory_ast = ast.parse(inventory_path.read_text())
def extract(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
def define(node, scope, filename):
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, 'exec'), scope)
project = D / 'synthetic-project'
project.mkdir()
(project / 'vcpkg.json').write_text('{}\n')
private_names = next(ast.literal_eval(n.value) for n in helper.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PRIVATE_NAMES' for t in n.targets))
scope = {'Path': Path, 'hashlib': hashlib, 'os': os, 'shutil': shutil, 'digest': digest, 'ROOT': project, 'PRIVATE_NAMES': private_names}
define(extract(inventory_ast, 'prefix_inventory'), scope, str(inventory_path))
for name in ('prepare', 'private_environment', 'vcpkg_arguments'):
    define(extract(helper, name), scope, str(helper_path))
prepare, inventory = scope['prepare'], scope['prefix_inventory']

def git_object(source, kind, payload):
    raw = kind.encode() + b' ' + str(len(payload)).encode() + b'\0' + payload
    oid = hashlib.sha1(raw).hexdigest()
    path = source / '.git/objects' / oid[:2] / oid[2:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zlib.compress(raw))
    return oid

def make_source(path):
    path.mkdir()
    (path / '.git/objects/info').mkdir(parents=True)
    (path / '.git/refs').mkdir()
    tracked = b'pinned contents\n'
    (path / 'tracked.txt').write_bytes(tracked)
    (path / 'tracked.txt').chmod(0o644)
    blob = git_object(path, 'blob', tracked)
    tree = git_object(path, 'tree', b'100644 tracked.txt\0' + bytes.fromhex(blob))
    payload = ('tree ' + tree + '\nauthor Reviewer <reviewer@example.invalid> 0 +0000\ncommitter Reviewer <reviewer@example.invalid> 0 +0000\n\nsynthetic source\n').encode()
    commit = git_object(path, 'commit', payload)
    (path / '.git/HEAD').write_text(commit + '\n')
    (path / '.git/config').write_text('[core]\nrepositoryformatversion = 0\nbare = false\nfilemode = true\n')
    (path / 'vcpkg').write_bytes(b'qualified bootstrap executable placeholder\n')
    (path / 'vcpkg').chmod(0o755)
    (path / 'vcpkg.disable-metrics').write_bytes(b'')
    return commit, tree, blob

rows = []
for case in ('clean', 'modified-tracked-bytes', 'modified-tracked-mode', 'unexpected-untracked'):
    root = D / 'source-controls' / case
    root.mkdir(parents=True)
    source, directory = root / 'source', root / 'operation'
    commit, tree, blob = make_source(source)
    directory.mkdir()
    binary_sha = digest(source / 'vcpkg')
    if case == 'modified-tracked-bytes':
        (source / 'tracked.txt').write_bytes(b'unadmitted working-tree contents\n')
    elif case == 'modified-tracked-mode':
        (source / 'tracked.txt').chmod(0o755)
    elif case == 'unexpected-untracked':
        (source / 'unexpected.cmake').write_text('unadmitted extra input\n')
    before = inventory(source)
    prepared = prepare(directory, {'vcpkg_source': str(source), 'downloads': [], 'vcpkg_commit': commit, 'vcpkg_tree': tree})
    copied = directory / 'vcpkg'
    assert prepared == before == inventory(source) == inventory(copied)
    assert digest(source / 'vcpkg') == digest(copied / 'vcpkg') == binary_sha
    assert (copied / '.git/HEAD').read_text().strip() == commit
    decoded = zlib.decompress((copied / '.git/objects' / commit[:2] / commit[2:]).read_bytes())
    assert decoded.split(b'\0', 1)[1].splitlines()[0] == b'tree ' + tree.encode()
    tracked = (copied / 'tracked.txt').read_bytes()
    current_blob = hashlib.sha1(b'blob ' + str(len(tracked)).encode() + b'\0' + tracked).hexdigest()
    row = {'case': case, 'accepted': True, 'git_commit': commit, 'git_tree': tree, 'tracked_blob_matches': current_blob == blob,
           'tracked_mode_matches': copied.joinpath('tracked.txt').stat().st_mode & 0o777 == 0o644,
           'unexpected_file_copied': (copied / 'unexpected.cmake').exists(), 'bootstrap_binary_unchanged': True, 'source_unchanged': True}
    assert row['tracked_blob_matches'] == (case != 'modified-tracked-bytes')
    assert row['tracked_mode_matches'] == (case != 'modified-tracked-mode')
    assert row['unexpected_file_copied'] == (case == 'unexpected-untracked')
    rows.append(row)

run_node = extract(helper, 'run')
run_rows = []
for case, native_rc, expected, exception_kind, accepted in (
    ('success-zero', 0, 0, None, True), ('expected-denial', 73, 73, None, True),
    ('unexpected-success', 0, 73, None, False), ('wrong-denial-code', 74, 73, None, False),
    ('unexpected-nonzero', 73, 0, None, False), ('oserror', None, 0, 'OSError', False),
    ('timeout', None, 0, 'TimeoutExpired', False), ('interrupt', None, 0, 'KeyboardInterrupt', False),
):
    directory = D / 'wrapper-controls' / case
    directory.mkdir(parents=True)
    report, calls, saves = {'commands': []}, [], []
    expected_exception = {'OSError': OSError('synthetic'), 'TimeoutExpired': subprocess.TimeoutExpired('mock', 7), 'KeyboardInterrupt': KeyboardInterrupt('synthetic')}.get(exception_kind)
    def native(label, argv, timeout, descriptor):
        calls.append({'label': label, 'argv': argv, 'timeout': timeout, 'descriptor': descriptor})
        if expected_exception is not None:
            raise expected_exception
        (directory / (label + '.stdout')).write_text('mock output\n')
        report['commands'].append({'case': label, 'returncode': native_rc})
        assert native_rc == 0
        return 'mock output\n'
    context = {'native': native, 'report': report, 'directory': directory, 'save': lambda: saves.append(json.loads(json.dumps(report)))}
    define(run_node, context, str(helper_path))
    error = None
    try:
        value = context['run']('only-case', ['mock'], expected=expected, timeout=7, descriptor=91)
    except BaseException as caught:
        error = caught
    assert (error is None) == accepted, case
    assert len(calls) == 1 and calls[0]['descriptor'] == 91 and calls[0]['timeout'] == 7
    if expected_exception is not None:
        assert error is expected_exception
    if accepted:
        assert value == 'mock output\n' and len(saves) == 1
        assert report['commands'][-1]['expected_returncode'] == expected and report['commands'][-1]['timeout_seconds'] == 7
    else:
        assert not saves
    run_rows.append({'case': case, 'expected_acceptance': accepted, 'observed_acceptance': error is None, 'propagated': type(error).__name__ if error else None})
check_frozen()
result = {'result': 'PASS: focused controls established the source-identity gap', 'created_at': datetime.now(timezone.utc).isoformat(),
          'helper_sha256': digest(helper_path), 'contract_sha256': digest(R / 'evidence/vcpkg-private/contract.json'),
          'source_controls': rows, 'wrapper_controls': run_rows, 'frozen_files_unchanged': len(frozen['files']),
          'native_subprocesses': 0, 'main_or_protected_invocations': 0,
          'method': 'Executed the actual AST-extracted prepare, prefix_inventory and run functions with private synthetic files and a mocked native callback; Git objects constructed and decoded with hashlib/zlib, with no Git subprocess.'}
(D / 'control-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
