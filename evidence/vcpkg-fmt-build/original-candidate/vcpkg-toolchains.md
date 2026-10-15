# vcpkg compiler composition

Task 12a1 prepares [one shared chainloader](../cmake/toolchains/vcpkg-macos-arm64.cmake)
for the qualified P2996 and GCC16 macOS ARM64 lanes. vcpkg remains the primary
`CMAKE_TOOLCHAIN_FILE`; both applications and overlay triplets select this
adapter through `VCPKG_CHAINLOAD_TOOLCHAIN_FILE`. The selected environment,
compiler prefix, SDK and target-triplet lane must agree.

The adapter retains the existing compiler files and the pinned native vcpkg
macOS toolchain. P2996 seeds its base flags once, then composes native PIC and
paired vcpkg flags before checking the complete initialized value. Repeated
inclusion must preserve exactly one composition. C++ runtime link flags and
executable compiler checks remain active. Explicit OLD link policy is rejected;
detector, port and application commands must select CMP0210 NEW.

Preparation permits bounded CMake script-mode controls only. Real compiler
detection, fmt Debug/Release builds, four-configuration consumers, ABI/cache
controls and private-root confinement remain pending their native operations.
The four target triplets are `arm64-osx-{p2996,gcc16}-{static,dynamic}`;
host helpers use the explicit native `arm64-osx` host triplet. Project linkage
remains independent of dependency linkage.

The [CMake prerequisite](../evidence/vcpkg-chainload/cmake-prerequisite.json)
identifies policy scopes, composition order and SDK inputs. The exact
[tool source review](../evidence/vcpkg-chainload/tool-boundary-review.json)
confirms that macOS children inherit the environment, while tracked variables
separately enter the package ABI. Triplets must track the selected lane/prefix
and explicitly hash all nested toolchain/compiler inputs. Invalid values still
need rejection; tracking alone does not validate them. Compiler-info caching
uses a narrower key, so later drift tests require fresh processes and isolated
detector caches. Package-hash changes alone cannot prove detector invalidation.

The Microsoft vcpkg-tool source is pinned to tag `2026-09-26`, commit
`51bf87ca6e9bf3e622d84ff323bd202ab1ca0c0b`, with MIT license retained beside
the selected source copies. The native fnox `codex_research` profile and Python
urllib/zipfile fetched and verified its official GitHub archive and metadata.
An initial lookup of the old `build.cpp` path failed; the retained corrected
receipt identifies `commands.build.cpp` and `buildenvironment.cpp`. No injected
secrets were recorded. Exa, Firecrawl, Last30Days and Context7 were not rerun;
inherited strict-five gaps remain unchanged. This was exact-source acquisition,
not a new comparative tool selection.

Preparation passed 71 script-mode cases. [Independent review](../evidence/vcpkg-chainload/preparation-review.json)
verified all 218 control artifacts and all intended diagnostics, then passed
six focused script runs: standalone P2996 before/after equivalence and both
lanes nested in the actual vcpkg policy scope. No findings remain. This closes
preparation only; actual language initialization and dependency builds follow.

Task 12a2 prepared the P2996 pair and shared macOS inputs. Its
[independent review](../evidence/vcpkg-p2996-triplets/final-review/review.json)
resolved two findings: the native extraction script leaves the public host
processor unset, and a defined-empty build type would suppress both dependency
configurations. The common file queries a private host value only when empty
and rejects every defined `VCPKG_BUILD_TYPE`. It tracks the selected environment
and binds nested compiler/toolchain, SDK and managed CMake/Ninja files.

Task 12b1 adds the GCC16 pair using that unchanged common file. GCC inputs
include both drivers, both language frontends, libstdc++ and libgcc; the SDK,
managed tools and included toolchains bring the additional-file count to 12.
The GCC preparation controls check native-style unseeded extraction, repeated
inclusion, compiler selection and conflicting environments. These are script
controls; they do not establish native compiler detection or built fmt linkage.

