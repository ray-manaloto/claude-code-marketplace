# Codex native record stores

Observed on Codex CLI 0.162.x / Codex Desktop, macOS, `CODEX_HOME=~/.codex`.
Paths and schemas drift between releases; verify with `sqlite3 -readonly <db> .schema`
before trusting a column name.

| Store | Path | What it holds | Notes |
| --- | --- | --- | --- |
| Rollout transcript | `sessions/YYYY/MM/DD/rollout-<start>-<thread-id>.jsonl` | Every record of a thread: `session_meta`, `turn_context`, `event_msg` (`thread_settings_applied`, `task_started`, `task_complete` with `last_agent_message`, `turn_aborted`, `item_completed`, `token_count`), `response_item` (`message` with role user/assistant/developer, `reasoning`, `function_call`/`function_call_output`, `custom_tool_call` named `exec` with JS source in `input`, `agent_message` between subagents), `compacted` (`replacement_history`), `token_usage_record`, `world_state`, `inter_agent_communication_metadata`. | Forks start with `session_meta.forked_from_id` + `forked_from_ordinal_exclusive`; ordinals continue from the parent. `function_call_output` and `agent_message` payloads may be `encrypted_content`. Timestamps are ISO-8601 UTC. |
| Thread index | `state_5.sqlite` table `threads` | id, `rollout_path`, cwd, title, `first_user_message`, model, `reasoning_effort`, git sha/branch/origin, created/updated (epoch seconds; `*_ms` siblings), archived, `name` (e.g. `[scheduler][fork][000]…`), `history_mode`. | Table `thread_spawn_edges(parent_thread_id, child_thread_id, status)` links subagent threads. `projects`, `thread_attachments` (worktree attachments the Desktop app shows). |
| Thread history | `thread_history_1.sqlite` tables `thread_turns`, `thread_items` | Per-turn status (`completed`/`failed`), `error_json` (usage-limit messages appear here), `duration_ms`, rollout ordinal/byte offsets; per-item JSON projections. | Multi-GB; query by `thread_id` only. |
| Tracing logs | `logs_2.sqlite` table `logs` | `ts` (epoch **seconds**), `ts_nanos`, level, target (`feedback_tags`, `codex_core::session::turn`, `codex_otel.agent_communication`, MCP catalogs…), `feedback_log_body`, `thread_id`, `process_uuid`. | 100–300 MB with WAL; always filter by `thread_id`. |
| Writer locks | `thread-writer-locks/<thread-id>.lock` | Empty marker files; mtime ≈ last turn start. | Presence is not liveness. |
| Shell snapshots | `shell_snapshots/<thread-id>.<nanos>.sh` | Environment snapshots taken per turn. | One file per dispatch; count ≈ turns with shell use. |
| Research receipts | `research-coverage/<thread-id>/<turn-id>/{manifest.json,required.json,<source>.json,<source>.raw}` + `*-last30days-plan.json` | Global hook's research-fanout output: policy (`strict-five-v2`), query, per-provider status, raw hashes. `-attemptN` suffixes keep retried runs. | A failed arm (quota, HTTP 402, validator rejection) is a recorded gap, not a pass. |
| Memories | `memories/MEMORY.md`, `memories/rollout_summaries/*.md`, `memories/skills/` | Codex's own cross-thread memory and per-rollout summaries. | Summaries exist only for some threads; grep by cwd or thread id. |
| Automations | `automations/<id>/automation.toml`, `memory.md` | Heartbeat/cron prompts, `rrule`, `status` (`PAUSED`/active), `target_thread_id`. | Explains why a thread keeps waking up. |
| Hook monitor | `hook-monitor/events.jsonl`, `failures/`, `latest-failure.json` | Global hook watchdog events. | |
| OTel export | config `[otel]` → `http://127.0.0.1:4318/v1/logs`; launchd `com.opensymphony.codex-otel` writes `~/Library/Application Support/OpenSymphony/codex-otel/codex-otel*.jsonl` | Redacted OTLP log records (body emptied; only `service.name`, `service.version`, `deployment.environment.name` kept), 10 MB rotation, 7 days. | Confirms activity windows and build versions only. |
| AgentsView archive | daemon `http://127.0.0.1:8080`, token file under `~/Library/Application Support/AgentsView-*/archive/native-server-token`; sessions keyed `codex:<thread-id>` | Imported Codex/Claude/Antigravity messages with ordinals, lexical and (when the embedding index is built) semantic search, browser URLs. | `coverage.semantic.status` tells you which mode answered. |
| App-server daemon | `app-server-daemon/*.log`, socket under `app-server-control/` | Desktop app ↔ core daemon logs. | `codex agents` browses live sessions (needs a working `timeout`-free shell). |

## Known gaps

- Compaction `replacement_history` is mostly developer boilerplate; mid-thread intent comes from turn-final messages and the assistant timeline.
- `state_5.threads.git_sha` is captured at thread start and goes stale.
- The rollout for a thread forked at ordinal N omits records < N; read the parent for earlier context.
- Deleted/archived threads keep rollouts under `archived_sessions/`.
