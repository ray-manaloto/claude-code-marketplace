"""Real runner and binding guards; actual synthetic imports, provider stubs only."""
import shutil
import copy
import hashlib
from pathlib import Path
import argparse
import json
import unittest
from unittest.mock import patch
import refresh
import test_runtime_runner as runner


class RuntimeStageTests(unittest.TestCase):
    setUp = runner.RunnerPreflightTests.setUp
    scenario = runner.RunnerPreflightTests.scenario
    admission_context = runner.RunnerPreflightTests.admission_context
    propose = runner.RunnerPreflightTests.propose

    def seed(self, proposal_mode):
        root, sid, attempt, native = self.scenario(proposal_mode)
        stack, command, imports = self.admission_context(root, native, 100)
        with stack: self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
        old = refresh.read(root / 'learning-state.json')
        catalog = (root / 'searches.json').read_bytes()
        if proposal_mode: self.propose(root, sid)
        attempt[:] = ['rejected', 0]
        return root, sid, attempt, native, old, catalog

    def test_drift_at_each_native_stage_boundary(self):
        for proposal_mode in (False, True):
            for location in ('search_before', 'search_after', 'diff_before', 'diff_after'):
                with self.subTest(proposal=proposal_mode, location=location):
                    original = self.f.uv.read_bytes()
                    root, sid, attempt, native, old, catalog = self.seed(proposal_mode)
                    preflight, baseline = refresh.runner_preflight, refresh.accepted_baseline
                    def drift(): self.f.uv.write_bytes(original + b'\nsynthetic drift')
                    def check(policy, cycle):
                        result = preflight(policy, cycle)
                        if location == 'search_before': drift()
                        return result
                    def resolve(*args):
                        result = baseline(*args)
                        if location == 'diff_before': drift()
                        return result
                    def provider(arguments, output, timeout):
                        result = native(arguments, output, timeout)
                        if (arguments[0] == 'github-search' and location == 'search_after'
                                or arguments[0] == 'github:diff' and location == 'diff_after'): drift()
                        return result
                    stack, command, imports = self.admission_context(root, provider, 200)
                    with stack, patch.object(refresh, 'runner_preflight', side_effect=check), \
                            patch.object(refresh, 'accepted_baseline', side_effect=resolve):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 2)
                        imports.assert_called_once()
                        self.assertEqual(command.call_count, 0 if location == 'search_before' else (2 if location == 'diff_after' else 1))
                        state = refresh.read(root / 'learning-state.json')
                        receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                        for field in ('queries', 'accepted_baseline', 'baseline_commit', 'coverage_commit', 'last_run_id'):
                            self.assertEqual(state[field], old[field], field)
                        self.assertEqual((root / 'searches.json').read_bytes(), catalog)
                        self.assertEqual(state['next_allowed_at'], old['next_allowed_at'] if location == 'search_before' else 265)
                        self.assertEqual(receipt['failed_stage'], 'runtime_binding')
                        self.assertEqual(receipt['comparison_state'], 'unresolved')
                        self.assertIs(receipt['provider_invoked'], location != 'search_before')
                        self.assertEqual(receipt['native_exit_code'], None if location == 'search_before' else 0)
                        self.assertEqual(receipt.get('diff_exit_code'), 0 if location == 'diff_after' else None)
                        marker = receipt['runtime_bindings'][location]
                        evidence = refresh.read(root / marker['receipt'])
                        self.assertEqual(refresh.digest(root / marker['receipt']), marker['receipt_sha256'])
                        self.assertEqual(evidence['outcome'], 'runtime_unavailable')
                        self.assertEqual(evidence['stage'] + '_' + evidence['phase'], location)
                        self.assertNotEqual(evidence['snapshot_sha256'], evidence['expected_sha256'])
                        self.assertEqual(evidence['native_exit_code'], 0 if location.endswith('after') else None)
                        refresh.verify_state_commitments(state)
                        if location == 'search_before':
                            path = root / marker['receipt']
                            bound_bytes = path.read_bytes()
                            path.write_bytes(b'[]')
                            with self.assertRaisesRegex(ValueError, 'binding receipt digest mismatch'):
                                refresh.verify_state_commitments(state)
                            path.write_bytes(bound_bytes)
                    self.f.uv.write_bytes(original)
                    attempt[:] = ['next', 0]
                    stack, command, imports = self.admission_context(root, native, 300)
                    with stack:
                        self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 0)
                        self.assertEqual(command.call_count, 2)
                        good = refresh.read(root / 'learning-state.json')
                        refresh.verify_state_commitments(good)
                        accepted = refresh.read(root / 'cycles' / good['last_cycle'] / 'receipt.json')
                        self.assertEqual(set(accepted['runtime_bindings']), {'search_before', 'search_after', 'diff_before', 'diff_after'})
                        for key, marker in accepted['runtime_bindings'].items():
                            evidence = refresh.read(root / marker['receipt'])
                            self.assertEqual(evidence['outcome'], 'runtime_ready')
                            self.assertEqual(evidence['snapshot_sha256'], evidence['expected_sha256'])
                            self.assertEqual(evidence['native_exit_code'], 0 if key.endswith('after') else None)
                        self.assertEqual(refresh.read(root / accepted['comparison_evidence'])['baseline_run_id'], old['last_run_id'])

    def test_known_native_failure_retains_actual_exit(self):
        for proposal_mode, task, expected in ((p, t, rc) for p in (False, True)
                                              for t, rc in (('github-search', 17), ('github:diff', 19))):
            with self.subTest(task=task, proposal=proposal_mode):
                root, sid, attempt, native, old, catalog = self.seed(proposal_mode)
                def provider(arguments, output, timeout):
                    code = native(arguments, output, timeout)
                    return expected if arguments[0] == task else code
                stack, command, imports = self.admission_context(root, provider, 200)
                with stack:
                    self.assertEqual(refresh.run(argparse.Namespace(proposal="proposal.json" if proposal_mode else None)), 17 if task == 'github-search' else 2)
                    state = refresh.read(root / 'learning-state.json')
                    receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                    self.assertEqual(state['next_allowed_at'], 265)
                    self.assertEqual(state['accepted_baseline'], old['accepted_baseline'])
                    field = 'native_exit_code' if task == 'github-search' else 'diff_exit_code'
                    self.assertEqual(receipt[field], expected)
                    marker = receipt['runtime_bindings'][('search' if task == 'github-search' else 'diff') + '_after']
                    self.assertEqual(refresh.read(root / marker['receipt'])['native_exit_code'], expected)
                    refresh.verify_state_commitments(state)

    def test_post_invocation_unknown_exit_cannot_accept(self):
        for proposal_mode, task in ((p, t) for p in (False, True) for t in ('github-search', 'github:diff')):
            with self.subTest(task=task, proposal=proposal_mode):
                root, sid, attempt, native, old, catalog = self.seed(proposal_mode)
                def provider(arguments, output, timeout):
                    code = native(arguments, output, timeout)
                    return None if arguments[0] == task else code
                stack, command, imports = self.admission_context(root, provider, 200)
                with stack:
                    self.assertEqual(refresh.run(argparse.Namespace(proposal="proposal.json" if proposal_mode else None)), 2)
                    state = refresh.read(root / 'learning-state.json')
                    self.assertEqual(state['accepted_baseline'], old['accepted_baseline'])
                    receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                    self.assertEqual(receipt['native_exit_code'], None if task == 'github-search' else 0)
                    self.assertIs(receipt['provider_invoked'], True)
                    self.assertFalse(receipt['fresh_snapshot_accepted'])
                    marker = receipt['runtime_bindings'][('search' if task == 'github-search' else 'diff') + '_after']
                    evidence = refresh.read(root / marker['receipt'])
                    self.assertIsNone(evidence['native_exit_code'])
                    self.assertIs(evidence['command_completed'], False)
                    calls = command.call_count
                    with patch.object(refresh.time, 'time', return_value=300):
                        self.assertEqual(refresh.run(argparse.Namespace(proposal="proposal.json" if proposal_mode else None)), 2)
                    self.assertEqual(command.call_count, calls)

    def test_cross_attempt_guard_borrowing_refused_and_own_proof_restored(self):
        for proposal in (False, True):
            with self.subTest(proposal=proposal):
                root, sid, attempt, native, old, catalog = self.seed(proposal)
                args = argparse.Namespace(proposal='proposal.json' if proposal else None)
                original, preflight = self.f.uv.read_bytes(), refresh.runner_preflight
                def drift(policy, cycle):
                    result = preflight(policy, cycle)
                    self.f.uv.write_bytes(original + b'\nsynthetic drift')
                    return result
                stack, command, imports = self.admission_context(root, native, 200)
                with stack, patch.object(refresh, 'runner_preflight', side_effect=drift):
                    self.assertEqual(refresh.run(args), 2)
                    command.assert_not_called()
                state_path, events = root / 'learning-state.json', root / 'learning-events.jsonl'
                saved_state, saved_events = state_path.read_bytes(), events.read_bytes()
                saved_cycles = set((root / 'cycles').iterdir())
                own = refresh.read(state_path)
                own_intent = refresh.read(root / own['terminal_commit']['receipt'])
                self.f.uv.write_bytes(original)
                def unknown(arguments, output, timeout):
                    native(arguments, output, timeout)
                    return None
                stack, command, imports = self.admission_context(root, unknown, 300)
                with stack:
                    self.assertEqual(refresh.run(args), 2)
                    command.assert_called_once()
                state = refresh.read(state_path)
                path = root / state['terminal_commit']['receipt']
                intent = refresh.read(path)
                self.assertIsNone(intent['native_exit_code'])
                self.assertIs(intent['provider_invoked'], True)
                intent.update(provider_invoked=False, failed_stage='runtime_binding')
                intent['runtime_bindings']['search_before'] = copy.deepcopy(own_intent['runtime_bindings']['search_before'])
                refresh.write(path, intent)
                records = [json.loads(line) for line in events.read_bytes().splitlines()]
                for record in records:
                    if record['cycle'] == intent['cycle']:
                        record['receipt_sha256'] = refresh.digest(path)
                        state['terminal_commit'].update(receipt_sha256=record['receipt_sha256'],
                            event_sha256=hashlib.sha256(refresh.canonical_bytes(record)).hexdigest())
                events.write_bytes(b''.join(refresh.canonical_bytes(record) for record in records))
                refresh.write(state_path, state)
                stack, command, imports = self.admission_context(root, native, 400)
                with stack:
                    with self.assertRaisesRegex(ValueError, 'binding.*cycle'):
                        refresh.verify_state_commitments(state)
                    self.assertEqual(refresh.run(args), 2)
                    command.assert_not_called()
                # Restore the complete synthetic attempt journal, including RF1 cycle inventory.
                for extra_cycle in set((root / 'cycles').iterdir()) - saved_cycles:
                    shutil.rmtree(extra_cycle)
                state_path.write_bytes(saved_state)
                events.write_bytes(saved_events)
                attempt[:] = ['next', 0]
                stack, command, imports = self.admission_context(root, native, 500)
                with stack:
                    refresh.verify_state_commitments(own)
                    guard_path = root / own_intent['runtime_bindings']['search_before']['receipt']
                    preflight_path = root / own_intent['runtime_preflight']['receipt']
                    guard_bytes, preflight_bytes = guard_path.read_bytes(), preflight_path.read_bytes()
                    for malformed in ('container', 'binding', 'expected_digest', 'stale_reference', 'guard_cycle'):
                        probe, guard = copy.deepcopy(own_intent), json.loads(guard_bytes)
                        admitted = json.loads(preflight_bytes)
                        if malformed == 'container': admitted = []
                        if malformed == 'binding': admitted['native_binding_after'] = {'wrong': True}
                        refresh.write(preflight_path, admitted)
                        probe['runtime_preflight']['receipt_sha256'] = refresh.digest(preflight_path)
                        guard['runtime_preflight'] = {key: probe['runtime_preflight'][key] for key in ('receipt', 'receipt_sha256')}
                        if malformed == 'stale_reference': guard['runtime_preflight']['receipt'] = 'cycles/stale/runtime-preflight.json'
                        if malformed == 'guard_cycle': guard['cycle'] = 'stale'
                        if malformed == 'expected_digest': guard['expected_sha256'] = '0' * 64
                        refresh.write(guard_path, guard)
                        probe['runtime_bindings']['search_before']['receipt_sha256'] = refresh.digest(guard_path)
                        with self.assertRaises(ValueError): refresh.verify_pre_native_binding(probe)
                        guard_path.write_bytes(guard_bytes)
                        preflight_path.write_bytes(preflight_bytes)
                    refresh.verify_state_commitments(own)
                    self.assertEqual(refresh.run(args), 0)
                    self.assertEqual(command.call_count, 2)
                    good = refresh.read(state_path)
                    receipt = refresh.read(root / 'cycles' / good['last_cycle'] / 'receipt.json')
                    self.assertEqual(refresh.read(root / receipt['comparison_evidence'])['baseline_run_id'], old['last_run_id'])

    def combined_recovery_control(self, mode, proposal):
        root, sid, attempt, native, old, catalog = self.seed(proposal)
        args = argparse.Namespace(proposal='proposal.json' if proposal else None)
        attempt[:] = ['candidate', 0]
        original = self.f.uv.read_bytes()
        def provider(arguments, output, timeout):
            code = native(arguments, output, timeout)
            if arguments[0] == 'github-search':
                if mode == 'exit_drift':
                    self.f.uv.write_bytes(original + b'\nsynthetic drift')
                    return 17
                if mode in ('missing_status', 'timing_overflow', 'summary_bool'):
                    response = refresh.read(output.with_suffix('.json'))
                    if mode == 'missing_status': response.pop('status')
                    if mode == 'timing_overflow': response['timing']['duration_ms'] = 10 ** 400
                    if mode == 'summary_bool': response['summary']['successful_searches'] = True
                    refresh.write(output.with_suffix('.json'), response)
            return code
        replace = Path.replace
        def interrupt(path, target):
            if Path(target) == root / 'learning-state.json' and json.loads(path.read_bytes()).get('last_run_id') == 'candidate':
                raise KeyboardInterrupt('synthetic interrupted promotion before state commit')
            return replace(path, target)
        stack, command, imports = self.admission_context(root, provider, 200)
        with stack:
            if mode == 'interruption':
                with patch.object(Path, 'replace', interrupt), self.assertRaises(KeyboardInterrupt):
                    refresh.run(args)
            else:
                self.assertEqual(refresh.run(args), 17 if mode == 'exit_drift' else 2)
            imports.assert_called_once()
            self.assertEqual(command.call_count, 2 if mode == 'interruption' else 1)
            state = refresh.read(root / 'learning-state.json')
            for field in ('queries', 'accepted_baseline', 'baseline_commit', 'coverage_commit', 'last_run_id'):
                self.assertEqual(state[field], old[field], field)
            self.assertEqual(state['next_allowed_at'], 265)
            if mode == 'interruption' and proposal:
                self.assertEqual((root / 'searches.json').read_bytes(), (root / 'candidate.json').read_bytes())
                self.assertNotEqual((root / 'searches.json').read_bytes(), catalog)
            if mode != 'interruption':
                self.assertEqual((root / 'searches.json').read_bytes(), catalog)
                receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                self.assertEqual(receipt['failed_stage'], 'runtime_binding' if mode == 'exit_drift' else 'result_validation')
                self.assertEqual(receipt['native_exit_code'], 17 if mode == 'exit_drift' else 0)
                self.assertFalse(receipt['fresh_snapshot_accepted'])
                self.assertIs(receipt['provider_invoked'], True)
                self.assertEqual(receipt['comparison_state'], 'unresolved')
                if mode == 'exit_drift':
                    guard = refresh.read(root / receipt['runtime_bindings']['search_after']['receipt'])
                    self.assertEqual(guard['native_exit_code'], 17)
                    self.assertIs(guard['command_completed'], True)
                    self.assertEqual(guard['outcome'], 'runtime_unavailable')
        self.f.uv.write_bytes(original)
        if mode == 'interruption':
            stack, command, imports = self.admission_context(root, native, 300)
            with stack, patch.object(refresh, 'runner_preflight', wraps=refresh.runner_preflight) as preflight:
                self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
                command.assert_not_called()
                imports.assert_not_called()
                preflight.assert_not_called()
                recovered = refresh.read(root / 'learning-state.json')
                self.assertEqual(recovered['accepted_baseline'], old['accepted_baseline'])
                self.assertEqual(recovered['queries'], old['queries'])
                self.assertEqual((root / 'searches.json').read_bytes(), catalog)
        attempt[:] = ['next', 0]
        stack, command, imports = self.admission_context(root, native, 400)
        with stack:
            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
            self.assertEqual(command.call_count, 2)
            imports.assert_called_once()
            good = refresh.read(root / 'learning-state.json')
            receipt = refresh.read(root / 'cycles' / good['last_cycle'] / 'receipt.json')
            self.assertEqual(refresh.read(root / receipt['comparison_evidence'])['baseline_run_id'], old['last_run_id'])
            refresh.verify_state_commitments(good)

    def test_malformed_envelope_after_real_preflight_preserves_baseline(self):
        for proposal in (False, True):
            for mode in ('missing_status', 'timing_overflow', 'summary_bool'):
                with self.subTest(proposal=proposal, mode=mode): self.combined_recovery_control(mode, proposal)

    def test_interrupted_promotion_recovers_before_preflight_and_provider(self):
        for proposal in (False, True):
            with self.subTest(proposal=proposal): self.combined_recovery_control('interruption', proposal)

    def test_post_native_binding_drift_retains_exit17(self):
        for proposal in (False, True):
            with self.subTest(proposal=proposal): self.combined_recovery_control('exit_drift', proposal)

if __name__ == '__main__': unittest.main()
