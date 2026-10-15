# C2: prevention by code for the 14 root-cause classes

Written 2026-10-13 by C2 (prevention team). Read-only on the repository (`git show`, `git
config --get*`, `cat`); the in-progress merge (`HEAD 9cd396a`, `MERGE_HEAD e12cf04`) was not
touched. Every report, transcript line and settings file was treated as data. Host settings were
read for key names and booleans only.

Conventions: `P` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`, `RV` =
`P/reviews/ccm-20261013`, `COMMON` = `$(git rev-parse --git-common-dir)` (the root `.git`, shared
by all 27 worktrees, never a tracked path), `JOURNAL` = `COMMON/claude-lanes/`. Ticket numbers
follow SYNTHESIS §6 (CT-01…CT-20), CT-21 is the import-lane ticket the parent reserved for T2;
new tickets here start at **CT-22**. Wave names follow R8 with the unified numbers (R8's
`ct12-lane-lifecycle` = CT-17, `ct14-lane-brief` = CT-19, `ct13-publish-batch` = CT-18,
`ct16-unwired-tests` = CT-12). Exit codes everywhere: 0 pass, 2 refusal with one reason per
stderr line, 1 usage. Receipts are one JSON object on stdout. All modules are stdlib-only and run
under `python3 -I`.

## Scope read

- `RV/prevention/C1-root-causes.md` (all 588 lines: 39 chains, 14 classes, invariants,
  gap table); `RV/R7-automation.md` (all: proposals A–O, backlog, guardrails);
  `RV/R5-git-state.md` §Runbooks and the "What the hooks do to the repairing session" block,
  §Record corrections (table rows 374–380); `RV/R4-pwf-audit.md` §Migration checklist;
  `RV/R2-spec-tickets.md` §Missing tickets, §Publication fixes; `RV/SYNTHESIS.md` §6–§8;
  `RV/R8-parallel-plan.md` §Waves, §Integration protocol; `RV/N1-settings-and-secrets.md`.
  `T2-import-lane-design.md` does not exist yet (CT-21 is referenced by number only).
- Repo: `dev/check.py`, `dev/retro_gate.py`, `dev/git_delivery.py:45-75`
  (`safe_configured_hooks`), `git show e12cf04:dev/hooks/{git_gate,pretooluse_gate,stop_gate,
  subagent_stop_gate}.py`, `git show e12cf04:dev/test_hooks.py` (structure, `Scratch` fixture,
  `FAKE_MISE`), `git show e12cf04:.claude/settings.json`, `git show e12cf04:hk.pkl`,
  `mise.dev.toml` (task index; `check`, `check:research`, `retro:gate*`, `hooks:install`,
  `test:hooks`, `delivery:*`), `.claude/agents/*.md` (5), `.claude/rules/*.md` (3),
  `.claude/skills/codex-session-history/` (layout, `codex_threads.py` subcommands),
  `docs/agents/{ticket-retro,claude-team,issue-tracker,claude-takeover}.md`, `dev/AGENTS.md`,
  `P/lanes/{gate-hooks (staged),a06-unit3}.json`, `P/task_plan.md:1-35`, `P/progress.md` tail,
  `P/skill-invocations.md:1-25`, `P/proposals/claude-takeover-spec/build_manifests.py:1-30`,
  `.git/info/exclude`, `git config --global --get-regexp '^hook\.'` (hk global
  `pre-commit`/`commit-msg`/`pre-push` entries exist; no local ones), `git --version` 2.54.0.
- Host (names/booleans only): `~/.claude/settings.json` keys `autoCompactEnabled=false`,
  `effortLevel`, `env` (5 `CLAUDE_CODE_*`/`ENABLE_TOOL_SEARCH` names, incl.
  `CLAUDE_CODE_FORK_SUBAGENT`), `hooks` (one `SessionStart` entry), `modelSettings` (per-model
  `effortLevel` only, no `autoCompactWindow`), `statusLine` (`statusline.sh`); `~/.claude.json`
  `autoCompactEnabled=false`, `autoCompactWindowsCache`. Plugin caches: planning-with-files
  3.24.0 `hooks/hooks.json` (SessionStart, UserPromptSubmit, PreToolUse, PostToolUse,
  PreCompact, Stop) and `scripts/`; mise skill 2.10.0 (`task_config.includes` replaces the
  defaults and last entry wins; `usage` `arg`/`flag` syntax). `hk --help` (2.6.0) and
  `hk install --help`.
- Transcript facts re-derived with `python3 -I` on the main JSONL (7.08 MB, 2,045 lines):
  assistant `message.usage` keys are `input_tokens`, `cache_creation_input_tokens`,
  `cache_read_input_tokens`, `output_tokens` (+ non-integer fields); the death line (2043) is an
  assistant line whose usage is all zeros, so the reader must skip zero-usage lines.
- Claude Code docs fetched 2026-10-13 (CLI 2.1.296 per the earlier guide report):
  - hooks: 33 events; common input `session_id`, `transcript_path`, `cwd`, `permission_mode`,
    `hook_event_name`, plus `agent_id`/`agent_type` "when the hook fires in a subagent";
    `PreToolUse` matches `Agent` and its `tool_input` is `{prompt, description, subagent_type,
    model}`; `SubagentStop` input adds `agent_id`, `agent_type`, `agent_transcript_path`,
    `last_assistant_message`, `stop_hook_active`, and its matcher is the agent `name`;
    `Stop` output `decision: "block"` + `reason`, capped at 8 consecutive continuations
    (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`); `UserPromptSubmit` input `prompt`, output
    `additionalContext` / `decision: "block"`; `SessionStart` sources `startup|resume|clear|
    compact|fork`, plain stdout is added to context, `CLAUDE_ENV_FILE` takes `export` lines;
    `PreCompact` can block (exit 2 / `decision`); `ConfigChange` (`project_settings`,
    `local_settings`, `user_settings`, `skills`) can block silently; `additionalContext` is
    accepted on PreToolUse, PostToolUse, Stop, SubagentStop, SessionStart, UserPromptSubmit;
    `onFailure: block` needs ≥ 2.1.295; `if` holds one permission rule; hooks edited in settings
    are "normally picked up automatically by the file watcher"; `hooks` arrays merge across
    settings files; `Hooks: <event>:<matcher> [...] finished with status N (Nms)` log lines.
  - sub-agents: definitions in `.claude/agents/` are watched, but "the watcher covers only
    directories that existed when the session started, so after creating a scope's first agent
    file in a new `agents` directory, restart to load it"; frontmatter `name` is what hooks see
    as `agent_type`; `skills:` preloads full content (not for `disable-model-invocation` skills);
    `isolation: worktree` branches from the default branch; frontmatter `hooks` support every
    event and `Stop` becomes `SubagentStop`.
  - skills: `` !`cmd` `` runs before the body is sent and a failing command aborts the whole
    invocation (`|| true` to tolerate); `disable-model-invocation: true` blocks the Skill tool
    and preloading; skill dirs are watched except a top-level dir created mid-session
    (`/reload-skills`); a slash name runs only "at the start of your message", a name later in
    the message is permission, not an invocation.
  - settings: precedence managed > `--settings` > `.claude/settings.local.json` >
    `.claude/settings.json` > `~/.claude/settings.json`; list keys merge; `autoCompactEnabled`
    is scope "Any file", default `true`, `DISABLE_AUTO_COMPACT` is the per-session override and
    "whichever of the two turns it off, the other can't turn it back on"; `autoCompactWindow`
    (any file, 100K–1M), `/autocompact`, `--autocompact`, `CLAUDE_CODE_AUTO_COMPACT_WINDOW`;
    native 1M models (Fable, Sonnet 5, Opus 4.7+) compact "at about 967K tokens by default";
    `env` applies to "every session and for the subprocesses Claude Code starts from it" and
    project/local files cannot set a listed set of variables (none of ours); `hooks`,
    `enabledPlugins`, `extraKnownMarketplaces`, `skillOverrides`, `permissions.*`, `statusLine`,
    `agent`, `disableAllHooks` are all "Any file".
  - statusline: stdin carries `context_window.{total_input_tokens, context_window_size,
    used_percentage, remaining_percentage, current_usage}`, `transcript_path`,
    `exceeds_200k_tokens`; runs on events, debounced 300 ms, optional `refreshInterval`.

## Design principles shared by every class

1. **One hook script per event, dispatching to rule modules.** `.claude/settings.json` wires
   exactly one command per `(event, matcher)`; each script imports rule modules under
   `dev/hooks/rules/` so lanes add files, not hook entries. Every script answers within a
   self-imposed budget (`HOOK_BUDGET_S`, default 6 s, below the 10 s configured timeout) and,
   when the budget is spent, emits a deny/block **with a reason** instead of letting
   `onFailure: block` fail closed silently (R7 O, class J).
2. **Earliest point that can block wins.** Order of preference: PreToolUse with the projected
   tool input (Write/Edit `content`, Bash tokens, Agent `tool_input`) → hk `pre-commit`
   (already live through the user's global hk install; `hk.pkl` defines no `pre-commit` today,
   so adding one needs no `hooks:install` and does not touch the A09 `safe_configured_hooks`
   set `{pre-commit, commit-msg, pre-push}`) → mise task guard inside `lane:*` → `check` /
   `check:planning` → Stop/SubagentStop (last resort, once).
3. **Rule modules are discovered, not registered.** `dev/check.py` gains one line that runs
   `dev/checks/*.py` (each exposes `check(root) -> list[str]`), and `dev/plan_records.py`
   (CT-15) runs `dev/planning_checks/*.py` the same way. A lane that adds a rule owns one new
   file; no two lanes edit `check.py` for a rule (R8 disjointness).
4. **Hooks never write parent-owned shared files.** They append only under `JOURNAL/`
   (untracked, shared across worktrees, survives context death); `lane:*`/`plan:*` tasks lift
   journal content into tracked records (R7 guardrail, D8).
5. **Identity of the caller.** Hook input without `agent_id` = the parent session; with
   `agent_id`/`agent_type` = a subagent (type is the frontmatter `name`, `general-purpose`,
   `Explore`, `Plan`, or `fork`); a fork session also carries SessionStart `source: fork`.
   Scripts expose `caller(event) -> {"parent","subagent","fork"}` in `dev/hooks/rules/common.py`
   and tests fix all three shapes (see Could not verify for the fork `agent_type` value).
6. **Fixtures reproduce the evidence.** `dev/fixtures/prevention/` holds one minimal case per
   finding (listed in §Test inventory), including a redacted 40-line slice of the real
   transcript shape (`usage` curve), the staged `gate-hooks.json`, a `MERGE_HEAD` scratch repo,
   the staged settings file and the 113 Bash command texts (heredocs kept, paths generalized).

---

## Per-class design

### A. Context budget blind (P1-1, P2-19, P2-13)

**Invariant.** `ctx(session) < T_fork` for every `Agent(subagent_type: fork)`; at every user
prompt the session is told `ctx` and the phase; `ctx ≥ T_delegate` ⇒ the turn's work is a
checkpoint (`plan:log`) or a delegation, never a build step; auto-compaction is on in the
effective settings or the session start reports that it is off and why. `ctx` =
`input_tokens + cache_creation_input_tokens + cache_read_input_tokens` of the last assistant
line in `transcript_path` whose sum is > 0.

**Enforcement point.** `PreToolUse` matcher `Agent` (reads `transcript_path`; the only point that
sees the dispatch before it happens) for the fork deny; `UserPromptSubmit` for the budget line
(stdout/`additionalContext` reaches the model every turn); `SessionStart` for the compaction
report (plain stdout is injected). `Stop` is too late (the fork is already dead) and
`SubagentStop` cannot stop a spawn, so the spawn rule lives in PreToolUse. Statusline would be
a user-side convenience only (the user already runs a personal `statusline.sh`).

**Mechanism.**
- `dev/context_budget.py` (library + CLI): `usage: context_budget.py <transcript.jsonl>
  [--window N] [--json]`. Reads the file backwards in 64 KiB chunks, returns
  `{"ctx":int,"line":int,"window":int,"pct":float,"timestamp":str}`; `--window` defaults to
  `$CLAUDE_CTX_WINDOW` else 1,000,000 (the native window of the session models; the
  statusline, not the hook input, carries `context_window_size`, so the value is a pin, see
  Could not verify). Exit 0 with the receipt, 2 if no usage line exists, 1 usage.
- Thresholds (tokens, in `dev/hooks/rules/common.py`, overridable through settings `env`):
  `CTX_WARN=450000`, `CTX_DELEGATE=600000`, `CTX_FORK_MAX=500000`, `CTX_HARD=850000`. Rationale:
  a fork starts at the parent's ctx (`a22113b3` began at 970,507), the integration sequence
  needs ≈ 150 K of headroom, and the default auto-compact point for 1M models is ≈ 967 K.
- `dev/hooks/agent_gate.py` (PreToolUse, matcher `Agent`): rule `fork_budget`: if
  `tool_input.subagent_type == "fork"` and `ctx ≥ CTX_FORK_MAX` → `permissionDecision: deny`,
  reason "fork would start at <ctx> tokens (limit <T>); dispatch a fresh `implementer`/
  `general-purpose` agent with `./dev/mise run lane:brief -- <unit> --role …` output, or
  `/clear` after `plan:handoff --write`". If `ctx ≥ CTX_HARD` and the prompt carries no
  `LANE-UNIT:` marker → `ask` with the reason (the user decides whether the parent may still
  delegate). Any other dispatch → allow with `additionalContext: "ctx <n> (<pct>%)"`.
- `dev/hooks/prompt_hook.py` (UserPromptSubmit): prints one line
  `ctx <n>/<window> (<pct>%) phase=<Current Phase from task_plan.md> next=<Next Step>`;
  at `≥ CTX_WARN` appends "checkpoint and delegate: run plan:log, then dispatch lanes; do not
  start a build in this window"; at `≥ CTX_DELEGATE` the line starts with `CONTEXT BUDGET:`
  and names `plan:handoff --write` then `/clear`. Never blocks (a block would hide the user's
  words, the class-E failure).
- `dev/hooks/session_start.py` (SessionStart, all sources): rule `autocompact`: reads
  `~/.claude/settings.json`, `~/.claude.json`, `.claude/settings.json`, `.claude/settings.local.json`
  for the keys `autoCompactEnabled`, `autoCompactWindow`, `env.DISABLE_AUTO_COMPACT` only and
  prints `auto-compact: <effective> (user=false, project=true, window=<n>)`; when the effective
  value is off it adds "project rule: forks and long integrations need compaction on; see
  docs/agents/claude-team.md#context-budget". Read-only, names and booleans only.
- Project settings (`.claude/settings.json`): `"autoCompactEnabled": true` and
  `"autoCompactWindow": 700000`. Shared project settings sit above user settings in the
  precedence stack, so the project value applies in this checkout unless the user sets
  `DISABLE_AUTO_COMPACT` in the environment ("whichever of the two turns it off, the other
  can't turn it back on"); the `~/.claude.json` copy is unverified (below). Turning the user
  file's `false` into `true` is a **user decision** (D-A1); the project file and the SessionStart
  line are what the project can do.
- Rule text (`docs/agents/claude-team.md` §Context budget, pointer from root `AGENTS.md`
  gotchas): Codex forensics and transcript reads run in subagents; at `CTX_WARN` the parent
  checkpoints (`plan:log`, `plan:handoff --write`) and delegates; at `CTX_DELEGATE` it ends the
  window (`/clear`) after the handoff check passes; forks are for ≤ 10-minute tasks under
  `CTX_FORK_MAX`.
- Wiring: `settings.json` hooks (snippet in §Settings), tasks `ctx:status` (`arg "[transcript]"`)
  in `mise/tasks/ct22.toml`.

**Tests first** (`dev/test_context_budget.py`, `dev/test_agent_gate.py`, `dev/test_prompt_hook.py`,
`dev/test_session_start.py`):
- T-A1 fixture `fixtures/prevention/transcript-usage-curve.jsonl` (6 assistant lines with the
  real curve 53 K → 977 K, last line all-zero usage as at `T:L2043`): `context_budget.py` returns
  `ctx=977093`-shaped value from the last non-zero line, not 0.
- T-A2 PreToolUse event `{tool_name:"Agent", tool_input:{subagent_type:"fork", prompt:"…"},
  transcript_path:<T-A1>}` → stdout JSON `permissionDecision == "deny"` and the reason names
  `lane:brief`; the same with `subagent_type:"implementer"` → allow with `additionalContext`.
- T-A3 a 20 MB synthetic transcript: the gate answers in < 1 s (backward read).
- T-A4 UserPromptSubmit with ctx 660 K (the 19:56Z quiz point) → the first stdout line starts
  with `CONTEXT BUDGET:` and names `plan:handoff --write`.
- T-A5 SessionStart with a temporary `HOME` whose `settings.json` says `autoCompactEnabled:false`
  and a project file saying `true` → stdout contains `auto-compact:` and both booleans; with no
  files → `auto-compact: default(on)`.
- T-A6 (settings) `.claude/settings.json` parses and holds `autoCompactEnabled: true`.

**Ordering / ownership.** New ticket **CT-22 "Context budget guard"**. Wave 0 (parent, before
the next integration, test-first, ≤ 80 lines each, declared in the wave-0 retro row): the
settings keys, `context_budget.py`, the `fork_budget` rule in `agent_gate.py`, the
`prompt_hook.py` budget line, the `session_start.py` auto-compact line, their four test files.
Wave 1+ (lane `ct22-context-budget`): thresholds through `env`, phase/next extraction, docs
section, `ctx:status` task. `owned_paths`: `dev/context_budget.py`, `dev/hooks/agent_gate.py`,
`dev/hooks/prompt_hook.py`, `dev/hooks/session_start.py`, `dev/hooks/rules/common.py`,
`dev/test_context_budget.py`, `dev/test_agent_gate.py`, `dev/test_prompt_hook.py`,
`dev/test_session_start.py`, `dev/fixtures/prevention/transcript-*.jsonl`,
`mise/tasks/ct22.toml`, `docs/agents/claude-team.md` (§Context budget only). Disjoint from
wave-1 R8 lanes (ct02b owns `pretooluse_gate.py`/`git_gate.py`/`test_hooks.py`).

**Guardrails.** User-confirmed: any change to `~/.claude/settings.json` or `~/.claude.json`
(the hook only reports). The parent is identified by the absence of `agent_id`; a subagent's
`UserPromptSubmit` never fires (no user prompts there); the fork deny applies to whoever
dispatches (parent or subagent), since the fork inherits the dispatcher's context.

### B. Records derived by hand (P1-1, P1-4, P1-9, P1-13, P2-10, P2-12, P2-14, P2-17, P2-24)

**Invariant.** For every `P/lanes/<u>.json`: `base_sha` = the allocation commit and
`allocated_from` = its parent, both reachable from `branch`; `status` prefix ∈ {allocated,
implementing, implemented, reviewed, integrated, published}; `status` past `reviewed` ⇒
`review.disposition` present; `retro == "passed"` ⇒ `retro_gate.py --unit <u>` rc 0 on this
tree; `published` ⇒ `integration_merge` is an ancestor of `refs/remotes/origin/<integration>`;
`P/task_plan.md` Lanes table = projection of the records; handoff base = `HEAD` or the remote
tip. No field is typed by a human or the model: `lane:set` derives it.

**Enforcement point.** PreToolUse `Write|Edit` on `lanes/*.json` with the projected content
(blocks the write that would corrupt the record, e.g. the `cat >` at `T:L1553` goes through
Bash, so the hk `pre-commit` step catches that route before the allocate commit); hk
`pre-commit` step `lane-validate` (every commit, already live through the global hk hooks);
`lane:validate` inside `check`; `Stop` (existing `stop_gate.py`) as the once-per-turn backstop.

**Mechanism.** Extends R7 A/B/F/G/J and CT-05/CT-15/CT-17:
- `dev/lane.py` (CT-05 `set|validate`, CT-17 `allocate|integrate|status`): the schema dict
  gains `allocated_from`, `allocation_commit`, `lane_commit`, `merged_head`, `review`
  (`{disposition, sha, agent, journal_line}`), `retro` (derived only), `integration_merge`,
  `published`, `holds`, `worktree_removed`, `import_source.data[]` (class L), `ledger_note`.
  `validate` checks the invariant list above with git (`merge-base --is-ancestor`,
  `rev-parse <base>^`), exit 2 with `lanes/<u>.json: <field>: <reason>` lines; receipt
  `{"records":n,"failures":[…]}`. `--staged` validates the index version (for the pre-commit step).
- `dev/hooks/record_guard.py` (PreToolUse, matcher `Write|Edit`): when `tool_input.file_path`
  matches `P/lanes/*.json`, project the write (`content`, or `old_string→new_string` applied
  to the current file) and run `lane.validate_record(dict)`; deny with the reasons and the
  `lane:set` command that would do it right. Same script hosts the class-I settings rule and the
  class-K progress-size rule (one script per event). Budget 2 s; on budget exhaustion deny with
  "record guard timed out; run ./dev/mise run lane:validate".
- `hk.pkl` `["pre-commit"]` step `records`: `check = "./dev/mise run check:records"`, where
  `check:records` runs `python3 -I dev/lane.py validate --staged && python3 -I
  dev/settings_check.py --staged` (< 1 s; `stash = "none"`). Lives alongside the existing
  `pre-merge-commit`/`pre-push` hooks; `pre-commit` is in A09's safe set.
- `plan:handoff --write/--check` (CT-15) regenerates the Lanes table and the handoff base from
  records and git; `--check` fails on `base ≠ HEAD ∧ base ≠ remote tip`.
- `stop_gate.py` (extend, CT-17): also runs `lane.validate()` and reports the first three
  failures as the block reason, once.

**Tests first** (`dev/test_lane.py` cases, fixtures `dev/fixtures/prevention/lanes/`):
- T-B1 the staged `gate-hooks.json` byte-for-byte: `validate` rc 2 with `status past review
  needs review` once `status` is set to `reviewed…`, and with the original text rc 2 on
  `base_sha e618243 is not the allocation commit (2d1f60e)` in a scratch repo that replays the
  allocate commit after the heredoc (`git rev-parse HEAD` then commit).
- T-B2 `a06-unit3.json` shape (`unit` ≠ retro file name) with `retro: passed` → rc 2
  `retro passed but retro_gate.py --unit a06-unit3 rc 2`.
- T-B3 `lane:set x retro=passed` → rc 2 "retro is derived"; `lane:set x status=integrated`
  after a passing record → receipt `retro: passed`.
- T-B4 PreToolUse Write of a lane JSON with `"status": "integrated"` and no `review` → deny
  naming `lane:set`; a Write of an unrelated path → no output.
- T-B5 scratch repo with `hk.pkl` pre-commit `records` step and a staged invalid record →
  `git commit` rc ≠ 0 with the validate reason (uses the `test_hooks.py` `HkHooks` pattern,
  skipped without `hk`).
- T-B6 `plan:handoff --check` on a `task_plan.md` whose handoff names `28fedf1` while HEAD is
  another SHA → rc 2 `base_ok:false`.
- T-B7 `published` record whose `integration_merge` is not on `origin/<branch>` (scratch remote)
  → rc 2.

**Ordering / ownership.** CT-05 (wave 1: schema, `set`, `validate`, `--staged`, T-B1–B3, B7),
CT-15 (wave 1: `plan:handoff`, T-B6), CT-17 (wave 2: `allocate` writes `base_sha`/
`allocated_from` after the commit; `status`; `stop_gate.py` extension), **CT-22** wave 0 gets
only the hook entry placeholders; `record_guard.py` and T-B4 belong to a new ticket
**CT-23 "Record and settings guard hooks"** (wave 2, after CT-05's library exists). `hk.pkl`
`pre-commit` step + `check:records` task: wave 0 parent edit (two lines), T-B5 with CT-23.
`owned_paths` CT-23: `dev/hooks/record_guard.py`, `dev/test_record_guard.py`,
`dev/settings_check.py` (moved from CT-16, see I), `dev/test_settings_check.py`,
`mise/tasks/ct23.toml`.

**Guardrails.** The hook never edits a record; it denies and names the task. `lane:set` is the
only writer; the parent runs it (D8). `published` is set by `delivery:publish-batch` (CT-18)
from the remote SHA, never by hand.

### C. Integration sequence non-resumable; gate bypass by merge form (P1-1, P1-3, P2-1, P2-2, P2-18, P2-20)

**Invariant.** `MERGE_HEAD` is absent at every Stop and SessionStart unless `JOURNAL/integrate/
<unit>.json` records an in-progress `lane:integrate` step; no Bash command on the integration
branch runs `git merge … --no-commit` (token-anchored), `--squash`, `rebase`, `cherry-pick`
or `pull --ff` of a lane; a lane merge changes only `owned_paths ∪ {lanes/<u>.json,
retros/<u>.md, lanes/<u>.log.md}`; `hooks:install` runs only if
`git_delivery.safe_configured_hooks` accepts the resulting config; publish precedes install;
untracked files a merge would overwrite are snapshotted first.

**Enforcement point.** PreToolUse `Bash` (token-anchored verb table; the only point that sees
the merge form before git runs); `lane:integrate` preflight (the runner is the normal path);
`SessionStart` line (recovery visibility); `hooks:install` task guard (mise task refuses);
`Stop` (block once while `MERGE_HEAD` exists without a runner receipt).

**Mechanism.** Extends R7 C/J/O, CT-02b, CT-17, CT-18:
- `pretooluse_gate.py` (CT-02b): `actions()` becomes token-anchored: strip heredoc bodies
  (`<<-?['"]?(\w+)['"]?` … terminator) and quoted strings, segment on operators, accept `git`
  only as the first token of a segment (after env assignments and `-C`/`-c` options). New
  verb table rows: `merge --no-commit|--squash` on the integration branch → deny "use
  ./dev/mise run lane:integrate -- <unit>"; `rebase|cherry-pick` with a lane ref → deny;
  `pull` with `--ff`/no `--no-ff` of a lane → deny; `lane:integrate`/`delivery:publish-batch`
  verbs gate like `delivery:publish` (R7 guardrail). `--dry-run` CLI (`pretooluse_gate.py
  --dry-run < event.json`) prints the parsed actions without running the gate, for the corpus
  test and for the parent to check a command before running it. Per-call budget: the gate
  stops after `HOOK_BUDGET_S` and denies with "gate timed out after N s; rerun ./dev/mise run
  retro:gate -- <unit>" (class J).
- `dev/lane.py integrate` (CT-17) as R7 C, plus: step 0 writes `JOURNAL/integrate/<unit>.json`
  `{"unit","step","lane_tip","started","snapshot":[…]}` before any git mutation and updates
  `step` after each; step 1.5 **snapshot**: `git merge --no-commit` is not used; instead the
  runner computes the merge's touched paths (`git merge-tree --write-tree HEAD <tip>` on Git
  2.54) and copies every untracked file it would overwrite to
  `JOURNAL/snapshots/<unit>/<timestamp>/` with a SHA-256 list in the receipt (P2-18); step 2
  runs `git merge --no-ff --no-edit -m <template>` only after the composed-tree gates pass
  on `merge-tree`'s result (so the merge commit is never half-done; if a gate must run on a
  checked-out tree, the runner uses a temporary worktree of the merge-tree result, not the
  root); `--continue` resumes from `step` in the journal; `--abort` runs `git merge --abort`
  and restores the snapshot. Foreign hunks are refused (step 3); parent wiring lands as a
  separate `lane:integrate --parent-hunk <path>` commit that the receipt names.
- `hooks:install` task guard: `run` becomes `python3 -I dev/hooks_install.py` which (1)
  refuses when `delivery:inspect-hooks` would refuse after install (dry-run: compose the
  config `hk install` would write and feed it to `git_delivery.safe_configured_hooks`), (2)
  refuses while `git log @{upstream}..HEAD` is non-empty ("publish first", P1-3), (3) else
  installs with `--legacy`/shim mode per CT-02b's reconciliation. Receipt
  `{"installed":bool,"events":[…],"inspect_hooks_rc":n}`.
- `session_start.py` rule `merge_state`: prints `merge in progress: <lane> (journal step <k>;
  run lane:integrate <unit> --continue|--abort)` or nothing. `stop_gate.py` rule
  `merge_state`: block once while `MERGE_HEAD` exists and no journal file names it.
- Rule text (`claude-team.md` §Integration): the merge form is the runner's; `--no-commit` is
  forbidden on the integration branch.

**Tests first** (`dev/test_hooks.py` CT-02b cases; `dev/test_lane.py` CT-17 cases):
- T-C1 corpus replay: `dev/fixtures/prevention/bash-corpus.jsonl` (the 113 session commands,
  paths generalized, heredocs intact; each row `{"command","expect":"allow|deny|gate:<lane>"}`)
  through `--dry-run`: exactly the real `git merge`/`git push`/`delivery:publish` segments are
  actions; the R7 heredoc that contained "git merge"/"git push" parses to no action.
- T-C2 `git merge --no-ff --no-commit claude/x-y` on branch `codex/marketplace-native-onboarding`
  → deny naming `lane:integrate`; the same with `--no-ff` only → gated by the retro gate as
  today; `git merge --abort` → allow.
- T-C3 scratch repo, `MERGE_HEAD` set by a real `git merge --no-commit`, no journal →
  `stop_gate.py` blocks once with `--continue|--abort`; with a journal file → no block.
- T-C4 `lane:integrate` killed (SIGKILL the subprocess) between the snapshot and the merge
  commit → `--continue` yields the same tree SHA as an uninterrupted run; `--abort` restores
  the untracked file from the snapshot byte-for-byte.
- T-C5 a lane whose tip touches `mise.dev.toml` outside `owned_paths` → rc 2 listing the path;
  `--parent-hunk mise.dev.toml` produces a second commit whose message names the hunk.
- T-C6 `hooks_install.py` in a scratch repo with an unpublished commit → rc 2 "publish first";
  after a scratch push → installs and `git_delivery.py inspect-hooks` still passes (the
  CT-02b reconciliation chosen) — this is the install × inspect case R5 asked for.
- T-C7 gate latency: 40 lane records with failing retros, a `git push` command → the hook
  returns a deny with "timed out" in < `HOOK_BUDGET_S + 1` s (never the harness timeout).

**Ordering / ownership.** CT-02b (wave 1 #1): T-C1, T-C2, T-C7, `--dry-run`, verb table,
budget; `hooks_install.py` + T-C6 (owned `dev/hooks_install.py`, `dev/test_hooks_install.py`,
`mise.dev.toml` `hooks:install` row only — the parent applies the row at integration). CT-17
(wave 2): journal, snapshot, `--continue/--abort`, `merge-tree` composition, `session_start.py`
`merge_state` rule (`dev/hooks/rules/merge_state.py`, a new file so CT-22's script stays
untouched), T-C3–C5. Wave 0: the `claude-team.md` sentence forbidding `--no-commit` (runbook
step 7 doc edit) and the corpus fixture file extracted by the parent (no code).

**Guardrails.** `lane:integrate` merges only into `codex/marketplace-native-onboarding`; `main`
is refused; `hooks:install` stays a parent-run, user-admitted operation (the guard only adds
refusals); `--abort` and `--continue` are the only two recovery verbs and both print what they
will do before acting.

### D. User-invoked skills emulated and misrecorded; stage rules advisory (P1-7, P1-8, P2-10b, P2-19, P2-21)

**Invariant.** Every row of `P/skill-invocations.md` with mode `typed by user` or `native` has a
matching event in `JOURNAL/invocations/<session>.jsonl` (slash token at prompt head, or a
`Skill` tool use); no `docs/agents/*.md` line matches `standing authorization|invocation
authority`; `docs/agents/issue-tracker.md` carries the installed seed's required headings and a
`seed_sha256` that equals the cache file's hash.

**Enforcement point.** `UserPromptSubmit` (the only hook that sees the raw prompt head, hence
whether `/name` was the first token) and `PostToolUse` matcher `Skill` (records model
invocations) write the journal; `check:planning` rule modules (tracked record vs journal, grep,
seed hash) block at commit/`check`; `SessionStart` prints the drift notice. PreToolUse cannot
help: the failure is a missing receipt, not a wrong action.

**Mechanism.**
- `prompt_hook.py` rule `invocation_receipt`: if `prompt` starts with `/`, append
  `{"ts","session_id","kind":"slash","token":<first token>,"args_len":n,"caller":…}` to
  `JOURNAL/invocations/<session_id>.jsonl`; also when the prompt contains `<pasted_content`
  and a `/name` inside it, append `{"kind":"slash-in-paste","token"}` and print
  `additionalContext: "/name inside pasted text is not an invocation; the user must type it
  first"` (P1-7's exact trap). Unknown commands never reach UserPromptSubmit as user turns
  (`T:L565-566` are system lines), so class E's ledger captures them from the transcript
  instead (see E).
- `dev/hooks/post_tool.py` (PostToolUse, matcher `Skill`): append `{"kind":"skill",
  "name":tool_input.skill, "args", "tool_use_id"}` to the same journal.
- `dev/plan_invocations.py`: `usage: plan_invocations.py --check|--write [--session <id>]`.
  `--check` parses the Markdown table in `P/skill-invocations.md` and fails any `typed by
  user`/`native` row with no journal line (`name`, same day); `--write` appends generated rows
  (mode from the journal, SHA-256 of the skill file from the plugin cache path) above the
  hand-written notes. Receipt `{"rows":n,"unmatched":[…]}`.
- `dev/planning_checks/invocation_wording.py`: greps `docs/agents/*.md` and
  `P/skill-invocations.md` for `standing authorization|invocation authority|standing user
  request is the invocation` → one reason per hit (the D15 rewrite becomes permanent).
- `dev/planning_checks/seed_pin.py`: `docs/agents/issue-tracker.md` front matter line
  `<!-- seed: mattpocock-skills/<version> sha256=<hex> -->`; the rule hashes the installed
  seed (`$CLAUDE_PLUGIN_ROOT`-independent: path pattern `~/.claude/plugins/cache/mattpocock/
  mattpocock-skills/<version>/…/issue-tracker seed`) when present and compares; it fails on a
  missing pin, warns (not fails) when the cache is absent (CI), and fails when the doc lacks
  the seed's `##` headings (list kept in the rule as data).
- `session_start.py` rule `plugin_version`: prints `mattpocock-skills <installed> (pinned
  <recorded>)` when they differ.
- Skill/role docs: `ticket-retro.md:4-8` and `claude-takeover.md:11` rewritten per D15 (runbook
  step 7); `.claude/agents/retro-writer.md` step 0: "you are the repo procedure, not the
  `retro` skill; the user types `/mattpocock-skills:retro` at phase ends".

**Tests first** (`dev/test_prompt_hook.py`, `dev/test_plan_invocations.py`,
`dev/test_planning_checks.py`):
- T-D1 UserPromptSubmit `prompt="<pasted_content id=\"539c\">/mattpocock-skills:grill-with-docs …"`
  → journal line `kind: slash-in-paste` and the `additionalContext` warning; `prompt=
  "/mattpocock-skills:retro <path>"` → `kind: slash`.
- T-D2 `skill-invocations.md` fixture with the real row "to-spec … file-guided fallback
  (standing authorization…)" → `invocation_wording.py` lists the line; the rewritten row → none.
- T-D3 `plan_invocations.py --check` with a `typed by user` row and an empty journal → rc 2
  naming the row; with a matching journal line → rc 0.
- T-D4 `seed_pin.py` with a doc lacking the pin → one reason; with a pin whose hash ≠ a fixture
  seed → one reason; with a matching fixture → none.

**Ordering / ownership.** New ticket **CT-24 "Invocation receipts and seed pin"** (wave 2;
blocked by CT-15 for the `check:planning` runner and CT-22 for `prompt_hook.py`'s rule hook).
`owned_paths`: `dev/hooks/post_tool.py`, `dev/hooks/rules/invocation_receipt.py`,
`dev/plan_invocations.py`, `dev/planning_checks/invocation_wording.py`,
`dev/planning_checks/seed_pin.py`, `dev/test_plan_invocations.py`,
`dev/test_planning_checks.py` (shared file: each rule's tests live in
`dev/test_planning_checks_<rule>.py` instead, to keep lanes disjoint), `mise/tasks/ct24.toml`,
`docs/agents/issue-tracker.md` (pin line only), `P/skill-invocations.md`. The D15 wording edits
are wave-0 parent doc edits.

**Guardrails.** The five-stage verbs stay user-typed; nothing in this class invokes a skill.
The journal records; `--write` only appends generated rows and never rewrites hand-written
ones.

### E. No ledger of requests, decisions and pending operations (P1-6, P1-8, P1-9, P2-6, P2-8, P2-9)

**Invariant.** Every user-originated text (user turns, queued messages, rejected slash commands
turned into system lines) has a row in `P/requests/<session>.jsonl` with an id; before
`to-spec` or `to-tickets` output is recorded as approved, every request row is cited by a
spec/ticket/decision id or carries `disposition: declined` with a reason; every
`decision.kind == "operation"` (relabel #91, draft PR, close #n) has a `receipt` before
`plan:handoff --check` passes; `lanes/*.json tickets[]` ⊆ approved ticket ids.

**Enforcement point.** `UserPromptSubmit` for live user prompts (append); a transcript sweep for
queued/rejected messages (`plan:requests --import`, run at Stop and SessionStart because the
harness never delivers `T:L566`-shaped lines to a hook); `check:planning` for citation
completeness; `lane:allocate` for approved ids (the earliest point where an unapproved id
becomes a build); `Stop` lists unreceipted operations once.

**Mechanism.**
- Tracked files (parent-owned, under `P/`): `requests/<session_id>.jsonl` (one row per user
  text: `{id:"R-<session8>-<n>", ts, kind:"turn|queued|rejected-command", text[:2000],
  sha256, disposition:null|{cited:[…]|declined:<reason>}}`) and `decisions.jsonl`
  (`{id:"D-<n>", ts, kind:"approval|decision|operation", subject, text, source:<request id or
  transcript line>, receipt:null|{path,sha256,rc}}`). Both are append-only; `plan:decide`
  is the writer.
- `prompt_hook.py` rule `request_capture`: append the live prompt to
  `JOURNAL/requests/<session_id>.jsonl` (untracked); `dev/plan_requests.py --import <session>`
  lifts journal rows into `P/requests/<session>.jsonl` and, reading `transcript_path`, adds
  rows for `type: "user"` lines not yet seen and for `type: "system"` lines whose text starts
  with `Unknown command:`/`Args from unknown skill:` (kind `rejected-command`, text = the
  args). Bounded backward read like class A.
- `dev/plan_requests.py`: `usage: plan_requests.py import <session>|cite <R-id> <ref>…|decline
  <R-id> <reason>|check`. `check` fails on any row with `disposition: null` older than the
  current session, and on any `decisions.jsonl` operation without a receipt.
- `dev/plan_decide.py`: `usage: plan_decide.py approval --subject <id>… --source <R-id>` /
  `operation --subject "relabel #91" --source <R-id>` / `receipt <D-id> --path <p> [--rc n]`.
  `approval` rows are the machine token the to-tickets quiz lacked: `lane:allocate --ticket
  CT-xx` refuses an id that no `approval` row names (class N) and that no tracker issue carries.
- `stop_gate.py` rule `pending_operations`: block once with "operations without receipt:
  D-3 relabel #91, D-7 draft PR" when the parent stops and such rows exist (continuation
  allowed); `session_start.py` prints the same list as a line.
- `dev/planning_checks/requests_cited.py`: the `check:planning` rule that runs
  `plan_requests.py check`.
- Rule text (`issue-tracker.md` §Standing improvement workflow): "to-spec may close only when
  `plan:requests check` passes for the sessions it drew on; approvals are `plan:decide
  approval` rows, not chat".

**Tests first** (`dev/test_plan_requests.py`, `dev/test_plan_decide.py`, `dev/test_stop_gate.py`):
- T-E1 transcript fixture containing the `T:L565-566` shape (`system` lines "Unknown command:
  /cc-plugin-plugin-authoring" and "Args from unknown skill: create a claude mod …") → `import`
  creates one row `kind: rejected-command` whose text starts "create a claude mod".
- T-E2 `plan_requests.py check` with that row undispositioned → rc 2 naming `R-…`; after
  `cite R-… CT-13` → rc 0.
- T-E3 `decisions.jsonl` with `operation relabel #91` and no receipt → Stop blocks once, the
  reason names `D-…`; with `stop_hook_active: true` → no output; after `receipt D-… --path
  journal/… --rc 0` → no block.
- T-E4 `lane:allocate --ticket CT-02` with no approval row and no tracker issue (offline) → rc 2
  "CT-02 is not approved"; with an approval row → proceeds (scratch repo).
- T-E5 `plan_decide.py approval` twice for the same subject → second call is a no-op receipt
  (idempotent), file still append-only (byte prefix unchanged).

**Ordering / ownership.** New ticket **CT-25 "Request and decision ledger"** (wave 1 if a
fourth/fifth slot is admitted, else wave 2; blocked by none for the ledger, by CT-17 for the
allocate refusal). `owned_paths`: `dev/plan_requests.py`, `dev/plan_decide.py`,
`dev/hooks/rules/request_capture.py`, `dev/hooks/rules/pending_operations.py`,
`dev/planning_checks/requests_cited.py`, `dev/test_plan_requests.py`, `dev/test_plan_decide.py`,
`dev/fixtures/prevention/transcript-rejected-command.jsonl`, `mise/tasks/ct25.toml`,
`P/requests/`, `P/decisions.jsonl`, `docs/agents/issue-tracker.md` (one paragraph). The
`stop_gate.py` rule import line is a parent hunk at integration. Wave 0: the parent seeds
`P/decisions.jsonl` with the already-accepted operations (#91 relabel, draft PR, T4 Phase C
budget) so the first Stop of the next session lists them.

**Guardrails.** Operations stay user-confirmed: the ledger lists them, nothing executes them.
Request text is user content: rows store ≤ 2,000 chars and a hash; secrets pasted by the user
would be copied, so `import` masks `ghp_…`, `sk-…`, `AKIA…` patterns (same masks as CT-10).

### F. Agent roles and briefs not machine-sourced; harness agent list frozen (P1-12, P2-10b, P2-20, P2-23)

**Invariant.** Every `Agent` call whose prompt carries `LANE-UNIT: <u>` uses `subagent_type ∈
{implementer, doc-writer, reviewer, retro-writer}` or carries `AGENT-FALLBACK: <role>` with
the role body inlined; a lane brief is ≤ 1.5 KB of pointers; an implementer transcript
contains a `Skill` tool use of `tdd` (or the preloaded skill marker) before its first `.py`
Write; the set of `.claude/agents/*.md` names at SessionStart equals the set on disk at
dispatch time, else the dispatch reason says "restart".

**Enforcement point.** `PreToolUse` matcher `Agent` (sees `subagent_type`, `prompt`, and the
disk state; the only point before the brief is spent); `SessionStart` (records the roster the
session was started with, which is what the harness watcher covers); `SubagentStop` (transcript
scan for `tdd` — too late to prevent, but it turns "code-first" into a block with a reason
instead of a retro row the parent waives).

**Mechanism.** Extends CT-19 (`lane:brief`, agent constants, receipt journal):
- `session_start.py` rule `agent_roster`: writes `JOURNAL/sessions/<session_id>.json`
  `{"started":ts,"agents_dir_existed":bool,"agents":[names from frontmatter],"source":…}`
  and prints `agents on disk: implementer, doc-writer, reviewer, retro-writer, extractor`. If
  `.claude/agents/` did not exist (or was empty) the line says "no project agents; creating
  `.claude/agents/` later needs a restart (sub-agents docs)".
- `agent_gate.py` rule `lane_dispatch`: for a prompt containing `LANE-UNIT:`:
  (1) `subagent_type == "general-purpose"` and the role exists on disk → deny: "use
  subagent_type: <role>; if the harness refuses the name, the agents directory was created
  after this session started: restart, or pass `AGENT-FALLBACK: <role>` with
  `lane:brief --inline-role`"; (2) `AGENT-FALLBACK:` present → allow and journal the fallback
  (`JOURNAL/<unit>.jsonl` line `kind: fallback-dispatch`); (3) prompt > 1,536 bytes before the
  judgement section marker `JUDGEMENT:` → deny "brief is <n> bytes; use lane:brief output +
  judgement"; (4) the roster recorded at SessionStart lacks a name that exists on disk now →
  `additionalContext: "agent <name> was added after session start; the Agent tool may not
  list it"`.
- `dev/lane_brief.py` (CT-19): `--inline-role <role>` appends the role's Markdown body
  (frontmatter stripped) under `AGENT-FALLBACK: <role>` for use with `general-purpose`;
  `--role reviewer` always emits the `CODING_STANDARDS.md` and `base_sha` slots (P2-20).
- `dev/hooks/subagent_receipt.py` (CT-19) rule `tdd_first`: for `agent_type == implementer`
  (or fallback marker), scan `agent_transcript_path` for the first `tool_use` named `Skill`
  with `tdd` (or the preload marker `<skill name="mattpocock-skills:tdd">` in the first
  system/user line) and the first `Write`/`Edit` of a `.py` path that is not `test_*.py`; if
  code precedes the red test, block once with "write the failing test first (tdd); record the
  deviation in the retro if it was deliberate".
- `.claude/agents/*.md`: constants moved in (R7 E list); `reviewer.md:18` "arrives with CT-04"
  stale text removed; each role gets a frontmatter `hooks: {Stop: [...]}`? No — settings-level
  `SubagentStop` with matcher `^(implementer|doc-writer|reviewer|retro-writer)$` keeps one
  journal script (frontmatter hooks need workspace trust and duplicate wiring).
- Rule text (`claude-team.md` §Roles): "`.claude/agents/*.md` are committed and present before
  the session that dispatches them; a session that creates the directory restarts".

**Tests first** (`dev/test_agent_gate.py`, `dev/test_session_start.py`,
`dev/test_subagent_receipt.py`, `dev/test_lane_brief.py`):
- T-F1 PreToolUse Agent, `subagent_type: general-purpose`, prompt from the real gate-hooks brief
  (`LANE-UNIT: gate-hooks`, 5.3 KB) with `.claude/agents/implementer.md` on disk → deny; the
  reason names `implementer` and `restart`.
- T-F2 same with `subagent_type: implementer` and a 1.2 KB prompt → allow; with 5.3 KB → deny
  on size.
- T-F3 SessionStart with an empty temp project (no `.claude/agents`) → the "needs a restart"
  line; with the five files → the roster line and a journal file listing five names; a later
  PreToolUse after adding `extra.md` → `additionalContext` naming `extra`.
- T-F4 SubagentStop with `agent_type: implementer` and a fixture agent transcript where the
  first `.py` Write precedes any `Skill(tdd)` → `decision: block`; transcript with `tdd` first
  → no output; `stop_hook_active` → no output.
- T-F5 `lane:brief --role implementer --inline-role implementer` ≤ 1.5 KB without the inline
  body, and the inline body equals `implementer.md` minus frontmatter.

**Ordering / ownership.** CT-19 (wave 2): `lane_brief.py`, `subagent_receipt.py` with
`tdd_first`, agent constants, T-F4/F5. **CT-22** wave 0 ships the `agent_roster` SessionStart
line and the `lane_dispatch` deny rule (1) only (both small; the restart cause recurs every
session). Rules (2)–(4) and T-F1–F3 go to a new ticket **CT-26 "Agent dispatch rules"**
(wave 3, after CT-19 so the fallback marker exists). `owned_paths` CT-26:
`dev/hooks/rules/lane_dispatch.py`, `dev/hooks/rules/agent_roster.py`,
`dev/test_agent_gate.py` (shared with CT-22: CT-22 lands first and CT-26 extends it;
sequential, not parallel), `mise/tasks/ct26.toml`, `docs/agents/claude-team.md` (§Roles
paragraph).

**Guardrails.** No hook changes `subagent_type` (`updatedInput` is not used: a silently
retargeted dispatch would hide the restart condition from the user); a deny names the fix.
Reviewer dispatches are never blocked on size (they carry the implementer's claims).

### G. Subagent reports condensed by the parent; no machine receipt (P1-2, P1-4, P2-4, P2-5, P2-22, P2-25)

**Invariant.** Every SubagentStop of a lane role appends `{ts, agent_id, agent_type, unit,
agent_transcript_path, last_assistant_message[:4000], tip, disposition?, findings:[P-n…]}` to
`JOURNAL/<unit>.jsonl`; `lanes/<u>.json review` = the journal's last reviewer disposition
(`lane:set --from-journal`); every `P-n` in the last reviewer message has a row in
`retros/<u>.md`; synthesizer/brief outputs land in tracked `P/codex-briefs/<thread>.md`;
`resource_admissions.network ∈ {none, admitted:<id>}` with a prep receipt.

**Enforcement point.** `SubagentStop` matcher `^(implementer|doc-writer|reviewer|retro-writer)$`
(the earliest place the final report exists as data; it survives the parent's death);
`lane:validate` (`review` ≠ journal → fail); `retro_gate.py` cross-check (class H); PreToolUse
`Write` deny for `/private/tmp`, `scratchpad` paths when the prompt is a lane (class L).

**Mechanism.** Extends R7 L and CT-19:
- `subagent_receipt.py`: unit from the `LANE-UNIT:` line of the first user message in
  `agent_transcript_path`, else the `cwd` branch; `disposition` parsed from the last message
  (`^(PASS|PASS-with-P[23]|FAIL)\b`), `findings` = every `P[123]-\d+` token; `tip` =
  `git rev-parse HEAD` in `cwd`. Writes one line; never blocks on its own (the gate script
  `subagent_stop_gate.py` keeps the retro block). Exit 0 always; a write failure prints a
  `systemMessage`.
- `dev/lane.py set --from-journal <unit>`: lifts `lane_commit` (implementer tip), `review`
  (`{disposition, sha, agent, journal_line}`) and refuses when the journal's tip is not a
  commit on `branch` (the "subagent receipt SHA absent from the parent's records" case:
  `validate` reports `journal tip <sha> not on branch <b>`).
- `retro_gate.py` (class H) gains `--journal JOURNAL/<unit>.jsonl`: every `P-n` in the last
  reviewer line needs a retro row containing that token.
- `lane:allocate --admit network=none|admitted:<id>` (CT-17) runs `tools:prepare`/`deps:sync`
  with `--offline` when `none`, records `{"prep_mode":"offline","tools_prepare":rc,
  "deps_sync":rc}` in the record; `lane:validate` requires the key (CT-05).
- Synthesizers: the brief template (`codex-session-history/references/brief-template.md`)
  gains item ids `[B-<thread8>-<n>]`; the parent's rule (`claude-team.md`) is that a
  synthesizer writes `P/codex-briefs/<thread>.md` itself (tracked, inside its allowlist) and
  `findings.md` cites item ids. `record_guard.py` (class L) denies record writes citing
  `/private/tmp` or `scratchpad`.

**Tests first** (`dev/test_subagent_receipt.py`, `dev/test_lane.py`, `dev/test_retro_gate.py`):
- T-G1 SubagentStop event `{agent_type:"reviewer", agent_transcript_path:<fixture with
  "LANE-UNIT: gate-hooks" and a last message "PASS. P3-1 …">, cwd:<root>}` → one journal line
  with `unit: gate-hooks`, `disposition: PASS`, `findings: ["P3-1"]`; the root `cwd` does not
  prevent unit resolution (the P3 at `retros/gate-hooks.md:18`).
- T-G2 `lane:set gate-hooks --from-journal` on the T-G1 journal → `review.disposition == "PASS"`
  and `status` unchanged; with a journal tip not on `claude/gate-hooks-wiring` → rc 2.
- T-G3 `retro_gate.py --unit x --journal <jsonl>` where the reviewer line names `P2-3` and the
  retro has no `P2-3` row → rc 2 "finding P2-3 has no disposition row".
- T-G4 `lane:validate` on a record with no `resource_admissions.network` → rc 2.
- T-G5 PreToolUse Write to `P/findings.md` with content citing `/private/tmp/claude-501/…`
  → deny naming `P/codex-briefs/` (class L rule, tested here for the brief path).

**Ordering / ownership.** CT-19 (wave 2): `subagent_receipt.py`, T-G1; CT-05 (wave 1):
`--from-journal`, network key, T-G2/G4; **CT-27 "Retro-gate truth checks"** (class H, wave 2,
after CT-11 which owns `retro_gate.py` in wave 1): `--journal`, T-G3; brief-template ids and
the synthesizer rule → CT-10 (wave 4). The settings `SubagentStop` matcher entry is a parent
hunk at CT-19 integration.

**Guardrails.** The journal is local and untracked (`.gitignore` frozen; `COMMON` is outside
the tree); `last_assistant_message` is truncated at 4,000 chars and masked for the secret
patterns before writing; the parent lifts, hooks never write records.

### H. Shape-checked gates mistaken for truth (P1-5, P1-10, P1-13, P2-4, P2-22)

**Invariant.** Every `dev/test_*.py` and `dev/**/test_*.py` is run by `check` discovery, by a
`test:*` task in `check:research` depends, or sits in an explicit exemption list with a reason;
`retros/<u>.md` exists for every record with `retro: passed` and `retro_gate.py --unit <u>`
is 0 on the tree; a deferral row naming `CT-nn` cites an item id `CT-nn/<k>` that exists in the
ticket body (manifest or tracker snapshot); a retro claim `rc 0`/`hk validate`/`PASS` for a
named check names a receipt path (`JOURNAL/checks/<sha>.json` or `P/lanes/<u>.log.md` line)
with that rc; every `ROOT / "evidence/…"` constant with a pinned SHA resolves to a tracked file
with that SHA.

**Enforcement point.** `check` (rule modules in `dev/checks/`, run by every lane and by
`lane:integrate`); `retro_gate.py` itself (it is already the gate the hooks call, so stricter
checks there propagate to all three layers at once); hk `pre-commit` `records` step for the
unit↔path check (cheap).

**Mechanism.**
- `dev/checks/unwired_tests.py` (CT-12, R7 H): globs tests, parses `mise.dev.toml` and
  `mise/tasks/*.toml` for `run` strings naming each file, reads `check.py`'s discovery globs
  (exposed as `DISCOVERY` in `check.py`), applies `dev/checks/exemptions.toml`; prints
  `unwired test: <path>`.
- `dev/checks/pinned_paths.py`: AST-scans `dev/**/*.py` for `ROOT / "evidence/..."` (and
  string constants under `evidence/`) paired with a 64-hex constant within 3 lines; each must
  be `git ls-files`-tracked and hash-equal; prints `pinned path missing: <path> (<module>:<line>)`.
  Fixture reproduces `codex_examples.py:25-26` (P1-10).
- `retro_gate.py` additions (CT-27): (a) `--unit <u>` requires `retros/<u>.md` *or* a record
  field `retro_record` pointing at the file (the a06 alias); `lane:validate` requires the
  field when the names differ; (b) deferral rows: a row whose disposition names `CT-\d+` must
  also name `CT-\d+/\d+` and the id must exist in `P/proposals/**/tickets*.json` (`items[]`,
  minted by `build_manifests.py`, class N) or in `P/ticket-ledger.json` snapshot; (c) named-check
  claims: a row/line matching `(rc 0|hk validate|check:acceptance-baseline …)` must be followed
  within the row by `receipt:<path>` whose file exists and whose `rc` field equals the claim;
  `lane:integrate`/`check` write `JOURNAL/checks/<tree-sha>-<task>.json` receipts
  (`{task, rc, tree, started, ended, selectors}`) so the claim can point at them;
  (d) `--journal` (class G).
- `mise/tasks/ct12.toml`: `test:retro-gate` (`-p test_retro_gate.py`), `test:hooks-session`
  etc. are listed in `check:research` depends by the parent hunk; `check.py` runs
  `dev/checks/*.py` (wave-0 one-liner).

**Tests first** (`dev/test_check_wiring.py`, `dev/test_pinned_paths.py`, `dev/test_retro_gate.py`):
- T-H1 fixture tree with `dev/test_x.py` and no task → `unwired_tests.py` prints the path;
  with `[tasks."test:x"] run = "… -p test_x.py"` and `check:research` depends listing it → none;
  the live repo at HEAD lists `dev/test_retro_gate.py` (red until `test:retro-gate` exists).
- T-H2 fixture module `ROOT / "evidence/codex-examples/release/config-schema.json"` with a
  SHA, file untracked → one reason; tracked with matching hash → none.
- T-H3 `retro_gate.py --unit a06-unit3` in a scratch plan with `retros/a06-classification-methods.md`
  and no `retro_record` → rc 2 "retro record missing: … (lane record names
  a06-classification-methods.md; set retro_record)"; with the field → rc 0.
- T-H4 retro row `| … | deferred to CT-02 |` → rc 2 "deferral cites no item id"; `CT-02/3`
  present in the manifest items → rc 0; `CT-02/9` absent → rc 2.
- T-H5 retro line "`hk validate` rc 0 (2.6.0 and 2.5.0)" with no `receipt:` → rc 2 "claim
  without receipt"; with `receipt:JOURNAL/checks/<sha>-hk-validate.json` holding `rc 0` → 0;
  holding `rc 2` → rc 2 "receipt rc 2 contradicts claim".

**Ordering / ownership.** CT-12 (unwired tests; R8 says wave 1 if a slot frees else wave 3 —
with the `dev/checks/` discovery line in wave 0 it no longer edits `check.py`, so it can run in
wave 1 as a fifth small lane): `dev/checks/unwired_tests.py`, `dev/checks/exemptions.toml`,
`dev/test_check_wiring.py`, `mise/tasks/ct12.toml`. **CT-27** (wave 2, blocked by CT-11):
`dev/retro_gate.py`, `dev/test_retro_gate.py`, `dev/fixtures/retros/*` new cases,
`dev/checks/pinned_paths.py`, `dev/test_pinned_paths.py`, `mise/tasks/ct27.toml`. `check.py`
receipt writing (`JOURNAL/checks/`) belongs to CT-11 (it already touches `check.py` for the
lock and the receipt is the lock's natural output).

**Guardrails.** Stricter gate rules apply to new records; existing records that fail (b)/(c)
are listed by `retro_gate.py --all` and corrected by the parent in a docs commit before CT-27
integrates (runbook row), so the Stop gate does not start blocking on history.

### I. Configuration composition and cross-tool contracts unvalidated (P1-2, P1-3, P2-5, P2-15, P2-16, P2-21)

**Invariant.** `keys(.claude/settings.json) ⊆ {$schema, hooks, enabledPlugins,
extraKnownMarketplaces, env, autoCompactEnabled, autoCompactWindow}`; `permissions`,
`skillOverrides`, `statusLine`, `model`, `additionalDirectories` ∉ keys; every
`enabledPlugins` marketplace is declared in `extraKnownMarketplaces` of the same file; `hooks`
reference existing scripts under `dev/hooks/` with `timeout ≤ 15` and `onFailure: block` only on
PreToolUse/Stop/SubagentStop; `env` carries `PLAN_ID` (project) and the local file carries
`PWF_PLAN_ROOT`, `PWF_TRUSTED_PYTHON`; `P/.mode` ∈ {`inject-smart`}; `hooks:install` ⇒
`safe_configured_hooks` accepts the result; the repo's Stop hook and the plugin's Stop hook are
both documented and tested on one payload.

**Enforcement point.** PreToolUse `Write|Edit` on `.claude/settings*.json` (projected content;
the lane commit `0c2748e` at 20:44Z is where it would have fired); hk `pre-commit` `records`
step (`settings_check.py --staged`); `check` rule module; `ConfigChange` is audit-only (its
block is silent).

**Mechanism.** CT-16 (as written) plus:
- `dev/settings_check.py`: `usage: settings_check.py [--staged] [--file <path>] [--json]`.
  Allowed-key set, forbidden-key set and hook constraints as data at the top; `--staged` reads
  `git show :.claude/settings.json`. Also validates `.claude/settings.local.json` **exists in
  `.git/info/exclude`** (it does) and never validates its content (personal). Exit 2 per
  violation `settings.json: key 'permissions' is personal (settings.local.json)`.
- `record_guard.py` rule `settings_schema`: deny a Write/Edit of `.claude/settings.json`
  whose projected content fails the check; allow `settings.local.json`.
- `dev/checks/settings_schema.py`: runs the same function inside `check`.
- `dev/planning_checks/pwf_mode.py`: `P/.mode` content and `env` pins (project `PLAN_ID`; the
  local pins are reported, not required, in CI).
- `test_hooks.py` (CT-02b) gains `test_two_stop_hooks_compose`: runs `stop_gate.py` and the
  plugin's `claude-hook.sh stop` (skipped when the cache is absent) on one payload and asserts
  at most one `decision: block`.
- `hooks_install.py` guard (class C) and the `delivery:inspect-hooks` dry run (T-C6).
- Docs: `.claude/AGENTS.md` names the key list by pointing at `settings_check.py`'s data
  block; `docs/agents/claude-team.md` §Hooks lists both Stop hooks and the rule "the plugin's
  `.mode` never carries `gate`"; fnox ≥ 1.39.0 and the exec-scoped route recorded in
  `docs/agents/` (N1, D4).

**Tests first** (`dev/test_settings_check.py`, `dev/test_record_guard.py`):
- T-I1 the staged `e12cf04:.claude/settings.json` bytes as fixture → rc 2 with two reasons
  (`permissions`; `enabledPlugins` marketplace `claude-community` undeclared); R5 §B's project
  file → rc 0.
- T-I2 a file whose `hooks.PreToolUse[0].hooks[0].command` names a missing script → rc 2.
- T-I3 PreToolUse Write of `.claude/settings.json` with `permissions` → deny; the same path
  `.claude/settings.local.json` → no output.
- T-I4 `pwf_mode.py` with `.mode` = `gate` → reason; `inject-smart` → none; missing `env.PLAN_ID`
  → reason.
- T-I5 the two Stop hooks on the T-C3 payload → ≤ 1 block.

**Ordering / ownership.** CT-16 → renamed in scope to **"Settings composition check"** stays
the owner of `dev/settings_check.py`, `dev/test_settings_check.py`,
`dev/checks/settings_schema.py`, `dev/planning_checks/pwf_mode.py`, `.claude/AGENTS.md`
(key-list pointer). It is gated on D4 (decided in wave 0) and no longer on CT-02 (the merge is
finished in wave 0), so it moves to **wave 1** as a small lane. CT-23 owns the
`record_guard.py` rule (imports `settings_check`). T-I5 belongs to CT-02b. The project
settings file itself is a wave-0 parent edit (R5 §B composition + the keys in §Settings).

**Guardrails.** Personal keys and `~/.claude/*` are never edited by a hook or task; the check
reads the local file only for existence in the exclude list. The `permissions.allow` rules the
user wants stay in `settings.local.json` (user-owned).

### J. Gate hooks without a real-command corpus or latency contract (P2-3)

**Invariant.** On the corpus of real session commands, the gate yields an action for exactly
the real `git merge|push|lane:integrate|delivery:publish*` segments; wall time per hook call <
`HOOK_BUDGET_S` (6 s) < configured `timeout` (10 s), else the output is a deny with a reason;
`GATE_TIMEOUT × lanes` never exceeds the budget (the gate caps lanes per call and reports the
rest).

**Enforcement point.** `test:hooks` (corpus + latency assertions, run in every lane and by
`check:research`); PreToolUse self-timing (the hook measures itself and degrades to
deny-with-reason).

**Mechanism.** CT-02b (R7 O) plus:
- `git_gate.run_gate` takes a `deadline` (monotonic) and `check_lanes` stops at the deadline,
  returning a refusal "gate budget exhausted after <k> of <n> lanes; rerun retro:gate for
  <remaining>" (fail closed, with words).
- `pretooluse_gate.py --dry-run` (class C) and `--time` (prints `{"ms":n,"actions":[…]}`).
- Corpus fixture `dev/fixtures/prevention/bash-corpus.jsonl` with `expect` per row; a second
  file `bash-corpus-synthetic.jsonl` adds `/usr/bin/git merge`, `env X=1 git push`,
  `git -C ../other merge`, `git cherry-pick`, `git rebase lane`, `git pull --ff`,
  `cat <<'EOF'\ngit merge x\nEOF`, `echo "git push"`.
- The `Hooks: PreToolUse:Bash […] finished with status 0 (Nms)` debug line is the field
  receipt; `test:hooks` asserts the hook's own `--time` on the corpus p95 < 500 ms with 10
  passing lane records.

**Tests first** (`dev/test_hooks.py`): T-C1, T-C7, plus T-J1 `--time` p95 assertion; T-J2 the
synthetic corpus row-by-row expectations.

**Ordering / ownership.** CT-02b (wave 1 #1). Fixture extraction (parent, wave 0, no code).

**Guardrails.** The corpus is sanitized (paths under `$HOME` replaced, no transcript bodies).

### K. Planning files unstructured for the plugin; progress by append; no host pin (P1-11, P2-13, P2-14, P2-15)

**Invariant.** `task_plan.md` has `## Goal`, `## Next Step`, `## Current Phase`, `## Phases` with
exactly one `in_progress` `### Phase`, `## Lanes` regenerated; `size(progress.md) < 900 KB`;
`check-complete.sh` says "in progress (k/n)"; from any lane worktree the pretool view shows the
root nonce; `env.PLAN_ID` set in project settings.

**Enforcement point.** `check:planning` (every lane + integration); PreToolUse `Write|Edit`/
Bash append guard on `progress.md` size (the append at 900 KB is the moment); `SessionStart`
probe of injected bytes (visibility); `plan:log` refusal.

**Mechanism.** CT-15 (`dev/plan_records.py`: `plan:log`, `plan:handoff`, `check:planning`
runner over `dev/planning_checks/*.py`) plus:
- `dev/planning_checks/skeleton.py`: headings, single `in_progress`, Lanes table == records
  projection (uses `lane.py`'s loader).
- `dev/planning_checks/progress_size.py`: `size < 900 KB` and the NEXT bullet in the last 20
  lines.
- `record_guard.py` rule `progress_size`: deny a Write/Edit to `progress.md` whose projected
  size ≥ 900 KB or that removes bytes before the last entry (append-only), reason "run
  plan:log / archive per planning-records.md". Bash `cat >>` appends are caught by the
  `check:planning` rule at the next commit (hk pre-commit `records` step includes
  `progress_size`).
- `session_start.py` rule `pwf_probe`: runs `inject-plan.py --context=pretool` from the plugin
  cache when present with a 2 s budget and prints `pwf: <bytes> bytes, nonce <8>`; prints
  `pwf: injection dark` when 0 bytes.
- Settings: `env.PLAN_ID` project; `PWF_PLAN_ROOT`, `PWF_TRUSTED_PYTHON`, `PWF_INJECT` local.
  Whether `env` reaches hook processes is unverified (R4): the SessionStart hook also writes
  `export PLAN_ID=…` to `CLAUDE_ENV_FILE` so Bash commands get it either way.

**Tests first** (`dev/test_plan_records.py`, `dev/test_record_guard.py`):
- T-K1 the current `task_plan.md` head (fixture) → `skeleton.py` lists "0 `### Phase`"; the R4
  skeleton → none.
- T-K2 a 901 KB `progress.md` → `progress_size.py` reason; PreToolUse Edit that would push the
  file over 900 KB → deny.
- T-K3 `plan:log "x"` keeps NEXT last and refuses at the cap (R7 F).
- T-K4 SessionStart with the plugin cache absent → `pwf: not installed`; with a fake
  `inject-plan.py` printing 2 KB → `pwf: 2048 bytes`.

**Ordering / ownership.** CT-15 (wave 1 #4): rules, T-K1/K3; CT-23 (wave 2): `progress_size`
guard rule, T-K2; CT-22 (wave 0/1): `pwf_probe` line, T-K4. The one-time migration is runbook
step 8 (parent, wave 0).

**Guardrails.** Hooks never write planning files; `plan:log` is the writer (D12 archive is a
parent decision).

### L. Outputs in ephemeral or untracked locations (P1-10, P2-7, P2-18, P2-24, P2-25)

**Invariant.** Every path a record cites resolves to a tracked path, a `JOURNAL/` path, or a
`~/.codex` path with a recorded SHA; no record cites `/private/tmp`, `/var/folders`,
`scratchpad`; untracked top-level entries are tracked, in `.git/info/exclude`, or listed in
`P/untracked.toml` with a reason; `import_source.data[]` lists every data file a lane's code
reads with its SHA and the data is tracked before `integrated`.

**Enforcement point.** PreToolUse `Write|Edit` on `P/**` and `docs/**` (deny the citation at
write time); `check:planning` citation resolver; `lane:validate` for `import_source.data`;
`session:status` untracked list; `lane:integrate` preflight.

**Mechanism.**
- `dev/planning_checks/citations.py`: regex over `P/{findings,task_plan,progress}.md`,
  `P/lanes/*.json`, `P/retros/*.md`, `docs/agents/*.md` for absolute paths and backticked
  relative paths; classify; fail on scratch/tmp; fail on relative paths that neither exist in
  `git ls-files` nor under `JOURNAL/`; `~/.codex/…` requires `sha256=` within the same line.
- `record_guard.py` rule `citations`: same classifier on projected content for writes under
  `P/` and `docs/`.
- `dev/exclude_sync.py`: `usage: exclude_sync.py --check|--write`, source of truth
  `dev/exclude.txt` (tracked: `.claude/worktrees/`, `.claude/settings.local.json`, `.agent/`,
  `.agents/`, `dev/hooks/__pycache__/`); `--write` rewrites the managed block of
  `.git/info/exclude`; `session_start.py` runs `--check` and prints drift (`.gitignore` stays
  frozen until CT-08).
- `lane.py`: `allocate --import <worktree> --data <path>…` fills `import_source.data`
  (`{path, sha256, tracked:bool}`); `validate` fails `integrated` with any `tracked:false`;
  `dev/checks/pinned_paths.py` (class H) catches the code side.
- Durable defaults recorded in `claude-team.md` §Where outputs go: briefs → `P/codex-briefs/`,
  drafts → `P/proposals/<spec>/drafts/`, backups/snapshots → `JOURNAL/snapshots/`, task outputs
  → `JOURNAL/<unit>.jsonl`, journals of tracker operations → `P/proposals/<spec>/journal/`.
  Subagent briefs say "write your report to <tracked path>" (lane:brief slot).

**Tests first** (`dev/test_planning_checks_citations.py`, `dev/test_exclude_sync.py`,
`dev/test_lane.py`):
- T-L1 `findings.md` fixture citing `/private/tmp/claude-501/…/tasks/abc.output` → one reason;
  citing `.planning/…/reviews/ccm-20261013/settings.json.before-ct02` untracked → one reason;
  same path tracked → none; `~/.codex/worktrees/2a14/... sha256=<hex>` → none.
- T-L2 `exclude_sync.py --check` with `.agent/` present and absent from exclude → rc 2;
  `--write` then `--check` → 0; the unmanaged lines of `exclude` are preserved byte-for-byte.
- T-L3 `a06-unit3` record with `import_source.data: [{path: evidence/codex-examples/release/
  config-schema.json, tracked: false}]` and `status: integrated` → `validate` rc 2.

**Ordering / ownership.** New ticket **CT-28 "Durable artifact locations"** (wave 2; blocked by
CT-15 runner, CT-05 schema). `owned_paths`: `dev/planning_checks/citations.py`,
`dev/exclude_sync.py`, `dev/exclude.txt`, `dev/hooks/rules/citations.py`,
`dev/test_planning_checks_citations.py`, `dev/test_exclude_sync.py`, `mise/tasks/ct28.toml`,
`docs/agents/claude-team.md` (§Where outputs go), `P/untracked.toml`. Wave 0: the parent runs
R3 sweep A / records `settings.json.before-ct02` by moving it under `P/reviews/…` tracked
(runbook step 10) and adds `.agent/` to the exclude file by hand.

**Guardrails.** `exclude_sync --write` touches only the managed block; `.gitignore` is never
written (baseline).

### M. Codex thread/packet state imported by hand (P2-9, P2-10, P2-11, P2-12, P2-24)

**Invariant.** The activation record's machine fields (`threads[].last_turn_status`,
`failed_children`, `active_automations`, `packet_writer_thread`, `newest_manifest_status`,
`worktrees[].dirty`) equal `codex:status` output at the record's timestamp; every superseded
packet holds `SUPERSEDED-BY-CLAUDE.json`; `findings.md` "Inherited limitations" is generated
with a manifest path and timestamp.

**Enforcement point.** mise `codex:status` (the skill's scripts, run at takeover and by
`session_start.py` with a budget when `~/.codex` exists); `check:planning` field compare
(`claude-takeover.md` gains a fenced JSON block the rule parses); PreToolUse is irrelevant (no
single tool call is the failure).

**Mechanism.**
- `.claude/skills/codex-session-history/scripts/codex_status.py` (mirrored to
  `.agents/skills/`): `usage: codex_status.py [--cwd <substr>] [--days N] [--json]`; composes
  `codex_threads.py list/turns/children`, `~/.codex/automations/*/automation.toml` (ACTIVE +
  rrule), packet ledgers (`lane-ledger.json` writer thread), the newest research manifests'
  statuses, and `git worktree list --porcelain` + per-worktree `status --short | wc -l` for
  `~/.codex/worktrees/*`; prints one JSON document. Read-only, bounded (sqlite row limits),
  2 s per source with a receipt of what timed out.
- `codex_status.py supersede <packet-dir> --by <session-id>` writes
  `SUPERSEDED-BY-CLAUDE.json` `{by, at, activation_record_sha}` into the packet (the one
  mutating subcommand; user-confirmed per packet).
- `docs/agents/claude-takeover.md` activation record: a fenced ```json codex-status``` block
  generated by `codex:status --json`; prose stays for decisions.
- `dev/planning_checks/codex_activation.py`: compares the block to a fresh
  `codex_status.py --json` when `~/.codex` is readable (else reports "not comparable"); fails
  on differing machine fields; also requires `findings.md` "Inherited limitations" lines to
  carry `manifest: <path> @ <ts>`.
- `session_start.py` rule `codex_status`: prints one line (ACTIVE automations count, dirty
  worktrees count, packets without supersession) when `~/.codex` exists; budget 2 s.

**Tests first** (`dev/test_codex_session_history.py` extension, fixture-backed temporary
`CODEX_HOME`): T-M1 fixture sqlite with eight failed children → `codex_status.py --json`
reports `failed_children: 8`; T-M2 an `automation.toml` ACTIVE → listed; T-M3 activation block
saying `failed_children: 0` against T-M1 → `codex_activation.py` one reason; T-M4 `supersede`
writes the file and is refused when it exists.

**Ordering / ownership.** New ticket **CT-29 "codex:status probe and packet supersession"**
(wave 3; blocked by CT-10's mask rule for shared script conventions, CT-15 runner).
`owned_paths`: both skill subtrees' `scripts/codex_status.py`, `dev/test_codex_session_history.py`
(CT-10 also edits it: sequential, CT-10 first or CT-29 takes a new `dev/test_codex_status.py`
— choose the latter), `dev/planning_checks/codex_activation.py`, `mise/tasks/ct29.toml`,
`docs/agents/claude-takeover.md` (JSON block). Wave 0: R3 sweep B writes the supersession files
by hand after the user admits it (D11).

**Guardrails.** Probe is read-only; `supersede` is per-packet and user-confirmed; digests stay
in the scratchpad (D13) and only paths/hashes enter records; commit subjects masked (CT-10).

### N. Ticket pipeline unvalidated before build (P1-6, P2-6, P2-7)

**Invariant.** `P/proposals/**/tickets*.json`: `parent_number` ∈ ℕ⁺ ∪ {null} and never a
placeholder (`999999`), unique `local_id`s, acyclic in-set `blocked_by`, builder docstring count
= `len(TICKETS)`, every ticket has `items[]` with ids `CT-nn/k`, builder reads only repo-relative
inputs; `lanes/*.json tickets[]` ⊆ tracker issues ∪ `approval` decisions.

**Enforcement point.** `check` rule module (fails the manifest commit `d0d6d4d` shape);
`lane:allocate` refusal (the moment a ticket becomes a lane); `issue:create-preview` dry run
(offline) as the publication preflight.

**Mechanism.**
- `dev/checks/proposals.py`: validates every `P/proposals/**/*.json` whose `schema` or shape
  marks it as a creation manifest (reuse `dev/issue_create.py`'s `manifest()` for syntax, then
  the extra rules); scans `build_manifests.py` for a path literal escaping the proposal dir
  (`../..`, `/private`, `scratchpad`) and for `parent_number` placeholders.
- `build_manifests.py` (per proposal) gains `items` per ticket (acceptance bullets numbered
  `CT-nn/k`) and refuses `PARENT` values ≥ 10⁶ or non-numeric; a `--offline-preview` flag
  prints the `issue:create-preview` intent without network.
- `lane.py allocate --ticket <ref>`: `ref` must be `#<n>` (verified against
  `P/ticket-ledger.json` snapshot or `gh issue view` when online) or `CT-nn` with an
  `approval` decision (class E); else rc 2 "ticket CT-02 unresolved: approve it (plan:decide
  approval) or publish it".
