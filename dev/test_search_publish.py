"""A05b public comparison and serial-writer controls; no credentials/network."""

import base64
import contextlib
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import httpx

from collect_saved_search import main
from github_search_one_page import capture
from search_catalog import ROOT, catalog, digest, quarantine, query_lock, record

SYNTHETIC = ROOT / "dev/fixtures/github-code-search-synthetic.json"


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".a05b-", dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.scratch = Path(self.temp.name)
        self.output = self.scratch / "records"
        self.row = catalog(ROOT / "dev/saved-searches.toml")[0][0]
        self.template = json.loads(SYNTHETIC.read_bytes())
        self.assertEqual(self.template["_fixture_kind"], "synthetic-offline-only")

    def envelope(self, query, count, sha="a" * 40):
        body = json.loads(base64.b64decode(self.template["body_base64"]))
        body["items"] = body["items"][:count]
        body["total_count"] = count
        for item in body["items"]:
            item["sha"] = sha
        response = httpx.Response(200, headers={"content-type": "application/json"},
                                  content=json.dumps(body).encode())
        return capture(response, query, self.row["per_page"], 1)

    def fixture(self, name, count):
        path = self.scratch / name
        controls = f"README repo:{self.row['repo']}"
        path.write_text(json.dumps({"format": "githubkit-http-sequence-v1",
                                    "responses": [self.envelope(self.row["effective_query"], count),
                                                  self.envelope(controls, 5)]}))
        return path

    def invoke(self, *extra):
        args = ["collect", "offline", *extra, "--output", str(self.output)]
        with patch.object(sys, "argv", args), \
             patch("collect_saved_search.credential",
                   side_effect=AssertionError("credential lookup")), \
             patch("httpx.HTTPTransport.handle_request",
                   side_effect=AssertionError("network")):
            stdout = StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main()
        return code, json.loads(stdout.getvalue())

    def selected(self, fixture):
        return self.invoke("--id", self.row["id"], "--fixture", str(fixture))

    def test_first_then_changed_then_quarantined_baseline(self):
        empty = self.fixture("empty.json", 0)
        full = self.fixture("full.json", 5)
        code, first = self.selected(empty)
        self.assertEqual(code, 0)
        self.assertEqual((first["status"], first["comparison"]["status"]),
                         ("empty_verified", "baseline_established"))
        comparison_path = Path(first["comparison_receipt"])
        self.assertTrue(comparison_path.is_file())
        self.assertTrue(comparison_path.stem.endswith(digest(comparison_path.read_bytes())))
        code, second = self.selected(full)
        self.assertEqual(code, 0)
        self.assertEqual(second["comparison"]["status"], "compared")
        self.assertEqual((second["comparison"]["new_count"],
                          second["comparison"]["gone_count"]), (5, 0))
        self.assertEqual(second["comparison"]["baseline_run_id"],
                         Path(first["receipt"]).name)
        quarantine(self.output, Path(second["receipt"]).name, "scratch reset")
        code, third = self.selected(empty)
        self.assertEqual(code, 0)
        self.assertEqual(third["comparison"]["status"], "baseline_established")
        self.assertEqual(third["comparison"]["reason"], "quarantine_reset")

    def test_invalid_baseline_refuses_before_credentials_and_new_record(self):
        fixture = self.fixture("empty.json", 0)
        _, first = self.selected(fixture)
        (Path(first["receipt"]) / "normalized.json").write_text("changed")
        code, refused = self.selected(fixture)
        self.assertEqual(code, 2)
        self.assertEqual(refused["comparison"]["status"], "unresolved")
        self.assertNotIn("receipt", refused)
        self.assertEqual(len(list((self.output / "runs").iterdir())), 1)

    def test_baseline_drift_during_collection_retains_raw_but_no_delta(self):
        fixture = self.fixture("empty.json", 0)
        _, first = self.selected(fixture)
        baseline = Path(first["receipt"])
        comparisons_before = list((self.output / "comparisons").iterdir())

        def record_then_corrupt(*args):
            target = record(*args)
            (baseline / "normalized.json").write_text("changed")
            return target

        with patch("collect_saved_search.record", side_effect=record_then_corrupt):
            code, result = self.selected(fixture)
        self.assertEqual(code, 2)
        self.assertEqual(result["comparison"]["status"], "unresolved")
        self.assertTrue(Path(result["receipt"]).is_dir())
        self.assertNotIn("comparison_receipt", result)
        self.assertEqual(list((self.output / "comparisons").iterdir()), comparisons_before)

    def test_all_and_subset_leave_other_queries_last_good(self):
        source = (ROOT / "dev/saved-searches.toml").read_text()
        header, first, *_ = source.split("[[search]]")
        original = header + "[[search]]" + first
        catalog_path = self.scratch / "catalog.toml"
        second = original.split("[[search]]", 1)[1].replace(
            'id = "codex-schema"', 'id = "other-schema"', 1)
        catalog_path.write_text(original + "\n[[search]]" + second)
        fixture_dir = self.scratch / "fixtures"
        fixture_dir.mkdir()
        empty = self.fixture("empty.json", 0)
        for name in ("codex-schema", "other-schema"):
            (fixture_dir / f"{name}.json").write_bytes(empty.read_bytes())
        code, all_result = self.invoke("--all", "--catalog", str(catalog_path),
                                       "--fixture-dir", str(fixture_dir))
        self.assertEqual(code, 0)
        self.assertEqual([item["comparison"]["status"] for item in all_result["results"]],
                         ["baseline_established", "baseline_established"])
        other = all_result["results"][1]["receipt"]
        code, selected = self.selected(empty)
        self.assertEqual(code, 0)
        self.assertEqual(selected["comparison"]["status"], "compared")
        self.assertTrue(Path(other).is_dir())
        self.assertEqual(len(list((self.output / "runs").glob("other-schema--*"))), 1)
        (Path(other) / "normalized.json").write_text("changed")
        code, mixed = self.invoke("--all", "--catalog", str(catalog_path),
                                  "--fixture-dir", str(fixture_dir))
        self.assertEqual(code, 2)
        self.assertEqual([item["comparison"]["status"] for item in mixed["results"]],
                         ["compared", "unresolved"])
        self.assertNotIn("receipt", mixed["results"][1])
        self.assertEqual(len(list((self.output / "runs").glob("other-schema--*"))), 1)

    def test_lock_serializes_public_writer_after_quarantine(self):
        fixture = self.fixture("empty.json", 0)
        _, first = self.selected(fixture)
        script = ("import sys; sys.path.insert(0, 'dev'); "
                  "from search_catalog import quarantine; "
                  "from pathlib import Path; "
                  "quarantine(Path(sys.argv[1]), sys.argv[2], 'race reset')")
        with query_lock(self.output, self.row["id"]):
            process = subprocess.Popen([sys.executable, "-B", "-c", script,
                                        str(self.output), Path(first["receipt"]).name],
                                       cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True)
            time.sleep(0.1)
            self.assertIsNone(process.poll())
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual((process.returncode, stdout, stderr), (0, "", ""))
        code, second = self.selected(fixture)
        self.assertEqual(code, 0)
        self.assertEqual(second["comparison"]["status"], "baseline_established")
        self.assertEqual(second["comparison"]["reason"], "quarantine_reset")

    def test_two_public_writers_bind_the_second_to_the_first(self):
        fixture = self.fixture("empty.json", 0)
        args = ["offline", "--id", self.row["id"], "--fixture", str(fixture),
                "--output", str(self.output)]
        slow = ("import sys,time; sys.path.insert(0, 'dev'); "
                "import collect_saved_search as m; original=m.collect; "
                "def_slow=lambda *a,**k: (time.sleep(0.25),original(*a,**k))[1]; "
                "m.collect=def_slow; sys.argv=['collect',*sys.argv[1:]]; "
                "raise SystemExit(m.main())")
        first = subprocess.Popen([sys.executable, "-B", "-c", slow, *args],
                                 cwd=ROOT, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        lock_path = self.output / "locks" / f"{self.row['id']}.lock"
        deadline = time.monotonic() + 5
        while not lock_path.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(lock_path.exists())
        second = subprocess.Popen([sys.executable, "-B", "dev/collect_saved_search.py",
                                   *args], cwd=ROOT, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        outputs = [process.communicate(timeout=10) for process in (first, second)]
        self.assertEqual([process.returncode for process in (first, second)], [0, 0],
                         outputs)
        first_result, second_result = (json.loads(result[0]) for result in outputs)
        self.assertEqual(first_result["comparison"]["status"], "baseline_established")
        self.assertEqual(second_result["comparison"]["status"], "compared")
        self.assertEqual(second_result["comparison"]["baseline_run_id"],
                         Path(first_result["receipt"]).name)


if __name__ == "__main__":
    unittest.main()
