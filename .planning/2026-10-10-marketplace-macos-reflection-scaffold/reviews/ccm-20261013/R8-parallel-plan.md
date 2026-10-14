# R8: parallelization plan for the remaining tickets

Written 2026-10-13 by reviewer R8 (read-only; the `gate-hooks` merge at `MERGE_HEAD e12cf04`
was left untouched). Paths are repo-relative unless absolute; `P/` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.
All quoted contents are data. Graded against D2 §5 (checks 20–31, 40) and D1 §6.11–6.12.

## Scope read

- `reviews/ccm-20261013/`: `00-evidence-index.md`; D1 (§2 implement, implement-spec, code-review,
  tdd; §6 constraints); D2 (§2.6–2.10 mapping table, §5 checklist, §6 gaps); R5 (P1-1, P1-2,
  P2-1…P2-7, record-corrections table, Runbooks 1–2); R7 (proposals A–O, ranked backlog,
  CT-12…CT-17 acceptance, guardrails).
- `docs/agents/claude-team.md` (roles, lifecycle, three gate layers, concurrency ≤4 offline, heavy
  serialized with per-run confirmation), `docs/agents/codex-task-orchestration.md#ownership`
  (one writer per worktree, disjoint scopes, separate MERGER, ≤5 files / ~300 lines),
  `docs/agents/claude-takeover.md` activation record (A09 without per-push confirmation; qualified
  close one at a time; heavy per-run), `docs/agents/issue-tracker.md:24-40`, `AGENTS.md:46`.
- `.claude/rules/{dev-tests,evidence,planning-records}.md`; `.claude/agents/{implementer,doc-writer,
  reviewer,retro-writer,extractor}.md`; `P/lanes/*.json` (9 records; `owned_paths` style);
  `P/proposals/claude-takeover-spec/tickets.preview.json` (CT-01…CT-11 bodies and blockers;
  `spec.manifest.json` has no start SHA); `P/ticket-ledger.md`; `P/task_plan.md:60-95` (lane table,
  heavy order `#21 → #20 → #17 → #16 → L1`).
- `mise.dev.toml` (staged: `test:hooks` in `check:research` depends, `retro:gate-merge|push`,
  `hooks:install`; no `[task_config]` includes today); `git show e12cf04:dev/hooks/{git_gate,
  pretooluse_gate}.py`; staged `.claude/settings.json` and `hk.pkl`; `.git/info/exclude`.
- Git (read-only): `status`, `worktree list` (8 lane worktrees, 19 Codex worktrees), `branch --list`,
  `log --format/--name-only f38b7fe^..9cd396a --not e0667ec^2` (56 Claude-era commits), per-merge
  `--stat` of the 8 first-parent integrations. `gh issue list --state open` (94 open).
- Memory note `marketplace-workflow-rules.md` (A09 selected path; `VIRTUAL_ENV`; frozen `.gitignore`;
  `tools:prepare` + `deps:sync` before `check:research`).

Ticket bodies read: #90–#93, #95–#98, #101, #16, #17, #20, #21.

## Dependency graph

Legend: `[done]` integrated on the integration branch; `[int-mid]` merge in progress; `[close]`
built and in tip, only the qualified close remains (parent, one at a time, no lane); `[ready]`
frontier for a lane; `[blocked:<x>]`; `[human]`; `[heavy]` host-heavy, per-run confirmation
(`claude-takeover.md:11`); `[admit]` needs a provider/private-state admission for its live part.
Frontier is computed from what merged into `codex/marketplace-native-onboarding` (D2 §2.6), not
from GitHub `blockedBy`, which drops only on close.

