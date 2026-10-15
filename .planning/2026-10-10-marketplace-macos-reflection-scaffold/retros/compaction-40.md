# compaction-40 retrospective: compaction at about 400K, thresholds, ceiling, Opus reviewer

Unit `compaction-40` (R-179; D188, D189, D190, D191). Worktree `.claude/worktrees/compaction-40`,
branch `claude/compaction-40`, cut from allocation commit `6257246` (base `1ec9edf`). Lane
commit `7213170`; integration tip `696e03f` merged as `5c2e2e9` (`--no-ff`, message file,
trailers, no lane branch name; clean, no conflicts). Implementer draft (Opus); review and retro
writer pending dispatch by the parent.

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

## Checks (worktree, `VIRTUAL_ENV` unset, one literal command each)

Red first: with only the tests changed, `./dev/mise run test:doctor` rc 1 (2 failures: thresholds
dict, window 700000) and `./dev/mise run test:frontier` rc 1 (4 failures: ceiling, mismatch,
cap, review model).

| Command | On `7213170` | On the merge `5c2e2e9` |
| --- | --- | --- |
| `./dev/mise run test:doctor` | rc 0 (14 tests) | rc 0 |
| `./dev/mise run test:frontier` | rc 0 (30 tests) | rc 0 |
| `diff -r .claude/skills/ticket-frontier .agents/skills/ticket-frontier` | rc 0 | rc 0 |
| `./dev/mise tasks validate` | rc 0 | rc 0 |
| `./dev/mise run check` | rc 0 (91 tests; json 2331, python 246, shell 6, toml 21) | rc 0 |
| `./dev/mise run check:acceptance-baseline` | rc 0 | rc 0 |
| `git diff --check` (worktree; on the merge `git diff --check 696e03f HEAD`) | rc 0 | rc 0 |
| `./dev/mise run doctor` | rc 0 | rc 0 |
| `./dev/mise run doctor:session-start` | rc 0, `context: auto-compact: user=true project=true · warn 220K · checkpoint 303K · fork_deny 275K · hard 358K` | rc 0, same line |
| hk pre-commit (`whitespace`, `records`) on the lane commit | passed | n/a |
| `./dev/mise run retro:gate -- compaction-40` | n/a | see the handoff (run after this record's commit) |

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
| P3 | Coding standards: `frontier.py:61` `FABLE_KINDS` still lists `"review"`; it only exempts that kind from escalation and `next` never computes a review kind, so the name now misleads once review runs on Opus. | Kept per the coordinator (no behaviour change, roster-v2 edit E note). Owner parent: rename or drop `"review"` in a later frontier lane if the dispatcher starts computing reviewer steps. |
| P3 | Automated checks: `frontier.py` fallback defaults (fraction 0.5, cap 8) disagreed with the `config.md` Default column after the change; no test reads them because every test copies the shipped config. | Applied in `7213170`: fallbacks 0.275 and 5, both mirrors; `test:frontier` rc 0, `diff -r` rc 0. No new test: the defaults apply only to a config missing the key. |
| P3 | Automated checks: `test_thresholds_below_autocompact_window...` asserted `value < window`, which would pass a threshold above the real trigger (window - 33K). | Applied in `7213170`: assertion is `value < window - 33_000` (R23 §1 formula); `test:doctor` rc 0, red run rc 1 before the values moved. |
| P3 | Information access: the runtime effect of 433000 is unverified in this lane; the window reaches a session only at the next process start (R23 §7.6) and the probe needs a fresh session. | Deferred with owner parent at the user's restart (R-175 quit-and-restart): `/autocompact` should print `Auto-compact window for Opus 5.5: 433k tokens (from settings)`; receipt is the first non-idle `compact_boundary` with `trigger: "auto"` and `preTokens` near 400,000 (exclude "Compacted while idle" rows). |
| P3 | Coding standards (size): 9 maintained files plus 9 mirror copies and about 100 changed lines, over the five-file guide. | Kept: every edit is a value or sentence the `delivers` list and the coordinator named, in one consistency set that the threshold-mismatch refusal requires to land together; no split point that leaves `plan` working. |
| P3 | Tool economy: the first red run wrote its log through a relative path (`../../../../c40.tmp`) that resolved outside the repository. | Applied in-lane: the file was moved into the session scratchpad and every later log used the absolute scratchpad path. No doc change: the implementer brief already says absolute paths only. |
| P3 | Navigation: `max_live_agents` 5 rests on roster-v2's `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6`, which lives on another branch. | Applied: the reason is written beside the key in `frontier.toml` and `config.md`. Owner parent: if roster-v2 drops that env key, revisit the cap (5 stays safe under the harness default). |

No-ops: none; every edited value changes what the doctor prints, what `plan` refuses or what the
frontier dispatches. The `evals.json` "(fraction 0.45)" hint is unchanged because it still
matches a 450_000 fork_deny on a 1M window. Navigation, steering, automated checks, coding
standards, tool economy and information access are the rows above.

## Parent edits (exact text; outside `owned_paths`)

1. `.claude/agents/frontier-scheduler.md` lines 34-35: replace
   `with a Fable reviewer and no sibling when a hot path or a frozen baseline file is` with
   `with an Opus reviewer (D189) and no sibling when a hot path or a frozen baseline file is`.
2. `.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md` lines 858-860:
   replace
   `Context budget (C4, binding; one threshold dict in \`dev/doctor/budget.py\`): warn 400 K,`
   `fork deny 500 K, checkpoint 550 K (run session-handoff, \`dev/handoff.py write\`; delegate with small briefs), hard 650 K,`
   `all below \`autoCompactWindow\` 700 K. Until the CT-23 mods exist (A2-13, A2-14), the parent applies`
   with
   `Context budget (C4, D190, D191; one threshold dict in \`dev/doctor/budget.py\`): warn 220 K,`
   `fork deny 275 K, checkpoint 303 K (run session-handoff, \`dev/handoff.py write\`; delegate with small briefs), hard 358 K,`
   `all below the 400 K compaction point of \`autoCompactWindow\` 433000. Until the CT-23 mods exist (A2-13, A2-14), the parent applies`.
3. `lanes/compaction-40.json`: status, final SHA, review and retro fields at integration
   (parent-owned record).
4. Optional: `task_plan.md:680` D21 row, append `; window superseded by D190 (433000)`.
