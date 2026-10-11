# vcpkg compiler composition

Task 12a1 prepares [one shared chainloader](../cmake/toolchains/vcpkg-macos-arm64.cmake)
for the qualified P2996 and GCC16 macOS ARM64 lanes. vcpkg remains the primary
`CMAKE_TOOLCHAIN_FILE`; both applications and later overlay triplets select this
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
The eventual four target triplets are `arm64-osx-{p2996,gcc16}-{static,dynamic}`;
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
