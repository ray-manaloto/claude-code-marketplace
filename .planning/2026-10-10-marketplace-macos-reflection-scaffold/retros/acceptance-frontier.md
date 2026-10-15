# Accepted acceptance-frontier correction

Status: independently reviewed, then explicitly accepted by the user on
2026-10-13 with “Apply the reviewed correction (Recommended)”. This changes
local prerequisite and hold scope only. No issue body, GitHub dependency edge,
runtime admission or completion state changes by this decision alone.

The parallel contract specialist found two P1 scheduling contradictions:

1. The published [#30 dependency receipt](../ticket-publication.json) requires
   #28, while the [#28 retro](/Users/rmanaloto/.codex/worktrees/issue-28-cli-contract/claude-code-marketplace/.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/issue-28.md)
   requires a real public Issues implementation supplied downstream by #30.
   Requiring full ticket closure in both directions prevents either gate.
2. The [active plan](../task_plan.md) pauses A06 until retrospective actions
   clear, while [A12b](../automation-amendment-draft.md) depends on A06 and owns
   routing #28's versioned baseline transition. Treating that future routing
   as necessary to clear A06's hold creates another cycle.

## Exact accepted disposition

| Boundary | Accepted prerequisite | Gates that remain mandatory |
| --- | --- | --- |
| #28 to #30 | Accept the reviewed offline v2 dispatch/help/isolation seam as the specific prerequisite milestone after source integration and its own review/checks. | Keep #28 partial/open until real public v2 and fresh Claude/OCI acceptance; #30 still needs its other native/schema/transport prerequisites. |
| #28 baseline routing | Permit a bounded local baseline-transition design/review independently of A06/A12b assembly. | Preserve all original baseline receipts; any changed accepted baseline requires explicit versioned review before application. |
| A06 retrospective hold | Once actionable defects in completed units are applied and verified, let externally blocked future runtime gates hold only their actual dependents. | Retain their exact failures, partial ticket status and runtime admissions. A12b still waits for A06's own gate. |
| #29 offline versus live | Accept only its reviewed offline bridge measurement as evidence for dependent design. | Live provider, fresh confined install, cancellation and native-caller acceptance stay pending. |

This accepts a correction to scheduling and admission scope, not permission to
claim runtime success, drop tests, close tickets, promote an installed runtime,
change credentials/billing or bypass the qualified tracker operations. No
GitHub mutation is part of the accepted local disposition. Any subsequent
ticket/edge amendment uses the existing exact-preimage operation and separate
verification. The offline #28 milestone must be named explicitly rather than
pretending GitHub's current ticket-level blocker already represents it.

## Parallelism and verification

The existing [publication/hold rule](../../../docs/agents/ticket-retro.md)
already lets independent reviewed units proceed. Feedback-helper integration
and the #13 offline cancellation repair were already independently authorized.
Keep one implementation/Git writer, parallel read-only specialists and a fresh
reviewer in a freed slot. Native/OCI work still needs current capacity and its
specific admission. No evidence supports running several host-heavy gates at once.

Independent review found no remaining material findings in these dispositions;
the user's subsequent decision authorized changing the earlier hold. The parent
applies this decision to the active source plan and accepted workflow amendment,
preserving historical snapshots. This coherent documentation unit uses six
maintained files to keep the decision, plan, amendment and team record aligned.
Mechanical source and test defects use existing checks. Scheduling scope is a
judgement decision; adding a linter would not settle its authority.

Navigation: source authority remains explicit. Automated checks: no missing new
mechanical check established in this bounded frontier review. Coding standards:
keep final review responsible for contract preservation. Global instructions
and no-op guidance need no new rules. Tool economy: reuse immutable passing
offline receipts until inputs change; no quota retries as a substitute for a
dependency decision. Information access: the exact source/receipts resolved
both cycles without broader credentials or global access.
