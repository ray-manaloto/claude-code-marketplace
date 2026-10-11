import ast
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tomllib
from types import SimpleNamespace

D = Path(__file__).parent.resolve()
R = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = R / 'evidence/mise-renovate'
load = lambda p: json.loads(p.read_text())
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
frozen = load(D / 'frozen-inputs.json')
def unchanged():
    for name, row in frozen['files'].items():
        assert digest(R / name) == row['sha256'], name
unchanged()
def forbidden(*args, **kwargs):
    raise RuntimeError('native execution disabled in reviewer synthetic controls')
subprocess.Popen = subprocess.run = subprocess.call = subprocess.check_call = subprocess.check_output = forbidden
os.system = forbidden
helper_path = R / 'dev/toolchains/mise_renovate.py'
helper = ast.parse(helper_path.read_text())
nodes = {n.name: n for n in helper.body if isinstance(n, ast.FunctionDef)}
def define(name, scope):
    exec(compile(ast.Module(body=[nodes[name]], type_ignores=[]), str(helper_path), 'exec'), scope)
base_path = 'evidence/p2996-registration/independent-registration/post-state.json'
baseline = load(R / base_path)
data = load(E / 'contract.json')
current = load(E / 'inventory/current-metadata.json')
original_baseline, original_data = copy.deepcopy(baseline), copy.deepcopy(data)
expected = copy.deepcopy(baseline)
expected['install_entries'] = copy.deepcopy(current['install_entries'])
for name in ('config.toml', 'mise.lock'):
    expected['protected']['global_files'][name] = {k: current['global_files'][name][k] for k in ('sha256', 'mode')}
scope = {'copy': copy}
define('overlay', scope)
overlay = scope['overlay']
result = overlay(baseline, data)
assert result == expected
result['install_entries']['npm-renovate/global']['link'] = './changed-private-result'
result['protected']['global_files']['config.toml']['sha256'] = '0' * 64
assert baseline == original_baseline and data == original_data
cases = [{'case': 'exact-overlay-and-output-mutation-isolation', 'pass': True}]
for case in ('wrong-existing-renovate-preimage', 'missing-global-alias'):
    b, d = copy.deepcopy(baseline), copy.deepcopy(data)
    if case == 'wrong-existing-renovate-preimage':
        b['install_entries']['npm-renovate/latest']['link'] = './unexpected'
    else:
        d['global_aliases'].pop(next(iter(d['global_aliases'])))
    try:
        overlay(b, d)
    except AssertionError:
        cases.append({'case': case, 'pass': True, 'observed': 'rejected'})
    else:
        raise AssertionError(case)

contents = {
    'config.toml': '[tools."npm:renovate"]\nversion = "44.149.3"\n[tools.cmake]\nversion = "4.4.4"\n',
    'mise.lock': '[[tools."npm:renovate"]]\nversion = "44.149.3"\nspecifiers = ["44.149.3"]\n[[tools.cmake]]\nversion = "4.4.4"\n',
}
for case in ('semantic-exact', 'semantic-lock-specifier', 'semantic-current-symlink', 'semantic-current-hash-drift'):
    home = D / 'semantic-controls' / case
    (home / '.config/mise').mkdir(parents=True)
    (home / 'backups').mkdir()
    candidate = {'global_updates': {}}
    for name, text in contents.items():
        old_path, new_path = home / 'backups' / name, home / '.config/mise' / name
        old_path.write_text(text)
        new_path.write_text(text.replace('44.149.3', '44.150.1'))
        candidate['global_updates'][name] = {'backup': str(old_path), 'previous': {'sha256': digest(old_path), 'mode': '0o600'}, 'current': {'sha256': digest(new_path), 'mode': '0o600'}}
    if case == 'semantic-lock-specifier':
        path = home / '.config/mise/mise.lock'
        path.write_text(path.read_text().replace('specifiers = ["44.150.1"]', 'specifiers = ["44.149.3"]'))
        candidate['global_updates']['mise.lock']['current']['sha256'] = digest(path)
    elif case == 'semantic-current-symlink':
        path = home / '.config/mise/config.toml'
        path.unlink()
        path.symlink_to(home / 'backups/config.toml')
    elif case == 'semantic-current-hash-drift':
        path = home / '.config/mise/config.toml'
        path.write_text(path.read_text() + '# hash drift without semantic change\n')
    class PrivatePath:
        def __new__(cls, value):
            return Path(value)
        @staticmethod
        def home():
            return home
    semantics = {'Path': PrivatePath, 'digest': digest, 'tomllib': tomllib}
    define('semantic_check', semantics)
    original = copy.deepcopy(candidate)
    error = None
    try:
        semantics['semantic_check'](candidate)
    except AssertionError as caught:
        error = caught
    assert (error is None) == (case == 'semantic-exact'), case
    assert candidate == original
    cases.append({'case': case, 'pass': True, 'observed': 'accepted' if error is None else 'rejected'})

