# retro-gate retrospective — deterministic retro gate (CT-01)

Unit `retro-gate`, branch `claude/retro-gate-task`, commit `894d07d`, merged with tip `c8f4e64` as `0f7ddad`. Exits (VIRTUAL_ENV unset): suite 15 tests rc 0 (pre- and post-merge), `retro:gate m0-remaining-work-merge` rc 0, `retro:gate A11b` rc 2, `tasks validate` rc 0 (51), `check` rc 0, `check:acceptance-baseline` rc 0 (19/19), `git diff --check` rc 0. Imported draft gave 5 red tests before the rewrite. Cold review: PASS-with-P2, all findings applied; merged with tip `9d478cd` as `82c351f` after repair `5ea8ee4` (final lane tip; integration merge `e618243`).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: the draft matched `pass` case-insensitively, so prose ("must pass named checks") counted as a receipt; category names wrapped across a line break were missed. | Applied: case-sensitive `PASS`, whitespace-collapsed matching; test `test_wrapped_category_counts_and_prose_pass_does_not`. Calibration moved to 22 pass / 15 fail of 37 (later-record-transfer, process-followup now pass; publication-scope fails on evidence). |
| P2 | Navigation: `claude/<unit>-<slug>` is ambiguous when the unit contains hyphens (`retro-gate`). | Applied: lane record `branch` match first, then longest existing record prefix; suite covers `claude/x-y` and `--from-merge-head`; `retro_gate.py` on this branch resolved `retro-gate`. |
| P3 | Information access: receipts did not bind runtime selectors (P3 routed from M0). | Applied: last line `selectors: <names>`, values never printed; tested. |
| P3 | Tool economy: suite took 9.5 s (each git call ~0.2 s). | Applied: template repo per class, lazy repo lookup; 5–7.6 s. |
| P2 | Automated checks (cold review P2-1, P2-2, P3-1, P3-3): `#\d+` inside `\b…\b` never matched after a space; reads were unbounded; open-state prose in a closed row was refused; an underivable branch guessed its first segment. | Applied in `5ea8ee4`: `(?<!\w)#\d+`; refuse >1 MiB; open words only in the last cell, resolved by evidence there; `--branch`, rc 1 "unit could not be derived; pass --unit or --branch", repeated `~N`/`^` stripped. 18 tests rc 0 (red first: 12 failures); corpus 23 pass / 15 fail of 38; A04, A05b, acceptance-frontier lose their open-finding reasons. |
| P3 | Coding standards (P3-4): ≈417 handwritten lines versus the ~300-line unit guide. | Rejected as a split, with the cold reviewer's concurrence: the brief fixed the file set and about half is tests. |

Steering: none, because the doc change is one record-shape paragraph and `AGENTS.md` is untouched.
No-ops: none, because no instruction restates what the code enforces.

## Review and integration disposition (parent, 2026-10-13)

Independent Fable cold review of `894d07d`: **PASS-with-P2** (dead `#N`
alternative in the owner regex; unbounded record read) plus P3s (prose
"pending" in a closed row refused; `--branch` needed for hooks without
`MERGE_HEAD` and a usage error instead of a guessed unit; ≈417 handwritten
lines versus the ~300 guide). All applied in `5ea8ee4` except the budget
finding, rejected as a split with the reviewer's concurrence. Focused
re-review of `82c351f`: **PASS for integration**, no remaining P1/P2; 18 tests
rc 0 (4.9 s), `check` rc 0, baseline 19/19, `tasks validate` rc 0, corpus
23 pass / 15 fail of 38. Provenance note: `5ea8ee4`'s parent is the earlier
merge `0f7ddad`, and its own diff is exactly the five lane files; the planning
files the reviewer saw came from that merge, not from the lane.

| Severity | Finding | Disposition |
| --- | --- | --- |
| P3 | `--branch codex/marketplace-native-onboarding` resolves to the M0 lane record because that record names the integration branch, so a hook run on the integration branch would gate on M0's retro. | Deferred with owner: ticket CT-02 (hook wiring) derives the unit from `MERGE_HEAD` for merges and from the lane record for pushes, and treats the integration branch itself as "no unit"; the M0 record keeps its historical branch field. |

Integrated by the parent: composed-tree gates `tasks validate` 52 rc 0, suite
18 rc 0, `check` rc 0, `check:acceptance-baseline` 19/19 rc 0,
`git diff --cached --check` rc 0, and the live task `./dev/mise run retro:gate -- <unit>`
returned PASSED for all six integrated records (`claude-takeover`,
`m0-remaining-work-merge`, `a06-classification-methods`, `codex-session-history`,
`rf-env-scrub`, `team`) and for this record.
