import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tomllib

BASELINE = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/evidence/p2996-registration/independent-registration/post-state.json")
DRIFT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/evidence/vcpkg-private/native-hold/config-drift-inventory.json")
CONTRACT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/evidence/mise-runtime/contract.json")
OUT = Path("/Users/rmanaloto/.local/state/marketplace-tool-foundation/shared-state-inventory-SwV3Qf")
ROOT = Path("/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace")
EXPECTED = {"baseline":"8a5f11975efc9a953d8b57bde87467af5460cd48a3f695224dcaa9148a205317","drift":"261a38aa0484c2eba8d25c43de194f3fc19f3ad638582b26cf1ae203a511c5ec","contract":"c56618b021993665015b8f40c448504a666cb121076a88fb6217df2611434ff5"}

def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        while data := stream.read(1024 * 1024):
            result.update(data)
    return result.hexdigest()

def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()

def extracted(path, expected_digest, name):
    assert digest(path) == expected_digest
    tree = ast.parse(path.read_text())
    node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
    assert not node.decorator_list and not node.args.defaults
    scope = {'Path': Path, 'os': os, 'digest': digest}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), scope)
    return scope[name]

def metadata(path):
    row = {'path': str(path), 'lexists': os.path.lexists(path), 'exists': path.exists()}
    if row['lexists']:
        row['lstat_mode'] = oct(path.lstat().st_mode & 0o777)
        row['symlink'] = os.readlink(path) if path.is_symlink() else None
    if row['exists']:
        stat = path.stat()
        row.update({'mode': oct(stat.st_mode & 0o777), 'realpath': str(path.resolve()), 'bytes': stat.st_size,
                    'modified_at': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()})
        if path.is_file():
            row['sha256'] = digest(path)
    return row

def mapping_diff(before, current):
    added = {key: current[key] for key in sorted(current.keys() - before.keys())}
    removed = {key: before[key] for key in sorted(before.keys() - current.keys())}
    changed = {key: {'before': before[key], 'current': current[key]} for key in sorted(before.keys() & current.keys()) if before[key] != current[key]}
    return {'baseline_count': len(before), 'current_count': len(current),
            'unchanged_count': sum(before[key] == current[key] for key in before.keys() & current.keys()),
            'added': added, 'removed': removed, 'changed': changed}

def summary(value, path):
    row = {'type': type(value).__name__, 'semantic_sha256': hashlib.sha256(stable_json(value)).hexdigest()}
    version_position = (path and path[-1] == 'version') or (len(path) == 2 and path[0] == 'tools')
    if version_position and isinstance(value, str) and re.fullmatch(r'v?[0-9]+(?:[.][0-9]+){1,3}(?:[-+][A-Za-z0-9._-]+)?', value):
        row['version'] = value
    if isinstance(value, (dict, list)):
        row['count'] = len(value)
    return row

def semantic_diff(before, current, path=()):
    if type(before) is not type(current):
        return [{'key_path': list(path), 'kind': 'type_changed', 'before': summary(before,path), 'current': summary(current,path)}]
    if isinstance(before, dict):
        rows = []
        for key in sorted(before.keys() | current.keys()):
            next_path = path + (key,)
            if key not in before:
                rows.append({'key_path': list(next_path), 'kind': 'added', 'current': summary(current[key],next_path)})
            elif key not in current:
                rows.append({'key_path': list(next_path), 'kind': 'removed', 'before': summary(before[key],next_path)})
            else:
                rows.extend(semantic_diff(before[key], current[key], next_path))
        return rows
    if isinstance(before, list):
        rows = []
        for index in range(max(len(before), len(current))):
            next_path = path + (index,)
            if index >= len(before):
                rows.append({'key_path': list(next_path), 'kind': 'added', 'current': summary(current[index],next_path)})
            elif index >= len(current):
                rows.append({'key_path': list(next_path), 'kind': 'removed', 'before': summary(before[index],next_path)})
            else:
                rows.extend(semantic_diff(before[index], current[index], next_path))
        return rows
    if before != current:
        return [{'key_path': list(path), 'kind': 'changed', 'before': summary(before,path), 'current': summary(current,path)}]
    return []

