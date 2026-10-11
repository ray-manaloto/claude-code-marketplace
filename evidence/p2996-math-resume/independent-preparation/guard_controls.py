"""Private AST controls for the new math-resume guards; no subprocesses or lease."""
import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
PRIVATE = Path(__file__).resolve().parent
HELPER = ROOT / 'dev/toolchains/p2996_build.py'
HELPER_SHA = '7b2bb266094f82008fe2c0f8cfba66ed6cd2e107ac301e3d3fb981c1aeb75d1f'
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(HELPER) == HELPER_SHA
tree = ast.parse(HELPER.read_text())
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
body = next(n for n in main.body if isinstance(n, ast.Try)).body
setup = next(n for n in body if isinstance(n, ast.If) and ast.unparse(n.test) == 'args.math_compatibility')
source_node = next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == 'source_state')
build_if = next(n for n in body if isinstance(n, ast.If) and ast.unparse(n.test) == 'args.build')
held = next(n for n in build_if.body if isinstance(n, ast.With))
history_guard = next(n for n in held.body if isinstance(n, ast.Assert) and 'history.items()' in ast.unparse(n))
generated = next(n for n in held.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'math_adaptation')
flags = [n for n in main.body if isinstance(n, ast.If) and 'parser.error' in ast.unparse(n)][:2]
namespace = [n for n in main.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'evidence' for t in n.targets)]
namespace += [n for n in main.body if isinstance(n, ast.If) and ast.unparse(n.test) == 'args.math_compatibility']
MATH_FILES = ('clang/lib/Headers/float.h', 'libcxx/include/float.h')
PARENT = json.loads((ROOT / 'evidence/p2996-math-resume/preparation/qualification.json').read_text())
SDK_FILES = tuple(r['path'] for r in PARENT['proposal']['sdk_adaptation']['patch']['files'])
results = []
serial = 0


def execute(nodes, ns):
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(HELPER), 'exec'), ns)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def check(name, action, rejects=False):
    try:
        action()
    except (AssertionError, FileNotFoundError, SystemExit) as error:
        assert rejects, (name, repr(error))
        observed = type(error).__name__
    else:
        assert not rejects, name + ' unexpectedly accepted'
        observed = None
    results.append({'case': name, 'passed': True, 'observed_exception': observed})
    write(PRIVATE / 'guard-controls.json', {'helper_sha256': HELPER_SHA, 'controls': results})


def fixture():
    global serial
    serial += 1
    directory = PRIVATE / 'guard-fixtures' / str(serial)
    directory.mkdir(parents=True)
    root, source, build = directory / 'root', directory / 'source', directory / 'build'
    root.mkdir()
    source.mkdir()
    build.mkdir()
    math = root / 'evidence/p2996-math-application'
    scratch = root / 'evidence/p2996-math-compatibility'
    compat = root / 'evidence/p2996-sdk-compatibility'
    closure = root / 'evidence/p2996-resume/failure-closure-review.json'
    retained = scratch / 'independent-scratch/retained-preimages.json'
    records = []
    for name in (*SDK_FILES, *MATH_FILES):
        p = source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(('postimage:' + name).encode())
        records.append({'path': name, 'after_sha256': digest(p)})
    sdk_receipts = {}
    for name in ('operation/qualification.json', 'application-review.json', 'scratch/proposal.json', 'scratch/rdf-comparator.patch'):
        p = compat / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(name)
        sdk_receipts[name] = digest(p)
    names = ['.ninja_log', '.ninja_deps']
    names += ['runtimes/' + child + '/' + file for child in ('builtins-bins', 'runtimes-bins') for file in ('.ninja_log', '.ninja_deps', 'CMakeCache.txt')]
    names += ['bin/clang-21']
    inventory, ninja = [], {}
    for name in names:
        p = build / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(('state:' + name).encode())
        inventory.append({'path': str(p), 'sha256': digest(p)})
        if p.name in ('.ninja_log', '.ninja_deps'):
            ninja[str(p)] = digest(p)
    write(closure, {'incremental_state': ninja})
    write(retained, {'inventory_records': inventory})
    patch_file = scratch / 'scratch/sdk-math.patch'
    patch_file.parent.mkdir(parents=True, exist_ok=True)
    patch_file.write_text('fixture math patch')
    apply_helper = root / 'dev/toolchains/p2996_math_apply.py'
    apply_helper.parent.mkdir(parents=True)
    apply_helper.write_text('fixture apply helper')
    patch = {'source': str(source), 'base_commit': 'base', 'files': records[len(SDK_FILES):],
             'patch_sha256': digest(patch_file), 'prior_source_diff_sha256': 'rdf-diff',
             'failure_closure_sha256': digest(closure)}
    write(scratch / 'scratch/proposal.json', patch)
    cumulative = hashlib.sha256(b'cumulative-seven-file-diff').hexdigest()
    operation = {'state': 'PASS: exact math adaptation applied', 'applied': True, 'lease_released': True,
                 'build_and_protected_state_unchanged': True, 'commands': [{'returncode': 0}] * 18,
                 'helper_sha256': digest(apply_helper), 'diff_sha256': cumulative,
                 'proposal': {'adaptation': patch, 'receipts': {str(retained.relative_to(root)): digest(retained)}}}
    write(math / 'operation/qualification.json', operation)
    review = {'result': 'PASS', 'findings': [], 'operation_sha256': digest(math / 'operation/qualification.json'),
              'helper_sha256': digest(apply_helper), 'diff_sha256': cumulative, 'patch_sha256': digest(patch_file)}
    write(math / 'application-review.json', review)
    ns = {'ROOT': root, 'Path': Path, 'digest': digest, 'load': lambda p: json.loads(p.read_text()),
          '__file__': str(root / 'dev/toolchains/p2996_build.py'), 'args': SimpleNamespace(math_compatibility=True),
          'math': math, 'math_adaptation': None, 'configuration': {'pin': 'base', 'tree': 'tree'},
          'source': source, 'build': build, 'directory': directory, 'compat': compat,
          'adaptation': {'diff_sha256': 'rdf-diff', 'patch': {'files': records[:len(SDK_FILES)]}, 'receipts': sdk_receipts},
          'MATH_FILES': MATH_FILES, 'SDK_FILES': SDK_FILES, 'report': {}}
    model = {'head': 'base', 'tree': 'tree', 'status': sorted(' M ' + name for name in (*SDK_FILES, *MATH_FILES)),
             'diff': b'cumulative-seven-file-diff'}
    def run(label, argv):
        key = label.rsplit('-', 1)[-1]
        if key == 'diff':
            (directory / (label + '.stdout')).write_bytes(model[key])
            return model[key].decode()
        return '\n'.join(model[key]) + '\n' if key == 'status' else model[key] + '\n'
    ns.update(run=run, git=['fixture-git'])
    return ns, model


