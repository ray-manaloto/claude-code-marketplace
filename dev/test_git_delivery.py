"""Scratch-repository contract tests for the A09 public command."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


HELPER = Path(__file__).with_name("git_delivery.py")
ROOT = HELPER.parent.parent


class DeliveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="a09-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        # Hermetic Git: no caller GIT_* state, no user or system config, scratch HOME.
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env["PATH"] = os.pathsep.join(("/usr/bin", "/bin", self.env.get("PATH", "")))
        self.env.update(HOME=str(self.base / "home"), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.repo = self.base / "repo"
        self.remote = self.base / "remote.git"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "A09 Test")
        self.git("config", "user.email", "a09@example.invalid")
        self.git("branch", "-M", "delivery")
        (self.repo / "selected.txt").write_text("base\n")
        (self.repo / "mise.dev.toml").write_text("base\n")
        (self.repo / "dev").mkdir()
        check = self.repo / "dev/mise"
        check.write_text("#!/bin/sh\nexit 0\n")
        check.chmod(0o700)
        self.git("add", "selected.txt", "mise.dev.toml", "dev/mise")
        self.git("commit", "-qm", "base")
        subprocess.run(["git", "init", "--bare", "-q", str(self.remote)], check=True, capture_output=True, env=self.env)
        self.git("remote", "add", "origin", str(self.remote))
        self.head = self.git("rev-parse", "HEAD")
        self.common = str((self.repo / ".git").resolve())
        self.url_hash = hashlib.sha256(str(self.remote).encode()).hexdigest()
        self.hook_hash = self.inspect_hook_hash()

    def inspect_hook_hash(self) -> str:
        argv = [sys.executable, str(HELPER), "inspect-hooks", "--root", str(self.repo),
                "--common-dir", self.common, "--branch", "delivery", "--head", self.head,
                "--remote", "origin", "--remote-url-sha256", self.url_hash]
        result = subprocess.run(argv, cwd=self.repo, text=True, capture_output=True, check=False, env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip().split("=", 1)[1]

    def git(self, *args: str) -> str:
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args], cwd=self.repo, capture_output=True, check=False, env=self.env)
        self.assertEqual(result.returncode, 0, f"scratch git {args[0]}: {result.stderr.decode(errors='replace')}")
        return result.stdout.decode().strip()

    def invoke(self, action: str, *extra: str, overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        values = {
            "root": str(self.repo), "common-dir": self.common,
            "branch": "delivery", "head": self.head,
            "remote": "origin", "remote-url-sha256": self.url_hash,
            "hook-tree-sha256": self.hook_hash,
        }
        values.update(overrides or {})
        argv = [sys.executable, str(HELPER), action]
        for key, value in values.items():
            argv.extend((f"--{key}", value))
        return subprocess.run([*argv, *extra], cwd=self.repo, text=True, capture_output=True, check=False, env=self.env)

    def prepare_selected(self) -> str:
        (self.repo / "selected.txt").write_text("reviewed\n")
        result = self.invoke("prepare", "--path", "selected.txt")
        self.assertEqual(result.returncode, 0, result.stderr)
        return dict(line.split("=", 1) for line in result.stdout.splitlines())["index_tree"]

    def test_prepare_refuses_identity_and_staged_extras(self) -> None:
        (self.repo / "selected.txt").write_text("reviewed\n")
        bad = (
            {"head": "0" * 40},
            {"common-dir": str(self.base)},
            {"remote-url-sha256": "0" * 64},
            {"branch": "other"},
        )
        for overrides in bad:
            with self.subTest(overrides=overrides):
                result = self.invoke("prepare", "--path", "selected.txt", overrides=overrides)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.git("diff", "--cached", "--name-only"), "")
        self.git("add", "mise.dev.toml")
        (self.repo / "mise.dev.toml").write_text("extra\n")
        self.git("add", "mise.dev.toml")
        self.assertEqual(self.invoke("prepare", "--path", "selected.txt").returncode, 2)

    def test_prepare_rejects_pathspec_magic_mixed_files_and_pushurl_divergence(self) -> None:
        (self.repo / "selected.txt").write_text("reviewed\n")
        for path in (":(top)*", "*.txt", "mise.dev.toml"):
            with self.subTest(path=path):
                self.assertEqual(self.invoke("prepare", "--path", path).returncode, 2)
                self.assertEqual(self.git("diff", "--cached", "--name-only"), "")
        second = self.base / "other.git"
        subprocess.run(["git", "init", "--bare", "-q", str(second)], check=True, capture_output=True, env=self.env)
        self.git("config", "remote.origin.pushurl", str(second))
        self.assertEqual(self.invoke("prepare", "--path", "selected.txt").returncode, 2)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    def test_stage_blob_and_prepare_preserve_mixed_working_file(self) -> None:
        (self.repo / "mise.dev.toml").write_text("reviewed\npaused\n")
        source = self.base / "reviewed.toml"
        source.write_text("reviewed\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        result = self.invoke("stage-blob", "--path", "mise.dev.toml", "--content-file", str(source), "--content-sha256", digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        blob = result.stdout.strip().split("=", 1)[1]
        self.assertEqual(self.git("show", ":mise.dev.toml"), "reviewed")
        self.assertEqual((self.repo / "mise.dev.toml").read_text(), "reviewed\npaused\n")
        (self.repo / "selected.txt").write_text("selected\n")
        prepared = self.invoke("prepare", "--path", "selected.txt", "--pre-staged", f"mise.dev.toml={blob}")
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        self.assertEqual(set(self.git("diff", "--cached", "--name-only").splitlines()), {"selected.txt", "mise.dev.toml"})
        self.assertEqual(self.invoke("prepare", "--path", "selected.txt", "--pre-staged", f"mise.dev.toml={'0' * 40}").returncode, 2)

    def test_stage_blob_accepts_first_untracked_mixed_file(self) -> None:
        (self.repo / "dev").mkdir(exist_ok=True)
        source = self.base / "reviewed-searches.toml"
        source.write_text("[[result]]\nname = 'reviewed'\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        result = self.invoke("stage-blob", "--path", "dev/saved-searches.toml",
                             "--content-file", str(source), "--content-sha256", digest)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", ":dev/saved-searches.toml"), source.read_text().strip())
        self.assertFalse((self.repo / "dev/saved-searches.toml").exists())

    def test_hook_tree_drift_refuses_before_staging(self) -> None:
        (self.repo / "selected.txt").write_text("reviewed\n")
        hook = self.repo / ".git/hooks/pre-push"
        hook.write_text("#!/bin/sh\nexit 0\n")
        hook.chmod(0o700)
        result = self.invoke("prepare", "--path", "selected.txt")
        self.assertEqual(result.returncode, 2)
        self.assertIn("hook preimage drift", result.stderr)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    def test_config_hook_drift_refuses_before_staging(self) -> None:
        (self.repo / "selected.txt").write_text("reviewed\n")
        self.git("config", "hook.review.event", "reference-transaction")
        self.git("config", "hook.review.command", "/usr/bin/true")
        self.assertEqual(self.invoke("inspect-hooks").returncode, 2)
        result = self.invoke("prepare", "--path", "selected.txt")
        self.assertEqual(result.returncode, 2)
        self.assertIn("configured Git hook could execute", result.stderr)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    # The user-global hk layout (D154): one hook.hk-<event> section per event.
    HK_EVENTS = ("pre-commit", "commit-msg", "prepare-commit-msg", "pre-push", "pre-merge-commit", "post-commit")

    def use_global_hooks(self, *events: str) -> None:
        home = Path(self.env["HOME"])
        home.mkdir(exist_ok=True)
        config = home / ".gitconfig"
        config.write_text("".join(
            f'[hook "hk-{event}"]\n\tcommand = hk run {event} --from-hook\n\tevent = {event}\n'
            for event in events
        ))
        self.env["GIT_CONFIG_GLOBAL"] = str(config)

    def test_inspect_hooks_admits_global_hk_layout(self) -> None:
        self.use_global_hooks(*self.HK_EVENTS)
        result = self.invoke("inspect-hooks")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"\Ahook_tree_sha256=[0-9a-f]{64}\n\Z")

    def test_inspect_hooks_refuses_unknown_global_event(self) -> None:
        for event in ("post-checkout", "reference-transaction"):
            with self.subTest(event=event):
                self.use_global_hooks(*self.HK_EVENTS, event)
                result = self.invoke("inspect-hooks")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "A09 refused: configured Git hook could execute during delivery\n")

    def test_stage_blob_rejects_symlink_target_and_selected_symlink_mode(self) -> None:
        source = self.base / "reviewed.toml"
        source.write_text("reviewed\n")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        (self.repo / "mise.dev.toml").unlink()
        (self.repo / "mise.dev.toml").symlink_to("selected.txt")
        self.assertEqual(self.invoke("stage-blob", "--path", "mise.dev.toml", "--content-file", str(source), "--content-sha256", digest).returncode, 2)
        (self.repo / "selected.txt").unlink()
        (self.repo / "selected.txt").symlink_to("mise.dev.toml")
        self.git("add", "selected.txt")
        tree = self.git("write-tree")
        message = self.base / "message"
        message.write_text("message\n")
        self.assertEqual(self.invoke("publish", "--path", "selected.txt", "--index-tree", tree,
                                     "--message-file", str(message), "--check-task", "check",
                                     "--gitleaks-bin", str(source)).returncode, 2)

    def test_publish_refuses_selected_drift_failing_check_and_scan_finding(self) -> None:
        tree = self.prepare_selected()
        message = self.base / "message.txt"
        message.write_text("selected change\n")
        scanner = self.base / "scanner"
        scanner.write_text("#!/bin/sh\nexit 1\n")
        scanner.chmod(0o700)
        (self.repo / "dev").mkdir(exist_ok=True)
        check = self.repo / "dev/mise"
        check.write_text("#!/bin/sh\nexit 7\n")
        check.chmod(0o700)
        options = ("--path", "selected.txt", "--index-tree", tree, "--message-file", str(message),
                   "--check-task", "check", "--gitleaks-bin", str(scanner))
        (self.repo / "selected.txt").write_text("drift\n")
        self.assertEqual(self.invoke("publish", *options).returncode, 2)
        (self.repo / "selected.txt").write_text("reviewed\n")
        self.assertIn("rc=7", self.invoke("publish", *options).stderr)
        check.write_text("#!/bin/sh\nexit 0\n")
        finding = self.invoke("publish", *options)
        self.assertEqual(finding.returncode, 2)
        self.assertIn("independent owner adjudication", finding.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery"), "")

    def test_publish_uses_hook_free_exact_sha_push(self) -> None:
        tree = self.prepare_selected()
        message = self.base / "message"
        message.write_text("reviewed change\n")
        scanner = self.base / "scanner"
        scanner.write_text("#!/bin/sh\nexit 0\n")
        scanner.chmod(0o700)
        (self.repo / "dev").mkdir(exist_ok=True)
        check = self.repo / "dev/mise"
        check.write_text("#!/bin/sh\nexit 0\n")
        check.chmod(0o700)
        marker = self.base / "hook-ran"
        hook = self.repo / ".git/hooks/reference-transaction"
        hook.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
        hook.chmod(0o700)
        configured_marker = self.base / "configured-hook-ran"
        for event in self.HK_EVENTS:  # every admitted event; none may fire on the publish path
            self.git("config", f"hook.safe-{event}.event", event)
            self.git("config", f"hook.safe-{event}.command", f"echo {event} >> '{configured_marker}'")
        result = self.invoke("publish", "--path", "selected.txt", "--index-tree", tree,
                             "--message-file", str(message), "--check-task", "check",
                             "--gitleaks-bin", str(scanner),
                             overrides={"hook-tree-sha256": self.inspect_hook_hash()})
        self.assertEqual(result.returncode, 0, result.stderr)
        published = dict(line.split("=", 1) for line in result.stdout.splitlines())["published"]
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery").split()[0], published)
        self.assertFalse(marker.exists())
        self.assertFalse(configured_marker.exists(), configured_marker.exists() and configured_marker.read_text())

    def test_publish_checks_staged_mixed_config(self) -> None:
        (self.repo / "mise.dev.toml").write_text("good\n")
        source = self.base / "reviewed-mise.toml"
        source.write_text("bad\n")
        staged = self.invoke("stage-blob", "--path", "mise.dev.toml",
                             "--content-file", str(source),
                             "--content-sha256", hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(staged.returncode, 0, staged.stderr)
        oid = dict(line.split("=", 1) for line in staged.stdout.splitlines())["blob"]
        (self.repo / "selected.txt").write_text("reviewed\n")
        check = self.repo / "dev/mise"
        check.write_text("#!/bin/sh\n[ \"$(cat mise.dev.toml)\" = bad ] && exit 23\nexit 0\n")
        check.chmod(0o700)
        options = ("--pre-staged", f"mise.dev.toml={oid}", "--path", "selected.txt", "--path", "dev/mise")
        prepared = self.invoke("prepare", *options)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        tree = dict(line.split("=", 1) for line in prepared.stdout.splitlines())["index_tree"]
        message = self.base / "message"
        message.write_text("reviewed change\n")
        result = self.invoke("publish", *options, "--index-tree", tree,
                             "--message-file", str(message), "--check-task", "check",
                             "--gitleaks-bin", str(self.base / "scanner"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("rc=23", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery"), "")

    def test_scratch_validation_ignores_inherited_configured_hook(self) -> None:
        tree = self.prepare_selected()
        marker = self.base / "inherited-hook-ran"
        self.env.update({
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "hook.inherited.event",
            "GIT_CONFIG_VALUE_0": "pre-commit",
            "GIT_CONFIG_KEY_1": "hook.inherited.command",
            "GIT_CONFIG_VALUE_1": f"touch {marker}",
        })
        self.hook_hash = self.inspect_hook_hash()
        message = self.base / "message"
        message.write_text("reviewed change\n")
        scanner = self.base / "scanner"
        scanner.write_text("#!/bin/sh\nexit 0\n")
        scanner.chmod(0o700)
        result = self.invoke("publish", "--path", "selected.txt", "--index-tree", tree,
                             "--message-file", str(message), "--check-task", "check",
                             "--gitleaks-bin", str(scanner))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())

    def test_scratch_validation_runs_source_pinned_installs(self) -> None:
        # dev/mise pins MISE_DATA_DIR to <checkout>/.mise; the copy must reach the source's installs.
        pinned = self.repo / ".mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks"
        check = self.repo / "dev/mise"
        check.write_text(
            "#!/bin/sh\n[ \"$*\" = 'run test:delivery' ] || exit 0\n"
            "bin=\"$(cd \"$(dirname \"$0\")/..\" && pwd -P)/.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks\"\n"
            f"[ \"$bin\" -ef '{pinned}' ] && [ \"$(\"$bin\" version)\" = 1.9.0 ] || exit 31\n")
        check.chmod(0o700)
        (self.repo / "selected.txt").write_text("reviewed\n")
        options = ("--path", "selected.txt", "--path", "dev/mise")
        prepared = self.invoke("prepare", *options)
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        tree = dict(line.split("=", 1) for line in prepared.stdout.splitlines())["index_tree"]
        message = self.base / "message"
        message.write_text("reviewed change\n")
        scanner = self.base / "scanner"
        scanner.write_text("#!/bin/sh\nexit 0\n")
        scanner.chmod(0o700)
        options += ("--index-tree", tree, "--message-file", str(message),
                    "--check-task", "check", "--gitleaks-bin", str(scanner))
        missing = self.invoke("publish", *options)
        self.assertEqual(missing.returncode, 2)
        self.assertIn("selected-tree run test:delivery: command failed (rc=31)", missing.stderr)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery"), "")
        pinned.parent.mkdir(parents=True)
        pinned.write_text("#!/bin/sh\necho 1.9.0\n")
        pinned.chmod(0o700)
        result = self.invoke("publish", *options)
        self.assertEqual(result.returncode, 0, result.stderr)
        published = dict(line.split("=", 1) for line in result.stdout.splitlines())["published"]
        self.assertEqual(self.git("rev-parse", f"{published}^{{tree}}"), tree)

    def test_scratch_validation_refuses_export_ignored_tree(self) -> None:
        (self.repo / ".gitattributes").write_text("selected.txt export-ignore\n")
        (self.repo / "selected.txt").write_text("reviewed\n")
        prepared = self.invoke("prepare", "--path", ".gitattributes", "--path", "selected.txt")
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        tree = dict(line.split("=", 1) for line in prepared.stdout.splitlines())["index_tree"]
        message = self.base / "message"
        message.write_text("reviewed change\n")
        result = self.invoke("publish", "--path", ".gitattributes", "--path", "selected.txt",
                             "--index-tree", tree, "--message-file", str(message),
                             "--check-task", "check", "--gitleaks-bin", str(self.base / "scanner"))
        self.assertEqual(result.returncode, 2)
        self.assertIn("scratch validation tree differs", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.head)

    def test_reviewed_baseline_refuses_new_fingerprint(self) -> None:
        tree = self.prepare_selected()
        message = self.base / "message"
        message.write_text("reviewed change\n")
        (self.repo / "dev").mkdir(exist_ok=True)
        check = self.repo / "dev/mise"
        check.write_text("#!/bin/sh\nexit 0\n")
        check.chmod(0o700)
        report_dir = self.repo / "evidence"
        report_dir.mkdir()
        baseline = report_dir / "known.json"
        baseline.write_text(json.dumps([{"Fingerprint": "known"}]))
        receipt = report_dir / "adjudication.json"
        receipt.write_text(json.dumps({
            "schema_version": 1, "pre_baseline_exit_code": 1, "pre_baseline_finding_count": 1,
            "adjudication_status": "independently_reviewed_pending_publish_gate",
            "scanned_head": self.head, "decision": "Treat these exact known findings as false positives",
            "baseline_report": {"path": "evidence/known.json", "sha256": hashlib.sha256(baseline.read_bytes()).hexdigest()},
            "independent_read_only_triage": {"reviewer": "reviewer", "finding_count": 1},
        }))
        scanner = self.base / "scanner"
        scanner.write_text("#!/bin/sh\ncase \"$*\" in *--pre-commit*) exit 0;; *--baseline-path*) exit 0;; *) printf '[{\"Fingerprint\":\"new\"}]'; exit 1;; esac\n")
        scanner.chmod(0o700)
        result = self.invoke("publish", "--path", "selected.txt", "--index-tree", tree,
                             "--message-file", str(message), "--check-task", "check",
                             "--gitleaks-bin", str(scanner), "--adjudication-file", str(receipt),
                             "--adjudication-sha256", hashlib.sha256(receipt.read_bytes()).hexdigest())
        self.assertEqual(result.returncode, 2)
        self.assertIn("differ from the exact reviewed baseline", result.stderr)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery"), "")

    def test_reviewed_baseline_preserves_raw_rc_and_allows_only_exact_known_set(self) -> None:
        tree = self.prepare_selected()
        message = self.base / "message"
        message.write_text("reviewed change\n")
        (self.repo / "dev").mkdir(exist_ok=True)
        check = self.repo / "dev/mise"
        check.write_text("#!/bin/sh\nexit 0\n")
        check.chmod(0o700)
        evidence = self.repo / "evidence"
        evidence.mkdir()
        baseline = evidence / "known.json"
        baseline.write_text(json.dumps([{"Fingerprint": "known"}]))
        receipt = evidence / "adjudication.json"
        receipt.write_text(json.dumps({
            "schema_version": 1, "pre_baseline_exit_code": 1, "pre_baseline_finding_count": 1,
            "adjudication_status": "independently_reviewed_pending_publish_gate",
            "scanned_head": self.head, "decision": "Treat these exact known findings as false positives",
            "baseline_report": {"path": "evidence/known.json", "sha256": hashlib.sha256(baseline.read_bytes()).hexdigest()},
            "independent_read_only_triage": {"reviewer": "reviewer", "finding_count": 1},
        }))
        scanner = self.base / "scanner"
        scanner.write_text("#!/bin/sh\ncase \"$*\" in *--pre-commit*) exit 0;; *--baseline-path*) exit 0;; *) printf '[{\"Fingerprint\":\"known\"}]'; exit 1;; esac\n")
        scanner.chmod(0o700)
        result = self.invoke("publish", "--path", "selected.txt", "--index-tree", tree,
                             "--message-file", str(message), "--check-task", "check",
                             "--gitleaks-bin", str(scanner), "--adjudication-file", str(receipt),
                             "--adjudication-sha256", hashlib.sha256(receipt.read_bytes()).hexdigest())
        self.assertEqual(result.returncode, 0, result.stderr)
        output = dict(line.split("=", 1) for line in result.stdout.splitlines())
        self.assertEqual(output["history_scan_rc"], "1")
        self.assertEqual(output["baseline_residual_rc"], "0")
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery").split()[0], output["published"])


    def recording_scanner(self, label: str = "calls") -> tuple[Path, Path]:
        calls = self.base / label
        calls.mkdir()
        scanner = self.base / f"{label}-scanner"
        scanner.write_text(f"#!/bin/sh\nout='{calls}'/$$\nprintf '%s\\n' \"$@\" > \"$out.argv\"\nenv > \"$out.env\"\nexit 0\n")
        scanner.chmod(0o700)
        return scanner, calls

    def publish_selected(self, scanner: Path, tree: str) -> subprocess.CompletedProcess[str]:
        message = self.base / "message"
        message.write_text("reviewed change\n")
        return self.invoke("publish", "--path", "selected.txt", "--index-tree", tree,
                           "--message-file", str(message), "--check-task", "check",
                           "--gitleaks-bin", str(scanner))

    def test_publish_scanner_never_sees_config_environment(self) -> None:
        names = {"GITLEAKS_CONFIG", "GITLEAKS_CONFIG_TOML", "BETTERLEAKS_CONFIG", "BETTERLEAKS_CONFIG_TOML"}
        self.env.update({name: str(self.base / "foreign.toml") for name in names})
        scanner, calls = self.recording_scanner()
        result = self.publish_selected(scanner, self.prepare_selected())
        self.assertEqual(result.returncode, 0, result.stderr)
        records = sorted(calls.glob("*.env"))
        self.assertEqual(len(records), 2)  # staged scan and outbound history scan
        for record in records:
            seen = {line.split("=", 1)[0] for line in record.read_text().splitlines()}
            self.assertEqual(seen & names, set(), record.name)


    def test_publish_passes_root_config_to_every_scan(self) -> None:
        # betterleaks auto-discovers a root .betterleaks.toml before .gitleaks.toml.
        scanner, calls = self.recording_scanner()
        result = self.publish_selected(scanner, self.prepare_selected())
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = str(self.repo.resolve() / ".gitleaks.toml")
        records = sorted(calls.glob("*.argv"))
        self.assertEqual(len(records), 2)
        for record in records:
            argv = record.read_text().splitlines()
            self.assertIn("--config", argv, record.name)
            self.assertEqual(argv[argv.index("--config") + 1], expected)


    def test_publish_refuses_root_scanner_ignore_file(self) -> None:
        # Both scanners load a root ignore file whatever --gitleaks-ignore-path names.
        tree = self.prepare_selected()
        for name in (".gitleaksignore", ".betterleaksignore"):
            with self.subTest(name=name):
                ignore = self.repo / name
                ignore.write_text("")
                self.addCleanup(ignore.unlink, missing_ok=True)
                scanner, calls = self.recording_scanner(name.lstrip("."))
                result = self.publish_selected(scanner, tree)
                ignore.unlink()
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stderr.count("\n"), 1)
                self.assertIn(f"checkout root holds {name}", result.stderr)
                self.assertEqual(list(calls.iterdir()), [])
                self.assertEqual(self.git("rev-parse", "HEAD"), self.head)
                self.assertEqual(self.git("ls-remote", "--heads", "origin", "delivery"), "")


    def pinned_betterleaks(self) -> str:
        # The mise.dev.toml pin, resolved by the repo's mise, never a PATH lookup.
        with (ROOT / "mise.dev.toml").open("rb") as source:
            version = tomllib.load(source)["tools"]["aqua:betterleaks/betterleaks"]
        env = {key: value for key, value in os.environ.items() if key not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")}
        found = subprocess.run([str(ROOT / "dev/mise"), "which", "betterleaks"], cwd=ROOT, env=env,
                               text=True, capture_output=True, check=False)
        binary = found.stdout.strip()
        if found.returncode or not binary or not Path(binary).is_file():
            missing = f"pinned betterleaks {version} is missing; run ./dev/mise install aqua:betterleaks/betterleaks"
            if os.environ.get("MISE_TASK_NAME") == "test:delivery":
                self.fail(missing)
            self.skipTest(missing)
        reported = subprocess.run([binary, "version"], env={"PATH": "/usr/bin:/bin", "HOME": str(self.base)},
                                  text=True, capture_output=True, check=False)
        self.assertEqual((reported.returncode, reported.stdout.strip()), (0, version), binary)
        return binary

    def test_root_config_reports_lone_aws_access_key_id(self) -> None:
        # betterleaks#408: the default rule needs a paired secret; .gitleaks.toml closes the gap.
        binary = self.pinned_betterleaks()
        config = self.repo / ".gitleaks.toml"
        shutil.copyfile(ROOT / ".gitleaks.toml", config)
        synthetic = "AKIA" + "QX7ZM2NB" + "K4RTW6YP"  # assembled so this file holds no key ID
        documented = "AKIA" + "IOSFODNN7" + "EXAMPLE"
        (self.repo / "leak.txt").write_text(f"id: {synthetic}\ndoc: {documented}\n")
        self.git("add", "leak.txt")
        self.git("commit", "-qm", "fixture")
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.base), "GIT_CONFIG_GLOBAL": os.devnull}
        result = subprocess.run([binary, "git", "--no-banner", "--redact=100", "--log-level=error",
                                 "--config", str(config), "--report-format=json", "--report-path=-",
                                 "--log-opts=HEAD~1..HEAD", str(self.repo)],
                                cwd=self.repo, env=env, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 1, result.stderr)
        rules = [finding["RuleID"] for finding in json.loads(result.stdout)]
        self.assertEqual(rules.count("aws-access-key-id"), 1, rules)


if __name__ == "__main__":
    unittest.main()
