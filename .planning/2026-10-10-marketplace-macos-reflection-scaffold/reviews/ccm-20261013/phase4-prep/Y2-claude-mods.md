# Y2: Claude Code mods for workflow automation

Reviewer: claude-code-guide agent, 2026-10-14; saved verbatim by the parent (the agent cannot write files).

## Summary

Mods are Claude-only JavaScript or TypeScript handlers that run inside Claude Code. They draw panes, a band above the prompt, and toasts only in the terminal and the Desktop Code tab. Hooks still run in `-p`, the SDK and cloud sessions, but nothing is drawn there.

Mods suit the display side: a status band, a lane pane, a `/lanes` command, and a grill dialog that answers `AskUserQuestion`. They should not be the only gate. Mods are switched off by `disableAllHooks`, `--safe-mode`, `--bare` and `allowManagedModsOnly`. Enforcement belongs in settings hooks, which can block: Stop (exit 2), PreToolUse (`permissionDecision`), PreCompact (exit 2). The built-in `statusLine` should carry HEAD versus upstream, merge state and context percent.

Packaging: a plugin directory at `plugins/workflow-mods/`, loaded with `--plugin-dir`, validated and tested in `./dev/mise run check`.

Gaps: the bundled `plugin-authoring` directory has no SKILL.md, only reference.md, types and examples.

