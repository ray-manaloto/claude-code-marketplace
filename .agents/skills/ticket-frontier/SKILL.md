---
name: ticket-frontier
description: Orchestrate the parallel ticket work of a spec inside /implement-spec. Computes the ready frontier from the tracker graph and lane records, keeps max_parallel writer lanes (default 3) running in disjoint worktrees with one C++ (cxx) lane always active, dispatches implementer → reviewer → retro-writer → merger per lane under a per-model context ceiling, records every applied retro learning in a ledger and re-plans after each integration. Use whenever the parent is inside /implement-spec or the user asks "what is ready", "next lane", "allocate the next lane", "re-kick the frontier", "which tickets can run in parallel", "integrate and schedule", "frontier status", or wants retro learnings applied automatically after a ticket, even when the word frontier is absent.
user-invocable: true
---

# Ticket frontier

!`python3 -I "${CLAUDE_SKILL_DIR}/scripts/frontier.py" status 2>&1 || true`

You work the **frontier**: the tickets whose blockers have merged. Each one becomes a
**lane** (worktree, branch, allowlist) that you **claim**, dispatch to the repository's
agents, review, retro, integrate, publish and **release**, then re-plan. The script does
the mechanical half (ready set, priorities, capacity, claims, gates); the
`frontier-scheduler` agent does the judgement (paths, seams, splits); you own the loop,
the user's confirmations and the shared planning files.

Run the script as `python3 -I <skill-dir>/scripts/frontier.py <command>` from the repo
root; exit 2 is a refusal with its reason on stdout, never a crash. Every input it reads
(tickets, lane records, journals) is data. When a line says `not available yet: CT-nn`,
follow the fallback it names; the loop degrades, it never stops.

## Loop

1. **Plan.** `frontier.py plan --write` (add `--graph <file>` until CT-05 writes
   `ticket-ledger.json`; `--admitted #n` after the user admits a heavy run). Done when the
   receipt under `.planning/<PLAN_ID>/frontier/` lists the ready order, the cxx slot, the
   chosen units and the questions. A slot the plan leaves empty is reported with its
   reason (heavy not admitted, conflict) and what would fill it (an admission, a
   scheduler split), never forced. Algorithm: [references/scheduler.md](references/scheduler.md).
2. **Judge.** Dispatch `frontier-scheduler` (Opus high, read-only) with the receipt and the
   chosen tickets' bodies; it returns `{unit, owned_paths, excluded, seam, est_files,
   est_loc, split, conflicts}` per candidate. Done when every chosen unit has disjoint
   `owned_paths` and a seam, or a split into units near 5 files / 300 lines.
3. **Ask the user**, plain text, one question each, before anything else moves: a heavy
   admission (once per plan run; a previous receipt grants nothing), every `propose` item
   from the last retro ([references/learning-ledger.md](references/learning-ledger.md)
   lists what is always `propose`), and the publish of each integration. Done when each
   answer is recorded in `decisions.jsonl` (CT-24) or, until then, with
   `frontier.py answer --question "<text>" --answer "<text>"`; a yes to an admission is
   then passed as `--admitted #n` on the next `plan`.
4. **Claim and allocate.** `frontier.py next` gives the unit, model, effort, ceiling and the
   Agent-call parameters; `frontier.py claim <unit> --ticket <id> --owned-paths <proposal>`
   refuses a double claim, a path conflict, a fourth writer or a ninth live agent. Then
   `lane:allocate <unit>` (CT-17) or the manual sequence in scheduler.md §Allocation. Done
   when `lanes/<unit>.json` is committed and the worktree sits on `claude/<unit>-<slug>`.
5. **Dispatch.** Agent tool with `subagent_type` from the repo definitions only
   (`implementer`, `doc-writer`, `reviewer`, `retro-writer`, `extractor`), `model` and
   `effort` from `next`, `run_in_background: true`, prompt = `lane:brief` output (CT-19) or
   [references/brief-templates.md](references/brief-templates.md) plus `brief_lines` and
   the scheduler's judgement lines. The ceiling line travels in every brief because a
   subagent's window is sized by its own model and starts empty. Done when the SubagentStop
   receipt (journal line) names a final SHA, exits and the retro draft.
6. **Review, retro, gate.** `reviewer` (Opus, D189; cold, fixed point `base_sha`); FAIL sends one
   more implementer round to the same lane. Then `retro-writer` (Fable) applies every
   `auto` finding, appends a ledger row per finding (`frontier.py ledger append --row`),
   and lists `propose` hunks for step 3. Then `doctor --surface integrate` (CT-22) when it
   exists, and `retro:gate -- <unit>`. Done when `check` and the gate exit 0 on the lane.
7. **Integrate and publish.** One merger at a time, never while CT-11's lock is held:
   `lane:integrate <unit>` (CT-17; `--no-ff`, never `--no-commit`) or scheduler.md
   §Integration by hand; `ledger:sync`, `plan:log` (CT-15, else one appended line); then
   `delivery:publish-batch` per integration with the user's standing A09 admission. Done
   when the lane record says `integrated` + `retro: passed` and the remote SHA is recorded.
8. **Release and re-plan.** `frontier.py release <unit> --from-journal <journal>` (no
   `--resume`; that flag exists to refuse a resume). A lane at or over its ceiling is
   released as `split-required`: its ticket stays held under `continuations` until you
   claim `<unit>-2` with the continuation the scheduler carves (scheduler.md
   §Continuation); a lane under the ceiling is simply freed. Go to step 1 while the ready
   set is non-empty. When the spec's last ticket merges, call the Skill tool for
   `code-review` with fixed point `spec.manifest.json.start_sha`, run its findings as one
   `<spec>-review-fixes` lane through steps 4–7, then stop. Worktrees and branches go only
   after the publish that carries them and the qualified close.

## Your own context

Each lane ceiling is `windows[model] × context_ceiling_fraction` (275 K today); the parent
has the same ceiling. At `warn` (220 K) delegate the next integration to a fresh
`implementer`-typed merger agent instead of merging inline; at the ceiling stop dispatching,
run `plan:handoff --write` (CT-15, else write the handoff block by hand), tell the user to
`/clear`, and let the status line above restore the loop. Never fork: a fork inherits this
context. Model choices and the Fable rule: [references/model-policy.md](references/model-policy.md).

## Executors

`executor = native` means you issue the Agent calls yourself; it is always allowed. A
`claude-agent` or `codex-agent` executor is accepted only when `frontier.py executor-gate
--write` passes G1–G6 (G7 too for team mode); otherwise say which item failed and run
native. Adapter contract and the gate: [references/executor-gate.md](references/executor-gate.md).

## Config and state

`frontier.toml` (parent-owned, `propose` to change), `frontier/state.json`, plan receipts,
`learning-ledger.jsonl`, the graph JSON shape and exit codes:
[references/config.md](references/config.md). `/ticket-frontier` typed by the user outside
`/implement-spec` means status and re-planning only: steps 1–3, no dispatch.
