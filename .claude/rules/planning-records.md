---
paths: [".planning/**"]
---

# Planning records

- Lane record `lanes/<unit>.json` holds: `unit`, `tickets`, `title`, `owner`, `writer_model`, `reviewer`, `worktree`, `branch`, `base_sha`, `import_source`, `owned_paths`, `excluded_shared_paths`, `required_checks`, `resource_admissions`, `status`, `created_at`. The parent writes it at allocation; a lane changes only its own `status`.
- Retro record `retros/<unit>.md` opens with one paragraph naming the unit, the commits and the command exits it binds. A table follows, ordered by severity (P1, P2, P3), one row per finding: severity, category and finding, source receipt, change, owner, disposition, verification.
- Disposition is `applied`, `rejected` with an evidence-backed reason, or `deferred` with an external blocker and its admission condition. Verification names a command and its actual exit code, or a SHA-256.
- Seven categories get a row or a line `<category>: none - <because>`: navigation, automated checks, coding standards, steering/global guidance, tool economy, no-ops, information access.
- `./dev/mise run retro:gate -- <unit>` passes before integration; see `docs/agents/ticket-retro.md` for the barrier rules.
- `progress.md` is append-only: add dated entries below the last one and leave earlier lines as written.
- `ticket-ledger.md` columns for issue, title, spec, GitHub state, frontier and blockers are regenerated from the tracker (`gh api graphql` with `blockedBy` and `parent`); the lane and local-state columns are the parent's edits at each lane transition.
- `task_plan.md` and `progress.md` are parent-owned shared files; a lane proposes edits in its handoff.
