# I3: Phase 3 group 3A, record corrections and the second-publish selected set

- Root checkout `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`, branch
  `codex/marketplace-native-onboarding`, HEAD `0a68dce` = remote, no `MERGE_HEAD`. Written by I3
  (session `ccm-20261013-check`).
- Authority: D1-D45 (D12 archive, D13 digests out, D15 wording, D24 CT-21 index only, D37 one
  publish per integration, D2 no `hooks:install`).
- `VIRTUAL_ENV` was unset for every gate. Logs are in the session scratchpad `i3/logs/` and are
  not committed.
- **Outcome: staged, not committed.** 93 paths are staged and equal the selected list. Nothing
  was committed, prepared or published.

## 1. Corrections applied

`P` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`. Every SHA below was checked
with `git rev-parse` and `merge-base --is-ancestor`. Integration merges `fa892d2`, `4c1ea6b`,
`e618243` and `7e22d13` are in `28fedf1` but not in `f250f75`. `361688e`, `55f3946` and
`447110a` are in `f250f75`.

### Lane records

Each record kept its existing JSON style (indent 2, its own `ensure_ascii`). `python3 -I`
`json.load` passed for all 10 records.

| Record | Field | Value |
|---|---|---|
| `lanes/nav.json` | `base_sha` | `7e22d13` → `c6ff7ef` (`5cadad4^`) |
| | `allocated_from` | `7e22d13` (new) |
| | `integration_merge` | `fa892d2` (new) |
| | `published` | `28fedf1` (new) |
| | `status` | "CT-04 publication pending" → "published 28fedf1" |
| `lanes/c1-catalog-promotion.json` | `base_sha` | `447110a` → `ca60871` (`52ce420^`) |
| | `allocated_from` | `447110a` (new) |
| | `merged_head` | `6c09b7f (7295463 = merge of 2d1f60e)` |
| | `integration_merge` | `4c1ea6b` (new) |
| | `published` | `28fedf1` (new) |
| | `status` | gains "published 28fedf1;". "#94 closure pending" is kept. |
| `lanes/retro-gate.json` | `integration_merge` | `e618243` (new) |
| | `published` | `28fedf1` (new) |
| | `status` | "publication pending" → "published 28fedf1" |
| `lanes/team.json` | `lane_commit` | `5107322 + sync 9103931, 5becfc0 + repairs ea8c8c9` |
| | `merged_head` | `ea8c8c9` (new) |
| | `integration_merge` | `7e22d13` (new) |
| | `published` | `28fedf1` (new) |
| | `status` | "publication pending" → "published 28fedf1" |
| `lanes/a06-unit3.json` | `integration_merge` | `361688e` (new) |
| | `status` | "publication pending" → "published f250f75" |
| | `retro` | `passed` is now true for the unit name (see the a06 retro alias below) |
| `lanes/codex-session-history.json` | `integration_merge` | `55f3946` (new) |
| | `status` | "publication pending" → "published f250f75" |
| | `review` | "focused re-review running" → "focused re-review PASS for integration" (retro line 46) |
| `lanes/rf-env-scrub.json` | `integration_merge` | `447110a` (new) |
| | `status` | "publication pending" → "published f250f75" |
| `lanes/gate-hooks.json` | `integration_merge` | "…SHA in progress.md" → `760b154 (parents 9cd396a 697e1da)` |
| | `published` | `0a68dce` (new) |
| | `status` | "A09 publication pending" → "published 0a68dce (A09)" |

Not changed:
- `lanes/m0-remaining-work-merge.json` is already correct.
- `lanes/ct21-codex-imports.json` is the T2 design record, committed as is.

### Retros

| File:line | Change |
|---|---|
| `P/retros/c1-catalog-promotion.md:6` | "merged with `e618243`" → "merged with `2d1f60e` as `7295463` (integration merge `4c1ea6b`)" |
| `P/retros/team.md:4` | "lane commit `9103931`" → "lane commit `5107322` … (sync merges `9103931`, `5becfc0`)" |
| `P/retros/retro-gate.md:3` | Appended "after repair `5ea8ee4` (final lane tip; integration merge `e618243`)" |

`retros/gate-hooks.md` was not changed. Its §4 corrections were committed in `760b154` (I1c).

### a06 retro alias

This follows R5 P2-5 and SYNTHESIS §5 step 7.
- The fix is `P/retros/a06-unit3.md`, a copy of `a06-classification-methods.md` with one added
  note at lines 3-4. The body is otherwise identical: `diff` of the copy without lines 2-4
  against the original gave rc 0.
- The original was kept.
- `python3 -I dev/retro_gate.py --unit a06-unit3` returned rc 2 ("retro record missing") before
  the copy and rc 0 after it.

### Docs

- `docs/agents/claude-team.md:95`: "`CODING_STANDARDS.md` arrives with ticket CT-04 (NAV)" →
  "Reviewer judgement rules live in `CODING_STANDARDS.md` (integrated with ticket CT-04, lane
  `nav`, merge `fa892d2`)".
- `docs/agents/claude-takeover.md`:
  - `:7`: "No Codex thread is mid-turn." is replaced by sweep C's sentence, verbatim.
  - `:11`: D15 wording. "runs under the user's standing authorization (round-1 Q3)" becomes
    "comes from mattpocock-skills 1.3.1; `to-spec`, `to-tickets`, `implement-spec` and `retro`
    were applied file-guided at the user's round-1 Q3 request; they have not been invoked. A
    stage counts as invoked only when the user types it; `skill-invocations.md` records each."
  - `:13`: a new Secrets bullet, from N1:
    - the project requires fnox ≥ 1.39.0;
    - no secret goes in any settings file or mise `[env]`;
    - the exec-scoped route is `fnox --config ~/.config/fnox/config.toml --profile <name>
      --no-defaults --no-daemon --non-interactive exec -- <command>`.
  - `:15-30`: a new subsection, "Codex coordination state superseded (read first when resuming
    Codex)", holding sweep B §4's notice verbatim.
  - "Immediate next work": a "Current (2026-10-13)" paragraph now points at the plan's
    `## Next Step` and SYNTHESIS §5-§6. The standby paragraph is kept as historical.