def edit(ns, relative, change, rebind=False):
    p = ns['ROOT'] / relative
    value = ns['load'](p)
    change(value)
    write(p, value)
    if rebind:
        review = ns['math'] / 'application-review.json'
        row = ns['load'](review)
        row['operation_sha256'] = digest(ns['math'] / 'operation/qualification.json')
        write(review, row)


class Parser:
    def error(self, message):
        raise SystemExit(message)


for name, resume, sdk, reject in [('math-without-sdk', True, False, True), ('math-sdk-without-resume', False, True, True), ('math-flags-valid', True, True, False)]:
    ns = {'args': SimpleNamespace(math_compatibility=True, sdk_compatibility=sdk, resume=resume), 'parser': Parser()}
    check(name, lambda ns=ns: execute(flags, ns), reject)
ns = {'ROOT': ROOT, 'args': SimpleNamespace(math_compatibility=True, sdk_compatibility=True)}
execute(namespace, ns)
check('math-evidence-namespace', lambda: (_ for _ in ()).throw(AssertionError()) if ns['evidence'] != ROOT / 'evidence/p2996-math-resume' else None)

ns, model = fixture()
check('valid-reviewed-math-application', lambda: execute([setup], ns))
op_rel = 'evidence/p2996-math-application/operation/qualification.json'
review_rel = 'evidence/p2996-math-application/application-review.json'
for name, relative, mutate in [
    ('math-not-applied', op_rel, lambda q: q.update(applied=False)),
    ('math-lease-not-released', op_rel, lambda q: q.update(lease_released=False)),
    ('math-protection-failed', op_rel, lambda q: q.update(build_and_protected_state_unchanged=False)),
    ('math-command-failed', op_rel, lambda q: q['commands'].__setitem__(0, {'returncode': 1})),
    ('math-review-failed', review_rel, lambda q: q.update(result='FAIL')),
    ('math-review-finding', review_rel, lambda q: q.update(findings=['finding'])),
    ('math-operation-binding-drift', review_rel, lambda q: q.update(operation_sha256='wrong')),
    ('math-cumulative-diff-binding-drift', review_rel, lambda q: q.update(diff_sha256='wrong')),
]:
    ns, model = fixture()
    edit(ns, relative, mutate)
    check(name, lambda ns=ns: execute([setup], ns), True)
for name, relative in [
    ('math-helper-byte-drift', 'dev/toolchains/p2996_math_apply.py'),
    ('math-patch-byte-drift', 'evidence/p2996-math-compatibility/scratch/sdk-math.patch'),
    ('failure-closure-byte-drift', 'evidence/p2996-resume/failure-closure-review.json'),
    ('retained-inventory-byte-drift', 'evidence/p2996-math-compatibility/independent-scratch/retained-preimages.json'),
]:
    ns, model = fixture()
    p = ns['ROOT'] / relative
    p.write_bytes(p.read_bytes() + b'\n')
    check(name, lambda ns=ns: execute([setup], ns), True)