for case in ('delegation-exact', 'contract-failure', 'semantic-failure', 'legacy-failure'):
    stages = []
    failure = AssertionError('private synthetic ' + case)
    unmodified_value = {'unmodified': object()}
    def loader(path):
        return baseline if path == R / base_path else unmodified_value
    previous = SimpleNamespace(__file__=str(R / 'dev/toolchains/mise_runtime.py'), load=loader, marker=object(), contract=object(), overlay=object(), function=object())
    def contract():
        stages.append('contract')
        if case == 'contract-failure':
            raise failure
        return data
    def semantic_check(value):
        stages.append('semantic')
        assert value is data
        if case == 'semantic-failure':
            raise failure
    def function(path, name, received):
        stages.append('function')
        assert path == Path(previous.__file__) and name == 'protected'
        assert set(received) == set(vars(previous))
        assert all(received[k] is v for k, v in vars(previous).items() if k != 'load')
        assert received['load'](R / base_path) == expected
        assert received['load'](R / 'unrelated-private-sentinel.json') is unmodified_value
        def delegated():
            stages.append('delegate')
            if case == 'legacy-failure':
                raise failure
            return {'private-sentinel': True}
        return delegated
    adapter = {'contract': contract, 'semantic_check': semantic_check, 'function': function, 'previous': previous,
               'Path': Path, 'ROOT': R, 'BASELINE': base_path, 'load': loader, 'overlay': overlay}
    define('protected', adapter)
    caught = None
    try:
        value = adapter['protected']()
    except AssertionError as error:
        caught = error
    assert (caught is None) == (case == 'delegation-exact')
    if caught is not None:
        assert caught is failure
    else:
        assert value == {'private-sentinel': True}
    assert stages == {'contract-failure': ['contract'], 'semantic-failure': ['contract', 'semantic']}.get(case, ['contract', 'semantic', 'function', 'delegate'])
    cases.append({'case': case, 'pass': True, 'stages': stages, 'failure_propagated_unchanged': caught is failure if caught is not None else None})
assert baseline == original_baseline and data == original_data
unchanged()
result = {'result': 'PASS', 'created_at': datetime.now(timezone.utc).isoformat(), 'helper_sha256': digest(helper_path),
          'contract_sha256': digest(E / 'contract.json'), 'candidate_sha256': digest(E / 'candidate.json'), 'cases': cases,
          'case_count': len(cases), 'frozen_inputs_unchanged': len(frozen['files']), 'actual_legacy_protected_calls': 0,
          'mocked_adapter_calls': 4, 'main_calls': 0, 'native_tool_commands': 0, 'live_shared_inventory_calls': 0,
          'method': 'Actual AST-extracted overlay and semantic_check with private toy files; actual AST-extracted protected adapter with contract/semantic/legacy delegation mocked. No main or real protection calls.'}
(D / 'control-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
