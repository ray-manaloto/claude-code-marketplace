# Brief: w0-doctor-records (implementer, sequenced)

LANE-UNIT: w0-doctor-records. Role: implementer (`.claude/agents/implementer.md`), Opus high, `tdd` preloaded.
Shorthand: ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace, P=ROOT/.planning/2026-10-10-marketplace-macos-reflection-scaffold, RV=P/reviews/ccm-20261013, C3/C4=RV/prevention/C{3,4}-*.md.
Tickets: CT-22 (CT-22a part 2, pending issue); C4 §Minimal wave-0 set row W0-4 (`lanes` minimal, `agents` mtime roster) and W0-2 (lane fixtures); C4 required change 2.
Precondition: w0-doctor and w0-decisions are integrated. The merger fills `<CUT>` below: the commit `docs: allocate lane w0-doctor-records` that updates P/lanes/w0-doctor-records.json (`allocated_from` = the tip it was cut from) and from which the worktree is cut.
Record: P/lanes/w0-doctor-records.json (parent-only, D8). Worktree ROOT/.claude/worktrees/w0-doctor-records, branch `claude/w0-doctor-records-detectors`, base `<CUT>`. Run `./dev/mise run tools:prepare && ./dev/mise run deps:sync` once if the merger did not.
Env: `export PWF_PLAN_ROOT=ROOT PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold; unset VIRTUAL_ENV`. Context ceiling 500K (D29/D30).
Owned: `dev/doctor/lanes.py`, `dev/doctor/agents.py`, `dev/test_doctor_records.py`, `dev/fixtures/doctor/lanes/`, `dev/fixtures/doctor/agents/`, P/retros/w0-doctor-records.md, P/ledger-w0-doctor-records.jsonl.
Never: the other `dev/doctor/*.py` and `dev/test_doctor.py` (w0-doctor's; use the core contract as built: `run(ctx)`, `SURFACES`, optional `context_lines(ctx)`), `mise.dev.toml`, `.claude/settings.json`, `hk.pkl`, `dev/check.py`, `dev/hooks/`, `dev/retro_gate.py`, `docs/agents/`, lane records (live ones included).

## Items and acceptance (red test first; cite the C3 id)
1. lanes.py (C3 §B :174-240, minus handoff and plan-table rows, which are CT-15/CT-22b): `B.status-stale`, `B.review-missing`, `B.retro-claim-unverified` (retro_gate subprocess, check surface only, 2 s per unit), `B.base-sha-off-by-one` with the fixed predicate (C4 change 2): allocation = newest first-parent commit whose subject is `docs: allocate lane <unit>` and touches the record, else the commit that added the record; assert `base_sha == allocation` and `allocated_from == allocation^`. A record whose status starts with `allocated` and whose `base_sha` is null is info, not a finding (the wave-0 records are written that way).
2. Tests: `test_lanes_base_sha_off_by_one` (fixture built so the vacuous form, "first commit of base..branch has parent base", passes while the fixed predicate fails; record `e618243`-shaped vs allocation `2d1f60e`-shaped), `test_lanes_base_sha_allocate_subject_form`, `test_lanes_allocated_null_base_is_not_a_finding`, `test_lanes_stale_status_while_merge_head_is_lane_tip` (status-stale + review-missing), `test_lanes_publication_pending_but_on_origin`, `test_lanes_retro_passed_but_gate_fails` (a06-unit3 shape), `test_lanes_clean_record_no_findings`.
3. agents.py (C3 §F :395-435, mtime form only): `F.agents-not-offered` when a `.claude/agents/*.md` is newer than the session's first transcript line on `resume|compact|clear`; the `agents:` roster line from frontmatter names. Tests `test_agents_created_after_session_start_flagged`, `test_agents_roster_line_lists_frontmatter_names` (clean twin, no finding).
4. Fixtures under `dev/fixtures/doctor/{lanes,agents}/`: shapes only (the staged gate-hooks record, a06-unit3), scratch repos built in the test like `dev/test_hooks.py:Scratch`. No `--fix` (CT-22b).
5. Live tree: run `python3 -I dev/doctor/cli.py --surface check --json` on the merged tip. Any B.* P1/P2 on today's records is a parent correction: list each as a literal JSON edit in the receipt; never edit a lane record. `check` must reach rc 0 after those parent edits; say whether it does before them.
Size: about 110 handwritten lines in two modules, <= 80 per file.

## Gates (expected rc 0 each; record actual rcs)
`python3 -I -m unittest discover -s dev -p 'test_doctor*.py' -v`; `./dev/mise run test:doctor`; the live `--surface check --json` run (rc and findings); `./dev/mise tasks validate`; `./dev/mise run check`; `./dev/mise run check:acceptance-baseline`; `./dev/mise run test:hooks`; `hk validate`; `git diff --check`; `./dev/mise run retro:gate -- w0-doctor-records`. Never `check:research`, push or publish.

Before reporting, merge the current integration tip (`codex/marketplace-native-onboarding`) into your branch, rerun the gates on the merged bytes, commit, `git status` clean. Draft the retro per `docs/agents/ticket-retro.md`.
Trailers: `Co-Authored-By: Claude <your model and version> <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_015qxgfYywpRPVMk8tYDLCHT`.
Receipt (<= 300 words): branch, final SHA, tip merged, changed paths (a subset of owned), each command with its rc, live findings with proposed record edits, deviations, unverified items, retro path.
