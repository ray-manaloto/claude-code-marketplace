"""Confined, reversible GitHubKit refresh and query experiment runner."""

import argparse
import configuration
import datetime as dt
from contextlib import ExitStack
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import runtime_preflight
import time
import tempfile
import uuid

# Importing this module never selects a runtime or writable state directory.
ROOT = BORROWED = PINNED_UV = RUNTIME_ADMISSION = None
PREFIX = []


def configure(state_directory, runtime_config):
    global ROOT, BORROWED, PINNED_UV, RUNTIME_ADMISSION, PREFIX
    settings = configuration.load(state_directory, runtime_config)
    ROOT, BORROWED = settings['root'], settings['borrowed']
    PINNED_UV, RUNTIME_ADMISSION = settings['uv'], settings['admission']
    PREFIX = settings['prefix']


def confined(value):
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Path must stay inside this workflow')
    return path


def read(path):
    return json.loads(path.read_text())


class NativeLaunchFailure(OSError):
    pass


class NativeOutputFailure(NativeLaunchFailure):
    pass


class StorageFailure(OSError):
    pass


def write_bytes(path, payload):
    if path.is_relative_to(ROOT):
        evidence_path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.' + path.name + '-', delete=False) as output:
            temporary = Path(output.name)
            output.write(payload)
        temporary.replace(path)
        temporary = None  # Successful replacement is the final mutation.
    except OSError as error:
        raise StorageFailure(str(error)) from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass  # Preserve the original writer failure; cleanup is best effort.


def write(path, data):
    write_bytes(path, (json.dumps(data, indent=2) + '\n').encode())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(item):
    if item.get('path'):
        return item['repo_name'] + ':' + item['path']
    return item.get('html_url', '')


def result_items(row):
    return row.get('items', []) + row.get('issues', []) + row.get('discussions', [])


def require(value, kind, label):
    if type(value) is not kind:
        raise ValueError(label + ' has an invalid JSON type')
    return value


def evidence_path(path):
    cursor = ROOT
    for part in path.relative_to(ROOT).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Linked evidence path is not an immutable binding')
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Evidence path resolves outside this workflow')
    return path


def native_item(item, container):
    require(item, dict, 'Result item')
    required = {'repo_name': str, 'html_url': str}
    optional = {}
    if container == 'items':
        optional = {'description': str, 'stars': int, 'topics': list, 'path': str, 'score': float, 'matched_text': str}
    else:
        required.update(number=int, title=str)
        optional = {'comments': int, 'created_at': str, 'body_snippet': str}
        if container == 'issues':
            required.update(state=str, user=str, is_pr=bool)
            optional.update(updated_at=str, closed_at=str, labels=list)
        else:
            required.update(author=str)
            optional.update(category=str)
    for key, kind in required.items():
        require(item[key], kind, 'Item ' + key)
    for key, kind in optional.items():
        value = item.get(key)
        if value is None:
            continue
        if kind is float:
            if type(value) not in (int, float):
                raise ValueError('Item score has an invalid JSON type')
        else:
            require(value, kind, 'Item ' + key)
        if kind is list:
            for entry in value:
                require(entry, str, 'Item ' + key + ' entry')
    # Match generated models: ignore cross-model extras and apply optional defaults.
    defaults = {'topics': [], 'labels': [], 'comments': 0}
    return {**{key: item[key] for key in required},
            **{key: item.get(key, defaults.get(key)) for key in optional}}


def native_delta(base, fresh):
    def indexed(row):
        mapping = {}
        modeled = [native_item(item, container) for container in ('items', 'issues', 'discussions')
                   for item in row.get(container, [])]
        for rank, item in enumerate(modeled, 1):
            if item.get('path'):
                key, title = item['repo_name'] + ':' + item['path'], item['path']
            elif 'number' in item:
                key, title = item['repo_name'] + '#' + str(item['number']), item['title']
            else:
                key, title = item['repo_name'], item.get('description')
            mapping[key] = (rank, title, item['html_url'])
        return mapping
    before, after = indexed(base), indexed(fresh)
    complete = base['is_complete'] and fresh['is_complete']
    expected = {}
    for key in list(after) + [key for key in before if key not in after]:
        previous, current = before.get(key), after.get(key)
        if current is None and (base['error_code'] != 'NONE' or fresh['error_code'] != 'NONE'):
            continue
        status = 'UNCHANGED' if previous and current else ('NEW' if current else 'GONE')
        caveat = None
        if not complete and status != 'UNCHANGED':
            status = 'RANKED_WINDOW_ENTERED' if current else 'RANKED_WINDOW_EXITED'
            caveat = ('Item entered top ranked window; may have existed previously beyond collection ceiling' if current
                      else 'Item fell out of top ranked window; still present on GitHub beyond collection ceiling')
        value = current or previous
        expected[key] = {'search_id': base['search_id'], 'item_id': key, 'status': status,
                         'title_or_path': value[1], 'url': value[2], 'caveat': caveat,
                         'previous_rank': previous[0] if previous else None, 'current_rank': current[0] if current else None}
    return expected


def rows_by_id(values):
    rows = {}
    for row in require(values, list, 'Result rows'):
        require(row, dict, 'Result row')
        sid = require(row['search_id'], str, 'Search ID')
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', sid) or sid in rows:
            raise ValueError('Invalid or duplicate result search ID')
        for key in ('search_type', 'query_fingerprint', 'query_executed', 'error_code'):
            require(row[key], str, key)
        require(row['is_complete'], bool, 'Completeness')
        require(row['timing'], dict, 'Timing')
        arrays = [require(row.get(k, []), list, k) for k in ('items', 'issues', 'discussions')]
        if sum(bool(items) for items in arrays) > 1:
            raise ValueError('Multiple populated result arrays')
        for container in ('items', 'issues', 'discussions'):
            for item in row.get(container, []):
                native_item(item, container)
        for key in ('item_count', 'total_count'):
            if require(row[key], int, key) < 0:
                raise ValueError('Negative result count')
        if row['item_count'] != len(result_items(row)) or not re.fullmatch(r'[0-9a-f]{64}', row['query_fingerprint']):
            raise ValueError('Invalid result count or fingerprint')
        rows[sid] = row
    return rows


def snapshot(manifest):
    data = require(read(evidence_path(manifest)), dict, 'Manifest')
    require(data['run_id'], str, 'Run ID')
    require(data['timestamp'], str, 'Timestamp')
    artifacts = require(data['artifacts'], list, 'Artifacts')
    values, paths = [], set()
    for artifact in artifacts:
        require(artifact, str, 'Artifact path')
        path = evidence_path(ROOT / 'results' / artifact)
        if (path.resolve().parent != manifest.parent.resolve() or path.is_symlink()
                or artifact != str(path.relative_to(ROOT / 'results')) or '..' in Path(artifact).parts
                or path in paths or path.name == 'manifest.json'):
            raise ValueError('Duplicate or unconfined artifact')
        paths.add(path)
        row = require(read(path), dict, 'Artifact row')
        if path.name != row['search_id'] + '.json':
            raise ValueError('Artifact filename/search ID mismatch')
        values.append(row)
    rows = rows_by_id(values)
    successful = [row for row in values if row['error_code'] == 'NONE']
    expected = {'total_searches': len(rows), 'successful_searches': len(successful),
                'failed_searches': len(rows) - len(successful), 'total_items': sum(r['item_count'] for r in successful)}
    if any(require(data[key], int, key) != value for key, value in expected.items()):
        raise ValueError('Manifest/result summary mismatch')
    return data, rows


def validate_search_envelope(response, rows, manifest, process_exit):
    require(response, dict, 'Search stdout')
    if (require(response['exit_code'], int, 'Search envelope exit') != require(process_exit, int, 'Search process exit')
            or process_exit != 0 or response['status'] != 'SUCCESS'
            or response.get('error') is not None or require(response['errors'], list, 'Search errors')):
        raise ValueError('Search envelope outcome mismatch')
    successful = [row for row in rows.values() if row['error_code'] == 'NONE']
    expected = {'total_searches': len(rows), 'successful_searches': len(successful),
                'failed_searches': len(rows) - len(successful), 'total_items_found': sum(row['item_count'] for row in successful)}
    summary = require(response['summary'], dict, 'Search summary')
    if expected['failed_searches'] or any(require(summary[key], int, 'Search summary ' + key) != value for key, value in expected.items()):
        raise ValueError('Search summary/result outcome mismatch')
    for key, value in expected.items():
        if require(manifest['total_items' if key == 'total_items_found' else key], int, 'Manifest summary') != value:
            raise ValueError('Search summary/manifest mismatch')
    timing = require(response['timing'], dict, 'Search timing')
    for key in ('start_time', 'end_time'):
        require(timing[key], str, 'Search timing ' + key)
    require(timing['duration_ns'], int, 'Search timing duration_ns')
    duration = timing['duration_ms']
    try:
        finite = type(duration) in (int, float) and math.isfinite(duration)
    except OverflowError as error:
        raise ValueError('Unrepresentable search timing duration_ms') from error
    if not finite:
        raise ValueError('Invalid search timing duration_ms')
    metadata = require(response['system_info'], dict, 'Search system metadata')
    for key in ('platform', 'python_version', 'cli_version', 'pydantic_version'):
        require(metadata[key], str, 'Search metadata ' + key)


def artifact_hashes(manifest, rows):
    return {sid: digest(manifest.parent / (sid + '.json')) for sid in rows}


