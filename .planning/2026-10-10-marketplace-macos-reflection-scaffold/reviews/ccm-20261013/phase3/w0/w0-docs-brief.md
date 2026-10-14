# Brief: w0-docs (doc-writer)

LANE-UNIT: w0-docs. Role: doc-writer (`.claude/agents/doc-writer.md`), Opus high per the parent (frontier `model_policy.docs` says sonnet), `writing-for-agents` preloaded.
Shorthand: ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace, P=ROOT/.planning/2026-10-10-marketplace-macos-reflection-scaffold, RV=P/reviews/ccm-20261013, C2/C4=RV/prevention/C{2,4}-*.md, S4=RV/SYNTHESIS.md §4 (lines 234-286).
Tickets: C4 W0-7 (D15, D26); CT-02b doc slice (merge rule, both Stop hooks); CT-23 doc slice (§Context budget). Residual list: P/task_plan.md Phase 4 W0-7 bullet; RV/phase3/I3-group3a-report.md §7.
Record: P/lanes/w0-docs.json (parent-only, D8; `base_sha` null by design). Worktree ROOT/.claude/worktrees/w0-docs, branch `claude/w0-docs-rules`, base A=`c21941f` (allocated_from `d420a7e`). Prep done: tools:prepare 0, deps:sync 0, check 0.
Env: `export PWF_PLAN_ROOT=ROOT PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold; unset VIRTUAL_ENV`. Context ceiling 500K (D29/D30).
Owned: `docs/agents/claude-team.md`, `docs/agents/ticket-retro.md`, `docs/agents/issue-tracker.md`, `.claude/AGENTS.md`, `P/skill-invocations.md` (row 20 only), `P/proposals/claude-takeover-spec/spec.md` (lines 61, 65 only), P/retros/w0-docs.md, P/ledger-w0-docs.jsonl.
Never: `docs/agents/claude-takeover.md` and `codex-task-orchestration.md` (their `2a14` paths wait for CT-21), the four CT-21 docs (`automation-amendment-review`, `github-search-reuse`, `workflow-reconciliation`, `codex-example-classification`), `dev/` (incl. `checkout_transfer.py:17`, CT-21), `mise.dev.toml`, `.claude/settings.json`, `hk.pkl`, root AGENTS/CLAUDE, task_plan/progress/findings/ledger, lane records.

## Items and acceptance (each edit cites its source row; every sentence changes what an agent does)
1. `claude-team.md` §Integration: merges are `--no-ff`, never `--no-commit` (C2 §C rule text :342; C4 §Repair-session safety; S4 claude-team row); run `retro:gate -- <unit>` by hand until hk layer 2 is installed (`hooks:install` waits for CT-02b, D2); the two-gate note (lane state vs pwf phase state).
2. `claude-team.md` §Context budget (C4 required change 4; C2 §A Rule text :181-185, numbers replaced by C4's): warn 400K -> checkpoint and delegate; checkpoint 550K -> handoff, then `/clear`; no fork at or above fork_deny 500K; hard 650K; all below `autoCompactWindow` 700000 (project settings, D21). State them as rules; the hooks that enforce them arrive with w0-session-hooks and are not claimed here.
3. `claude-team.md` §Roles restart rule (C2 §F rule text :567-568): `.claude/agents/*.md` exist and are committed before the session that dispatches them; a session that creates them restarts.
4. `claude-team.md` hooks: the pwf Stop hook and `stop_gate.py` compose (one block per Stop); pwf `.mode` never carries `gate`; `onFailure` is inert on Stop/SubagentStop (C4 change 6); caveats from S4: trust-held hooks, `disableAllHooks`, managed settings.
5. `ticket-retro.md:4-8`: the D15 rewrite text in S4's ticket-retro row.
6. `.claude/AGENTS.md`: the project settings key list (`$schema`, `env`, `autoCompactEnabled`, `autoCompactWindow`, `enabledPlugins`, `extraKnownMarketplaces`, `hooks`) and the marketplaces line (project marketplaces in `settings.json`, personal ones in `settings.local.json`).
7. `issue-tracker.md`: a section headed `When a skill says publish / fetch` (the seed's heading, so the user-typed setup rewrite keeps it) with the `issue:*` qualified-operation mapping and "`research/<name>` branches stay local until an admitted A09 publish" (S4 row).
8. `P/skill-invocations.md:20` and `spec.md:61,65` per their S4 rows (D14: CT-13 carries the UI-mod request; D10: spec `start_sha` `361688e`).
9. Verify only, no edit: `.git/info/exclude` holds `.agent/` and the settings backup path; the secrets line is at `claude-takeover.md:13`. Report both.
Every cited path resolves (`rg --files`), every cited task exists (`./dev/mise tasks ls`).

## Gates (expected rc 0 each; record actual rcs)
`./dev/mise tasks validate`; `./dev/mise run check`; `./dev/mise run check:acceptance-baseline`; `./dev/mise run test:hooks`; `hk validate`; `git diff --check`; `./dev/mise run retro:gate -- w0-docs`. Never `check:research`, push or publish.

Before reporting, merge the current integration tip (`codex/marketplace-native-onboarding`) into your branch, rerun the gates on the merged bytes, commit, `git status` clean. Draft the retro per `docs/agents/ticket-retro.md`.
Trailers: `Co-Authored-By: Claude <your model and version> <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_015qxgfYywpRPVMk8tYDLCHT`.
Receipt (<= 300 words): branch, final SHA, tip merged, changed paths (a subset of owned), each command with its rc, item 9 results, deviations, unverified items, retro path.
