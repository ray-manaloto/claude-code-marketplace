# Project handoff

Updated 2026-10-11. PLAN_ID: `2026-10-10-marketplace-macos-reflection-scaffold`.
The parent Codex chat is the sole project writer; monitor
`01a122d7-dfe6-72c3-ab32-823fadb96690` is read-only. Native inspection/review workers
own no files. See the [team contract](agents/codex-task-orchestration.md).

## Identity and current state

- Worktree: `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace`.
- Branch: `codex/marketplace-native-onboarding`.
- Source HEAD: `6b5b092efa6bdf678815073db42f69fae3f07ab3`.
- Common Git directory: `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git`.
- N0–N4 implemented, independently reviewed and locally qualified.
- Onboarding checkpoint: `67bd4827532864ecb934050dde6c0c11b92f9939`; clean
  post-commit worktree and baseline check exit 0.
- Cold review passed after one receipt-minimization finding was fixed/rechecked.
- Delivery is local checkpoint commits only; no publication. Read actual
  HEAD/status before resuming; dated receipts identify their tested snapshots.

New files provide root/scoped guidance, accepted decisions, native project roles,
an explicit development wrapper, the [task index](build-roadmap.md) and sanitized
[evidence](../evidence/onboarding/README.md). All 19 original tracked files match
their baseline. Current development checks require only already installed tools.

## Limits and next action

The initial startup probe missed four bundled MCP endpoints. This is recorded;
a corrected startup-only probe loaded the project with no MCP startup notifications.
Direct protocol evidence separately qualifies custom-role assignment/completion.
Global Codex config/hooks remain unchanged. The inherited chronicle warning and
the read-only research-guard limitation are preserved.

Full Claude/OCI acceptance, MCP connectivity and provider research are unqualified.
Existing research gaps are Context7 quota, Firecrawl 402/provisional fallback and
Last30Days validation. The minimal GCC native core is now qualified as described
below. LLVM configuration and global vcpkg registration are qualified; the LLVM
reflection compiler and private runtimes are qualified below; dependency,
application-matrix and package qualification remain pending.

Task 08a passed its [formatting, clangd and archive fixture](llvm-tools.md),
including an independent reproduction and expected failing format control.
The formatted reflection source compiled and ran through a native archive with
the three private runtimes. Task 08b's tidy and static-analysis controls also pass
with independent reproduction, source preservation and unchanged defaults.
Both initial analyzer failures are retained with source-backed corrections;
Task 08c's source-based coverage fixture passed independent reproduction with
fresh raw/merged profiles, exact branch counts and a failing missing-data control.
The later application coverage cross-product remains pending.

Task 09's pinned [IWYU source and private build](iwyu-toolchain.md) passed native
installation and independent artifact verification. The shared mise executable
changed afterward to 2026.10.8; all other protected records match. Task 09b1
passed twelve read-only probes and independent review, reattesting the exact
replacement with unchanged profiles/defaults. Reflection analysis, relocation
and advice/rebuild follow separately; replacement provenance remains unknown.

Task 10a's [P2996 CMake fixture](../scratch/p2996-toolchain/README.md) passed
native ABI/custom probes, four build/test/runtime cells and eight isolation
controls with independent reproduction. Private libc++ origins and protected
state match. Library/dependency linkage qualification follows separately.

Task 01 passed: pinned source/license acquisition and the four-file
[scratch adaptation](../scratch/template-reuse/README.md) have independent
reviews and passing static/baseline checks. Native CMake preset listing now passes;
the later GCC fixture and core gates are recorded below.

Task 04a passed: the [prepared profiles](../dev/global-mise/README.md) and native
named locks have 35 bounded controls and a passing independent cold review.
The proposal is committed at `a07f40c` and preparation evidence at `605cb8d`.

Task 04b applied seven new named files and installed only CMake 4.4.4 and
sccache 0.18.0; Ninja 1.13.2 was reused unchanged. Native installation exited 0.
The [host checks](../evidence/tool-foundation/host-qualification.json) pass:
managed paths, ARM64 support, versions, profile environment controls and native
preset listing. Default config/lock bytes, compiler settings and PATH match the
pre-apply state. Independent application review passed after two recording fixes.

Task 02 passed at `ad6b63bc732afdd119262849b7873712b5d917a4`: the
[TCPM trial](../scratch/tcpm-trial/README.md) generates three trees and twelve
cells reproducibly; native CMake accepts all four preset kinds and rejects
invalid workflows. Independent review reproduced the checked-in JSON. Python
3.14 failed during generation; the successful private Python 3.13 environment
uses the same generator source and leaves global Python unchanged.

Task 05a passed: exact GCC package/source inventory and the
[native snapshot plan](../dev/toolchains/README.md) have independent review.
Both native runs resolve eight captured formulae to four missing bottles and
reject missing GCC metadata. These preparation checks do not qualify a compiler.

Task 05b has verified four downloaded archives and enumerated their prefix
writes. Two shared debugger directories require native expansion while
preserving GLib. External global tool updates triggered a preimage stop; fresh
private baselines preserve those updates. Independent preparation review passed
after parent/control preimages were completed. The later installation operation
requires fresh package-writer, exact-preimage and native-plan checks.