def comparison(outcome, baseline, candidate, before_id, after_id, changes, feedback):
    require(outcome, dict, 'Comparison stdout')
    if (outcome.get('status') != 'SUCCESS' or require(outcome.get('exit_code'), int, 'Comparison exit code') != 0 or outcome.get('error')
            or outcome.get('baseline_run_id') != before_id or outcome.get('candidate_run_id') != after_id):
        raise ValueError('Invalid comparison outcome evidence')
    shared = baseline.keys() & candidate.keys()
    drift = (baseline.keys() ^ candidate.keys()) | {sid for sid in shared if baseline[sid]['query_fingerprint'] != candidate[sid]['query_fingerprint']}
    if not drift <= set(changes):
        raise ValueError('Unexpected incompatible query identities')
    queries, seen = require(outcome['queries'], list, 'Comparison queries'), set()
    statuses = {'NEW': 'new_count', 'GONE': 'gone_count', 'RANKED_WINDOW_ENTERED': 'entered_window_count',
                'RANKED_WINDOW_EXITED': 'exited_window_count', 'UNCHANGED': 'unchanged_count'}
    for query in queries:
        require(query, dict, 'Comparison query')
        sid = require(query['search_id'], str, 'Compared search ID')
        if sid in seen or sid not in shared:
            raise ValueError('Duplicate or unexpected comparison query')
        seen.add(sid)
        base, fresh = baseline[sid], candidate[sid]
        expected = {'search_type': base['search_type'], 'query_fingerprint': fresh['query_fingerprint'],
                    'baseline_run_id': before_id, 'candidate_run_id': after_id,
                    'baseline_count': base['item_count'], 'candidate_count': fresh['item_count'],
                    'is_baseline_complete': base['is_complete'], 'is_candidate_complete': fresh['is_complete']}
        if any(require(query[key], type(value), key) != value for key, value in expected.items()):
            raise ValueError('Comparison query is not bound to snapshots')
        expected_items = native_delta(base, fresh)
        counts, item_ids = {key: 0 for key in statuses.values()}, set()
        for item in require(query['items'], list, 'Compared items'):
            require(item, dict, 'Compared item')
            status = require(item['status'], str, 'Item status')
            item_id = require(item['item_id'], str, 'Compared item ID')
            require(item['url'], str, 'Compared item URL')
            if item['search_id'] != sid or status not in statuses or item_id in item_ids:
                raise ValueError('Invalid or duplicate compared item')
            if item_id not in expected_items:
                raise ValueError('Compared item is absent from native snapshot delta')
            for key, value in expected_items[item_id].items():
                actual = item.get(key) if value is None else item[key]
                if actual is not None:
                    require(actual, type(value), 'Compared item ' + key)
                if actual != value:
                    raise ValueError('Compared item does not match native snapshot delta')
            item_ids.add(item_id)
            counts[statuses[status]] += 1
        if item_ids != expected_items.keys():
            raise ValueError('Comparison omits native snapshot delta items')
        if any(require(query[key], int, key) != value for key, value in counts.items()):
            raise ValueError('Comparison item totals mismatch')
    if (seen != shared or require(outcome['total_queries_compared'], int, 'Compared total') != len(shared)
            or require(outcome['incompatible_queries'], int, 'Incompatible total') != len(drift)):
        raise ValueError('Comparison query totals mismatch')
    reasons = {}
    for sid in baseline.keys() | candidate.keys():
        why = ['approved_query_identity_drift'] if sid in drift else []
        for row in (baseline.get(sid), candidate.get(sid)):
            if row is None:
                continue
            why.extend(coverage_reasons(row, feedback.get(sid, {})))
        reasons[sid] = list(dict.fromkeys(why))
    for query in queries:
        why = reasons[query['search_id']]
        query.update(content_claims_eligible=not why, suppression_reasons=why)
        query['suppressed_counts'] = {'new_count': query['new_count'] if why else 0, 'gone_count': query['gone_count'] if why else 0}
        if why:
            query['items'] = [item for item in query['items'] if item['status'] not in ('NEW', 'GONE')]
            query.update({'new_count': 0, 'gone_count': 0})
    outcome['suppressed_queries'] = sorted(sid for sid, why in reasons.items() if why)
    outcome['suppression_reasons'] = {sid: why for sid, why in reasons.items() if why}
    outcome['suppression_reason'] = 'Approved query identity drift' if drift else ('Coverage is not eligible for content claims' if outcome['suppressed_queries'] else None)
    return outcome


def query_contract(search):
    normalized = {key: sorted(search.get(key) or []) for key in ('filenames', 'languages', 'topics')}
    normalized.update({'min_stars': search.get('min_stars'), 'order': (search.get('order') or 'desc').lower(),
                       'query': search['query'].strip(), 'search_type': search['search_type'],
                       'sort': (search.get('sort') or '').lower(), 'target_repo': (search.get('target_repo') or '').strip().lower()})
    fingerprint = hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    parts = [search['query'].strip()]
    if search.get('target_repo'):
        parts.append('repo:' + search['target_repo'])
    for key, qualifier in [('languages', 'language'), ('filenames', 'filename'), ('topics', 'topic')]:
        parts.extend(qualifier + ':' + value for value in search.get(key) or [])
    if search.get('min_stars') is not None:
        parts.append('stars:>=' + str(search['min_stars']))
    if search['search_type'] in ('ISSUE', 'PULL_REQUEST'):
        parts.append('is:issue' if search['search_type'] == 'ISSUE' else 'is:pr')
    return fingerprint, ' '.join(parts)


def bind_catalog(rows, definitions):
    if rows.keys() != definitions.keys():
        raise ValueError('Result IDs differ from selected catalog')
    for sid, row in rows.items():
        if (row['search_type'] != definitions[sid]['search_type']
                or (row['query_fingerprint'], row['query_executed']) != query_contract(definitions[sid])):
            raise ValueError('Result fingerprint/effective query differs from selected catalog')


def check_catalog(catalog, policy):
    searches = require(require(catalog, dict, 'Catalog')['searches'], list, 'Catalog searches')
    ids, definitions = set(), set()
    allowed = {'id', 'description', 'search_type', 'query', 'target_repo', 'topics', 'languages', 'filenames', 'min_stars', 'sort', 'order', 'deep', 'max_pages', 'max_items'}
    sorts = {'CODE': {'indexed'}, 'ISSUE': {'comments', 'reactions', 'created', 'updated'},
             'PULL_REQUEST': {'comments', 'reactions', 'created', 'updated'},
             'TOPIC': {'stars', 'forks', 'help-wanted-issues', 'updated'},
             'REPOSITORY': {'stars', 'forks', 'help-wanted-issues', 'updated'}, 'DISCUSSION': set()}
    for search in searches:
        require(search, dict, 'Catalog search')
        if search.keys() - allowed:
            raise ValueError('Unknown catalog search fields')
        for key in ('id', 'description', 'query', 'search_type'):
            require(search[key], str, key)
        kind = search['search_type']
        if kind not in sorts:
            raise ValueError('Unsupported search type')
        for key in ('target_repo', 'sort', 'order'):
            if search.get(key) is not None:
                require(search[key], str, key)
        for key in ('topics', 'languages', 'filenames'):
            if search.get(key) is not None:
                for value in require(search[key], list, key):
                    require(value, str, key + ' member')
        if search.get('min_stars') is not None and require(search['min_stars'], int, 'Star floor') < 0:
            raise ValueError('Negative star floor')
        for key, default in [('max_pages', 1), ('max_items', 100)]:
            if require(search.get(key, default), int, key) < 1:
                raise ValueError('Invalid pagination/item ceiling')
        if require(search.get('deep', False), bool, 'Deep flag'):
            raise ValueError('Deep-only searches are unsupported here')
        if kind != 'DISCUSSION' and (search.get('sort') is not None and search['sort'] not in sorts[kind]
                or search.get('order') is not None and search['order'] not in ('asc', 'desc')):
            raise ValueError('Unsupported sort/order would silently fall back')
        sid = search['id']
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', sid) or sid in ids:
            raise ValueError('Invalid or duplicate search ID')
        ids.add(sid)
        definition = {k: v for k, v in search.items() if k not in ('id', 'description')}
        key = json.dumps(definition, sort_keys=True)
        if key in definitions:
            raise ValueError('Duplicate query definition')
        definitions.add(key)
        if search.get('deep') or search.get('max_pages', 1) < 1:
            raise ValueError('Deep-only or invalid pagination is unsupported here')
    code_pages = sum(s.get('max_pages', 1) for s in searches if s['search_type'] == 'CODE')
    rest_pages = sum(s.get('max_pages', 1) for s in searches if s['search_type'] in ('ISSUE', 'PULL_REQUEST'))
    if len(ids) > policy['max_active_searches'] or code_pages > policy['max_code_pages_per_run'] or rest_pages > policy['max_issue_pr_pages_per_run']:
        raise ValueError('Catalog exceeds configured search/page budget')
    return {s['id']: s for s in searches}


def check_proposal(proposal, old, new, policy):
    if not old.keys() <= new.keys():
        raise ValueError('Experiments must preserve existing discovery searches')
    changed = {sid for sid in new if old.get(sid) != new[sid]}
    if not changed or len(changed) > policy['max_changed_searches_per_refresh']:
        raise ValueError('Invalid experiment size')
    if len(new.keys() - old.keys()) > policy['max_new_searches_per_refresh']:
        raise ValueError('Too many new searches')
    if changed != set(proposal['changes']):
        raise ValueError('Every changed query needs an explicit evidence record')
    for change in proposal['changes'].values():
        if not change.get('reason') or not change.get('source_urls') or not change.get('expect'):
            raise ValueError('Missing rationale, source or measurable expectation')
        if any(not u.startswith('https://') for u in change['source_urls']):
            raise ValueError('Source citations must be HTTPS URLs')
        if not change['expect'].get('required_urls'):
            raise ValueError('Every experiment needs a previously inspected relevance anchor')
    return changed


def evaluate(proposal, rows):
    failures = []
    for sid, change in proposal['changes'].items():
        row, expected = rows.get(sid, {}), change['expect']
        urls = {i.get('html_url') for i in result_items(row)}
        if row.get('error_code') != 'NONE':
            failures.append(sid + ': query failed or missing')
        if row.get('item_count', 0) < expected.get('min_items', 1):
            failures.append(sid + ': insufficient results')
        if row.get('total_count', 0) > expected.get('max_total', float('inf')):
            failures.append(sid + ': scope still too broad')
        if expected.get('complete') and not row.get('is_complete'):
            failures.append(sid + ': incomplete coverage')
        if not set(expected['required_urls']) <= urls:
            failures.append(sid + ': lost relevance anchor')
    return failures


def coverage_reasons(row, feedback):
    reasons = []
    if row['error_code'] != 'NONE':
        reasons.append('query_error')
    if not row['is_complete']:
        reasons.append('incomplete_coverage')
    if row['total_count'] > row['item_count']:
        reasons.append('collection_capped')
    if feedback.get('unverified_empty') or (row['error_code'] == 'NONE' and not result_items(row)):
        reasons.append('unverified_empty')
    return reasons


