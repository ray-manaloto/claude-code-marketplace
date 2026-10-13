# Publication scope retrospective

The user had already authorized pushing the integration branch in item 16 of
the supplied workflow request. Source-root HEAD `8fededab` nevertheless had
13 local commits beyond the last recorded remote `111424b0`: reviewed retro
archives, the retro protocol and status updates. The parent carried the #13
native acceptance hold across independent completed source documentation.

| Severity | Finding | Applied action and verification |
| --- | --- | --- |
| P1 | Workflow judgement: an incomplete native gate was treated as a branch-wide publication hold despite existing authorization. | Parent clarified hold scope in `docs/agents/ticket-retro.md` and selected this source branch for the existing A09 delivery gate. Publication must bind the exact tree and outbound history, pass named checks and secret scans, and verify the remote SHA. The gate's result is recorded separately from this pre-publication review. |

Navigation: the active source plan and qualified `delivery:*` tasks already
identify the correct checkout and route. Automated checks: A09 already checks
identity, exact tree, named checks, hooks, outbound secrets and remote postimage;
the missing step was invoking it, so no duplicate gate is added. Coding
standards: this is scope judgement recorded in the existing workflow document.
Global AGENTS.md and no-op instructions: no change warranted. Tool economy:
reuse the existing gate and reviewer receipts. Information access: the original
authorization was available and is now reconciled with the current hold.

This delivery excludes detached #13/#28/#29 code and the separate
research-feedback-retro handoff. Their integration and acceptance remain
separate. #13 is inconclusive; its new native control has not run. Publishing
these records does not complete those tickets or authorize a force-push, merge,
release, new remote branch or marketplace publication. Independent review and
the named publication gate must settle this selected unit before it is reported
published.
