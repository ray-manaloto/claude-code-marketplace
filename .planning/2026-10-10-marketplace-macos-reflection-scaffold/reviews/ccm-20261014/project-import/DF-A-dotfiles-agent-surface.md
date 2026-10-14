# DF-A: dotfiles Claude and Codex agent surface (project import, 2026-10-14)

Written by subagent DF-A of session `ccm-20261014` (`ce9c0b3d`), read-only. DF =
`/Users/rmanaloto/dev/github/ray-manaloto/dotfiles`, detached HEAD `7744a9c6` (2026-10-13). MP at
`21af565`. No DF script, task, hook or test ran: files were read with `sed`, `grep`, `wc`, `diff`,
`git log` and `python3 -I` on frontmatter only. Paths without a prefix are DF paths; `MP:` marks MP.

Engine facts come from three sources, each cited where used:
- T: the bundled plugin-authoring declarations for 2.1.296,
  `/private/tmp/claude-501/bundled-skills/2.1.296/<hash>/plugin-authoring/types/claude-code.d.ts`, and
  its `reference.md` (a temp path; the installed CLI is 2.1.299, so every T fact is re-checked by the
  CT-31a spike row below).
- H: the offline Claude Code docs snapshot in KB, `sources/agent-harness-docs/docs/claude-code/`
  (files dated 2026-09-15): `hooks.md`, `prompt-caching.md`, `plugins-reference.md`, `cli-reference.md`,
  `settings-reference.md`.
- F1: `P/reviews/ccm-20261014/grill-facts/F1-claude-code-mechanics-u2-u3.md`.

Sibling reports `A1-agent-dispatch-skills.md` and `KB-A-knowledge-base-agent-surface.md` landed while this
ran. Rows they already propose are not repeated here; section 3 names the overlaps and one conflict.

## 1. Inventory

### 1.1 Mods (function-hook plugins under `.claude/skills/<x>/`, each `<x>@skills-dir`)

| Mod | Files | Size | Last commit | What it does |
|---|---|---|---|---|
| session-start | `.claude/skills/session-start/{SKILL.md, .claude-plugin/plugin.json, hooks/hooks.json, hooks/register.ts}`; Python `python/src/dotfiles_setup/session_start.py`, `session_common.py`; task `mise.toml:1760-1764`; tests `tests/test_session_start.py` (510), `tests/test_session_start_hook.py` (44), `tests/fixtures/session_start_hook/harness.ts` (560) | register.ts 300, session_start.py 434, session_common.py 203, SKILL.md 56 | 2026-10-04 `2bd5f9ed` (Python), 2026-10-03 (mod) | On `session.start` asks Python once per session id, queues `/rename`, `/reload-skills`, `/reload-plugins --force` unawaited; defers naming to the first prompt with a Haiku slug on the default branch |
| coordinator-handoff | `.claude/skills/coordinator-handoff/{SKILL.md 119, .claude-plugin/, hooks/register.ts 317}`; `coordinator_handoff.py` 1358, `handoff_inbox.py` 428; spec `docs/specs/coordinator-auto-handoff-2026-10-02.md` 545 and `-requirements.md` 47 | 2,814 lines with the spec | 2026-10-05 `d6db6d2a` | `session.measure` hook: at 30% context (step 5%) auto-submits `/coordinator-handoff`, which runs `/session-handoff` unattended, ships a docs PR, launches a `claude --bg` successor and goes idle |
| install-doctor | `.claude/skills/install-doctor/{.claude-plugin/, hooks/register.ts 429}` (no SKILL.md); `install_doctor.py` 660; hand copy under `.agents/skills/install-doctor/` | 1,089 | 2026-10-04 `ee3b29da` | `classic.SessionStart` reports the `claude doctor` verdict; `classic.PreToolUse` denies tool calls while the install is invalid |
| plugin-health | `.claude/skills/plugin-health/{SKILL.md 73, .claude-plugin/, hooks/plugin-health.ts 94}`; `plugin_health.py` 476; generated `.claude/types/plugin-health.d.ts` | 643 | 2026-10-02 `b1bec698` | `classic.SessionStart` reports `enabledPlugins` declared versus `claude plugin list --json` effective |

### 1.2 Settings, hooks and launchers

- `.claude/settings.json` (218 lines, 2026-10-03 `53d18743`): `env` with 9 keys (`:4-14`), 7 permission allows
  and 33 denies (`:15-63`), hooks PreToolUse (`:70-81`), PostToolUse Edit/Write and Agent (`:82-103`),
  SessionStart `startup|resume` running `tool-currency-check` and `doctor` with a 600 s timeout
  (`:104-115`), InstructionsLoaded (`:116-126`), SubagentStart (`:127-137`); 24 `enabledPlugins` and 8
  `extraKnownMarketplaces`. `.claude/settings.local.json` (untracked) keys: `env`
  (`DOTFILES_COORDINATOR_HANDOFF_PCT`), `permissions`, `disabledMcpjsonServers`, `outputStyle`.
- `scripts/pretooluse-guard.sh` (42, 2026-10-03): fail-open shim with a fail-open log, venv interpreter
  first, `uv run` fallback (`:23-41`).
