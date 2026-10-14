# M0 retrospective — merge of codex/marketplace-remaining-work

Unit: `m0-remaining-work-merge`. Merge commit `e0667ec` (parents `f38b7fe`
and `01952894`) on `codex/marketplace-native-onboarding`. Conflicts resolved
under the user's 2026-10-13 direction: `docs/agents/ticket-retro.md` item 5 kept
HEAD's per-lane barrier; `mise.dev.toml` kept both sides. Composed-tree gates
with the inherited `VIRTUAL_ENV` removed: `tasks validate` 50 tasks rc 0,
`check` rc 0, `check:acceptance-baseline` 19/19 rc 0, `check:research-outcomes`
19 tests rc 0, `check:research` rc 0 (87 `research_refresh` tests, 31 outcome
tests and every `test:*` suite OK), `git diff --cached --check` rc 0, post-commit
`check:acceptance-baseline` rc 0. Independent cold review by a Fable reviewer is
recorded in `progress.md` with its disposition; publication through A09 follows it.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: with the project's own venv exported (which `mise env` does in this checkout), four `dev/research_refresh/test_refresh.py` tests fail — three `launch.call_count 0 != 1` and one `ValueError: Conflicting runtime overrides: VIRTUAL_ENV` — because `runtime_preflight.overrides()` compares the inherited `VIRTUAL_ENV` against each test's temporary project `.venv`. The same failures reproduce in Codex's clean `marketplace-remaining` worktree at `01952894` with both interpreters, so the merge did not introduce them; the branch's receipt recorded 118 passing tests in an environment without the selector. A human following the mise-first mandate hits a red `check` for an environmental reason. | Repair allocated through this barrier as lane `rf-env-scrub` (owner: Opus implementer, reviewer: Fable), paths `dev/check.py`, `dev/research_refresh/test_refresh.py`, `dev/research_refresh/runtime_preflight.py`, `docs/research-feedback.md`: scrub inherited runtime selectors in the harness or accept a selector that resolves to the project's own `.venv`, with a regression test that sets `VIRTUAL_ENV` to a foreign path and to the project path. Until it lands, C1/C2/C3 (which build on this runner) stay held; A06u3 and SKILL are independent and proceed. Verification: `check:research` rc 0 with `VIRTUAL_ENV` exported, recorded in that lane's retro. |
| P3 | Information access: the imported receipt `evidence/research-feedback/checks.json` binds commands and exit codes but not the environment selectors the suite depends on, so a green receipt could not be reproduced here without diagnosis. | Applied in this unit's own receipts: the merge commit message and this record name the removed selector. Routed to the GATE lane as a requirement: the `retro:gate` receipt format records the selector names (`VIRTUAL_ENV`, `UV_PROJECT_ENVIRONMENT`, `MARKETPLACE_PYTHON`) present when a gate ran. Owner: GATE lane; verified by its tests. |
| P3 | Steering: the branch's `docs/agents/ticket-retro.md` still carried the superseded hold-all-dispatch barrier; two authoritative texts had drifted across worktrees. | Resolved by keeping the user-confirmed HEAD text; the NAV lane makes the retro protocol a single source of truth pointed to from `AGENTS.md` rather than restated. Verified: `git grep` finds no conflict markers in `e0667ec`. |

Navigation: none — `git merge-tree --write-tree` located the two conflict
files and the six both-touched paths before the merge, so no path was guessed.
Coding standards: none — no judgement rule arises from a conflict resolution.
Tool economy: applied — the dry-run merge-tree avoided an aborted merge, and
the gate output was filtered to exits and suite summaries instead of full logs.
No-ops: none. All actionable findings are applied or allocated to a named lane
with a verification step; none is deferred without an owner.
