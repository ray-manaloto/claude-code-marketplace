# Review brief: w0-doctor-records (reviewer)

LANE-UNIT: w0-doctor-records. Role: reviewer (`.claude/agents/reviewer.md`), Fable high, cold, read-only: do not edit, write, commit, merge, push or spawn agents; return text only (the parent saves it as `RV/phase3/w0/w0-doctor-records-review.md`).
Shorthand: ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace, P=ROOT/.planning/2026-10-10-marketplace-macos-reflection-scaffold, RV=P/reviews/ccm-20261013, C2/C3/C4=RV/prevention/C{2,3,4}-*.md.
Inputs: record P/lanes/w0-doctor-records.json; acceptance source RV/phase3/w0/w0-doctor-records-brief.md (items and test names) and the C2/C3/C4 anchors it cites; ticket CT-22 (CT-22a part 2); the implementer's receipt (path from the parent).
Worktree ROOT/.claude/worktrees/w0-doctor-records, branch `claude/w0-doctor-records-detectors`, fixed point (base) `<CUT>` (the `docs: allocate lane w0-doctor-records` commit), head = the receipt's final SHA.
Diff: `git diff codex/marketplace-native-onboarding...<head>` is the lane's own change after its tip merge; also `git diff --stat `<CUT>` (the `docs: allocate lane w0-doctor-records` commit)..<head>` and `git log --first-parent `<CUT>` (the `docs: allocate lane w0-doctor-records` commit)..<head>` to confirm the tip merge. Read every changed file.

## Standards axis (each holds or is a finding)
- Changed paths are a subset of `owned_paths` plus the lane's retro and ledger; no lane record, task_plan, progress, findings or ticket-ledger edit; the 19 baseline files untouched (`./dev/mise run check:acceptance-baseline`).
- `CODING_STANDARDS.md`, the nearest `AGENTS.md`, `.claude/rules/*.md`, `docs/agents/codex-task-orchestration.md#ownership`; stdlib only, checked against `sys.stdlib_module_names`, not inferred from `python3 -I` (C4 change 12); <= 80 handwritten lines per file and about 300 per unit (C4), else a reported split point.
- Tests assert an external seam (CLI, hook stdin/stdout, scratch repo), are red-first per the receipt, and name the C2/C3 ids; no tautological expectations.
- Receipts bind actual rcs; no named check is claimed while another ran; the retro draft passes `./dev/mise run retro:gate -- w0-doctor-records`.

## Spec axis
Every item in the brief is demonstrated by a named test or a receipt line, or recorded as unrun with a reason. Lane-specific checks:
- The base_sha test fails against the vacuous predicate ("first commit of base..branch has parent base"): read the fixture construction, not only the assertion (C4 change 2, claim 11a).
- False positives: clean record twin returns `[]`; an `allocated` record with null `base_sha` is not a finding; the five live `w0-*` records produce no B.* finding by construction.
- `B.retro-claim-unverified` runs only on the check surface within 2 s per unit; no detector writes a record (no `--fix`).
- No edit to w0-doctor's files; `test_doctor_records.py` is picked up by `test:doctor`.
- Live findings: the receipt's proposed record edits are literal and each is backed by a git fact you can reproduce.
- Latency: session-start surface wall time with the two modules added stays under 3,000 ms (time it yourself).

## Re-run yourself (read-only; record each rc)
`python3 -I -m unittest discover -s dev -p 'test_doctor*.py' -v`; `python3 -I dev/doctor/cli.py --surface check --json`; `/usr/bin/time -p python3 -I dev/doctor/cli.py --surface session-start --format context < /dev/null`; `./dev/mise run retro:gate -- w0-doctor-records`.

## Verdict format
`## Standards` and `## Spec` blocks, findings severity-ordered P1/P2/P3 with `path:line` and the evidence read (P1 blocks integration, P2 is fixed before acceptance, P3 defers with an owner), then `Disposition: PASS | PASS-with-P2/P3 | FAIL` and the checks you did not run. <= 400 words per axis.
