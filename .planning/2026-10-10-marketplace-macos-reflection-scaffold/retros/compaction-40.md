# compaction-40 retrospective: compaction at about 400K, thresholds, ceiling, Opus reviewer

Unit `compaction-40` (R-179; D188, D189, D190, D191). Worktree `.claude/worktrees/compaction-40`,
branch `claude/compaction-40`, cut from allocation commit `6257246` (base `1ec9edf`). Lane
commit `7213170`; integration tip `696e03f` merged as `5c2e2e9` (`--no-ff`, message file,
trailers, no lane branch name; clean, no conflicts); implementer draft `6fca41d` (Opus).
Cold review (Opus 5.5, read-only, on `6fca41d`; parent handoff): PASS with two P3s, every value
matches D190/D191, the threshold order is right, all checks exit 0. Retro (Fable): the two P3s
applied test-first in `0cab4ff`; integration tip `a8e3682` merged as `c2aa3fd` (`--no-ff`,
message file, branch name; clean). A first merge attempt named the briefed SHA `9eb0c99`, which
the branch had already moved past, and the hk pre-merge-commit gate refused it ("no lane branch
derivable"): `git merge --abort`, then the merge by branch name. Writer models: Opus wrote
`7213170` and `6fca41d`, Fable wrote `0cab4ff`, `c2aa3fd` and this record.

Sources: `reviews/ccm-20261014/research7/R23-compaction-percent.md` §1, §7.5, §7.7; the
roster-v2 retro parent edits B-E (`claude/roster-v2`); two coordinator additions from the
roster-v2 cold review (`max_live_agents` 5, `scheduler.md` reviewer model).

Delivered (all inside `owned_paths`):
- `.claude/settings.json`: `autoCompactWindow` 700000 -> 433000, no other key (compaction fires
  at 433000 - 20000 - 13000 = 400,000, R23 §1). No `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, no
  `modelSettings`, no user-settings change.
- `dev/doctor/budget.py`: `THRESHOLDS` warn 220_000, checkpoint 303_000, fork_deny 275_000,
  hard 358_000 (R23 §7.5 proportional set) and its comment.
- `frontier.toml`: `context_ceiling_fraction = 0.275` (0.275 x 1,000,000 = 275,000 = fork_deny,
  D191); `review = { model = "opus", effort = "high" }` (D189, roster-v2 edit B);
  `max_live_agents = 5` (coordinator addition 1).
- `docs/agents/claude-team.md`: reviewer row Opus (edit E); budget sentence and table.
- Ticket-frontier skill, both copies byte-identical: `SKILL.md` step 6 reviewer (edit D), "275 K
  today", warn 220 K; `references/config.md` (cap 5 with its reason, fraction 0.275);
  `references/model-policy.md` (review row opus, ceiling column 275,000, rule (a) without
  `review` per edit C, Thresholds paragraph); `references/scheduler.md` (cap 5, Opus reviewer for
  hot-path and baseline lanes); `evals/evals.json` (expected ceilings 275000, live 4/5);
  `scripts/frontier.py` fallback defaults 0.5 -> 0.275 and 8 -> 5 (match the config.md Default
  column; the shipped config sets both, so behaviour is unchanged).
- Tests: `dev/test_doctor.py` (window 433000; thresholds dict; every threshold below
  window - 33_000), `dev/test_ticket_frontier.py` (mismatch fixture 250000 vs 275000, `next`
  ceiling 275000, cap test renamed `test_live_agent_hard_cap_is_five`, new
  `test_shipped_policy_reviews_on_opus`).

## Retro fixes (`0cab4ff`, test-first, both P3s from the cold review)

- `dev/test_doctor.py`: the D191 invariant `fork_deny == int(windows[model] * fraction)` now loops
  over every model in `frontier.toml` `[windows]` (subTest per model; the set must be non-empty).
  Red: with `sonnet = 200000` planted in `frontier.toml`, `./dev/mise run test:doctor` rc 1, the
  failure naming `model='sonnet'`; planted edit reverted with `git checkout --`. Green on the real
  config: rc 0 (14 tests).
- `scripts/frontier.py:61` (both copies): `FABLE_KINDS = ("retro", "synthesis", "design")`,
  `"review"` dropped, comment states the guard's job. New
  `test_fable_kinds_match_shipped_policy` pins the constant to the `[model_policy]` kinds whose
  model is `fable`. Red with `"review"` listed: `./dev/mise run test:frontier` rc 1
  (`AssertionError: Items in the first set but not the second`); green: rc 0 (31 tests).
  Behaviour unchanged: `next` computes only `implement` and `docs` kinds, so the guard never saw
  `review`. `references/model-policy.md` rule (a) already listed retro, synthesis and design.
- First green run left `scripts/__pycache__/` in the `.claude` copy (the in-process import),
  `diff -r` rc 1; the test now sets `sys.dont_write_bytecode = True` before loading the script,
  the cache was removed, `diff -r` rc 0.

## Checks (worktree, `VIRTUAL_ENV` unset, one literal command each)

Red first: with only the tests changed, `./dev/mise run test:doctor` rc 1 (2 failures: thresholds
dict, window 700000) and `./dev/mise run test:frontier` rc 1 (4 failures: ceiling, mismatch,
cap, review model).

| Command | On `7213170` | On the merge `5c2e2e9` | On the merge `c2aa3fd` (retro) |
| --- | --- | --- | --- |
| `./dev/mise run test:doctor` | rc 0 (14 tests) | rc 0 | rc 0 (14 tests) |
| `./dev/mise run test:frontier` | rc 0 (30 tests) | rc 0 | rc 0 (31 tests) |
| `diff -r .claude/skills/ticket-frontier .agents/skills/ticket-frontier` | rc 0 | rc 0 | rc 0 |
| `./dev/mise tasks validate` | rc 0 | rc 0 | rc 0 |
| `./dev/mise run check` | rc 0 (91 tests; json 2331, python 246, shell 6, toml 21) | rc 0 | rc 0 (91 tests; json 2333, python 246, shell 6, toml 21) |
| `./dev/mise run check:acceptance-baseline` | rc 0 | rc 0 | rc 0 |
| `git diff --check` (worktree; on the merges `git diff --check 696e03f HEAD`, `git diff --check 6257246`) | rc 0 | rc 0 | rc 0 |
| `./dev/mise run doctor` | rc 0 | rc 0 | n/a |
| `./dev/mise run doctor:session-start` | rc 0, `context: auto-compact: user=true project=true · warn 220K · checkpoint 303K · fork_deny 275K · hard 358K` | rc 0, same line | rc 0, same line |
| hk pre-commit (`whitespace`, `records`) on the lane commit | passed | n/a | passed on `0cab4ff` |
| `./dev/mise run retro:gate -- compaction-40` | n/a | n/a | rc 0 (`RETRO GATE PASSED`), rerun on the record commit below |

## Repo grep for stale policy (700000, 400K/500K/550K/650K, Fable reviewer, cap 8)

Fixed in lane: every hit inside `owned_paths` (list above, including `scheduler.md:40` cap 8,
`evals.json` ceilings and the `frontier.py` fallbacks the brief did not name).
Outside `owned_paths`, stated as current policy (parent edits 1 and 2):
- `.claude/agents/frontier-scheduler.md:35` "with a Fable reviewer".
- `task_plan.md:858-860` Context budget line (400 K, 500 K, 550 K, 650 K, `autoCompactWindow` 700 K).
Historical, left as records of what was true: `task_plan.md:62` (R-179 text), `:128` (W0-1),
`:680` (D21 row), `progress.md:439`, `lanes/w0-doctor.json:22`, `lanes/w0-docs.json:23`,
`context_ceiling_tokens: 500000` and `reviewer (fable, ...)` fields in earlier lane records,
`dev/test_ticket_frontier.py:39` fixture lane (`reviewer (fable, cold)`, a test datum).

## Findings

| Severity | Category and finding | Applied action, verification and disposition |
| --- | --- | --- |
| P2 | Steering: two out-of-scope files still state the old policy as current: `.claude/agents/frontier-scheduler.md:35` (Fable reviewer for hot-path lanes, same rule as `scheduler.md:76`) and the `task_plan.md` Context budget line (C4 values, 700 K). A session reading either would brief the old numbers. | Deferred with owner parent: exact text in Parent edits 1 and 2 (both paths excluded for this lane). Verification after applying: `./dev/mise run check` rc 0 and the grep above returns only historical rows. |
| P3 | Coding standards: `frontier.py:61` `FABLE_KINDS` still listed `"review"`; it only exempts that kind from escalation and `next` never computes a review kind, so the name misled once review ran on Opus (cold review P3). | Applied in `0cab4ff`: `"review"` dropped, comment names the guard; `test_fable_kinds_match_shipped_policy` pins the constant to the shipped policy. `./dev/mise run test:frontier` rc 1 red, rc 0 green; `diff -r` rc 0. |
| P3 | Automated checks: `test_thresholds_below_autocompact_window_and_match_frontier_ceiling` checked the D191 invariant for opus only; a 200K window on another model would pass unnoticed (cold review P3). | Applied in `0cab4ff`: loop over every `[windows]` model with the script's own `int(window * fraction)`. `./dev/mise run test:doctor` rc 1 on a planted `sonnet = 200000`, rc 0 on the real config. |
| P3 | Automated checks: importing a mirrored skill script in-process writes `scripts/__pycache__/` into one copy, and the mirror diff (`diff -r`, `test_skill_mirror_is_byte_identical`) goes red. The existing check caught it; no new guardrail. | Applied in `0cab4ff`: `sys.dont_write_bytecode = True` before the load, cache removed; `diff -r` rc 0 and `test:frontier` rc 0. |
| P3 | Automated checks: `frontier.py` fallback defaults (fraction 0.5, cap 8) disagreed with the `config.md` Default column after the change; no test reads them because every test copies the shipped config. | Applied in `7213170`: fallbacks 0.275 and 5, both mirrors; `test:frontier` rc 0, `diff -r` rc 0. No new test: the defaults apply only to a config missing the key. |
| P3 | Automated checks: `test_thresholds_below_autocompact_window...` asserted `value < window`, which would pass a threshold above the real trigger (window - 33K). | Applied in `7213170`: assertion is `value < window - 33_000` (R23 §1 formula); `test:doctor` rc 0, red run rc 1 before the values moved. |
| P3 | Information access: the runtime effect of 433000 is unverified in this lane; the window reaches a session only at the next process start (R23 §7.6) and the probe needs a fresh session. | Deferred with owner parent at the user's restart (R-175 quit-and-restart): `/autocompact` or `/context` shows a 433k (about 400K) window; receipt is the first non-idle `compact_boundary` with `trigger: "auto"` and `preTokens` near 400,000 (exclude "Compacted while idle" rows). |
| P3 | Tool economy: the merge brief named the integration tip by SHA (`9eb0c99`); the branch had advanced to `a8e3682` and the hk pre-merge-commit gate refused the SHA (no ref points at it). One aborted merge. | Applied in-lane: merge by branch name (`codex/marketplace-native-onboarding`), `c2aa3fd`. No doc change: `dev/hooks/git_gate.py` already documents that a bare SHA is classified by the refs pointing at it; briefs that say "merge the integration tip" already mean the branch. |
| P3 | Coding standards (size): 9 maintained files plus 9 mirror copies and about 100 changed lines, over the five-file guide. | Kept: every edit is a value or sentence the `delivers` list and the coordinator named, in one consistency set that the threshold-mismatch refusal requires to land together; no split point that leaves `plan` working. |
| P3 | Tool economy: the first red run wrote its log through a relative path (`../../../../c40.tmp`) that resolved outside the repository. | Applied in-lane: the file was moved into the session scratchpad and every later log used the absolute scratchpad path. No doc change: the implementer brief already says absolute paths only. |
| P3 | Navigation: `max_live_agents` 5 rests on roster-v2's `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6`, which lives on another branch. | Applied: the reason is written beside the key in `frontier.toml` and `config.md`. Owner parent: if roster-v2 drops that env key, revisit the cap (5 stays safe under the harness default). |

No-ops: none; every edited value changes what the doctor prints, what `plan` refuses or what the
frontier dispatches. The `evals.json` "(fraction 0.45)" hint is unchanged because it still
matches a 450_000 fork_deny on a 1M window. Navigation, steering, automated checks, coding
standards, tool economy and information access are the rows above.

## Parent edits (exact text; outside `owned_paths`)

1. `.claude/agents/frontier-scheduler.md` line 35 (`with a Fable reviewer and no sibling when a
   hot path or a frozen baseline file is` -> `with an Opus reviewer (D189) and no sibling when a
   hot path or a frozen baseline file is`): owned by lane roster-v2's retro, which is applying it;
   nothing for this lane's integration to apply. Verify after roster-v2 lands:
   `grep -n "Fable reviewer" .claude/agents/frontier-scheduler.md` returns nothing.
2. `.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md` lines 858-860:
   replace
   `Context budget (C4, binding; one threshold dict in \`dev/doctor/budget.py\`): warn 400 K,`
   `fork deny 500 K, checkpoint 550 K (run session-handoff, \`dev/handoff.py write\`; delegate with small briefs), hard 650 K,`
   `all below \`autoCompactWindow\` 700 K. Until the CT-23 mods exist (A2-13, A2-14), the parent applies`
   with
   `Context budget (C4, D190, D191; one threshold dict in \`dev/doctor/budget.py\`): warn 220 K,`
   `fork deny 275 K, checkpoint 303 K (run session-handoff, \`dev/handoff.py write\`; delegate with small briefs), hard 358 K,`
   `all below the 400 K compaction point of \`autoCompactWindow\` 433000. Until the CT-23 mods exist (A2-13, A2-14), the parent applies`.
3. `task_plan.md` lines 899-900: replace
   `- Models: Opus 5.5 implementers for code lanes, Sonnet 5.5 for documentation`
   `  lanes, Fable for review, retro and synthesis, Haiku for mechanical extraction.`
   with
   `- Models: Opus 5.5 implementers for code lanes, Sonnet 5.5 for documentation`
   `  lanes, Opus for review (D189), Fable for retro and synthesis, Haiku for mechanical extraction.`
4. `lanes/compaction-40.json` (parent-owned record): status, final SHA, review and retro fields at
   integration; and `delivers` gains three entries:
   `"frontier.toml max_live_agents = 5 (roster-v2 cold review: CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6 leaves a fork slot); dev/test_ticket_frontier.py test_live_agent_hard_cap_is_five"`,
   `"scripts/frontier.py fallback defaults 0.5 -> 0.275 and 8 -> 5 (match references/config.md Default column); FABLE_KINDS without review, pinned by test_fable_kinds_match_shipped_policy"`,
   `"references/scheduler.md (cap 5, Opus reviewer for hot-path and baseline lanes) and evals/evals.json (ceilings 275000, live 4/5), both mirrors"`.
5. Optional: `task_plan.md:680` D21 row, append `; window superseded by D190 (433000)` to the
   status cell.
6. Runtime acceptance after the restart (owner parent, Information access row): `/autocompact` or
   `/context` shows a 433k (about 400K) window.
