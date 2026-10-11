"""Private fixtures exercising only new math-application guards; no subprocesses."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
PRIVATE = Path(__file__).resolve().parent
TARGET = ROOT / 'dev/toolchains/p2996_math_apply.py'
SHA = '974918e2f048dcd389201e84a8781293fa34396e7d20cc05705447bd9b37b6c2'
FILES = ('clang/lib/Headers/float.h', 'libcxx/include/float.h')
prior = json.loads((ROOT / 'evidence/p2996-sdk-compatibility/operation/qualification.json').read_text())
SDK_FILES = tuple(row['path'] for row in prior['proposal']['adaptation']['files'])
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(TARGET) == SHA
tree = ast.parse(TARGET.read_text())
results = []
counter = 0


def workspace():
    global counter
    counter += 1
    p = PRIVATE / 'guard-fixtures' / str(counter)
    p.mkdir(parents=True)
    assert p.is_relative_to(PRIVATE)
    return p


def function(name, ns):
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(TARGET), 'exec'), ns)
    return ns[name]


def check(name, action, rejects=False):
    try:
        action()
    except AssertionError:
        assert rejects, name + ' unexpectedly rejected'
        result = 'rejected'
    else:
        assert not rejects, name + ' unexpectedly accepted'
        result = 'accepted'
    results.append({'case': name, 'result': result, 'passed': True})
    (PRIVATE / 'guard-controls.json').write_text(json.dumps({'helper_sha256': SHA, 'controls': results}, indent=2) + '\n')


def source_fixture(patched=False):
    directory = workspace()
    source = directory / 'source'
    source.mkdir()
    rows = []
    for name in (*SDK_FILES, *FILES):
        p = source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        before, after = ('before:' + name).encode(), ('after:' + name).encode()
        p.write_bytes(after if patched or name in SDK_FILES else before)
        rows.append({'path': name, 'before_sha256': hashlib.sha256(before).hexdigest(),
                     'after_sha256': hashlib.sha256(after).hexdigest()})
    model = {'head': 'fixture-head', 'tree': 'fixture-tree', 'diff': b'after-diff' if patched else b'prior-diff',
             'status': sorted(' M ' + n for n in (*SDK_FILES, *(FILES if patched else ())))}
    def run(label, argv):
        if label.endswith('-diff'):
            (directory / (label + '.stdout')).write_bytes(model['diff'])
            return model['diff'].decode()
        key = label.rsplit('-', 1)[-1]
        return '\n'.join(model[key]) + '\n' if key == 'status' else model[key] + '\n'
    ns = {'Path': Path, 'digest': digest, 'directory': directory, 'source': source,
          'configuration': {'pin': 'fixture-head', 'tree': 'fixture-tree'},
          'git': ['fixture-git'], 'run': run, 'SDK_FILES': SDK_FILES, 'FILES': FILES,
          'prior': {'proposal': {'adaptation': {'files': rows[:len(SDK_FILES)]}}},
          'adaptation': {'files': rows[len(SDK_FILES):], 'prior_source_diff_sha256': hashlib.sha256(b'prior-diff').hexdigest()}}
    return ns, model, function('source_state', ns)


for stage, patched in [('source-before', False), ('source-immediate', False), ('source-after', True)]:
    ns, model, f = source_fixture(patched)
    check(stage + '-valid', lambda f=f, stage=stage, patched=patched: f(stage, patched))

for name, key, value in [('head-drift', 'head', 'other-head'), ('tree-drift', 'tree', 'other-tree'),
                         ('extra-untracked', 'status', sorted([' M ' + n for n in SDK_FILES] + ['?? extra'])),
                         ('staged-edit', 'status', sorted(['M  ' + SDK_FILES[0]] + [' M ' + n for n in SDK_FILES[1:]])),
                         ('prior-diff-drift', 'diff', b'changed-diff')]:
    ns, model, f = source_fixture()
    model[key] = value
    check(name, lambda f=f: f('source-immediate'), True)

for name, relative, patched in [('prior-rdf-postimage-drift', SDK_FILES[0], False),
                                ('math-preimage-drift', FILES[0], False),
                                ('math-postimage-drift', FILES[1], True)]:
    ns, model, f = source_fixture(patched)
    (ns['source'] / relative).write_bytes(b'drift')
    check(name, lambda f=f, patched=patched: f('source-after' if patched else 'source-immediate', patched), True)

ns, model, f = source_fixture()
target = ns['source'] / FILES[0]
outside = ns['directory'] / 'outside-header'
outside.write_bytes(target.read_bytes())
target.unlink()
target.symlink_to(outside)
check('source-symlink-escape', lambda: f('source-immediate'), True)


def input_fixture():
    directory = workspace()
    root = directory / 'root'
    root.mkdir()
    receipt, helper = root / 'receipt.json', root / 'dep.py'
    receipt.write_bytes(b'receipt')
    helper.write_bytes(b'helper')
    ns = {'ROOT': root, 'Path': Path, '__file__': str(root / 'apply.py'), 'digest': digest,
          'report': {'proposal': {'receipts': {'receipt.json': digest(receipt)}, 'helpers': {'dep.py': digest(helper)}}},
          'protected': lambda: None}
    return receipt, helper, function('inputs', ns)


receipt, helper, f = input_fixture()
check('input-bindings-valid', f)
for name, index in [('bound-receipt-drift', 0), ('bound-helper-drift', 1)]:
    receipt, helper, f = input_fixture()
    (receipt, helper)[index].write_bytes(b'drift')
    check(name, f, True)


def protected_fixture():
    directory = workspace()
    source = directory / 'source'
    source.mkdir()
    headers = {}
    for name in (*FILES, 'libcxx/include/clamp.h'):
        p = source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(name.encode())
        headers[str(p)] = digest(p)
    log, deps, executable, link, missing = [directory / n for n in ('.ninja_log', '.ninja_deps', 'clang-21', 'clang', 'clangd')]
    for p in [log, deps, executable]:
        p.write_bytes(p.name.encode())
    link.symlink_to(executable)
    rows = []
    for p in [log, deps, link, missing]:
        row = {'path': str(p), 'lexists': os.path.lexists(p), 'exists': p.exists()}
        if p.exists():
            row.update(sha256=digest(p), resolved_path=str(p.resolve()))
        if p.is_symlink():
            row['symlink_target'] = os.readlink(p)
        rows.append(row)
    ns = {'Path': Path, 'os': os, 'digest': digest, 'FILES': FILES, 'source': source,
          'baseline': {'protected': {}, 'directories': {}, 'install_entries': []},
          'preserved': lambda _: None, 'snapshot': lambda _: {}, 'install_entries': lambda _: [],
          'retained': {'source_generated': headers, 'inventory_records': rows}}
    return ns, {'log': log, 'deps': deps, 'executable': executable, 'link': link, 'missing': missing,
                'clamp': source / 'libcxx/include/clamp.h'}, function('protected', ns)


ns, files, f = protected_fixture()
check('retained-inventory-valid', f)
for name, key in [('ninja-log-drift', 'log'), ('ninja-deps-drift', 'deps'), ('unedited-header-drift', 'clamp'),
                  ('missing-artifact-created', 'missing')]:
    ns, files, f = protected_fixture()
    files[key].write_bytes(b'drift')
    check(name, f, True)
ns, files, f = protected_fixture()
files['log'].unlink()
check('recorded-artifact-removed', f, True)
ns, files, f = protected_fixture()
other = files['executable'].with_name('other-clang')
other.write_bytes(files['executable'].read_bytes())
files['link'].unlink()
files['link'].symlink_to(other)
check('recorded-symlink-retargeted', f, True)
ns, files, f = protected_fixture()
(ns['source'] / FILES[0]).write_bytes(b'allowed-source-edit-checked-by-source-state')
check('protected-excludes-only-admitted-source-header', f)


admission_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Assert) and 147 <= n.lineno <= 157]
assert len(admission_nodes) == 8
admission_code = compile(ast.Module(body=sorted(admission_nodes, key=lambda n: n.lineno), type_ignores=[]), str(TARGET), 'exec')


def admission_fixture():
    directory = workspace()
    module, helper, review_path = [directory / n for n in ('lock.py', 'apply.py', 'review.json')]
    module.write_bytes(b'lock')
    helper.write_bytes(b'helper')
    review_path.write_bytes(b'review')
    proposal = {'fixture': 'exact'}
    review = {'helper_sha256': digest(helper), 'proposal': copy.deepcopy(proposal), 'result': 'PASS: fixture', 'findings': []}
    admission = {'helper_sha256': digest(helper), 'proposal': copy.deepcopy(proposal),
                 'run_directory': str(directory), 'review_sha256': digest(review_path)}
    state = {'lock_path': Path.home() / '.local/state/dotfiles/heavy-gate.lock'}
    lease = SimpleNamespace(HEAVY_GATE='fixture', LOCK_FD_ENV='FIXTURE_FD',
                            lock_path=lambda _: state['lock_path'], holder_env_name=lambda _: 'FIXTURE_HELD')
    ns = {'admission': admission, 'review': review, 'report': {'proposal': proposal}, 'directory': directory,
          'review_path': review_path, '__file__': str(helper), 'Path': Path, 'digest': digest,
          'LOCK_MODULE': module, 'LOCK_SHA': digest(module), 'lease': lease, 'os': SimpleNamespace(environ={})}
    return ns, state, lambda: exec(admission_code, ns)


ns, state, f = admission_fixture()
check('admission-and-canonical-lock-valid', f)
for name, container, key, value in [
    ('admission-helper-drift', 'admission', 'helper_sha256', 'wrong'),
    ('admission-proposal-drift', 'admission', 'proposal', {'different': True}),
    ('review-proposal-drift', 'review', 'proposal', {'different': True}),
    ('admission-directory-drift', 'admission', 'run_directory', '/different'),
    ('admission-review-digest-drift', 'admission', 'review_sha256', 'wrong'),
    ('review-not-passed', 'review', 'result', 'FAIL'),
    ('review-has-findings', 'review', 'findings', ['finding'])]:
    ns, state, f = admission_fixture()
    ns[container][key] = value
    check(name, f, True)
ns, state, f = admission_fixture()
state['lock_path'] = PRIVATE / 'alternate-lock'
check('alternate-lock-root-rejected', f, True)
for name in ['FIXTURE_HELD', 'FIXTURE_FD']:
    ns, state, f = admission_fixture()
    ns['os'].environ[name] = 'inherited'
    check('inherited-' + name.lower() + '-rejected', f, True)

(PRIVATE / 'guard-controls.json').write_text(json.dumps({
    'result': 'PASS', 'helper_sha256': SHA, 'controls': results,
    'method': 'Exact extracted AST with private file fixtures and synthetic Git/lease state; no native apply, lease operation, compiler or build.',
    'shared_writes': 0, 'native_apply_invocations': 0,
}, indent=2) + '\n')
print(json.dumps({'result': 'PASS', 'controls': len(results), 'receipt': str(PRIVATE / 'guard-controls.json')}))
