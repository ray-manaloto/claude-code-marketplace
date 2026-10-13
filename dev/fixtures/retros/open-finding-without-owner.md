# fixture retrospective — open finding without owner

Unit: `fixture-open-finding-without-owner`. Exits: suite rc 0 (4 tests), `tasks validate` rc 0,
`check:acceptance-baseline` rc 0.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: suite rc 0, yet nothing refused a duplicated row. | Pending: add an assertion for a single row. |
| P3 | Navigation: the brief named a path relative to the wrong directory. | Applied: the brief names the absolute path; verified by rerunning the step. |

Coding standards: none, because no judgement rule arose from this unit.
Steering: none, because `AGENTS.md` still points to the protocol unchanged.
Tool economy: none, because output was filtered to exits and summaries.
No-ops: none, because no instruction restated code behaviour.
Information access: none, because every receipt named its environment.
