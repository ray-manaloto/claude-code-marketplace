# Antigravity native record stores

Observed on the Antigravity desktop app 2.23.0 (macOS, 2026-10-14; research
R20, D153). No official documentation of the format exists: everything here
was observed on one machine or reverse-engineered by third parties
(AgentsView `internal/parser/antigravity*.go`, doubleagent
`analyzer/research/antigravity.md`), and it drifts between builds. Check a
schema with `sqlite3 'file:<copy>?mode=ro&immutable=1' .schema` before
trusting a column.

## Desktop root `~/.gemini/antigravity/`

| Store | Path | What it holds | Notes |
| --- | --- | --- | --- |
| Conversation db | `conversations/<id>.db` (+ `-wal`, `-shm`) | One row per step: `steps(idx, step_type, status, has_subtrajectory, metadata, error_details, permissions, task_details, render_info, step_payload, step_format)`; `gen_metadata(idx, data, size)` (full prompts, token usage); `trajectory_meta`, `trajectory_metadata_blob(id, data)` (workspace URI, branch), `executor_metadata(idx, data)` (one row per agent execution; a failed one carries `execution error: <phase>: …`, for example `pre-invocation hook: context summarization`), `parent_references`, `battle_mode_infos`. | WAL format (header bytes 18-19 = `02 02`). Blobs are plain protobuf (`gemini_coder.Step`), not encrypted on this build. Up to 2.8 GB. `immutable=1` skips the WAL: check `wal_bytes`. |
| Legacy conversation | `conversations/<id>.pb` | Conversations from before the SQLite move (6 here). | AES-encrypted per AgentsView `antigravity_crypto.go`; unreadable, and these have no mirror. Their brain directory keeps artifacts and `.resolved.N` versions; the index content table keeps partial prompt and answer text. |
| Summaries and index | `conversation_summaries.db` | `conversation_summaries`: `conversation_id`, `title`, `preview`, `step_count`, `last_modified_time`, `workspace_uris` (JSON array of `file://` URIs), `status`, `source`, `project_id`, `agent_name`, `parent_conversation_id`, `nesting_depth`, `not_fully_idle`, `killed`, `last_user_input_time`, `last_user_input_step_index`, `raw_summary`. FTS5 table `conversations_fts`. | Times are text `YYYY-MM-DD HH:MM:SS.ffffff+00:00` (UTC). Subagents have an empty title and `last_user_input_time` `0001-01-01…`. `status` read `CASCADE_RUN_STATUS_IDLE` for every row, stopped or not. |
| Full-text index | `conversations_fts` in the summaries db | Columns 0-9 unindexed (`conversation_id`, `chunk_index`, `chunk_first_step`, `chunk_last_step`, `last_modified_time`, `step_count`, `last_step_created_at`, `archived`, byte offsets); indexed 10 `title`, 11 `workspace`, 12 `project`, 13 `user_body`, 14 `agent_body`. `unicode61` tokenizer, prefix indexes 1-3. | Lazy: it covered 35 of 247 conversations here, so a search reports coverage and adds `rg` over the mirrors. The content table `conversations_fts_content` (`c0` id, `c1` chunk, `c2`/`c3` step range, `c13` user text, `c14` agent text) is readable directly. |
| Artifacts | `brain/<id>/*.md` + `*.md.metadata.json` | Plans, walkthroughs, proposals, `task.md` (older builds). Metadata: `summary`, `updatedAt` (UTC), `requestFeedback`, `userFacing`. | Older builds keep versions as `*.md.resolved` and `*.md.resolved.N`. |
| Step mirror | `brain/<id>/.system_generated/logs/transcript_full.jsonl` (+ `transcript.jsonl` with `truncated_fields`, `chunks/`) | One JSON object per step: `step_index`, `source` (`USER_EXPLICIT`, `MODEL`, `SYSTEM`), `type`, `status` (`DONE`, `RUNNING`, `ERROR`, `INVALID`), `created_at` (UTC), `content`, `tool_calls[{name,args}]`, `thinking`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `error`. | Present for every conversation except the legacy `.pb` ones. Can omit or repeat steps (below). Rewritten and truncated at checkpoints (Sessions Viewer). Context fill of a call is `input_tokens + cache_read_tokens`. |
| Tool outputs | `brain/<id>/.system_generated/steps/<idx>/output.txt` | Tool output per step. | Can hold anything the agent read. |
| Background tasks | `brain/<id>/.system_generated/tasks/task-<idx>.log` | Logs of async `run_command` tasks; the task id is `<id>/task-<idx>`. | Hundreds per long conversation. |
| Subagents | `brain/<id>/.system_generated/subagents/<child>.json` | `conversationId`, `subagentDescriptor{typeName, role}`, `state`, `spawnStepIndex`, `workspaceUris`. | `state` stays `SUBAGENT_STATE_ALIVE` after a restart stops the child. Not every build writes these; the summaries' `parent_conversation_id` always links the child. |
| Messages | `brain/<id>/.system_generated/messages/<uuid>.json`, `read.json`, `undelivered/` | `id`, `sender` (`user`, `system`, a child id, `<id>/task-<n>`), `recipient`, `priority`, `timestamp`, `hideFromUser`, `content`. | Holds the "[Notice] All your subagents and background tasks have been stopped due to server restart" messages and child reports. |
| Uploads and media | `brain/<id>/.tempmediaStorage/`, `.user_uploaded/`, `scratch/` | Screenshots, uploads, agent scratch. | Binary; list only. |
| Other | `annotations/<id>.pbtxt` (last view time), `agyhub_summaries_proto.pb` (summaries mirror with subagent role), `antigravity_state.pbtxt`, `user_settings.pb`, `knowledge/<topic>/`, `implicit/<id>.pb` (encrypted), `code_tracker/active/`, `mcp/`, `plugin_data/`, `builtin/skills/`, `bin/` | Settings, knowledge items, tracked file snapshots, MCP and plugin state. | `plugin_data/*/token.json` is a credential. |

