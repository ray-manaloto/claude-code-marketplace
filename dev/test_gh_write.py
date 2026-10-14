"""gh:write seam tests (D179, R-174): the CLI and the mise task against a recording gh shim; no network."""

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

from git_delivery import PRIVATE_RULE_ID
from test_issue_create import private_name_sample, secret_sample, use_synthetic_private_rule

ROOT = Path(__file__).resolve().parents[1]
SCRUB = ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "BETTERLEAKS_CONFIG", "BETTERLEAKS_CONFIG_TOML", "GITLEAKS_CONFIG",
         "GITLEAKS_CONFIG_TOML", "GH_TOKEN", "GITHUB_TOKEN", "GH_HOST", "GH_REPO", "GH_SHIM_RC")
SHIM = """#!{python} -I
import json, os, sys
with open(os.environ["GH_SHIM_RECORD"], "w") as record:
    json.dump({{"argv": sys.argv[1:], "stdin": sys.stdin.read()}}, record)
sys.exit(int(os.environ.get("GH_SHIM_RC", "0")))
"""


class GhWrite(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve())
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        use_synthetic_private_rule(self, self.base)  # in os.environ before self.env copies it (D178)
        (self.base / "home").mkdir()
        (self.base / "bin").mkdir()
        (self.base / "bin" / "gh").write_text(SHIM.format(python=sys.executable))
        (self.base / "bin" / "gh").chmod(0o755)
        self.record = self.base / "record.json"
        # The real HOME stays: mise keeps its config trust there. Selectors, scanner config and GitHub
        # credentials are scrubbed, and CODEX_HOME is a scratch tree (.claude/rules/dev-tests.md).
        self.env = {**{k: v for k, v in os.environ.items() if k not in SCRUB},
                    "PATH": os.pathsep.join([str(self.base / "bin"), os.environ["PATH"]]),
                    "CODEX_HOME": str(self.base / "home"), "GH_SHIM_RECORD": str(self.record)}

    def route(self, *args, stdin="", **env):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "dev" / "gh_write.py"), *args], cwd=self.base,
                                input=stdin, env={**self.env, **env}, capture_output=True, text=True, timeout=120)
        return result.returncode, result.stdout + result.stderr

    def test_a_scan_hit_refuses_by_position_and_rule_before_gh_runs(self):
        cases = (  # (gh args, file text, stdin, refused field, rule)
            (["issue", "comment", "12", "--body", "note {private}"], "", "", "arg 5", PRIVATE_RULE_ID),
            (["pr", "comment", "4", "--body-file", "c.md"], "{secret}", "", "arg 5 file", "aws-access-key-id"),
            (["issue", "create", "-t", "t", "-F", "c.md"], "{private}", "", "arg 6 file", PRIVATE_RULE_ID),
            (["api", "repos/o/r/issues/1/comments", "-F", "body=@c.md"], "{secret}", "", "arg 4 file",
             "aws-access-key-id"),
            (["api", "-X", "POST", "repos/o/r/issues", "--input=c.md"], "{private}", "", "arg 5 file",
             PRIVATE_RULE_ID),
            (["issue", "comment", "1", "--body-file", "-"], "", "{secret}", "arg 5 stdin", "aws-access-key-id"),
        )
        samples = {"private": private_name_sample(), "secret": secret_sample()}
        for index, (args, text, stdin, field, rule) in enumerate(cases):
            with self.subTest(case=index):
                (self.base / "c.md").write_text(text.format(**samples))
                rc, out = self.route(*[arg.format(**samples) for arg in args], stdin=stdin.format(**samples))
                self.assertFalse(any(sample in out for sample in samples.values()), "fixture text leaked into output")
                self.assertEqual((rc, out.splitlines()), (2, [
                    f"REFUSED: secret scan hit: local id gh:write, field {field}, rule {rule}; nothing sent"]))
                self.assertFalse(self.record.exists(), "gh ran after a scan hit")

    def test_clean_text_runs_gh_with_the_same_argv_stdin_and_exit(self):
        (self.base / "c.md").write_text("clean body\n")
        args = ["pr", "comment", "4", "--body-file", "c.md", "-b", "plain -- words", "--input", "-"]
        rc, out = self.route(*args, stdin="piped text\n", GH_SHIM_RC="3")
        self.assertEqual((rc, out), (3, ""))
        self.assertEqual(json.loads(self.record.read_text()), {"argv": args, "stdin": "piped text\n"})
        rc, _ = self.route("issue", "view", "12", stdin="ignored")
        self.assertEqual((rc, json.loads(self.record.read_text())), (0, {"argv": ["issue", "view", "12"], "stdin": ""}))

    def test_fail_closed_on_an_unreadable_file_or_a_missing_scanner(self):
        os.mkfifo(self.base / "pipe")
        rc, out = self.route("issue", "comment", "1", "--body-file", "pipe")
        self.assertEqual((rc, out.splitlines()), (2, ["REFUSED: arg 5 names a file the scan cannot read; nothing sent"]))
        rc, out = self.route("issue", "comment", "1", "-b", "x", MARKETPLACE_MISE_BIN=str(self.base / "absent"))
        self.assertEqual((rc, out.splitlines()), (2, ["REFUSED: pinned betterleaks scanner unavailable; nothing sent"]))
        self.assertFalse(self.record.exists(), "gh ran without a completed scan")

    def test_the_mise_task_passes_the_gh_args_through(self):
        args = ["api", "-X", "POST", "repos/o/r/issues", "-f", "title=a b"]
        result = subprocess.run([str(ROOT / "dev" / "mise"), "run", "-q", "gh:write", "--", *args], cwd=self.base,
                                env={**self.env, "UV_OFFLINE": "1"}, capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        self.assertEqual(json.loads(self.record.read_text())["argv"], args)


@unittest.skipUnless(shutil.which("codex"), "codex is not installed")
class CodexRules(unittest.TestCase):
    """`codex execpolicy check` over the project rules: raw gh write prefixes are forbidden, naming the route."""

    FORBIDDEN = ("gh issue comment 12 --body x", "gh issue create", "gh issue edit 3", "gh issue close 3",
                 "gh issue reopen 3", "gh pr create --fill", "gh pr edit 4", "gh pr comment 4 -b x",
                 "gh pr review 4 --approve", "gh pr close 4", "gh pr merge 4", "gh pr ready 4", "gh release create v1",
                 "gh gist create f.txt", "gh label create bug", "gh repo edit", "gh repo deploy-key add k.pub",
                 "gh api -X POST repos/o/r/issues", "gh api --method PATCH repos/o/r", "gh api -XDELETE repos/o/r",
                 "gh api --method=PUT repos/o/r/topics", "gh api -Xpost repos/o/r/issues", "gh api -Xdelete repos/o/r")
    ALLOWED = ("gh issue view 12", "gh pr list", "gh pr diff 4", "gh api repos/o/r", "gh api -X GET search/issues",
               "./dev/mise run gh:write -- issue comment 1 -b x")

    def check(self, command):
        with tempfile.TemporaryDirectory() as home:
            result = subprocess.run([shutil.which("codex"), "execpolicy", "check", "--rules",
                                     str(ROOT / ".codex" / "rules" / "gh-write.rules"), "--", *shlex.split(command)],
                                    env={"PATH": os.environ["PATH"], "HOME": home, "CODEX_HOME": home},
                                    capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr[-2000:])
        return json.loads(result.stdout)

    def test_raw_gh_write_prefixes_are_forbidden_and_reads_pass(self):
        for command in self.FORBIDDEN:
            with self.subTest(command=command):
                result = self.check(command)
                self.assertEqual(result.get("decision"), "forbidden", result)
                for rule in result["matchedRules"]:
                    self.assertIn("./dev/mise run gh:write -- <gh args>", rule["prefixRuleMatch"]["justification"])
        for command in self.ALLOWED:
            with self.subTest(command=command):
                self.assertEqual(self.check(command), {"matchedRules": []})


if __name__ == "__main__":
    unittest.main()
