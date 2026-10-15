# 6. This repository absorbs the agent workflow of three source projects, which are then sunset

Date: 2026-10-14

## Status

Accepted (user, grill-with-docs round 3; plan decisions D87 and D88; amends ADR 0004). Extended by
D96 (the knowledge-base backend and an installable package move here), D98 (TR exported
by path allow-list only) and D109 (this repository owns the host-wide heavy lock).

## Context

Agent-workflow features were spread over four repositories. The dotfiles repository held the
session-start mod, research sweeps and handoff tooling; the knowledge-base repository held session
state, skill lint and its own `aggregated-research` entry point; the TR project held an
offline documentation corpus and audits; this repository publishes the marketplace and its plugin.
Each copy drifted: the dotfiles session-start mod has no `ccm` prefix and does not wait for its
reloads, and the TR import (D81) found fabricated output and lossy indexes. Codex had
dispatch skills (`claude-agent`, `codex-agent`) that Claude lacked.

## Decision

This repository becomes the single home of the agent workflow: skills, agents, hooks, mods, mise
tasks, research tooling, planning, handoff and checks, plus the offline documentation, cloned
repositories, documents, blogs and articles the three source projects collected. Features come
over as improved designs through tickets, never as copies, under the greenfield rule (ADR 0002).
Mods are built here as a local directory plugin rather than in the dotfiles repository. The Claude
versions of the two Codex dispatch skills and their shared protocol live here too. Host setup
(shell, chezmoi, fnox configuration, global mise profiles, devcontainers) stays in the dotfiles
repository until a later decision.

## Consequences

A read-only import review (`.planning/<PLAN_ID>/reviews/ccm-20261014/project-import/`) inventories
each source and writes a sunset checklist; a source project is retired only after every item on
its checklist has a landed ticket here. Until then the source projects keep running unchanged and
are read, never edited, by this repository's agents, except by the sunset tickets CT-62 and CT-78
under their outward admissions (D96) and the dotfiles `host_lock.py` repoint that flips with
CT-63a (D109).
