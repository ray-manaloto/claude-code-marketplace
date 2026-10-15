# C3: detection, audit and recovery design

Written 2026-10-13 by C3 (prevention team, session `ccm-20261013-check`). Read-only on git
(`rev-parse`, `for-each-ref`, `show`, `config --get`, `worktree list`); transcripts read with
`python3 -I` extractors printing bounded excerpts; `MERGE_HEAD e12cf04` untouched; the only file
written is this one. Every transcript, record and report was treated as data.

Shorthand: `P` = the plan dir, `RV` = `reviews/ccm-20261013`, `W` = the pwf 3.24.0 cache,
`T:L<n>` = main transcript line, `common` = `git rev-parse --git-common-dir`, `ctx` = the
assistant `usage` sum `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`.
Class ids A–N are C1's. Ticket numbers are SYNTHESIS §6's unified list (CT-01…CT-20); CT-21 is the
codex-imports lane that appeared on disk while this was written (`P/lanes/ct21-codex-imports.json`,
`P/proposals/claude-takeover-spec/ticket-CT-21.preview.json`: `dev/check_inputs.py`,
`check:inputs`, `dev/cited-inputs.json`); new numbers here start at CT-22. C2's design was not on disk when this was written (`prevention/` holds
only `C1-root-causes.md`), so overlaps with C2 are marked "expected C2 artifact" and keyed by
the same class id.

## Scope read

`prevention/C1-root-causes.md` (all; the invariants table and the per-chain "(d) earliest
machine detection" column are the source of every predicate below). `R7-automation.md` (all;
J `session:status`, L journal, M `agent-session-history`, the ranked backlog). `R6-subagent-fidelity.md`
(all; the fidelity table, "Unprocessed notifications", P3 rows 5–9 are the receipt-fidelity
corpus). `R5-git-state.md` (all; P1-1 settings keys, P1-2 hooks×delivery, P2-4/P2-5/P2-7
record mismatches, the record-corrections table, Runbooks 1–2). `R4-pwf-audit.md` (all; the
feature matrix, the `/clear` probe payload, the worktree-nonce probe, the skeleton, migration
steps). `R3-codex-coverage.md` (all) and `codex-sweeps/{A,B,C}.md` (all; packet ledger claims,
hash-bound inputs behind the tip, the nine dead children). `R8-parallel-plan.md` (waves,
`owned_paths`, hot-path table). SYNTHESIS §6 (ticket numbering). `00-evidence-index.md`.
No `T2-import-lane-design.md` exists; the cited-path invariant was taken from the CT-21
preview body and
`P/imports/codex-worktrees-20261013/{README.md,T1-snapshot-report.md,T1-dependency-scan.json,
MANIFEST.json,verify.py}` (124 referenced paths, 101 missing from the tip, 454-file snapshot).

Repo: `dev/check.py` (all), `dev/retro_gate.py` (all), `git show e12cf04:dev/hooks/{git_gate,
pretooluse_gate,stop_gate,subagent_stop_gate}.py` (all), staged `.claude/settings.json`, `hk.pkl`,
`mise.dev.toml` (all tasks), `dev/test_hooks.py` (class and test names), `dev/git_delivery.py:40-80`,
`ci/acceptance.sh:1-60`, `docs/agents/{claude-team (staged),ticket-retro}.md`, `.claude/agents/
{implementer,reviewer,retro-writer}.md`, `.claude/rules/{dev-tests,evidence,planning-records}.md`,
`P/lanes/*.json` (all nine, projected), `P/task_plan.md:1-40,60-95`, `P/progress.md` tail,
`P/ticket-ledger.md:1-30`, `P/skill-invocations.md`, `P/findings.md`, `.claude/skills/
codex-session-history/SKILL.md` and the five scripts' interfaces (`codex_rollout_digest.py`
`mask/clip/SECRET_RE/digest`, `codex_threads.py list|show|children|turns|logs`,
`codex_research_receipts.py`). Git facts: HEAD `9cd396a`, `MERGE_HEAD e12cf04`, no `merge.ff`,
`.git/hooks` samples only, exclude file (2 entries), 27 worktrees, `.git/{AUTO_MERGE,MERGE_HEAD,
MERGE_MODE,MERGE_MSG}` mtime 16:30 local.