- Python hook modules: `hook_dispatch.py` 85 (one process per PreToolUse call), `hook_guard.py` 1189
  (2026-10-13, the mise-tasks-only deny table, wait-loop and secret-print patterns, zsh `=` separator,
  raw plugin removal, raw `codex exec`), `ask_quality.py` 228, `worktree_guard.py` 99, `branch_guard.py`
  293, `script_guard.py` 215, `environment_admission.py` 286, `heredoc.py` 107, `coordinator_write_guard.py`
  88, `graphify_hook.py` 187, `hook_selfcheck.py` 1012 (wired-hook end-to-end check plus the
  SubagentStart contract and PostToolUse/Agent reminder), `instructions_observer.py` 319 (2026-09-03),
  `mise_config_context.py` 219, `fnhook_gates.py` 686 (2026-10-11, `claude plugin validate` plus `tsc`).
- `.claude/types/` (13,336 lines, 2026-10-01): vendored `claude-code.d.ts` (13,186) refreshed by
  `schema-vendor-refresh` from GitHub raw at a pinned version.
- Codex: `.codex/hooks.json` (28, 2026-10-03) wires the same `pretooluse-guard.sh` for Codex with Claude
  tool names; `.codex/config.toml` (17, untracked) repeats 8 of the 9 Claude env keys and sets the handoff
  percent to 80 (`:14`); `.codex/agents/` 31 TOML files, 18 tracked, 13 gitignored Codex-app exports;
  `.agents/plugins/marketplace.json` (20, 2026-04-01) lists the Codex plugin
  `plugins/dotfiles-build-optimizer/` (7 skills, 6 scripts, 877 lines, 2026-08-08).

### 1.3 Skills, agents, rules, workflows

- Skills: `.claude/skills` 46 directories (45 SKILL.md, 6,122 lines; 7 exceed 200 lines: graphify 719,
  session-handoff 384, adversarial-review 296, research-sweep 268, mintlify 261, codex-sdlc-team 232,
  datamodel-code-generator 227). `.agents/skills` 48 (adds Codex-only `clear-prep` 250 and
  `codex-task-orchestration` 314); `diff -rq` shows 33 differing entries, all generated by
  `skills_mirror.py` rewrites (F3). No `.claude/commands/`: slash commands are skills; four set
  `disable-model-invocation` or `argument-hint` (session-start, handoff, resume, clear-prep,
  coordinator-handoff, session-resume). Skills cite `mise run` 235 times and bypass it in 41 lines
  (`uv run` 15, `python` 22, `curl` 17, `gh api` 9, `dotfiles-setup` 15, `firecrawl` 6, `claude -p` 1,
  `npx` 1; grep counts over `*/SKILL.md`).
