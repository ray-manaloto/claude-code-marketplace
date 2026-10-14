# Review brief: w0-session-hooks (reviewer)

LANE-UNIT: w0-session-hooks. Role: reviewer (`.claude/agents/reviewer.md`), Fable high, cold, read-only: do not edit, write, commit, merge, push or spawn agents; return text only (the parent saves it as `RV/phase3/w0/w0-session-hooks-review.md`).
Shorthand: ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace, P=ROOT/.planning/2026-10-10-marketplace-macos-reflection-scaffold, RV=P/reviews/ccm-20261013, C2/C3/C4=RV/prevention/C{2,3,4}-*.md.
Inputs: record P/lanes/w0-session-hooks.json; acceptance source RV/phase3/w0/w0-session-hooks-brief.md (items and test names) and the C2/C3/C4 anchors it cites; ticket CT-23 (wave-0 seeds); the implementer's receipt (path from the parent).
Worktree ROOT/.claude/worktrees/w0-session-hooks, branch `claude/w0-session-hooks-budget`, fixed point (base) `<CUT>` (the `docs: allocate lane w0-session-hooks` commit), head = the receipt's final SHA.
Diff: `git diff codex/marketplace-native-onboarding...<head>` is the lane's own change after its tip merge; also `git diff --stat `<CUT>` (the `docs: allocate lane w0-session-hooks` commit)..<head>` and `git log --first-parent `<CUT>` (the `docs: allocate lane w0-session-hooks` commit)..<head>` to confirm the tip merge. Read every changed file.

## Standards axis (each holds or is a finding)
- Changed paths are a subset of `owned_paths` plus the lane's retro and ledger; no lane record, task_plan, progress, findings or ticket-ledger edit; the 19 baseline files untouched (`./dev/mise run check:acceptance-baseline`).
- `CODING_STANDARDS.md`, the nearest `AGENTS.md`, `.claude/rules/*.md`, `docs/agents/codex-task-orchestration.md#ownership`; stdlib only, checked against `sys.stdlib_module_names`, not inferred from `python3 -I` (C4 change 12); <= 80 handwritten lines per file and about 300 per unit (C4), else a reported split point.
- Tests assert an external seam (CLI, hook stdin/stdout, scratch repo), are red-first per the receipt, and name the C2/C3 ids; no tautological expectations.
- Receipts bind actual rcs; no named check is claimed while another ran; the retro draft passes `./dev/mise run retro:gate -- w0-session-hooks`.

## Spec axis
Every item in the brief is demonstrated by a named test or a receipt line, or recorded as unrun with a reason. Lane-specific checks:
- False positives: fork under budget, `implementer` dispatch, `general-purpose` without `LANE-UNIT:`, and a typed `/command` are all allowed or silent; prompt_hook never emits a block decision.
- Thresholds come from `dev/doctor/budget.py` (no second table); the deny output uses the documented PreToolUse JSON (`hookSpecificOutput.permissionDecision`) like `dev/hooks/pretooluse_gate.py`; `subagent_type` is never rewritten.
- Hook latency: time `agent_gate.py` and `prompt_hook.py` yourself on the fixture payloads and on the 20 MB synthetic transcript (`/usr/bin/time -p python3 -I dev/hooks/agent_gate.py < payload.json`, payload built in your scratchpad); compare with the receipt; about 60 ms typical, under 1 s.
- Fixtures: no transcript bodies, no secrets (`gitleaks dir dev/fixtures/hooks` rc), `$HOME` paths generalised; spot-check 10 corpus rows' `expect` lists against the gate's verb table (C2 §J); row count 113 or the difference explained.
- Wiring: PreToolUse `Agent` has `onFailure: block`, UserPromptSubmit has none; `test:hooks-session` is in `check:research` depends; the Settings test covers the inventory in C4 §Hook inventory.
- D26: nothing blocking beyond the `Agent` deny; no Stop or SubagentStop change.

## Re-run yourself (read-only; record each rc)
`python3 -I -m unittest dev/test_context_budget.py dev/test_agent_gate.py dev/test_prompt_hook.py -v` (from the worktree root); `python3 -I -m unittest discover -s dev -p test_hooks.py -v`; `gitleaks dir dev/fixtures/hooks`; `./dev/mise run retro:gate -- w0-session-hooks`.

## Verdict format
`## Standards` and `## Spec` blocks, findings severity-ordered P1/P2/P3 with `path:line` and the evidence read (P1 blocks integration, P2 is fixed before acceptance, P3 defers with an owner), then `Disposition: PASS | PASS-with-P2/P3 | FAIL` and the checks you did not run. <= 400 words per axis.
