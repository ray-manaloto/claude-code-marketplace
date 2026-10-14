# Refresh improvement decisions and proposed tickets

Owner: this task, isolated `codex/research-feedback-retro` integration candidate.
Base: `600130d1a23e429e986e817630af671c84592c3d`.
Status: user approved the four-ticket graph and review decisions on 2026-10-12;
focused re-review completed; its bounded clarifications applied. Tracker publication remains blocked.

The user confirmed all three design/test-seam recommendations on 2026-10-12.
Use [the glossary](../../GLOSSARY.md) and the three linked specs below.
No additional architectural ADR is warranted: these bounded safeguards are reversible.

## Proposed vertical slices

1. **RF1 — Preserve accepted history after comparison failure**
   - Spec: [comparison failure](specs/01-comparison-failure.md).
   - Blocked by: none semantically.
   - Delivers: ordinary/proposal failure exits, retained raw evidence and receipt,
     preserved baseline/history, and a next-success control using the preserved baseline.
   - Acceptance: failure/timeout, proposal isolation, first baseline, subsequent success;
     focused/full checks, independent review and applied retro findings.
2. **RF2 — Stop unavailable borrowed runtimes before research launch**
   - Spec: [runtime preflight](specs/02-runtime-preflight.md).
   - Blocked by: none semantically; serialize edits with RF1 because both touch the private runner.
   - Delivers: bounded exact-runtime imports, retained unavailable-runtime receipt,
     zero fnox/provider calls on failure, and healthy/failed native controls.
   - Acceptance: SSL/SDK/timeout/healthy cases, state preservation, focused/full checks,
     independent review and applied retro findings.
3. **RF3a — Share verified refresh outcome behavior**
   - Spec: [shared outcomes](specs/03-shared-outcomes.md).
   - Blocked by: RF1 and RF2; shared behavior is bound to their reviewed contracts.
   - Delivers: sanitized pure outcome contract/fixtures integrated with feedback
     checks, compatible comparison vocabulary, and verified retro closure.
   - Acceptance: native failure, invalid JSON, comparison/runtime failures, recovery,
     normal checks and baseline preservation; independent review and retro re-review.
4. **RF3b — Document the standing improvement workflow**
   - Spec: [shared outcomes and guidance](specs/03-shared-outcomes.md).
   - Blocked by: none semantically.
     Parent serializes its private guide application with RF1/RF2.
   - Delivers: short project pointer, staged amendment for the peer's existing
     workflow authority, and this task's private five-stage guide.
   - Acceptance: working navigation, exact ownership/publication boundaries,
     independent documentation review and applied retro findings.

## Ownership and publication

The user approved Fable's split into RF3a shared outcomes (blocked by RF1/RF2)
and RF3b standing guidance (no semantic blockers). RF3b drafts an amendment for the
peer-owned authority instead of copying or overwriting its guidance.

The protected peer owns A01/A05b and public GitHubKit transport. These tickets
cover the private refresh integration and sanitized reuse only. Parent-owned
planning in the protected checkout remains unchanged.
Each implementation ticket gets an isolated worktree and explicit scope;
the parent coordinates private-runner writes and reviewed integration.
Private files are outside Git: implement RF1/RF2 on frozen scratch copies, bind
their preimage/postimage hashes and test receipts, then let the parent serialize
guarded application to the live workflow. A Git worktree alone cannot isolate
those files. Private changes are applied/verified, never described as committed
or integrated; only sanitized shared artifacts have those Git states.
Before each private edit preserve runner, tests and guide preimages in the
ticket's unique evidence directory. Shared receipts exclude private diagnostic
bodies, credentials and machine paths. Each final scope stays near five
maintained files and 300 handwritten lines; split further if necessary.

GitHub is the configured tracker. Its qualified A07/A08 mutation commands are
not yet available. These files are unpublished review drafts, not substitute
GitHub issues or verified native blocking links. Hold readiness labels and
record the publication blocker until those operations are qualified.

## Standing sequence to document in RF3

For every improvement: grill-with-docs → to-spec → to-tickets → implement-spec → retro.
Confirm decisions/test seams, approve ticket granularity and true blockers,
implement/test/review in isolated lanes, then apply and verify every actionable
retro finding. Repeat review/retro after material fixes. Record constrained
stages and keep implemented, tested, reviewed, committed, integrated and published distinct.
