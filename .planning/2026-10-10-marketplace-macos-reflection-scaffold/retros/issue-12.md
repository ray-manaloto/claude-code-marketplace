# Issue #12 retrospective — failed LSan closure

Historical local ticket gate: committed `2cc4c0295d58e6fa857c9f4a1df02dfeebe0630f`; GitHub issue remained open at last verification. This retro uses `evidence/p2996-lsan/ticket12-closure-review.md` and the W4 progress log; it does not rerun the admitted native build. Independent closure review PASS matched 81 retained hashes. The native run exited 1 after the clean LSan witness timed out, so LSan and LSan+UBSan remain unqualified.

| Severity | Category and finding | Action and verification |
| --- | --- | --- |
| P1 | Automated checks / information access: a compiler/link success preceded a runtime deadlock; a generic green build could have hidden the unqualified mode. | Existing closure receipt records the 20-second timeout, runner exit 1, absent owned PIDs and free lease. Issue #13 is the bounded private repair verdict; it must keep negative controls and exact source identity before another native trial. No pass is inferred. |
| P2 | Automated checks: the staged Gitleaks scan exited 1 for six classified hash/path false positives and whitespace check flagged a byte-exact captured diff. A bare exit code would be misleading. | The retained reviewer report names each alert and the immutable diff exception. Future A09 outbound scanning must bind the complete commit/blob set, preserve classified alerts and refuse unknown ones; A09 remains pending. |

Navigation, coding standards, global AGENTS bloat, tool economy and no-op instructions: no new actionable change beyond the existing linked closure and named successor. The review did not rerun native acceptance or all source hashes. Priority remains with W5's portable workflow; #13 waits for fresh host-heavy admission and #12 publication/state reconciliation through A09/A12b.
