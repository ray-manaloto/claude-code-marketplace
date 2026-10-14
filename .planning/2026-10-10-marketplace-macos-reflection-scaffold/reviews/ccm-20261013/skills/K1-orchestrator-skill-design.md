# K1: `ticket-frontier` — orchestrator skill design

Written 2026-10-13 by K1 (read-only; `MERGE_HEAD e12cf04` untouched). `P/` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. Sources are cited inline; all quoted contents are data. Built next with skill-creator (`~/.claude/plugins/cache/claude-plugins-official/skill-creator/8d392c816966`: SKILL.md with `name` + pushy `description`, `scripts/`, `references/`, `evals/evals.json`).

## 1. Name and invocation

**Candidates:** `ticket-frontier` (recommended), `lane-frontier`, `frontier-orchestrator`. `Frontier` and `Lane` are glossary words (`GLOSSARY.md` §Workflow); the skill works the ticket frontier and allocates lanes, so `ticket-frontier` names the input, not the mechanism.

**Frontmatter** (`code.claude.com/docs/en/skills`: `description` + `when_to_use` capped at 1,536 chars; `context: fork` runs the body in a subagent that "doesn't see your conversation history"):

```yaml
name: ticket-frontier
description: Orchestrate the parallel ticket work of a spec: compute the ready frontier from the tracker graph and lane records, keep N lanes (default 3) running in disjoint worktrees with one C++ lane always active, dispatch implementer → reviewer → retro-writer → merger per lane under a per-model context ceiling, and record each applied retro learning in a ledger. Use whenever the parent is inside /implement-spec, asks "what is ready", "allocate the next lane", "re-kick the frontier", "which tickets can run in parallel", "integrate and schedule", or wants retro learnings applied automatically after a ticket.
user-invocable: true
```

No `context: fork`: the body dispatches `Agent` calls, asks the user before `delivery:publish` and qualified closes (`AGENTS.md:49-51`), and must satisfy the `Stop` gate; a forked body would lose the conversation and the publish admission. Model-invoked (default), so the user-typed `/mattpocock-skills:implement-spec` can call it through the Skill tool (D1 §1: "A user-invoked skill may invoke model-invoked skills"), one skill per call. It never calls a user-invoked skill; it tells the user to type `/mattpocock-skills:retro` at the end of the build window (D1 §6.1, §6.5).

**Dispatches** (repo definitions, never `general-purpose`, never `isolation: worktree`, which branches "from your default branch rather than the parent session's HEAD" — sub-agents docs; SYNTHESIS §6): `implementer`, `doc-writer`, `reviewer`, `retro-writer`, `extractor`, plus the new `frontier-scheduler` (§3). Model/effort per step come from §2's policy and are passed as the Agent tool's `model`/`effort` overrides, so the agent file's defaults are the floor, not the decision.

**Writes:** `P/frontier/state.json` (claims, active lanes, executor, ceilings, last plan hash); `P/frontier/plan-<utc>.json` receipts (ready set, scores, chosen lanes, rule ids); `P/frontier/learning-ledger.jsonl` (§6); `P/frontier/executor-gate.json` (§7). It reads `P/lanes/<unit>.json` (parent-owned) and `P/ledger-<unit>.jsonl` (lane-owned, SYNTHESIS D8); `P/progress.md` only through `plan:log` (CT-15). Everything else goes through `lane:allocate|integrate|status` (CT-17), `lane:brief` (CT-19), `ledger:sync` (CT-05), `delivery:publish-batch` (CT-18) and `doctor` (CT-22).

## 2. Inputs and configuration

File: `P/frontier.toml` (TOML, parent-owned, read by `scripts/frontier.py` with `tomllib`).