for name, key, value in [('prior-rdf-diff-mismatch', 'prior_source_diff_sha256', 'wrong'), ('math-base-commit-mismatch', 'base_commit', 'wrong'), ('math-source-path-mismatch', 'source', '/fixture-other-source')]:
    ns, model = fixture()
    edit(ns, op_rel, lambda q, key=key, value=value: q['proposal']['adaptation'].__setitem__(key, value), True)
    changed = ns['load'](ns['math'] / 'operation/qualification.json')['proposal']['adaptation']
    write(ns['ROOT'] / 'evidence/p2996-math-compatibility/scratch/proposal.json', changed)
    check(name, lambda ns=ns: execute([setup], ns), True)
for name, relative in [('changed-child-state-before-preparation', 'runtimes/runtimes-bins/.ninja_deps'), ('changed-child-cache-before-preparation', 'runtimes/builtins-bins/CMakeCache.txt')]:
    ns, model = fixture()
    (ns['build'] / relative).write_bytes(b'drift')
    check(name, lambda ns=ns: execute([setup], ns), True)
ns, model = fixture()
retained = ns['ROOT'] / 'evidence/p2996-math-compatibility/independent-scratch/retained-preimages.json'
q = ns['load'](retained)
q['inventory_records'] = [row for row in q['inventory_records'] if not row['path'].endswith('builtins-bins/CMakeCache.txt')]
write(retained, q)
edit(ns, op_rel, lambda q: q['proposal']['receipts'].__setitem__(str(retained.relative_to(ns['ROOT'])), digest(retained)), True)
check('missing-retained-child-cache-rejected', lambda: execute([setup], ns), True)

ns, model = fixture()
execute([setup, source_node], ns)
for stage in ['source', 'source-immediate', 'source-after']:
    check('seven-file-valid-' + stage, lambda stage=stage: ns['source_state'](stage))
for name, change in [
    ('missing-math-status-entry', lambda ns, m: m['status'].remove(' M ' + MATH_FILES[0])),
    ('changed-cumulative-diff', lambda ns, m: m.update(diff=b'drift')),
    ('math-receipt-drift-before-lease', lambda ns, m: (ns['math'] / 'application-review.json').write_text('drift')),
    ('compiler-float-source-drift', lambda ns, m: (ns['source'] / MATH_FILES[0]).write_text('drift')),
    ('libcxx-float-source-drift', lambda ns, m: (ns['source'] / MATH_FILES[1]).write_text('drift')),
]:
    ns, model = fixture()
    execute([setup, source_node], ns)
    ns['source_state']('source')
    change(ns, model)
    check(name, lambda ns=ns: ns['source_state']('source-immediate'), True)
ns, model = fixture()
execute([setup, source_node], ns)
p = ns['source'] / MATH_FILES[0]
outside = ns['directory'] / 'outside-float.h'
outside.write_bytes(p.read_bytes())
p.unlink()
p.symlink_to(outside)
check('math-source-symlink-escape', lambda: ns['source_state']('source-after'), True)

ns, model = fixture()
execute([setup], ns)
check('retained-history-valid-immediately-before-build', lambda: execute([history_guard], ns))
for relative in ['runtimes/builtins-bins/.ninja_log', 'runtimes/builtins-bins/.ninja_deps', 'runtimes/runtimes-bins/.ninja_log', 'runtimes/runtimes-bins/.ninja_deps', 'runtimes/builtins-bins/CMakeCache.txt', 'runtimes/runtimes-bins/CMakeCache.txt', 'bin/clang-21']:
    ns, model = fixture()
    execute([setup], ns)
    (ns['build'] / relative).write_bytes(b'drift')
    check('history-drift-' + relative, lambda ns=ns: execute([history_guard], ns), True)

for bad in [None, 'lib/clang/21/include/float.h', 'include/c++/v1/float.h']:
    ns, model = fixture()
    execute([setup], ns)
    for relative, row in zip(['lib/clang/21/include/float.h', 'include/c++/v1/float.h'], ns['math_adaptation']['patch']['files'], strict=True):
        p = ns['build'] / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((ns['source'] / row['path']).read_bytes() if relative != bad else b'old-generated-header')
    check('generated-math-headers-' + (bad or 'both-valid'), lambda ns=ns: execute([generated], ns), bad is not None)
ns, model = fixture()
execute([setup], ns)
check('missing-generated-math-header', lambda: execute([generated], ns), True)

order = {'history_guard': held.body.index(history_guard), 'generated_guard': held.body.index(generated)}
for label in ['source-immediate', 'source-after', 'llvm-build']:
    order[label] = next(i for i, n in enumerate(held.body) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call) and n.value.args and isinstance(n.value.args[0], ast.Constant) and n.value.args[0].value == label)
assert order['source-immediate'] < order['history_guard'] < order['llvm-build'] < order['source-after'] < order['generated_guard']
write(PRIVATE / 'guard-controls.json', {'result': 'PASS', 'helper_sha256': HELPER_SHA, 'controls': results, 'static_held_order': order,
      'scope': 'Exact new math guard AST with only private fake source/build/receipt trees; no subprocess, lease or real apply/build.'})
print(json.dumps({'result': 'PASS', 'controls': len(results), 'static_held_order': order}))
