# Issue #25 retrospective — Python bridge placement

Historical local ticket gate: committed `54d34c8b8d5636614f772f628e705f9eb93c5ac6`; GitHub issue remained open at last verification. This retro uses `evidence/python-bridge/ticket25-review.md`, `docs/agents/python-bridge-placement.md` and the W4 progress log. Reviewer PASS checked ten successful samples, two deliberate exit-42 failures and protocol replay; parent checks and 19-file baseline exited 0.

| Severity | Category and finding | Action and verification |
| --- | --- | --- |
| P1 | Automated checks: the in-process candidate was a Python proxy, not a compiled C++ embed; warm synthetic medians do not qualify production latency, ownership or cancellation. | Preserve the helper choice as reversible initial placement. Future #30 must prove typed child-process mapping, nonzero/malformed/timeout failure propagation and rollback; #29 separately measures Context7 bridge. No C++ or production performance claim is made. |
| P2 | Information access / navigation: the child path depends on the installed CLI/runtime and a private synthetic `gh` stub. | The placement doc links its exact source and measurement; A10 must inventory path-dependent inputs before transfer, and A12b must route fresh-session/OCI acceptance. |

Coding standards, global AGENTS bloat, tool economy and no-op instructions: no additional actionable finding. #29/#30 remain downstream of their published graph prerequisites; W5 search/task work does not substitute for their native tracer gates.