Page key (all under https://code.claude.com/docs/en/): M-OV plugins/mods/overview, M-EV plugins/mods/events, M-IF plugins/mods/interface, M-API plugins/mods/api, M-REF plugins/mods/reference, M-CR plugins/mods/create, M-AD plugins/mods/admin, M-TS plugins/mods/troubleshoot, M-TEST plugins/mods/test, H hooks, SL statusline, SK skills, CMD commands, PL plugins. Local: `/private/tmp/claude-501/bundled-skills/2.1.296/005e5f45c20a8437ea4b69f3330aba3b/plugin-authoring/reference.md` (PA).

## 1. Capability map

| Capability | API or file | Limit |
|---|---|---|
| Hook: observe, rewrite, answer | `on(event, matcher, ($, e, next))` in the hooks module (M-EV, M-REF) | 10 s per hook, excluding time in `next` or API calls; `.catch` 1 s |
| Tool guard | `tool.call` answers `{deny}` or `{result}`; `tool.check` returns `{decision}` (M-EV) | Mods run before non-managed settings PreToolUse hooks |
| Pane | `$.ui.open({id,title,focus,closeOnEscape,rows,columns})` plus `ui.render{component:'Pane'}` (M-IF) | Timer-opened panes need 144+ columns |
| Band above prompt | `ui.render{component:'AbovePrompt'}` (M-IF) | One shared strip; a tree replaces later mods unless it includes `await next(e)` |
| Redraw built-in sites | Spinner, ToolUse, AskUserQuestion, etc. (M-REF render sites) | Tree must include the reference once or the engine draws its own |
| Controls | Button (`hotkey`, `plain`), Input (`onSubmit`), Select (M-IF, M-REF) | Hotkey is one digit or lowercase letter |
| Toast, status, log | `$.ui.toast` (4 s default), `$.ui.status` (line under prompt), `$.ui.log` (transcript, or `{to:'debug'}`) (M-API) | |
| Commands | `$.command.register({name,description,argumentHint,immediate})`; `command.run` answers `{text}` or `{}` (M-API) | Built-in names refused |
| Tools for Claude | `$.tool.register`, exposed as `mcp__<plugin>__<name>` (M-API) | |
| Ask user | `$.ui.ask(question, labels)`, resolves to label or typed text (M-EV) | Wait inside a mods API call is not counted against the hook limit |
| Model, timers | `$.model.complete`, `$.model.fork`; `$.clock.every/after` (M-API) | Bills to user; timers stop on reload |
| Shell, files, network | `$.process.run` (argv, no shell, 30 s default, 10 min max), `$.fs` (4 MiB), `$.http.fetch` (30 s) (M-API, M-REF) | Not governed by Bash deny rules (M-AD) |
| State | `$.state` (declared in `types/index.d.ts`), `$.store` (4 MiB, shared by all sessions) (M-IF) | |
| Session, agents | `$.session.usage()` gives context tokens, window, percent and rate limits; `$.agent.list()` gives status (M-REF) | |
| Redraw throttle | `$.ui.invalidate('ui.render')`: 10 per second, 30 for the visible terminal pane (M-REF) | |

Settings hooks (H) and `statusLine` (SL) are separate: they run scripts, not handlers. The status line receives stdin JSON with `context_window.used_percentage`, `total_input_tokens`, `context_window_size` (200K default or 1M), `workspace.git_worktree`, `transcript_path` and `session_id`. It is debounced at 300 ms, and `refreshInterval` has a minimum of 1 (SL).

## 2. Proposed mods

Shared layout. `modules` takes one path, so `register.js` imports the rest.

```
plugins/workflow-mods/
  .claude-plugin/plugin.json   # name, version, "types" if $.state is used
  hooks/hooks.json             # {"modules": ["./register.js"]}
  hooks/register.js            # imports band, lanes, grill, verify
  hooks/{band,lanes,grill,verify}.js
  types/index.d.ts             # only if $.state is used
  tests/*.test.ts              # claude plugin test
```

**(a) Status band (AbovePrompt band).** Shows active lanes, pending decisions, and the last verify result. Data: `frontier.py status --json`, pending rows from `decisions.jsonl` (read-only query on `dev/plan_decide.py`). Events: `session.start`, `ui.render{AbovePrompt}`, `turn.complete`. Cadence: `$.clock.every(5000)` plus invalidate on `turn.complete`; each poll well under 200 ms. Removes checking lanes and decisions by hand. Git and context percent stay in the built-in status line: `git rev-list --left-right --count HEAD...@{u}`, `git rev-parse --git-path MERGE_HEAD`, and `used_percentage`; the 550K threshold only makes sense with a 1M window, so compute it from `total_input_tokens`.

```js
// hooks/band.js
let state = { active: 0, pending: 0 }
export function register(on) {
  on('session.start', async ($, e, next) => {
    $.clock.every(5000, async () => {
      const r = await $.process.run(['python3', 'scripts/frontier.py', 'status', '--json'])
      if (r.exitCode === 0) state = JSON.parse(r.stdout) // guard in real code
      $.ui.invalidate('ui.render')
    })
    return next(e)
  })
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const { Box, Text } = $.ui.resolve(e)
    return Box({
      flexDirection: 'row', columnGap: 2,
      children: [
        Text({ children: ['lanes ' + state.active] }),
        Text({ children: ['decisions ' + state.pending] }),
        await next(e), // keep later mods' band content
      ],
    })
  })
}
```

**(b) Lane pane.** Pane plus command. `/lanes` (`immediate: true`) opens pane `id: 'lanes'`, and `ui.render{Pane}` filters on `requestId === 'lanes'`. Data: frontier status JSON, lane records under `.planning/.../lanes/`, `$.agent.list()` for live subagents. Events: `command.run`, `ui.render{Pane}`, `ui.close` (stops the timer). Cadence 2 s while open; a button press runs `git -C .claude/worktrees/<unit> status --short`. Removes listing worktrees and lane stages by hand.

**(c) Verify.** The display is a mod: a `turn.complete` text line, a red band flag, a toast. The enforcement is a settings Stop hook that exits 2 when the receipt is missing (H). A mod cannot block the end of a turn (`turn.complete` only observes). Keep `/verify` as a skill; do not register a mod command with that name.

**(d) Pre-clear handoff check.** A `/handoff-check` mod command runs `session:handoff --check` and shows the result in a pane or toast. Blocking `/clear` is not verifiable (`session.end` can only pass through, M-REF). Enforce with a settings PreCompact hook (exit 2 blocks compaction, H) and optionally a `session.compact` `{skip}` mod hook (M-REF). A Stop-hook check can block when tokens reach 550K without a handoff.

**(e) Grill mod (CT-13).** A `tool.call` hook matching `{tool:'AskUserQuestion'}` asks each question with `await $.ui.ask(question, options)` (already offers a typed-answer row), then asks for notes with a second `$.ui.ask`, and returns `{ result }` without calling `next`. The result shape must match the tool type in the generated `claude-code-tools/index.d.ts`. The test kit uses `{ answers: { [question]: label } }` (M-TEST), the only evidence. Do not put an `Input` inside the AskUserQuestion site: a value entered there has no route back to the tool.

**(f) Agent-dispatch guard.** Enforce in settings PreToolUse, matching the subagent tool (name to confirm), with a script that reads `decisions.jsonl` and runs `brief_lint`. A mod-only deny would fail silently under `disableAllHooks`, `--safe-mode`, `--bare` or `allowManagedModsOnly`. A mod's `{deny}` also stops later settings PreToolUse hooks (M-EV), so the mod must not be the only guard.

**(g) Other easy wins.** `classic.SessionStart` with `source` clear, resume or fork refreshes band state (M-IF). `turn.step` gives per-request usage. `session.measure` and `$.session.usage()` feed the band without parsing the transcript.

## 3. What should not be a mod

- Stop and SubagentStop gates: settings hooks with documented blocking (H); must run in headless and CI sessions too.
- Bash gate: fix the "git merge" false positive with the `if` field (`Bash(git merge *)`), which uses permission rule syntax (H), not a substring regex.
- Doctor session-start block: a SessionStart hook with `additionalContext` (H). Mods do not draw in `-p` or cloud.
- Context checkpoint and fork-deny: PreCompact, Stop and UserPromptSubmit reading `transcript_path`; the mod only displays.
- Frontier, receipts, `/verify` writer, doctor surface: skills, agents, scripts and mise tasks, which run headless.

Mods are off under the switches listed above, are not sandboxed, and bypass Bash deny rules through `$.process.run` (M-AD).

## 4. Packaging

- Dev loop: `claude --plugin-dir ./plugins/workflow-mods`. Saves reload the hooks module after a short quiet period, or at turn end while Claude is editing. `/reload-plugins` for installed copies (M-CR, PA).
- Ship: `plugins/workflow-mods/`, matching `plugins/aggregated-research/`. A folder marketplace with a relative source is read in place (PA, PL). Enablement (`extraKnownMarketplaces`, `enabledPlugins`) belongs in `.claude/settings.json` under CT-02. Collaborators still install.
- Versioning: bump `version` for installed copies (cached by version); in-place folder marketplaces need no bump during development.
- Tests: `claude plugin test` runs `tests/*.test.ts` with no sign-in or network, exits 1 on failure. `claude plugin validate <dir> --strict --json` belongs in `./dev/mise run check` (M-TEST, M-REF).
- Authoring loop: `/plugin-authoring` (built-in, from `cc-plugin-plugin-authoring`) lets Claude write the mod; generated types land in `.claude-plugin/types/`; session-written mods go to `~/.claude/dev-mods/<session-id>/` and expire by `cleanupPeriodDays`, so copy them into the repo (M-CR).
- Version gate: mods need Claude Code 2.1.287 or later (`claude --version`).
- Codex: mods stay out of Codex configuration, as AGENTS.md requires.

## 5. CT-31 ticket text

**Title:** CT-31 Workflow mods: status band, lane pane, verify display, grill dialog (subsumes CT-13; close CT-13 as duplicate)

**Blocked by:** CT-02 (settings composition enables the plugin), w0-doctor (band data source), CT-29 (`session:handoff --check`), the `/verify` receipt format (Y3).

**owned_paths:** `plugins/workflow-mods/**`, `docs/agents/workflow-mods.md`.

**Disjoint from queued lanes:** must not touch `.claude/settings.json` or `.claude/hooks/**` (CT-02, w0-session-hooks), `dev/doctor/**` and `dev/mise.toml` (w0-doctor, w0-doctor-records), `scripts/frontier.py` and `scripts/session/**` (CT-29, CT-21, CT-26, CT-28, D7). Check `evidence/onboarding/baseline-files.json` before touching `.claude-plugin/marketplace.json`.

**Acceptance:** `claude plugin validate --strict` passes; `claude plugin test` covers band parsing, lane rendering, and the grill answer shape; the band and lane pane show in a `--plugin-dir` session; no mod is the sole gate (gates stay in settings hooks); the ticket ends at the retro gate and runs `/verify`, writing a receipt.

## 6. Could not verify

- The bundled SKILL.md is absent; reference.md and the docs were used.
- Whether a `command.run` hook on built-in `/clear` or `/compact` can refuse the command.
- `$.process.run` options (`cwd`, timeout) and the minimum `$.clock.every` interval.
- The `AskUserQuestion` result shape beyond the test-kit example, and the `$.ui.ask` signature.
- The subagent dispatch tool name and its input fields, and how `brief_lint` plugs in.
- Whether the Stop input includes a re-entry flag such as `stop_hook_active`.
- Lane record field names and the `dev/plan_decide.py` query subcommand.
- Whether the built-in status line refreshes during a turn beyond event triggers and `refreshInterval`.
- Whether `context_window.total_input_tokens` matches `$.session.usage().context.tokens`.
- The user's exact Claude Code build, and `/verify`'s receipt path (assumed).
- None of the examples were run; skeletons are unexecuted.