def metrics(rows, previous):
    output = {}
    for sid, row in rows.items():
        prior = previous.get(sid, {})
        same = row.get('query_fingerprint') == prior.get('fingerprint')
        ok = row.get('error_code') == 'NONE'
        keys = sorted({identity(i) for i in result_items(row)})
        last_nonempty = prior.get('last_nonempty_items', prior.get('items', 0)) if same else 0
        if ok and keys:
            last_nonempty = len(keys)
        unverified_empty = ok and not keys
        empty_regression = unverified_empty and last_nonempty > 0
        output[sid] = {
            'fingerprint': row.get('query_fingerprint'), 'error_code': row.get('error_code'),
            'items': row.get('item_count', 0), 'total': row.get('total_count', 0),
            'complete': bool(row.get('is_complete')) and ok and not unverified_empty and row['total_count'] <= row['item_count'],
            'native_complete': bool(row.get('is_complete')), 'identities': keys,
            'last_nonempty_items': last_nonempty, 'empty_regression': empty_regression, 'unverified_empty': unverified_empty,
            'recovered_from_empty': bool(same and ok and keys and (prior.get('unverified_empty') or prior.get('empty_regression'))),
            'capped_streak': (prior.get('capped_streak', 0) if same else 0) + 1 if ok and (not row.get('is_complete') or row['total_count'] > row['item_count']) else 0,
            'error_streak': (prior.get('error_streak', 0) if same else 0) + 1 if not ok else 0,
            'empty_streak': (prior.get('empty_streak', 0) if same else 0) + 1 if ok and not keys else 0,
            'unchanged_streak': prior.get('unchanged_streak', 0) + 1 if same and ok and not unverified_empty and keys == prior.get('identities') else 0,
        }
    return output


def command(arguments, output, timeout):
    with ExitStack() as streams:
        try:
            stdout = streams.enter_context(output.with_suffix('.json').open('w'))
            stderr = streams.enter_context(output.with_suffix('.stderr').open('w'))
        except OSError as error:
            raise NativeOutputFailure(str(error)) from error
        try:
            child = subprocess.Popen(PREFIX + arguments, cwd=ROOT, env=runtime_preflight.native_environment(BORROWED, PINNED_UV, os.environ), stdout=stdout, stderr=stderr, start_new_session=True)
        except OSError as error:
            raise NativeLaunchFailure(str(error)) from error
        try:
            return child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            return 124


def immutable(run_id):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', require(run_id, str, 'Run ID')):
        raise ValueError('Invalid immutable run ID')
    matches = list(evidence_path(ROOT / 'results/runs').glob('*_' + run_id))
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous immutable run')
    if matches[0].is_symlink() or matches[0].resolve().parent != (ROOT / 'results/runs').resolve():
        raise ValueError('Unconfined immutable run')
    manifest = matches[0] / 'manifest.json'
    data, rows = snapshot(manifest)
    if data['run_id'] != run_id:
        raise ValueError('Immutable run identity mismatch')
    return manifest, rows


def accepted_baseline(state, receipt, policy):
    bound = state.get('accepted_baseline')
    if bound is not None:
        require(bound, dict, 'Accepted baseline')
    run_id = (bound or {}).get('run_id', state.get('last_run_id'))
    if not run_id:
        if 'pending_baseline_initialization' in state:
            pending = require(state['pending_baseline_initialization'], dict, 'Coverage-only initialization')
            cycle = require(pending['cycle'], str, 'Coverage cycle')
            if not re.fullmatch(r'[0-9TZ]+-[0-9a-f]+', cycle) or bound is not None or 'last_cycle' in state or 'last_run_id' in state:
                raise ValueError('Invalid coverage-only initialization identity')
            path = evidence_path(ROOT / state['coverage_commit']['receipt']) if 'commit_format_version' in state else evidence_path(ROOT / 'cycles' / cycle / 'receipt.json')
            previous = require(read(path), dict, 'Coverage-only receipt')
            manifest, rows = immutable(pending['run_id'])
            catalog = evidence_path(ROOT / 'cycles' / cycle / 'catalog-used.json')
            bindings = {'manifest_sha256': digest(manifest), 'artifact_sha256': artifact_hashes(manifest, rows), 'catalog_sha256': digest(catalog)}
            if any(pending[key] != value for key, value in bindings.items()):
                raise ValueError('Coverage-only initialization evidence changed')
            bind_catalog(rows, check_catalog(read(catalog), policy))
            warnings = {sid: coverage_reasons(row, {}) for sid, row in rows.items() if coverage_reasons(row, {})}
            if (previous.get('cycle') != cycle or previous.get('run_id') != pending['run_id']
                    or previous.get('attempt_status') != 'accepted_with_coverage_warning'
                    or require(previous.get('native_exit_code'), int, 'Coverage native exit') != 0
                    or require(previous.get('runner_exit_code'), int, 'Coverage runner exit') != 2
                    or previous.get('fresh_snapshot_accepted') is not False or previous.get('comparison_state') != 'suppressed'
                    or previous.get('diff_stdout') or not warnings
                    or require(previous.get('coverage_warning_queries'), dict, 'Coverage warnings') != warnings
                    or require(previous.get('catalog_binding'), dict, 'Coverage catalog binding').get('catalog_sha256') != bindings['catalog_sha256']
                    or previous.get('manifest_sha256') != bindings['manifest_sha256'] or previous.get('artifact_sha256') != bindings['artifact_sha256']):
                raise ValueError('Coverage-only initialization lacks matched warning receipt')
            receipt['initialization_resume'] = {'cycle': cycle, 'receipt_sha256': digest(path)}
            return None
        if state.get('queries'):
            raise ValueError('Accepted history has no verifiable baseline')
        return None
    manifest, rows = immutable(run_id)
    hashes = artifact_hashes(manifest, rows)
    receipt['baseline_artifact_sha256'] = hashes
    sha = digest(manifest)
    if bound:
        if bound['manifest_sha256'] != sha or bound.get('artifact_sha256', hashes) != hashes:
            raise ValueError('Accepted baseline manifest changed')
    else:
        path = confined('cycles/' + state['last_cycle'] + '/receipt.json')
        previous = read(path)
        require(previous, dict, 'Legacy acceptance receipt')
        if 'attempt_status' in previous and previous['attempt_status'] != 'accepted':
            raise ValueError('Legacy receipt has no accepted outcome')
        require(previous.get('native_exit_code'), int, 'Legacy native exit')
        for key in ('diff_exit_code', 'runner_exit_code'):
            if key in previous:
                require(previous[key], int, 'Legacy ' + key)
        if 'fresh_snapshot_accepted' in previous and previous['fresh_snapshot_accepted'] is not True:
            raise ValueError('Legacy receipt explicitly denies acceptance')
        for key in ('failed', 'experiment_failures', 'unverified_empty_queries'):
            if key in previous:
                require(previous[key], list, key)
        if (previous.get('cycle') != state['last_cycle'] or previous.get('run_id') != run_id
                or previous.get('native_exit_code') != 0 or previous.get('diff_exit_code', 0) != 0
                or previous.get('runner_exit_code', 0) != 0 or previous.get('experiment_failures')
                or previous.get('unverified_empty_queries') or previous.get('failed')
                or previous.get('attempt_status') in ('failed', 'incomplete')):
            raise ValueError('Legacy acceptance lacks a successful bound receipt')
        receipt['baseline_migration'] = {'run_id': run_id, 'receipt': str(path.relative_to(ROOT)),
                                         'receipt_sha256': digest(path), 'manifest_sha256': sha}
    catalog = evidence_path(ROOT / 'cycles' / state['last_cycle'] / 'catalog-used.json')
    if catalog.exists():
        if bound and 'catalog_sha256' in bound and bound['catalog_sha256'] != digest(catalog):
            raise ValueError('Accepted selected catalog changed')
        bind_catalog(rows, check_catalog(read(catalog), policy))
        receipt['baseline_catalog_binding'] = {'status': 'verified', 'catalog': str(catalog.relative_to(ROOT)), 'catalog_sha256': digest(catalog)}
    else:
        receipt['baseline_catalog_binding'] = {'status': 'unavailable', 'reason': 'Required historical selected catalog is missing'}
        raise ValueError('Accepted selected catalog is missing; restore exact retained request evidence')
    return manifest


def promoted_drift(state, policy, active, active_sha):
    """Query IDs that committed catalog-only promotions changed after the fixed accepted baseline."""
    marker = state.get('coverage_commit')
    if marker is None or 'accepted_baseline' not in state:
        return set()
    if require(verify_commit(marker).get('catalog_binding'), dict, 'Coverage catalog binding').get('catalog_sha256') != active_sha:
        return set()  # Only a catalog committed through a runner cycle approves identity drift.
    accepted = check_catalog(read(evidence_path(ROOT / 'cycles' / state['last_cycle'] / 'catalog-used.json')), policy)
    return {sid for sid in active if accepted.get(sid) != active[sid]}


def promote(cycle, canonical, receipt, old, new, proposal, state, state_path):
    receipt['failed_stage'] = 'promotion_intent'
    changes = evidence_path(ROOT / 'search-changes.jsonl')
    appended = ''.join(json.dumps({'cycle': cycle.name, 'verification_run_id': receipt['run_id'],
                                   'search_id': sid, 'before': old.get(sid), 'after': new[sid], **change}) + '\n'
                       for sid, change in proposal['changes'].items()).encode()
    mutations = []
    for label, target, after in [('catalog', canonical, (cycle / 'catalog-used.json').read_bytes()),
                                  ('changelog', changes, (changes.read_bytes() if changes.exists() else b'') + appended)]:
        existed = target.exists()
        before = target.read_bytes() if existed else b''
        before_path = cycle / ('promotion-before-' + label + '.bin')
        after_path = cycle / ('promotion-after-' + label + '.bin')
        write_bytes(before_path, before)
        write_bytes(after_path, after)
        mutations.append({'path': str(target.relative_to(ROOT)), 'before_exists': existed,
                          'before': before_path.name, 'before_sha256': digest(before_path),
                          'after': after_path.name, 'after_sha256': digest(after_path)})
    if digest(canonical) != receipt['catalog_sha256_before']:
        raise ValueError('Catalog changed before promotion intent')
    start = require(read(cycle / 'start-intent.json'), dict, 'Promotion start intent')
    write(cycle / 'promotion-intent.json', {'format_version': 1, 'cycle': cycle.name, 'mutations': mutations,
          'start_intent_sha256': digest(cycle / 'start-intent.json'), 'accepted_projection_sha256': start['accepted_projection_sha256'],
          'predecessors': start['predecessors']})
    receipt['promotion_intent_sha256'] = digest(cycle / 'promotion-intent.json')
    state['recovery_admission'] = {'cycle': cycle.name, 'start_intent_sha256': digest(cycle / 'start-intent.json'),
                                 'promotion_intent_sha256': receipt['promotion_intent_sha256'], 'predecessors': start['predecessors'],
                                 'accepted_projection_sha256': start['accepted_projection_sha256'], 'catalog_before_sha256': start['catalog_before_sha256']}
    write(state_path, state)  # Persist exact journal admission before either promoted mutation.
    receipt['recovery_admission'] = state['recovery_admission']
    for mutation in mutations:
        target = evidence_path(ROOT / mutation['path'])
        if target.exists() != mutation['before_exists'] or (target.exists() and digest(target) != mutation['before_sha256']):
            raise ValueError('Concurrent edit before promotion: ' + mutation['path'])
        receipt['failed_stage'] = 'promotion_' + ('catalog' if target == canonical else 'changelog')
        write_bytes(target, (cycle / mutation['after']).read_bytes())
    receipt['promoted'] = True


