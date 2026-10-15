from pathlib import Path
from datetime import datetime, timezone
import ast, copy, hashlib, json, os, subprocess, sys
from types import SimpleNamespace
D = Path(__file__).parent
R = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
H = R / 'dev/toolchains/mise_renovate.py'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
textsha = lambda v: hashlib.sha256(v.encode()).hexdigest()
F = load(D / 'frozen-inputs.json')['files']
def unchanged():
    for name, entry in F.items():
        assert sha(R / name) == entry['sha256'], name
unchanged()
def prohibited(*args, **kwargs):
    raise AssertionError('native subprocess forbidden in reviewer controls')
for name in ['Popen', 'run', 'call', 'check_call', 'check_output']:
    setattr(subprocess, name, prohibited)
os.system = prohibited
# Only the new pure functions and new profile-loop statements are compiled.
# No candidate module imports, main(), protected(), or old wrapper execution.
tree = ast.parse(H.read_text())
functions = {n.name:n for n in tree.body if isinstance(n, ast.FunctionDef)}
ns = {'os':os, 'hashlib':hashlib}
exec(compile(ast.Module(body=[functions['path_transition'], functions['compare_profile']], type_ignores=[]), str(H), 'exec'), ns)
transition, compare = ns['path_transition'], ns['compare_profile']
main_try = next(n for n in functions['main'].body if isinstance(n, ast.Try))
start = next(i for i,n in enumerate(main_try.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='probe' for t in n.targets))
end = next(i for i,n in enumerate(main_try.body) if isinstance(n,ast.Assert) and any(isinstance(v,ast.Constant) and v.value=='default-after' for v in ast.walk(n)))
loop_body = copy.deepcopy(main_try.body[start:end+1])
loop = ast.FunctionDef(name='review_profile_loop', args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=loop_body,decorator_list=[])
loop_code = compile(ast.fix_missing_locations(ast.Module(body=[loop], type_ignores=[])), str(H), 'exec')
data = load(D / 'frozen-contract.json')
old, new = data['path_transition']['previous'], data['path_transition']['current']
cases = []
def passed(name, **extra):
    cases.append({'case':name, 'pass':True, **extra})

