# gate-git-path retrospective: deny gates and retro gate resolve git outside the mise shims (D129)

Unit `gate-git-path`, branch `claude/gate-git-path-fix`, base `c33ba4e` (the allocation commit;
`allocated_from` `21af565`), worktree `.claude/worktrees/gate-git-path`. Commits: `976a093`
(implementation, 4 files, +126/-2), `4219a85` (GGP-1 fix), then the retro commit carrying this
record. Implementer: Opus 5.5, high (trailer `Claude Opus 5.5`, matching `writer_model`).
Reviews: cold, read-only, Fable 5.1, high: review 1 FAIL (GGP-1 P1, GGP-2 P2, GGP-3 P3, GGP-4 P3);
review 2 of `4219a85` PASS-with-P3 (GGP-5, GGP-6). Retro writer: Fable 5.1, high, inside the
worktree, editing this file only; the retro commit's trailer names Fable (steering row below).

Exits re-run by the retro on `4219a85`, `VIRTUAL_ENV` unset, hk 2.6.0 present (`HkHooks` ran):
`python3 -I -m unittest discover -s dev -p test_hooks.py` 16 tests OK rc 0;
`python3 -I -m unittest discover -s dev -p test_retro_gate.py` 20 tests OK rc 0; both resolvers
return `/usr/bin/git` on this host (`~/.local/share/mise/shims/git -> ~/.local/bin/mise` is
skipped). Implementer exits (`metrics/agent-runs.jsonl` rows 11 and 17): tests OK, `check` rc 0,
`check:acceptance-baseline` rc 0 after each commit. On this record before its commit:
`./dev/mise run retro:gate -- gate-git-path` rc 0, `./dev/mise run check` rc 0; the handoff
repeats both on the commit. Not run by the lane: `check:research` (parent-run, serialized).

## Timing receipt (GGP-2 applied, GGP-5 bound)

Method (R8 section 6, `gatebench4.py`): each gate runs 33 times under the worktree's
`.venv/bin/python -I`, the first 3 runs are dropped, median and p90 of 30; the first `git` on
PATH is the mise shim (`path_git_first`); `before` is a clone at `c33ba4e`, `after` is the lane
worktree. Files in the session scratchpad
`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/bench/`:

| File | SHA-256 | Result (median ms, before to after; p90 in parentheses) |
| --- | --- | --- |
| `gatebench4-integration-fix.json` | `7422b992ebfb30e8fcdd64171ab2add14b344a4209bf074c0e93bf6a2cc5c3d8` | cwd the integration clone at `c33ba4e` (allow path, empty stdout): PreToolUse `git push origin HEAD` 385.4 to 57.5 (404.9 to 61.0); Stop 200.6 to 49.4 (211.0 to 52.2); SubagentStop 381.5 to 63.1 (414.0 to 70.2); rc 0 and identical stdout before and after. |
| `gatebench3-fix.json` | `7661f418099f44f44c0023c1a32868d951e419892a5c61167020926c637ff725` | cwd the lane worktree (deny path: PreToolUse deny and SubagentStop block each spawn the retro-gate child): PreToolUse 418.7 to 101.4; Stop 209.6 to 49.6; SubagentStop 430.5 to 101.0; stdout identical before and after per gate. |
| `gatebench3.py` | `4eadd24eeeaafbabdcf6bf02bd1c0a38f1dea6960889b8e11b90fccb78999071` | the deny-path script |
| `gatebench4.py` | `73e1e9b75620ccff0eee40c2c65a0f1f64b26f7a371cba50d91cfba90b97d045` | the same script with a `cwd` argument |

Binding to `4219a85`: the JSONs were written at 10:04:57 and 10:05:35 from the worktree whose
next commit, 43 s and 5 s later, is `4219a85` (10:05:40); the worktree carries no uncommitted
change. R8's figures on this host were 401.0 to 54.6, 228.5 to 45.8 and 373.1 to 62.1.

