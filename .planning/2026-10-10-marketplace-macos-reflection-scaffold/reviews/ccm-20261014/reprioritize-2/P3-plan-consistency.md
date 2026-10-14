# P3 plan consistency after revs 5-10, D59-D81, Phase 4b, CT-41..CT-58 (2026-10-14, read-only)

TP task_plan.md, TL ticket-ledger.md, PR progress.md, DJ decisions.jsonl, HO `phase3/HANDOFF-2026-10-14.md`, TPL handoff template, CTM `docs/agents/claude-team.md`, SK ticket-frontier `SKILL.md`, FT frontier.toml, SP takeover spec.md. HEAD `21af565` = origin.

R3: fixed F1-F6, F8, F10, F11, F13-F17, F19-F21, F23, F26-F29. Open: F7 (N24), F9 (N9), F12 (TP:364, 385), F22 (N29), F24, F25 (N34), F30 (N30); PR:688-689 claims F9, F12, F30 applied.

## 1. Findings

| id | sev | file:line | current text | replacement |
|---|---|---|---|---|
| N1 | P1 | HO:67-68 | "folds CT-30..CT-39 and D59-D62 into `proposals/claude-takeover-spec/spec.md`" | "folds CT-25..CT-58 (D72 closures) and D59..D81 into `spec.md` at the Phase 4b gate" |
| N2 | P1 | TP:36, TP:229 | "fold CT-25..CT-40 and D59..D80" | "fold CT-25..CT-58 and D59..D81" (TP:260 already folds CT-41..CT-58 at the gate) |
| N3 | P1 | HO:103, HO:117 | "(c) Cut `w0-doctor-records` and `w0-session-hooks` from the new tip"; "(d) Dispatch CT-21 in parallel now" | "w0-doctor-records and CT-21 in wave 0b, w0-session-hooks in 0c (plan Phase 4b)". HO:418 makes session-resume follow §2 in order. |
| N4 | P1 | HO:125-128 | "(f) Ask the user: D47, D48 ...; whether D59 lifts the frozen acceptance baseline ...; ... (D21); ... (D9, D20)" | "(f) Ask only: the typed stages (§2(j)) and the Docker volumes (D80); the rest is settled (DL-72..DL-79, DL-97..DL-100)." |
| N5 | P1 | HO:159-161 | "only the pre-approved rows below run before publication ... Then in parallel:" | rows unmarked, nine outside D77, CT-40/`21-offline`/D49 missing: "Order: plan Phase 4b; only waves 0a-0c run before publication." |
| N6 | P1 | TP:662-663; TP:609 | "with per-run user confirmation"; "confirm each heavy run" | "a notice per run, no question (D68); a concurrent second heavy run needs its own admission (D42)" |
| N7 | P1 | TL:168 vs TP:400 | CT-39 blocked by "...; D60; CT-38"; CT-38 blocked by "CT-39 (D71)" | cycle. TL:168 "spec publication (D59); CT-26 (D71)"; TL:167 add "CT-39 (D71)" |
| N8 | P1 | CTM:131-133; `docs/agents/claude-takeover.md`:11 | "Up to four offline lanes ... confirmation for each run"; "host-heavy runs need per-run confirmation" | "Up to `max_parallel` (3) writer lanes, one always cxx (D65, D78); heavy C++ runs one at a time under D68, each recorded." (CT-40 owns it; TP:616 cites CTM) |
| N9 | P2 | TP:145, 148, 391, 395; TL:158, 162 | "D57 (corpus, pending user)", "(D54 is pending)", "D54 pending", "D57 (pending user)" | "accepted (DL-65/DL-66, DL-81)"; drop from Blocked-by |
| N10 | P2 | TP:206-208 | "Still the user's: whether D59 lifts the frozen acceptance baseline ...; D47, D48; ... (D21 autoCompact, mde config, DL-1..DL-3, a user-global U3 hook)" | "Settled: D64, D47, D48, D21, D67, D62, DL-1, DL-2. Open: DL-3 (held, DL-80)." |
| N11 | P2 | TP:128-130, 396; TL:163 | "turn each class into a prevention ... or code"; "land each class as a skill/doc line or code check" | "read-only audit; findings become acceptance rows (D72); CT-49, CT-51 build checks" |
| N12 | P2 | TP:135-137, 397; TL:164 | "`ccm-<UTC timestamp, nanoseconds ...>`", "`ccm-<ns timestamp>[-<feature>]`" | D61 format: local time plus UTC offset, `.<unit>` suffix; mod in dotfiles (D66); CT-35 = backstop and adoption test (D74) |
| N13 | P2 | TL:135, 138, 141, 142, 144, 145, 153 | CT-09, CT-15, CT-24 "READY"; CT-16 "proposed; file-disjoint from CT-22b"; CT-06, CT-12 "proposed"; CT-13 "held" | copy TP:368-386: "closed (D72)", "folded into ... (D72)", "split ... (D72)" |
| N14 | P2 | TL:137, TP:370 | "held \| user admission (D6) \| ... wave 4" | "admitted (D64) \| wave 1" |
| N15 | P2 | TP:387, TL:154; TP:379, TL:146 | CT-25 blocked by "CT-05, CT-15, CT-17, CT-19, CT-22, CT-24"; CT-17 by "..., CT-24" | CT-25: "CT-05, CT-17, CT-19, CT-22b, CT-29, CT-30, CT-40"; CT-17: drop CT-24 (its own remainder) |
| N16 | P2 | TP:231, 238 vs TP:392 | "CT-31a display mods" (wave 2), "CT-31b" (9); CT-31 blocked by "CT-29, CT-32a" (waves 5, 4) | CT-31a/b exist nowhere else: add rows (CT-31a blocked by CT-02; CT-31b by CT-29, CT-32a) under a D row |
| N17 | P2 | TP:298-300 | "CT-54 ... 4+" (needs CT-38, wave 10); "CT-58 in 10" (needs CT-14, TP:231 or 240); "CT-53 in the cxx slot after `21-offline`" (needs CT-52, publication) | CT-54 after 10; CT-14 once, before 10; CT-53 after CT-52 |
| N18 | P2 | TP:235, 237 vs TP:540 | "#22, #18 heavy" (6), "#23, then the LLVM chain" (8) vs D68 "#21, #20, #17, #16, then #96" | a D row amending D68, or #96 first |
| N19 | P2 | TP:324-336, 341-350, 337, 351 | twelve "- [ ]"; "**Status:** pending" | "**Status:** superseded (D77)"; plain bullets |
| N20 | P2 | TP:85 | "12 waits for the user's word" | delete (12 is ticked) |
| N21 | P2 | HO:217-218 | "Do not start before the w0-doctor integration: ct11-check-lock, ct05-ledger ... Move up after wave 0: CT-11, CT-02b" | "CT-05, CT-11 in wave 3, CT-02b in 6; CT-05 precedes CT-19 (D79)." |
| N22 | P2 | HO:195-196; HO:156 | "the parent routes its own planning edits through that lane"; "CT-23 pin route" | "The parent runs CT-30 (D75)."; "CT-37 pin route (D73)" |
| N23 | P2 | TP:384; TL:151 | "1 heavy slot or 2 (b)" | "7, writer slot (D5)" |
| N24 | P2 | TP:602-603; TP:671 | "no `/clear` until tickets publish"; "None of the five stages has been invoked" | drop the clause; "grill-with-docs typed twice (`skill-invocations.md`:32-35)" |
| N25 | P2 | HO:368 | "`DL-1..DL-4` are pending operations; `approved()` is empty until §3.4" | "DL-1, DL-2 receipted (DL-97, DL-98); DL-3 held; DL-4 pending" |
| N26 | P2 | TP:676-677; TP:439 | "the label is still `ready-for-agent`"; "relabel `ready-for-human`" | "relabelled 2026-10-14 (DL-97)" (live label UNVERIFIED) |
| N27 | P2 | TP:395, TL:162; HO:440 | "spike any time"; "The 30-minute spike ... runs first" | outside D77's set: "after publication, with CT-33" |
| N28 | P2 | TL:150; TP:229 | "lane record uncommitted"; "CT-34 audit, read-only" before publication | record is tracked; CT-34 is outside D77 and needs the transcript admission (TP:286) |
| N29 | P3 | HO:14-23 | revision notes 2, "4-9", 3 | 2, 3, 4-10 |
| N30 | P3 | `.claude/AGENTS.md`:5; CTM:11-18 | roster without `frontier-scheduler` | add it, or cite CT-56 |
| N31 | P3 | HO:214; HO:269 | "for CT-25..CT-40"; "(DL-100 was last ...)" | "CT-25..CT-58"; "DL-101" |
| N32 | P3 | HO:347-348 | "D46 decided by the parent (DL-50)" | append "; revoked by D65 (DL-69)" |
| N33 | P3 | TP:429-430; TP:357-358 | provenance stops at CT-40; "States: built, integrated, published ..., proposed" | add CT-41..CT-58 (D81); add "decided, closed, folded, split" |
| N34 | P3 | TP:464-466; TP:522; TP:527 | header covers D1-D41; "DL-64, DL-81"; D55 "(parent; DL-56)" | "D42-D81: K2 defaults and 2026-10-14"; add DL-54; "amended by D61, D74" |
| N35 | P3 | TP:240, 440, 442 | "#4, #9" (absent from TL); "wave 2 #4 offline lane"; "Phase 7" | name #4/#9 (R2:82); Phase 4b terms |
| N36 | P3 | ADR 0004:7, 0005:7-8; FT:23, `scheduler.md`:52 | status omits D74, D78; "offline portion" (GLOSSARY:108 _Avoid_) | add D74, D78; "split unit" |
| N37 | P3 | HO:472-473; SK:61, 79 | "CT-15 `plan:log`", "nine integrated worktrees"; "(CT-15, else ...)" | CT-15 split (D72); worktrees removed (DL-82) |

