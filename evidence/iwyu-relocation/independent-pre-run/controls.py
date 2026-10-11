import ast
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

D = Path(__file__).resolve().parent
ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
HELPER = ROOT / 'dev/toolchains/iwyu_relocation.py'
EXPECTED = '3ede4efb222e3510fc3e0c9f0644fdbce39bf888c34fefb02ab3afedd786eff4'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(HELPER) == EXPECTED
frozen = json.loads((D / 'frozen-inputs.json').read_text())
for p, row in frozen['files'].items():
    assert sha(ROOT / p) == row['sha256']
started = datetime.now(timezone.utc).isoformat()
clock = time.monotonic()
source = HELPER.read_text()
tree = ast.parse(source)
header_def = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'header_trace')
main_def = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
run_def = next(n for n in main_def.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
def forbidden(*args, **kwargs):
    raise RuntimeError('native subprocess forbidden in reviewer controls')
subprocess.Popen = forbidden
subprocess.run = forbidden
ns = {'Path': Path, 're': re, 'digest': sha}
exec(compile(ast.Module(body=[header_def, run_def], type_ignores=[]), str(HELPER), 'exec'), ns)
S = D / 'scratch'
resources = S / 'resources'
inc = resources / 'include'
inc.mkdir(parents=True)
files = {'stddef.h': '/* synthetic stddef */\n', '__stddef_size_t.h': '/* synthetic size_t */\n', '__stddef_null.h': '/* synthetic null */\n'}
for name, content in files.items():
    (inc / name).write_text(content)
outside = S / 'fallback.h'
outside.write_text('/* synthetic fallback */\n')
records = [{'path': 'include/' + name, 'kind': 'file', 'sha256': sha(inc / name)} for name in files]
paths = [inc / name for name in files]
trace = lambda selected: ''.join('.' * (index + 1) + ' ' + str(path) + '\n' for index, path in enumerate(selected))
header_cases = []
def check_header(name, content, inventory=records, accepted=False):
    try:
        result = ns['header_trace'](content, resources, inventory)
    except AssertionError:
        assert not accepted, name
        header_cases.append({'case': name, 'outcome': 'rejected', 'exception': 'AssertionError'})
    else:
        assert accepted, name
        assert result == [{'path': str(p), 'sha256': sha(p)} for p in paths]
        header_cases.append({'case': name, 'outcome': 'accepted', 'rows': len(result)})
check_header('exact-copied-builtin-headers', trace(paths), accepted=True)
check_header('empty-trace', '')
check_header('missing-stddef', trace(paths[1:]))
check_header('missing-size-t', trace([paths[0], paths[2]]))
check_header('fallback-outside-copied-resources', trace(paths + [outside]))
(inc / '__stddef_null.h').write_text('/* changed synthetic header */\n')
check_header('changed-header-bytes', trace(paths))
(inc / '__stddef_null.h').write_text(files['__stddef_null.h'])
check_header('header-absent-from-inventory', trace(paths), records[:2])
check_header('error-diagnostic', trace(paths) + 'fixture.cc:1:1: error: rejected\n')
check_header('fatal-error-diagnostic', trace(paths) + 'fixture.cc:1:1: fatal error: rejected\n')
check_header('relative-trace-path', trace(paths) + '. include/other.h\n')
check_header('noncanonical-trace-path', trace(paths) + '. ' + str(resources) + '/include/../include/stddef.h\n')
(inc / '__stddef_size_t.h').unlink()
(inc / '__stddef_size_t.h').symlink_to(outside)
check_header('symlink-escape', trace(paths))
(inc / '__stddef_size_t.h').unlink()
(inc / '__stddef_size_t.h').write_text(files['__stddef_size_t.h'])

run_cases = []
def check_run(name, actual=0, expected=0, error=None, accepted=False, duplicate=False, wrong_case=False):
    directory = S / name
    directory.mkdir()
    report = {'commands': [{'case': name, 'returncode': 0}]} if duplicate else {'commands': []}
    calls, saves = [], []
    argv = ['synthetic-native-tool', '--synthetic']
    def native(label, supplied, timeout=60, descriptor=None):
        calls.append({'case': label, 'argv': supplied, 'timeout': timeout, 'descriptor': descriptor})
        assert supplied == argv and timeout == 17 and descriptor == 91
        if error is not None:
            raise error
        report['commands'].append({'case': 'other-label' if wrong_case else label, 'returncode': actual})
        (directory / (label + '.stdout')).write_text('synthetic result\n')
        assert actual == 0, 'native nonzero result'
        return 'synthetic result\n'
    def save():
        saves.append(copy.deepcopy(report))
    ns.update(directory=directory, report=report, native=native, save=save)
    caught = None
    try:
        result = ns['run'](name, argv, timeout=17, descriptor=91, expected=expected)
    except BaseException as exc:
        caught = type(exc).__name__
        assert not accepted, name
        if error is not None and not isinstance(error, AssertionError):
            assert exc is error, name
        else:
            assert isinstance(exc, AssertionError), name
    else:
        assert accepted and result == 'synthetic result\n', name
    assert len(calls) == (0 if duplicate else 1), name
    recorded = error is None and not duplicate and not wrong_case
    assert len(saves) == (1 if recorded else 0), name
    if recorded:
        assert report['commands'][-1]['expected_returncode'] == expected
        assert report['commands'][-1]['timeout_seconds'] == 17
        assert saves[-1] == report
    run_cases.append({'case': name, 'actual_mock_returncode': None if error or duplicate else actual,
                      'expected_returncode': expected, 'outcome': 'accepted' if accepted else 'rejected',
                      'exception': caught, 'mock_calls': len(calls), 'save_calls': len(saves)})
check_run('expected-zero', accepted=True)
check_run('expected-one', actual=1, expected=1, accepted=True)
check_run('unexpected-zero', expected=1)
check_run('unexpected-nonzero', actual=23)
check_run('wrong-nonzero', actual=2, expected=1)
check_run('signal-result', actual=-15, expected=1)
check_run('assertion-before-receipt', expected=1, error=AssertionError('synthetic pre-receipt failure'))
check_run('wrong-receipt-case', actual=1, expected=1, wrong_case=True)
check_run('spawn-error-propagates', error=OSError('synthetic spawn failure'))
check_run('timeout-propagates', error=subprocess.TimeoutExpired(['synthetic-native-tool'], 17))
check_run('interrupt-propagates', error=KeyboardInterrupt('synthetic interrupt'))
check_run('duplicate-label', duplicate=True)
for p, row in frozen['files'].items():
    assert sha(ROOT / p) == row['sha256']
result = {'result': 'PASS', 'helper_sha256': EXPECTED, 'started_at': started,
          'finished_at': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - clock,
          'extracted_functions': {'header_trace': header_def.lineno, 'main.run': run_def.lineno},
          'header_trace_controls': header_cases, 'mocked_run_controls': run_cases,
          'frozen_files_unchanged': len(frozen['files']), 'native_subprocesses': 0,
          'protected_calls': 0, 'limitations': ['Native runner and resource tool behavior not executed.',
          'Exceptions and exit codes in run controls are mocked, not process-termination tests.']}
(D / 'controls.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'result': result['result'], 'header_controls': len(header_cases), 'mocked_run_controls': len(run_cases),
                  'elapsed_seconds': result['elapsed_seconds'], 'native_subprocesses': 0}))