- `issue:create-preview` already exists; `mise/tasks/ct30.toml` adds `proposals:check`.

**Tests first** (`dev/test_checks_proposals.py`, `dev/test_lane.py`): T-N1 the committed
`tickets.preview.json` (`parent_number: 999999`, CT-11 before CT-10, edges CT-08←CT-02) → three
reasons; T-N2 a cyclic `blocked_by` → reason; T-N3 builder fixture with `../../drafts/…` →
reason; T-N4 `allocate --ticket CT-02` offline, no approval → rc 2 (shared with T-E4).

**Ordering / ownership.** New ticket **CT-30 "Proposal validator and allocation refusal"**
(wave 2; the allocate part is CT-17's, so CT-30 owns the validator and the builder changes;
CT-17 imports `plan_decide.approved()` from CT-25). `owned_paths`: `dev/checks/proposals.py`,
`dev/test_checks_proposals.py`, `P/proposals/claude-takeover-spec/build_manifests.py`,
`mise/tasks/ct30.toml`. R2's publication fixes 2–5 remain runbook step 11 (parent, wave 0),
re-run through `proposals:check` before `issue:create-apply`.

**Guardrails.** No batch apply; every `issue:*-apply` stays a single confirmed step; the
validator never calls the network (`inventory()` is the online step the user triggers).

