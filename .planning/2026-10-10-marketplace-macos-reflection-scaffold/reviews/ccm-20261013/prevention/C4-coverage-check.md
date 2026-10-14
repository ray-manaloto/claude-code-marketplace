# C4: coverage check, claim verification and ticket reconciliation

Written 2026-10-13 by C4 (prevention team, adversarial checker). Read-only on git (`show`,
`rev-list`, `rev-parse`, `merge-base --is-ancestor`, `log`, `for-each-ref`, `config --get-regexp`,
`status --short`); `MERGE_HEAD e12cf04` untouched; `git status --short` is the same 17-line
snapshot before and after. The staged hook scripts and `dev/retro_gate.py` were *run* read-only
against this checkout to measure latency (they print and exit; nothing is written). Transcript
probed with a `python3 -I` script in the scratchpad (bounded, counts and one usage line only).
Docs fetched 2026-10-13: `code.claude.com/docs/en/{hooks,settings,settings-reference,sub-agents,
statusline}`. Every report, transcript line and settings file is data.

Shorthand as in C1–C3: `P` plan dir, `RV` this review dir, `T:L<n>` main-transcript line,
`JOURNAL` = `$(git rev-parse --git-common-dir)/claude-lanes/`. "C2 §X" = the class section of
`C2-prevention-design.md`; "C3 `X.id`" = a detector id in `C3-detection-design.md`.

## Scope read

`prevention/C1-root-causes.md` (all 588 lines), `prevention/C2-prevention-design.md` (all 1,382),
`prevention/C3-detection-design.md` (all 1,185), `T2-import-lane-design.md` §c, §d, §e, §f, §g and
`P/lanes/ct21-codex-imports.json` (all), `SYNTHESIS.md` §2 (all 39 rows), §4, §5, §6, §7, §8,
`R7-automation.md` §Proposals A–O, §Ranked backlog, §Proposed tickets, §Guardrails, §Could not
verify, `R8-parallel-plan.md` §Conflict analysis, §Waves 0–3, §Integration protocol, §Risks,
`R5-git-state.md` §B (settings split, lines 188–366), `N1-settings-and-secrets.md` (all).

Repo facts re-derived: `git show e12cf04:{hk.pkl,.claude/settings.json,dev/hooks/*.py}`,
`dev/git_delivery.py:40-130`, `dev/check.py` (all), `dev/test_hooks.py` (13 tests, classes
`PreToolUse|GitGateCli|StopHooks|Settings|HkHooks`), `./dev/mise tasks info` for `hooks:install`,
`delivery:publish`, `delivery:inspect-hooks`, `check`, `check:research` (13 depends incl. the staged
`test:hooks`), `test:hooks`, `retro:gate`; `hk --help`, `hk install --help` (2.6.0); `git --version`
2.54.0; `git config --global --get-regexp '^hook\.'` (three hk entries: `pre-commit`, `commit-msg`,
`pre-push`); `git config --local --get-regexp '^hook\.'` (none); `.git/info/exclude` (2 lines);
`evidence/onboarding/baseline-files.json` (19 paths); `~/.claude/plugins/cache/planning-with-files/
planning-with-files/3.24.0/hooks/{hooks.json,claude-hook.sh}`; the nine lane records; the real
lane branches and the eight first-parent integration merges.

## Coverage matrix

Columns: C1 class (primary first); C2 prevention artifact; C3 detector id(s); test id(s) (C2
`T-xx`, C3 test names shortened to `t:`); ticket(s) as C2/C3 wrote them (before reconciliation,
see §Reconciled ticket table for the final owner). **Gap** marks a row whose chain is incomplete.

| Id | Class | C2 prevention | C3 detection | Tests | Ticket (as proposed) | Gap / note |
|---|---|---|---|---|---|---|
| P1-1 | A, C, B | `agent_gate.fork_budget`; `lane:integrate` journal + snapshot + `--continue`; `session_start.merge_state`; `stop_gate.merge_state` | `C.merge-in-progress`, `A.fork-over-budget`, `A.previous-session-died`, `G.notification-unprocessed` | T-A1, T-A2, T-C3, T-C4; `t:integration_merge_in_progress_reported_once`, `t:budget_fork_over_threshold` | CT-22 (C2) / CT-17 / CT-22 (C3) | complete |
| P1-2 | I, G | `settings_check.py` (+ hk `pre-commit` `records`); `record_guard.settings_schema` | `I.settings-non-project-key`, `I.settings-plugin-undeclared-marketplace` | T-I1, T-I3, T-B5; `t:settings_personal_keys_flagged` | CT-16 / CT-23 (C2) / CT-22 (C3) | complete; two implementations of one rule (merge, §Keep/Merge) |
| P1-3 | I, C | `hooks_install.py` guard (publish-first; `inspect-hooks` dry run) | `C.hooks-break-delivery` | T-C6; `t:integration_hooks_break_delivery` | CT-02b / CT-22 | complete |
| P1-4 | G, B | `subagent_receipt.py` journal; `lane:set --from-journal`; `record_guard` lane rule | `G.disposition-vs-record`, `B.review-missing`, `B.handoff-text-contradicts-record` | T-G1, T-G2, T-B1, T-B4; `t:receipts_reviewer_disposition_vs_record` | CT-19 / CT-05 / CT-23 | complete (`record_guard` route is dropped below; the pre-commit step covers it) |
| P1-5 | H | `dev/checks/unwired_tests.py` | `H.unwired-test` | T-H1; `t:gates_unwired_test_detected` | CT-12 / CT-22 | complete; one implementation, two trees (merge) |
| P1-6 | E, N | `plan_decide approval`; `lane:allocate --ticket` refusal | `N.approval-missing`, `E.lane-ticket-unresolved` | T-E4/T-N4; `t:tickets_approval_row_clears_finding` | CT-25 / CT-30 / CT-17 | complete |
| P1-7 | D | `prompt_hook.invocation_receipt` (slash-in-paste warning); `plan_invocations --check`; `invocation_wording.py` | `D.invocation-row-unbacked`, `D.doc-wording` | T-D1, T-D2, T-D3; `t:invocations_row_typed_but_pasted` | CT-24 / CT-22 / CT-23 | complete |
| P1-8 | E, D | `plan_requests import` (rejected-command rows) | `E.request-uncaptured` | T-E1, T-E2; `t:requests_rejected_slash_command_counts_as_request` | CT-25 / CT-23 | complete; the live prevention is CT-13 (AskUserQuestion), which neither C2 nor C3 lists |
| P1-9 | E, B | `stop_gate.pending_operations`; `plan_decide receipt` | `E.operation-unreceipted` | T-E3; `t:requests_operation_without_receipt` | CT-25 / CT-22 | complete |
| P1-10 | L, H | `dev/checks/pinned_paths.py`; `lane:validate import_source.data` | `H.pinned-data-missing`, `L.cited-path-missing`; T2 `check:inputs` | T-H2, T-L3; `t:gates_pinned_evidence_missing…`; T2 `test_check_inputs.py` | CT-27 / CT-28 / CT-22 / CT-21 | **three owners of one invariant** (C2 `pinned_paths`, C3 `gates.py`, T2 `check_inputs.py`); survivor CT-21 |
| P1-11 | K | `planning_checks/{skeleton,progress_size}.py`; `plan:log` cap; `record_guard.progress_size` | `K.plan-no-phases`, `K.plan-missing-keep-section`, `K.progress-size` | T-K1, T-K2, T-K3; `t:planfiles_zero_phases_flagged` | CT-15 / CT-23 / CT-22 | complete |
| P1-12 | F | `session_start.agent_roster`; `agent_gate.lane_dispatch` rule 1; `subagent_receipt.tdd_first` | `F.agents-not-offered`, `F.lane-dispatch-generic`, `F.tdd-not-first` | T-F1, T-F3, T-F4; `t:agents_created_after_session_start_flagged`, `t:agents_tdd_skill_before_first_write` | CT-22 / CT-26 / CT-19 / CT-23 | complete |
| P1-13 | H, B | `retro_gate --unit` + `retro_record` alias; `lane:validate retro passed ⇒ gate rc 0` | `H.retro-unit-alias`, `B.retro-claim-unverified` | T-B2, T-H3; `t:gates_unit_retro_alias`, `t:lanes_retro_passed_but_gate_fails` | CT-27 / CT-05 (SYNTHESIS: CT-12) | complete; alias ownership collides three ways (CT-12 per SYNTHESIS, CT-27 per C2, runbook step 7 `git mv` makes it moot) |
| P2-1 | C | `pretooluse_gate` `--no-commit` deny (token-anchored) | `C.no-commit-merge` (sweep), `C.hooks-not-installed` | T-C2; `t:integration_no_commit_merge_from_corpus` | CT-02b / CT-23 | complete |
| P2-2 | C | `lane:integrate` foreign-hunk refusal, `--parent-hunk` | `C.foreign-hunk` | T-C5; `t:integration_foreign_hunk_detected_and_declared` | CT-17 / CT-22 | complete |
| P2-3 | J | corpus replay, `--dry-run`, `--time`, deadline deny | `J.corpus-mismatch`, `J.hook-latency`, `J.timeout-arithmetic`, `J.hook-error-observed` | T-C1, T-C7, T-J1, T-J2; `t:hookcorpus_*` | CT-02b / CT-22 | complete; the corpus fixture is proposed twice (`fixtures/prevention/` and `fixtures/doctor/`) |
| P2-4 | H, G | `retro_gate` deferral item ids `CT-nn/k` | `H.retro-deferral-unbound` | T-H4; `t:gates_deferral_row_bare_ct_id` | CT-27 / CT-22 | complete, but the `CT-nn/k` id scheme needs `build_manifests.py items[]` (CT-30) and published issues; see §Required changes 9 |
| P2-5 | G, I | `lane:validate resource_admissions.network`; `lane:allocate --admit` prep receipt | `I.lane-admission-missing` | T-G4 | CT-05 / CT-17 / CT-22 | complete |
| P2-6 | N, E | `proposals.py` (acyclic, in-set edges); `plan_decide approval` | `N.manifest-dangling-edge`, `N.manifest-cycle` | T-N1, T-N2; `t:tickets_cycle_detected` | CT-30 / CT-25 / CT-22 | **prevention-only for the semantic half**: a wrong-but-acyclic edge (CT-08←CT-02) is undetectable by a validator; the approval gate (E) is the only guard. Justified. |
| P2-7 | N, L | `proposals.py` placeholder/count/order/scratch-input rules; `build_manifests.py` refusals | `N.manifest-placeholder-parent`, `N.manifest-count-mismatch`, `N.manifest-order`, `N.builder-scratchpad-input` | T-N1, T-N3; `t:tickets_placeholder_parent_and_count` | CT-30 / CT-22 | complete |
| P2-8 | E | `stop_gate.pending_operations` | `E.operation-unreceipted` | T-E3 | CT-25 | complete |
| P2-9 | M, E | `codex_status.py` (TERMINAL state); decisions cross-check at spec time (no artifact named) | `M.activation-record-drift` (fields do not include T4 TERMINAL/budget) | T-M1–M4 cover children/automation/packet, not the TERMINAL probe | CT-29 / CT-10 | **Gap**: no artifact or test reads `TERMINAL.json` budgets into the ledger row; the "carrier" is a spec/ledger text decision (D19). Mark as operation + ledger row, detection via `M.activation-record-drift` only if `codex_status` gains a `terminal` field (change 10) |
| P2-10 | M, B | `codex_status.py` + `codex_activation.py` compare | `M.activation-record-drift` | T-M1, T-M3; `t:codexstate_failed_children_counted` | CT-29 / CT-10 | complete |
| P2-10b | D, F | `retro-writer.md` step 0 text; `/lane-retro` (CT-06) with `agent: retro-writer`; C1's "retro author role" check is **not designed** by C2 | none (`F.lane-dispatch-generic` checks dispatch type, not who authored `retros/<u>.md`) | none | CT-06 / CT-19 | **Gap**: no test and no detector for "retro record written by the implementer or parent, no `retro-writer` stop in the journal". Cheap fix: `G.journal-missing` variant `G.retro-author-not-retro-writer` (change 8) |
| P2-11 | M | `codex_status.py supersede` | `M.automation-active-unrecorded`, `M.packet-not-superseded` | T-M2, T-M4; `t:codexstate_packet_without_supersession` | CT-29 / CT-10 | complete; time-critical operation (Codex resumes 2026-10-19) is sweep B, not a lane |
| P2-12 | M, B | `codex_activation.py` requires `manifest: <path> @ <ts>` on "Inherited limitations" lines | `M.activation-record-drift` (newest manifest statuses) | T-M3 (indirect) | CT-29 / CT-10 | **thin**: no test asserts the manifest-line requirement; add one case (change 10) |
| P2-13 | K, A | smart view (CT-15), no artifact for the cache cause | `K.subagent-reinjection` (P3, sweep) | C3 `test_doctor_transcripts` re-injection count | CT-15 / CT-23 | **detection-only, justified**: cause is upstream (`prompt_id` in the pwf cache digest, unverified); the repo can only bound the frame size |
| P2-14 | B, K | `skeleton.py` Lanes-table == records; `plan:handoff --write` | `B.plan-table-vs-lanes` | T-K1 (partial), T-B6 | CT-15 / CT-22 | complete once T-K1 asserts the table projection explicitly |
| P2-15 | I, K | `session_start.pwf_probe`; `pwf_mode.py` pins | `I.pins-missing`, `K.*` injection bytes line | T-K4, T-I4 | CT-22 / CT-16 | complete; the probe is dropped below (pins check suffices) |
| P2-16 | I | `test_two_stop_hooks_compose`; `pwf_mode.py` `.mode` rule | `I.mode-gate`, `I.mode-absent` | T-I5, T-I4 | CT-02b / CT-16 | complete |
| P2-17 | B | `lane:allocate` writes `base_sha` = allocation commit, `allocated_from` = parent | `B.base-sha-off-by-one` | T-B1; `t:lanes_base_sha_off_by_one` | CT-17 / CT-05 / CT-22 | **detector predicate wrong** (see Claim 11a): as written it cannot fire. Prevention is sound. |
| P2-18 | L, C | `lane:integrate` snapshot step | `C.untracked-overwrite-risk`, `doctor --snapshot` | T-C4; `t:integration_snapshot_lists_untracked_overwrites` | CT-17 / CT-22 | complete; two snapshot writers (runner and doctor) → one function (change 5) |
| P2-19 | A, D | `prompt_hook` budget line; §Context budget rule | `A.ctx-over-checkpoint` | T-A4; `t:budget_*` | CT-22 | complete |
| P2-20 | F, C | `lane_brief --role reviewer` CODING_STANDARDS slot; `lane:validate published ⇒ worktree_removed ∨ holds`; `reviewer.md:18` fix | `C.worktree-after-publish`, `F.role-file-stale` | T-F5 (brief), `t:agents_role_file_arrives_with_existing_artifact`; **no test** for `worktree_removed/holds` | CT-19 / CT-05 / CT-22 | **Gap** for the first half of the finding: "no final `code-review` scheduled" has no artifact beyond "a plan phase" (process only; acceptable if `plan:handoff --check` lists outstanding stage steps — C1 (e) suggested it, C2 did not design it). Add T-B8 for `holds` |
| P2-21 | D, I | `seed_pin.py`; `session_start.plugin_version` | `D.seed-drift`, `D.plugin-version-drift` | T-D4; `t:invocations_seed_marker_present_and_matching` | CT-24 / CT-22 | complete (seed-hash pin deferred below; heading check kept) |
| P2-22 | G, H | `retro_gate --journal` P-n cross-check; named-check `receipt:` rule | `G.p-item-unrecorded`, `H.named-check-claim-unreceipted` | T-G3, T-H5; `t:receipts_p_items_all_in_retro` | CT-27 / CT-23 | complete; receipt rule deferred below (history would fail), P-n cross-check kept |
| P2-23 | F | `agent_gate` size cap; `lane_brief` ≤ 1.5 KB | `F.brief-oversized`, `F.lane-dispatch-generic` | T-F2, T-F5 | CT-26 / CT-19 | complete |
| P2-24 | M, B, L | `exclude_sync.py` + `dev/exclude.txt`; `codex_status` worktree census | `L.untracked-top-level`, `M.worktree-census-drift` | T-L2; `t:citations_untracked_top_level_excluded_is_clean` | CT-28 / CT-29 / CT-22 | complete |
| P2-25 | G, L | `record_guard.citations` (scratch paths); brief-template item ids; `P/codex-briefs/` rule | `L.scratchpad-citation`, `G.open-claim-dropped` | T-G5, T-L1; `t:citations_scratchpad_reference_flagged`, `t:receipts_*` | CT-23 / CT-28 / CT-10 | complete; the write-time deny is dropped below (pre-commit `check:planning` catches it) |

