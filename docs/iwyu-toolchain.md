# Matching-fork IWYU foundation

Task 09a prepares the accepted [IWYU commit](https://github.com/include-what-you-use/include-what-you-use/tree/791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3),
`791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3`, tree
`b793b517dd7a261da9e574572264b6d59ed4b7c4`. The
[source acquisition](../evidence/iwyu-source/operation/acquisition.json) passed
all ten Git commands, verified 854 working-tree files against their Git blobs,
and matched both earlier pinned CMake/license fragments. No source was patched.
Native configure/build/install and independent artifact verification passed.
The later runtime replacement was reattested separately below. Bounded
reflection advice, fixing and rebuilding passed native checks and independent
artifact review; resource relocation remains pending.

The retained [upstream license](../evidence/iwyu-source/upstream/LICENSE.TXT.source)
is University of Illinois/NCSA. Both `iwyu_getopt` files carry that license
header; the implementation records Kim Gräsman's permission and is guarded by
`_MSC_VER`. Preserve these notices with source and any binary distribution.
The matching LLVM fork's license and adaptations remain in its own receipts.

## Source and build contract

Run `dev/toolchains/iwyu_source.py --directory <new-absolute-private-directory>`
with an existing Python through native `fnox --config ~/.config/fnox/config.toml
--profile codex_research --no-defaults --no-daemon --non-interactive exec --`.
The helper ignores global/system Git configuration, uses an empty Git template,
and records command exits and source hashes without injected credentials.
Native fnox, Python's HTTP client and `/usr/bin/git` ran for this acquisition.
No Exa, Firecrawl, Last30Days, Context7 or new comparative sweep ran; inherited
strict-five gaps remain unchanged.

The [initial cache](../dev/toolchains/iwyu-bootstrap.cmake) follows the
[installed package contract](../evidence/iwyu-source/native-prerequisite.json).
Use the isolated `cpp-build` environment and supply attested absolute
`MARKETPLACE_IWYU_CC`, `CXX`, `SDK`, `NINJA`, `LLVM_PREFIX` and `PREFIX` variables
(each has that full prefix). The build uses the same Apple CLT compiler/default
standard library as the qualified LLVM libraries. IWYU itself is C++17; its
ability to analyze C++26 reflection is a later functional test.

Explicit LLVM/Clang package directories select the exact fork headers and
dylibs. AddLLVM supplies native Darwin rpaths, including the fixed LLVM prefix
when IWYU installs separately. Do not override `CMAKE_INSTALL_RPATH` or use the
product's private-libc++ toolchain. Optional Python test enumeration is disabled
at initial configure; `fix_includes.py` remains available for an explicit fixture.

Relocation will move only the private IWYU install tree while the qualified LLVM
installation stays fixed. Verify actual resources, dylib origins, diagnostics,
recommendation exits and the rebuilt reflection fixture from that moved tree.
Moving LLVM itself, global registration and full upstream test-suite acceptance
are separate, unqualified operations. [Independent preparation
review](../evidence/iwyu-source/preparation-review.json) passed without findings.

## Private native operation

Task 09b's `dev/toolchains/iwyu_build.py` first records a preparation proposal.
Its `--execute` mode requires the independently reviewed proposal, exact helper
hash and fresh admission for a new private run directory. It repeats the shared
lease, process/container census, CPU/disk checks and protected-state checks.
Configure, build and install have 180/1800/120-second limits and retained logs;
the build uses one job and keeps an 8 GiB disk reserve. Generated and executed
commands must match, and the installed ARM64 binary must load the exact fork
LLVM/Clang libraries with the Apple bootstrap standard library. License notices
are retained in the private install tree. The [native operation](../evidence/iwyu-build/operation/qualification.json)
passed all forty commands. Eleven retained warnings instantiate one upstream
`EnumeratorSpec` switch omission; bounded reflection analysis remains required.

The [artifact review](../evidence/iwyu-build/installation-review.json) verifies
all forty exits, sixteen executed commands and installed dependencies. Its
10,588 current-state checks found only the shared mise executable replaced after
the operation, from 2026.10.7 to 2026.10.8. Attribution is unestablished. Preserve
both runtime identities and the successful historical operation. Task 09b1
reattested the new runtime and existing profiles before semantic qualification.

Task 09b1's [runtime helper](../dev/toolchains/mise_runtime.py) binds the observed
replacement and historical inputs in a separate contract. Its in-memory overlay
changes only the unique mise record's SHA-256 and size; all other protection
checks remain active. Read-only version, ARM64, profile and isolation probes
must preserve complete default/build/P2996/GCC16 outputs and shared state.
The replacement's installer attribution and release-download provenance remain
unknown; this unit qualifies the observed executable for these local commands.
All twelve [native probes](../evidence/mise-runtime/operation/qualification.json)
passed. [Independent review](../evidence/mise-runtime/runtime-review.json)
passed 21 focused controls, exact receipt comparisons and the current protection
check. New operations use this current binding; historical helpers retain their
original fingerprints. The earlier live-drift finding remains in its original receipt.

Task 09c1 prepares one private reflected-type program with a transitive include.
The [bounded helper](../dev/toolchains/iwyu_reflection.py) requires the exact
direct-header recommendation, feeds only saved analysis stderr to the upstream
fixer with one absolute file allowlisted, and verifies the complete resulting
bytes. It then rebuilds/runs and requires clean analysis; omission of the
reflection flag must fail. The source recipe binds the fixed compiler, SDK,
libc++ and analyzer. Separate admission, a fresh capacity check and the canonical
host lease precede native work. The [native operation](../evidence/iwyu-reflection/operation/qualification.json)
matched all 32 expected exits: exact advice returned 23, the fixer/build/run and
clean analysis returned 0, and the missing-flag control returned 1. The fix only
replaces the indirect include with `value.h`; `<meta>` and program bytes remain.
Source, installation, defaults and lease checks passed. [Independent artifact
review](../evidence/iwyu-reflection/artifact-review.json) verified all 71 receipt
copies, 32 native exits, exact fixer input/edit, both ARM64 binaries and current
protected state without findings. Copied-resource relocation follows separately,
and full reflection visitor coverage is unqualified.

Task 09c2's [relocation helper](../dev/toolchains/iwyu_relocation.py) copies the
qualified IWYU install and Clang builtin resources, verifies their inventories,
then renames only that copy. Explicit resource selection must read the moved
headers in an actual trace; an empty resource directory must fail. The corrected
reflection fixture must remain clean, and moved IWYU must load the fixed LLVM
libraries. Original installations, sources and defaults remain guarded. Native
execution requires independent preparation review and fresh capacity admission;
automatic resource discovery and LLVM relocation are outside this contract.
Preparation review and the [native operation](../evidence/iwyu-relocation/operation/qualification.json)
passed all 24 focused controls and 31 expected native results, respectively.
Copied headers were traced, the empty-resource control failed as intended, and
moved reflection analysis remained clean. [Final artifact review](../evidence/iwyu-relocation/artifact-review.json)
passed all 70 receipt copies, 62 command logs, nine moved-header hashes and the
current preservation/inventory checks without findings. Task 09 is qualified for
this bounded reflection fixture and explicit copied-resource contract.
