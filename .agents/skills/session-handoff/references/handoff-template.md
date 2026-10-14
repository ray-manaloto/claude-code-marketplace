# Handoff template

Hand-written sentences `dev/handoff.py write` preserves; everything else in `## Next Step`, the
NEXT bullet and HANDOFF §1/§7/§8 is regenerated from `dev/handoff.py state`. Edit a section,
run `write --dry-run`, then copy this file to `.agents/skills/session-handoff/references/` (mirror rule).
Keep each section short: the block budget is 16 lines of 100 characters; no em-dashes. `notes`
bullets are optional and dropped from the block, in order, when they do not fit (they always stay
here). `state-rows` holds hand-written `| Item | Value |` rows appended to HANDOFF §1.

## action
Integrate w0-doctor (`f1bbc8d`) as reviewed per HANDOFF §2(b) (D101); then wave 0a of Phase 4b:
CT-40, the D7 spike, `21-offline` (lane record first), the first CT-80 check. Before publication
run only waves pre to 0c and the gate row (D77, D86, D104); later rows wait for the typed stages
(D90).

## owner
Owner: start as `ccm-20261014T034212.915972000-05` (D61 format, D76; HANDOFF §8);
rewrite owner line 4 with `dev/handoff.py owner`.

## pending-user
Pending user: Q2-order-v2 §6 U1-U5 (CT-63a one unit or split, D109; Q83 gate scripts and D60;
#13 fallback after R4; Q82 D99 and the remote switch; `delivery:publish` on CT-18), HANDOFF
§2(f); the typed stages at the gate (HANDOFF §2(j), D90).

## runbook
Runbook: `reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md`.

## notes
- Order: plan Phase 4b (D65, D68-D110; ADR 0005, ADR 0007) from
  `reviews/ccm-20261014/reprioritize-3/Q2-order-v2.md`; grill answers D63-D110.
- Mods replace owned settings hooks except the three deny gates (D102,
  `docs/agents/hooks-and-mods.md`); CT-80 watches upstream; w0-session-hooks closed (D97).
- Imports: TR CT-41..CT-58 (D81); project import CT-59..CT-79 (D87, D88); CT-80 (D102),
  CT-81 (D106); D85 approved the splits and merges; this repository owns the host lock (D109).
- Grill rounds 3-5 answered (D83-D110; `reviews/ccm-20261014/grill-round3-questions.md`): absorb
  and sunset dotfiles, knowledge-base and TR (ADR 0006); research mirrors to `/offline/`.

## state-rows
| CI | research-fast `38510694690` on `21af5650`: success (04:19:59Z) |
| Claude Code CLI | 2.1.299 (X3 §5 G6); X1's review targets 2.1.296 notes and applies |
| `hooks:install` | not run (D2); hk hooks are live through the user's global hk install |
