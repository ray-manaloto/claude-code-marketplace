# Revised ticket graph for spec #11 — review draft

This revision applies the [adversarial review](/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/docs/agents/full-baseline-ticket-review.md). No sub-issues have been published. Each numbered ticket is a fresh-context, reviewable unit (about five maintained files and 300 handwritten changed lines); a ticket that proves larger must be split before implementation. Native GitHub dependencies below express necessary ordering, but issue closure alone never admits downstream work: the blocker also needs a successful acceptance disposition, independent review and receipts bound to the same inputs. An incomplete or failed required mode remains open/blocked; a negative diagnostic result is recorded without falsely unblocking release. Only one implementation writer per Git common directory and one host-wide heavy operation may run.

The existing qualified reflection baseline and Tasks 01–13 are inherited inputs. Tickets 01–12 finish native Tasks 14c–20 before product migration. Tickets 13–18 are source/decision preparation and may be done while native work proceeds; ticket 19 is the first backend migration and is blocked by the native foundation gate. Every provider and host operation preserves the public `ray-manaloto` marketplace, `aggregated-research` plugin, existing `trackers` CLI behavior and data paths.

| # | Title | Blocked by | What it delivers |
| --- | --- | --- | --- |
| 01 | Seal Task 14c failed LSan closure | None | Commit the reviewed timeout/closure evidence and exact source identities so a fresh agent can reproduce the known blocker. |
| 02 | Private LSan repair verdict (14c1) | 01 | Capture the runtime link recipe and compare original/patched clean, leak and overflow witnesses under admission; a negative verdict remains explicit. |
| 03 | Installed LSan guard preparation | 02 | If the private repair qualifies, prepare a reviewed ASan/TSan/LSan overlay, exact preimages, backup/recovery and drift refusals without installing it. |
| 04 | Guarded LSan promotion | 03 | Under fresh ownership and lease, install the reviewed repair and qualify LSan and LSan+UBSan with clean and deliberate-error controls; only a successful qualification closes this blocker. |
| 05 | GCC sanitizer witnesses (Task 15) | None | GCC ASan, UBSan and combined modes produce clean/error receipts; unavailable Darwin modes are evidenced rather than assumed. |
| 06 | P2996 admitted-family coverage (Task 16) | None | Real output, merge and report work for already-qualified P2996 ASan/UBSan/TSan families, with missing cells explicit. |
| 07 | GCC coverage cells (Task 16) | 05 | Real GCC coverage output, merge and report work for each admitted GCC family. |
| 08 | LSan coverage cells (Task 16) | 04 | Real LSan and LSan+UBSan coverage output, merge and report work after the installed runtime qualifies. |
| 09 | Reflection-core analysis commands (Task 17) | None | Pinned format, clangd, tidy, IWYU, cppcheck and cache commands check the actual core and preserve failing exits. |
| 10 | Relocated CMake Config consumers (Task 18) | None | Independently relocated static and shared consumers find the installed core and transitive dependencies. |
| 11 | Native CPS consumers (Task 19) | 10 | Independently relocated CPS-only static and shared consumers find the same target model. |
| 12 | Native foundation acceptance (Task 20) | 04, 05, 06, 07, 08, 09, 10, 11 | Fresh-shell, warm-cache, drift and admitted matrix receipts prove all required native foundation modes before backend migration. |
| 13 | Pin legacy trackers behavior and ownership | None | Capture the external knowledge-base commit, public `trackers` output/data fixture and import boundary without editing that other repository. |
| 14 | Measure Python bridge placement | 13 | Compare embedded versus helper-process paths and select a rollback-capable bridge from actual CLI behavior. |
| 15 | Issues schema and generator qualification | 13 | One canonical Issues request/result catalog yields Python and strict POD-style C++ records with missing/null and extension-data fixtures. |
| 16 | Admit Issues transport dependencies | None | Select and qualify a bounded JSON/HTTP or `gh` process transport with compiler/runtime provenance and no implicit global install. |
| 17 | Additive CLI extension contract | 13 | Define how new operation verbs coexist with the exact `trackers` help/output/data contract and update only the corresponding acceptance assertion. |
| 18 | Measure Context7 JavaScript bridge | 14 | Qualify an installed-version Context7 bridge/runtime path and record quota and confined-install effects before the operation migrates. |
| 19 | Native GitHub Issues tracer | 12, 14, 15, 16, 17 | A typed Issues call crosses the native core and additive CLI seam, matches the pinned legacy fixture, and rolls back safely. |
| 20 | Tagged batch and outcome tracer | 19 | Two public calls retain stable IDs, missing/null distinctions, attempts, failure, partial and cancellation statuses through the CLI. |
| 21 | Identity registry tracer | 20 | Public Issues results and a second-route fixture distinguish provider, route, upstream, corpus, capability and model identity. |
| 22 | Borrow lifetime and cancellation | 20 | The single-thread event loop retains pointer/count views until final borrow acknowledgment, including cancellation; negative lifetime control fails as expected. |
| 23 | Immutable raw attempt artifacts | 20 | A CLI run yields hash-verified raw attempts and source artifacts without rewriting failures or partials. |
| 24 | GitHub source-at-ref operation | 21, 22, 23 | A typed source-at-ref call captures pinned primary-source bytes with provenance for a material comparison. |
| 25 | GitHub Discussions operation | 21, 22, 23 | A typed Discussion search uses a Discussions-enabled positive-control target and distinguishes verified empty from disabled/unavailable. |
| 26 | GitHub Releases operation | 21, 22, 23 | A typed Releases call returns provenance and explicit failure through the new CLI seam. |
| 27 | Exa operation | 21, 22, 23 | A typed Exa call returns raw provenance and an honest route result through the new CLI seam. |
| 28 | Firecrawl operation | 21, 22, 23 | A typed Firecrawl call records primary credits exhaustion and any provisional substitute as separate attempts. |
| 29 | Context7 operation | 18, 21, 22, 23 | A typed Context7 call crosses the qualified JS bridge, preserving source identity and quota failure. |
| 30 | Last30Days operation | 21, 22, 23 | A typed Last30Days plan retains its source routes and validator failure without treating its Exa route as another upstream. |
| 31 | Research-plan validation | 20, 21 | The CLI validates required capabilities, corpora, primary standards, freshness, budgets and fallback policy before dispatch. |
| 32 | Independent-source coverage verdict | 24, 27, 30, 31 | A material comparison uses primary evidence and two independent deduplicated upstreams/corpora, separate from process exit. |
| 33 | Bounded failure and controlled-empty verdicts | 25, 31 | Public runs distinguish quota, auth, rate limit, bounded timeout, transport failure and controlled empty with a same-capability positive control. |
| 34 | Equivalent fallback decision | 28, 31, 32 | A failed primary attempt remains visible while only an evidenced capability-and-corpus-equivalent route can satisfy the plan. |
| 35 | Deterministic bounded cache | 23, 31 | Repeated CLI calls reuse only fresh, scope-compatible successes with visible key/provenance; failures and auth-scoped data do not leak. |
| 36 | Optional inference attribution | 31, 32 | Model-free research has no inference usage; an opt-in fixture reports actual route/model/usage and measured or unknown cost without new paid spend. |
| 37 | Native core delivery to Claude plugin | 10, 19 | A measured package/install path supplies the native core in the confined plugin environment while retaining the pipx-only rollback and public identity. |
| 38 | Full Claude CLI/data parity receipt | 24, 25, 26, 27, 28, 29, 30, 32, 33, 34, 35, 36, 37 | Receipt-only comparison proves `trackers` unchanged and all new operation verbs/data paths compatible with their declared baselines. |
| 39 | MCP read-only research tracer | 20, 22, 23 | A client lists and calls one real read-only research tool and accepts validated structured result and text fallback. |
| 40 | Generated MCP operation catalog | 24, 25, 26, 27, 28, 29, 30, 39 | Common contracts generate typed read-only tools for each operation; tools/list and tools/call agree with the CLI schema. |
| 41 | Opt-in mutation and private-upload guard | 40 | A controlled fixture proves default denial; explicit profile and per-run destination allow a named opt-in path without default private-byte upload. |
| 42 | Generated thin Claude adapter | 37, 40, 41 | Claude registration is generated from common contracts, retains public plugin/hook identity and invokes the shared core. |
| 43 | Fresh Claude plugin/session acceptance | 38, 42 | A fresh install/session exercises the real hook, CLI, MCP research call and confined data path. |
| 44 | Codex adapter | 40, 41 | A version-qualified generated registration loads from an unrelated cwd and invokes the read-only MCP contract. |
| 45 | Antigravity adapter | 40, 41 | Installed-version inventory precedes generated skill/MCP registration and unrelated-cwd invocation; absent host remains a recorded blocker. |
| 46 | OpenCode adapter | 40, 41 | Installed V1/V2 contract inventory precedes generated skill/MCP registration and unrelated-cwd invocation. |
| 47 | Cross-host schema and loader acceptance | 43, 44, 45, 46 | Fresh host sessions prove generated models, missing/null fields, tools/list and tools/call agree with the common contract. |
| 48 | Final native requalification | 38, 47 | On the final product HEAD, rerun admitted native matrix and relocated Config/CPS consumers so foundation evidence is not stale. |
| 49 | Provider acceptance | 32, 33, 34, 35, 36, 47 | Live provider receipts satisfy the declared five-route plan, or remain explicitly incomplete for quota, disabled Discussions or provisional fallback. |
| 50 | Admitted OCI release acceptance | 43, 47, 48, 49 | Separately admitted full Claude/container acceptance records actual exits, source IDs, reviewer disposition and remaining release blockers. |

The mechanically eligible set at draft time is 01, 05, 06, 09, 10, 13 and 16. Eligibility does not authorize parallel writes or host-heavy execution; the sole writer chooses one unit and obtains its specific admission. If ticket 02 finds no viable repair, tickets 03/04/08/12/19/48/50 remain blocked until the required LSan mode is qualified or the user revises that requirement. Current strict-five research remains incomplete; no ticket silently waives provider quotas or credits.
