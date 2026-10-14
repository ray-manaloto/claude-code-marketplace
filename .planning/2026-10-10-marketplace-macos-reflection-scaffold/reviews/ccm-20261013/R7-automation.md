# R7: automation candidates for session ccm-20261013

Reviewer R7, 2026-10-13, read-only. Question: which commands, record edits and
agent briefs that the session ran by hand should become mise tasks, scripts,
skills, agent definitions or hooks, so the next session spends its tokens on
judgement rather than bookkeeping. Transcript contents are treated as data.
Byte counts are UTF-8 characters of tool input plus tool result. Token figures
are bytes/4 and measure context occupancy, not billed tokens.

## Scope read

- Main transcript `464a2816-…jsonl` (2045 lines), checked with `python3 -I`
  extractors. Tool counts match the index: Bash 113, Write 34, Edit 6, Agent 27,
  SendUserMessage 30, SendMessage 13. I extracted every Bash command, Agent
  prompt and Write/Edit path. The parent's context, from assistant `usage`, went
  from 53 K tokens at 18:54Z to 490 K at 19:17Z (orientation and Codex
  forensics), to 698 K at 20:00Z and 977 K at 21:02Z, and died at 21:30Z.
- Subagent transcripts. Implementers: `a9a11665` (A06u3), `aa49b9b1`
  (gate-hooks), `a85dc4eb` (retro-gate). Reviewers: `a221b354` (gate-hooks),
  `a623306f` (NAV). Merger forks: `a9809447` and `a22113b3`. Handoff writer:
  `a162b749`.
- Existing automation:
  - `mise.dev.toml` (`./dev/mise tasks ls`; definitions of `check`,
    `check:research`, `retro:gate*`, `hooks:install`, `test:hooks`,
    `delivery:*`, `issue:*`, `tools:prepare`, `deps:sync`)
  - `dev/retro_gate.py`, `dev/check.py`
  - the staged hook scripts `dev/hooks/{git_gate,pretooluse_gate,stop_gate,subagent_stop_gate}.py`,
    `hk.pkl` and the staged `.claude/settings.json`
  - `.claude/agents/*.md`, `.claude/rules/planning-records.md`,
    `.claude/skills/codex-session-history/`
  - `docs/agents/claude-team.md`, `claude-takeover.md:11`,
    `codex-task-orchestration.md#ownership`, `ticket-retro.md`
  - `proposals/claude-takeover-spec/tickets.preview.json` (CT-01…CT-11)
  - the memory note `marketplace-workflow-rules.md`