for mode in ['valid', 'disagreeing-proof', 'other-profile-value', 'proof-stderr', 'old-final-default', 'changed-final-default', 'proof-child-error']:
    directory = D / ('fixture-' + mode)
    directory.mkdir()
    lanes = ['default', 'cpp-build', 'p2996', 'gcc16']
    paths = {lane:'/fixture/' + lane + ':' + new + '::/tail:' for lane in lanes}
    expected, observed = {}, {}
    for lane in lanes:
        selected = {'CC':'/fixture/'+lane+'/cc', 'CPATH':None, 'SDKROOT':None}
        if lane == 'gcc16':
            selected['MARKETPLACE_GCC16_PREFIX'] = '/fixture/gcc16'
        if lane == 'p2996':
            selected['MARKETPLACE_P2996_PREFIX'] = '/fixture/p2996'
        prior = paths[lane].replace(':'+new+':', ':'+old+':')
        expected[lane] = {'path_sha256':textsha(prior), 'selected':selected, 'tools':{'cmake':'/fixture/cmake'}}
        observed[lane] = expected[lane] | {'path_sha256':textsha(paths[lane])}
    expected_paths = {lane:lane+'.json' for lane in lanes}
    inherited = {'profiles':expected_paths, 'p2996_prefix':'/fixture/p2996', 'isolation_keys':['CPATH','SDKROOT']}
    observed_text = {lane:json.dumps(value)+'\n' for lane,value in observed.items()}
    report = {}; env = {}; calls = []
    sentinel = OSError('synthetic proof command failure')
    def fixture_load(p):
        assert p.parent == directory
        return copy.deepcopy(expected[p.stem])
    def run(label, argv):
        calls.append(label)
        (directory / (label+'.stderr')).write_text('diagnostic\n' if mode=='proof-stderr' and label=='default-path-transition' else '')
        if label == 'default-after':
            assert argv == normal_argv
            if mode == 'old-final-default':
                return json.dumps(expected['default'])+'\n'
            if mode == 'changed-final-default':
                return json.dumps(observed['default'] | {'tools':{'cmake':'/different'}})+'\n'
            return observed_text['default']
        lane = next(lane for lane in lanes if label.startswith(lane+'-'))
        assert argv[0] == '/mock/mise' and '--fresh-env' in argv and '--no-deps' in argv and '--no-hooks' in argv
        assert ('-E' not in argv) if lane=='default' else argv[argv.index('-E')+1]==lane
        if label.endswith('-profile'):
            assert argv[-2:] == normal_argv[-2:]
            value = observed[lane]
            if mode == 'other-profile-value' and lane=='default':
                value = value | {'tools':{'cmake':'/unexpected'}}
            return json.dumps(value)+'\n'
        if label.endswith('-path-transition'):
            assert argv[-2:] == [old,new] and argv[-6:-3] == ['/mock/python','-B','-c']
            assert 'from mise_renovate import path_transition;' in argv[-3]
            if mode == 'proof-child-error':
                raise sentinel
            proof_path = paths[lane] + '/unrelated' if mode=='disagreeing-proof' else paths[lane]
            return json.dumps(transition(proof_path,old,new))+'\n'
        assert label.endswith('-isolation')
        return json.dumps({key:observed[lane]['selected'].get(key) for key in inherited['isolation_keys']})+'\n'
    normal_argv = ['/mock/mise','--no-hooks','-C','/mock/cwd','exec','--fresh-env','--no-deps','--','/mock/old-python','/mock/allowlist.py']
    scope = {'Path':Path,'__file__':str(H),'sys':SimpleNamespace(executable='/mock/python'),'json':json,'report':report,'env':env,'data':data,'current':{'path':'/mock/mise'},'inherited':inherited,'directory':directory,'ROOT':directory,'normal_argv':normal_argv,'load':fixture_load,'run':run,'compare_profile':compare}
    exec(loop_code,scope)
    try:
        scope['review_profile_loop']()
    except OSError as error:
        assert mode=='proof-child-error' and error is sentinel
        assert calls == ['default-profile','default-path-transition'] and report['path_transitions']=={}
        passed(mode, exception_identity_preserved=True, mock_calls=calls)
    except AssertionError:
        assert mode not in ['valid','proof-child-error']
        if mode in ['disagreeing-proof','other-profile-value']:
            assert calls == ['default-profile','default-path-transition'] and report['path_transitions']=={}
        if mode in ['old-final-default','changed-final-default']:
            assert calls[-1]=='default-after' and set(report['path_transitions'])==set(lanes)
        passed(mode, rejected=True, mock_calls=calls)
    else:
        assert mode=='valid' and len(calls)==13 and calls[-1]=='default-after'
        assert set(report['path_transitions'])==set(lanes) and env=={}
        for lane in lanes:assert report['path_transitions'][lane]==transition(paths[lane],old,new)
        passed('four-lanes-bind-separate-proof-and-new-final-default',mock_calls=calls)

value = ':' + new + '::/tail:'
expected = {'path_sha256':textsha(':'+old+'::/tail:'),'other':'same'}
observed = expected | {'path_sha256':textsha(value)}
proof = transition(value,old,new)
compare(observed,expected,proof)
passed('leading-trailing-and-consecutive-empty-PATH-components-preserved')
changed = value + ':'
try:
    compare(observed | {'path_sha256':textsha(changed)},expected,transition(changed,old,new))
except AssertionError:
    passed('additional-empty-PATH-component-rejected')
else:
    raise AssertionError('unrelated empty PATH component accepted')
unchanged()
assert len(cases)==9
result = {'result':'PASS','at':datetime.now(timezone.utc).isoformat(),'helper_sha256':sha(H),'contract_sha256':sha(D/'frozen-contract.json'),'candidate_sha256':sha(D/'frozen-candidate.json'),'cases':cases,'native_commands':0,'main_calls':0,'protected_calls':0,'candidate_imports':0,'mock_loop_cases':7,'pure_path_cases':2,'unchanged_watched_files':len(F)}
(D/'control-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'result':'PASS','cases':len(cases),'native_commands':0,'main_calls':0,'protected_calls':0}))
