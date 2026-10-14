# R20: Antigravity session history, storage map and a skill design (D153)

Research agent R20, research6 team, 2026-10-14. Task: map where the Antigravity desktop app keeps
conversations, artifacts, plans, tasks, subagents, background tasks and settings on this Mac, show
how to search them with system tools, and design a skill that does for Antigravity what
`.claude/skills/codex-session-history` does for Codex. TR-specific findings are in the private
report named by the task, not here. Offline mirror: `offline/research/R20/` (`manifest.json`, 50
items; `queries.jsonl`, 53 rows).

## Verdict

Build `antigravity-session-history` as a SKILL.md-only skill: a storage map reference, copy-paste
`sqlite3`, `jq`, `rg` and `strings` recipes, the codex skill's brief template, and no `scripts/`
directory. Confidence: high for the storage map and recipes, medium for the parser boundary.

What decides it:

1. Conversation text is readable without decryption on this install. The desktop app (2.23.0, read
   from `/Applications/Antigravity.app/Contents/Info.plist` and
   `~/Library/Logs/Antigravity/language_server.log:3`) writes every conversation twice. One copy is
   a SQLite database of protobuf steps (`~/.gemini/antigravity/conversations/<uuid>.db`). The other
   is a plain JSONL mirror (`brain/<uuid>/.system_generated/logs/transcript_full.jsonl`), which
   `jq` reads directly. A byte search of a copied database found user and model text in
   `steps.step_payload` and `gen_metadata.data`, so the protobuf payloads are not encrypted here.
   Only the legacy `conversations/*.pb` files are opaque: gzip makes them bigger (26,847,416 to
   26,855,634 bytes), and two sources describe them as AES-encrypted
   ([ericxliu.me](https://ericxliu.me/posts/reverse-engineering-antigravity-ide/), mirror
   `pages/ericxliu-reverse-engineering.md:53-56`; AgentsView `internal/parser/antigravity_crypto.go:18-40`
   at `dcdad61`).
2. The app ships a native full-text index: `conversation_summaries.db` holds an FTS5 table
   `conversations_fts` over title, workspace, user text and agent text, with step ranges. One
   `sqlite3 … MATCH` query does what the codex skill does with a Python script.
3. A parser is needed only for three gaps. (a) Steps the JSONL mirror leaves out: in one
   22,233-step conversation the mirror held 22,221 lines and was missing every quota error at the
   end. (b) Token usage, which lives only in `gen_metadata`. (c) Conversations that have a database
   but no mirror (6 of 247 here). Under D112/D113 that parser is a C++ ticket (section "Skill
   design", item 8), not Python. Prior art exists in Go, Python and Rust (section "Code examples").
4. Never run the app's CLI for this. `agy` importing a desktop conversation rewrites the desktop
   summaries row: id, title, project and source (google-antigravity/antigravity-cli#1006, opened
   2026-09-12, still open). Copy files first, then open them with `mode=ro&immutable=1`.

## 1. Queries sent in stage 1, exact text

Preflight (D142): Firecrawl `firecrawl credits --json` showed `remainingCredits` -128, so it was
SKIPPED with CREDITS_EXHAUSTED (seq 1). Serper balance was 1307 (seq 2), SerpApi
`plan_searches_left` 245 (seq 3), GitHub search 30, code_search 10 and graphql 5000 (seq 4).
Exa and Context7 have no balance endpoint (seq 5, 6). Repository feature checks: seq 27.

| seq | Provider | Query |
|---|---|---|
| 7 | exa | `Google Antigravity conversation history storage ~/.gemini/antigravity conversations .pb brain directory` |
| 8 | exa | `export or search Google Antigravity agent conversation transcripts transcript.jsonl brain artifacts` |
| 9 | exa | `Antigravity IDE conversations protobuf decode recover chat history` |
| 10 | context7 | `ctx7 library antigravity "conversation history storage location"` |
| 11 | firecrawl | not called (preflight) |
| 12 | serper | `Antigravity "conversations" ".pb" "brain" "transcript.jsonl"` |
| 13 | serper | `Antigravity "conversation_summaries.db"` |
| 14 | serper | `antigravity ".system_generated" transcript` |
| 15-25 | webclaw | 11 pages, URLs in section 2 |
| 26 | last30days | `last30days.py "Google Antigravity conversation history storage and search" --plan plan.json --emit json --search reddit,hackernews,github --save-dir ""` (plan: `local/last30days/plan.json`, two subqueries) |

## 2. Results from each

| seq | Hits | Top results | Used |
|---|---|---|---|
| 7 | 10 | [Managing conversations, Antigravity CLI docs](https://antigravity.google/docs/cli/conversations/); Shivansh-Malviya/resurrect; forum threads on lost history and `.pb` files | yes |
| 8 | 10 | [agent-sessions guide](https://jazzyalex.github.io/agent-sessions/guides/antigravity-cli-local-history.html); [Artifacts docs](https://antigravity.google/docs/artifacts/); [Sessions Viewer](https://sessions-viewer.js-bridge.com/agents/antigravity-cli); mjacobs/agy-reader; [txcript format doc](https://docs.rs/crate/txcript/latest/source/docs/formats/antigravity.md) | yes |
| 9 | 10 | arashz/antigravity_decryptor; Antigravity-Legacy-Migrator; [ericxliu.me reverse engineering](https://ericxliu.me/posts/reverse-engineering-antigravity-ide/); mjacobs/agy-reader | yes |
| 10 | 0 | Context7 "Monthly quota reached", rc 1: SKIPPED, CREDITS_EXHAUSTED (`probe/ctx7/lib1.txt`) | gap |
| 12 | 2 | manaflow-ai/cmux#4531; PeonPing changelog | no |
| 13 | 10 | google-antigravity/antigravity-cli#1006; [session-migrate antigravity-format.md](https://github.com/xhluca/session-migrate/blob/main/docs/antigravity-format.md); [ClawMetry Antigravity](https://clawmetry.com/docs/runtime/antigravity/); [SpecterOps Blacklight](https://specterops.io/blog/2026/08/12/blacklight-ai-agent-endpoint-artifacts/) | yes |
| 14 | 0 | EMPTY_UNVERIFIED | no |
| 15-25 | 1 each | mirrored to `offline/research/R20/pages/<name>.md`: agy-cli-conversations, agy-artifacts, agent-sessions-agy-cli, txcript-antigravity-format, sessions-viewer-agy-cli, ericxliu-reverse-engineering, session-migrate-antigravity-format, specterops-blacklight, forum-pb-files-still-exist, forum-trajectory-not-found, clawmetry-antigravity | yes |
| 26 | 13 | Chatixia-AI/interlatch#14 "Record Google Antigravity sessions"; stablyai/orca#24692; the other 11 were off topic. Status DEGRADED (Reddit partial). | yes, 2 |

## 3. GitHub issues, PRs and discussions searched (stage 2)

| seq | Search | Seeded by | Result |
|---|---|---|---|
| 28 | `gh issue view 1006 --repo google-antigravity/antigravity-cli --comments` | 13 | CLI import mutates the desktop `conversation_summaries.db` and `agyhub_summaries_proto.pb` |
| 29 | `gh search issues "conversation_summaries.db"` | 13 | 20 hits |
| 30 | `gh search issues "transcript_full.jsonl"` | 19 | 20 hits |
| 31 | antigravity-cli#727 (2026-08-02, open) | 13 via 29 | Unindexed conversations make `/resume` load every database; `gen_metadata` blobs grow large |
| 32 | seanthegeek/doubleagent#83 (2026-10-13, open) | 13 via 29 | Desktop app 2.23.0 on macOS: same SQLite-of-protobuf layout as the CLI, `trajectory_meta.source` 1 versus 17 for the CLI, plus `annotations/<uuid>.pbtxt`, `agyhub_summaries_proto.pb`, logs in `~/Library/Logs/Antigravity/` |
| 33 | repolex-ai/ravel#26 (2026-10-14, open) | 13 via 29 | Discover conversations from `conversation_summaries.db`, not the REPL `history.jsonl`; `parent_conversation_id` links subagents |
| 34 | ccusage/ccusage#1874 (closed 2026-10-13) | 13 via 29 | Scanning every `*.db` under the root picks up `conversation_summaries.db` itself; filter to `conversations/` |
| 35 | seanthegeek/doubleagent#87 (2026-10-13, open) | 19 via 30 | The JSONL mirror and the database duplicate each other; read the mirror only when the database is missing |
| 36 | `gh search prs "antigravity conversation_summaries"` | 13 | 15 hits (readers in many session tools) |
| 37 | `gh search prs "antigravity brain transcript_full"` | 19 | 1 hit, kurrent-io/kcap-cli#262 |
| 38 | `gh pr view 24692 --repo stablyai/orca` (merged 2026-10-02) | 26 | Discovers the three roots and both transcript names; TypeScript index reader |
| 39 | `gh pr view 14 --repo Chatixia-AI/interlatch` (merged 2026-10-02) | 26 | Reads `transcript_full.jsonl` and treats the store as unusable (encrypted `.pb` before, protobuf SQLite now); writes nothing into `~/.gemini` |
| 40, 41 | GraphQL `type:DISCUSSION`: "antigravity conversation history export", "antigravity brain transcript" | 7, 8 | 15 and 7 hits, none about storage (google-gemini/gemini-cli discussion 27274 announces the move to Antigravity CLI) |
| 42-45 | `git clone --filter=blob:none` of kenn-io/agentsview `dcdad61`, xhluca/antigravity-session-interoperability `b85c60a`, mjacobs/agy-reader `fd9df25`, seanthegeek/doubleagent `a124dee` | 8, 21, 8, 13 | code examples below |

Discussions are off for antigravity-cli, agy-reader, the interoperability repository, agentsview
and antigravity_decryptor (`has_discussions` false, seq 27), so no discussion search ran on them.

## 4. Saved searches (githubkit route, reproduced read-only) and proposed rows

`./dev/mise run research:collect` writes into a tracked path, so it was not run. The collector
sends `GET /search/code` (`dev/github_search_one_page.py:144`) with `q="<query> repo:<repo>"`
(`dev/control_saved_search.py:33`, `dev/collect_saved_search.py:157`); I
reproduced that request with `gh api -X GET search/code -f q=… -F per_page=5 -F page=1`, writing
the output to `offline/research/R20/gh/saved/`.

| seq | Row | Query | Hits | Control (README) |
|---|---|---|---|---|
| 46, 47 | existing `codex-schema` (`dev/saved-searches.toml:3-15`) | `schema repo:openai/codex` | 878 | 161 |
| 48, 49 | proposed `agentsview-antigravity-steps` | `step_payload repo:kenn-io/agentsview` | 4 | 73 |
| 50, 51 | proposed `doubleagent-antigravity-transcript` | `transcript_full repo:seanthegeek/doubleagent` | 2 | 57 |
| 52, 53 | proposed `agy-reader-trajectory-sidecar` | `trajectory.json repo:mjacobs/agy-reader` | 32 | 6 |

Proposed rows (not added to `dev/saved-searches.toml`):

```toml
# Antigravity session history (research R20, decision D153, 2026-10-14)
[[search]]
id = "agentsview-antigravity-steps"
query = "step_payload"
repo = "kenn-io/agentsview"                   # 4 hits today; control README 73
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "doubleagent-antigravity-transcript"
query = "transcript_full"
repo = "seanthegeek/doubleagent"              # 2 hits; control README 57
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "agy-reader-trajectory-sidecar"
query = "trajectory.json"
repo = "mjacobs/agy-reader"                    # 32 hits; control README 6
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 5. Seed-to-search map

| Stage-1 seq | Named | Stage-2 seq |
|---|---|---|
| 7 | forum threads, `.pb` recovery tools | 40 |
| 8 | mjacobs/agy-reader, agentsview (named in its README) | 41, 42, 44, 48, 52 |
| 13 | antigravity-cli#1006, `conversation_summaries.db` | 28, 29, 31-34, 36, 45, 50 |
| 19 | `transcript_full.jsonl` (Sessions Viewer page) | 30, 35, 37 |
| 21 | xhluca/antigravity-session-interoperability | 43 |
| 26 | interlatch#14, orca#24692 | 38, 39 |

## 6. Findings: storage map

All paths are under `$HOME`. Sizes were measured on 2026-10-14 with `du`, `ls` and `wc`. The app was
running and was never touched.

### 6.1 `~/.gemini/antigravity/` (desktop app data root)

| Path | Holds | Format | Size here | Search with |
|---|---|---|---|---|
| `conversations/<uuid>.db` (+ `-wal`, `-shm` while live) | The whole conversation, one row per step. Tables `trajectory_meta`, `steps(idx, step_type, status, has_subtrajectory, metadata, error_details, permissions, task_details, render_info, step_payload, step_format)`, `gen_metadata(idx, data, size)`, `executor_metadata`, `parent_references`, `trajectory_metadata_blob` ("main": workspace URI, branch), `battle_mode_infos` | SQLite, `user_version` 1. Blobs are plain protobuf (`gemini_coder.Step`) | 241 files, 6.0 GB; largest 2.8 GB | copy, then `sqlite3 'file:<copy>?mode=ro&immutable=1'`; `strings -n 8` on `hex()`-unhexed blobs; `protoc --decode_raw` if installed (it is not here) |
| `conversations/<uuid>.pb` | Legacy conversations from before the move to SQLite | opaque, AES per AgentsView `antigravity_crypto.go:18-40`; incompressible | 6 files, 36 MB | not readable; use the matching `brain/<uuid>/` |
| `conversation_summaries.db` | One row per conversation: `title`, `preview`, `step_count`, `last_modified_time`, `workspace_uris`, `status` (`CASCADE_RUN_STATUS_IDLE`), `project_id`, `agent_name`, `parent_conversation_id`, `nesting_depth`, `not_fully_idle`, `killed`, `last_user_input_time`, `last_user_input_step_index`, `app_data_dir`. Also the FTS5 table `conversations_fts` (`title`, `workspace`, `project`, `user_body`, `agent_body`, with chunk step ranges and byte offsets) | SQLite + FTS5 | 4.4 MB; 247 summaries, FTS covers 35 conversations in 139 chunks | `sqlite3` with `MATCH` and `snippet()` |
| `brain/<uuid>/*.md` + `*.md.metadata.json` | Artifacts: named plans, reports, walkthroughs, `task.md` in older builds; metadata keys `summary`, `updatedAt`, `requestFeedback`, `userFacing`; older builds keep versions as `*.md.resolved` and `*.md.resolved.N` | Markdown, JSON | 247 dirs, 413 MB total | `rg`, `jq`; checkboxes via `rg -c '^\s*- \[x\]'` |
| `brain/<uuid>/.system_generated/logs/transcript_full.jsonl`, `transcript.jsonl`, `chunks/` | Step mirror, one JSON object per step: `step_index`, `source` (USER_EXPLICIT, MODEL, SYSTEM), `type` (USER_INPUT, PLANNER_RESPONSE, GENERIC, SYSTEM_MESSAGE, CHECKPOINT, ERROR_MESSAGE), `status`, `created_at`, `content`, `tool_calls[{name,args}]`, `thinking`, token counts, `error`. `transcript.jsonl` carries `truncated_fields`; `_full` does not | JSONL, plaintext | present in 241 of 247 brains; up to 150 MB per conversation | `jq`, `rg` |
| `brain/<uuid>/.system_generated/steps/<idx>/output.txt` | Tool outputs per step | text | 34 MB in one large conversation | `rg` |
| `brain/<uuid>/.system_generated/tasks/task-<idx>.log` | Background command logs (`run_command` async tasks) | text | 821 logs, 90 MB in one conversation | `tail`, `rg` |
| `brain/<uuid>/.system_generated/subagents/<id>.json` | `conversationId`, `subagentDescriptor{typeName, role}`, `state`, `spawnStepIndex`, `workspaceUris` | JSON | small | `jq` |
| `brain/<uuid>/.system_generated/messages/<uuid>.json`, `read.json`, `undelivered/` | Inter-agent and system messages: `sender`, `recipient`, `priority`, `timestamp`, `hideFromUser`, `content` (subagent reports, the "server restart" notice) | JSON | 806 files, 6.8 MB in one conversation | `rg -l '"sender": *"<child-id>'`, `jq` |
| `brain/<uuid>/.tempmediaStorage/`, `.user_uploaded/`, `scratch/` | Screenshots, uploads, agent scratch | binary, any | varies | `ls` |
| `annotations/<uuid>.pbtxt` | `last_user_view_time`, flags | text protobuf | 53 files, 212 KB | `rg` |
| `agyhub_summaries_proto.pb` | Summaries mirror including subagent type, role and parent | binary protobuf | 204 KB | `strings` |
| `antigravity_state.pbtxt`, `user_settings.pb` | Onboarding, last selected model, settings | text and binary protobuf | 1 KB, 24 B | `cat`, `xxd` |
| `knowledge/<topic>/{metadata.json,timestamps.json,artifacts/**/*.md}` | Knowledge items | JSON, Markdown | 368 KB | `rg`, `jq` |
| `implicit/<uuid>.pb` | Implicit context | encrypted per AgentsView `antigravity.go:24` | 5.7 MB | not readable |
| `code_tracker/active/<repo>_<sha>/` | File snapshots the agent tracked | files | 392 KB | `rg` |
| `mcp/<server>/`, `plugin_data/<plugin>/`, `builtin/skills/`, `cache/marketplaces/`, `bin/` | MCP catalogs, plugin state, built-in skills, marketplace cache, helper binaries | mixed | small to 12 MB | skip `bin/`; never read tokens (below) |

### 6.2 Sibling roots

- `~/.gemini/antigravity-cli/` (the `agy` CLI): the same layout, 178 conversations (254 MB of
  `.db`), brain 2.2 GB, `history.jsonl` (REPL input lines: `display`, `timestamp`, `type`,
  `workspace`), `log/cli-*.log`, `jetbox_summaries_proto.pb`, and a summaries db with no FTS table.
  txcript's format doc describes this CLI store (mirror `pages/txcript-antigravity-format.md`).
- `~/.gemini/antigravity-ide/` (56 MB) and `~/.gemini/antigravity-backup/` (43 MB): copies the
  July upgrade wizard made (`~/Library/Logs/Antigravity/main.log:2-3`).
- `~/Library/Application Support/Antigravity/`: the Electron user-data directory. It holds
  `app_storage.json` (UI layout keyed by conversation id, pinned order, last project), Chromium
  stores, and the old VS Code-fork layout `User/globalStorage/state.vscdb` (SQLite `ItemTable`
  with protobuf values; last written in April here) and `logs/` (April and earlier).
- `~/Library/Logs/Antigravity/main.log`, `language_server.log`: current app and language server
  logs (version, port, errors).

### 6.3 Secrets and private content (never read or copy)

`~/.gemini/jetski-standalone-oauth-token`, `oauth_creds.json`, `mcp-oauth-tokens-v2.json`, and
`plugin_data/<plugin>/token.json` (doubleagent research doc, section 6, mirror
`repos/seanthegeek_doubleagent/analyzer/research/antigravity.md:535-548`). Transcripts, `steps/*/output.txt`,
`tasks/*.log`, `gen_metadata` (full prompts with file contents) and the FTS bodies contain whatever
the agent read. Write digests to a scratch directory and cite paths.

### 6.4 Behaviours that matter for a reader

- The mirror can leave steps out. In one 22,233-step conversation, `transcript_full.jsonl` had
  22,221 lines and was missing the closing `ERROR_MESSAGE` steps (`steps.step_type` 17), each of
  them a 429 "Individual quota reached" body with model and reset time. Liveness has to come from
  the database. Sessions Viewer also reports that both files are rewritten and truncated at
  checkpoints (mirror `pages/sessions-viewer-agy-cli.md:81-87`).
- The FTS index is lazy: it covers 35 of 247 conversations. Use `rg` over the mirrors to cover the
  rest.
- Summaries can lag the database, and conversations missing from the index are never shown in
  the UI (ClawMetry, mirror `pages/clawmetry-antigravity.md:76-83`; antigravity-cli#727).
- Subagents are full conversations with their own brain dirs. The parent edge is in
  `conversation_summaries.parent_conversation_id`, in `subagents/*.json`, and in the child's
  report message under the parent's `messages/`.
- Plan approval shows up as a USER_INPUT step whose content begins "Comments on artifact URI:
  file://…/brain/<uuid>/<name>.md" and contains "The user has approved this document."
- Step types (doubleagent research doc, `analyzer/research/antigravity.md:280-330`): 14
  USER_INPUT, 15 PLANNER_RESPONSE, 132 GENERIC, 17 ERROR_MESSAGE, 101 SYSTEM_MESSAGE, 23
  CHECKPOINT; status 3 DONE, 7 ERROR.

## 7. Search recipes (system tools only)

```sh
AG=~/.gemini/antigravity; S=<scratch>          # also try ~/.gemini/antigravity-cli
# 0. Snapshot before reading: never open the live file. Include -wal/-shm when present.
cp -p "$AG"/conversation_summaries.db* "$S"/
RO() { sqlite3 -readonly "file:$1?mode=ro&immutable=1" "$2"; }
# 1. Resolve: newest conversations for a workspace, or by title
RO "$S/conversation_summaries.db" "select conversation_id,title,step_count,status,last_user_input_time,
  parent_conversation_id from conversation_summaries where workspace_uris like '%<repo-substring>%'
  order by last_modified_time desc limit 20"
# 2. Full text (indexed conversations only); column 14 is agent_body, 13 is user_body
RO "$S/conversation_summaries.db" "select conversation_id,chunk_first_step,chunk_last_step,
  snippet(conversations_fts,14,'[',']','…',12) from conversations_fts
  where conversations_fts match 'agent_body:<term>' order by rank limit 10"
rg -l '<term>' "$AG"/brain/*/.system_generated/logs/transcript_full.jsonl   # covers the rest
# 3. Turns: user prompts, turn-final messages, approvals
T="$AG/brain/<id>/.system_generated/logs/transcript_full.jsonl"
jq -r 'select(.type=="USER_INPUT")|"\(.step_index)\t\(.created_at)\t\(.content|gsub("\n";" ")|.[0:200])"' "$T"
jq -r 'select(.type=="PLANNER_RESPONSE" and (.content//"")!="")|"\(.step_index)\t\(.created_at)\t\(.content|.[0:300])"' "$T"
# 4. Write-like calls and commands
jq -r 'select(.tool_calls)|.step_index as $s|.tool_calls[]|select(.name|test("write_to_file|replace_file_content|run_command"))
  |"\($s)\t\(.name)\t\(.args.TargetFile // .args.CommandLine)"' "$T"
# 5. Liveness and errors the mirror omits (copy the conversation db first)
cp -p "$AG/conversations/<id>.db"* "$S"/
RO "$S/<id>.db" "select idx,step_type,status from steps order by idx desc limit 10"
RO "$S/<id>.db" "select hex(step_payload) from steps where idx=<n>" | xxd -r -p | strings -n 8 | head
# 6. Artifacts, versions, checkboxes, subagents, background tasks
for f in "$AG"/brain/<id>/*.md.metadata.json; do jq -r '"\(.updatedAt) \(input_filename)"' "$f"; done | sort
rg -c '^\s*- \[x\]' "$AG"/brain/<id>/task.md; ls "$AG"/brain/<id>/*.resolved.* 2>/dev/null
jq -r '[.conversationId,.subagentDescriptor.role,.state,.spawnStepIndex]|@tsv' "$AG"/brain/<id>/.system_generated/subagents/*.json
tail -c 600 "$AG"/brain/<id>/.system_generated/tasks/task-<idx>.log
```

## 8. Skill design: `antigravity-session-history`

It mirrors `codex-session-history` (`.claude/skills/codex-session-history/SKILL.md:1-63`, kept
identical under `.agents/skills/`).

1. **Name and location.** `.claude/skills/antigravity-session-history/` and the same tree under
   `.agents/skills/antigravity-session-history/`, changed together (`.claude/AGENTS.md`). Built with
   `/skill-creator` per D153.
2. **Triggers (description).** Retrieve what a Google Antigravity (desktop app, IDE or `agy` CLI)
   conversation did from its native records (conversation SQLite, summaries and FTS index, brain
   artifacts, JSONL step mirror, subagent and background-task records, messages, logs). Fire when a
   task mentions Antigravity, `agy`, `~/.gemini/antigravity*`, a `brain/<uuid>` path, an Antigravity
   plan or artifact, "what was Antigravity doing", a takeover from Antigravity, an Antigravity quota
   stop, or a Claude agent resuming or auditing Antigravity work.
3. **Inputs.** A conversation id or prefix, a title fragment, a workspace path substring, or a
   search term; optional `--days` and data root (default `~/.gemini/antigravity`, then
   `-cli`, `-ide`, `-backup`).
4. **Steps, matching the codex skill's six.** (1) Resolve the conversation through the summaries db
   copy and FTS, then `rg` for unindexed ones. Done when you can name the db, the brain dir and the
   workspace. (2) Establish liveness from `status`, `not_fully_idle`, `killed`, the last steps in
   the db (error type 17 with the 429 body and reset time), the system-restart notice in
   `messages/`, and a running app (`pgrep -fl Antigravity`). The result is running,
   stopped-clean or stopped-failed. (3) Digest the mirror into `<scratch>/<id>.md` with the jq
   recipes: user prompts, `ask_question` answers, turn-final messages, approvals, write-like calls,
   commits, errors. Hand a large digest to a synthesizer with the brief template.
   (4) Pull artifacts and receipts: `*.md` with metadata `updatedAt` and SHA-256, `.resolved.N`
   versions, `task.md` checkbox counts, `subagents/*.json`, child reports in `messages/`, and
   `tasks/*.log` tails. (5) Cross-check the workspace's Git state read-only and, when the archive
   has Antigravity rows, AgentsView. (6) Report with `[created_at step=N]`, keeping proposed apart
   from approved, and saying "not observed" when a record is missing.
5. **Outputs.** A bounded digest in scratch and an eight-section brief. Reuse
   `codex-session-history/references/brief-template.md` with "step" in place of "ord".
6. **Receipts.** Every claim carries `[created_at step=N]`. Artifacts carry path, `updatedAt` and
   SHA-256. Each db copy records source mtime and SHA-256. The report records the mirror-versus-db
   step count difference and quotes quota errors with model and reset timestamp. A missing record
   reads "not observed".
7. **Files.** `SKILL.md`, `references/sources.md` (section 6 of this report), `references/recipes.md`
   (section 7), `evals/evals.json` with three prompts: liveness and last turns of a conversation
   that hit a quota stop; a takeover brief with artifacts and approvals; and a search across
   conversations for a term, using FTS plus `rg` and reporting the index coverage. No `scripts/`:
   the classification is config and existing tools, so it is allowed now (D112/D113).
8. **Parser boundary: a C++ ticket.** Propose "CT: Antigravity trajectory reader in the C++ core".
   Open a copied conversation db read-only through the SQLite C API. Walk `steps.step_payload` and
   `gen_metadata.data` with a bounded protobuf wire walker (field numbers from the doubleagent
   research doc and AgentsView `antigravity_proto.go`). Emit JSONL in the mirror's schema for steps
   the mirror lacks, plus token usage. Acceptance: on a corpus copy, every `steps.idx` appears once,
   error steps carry their user message, and no write reaches `~/.gemini`. A thin bridge calls it.
   Until it lands, the skill uses `strings` on single blobs, or `protoc --decode_raw` where protoc
   is installed.
9. **Safety rules in SKILL.md.** Copy before you open; `mode=ro&immutable=1` (a copy whose `-wal` is non-empty: `immutable=1` skips the WAL, so reread the scratch copy with `?mode=ro`, skill recipe 0); never start the app or
   `agy` (antigravity-cli#1006); never read token files; digests stay in scratch.
10. **AgentsView.** The codex skill's sources table says the archive imports Antigravity
    (`.claude/skills/codex-session-history/references/sources.md:20`), and AgentsView 0.45.0 has
    Antigravity parsers (`internal/parser/antigravity.go:19-24`). Even so, this machine's archive
    returned no rows for `agentsview_search.py search harvester --agent antigravity --since 30d`
    (rc 0, lexical mode). Enabling Antigravity ingestion is an existing-tool config change and needs
    its own admission under AGENTS.md.

## 9. Code examples found

| Repository | Path | Commit or link | What it shows |
|---|---|---|---|
| kenn-io/agentsview | `internal/parser/antigravity.go:19-24, 396-398`; `antigravity_proto.go:10-14`; `antigravity_crypto.go:18-40`; `antigravity_brain_transcript.go:16-30` | `dcdad6139bb3db00a2671e040a0e949edc143bf7` | Go: IDE store layout, `SELECT idx, step_type, step_payload FROM steps`, generic wire walker, legacy `.pb` AES, mirror schema |
| seanthegeek/doubleagent | `analyzer/research/antigravity.md:147-171, 263-330, 443-548`; `analyzer/doubleagent/parsers/antigravity.py` | `a124dee9f61b91f806029c67f0d6f1861bc71aba` | Store table, SQL schema, step and status enums, payload field numbers, secrets |
| mjacobs/agy-reader | `README.md:1-40`; `skills/agy-format-audit/SKILL.md` | `fd9df25e2a596d4910f8954a0949bfb4316b214b` | Daemon-RPC sidecar reader and a format-audit skill. It says CLI stores are AES-GCM at rest, which this install's desktop db contradicts (Verdict item 1) |
| xhluca/antigravity-session-interoperability | `docs/`, `scripts/` | `b85c60a1eacd44808fa7b1cffc343e4af936df9d` | Observed schema notes and a synthetic fixture generator (standard library only) |
| stablyai/orca | `src/main/ai-vault/antigravity-index-reader.ts`, `antigravity-transcript-candidates.ts` | PR #24692, merged 2026-10-02 | TypeScript discovery of three roots and both transcript names |
| Chatixia-AI/interlatch | `antigravity_parser.py` | PR #14, merged 2026-10-02 | Python reader of `transcript_full.jsonl` that never writes to `~/.gemini` |

## 10. Routes table

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| preflight | Firecrawl credits | `fnox … exec -- firecrawl credits --json` | 0 | -128 credits | SKIPPED |
| preflight | Serper, SerpApi accounts | `curl` with key from env | 0, 0 | 1307, 245 | yes |
| preflight | GitHub | `gh api rate_limit`; `gh api repos/<r>` (9 repos) | 0 | n/a | yes |
| 1 | Exa | `fnox … exec -- bash -c 'curl … https://api.exa.ai/search'` x3 | 0 | 10 each | yes |
| 1 | Context7 | `fnox … exec -- ctx7 library antigravity …` | 1 | quota | gap |
| 1 | Firecrawl | not called | n/a | n/a | gap |
| 1 | Serper | `curl https://google.serper.dev/search` x3 | 0 | 2, 10, 0 | yes |
| 1 | webclaw | `fnox … exec -- webclaw <url> -f markdown` x11 | 0 | 11 pages | yes |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fnox … exec -- python3 -I last30days.py … --plan` | 0 | 13 | 2 used |
| 2 | gh issues, PRs, views | `gh search issues|prs`, `gh issue view --comments`, `gh pr view` | 0 | see section 3 | yes |
| 2 | GraphQL discussions | `gh api graphql` type DISCUSSION x2 | 0 | 15, 7 | no |
| 2 | Clones | `git clone --filter=blob:none` x4 | 0 | 4 | yes |
| 2 | Saved searches | `gh api -X GET search/code` x8 (4 queries + 4 controls) | 0 | section 4 | yes |
| local | SQLite | `cp -p` then `sqlite3 'file:…?mode=ro&immutable=1'` | 0 | schemas, rows | yes |
| local | JSONL, files | `jq`, `rg`, `strings`, `du`, `stat`, `gzip -c \| wc -c` | 0 | n/a | yes |
| local | AgentsView | `python3 -I …/agentsview_search.py search harvester --agent antigravity --since 30d` | 0 | 0 | gap |
| local | protoc | `which protoc` | 1 | not installed | gap |

## 11. Open gaps

- Context7 hit its monthly quota and Firecrawl had no credits, so neither returned anything. Serper
  and webclaw covered the web route. Last30Days' Reddit source was partial.
- No official Antigravity documentation of the storage format exists; the docs cover only
  conversation management (mirror `pages/agy-cli-conversations.md`). Everything in section 6 is
  either observed on this machine or reverse-engineered by third parties, and may drift between
  releases.
- The local AgentsView archive has no Antigravity rows. Why (root configuration or the archive's
  remote mode) was not established, because `agentsview doctor` was not run.
- `protoc` is not installed, so `--decode_raw` could not be tried.
- The encryption claim for `.db` stores in the agy-reader README was not tested against an `agy`
  CLI store; only the desktop store was checked.
- The meaning of `conversations_fts` chunk coverage (which conversations get indexed, and when)
  is UNVERIFIED.
