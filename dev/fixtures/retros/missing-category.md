# fixture retrospective — missing category

Unit: `fixture-missing-category`. Exits: suite rc 0 (4 tests), `tasks validate` rc 0,
`check:acceptance-baseline` rc 0.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: nothing refused a duplicated task row. | Applied: the suite asserts a single row; a mutation made it fail with rc 1. |
| P3 | Navigation: the brief named a path relative to the wrong directory. | Applied: the brief names the absolute path; verified by rerunning the step. |

Coding standards: none, because no judgement rule arose from this unit.
Steering: none, because `AGENTS.md` still points to the protocol unchanged.
No-ops: none, because no instruction restated code behaviour.
Information access: none, because every receipt named its environment.
