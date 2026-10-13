"""Offline CLI controls for portable paths and refusal before side effects."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import configuration
import runtime_preflight


class PortableConfiguration(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='refresh portable ')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.state = self.root / 'state'
        self.borrowed = self.root / 'borrowed'
        self.repository = self.root / 'checkout'
        for path in (self.state, self.borrowed, self.repository):
            path.mkdir()
        self.config = self.root / 'runtime.json'
        self.value = {'format_version': 1, 'borrowed_project': str(self.borrowed)}
        for key in ('uv', 'fnox', 'mise', 'fnox_config', 'runtime_admission'):
            path = self.root / key
            path.write_text('{}' if key == 'runtime_admission' else '#!/bin/sh\nexit 91\n')
            path.chmod(0o700)
            self.value[key] = str(path)
        self.save()

    def save(self, value=None):
        self.config.write_text(json.dumps(self.value if value is None else value))

    def invoke(self, *arguments):
        script = Path(__file__).with_name('refresh.py')
        return subprocess.run([sys.executable, '-B', str(script), *arguments],
                              cwd=self.root, capture_output=True, text=True, timeout=10)

    def test_explicit_paths_keep_fixed_native_contract(self):
        settings = configuration.load(self.state, self.config, self.repository)
        self.assertEqual(settings['root'], self.state)
        self.assertEqual(settings['borrowed'], self.borrowed)
        self.assertEqual(settings['prefix'], [self.value['fnox'], '--config',
            self.value['fnox_config'], '--profile', 'codex_research', '--no-defaults',
            '--no-daemon', '--non-interactive', 'exec', '--', self.value['mise'],
            '-C', str(self.borrowed), 'run', '--no-deps', '--skip-tools'])
        self.assertEqual(list(self.state.iterdir()), [])

    def test_rejects_renamed_uv_before_native_path_can_choose_another_executable(self):
        renamed = self.root / 'uv-0.13.0'
        renamed.write_bytes(Path(self.value['uv']).read_bytes())
        renamed.chmod(0o700)
        self.save({**self.value, 'uv': str(renamed)})
        with self.assertRaises(ValueError):
            configuration.load(self.state, self.config, self.repository)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_rejects_uv_path_separators_in_directories_and_aliases(self):
        directory = self.root / ('tools' + os.pathsep + 'admitted')
        directory.mkdir()
        (directory / 'uv').symlink_to(self.value['uv'])
        alias = self.root / ('alias' + os.pathsep + 'admitted')
        alias.symlink_to(self.root, target_is_directory=True)
        for selected in (directory / 'uv', alias / 'uv'):
            with self.subTest(selected=selected):
                self.save({**self.value, 'uv': str(selected)})
                with self.assertRaises(ValueError):
                    configuration.load(self.state, self.config, self.repository)
        self.assertEqual(list(self.state.iterdir()), [])

    def test_runtime_aliases_keep_admitted_identity_and_exact_native_uv(self):
        alias = self.root / 'borrowed-alias'
        alias.symlink_to(self.borrowed, target_is_directory=True)
        tool_directory = self.root / 'selected-tools'
        tool_directory.mkdir()
        selected_uv = tool_directory / 'uv'
        selected_uv.symlink_to(self.value['uv'])
        self.save({**self.value, 'borrowed_project': str(alias), 'uv': str(selected_uv)})
        settings = configuration.load(self.state, self.config, self.repository)
        self.assertEqual(settings['borrowed'], alias)
        self.assertEqual(settings['uv'], selected_uv)
        native = runtime_preflight.native_environment(alias, selected_uv, {'PATH': str(self.root)})
        self.assertEqual(shutil.which('uv', path=native['PATH']), str(selected_uv))
        self.assertEqual(Path(shutil.which('uv', path=native['PATH'])).resolve(), selected_uv.resolve())
        self.assertEqual(list(self.state.iterdir()), [])

    def test_cli_missing_or_invalid_configuration_has_no_side_effects(self):
        before = set(self.root.rglob('*'))
        for arguments in ((), ('--state-dir', str(self.state)),
                          ('--state-dir', str(self.state), '--runtime-config', str(self.config))):
            with self.subTest(arguments=arguments):
                if '--runtime-config' in arguments:
                    self.save({**self.value, 'unexpected_secret': 'synthetic'})
                result = self.invoke(*arguments)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(set(self.root.rglob('*')), before)
                self.assertNotIn('synthetic', result.stdout + result.stderr)

    def test_rejects_malformed_relative_missing_and_overlapping_paths(self):
        cases = [None, [], {**self.value, 'format_version': True},
                 {**self.value, 'uv': 'relative'}, {**self.value, 'uv': str(self.root / 'absent')},
                 {**self.value, 'borrowed_project': str(self.state)}]
        for value in cases:
            with self.subTest(value=value):
                self.config.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    configuration.load(self.state, self.config, self.repository)
        self.save()
        for state in (self.repository, self.root, self.borrowed):
            with self.subTest(state=state), self.assertRaises(ValueError):
                configuration.load(state, self.config, self.repository)
        linked = self.root / 'linked-checkout'
        linked.symlink_to(self.repository, target_is_directory=True)
        with self.assertRaises(ValueError):
            configuration.load(linked, self.config, self.repository)
        self.config.write_text(json.dumps(self.value)[:-1] + ', "format_version": 1}')
        with self.assertRaises(ValueError):
            configuration.load(self.state, self.config, self.repository)

    def test_valid_configuration_stops_at_unavailable_runtime_without_native_launch(self):
        examples = Path(__file__).with_name('examples')
        for name in ('policy.json', 'searches.json'):
            (self.state / name).write_bytes((examples / name).read_bytes())
        marker = self.root / 'native-was-invoked'
        Path(self.value['fnox']).write_text('#!/bin/sh\ntouch "' + str(marker) + '"\nexit 91\n')
        result = self.invoke('--state-dir', str(self.state), '--runtime-config', str(self.config))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(marker.exists())
        receipts = list((self.state / 'cycles').glob('*/receipt.json'))
        self.assertEqual(len(receipts), 1, result.stdout + result.stderr)
        receipt = json.loads(receipts[0].read_text())
        self.assertEqual(receipt['attempt_status'], 'failed')
        self.assertEqual(receipt['failed_stage'], 'runtime_preflight')
        self.assertFalse(receipt['provider_invoked'])
        preflight = json.loads((receipts[0].parent / 'runtime-preflight.json').read_text())
        self.assertEqual(preflight['outcome'], 'runtime_unavailable')


if __name__ == '__main__':
    unittest.main()
