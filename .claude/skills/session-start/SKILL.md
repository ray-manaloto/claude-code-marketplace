---
name: session-start
description: "Reference for the project session-start mod (CT-35): what it does at the start of each session, the status lines it can leave, and how to turn it off. It runs by itself; read this when a session started without its skills reloaded, without a ccm- title, or with a session-start status line."
disable-model-invocation: true
---

# session-start mod

A project skills-dir plugin (`session-start@skills-dir`, `defaultEnabled: true`) whose hooks
module is `hooks/register.ts`. It calls only the engine and the OS `date` command
(ADR 0008); it moves onto the mods library when CT-31a lands (D187).

| Event | Session | What it does |
| --- | --- | --- |
| `session.start` | interactive only | awaits a plain `/reload-plugins` (never `--force`, D103); the engine holds the first prompt until it settles |
| `classic.SessionStart` | `startup`, `clear` | returns `reloadSkills: true` |
| `classic.SessionStart` | `startup` without a title | also returns `sessionTitle` = `ccm-` + `date +%Y%m%dT%H%M%S.%N%z`, offset cut to the hour (`ccm-20261014T184849.575921000-05`, D61, D76) |

`claude -n <name>` wins: the title is set only when `session_title` is absent. On `/clear`
the engine ignores a title (#67389), so none is sent. `session.start` does not fire after
`/clear`, `/resume` or `/branch`.

## Status lines

- `session-start: /reload-plugins held: <the reload's line>`: the reload would change MCP or
  LSP tools and invalidate the prompt cache, so nothing reloaded. Start a new session, or type
  `/reload-plugins --force` if losing the cache is acceptable.
- `session-start ERROR: /reload-plugins rejected: <reason>`: the engine refused the command.
- `session-start ERROR: date exited <code>: <stderr>`: skills still reload; no title was set.

No status line after a start means the reload applied, or the hook did not run: check
`claude --debug` for a `session-start` line.

## Checks and rollback

- `claude plugin validate --strict .claude/skills/session-start`
- `claude plugin test .claude/skills/session-start` (mocked engine; no session, model or network)
- Turn it off: `claude plugin disable session-start@skills-dir`.
- Codex cannot run mods, so this skill has no `.agents/skills` copy.