---

## Specifics for the two new causes

### (A) Context budget and `autoCompactEnabled: false`

- **What the project can set** (`.claude/settings.json`, wave 0): `"autoCompactEnabled": true`
  and `"autoCompactWindow": 700000`. Both keys are "Any file" scope and the shared project file
  outranks `~/.claude/settings.json` in the documented stack. What it cannot override: an
  environment `DISABLE_AUTO_COMPACT=1` (documented as sticky-off) and, unverified, the
  `~/.claude.json` copy of `autoCompactEnabled` (that file holds "global config keys" the CLI
  writes for itself; whether its value participates in the stack is not documented in the
  pages fetched). Hence the SessionStart line reports the effective state and the user decides
  (**D-A1**: keep `false` globally and accept forks are denied above 500 K, or set `true`).
- **Hook that reads the budget**: `dev/context_budget.py` reads `transcript_path` backwards;
  `prompt_hook.py` prints `ctx n/window (pct%)` every turn (plain stdout is injected on
  UserPromptSubmit); `agent_gate.py` denies `fork` above `CTX_FORK_MAX` and asks above
  `CTX_HARD`. Thresholds live in `dev/hooks/rules/common.py` and can be raised through
  settings `env` (`CTX_FORK_MAX=…`), never lowered below 200 K.