```toml
schema = 1
max_parallel = 3                    # implementer/doc-writer lanes at once; reviewers, retro-writers, extractor and scheduler are not counted
always_active = ["cxx"]             # one slot of max_parallel is reserved for this class while any member is ready
context_ceiling_fraction = 0.5      # per-model window × fraction = the lane ceiling
executor = "native"                 # native | claude-agent | codex-agent; a non-native value is refused unless executor-gate.json passes (§7)
retro_apply = "auto"                # auto | propose; §6 lists what stays propose regardless
publish_batch = "per-integration"   # per-integration | per-wave
check_lock = true                   # refuse to dispatch a merger while CT-11's lock is held

[classes.cxx]                       # tickets of the native C++26 P2996 core (docs/accepted-decisions.md)
spec = "#11"
include = ["#13", "#14", "#15", "#16", "#17", "#18", "#19", "#20", "#21", "#22", "#23", "#30-#61"]
heavy = true                        # every member needs a per-run admission (claude-team.md §Concurrency)
first = "#21"                       # heavy order from task_plan.md:92: #21 → #20 → #17 → #16 → L1

[windows]                           # tokens; platform.claude.com/docs/en/about-claude/models/overview (fetched 2026-10-13): all four list a 1M context window, 128K max output
fable = 1000000
opus = 1000000
sonnet = 1000000
haiku = 1000000

[model_policy]                      # step kind → model/effort; see the Fable rule below
implement = { model = "opus", effort = "high" }
docs = { model = "sonnet", effort = "high" }
review = { model = "fable", effort = "high" }
retro = { model = "fable", effort = "high" }
synthesis = { model = "fable", effort = "high" }
design = { model = "fable", effort = "high" }
schedule = { model = "opus", effort = "high" }
extraction = { model = "haiku", effort = "low" }
escalate_after_partial = 1          # Opus attempts on one unit before the next attempt is Fable
```

**Ceilings:** with every current model at 1M, 0.5 gives 500,000 tokens for each lane, equal to C4's `fork_deny` (500 K) and below `warn` 400 K < `checkpoint` 550 K < `hard` 650 K < `autoCompactWindow` 700 K (SYNTHESIS §2b class A). `frontier.py plan` refuses when `fraction × window` differs from `dev/doctor/budget.py`'s `fork_deny`, so there is one threshold source (Q2).

**The "Fable only when Opus cannot" rule, checkable:** a step runs on Fable iff (a) its kind is `review`, `retro`, `synthesis` or `design`, or (b) the unit's receipt journal (`<common>/claude-lanes/<unit>.jsonl`, CT-19) holds ≥ `escalate_after_partial` lines with `agent_type: implementer`, `model: opus` and `task_status ∈ {partial, blocked}` whose reason is tagged `reasoning` (not `admission`, `conflict` or `ceiling`), or (c) the ticket carries the `design` class. Every plan receipt records `{"step","model","effort","rule":"policy.kind|escalation|class"}`; the doctor detector `F.model-policy-violation` (CT-22 `agents.py`) compares journal `model` fields against the receipt. Fable costs $10/$50 per MTok against Opus's $4/$20 (models overview), so the rule is also the cost control.

## 3. Scheduler

**Ready set** (`frontier.py plan`, stdlib, offline): read `P/ticket-ledger.json` (CT-05 snapshot of the tracker graph with `blockedBy`/`parent`), `P/lanes/*.json` and `P/frontier/state.json`. A ticket is *done* when its lane record says `integrated` or `published` with `retro: passed`, or the tracker says closed with an accepted disposition; GitHub `blockedBy` drops only on close, so the frontier is computed from what merged (`D/implement-spec:60`; R8 "Dependency graph"). A ticket is *ready* when every blocker is done, it is not claimed, and it is not held by a retro barrier (`ticket-retro.md` §5).

