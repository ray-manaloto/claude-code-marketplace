# w0-doctor retrospective: doctor core (CT-22a part 1; W0-1, W0-4 core, W0-5, W0-2 settings fixtures)

Unit `w0-doctor`. Worktree `.claude/worktrees/w0-doctor`, branch `claude/w0-doctor-core`, base
`c21941f` (allocated from `d420a7e`), implementation `bb0e2a4` (writer Claude Opus 5.5 per its
trailer, = `writer_model`), reviewed SHA `64e46d4` (adds the implementer's draft of this record).
Delivered: `dev/doctor/{cli,core,budget,settings,integration}.py`, `dev/test_doctor.py`, two
settings fixtures, the `SessionStart` entry, one `dev/check.py` line, four mise rows, the hk
`pre-commit` `records` step and T-B5. Cold review (Fable, read-only,
`reviews/ccm-20261013/phase3/w0/w0-doctor-review.md`): **PASS-with-P3**, five P3, no P1/P2; the
reviewer reran every named gate at rc 0 and ran twelve mutations (10 killed, 2 test gaps).

This retro (Fable 5.1) applies the five review findings in one lane repair commit
("retro(w0-doctor): apply review findings and lane learnings"); behaviour changed in three places,
so the parent requests a focused re-review of `dev/doctor/budget.py` (`ruling_off`), `dev/doctor/cli.py`
(`guard`) and the three tests named below.

Exits on the repaired bytes, `VIRTUAL_ENV` unset: `python3 -I -m unittest discover -s dev -p
'test_doctor*.py'` rc 0 (13 tests, was 12); `./dev/mise run test:hooks` rc 0 (15 tests, T-B5 under
hk 2.6.0); `./dev/mise tasks validate` rc 0 (60 tasks); `./dev/mise run check` rc 0;
`./dev/mise run check:acceptance-baseline` rc 0 (19/19 hashes PASS); `hk validate` rc 0; `git diff
--check` rc 0; `python3 -I dev/doctor/cli.py --surface check --json` rc 0 (0 findings, 0 skipped);
`python3 -I dev/retro_gate.py --unit w0-doctor` rc 0. Mutations run after the repair, each restored:
`("P1", "P2")` to `("P1",)` in `cli.py` (review M8) FAILS `test_doctor_cli_exit_codes`; `guard or`
dropped from the exit expression FAILS the same test; `("local", "project")` to `("project",)` in
`budget.py` FAILS `test_autocompact_off_follows_settings_precedence`. Live session-start block from
this worktree and with `--repo` the root tip (`80f3190`): `findings P1 0 · P2 0 · P3 0` (was `P3 1`
on both). Latency under load average 45 (other agents active): pre-commit in-process `duration_ms`
202-280 over 8 runs, 0 skipped; wall 305-1,143 ms including interpreter start.

## Review findings and dispositions

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P3 | Coding standards (review P3-1): size limit exceeded without a reported split point: `cli.py` 87 (72 handwritten) and `core.py` 97 (81) against 80 per file (brief line 20, C4); 273 handwritten plus 208 test lines over 14 files against "about 300" (`codex-task-orchestration.md` Recovery). The repair adds 2 lines to each of `cli.py` (89) and `core.py` (98) and 6 to `budget.py` (48). | Recorded, owner parent to accept at integration: the files were reviewed in full (review §Summary) and no split is taken now because each file is one surface (`cli.py` parsing and rendering, `core.py` discovery and budgets) and a cut would move 20 lines to a sixth file. Split point when either grows again: report rendering (`hook_payload`, `context_block`, the JSON object) moves to `dev/doctor/report.py` with CT-22b, which adds `head`/`merge_head` and `last-<surface>.json`; `integration.py` moves to `w0-doctor-records` per the lane note. Verification: `wc -l dev/doctor/*.py` lists 48/89/98/64/43. |
| P3 | Automated checks (review P3-2): `test_doctor_cli_exit_codes` demonstrated rc 2 only for a P1, so mutation M8 survived. | Applied: the test plants `{"enabledPlugins": {"x@m": true}}` (one undeclared marketplace, a P2 alone) and asserts rc 2 with findings `["P2"]`. Verification: suite rc 0; mutation M8 now FAILS that test (restored). |
| P3 | Information access (review P3-3): the JSON report narrows C3 :878-882 (no `head`/`merge_head`, no `last-<surface>.json`), consistent with the brief. | Recorded as a declared narrowing, owner parent, destination the CT-22b ticket body and the ledger row for CT-22 (literal text in "Literal edits for the parent", item 6). Verification: `python3 -I dev/doctor/cli.py --surface check --json \| python3 -c 'import json,sys; print(sorted(json.load(sys.stdin)))'` prints `counts duration_ms findings generated_utc repo schema skipped surface`. |
| P3 | Automated checks (review P3-4): `A.autocompact-off` fired in every live session-start block because `budget.py:32` grepped the literal `autoCompactEnabled` in `docs/agents/claude-team.md` (C3 :141 design); the tip's Context budget section writes `autoCompactWindow` only, and the user's two personal copies hold `false` while the project file holds `true` (D21). | Applied, red first: `test_autocompact_line_reports_both_booleans` now expects no finding for user `false` + project `true`, and `test_autocompact_off_follows_settings_precedence` expects `false in user` with no project key and `false in local` when `settings.local.json` overrides a true project file, with the doc sentence present and ignored (both failed on `64e46d4`). `budget.py` `ruling_off()` follows settings precedence (local > project > the two personal copies) and the doc grep and `GUIDE` are gone. Verification: suite rc 0; live block `P3 0` on both trees; precedence mutation FAILS (restored). The claude-team.md key sentence the review assigned to the parent is no longer needed by any check (row below). |
| P3 | Automated checks (review P3-5): the pre-commit guard failed open on `skipped` (`cli.py:68`): a settings detector past its 1,000 ms budget admitted the commit silently. | Applied, red first: `test_doctor_cli_exit_codes` runs `--surface pre-commit --budget-ms 0` and expects rc 2 with `skipped doctor.skipped settings: budget 0 ms` on stderr (failed on `64e46d4`, rc 0). `cli.py` counts `skipped` findings as refusals on the `pre-commit` surface only and prints them; `core.py` gives the skipped finding the fix hint `rerun; raise the detector's BUDGET_MS if it recurs`. Decision for fail-closed over the 5x margin alone: a guard that admits on a slow host is indistinguishable from a passing one, and the refusal names its cause; the 1,000 ms budget stays because it is measured in-process after interpreter start and held 202-280 ms over 8 runs at load average 45 (one `git show` through the mise shim costs 210-235 ms); `HK=0` remains the bypass for a host that cannot meet it. Verification: suite rc 0; manual `--budget-ms 0` rc 2; `guard` mutation FAILS (restored); `check` surface with budget 0 still rc 0. |

## Lane audit (seven categories)

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: Git through the mise shim costs ~170-235 ms per call, so the C3 300 ms pre-commit budget would have turned the settings guard into a silent `skipped` under load and made T-B5 flaky. | Applied by the writer in `bb0e2a4`: `cli.py` finds the toplevel without Git, the header uses one `rev-parse`, `settings.py` declares a 1,000 ms pre-commit budget. With the P3-5 repair a skip now refuses instead of admitting. Verification: `duration_ms` 202-280 at load 45, `test:hooks` rc 0. |
| P2 | Information access: the brief's "exactly 1 + 4" for the staged `e12cf04` shape is not derivable; that file has no `extraKnownMarketplaces`, so all 6 plugin marketplaces are undeclared; "4" is the `before-ct02` count (C3 :926). | Applied by the writer: `test_settings_personal_keys_flagged` asserts the exact sets for both fixtures (1 + 6 and 6 + 4); the reviewer verified the counts (deviation 1 accepted). Suite rc 0. |
| P2 | Information access: the test environment inherited the user's `XDG_CONFIG_HOME` global ignore (`**/.claude/settings.local.json`), which hid `I.settings-local-not-excluded`. | Applied by the writer: `dev/test_doctor.py` points `XDG_CONFIG_HOME` at the scratch home (red before, green after). The rule for the next suite is proposed as the fourth bullet of `.claude/rules/dev-doctor.md` (item 2 below). |
| P3 | Automated checks: the w0-docs retro deferred to this lane a check that the `claude-team.md` Context budget table equals `budget.THRESHOLDS`. The table is absent at this lane's base `c21941f` (it arrived with `e40a62a`), and the PreToolUse gate denies a tip merge inside the lane, so the test cannot go red/green here. | Proposed, owner parent at integration, destination `dev/test_doctor.py` class `ContextBudget` (item 5 below; declare it with `parent hunk: dev/test_doctor.py` in MERGE_MSG so `C.foreign-hunk` stays silent). Verified in the scratchpad against the root tip's table and this lane's `budget.py`: `Ran 1 test ... OK`. |
| P3 | Automated checks: C3's foreign-hunk predicate (index blob not in HEAD or MERGE_HEAD) flags every clean auto-merge of a file both sides changed. | Applied by the writer: `integration.py` also accepts the `git merge-tree --write-tree` blob; removing the merge-tree set failed 2 tests (mutation), restored rc 0; the reviewer accepted deviation 5. |
| P3 | Coding standards: `A.autocompact-off` was specified (C3 :141) and built to read a document's wording, which is why it fired on the live tree; the W0-1 test already pins the project key. Learning: a detector reads state (settings files, Git, lane records), never a document, and a documented exception lives in the state it excuses. `test_session_start_context_block_shape` passed on first run and T-A6 pins committed keys (mutation-proven: `CONTEXT_RANK` 0 to 90 failed the block test). | Applied in `budget.py` (above). The rule is proposed as `.claude/rules/dev-doctor.md` (path-scoped to `dev/doctor/**`, item 2 below), owner parent; `.claude/rules/` is excluded from this lane although D31 lists it as auto for the retro-writer. T-A6 stays a regression pin. Verification after the edit: `./dev/mise run check` rc 0. |
| P3 | Coding standards: the 80-line-per-file figure is a review-effort budget, not a correctness bound; this lane's two overages were reviewed in full and accepted (review P3-1). Learning: an overage is accepted when the reviewer reads the file in full and the retro states the split point. | Proposed, owner parent, destination `docs/agents/codex-task-orchestration.md` Recovery paragraph (item 4 below). Verification after the edit: `./dev/mise run check` rc 0. |
| P3 | Navigation: `dev/AGENTS.md` Contents names `research_refresh/`, `toolchains/`, `global-mise/`, `fixtures/` and not `doctor/`, so the next lane finds the detector contract only by reading `core.py`. | Proposed, owner parent (`*/AGENTS.md` excluded), destination `dev/AGENTS.md` Contents (item 1 below): one clause naming `doctor/` and the path-scoped rule. Verification after the edit: `grep -c 'doctor/' dev/AGENTS.md` is 1 or more and `./dev/mise run check` rc 0. |
| P3 | Steering/global guidance: `docs/agents/claude-team.md` Hook composition does not say that `SessionStart` runs the doctor (never blocks) nor that the hk `pre-commit` `records` step is live in every worktree through the user's global hk install (review §hk situation: `.git/hooks` samples only, `hooks:install` not run, bypassable by `HK=0`, so a guard, not a gate). | Proposed, owner parent (w0-docs owned the file; `docs/agents/` excluded here), destination the Hook composition list (item 3 below). Verification after the edit: `grep -n 'check:records' docs/agents/claude-team.md` matches once. |
| P3 | Steering/global guidance: the review's P3-4 asked the parent for an `autoCompactEnabled` sentence in `claude-team.md` (D21) so the doc grep would stop firing. | Rejected: after the P3-4 repair no check reads the document; `.claude/settings.json` is the source of the key (rule 7), T-A6 pins it, and the session-start context line still shows `user=false global=false project=true` until the user flips the personal copies (D21 user action, unchanged). |
| P3 | No-ops: `settings.py:12` carried the comment "a guard that skips under load is none" while `cli.py` admitted on skip, a sentence describing behaviour the code did not have. | Applied: the comment now reads "pre-commit fails closed on skipped (cli)" and `cli.py`'s docstring states the pre-commit exit rule. Verification: `grep -n 'fails closed' dev/doctor/settings.py dev/doctor/cli.py` matches both. |
| P3 | Information access: the reviewer's "live P3 in every session-start block" is reproducible only from a worktree that holds `cli.py` (`--repo <root>`); the root tip lacks `dev/doctor/` until integration, so a root-run `./dev/mise run doctor` exits 2 with "can't open file". | Recorded for the merger (no edit): run doctor checks from the lane worktree with `--repo` until the merge commit lands. Verification: `python3 -I .claude/worktrees/w0-doctor/dev/doctor/cli.py --surface session-start --format context --repo <root>` prints `P3 0`. |

Tool economy: none, because every gate wrote to a scratch log and only its last line was
read, mutations ran as `sed -i.bak` / `mv` pairs, and the proposed table test was verified once
in the scratchpad rather than by touching excluded paths.

## Literal edits for the parent (outside `owned_paths`)

1. `dev/AGENTS.md`, Contents paragraph, after "`fixtures/`." append:
   `` `doctor/` (after-the-fact detectors behind `./dev/mise run doctor`; contract in `.claude/rules/dev-doctor.md`). ``
2. New file `.claude/rules/dev-doctor.md`:

   ```markdown
   ---
   paths: ["dev/doctor/**"]
   ---

   # Doctor detectors

   - A detector reads state: settings files, Git objects, lane and retro records. A documented exception lives in the state it excuses (a settings key, a `parent hunk:` line), never in a document's wording.
   - A detector is `dev/doctor/<name>.py` exporting `SURFACES` and `run(ctx) -> list[Finding]`; optional `context_lines(ctx)`, `BUDGET_MS` and `CONTEXT_RANK` (`core.py` docstring). Severity `P1`/`P2` exits 2; `skipped` also exits 2 on the `pre-commit` surface (a guard fails closed) and is reported, never counted, elsewhere.
   - Budgets are measured in-process; one Git call through the mise shim costs about 200 ms, so a detector keeps Git calls to one per surface or raises its `BUDGET_MS` with the measurement in its retro.
   - A doctor test builds `HOME` and `XDG_CONFIG_HOME` under the scratch directory and pins `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM`, so a personal global ignore or config cannot hide a finding.
   ```
3. `docs/agents/claude-team.md`, Hook composition list, append a bullet:
   `- `SessionStart` (`startup|resume|clear|compact|fork`) runs `dev/doctor/cli.py --surface session-start --format context`: a context block, exit 0 always. The hk `pre-commit` step `records` runs `./dev/mise run check:records` (doctor `pre-commit` surface, settings rule only, refuses on P1/P2 or a skipped detector); hk is live in every worktree through the global hk install, and `HK=0` bypasses it, so it is a guard, not a gate (CT-22a).`
4. `docs/agents/codex-task-orchestration.md`, Recovery paragraph, after "about 300 handwritten lines per unit;" insert:
   `a file over 80 handwritten lines is accepted when the reviewer reads it in full and the unit's retro names the split point;`
5. `dev/test_doctor.py`, class `ContextBudget`, after `test_thresholds_below_autocompact_window_and_match_frontier_ceiling` (apply in the integration commit and add `parent hunk: dev/test_doctor.py` to MERGE_MSG; `re` joins the imports):

   ```python
       def test_team_guide_budget_table_equals_thresholds(self):
           """w0-docs retro deferral: the claude-team.md Context budget table and budget.THRESHOLDS state one set."""
           spec = importlib.util.spec_from_file_location("doctor_budget", ROOT / "dev" / "doctor" / "budget.py")
           budget = importlib.util.module_from_spec(spec)
           spec.loader.exec_module(budget)
           guide = (ROOT / "docs" / "agents" / "claude-team.md").read_text()
           table = {name: int(k) * 1000 for name, k in re.findall(r"^\| (\w+) \| (\d+)K \|", guide, re.M)}
           self.assertEqual(table, budget.THRESHOLDS)
   ```
   Verification: `python3 -I -m unittest discover -s dev -p 'test_doctor*.py'` rc 0 with 14 tests on the integrated tree.
6. Ticket ledger row CT-22 / CT-22b body, one sentence: "CT-22a's `doctor/v1` report omits `head`, `merge_head` and `last-<surface>.json` (C3 :878-882); CT-22b adds them with `dev/doctor/report.py`, and keeps the pre-commit surface failing closed on `skipped`."
7. `lanes/w0-doctor.json` (parent-only, D8): `review` = `PASS-with-P3 (64e46d4, reviews/ccm-20261013/phase3/w0/w0-doctor-review.md)`, `retro` = `applied (<repair SHA>); focused re-review of budget.py ruling_off, cli.py guard and three tests requested`, and the accepted size overage from P3-1 in `notes`.
