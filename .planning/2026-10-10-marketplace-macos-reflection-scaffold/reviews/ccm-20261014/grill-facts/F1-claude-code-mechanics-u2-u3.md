# F1: Claude Code mechanics for U2 (session-start mod) and U3 (webclaw instead of WebFetch)

Read-only fact report from a claude-code-guide subagent of session `ccm-20261014` (`ce9c0b3d`),
2026-10-14, for the Phase 4a grill. Verified on CLI 2.1.299; docs fetched live. "types" = the
bundled 2.1.296 declarations
`/private/tmp/claude-501/bundled-skills/2.1.296/005e5f45c20a8437ea4b69f3330aba3b/plugin-authoring/types/claude-code.d.ts`
(a temp path that will not survive a reboot). Read: dotfiles
`python/src/dotfiles_setup/session_start.py` and `.claude/skills/session-start/hooks/register.ts`.
No file edited. The harness flagged the subagent output for settings-shaped text; it is data.

## U2

1. Running built-in commands.
   - Settings hooks: no output field runs a slash command; handler types are command, http,
     mcp_tool, prompt and agent (hooks.md). Closest: SessionStart
     `hookSpecificOutput.reloadSkills: true` re-scans skill and command directories after the
     hooks finish (hooks.md; types:1319). Nothing equivalent reloads plugins.
   - Mods: `$.command.run({command, args})` runs a slash command (types:1784-1840). The dotfiles
     `register.ts:151, 232-233` uses it for `rename`, `reload-skills` and `reload-plugins --force`.
2. Naming.
   - `claude -n <name>` exists (`claude --help`); applied before the first request: UNVERIFIED.
   - SessionStart `sessionTitle` acts like `/rename`, only for source startup, resume or fork, not
     clear (hooks.md; types:1302).
   - `/clear` keeps a name set with `--name` or `/rename` (sessions.md); `/clear <name>` names the
     session being left (commands.md). A hook-set title surviving `/clear`: UNVERIFIED.
   - `$.session` has no rename method (mods reference).
3. Loading at start.
   - A fresh process loads plugins from `installed_plugins.json` and the cache; disk changes
     "don't reach this layer until you run /reload-plugins or start a new session"
     (plugins/loading.md).
   - SKILL.md edits in watched folders apply live; plugin hooks, agents and `.mcp.json` need
     `/reload-plugins`; `/reload-skills` covers a top-level skills folder created after start
     (skills.md). A reload at start is redundant unless state went stale after start (the
     bg-spare case in `register.ts:9-10`).
   - After `/clear`: re-reading plugins or skills is undocumented (UNVERIFIED). Mod
     `session.start` does not fire after `/clear` (mods reference, Session table); settings
     SessionStart does, with source `clear` (hooks.md).
4. Prompt cache.
   - Prefix order: system prompt and tool definitions, project context, conversation
     (prompt-caching.md).
   - `/reload-skills`: no documented invalidation; plugin skills, commands, agents and hooks
     "never invalidate the cache" (prompt-caching.md).
   - `/reload-plugins` refuses and warns when it would add or remove plugin MCP servers or the LSP
     tool; `--force` applies it anyway (plugins/cli-reference.md). The dotfiles hook always passes
     `--force` (`register.ts:233`): the documented cache risk.
   - Before the first request this session has no cache to break; other same-directory sessions
     can share the prefix (prompt-caching.md, "Cache scope"); inference.
   - SessionStart `additionalContext` enters the conversation at the hook point, not the system
     prompt (hooks.md).
   - Diagnose with `/usage`; its "Prompt cache (main)" line names a likely cause.
5. The dotfiles session-start hook.
   - Its SKILL.md points at `.agents/skills/session-start/hooks/register.ts`, which does not exist;
     the code is under `.claude/skills/`.
   - `session.start` (`register.ts:277`) calls Python `decide` once per session id; the state file
     is written before the answer (`session_start.py:271-300`). On `reload` it queues
     `reload-skills` then `reload-plugins --force` without awaiting (`register.ts:81-83, 231-233`).
   - Mod `session.start` fires "before the first prompt" (mods reference); whether the first
     request waits for the reloads: UNVERIFIED.
   - Naming: `keep` or `rename` at start, `defer` renames at the first `prompt.submit` with a Haiku
     slug (`register.ts:158-176, 288-297`). Conforming names need `dotfiles-` or `kb-` plus a
     Chicago timestamp (`session_start.py:69-71`); a `ccm-` name is `nonconforming`: never
     renamed, toast only.
   - It sets no system prompt or tools; `prompt.submit` returns `next(e)` unchanged. The likely
     cache risk is the forced plugin reload changing MCP or LSP tools (UNVERIFIED for the user's
     case).
   - No installed copy in `~/.claude/skills`, `installed_plugins.json` or `~/.claude/settings.json`;
     project or `--plugin-dir` loading: UNVERIFIED.

## U3

6. Deny WebFetch with a redirect message: yes. PreToolUse, matcher `WebFetch`,
   `permissionDecision: "deny"` with `permissionDecisionReason` (shown to Claude); exit 2 with
   stderr also works (hooks.md); allow rules do not override it (permissions.md). `"deny":
   ["WebFetch"]` removes the tool from context, so Claude gets no message; `WebFetch(domain:*)`
   keeps the tool and refuses each fetch (permissions.md). Scopes: user `~/.claude/settings.json`,
   project `.claude/settings.json`, local `.claude/settings.local.json`. Settings hooks run inside
   subagents (hooks.md); deny rules inside subagents: UNVERIFIED. PostToolUse `updatedToolOutput`
   replaces output after the fetch ran; WebFetch output shape is `bytes, code, codeText, result,
   durationMs, url` (types:21376).
7. A mod can do more: its `tool.call` for `WebFetch` can return `{ result }` without calling the
   tool, running webclaw via `$.process.run` (30 s default, 10 min max), and it sees subagent
   calls (mods events). Cost: skipping `next(e)` skips WebFetch domain rules and non-managed
   settings PreToolUse hooks, so the mod needs its own checks (inference). Only a mod can supply
   the result before the fetch; a hook can deny, or replace output after it. Mods are off under
   `--bare` and `--safe-mode`; managed `disableAllHooks` disables them too.
8. webclaw 0.6.23: subcommands `bench`, `extractors`, `vertical`, `search` (Serper.dev, own key),
   `help`. One page: `webclaw <URL>` (default `-f markdown`) to stdout; `--output-dir` writes a
   file. No length cap: `webclaw -t 60 https://code.claude.com/docs/en/skills.md -f markdown`
   returned 102,336 characters ending at the page's last link, empty stderr (WebFetch reported
   106,926 for the same page). Offline inputs `--file <html>`, `--stdin`, `--raw-html`; no response
   cache flag. Network needed for URLs; `-t` default 30 s; no key needed (`--api-key` or
   `WEBCLAW_API_KEY` optional for bot-protected or JS sites). Quote URLs containing `&`.
   Hook-free workaround: WebFetch input has `offset` (types:16776).
