from pathlib import Path
from datetime import UTC, datetime
import ast
import copy
import difflib
import hashlib
import json
import tomllib

ROOT = Path('/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace')
E = ROOT / 'evidence/core-p2996'
D = Path(__file__).parent
HELPER_SHA = 'c35136f176b64a9a4d26d1ee8bfcd4562b794a8bc597caa7c6ef539a46140208'
PROPOSAL_SHA = 'da265185e7540877c78677ecd2108a240046d3acb2716a310996e3418a74d2c3'
def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def load(path):
    return json.loads(Path(path).read_text())
def record(path):
    path = Path(path)
    return {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}

helper = ROOT / 'dev/toolchains/core_matrix.py'
old_helper = E / 'attempt-1/operation/core_matrix.py.source'
assert sha(helper) == HELPER_SHA
assert sha(E / 'proposal.json') == PROPOSAL_SHA
assert sha(old_helper) == '3a3c06f9f736929d02b6843d344a69380c42962f7eccdff0a0e7b77f150a035c'
old, new = old_helper.read_text(), helper.read_text()
previous = '                assert json.loads(run(lane + "-profile", base + normal_argv[-2:], fd)) == (runtime if lane == "p2996" else gcc)["selected_environment"]\n'
replacement = '                # Both named profiles share the later qualified foundation PATH.\n                expected_profile = (runtime if lane == "p2996" else gcc)["selected_environment"] | {\n                    "path_sha256": runtime["selected_environment"]["path_sha256"]}\n                assert json.loads(run(lane + "-profile", base + normal_argv[-2:], fd)) == expected_profile\n'
assert old.count(previous) == 1 and new == old.replace(previous, replacement)
(D / 'reviewed-delta.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(old_helper),tofile=str(helper))))
proposal = load(E / 'proposal.json')
prior_proposal = load(E / 'attempt-1/proposal.json')
assert len(proposal['inputs']) == 72 and len(proposal['tool_hashes']) == 18
assert set(proposal['inputs']) - set(prior_proposal['inputs']) == {'evidence/core-p2996/profile-path-diagnosis.json','evidence/core-p2996/profile-correction-replay.json'}
assert [p for p in prior_proposal['inputs'] if proposal['inputs'][p] != prior_proposal['inputs'][p]] == ['dev/toolchains/core_matrix.py']
assert proposal['tool_hashes'] == prior_proposal['tool_hashes']
assert proposal['base_head'] == prior_proposal['base_head'] == '4247f308ed6cc0ad77b1bd61bbb849f317628661'
def inputs_match():
    assert sha(helper) == HELPER_SHA and sha(E / 'proposal.json') == PROPOSAL_SHA
    for p, value in proposal['inputs'].items():
        assert sha(ROOT / p) == value, p
    for p, value in proposal['tool_hashes'].items():
        assert sha(p) == value, p
inputs_match()
diagnosis = load(E / 'profile-path-diagnosis.json')
assert sha(E / 'profile-path-diagnosis.json') == 'dab01c46106c87b0f0af7f8c042067231f786f08d4c7785792902e85b47d977d'
verified_bindings = []
for binding in diagnosis['read_bindings']:
    original = Path(binding['path'])
    path = old_helper if original == helper else original
    assert sha(path) == binding['sha256'] and path.stat().st_size == binding['bytes'], str(path)
    verified_bindings.append({'recorded_path':str(original),'verified_path':str(path),'sha256':binding['sha256']})
assert len(verified_bindings) == 22
profile_sources = []
for item in diagnosis['source_contract']['profile_files']:
    path = Path(item['path']); assert sha(path) == item['sha256']
    contents = tomllib.loads(path.read_text())
    assert 'PATH' not in contents.get('env', {})
    if path.name in ('config.gcc16.toml','config.p2996.toml'):
        assert contents['include'] == ['cpp-foundation/common.toml'] and 'tools' not in contents
    else:
        assert contents['tools'] == {'cmake':'4.4.4','ninja':'1.13.2','sccache':'0.18.0'}
    profile_sources.append(record(path))
gcc = load(ROOT / 'evidence/gcc-runtime/qualification.json')
runtime_path = ROOT / 'evidence/p2996-reflection/operation/qualification.json'
runtime = load(runtime_path)
assert sha(runtime_path) == 'cdc6859a8b2a31c778de9e1d7351e8abd6c816d91e5386924ba91acb81e5cb77'
assert runtime['state'].startswith('PASS')
observed_gcc = load(E / 'attempt-1/operation/gcc16-profile.stdout')
observed_p = load(E / 'attempt-1/operation/p2996-profile.stdout')
assert observed_gcc['selected'] == gcc['selected_environment']['selected'] and len(observed_gcc['selected']) == 32
assert observed_gcc['homebrew_llvm_on_path'] == gcc['selected_environment']['homebrew_llvm_on_path']
assert observed_p == runtime['selected_environment']
accepted_profile_command = next(c for c in runtime['commands'] if c['case'] == 'named-profile')
assert accepted_profile_command['returncode'] == 0
for item in accepted_profile_command['logs']:
    assert sha(item['path']) == item['sha256']
assert load(accepted_profile_command['logs'][0]['path']) == observed_p
registration = load(ROOT / 'evidence/p2996-registration/operation/qualification.json')
assert accepted_profile_command['started_at'] < registration['commands'][0]['started_at']
replay = load(E / 'profile-correction-replay.json')
assert replay['helper_sha256'] == HELPER_SHA
for path, value in replay['source_refs'].items():
    assert sha(ROOT / path) == value
assert set(replay['rejections']) == {'CC','CXX','MARKETPLACE_CPP_LANE','MARKETPLACE_GCC16_PREFIX','path_sha256','homebrew_llvm_on_path'}
assert all(replay['rejections'].values())
syntax = ast.parse(new)
assignment = next(n for n in ast.walk(syntax) if isinstance(n,ast.Assign) and n.lineno == 165)
assertion = next(n for n in ast.walk(syntax) if isinstance(n,ast.Assert) and n.lineno == 167)
code = compile(ast.Module(body=[assignment, assertion],type_ignores=[]),str(helper),'exec')
source_preimage = copy.deepcopy((gcc, runtime))
def evaluate(lane, observed):
    calls = []
    def recorded_run(label, argv, descriptor):
        calls.append({'label':label,'argv':argv,'descriptor':descriptor})
        return json.dumps(observed)
    scope = {'runtime':runtime,'gcc':gcc,'lane':lane,'json':json,'run':recorded_run,'base':['recorded-profile-only'],'normal_argv':['recorded-python','recorded-probe'],'fd':None}
    try:
        exec(code,scope)
        passed = True
    except AssertionError:
        passed = False
    assert calls == [{'label':lane+'-profile','argv':['recorded-profile-only','recorded-python','recorded-probe'],'descriptor':None}]
    assert (gcc,runtime) == source_preimage
    return passed
assert evaluate('gcc16',observed_gcc) and evaluate('p2996',observed_p)
rejections = {}
for name in replay['rejections']:
    mutated = copy.deepcopy(observed_gcc)
    if name in mutated['selected']:
        mutated['selected'][name] = 'unqualified-delta-control'
    elif name == 'path_sha256':
        mutated[name] = '0' * 64
    else:
        mutated[name] = not mutated[name]
    rejections[name] = not evaluate('gcc16',mutated)
assert all(rejections.values())
assert not evaluate('gcc16',gcc['selected_environment'])
replay_result = {'result':'PASS exact candidate comparison AST replay','native_subprocesses':0,'positive_recorded_profiles':['gcc16','p2996'],'six_field_mutations_rejected':rejections,'historical_GCC_PATH_rejected':True,'input_receipt_dictionaries_unchanged':True,'extracted_helper_lines':[165,167]}
(D / 'comparison-replay.json').write_text(json.dumps(replay_result,indent=2)+'\n')
static = load(E / 'profile-correction-static-checks.json')
assert static['helper_sha256'] == HELPER_SHA and len(static['checks']) == 3
assert all(c['returncode'] == 0 for c in static['checks'])
assert json.loads(static['checks'][2]['stdout'])['checks']['baseline'] == 19
originals = load(ROOT / 'evidence/onboarding/baseline-files.json')['files']
assert len(originals) == 19
assert all(sha(ROOT/r['path']) == r['sha256'] and (ROOT/r['path']).stat().st_size == r['bytes'] for r in originals)
prior_refs = []
for path, expected in [(E/'attempt-1/pre-run-review.json','b4bfe6e53281024a022e3113a4b2edef021cfe6f55774d743dfdc5deb7c72e7a'),(E/'attempt-1/failure-review.json','ca59e1a6852ae4eb7b360a7e96c4a8d57521ad064e912e429b768f1ec7d031db')]:
    assert sha(path) == expected and load(path)['result'].startswith('PASS') and not load(path)['findings']
    prior_refs.append(record(path))
inputs_match()
receipt = {'result':'PASS: 03b2b pre-run profile comparison delta; native retry remains UNVERIFIED','findings':[],'helper_sha256':HELPER_SHA,'proposal_sha256':PROPOSAL_SHA,'identity':{'checkout':str(ROOT),'branch':'codex/marketplace-native-onboarding','head':proposal['base_head'],'common_git_directory':'/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git'},'scope':'Exact four-line replacement of the profile equality guard; source and recorded-data replay only','delta':{'old_helper_sha256':sha(old_helper),'new_helper_lines':325,'other_helper_bytes_identical':True,'changed_expected_field':'path_sha256','immutable_expected_source':record(runtime_path),'all_32_GCC_selected_fields_and_llvm_boolean_retained':True,'full_dictionary_equality_retained':True,'fresh_mise_invocation_unchanged':True,'lease_capacity_timeout_build_source_compiler_SDK_protected_state_guards_unchanged':True},'proposal':{'verified_inputs':72,'verified_tool_hashes':18,'existing_inputs_changed':['dev/toolchains/core_matrix.py'],'two_added_inputs':['evidence/core-p2996/profile-path-diagnosis.json','evidence/core-p2996/profile-correction-replay.json'],'before_after_hashes_match':True},'shared_profile_sources':profile_sources,'diagnosis':{'receipt':record(E/'profile-path-diagnosis.json'),'read_bindings_verified':22,'historical_evolving_helper_checked_at_retained_old_source':True,'new_PATH_precedes_P2996_registration':True,'earlier_PATH_transition_cause':'UNPROVEN; no vcpkg causal inference','read_bindings':verified_bindings},'replay':replay_result,'parent_replay':record(E/'profile-correction-replay.json'),'retained_static_checks':{'receipt':record(E/'profile-correction-static-checks.json'),'help_exit':0,'tasks_validate_exit':0,'acceptance_baseline_exit':0,'original_files':19,'rerun_by_reviewer':False},'independent_Claude_original_hashes_verified':19,'prior_reviews':prior_refs,'executed_reviewer_checks':['Python -B read-only file/hash verification and exact comparison AST replay'],'native_compiler_build_profile_lease_operations':0,'checks_not_run':['native retry and sixteen-cell matrix','compiler/profile/CMake/Ninja/CTest invocations','fresh capacity or host lease','old guard batteries or broad preserved-state inventories'],'completed_at':datetime.now(UTC).isoformat()}
(D / 'pre-run-review.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'result':receipt['result'],'inputs':72,'tools':18,'diagnosis_bindings':22,'recorded_profile_positives':2,'field_mutation_rejections':6,'historical_path_rejection':1,'native_subprocesses':0}))
