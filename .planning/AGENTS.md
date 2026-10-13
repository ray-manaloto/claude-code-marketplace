# .planning/

Plans live in `.planning/<PLAN_ID>/`; the current PLAN_ID is in the root `AGENTS.md`.
Path-scoped rules load from `.claude/rules/planning-records.md`.

- Inside it: `task_plan.md` (phases, lane table), `findings.md`, `progress.md`
  (append-only): parent-owned shared files; a lane proposes edits in its handoff.
- `completion-contract.md`: source of the standing workflow and the preservation list.
- `lanes/<unit>.json`: allocation record with path allowlist, base SHA, reviewer and
  status; a lane changes its own `status` only.
- `retros/<unit>.md`: the unit's retro; shape and gate in `docs/agents/ticket-retro.md`.
- `ticket-ledger.md`: issue, state, frontier, blockers and lane per ticket, regenerated
  from the tracker.
- `PWF_PLAN_ROOT` is the project root; a competing plan stays out of the tree.