def rollback(cycle, receipt):
    intent = cycle / 'promotion-intent.json'
    receipt['promoted'] = False
    if not intent.exists():
        return
    conflicts = []
    try:
        if digest(intent) != receipt.get('promotion_intent_sha256'):
            raise ValueError('Promotion intent digest changed')
        data = require(read(intent), dict, 'Promotion intent')
        mutations = require(data['mutations'], list, 'Promotion mutations')
        for mutation in reversed(mutations):
            require(mutation, dict, 'Promotion mutation')
            target = evidence_path(ROOT / mutation['path'])
            before = cycle / mutation['before']
            current = digest(target) if target.exists() else None
            original = mutation['before_sha256'] if mutation['before_exists'] else None
            if current == original:
                continue
            if current != mutation['after_sha256'] or digest(before) != mutation['before_sha256']:
                conflicts.append(mutation['path'])
                continue
            try:
                if mutation['before_exists']:
                    write_bytes(target, before.read_bytes())
                else:
                    target.unlink()
            except OSError:
                conflicts.append(mutation['path'])
        receipt['residual_mutations'] = {}
        for mutation in mutations:
            target = evidence_path(ROOT / mutation['path'])
            current = digest(target) if target.exists() else None
            original = mutation['before_sha256'] if mutation['before_exists'] else None
            if current != original:
                receipt['residual_mutations'][mutation['path']] = {'sha256': current, 'matches_candidate': current == mutation['after_sha256']}
        receipt['catalog_sha256_after'] = digest(ROOT / 'searches.json')
    except (OSError, ValueError, KeyError, TypeError) as error:
        conflicts.append('intent: ' + str(error))
        receipt['residual_mutations'] = {'unverified': str(error)}
    receipt['rollback_conflicts'] = conflicts
    receipt['rollback_status'] = 'conflict' if conflicts else 'restored'


def bind_outputs(cycle, receipt):
    for label, file in [('stdout', 'response.json'), ('stderr', 'response.stderr'),
                        ('diff_stdout', 'diff.json'), ('diff_stderr', 'diff.stderr')]:
        path = cycle / file
        receipt[label + '_available'] = path.exists()
        if path.exists():
            receipt[label] = str(path.relative_to(ROOT))
            receipt[label + '_sha256'] = digest(evidence_path(path))
        else:
            receipt.setdefault(label, None)
            receipt[label + '_sha256'] = None


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def projection_digest(state, baseline=False):
    keys = ('accepted_baseline', 'last_run_id', 'last_cycle')
    if not baseline:
        keys += ('queries', 'pending_baseline_initialization', 'baseline_legacy')
    return hashlib.sha256(canonical_bytes({key: state[key] for key in keys if key in state})).hexdigest()


def event_records(path):
    path = evidence_path(path)
    raw = path.read_bytes() if path.exists() else b''
    if raw and not raw.endswith(b'\n'):
        raise ValueError('Partial event tail')
    records = {}
    for line in raw.splitlines(keepends=True):
        value = json.loads(line)
        if not isinstance(value, dict) or not isinstance(value.get('cycle'), str) or not value['cycle']:
            raise ValueError('Invalid event record')
        if value['cycle'] in records:
            raise ValueError('Duplicate event cycle')
        if 'format_version' in value:
            if type(value['format_version']) is not int or value['format_version'] != 1:
                raise ValueError('Unsupported event format')
            if not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}', value['cycle']):
                raise ValueError('Invalid modern event cycle')
            if set(value) != {'format_version', 'cycle', 'outcome', 'receipt', 'receipt_sha256'}:
                raise ValueError('Invalid event fields')
            if value['outcome'] not in ('accepted', 'accepted_with_coverage_warning', 'failed', 'incomplete'):
                raise ValueError('Invalid event outcome')
            if value['receipt'] != 'cycles/' + value['cycle'] + '/receipt-precommit.json':
                raise ValueError('Invalid event receipt reference')
            evidence_path(ROOT / value['receipt'])
            if not isinstance(value['receipt_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', value['receipt_sha256']):
                raise ValueError('Invalid event receipt digest')
            if line != canonical_bytes(value):
                raise ValueError('Noncanonical event bytes')
        records[value['cycle']] = line
    return records


def verify_commit(marker, baseline=False):
    marker = require(marker, dict, 'Commitment marker')
    keys = {'format_version', 'cycle', 'outcome', 'receipt', 'receipt_sha256', 'event_sha256'}
    if set(marker) != keys | ({'projection_sha256'} if baseline else set()):
        raise ValueError('Invalid commitment fields')
    if require(marker['format_version'], int, 'Commitment version') != 1:
        raise ValueError('Unsupported commitment version')
    event = {key: marker[key] for key in keys if key != 'event_sha256'}
    raw = canonical_bytes(event)
    if event_records(ROOT / 'learning-events.jsonl').get(marker['cycle']) != raw:
        raise ValueError('Missing or changed committed event')
    if marker['event_sha256'] != hashlib.sha256(raw).hexdigest():
        raise ValueError('Committed event digest mismatch')
    path = evidence_path(ROOT / marker['receipt'])
    if digest(path) != marker['receipt_sha256']:
        raise ValueError('Committed receipt digest mismatch')
    intent = require(read(path), dict, 'Committed receipt')
    if require(intent.get('format_version'), int, 'Receipt version') != 1:
        raise ValueError('Unsupported committed receipt version')
    outcome = intent.get('attempt_status')
    if intent.get('cycle') != marker['cycle'] or outcome != marker['outcome']:
        raise ValueError('Committed receipt/event correspondence mismatch')
    native = intent.get('native_exit_code')
    if native is not None:
        require(native, int, 'Committed native exit')
    elif intent.get('provider_invoked') is not False:
        raise ValueError('Null native exit lacks pre-native evidence')
    elif intent.get('failed_stage') == 'runtime_binding':
        verify_pre_native_binding(intent)
    elif intent.get('failed_stage') not in ('cycle_preparation', 'output_admission', 'baseline_resolution', 'search', 'runtime_preflight'):
        raise ValueError('Null native exit lacks pre-native evidence')
    runner = require(intent.get('runner_exit_code'), int, 'Committed runner exit')
    fresh = require(intent.get('fresh_snapshot_accepted'), bool, 'Committed acceptance')
    if outcome == 'accepted':
        valid = native == 0 and runner == 0 and fresh
    elif outcome == 'accepted_with_coverage_warning':
        valid = native == 0 and runner == 2 and not fresh
    else:
        valid = outcome in ('failed', 'incomplete') and runner != 0 and not fresh
    if 'diff_exit_code' in intent:
        diff = require(intent['diff_exit_code'], int, 'Committed comparison exit')
        valid = valid and (diff == 0 or outcome in ('failed', 'incomplete'))
    if outcome in ('accepted', 'accepted_with_coverage_warning'):
        warnings = require(intent.get('coverage_warning_queries'), dict, 'Committed coverage warnings')
        valid = valid and bool(warnings) == (outcome == 'accepted_with_coverage_warning')
        valid = valid and not require(intent.get('experiment_failures'), list, 'Committed experiment failures')
        valid = valid and intent.get('comparison_state') in ('baseline_established', 'compared', 'suppressed')
    if not valid or (baseline and outcome != 'accepted'):
        raise ValueError('Invalid committed outcome/exit correspondence')
    return intent


def immutable_record(path, value):
    payload = canonical_bytes(value)
    path = evidence_path(path)
    if path.exists():
        if path.read_bytes() != payload:
            raise ValueError('Conflicting or partial recovery record')
    else:
        write_bytes(path, payload)
    return hashlib.sha256(payload).hexdigest()


def recovery_plan(cycle, state):
    start = require(read(evidence_path(cycle / 'start-intent.json')), dict, 'Recovery start')
    journal = evidence_path(cycle / 'promotion-intent.json')
    mutations = require(read(journal), dict, 'Recovery journal')['mutations'] if journal.exists() else []
    return {'format_version': 1, 'cycle': cycle.name, 'start_intent_sha256': digest(cycle / 'start-intent.json'),
            'promotion_intent_sha256': digest(journal) if journal.exists() else None, 'mutations': mutations,
            'accepted_projection_sha256': start['accepted_projection_sha256'], 'catalog_before_sha256': start['catalog_before_sha256'],
            'predecessors': start['predecessors'], 'predecessor_recovery_commit': state.get('recovery_commit')}


def recovered_history(state, reachable):
    recovered, marker = {}, state.get('recovery_commit')
    while marker is not None:
        marker = require(marker, dict, 'Recovery commitment')
        if set(marker) != {'cycle', 'receipt', 'receipt_sha256'}:
            raise ValueError('Invalid recovery commitment fields')
        cycle = require(marker['cycle'], str, 'Recovery cycle')
        if not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}', cycle) or cycle in recovered or marker['receipt'] != 'cycles/' + cycle + '/recovery-result.json':
            raise ValueError('Invalid or duplicate recovery cycle')
        path = evidence_path(ROOT / marker['receipt'])
        if digest(path) != marker['receipt_sha256']:
            raise ValueError('Recovery result digest mismatch')
        result = require(read(path), dict, 'Recovery result')
        if (set(result) != {'format_version', 'cycle', 'attempt_status', 'recovery_intent_sha256'}
                or require(result['format_version'], int, 'Recovery version') != 1
                or result['cycle'] != cycle or result['attempt_status'] != 'recovered' or path.read_bytes() != canonical_bytes(result)):
            raise ValueError('Invalid recovery result')
        intent_path = evidence_path(path.with_name('recovery-intent.json'))
        if digest(intent_path) != result['recovery_intent_sha256']:
            raise ValueError('Recovery intent digest mismatch')
        plan = require(read(intent_path), dict, 'Recovery intent')
        expected = recovery_plan(path.parent, {**state, 'recovery_commit': plan.get('predecessor_recovery_commit')})
        if plan != expected or intent_path.read_bytes() != canonical_bytes(plan) or require(plan['format_version'], int, 'Recovery intent version') != 1:
            raise ValueError('Recovery plan binding changed')
        if cycle in reachable:
            raise ValueError('Recovery cannot supersede a committed query attempt')
        root = marker == state.get('recovery_commit')
        linked = any(value.get('predecessor_recovery_commit') == marker for value in reachable.values())
        if root and not linked:
            if plan['accepted_projection_sha256'] != projection_digest(state):
                raise ValueError('Recovery acceptance projection changed')
            for mutation in plan['mutations']:
                target = evidence_path(ROOT / mutation['path'])
                original = mutation['before_sha256'] if mutation['before_exists'] else None
                if (digest(target) if target.exists() else None) != original:
                    raise ValueError('Recovery completion has residual target changes')
        recovered[cycle] = plan
        marker = plan['predecessor_recovery_commit']
    return recovered


