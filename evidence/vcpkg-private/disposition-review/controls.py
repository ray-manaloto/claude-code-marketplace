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
E = R / 'evidence/vcpkg-private'
load = lambda p: json.loads(p.read_text())
source = Path(load(E / 'contract.json')['vcpkg_source'])
blob_hashes = {}
def digest(p):
    data = p.read_bytes()
    if p.is_relative_to(source):
        blob_hashes[str(p)] = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return hashlib.sha256(data).hexdigest()
frozen = load(D / 'frozen-inputs.json')
def check_frozen():
    for p, row in frozen['files'].items():
        assert digest(R / p) == row['sha256'], p
check_frozen()
def forbidden(*args, **kwargs):
    raise RuntimeError('native execution disabled for narrow disposition controls')
subprocess.Popen = subprocess.run = subprocess.call = subprocess.check_call = subprocess.check_output = forbidden
os.system = forbidden
contract = load(E / 'contract.json')
helper_path = R / 'dev/toolchains/vcpkg_private.py'
helper = ast.parse(helper_path.read_text())
inventory_path = R / 'dev/toolchains/p2996_install.py'
assert digest(inventory_path) == contract['inputs']['dev/toolchains/p2996_install.py']
inventory_ast = ast.parse(inventory_path.read_text())
def extract(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
def define(node, scope, filename):
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, 'exec'), scope)
scope = {'Path': Path, 'hashlib': hashlib, 'os': os, 'shutil': shutil, 'digest': digest, 'load': load}
define(extract(inventory_ast, 'prefix_inventory'), scope, str(inventory_path))
inventory = scope['prefix_inventory']
bound = load(R / contract['source_inventory'])
current = inventory(source)
assert current == bound
assert len(bound) == 17644 and all(r['kind'] in ('file', 'directory') for r in bound)
by_path = {r['path']: r for r in bound}
assert len(by_path) == len(bound)
proof = load(E / 'source-identity/proof.json')
assert proof['state'] == 'PASS' and proof['source'] == str(source)
assert proof['identity'] == [contract['vcpkg_commit'], contract['vcpkg_tree']]
for row in proof['commands']:
    assert row['returncode'] == 0
    for stream in ('stdout', 'stderr'):
        assert digest(E / 'source-identity' / (row['case'] + '.' + stream)) == row[stream + '_sha256']
assert (E / 'source-identity/identity.stdout').read_text().splitlines() == proof['identity']
assert (source / '.git/HEAD').read_text().strip() == contract['vcpkg_commit']
entries = (E / 'source-identity/tree.stdout').read_bytes().split(b'\0')
assert entries.pop() == b''
trie, tracked = {}, set()
for entry in entries:
    metadata, path_bytes = entry.split(b'\t', 1)
    mode, kind, oid = metadata.split(b' ')
    assert kind == b'blob' and mode in (b'100644', b'100755')
    parts = path_bytes.split(b'/')
    assert all(p not in (b'', b'.', b'..') for p in parts)
    path = path_bytes.decode('utf-8')
    assert path not in tracked
    tracked.add(path)
    row = by_path[path]
    assert row['kind'] == 'file' and blob_hashes[str(source / path)] == oid.decode(), path
    assert (int(row['mode'], 8) & 0o111 != 0) == (mode == b'100755'), path
    node = trie
    for part in parts[:-1]:
        node = node.setdefault(part, {})
        assert isinstance(node, dict)
    assert parts[-1] not in node
    node[parts[-1]] = (mode, bytes.fromhex(oid.decode()))

def tree_id(node):
    result = []
    for name, item in node.items():
        if isinstance(item, dict):
            result.append((name + b'/', b'40000 ' + name + b'\0' + tree_id(item)))
        else:
            mode, oid = item
            result.append((name, mode + b' ' + name + b'\0' + oid))
    body = b''.join(v for _, v in sorted(result))
    return hashlib.sha1(b'tree ' + str(len(body)).encode() + b'\0' + body).digest()
