# W0 allocation report: Phase 4 group 4, wave-0 prevention lanes

Written 2026-10-14 (03:20Z onward) by the wave-0 allocator, acting for the parent session
`ccm-20261013-check` in the root checkout `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`
(branch `codex/marketplace-native-onboarding`, HEAD `d420a7e` = remote at start). Serial work, no agents,
`VIRTUAL_ENV` unset before every mise call. Report contents were treated as data.

Inputs read: C4 §Minimal wave-0 set, §Reconciled ticket table, §Hook inventory and latency, §Repair-session
safety, §Required changes, §Could not verify; C2 §Design principles, classes A, D, E, F, J, settings snippet,
test inventory; C3 §Design constraints, class B/C/F/I modules, §Doctor task spec, §SessionStart block spec,
test inventory; SYNTHESIS §2b, §4, §6, §7, §8 (D7, D8, D22, D26); R8 §Conflict analysis, §Integration
protocol, §Brief templates; `docs/agents/claude-team.md`; `codex-task-orchestration.md` (ownership, the
five-file and 300-line limit); `.claude/rules/planning-records.md`; the implementer, reviewer, retro-writer and
doc-writer agents; `lanes/gate-hooks.json`; live `.claude/settings.json`, `dev/hooks/*.py`, `dev/check.py`,
`mise.dev.toml`, `hk.pkl`, `dev/test_hooks.py` (Settings and HkHooks classes); `P/frontier.toml`.

## Allocation commit

