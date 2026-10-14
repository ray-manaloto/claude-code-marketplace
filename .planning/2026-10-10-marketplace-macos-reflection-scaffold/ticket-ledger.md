# Ticket ledger

Every GitHub issue for this repository with its live state, frontier status, blocking edges, Claude
lane and local evidence state. Regenerate the first six columns from the tracker (`gh api graphql`
with `blockedBy`/`parent`); the last two are maintained by the parent at each lane transition.
Frontier = open with no open blockers; a closed blocker still needs an accepted disposition before
dependents start. Snapshot: 2026-10-13 (records update by review session `ccm-20261013-check`):
integration tip `0a68dce` = remote `codex/marketplace-native-onboarding` (A09 publish of merge
`760b154`, CT-02, lane `claude/gate-hooks-wiring` at `697e1da`); no `MERGE_HEAD`. The GitHub
columns were last regenerated at tip `05c3dc9`; sweep B re-queried #62–#83 and #101 read-only on 2026-10-13 (all OPEN; #62–#78
labelled `ready-for-agent`, #79–#83 unlabelled). Takeover-spec tickets CT-01…CT-25 (+CT-02b) have no
GitHub issue yet and are listed in their own table below; closure prerequisites for #62–#78 and the
T4 state follow it.

| Issue | Title | Spec | GH | Frontier | Blocked by | Lane | Local state |
|---|---|---|---|---|---|---|---|
| [#11](https://github.com/ray-manaloto/claude-code-marketplace/issues/11) | Spec: Native research core and cross-host research baseline | — | OPEN | READY | — |  | spec; 67 children; amended 2026-10-12 |
| [#12](https://github.com/ray-manaloto/claude-code-marketplace/issues/12) | 01: Seal Task 14c failed LSan closure | #11 | OPEN | READY | — | CLOSE | closure committed 2cc4c029 (in tip); tracker close pending |
| [#13](https://github.com/ray-manaloto/claude-code-marketplace/issues/13) | 02: Private LSan repair verdict (14c1) | #11 | OPEN | blocked | #12 |  | PARTIAL: offline repair 4905c8e in issue-13-lsan worktree (not in tip); native LSan trial inconclusive |
| [#14](https://github.com/ray-manaloto/claude-code-marketplace/issues/14) | 03: Installed LSan guard preparation | #11 | OPEN | blocked | #13 |  |  |
| [#15](https://github.com/ray-manaloto/claude-code-marketplace/issues/15) | 04: Guarded LSan promotion | #11 | OPEN | blocked | #14 |  |  |
| [#16](https://github.com/ray-manaloto/claude-code-marketplace/issues/16) | 05: GCC sanitizer witnesses (Task 15) | #11 | OPEN | READY | — | heavy 4 |  |
| [#17](https://github.com/ray-manaloto/claude-code-marketplace/issues/17) | 06: P2996 admitted-family coverage (Task 16) | #11 | OPEN | READY | — | heavy 3 |  |
| [#18](https://github.com/ray-manaloto/claude-code-marketplace/issues/18) | 07: GCC coverage cells (Task 16) | #11 | OPEN | blocked | #16 |  |  |
| [#19](https://github.com/ray-manaloto/claude-code-marketplace/issues/19) | 08: LSan coverage cells (Task 16) | #11 | OPEN | blocked | #15 |  |  |
| [#20](https://github.com/ray-manaloto/claude-code-marketplace/issues/20) | 09: Reflection-core analysis commands (Task 17) | #11 | OPEN | READY | — | heavy 2 |  |
| [#21](https://github.com/ray-manaloto/claude-code-marketplace/issues/21) | 10: Relocated CMake Config consumers (Task 18) | #11 | OPEN | READY | — | heavy 1 |  |
| [#22](https://github.com/ray-manaloto/claude-code-marketplace/issues/22) | 11: Native CPS consumers (Task 19) | #11 | OPEN | blocked | #21 |  |  |
| [#23](https://github.com/ray-manaloto/claude-code-marketplace/issues/23) | 12: Native foundation acceptance (Task 20) | #11 | OPEN | blocked | #21, #16, #19, #22, #15, #17, #20, #18 |  |  |
| [#24](https://github.com/ray-manaloto/claude-code-marketplace/issues/24) | 13: Pin legacy trackers behavior and ownership | #11 | OPEN | READY | — | CLOSE | boundary committed 931b536 (in tip); tracker close pending |
| [#25](https://github.com/ray-manaloto/claude-code-marketplace/issues/25) | 14: Measure Python bridge placement | #11 | OPEN | blocked | #24 | CLOSE | helper selection committed 54d34c8b (in tip); tracker close pending |
| [#26](https://github.com/ray-manaloto/claude-code-marketplace/issues/26) | 15: Issues schema and generator qualification | #11 | OPEN | blocked | #24 | wave 2 |  |
| [#27](https://github.com/ray-manaloto/claude-code-marketplace/issues/27) | 16: Admit Issues transport dependencies | #11 | OPEN | READY | — | wave 2 |  |
| [#28](https://github.com/ray-manaloto/claude-code-marketplace/issues/28) | 17: Additive CLI extension contract | #11 | OPEN | blocked | #24 |  | PARTIAL: offline v2 contract integrated cbb455b; public v2 + Claude/OCI pending |
| [#29](https://github.com/ray-manaloto/claude-code-marketplace/issues/29) | 18: Measure Context7 JavaScript bridge | #11 | OPEN | blocked | #25 |  | PARTIAL: offline bridge integrated 66905b4; live/confined/native pending; #40 held |
| [#30](https://github.com/ray-manaloto/claude-code-marketplace/issues/30) | 19: Native GitHub Issues tracer | #11 | OPEN | blocked | #25, #27, #23, #26, #28 |  |  |
| [#31](https://github.com/ray-manaloto/claude-code-marketplace/issues/31) | 20: Tagged batch and outcome tracer | #11 | OPEN | blocked | #30 |  |  |
| [#32](https://github.com/ray-manaloto/claude-code-marketplace/issues/32) | 21: Identity registry tracer | #11 | OPEN | blocked | #31 |  |  |
| [#33](https://github.com/ray-manaloto/claude-code-marketplace/issues/33) | 22: Borrow lifetime and cancellation | #11 | OPEN | blocked | #31 |  |  |
| [#34](https://github.com/ray-manaloto/claude-code-marketplace/issues/34) | 23: Immutable raw attempt artifacts | #11 | OPEN | blocked | #31 |  |  |
| [#35](https://github.com/ray-manaloto/claude-code-marketplace/issues/35) | 24: GitHub source-at-ref operation | #11 | OPEN | blocked | #34, #33, #32 |  |  |
| [#36](https://github.com/ray-manaloto/claude-code-marketplace/issues/36) | 25: GitHub Discussions operation | #11 | OPEN | blocked | #32, #33, #34 |  |  |
| [#37](https://github.com/ray-manaloto/claude-code-marketplace/issues/37) | 26: GitHub Releases operation | #11 | OPEN | blocked | #34, #32, #33 |  |  |
| [#38](https://github.com/ray-manaloto/claude-code-marketplace/issues/38) | 27: Exa operation | #11 | OPEN | blocked | #34, #33, #32 |  |  |
| [#39](https://github.com/ray-manaloto/claude-code-marketplace/issues/39) | 28: Firecrawl operation | #11 | OPEN | blocked | #34, #33, #32 |  |  |
| [#40](https://github.com/ray-manaloto/claude-code-marketplace/issues/40) | 29: Context7 operation | #11 | OPEN | blocked | #34, #29, #32, #33 |  |  |
| [#41](https://github.com/ray-manaloto/claude-code-marketplace/issues/41) | 30: Last30Days operation | #11 | OPEN | blocked | #32, #33, #34 |  |  |
| [#42](https://github.com/ray-manaloto/claude-code-marketplace/issues/42) | 31: Research-plan validation | #11 | OPEN | blocked | #31, #32 |  |  |
| [#43](https://github.com/ray-manaloto/claude-code-marketplace/issues/43) | 32: Independent-source coverage verdict | #11 | OPEN | blocked | #35, #41, #42, #38 |  |  |
| [#44](https://github.com/ray-manaloto/claude-code-marketplace/issues/44) | 33: Bounded failure and controlled-empty verdicts | #11 | OPEN | blocked | #42, #36 |  |  |
| [#45](https://github.com/ray-manaloto/claude-code-marketplace/issues/45) | 34: Equivalent fallback decision | #11 | OPEN | blocked | #42, #39, #43 |  |  |
| [#46](https://github.com/ray-manaloto/claude-code-marketplace/issues/46) | 35: Deterministic bounded cache | #11 | OPEN | blocked | #42, #34 |  |  |
| [#47](https://github.com/ray-manaloto/claude-code-marketplace/issues/47) | 36: Optional inference attribution | #11 | OPEN | blocked | #42, #43 |  |  |
| [#48](https://github.com/ray-manaloto/claude-code-marketplace/issues/48) | 37: Native core delivery to Claude plugin | #11 | OPEN | blocked | #21, #30 |  |  |
| [#49](https://github.com/ray-manaloto/claude-code-marketplace/issues/49) | 38: Full Claude CLI/data parity receipt | #11 | OPEN | blocked | #36, #40, #47, #39, #44, #35, #38, #43, #46, #41, #48, #37, #45 |  |  |
| [#50](https://github.com/ray-manaloto/claude-code-marketplace/issues/50) | 39: MCP read-only research tracer | #11 | OPEN | blocked | #31, #34, #33 |  |  |
| [#51](https://github.com/ray-manaloto/claude-code-marketplace/issues/51) | 40: Generated MCP operation catalog | #11 | OPEN | blocked | #36, #50, #41, #39, #37, #35, #38, #40 |  |  |
| [#52](https://github.com/ray-manaloto/claude-code-marketplace/issues/52) | 41: Opt-in mutation and private-upload guard | #11 | OPEN | blocked | #51 |  |  |
| [#53](https://github.com/ray-manaloto/claude-code-marketplace/issues/53) | 42: Generated thin Claude adapter | #11 | OPEN | blocked | #51, #48, #52 |  |  |
| [#54](https://github.com/ray-manaloto/claude-code-marketplace/issues/54) | 43: Fresh Claude plugin/session acceptance | #11 | OPEN | blocked | #53, #49 |  |  |
| [#55](https://github.com/ray-manaloto/claude-code-marketplace/issues/55) | 44: Codex adapter | #11 | OPEN | blocked | #51, #52 |  |  |
| [#56](https://github.com/ray-manaloto/claude-code-marketplace/issues/56) | 45: Antigravity adapter | #11 | OPEN | blocked | #52, #51 |  |  |
| [#57](https://github.com/ray-manaloto/claude-code-marketplace/issues/57) | 46: OpenCode adapter | #11 | OPEN | blocked | #52, #51 |  |  |
| [#58](https://github.com/ray-manaloto/claude-code-marketplace/issues/58) | 47: Cross-host schema and loader acceptance | #11 | OPEN | blocked | #56, #54, #57, #55 |  |  |
| [#59](https://github.com/ray-manaloto/claude-code-marketplace/issues/59) | 48: Final native requalification | #11 | OPEN | blocked | #49, #58 |  |  |
| [#60](https://github.com/ray-manaloto/claude-code-marketplace/issues/60) | 49: Provider acceptance | #11 | OPEN | blocked | #44, #58, #47, #43, #45, #46 |  |  |
| [#61](https://github.com/ray-manaloto/claude-code-marketplace/issues/61) | 50: Admitted OCI release acceptance | #11 | OPEN | blocked | #54, #58, #60, #59 |  |  |
| [#62](https://github.com/ray-manaloto/claude-code-marketplace/issues/62) | A01 — Portable locked task bootstrap | #11 | OPEN | READY | — | CLOSE | A01 published 93bb798 (in tip); closure pending: packet verdict `CODE_CRITERIA_READY`, prerequisites in "Closure prerequisites" |
| [#63](https://github.com/ray-manaloto/claude-code-marketplace/issues/63) | A02 — One-page GitHubKit search receipt | #11 | OPEN | blocked | #62 | CLOSE | A02 published 93bb798; closure pending: `PARTIAL_NOT_YET_READY` (archival supplement awaits independent review; captures only in `2a14`, import = CT-21) |
| [#64](https://github.com/ray-manaloto/claude-code-marketplace/issues/64) | A03a — Bounded collection and attempt recording | #11 | OPEN | blocked | #66 | CLOSE | A03a published 93bb798; closure pending: `CODE_CRITERIA_READY`, chained on its blocker's disposition; see "Closure prerequisites" |
| [#65](https://github.com/ray-manaloto/claude-code-marketplace/issues/65) | A03b — Controlled empty and completeness verdicts | #11 | OPEN | blocked | #64 | CLOSE | A03b published 93bb798; closure pending: `CODE_CRITERIA_READY`, chained on its blocker's disposition; see "Closure prerequisites" |
| [#66](https://github.com/ray-manaloto/claude-code-marketplace/issues/66) | A04 — Validated catalog and immutable recording | #11 | OPEN | blocked | #63 | CLOSE | A04 published 93bb798; closure pending: `CODE_CRITERIA_READY`, chained on its blocker's disposition; see "Closure prerequisites" |
| [#67](https://github.com/ray-manaloto/claude-code-marketplace/issues/67) | A05a — Compatible baseline and pure comparison | #11 | OPEN | blocked | #66, #65 | CLOSE | A05a published 93bb798; closure pending: `CODE_CRITERIA_READY`, chained on its blocker's disposition; see "Closure prerequisites" |
| [#68](https://github.com/ray-manaloto/claude-code-marketplace/issues/68) | A05b — Public rerun and comparison receipt | #11 | OPEN | blocked | #67 | CLOSE | A05b published 93bb798; closure pending: `CODE_CRITERIA_READY`, chained on its blocker's disposition; see "Closure prerequisites" |
| [#69](https://github.com/ray-manaloto/claude-code-marketplace/issues/69) | A06 — Codex release-schema example receipt | #11 | OPEN | blocked | #68 | a06-unit3 / CLOSE | unit1 a071340 + unit2 5acdc3a + unit3 8f783a0 integrated (merge 361688e; 24 tests, review PASS-with-P3: deeply nested TOML RecursionError → next unit); published `f250f75`; retained corpus + schema exist only in `2a14` (P1-10); corpus/schema import = CT-21 (evidence/codex-examples, evidence/saved-searches); consumption after it integrates; no closure inventory (sweep B) |
| [#70](https://github.com/ray-manaloto/claude-code-marketplace/issues/70) | A07a — Qualify one-issue amendment operations | #11 | OPEN | blocked | #66 | CLOSE | A07a published a8ecd40; closure pending: `CODE_CRITERIA_READY` on pre-T3 helper bytes; needs the T3 helper-byte refresh |
| [#71](https://github.com/ray-manaloto/claude-code-marketplace/issues/71) | A07b — Apply the approved spec #11 amendment | #11 | OPEN | blocked | #70 | CLOSE | A07b applied; spec #11 body verified live; closure pending: `CODE_CRITERIA_READY` on cached `graph/spec11.json`; needs helper-byte refresh and a fresh #11 postimage read |
| [#72](https://github.com/ray-manaloto/claude-code-marketplace/issues/72) | A08a — Publish and bind ticket identities | #11 | OPEN | blocked | #71 | CLOSE | A08a published 3972f3b; closure pending: not prepared (no closure inventory; sweep B) |
| [#73](https://github.com/ray-manaloto/claude-code-marketplace/issues/73) | A08b — Verify and publish dependency relationships | #11 | OPEN | blocked | #72 | CLOSE | A08b verified 906cdbc; closure pending: not prepared (no closure inventory; sweep B) |
| [#74](https://github.com/ray-manaloto/claude-code-marketplace/issues/74) | A09 — Reviewed commit and branch publication | #11 | OPEN | blocked | #62 | CLOSE | A09 published; route used for f0d79a0/a071340/848552c; closure pending: not prepared (no closure inventory; sweep B) |
| [#75](https://github.com/ray-manaloto/claude-code-marketplace/issues/75) | A10 — Reviewable checkout-transfer plan | #11 | OPEN | blocked | #74 | CLOSE | A10 published bcf9760; closure pending: not prepared (no closure inventory; sweep B) |
| [#76](https://github.com/ray-manaloto/claude-code-marketplace/issues/76) | A11 — Apply and verify source-checkout transfer | #11 | OPEN | blocked | #75 | CLOSE | A11 accepted by manual reconciliation after guard rc 2 (42d94f9); closure pending: not prepared (no closure inventory; sweep B) |
| [#77](https://github.com/ray-manaloto/claude-code-marketplace/issues/77) | A12a — Qualify the portable fast-check and hosted CI route | #11 | OPEN | blocked | #74, #63, #62 | CLOSE | A12a published a8ecd40; research-fast CI passed; closure pending: not prepared (no closure inventory; sweep B) |
| [#78](https://github.com/ray-manaloto/claude-code-marketplace/issues/78) | A12b — Assemble the remainder amendment | #11 | OPEN | blocked | #77, #73, #69 |  | waits for A06 acceptance; closure not prepared (no closure inventory; sweep B) |
| [#79](https://github.com/ray-manaloto/claude-code-marketplace/issues/79) | [Spec] Preserve acceptance state when comparison fails | — | OPEN | READY | — | CLOSE | RF spec; children #84 #85 closed; T4 Phase C parent batch previewed (cmds 096–099, rc 0) and never applied; a new attempt needs a new user-approved budget (D25) |
| [#80](https://github.com/ray-manaloto/claude-code-marketplace/issues/80) | [Spec] Check the exact borrowed runtime before research launch | — | OPEN | READY | — | CLOSE | RF spec; children closed; T4 Phase C parent batch previewed (cmds 096–099, rc 0) and never applied; a new attempt needs a new user-approved budget (D25) |
| [#81](https://github.com/ray-manaloto/claude-code-marketplace/issues/81) | [Spec] Share refresh outcome safeguards and the improvement workflow | — | OPEN | READY | — | CLOSE | RF spec; children closed; T4 Phase C parent batch previewed (cmds 096–099, rc 0) and never applied; a new attempt needs a new user-approved budget (D25) |
| [#82](https://github.com/ray-manaloto/claude-code-marketplace/issues/82) | [Spec] Share the complete reusable refresh workflow | — | OPEN | READY | — | CLOSE | RF spec; children closed; T4 Phase C parent batch previewed (cmds 096–099, rc 0) and never applied; a new attempt needs a new user-approved budget (D25) |
| [#83](https://github.com/ray-manaloto/claude-code-marketplace/issues/83) | [Spec] Complete the remaining Marketplace session work | — | OPEN | READY | — |  | remaining-work spec; 20 children published 2026-10-13 |
| [#84](https://github.com/ray-manaloto/claude-code-marketplace/issues/84) | RF1: Preserve accepted history after comparison failure | #79 | CLOSED | closed | — |  | CLOSED by T4 Phase C |
| [#85](https://github.com/ray-manaloto/claude-code-marketplace/issues/85) | RF2: Stop unavailable borrowed runtimes before launch | #80 | CLOSED | closed | — |  | CLOSED by T4 Phase C |
| [#86](https://github.com/ray-manaloto/claude-code-marketplace/issues/86) | RF3b: Document the standing improvement workflow | #81 | CLOSED | closed | — |  | CLOSED by T4 Phase C |
| [#87](https://github.com/ray-manaloto/claude-code-marketplace/issues/87) | RF3a: Share verified refresh outcome behavior | #81 | CLOSED | closed | #85, #84 |  | CLOSED by T4 Phase C |
| [#88](https://github.com/ray-manaloto/claude-code-marketplace/issues/88) | RF4: Publish the complete reusable refresh package | #82 | CLOSED | closed | #86, #87, #85, #84 |  | CLOSED by T4 Phase C |
| [#89](https://github.com/ray-manaloto/claude-code-marketplace/issues/89) | W1: Record parallel worktree and retro ownership | #83 | CLOSED | closed | — |  | CLOSED; W1 published f0d79a0 |
| [#90](https://github.com/ray-manaloto/claude-code-marketplace/issues/90) | B1: Reconcile published source and tracker status | #83 | OPEN | READY | — | B1 (after M0) | B1 c33dcb1 in tip via M0 e0667ec; published 05c3dc9; closure pending |
| [#91](https://github.com/ray-manaloto/claude-code-marketplace/issues/91) | B2: Repair stale worktree attachments | #83 | OPEN | READY | — | human | B2 needs the Codex Desktop attachment operation: four stale Desktop attachments bind `issue-13-lsan` (4905c8e) to 01a130ef; relabel → `ready-for-human` accepted in round-1 Q6, not applied (still `ready-for-agent`, P1-9) |
| [#92](https://github.com/ray-manaloto/claude-code-marketplace/issues/92) | T1: Publish approved specs and tickets through the existing journal | #83 | OPEN | READY | — | M0/CLOSE | T1 in tip (c6caaca/d2a4103 + 20ff60c via M0); published 05c3dc9; closure pending |
| [#93](https://github.com/ray-manaloto/claude-code-marketplace/issues/93) | T3: Close tickets only from accepted evidence | #83 | OPEN | READY | — | M0/CLOSE | T3 fa3ab5c in tip via M0 e0667ec; published 05c3dc9; closure pending |
| [#94](https://github.com/ray-manaloto/claude-code-marketplace/issues/94) | C1: Qualify affected queries without accepting an incomplete baseline | #83 | OPEN | READY | — | C1 (`c1-catalog-promotion`) | integrated 52ce420+6c09b7f (merge 4c1ea6b), published `28fedf1`; lane retro passed; closure pending; its input, the focused-search proposal (7 capped + 1 unverified-empty searches block a new baseline), is unrun |
| [#95](https://github.com/ray-manaloto/claude-code-marketplace/issues/95) | C3: Diagnose the known-empty discussion search | #83 | OPEN | READY | — | C3 (released) | focused-search proposal unrun; offline diagnostic is wave 2 #4 |
| [#96](https://github.com/ray-manaloto/claude-code-marketplace/issues/96) | L1: Qualify a private exact LLVM bundle | #83 | OPEN | READY | — | heavy 5 | L1 heavy lane; per-run confirmation; last in heavy order |
| [#97](https://github.com/ray-manaloto/claude-code-marketplace/issues/97) | T2: Publish and audit the approved dependency graph | #83 | OPEN | blocked | #92 | M0/CLOSE | T2 0195289 in tip via M0 e0667ec; published 05c3dc9; closure pending; the dependency-link replacement awaited from 01a130ef is moot after M0 (confirm) |
| [#98](https://github.com/ray-manaloto/claude-code-marketplace/issues/98) | C2: Adopt the qualified runner and evaluate the retained companion | #83 | OPEN | blocked | #94 | C2 (after C1, released) |  |
| [#99](https://github.com/ray-manaloto/claude-code-marketplace/issues/99) | L2: Build and qualify IWYU for that LLVM bundle | #83 | OPEN | blocked | #96 |  |  |
| [#100](https://github.com/ray-manaloto/claude-code-marketplace/issues/100) | L3: Build the portable project consumer with upstream LLVM | #83 | OPEN | blocked | #96 |  |  |
| [#101](https://github.com/ray-manaloto/claude-code-marketplace/issues/101) | T4: Publish the new graph and reconcile completed RF history | #83 | OPEN | blocked | #93, #97, #90, #89 | M0/CLOSE | T4 attempt 3 `STOPPED/NOT_COMPLETED` (`TimeoutError` after a 901.8 s approval wait, cap 900 s); children RF1–RF4/W1 + 25 labels `VERIFIED`; parent batch #79–#82 previewed, never applied; budgets original 3/3, recovery 3/3; `phase-c-policy-v2.md` grants no fourth attempt; postimages at `~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/t4-parent-metadata/postimages/` target three repo files, all drifted from the tip; branch content in tip via M0; see "T4 state" |
| [#102](https://github.com/ray-manaloto/claude-code-marketplace/issues/102) | L4a: Qualify formatting and language diagnostics | #83 | OPEN | blocked | #100 |  |  |
| [#103](https://github.com/ray-manaloto/claude-code-marketplace/issues/103) | L4b: Qualify IWYU on the portable project consumer | #83 | OPEN | blocked | #100, #99 |  |  |
| [#104](https://github.com/ray-manaloto/claude-code-marketplace/issues/104) | L4c: Qualify the static analyzer on portable code | #83 | OPEN | blocked | #100 |  |  |
| [#105](https://github.com/ray-manaloto/claude-code-marketplace/issues/105) | L4d: Qualify a source-coverage witness | #83 | OPEN | blocked | #100 |  |  |
| [#106](https://github.com/ray-manaloto/claude-code-marketplace/issues/106) | L5a: Run locked compiler qualification in CI | #83 | OPEN | blocked | #105, #104, #103, #102 |  |  |
| [#107](https://github.com/ray-manaloto/claude-code-marketplace/issues/107) | L5b: Create exact LLVM and IWYU update PRs | #83 | OPEN | blocked | #106 |  |  |
| [#108](https://github.com/ray-manaloto/claude-code-marketplace/issues/108) | L6: Activate the merged qualified bundle through the global owner | #83 | OPEN | blocked | #106 |  |  |

## Takeover-spec tickets (CT, proposed; no GitHub issue yet)

Source: `reviews/ccm-20261013/SYNTHESIS.md` §6 (C4's reconciled table, binding; D23 approval pending
at `/to-tickets`); CT-25 from `reviews/ccm-20261013/skills/K1-orchestrator-skill-design.md` §8 (D32,
accepted 2026-10-13). GH = `pending` until Runbook step 11 creates the spec and tickets; Spec = the
takeover spec (`proposals/claude-takeover-spec/spec.md`), unpublished. Frontier here: done, in
progress, READY (no open blocker) or blocked/held. Lane column: lane unit (from `lanes/*.json` where
one exists, otherwise not allocated) and wave. Local state: state per §6, then the lane record's
`retro`. CT-01, CT-03 and CT-04 were built before any ticket was approved (P1-6); their texts, edges
and criteria still need approval.

| Issue | Title | Spec | GH | Frontier | Blocked by | Lane | Local state |
|---|---|---|---|---|---|---|---|
| CT-01 (pending issue) | Retro gate task | CT-SPEC (pending) | pending | done | — | retro-gate · done | integrated (merge e618243), published `28fedf1`; retro passed; acceptance criterion 2 open (no task runs `dev/test_retro_gate.py`, P1-5) → CT-12 |
| CT-02 (pending issue) | Hook wiring for the retro gate | CT-SPEC (pending) | pending | done | CT-01 | gate-hooks · done | integrated (merge 760b154, lane 697e1da = 0c2748e + repairs dec8425, 697e1da), published `0a68dce`; retro passed (`retro:gate -- gate-hooks` rc 0); cold review PASS-with-P2, re-review PASS a221b354, repair re-review PASS-with-P3 (`reviews/ccm-20261013/phase3/I1b-review.md`); record corrections per SYNTHESIS §4 |
| CT-02b (pending issue) | Gate follow-up: token-anchored verbs, heredoc strip, no-commit deny, dry-run and time flags, deadline deny-with-reason, corpus test, hooks_install guard (publish first), two-Stop-hook compose test | CT-SPEC (pending) | pending | blocked | CT-02 | not allocated · wave 1 #1 | proposed; parent hunk: `hooks:install` row; owns reviewer P3-2, P3-5 and the re-review P3 of gate-hooks |
| CT-03 (pending issue) | Team roles, rules, vocabulary | CT-SPEC (pending) | pending | done | — | team · done | integrated (merge 7e22d13), published `28fedf1`; retro passed |
| CT-04 (pending issue) | Guidance hierarchy | CT-SPEC (pending) | pending | done | — | nav · done | integrated (merge fa892d2), published `28fedf1`; retro passed |
| CT-05 (pending issue) | Lane-record validator (lane:set, lane:validate staged and from-journal, derived retro, network admission, import_source.data, published-on-origin, holds, T-B8) and ticket ledger generator | CT-SPEC (pending) | pending | READY | — | not allocated · wave 1 #3 | proposed; imports `dev/doctor/lanes.py` predicates |
| CT-06 (pending issue) | `/lane-retro <unit>` | CT-SPEC (pending) | pending | blocked | CT-01, CT-03, CT-19 | not allocated · wave 3 | proposed |
| CT-07 (pending issue) | Codex compatibility (roles and config; mirror test) | CT-SPEC (pending) | pending | blocked | CT-02, CT-03 | not allocated · wave 3 | proposed; coordinate with dynamic-agents ticket 30, which also targets `.codex/` |
| CT-08 (pending issue) | Baseline transition v2 (`.gitignore`; `.agent/` decision) | CT-SPEC (pending) | pending | held | user admission (D6) | not allocated · wave 4 | proposed; the only ticket touching a frozen baseline file; not a prerequisite of CT-21 |
| CT-09 (pending issue) | Tool adoption decision table | CT-SPEC (pending) | pending | READY | — | not allocated · wave 3 | proposed; doc-writer |
| CT-10 (pending issue) | codex-session-history coverage, eval loop, mask, `codex_status.py` (status write, supersede, terminal field), activation manifest-line test, brief composer | CT-SPEC (pending) | pending | READY | — | not allocated · wave 4 | proposed; the supersession operation was sweep B (before 2026-10-19) |
| CT-11 (pending issue) | Serialize named checks (lock) and `JOURNAL/checks/` receipt line | CT-SPEC (pending) | pending | READY | — | not allocated · wave 1 #2 | proposed; the wave-0 one-line doctor call in `check.py` precedes the cut |
| CT-12 (pending issue) | Wire every development test (`test:retro-gate`, unwired_tests rule, exemptions data, AGENTS line-cap and pointer checks) | CT-SPEC (pending) | pending | blocked | CT-22a | not allocated · wave 1 #6 if admitted, else 2 | proposed; no `check.py` edit; no `retro_gate.py` alias |
| CT-13 (pending issue) | Grilling-question mod (AskUserQuestion) | CT-SPEC (pending) | pending | held | D14 | user-typed | proposed; live prevention for P1-8 |
| CT-14 (pending issue) | `plugins/aggregated-research` guidance and `CLAUDE.md` importer | CT-SPEC (pending) | pending | READY | — | not allocated · wave 3/4 | proposed |
| CT-15 (pending issue) | Planning-file shape, `plan:log`, `plan:handoff` write and check, `check:planning` runner | CT-SPEC (pending) | pending | READY | — | not allocated · wave 1 #4 | proposed; one-time migration = Runbook step 9 |
| CT-16 (pending issue) | Settings composition check (`dev/doctor/settings.py` rule, `settings_check.py` alias) | CT-SPEC (pending) | pending | blocked | D4, CT-22a (sequential) | not allocated · wave 1 (sixth lane) or 2 | proposed; file-disjoint from CT-22b |
| CT-17 (pending issue) | Lane lifecycle: `lane:allocate`, `lane:integrate`, `session:status`, `stop_gate` extensions | CT-SPEC (pending) | pending | blocked | CT-01, CT-02, CT-05, CT-11, CT-22a, CT-24 | not allocated · wave 2 #1 | proposed; split allocate/status from integrate past 300 lines |
| CT-18 (pending issue) | A09 batch publish wrapper (refuses `MERGE_HEAD`; doctor publish surface first) | CT-SPEC (pending) | pending | blocked | CT-02, CT-22a | not allocated · wave 2 #3 | proposed |
| CT-19 (pending issue) | Slotted briefs, agent constants, reviewer and retro-writer fixes, SubagentStop receipt journal, brief-size rule in `agent_gate` | CT-SPEC (pending) | pending | blocked | CT-02, CT-03, CT-05 | not allocated · wave 2 #2 | proposed; parent hunk: SubagentStop matcher entry |
| CT-20 (pending issue) | `agent-session-history` skill, `/session-review`, transcript detectors, doctor sweep surface | CT-SPEC (pending) | pending | blocked | CT-07, CT-10, CT-22 | not allocated · wave 4 | proposed; absorbs C3's sweep ticket |
| CT-21 (pending issue) | CT-21: Import Codex worktree inputs and cited evidence; fail closed on missing inputs | CT-SPEC (pending) | pending | READY | — | ct21-codex-imports (allocated-pending-merge) · wave 1 #5 (D24) else wave 2 first | proposed; designed: reviews/ccm-20261013/T2-import-lane-design.md; imports 119 files (1,057,200 B) from imports/codex-worktrees-20261013 (MANIFEST 259f9fae…); unblocks #69 and the #63–#68/#71–#74 closure rows; lane record uncommitted, retro pending |
| CT-22 (pending issue) | Doctor core (`dev/doctor/**`, six surfaces, context format, proven-by-git fix, snapshot); CT-22a = wave-0 slice | CT-SPEC (pending) | pending | READY | — | not allocated · wave 0 (22a), wave 1 heavy slot or 2 (22b) | proposed; parent hunks: settings SessionStart entry, `check.py` line, `check:research` += `test:doctor`, `hk.pkl` records step |
| CT-23 (pending issue) | Session hooks follow-up: thresholds via env, `ctx:status`, phase and next extraction in `prompt_hook`, `agent_gate` roster-drift context | CT-SPEC (pending) | pending | blocked | CT-19 (sequential on `agent_gate.py`), CT-22 | not allocated · wave 3 | proposed; wave-0 seeds exist |
| CT-24 (pending issue) | Decisions ledger: `plan_decide.py`, `decisions.jsonl` format, `plan:decide`, `issue-tracker.md` paragraph | CT-SPEC (pending) | pending | READY | — | not allocated · wave 1 (small) | proposed; wave-0 seed |
| CT-25 (pending issue) | ticket-frontier orchestration skill (`scripts/frontier.py`, `frontier-scheduler` agent, executor gate G1-G7, learning ledger; K1 §8) | CT-SPEC (pending) | pending | blocked | CT-05, CT-15, CT-17, CT-19, CT-22, CT-24 | not allocated · wave 3 | proposed (D32; D27–D41 accepted 2026-10-13); skill name `ticket-frontier` (D34); K2 prototype under `.claude/skills/ticket-frontier` is not a lane output until CT-25 is allocated |

## Closure prerequisites (#62–#78, sweep B)

Source: `reviews/ccm-20261013/codex-sweeps/B-packet-and-t4-state.md` §1. Common holds for every row:
(a) qualified acceptance-close (`issue:completion-preview` → `issue:apply` → `issue:verify`,
evidence JSON binding acceptance, review, retro and delivery receipts; the T3-extended
`dev/issue_amend.py` at the tip is that tool), (b) fresh live issue, body, label and edge preimages,
(c) peer issue-write slot release, (d) per-issue admission, (e) settled retro and parent acceptance,
(f) prerequisite ticket disposition. Every inventory binds source `d2a41032` and the T1
`check:research` receipt `5a235e38…`; both are behind the tip. Of 23 bound files re-hashed at
`9cd396a`, 19 match and 4 drifted (`mise.dev.toml`, `docs/onboarding.md`, `dev/issue_amend.py`,
`dev/test_issue_amend.py`), so every `CODE_CRITERIA_READY` verdict was reviewed against pre-T3
bytes.

| Issue | Packet verdict | Still required before a qualified close | Hash-bound inputs and drift | Inventory status |
|---|---|---|---|---|
| #62 A01 | `CODE_CRITERIA_READY` (reviewer `/root/a01_archival_review`) | common (a)–(e); the final parent closure packet; limits: A09 original publish-process receipts not located, A12a owns CI, Claude/container acceptance pending | six files match; drifted: `mise.dev.toml` (`c4b5d68f`→`81f7dfcd`), `docs/onboarding.md` (`ef9732b8`→`3e65c4dd`) | inventory JSON + criteria + archival review in packet |
| #63 A02 | map PASS; readiness `PARTIAL_NOT_YET_READY` | #62 disposition; independent review of the archival supplement; accept "producer exit / wire-request count unbound" as an evidence disposition; common (a)–(d) | captures only in `2a14` (import = CT-21); `dev/github_search_one_page.py` hash not recorded (drift unknown) | archival supplement awaiting review |
| #64 A03a | `CODE_CRITERIA_READY` | #66 (→#63) disposition; common (a)–(e) | `dev/collect_saved_search.py` and test match; capture `…8385f42d…` only in `2a14` | inventory + criteria review |
| #65 A03b | `CODE_CRITERIA_READY` | #64 disposition; common | `dev/control_saved_search.py` and test match; capture `…59b358fe…` only in `2a14` | inventory + shared 65/66/67 review |
| #66 A04 | `CODE_CRITERIA_READY` | #63 disposition; common | `dev/search_catalog.py`, test, `dev/saved-searches.toml` match; two fixture captures only in `2a14` | inventory + shared review |
| #67 A05a | `CODE_CRITERIA_READY` | #65 and #66 dispositions; common | `dev/search_compare.py` and test match | inventory + shared review |
| #68 A05b | `CODE_CRITERIA_READY` | #67 disposition; common; no fresh live or provider claim | `dev/search_publish.py` and test match; comparison receipt `…96dbbeb7…` only in `2a14` | inventory |
| #69 A06 | none (unit3 "independently accepted"; Claude integrated `8f783a0`) | a closure inventory; the CT-21 import of the retained corpus and schema; full ticket acceptance; common | lane `integration_base_head 848552cd`, `candidate_sha256 96b5dd74…`; corpus and schema only in `2a14` | never written |
| #70 A07a | `CODE_CRITERIA_READY` | #66 disposition; T3 current-helper-byte refresh; common | drifted: `dev/issue_amend.py` (`3983910e`→`63f59b20`), `dev/test_issue_amend.py` (`a73e3ab9`→`21716791`), `mise.dev.toml`; `docs/agents/issue-tracker.md` `d3a2b79d` | inventory |
| #71 A07b | `CODE_CRITERIA_READY` on frozen inputs + cached `graph/spec11.json` | #70 disposition; helper-byte refresh; fresh live #11 postimage read; common | `retros/A07b.md` matches; `spec-11-amendment-candidate.{md,json}` and `A07b.*` intents only in `2a14` | inventory |
| #72 A08a | none | an inventory and criteria map, independent criterion review, then common (a)–(f) | nothing hash-bound in the packet; tip commit `3972f3b`; cited `graph-audit.json` only in `2a14` (import = CT-21) | not prepared |
| #73 A08b | none | as #72 | nothing hash-bound in the packet; tip commit `906cdbc`; cited `local-edge-receipt.json` only in `2a14` (import = CT-21) | not prepared |
| #74 A09 | none | as #72 | nothing hash-bound in the packet; `a09-history-scan-triage.md` and `a09-scan-adjudication.json` only in `2a14` (import = CT-21) | not prepared |
| #75 A10 | none | as #72 | nothing hash-bound; tip commit `bcf9760` | not prepared |
| #76 A11 | none | as #72 | nothing hash-bound; tip commit `42d94f9` | not prepared |
| #77 A12a | none | as #72 | nothing hash-bound; tip commit `a8ecd40` | not prepared |
| #78 A12b | none | as #72, plus A06 (#69) acceptance | nothing hash-bound | not prepared |

## T4 state (#79–#82, #101)

T4 recovery attempt 3 (`recovery-attempt3/TERMINAL.json`): `STOPPED` / `NOT_COMPLETED`, reason
`TimeoutError; stop all new sends`, 1,672 of 3,600 active seconds, 99 commands. Children batch RF1,
RF2, RF3a, RF3b, RF4, W1 closed and `VERIFIED` (`sent: true`), 25 labels `VERIFIED`. Parent batch
#79–#82: previews ran (commands 096–099, exit 0), then `checkpoint-refusal-parents.json` = `REFUSED
/ MISSING_APPROVAL_WAIT_EXHAUSTED` after a 901.8 s wait (cap 900 s); no parent completion was
applied. Budgets: `original_budget 3/3`, `recovery_budget 3/3`; `phase-c-policy-v2.md` "does not
grant a fourth attempt". Postimages in
`~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/t4-parent-metadata/postimages/`
target three repo files (`docs/research-feedback-retro/README.md`, `ticket-draft.md`,
`workflow-authority-amendment.md`), all drifted from `9cd396a`; `docs/remaining-work/README.md` and
`tracker.json` were never produced. A new attempt needs a fresh user-approved budget, a fresh
issue-write interval, a repeated children-state preflight and parent packets rebuilt from fresh
preimages (D25). No release of the T4 issue-write interval after attempt 3 is recorded.
