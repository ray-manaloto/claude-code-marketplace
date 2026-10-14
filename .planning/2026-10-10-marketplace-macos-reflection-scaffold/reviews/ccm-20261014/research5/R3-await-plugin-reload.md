# R3: Can a session-start mod finish plugin and skill reloads and the rename before the first request?

Research subagent R3 of session `ccm-20261014` (`ce9c0b3d`), 2026-10-14, for the user's Q71. Read-only
except this file; no `claude` session started, no GitHub write. Scratch:
`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/research5/R3/` (S below).
Installed CLI 2.1.299; newest type bundle on disk is 2.1.296 (T =
`/private/tmp/claude-501/bundled-skills/2.1.296/005e5f45c20a8437ea4b69f3330aba3b/plugin-authoring/types/claude-code.d.ts`,
PA = `reference.md` beside it). B = the 2.1.299 binary `~/.local/share/claude/versions/2.1.299`, read with
`strings -n 8` (offsets below are byte offsets in that output, S/bin-strings/strings.txt); its JavaScript is
minified, so names like `JYo` are build-local and every B claim is a reading of code, not an executed test.

## Verdict

Recommendation for the fork: **await in the mod**, with three changes to the A2 plan. Confidence: high that
the mechanism works on 2.1.299 (documented contract plus the engine code that implements it); medium until
spike arm 5 measures it live.

1. Plugins: in `session.start`, `await $.command.run({ command: 'reload-plugins' })` with **no `--force`**,
   interactive sessions only, gated on a staleness check, the rejection and a held answer surfaced by
   status and toast.
2. Skills and name: answer `classic.SessionStart` with `{ reloadSkills: true, sessionTitle }` instead of
   queuing `/reload-skills` and `/rename` (documented, applied before Claude's first response, no transcript
   echo).
3. Do not keep the dotfiles shape (`void $.command.run(...)`, `--force`): it can lose the race to the
   user's first prompt.

The evidence that decides it:
- The engine awaits the first `session.start` before the first prompt (T:4331-4334; PA:158-160; docs
  `plugins/mods/api` line 15: "Claude Code waits for that hook before the first prompt"), and Anthropic's own
  PR anthropics/claude-code#94594 (merged 2026-09-15) says "The engine holds the first prompt until
  `session.start` settles".
- `$.command.run` resolves after the command ran, with its output (T:3072-3081, T:1828-1843). Its refusal
  "inside a hook the turn is waiting on" does not cover `session.start`: in B the check fires only when the
  calling dispatch holds the turn (`"command.run":{check:...r.turnHeld...}`, offset 24513028), and the list of
  turn-holding events (`var zun=[...]` and `Gun`, offsets 24499436-24499602) has no `session.start` and
  exempts `classic.SessionStart`.
- B gives commands queued from `session.start` a pass: `lye` marks each `$.command.run` whose root event is
  `session.start` as a start input (offset 23829775), and the REPL queue processor `Ydt` (offset 46322717)
  runs a start input while `session.start` is in flight and holds every other input (the user's typed
  prompt) until it settles. So an awaited reload is designed to run, resolve, and only then let the first
  prompt through; no deadlock.
- Once `session.start` returns, that pass ends (`zK` is cleared, offset 38338579) and plugin commands queue
  at priority `later` (`OYe`, offset 23827736; `FU={now:0,next:1,later:2}`, offset 22143964), so an unawaited
  reload can run after a quickly typed prompt: the inversion reported in anthropics/claude-code#84320
  (2026-08-05, CC 2.1.222, closed as stale 2026-10-05).
- Before any response `--force` changes nothing: `/reload-plugins` holds only when `wouldInvalidateCache`,
  which B computes as `(MCP servers added or removed || LSP tool change) && !toolSearchEnabled &&
  totalOutputTokens > 0` (`Y5`, offset 35365394; `Jg` = `costLedger.totalOutputTokens()`, offset 12958041).
  A plain `/reload-plugins` therefore applies everything in a fresh session and refuses, with a warning,
  only when a real cached conversation would be re-read. Dropping `--force` keeps the "never invalidate"
  promise even when the reload lands late (resume, a slow start).

## Findings

### Q1. Does `$.command.run` return a promise that resolves after the command completes?

