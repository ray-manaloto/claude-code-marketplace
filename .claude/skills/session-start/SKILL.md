---
name: session-start
description: "Reference for the project session-start mod (CT-35): what it does at the start of each session, the status lines it can leave, and how to turn it off. It runs by itself; read this when a session started without its skills reloaded, without a ccm- title, or with a session-start status line."
disable-model-invocation: true
---

# session-start mod

A project skills-dir plugin (`session-start@skills-dir`, `defaultEnabled: true`) whose hooks
module is `hooks/register.ts` (every engine call) with pure helpers in `hooks/log.ts`. It calls
only the engine, `/bin/date` and `/bin/sh` (ADR 0008); it moves onto the mods library when
CT-31a lands (D187). Every wait is bounded: `/bin/date` and the log append 5 s, the reload 30 s.

| Event | Session | What it does |
| --- | --- | --- |
| `session.start` | interactive only | awaits a plain `/reload-plugins` (never `--force`, D103) for at most 30 s; the engine holds the first prompt until it settles |
| `classic.SessionStart` | `startup`, `clear` | returns `reloadSkills: true` |
| `classic.SessionStart` | `startup` without a title | also returns `sessionTitle` = `ccm-` + `/bin/date +%Y%m%dT%H%M%S.%N%z`, offset cut to the hour (`ccm-20261014T184849.575921000-05`, D61, D76); output off that shape sets no title |

`claude -n <name>` wins: the title is set only when `session_title` is absent. On `/clear`
the engine ignores a title (#67389), so none is sent. `session.start` does not fire after
`/clear`, `/resume` or `/branch`.

Where `sec-default@builtin` is seated (managed settings, a `managed-mcp.json`, or a Team or
Enterprise sign-in), `classic.*` hooks of this project plugin do not run: no skills reload and
no title, while the `session.start` reload still runs (#102134). `claude doctor` shows
`Organization policy: not applicable to Pro and Max accounts` where none applies.

## Status lines

- `session-start: /reload-plugins held: <the reload's line>`: the reload would change MCP or
  LSP tools and invalidate the prompt cache, so nothing reloaded. Start a new session, or type
  `/reload-plugins --force` if losing the cache is acceptable.
- `session-start ERROR: /reload-plugins rejected: <reason>`: the engine refused the command.
- `session-start ERROR: /reload-plugins timeout: no answer after 30000 ms`: the reload was still
  running at the deadline; the session went on without waiting for it.
- `session-start ERROR: date exited <code>: <stderr>` or `session-start ERROR: date output
  unexpected: <output>`: skills still reload; no title was set.

Engine and OS text in a status line or a log row is an excerpt: `token=`, `key=`, `secret=`,
`password=` values and `Bearer` tokens redacted, then the first 120 characters.

No status line after a start means the reload applied, or the hook did not run: the
diagnostic log below tells the two apart.

## Diagnostic log

Every step appends one JSON line to
`~/.local/state/claude-code-marketplace/session-start/events.jsonl` (directory 0700, file 0600;
`MARKETPLACE_SESSION_START_LOG` names another directory) through `/bin/sh`, and the same row goes
to the debug log (`$.ui.log`, `claude --debug`). The append re-tightens the directory to 0700 and
refuses a symlinked `events.jsonl` (exit 3, nothing written). With neither `HOME` nor the override
set, only the debug rows go out, led by one `error` row saying the file log was skipped. Fields:
`ts` (UTC, ns, from `/bin/date -u`), `session_id`, `cli_version`, `event` (`session.start` or
`classic.SessionStart` with `source`), `step`, `result` (an excerpt, see above), `duration_ms` (on
`reload_plugins_end`) and `transcript_path` (on a classic `fired` row).

| `event` | `step` values, in order |
| --- | --- |
| `session.start` | `fired` (`interactive` or `not interactive: no reload`), `reload_plugins_begin`, `reload_plugins_end` (`accepted`, `held: ...`, `rejected: ...`, `timeout: ...`) |
| `classic.SessionStart` | `fired`; on startup and clear `reload_skills_returned`, then `title_set`, `title_kept` (`claude -n`), `title_skipped` (clear, or after an `error` row when `date` failed or printed an unexpected shape) |

## Detect a failure after a restart

Set `L=~/.local/state/claude-code-marketplace/session-start/events.jsonl` and `SID` to the
session's id (its transcript file's name). Each check names what a healthy start prints.

1. Did not fire (mods off, the rollout switch, an untrusted folder, or a `sec-default` hold for the
   classic rows): `jq -r --arg s "$SID" 'select(.session_id==$s and .step=="fired") | .event' "$L"`
   prints `session.start` and `classic.SessionStart` when well; nothing, or only `session.start`,
   is the failure.
2. Reload missing or not accepted:
   `jq -r --arg s "$SID" 'select(.session_id==$s and .step=="reload_plugins_end") | .result' "$L"`
   prints `accepted` when well; nothing (missing), `held: ...`, `rejected: ...` or `timeout: ...`
   is the failure.
3. Reload finished after the first prompt reached the transcript:
   `python3 -I -c 'import json,sys,datetime as d;L,S=sys.argv[1:];R=[json.loads(l) for l in open(L)];R=[r for r in R if r.get("session_id")==S];T=next(r["transcript_path"] for r in R if r.get("transcript_path"));e=[r["ts"] for r in R if r["step"]=="reload_plugins_end"];u=next(r["timestamp"] for r in map(json.loads,open(T)) if r.get("type")=="user" and not r.get("isMeta") and isinstance(r.get("message",{}).get("content"),str));a=d.datetime.strptime(e[-1][:22],"%Y%m%dT%H%M%S.%f").replace(tzinfo=d.timezone.utc);b=d.datetime.fromisoformat(u.replace("Z","+00:00"));print("LATE" if a>b else "ok",a.isoformat(),b.isoformat())' "$L" "$SID"`
   prints `ok` and the two times when well; `LATE` means the reload lost the race.
   `StopIteration` means no classic row or no typed prompt yet; `IndexError` means no
   `reload_plugins_end` row (check 2).
4. No title, or an error:
   `jq -c --arg s "$SID" 'select(.session_id==$s and (.step=="title_skipped" or .step=="error"))' "$L"`
   prints nothing after a startup when well; a row means no `ccm-` title or a failed step. After
   `/clear` one `title_skipped` row is expected.

## Checks and rollback

- `claude plugin validate --strict .claude/skills/session-start`
- `claude plugin test .claude/skills/session-start` (mocked engine; no session, model or network)
- Turn it off: `claude plugin disable session-start@skills-dir`.
- Codex cannot run mods, so this skill has no `.agents/skills` copy.