def recover_interrupted(state, state_path, history):
    cycle = ROOT / 'cycles' / history['blocked'][0]
    diagnostic = {'cycle': cycle.name, 'attempt_status': 'incomplete', 'runner_exit_code': 2, 'failed_stage': 'startup_recovery'}
    try:
        if len(history['blocked']) != 1 or history['cycles'][cycle.name] != 'interrupted':
            raise ValueError('Unknown or ambiguous interruption has no rollback authority')
        plan = recovery_plan(cycle, state)
        if plan['accepted_projection_sha256'] != projection_digest(state) or plan['predecessors'] != {key: state.get(key + '_commit') for key in ('terminal', 'baseline', 'coverage')} or state.get('attempt_start_commit') != {'cycle': cycle.name, 'start_intent_sha256': plan['start_intent_sha256']}:
            raise ValueError('Recovery start admission changed')
        if plan['promotion_intent_sha256'] is not None and state.get('recovery_admission') != {key: plan[key] for key in ('cycle', 'start_intent_sha256', 'promotion_intent_sha256', 'predecessors', 'accepted_projection_sha256', 'catalog_before_sha256')}:
            raise ValueError('Recovery journal admission changed')
        plan_sha = immutable_record(cycle / 'recovery-intent.json', plan)
        result = {'format_version': 1, 'cycle': cycle.name, 'attempt_status': 'recovered', 'recovery_intent_sha256': plan_sha}
        result_path = evidence_path(cycle / 'recovery-result.json')
        if result_path.exists():
            immutable_record(result_path, result)  # Reject conflicting completion before any rollback.
        if plan['mutations'] and [m['path'] for m in plan['mutations']] != ['searches.json', 'search-changes.jsonl']:
            raise ValueError('Recovery target whitelist mismatch')
        if not plan['mutations'] and digest(ROOT / 'searches.json') != plan['catalog_before_sha256']:
            raise ValueError('Unowned catalog change during non-promoting attempt')
        for mutation in reversed(plan['mutations']):
            target = evidence_path(ROOT / mutation['path'])
            current = digest(target) if target.exists() else None
            original = mutation['before_sha256'] if mutation['before_exists'] else None
            if current == original:
                continue
            if current != mutation['after_sha256']:
                raise ValueError('Recovery preserves external edit: ' + mutation['path'])
            before = evidence_path(cycle / mutation['before'])
            if digest(before) != mutation['before_sha256']:
                raise ValueError('Recovery preimage digest mismatch')
            if mutation['before_exists']:
                write_bytes(target, before.read_bytes())
            else:
                target.unlink()
        result_sha = immutable_record(result_path, result)
        updated = {**state, 'recovery_commit': {'cycle': cycle.name, 'receipt': str(result_path.relative_to(ROOT)), 'receipt_sha256': result_sha}}
        write(state_path, updated)
        diagnostic['recovery_status'] = 'recovered'
    except (OSError, ValueError, KeyError, TypeError) as error:
        diagnostic['recovery_status'] = 'blocked'
        diagnostic['error'] = str(error)
    try:
        write(cycle / 'recovery-diagnostic.json', diagnostic)
    except OSError:
        pass  # Retained intent/result are immutable; diagnostic failure cannot grant completion.
    print(json.dumps(diagnostic))
    return 2  # Recovery is an explicit non-query turn; acceptance and cooldown are preserved.


def startup_history(state):
    reachable, frontier = {}, []
    pending = [(state[key + '_commit'], key == 'baseline', frozenset()) for key in ('terminal', 'baseline', 'coverage') if key + '_commit' in state]
    while pending:
        marker, baseline, ancestors = pending.pop()
        marker = require(marker, dict, 'Historical commitment')
        cycle = require(marker.get('cycle'), str, 'Historical cycle')
        if cycle in ancestors:
            raise ValueError('Cyclic commitment history')
        intent = verify_commit(marker, baseline=baseline)
        if cycle in reachable:
            if reachable[cycle] != intent:
                raise ValueError('Conflicting historical commitment')
            continue
        reachable[cycle] = intent
        for key in ('terminal', 'baseline', 'coverage'):
            field = 'predecessor_' + key + '_commit'
            if field not in intent:
                frontier.append(cycle + ':' + key)
            elif intent[field] is not None:
                pending.append((intent[field], key == 'baseline', ancestors | {cycle}))
    for cycle, intent in reachable.items():
        for label in ('preparation', 'start', 'promotion'):
            field = label + '_intent_sha256'
            if field in intent:  # Historical absence is a frontier, explicit references are mandatory.
                expected = require(intent[field], str, 'Committed artifact digest')
                if not re.fullmatch(r'[0-9a-f]{64}', expected):
                    raise ValueError('Invalid committed artifact digest')
                path = evidence_path(ROOT / 'cycles' / cycle / (label + '-intent.json'))
                if digest(path) != expected:
                    raise ValueError('Missing or changed committed ' + label + ' intent')
                value = require(read(path), dict, 'Committed ' + label + ' intent')
                if value.get('cycle') != cycle:
                    raise ValueError('Committed artifact cycle mismatch')
    if 'recovery_admission' in state:
        admission = require(state['recovery_admission'], dict, 'Persisted recovery admission')
        if set(admission) != {'cycle', 'start_intent_sha256', 'promotion_intent_sha256', 'predecessors', 'accepted_projection_sha256', 'catalog_before_sha256'}:
            raise ValueError('Invalid recovery admission fields')
        cycle = require(admission['cycle'], str, 'Recovery admission cycle')
        if not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}', cycle):
            raise ValueError('Invalid recovery admission cycle')
        for label in ('start', 'promotion'):
            if digest(evidence_path(ROOT / 'cycles' / cycle / (label + '-intent.json'))) != admission[label + '_intent_sha256']:
                raise ValueError('Persisted recovery artifact missing or changed')
        start = require(read(evidence_path(ROOT / 'cycles' / cycle / 'start-intent.json')), dict, 'Recovery start intent')
        if any(admission[key] != start.get(key) for key in ('predecessors', 'accepted_projection_sha256', 'catalog_before_sha256')):
            raise ValueError('Recovery admission/start mismatch')
    recovered = recovered_history(state, reachable)
    records = event_records(ROOT / 'learning-events.jsonl')
    classified = {cycle: 'committed' if cycle == state.get('terminal_commit', {}).get('cycle') else 'superseded' for cycle in reachable}
    cycles = evidence_path(ROOT / 'cycles')
    if 'attempt_start_commit' in state:
        marker = require(state['attempt_start_commit'], dict, 'Persisted attempt admission')
        if set(marker) != {'cycle', 'start_intent_sha256'} or not isinstance(marker.get('cycle'), str) or not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}', marker['cycle']):
            raise ValueError('Invalid persisted attempt admission')
        if digest(evidence_path(cycles / marker['cycle'] / 'start-intent.json')) != marker['start_intent_sha256']:
            raise ValueError('Persisted start binding missing or changed')
    if cycles.exists():
        for path in sorted(cycles.iterdir()):
            evidence_path(path)
            if not path.is_dir():
                raise ValueError('Unexpected cycle entry')
            start_path, intent_path = path / 'start-intent.json', path / 'receipt-precommit.json'
            preparation = path / 'preparation-intent.json'
            if preparation.exists():
                prepared = require(read(evidence_path(preparation)), dict, 'Preparation intent')
                if set(prepared) != {'format_version', 'cycle', 'catalog_before_sha256'} or require(prepared['format_version'], int, 'Preparation version') != 1 or prepared['cycle'] != path.name:
                    raise ValueError('Invalid preparation intent')
                if path.name in reachable and reachable[path.name].get('preparation_intent_sha256') != digest(preparation):
                    raise ValueError('Committed preparation binding changed')
            start = None
            if start_path.exists():
                start = require(read(evidence_path(start_path)), dict, 'Start intent')
                expected = {'format_version', 'cycle', 'accepted_projection_sha256', 'catalog_before_sha256', 'catalog_used_sha256', 'predecessors'}
                if (set(start) != expected or require(start['format_version'], int, 'Start version') != 1
                        or start['cycle'] != path.name or not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}', path.name)):
                    raise ValueError('Invalid start intent')
                for label in ('before', 'used'):
                    if digest(evidence_path(path / ('catalog-' + label + '.json'))) != start['catalog_' + label + '_sha256']:
                        raise ValueError('Start catalog binding changed')
                predecessors = require(start['predecessors'], dict, 'Start predecessors')
                if set(predecessors) != {'terminal', 'baseline', 'coverage'}:
                    raise ValueError('Invalid start predecessors')
                for key, marker in predecessors.items():
                    if marker is not None:
                        verify_commit(marker, baseline=key == 'baseline')
                require(start['accepted_projection_sha256'], str, 'Start projection')
            journal = path / 'promotion-intent.json'
            if journal.exists() and start is not None:
                value = require(read(evidence_path(journal)), dict, 'Bound promotion intent')
                if (require(value.get('format_version'), int, 'Promotion version') != 1 or value.get('cycle') != path.name
                        or value.get('start_intent_sha256') != digest(start_path)
                        or value.get('accepted_projection_sha256') != start['accepted_projection_sha256']
                        or value.get('predecessors') != start['predecessors']):
                    raise ValueError('Promotion/start admission binding changed')
                mutations = require(value.get('mutations'), list, 'Bound promotion mutations')
                if [m.get('path') for m in mutations if isinstance(m, dict)] != ['searches.json', 'search-changes.jsonl']:
                    raise ValueError('Invalid promotion target set')
                for mutation in mutations:
                    require(mutation['before_exists'], bool, 'Promotion preimage existence')
                    for label in ('before', 'after'):
                        filename = mutation[label]
                        if require(filename, str, 'Promotion artifact') != 'promotion-' + label + '-' + ('catalog' if mutation['path'] == 'searches.json' else 'changelog') + '.bin':
                            raise ValueError('Invalid promotion artifact reference')
                        if digest(evidence_path(path / filename)) != mutation[label + '_sha256']:
                            raise ValueError('Promotion artifact changed')
                if mutations[0]['before_sha256'] != start['catalog_before_sha256'] or mutations[0]['after_sha256'] != start['catalog_used_sha256']:
                    raise ValueError('Promotion catalog was not admitted')
            if path.name in reachable:
                if journal.exists() and start is not None and reachable[path.name].get('promotion_intent_sha256') != digest(journal):
                    raise ValueError('Committed promotion journal changed')
                if start is not None and start['predecessors'] != {key: reachable[path.name].get('predecessor_' + key + '_commit') for key in ('terminal', 'baseline', 'coverage')}:
                    raise ValueError('Committed start predecessor mismatch')
                if reachable[path.name].get('start_intent_sha256') is not None and (start is None or reachable[path.name]['start_intent_sha256'] != digest(start_path)):
                    raise ValueError('Committed start evidence changed')
                continue
            if path.name in recovered:
                classified[path.name] = 'recovered'
                continue
            intent = require(read(evidence_path(intent_path)), dict, 'Uncommitted intent') if intent_path.exists() else None
            diagnostic = intent is not None and intent.get('prior_commitments_validated') is False and intent.get('provider_invoked') is False
            if diagnostic and not journal.exists() and not (path / 'catalog-before.json').exists() and start is None:
                if intent.get('catalog_sha256_before') != digest(ROOT / 'searches.json') or path.name not in records:
                    raise ValueError('Unverified admission diagnostic')
                event = json.loads(records[path.name])
                verify_commit({**event, 'event_sha256': hashlib.sha256(records[path.name]).hexdigest()})
                classified[path.name] = 'admission_diagnostic'
            elif start is not None:
                if start['accepted_projection_sha256'] != projection_digest(state) or start['predecessors'] != {key: state.get(key + '_commit') for key in ('terminal', 'baseline', 'coverage')}:
                    raise ValueError('Interrupted start does not descend from preserved acceptance')
                marker = require(state.get('attempt_start_commit'), dict, 'Interrupted start commitment')
                if marker != {'cycle': path.name, 'start_intent_sha256': digest(start_path)}:
                    raise ValueError('Interrupted start lacks persisted admission')
                if journal.exists():
                    admission = require(state.get('recovery_admission'), dict, 'Interrupted promotion admission')
                    if admission != {'cycle': path.name, 'start_intent_sha256': digest(start_path), 'promotion_intent_sha256': digest(journal), 'predecessors': start['predecessors'], 'accepted_projection_sha256': start['accepted_projection_sha256'], 'catalog_before_sha256': start['catalog_before_sha256']}:
                        raise ValueError('Interrupted journal lacks persisted admission')
                classified[path.name] = 'interrupted'
            elif preparation.exists() or (intent is not None and intent.get('predecessor_terminal_commit') is not None):
                classified[path.name] = 'unknown'
            else:
                classified[path.name] = 'limited_history'
                frontier.append(path.name)
    for cycle, raw in records.items():
        if cycle not in classified and 'format_version' in json.loads(raw):
            classified[cycle] = 'unknown'
    return {'cycles': classified, 'limited_history_frontier': sorted(set(frontier)),
            'blocked': sorted(cycle for cycle, kind in classified.items() if kind in ('interrupted', 'unknown'))}


