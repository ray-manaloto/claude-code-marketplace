"""Offline checks for data integrity and failed experiment isolation."""
import argparse
import contextlib
import copy
import fcntl
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import refresh


class FeedbackChecks(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        fixture_root = Path(temporary.name).resolve()
        selection = patch.multiple(refresh, ROOT=fixture_root,
                                   BORROWED=fixture_root / 'borrowed', PINNED_UV=fixture_root / 'uv')
        selection.start()
        self.addCleanup(selection.stop)
        preflight = patch.object(refresh, "runner_preflight", return_value={"outcome": "runtime_ready", "exit_code": 0})
        preflight.start()  # RF1 regressions stub RF2; real synthetic integration is separate.
        self.addCleanup(preflight.stop)
        binding = patch.object(refresh, "binding_guard", return_value=None)
        binding.start()  # RF1 fixtures also stub RF2 stage metadata; dedicated tests keep it real.
        self.addCleanup(binding.stop)
        examples = Path(__file__).with_name('examples')
        self.policy = refresh.read(examples / 'policy.json')
        self.catalog = refresh.read(examples / 'searches.json')
        self.row = {'search_id': 'test', 'search_type': 'ISSUE', 'query_fingerprint': 'a' * 64, 'query_executed': 'test', 'timing': {}, 'error_code': 'NONE', 'is_complete': True, 'item_count': 1, 'total_count': 1, 'items': [], 'issues': [{'repo_name': 'o/r', 'number': 1, 'title': 'Issue', 'state': 'open', 'html_url': 'https://github.com/o/r/issues/1', 'user': 'o', 'is_pr': False}], 'discussions': []}
        self.proposal = {'changes': {'test': {'reason': 'A verified source narrows noise', 'source_urls': ['https://docs.github.com/en/rest/search/search'], 'expect': {'min_items': 1, 'max_total': 2, 'complete': True, 'required_urls': ['https://github.com/o/r/issues/1']}}}}

    def test_code_identity_ignores_commit_churn(self):
        first = {'repo_name': 'o/r', 'path': 'file.cpp', 'html_url': 'https://github.com/o/r/blob/aaaa/file.cpp'}
        self.assertEqual(refresh.identity(first), refresh.identity({**first, 'html_url': 'https://github.com/o/r/blob/bbbb/file.cpp'}))

    def test_changed_fingerprint_resets_history(self):
        previous = {'test': {'fingerprint': 'b', 'capped_streak': 5}}
        rows = {'test': {**self.row, 'is_complete': False}}
        self.assertEqual(refresh.metrics(rows, previous)['test']['capped_streak'], 1)

    def test_failed_query_is_not_empty_success(self):
        row = {**self.row, 'error_code': 'API_ERROR', 'issues': [], 'item_count': 0}
        metric = refresh.metrics({'test': row}, {})['test']
        self.assertEqual(metric['error_streak'], 1)
        self.assertEqual(metric['empty_streak'], 0)
        self.assertFalse(metric['complete'])

    def test_unexpected_empty_persists_until_results_recover(self):
        prior = refresh.metrics({'test': self.row}, {})
        empty = {**self.row, 'issues': [], 'item_count': 0, 'total_count': 0}
        for _ in range(2):
            prior = refresh.metrics({'test': empty}, prior)
            self.assertTrue(prior['test']['empty_regression'])
            self.assertTrue(prior['test']['native_complete'])
            self.assertFalse(prior['test']['complete'])
            self.assertEqual(prior['test']['last_nonempty_items'], 1)
            self.assertEqual(prior['test']['capped_streak'], 0)
            self.assertEqual(prior['test']['unchanged_streak'], 0)
        recovered = refresh.metrics({'test': self.row}, prior)['test']
        self.assertTrue(recovered['complete'])
        self.assertFalse(recovered['empty_regression'])
        self.assertTrue(recovered['recovered_from_empty'])
        self.assertFalse(refresh.metrics({'test': self.row}, {'test': recovered})['test']['recovered_from_empty'])

    def test_new_query_empty_is_separate_from_a_regression(self):
        empty = {**self.row, 'issues': [], 'item_count': 0, 'total_count': 0}
        for previous in ({}, {'test': {'fingerprint': 'different', 'items': 5}}):
            row = refresh.metrics({'test': empty}, previous)['test']
            self.assertFalse(row['empty_regression'])
            self.assertFalse(row['complete'])
            self.assertTrue(row['unverified_empty'])

    def test_api_error_does_not_erase_nonempty_history(self):
        prior = refresh.metrics({'test': self.row}, {})
        empty = {**self.row, 'issues': [], 'item_count': 0, 'total_count': 0}
        failed = refresh.metrics({'test': {**empty, 'error_code': 'API_ERROR'}}, prior)
        self.assertEqual(failed['test']['last_nonempty_items'], 1)
        self.assertTrue(refresh.metrics({'test': empty}, failed)['test']['empty_regression'])

    def test_empty_coverage_blocks_an_unrelated_valid_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            catalog = {'searches': self.catalog['searches'][:2]}
            refresh.write(root / 'policy.json', self.policy)
            refresh.write(root / 'searches.json', catalog)
            before = (root / 'searches.json').read_bytes()
            candidate = copy.deepcopy(catalog)
            candidate['searches'][0]['query'] += ' in:title'
            changed_id, empty_id = [s['id'] for s in candidate['searches']]
            prior_row = self.fixture_row(catalog['searches'][1])
            refresh.write(root / 'learning-state.json', {'queries': refresh.metrics({empty_id: prior_row}, {})})
            refresh.write(root / 'candidate.json', candidate)
            refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {changed_id: self.proposal['changes']['test']}})

            def fake_command(arguments, output, timeout):
                run_dir = root / 'results/runs/test_run'
                rows = [self.fixture_row(candidate['searches'][0]), {**prior_row, 'issues': [], 'item_count': 0, 'total_count': 0}]
                artifacts = []
                for row in rows:
                    file = run_dir / (row['search_id'] + '.json')
                    refresh.write(file, row)
                    artifacts.append(str(file.relative_to(root / 'results')))
                manifest = self.manifest('run', rows, artifacts)
                refresh.write(root / 'results/manifest.json', manifest)
                refresh.write(run_dir / 'manifest.json', manifest)
                refresh.write(output.with_suffix('.json'), self.envelope(rows))
                return 0

            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', fake_command), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json')), 2)
            event = self.event_receipt(root)
            self.assertEqual(event['unverified_empty_queries'], [empty_id])
            self.assertFalse(event['promoted'])
            self.assertEqual((root / 'searches.json').read_bytes(), before)

    def fixture_row(self, search):
        normalized = {key: sorted(search.get(key) or []) for key in ('filenames', 'languages', 'topics')}
        normalized.update({'min_stars': search.get('min_stars'), 'order': (search.get('order') or 'desc').lower(), 'query': search['query'].strip(), 'search_type': search['search_type'], 'sort': (search.get('sort') or '').lower(), 'target_repo': (search.get('target_repo') or '').strip().lower()})
        parts = [search['query'].strip()]
        if search.get('target_repo'):
            parts.append('repo:' + search['target_repo'])
        for key, qualifier in [('languages', 'language'), ('filenames', 'filename'), ('topics', 'topic')]:
            parts.extend(qualifier + ':' + value for value in search.get(key) or [])
        if search.get('min_stars') is not None:
            parts.append('stars:>=' + str(search['min_stars']))
        if search['search_type'] in ('ISSUE', 'PULL_REQUEST'):
            parts.append('is:issue' if search['search_type'] == 'ISSUE' else 'is:pr')
        arrays = {'items': [], 'issues': [], 'discussions': []}
        if search['search_type'] in ('ISSUE', 'PULL_REQUEST'):
            arrays['issues'] = [{**self.row['issues'][0], 'is_pr': search['search_type'] == 'PULL_REQUEST'}]
        elif search['search_type'] == 'DISCUSSION':
            arrays['discussions'] = [{'repo_name': 'o/r', 'number': 1, 'title': 'Discussion', 'html_url': 'https://github.com/o/r/issues/1', 'author': 'o'}]
        else:
            arrays['items'] = [{'repo_name': 'o/r', 'html_url': 'https://github.com/o/r/issues/1'}]
        return {**self.row, **arrays, 'search_id': search['id'], 'search_type': search['search_type'], 'query_executed': ' '.join(parts), 'query_fingerprint': hashlib.sha256(json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}

    def manifest(self, run_id, rows, artifacts):
        successful = [r for r in rows if r['error_code'] == 'NONE']
        return {'run_id': run_id, 'timestamp': '2026-10-12T00:00:00Z', 'total_searches': len(rows), 'successful_searches': len(successful), 'failed_searches': len(rows) - len(successful), 'total_items': sum(r['item_count'] for r in successful), 'artifacts': artifacts, 'errors': []}


    def envelope(self, rows):
        successful = [r for r in rows if r['error_code'] == 'NONE']
        failed = len(rows) - len(successful)
        return {'exit_code': 8 if failed else 0, 'status': ('ERROR' if successful else 'FAILURE') if failed else 'SUCCESS',
                'summary': {'total_searches': len(rows), 'successful_searches': len(successful), 'failed_searches': failed, 'total_items_found': sum(r['item_count'] for r in successful)},
                'results': rows, 'error': None, 'errors': [],
                'timing': {'start_time': '2026-10-12T00:00:00.000000000Z', 'end_time': '2026-10-12T00:00:00.001000000Z', 'duration_ms': 1.0, 'duration_ns': 1000000},
                'system_info': {'platform': 'offline', 'python_version': '3.12', 'cli_version': '0.1.0', 'pydantic_version': '2'}}

    def comparison(self, root, baseline, candidate, sid):
        row = refresh.read(root / 'results/runs' / ('test_' + candidate) / (sid + '.json'))
        base = refresh.read(root / 'results/runs' / ('test_' + baseline) / (sid + '.json'))
        def indexed(result):
            values = result.get('items', []) + result.get('issues', []) + result.get('discussions', [])
            mapping = {}
            for rank, value in enumerate(values, 1):
                key = value['repo_name'] + (':' + value['path'] if value.get('path') else ('#' + str(value['number']) if 'number' in value else ''))
                title = value['path'] if value.get('path') else (value['title'] if 'number' in value else value.get('description'))
                mapping[key] = (rank, title, value['html_url'])
            return mapping
        before, after = indexed(base), indexed(row)
        complete = base['is_complete'] and row['is_complete']
        items = []
        for key in after.keys() | before.keys():
            if key not in after and (base['error_code'] != 'NONE' or row['error_code'] != 'NONE'):
                continue
            current, previous = after.get(key), before.get(key)
            status = 'UNCHANGED' if current and previous else ('NEW' if current else 'GONE')
            if not complete and status != 'UNCHANGED':
                status = 'RANKED_WINDOW_ENTERED' if current else 'RANKED_WINDOW_EXITED'
            value = current or previous
            caveat = {'RANKED_WINDOW_ENTERED': 'Item entered top ranked window; may have existed previously beyond collection ceiling', 'RANKED_WINDOW_EXITED': 'Item fell out of top ranked window; still present on GitHub beyond collection ceiling'}.get(status)
            items.append({'search_id': sid, 'status': status, 'item_id': key, 'url': value[2], 'title_or_path': value[1], 'previous_rank': previous[0] if previous else None, 'current_rank': current[0] if current else None, 'caveat': caveat})
        query = {'search_id': sid, 'search_type': row['search_type'], 'query_fingerprint': row['query_fingerprint'], 'baseline_run_id': baseline, 'candidate_run_id': candidate, 'baseline_count': base['item_count'], 'candidate_count': row['item_count'], 'is_baseline_complete': base['is_complete'], 'is_candidate_complete': row['is_complete'], 'items': items}
        for status, field in [('NEW', 'new_count'), ('GONE', 'gone_count'), ('UNCHANGED', 'unchanged_count'), ('RANKED_WINDOW_ENTERED', 'entered_window_count'), ('RANKED_WINDOW_EXITED', 'exited_window_count')]:
            query[field] = sum(item['status'] == status for item in items)
        return {'status': 'SUCCESS', 'exit_code': 0, 'error': None, 'baseline_run_id': baseline, 'candidate_run_id': candidate, 'total_queries_compared': 1, 'incompatible_queries': 0, 'queries': [query], 'timing': {}, 'system_info': {}}

    def event_receipt(self, root):
        event = json.loads((root / 'learning-events.jsonl').read_text())
        return refresh.read(root / event['receipt']) if 'format_version' in event else event

    def workflow(self, root):
        refresh.write(root / 'policy.json', {**self.policy, 'minimum_seconds_between_runs': 0})
        refresh.write(root / 'searches.json', {'searches': self.catalog['searches'][:1]})
        return self.catalog['searches'][0]['id']

    def observation(self, root, run_id, sid):
        state = refresh.read(root / 'learning-state.json') if (root / 'learning-state.json').exists() else {}
        used = root / 'cycles' / state.get('last_attempt_cycle', '') / 'catalog-used.json'
        catalog = refresh.read(used if used.exists() else root / 'searches.json')
        row = self.fixture_row(next(s for s in catalog['searches'] if s['id'] == sid))
        if run_id == 'old':
            refresh.write(root / 'cycles/old-cycle/catalog-used.json', catalog)
            refresh.write(root / 'cycles/old-cycle/receipt.json', {'cycle': 'old-cycle', 'run_id': 'old', 'native_exit_code': 0, 'diff_exit_code': 0})
        directory = root / 'results/runs' / ('test_' + run_id)
        refresh.write(directory / (sid + '.json'), row)
        manifest = self.manifest(run_id, [row], ['runs/test_' + run_id + '/' + sid + '.json'])
        refresh.write(directory / 'manifest.json', manifest)
        refresh.write(root / 'results/manifest.json', manifest)
        return directory, row


    def test_native_envelope_refuses_forged_success_and_recovers_old_baseline(self):
        faults = ('exit_bool', 'exit_string', 'exit_mismatch', 'status', 'status_null', 'error', 'errors_null', 'errors_root', 'errors_nonempty',
                  'summary_root', 'summary_missing', 'summary_count', 'summary_bool', 'summary_negative', 'failed_row',
                  'timing_missing', 'timing_root', 'timing_start', 'timing_ns_bool', 'timing_ms_bool', 'timing_ms_huge', 'timing_ms_negative_huge', 'metadata_missing', 'metadata_root',
                  'metadata_field', 'metadata_type', 'native8', 'native1', 'valid', 'error_absent')
        for proposal_mode in (False, True):
            for fault in faults:
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve(); sid = self.workflow(root); stage = ['healthy']; comparisons = []
                    def native(arguments, output, timeout):
                        if arguments[0] != 'github-search':
                            base = Path(arguments[2]).name.removeprefix('test_'); comparisons.append(base)
                            refresh.write(output.with_suffix('.json'), self.comparison(root, base, stage[0], sid))
                            return 0
                        run, row = self.observation(root, stage[0], sid)
                        value = {'exit_code': 0, 'status': 'SUCCESS', 'error': None, 'errors': [], 'results': [row],
                                 'summary': {'total_searches': 1, 'successful_searches': 1, 'failed_searches': 0, 'total_items_found': 1},
                                 'timing': {'start_time': 'start', 'end_time': 'end', 'duration_ms': 1.0, 'duration_ns': 1000000},
                                 'system_info': {'platform': 'offline', 'python_version': '3.12', 'cli_version': '0.1', 'pydantic_version': '2'}}
                        if stage[0] == 'candidate':
                            if fault in ('exit_bool', 'exit_string', 'exit_mismatch'): value['exit_code'] = {'exit_bool': False, 'exit_string': '0', 'exit_mismatch': 8}[fault]
                            elif fault in ('status', 'status_null'): value['status'] = 'ERROR' if fault == 'status' else None
                            elif fault == 'error': value['error'] = {}
                            elif fault.startswith('errors_'): value['errors'] = {'errors_null': None, 'errors_root': {}, 'errors_nonempty': [{}]}[fault]
                            elif fault == 'summary_root': value['summary'] = []
                            elif fault == 'summary_missing': del value['summary']['successful_searches']
                            elif fault in ('summary_count', 'summary_bool', 'summary_negative'): value['summary']['total_items_found'] = {'summary_count': 2, 'summary_bool': True, 'summary_negative': -1}[fault]
                            elif fault == 'failed_row':
                                row['error_code'] = 'API_ERROR'; refresh.write(run / (sid + '.json'), row)
                                manifest = self.manifest('candidate', [row], ['runs/test_candidate/' + sid + '.json'])
                                refresh.write(run / 'manifest.json', manifest); refresh.write(root / 'results/manifest.json', manifest)
                                value['summary'].update(successful_searches=0, failed_searches=1, total_items_found=0)
                            elif fault in ('timing_missing', 'metadata_missing'): del value['timing' if fault == 'timing_missing' else 'system_info']
                            elif fault in ('timing_root', 'metadata_root'): value['timing' if fault == 'timing_root' else 'system_info'] = []
                            elif fault == 'timing_start': value['timing']['start_time'] = None
                            elif fault == 'timing_ns_bool': value['timing']['duration_ns'] = False
                            elif fault == 'timing_ms_bool': value['timing']['duration_ms'] = False
                            elif fault in ('timing_ms_huge', 'timing_ms_negative_huge'): value['timing']['duration_ms'] = 10 ** 400 if fault == 'timing_ms_huge' else -(10 ** 400)
                            elif fault == 'metadata_field': del value['system_info']['pydantic_version']
                            elif fault == 'metadata_type': value['system_info']['cli_version'] = 1
                            elif fault in ('native8', 'native1'): value.update(exit_code=8 if fault == 'native8' else 1, status='FAILURE')
                            elif fault == 'error_absent': del value['error']
                        refresh.write(output.with_suffix('.json'), value)
                        return value['exit_code'] if stage[0] == 'candidate' and fault in ('native8', 'native1') else 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                        prior = refresh.read(root / 'learning-state.json'); before = (root / 'searches.json').read_bytes()
                        if proposal_mode:
                            candidate = refresh.read(root / 'searches.json'); candidate['searches'][0]['max_items'] += 1
                            refresh.write(root / 'candidate.json', candidate)
                            refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                        stage[0] = 'candidate'
                        expected = 0 if fault in ('valid', 'error_absent') else (8 if fault == 'native8' else (1 if fault == 'native1' else 2))
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), expected)
                        state = refresh.read(root / 'learning-state.json'); receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                        if expected:
                            for key in ('accepted_baseline', 'last_run_id', 'last_cycle', 'queries', 'baseline_commit', 'coverage_commit'):
                                self.assertEqual(state.get(key), prior.get(key))
                            self.assertEqual((root / 'searches.json').read_bytes(), before)
                            self.assertEqual(receipt['attempt_status'], 'failed'); self.assertFalse(receipt['promoted'])
                            self.assertEqual(receipt['native_exit_code'], 8 if fault == 'native8' else (1 if fault == 'native1' else 0))
                            self.assertIs(receipt['provider_invoked'], True)
                            self.assertIn('next_allowed_at', state)
                            self.assertEqual(receipt['failed_stage'], 'search' if fault in ('native8', 'native1') else 'result_validation')
                            self.assertNotIn('comparison_evidence', receipt); self.assertEqual(comparisons, [])
                            stage[0] = 'recovered'; self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                            self.assertEqual(comparisons, ['healthy'])

    def test_comparison_failure_preserves_baseline_for_next_success(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sid = self.workflow(root)
            calls, attempt = [], ['first', 0]

            def native(arguments, output, timeout):
                if arguments[0] == 'github-search':
                    _, row = self.observation(root, attempt[0], sid)
                    refresh.write(output.with_suffix('.json'), self.envelope([row]))
                    return 0
                calls.append(arguments[2:4])
                refresh.write(output.with_suffix('.json'), self.comparison(root, 'first', attempt[0], sid))
                output.with_suffix('.stderr').write_text('comparison diagnostics')
                return attempt[1]

            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                accepted = refresh.read(root / 'learning-state.json')
                attempt[:] = ['rejected', 124]
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                state = refresh.read(root / 'learning-state.json')
                for field in ('queries', 'last_run_id', 'last_cycle', 'accepted_baseline'):
                    self.assertEqual(state[field], accepted[field])
                receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                self.assertEqual(receipt['diff_exit_code'], 124)
                self.assertEqual(receipt['attempt_status'], 'failed')
                self.assertTrue((root / receipt['diff_stdout']).exists())
                attempt[:] = ['next', 0]
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
            self.assertEqual([Path(c[0]).name for c in calls], ['test_first', 'test_first'])

    def test_legacy_baseline_requires_success_receipt_and_unique_run(self):
        for condition in ('missing_receipt', 'missing_run', 'ambiguous', 'list_receipt', 'null_receipt', 'catalog_mismatch', 'catalog_unavailable', 'bool_native', 'bool_diff', 'null_runner', 'null_acceptance', 'null_outcome', 'valid'):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                old_dir, row = self.observation(root, 'old', sid)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle'}
                refresh.write(root / 'learning-state.json', prior)
                if condition == 'missing_receipt':
                    (root / 'cycles/old-cycle/receipt.json').unlink()
                else:
                    refresh.write(root / 'cycles/old-cycle/receipt.json', {'cycle': 'old-cycle', 'run_id': 'old', 'native_exit_code': 0, 'diff_exit_code': 0})
                if condition in ('catalog_mismatch', 'valid'):
                    catalog = refresh.read(root / 'searches.json')
                    if condition == 'catalog_mismatch':
                        catalog['searches'][0]['query'] = 'a different catalog'
                    refresh.write(root / 'cycles/old-cycle/catalog-used.json', catalog)
                if condition == 'catalog_unavailable':
                    (root / 'cycles/old-cycle/catalog-used.json').unlink()
                if condition in ('list_receipt', 'null_receipt'):
                    refresh.write(root / 'cycles/old-cycle/receipt.json', [] if condition == 'list_receipt' else None)
                malformed = {'bool_native': ('native_exit_code', False), 'bool_diff': ('diff_exit_code', False), 'null_runner': ('runner_exit_code', None), 'null_acceptance': ('fresh_snapshot_accepted', None), 'null_outcome': ('attempt_status', None)}
                if condition in malformed:
                    path = root / 'cycles/old-cycle/receipt.json'
                    key, value = malformed[condition]
                    refresh.write(path, {**refresh.read(path), key: value})
                if condition == 'missing_run':
                    (old_dir / 'manifest.json').unlink()
                if condition == 'ambiguous':
                    refresh.write(root / 'results/runs/duplicate_old/manifest.json', refresh.read(old_dir / 'manifest.json'))

                def native(arguments, output, timeout):
                    if arguments[0] == 'github-search':
                        _, fresh = self.observation(root, 'new', sid)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                    else:
                        refresh.write(output.with_suffix('.json'), self.comparison(root, 'old', 'new', sid))
                    return 0

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0 if condition == 'valid' else 2)
                state = refresh.read(root / 'learning-state.json')
                receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                if condition == 'valid':
                    self.assertEqual(receipt['baseline_migration']['run_id'], 'old')
                    self.assertEqual(receipt['baseline_catalog_binding']['status'], 'verified')
                    self.assertEqual(state['commit_format_version'], 1)
                    self.assertEqual(state['baseline_commit']['outcome'], 'accepted')
                    self.assertNotIn('baseline_legacy', state)
                else:
                    self.assertEqual(state['queries'], prior['queries'])
                    self.assertEqual(state['last_run_id'], 'old')
                    self.assertEqual(receipt['attempt_status'], 'failed')
                    self.assertEqual(receipt['failed_stage'], 'baseline_resolution')
                    self.assertEqual(receipt['runner_exit_code'], 2)

    def test_acceptance_state_is_last_and_storage_failure_is_incomplete(self):
        for storage_failure in (False, True):
            with self.subTest(storage_failure=storage_failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                replace = Path.replace

                def native(arguments, output, timeout):
                    start = refresh.read(root / 'learning-state.json')
                    self.assertIn('next_allowed_at', start)
                    cycle = root / 'cycles' / start['last_attempt_cycle']
                    self.assertEqual(refresh.read(cycle / 'receipt.json')['attempt_status'], 'incomplete')
                    _, row = self.observation(root, 'first', sid)
                    refresh.write(output.with_suffix('.json'), self.envelope([row]))
                    return 0

                def persist(path, target):
                    if target == root / 'learning-state.json' and refresh.read(path).get('accepted_baseline'):
                        cycle = root / 'cycles' / refresh.read(path)['last_cycle']
                        self.assertEqual(refresh.read(cycle / 'receipt.json')['attempt_status'], 'accepted')
                        self.assertEqual(json.loads((root / 'learning-events.jsonl').read_text())['cycle'], cycle.name)
                        if storage_failure:
                            raise OSError('simulated state commit failure')
                    return replace(path, target)

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(Path, 'replace', persist), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2 if storage_failure else 0)
                state = refresh.read(root / 'learning-state.json')
                if storage_failure:
                    self.assertNotIn('accepted_baseline', state)
                    receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                    self.assertEqual(receipt['attempt_status'], 'incomplete')

    def test_promotion_storage_failure_rolls_back_exact_preimages(self):
        for fault in ('preparation', 'start_receipt', 'start_state', 'intent', 'admission', 'catalog', 'changelog', 'receipt', 'event', 'state', 'rollback', 'concurrent', 'concurrent_both'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                policy = refresh.read(root / 'policy.json')
                policy['minimum_seconds_between_runs'] = 30
                refresh.write(root / 'policy.json', policy)
                old, row = self.observation(root, 'old', sid)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                before = (root / 'searches.json').read_bytes()
                changes_before = b'{"cycle":"previous"}\n'
                (root / 'search-changes.jsonl').write_bytes(changes_before)
                candidate = refresh.read(root / 'searches.json')
                candidate['searches'][0]['max_items'] += 1
                refresh.write(root / 'candidate.json', candidate)
                refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                external = {**candidate, 'external_edit': True}
                external_bytes = json.dumps(external).encode()
                replace, opened = Path.replace, Path.open
                finished, tripped, compared, invoked, external_changes = [False], [False], [], [], []
                def native(arguments, output, timeout):
                    invoked.append(arguments[0])
                    if arguments[0] == 'github-search':
                        _, fresh = self.observation(root, 'new' if not finished[0] else 'recovery', sid)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                    else:
                        compared.append(Path(arguments[2]).name)
                        refresh.write(output.with_suffix('.json'), self.comparison(root, 'old', 'new' if len(compared) == 1 else 'recovery', sid))
                        output.with_suffix('.stderr').write_text('retained diff stderr')
                        finished[0] = True
                    return 0
                def persist(path, target):
                    names = {'preparation': 'catalog-before.json', 'intent': 'promotion-intent.json', 'admission': 'learning-state.json', 'catalog': 'searches.json', 'changelog': 'search-changes.jsonl', 'receipt': 'receipt-precommit.json', 'state': 'learning-state.json', 'concurrent': 'learning-state.json', 'concurrent_both': 'learning-state.json', 'rollback': 'learning-state.json', 'start_receipt': 'receipt.json', 'start_state': 'learning-state.json'}
                    if fault == 'rollback' and tripped[0] and target == root / 'searches.json':
                        raise OSError('actual rollback replace fault')
                    if not tripped[0] and fault in names and target.name == names[fault] and (finished[0] or fault in ('preparation', 'start_receipt', 'start_state')) and (fault not in ('state', 'concurrent', 'concurrent_both', 'rollback') or json.loads(path.read_bytes()).get('last_run_id') == 'new'):
                        tripped[0] = True
                        if fault in ('concurrent', 'concurrent_both'):
                            (root / 'searches.json').write_bytes(external_bytes)
                            if fault == 'concurrent_both':
                                external_changes.append((root / 'search-changes.jsonl').read_bytes() + b'{"external":true}\n')
                                (root / 'search-changes.jsonl').write_bytes(external_changes[0])
                        raise OSError('actual replace fault: ' + fault)
                    return replace(path, target)
                def append(path, mode='r', *args, **kwargs):
                    if fault == 'event' and finished[0] and not tripped[0] and path.name == 'learning-events.jsonl' and mode == 'a':
                        tripped[0] = True
                        raise OSError('actual event open fault')
                    return opened(path, mode, *args, **kwargs)
                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(Path, 'replace', persist), patch.object(Path, 'open', append), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json')), 2)
                self.assertTrue(tripped[0])
                state = refresh.read(root / 'learning-state.json')
                for key in ('queries', 'last_run_id', 'last_cycle', 'accepted_baseline'):
                    self.assertEqual(state[key], prior[key])
                self.assertEqual((root / 'searches.json').read_bytes(), external_bytes if fault in ('concurrent', 'concurrent_both') else ((root / 'candidate.json').read_bytes() if fault == 'rollback' else before))
                self.assertEqual((root / 'search-changes.jsonl').read_bytes(), external_changes[0] if fault == 'concurrent_both' else changes_before)
                cycle = next((root / 'cycles').glob('[0-9]*-*/'))
                receipt = refresh.read(cycle / 'receipt.json')
                self.assertEqual(receipt['attempt_status'], 'incomplete')
                self.assertFalse(receipt['promoted'])
                if fault in ('concurrent', 'concurrent_both', 'rollback'):
                    self.assertIn('searches.json', receipt['rollback_conflicts'])
                    self.assertIn('searches.json', receipt['residual_mutations'])
                if fault == 'concurrent_both':
                    self.assertIn('search-changes.jsonl', receipt['rollback_conflicts'])
                if fault not in ('preparation', 'start_receipt', 'start_state', 'intent'):
                    self.assertEqual((cycle / 'promotion-before-catalog.bin').read_bytes(), before)
                if fault in ('preparation', 'start_receipt', 'start_state'):
                    self.assertEqual(invoked, [])
                    self.assertIsNone(receipt['native_exit_code'])
                    self.assertIs(receipt['provider_invoked'], False)
                    self.assertFalse(receipt['stdout_available'])
                    with patch.object(refresh, 'ROOT', root):
                        self.assertTrue(refresh.verify_state_commitments(state))
                else:
                    self.assertEqual(refresh.digest(cycle / 'diff.json'), receipt['diff_stdout_sha256'])
                    self.assertEqual(refresh.digest(cycle / 'diff.stderr'), receipt['diff_stderr_sha256'])
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as blocked:
                        with self.assertRaisesRegex(ValueError, 'Cooldown'):
                            refresh.run(argparse.Namespace(proposal=None))
                        blocked.assert_not_called()
                if fault in ('preparation', 'start_receipt', 'start_state'):
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(refresh.time, 'time', return_value=state.get('next_allowed_at', 0) + 1), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    self.assertEqual(compared, ['test_old'])
                if fault == 'state':
                    preserved = (root / 'learning-state.json').read_bytes()
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as blocked, patch.object(refresh.time, 'time', return_value=state['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)  # Explicit recovery is a non-query turn.
                        blocked.assert_not_called()
                    recovered = refresh.read(root / 'learning-state.json')
                    self.assertEqual({k: v for k, v in recovered.items() if k != 'recovery_commit'}, json.loads(preserved))
                    self.assertEqual(compared, ['test_old'])
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(refresh.time, 'time', return_value=state['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    self.assertEqual(compared, ['test_old', 'test_old'])

    def test_atomic_write_does_not_follow_fixed_temporary_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sid = self.workflow(root)
            outside = root / 'untouched.txt'
            outside.write_bytes(b'untouched')
            link = root / 'learning-state.json.tmp'
            link.symlink_to(outside)
            def native(arguments, output, timeout):
                _, row = self.observation(root, 'first', sid)
                refresh.write(output.with_suffix('.json'), self.envelope([row]))
                return 0
            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
            self.assertEqual(outside.read_bytes(), b'untouched')
            self.assertTrue(link.is_symlink())

    def test_committed_state_survives_diagnostic_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sid = self.workflow(root)
            def native(arguments, output, timeout):
                _, row = self.observation(root, 'first', sid)
                refresh.write(output.with_suffix('.json'), self.envelope([row]))
                return 0
            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch('builtins.print', side_effect=OSError('diagnostic output unavailable')):
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
            state = refresh.read(root / 'learning-state.json')
            self.assertEqual(state['last_run_id'], 'first')
            self.assertEqual(refresh.read(root / 'cycles' / state['last_cycle'] / 'receipt.json')['attempt_status'], 'accepted')

    def test_write_boundary_preserves_commit_or_initial_storage_error(self):
        for fault in ('postcommit_cleanup', 'metrics_parent_mkdir', 'writer_and_cleanup'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                old, row = self.observation(root, 'old', sid)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                before = (root / 'searches.json').read_bytes()
                candidate = refresh.read(root / 'searches.json')
                candidate['searches'][0]['max_items'] += 1
                refresh.write(root / 'candidate.json', candidate)
                refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                replaced, done, tripped, cleanup_tripped = [False], [False], [False], [False]
                replace, mkdir, unlink = Path.replace, Path.mkdir, Path.unlink
                def native(arguments, output, timeout):
                    if arguments[0] == 'github-search':
                        _, fresh = self.observation(root, 'new', sid)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        done[0] = True
                    else:
                        refresh.write(output.with_suffix('.json'), self.comparison(root, 'old', 'new', sid))
                    return 0
                def commit(path, target):
                    if fault == 'writer_and_cleanup' and target.name == 'metrics.json':
                        tripped[0] = True
                        raise PermissionError('initial metrics writer fault')
                    result = replace(path, target)
                    if target == root / 'learning-state.json' and refresh.read(target).get('last_run_id') == 'new':
                        replaced[0] = True
                    return result
                def makedir(path, *args, **kwargs):
                    if fault == 'metrics_parent_mkdir' and done[0] and not tripped[0] and path.parent == root / 'cycles':
                        tripped[0] = True
                        raise PermissionError('initial metrics parent mkdir fault')
                    return mkdir(path, *args, **kwargs)
                def cleanup(path, *args, **kwargs):
                    if (fault == 'postcommit_cleanup' and replaced[0] and path.name.startswith('.learning-state.json-')) or (fault == 'writer_and_cleanup' and path.name.startswith('.metrics.json-')):
                        cleanup_tripped[0] = True
                        raise PermissionError('secondary temporary cleanup fault')
                    return unlink(path, *args, **kwargs)
                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(Path, 'replace', commit), patch.object(Path, 'mkdir', makedir), patch.object(Path, 'unlink', cleanup), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json')), 0 if fault == 'postcommit_cleanup' else 2)
                state = refresh.read(root / 'learning-state.json')
                receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                if fault == 'postcommit_cleanup':
                    self.assertTrue(replaced[0])
                    self.assertFalse(cleanup_tripped[0])
                    self.assertEqual(state['last_run_id'], 'new')
                    self.assertTrue(receipt['promoted'])
                    self.assertEqual(receipt['attempt_status'], 'accepted')
                    self.assertEqual((root / 'searches.json').read_bytes(), (root / 'candidate.json').read_bytes())
                else:
                    self.assertTrue(tripped[0])
                    self.assertEqual(receipt['attempt_status'], 'incomplete')
                    self.assertIn('initial metrics', receipt['storage_error'])
                    self.assertNotIn('secondary', receipt['storage_error'])
                    self.assertEqual(state['queries'], prior['queries'])
                    self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                    self.assertEqual((root / 'searches.json').read_bytes(), before)

    def test_terminal_commit_binds_exact_event_and_refuses_corrupt_records(self):
        faults = ('identical', 'intent_conflict', 'dangling_symlink', 'modern_traversal', 'conflict', 'duplicate', 'partial', 'wrong_root', 'wrong_version', 'noncanonical', 'receipt_mutation', 'event_mutation')
        for proposal_mode in (False, True):
            for fault in faults:
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    old, row = self.observation(root, 'old', sid)
                    prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old / 'manifest.json')}}
                    refresh.write(root / 'learning-state.json', prior)
                    before = (root / 'searches.json').read_bytes()
                    if proposal_mode:
                        candidate = refresh.read(root / 'searches.json')
                        candidate['searches'][0]['max_items'] += 1
                        refresh.write(root / 'candidate.json', candidate)
                        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                    legacy = b'{"cycle":"../../historical label","note":" preserve exact bytes "}\n'
                    events = root / 'learning-events.jsonl'
                    events.write_bytes(legacy)
                    external = root.parent / (root.name + '-outside-events')
                    self.addCleanup(external.unlink, missing_ok=True)
                    if fault == 'dangling_symlink':
                        events.unlink()
                        events.symlink_to(external)
                    replace, opened = Path.replace, Path.open
                    expected, seeded, invoked = [], [], []
                    def native(arguments, output, timeout):
                        invoked.append(arguments[0])
                        if arguments[0] == 'github-search':
                            _, fresh = self.observation(root, 'new', sid)
                            refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        else:
                            refresh.write(output.with_suffix('.json'), self.comparison(root, 'old', 'new', sid))
                        return 0
                    def persist(path, target):
                        result = replace(path, target)
                        if fault == 'intent_conflict' and target.name == 'receipt.json' and refresh.read(target).get('native_exit_code') is None:
                            (target.parent / 'receipt-precommit.json').write_bytes(b'{}\n')
                        if target.name == 'receipt-precommit.json':
                            if fault == 'dangling_symlink':
                                return result
                            intent = refresh.read(target)
                            event = {'format_version': 1, 'cycle': target.parent.name, 'outcome': intent['attempt_status'], 'receipt': str(target.relative_to(root)), 'receipt_sha256': refresh.digest(target)}
                            payload = (json.dumps(event, sort_keys=True, separators=(',', ':')) + '\n').encode()
                            expected.append(payload)
                            data = legacy
                            if fault == 'identical':
                                data += payload
                            elif fault == 'conflict':
                                data += (json.dumps({**event, 'outcome': 'failed'}, sort_keys=True, separators=(',', ':')) + '\n').encode()
                            elif fault == 'modern_traversal':
                                invalid = {**event, 'cycle': '../../escape', 'receipt': 'cycles/../../escape/receipt-precommit.json'}
                                data += (json.dumps(invalid, sort_keys=True, separators=(',', ':')) + '\n').encode()
                            elif fault == 'duplicate':
                                data += payload * 2
                            elif fault == 'partial':
                                data += b'{"cycle":'
                            elif fault == 'wrong_root':
                                data += b'[]\n'
                            elif fault == 'wrong_version':
                                data += (json.dumps({**event, 'format_version': True}) + '\n').encode()
                            elif fault == 'noncanonical':
                                data += (json.dumps(event, indent=2) + '\n').encode()
                            events.write_bytes(data)
                            seeded.append(data)
                        return result
                    @contextlib.contextmanager
                    def event_open(path, mode='r', *args, **kwargs):
                        with opened(path, mode, *args, **kwargs) as stream:
                            yield stream
                        if path == events and mode == 'a':
                            if fault == 'receipt_mutation':
                                receipt_path = root / json.loads(expected[0])['receipt']
                                receipt_path.write_bytes(b'{}\n')
                            elif fault == 'event_mutation':
                                events.write_bytes(legacy + expected[0].replace(b'"outcome":"accepted"', b'"outcome":"failed"'))
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(Path, 'replace', persist), patch.object(Path, 'open', event_open), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 0 if fault == 'identical' else 2)
                    state = refresh.read(root / 'learning-state.json')
                    if fault == 'dangling_symlink':
                        self.assertFalse(invoked)
                        self.assertEqual(state, prior)
                        self.assertEqual((root / 'searches.json').read_bytes(), before)
                        self.assertFalse(external.exists())
                        self.assertTrue(events.is_symlink())
                        continue
                    cycle = root / 'cycles' / state['last_attempt_cycle']
                    receipt = refresh.read(cycle / 'receipt.json')
                    if fault == 'identical':
                        self.assertEqual(events.read_bytes(), legacy + expected[0])
                        marker = state['terminal_commit']
                        self.assertEqual(marker['event_sha256'], hashlib.sha256(expected[0]).hexdigest())
                        self.assertEqual(marker['receipt_sha256'], refresh.digest(cycle / 'receipt-precommit.json'))
                        self.assertEqual(state['baseline_commit']['receipt_sha256'], marker['receipt_sha256'])
                        self.assertEqual(receipt['format_version'], 1)
                        self.assertTrue(state['baseline_commit'])
                    else:
                        self.assertEqual(state['queries'], prior['queries'])
                        self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                        self.assertNotIn('terminal_commit', state)
                        self.assertEqual((root / 'searches.json').read_bytes(), before)
                        self.assertEqual(receipt['attempt_status'], 'incomplete')
                        if fault == 'dangling_symlink':
                            self.assertFalse(external.exists())
                            self.assertTrue(events.is_symlink())
                        elif fault == 'intent_conflict':
                            self.assertEqual((cycle / 'receipt-precommit.json').read_bytes(), b'{}\n')
                            self.assertEqual(events.read_bytes(), legacy)
                        elif fault not in ('receipt_mutation', 'event_mutation'):
                            self.assertEqual(events.read_bytes(), seeded[0])

    def test_terminal_and_baseline_commitments_survive_warning_and_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            sid = self.workflow(root)
            stage = ['healthy']
            def native(arguments, output, timeout):
                if stage[0] == 'failed':
                    return 2
                if arguments[0] == 'github-search':
                    run, row = self.observation(root, stage[0], sid)
                    if stage[0] == 'warning':
                        row.update(issues=[], item_count=0, total_count=0)
                        refresh.write(run / (sid + '.json'), row)
                        manifest = self.manifest('warning', [row], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                        refresh.write(run / 'manifest.json', manifest)
                        refresh.write(root / 'results/manifest.json', manifest)
                    refresh.write(output.with_suffix('.json'), self.envelope([row]))
                else:
                    refresh.write(output.with_suffix('.json'), self.comparison(root, 'healthy', stage[0], sid))
                return 0
            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                healthy = refresh.read(root / 'learning-state.json')
                baseline = healthy['baseline_commit']
                predecessor = healthy['terminal_commit']
                for mode, outcome in (('warning', 'accepted_with_coverage_warning'), ('failed', 'failed')):
                    stage[0] = mode
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                    state = refresh.read(root / 'learning-state.json')
                    self.assertEqual(state['baseline_commit'], baseline)
                    self.assertEqual(state['last_run_id'], 'healthy')
                    self.assertEqual(state['terminal_commit']['outcome'], outcome)
                    intent = refresh.read(root / state['terminal_commit']['receipt'])
                    self.assertEqual(intent['predecessor_terminal_commit'], predecessor)
                    self.assertEqual(intent['predecessor_baseline_commit'], baseline)
                    predecessor = state['terminal_commit']
                    self.assertEqual(intent['state_projection_sha256'], refresh.projection_digest(state))
                    self.assertEqual(baseline['projection_sha256'], refresh.projection_digest(state, baseline=True))
                    altered = {**state, 'next_allowed_at': 123, 'last_attempt_cycle': 'mutable', 'latest_observation': {'test': True}}
                    self.assertEqual(refresh.projection_digest(altered), refresh.projection_digest(state))
                    if mode == 'warning':
                        self.assertEqual(state['queries'][sid]['empty_streak'], 1)
                        warning_queries = state['queries']
                    else:
                        self.assertEqual(state['queries'], warning_queries)
                previous = state
                stage[0] = 'next'
                replace = Path.replace
                def reject_commit(path, target):
                    if target == root / 'learning-state.json' and refresh.read(path).get('terminal_commit', {}).get('cycle') != previous['terminal_commit']['cycle']:
                        raise PermissionError('final state write blocked')
                    return replace(path, target)
                with patch.object(Path, 'replace', reject_commit):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                rejected = refresh.read(root / 'learning-state.json')
                self.assertEqual(rejected['terminal_commit'], previous['terminal_commit'])
                self.assertEqual(rejected['baseline_commit'], baseline)
                self.assertEqual(rejected['queries'], previous['queries'])
                self.assertEqual(rejected['last_run_id'], 'healthy')
                self.assertIn('next_allowed_at', rejected)
                intent = refresh.read(root / 'cycles' / rejected['last_attempt_cycle'] / 'receipt.json')
                self.assertEqual((intent['attempt_status'], intent['failed_stage']), ('incomplete', 'state'))
                records = [json.loads(line) for line in (root / 'learning-events.jsonl').read_bytes().splitlines()]
                self.assertEqual([record['outcome'] for record in records], ['accepted', 'accepted_with_coverage_warning', 'failed', 'accepted'])

    def test_modern_prior_proofs_fail_closed_before_acceptance(self):
        faults = ('valid', 'missing_format', 'all_proofs_removed', 'bool_format', 'missing_terminal', 'missing_baseline', 'receipt_missing', 'receipt_bytes', 'event_bytes', 'queries', 'baseline', 'bool_exit', 'bool_runner', 'bool_receipt_version', 'warning_without_coverage', 'marker_reference')
        for proposal_mode in (False, True):
            for fault in faults:
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    stage = ['old']
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            _, row = self.observation(root, stage[0], sid)
                            refresh.write(output.with_suffix('.json'), self.envelope([row]))
                        else:
                            refresh.write(output.with_suffix('.json'), self.comparison(root, 'old', 'new', sid))
                        return 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                        state = refresh.read(root / 'learning-state.json')
                        if fault == 'missing_format':
                            state.pop('commit_format_version')
                        elif fault == 'all_proofs_removed':
                            for key in ('commit_format_version', 'terminal_commit', 'baseline_commit', 'coverage_commit'):
                                state.pop(key, None)
                        elif fault == 'bool_format':
                            state['commit_format_version'] = True
                        elif fault == 'missing_terminal':
                            state.pop('terminal_commit')
                        elif fault == 'missing_baseline':
                            state.pop('baseline_commit')
                        elif fault == 'queries':
                            state['queries'][sid]['empty_streak'] = 7
                        elif fault == 'baseline':
                            state['accepted_baseline']['manifest_sha256'] = '0' * 64
                        elif fault == 'marker_reference':
                            state['terminal_commit']['receipt'] = '../../outside.json'
                        elif fault in ('receipt_missing', 'receipt_bytes'):
                            path = root / state['terminal_commit']['receipt']
                            path.unlink() if fault == 'receipt_missing' else path.write_bytes(b'{}\n')
                        elif fault == 'event_bytes':
                            path = root / 'learning-events.jsonl'
                            path.write_bytes(path.read_bytes().replace(b'"outcome":"accepted"', b'"outcome":"failed"'))
                        elif fault in ('bool_exit', 'bool_runner', 'bool_receipt_version', 'warning_without_coverage'):
                            path = root / state['terminal_commit']['receipt']
                            value = refresh.read(path)
                            if fault == 'warning_without_coverage':
                                value.update(attempt_status='accepted_with_coverage_warning', runner_exit_code=2, fresh_snapshot_accepted=False)
                            else:
                                value[{'bool_exit': 'native_exit_code', 'bool_runner': 'runner_exit_code', 'bool_receipt_version': 'format_version'}[fault]] = True if fault == 'bool_receipt_version' else False
                            refresh.write(path, value)
                            event = json.loads((root / 'learning-events.jsonl').read_bytes())
                            event['receipt_sha256'] = refresh.digest(path)
                            event['outcome'] = value['attempt_status']
                            raw = (json.dumps(event, sort_keys=True, separators=(',', ':')) + '\n').encode()
                            (root / 'learning-events.jsonl').write_bytes(raw)
                            for label in ('terminal_commit', 'baseline_commit'):
                                state[label].update(receipt_sha256=event['receipt_sha256'], event_sha256=hashlib.sha256(raw).hexdigest(), outcome=event['outcome'])
                        refresh.write(root / 'learning-state.json', state)
                        before = (root / 'searches.json').read_bytes()
                        if proposal_mode:
                            candidate = refresh.read(root / 'searches.json')
                            candidate['searches'][0]['max_items'] += 1
                            refresh.write(root / 'candidate.json', candidate)
                            refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                        stage[0] = 'new'
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 0 if fault == 'valid' else 2)
                        after = refresh.read(root / 'learning-state.json')
                        if fault != 'valid':
                            self.assertEqual(after['queries'], state['queries'])
                            self.assertEqual(after['accepted_baseline'], state['accepted_baseline'])
                            self.assertEqual(after.get('terminal_commit'), state.get('terminal_commit'))
                            self.assertEqual((root / 'searches.json').read_bytes(), before)
                            cycle = max((root / 'cycles').iterdir(), key=lambda path: path.stat().st_mtime_ns)
                            receipt = refresh.read(cycle / 'receipt.json')
                            self.assertEqual(receipt['failed_stage'], 'baseline_resolution')
                            self.assertFalse(receipt['fresh_snapshot_accepted'])
                        else:
                            self.assertEqual(after['last_run_id'], 'new')

    def test_old_baseline_proof_after_warning_failure_and_restoration(self):
        for fault in ('receipt_missing', 'marker_root'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                stage, comparisons = ['healthy'], []
                def native(arguments, output, timeout):
                    if stage[0] == 'failed':
                        return 2
                    if arguments[0] == 'github-search':
                        run, row = self.observation(root, stage[0], sid)
                        if stage[0] == 'warning':
                            row.update(issues=[], item_count=0, total_count=0)
                            refresh.write(run / (sid + '.json'), row)
                            manifest = self.manifest('warning', [row], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                            refresh.write(run / 'manifest.json', manifest)
                            refresh.write(root / 'results/manifest.json', manifest)
                        refresh.write(output.with_suffix('.json'), self.envelope([row]))
                    else:
                        comparisons.append(Path(arguments[2]).name)
                        refresh.write(output.with_suffix('.json'), self.comparison(root, 'healthy', stage[0], sid))
                    return 0
                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as command, contextlib.redirect_stdout(io.StringIO()):
                    for mode, rc in (('healthy', 0), ('warning', 2), ('failed', 2)):
                        stage[0] = mode
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), rc)
                    prior = refresh.read(root / 'learning-state.json')
                    path = root / prior['baseline_commit']['receipt']
                    before = path.read_bytes()
                    damaged = copy.deepcopy(prior)
                    path.unlink() if fault == 'receipt_missing' else damaged.update(baseline_commit=[])
                    refresh.write(root / 'learning-state.json', damaged)
                    stage[0] = 'next'
                    calls = command.call_count
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                    self.assertEqual(command.call_count, calls)
                    rejected = refresh.read(root / 'learning-state.json')
                    self.assertEqual(rejected['queries'], prior['queries'])
                    self.assertEqual(rejected['accepted_baseline'], prior['accepted_baseline'])
                    self.assertEqual(rejected['terminal_commit'], prior['terminal_commit'])
                    failure = refresh.read(root / 'cycles' / rejected['last_failed_cycle'] / 'receipt.json')
                    self.assertEqual(failure['failed_stage'], 'baseline_resolution')
                    path.write_bytes(before)  # Explicit exact evidence restoration, never an automatic runner reset.
                    refresh.write(root / 'learning-state.json', prior)
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    self.assertEqual(comparisons, ['test_healthy', 'test_healthy'])
                    self.assertEqual(refresh.read(root / 'learning-state.json')['last_run_id'], 'next')

    def test_retained_coverage_legacy_and_null_native_proofs(self):
        for proposal_mode in (False, True):
            for fault in ('missing_coverage', 'coverage_root', 'fake_legacy', 'null_native'):
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    stage = ['healthy']
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            run, row = self.observation(root, stage[0], sid)
                            if stage[0] == 'warning':
                                row.update(issues=[], item_count=0, total_count=0)
                                refresh.write(run / (sid + '.json'), row)
                                manifest = self.manifest('warning', [row], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                                refresh.write(run / 'manifest.json', manifest)
                                refresh.write(root / 'results/manifest.json', manifest)
                            refresh.write(output.with_suffix('.json'), self.envelope([row]))
                        else:
                            refresh.write(output.with_suffix('.json'), self.comparison(root, 'healthy', stage[0], sid))
                            return 124 if stage[0] == 'failed' else 0
                        return 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as command, contextlib.redirect_stdout(io.StringIO()):
                        for mode, rc in (('healthy', 0), ('warning', 2), ('failed', 2)):
                            stage[0] = mode
                            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), rc)
                        state = refresh.read(root / 'learning-state.json')
                        if fault == 'missing_coverage':
                            state.pop('coverage_commit')
                        elif fault == 'coverage_root':
                            state['coverage_commit'] = []
                        else:
                            path = root / state['terminal_commit']['receipt']
                            intent = refresh.read(path)
                            if fault == 'fake_legacy':
                                state['baseline_legacy'] = True
                                state.pop('baseline_commit')
                                intent['state_projection_sha256'] = refresh.projection_digest(state)
                            else:
                                self.assertEqual((intent['native_exit_code'], intent['diff_exit_code']), (0, 124))
                                intent['native_exit_code'] = None
                            refresh.write(path, intent)
                            events = root / 'learning-events.jsonl'
                            records = [json.loads(line) for line in events.read_bytes().splitlines()]
                            event = records[-1]
                            event['receipt_sha256'] = refresh.digest(path)
                            raw = (json.dumps(event, sort_keys=True, separators=(',', ':')) + '\n').encode()
                            events.write_bytes(b''.join((json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode() for value in records))
                            state['terminal_commit'].update(receipt_sha256=event['receipt_sha256'], event_sha256=hashlib.sha256(raw).hexdigest())
                        refresh.write(root / 'learning-state.json', state)
                        before = (root / 'searches.json').read_bytes()
                        if proposal_mode:
                            candidate = refresh.read(root / 'searches.json')
                            candidate['searches'][0]['max_items'] += 1
                            refresh.write(root / 'candidate.json', candidate)
                            refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                        stage[0] = 'next'
                        calls = command.call_count
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 2)
                        self.assertEqual(command.call_count, calls)
                        rejected = refresh.read(root / 'learning-state.json')
                        self.assertEqual(rejected['queries'], state['queries'])
                        self.assertEqual(rejected['accepted_baseline'], state['accepted_baseline'])
                        self.assertEqual((root / 'searches.json').read_bytes(), before)
                        failure = refresh.read(root / 'cycles' / rejected['last_failed_cycle'] / 'receipt.json')
                        self.assertEqual(failure['failed_stage'], 'baseline_resolution')
                        self.assertFalse(failure['fresh_snapshot_accepted'])

    def test_launch_failure_and_unvalidated_preparation_cannot_poison_proof(self):
        for proposal_mode in (False, True):
            for fault in ('launch', 'stdout_open', 'stderr_open', 'invalid_then_preparation'):
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    stage, comparisons = ['healthy'], []
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            _, row = self.observation(root, stage[0], sid)
                            refresh.write(output.with_suffix('.json'), self.envelope([row]))
                        else:
                            comparisons.append(Path(arguments[2]).name)
                            refresh.write(output.with_suffix('.json'), self.comparison(root, 'healthy', stage[0], sid))
                        return 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    original = refresh.read(root / 'learning-state.json')
                    before = (root / 'searches.json').read_bytes()
                    policy = refresh.read(root / 'policy.json')
                    policy['minimum_seconds_between_runs'] = 30
                    refresh.write(root / 'policy.json', policy)
                    if proposal_mode:
                        candidate = refresh.read(root / 'searches.json')
                        candidate['searches'][0]['max_items'] += 1
                        refresh.write(root / 'candidate.json', candidate)
                        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                    args = argparse.Namespace(proposal='proposal.json' if proposal_mode else None)
                    if fault in ('launch', 'stdout_open', 'stderr_open'):
                        original_open = Path.open
                        def acquire(path, *args, **kwargs):
                            if fault.endswith('_open') and path.name == ('response.json' if fault == 'stdout_open' else 'response.stderr') and args == ('w',):
                                raise PermissionError('offline output acquisition denied')
                            return original_open(path, *args, **kwargs)
                        with patch.object(Path, 'open', acquire), patch.object(refresh, 'ROOT', root), patch.object(refresh.subprocess, 'Popen', side_effect=FileNotFoundError('offline native executable unavailable')) as launch, contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(args), 2)
                            self.assertEqual(launch.call_count, 1 if fault == 'launch' else 0)
                        failed = refresh.read(root / 'learning-state.json')
                        receipt = refresh.read(root / 'cycles' / failed['last_failed_cycle'] / 'receipt.json')
                        self.assertIsNone(receipt['native_exit_code'])
                        for label in ('stdout', 'stderr'):
                            available = fault == 'launch' or (fault == 'stderr_open' and label == 'stdout')
                            self.assertIs(receipt[label + '_available'], available)
                            self.assertEqual(receipt[label + '_sha256'], hashlib.sha256(b'').hexdigest() if available else None)
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as blocked:
                            with self.assertRaisesRegex(ValueError, 'Cooldown'):
                                refresh.run(args)
                            blocked.assert_not_called()
                    else:
                        invalid = {**original, 'terminal_commit': []}
                        refresh.write(root / 'learning-state.json', invalid)
                        replace = Path.replace
                        def early_write(path, target):
                            if target.name == 'catalog-before.json':
                                raise PermissionError('offline early preparation writer fault')
                            return replace(path, target)
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as blocked, patch.object(Path, 'replace', early_write), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(args), 2)
                            blocked.assert_not_called()
                        failed = refresh.read(root / 'learning-state.json')
                        stage[0] = 'probe'
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as blocked, contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(args), 2)
                            blocked.assert_not_called()
                        self.assertEqual(failed['terminal_commit'], [])
                        refresh.write(root / 'learning-state.json', original)  # Exact evidence restoration only.
                    self.assertEqual(failed['queries'], original['queries'])
                    self.assertEqual(failed['accepted_baseline'], original['accepted_baseline'])
                    self.assertEqual((root / 'searches.json').read_bytes(), before)
                    stage[0] = 'recovered'
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(refresh.time, 'time', return_value=failed.get('next_allowed_at', 0) + 1), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(args), 0)
                    self.assertEqual(comparisons, ['test_healthy'])
                    self.assertEqual(refresh.read(root / 'learning-state.json')['last_run_id'], 'recovered')
                    if fault in ('launch', 'stdout_open', 'stderr_open'):
                        self.assertIs(receipt['provider_invoked'], False)
                        self.assertEqual(receipt['launch_status'], 'failed_before_start')
                        if fault.endswith('_open'):
                            self.assertEqual(receipt['attempt_status'], 'incomplete')
                            self.assertIn('output acquisition denied', receipt['storage_error'])

    def test_guarded_startup_recovery_and_faults_preserve_old_acceptance(self):
        cases = [(boundary, None) for boundary in ('catalog', 'changelog', 'precommit', 'event', 'state', 'committed')]
        cases += [('event', fault) for fault in ('intent', 'rollback', 'result', 'commit', 'conflict', 'catalog_conflict', 'changelog_conflict', 'diagnostic', 'partial', 'duplicate', 'result_partial', 'result_duplicate')]
        for proposal_mode in (False, True):
            for boundary, fault in cases:
                if not proposal_mode and (boundary in ('catalog', 'changelog') or fault in ('rollback', 'conflict', 'catalog_conflict', 'changelog_conflict')):
                    continue
                with self.subTest(proposal=proposal_mode, boundary=boundary, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid, stage, bases = self.workflow(root), ['healthy'], []
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            _, row = self.observation(root, stage[0], sid)
                            refresh.write(output.with_suffix('.json'), self.envelope([row]))
                        else:
                            base = Path(arguments[2]).name.removeprefix('test_')
                            bases.append(base)
                            refresh.write(output.with_suffix('.json'), self.comparison(root, base, stage[0], sid))
                        return 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    accepted = refresh.read(root / 'learning-state.json')
                    before, changes = (root / 'searches.json').read_bytes(), root / 'search-changes.jsonl'
                    if proposal_mode:
                        changes.write_bytes(b'{"historical":true}\n')
                        candidate = refresh.read(root / 'searches.json')
                        candidate['searches'][0]['max_items'] += 1
                        refresh.write(root / 'candidate.json', candidate)
                        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                    changelog_before = changes.read_bytes() if changes.exists() else None
                    policy = refresh.read(root / 'policy.json'); policy['minimum_seconds_between_runs'] = 30
                    refresh.write(root / 'policy.json', policy)
                    replace, opened = Path.replace, Path.open
                    stage[0] = 'interrupted'
                    def interrupt(path, target):
                        final = target == root / 'learning-state.json' and json.loads(path.read_bytes()).get('last_run_id') == 'interrupted'
                        if boundary == 'state' and final:
                            raise KeyboardInterrupt('offline pre-state interruption')
                        result = replace(path, target)
                        if (boundary == 'catalog' and target == root / 'searches.json') or (boundary == 'changelog' and target == changes) or (boundary == 'precommit' and target.name == 'receipt-precommit.json') or (boundary == 'committed' and final):
                            raise KeyboardInterrupt('offline post-replace interruption')
                        return result
                    @contextlib.contextmanager
                    def event(path, mode='r', *args, **kwargs):
                        with opened(path, mode, *args, **kwargs) as stream:
                            yield stream
                        if boundary == 'event' and path.name == 'learning-events.jsonl' and mode == 'a':
                            raise KeyboardInterrupt('offline post-event interruption')
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(Path, 'replace', interrupt), patch.object(Path, 'open', event), contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(KeyboardInterrupt):
                            refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None))
                    interrupted = refresh.read(root / 'learning-state.json')
                    cycle = root / 'cycles' / interrupted['last_attempt_cycle']
                    frozen = {path.name: path.read_bytes() for path in cycle.iterdir() if path.is_file()}
                    event_bytes = (root / 'learning-events.jsonl').read_bytes()
                    stage[0] = 'recovered'
                    if boundary == 'committed':
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(refresh.time, 'time', return_value=interrupted['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                        self.assertEqual(bases[-1], 'interrupted')
                        self.assertEqual((root / 'searches.json').read_bytes(), (root / 'candidate.json').read_bytes() if proposal_mode else before)
                        self.assertFalse((cycle / 'recovery-result.json').exists())
                        continue
                    postimage = (root / 'searches.json').read_bytes()
                    if fault in ('conflict', 'catalog_conflict'):
                        (root / 'searches.json').write_bytes(b'{"external":true}\n')
                    if fault in ('conflict', 'changelog_conflict'):
                        changes.write_bytes(b'{"external_append":true}\n')
                    if fault in ('partial', 'duplicate', 'result_partial', 'result_duplicate'):
                        (cycle / ('recovery-result.json' if fault.startswith('result_') else 'recovery-intent.json')).write_bytes(b'{' if fault.endswith('partial') else b'{}\n{}\n')
                    def recover_writer(path, target):
                        name = {'intent': 'recovery-intent.json', 'rollback': 'searches.json', 'result': 'recovery-result.json', 'commit': 'learning-state.json', 'diagnostic': 'recovery-diagnostic.json'}.get(fault)
                        if target.name == name:
                            raise PermissionError('offline recovery writer fault')
                        return replace(path, target)
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as blocked, patch.object(Path, 'replace', recover_writer), patch.object(refresh.time, 'time', return_value=interrupted['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                        blocked.assert_not_called()
                    current = refresh.read(root / 'learning-state.json')
                    for key in ('accepted_baseline', 'last_run_id', 'last_cycle', 'queries', 'terminal_commit', 'baseline_commit', 'coverage_commit', 'next_allowed_at'):
                        self.assertEqual(current.get(key), interrupted.get(key))
                    for name, payload in frozen.items():
                        self.assertEqual((cycle / name).read_bytes(), payload)
                    self.assertEqual((root / 'learning-events.jsonl').read_bytes(), event_bytes)
                    if fault in ('conflict', 'catalog_conflict', 'changelog_conflict'):
                        self.assertEqual((root / 'searches.json').read_bytes(), postimage if fault == 'changelog_conflict' else b'{"external":true}\n')
                        self.assertEqual(changes.read_bytes(), changelog_before if fault == 'catalog_conflict' else b'{"external_append":true}\n')
                        # Reverse rollback can restore changelog before detecting an external catalog edit.
                        (root / 'searches.json').write_bytes(postimage); changes.write_bytes(frozen['promotion-after-changelog.bin'])
                    if fault == 'diagnostic':
                        self.assertIn('recovery_commit', current)
                        self.assertFalse((cycle / 'recovery-diagnostic.json').exists())
                        self.assertEqual((root / 'searches.json').read_bytes(), before)
                        self.assertEqual(changes.read_bytes() if changes.exists() else None, changelog_before)
                    if fault in ('partial', 'duplicate', 'result_partial', 'result_duplicate'):
                        self.assertEqual((root / 'searches.json').read_bytes(), postimage)
                        self.assertNotIn('recovery_commit', current)
                        continue  # Conflicting evidence requires exact operator restoration.
                    if fault is not None and fault != 'diagnostic':
                        self.assertNotIn('recovery_commit', current)
                        retry_records = {name: (cycle / name).read_bytes() for name in ('recovery-intent.json', 'recovery-result.json') if (cycle / name).exists()}
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as blocked, patch.object(refresh.time, 'time', return_value=interrupted['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                            blocked.assert_not_called()
                        for name, payload in retry_records.items():
                            self.assertEqual((cycle / name).read_bytes(), payload)
                    self.assertEqual((root / 'searches.json').read_bytes(), before)
                    self.assertEqual(changes.read_bytes() if changes.exists() else None, changelog_before)
                    recovered = refresh.read(root / 'learning-state.json')
                    self.assertEqual(recovered['recovery_commit']['receipt_sha256'], refresh.digest(cycle / 'recovery-result.json'))
                    exact_records = {name: (cycle / name).read_bytes() for name in ('recovery-intent.json', 'recovery-result.json')}
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(refresh.time, 'time', return_value=interrupted['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    self.assertEqual(bases[-1], 'healthy')
                    for name, payload in exact_records.items():
                        self.assertEqual((cycle / name).read_bytes(), payload)
                    self.assertEqual(refresh.read(root / 'learning-state.json')['recovery_commit'], recovered['recovery_commit'])
                    if proposal_mode and boundary == 'event' and fault is None:
                        prior_recovery = recovered['recovery_commit']
                        result_bytes = (cycle / 'recovery-result.json').read_bytes()
                        clock = refresh.read(root / 'learning-state.json')['next_allowed_at'] + 1
                        stage[0] = 'second_interruption'
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(Path, 'open', event), patch.object(refresh.time, 'time', return_value=clock), contextlib.redirect_stdout(io.StringIO()):
                            with self.assertRaises(KeyboardInterrupt):
                                refresh.run(argparse.Namespace(proposal=None))
                        second = refresh.read(root / 'learning-state.json')
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as blocked, patch.object(refresh.time, 'time', return_value=second['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                            blocked.assert_not_called()
                        intent = refresh.read(root / 'cycles' / second['last_attempt_cycle'] / 'recovery-intent.json')
                        self.assertEqual(intent['predecessor_recovery_commit'], prior_recovery)
                        stage[0] = 'chain_healthy'
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), patch.object(refresh.time, 'time', return_value=second['next_allowed_at'] + 1), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                        self.assertEqual((cycle / 'recovery-result.json').read_bytes(), result_bytes)

    def test_reached_bound_artifacts_are_required_and_restoration_admits(self):
        for proposal_mode in (False, True):
            for superseded in (False, True):
                for artifact in ('preparation-intent.json', 'start-intent.json', 'promotion-intent.json', 'promotion-before-catalog.bin'):
                    for fault in ('missing', 'changed'):
                        with self.subTest(proposal=proposal_mode, superseded=superseded, artifact=artifact, fault=fault), tempfile.TemporaryDirectory() as directory:
                            root = Path(directory).resolve()
                            sid = self.workflow(root)
                            stage = ['promoted']
                            def proposal():
                                candidate = refresh.read(root / 'searches.json')
                                candidate['searches'][0]['max_items'] += 1
                                refresh.write(root / 'candidate.json', candidate)
                                refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                            def native(arguments, output, timeout):
                                if arguments[0] == 'github-search':
                                    _, row = self.observation(root, stage[0], sid)
                                    refresh.write(output.with_suffix('.json'), self.envelope([row]))
                                else:
                                    base = Path(arguments[2]).name.removeprefix('test_')
                                    refresh.write(output.with_suffix('.json'), self.comparison(root, base, stage[0], sid))
                                return 0
                            proposal()
                            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                                self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json')), 0)
                                bound = refresh.read(root / 'learning-state.json')
                                if superseded:
                                    stage[0] = 'successor'
                                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                            path = root / 'cycles' / bound['last_cycle'] / artifact
                            original = path.read_bytes()
                            if proposal_mode:
                                proposal()
                            args = argparse.Namespace(proposal='proposal.json' if proposal_mode else None)
                            state_bytes, catalog_bytes = (root / 'learning-state.json').read_bytes(), (root / 'searches.json').read_bytes()
                            path.unlink() if fault == 'missing' else path.write_bytes(b'{}\n')
                            stage[0] = 'refused'
                            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as blocked, contextlib.redirect_stdout(io.StringIO()):
                                self.assertEqual(refresh.run(args), 2)
                                blocked.assert_not_called()
                            self.assertEqual((root / 'learning-state.json').read_bytes(), state_bytes)
                            self.assertEqual((root / 'searches.json').read_bytes(), catalog_bytes)
                            path.write_bytes(original)  # Exact retained artifact restoration, never reconstruction.
                            stage[0] = 'restored'
                            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                                self.assertEqual(refresh.run(args), 0)

    def test_startup_classifies_history_and_blocks_interrupted_attempts(self):
        for proposal_mode in (False, True):
            for fault in ('start', 'precommit', 'ancestor', 'missing_start', 'journal', 'preparation'):
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    stage = ['first']
                    refresh.write(root / 'cycles/archive/receipt.json', {'cycle': 'archive', 'native_exit_code': 0})
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            _, row = self.observation(root, stage[0], sid)
                            refresh.write(output.with_suffix('.json'), self.envelope([row]))
                        else:
                            base = Path(arguments[2]).name.removeprefix('test_')
                            refresh.write(output.with_suffix('.json'), self.comparison(root, base, stage[0], sid))
                        return 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                        first = refresh.read(root / 'learning-state.json')
                        stage[0] = 'second'
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    accepted = refresh.read(root / 'learning-state.json')
                    with patch.object(refresh, 'ROOT', root):
                        classified = refresh.startup_history(accepted)
                    self.assertEqual(classified['cycles'][first['last_cycle']], 'superseded')
                    self.assertEqual(classified['cycles']['archive'], 'limited_history')
                    self.assertIn('archive', classified['limited_history_frontier'])
                    before = (root / 'searches.json').read_bytes()
                    if proposal_mode:
                        candidate = refresh.read(root / 'searches.json')
                        candidate['searches'][0]['max_items'] += 1
                        refresh.write(root / 'candidate.json', candidate)
                        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                    args = argparse.Namespace(proposal='proposal.json' if proposal_mode else None)
                    if fault == 'ancestor':
                        path = root / first['terminal_commit']['receipt']
                        path.write_bytes(path.read_bytes() + b' ')
                    else:
                        stage[0] = 'interrupted'
                        replace = Path.replace
                        def interrupt(path, target):
                            if target.name == ('catalog-used.json' if fault == 'preparation' else 'receipt-precommit.json'):
                                raise KeyboardInterrupt('offline process interruption at storage boundary')
                            return replace(path, target)
                        def start_interrupt(*args):
                            raise KeyboardInterrupt('offline process interruption before search')
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', start_interrupt if fault in ('start', 'missing_start') else native), patch.object(Path, 'replace', interrupt if fault in ('precommit', 'journal', 'preparation') else replace), contextlib.redirect_stdout(io.StringIO()):
                            with self.assertRaises(KeyboardInterrupt):
                                refresh.run(args)
                    interrupted = refresh.read(root / 'learning-state.json')
                    if fault not in ('ancestor', 'preparation'):
                        cycle = root / 'cycles' / interrupted['last_attempt_cycle']
                        start_path = cycle / 'start-intent.json'
                        self.assertEqual(interrupted['attempt_start_commit']['start_intent_sha256'], refresh.digest(start_path))
                        if proposal_mode and fault in ('precommit', 'journal'):
                            admission = interrupted['recovery_admission']
                            self.assertEqual(admission['promotion_intent_sha256'], refresh.digest(cycle / 'promotion-intent.json'))
                            self.assertEqual(admission['catalog_before_sha256'], hashlib.sha256(before).hexdigest())
                            self.assertEqual(admission['predecessors']['terminal'], accepted['terminal_commit'])
                        if fault == 'missing_start':
                            start_path.unlink()
                        if fault == 'journal' and proposal_mode:
                            (cycle / 'promotion-intent.json').write_bytes(b'{}\n')
                    preserved = (root / 'learning-state.json').read_bytes()
                    stage[0] = 'probe'
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as blocked, contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(args), 2)
                        blocked.assert_not_called()
                    recovered = refresh.read(root / 'learning-state.json')
                    if fault in ('start', 'precommit') or (fault == 'journal' and not proposal_mode):
                        self.assertEqual({k: v for k, v in recovered.items() if k != 'recovery_commit'}, json.loads(preserved))
                        self.assertIn('recovery_commit', recovered)
                    else:
                        self.assertEqual((root / 'learning-state.json').read_bytes(), preserved)
                    self.assertEqual((root / 'searches.json').read_bytes(), before if fault != 'journal' or not proposal_mode else (root / 'candidate.json').read_bytes())
                    self.assertEqual(refresh.read(root / 'learning-state.json')['accepted_baseline'], accepted['accepted_baseline'])

    def test_post_launch_wait_and_close_errors_are_not_prestart_failures(self):
        class ClosingStream(io.StringIO):
            def close(self):
                super().close()
                raise PermissionError('offline post-launch stream close')
        for fault in ('wait', 'close'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                streams = [ClosingStream() if fault == 'close' else io.StringIO(), io.StringIO()]
                with patch.object(Path, 'open', side_effect=streams), patch.object(refresh.subprocess, 'Popen') as launch:
                    launch.return_value.wait.side_effect = PermissionError('offline child wait') if fault == 'wait' else None
                    launch.return_value.wait.return_value = 0
                    with self.assertRaises(PermissionError) as caught:
                        refresh.command(['offline'], Path(directory) / 'response', 1)
                    self.assertNotIsInstance(caught.exception, refresh.NativeLaunchFailure)
                    self.assertEqual(launch.call_count, 1)
                    launch.return_value.wait.assert_called_once_with(timeout=1)

    def test_proposal_comparison_failure_never_promotes(self):
        for diff_exit, envelope in ((1, {}), (0, {'status': 'SUCCESS'})):
            with self.subTest(diff_exit=diff_exit), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                old_dir, row = self.observation(root, 'old', sid)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                candidate = refresh.read(root / 'searches.json')
                candidate['searches'][0]['query'] += ' in:title'
                refresh.write(root / 'candidate.json', candidate)
                before = (root / 'searches.json').read_bytes()
                refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})

                def native(arguments, output, timeout):
                    if arguments[0] == 'github-search':
                        _, fresh = self.observation(root, 'new', sid)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        return 0
                    refresh.write(output.with_suffix('.json'), envelope)
                    output.with_suffix('.stderr').write_text('diagnostics')
                    return diff_exit

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json')), 2)
                self.assertEqual((root / 'searches.json').read_bytes(), before)
                state = refresh.read(root / 'learning-state.json')
                self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                self.assertEqual(state['queries'], prior['queries'])

    def test_snapshot_contract_rejects_unbound_or_invalid_observations(self):
        for fault in ('manifest_root', 'response_root', 'results_root', 'duplicate', 'escape', 'stdout_mismatch', 'multiple_arrays', 'count', 'top_mismatch', 'valid'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)

                def native(arguments, output, timeout):
                    run, row = self.observation(root, 'first', sid)
                    artifact = run / (sid + '.json')
                    response = self.envelope([row])
                    if fault == 'manifest_root':
                        refresh.write(run / 'manifest.json', [])
                    elif fault in ('response_root', 'results_root'):
                        response = [] if fault == 'response_root' else {**self.envelope([row]), 'results': {}}
                    elif fault == 'duplicate':
                        response['results'].append(row)
                    elif fault == 'escape':
                        manifest = refresh.read(run / 'manifest.json')
                        manifest['artifacts'] = ['../../' + sid + '.json']
                        refresh.write(run / 'manifest.json', manifest)
                        refresh.write(root / 'results/manifest.json', manifest)
                    elif fault == 'stdout_mismatch':
                        response['results'] = [{**row, 'total_count': 2}]
                    elif fault in ('multiple_arrays', 'count'):
                        row = {**row, 'items': row['issues']} if fault == 'multiple_arrays' else {**row, 'item_count': 2}
                        refresh.write(artifact, row)
                        response['results'] = [row]
                    elif fault == 'top_mismatch':
                        refresh.write(root / 'results/manifest.json', {**refresh.read(run / 'manifest.json'), 'total_items': 7})
                    refresh.write(output.with_suffix('.json'), response)
                    return 0

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0 if fault == 'valid' else 2)
                state = refresh.read(root / 'learning-state.json')
                receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                if fault == 'valid':
                    artifact = root / 'results/runs/test_first' / (sid + '.json')
                    self.assertEqual(receipt['artifact_sha256'][sid], hashlib.sha256(artifact.read_bytes()).hexdigest())
                else:
                    self.assertNotIn('accepted_baseline', state)
                    self.assertEqual(receipt['attempt_status'], 'failed')

    def test_diff_rows_must_bind_to_both_snapshots_and_report_truthful_totals(self):
        faults = ('root', 'queries_root', 'missing', 'duplicate', 'type', 'fingerprint', 'run_id', 'count', 'summary', 'incompatible', 'valid', 'approved_drift')
        for fault in faults:
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                old_dir, row = self.observation(root, 'old', sid)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                proposal = None
                if fault == 'approved_drift':
                    catalog = refresh.read(root / 'searches.json')
                    catalog['searches'][0]['query'] += ' in:title'
                    refresh.write(root / 'candidate.json', catalog)
                    proposal = 'proposal.json'
                    refresh.write(root / proposal, {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})

                def native(arguments, output, timeout):
                    if arguments[0] == 'github-search':
                        run, fresh = self.observation(root, 'new', sid)
                        if fault == 'approved_drift':
                            fresh['issues'][0]['number'] = 2
                            refresh.write(run / (sid + '.json'), fresh)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        return 0
                    outcome = self.comparison(root, 'old', 'new', sid)
                    query = outcome['queries'][0]
                    if fault in ('root', 'queries_root'):
                        outcome = [] if fault == 'root' else {**outcome, 'queries': {}}
                    elif fault in ('missing', 'duplicate'):
                        outcome['queries'] = [] if fault == 'missing' else [query, query]
                    elif fault in ('type', 'fingerprint', 'run_id', 'count'):
                        key = {'type': 'search_type', 'fingerprint': 'query_fingerprint', 'run_id': 'baseline_run_id', 'count': 'candidate_count'}[fault]
                        query[key] = 7 if fault == 'count' else 'wrong'
                    elif fault in ('summary', 'incompatible'):
                        outcome['total_queries_compared' if fault == 'summary' else 'incompatible_queries'] = 7
                    elif fault == 'approved_drift':
                        outcome['incompatible_queries'] = 1

                    refresh.write(output.with_suffix('.json'), outcome)
                    return 0

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=proposal)), 0 if fault in ('valid', 'approved_drift') else 2)
                state = refresh.read(root / 'learning-state.json')
                receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                if fault == 'approved_drift':
                    sanitized = refresh.read(root / receipt['comparison_evidence'])
                    self.assertEqual(receipt['suppressed_queries'], [sid])
                    self.assertEqual(sanitized['queries'][0]['new_count'], 0)
                    self.assertEqual(sanitized['queries'][0]['items'], [])
                    self.assertEqual(refresh.read(root / receipt['diff_stdout'])['queries'][0]['new_count'], 1)
                    self.assertEqual(receipt['comparison_evidence_sha256'], hashlib.sha256((root / receipt['comparison_evidence']).read_bytes()).hexdigest())
                    self.assertEqual(sanitized['suppression_reason'], 'Approved query identity drift')
                elif fault != 'valid':
                    self.assertEqual(state['queries'], prior['queries'])
                    self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                    self.assertEqual(receipt['failed_stage'], 'comparison')

    def test_native_item_and_delta_contract_at_runner_boundary(self):
        faults = ('missing_repo', 'wrong_number', 'boolean_comments', 'wrong_labels', 'forged_status', 'rank', 'boolean_rank', 'title', 'url', 'caveat', 'omitted_item', 'count', 'duplicate_native', 'minimal_native')
        for proposal_mode in (False, True):
            for fault in faults:
                with self.subTest(proposal=proposal_mode, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    old_dir, row = self.observation(root, 'old', sid)
                    prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                    refresh.write(root / 'learning-state.json', prior)
                    before = (root / 'searches.json').read_bytes()
                    if proposal_mode:
                        candidate = refresh.read(root / 'searches.json')
                        candidate['searches'][0]['max_items'] += 1
                        refresh.write(root / 'candidate.json', candidate)
                        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            run, fresh = self.observation(root, 'new', sid)
                            item = fresh['issues'][0]
                            if fault == 'missing_repo':
                                del item['repo_name']
                            elif fault in ('wrong_number', 'boolean_comments', 'wrong_labels'):
                                item[{'wrong_number': 'number', 'boolean_comments': 'comments', 'wrong_labels': 'labels'}[fault]] = {'wrong_number': '1', 'boolean_comments': True, 'wrong_labels': [False]}[fault]
                            elif fault == 'duplicate_native':
                                fresh['issues'].append({**item, 'title': 'Last occurrence'})
                                fresh['item_count'] = fresh['total_count'] = 2
                            refresh.write(run / (sid + '.json'), fresh)
                            manifest = self.manifest('new', [fresh], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                            refresh.write(run / 'manifest.json', manifest)
                            refresh.write(root / 'results/manifest.json', manifest)
                            refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                            return 0
                        outcome = self.comparison(root, 'old', 'new', sid)
                        query, item = outcome['queries'][0], outcome['queries'][0]['items'][0]
                        if fault == 'forged_status':
                            item['status'] = 'NEW'
                            query.update(new_count=1, unchanged_count=0)
                        elif fault in ('rank', 'boolean_rank', 'title', 'url', 'caveat'):
                            item[{'rank': 'current_rank', 'boolean_rank': 'previous_rank', 'title': 'title_or_path', 'url': 'url', 'caveat': 'caveat'}[fault]] = {'rank': 3, 'boolean_rank': True, 'title': 'Forged', 'url': 'https://wrong', 'caveat': 'Unsupported'}[fault]
                        elif fault == 'omitted_item':
                            query.update(items=[], unchanged_count=0)
                        elif fault == 'count':
                            query['unchanged_count'] = True
                        refresh.write(output.with_suffix('.json'), outcome)
                        return 0
                    valid = fault in ('duplicate_native', 'minimal_native')
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 0 if valid else 2)
                    state = refresh.read(root / 'learning-state.json')
                    receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                    if not valid:
                        self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                        self.assertEqual(state['queries'], prior['queries'])
                        self.assertEqual((root / 'searches.json').read_bytes(), before)
                        self.assertFalse(receipt['promoted'])
                        self.assertEqual(receipt['failed_stage'], 'result_validation' if fault in faults[:4] else 'comparison')
                        self.assertEqual(receipt['attempt_status'], 'failed')

    def test_native_shape_and_window_semantics_remain_compatible(self):
        cases = [('CODE', 'repo_fallback'), ('CODE', 'path'), ('REPOSITORY', 'optional'), ('TOPIC', 'optional'), ('DISCUSSION', 'optional'), ('PULL_REQUEST', 'optional'), ('ISSUE', 'gone'), ('ISSUE', 'window'), ('ISSUE', 'error_new')]
        for kind, mode in cases:
            with self.subTest(kind=kind, mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                catalog = refresh.read(root / 'searches.json')
                catalog['searches'][0].update(search_type=kind, sort=None, order=None)
                refresh.write(root / 'searches.json', catalog)
                old_dir, row = self.observation(root, 'old', sid)
                refresh.write(root / 'cycles/old-cycle/catalog-used.json', catalog)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                def native(arguments, output, timeout):
                    if arguments[0] == 'github-search':
                        run, fresh = self.observation(root, 'new', sid)
                        active = next(key for key in ('items', 'issues', 'discussions') if fresh[key])
                        item = fresh[active][0]
                        if mode == 'path':
                            item.update(path='file.cpp', score=0, topics=None)
                        elif mode == 'optional':
                            item.update(comments=None, created_at=None) if active != 'items' else item.update(path='', description='', stars=0, topics=['x'])
                        elif mode == 'gone':
                            fresh[active] = []
                            fresh['item_count'] = 0
                        elif mode in ('window', 'error_new'):
                            item.update(number=0, title='')
                            fresh['is_complete'] = mode != 'window'
                            if mode == 'error_new':
                                fresh['error_code'] = 'API_ERROR'
                        refresh.write(run / (sid + '.json'), fresh)
                        manifest = self.manifest('new', [fresh], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                        refresh.write(run / 'manifest.json', manifest)
                        refresh.write(root / 'results/manifest.json', manifest)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        if mode == 'error_new':
                            return 8
                    else:
                        outcome = self.comparison(root, 'old', 'new', sid)
                        refresh.write(output.with_suffix('.json'), outcome)
                    return 0
                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 8 if mode == 'error_new' else (2 if mode in ('gone', 'window') else 0))
                state = refresh.read(root / 'learning-state.json')
                receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                if mode == 'error_new':
                    self.assertEqual(state['queries'], prior['queries'])
                    self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                    self.assertEqual(receipt['failed_stage'], 'search')
                    self.assertNotIn('comparison_evidence', receipt)
                    # Native raw diff mechanics remain valid independently of failed batch admission.
                    outcome = self.comparison(root, 'old', 'new', sid)
                    fresh = refresh.read(root / 'results/runs/test_new' / (sid + '.json'))
                    feedback = refresh.metrics({sid: fresh}, prior['queries'])
                    derived = refresh.comparison(copy.deepcopy(outcome), {sid: row}, {sid: fresh}, 'old', 'new', {}, feedback)
                    self.assertEqual((outcome['queries'][0]['new_count'], outcome['queries'][0]['gone_count']), (1, 0))
                    self.assertEqual(derived['queries'][0]['suppression_reasons'], ['query_error'])
                    self.assertEqual((derived['queries'][0]['new_count'], derived['queries'][0]['gone_count']), (0, 0))
                    continue
                self.assertIn('comparison_evidence', receipt)
                raw_path = root / receipt['diff_stdout']
                self.assertEqual(refresh.digest(raw_path), receipt['diff_stdout_sha256'])
                raw = refresh.read(raw_path)['queries'][0]
                if mode == 'window':
                    self.assertEqual((raw['entered_window_count'], raw['exited_window_count']), (1, 1))
                elif mode == 'error_new':
                    self.assertEqual((raw['new_count'], raw['gone_count']), (1, 0))

    def test_ignored_cross_model_extras_cannot_forge_native_delta(self):
        for kind, active, expected_id, expected_title in [('ISSUE', 'issues', 'o/r#1', 'Issue'), ('DISCUSSION', 'discussions', 'o/r#1', 'Discussion'), ('REPOSITORY', 'items', 'o/r', None)]:
            for proposal_mode in (False, True):
                for forged in (False, True):
                    with self.subTest(kind=kind, proposal=proposal_mode, forged=forged), tempfile.TemporaryDirectory() as directory:
                        root = Path(directory).resolve()
                        sid = self.workflow(root)
                        catalog = refresh.read(root / 'searches.json')
                        catalog['searches'][0].update(search_type=kind, sort=None, order=None)
                        refresh.write(root / 'searches.json', catalog)
                        old_dir, row = self.observation(root, 'old', sid)
                        prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                        refresh.write(root / 'learning-state.json', prior)
                        before = (root / 'searches.json').read_bytes()
                        if proposal_mode:
                            candidate = copy.deepcopy(catalog)
                            candidate['searches'][0]['max_items'] += 1
                            refresh.write(root / 'candidate.json', candidate)
                            refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                        def native(arguments, output, timeout):
                            if arguments[0] == 'github-search':
                                run, fresh = self.observation(root, 'new', sid)
                                fresh[active][0].update({'number': 7, 'title': 'Forged'} if active == 'items' else {'path': 'forged.cpp'})
                                refresh.write(run / (sid + '.json'), fresh)
                                refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                            else:
                                # Literal source-model outcome, independent of the fixture extractor.
                                query = {'search_id': sid, 'search_type': kind, 'query_fingerprint': row['query_fingerprint'], 'baseline_run_id': 'old', 'candidate_run_id': 'new', 'baseline_count': 1, 'candidate_count': 1, 'is_baseline_complete': True, 'is_candidate_complete': True, 'new_count': 0, 'gone_count': 0, 'entered_window_count': 0, 'exited_window_count': 0, 'unchanged_count': 1,
                                         'items': [{'search_id': sid, 'status': 'UNCHANGED', 'item_id': expected_id, 'title_or_path': expected_title, 'url': 'https://github.com/o/r/issues/1', 'previous_rank': 1, 'current_rank': 1, 'caveat': None}]}
                                if forged:
                                    query.update(new_count=1, gone_count=1, unchanged_count=0)
                                    query['items'] = [{'search_id': sid, 'status': 'NEW', 'item_id': 'o/r#7' if active == 'items' else 'o/r:forged.cpp', 'title_or_path': 'Forged' if active == 'items' else 'forged.cpp', 'url': 'https://github.com/o/r/issues/1', 'previous_rank': None, 'current_rank': 1, 'caveat': None}, {'search_id': sid, 'status': 'GONE', 'item_id': expected_id, 'title_or_path': expected_title, 'url': 'https://github.com/o/r/issues/1', 'previous_rank': 1, 'current_rank': None, 'caveat': None}]
                                refresh.write(output.with_suffix('.json'), {'status': 'SUCCESS', 'exit_code': 0, 'error': None, 'baseline_run_id': 'old', 'candidate_run_id': 'new', 'total_queries_compared': 1, 'incompatible_queries': 0, 'queries': [query], 'timing': {}, 'system_info': {}})
                            return 0
                        with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 2 if forged else 0)
                        state = refresh.read(root / 'learning-state.json')
                        receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                        if forged:
                            self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                            self.assertEqual(state['queries'], prior['queries'])
                            self.assertEqual((root / 'searches.json').read_bytes(), before)
                            self.assertEqual(receipt['failed_stage'], 'comparison')
                            self.assertFalse(receipt['promoted'])
                        else:
                            self.assertEqual(state['last_run_id'], 'new')
                            self.assertEqual(receipt['promoted'], proposal_mode)
                            raw = refresh.read(root / receipt['diff_stdout'])
                            self.assertEqual(raw['queries'][0]['items'][0]['status'], 'UNCHANGED')

    def test_coverage_warning_suppresses_claims_and_preserves_baseline(self):
        for mode in ('error', 'capped', 'capped_complete', 'capped_forged_title', 'incomplete', 'empty', 'comparison_failure'):
            for proposal_mode in (False, True):
                with self.subTest(mode=mode, proposal=proposal_mode), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    old_dir, row = self.observation(root, 'old', sid)
                    prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                    refresh.write(root / 'learning-state.json', prior)
                    before = (root / 'searches.json').read_bytes()
                    if proposal_mode:
                        candidate = refresh.read(root / 'searches.json')
                        candidate['searches'][0]['max_items'] += 1
                        refresh.write(root / 'candidate.json', candidate)
                        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            run, fresh = self.observation(root, 'new', sid)
                            if mode in ('empty', 'comparison_failure'):
                                fresh.update(issues=[], item_count=0, total_count=0)
                            else:
                                fresh['issues'][0]['number'] = 2
                                fresh['error_code'] = 'API_ERROR' if mode == 'error' else 'NONE'
                                fresh['is_complete'] = mode not in ('capped', 'capped_forged_title', 'incomplete')
                                if mode in ('capped', 'capped_complete', 'capped_forged_title'):
                                    fresh['total_count'] = 2
                            refresh.write(run / (sid + '.json'), fresh)
                            manifest = self.manifest('new', [fresh], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                            refresh.write(run / 'manifest.json', manifest)
                            refresh.write(root / 'results/manifest.json', manifest)
                            refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                            return 8 if mode == 'error' else 0
                        outcome = self.comparison(root, 'old', 'new', sid)
                        if mode == 'capped_forged_title':
                            outcome['queries'][0]['items'][0]['title_or_path'] = 'Forged title'
                        refresh.write(output.with_suffix('.json'), outcome)
                        return 124 if mode == 'comparison_failure' else 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 8 if mode == 'error' else 2)
                    state = refresh.read(root / 'learning-state.json')
                    receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                    self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                    self.assertEqual(state['last_run_id'], 'old')
                    self.assertEqual((root / 'searches.json').read_bytes(), before)
                    self.assertFalse(receipt['promoted'])
                    if mode in ('error', 'comparison_failure', 'capped_forged_title') or proposal_mode:
                        self.assertEqual(state['queries'], prior['queries'])
                        self.assertEqual(receipt['attempt_status'], 'failed')
                    else:
                        self.assertEqual(receipt['attempt_status'], 'accepted_with_coverage_warning')
                        self.assertNotEqual(state['queries'], prior['queries'])
                    if mode in ('error', 'comparison_failure', 'capped_forged_title'):
                        self.assertEqual(receipt['failed_stage'], 'search' if mode == 'error' else 'comparison')
                        self.assertNotIn('comparison_evidence', receipt)
                    else:
                        raw = refresh.read(root / receipt['diff_stdout'])['queries'][0]
                        derived = refresh.read(root / receipt['comparison_evidence'])['queries'][0]
                        self.assertFalse(derived['content_claims_eligible'])
                        self.assertEqual((derived['new_count'], derived['gone_count']), (0, 0))
                        expected = {'error': ['query_error'], 'capped': ['incomplete_coverage', 'collection_capped'], 'capped_complete': ['collection_capped'], 'incomplete': ['incomplete_coverage'], 'empty': ['unverified_empty']}[mode]
                        self.assertEqual(derived['suppression_reasons'], expected)
                        self.assertEqual(raw['new_count'], 1 if mode in ('error', 'capped_complete') else 0)
                        self.assertEqual(derived['suppressed_counts'], {'new_count': raw['new_count'], 'gone_count': raw['gone_count']})
                        self.assertEqual(receipt['comparison_state'], 'suppressed')
                        if mode in ('capped', 'incomplete'):
                            self.assertEqual((derived['entered_window_count'], derived['exited_window_count']), (1, 1))
                        self.assertEqual(refresh.digest(root / receipt['diff_stdout']), receipt['diff_stdout_sha256'])

    def test_empty_coverage_recovers_against_old_baseline_or_initializes_without_one(self):
        for first_run in (False, True):
            for corrupt_marker in ('missing_receipt', 'missing_commit', 'missing_event', 'marker_root', 'digest', 'legacy_field', 'wrong_status', False) if first_run else (False,):
                with self.subTest(first=first_run, corrupt=corrupt_marker), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    if not first_run:
                        run, row = self.observation(root, 'old', sid)
                        refresh.write(root / 'learning-state.json', {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(run / 'manifest.json')}})
                    stage, compared = ['empty'], []
                    def native(arguments, output, timeout):
                        if arguments[0] == 'github-search':
                            run, fresh = self.observation(root, stage[0], sid)
                            if stage[0].startswith('empty'):
                                fresh.update(issues=[], item_count=0, total_count=0)
                                refresh.write(run / (sid + '.json'), fresh)
                                manifest = self.manifest(stage[0], [fresh], [str((run / (sid + '.json')).relative_to(root / 'results'))])
                                refresh.write(run / 'manifest.json', manifest)
                                refresh.write(root / 'results/manifest.json', manifest)
                            refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        else:
                            compared.append(Path(arguments[2]).name)
                            refresh.write(output.with_suffix('.json'), self.comparison(root, 'old', stage[0], sid))
                        return 0
                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                        warning = refresh.read(root / 'learning-state.json')
                        self.assertEqual(warning['queries'][sid]['empty_streak'], 1)
                        self.assertTrue(warning['queries'][sid]['unverified_empty'])
                        if first_run:
                            self.assertNotIn('accepted_baseline', warning)
                            marker = warning['pending_baseline_initialization']
                            path = root / warning['coverage_commit']['receipt']
                            if corrupt_marker == 'missing_receipt':
                                path.unlink()
                            elif corrupt_marker == 'wrong_status':
                                damaged = refresh.read(path)
                                damaged['attempt_status'] = 'accepted'
                                refresh.write(path, damaged)
                            elif corrupt_marker:
                                if corrupt_marker == 'missing_commit':
                                    warning.pop('coverage_commit')
                                elif corrupt_marker == 'missing_event':
                                    (root / 'learning-events.jsonl').unlink()
                                elif corrupt_marker == 'marker_root':
                                    warning['pending_baseline_initialization'] = []
                                elif corrupt_marker == 'digest':
                                    marker['manifest_sha256'] = '0' * 64
                                else:
                                    warning['last_run_id'] = None
                                refresh.write(root / 'learning-state.json', warning)
                        else:
                            self.assertEqual(warning['last_run_id'], 'old')
                            self.assertIs(warning['baseline_legacy'], True)
                            self.assertNotIn('baseline_commit', warning)
                        if first_run and not corrupt_marker:
                            for count in (2, 3):
                                stage[0] = 'empty' + str(count)
                                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                                repeated = refresh.read(root / 'learning-state.json')
                                self.assertEqual(repeated['queries'][sid]['empty_streak'], count)
                                self.assertNotIn('accepted_baseline', repeated)
                                self.assertEqual(repeated['pending_baseline_initialization']['run_id'], stage[0])
                            self.assertEqual(compared, [])
                        stage[0] = 'healthy'
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2 if corrupt_marker else 0)
                    recovered = refresh.read(root / 'learning-state.json')
                    if corrupt_marker:
                        self.assertNotIn('accepted_baseline', recovered)
                        self.assertEqual(recovered['queries'], warning['queries'])
                        receipt = refresh.read(root / 'cycles' / recovered['last_failed_cycle'] / 'receipt.json')
                        self.assertEqual(receipt['failed_stage'], 'baseline_resolution')
                    else:
                        self.assertEqual(recovered['last_run_id'], 'healthy')
                        self.assertNotIn('baseline_legacy', recovered)
                        self.assertEqual(recovered['baseline_commit']['outcome'], 'accepted')
                        self.assertTrue(recovered['queries'][sid]['recovered_from_empty'])
                        self.assertNotIn('pending_baseline_initialization', recovered)
                        self.assertEqual(compared, [] if first_run else ['test_old', 'test_old'])

    def test_mixed_query_claims_are_suppressed_individually(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            healthy = self.workflow(root)
            catalog = refresh.read(root / 'searches.json')
            catalog['searches'].append({**catalog['searches'][0], 'id': 'unsafe', 'query': 'another query'})
            refresh.write(root / 'searches.json', catalog)
            def publish(run_id, unsafe=False):
                run, row = self.observation(root, run_id, healthy)
                other = self.fixture_row(catalog['searches'][1])
                if unsafe:
                    other['issues'][0]['number'] = 2
                    other['total_count'] = 2  # Native complete flag contradicts collection ceiling.
                rows = [row, other]
                for value in rows:
                    refresh.write(run / (value['search_id'] + '.json'), value)
                manifest = self.manifest(run_id, rows, [str((run / (r['search_id'] + '.json')).relative_to(root / 'results')) for r in rows])
                refresh.write(run / 'manifest.json', manifest)
                refresh.write(root / 'results/manifest.json', manifest)
                return run, rows
            old, rows = publish('old')
            prior = {'queries': refresh.metrics({r['search_id']: r for r in rows}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old / 'manifest.json')}}
            refresh.write(root / 'learning-state.json', prior)
            raw_bytes = []
            def native(arguments, output, timeout):
                if arguments[0] == 'github-search':
                    _, fresh = publish('new', True)
                    refresh.write(output.with_suffix('.json'), self.envelope(fresh))
                else:
                    outcome = self.comparison(root, 'old', 'new', healthy)
                    outcome['queries'].extend(self.comparison(root, 'old', 'new', 'unsafe')['queries'])
                    outcome['total_queries_compared'] = 2
                    refresh.write(output.with_suffix('.json'), outcome)
                    raw_bytes.append(output.with_suffix('.json').read_bytes())
                return 0
            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
            state = refresh.read(root / 'learning-state.json')
            receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
            derived = refresh.read(root / receipt['comparison_evidence'])
            queries = {q['search_id']: q for q in derived['queries']}
            self.assertTrue(queries[healthy]['content_claims_eligible'])
            self.assertEqual(queries[healthy]['unchanged_count'], 1)
            self.assertEqual(queries['unsafe']['suppression_reasons'], ['collection_capped'])
            self.assertEqual(queries['unsafe']['suppressed_counts'], {'new_count': 1, 'gone_count': 1})
            self.assertEqual((queries['unsafe']['new_count'], queries['unsafe']['gone_count']), (0, 0))
            self.assertEqual((root / receipt['diff_stdout']).read_bytes(), raw_bytes[0])
            self.assertEqual(refresh.digest(root / receipt['comparison_evidence']), receipt['comparison_evidence_sha256'])
            self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
            self.assertFalse(state['queries']['unsafe']['complete'])

    def test_linked_evidence_and_boolean_diff_exit_cannot_advance_acceptance(self):
        for fault in ('runs_ancestor', 'manifest_link', 'boolean_exit', 'boolean_total', 'boolean_incompatible'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve() / 'workflow'
                sid = self.workflow(root)
                old_dir, row = self.observation(root, 'old', sid)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                if fault == 'runs_ancestor':
                    outside = root.parent / 'external-runs'
                    (root / 'results/runs').rename(outside)
                    (root / 'results/runs').symlink_to(outside, target_is_directory=True)

                def native(arguments, output, timeout):
                    if arguments[0] == 'github-search':
                        run, fresh = self.observation(root, 'new', sid)
                        if fault == 'manifest_link':
                            outside = root.parent / 'external-manifest.json'
                            (run / 'manifest.json').rename(outside)
                            (run / 'manifest.json').symlink_to(outside)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                        return 0
                    outcome = self.comparison(root, 'old', 'new', sid)
                    if fault.startswith('boolean_'):
                        key = {'boolean_exit': 'exit_code', 'boolean_total': 'total_queries_compared', 'boolean_incompatible': 'incompatible_queries'}[fault]
                        outcome[key] = False if fault != 'boolean_total' else True
                    refresh.write(output.with_suffix('.json'), outcome)
                    return 0

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=native) as command, contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                    if fault == 'runs_ancestor':
                        command.assert_not_called()
                state = refresh.read(root / 'learning-state.json')
                self.assertEqual(state['queries'], prior['queries'])
                self.assertEqual(state['accepted_baseline'], prior['accepted_baseline'])
                receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                self.assertEqual(receipt['attempt_status'], 'failed')
                self.assertEqual(receipt['failed_stage'], 'output_admission' if fault == 'runs_ancestor' else ('result_validation' if fault == 'manifest_link' else 'comparison'))

    def test_selected_catalog_binds_matching_stdout_and_artifacts(self):
        cases = [
            ({'search_type': 'ISSUE', 'query': '  café  '}, '61d40b0714148e46aebff33fb53c8b5d4f765686980a38c792f3fe64dd893e2f', 'café is:issue'),
            ({'search_type': 'PULL_REQUEST', 'query': ' topic:cpp ', 'target_repo': 'Owner/Repo', 'languages': ['Rust', 'C++'], 'filenames': ['z.hpp', 'a.hpp'], 'topics': ['é', 'cpp'], 'min_stars': 3, 'sort': 'updated', 'order': 'asc'}, '9cf0ee38342bf020e1b00990592ea93f158c1ef9eea30dfbe01a95e67d95cd87', 'topic:cpp repo:Owner/Repo language:Rust language:C++ filename:z.hpp filename:a.hpp topic:é topic:cpp stars:>=3 is:pr'),
            ({'search_type': 'CODE', 'query': 'struct X', 'sort': 'indexed'}, 'de87bb5495ebb00f6c90a6db0d4886de1df53bb9f9894d07fff88e2bbd040348', 'struct X'),
            ({'search_type': 'ISSUE', 'query': '  café  ', 'languages': None, 'filenames': [], 'topics': None, 'min_stars': None, 'sort': None, 'order': None, 'target_repo': None, 'max_pages': 2, 'max_items': 5, 'deep': False, 'description': 'Excluded from fingerprint'}, '61d40b0714148e46aebff33fb53c8b5d4f765686980a38c792f3fe64dd893e2f', 'café is:issue'),
            ({'search_type': 'PULL_REQUEST', 'query': ' topic:cpp ', 'target_repo': 'Owner/Repo', 'languages': ['C++', 'Rust'], 'filenames': ['a.hpp', 'z.hpp'], 'topics': ['cpp', 'é'], 'min_stars': 3, 'sort': 'updated', 'order': 'asc'}, '9cf0ee38342bf020e1b00990592ea93f158c1ef9eea30dfbe01a95e67d95cd87', 'topic:cpp repo:Owner/Repo language:C++ language:Rust filename:a.hpp filename:z.hpp topic:cpp topic:é stars:>=3 is:pr'),
            ({'search_type': 'TOPIC', 'query': '  café  ', 'sort': 'stars'}, 'fee2a3568cd70a3a598dc3272887849e7539cb7319906003009f984b31123554', 'café'),
            ({'search_type': 'REPOSITORY', 'query': '  café  ', 'sort': 'stars'}, 'd823db7a667058b798d14bf0a4dc820a96ca7b06c457676cd04a3b0cd99ca0b2', 'café'),
            ({'search_type': 'DISCUSSION', 'query': '  café  ', 'sort': 'IGNORED', 'order': 'ASC'}, '3ee39f4bab02bfaf201a8e3f2677adf6f7e6d607ce863bf21e36c430c8aaa38c', 'café'),
        ]
        for definition, fingerprint, query in cases:
            for fault in ('fingerprint', 'query', 'valid'):
                with self.subTest(definition=definition, fault=fault), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory).resolve()
                    sid = self.workflow(root)
                    refresh.write(root / 'searches.json', {'searches': [{'id': sid, 'description': 'Native contract fixture', **definition}]})
                    before = (root / 'searches.json').read_bytes()

                    def native(arguments, output, timeout):
                        run, row = self.observation(root, 'first', sid)
                        row.update({'query_fingerprint': 'f' * 64 if fault == 'fingerprint' else fingerprint, 'query_executed': 'contradictory query' if fault == 'query' else query})
                        refresh.write(run / (sid + '.json'), row)
                        refresh.write(output.with_suffix('.json'), self.envelope([row]))
                        return 0

                    with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0 if fault == 'valid' else 2)
                    state = refresh.read(root / 'learning-state.json')
                    receipt = refresh.read(root / 'cycles' / state['last_attempt_cycle'] / 'receipt.json')
                    self.assertEqual((root / 'searches.json').read_bytes(), before)
                    if fault != 'valid':
                        self.assertNotIn('accepted_baseline', state)
                        self.assertEqual(receipt['failed_stage'], 'result_validation')
                    elif definition['search_type'] == 'DISCUSSION':
                        self.assertEqual(receipt['catalog_binding']['transport_ignored_fields'], {sid: ['sort', 'order']})

    def test_invalid_catalog_shapes_and_fallback_options_stop_before_launch(self):
        faults = [{'unknown': True}, {'sort': 'UPDATED'}, {'order': 'ASC'}, {'languages': 'C++'}, {'topics': [7]}, {'min_stars': True}, {'max_pages': True}, {'max_items': False}, {'deep': 'false'}, {'search_type': 'OTHER'}]
        for override in faults:
            with self.subTest(override=override), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                self.workflow(root)
                catalog = refresh.read(root / 'searches.json')
                catalog['searches'][0].update(override)
                refresh.write(root / 'searches.json', catalog)
                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'configure'), patch.object(refresh, 'command') as command, patch('sys.argv', ['refresh.py', '--state-dir', str(root), '--runtime-config', '/synthetic/runtime.json']), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.main(), 2)
                    command.assert_not_called()
                self.assertFalse((root / 'learning-state.json').exists())

    def test_missing_historical_catalog_blocks_refresh_and_proposal_claims(self):
        for proposal_run in (False, True):
            with self.subTest(proposal=proposal_run), tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                sid = self.workflow(root)
                old_dir, row = self.observation(root, 'old', sid)
                row['issues'] = [{**row['issues'][0], 'number': 0, 'html_url': 'https://github.com/o/r/issues/0'}]
                refresh.write(old_dir / (sid + '.json'), row)
                prior = {'queries': refresh.metrics({sid: row}, {}), 'last_run_id': 'old', 'last_cycle': 'old-cycle', 'accepted_baseline': {'run_id': 'old', 'manifest_sha256': refresh.digest(old_dir / 'manifest.json')}}
                refresh.write(root / 'learning-state.json', prior)
                catalog = root / 'cycles/old-cycle/catalog-used.json'
                if catalog.exists():
                    catalog.unlink()
                proposal = None
                before = (root / 'searches.json').read_bytes()
                if proposal_run:
                    candidate = refresh.read(root / 'searches.json')
                    candidate['searches'][0]['max_items'] += 1
                    refresh.write(root / 'candidate.json', candidate)
                    proposal = 'proposal.json'
                    refresh.write(root / proposal, {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {sid: self.proposal['changes']['test']}})
                native_stages = []

                def native(arguments, output, timeout):
                    native_stages.append(arguments[0])
                    if arguments[0] == 'github-search':
                        _, fresh = self.observation(root, 'new', sid)
                        refresh.write(output.with_suffix('.json'), self.envelope([fresh]))
                    else:
                        outcome = self.comparison(root, 'old', 'new', sid)
                        outcome['queries'][0].update({'new_count': 1, 'unchanged_count': 0})
                        outcome['queries'][0]['items'][0]['status'] = 'NEW'
                        refresh.write(output.with_suffix('.json'), outcome)
                    return 0

                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', native), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=proposal)), 2)
                state = refresh.read(root / 'learning-state.json')
                for field in ('queries', 'last_run_id', 'last_cycle', 'accepted_baseline'):
                    self.assertEqual(state[field], prior[field])
                receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                self.assertEqual(receipt['failed_stage'], 'baseline_resolution')
                self.assertFalse(receipt['promoted'])
                self.assertFalse(receipt['fresh_snapshot_accepted'])
                self.assertNotIn('comparison_evidence', receipt)
                self.assertEqual(native_stages, ['github-search'])
                self.assertEqual((root / 'searches.json').read_bytes(), before)
                self.assertFalse(catalog.exists())

    def test_relevance_anchor_required(self):
        self.assertEqual(refresh.evaluate(self.proposal, {'test': self.row}), [])
        self.assertTrue(refresh.evaluate(self.proposal, {'test': {**self.row, 'issues': []}}))

    def test_capped_result_cannot_pass_complete_expectation(self):
        self.assertTrue(refresh.evaluate(self.proposal, {'test': {**self.row, 'is_complete': False}}))

    def test_budget_and_path_escape(self):
        with self.assertRaises(ValueError):
            refresh.confined('../escape.json')
        with self.assertRaises(ValueError):
            refresh.check_catalog(self.catalog, {**self.policy, 'max_code_pages_per_run': 1})

    def test_removal_and_missing_evidence_rejected(self):
        old = refresh.check_catalog(self.catalog, self.policy)
        with self.assertRaises(ValueError):
            refresh.check_proposal(self.proposal, old, {}, self.policy)
        with self.assertRaises(ValueError):
            refresh.check_proposal({'changes': {}}, old, {**old, 'new': {'id': 'new'}}, self.policy)

    def test_cooldown_blocks_network_before_start(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            refresh.write(root / 'policy.json', self.policy)
            refresh.write(root / 'learning-state.json', {'next_allowed_at': refresh.time.time() + 300})
            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as command:
                with self.assertRaisesRegex(ValueError, 'Cooldown'):
                    refresh.run(argparse.Namespace(proposal=None))
                command.assert_not_called()

    def test_concurrent_runner_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with (root / '.refresh.lock').open('a') as held:
                fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
                with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'configure'), patch.object(refresh, 'run') as run, patch('sys.argv', ['refresh.py', '--state-dir', str(root), '--runtime-config', '/synthetic/runtime.json']), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(refresh.main(), 2)
                    run.assert_not_called()

    def test_launch_failure_preserves_last_snapshot_and_exit(self):
        self.check_failed_native_attempt(1, '')
        self.check_failed_native_attempt(1, '', available=False)

    def test_success_with_invalid_stdout_is_not_empty_success(self):
        self.check_failed_native_attempt(0, '')

    def check_failed_native_attempt(self, native_exit, stdout, available=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            refresh.write(root / 'policy.json', self.policy)
            refresh.write(root / 'searches.json', self.catalog)
            queries = refresh.metrics({'test': self.row}, {})
            refresh.write(root / 'learning-state.json', {'queries': queries, 'last_run_id': 'old', 'last_cycle': 'old-cycle'})
            refresh.write(root / 'results/manifest.json', {'run_id': 'old'})
            before = (root / 'searches.json').read_bytes()

            def fake_command(arguments, output, timeout):
                if available:
                    output.with_suffix('.json').write_text(stdout)
                    output.with_suffix('.stderr').write_text('simulated native launch failure')
                return native_exit

            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', side_effect=fake_command) as command, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), native_exit or 2)
            self.assertEqual(command.call_count, 1)
            state = refresh.read(root / 'learning-state.json')
            self.assertEqual(state['queries'], queries)
            self.assertEqual(state['last_run_id'], 'old')
            self.assertEqual(state['last_cycle'], 'old-cycle')
            event = self.event_receipt(root)
            self.assertEqual(event['native_exit_code'], native_exit)
            self.assertFalse(event['promoted'])
            self.assertFalse(event['fresh_snapshot_accepted'])
            self.assertEqual(state['last_failed_cycle'], event['cycle'])
            for label in ('stdout', 'stderr'):
                self.assertEqual(event[label + '_available'], available)
                self.assertEqual(event[label + '_sha256'], refresh.digest(root / event[label]) if available else None)
            self.assertEqual(refresh.read(root / 'results/manifest.json')['run_id'], 'old')
            self.assertEqual((root / 'searches.json').read_bytes(), before)

    def test_stale_proposal_is_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            refresh.write(root / 'policy.json', self.policy)
            refresh.write(root / 'searches.json', self.catalog)
            refresh.write(root / 'candidate.json', self.catalog)
            refresh.write(root / 'proposal.json', {'catalog': 'candidate.json', 'base_catalog_sha256': 'wrong'})
            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command') as command:
                with self.assertRaisesRegex(ValueError, 'Stale proposal'):
                    refresh.run(argparse.Namespace(proposal='proposal.json'))
                command.assert_not_called()

    def test_failed_experiment_preserves_catalog_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            refresh.write(root / 'policy.json', self.policy)
            refresh.write(root / 'searches.json', self.catalog)
            before = (root / 'searches.json').read_bytes()
            candidate = copy.deepcopy(self.catalog)
            candidate['searches'][0]['query'] += ' in:title'
            changed_id = candidate['searches'][0]['id']
            change = copy.deepcopy(self.proposal['changes']['test'])
            proposal = {'catalog': 'candidate.json', 'base_catalog_sha256': refresh.digest(root / 'searches.json'), 'changes': {changed_id: change}}
            refresh.write(root / 'candidate.json', candidate)
            refresh.write(root / 'proposal.json', proposal)

            def fake_command(arguments, output, timeout):
                run_dir = root / 'results' / 'runs' / 'test_run'
                rows = [{**self.fixture_row(s), 'issues': [], 'item_count': 0} for s in candidate['searches']]
                artifacts = []
                for row in rows:
                    file = run_dir / (row['search_id'] + '.json')
                    refresh.write(file, row)
                    artifacts.append(str(file.relative_to(root / 'results')))
                manifest = self.manifest('run', rows, artifacts)
                refresh.write(root / 'results' / 'manifest.json', manifest)
                refresh.write(run_dir / 'manifest.json', manifest)
                refresh.write(output.with_suffix('.json'), self.envelope(rows))
                return 0

            with patch.object(refresh, 'ROOT', root), patch.object(refresh, 'command', fake_command), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json')), 2)
            self.assertEqual((root / 'searches.json').read_bytes(), before)
            self.assertFalse(self.event_receipt(root)['promoted'])


if __name__ == '__main__':
    unittest.main()
