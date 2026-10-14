@AGENTS.md

Codex-specific configuration under `.codex/` is not Claude hook configuration.

## Agent skills

The issue tracker pointer lives in `AGENTS.md` (`docs/agents/issue-tracker.md`).

### Triage labels

Use the five canonical triage roles in `docs/agents/triage-labels.md`.

### Domain docs

Use the single-context glossary and ADR layout in `docs/agents/domain.md`.

# Compact instructions

Carry the task_plan `## Open requests` section into the summary under Pending Tasks: every open
`- [ ] R-n (...)` line verbatim, its `issue:` link and any `owner user` included; the decision ids in
its parentheses are references, and the line stays open until its box is ticked (D166). Done when
the summary holds one `R-n` line per open item the PreCompact hook printed.
