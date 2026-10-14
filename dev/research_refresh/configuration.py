"""Explicit local paths for the optional refresh CLI; no discovery or writes."""
import json
import os
from pathlib import Path
import runtime_preflight


def absolute_path(value, label):
    if not isinstance(value, (str, Path)) or not str(value) or not Path(value).is_absolute():
        raise ValueError(label + ' must be an absolute existing path')
    try:
        Path(value).resolve(strict=True)
        return Path(value)
    except (OSError, ValueError, RuntimeError) as error:
        raise ValueError(label + ' must be an absolute existing path') from error


def inside_checkout(path):
    return any((parent / '.git').exists() for parent in (path, *path.parents))


def overlaps(first, second):
    first, second = first.resolve(), second.resolve()
    return first.is_relative_to(second) or second.is_relative_to(first)


def load(state_directory, runtime_config, repository=None):
    """Validate all selections before any caller can lock, write or launch."""
    repository = (repository or Path(__file__).resolve().parents[2]).resolve()
    state = absolute_path(state_directory, 'State directory').resolve()
    config = absolute_path(runtime_config, 'Runtime configuration').resolve()
    if not state.is_dir() or overlaps(state, repository) or inside_checkout(state):
        raise ValueError('State directory must be a separate directory outside Git checkouts')
    if not config.is_file() or config.is_relative_to(repository) or inside_checkout(config.parent):
        raise ValueError('Runtime configuration must be a local file outside Git checkouts')
    try:
        values = json.loads(config.read_text(), object_pairs_hook=runtime_preflight.unique_object)
    except (OSError, ValueError) as error:
        raise ValueError('Runtime configuration must be readable, unambiguous JSON') from error
    keys = {'format_version', 'borrowed_project', 'uv', 'fnox', 'fnox_config', 'mise', 'runtime_admission'}
    if (type(values) is not dict or set(values) != keys
            or type(values.get('format_version')) is not int or values['format_version'] != 1):
        raise ValueError('Runtime configuration has an unsupported format or fields')
    paths = {}
    for key in sorted(keys - {'format_version'}):
        if type(values[key]) is not str:
            raise ValueError('Runtime path fields must be strings')
        paths[key] = absolute_path(values[key], key)
    borrowed = paths['borrowed_project']
    if not borrowed.is_dir() or overlaps(state, borrowed):
        raise ValueError('Borrowed project and state directory must be separate directories')
    for key in ('uv', 'fnox', 'mise', 'fnox_config', 'runtime_admission'):
        if not paths[key].is_file():
            raise ValueError(key + ' must select an existing file')
    for key in ('uv', 'fnox', 'mise'):
        if not os.access(paths[key], os.X_OK):
            raise ValueError(key + ' must select an executable file')
    if paths['uv'].name != 'uv':
        raise ValueError('Selected uv executable must be named uv for native task PATH selection')
    if os.pathsep in str(paths['uv'].parent):
        raise ValueError('Selected uv directory must not contain a PATH separator')
    prefix = [str(paths['fnox']), '--config', str(paths['fnox_config']), '--profile',
              'codex_research', '--no-defaults', '--no-daemon', '--non-interactive',
              'exec', '--', str(paths['mise']), '-C', str(borrowed),
              'run', '--no-deps', '--skip-tools']
    return {'root': state, 'borrowed': borrowed, 'uv': paths['uv'],
            'admission': paths['runtime_admission'], 'prefix': prefix}
