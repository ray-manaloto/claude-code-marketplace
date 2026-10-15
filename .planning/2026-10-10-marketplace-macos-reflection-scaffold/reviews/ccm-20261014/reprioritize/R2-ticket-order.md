# R2: non-C++ ticket order under D59

Read-only, 2026-10-14, tip `21af565`. Keys: TP `P/task_plan.md`, TL `P/ticket-ledger.md`, HO
`RV/phase3/HANDOFF-2026-10-14.md`, FT `P/frontier.toml`, SY `RV/SYNTHESIS.md`, R8
`RV/R8-parallel-plan.md`, X2/Y2/Z1 `RV/phase4-prep/*`, F2 `grill-facts/F2-*`, RV =
`P/reviews/ccm-20261013`. WDI/WDR/WSH = w0-doctor integration, w0-doctor-records,
w0-session-hooks. SPEC = user-typed stages HO:202-216. `*` = edge absent from current tables.

## 1. Dependency graph (h hard, p path)

```
WDI    -> WDR, WSH, CT-21 cut, CT-26, CT-29, CT-32a (h; HO:79-109, TL:155-160); CT-30 (soft)
WDR    -> CT-05 (p, imports lanes.py TL:134), CT-17, CT-18, CT-22b, CT-12, CT-16 (h, TL:141-147)
WSH    -> CT-02b (p corpus/test_hooks.py TL:131), CT-32b (h TL:161), CT-23, CT-30 (p settings.json TP:292), CT-33 (p)
D7     -> CT-21, CT-29, CT-32a, CT-39 (p mise/tasks/, HO:198-199)
SPEC   -> every CT ticket (D59 TP:413, HO:72-75)
CT-26  -> CT-39 (p* hk.pkl, mise.dev.toml head, dev/bootstrap.py; X2:137-142)
WDR,WSH,CT-21 -> CT-39 (p* new dev/*.py)
CT-39  -> CT-02b, 05, 11, 17, 18, 19, 22b, 23, 29, 32a, 33, 37, #95 (p* package layout; F2:94-96)
CT-30  -> CT-29 (h TL:157), CT-32a (p HO:192-194), CT-05 (p* planning-records.md R8:145 vs HO:175),
          CT-25 (p* ticket-frontier SKILL.md HO:175)
CT-05  -> CT-17 (h; p dev/lane.py R8:145,166), CT-19 (h TL:148), CT-25 (h)
CT-11  -> CT-17 (h); CT-11 x CT-32a (p* retro_gate.py R8:144 vs HO:177)
CT-02b -> CT-32b (h), CT-18 (p* dev/git_delivery.py R8:143,168)
D49    -> CT-19 (p* .claude/agents/*.md HO:140-143 vs R8:167)
CT-17  x CT-32b x WSH (p* stop_gate.py SY:377, HO:180, lanes/w0-session-hooks.json notes)
CT-17  x CT-29 (p* session:status vs mise/tasks/session.toml SY:377, HO:176)
CT-19  -> CT-23, CT-06, CT-25 (h); CT-32a -> CT-32b, CT-31 (h)
CT-29  -> CT-37 (h TL:166), CT-31 (h), CT-35 (p* shared name generator D61 TP:415)
CT-31  -> CT-35, CT-36 (p* one hooks/register.js, Y2:41-47)
CT-22b, CT-07, CT-10 -> CT-20 (h TL:149)
```

Critical path (proposed graph): **WDI -> {WDR, CT-21, WSH last per D26} -> SPEC -> CT-26 -> CT-39
-> CT-05 -> CT-17 -> CT-25** (CT-11, CT-19, CT-22b join at CT-17/CT-25). Second chain: CT-30 -> CT-29 -> CT-37 -> CT-35.
Priority follows K1's rule, critical-path length then out-degree (`RV/skills/K1-*.md:69`).

