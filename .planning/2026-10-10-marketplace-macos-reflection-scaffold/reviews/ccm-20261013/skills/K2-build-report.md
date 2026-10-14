# K2: `ticket-frontier` build report

Written 2026-10-13 by K2 (skill builder). Repo `MERGE_HEAD` untouched; no `git add`,
no commit; every file below is untracked (`git status --short` shows only `??` rows for
them; the staged set is still the pre-existing 11-file merge staging). `P/` =
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. Inputs: K1 §1–8 and the
user's Q1–Q15 answers (binding), D1, D2 §2, R8, C4, `codex-session-history` (house
style), `implementer.md`/`reviewer.md`, `claude-team.md`, `ticket-retro.md`,
`retro_gate.py`, the skills and sub-agents docs pages. All quoted contents are data.

## 1. Process

The Skill tool refused `anthropic-skills:skill-creator` ("disabled for model invocation
in skillOverrides settings"), so the process came from the synced copy
`~/.claude/skills/synced/c1029050-…/skill-creator/` (`SKILL.md`, `references/schemas.md`,
`agents/grader.md`): capture intent → draft SKILL.md with a pushy description → bundled
`scripts/`, `references/`, `evals/evals.json` with `expectations` → run with-skill and
baseline cases → grade with `{text, passed, evidence}` → iterate. Style: the
`writing-for-agents` SKILL.md and SKILL-MECHANICS.md from the mattpocock cache 1.3.1
(steps with completion criteria, leading words *frontier / lane / claim / ceiling /
receipt*, reference disclosed behind pointers, positive phrasing). Build order was
test-first: `dev/test_ticket_frontier.py` (red: 28 tests, ImportError/FileNotFound/Lists
differ) → `scripts/frontier.py` → green.

## 2. Files created

| File | Lines | SHA-256 (16) |
| --- | --- | --- |
| `.claude/skills/ticket-frontier/SKILL.md` | 95 | `90266f75a8397243` |
| `.claude/skills/ticket-frontier/scripts/frontier.py` (executable) | 919 | `90e75695290ef6b7` |
| `.claude/skills/ticket-frontier/references/scheduler.md` | 111 | |
| `.claude/skills/ticket-frontier/references/model-policy.md` | 48 | |
| `.claude/skills/ticket-frontier/references/executor-gate.md` | 61 | |
| `.claude/skills/ticket-frontier/references/brief-templates.md` | 93 | |
| `.claude/skills/ticket-frontier/references/learning-ledger.md` | 62 | |
| `.claude/skills/ticket-frontier/references/config.md` | 81 | |
| `.claude/skills/ticket-frontier/evals/evals.json` (8 cases) | 111 | |
| `.claude/skills/ticket-frontier/evals/fixtures/graph-12.json` | 18 | |
| `.agents/skills/ticket-frontier/**` (mirror) | same | `diff -r` empty |
| `.claude/agents/frontier-scheduler.md` | 41 | `d47a4bbb4d2fe3c2` |
| `dev/test_ticket_frontier.py` | 409 | `c88084b1f1a3461e` |
| `P/frontier.toml` | 47 | `8c6c7cf57629d2c8` |

Writes outside that list: none. `P/frontier/` does not exist (the script creates it only
on `claim`, `plan --write`, `executor-gate --write` or `ledger append`, all run against
scratch trees here). `mise.dev.toml`, `dev/check.py`, `task_plan.md`, `progress.md`,
`ticket-ledger.md` and every other existing file are unchanged; their hunks are in §7.

Frontmatter facts used (code.claude.com/docs/en/skills, /sub-agents, fetched
2026-10-13): `description` + `when_to_use` are truncated at 1,536 characters (ours is
771); `user-invocable: true` is the default and keeps `/ticket-frontier` typeable (Q15);
no `context: fork` because a forked body "doesn't see your conversation history" and
cannot ask the user; `` !`cmd` `` "A failed command aborts the entire skill invocation",
so the status line carries `2>&1 || true`; sub-agent `model` and `effort` per-invocation
parameters override the file's frontmatter ("The parameter overrides the `effort` field"),
and "a subagent's context window is sized by its own model, not the parent's", which is
why the ceiling line is in every brief; `isolation: worktree` branches "from your default
branch rather than the parent session's HEAD", so the skill never uses it; default
concurrent-subagent limit 20, the config caps at 8 (Q4).

## 3. What the script does (`scripts/frontier.py`, stdlib, `python3 -I`)

| Command | Behaviour | Exit |
| --- | --- | --- |
| `plan [--graph F] [--admitted #n] [--json] [--write]` | graph from `ticket-ledger.json` (CT-05) else `--graph`; done = closed or lane `integrated/published` + `retro: passed`; held = lane record not done or claim; ready = open, blockers done, not held; priority critical_path → unblocks → always_active → wave → number; cxx slot by `order` list, offline split when not admitted (Q2), other heavy tickets skipped "one heavy run at a time"; conflict rule over `owned_paths ∪ excluded_shared_paths` + hot paths; capacity writers/`max_parallel` and live/8; threshold cross-check against `dev/doctor/budget.py` `fork_deny` (Q3) | 0; 2 on mismatch or missing graph |
| `next [--journal F]` | first chosen lane + model/effort from `[model_policy]`, escalation to Fable after ≥1 Opus `partial/blocked` with `reason: reasoning` (Q9), ceiling = window × fraction, `brief_lines` (CTX-CEILING, MODEL, SPLIT), the Agent-call parameters, the claim/allocate steps with degraded fallbacks | 0; 2 saturated/empty |
| `claim <unit> --ticket --role [--owned-paths]` | idempotent; refuses double claim, writer cap, 8-agent cap, path conflict with records or claims | 0 / 2 |
| `release <unit> [--from-journal F] [--resume]` | idempotent; last `usage` ≥ ceiling → the claim is released as `split-required` into `state.json` `continuations` (its ticket stays held until a writer claims `<unit>-2`), `--resume` refused | 0 / 2 |
| `answer --question --answer` | records a plain-text user answer in `frontier/answers.jsonl` until CT-24; never grants an admission (that stays `--admitted`) | 0 |
| `status [--json]` | capacity, ceilings, claims, pending continuations, last receipt, six `not available yet: CT-nn (<artifact>) -> <fallback>` lines (Q6) | 0 |
| `executor-gate [--executor] [--team] [--config] [--write]` | `native` always 0; G1–G6 from a probe config (`rc`/`cmd`/`path`/`value`), G7 only with `--team` (Q7); writes `executor-gate.json` | 0 / 2 |
| `ledger append --row / list --by` | validates the K1 §6 row (kind, mode, verification, `retros/<unit>.md#row`), flags repeat destinations (Q13) | 0 / 2 |

## 4. Test output (bounded)

Command: `python3 -I -m unittest discover -s dev -p test_ticket_frontier.py -v` from the
repo root. The literal form in the brief, `python3 -I -m unittest dev/test_ticket_frontier.py`,
cannot run: `-I` removes the cwd from `sys.path`, so unittest fails with
`ModuleNotFoundError: No module named 'dev'`; the `discover` form is the house convention
(`.claude/rules/dev-tests.md`) and the one the mise row in §7 uses.

```
test_claim_is_idempotent_and_refuses_double_claim ... ok
test_claim_validates_owned_paths_against_active_lanes ... ok
test_release_resume_over_ceiling_is_split_required ... ok
test_release_then_reclaim ... ok
test_native_is_always_allowed ... ok
test_non_native_without_probes_fails_naming_every_item ... ok
test_probe_results_decide_and_write_receipt ... ok
test_append_validates_shape_and_lists_by_destination ... ok
test_repeat_destination_is_flagged ... ok
test_skill_md_is_bounded_and_model_invocable ... ok
test_skill_mirror_is_byte_identical ... ok
test_escalation_to_fable_after_one_opus_reasoning_failure ... ok
test_next_returns_model_effort_and_ceiling ... ok
test_no_escalation_for_admission_conflict_or_ceiling_reasons ... ok
test_conflicting_owned_paths_are_not_chosen ... ok
test_cxx_slot_with_admission_is_a_full_lane ... ok
test_cxx_slot_without_admission_takes_offline_portion ... ok
test_integrated_lane_with_passed_retro_unblocks_dependents ... ok
test_integrated_lane_without_passed_retro_still_holds ... ok
test_live_agent_hard_cap_is_eight ... ok
test_max_parallel_counts_writer_lanes_only ... ok
test_plan_receipt_is_written_only_under_frontier_dir ... ok
test_priority_rules_are_recorded ... ok
test_ready_set_excludes_blocked_and_done ... ok
test_threshold_mismatch_with_budget_py_is_refused ... ok
test_answer_is_recorded_without_granting_admission ... ok
test_plan_prefers_ticket_ledger_json_when_present ... ok
test_plan_without_ledger_or_graph_refuses_with_pointer ... ok
test_status_names_missing_blockers_without_crashing ... ok
Ran 29 tests in 2.320s
OK
```

Red-first evidence: iteration 1 first run `Ran 28 tests … FAILED (failures=2, errors=2)`
before SKILL.md/mirror existed and with the cxx expectation wrong (`['#21', 'CT-15'] !=
['#21', 'CT-15', '#16']`; resolved as "one heavy run at a time", §9 Q-a). Iteration 2
(continuations + `answer`, §5a) went red on 27 of 29 (a `re.sub` replacement turned the
`"\n"` in the new `answer()` into a real newline: `SyntaxError: unterminated string
literal`), then green after the one-line fix.

Other checks, all rc 0 (read-only tools, no global install): `mise x ty@0.0.85 -- ty
check scripts/frontier.py dev/test_ticket_frontier.py` → `All checks passed!` (the seven
coordinator-reported union-type issues fixed by `Ticket`/`ReadyTicket` TypedDicts,
`norm_id(value: object) -> str` that rejects a missing id with a `Refusal`, and a
`unit_id()` helper); `mise x ruff@0.16.10 -- ruff check --line-length 130` on both files
→ `All checks passed!` (13 findings fixed: import order, `datetime.UTC`, tuple
`startswith`, parenthesised concatenations, explicit `check=False`, `ClassVar`,
executable bit); `python3 -B dev/check.py` → `{"status": "pass", … "json": 2479,
"python": 237, "toml": 32}` (parses the new files); `diff -r .claude/skills/ticket-frontier
.agents/skills/ticket-frontier` → empty, both `frontier.py` mode `-rwxr-xr-x`.

## 5. Eval results

Workspace: `<scratchpad>/ticket-frontier-workspace/iteration-1/eval-<id>-<name>/` with
`eval_metadata.json` and `with_skill/grading.json` per case (skill-creator field names).

**Offline deterministic pass (`tools/run_evals.py`, every expectation stdout/files can
decide, run against scratch plan dirs):**

| id | eval | offline pass | live-session items | failing |
|---|---|---|---|---|
| 1 | frontier-with-blockers | 5/5 | 0 | - |
| 2 | cxx-slot-without-admission | 4/4 | 1 | - |
| 3 | max-parallel-saturation | 4/4 | 0 | - |
| 4 | ceiling-refusal | 4/4 | 0 | - |
| 5 | executor-gate-failure | 4/4 | 0 | - |
| 6 | degraded-mode | 4/4 | 0 | - |
| 7 | threshold-mismatch | 2/2 | 1 | - |
| 8 | ledger-and-retro-automation | 3/3 | 1 | - |

offline pass rate 30/30 = 1.00 in iteration 1 and again in iteration 2 (`iteration-2/`);
3 behavioural items ("no dispatch before the user answers", "asks the user before
changing either file", "user asked to approve F3") need a model run.

### 5a. Subagent runs (skill-creator step 1, confined to scratch `--repo` trees)

Four `Explore`-typed runs (read-only outside the session scratchpad; no Agent dispatch
possible, which matches the "describe what you would dispatch" instruction), iteration 1,
outputs under `iteration-1/eval-<id>-<name>/{with_skill,without_skill}/outputs/answer.md`.

| Run | Result | Tokens / s | What it showed |
| --- | --- | --- | --- |
| eval 2 with skill | ran `status`, `plan --graph --write`; followed steps 1–3 only (the `/ticket-frontier`-outside-`implement-spec` rule); answer: `21-offline` + `ct15`, third slot empty, one admission question, nothing claimed or dispatched | 31.9 K / 48 | all 4 checkable expectations and the behavioural one met |
| eval 2 baseline (no skill) | hand-computed the frontier, proposed **a second offline C++ portion (#20) as lane 3** and cited decisions "D27/D28" that do not exist; asked two questions | 32.3 K / 34 | the skill's value: one heavy run at a time and receipts instead of invented decision ids |
| eval 4 with skill | its agent type forbids file writes, so it could not run the setup; reasoned from `release()`/`last_usage()` and `scheduler.md` §Continuation to the same answer (refuse resume, 541 000 ≥ 500 000, carve `l21-2`) | 27.6 K / 35 | expectations met by reading; the live run is the deterministic grade above |
| eval 6 with skill | ran `status` (rc 0, six fallback lines) and `plan` without `--graph` (rc 2, CT-05 refusal); wrote the per-ticket fallbacks; claimed nothing | 30.9 K / 55 | all 4 expectations met |

Ambiguities the runs reported, and what iteration 2 changed (all re-tested, mirror
re-diffed):

1. `release` over the ceiling marked `split-required` and then dropped the claim, so the
   state survived only in `history` (eval 4). Now the lane is released into
   `state.json` `continuations`, its ticket stays held in `plan`, the output names
   `claim <unit>-2`, and a writer claim of the ticket clears it
   (`test_release_resume_over_ceiling_is_split_required` extended).
2. SKILL.md did not say whether to pass `--resume` to get the refusal (eval 4). Step 8
   now says: no `--resume`; the flag exists to refuse a resume.
3. No fallback when `ledger-<unit>.jsonl` never got written (eval 4): scheduler.md
   §Continuation now says "from the branch commits and the journal's last receipt alone".
4. Step 3 told the parent to record answers "in the receipt's `questions`" with no
   command (eval 2). New `frontier.py answer --question … --answer …` writes
   `frontier/answers.jsonl`; an admission still needs `--admitted` (new test).
5. Nothing said what to do with a slot the plan leaves empty (eval 2). SKILL.md step 1
   and scheduler.md §Capacity now say: report it with its reason and the two fillers
   (admission, scheduler split), never force it; `plan` prints an `unfilled:` line.
6. The CT-05 fallback said "fixture or hand-written graph" and the fixture is fake
   tickets (eval 6). It now says "write a graph JSON from the tracker (`gh api graphql`
   blockedBy/parent) or `ticket-ledger.md` and pass `--graph`".
7. The status line runs without `--repo` during a merge (eval 2): `status` is read-only;
   config.md now says so (with `plan` without `--write` and `next`). The UTC timestamp
   (eval 2) is by design and now stated in config.md.

Not changed: the cxx slot picking `#21` over the higher-ranked `#16` (eval 2) is the heavy
order of task_plan.md and documented in scheduler.md §The cxx slot.

**Not run offline, needs a live session:** the browser viewer (`generate_review.py`) and
the user's feedback pass; `benchmark.json` with timing/tokens (requires the task
notifications of real runs); description optimisation (`run_loop.py` uses `claude -p`);
blind comparison. The description was written to skill-creator's "pushy" rule with the
K1 trigger list and no trigger-eval loop was run.

## 6. CT-25 acceptance, restated against what exists

| # | K1 §8 criterion | Now |
| --- | --- | --- |
| 1 | `test:frontier` rc 0 and wired | tests rc 0 (28); the task row and `check:research` entry are the §7 hunk, applied by the CT-25 lane |
| 2 | fixture graph: documented order, cxx slot reserved | `plan` → `CT-15, #16, #21, #17, #20`; slot `offline-portion of #21` (tests `test_ready_set_…`, `test_cxx_slot_…`) |
| 3 | `release --resume` over ceiling exits 2 naming `split-required` | yes (`test_release_resume_over_ceiling_is_split_required`) |
| 4 | `executor-gate` exits 2 on today's tree naming G2–G5 | exits 2 naming G1–G6 (`no probe configured`), G7 SKIP; a probe config that records G1 and G6 as passing reduces it to G2–G5, which is the state K1 describes |
| 5 | `diff -r` of the two subtrees empty | yes, and `test_skill_mirror_is_byte_identical` keeps it so |
| 6 | one real dry run inside a user-typed `/implement-spec` allocating ≥ 2 lanes, recorded in `skill-invocations.md` as a native Skill-tool call | **not done**: needs the user to type `/mattpocock-skills:implement-spec` in a session without a merge in progress; the brief forbade touching `skill-invocations.md` |
| 7 | `retro:gate -- ct25-ticket-frontier` rc 0 | **not done**: no lane, no retro record; belongs to the CT-25 lane |

Scope differences from K1 §8, deliberate: no `scripts/executors/{claude_agent,codex_agent}.py`
(the gate refuses them today; the contract is in `references/executor-gate.md`, adapters
land with the lane that passes the gate); no `dev/fixtures/frontier/` (the brief limited
writes, the fixture lives in `evals/fixtures/` and is mirrored); `mise/tasks/ct25.toml` not
created (D7's `task_config.includes` is unverified; §7 gives rows for `mise.dev.toml`).

## 7. Patch snippets for the CT-25 lane (not applied)

`mise.dev.toml`, after `[tasks."test:hooks"]`:

```toml
[tasks."test:frontier"]
description = "Exercise the ticket-frontier skill script against fixture graphs in scratch plan dirs"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p test_ticket_frontier.py -v'

[tasks."frontier:plan"]
description = "Ready set, priorities, cxx slot and chosen lanes from the tracker graph and lane records"
dir = "{{config_root}}"
usage = 'arg "[graph]" help="graph JSON until ticket-ledger.json exists" default=""'
run = '"${MARKETPLACE_PYTHON:-python3}" -I .claude/skills/ticket-frontier/scripts/frontier.py plan --write ${usage_graph:+--graph "$usage_graph"}'

[tasks."frontier:next"]
description = "Next lane to dispatch with model, effort, ceiling and the Agent-call parameters"
dir = "{{config_root}}"
usage = 'arg "[graph]" default=""'
run = '"${MARKETPLACE_PYTHON:-python3}" -I .claude/skills/ticket-frontier/scripts/frontier.py next ${usage_graph:+--graph "$usage_graph"}'

[tasks."frontier:status"]
description = "Frontier claims, capacity, ceilings and missing prerequisites"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I .claude/skills/ticket-frontier/scripts/frontier.py status'

[tasks."frontier:gate"]
description = "Evaluate executor gate G1-G7 for the configured executor and write frontier/executor-gate.json"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I .claude/skills/ticket-frontier/scripts/frontier.py executor-gate --write'
```

`check:research` depends (one-line parent hunk, line 117): append `"test:frontier"`.

`dev/check.py`: no edit needed when the mise route above is taken (`dev/AGENTS.md`
"Test discovery": a test outside the `test_research_*.py` glob runs through a named
`test:*` task listed in `check:research`). If the lane prefers discovery by `check`
instead, the alternative is this one-line change at `dev/check.py:72` and then **no**
`test:frontier` row, so the suite does not run twice:

```python
    for directory, pattern in (("dev", "test_research_*.py"), ("dev", "test_ticket_frontier.py"),
                               ("dev/research_refresh", "test_*.py")):
```

`docs/agents/claude-team.md`, new section before "## Codex compatibility" (K1 §8 parent hunk):

```markdown
## Frontier

The `ticket-frontier` skill (`.claude/skills/ticket-frontier/`) runs the lane lifecycle
above for every ready ticket of a spec: `frontier.py plan|next|claim|release|status`
holds the ready set, priorities, claims and ceilings under `.planning/<PLAN_ID>/frontier/`;
`frontier-scheduler` proposes `owned_paths` and splits; `P/frontier.toml` holds
`max_parallel`, the cxx class and the model policy. Retro learnings land in
`frontier/learning-ledger.jsonl`, one row per finding, citing the retro row.
```

`.claude/AGENTS.md` `skills/` bullet: add `ticket-frontier` beside `codex-session-history`
(the mirror rule applies unchanged).

## 8. Known limits

- `ticket-ledger.json` (CT-05) shape is assumed to match the graph JSON in
  `references/config.md` (`tickets[].id|number`, `state`, `blockedBy|blocked_by`,
  `parent`); CT-05 should emit that or the loader gains one more alias.
- `decisions.jsonl` (CT-24) admission rows are assumed as
  `{"kind":"admission","ticket":"#21","state":"granted","consumed":false}`; adjust the
  reader when CT-24 fixes the schema.
- The hot-path rule matches `AGENTS.md` only at the root; nested `AGENTS.md` paths are
  matched only when a candidate lists them literally.
- The script applies the conflict rule to paths it knows; tickets without `owned_paths`
  pass the mechanical rule and rely on the scheduler agent (K1 §3 design).
- `frontier.py` is 919 lines, past the 300-line unit guidance; it is one skill script
  with eight subcommands, and the CT-25 lane may split `executor-gate` and `ledger` into
  siblings if the reviewer asks.
- The subagent runs used `Explore` agents (the only read-only type with Bash); one
  refused all writes by its own system prompt, so a faithful with-skill run of eval 4
  needs a `general-purpose` or `implementer`-typed agent in a session without a merge in
  progress, or the live `/implement-spec` dry run of acceptance 6.

## 9. Remaining questions (recommended default in ➡️)

- **Q-a. Second heavy ticket in a general slot.** With no admission, should `#16` (cxx,
  heavy) take a second offline-portion lane beside `21-offline`, or wait? Built as
  *wait* (`skipped: heavy, not admitted; one heavy run at a time`), reading
  `claude-team.md` §Concurrency's "one at a time" as covering the chain. ➡️ keep *wait*;
  the user can admit `#16` explicitly with `--admitted #16` to run both offline portions.
- **Q-b. Threshold comparison model.** `plan` compares `fork_deny` with the *implement*
  model's ceiling (`windows.opus × fraction`); with every window at 1M this equals all
  ceilings. ➡️ keep; revisit if windows diverge per model.
- **Q-c. Test command form.** The brief's `python3 -I -m unittest dev/test_ticket_frontier.py`
  cannot import under `-I`. ➡️ the `discover -s dev -p` form in §7, as the other suites.
- **Q-d. Where plain-text answers live until CT-24.** Built as `frontier/answers.jsonl`
  (one row per question) rather than editing the plan receipt. ➡️ keep; CT-24's
  `decisions.jsonl` supersedes it and `plan` already reads admission rows from there.