def original_legacy_receipt(state):
    path = evidence_path(ROOT / 'cycles' / require(state.get('last_cycle'), str, 'Legacy baseline cycle') / 'receipt.json')
    value = require(read(path), dict, 'Original legacy baseline receipt')
    immutable_receipt = evidence_path(path.with_name('receipt-precommit.json'))
    if immutable_receipt.exists() and 'format_version' in require(read(immutable_receipt), dict, 'Historical immutable receipt'):
        raise ValueError('Modern immutable baseline cannot become legacy')
    if ('format_version' in value or value.get('cycle') != state['last_cycle']
            or value.get('run_id') != state.get('last_run_id')
            or require(value.get('native_exit_code'), int, 'Original legacy native exit') != 0):
        raise ValueError('Baseline is not original unversioned legacy acceptance')
    for key in ('diff_exit_code', 'runner_exit_code'):
        if key in value and require(value[key], int, 'Original legacy ' + key) != 0:
            raise ValueError('Original legacy receipt failed')
    if ('attempt_status' in value and value['attempt_status'] != 'accepted') or ('fresh_snapshot_accepted' in value and value['fresh_snapshot_accepted'] is not True):
        raise ValueError('Original legacy receipt denies acceptance')
    for key in ('failed', 'experiment_failures', 'unverified_empty_queries'):
        if key in value and require(value[key], list, 'Original legacy ' + key):
            raise ValueError('Original legacy receipt lacks eligible acceptance')
    return path


def verify_state_commitments(state):
    modern = 'commit_format_version' in state
    if not modern:
        if any(key in state for key in ('terminal_commit', 'baseline_commit', 'coverage_commit', 'baseline_legacy')):
            raise ValueError('Modern proof lacks state format; no legacy fallback')
        pending = require(state['pending_baseline_initialization'], dict, 'Legacy coverage initialization') if 'pending_baseline_initialization' in state else {}
        cycle = state.get('last_cycle') or pending.get('cycle')
        if cycle:
            for filename in ('receipt-precommit.json', 'receipt.json'):
                path = evidence_path(ROOT / 'cycles' / require(cycle, str, 'Legacy cycle') / filename)
                if path.exists() and 'format_version' in require(read(path), dict, 'Historical receipt'):
                    raise ValueError('Modern receipt cannot fall back to legacy state')
        return False
    if require(state['commit_format_version'], int, 'State commitment version') != 1:
        raise ValueError('Unsupported state commitment version')
    intent = verify_commit(state.get('terminal_commit'))
    if intent.get('state_projection_sha256') != projection_digest(state):
        raise ValueError('Committed state projection mismatch')
    if 'baseline_legacy' in state:
        if state['baseline_legacy'] is not True or 'baseline_commit' in state or not state.get('last_run_id'):
            raise ValueError('Invalid explicit legacy baseline coexistence')
        original_legacy_receipt(state)
    elif state.get('last_run_id') or 'accepted_baseline' in state:
        baseline = verify_commit(state.get('baseline_commit'), baseline=True)
        bound = require(state.get('accepted_baseline'), dict, 'Committed baseline')
        if (baseline.get('baseline_projection_sha256') != projection_digest(state, baseline=True)
                or state['baseline_commit']['projection_sha256'] != baseline['baseline_projection_sha256']
                or baseline.get('cycle') != state.get('last_cycle') or baseline.get('run_id') != state.get('last_run_id')
                or bound.get('run_id') != state.get('last_run_id')
                or any(bound.get(key) != baseline.get(key) for key in ('manifest_sha256', 'artifact_sha256'))
                or bound.get('catalog_sha256') != require(baseline.get('catalog_binding'), dict, 'Committed catalog binding').get('catalog_sha256')):
            raise ValueError('Committed baseline correspondence mismatch')
    elif 'baseline_commit' in state:
        raise ValueError('Baseline proof has no accepted baseline')
    if 'coverage_commit' in state:
        coverage = verify_commit(state['coverage_commit'])
        if (coverage['attempt_status'] not in ('accepted', 'accepted_with_coverage_warning')
                or coverage.get('coverage_projection_sha256') != hashlib.sha256(canonical_bytes(state.get('queries', {}))).hexdigest()):
            raise ValueError('Committed coverage projection mismatch')
    elif state.get('queries'):
        if (state.get('baseline_legacy') is not True or intent.get('coverage_provenance') != 'legacy'
                or intent.get('predecessor_coverage_commit') is not None):
            raise ValueError('Missing retained coverage commitment')
        original_legacy_receipt(state)
    if 'pending_baseline_initialization' in state:
        pending = require(state['pending_baseline_initialization'], dict, 'Coverage initialization')
        coverage = verify_commit(state.get('coverage_commit'))
        if (coverage['attempt_status'] != 'accepted_with_coverage_warning' or pending.get('cycle') != coverage['cycle']
                or pending.get('run_id') != coverage.get('run_id') or state.get('last_run_id') or 'accepted_baseline' in state
                or coverage.get('state_projection_sha256') != projection_digest(state)):
            raise ValueError('Coverage initialization lacks committed warning chain')
    return True


def terminal(cycle, state_path, state, receipt):
    stage = 'receipt_precommit'
    try:
        bind_outputs(cycle, receipt)
        committed = dict(state)
        if 'commit_format_version' not in state and state.get('last_run_id'):
            committed['baseline_legacy'] = True
        if receipt.get('fresh_snapshot_accepted'):
            committed.pop('baseline_legacy', None)
        receipt.update({'format_version': 1, 'coverage_projection_sha256': hashlib.sha256(canonical_bytes(committed.get('queries', {}))).hexdigest(),
                        'coverage_provenance': 'legacy' if committed.get('baseline_legacy') and 'coverage_commit' not in state else 'modern',
                        'state_projection_sha256': projection_digest(committed),
                        'baseline_projection_sha256': projection_digest(committed, baseline=True)})
        intent = cycle / 'receipt-precommit.json'
        payload = (json.dumps(receipt, indent=2) + '\n').encode()
        if intent.exists():
            if evidence_path(intent).read_bytes() != payload:
                raise ValueError('Conflicting immutable terminal intent')
        else:
            write_bytes(intent, payload)
        intent_sha = hashlib.sha256(payload).hexdigest()
        stage = 'receipt'
        write(cycle / 'receipt.json', receipt)
        stage = 'event'
        events = ROOT / 'learning-events.jsonl'
        event = {'format_version': 1, 'cycle': cycle.name, 'outcome': receipt['attempt_status'],
                 'receipt': str(intent.relative_to(ROOT)), 'receipt_sha256': intent_sha}
        event_bytes = canonical_bytes(event)
        records = event_records(events)
        if cycle.name in records:
            if records[cycle.name] != event_bytes:
                raise ValueError('Conflicting terminal event')
        else:
            with evidence_path(events).open('a') as log:
                log.write(event_bytes.decode())
        if digest(evidence_path(intent)) != intent_sha or event_records(events).get(cycle.name) != event_bytes:
            raise ValueError('Terminal evidence changed before commitment')
        marker = {**event, 'event_sha256': hashlib.sha256(event_bytes).hexdigest()}
        committed.update({'commit_format_version': 1, 'terminal_commit': marker})
        if receipt.get('fresh_snapshot_accepted'):
            committed['baseline_commit'] = {**marker, 'projection_sha256': receipt['baseline_projection_sha256']}
        if receipt['attempt_status'] in ('accepted', 'accepted_with_coverage_warning'):
            committed['coverage_commit'] = marker
        stage = 'state'
        write(state_path, committed if receipt.get('prior_commitments_validated') and not receipt.get('prior_commitment_invalid') else state)
    except (OSError, ValueError, KeyError) as error:
        rollback(cycle, receipt)
        receipt.update({'attempt_status': 'incomplete', 'runner_exit_code': 2,
                        'fresh_snapshot_accepted': False, 'storage_error': str(error), 'failed_stage': stage})
        try:
            write(cycle / 'receipt.json', receipt)
        except OSError:
            pass
    try:
        print(json.dumps(receipt, indent=2))
    except OSError:
        pass  # Diagnostic output cannot undo a completed state replacement.
    return receipt['runner_exit_code']


