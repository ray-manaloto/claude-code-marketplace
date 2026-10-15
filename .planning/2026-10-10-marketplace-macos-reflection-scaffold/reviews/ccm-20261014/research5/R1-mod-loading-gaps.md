# R1: Mod loading gaps after MP deletes its settings hooks (research round 5, 2026-10-14)

Written by research agent R1 of session `ccm-20261014` (`ce9c0b3d`) for the user's Q68. Read-only
except this file. MP at `21af565`, branch `codex/marketplace-native-onboarding`. Installed CLI:
`claude --version` prints `2.1.299 (Claude Code)`. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.
S = `/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/research5/R1/`
(every fetched page, issue JSON and search result is kept there).

Citation keys. Docs were fetched on 2026-10-14 with `curl -sS -L https://code.claude.com/docs/en/<page>.md`
into `S/docs/<page>-raw.md`; `page.md:N` is line N of that copy. PERM = `permissions.md`, LD =
`plugins/loading.md`, MTS = `plugins/mods/troubleshoot.md`, MAD = `plugins/mods/admin.md`, MOV =
`plugins/mods/overview.md`, MREF = `plugins/mods/reference.md`, MCR = `plugins/mods/create.md`, MTEST =
`plugins/mods/test.md`, HL = `headless.md`, HK = `hooks.md`, CLI = `cli-reference.md`, ENV = `env-vars.md`,
PCR = `plugins/create.md`, ORG = `plugins/org.md`, ERR = `errors.md`, WT = `worktrees.md`, SET =
`settings.md`. CL = `CHANGELOG.md` of anthropics/claude-code fetched with `gh api -H 'Accept:
application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` (1,015,061 bytes, top
entry 2.1.299), cited as `CL <version>:<line>`. `#N` without a repository is anthropics/claude-code issue N.
A2 = `P/reviews/ccm-20261014/project-import/A2-typescript-mods-library.md`.

## Verdict

Recommendation for A2 section 4 decision 1: do not accept every gap. Keep three thin settings hooks,
the deny gates MP already has (PreToolUse Bash, Stop, SubagentStop in `.claude/settings.json:41-77`,
each `onFailure: "block"`), as an explicit exception to D92, and move every non-gating hook (SessionStart
doctor context, prompt context, the Agent gate's context line, WebFetch, the UI) to mods as D92 says.
Use `--plugin-dir .claude/skills/workflow-mods` (or an absolute `CLAUDE_CODE_PLUGIN_DIRS`) only for scripted
runs that want mod features, and keep hk as the Git gate. Where a mod later takes over richer Stop or
SubagentStop behaviour, use the stand-down pattern shipped by breferrari/obsidian-mind (section 6) so the
settings hook runs only when the mod did not. Confidence: medium-high.

Evidence that decides it:
1. The remote rollout switch is real, was observed serving off to users for at least ten days, and also
   turns off `--plugin-dir` and `CLAUDE_CODE_PLUGIN_DIRS` mods in `-p` runs: #99130 (opened 2026-10-03,
   still open) logs `hooks module tg-messenger@inline not loaded: hooks modules are turned off for installed
   plugins in this process: the rollout switch served off`, with reports through 2026-10-12 on 2.1.295.
   wasikarn/method-harness#323 saw it flip off in 1 of about 8 headless probe runs on 2.1.287 and found
   only `@builtin` plugins skip the gate. CL 2.1.299:27 confirms Anthropic now also unloads running mods
   between turns when switched off. Settings hooks are not behind this switch. `--plugin-dir` therefore
   cannot cover this gap, and it hits interactive sessions too.
2. The `classic.*` bridge that MP's Stop and SubagentStop gates would ride is not reliably delivered to
   modules: #96831 (open, 2.1.281) saw no `classic.*` event in `-p`; a 2026-10-08 comment there reports
   `-p` now delivers them on 2.1.294 but a `claude --bg` session delivers none while settings hooks fire;
   #100869 (open, 2026-10-09, 2.1.295) reports `classic.Stop` and `classic.PreToolUse` never reaching a
   `--plugin-dir` module in `-p` or interactive runs while settings hooks for the same events fired. No
   CHANGELOG entry through 2.1.299 fixes it. A2 itself lists "a live mod `classic.Stop` block in a session"
   as unverified (A2 line 419).