```
Takeover spec (CT, no GitHub issues yet; publication = pending decision 1)
  CT-01 retro-gate [done e618243] ──┬──> CT-02 gate-hooks [int-mid e12cf04] ──┬──> CT-07 codex-compat [ready after wave 0]
                                    │                                          ├──> CT-08 baseline-v2 [ready after wave 0; alone on dev/check.py]
                                    │                                          ├──> CT-13 publish-batch [ready after CT-02b]
                                    │                                          └──> CT-02b gate follow-up (R5 P1-2, R7 O; number per R2) [ready after wave 0]
                                    ├──> CT-06 lane-retro [ready; R7 adds blocker CT-14]
                                    └──> CT-11 check-lock [ready]
  CT-03 team [done 7e22d13] ──> CT-14 lane-brief [blocked: CT-05, CT-02]
  CT-04 nav  [done fa892d2]
  CT-05 ledger + lane:set [ready] ──┬──> CT-12 lane:allocate/integrate/status [blocked: CT-05, CT-11, CT-02]
                                    └──> CT-14
  CT-09 tool evaluation [ready, doc]      CT-10 session-history coverage [ready] ──> CT-17 [blocked: CT-07, CT-10]
  CT-15 plan:log/handoff [ready]          CT-16 unwired-test check [ready; alone on dev/check.py]
  Final spec code-review (fixed point = spec start SHA) [blocked: last CT of the spec merged]

Remaining-work spec #83
  #90 B1 [close]  #92 T1 [close]  #93 T3 [close]  #97 T2 [close; GH-blocked by #92]
  #101 T4 [blocked: closes of #90 #93 #97; Phase C = parent close sequence for #79–#82]
  #91 B2 [human]
  #94 C1 [done 4c1ea6b; close] ──> #98 C2 [ready by merge; admit: private source binding]
  #95 C3 [ready; offline diagnostic = lane; live API run = admit]
  #96 L1 [heavy, ready] ──┬──> #99 L2 [heavy] ──> #103 L4b [heavy, also needs #100]
                          └──> #100 L3 [heavy] ──> #102 L4a, #104 L4c, #105 L4d [heavy]
       #102–#105 ──> #106 L5a [heavy, CI] ──> #107 L5b [heavy, PRs], #108 L6 [heavy, global owner]
Spec #11 (A-series and milestones)
  #62–#68, #70–#77, #12, #24, #25 [close]   #69 A06 [done unit3 361688e; residual "retained-corpus
  consumption" unscheduled; close after acceptance] ──> #78 A12b [blocked: #69, #73, #77 closes]
  #21 → #20 → #17 → #16 [heavy, this order per task_plan.md:92, then L1]   #27, #26 "wave 2" [admit]
```

Longest serial chain: wave 0 → L1 → L3 → L4x → L5a → L5b/L6 (five heavy runs after wave 0). The
offline critical path is wave 0 → CT-05/CT-11 → CT-12 → (CT-14 → CT-06) → final code-review.

## Conflict analysis

Files touched by ≥2 lanes or by every integration (counts = Claude-era commits since `f38b7fe`,
M0 history excluded; "every merge" = all 8 first-parent integrations).