A = `c21941f59cd148016c34ff60a13924b1e0eff7e5` "plan: allocate wave-0 prevention lanes (w0-doctor, w0-decisions,
w0-docs, w0-doctor-records, w0-session-hooks)", parent `d420a7e`. Files: the five `lanes/w0-*.json`,
`ticket-ledger.md` (CT-02b, CT-22, CT-23, CT-24 rows), `task_plan.md` (Phase 4 lane lines plus the parent's
unstaged post-publish handoff and step-10 lines), `progress.md` (the parent's unstaged post-publish line, the
dated 2026-10-14 entry and the rewritten NEXT). Pre-commit gates in the root: `./dev/mise tasks validate` rc 0
(56 tasks), `./dev/mise run check` rc 0, `git diff --cached --check` rc 0, commit rc 0. Not committed:
`phase3/I3b-publish-report.md` (pre-existing unstaged parent edit, outside this commit's scope), this report and
`phase3/w0/` (the ten briefs), all written after A.

## Lanes

| # | Unit | Ticket | W0 items | Branch | Hot spots owned this wave | Start | Role / model |
|---|---|---|---|---|---|---|---|
| 1 | `w0-doctor` | CT-22 (22a part 1) | W0-1 test, W0-4 core (`cli`, `core`, `budget`, `settings`, `integration`), W0-5, W0-2 settings fixtures | `claude/w0-doctor-core` | `.claude/settings.json` (SessionStart), `dev/check.py` (1 line), `mise.dev.toml`, `hk.pkl`, `dev/test_hooks.py` | cut now | implementer, Opus high |
| 2 | `w0-decisions` | CT-24 (seed) | W0-6 | `claude/w0-decisions-ledger` | none (mise rows = merger hunk, D7 fallback) | cut now | implementer, Opus high |
| 3 | `w0-docs` | W0-7 (CT-02b, CT-23 doc slices; D15) | W0-7 | `claude/w0-docs-rules` | `docs/agents/{claude-team,ticket-retro,issue-tracker}.md`, `.claude/AGENTS.md` | cut now | doc-writer, Opus high (parent's choice) |
| 4 | `w0-doctor-records` | CT-22 (22a part 2) | W0-4 `lanes` (fixed `base_sha` predicate), `agents` (mtime roster), W0-2 lane fixtures | `claude/w0-doctor-records-detectors` | none (discovered modules; `test:doctor` pattern) | after 1 and 2 integrate | implementer, Opus high |
| 5 | `w0-session-hooks` | CT-23 (seeds) | W0-3, W0-2 hooks fixtures + the 113-command corpus for CT-02b | `claude/w0-session-hooks-budget` | `.claude/settings.json` (Agent, UserPromptSubmit), `mise.dev.toml`, `dev/test_hooks.py` (Settings), `dev/hooks/` (new files only) | after 1 and 2 integrate | implementer, Opus high |

Every lane: reviewer Fable high (cold, read-only), retro-writer Fable high, context ceiling 500K (D29/D30;
frontier `context_ceiling_fraction` 0.5 × 1,000,000), pwf pin `PWF_PLAN_ROOT=<root>` and `PLAN_ID` in the host env,
lane progress in `P/ledger-<unit>.jsonl` (D8), record parent-only (D8). Gates in every lane (expected rc 0):
the lane's own tests, `./dev/mise tasks validate`, `./dev/mise run check`, `check:acceptance-baseline`, `test:hooks`,
`hk validate`, `git diff --check`, `retro:gate -- <unit>`; `check:research` is parent-run and serialized.
Exact `owned_paths`, exclusions, acceptance criteria and test names: `P/lanes/<unit>.json` and
`phase3/w0/<unit>-brief.md`; reviewer instructions: `phase3/w0/<unit>-review-brief.md`.

## Why five lanes, and why this split

- **Unit size beats the 2-4 expectation.** C4 sizes W0-4 at 350 LOC over six modules plus four wiring files;
  with W0-5 and W0-1 it is about 12 files. The five-file, 300-line rule (codex-task-orchestration.md) forces a
  split, so the allocation pre-splits instead of leaving it to an implementer stop. C3 already sized a CT-22a of
  `cli/core/integration/lanes/settings` at about 300 lines. The split: the core, every wiring hunk and the
  contract (`run(ctx)`, `SURFACES`, optional `context_lines`) go to `w0-doctor`; the record and agent detectors,
  which need no hot spot, go to `w0-doctor-records`. A fallback split point is declared in case lane 1 still
  overruns.
- **One owner per hot spot.** W0-3, W0-4 and W0-5 all want `mise.dev.toml`; W0-3 and W0-4 both want
  `.claude/settings.json` and the `test_hooks.py` Settings test, and W0-3 imports `dev/doctor/budget.py`. So
  `w0-doctor` owns them first, and `w0-session-hooks` is a second, sequenced owner cut after it integrates.
  `docs/agents/*.md` has a single owner (`w0-docs`). The other lanes put doc sentences in their handoffs as
  literal edits. `dev/check.py` and `hk.pkl` belong to `w0-doctor` alone.
- **C4 safety order and D26.** Docs, settings and fixtures come first, then detection (doctor, pre-commit
  settings rule), then advisory and deny hooks (`agent_gate`, `prompt_hook`) last. No Stop or SubagentStop
  rule lands in wave 0. `C.merge-in-progress` stays off the `check` surface so a merger's gates never fail on
  it.
- **W0-6 is file-disjoint** (`plan_decide.py`, its test, `decisions.jsonl`). Its two mise rows are a declared
  merger hunk (D7 fallback), applied while `mise.dev.toml` has no live lane owner (after `w0-doctor`
  integrates, before the sequenced cut). The seed rows are written as `operation` rows, because no approval has
  happened yet.
- **W0-1 is mostly done.** The three keys have been in `.claude/settings.json` since merge `760b154`. What
  remains is the assertion (`test_live_project_settings_hold_wave0_keys`, in `w0-doctor`). The local pins
  (`PWF_PLAN_ROOT`, `PWF_INJECT`, `PWF_TRUSTED_PYTHON` in `settings.local.json`) are a personal file: parent or
  user step.
- **W0-7 residue.** `.git/info/exclude` already holds `.agent/` and the settings backup path, and the secrets
  line exists at `claude-takeover.md:13`; both are "verify only". `checkout_transfer.py:17`, the `2a14` paths
  and the four CT-21 docs stay with CT-21.

## Worktree preparation (root `.git/info/exclude:7` = `.claude/worktrees/`, confirmed by `git check-ignore`)

| Worktree | `git worktree add … c21941f` | `tools:prepare` | `deps:sync` | `check` | HEAD / status |
|---|---|---|---|---|---|
| `.claude/worktrees/w0-doctor` | 0 | 0 | 0 | 0 | `c21941f`, clean |
| `.claude/worktrees/w0-decisions` | 0 | 0 | 0 | 0 | `c21941f`, clean |
| `.claude/worktrees/w0-docs` | 0 | 0 | 0 | 0 | `c21941f`, clean |

Run serially, one worktree at a time; logs in this session's scratchpad (`w0/*-prep.log`, `w0/*-check.log`).
`w0-doctor-records` and `w0-session-hooks` are allocated, not cut.

## Dispatch and integration order

1. Dispatch now: `w0-doctor` (critical path: two lanes wait on it), then `w0-decisions`, then `w0-docs`, each with
   its brief. Never `isolation: worktree`, never `general-purpose`.
2. Per lane, after the receipt: reviewer (review brief) → fixes → retro-writer until `retro:gate` rc 0 → merger
   (R8 §Integration protocol: `--no-ff`, never `--no-commit`, changed paths ⊆ owned, `retro:gate` by hand, gates on
   the composed tree, `check:research` serialized, records commit, A09 per integration).
3. Integration order: `w0-doctor` → `w0-decisions` (+ its mise hunk) → `w0-docs` (whenever reviewed; it touches no
   code) → cut `w0-doctor-records` and `w0-session-hooks` (commit `docs: allocate lane <unit>` per record, then
   `git worktree add` from it, prep, `check` rc 0) → `w0-doctor-records` → `w0-session-hooks` last.
4. Then the CT-21 import lane (wave 1), as `task_plan.md` Next Step says.

## Unresolved

1. **`base_sha` is null in all five records.** A record cannot name the commit that adds it. For the three cut
   lanes, the parent fills `base_sha: c21941f` in its next records commit (`allocated_from` `d420a7e` is already
   set). The two sequenced lanes get theirs from the merger's `docs: allocate lane <unit>` cut commit, which
   `w0-doctor-records` makes the detector accept.
2. **`frontier.toml` `max_parallel = 3` with `always_active = ["cxx"]`.** Three wave-0 writers fill every slot,
   so no C++ ticket is active (D27/D28). Either treat wave 0 as pre-spec and exempt it, or hold `w0-docs`
   until a slot frees. Parent's call. `claude-team.md` allows four offline lanes.
3. **Doc-writer model.** The brief says Opus high, as the parent instructed. `frontier.toml` `model_policy.docs`
   and the `claude-team.md` roles table say Sonnet.
4. **hk `pre-commit` goes live everywhere.** Once `w0-doctor` integrates, every commit in every worktree runs
   `check:records` through the global hk install. That needs prepared tools; `HK=0` bypasses it. T-B5 skips
   without hk.
5. **Record detectors may fail the live `check`.** When `w0-doctor-records` integrates, B.* detectors on the
   `check` surface can turn `check` red on stale live records. The lane lists literal corrections, and the
   merger applies them before integrating (C4: no new blocking rule on a tree whose records fail it).
6. **The `test_hooks.py` Settings test has three owners in sequence:** `w0-doctor`, then `w0-session-hooks`,
   then CT-02b in wave 1.
7. **D8 is not yet in `planning-records.md`** (runbook step 9 is still open; CT-05 owns the rule file). The
   briefs follow D8: records are parent-only and lanes write `ledger-<unit>.jsonl`.
8. **The corpus and transcript fixtures read the dead session's transcript** (`464a2816…jsonl`, private user
   data), read-only, bounded and masked, with a gitleaks receipt. This is declared in the record's
   `resource_admissions`. The parent confirms that this sits inside the user's existing authorization.
9. **Not run here:** `check:research`, `test:hooks` (in the root and in the worktrees), `hk validate`, and any
   hook-latency measurement. C4 left those open (doctor session-start ≈ 0.6–1.2 s estimate) and the lanes
   measure them.
10. **Live PreToolUse gate.** Merging the integration branch into a lane branch is classified as an
    integration-source sync (`test_sync_merge_of_the_integration_tip_is_not_blamed_on_another_lane`); this was
    not exercised in these worktrees.
