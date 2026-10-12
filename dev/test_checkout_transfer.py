"""A10 scratch controls for dry-run transfer and refusal boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import checkout_transfer as transfer

HELPER = Path(__file__).with_name("checkout_transfer.py")


class TransferTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="a10-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source, self.old = self.base / "source", self.base / "old"
        self.env = os.environ.copy()
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        self.source.mkdir()
        self.git(self.source, "init", "-q")
        self.git(self.source, "config", "user.name", "A10 Test")
        self.git(self.source, "config", "user.email", "a10@example.invalid")
        self.git(self.source, "branch", "-M", "main")
        (self.source / "README.md").write_text("source\n")
        (self.source / ".gitignore").write_text("cache.bin\n")
        self.git(self.source, "add", ".gitignore", "README.md")
        self.git(self.source, "commit", "-qm", "source")
        self.source_head = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "worktree", "add", "-qb", "delivery", str(self.old))
        (self.old / "nested").mkdir()
        (self.old / "nested/new.txt").write_text("target\n")
        (self.old / "target.txt").write_text("target\n")
        self.git(self.old, "add", "nested/new.txt", "target.txt")
        self.git(self.old, "commit", "-qm", "published")
        self.commit = self.git(self.old, "rev-parse", "HEAD")
        self.git(self.old, "update-ref", "refs/remotes/origin/delivery", self.commit)
        (self.source / "handoff.txt").write_text("retain\n")
        (self.old / "cache.bin").write_text("old-only\n")

    def git(self, cwd: Path, *args: str) -> str:
        p = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=cwd,
                           env=self.env, capture_output=True, text=True, check=False)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def invoke(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-B", str(HELPER), "plan", "--source", str(self.source),
                               "--old", str(self.old), "--source-head", self.source_head,
                               "--commit", self.commit, "--branch", "delivery", *extra],
                              cwd=self.old, env=self.env, capture_output=True, text=True, check=False)

    def test_plan_pending_approval_and_source_execution(self) -> None:
        first = self.invoke()
        self.assertEqual(first.returncode, 0, first.stderr)
        plan = json.loads(first.stdout)
        self.assertEqual(plan["pending_untracked"], ["handoff.txt"])
        self.assertFalse(plan["ready_for_apply"])
        self.assertEqual(plan["execution_probe"]["executing_cwd"], str(self.source.resolve()))
        self.assertEqual(plan["old_worktree_inventory"]["ignored"]["count"], 1)
        digest = hashlib.sha256((self.source / "handoff.txt").read_bytes()).hexdigest()
        approved = self.invoke("--approve-untracked", f"handoff.txt={digest}")
        self.assertEqual(approved.returncode, 0, approved.stderr)
        approved_plan = json.loads(approved.stdout)
        self.assertFalse(approved_plan["ready_for_apply"])
        self.assertEqual(approved_plan["source_environment"]["observed"], {".mise": "absent", ".venv": "absent"})
        self.assertIn("./dev/mise run tools:prepare", approved_plan["source_environment"]["required_after_switch"])
        admitted = self.invoke("--approve-untracked", f"handoff.txt={digest}",
                              "--preparation-decision", "admit-source-preparation")
        self.assertEqual(admitted.returncode, 0, admitted.stderr)
        self.assertTrue(json.loads(admitted.stdout)["ready_for_apply"])
        self.assertEqual(self.invoke("--approve-untracked", "handoff.txt=" + "0" * 64).returncode, 2)

    def test_refuses_target_path_and_parent_collisions(self) -> None:
        (self.source / "target.txt").symlink_to("README.md")
        self.assertEqual(self.invoke().returncode, 2)
        (self.source / "target.txt").unlink()
        (self.source / "nested").write_text("parent file\n")
        self.assertEqual(self.invoke().returncode, 2)
        (self.source / "nested").unlink()
        (self.source / "nested").symlink_to("README.md")
        self.assertEqual(self.invoke().returncode, 2)

    def test_refuses_drift_and_wrong_probe_cwd(self) -> None:
        (self.source / "README.md").write_text("dirty\n")
        self.assertEqual(self.invoke().returncode, 2)
        (self.source / "README.md").write_text("source\n")
        self.git(self.old, "update-ref", "refs/remotes/origin/delivery", self.source_head)
        self.assertEqual(self.invoke().returncode, 2)
        probe = subprocess.run([sys.executable, "-B", str(HELPER), "probe", "--source", str(self.source)],
                               cwd=self.old, env=self.env, capture_output=True, check=False)
        self.assertEqual(probe.returncode, 2)

    def test_refuses_ignored_target_collision(self) -> None:
        (self.old / "cache.bin").write_text("published\n")
        self.git(self.old, "add", "-f", "cache.bin")
        self.git(self.old, "commit", "-qm", "add ignored target")
        self.commit = self.git(self.old, "rev-parse", "HEAD")
        self.git(self.old, "update-ref", "refs/remotes/origin/delivery", self.commit)
        (self.source / "cache.bin").write_text("retained ignored\n")
        self.assertEqual(self.invoke().returncode, 2)

    def test_refuses_unbounded_ignored_content_and_unsafe_environment(self) -> None:
        with (self.old / "cache.bin").open("wb") as stream:
            stream.truncate(257 * 1024 * 1024)
        self.assertEqual(self.invoke().returncode, 2)
        (self.old / "cache.bin").write_text("old-only\n")
        (self.source / ".mise").symlink_to(self.old / ".mise")
        self.assertEqual(self.invoke().returncode, 2)

    def test_refuses_assume_unchanged_tracked_bytes(self) -> None:
        self.git(self.source, "update-index", "--assume-unchanged", "README.md")
        (self.source / "README.md").write_text("hidden tracked edit\n")
        self.assertEqual(self.invoke().returncode, 2)

    def test_refuses_untracked_approval_changed_during_plan(self) -> None:
        original = hashlib.sha256((self.source / "handoff.txt").read_bytes()).hexdigest()
        arguments = argparse.Namespace(source=self.source, old=self.old, commit=self.commit,
                                       source_head=self.source_head, branch="delivery",
                                       approve_untracked=[f"handoff.txt={original}"], approvals_file=None,
                                       preparation_decision="admit-source-preparation")
        def change_during_probe(_source: Path) -> dict[str, str]:
            (self.source / "handoff.txt").write_text("changed after approval\n")
            return {"executing_cwd": str(self.source.resolve())}
        with mock.patch.object(transfer, "probe", side_effect=change_during_probe):
            with self.assertRaisesRegex(transfer.Refusal, "source changed during planning"):
                transfer.plan(arguments)


if __name__ == "__main__":
    unittest.main()
