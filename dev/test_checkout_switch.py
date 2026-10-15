"""Real scratch worktree checks for the A11b guarded switch."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import checkout_apply as admission
import checkout_switch as switch
import checkout_transfer as transfer


PLAN = Path(__file__).with_name("checkout_transfer.py")


class SwitchTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory(prefix="a11b-")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.source, self.old, self.remote = (self.base / name for name in ("source", "old", "remote.git"))
        self.plan_file, self.intent_file, self.journal = (self.base / name for name in ("plan.json", "intent.json", "journal"))
        self.env = os.environ.copy()
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull, GIT_TERMINAL_PROMPT="0")
        self.source.mkdir()
        self.git(self.source, "init", "-q")
        self.git(self.source, "config", "user.name", "A11 Test")
        self.git(self.source, "config", "user.email", "a11@example.invalid")
        self.git(self.source, "branch", "-M", "main")
        (self.source / ".gitignore").write_text("cache.bin\n")
        (self.source / "README.md").write_text("source\n")
        self.git(self.source, "add", ".gitignore", "README.md")
        self.git(self.source, "commit", "-qm", "source")
        self.source_head = self.git(self.source, "rev-parse", "HEAD")
        self.git(self.source, "worktree", "add", "-qb", "delivery", str(self.old))
        (self.old / "target.txt").write_text("published\n")
        self.git(self.old, "add", "target.txt")
        self.git(self.old, "commit", "-qm", "delivery")
        self.commit = self.git(self.old, "rev-parse", "HEAD")
        self.remote.mkdir()
        self.git(self.remote, "init", "--bare", "-q")
        self.git(self.source, "remote", "add", "origin", str(self.remote))
        self.git(self.old, "push", "-q", "origin", "delivery")
        self.git(self.old, "update-ref", "refs/remotes/origin/delivery", self.commit)
        (self.source / "handoff.txt").write_text("approved handoff\n")
        (self.old / "target.txt").write_text("retained edit\n")
        (self.old / "local.txt").write_text("retained untracked\n")
        (self.old / "cache.bin").write_text("retained ignored\n")

    def git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=cwd,
                                env=self.env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def prepare(self) -> tuple[str, str]:
        approved = hashlib.sha256((self.source / "handoff.txt").read_bytes()).hexdigest()
        result = subprocess.run([sys.executable, "-B", str(PLAN), "plan", "--source", str(self.source),
                                 "--old", str(self.old), "--source-head", self.source_head,
                                 "--commit", self.commit, "--branch", "delivery",
                                 "--approve-untracked", f"handoff.txt={approved}",
                                 "--preparation-decision", "admit-source-preparation"],
                                cwd=self.base, env=self.env, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.plan_file.write_bytes(result.stdout)
        plan_sha = hashlib.sha256(result.stdout).hexdigest()
        plan = admission.load_plan(self.plan_file, plan_sha)
        intent = admission.verify(plan, plan_sha, (self.source, self.old, "delivery"))
        admission.create_intent(self.intent_file, intent, (self.source, self.old))
        return plan_sha, hashlib.sha256(self.intent_file.read_bytes()).hexdigest()

    def execute(self, digests: tuple[str, str]) -> dict[str, str]:
        return switch.execute(self.plan_file, digests[0], self.intent_file, digests[1],
                              self.journal, (self.source, self.old, "delivery"))

    def test_switch_preserves_dirty_untracked_ignored_and_refuses_replay(self) -> None:
        digests = self.prepare()
        self.assertEqual(self.execute(digests)["status"], "SWITCHED")
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "delivery")
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "")
        self.assertEqual(self.git(self.source, "rev-parse", "HEAD"), self.commit)
        self.assertEqual((self.old / "target.txt").read_text(), "retained edit\n")
        self.assertEqual((self.old / "local.txt").read_text(), "retained untracked\n")
        self.assertEqual((self.old / "cache.bin").read_text(), "retained ignored\n")
        self.assertEqual((self.source / "handoff.txt").read_text(), "approved handoff\n")
        self.assertTrue((self.journal / "verified.json").exists())
        with self.assertRaises(transfer.Refusal):
            self.execute(digests)

    def test_drift_refused_before_journal_or_mutation(self) -> None:
        digests = self.prepare()
        (self.old / "cache.bin").write_text("drift\n")
        with self.assertRaises(transfer.Refusal):
            self.execute(digests)
        self.assertFalse(self.journal.exists())
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "delivery")
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "main")

    def test_failed_source_switch_restores_old_owner(self) -> None:
        digests = self.prepare()
        real = switch.git_change
        def fail_source(root: Path, *args: str) -> None:
            if root == self.source:
                raise transfer.Refusal("injected switch failure")
            real(root, *args)
        with patch.object(switch, "git_change", side_effect=fail_source):
            with self.assertRaises(transfer.Refusal):
                self.execute(digests)
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "delivery")
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "main")
        self.assertTrue((self.journal / "recovered.json").exists())

    def test_post_detach_interruption_is_replay_boundary(self) -> None:
        digests = self.prepare()
        self.journal.mkdir()
        switch.record(self.journal, "detach_started")
        self.git(self.old, "switch", "--detach", self.commit)
        with self.assertRaises(transfer.Refusal):
            self.execute(digests)
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "")
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "main")
        self.assertEqual(json.loads((self.journal / "detach_started.json").read_text())["phase"], "detach_started")

    def test_post_switch_verification_failure_requires_inspection(self) -> None:
        digests = self.prepare()
        with patch.object(switch, "verify_post", side_effect=transfer.Refusal("injected verification failure")):
            with self.assertRaises(transfer.Refusal):
                self.execute(digests)
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "delivery")
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "")
        self.assertTrue((self.journal / "recovery_required.json").exists())


if __name__ == "__main__":
    unittest.main()