**Priority** (ties broken in order): (1) critical-path length = longest blocker chain from the ticket to a sink in the remaining graph; (2) out-degree = number of open tickets it unblocks; (3) membership in an `always_active` class; (4) wave number from C4's reconciled table (`P/frontier.toml [waves]` optional override); (5) ticket number. **Conflict rule:** a candidate joins the active set only if its proposed `owned_paths` intersect no active lane's `owned_paths ∪ excluded_shared_paths` and it touches at most one of R8's hot paths (`dev/check.py`, `dev/hooks/`, `dev/lane.py`, `docs/agents/claude-team.md`, `.claude/settings.json`, any `AGENTS.md`), each of which has one owner per wave. **Capacity:** `len(active) < max_parallel`; the `cxx` slot is filled first whenever a `cxx` member is ready; a heavy member needs an admission line in `P/decisions.jsonl` (CT-24) for this run, else the slot takes the ticket's offline portion (source, CMake and fixture preparation the implementer splits out and reports as a unit per `implementer.md` step 3) and the plan receipt records `cxx_slot: "offline-portion of #21; heavy run not admitted"`. The heavy chain stays serialized at one run at a time with a fresh confirmation each time (`claude-team.md` §Concurrency, D5).

**`frontier-scheduler` agent** (`.claude/agents/frontier-scheduler.md`): `model: opus`, `effort: high`, `permissionMode: plan`, `disallowedTools: [Edit, Write, NotebookEdit, Agent]`, `maxTurns: 40`. Input: the plan receipt from `frontier.py plan` (mechanical part done) and the ready tickets' bodies. Its judgement, which the script cannot do because tickets carry no paths (D1 §6.9): propose `owned_paths` and `excluded_shared_paths` per ready ticket from the body and the tree, name the seam, estimate files/LOC, flag conflicts the path rule missed, and decide single lane vs several (below). Output: JSON `{unit, ticket, owner_role, owned_paths, excluded, seam, est_files, est_loc, split, conflicts}` per candidate; the parent writes nothing until `frontier.py claim` validates it against the conflict rule. Runs: at skill start; after every `frontier.py release`; after every failure receipt (journal line with `task_status ∈ {partial, blocked, failed}`); whenever the `cxx` slot empties. Fable only under §2(b).

**Single agent vs team:** under `executor = native` the scheduler decides, and "team" means several lanes with disjoint allowlists under one ticket, one writer per worktree (`codex-task-orchestration.md#ownership`), integrated serially. Criteria: `est_files > 5` or `est_loc > 300` → split into sub-units (the unit-size rule); ≥ 2 independently testable seams → parallel sub-lanes; a documentation half → a `doc-writer` sub-lane; high review risk (a hot path or a frozen baseline file) → one lane, Fable reviewer, no parallel sibling. Under `executor = claude-agent` the executor's own selection (dynamic-agents ticket 06 "Choose topology, model and effort"; design Q1) decides topology within the caller constraints the skill passes (max files, ownership, model policy, `allow_subagents`); the skill still enforces path disjointness before dispatch.

## 4. Context budget

Each lane's ceiling = `windows[model] × context_ceiling_fraction` (500 K today for every role). Enforcement, four layers:

1. **Brief line** (`lane:brief` slot, CT-19): `CTX-CEILING: 500000 (model opus). Checkpoint to P/ledger-<unit>.jsonl at 400000; at the ceiling commit, write the handoff and stop; do not fork.` Subagent context is "sized by its own model, not the parent's" and each starts fresh (sub-agents docs), so the number is per lane.
2. **PreToolUse `Agent` gate** (`dev/hooks/agent_gate.py`, C2 §A, wave 0): reads `transcript_path` backwards (`dev/context_budget.py`: `ctx = input + cache_creation + cache_read` of the last assistant line) and denies `subagent_type: fork` at `ctx ≥ fork_deny`, since a fork inherits the dispatcher's context; a lane dispatch is allowed with `additionalContext: "ctx <n>"`.
3. **SubagentStop receipt** (`dev/hooks/subagent_receipt.py`, CT-19) records first and last `usage` sums of `agent_transcript_path`. `frontier.py release <unit> --from-journal` refuses `--resume` when the last sum ≥ ceiling and marks the lane `split-required`; the scheduler carves a continuation unit from the lane's commits and ledger for a fresh agent with a new `lane:brief` (state travels through the branch and `P/ledger-<unit>.jsonl`, never the transcript).
4. **Parent budget:** `prompt_hook.py` prints `ctx n/window` every turn; at `warn` the skill's loop runs `plan:log` and delegates the next integration to a fresh merger agent rather than doing it inline; at the same fraction (0.5 = `fork_deny`) it stops dispatching new work, runs `plan:handoff --write`, and tells the user to `/clear` once `plan:handoff --check` passes (D1 §6.6 ordering: Continue → /clear → /handoff → subagent → /compact). `.claude/settings.json` sets `autoCompactEnabled: true`, `autoCompactWindow: 700000` (D21).

