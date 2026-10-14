# Antigravity search recipes

System tools only (`sqlite3`, `jq`, `rg`, `find`, `xxd`, `strings`, `shasum`;
macOS `stat -f`). Paste the setup block first; every later recipe assumes
`AG`, `S`, `RO` and `snap`, and recipes 4-6 reuse `T` from recipe 3.
Placeholders: `<id>` a full conversation id, `<n>` a step index, `<term>` a
search term, `<repo-substring>` part of a workspace path. Long outputs go to
`$S`, not to the conversation.

## 0. Setup and snapshot

```sh
AG=~/.gemini/antigravity        # the agy CLI: ~/.gemini/antigravity-cli
S=<scratch>/agy/$(basename "$AG"); mkdir -p "$S"   # one scratch dir per root, outside the repository
RO() { sqlite3 -readonly "file:$1?mode=ro&immutable=1" "$2"; }
# snap <live-db>: copy it with -wal/-shm into $S and append a receipt line
snap() { for f in "$1" "$1-wal" "$1-shm"; do [ -e "$f" ] && cp -p "$f" "$S"/; done
  b="$S/$(basename "$1")"
  printf '%s src_mtime=%s sha256=%s wal_bytes=%s\n' "$1" "$(stat -f %Sm -t %FT%T%z "$1")" \
    "$(shasum -a 256 "$b" | cut -c1-64)" "$(stat -f %z "$b-wal" 2>/dev/null || echo 0)" \
    | tee -a "$S/snapshots.txt"; }
snap "$AG/conversation_summaries.db"
```

`wal_bytes` above 0 means the immutable read below misses the newest
transactions (an immutable open skips the WAL). Take those steps from the
mirror; when only the database has them, rerun the query on the scratch copy
as `sqlite3 -readonly "file:$S/<file>?mode=ro"`.

## 1. Resolve a conversation

```sh
RO "$S/conversation_summaries.db" "select conversation_id, title, step_count, killed, nesting_depth,
  parent_conversation_id, last_modified_time, workspace_uris from conversation_summaries
  where workspace_uris like '%<repo-substring>%'   -- or title like '%<fragment>%' / conversation_id like '<prefix>%'
  order by last_modified_time desc limit 20"
# subagents of one conversation (each is a conversation with its own db and brain dir)
RO "$S/conversation_summaries.db" "select conversation_id, step_count, last_modified_time
  from conversation_summaries where parent_conversation_id = '<id>' order by last_modified_time"
ls -la "$AG/conversations/<id>".*; ls -a "$AG/brain/<id>"
```

## 2. Search across conversations, with coverage

Run this block once per root: set `AG` and `S` (recipe 0) for
`~/.gemini/antigravity`, then again for `~/.gemini/antigravity-cli`, whose
summaries database has no `conversations_fts` table (skip the index queries
there). `-ide` and `-backup` hold older copies of desktop conversations.

```sh
# full-text index: only the conversations it covers; -1 lets snippet pick the matching column
RO "$S/conversation_summaries.db" "select conversation_id, chunk_first_step, chunk_last_step,
  snippet(conversations_fts, -1, '[', ']', '…', 10) from conversations_fts
  where conversations_fts match '<term>' order by rank limit 30"
#   column filter: match 'agent_body:<term>' or 'user_body:<term>'; quote punctuation: match '"pre-commit"'
RO "$S/conversation_summaries.db" "select distinct conversation_id from conversations_fts
  where conversations_fts match '<term>'" | sort > "$S/fts.ids"
# mirrors cover the rest (.system_generated is hidden, hence --hidden)
rg -l -i --hidden -g transcript_full.jsonl -- '<term>' "$AG/brain" \
  | sed -E 's|.*/brain/([^/]+)/.*|\1|' | sort > "$S/rg.ids"
comm -13 "$S/fts.ids" "$S/rg.ids"                 # found only through the mirrors
rg -l -i -g '*.md' -- '<term>' "$AG/brain"        # artifacts (plans, walkthroughs)
rg -l -i --hidden -g output.txt -g 'task-*.log' -- '<term>' "$AG/brain" \
  | sed -E 's|.*/brain/([^/]+)/.*|\1|' | sort -u   # tool outputs and background-task logs
# coverage line: indexed / summaries / mirrors present
RO "$S/conversation_summaries.db" "select (select count(distinct conversation_id) from conversations_fts),
  (select count(*) from conversation_summaries)"
find "$AG/brain" -path '*/.system_generated/logs/transcript_full.jsonl' | wc -l
find "$AG/conversations" -name '*.pb' | wc -l      # legacy conversations: no mirror, no database
# a legacy conversation's only transcript text: the index content (partial; c13 user, c14 agent)
RO "$S/conversation_summaries.db" "select c2, c3, length(c13), length(c14) from conversations_fts_content
  where c0 = '<id>' order by c1"
# where in one conversation: matching steps
jq -c 'select(tostring|test("<term>";"i"))|{step_index,type,created_at}' "$AG/brain/<id>/.system_generated/logs/transcript_full.jsonl" | head
```

