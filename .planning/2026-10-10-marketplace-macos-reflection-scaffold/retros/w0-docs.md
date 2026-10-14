# w0-docs retrospective: wave-0 documentation slices (W0-7, CT-02b and CT-23 doc slices)

Unit: `w0-docs` (ticket W0-7 of C4, D15 and D26; documentation slices of CT-02b and CT-23).
Worktree `.claude/worktrees/w0-docs`, branch `claude/w0-docs-rules`, base `c21941f`
(allocated from `d420a7e`). Delivered: `claude-team.md` gains the Integration, Hook
composition and Context budget sections and the Roles restart rule; `ticket-retro.md`
opening paragraph carries the D15 rewrite; `.claude/AGENTS.md` lists the project settings
keys and the marketplaces split; `issue-tracker.md` gains `When a skill says publish /
fetch`; `skill-invocations.md` row 20 and `spec.md` lines 61 and 65 carry their record
corrections. Hook behaviour that does not exist at the base is marked with the ticket it
lands with (CT-02b, CT-16, CT-22).

Exits recorded by the writer: `tasks validate` rc 0 (56 tasks), `check` rc 0,
`check:acceptance-baseline` rc 0 (19/19 hashes PASS), `git diff --check` rc 0; every
cited path resolves and every cited task appears in `./dev/mise tasks ls`. Review: pending
(Fable cold review, owner parent).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P3 | Navigation: `claude-team.md` grew from 95 to 143 lines, so the hook and budget material now sits in a file whose first screen is the roles table. | Deferred with owner parent: split Hook composition and Context budget into their own `docs/agents/` documents behind pointers when CT-22 lands the enforcing hooks; recorded in the ticket ledger at that integration. |
| P3 | Automated checks: the budget numbers (400K, 500K, 550K, 650K) are stated in prose and in `doctor/budget.py:THRESHOLDS` once CT-22 lands, so they can drift. | Deferred with owner CT-22 (`w0-doctor` and `w0-session-hooks`): add a check that the table equals `THRESHOLDS`; until then `claude-team.md` is the source and CT-22 imports from it. |
| P3 | Steering: `.claude/AGENTS.md` caches the `settings.json` key list, which `settings.json` itself answers. | Applied as a cache: the list records which keys are shared versus personal, which the file cannot say; reviewer to confirm the cache is worth its lines. |
| P3 | Information access: `spec.md` and `skill-invocations.md` previously asserted the user typed `/grill-with-docs`, a premise the session transcript contradicts (`T:L21`). | Applied: row 20 and the spec's Further Notes now state the pasted mode; the owned scope allowed row 20 only, so the setup-session rows were folded into row 20's output cell. The parent may split them into rows. |

Coding standards: none, because the change is documentation only and no judgement rule
was added to `CODING_STANDARDS.md`. Tool economy: none, because each file was edited in
one scripted pass and the gates ran once before and once after the tip merge. No-ops:
applied; the `ticket-retro.md` sentence that the skill's standing request is the
invocation authority was removed rather than reworded, and no prohibition stands without
a positive target (`--no-ff`, `retro:gate` by hand, `.mode` absent or `inject-smart`).