## 5. Integration loop

Per lane, each stage ends on a receipt and a state word (`claude-team.md` §Lane lifecycle):

1. `frontier.py next` → scheduler JSON → `frontier.py claim <unit>` → `lane:allocate` (record committed first, `base_sha` = allocation commit, worktree on `claude/<unit>-<slug>`, `tools:prepare`/`deps:sync`).
2. `implementer` (or `doc-writer`) in the background with `lane:brief --role implementer` + the judgement lines (seam, ceiling, model); it calls the Skill tool for `tdd` red-first, keeps the unit near 5 files / 300 lines, merges the integration tip, commits, drafts the retro, appends to its ledger. SubagentStop writes the journal line.
3. `reviewer` (Fable, cold, fixed point `base_sha`, `CODING_STANDARDS.md` input) → disposition into the journal; `lane:set --from-journal`. FAIL → one more implementer round on the same lane; PASS-with-P2 → the fix lands before step 4.
4. `retro-writer` (Fable) applies every actionable finding (§6), reruns `check` and `retro:gate -- <unit>` until both exit 0; cross-scope edits come back as literal hunks.
5. Merger = the parent, or a fresh `implementer`-typed merger agent when the parent is above `warn`: `doctor --surface integrate --unit <unit>`, then `lane:integrate <unit>` (`--no-ff`, never `--no-commit`; paths ⊆ allowlist; composed-tree gates; `ledger:sync`; `plan:log`), one merger at a time under the CT-11 lock; `check:research` only here.
6. Publish: `delivery:publish-batch` after every integration (`publish_batch = per-integration`; `per-wave` batches to the wave end) with the user's standing A09 admission; the parent asks before a qualified close.
7. `frontier.py release <unit>` → scheduler re-run → back to 1 while the ready set is non-empty.

Spec end: when the last ticket of a spec has merged, the parent calls the Skill tool for `code-review` with fixed point `spec.manifest.json.start_sha` and the spec issue as source (D2 §2.8; D10); findings go to one `<spec>-review-fixes` lane through steps 1–6, then focused checks and stop. Worktrees and lane branches are removed only after the publish that carries them and the qualified close (R8 protocol 6; D9); `lane:set` records `worktree removed`.

## 6. Retro automation

The automated step after every ticket is step 4 above plus three additions:

- **Learning ledger** `P/frontier/learning-ledger.jsonl`, one line per applied, rejected or deferred finding: `{ts, ticket, unit, category, finding_id, kind: mechanical|judgement|navigation|workflow|role, destination: <path>, mode: auto|propose, verification: {cmd, rc}, retro_row, applied_by: retro-writer|parent|user}`. `retro:gate` already checks the record's shape; the ledger makes the destination and the trigger queryable (`frontier.py ledger --by destination|ticket`), which is what "self-learning" needs to notice the same lesson landing twice (a repeat becomes a failing check per `D/retro:63-66`).
- **Doctor re-run**: after the retro-writer returns, `doctor --surface integrate --unit <unit> --json` (CT-22) runs before the merger; a P1/P2 sends the lane back to step 4, not to the parent's judgement.
- **Destination routing** (`CODING_STANDARDS.md` rule 12): mechanical → `dev/check.py` rule or `dev/test_*.py` + a wired `test:*` row; judgement → `CODING_STANDARDS.md`; navigation → nearest `AGENTS.md` or a `paths:`-scoped `.claude/rules/*.md`; repeated workflow → a skill under `.claude/skills/` with its `.agents/skills/` mirror; role → `.claude/agents/*.md`; hook → `dev/hooks/` + a settings hunk.