3. A settings hook can fail closed per hook (`onFailure: "block"`, HK.md:902-935, 2.1.295+); a mod that does
   not load is skipped and "the session continues" (MTS.md:9), and `.catch` only covers a hook that loaded
   (method-harness#323, Gates bullet). Anthropic's own comparison says pick a settings hook when "You want to
   block, allow, or log an event with a script you already have" (MOV.md:219), and "Settings hooks keep
   working ... Nothing about them is deprecated" (MAD.md:75). MP's gates are existing Python scripts.
4. MP-specific: `dev/hooks/pretooluse_gate.py:1-10` is the only gate on `delivery:publish`, because
   `dev/git_delivery.py:50,415` pushes with `--no-verify` and so skips hk pre-push. If that hook becomes a
   mod and the mod is off, nothing gates publishing a failing lane.
5. Every real project found that weighed this kept its shell or settings hooks: method-harness#323
   ("Deny gates ... stay shell. A mod is fail-open whenever modules are off"), HiQS-Labs/XYZ-forge#964
   ("guardrails that only block or allow are settings-hook work"), breferrari/obsidian-mind (settings hooks
   stay and stand down when the mod handled the event), lossless-claude/lcm PR #377 (command hooks stay and
   exit early while the module is loaded). None was found that enforces gates through mods alone, in CI or
   locally.

What would flip it to "accept the gaps": a live probe on 2.1.299 (an admitted operation, section 5) that
shows a skills-dir module's `classic.Stop` and `classic.SubagentStop` `{ block }` landing in interactive,
`-p` and `--bg` sessions, plus a supported local override for the rollout switch or the mods API leaving
early access. Until then the Stop gates would be off with no signal in exactly the cases above.

Two A2 claims are weaker than stated and change the cost side: G2 (subdirectory starts) applies to settings
hooks too (PERM.md:664), and G1's "OCI acceptance run" never ran MP's hooks (`ci/acceptance.sh:42,151` run
`claude -p` after `cd /tmp`). So keeping thin settings hooks buys coverage for G3, G4, the classic-delivery
bug, VS Code, Desktop and `delivery:publish`, not for G2.

## 1. A2 section 1.3 claims, checked

