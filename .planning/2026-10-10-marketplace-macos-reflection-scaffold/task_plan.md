# Marketplace onboarding and C++ foundation

PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`
Plan owner and sole implementation writer: parent Codex chat.
Project root: `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`.
Set `PWF_PLAN_ROOT` to that root and `PLAN_ID` above for commands launched elsewhere.

## Objective

Qualify native Codex onboarding while preserving the Claude marketplace and OCI
acceptance contracts. The accepted product direction is incremental migration
to a native C++26 P2996 research core; build/toolchain work follows onboarding.

## Small units

Each unit has one purpose, at most about five maintained files and 300 handwritten
changed lines. Generated evidence is checked mechanically. Settle each unit's
acceptance before expanding it; parent writes, workers inspect and review.

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

After N4, continue the source matrix's small tasks: template reuse qualification;
then a separately admitted global tool foundation and TCPM trial; compiler,
vcpkg, preset, analysis and package qualification follow their recorded edges.
Do not treat source-backed tool pins or 96 candidate trees / 384 cells as runtime
qualified. Preserve all inherited research failures.

## Evidence

See `findings.md`, `progress.md`, and `docs/agents/codex-task-orchestration.md`.
Historical handoff sources stay immutable in the source checkout and original
research directories. New receipts belong only to this worktree.
