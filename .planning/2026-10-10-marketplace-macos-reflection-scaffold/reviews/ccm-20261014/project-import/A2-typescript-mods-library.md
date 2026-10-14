# A2: TypeScript mods library (design, 2026-10-14)

Written by subagent A2 of session `ccm-20261014` (`ce9c0b3d`), read-only except this file. MP at
`21af565`, branch `codex/marketplace-native-onboarding`. Installed CLI: Claude Code 2.1.299 (`claude
--version`). P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. Decisions this design
serves: D89 (DL-117), D92 (DL-122), D93 (DL-123), D94 (DL-124), D95 (DL-125), D97 (DL-127) in
`P/decisions.jsonl:117-127`.

## Sources and spikes

- T: the 2.1.296 declarations
  `/private/tmp/claude-501/bundled-skills/2.1.296/005e5f45c20a8437ea4b69f3330aba3b/plugin-authoring/types/claude-code.d.ts`
  (newest bundle on disk; no 2.1.299 bundle exists yet) and `reference.md` beside it (PA). The dotfiles copy
  `dotfiles/.claude/types/claude-code.d.ts` is 2.1.277 and stale (its header, line 1).
- Docs fetched on 2026-10-14 with `webclaw -t 60 <url> -f markdown`; line numbers refer to that output.
  M-OV `https://code.claude.com/docs/en/plugins/mods/overview.md`, M-EV `.../plugins/mods/events.md`, M-REF
  `.../plugins/mods/reference.md`, M-CR `.../plugins/mods/create.md`, M-TS `.../plugins/mods/troubleshoot.md`,
  M-AD `.../plugins/mods/admin.md`, H `.../hooks.md`, CLI `.../cli-reference.md`, LD `.../plugins/loading.md`,
  PERM `.../permissions.md` (raw markdown via curl; webclaw truncated it).
- Upstream mods source, `gh api` on `anthropics/claude-code` default branch: `mods/README.md`,
  `mods/tsconfig.json`, `mods/sec-default/README.md`, `mods/diff/hooks/host/host.ts`; issue
  anthropics/claude-code#92533 (open, created 2026-09-06).
- Tool facts: npm registry dist-tags (2026-10-14), `https://raw.githubusercontent.com/nodejs/Release/main/schedule.json`,
  pnpm `https://pnpm.io/settings/dependency-resolution` and `https://pnpm.io/settings/build`, oxlint
  `https://oxc.rs/docs/guide/usage/linter/type-aware.html`, Biome `https://biomejs.dev/linter/rules/no-floating-promises/`,
  mise deps `https://mise.jdx.dev/dev-tools/deps.html`, hk builtins `https://github.com/jdx/hk/tree/v2.6.0/pkl/builtins`.
- Research route: webclaw, curl and `gh api` only. The AGENTS.md five-source fnox route (Exa, Firecrawl,
  Last30Days, Context7, GitHub) was not run: no provider calls were admitted for this design. Gap recorded.