## Findings

| Severity | Category and finding (source) | Action, verification and disposition |
| --- | --- | --- |
| P1 | Automated checks: GGP-1, a shim-only host turned the three settings hooks fail-open. `976a093`'s resolver returned None when PATH held only shims, and `pretooluse_gate.py`, `stop_gate.py` and `subagent_stop_gate.py` exit 0 with no output when `git(..., "rev-parse", "--show-toplevel")` is None. Its test `test_only_shims_on_path_fails_closed_without_running_them` asserted the `git_gate.py` CLI usage exit (rc 1) and the retro gate's rc 1, seams the hooks never see (review 1; `976a093` diff). | Applied in `4219a85`: the resolver keeps the first skipped shim and returns it when no other git exists (slow, enforcing); the shim-only tests run a recording shim that execs the real git and assert deny, block, rc 2 and that the shim ran. Retro re-run: 16 and 20 tests OK rc 0. Review 2 PASS. Judgement learning: a property a test names is asserted at every seam that carries it; proposed, owner parent, `CODING_STANDARDS.md` (parent edit 1). |
| P2 | Automated checks: `dev/test_retro_gate.py` (20 tests, a required check of this lane and of CT-01) is reached by neither route `.claude/rules/dev-tests.md` allows: `dev/check.py` discovers only `test_research_*.py` and `research_refresh/test_*.py`, `mise.dev.toml` has no `test:retro-gate` task, `check:research` and the hosted workflows (`research-fast.yml` runs `check:research`; `development.yml` runs `check.py`) never run it. The lane and the CT-01 retro ran it by hand. | Mechanical, destination `mise.dev.toml` (an excluded shared path). Verified in the worktree with parent edit 2 applied, then reverted: `./dev/mise tasks validate` rc 0 (57 tasks), `./dev/mise run test:retro-gate` OK rc 0, `./dev/mise tasks deps check:research` lists it. Deferred, owner parent: apply at the `mise.dev.toml` integration (w0-doctor owns the file this wave) and rerun `tasks validate`. |
| P2 | Automated checks: GGP-2, no timing receipt for the three gates before and after (review 1; lane record `delivers` 3). | Applied: the receipt section above, two JSON files and two scripts bound by SHA-256 and to `4219a85` (GGP-5). R8's proposed mechanical timing check ("Stop under 60 ms on this host") is rejected: the figure is host- and load-bound (49.4 here, 45.8 in R8), so a threshold gate would flake; the deterministic proxy already in both suites is the marker assertion that no gate executed the shim. |
| P3 | Navigation: GGP-3, the allocation record committed in `c33ba4e` (on the integration branch) has `base_sha` null, `checks` for `required_checks` and no `resource_admissions` or `created_at`; `.claude/rules/planning-records.md` lists the keys and nothing checks them (`git_gate.lanes()` and `retro_gate.lane_unit()` read `unit` and `branch` only). The parent's working copy is corrected and uncommitted. Across the corpus, 5 of 16 records lack `import_source` and one lacks `excluded_shared_paths`, so a check of the rule's full list would fail today; the six keys the gates, reviewer and merger rely on pass 16 of 16 in the parent's checkout. | Mechanical, destination `dev/check.py` (parent edit 3). Verified in the worktree with the hunk applied, then reverted: `python3 -B dev/check.py` fails with `Lane record lacks base_sha, required_checks: .planning/.../lanes/gate-git-path.json` (it catches the committed defect); the same loop over the parent's corrected `lanes/` passes 16 of 16. Deferred, owner parent: commit the corrected record in the same or an earlier commit as the hunk, else `check` fails on the integration branch. The null `base_sha` follows from the record's `base_rule` (a commit cannot name itself): parent edit 4 proposes the rule wording. |
| P3 | Steering: the brief and `delivers` 1 called the resolver's None "the existing None or refusal behaviour (fail closed)"; the hooks' None branch allows (GGP-4), and the implementer tested the claim at the CLI seam only (P1 above). After `4219a85` None means no git at all on PATH. | GGP-4 deferred, owner CT-02b.1 (wave 18, the first writer of `dev/hooks/**`; the three hook scripts are excluded shared paths here), with R8's second item: `onFailure: block` does not apply to Stop and SubagentStop, so fail-closed there needs another mechanism. The learning is parent edit 1. |
| P3 | Steering: the retro brief asked for a `Claude Opus 5.5` trailer on this commit; `.claude/rules/planning-records.md` says the trailer names the model that wrote and the lane record's `retro_writer` says fable. | Applied: the retro commit's trailer names `Claude Fable 5.1`; verification `git log -1 --format=%B` on the retro commit. No rule change: the rule already says this. |
| P3 | Automated checks: GGP-6, `dev/test_hooks.py:266-268` discards the PreToolUse rc in the shim-only test and the test skips `subagent_stop_gate.py` (review 2). | Literal test-only edit (parent edit 5) verified in the worktree, then reverted: `GitResolution` 2 tests OK rc 0 with the rc tuple and the SubagentStop block asserted. Deferred, owner parent at integration (apply from the edit; focused re-review at the parent's choice), else the implementer at the next touch of the file (CT-02b.1) as review 2 disposed. The retro wrote only this record, per the brief. |
| P3 | Coding standards: `git_executable()` is copied between `dev/hooks/git_gate.py` and `dev/retro_gate.py` (both docstrings say so; `git_gate` spawns `retro_gate`, and `retro_gate` runs standalone under `-I`, so neither imports the other). A drift between the copies would re-open GGP-1 in one gate only. | Mechanical drift guard (parent edit 6) verified in the worktree, then reverted: the test passes on `4219a85`; a one-token mutation of `retro_gate.py`'s copy fails it. Deferred, owner parent at integration (`dev/test_retro_gate.py`, git-resolution tests). |
| P3 | Navigation: the shim gotcha lives only in two docstrings and two test comments (`GIT_DIR`); `dev/AGENTS.md` "Writing a helper" is silent, so the next per-call gate or test author re-measures it. | Proposed, owner parent: the one-line bullet in parent edit 7 (`dev/AGENTS.md` is outside `owned_paths`). |
| P3 | Information access: the timing receipts live in the session scratchpad, not the repository; the two review verdicts (GGP-1 to GGP-6) exist only in the parent's transcript and `metrics/agent-runs.jsonl` rows 13 and 18, and the lane record's `review` is null. | This record inlines the medians and the four hashes, and restates the six findings with their dispositions. Deferred, owner parent at receipt: copy the four bench files under `reviews/ccm-20261014/research5/` (parent-owned) and set the lane record's `review`; both are outside `owned_paths`. |

Tool economy: none, because the lane's runs (`metrics/agent-runs.jsonl`) were 28 tool uses in
468 s for the implementation, 15 for review 1, 5 for the fix (125k tokens, a resumed context) and
12 for review 2; the only waste was a second bench script differing by one argument, which stayed
in scratch. The retro spent about 12 batched calls; one `cat` of R8 overflowed the output cap and
was re-read by section.

No-ops: the `976a093` shim-only test was a no-op for the property its name claimed (P1 row);
`4219a85` replaced it. No instruction was removed, and the new docstrings state only the shim rule
and the copy relationship.

Global guidance (`AGENTS.md`, `CLAUDE.md`, rules, skills, agents): none changed in the lane; the
proposals above name their files, owners and literal text below.

## Parent edits (outside `owned_paths`; literal, apply unread)

1. `CODING_STANDARDS.md`, section Tests, after rule 2 (number at the parent's choice; the
   w0-decisions rule 14 proposal pends as D48):
   `A test named for a property (fail closed, deny, block) asserts it at every seam that carries it: a usage exit at one CLI seam is not a refusal at a hook seam.`
2. `mise.dev.toml`: in `[tasks."check:research"]` replace
   `"test:codex-session-history", "test:hooks"]` with
   `"test:codex-session-history", "test:hooks", "test:retro-gate"]`, and append after
   `[tasks."test:hooks"]`:
   ```toml
   [tasks."test:retro-gate"]
   description = "Exercise the retro gate CLI, unit derivation and git resolution in scratch repositories"
   dir = "{{config_root}}"
   run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p test_retro_gate.py -v'
   ```
3. `dev/check.py`: replace
   `counts = {"json": 0, "toml": 0, "python": 0, "shell": 0, "baseline": 0}` with
   `counts = {"json": 0, "toml": 0, "python": 0, "shell": 0, "lane": 0, "baseline": 0}`, and
   insert before `    if baseline:`:
   ```python
       for path in sorted((ROOT / ".planning").glob("*/lanes/*.json")):
           lane = json.loads(path.read_text())
           missing = [key for key in ("unit", "branch", "base_sha", "owned_paths", "required_checks", "status") if not lane.get(key)]
           if missing:
               raise ValueError(f"Lane record lacks {', '.join(missing)}: {path.relative_to(ROOT)} (.claude/rules/planning-records.md)")
           counts["lane"] += 1

   ```
   Commit the corrected `lanes/gate-git-path.json` with or before this hunk.
4. `.claude/rules/planning-records.md`, first bullet, after "The parent writes it at allocation;":
   `\`base_sha\` is the integration tip the lane is allocated from (\`allocated_from\`), since the commit that adds the record cannot name itself; the worktree is cut from that allocation commit, so \`git log <base_sha>..HEAD\` starts with the record.`
5. `dev/test_hooks.py`, in `test_only_shims_on_path_still_enforce_through_the_shim`, replace
   ```python
           self.env["PATH"] = os.pathsep.join([str(self.shims), str(relocated)])
           rc, out = self.hook("pretooluse_gate.py", {"tool_name": "Bash", "cwd": str(self.repo),
                                                      "tool_input": {"command": "git push origin claude/x-y"}})
           self.assertIn('"permissionDecision": "deny"', out)
   ```
   with
   ```python
           self.git("checkout", "-q", "claude/x-y")
           self.env["PATH"] = os.pathsep.join([str(self.shims), str(relocated)])
           rc, out = self.hook("pretooluse_gate.py", {"tool_name": "Bash", "cwd": str(self.repo),
                                                      "tool_input": {"command": "git push origin claude/x-y"}})
           self.assertEqual((rc, json.loads(out)["hookSpecificOutput"]["permissionDecision"]), (0, "deny"), out)
           rc, out = self.hook("subagent_stop_gate.py", {"cwd": str(self.repo)})
           self.assertEqual((rc, json.loads(out)["decision"]), (0, "block"), out)
   ```
6. `dev/test_retro_gate.py`, in `RetroGateUnitDerivation`, before
   `test_only_shims_on_path_still_derive_the_unit_through_the_shim`:
   ```python
       def test_git_resolver_matches_the_hook_copy(self):
           """dev/hooks/git_gate.py keeps the same resolver with no shared import; the code after the docstring stays identical."""
           def body(path):
               text = (ROOT / path).read_text()
               start = text.index("def git_executable()")
               return text[text.index('"""', text.index('"""', start) + 3) + 3:text.index("\ndef git(", start)]
           self.assertEqual(body("dev/retro_gate.py"), body("dev/hooks/git_gate.py"))

   ```
7. `dev/AGENTS.md`, section "Writing a helper", after the exit-codes bullet:
   `- A hook or gate that spawns git per call resolves it with \`git_executable()\` (\`dev/hooks/git_gate.py\`; \`dev/retro_gate.py\` keeps a copy): a mise shim costs about 186 ms per call against 9.5 ms for \`/usr/bin/git\`. A test that spawns git puts \`git --exec-path\` first on PATH.`
