# gate-hooks retrospective — hook wiring for the retro gate (CT-02)

Unit `gate-hooks`, branch `claude/gate-hooks-wiring`, base `2d1f60e` (allocated from `e618243`). Written by
the implementer inside the lane worktree (lane-worktree retro convention), before
independent review. Exits with `VIRTUAL_ENV` unset: `test_hooks.py` 10 tests rc 0
(4.0 s; 10 before repair, 13 after `dec8425`), `hk validate` rc 0 (the cold reviewer ran
hk 2.6.0 only; 2.5.0 was verified at integration, see below), `tasks validate` rc 0 (56), `check` rc 0,
`check:acceptance-baseline` rc 0 (19/19), `git diff --check` rc 0. Not run: a
fresh Claude Code session exercising the settings hooks, and `hk install` in the
real checkout (parent-run at integration).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P1 | Automated checks: the host's global hk hooks run `mise x hk -- hk`, which resolves hk 2.5.0, and the first commit failed with "hk version 2.5.0 is less than the minimum required version 2.6.0". A 2.6.0-only `hk.pkl` would block every commit in the checkout. | Applied: `hk.pkl` amends the 2.5.0 package with `min_hk_version = "2.5.0"`. `hk validate` rc 0 under hk 2.6.0 (cold reviewer) and, at integration, under hk 2.5.0 (`mise x hk -- hk validate` rc 0); the empty-`HOME` run is the implementer's claim. The commit then went through. |
| P2 | Automated checks: the brief's `retro:gate-merge` = `retro_gate.py --from-merge-head` cannot gate a merge. A probe hook showed Git writes `MERGE_HEAD` only after `pre-merge-commit` succeeds; the hook sees `GIT_REFLOG_ACTION=merge claude/x-y`. `--branch main` also exits 1, so merging `main` would be refused. | Applied: `dev/hooks/git_gate.py merge` reads `MERGE_HEAD` or `GIT_REFLOG_ACTION` and skips the integration branch and `main`. The scratch hk test failed first (merge accepted, rc 0) and now passes. |
| P2 | Navigation: a global hk install (`hook.hk-*` in `~/.gitconfig`, present on this host) makes a plain `hk install` skip the per-repository hooks, and `pre-merge-commit` is not global. | Applied: `hooks:install` runs `hk install --force-local`; hk reports that the local hook replaces the global one (one run per event). This was checked in a scratch repository with a fake global config. |
| P2 | Automated checks: `delivery:publish` pushes with `--no-verify` (`dev/git_delivery.py` line 415), so hk `pre-push` never sees a publication. | Applied: the PreToolUse hook checks the unpublished lane merges for `delivery:publish`; covered by `test_delivery_publish_checks_unpublished_lane_merges`. |
| P3 | Tool economy: `git` resolves to a version-manager shim at ~0.15 s per call; the first suite run took 25.0 s. | Applied: the tests put `git --exec-path` first on `PATH`; the suite now takes 3.3–4.0 s. |
| P3 | Information access: SubagentStop keys on the event `cwd`. A subagent that drives a worktree by absolute paths (as this lane did) reports the root checkout, so that layer cannot see it. | Deferred with owner parent: evaluate `agent_type` or the lane worktree in a later ticket. The hk merge/push layers and PreToolUse still bind such lanes. |
| P3 | Steering/global guidance: `stop_gate.py` blocks the parent once per stop while the five integrated lane records (`a06-unit3`, `codex-session-history`, `retro-gate`, `rf-env-scrub`, `team`) lack `"retro": "passed"`. | Resolved in `4870211` (the parent set `"retro": "passed"` on those records after `retro:gate` rc 0). The vocabulary is documented in `docs/agents/claude-team.md`. |
| P3 | Automated checks: `.claude/rules/dev-tests.md` routes a test through `check:research` depends; `test:hooks` is not listed there (that row is outside this lane's hook-only allowlist). | Applied at integration (`mise.dev.toml` `check:research` depends gains `test:hooks`; a declared parent hunk of the integration merge). The hk class skips when `hk` is absent. |
| P3 | Coding standards: the diff is ≈645 added lines: 289 script lines, 221 test lines and 63 lines of settings, mostly copied. That exceeds the 400-line report threshold. The scripts were written before their contract tests, so only the hk merge test was observed red first. | Reported in the handoff; whether to split is the parent's or reviewer's call (owner parent). |

No-ops: none, because each hook script enforces a rule that no existing check covered.

Steering beyond the row above: none, because `AGENTS.md` and `CLAUDE.md` are untouched.

## Cold review disposition (Fable, PASS-with-P2) and repair

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks (P2-1): `git_gate.py` accepted `name-rev` suffixes, so a sync merge of the integration tip was blamed on another lane. Observed: `retro:gate-push` rc 2 blamed `claude/nav-guidance-hierarchy` for `51f63c6`. | Applied: only exact ref names count. A merge is attributed by its default subject, else by refs pointing exactly at its second parent; the integration branch wins and lane-record branches are preferred. The regression test `test_sync_merge_of_the_integration_tip_is_not_blamed_on_another_lane` failed first (it blamed `claude/a-b`) and now passes. On this branch, `git_gate.py push` rc 0. |
| P2 | Steering/global guidance (P2-2): the layer-2 paragraph overclaimed. A fast-forward, `--squash`, `--no-commit` then commit, and an unknown merge source all passed open. | Applied: `hooks:install` also sets local `merge.ff=false` and logs it. The merge gate refuses a source it cannot classify, or a missing source; `main` and the integration branch are allowed. The paragraph lists fast-forward (merge or pull), squash, rebase and cherry-pick as outside layer 2, with pre-push as the backstop. Tests: `test_merge_gate_classifies_the_merge_source`, and the hk test merges a fast-forwardable branch. |
| P3 | Automated checks (P3-2/3): there were no tests for a multi-lane push, a merge of `main`, a missing merge source or a gate exit 1. The fake `dev/mise` used `shell=True`. | Applied: `test_push_refuses_only_the_failing_lane` and `test_merge_gate_classifies_the_merge_source`. The fake mise uses `shlex` argv; the suite has 13 tests, rc 0. Not covered (deferred, owner CT-02b): the reviewer's P3-2 bypasses of the PreToolUse gate (`/usr/bin/git merge`, cherry-pick, rebase, pull). |
| P3 | Information access (P3-4): reasons carried absolute paths and raw exception text. | Applied: reasons are repository-relative, and timeouts or start failures are classified. Tests assert that the scratch path never appears. |

| P3 | Automated checks (review P3-5): after `hooks:install`, unpublished lane merges make hk `pre-push` gate every push of the integration branch. | Deferred, owner CT-02b; `hooks:install` is not run at integration (decision D2) so the first A09 publish is unaffected. |
| P3 | Automated checks (re-review P3): a merge with a custom subject cannot be attributed to a lane; the attribution should also match `^Integrate lane`. | Deferred, owner CT-02b. |

## Integration repair (I1b): `test:hooks` under `dev/mise`

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P1 | Automated checks: on `e12cf04`, `./dev/mise run test:hooks` was rc 1 (`HkHooks.test_merge_commit_and_push_refused_then_accepted`, `mise ERROR Config files in …/repo/mise.dev.toml are not trusted`). `environment()` kept the outer `MISE_*` trust and config variables, so a nested mise call in the scratch repo saw its untrusted copy. The direct unittest run passed, so the earlier "13 tests, rc 0" receipt did not cover the `dev/mise` path. | Applied: `environment()` also scrubs the `MISE_` prefix. The regression test `ScratchEnvironment.test_outer_mise_trust_and_config_do_not_reach_the_scratch_repo` failed first (6 `MISE_*` keys leaked) and now passes. Results: direct suite rc 0, `./dev/mise run test:hooks` rc 0 (14 tests), `check` rc 0, `hk validate` rc 0, `git diff --check` rc 0. Focused re-review of `697e1da` (Fable, cold): PASS-with-P3, `reviews/ccm-20261013/phase3/I1b-review.md`. |
| P3 | Steering/global guidance (I1b re-review P3-1..P3-3): the trailer names the model that wrote the commit (Opus 5.5) rather than the parent's requested line; the retro path was not in `owned_paths`; this row said the re-review was pending. | P3-1: kept as written, because the integrating session's harness attribution names the same model and no user instruction sets the line; `697e1da` is not amended. P3-2: applied, `lanes/gate-hooks.json#owned_paths` lists this record. P3-3: applied in this row. |

## Integration (parent, merge of `697e1da` into `codex/marketplace-native-onboarding`)

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Steering/global guidance: focused re-review of `e12cf04` (reviewer `a221b354`) returned PASS for integration with `retro:gate -- gate-hooks` rc 0; the merger fork then died before committing, leaving the merge staged. | Applied: the staged merge of `e12cf04` was kept for the review session `ccm-20261013` (decision D1); `test:hooks` then failed under `dev/mise`, so the merger aborted it after backing up the composed parent hunks (`reviews/ccm-20261013/plan-backups/group1/composed/`), merged the repaired tip `697e1da` with `--no-ff --no-commit`, re-applied the declared parent hunks and committed once the gates exited 0. |
| P2 | Coding standards: the lane's `.claude/settings.json` carried personal keys (MCP `permissions`, personal plugins) and no marketplaces for its project plugins (review P3-1). | Applied: settings composition per R5 §B (decision D4): the project file holds `$schema`, hooks, the four workflow plugins and their marketplaces, plus `autoCompactEnabled`/`autoCompactWindow` (D21) and `env.PLAN_ID`; personal keys moved to the excluded `settings.local.json`. A lossless key-set assertion exited 0. |
| P3 | Automated checks: `hooks:install` (hk Git hooks, `merge.ff=false`) is not run in the real checkout. | Deferred, owner CT-02b (decision D2); `retro:gate` runs by hand before each integration until then. |
