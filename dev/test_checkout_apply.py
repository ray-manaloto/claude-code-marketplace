"""Scratch A11a admission controls; no test switches the source checkout."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

import checkout_apply as apply
import checkout_transfer as transfer


APPLY = Path(__file__).with_name("checkout_apply.py")
PLAN = Path(__file__).with_name("checkout_transfer.py")


class ApplyPreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="a11a-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source, self.old, self.remote = (self.base / name for name in ("source", "old", "remote.git"))
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
        (self.old / "cache.bin").write_text("retained artifact\n")
        self.plan_file, self.intent_file = self.base / "plan.json", self.base / "intent.json"

    def git(self, cwd: Path, *args: str) -> str:
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=cwd,
                                env=self.env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def prepare_plan(self) -> str:
        approval = hashlib.sha256((self.source / "handoff.txt").read_bytes()).hexdigest()
        result = subprocess.run([sys.executable, "-B", str(PLAN), "plan", "--source", str(self.source),
                                 "--old", str(self.old), "--source-head", self.source_head,
                                 "--commit", self.commit, "--branch", "delivery",
                                 "--approve-untracked", f"handoff.txt={approval}",
                                 "--preparation-decision", "admit-source-preparation"],
                                cwd=self.base, env=self.env, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.plan_file.write_bytes(result.stdout)
        return hashlib.sha256(result.stdout).hexdigest()

    def invoke(self, digest: str) -> SimpleNamespace:
        try:
            plan = apply.load_plan(self.plan_file, digest)
            intent = apply.verify(plan, digest, (self.source, self.old, "delivery"))
            apply.create_intent(self.intent_file, intent, (self.source, self.old))
            return SimpleNamespace(returncode=0, stderr="")
        except (transfer.Refusal, OSError, ValueError, KeyError, TypeError) as exc:
            return SimpleNamespace(returncode=2, stderr=str(exc))

    def test_production_cli_refuses_valid_foreign_plan(self) -> None:
        digest = self.prepare_plan()
        result = subprocess.run([sys.executable, "-B", str(APPLY), "prepare",
                                 "--plan-file", str(self.plan_file), "--plan-sha256", digest,
                                 "--intent-file", str(self.intent_file)], cwd=self.base,
                                env=self.env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside the admitted checkout binding", result.stderr)
        self.assertFalse(self.intent_file.exists())

    def test_prepare_preserves_both_roots_and_records_retention(self) -> None:
        digest = self.prepare_plan()
        result = self.invoke(digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        intent = json.loads(self.intent_file.read_text())
        self.assertEqual(intent["mode"], "preparation-only")
        self.assertEqual(intent["published_commit"], self.commit)
        self.assertEqual(intent["retained_old_ignored"]["count"], 1)
        self.assertEqual(self.git(self.source, "branch", "--show-current"), "main")
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "delivery")
        self.assertEqual((self.old / "cache.bin").read_text(), "retained artifact\n")
        self.assertEqual(self.intent_file.stat().st_mode & 0o777, 0o600)

    def test_refuses_source_drift_and_target_collision(self) -> None:
        digest = self.prepare_plan()
        (self.source / "handoff.txt").write_text("changed\n")
        self.assertEqual(self.invoke(digest).returncode, 2)
        self.assertFalse(self.intent_file.exists())
        (self.source / "handoff.txt").write_text("approved handoff\n")
        (self.source / "target.txt").write_text("collision\n")
        self.assertEqual(self.invoke(digest).returncode, 2)
        self.assertFalse(self.intent_file.exists())

    def test_refuses_remote_drift_and_plan_hash_drift(self) -> None:
        digest = self.prepare_plan()
        self.assertEqual(self.invoke("0" * 64).returncode, 2)
        self.git(self.source, "push", "-q", "--force", "origin", "main:delivery")
        self.assertEqual(self.invoke(digest).returncode, 2)
        self.assertFalse(self.intent_file.exists())

    def test_existing_intent_is_recovery_boundary(self) -> None:
        digest = self.prepare_plan()
        self.intent_file.write_text("interrupted or prior attempt\n")
        self.assertEqual(self.invoke(digest).returncode, 2)
        self.assertEqual(self.intent_file.read_text(), "interrupted or prior attempt\n")
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "delivery")

    def test_dirty_old_worktree_is_bound_and_preserved(self) -> None:
        (self.old / "target.txt").write_text("retained edit\n")
        digest = self.prepare_plan()
        result = self.invoke(digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        intent = json.loads(self.intent_file.read_text())
        self.assertEqual(intent["retained_old_dirty"][0]["path"], "target.txt")
        self.assertEqual((self.old / "target.txt").read_text(), "retained edit\n")
        self.assertEqual(self.git(self.old, "branch", "--show-current"), "delivery")

    def test_unready_plan_refused(self) -> None:
        digest = self.prepare_plan()
        plan = json.loads(self.plan_file.read_text())
        plan["ready_for_apply"] = False
        self.plan_file.write_text(json.dumps(plan))
        digest = hashlib.sha256(self.plan_file.read_bytes()).hexdigest()
        self.assertEqual(self.invoke(digest).returncode, 2)


if __name__ == "__main__":
    unittest.main()
