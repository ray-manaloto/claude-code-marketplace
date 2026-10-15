# CT-87: live hook probe receipt (decision D169)

Ticket CT-87 under decision D169 (the user admitted one throwaway `claude -p` probe in a scratch
repository). CL4 section 7 calls this probe "CT-86"; the parent numbered it CT-87. Run by a
subagent of session `ccm-20261014` on 2026-10-14, 19:55:27Z to 19:55:56Z. Nothing in MP was edited
except this file. Inputs: `CL3-research.md` sections 1, 7.1 and 11, `CL4-proposal.md` section 7.

Abbreviations: `<R>` is the scratch repository
`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/hookprobe`
(new `git init`, branch `main`, no commits, no remote); `<T>` is the probe's transcript directory
`~/.claude/projects/-private-tmp-claude-501--Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace-ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34-scratchpad-hookprobe`.
Both are outside MP and temporary (`/private/tmp`).

## Result per item

| Item | Result | Evidence |
|---|---|---|
| (1) `UserPromptSubmit` with prompt text and `prompt_id`, typed slash command before expansion | PASS | Fired for `/probe-cmd alpha` with `"prompt":"/probe-cmd alpha"` (the unexpanded text; the transcript user message holds the expanded command body) and `prompt_id` `ff1c3221-...`; fired for the plain prompt with `prompt_id` `526dc3a5-...`. It did NOT fire for the built-in `/compact`, although that command got its own `prompt_id` (`897affc9-...`), which PreCompact, SessionStart(compact), PostCompact and the compaction SubagentStop carry |
| (2) `PostToolUse` matcher `AskUserQuestion` carries the answer | PASS, with a permission host | In `-p` the tool is offered only when the run has a permission host (`hooks.md:1968` in the CL3 mirror). The driver acted as that host (`--permission-prompt-tool stdio`, the Agent SDK `canUseTool` path) and answered `Blue` plus a free-text note. `tool_response` equals `tool_input` and holds `answers` and `annotations.<question>.notes`; the model received `"Probe question: which color?"="Blue" notes: probe free-text note N-7731` |
| (3) `PreCompact` fires on manual compaction; stdout appended to the compaction instructions | PASS (manual path only) | PreCompact fired (`trigger: manual`, `custom_instructions: null`). Its stdout asked for `PRECOMPACT-6BCDBDE8`; the summarizer's analysis names it as part of the compaction instruction ("It also asks for the literal token PRECOMPACT-6BCDBDE8 on its own line"), and the summary opens with that line. The marker occurs in no prompt before compaction, so the only source is the hook stdout. Found in `PostCompact.compact_summary` and in the transcript's `isCompactSummary` row (uuid `777e3e8a-3e28-4136-91ad-114cf27d6f7d`) |
| (4) `SessionStart` source `compact` fires after it | PASS | Hook order in `logs/all.jsonl`: PreCompact, SubagentStop (the internal compaction agent, `agent_type ""`), SessionStart `source: compact` (payload adds `prompt_id` and `model`), PostCompact. This matches #78760 |
| (5) `SubagentStart` fires and its `additionalContext` reaches the subagent | PASS | SubagentStart fired (`agent_type probe-echo`, `agent_id a4cd2905d8e164af3`, with `prompt_id`). The subagent transcript has an `attachment` row of type `hook_additional_context` with `["Probe context marker: SUBAGENTCTX-043E7AB5"]` (row 3), the request text `SubagentStart hook additional context: Probe context marker: SUBAGENTCTX-043E7AB5` (row 12), and the subagent replied the marker verbatim (row 14; also `SubagentStop.last_assistant_message`) |

Not tested here: PreCompact on the automatic path (CL3 section 11 (a) asks for it; a tiny session
cannot reach the auto threshold cheaply); pwf's JSON `systemMessage` from PreCompact (CL4 (b)); a
synchronous `UserPromptSubmit` stdout reaching the model (CL4 (f); these hooks print nothing);
AskUserQuestion denied or failing (it succeeded, so `PostToolUseFailure` never fired); the
interactive TUI.

Other observations:
- After compaction the transcript gets a `local-command-stdout` row (`repeatsCompactSummary: true`,
  uuid `241bb63f-c53a-4628-a417-e6a3b48221fa`) reading `Compacted PreCompact [<hook command>]
  completed successfully: <hook stdout>`, so the PreCompact stdout also reaches the model's
  post-compaction context, once.
- Compaction runs as an internal subagent: one `SubagentStop` (agent `aaf88b20363d1f017`, empty
  `agent_type`) with no matching `SubagentStart`; its `agent_transcript_path` file was never written.
  A SubagentStop gate (CL3 M10) will see this agent.
