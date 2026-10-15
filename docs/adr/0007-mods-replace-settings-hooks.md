# 7. Mods replace this repository's settings hooks

Date: 2026-10-14

## Status

Accepted (user, grill-with-docs rounds 4 and 5; plan decisions D92 to D95, D97, D102 and D103;
supersedes D55 and the settings-hook backstop rule of ADR 0004). D99 makes the plugin's
consumer-facing SessionStart hook a mod too (Q82 asks how to detect the remote switch first); D100
decided the gaps Q68, Q70 and Q71 on research R1-R3; D101 keeps w0-doctor's SessionStart entry until
A2-11 replaces it; D103 replaces the forced reload with an awaited plain `/reload-plugins`.

## Context

This repository enforced its workflow through settings hooks: a PreToolUse gate on Bash, Stop and
SubagentStop retro and verify gates, and session hooks. Claude Code mods can also act on session,
prompt and tool events, can answer a tool call before it runs, and can run slash commands, which no
hook can. The user wants one extension mechanism to build up, a library of mods, rather than two.
Neither mods nor settings hooks run under `--bare` or `--safe-mode`; only managed settings would
guard those sessions.

## Decision

Every settings hook this repository owns migrates into a mod, and the hook is deleted in the same
change, except the three deny gates (Bash `PreToolUse`, `Stop`, `SubagentStop`), which stay thin
settings hooks after cited research (D102; `docs/agents/hooks-and-mods.md`). The mods form one TypeScript library with a modern project setup, continuous integration
and mise, hk and fnox integration. The session-start mod names the session and runs
`/reload-skills` and `/reload-plugins --force` before the first request; the WebFetch mod answers
fetches through the `web:fetch` task and denies on failure. Sessions started with `--bare` or
`--safe-mode` are unguarded by choice; no managed settings are added. Third-party plugin hooks,
such as planning-with-files, are outside this decision.

## Consequences

The wave-0 lane that would have built new settings hooks is closed before its cut. The deny-gate
tickets (CT-02b, CT-17's stop-gate part CT-17b, CT-32b) stay hook work on the three gate scripts
(D102); CT-23 and the mod tickets (CT-31, CT-35, CT-36), plus mod units of CT-19, CT-37 and CT-61,
are built on the library. hk Git hooks stay the Git-side gate (A2 G5). CT-80 watches the upstream
issues behind D102, and a change there reopens it. Where a hook event has no mod equivalent, the
design report
(`.planning/<PLAN_ID>/reviews/ccm-20261014/project-import/A2-typescript-mods-library.md`) names the
gap, and the user decides each one.
