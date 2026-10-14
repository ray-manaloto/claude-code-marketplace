# Issue #24 retrospective — pinned legacy trackers boundary

Historical local ticket gate: committed `931b536733c668e5bab21b9ebce795f8fccf6051`; GitHub issue remained open at last verification. This retro uses `evidence/legacy-trackers/ticket24-review.md`, `docs/agents/legacy-trackers-boundary.md` and the W4 progress log. Independent read-only review PASS replayed hit/null fixtures in memory against pinned KB source and installed modules; parent checks and 19-file baseline exited 0.

| Severity | Category and finding | Action and verification |
| --- | --- | --- |
| P1 | Automated checks / information access: synthetic hit/null fixtures prove the pinned local dispatch boundary but not live GitHub, fresh Claude SessionStart or OCI acceptance. | Preserve those scopes in the boundary doc. Future #28 owns additive CLI acceptance and an explicitly versioned baseline transition; A12b maps the hosted/OCI expansion. No live pass is inferred. |
| P2 | Navigation: the dependency on an external KB commit and installed modules can be lost during a worktree move. | The boundary doc and review bind commit/tree/module digests; A10 inventory must carry these path-dependent inputs into transfer and verify source-root operation. |

Coding standards, global AGENTS bloat, tool economy and no-op instructions: no additional action. #25 used this pinned prerequisite; #26/#28 remain separate schema and CLI tasks. Their priority stays behind W5's project-owned task interface and the frozen-baseline rule.