- `--include-hook-events` streamed `hook_started`/`hook_response` for SessionStart, UserPromptSubmit,
  SubagentStart, SubagentStop, PreToolUse and PostToolUse, but not for PreCompact or PostCompact,
  although both ran (hook logs).
- `prompt_id` is on every payload of a turn (PreToolUse, PostToolUse, SubagentStart, SubagentStop),
  so ledger rows can join on it.
- Compaction kept a verbatim tail of two assistant rows (`preservedMessages`); the summary therefore
  called step 3 "not yet done" while the preserved tail held the step-3 reply. `pre_tokens` 360,659,
  `post_tokens` 8,141.

## CLI and environment

- `claude --version`: `2.1.300 (Claude Code)`; binary
  `/Users/rmanaloto/.local/share/claude/versions/2.1.300`. Session model reported as
  `claude-haiku-5-5` (`--model haiku`).
- Hook tool: `/usr/bin/jq` `jq-1.7.1-apple`.
- Environment: the child got only `HOME`, `USER`, `LOGNAME`, `TMPDIR`, `LANG`,
  `PATH=/usr/bin:/bin:/usr/sbin:/sbin:/Users/rmanaloto/.local/bin`, `SHELL=/bin/zsh`, `TERM=dumb`.
  The parent's `CLAUDE_CODE_*`, `CLAUDECODE`, `PWF_*`, `PLAN_ID`, `FNOX_*` and `MISE_GITHUB_TOKEN`
  were not passed. Auth was the CLI's own stored login; no credential was passed.
- `--setting-sources project`: user settings (and so the user's enabled plugins and its herdr
  SessionStart hook) were not loaded; the init message lists only the built-in plugins
  `cc-plugin-agents-md`, `cc-plugin-telemetry`, `cc-plugin-plugin-authoring`, and tools
  `["Task","AskUserQuestion"]`. No global setting was changed.