Host: `W/scripts/plan-doctor.sh` (all), `W/scripts/check-complete.sh` (all), `W/hooks/hooks.json`.
Claude Code hooks docs (https://code.claude.com/docs/en/hooks, two 100 K-char windows): common
fields `session_id, prompt_id, transcript_path, cwd, scratchpad_dir, permission_mode, effort,
hook_event_name (+ agent_id, agent_type)`; SessionStart `source ∈ {startup, resume, clear, compact,
fork}`, on `resume|fork` also `context_tokens`, `seconds_since_last_response`; SessionStart and
UserPromptSubmit accept `hookSpecificOutput.additionalContext` and plain stdout; SubagentStop
carries `agent_id, agent_type, agent_transcript_path, last_assistant_message, stop_hook_active`
and the parent's `transcript_path`; Stop carries `last_assistant_message, background_tasks,
session_crons`; `transcript_path` "may lag the in-memory conversation"; `onFailure` has no effect
on Stop/SubagentStop; command-hook default timeout 600 s (30 s on UserPromptSubmit); `if` filters
run only on tool events; `CLAUDE_ENV_FILE` only at SessionStart/Setup; settings hook edits are
picked up by the file watcher.

Transcripts (bounded): main `464a2816…jsonl` line types and key sets (2045 lines; `attachment`
509, `user` 273, `assistant` 390, `system` 46, `queue-operation` 88), `L6` (SessionStart
`hook_success` with the pwf `additionalContext`), `L29` (`total_tokens_reminder`
`<total_tokens>15000000 tokens left</total_tokens>`), `L2029` (the `<task-notification>` user turn:
`origin.kind = task-notification`, `turnOrigin = task_notification`, `<status>failed</status>`,
`<output-file>` under the setup session's `tasks/`), `L2043` (`isApiErrorMessage: true`,
`error: invalid_request`, text "Prompt is too long", `usage` all zero); fork
`agent-a22113b35136b11c1.jsonl` (18 lines: `fork-context-ref` with `parentLastUuid`, first
`usage` `cache_read 967,340 + creation 3,165`, last real `usage` 974,113 + 2,125, the
`total_tokens_reminder` inside it said 14,025,109 left) and its `.meta.json`
(`agentType: fork, isFork: true, model: inherit, requestShape: background`); reviewer
`a221b354` final text ("Re-review (e12cf04): PASS for integration … Side effects: … custom-subject
merge unatt…"). Attachment kinds present: `hook_additional_context` 58, `hook_success` 12,
`agent_listing_delta` 1, `skill_listing` 2, `deferred_tools_record` 60.

Host settings (key names and booleans only): `~/.claude/settings.json` and `~/.claude.json`
`autoCompactEnabled: false`; user `env` carries five `CLAUDE_CODE_*`/`ENABLE_TOOL_SEARCH` flags.
Codex: `~/.codex/automations/refresh-llvm-github-research/automation.toml` `status = ACTIVE`,
`rrule FREQ=HOURLY;INTERVAL=4`, target `01a12bd1`; packet `…/qbj4yn5d/lane-ledger.json` keys
(`source_writer_allocation.owner "/root"`, `updated_at`, 11 `issue*_closure_preparation`).

## Design constraints

- **Detection, not prevention.** Every detector below assumes C2's hooks were bypassed, the
  session died, or a human overrode a rule. It reads state after the fact and never blocks a
  tool call; the only hooks it occupies are `SessionStart` and `UserPromptSubmit` (context
  injection, exit 0 always, `onFailure: continue`).
- **One module tree, stdlib only.** `dev/doctor/cli.py` (entry; inserts its own directory on
  `sys.path` the way `dev/hooks/*.py` do, so `python3 -I` works), `dev/doctor/core.py`
  (`Finding`, `Context`, git helpers reusing `dev/hooks/git_gate.py` by path import, budget
  timer, JSON writer), one `dev/doctor/<check>.py` per class with `run(ctx) -> list[Finding]`
  and `FIXES = {finding_id: fix_fn}`. No `dev/check.py`, `dev/retro_gate.py`, `dev/hooks/*`,
  `dev/lane.py`, `dev/git_delivery.py` edits: those are R8 wave-1/2 owners.
- **Finding shape** (one JSON object per finding, sorted P1→P3 then id):

  ```json
  {"id": "C.merge-in-progress", "class": "C", "severity": "P1",
   "subject": "MERGE_HEAD e12cf04 (claude/gate-hooks-wiring, lane gate-hooks)",
   "evidence": [".git/MERGE_HEAD mtime 2026-10-13T21:30:16Z", "11 staged paths", "1 foreign hunk: mise.dev.toml"],
   "fix_hint": "./dev/mise run lane:integrate -- gate-hooks --continue  (or --abort after `doctor --snapshot`)",
   "auto_fixable": false}
  ```

  `severity ∈ {P1, P2, P3, info, skipped}`; `skipped` carries the reason a detector could not
  run on this surface (no transcript, no `gh`, CI) and never affects the exit code.
- **Exit codes** follow `dev/retro_gate.py`: 0 no P1/P2; 2 at least one P1 or P2; 1 usage;
  3 a detector raised (also emitted as finding `doctor.detector-error`, P2).
- **Budgets.** Each detector declares `budget_ms` per surface; `core` kills it at the budget and
  emits `skipped` with "budget". The `session-start` surface totals ≤ 3,000 ms (hook timeout
  15 s, pwf's own SessionStart hook runs in parallel). The `check` surface spawns no network,
  reads no transcript and takes no lock: it is read-only and tolerates the CT-11 lock holder.
- **No writes except under `--fix`.** Auto-fixes write only (a) derived record fields the
  doctor can prove from git, (b) files under `<common>/claude-doctor/` and
  `<common>/claude-lanes/snapshots/`, (c) `.git/info/exclude` lines. Everything else prints the
  exact command or literal diff and stays `auto_fixable: false`.

## Per-class detectors

Each subsection: predicate and data; module and finding ids; surfaces; recovery; tests first;
ticket. Fixture names refer to the Test inventory.

### A. Context budget blind

**Predicate.** `ctx(last assistant usage in transcript_path) < T_warn (400 K) < T_checkpoint
(600 K) < T_fork (650 K)`; every `Agent(subagent_type: fork)` started below `T_fork`;
`autoCompactEnabled ≠ false` or `docs/agents/claude-team.md` records the decision. The
`total_tokens_reminder` attachment (`<total_tokens>15000000 tokens left</total_tokens>`, `T:L29`)
is the account budget, not the window: the dying fork still saw 14,025,109 left at ctx 974 K,
so the detector never reads it as a context measure.

**Data.** Hook payload `transcript_path` (last `type == "assistant"` line with `message.usage`;
on `SessionStart source ∈ {resume, fork}` the payload's `context_tokens` directly); the
transcript's byte size as a fallback proxy (main: 7.1 MB at 977 K, ≈ 7.3 KB per 1 K tokens, so
4.4 MB ≈ 600 K); `subagents/agent-*.meta.json` (`isFork`) plus each fork's first `usage`;
`~/.claude/settings.json` and `~/.claude.json` key `autoCompactEnabled` (value only); the
previous session's death point (most recent sibling `<id>.jsonl` in the project dir modified
within 7 days whose last assistant line has `isApiErrorMessage: true`).

**Module `dev/doctor/budget.py`.** Findings: `A.ctx-over-checkpoint` (P2 at ≥ 600 K, P1 at
≥ 800 K; subject `ctx <n>K`), `A.fork-over-budget` (P1; one per fork whose first `cache_read +
creation ≥ T_fork`; fixture `a22113b3` 970,505), `A.autocompact-off` (P3 unless the team guide
contains `autoCompactEnabled`), `A.previous-session-died` (P2; subject session id, time, ctx,
the count of unprocessed notifications from G).

**Surfaces.** `SessionStart`: the `previous session` line (after `/clear` ctx is ~0, so the
useful fact is how the last one ended) and the `context` policy line. `UserPromptSubmit`: a
one-line `ctx <n>K / 1,000K (<phase>)` only when ctx crosses a 100 K bucket since the last
fire (state in `<common>/claude-doctor/session-<id>.json`). `session-review`: the ctx curve
(one point per user turn), every fork's start ctx, the death point. Not in `check`/CI (no
transcript).

**Budget rule (what the parent must do).** At ctx ≥ 600 K or transcript ≥ 4.4 MB: run
`plan:handoff --write` and `plan:log` (CT-15), stop launching forks, and delegate remaining
steps to non-fork agents with ≤ 1.5 KB briefs (`lane:brief`, CT-19). At ≥ 800 K: finish the
current record write, hand off, `/clear`. The deny itself (PreToolUse on `Agent` with
`subagent_type: fork` above 650 K) is C2's artifact; this detector reports the breach
after the fact and supplies the threshold constants from one place
(`dev/doctor/budget.py:THRESHOLDS`) so both read the same numbers.

**Recovery.** None on git. After a death: the next session's SessionStart block names the
unprocessed notifications (G) and the staged state (C); the parent acts on those first.

**Tests first.** `test_budget_fork_over_threshold_from_meta_and_first_usage` (fixture
`transcripts/fork-970k/`: `.meta.json` `isFork: true`, first assistant `usage` cache_read
967,340 + creation 3,165 → exactly one `A.fork-over-budget`); `test_budget_total_tokens_reminder_is_ignored`
(fixture with `<total_tokens>14025109 …>` and ctx 50 K → no finding);
`test_budget_death_point_detected` (last assistant `isApiErrorMessage: true` → one
`A.previous-session-died`); `test_budget_clean_session_no_findings` (ctx 120 K, no forks,
`autoCompactEnabled` absent → `[]`).

**Ticket.** CT-22 (doctor core). The deny hook and the `claude-team.md` sentence on
`autoCompactEnabled` are C2 / runbook items (expected C2 artifact: PreToolUse matcher `Agent`).

### B. Records derived by hand

**Predicate.** For every `P/lanes/<unit>.json`: `base_sha` is a commit and equals the parent of
the lane's first own commit (`git rev-list --reverse --first-parent <base_sha>..<branch> | head -1`
has parent `base_sha`; if `allocated_from` exists, `base_sha` is the allocation commit and
`allocated_from` its parent); `status` prefix ∈ `{allocated, implementing, implemented,
reviewed, integrated, published}` (staged `claude-team.md` vocabulary); `"integrated" ∈ status
⇒ merged_head or branch is an ancestor of HEAD`; `published` set or `"published" ∈ status ⇒
integration merge is an ancestor of origin/<integration>`; the converse, status says
"publication pending" while the integration merge is on origin ⇒ stale; status below
`reviewed` while the branch is `MERGE_HEAD` or already an ancestor of HEAD ⇒ stale; `review`
present whenever status ≥ reviewed; `retro == "passed"` ⇒ `retro_gate.py --unit <unit>` rc 0
on the tree; the plan's Lanes table projects the records; the handoff block's base claim equals
`HEAD` or the remote.

**Data.** `lanes/*.json` (loaded through `git_gate.lanes()`), `git` plumbing (`rev-parse`,
`merge-base --is-ancestor`, `rev-list`, `for-each-ref`, `log --first-parent --merges` to find
the integration merge whose second parent is the lane tip), `P/task_plan.md` (`## Session
handoff` block lines 14–30 and the `| Lane | Unit |` table), `retro_gate.py` (subprocess,
2 s budget per unit, `check` surface only).

**Module `dev/doctor/lanes.py`.** Findings: `B.base-sha-off-by-one` (P3; subject unit; evidence
recorded vs derived; fixture gate-hooks `e618243` vs `2d1f60e`), `B.status-stale` (P2; one per
record; evidence the git fact that contradicts it; fixtures: six "publication pending" records
whose merges are in `28fedf1`; gate-hooks "awaiting cold review" while `MERGE_HEAD` is its
tip), `B.review-missing` (P2; status ≥ reviewed and no `review`), `B.retro-claim-unverified`
(P2; `retro: passed` but gate rc ≠ 0; fixture a06-unit3 rc 2 — the alias itself is H),
`B.plan-table-vs-lanes` (P3; row count and state words differ from the projection),
`B.handoff-base-stale` (P2; "Handoff base: `<sha>`" or "local tip = published remote `<sha>`"
≠ HEAD and ≠ `origin/<branch>`; fixture `9cd396a` vs `28fedf1`), `B.handoff-text-contradicts-record`
(P2; the block says "re-review in progress|awaiting review" for a unit whose record or journal
holds a PASS).

**Surfaces.** `SessionStart`: the `lanes (n)` and `handoff` lines. `check` (static, the
retro-gate subprocess included). `integrate` preflight (CT-17 calls `doctor --surface
integrate --unit <u>`: the unit's findings must be empty before step 2). `pre-push`: any
`published`/`integrated` claim that git contradicts refuses the push (P2 → rc 2). CI: same as
`check`.

**Recovery.** `lane:set <unit> --from-git` (CT-05/CT-17) derives `merged_head`,
`integration_merge`, `published`, `base_sha`/`allocated_from` from git. Until it lands,
`doctor --fix B.status-stale` applies only the derivable facts: adds `integration_merge` and
`published: <remote sha>` when git proves them, and rewrites `"publication pending"` to
`"published <sha>"` (auto, because the fact is proven and the text is the vocabulary's own);
it never promotes `status` past `reviewed` and never writes `retro: passed`. `retro` demotion
to `pending` when the gate fails is printed, not applied. `plan:handoff --rewrite` (CT-15
`--write`) regenerates the base and lane sentences; before CT-15, `doctor --fix
B.handoff-base-stale` rewrites only the two literal sentences inside the block and leaves
`Next:` alone (auto). Status text and `review` fields are user-confirmed edits (the doctor
prints the R5 record-corrections row).

**Tests first.** Scratch repos built like `dev/test_hooks.py:Scratch` (init, integration
branch, lane branch, allocation commit, merge, a bare `origin` with a pushed tip).
`test_lanes_base_sha_off_by_one` (record `base_sha` = allocation commit's parent → exactly
`B.base-sha-off-by-one`); `test_lanes_publication_pending_but_on_origin` (merge pushed, status
"publication pending" → `B.status-stale`, `--fix` writes `published`, re-run → `[]`);
`test_lanes_stale_status_while_merge_head_is_lane_tip` (gate-hooks fixture → `B.status-stale`
+ `B.review-missing`); `test_lanes_retro_passed_but_gate_fails` (a06-unit3 fixture →
`B.retro-claim-unverified` once; the H alias test asserts the companion finding);
`test_lanes_handoff_base_claims_remote` (task_plan fixture with "local tip = published remote
`<origin sha>`" while HEAD is one ahead → `B.handoff-base-stale`); `test_lanes_clean_record_no_findings`
(allocation commit as `base_sha`, status integrated, merge on origin, `published` set, retro
file passes → `[]`).

**Ticket.** CT-22 hosts the detectors; CT-05 (`lane:validate`) and CT-17 (`session:status`) are
the owners of the same predicates as refusals — the doctor imports `dev/lane.py`'s schema once
CT-05 lands and keeps its own copy until then (duplication declared, removed by CT-05's
acceptance "doctor's `B.*` pass through `lane:validate`").

### C. Integration sequence non-resumable; gate bypass by merge form

**Predicate.** `MERGE_HEAD` absent at every SessionStart and Stop, or a runner receipt names
the resumable step; when present, the merge source classifies as one lane and every staged
blob is from HEAD or MERGE_HEAD (no foreign hunk) unless `MERGE_MSG` declares `parent hunk:`;
configured Git hooks (`git config --local --get-regexp '^hook\.'`) pass
`git_delivery.safe_configured_hooks` (so `hooks:install` has not broken A09); no lane with
status `implemented|reviewed` has a tip whose merge-base with HEAD is behind HEAD (tip moved
after review); a `published` lane's worktree is removed or the record carries `holds`.

**Data.** `.git/MERGE_HEAD`, `MERGE_MSG`, `MERGE_MODE` (mtime = when it started);
`git_gate.merge_sources/classify` (path-imported from `dev/hooks/git_gate.py`); `git diff
--cached --name-only`, `git ls-tree HEAD|MERGE_HEAD <path>` blob ids vs `git ls-files -s`;
`<common>/claude-lanes/integrate/<unit>.json` (CT-17's step receipt); `git config --local
--get-regexp '^hook\.' -z` fed to `safe_configured_hooks` (path-imported, pure function);
`git config --get merge.ff`; `git worktree list --porcelain`.

**Module `dev/doctor/integration.py`.** Findings: `C.merge-in-progress` (P1; evidence source,
lane, staged count, age, foreign hunks, whether a CT-17 receipt exists → then P2 with
`--continue`), `C.foreign-hunk` (P2 per path whose index blob ∉ {HEAD blob, MERGE_HEAD blob};
fixture `mise.dev.toml` `625569e` ∉ {`9cd396a` blob, `9793a0c`}; suppressed when `MERGE_MSG`
contains `parent hunk: <path>`), `C.hooks-break-delivery` (P1; `safe_configured_hooks` raised;
evidence the event name; fixture a local `hook.hk-pre-merge-commit.event=pre-merge-commit`),
`C.hooks-not-installed` (info; `hooks_installed=false`, `merge.ff` unset), `C.lane-not-remerged`
(P3; fixtures SKILL `ea893a8`, C1 `6c09b7f`), `C.worktree-after-publish` (P3), `C.untracked-overwrite-risk`
(P2 when `MERGE_HEAD` is set and a staged path has no HEAD blob and an untracked snapshot does
not exist under `<common>/claude-lanes/snapshots/`; fixture `.claude/settings.json`).
`C.no-commit-merge` is a session-review finding (P2 per token-anchored `git merge … --no-commit`
Bash command on the integration branch, parsed with `pretooluse_gate.actions()` after heredoc
stripping; fixtures `T:L1083, L1269, L1446, L2009` and the fork's `L14`).

**Surfaces.** `SessionStart` (the `MERGE IN PROGRESS` line is the first line after the header
when present). `integrate` and `publish` preflight: `C.merge-in-progress` → rc 2 (CT-18's
`publish-batch` already refuses `MERGE_HEAD`; the doctor makes the manual `delivery:prepare`
route refuse too). `pre-push`: `C.hooks-break-delivery` and `C.merge-in-progress`. CI: `skipped`
(a CI checkout has no `MERGE_HEAD`).

**Recovery.** User-confirmed: `./dev/mise run lane:integrate -- <unit> --continue` (replays the
gates from the staged state, writes the record, commits) or `--abort`; before CT-17, R5
Runbook 1 steps 2–6 in order. Auto, safe: `doctor --snapshot` copies every untracked path the
merge would overwrite plus `.claude/settings.local.json` to
`<common>/claude-lanes/snapshots/<utc>/` with a `MANIFEST.json` (`verify.py` shape) — the
SessionStart block offers it before any `--abort`. `C.hooks-break-delivery`: print `git config
--local --unset-all hook.<name>.<field>` lines and the CT-02b pointer; never auto.
`C.foreign-hunk`: print the `git diff --cached <MERGE_HEAD> -- <path>` hunk and the message-file
line to declare it.

**Tests first.** `test_integration_merge_in_progress_reported_once` (scratch repo after `git
merge --no-ff --no-commit lane` → one `C.merge-in-progress` with lane name, no `C.foreign-hunk`);
`test_integration_foreign_hunk_detected_and_declared` (edit a staged file to a third content →
`C.foreign-hunk`; add `parent hunk: <path>` to `MERGE_MSG` → gone);
`test_integration_hooks_break_delivery` (set `hook.x.event=pre-merge-commit` locally → P1;
`pre-push` only → `[]`); `test_integration_snapshot_lists_untracked_overwrites`
(`--snapshot` writes the manifest; re-run → `C.untracked-overwrite-risk` absent);
`test_integration_no_commit_merge_from_corpus` (corpus fixture with the fork's command and the
R7 heredoc → one finding, the heredoc ignored); `test_integration_clean_checkout_no_findings`.

**Ticket.** CT-22 (detectors, snapshot). CT-17 owns `lane:integrate --continue/--abort` and
`session:status`; CT-17's acceptance gains "`session:status` output equals `doctor --class C
--json`" so the two never drift (the doctor's `integration.py` is the module CT-17's `status`
imports). CT-02b owns the delivery reconciliation. Expected C2 artifact: PreToolUse deny of
`--no-commit`.

### D. User-invoked skills emulated and misrecorded

**Predicate.** No line in `docs/agents/*.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/**/*.md`
matches `standing authorization|invocation authority`; every `P/skill-invocations.md` row
with mode `typed by user`/`native` has a harness event (a user turn whose text starts with
`/<skill>` outside `<pasted_content>`, or a `Skill` tool_use with that name); `docs/agents/
issue-tracker.md` carries the installed seed's required headings and a `seed` marker whose
SHA matches the plugin cache; the plugin cache version equals the one recorded in
`skill-invocations.md`.

**Data.** The doc globs; `skill-invocations.md` table (columns Stage, Skill, Source, SHA-256,
Mode, Invoked by); transcript user turns (`type == "user"`, `message.content` text, not
`isMeta`, `origin.kind` absent or `user`), `queue-operation` lines (`content`), `system` lines
containing `Unknown command:`; `Skill` tool_use blocks; `~/.claude/plugins/cache/mattpocock/
mattpocock-skills/<ver>/` (path only) and `installed_plugins.json` version/SHA; the seed
headings list (R1's grep phrases; see Could not verify).

**Module `dev/doctor/invocations.py`.** Findings: `D.doc-wording` (P2 per line; fixture
`ticket-retro.md:7` "this standing user request is the invocation authority"),
`D.invocation-row-unbacked` (P2 per row; fixture: the `grill-with-docs` row "typed by user"
vs `T:L21` where the command sits inside `<pasted_content id="539c">`),
`D.invocation-unrecorded` (P3; a typed slash command or `Skill` tool_use with no row; fixture:
setup session `/mattpocock-skills:domain-modeling` at `T0:L127`), `D.seed-drift` (P3; missing
marker or heading), `D.plugin-version-drift` (info; cache version ≠ recorded).

**Surfaces.** `check:planning` / `check` (`D.doc-wording`, `D.seed-drift`, offline).
`SessionStart`: one `plugins:` line only when the cache version differs from the recorded one.
`session-review`: the row-vs-event comparison.

**Recovery.** C2's hook appends `P/skill-invocations.jsonl` (slash token or Skill name, SHA,
time); `doctor --fix D.invocation-unrecorded` regenerates the table rows from the jsonl (auto
once the jsonl exists; before that it prints the row). Wording fixes are literal edits for the
user (printed as `sed`-free before/after lines). Seed drift: the user types
`/mattpocock-skills:setup-matt-pocock-skills` (SYNTHESIS §6 step 2) and the doc gains the
marker `<!-- seed: <cache path> sha256=<hex> -->`.

**Tests first.** `test_invocations_doc_wording_flagged` (fixture doc with the sentence → one
finding; a doc quoting it inside a fenced block → still flagged, by design);
`test_invocations_row_typed_but_pasted` (transcript fixture: user turn text
`<pasted_content …>/mattpocock-skills:grill-with-docs …` → `D.invocation-row-unbacked`);
`test_invocations_native_row_backed_by_skill_tool_use` (Skill tool_use `grilling` → `[]`);
`test_invocations_seed_marker_present_and_matching` → `[]`.

**Ticket.** CT-23 (doctor sweep; transcript-reading detectors) for the row checks; CT-22 for
the static grep. Expected C2 artifact: the UserPromptSubmit/PostToolUse(Skill) appender.

### E. No ledger of requests, decisions and operations

**Predicate.** Every user-originated text of a session (user turns, queued prompts, rejected
slash commands `T:L565-566`) has a row in `P/requests-<session>.jsonl` (C2's capture); every
row has a `disposition ∈ {cited:<spec|ticket|decision id>, declined:<reason>, deferred:<id>}`
before the spec closes; every `P/decisions.jsonl` row with `kind == operation` has a `receipt`
(path, SHA or tracker read-back) before a handoff is written; `lanes/*.json tickets[]` ids
resolve to a tracker issue or an `approved` decision row.

**Data.** The two jsonl files (format per C2; the doctor tolerates absence with `skipped`),
transcripts (for the capture audit), `P/ticket-ledger.md` snapshot (`#nn` rows), `gh issue
view <n> --json number,labels` in the `sweep` surface only (3 s budget per call, max 10 calls),
`lanes/*.json`.

**Module `dev/doctor/requests.py`.** Findings: `E.request-uncaptured` (P2 per user text with no
row; session-review; fixture `T:L500` the AskUserQuestion-mod request and `L566` "Args from
unknown skill"), `E.request-undisposed` (P2 per row without disposition; `check:planning`),
`E.operation-unreceipted` (P2 per operation; fixture rows `#91 relabel` and `draft PR`; in
`sweep`, `gh issue view 91` still `ready-for-agent` confirms it), `E.lane-ticket-unresolved`
(P2; fixture gate-hooks `"CT-02 (… publication pending user approval)"` resolves to nothing).

**Surfaces.** `check:planning` (undisposed, unresolved, unreceipted — offline, using the
ledger snapshot). `Stop` reason once: C2's `stop_gate.py` extension may call
`doctor --class E --json` and surface the unreceipted operations list as its reason (the
doctor itself never blocks). `session-review`: capture audit. `SessionStart`: the `pending
user operations:` line.

**Recovery.** All user-confirmed: the doctor prints the undisposed requests as a numbered
list for an `AskUserQuestion` round (the mechanism the lost 19:14Z request asked for);
operations run through their qualified tasks (`issue:preview/apply/verify` for #91, `gh pr
create --draft` for the PR) and `ledger:sync` records the receipt. No auto-fix.

**Tests first.** `test_requests_uncaptured_user_turn` (transcript fixture with three user
texts, jsonl with two → one finding naming the third's timestamp and first 80 chars);
`test_requests_rejected_slash_command_counts_as_request` (`system` "Unknown command" + the
queue-operation content → finding); `test_requests_operation_without_receipt` →
`E.operation-unreceipted`; `test_requests_lane_ticket_resolves_to_ledger_row` → `[]`;
`test_requests_absent_ledger_is_skipped_not_failed` (`severity: skipped`).

**Ticket.** CT-23 (transcript side) and CT-15 `check:planning` (static side; the rule lives in
`dev/doctor/requests.py` and `check:planning` calls `doctor --class E,N --surface check`).
Expected C2 artifacts: the capture hook and the jsonl formats; C3 reads them.

### F. Agent roles and briefs not machine-sourced

**Predicate.** The set of `.claude/agents/*.md` names equals the list the session was offered
(`agent_listing_delta` / the `Available agent types` reminder); no `.claude/agents/*.md` is
newer than the session's first transcript line; every `Agent` call carrying a lane marker
(`LANE-UNIT:` or `Role: implementer|doc-writer|reviewer|retro-writer`) uses that
`subagent_type`; an implementer transcript holds a `Skill` tool_use named `*tdd` before its
first `Write|Edit` of a non-test `.py`; no `Agent` call passes `isolation: worktree`; lane
briefs ≤ 1.5 KB; no `.claude/agents/*.md` line says `arrives with CT-nn` for a file that exists.

**Data.** `.claude/agents/*.md` (names, mtimes); transcript attachments of type
`agent_listing_delta` and `skill_listing`, and `Available agent types` reminders in user
turns (`T:L25/L46`); `Agent` tool_use inputs (`subagent_type`, `isolation`, `prompt` length);
`subagents/agent-*.jsonl` (+ `.meta.json agentType`); `CODING_STANDARDS.md` existence.

**Module `dev/doctor/agents.py`.** Findings: `F.agents-not-offered` (P2; set difference,
evidence the mtimes; fixtures: the five role files landed 20:07–20:25Z, session started 18:40Z),
`F.lane-dispatch-generic` (P2; count and the first three agent ids; fixture 17/17
`general-purpose`), `F.worktree-isolation-used` (P2), `F.tdd-not-first` (P3 per implementer
transcript), `F.brief-oversized` (P3; after CT-19), `F.role-file-stale` (P3; fixture
`reviewer.md:18` "arrives with CT-04" while `CODING_STANDARDS.md` exists).

**Surfaces.** `SessionStart`: records `session_start_utc` and the agent-file mtimes in
`<common>/claude-doctor/session-<id>.json`; the `agents:` line. `UserPromptSubmit`: after the
first prompt the transcript holds the listing attachment; when it differs from disk the line
`agents: 5 on disk, 0 offered → restart the session` is injected once. `check`:
`F.role-file-stale`. `session-review`: dispatch types, tdd order, brief sizes.

**Recovery.** Restart the session (user; the harness enumerates agents at start — see Could
not verify). `lane:brief` (CT-19) replaces hand-written briefs. Stale role text: literal edit
printed. No auto-fix (role files are CT-19's `owned_paths`).

**Tests first.** `test_agents_created_after_session_start_flagged` (fixture agents dir with
mtimes after the recorded start → one finding); `test_agents_lane_prompt_with_general_purpose`
(transcript fixture: one `Agent` with `LANE-UNIT:` and `general-purpose` → one finding; one
with `implementer` → `[]`); `test_agents_tdd_skill_before_first_write` (subagent fixture with
`Skill tdd` then `Write dev/x.py` → `[]`; reversed → `F.tdd-not-first`);
`test_agents_role_file_arrives_with_existing_artifact`.

**Ticket.** CT-22 (static) + CT-23 (transcript). CT-19 owns the briefs and role bodies.

### G. Subagent reports condensed by the parent; no machine receipt

**Predicate.** Every `<task-notification>` user turn is followed, before the next user prompt,
by a processing action (a `Write|Edit|Bash` that changes a file under `P/` or commits, a
`SendMessage`, or an `Agent` dispatch; a read-only `Bash` or `SendUserMessage` does not
count); every reviewer's final disposition equals the lane record's `review`; every `P\d-\d+`
item in a reviewer's final report has a row (or an explicit rejection) in `retros/<unit>.md`;
every SHA an implementer reports resolves and is the lane tip or named in the record; every
"Not run:|could not tell|unverified whether" sentence in a final report appears in a record;
`<common>/claude-lanes/<unit>.jsonl` (CT-19 journal) agrees with the record.

**Data.** Main transcript (`origin.kind == "task-notification"` user turns with `<task-id>`,
`<status>`, `<summary>`), `subagents/agent-<id>.jsonl` last assistant text (bounded 4,000
chars, `mask()`ed), `.meta.json` (`agentType`, `description`), `lanes/*.json`, `retros/*.md`,
the journal files, `git rev-parse --verify`.

**Module `dev/doctor/receipts.py`** (reuses `codex_rollout_digest.clip/mask/SECRET_RE` by path
import). Findings: `G.notification-unprocessed` (P1 when `<status>failed</status>`, else P2;
subject agent id and description; fixtures `T:L2029` a22113b3 failed → parent's only
follow-up was a read-only Bash (`L2032`) then death; `T:L1984` a221b354 PASS → only
`SendUserMessage`), `G.disposition-vs-record` (P1; fixture "Re-review (e12cf04): PASS" vs
record "awaiting cold review"), `G.p-item-unrecorded` (P2 per item; fixture a221b354 P3-5 and
the re-review P3 absent from `retros/gate-hooks.md`), `G.sha-unrecorded` (P2; a reported SHA
not in the record; fixture aa49b9b1 `e12cf04` vs record with no `merged_head`),
`G.open-claim-dropped` (P3; fixture a73b376a "could not tell whether … network"),
`G.journal-vs-record` (P2; CT-19 journal last reviewer line ≠ `review`), `G.journal-missing`
(P3; lane ≥ reviewed with no journal; `skipped` before CT-19 integrates).

**Surfaces.** `SessionStart`: the `previous session` line's counts come from a bounded scan of
the last 300 lines of the most recent sibling transcript (≤ 1 s). `session-review`: full
table (27 agents in the fixture session). `integrate` preflight: `G.disposition-vs-record`
and `G.p-item-unrecorded` for the unit (reads the journal, else the subagent transcript named
in the record's `review_transcript` field if present, else `skipped`).

**Recovery.** `lane:set <unit> --from-journal` (CT-19): auto when the journal holds exactly one
latest reviewer line and the record's `review` is absent or older (derived fact). Unrecorded
P-items: dispatch `retro-writer` for the unit (user-confirmed; the doctor prints the items).
Unprocessed notification: the doctor prints the agent's final report (bounded 2 KB, masked)
into the SessionStart/UserPromptSubmit context so the parent processes it now; nothing is
written for it.

**Tests first.** `test_receipts_failed_notification_followed_by_readonly_bash_is_unprocessed`
(fixture `transcripts/notification-failed/`: notification user turn, one assistant Bash
`git status`, one `isApiErrorMessage` assistant → exactly one P1);
`test_receipts_pass_notification_with_only_send_user_message` (→ P2);
`test_receipts_notification_followed_by_record_write_is_processed` (assistant `Write
P/lanes/x.json` → `[]`); `test_receipts_reviewer_disposition_vs_record` (subagent final
"Re-review: PASS", record `status: implemented`, no `review` → `G.disposition-vs-record`);
`test_receipts_p_items_all_in_retro` (P2-1, P3-1 in report and retro → `[]`; P3-5 missing →
one finding naming `P3-5`); `test_receipts_journal_line_lifts_review` (`--fix` writes
`review` from the journal, re-run `[]`).

**Ticket.** CT-23 (sweep) and CT-20 (the digester the sweep uses). CT-19 owns the journal writer
(expected C2 artifact) and `lane:set --from-journal`.

### H. Shape-checked gates mistaken for truth

**Predicate.** Every `dev/test_*.py` and `dev/**/test_*.py` is discovered by `dev/check.py`'s
patterns, or named by a `test:*` task that `check:research` `depends` on (including
`mise/tasks/*.toml` includes), or listed in `dev/doctor/exemptions.json` with a reason;
`retros/<unit>.md` exists for every `lanes/<unit>.json` (an alias — a retro named from the
branch slug — is a finding, not a pass); every retro deferral row naming `CT-nn` cites an item
id `CT-nn#<k>` that resolves in the manifest (`proposals/**/tickets*.json` or
`dev/issue-tickets.json`) or a `#<issue>` that exists in the ledger snapshot; every `ROOT /
"evidence/…"` (or `"evidence/..."`) constant in `dev/*.py` that sits within five lines of a
`*_SHA256 = "<64 hex>"` constant resolves to a tracked file with that hash; a retro's named-check
claim (`test:hooks rc 0`, `hk validate rc 0`, `check:research rc 0`) has a receipt line in the
unit's journal or an `evidence/` path (after CT-11 writes check receipts).

**Data.** `git ls-files 'dev/test_*.py' 'dev/*/test_*.py'`; `dev/check.py` discovery tuples
(parsed by regex `("dev", "test_research_*.py")` style, not imported); `mise.dev.toml` +
`mise/tasks/*.toml` via `tomllib` (`[tasks."check:research"].depends`, each task's `run`
string for `-p <pattern>`); `lanes/*.json`, `retros/*.md`; manifests; `git ls-files
--error-unmatch`, `git hash-object` vs the pinned hex; journals.

**Module `dev/doctor/gates.py`.** Findings: `H.unwired-test` (P1 per file; fixtures
`dev/test_retro_gate.py` today, `dev/test_hooks.py` before the staged hunk),
`H.retro-unit-alias` (P2; fixture `a06-unit3` → `retros/a06-classification-methods.md`
resolves through `branch`, `retros/a06-unit3.md` absent), `H.retro-deferral-unbound` (P3 per
row; fixtures `retros/team.md:27`, `nav.md:26`, `codex-session-history.md:54`),
`H.pinned-data-missing` (P1; fixture `dev/codex_examples.py:25-26` `config-schema.json`
`7933a705…`; evidence whether the snapshot holds a matching blob), `H.pinned-data-hash-mismatch`
(P1), `H.named-check-claim-unreceipted` (P3; `skipped` until CT-11 receipts exist).

**Surfaces.** `check` (the doctor is `check`'s first `depends`), CI, `integrate` preflight.
`SessionStart`: only the P1 counts in the `findings:` line (no detail; `check` carries it).

**Recovery.** `H.unwired-test`: print the exact `[tasks."test:<name>"]` TOML row and the
`depends` entry (CT-12 lands `test:retro-gate`); no auto. `H.retro-unit-alias`: `lane:set
a06-unit3 retro_record=retros/a06-classification-methods.md` once `retro_gate.py` learns
`retro_record` (CT-12 "alias routed here"), or `git mv` — user-confirmed. `H.pinned-data-missing`:
`doctor --fix H.pinned-data-missing --from-snapshot P/imports/codex-worktrees-20261013` copies
the file from `<snapshot>/2a14/untracked/<path>` after `MANIFEST.json` and the pinned hash agree
(auto: the hash in code is the acceptance criterion; the copy lands untracked and the commit is
the user's). Deferral rows: print the row with the candidate item ids.

**Tests first.** `test_gates_unwired_test_detected` (fixture tree with `dev/test_x.py`, a
`mise.dev.toml` whose `check:research` lacks it → one P1; add `test:x` → `[]`; add to
`exemptions.json` with reason → `[]`); `test_gates_unit_retro_alias` (lanes/a06-unit3.json +
retros/a06-classification-methods.md → exactly `H.retro-unit-alias`; `B.retro-claim-unverified`
is asserted in the lanes test, not here); `test_gates_deferral_row_bare_ct_id` (retro row
"owner CT-02" → P3; "owner CT-02#3" with manifest item → `[]`; "#69" → `[]`);
`test_gates_pinned_evidence_missing_then_restored_from_snapshot` (`dev/x.py` with `SCHEMA =
ROOT / "evidence/a.json"` and `SCHEMA_SHA256 = <sha of fixture>`; missing → P1; `--fix
--from-snapshot` copies; re-run → `[]`; a snapshot blob with the wrong hash → still P1, nothing
copied).

**Ticket.** CT-22 hosts `gates.py`; CT-12 moves `H.unwired-test` into `dev/check.py` by
importing `dev/doctor/gates.py:unwired_tests()` (one implementation, two callers; CT-12's
acceptance text gains that sentence). CT-21 consumes `H.pinned-data-missing`'s fix
(its acceptance makes `dev/codex_examples.py` exit 3 naming the path); after CT-21 the doctor
reads `dev/cited-inputs.json` for the pinned set instead of scanning constants.

### I. Configuration composition unvalidated

**Predicate.** `keys(.claude/settings.json) ⊆ {$schema, hooks, enabledPlugins,
extraKnownMarketplaces, env}`; `permissions ∉ keys`; `{marketplace of each enabledPlugins
key} ⊆ keys(extraKnownMarketplaces)`; no value contains `/Users/`; every hook `command`
names an existing script and `python3 -I <script> <<< '{}'` exits 0 within 1 s;
`.claude/settings.local.json` is excluded (`git check-ignore -q`); when a pre-split backup
exists, `{project − hooks} ⊎ local == backup` (R5's lossless assertion); `P/.mode` has no
`gate`; `env` (project or local) carries `PLAN_ID`, local carries `PWF_PLAN_ROOT` and
`PWF_TRUSTED_PYTHON`; every lane record has `resource_admissions.network ∈ {none,
admitted:<id>}` (CT-05 field); seed/plugin versions as in D.

**Data.** The two settings files, `.git/info/exclude`, `git check-ignore`, the backup search
list (`<common>/claude-lanes/snapshots/*/.claude/settings.json`, `RV/settings.json.before-ct02`),
`P/.mode`, `lanes/*.json`.

**Module `dev/doctor/settings.py`.** Findings: `I.settings-non-project-key` (P1 per key;
fixture staged file: `permissions`, and `enabledPlugins` carrying 8 entries incl.
`codex@openai-codex`, `eli5`, `html-plan`, `next-steps` → the plugin list is P2
`I.settings-plugin-undeclared-marketplace` when its marketplace is absent, P1 for
`permissions`), `I.settings-absolute-path` (P2), `I.settings-hook-script-missing` (P1),
`I.settings-local-not-excluded` (P1), `I.settings-split-lossy` (P1 when a backup exists and
the union differs), `I.mode-gate` (P2), `I.mode-absent` (P3), `I.pins-missing` (P3 per
variable), `I.lane-admission-missing` (P3 per lane; `skipped` before CT-05 defines the key).

**Surfaces.** `check` and CI (CT-16's rule; the doctor hosts it until CT-16 lands and CT-16
then imports `settings.py:project_key_violations()`), hk `pre-commit` (`doctor --surface
pre-commit`: `I.*` only, < 300 ms, so the staged file is refused before the commit; parent
hunk in `hk.pkl`), `SessionStart` (the `hooks:` line names the offending keys), `publish`
preflight (P1 → rc 2). Expected C2 artifact: PostToolUse on `.claude/settings*.json`.

**Recovery.** `doctor --fix I.settings-non-project-key --backup <path>`: writes the R5 §B
split (project = `$schema, hooks, enabledPlugins{4 workflow plugins}, extraKnownMarketplaces
{their 4}`, everything else to local), runs the key-set and lossless assertions, prints the
before/after key sets, and refuses when the assertion fails. Auto under `--fix` because D4's
default was accepted and the assertion is total; the user still decides whether to commit.
`I.settings-local-not-excluded`: append to `.git/info/exclude` (auto). `I.mode-absent`:
write `inject-smart` (auto, CT-15 step 6). `I.pins-missing`: print the `env` block for
`settings.local.json` (user-confirmed: personal file).

**Tests first.** `test_settings_personal_keys_flagged` (the staged fixture → exactly
`I.settings-non-project-key[permissions]` + `I.settings-plugin-undeclared-marketplace`
×4 and nothing else); `test_settings_split_fix_is_lossless` (`--fix --backup` on the
`settings.json.before-ct02` fixture → both files, assertion passes, re-run `[]`);
`test_settings_split_refuses_when_union_differs`; `test_settings_hook_script_missing`;
`test_settings_recommended_file_is_clean` (R5 §B project file → `[]`).

**Ticket.** CT-16 owns the committed rule; CT-22 hosts the module and the fix; CT-15 owns
`.mode`/pins; CT-05 the admission key.

### J. Gate hooks without a real-command corpus or a latency contract

**Predicate.** For the corpus `dev/fixtures/doctor/bash-corpus.jsonl` (one line per real
Bash command of the session, `{"command": …, "expect": "gate"|"pass", "source": "T:L<n>"}`,
bodies of heredocs kept but redacted of paths outside the repo), `pretooluse_gate.actions()`
yields a merge/push/publish action exactly for the `gate` lines; the wall time of
`pretooluse_gate.main()` on each line with the retro gate stubbed is < `timeout − 2 s`
(settings `PreToolUse.timeout`); `git_gate.GATE_TIMEOUT × 2 ≤ timeout`; the transcript's
`system` hook lines contain no `timed out|blocking because onFailure` for repo hooks.

**Data.** The corpus (built once by `session_review.py --emit-corpus` from the 113 parent and
the fork/merger commands, reviewed by hand, committed), the staged hook scripts (path import),
`.claude/settings.json` timeouts, transcript `system` lines (`hookErrors`, `durationMs`,
`content`).

**Module `dev/doctor/hookcorpus.py`.** Findings: `J.corpus-mismatch` (P1 per line; fixtures:
R7's read-only heredoc containing `git merge`/`git push` text expected `pass`, the fork's real
`git merge --no-ff --no-commit claude/gate-hooks-wiring` expected `gate`), `J.hook-latency`
(P2; per-call ms over budget), `J.timeout-arithmetic` (P3; `8 × 2 > 10` today),
`J.hook-error-observed` (P2; session-review; fixture: the review session's "timed out;
blocking because onFailure is block" line).

**Surfaces.** `check` and CI (corpus replay with the gate stubbed: no git subprocess, < 200
ms). `session-review` for observed errors. Not at SessionStart.

**Recovery.** Code changes are CT-02b's; the doctor prints the mismatching lines and the
`actions()` output. `J.timeout-arithmetic`: print the settings edit. No auto-fix.

**Tests first.** `test_hookcorpus_heredoc_text_does_not_gate` (the R7 command → no action);
`test_hookcorpus_real_merge_gates` (→ one `merge` action with the lane);
`test_hookcorpus_latency_under_budget` (stubbed gate, 50 corpus lines, each < 100 ms);
`test_hookcorpus_timeout_arithmetic` (settings fixture timeout 10, `GATE_TIMEOUT` 8 → P3;
timeout 30 → `[]`). The first two fail today against `e12cf04` (that is the point) and pass
after CT-02b; the corpus test is therefore CT-02b's acceptance test, shipped by CT-22 as
`expectedFailure` until CT-02b lands.

**Ticket.** CT-22 (corpus, replay); CT-02b (the fix).

### K. Planning files unstructured for the plugin; progress by append; no host pin

**Predicate (extends `plan-doctor.sh`, does not repeat it).** `plan-doctor.sh` already checks
resolution, that `inject-plan.sh --context=userprompt` emits a frame, attestation presence,
install surfaces and one fire's latency; `check-complete.sh` reports phase counts. The doctor
adds: `task_plan.md` has `## Goal`, `## Next Step`, `## Current Phase`, `## Phases` with ≥ 1
`### Phase` and exactly one `**Status:** in_progress`; `size(progress.md) < 500 KB` (P2) and
`< 900 KB` (P1; pwf's 1 MiB cliff silences all injection); the last 20 lines of `progress.md`
start at an entry boundary (a line beginning `- 20` within the window); the handoff block, if
still used, ends by line 30 and the NEXT bullet is within the last 20 lines (CT-15
`plan:handoff --check` owns this; the doctor calls it when the task exists, else its own
regex); **from each lane worktree cwd** the pretool view's nonce equals the root's (R4's probe:
`python3 -I W/scripts/inject-plan.py --context=pretool` with the host env, parse `nonce=`);
`W` version in `~/.claude/plugins/cache/planning-with-files/planning-with-files/` equals the one
the memory/record names; subagent transcripts show ≤ 5 identical `hook_additional_context`
frames (P3; upstream).

**Data.** `P/task_plan.md`, `P/progress.md`, `P/.mode`, `git worktree list --porcelain`
(`.claude/worktrees/*` only), `W/scripts/inject-plan.py` (subprocess, 42 ms each, run for at
most 8 worktrees → ≤ 400 ms), `W/scripts/check-complete.sh` (advisory), subagent transcripts.

**Module `dev/doctor/planfiles.py`.** Findings: `K.plan-no-phases` (P2; today 0 `### Phase`),
`K.plan-missing-keep-section` (P2 per section), `K.plan-multiple-in-progress` (P2),
`K.progress-size` (P2/P1), `K.progress-tail-mid-entry` (P3), `K.handoff-window` (P2),
`K.worktree-stale-plan` (P2 per worktree whose nonce differs; fixture `.claude/worktrees/team`
nonce `99dca3` vs root `66846b`), `K.pwf-version-drift` (info), `K.subagent-reinjection` (P3;
session-review).

**Surfaces.** `check:planning` (CT-15) and `check` (static; the worktree probe is skipped in
CI). `SessionStart`: the `plan:` line (phases, size, injection bytes from the python twin,
`.mode`), ≤ 150 ms. `session-review`: re-injection counts.

**Recovery.** The one-time migration (R4 steps 1–10) is user-confirmed. Auto under `--fix`:
`I.mode-absent` (above); `K.progress-size` → `doctor --fix K.progress-size` moves lines up to
the last publication marker into `progress-archive-<date>.md` and leaves a header plus the
tail (auto only after `.claude/rules/planning-records.md` admits dated archives, which CT-05
owns; before that it prints the `git mv` plan). Pins → `settings.local.json env` printed.

**Tests first.** `test_planfiles_zero_phases_flagged` (today's plan head as fixture → `K.plan-no-phases`
+ three `K.plan-missing-keep-section`); `test_planfiles_skeleton_is_clean` (R4's skeleton →
`[]`); `test_planfiles_progress_over_limits` (900 KB fixture → P1); `test_planfiles_worktree_nonce_differs`
(fixture repo with a worktree carrying an older `task_plan.md`, `W` stub script printing a
nonce derived from the file hash → one finding; with `PWF_PLAN_ROOT` pinned → `[]`).

**Ticket.** CT-15 owns `check:planning`, `plan:log`, `plan:handoff`; CT-22 hosts the worktree
probe and the size/structure predicates (`check:planning` calls `doctor --class K`).

### L. Outputs in ephemeral or untracked locations

**Predicate.** Every path-like token in a tracked record or code constant resolves to: a
tracked path; a path on disk under the main checkout that is deliberately untracked and listed
in `dev/doctor/untracked-allow.json` with a reason; a path under `<common>/claude-lanes/` or
`<common>/claude-doctor/`; or an external path (`~/.codex/…`, `/var/folders/…/T/…`,
`~/.local/state/…`) accompanied within the same record by a SHA-256; no record cites
`/private/tmp` or `scratchpad`; untracked top-level entries are excluded or allow-listed; the
snapshot `P/imports/codex-worktrees-20261013` verifies (`verify.py` rc 0) while anything still
depends on it.

**Data.** `git ls-files` for `.planning/**/*.md`, `lanes/*.json`, `docs/**/*.md`, `dev/*.py`
(string constants), `AGENTS.md`, `GLOSSARY.md`; the token extractor from
`T1-dependency-scan.json`'s scan (`ref`, `kind ∈ {file, dir, basename}`, `target`,
`exists_in_tip`, `ondisk_main_checkout`, `in_snapshot`), reimplemented in the doctor from the
report's rules: tokens matching `(?:^|[\s`'"(])((?:evidence|docs|dev|\.planning|plugins|ci)/[\w./-]+)`
and absolute `/Users/…/claude-code-marketplace/…` paths; `MANIFEST.json` for `in_snapshot`;
`git status --porcelain --untracked-files=normal`; `.git/info/exclude`.

**Module `dev/doctor/citations.py`.** Findings: `L.cited-path-missing` (aggregated per citing
file: P1 when the citer is `dev/*.py`, P2 for docs/records, P3 for `progress.md` lines older
than the last publication; evidence `n refs, k in snapshot`; fixture: 101 missing / 241
reference lines, `dev/codex_examples.py` 4 refs, `task_plan.md:322`), `L.scratchpad-citation`
(P2 per line; fixture `00-evidence-index.md:17-20` style paths if they ever enter a record;
today's records: none in tracked files, `lanes/a06-unit3.json` cites the `/var/folders` packet
without a hash → `L.external-citation-unhashed` P3), `L.untracked-top-level` (P3 per entry;
fixtures `.agent/`, `P/reviews/`, `P/imports/`), `L.snapshot-verify-failed` (P2; `verify.py`
rc ≠ 0; `sweep` surface only, 11 MB hashing).

**Surfaces.** `check:planning`/`check` (citation resolver; ≤ 1 s on today's tree: 124 distinct
tokens), CI (same; `in_snapshot` evidence `skipped` when the snapshot is absent),
`SessionStart` (`cited paths:` line with the counts only, read from the last `check` result
cached in `<common>/claude-doctor/last-check.json` — the resolver does not run at start).

**Recovery.** `doctor --fix L.cited-path-missing --from-snapshot <dir> [--only dev]` copies
files whose MANIFEST hash is present (auto for code-cited data, i.e. the H.pinned set; the
rest user-confirmed because 7.4 MB of evidence and the `keep-private` classification in sweep A
are the user's call). `L.untracked-top-level`: append to `.git/info/exclude` or to
`untracked-allow.json` with a reason (auto for the exclude line when the entry is `.agent/`
or `*/reviews/`, printed otherwise). `L.external-citation-unhashed`: print the `sha256sum`
line to add.

**Tests first.** `test_citations_missing_paths_aggregated_by_citer` (fixture tree: `dev/x.py`
cites 2 missing, `docs/a.md` cites 1 missing + 1 present → two findings, P1 and P2, counts
2 and 1); `test_citations_snapshot_restores_code_cited_paths` (`--fix --only dev` copies the 2,
re-run leaves only the docs P2); `test_citations_scratchpad_reference_flagged`;
`test_citations_untracked_top_level_excluded_is_clean`; `test_citations_real_repo_matches_t1_scan`
(opt-in `DOCTOR_REAL_REPO=1`: the doctor's missing set equals `T1-dependency-scan.json`'s
`exists_in_tip == false ∧ ondisk_main_checkout == false` set — 101 today).

**Ticket.** CT-21 owns the cited-input invariant (`dev/check_inputs.py` walking every path a
tracked retro, manifest row or code default cites, `dev/cited-inputs.json` for keep-private
sets, `check:inputs` wired into `check`). The doctor therefore does not duplicate the
resolver: `L.cited-path-missing` calls `check_inputs.py` once it exists and, until then, runs
the T1-scan rules above; `L.scratchpad-citation`, `L.external-citation-unhashed`,
`L.untracked-top-level` and `L.snapshot-verify-failed` stay in CT-22. CT-21's lane consumes
the `--from-snapshot` fix (its own acceptance already copies the 119 files).

### M. Codex thread and packet state imported by hand

**Predicate.** The activation record `docs/agents/claude-takeover.md` carries a generated
fenced block ```` ```json codex-status ```` whose fields equal the probe's output: per named
thread the last turn's `status`/`error`/`completed_at`; the count and ids of children whose
last turn is `failed` inside a turn; automations with `status = ACTIVE` whose
`target_thread_id` is one of the threads (id, rrule, last cycle dir); each private packet's
`lane-ledger.json` `updated_at`, `source_writer_allocation.owner`, and whether
`SUPERSEDED-BY-CLAUDE.json` exists beside it; the newest research-coverage manifest per thread
with per-provider statuses; the worktree census (`git worktree list` rows with branch, HEAD,
dirty count under `GIT_OPTIONAL_LOCKS=0`, in-tip, in-origin) versus the table in
`findings.md`; `codex/*` branches with commits not in the tip versus the records.

**Data.** `codex_threads.py --json show|turns|children`, `codex_research_receipts.py --json`
(path-imported from `.claude/skills/codex-session-history/scripts/`, all read-only sqlite
`?mode=ro`), `~/.codex/automations/*/automation.toml` (`tomllib`), the packet path recorded in
`lanes/a06-unit3.json:import_source.codex_packet` and `claude-takeover.md`, `git worktree
list --porcelain`, `git for-each-ref refs/heads/codex`, `git merge-base --is-ancestor`,
`findings.md`.

**Module `dev/doctor/codexstate.py`.** Findings: `M.activation-record-drift` (P2 per field;
fixtures: "No Codex thread is mid-turn" vs 9 failed children; stop causes; "Context7 quota
exhausted" vs manifests `05:10Z/05:19Z` `context7 = ok`), `M.automation-active-unrecorded`
(P2; fixture `refresh-llvm-github-research` ACTIVE, 4 h, target `01a12bd1`),
`M.packet-not-superseded` (P2; fixture `qbj4yn5d/` has no supersession file; the packet
ledger still names `/root` at `d2a41032`), `M.worktree-census-drift` (P3; fixture 11 dirty vs
3 recorded; `codex/28|29-offline-refresh` unrecorded), `M.resume-window` (info; the usage-limit
date `2026-10-19` from the thread errors; the line appears at SessionStart within 48 h of it).

**Surfaces.** `SessionStart`: the `codex:` line (automation ACTIVE, packet mtime, supersession
present?) — sqlite is not opened at start; the automation toml and the packet file stat take
< 50 ms. `sweep` and the takeover procedure: the full probe. CI: `skipped`.

**Recovery.** `codex:status --write` (CT-10 addition) regenerates the fenced block in
`claude-takeover.md` and the worktree table in `findings.md` between `<!-- codex-status -->`
markers (auto: generated facts). The supersession file (`SUPERSEDED-BY-CLAUDE.json` with the
sweep-B notice text, the activation record path and SHA) is written into each packet by
`codex:supersede` after user confirmation (it writes into Codex's private state). Branch
cleanup stays user-confirmed.

**Tests first.** Fixtures under a temporary `CODEX_HOME` (the convention
`dev/test_codex_session_history.py` already uses): `test_codexstate_failed_children_counted`
(synthetic `state_5.sqlite`/`thread_history_1.sqlite` with 2 failed child turns → the probe
reports 2; a record block saying 0 → `M.activation-record-drift`);
`test_codexstate_active_automation_unrecorded` (toml fixture → P2; block lists it → `[]`);
`test_codexstate_packet_without_supersession` (dir fixture → P2; file present → `[]`);
`test_codexstate_write_regenerates_block_idempotently` (`--fix` twice → identical bytes).

**Ticket.** CT-10 (the skill owns `codex:status`/`codex:supersede`; `dev/doctor/codexstate.py`
is a thin caller shipped by CT-22 that `skipped`s until the scripts exist).

### N. Ticket pipeline unvalidated before build

**Predicate.** For every `proposals/**/tickets*.json` and `dev/issue-tickets.json`:
`parent_number` is `null` or an issue in the ledger snapshot; ids unique; `blocked_by` edges
acyclic within the set and each target in the set or a real issue; ids in ascending order of
definition; the builder's docstring count equals `len(tickets)`; the builder references no
`/private/tmp` or `scratchpad` input; `P/decisions.jsonl` holds `{"kind": "approval",
"subject": "to-tickets", "manifest_sha256": <current>}` before any `lanes/*.json` cites a `CT-`
id; `issue:create-preview` dry-run accepts the manifest (sweep).

**Data.** The manifest JSON files, `build_manifests.py` (regex over the docstring for
`(\d+|ten|eleven|twelve|…) tickets` and `TICKETS = [` entries), the decisions jsonl (C2
format), `ticket-ledger.md`, `lanes/*.json`.

**Module `dev/doctor/tickets.py`.** Findings: `N.manifest-placeholder-parent` (P2; fixture
`999999`), `N.manifest-count-mismatch` (P3; "ten" vs 11), `N.manifest-order` (P3; CT-11 before
CT-10), `N.manifest-cycle` (P1), `N.manifest-dangling-edge` (P2), `N.builder-scratchpad-input`
(P2), `N.approval-missing` (P2; lanes cite CT ids with no approval row; fixture all CT lanes
today), `N.preview-dry-run-failed` (P2; sweep).

**Surfaces.** `check` and CI (offline), `lane:allocate` refusal (CT-17 imports
`tickets.py:resolve_ticket()`), `sweep` (dry run).

**Recovery.** User-confirmed: rebuild the manifest with the real parent after the spec is
published (SYNTHESIS §6 step 4), record the approval row (the to-tickets quiz's "approved"
answer is the event C2 captures). No auto-fix.

**Tests first.** `test_tickets_placeholder_parent_and_count` (today's manifest shape → P2 +
P3 + order P3, nothing else); `test_tickets_cycle_detected`; `test_tickets_approval_row_clears_finding`;
`test_tickets_clean_manifest_no_findings`.

**Ticket.** CT-22 (validator); CT-17 (`lane:allocate` refusal); the R2 "Publication fixes"
runbook step supplies the fixture.

## Doctor task spec

**CLI.** `python3 -I dev/doctor/cli.py [--surface session-start|prompt|check|pre-commit|
pre-push|integrate|publish|ci|sweep|all] [--class A,B,…] [--check <id>,…] [--unit <u>]
[--json] [--format context] [--fix [<id>,…]] [--backup <path>] [--from-snapshot <dir>]
[--snapshot] [--session <id|latest>] [--repo <dir>] [--plan-id <id>] [--budget-ms <n>]`.
Hook payload JSON on stdin is accepted and used for `transcript_path`, `cwd`, `session_id`,
`source`, `context_tokens`. Defaults: `--surface all` in a terminal, `--surface check` when
`CI` is set.

**mise tasks** (`mise/tasks/doctor.toml`, included by the parent's `[task_config] includes`
hunk from R8 wave 0.3; until that convention lands, the same three rows go into
`mise.dev.toml` as a parent hunk):

```toml
[tasks.doctor]
description = "Detect merge, record, settings, gate, planning and citation drift; exit 2 on P1/P2"
dir = "{{config_root}}"
usage = 'arg "[args]" var=#true help="--surface … --class … --json --fix …"'
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/doctor/cli.py ${usage_args}'

[tasks."doctor:session-start"]
description = "Compact checkout-state block for a fresh session (hook form, exit 0 always)"
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/doctor/cli.py --surface session-start --format context'

[tasks."test:doctor"]
description = "Exercise every doctor detector against fixture repositories and transcripts"
run = '"${MARKETPLACE_PYTHON:-python3}" -I -m unittest discover -s dev -p "test_doctor*.py" -v'
```

Wiring (parent hunks, declared at integration): `[tasks.check].depends = ["doctor"]`;
`check:research` gains `test:doctor`; CT-17's `lane:integrate` and CT-18's `publish-batch`
call `doctor --surface integrate|publish --unit <u> --json` as their first step; the manual
A09 route adds `doctor` to the publish intent's `check_task` list (`delivery:prepare` itself
is SHA-bound and keeps no `depends`). Note on `depends`: mise runs `depends` concurrently and
before the task, so "first" means "a prerequisite", not an ordering among the 13 `check:research`
dependencies; the doctor is read-only and lock-free, so a concurrent `test:*` run cannot
corrupt it, and it must not take the CT-11 lock (a raced doctor result is still correct because
it reads git plumbing and files, not test outputs).

**hk** (`hk.pkl`, parent hunk, after CT-02b reconciles installation): `["pre-commit"]` step
`doctor-settings` = `./dev/mise run doctor -- --surface pre-commit` (`I.*` only, < 300 ms);
`["pre-push"]` step `doctor` = `./dev/mise run doctor -- --surface pre-push` (`B.status-*`,
`C.merge-in-progress`, `C.hooks-break-delivery`, `I.settings-*`).

**CI.** `check:research` already runs in the hosted research-fast workflow; the doctor's `ci`
profile runs there through `check`. Host-only detectors (`A`, `D.invocation-*`, `E.*-uncaptured`,
`G`, `K.worktree-stale-plan`, `M`) emit `skipped` with reason `ci`. `ci/acceptance.sh` is a
frozen baseline file and is not edited; a static `doctor --surface ci` step can join
`.github/workflows/research-fast.yml` only through CT-08's reviewed transition.

**JSON output.** `{"schema": "doctor/v1", "generated_utc": …, "surface": …, "repo": …,
"head": …, "merge_head": …|null, "findings": [ … ], "skipped": [ … ], "counts": {"P1": n,
"P2": n, "P3": n}, "duration_ms": n}`; the same object is written to
`<common>/claude-doctor/last-<surface>.json` on every run so the next SessionStart can print
counts without re-running slow detectors.

**Surfaces → detectors → budget.**

| Surface | Detectors (ids by class) | Budget | Writes |
|---|---|---|---|
| `session-start` | C.merge-in-progress, C.foreign-hunk, C.hooks-*, C.untracked-overwrite-risk; B.status-stale, B.review-missing, B.handoff-*; I.settings-non-project-key, I.settings-local-not-excluded, I.mode-*; A.previous-session-died (+ G counts from the last 300 lines of the previous transcript); F.agents-* (mtime form); K.plan-no-phases, K.progress-size, injection bytes via the python twin; M.automation-active-unrecorded, M.packet-not-superseded (stat only); E.operation-unreceipted (from decisions jsonl); counts from `last-check.json` for H/L/N | 3,000 ms | `<common>/claude-doctor/session-<id>.json` |
| `prompt` (UserPromptSubmit) | state digest (HEAD, MERGE_HEAD, index tree via `git write-tree` on a temp index, lanes dir hash, task_plan head hash) vs the stored one; when changed, the `session-start` set again; A.ctx bucket line; F.agents-not-offered (listing attachment form) | 1,500 ms | the digest file |
| `pre-commit` | I.* | 300 ms | none |
| `check` / `ci` | B.* (incl. the retro-gate subprocess), C.hooks-break-delivery, D.doc-wording, D.seed-drift, E/N static, F.role-file-stale, H.*, I.*, J.corpus-*, K.* (worktree probe skipped in CI), L.cited-*, L.untracked-top-level | 10 s | `last-check.json` |
| `integrate --unit` | B.* for the unit, C.*, G.disposition-vs-record, G.p-item-unrecorded, H.retro-unit-alias, H.unwired-test, N.approval-missing | 10 s | none |
| `publish` | C.merge-in-progress, B.status-* for every lane, I.*, H.unwired-test | 5 s | none |
| `pre-push` | the publish set | 5 s | none |
| `sweep` (session-review) | everything, plus A.* curve, C.no-commit-merge, D.invocation-*, E.request-uncaptured, F.lane-dispatch-*, F.tdd-not-first, G.* full, J.hook-error-observed, K.subagent-reinjection, L.snapshot-verify, M.* full, N.preview-dry-run (gh, ≤ 10 calls) | 120 s | `<common>/claude-doctor/sweep-<session>.json`, and `RV/<label>/00-evidence-index.md` when `/session-review` asks |

**Hook entries** (`.claude/settings.json` hunk, parent-owned; `onFailure` deliberately
absent so a doctor failure never blocks):

```json
"SessionStart": [{"matcher": "startup|resume|clear|compact|fork", "hooks": [{"type": "command",
  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/doctor/cli.py\" --surface session-start --format context",
  "timeout": 15, "statusMessage": "Checking checkout state"}]}],
"UserPromptSubmit": [{"hooks": [{"type": "command",
  "command": "python3 -I \"$CLAUDE_PROJECT_DIR/dev/doctor/cli.py\" --surface prompt --format context",
  "timeout": 5}]}]
```

The `context` format prints the block below as plain stdout (SessionStart and UserPromptSubmit
both add plain stdout to context); it prints nothing when there is nothing to say (`prompt`
surface with an unchanged digest and no bucket crossing).

## SessionStart context block spec

Template (≤ 30 lines, ≤ 2.5 KB; a line is omitted when its state is clean; the `MERGE IN
PROGRESS` pair, when present, is always lines 3–4; order within the block is P1 facts, then
records, then advisories; values below are today's, rendered from the evidence read for this
report, not from a run):

```
[doctor] checkout 2026-10-13T23:40Z · /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace · plan 2026-10-10-marketplace-macos-reflection-scaffold
branch codex/marketplace-native-onboarding · HEAD 9cd396a · origin 28fedf1 · ahead 1 · no upstream
MERGE IN PROGRESS since 21:30:16Z: MERGE_HEAD e12cf04 = claude/gate-hooks-wiring (lane gate-hooks) · 11 staged · 1 foreign hunk: mise.dev.toml
  resume: ./dev/mise run lane:integrate -- gate-hooks --continue · or: doctor --snapshot, then --abort · nothing else touches the index first
untracked top-level: .agent/ (unexcluded) · .planning/…/reviews/ · .planning/…/imports/ (snapshot 454/454 ok)
hooks: hk not installed (merge.ff unset) · project hooks live: PreToolUse Stop SubagentStop · settings.json carries non-project keys: permissions, enabledPlugins(8 → 4 undeclared marketplaces)
lanes 9: 7 integrated · 6 say "publication pending" but are on origin 28fedf1 · gate-hooks "awaiting cold review" vs re-review PASS 21:04Z (a221b354, unrecorded)
  retro claim: a06-unit3 says passed, retro:gate rc 2 (record is retros/a06-classification-methods.md) · base_sha off by one: gate-hooks, nav, c1-catalog-promotion
handoff task_plan.md:14-30: "local tip = published remote 28fedf1" but HEAD 9cd396a unpushed · "re-review in progress" contradicts PASS · NEXT bullet in tail: ok
previous session 464a2816: died 21:30:32Z "Prompt is too long" at ctx 977K · unprocessed: fork a22113b3 FAILED (merger: settings split + merge --no-commit) · PASS a221b354 not in any record
context: autoCompactEnabled=false (user setting) · checkpoint at ctx ≥ 600K (plan:handoff --write, plan:log, delegate) · no fork ≥ 650K
agents: .claude/agents has implementer doc-writer reviewer retro-writer extractor · offered list unknown until the first prompt
cited paths (last check): 101 missing from tip (22 code/data, 79 evidence) · 4 cited by dev/codex_examples.py · all 101 in imports/codex-worktrees-20261013
codex: automation refresh-llvm-github-research ACTIVE every 4h → 01a12bd1 (limit lifts 2026-10-19) · packet lane-ledger 14:07Z not superseded · 9 children died mid-turn
plan: 0 ### Phase (pwf status/gate/smart dark) · progress.md 246 KB · injection 5,359 B ok · .mode absent · worktree copies differ from root (8/8)
pending user operations: #91 relabel (tracker still ready-for-agent) · draft PR to main · to-tickets approval CT-01…CT-20 · settings composition (D4)
findings P1 4 · P2 11 · P3 7 → ./dev/mise run doctor   (json: doctor -- --json; fix derivable facts: doctor -- --fix)
```

Rules: every SHA is 7 chars; every claim on a record line names the file; no line quotes
transcript text beyond an agent description; the block ends with the `findings` line; the
`prompt` surface re-emits only the lines whose state changed plus the `findings` line.

## Session-review skill spec

**Name and home.** `agent-session-history` at `.claude/skills/agent-session-history/`
(mirrored under `.agents/skills/`, CT-07 byte-identity test), extending
`codex-session-history` with a Claude backend rather than forking it: `SKILL.md` keeps the
six-step shape (resolve → liveness → digest → receipts → cross-check → report with ordinals;
for Claude, "ordinal" = transcript line number `L<n>` and ISO timestamp) and routes
`codex://` ids to the existing scripts and Claude session ids/paths to the new ones.

**Scripts** (`python3 -I`, stdlib, no network):

- `claude_session_digest.py <session-id|path> [--subagents] [--out <file>] [--json]
  [--user-chars 2500] [--final-chars 3500] [--write-cap 400]` — streams `<id>.jsonl` and emits:
  identity (`sessionId`, `version`, `gitBranch`, first/last timestamps, line count, bytes);
  the user-turn ledger (every `type == "user"` text not `isMeta`/tool_result, plus
  `queue-operation` enqueues and `system` "Unknown command" lines, each with `L<n>`, time,
  first 2,500 chars `mask()`ed); the tool histogram; every `Agent` call (`L<n>`, description,
  `subagent_type`, model, `isolation`, prompt bytes, `LANE-UNIT` marker); every
  `<task-notification>` (`L<n>`, task id, status, summary, and the classification
  processed/unprocessed with the first following action); Bash commands clipped to 240 chars
  with pattern tags (R7 P1–P16; `--emit-corpus` writes the J corpus lines); Write/Edit paths;
  the ctx curve per user turn (`usage` sums) and the death point (`isApiErrorMessage`);
  attachment kinds by count and bytes (`hook_additional_context` per hook name); `Skill`
  tool_uses and slash tokens; commit SHAs seen in tool results (`COMMIT_RE` from the Codex
  digester). Reuses `codex_rollout_digest.py`'s `mask`, `clip`, `SECRET_RE`, `COMMIT_RE`,
  `SHA_RE` by path import; raw tool output is never copied.
- `claude_subagents.py <session-id> [--json]` — one row per `subagents/agent-*.jsonl`: id,
  `agentType`/`isFork`/`model` from `.meta.json`, first and last `usage` ctx, event count,
  the final assistant text (clipped), the P-items, SHAs, "Not run"/"could not" sentences and
  the disposition token it contains, re-injection frame count.
- `session_review.py <session-id|latest> [--label <RV dir>] [--json]` — joins the two
  digests with the repo (`lanes/*.json`, `retros/*.md`, `ticket-ledger.md`, `task_plan.md`,
  the journals, `skill-invocations.md`, `requests-*.jsonl`, `decisions.jsonl`) and prints the
  doctor's finding shape for classes A, C (no-commit), D, E, F, G, J, K (re-injection); it is
  the implementation `dev/doctor/cli.py --surface sweep` calls. With `--label` it also writes
  `RV/<label>/00-evidence-index.md` (the shape of this review's index: sessions table, user
  prompts, death point, git snapshot, subagent table) and prints the seven reviewer briefs
  (R1–R7) as `lane:brief`-style slots.

**Skill `/session-review <session-id|latest>`** (`disable-model-invocation: true`,
`argument-hint`): injects `` !`python3 -I <skill>/scripts/session_review.py $0 --json | head -c 12000` ``
and asks the model only to (1) list the P1/P2 findings, (2) propose the `lane:set
--from-journal`, `retro-writer` and `AskUserQuestion` actions per class, (3) record the run in
`P/progress.md` through `plan:log`. It writes nothing itself.

**Schedule.** Two routes, both user-admitted: (a) a `Stop`-time call is wrong (hooks must stay
short); instead the `SessionStart` surface already sweeps the previous session's last 300
lines; (b) a daily sweep `./dev/mise run doctor -- --surface sweep --session latest --json`
through the host scheduler (the `schedule` skill or launchd, outside the repo) writing
`<common>/claude-doctor/sweep-<id>.json`; the next SessionStart prints its P1 count. Nothing
in the repo registers a daemon (AGENTS.md: daemon registration waits for instruction).

**Tests.** `dev/test_agent_session_history.py` under a temporary `HOME` with synthetic
transcripts whose line shapes copy the real ones read for this report (user turn with
`promptSource`, assistant with `usage`, `attachment` of each kind, the task-notification turn,
`fork-context-ref`, `.meta.json`), asserting counts, the ctx curve, the death point, the
notification classification and that no real `~/.claude` path is opened (`HOME` points at the
fixture).

## Recovery table

| Class | Finding | Recovery action | Auto under `--fix`? | Precondition / who confirms |
|---|---|---|---|---|
| A | ctx-over-checkpoint | `plan:handoff --write`, `plan:log`, delegate with ≤ 1.5 KB briefs, `/clear` at ≥ 800 K | no (behavioural) | parent, immediately |
| A | fork-over-budget / previous-session-died | act on the G findings first | no | — |
| B | status-stale (published on origin) | add `integration_merge`, `published`, rewrite "publication pending" | **yes** (proven by git) | — |
| B | handoff-base-stale | rewrite the base/remote sentences (`plan:handoff --rewrite`) | **yes** | CT-15 or the doctor's two-sentence rewrite |
| B | retro-claim-unverified | run `retro:gate`; fix the record or demote `retro` | demotion printed, not applied | user |
| B | review-missing / disposition text | `lane:set <u> review=…` from the journal (G) | yes when the journal has one latest line | CT-19 journal |
| B | base-sha-off-by-one | `lane:set --from-git` (CT-17) adds `allocated_from` | yes after CT-17 | — |
| C | merge-in-progress | `lane:integrate -- <u> --continue` or `--abort` (R5 Runbook 1 before CT-17) | no | user chooses; `--snapshot` first |
| C | untracked-overwrite-risk | `doctor --snapshot` → `<common>/claude-lanes/snapshots/<utc>/` | **yes** | — |
| C | foreign-hunk | declare `parent hunk: <path>` in the message file or `git restore --staged` it | no | user |
| C | hooks-break-delivery | `git config --local --unset-all hook.<x>.<f>`; CT-02b | no | user |
| C | lane-not-remerged | send the lane back to merge the tip | no | parent |
| D | invocation-unrecorded | regenerate rows from `skill-invocations.jsonl` | yes once the jsonl exists | C2 hook |
| D | doc-wording / seed-drift | literal edit; `/setup-matt-pocock-skills` | no | user |
| E | all | `AskUserQuestion` round from the printed list; qualified operations; `ledger:sync` | no | user |
| F | agents-not-offered | restart the session | no | user |
| F | lane-dispatch-generic / brief-oversized | `lane:brief` (CT-19) | no | — |
| G | notification-unprocessed | the final report is injected (≤ 2 KB) for the parent to process | no (context only) | — |
| G | journal-vs-record / review lift | `lane:set --from-journal` | **yes** | one unambiguous latest line |
| G | p-item-unrecorded / open-claim-dropped | `retro-writer` rerun for the unit | no | parent dispatch |
| H | unwired-test | TOML row printed; CT-12 | no | — |
| H | retro-unit-alias | `retro_record` field (CT-12) or `git mv` | no | user |
| H | pinned-data-missing | copy from the snapshot when MANIFEST and the code hash agree | **yes** (untracked copy) | snapshot present |
| I | settings-non-project-key | R5 §B split with the key-set + lossless assertions | **yes** with `--backup` | backup present; assertion passes |
| I | settings-local-not-excluded / mode-absent | exclude line; `.mode = inject-smart` | **yes** | — |
| I | pins-missing | `env` block for `settings.local.json` printed | no | user (personal file) |
| J | all | CT-02b code; lines printed | no | — |
| K | plan structure / progress size | R4 migration steps; `progress-archive` after the rule amendment | no (size: yes after CT-05 amends the rule) | parent |
| K | worktree-stale-plan | pin `PWF_PLAN_ROOT`/`PLAN_ID` in the host env | no | user |
| L | cited-path-missing (code-cited) | copy from the snapshot (`--only dev`) | **yes** | MANIFEST hash present |
| L | cited-path-missing (docs/evidence) | import lane decides (keep-private vs import) | no | user |
| L | untracked-top-level | exclude line (`.agent/`, `*/reviews/`) | **yes** | — |
| M | activation-record-drift / census | `codex:status --write` regenerates the fenced block and table | **yes** (generated facts) | CT-10 scripts |
| M | packet-not-superseded | `codex:supersede <packet>` writes `SUPERSEDED-BY-CLAUDE.json` | no | user (Codex private state) |
| N | all | rebuild manifest; approval row; `issue:create-*` | no | user |

Auto-fixable findings: 12 of 58 ids (B ×2 + CT-17's third, C ×1, D ×1, G ×1, H ×1, I ×2,
K ×1 conditional, L ×2, M ×1). Every auto-fix prints before/after and refuses when its
assertion fails; none touches `status` promotion, `retro: passed`, Codex private state, the
index, or a frozen baseline file.

## Test inventory

Files: `dev/test_doctor.py` (scratch-repo detectors B, C, H, I, L, N; `Scratch` helper
mirrored from `dev/test_hooks.py`), `dev/test_doctor_transcripts.py` (A, D, E, F, G, J, K
re-injection over fixture transcripts under a temporary `HOME`), `dev/test_doctor_codex.py`
(M under a temporary `CODEX_HOME`), `dev/test_agent_session_history.py` (the skill).
Fixtures under `dev/fixtures/doctor/`:

| Fixture | Reproduces (evidence) | Detector asserted exactly | Clean twin |
|---|---|---|---|
| `repo/mid-merge` (built in test: lane branch, `merge --no-ff --no-commit`, one staged third-content file) | `MERGE_HEAD e12cf04`, foreign `mise.dev.toml` hunk (R5 P2-1) | `C.merge-in-progress`, `C.foreign-hunk` | after `git commit` → `[]` |
| `lanes/gate-hooks.json` + refs | status "awaiting cold review", no `review`, `base_sha` = allocation parent (R5 P2-4) | `B.status-stale`, `B.review-missing`, `B.base-sha-off-by-one` | corrected record → `[]` |
| `lanes/published-pending.json` + bare origin | six "publication pending" records on `28fedf1` (R5 P3-3) | `B.status-stale`; `--fix` adds `published` | — |
| `plan/task_plan-handoff.md` | "local tip = published remote `28fedf1`" vs HEAD `9cd396a` (R5 P3-5); "re-review in progress" (R6 P2-1) | `B.handoff-base-stale`, `B.handoff-text-contradicts-record` | rewritten block → `[]` |
| `settings/staged.json`, `settings/before-ct02.json` (key names and the shape of R5 P1-1; values replaced by placeholders except the plugin ids) | personal keys staged | `I.settings-non-project-key`, `I.settings-plugin-undeclared-marketplace` ×4; `--fix --backup` lossless | R5 §B project file → `[]` |
| `citations/` (3 citers, 3 missing, MANIFEST + snapshot blobs) + opt-in real-repo run | 101 missing cited paths (T1 scan), `codex_examples.py` pins | `L.cited-path-missing` ×2 (P1, P2), `H.pinned-data-missing`; `--fix --from-snapshot` | all present → `[]` |
| `transcripts/notification-failed/` (`<id>.jsonl` 6 lines + `subagents/agent-a22113b35136b11c1.{jsonl,meta.json}` 18-line shape) | `T:L2029` failed fork, probe, death (R6 "Unprocessed notifications") | `G.notification-unprocessed` (P1), `A.previous-session-died`, `A.fork-over-budget` (970,505) | notification followed by a `Write` under `P/` → only `A.fork-over-budget` |
| `transcripts/review-pass-unrecorded/` | `T:L1984` a221b354 re-review PASS, record stale, P3-5 dropped (R6 P2-1, P3 rows 5–7) | `G.disposition-vs-record`, `G.p-item-unrecorded[P3-5]` | retro row added → `[]` |
| `lanes/a06-unit3.json` + `retros/a06-classification-methods.md` | the a06 alias (R5 P2-5; C1 P1-13) | `H.retro-unit-alias`, `B.retro-claim-unverified` | `retros/a06-unit3.md` present → `[]` |
| `corpus/bash-corpus.jsonl` (R7 heredoc, the fork's merge, 10 benign commands) | PreToolUse false positive (R7 Guardrails) | `J.corpus-mismatch` (expectedFailure until CT-02b) | — |
| `plan/task_plan-today.md` (first 40 lines) / `plan/skeleton.md` (R4) | 0 `### Phase` | `K.plan-no-phases`, `K.plan-missing-keep-section` ×3 | skeleton → `[]` |
| `repo/worktree-stale` + stub `inject-plan.py` | R4 nonce probe | `K.worktree-stale-plan` | pinned env → `[]` |
| `codex/` (synthetic sqlite, `automation.toml`, packet dir) | 9 dead children, ACTIVE automation, packet ledger (R3, sweeps B/C) | `M.*` ×3 | record block regenerated → `[]` |
| `tickets/preview-999999.json`, `build_manifests.py` docstring | placeholder parent, "ten", order (R2) | `N.*` ×3 | fixed manifest → `[]` |
| `invocations/` | pasted `/grill-with-docs`, typed `/domain-modeling` (R6 Setup session), `ticket-retro.md:7` wording | `D.*` ×3 | — |
| `agents/` dir with late mtimes; transcript with `LANE-UNIT` + `general-purpose` | agents never offered; 17/17 generic (C1 P1-12) | `F.agents-not-offered`, `F.lane-dispatch-generic` | — |

Every detector test has the false-positive twin (last column) asserting `run(ctx) == []`, and
`test_doctor_cli_exit_codes` asserts 0/2/1/3. The real-repo tests (`DOCTOR_REAL_REPO=1`) are
not part of `check`; they are the implementer's receipt that the fixtures reproduce today's
tree (expected counts: 4 P1, 11 P2, 7 P3 on this checkout at `9cd396a` + `MERGE_HEAD e12cf04`).

## Ticket mapping

Owned paths of the doctor lane are disjoint from every R8 wave-1 lane (`ct02b`: `dev/hooks/`,
`dev/git_delivery.py`; `ct11`: `dev/check.py`, `dev/retro_gate.py`, `dev/check_lock.py`;
`ct05`: `dev/lane.py`, `dev/ledger.py`, `.claude/rules/planning-records.md`; `ct15`:
`dev/plan_records.py`) and from wave 2 (`dev/lane_brief.py`, `dev/hooks/subagent_receipt.py`,
`.claude/agents/*.md`).

| Ticket | Scope | Detectors / artifacts | Blocked by | Owned paths | Parent hunks at integration |
|---|---|---|---|---|---|
| **CT-22** (new) Doctor core and static detectors | `dev/doctor/{cli,core,lanes,integration,settings,gates,citations,tickets,planfiles,hookcorpus,agents,invocations,requests,codexstate}.py`, fixtures, tests, mise rows, the SessionStart/UserPromptSubmit context block, `--fix` for the 12 auto ids, `--snapshot` | A (static part), B, C, F.role-file-stale, H, I, J corpus, K static + worktree probe, L, N; thin callers for E/M that `skipped` until their inputs exist | none for wave 1 (reads `dev/hooks/git_gate.py` and `git_delivery.safe_configured_hooks` by path import, no edits) | `dev/doctor/**`, `dev/test_doctor*.py`, `dev/fixtures/doctor/**`, `mise/tasks/doctor.toml`, `P/retros/ct21-doctor.md`, `P/lanes/ct21-doctor.log.md` | `.claude/settings.json` two hook entries; `[tasks.check].depends`; `check:research` `test:doctor`; `hk.pkl` two steps (after CT-02b) |
| **CT-23** (new) Doctor sweep and session review | `session_review.py`, the transcript detectors, `/session-review`, the corpus emitter | A curve/death, C.no-commit, D rows, E capture, F dispatch/tdd, G all, J observed, K re-injection | CT-20 (digester) or co-allocated with it; CT-19 for journal reads (skips without it) | `.claude/skills/agent-session-history/**`, `.agents/skills/agent-session-history/**`, `dev/test_agent_session_history.py`, `dev/test_doctor_transcripts.py`, `dev/fixtures/doctor/transcripts/**` | `progress.md` line via `plan:log` |
| CT-20 (existing) | gains `claude_session_digest.py`, `claude_subagents.py` (the brief's "agent-session-history extending codex-session-history") | the digesters CT-23's review uses | CT-07, CT-10 | as SYNTHESIS §6 | — |
| CT-21 (existing, on disk) Import Codex worktree inputs | `dev/check_inputs.py`, `check:inputs`, `dev/cited-inputs.json`, the 119-file import | L.cited-path-missing's resolver, H.pinned-data set | none | per its lane record | `check`/`check:research` wiring (its own ticket) |
| CT-10 (existing) | gains `codex_status.py` (`codex:status --write`) and `codex:supersede` | M | — | the skill's two subtrees | the fenced block markers in `claude-takeover.md`, `findings.md` |
| CT-05 (existing) | `lane:validate` imports `dev/doctor/lanes.py` predicates; `lane:set --from-git` | B refusal form | — | as R8 | — |
| CT-12 (existing) | `dev/check.py` imports `dev/doctor/gates.py:unwired_tests()`; `retro_record` alias | H.unwired-test, H.retro-unit-alias | — | as R8 `ct16` | — |
| CT-15 (existing) | `check:planning` calls `doctor --class D,E,K,L,N --surface check`; `plan:handoff --check/--write` | K window, B handoff rewrite | — | as R8 | — |
| CT-16 (existing) | imports `dev/doctor/settings.py:project_key_violations()` | I | CT-02, D4 | — | — |
| CT-17 (existing) | `session:status` = `doctor --class C --json`; `lane:integrate` first step = `doctor --surface integrate --unit`; `lane:allocate` imports `tickets.py:resolve_ticket()` | C, N refusal forms | as SYNTHESIS | as R8 `ct12` | — |
| CT-18 (existing) | `publish-batch` first step = `doctor --surface publish` | C, B, I at publish | CT-02 | as R8 `ct13` | — |
| CT-19 (existing) | journal format consumed by `receipts.py`; `lane:set --from-journal` | G | as SYNTHESIS | as R8 `ct14` | — |
| CT-02b (existing) | makes `J.corpus-mismatch` pass; reconciles `C.hooks-break-delivery` | J, C | CT-02 | as R8 | — |

Expected C2 artifacts under the same class ids (C3 reads, never writes them): A PreToolUse
`Agent` fork deny; C PreToolUse `--no-commit` deny; D `skill-invocations.jsonl` appender;
E `requests-<session>.jsonl` and `decisions.jsonl` capture; G `subagent_receipt.py` journal
(CT-19); I PostToolUse settings guard. If C2 also proposes a SessionStart hook or a
`session:status` probe, it is the same artifact as CT-22's `session-start` surface and should
be built once, in `dev/doctor/`.

Slotting: CT-22 fits wave 1 as a fifth lane only if the user lifts R8's four-lane cap;
otherwise it is the first wave-2 lane (its `owned_paths` intersect nothing there) and the
SessionStart block arrives one wave later than the merge-recovery need it answers. A
reduced CT-22a (`cli.py`, `core.py`, `integration.py`, `lanes.py`, `settings.py`, the
SessionStart surface, ~300 lines) could run in wave 1's heavy slot since it is offline and
touches no shared file; the rest becomes CT-22b in wave 2.

## Session-start playbook

What a fresh session (after `/clear`, `startup`, `resume` or `compact`) receives or runs, in
order; steps 1–2 are automatic once CT-22's hooks are in `.claude/settings.json`:

1. **Hooks (parallel):** pwf injects plan head-50 / progress tail-20 (unchanged); the doctor
   injects the checkout-state block (≤ 30 lines). The parent reads the doctor block first: it
   is state, the plan is intent.
2. **P1 lines first.** `MERGE IN PROGRESS` → the only admissible first action is the
   `--continue`/`--abort` decision (ask the user through `AskUserQuestion`, offering
   `--snapshot` first); nothing else touches the index. `settings.json carries non-project
   keys` → no commit until the split. `hooks:install` breakage → no publish.
3. **Previous session triage.** If the block names a dead session or unprocessed
   notifications: `/session-review latest` (or `doctor --surface sweep --session latest --json`);
   apply `lane:set --from-journal`, read the ≤ 2 KB final reports the sweep prints, dispatch
   `retro-writer` for unrecorded P-items.
4. **Records before plan prose.** For every lane the block flags, read `lanes/<unit>.json`
   and `retros/<unit>.md`; do not read `progress.md` history. Run `doctor --fix` for the
   derivable facts (published, integration merge, handoff base) and `plan:handoff --check`.
5. **Context budget.** Note the ctx line (0 after `/clear`; `context_tokens` on resume). Plan
   the checkpoint: at 600 K the parent writes the handoff and delegates; no fork past 650 K;
   Codex forensics and transcript digests run in subagents, never inline (R7 P14: 79 K tokens).
6. **Agents offered.** After the first prompt the `agents:` line says whether `.claude/agents`
   matches the offered list; if not, restart before dispatching any lane.
7. **Pending user operations.** Ask about the listed operations/decisions once, with
   `AskUserQuestion`, before building (E).
8. **Only then** continue from `## Next Step` (or the handoff `Next:` line until CT-15
   migrates the plan), dispatching through `lane:brief` with the role agent types.

The detector reads the budget from `transcript_path` (`usage` sums; `context_tokens` on
resume/fork), never from `<total_tokens>`; thresholds live in `dev/doctor/budget.py:THRESHOLDS`
`{"warn": 400_000, "checkpoint": 600_000, "fork_deny": 650_000, "clear": 800_000,
"bytes_per_ktoken": 7_300}` and C2's deny hook imports the same dict.

## Could not verify

- Whether `hookSpecificOutput.additionalContext` on `SessionStart` and plain stdout are both
  added for `source: clear` in CLI 2.1.296 exactly as for `startup`: the docs' SessionStart
  example shows `additionalContext`, and the pwf hook's `L6` payload proves the `clear` route
  injects; the doctor uses plain stdout (documented for SessionStart and UserPromptSubmit) and
  the context block was not run through a live hook here.
- The `agent_listing_delta` attachment's content shape (seen once in the main transcript, not
  opened); `F.agents-not-offered` therefore also carries the mtime form, which needs no
  attachment.
- `transcript_path` lag ("may lag the in-memory conversation"): the ctx line may be one turn
  behind; the thresholds leave 50 K of margin for that.
- Whether mise `depends` on `check` runs before or concurrently with `check:research`'s other
  dependencies (treated as concurrent; the doctor is lock-free and read-only for that reason),
  and whether `task_config.includes` validates under `./dev/mise` (R8 D7; the rows fall back
  into `mise.dev.toml` as a parent hunk).
- The seed headings `D.seed-drift` must look for: R1 names the phrases; the installed seed
  file path under `mattpocock-skills/1.3.1/` was not opened.
- The exact C2 formats for `requests-<session>.jsonl`, `decisions.jsonl`,
  `skill-invocations.jsonl` and the CT-19 journal: E, D and G detectors are specified against
  the field names used here and must be aligned when C2's design lands.
- The doctor's expected counts on today's tree (4 P1, 11 P2, 7 P3) are derived from the
  reports and the lane projections, not from a run; the real-repo test fixes them at
  implementation time.
- `git write-tree` on a temporary index for the `prompt` surface digest: cost on a 27-worktree
  common dir was not measured; `git diff --cached --quiet` plus `git status --porcelain`
  hashing is the fallback.
- hk 2.5.0 `check =` step syntax for the two doctor steps was taken from the staged `hk.pkl`
  and not validated with `hk validate`.
- Whether `codex_threads.py` can be imported as a module without side effects (its `main()`
  parses argv); the doctor may need to subprocess it, which the budget table assumes.
- Whether a lane worktree's hooks fire with the worktree cwd for `isolation: worktree`
  (R4 could not either); `K.worktree-stale-plan` detects the state regardless of how it
  arises.
