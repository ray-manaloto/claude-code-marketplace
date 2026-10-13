---
paths: [".planning/**"]
---

# Planning records

- Lane record `lanes/<unit>.json` holds: `unit`, `tickets`, `title`, `owner`, `writer_model`, `reviewer`, `worktree`, `branch`, `base_sha`, `import_source`, `owned_paths`, `excluded_shared_paths`, `required_checks`, `resource_admissions`, `status`, `created_at`. The parent writes it at allocation; a lane changes only its own `status`.
- Retro record `retros/<unit>.md`: `docs/agents/ticket-retro.md` is the single source for its shape. The gate (`./dev/mise run retro:gate -- <unit>`) checks three things: each of the seven categories is addressed (a finding row or an explicit `none ... because`); at least one verification binding is present (exit code, PASS, SHA-256 or named check); no finding is open without an owner, blocker or deferral.
- `progress.md` is append-only: add dated entries below the last one and leave earlier lines as written.
- `ticket-ledger.md` columns for issue, title, spec, GitHub state, frontier and blockers are regenerated from the tracker (`gh api graphql` with `blockedBy` and `parent`); the lane and local-state columns are the parent's edits at each lane transition.
- `task_plan.md` and `progress.md` are parent-owned shared files; a lane proposes edits in its handoff.