- Workspace trust: `-p` skips the trust dialog (help text: "The workspace trust dialog is skipped
  when Claude is run in non-interactive mode"); the project hooks ran with no prompt and no
  workaround.

## Settings used (`<R>/.claude/settings.json`, sha256 `3bb9016122f8b1bfb8c72bad5edc729076bf4a006ef406b91034265166a9ce87`)

One command hook per event; `H` = `/bin/sh <R>/.claude/hooks`:

```json
{"UserPromptSubmit":[{"hooks":[{"type":"command","command":"H/log.sh UserPromptSubmit"}]}]}
{"PreToolUse":[{"matcher":"AskUserQuestion","hooks":[{"type":"command","command":"H/log.sh PreToolUse"}]}]}
{"PostToolUse":[{"matcher":"AskUserQuestion","hooks":[{"type":"command","command":"H/log.sh PostToolUse"}]}]}
{"PostToolUseFailure":[{"matcher":"AskUserQuestion","hooks":[{"type":"command","command":"H/log.sh PostToolUseFailure"}]}]}
{"PreCompact":[{"hooks":[{"type":"command","command":"H/precompact.sh"}]}]}
{"PostCompact":[{"hooks":[{"type":"command","command":"H/log.sh PostCompact"}]}]}
{"SessionStart":[{"hooks":[{"type":"command","command":"H/log.sh SessionStart"}]}]}
{"SubagentStart":[{"hooks":[{"type":"command","command":"H/subagentstart.sh"}]}]}
{"SubagentStop":[{"hooks":[{"type":"command","command":"H/log.sh SubagentStop"}]}]}
```

`log.sh <Event>` (log-only; the raw copy guards against #89622 invalid JSON):

```sh
#!/bin/sh
# Log-only probe hook: append the hook's stdin JSON to logs. $1 = event label.
L=<R>/logs
in=$(/bin/cat)
printf '%s\n' "$in" >> "$L/raw.log"
printf '%s\n' "$in" | /usr/bin/jq -c . >> "$L/$1.jsonl" 2>> "$L/jq-errors.log"
printf '%s\n' "$in" | /usr/bin/jq -c . >> "$L/all.jsonl" 2>/dev/null
exit 0
```

`precompact.sh` runs `log.sh PreCompact`, then prints one plain line:
`Probe instruction: the summary must contain the literal token PRECOMPACT-6BCDBDE8 on a line of its own.`
`subagentstart.sh` runs `log.sh SubagentStart`, then prints
`{"hookSpecificOutput":{"hookEventName":"SubagentStart","additionalContext":"Probe context marker: SUBAGENTCTX-043E7AB5"}}`.
Both markers were random (`openssl rand -hex 4`) and appear in no prompt.

Probe fixtures in `<R>/.claude/`: `commands/probe-cmd.md` (body: call Agent `probe-echo` once, then
AskUserQuestion once with "Probe question: which color?" Red/Blue, then reply one line) and
`agents/probe-echo.md` (`model: haiku`; quote every context line containing `SUBAGENTCTX-`, use no
tool).

## Invocation (one `claude -p` process)

A Python driver (`scratchpad/hookprobe-driver/drive.py`, sha256
`a8329c316304e4607dd7d94dd46ebd3e205cba7e6f687a318f41023c6013b651`, run with `python3 -I`, cwd
`<R>`) started one process and fed it three user messages over stream-json, each after the previous
`result`: `/probe-cmd alpha`, `/compact`, `Reply with the single word DONE.` It answered the single
`can_use_tool` request (AskUserQuestion) with `behavior: allow` and `updatedInput` = the input plus
`answers` (last option, `Blue`) and `annotations.<question>.notes`.

```
claude -p --input-format stream-json --output-format stream-json --verbose --include-hook-events \
  --permission-prompt-tool stdio --model haiku --tools Agent,AskUserQuestion \
  --setting-sources project --max-turns 8 --max-budget-usd 1.00
```

| Step | Message | Result row | Exit |
|---|---|---|---|
| 1 | `/probe-cmd alpha` | `success`, 3 turns, 13.1 s, result `SUBAGENT_REPORT=SUBAGENTCTX-043E7AB5 ANSWER=Blue` | |
| 2 | `/compact` | `success`, 0 turns, 7.8 s, `compact_boundary` trigger manual | |
| 3 | `Reply with the single word DONE.` | `success`, 1 turn, 6.6 s, result `DONE` | |
| process | | stdin closed after step 3 | `claude` exit 0; driver exit 0 |

Session id `797fac9e-45f6-4000-bb0b-7a4b6c71a99d`; stream log `scratchpad/hookprobe-run1/stream.jsonl`
(sha256 `de4271439e7c527f720dd668eb0e59b16863b6bc417f80a29e21a9a6d3e331de`), empty stderr.
Tool calls in the whole run: Agent 1, AskUserQuestion 1 (main and subagent transcripts).

## Cost

CLI-reported cumulative `total_cost_usd` 0.7616 (after step 1: 0.3831; after step 2: 0.4061; after
step 3: 0.7616), all `claude-haiku-5-5`. This exceeds the "few cents" admitted for D169. Cause: the
account's claude.ai connectors put 383 MCP tool definitions into the context (Vercel 236, Docusign
31, Gmail 30, Supabase 28, Slack 13, Drive 11, Firecrawl 9, Calendar 9, Claude Docs 8, Exa 3,
Context7 2, tldraw 2, Mermaid 1; counted in the transcript's request blobs), about 355,000 to
362,000 cache-creation tokens per request. `--tools` limits built-in tools only, and the isolation
flags dropped the user-settings env (including `ENABLE_TOOL_SEARCH`) that normally defers them. No
connector tool was called. For a future probe, add `--strict-mcp-config` with no `--mcp-config`
(help: "Only use MCP servers from --mcp-config, ignoring all other MCP configurations"; whether it
covers claude.ai connectors is UNVERIFIED) and keep `--max-budget-usd`.

## Hook log excerpts (`<R>/logs/all.jsonl`, in firing order; `cwd` dropped, long fields shortened)

No secrets were present (regex scan for API-key, GitHub-token and Slack-token shapes and e-mail
addresses found only paths). Hashes: `all.jsonl` and `raw.log`
`6049dc8102521d0879663c7239d1779cc73b0a8f180e05e9d80c7077fd642822` (identical), `jq-errors.log` empty.

```jsonl
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","hook_event_name":"SessionStart","source":"startup"}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"ff1c3221-ef20-4940-a382-bf0dadcffa05","permission_mode":"default","hook_event_name":"UserPromptSubmit","prompt":"/probe-cmd alpha"}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"ff1c3221-ef20-4940-a382-bf0dadcffa05","agent_id":"a4cd2905d8e164af3","agent_type":"probe-echo","hook_event_name":"SubagentStart"}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"ff1c3221-ef20-4940-a382-bf0dadcffa05","permission_mode":"default","agent_id":"a4cd2905d8e164af3","agent_type":"probe-echo","effort":{"level":"medium"},"hook_event_name":"SubagentStop","stop_hook_active":false,"agent_transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d/subagents/agent-a4cd2905d8e164af3.jsonl","last_assistant_message":"SUBAGENTCTX-043E7AB5","background_tasks":[],"session_crons":[]}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"ff1c3221-ef20-4940-a382-bf0dadcffa05","permission_mode":"default","effort":{"level":"medium"},"hook_event_name":"PreToolUse","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"Probe question: which color?","header":"Color","options":[{"label":"Red","description":"red"},{"label":"Blue","description":"blue"}],"multiSelect":false}]},"tool_use_id":"toolu_01NaR2bfprATUFujrY2dE1Hy"}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"ff1c3221-ef20-4940-a382-bf0dadcffa05","permission_mode":"default","effort":{"level":"medium"},"hook_event_name":"PostToolUse","tool_name":"AskUserQuestion","tool_input":{"questions":[{"question":"Probe question: which color?","header":"Color","options":[{"label":"Red","description":"red"},{"label":"Blue","description":"blue"}],"multiSelect":false}],"answers":{"Probe question: which color?":"Blue"},"annotations":{"Probe question: which color?":{"notes":"probe free-text note N-7731"}}},"tool_response":{"questions":[{"question":"Probe question: which color?","header":"Color","options":[{"label":"Red","description":"red"},{"label":"Blue","description":"blue"}],"multiSelect":false}],"answers":{"Probe question: which color?":"Blue"},"annotations":{"Probe question: which color?":{"notes":"probe free-text note N-7731"}}},"tool_use_id":"toolu_01NaR2bfprATUFujrY2dE1Hy","duration_ms":0}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"897affc9-1d30-4557-b55e-8afbd58241a6","hook_event_name":"PreCompact","trigger":"manual","custom_instructions":null}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"897affc9-1d30-4557-b55e-8afbd58241a6","permission_mode":"default","agent_id":"aaf88b20363d1f017","agent_type":"","effort":{"level":"medium"},"hook_event_name":"SubagentStop","stop_hook_active":false,"agent_transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d/subagents/agent-aaf88b20363d1f017.jsonl","last_assistant_message":"<analysis>\nThis session is a short hook-probe run triggered by the `/probe-cmd` ...<truncated>","background_tasks":[],"session_crons":[]}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"897affc9-1d30-4557-b55e-8afbd58241a6","hook_event_name":"SessionStart","source":"compact","model":"claude-haiku-5-5"}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"897affc9-1d30-4557-b55e-8afbd58241a6","hook_event_name":"PostCompact","trigger":"manual","compact_summary":"<3999 chars; excerpt below>"}
{"session_id":"797fac9e-45f6-4000-bb0b-7a4b6c71a99d","transcript_path":"<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d.jsonl","prompt_id":"526dc3a5-c5d1-4c46-b4ca-8d425e3db75b","permission_mode":"default","hook_event_name":"UserPromptSubmit","prompt":"Reply with the single word DONE."}
```

`PostCompact.compact_summary` (3,999 characters), opening lines of `<summary>` and the analysis
sentence that names the instruction:

```
The most recent message is a system-level instruction to respond with text only, with no tool calls, in an analysis-plus-summary format. It also asks for the literal token PRECOMPACT-6BCDBDE8 on its own line in the summary. That token is a harness probe instruction, not something from the user's original probe. [...]
</analysis>

<summary>
PRECOMPACT-6BCDBDE8

1. Primary Request and Intent:
   The user invoked `/probe-cmd alpha` as a hook probe. [...]
```

Post-compaction row seen by the model (`repeatsCompactSummary: true`):

```
<local-command-stdout>Compacted PreCompact [/bin/sh <R>/.claude/hooks/precompact.sh] completed successfully: Probe instruction: the summary must contain the literal token PRECOMPACT-6BCDBDE8 on a line of its own.
PostCompact [/bin/sh <R>/.claude/hooks/log.sh PostCompact] completed successfully</local-command-stdout>
```

Subagent transcript `<T>/797fac9e-45f6-4000-bb0b-7a4b6c71a99d/subagents/agent-a4cd2905d8e164af3.jsonl`:

```
row 3  attachment hook_additional_context hookName SubagentStart content ["Probe context marker: SUBAGENTCTX-043E7AB5"]
row 12 request text "SubagentStart hook additional context: Probe context marker: SUBAGENTCTX-043E7AB5\n\n# Environment ..."
row 14 assistant "SUBAGENTCTX-043E7AB5"
```

## What this means for CT-88 and the capture ticket

- The PreCompact leg (CL3 M5) works on 2.1.300 for manual compaction: plain exit-0 stdout becomes a
  compaction instruction the summarizer obeys, and it is also echoed once after compaction. The auto
  path stays UNVERIFIED on this host.
- The AskUserQuestion leg (CL3 M2) can key answer rows on `tool_use_id` and `prompt_id`, and
  `tool_response.annotations.<question>.notes` carries free text.
- A `UserPromptSubmit` ledger misses built-in commands such as `/compact`; their `prompt_id` shows up
  only on the compaction hooks.
- SubagentStart `additionalContext` is the confirmed route for carrying the open list into subagents
  (CL3 M7).

## Leftovers outside MP

`<R>` (repository, hooks, logs), `scratchpad/hookprobe-driver/`, `scratchpad/hookprobe-run1/` and
`<T>` (the session transcript, one subagent transcript and an empty `memory/` directory). `claude
purge <R>` would remove the Claude Code state for that path; nothing was purged.