os.umask(0o077)
stage = 'inputs'
try:
    assert digest(BASELINE) == EXPECTED['baseline']
    assert digest(DRIFT) == EXPECTED['drift']
    assert digest(CONTRACT) == EXPECTED['contract']
    baseline = json.loads(BASELINE.read_text())
    prior_drift = json.loads(DRIFT.read_text())
    contract = json.loads(CONTRACT.read_text())
    snapshot = extracted(ROOT / 'dev/toolchains/mise_link_probe.py', "b5eba47313527daaed5d6de36d05105e0b2d044494025b5b16a3d31cb9868eb0", 'snapshot')
    install_entries = extracted(ROOT / 'dev/toolchains/vcpkg_register.py', "2e41d87e285392f9d52c96870d34a59d3ce7021263adbc6bd4f2053636612ca6", 'install_entries')
    started = datetime.now(timezone.utc).isoformat()
    stage = 'install_entries'
    installs_path = Path('/Users/rmanaloto/.local/share/mise/installs')
    current_installs = install_entries(installs_path)
    install_diff = mapping_diff(baseline['install_entries'], current_installs)
    stage = 'directory_snapshots'
    directories = {path: snapshot(Path(path)) for path in baseline['directories']}
    directory_diffs = {path: mapping_diff(baseline['directories'][path], value) for path,value in directories.items()}
    stage = 'global_metadata'
    global_files = {}
    for name, expected in baseline['protected']['global_files'].items():
        row = metadata(Path('/Users/rmanaloto/.config/mise') / name)
        row.update({'expected_sha256':expected['sha256'], 'expected_mode':expected['mode'],
                    'digest_matches_baseline':row.get('sha256') == expected['sha256'],
                    'mode_matches_baseline':row.get('mode') == expected['mode'], 'not_symlink':row.get('symlink') is None})
        global_files[name] = row
    stage = 'semantic_diff'
    semantic = {}
    for name in ('config.toml','mise.lock'):
        path = Path('/Users/rmanaloto/.config/mise') / name
        old = next(row for row in prior_drift['global_files'] if row['path'] == str(path))
        backup = Path(old['backup_path'])
        before = metadata(backup)
        assert before['sha256'] == baseline['protected']['global_files'][name]['sha256']
        changes = semantic_diff(tomllib.loads(backup.read_text()), tomllib.loads(path.read_text()))
        semantic[name] = {'backup':before, 'current_sha256':global_files[name]['sha256'], 'changes':changes, 'change_count':len(changes)}
    stage = 'accepted_mise'
    mise = metadata(Path(contract['current_mise']['path']))
    mise.update({'accepted_sha256':contract['current_mise']['sha256'], 'accepted_bytes':contract['current_mise']['bytes'],
                 'accepted_recorded_version':contract['current_mise']['version'], 'version_executed':False,
                 'matches_accepted_digest':mise.get('sha256') == contract['current_mise']['sha256'],
                 'matches_accepted_size':mise.get('bytes') == contract['current_mise']['bytes']})
    stage = 'save_metadata'
    current = {'schema':1,'recorded_at':datetime.now(timezone.utc).isoformat(), 'install_entries':current_installs,'directories':directories,'global_files':global_files,'mise':mise}
    result = {'schema':1,'status':'OBSERVATION_ONLY_NOT_ACCEPTANCE','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
              'install_entries':install_diff,'directories':directory_diffs,'global_files':global_files,'semantic_differences':semantic,'mise':mise,
              'scope':{'protected_called':False,'native_mise_calls':0,'native_compiler_calls':0,'native_vcpkg_calls':0,'shared_writes':0,'full_llvm_prefix_scan':False}}
    for name,value in [('current-metadata.json',current),('comparison.json',result)]:
        with (OUT / name).open('x') as stream:
            json.dump(value,stream,sort_keys=True,indent=2)
            stream.write('\n')
    print(json.dumps({'status':result['status'],'install_counts':{name:len(install_diff[name]) for name in ('added','removed','changed')},
                      'directory_counts':{path:{name:len(value[name]) for name in ('added','removed','changed')} for path,value in directory_diffs.items()},
                      'global_changed':[name for name,row in global_files.items() if not row['digest_matches_baseline'] or not row['mode_matches_baseline']],
                      'semantic_change_counts':{name:row['change_count'] for name,row in semantic.items()},'mise_matches_accepted_digest':mise['matches_accepted_digest']}))
except BaseException as error:
    print(json.dumps({'status':'INVENTORY_ERROR','stage':stage,'error_type':type(error).__name__}))
    sys.exit(1)