- `docs/accepted-decisions.md`: +53 lines, the "Automation and observability clarification
  (2026-10-12)" section. It is hunk 1 only of
  `P/imports/codex-worktrees-20261013/2a14/modified/docs/accepted-decisions.md.diff`.
  - Before: HEAD blob = working blob = `5fc8c85`, which matches sweep A.
  - `git apply --check` rc 0, then `git apply` rc 0. The new blob is `7104df6`.
  - **Hunk 2 was not applied.** It rewrites the "Global mise owns tool installations" bullet.
    SYNTHESIS §4 says T2 could not verify that its wording is the user's, so the user should be
    asked.

### Builder and spec proposals

- `P/proposals/claude-takeover-spec/build_manifests.py`, per R2 publication fix 3:
  - Docstring "ten tickets" → "eleven tickets (CT-01..CT-11)". `TICKETS` holds 11 entries, not
    R2's prospective 16, because R2's body edits are not applied.
  - Docstring `../../drafts/spec-claude-takeover.md` → "spec.md beside this script".
  - `TICKETS` is reordered so CT-10 precedes CT-11.
- Before the edit, the builder reproduced both committed manifests byte for byte (`cmp` rc 0).
- `tickets.preview.json` was regenerated (`tickets … 999999`). Its order is now CT-01…CT-11 and
  the per-ticket content is identical (dict compare True).
- `spec.manifest.json` is unchanged (`cmp` rc 0).

## 2. Exclusions (`.git/info/exclude` only; `.gitignore` untouched)

- Six anchored lines were appended (lines 10-15). The pre-edit copy is in scratchpad
  `i3/exclude.before`.
- `git check-ignore -v` returned rc 0 for each one:
  - `exclude:10` `reviews/ccm-20261013/settings.json.before-ct02`
  - `exclude:11` `reviews/ccm-20261013/plan-backups/`
  - `exclude:12` `reviews/ccm-20261013/codex-briefs/digests/`
  - `exclude:13` `imports/codex-worktrees-20261013/2a14/`
  - `exclude:14` `imports/codex-worktrees-20261013/c658/`
  - `exclude:15` `.agent/`
- `git status --porcelain --ignored` lists all six as `!!`.
- The ticket-frontier state directory `P/frontier/` does not exist (`frontier.py:156` would
  create it on first write), so no line was added. `frontier.toml` is selected.
- `plan-backups/` is excluded per this brief. P3 §7 had proposed committing it.
  `plan-backups/group1/composed/settings.local.json` holds the personal allow-list, as I1c §1
  warned. The D12 reversibility receipt therefore stays local.

## 3. Secret and privacy scan

- Searched the selected set for MCP tool names (`mcp__<server>__`), a `"permissions":` key and
  the personal `Downloads` path.
- Hits before redaction:
  - R5 `:302-312` reproduced the seven-rule allow-list in its recommended local-settings block,
    and R5 `:326` held the personal path.
  - The memory-server delete-tool names appeared in R5 `:59,215`, M1 `:34,146`, N1 `:11` and SYNTHESIS `:39`.
- All of these were redacted:
  - the allow-list block became one `"_redacted"` placeholder line;
  - each tool name became `<memory-server delete tools>`;
  - the path became `<personal directory>`.
- Pre-redaction copies are in scratchpad `i3/pre-redaction/`.
- Remaining hits, both accepted:
  - `prevention/C2-prevention-design.md:1233`, a placeholder `"permissions": {"allow": ["<the
    seven MCP rules, verbatim from the backup>"]}` that contains no rule;
  - `codex-briefs/01a13185.brief.md:11`, prose naming the `<TR>` donor folder.