## 3. Turns: prompts, answers, turn-final messages, approvals, errors

```sh
T="$AG/brain/<id>/.system_generated/logs/transcript_full.jsonl"
wc -l < "$T"; tail -1 "$T" | jq -c '{step_index,type,created_at}'
jq -r .type "$T" | sort | uniq -c                 # step mix; builds differ (see sources.md)
# user prompts
jq -r 'select(.type=="USER_INPUT")|"\(.step_index)\t\(.created_at)\t\(.content//""|gsub("\\s+";" ")|.[0:200])"' "$T"
# answers to ask_question ("A1: …")
jq -r 'select(.type=="ASK_QUESTION")|"\(.step_index)\t\(.created_at)\t\(.content//""|gsub("\\s+";" ")|.[0:300])"' "$T"
# turn-final messages: the last non-empty PLANNER_RESPONSE before each USER_INPUT and at the end
jq -rn 'foreach ((inputs|select(.type=="USER_INPUT" or (.type=="PLANNER_RESPONSE" and (.content//"")!=""))), {type:"END"}) as $s
  ({last:null, out:null}; if $s.type=="PLANNER_RESPONSE" then {last:$s, out:null} else {last:null, out:.last} end;
  .out // empty | "\(.step_index)\t\(.created_at)\t\(.content|gsub("\\s+";" ")|.[0:300])")' "$T"
# plan approvals, then artifact comments that are not approvals
jq -r 'select(.type=="USER_INPUT" and ((.content//"")|test("has approved this document")))
  |"\(.step_index)\t\(.created_at)\t\(.content|capture("artifact URI: (?<u>\\S+)").u)"' "$T"
jq -r 'select(.type=="USER_INPUT" and ((.content//"")|startswith("Comments on artifact URI"))
  and ((.content|test("has approved this document"))|not))|"\(.step_index)\t\(.created_at)\t\(.content|gsub("\\s+";" ")|.[0:300])"' "$T"
# errors the mirror kept
jq -r 'select(.type=="ERROR_MESSAGE")|"\(.step_index)\t\(.created_at)\t\((.error//.content//"")|tostring|gsub("\\s+";" ")|.[0:200])"' "$T"
# context fill of the last model call (near the model's window means a resume starts with a summary)
jq -rn 'reduce (inputs|select(.type=="PLANNER_RESPONSE" and .input_tokens)) as $s (null; $s)
  |"\(.step_index)\t\(.created_at)\tcontext≈\((.input_tokens // 0) + (.cache_read_tokens // 0)) tokens"' "$T"
```

## 4. Write-like calls, commands, commits

Tool calls sit on `PLANNER_RESPONSE` steps (`tool_calls[{name,args}]`); the
next step holds the result.

```sh
jq -r 'select(.tool_calls)|.step_index as $s|.created_at as $t|.tool_calls[]
  |select(.name|test("^(write_to_file|replace_file_content|multi_replace_file_content|run_command)$"))
  |"\($s)\t\($t)\t\(.name)\t\((.args.TargetFile // .args.CommandLine // "")|gsub("\\s+";" ")|.[0:200])"' "$T"
# git and gh commands, then the commit lines git printed ("[branch sha] subject")
jq -r 'select(.tool_calls)|.step_index as $s|.created_at as $t|.tool_calls[]|select(.name=="run_command")
  |(.args.CommandLine // "")|select(test("\\bgit (commit|push|merge|tag)\\b|\\bgh pr "))|"\($s)\t\($t)\t\(gsub("\\s+";" ")|.[0:200])"' "$T"
jq -r 'select(.type!="PLANNER_RESPONSE")|.step_index as $s|.created_at as $t|(.content//"")
  |[match("\\[[^]\\s]+ ([0-9a-f]{7,40})\\] [^\\n]{0,100}";"g").string][]|"\($s)\t\($t)\t\(.)"' "$T"
```

