# Handoff template

Hand-written sentences `dev/handoff.py write` preserves; everything else in `## Next Step`, the
NEXT bullet and HANDOFF §1/§7/§8 is regenerated from `dev/handoff.py state`. Edit a section,
run `write --dry-run`, then copy this file to `.agents/skills/session-handoff/references/` (mirror rule).
The `owner` sentence carries no session name and no backticked span: `write` reads the first
backticked span there as the next session's name. `action` leads with the release intake while
one is pending, in the shape "First <R-n>, the release intake (<report path>). Then <work>."
Keep each section short: the block budget is 16 lines of 100 characters; no em-dashes. `notes`
bullets are optional and dropped from the block, in order, when they do not fit (they always stay
here). `state-rows` holds hand-written `| Item | Value |` rows appended to HANDOFF §1; the CLI row reads
"<`claude --version`> installed; the handing-off session ran <version>" (the session-start log's
`cli_version` for this session, else `/status`), and session-resume compares the second version.
There is no `pending-user` section (D167, CT-90): `write` generates the roll-call line (open
request ids, unprojected and unlinked counts) and the `Pending user` line from the `- [ ] R-n`
items of the plan's `## Open requests`; an item awaits the user when it says `owner user`. A
`pending-user` section here makes `write` refuse. Something the user owes becomes an R-n line.

## action
First R-176, the Claude Code 2.1.300 release intake (`reviews/ccm-20261014/cc-2.1.300/README.md`).
Then Wave 0a of Phase 4b: CT-40, the D7 spike, `21-offline` (lane record first), the first CT-80
check (D77, D82, D104). History was replaced (D143, D148): rebase old-history branches, never merge.

## owner
Owner: start with the HANDOFF §8 command (a fresh next-name, D61, D76); rewrite owner line 4 with
dev/handoff.py owner.

## runbook
Runbook: `reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md`.

## notes
- Integrated and published 2026-10-14: gate-git-path (`2185777`) and w0-doctor (`959c56f`) on
  the scrubbed baseline `62b154a`; receipts in `reviews/ccm-20261014/republish/`.
- TR material stays local (D144); `.gitleaks.toml` plus the private rule file (D178,
  `.claude/rules/secret-scanner.md`) guard A09 publish (D145); a plain push is not scanned, so
  publish only through A09. No environment listing under fnox (D146).
- Order: plan Phase 4b (D65, D68-D110; ADR 0005, ADR 0007) from
  `reviews/ccm-20261014/reprioritize-3/Q2-order-v2.md`; decisions through D188.
- Mods replace owned settings hooks except the three deny gates (D102,
  `docs/agents/hooks-and-mods.md`); C++ library with thin bridges (D112, ADR 0008).

## state-rows
| CI | on `959c56f`: development checks, research-fast (2) and acceptance success (17:23:46Z) |
| Claude Code CLI | 2.1.300 installed; the handing-off session ran 2.1.299 |
| `hooks:install` | not run (D2); hk hooks are live through the user's global hk install |
