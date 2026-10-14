# w0-doctor retrospective (CT-22a part 1; W0-1, W0-4 core, W0-5, W0-2 settings fixtures)

Unit: `w0-doctor`. Branch `claude/w0-doctor-core`, base `c21941f`, implementation commit `bb0e2a4`;
integration tip `c21941f` merged (already an ancestor, "Already up to date", rc 0). Draft by the
implementer; independent review and the retro-writer pass are still pending.

Exits on the lane bytes: `python3 -I -m unittest discover -s dev -p 'test_doctor*.py' -v` rc 0 (12 tests);
`./dev/mise run test:doctor` rc 0; `python3 -I dev/doctor/cli.py --surface check --json` rc 0 (0 findings);
`./dev/mise tasks validate` rc 0; `./dev/mise run check` rc 0; `./dev/mise run check:acceptance-baseline`
rc 0 (19 baseline files); `./dev/mise run test:hooks` rc 0 (15 tests, HkHooks ran, not skipped);
`hk validate` rc 0; `git diff --check` rc 0. Negative control: a `permissions` key in the project file
made `./dev/mise run check` exit 1 (doctor rc 2). Latency on this worktree: session-start 369-396 ms
(budget 3,000), pre-commit 204-237 ms (target < 300).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: Git through the mise shim costs ~170 ms per call, so the C3 300 ms pre-commit budget would turn the settings guard into a silent `skipped` under load (and make T-B5 flaky). | Applied: `cli.py` finds the toplevel without Git, the header uses one `rev-parse`, `settings.py` declares a 1,000 ms pre-commit budget. Verified: pre-commit 204-237 ms, `test:hooks` rc 0. |
| P2 | Information access: the brief's "exactly 1 + 4" for the staged `e12cf04` shape is not derivable; that file has no `extraKnownMarketplaces`, so all 6 plugin marketplaces are undeclared. The "4" is the `before-ct02` count (C3 :926). | Applied: `test_settings_personal_keys_flagged` asserts the exact sets for both fixtures (1 + 6 and 6 + 4); reported to the parent as a deviation in the handoff. Suite rc 0. |
| P2 | Information access: the test environment inherited the user's `XDG_CONFIG_HOME` global ignore (`**/.claude/settings.local.json`), which hid `I.settings-local-not-excluded`. | Applied: `dev/test_doctor.py` points `XDG_CONFIG_HOME` at the scratch home; the test failed before and passes after (rc 0). |
| P3 | Automated checks: C3's foreign-hunk predicate (index blob not in HEAD or MERGE_HEAD) flags every clean auto-merge of a file both sides changed. | Applied: `integration.py` also accepts the `git merge-tree --write-tree` blob; the lane fixture is such an auto-merge, and removing the merge-tree set failed 2 tests (mutation), restored rc 0. |
| P3 | Coding standards: `test_session_start_context_block_shape` passed on first run (the block renderer landed with the exit-code slice) and `test_live_project_settings_hold_wave0_keys` pins keys already committed. | Applied: mutation check, integration `CONTEXT_RANK` 0 -> 90 failed the block test, restored rc 0; T-A6 is recorded as a regression pin, not a red-first test. |
| P3 | Steering: `docs/agents/claude-team.md` does not yet say that SessionStart runs the doctor and that hk pre-commit runs `check:records`. | Assigned to the parent (cross-scope, owned by w0-docs); the literal sentence is in the handoff receipt. |
| P3 | Information access: the repo already has hk hooks installed, so the new pre-commit `records` step ran on this lane's own commit (`check:records` passed). It will be live in every worktree whose `hk.pkl` carries it once integrated. | Rejected as a change request: no edit needed, `check:records` rc 0 on the tip; noted for the parent in the handoff. |

Coding standards: none beyond the row above, because no new judgement rule arose.
Navigation: none, because the brief's absolute paths and C2/C3/C4 line anchors resolved directly.
Tool economy: none, because every gate wrote to a scratch file and only the rc and summary line were read.
No-ops: none, because no instruction restated code behaviour.
