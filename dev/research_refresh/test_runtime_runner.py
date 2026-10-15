"""Actual runner + actual synthetic preflight; only provider transport is stubbed."""
import argparse
import contextlib
import copy
import io
import json
import os
import unittest
from unittest.mock import patch
import refresh
import runtime_preflight as runtime
import test_refresh as feedback
import test_runtime_binding as binding


class RunnerPreflightTests(unittest.TestCase):
    def setUp(self):
        self.fixture = binding.NativeBindingTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.model = feedback.FeedbackChecks()
        self.model.setUp()
        self.model.doCleanups()  # Inherited RF1 seam must not mock this integration.
        self.f = self.fixture
        self.admission = self.f.cycle / 'admission.json'
        refresh.write(self.admission, self.f.admission)
        self.native_tasks = (self.f.project / 'mise.toml').read_text()
        self.healthy = 'print(' + repr(json.dumps(self.f.expected)) + ')'

    def scenario(self, proposal_mode):
        root = (self.f.cycle / ('proposal' if proposal_mode else 'ordinary')).resolve()
        if root.exists():
            import shutil
            shutil.rmtree(root)
        sid = self.model.workflow(root)
        policy = refresh.read(root / 'policy.json')
        refresh.write(root / 'policy.json', {**policy, 'minimum_seconds_between_runs': 65})
        attempt = ['first', 0]
        def native(arguments, output, timeout):
            if arguments[0] == 'github-search':
                if attempt[1]: return attempt[1]
                _, row = self.model.observation(root, attempt[0], sid)
                refresh.write(output.with_suffix('.json'), self.model.envelope([row]))
            else:
                refresh.write(output.with_suffix('.json'), self.model.comparison(root, 'first', attempt[0], sid))
            return 0
        return root, sid, attempt, native

    def admission_context(self, root, native, now):
        stack = contextlib.ExitStack()
        stack.enter_context(patch.object(refresh, 'ROOT', root))
        stack.enter_context(patch.object(refresh, 'BORROWED', self.f.project))
        stack.enter_context(patch.object(refresh, 'PINNED_UV', self.f.uv))
        # Seam changes only admission file location, not its actual JSON/binding logic.
        stack.enter_context(patch.object(refresh, 'RUNTIME_ADMISSION', self.admission, create=True))
        stack.enter_context(patch.dict(os.environ, {}, clear=True))
        stack.enter_context(patch.object(refresh.time, 'time', return_value=now))
        command = stack.enter_context(patch.object(refresh, 'command', side_effect=native))
        imports = stack.enter_context(patch.object(runtime, 'check', wraps=runtime.check))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        return stack, command, imports

    def propose(self, root, sid):
        candidate = refresh.read(root / 'searches.json')
        candidate['searches'][0]['description'] += ' synthetic refinement'
        refresh.write(root / 'candidate.json', candidate)
        refresh.write(root / 'proposal.json', {'catalog': 'candidate.json',
            'base_catalog_sha256': refresh.digest(root / 'searches.json'),
            'changes': {sid: self.model.proposal['changes']['test']}})

    def exercise_unavailable(self, condition):
        for proposal_mode in (False, True):
            with self.subTest(proposal=proposal_mode, condition=condition):
                self.f.executable(self.healthy)
                refresh.write(self.admission, self.f.admission)
                self.f.metadata.write_text('Name: githubkit\nVersion: 0.16.1\n')
                (self.f.project / 'mise.toml').write_text(self.native_tasks)
                root, sid, attempt, native = self.scenario(proposal_mode)
                stack, command, imports = self.admission_context(root, native, 100)
                with stack:
                    self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
                    imports.assert_called_once()
                    self.assertEqual(imports.call_args.kwargs['timeout'], 10)
                old = refresh.read(root / 'learning-state.json')
                catalog = (root / 'searches.json').read_bytes()
                if proposal_mode: self.propose(root, sid)
                if condition in ('ssl', 'githubkit'):
                    self.f.executable('raise ImportError(' + repr(condition + ' unavailable') + ')')
                if condition == 'timeout': self.f.executable('import time;time.sleep(30)')
                if condition == 'identity':
                    wrong = {**self.f.expected, 'prefix': '/synthetic/wrong'}
                    self.f.executable('print(' + repr(json.dumps(wrong)) + ')')
                if condition == 'sdk_pin': self.f.metadata.write_text('Version: 9.0\n')
                if condition == 'duplicate_admission':
                    self.admission.write_text(self.admission.read_text().replace('"uv_version":', '"uv_version":"wrong","uv_version":'))
                if condition in ('admission_list', 'admission_null'):
                    refresh.write(self.admission, [] if condition == 'admission_list' else None)
                if condition in ('help_list', 'receipt_null'):
                    malformed = copy.deepcopy(self.f.admission)
                    if condition == 'help_list': malformed['help_receipts'] = []
                    else: malformed['help_receipts']['uv-version.txt'] = None
                    refresh.write(self.admission, malformed)
                if condition == 'tasks_list': (self.f.project / 'mise.toml').write_text('tasks=["synthetic"]\n')
                if condition == 'task_scalar': (self.f.project / 'mise.toml').write_text('[tasks]\ngithub-search="synthetic"\n')
                stack, command, imports = self.admission_context(root, native, 200)
                with stack:
                    if condition == 'override': os.environ['UV_PROJECT'] = '/private-selector-value'
                    self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 2)
                    command.assert_not_called()
                    self.assertEqual(imports.call_count, 0 if condition in ('sdk_pin', 'duplicate_admission', 'override', 'admission_list', 'admission_null', 'help_list', 'receipt_null', 'tasks_list', 'task_scalar') else 1)
                    state = refresh.read(root / 'learning-state.json')
                    for field in ('queries', 'accepted_baseline', 'baseline_commit', 'coverage_commit', 'last_run_id', 'next_allowed_at'):
                        self.assertEqual(state[field], old[field], field)
                    self.assertEqual((root / 'searches.json').read_bytes(), catalog)
                    receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
                    self.assertIsNone(receipt['native_exit_code'])
                    self.assertIs(receipt['provider_invoked'], False)
                    self.assertEqual(receipt['failed_stage'], 'runtime_preflight')
                    self.assertEqual(receipt['comparison_state'], 'unresolved')
                    preflight = refresh.read(root / receipt['runtime_preflight']['receipt'])
                    self.assertEqual(preflight['outcome'], 'runtime_unavailable')
                    errors = {'admission_list': 'Runtime admission has an invalid JSON type',
                              'admission_null': 'Runtime admission has an invalid JSON type',
                              'help_list': 'Runtime help receipts must be an object',
                              'receipt_null': 'Runtime help receipt must be an object: uv-version.txt',
                              'tasks_list': 'Borrowed native tasks must be an object',
                              'task_scalar': 'Borrowed native task records must be objects'}
                    if condition in errors: self.assertEqual(preflight['error'], errors[condition])
                    expected_exit = 1 if condition in ('ssl', 'githubkit') else (-9 if condition == 'timeout' else (0 if condition == 'identity' else None))
                    self.assertEqual(preflight['exit_code'], expected_exit)
                    self.assertEqual(receipt['runtime_preflight']['exit_code'], expected_exit)
                    for key in ('receipt', 'stdout', 'stderr'):
                        self.assertEqual(refresh.digest(root / receipt['runtime_preflight'][key]), receipt['runtime_preflight'][key + '_sha256'])
                    if condition == 'timeout':
                        self.assertTrue(preflight['timed_out'])
                        with self.assertRaises(ProcessLookupError): os.killpg(preflight['pid'], 0)
                    self.assertNotIn('/private-selector-value', json.dumps(receipt))
                    refresh.verify_state_commitments(state)
                (self.f.project / 'mise.toml').write_text(self.native_tasks)
                self.f.metadata.write_text('Name: githubkit\nVersion: 0.16.1\n')
                refresh.write(self.admission, self.f.admission)
                self.f.executable(self.healthy)
                attempt[:] = ['next', 0]
                stack, command, imports = self.admission_context(root, native, 300)
                with stack:
                    self.assertEqual(refresh.run(argparse.Namespace(proposal='proposal.json' if proposal_mode else None)), 0)
                    self.assertEqual(command.call_count, 2)
                    imports.assert_called_once()
                    refresh.verify_state_commitments(refresh.read(root / 'learning-state.json'))

    def test_ssl_failure(self): self.exercise_unavailable('ssl')
    def test_sdk_import_failure(self): self.exercise_unavailable('githubkit')
    def test_actual_timeout(self): self.exercise_unavailable('timeout')
    def test_conflicting_override(self): self.exercise_unavailable('override')
    def test_sdk_pin_mismatch(self): self.exercise_unavailable('sdk_pin')
    def test_duplicate_admission_refused(self): self.exercise_unavailable('duplicate_admission')

    def test_wrong_import_identity(self): self.exercise_unavailable('identity')

    def test_malformed_admission_containers(self):
        for condition in ('admission_list', 'admission_null', 'help_list', 'receipt_null', 'tasks_list', 'task_scalar'):
            self.exercise_unavailable(condition)

    def test_validation_precedes_preflight(self):
        root, sid, attempt, native = self.scenario(False)
        stack, command, imports = self.admission_context(root, native, 100)
        with stack: self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 0)
        state = refresh.read(root / 'learning-state.json')
        stack, command, imports = self.admission_context(root, native, 150)
        with stack:
            with self.assertRaisesRegex(ValueError, 'Cooldown active'):
                refresh.run(argparse.Namespace(proposal=None))
            imports.assert_not_called()
            command.assert_not_called()
        catalog = (root / 'searches.json').read_bytes()
        invalid = json.loads(catalog)
        invalid['searches'][0]['max_pages'] = 0
        refresh.write(root / 'searches.json', invalid)
        stack, command, imports = self.admission_context(root, native, 200)
        with stack:
            with self.assertRaises(ValueError): refresh.run(argparse.Namespace(proposal=None))
            imports.assert_not_called()
            command.assert_not_called()
        (root / 'searches.json').write_bytes(catalog)
        state['terminal_commit']['event_sha256'] = '0' * 64
        refresh.write(root / 'learning-state.json', state)
        stack, command, imports = self.admission_context(root, native, 200)
        with stack:
            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 2)
            imports.assert_not_called()
            command.assert_not_called()
            observed = refresh.read(root / 'learning-state.json')
            failed = refresh.read(root / 'cycles' / observed['last_failed_cycle'] / 'receipt.json')
            self.assertEqual(failed['failed_stage'], 'baseline_resolution')

    def test_healthy_preflight_then_native_failure(self):
        root, sid, attempt, native = self.scenario(False)
        attempt[:] = ['failed', 17]
        stack, command, imports = self.admission_context(root, native, 100)
        with stack:
            self.assertEqual(refresh.run(argparse.Namespace(proposal=None)), 17)
            imports.assert_called_once()
            command.assert_called_once()
        state = refresh.read(root / 'learning-state.json')
        self.assertEqual(state['next_allowed_at'], 165)
        receipt = refresh.read(root / 'cycles' / state['last_failed_cycle'] / 'receipt.json')
        self.assertEqual(receipt['runtime_preflight']['outcome'], 'runtime_ready')
        self.assertEqual(receipt['runtime_preflight']['exit_code'], 0)
        self.assertEqual(receipt['native_exit_code'], 17)
        self.assertIs(receipt['provider_invoked'], True)

if __name__ == '__main__': unittest.main()
