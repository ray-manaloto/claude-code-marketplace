"""Offline native assembly seam; Popen interception never executes fnox/mise/uv."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import refresh
import configuration
import runtime_preflight as runtime
import test_runtime_preflight as fixtures


class NativeBindingTests(unittest.TestCase):
    executable = fixtures.RuntimePreflightTests.executable
    # Reuse synthetic filesystem fixture, but do not inherit subprocess test cases.
    def setUp(self):
        fixtures.RuntimePreflightTests.setUp(self)
        self.uv = Path(self.temp.name) / 'uv/uv'
        self.uv.parent.mkdir()
        self.uv.write_text('synthetic pinned uv')
        self.uv.chmod(0o755)
        self.project.joinpath('mise.toml').write_text('''[tasks.github-search]
run = 'uv run github-search "$@"'
[tasks."github:diff"]
run = 'uv run github-search diff "$@"'
''')
        self.admission = {'status': 'read_only_admission_inputs_verified_not_native_runtime_qualification',
                          'mise_version': '2026.10.8', 'uv_version': '0.13.0',
                          'borrowed_root': str(self.project), 'help_receipts': {}}
        for name in ('mise-version.txt', 'mise-run-help.txt', 'uv-version.txt',
                     'uv-run-help.txt', 'uv-run-help-long.txt'):
            path = self.cycle / name
            path.write_text('synthetic pinned help')
            self.admission['help_receipts'][name] = {'path': str(path),
                                                   'sha256': runtime.sha(path), 'exit_code': 0}
        # Explicit synthetic selections replace the former machine-wide defaults.
        config = {'format_version': 1, 'borrowed_project': str(self.project), 'uv': str(self.uv)}
        for name in ('fnox', 'mise', 'fnox_config', 'runtime_admission'):
            path = self.cycle / name
            path.write_text(json.dumps(self.admission) if name == 'runtime_admission' else '#!/bin/sh\nexit 91\n')
            path.chmod(0o755)
            config[name] = str(path)
        config_path = Path(self.temp.name) / 'runtime.json'
        config_path.write_text(json.dumps(config))
        settings = configuration.load(self.cycle, config_path)
        selection = patch.multiple(refresh, ROOT=settings['root'], BORROWED=settings['borrowed'],
                                   PINNED_UV=settings['uv'], RUNTIME_ADMISSION=settings['admission'],
                                   PREFIX=settings['prefix'])
        selection.start()
        self.addCleanup(selection.stop)

    def binding(self):
        return runtime.native_binding(self.project, '0.16.1', self.uv, self.admission)

    def test_admission_and_launch_metadata_are_bound(self):
        bound = self.binding()
        self.assertEqual(bound['uv']['resolved'], str(self.uv.resolve()))
        self.assertEqual(bound['runtime']['interpreter'], str(self.python))
        self.assertEqual(bound, self.binding())
        self.uv.write_text('changed executable')
        self.assertNotEqual(bound, self.binding())
        self.project.joinpath('mise.toml').write_text('[tasks.github-search]\nrun="uv sync"\n')
        with self.assertRaises(ValueError):
            self.binding()

    def test_invalid_help_refused(self):
        for mutation in ('hash', 'exit', 'version', 'root', 'missing'):
            with self.subTest(mutation=mutation):
                admission = copy.deepcopy(self.admission)
                if mutation == 'hash': admission['help_receipts']['uv-version.txt']['sha256'] = 'bad'
                if mutation == 'exit': admission['help_receipts']['uv-version.txt']['exit_code'] = True
                if mutation == 'version': admission['uv_version'] = '0.12.7'
                if mutation == 'root': admission['borrowed_root'] = '/other'
                if mutation == 'missing': del admission['help_receipts']['mise-run-help.txt']
                with self.assertRaises(ValueError):
                    runtime.native_binding(self.project, '0.16.1', self.uv, admission)

    def test_command_real_assembly_beneath_popen(self):
        for task in ('github-search', 'github:diff'):
            with self.subTest(task=task), patch.object(refresh, 'BORROWED', self.project), \
                    patch.object(refresh, 'PINNED_UV', self.uv), \
                    patch.dict(os.environ, {'PATH': '/synthetic/path'}, clear=True), \
                    patch.object(refresh.subprocess, 'Popen') as launch:
                launch.return_value.wait.return_value = 0
                self.assertEqual(refresh.command([task, '--', '--json'], self.cycle / task, 180), 0)
                args, kwargs = launch.call_args
                self.assertEqual(args[0], refresh.PREFIX + [task, '--', '--json'])
                self.assertEqual(args[0][args[0].index('exec') + 1], '--')
                self.assertEqual(args[0][-6:-3], ['run', '--no-deps', '--skip-tools'])
                env = kwargs['env']
                for key, value in {'UV_NO_SYNC': '1', 'UV_NO_ENV_FILE': '1',
                                   'UV_PYTHON_DOWNLOADS': 'never', 'UV_COMPILE_BYTECODE': '0',
                                   'PYTHONDONTWRITEBYTECODE': '1', 'UV_PYTHON': str(self.python),
                                   'UV_PROJECT_ENVIRONMENT': str(self.venv),
                                   'VIRTUAL_ENV': str(self.venv)}.items():
                    self.assertEqual(env[key], value)
                self.assertEqual(env['PATH'], str(self.uv.parent) + os.pathsep + '/synthetic/path')
                self.assertNotIn('UV_NO_CONFIG', env)
                self.assertTrue(kwargs['start_new_session'])
                launch.return_value.wait.assert_called_once_with(timeout=180)

    def test_matching_venv_selectors_permit_native_assembly(self):
        matching = {'VIRTUAL_ENV': str(self.venv), 'UV_PROJECT_ENVIRONMENT': str(self.venv)}
        for task in ('github-search', 'github:diff'):
            with self.subTest(task=task), patch.object(refresh, 'BORROWED', self.project), \
                    patch.object(refresh, 'PINNED_UV', self.uv), \
                    patch.dict(os.environ, matching, clear=True), \
                    patch.object(refresh.subprocess, 'Popen') as launch:
                launch.return_value.wait.return_value = 0
                self.assertEqual(refresh.command([task, '--', '--json'], self.cycle / task, 180), 0)
                launch.assert_called_once()
                for name, value in matching.items():
                    self.assertEqual(launch.call_args.kwargs['env'][name], value)
                self.assertEqual(launch.call_args.kwargs['env']['UV_PYTHON'], str(self.python))
                self.assertEqual(launch.call_args.args[0], refresh.PREFIX + [task, '--', '--json'])

    def test_metadata_and_entrypoint_shebang_drift_detected(self):
        entrypoint = self.venv / 'bin/github-search'
        entrypoint.write_text('#!' + str(self.python) + '\n# synthetic entrypoint\n')
        bound = self.binding()
        for filename, changed in (('pyvenv.cfg', b'synthetic metadata drift\n'),
                                  ('bin/github-search', b'#!/another/python\n# synthetic entrypoint\n')):
            path = self.venv / filename
            original = path.read_bytes()
            with self.subTest(filename=filename):
                path.write_bytes(changed)
                observed = self.binding()
                self.assertNotEqual(observed, bound)
                self.assertEqual(observed['runtime']['files'][str(path)], runtime.sha(path))
                self.assertNotEqual(observed['runtime']['files'][str(path)],
                                    bound['runtime']['files'][str(path)])
                self.assertEqual(observed['runtime']['interpreter'], str(self.python))
                self.assertEqual(observed['uv'], bound['uv'])
                path.write_bytes(original)
                self.assertEqual(self.binding(), bound)

    def test_conflicts_refuse_command_without_values(self):
        for selector in runtime.SELECTORS + ('UV_NO_CONFIG', 'VIRTUAL_ENV', 'UV_PROJECT_ENVIRONMENT'):
            with self.subTest(selector=selector), patch.object(refresh, 'BORROWED', self.project), \
                    patch.dict(os.environ, {selector: '/private-selector-value'}, clear=True), \
                    patch.object(refresh.subprocess, 'Popen') as launch:
                with self.assertRaises(ValueError) as error:
                    refresh.command(['github-search'], self.cycle / 'out', 180)
                self.assertIn(selector, str(error.exception))
                self.assertNotIn('/private-selector-value', str(error.exception))
                launch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
