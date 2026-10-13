"""Read-only binding and isolated imports for the borrowed GitHubKit runtime."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tomllib

SELECTORS = ('UV_PROJECT', 'UV_WORKING_DIR', 'UV_PYTHON', 'UV_CONFIG_FILE',
             'UV_ENV_FILE', 'UV_ISOLATED', 'UV_NO_PROJECT', 'PYTHONHOME', 'PYTHONPATH')
IMPORTS = '''import importlib.metadata, json, pathlib, ssl, sys
import githubkit
print(json.dumps(dict(executable=str(pathlib.Path(sys.executable).absolute()),
    resolved=str(pathlib.Path(sys.executable).resolve()), prefix=str(pathlib.Path(sys.prefix).resolve()),
    sdk_version=importlib.metadata.version("githubkit"))))
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Import identity contains duplicate keys')
        result[key] = value
    return result


def overrides(environment, project):
    """Return names only: values may contain private paths or credentials."""
    conflicts = [key for key in SELECTORS if environment.get(key)]
    expected = (Path(project) / '.venv').resolve()
    for key in ('VIRTUAL_ENV', 'UV_PROJECT_ENVIRONMENT'):
        if environment.get(key) and Path(environment[key]).resolve() != expected:
            conflicts.append(key)
    return conflicts


def snapshot(project, expected_sdk):
    project = Path(project).absolute()
    venv = project / '.venv'
    interpreter = venv / 'bin/python'
    metadata = list(venv.glob('lib/python*/site-packages/githubkit-*.dist-info/METADATA'))
    if len(metadata) != 1:
        raise ValueError('Expected one installed GitHubKit metadata file')
    versions = [line[9:] for line in metadata[0].read_text().splitlines()
                if line.startswith('Version: ')]
    if versions != [expected_sdk]:
        raise ValueError('Installed GitHubKit version differs from policy')
    paths = [interpreter.resolve(strict=True), venv / 'pyvenv.cfg', metadata[0],
             venv / 'bin/github-search', project / 'pyproject.toml',
             project / 'uv.lock', project / 'mise.toml']
    return dict(interpreter=str(interpreter), resolved=str(interpreter.resolve()),
                prefix=str(venv.resolve()), sdk_version=expected_sdk,
                files={str(p): sha(p) for p in paths})


def check(project, expected_sdk, cycle, timeout=10, environment=None):
    """Run no credentials or providers; report actual output and bounded exit."""
    environment = os.environ if environment is None else environment
    result = dict(stage='runtime_preflight', outcome='runtime_unavailable',
                  exit_code=None, timed_out=False, launched=False)
    conflicts = overrides(environment, project)
    if conflicts:
        return {**result, 'conflicting_overrides': conflicts}
    try:
        before = snapshot(project, expected_sdk)
        result['before'] = before
        safe_env = {key: environment[key] for key in ('PATH', 'LANG', 'LC_ALL', 'TMPDIR', 'SYSTEMROOT')
                    if key in environment}
        command = [before['interpreter'], '-I', '-B', '-c', IMPORTS]
        result['command'] = command
        process = subprocess.Popen(command, cwd=cycle, env=safe_env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        result['launched'] = True
        result['pid'] = process.pid
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            result['timed_out'] = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=0.25)
            except subprocess.TimeoutExpired as error:
                result['cleanup_incomplete'] = True
                stdout, stderr = error.output or b'', error.stderr or b''
                process.stdout.close()
                process.stderr.close()
                try:
                    process.wait(timeout=0.25)
                except subprocess.TimeoutExpired:
                    result['leader_unreaped'] = True
        result.update(exit_code=process.returncode,
                      stdout=stdout.decode(errors='replace'), stderr=stderr.decode(errors='replace'))
        after = snapshot(project, expected_sdk)
        result['after'] = after
        if before != after:
            raise ValueError('Borrowed runtime metadata changed during preflight')
        if result['timed_out'] or result['exit_code'] != 0:
            return result
        observed = json.loads(result['stdout'], object_pairs_hook=unique_object)
        wanted = {key: before[key] for key in ('executable', 'resolved', 'prefix', 'sdk_version')
                  if key in before}
        wanted['executable'] = before['interpreter']
        if observed != wanted:
            raise ValueError('Import process identity differs from bound runtime')
        result['outcome'] = 'runtime_ready'
    except (OSError, ValueError) as error:
        result['error'] = str(error)
    return result


def native_environment(project, uv, environment):
    """Keep the authorized project configuration; refuse inherited selectors."""
    conflicts = overrides(environment, project)
    if environment.get('UV_NO_CONFIG'):
        conflicts.append('UV_NO_CONFIG')
    if conflicts:
        raise ValueError('Conflicting runtime overrides: ' + ', '.join(conflicts))
    venv = Path(project).absolute() / '.venv'
    return {**environment, 'UV_NO_SYNC': '1', 'UV_NO_ENV_FILE': '1',
            'UV_PYTHON_DOWNLOADS': 'never', 'UV_COMPILE_BYTECODE': '0',
            'PYTHONDONTWRITEBYTECODE': '1', 'UV_PYTHON': str(venv / 'bin/python'),
            'UV_PROJECT_ENVIRONMENT': str(venv), 'VIRTUAL_ENV': str(venv),
            'PATH': str(Path(uv).absolute().parent) + os.pathsep + environment.get('PATH', '')}


def native_binding(project, expected_sdk, uv, admission):
    """Verify retained installed-help admission and bind native launch metadata."""
    if type(admission) is not dict:
        raise ValueError('Runtime admission must be an object')
    if (admission.get('status') != 'read_only_admission_inputs_verified_not_native_runtime_qualification'
            or admission.get('mise_version') != '2026.10.8'
            or admission.get('uv_version') != '0.13.0'
            or admission.get('borrowed_root') != str(Path(project).absolute())):
        raise ValueError('Runtime admission identity mismatch')
    expected_help = ('mise-version.txt', 'mise-run-help.txt', 'uv-version.txt',
                     'uv-run-help.txt', 'uv-run-help-long.txt')
    receipts = admission.get('help_receipts')
    if type(receipts) is not dict:
        raise ValueError('Runtime help receipts must be an object')
    for name in expected_help:
        receipt = receipts.get(name)
        if type(receipt) is not dict:
            raise ValueError('Runtime help receipt must be an object: ' + name)
        if (type(receipt.get('exit_code')) is not int or receipt['exit_code'] != 0
                or not receipt.get('path') or sha(receipt['path']) != receipt.get('sha256')):
            raise ValueError('Runtime admission help binding mismatch: ' + name)
    tasks = tomllib.loads((Path(project) / 'mise.toml').read_text()).get('tasks', {})
    if type(tasks) is not dict:
        raise ValueError('Borrowed native tasks must be an object')
    wanted = {'github-search': 'uv run github-search "$@"',
              'github:diff': 'uv run github-search diff "$@"'}
    if any(type(tasks.get(name)) is not dict for name in wanted):
        raise ValueError('Borrowed native task records must be objects')
    if any(tasks[name].get('run') != script for name, script in wanted.items()):
        raise ValueError('Borrowed native task launch definition mismatch')
    executable = Path(uv).resolve(strict=True)
    return {'runtime': snapshot(project, expected_sdk),
            'uv': {'path': str(Path(uv).absolute()), 'resolved': str(executable), 'sha256': sha(executable)},
            'admission_sha256': hashlib.sha256(json.dumps(admission, sort_keys=True).encode()).hexdigest()}