Yes.
- T:3072-3081: "Runs a slash command as if the person typed `/command args`: the event `command.run`, queued
  and run once the session is idle. ... Rejects an unknown name, and inside a hook the turn is waiting on.
  `const { text } = await $.command.run({ command: "status" })`". T:1828-1843: `CommandRunResult` is "what
  `next(e)` and `$.command.run` resolve to: the command's output text and the notes it leaves the model".
- B `JYo` (offset 23965631): checks the name, logs `$.command.run (<plugin>): N chars queued`, enqueues the
  text as a prompt-mode queue item with `priority: "later"` and `origin: {kind: "plugin"}`, and returns a
  waiter keyed by the item's uuid; `lxn` (offset 26496525) settles that waiter with the command's text and
  context after `n.run(e.args)` finishes.
- A held reload resolves, it does not reject: `/reload-plugins` returns its warning as text (B offset
  35385723 region, `if(f!==null)return ... {type:"text",value:f}`), so the mod must read `text`. The dotfiles
  cold review finding 13 makes the same point for `/rename`
  (https://github.com/ray-manaloto/dotfiles/blob/a52a3c3c389b6933ca0b8abc2a6645782c70f759/docs/research/kb/reports/agents/cold-review-coordinator-auto-handoff-df481e1f.md#L31).
- Other refusals in B: a plugin command after the person stopped the session and sent nothing since
  (`rye`, flag `tengu_plugin_input_refusal`); `/reload-plugins` from a plugin in a non-interactive session
  (`Ee`: allowed only when interactive or typed directly, offset 35387473; docs `plugins/cli-reference` line
  865). The dotfiles mod already skips `-p` (`register.ts:280`).

### Q2. Are `session.start` handlers awaited before the first request?

The first `session.start` is awaited before the first prompt; later ones (reloads) are not.
- T:4331-4336: "Fires once per process for each loaded plugin, before the first prompt, then once per fresh
  load of one (never `/clear`)... The first is awaited: a `$.tool.register` is listed by turn one. A later one
  runs its hooks alone". PA:158-160 and docs `plugins/mods/api` line 15 say the same; `api` line 198 shows the
  cost side ("Return without waiting for the timer, so the session starts right away").
- anthropics/claude-code#94594 (PR, 2026-09-15, Anthropic's `mods/diff`): its awaited `git status` in
  `session.start` made "every session's first turn" wait, so they moved it out. Evidence that the wait is real
  and that it costs first-prompt latency.
- B: the REPL raises it through `_raiseSessionStart(){hNr({...surface:"terminal",isInteractive:!0})}` (offset
  45158133); `hNr` (offset 38338579) creates the start-input set, runs `Po` (awaits
  `gre().session.start(...)`, offset 38335944) and clears the set when it settles. `Ki` (offset 30184389)
  answers a non-start input with "waits" while `B5()` (the start promise) is pending.
- The hook's 10 s budget does not count time inside a `$` call (docs `plugins/mods/reference` line 283;
  PA:154), so awaiting the reload does not trip it. No cap on how long the first prompt waits was found in
  the REPL path (`waitOut`, offset ~39030825 loops until the start settles): a hung reload would hold the
  first prompt (UNVERIFIED live; Esc behavior not traced).
- `session.start` does not fire after `/clear`, `/resume` or `/branch` (docs `plugins/mods/reference` line
  117; T:11063), while the classic event fires with `source: 'clear'` (hooks.md, SessionStart input).
- Settings and classic SessionStart hooks: "Claude's first response still waits for the hooks to finish ... a
  prompt you send while SessionStart hooks are still running doesn't reach Claude until they finish"
  (https://code.claude.com/docs/en/hooks, SessionStart section). That is why `sessionTitle` and
  `reloadSkills` from `classic.SessionStart` land before the first request.

### Q3. What does `/reload-plugins --force` do to the cache when run before any request?

Nothing: there is no cached prefix yet, and the flag only bypasses a check that is off at that point.
- Docs: the reload "warns and skips unless you pass `--force`" only when it "would change which MCP tools are
  loaded and invalidate the prompt cache" (`commands` line 127; `plugins/cli-reference` lines 847, 859;
  `prompt-caching` line 154). Plugin skills, commands, agents, hooks, monitors and themes "never" invalidate
  the cache; they are appended (`prompt-caching` line 135). With tool search deferring MCP tools, "Claude Code
  keeps the tool list from the conversation's first request for the whole conversation" (`prompt-caching`
  line 113).
