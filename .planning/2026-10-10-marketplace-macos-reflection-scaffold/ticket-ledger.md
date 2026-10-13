# Ticket ledger

Every GitHub issue for this repository with its live state, frontier status, blocking edges, Claude lane and local evidence state. Regenerate the first six columns from the tracker (`gh api graphql` with `blockedBy`/`parent`); the last two are maintained by the parent at each lane transition. Frontier = open with no open blockers; a closed blocker still needs an accepted disposition before dependents start. Snapshot: 2026-10-13, integration tip `05c3dc9` (M0 merged and published), remote `05c3dc9`.

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
| [#62](https://github.com/ray-manaloto/claude-code-marketplace/issues/62) | A01 — Portable locked task bootstrap | #11 | OPEN | READY | — | CLOSE | A01 published 93bb798 (in tip); closure pending |
| [#63](https://github.com/ray-manaloto/claude-code-marketplace/issues/63) | A02 — One-page GitHubKit search receipt | #11 | OPEN | blocked | #62 | CLOSE | A02 published 93bb798; closure pending |
| [#64](https://github.com/ray-manaloto/claude-code-marketplace/issues/64) | A03a — Bounded collection and attempt recording | #11 | OPEN | blocked | #66 | CLOSE | A03a published 93bb798; closure pending |
| [#65](https://github.com/ray-manaloto/claude-code-marketplace/issues/65) | A03b — Controlled empty and completeness verdicts | #11 | OPEN | blocked | #64 | CLOSE | A03b published 93bb798; closure pending |
| [#66](https://github.com/ray-manaloto/claude-code-marketplace/issues/66) | A04 — Validated catalog and immutable recording | #11 | OPEN | blocked | #63 | CLOSE | A04 published 93bb798; closure pending |
| [#67](https://github.com/ray-manaloto/claude-code-marketplace/issues/67) | A05a — Compatible baseline and pure comparison | #11 | OPEN | blocked | #66, #65 | CLOSE | A05a published 93bb798; closure pending |
| [#68](https://github.com/ray-manaloto/claude-code-marketplace/issues/68) | A05b — Public rerun and comparison receipt | #11 | OPEN | blocked | #67 | CLOSE | A05b published 93bb798; closure pending |
| [#69](https://github.com/ray-manaloto/claude-code-marketplace/issues/69) | A06 — Codex release-schema example receipt | #11 | OPEN | blocked | #68 | CLOSE | unit1 a071340 + unit2 5acdc3a + unit3 8f783a0 integrated (24 tests, review PASS-with-P3: deeply nested TOML RecursionError → next unit); publication pending; retained-corpus consumption still open |
| [#70](https://github.com/ray-manaloto/claude-code-marketplace/issues/70) | A07a — Qualify one-issue amendment operations | #11 | OPEN | blocked | #66 | CLOSE | A07a published a8ecd40; closure pending |
| [#71](https://github.com/ray-manaloto/claude-code-marketplace/issues/71) | A07b — Apply the approved spec #11 amendment | #11 | OPEN | blocked | #70 | CLOSE | A07b applied; spec #11 body verified live; closure pending |
| [#72](https://github.com/ray-manaloto/claude-code-marketplace/issues/72) | A08a — Publish and bind ticket identities | #11 | OPEN | blocked | #71 | CLOSE | A08a published 3972f3b; closure pending |
| [#73](https://github.com/ray-manaloto/claude-code-marketplace/issues/73) | A08b — Verify and publish dependency relationships | #11 | OPEN | blocked | #72 | CLOSE | A08b verified 906cdbc; closure pending |
| [#74](https://github.com/ray-manaloto/claude-code-marketplace/issues/74) | A09 — Reviewed commit and branch publication | #11 | OPEN | blocked | #62 | CLOSE | A09 published; route used for f0d79a0/a071340/848552c; closure pending |
| [#75](https://github.com/ray-manaloto/claude-code-marketplace/issues/75) | A10 — Reviewable checkout-transfer plan | #11 | OPEN | blocked | #74 | CLOSE | A10 published bcf9760; closure pending |
| [#76](https://github.com/ray-manaloto/claude-code-marketplace/issues/76) | A11 — Apply and verify source-checkout transfer | #11 | OPEN | blocked | #75 | CLOSE | A11 accepted by manual reconciliation after guard rc 2 (42d94f9); closure pending |
| [#77](https://github.com/ray-manaloto/claude-code-marketplace/issues/77) | A12a — Qualify the portable fast-check and hosted CI route | #11 | OPEN | blocked | #74, #63, #62 | CLOSE | A12a published a8ecd40; research-fast CI passed; closure pending |
| [#78](https://github.com/ray-manaloto/claude-code-marketplace/issues/78) | A12b — Assemble the remainder amendment | #11 | OPEN | blocked | #77, #73, #69 |  | waits for A06 acceptance |
| [#79](https://github.com/ray-manaloto/claude-code-marketplace/issues/79) | [Spec] Preserve acceptance state when comparison fails | — | OPEN | READY | — | CLOSE | RF spec; children #84 #85 closed; closure review pending (T4 Phase C) |
| [#80](https://github.com/ray-manaloto/claude-code-marketplace/issues/80) | [Spec] Check the exact borrowed runtime before research launch | — | OPEN | READY | — | CLOSE | RF spec; children closed; closure review pending (T4 Phase C) |
| [#81](https://github.com/ray-manaloto/claude-code-marketplace/issues/81) | [Spec] Share refresh outcome safeguards and the improvement workflow | — | OPEN | READY | — | CLOSE | RF spec; children closed; closure review pending (T4 Phase C) |
| [#82](https://github.com/ray-manaloto/claude-code-marketplace/issues/82) | [Spec] Share the complete reusable refresh workflow | — | OPEN | READY | — | CLOSE | RF spec; children closed; closure review pending (T4 Phase C) |
| [#83](https://github.com/ray-manaloto/claude-code-marketplace/issues/83) | [Spec] Complete the remaining Marketplace session work | — | OPEN | READY | — |  | remaining-work spec; 20 children published 2026-10-13 |
| [#84](https://github.com/ray-manaloto/claude-code-marketplace/issues/84) | RF1: Preserve accepted history after comparison failure | #79 | CLOSED | closed | — |  | CLOSED by T4 Phase C |
| [#85](https://github.com/ray-manaloto/claude-code-marketplace/issues/85) | RF2: Stop unavailable borrowed runtimes before launch | #80 | CLOSED | closed | — |  | CLOSED by T4 Phase C |
| [#86](https://github.com/ray-manaloto/claude-code-marketplace/issues/86) | RF3b: Document the standing improvement workflow | #81 | CLOSED | closed | — |  | CLOSED by T4 Phase C |
| [#87](https://github.com/ray-manaloto/claude-code-marketplace/issues/87) | RF3a: Share verified refresh outcome behavior | #81 | CLOSED | closed | #85, #84 |  | CLOSED by T4 Phase C |
| [#88](https://github.com/ray-manaloto/claude-code-marketplace/issues/88) | RF4: Publish the complete reusable refresh package | #82 | CLOSED | closed | #86, #87, #85, #84 |  | CLOSED by T4 Phase C |
| [#89](https://github.com/ray-manaloto/claude-code-marketplace/issues/89) | W1: Record parallel worktree and retro ownership | #83 | CLOSED | closed | — |  | CLOSED; W1 published f0d79a0 |
| [#90](https://github.com/ray-manaloto/claude-code-marketplace/issues/90) | B1: Reconcile published source and tracker status | #83 | OPEN | READY | — | B1 (after M0) | B1 c33dcb1 in tip via M0 e0667ec; publication + closure pending |
| [#91](https://github.com/ray-manaloto/claude-code-marketplace/issues/91) | B2: Repair stale worktree attachments | #83 | OPEN | READY | — | human | B2 needs the Codex Desktop attachment operation → ready-for-human candidate |
| [#92](https://github.com/ray-manaloto/claude-code-marketplace/issues/92) | T1: Publish approved specs and tickets through the existing journal | #83 | OPEN | READY | — | M0/CLOSE | T1 in tip (c6caaca/d2a4103 + 20ff60c via M0); publication + closure pending |
| [#93](https://github.com/ray-manaloto/claude-code-marketplace/issues/93) | T3: Close tickets only from accepted evidence | #83 | OPEN | READY | — | M0/CLOSE | T3 fa3ab5c in tip via M0 e0667ec; publication + closure pending |
| [#94](https://github.com/ray-manaloto/claude-code-marketplace/issues/94) | C1: Qualify affected queries without accepting an incomplete baseline | #83 | OPEN | READY | — | C1 (integrated 52ce420+6c09b7f; closure pending) |  |
| [#95](https://github.com/ray-manaloto/claude-code-marketplace/issues/95) | C3: Diagnose the known-empty discussion search | #83 | OPEN | READY | — | C3 (released) |  |
| [#96](https://github.com/ray-manaloto/claude-code-marketplace/issues/96) | L1: Qualify a private exact LLVM bundle | #83 | OPEN | READY | — | heavy 5 | L1 heavy lane; per-run confirmation; last in heavy order |
| [#97](https://github.com/ray-manaloto/claude-code-marketplace/issues/97) | T2: Publish and audit the approved dependency graph | #83 | OPEN | blocked | #92 | M0/CLOSE | T2 0195289 in tip via M0 e0667ec; publication + closure pending |
| [#98](https://github.com/ray-manaloto/claude-code-marketplace/issues/98) | C2: Adopt the qualified runner and evaluate the retained companion | #83 | OPEN | blocked | #94 | C2 (after C1, released) |  |
| [#99](https://github.com/ray-manaloto/claude-code-marketplace/issues/99) | L2: Build and qualify IWYU for that LLVM bundle | #83 | OPEN | blocked | #96 |  |  |
| [#100](https://github.com/ray-manaloto/claude-code-marketplace/issues/100) | L3: Build the portable project consumer with upstream LLVM | #83 | OPEN | blocked | #96 |  |  |
| [#101](https://github.com/ray-manaloto/claude-code-marketplace/issues/101) | T4: Publish the new graph and reconcile completed RF history | #83 | OPEN | blocked | #93, #97, #90, #89 | M0/CLOSE | T4 Phase A/B + recovery done; 25 labels + 6 child closures verified; branch content in tip via M0; parent-spec closures (#79–#82) and source metadata pending |
| [#102](https://github.com/ray-manaloto/claude-code-marketplace/issues/102) | L4a: Qualify formatting and language diagnostics | #83 | OPEN | blocked | #100 |  |  |
| [#103](https://github.com/ray-manaloto/claude-code-marketplace/issues/103) | L4b: Qualify IWYU on the portable project consumer | #83 | OPEN | blocked | #100, #99 |  |  |
| [#104](https://github.com/ray-manaloto/claude-code-marketplace/issues/104) | L4c: Qualify the static analyzer on portable code | #83 | OPEN | blocked | #100 |  |  |
| [#105](https://github.com/ray-manaloto/claude-code-marketplace/issues/105) | L4d: Qualify a source-coverage witness | #83 | OPEN | blocked | #100 |  |  |
| [#106](https://github.com/ray-manaloto/claude-code-marketplace/issues/106) | L5a: Run locked compiler qualification in CI | #83 | OPEN | blocked | #105, #104, #103, #102 |  |  |
| [#107](https://github.com/ray-manaloto/claude-code-marketplace/issues/107) | L5b: Create exact LLVM and IWYU update PRs | #83 | OPEN | blocked | #106 |  |  |
| [#108](https://github.com/ray-manaloto/claude-code-marketplace/issues/108) | L6: Activate the merged qualified bundle through the global owner | #83 | OPEN | blocked | #106 |  |  |