def failed_attempt(cycle, state_path, state, receipt, reason):
    code = receipt['native_exit_code'] or 2
    receipt.update({'status': 'FAILED', 'failure_reason': reason,
                    'runner_exit_code': code, 'fresh_snapshot_accepted': False,
                    'attempt_status': 'incomplete' if receipt.get('storage_error') else 'failed', 'comparison_state': 'unresolved',
                    'previous_run_id': state.get('last_run_id'),
                    'stdout': str((cycle / 'response.json').relative_to(ROOT)),
                    'stderr': str((cycle / 'response.stderr').relative_to(ROOT))})
    rollback(cycle, receipt)
    state.update({'last_attempt_cycle': cycle.name, 'last_failed_cycle': cycle.name})
    return terminal(cycle, state_path, state, receipt)


def launch_binding(policy):
    sdk = require(policy['runtime_expected_sdk_version'], str, 'Expected SDK')
    timeout = require(policy['runtime_preflight_timeout_seconds'], int, 'Preflight timeout')
    if sdk != '0.16.1' or timeout != 10:
        raise ValueError('Runtime policy differs from approved defaults')
    admission = json.loads(RUNTIME_ADMISSION.read_text(), object_pairs_hook=runtime_preflight.unique_object)
    require(admission, dict, 'Runtime admission')
    runtime_preflight.native_environment(BORROWED, PINNED_UV, os.environ)
    bound = runtime_preflight.native_binding(BORROWED, sdk, PINNED_UV, admission)
    return bound


def runner_preflight(policy, cycle):
    """One credential-free preflight; admission exceptions have no process exit."""
    result = {'stage': 'runtime_preflight', 'outcome': 'runtime_unavailable',
              'exit_code': None, 'launched': False, 'timed_out': False}
    try:
        bound = launch_binding(policy)
        sdk, timeout = policy['runtime_expected_sdk_version'], policy['runtime_preflight_timeout_seconds']
        result = runtime_preflight.check(BORROWED, sdk, cycle, timeout=timeout)
        result['native_binding_before'] = bound
        after = launch_binding(policy)
        result['native_binding_after'] = after
        if bound != after:
            result.update(outcome='runtime_unavailable', error='Runtime launch binding changed during preflight')
    except (OSError, ValueError, KeyError, TypeError) as error:
        result.update(outcome='runtime_unavailable', error=str(error))
    return result


def binding_guard(policy, cycle, receipt, preflight, stage, phase):
    """Read/record metadata only; keep existing native transport and real exits."""
    expected = require(preflight['native_binding_after'], dict, 'Admitted runtime binding')
    record = {'cycle': cycle.name, 'stage': stage, 'phase': phase, 'outcome': 'runtime_unavailable',
              'runtime_preflight': {key: receipt['runtime_preflight'][key] for key in ('receipt', 'receipt_sha256')},
              'provider_invoked': receipt['provider_invoked'],
              'native_exit_code': receipt.get('native_exit_code' if stage == 'search' else 'diff_exit_code'),
              'expected_sha256': hashlib.sha256(canonical_bytes(expected)).hexdigest(),
              'snapshot_sha256': None,
              'command_completed': phase == 'after' and type(receipt.get('native_exit_code' if stage == 'search' else 'diff_exit_code')) is int}
    try:
        observed = launch_binding(policy)
        record.update(snapshot=observed, snapshot_sha256=hashlib.sha256(canonical_bytes(observed)).hexdigest())
        if observed != expected:
            raise ValueError('Borrowed runtime launch metadata changed')
        record['outcome'] = 'runtime_ready'
    except (OSError, ValueError, KeyError, TypeError) as error:
        record['error'] = str(error)
    # A failure to retain guard evidence is preparation failure, not drift proof.
    receipt['failed_stage'] = 'cycle_preparation'
    path = cycle / ('runtime-binding-' + stage + '-' + phase + '.json')
    write(path, record)
    receipt.setdefault('runtime_bindings', {})[stage + '_' + phase] = {
        'receipt': str(path.relative_to(ROOT)), 'receipt_sha256': digest(path)}
    if record['outcome'] != 'runtime_ready':
        receipt['failed_stage'] = 'runtime_binding'
        raise ValueError('Runtime binding unavailable at ' + stage + '_' + phase)
    receipt['failed_stage'] = 'search' if stage == 'search' else 'comparison'


def verify_pre_native_binding(intent):
    markers = require(intent.get('runtime_bindings'), dict, 'Runtime binding markers')
    marker = require(markers.get('search_before'), dict, 'Pre-native binding marker')
    cycle = require(intent.get('cycle'), str, 'Pre-native binding cycle')
    if marker.get('receipt') != 'cycles/' + cycle + '/runtime-binding-search-before.json':
        raise ValueError('Pre-native binding receipt cycle mismatch')
    path = evidence_path(ROOT / marker['receipt'])
    if digest(path) != marker.get('receipt_sha256'):
        raise ValueError('Pre-native binding receipt digest mismatch')
    record = require(read(path), dict, 'Pre-native binding receipt')
    preflight = require(intent.get('runtime_preflight'), dict, 'Admitted preflight marker')
    reference = {key: preflight.get(key) for key in ('receipt', 'receipt_sha256')}
    if (record.get('cycle') != cycle or record.get('runtime_preflight') != reference
            or reference['receipt'] != 'cycles/' + cycle + '/runtime-preflight.json'):
        raise ValueError('Pre-native binding/preflight cycle correspondence mismatch')
    preflight_path = evidence_path(ROOT / reference['receipt'])
    if digest(preflight_path) != reference['receipt_sha256']:
        raise ValueError('Admitted preflight receipt digest mismatch')
    admitted = require(read(preflight_path), dict, 'Admitted preflight receipt')
    expected = require(admitted.get('native_binding_after'), dict, 'Admitted preflight binding')
    if (admitted.get('outcome') != 'runtime_ready' or type(admitted.get('exit_code')) is not int
            or admitted['exit_code'] != 0 or preflight.get('outcome') != 'runtime_ready'
            or type(preflight.get('exit_code')) is not int or preflight['exit_code'] != 0
            or admitted.get('native_binding_before') != expected
            or record.get('expected_sha256') != hashlib.sha256(canonical_bytes(expected)).hexdigest()):
        raise ValueError('Pre-native binding/admitted preflight mismatch')
    if (record.get('stage') != 'search' or record.get('phase') != 'before'
            or record.get('outcome') != 'runtime_unavailable'
            or record.get('provider_invoked') is not False or record.get('native_exit_code') is not None
            or record.get('command_completed') is not False):
        raise ValueError('Null native exit lacks unavailable pre-native binding evidence')