**`auto` (applied by the retro-writer inside the lane, verified by `check` and `retro:gate`):** anything inside the lane's `owned_paths`; new tests and their task rows; the nearest directory `AGENTS.md` pointer line; a `.claude/rules/*.md` scoped to the lane's paths; `references/` files of a skill the lane owns; the ledger line itself.

**`propose` regardless of `retro_apply` (literal hunk in the handoff, applied by the parent after the user says so):** root `AGENTS.md`/`CLAUDE.md` and `.claude/AGENTS.md`; `.claude/settings.json` hooks and `hk.pkl`; `.claude/agents/*.md` frontmatter (`model`, `effort`, `permissionMode`, `tools`); `CODING_STANDARDS.md` rule additions or deletions; `dev/check.py` rules that widen a refusal set; `P/frontier.toml`; the 19 frozen baseline files; any `docs/accepted-decisions.md` supersession. Session-level `/mattpocock-skills:retro` stays user-typed per build window (D16); its picks enter as one gated `retro-writer` lane and the same ledger.

## 7. Executor gate G and the adapter interface

`executor = claude-agent` (or `codex-agent`) is accepted only when `frontier.py executor-gate --write` finds every item below with rc 0 in `P/frontier/executor-gate.json`; otherwise the skill runs `native` and says which item failed.

| # | Condition ("takeover work complete") | Check |
|---|---|---|
| G1 | CT-17 (`lane:allocate/integrate`), CT-19 (`lane:brief`, receipt journal), CT-22 (doctor), CT-07 (Codex compatibility) are `published` with `retro: passed` | `lane:validate` over the four records |
| G2 | `~/.codex/skills/{codex-agent,claude-agent,.shared/agent-protocol}` are under version control with a recorded HEAD (brief 01a13185 §7 item 5: "no VCS") | `git -C … rev-parse HEAD` |
| G3 | Protocol tests, schema and codegen drift checks pass: `mise -C ~/.codex/skills/.shared/agent-protocol run test`, `schemas:check`, `codegen:check` (127 tests at last report) | three rc 0 |
| G4 | Dynamic-agents tickets 01–07 (constrained run, dual-channel verification, capability discovery for both harnesses, immutable definitions, topology/model/effort selection, capacity reservation) integrated on `spec/dynamic-agents` and promoted (ticket 33) into the installed skills; today 01, 26, 27a–28a are integrated, 02/03 in progress, 04–07 `ready-for-agent` | ticket `Status: complete` lines plus `diff -r` installed vs `implementation/repo@HEAD` |
| G5 | A tested command (tickets 04 + 12) emits a capability snapshot for this checkout and Claude Code version: effective settings layers, `env`, feature flags, agents on disk. Today only the static 9,542-record inventory JSON exists under `configuration-report/` | rc 0 and its test in `run test` |
| G6 | Smoke: `dispatch:claude` with `mode: review`, `claude.mode: safe`, `workdir` = this checkout returns `status: completed`, `execution.exit_code: 0`, `result_schema.validation: passed` | envelope fields |
| G7 | Only for `allow_subagents: true`: one `agent-qualify` sidecar whose `participation` verdict is `native_qualified`; until then the executor runs single-agent lanes only (`claude -p` never spawns Agent Teams; design note) | sidecar field |

**Adapter interface** (`scripts/executors/<name>.py`, one module per executor, selected by config only):

```
dispatch(brief_path, role, model, effort, ceiling, workdir, allow_team: bool) -> Receipt
status(run_id) -> {state, usage_total, task_status}
cancel(run_id) -> rc
Receipt = {run_id, provider, task_status, exit_code, usage: {input, output, total}, artifacts: {transcript|native_stdout}, session_id}
```