- **Rule for the parent** (`claude-team.md` §Context budget, injected through AGENTS.md): at
  `CTX_WARN` (45 %) checkpoint (`plan:log`, `plan:handoff --write`) and delegate; at
  `CTX_DELEGATE` (60 %) finish the window (`/clear`) once `plan:handoff --check` passes; Codex
  forensics, transcript reads and synthesis always in subagents (the skill exists now); grill
  → spec → tickets never in one window with a build.
- **"SubagentStop guard that refuses to spawn a fork"**: spawning is a PreToolUse event, not a
  SubagentStop one, so the refusal lives in `agent_gate.py` (PreToolUse `Agent`); SubagentStop
  cannot prevent a spawn. The SubagentStop side (`subagent_receipt.py`) records each fork's
  first/last `usage` so `session:status` can report "fork started at 970 K and died".
- **PreCompact**: not blocked by the project (the plugin's PreCompact writes its checkpoint);
  a repo `PreCompact` hook is not added.

### (L) Agent types not selectable mid-session

- **Cause (docs-confirmed)**: "the watcher covers only directories that existed when the
  session started, so after creating a scope's first agent file in a new `agents` directory,
  restart to load it" (sub-agents page). `.claude/agents/` was created at 20:07Z in a session
  started at 18:54Z, so the roster offered at `T:L25/L46` never changed. Edits to files in a
  pre-existing directory are picked up "within a few seconds"; `/agents` only prints a
  reminder; there is no reload command for agents (skills have `/reload-skills`, plugins
  `/reload-plugins`).
- **What the project does**: (1) `.claude/agents/*.md` is committed (it is) and the wave-0
  retro records that the directory now exists at session start for every future session;
  (2) `session_start.py` records the roster on disk at start (`JOURNAL/sessions/<id>.json`)
  and prints it; a session that finds the directory absent prints the restart rule;
  (3) `agent_gate.py` denies `general-purpose` for lane prompts while a role exists on disk,
  with the restart instruction in the reason, and flags names added after start;
  (4) `lane:brief --inline-role <role>` is the fallback: the role body (frontmatter stripped)
  under `AGENT-FALLBACK: <role>` inside a `general-purpose` brief, journaled as a fallback so the
  retro records that `maxTurns`/`permissionMode`/`skills` preload did not apply. The fallback
  does not reproduce `skills:` preload, so the brief's first line is "invoke
  `mattpocock-skills:tdd` now" for implementers (the Skill tool works for model-invocable skills).

---

## Ordering and ownership (consolidated)

**Wave 0** (serial, parent, after Runbook 1's merge commit and publish; each code item is
test-first, ≤ 80 lines, declared in the wave-0 retro row; the hook entries go live through the
file watcher, so they are the first thing the next session gets):

| # | Item | Class | Files |
|---|---|---|---|
| 0.a | `.claude/settings.json` composition (R5 §B) + `autoCompactEnabled`, `autoCompactWindow`, `env.PLAN_ID`, hook entries for `session_start.py`, `agent_gate.py`, `prompt_hook.py`, `record_guard.py` (entries whose scripts do not exist yet are omitted until the lane lands) | A, I, K | `.claude/settings.json`, `.claude/settings.local.json` (local pins; untracked) |
| 0.b | `dev/context_budget.py`, `dev/hooks/rules/common.py`, `dev/hooks/agent_gate.py` (`fork_budget`, `lane_dispatch` rule 1), `dev/hooks/prompt_hook.py` (budget line), `dev/hooks/session_start.py` (`autocompact`, `agent_roster`, `merge_state` MERGE_HEAD line) + 4 test files + `test:hooks-session` task | A, F, C | as named |
| 0.c | `dev/check.py`: one line running `dev/checks/*.py`; `dev/checks/__init__.py` empty; `hk.pkl` `pre-commit` hook with step `records` → `check:records` (initially runs the settings check only) | B, H, I | `dev/check.py`, `hk.pkl`, `mise.dev.toml` (`check:records`) |
| 0.d | `dev/settings_check.py` minimal (allowed/forbidden keys) + test | I | as named |
| 0.e | Fixtures the lanes need, extracted by the parent: `bash-corpus.jsonl`, `transcript-usage-curve.jsonl`, `transcript-rejected-command.jsonl`, staged `gate-hooks.json`, `settings.json.before-ct02` | J, A, E, B, I | `dev/fixtures/prevention/` |
| 0.f | Docs: `--no-commit` forbidden; D15 wording; §Context budget; §Roles restart rule; `P/decisions.jsonl` seeded with #91 relabel, draft PR, T4 budget; `.agent/` in `.git/info/exclude` | C, D, A, F, E, L | `docs/agents/*.md`, `P/decisions.jsonl` |

**Wave 1** (R8 order kept; CT-16 and CT-12 added as small lanes if D5 admits five, else wave 2):
CT-02b (C, J, I-T5) → CT-11 (H receipts) → CT-05 (B, G) → CT-15 (K) → CT-16 (I) → CT-12 (H).
**Wave 2**: CT-17 (B, C), CT-19 (F, G), CT-18, CT-23 (B, I, K guard rules), CT-25 (E), CT-27 (H,
G), CT-28 (L), CT-30 (N), C3 #95. **Wave 3**: CT-07, CT-06, CT-09, CT-24 (D), CT-26 (F), CT-29
(M). **Wave 4+**: CT-10, CT-20 (its digest replaces the hand-extracted corpus), CT-08, CT-21.

Disjointness rule applied: every new lane owns new files only (`dev/hooks/rules/<rule>.py`,
`dev/checks/<rule>.py`, `dev/planning_checks/<rule>.py`, `dev/test_<module>.py`,
`mise/tasks/<unit>.toml`); the three one-line edits to shared files (`check.py` discovery,
`hk.pkl` pre-commit, hook entries in settings) are wave-0 parent commits; later wiring lines
(`check:research` depends, SubagentStop matcher) are declared parent hunks at integration
(R8 protocol step 4).

## Guardrails (all classes)

- **User-confirmed, never automated**: A09 publish outside the takeover grant (and any publish
  of `main`), ticket close, merge to `main`, draft PR, `hooks:install`, `issue:*-apply`,
  `codex_status.py supersede`, edits to `~/.claude/settings.json`, `~/.claude.json`,
  `~/.gitconfig`, global mise/fnox, `.gitignore` (CT-08). Hooks and tasks *report* and *refuse*;
  only `lane:*`/`plan:*`/`ledger:*` tasks write tracked records, and only the parent runs them.
- **Caller identity**: `caller(event)` returns `parent` when `agent_id` is absent, `subagent`
  when present (with `agent_type`), `fork` when `agent_type == "fork"` or the SessionStart
  `source == "fork"` marker for that `session_id` exists in `JOURNAL/sessions/`. Rules by
  caller: the fork deny and `pending_operations` apply to the parent; `tdd_first` and the
  receipt journal apply to lane roles; `lane_dispatch` applies to any caller (a subagent that
  spawns lanes is itself a parent for that purpose). A subagent never sees UserPromptSubmit.
- **Fail-closed with words**: every deny/block carries the task that fixes it; timeouts become
  denies with reasons inside the budget; `stop_hook_active` always passes; the Stop cap of 8
  is never approached (each rule blocks once per session, tracked in `JOURNAL/sessions/`).
- **No shared-file writes from hooks**; journals under `COMMON/claude-lanes/`; secrets masked
  before any journal write; transcript reads are bounded and backward.

## Consolidated artifact list

| File | Purpose | Wires into | Ticket | Wave |
|---|---|---|---|---|
| `.claude/settings.json` | project keys only; `autoCompactEnabled`, `autoCompactWindow`, `env.PLAN_ID`, one hook entry per event | Claude Code | wave 0 (CT-16 checks it) | 0 |
| `dev/context_budget.py` | ctx from transcript (backward read), `ctx:status` task | `agent_gate`, `prompt_hook`, `session:status` | CT-22 | 0 |
| `dev/hooks/rules/common.py` | thresholds, `caller()`, budget timer, journal helpers, masks | all hook scripts | CT-22 | 0 |
| `dev/hooks/agent_gate.py` | PreToolUse `Agent`: `fork_budget`, `lane_dispatch`, size cap, roster drift | settings PreToolUse(Agent) | CT-22 / CT-26 | 0 / 3 |
| `dev/hooks/prompt_hook.py` | UserPromptSubmit: ctx line, invocation receipt, request capture | settings UserPromptSubmit | CT-22 / CT-24 / CT-25 | 0 / 3 / 2 |
| `dev/hooks/session_start.py` | SessionStart: auto-compact, roster, merge state, pwf probe, exclude drift, codex status, pending ops, `CLAUDE_ENV_FILE` pins | settings SessionStart | CT-22 (+rules from CT-17, CT-28, CT-29, CT-25) | 0 + |
| `dev/hooks/record_guard.py` | PreToolUse `Write\|Edit`: lane JSON, settings schema, progress size, citations | settings PreToolUse(Write\|Edit) | CT-23 | 2 |
| `dev/hooks/post_tool.py` | PostToolUse `Skill`: invocation journal | settings PostToolUse(Skill) | CT-24 | 3 |
| `dev/hooks/subagent_receipt.py` | SubagentStop journal, `tdd_first` | settings SubagentStop(^roles$) | CT-19 | 2 |
| `dev/hooks/pretooluse_gate.py` (+`git_gate.py`) | token-anchored verbs, `--no-commit` deny, `--dry-run`, `--time`, deadline | existing entry | CT-02b | 1 |
| `dev/hooks/stop_gate.py` | + `lane.validate`, `merge_state`, `pending_operations` | existing entry | CT-17 / CT-25 | 2 |
| `dev/hooks/rules/{merge_state,lane_dispatch,agent_roster,invocation_receipt,request_capture,pending_operations,citations}.py` | one rule per file | the scripts above | CT-17, CT-26, CT-22, CT-24, CT-25, CT-25, CT-28 | 2–3 |
| `dev/settings_check.py` | settings composition (`--staged`) | `check:records`, `dev/checks/settings_schema.py`, `record_guard` | CT-16 (minimal in wave 0) | 0/1 |
| `dev/check.py` | + runs `dev/checks/*.py`; writes `JOURNAL/checks/` receipts (CT-11) | `check` | wave 0 / CT-11 | 0/1 |
| `dev/checks/{unwired_tests,pinned_paths,settings_schema,proposals}.py` + `exemptions.toml` | `check` rules | `dev/check.py` | CT-12, CT-27, CT-16, CT-30 | 1–2 |
| `dev/lane.py` | `set|validate(--staged, --from-journal)|allocate(--admit, --import --data, --ticket approval)|integrate(journal, snapshot, --continue/--abort, --parent-hunk)|status|brief` | `lane:*` tasks, hk `records`, `stop_gate` | CT-05, CT-17, CT-19 | 1–2 |
| `dev/lane_brief.py` | `lane:brief` incl. `--inline-role`, reviewer slots | `lane:brief` | CT-19 | 2 |
| `dev/plan_records.py` | `plan:log`, `plan:handoff --write/--check`, `check:planning` runner over `dev/planning_checks/*.py` | tasks, `check:planning` | CT-15 | 1 |
| `dev/planning_checks/{skeleton,progress_size,invocation_wording,seed_pin,requests_cited,citations,pwf_mode,codex_activation}.py` | planning rules | `check:planning` | CT-15, CT-15, CT-24, CT-24, CT-25, CT-28, CT-16, CT-29 | 1–3 |
| `dev/plan_requests.py`, `dev/plan_decide.py` | request/decision ledger CLIs | tasks `plan:requests`, `plan:decide`; `lane:allocate` | CT-25 | 2 |
| `dev/plan_invocations.py` | invocation record generator/check | task `plan:invocations` | CT-24 | 3 |
| `dev/hooks_install.py` | guarded `hooks:install` (publish-first, inspect-hooks dry run) | `hooks:install` row | CT-02b | 1 |
| `dev/exclude_sync.py`, `dev/exclude.txt` | managed `.git/info/exclude` block | task `exclude:sync`, `session_start` | CT-28 | 2 |
| `dev/retro_gate.py` | `retro_record`, item ids, receipts, `--journal` | all three gate layers | CT-27 | 2 |
| `.claude/skills/codex-session-history/scripts/codex_status.py` (+ `.agents` mirror) | Codex probe + `supersede` | task `codex:status` | CT-29 | 3 |
| `P/proposals/claude-takeover-spec/build_manifests.py` | `items[]`, placeholder refusal, `--offline-preview` | `proposals:check`, `issue:create-preview` | CT-30 | 2 |
| `hk.pkl` | `pre-commit` hook, step `records` | global hk hooks (live) | wave 0 | 0 |
| `mise/tasks/<unit>.toml` | task rows per lane (D7 includes); fallback rows in `mise.dev.toml` | `./dev/mise` | each lane | 1+ |
| `.claude/agents/*.md` | constants, `reviewer.md:18` fix, retro-writer step 0 | Agent tool | CT-19 | 2 |
| `docs/agents/claude-team.md` (§Context budget, §Integration, §Roles, §Where outputs go, §Hooks) | rules | AGENTS.md pointer | wave 0 + lanes | 0+ |
| `P/requests/`, `P/decisions.jsonl`, `P/untracked.toml`, `P/codex-briefs/` | tracked ledgers | `plan:*`, `check:planning` | CT-25, CT-28 | 0/2 |
| `dev/fixtures/prevention/**` | reproductions | tests | wave 0 + lanes | 0+ |

Counts: 16 new or extended Python modules outside hooks; 9 hook scripts (6 new: `agent_gate`,
`prompt_hook`, `session_start`, `record_guard`, `post_tool`, `subagent_receipt`; 3 extended:
`pretooluse_gate`, `stop_gate`, `git_gate`); 7 rule-module files under `dev/hooks/rules/`;
12 rule modules under `dev/checks/` + `dev/planning_checks/`;
≈ 20 mise task rows (`ctx:status`, `check:records`, `lane:set|validate|allocate|integrate|
status|brief`, `plan:log|handoff|requests|decide|invocations`, `check:planning`,
`proposals:check`, `exclude:sync`, `codex:status`, `test:hooks-session`, `test:retro-gate`,
`ledger:sync`), 5 settings hook entries, 1 hk hook, 9 new tickets (CT-22…CT-30).

## Settings and hook JSON snippets (ready to paste)

`.claude/settings.json` (project; R5 §B keys plus the wave-0 additions; hook entries whose
script does not exist yet are added when the lane integrates):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "autoCompactEnabled": true,
  "autoCompactWindow": 700000,
  "env": {
    "PLAN_ID": "2026-10-10-marketplace-macos-reflection-scaffold",
    "HOOK_BUDGET_S": "6",
    "CTX_WARN": "450000",
    "CTX_DELEGATE": "600000",
    "CTX_FORK_MAX": "500000",
    "CTX_HARD": "850000"
  },
  "enabledPlugins": {
    "planning-with-files@planning-with-files": true,
    "astral@astral-sh": true,
    "mise@brentmitchell25": true,
    "mattpocock-skills@mattpocock": true
  },
  "extraKnownMarketplaces": {
    "planning-with-files": {"source": {"source": "github", "repo": "<from R5 §B>"}},
    "astral-sh": {"source": {"source": "github", "repo": "<from R5 §B>"}},
    "brentmitchell25": {"source": {"source": "github", "repo": "<from R5 §B>"}},
    "mattpocock": {"source": {"source": "github", "repo": "<from R5 §B>"}}
  },
  "hooks": {
    "SessionStart": [
      {"matcher": "startup|resume|clear|compact|fork",
       "hooks": [{"type": "command", "timeout": 10,
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/session_start.py\""}]}
    ],
    "UserPromptSubmit": [
      {"hooks": [{"type": "command", "timeout": 10,
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/prompt_hook.py\""}]}
    ],
    "PreToolUse": [
      {"matcher": "Bash",
       "hooks": [{"type": "command", "timeout": 10, "onFailure": "block",
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/pretooluse_gate.py\""}]},
      {"matcher": "Agent",
       "hooks": [{"type": "command", "timeout": 10, "onFailure": "block",
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/agent_gate.py\""}]},
      {"matcher": "Write|Edit",
       "hooks": [{"type": "command", "timeout": 10, "onFailure": "block",
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/record_guard.py\""}]}
    ],
    "PostToolUse": [
      {"matcher": "Skill",
       "hooks": [{"type": "command", "timeout": 5,
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/post_tool.py\""}]}
    ],
    "SubagentStop": [
      {"hooks": [{"type": "command", "timeout": 15, "onFailure": "block",
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/subagent_stop_gate.py\""}]},
      {"matcher": "^(implementer|doc-writer|reviewer|retro-writer)$",
       "hooks": [{"type": "command", "timeout": 10,
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/subagent_receipt.py\""}]}
    ],
    "Stop": [
      {"hooks": [{"type": "command", "timeout": 10, "onFailure": "block",
                  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/hooks/stop_gate.py\""}]}
    ]
  }
}
```

`.claude/settings.local.json` (per user, untracked; from N1/R5 plus the pins):

```json
{
  "env": {
    "PWF_PLAN_ROOT": "/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace",
    "PWF_INJECT": "smart",
    "PWF_TRUSTED_PYTHON": "/absolute/path/to/python3"
  },
  "permissions": {"allow": ["<the seven MCP rules, verbatim from the backup>"]},
  "enabledPlugins": {"eli5@claude-community": true, "html-plan@claude-community": true,
                     "next-steps@claude-community": true, "codex@openai-codex": true},
  "extraKnownMarketplaces": {"claude-community": "<verbatim>", "openai-codex": "<verbatim>"},
  "skillOverrides": "<verbatim>",
  "additionalDirectories": "<verbatim, undocumented top-level key kept as found>"
}
```

`hk.pkl` addition (wave 0; fires through the user's global `hook.hk-pre-commit` entry, no
install step):

```pkl
    ["pre-commit"] {
        stash = "none"
        steps {
            ["records"] { check = "./dev/mise run check:records" }
        }
    }