**Gap count: 5** rows with an incomplete chain (P2-9 no probe/test for the TERMINAL state;
P2-10b no detector/test for retro authorship; P2-12 no test; P2-17 detector predicate cannot
fire; P2-20 no test for `holds`/worktree removal and no artifact for the final `code-review`),
plus **2** justified one-sided rows (P2-6 semantic edges: prevention-only; P2-13: detection-only).
All 39 findings have at least one prevention *or* detection artifact; 34 have all three.

Duplicated ownership (one invariant, ≥ 2 implementations): P1-2 settings rule (C2
`settings_check` vs C3 `settings.py`), P1-5 unwired tests (C2 `checks/unwired_tests` vs C3
`gates.py`), P1-10 pinned data (C2, C3, T2), P1-13 alias (CT-12 / CT-27 / runbook), P2-3 corpus
(two fixture paths), P2-18 snapshot (runner vs doctor), P2-24 untracked allow-list (C2
`P/untracked.toml` vs C3 `dev/doctor/untracked-allow.json` vs C2 `dev/exclude.txt`), class K
(`planning_checks/*` vs `planfiles.py`), class N (`checks/proposals.py` vs `tickets.py`), the
threshold table (C2 `rules/common.py` 450/600/500/850 K vs C3 `budget.py` 400/600/650/800 K),
and the whole `dev/checks/` + `dev/planning_checks/` tree (C2, 12 modules) vs `dev/doctor/`
(C3, 14 modules). Resolved in §Keep/Merge/Defer/Drop.

## Claim verification table