Task 05c installed GCC 16.2.0, ISL 0.28, MPFR 4.2.2 and libmpc 1.4.1 through
native mise after those checks. All command exit codes are 0; planned links,
GLib preservation and unchanged global/default environment checks pass.
Independent [installed-state review](../evidence/gcc-bootstrap/postinstall-review.json)
passed. Task 05d's [runtime witness](../evidence/gcc-runtime/qualification.json)
passes through the existing `gcc16` environment: GCC 16.2.0, libstdc++ 16,
ARM64 executables and the explicit macOS 27.0 SDK. Reflection compile/link/run
exits 0; omitting `-freflection` exits 1. Both feature macros are `202603L`.
Direct library loads and standard-library symbol bindings select libstdc++;
dyld resolves it to the installed prefix. macOS system libc++ images also load,
so their mere presence is not treated as compiler contamination.
Defaults and all nine global files remain unchanged. Independent
[runtime review](../evidence/gcc-runtime/runtime-review.json) passed after one
complete rerun and verification of all receipts and protected files.

Task 10b is committed at `637dbe8b0d059be519f1c4b743555ac4c75aaf24`:
the [GCC CMake fixture](../evidence/gcc-cmake/qualification.json) passes all four
configurations and isolation controls. Task 03a is committed at
`28c4e5293fecc9296c36ded73f44d0a5fa8c7b8b`: the
[native core](../evidence/core-skeleton/qualification.json) passes eight cells,
static/shared across all four configurations, with independent reproduction.
Reflection flags remain private to the implementation. A reproduced GCC Darwin
C++26 MinSizeRel duplicate-symbol defect is avoided with the target-scoped
`-fno-declone-ctor-dtor` control; the optimization and negative controls are
retained. Both post-commit baseline checks passed.

Task 03b's [two-compiler core qualification](core-qualification.md) now passes
all sixteen static/shared configuration cells, four ABI probes and seven
controls. Exports, private reflection, runtime origins and protected/default
state pass; the runner exited 0 and released the lease. Independent artifact
review passed without findings. The earlier failed PATH comparison and its correction are
retained separately; dependency and package qualification follow later.

Task 06a is committed at `fe108bce6f5226005c5082bc85fba7ae31d2aeb6`:
[pinned LLVM source and the initial cache](p2996-toolchain.md) passed independent
review and script-mode controls. That milestone ran no LLVM configuration or build.
Task 11a's [vcpkg preparation](vcpkg-toolchain.md) passed independent source review
and reproduction of all thirteen private native registration cases. This admits
no global registration. Task 11b's private native bootstrap subsequently passed
checksum, ARM64 execution and root-discovery checks with independent review.
Task 11c's project manifest and guarded registration preparation are committed
at `ad73b79b05c669574649af3c05e282ec417646e1`, with independent review and all
eight native preparation commands passing. Operation 11d has promoted the exact
reviewed vcpkg namespace after fresh writer/preimage checks. All eight commands
passed with protected state unchanged. Independent installed-state review passed,
including a fresh ARM64 consumer and all nine private backup checks.

Reproduce from this checkout using an existing Python 3.11+ interpreter and
`python3 -B dev/toolchains/gcc_reflection.py --run-dir <new-private-directory>`.
The script selects `MARKETPLACE_GCC16_PREFIX=/opt/homebrew/Cellar/gcc/16.2.0`
only in its child environment and uses an empty cwd to avoid the root OCI setup.
It writes bounded command logs and does not install tools or edit global profiles.

Task 06b's guarded outer LLVM configure passed all 14 commands after fresh
capacity checks and acquisition of the shared lease. Generated files and runtime
commands are retained and independently reviewed. Protected state is unchanged;
the lease is released. Compiler builds and runtime qualification remain pending.
Global Python promotion/telemetry and other repositories remain separate streams.

Task 07a prepares the guarded cold-build operation with explicit nested build
limits, durable logs, timeout cleanup and disk reserves. Independent preparation
review passed after two cleanup repairs. Task 07b's first native build exited 1
after 363.49 seconds: the pinned LLVM RDF comparator conflicts with the macOS 27
libc++ headers. The failed logs and incremental tree are retained; protected
shared state is unchanged. Independent failure closure passed: the lease is
free, no build processes remain, and the default environment matches. A bounded
compatibility repair is prepared in scratch: the original failure reproduces,
and all three repaired translation units pass syntax checks. Independent patch
and application-helper review passed, including reproduction and guard controls.
Operation 07b2 applied the exact five-file patch: all eleven native commands
passed, source postimages match, reverse applicability passes, protected state
is unchanged and the lease is released. Independent application closure passed,
including all 1347 recorded build outputs, eight generated files and both Ninja
state files. Compiler restart and runtime acceptance remain incomplete.