- B `Y5` (offset 35365394): `wouldInvalidateCache:(k||a!==null)&&!p&&s` where `k` = plugin MCP servers added or
  removed, `a` = LSP tool change, `p` = tool search enabled for the model, `s = Jg() > 0`; `Jg` is imported
  from the chunk whose export list is the only one in B holding `ke, Jg, yM, Ly` and defines
  `function Jg(){return n().costLedger.totalOutputTokens()}` (offset 12958041; check in S/bin-strings). In the
  command (offset 35385723 region) `--force` only sets `f = null` instead of `Q(a, n)`, that is, it skips the
  hold; nothing else changes.
- Third-party bundle reading agrees: changelogs.core-directive.com entries for v2.1.163 ("If ToolSearch is
  active ... the warning is suppressed") and v2.1.268 (`hold_on_cache_impact`, `cache_impact` with
  `mcp_servers_added`, `mcp_servers_removed`, `lsp_tool_change`):
  https://changelogs.core-directive.com/v/2.1.163/e/reload-plugins-cache-impact-warning,
  https://changelogs.core-directive.com/v/2.1.268/e/reload-plugins-sdk-request-gains-a-hold-on-cache-impact-opti.
- anthropics/claude-code#93657 (open, 2026-09-11) asks for auto-reload "when the session has no user turns
  yet" because "there is no conversation history to re-read, so the cache cost of reloading is zero"; it
  also notes plugin auto-update lands up to ten minutes after start, so a reload at start cannot pick that up.
- Cost that does remain: the command's transcript lines (the dotfiles live run showed both reloads as "Prompt
  from the session-start plugin",
  https://github.com/ray-manaloto/dotfiles/blob/a52a3c3c389b6933ca0b8abc2a6645782c70f759/docs/research/kb/reports/agents/live-arms-coordinator-auto-handoff-2026-10-02.md#L12)
  open the first request; 2.1.299 `/reload-skills` "re-sends the full skill list to Claude" (CHANGELOG
  2.1.299, line 149 of the raw file). Appended content, not invalidation. Cross-session prefix sharing in the
  same directory (`prompt-caching`, "Cache scope") can miss if the reload changed the tool list; inference.