`native`: `dispatch` prints the Agent tool parameters (`subagent_type`, `model`, `effort`, `prompt` = `lane:brief` output + judgement, `run_in_background: true`) for the parent to issue; the receipt is the CT-19 journal line. `claude-agent`: writes a `contract_version: "2.0"` request (`task_file` = brief, `workdir` = worktree, `mode: implement|review`, `model`, `effort`, `timeout_s`, `allow_subagents`, `claude.agents_file` = `.claude/agents` as JSON, `claude.tools`), runs `mise -C ~/.codex/skills/.shared/agent-protocol run dispatch:claude -- <request.json>`, and maps the envelope (`usage.total_tokens`, `task_status`, `native.claude`) onto `Receipt`; the ceiling check reads `usage.input_tokens` of the terminal object. `codex-agent`: same with `dispatch:codex` and `codex.sandbox: workspace-write`. Each adapter has one fixture test on a saved envelope.

## 8. Files to create and the ticket

| File | Purpose |
|---|---|
| `.claude/skills/ticket-frontier/SKILL.md` | ≤ 150 lines: frontmatter (§1), the loop (§5) as numbered steps with completion criteria, pointers to references; `!`python3 -I <skill>/scripts/frontier.py status`` injected at the top (`|| true`, since a failed injection aborts the skill) |
| `references/scheduler.md`, `context-budget.md`, `executors.md`, `retro-automation.md`, `brief-slots.md` | §3, §4, §7, §6 and the judgement-line templates (R8 "Brief templates") |
| `scripts/frontier.py` | stdlib, `python3 -I`: `plan`, `next`, `claim <unit>`, `release <unit> [--from-journal] [--resume]`, `status`, `executor-gate [--write]`, `ledger`; reads `ticket-ledger.json`, lane records, `frontier.toml`, `budget.py` thresholds; writes only under `P/frontier/`; exit 0/2/1 |
| `scripts/executors/{native,claude_agent,codex_agent}.py` | §7 adapters |
| `evals/evals.json` | 3 prompts: "inside implement-spec, give me the next three lanes for spec #<n> with one C++ lane", "lane ct05 died at 540K tokens, what now", "switch executor to claude-agent" (expected: refused with the failing G item) |
| `.agents/skills/ticket-frontier/**` | byte-identical mirror (`.claude/AGENTS.md`; CT-07 mirror test) |
| `.claude/agents/frontier-scheduler.md` | §3 definition |
| `P/frontier.toml`, `P/frontier/` (seeded `state.json`, empty ledger) | §2 |
| `mise/tasks/ct25.toml` | `frontier:plan|next|status|claim|release|gate`, `test:frontier` (parent hunk adds it to `check:research` depends) |
| `dev/test_frontier.py`, `dev/fixtures/frontier/` | seam tests: ready set and priority on a 12-ticket graph; cxx slot with and without an admission; conflict refusal; ceiling refusal from a journal fixture; executor-gate refusal; ledger append |
| `docs/agents/claude-team.md` §Frontier (parent hunk) | one paragraph pointing at the skill |

**Ticket CT-25 "ticket-frontier orchestrator skill"** — next free after CT-24 (SYNTHESIS §6). Blocked by CT-05 (`ticket-ledger.json`, `lane:validate`), CT-15 (`plan:log`), CT-17 (`lane:allocate/integrate`), CT-19 (`lane:brief`, receipt journal), CT-22 (doctor, `budget.py`), CT-24 (`decisions.jsonl` admissions); wave 3 at the earliest (after CT-17/CT-19 integrate in wave 2). `owned_paths`: the two skill subtrees, `.claude/agents/frontier-scheduler.md`, `P/frontier.toml`, `P/frontier/`, `dev/test_frontier.py`, `dev/fixtures/frontier/`, `mise/tasks/ct25.toml`. Acceptance: (1) `test:frontier` rc 0 and wired; (2) on the fixture graph `frontier.py plan` returns the documented order and reserves the cxx slot; (3) `release --resume` on a journal with last usage ≥ ceiling exits 2 naming `split-required`; (4) `executor-gate` exits 2 on today's tree naming G2–G5; (5) `diff -r` of the two skill subtrees is empty; (6) one real dry run inside a user-typed `/implement-spec` window allocates ≥ 2 lanes with disjoint allowlists and a plan receipt, recorded in `skill-invocations.md` as a native Skill-tool call; (7) `retro:gate -- ct25-ticket-frontier` rc 0.