Task 07b3 prepares an explicit SDK-adapted incremental restart. Source and
receipt hashes are bound to a new proposal and rechecked immediately under the
shared lease before compilation. Independent review passed with seven native
preparation commands and 24 drift controls. Fresh capacity has no observed
blocker; the separately admitted restart must repeat live checks under its lease.
Task 07b4's incremental build exited 1 after 1365.16 seconds. The repaired RDF
files compiled, but libc++ `random_shuffle.cpp` failed because the SDK no longer
provides the `INFINITY` macro through this include chain. Exact failed logs and
the partial tree are retained in
[the failure checkpoint](../evidence/p2996-resume/failed-incremental-build/qualification.json).
Independent failure closure passed: the lease is free, builders are absent,
protected state and the default environment match, and all 19 original files
are preserved. The bounded partial inventory records both child configurations
and six Ninja state hashes. The initial one-line infinity candidate was
superseded by the scratch controls below. The compiler remains unqualified;
no installation has run.

Task 07b5's scratch controls now pass for a two-header SDK request repair.
The original failure and insufficient one-line workaround are retained as
negative controls. Public math macros pass C++17/23/26 checks, both include
orders pass, and the unchanged upstream clamping test builds and runs.
Native VFS overlays leave actual source, generated headers and protected state
unchanged. Independent review reproduced all sixteen outcomes and passed
preservation/static checks. Normal incremental rules reach both header copies;
guarded source application is next.

Task 07b6 prepares that application with exact scratch evidence, source and
retained build bindings. Independent review passed: seven native commands,
34 private guard controls, preservation and static checks all passed. Source
application was admitted separately as 07b7. All eighteen native commands passed
and the two source headers now have their reviewed postimages. Generated/build
and protected state are unchanged. Independent closure verified all operation
records, source postimages, free lease and default consumer; static/baseline
checks passed. Preparing the seven-file incremental restart is next.

Task 07b8 prepares that restart with both adaptation receipts, the cumulative
source diff and retained child build state. Native preparation and independent
review passed, including all 44 new guard controls and preserved inventories.
The fresh read-only capacity snapshot reports no observed blocker; actual build
admission must repeat checks under the lease.

Task 07b8 is committed at `db9c16cb860eedb6f1f472773f488b365413d839`.
Operation 07b9 has a separate scoped admission after fresh process, memory and
Docker checks. The bounded incremental build must produce its native final exit
and independently reviewed artifacts before installation or runtime acceptance.
The native build has now exited 0 and all 22 commands passed. The repaired
runtime sources compiled, both generated headers refreshed, required tool paths
exist and the lease is released. Independent artifact review passed without
findings, including the ARM64 tools, runtime inventory, protected/default state
and all original files. Installation and compiler/runtime qualification follow.

The successful build is committed at `628c0921cdbbc9bfdfebb6a5187ed611c9889cb8`.
Task 07c1 prepares the private installer against reviewed source/build hashes,
427 install scripts, three manifests and 17 aliases. Parent preparation passed
all seven native commands with preserved state. Independent review passed all
48 new guard cases and verified the repaired alias-chain comparison. Scoped
preservation and original-file checks passed; the prefix remains absent.
Preparation is committed at `2bdb63b359cc3a27f8515324b9bdb1a78494463e`.
Operation 07c2 has fresh scoped admission for the three private native installs;
its final native exits and independent installed-artifact review are pending.
All three installs have now exited 0 and the complete prefix inventory matches
the manifests and aliases. Source/build/protected/default checks passed and
the lease is released. Independent installed-artifact review is next.
Independent installation review passed without findings, including the complete
prefix, ARM64 metadata, archive tables, patched headers and CMake exports.
Protected state and original files passed. Compiler/runtime qualification is next.

Installation is committed at `3a55cd040e4cf31da8b1ae82c19b225ce4bb518a`;
the post-commit baseline passed. Task 07d now prepares a private reflection and
exception witness using this fork's feature guard, explicit headers and runtimes.
Parent probes passed, including reflection and exception handling, all three
private runtime images, and the intended negative control. [Independent runtime review](../evidence/p2996-reflection/reflection-review.json)
passed with preserved prefix, source/build, protected/default state and all
original files. Global mise registration is next.

Reflection qualification is committed at `5c0de926a7c07c0a5d732543a83068d84370627c`.
Task 07e1's native mise registration preparation passed both thirteen-command
trials and all sixteen focused guards. [Independent review](../evidence/p2996-registration/preparation-review.json)
passed with the namespace absent and protected/default state unchanged.
Global registration receives a separate operation after this checkpoint.
Preparation is committed at `38c61dfd9ae46d1f102b38c2dba37fd46714c000`.
Task 07e2's [scoped admission](../evidence/p2996-registration/admission.json)
records fresh ownership for the reviewed namespace promotion. Native execution
and independent post-registration preservation/discovery review are pending.
The operation now passed all thirteen native commands and promoted the exact
namespace. Global discovery, compiler identity and protected/default checks
passed; independent registration review remains.
[Independent registration review](../evidence/p2996-registration/registration-review.json)
passed with exact native discovery and only the two admitted install entries
added. All protected/default state and original files passed. Task 07 is now
qualified; LLVM tool fixtures and CMake/IWYU integration follow separately.
