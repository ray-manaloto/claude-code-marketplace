# Share refresh outcome safeguards and the improvement workflow

Status: local spec; user confirmed shared scope and test seam on 2026-10-12.
Tracker publication pending qualified project operations; no readiness label applied.

## Problem Statement

Failed-attempt safeguards and their regression checks live only in a private refresh
workflow. Shared development checks cannot protect these lessons, and future
improvements lack a durable, explicit sequence from decisions to verified retro fixes.

## Solution

Share sanitized refresh outcome/receipt behavior beside the existing offline
feedback guard, exercise it through the agreed runner boundary, and document
grill-with-docs → to-spec → to-tickets → implement-spec → retro for future work.

## User Stories

1. As a maintainer, I want shared failed-attempt behavior, so that future callers retain native failures.
2. As a reviewer, I want invalid output rejected after native success, so that exit zero is not sufficient acceptance.
3. As a maintainer, I want comparison failure represented, so that wrappers cannot silently advance baselines.
4. As a reviewer, I want unavailable-runtime represented, so that no query result is implied.
5. As a maintainer, I want accepted state separate from attempts, so that a failure does not replace history.
6. As a reviewer, I want private credentials and paths excluded, so that shared fixtures are safe.
7. As a maintainer, I want existing feedback semantics reused, so that coverage logic is not duplicated.
8. As a reviewer, I want shared checks in the normal development entry point, so that regressions are caught.
9. As a maintainer, I want each improvement specified before implementation, so that its contract is reviewable.
10. As a maintainer, I want ticket blockers approved, so that ownership and sequencing are explicit.
11. As a reviewer, I want every actionable retro finding applied and verified, so that learning changes behavior.
12. As a maintainer, I want partial and published states distinct, so that local success is not mistaken for delivery.
13. As a maintainer, I want existing peer work preserved, so that sharing does not duplicate the unified transport.
14. As a reviewer, I want constrained workflow stages recorded, so that tracker blockers remain visible.

## Implementation Decisions

- Share a dependency-free development outcome contract with synthetic, sanitized fixtures.
- Exercise stage exits, receipt fields, retained evidence and accepted state through one runner boundary.
- Cover native failure, invalid stdout after native success, comparison failure and runtime-preflight failure.
- Reuse existing feedback logic; outcomes neither certify completeness nor compute NEW/GONE.
- Keep private runtime bindings and transport implementation outside the shared contract.
- Document the five-stage workflow in project guidance and the private refresh guide; keep agent steering a short pointer.
- Implement tickets in isolated worktrees, integrate reviewed changes serially, and apply every actionable retro finding before acceptance.
- Publish specs/tickets only through qualified project operations; preserve pending publication honestly.

### Shared contract boundary

- Share pure receipt/state-transition behavior only; do not add a second live
  transport or subprocess runner. Keep runner-boundary integration checks private,
  and drive the shared contract with synthetic observations at that same outcome boundary.
- Keep comparison outcome separate from overall attempt failure. Map comparison
  states to the peer contract: baseline_established, compared, suppressed, unresolved.
  Runtime unavailability means no comparison occurred, not a fifth comparison state.
- Unverified empties map to suppressed with a coverage reason and no NEW/GONE.
  Post-native runtime drift fails at runtime_binding, makes comparison unresolved
  and retains cooldown because a provider stage was invoked.
- Preserve post-cycle exceptions, evidence-before-state ordering and incomplete
  cycle semantics from spec 01. A terminal receipt alone does not commit acceptance.
- Shared evidence references contain confined relative paths and content digests;
  private diagnostic bodies and launch commands never cross into Git. Handwrite
  synthetic fixtures; validate references and reject private absolute path fields.
- Do not duplicate peer-owned workflow authority. Prepare a scoped amendment for
  its owner, with a short local navigation pointer and a separate private guide update.
- The user approved RF3a shared behavior (blocked by RF1/RF2) and RF3b workflow
  guidance (no semantic blockers) as separate tickets. Their scopes stay separate.

## Testing Decisions

- Use highest practical runner boundary with temporary evidence/state and injected external command outcomes.
- Assert exact exits, retained diagnostic references, unchanged accepted state and no unintended invocations.
- Chain failed attempts and subsequent success; reuse current replay-envelope and error-history controls.
- Run focused tests, normal development checks and original acceptance hash checks.
- Obtain independent review and repeat affected checks/review after retro fixes.
- Verify status mapping, incomplete-cycle behavior, and malformed/private evidence
  rejection; test external behavior rather than source-text bans on import names.

## Out of Scope

Private data in Git, copied secrets/transcripts, peer-owned transport changes, new
global skills/hooks, deployment, push/merge, full OCI acceptance and schedule changes.

## Further Notes

Build on the existing isolated feedback branch. This is shared development tooling,
not a replacement for the accepted native C++26 product core.