## 9. Open questions for the user

**Blocking the build**

1. **What is "the C++ ticket class"?** Context: tickets carry no paths or labels for it. Options: (a) the explicit `include` list in §2 under spec #11; (b) a tracker label `area:cxx` applied through `issue:apply`; (c) title prefix. ➡️ (a) now, (b) when the next `to-tickets` run can set labels.
2. **What fills the cxx slot when no heavy run is admitted?** Context: every ready C++ ticket (#21, #20, #17, #16) is host-heavy and serialized with a per-run confirmation. Options: (a) the ticket's offline portion as a split unit; (b) leave the slot empty and ask each cycle; (c) drop the always-active rule for heavy classes. ➡️ (a), with the admission asked once per scheduler run.
3. **Single threshold source.** Context: C4 puts `warn/checkpoint/fork_deny/hard` in `dev/doctor/budget.py`. Options: (a) `frontier.toml` holds the fraction and `plan` refuses on mismatch with `budget.py`; (b) `budget.py` reads `frontier.toml`. ➡️ (a).
4. **What `max_parallel` counts.** Options: (a) writer lanes only (reviewers, retro-writers, scheduler, extractor uncounted); (b) every live agent. ➡️ (a) with a hard cap of 8 live agents (docs: 20 concurrent subagents per session).
5. **`auto` vs `propose` boundary.** Context: §6 lists what stays `propose`. Options: accept the list; move `CODING_STANDARDS.md` additions to `auto`; move `.claude/rules` to `propose`. ➡️ accept the list.
6. **Ticket slot and blockers.** Context: a fully wired skill needs CT-17/19/22; a v0 could run on hand-written lane records in wave 2. Options: (a) CT-25 in wave 3 after its blockers; (b) a wave-2 v0 with `plan|next|status` only and by-hand allocation. ➡️ (a); the parent follows §5 manually until then.
7. **Executor gate list G1–G7.** Context: the Codex thread's work is local, unversioned and partly in progress. Options: accept G1–G7; drop G5 (no generator required); require G7 for any executor switch. ➡️ accept G1–G7, G7 only for team mode.

**Can default now, revisit later**

8. **Name.** ➡️ `ticket-frontier`.
9. **Fable escalation.** ➡️ after one Opus attempt ends partial/blocked with a `reasoning` reason; never for `admission`/`conflict`/`ceiling` reasons.
10. **Scheduler model.** ➡️ Opus high; Fable only under the escalation rule.
11. **Publish batch.** ➡️ per integration (the session died once with a lane unpublished, R8).
12. **Confirmation surface.** ➡️ plain text questions until CT-13 (AskUserQuestion mod) lands; then the mod.
13. **Learning ledger format.** ➡️ JSONL under `P/frontier/`, rows cite `retros/<unit>.md` row ids; no second copy in the retro.
14. **`allow_subagents` under `claude-agent`.** ➡️ `false` until G7.
15. **User-invocable `/ticket-frontier`.** ➡️ yes, for status and re-planning outside `/implement-spec`.

## 10. Could not verify

- Whether a subagent's own hooks receive `transcript_path` = its `agent-{id}.jsonl` (mid-run ceiling enforcement inside a lane); the design relies on SubagentStop and the brief line.
- The Agent tool's `effort` override reaching a project agent whose frontmatter sets `effort`.
- The skills and sub-agents pages were read to 100,000 of ~108,000 characters; skill-to-Skill-tool nesting is taken from D1 §1, not the page.
- Claude Code's effective window in this session (the models page lists 1M; hook payloads carry no `context_window_size`, C2 §A).
- `task_config.includes` under `./dev/mise` (D7).
- Dynamic-agents tickets 04–07 and 33 beyond their `Status` lines; the protocol test suite was not run (environment setup during a merge in progress); G5's absence is inferred from the directory listing.
- Token cost per cycle of three Opus writers plus Fable reviewers and retro-writers (R8 risk 5).
