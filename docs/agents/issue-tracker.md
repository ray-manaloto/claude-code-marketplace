# Issue tracker: GitHub

Specs and tickets for this repository live in GitHub Issues at
`ray-manaloto/claude-code-marketplace`. Use the `gh` CLI from this checkout.
Existing issues remain untouched unless their owner explicitly requests an
update. Pull requests are not a triage request surface.

## Standing improvement workflow

Use grill-with-docs → to-spec → to-tickets → implement-spec → retro. Retain each
stage's decisions, evidence and actual completion status; approved design and
test seams precede implementation. Reuse inherited skills and existing checks.
Implement small dependency-aware units under the [ownership rule](codex-task-orchestration.md#ownership),
preserving exact preimages and actual exits. Independent final code review checks
correctness and accepted-contract preservation. The [retro gate](ticket-retro.md)
controls acceptance and new-ticket dispatch.

This workflow grants no additional ownership, runtime, credential, research,
tracker-publication or shipping authority. Publish specs and tickets only through
the qualified project operation; missing qualification means local drafts with a
named blocker. A staged amendment or published plan is not source-owner approval
or execution readiness.

## Qualified tracker operations

- Read issues with `gh issue view` and `gh issue list`. For approved new
  sub-issues, use the named `issue:create-preview`, `issue:create-apply`, and
  `issue:create-verify` tasks with their SHA-bound manifest and journal.
  Ambiguous creation is verify-only; preserve the parent and local-ID binding.
- Publish approved blocker edges with `issue:new-edge-preview`,
  `issue:new-edge-apply`, and `issue:new-edge-verify`, then run
  `issue:new-edges-audit`. Check the full existing and new dependency map
  before reporting the graph complete. An ambiguous attempt is verify-only.
- For an authorized body or label update, use `issue:preview`, `issue:apply`,
  and `issue:verify` with exact files and a fresh preimage. Add
  `ready-for-agent` only after the approved dependency map is verified;
  an open blocker still gates execution. Issue creation, publication or a
  label never closes a ticket: acceptance receipts and review control closure.
  Keep planned, implemented, tested, reviewed, committed and published states
  distinct.
- Before claiming a ticket, verify checkout, branch, HEAD, worktree changes,
  prerequisite receipts and the explicit allocation under the
  [ownership rule](codex-task-orchestration.md#ownership). Transfer ownership
  explicitly during a Claude takeover.
- Creating an issue is publication of a plan, not authorization to push a
  branch, merge a PR, modify global tools, or run host-heavy operations.
  Preserve the separate project admission checks.