```

`mise.dev.toml` rows (wave 0; later rows per lane in `mise/tasks/<unit>.toml`):

```toml
[tasks."check:records"]
description = "Fast staged-content checks for lane records and project settings (hk pre-commit)"
dir = "{{config_root}}"
run = ['"${MARKETPLACE_PYTHON:-python3}" -I dev/settings_check.py --staged']
# CT-05 appends: '"${MARKETPLACE_PYTHON:-python3}" -I dev/lane.py validate --staged'

[tasks."test:hooks-session"]
description = "Contract tests for the session, prompt and agent hooks (stdin JSON, scratch HOME)"
dir = "{{config_root}}"
run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p "test_*_hook.py" -v'

[tasks."ctx:status"]
description = "Context budget of a Claude transcript (defaults to the newest in this project)"
dir = "{{config_root}}"
usage = 'arg "[transcript]"'
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/context_budget.py "${usage_transcript:-}" --json'
```

`dev/check.py` wave-0 line (inside `check()`, before the unittest loop):

```python
for rule in sorted((ROOT / "dev/checks").glob("*.py")):
    if rule.name != "__init__.py":
        run(sys.executable, "-I", str(rule), env=scrubbed(os.environ))   # rc≠0 ⇒ CalledProcessError
```

Hook output shapes the scripts use (from the docs): PreToolUse deny
`{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny",
"permissionDecisionReason":"…"}}`, ask `"permissionDecision":"ask"`, context
`{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"…"}}`; Stop/SubagentStop
block `{"decision":"block","reason":"…"}`; UserPromptSubmit/SessionStart plain stdout lines
(injected) or `{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"…"}}`.

## Test inventory

| Id | File | Fixture | Assertion | Reproduces | Ticket |
|---|---|---|---|---|---|
| T-A1 | `test_context_budget.py` | `transcript-usage-curve.jsonl` (last line zero usage) | ctx = last non-zero sum | P1-1 death line | CT-22 |
| T-A2 | `test_agent_gate.py` | T-A1 + Agent event `fork` | deny naming `lane:brief`; `implementer` → allow + ctx context | P1-1 | CT-22 |
| T-A3 | `test_context_budget.py` | 20 MB synthetic | < 1 s | hook budget | CT-22 |
| T-A4 | `test_prompt_hook.py` | ctx 660 K | `CONTEXT BUDGET:` line | P2-19 | CT-22 |
| T-A5 | `test_session_start.py` | temp HOME `autoCompactEnabled:false` | `auto-compact:` line with both booleans | class A | CT-22 |
| T-A6 | `test_settings_check.py` | project settings | `autoCompactEnabled: true` present | class A | CT-16 |
| T-B1 | `test_lane.py` | staged `gate-hooks.json` + replayed allocate commit | `base_sha` off by one; `review` missing | P2-17, P1-4 | CT-05 |
| T-B2 | `test_lane.py` | `a06-unit3.json` shape | `retro passed` vs gate rc 2 | P1-13 | CT-05 |
| T-B3 | `test_lane.py` | — | `retro` not settable; derived on `integrated` | class B | CT-05 |
| T-B4 | `test_record_guard.py` | Write of invalid lane JSON | deny naming `lane:set` | P1-4 | CT-23 |
| T-B5 | `test_hooks.py` (HkHooks) | staged invalid record | `git commit` refused by `records` step | class B | CT-23 |
| T-B6 | `test_plan_records.py` | handoff base `28fedf1` ≠ HEAD | `--check` rc 2 | P1-1 handoff | CT-15 |
| T-B7 | `test_lane.py` | `published` not on origin | rc 2 | class B | CT-05 |
| T-C1 | `test_hooks.py` | `bash-corpus.jsonl` (113 real commands) | exact action set; R7 heredoc → none | P2-3 | CT-02b |
| T-C2 | `test_hooks.py` | `git merge --no-ff --no-commit claude/x-y` | deny naming `lane:integrate` | P2-1 | CT-02b |
| T-C3 | `test_stop_gate.py` | scratch repo with `MERGE_HEAD`, no journal | block once; journal → none | P1-1 | CT-17 |
| T-C4 | `test_lane.py` | killed `integrate` | `--continue` same tree; `--abort` restores snapshot | P1-1, P2-18 | CT-17 |
| T-C5 | `test_lane.py` | lane tip touching `mise.dev.toml` | rc 2; `--parent-hunk` second commit | P2-2 | CT-17 |
| T-C6 | `test_hooks_install.py` | unpublished commit; then pushed | rc 2 "publish first"; install × `inspect-hooks` passes | P1-3 | CT-02b |
| T-C7 | `test_hooks.py` | 40 failing lanes, `git push` | deny "timed out" < budget+1 s | P2-3 timeout | CT-02b |
| T-D1 | `test_prompt_hook.py` | prompt with `<pasted_content>…/mattpocock-skills:…` | `slash-in-paste` journal + warning | P1-7 | CT-24 |
| T-D2 | `test_planning_checks_invocation_wording.py` | real "standing authorization" row | one reason | P1-7 | CT-24 |
| T-D3 | `test_plan_invocations.py` | `typed by user` row, empty journal | rc 2 | P1-7 | CT-24 |
| T-D4 | `test_planning_checks_seed_pin.py` | doc without pin / wrong hash | reasons | P2-21 | CT-24 |
| T-E1 | `test_plan_requests.py` | `transcript-rejected-command.jsonl` (`T:L565-566` shape) | row `rejected-command` | P1-8 | CT-25 |
| T-E2 | `test_plan_requests.py` | undispositioned row | rc 2; after `cite` rc 0 | P1-8 | CT-25 |
| T-E3 | `test_stop_gate.py` | operation without receipt | block once; receipt → none | P1-9, P2-8 | CT-25 |
| T-E4/T-N4 | `test_lane.py` | `allocate --ticket CT-02` unapproved | rc 2 | P1-6 | CT-17/CT-30 |
| T-E5 | `test_plan_decide.py` | duplicate approval | idempotent, append-only | class E | CT-25 |
| T-F1 | `test_agent_gate.py` | real 5.3 KB `general-purpose` lane brief, roles on disk | deny naming `implementer` + restart | P1-12, P2-23 | CT-26 |
| T-F2 | `test_agent_gate.py` | `implementer` 1.2 KB / 5.3 KB | allow / deny on size | P2-23 | CT-26 |
| T-F3 | `test_session_start.py` | no `.claude/agents` / five files / added later | restart line / roster / drift context | P1-12 | CT-22, CT-26 |
| T-F4 | `test_subagent_receipt.py` | implementer transcript code-before-test | block once | P1-12 (tdd) | CT-19 |
| T-F5 | `test_lane_brief.py` | `--inline-role implementer` | ≤ 1.5 KB; body = definition minus frontmatter | class F | CT-19 |
| T-G1 | `test_subagent_receipt.py` | reviewer stop, root `cwd`, `LANE-UNIT` marker | journal line with unit, PASS, `P3-1` | P1-4, gate-hooks P3 | CT-19 |
| T-G2 | `test_lane.py` | T-G1 journal; tip not on branch | `review` lifted; rc 2 | P1-4 | CT-05 |
| T-G3 | `test_retro_gate.py` | reviewer `P2-3`, retro without row | rc 2 | P2-22 | CT-27 |
| T-G4 | `test_lane.py` | record without `network` | rc 2 | P2-5 | CT-05 |
| T-G5 | `test_record_guard.py` | `findings.md` write citing `/private/tmp` | deny | P2-25 | CT-23/CT-28 |
| T-H1 | `test_check_wiring.py` | unwired `test_x.py`; live `test_retro_gate.py` | listed / none after wiring | P1-5 | CT-12 |
| T-H2 | `test_pinned_paths.py` | `ROOT/"evidence/…"` + SHA, untracked | reason | P1-10 | CT-27 |
| T-H3 | `test_retro_gate.py` | `a06-unit3` alias without `retro_record` | rc 2; with field rc 0 | P1-13 | CT-27 |
| T-H4 | `test_retro_gate.py` | deferral `CT-02` without item id | rc 2; `CT-02/3` → 0 | P2-4 | CT-27 |
| T-H5 | `test_retro_gate.py` | `hk validate rc 0` claim without/with receipt | rc 2 / 0 / contradiction rc 2 | P2-22 | CT-27 |
| T-I1 | `test_settings_check.py` | staged `e12cf04` settings bytes | two reasons; R5 §B file → 0 | P1-2 | CT-16 |
| T-I2 | `test_settings_check.py` | hook naming a missing script | rc 2 | class I | CT-16 |
| T-I3 | `test_record_guard.py` | Write `permissions` into settings.json / local | deny / none | P1-2 | CT-23 |
| T-I4 | `test_planning_checks_pwf_mode.py` | `.mode = gate`; missing `PLAN_ID` | reasons | P2-16, P2-15 | CT-16 |
| T-I5 | `test_hooks.py` | both Stop hooks, one payload | ≤ 1 block | P2-16 | CT-02b |
| T-J1 | `test_hooks.py` | corpus `--time` | p95 < 500 ms | P2-3 | CT-02b |
| T-J2 | `test_hooks.py` | synthetic bypass corpus | per-row expectations | reviewer P3-2 | CT-02b |
| T-K1 | `test_plan_records.py` | current `task_plan.md` head | "0 `### Phase`" | P1-11 | CT-15 |
| T-K2 | `test_record_guard.py` | 901 KB `progress.md` edit | deny | P1-11 | CT-23 |
| T-K3 | `test_plan_records.py` | `plan:log` at cap | NEXT last; refusal | P1-11 | CT-15 |
| T-K4 | `test_session_start.py` | plugin absent / fake injector | `pwf:` line | P2-15 | CT-22 |
| T-L1 | `test_planning_checks_citations.py` | scratch/tmp, untracked, codex+sha | reasons / none | P2-25, P1-10 | CT-28 |
| T-L2 | `test_exclude_sync.py` | `.agent/` unexcluded | rc 2; `--write` idempotent | P2-24 | CT-28 |
| T-L3 | `test_lane.py` | `import_source.data tracked:false`, integrated | rc 2 | P1-10 | CT-05/CT-28 |
| T-M1–M4 | `test_codex_status.py` | fixture sqlite/automation/packet | counts; activation mismatch; supersede once | P2-10, P2-11, P2-9 | CT-29 |
| T-N1–N3 | `test_checks_proposals.py` | committed `tickets.preview.json`; cycle; builder path | reasons | P2-7, P2-6 | CT-30 |