progress.md (append-only): PR:637, 646-647 superseded by PR:666, 687; no entry records the rev 10 `write` (HO:27; last is rev 9, PR:696).

## 2. Cross-record mismatches

- DJ:4 DL-4 "CT-01..CT-25 (+CT-02b)" vs TP:315-316, HO:205-208 (CT-01..CT-58); shown at HO:38. Append an operation with the full range; close DL-4 by receipt.
- D51, D52, D53 still lack DL rows (HO:361-363).
- D61: TP:533 (local time, `.<unit>`) vs DL-62 ("UTC ...Z", "-<unit>"); DL-76 never states the format.
- `lanes/w0-decisions.json` "remainder ... stays with the wave-1 CT-24 lane" vs D72 (to CT-17); `lanes/ct21-codex-imports.json` "waits for the gate-hooks merge".
- SP:34, 47, 61 (per-run confirmation, four lanes, #11/#83 and heavy work out of scope) vs D66, D68, D69, D78.
- Wave columns (TP:362-420, TL Lane) use "wave 1 (int. n)"; Phase 4b differs for 14 tickets.

## 3. Wrong once the new order replaces the Phase 4b table

1. TP:217-219: add D81, the new D row, `reprioritize-2/`.
2. TP:224-240 names none of CT-41..CT-58: add them; delete TP:298-301.
3. TP:306-308: tick with the receipt.
4. TP:11-12, TPL:11-12, PR:721-722 (wave 0a list), TP:36, TP:229: follow any change.
5. TP:362-420 and TL:129-187 waves: regenerate, one scheme.
6. FT:47 `[waves]` is empty: fill it (`propose`, K1 §6) or the scheduler ignores the order after CT-40; FT:21-22, SK:35-36 follow the new cxx column (TP:250-255).
7. HO:159-196: pointer to Phase 4b; HO:14; HO:205-208.
8. TPL:26-27 "(D65, D68-D80; ADR 0005) ... (grill-facts, reprioritize)": add D81, the new row, `reprioritize-2`.
9. TP:440-442; ADR 0005:21 "three parallel lanes" if `max_parallel` changes.
10. CT-08 (wave 1) must edit `AGENTS.md`:9-10 ("19 acceptance-baseline files") and `.claude/AGENTS.md`:15-16 ("frozen baseline file").
11. D77 (TP:549) stays; the new D row supersedes its fold range.
