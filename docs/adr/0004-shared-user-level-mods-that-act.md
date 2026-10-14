# 4. Mods may act where only a mod can, and shared mods live in the dotfiles repo

Date: 2026-10-14

## Status

Accepted (user, grill-with-docs rounds 1 and 2; plan decisions D61, D62, D66 and D74, amending
D55). Amended by ADR 0006 (D87, 2026-10-14): the shared mods are built in this repository as a
local directory plugin, not in the dotfiles repository. Superseded in part by ADR 0007 (D92): mods
now replace this repository's settings hooks, so the settings-hook backstop rule no longer holds.
D102 keeps the three deny gates as settings hooks for reasons of their own (ADR 0007).

## Context

D55 kept mods display-only, with every gate in settings hooks. Two user requests need behaviour
only a mod has (`.planning/<PLAN_ID>/reviews/ccm-20261014/grill-facts/F1-claude-code-mechanics-u2-u3.md`):
running `/reload-plugins` and renaming the session before the first prompt, and answering a
WebFetch call with webclaw's full page before the fetch runs. Both needs apply to every project,
and the dotfiles repo already had a project-local session-start mod with the same purpose.

## Decision

A mod may act when no hook can do the job, and each such mod keeps a settings-hook backstop for
sessions where mods are off (`--bare`, `--safe-mode`) or events where the mod does not fire
(`/clear`). Mods that serve every project are built once in the dotfiles repo as user-level mods
with a per-repository table (session-name prefixes `ccm`, `dotfiles`, `kb`); this repository keeps
only its backstop hooks and tests. Display-only mods stay project-local.

## Consequences

Work on these mods happens in the dotfiles repository under the admission recorded as D66; this
repository's tickets CT-35 and CT-36 verify the adopted mods rather than build copies.
