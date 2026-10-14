# Review brief: w0-docs (reviewer)

LANE-UNIT: w0-docs. Role: reviewer (`.claude/agents/reviewer.md`), Fable high, cold, read-only: do not edit, write, commit, merge, push or spawn agents; return text only (the parent saves it as `RV/phase3/w0/w0-docs-review.md`).
Shorthand: ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace, P=ROOT/.planning/2026-10-10-marketplace-macos-reflection-scaffold, RV=P/reviews/ccm-20261013, C2/C3/C4=RV/prevention/C{2,3,4}-*.md.
Inputs: record P/lanes/w0-docs.json; acceptance source RV/phase3/w0/w0-docs-brief.md (items and test names) and the C2/C3/C4 anchors it cites; ticket W0-7 (CT-02b and CT-23 doc slices, D15); the implementer's receipt (path from the parent).
Worktree ROOT/.claude/worktrees/w0-docs, branch `claude/w0-docs-rules`, fixed point (base) `c21941f`, head = the receipt's final SHA.
Diff: `git diff codex/marketplace-native-onboarding...<head>` is the lane's own change after its tip merge; also `git diff --stat `c21941f`..<head>` and `git log --first-parent `c21941f`..<head>` to confirm the tip merge. Read every changed file.

## Standards axis (each holds or is a finding)
- Changed paths are a subset of `owned_paths` plus the lane's retro and ledger; no lane record, task_plan, progress, findings or ticket-ledger edit; the 19 baseline files untouched (`./dev/mise run check:acceptance-baseline`).
- `CODING_STANDARDS.md`, the nearest `AGENTS.md`, `.claude/rules/*.md`, `docs/agents/codex-task-orchestration.md#ownership`; stdlib only, checked against `sys.stdlib_module_names`, not inferred from `python3 -I` (C4 change 12); <= 80 handwritten lines per file and about 300 per unit (C4), else a reported split point.
- Tests assert an external seam (CLI, hook stdin/stdout, scratch repo), are red-first per the receipt, and name the C2/C3 ids; no tautological expectations.
- Receipts bind actual rcs; no named check is claimed while another ran; the retro draft passes `./dev/mise run retro:gate -- w0-docs`.

## Spec axis
Every item in the brief is demonstrated by a named test or a receipt line, or recorded as unrun with a reason. Lane-specific checks:
- Each edit matches its source row (SYNTHESIS §4, C2 rule texts, C4 changes 4 and 6) and states a behaviour; no sentence claims a hook that is not yet integrated (doctor, agent_gate, prompt_hook).
- Thresholds equal C4's (400K/550K/500K/650K, below 700000); the merge rule says `--no-ff`, never `--no-commit`; `.mode` never `gate`.
- `ticket-retro.md:4-8` no longer says "standing user request is the invocation authority"; `rg -n 'standing authorization|invocation authority' docs/agents` is empty.
- Out-of-scope lines untouched: `claude-takeover.md`, `codex-task-orchestration.md`, the four CT-21 docs, `dev/checkout_transfer.py`.
- Every cited path resolves (`rg --files`), every cited task exists (`./dev/mise tasks ls`); item 9 verification reported.

## Re-run yourself (read-only; record each rc)
`./dev/mise run check`; `./dev/mise tasks validate`; `rg -n 'standing authorization|invocation authority' docs/agents`; `./dev/mise run retro:gate -- w0-docs`.

## Verdict format
`## Standards` and `## Spec` blocks, findings severity-ordered P1/P2/P3 with `path:line` and the evidence read (P1 blocks integration, P2 is fixed before acceptance, P3 defers with an owner), then `Disposition: PASS | PASS-with-P2/P3 | FAIL` and the checks you did not run. <= 400 words per axis.
