"""A04 public recording and validation controls in project-confined scratch."""

import contextlib
import fcntl
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from search_catalog import (ROOT, CatalogError, catalog, digest, encoded, inspect_runs,
                            main, quarantine)

SCRIPT = ROOT / "dev/search_catalog.py"
CATALOG = ROOT / "dev/saved-searches.toml"
FIXTURE = ROOT / "dev/fixtures/github-code-search-empty.json"


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".a04-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.scratch = Path(self.temp.name)
        self.output = self.scratch / "records"

    def invoke(self, *args):
        env = os.environ.copy()
        for key in ("GITHUB_TOKEN", "GH_TOKEN", "GH_HOST"):
            env.pop(key, None)
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args,
                               "--output", str(self.output)], text=True,
                              capture_output=True, env=env, check=False)

    def test_catalog_validation_rejects_unsafe_and_case_colliding_ids(self):
        rows, source_hash = catalog(CATALOG)
        self.assertIn("codex-schema", {row["id"] for row in rows})
        self.assertEqual(len(source_hash), 64)
        source = CATALOG.read_text()
        invalid = self.scratch / "invalid.toml"
        invalid.write_text(source.replace('id = "codex-schema"', 'id = "../unsafe"'))
        with self.assertRaisesRegex(CatalogError, "unsafe or case-colliding"):
            catalog(invalid)
        invalid.write_text(source + "[[search]]" + source.split("[[search]]", 1)[1].replace(
            'id = "codex-schema"', 'id = "Codex-Schema"'))
        with self.assertRaisesRegex(CatalogError, "unsafe or case-colliding"):
            catalog(invalid)
        invalid.write_text(source.replace('repo = "openai/codex"', 'repo = "../codex"'))
        with self.assertRaisesRegex(CatalogError, "invalid query or repository"):
            catalog(invalid)
        invalid.write_text(source.replace('query = "README"', 'query = "schema"'))
        with self.assertRaisesRegex(CatalogError, "invalid control definition"):
            catalog(invalid)

    def test_invalid_live_selection_never_requests_credentials(self):
        with patch.object(sys, "argv", [str(SCRIPT), "live", "--id", "missing",
                                        "--output", str(self.output)]):
            with patch("search_catalog.credential", side_effect=AssertionError("auth")):
                with patch("search_catalog.GitHub", side_effect=AssertionError("network")):
                    with contextlib.redirect_stderr(StringIO()):
                        self.assertEqual(main(), 2)

    def test_two_processes_append_and_quarantine_without_rewrite(self):
        args = ["offline", "--id", "codex-schema", "--fixture", str(FIXTURE)]
        env = {k: v for k, v in os.environ.items()
               if k not in ("GITHUB_TOKEN", "GH_TOKEN", "GH_HOST")}
        command = [sys.executable, "-B", str(SCRIPT), *args, "--output", str(self.output)]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True, env=env)
                     for _ in range(2)]
        results = [process.communicate(timeout=15) for process in processes]
        self.assertEqual([process.returncode for process in processes], [0, 0], results)
        paths = [Path(json.loads(stdout)["receipt"]) for stdout, _ in results]
        self.assertEqual(len(set(paths)), 2)
        originals = {path: {p.name: digest(p.read_bytes()) for p in path.iterdir()}
                     for path in paths}
        self.assertEqual(inspect_runs(self.output, "codex-schema")["valid"], 2)
        target = paths[0]
        (target / "raw.json").write_bytes(b"corrupt scratch copy")
        with self.assertRaisesRegex(CatalogError, "corrupt selected"):
            inspect_runs(self.output, "codex-schema")
        manifest_before = (target / "manifest.json").read_bytes()
        exclusion = quarantine(self.output, target.name, "scratch corruption")
        self.assertTrue(exclusion.is_file())
        self.assertEqual((target / "manifest.json").read_bytes(), manifest_before)
        counts = inspect_runs(self.output, "codex-schema")
        self.assertEqual((counts["valid"], counts["quarantined"]), (1, 1))
        for path in paths[1:]:
            self.assertEqual({p.name: digest(p.read_bytes()) for p in path.iterdir()},
                             originals[path])

    def test_interrupted_and_unselected_corrupt_are_reported(self):
        runs = self.output / "runs"
        runs.mkdir(parents=True)
        (runs / "codex-schema--1791834335766132000--0123456789abcdef").mkdir()
        other = runs / "Other--1791834335766132001--0123456789abcdef"
        other.mkdir()
        (other / "manifest.json").write_text("bad")
        counts = inspect_runs(self.output, "codex-schema")
        self.assertEqual((counts["interrupted"], counts["corrupt_unselected"]), (1, 1))

    def test_corrupt_selected_record_refuses_before_live_auth(self):
        result = self.invoke("offline", "--id", "codex-schema", "--fixture", str(FIXTURE))
        self.assertEqual(result.returncode, 0, result.stderr)
        target = Path(json.loads(result.stdout)["receipt"])
        (target / "normalized.json").write_text("corrupt scratch copy")
        with patch.object(sys, "argv", [str(SCRIPT), "live", "--id", "codex-schema",
                                        "--output", str(self.output)]):
            with patch("search_catalog.credential", side_effect=AssertionError("auth")):
                with patch("search_catalog.GitHub", side_effect=AssertionError("network")):
                    with contextlib.redirect_stderr(StringIO()):
                        self.assertEqual(main(), 2)

    def test_selected_symlink_and_unselected_directory_manifest(self):
        runs = self.output / "runs"
        runs.mkdir(parents=True)
        selected = runs / "codex-schema--1791834335766132000--0123456789abcdef"
        selected.symlink_to(self.scratch, target_is_directory=True)
        with self.assertRaisesRegex(CatalogError, "symlinked selected run"):
            inspect_runs(self.output, "codex-schema")
        selected.unlink()
        other = runs / "Other--1791834335766132001--0123456789abcdef"
        (other / "manifest.json").mkdir(parents=True)
        self.assertEqual(inspect_runs(self.output, "codex-schema")["corrupt_unselected"], 1)

    def test_active_writer_and_interrupted_writer_are_distinct(self):
        runs = self.output / "runs"
        active = runs / "codex-schema--1791834335766132000--0123456789abcdef"
        active.mkdir(parents=True)
        with (active / ".writer.lock").open("xb") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            counts = inspect_runs(self.output, "codex-schema")
            self.assertEqual((counts["active"], counts["interrupted"]), (1, 0))
        counts = inspect_runs(self.output, "codex-schema")
        self.assertEqual((counts["active"], counts["interrupted"]), (0, 1))

    def test_incomplete_quarantine_entry_is_ignored_and_latest_reset(self):
        args = ("offline", "--id", "codex-schema", "--fixture", str(FIXTURE))
        first = self.invoke(*args)
        second = self.invoke(*args)
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        paths = [Path(json.loads(result.stdout)["receipt"]) for result in (first, second)]
        newest = max(paths, key=lambda path: int(path.name.split("--")[1]))
        ledger = quarantine(self.output, newest.name, "reset observation")
        (ledger.parent / ".pending-interrupted").write_bytes(b"partial")
        counts = inspect_runs(self.output, "codex-schema")
        self.assertEqual((counts["quarantined"], counts["baseline_reset"],
                          counts["latest_valid"]), (1, True, None))
        disappearing = ledger.parent / ".pending-disappearing"
        disappearing.write_bytes(b"partial")
        original_lstat = Path.lstat

        def vanish(path):
            if path == disappearing:
                raise FileNotFoundError(path)
            return original_lstat(path)

        with patch.object(Path, "lstat", vanish):
            self.assertEqual(inspect_runs(self.output, "codex-schema")["quarantined"], 1)
        next_result = self.invoke(*args)
        self.assertEqual(next_result.returncode, 0, next_result.stderr)
        self.assertFalse(inspect_runs(self.output, "codex-schema")["baseline_reset"])

    def test_reset_uses_quarantine_event_not_run_name_or_creation_order(self):
        custom = self.scratch / "double-dash.toml"
        custom.write_text(CATALOG.read_text().replace('id = "codex-schema"',
                                                      'id = "codex--schema"'))
        args = ("offline", "--id", "codex--schema", "--catalog", str(custom),
                "--fixture", str(FIXTURE))
        results = [self.invoke(*args) for _ in range(2)]
        self.assertEqual([result.returncode for result in results], [0, 0])
        paths = [Path(json.loads(result.stdout)["receipt"]) for result in results]
        earlier = min(paths, key=lambda path: int(path.name.rsplit("--", 2)[1]))
        manifest = earlier / "manifest.json"
        changed = json.loads(manifest.read_bytes())
        changed["observed_at_ns"] = time.time_ns() + 1_000_000_000
        manifest.write_bytes(encoded(changed))  # Scratch-only overlap fixture.
        quarantine(self.output, earlier.name, "overlapping writer reset")
        counts = inspect_runs(self.output, "codex--schema")
        self.assertEqual((counts["quarantined"], counts["baseline_reset"],
                          counts["latest_valid"]), (1, True, None))


if __name__ == "__main__":
    unittest.main()