def run(args):
    policy, canonical = read(ROOT / 'policy.json'), ROOT / 'searches.json'
    state_path = ROOT / 'learning-state.json'
    state = read(state_path) if state_path.exists() else {'queries': {}}
    if time.time() < state.get('next_allowed_at', 0):
        raise ValueError('Cooldown active; defer to next scheduled or manual run')
    try:
        verified = verify_state_commitments(state)
    except (OSError, ValueError, KeyError, TypeError):
        verified = None  # Existing baseline-resolution failure retains its diagnostic.
    if verified is not None:
        try:
            history = startup_history(state)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps({'attempt_status': 'incomplete', 'runner_exit_code': 2, 'failed_stage': 'startup_admission', 'error': str(error)}))
            return 2
        if history['blocked']:
            return recover_interrupted(state, state_path, history)
    before_hash = digest(canonical)
    old = check_catalog(read(canonical), policy)
    proposal = read(confined(args.proposal)) if args.proposal else None
    candidate = confined(proposal['catalog']) if proposal else canonical
    new = check_catalog(read(candidate), policy)
    if proposal:
        if proposal['base_catalog_sha256'] != before_hash:
            raise ValueError('Stale proposal; active catalog changed')
        check_proposal(proposal, old, new, policy)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    cycle = ROOT / 'cycles' / stamp
    prior_manifest = ROOT / 'results' / 'manifest.json'
    baseline = state.get('accepted_baseline')
    receipt = {'cycle': cycle.name, 'native_exit_code': None, 'provider_invoked': False, 'prior_commitments_validated': False, 'catalog_sha256_before': before_hash, 'promoted': False, 'failed_stage': 'cycle_preparation'}
    try:
        receipt['failed_stage'] = 'baseline_resolution'
        try:
            modern = verify_state_commitments(state)
        except (OSError, ValueError, KeyError, TypeError) as error:
            receipt['prior_commitment_invalid'] = True
            return failed_attempt(cycle, state_path, state, receipt, str(error))
        if modern:
            receipt['predecessor_terminal_commit'] = state['terminal_commit']
            receipt['predecessor_baseline_commit'] = state.get('baseline_commit')
            receipt['predecessor_coverage_commit'] = state.get('coverage_commit')
        receipt['predecessor_recovery_commit'] = state.get('recovery_commit')
        receipt['prior_state_format'] = 'modern' if modern else 'legacy'
        receipt['prior_commitments_validated'] = True
        receipt['startup_history'] = history
        receipt['failed_stage'] = 'cycle_preparation'
        evidence_path(cycle)
        cycle.mkdir(parents=True)
        write(cycle / 'preparation-intent.json', {'format_version': 1, 'cycle': cycle.name, 'catalog_before_sha256': before_hash})
        receipt['preparation_intent_sha256'] = digest(cycle / 'preparation-intent.json')
        write_bytes(cycle / 'catalog-before.json', canonical.read_bytes())
        write_bytes(cycle / 'catalog-used.json', candidate.read_bytes())
        if proposal:
            write(cycle / 'proposal.json', proposal)
        receipt['failed_stage'] = 'output_admission'
        evidence_path(ROOT / 'results/runs')
        evidence_path(prior_manifest)
        latest = read(prior_manifest)['run_id'] if prior_manifest.exists() else None
        write(cycle / 'baseline.json', baseline)
        receipt['failed_stage'] = 'runtime_preflight'
        preflight = runner_preflight(policy, cycle)
        references = {key: cycle / ('runtime-preflight.' + suffix)
                      for key, suffix in (('receipt', 'json'), ('stdout', 'stdout'), ('stderr', 'stderr'))}
        write(references['receipt'], preflight)
        for key in ('stdout', 'stderr'):
            write_bytes(references[key], preflight.get(key, '').encode())
        receipt['runtime_preflight'] = {'outcome': preflight['outcome'], 'exit_code': preflight['exit_code'],
            **{key: str(path.relative_to(ROOT)) for key, path in references.items()},
            **{key + '_sha256': digest(path) for key, path in references.items()}}
        if preflight['outcome'] != 'runtime_ready':
            return failed_attempt(cycle, state_path, state, receipt, 'Borrowed runtime unavailable; inspect retained preflight diagnostics')
        receipt.update({'attempt_status': 'incomplete', 'comparison_state': 'unresolved', 'failed_stage': 'search'})
        write(cycle / 'receipt.json', receipt)
        binding_guard(policy, cycle, receipt, preflight, 'search', 'before')
        state.update({'next_allowed_at': time.time() + policy['minimum_seconds_between_runs'], 'last_attempt_cycle': cycle.name})
        write(cycle / 'start-intent.json', {'format_version': 1, 'cycle': cycle.name,
              'accepted_projection_sha256': projection_digest(state), 'catalog_before_sha256': digest(cycle / 'catalog-before.json'),
              'catalog_used_sha256': digest(cycle / 'catalog-used.json'),
              'predecessors': {key: state.get(key + '_commit') for key in ('terminal', 'baseline', 'coverage')}})
        receipt['start_intent_sha256'] = digest(cycle / 'start-intent.json')
        state['attempt_start_commit'] = {'cycle': cycle.name, 'start_intent_sha256': receipt['start_intent_sha256']}
        write(state_path, state)
        receipt['provider_invoked'] = True
        try:
            rc = command(['github-search', '--', '--catalog', str(cycle / 'catalog-used.json'), '--output-dir', str(ROOT / 'results'), '--report-path', str(cycle / 'native-report.md'), '--json'], cycle / 'response', policy['command_timeout_seconds'])
        except NativeLaunchFailure as error:
            receipt.update({'provider_invoked': False, 'launch_status': 'failed_before_start', 'launch_error': str(error)})
            if isinstance(error, NativeOutputFailure):
                receipt['storage_error'] = str(error)
            return failed_attempt(cycle, state_path, state, receipt, str(error))
        receipt['native_exit_code'] = rc
        binding_guard(policy, cycle, receipt, preflight, 'search', 'after')
        require(rc, int, 'Native search exit')
        if rc:
            return failed_attempt(cycle, state_path, state, receipt, 'Native command failed; inspect retained stderr')
        try:
            response = read(cycle / 'response.json')
        except (OSError, ValueError):
            return failed_attempt(cycle, state_path, state, receipt, 'Native stdout is missing or invalid JSON')
        receipt['failed_stage'] = 'result_validation'
        rows = rows_by_id(require(response, dict, 'Search stdout')['results'])
        data = require(read(prior_manifest), dict, 'Latest manifest')
        state['latest_observation_run_id'] = data['run_id']
        if data['run_id'] == latest or set(rows) != set(new):
            raise ValueError('No fresh complete result set; preserved failure evidence')
        manifest, stored = immutable(data['run_id'])
        if prior_manifest.read_bytes() != manifest.read_bytes() or rows != stored:
            raise ValueError('Search stdout/latest manifest is not bound to immutable artifacts')
        validate_search_envelope(response, rows, data, rc)
        bind_catalog(rows, new)
        receipt['catalog_binding'] = {'catalog_sha256': digest(cycle / 'catalog-used.json'), 'search_ids': sorted(rows),
                                      'transport_ignored_fields': {sid: ['sort', 'order'] for sid in new if new[sid]['search_type'] == 'DISCUSSION'}}
        receipt['artifact_sha256'] = artifact_hashes(manifest, stored)
        receipt['manifest_sha256'] = digest(manifest)
        receipt.update({'run_id': data['run_id'], 'manifest': str(manifest.relative_to(ROOT)), 'searches': len(rows), 'entries': sum(r.get('item_count', 0) for r in rows.values()), 'failed': [sid for sid, r in rows.items() if r.get('error_code') != 'NONE']})
        feedback = metrics(rows, state.get('queries', {}))
        write(cycle / 'metrics.json', feedback)
        receipt['unverified_empty_queries'] = [sid for sid, row in feedback.items() if row['unverified_empty']]
        receipt['coverage_warning_queries'] = {sid: coverage_reasons(rows[sid], metric) for sid, metric in feedback.items() if coverage_reasons(rows[sid], metric)}
        receipt['recovered_empty_queries'] = [sid for sid, row in feedback.items() if row['recovered_from_empty']]
        receipt['failed_stage'] = 'baseline_resolution'
        prior = accepted_baseline(state, receipt, policy)
        receipt['comparison_state'] = 'baseline_established'
        if prior:
            receipt['failed_stage'] = 'comparison'
            binding_guard(policy, cycle, receipt, preflight, 'diff', 'before')
            receipt['diff_exit_code'] = command(['github:diff', '--', str(prior.parent), str(manifest.parent), '--results-dir', str(ROOT / 'results'), '--json'], cycle / 'diff', policy['command_timeout_seconds'])
            binding_guard(policy, cycle, receipt, preflight, 'diff', 'after')
            require(receipt['diff_exit_code'], int, 'Native comparison exit')
            for label, path in [('diff_stdout', cycle / 'diff.json'), ('diff_stderr', cycle / 'diff.stderr')]:
                receipt[label] = str(path.relative_to(ROOT))
                receipt[label + '_sha256'] = digest(path) if path.exists() else None
            receipt['comparison_state'] = 'compared'
        if receipt.get('diff_exit_code', 0):
            return failed_attempt(cycle, state_path, state, receipt, 'Snapshot comparison failed')
        if prior:
            _, baseline_rows = snapshot(prior)
            receipt['promoted_query_drift'] = sorted(promoted_drift(state, policy, old, before_hash))
            approved = set((proposal or {}).get('changes', {})) | set(receipt['promoted_query_drift'])
            outcome = comparison(read(cycle / 'diff.json'), baseline_rows, rows, read(prior)['run_id'], data['run_id'], approved, feedback)
            receipt['suppressed_queries'] = outcome['suppressed_queries']
            if receipt['suppressed_queries']:
                receipt['comparison_state'] = 'suppressed'
            write(cycle / 'comparison.json', outcome)
            receipt['comparison_evidence'] = str((cycle / 'comparison.json').relative_to(ROOT))
            receipt['comparison_evidence_sha256'] = digest(cycle / 'comparison.json')
        failures = evaluate(proposal, rows) if proposal else []
        if proposal and (rc or receipt['failed']):
            failures.append('Batch failure prevents promotion')
        # Affected queries must be complete and nonempty; unrelated warnings permit catalog-only promotion.
        affected = sorted(set((proposal or {}).get('changes', {})) & receipt['coverage_warning_queries'].keys())
        if affected:
            failures.append('Affected query coverage warning prevents promotion: ' + ', '.join(affected))
        if proposal and any(metric['empty_regression'] for metric in feedback.values()):
            failures.append('Unexpected empty regression prevents promotion; coverage unverified')
        if proposal and digest(canonical) != before_hash:
            failures.append('Concurrent active catalog change prevents promotion')
        if proposal and not failures:
            promote(cycle, canonical, receipt, old, new, proposal, state, state_path)
        receipt['experiment_failures'] = failures
        receipt['catalog_sha256_after'] = digest(canonical)
        receipt['partial_queries'] = [sid for sid, r in feedback.items() if not r['complete']]
        proposed = dict(state)
        warning = bool(receipt['coverage_warning_queries'])
        if warning:
            receipt['comparison_state'] = 'suppressed'
        receipt['catalog_only_promotion'] = receipt['promoted'] and warning  # Baseline stays fixed.
        if not proposal or receipt['promoted']:
            proposed['queries'] = feedback
            if warning and prior is None:
                proposed['pending_baseline_initialization'] = {'cycle': cycle.name, 'run_id': data['run_id'], 'manifest_sha256': digest(manifest), 'artifact_sha256': receipt['artifact_sha256'], 'catalog_sha256': receipt['catalog_binding']['catalog_sha256']}
            if not warning:
                proposed.pop('pending_baseline_initialization', None)
                proposed.update({'last_run_id': data['run_id'], 'last_cycle': cycle.name,
                                 'accepted_baseline': {'run_id': data['run_id'], 'manifest_sha256': digest(manifest), 'artifact_sha256': receipt['artifact_sha256'], 'catalog_sha256': receipt['catalog_binding']['catalog_sha256']}})
        receipt.update({'attempt_status': 'failed' if failures else ('accepted_with_coverage_warning' if warning else 'accepted'),
                        'runner_exit_code': 2 if failures or warning else 0,
                        'fresh_snapshot_accepted': not failures and not warning,
                        'failed_stage': 'proposal' if failures else None})
        return terminal(cycle, state_path, proposed, receipt)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
        if isinstance(error, StorageFailure) or (isinstance(error, OSError) and receipt['failed_stage'] == 'cycle_preparation'):
            receipt['storage_error'] = str(error)
        return failed_attempt(cycle, state_path, state, receipt, str(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', required=True, help='Existing private state directory outside Git checkouts')
    parser.add_argument('--runtime-config', required=True, help='Existing local JSON selecting the admitted runtime and tools')
    parser.add_argument('--proposal', help='Confined proposal JSON; otherwise refresh current catalog')
    args = parser.parse_args()
    try:
        configure(args.state_dir, args.runtime_config)
        with evidence_path(ROOT / '.refresh.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return run(args)
    except (BlockingIOError, OSError, ValueError, KeyError, IndexError) as error:
        print(json.dumps({'status': 'BLOCKED', 'error': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
