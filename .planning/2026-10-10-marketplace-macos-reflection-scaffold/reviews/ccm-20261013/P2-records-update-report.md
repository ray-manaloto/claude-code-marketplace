# P2: progress, findings and ledger update (plan-update team, 2026-10-13)

Writer: P2 of session `ccm-20261013-check`. Scope: `P/progress.md`, `P/progress-archive-2026-10-13.md`
(new), `P/findings.md`, `P/ticket-ledger.md`, this report. No Git state was changed: HEAD `9cd396a`,
`MERGE_HEAD e12cf04` and the 11 staged paths were checked before and after the edits. `task_plan.md`
was not touched (P1 owns it). Pre-update copies: `plan-backups/{progress,findings,ticket-ledger}.pre-update-20261013.md`.

## Changes per file

| File | Before | After | What changed |
|---|---|---|---|
| `P/progress.md` | 3,429 lines, 246,501 B | 431 lines, 29,764 B | Former lines 1–3026 moved to the archive. Lines 3027–3419 (the last 39 top-level entries: 17 Codex-era, 22 Claude-era) kept verbatim under one heading. A one-line archive pointer added below `# Progress`. One new dated entry for this review appended. The NEXT bullet rewritten as the last bullet (10 lines). |
| `P/progress-archive-2026-10-13.md` | — | 3,046 lines, 220,112 B | 6-line header, then former lines 1–3026 verbatim. The superseded NEXT bullet (former lines 3421–3429) is appended under its own heading. |
| `P/findings.md` | 56 lines, 3,473 B | 200 lines, 15,525 B | "Inherited limitations": the research paragraph now states the narrowed strict-five gap (`firecrawl-search` provisional only) and cites the three manifests (R3 P2-3). "Claude takeover": the stale "Unpublished local tip / A06 unit3 uncommitted" bullet is replaced by T2's three bullets, extended with the A06 schema and corpus paths, sizes and SHA (R3). Added: the `01a13185` footprint (c658 239 KB schema, `~/.codex/config.toml`, unversioned `~/.codex/skills`, ticket 30), the sweep A inventory pointer, the `codex/28\|29-offline-refresh` absorption and the codex-briefs pointer. New section "Session review ccm-20261013 (2026-10-13)": the 14 root-cause classes with pointers, the two environment facts, the mattpocock invocation constraint, sweeps A, B and C (with the supersession notice and the "mid-turn" sentence quoted verbatim), the active Codex automation, the fnox posture (N1) and the pwf hazards. |
| `P/ticket-ledger.md` | 104 lines, 19,159 B, 98 issue rows | 164 lines, 35,622 B, 98 issue rows + 25 CT rows + 17 closure rows | New snapshot line: tip `9cd396a`, remote `28fedf1`, `MERGE_HEAD e12cf04`, date, GitHub-column provenance. Lane and local-state columns corrected for 29 rows (#62–#82, #90–#95, #97, #101); the first six (tracker) columns are unchanged in all 98 rows (verified by diff against the backup). New table of CT-01…CT-24 plus CT-02b (25 rows). New sub-table "Closure prerequisites (#62–#78, sweep B)" (17 rows). New "T4 state (#79–#82, #101)" paragraph. |

Ledger row corrections in detail:
- #69 is "published `f250f75`", ancestry verified (`361688e` ⊂ `f250f75`). The retained corpus and schema exist only in `2a14`; T2's CT-21 import wording replaces "retained-corpus consumption still open"; no closure inventory exists.
- #94: the state that sat in the Lane column moved to Local state. Integrated (merge `4c1ea6b`) and published `28fedf1` (ancestry verified). The focused-search proposal is still unrun.
- #95: focused-search proposal unrun.
- #97: the dependency-link replacement is moot after M0 (confirm).
- #90, #92, #93, #97: "publication + closure pending" becomes "published `05c3dc9`; closure pending" (`e0667ec`, `c33dcb1`, `fa3ab5c`, `0195289`, `d2a4103` and `20ff60c` are ancestors of `05c3dc9`).
- #91: adds the four stale Desktop attachments and the unapplied `ready-for-human` relabel.
- #62–#78: each row now carries a short closure-prerequisite state.
- #79–#82: the parent batch was previewed and never applied.
- #101: T4 attempt-3 terminal state.

CT rows: GitHub `pending`; Spec `CT-SPEC (pending)`; state from SYNTHESIS §6 / C4. CT-01, CT-03 and CT-04 are integrated and published at `28fedf1` (ancestry verified). CT-02 is mid-merge. CT-21 is proposed, with lane `ct21-codex-imports` allocated-pending-merge. All others are proposed. Retro values come from `lanes/*.json`:
- retro-gate, team, nav: `passed`
- gate-hooks: field absent; the staged record passes `retro:gate`
- ct21: `pending`

## NEXT bullet (verbatim; last bullet of `progress.md`, wholly inside `tail -20`)

```
- NEXT (2026-10-13, owner session `ccm-20261013-check`; rewrite in place, keep last): after
  the user approves D1–D26 (`reviews/ccm-20261013/SYNTHESIS.md` §8), run SYNTHESIS §5 Runbook
  step 1 (copy `.claude/settings.local.json` and `git diff --cached` to the scratchpad; keep
  `reviews/ccm-20261013/settings.json.before-ct02`), then steps 2–8 in order. Do not restart
  the merge, do not commit the staged settings as-is, do not run `hooks:install` (publish first).
  Pending user decisions: all of D1–D26, first D1 (finish the merge), D2, D4 (settings split),
  D3/D23 (ticket approval at `/to-tickets`), D21 (auto-compaction), D24 (CT-21), D25 (T4).
  State: HEAD `9cd396a` (one commit ahead of the remote), `MERGE_HEAD e12cf04` (CT-02, staged,
  uncommitted), remote `codex/marketplace-native-onboarding` = `28fedf1`. Tickets:
  `ticket-ledger.md`.
```

## Validation

- `progress.md`:
  - The archive is lossless. `python3 -I` rebuilt the original from three parts and compared it with the backup: True, 3,429 lines. The parts were archive lines 9–3034, new-file lines 7–399 plus the blank line, and the archived NEXT bullet.
  - `tail -20` shows the NEXT bullet at offset 10, all 10 of its lines inside the window.
  - 29,764 B is 2.8% of the 1 MiB `PROGRESS_LIMIT`.
- `ticket-ledger.md`: every table row was parsed with `python3 -I`, splitting on unescaped pipes outside backticks and cross-checked with a naive split:
  - table at line 5: 100 rows (98 data), 8 columns in every row
  - table at line 110: 27 rows (25 data), 8 columns in every row
  - table at line 142: 19 rows (17 data), 5 columns in every row
  - No row has a mismatched count, and every row ends with `|`.

## Not placed (outside this writer's files) and notes

- SYNTHESIS §4 corrections for other files are untouched:
  - lane records, `retros/gate-hooks.md`, `retros/c1-catalog-promotion.md`, `retros/retro-gate.md`, `retros/team.md`
  - `skill-invocations.md`
  - `docs/agents/{claude-takeover,ticket-retro,claude-team,issue-tracker}.md`, `.claude/AGENTS.md`, `docs/accepted-decisions.md`
  - `build_manifests.py`, `spec.md`
  - `00-evidence-index.md`, `.git/info/exclude`, `dev/checkout_transfer.py`
  - the four `2a14` absolute-path rewrites
  - the pwf memory note

  The supersession notice, the "mid-turn" sentence and the automation facts are quoted in `findings.md` for reference only. Their destination is still `docs/agents/claude-takeover.md` (Runbook step 7).
- R3 lost items whose destination is not mine:
  - the `lanes/a06-unit3.json` `import_source` note
  - `task_plan.md` items: pending decisions, the ticket-30 out-of-scope sentence, the standing mandates paragraph, the CLOSE lane row (P1)
  - the namespace and mise-first rules in `GLOSSARY.md` and `CODING_STANDARDS.md`

  The mandates are summarized in `findings.md` beside the `accepted-decisions.md` block.
- Rule tension:
  - `.claude/rules/planning-records.md` says `progress.md` is append-only. The archive was done as instructed (D12 default "yes") before the user approved D12 and before Runbook step 9 amends the rule to admit dated archives. No line was lost.
  - Runbook step 9's `git mv` sub-step is now a `git add` of both files.
  - R4 would drop the NEXT-last convention once `task_plan.md` has `## Next Step`. It was kept per the brief, so the NEXT bullet and P1's Next Step must say the same thing.
- SYNTHESIS §4 asked for "CT-01…CT-20 rows"; §6 (revision 2, binding) has CT-01…CT-24 plus CT-02b, and that range was used.
- Unallocated CT tickets show "not allocated" instead of R8's unit names, because R8's names predate C4's renumbering (for example, R8's `ct12-lane-lifecycle` is CT-17 now).
- GitHub columns were not regenerated (no `gh` call). The tracker facts are sweep B's read-only re-query of #62–#83 and #101 only.