## Could not verify

- Whether `~/.claude.json`'s `autoCompactEnabled: false` participates in the settings stack
  (the settings page calls that file CLI-written "global config"; the reference marks the key
  "Any file"). The design reports both files and leaves the global change to the user.
- The `agent_type` value a fork session's hooks receive (docs name `fork` only as a SessionStart
  `source`); `caller()` treats either marker as `fork` and T-A2 fixes both shapes.
- Whether project `env` values reach hook processes (R4 open point); `session_start.py` writes
  the pins to `CLAUDE_ENV_FILE` as the belt-and-braces route, and thresholds default in code.
- The context window size from inside a hook: the hook input has no `context_window`; the
  statusline does. The 1,000,000 default is a pin (`CLAUDE_CTX_WINDOW`), and the auto-compact
  point for the session models (~967 K) is from the model-config page, not measured here.
- `git merge-tree --write-tree` availability for the no-half-merge composition: Git 2.54 has
  it (added in 2.38); whether the composed-tree named checks can run from a temporary worktree
  with identical results was not tested.
- That the global hk `pre-commit` entry runs `hk run pre-commit` for this repo once `hk.pkl`
  defines the hook (inferred from `hk install --help` and the existing `hook.hk-pre-commit`
  config; R5 observed the global hooks as no-ops because `hk.pkl` defines neither).
- `hk install` reconciliation mode (`--legacy` shims vs admitting `pre-merge-commit`) is
  CT-02b's choice; T-C6 pins whichever is chosen.
- The 113-command corpus must be extracted and sanitized by the parent (wave 0.e); expected
  actions per row are the parent's labels, reviewed once.
- Whether `PreToolUse` for `Edit` receives `old_string`/`new_string` under those names in
  2.1.296 (inferred from the Edit tool schema); `record_guard.py` falls back to PostToolUse
  feedback when the projection is impossible.
- R8's wave slot arithmetic with the five added small lanes (CT-16, CT-12 in wave 1; CT-23,
  CT-25, CT-27, CT-28, CT-30 in wave 2) depends on D5; the dependency edges are stated so the
  parent can defer any of them a wave without breaking another.
