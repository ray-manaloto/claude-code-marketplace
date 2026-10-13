# Issue tracker: GitHub

Specs and tickets for this repository live in GitHub Issues at
`ray-manaloto/claude-code-marketplace`. Use the `gh` CLI from this checkout.
Existing issues remain untouched unless their owner explicitly requests an
update. Pull requests are not a triage request surface.

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
- One implementation writer owns the Git common directory at a time. An
  agent claiming a ticket must verify checkout, branch, HEAD, worktree changes,
  prerequisite receipts, and no active writer before editing. Transfer
  ownership explicitly during a Claude takeover.
- Creating an issue is publication of a plan, not authorization to push a
  branch, merge a PR, modify global tools, or run host-heavy operations.
  Preserve the separate project admission checks.