- Note: the same seven rules are already in published history (`0c2748e:.claude/settings.json`,
  an ancestor of `origin`). Redacting the reports does not remove them from history.
- gitleaks 8.30.1 (absolute path; the global shim has no version) ran in `dir` mode on an
  `rsync --files-from` copy of the 93 paths. rc 0, "no leaks found", 0 findings. It ran once
  before the final record edits and once at the end (§5).

## 4. Selected set

- The list is in `phase3/I3-selected-paths.txt`, one path per line, sorted. It holds **93
  paths**:
  - the 5 planning files;
  - 9 lane records (8 corrected plus `ct21-codex-imports.json`);
  - 4 retros (`a06-unit3.md` new; c1, team, retro-gate);
  - 3 proposals (`ticket-CT-21.preview.json`, `build_manifests.py`, `tickets.preview.json`);
  - 6 CT-21 index files;
  - 40 review-dir files;
  - the ticket-frontier mirrors (10 + 10), the agent, the test and `frontier.toml`;
  - 3 docs.
- Bytes: 2,525,111 for the 92 paths other than this report, measured before the report was
  written.
- Staged equals selected: `git diff --cached --name-only | sort | diff - list` rc 0. Every
  non-ignored change in the tree is in the list (`comm` both ways empty).
- Deviations from the brief's list:
  - `T1-dependency-scan.json` was added, because D24 names "T1 report and scan".
  - `tickets.preview.json` was added, because it was regenerated after the reorder.
  - Retros c1, team and retro-gate were added (SYNTHESIS §4 rows).
- Not selected: everything in §2, `.claude/settings.local.json`, `mise.dev.toml`, `dev/check.py`.
  The K2 mise/check hunks belong to CT-25 and are not applied.
- `git add --dry-run` returned rc 0 with 93 "add" lines and no other output. `git add` returned
  rc 0.
- The first `git diff --cached --check` returned rc 2: trailing whitespace on
  `P2-records-update-report.md:70,76`, two space-only continuation lines. Both were stripped and
  re-added, then the check returned rc 0.

## 5. Gates on the composed tree (staged; `VIRTUAL_ENV` unset)

| Command | rc | Summary |
|---|---|---|
| `./dev/mise tasks validate` | 0 | 56 tasks |
| `./dev/mise run check` | 0 | 91 tests OK, status pass |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19, pass |
| `python3 -I -m unittest discover -s dev -p test_ticket_frontier.py` | 0 | Ran 29, OK |
| `python3 -I dev/retro_gate.py --unit ccm-20261013-session` | 0 | PASSED |
| `retro_gate.py --unit` a06-unit3, c1-catalog-promotion, codex-session-history, gate-hooks, nav, retro-gate, rf-env-scrub, team, m0-remaining-work-merge | 0 ×9 | PASSED, selectors none |
| `git diff --cached --check` / `git diff --check` | 0 / 0 | after the whitespace fix |

After `progress.md`, `task_plan.md` and this report were re-added, the parent's final rerun of
`check`, `diff --cached --check` and gitleaks is recorded in the handoff message, not here,
because this file cannot record its own final state.

## 6. Records

- `progress.md` has a dated group-3A entry, and NEXT was rewritten in place as the last bullet:
  "group 3B: Fable cold review of the staged tree …, then A09 prepare/publish with the selected
  paths".
- `task_plan.md` handoff lines 11 and 16-19 and `## Next Step` (lines 29-30) were updated in
  place and stay inside the first 30 lines. "Pending user" no longer lists D1-D26.

## 7. Residuals (not applied)

- `accepted-decisions.md` hunk 2: needs the user's confirmation of its wording.
- `docs/agents/ticket-retro.md:4-8` D15 rewrite: the brief scoped D15 to `claude-takeover.md`.
  SYNTHESIS §4 also lists this file.
- `claude-team.md` merge rule (`--no-ff`, never `--no-commit`), two-gate note and hooks caveats;
  `.claude/AGENTS.md` marketplaces line; `docs/agents/issue-tracker.md` `issue:*` mapping. All
  are SYNTHESIS §4 rows outside this brief (W0-7).
- `claude-takeover.md:10` automation facts (4 h rrule, last cycle) and the `:26` and
  `codex-task-orchestration.md:6` absolute `2a14` paths. These wait for CT-21.
- `skill-invocations.md:20`, `spec.md:61,65`, the R2 ticket-body edits (CT-12…CT-16 and the
  split of CT-09), `00-evidence-index.md` "28" heading and `dev/checkout_transfer.py:17`
  (CT-21).
- `.mode` and the `planning-records.md` amendment (step 9): not part of this brief.
- Not run: `check:research`, `test:hooks`, container, provider, hook-runtime and fresh-session
  acceptance.