Spikes, all in the session scratchpad (nothing in the repo), on this host:
- S1. TypeScript 7.0.2 `tsc -p` with upstream `mods/tsconfig.json` options plus `exactOptionalPropertyTypes`
  and `verbatimModuleSyntax`, against T: rc 0 for a module hooking `classic.Stop` (answer `{ block }`),
  `tool.call` WebFetch (answer `{ result }` in WebFetch's output shape), `agent.spawn` and `classic.SessionStart`
  (answer `{ sessionTitle, reloadSkills, additionalContext }`); rc 1 with the right messages for `block: 42`,
  a string assigned to a number, and `$.session.rename` (absent). 0.09 s wall.
- S2. `claude plugin validate .` (2.1.299): passed with warnings (no `description`, no `author`); it listed each
  gating hook "with .catch" or "without .catch", and printed: "hooks on classic.Stop, classic.SessionStart do
  not run in a plugin a person installs where an organization manages Claude Code".
- S3. `claude plugin test .` (2.1.299, signed in, macOS): 3 of 3 pass. A `classic.Stop` hook answered
  `{ block: 'gate failed' }` when a stubbed `process.run` exited 2; passed on `stop_hook_active`; a `tool.call`
  WebFetch hook answered with the stubbed page.
- S4. oxlint 1.88.0 with oxlint-tsgolint 7.0.2004 `--type-aware` flagged both unawaited `$.command.run(...)` and
  `$.process.run(...)` in a `session.start` hook (rc 1). Biome 2.5.15 with nursery `noFloatingPromises` and
  `noMisusedPromises` reported nothing on the same file.
- S5. Vitest 5.0.4 ran a spec over a typed fake `Host` (`vi.fn<Host['process']['run']>`): 2 pass; tsc 7 type-checked
  the spec. Vitest's default include also collected the engine-kit `tests/*.test.ts` and failed on
  `claude-code/testing`, so the unit-test glob must exclude them.
- S6. `https://raw.githubusercontent.com/anthropics/claude-code/v2.1.299/mods/types/claude-code.d.ts` serves a file
  whose header reads "Written by Claude Code 2.1.277": the upstream copy lags and is not a version-matched source.
- Host facts: no `/Library/Application Support/ClaudeCode/` (no managed settings); `claude auth status` reports
  `subscriptionType: max`, so the `sec-default` guard is not seated today (M-REF:322).

## 1. Hook-to-mod map

### 1.1 Facts every row relies on

- A settings hook event is also a mod event `classic.<Event>`; it "fires wherever the engine runs the classic hook,
  whether or not any settings hook is configured" (T:1235-1243). Its answer is a `ClassicResult` whose `block` is
  "`decision: "block"` ... the event's block, veto or re-prompt" (T:1282-1287) and whose event-specific fields are
  listed per event (T:1366-1383: SessionStart `additionalContext`, `sessionTitle`, `reloadSkills`; UserPromptSubmit
  `additionalContext`, `sessionTitle`; Stop and SubagentStop `additionalContext`). The chain is [managed settings
  hooks, hooks modules, other settings hooks] (T:1250-1251). S1 and S3 confirm the shape and the engine kit.
- `tool.call` fires for subagent calls too (M-EV:100), with `e.agentId` (T:194-204). Managed PreToolUse hooks run
  first; project and plugin PreToolUse hooks run after the last mod calls `next`, so a mod that answers without
  `next` keeps them from running (M-EV:141, 305-312).
- A failing hook is skipped unless `.catch` answers; `.catch` has 1 s, and if it throws the hook is skipped as if
  it had none (M-EV:314-340; M-REF:283-284). A hook's own time limit is 10 s, not counting time inside `next` or a
  `$` call (M-REF:283), so a `$.process.run` child does not spend it.
- `session.start` fires once per loaded mod before the first prompt, "Not after `/clear`, `/resume`, or `/branch`"
  (M-REF:117); `session.end` fires with `reason: 'clear'` (T:4423-4434).
- Settings hooks and mods are both off under `--bare` (CLI:74; M-TS:66) and `--safe-mode` (CLI:131; M-CR:62), and
  `disableAllHooks` stops both (M-OV:106). So D92's accepted gap costs nothing relative to today's hooks.

### 1.2 Map

| Hook (today or planned) | Mod event and API | Blocking | Subagents | `/clear` | Failure handling |
|---|---|---|---|---|---|
| PreToolUse Bash retro gate (CT-02; `.claude/settings.json:41-53`, `dev/hooks/pretooluse_gate.py:63-84`; D58 false positive at `:71-72`) | `tool.call` `{ tool: 'Bash' }`: a TS token parse of `e.command` (segments, `git -C`, heredoc bodies and quotes skipped) prefilters; only a hit runs the existing Python gate through task `gates:bash`; answer `{ deny: reason }` before `next` | Same effect: Claude reads the reason as the tool result, no prompt (M-EV:102-115). Runs before the remaining settings PreToolUse hooks, so a deny also stops user-level hooks such as planning-with-files' injector | Yes (M-EV:100). The event has no `cwd`: Bash input is `command, timeout, description, run_in_background, dangerouslyDisableSandbox` (T:16196-16201), while the settings input carries `cwd`. Repo resolution falls back to `git -C` and `$.session.cwd()` (spike A2-0 arm 6) | No effect (module stays loaded) | Settings: `onFailure: block` works on PreToolUse (H, "Block the action when a hook fails"). Mod: `.catch` denies when `next.called` is false |
| Stop retro gate (`dev/hooks/stop_gate.py:18-33`, settings `:66-77`) | `classic.Stop` answering `{ block: reason }` when `!e.stop_hook_active` | Same re-prompt; the 8-continuation cap (H, Stop input) applies to the event. Two gates (retro, then CT-32b verify) must compose in one hook: a first hook that answers without `next` hides the second | Main loop only, as today | No effect | Better than today: H says `onFailure` has no effect on Stop and SubagentStop, while a mod's `.catch` can answer `{ block }` when `!e.stop_hook_active` (fail closed once, never a loop) |
| SubagentStop retro gate (`dev/hooks/subagent_stop_gate.py:19-36`, settings `:54-65`) | `classic.SubagentStop` `{ block }`; `e` carries `cwd`, `agent_id`, `agent_type`, `last_assistant_message` (H, SubagentStop input) | Same: the reason becomes the subagent's next instruction (H); DF-A 3.5 CT-32b row (block displaces the final report) holds for both | Every subagent, internal ones included (H) | No effect | Same as Stop |
| SessionStart doctor (w0-doctor `f1bbc8d`; `.claude/worktrees/w0-doctor/.claude/settings.json`, matcher `startup\|resume\|clear\|compact\|fork`, timeout 15) | `classic.SessionStart` answering `{ ...await next(e), additionalContext: [stdout] }` from task `doctor:session-start` (`timeoutMs: 15000`) | Context only, never blocks, as today | Main session | Fires with `source: 'clear'` (classic event), unlike `session.start` | Non-blocking in both; the mod logs `doctor-context ERROR: <reason>` and adds a one-line "doctor did not run" context |
| UserPromptSubmit prompt hook (w0-session-hooks, `P/lanes/w0-session-hooks.json:24`; cancelled by D97; CT-23) | `prompt.submit` returning `next({ ...e, context: [...(e.context ?? []), line] })`; ctx from `$.session.usage().context` (T:11712-11727), no transcript read (replaces `dev/context_budget.py`) | Never drops, as designed | Main prompts only, as today | No effect; thresholds re-armed by session id | `.catch` passes the prompt (`next(e)`) |
| PreToolUse Agent gate (`P/lanes/w0-session-hooks.json:23`; CT-23, CT-19) | `agent.spawn` (T:4084-4098): `{ deny }` for a fork at ctx >= `fork_deny` and for a `LANE-UNIT` brief sent to `general-purpose` while the role exists; for `implementer` the hook appends the ctx line to `e.prompt` (`next({ ...e, prompt })`) instead of `additionalContext` | `agent.spawn` has no `ask`. The `ctx >= hard` ask becomes `tool.check` `{ tool: 'Agent' }` answering `{ decision: 'ask' }` (M-EV:182-205), or `$.ui.ask`, which has no surface in `-p` (deny there) | Spawns from subagents too (`parentAgentId`, T:317). `SendMessage` resumes skip `agent.spawn` (M-REF:134); match `tool.call` `SendMessage` if needed | No effect | `.catch` denies (`next.called` false); validate flags a gate without `.catch` (S2) |
| CT-17 `stop_gate` extensions (ticket-ledger.md:148) | Same `classic.Stop` hook, more lane-state checks | As Stop | As Stop | As Stop | As Stop |
| CT-23 follow-ups (ledger:154): thresholds via env, `ctx:status`, phase and next extraction, roster-drift context | `$.env.get` validated in TS (bad value reported by toast and context line, never defaulted); phase and next via task `plan:status --json`; roster drift inside `agent.spawn`; `ctx:status` stays a Python task for use outside sessions | n/a | n/a | n/a | Not `userConfig`: a value outside a field's bounds refuses the whole module load (M-TS, "options do not fit plugin.json userConfig"), which would switch every gate off |
| CT-32b verify enforcement (ledger:163) | The Stop, SubagentStop and Bash hooks above call task `verify:check` (CT-32a) | As each host hook | As each | As each | As each |
| CT-35 session start (ledger:166; D61, D93) | `classic.SessionStart` `{ sessionTitle, reloadSkills: true }` on startup, resume and fork (no queued `/rename`; `$.session` has no rename, S1); `classic.UserPromptSubmit` `{ sessionTitle }` at the first prompt after `/clear` (SessionStart ignores the title on clear, F1 item 2); `session.start` awaits `$.command.run({ command: 'reload-plugins', args: '--force' })` | `$.command.run` is "queued and run once the session is idle" and rejects "inside a hook the turn is waiting on" (T:3072-3079): whether the await completes before the first request, or deadlocks, is spike arm 5 | n/a | `session.start` does not fire after `/clear`; the clear path is `classic.SessionStart` with `source: 'clear'` | The dotfiles mod voids the reloads (`dotfiles/.claude/skills/session-start/hooks/register.ts:79-84, 231-234`) and runs a cold `uv run` with a 60 s timeout (`:28, 108-109`); lint `no-void` plus `typescript/no-floating-promises` (S4) stops the first, tasks stop the second |
| CT-36 WebFetch (ledger:167; D95) | `tool.call` `{ tool: 'WebFetch' }` answering `{ result }` in WebFetch's output shape from task `web:fetch` (`timeoutMs: 60000`); `{ deny }` on failure; `$.tool.check` first to keep permission rules, since answering without `next` skips them and every later PreToolUse hook (M-EV:305-312) | Answers before the fetch; no settings backstop (D95) | Yes | No effect | `.catch` denies |
| CT-02b follow-ups (ledger:133; KB-A:279-284 rows 1-6; DF-A 3.4 rows 1-3) | `tool.call` on Bash, Edit, Write, NotebookEdit, AskUserQuestion, EnterWorktree; lane paths read `e.agentId` (KB-A CT-31 row 5) | Deny before `next` | Yes | No effect | `.catch` denies |
| CT-19 parts (ledger:150; DF-A 3.5): SubagentStart constants, SubagentStop journal | `agent.spawn` prompt rewrite; `classic.SubagentStop` observe plus a task | n/a | Yes | n/a | Observe hooks pass on failure |
| CT-61 InstructionsLoaded (ledger:192) | `classic.InstructionsLoaded` observe plus task `guidance:record` | n/a | n/a | n/a | Pass |
| CT-37 context trigger | `session.measure` (DF-A 3.3) | n/a | Main | Re-arm per session id | Pass |

### 1.3 Gaps: what "delete hooks" cannot achieve

- G1. Untrusted headless runs. A project `@skills-dir` plugin is "Not used" in a `claude -p` or SDK run in a folder
  never trusted, while settings hooks are "Used" there (PERM:743-751; LD:79: "running with `-p` isn't enough").
  CI, containers, fresh clones and the OCI acceptance run lose every gate. Trust is keyed on the repository root and
  a worktree uses the main checkout's (PERM:720-724), so lane worktrees of a trusted MP checkout are covered.
- G2. Subdirectory starts. A repository `.claude/skills/` plugin "doesn't load" when the session starts in a
  subdirectory (LD:75); the Desktop app in a worktree loads the main checkout's copy (LD:76).
- G3. One failure domain. A module load error, a hooks-worker crash traced to the mod, three worker crashes ("every
  mod that isn't built in" unloaded for the session, M-TS:140-162), Anthropic's remote rollout switch (M-TS:29, 62),
  or a same-named plugin (M-TS:67) switch every gate off at once. Outside a hot-reloading session the reason reaches
  only the debug log (M-TS:15-19). Settings hooks fail one script at a time.
- G4. Managed settings or a Team or Enterprise sign-in seat `sec-default` outermost, and its `classic.*` row makes
  those events "continue past the user tier" (upstream `mods/sec-default/README.md`, rows table), so a user mod's
  `classic.Stop`, `classic.SubagentStop`, `classic.SessionStart`, `classic.UserPromptSubmit` and
  `classic.InstructionsLoaded` hooks, and `session.compact`, never run; validate says so (S2). `tool.call`,
  `prompt.submit` and `agent.spawn` for core and user agents still pass. Not active on this host today.
- G5. Git hooks. hk `pre-merge-commit` and `pre-push` (`hk.pkl:9-20`) run `dev/hooks/git_gate.py` through
  `retro:gate-merge` and `retro:gate-push` (`mise.dev.toml:330-338`). No mod event exists for Git, and a mod's own
  `git` runs "with repo hooks off" (T:3512). These stay; they are also the only gate for Codex and humans.
- G6. Fail-closed is bounded: a `.catch` that throws or passes 1 s fails open (M-EV:340).
- G7. anthropics/claude-code#92533 (open): any `tool.call` hook on Bash makes every Bash call of an
  `Agent(isolation: "worktree")` subagent refuse ("isolation context ... was lost"), even a passthrough. MP lanes use
  `git worktree add`, not `isolation: "worktree"`, so today's lanes are unaffected; any future isolation use is not.
- G8. No mod answer replaces a PreToolUse `ask` at `agent.spawn` (only `deny` or a model), and no `$` method renames a
  session; both have the workarounds in 1.2.
- G9. `$.process.run` children run outside the Bash sandbox and are not governed by Bash deny rules (M-OV:79; Y2
  section 3).
- G10. The `aggregated-research` plugin's SessionStart hook (`plugins/aggregated-research/hooks/hooks.json`) is a
  frozen baseline file and a consumer-facing product hook (`evidence/onboarding/baseline-files.json`); migrating it
  changes the published plugin and needs CT-08 (decision 2 below).

## 2. Library design

### 2.1 Location and loading

Choice: the plugin Claude Code loads is `.claude/skills/workflow-mods/` (`workflow-mods@skills-dir`), and the
TypeScript project that checks it is `mods/` at the repository root. There is no build: Claude Code "loads `.js` and
`.ts` files directly" and needs no Node.js, bundler or build step (M-CR:12), so the plugin folder is the source.

Trade-off (DF-A 3.0 decision 3, confirmed by LD):
- Skills-dir plugin: discovered in place, never copied (LD:188), watched with hot reload (PA line 72), loads in
  every interactive session started at the repo root after trust (LD:53, 69), not listed in
  `.claude-plugin/marketplace.json`, so consumers never receive a mod that calls `./dev/mise`. Costs: G1, G2,
  CT-38a's skills-tree exception (DF-A 3.6), and a mirror-rule exemption (no `.agents/skills` twin).
- `plugins/workflow-mods/` plus a marketplace entry (Y2 section 4, CT-31's current owned path): publishes to
  consumers, runs the installed copy cached by version, and a folder marketplace needs an absolute path (DF-A 3.0).
- `--plugin-dir` or `CLAUDE_CODE_PLUGIN_DIRS`: per launch or user env (`~/.claude/settings.json`), never a project
  setting (PA line 72). Kept as the route for MP's own scripted runs (G1).
- A symlink `.claude/skills/workflow-mods -> ../../mods/plugin` would keep all TS in one tree; whether skills-dir
  discovery follows it is unverified (spike arm 1). Default is the physical folder.

`.claude/settings.json` sets `enabledPlugins["workflow-mods@skills-dir"] = true` so intent is explicit (LD:53); the
doctor's `I.settings-plugin-undeclared-marketplace` detector (w0-doctor) must treat `skills-dir` as a reserved origin.

Layout:
```
.claude/skills/workflow-mods/           loaded by Claude Code; source = runtime
  .claude-plugin/plugin.json             name, version (SemVer), description, author
  hooks/hooks.json                       {"modules": ["./register.ts"]}
  hooks/register.ts                      export const register: Register; one line per feature
  hooks/features/<feature>.ts            stop-gates, bash-gate, doctor-context, prompt-context, agent-gate, ...
  hooks/lib/{host,task,guard,shell,budget,lanes,url}.ts
  tests/<feature>.test.ts                engine kit, run by `claude plugin test`
mods/                                    TypeScript project; nothing here loads in a session
  package.json, pnpm-lock.yaml, pnpm-workspace.yaml, .gitignore (node_modules/, coverage/)
  tsconfig.json, tsconfig.test.json, biome.json, .oxlintrc.json, vitest.config.ts
  types/claude-code/{claude-code.d.ts, PIN.json}
  scripts/{types-pin.ts, validate-report.ts}
  test/fake-host.ts, test/*.spec.ts, test/fixtures/
```
`node_modules/` is ignored by `mods/.gitignore`, never the frozen root `.gitignore` (one line, `mise-oci/`), so no
unit needs CT-08.

### 2.2 Runtime, package manager, pins

- The mods run in "an environment of its own, with no DOM and no Node" (T:18-19), so Node is tooling only.
- Node 26.11.1 in `mise.dev.toml` `[tools]` and `mise.dev.lock`: Active LTS from 2026-10-28 (Node release schedule);
  24.21.0 (Krypton, maintenance from 2026-10-20) is the fallback if a tool lags. Exact versions, no ranges.
- pnpm 12.11.2 from mise (no corepack), `packageManager` set in `mods/package.json`; `mods/pnpm-workspace.yaml`
  keeps `minimumReleaseAge` (default 1440 minutes since v11), sets `trustPolicy: no-downgrade` (v10.21), keeps
  `strictDepBuilds: true` (default) and an empty `allowBuilds` (v10.26): no dependency runs install scripts.
  Each pin is the newest version older than the release-age window when A2-1 runs.
- `claude` 2.1.299 pinned in `mise.dev.toml` (`aqua:anthropics/claude-code`, the mise registry's `claude`) for CI
  and the types pin; the host's auto-updated native CLI may run a newer version than the pin.
- `[deps.pnpm]` with `dir = "mods"`, `auto = false`, `run = "pnpm install --frozen-lockfile"`, mirroring MP's
  `[deps.uv]` (`mise.dev.toml`, deps section; mise deps "Provider options", `dir`). `dev/mise` reads only
  `mise.dev.toml` (`dev/mise:14`), so every `mods:*` task lives there.
- Bun 1.4.3 was considered (one binary for install, test and TS) and not chosen: the mods runtime is neither Bun nor
  Node, and the chosen linter and test runner are Node-first.

devDependencies only, zero runtime dependencies (versions current on 2026-10-14): `typescript` 7.0.2,
`vitest` 5.0.4, `@vitest/coverage-v8` 5.0.4, `oxlint` 1.88.0, `oxlint-tsgolint` 7.0.2004, `@biomejs/biome` 2.5.15,
`@types/node` matching Node 26 (test files only).

### 2.3 TypeScript config and module format

`mods/tsconfig.json` starts from upstream `mods/tsconfig.json` (target and lib `es2023`, `types: []`, `module:
esnext`, `moduleResolution: bundler`, `strict`, `noUncheckedIndexedAccess`, `noEmit`, `skipLibCheck`, `jsx: react`,
`jsxFactory: h`, `jsxFragmentFactory: Fragment`) and adds `exactOptionalPropertyTypes`, `verbatimModuleSyntax`,
`isolatedModules`, `noImplicitOverride`, `noFallthroughCasesInSwitch`. `include`: `types/**/*.d.ts` and
`../.claude/skills/workflow-mods/hooks/**/*`. `types: []` with an ES lib means a `node:` import fails type-check, the
loader rule "no Node builtins" (KB-A CT-31 row 3). `tsconfig.test.json` extends it for `test/**` with `@types/node`.
ES modules only (`"type": "module"`), extensionless relative imports as upstream `diff` does, no `import()` (a module
holding one does not load, PA line 14), and `export const register: Register` so tsc never accepts an untyped module
(KB-A CT-31 row 2). TS 7.0.2 reads T and checks in 0.09 s (S1).

### 2.4 Bundler: none

Nothing to bundle: runtime imports are relative plugin files and type-only `claude-code` (empty at run time, T:15),
and there are no runtime dependencies. If one is ever needed, it is vendored as one file under `hooks/vendor/` by
esbuild with a `mods:vendor --check` that rebuilds and compares bytes; that is a later decision, not built now.

### 2.5 Tests

- Unit tier, Vitest, no Claude: features take a narrow `Host` (a `Pick` of the `$` members they use: `process.run`,
  `fs.read`/`list`/`stat`, `session.cwd`/`root`/`usage`/`version`, `ui.status`/`toast`/`log`, `command.run`,
  `env.get`), the seam upstream's own `diff` mod uses (`mods/diff/hooks/host/host.ts`). `$` satisfies it
  structurally, so `register.ts` passes `$` with no cast. `mods/test/fake-host.ts` builds a typed fake whose members
  are `vi.fn<Host[...]>()` and throw "unstubbed <member>" by default, as the engine kit does for unanswered calls
  (upstream `mods/README.md`, Testing); `fake-host.spec.ts` asserts with `expectTypeOf` that the fake is a `Host` and
  that `Host` is assignable from the pinned `EngineInterface`, so a CLI bump that changes a used signature fails
  tsc. Vitest `include: ['test/**/*.spec.ts']` only (S5).
- Engine tier, `claude plugin test .claude/skills/workflow-mods`: `tests/*.test.ts` against the engine's own `$`,
  stubs via `on('process.run', ...)`, `$.classic.Stop(...)`, `$.tool.call(...)` (S3; PA line 81). This is the only
  proof of event wiring, `.catch` behaviour and answer shapes; it needs no session, sign-in or network (`plugins/mods/test.md`:7, 13).
- Coverage: `@vitest/coverage-v8` over `hooks/lib/**` and `hooks/features/**`, thresholds lines 90, statements 90,
  functions 90, branches 85; engine-tier runs are not counted (they run inside the CLI).
- Every JSON contract between a mod and a task has a committed schema (D83) and one fixture per enum value
  (DF-A CT-31a row 4), exercised by the Python tests and by Vitest.

### 2.6 Lint, format, type-check

- Lint: oxlint 1.88 `--type-aware` (tsgolint on typescript-go, 59 of 61 typescript-eslint type-aware rules, OX). S4
  shows it catches the dotfiles defect class; Biome 2.5.15's nursery rule did not. Rules at error:
  `typescript/no-floating-promises` (ignoreVoid false), `typescript/no-misused-promises`,
  `typescript/switch-exhaustiveness-check`, `no-void` (the dotfiles mod hides its reloads behind `void`),
  `no-restricted-imports` (bare specifiers other than `claude-code`, and `node:*`), `import/no-cycle`.
- Format: Biome 2.5.15, formatter only (`linter.enabled: false`), hk builtin `biome` step. oxfmt 0.73 is pre-1.0.
- Type-check: `tsc -p mods/tsconfig.json` and `-p mods/tsconfig.test.json`.
- `claude plugin validate --strict --json`: `mods/scripts/validate-report.ts` fails on any warning and on any
  `gatingHooks` entry without `.catch` (S2 lists them), so every gate has a fail-closed handler.

### 2.7 mise tasks (`mise.dev.toml`)

`mods:deps` (`mise deps install pnpm`), `mods:fmt` and `mods:fmt:check`, `mods:lint`, `mods:typecheck`, `mods:test`
(Vitest with coverage), `mods:test:engine` (`claude plugin test`), `mods:validate`, `mods:types:check`,
`mods:types:refresh` (explicit, writes), `mods:check` (every read-only check), `mods:ci` (`mods:deps` then
`mods:check` with JUnit and coverage reporters). Gate tasks the mods call: `gates:bash`, `doctor:session-start`
(w0-doctor), `ctx:thresholds`, `retro:gate`, `verify:check`, `session:name`, `web:fetch`, `guidance:record`,
`plan:status`. `./dev/mise run check` stays runtime-free apart from D89's `claude plugin validate --strict`;
`mods:check` runs in hk and CI (AGENTS.md, "do not install plugin runtimes just to lint").

### 2.8 hk steps (`hk.pkl`)

pre-commit: builtin `biome` on `mods/**` and `.claude/skills/workflow-mods/**`; a `mods` step `check =
"./dev/mise run mods:lint mods:typecheck"` on the same globs; builtins `actionlint` and `zizmor` on
`.github/workflows/*.yml`. pre-push: `./dev/mise run mods:test mods:test:engine mods:validate mods:types:check`.
`stash = "none"` as the existing hooks. hk 2.6.0 ships all four builtins (`hk builtins`).

### 2.9 GitHub Actions

New `.github/workflows/mods.yml` (not the baseline `acceptance.yml`, and not `development.yml`, which CT-26b
edits): `pull_request` with path filters (`mods/**`, `.claude/skills/workflow-mods/**`, `mise.dev.*`, `hk.pkl`, the
workflow) and `workflow_dispatch`; `permissions: contents: read`; `concurrency` cancel-in-progress per ref; one job
on `ubuntu-24.04`, `timeout-minutes: 10`; actions pinned by commit SHA with the tag in a comment (zizmor);
`actions/checkout` with `persist-credentials: false`; `jdx/mise-action` at CT-26a's pin; `actions/cache` for `.mise`
keyed on `mise.dev.lock` and for the pnpm store keyed on `mods/pnpm-lock.yaml`; `./dev/mise run mods:ci`;
`actions/upload-artifact` for JUnit and coverage `if: always()`. No matrix: the engine is platform-neutral JS and
the toolchain is one version; add macOS only if spike arm 8 shows a difference. No secrets.

### 2.10 Release and versioning

The plugin is not published, so there is nothing to deploy: it goes live when an integration lands in the main
checkout (hot reload, PA line 72). `plugin.json` `version` is the single version (SemVer from 0.1.0, as D89 sets for
`aggregated-research`); any change under `.claude/skills/workflow-mods/` needs a bump, checked by CT-57's rule
extended to this plugin. `mods/package.json` is `private: true` with no version. No release-please or changesets:
there is no consumer, and tags and pushes are outward actions that wait for instruction (AGENTS.md). The mod
reports its version and the running CLI's (`$.session.version()`, PA line 165) in its status line.

### 2.11 Built output against source

There is no built output, so nothing stale can be committed. `mods:validate` also fails when the plugin folder holds
anything but `.ts`, `.tsx`, `.json`, `.md` and `.gitignore`, a `node_modules`, or a `.js` file (a build artifact by
definition here). If spike arm 2 shows the engine lays `.claude-plugin/types/` beside a skills-dir plugin, a nested
`.claude/skills/workflow-mods/.gitignore` ignores it.

### 2.12 Types pinned to the CLI

`mods/types/claude-code/claude-code.d.ts` is vendored from the engine's own output for one CLI version, never
hand-edited (KB-A CT-31 row 1); `PIN.json` records `cli`, `sha256` and the source path. Sources in order: the
bundled `plugin-authoring/types/claude-code.d.ts` the CLI writes when the skill loads, or
`.claude-plugin/types/claude-code/index.d.ts` laid beside a watched mod (PA line 43); not upstream GitHub, which lags
(S6; dotfiles `.claude/types/README.md` measured the same). `mods:types:check` fails when `PIN.cli` differs from the
`claude` pin in `mise.dev.toml`, when the header's first line is not `// Written by Claude Code <cli>.`, or on a
sha256 mismatch; it warns when the host `claude --version` differs. At run time the mod compares
`$.session.version()` with the pinned version (a constant `hooks/lib/pin.ts` written by the refresh, since a mod
cannot import JSON) and shows a toast on drift. A bump changes the mise pin, runs `mods:types:refresh`, and commits
the d.ts, `PIN.json` and `pin.ts` together after `mods:check`. The header warns the API is "EARLY ACCESS" (T:4).

### 2.13 fnox

No secret is needed: `claude plugin test` needs no sign-in, CI uses the default read-only token, mods call no paid
API (`$.model.*` is not used by the gates). One optional secret: `WEBCLAW_API_KEY` for bot-protected pages (F1
item 8). If the user wants it, the `web:fetch` task (not the mod) runs `fnox --config ~/.config/fnox/config.toml
--profile <profile> --no-defaults --no-daemon --non-interactive exec -- webclaw ...`; no mod reads a secret through
`$.env`.

### 2.14 Python helpers from mods

`hooks/lib/task.ts` is the only door:
```ts
const r = await host.process.run(['./dev/mise', 'run', '-q', name, '--', ...args],
  { cwd: root, stdin: JSON.stringify(input), timeoutMs })   // argv, no shell (T:3500-3522)
```
- `root` from `$.session.root()`, or the classic event's `cwd` for SubagentStop; `timeoutMs` explicit per task
  (gates 10000, `doctor:session-start` 15000 per D22, `web:fetch` 60000, `session:name` 5000; 30 s default and 10
  min cap, T:8007-8026). Child time does not spend the 10 s hook budget (M-REF:283), but the user waits, so p95 is a
  receipt field (DF-A 3.4 row 4).
- Exit 0 with one JSON object on stdout, 2 refusal with a JSON reason, anything else is a failure routed to the
  `.catch` answer (`dev/AGENTS.md` exit-code rule). Stdout is parsed by a typed guard, never trusted as shaped.
- Tasks run Python with `-I` and never sync an environment in a gate path (`uv run --no-sync --offline` after CT-39;
  DFA-D5, KB-D21). Per-call cost is avoided by a TS prefilter: the Bash gate spawns only on a token hit.
- Environment (`PATH`, `MARKETPLACE_MISE_BIN`, `PLAN_ID`) reaching the child is spike arm 7; `PLAN_ID` is passed in
  `init.env` explicitly.

### 2.15 Rules every mod follows (checked)

Every gating hook has `.catch` answering the event's refusal when `next.called` is false (validate report);
classic Stop gates refuse once and pass on `stop_hook_active`; state that outlives a call is keyed by `session_id` and
cleared on `session.end` with `reason: 'clear'` (module variables survive `/clear`; `$.state` survives reloads, PA
line 118); every hook writes a status entry and `<feature> ERROR: <reason>` on failure (DF-A CT-31a row 3); no
`tool.call` hook on a tool it does not gate (KB-A CT-31 row 4).

## 3. Ticket breakdown

Units obey `docs/agents/codex-task-orchestration.md:204` (at most five maintained files, about 300 handwritten lines;
generated files marked "gen" are not counted). PL = `.claude/skills/workflow-mods/`. Every migration unit deletes
its settings entry and replaces the `dev/test_hooks.py` Settings inventory assertion (`:226-238`) in the same change;
the last of A2-7, A2-9 and A2-11 removes the `hooks` key and makes the test assert its absence.

| Id | Unit | Files | Lines | Blockers | Ticket | Deletes |
|---|---|---|---|---|---|---|
| A2-0 | Spike, live arms 1-10 (below) | `P/reviews/ccm-20261014/project-import/A2-0-spike-receipt.md`; throwaway mods in the scratchpad | 150 | fresh-session admission (interactive and `-p`) | CT-31a (DF-A CT-31a row 2) | none |
| A2-1 | Toolchain pins and package | `mise.dev.toml`, `mise.dev.lock` (gen), `mods/package.json`, `mods/pnpm-workspace.yaml`, `mods/.gitignore`; `mods/pnpm-lock.yaml` (gen) | 120 | CT-26a; A2-0 arm 1 | CT-31a | none |
| A2-2 | Type contract | `mods/tsconfig.json`, `mods/tsconfig.test.json`, `mods/types/claude-code/claude-code.d.ts` (gen), `mods/types/claude-code/PIN.json`, `mods/scripts/types-pin.ts` | 150 | A2-1; A2-0 arm 2 | CT-31a (KB-A CT-31 rows 1-2) | none |
| A2-3 | Lint, format, unit harness | `mods/biome.json`, `mods/.oxlintrc.json`, `mods/vitest.config.ts`, `mods/test/fake-host.ts`, `mods/test/fake-host.spec.ts` | 220 | A2-2 | CT-31a (KB-A CT-31 row 3) | none |
| A2-4 | Plugin skeleton | `PL/.claude-plugin/plugin.json`, `PL/hooks/hooks.json`, `PL/hooks/register.ts`, `PL/tests/register.test.ts`, `.claude/settings.json` (`enabledPlugins`) | 120 | A2-3; CT-38a; A2-0 arm 1 | CT-31a rows 1, 3 | none |
| A2-5 | Host seam, task runner, guards | `PL/hooks/lib/host.ts`, `PL/hooks/lib/task.ts`, `PL/hooks/lib/guard.ts`, `mods/test/task.spec.ts`, `mods/test/guard.spec.ts` | 290 | A2-4; A2-0 arm 7 | CT-31a rows 3-4 | none |
| A2-6 | hk, CI, validate report, guide | `hk.pkl`, `.github/workflows/mods.yml`, `mise.dev.toml` (`mods:ci`, `gates:bash` over the existing script), `mods/scripts/validate-report.ts`, `docs/agents/workflow-mods.md` | 260 | A2-5; CT-26a; CT-26b (`claude` in CI, D89); A2-0 arm 8 | CT-31a; CT-57 | none |
| A2-7 | Stop and SubagentStop gates | `PL/hooks/features/stop-gates.ts`, `PL/tests/stop-gates.test.ts`, `PL/hooks/register.ts`, `.claude/settings.json`, `dev/test_hooks.py` | 260 | A2-6; A2-0 arm 3 | CT-02b (D51 slice) | `dev/hooks/stop_gate.py`, `dev/hooks/subagent_stop_gate.py`, settings `Stop` and `SubagentStop` (`:54-77`), `StopHooks` tests (`dev/test_hooks.py:194-224`, replaced by engine tests) |
| A2-8 | Shell token parser and corpus | `PL/hooks/lib/shell.ts`, `mods/test/shell.spec.ts`, `mods/test/fixtures/bash-corpus.jsonl` | 280 | A2-5; the w0-session-hooks private-input admission (bounded, redacted extraction, `P/lanes/w0-session-hooks.json:93`) | CT-02b (corpus, token-anchored verbs, heredoc strip) | none |
| A2-9 | Bash gate mod | `PL/hooks/features/bash-gate.ts`, `PL/tests/bash-gate.test.ts`, `PL/hooks/register.ts`, `.claude/settings.json`, `dev/test_hooks.py` (PreToolUse class drives `gates:bash`) | 230 | A2-8; A2-0 arm 4 (decision 3) | CT-02, CT-02b | settings `PreToolUse` Bash (`:41-53`); D58's planned `if` field is moot |
| A2-10 | Retire `dev/hooks/` | `python/src/marketplace_dev/gates/bash.py` (moved), `.../gates/git.py` (moved), `mise.dev.toml` (`gates:bash`, `retro:gate-merge`, `retro:gate-push` repointed), `dev/test_hooks.py` | 120 | CT-39; A2-9 | CT-39 | `dev/hooks/pretooluse_gate.py`, `dev/hooks/git_gate.py` (moved; hk keeps working through the tasks) |
| A2-11 | Doctor context | `PL/hooks/features/doctor-context.ts`, `PL/tests/doctor-context.test.ts`, `PL/hooks/register.ts`, `.claude/settings.json`, `dev/test_hooks.py` | 150 | w0-doctor integrated; A2-6 | w0-doctor follow-up (D92) | settings `SessionStart` added by w0-doctor |
| A2-12 | Thresholds task | `dev/doctor/budget.py` (`--json`), `mise.dev.toml` (`ctx:thresholds`), `dev/test_doctor.py` | 60 | w0-doctor integrated | CT-23 (D97 seed) | none |
| A2-13 | Prompt context | `PL/hooks/features/prompt-context.ts`, `PL/hooks/lib/budget.ts`, `PL/tests/prompt-context.test.ts`, `mods/test/budget.spec.ts`, `PL/hooks/register.ts` | 260 | A2-12; A2-0 arm 9 (paste) | CT-23 (D97 seed) | planned `dev/hooks/prompt_hook.py`, `dev/context_budget.py` never created |
| A2-14 | Agent gate | `PL/hooks/features/agent-gate.ts`, `PL/tests/agent-gate.test.ts`, `mods/test/agent-gate.spec.ts`, `PL/hooks/register.ts` | 240 | A2-13; CT-19 order (ledger:154) | CT-23 (D97 seed), CT-19 | planned `dev/hooks/agent_gate.py` never created |
| A2-15 | Bash rule follow-ups | `PL/hooks/lib/shell.ts`, `PL/hooks/features/bash-gate.ts`, `PL/hooks/features/stop-gates.ts` (two-gate compose), `mods/test/shell.spec.ts`, `PL/tests/bash-gate.test.ts` | 250 | A2-9 | CT-02b (no-commit deny, dry-run and time flags, deadline deny, `hooks:install` guard, compose test) | none |
| A2-16 | Protected writes, secret printing | `PL/hooks/features/protect.ts`, `PL/hooks/lib/paths.ts`, `mods/test/protect.spec.ts`, `PL/tests/protect.test.ts`, `PL/hooks/register.ts` | 290 | A2-8 | CT-02b (KB-A rows 1-3) | none |
| A2-17 | Destructive git, absent binaries, lane paths | `PL/hooks/features/git-safety.ts`, `PL/hooks/lib/lanes.ts`, `mods/test/git-safety.spec.ts`, `PL/tests/git-safety.test.ts`, `PL/hooks/register.ts` | 290 | A2-8; CT-19 (lane path overlap) | CT-02b (KB-A rows 4-6) | none |
| A2-18 | Tool rules | `PL/hooks/features/tool-rules.ts`, `mods/test/tool-rules.spec.ts`, `PL/tests/tool-rules.test.ts`, `PL/hooks/register.ts` | 220 | A2-8 | CT-02b (DF-A 3.4 rows 1-3: AskUserQuestion, wait loops, EnterWorktree) | none |
| A2-19 | CT-23 follow-ups | `PL/hooks/features/prompt-context.ts`, `PL/hooks/features/agent-gate.ts`, `PL/hooks/lib/budget.ts`, `mods/test/budget.spec.ts`, `PL/tests/prompt-context.test.ts` | 220 | A2-14; `plan:status` task (CT-23 Python part) | CT-23 | none |
| A2-20 | Verify enforcement | `PL/hooks/features/stop-gates.ts`, `PL/hooks/features/bash-gate.ts`, `PL/hooks/lib/verify.ts`, `PL/tests/stop-gates.test.ts`, `mods/test/verify.spec.ts` | 220 | CT-32a; A2-7; A2-15 | CT-32b | none (its planned `dev/hooks` edits never happen) |
| A2-21 | Stop-gate lane lifecycle | `PL/hooks/features/stop-gates.ts`, `PL/hooks/lib/lanes.ts`, `PL/tests/stop-gates.test.ts`, `mods/test/lanes.spec.ts` | 180 | CT-17 lane states; A2-20 | CT-17 (stop-gate part) | none |
| A2-22 | Name generator | `python/src/marketplace_dev/session/name.py`, its test, `mise.dev.toml` (`session:name`) | 200 | CT-39 | CT-35 (DF-A 3.1 row 3) | none |
| A2-23 | Session-start mod | `PL/hooks/features/session-start.ts`, `PL/tests/session-start.test.ts`, `mods/test/session-start.spec.ts`, `PL/hooks/register.ts` | 250 | A2-22; A2-0 arm 5 (decision 4) | CT-35 | D61's planned settings SessionStart for `/clear` never created |
| A2-24 | `web:fetch` task | `python/src/marketplace_dev/web_fetch.py`, its test, `mise.dev.toml` (task and webclaw pin) | 220 | CT-39 | CT-36 (W1) | none |
| A2-25 | WebFetch mod | `PL/hooks/features/web-fetch.ts`, `PL/hooks/lib/url.ts`, `mods/test/url.spec.ts`, `PL/tests/web-fetch.test.ts`, `PL/hooks/register.ts` | 280 | A2-24 | CT-36 | none (D95: no backstop) |
| A2-26 | Status band | feature, engine test, spec, `register.ts`, `PL/types/index.d.ts` (`$.state`) | 250 | w0-doctor; A2-6 | CT-31a (band) | none |
| A2-27 | Lane pane and `/lanes` | feature, engine test, spec, `register.ts` | 280 | A2-26 | CT-31b | none |
| A2-28 | Verify display | feature, engine test, `register.ts` | 150 | CT-32a; A2-26 | CT-31b | none |
| A2-29 | Grill dialog | feature, engine test, spec, `register.ts` | 200 | A2-6 | CT-31b (CT-13) | none |

30 units: 7 foundation (A2-0 to A2-6), 8 that migrate or replace hooks (A2-7 to A2-14), 15 that carry existing
tickets onto the library. Tickets that become mod tickets: CT-31 (A2-0 to A2-6 replace the `plugins/workflow-mods/`
home in its ledger row 161; A2-26 to A2-29), CT-02b (A2-7, A2-8, A2-9, A2-15 to A2-18), CT-23 (A2-12 to A2-14,
A2-19), CT-32b (A2-20), CT-17 stop-gate part (A2-21), CT-35 (A2-22, A2-23), CT-36 (A2-24, A2-25). CT-19, CT-37 and
CT-61 also land features on the library (rows in 1.2). Blockers named by the brief: CT-26a gates A2-1 and A2-6,
CT-26b gates A2-6, CT-38a gates A2-4, CT-39 gates A2-10, A2-22 and A2-24; CT-08 gates nothing here (nested
`.gitignore`), only decision 2.

A2-0 arms: (1) skills-dir load at the root, in a lane-worktree session, `-p` in the trusted checkout, `-p` in a
never-trusted clone, a subdirectory, a symlinked folder; (2) whether the engine lays types beside a skills-dir
plugin, and the 2.1.299 refresh route; (3) live `classic.Stop` and `classic.SubagentStop` `{ block }`, the reason
reaching the subagent, the 8-continuation cap; (4) #92533 with `tool.call`, `classic.PreToolUse` and `tool.check`
on Bash, each with an `isolation: "worktree"` subagent running `pwd`; (5) `session.start` awaiting
`reload-skills` and `reload-plugins --force` (completion before the first request, deadlock), `sessionTitle`
visible before the first request, the `/clear` title path, whether `classic.SessionStart` is awaited before the
first prompt; (6) `$.session.cwd()` against a subagent's Bash `cd`; (7) child environment and `./dev/mise` p50 and
p95; (8) `claude plugin test` on a clean Linux runner with no sign-in (rollout switch); (9) telling a paste from
typing for T-D1 (`prompt.submit` text has "pastes already expanded", T:9061; `prompt.edit` has a 50 ms budget,
M-REF:283); (10) whether a `--plugin-dir` hooks module loads under `--bare` (the `--bare` help lists `--plugin-dir`
as explicit context).

## 4. Risks and decisions

Decisions for the user (real forks only):
1. Gap classes beyond `--bare` and `--safe-mode` (G1, G2, G3, G4): accept them, with MP's own scripted runs passing
   `--plugin-dir .claude/skills/workflow-mods` and hk staying the Git-side gate? Recommended: yes.
2. Is the `aggregated-research` plugin's SessionStart hook (baseline, consumer-facing) inside "every settings hook MP
   owns"? Recommended: no; it is product surface and needs CT-08.
3. If spike arm 4 shows every Bash hook variant breaks worktree-isolated subagents (#92533 open): keep the Bash gates
   as mods and never use `isolation: "worktree"`, or keep this one gate as a settings hook (an exception to D92)?
   Recommended: mods plus a rule and a guard that denies `Agent` calls with `isolation: "worktree"` until the issue
   closes.
4. If spike arm 5 shows `/reload-plugins --force` cannot be awaited before the first request from a mod: queue it
   (it may land after the first prompt) or the user keeps typing it? Naming is unaffected: `sessionTitle` from
   `classic.SessionStart` is synchronous.

Risks:
- Early-access API churn (T:4) against an auto-updating host CLI: pinned types, pinned CI CLI, engine-tier tests,
  run-time version toast (2.12).
- One failure domain (G3): a broken mod merged into the main checkout hot-reloads and switches every gate off;
  pre-commit and pre-push run validate, lint and tsc, CI runs both test tiers.
- `$.process.run` latency on hot paths: prefilters, p95 receipts.
- Young tool versions (Vitest 5.0.4 published 2026-10-12) against `minimumReleaseAge`: pin the newest version
  outside the window at lock time.
- `claude plugin test` in unauthenticated CI is unproven (arm 8); fallback is local engine tests with CI on the
  unit tier only.
- Integration order: w0-doctor (`f1bbc8d`) was reviewed with a settings SessionStart entry. Recommended:
  integrate it as reviewed and let A2-11 delete the entry, rather than re-review a stripped lane.
- Parent hunks outside the units: `.claude/AGENTS.md` (settings keys list names `hooks`), `AGENTS.md` pointer to
  `docs/agents/workflow-mods.md`, CT-31's ledger owned paths.

Could not verify: a live mod `classic.Stop` block in a session (engine kit only); skills-dir loading in worktrees and
headless runs on this checkout; whether the engine lays types beside a skills-dir plugin; `$.session.cwd()`
semantics; the T line numbers on 2.1.299 (T is 2.1.296); every A2-0 arm.