| # | Claim (who) | Verdict | Evidence |
|---|---|---|---|
| 1 | A project `.claude/settings.json` `autoCompactEnabled: true` overrides the user file's `false` (C2 §A) | **CONFIRMED, with two caveats** | settings page: "a key at a higher level overrides the same key anywhere below it"; stack: managed > `--settings` > project local > shared project > user. settings-reference `autoCompactEnabled`: Scope "Any file", Default `true`, "Per-session overrides: `DISABLE_AUTO_COMPACT` turns auto-compact off for one session; whichever of the two turns it off, the other can't turn it back on". Caveat 1: a shell `DISABLE_AUTO_COMPACT` beats the project file. Caveat 2: `~/.claude.json` is "a fifth file … that it writes for itself" holding "global config keys"; the reference lists `autoCompactEnabled` as "Any file", **not** "Global config", so the `~/.claude.json` copy should be inert — but the pages fetched never say so (UNVERIFIABLE); C2's D-A1 (user flips both) stands. Not a trust-gated key (trust gates `permissions.allow`, `permissions.additionalDirectories`, `extraKnownMarketplaces`, most `env`). |
| 2 | `autoCompactWindow` exists as a setting (C2) | **CONFIRMED** | settings-reference: Scope "Any file", "number of tokens, from `100000` to `1000000`", default unset, `--autocompact` and `CLAUDE_CODE_AUTO_COMPACT_WINDOW` override it; `/autocompact` writes a per-model value under `modelSettings` that wins in the same file. C2's `700000` is in range. |
| 3 | A PreToolUse hook on the Agent tool can read `transcript_path` and deny a spawn (C2 §A) | **CONFIRMED** | hooks page: PreToolUse "Matches on any tool name except `EndConversation`: … `Agent` …"; Agent `tool_input` = `{prompt, description, subagent_type, model}`; `transcript_path` is a common field; deny shape `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":…}}` (also `allow|ask|defer`, `additionalContext`, `updatedInput`). Caveat: "The transcript file is written asynchronously and may lag the in-memory conversation" (one-turn lag; C3's 50 K margin is right). A **timed-out** PreToolUse hook "doesn't block the tool call" unless `onFailure: block` — so C2's in-budget deny-with-reason is the only reliable fail-closed path. |
| 4 | Hook stdin carries what C2/C3 assume per event | **CONFIRMED** (one field unverifiable) | Common: `session_id, prompt_id, transcript_path, cwd, scratchpad_dir, permission_mode, effort, hook_event_name` (+ `agent_id`, `agent_type` "when the hook fires inside a subagent"). PreToolUse/PostToolUse: `tool_name`, `tool_input`. SubagentStop: "`stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`, and `last_assistant_message`. The `agent_type` field is the value used for matcher filtering" (matcher = frontmatter `name`). Stop: `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons`. UserPromptSubmit: `prompt` (+ `session_title`). SessionStart: `source ∈ {startup, resume, clear, compact, fork}`; on `resume|fork`: `context_tokens`, `seconds_since_last_response`, …. UNVERIFIABLE: the `agent_type` value a *fork's* hooks receive (C2 treats `fork`/`source: fork` as equivalent; the fork `.meta.json` says `agentType: fork`). |
| 5 | SessionStart `additionalContext` / plain stdout reaches the model (C2, C3) | **CONFIRMED** | hooks page: "The exceptions are `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch`, where Claude Code adds plain-text stdout as context"; `hookSpecificOutput.additionalContext` accepted on SessionStart; `CLAUDE_ENV_FILE` for `export` lines. Field evidence: `T:L6` carries the pwf SessionStart `additionalContext` (C3). |
| 6 | An `agents/` directory created mid-session is not picked up until restart (C2 §L, C3 F) | **CONFIRMED verbatim** | sub-agents page: "The watcher covers only directories that existed when the session started, so after creating a scope's first agent file in a new `agents` directory, restart to load it." Also: `isolation: worktree` branches "by default from your default branch rather than the parent session's `HEAD`" (R7/R8 guardrail confirmed); hooks "receive this value [`name`] as `agent_type`"; "A fork can't spawn further forks." |
| 7 | hk `pre-commit` steps run through the user's global hk install without `hooks:install` (C2 principle 2) | **CONFIRMED** (two caveats) | `git config --global`: `hook.hk-pre-commit.command = test "${HK:-1}" = "0" \|\| ~/.local/bin/mise x hk -- hk run pre-commit --from-hook --staged`, `.event = pre-commit` (+ `commit-msg`, `pre-push`); `hk install --help`: "In a project without an `hk.pkl`, the installed hook exits silently"; `e12cf04:hk.pkl` defines only `pre-merge-commit` and `pre-push`, so today the global `pre-commit` is a no-op and defining `["pre-commit"]` arms it. Caveats: (a) it then fires on **every commit in every worktree** (lane implementers included) through `mise x hk` (≈0.25 s mise start + the step); (b) `hk run` evaluates `amends "package://github.com/jdx/hk/releases/download/v2.5.0/…"`, which needs the pkl package cache (offline behaviour UNVERIFIABLE here); (c) `HK=0` or `git commit --no-verify` bypasses it, so it is a guard, not a gate. |
| 8 | The A09 `delivery:publish` safe set and what it rejects (C2 §C/§I, C3 C) | **CONFIRMED** | `dev/git_delivery.py:49-71` `safe_configured_hooks`: every `hook.<name>.{event,command}` pair from `git config --null --get-regexp '^hook\.'` (**all scopes**, global included) must have exactly those two fields, `event ∈ {pre-commit, commit-msg, pre-push}` and a non-empty command; anything else raises `Refusal("configured Git hook could execute during delivery")` or "unsupported configured Git hook". `hook_tree_digest` also folds the raw config bytes into `hook_tree_sha256`, so any new `hook.*` entry changes the intent digest ("Git hook preimage drift"). Today's three global entries pass. `hooks:install` = `hk install --force-local` + `git config --local merge.ff false` (mise tasks info); on Git 2.54 `--force-local` "uses config-based hooks (`hook.<name>.command`)" for each hook in `hk.pkl`, hence a local `hook.hk-pre-merge-commit.event = pre-merge-commit` → refused. P1-3 stands. Adding a `["pre-commit"]` hook to `hk.pkl` writes **no** git config, so the digest is unchanged. |
| 9 | `python3 -I` stdlib-only is enforceable in `check.py` (C2 preamble) | **PARTLY WRONG as phrased, enforceable by another route** | `-I` = `-E -s -P`: ignores `PYTHON*` env, user site-packages and the script directory; the interpreter's own `site-packages` stay importable, so `-I` does not prove stdlib-only. Enforceable in ≈30 lines as a rule: AST-scan `dev/**/*.py` imports against `sys.stdlib_module_names` (3.10+; `check.py` already requires 3.11) with an allow-list for repo-local modules (`git_gate`, `runtime_preflight`, …). `check.py` today only `compile()`s each file. |
| 10 | `usage` sums, not `<total_tokens>` attachments, are the context source (C3 A; C1) | **CONFIRMED** | Transcript probe: 120 `total_tokens` attachments, all of type `total_tokens_reminder` with text `<total_tokens>15000000 tokens left</total_tokens>`-shaped at `T:L29` while ctx was ≈53 K; the dying fork saw 14,025,109 "left" at ctx 974 K (C3). Last non-zero assistant `usage` is `T:L2032`: `input 2 + cache_creation 3,077 + cache_read 974,014` = **977,093**, which is C1's death ctx. The statusline (not hooks) gets `context_window.{total_input_tokens, context_window_size, used_percentage, remaining_percentage, current_usage}` and `exceeds_200k_tokens` (statusline page), debounced 300 ms. |
| 11a | Git plumbing (C3 B): "`base_sha` equals the parent of the lane's first own commit: `git rev-list --reverse --first-parent <base_sha>..<branch> \| head -1` has parent `base_sha`" | **WRONG (vacuous)** | Run on the real lane: `git rev-list --reverse --first-parent e618243..claude/gate-hooks-wiring \| head -1` = `2d1f60e` (`docs: allocate lane gate-hooks (CT-02)`), whose parent is `e618243` — i.e. the recorded `base_sha`. The first commit of `<X>..<branch>` on the first-parent line always has parent `X`, so `B.base-sha-off-by-one` can never fire and `t:lanes_base_sha_off_by_one` would pass for the wrong reason. Correct derivation: the allocation commit is the one that **added** `lanes/<unit>.json` (`git log --diff-filter=A --format=%H -- P/lanes/<unit>.json`, or the first-parent commit whose subject is `docs: allocate lane <unit>`); `base_sha` must equal it, `allocated_from` its parent. |
| 11b | `git merge-base --is-ancestor <lane-tip> HEAD` decides "integrated" (C3 B, C) | **CONFIRMED** | `claude/gate-hooks-wiring` vs `HEAD` → rc 1 (not yet merged); `e12cf04` vs `MERGE_HEAD` → rc 0. |
| 11c | The integration merge is the first-parent merge whose second parent is the lane tip (C3 B) | **CONFIRMED** | `git log --first-parent --merges --format='%h %p'`: `fa892d2`→`6840342` = `claude/nav-guidance-hierarchy`; `4c1ea6b`→`6c09b7f` = `claude/c1-catalog-promotion`; `e618243`→`82c351f` = `claude/retro-gate-task`; `7e22d13`→`ea8c8c9` = `claude/team-roles-rules`; `447110a`→`281a198` = `claude/rf-env-scrub-inherited-selectors`; `55f3946`→`ea893a8` = `claude/codex-session-history-skill`; `361688e`→`93402c0` = `claude/a06-unit3-classification-methods`. 7 of 7. |
| 12 | `onFailure: block` is meaningful on Stop/SubagentStop (C2 §I invariant: "`onFailure: block` only on PreToolUse/Stop/SubagentStop"; the staged settings carry it there) | **WRONG for Stop/SubagentStop** (harmless) | hooks page: "The field has no effect on these hooks: `Stop`, `SubagentStop`, `TaskCompleted`, and `TeammateIdle`". `onFailure: block` "Requires Claude Code v2.1.295 or later"; failure = failed start, exit ≠ 0/2, timeout, invalid output. C3 states this correctly. The invariant text and the settings snippet should drop it on those two events. |
| 13 | Stop blocks are capped at 8 consecutive continuations (C2) | **CONFIRMED** | "after stop hooks have continued the turn eight times in a row, Claude Code overrides the next block and ends the turn … To raise the cap, set `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`." |
| 14 | Hooks defined in several settings files merge; matching hooks run in parallel (C2, C3) | **CONFIRMED** | settings-reference `hooks`: "Hooks merge across files rather than replacing each other"; hooks page: "All matching hooks run in parallel", "If you define the same handler in more than one settings file, it runs once. A plugin's or skill's copy of the same handler stays separate." So the per-event wall time is the slowest matching hook, not the sum. |
| 15 | Default command-hook timeout 600 s, 30 s on UserPromptSubmit (C3) | **CONFIRMED** | hooks page timeout section. |
| 16 | PostToolUse can match `Skill` (C2 §D) | **CONFIRMED** | "a `PreToolUse` hook matching the `Skill` tool fires only when Claude calls the tool"; PostToolUse "Matches on tool name, same values as PreToolUse". |
| 17 | `env` in settings reaches hook subprocesses (C2 §K, "unverified") | **CONFIRMED for subprocesses, not stated for hooks** | settings-reference index: `env` "Set environment variables for every session and its subprocesses" (Any file); project/local files cannot set `CLAUDE_CONFIG_DIR`, `HOME`, `TMPDIR`, telemetry exporters, `CLAUDE_CODE_PROCESS_WRAPPER`, … (none of ours). Hooks are subprocesses; the `CLAUDE_ENV_FILE` belt-and-braces route stays reasonable. |
| 18 | Top-level `additionalDirectories` is undocumented (R5, C2) | **CONFIRMED** | settings-reference lists only `permissions.additionalDirectories` ("nested key under `permissions`"). |
| 19 | The PreToolUse false positive and its latency (R7 O, P2-3) | **Segmentation CONFIRMED by code; timeout cause still unreproduced** | `pretooluse_gate.py:23` `SEGMENT` includes `\n`, so a heredoc line `git merge x` is an action; the staged gate on this checkout: benign `ls` 42 ms; heredoc containing `git merge x`/`git push y` → gate ran, **no deny today** (the gate-hooks retro passes, rc 0), so the R7 block needed a failing lane or a timeout; real `git merge --no-ff claude/gate-hooks-wiring` with `MERGE_HEAD` set 676 ms; `git push origin HEAD` 348 ms; `stop_gate.py` 201 ms (prints nothing today); `retro_gate.py --unit gate-hooks` 196 ms; `--unit a06-unit3` 193 ms, rc 2 "retro record missing" (P1-13 reproduced). `python3 -I` start 27 ms; `git rev-parse` 168 ms on this 27-worktree checkout; `./dev/mise tasks ls` 233 ms. |

Wrong or vacuous claims: **3** (11a, 12, 9-as-phrased); unverifiable: 3 (claim 1's `~/.claude.json`
participation, claim 4's fork `agent_type`, claim 7's offline pkl cache).

## Keep / Merge / Defer / Drop

Rule: KEEP = prevents or detects a finding that occurred and has a named test; MERGE = duplicate of
an R7/C2/C3/T2 sibling (survivor named); DEFER = no occurred finding, or depends on an undecided
scheme; DROP = wrong, harmful, or latency on every tool call without a matching occurred finding.
"Size" = LOC / tests / Opus-implementer hours (tests included), estimates.

| Artifact (origin) | Class | Verdict | Survivor / reason | Size |
|---|---|---|---|---|
| `.claude/settings.json` composition (R5 §B) + `autoCompactEnabled`, `autoCompactWindow`, `env.PLAN_ID` (C2) | A, I, K | **KEEP** (wave 0) | P1-2, P1-1, P1-11; runbook step 2 + 9 | 0 / 1 (T-I1) / 0.5 h |
| `dev/context_budget.py` (C2) | A | **KEEP** (wave 0) | P1-1; T-A1, T-A3; thresholds in one dict shared with C3 `budget.py` | 60 / 3 / 1 h |
| `dev/hooks/agent_gate.py` `fork_budget` + `lane_dispatch` rule 1 (C2) | A, F | **KEEP** (wave 0) | P1-1, P1-12; T-A2, T-F1 | 70 / 4 / 1.5 h |
| `agent_gate` rules 2–4: fallback marker, size cap, roster drift (C2 CT-26) | F | **MERGE** size cap into CT-19 (`lane_brief` already caps at 1.5 KB, the hook asserts it, 5 lines); **DEFER** fallback marker and roster-drift context (no finding needs them once rule 1 and the SessionStart roster line exist) | CT-19 | 15 / 1 / 0.3 h |
| `dev/hooks/prompt_hook.py` ctx line + slash-in-paste warning (C2) | A, D | **KEEP** (wave 0); **MERGE** C3's UserPromptSubmit `prompt` surface into it (one UserPromptSubmit script) | P2-19, P1-7; T-A4, T-D1 | 50 / 3 / 1 h |
| `prompt_hook` `request_capture` journal + `plan_requests.py import/cite/decline/check` (C2 CT-25) | E | **DEFER** | P1-8's live prevention is CT-13 (AskUserQuestion) plus the decisions ledger; the audit side is C3 `E.request-uncaptured` in session-review (CT-20). A per-prompt journal of user text duplicates the transcript. | — |
| `dev/plan_decide.py` + `P/decisions.jsonl` (approval / operation / receipt) (C2 CT-25) | E, N | **KEEP** (wave 0 seed, wave 1 CLI) | P1-6, P1-9, P2-8; T-E3, T-E4, T-E5 | 80 / 4 / 1.5 h |
| `stop_gate` `pending_operations` block (C2) | E | **MERGE** into the SessionStart block as a line (C3 `E.operation-unreceipted`); no Stop block | a Stop block costs a continuation turn per stop until the receipt exists; the SessionStart line is enough for "on your word" operations | — |
| `dev/hooks/session_start.py` (`autocompact`, `agent_roster`, `merge_state`, exclude drift, `CLAUDE_ENV_FILE` pins) (C2) | A, F, C, L | **MERGE** into `dev/doctor/cli.py --surface session-start` (C3), built as the wave-0 slice ("CT-22a") | C3 already says: "If C2 also proposes a SessionStart hook … it is the same artifact … built once, in `dev/doctor/`". The three C2 lines become detectors `A.autocompact-off`, `F.agents-not-offered` (mtime form), `C.merge-in-progress` | 200 / 8 / 4 h (incl. `cli.py`, `core.py`, `integration.py`, `lanes.py` minimal, `settings.py`) |
| `session_start` `pwf_probe` (runs `inject-plan.py` at start) (C2) | K | **DEFER** | P2-15's guard is `PWF_TRUSTED_PYTHON` pinned (`I.pins-missing`) and the `claude-hook.sh` fast path (42 ms); re-running the injector at SessionStart adds work to the slowest event | — |
| `session_start` `codex_status` line (C2, 2 s budget) | M | **MERGE** into C3 `M.*` stat-only line (< 50 ms, no sqlite at start) | C3 | — |
| `dev/settings_check.py` (C2 CT-16) vs `dev/doctor/settings.py` (C3) | I | **MERGE**: one implementation in `dev/doctor/settings.py`; `settings_check.py` is at most a 10-line CLI alias; CT-16 owns it | P1-2; T-I1, T-I2 | 80 / 5 / 1.5 h |
| hk `["pre-commit"]` step `records` → `check:records` (C2) ≡ C3 `doctor-settings` ≡ T2 `cited-inputs` | B, I, L | **MERGE**: one `["pre-commit"]` hook (parent-owned `hk.pkl`), steps added as declared parent hunks: `records` = `doctor --surface pre-commit` (I.* + `lane:validate --staged`), `cited-inputs` = `check:inputs` (CT-21) | wave 0 for the hook + settings rule; the lane-record rule only after the records are corrected (runbook 7) | 10 / 1 (T-B5) / 0.5 h |
| `dev/hooks/record_guard.py` PreToolUse `Write\|Edit` (lane JSON, settings schema, progress size, citations) (C2 CT-23) | B, I, K, L | **DROP** | The writes that caused P1-4/P1-13/P2-17 went through Bash heredocs (`cat >`), which this hook never sees (C2 admits it); the pre-commit `records` step and `check:planning` catch both routes. It would add a python start (~50 ms) to every Write/Edit on top of the pwf PreToolUse hook, for no occurred finding it uniquely catches. CT-23 (C2) disappears. | — |
| `dev/hooks/post_tool.py` PostToolUse `Skill` journal + `plan_invocations.py --write` (C2 CT-24) | D | **DROP** journal; **MERGE** `--check` into C3 `D.invocation-row-unbacked` (reads `Skill` tool_use from the transcript directly) | the transcript already records every `Skill` call; a second journal is redundant | — |
| `dev/planning_checks/invocation_wording.py` (C2) ≡ C3 `D.doc-wording` | D | **MERGE** into doctor | P1-7; T-D2 | 20 / 2 / 0.3 h |
| `dev/planning_checks/seed_pin.py` (C2) ≡ C3 `D.seed-drift` | D | **KEEP heading check**, **DEFER hash pin** | P2-21: the required-heading list catches the observed drift; hashing the plugin cache path couples the repo to a host path | 30 / 2 / 0.5 h |
| `pretooluse_gate.py` token-anchored parsing, `--no-commit` deny, `--dry-run`, `--time`, deadline deny (C2, R7 O) | C, J | **KEEP** (CT-02b, wave 1 #1) | P2-1, P2-3; T-C1, T-C2, T-C7, T-J1, T-J2 | 120 / 8 / 3 h |
| corpus fixture (113 real commands) (C2 `fixtures/prevention/bash-corpus.jsonl`; C3 `fixtures/doctor/bash-corpus.jsonl`) | J | **MERGE**: one file `dev/fixtures/hooks/bash-corpus.jsonl`, owned by CT-02b, extracted by the parent in wave 0 | — | data / 0 / 1.5 h (labelling) |
| `dev/doctor/hookcorpus.py` (C3) | J | **DROP** as a `check` detector; keep `J.timeout-arithmetic` (10 lines) in `settings.py` | the corpus replay is CT-02b's unit test (`test_hooks.py`); running it again inside `check` duplicates it | — |
| `dev/hooks_install.py` guard (C2) | I, C | **KEEP** (CT-02b) | P1-3; T-C6 | 60 / 3 / 1.5 h |
| `dev/lane.py set\|validate` (R7 A, CT-05) | B | **KEEP** (wave 1) | P1-4, P1-13, P2-17; T-B1–B3, T-B7, T-G2, T-G4 | 250 / 8 / 5 h |
| `dev/doctor/lanes.py` (C3 B) | B | **KEEP, fix predicate** (Claim 11a); CT-05 imports its predicates (C3 already says so) | one schema, two callers (refusal in `lane:validate`, report in doctor) | 150 / 6 / 3 h |
| `dev/lane.py allocate\|integrate\|status` + journal + snapshot + `--continue/--abort` (R7 B/C/J, C2 CT-17) | C, B | **KEEP** (wave 2) | P1-1, P2-2, P2-17, P2-18; T-C3–C5 | 350 / 10 / 8 h (split per R7) |
| `merge-tree --write-tree` composition and temporary-worktree gates inside `lane:integrate` (C2 §C) | C | **DEFER** | R7 C's shape (runner merges `--no-commit`, gates in-task, journal step, `--continue`) covers P1-1; the PreToolUse `--no-commit` deny targets ad-hoc Bash, and the runner's own `git` subprocess is not a Bash tool call, so no conflict. `merge-tree` + a temp worktree is a second integration engine with untested gate equivalence (C2 "Could not verify"). | — |
| `doctor --snapshot` (C3) vs runner snapshot step (C2) | C, L | **MERGE**: one function in `dev/doctor/integration.py` that the runner calls | P2-18 | 40 / 2 / 1 h |
| `stop_gate.py` + `lane.validate()` first-three-failures + `merge_state` (C2) | B, C | **KEEP**, land with CT-17 (wave 2), after every record validates (see §Repair-session safety); one combined reason per Stop | P1-1, P1-4; T-C3 | 30 / 2 / 0.5 h |
| `dev/hooks/subagent_receipt.py` journal (R7 L, CT-19) | G | **KEEP** (wave 2) | P1-4, P2-22; T-G1 | 80 / 3 / 2 h |
| `subagent_receipt` `tdd_first` SubagentStop **block** (C2) | F | **DEFER the block; KEEP the detector** (`F.tdd-not-first`, session-review) | blocking after the code is written does not prevent; the `skills:` preload leaves no `Skill` tool_use, so the scan is fragile (C2 relies on an unverified "preload marker") | — |
| `dev/lane_brief.py` + agent constants + `reviewer.md:18` fix + `retro-writer.md` step 0 (R7 E, CT-19) | F | **KEEP** | P1-12, P2-20, P2-23, P2-10b; T-F5 | 150 / 4 / 3 h |
| `dev/plan_records.py` `plan:log`, `plan:handoff --write/--check` (R7 F, CT-15) | K, B | **KEEP** (wave 1) | P1-11, P2-14, P1-1 handoff; T-B6, T-K3 | 200 / 6 / 4 h |
| `dev/planning_checks/{skeleton,progress_size,pwf_mode}.py` (C2) ≡ `dev/doctor/planfiles.py` + `I.mode-*`/`I.pins-missing` (C3) | K, I | **MERGE** into doctor; `check:planning` (CT-15) calls `doctor --class K,I,D,E,N,L --surface check` (C3's wiring) | P1-11, P2-15, P2-16; T-K1, T-I4 | 120 / 5 / 2 h |
| `K.worktree-stale-plan` nonce probe (C3) | K | **DEFER** | P1-11's pin fix is the prevention; the probe spawns the injector per worktree (≤ 8 × 42 ms) for a state the pin makes impossible; keep as session-review only | — |
| `dev/checks/unwired_tests.py` (C2, CT-12) ≡ `dev/doctor/gates.py:unwired_tests()` (C3) | H | **MERGE**: one implementation in `dev/doctor/gates.py`; CT-12 wires `test:retro-gate` and owns `exemptions` data | P1-5; T-H1 | 60 / 3 / 1.5 h |
| `dev/checks/pinned_paths.py` (C2 CT-27) ≡ `H.pinned-data-missing` (C3) ≡ `dev/check_inputs.py` + `dev/cited-inputs.json` (T2 CT-21) | L, H | **MERGE** into CT-21's `check_inputs.py` (the only one with the data plan and the mirror declaration); doctor `H.pinned-data-*` calls it (C3 already plans this) | P1-10; T2 `test_check_inputs.py`, T-H2 as a CT-21 case | in CT-21 |
| `--fix H.pinned-data-missing --from-snapshot` and `--fix L.cited-path-missing` copiers (C3) | H, L | **DROP** | CT-21 copies the 119 files by plan with hash verification; a second copier in the doctor duplicates the lane and can race it | — |
| `retro_gate.py` `retro_record` alias (SYNTHESIS CT-12 / C2 CT-27) | H | **DROP** | runbook step 7 renames `retros/a06-classification-methods.md` → `retros/a06-unit3.md`; afterwards `lane:validate` requires `unit == retro file name` and `H.retro-unit-alias` detects a recurrence. No `retro_gate.py` edit, no CT-11 collision. | — |
| `retro_gate.py` deferral item ids `CT-nn/k` + `build_manifests.py items[]` (C2 CT-27/CT-30) | H, N | **DEFER** until tickets are published; interim rule: a deferral row cites `#<issue>` present in `P/ticket-ledger.json` (`H.retro-deferral-unbound`, C3) | P2-4 | 25 / 2 / 0.5 h |
| `retro_gate.py` named-check `receipt:` rule + `JOURNAL/checks/` receipts (C2 CT-27, CT-11) | H | **DEFER** | P2-22 occurred, but the rule fails every existing retro (C2 admits a history-correction commit) and makes the retro-writer's claims depend on a receipt format nobody has specified; the P-n cross-check (next row) catches the observed loss | — |
| `retro_gate --journal` P-n cross-check (C2) ≡ `G.p-item-unrecorded` (C3, integrate surface) | G | **MERGE** into doctor `receipts.py` run at `lane:integrate` preflight; no `retro_gate.py` edit | P2-22; T-G3 | 40 / 2 / 1 h |
| `dev/exclude_sync.py` + `dev/exclude.txt` (C2 CT-28) vs `L.untracked-top-level --fix` (C3) vs `P/untracked.toml` (C2) vs `dev/doctor/untracked-allow.json` (C3) | L | **MERGE**: `dev/exclude.txt` is the one allow-list; `exclude_sync --check/--write` lives in `dev/doctor/citations.py` as the `L.untracked-top-level` fix; drop `P/untracked.toml` and `untracked-allow.json` | P2-24; T-L2 | 50 / 3 / 1 h |
| `L.scratchpad-citation`, `L.external-citation-unhashed` (C3) ≡ `planning_checks/citations.py` (C2) | L | **MERGE** into doctor | P2-25; T-L1 | 40 / 2 / 1 h |
| `codex_status.py` (+ `supersede`) + `codex_activation.py` (C2 CT-29) ≡ `dev/doctor/codexstate.py` + CT-10 `codex:status --write` (C3) | M | **MERGE** into CT-10 (R7 N and C3 route it there); `codexstate.py` stays the thin caller in CT-22 | P2-9…P2-12, P2-24; T-M1–M4 | 200 / 6 / 4 h (in CT-10) |
| `dev/checks/proposals.py` + `build_manifests.py` refusals (C2 CT-30) ≡ `dev/doctor/tickets.py` (C3) | N | **MERGE** into doctor `tickets.py`; builder refusals stay runbook step 11 edits | P2-6, P2-7; T-N1–N3 | 70 / 4 / 1.5 h |
| `lane:allocate --ticket` approval refusal (C2 CT-30/CT-17) ≡ `tickets.py:resolve_ticket()` (C3) | N, E | **KEEP** in CT-17, importing from doctor | P1-6; T-E4 | 20 / 1 / 0.5 h |
| `dev/doctor/{cli,core}.py`, finding shape, surfaces, budgets, `last-<surface>.json` (C3) | all | **KEEP** (CT-22) | the one tree every static rule lives in | 180 / 4 / 3 h |
| `dev/doctor/integration.py` (C3 C) | C | **KEEP** (wave 0 slice) | P1-1, P1-3, P2-2, P2-18 | 120 / 6 / 2.5 h |
| `dev/doctor/agents.py` static part (C3 F) | F | **KEEP** | P1-12 (mtime form), P2-20 (`F.role-file-stale`) | 60 / 3 / 1 h |
| `dev/doctor/invocations.py`, `requests.py` static parts (C3 D, E) | D, E | **KEEP** | P1-7, P1-9, P1-6 | 80 / 5 / 1.5 h |
| `dev/doctor/budget.py` (C3 A) | A | **KEEP**; thresholds dict is the single source for `context_budget.py` | P1-1, P2-19 | 60 / 4 / 1 h |
| C3 UserPromptSubmit `prompt` surface: state digest (`git write-tree` on a temp index, lanes hash) and re-run of the session-start set when changed, 1.5 s budget | — | **DROP** | up to 1.5 s on **every** user prompt for no occurred finding (state drift between prompts is what the Stop gate and `lane:integrate` cover); keep only the ctx bucket line (merged into `prompt_hook.py`) | — |
| C3 `pre-push` hk step `doctor --surface pre-push` | B, C, I | **DEFER** | A09 pushes with `--no-verify` (`git_delivery.py` comment), so hk `pre-push` never guards the publish route; manual pushes are already gated by PreToolUse. `delivery:publish-batch` (CT-18) runs `doctor --surface publish` instead | — |
| C3 `--fix I.settings-non-project-key --backup` (lossless split) | I | **DROP** | one-time repair done by hand in runbook step 2; a 60-line fixer for an operation that never recurs once the pre-commit rule exists | — |
| C3 `--fix` for `B.status-stale` (published/integration_merge), `B.handoff-base-stale`, `I.settings-local-not-excluded`, `I.mode-absent`, `L.untracked-top-level`, `G.journal-vs-record` | B, I, L, G | **KEEP** (proven-by-git facts only) | P3 records drift, P1-4 | 100 / 6 / 2 h |
| `agent-session-history` skill + `claude_session_digest.py` + `claude_subagents.py` + `session_review.py` (R7 M = CT-20; C3 CT-23 "doctor sweep") | A, C, D, E, F, G, J, K | **MERGE** C3's CT-23 into CT-20 (one skill, wave 4); `doctor --surface sweep` calls `session_review.py` | the sweep detectors are the digester; two tickets for one script set | 600 / 12 / 10 h (CT-20) |
| C3 daily sweep schedule via host scheduler | — | **DEFER** | AGENTS.md: daemon registration waits for instruction; the SessionStart previous-session line covers the need | — |
| `P/codex-briefs/` tracked + brief-template item ids (C2 §G) | G, L | **DEFER** to CT-10 (wave 4) | P2-25 occurred, but the fix is a brief-template convention; no code | — |
| `mise/tasks/<unit>.toml` includes (R8 0.3) | — | **KEEP, conditional on D7** (`task_config.includes` validates under `./dev/mise`; unverified by every report) | — | — |
| `ctx:status`, `test:hooks-session`, `check:records`, `doctor`, `doctor:session-start`, `test:doctor` tasks | — | **KEEP** (each new test file must be wired or P1-5 recurs; `test:hooks-session` and `test:doctor` join `check:research` depends as parent hunks) | — | — |
| docs: `--no-commit` forbidden, D15 wording, §Context budget, §Roles restart, §Hooks (two Stop hooks), secrets posture (N1) | C, D, A, F, I | **KEEP** (wave 0, parent) | — | 0 / 0 / 1 h |

Counts over the 56 rows above: **KEEP 29, MERGE 16, DEFER 10, DROP 8** (a row with two verdicts is
counted under the first). Net effect: C2's 9 hook scripts become **5** (`pretooluse_gate`,
`agent_gate`, `prompt_hook`, `stop_gate`, `subagent_stop_gate` + the `subagent_receipt` sibling and
the doctor SessionStart command = 7 commands, 2 fewer than C2, 1 fewer event than C2+C3); C2's two
rule trees (`dev/checks/`, `dev/planning_checks/`, 12 modules) and C3's `dev/doctor/` (14 modules)
become one tree of **11** doctor modules (`cli, core, budget, lanes, integration, settings,
gates, citations, tickets, planfiles, agents, invocations, requests, receipts, codexstate` minus
`hookcorpus`, with `invocations`+`requests` and `agents` small); 9 + 2 new tickets become **3**.

## Minimal wave-0 set

What must exist before the first wave-1 integration (after runbook steps 1–8; each item test-first,
≤ 80 handwritten lines per file, declared in the wave-0 retro row):

| # | Item | Prevents / detects | Files | LOC / tests / h |
|---|---|---|---|---|
| W0-1 | Settings composition (R5 §B) already done in runbook step 2; add `autoCompactEnabled: true`, `autoCompactWindow: 700000`, `env.PLAN_ID` in step 9's commit; assertion in step 2 admits the three keys | P1-2, P1-1, P1-11 | `.claude/settings.json`, `.claude/settings.local.json` (pins, untracked) | 0 / 1 / 0.5 |
| W0-2 | Fixtures extracted by the parent: usage-curve transcript slice (6 lines, last all-zero), rejected-command shape (`T:L565-566`), staged `gate-hooks.json`, staged settings bytes, the 113-command corpus with `expect` labels | T-A1, T-E1, T-B1, T-I1, T-C1 | `dev/fixtures/hooks/`, `dev/fixtures/doctor/` | data / 0 / 1.5 |
| W0-3 | `dev/context_budget.py` + `dev/hooks/agent_gate.py` (`fork_budget`, `lane_dispatch` rule 1) + `dev/hooks/prompt_hook.py` (ctx line, slash-in-paste) + tests; settings entries PreToolUse `Agent`, UserPromptSubmit; `test:hooks-session` task wired into `check:research` depends | P1-1, P1-12, P2-19, P1-7 | as named, `dev/test_{context_budget,agent_gate,prompt_hook}.py`, `mise.dev.toml` (3 rows) | 180 / 10 / 3.5 |
| W0-4 | Doctor slice CT-22a: `dev/doctor/{cli,core,integration,settings,lanes(minimal: status-stale, review-missing, retro-claim, base_sha via allocation commit),agents(mtime roster)}.py`, `--surface session-start\|check\|pre-commit`, `--format context`; settings entry SessionStart (timeout 15, no `onFailure`); `dev/check.py` gains one line running `doctor --surface check`; `doctor:session-start`, `test:doctor` tasks | P1-1, P1-2, P1-3, P1-4, P1-12, P1-13, P2-2, P2-17, P2-18 | `dev/doctor/**`, `dev/test_doctor.py`, `dev/check.py` (1 line), `mise.dev.toml` (3 rows), `.claude/settings.json` (1 entry) | 350 / 14 / 6 |
| W0-5 | `hk.pkl` `["pre-commit"] { stash = "none"; steps { ["records"] { check = "./dev/mise run check:records" } } }` with `check:records` = `doctor --surface pre-commit` (settings rule only until runbook step 7 corrects every record, then `lane:validate --staged` joins in CT-05) | P1-2 at commit time | `hk.pkl`, `mise.dev.toml` (1 row), T-B5 (skipped without hk) | 10 / 1 / 0.5 |
| W0-6 | `P/decisions.jsonl` seeded (#91 relabel, draft PR, T4 Phase C budget, to-tickets approval pending) + `dev/plan_decide.py` minimal (`approval`, `operation`, `receipt`) | P1-6, P1-9, P2-8 | `P/decisions.jsonl`, `dev/plan_decide.py`, `dev/test_plan_decide.py` | 80 / 4 / 1.5 |
| W0-7 | Docs: `claude-team.md` §Integration ("`--no-ff`, never `--no-commit`"), §Context budget, §Roles (restart rule), §Hooks (both Stop hooks; `.mode` never `gate`); D15 rewrites; `.claude/AGENTS.md` key-list pointer; `.agent/` + the backup path in `.git/info/exclude`; secrets posture line (N1) | C, A, F, I, D, L | `docs/agents/*.md`, `.claude/AGENTS.md`, `.git/info/exclude` | 0 / 0 / 1 |

Total ≈ **620 LOC, 30 tests, ≈ 14.5 Opus hours** (C2 estimated the whole programme at 1,382
design lines / 66 tests; this wave-0 set is the part that must precede the next integration).
Everything else lands by lane in waves 1–4.

## Reconciled ticket table

Numbering rule: CT-01…CT-21 keep SYNTHESIS §6 / T2 meanings; the C2/C3 collision on CT-22/CT-23
is resolved by giving **CT-22 to the doctor** (the larger lane; C2's CT-22 is mostly wave-0 parent
work) and **CT-23 to the session hooks follow-up** (C2's CT-22 remainder + CT-26); C2's CT-25
(trimmed to the decisions ledger) becomes **CT-24**. C2's CT-23 (record guard), CT-24 (invocation
receipts), CT-27, CT-28, CT-29, CT-30 and C3's CT-23 are absorbed as shown. Final range
**CT-01…CT-24** (plus CT-02b).

| Ticket | Title | Source | Blocked by | Wave | `owned_paths` (allowlist; records/retro/log per unit implied) | Notes |
|---|---|---|---|---|---|---|
| CT-01 | Retro gate task | R2 | — | done | — | integrated, published; AC2 open → CT-12 |
| CT-02 | Hook wiring for the retro gate | R2 | CT-01 | runbook 1 | — | mid-merge; Runbook 1 |
| CT-02b | Gate follow-up: token-anchored verbs, heredoc strip, `--no-commit` deny, `--dry-run`/`--time`, deadline deny-with-reason, corpus test, `hooks_install.py` guard (publish-first, `inspect-hooks` dry run), `test_two_stop_hooks_compose` | R7 O, R5 P1-2, C2 §C/§J/§I | CT-02 | 1 #1 | `dev/hooks/pretooluse_gate.py`, `dev/hooks/git_gate.py`, `dev/test_hooks.py`, `dev/hooks_install.py`, `dev/test_hooks_install.py`, `dev/git_delivery.py` (`safe_configured_hooks` only), `dev/test_git_delivery.py`, `dev/fixtures/hooks/**`, `mise/tasks/ct02b.toml` | parent hunk: `hooks:install` row in `mise.dev.toml` |
| CT-03 | Team roles, rules, vocabulary | R2 | — | done | — | |
| CT-04 | Guidance hierarchy | R2 | — | done | — | |
| CT-05 | Lane-record validator (`lane:set`/`lane:validate --staged --from-journal`, `retro` derived, `resource_admissions.network`, `import_source.data`, `published ⇒ on origin`, `holds`), ticket ledger generator | R2, R7 A/G, C2 §B/§G/§L | — | 1 #3 | `dev/lane.py` (`set`, `validate`), `dev/test_lane.py`, `dev/ledger.py`, `dev/test_ledger.py`, `dev/fixtures/lanes/`, `dev/fixtures/ledger/`, `mise/tasks/ct05.toml`, `.claude/rules/planning-records.md`, `P/ticket-ledger.json` | imports `dev/doctor/lanes.py` predicates (CT-22a lands in wave 0); `check:records` gains `lane:validate --staged` as a parent hunk |
| CT-06 | `/lane-retro <unit>` | R2, R7 K | CT-01, CT-03, CT-19 | 3 | `.claude/skills/lane-retro/**`, `.agents/skills/lane-retro/**`, `dev/test_lane_retro_skill.py` | |
| CT-07 | Codex compatibility (roles/config; mirror test) | R2 | CT-02, CT-03 | 3 | `.codex/**`, `dev/test_skill_mirror.py`, `docs/agents/claude-team.md` (Codex section) | |
| CT-08 | Baseline transition v2 (`.gitignore`; `.agent/` decision) | R2 | user admission (D6) | 4 | `.gitignore`, `evidence/onboarding/baseline-files.v2.json`, `dev/check.py` | **touches a frozen baseline file** (`.gitignore`); alone on `dev/check.py` in its wave |
| CT-09 | Tool adoption decision table | R2 | — | 3 | `docs/agents/tool-evaluation.md` | doc-writer |
| CT-10 | codex-session-history coverage + eval loop + mask + **`codex_status.py` (`codex:status --write`, `codex:supersede`) + brief composer** | R2, R7 N, C2 §M (was CT-29), C3 M | — | 4 (the supersession **operation** is sweep B, before 2026-10-19) | both skill subtrees, `dev/test_codex_session_history.py`, `dev/test_codex_status.py`, `docs/agents/claude-takeover.md` (fenced block), `mise/tasks/ct10.toml` | |
| CT-11 | Serialize named checks (lock) + `JOURNAL/checks/` receipt line | R2, R7 I | — | 1 #2 | `dev/check_lock.py`, `dev/test_check_lock.py`, `dev/check.py` (lock only), `dev/retro_gate.py` (lock line only), `mise/tasks/ct11.toml` | the wave-0 one-line `doctor` call in `check.py` precedes the cut |
| CT-12 | Wire every development test (`test:retro-gate`; `unwired_tests` rule via `dev/doctor/gates.py`; exemptions data; AGENTS line-cap/pointer checks) | R2, R7 H, C2 §H, C3 H | CT-22a (wave 0) | 1 #5 (small; no `check.py` edit any more) | `dev/doctor/exemptions.toml`, `dev/test_check_wiring.py`, `mise/tasks/ct12.toml` | the rule implementation lives in CT-22's `gates.py`; CT-12 wires and tests it on the live tree |
| CT-13 | Grilling-question mod (AskUserQuestion) | SYNTHESIS (19:14Z request) | D14 | user-typed | `.claude/plugins/…` or a `CLAUDE.md` rule | the live prevention for P1-8 |
| CT-14 | `plugins/aggregated-research` guidance + `CLAUDE.md` importer | R2 | — | 3/4 | `plugins/aggregated-research/AGENTS.md`, `CLAUDE.md` | |
| CT-15 | Planning-file shape, `plan:log`, `plan:handoff --write/--check`, `check:planning` runner (calls `doctor --class K,I,D,E,N,L --surface check`) | R2, R7 F, R4, C2 §K | — | 1 #4 | `dev/plan_records.py`, `dev/test_plan_records.py`, `dev/fixtures/plan/`, `mise/tasks/ct15.toml` | one-time migration = runbook step 9 (parent) |
| CT-16 | Settings composition check (`dev/doctor/settings.py` rule; `settings_check.py` alias; `.claude/AGENTS.md` pointer; T-I1, T-I2, T-I4) | R2, C2 §I, C3 I | D4 (wave 0) | 1 (small, sixth lane) or 2 | `dev/doctor/settings.py`, `dev/settings_check.py`, `dev/test_settings_check.py`, `.claude/AGENTS.md` | no longer blocked by CT-02 (the merge finishes in wave 0); shares `dev/doctor/` with CT-22 → **sequential after CT-22a, file-disjoint from CT-22b** |
| CT-17 | Lane lifecycle: `lane:allocate` (records `base_sha` = allocation commit, `--admit`, `--ticket` approval refusal), `lane:integrate` (journal, snapshot via doctor, `--continue/--abort`, foreign-hunk refusal, `--parent-hunk`), `session:status` (= `doctor --class C --json`), `stop_gate` extensions (`merge_state`, `lane.validate`) | R7 B/C/J, C2 §B/§C/§E, C3 C | CT-01, CT-02, CT-05, CT-11, CT-22a, CT-24 | 2 #1 | `dev/lane.py` (`allocate`, `integrate`, `status`), `dev/test_lane.py`, `dev/fixtures/lanes/` (new cases), `dev/hooks/stop_gate.py`, `dev/test_stop_gate.py`, `mise/tasks/ct17.toml` | split `allocate|status` from `integrate` past 300 lines (R7) |
| CT-18 | A09 batch publish wrapper (refuses `MERGE_HEAD`; first step `doctor --surface publish`) | R7 D | CT-02, CT-22a | 2 #3 | `dev/git_delivery.py` (`batch`), `dev/test_git_delivery.py`, `mise/tasks/ct18.toml` | |
| CT-19 | Slotted briefs (`lane:brief` ≤ 1.5 KB, `--role reviewer` slots), agent constants, `reviewer.md:18` fix, `retro-writer.md` step 0, SubagentStop receipt journal (`subagent_receipt.py`), brief-size assertion in `agent_gate` | R7 E/L, C2 §F/§G, C3 G | CT-02, CT-03, CT-05 | 2 #2 | `dev/lane_brief.py`, `dev/test_lane_brief.py`, `dev/hooks/subagent_receipt.py`, `dev/test_subagent_receipt.py`, `.claude/agents/*.md`, `dev/hooks/agent_gate.py` (size rule only; CT-23 is sequential after) , `mise/tasks/ct19.toml` | parent hunk: SubagentStop matcher entry in settings |
| CT-20 | `agent-session-history` skill: `claude_session_digest.py`, `claude_subagents.py`, `session_review.py`, `/session-review`; transcript detectors (A curve/death, C no-commit, D rows, E capture, F dispatch/tdd, G all, J observed, K re-injection); `doctor --surface sweep` calls it | R7 M, C3 CT-23 (absorbed) | CT-07, CT-10, CT-22 | 4 | `.claude/skills/agent-session-history/**`, `.agents/skills/agent-session-history/**`, `dev/test_agent_session_history.py`, `dev/test_doctor_transcripts.py`, `dev/fixtures/doctor/transcripts/**` | |
| CT-21 | Import Codex worktree inputs; `check_inputs.py`, `dev/cited-inputs.json`, `check:inputs`; fail closed on missing inputs; **absorbs** C2 `pinned_paths` and C3 `H.pinned-data-*` resolver | T2 | none | 1 #5 (if a fifth lane is admitted) else 2 first | per `P/lanes/ct21-codex-imports.json` (evidence new files, four `dev/*` files, `check_inputs.py` + test, `dev/fixtures/inputs/`, `mise/tasks/ct21.toml`, `.github/workflows/development.yml` one step) | `development.yml` is **not** a baseline file (`acceptance.yml` is); no `.gitignore` edit (`git add -f`). Parent hunks: `mise.dev.toml` depends ×3, `accepted-decisions.md`, four path rewrites, hk `cited-inputs` step |
| **CT-22** | **Doctor core**: `dev/doctor/{cli,core,budget,lanes,integration,settings,gates,citations,tickets,planfiles,agents,invocations,requests,receipts,codexstate}.py`, surfaces `session-start|check|pre-commit|integrate|publish|sweep`, `--format context`, `--fix` (proven-by-git only), `--snapshot`; fixtures; `test:doctor`; CT-22a = wave-0 slice | C3 (CT-22) + C2 `dev/checks/*`, `dev/planning_checks/*`, CT-24 wording/seed, CT-27 deferral rule, CT-28 citations/exclude, CT-30 validator | none (reads `git_gate.py`, `git_delivery.py`, `check_inputs.py` by path import; `skipped` when absent) | 0 (CT-22a) + 1 heavy slot / 2 (CT-22b) | `dev/doctor/**`, `dev/test_doctor*.py`, `dev/fixtures/doctor/**`, `dev/exclude.txt`, `mise/tasks/ct22.toml` | parent hunks: settings SessionStart entry (wave 0), `check.py` line (wave 0), `check:research` += `test:doctor`, `hk.pkl` `records` step. Disjoint from every R8 wave-1 lane and from CT-21. |
| **CT-23** | **Session hooks follow-up**: thresholds via `env`, `ctx:status`, phase/next extraction in `prompt_hook`, `agent_gate` roster-drift context and (optional) `AGENT-FALLBACK` with `lane:brief --inline-role`, docs §Context budget | C2 CT-22 remainder + CT-26 | CT-19 (shared `agent_gate.py`, sequential), CT-22 | 3 | `dev/context_budget.py`, `dev/hooks/agent_gate.py`, `dev/hooks/prompt_hook.py`, `dev/hooks/rules/common.py`, their tests, `mise/tasks/ct23.toml`, `docs/agents/claude-team.md` (§Context budget) | wave-0 seeds exist; this lane finishes them |
| **CT-24** | **Decisions ledger**: `plan_decide.py` (`approval|operation|receipt`), `P/decisions.jsonl` format, `plan:decide` task, `issue-tracker.md` paragraph ("approvals are `plan:decide approval` rows, not chat"); `lane:allocate` imports `approved()` | C2 CT-25 (trimmed; request capture deferred) | none | 1 (small) | `dev/plan_decide.py`, `dev/test_plan_decide.py`, `mise/tasks/ct24.toml`, `docs/agents/issue-tracker.md` (one paragraph), `P/decisions.jsonl` (parent seeds, lane defines the format) | |

Absorbed (no ticket): C2 CT-23 record guard (dropped), C2 CT-24 (→ CT-22 static, CT-20 transcript),
C2 CT-26 (→ CT-19 size cap, CT-23 rest), C2 CT-27 (→ CT-22 deferral rule, CT-21 pinned data, CT-05
unit↔file, CT-22 P-n cross-check), C2 CT-28 (→ CT-21 resolver, CT-22 exclude/scratch), C2 CT-29
(→ CT-10), C2 CT-30 (→ CT-22 validator, CT-17 refusal, runbook 11), C3 CT-23 (→ CT-20).

Every C2/C3 artifact maps to exactly one ticket in the table above or to a wave-0 parent item
(W0-1…W0-7) or to a DROP/DEFER row. Spot checks: `hooks_install.py` → CT-02b only; `settings.py`
rule → CT-16 (CT-22a ships the module skeleton, CT-16 the rule and tests: sequential, declared);
`subagent_receipt.py` → CT-19; `codex_status.py` → CT-10; `check_inputs.py` → CT-21; the corpus →
CT-02b; `exclude.txt` → CT-22.

`owned_paths` disjointness against R8 wave 1 (`ct02b`: `dev/hooks/{pretooluse_gate,git_gate}.py`,
`dev/test_hooks.py`, `dev/git_delivery.py`; `ct11`: `dev/check.py`, `dev/retro_gate.py`,
`dev/check_lock.py`; `ct05`: `dev/lane.py`, `dev/ledger.py`, `planning-records.md`; `ct15`:
`dev/plan_records.py`) and T2's CT-21: CT-22 (`dev/doctor/**`), CT-24 (`dev/plan_decide.py`),
CT-16 (`dev/doctor/settings.py`, `dev/settings_check.py`) and CT-12 (`dev/doctor/exemptions.toml`,
`dev/test_check_wiring.py`) touch none of those. Two **sequential** pairs inside one tree must be
declared: CT-22a → CT-16 (both under `dev/doctor/`, file-disjoint) and CT-19 → CT-23 (both edit
`dev/hooks/agent_gate.py`; CT-23 is a wave later). Shared files touched only by wave-0 parent
commits: `.claude/settings.json`, `hk.pkl`, `mise.dev.toml`, `dev/check.py` (one line, before the
`ct11` cut), `docs/agents/*.md`, `.git/info/exclude`.

Frozen-baseline exposure: only **CT-08** touches a baseline file (`.gitignore`). CT-21's
`.github/workflows/development.yml` is not in the 19-file list (`acceptance.yml` is). No C2/C3
artifact writes `.gitignore` or `ci/acceptance.sh` (`exclude_sync` writes `.git/info/exclude`,
which is untracked). C2's §K/§L invariants and C3's CI note respect this.

## Hook inventory and latency

Final `.claude/settings.json` after wave 0 + the lanes (project hooks) plus the pwf 3.24.0 plugin
hooks (separate copies; "a plugin's … copy of the same handler stays separate"). Latency = measured
on this checkout where a script exists (claim 19), otherwise estimated from python start (27 ms) +
git calls (≈170 ms each here) + file reads. Matching hooks run in parallel, so the per-event wall
time is the **max**, not the sum.

| Event | Matcher | Command | Timeout | `onFailure` | Latency (typ / worst) | Blocks? |
|---|---|---|---|---|---|---|
| SessionStart | `startup\|resume\|clear\|compact` | pwf `claude-hook.sh session-start` (python fast path) | 10 s | continue (default) | 42 ms / **7.6 s** if `python3` is off PATH (shell chain) | no |
| SessionStart | `startup\|resume\|clear\|compact\|fork` | `dev/doctor/cli.py --surface session-start --format context` | 15 s | continue | ≈0.6–1.2 s (git plumbing ×4–6, lanes, settings, mtimes) / 3 s budget | no |
| UserPromptSubmit | — | pwf `user-prompt-submit` | 10 s | continue | 42 ms | no |
| UserPromptSubmit | — | `dev/hooks/prompt_hook.py` (ctx line, slash-in-paste; thresholds from `doctor/budget.py`) | 10 s | continue | ≈60 ms (backward read of the transcript tail + `task_plan.md` head) | no (never) |
| PreToolUse | `Write\|Edit\|Bash\|Read\|Glob\|Grep` | pwf `pre-tool-use` | 10 s | continue | 42 ms | no |
| PreToolUse | `Bash` | `dev/hooks/pretooluse_gate.py` | 10 s | **block** | 42 ms benign; 350–700 ms on `merge\|push\|publish`; ≤ 6 s budget then deny-with-reason (CT-02b) | yes (deny) |
| PreToolUse | `Agent` | `dev/hooks/agent_gate.py` | 10 s | block | ≈60 ms | yes (deny fork ≥ `fork_deny`; deny `general-purpose` lane prompts) |
| PostToolUse | `Write\|Edit` | pwf `post-tool-use` | 10 s | continue | 42 ms | no |
| PreCompact | `*` | pwf `pre-compact` | 10 s | continue | 42 ms | no (repo adds none) |
| SubagentStop | — | `dev/hooks/subagent_stop_gate.py` (existing) | 15 s | (inert on this event) | ≈200–400 ms (git ×2 + retro gate) | yes, lane worktrees only |
| SubagentStop | `^(implementer\|doc-writer\|reviewer\|retro-writer)$` | `dev/hooks/subagent_receipt.py` (CT-19) | 10 s | — | ≈100 ms (one `rev-parse`, one append) | no |
| Stop | — | pwf `stop` (`gate-stop.sh`; silent unless `.mode` carries `gate`) | 10 s | continue | 42 ms | only in `gated` mode (forbidden by `I.mode-gate`) |
| Stop | — | `dev/hooks/stop_gate.py` (+ CT-17: `merge_state`, `lane.validate` first three failures; one combined reason) | 10 s | (inert) | 201 ms today; ≈0.5 s with validate | yes, once per condition |

Dropped from the inventory versus C2+C3: PreToolUse `Write|Edit` (`record_guard`), PostToolUse
`Skill` (`post_tool`), C3's UserPromptSubmit doctor `prompt` surface, C3's `pre-push` hk step, C2's
Stop `pending_operations`. Maximum hook wall time per event after the change: SessionStart ≈ 3 s
(7.6 s only in the pwf shell-fallback failure mode, which `I.pins-missing` flags); UserPromptSubmit
≈ 0.1 s; PreToolUse(Bash) ≈ 0.05 s normal, ≈ 0.7 s during a merge, 6 s hard budget; PreToolUse(Agent)
≈ 0.06 s; SubagentStop ≈ 0.4 s; Stop ≈ 0.5 s. All inside the configured timeouts with the 10 s
default; the only arithmetic risk is CT-02's `GATE_TIMEOUT = 8` per lane × lanes (`J.timeout-arithmetic`),
removed by CT-02b's deadline.

Double-blocking and ordering: (1) pwf Stop vs `stop_gate.py`: both can only block in pwf `gated`
mode; `I.mode-gate` + T-I5 (`≤ 1 block` on one payload) keep it to one. (2) Inside `stop_gate.py`,
three rules (retro, `merge_state`, `lane.validate`) must emit **one** block with a combined reason;
as C2 wrote them ("block once" each) they would spend up to three continuation turns against the
cap of eight. (3) `subagent_stop_gate.py` (all agents) and `subagent_receipt.py` (roles) run in
parallel on the same stop; the receipt never blocks, so no conflict; the journal line is written
even when the gate blocks (desired). (4) `onFailure: block` on Stop/SubagentStop in the staged file
is inert (claim 12); harmless, but the C2 snippet should not present it as a safety property.
(5) The hk `pre-commit` step and the PreToolUse gate never meet (`git commit` is outside the verb
table by design; the step guards content, the gate guards merge/push form).

## Repair-session safety

Phase 3 = SYNTHESIS §5 runbook steps 1–13 run by the next session on this checkout with the
**existing** CT-02 hooks live (file watcher). Of the proposed artifacts:

| Artifact | Effect if present during Phase 3 | Decision |
|---|---|---|
| `stop_gate` `merge_state` rule (block while `MERGE_HEAD` exists without a runner journal) | **blocks every Stop of the repair session** from step 1 until step 6 commits the merge (the merge is in progress by design and no journal exists) | land with CT-17 (wave 2); never before the merge commit |
| `stop_gate` `lane.validate` rule | **blocks every Stop** until step 7 corrects the nine records (six "publication pending", three `base_sha`, missing `review`, a06 alias) | land after step 7 and after CT-05's validator passes on all nine records |
| hk `pre-commit` `records` step with `lane:validate --staged` | the **merge commit at step 6** stages `lanes/gate-hooks.json`; a validator over the whole lanes dir refuses the commit until step 7 (and `--no-verify` would hide the step's value) | wave 0, **settings rule only**; add `lane:validate --staged` with CT-05 |
| hk `pre-commit` settings rule | after step 2 the staged file is project-only → passes; before step 2 it would refuse the merge commit, which is the desired order anyway | safe after step 2 |
| `pretooluse_gate` `--no-commit` deny (CT-02b) | Runbook 1 runs no new merge; Runbook 2's re-merge is `--no-ff` (allowed); `git merge --abort` allowed | safe either way; lands in wave 1 |
| existing PreToolUse gate (live) | step 6's message file: no line may start with `git merge`/`git push` (SYNTHESIS already says so); every Bash call during the merge costs ≤ 0.7 s | known; tolerated |
| `agent_gate` fork deny / `lane_dispatch` | the repair session starts at ctx ≈ 0; sweeps A/B/C are not lane prompts (no `LANE-UNIT:`) | safe |
| `prompt_hook` ctx line | advisory only | safe, helpful |
| project `autoCompactEnabled: true` / `autoCompactWindow: 700000` | compaction could fire mid-repair if the session ran past 700 K; the repair should finish far below (steps are mechanical) | safe; enables recovery if the repair runs long |
| doctor SessionStart block | read-only; exactly the state the repair needs (MERGE IN PROGRESS, staged count, foreign hunk, stale records) | land **first** if anything lands before the runbook; otherwise the runbook's own identity check suffices |
| doctor `--fix` (status-stale, handoff base) | writes records; would collide with the runbook's step 7 docs commit if run concurrently | run only as part of step 7, or not at all in Phase 3 |

Recommended order: **(1)** runbook steps 1–8 with no new hooks (the existing CT-02 hooks only);
**(2)** wave 0 W0-1/W0-2/W0-7 (settings keys, fixtures, docs) in the step-9/10 commits; **(3)** doctor
slice CT-22a (detection, `onFailure` continue, read-only) and the hk `pre-commit` settings rule;
**(4)** `agent_gate` + `prompt_hook` (deny/advice; low blast radius); **(5)** the Stop-gate
extensions and `lane:validate --staged` only after CT-05 proves every record validates. Detection
first, then advisory hooks, then blocking rules — never a new blocking rule on a tree whose
records are known to fail it.

## Required changes

1. **One static-rule tree.** Replace C2's `dev/checks/*.py` + `dev/planning_checks/*.py` (12
   modules, two discovery loops) with C3's `dev/doctor/` (CT-22); `dev/check.py` gains one line
   (`doctor --surface check`, rc 2 ⇒ fail) and `check:planning` (CT-15) calls `doctor --class
   K,I,D,E,N,L --surface check`. C3's "expected C2 artifact" notes already assume this.
2. **Fix the `base_sha` detector** (claim 11a): derive the allocation commit as the commit that
   added `P/lanes/<unit>.json` (`git log --diff-filter=A --format=%H -- <path>` on the first-parent
   line of the integration branch, or the `docs: allocate lane <unit>` subject), then assert
   `base_sha == allocation` and `allocated_from == allocation^`; add the clean twin. The fixture
   must be built so the vacuous predicate fails the test (record `e618243`, allocation `2d1f60e`).
3. **Drop `record_guard.py` and C2 CT-23**; the hk `pre-commit` `records` step and
   `check:planning` carry the lane-JSON, settings, progress-size and citation rules for both the
   Write/Edit and the Bash-heredoc routes. Drop `post_tool.py` and the invocation journal
   (CT-24 → CT-22/CT-20).
4. **One UserPromptSubmit script and one SessionStart command.** `prompt_hook.py` carries the ctx
   line (thresholds imported from `dev/doctor/budget.py:THRESHOLDS`) and the slash-in-paste
   warning; C3's `prompt` surface digest re-run is dropped. `dev/doctor/cli.py --surface
   session-start` replaces C2's `session_start.py` (C2's `autocompact`, `agent_roster`,
   `merge_state` lines become detectors). One threshold dict: `warn 400 K, checkpoint 550 K,
   fork_deny 500 K, hard 650 K`, all below the project `autoCompactWindow 700000`.
5. **One snapshot function** (`dev/doctor/integration.py`) used by `doctor --snapshot` and by
   `lane:integrate` step 1.5; one corpus file (`dev/fixtures/hooks/bash-corpus.jsonl`, CT-02b);
   one untracked allow-list (`dev/exclude.txt`); one pinned-data resolver (CT-21
   `check_inputs.py`, consumed by `H.pinned-data-*`).
6. **Stop gate: one block per Stop.** `stop_gate.py` evaluates every rule and prints one
   `decision: block` with the combined reasons; `pending_operations` moves to the SessionStart
   line. Remove `onFailure: block` from the Stop and SubagentStop entries in the C2 snippet (inert
   per the docs; keep the staged file's copies if the user prefers not to touch them in Phase 3).
7. **Defer** `merge-tree` composition in `lane:integrate` (keep R7 C's shape), the `tdd_first`
   SubagentStop block (keep the session-review detector), the named-check `receipt:` rule, the
   `CT-nn/k` item-id scheme (interim: `#<issue>` from the ledger snapshot), `plan_requests`
   capture/import, the pwf injector probe, the worktree-nonce probe at `check`, the `pre-push`
   doctor step, the daily sweep schedule, the seed-hash pin (keep the heading check), and the
   `--fix` settings split and snapshot copiers (drop).
8. **Close the P2-10b gap**: add `G.retro-author-not-retro-writer` (a lane ≥ `reviewed` whose
   journal has no `retro-writer` stop while `retros/<u>.md` exists; `skipped` before CT-19) with a
   fixture; and the P2-20 gap: `lane:validate` test T-B8 (`published` ⇒ `worktree_removed` or
   `holds`), plus `plan:handoff --check` listing outstanding stage steps (final `code-review`,
   cleanup) from `spec.manifest.json`.
9. **Drop the `retro_record` alias** everywhere (SYNTHESIS CT-12 row, C2 CT-27): runbook step 7's
   rename resolves P1-13; `lane:validate` then requires `unit == retro file name` and
   `H.retro-unit-alias` reports a recurrence. This removes the CT-11/CT-12/CT-27 collision on
   `dev/retro_gate.py`.
10. **Thin M/N rows**: `codex_status.py` gains a `terminal` field per packet (`TERMINAL.json`
    status, budgets) so P2-9 has a probe; `codex_activation.py` gets a test for the "Inherited
    limitations … manifest: <path> @ <ts>" requirement (P2-12); `N.*` keeps the structural
    validator and the approval row, with the semantic-edge limit stated in the ticket body.
11. **Ticket list** as in §Reconciled ticket table: CT-01…CT-24 + CT-02b; C2's CT-25…CT-30 and
    C3's CT-23 are absorbed; declare the two sequential pairs (CT-22a → CT-16, CT-19 → CT-23) in
    the lane records; move CT-12 and CT-16 to wave 1 as small lanes only if D5 admits six lanes,
    else wave 2.
12. **Claim hygiene in the designs**: replace "stdlib-only under `python3 -I`" with the AST rule
    against `sys.stdlib_module_names` (≈30 lines in `dev/doctor/gates.py`); state that a timed-out
    PreToolUse hook does not block unless `onFailure: block`, so the in-budget deny is the gate;
    record that the hk `pre-commit` hook fires in every worktree through `mise x hk` (≈0.25 s mise
    start + step) and is bypassable by `HK=0`/`--no-verify` (a guard, not a gate; `pre-push`
    never guards A09 because it pushes `--no-verify`).
13. **Wave-0 content** = W0-1…W0-7 (≈620 LOC, 30 tests, ≈14.5 h), landed in the order given in
    §Repair-session safety; nothing from waves 1+ precedes the first wave-1 cut.

## Verdict

**APPROVE WITH CHANGES** (1–13 above). The three designs cover all 39 findings (34 with a full
prevention + detection + test chain; 5 gaps, all closable in ≤ 40 lines each; 2 one-sided rows
justified). The root-cause analysis (C1) holds; C2 and C3 extend R7 rather than fork it (every
R7 proposal A–O keeps its ticket; C2's `lane.py`/`plan_records.py`/`subagent_receipt.py` are R7's
A–F/L; C3's doctor is R7 J generalised). The defects are duplication and reach, not direction:
two static-rule trees, two SessionStart commands, two UserPromptSubmit surfaces, three pinned-data
resolvers, two snapshot writers, two threshold tables, nine new tickets where three suffice, one
hook per Write/Edit and one per Skill call that no occurred finding needs, one detector predicate
that cannot fire, and three Stop rules that would each spend a continuation turn. With the merges
the programme shrinks to 5 project hook scripts + 1 doctor command, one `dev/doctor/` tree of
≈11 modules, 24 tickets, and a wave 0 of ≈620 lines that the repair session can land without
blocking itself.

## Could not verify

- Whether `~/.claude.json`'s `autoCompactEnabled: false` participates in the effective value
  (the reference marks the key "Any file" and lists it nowhere under "Global config"; no page
  fetched says the CLI-written copy is ignored). D-A1 (user flips both) stands.
- The `agent_type` value a fork's hooks receive; `.meta.json` says `agentType: fork`.
- `hk run pre-commit` offline behaviour when the `package://…hk@2.5.0` pkl is not in the cache;
  and whether `hk` 2.6.0 accepts the staged `hk.pkl` (`min_hk_version 2.5.0`) under `mise x hk`
  (`hk validate` was not run: it is a named check in the runbook, step 5).
- Whether `task_config.includes` validates under `./dev/mise` (R8 D7; every report defers it).
- Latency of the doctor `session-start` surface (≈0.6–1.2 s is an estimate from 4–6 git calls at
  ≈170 ms each on this 27-worktree checkout; `git rev-parse HEAD` alone took 168 ms here, so the
  3 s budget is realistic but not measured).
- The R7 PreToolUse timeout: the staged gate took 676 ms on the real in-progress merge and did
  not deny the heredoc command today (the lane passes); the 10 s timeout remains unreproduced.
- The pwf shell-chain figure (7.6 s) is R4's; the fast path exists in `claude-hook.sh` (lines
  123–138) and was not timed here.
- C3's expected counts on today's tree (4 P1 / 11 P2 / 7 P3) and C2's 66-test total were not
  recomputed; the matrix counts rows, not test functions.
- `agent_listing_delta` attachment shape (C3 F); the mtime form needs no attachment.
- Whether `hk install --force-local` on Git 2.54 writes the config entries under `--local` scope
  exactly as `hook.hk-<name>.{event,command}` (inferred from `hk install --help` and the global
  entries' shape; not run — a write).