Cycle to cut: HO:221 (from FORK:34-36) holds CT-05 "until w0-doctor and CT-19 land", while TL:148
blocks CT-19 on CT-05. Drop the CT-19 clause.

## 2. Greenfield consolidation (D59: no dual paths)

| Proposal | Reason | owned_paths effect |
|---|---|---|
| Close CT-13 as duplicate of CT-31 | TL:142, D55 | none |
| Dissolve CT-15: shape and ledgers to CT-30; `plan:handoff`, `plan:log` to CT-29; `check:planning` (= `doctor --class K,...`, SY:375) to CT-22b | four tickets own handoff and plan shape | `dev/plan_records.py` never created |
| CT-29 adopts the untracked Z1 build and splits it (Z1:14-31) | `dev/handoff.py` (929 lines), `dev/test_handoff.py` and both skills are untracked, "no lane may lose them" (TP:147-148, `git status`); HO:176 names `dev/doctor/handoff.py` and omits `session-handoff/**` | add those paths to CT-29 |
| CT-37 = CT-29's second unit, never parallel; it alone decides the env carrier (now also CT-23 TL:152 and CT-30/D54) and the context trigger (TP:187-189) | one pin route, one owner | CT-23 and CT-30 lose those items |
| One mods plugin: CT-31a skeleton + grill, then CT-35 and CT-36 modules, then CT-31b band/lane/verify after CT-29, CT-32a | Y2:41-47 single `register.js` | all `plugins/workflow-mods/**`; backstop hooks stay parent hunks |
| CT-36 drops the layout review (settled by F2 and D62, TP:416); the webclaw pin and `web:fetch` task, named in D62 and owned by no ticket (`grep -rn web:fetch P`: TP:416, DL-63 only), go to CT-36 | duplicate scope, orphan task | CT-33 consumes CT-36's pin |
| CT-12 and CT-07's mirror test into CT-38 (wiring table and `skills:sync`, TP:170-177) | two wiring rules, two mirror checks | CT-07 keeps `.codex/` roles only |
| Invert TL:168 to CT-39 -> CT-38 | the lint (skills run only `./dev/mise run`) cannot pass before CT-39's tasks exist | CT-38 lands last over all skills |
| CT-16 into CT-22b, no `settings_check.py` alias (TL:145) | WDR's `settings.py` already implements class I (`.claude/worktrees/w0-doctor/dev/doctor/settings.py:1-35`); an alias is a shim | |
| CT-06 and CT-32b's `frontier.py release` refusal (TL:161) into CT-25 | frontier step 6 already loops the retro (`.claude/skills/ticket-frontier/SKILL.md:54-58`); FORK:71-72 says CT-25 is built | CT-32b keeps `dev/hooks/` only |
| CT-02b deletes substring verb matching once WSH's `if` field (D58, TP:412) lands | two mechanisms | |
| Close CT-09: gh-stack kept (`.claude/AGENTS.md:10`), status band = CT-31, versioning = CT-28 G2 (`tickets.preview.json` CT-09) | superseded | |
| Close CT-24 at WDI (mise rows HO:226); `approved()` import to CT-17 (SY:384) | remainder unitemized | |
| CT-34: read-only audit before `/to-tickets`; each error class becomes an acceptance row of its owner; code merges into CT-20 | its fixes hit every hot path (FT:45) | residual docs only |

The parent folds these into `spec.md` before SPEC (HO:72-75), so tickets are filed consolidated.

## 3. Order (two non-C++ writer slots plus cxx; FT:7,10; D46 TP:398 exempts wave 0)

