# Marketplace onboarding and C++ foundation

PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`
Plan and integration-branch owner: parent Codex chat. Current writing is
serialized across the Git common directory; review agents are read-only.
Project root: `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`.
Set `PWF_PLAN_ROOT` to that root and `PLAN_ID` above for commands launched elsewhere.
The detached `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`
retains its uncommitted work and private evidence. Do not reset or archive it.

## Objective

Qualify native Codex onboarding while preserving the Claude marketplace and OCI
acceptance contracts. The accepted product direction is incremental migration
to a native C++26 P2996 research core; build/toolchain work follows onboarding.

## Small units

Each unit has one purpose, at most about five maintained files and 300 handwritten
changed lines. Generated evidence is checked mechanically. Settle each unit's
acceptance before admitting dependents. The parent owns this plan and serializes
implementation and integration under the current common-directory boundary.

| Unit | Deliverable | Gate | State |
| --- | --- | --- | --- |
| N0 | Ownership, plan, live bounded team | Identity, source hashes, worker ACKs | Complete |
| N1 | Root/scoped guidance and accepted decisions | Source comparison; documentation review | Complete |
| N2 | Necessary project Codex config and roles | Exact CLI schema; merged transports; role loading | Complete |
| N3 | Separate development commands | No install/bootstrap; lightweight checks; OCI bytes preserved | Complete |
| N4 | Fresh-session qualification and handoff | Worktree and unrelated-cwd probes; cold review | Complete |
| 01a | Acquire exact template/helper/generator source and licenses | Pinned paths, hashes, immutable research preserved | Complete |
| 01b | Small scratch preset adaptation and reuse ledger | License attribution; safe includes; independent review | Complete |
| 04a | Global tool ownership inventory and prepared patch | Concurrent-writer census; exact preimages; independent review | Complete |
| 04b | Managed build tools and named environments | Ownership admitted; native configuration and environment checks | Complete |
| 02a | Pinned TCPM source and local development environment | Blob/source identity, locked dependencies, CLI smoke | Complete |
| 02b | Representative native preset matrix | Deterministic regeneration, exclusions, four native preset kinds | Complete |
| 05a | GCC16 source/package inventory and prepared native bootstrap | Exact current mise contract, package identities and reviewed isolation | Complete |
| 05b | Captured GCC bottles and installation preparation | Archive hashes, complete prefix writes, protected preimages and independent review | Complete |
| 05c | Guarded native four-bottle installation | Immediate ownership/preimage/plan checks, native exit code, installed links and preserved defaults | Complete |
| 05d | GCC16 environment and reflection witness | Exact compiler/stdlib/SDK identity, positive compile/link/run and negative flag control | Complete |
| 10b | GCC16 CMake toolchain fixture | Intended compiler/SDK/libstdc++, four Multi-Config build/test cells and isolation controls | Complete |
| 03a | Minimal native library, POD facade and smoke executable | Qualified GCC static/shared builds; private reflection flags; original acceptance hashes | Complete |
| 06a | Pinned LLVM source and bounded bootstrap recipe | Exact commit/tree and license; matching runtimes; source-only acquisition and independent review | Complete |
| 11a | Pinned vcpkg source and native registration preparation | Exact tool and registry provenance; isolated native link contract; independent review | Complete |
| 11b | Private native vcpkg bootstrap | Pinned binary checksum, ARM64 execution, root discovery and independent review | Complete |
| 11c | vcpkg promotion preparation and project manifest | Reviewed namespace-only helper; controlled guards; native manifest check | Complete |
| 11d | Scoped global vcpkg promotion | Fresh ownership/preimages; exact reviewed helper; native global discovery | Complete |
| 06b | Guarded P2996 outer configure | Fresh shared capacity; exact inputs; generated runtime commands; independent review | Complete |
| 07a | Guarded cold-build preparation | Nested build limits, durable logs, timeout/reserve controls; independent review | Complete |
| 07b | Native P2996 cold build | Fresh capacity and lease; actual final exit; child caches and artifact review | Complete |
| 07b1 | SDK comparator repair preparation | Exact five-file patch; negative and positive syntax controls; independent review | Complete |
| 07b2 | Guarded SDK source adaptation | Exact source postimages; native apply/reverse checks; independent review | Complete |
| 07b3 | Guarded incremental restart preparation | Applied-source and history binding; drift controls; independent review | Complete |
| 07b4 | Native incremental LLVM restart | Fresh admission; final native exit; runtime and artifact review | Failed; closure verified |
| 07b5 | SDK math compatibility scratch controls | Reproduced macro failure; smallest source repair; boundary test; independent review | Complete |
| 07b6 | Guarded math source application preparation | Exact two-header patch; prior source/build preservation; independent review | Complete |
| 07b7 | Guarded math source application | Exact seven-file source state; reverse check; retained build state; independent closure | Complete |
| 07b8 | Guarded math-adapted restart preparation | Both source adaptations; child build/history bindings; independent drift review | Complete |
| 07b9 | Native math-adapted LLVM restart | Fresh capacity and lease; final native exit; runtime and artifact review | Complete |
| 07c1 | Guarded private installation preparation | Reviewed scripts and build bindings; prefix/manifests/aliases; independent guard review | Complete |
| 07c2 | Native private LLVM installation | Fresh admission; three native exits; complete prefix inventory; independent artifact review | Complete |
| 07d | Private P2996 reflection and runtime witness | Named environment; exact headers/runtime origins; positive and negative controls; independent review | Complete |
| 07e1 | Native P2996 registration preparation | Private namespace discovery; exact preimages and scope; independent guard review | Complete |
| 07e2 | Scoped native P2996 registration | Fresh ownership and preimages; exclusive promotion; global discovery and independent review | Complete |
| 08a | LLVM formatting, clangd and archive fixture | Actual formatted reflection compile/archive/link/run; isolated clangd CDB check; independent review | Complete |
| 08b | LLVM tidy and static-analysis controls | Intended diagnostics and failing exits; corrected clean cases; reflection parsing and independent review | Complete |
| 08c | LLVM source-based coverage fixture | Fresh reflection profiles; exact branch counts; missing-data control and independent review | Complete |
| 10a1 | P2996 CMake toolchain preparation | Exact compiler/runtime contract, native CMake link propagation and independent source review | Complete |
| 10a2 | Native P2996 CMake fixture | Actual ABI/custom probes, four build/test/runtime cells, isolation controls and independent review | Complete |
| 03b1 | Native core P2996 compatibility preparation | Compiler-specific guards, private flags, honest CTest exits and independent source review | Complete |
| 03b2a | Native core command acceptance rules | Recorded native command replay, rejection controls and independent review | Complete |
| 03b2b | Native core two-compiler qualification | Static/shared four-configuration cells, runtime origins, failure controls and independent review | Complete |
| 09a | Pinned IWYU source and matching-fork build preparation | Exact source/license identity, native LLVM package contract and independent review | Complete |
| 09b | Guarded private IWYU build and installation | Fresh shared capacity, exact compiler/link commands, native exits, dependencies and independent review | Complete; runtime drift reattested in 09b1 |
| 09b1 | Reattest replaced mise runtime | Exact single-path change, existing profile parity, protected-state checks and independent review | Complete |
| 09c1 | IWYU reflection advice and fixer | Exact include recommendations, restricted fixer, native rebuild/run and clean reanalysis | Complete |
| 09c2 | IWYU copied-resource relocation | Moved-copy identity, explicit resource override, actual header trace and negative control | Complete |
| 12a1 | Shared vcpkg chainloader preparation | Pinned source boundaries, policy/flag composition and bounded CMake controls | Complete |
| 12a2 | P2996 overlay triplet preparation | Explicit ABI inputs, environment tracking, dual configurations and script controls | Complete |
| 12b1 | GCC16 overlay triplet preparation | Shared-input reuse, GCC ABI entries and focused script controls | Complete |
| 12c1 | Private vcpkg execution preparation | Reviewed source binding and native fail-closed receipt | Prepared; native held by shared drift |
| 12c1a | Observed mise update reattestation | Exact metadata changes, preserved compiler guards and existing profile parity | Complete |
| 12c1b | Private vcpkg qualification retry | Qualified shared state; fresh capacity; copy, confinement and host-tool selection | Complete |
| 12c2a | pkg-config prerequisite preparation | Exact native profile discovery, provisioning source/ownership contract if required | Complete |
| 12c2b | Guarded native pkgconf installation | Reviewed write set; fresh capacity; native exit, links, package lookup and preserved defaults | Complete |
| 12c3a | Qualified pkgconf ABI and fmt build inputs | Exact selection guards, retained ABI entries and bounded CMake controls | Complete |
| 12c3b | Private native fmt builds | Reviewed build/configure limits; fresh capacity; native exits, detector and ABI receipts | Complete |
| 12c3c | Application and fmt consumer parity | Public vcpkg composition; eight build/run cells; actual loader paths and preserved dependency roots | Complete |
| 13a | Native baseline preset preparation | Deterministic TCPM generation; eight trees, 32 cells, independent linkage and four preset kinds | Complete |
| 13b | Native baseline matrix | Eight isolated preset trees; 32 build/test/runtime cells; independent linkage and exact dependency mapping | Complete |
| 14a | LLVM ASan/UBSan runtime witnesses | Pinned source contract; clean reflection consumer and deliberate memory/overflow diagnostics | Failed; closure verified |
| 14a1 | Private ASan startup repair | Exact source patch; original timeout control; seven sanitizer cases; independent review | Complete |
| 14a2 | Installed ASan guard preparation | Exact single-file overlay; preserved guard chain; confined replacement controls | Complete |
| 14a3 | Installed ASan promotion | Exact backup/recovery; fresh ownership; installed-path sanitizer witnesses | Complete |
| 14b | P2996 TSan and TSan+UBSan witnesses | Ordered clean case; data-race and overflow diagnostics; exact runtimes | Failed; closure independently verified |
| 14b1 | Private TSan startup repair trial | Exact TSan link recipe; original/patch A/B witnesses; no installed write | Complete |
| 14b2a | Installed TSan guard preparation | Composed ASan/TSan inventory overlay and private exact-file controls | Complete |
| 14b2b | Guarded installed TSan promotion | Exact prior/next identities, fresh admission and five installed-path witnesses | Complete |
| 14c | P2996 LSan and LSan+UBSan witnesses | Clean/leak/overflow diagnostics, exact runtime and private builds | Blocked: installed LSan clean exit deadlocks during leak scan; closure verified |
| 14c1 | Private LSan stopped-world repair preparation | Exact pinned-source hunk, syntax control and independent review | Planned |

## Full-baseline spec workflow

The user expanded the requested spec to the complete accepted research baseline,
including the remaining build foundation and thin Claude, Codex, Antigravity
and OpenCode adapters. The PDF updater and SBE/firmware phase remain excluded.
GitHub Issues will hold one spec and bounded dependency-linked tickets. A
standby Claude takeover runbook is required before long implementation work.
The one-writer and per-unit gates above remain in force.

| Unit | Deliverable | Gate | State |
| --- | --- | --- | --- |
| W0 | Configure skill tracker, labels and domain-doc routing | User-reviewed draft, exact Git identity, lightweight checks, GitHub label verification | Complete; committed `0a7a2444` |
| W1 | Publish full-baseline spec | Accepted scope and test seams, source-backed claims, ready-for-agent issue | Complete; GitHub #11 |
| W2 | Publish context-sized ticket graph | User-approved granularity and genuine native blocking edges | Complete; 50 sub-issues #12–#61 under #11, all parent/body/label/edge checks verified |
| W3 | Standby Claude takeover document | Exact live state, issue frontier and explicit sole-writer transfer | Complete; independent final review found no material findings; standby only |
| W4 | Implement approved ticket graph | Per-worktree ownership, disjoint file scopes, bounded tests/review, per-ticket retro with all actionable findings applied and verified, then serialized integration | Independent #13/#28/#29 worktrees admitted after user-facing parallel summary; no integration or publication of those three tickets. #13 repaired pre-run review passed and one guarded private LSan trial ran; command rc 1, overall INCONCLUSIVE, patched clean case rc 86 for 120-byte leak; later read-only closure reconciliation passed. Trial and partial retro are locally committed through `65d93d1`; clean-control preparation reached `8062821` but three live census reviews withheld admission. The requested [follow-up retro](/Users/rmanaloto/.codex/worktrees/issue-13-lsan/claude-code-marketplace/.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/issue-13.md) applied offline regression gates, retry guidance and proposal retirement at local commit `5e119e5`; task validation/check/baseline and independent code/document reviews passed. The overall #13 gate remains partial. The bounded native experiment and full witness gate remain unrun. #28 offline v2 CLI contract is locally committed at `a1bd33e`; public CLI/OCI acceptance remains partial. #29 offline Context7 bridge is locally committed at `3131b89`; live provider/confined install remains partial. #30 waits for prerequisites. #12 closure committed `2cc4c029`, #24 boundary committed `931b536`, #25 helper selection committed `54d34c8b`; GitHub issues remain open at last verification |
| W5 | Reconcile the 17-point workflow clarification | Source-backed gap audit, resolved decision frontier, reviewed spec/ticket amendment, per-task retro application gate | Retrospective remediation active; A01–A05b and A09 published at `93bb798b`; A07a and A12a published at `a8ecd40b`, with hosted fast CI success; A10 planner published at `bcf97606`; A07b spec #11 body verified live; A08 publisher published at `3972f3b9`, all 17 child issues #62–#78 independently verified under #11, and all 21 new blocker edges independently verified live after A08b1 publication `623dad43`; A08b2 independently verified the complete 67-child graph, all 139 blocker edges and sole `ready-for-agent` labels on #12–#78, with handoff published at `906cdbc1`; individual acceptance and closure remain separate. A11a preflight published at `d95e3406`, A11b helper at `48027d2d`, and source handoff at `42d94f`; the guarded live switch returned rc 2 on an unexpected `.venv`, but exact checkout/retained state was independently reconciled and source-root tools/deps/static/baseline checks passed. A11 physical transfer is accepted by manual reconciliation, not an automated guard pass. A06 remains paused; #13/#28/#29 local states are recorded in W4 without source integration |

The approved historical A-index is
[automation-amendment-draft.md](automation-amendment-draft.md). Its older
"unpublished" wording and the phase notes below are preserved as history;
the W5 row above and [progress.md](progress.md) carry current publication state.
The source-branch retrospective protocol transfer and ten-record historical
audit passed local static checks and independent archival re-review. The
later ten-record archive and its linked receipts passed the same bounded
checks. Both transfers are locally committed through `9975c98`; remote
publication remains separate from A06/A12b admission.
The user approved its original fourteen-slice breakdown and blocking edges on 2026-10-12.
A01/A02 retrospectives split late A12 into A12a fast-check/hosted CI
qualification after A09 publication and A12b assembly. A04's retro split A03
into A03a bounded attempts and A03b controlled-empty verdicts. Reviewed
A01–A05b code and the A09 delivery gate are published on the integration
branch at `93bb798b`; A07a and A12a follow at `a8ecd40b`. The hosted
`research-fast` run on that exact SHA concluded success. Their GitHub
amendment issues remain unpublished.
A02 exposed a missing host SSL library
in the shared Python tool; A01 now uses a project-scoped tool install. Focused
read-only reviews of A01, A02 and A04 passed. Their retro records and local
improvements are complete. `check:research` exits 0; it is not hosted CI
acceptance. A04's nine offline controls pass and its immutable receipts remain
uncommitted. A03a passed twelve offline controls and focused review; its
final-source live receipt is bounded `partial` with `item_limit` (10/898), not
a full or controlled-empty result. Its retro applies the private-result and
timeout-safe seam to A03b. A03b passed six control fixtures and focused
review; it can promote only a complete candidate with passed same-budget
controls. Its complete and verified-empty outcomes are exercised in offline
fixtures only. A05 is split into read-only baseline/comparison A05a and
concurrency-safe public rerun A05b. A05a passed seven comparison fixtures and
focused review, with A03b normalization version 2, captured published-run
inventory, and hash-checked bytes used for comparison. Its retro requires A05b
to bind public reruns and quarantine under a per-query writer lock. A05b passed
six public offline fixtures, focused review and a bounded live command. The
live search is partial and its comparison is suppressed. A06 is paused under
the user's retrospective-action hold; no live full-inventory or NEW/GONE
result has been qualified. The [application audit](retros/application-audit-2026-10-12.md)
preserves its original snapshot and adds current statuses for the now-complete
hosted fast check, physical transfer, publication actions and remaining
ticket blockers. The user clarified that named retrospective actions
may proceed in prerequisite order to clear this hold. The user's later
parallel-worktree direction admits independent #13/#28/#29; A06 and other
unrelated tickets remain paused until the open actions are applied and
verified or explicitly rejected.
Parent ownership of this plan and the integration branch is unchanged. The
earlier separate ticket worktrees retain their files; current writing is
serialized across this Git common directory. Record each approved local slice's state and receipts; the
old GitHub frontier does not override W5. The native review and explicit parent
dispositions are in [automation-amendment-review.md](../../docs/agents/automation-amendment-review.md).
Do not reopen the twelve settled requirement interpretations or manually publish
bootstrap issues/commits. The current review-task helper is not A01 acceptance.

Onboarding is committed at `67bd4827532864ecb934050dde6c0c11b92f9939`.
Its post-commit baseline check exited 0 and the worktree was clean.
Task 01 uses the accepted pinned shortlist; this is source qualification,
not a new comparative research sweep or a runtime toolchain qualification.

## Acceptance required before completion

- Exact checkout/branch/HEAD and source provenance recorded.
- Fresh read-only sessions load project guidance using native project selection.
- Configuration and roles validate against the installed CLI, currently 0.162.1.
- Available global skills/plugins reused without copying Claude lifecycle behavior.
- Lightweight checks record actual exit codes; independent findings are dispositioned.
- Existing acceptance inputs remain unchanged; full OCI execution is explicitly pending.

## Admission and later work

Project-local lightweight work and read-only ownership/tool inventory are admitted.
Task 04a prepares the accepted later global mise phase before any host mutation.
Global settings, hooks, trust, credentials, model defaults, other projects,
containers, heavy builds, publication and destructive cleanup remain outside it.
Task 04b's bounded admission is recorded in
`evidence/tool-foundation/global-admission.json`: seven new named files and three
explicit managed build-tool versions, one installer job, no existing default
config/lock changes. The seven files were applied after preimage checks; native
installation, host qualification and independent application review passed. Broader
global ownership, compiler builds and host-heavy capacity remain unadmitted.
Task 05a permits read-only compiler inventory, primary-source acquisition and
project-local preparation. It does not authorize installation or compilation.
Task 05b prepares a bounded four-bottle operation. Download and inspect archives
privately, then record ownership, preimages and exact write targets before apply.
Canonical Homebrew writes and compiler execution await that admission record.
Task 05c's bounded installer and three review repairs have been independently
verified. `evidence/gcc-bootstrap/install-admission.json` admits only the four
reviewed native pours and two directory conversions after immediate guards.
Task 05c executed no compiler; runtime qualification follows in task 05d.
Task 05d admits sequential, sixty-second-bounded compiler probes and one tiny
reflection witness in a new private directory. The fresh census found no compiler
or build processes; this does not admit a cold toolchain or matrix build. Existing
global profiles are selected without edits; all protected preimages remain gates.
Task 10b admits only the tiny CMake fixture and sequential one-job builds in a
new private directory. Its five maintained files are the toolchain, fixture
CMakeLists/README and selected plan/progress. No dependency or compiler build,
global edit, source bootstrap or cache server is included.
Task 03a admits the root CMake file, public header, library source, smoke source
and this plan. Qualify static/shared libraries in all four configurations using
sequential one-job, sixty-second-bounded builds in new private directories.
No dependencies, installers, cache server, adapter replacement or OCI run is
included. The smoke executable is a foundation witness, not the plugin CLI.
Task 06a permits exact-source acquisition into a new private checkout and a
reviewable native bootstrap recipe. Its maintained files are the source helper,
CMake initial cache, documentation and these two planning records. No compiler
build, installation, global registration or configure probe is included;
configuration and the cold build receive separate bounded operations.
Task 11a qualifies the already accepted vcpkg commit and native mise registration
in new private directories while the shared heavy lease is occupied. Its scope
is one confined preparation helper, two documentation files and these planning
records, with generated source/experiment receipts. No bootstrap, dependency
build, global link, configuration change or shim mutation is admitted here.
No native goal was requested. Monitor chat owns no marketplace files.

Task 09a admits exact pinned IWYU source acquisition and source-only build
preparation. Its maintained files are the acquisition helper, initial cache,
IWYU documentation and these planning records. Build the tool against the
qualified fork's headers/libraries using its admitted Apple bootstrap runtime;
qualifying reflection analysis and relocation requires a later native operation.
Script-mode CMake guard checks are admitted; they configure no project and run
no compiler. Installation, global registration and shared-prefix writes are excluded.

Task 09b separately admits the reviewed one-job private IWYU operation in
`evidence/iwyu-build/admission.json`, after fresh capacity and independent
pre-run review. The runner repeats the canonical lease/census and exact input
checks before configure/build/install; shared source, LLVM prefix and defaults
remain protected. Analysis, relocation and global registration are later gates.

After N4, continue the source matrix's small tasks: template reuse qualification;
then a separately admitted global tool foundation and TCPM trial; compiler,
vcpkg, preset, analysis and package qualification follow their recorded edges.
Do not treat source-backed tool pins or 96 candidate trees / 384 cells as runtime
qualified. Preserve all inherited research failures.

## Evidence

Task 12a1 admits the P2996 composition correction, shared vcpkg chainloader,
`docs/vcpkg-toolchains.md` and these two planning files. Retained source receipts
and bounded CMake script-mode controls are allowed; no compiler detection,
dependency build, installation, shared-source mutation or cache service is
included. Native task 12 operations receive separate capacity admission.

Task 12a2 admits two P2996 triplets, their common macOS inputs and these two
planning files. Exact-source prerequisite copies and CMake script controls may
be retained. The common file may prepare the existing GCC lane, but no GCC
triplet, native compiler detection, dependency build or tool execution is
qualified by this unit. Keep dependency Debug and Release enabled and record
nested toolchain, runtime, SDK and managed build-tool ABI inputs explicitly.

Task 12b1 admits two GCC16 triplets, `docs/vcpkg-toolchains.md` and these two
planning files. Reuse the committed common inputs without changes. Bounded
CMake script controls may inspect GCC files and the chainloader; native compiler
detection, dependency builds and cache/confinement qualification remain separate.

Task 12c1 admits one private vcpkg preparation/probe helper, composition docs
and these planning files. After independent review and fresh shared capacity,
it may copy the exact vcpkg checkout and fmt inputs, select the existing named
profiles, verify managed host tools and exercise local write/network restrictions.
Keep real HOME unchanged. No dependency/compiler build, patch application,
global registration, cache provider or integration command is included.

Task 12c1a prepares an exact overlay of independently inventoried shared-state
changes. After source review it may run existing read-only profile and isolation
probes, each bounded to sixty seconds, in a new private directory. Preserve all
historical receipts and every unrelated protection check. No installation,
global write, compiler/vcpkg execution or lease acquisition is included.

See `findings.md`, `progress.md`, and `docs/agents/codex-task-orchestration.md`.
Task 12c1b admits the unchanged private vcpkg probe under the qualified 12c1a
guard and current profile receipts, after independent review and fresh capacity.
Only the helper, composition docs and these planning files are maintained.
No dependency build, compiler detection, global write or cache provider is included.
Historical handoff sources stay immutable in the source checkout and original
research directories. New receipts belong only to this worktree.

Task 12c2a resolves the pkg-config prerequisite before dependency execution.
Bounded read-only profile discovery uses the qualified shared-state guard and
private sandbox. Preparation includes one bottle-inventory helper and a private
captured-metadata dry run with a missing-metadata failure control. Prepare exact
native mise inputs and preimages for review before installation or global writes.
Keep fmt package validation enabled; no compiler or dependency build is included.

Task 12c2b prepares one guarded pkgconf installation helper, composition docs
and these planning files. Review the exact pinned archive, native command and
postimage allowlist before admission. Installation requires fresh shared capacity,
canonical lease and immediate prefix/writer checks; preserve all existing guards.
No compiler/dependency build or global mise configuration change is included.

Task 12c3a admits the common triplet, composition docs and these planning files.
Bind the already-qualified pkgconf selection and executable/runtime ABI inputs;
keep fmt as a compiled library without modules for the smallest parity witness.
Bounded CMake script controls perform no compiler detection, dependency build,
installation, lease acquisition or shared writes.

Task 12c3b prepares one private fmt build helper, composition docs and these
planning files. Review exact inputs, four ordinary manifest installs, fresh
per-triplet state and confinement before fresh capacity admission. Allow one job
per dependency build and up to two concurrent Debug/Release CMake configure
processes, including their compiler probes, within the single leased operation.
Keep compiler tracking and both dependency configurations enabled. No shared
installation, binary cache, consumer build or full matrix is included.

Task 12c3c admits the root CMake composition guard, one private consumer helper,
composition docs and these planning files. Prepare eight Debug/Release consumer
cells against the four retained fmt installations, using the actual research
core target. Disable vcpkg automatic installation and keep dependency roots
read-only. Native configure/build/run requires independent preparation review,
fresh capacity and the canonical lease. No dependency rebuild, global write,
binary cache, instrumentation family or full baseline matrix is included.

Task 13a admits root CMake integration, the existing smoke source, one native
TCPM baseline template and these planning records. Generated native preset JSON
is checked mechanically and committed. Keep core/fmt linkage independent and
use the four retained fmt installations with installation disabled. Generation
and native preset listing may run without configuring a project or invoking a
compiler. The full 32-cell native operation follows separate review and fresh
capacity admission. No dependency rebuild, cache or instrumentation is included.

Task 13b admits one private baseline runner, root target metadata, baseline docs
and these planning files. Execute the committed native presets in eight fresh
private trees with one job, all four configurations and independent core/fmt
linkage. Reuse retained dependencies read-only with installation disabled.
Native operations require independent preparation review, fresh capacity and
the canonical lease. No dependency build, instrumentation, cache provider,
shared installation or global write is included.

Task 14a admits one confined sanitizer witness runner, one public-header consumer
fixture, sanitizer docs and these planning files. Prepare ASan, UBSan and combined
runtime controls against the qualified P2996 core and runtimes. Native execution
requires independent preparation review, fresh capacity and the canonical lease.
No dependency build, preset expansion, shared write, cache or coverage is included.
Retain the first failed capacity receipt. A separately reviewed rule may admit
only the observed Zed clangd identities and ancestry, with fresh working-directory
and identity checks, CPU limits and all other existing admission guards preserved.

Task 14a1 admits one scratch runner, one source patch, sanitizer docs and these
planning files. Reuse the reviewed confinement, capacity, lease and preservation
guards. Build only private copies of the original and patched ASan runtime, using
the captured 127-object recipe and one replaced object. Require the original
startup timeout and all seven existing sanitizer cases before any later runtime
promotion. Native work requires preparation review and fresh admission; shared
source/build/prefix changes and instrumentation matrices are separate units.

Task 14a2 admits one guard/replacement module, sanitizer docs and these planning
files. Prepare exact expectations for the independently qualified ASan candidate
without changing historical inventory bytes or inherited guard functions. Pure
overlay controls and private sandboxed replacement/restore controls are allowed.
No installed write, compiler/runtime execution, capacity lease or promotion is
included. A separate native operation must bind source/build state, back up the
original, obtain fresh admission and qualify the installed runtime path.

Task 14a3 admits one promotion runner, sanitizer docs and these planning files.
Prepare one exact installed ASan replacement with a retained original backup,
explicit before/after guards and recovery while the canonical lease is held.
Private transaction controls are allowed; native mutation requires independent
preparation review and fresh capacity. Reuse the three qualified witness binaries
for all seven installed-path cases, without a loader-path override. Preserve
source Git state, bound build inputs and unrelated protected state. No compiler
or dependency build, global configuration change or full matrix is included.

Task 14b admits one confined TSan runner, one public-header witness, sanitizer
docs and these planning files. Reuse the qualified installed-ASan preservation
guard and require five TSan/combined clean/error cases with exact loader paths.
Native work requires independent preparation review, fresh capacity and the
canonical lease. No runtime replacement, dependency build, coverage, preset
expansion, shared installation or full matrix is included.

Task 14b1 permits a private original/patched TSan runtime comparison using the
already qualified mapping-object repair and the captured TSan-specific link
recipe. Keep the installed runtime and shared build tree unchanged. Verify the
original startup failure, patched clean startup and deliberate race before any
installed promotion. Require source/object provenance, separate preparation
review, fresh capacity, canonical lease and closed operation receipts.

Task 14b2a prepares a TSan installed-runtime guard against the reviewed private
candidate. Compose the existing ASan overlay with a second exact TSan-row overlay
over the two immutable historical inventories; retain the prior guard chain.
Exercise pure overlays and private confined replacement/restore/refusal controls.
No installed write, native witness, capacity lease or promotion is included.

Task 14b2b prepares one guarded installed TSan replacement from the reviewed
private candidate. Require exact source, tool, prefix and witness identities,
fresh capacity, canonical ownership lease, retained original backup and
unknown-target refusal. Run clean and deliberate-error TSan/TSan+UBSan cases
through the installed loader path; preserve ASan, defaults and unrelated prefix
entries. Collect closure and independent artifact review before completion.

Task 14c admits one confined LSan runner, one public-header witness, sanitizer
docs and these planning files. Reuse the qualified P2996 core, installed runtime,
current ASan/TSan preservation guard and native capacity/lease rules. Require
clean and leak cases in both modes plus signed-overflow detection in the combined
mode, with exact loader paths. Native compiler/runtime execution follows separate
preparation review and fresh capacity. No runtime replacement, dependency build,
shared installation, preset expansion or full matrix is included.