## Sibling roots and logs

- `~/.gemini/antigravity-cli/` (the `agy` CLI): same layout, its own
  `conversations/`, `brain/`, `history.jsonl` (REPL input: `display`,
  `timestamp`, `type`, `workspace`), `log/cli-*.log`,
  `jetbox_summaries_proto.pb`; its summaries db has no `conversations_fts`,
  and it listed 6 conversations with neither a database nor a brain directory.
  agy-reader reports CLI dbs as AES-GCM at rest; untested here.
- `~/.gemini/antigravity-ide/`, `~/.gemini/antigravity-backup/`: copies the
  July upgrade wizard made.
- `~/Library/Application Support/Antigravity/`: Electron user data
  (`app_storage.json` UI layout, old VS Code-fork `User/globalStorage/state.vscdb`).
- `~/Library/Logs/Antigravity/main.log`, `language_server.log`: app version,
  port, errors.
- Credentials, never read: `~/.gemini/jetski-standalone-oauth-token`,
  `oauth_creds.json`, `mcp-oauth-tokens-v2.json`, `plugin_data/*/token.json`.

## Enums

- `steps.step_type`: 14 `USER_INPUT`, 15 `PLANNER_RESPONSE`, 17
  `ERROR_MESSAGE`, 23 `CHECKPOINT`, 101 `SYSTEM_MESSAGE`, 132 `GENERIC`; other
  values (5, 8, 21, …) are tool steps (doubleagent research doc lines 280-330).
- `steps.status`: 3 done, 7 error. A long conversation showed status 5 on
  every step before index 20290 and 3 after it; 5's meaning is unverified, so
  read status from the mirror and errors from `step_type`.
- Mirror `type` differs by build: newer builds write `GENERIC` for tool
  results and `ASK_QUESTION` for answered questions; older builds also write
  `VIEW_FILE`, `RUN_COMMAND`, `CODE_ACTION`, `LIST_DIRECTORY`, `GREP_SEARCH`,
  `FIND`, `INVOKE_SUBAGENT`, `EPHEMERAL_MESSAGE`, `CONVERSATION_HISTORY`. In
  every build the call itself is in `PLANNER_RESPONSE.tool_calls`.
- Tool names seen: `run_command` (`CommandLine`, `Cwd`), `write_to_file`
  (`TargetFile`, `CodeContent`, `ArtifactMetadata`), `replace_file_content`
  (`TargetFile`), `view_file`, `ask_question` (`questions`), `manage_task`
  (`Action`, `TaskId`), `schedule`, `manage_subagents`, `invoke_subagent`,
  `search_web`, `read_url_content`, `call_mcp_tool`, `send_message`.

## AgentsView

AgentsView 0.45.0 has Antigravity parsers, and `codex-session-history`'s
`agentsview_search.py` queries the local archive (`--agent antigravity`). The
archive on this machine held no Antigravity rows (R20); enabling that import is
an existing-tool configuration change with its own admission.

## Known gaps

- The mirror can drop steps: a 22,233-step conversation's mirror held 22,221
  lines (22,217 unique steps, 4 indexes written twice) and lacked all 16 of
  its `step_type` 17 quota errors, the closing ones included. Liveness and the
  stop reason come from the database. Across both roots, about 3,000 steps
  were mirror-less, most of them error notices.
- An immutable open of a copy whose `-wal` is non-empty misses the WAL's
  transactions (a 10-row WAL read as 0 rows in a synthetic check).
- The running app keeps empty `-wal` and `-shm` files beside the databases
  it has open (an August conversation's were dated the morning of the check),
  so their mtimes say when the app opened it, not when the agent last acted.
- The app can quit between two checks (an auto-update restarted it during
  this skill's evals); take liveness from step times and the database tail,
  and `pgrep` only as a point-in-time observation.
- Summaries can lag the database; conversations missing from the summaries
  are invisible in the app (antigravity-cli#727).
- Database-only steps have no `created_at` in a readable column; their payload
  carries the HTTP `Date` header for API errors.
- No decoder for `step_payload` and `gen_metadata` exists in this repository
  yet (C++ core ticket); `strings` and `protoc --decode_raw` are the stopgaps.