- Claude Code documentation, fetched 2026-10-13:
  - [hooks](https://code.claude.com/docs/en/hooks): SubagentStop input carries
    `agent_id`, `agent_type`, `agent_transcript_path` and
    `last_assistant_message`; its matcher matches the agent type. PostToolUse
    input carries `tool_input.file_path`, and the hook can return
    `decision: "block"`. The `if` field in permission-rule syntax filters by
    arguments; the docs call it "best-effort".
  - [skills](https://code.claude.com/docs/en/skills): `disable-model-invocation`,
    `argument-hint`, `context: fork` + `agent`, `$0`/`$1` arguments, and
    `` !`cmd` `` dynamic context injection.
  - [sub-agents](https://code.claude.com/docs/en/sub-agents): the frontmatter
    `hooks` field exists (a `Stop` hook becomes SubagentStop). `isolation:
    worktree` branches "from your default branch rather than the parent
    session's HEAD".

## Pattern measurements

Parent session only, unless the Source column says otherwise. "Calls" counts
tool calls that contain the pattern. One Bash call often chains several
patterns, so rows overlap.

| # | Pattern (manual form) | Calls / uses | Context cost | Source |
|---|---|---|---|---|
| P1 | **Lane-record patching**: `python3 -I - <<EOF … json.loads(lanes/<u>.json) … d['status']=…` and `cat > $PL/lanes/<u>.json <<EOF` | 22 calls (17 patches, 4 creates, 4 Write) | ≈18 K tok (65 KB in) | parent. Merger `a9809447` adds 2 calls, ≈1.7 K |
| P2 | **Ledger row edits**: `t.replace("<old row text>","<new>")` on `ticket-ledger.md`, with no assertion that the old text matched | 13 calls | ≈11.6 K tok | parent and `a9809447` (+2.2 K) |
| P3 | **Progress appends**: `cat >> $PL/progress.md <<'EOF'` | 18 calls | ≈15.7 K tok | parent and `a9809447` (4 calls, +4 K) |
| P4 | **Integration sequence**: status filter → `git merge --no-ff --no-commit <lane>` → `tasks validate` → `check` → `check:acceptance-baseline` → (`check:research`) → `git diff --cached --check` → `retro:gate` → lane/ledger/progress patch → `git -c user.name=… commit -F - <<EOF … trailers` | 6 merges in the parent and 3 in forks; named-gate calls 36 (≈27.5 K tok); commits with trailers 23 (≈17.7 K tok) | ≈5 K tok per integration across about 4 calls | parent, `a9809447`, `a22113b3` (died after merge rc 0) |
| P5 | **A09 publish**: compute `remote_url_sha256`, hard-code `hook_tree_sha256`, build the prepare intent → `shasum` → `delivery:prepare` → parse `index_tree` → build the publish intent and message → `shasum` → `delivery:publish` → `ls-remote` | 4 publishes, 8 parent calls plus 2 fork calls | ≈8.5 K + 2.3 K tok; one call alone is 5.4 KB of script (bash #94) | parent, `a9809447` |
| P6 | **Worktree allocation**: write the lane JSON → commit → `git worktree add -b claude/<u> .claude/worktrees/<u> HEAD` → (lane runs `tools:prepare && deps:sync`) | 8 lanes, 6 parent calls | ≈5.2 K tok in the parent, plus 2–3 prep calls per implementer | parent, implementers |
| P7 | **Implementer and doc-writer dispatch briefs**: role, worktree, allowlist, read-first list, environment, gates, trailer lines, merge of the tip, handoff format, seven-category retro draft | 8 briefs, 4.2–6.8 KB each (mean 5.3 KB) | ≈10.6 K tok | parent |
| P8 | **Cold-review dispatch briefs**: role, read-only, worktree, SHAs, owned paths, implementer claims, standards/spec axes, reruns, P1/P2/P3 scale, word cap | 9 briefs, 3.4–6.0 KB (mean 4.0 KB) | ≈9.1 K tok | parent |
| P9 | **Brief boilerplate** shared across the 17 lane briefs | "no spawn" 17/17, "never push" 17/17, baseline gate 17/17, `diff --check` 16/17, word cap 16/17, lane-record path 15/17, `tasks validate` 15/17, `VIRTUAL_ENV` 12/17, P1/P2/P3 scale 9/17, trailers 8/17, tip merge 8/17, seven retro categories 6/17 | ≈55% of 78.9 KB (estimate) | none of the 17 used `subagent_type: implementer/doc-writer/reviewer`. All were `general-purpose`, including 6 dispatched after the team lane integrated the definitions (20:25Z) |
| P10 | **Retro writing and disposition appends**: Write `retros/<u>.md` and `cat >> retros/<u>.md` | 5 Writes and 3 appends | ≈9.3 K tok | parent |
| P11 | **Status probe**: `git log --oneline -N && git status --short \| grep -v '^?? \.\(agent\|agents\|claude\)/$' …` | 5 standalone; the filter appears in 17 commands in 3 drifting variants | ≈3 K tok | parent (bash #110, #111, #113), merger forks |
| P12 | **Gate re-runs inside lanes**: `cd <worktree> && unset VIRTUAL_ENV && …` | implementers: retro gate 16–17 calls (35–45 runs) per gate lane; unittest discovery 10–13; `cd` into the worktree 23–42 times; `unset VIRTUAL_ENV` 31× in `a85dc4eb` | most of each 0.4–1.3 MB subagent transcript | subagents |
| P13 | **Handoff block rewrite** to fit the planning-with-files windows (plan head 30/50 lines, progress tail 20) | 1 agent with 70 Bash calls, including search scripts `anneal.py`, `model*.py` and `final_search*.py` that fit line widths | 1.43 MB subagent transcript | `a162b749` |
| P14 | **Codex thread synthesis and forensics**: rollouts, `state_5.sqlite`, `logs_2.sqlite`, AgentsView, OTel, worktrees | 44 parent calls, plus 4 synthesis agents | ≈79 K tok in the parent, the largest single parent bucket; 1.1–1.7 MB per synthesis agent | parent, `af30d80a`, `a43833a6`, `acef1bdf`, `ae55d482` |
| P15 | **Tracker reads and manifest builds**: `gh issue view`, GraphQL dump, `build_manifests.py`, `issue_create`/`issue_edges` greps | 15 calls | ≈28 K tok | parent |
| P16 | **Hook-injected planning context**: planning-with-files `hook_additional_context` | 58 injections, 271 KB | ≈68 K tok | parent (an external plugin; its size follows the handoff block) |
| P17 | **This session review**: evidence index plus R1…R7 transcript extraction | R7 alone wrote 7 ad-hoc extractors (`ext.py`, `cost.py`, `feat*.py`, `pat.py`) | not measured | this session |

What the records show these patterns cost:

- **Off-by-one base SHAs.** For `c1-catalog-promotion`, `nav` and `gate-hooks`,
  the record's `base_sha` (`447110a`, `7e22d13`, `e618243`) is the parent of the
  commit the worktree was actually cut from (`ca60871`, `c6ff7ef`, `2d1f60e`).
  The heredoc evaluated `$(git rev-parse --short HEAD)` before the allocation
  commit. The C1 brief says base `ca60871` while its record says `447110a`. For
  `retro-gate` and `team`, the worktree was cut before the record was
  committed. The TEAM reviewer flagged this at line 1231: "The lane record sits
  only on the integration branch, not the base SHA."
- **Stale lane fields.** The staged `lanes/gate-hooks.json` says
  `"status": "implemented (Opus), awaiting cold review"` after the re-review
  passed, and has no `review` or `retro` field. `published` exists in 3 of 9
  records and `merged_head` is missing from `team`. Records carry the fields
  `lane_commit`, `merged_head`, `review`, `retro`, `published`, `holds`,
  `context` and `originating_retro`, none of which
  `.claude/rules/planning-records.md:7` lists. That rule also says "a lane
  changes only its own `status`", yet the parent patched records 22 times.
- **Stale handoff.** The handoff block injected into this review session says
  "focused re-review in progress" and "Handoff base: `28fedf1`". HEAD is
  `9cd396a`, and the re-review had passed (index row `a221b354`).
- **A merge left half-done.** Fork `a22113b3` ran `git merge --no-ff --no-commit
  claude/gate-hooks-wiring` (rc 0) and then died with `Prompt is too long`. The
  parent's probe at line 2031 showed `merge-in-progress: yes` and nothing
  recorded it. The staged `mise.dev.toml` still carries the uncommitted edit
  that adds `test:hooks` to `check:research`.
- **Unwired tests.** `test:hooks` was not in `check:research` until that
  uncommitted parent edit (gate-hooks retro P3 at line 20). Separately,
  `dev/test_retro_gate.py` is referenced by no mise task and is not discovered
  by `dev/check.py:72`, which covers only `test_research_*.py` and
  `research_refresh`. No named check runs it today.
- **Raced checks.** One `check:research` run raced another worktree's run,
  producing 15 `test:collect` errors and a stray `.a05b-8uuawcfh/` directory in
  the root (line 1369). NAV's first batch hit a transient `mise ERROR` (nav
  retro P3). CT-11 covers this.
- **Lanes not re-merged.** SKILL (`ea893a8`) and C1 (`6c09b7f`) were not merged
  again after the tip moved; nothing flags this.
- **The gate hook blocked this review.** With the staged
  `.claude/settings.json` live and `MERGE_HEAD` present, a read-only Bash call
  of mine was blocked. It was a heredoc whose text contained the words "merge"
  and "push": `PreToolUse:Bash hook error: … pretooluse_gate.py: timed out;
  blocking because onFailure is "block"`. `pretooluse_gate.py` splits heredoc
  bodies on newlines and treats any line starting `git merge` as an action.
  During an in-progress merge it then runs the retro gate. That exceeded the
  10 s timeout and failed closed. See Guardrails.

## Proposals

Each subsection covers the interface, where it lives, what it extends, what it
prevents and the ticket. All receipts are single-line JSON on stdout. Exit codes
follow `dev/retro_gate.py`: 0 pass, 2 refusal with one reason per stderr line,
1 usage error. Lane tooling lives in one new module, `dev/lane.py` with
`dev/test_lane.py`, behind mise tasks, so humans, Claude, Codex and CI run the
same code (the repository's mise-first convention).

### A. `lane:set` and `lane:validate`: a lane record with a schema and a single writer

- **Interface**:
  - `./dev/mise run lane:set -- <unit> <key>=<value>…`
    - Usage: `arg "<unit>"; arg "<assignments>" var=#true`.
    - Allowed keys: `status`, `lane_commit`, `merged_head`, `review.disposition`,
      `review.sha`, `review.agent`, `published`, `holds`.
    - `retro` cannot be set. It is derived: `passed` only when `retro_gate.py
      --unit <unit>` exits 0 on the current tree.
  - `./dev/mise run lane:validate` checks every `lanes/*.json` against the
    schema.
  - Receipt: `{"unit","changed":{k:[old,new]},"record_sha256","retro":"passed|pending"}`.
  - Exit 2 on an unknown key, a status outside the vocabulary prefixes in
    `claude-team.md`, or a `lane_commit` that is not a commit on `branch`.
- **Home**: `dev/lane.py set|validate`. The schema is a dict in the module,
  documented in `.claude/rules/planning-records.md:7`, which is updated to
  match the fields actually in use.
- **Extends**: CT-05 ("validates every lane record against its schema", named
  field on failure); reuses `git_gate.lanes()` for loading.
- **Prevents**: stale lane fields (the gate-hooks record); hand-typed
  `"retro": "passed"` that the gate never confirmed; JSON damaged by heredoc
  interpolation.
- **Saves**: about 800 → 100 tokens per edit, 24 edits per session (≈17 K).
- **Ticket**: fold into CT-05 (acceptance below).

### B. `lane:allocate`: record, commit, worktree and preparation in one step

- **Interface**:
  - Command: `./dev/mise run lane:allocate -- <unit> --ticket <ref>… --title <t>
    --owner implementer|doc-writer --model opus|sonnet --owned <path>…
    [--exclude <path>…] [--check <named-check>…] [--admit key=value…]
    [--slug <s>] [--no-prepare]`.
  - What it does:
    1. Refuses a dirty tree, an existing `MERGE_HEAD`, an existing worktree or
       branch, or `owned_paths` that overlap the `owned_paths` of any record
       still below `integrated`.
    2. Writes `lanes/<unit>.json` with `base_sha` set to the current tip and
       commits it as `docs: allocate lane <unit> (<ticket>)` with trailers from
       `$CLAUDE_TRAILERS_FILE`.
    3. Runs `git worktree add -b claude/<unit>-<slug>
       .claude/worktrees/<unit> <allocation_commit>` and records
       `allocation_commit` in the record.
    4. Runs `tools:prepare` and `deps:sync` inside the worktree unless
       `--no-prepare` is passed.
  - Receipt: `{"unit","branch","worktree","base_sha","allocation_commit","prep":{"tools_prepare":rc,"deps_sync":rc}}`.
- **Home**: `dev/lane.py allocate`.
- **Extends**: the schema from proposal A; `tools:prepare`, `deps:sync`; the
  ownership rule in `codex-task-orchestration.md#ownership` (disjoint scopes,
  one writer per worktree).
- **Prevents**: the off-by-one `base_sha` in three lanes; worktrees cut before
  their record exists (`retro-gate`, `team`); lanes running `check:research`
  without preparation (memory note); overlapping allowlists.
- **Saves**: about 1.5 K → 150 tokens per allocation, 8 per session.
- **Ticket**: new, CT-12 (below).

### C. `lane:integrate`: the integration sequence as one resumable task

- **Interface**:
  - Command: `./dev/mise run lane:integrate -- <unit> [--continue|--abort]
    [--message-file <f>] [--skip-check <name>]`. The task refuses `--skip-check`
    for `check`, the baseline and the retro gate.
  - Steps (the task refuses at any step, see exit codes):
    1. Preflight:
       - the current branch is `codex/marketplace-native-onboarding` (never
         `main`);
       - the tree is clean apart from known untracked paths;
       - `MERGE_HEAD` is absent, or with `--continue` names this lane's branch;
       - the record has `review.disposition` starting with `PASS`;
       - `retro_gate.py --branch <branch>` exits 0 against the lane tip.
    2. `git merge --no-ff --no-commit <branch>`.
    3. The changed paths must fit inside `owned_paths ∪ {lanes/<unit>.json,
       retros/<unit>.md}`; anything outside is listed and refused.
    4. Gates in this order, each exit recorded: `tasks validate`, `check`,
       `check:acceptance-baseline`, the record's `required_checks` that are
       named tasks (for example `check:research`), `git diff --cached
       --check`, then `retro:gate -- <unit>` on the composed tree.
    5. `lane:set <unit> status=integrated merged_head=<lane tip>`, which
       derives `retro=passed`.
    6. `ledger:sync` (CT-05), then `plan:log` (proposal F).
    7. Commit with a message template plus `$CLAUDE_TRAILERS_FILE`.
  - Receipt: `{"unit","merge_commit","gates":{name:rc},"paths_outside_allowlist":[],"record":{…},"next":"publish"}`.
  - Exit codes:
    - 0: integrated;
    - 2: refused before the merge, or a gate failed (the merge is left staged
      and the receipt names `--continue` or `--abort`);
    - 3: merge conflict (left in progress, conflicts listed);
    - 1: usage error.
  - Idempotence: a second run on an already-integrated unit exits 0 with
    `"noop": true`.
- **Home**: `dev/lane.py integrate`.
- **Extends**: `retro:gate`, `git_gate.check_lanes()`, the existing named
  checks, CT-05.
- **Prevents**:
  - a merge left half-done: the next session runs `lane:integrate gate-hooks
    --continue` instead of reconstructing state from a dead fork;
  - stale records after integration;
  - forgotten composed-tree gates;
  - out-of-allowlist paths that are now checked only by reviewer reading.
- **Gate interaction**: `pretooluse_gate.py` matches only `git merge`, `git
  push` and `delivery:publish` tokens (`actions()`, lines 30–47). A task
  wrapper therefore bypasses layer 3. Add `lane:integrate` to the verbs it
  maps to `git_gate.check_lanes()`, alongside `delivery:publish`. The hk
  `pre-merge-commit` layer never fires on `--no-commit` (`claude-team.md:59`),
  so the gate inside the task carries the weight.
- **Saves**: about 5 K → 600 tokens per integration, 9 per session (≈40 K);
  also the fork briefs (4.9 KB and 3.9 KB) that existed only to run this
  sequence.
- **Ticket**: CT-12 (allocate and integrate split into two units if they exceed
  300 lines). Blocked by CT-01, CT-02, CT-05 and CT-11.

### D. `delivery:publish-batch`: an A09 wrapper that derives the intents

- **Interface**:
  - Command: `./dev/mise run delivery:publish-batch -- --note "<progress line>"
    --message-file <f> [--path <p>…]`.
  - Steps:
    1. Refuses `MERGE_HEAD`, a dirty index or a branch other than the
       integration branch.
    2. Derives `root`, `common_dir`, `branch`, `head`, `remote` and
       `remote_url_sha256` from Git. Derives `hook_tree_sha256` from a live
       `delivery:inspect-hooks` run instead of a value pasted into the command.
    3. Appends the `--note` through `plan:log`, which supplies the selected
       path A09 requires.
    4. Writes both intents and their sha256 under
       `$TMPDIR/marketplace-a09/<head>/`.
    5. Runs `delivery:prepare`, threads `index_tree` into the publish intent,
       runs `delivery:publish` with `check_task=[deps:check,
       check:acceptance-baseline, test:delivery]`, and reads back `ls-remote`.
  - Receipt: `{"head","index_tree","published","remote_sha","intent_sha256":{prepare,publish},"history_scan_rc","baseline_residual_rc"}`.
  - Exit codes: the rc of the A09 step that refused, or 0.
- **Home**: `dev/git_delivery.py batch` (a new subcommand next to `prepare` and
  `publish`), tested in `dev/test_git_delivery.py` (`test:delivery`).
- **Extends**: `delivery:prepare`, `delivery:publish`, `delivery:inspect-hooks`.
  It keeps both SHA-bound steps and only removes the manual threading between
  them.
- **Prevents**: the "empty path list" refusal (memory note). It also prevents a
  stale hard-coded `hook_tree_sha256` (`a21be5fe…` in the session's intents).
  `hooks:install` writes new Git hooks, so the digest will likely change after
  CT-02 integrates; I have not verified this (see Could not verify).
- **Saves**: about 3 K → 300 tokens per publish, 4 per session.
- **Gate interaction**: add `delivery:publish-batch` to the verbs
  `pretooluse_gate.py` gates, so unpublished lane merges are still checked.
- **Ticket**: new, CT-13. Blocked by CT-02.

### E. `lane:brief` plus slotted agent definitions

- **Interface**:
  - Command: `./dev/mise run lane:brief -- <unit> --role
    implementer|doc-writer|reviewer|retro-writer [--handoff <file>]`.
  - It prints the pointer block from the lane record: worktree, branch,
    `base_sha` and `allocation_commit`, owned and excluded paths,
    `required_checks` as literal commands, the ticket fetch command, the
    reviewer's handoff claims from `--handoff`, and a machine line
    `LANE-UNIT: <unit>`. Plain text, at most 1.5 KB.
  - The parent's brief becomes `subagent_type: implementer` with the
    `lane:brief` output, then only the judgement: acceptance criteria, the
    design question and known risks.
- **Home**: `dev/lane.py brief`, plus edits to `.claude/agents/{implementer,doc-writer,reviewer,retro-writer}.md`.
  Move these constants into the agent bodies:
  - the never-spawn and never-push rules;
  - the gate list in order;
  - the instruction to merge the integration tip and rerun the gates;
  - the handoff schema and word cap;
  - the seven retro categories;
  - the P1/P2/P3 scale and dispositions;
  - the trailer lines, read from a file path in the brief, since the session
    URL changes per session.
- **Extends**: the existing agent definitions (CT-03); the retro-writer step 1
  inputs.
- **Prevents**: brief drift (`VIRTUAL_ENV` guidance in 12 of 17 briefs, the
  retro categories in only 6 of 17, trailers in 8 of 17); mismatched base SHAs
  between brief and record (the C1 case). Every lane then runs under the
  definitions' `maxTurns`, `permissionMode` and `disallowedTools`.
- **Saves**: about 55% of 79 KB per session (≈11 K tokens in the parent).
- **Ticket**: new, CT-14. Blocked by CT-03 and CT-05. CT-06 consumes it.

### F. `plan:log` and `plan:handoff`

- **Interface**:
  - `./dev/mise run plan:log -- "<text>"` appends a dated bullet to
    `progress.md` above the `NEXT` bullet, which stays last. Exits 2 if the
    file would pass 900 KB (planning-with-files drops injection above 1 MiB,
    per the `a2a63789` report).
  - `./dev/mise run plan:handoff -- --write|--check`:
    - `--write` regenerates the base, integrated-lanes and pending sentences
      of the `## Session handoff` block from `git rev-parse HEAD`, the remote
      tip and the lane records, and leaves the hand-written `Next:` and
      pending-decision text alone;
    - `--check` asserts the block ends by line 30 of `task_plan.md`, the NEXT
      bullet sits in the last 20 lines of `progress.md`, the cited base equals
      HEAD or the remote, and the lane list matches the records;
    - receipt: `{"block_lines":[s,e],"next_bullet_tail_offset","base_ok","lanes_ok"}`.
- **Home**: `dev/plan_records.py`; `plan:handoff --check` joins `dev/check.py`
  as a named sub-check, or runs as a separate `check:planning` task if `check`
  must stay manifest-only.
- **Extends**: `.claude/rules/planning-records.md` (append-only progress) and
  the injection windows recorded in memory `planning-with-files-injection.md`.
- **Prevents**: a buried NEXT bullet; the stale "re-review in progress" and
  base `28fedf1` handoff injected into this session; 70-call searches like
  `a162b749`'s.
- **Saves**: about 870 → 80 tokens per progress entry, 22 per session; plus
  one 1.4 MB agent per handoff.
- **Ticket**: new, CT-15.

### G. `ledger:sync` (CT-05 as written, plus derived local columns)

- **Interface**: `./dev/mise run ledger:sync [-- --check]`.
  - The first six columns come from `gh api graphql` (`blockedBy`, `parent`).
  - The Lane and Local-state columns come from the lane records' `tickets`,
    `status` and `review`; free text sits in an optional `ledger_note` field.
  - `--check` makes no tracker call and compares against the last snapshot
    stored in `ticket-ledger.json`.
  - Receipt: `{"rows","changed_rows":[…],"snapshot_sha256"}`.
- **Home**: `dev/ledger.py`. It reuses the GraphQL query the parent ran at
  bash #23 (`gh-issues-graph.json`).
- **Prevents**: silent no-op `str.replace` edits (bash #68 replaced six row
  strings with no assertion); ledger rows that disagree with the lane records.
- **Ticket**: CT-05, with the acceptance additions below.

### H. A check that new tests are wired into a named task

- **Interface**: a new rule in `dev/check.py`. Every `dev/test_*.py` and
  `dev/**/test_*.py` must be (a) named by a `test:*` task that `check:research`
  depends on, (b) discovered by `check.py`'s own discovery list, or (c) listed
  in an explicit exemption with a reason. A violation prints `unwired test:
  <path>` and exits 1, the convention `check` already uses.
- **Extends**: `dev/check.py:72` discovery and `.claude/rules/dev-tests.md`
  ("route a test through `check:research` depends").
- **Prevents**: forgotten `test:hooks` wiring; the live gap where
  `dev/test_retro_gate.py` runs under no named check.
- **Ticket**: new, CT-16, about 40 lines. Blocked by none; it needs a CT-01
  follow-up that adds `test:retro-gate`.

### I. CT-11 named-check lock

- **Interface**: `dev/check_lock.py`, a context manager taking `fcntl.flock`
  on `<git-common-dir>/marketplace-checks.lock`. The common dir is shared by
  all worktrees and is not a tracked path. The holder (pid, worktree, task,
  start) goes in the file. Bounded wait from `$CHECK_LOCK_WAIT`, default 600 s,
  then exit 2 naming the holder. `check.py` and the `check:research` run take
  it; `retro_gate.py` reports the lock outcome in its last line.
- **Prevents**: the 15 `test:collect` errors, the stray `.a05b-*` directory and
  the transient `mise ERROR`.
- **Ticket**: CT-11 as written. `lane:integrate` (C) depends on it.

### J. `session:status`: one probe instead of three drifting grep filters

- **Interface**: `./dev/mise run session:status`. It prints one JSON object:
  - branch, HEAD, remote tip, ahead and behind;
  - `merge_in_progress` with `MERGE_HEAD` and its lane;
  - counts of staged, unstaged and untracked files, excluding `.agent/` and
    `.agents/`;
  - `hooks_installed` (hk hooks present, `merge.ff=false`);
  - per lane: `status`, `retro`, `review`, `branch_tip`, whether
    `lane_commit == branch_tip`, whether the branch is an ancestor of HEAD,
    whether the worktree exists, and a `drift` list (for example "tip moved
    after review", "integrated but not ancestor", "worktree without record").
- **Home**: `dev/lane.py status`. Optionally a SessionStart hook prints a
  one-line summary (`merge in progress: gate-hooks; 2 lanes drifted`) as plain
  stdout, which the hooks page says Claude Code adds to context.
- **Prevents**: an unnoticed half-done merge at session start; SKILL and C1
  "not re-merged" going unflagged; the probe variants in 17 commands.
- **Ticket**: CT-12 (shares the module).

### K. `/lane-retro <unit>` (CT-06) on the slotted brief

- **Interface**: `.claude/skills/lane-retro/SKILL.md` with
  `disable-model-invocation: true`, `argument-hint: "<unit>"`, `context: fork`
  and `agent: retro-writer`. The body injects
  `` !`./dev/mise run -q lane:brief -- $0 --role retro-writer` `` and
  `` !`./dev/mise run -q retro:gate -- $0` `` so the writer starts with the
  record and the gate's current refusals. A failing injected command aborts the
  skill, so the gate injection needs `|| true`. It loops until the gate exits 0
  and writes the cross-scope edits to the handoff. It must be mirrored under
  `.agents/skills/` (CT-07 mirror test).
- **Prevents**: the parent writing 5 retro records and 3 disposition appends
  itself (≈9.3 K tokens); P3 findings deferred without an owner, which the
  gate refuses mechanically.
- **Ticket**: CT-06. Add a blocker on CT-14 (`lane:brief`).

### L. SubagentStop receipt journal

- **Interface**: extend `dev/hooks/subagent_stop_gate.py`, or add a sibling
  `subagent_receipt.py` with matcher `implementer|doc-writer|reviewer|retro-writer`.
  On every stop it appends one line to `<git-common-dir>/claude-lanes/<unit>.jsonl`.
  - The unit comes from the `LANE-UNIT:` line in the first user turn of
    `agent_transcript_path`, falling back to the `cwd` branch.
  - The line holds `agent_id`, `agent_type`, `agent_transcript_path`,
    `last_assistant_message[:4000]`, the branch tip and a timestamp. The file
    is local and untracked, so `.gitignore` stays untouched.
  - `lane:set <unit> --from-journal` then lifts `lane_commit` and the reviewer
    disposition into the record.
- **Prevents**: losing handoff receipts when the parent's context dies (fork
  `a22113b3`). It also fixes the P3 at gate-hooks retro line 18: SubagentStop
  keys on `cwd`, and absolute-path lanes report the root checkout, so the
  `LANE-UNIT` marker restores the lane binding.
- **Ticket**: CT-14 (with the brief marker). Blocked by CT-02.

### M. `agent-session-history` and `/session-review <session-id>`

- **Interface**:
  - Generalize `codex-session-history` into a sibling skill
    `agent-session-history`. It adds `scripts/claude_session_digest.py
    <session-id|path> [--subagents] [--json]`, which reads
    `~/.claude/projects/<proj>/<id>.jsonl` and `<id>/subagents/agent-*.jsonl`
    plus `.meta.json`, and prints:
    - a tool histogram;
    - Bash commands truncated to N characters, with pattern tags (proposals
      A–J);
    - the Agent briefs (description, type, model, length);
    - Write/Edit paths;
    - a context-growth curve from `usage`;
    - attachment kinds by size (for example `hook_additional_context`);
    - the death point (`Prompt is too long`);
    - the subagent table.
  - `/session-review <session-id>` (user-invoked) writes
    `reviews/<label>/00-evidence-index.md` from the digest and prints the
    seven reviewer briefs (R1–R7) as `lane:brief`-style slots.
- **Home**: `.claude/skills/agent-session-history/` and its `.agents/skills/`
  mirror, with fixture-backed tests under a temporary HOME, as CT-10 requires
  for the Codex scripts.
- **Prevents**: every reviewer rebuilding extractors (R7 wrote 7); unbounded
  reads of 7 MB transcripts.
- **Ticket**: new, CT-17. Blocked by CT-10 and CT-07.

### N. Codex-thread brief generator (P14)

- **Interface**: `codex_threads.py brief <id> --budget 900w`, which composes
  the digest, research receipts and writer-lock state into the
  `references/brief-template.md` shape, so the synthesis agents become one
  script run each.
- **Note**: the parent spent ≈79 K tokens on Codex forensics before the skill
  existed. The skill now covers most of it; the remaining step is the brief
  composer.
- **Ticket**: fold into CT-10.

### O. PreToolUse gate fixes (found while writing this review)

- **Interface**: change `pretooluse_gate.py` in two ways.
  - Strip heredoc bodies (`<<'EOF' … EOF`) and quoted strings before
    segmenting, and accept `git` only as the first token of a segment.
  - Give the gate its own time budget below the hook timeout. When the retro
    gate cannot finish, emit a `deny` with the reason "gate timed out; rerun
    `./dev/mise run retro:gate -- <unit>`" instead of letting the harness fail
    closed with no reason. Alternatively raise `timeout` above the observed
    gate time.
- **Prevents**: read-only commands blocked during an in-progress merge (this
  review). It also keeps the gate's purpose (merge, push, publish) separate
  from incidental words in arguments.
- **Ticket**: a CT-02 repair before integration, since CT-02 is staged
  unmerged right now.

## Ranked backlog

Score = tokens saved per use × uses per session × a risk weight. The weight is
1 with no recorded mistake prevented, 2 with one, and 3 when the mistake caused
a dead fork, a wrong record or a blocked session. Token figures come from the
measurements above and are rounded.

| Rank | Proposal | Tokens/use × uses | Recorded mistakes prevented | Score | Ticket / blockers |
|---|---|---|---|---|---|
| 1 | C `lane:integrate` (+ `--continue`) | 4.4 K × 9 ≈ 40 K | merge left half-done; stale lane fields; out-of-allowlist paths; stale handoff after integration | 40 K × 3 = 120 K | CT-12, blocked by CT-01, CT-02, CT-05, CT-11 |
| 2 | A `lane:set` / `lane:validate` | 0.7 K × 24 ≈ 17 K | stale lane fields; hand-set `retro: passed` | 17 K × 3 = 51 K | CT-05 |
| 3 | F `plan:log` / `plan:handoff --check` | 0.8 K × 22 ≈ 18 K, plus one 1.4 MB agent | buried NEXT bullet; stale handoff base and status | 18 K × 2 = 36 K | CT-15, no blockers |
| 4 | E `lane:brief` + slotted agents (+ L journal) | 0.65 K × 17 ≈ 11 K | brief/record base-SHA mismatch; drift of gates and categories; lost receipts on context death | 11 K × 3 = 33 K | CT-14, blocked by CT-03, CT-05 (L also by CT-02) |
| 5 | B `lane:allocate` | 1.35 K × 8 ≈ 11 K | off-by-one `base_sha` (3 lanes); worktree cut before record (2 lanes); missing worktree prep | 11 K × 3 = 33 K | CT-12, blocked by CT-05 |
| 6 | G `ledger:sync` | 0.9 K × 15 ≈ 13 K | silent no-op row replaces | 13 K × 2 = 26 K | CT-05 |
| 7 | D `delivery:publish-batch` | 2.7 K × 4 ≈ 11 K | empty-path refusal; stale hook digest after `hooks:install` (likely, unverified) | 11 K × 2 = 22 K | CT-13, blocked by CT-02 |
| 8 | I CT-11 lock | rerun cost ≈ 3 K × 2 | raced results; stray scratch directory in root | 6 K × 3 = 18 K | CT-11, blocked by CT-01 |
| 9 | J `session:status` (+ SessionStart line) | 0.6 K × 8 ≈ 5 K | unnoticed half-done merge; lanes not re-merged | 5 K × 3 = 15 K | CT-12 |
| 10 | K `/lane-retro` | 3 K × 3 (parent-written retros) ≈ 9 K | P3 findings without owners (mechanically refused) | 9 K × 1.5 = 14 K | CT-06, blocked by CT-01, CT-03 + CT-14 |
| 11 | O PreToolUse gate fixes | per blocked call | false-positive block during merge (observed) | low tokens, high risk | CT-02 repair, before integration |
| 12 | H test-wiring check | small | forgotten `test:hooks`; live gap `test_retro_gate.py` | low tokens, high risk | CT-16, no blockers (+ a `test:retro-gate` task) |
| 13 | M `agent-session-history` + `/session-review` | per review, ≈ 20–40 K across reviewers | none recorded (efficiency only) | — | CT-17, blocked by CT-07, CT-10 |
| 14 | N Codex brief composer | ≈ 1.2 MB of agent transcript per thread × 4 at the next takeover | none | — | CT-10 |

**Quick wins.** O and H save few tokens but close live gaps, so do them first:
the staged gate blocks unrelated commands during the pending merge, and
`dev/test_retro_gate.py` runs under no named check.

### Proposed tickets and acceptance additions

- **CT-05 additions.**
  - `lane:set` refuses an unknown key, naming the key.
  - `retro` is derived from a `retro_gate.py` exit and cannot be assigned.
  - `lane:validate` fails on today's staged `gate-hooks.json`, either because
    `review` is missing for a status past review or because the status is
    stale.
  - The Local-state column is generated from the records.
- **CT-12: Lane lifecycle commands (allocate, integrate, status).**
  - Acceptance:
    - `allocate` in a scratch repository records a `base_sha` and an
      `allocation_commit` equal to the worktree's actual base;
    - `integrate` refuses `main`, an absent `PASS`, a failing gate and a path
      outside the allowlist, each with a reason;
    - after a simulated crash between merge and commit, `integrate --continue`
      completes to the same tree as an uninterrupted run;
    - `status` reports `merge_in_progress` and `tip moved after review` on
      fixtures;
    - `check` and the baseline stay at rc 0.
  - Blocked by CT-01, CT-02, CT-05 and CT-11. Split allocate and status from
    integrate if the unit passes 300 lines.
- **CT-13: A09 batch publish wrapper.**
  - Acceptance: derives every intent field from live Git and
    `delivery:inspect-hooks`; refuses `MERGE_HEAD`; publishes byte-identical
    intents to the manual route in a scratch remote (`test:delivery`);
    `pretooluse_gate` gates the new verb.
  - Blocked by CT-02.
- **CT-14: Slotted lane briefs, agent constants and receipt journal.**
  - Acceptance:
    - `lane:brief` output stays under 1.5 KB and matches the record;
    - the agent definitions carry the moved constants, and a test diffs a
      brief against them for duplication;
    - SubagentStop writes one journal line per lane stop in a scratch run,
      with the unit taken from the `LANE-UNIT` marker when `cwd` is the root.
  - Blocked by CT-02, CT-03 and CT-05.
- **CT-15: Planning-record writers and handoff check.**
  - Acceptance: `plan:log` keeps NEXT last; `--check` fails on a block ending
    after line 30, a NEXT bullet outside the last 20 lines, or a base differing
    from HEAD and the remote; the check is idempotent and makes no network
    call.
  - Blocked by none.
- **CT-16: Unwired-test check.**
  - Acceptance: `check` fails on a fixture `dev/test_x.py` that no task
    references; `test_retro_gate.py` is wired through a new `test:retro-gate`
    in `check:research` depends.
  - Blocked by none.
- **CT-17: agent-session-history skill and `/session-review`.**
  - Acceptance: the digest of a fixture Claude transcript reports tool counts,
    briefs, context curve and death point; the skill reads no real
    `~/.claude` in tests; the mirror test passes.
  - Blocked by CT-07 and CT-10.
- **CT-02 repair (O).**
  - Acceptance: a `test_hooks.py` case with `MERGE_HEAD` set allows a Bash
    command whose heredoc body contains a line `git merge x`, and denies a real
    `git merge claude/x-y` of a failing lane. A gate run that exceeds its
    budget yields a `deny` with a reason, never a harness timeout.

## Guardrails

- **Commands that stay user-confirmed or authority-bound.**
  - `claude-takeover.md:11` grants publishing the integration branch through
    A09 without per-push confirmation. It allows closing tickets only through
    the qualified close operation, one at a time; a draft PR to `main`, never
    merged; and host-heavy runs only with per-run confirmation.
  - `AGENTS.md:50-51` makes push, publish and merge wait for explicit
    instruction outside that grant.
  - Therefore:
    - `delivery:publish-batch` may run unattended only for the integration
      branch, and must refuse any other branch or `main`;
    - there is no batch close and no `issue:*-apply` loop. Every
      `issue:create-apply`, `issue:new-edge-apply` and close stays a single,
      separately invoked step after the user approves the to-tickets output
      (pending decision 1);
    - `lane:integrate` merges only into the integration branch;
    - nothing automates a merge to `main`, `hooks:install`, a settings
      migration or a daemon registration;
    - the five-stage verbs stay user-typed, because mattpocock skills set
      `disable-model-invocation`.
- **Interaction with the gate hooks in `dev/hooks/`.**
  - `pretooluse_gate.py` recognizes only `git merge`, `git push` and
    `delivery:publish` tokens. Every new wrapper that merges or pushes
    (`lane:integrate`, `delivery:publish-batch`) must (a) call
    `git_gate.check_lanes()` itself before acting, and (b) be added to the
    hook's verb table so a Claude-side bypass is impossible.
  - Conversely, the hook must stop matching incidental text (proposal O). With
    `onFailure: "block"` and a 10 s timeout, a slow gate run during a merge
    blocks unrelated commands, as it did in this review.
  - hk `pre-merge-commit` does not fire for `--no-commit` merges
    (`claude-team.md:59`), so the task-level gate is the real layer; `pre-push`
    is the backstop.
  - `stop_gate.py` blocks while a record says `integrated` without
    `retro: passed`. Deriving `retro` in `lane:set` keeps that hook honest;
    otherwise a hand-typed `"passed"` silences it.
  - `subagent_stop_gate.py` keys on `cwd`. The `LANE-UNIT` marker (proposal L)
    keeps it effective for lanes driven by absolute paths.
- **Hook writes to shared files.** No hook writes `task_plan.md`,
  `progress.md`, `ticket-ledger.md` or lane records. These are parent-owned
  (`planning-records.md`) and lanes run in parallel. Hooks write only the local
  journal under the Git common dir; the parent's tasks lift journal content
  into records. A PostToolUse hook that regenerates the ledger on every lane
  JSON write is rejected for that reason. The serialized `lane:set` →
  `ledger:sync` call inside `lane:integrate` covers the same need.
- **Isolation.** Do not use `isolation: worktree` in the lane agents. It
  branches from the default branch, not the integration tip (sub-agents docs),
  which would reintroduce wrong base SHAs. `lane:allocate` keeps cutting from
  the allocation commit.
- **Named checks** run inside the CT-11 lock. Until CT-11 lands, `lane:integrate`
  refuses to start while another `check` process holds the repository (a
  `pgrep` fallback), and a raced result is never recorded as a receipt
  (`AGENTS.md` gotcha).
- **Secrets.** `delivery:publish-batch` and the session digests write to
  `$TMPDIR` scratch and print paths and hashes, never transcript or rollout
  bodies (codex-session-history rule).

## Could not verify

- Whether `hk install --force-local` changes `delivery:inspect-hooks`' digest. I
  ran no write task. The claim is inferred from the task's description ("active
  Git file and config hook digest") and from `hooks:install` writing hooks. Run
  `delivery:inspect-hooks` before and after `hooks:install` to settle it.
- The exact cause of the PreToolUse timeout. Candidates: heredoc lines starting
  `git merge`/`git push` parsed as actions; then `classify(merge_sources)`
  with `MERGE_HEAD` set; then one or more `retro_gate.py` runs. I did not time
  the gate in isolation, because doing so would run the hook path again during
  the in-progress merge.
- Why the 6 lane dispatches after 20:25Z used `general-purpose` rather than the
  new `.claude/agents/*` types. They may not have loaded mid-session, or the
  parent may have chosen `general-purpose`. The transcript shows only the
  `subagent_type` values.
- Token figures count context occupancy (bytes/4). They do not count re-reads
  of cached context on later turns, which multiply the real cost of early bulky
  output; thinking blocks are redacted (0 bytes) in the transcript.
- The planning-with-files injection size (58 injections, 271 KB) is attributed
  from `attachment:hook_additional_context`. I did not separate it by hook
  event.
- I did not read the subagent transcripts of the other 20 agents beyond their
  sizes. Command-pattern counts for subagents cover the 5 sampled agents plus 3
  forks and the handoff writer.
- `dev/hooks/__pycache__/` exists in the root checkout. I did not determine
  which run produced it; it is untracked and ignored by none of the frozen
  rules I read.
