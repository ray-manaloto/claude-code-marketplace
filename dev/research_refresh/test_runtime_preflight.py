import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import runtime_preflight as runtime


class RuntimePreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'borrowed'
        self.venv = self.project / '.venv'
        self.python = self.venv / 'bin/python'
        self.python.parent.mkdir(parents=True)
        self.metadata = self.venv / 'lib/python3.15/site-packages/githubkit-0.16.1.dist-info/METADATA'
        self.metadata.parent.mkdir(parents=True)
        self.metadata.write_text('Name: githubkit\nVersion: 0.16.1\n')
        for name in ('pyproject.toml', 'uv.lock', 'mise.toml', '.venv/pyvenv.cfg', '.venv/bin/github-search'):
            (self.project / name).write_text('fixture\n')
        self.cycle = Path(self.temp.name) / 'cycle'
        self.cycle.mkdir()
        self.expected = dict(executable=str(self.python), resolved=str(self.python.resolve()),
                             prefix=str(self.venv.resolve()), sdk_version='0.16.1')
        self.executable('print(' + repr(json.dumps(self.expected)) + ')')

    def executable(self, body):
        self.python.write_text('#!' + sys.executable + '\n' + body + '\n')
        self.python.chmod(0o755)

    def check(self, **kwargs):
        return runtime.check(self.project, '0.16.1', self.cycle, environment={}, **kwargs)

    def test_actual_healthy_process_and_isolation(self):
        with patch.object(runtime.subprocess, 'Popen', wraps=runtime.subprocess.Popen) as launch:
            result = self.check()
        self.assertEqual(launch.call_args.kwargs['cwd'], self.cycle)
        self.assertEqual(launch.call_args.kwargs['env'], {})
        self.assertTrue(launch.call_args.kwargs['start_new_session'])
        self.assertEqual(result['outcome'], 'runtime_ready')
        self.assertEqual(result['exit_code'], 0)
        self.assertEqual(result['command'][1:3], ['-I', '-B'])
        self.assertEqual(result['before'], result['after'])
        self.executable('import os; assert "GH_TOKEN" not in os.environ\nprint(' + repr(json.dumps(self.expected)) + ')')
        result = runtime.check(self.project, '0.16.1', self.cycle, environment={'GH_TOKEN': 'synthetic-never-record'})
        self.assertEqual(result['outcome'], 'runtime_ready')
        self.assertNotIn('synthetic-never-record', json.dumps(result))

    def test_actual_import_failure(self):
        for module in ('ssl', 'githubkit'):
            with self.subTest(module=module):
                self.executable('raise ImportError(' + repr(module + ' unavailable') + ')')
                result = self.check()
                self.assertEqual(result['outcome'], 'runtime_unavailable')
                self.assertEqual(result['exit_code'], 1)
                self.assertIn(module, result['stderr'])

    def test_actual_timeout_reaps_process_group(self):
        self.executable('import time\ntime.sleep(30)')
        result = self.check(timeout=0.1)
        self.assertTrue(result['timed_out'])
        self.assertEqual(result['exit_code'], -9)
        with self.assertRaises(ProcessLookupError):
            os.killpg(result['pid'], 0)

    def test_overrides_refuse_before_process(self):
        for name in runtime.SELECTORS + ('VIRTUAL_ENV', 'UV_PROJECT_ENVIRONMENT'):
            with self.subTest(name=name), patch.object(runtime.subprocess, 'Popen') as launch:
                result = runtime.check(self.project, '0.16.1', self.cycle, environment={name: '/conflicting'})
                self.assertEqual(result['conflicting_overrides'], [name])
                self.assertFalse(result['launched'])
                launch.assert_not_called()
        result = runtime.check(self.project, '0.16.1', self.cycle,
                               environment={'VIRTUAL_ENV': str(self.venv), 'UV_PROJECT_ENVIRONMENT': str(self.venv)})
        self.assertEqual(result['outcome'], 'runtime_ready')

    def test_sdk_mismatch_refuses_before_process(self):
        self.metadata.write_text('Version: 9.0\n')
        with patch.object(runtime.subprocess, 'Popen') as launch:
            result = self.check()
            self.assertIn('version differs', result['error'])
            launch.assert_not_called()

    def test_process_identity_and_metadata_drift(self):
        wrong = {**self.expected, 'prefix': '/another/runtime'}
        self.executable('print(' + repr(json.dumps(wrong)) + ')')
        self.assertIn('identity differs', self.check()['error'])
        self.executable('from pathlib import Path\nPath(' + repr(str(self.project / 'uv.lock')) + ').write_text("changed")\nprint(' + repr(json.dumps(self.expected)) + ')')
        self.assertIn('metadata changed', self.check()['error'])

    def test_missing_metadata_and_malformed_import_identity(self):
        self.metadata.unlink()
        self.assertFalse(self.check()['launched'])
        self.metadata.write_text('Version: 0.16.1\n')
        for output in ('not json', '[]', '{}', json.dumps({**self.expected, 'sdk_version': True})):
            with self.subTest(output=output):
                self.executable('print(' + repr(output) + ')')
                result = self.check()
                self.assertEqual(result['outcome'], 'runtime_unavailable')
                self.assertEqual(result['exit_code'], 0)
                self.assertIn('error', result)

    def test_duplicate_identity_keys_refused(self):
        ambiguous = json.dumps(self.expected).replace('"prefix":', '"prefix":"/wrong/runtime","prefix":')
        self.executable('print(' + repr(ambiguous) + ')')
        result = self.check()
        self.assertEqual(result['outcome'], 'runtime_unavailable')
        self.assertIn('duplicate', result['error'])

    def test_detached_pipe_holder_does_not_extend_bound(self):
        pidfile = self.cycle / 'child.pid'
        body = ('import subprocess, time\n'
                'child=subprocess.Popen([' + repr(sys.executable) + ',"-c","import time;time.sleep(5)"], start_new_session=True)\n'
                'from pathlib import Path\nPath(' + repr(str(pidfile)) + ').write_text(str(child.pid))\n'
                'time.sleep(30)')
        self.executable(body)
        start = time.monotonic()
        try:
            result = self.check(timeout=0.5)
            self.assertTrue(pidfile.exists(), 'fixture must spawn before timeout')
            self.assertLess(time.monotonic() - start, 1.5)
            self.assertTrue(result['timed_out'])
            self.assertTrue(result['cleanup_incomplete'])
            self.assertEqual(result['outcome'], 'runtime_unavailable')
            with self.assertRaises(ProcessLookupError):
                os.killpg(result['pid'], 0)
        finally:
            if pidfile.exists():
                try:
                    os.killpg(int(pidfile.read_text()), 9)
                except ProcessLookupError:
                    pass


if __name__ == '__main__':
    unittest.main()