| Wave | Lane 1 | Lane 2 | Blockers met / reason |
|---|---|---|---|
| 0a | WDI, serial, parent | D7 spike, throwaway, `mise/` | HO:79; D7 fixes CT-39's task-file layout |
| 0b | WDR (`dev/doctor/{lanes,agents}.py`) | CT-21 (`evidence/`, `dev/check_inputs.py`) | WDI; completes CT-22a; CT-21 ends P1-10 and frees the #63-#74 closure rows (TL:150) |
| 0c | WSH (integrates last, D26) | D49 tooling (`merger.md`, reviewer heredoc) | WDI; frees `settings.json`; cuts merger cost |
| gate | SPEC (user); CT-34 audit runs read-only meanwhile | | |
| 1 | CT-26 (X2:137-142) | CT-30 (+CT-15 shape; planning records) | WDI, D50, D54; CT-30 removes HO:465 legacy items |
| 2 | CT-39, exclusive over `dev/**`, task rows, `pyproject.toml`, `uv.lock`, `hk.pkl`; serial units | CT-31a (JS only) or CT-14 (docs) | CT-26, wave 0; retires 28 `MARKETPLACE_PYTHON` and 27 bare-script rows (TP:162-163) |
| 3 | CT-05 (`dev/lane.py`, `ledger.py`) | CT-11 (`check.py`, `retro_gate.py`, lock) | CT-39, CT-30; both feed CT-17 |
| 4 | CT-17 (+CT-24 rest) | CT-32a | CT-05, CT-11, WDR; verify unblocks 32b, 31b |
| 5 | CT-19 | CT-29 (+Z1 files) | D49, CT-05; CT-30 |
| 6 | CT-02b | CT-37 | WSH; CT-29 |
| 7 | CT-32b | CT-22b (+CT-16) | CT-32a, CT-02b; WDR |
| 8 | CT-25 (+CT-06) | CT-18 | CT-17, 19, 22b; CT-02b |
| 9 | CT-23 | CT-31b | CT-19, 22b; CT-29, 32a |
| 10 | CT-38 (+CT-12, mirror) | CT-35 | all skill writers done; CT-31a |
| 11+ | CT-36, then CT-33 | CT-10, CT-14, CT-07 roles, CT-20 (+CT-34 code), #95 C3 (R8:169) | webclaw admission; CT-22b |

Held: CT-08 (D6), CT-28 (G2/G3, TL:156), #98 (after #94), #101 (D25), #91 human, #4 and #9
(touch frozen `ci/acceptance.sh`, `acceptance.yml`). Closes run between waves. #24-#29: R1:74
proposes them for the cxx class.

## 4. Risks

- Missed conflicts: the `*` edges above; CT-38's lint shares a decision table with the PreToolUse
  guard (TP:172-173), so it is a `dev/hooks/` writer (FT:44-45); CT-30 owns `task_plan.md` and
  `progress.md` (HO:175) while every integration's records commit edits them: run it parent-side
  or freeze records commits (HO:199-200); CT-39 vs the cxx lane on `mise.dev.toml` (no C++ rows
  today, `grep '^\[tasks' mise.dev.toml`) UNVERIFIED for future rows.
- Unclear acceptance: CT-34..CT-39 take owned_paths "from the review wave's reports" (TL:163-168),
  but D59 replaced that wave (HO:73); whether CT-39 moves the six skill-bundled scripts
  (`find .claude/skills -name '*.py'`) breaks Codex mirrors: UNVERIFIED; CT-35 slash-command
  timing and cache effect are UNVERIFIED (F1:21,57-58).
- Admissions: SPEC stages; A09 publish per integration; D60-D62 are parent defaults the user may
  override (TP:414-416); webclaw install and live crawl (CT-33, CT-36); reading `~/.claude`
  transcripts (CT-34, CT-20; TP:192-194); a fresh `claude -p` session (CT-37, TP:190-191); a
  `.claude-plugin/marketplace.json` entry for workflow-mods would edit a frozen baseline file
  (`evidence/onboarding/baseline-files.json`, Y2:121); the D59 baseline question (TP:203-204).
- Throughput: CT-39 serializes all Python for its units; the alternative (each ticket migrates
  its subsystem) keeps parallelism but spreads one structural change over many lanes.
