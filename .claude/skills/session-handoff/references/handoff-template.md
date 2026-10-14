# Handoff template

Hand-written sentences `dev/handoff.py write` preserves; everything else in `## Next Step`, the
NEXT bullet and HANDOFF §1/§7/§8 is regenerated from `dev/handoff.py state`. Edit a section,
run `write --dry-run`, then copy this file to `.agents/skills/session-handoff/references/` (mirror rule).
Keep each section short: the block budget is 16 lines of 100 characters; no em-dashes. `notes`
bullets are optional and dropped from the block, in order, when they do not fit (they always stay
here). `state-rows` holds hand-written `| Item | Value |` rows appended to HANDOFF §1.

## action
Wave 0a of Phase 4b: CT-40, the D7 spike, `21-offline` (lane record first), the first CT-80
check (D77, D82, D104). History was replaced (D143, D148): rebase old-history branches, never merge.

## owner
Owner: start as `ccm-20261014T034212.915972000-05` (D61 format, D76; HANDOFF §8);
rewrite owner line 4 with `dev/handoff.py owner`.

## pending-user
Pending user: GitHub Support purge request (`reviews/ccm-20261014/republish/`); file the
guard and C++ check tickets; Q2-order-v2 §6 U1-U5; typed stages (HANDOFF §2(j), D90).

## runbook
Runbook: `reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md`.

## notes
- Integrated and published 2026-10-14: gate-git-path (`2185777`) and w0-doctor (`959c56f`) on
  the scrubbed baseline `62b154a`; receipts in `reviews/ccm-20261014/republish/`.
- TR material stays local (D144); `.gitleaks.toml` guards A09 publish (D145); a plain push is
  not scanned, so publish only through A09. No environment listing under fnox (D146).
- Order: plan Phase 4b (D65, D68-D110; ADR 0005, ADR 0007) from
  `reviews/ccm-20261014/reprioritize-3/Q2-order-v2.md`; decisions through D149.
- Mods replace owned settings hooks except the three deny gates (D102,
  `docs/agents/hooks-and-mods.md`); C++ library with thin bridges (D112, ADR 0008).

## state-rows
| CI | on `959c56f`: development checks, research-fast (2) and acceptance success (17:23:46Z) |
| Claude Code CLI | 2.1.299 (X3 §5 G6); X1's review targets 2.1.296 notes and applies |
| `hooks:install` | not run (D2); hk hooks are live through the user's global hk install |
