# rf-env-scrub retrospective — research_refresh harness and inherited selectors

Unit: `rf-env-scrub`, the bounded repair allocated through the retro barrier
of [M0](m0-remaining-work-merge.md) (finding P2). Worktree
`.claude/worktrees/rf-env-scrub`, branch `claude/rf-env-scrub-inherited-selectors`,
repair commit `716e888` on base `e0667ec`, merged with `8c5656f` as `281a198`
(5 files, +49/−3). Defect: with `VIRTUAL_ENV=<repo>/.venv` exported — which
`mise env` does in this checkout — four `dev/research_refresh/test_refresh.py`
tests failed because `runtime_preflight.overrides()` compared the inherited
selector against each test's temporary project `.venv`; reproduced first in the
worktree (rc 1, 3 failures + 1 error) and in the root checkout at `f039041`.

Repair, test-first: `runtime_preflight.INHERITED` (the selector names plus
`VIRTUAL_ENV`, `UV_PROJECT_ENVIRONMENT`, `UV_NO_CONFIG`) and `scrubbed(environment)`;
`test_refresh.py` setUp runs with a scrubbed copy of `os.environ`; new tests
prove a foreign `VIRTUAL_ENV` is still refused at the product boundary without
a launch, the scrubbed harness launches exactly once with the project `.venv`,
and a symlink resolving to the project `.venv` is accepted; `dev/check.py`
runs discovered suites with `scrubbed(os.environ)` (bytecode writes off);
`docs/research-feedback.md` states the contract in two sentences.
`overrides()`, `native_environment()` and `refresh.py` are unchanged.

Exits recorded by the implementer: 89 `research_refresh` tests rc 0 with
`VIRTUAL_ENV` unset, exported to the project `.venv`, and exported to a foreign
temp path; `tasks validate` 50 rc 0; `check` rc 0 with the project venv
exported (before and after the merge); `check:research` rc 0 in all three
modes after `tools:prepare`/`deps:sync`; `check:acceptance-baseline` 19/19
rc 0; `git diff --check` rc 0. Independent Fable cold review: **PASS-with-P3**
— scope exact, product behaviour preserved (patch-id of the repair equals the
merge delta), `check.py` coupling acceptable (one function, loud `ImportError`,
no bytecode), hermeticity confirmed with extra `UV_*` probes, before/after
established on the root checkout; reviewer exits 89/89/89 rc 0, `check` rc 0
with the venv exported, validate rc 0, baseline 19/19, diff-check rc 0.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: the imported harness inherited the developer's shell selectors, so the mise-first gate went red for an environmental reason. | Applied: harness and `check.py` scrub inherited selectors; regression tests cover foreign, project and symlink cases. Verified by the exits above and the reviewer's rerun. |
| P3 | Information access: the lane brief assumed `check:research` runs in a fresh worktree, but it needs `tools:prepare` and `deps:sync` first; `mise env` also resets `VIRTUAL_ENV` inside tasks, so the foreign-selector case is proven by the direct unittest run, not by the mise task. | Applied by the parent: lane briefs now say to prepare worktree tools before `check:research` (recorded in the workflow memory and the implementer brief template); the direct run is the receipt for the foreign case. |
| P3 | Navigation: the handoff named tip `8c5656f` while the integration branch had moved to `f039041`; `merge-tree` was clean and the owned paths were untouched, so no re-merge was needed. | Applied: the parent records the actual tip at integration; lane records carry `merged_head`. |
| P3 | Coding standards: `check.py` importing a research module is a judgement call. | Reviewer's call: acceptable as is; no duplicate selector list. No rule added. |

Steering/global guidance: none — no instruction file changed; the contract
sentences live in the research-feedback doc the runner already points to.
Tool economy: applied — logs went to the scratchpad and only exits and
summaries were read. No-ops: none. All actionable findings are applied; the
reviewer's observation that `scrubbed()` also strips `PYTHONHOME` needs no
action because `native_environment` already refuses it. With this repair
integrated, lanes C1, C2 and C3 are released from the M0 barrier.