- Session title: titles are requests "outside that conversation" (`prompt-caching`, "Which TTL each request
  gets"); a `/rename` run as a command adds a "The user named this session" reminder to the conversation
  (ddaanet probe,
  https://github.com/ddaanet/handoff/blob/fcb716a7e44f2dcd71f28f014877fa7bf0c60b45/plans/2026-10-08-plugin-becomes-a-mod/reports/probe-autoname-rename.md#L34).
  Whether `sessionTitle` adds anything to the request: UNVERIFIED (nothing in `prompt-caching` lists it).

### Q4. Is there a settings or mod mechanism to reload plugins before the first request?

- Settings: no. SessionStart `reloadSkills: true` re-scans skill and command directories after the hooks
  complete (hooks.md, "Reload skills that a hook installs"; CHANGELOG 2.1.152); nothing reloads plugins.
  #93657 says a SessionStart hook "Doesn't help the current session" for plugin updates.
- Mods: `$.command.run({ command: 'reload-plugins' })` from `session.start` is the only route, and B treats it
  as a start input (Q2). `classic.SessionStart` can answer `reloadSkills` and `sessionTitle` (T:1366-1383 per
  A2; S1 spike type-checked it).
- Automatic paths that avoid a command: `--plugin-dir` folders apply adds and removes at once unless a full
  re-read would follow (`prompt-caching` line 152, 2.1.265); skills-dir and `--plugin-dir` hooks modules hot
  reload on save (PA:72-73); the SDK `reloadPlugins({ holdOnCacheImpact })` (core-directive 2.1.268 entry).
  None runs at session start for a stale pre-warmed worker.
- Why reload at start at all: a fresh process loads the current plugin set (`plugins/loading` line 34), so the
  reload only helps state that went stale after load, the dotfiles "bg spares can predate the claim" case
  (`dotfiles/.claude/skills/session-start/hooks/register.ts:9-10`; the agent view pre-warms a worker,
  CHANGELOG 2.1.238). Whether `session.start` fires at pre-warm or at claim: UNVERIFIED; if at pre-warm,
  neither await nor queue fixes the staleness.

### The dotfiles mod today

`register.ts:79-84` voids `$.command.run(...)`, `:231-234` queues `reload-skills` then `reload-plugins --force`
after a `uv run` decide of up to 60 s (`:28, 106-110`), and `:276-286` awaits `start()` inside
`session.start`, so the decide itself already holds the first prompt while the reloads are not awaited.
Because the calls are made during the hook they are start inputs only until the hook returns; the live run
passed (dotfiles live-arms L12) but the ordering is a race, not a guarantee. The 2.1.292 fix "a mod's
start-up prompt, command or subagent being queued a second time when the hooks worker was replaced"
(CHANGELOG line 542) and PA:162 ("awaited or not") show start-up commands are a supported pattern either way.

## Code examples found

None of the public examples awaits a reload inside `session.start`; most move `$.command.run` onto a timer
because of the "turn is waiting" refusal, which B shows does not apply to `session.start`.

| Repo, file | What it does | Permalink |
|---|---|---|
| ray-manaloto/dotfiles `.claude/skills/session-start/hooks/register.ts` | `void` queue of `reload-skills` and `reload-plugins --force` from `session.start` | https://github.com/ray-manaloto/dotfiles/blob/a52a3c3c389b6933ca0b8abc2a6645782c70f759/.claude/skills/session-start/hooks/register.ts#L79-L84 and #L231-L234 |
| ninthspace/claude-code-marketplace `plugin-sync/hooks/register.ts` | compares `installed_plugins.json` versions to the loaded set; plain `/reload-plugins` awaited from a 5 min clock and after `turn.complete` | https://github.com/ninthspace/claude-code-marketplace/blob/291494713f9bbda6f6692bbc98d4ce3993152c8c/plugin-sync/hooks/register.ts#L22-L61 |
| luisfmontes/rainforest-mind `hooks/plugins-em-dia.ts` | updates plugins, then plain `/reload-plugins` from a 1 s timer ("the host refuses `$.command.run` inside a `command.run` hook") | https://github.com/luisfmontes/rainforest-mind/blob/8942d54dcd838372b260738fefe814b2b39dbcc5/hooks/plugins-em-dia.ts#L163-L171 |
| ShiftinBits/constellation-claude `hooks/onboarding.ts` | `/reload-plugins` through `after(0)` | https://github.com/ShiftinBits/constellation-claude/blob/e6ebf0e0e6333c82ed50baa445864276324331cb/hooks/onboarding.ts#L346-L350 |
| SaM-runtime/claude-console `plugins/console-status/hooks/register.tsx` | `--force` reload on a timer plus a watchdog toast | https://github.com/SaM-runtime/claude-console/blob/e85268429ede4a03dba5daa92fd908d4f20e49ef/plugins/console-status/hooks/register.tsx#L1621-L1628 |
| HeyCubit/effortless `hooks/register.tsx` | `RELOAD_ARGS = '--force'` with the reason "a plain /reload-plugins holds back a change that would make the next message re-read the chat" | https://github.com/HeyCubit/effortless/blob/e553b18e9f5e8ce3533f3ce9c666e7e8bc9234f9/hooks/register.tsx#L2894-L2897 |
| SeongGwangJu/k-mods `mods/mod-store/hooks/register.ts` | awaited plain reload, toast on failure | https://github.com/SeongGwangJu/k-mods/blob/8edbff042ff1baca090f114146c9262542d58818/mods/mod-store/hooks/register.ts#L166-L173 |
| ayagmar/claude-modmgr `plugin/hooks/register.tsx` | reload port `(await $.command.run(...)).text`; times `session.start blocking` | https://github.com/ayagmar/claude-modmgr/blob/88051b0c979fe4601e6e421ecf82a6b28f7a87c6/plugin/hooks/register.tsx#L166 and #L289-L294 |
| Berkay2002/berkays-mods `plugins/identity-keeper/hooks/register.ts` | restores a name with `/rename` from `session.start` via `clock.after(0)`, falls back to `$.prompt.fill` | https://github.com/Berkay2002/berkays-mods/blob/c7eb68e086eec51970d0edc9efecf1038f6caba6/plugins/identity-keeper/hooks/register.ts#L60-L91 |
| PieroJF/claude-handoff-skill `mod/hooks/register.ts` | first `/rename` on a 250 ms timer | https://github.com/PieroJF/claude-handoff-skill/blob/6a41d6c2e5624d60960a8a57d78b02f847392ddb/mod/hooks/register.ts#L54-L55 |
| KilimcininKorOglu/claude-code-mods `plugins/self-command/README.md` | measured on 2.1.283: a timer-run `/reload-plugins` ran after the turn and kept the mod's state | https://github.com/KilimcininKorOglu/claude-code-mods/blob/887502f537951b55221ddb71154af2ff60c551a5/plugins/self-command/README.md#L21-L25 |
| ddaanet/handoff probe report | `$.command.run` from a `command.run` hook is refused awaited or not; rename from `turn.complete` works | https://github.com/ddaanet/handoff/blob/fcb716a7e44f2dcd71f28f014877fa7bf0c60b45/plans/2026-10-08-plugin-becomes-a-mod/reports/probe-autoname-rename.md#L25-L29 |
| anthropics/claude-code `mods/diff` PR #94594 | moved awaited work out of `session.start` because it held the first prompt | https://github.com/anthropics/claude-code/pull/94594 |
| issue #99169 (2026-10-03) | a mod sets `/color` with `$.command.run` at session start; the echo is "the first transcript line" of every session | https://github.com/anthropics/claude-code/issues/99169 |

## Sketch for the fork (A2-23 / CT-35)

```ts
on('classic.SessionStart', async ($, e, next) => {
  const r = await next(e)
  if (e.source === 'clear' || e.source === 'compact') return r   // sessionTitle is ignored on clear (#67389)
  return { ...r, reloadSkills: true, sessionTitle: await titleFor($, e) }
})
on('session.start', async ($, e, next) => {
  const r = await next(e)
  if (!e.isInteractive || !(await pluginsStale($))) return r      // skip the latency when nothing changed
  try {
    const { text = '' } = await $.command.run({ command: 'reload-plugins' })   // no --force
    if (text.includes('--force to apply')) $.ui.toast('plugin reload held to keep the prompt cache')
  } catch (err) {
    $.ui.status(`session-start ERROR: reload-plugins rejected`)
  }
  return r
}).catch(($, e, next) => next(e))
```

Spike arm 5 acceptance: (a) a fresh interactive session with a stale plugin on disk shows the reload output
before the first prompt's request (debug log order: `$.command.run ... queued`, reload summary, then the
first API request); (b) a prompt typed during start waits; (c) time from launch to the first request with and
without the reload; (d) `--resume` of a conversation with output tokens and a pending MCP change: plain reload
holds, `--force` would not; (e) the mod's own files changed: the reload re-fires `session.start` without
deadlock (PA:162 dedup); (f) `/clear` path keeps using `classic.SessionStart` and `classic.UserPromptSubmit`
`sessionTitle` (A2 section 1.2).

## Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Local types and reference | `grep`/`sed` on T and PA (2.1.296) | 0 | n/a | yes |
| 1 | webclaw docs | `webclaw -t 60 https://code.claude.com/docs/en/<page>.md -f markdown` for plugins/mods/{reference,events,overview,troubleshoot,api,create,admin}, plugins/cli-reference, plugins/loading, prompt-caching, commands, hooks, skills, plugins-reference, changelog, sessions | 0 x16 | n/a | yes (S/docs) |
| 1 | CHANGELOG | `gh api -H 'Accept: application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` | 0 | 1,015,061 bytes | yes |
| 1 | Exa | `fnox ... exec -- exa.sh` (curl POST api.exa.ai/search, key from env) x4 | 0, HTTP 200 x4 | 10 each | yes: core-directive, dev.to, #19491, #63028, #67389 |
| 1 | Firecrawl | `fnox ... exec -- firecrawl scrape <url> --format markdown` | 1 | "Insufficient credits" | gap |
| 1 | webclaw (Firecrawl fallback) | `webclaw -t 60 <url> -f markdown` x12 (core-directive x6, dev.to, mods.guide, modscode, claudemods.dev, firecrawl blog, agentpatterns) | 0 x12 | n/a | yes (core-directive) |
| 1 | Context7 | `fnox ... exec -- ctx7 library "claude code" ...`; `ctx7 docs /websites/code_claude ...`; `ctx7 docs /llmstxt/code_claude_llms_txt ...` | 0 x3 | 5 libraries; 2 docs pulls | corroborates only |
| 1 | Serper | `fnox ... exec -- serper.sh` (curl POST google.serper.dev/search) x3 | 0, HTTP 200 | 10, 10, 0 | nothing new |
| 1 | SerpApi | not run (Serper answered) | n/a | n/a | no |
| 1 | Last30Days | `python3 last30days.py --help`; run 1 `--plan` without `freshness_mode`; run 2 `SSL_CERT_FILE=/etc/ssl/cert.pem fnox ... exec -- python3 last30days.py <topic> --quick --plan plan.json --emit compact --save-dir "" --days 30` | 0, 2, 0 | Reddit 6, X 6, Web HTTP 422 | nothing relevant; web gap |
| 1b | Installed binary | `strings -n 8 ~/.local/share/claude/versions/2.1.299` + Python context reads (no execution) | 0 | n/a | yes, decisive |
| 2 | Upstream mods source | `git clone --depth 1 --filter=blob:none --sparse` anthropics/claude-code, `mods/` at `9b4f0d6` | 0 | n/a | yes |
| 2 | `gh search issues` CLI | `gh search issues <q> --repo anthropics/claude-code --include-prs` x22 | 0 | 0 for every hyphenated term (CLI quirk; REST control `reload-plugins` = 485) | replaced by REST |
| 2 | REST issue search | `gh api -X GET search/issues -f q='<q> repo:anthropics/claude-code'` x15 | 0 | 1 to 485 | yes: #84320, #93657, #94594, #99169, #100926 |
| 2 | Issue reads | `gh issue view N --comments`; REST `issues/N` and `issues/N/comments` (99169, 100926 printed 0 bytes via `gh issue view`) | 0 | 13 issues | yes |
| 2 | Discussions | `gh api graphql` search `type:DISCUSSION` x4; repo check | 0 | 38, 4, 0, 29; anthropics/claude-code has discussions disabled | nothing relevant |
| 2 | Code search | `gh api -X GET search/code -f q=<q> -F per_page=30` x20 in 2 rounds | 0, except 5 rate-limited and 2 HTTP 503 | e.g. `"$.command.run" "reload-plugins"` 199, `"command.run" "reload-plugins" "session.start"` 457, `"session.start" "reload-plugins" language:TypeScript` 74 | yes |
| 2 | Raw files | `gh api -H raw repos/<r>/contents/<p>?ref=<sha>` x20 | 0 | n/a | yes (S/code/files) |
| 2 | Saved-search route | read `dev/saved-searches.toml`, `dev/collect_saved_search.py`; reproduced `search/code` `q=<query> repo:anthropics/claude-code`, `per_page=5`, pages 1-2, control `README` | 0 x8, then rate-limited x4 | 21, 43, 1; control 42 | yes |
| local | dotfiles reports | `grep` in `dotfiles/docs/research/kb/reports/agents/` | 0 | 4 files | yes |

## Proposed saved-search rows (not added to `dev/saved-searches.toml`)

```toml
[[search]]
id = "cc-mods-command-run"
query = "\"command.run\""
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "cc-mods-session-start"
query = "\"session.start\""
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

Results on 2026-10-14: 21 and 43 hits (upstream `mods/diff`, `mods/telemetry`, `mods/sec-default`, `mods/README.md`);
control 42. A third row, `"reload-plugins"` in the same repo, returned 1 (`feed.xml`) and is not worth keeping.
The collector only speaks `search/code` (`collect_saved_search.py:179`), so issue watches such as
`"reload-plugins" SessionStart` (35) or `"command.run" "session.start"` (20) on `search/issues` need a schema
change first.

## Open gaps

- No live run (the brief forbids `claude` session starts): arm 5 must confirm Q2 end to end, measure the added
  first-prompt latency, and check `--resume` and the self-reload case. Every B claim is a static reading of
  minified 2.1.299 code; identifiers change per build and the API is early access (T:4).
- Types are 2.1.296 against a 2.1.299 CLI; T line numbers may shift.
- Whether the cost ledger's output tokens are restored on `--resume` (decides whether a plain reload holds
  there): UNVERIFIED.
- `waitsOnSessionStart` (the `Ydt` parameter) may exempt some typed inputs from waiting; not traced. Whether a
  `claude "<prompt>"` argument goes through the same wait: UNVERIFIED.
- Pre-warmed worker timing of `session.start` (pre-warm or claim): UNVERIFIED; it decides whether any start-time
  reload fixes the bg-spare case.
- Quotas: Firecrawl out of credits; Last30Days web HTTP 422; GitHub code search secondary rate limit hit twice
  (5 queries rerun, 4 saved-search pages lost); `filename:claude-code.d.ts` returned 0 (not indexed); SerpApi
  not exercised.