- research-sweep: `.claude/skills/research-sweep/SKILL.md` 268 lines (2026-10-05) plus
  `.claude/workflows/research-sweep-run.js` 943 lines (2026-10-05 `2f4803b8`), backed by
  `research_fanout.py` 3,256 lines and `research_scope.py` 71 (Python owned by whichever report covers
  DF's research tooling).
- Other workflows: `gated-implementation.js` 151 (2026-09-12), `modernization-audit.js` 235 (2026-09-24),
  `graphify-refresh.js` 108 (2026-09-22).
- Agents: `.claude/agents` 25 files (2026-09-10 to 2026-10-02): 12 `codex-{sol,astra}-*` wrappers (178 to
  342 lines each, each pair differing in 14 to 20 lines), `adversarial-critic`, `claude-advisor` (Fable,
  xhigh), `claude-code-expert`, `cold-reviewer` (tools include Write and Edit), `dockerfile-reviewer`,
  `gate-runner` (haiku), `graphify-operator`, `graphify-researcher`, `issue-filer`, `premise-verifier`,
  `pwf-scribe`, `spec-scribe`, `staleness-auditor`; routing in `.claude/token-routing.md` (38).
- Rules: `.claude/rules` 28 files, 148,736 bytes; 26 load eagerly (no `paths:`), 2 path-scoped.
- Runtime state in the tree: `.agent/state/session-start/` holds 233 per-session JSON files with no
  pruning; `.claude/agent-memory-local/`, `.claude/scheduled_tasks.lock`,
  `.claude/ultrapowers-preferences.json`.

## 2. Defects (assume wrong; evidence)

Session-start mod
- DFA-D1. Late and forced reloads. `session.start` awaits `next(e)` first (`register.ts:277-278`), then
  queues `/reload-skills` and `/reload-plugins --force` without awaiting (`register.ts:79-84, 231-234`);
  `$.command.run` is "queued and run once the session is idle" and "rejects ... inside a hook the turn is
  waiting on" (T `claude-code.d.ts:3072-3081`). Python sets `reload: true` for every first-seen session id,
  `unknown` and `nonconforming` included (`session_start.py:294-300`). The spec accepted the cost: "the
  reason the reload is worth a prompt-cache invalidation at turn zero" (spec `:350-351`). H says plugin
  skills, commands, agents and hooks never invalidate the cache (`prompt-caching.md:126`) and a plain
  `/reload-plugins` refuses a reload that would re-read the whole prompt (`:148`): the invalidation the
  user saw comes from `--force`.
- DFA-D2. Late, model-made names. On the default branch the rename waits for the first `prompt.submit`,
  which also awaits `next(e)` before scheduling a Haiku completion (`register.ts:158-176, 288-299`); the
  rename is itself a queued command.
- DFA-D3. Undocumented identity sources. The current name is read from `~/.claude/jobs/<id8>/state.json`
  (spec P3, "undocumented, fail closed") or by walking the process tree and `shlex`-parsing the nearest
  `claude` argv (`session_start.py:140-178`). H documents the SessionStart input field `session_title`
  ("the current session title if one is already set, for example via `--name` or `/rename`",
  `hooks.md:1155`) and the output `sessionTitle` (`:1191`).
- DFA-D4. Fixed prefixes and zone. Conforming names need `dotfiles|kb` and a `.feature` suffix
  (`session_start.py:69-71`), so `ccm-` names are `nonconforming`; the zone is hard-coded
  `America/Chicago` (`session_common.py:29`), against D61's local time and its optional `.<unit>`.
- DFA-D5. Cold `uv run` console script at every session start: `uv run --project python dotfiles-setup
  session-start` with a 60 s timeout (`register.ts:28, 102-111`): implicit sync, no `-I`, and it bypasses
  its own task row (`mise.toml:1764`), against DF's skill-task-Python rule and MP's D60.
- DFA-D6. Error mislabelled. `read_state` raises `StateUnreadableError`, an `OSError` subclass
  (`session_common.py:51-56, 104-116`), which `decide` reports as `state-write-failed`
  (`session_start.py:290-293`).
- DFA-D7. Contract mirrored by comment. The action and reason enums are duplicated in TypeScript and
  Python with "Mirrors ..." comments only (`register.ts:37-41`; coordinator `register.ts:31-36`);
  plugin-health alone generates its types.
- DFA-D8. State never collected: 233 files in `.agent/state/session-start/`.
- DFA-D9. The Codex mirror documents a Claude-only mod and names a path that does not exist:
  `.agents/skills/session-start/SKILL.md:9` (`.agents/skills/session-start/hooks/register.ts`, F1 item 5);
  `.agents/skills/install-doctor/` carries a hand copy of a mod, which the spec itself calls legacy
  (spec section 4).

Coordinator auto-handoff
- DFA-D10. A Python process per turn above the limit (spec P8, `:336`, "~1 s per turn"; `register.ts:115-132`).
- DFA-D11. Unattended outward actions: the old session pushes and ships a docs PR (`SKILL.md:44-60`),
  launches `claude --bg` with `bgIsolation: none` (`:75-80`) whose write guard "fails open on a missing
  identity, a failed git probe and the topology cases" and does not cover Bash (`:77-80`), and the
  successor retires the old session with `claude stop`. MP admits none of these without an explicit
  instruction (MP `AGENTS.md`, Gotchas).
- DFA-D12. Three different handoff thresholds: default 30 (spec 3a), the untracked Codex config 80
  (`.codex/config.toml:14`), a per-user value in `settings.local.json`; no parity check.

Hooks and settings
- DFA-D13. SessionStart runs `tool-currency-check` and `doctor` with a 600 s timeout on every startup and
  resume (`settings.json:104-115`); "a prompt you send while SessionStart hooks are still running doesn't
  reach Claude until they finish" (H `hooks.md:1142`).
- DFA-D14. The PreToolUse guard fails open and logs it (`pretooluse-guard.sh:23-28, 39-41`); its fallback
  `uv run` can re-sync the venv inside a hook; it uses `-P` rather than `-I` (`:31-35`). PostToolUse,
  InstructionsLoaded and SubagentStart hooks run `uv run --project ... dotfiles-setup` with implicit sync
  (`settings.json:88, 98, 121, 132`).
- DFA-D15. `.codex/hooks.json` copies the Claude hook with Claude tool names into Codex (`:5`); whether
  Codex ever matches them is UNVERIFIED, and MP forbids the copy (MP `CLAUDE.md`, `AGENTS.md` Gotchas).
- DFA-D16. 148,736 bytes of rules, 26 of 28 eager, load into every session and every non-Explore subagent;
  the workflow measured 152,855 bytes per agent (`research-sweep-run.js:20-23`).
- DFA-D17. Vendored types drift: 13,186 lines vendored at 2.1.277 while 2.1.288 ran
  (`session-start/SKILL.md:55-56`); T says the engine lays version-matched declarations beside a watched
  mod folder (`reference.md:43`).

Agents
- DFA-D18. 12 `codex-sol-*`/`codex-astra-*` files differ only in the model pin (14 to 20 lines per pair),
  generated by `codex_lane_mirror.py` and policed by `codex_agent_parity.py`: a data difference stored as
  files.
- DFA-D19. A reviewer named "cold" can edit: `cold-reviewer.md` tools include Write and Edit and keep
  local memory; `adversarial-critic` disallows Edit but not Write.
- DFA-D20. Review isolation by request only: codex-sdlc-team review mode passes no `-s`, so "every lane
  runs under the machine's `danger-full-access` and `review` is asked (not prevented) not to write"
  (`codex-sdlc-team/SKILL.md:55-57`).

research-sweep
- DFA-D21. 268-line narrative skill with raw `gh api` (`:185`), `mise exec -- firecrawl scrape` (`:199`), a
  shallow clone into `$TMPDIR` (`:201-203`) and an absolute cross-repo corpus path
  (`~/dev/github/ray-manaloto/knowledge-base/...`, `:158`).
- DFA-D22. The workflow has no filesystem, so every mandatory number reaches it as a `PROBE-JSON` line an
  agent copied by hand (`research-sweep-run.js:83-97`): 11 to 17 agents (`:27`), each a transcription
  point, each carrying about 150 KB of eager rules.
- DFA-D23. Firecrawl first, webclaw only on credit exhaustion (`research-sweep-run.js:131, 185`), the
  opposite of MP's D62.

## 3. Features to import

### 3.0 Decisions this design asks of the user

These change the text of D61, D62 or Y2 and need the user's yes before any brief cites them:
1. Naming moves from the mod to settings hooks. H shows a settings SessionStart hook can read
   `session_title` and set `sessionTitle` on startup, resume and fork (`hooks.md:1155, 1191`), and the
   first prompt waits for it (`:1142`). After `/clear`, where `sessionTitle` is ignored, a settings
   UserPromptSubmit hook sets it at the first prompt (`:1380`). This works with mods off; the mod no
   longer renames.
2. No automatic `--force`. The mod runs `/reload-plugins` only when plugin files changed since they
   loaded; a held reload shows a band asking the user to type `/reload-plugins --force` (D61 asks for
   `--force` every time; H `prompt-caching.md:126, 148` shows that is the only cache risk).
3. The mods plugin lives at `MP:.claude/skills/workflow-mods/` as a `@skills-dir` plugin, not at
   `MP:plugins/workflow-mods/` (Y2, CT-31). A skills-dir plugin "is discovered in place rather than copied
   into the plugin cache", loads at the next session after workspace trust, and its hooks module is
   watched (H `plugins-reference.md:374-409`; T `reference.md:72`). The other carriers fail a need:
   listing it in `MP:.claude-plugin/marketplace.json` publishes to consumers a plugin whose modules call
   `./dev/mise`, which consumer repos lack; a `directory` marketplace needs an absolute path
   (H `settings-reference.md:4253`); `--plugin-dir` misses every session the user starts by hand.
   Conflict to reconcile: KB-A's CT-38 row 3 fails any plugin manifest inside a skill directory; this
   design needs one listed exception (row CT-38 below).
4. The WebFetch backstop names `./dev/mise run web:fetch -- '<url>'`, not `webclaw <url>` (D62 wrote the
   latter for a user-level hook in dotfiles; D87 moved it here, where skills call tasks, CT-38). D62's
   premise that the backstop covers `--bare` and `--safe-mode` is wrong: both turn settings hooks off
   (H `cli-reference.md:72, 124`); `--bare` has no WebFetch at all, `--safe-mode` keeps it unguarded.
   Only managed settings would cover safe mode, a global admission this design does not take.

### 3.1 Session start (owner CT-35; plugin home rows on CT-31a)

Improved design. A settings SessionStart hook does the naming and the skill re-scan; a settings
UserPromptSubmit hook finishes the `/clear` rename; the mod in `workflow-mods` only reloads plugins
when they are stale. One Python generator makes every name.

- Python (stdlib only, D60): `MP:python/src/marketplace_dev/session/name.py` (generator and conformance
  check) and `MP:python/src/marketplace_dev/hooks/session_start.py` (SessionStart and UserPromptSubmit
  handlers), reached through CT-02b's hook launcher; rows `session:start-hook` in `MP:mise.dev.toml`.
- Mod: `MP:.claude/skills/workflow-mods/hooks/session.ts`, imported by the plugin's single `register.ts`.
- Settings: `MP:.claude/settings.json` SessionStart (matcher `startup|resume|fork|clear`) and
  UserPromptSubmit entries.

CT-35 acceptance rows:
1. Naming: on `startup`, `resume` or `fork` the hook emits `sessionTitle` only when `session_title` is empty;
   a conforming title is kept; a nonconforming one is never renamed and gets one `systemMessage`; a fork
   whose title equals its parent's gets `<parent>.fork-<4 hex of the session id>`. No job record, process
   tree or argv is read (fixes DFA-D3).
2. `/clear`: the hook returns `reloadSkills: true` and records a pending title for the new session id;
   the UserPromptSubmit hook emits it once at the first prompt and is silent otherwise; `compact` does
   nothing.
3. Generator: `ccm-YYYYMMDDTHHMMSS.nnnnnnnnn<offset>` in local time from `time.time_ns()`, offset `+HH` or
   `-HH`, `+HHMM` when minutes are not zero, UTC as `+00`; optional `.<unit>` matching `[a-z0-9-]+`; one
   prefix, `ccm` (the D66 table's `dotfiles` and `kb` rows are dropped: the plugin is project-scoped and
   both repos are sunset, D87); golden vectors for CDT, CST, +0530, UTC and both DST edges; the hook,
   `MP:dev/handoff.py` (CT-29) and lane launchers (CT-17, CT-59) import it (fixes DFA-D4).
4. Mod: at its first `session.start` it records a fingerprint of the loaded plugin components (hooks
   modules, agents, `.mcp.json`, `.lsp.json` of the repo's plugins); on `session.end` with reason `clear`
   (T: no `session.start` follows a `/clear`, `claude-code.d.ts:11062-11064`), and at `session.start`
   for a claimed background spare, it queues `/reload-plugins` only when the fingerprint changed; never
   `--force`; a held reload sets the band text naming `/reload-plugins --force` (fixes DFA-D1).
5. The mod starts no process and calls no model at session start; hook state lives under
   `~/.local/state/ccm/session-start/`, one file per session id, deleted after 7 days by the hook itself
   (fixes DFA-D5, DFA-D8).
6. Tests: Python unit tests drive both hooks with one fixture payload per `source`; an end-to-end test
   runs the exact `command` strings from `MP:.claude/settings.json`; `claude plugin test` arms (T
   `reference.md:81`) prove an unchanged fingerprint queues nothing, a changed one queues one
   `/reload-plugins` without `--force`, and a held reload sets the band.
7. Live arm (admitted fresh-session operation): for a fresh start, a `/clear` and a resume, the title is
   visible before the first request and the first two requests' cache numbers (`/usage` "Prompt cache
   (main)", or the transcript `usage` fields under a transcript admission) show no invalidation the hooks
   or the mod caused; receipts under `MP:evidence/`.

CT-31a acceptance rows (the plugin home that CT-35, CT-36 and CT-37 share):
1. The plugin is `MP:.claude/skills/workflow-mods/` (`.claude-plugin/plugin.json` with `version` per D89,
   `hooks/hooks.json` naming one module) and is not listed in `MP:.claude-plugin/marketplace.json`;
   `docs/agents/workflow-mods.md` and CT-57's check follow the path (decision 3).
2. First step, a spike with control arms and receipts: the plugin loads in a session started at the repo
   root and in one started in a lane worktree; behaviour without workspace trust and from a subdirectory
   (H warns it then does not load, `plugins-reference.md:402`); whether the engine lays types beside a
   skills-dir plugin as it does for watched `--plugin-dir` folders (T `reference.md:43`; KB-A CT-31 row 1 covers the types task itself); whether a `session.start` hook that awaits
   `$.command.run` deadlocks (DF never awaits it, coordinator `register.ts:282`).
3. One hooks module `register.ts` imports one file per feature (session, web fetch, context, band); every
   hook writes a status entry on each event and `<feature> ERROR: <reason>` on failure, because a failed
   hook is skipped silently (T `claude-code.d.ts:3943-3948`; DF spec section 3d).
4. Every JSON contract between a mod and a task has a committed schema under the D83 rule and one test
   fixture per enum value; no enum is mirrored by comment (fixes DFA-D7).

### 3.2 webclaw over WebFetch (owner CT-36)

Improved design. A `tool.call` hook on `{ tool: "WebFetch" }` answers with `{ result }` instead of calling
`next`, so WebFetch never runs and the settings PreToolUse hooks beneath it do not fire (T
`claude-code.d.ts:3950-3962`; F1 item 7). When the mod is absent or fails, `next` runs, the settings
PreToolUse backstop denies, and the model reads the task to run. Files:
`MP:.claude/skills/workflow-mods/hooks/web-fetch.ts`,
`MP:python/src/marketplace_dev/hooks/webfetch_backstop.py`, the `web:fetch` row and module from W1
(`MP:python/src/marketplace_dev/web_fetch.py`).

CT-36 acceptance rows:
1. Guard shape: `on("tool.call", { tool: "WebFetch" }, ...).catch(...)` whose handler denies with
   "fetch with `./dev/mise run web:fetch -- '<url>'`" whenever the hook had not called `next`
   (T `reference.md:79`). The handler refuses a non-https URL, credentials in the URL, `localhost` and
   loopback, link-local and private literals, and URLs over 2,048 characters. Then
   `$.tool.check({ tool: "WebFetch", input })` gives the rules and mode verdict without running PreToolUse
   (T `claude-code.d.ts:3032-3042`): allow fetches, deny denies with its reason, ask denies with the
   `WebFetch(domain:<host>)` rule to add and the task to run instead.
2. Fetch and answer: `$.process.run(["./dev/mise", "run", "-q", "web:fetch", "--", url, "--format",
   "markdown"])` with a 60 s timeout. The answer has WebFetch's output shape `bytes, code, codeText,
   result, durationMs, url` (T `claude-code.d.ts:21376-21392`). `result` holds the whole page up to
   `inlineMaxChars`, a `userConfig` option whose default the spike sets. A longer page is written whole
   to the session scratch directory and named by sha256, with its head inline and the path; WebFetch's
   `offset` input (T `:16776-16783`) is served from that file without a refetch. The page is framed as
   untrusted data with a nonce (the CT-43 extract rule). `context` says WebFetch's `prompt` was not
   applied and quotes it. Nothing is written into the corpus (W1 contract).
3. Backstop: a settings PreToolUse entry, matcher `WebFetch`, returns `permissionDecision: "deny"` with a
   reason naming `./dev/mise run web:fetch -- '<url>'`. `docs/agents/workflow-mods.md` states what it
   covers: plugin not loaded, untrusted folder, a subdirectory start, a disabled plugin, a failed mod. It
   also states what it does not cover: `--safe-mode`, and `--bare`, which has no WebFetch (decision 4).
   No `permissions.deny` rule names WebFetch: a deny rule removes the tool, and the mod would never fire
   (F1 item 6).
4. Tests: `claude plugin test` with a stand-in `classic.PreToolUse` beneath the mod (T `reference.md:81`
   describes that ordering): a mod answer never reaches the stand-in, a throwing mod is denied by
   `.catch`, a `tool.check` deny and ask each produce their message. The backstop script is run through
   its exact settings command string. A spike arm records what the model reads for a 300 KB page
   returned inline, which sets `inlineMaxChars`. Overlap: KB-A CT-31 row 4 (the mod matches only
   WebFetch) stands.

### 3.3 Context trigger and handoff census (owners CT-37, CT-31b, CT-29b)

- CT-37 row: the measured context trigger reads `session.measure` (`e.context.percent`, pushed after each
  main turn; DF spec section 0 table, T event docs) inside `workflow-mods/hooks/context.ts`. It starts no
  process per turn (fixes DFA-D10). It fires once per threshold crossing per conversation and re-arms after
  `/clear`. The threshold is one env name with CT-23's validation (a number in (0, 100], a bad value
  reported, never silently defaulted; DF `register.ts:69-74`). The default action is a band entry and a
  toast naming `/session-handoff`; auto-submitting it is opt-in. The transcript-token computation already
  in CT-37 (5) stays as the mods-off fallback. It launches no successor, pushes nothing and stops no
  session (DFA-D11).
- CT-31b row: the band shows `ctx N%/T%` from the same handler and the session-start status of 3.1.
- CT-29b row: the handoff records a census of live heavy runs (pid, argv, log path, whether it holds
  `heavy-gate.lock`), and `session:handoff --check` fails while a live run is missing from it (DF
  requirements 11 and 15-16, `coordinator_handoff.py` `HEAVY_COMMAND_RE`).

### 3.4 Hook gates (owner CT-02b)

KB-A's six CT-02b rows (shell writes, one matcher, secret printing, destructive git, absent binaries,
lane paths) cover DF's secret-print patterns (`hook_guard.py:314-366`) too. Four DF features remain:
1. AskUserQuestion joins the matcher: a single-select question must lead with a `(Recommended)` option
   and no other option may claim it; the deny names the rule (`ask_quality.py`; MP's grill already
   answers in that shape).
2. Unbounded wait loops (`while`/`until` with `sleep` and no deadline) are denied with a redirect to a
   bounded-wait task; bounded loops pass (`hook_guard.py:185-293`).
3. EnterWorktree accepts only an existing `.claude/worktrees/<unit>` of the main checkout and denies
   anything it cannot verify (`worktree_guard.py`).
4. A test runs every `command` string in `MP:.claude/settings.json` verbatim against fixture payloads
   (`hook_selfcheck.py` drives the wired path, not the module), and the launcher's p95 latency is
   measured and recorded in the receipt (`hook_dispatch.py:4-9` measured 0.57 to 0.69 s of process
   starts per call before consolidation).

### 3.5 Briefs, subagents and verify (owners CT-19, CT-32a, CT-32b)

- CT-19 row 1: every brief has a finite answer set: an enumerated question list and a stop condition,
  never an open "what is broken" search (`adversarial-review/SKILL.md`: six inconclusive rounds, then
  one decisive round once the brief enumerated 3 questions over 32 cells). KB-A CT-19 row 1 owns the
  PREMISES slot and premise-verifier.
- CT-19 row 2: a SubagentStart hook gives built-in agent types that have no MP definition (general-purpose,
  Explore) the agent constants: where the report goes, written by Bash heredoc (D49), never editing
  shared plan files (`hook_selfcheck.py:711-731`).
- CT-32b row: a SubagentStop block must not displace the lane's report. The block reason tells the lane to
  end with its full receipt again, and a test asserts the final message still carries it. DF removed its
  SubagentStop hook because the forced turn "becomes the delegate's new final assistant message"
  (`hook_selfcheck.py:756-771`); MP keeps its gate (`MP:dev/hooks/subagent_stop_gate.py`), so it needs
  this guard.
- CT-32a row: the verify recipe drives the real surfaces (each hook through its settings command string,
  each task by name), and every probe writes a file whose rc is read back, never a piped tail
  (`verify/SKILL.md` recipe tables).

### 3.6 Skills tree, doctor and session review (owners CT-38, CT-22b, CT-20b, CT-59)

- CT-38 row: a skills-tree directory holding `.claude-plugin/` is allowed only when listed (today only
  `workflow-mods`), is Claude-only and has no `.agents/skills` twin. `skills:verify` also fails a mirrored
  SKILL.md that names a path present only under `.claude/` (DFA-D9). This amends KB-A's CT-38 row 3
  (decision 3).
- CT-22b row 1: plugin health: `enabledPlugins` declared against `claude plugin list --json` effective for
  this project, with a typed exit (`plugin_health.py`; the 2026-09-13 incident in `plugin-health/SKILL.md`).
- CT-22b row 2: a read-only report of the auto-memory index against its load budget (first 200 lines or
  25 KB) and of entries a trim would lose (`memory-index-curation/SKILL.md`).
- CT-20b row: automation candidates are ranked by the number of distinct sessions that ran a normalized
  command, not by repetition inside one session, beside a lane of manual-work passages from the plan and
  handoff; the judgement stays with the reviewing agent (`session-review/SKILL.md` "Read both automation
  lanes").
- CT-59 row: DF's codex-sdlc-team (five fixed specialists in `.codex/agents/codex-sdlc-*.toml`) is not
  imported as a team; each specialist is a role row dispatched through CT-59's protocol. The sol/astra
  model split is a field of the role row, not twin files (DFA-D18). A1 owns the sandbox rule (DFA-D20).

### 3.7 New tickets

| Id | Title | Size | Improved design | MP destination | Blockers | Admissions |
|---|---|---|---|---|---|---|
| DF-A-1 | GitHub dependency and code-search control stage for aggregated-research | M | DF's research-sweep stages as one operation in the spec #11 shape, results read from files, never retyped. (a) issues, discussions and releases searched for `repo` and every related repo in both directions, each source's outcome read from its manifest, not the fan-out's rc (DF #1473); a tracker the API reports disabled is a note. (b) repo existence and rename check (`repos/<r>`: 404 not found, 403 or 429 could not check, rename names the canonical repo). (c) code-search controls: one health query, a README-indexed check per repo, a planner must-hit with the same qualifier set as each zero it arms, a fresh known-absent; a 403 or 429 is rate-limited, never 0. (d) caller links fetched through `web:fetch` (D62, unlimited per D86) into the run's store and always read. (e) the run's `status` and full `statuses` list computed by Python from those files. Absence claims and misleading-by-omission judging go to KB-A-6's spine as rows; saved searches stay with `MP:dev/search_catalog.py` (stronger, W1 T14) | spec #11 operation beside `trackers` (#28 verb), committed schema (D83), fixtures under `MP:evidence/`; plugin skill text in `MP:plugins/aggregated-research/skills/aggregated-research/` | KB-A-1 or #28; #32-#34; CT-36 (`web:fetch`); the report that imports `research_fanout.py` | network and GitHub API quota (code search 10 requests a minute) for the live arm |
| DF-A-2 | Instruction-load observer and never-fired report | S | Settings `InstructionsLoaded` hook (stdlib only, CT-02b launcher) appends one JSONL row per load (file relative to the repo root, trigger, agent type) to `~/.local/state/ccm/instructions/<session-id>.jsonl`; `guidance:fired` reports eager files never needed and path-scoped rules that never fired over the last N sessions, feeding KB-A's CT-58 eager budget with runtime evidence (`instructions_observer.py`, DF #917) | `MP:python/src/marketplace_dev/hooks/instructions_loaded.py`, `MP:python/src/marketplace_dev/guidance/fired.py`, task rows, `MP:.claude/settings.json` | CT-39, CT-02b, CT-58 | none |
| DF-A-3 | Dotfiles agent-surface sunset | S | One dotfiles change per section 5 group, each only after its MP owner integrated and passed `/verify`; DF host-setup guards stay | dotfiles repository | every owner in section 5; CT-35, CT-36 | dotfiles writes and push (outward, explicit instruction) |

The research-sweep workflow script (`research-sweep-run.js`) is not imported as a script: once DF-A-1
computes every number from files, model nodes (triage, synthesis, refuters) belong to KB-A-6's plugin
agents, and running a Workflow needs the user's opt-in.

## 4. Not imported

- Mod renaming, the Haiku slug, the branch-slug `.feature` suffix and the `defer`, `unknown` and `pending`
  machinery (`register.ts:142-217`): D61 has no feature part, and the documented `session_title` and
  `sessionTitle` replace them.
- Job-record and process-argv identity reads (`session_start.py:140-178`, `session_common.py:72-96`):
  undocumented harness state.
- The coordinator's successor launch, docs-PR ship and push, `claude stop` retirement, ship queue and
  handoff inbox (`coordinator-handoff/SKILL.md`, `coordinator_handoff.py`, `handoff_inbox.py`): MP admits
  no unattended push, publish or fresh session; the census idea survives as the CT-29b row.
- install-doctor (claude install health with a PreToolUse deny): host setup, stays in DF.
- `.codex/hooks.json`: a Claude hook copied into Codex, which MP forbids.
- The 12 codex-sol/astra wrappers, `token-routing.md`, `claude-advisor`, `claude-code-expert` (the built-in
  claude-code-guide covers it), `gate-runner`, `pwf-scribe`, `spec-scribe`, `issue-filer`, the
  write-capable `cold-reviewer`: MP's reviewer, extractor, doc-writer and CT-59 cover the roles with
  enforced tools.
- `.claude/types/` vendored declarations (DFA-D17) and the `schema-vendor-refresh` route for them.
- Rule texts as written (148 KB): their substance is in the rows above and KB-A's; MP keeps path-scoped
  rules.
- Workflows `gated-implementation.js` (CT-59 and ticket-frontier cover it), `modernization-audit.js`
  (KB-A's CT-22b `tools:audit` row covers the native-first audit), `graphify-refresh.js` (CT-55 decides
  graphify).
- Skills: graphify, graphify-currency, graphify-fleet, blast-radius (CT-55); mcp2cli, mintlify (CT-41's
  `llms-txt` plan covers its fetch), find-docs, context7-cli (CT-44: Context7 only through a pinned task);
  five-stage-workflow (MP `AGENTS.md` already holds the route); handoff, resume, clear-prep (pushed
  cross-surface handoffs; CT-37 owns new terminals); codex-team-research, codex-task-orchestration (Codex
  Desktop, CT-59 and CT-10); research-with-verification-gap-fill (its verifier pass is KB-A-6's);
  token-check (CT-38's wiring table, F3); pr-workflow (A09 and CT-18); codex-schema and
  datamodel-code-generator (CT-52 under D83); plugin-inventory and plugin-removal (host plugin state,
  stays in DF); host setup skills chezmoi-check, devcontainer-sync, devcontainer-workflow,
  devcontainer-feature-schema-probe, lock-image, lock-shared, ssh-ignoreunknown-cross-platform,
  bake-action-set-precedence-expertise, pkl-import-hyphen-alias-expertise, pin-parity, lint-delta, reap,
  ci-warning-investigator, tool-currency-check, dockerfile-reviewer.
- `plugins/dotfiles-build-optimizer` and `.agents/plugins/marketplace.json`: a Codex plugin for DF's CI
  with `.omx` state, last touched 2026-08-08.
- Runtime state: `.agent/state/session-start/`, `.claude/agent-memory-local/`,
  `.claude/scheduled_tasks.lock`, `.claude/ultrapowers-preferences.json`.

## 5. Sunset checklist (dotfiles agent surface)

Each deletion is a dotfiles change under DF-A-3, made only after the named MP owner is integrated and its
`/verify` receipt exists. DF keeps what its host-setup work still uses.

1. After CT-35 and CT-31a: `.claude/skills/session-start/`, `.agents/skills/session-start/`,
   `session_start.py`, the session-start part of `session_common.py`, `mise.toml:1760-1764`,
   `tests/test_session_start.py`, `tests/test_session_start_hook.py`,
   `tests/fixtures/session_start_hook/`, `.agent/state/session-start/`.
2. After CT-37, CT-31b and CT-29b: `.claude/skills/coordinator-handoff/`,
   `.agents/skills/coordinator-handoff/`, `coordinator_handoff.py`, `handoff_inbox.py`,
   `coordinator_write_guard.py`, their tests and fixtures, the `coordinator-handoff` task, the
   `DOTFILES_COORDINATOR_HANDOFF_*` keys in `.claude/settings.local.json` and `.codex/config.toml`; the
   spec and requirements stay in Git history.
3. After CT-22b: `.claude/skills/plugin-health/` (mod and skill), `.agents/skills/plugin-health/`,
   `plugin_health.py`, `.claude/types/plugin-health.d.ts`, the plugin-health tasks; memory-index-curation
   once CT-22b row 2 lands.
4. After CT-02b and DF-A-2: `instructions_observer.py`, `hook_selfcheck.py`'s SubagentStart contract,
   `ask_quality.py`. Keep `scripts/pretooluse-guard.sh`, `hook_dispatch.py`, `hook_guard.py`,
   `branch_guard.py`, `worktree_guard.py` while DF hosts setup work, trimmed of rules that only served
   moved skills.
5. After CT-19, CT-32a, CT-32b, CT-20b, CT-59 and A1's sunset: skills verify, session-review,
   adversarial-review, codex-sdlc-team, codex-team-research, parallel-work-split, five-stage-workflow,
   research-with-verification-gap-fill and their `.agents` mirrors; `.claude/agents/` except
   `dockerfile-reviewer`; `.codex/agents/`; `.claude/token-routing.md`; `codex_lane.py`,
   `codex_lane_mirror.py`, `codex_agent_parity.py`, `codex_agent_validate.py`, `codex_verdict.py` (if A1's
   report does not claim them).
6. After DF-A-1 and the import of `research_fanout.py` (not in DF-A's scope): `research-sweep` (both trees),
   `.claude/workflows/research-sweep-run.js`, the `research-fanout` and `research-saved-search` tasks.
   This is also an MP blocker: `MP:AGENTS.md:57-60` runs `mise -C <dotfiles-checkout> run
   research-fanout` for strict hook receipts, and `MP:dev/toolchains/p2996_configure.py:19` imports DF's
   `host_lock.py` by absolute path. Both must move before DF's copies go; the parent should confirm a
   sibling report owns them.
7. Not tied to an import, delete with the first sunset change: `.claude/types/claude-code.d.ts` and its
   README, `.claude/workflows/{gated-implementation,modernization-audit,graphify-refresh}.js`,
   `.codex/hooks.json`, `.agents/skills/install-doctor/` (the hand copy),
   `plugins/dotfiles-build-optimizer/` and `.agents/plugins/marketplace.json` (confirm with the user, Codex
   returns 2026-10-19), `.agents/skills/{clear-prep,codex-task-orchestration}`, the `handoff` and `resume`
   skills.
8. Stays in DF (host setup): install-doctor, plugin-inventory, plugin-removal, the devcontainer, lock,
   chezmoi, ssh, bake, pkl, pin-parity, lint-delta, reap and tool-currency skills, `dockerfile-reviewer`,
   the SessionStart doctor (moved off the prompt path: DFA-D13 is DF's to fix), the permission denies in
   `.claude/settings.json:25-58`.

Counts: 3 new tickets (DF-A-1..DF-A-3) and 31 acceptance rows on 14 tickets or ticket parts: CT-35 (7), CT-31a (4),
CT-36 (4), CT-02b (4), CT-19 (2), CT-22b (2), CT-37 (1), CT-31b (1), CT-29b (1), CT-32a (1), CT-32b (1),
CT-38 (1), CT-20b (1), CT-59 (1); four decisions for the user (3.0).