Task 12c1 prepares the [private execution probe](../dev/toolchains/vcpkg_private.py).
It copies the pinned vcpkg checkout, including its Git objects, and the two
verified fmt downloads into an operation-owned directory. Downloads, buildtrees,
packages, installed metadata, registry cache and temporary files use private
roots. Metrics and binary caching are disabled; the real HOME value is retained.
The Apple sandbox profile denies descendant file writes outside that directory
and network access, subject to declared inherited log/lease descriptors. Local
positive-write, outside-write, symlink-escape and loopback-denial controls must
pass before vcpkg runs. Existing compiler profiles, tool paths/versions, source
bytes, defaults and the shared lease are checked. Independent preparation review
passed, but the admitted run exited 1 at its first protection guard: an external
Renovate update changed the global config and lockfile. No copies or child
commands started. Native qualification awaits a separate shared-state
reattestation; dependency builds require a subsequent unit.
The copy is bound to a complete reviewed source inventory. Every tracked blob
and executable mode matches the pinned Git tree; the only extra source files
are the exact bootstrapped binary and empty metrics-disable marker.

Task 12c1a passed a separate read-only reattestation of the observed mise
update metadata. It binds exact additions and changed links, preserves the
prior baselines, and compares all four existing profiles and their isolation
values. The full compiler, SDK, package and shared-directory guards passed.
This reattestation writes no shared state and does not qualify vcpkg execution.
PATH comparison must prove exactly two bound Renovate version components changed;
all other profile values and the reconstructed historical PATH hash must match.
Both `bin` and `node_modules/.bin` are bound separately; prefixes are not rewritten.
All 15 commands exited 0 and the default environment was restored. The two
earlier failed comparisons remain preserved; independent artifact review passed.

Task 12c1b prepares the private vcpkg retry using the qualified 12c1a guard and
its exact default/P2996/GCC16 profile receipts. The copy, confinement and tool
selection procedure is unchanged. A new contract and operation directory retain
the earlier failed attempt; independent review and fresh capacity precede execution.
The admitted retry exited 0. All 24 command outcomes matched, including three
expected denials. Both profiles selected the exact managed CMake/Ninja tools;
source/default protections passed and the lease was released. Independent artifact
review passed all 52 copied files, 48 logs and 24 command outcomes with no findings.
This does not qualify compiler detection or built dependencies.

The pinned fmt port runs pkg-config validation for both dependency configurations.
Task 12c2a checks actual availability in the qualified compiler profiles before
preparing any required provisioning. Fixed-path absence alone is insufficient.
The port checks remain enabled, and dependency execution is still pending.
The guarded profile lookup found no executable or override in either lane.
The preparation candidate uses native mise Homebrew bootstrap with captured
pkgconf 3.0.8 metadata and its ARM64 bottle. Its dry run and missing-metadata
control passed: the plan names one bottle, and missing metadata returns 1.
The inventory contains 50 archive members and 30 absent prefix destinations,
with no existing directory materialization. Shared-state and prefix checks
passed. Independent review passed all source/archive bindings and six scratch
controls with no findings. Installation remains a separate phase.
Native fnox/Python acquired official Homebrew and pinned GitHub sources; native
mise ran only version/help/dry-run commands. Exa, Firecrawl, Last30Days and
Context7 were not rerun, and the inherited strict-five gaps remain incomplete.

Task 12c2b prepares the [guarded pkgconf installation](../dev/toolchains/pkgconf_install.py).
It repeats the captured plan and immediate ownership/preimage checks under the
shared lease, then verifies the installed keg, public links and native lookup.
The existing compiler, SDK, mise and default-environment guards remain active.
Independent preparation review and fresh capacity passed. The native operation
returned 0 with 28 successful commands, exact keg/link postimages, five valid
ARM64 signatures/runtime dependencies, native package lookup and preserved
defaults. Independent artifact review passed with no findings; no dependency
build ran.

Task 12c3a binds the qualified pkgconf entry through `PKG_CONFIG`, rejects a
conflicting `PKGCONFIG` variable/cache, and adds the executable and package
library bytes to the target ABI inputs. The shared triplet selects
`FMT_MODULE=OFF` for the compiled-library witness while retaining both dependency
configurations. All eight script controls and independent source/receipt review
passed with no findings. Actual host/target compiler selection and fmt linkage
remain unqualified.

Task 12c3b prepares four sequential, one-job private fmt installs, each with
fresh detector/build/package/installed roots and both dependency configurations.
The runner keeps host CC/CXX unset, constrains PATH, checks exact detector and
ABI inputs, and reuses the qualified source-copy and sandbox contracts. Fresh
capacity, a canonical lease and independent review precede native execution.
Compiled commands, package artifacts and later consumers remain separate gates.
