# gate-hooks retrospective — hook wiring for the retro gate (CT-02)

Unit `gate-hooks`, branch `claude/gate-hooks-wiring`, base `2d1f60e`. Written by
the implementer inside the lane worktree (lane-worktree retro convention), before
independent review. Exits with `VIRTUAL_ENV` unset: `test_hooks.py` 10 tests rc 0
(4.0 s), `hk validate` rc 0 (hk 2.6.0 and 2.5.0), `tasks validate` rc 0 (56), `check` rc 0,
`check:acceptance-baseline` rc 0 (19/19), `git diff --check` rc 0. Not run: a
fresh Claude Code session exercising the settings hooks, and `hk install` in the
real checkout (parent-run at integration).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P1 | Automated checks: the host's global hk hooks run `mise x hk -- hk`, which resolves hk 2.5.0, and the first commit failed with "hk version 2.5.0 is less than the minimum required version 2.6.0". A 2.6.0-only `hk.pkl` would block every commit in the checkout. | Applied: `hk.pkl` amends the 2.5.0 package with `min_hk_version = "2.5.0"`. `hk validate` rc 0 under hk 2.6.0, under hk 2.5.0 and with an empty `HOME`; the commit then went through. |
| P2 | Automated checks: the brief's `retro:gate-merge` = `retro_gate.py --from-merge-head` cannot gate a merge. A probe hook showed Git writes `MERGE_HEAD` only after `pre-merge-commit` succeeds; the hook sees `GIT_REFLOG_ACTION=merge claude/x-y`. `--branch main` also exits 1, so merging `main` would be refused. | Applied: `dev/hooks/git_gate.py merge` reads `MERGE_HEAD` or `GIT_REFLOG_ACTION` and skips the integration branch and `main`. The scratch hk test failed first (merge accepted, rc 0) and now passes. |
| P2 | Navigation: a global hk install (`hook.hk-*` in `~/.gitconfig`, present on this host) makes a plain `hk install` skip the per-repository hooks, and `pre-merge-commit` is not global. | Applied: `hooks:install` runs `hk install --force-local`; hk reports that the local hook replaces the global one (one run per event). This was checked in a scratch repository with a fake global config. |
| P2 | Automated checks: `delivery:publish` pushes with `--no-verify` (`dev/git_delivery.py` line 415), so hk `pre-push` never sees a publication. | Applied: the PreToolUse hook checks the unpublished lane merges for `delivery:publish`; covered by `test_delivery_publish_checks_unpublished_lane_merges`. |
| P3 | Tool economy: `git` resolves to a version-manager shim at ~0.15 s per call; the first suite run took 25.0 s. | Applied: the tests put `git --exec-path` first on `PATH`; the suite now takes 3.3–4.0 s. |
| P3 | Information access: SubagentStop keys on the event `cwd`. A subagent that drives a worktree by absolute paths (as this lane did) reports the root checkout, so that layer cannot see it. | Deferred with owner parent: evaluate `agent_type` or the lane worktree in a later ticket. The hk merge/push layers and PreToolUse still bind such lanes. |
| P3 | Steering/global guidance: `stop_gate.py` blocks the parent once per stop while the five integrated lane records (`a06-unit3`, `codex-session-history`, `retro-gate`, `rf-env-scrub`, `team`) lack `"retro": "passed"`. | Owner parent: set the field in those shared lane records after `retro:gate` rc 0. The vocabulary is documented in `docs/agents/claude-team.md`. |
| P3 | Automated checks: `.claude/rules/dev-tests.md` routes a test through `check:research` depends; `test:hooks` is not listed there (that row is outside this lane's hook-only allowlist). | Owner parent: add `test:hooks` to `check:research` depends at integration. The hk class skips when `hk` is absent. |
| P3 | Coding standards: the diff is ≈645 added lines: 289 script lines, 221 test lines and 63 lines of settings, mostly copied. That exceeds the 400-line report threshold. The scripts were written before their contract tests, so only the hk merge test was observed red first. | Reported in the handoff; whether to split is the parent's or reviewer's call (owner parent). |

No-ops: none, because each hook script enforces a rule that no existing check covered.

Steering beyond the row above: none, because `AGENTS.md` and `CLAUDE.md` are untouched.
