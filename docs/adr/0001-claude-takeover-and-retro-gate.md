# 1. Claude team takeover with a mechanical retro gate

Date: 2026-10-13

## Status

Accepted

## Context

Four Codex threads carried the marketplace work from 2026-10-10 to 2026-10-13
under a single-writer-per-worktree contract with a retrospective after every
unit. On 2026-10-13 Codex hit its usage limit until 2026-10-19 while T4, A06
unit3 and two tracker commits were mid-flight. The user asked a Claude Code team
to take over, keep every Codex worktree and private evidence packet untouched as
import sources, and make "retro after every ticket, apply every learning" a rule
the harness enforces instead of one an agent remembers. Codex may resume after
2026-10-19 and must meet the same rule. The parent's draft gate, calibrated against
the 33 existing Codex retro records, found 17 that skipped at least one
category, which is why prose lost to a mechanical check.

## Decision

The Claude session is the sole integration writer for
`codex/marketplace-native-onboarding` and the canonical plan. Implementers work
in `.claude/worktrees/<unit>` on `claude/<unit>-<slug>` branches with path
allowlists, and a separate merger integrates serially.

One deterministic check, `dev/retro_gate.py`, enforces the retrospective. It
runs three ways from the same mise task: as an `hk` git `pre-merge-commit` and
`pre-push` step (agent-independent, so it binds Codex too), as Claude Code
`PreToolUse` denials on `git merge`, `git push` and `delivery:publish`, and as
`Stop`/`SubagentStop` blocks keyed to a lane record.

Learnings land by kind: navigation in the nearest `AGENTS.md` or
`.claude/rules`, judgement in `CODING_STANDARDS.md`, repeated workflows in
skills, roles in `.claude/agents`, mechanical rules in `dev/check.py`.

## Consequences

Integration and publication fail closed when a unit has no retro record or an
unresolved finding, for humans and for both agents. Retained Codex worktrees
cannot push until they carry `hk.pkl`, which is intended. The gate checks record
shape and bindings only; judgement about findings stays with the independent
reviewer. Every lane pays the cost of a retro record before it can land, and the
plan ledger becomes the place where ticket state is read.
