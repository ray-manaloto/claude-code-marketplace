# 2. Greenfield: no technical debt, frozen baseline lifted

Date: 2026-10-14

## Status

Accepted (user, grill-with-docs round 1; plan decisions D59 and D64)

## Context

The project carried compatibility layers from its Codex phase: two ways to launch Python in mise
tasks, a frozen 19-file acceptance baseline that forced workarounds (worktrees hidden through
`.git/info/exclude` because `.gitignore` was frozen, new tooling kept out of the root mise files),
and migrations planned as "later" tickets. The user declared the project greenfield.

## Decision

Every change modernizes fully and removes the old path in the same change: no compatibility
shims, no dual paths, no deferred migrations. The frozen baseline is lifted through CT-08, which
runs in the first implement-spec wave and re-records the baseline after deliberate changes.
Marketplace and plugin identity (names, CLI, wrappers, data paths) stay preserved; what lifts is
the byte freeze, not the identity.

## Consequences

A reviewer rejects a lane that leaves an old path beside a new one. Work that only existed to
respect the freeze (for example `.git/info/exclude` entries) is removed by CT-08 rather than kept.
