@AGENTS.md

Codex-specific configuration under `.codex/` is not Claude hook configuration.

## Agent skills

The issue tracker pointer lives in `AGENTS.md` (`docs/agents/issue-tracker.md`).

### Triage labels

Use the five canonical triage roles in `docs/agents/triage-labels.md`.

### Domain docs

Use the single-context glossary and ADR layout in `docs/agents/domain.md`.

# Compact instructions

Carry every open request into the summary under Pending Tasks: each `R-n` id from the task_plan
`## Open requests` section with its `p:<id8>` key, owner, blocker and next action, one line per id.
Keep open requests apart from decisions; a decision id beside a request is a reference, not its
closure (D166).
