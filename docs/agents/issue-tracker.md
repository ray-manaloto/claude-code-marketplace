# Issue tracker: GitHub

Specs and tickets for this repository live in GitHub Issues at
`ray-manaloto/claude-code-marketplace`. Use the `gh` CLI from this checkout.
Existing issues remain untouched unless their owner explicitly requests an
update. Pull requests are not a triage request surface.

- Create/read/list issues with `gh issue create`, `gh issue view`, and
  `gh issue list`. Use a body file for multiline content.
- Publish one approved spec issue. Publish its approved tracer-bullet tickets
  as sub-issues using `gh issue create --parent <spec-number>`.
- Record genuine blockers with `gh issue create --blocked-by <issue-numbers>`
  or `gh issue edit <number> --add-blocked-by <issue-numbers>`. Check
  `gh issue view <number> --json blockedBy,blocking` before claiming a
  frontier ticket. If native dependencies are unavailable, include
  `Blocked by: #...` in the ticket body and verify open blocker states.
- A ready ticket carries `ready-for-agent`. Do not mark a ticket complete
  until its acceptance receipts and review disposition are recorded. Keep
  planned, implemented, tested, reviewed, committed, and published states
  distinct.
- One implementation writer owns the Git common directory at a time. An
  agent claiming a ticket must verify checkout, branch, HEAD, worktree changes,
  prerequisite receipts, and no active writer before editing. Transfer
  ownership explicitly during a Claude takeover.
- Creating an issue is publication of a plan, not authorization to push a
  branch, merge a PR, modify global tools, or run host-heavy operations.
  Preserve the separate project admission checks.