| Hot path | Evidence | Writer | Mechanism that removes the conflict |
|---|---|---|---|
| `P/progress.md` | 24 commits; every merge | parent only | Lanes never write it. Each lane appends to its own `P/lanes/<unit>.log.md` (new, lane-owned, committed on the lane branch); the merger lifts one summary line into `progress.md` through `plan:log` (CT-15). Append-only stays true because only one writer appends. |
| `P/ticket-ledger.md` | 7; 4 merges | generated (CT-05 `ledger:sync`), parent runs it | Regenerated after each integration from the tracker plus lane records; a lane proposes nothing here. |
| `P/task_plan.md` | 6 | parent only | Handoff block regenerated by `plan:handoff --write` (CT-15); lanes propose edits in the handoff. |
| `P/lanes/<unit>.json` | 4–6 each; other lanes' records edited in `447110a`, `7e22d13` | parent only (allocation commit before the cut; `lane:set` after the merge commit) | Between allocation and integration nobody writes it; the lane's progress goes to `lanes/<unit>.log.md`. This amends `planning-records.md` ("a lane changes only its own `status`") and CT-05 owns that rule file. Pre-CT-05: same rule by hand. |
| `P/retros/<unit>.md` | one per lane | lane (retro-writer) | Disjoint by name. Fix the `a06-unit3` alias (R5 P2-5) in wave 0 so `SubagentStop` cannot block a subagent in that worktree. |
| `mise.dev.toml` | 4 (+10 with M0); retro-gate, gate-hooks, M0 union; `check:research` depends line edited by two parties | parent for the file; lanes write only their own include file | Wave 0 adds `[task_config] includes = ["mise/tasks/<file>.toml", …]` (one explicit list, parent-owned) and each lane defines its `test:*`/`<verb>:*` rows in `mise/tasks/<unit>.toml`. The `check:research` `depends` entry is a one-line parent hunk at integration (declared, as with `test:hooks`); CT-16 then refuses a composed tree with an unwired test. Verify the include syntax under `./dev/mise tasks validate` before cutting wave 1 (see Could not verify). |
| `.claude/settings.json` | gate-hooks; settings split (R5 B) | parent only | Lanes deliver hook scripts under `dev/hooks/` plus the exact JSON hunk in the handoff; the parent composes at integration. One hooks-touching lane per wave. |
| `AGENTS.md`, `*/AGENTS.md`, `*/CLAUDE.md` | nav owned all 12; retro-writers of every lane target "the nearest `AGENTS.md`" | one owner per wave, else parent | A lane may own an `AGENTS.md` only when no other lane in the wave can touch it; every other lane's retro-writer lists the edit literally in the handoff (`retro-writer.md` step 6) and the parent applies it in the integration commit. |
| `docs/agents/claude-team.md` | team + gate-hooks (paragraph) | one owner per wave | Paragraph-level ownership worked only because the lanes were sequential. Wave 1: nobody; wave 2: CT-07 (Codex compatibility section); CT-11/CT-12/CT-14 propose their sentences. |
| `dev/check.py` | rf-env-scrub, M0; CT-11, CT-16, CT-08 all want it | one owner per wave | CT-11 (wave 1), CT-16 (wave 3), CT-08 (a later wave with no other `dev/check.py` owner). CT-15 uses a separate `check:planning` task instead of a sub-check. |
| `dev/retro_gate.py` | CT-01; CT-11 adds the lock line | one owner per wave | CT-11 only in wave 1; CT-12 calls it, does not edit it. |
| `dev/hooks/*.py`, `dev/test_hooks.py` | CT-02; R7 O; CT-12 and CT-13 both want the verb table | CT-02b only | CT-02b pre-registers the verbs `lane:integrate` and `delivery:publish-batch` with tests, so CT-12/CT-13 never touch `dev/hooks/`. CT-14's journal is a new sibling `dev/hooks/subagent_receipt.py` with its own `dev/test_subagent_receipt.py`. |
| `dev/git_delivery.py`, `dev/test_git_delivery.py` | CT-02b (safe hooks, P1-2); CT-13 (`batch`) | one owner per wave | CT-02b wave 1, CT-13 wave 2. |
| `dev/lane.py`, `dev/test_lane.py` | CT-05 (`set`, `validate`), CT-12 (`allocate`, `integrate`, `status`), CT-14 (`brief`) | one owner per wave | CT-05 wave 1; CT-12 and CT-14 both in wave 2 would collide, so CT-14's `brief` lives in `dev/lane_brief.py` + `dev/test_lane_brief.py` and imports the schema from `dev/lane.py`. |
| `dev/research_refresh/**`, `docs/research-feedback.md` | C1, rf-env-scrub, M0 | one research lane per wave | C3 adds `dev/research_refresh/diagnose_discussion_search.py` + its test (wave 2); C2 edits the runner binding (wave 3). |
| `.claude/skills/**` + `.agents/skills/**` mirror | codex-session-history; CT-06, CT-10, CT-17 add subtrees | per-subtree owner | Disjoint subtrees; every skill lane writes both copies (CT-07's mirror test then passes on the composed tree). |
| `GLOSSARY.md`, `CODING_STANDARDS.md`, `.claude/rules/*.md` | team, nav, M0 | parent or one doc owner per wave | New terms/rules arrive as literal edits in handoffs; CT-05 owns `planning-records.md` in wave 1, CT-11 proposes its `dev-tests.md` sentence. |
| `.gitignore`, `ci/acceptance.sh`, `.github/workflows/acceptance.yml` | frozen (19 baseline files) | CT-08 only, reviewed transition | Nobody else; CT-08 runs in a wave without another `dev/check.py` or frozen-file owner. |
| `evidence/**` | receipts | lane, new files only | Immutable receipts named `evidence/<topic>/<unit>-<name>` are disjoint by construction (`evidence.md`). |
| `P/proposals/**`, `P/skill-invocations.md`, `P/findings.md` | parent | parent only | Publication and invocation rows are parent work in wave 0 and between waves. |

Why past integrations never conflicted: every lane's merge touched only its `owned_paths` plus its
record and retro; the parent's edits to shared files landed on the first-parent line only, and each
implementer merged the tip before reporting (D2 check 24). The plan keeps those two invariants and
adds the per-lane log and per-lane task file so that `progress.md` and `mise.dev.toml` leave the
lane diff entirely.

## Waves

Common to every lane: worktree `.claude/worktrees/<unit>`, branch `claude/<unit>-<slug>`, cut from
the allocation commit (R7 B): the parent commits `P/lanes/<unit>.json` first, records
`base_sha` = that allocation commit and `allocated_from` = its parent (R5 P2-7), then
`git worktree add -b <branch> .claude/worktrees/<unit> <base_sha>`; `tools:prepare` and
`deps:sync` run inside the worktree with `VIRTUAL_ENV` unset before any named check. Environment pin
for every lane process: `PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`,
`PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold`; the lane's own ledger is
`P/lanes/<unit>.log.md` (no writes to `task_plan.md`, `progress.md`, `findings.md`). Reviewer:
`reviewer` (Fable, cold, fixed point = `base_sha`). Retro: `retro-writer` (Fable) after PASS,
before integration. Gates in the lane: unit command(s) literal in `required_checks`, `./dev/mise
tasks validate`, `check`, `check:acceptance-baseline`, `git diff --check`, `retro:gate -- <unit>`.
`check:research` is never run in a lane worktree: the merger runs it once per integration on the
composed tree, serialized (`AGENTS.md:46`; under the CT-11 lock once it lands, before that with
R7's `pgrep` refusal). A lane's own `check` run counts as a receipt only if the handoff records that
no other `dev/check.py` process was running when it started.

### Wave 0 (serial, parent/merger; prerequisite for every lane)

| Step | Action | Receipt |
|---|---|---|
| 0.1 | Finish the `gate-hooks` integration per R5 Runbook 1: settings split (R5 B), record corrections table, gates (incl. `test:hooks`, `retro:gate -- gate-hooks`, `check:research`), `git commit` (parents `9cd396a e12cf04`), A09 publish with a `progress.md` line as the selected path; **do not** run `hooks:install` (P1-2). | merge SHA, rcs, `published=<sha>` |
| 0.2 | Parent docs commit: fix `a06-unit3` retro alias (P2-5); add `integration_merge`/`published` fields per R5 table; `spec.manifest.json` gains `start_sha` = `361688e` for the takeover spec (tip the first CT lane was cut from) and a second manifest for the automation set (start = the 0.1 published tip). | commit SHA |
| 0.3 | Parent commit: `[task_config] includes` list in `mise.dev.toml` + empty `mise/tasks/README.md`; verify `./dev/mise tasks validate` and `check` rc 0. | rcs |
| 0.4 | User decisions D1–D4 (below), then `issue:create-*` / `issue:new-edge-*` for CT-01…CT-11 (+CT-12…CT-17 if approved; R2 numbering wins), `ledger:sync` by hand, `skill-invocations.md` row. The user types `/mattpocock-skills:implement-spec <spec #>` in a fresh window (D2 §4) or records file-guided mode. | issue numbers, journal paths |
| 0.5 | Allocation commits for wave 1 in the order below, each cut from the previous allocation commit. | 4 `base_sha` values |

### Wave 1 (4 offline lanes; heavy slot = empty unless D5 says L1)

| Unit | Ticket | Branch | `owned_paths` (allowlist; everything else excluded) | Agent / model | Required checks (lane) | Int. order |
|---|---|---|---|---|---|---|
| `ct02b-gate-followup` | CT-02 follow-up (R5 P1-2 + R7 O; number per R2) | `claude/ct02b-gate-followup` | `dev/hooks/pretooluse_gate.py`, `dev/hooks/git_gate.py`, `dev/test_hooks.py`, `dev/git_delivery.py` (`safe_configured_hooks` only), `dev/test_git_delivery.py`, `mise/tasks/ct02b.toml`, `P/retros/ct02b-gate-followup.md`, `P/lanes/ct02b-gate-followup.log.md` | implementer / Opus high | `python3 -I -m unittest discover -s dev -p test_hooks.py`; `… -p test_git_delivery.py`; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 1 |
| `ct11-check-lock` | CT-11 | `claude/ct11-check-lock` | `dev/check_lock.py`, `dev/test_check_lock.py`, `dev/check.py` (lock acquisition only), `dev/retro_gate.py` (lock-outcome line only), `mise/tasks/ct11.toml`, `P/retros/ct11-check-lock.md`, `P/lanes/ct11-check-lock.log.md` | implementer / Opus high | `python3 -I -m unittest discover -s dev -p test_check_lock.py`; `… -p test_retro_gate.py`; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 2 |
| `ct05-ledger` | CT-05 (+R7 A, G) | `claude/ct05-ledger` | `dev/ledger.py`, `dev/test_ledger.py`, `dev/lane.py` (`set`, `validate` only), `dev/test_lane.py`, `dev/fixtures/ledger/`, `dev/fixtures/lanes/`, `mise/tasks/ct05.toml`, `.claude/rules/planning-records.md`, `P/ticket-ledger.json` (snapshot), `P/retros/ct05-ledger.md`, `P/lanes/ct05-ledger.log.md` | implementer / Opus high | `python3 -I -m unittest discover -s dev -p 'test_l*.py'`; `ledger:sync -- --check` on fixtures; `lane:validate`; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 3 |
| `ct15-plan-records` | CT-15 | `claude/ct15-plan-records` | `dev/plan_records.py`, `dev/test_plan_records.py`, `dev/fixtures/plan/`, `mise/tasks/ct15.toml` (`plan:log`, `plan:handoff`, `check:planning`), `P/retros/ct15-plan-records.md`, `P/lanes/ct15-plan-records.log.md` | implementer / Opus high | `python3 -I -m unittest discover -s dev -p test_plan_records.py`; `check:planning` on fixtures; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 4 |

Pairwise disjointness: `ct02b` is the only writer under `dev/hooks/` and `dev/git_delivery.py`;
`ct11` the only writer of `dev/check.py` and `dev/retro_gate.py`; `ct05` the only writer of
`dev/lane.py`, `dev/ledger.py` and `.claude/rules/planning-records.md`; `ct15` the only writer of
`dev/plan_records.py`. Fixture directories, `mise/tasks/<unit>.toml`, retro and log files are named
per unit. The one shared line (`check:research` depends) is a parent hunk at integration. Split
rule: `ct05` reports a split point (`ct05-lane-record` for `lane:set|validate`) when it passes
300 handwritten lines; the second unit joins wave 2.

Integration order rationale: `ct02b` first removes the live PreToolUse false positive (R7 O) that
slows every later Bash call; `ct11` second so the remaining integrations run under the lock;
`ct05` third so `ledger:sync` and `lane:set` serve the rest of the wave; `ct15` last.

### Wave 2 (4 offline lanes; heavy slot = L1 #96 if D5, else #21)

Cut from the tip after the last wave-1 integration and its publish.

| Unit | Ticket | Branch | `owned_paths` | Agent / model | Required checks (lane) | Int. order |
|---|---|---|---|---|---|---|
| `ct12-lane-lifecycle` | CT-12 (R7 B, C, J) | `claude/ct12-lane-lifecycle` | `dev/lane.py` (`allocate`, `integrate`, `status`), `dev/test_lane.py`, `dev/fixtures/lanes/` (new cases), `mise/tasks/ct12.toml`, `P/retros/ct12-lane-lifecycle.md`, `P/lanes/ct12-lane-lifecycle.log.md` | implementer / Opus high | `python3 -I -m unittest discover -s dev -p test_lane.py`; scratch-repo `allocate`/`integrate --continue` cases; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 1 |
| `ct14-lane-brief` | CT-14 (R7 E, L) | `claude/ct14-lane-brief` | `dev/lane_brief.py`, `dev/test_lane_brief.py`, `dev/hooks/subagent_receipt.py`, `dev/test_subagent_receipt.py`, `.claude/agents/{implementer,doc-writer,reviewer,retro-writer}.md`, `mise/tasks/ct14.toml`, `P/retros/ct14-lane-brief.md`, `P/lanes/ct14-lane-brief.log.md` (settings hook entry proposed to the parent) | implementer / Opus high | the two unit commands; brief size test (<1.5 KB); `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 2 |
| `ct13-publish-batch` | CT-13 (R7 D) | `claude/ct13-publish-batch` | `dev/git_delivery.py` (`batch` subcommand), `dev/test_git_delivery.py`, `mise/tasks/ct13.toml`, `P/retros/ct13-publish-batch.md`, `P/lanes/ct13-publish-batch.log.md` | implementer / Opus high | `… -p test_git_delivery.py` (scratch remote); `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 3 |
| `c3-discussion-diagnostic` | #95 C3 (offline part) | `claude/c3-discussion-diagnostic` | `dev/research_refresh/diagnose_discussion_search.py`, `dev/research_refresh/test_diagnose_discussion_search.py`, `dev/fixtures/github-discussion-*.json`, `docs/research-feedback.md` (C3 section), `mise/tasks/c3.toml`, `P/retros/c3-discussion-diagnostic.md`, `P/lanes/c3-discussion-diagnostic.log.md` | implementer / Opus high | `python3 -B -m unittest discover -s dev/research_refresh -p 'test_*.py'`; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 4 |

Disjointness: `ct12` and `ct14` share only the schema import (`dev/lane.py` is `ct12`'s; `ct14`
writes `dev/lane_brief.py`); `ct13` is alone in `dev/git_delivery.py` now that `ct02b` landed;
`c3` is alone under `dev/research_refresh/` and `docs/research-feedback.md`; `ct14` is the only
writer of `.claude/agents/*.md` and the only new hook script. C3's live API run is a separately
admitted operation after the lane merges (evidence file named by unit).

### Wave 3 (4 offline lanes; heavy slot = next in the heavy order)

| Unit | Ticket | Branch | `owned_paths` | Agent / model | Required checks (lane) | Int. order |
|---|---|---|---|---|---|---|
| `ct07-codex-compat` | CT-07 | `claude/ct07-codex-compat` | `.codex/agents/*.toml`, `.codex/config.toml`, `dev/test_skill_mirror.py`, `docs/agents/claude-team.md` (Codex compatibility section), `mise/tasks/ct07.toml`, `P/retros/ct07-codex-compat.md`, `P/lanes/ct07-codex-compat.log.md` | implementer / Opus high | `python3 -I -m unittest discover -s dev -p test_skill_mirror.py`; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 1 |
| `ct16-unwired-tests` | CT-16 (R7 H) | `claude/ct16-unwired-tests` | `dev/check.py` (one rule), `dev/test_check_wiring.py`, `dev/fixtures/check/`, `mise/tasks/ct16.toml` (`test:retro-gate`), `P/retros/ct16-unwired-tests.md`, `P/lanes/ct16-unwired-tests.log.md` | implementer / Opus high | the unit command; `tasks validate`; `check` (must now pass on the composed tree); baseline; `git diff --check`; `retro:gate` | 2 |
| `ct06-lane-retro` | CT-06 (R7 K) | `claude/ct06-lane-retro` | `.claude/skills/lane-retro/**`, `.agents/skills/lane-retro/**`, `dev/test_lane_retro_skill.py`, `P/retros/ct06-lane-retro.md`, `P/lanes/ct06-lane-retro.log.md` | implementer / Opus high | the unit command; mirror identical (`diff -r`); `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 3 |
| `ct09-tool-evaluation` | CT-09 | `claude/ct09-tool-evaluation` | `docs/agents/tool-evaluation.md` (new; the `docs/AGENTS.md` pointer line is proposed to the parent), `P/retros/ct09-tool-evaluation.md`, `P/lanes/ct09-tool-evaluation.log.md` | doc-writer / Sonnet high | every cited path resolves; `tasks validate`; `check`; baseline; `git diff --check`; `retro:gate` | 4 |

Disjointness: `ct07` alone in `.codex/` and `claude-team.md`; `ct16` alone in `dev/check.py`;
`ct06` alone under both `lane-retro` subtrees (its mirror satisfies `ct07`'s test on the composed
tree, so `ct07` integrates first and `ct06` reruns the mirror test after its tip merge); `ct09`
writes one new doc. CT-10 (`dev/test_codex_session_history.py`, both skill subtrees), CT-17,
CT-08 (alone on `dev/check.py` and the frozen files; D6), C2 (#98; `dev/research_refresh/`
binding; admit), the `ct05` split unit, the A06 residual unit and the final `<spec>-review-fixes`
lane form wave 4+. Closures (#90, #92, #93, #97, #79–#82 via T4, #62–#77, #12, #24, #25, #94) are
parent-run qualified closes between waves, never lanes.

## Integration protocol

1. **One merger at a time**, on the root checkout, branch `codex/marketplace-native-onboarding`,
   `MERGE_HEAD` absent, `VIRTUAL_ENV` unset, no named check running anywhere (lock, else `pgrep`).
2. **Preflight**: record has `review` ∈ {PASS, PASS-with-P2/P3 closed}; `retro_gate.py --branch
   <branch>` rc 0; the implementer's handoff names a tip merge equal to the current tip (else
   send it back to merge again: "cut from the tip after the previous integration; merge tip
   before reporting").
3. **Merge**: `git merge --no-ff <branch>` with a message file, no `--no-commit` (D2 §3.7; hk
   `pre-merge-commit` fires only on a real merge commit once `hooks:install` is reconciled; until
   then the merger runs `retro:gate -- <unit>` by hand first). Changed paths ⊆ `owned_paths` ∪
   {record, retro, log}; anything else aborts (`git merge --abort` is hook-exempt).
4. **Parent hunks** in the same commit, declared in the message: `check:research` depends entry,
   settings hook entry, AGENTS/rules/GLOSSARY literal edits from the handoff. Gates on the
   composed tree, each rc recorded: `tasks validate`, `check`, `check:acceptance-baseline`,
   the record's named checks, `check:research` (serialized), `git diff --check`, `retro:gate --
   <unit>`.
5. **Records**: `lane:set <unit> status=integrated merged_head=<lane tip>` (derives `retro`),
   `ledger:sync`, `plan:log "<one line>"`; before CT-05/CT-15 land, the same three edits by hand in
   one docs commit, `status` and `retro` set together (Stop gate).
6. **Publish (A09)**: `delivery:prepare` then `delivery:publish` with `check_task=[deps:check,
   check:acceptance-baseline, test:delivery, test:hooks]`, selected path = the `progress.md` line.
   Batch size: wave 1 publishes after every integration (the session died once with one lane
   unpublished); from CT-13 on, `delivery:publish-batch` after every integration. The push gate
   attributes a merge by `Merge branch '<b>'` or by a ref pointing exactly at the second parent, so
   **lane branches and worktrees are deleted only after the publish that carries them** (then
   R5's cleanup block, lane `status` gains `worktree removed`).
7. **Recovery**: merger dies with `MERGE_HEAD` set → next session verifies `MERGE_HEAD` names the
   lane (`git_gate.merge_sources`), repeats steps 3–6 from the staged state (R5 Runbook 1 shape);
   after CT-12: `lane:integrate <unit> --continue`, or `--abort`. A lane record saying `integrated`
   without `retro: passed` blocks the parent's turn once; fix the record, do not bypass.
8. **Final implement-spec `code-review`** (model-invoked Skill, parent, foreground): once per spec
   after its last ticket merges, fixed point = `spec.manifest.json.start_sha` (`361688e` for the
   takeover spec: diff includes C1, rf-env-scrub and the skill lane, which the Spec axis lists as
   out of scope, not failures; the automation set uses the wave-0 published tip), spec source =
   the spec issue, `CODING_STANDARDS.md` mandatory. Findings go to one `<spec>-review-fixes` lane
   (record, cold review, retro, gate; stop after focused checks). It runs after wave 3 for the
   takeover spec if CT-08 and CT-10 have landed, otherwise after wave 4.

## Brief templates

Implementer (pointers only; `.claude/agents/implementer.md` holds the procedure):

```
LANE-UNIT: <unit>
Role: implementer (.claude/agents/implementer.md). Ticket: <issue URL or P/proposals/.../tickets.preview.json#<CT-id>>.
Record: P/lanes/<unit>.json (read first; it is parent-owned, do not edit).
Worktree: .claude/worktrees/<unit>  Branch: claude/<unit>-<slug>  base_sha: <allocation commit>
Env: PWF_PLAN_ROOT=<root> PLAN_ID=<plan id>; unset VIRTUAL_ENV; run ./dev/mise run tools:prepare && deps:sync once.
Allowlist: exactly record.owned_paths. Your ledger: P/lanes/<unit>.log.md (append-only). Never: task_plan.md, progress.md,
  findings.md, ticket-ledger.md, mise.dev.toml, .claude/settings.json, any AGENTS.md outside the allowlist.
Tasks: put new test:*/verb rows in mise/tasks/<unit>.toml; name the check:research entry you need in the handoff.
Seam: <the seam the ticket names>; tdd red first. Size: ~5 files / 300 lines, report a split point past that.
Checks (literal, record.required_checks): <cmd 1> ; <cmd 2> ; ./dev/mise tasks validate ; ./dev/mise run check ;
  ./dev/mise run check:acceptance-baseline ; git diff --check ; ./dev/mise run retro:gate -- <unit>
  Never run check:research here. Record for each: command, rc, selectors present, and whether another dev/check.py ran.
Retro draft: P/retros/<unit>.md per docs/agents/ticket-retro.md (seven categories).
Before reporting: git merge <integration tip SHA you observed last>, rerun affected checks, commit, git status clean.
Commit trailers (read from <scratchpad>/trailers.txt): Co-Authored-By / Claude-Session lines.
Handoff (<=300 words): branch, final SHA, tip merged, changed paths, each command + rc, unverified items, proposed
  edits outside the allowlist as literal diffs (AGENTS/rules/GLOSSARY/settings/check:research), retro path.
Do not: push, publish, merge into the integration branch, spawn agents, close tickets, edit other lanes' files.
```

Reviewer (pointers only; `.claude/agents/reviewer.md` holds the axes and dispositions):

```
LANE-UNIT: <unit>
Role: reviewer (.claude/agents/reviewer.md), read-only, cold. Ticket: <URL or preview pointer>.
Record: P/lanes/<unit>.json. Branch: claude/<unit>-<slug>. Fixed point: <base_sha>. Head: <lane tip SHA>.
Diff: git diff <base_sha>..<head> (read every changed file). Handoff receipt: <scratchpad path>.
Standards sources: CODING_STANDARDS.md, nearest AGENTS.md, .claude/rules/*.md, docs/agents/ticket-retro.md,
  docs/agents/codex-task-orchestration.md#ownership. Baseline: evidence/onboarding/baseline-files.json (19 untouched).
Spec source: the ticket's acceptance criteria (and P/proposals/claude-takeover-spec/spec.md for CT-*).
Check: changed paths subset of owned_paths + record/retro/log; tests assert an external seam; receipts bind exact rc;
  tip merge present; no named check claimed as a receipt while another ran.
Re-run yourself (read-only): <unit test command>; ./dev/mise run retro:gate -- <unit> in the worktree.
Report: ## Standards and ## Spec blocks, severity-ordered P1/P2/P3 with path:line, disposition
  (PASS | PASS-with-P2/P3 | FAIL), the checks you did not run. <=400 words per axis.
Do not: edit, write, merge, push, or spawn agents.
```

Retro-writer and merger briefs reuse the same header lines (LANE-UNIT, record, branch, SHAs,
receipt path) and point at `.claude/agents/retro-writer.md` or the Integration protocol above.
CT-14's `lane:brief` prints the header block from the record so the parent types only the judgement
lines.

## Tickets added by R2 (placeholder)

R2 runs in parallel and may add or renumber tickets (CT-02b, the `ct05` split, CT-12…CT-17 are
R7/R8 names until R2 settles them). Slotting rule: a new ticket joins the earliest wave in which its
blockers have merged **and** its `owned_paths` intersect no lane of that wave; a ticket that needs
`dev/check.py`, `dev/hooks/`, `dev/lane.py`, `docs/agents/claude-team.md`, `.claude/settings.json`
or any `AGENTS.md` waits for the wave whose owner of that path has integrated. Waves never exceed
four offline lanes; a fifth candidate moves to the next wave, lower R7 score first.

| R2 ticket | Blockers | Owned paths | Earliest wave | Conflicts with |
|---|---|---|---|---|
| _to be filled by the parent from R2's output_ | | | | |

## Risks and user decisions

- **D1 Runbook choice for `gate-hooks`.** Runbook 1 (finish the staged merge; declared parent
  hunks) or Runbook 2 (abort, re-cut, re-review). Recommendation: Runbook 1; it is faster and the
  records keep it traceable. Nothing below starts before it is published.
- **D2 `hooks:install` deferral.** R5 P1-2: installing hk config-based hooks makes A09 refuse.
  Recommendation: defer; `ct02b-gate-followup` reconciles (`--legacy` shims or admit
  `pre-merge-commit`), after which the parent runs `hooks:install` once. Until then layer 2 is
  absent and the merger runs `retro:gate` by hand (P2-2).
- **D3 to-tickets approval and publication** of CT-01…CT-11 plus the R7 set (CT-12…CT-17, renumbered
  by R2). Lanes can run on local IDs, but `implement-spec` resolves tickets "the tracker's way", so
  closure and the final `code-review`'s spec source need the issues. Also: who types
  `/mattpocock-skills:implement-spec` (user, fresh window) versus file-guided mode recorded in
  `skill-invocations.md`.
- **D4 Settings composition** (R5 B): project `$schema` + `hooks`; `permissions`, `enabledPlugins`
  and the rest to `settings.local.json`. Default accepted unless the user wants `enabledPlugins`
  shared.
- **D5 Heavy chain start.** The L-chain is five serial heavy runs; `task_plan.md:92` puts L1 after
  `#21 → #20 → #17 → #16`. Options: (a) keep that order, heavy slot in wave 2 = #21; (b) start L1
  in wave 1's heavy slot because L6 is the user's stated product goal. Each run needs its own
  confirmation either way; the offline waves are unaffected.
- **D6 CT-08 baseline transition v2.** `.gitignore`, `ci/acceptance.sh` and
  `.github/workflows/acceptance.yml` are frozen; the transition edits `.gitignore` and the baseline
  logic in `dev/check.py`. It can run in parallel with lanes that touch neither `dev/check.py` nor
  frozen files (not with CT-11 or CT-16), so wave 4 at the earliest. Decide whether the transition
  also changes the CI acceptance files (needs the fresh-session acceptance admission) or only
  `.gitignore` + `evidence/onboarding/baseline-files.v2.json` + `dev/check.py`.
- **D7 `mise/tasks/` include files** (wave 0.3). A new convention; if `task_config.includes` does
  not validate under `./dev/mise`, fall back to "lanes propose TOML rows, the parent appends
  them at integration" (every integration becomes a declared evil merge).
- **D8 Per-lane log file** `P/lanes/<unit>.log.md` and parent-only lane records amend
  `.claude/rules/planning-records.md` (CT-05 lane). Accept or keep "lane edits `status`" (then a
  lane's status commit and the parent's post-review edit can collide; keep the parent off the
  record until the merge commit).
- **D9 Worktree cleanup.** Eight integrated worktrees remain; delete after publish (push gate needs
  the refs) and after the `a06-unit3` record fix. Decide now or keep for audit.
- **Risks.** (1) `check:research` serialized means wave throughput is bounded by the merger, not
  the lanes; (2) `SubagentStop` blocks subagents whose `cwd` is a lane worktree with a failing
  record (keep records passing before dispatching reviewers into worktrees); (3) `PreToolUse`
  `onFailure: block` with a 10 s budget denies unrelated Bash calls while a slow gate runs
  (`ct02b` fixes it; until then expect spurious denials during merges); (4) `.venv` per worktree
  is created by `deps:sync` and ignored, but a lane that runs `check` without `deps:sync` sees
  `deps:check` refusals; (5) four Opus implementers plus reviewers and retro-writers in one wave
  are a token burst; the user may cap wave 1 at three.

## Could not verify

- `task_config.includes` behaviour under the `./dev/mise` wrapper (mise `2026.10.8` minimum;
  include paths relative to `mise.dev.toml`) and whether wildcard `depends` would remove the
  `check:research` parent hunk; both need a scratch run of `./dev/mise tasks validate` (not run:
  write task during a merge in progress).
- Unit sizes: CT-05 (ledger + lane:set/validate) and CT-12 likely exceed 300 lines; split points
  are named, line counts are estimates.
- Which of #16/#17/#20/#21 and L1 the user wants first; the heavy order is quoted from
  `task_plan.md:92`, not re-derived.
- The exact `owned_paths` of C3 and C2: inferred from the ticket bodies (no file paths in tickets by
  rule); the implementer confirms them at step 1.
- Whether `.codex/config.toml`'s `max_concurrent_threads_per_session = 3` interacts with any Claude
  lane (it should not; Codex is idle until 2026-10-19).
- R2's final ticket list; the placeholder table is empty by design.
- Whether `hk install --force-local` changes the `delivery:inspect-hooks` digest (R7 also could not).