| Claim (A2 1.3) | Verdict | Evidence |
|---|---|---|
| G1. `claude -p` (or SDK) in a folder never trusted skips a project `@skills-dir` plugin but still runs settings hooks | Verified, with a scope correction | PERM.md:747-751 (row "Hooks in settings files" is "Used" under "`claude -p` or the SDK, folder never trusted"; row "a project `@skills-dir` plugin" is "Not used"); LD.md:77-79 ("Trusting a parent folder or running with `-p` isn't enough"); HL.md:41. anthropics/claude-code-action `src/github/operations/restore-config.ts` (commit 6a5f1d8, lines 231-241) restores `.claude/` from the base branch because "The CLI's non-interactive mode trusts cwd ... executing hooks (including SessionStart)". Correction: the gap is "never trusted", not "every `-p` run". In a folder with saved trust the row needs "this exact folder trusted" and is met (PERM.md:756; ORG.md:90 states the same rule for repository marketplaces in `-p`). MP is trusted on this host: `~/.claude.json` has `hasTrustDialogAccepted: true` for the MP root and its parent (read of those two keys only, 2026-10-14). `claude --help` (2.1.299) adds that a run whose stdout is not a TTY counts as non-interactive. MP has no CI job that runs `claude -p` in the checkout (`.github/workflows/*.yml` only run `claude --version`), and `ci/acceptance.sh:42,151` runs `claude -p` from `/tmp`, so A2's "the OCI acceptance run loses every gate" is wrong: it never had them. |
| G2. A session started in a subdirectory does not load the plugin | Verified for mods, but not a mods-only gap | LD.md:75 (skills-dir plugins are read from the primary working directory's `.claude/skills/` and parents are not searched; `/cd` on 2.1.246+). PERM.md:664: "Hooks and other `.claude/settings.json` keys load from the current working directory's `.claude/` folder with no parent-directory fallback"; only `.claude/settings.local.json` loads from the repository root. So today's settings hooks are also absent in a subdirectory start, and a thin settings hook in `.claude/settings.json` would not fix G2. Related: #87325 (closed stale 2026-09-20; collaborator bcherny confirmed on 2.1.234 that skills-dir plugins are "scanned before you answer" the first trust dialog and load only after `/reload-plugins` or a relaunch). |
| G3. A module load error, a hooks-worker crash or Anthropic's remote switch turns every mod gate off at once | Verified | MTS.md:9 (a failing module or hook is skipped and the session continues); MTS.md:85-89 (`hooks module did not load`); MTS.md:142 (installed mods share one worker; a crash traced to one mod unloads it); MTS.md:162 (three untraced crashes unload "every mod that isn't built in"); MTS.md:62-63 and MTS.md:29-30 (rollout switch, served off or saved off); #99130 and method-harness#323 above; CL 2.1.299:27. One module per plugin (method-harness#323: "a second `modules` entry is refused"), so all MP gates in one plugin share one load. Recent fixes show the window is still moving: CL 2.1.292:546 (tool calls during a worker restart answered without the plugins' permission hooks), CL 2.1.293:451 (`classic.*` hooks skipped during a worker restart), CL 2.1.295:336, CL 2.1.289:789 (installed mods not loading in the first session after an upgrade). |
| G4. Under managed settings or a Team/Enterprise sign-in, user mods' `classic.*` hooks are skipped | Verified | anthropics/claude-code `mods/sec-default/README.md` at 9b4f0d6 (2026-10-14), line 28: "`classic.*` / Continue past the user tier", and line 31 for `session.compact`; MAD.md:58-62 (the guard loads with managed settings or a Team or Enterprise sign-in); MREF.md:322. Wider than A2 says: managed `allowManagedModsOnly` refuses user mods entirely (MAD.md:24-31), `disableSideloadFlags` rejects `--plugin-dir` (MREF.md:319), and `allowManagedHooksOnly` blocks user settings hooks and mods alike (MREF.md:317). Not active here: no `/Library/Application Support/ClaudeCode/`, and A2 records `subscriptionType: max`. |
| G5. Git hooks have no mod event | Verified | The 2.1.296 declarations say a mod's git "runs with repo hooks off" (`/private/tmp/claude-501/bundled-skills/2.1.296/.../claude-code.d.ts:3512`); no Git event appears in the event lists of MREF or the sec-default rows. hk carries the Git gates (`hk.pkl:9-20`, `mise.dev.toml:330-338`). Gap A2 missed: `delivery:publish` pushes with `--no-verify` (`dev/git_delivery.py:50,415`), so hk pre-push never sees it; only the PreToolUse Bash gate covers it (`dev/hooks/pretooluse_gate.py:1-10`). |

## 2. Which sessions lose which gates

| Session | Settings hooks in `.claude/settings.json` (today) | Project skills-dir mod (`workflow-mods@skills-dir`) | `--plugin-dir` or `CLAUDE_CODE_PLUGIN_DIRS` mod |
|---|---|---|---|
| Interactive CLI at the repo root, trusted | Run | Load (LD.md:53, 77) | Load; inline wins over the same-named skills-dir copy (LD.md:367-369) |
| Interactive CLI in a lane worktree of trusted MP | Worktree's own settings | Worktree's own `.claude/skills/` copy (WT.md:237); trust keyed on the main checkout (PERM.md:722), with an open edge case when an ancestor folder was once declined (#97991, open) | Load |
| First interactive launch in a fresh clone | Run after the trust dialog | Scanned before the answer, load after `/reload-plugins` or relaunch (#87325, bcherny, 2.1.234; current state UNVERIFIED) | Load |
| Started in a subdirectory | Not loaded (PERM.md:664) | Not loaded (LD.md:75) | Load (user env or flag) |
| `claude -p` or SDK, folder never trusted (CI, containers, fresh clones) | Run (PERM.md:749, HL.md:41) | Not used (PERM.md:751) | Load (MCR.md:205-216, MTS.md:19, MOV.md:199) |
| `claude -p`, folder trusted | Run | Used (inferred from PERM.md:751, 756; not probed) | Load |
| `claude --bg` and agent view | Run; trust required or it exits (CLI.md:76, CL 2.1.281:1570) | Load, but `classic.*` reported never delivered to modules (#96831 comment, 2.1.294) | Same `classic.*` problem |
| `--bare` | Off (CLI.md:74) | Off (MTS.md:66) | Plugin loads (HL.md:59); whether its hooks module runs is UNVERIFIED (MTS.md:66 names "installed plugins that are not managed") |
| `--safe-mode`, `disableAllHooks` | Off (CLI.md:127; MOV.md:106) | Off | Off |
| Rollout switch served off | Run | Off | Off (#99130) |
| Module load error, untraced worker crashes | Run, one script at a time | Off for the session | Off for the session |
| Managed settings or Team/Enterprise sign-in | Run unless `allowManagedHooksOnly` | `classic.*` and `session.compact` hooks skipped; all refused under `allowManagedModsOnly` | Same, and rejected outright under `disableSideloadFlags` |
| VS Code extension | Run | Never loads project `@skills-dir` plugins (#100448, open, 2.1.292; #95791 on Windows) | Loads (#100448: the `@inline` origin works) |
| Desktop app Code tab | Main checkout's config in a worktree (WT.md:243) | Reported loaded but hooks never run (#101640, open, 2.1.295) | `CLAUDE_CODE_PLUGIN_DIRS` ignored in desktop sessions (#101640) |
| Codex, humans, plain Git | Never had Claude hooks | n/a | n/a; hk only |

## 3. Gaps A2 did not list

- N1. `classic.*` delivery to modules is unreliable across versions and session kinds: #96831, #100869 (both
  open, no maintainer reply), against tarakanof/Ember#253 (2026-10-04, 2.1.288) which saw `classic.PreToolUse`
  and `classic.PermissionRequest` reach a `-p` module. Conflicting reports mean a version-dependent bug; MP's
  Stop and SubagentStop gates depend on exactly this bridge. Separately, #92533 (comment by cstarlea,
  2026-10-02) saw a `classic.PreToolUse` `{ deny }` have no effect on 2.1.287.
- N2. VS Code extension never loads project skills-dir plugins (#100448, #95791).
- N3. Desktop Code tab: mods reported loaded but never run (#101640).
- N4. First launch in a new clone: plugin scanned before trust is answered (#87325).
- N5. Trust state can silently revert: #97888 (open, 2.1.283) reports `hasTrustDialogAccepted` flipping to
  `false` on actively used projects; CL 2.1.259:2772 fixed concurrent sessions reverting `~/.claude.json`, and
  CL 2.1.299:43 fixed trust "appearing lost" on Linux. A revert drops a skills-dir mod from `-p` runs silently,
  while settings hooks keep running.
- N6. `delivery:publish` bypasses hk (section 1, G5 row).
- N7. A mod's own failure paths that a settings hook does not have: #92533 (any `tool.call` hook on Bash, even
  a passthrough, refuses every Bash call of an `Agent(isolation: "worktree")` subagent; open since 2026-09-06,
  confirmed on 2.1.287 by several commenters); a hook that overruns 10 s is skipped and the call proceeds
  (#91870 comment by Spencer-Morley, 2026-09-08, 2.1.263; maintainer poteat's reply recommends `Promise.race`).
- Symmetric risk for thin settings hooks: "Settings files that fail validation are silently ignored" in `-p`
  (`claude --help`, 2.1.299), so a settings-file schema check (MP's `dev/check.py`) must stay.

## 4. What others do

### 4.1 Loading a plugin or mod in headless and CI runs

- `--plugin-dir` works with `-p`: the official tutorial runs `claude -p "/tally" --plugin-dir ./first-mod`
  (MCR.md:205-216); load failures and hooks-module refusals print to stderr in `-p` (MTS.md:19, 50-52); mods'
  hooks run in `claude -p` and the Agent SDK (MOV.md:199); CL 2.1.295:354 fixed type files written into a
  `--plugin-dir` folder "in `-p` and SDK sessions". Bare mode accepts `--plugin-dir` (HL.md:59).
- `CLAUDE_CODE_PLUGIN_DIRS` loads plugins "the way a `--plugin-dir` flag loads it", absolute or `~` paths only,
  2.1.280+ (ENV.md:358); project and local settings cannot set it, and managed settings can turn both routes
  off (PCR.md:225-227). The SDK `plugins` option gives the same `@inline` origin (LD.md:52).
- `--plugin-dir` is personal scope, so the trust restrictions on project plugins do not apply (LD.md:85).
- It does not escape the rollout switch (#99130 `@inline` line) or managed `disableSideloadFlags`.
- Real use in CI: RackulaLives/Rackula `.github/workflows/security-triage.yml` (commit 4a34879, lines 226-229)
  passes `claude_args: '--plugin-dir .github/claude-plugins/secure-coding ...'` to claude-code-action because
  "headless CI does not auto-install marketplace plugins ... so --plugin-dir loads it deterministically";
  akitaonrails/ai-memory `.github/workflows/plugins.yml` (e264d8e, lines 12, 122-127) fires a plugin's hooks
  in a credential-free `claude -p --plugin-dir`; daycry/custom-agents `.github/workflows/headless.yml`
  (54c3523, lines 100-140); MattHB1/claude-workspace `.github/workflows/tier2-load.yml` (614026f). Code search
  `"--plugin-dir" path:.github/workflows` reports 297 files (token match, not all exact).
- anthropics/claude-code-action has `plugins`, `plugin_marketplaces` and `claude_args` inputs (`action.yml`
  at 34968b5, lines 104, 160-167) and no trust write (code search `hasTrustDialogAccepted
  repo:anthropics/claude-code-action`: 0).

### 4.2 Granting workspace trust without the dialog

- Documented route: set `projects["<repository root>"].hasTrustDialogAccepted: true` in `~/.claude.json`
  (PERM.md:756; ERR.md:5225-5231 "In non-interactive mode with `-p` no dialog is shown. Set the
  `hasTrustDialogAccepted` entry"; ORG.md:90 for `-p` runs). SET.md:443 still calls `~/.claude.json` a file
  Claude Code "writes for itself; you don't need to edit it", and #79707 (open, 2026-07-21) asks for a
  supported `claude trust <dir>` command or env var and notes the write races concurrent sessions.
- No flag or environment variable exists: `claude --help` (2.1.299) has none, ENV.md has no trust variable,
  CL has no such entry, and the YoraiLevi gist (verified on 2.1.234) says "There is no CLI flag for this" and
  that `CLAUDE_CODE_SANDBOXED=1` moves the dialog gate only. CL 2.1.248:3019 fixed `claude agents` skipping the
  trust prompt when `CI` is set, so `CI` is not a trust switch. claudecodeguides.com's
  `CLAUDE_CODE_TRUST_WORKSPACE=1` and `claude --trust` appear in no doc, CLI help or changelog: refuted.
- Real projects write that trust entry, for example JacquesAttinger/Marshall PR #32 (merged 2026-10-12, merge 9ced6ab) adds
  `src/trust.ts` `ensureRepoTrusted(repoPath)`: real-path key, re-read before write, temp file plus rename,
  mode 0600, 9 tests. PR titles only (bodies not read): Capchase/agent-swarm#119 "seed workspace trust for every
  Claude session", qrafttech/remote-agent#3 "pre-trust the checkout". Code search counts
  `hasTrustDialogAccepted`: 51 workflow files, 3,616 TypeScript, 1,404 Python, 1,328 Shell.
- Caveat: trust also turns on the repository's `permissions.allow` rules and other gated rows (PERM.md:747-754),
  so writing it in CI widens more than the plugin.

### 4.3 Failing closed when a mod does not load

- Documented CI check: read `system/init` `plugins` and `plugin_errors` and fail when the plugin is missing
  (HL.md:262-271; ORG.md:115). This proves the plugin loaded, not that its hooks module did; a refused module
  prints `hooks module not loaded` to stderr in `-p` (MTS.md:50-52), and `claude plugin test` exits 1 with
  `hooks modules are turned off` when mods cannot load in that shell (MTEST.md:55), a cheap preflight for the
  rollout switch.
- daycry/custom-agents `headless.yml` (54c3523, lines 100-140) checks `plugins`, `plugin_errors` and a witness
  file the hook writes, and exits 1 when the plugin did not load; it notes the docs do not say whether a
  `--plugin-dir` plugin's hooks run under `--bare` and retries without it.
- In-session, a mod that never loads cannot deny anything. The projects that care keep a settings or command
  hook that runs when the mod is absent: obsidian-mind's stand-down token (section 6), lcm's env-var early exit
  (PR #377; its author lists env-var dedup as a risk), and method-harness's "Load-proof line, one per session"
  follow-up plus its rule "An env marker must never stand down a deny gate" because a cloned repo's settings
  `env` can set the same variable while modules are off.

### 4.4 Projects enforcing gates through mods in CI

None found. CI use of mods is `claude plugin validate` and `claude plugin test` (code search `"claude plugin
test" path:.github/workflows`: 362 files; examples breferrari/obsidian-mind `.github/workflows/mod.yml` at
8fabc05, hamzafer/claude-code-mods, galando/temper, sd0xdev/sd0x-harness). Gate-shaped mods exist
(Jvrd97/claude-done-gate, kapral18/dotfiles `checked-gate`, rbartoli/agent-usage-guard, found by code search
`"tool.call" "deny" "stop_hook_active" filename:register.ts`, 29 files), but no workflow was found that runs
an agent with such a mod as the enforcing gate. This is a negative from bounded searches, so UNVERIFIED as
absolute.

## 5. Recommendation detail for the fork

- Keep in `.claude/settings.json`, unchanged: PreToolUse Bash (`pretooluse_gate.py`), Stop (`stop_gate.py`),
  SubagentStop (`subagent_stop_gate.py`), each `onFailure: "block"`. These cover every session kind in section 2
  except subdirectory starts, `--bare`, `--safe-mode` and `disableAllHooks`, which no Claude hook covers.
- Do not add a `tool.call` hook on Bash to the mod while #92533 is open; the settings PreToolUse gate avoids it.
- Move to mods per D92: SessionStart doctor context, `prompt.submit` context, `agent.spawn` (with its `.catch`
  deny), WebFetch, CT-35 naming, observers. Their loss in the gap sessions costs context, not enforcement.
- If a mod adds Stop or SubagentStop behaviour, pass a stand-down field to `next` (obsidian-mind pattern) so
  the settings script exits only when the mod handled that event; never key stand-down on an env var.
- Scripted runs: pass `--plugin-dir` (or absolute `CLAUDE_CODE_PLUGIN_DIRS`) where mod features matter; for a
  CI agent run that must be gated, rely on the settings hooks and add the `system/init` plus witness check.
- Close the `delivery:publish` hole at the source as a ticket: have `dev/git_delivery.py publish` run
  `git_gate.py push` itself, so no Claude hook is needed for it.
- Record the exception against D92 and ADR 0007 as a user decision; it is not this report's to make.
- Probe before revisiting (admitted operation; this brief forbids `claude` session starts): a throwaway repo
  with a skills-dir mod answering `classic.Stop` and `classic.SubagentStop` `{ block }` and writing a witness on
  `session.start`, run interactive, `-p` trusted, `-p` untrusted with `--plugin-dir`, and `--bg` on 2.1.299,
  reading `~/.claude/debug/` lines.

## 6. Code examples found

- Stand-down fallback: breferrari/obsidian-mind
  `https://github.com/breferrari/obsidian-mind/blob/8fabc05e2800dc25bf4382a654c73178d9933d6e/.claude/skills/obsidian-mind/hooks/register.ts#L26-L30`
  ("the settings hook is passed `om_mod: "standdown"` and exits, but only on an event this hook actually
  handled ... if it fails the hook throws, Claude Code skips it, and the settings hook gets the original event")
  and `#L147-L177` (`classic.Stop` hook returning `next({ ...e, om_mod: "standdown" })`). README at 2cb2e01,
  lines 215-222: "Wherever the mod does not load, the hooks run exactly as before: ... older Claude Code, a
  session started in a vault subfolder ..., or a folder you have not trusted." Its `.claude/settings.json`
  keeps SessionStart and Stop command hooks.
- Command hooks kept with module dedup: lossless-claude/lcm PR #377 (merged 2026-09-08, merge c162f56).
- Keep/port decision table: wasikarn/method-harness#323 (2026-10-02 to 2026-10-04).
- Programmatic trust: JacquesAttinger/Marshall PR #32, `src/trust.ts` (last commit 5c63037).
- CI load check with witness: daycry/custom-agents `.github/workflows/headless.yml` at 54c3523, lines 100-140.
- `--plugin-dir` through claude-code-action: RackulaLives/Rackula `.github/workflows/security-triage.yml` at
  4a34879, lines 226-229.
- Why CI `-p` runs settings hooks: anthropics/claude-code-action `src/github/operations/restore-config.ts` at
  6a5f1d8, lines 20-35 (`SENSITIVE_PATHS`) and 231-262.
- `classic.*` tier rule: anthropics/claude-code `mods/sec-default/README.md` at 9b4f0d6, lines 1-28.

## 7. Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | webclaw docs | `webclaw -t 60 https://code.claude.com/docs/en/<page>.md -f markdown` x25 | 0 each | 25 pages | Partly; permissions came back short, so raw curl copies are cited |
| 1 | curl raw docs | `curl -sS -L https://code.claude.com/docs/en/<page>.md` x21 | 0 each | 21 pages | Yes, all line cites |
| 1 | Exa | `fx exa.sh <out> "<query>" 10` (curl POST api.exa.ai/search, key from env) x11 | 0, HTTP 200 each | 10 each | Yes: seeded #79707, #90220, #99130, #42363, claude-code-action#664, the gist, mod tutorials |
| 1 | Context7 | `fx ctx7 library "claude code"`; `fx ctx7 docs <id> "<query>"` x4 (`/websites/code_claude` x2, `/llmstxt/code_claude_llms_txt`, `/anthropics/claude-code`) | 0 each | 5 libraries; 4 snippet sets | Yes: ORG.md:90 trust rule, ERR text, PCR.md:225, sec-default rows |
| 1 | Firecrawl | `fx firecrawl search "<query>" --limit 5 --json` | 1 | HTTP 402 insufficient credits | No; recorded gap |
| 1 | webclaw fallback | `webclaw -t 60 <url> -f markdown`: YoraiLevi gist, claudecodeguides.com, changelogs.core-directive.com | 0 each | 3 pages | Gist yes; claudecodeguides refuted; core-directive not used (third-party) |
| 1 | Serper | `fx serper.sh <out> "<query>"` (POST google.serper.dev/search) x5 | 0, HTTP 200 each | 10 each | Yes: corroborated #79707, gist |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3 last30days.py --plan plan.json --emit md --quick --save-dir ""` | 0 | Reddit 3 off-topic; YouTube ScrapeCreators HTTP 402 | No |
| 1 | Last30Days | same, `--search reddit,hackernews,github,x`, 3-subquery plan | 0 | X 48, HN 13, GitHub 25; Reddit ScrapeCreators HTTP 402 x3 | Yes: Marshall#32, method-harness#323, Ember#253, XYZ-forge#964, #100736 |
| 2 | gh issue view | `gh issue view <n> --repo <r> --comments --json ...` x30 (26 claude-code, 4 others) | 0 each | bodies in `S/gh/issues` | Yes |
| 2 | gh pr view | Marshall#32, lcm#377 | 0, 0 | 2 | Yes |
| 2 | gh search issues | `gh search issues "<q>" --repo anthropics/claude-code` x27 | 0 each | 0 to 15 | Yes: #100869, #96831, #100448, #101640, #97888, #97991, #87325 |
| 2 | gh search prs | `gh search prs "<q>"` x6 | 0 each | 0 to 12 | Yes: lcm#377, Marshall#32, trust PR titles |
| 2 | GraphQL discussions | `gh api graphql` search type DISCUSSION x6 | 0 each | 0 relevant; `repo:anthropics/claude-code mods` 0 | No |
| 2 | gh api search/code (global) | `gh api -X GET search/code -f q='<q>'` x14 | 0 x13, 1 x1 (HTTP 503 "too many shards failed" on `"om_mod" standdown`) | counts in section 4 | Yes |
| 2 | gh api contents | raw file reads, about 30 | 0 each | n/a | Yes, section 6 |
| 2 | CHANGELOG | `gh api -H 'Accept: application/vnd.github.raw' .../CHANGELOG.md` | 0 | 1,015,061 bytes | Yes |
| 2 | Saved searches (task) | `./dev/mise run research:collect` | not run | n/a | Writes a tracked path another lane owns |
| 2 | Saved searches (reproduced) | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=1,2` plus control | 0 each, one control 403 rate limit | see section 8 | Yes |
| 2 | Saved searches (issues) | `gh api -X GET search/issues -f q='<q> repo:anthropics/claude-code is:issue'` x4 plus control `mods ... is:issue` (269) | 0 each | 10, 17, 33, 189 | Yes |
| local | CLI facts | `claude --version`, `claude --help` (no session); python read of two `~/.claude.json` keys | 0 | n/a | Yes |

`fx` = `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --` (wrapper `S/bin/fx`); keys reached the commands through the environment only.

## 8. Proposed saved-search rows (not added; `dev/saved-searches.toml` untouched)

Reproduced read-only in the collector's shape (`dev/collect_saved_search.py:156-182`: `/search/code`,
`<query> repo:<repo>`, per_page 5, two pages, control query). Existing row `codex-hook-examples`
(`SessionStart filename:hooks.json`, openai/codex) returned 0 today while its control returned 159; worth a
look by the row's owner.

```toml
[[search]]
id = "cc-sec-default-classic"
query = "\"classic.*\" path:mods/sec-default"
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "cca-sensitive-paths"
query = "SENSITIVE_PATHS"
repo = "anthropics/claude-code-action"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "om-mod-standdown"
query = "standdown filename:register.ts"
repo = "breferrari/obsidian-mind"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

Results today: `cc-sec-default-classic` 2 (`mods/sec-default/README.md`, `mods/sec-default/hooks/register.ts`;
control 42); `cca-sensitive-paths` 2 (`restore-config.ts`, a test; control 11); `om-mod-standdown` 1 (control
49). Rejected: `ClassicEventName` in anthropics/claude-code (0; the 800 KB declarations file is likely outside
the code-search index, UNVERIFIED) and `"hooks module" filename:CHANGELOG.md` (0, same reason). Issue
watches the schema cannot express (the collector only calls `/search/code`): `"rollout switch"`,
`"classic." "hooks module"`, `"skills-dir" trust`, `hasTrustDialogAccepted`, each `repo:anthropics/claude-code
is:issue`.

## 9. Open gaps

- No live probe: the brief forbids `claude` session starts, so every session-matrix cell is from docs and third
  party reports. The decisive unknown is N1 on 2.1.299 (classic delivery in interactive, `-p`, `--bg`).
- `-p` in a trusted folder loading a skills-dir plugin is inferred from PERM.md:751 and 756, not observed.
- Whether a `--plugin-dir` hooks module runs under `--bare` (MTS.md:66 wording) is UNVERIFIED.
- #87325's scan-before-trust behaviour may be fixed after 2.1.234; current state UNVERIFIED.
- Docs say installed mods share one worker (MTS.md:142); a 2.1.261 measurement in #91870 (deafsquad) said each
  module has its own worker. Splitting gates across plugins would help load errors only; the switch and the
  three-crash rule still take all of them.
- Firecrawl quota (HTTP 402), ScrapeCreators quota (HTTP 402 for YouTube and Reddit backup), one code-search
  HTTP 503 and one rate-limit 403 stay gaps. SerpApi was not needed.
- Trust PR bodies for Capchase/agent-swarm#119 and qrafttech/remote-agent#3 were not read (titles only).
