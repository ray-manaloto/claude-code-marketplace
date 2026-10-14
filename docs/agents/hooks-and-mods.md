# Hooks and mods

Which workflow rules run as Claude Code mods, which stay settings hooks, and what to watch before
changing that. Decisions: D92, D94, D95, D102, D103, D128, D130 and D131 in the plan's Decisions
table; ADR 0007 and ADR 0008. Evidence: `.planning/<PLAN_ID>/reviews/ccm-20261014/research5/` R1
(mod loading gaps), R2 (issue #92533), R3 (awaiting the plugin reload), R7 (detecting the remote
switch), R8 (C++ gate hooks) and R9 (C++ bridges), all cited to Claude Code docs, its changelog and
anthropics/claude-code issues.

## The rule

- New workflow behaviour is a mod in the TypeScript mods library (D92, D94). Mods replace this
  repository's settings hooks, and the replacing change deletes the hook.
- Three deny gates stay thin settings hooks (D102): `PreToolUse` on Bash, `Stop` and `SubagentStop`
  in `.claude/settings.json`, run by `dev/hooks/pretooluse_gate.py`, `stop_gate.py` and
  `subagent_stop_gate.py`. Do not move or delete them without a new decision.
- Until the mods-library units land, the other hooks in `.claude/settings.json` stay as they are; the
  unit that ships each mod deletes its hook in the same change (D59).
- Third-party plugin hooks, such as planning-with-files, are outside this rule.

## Why the three deny gates stay hooks

Cited in R1 and R2:
- Anthropic's remote rollout switch has turned mods off for real users, including mods loaded with
  `--plugin-dir` in `claude -p` runs: [anthropics/claude-code#99130](https://github.com/anthropics/claude-code/issues/99130).
  A gate that a remote switch can disable is not a gate.
- `Stop` events reach mods unreliably depending on version and session type:
  [#96831](https://github.com/anthropics/claude-code/issues/96831),
  [#100869](https://github.com/anthropics/claude-code/issues/100869), both open through 2.1.299.
- `delivery:publish` pushes with `--no-verify`, so the hk pre-push hook cannot stop it; the Bash
  `PreToolUse` gate is the only check on that path.
- A headless run in a folder that was never trusted (CI, a fresh clone) skips a project skills-dir
  plugin but still runs settings hooks (R1 confirms A2 section 1.3).
- No project R1 examined enforces deny gates through mods.

## What mods must do differently (R2, R3)

- A Bash mod uses `tool.check`, never a `tool.call` hook with a Bash, empty, `*` or RegExp matcher:
  that shape broke Bash in worktree-isolated subagents
  ([#92533](https://github.com/anthropics/claude-code/issues/92533), fixed in the 2.1.288 changelog
  but still open; npm `stable` was 2.1.287 on 2026-10-14). Do not spawn subagents with
  `isolation: "worktree"` until a regression check on this host passes.
- Mod events do not report the working directory
  ([#101384](https://github.com/anthropics/claude-code/issues/101384), open); a rule that depends on
  the directory stays in a hook or in hk.
- The session-start mod awaits `/reload-plugins` without `--force` inside `session.start`; the first
  prompt waits for it ([PR #94594](https://github.com/anthropics/claude-code/pull/94594)). Queued,
  unawaited commands can lose the race to the first prompt
  ([#84320](https://github.com/anthropics/claude-code/issues/84320)). Skills reload and the session
  name come from its `classic.SessionStart` result (`reloadSkills`, `sessionTitle`).

## Mods stay thin, and the gates go native (R7, R8, R9)

- A mod holds no logic of its own: it calls the C++ core through `$.process.run` and relays the
  JSON result, because a mod cannot load native code (R9; D130; ADR 0008).
- The aggregated-research plugin's SessionStart follows R7 (D128): the mod does the work and passes
  a handled mark to `next()`; a thin hook in the same plugin stands down on the mark, else does the
  work itself; a per-session claim directory prevents a double run. One admitted live probe runs
  first and confirms that the mark reaches the hook and the start-up order.
- The three deny gates port to C++ once the `rsm-core` skeleton builds, with a bootstrap path so an
  unbuilt binary cannot block the build that makes it (D131). They stay settings hooks (D102).
- Claude Code's docs say `onFailure` has no effect on `Stop` and `SubagentStop` (R8, section 2): a
  Stop or SubagentStop gate that crashes or cannot start lets the turn end, so it is silently off
  whatever `onFailure` says in `.claude/settings.json`. Fail-closed there needs another mechanism
  (CT-02b.1).

## Watch list (ticket CT-80)

Recheck before any change to the rule, and whenever one of these moves: #99130, #96831, #100869,
#92533, #101384, #84320, and any Claude Code changelog entry that mentions mods, `tool.check`,
`session.start` or the rollout switch. A recheck runs the two-stage research route of D100 and writes
a new cited report beside R1-R3; a decision changes only from that report.