reconstructed = tree_id(trie).hex()
assert reconstructed == contract['vcpkg_tree']
assert len(tracked) == proof['tracked_files'] == 14337
files = {r['path'] for r in bound if r['kind'] == 'file'}
extras = files - tracked - {p for p in files if p.startswith('.git/')}
assert extras == set(proof['extra_files']) == {'vcpkg', 'vcpkg.disable-metrics'}
assert by_path['vcpkg']['sha256'] == contract['tools'][str(source / 'vcpkg')]
assert by_path['vcpkg.disable-metrics']['bytes'] == 0
assert by_path['vcpkg.disable-metrics']['sha256'] == hashlib.sha256(b'').hexdigest()
assert len(files) == proof['inventory_files'] == 14348
source_result = {'inventory_records': len(bound), 'inventory_files': len(files), 'tracked_blobs_and_executable_modes': len(tracked),
                 'reconstructed_git_tree': reconstructed, 'qualified_extra_files': sorted(extras), 'current_full_source_matches_bound_inventory': True,
                 'original_source_git_commands': 0, 'original_source_mutations': 0}

prior = E / 'initial-review/controls.py'
assert digest(prior) == '13a195307188296abff699371c340e98d09b5b472b28daf23452550030d0c851'
prior_ast = ast.parse(prior.read_text())
fixture_scope = {'hashlib': hashlib, 'zlib': zlib}
for name in ('git_object', 'make_source'):
    define(extract(prior_ast, name), fixture_scope, str(prior))
project = D / 'synthetic-project'
project.mkdir()
(project / 'vcpkg.json').write_text('{}\n')
scope['ROOT'] = project
scope['PRIVATE_NAMES'] = next(ast.literal_eval(n.value) for n in helper.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PRIVATE_NAMES' for t in n.targets))
define(extract(helper, 'prepare'), scope, str(helper_path))
rows = []
for case in ('clean', 'modified-tracked-bytes', 'modified-tracked-mode', 'unexpected-untracked', 'git-metadata', 'bootstrap-binary', 'metrics-marker'):
    root = D / 'source-controls' / case
    root.mkdir(parents=True)
    tiny_source, directory = root / 'source', root / 'operation'
    fixture_scope['make_source'](tiny_source)
    directory.mkdir()
    expected = inventory(tiny_source)
    inventory_name = case + '-inventory.json'
    (project / inventory_name).write_text(json.dumps(expected, indent=2) + '\n')
    if case == 'modified-tracked-bytes':
        (tiny_source / 'tracked.txt').write_bytes(b'unadmitted working-tree contents\n')
    elif case == 'modified-tracked-mode':
        (tiny_source / 'tracked.txt').chmod(0o755)
    elif case == 'unexpected-untracked':
        (tiny_source / 'unexpected.cmake').write_text('unadmitted extra input\n')
    elif case == 'git-metadata':
        (tiny_source / '.git/config').write_text('[core]\nfilemode = false\n')
    elif case == 'bootstrap-binary':
        (tiny_source / 'vcpkg').write_text('unadmitted executable contents\n')
    elif case == 'metrics-marker':
        (tiny_source / 'vcpkg.disable-metrics').write_text('unadmitted marker contents\n')
    before = inventory(tiny_source)
    error = None
    try:
        scope['prepare'](directory, {'vcpkg_source': str(tiny_source), 'downloads': [], 'source_inventory': inventory_name})
    except AssertionError as caught:
        error = str(caught)
    accepted = error is None
    assert accepted == (case == 'clean'), case
    assert inventory(tiny_source) == before
    assert (directory / 'vcpkg').exists() == accepted
    if accepted:
        assert inventory(directory / 'vcpkg') == expected
    else:
        assert error == 'vcpkg source inventory drift' and list(directory.iterdir()) == []
    rows.append({'case': case, 'accepted': accepted, 'expected_accepted': case == 'clean', 'copy_started': (directory / 'vcpkg').exists(), 'source_unchanged': True, 'error': error})
check_frozen()
result = {'result': 'PASS', 'finding': '12C1-01', 'disposition': 'FIXED', 'created_at': datetime.now(timezone.utc).isoformat(),
          'helper_sha256': digest(helper_path), 'contract_sha256': digest(E / 'contract.json'), 'candidate_sha256': digest(E / 'candidate.json'),
          'inventory_derivation': source_result, 'source_controls': rows, 'frozen_files_unchanged': len(frozen['files']),
          'native_tool_subprocesses': 0, 'main_or_protected_invocations': 0, 'earlier_wrapper_controls_reexecuted': 0}
(D / 'control-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