## 5. Liveness and the steps the mirror omits

```sh
snap "$AG/conversations/<id>.db"
RO "$S/<id>.db" "select idx, step_type, status, length(step_payload) from steps order by idx desc limit 12"
# steps only the database holds (the mirror can drop the closing errors)
jq -r .step_index "$T" | sort -u > "$S/<id>.mirror.idx"   # the mirror can repeat an index
RO "$S/<id>.db" "select idx from steps" | sort > "$S/<id>.db.idx"
wc -l < "$T"; wc -l < "$S/<id>.mirror.idx"; wc -l < "$S/<id>.db.idx"   # lines, unique steps, db steps
comm -13 "$S/<id>.mirror.idx" "$S/<id>.db.idx" | sort -n | tr '\n' ' '; echo
# decode one step; a quota stop names model, reason, reset time and the HTTP date
RO "$S/<id>.db" "select hex(step_payload) from steps where idx=<n>" | xxd -r -p | LC_ALL=C strings -n 8 \
  | grep -oE 'RESOURCE_EXHAUSTED[^.]*\.|"(model|quotaResetTimeStamp|quotaResetDelay|reason)": *"[^"]*"|"Date":\["[^"]*"' | sort -u
# which phase each recent execution failed in ("pre-invocation hook: context summarization" = a full context)
for r in $(RO "$S/<id>.db" "select idx from executor_metadata order by idx desc limit 4"); do
  printf '%s\t' "$r"; RO "$S/<id>.db" "select hex(data) from executor_metadata where idx=$r" | xxd -r -p \
    | LC_ALL=C strings -n 8 | grep -o -E 'execution error: [^.]{0,120}' | head -1; echo; done
# summaries row, restart notices, running app
RO "$S/conversation_summaries.db" "select status, killed, not_fully_idle, last_user_input_time,
  last_user_input_step_index, step_count, last_modified_time from conversation_summaries where conversation_id='<id>'"
rg -l 'stopped due to server restart' "$AG/brain/<id>/.system_generated/messages" \
  | xargs -I{} jq -r '.timestamp' {} | sort | tail -3
pgrep -fl 'Antigravity.app/Contents/(MacOS/Antigravity|Resources/bin/language_server)'
```

## 6. Artifacts, versions, checkboxes, subagents, background tasks

```sh
B="$AG/brain/<id>"
find "$B" -maxdepth 1 -name '*.md' | sort | while read -r f; do
  printf '%s\t%s\t%s\t%s\n' "$(jq -r '.updatedAt // "-"' "$f.metadata.json" 2>/dev/null)" \
    "$(jq -r '.requestFeedback // false' "$f.metadata.json" 2>/dev/null)" \
    "$(shasum -a 256 "$f" | cut -c1-64)" "$f"; done
find "$B" -maxdepth 1 -name '*.resolved*' | sort                 # versions (older builds)
# versions (newer builds): every write to a brain artifact, with its step and first line
jq -r 'select(.tool_calls)|.step_index as $s|.created_at as $t|.tool_calls[]
  |select((.name|test("^(write_to_file|replace_file_content|multi_replace_file_content)$"))
    and ((.args.TargetFile // "")|test("/brain/[^/]+/[^/]+\\.md$")))
  |"\($s)\t\($t)\t\(.name)\t\(.args.TargetFile|split("/")|last)\t\((.args.CodeContent // .args.ReplacementContent // "")|split("\n")[0]|.[0:80])"' "$T"
[ -f "$B/task.md" ] && echo "done $(grep -cE '^[[:space:]]*- \[x\]' "$B/task.md") open $(grep -cE '^[[:space:]]*- \[ \]' "$B/task.md")"
find "$B/.system_generated/subagents" -name '*.json' -exec \
  jq -r '[.conversationId,.subagentDescriptor.typeName,.subagentDescriptor.role,.state,.spawnStepIndex]|@tsv' {} +
rg -l '"sender": *"<child-id>' "$B/.system_generated/messages"   # a child's reports to the parent
ls -t "$B/.system_generated/tasks" | head -5; tail -c 600 "$B/.system_generated/tasks/task-<n>.log"
```
