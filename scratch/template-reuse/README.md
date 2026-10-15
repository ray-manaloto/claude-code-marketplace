# Template reuse qualification — task 01

This source-only fixture adapts selected upstream preset patterns into four
small files. It has no `CMakeLists.txt`, targets, dependency bootstrap or compiler
selection. Do not use it as the application build. Task 02 qualifies native
schema/generation with managed CMake 4.4.4; task 03 adds a buildable skeleton
after task 10a or 10b qualifies an actual reflection compiler.

## Adopted source

| Upstream pin | Exact files inspected and reused | Adaptation |
| --- | --- | --- |
| [aminya/cpp_vcpkg_project](https://github.com/aminya/cpp_vcpkg_project/tree/810d0493559212c9e5eddb8acb9af1a9ff2a05ff) `810d0493559212c9e5eddb8acb9af1a9ff2a05ff` | `CMakePresets.json`; `cmake/presets/CMakeWorkflowPresets.json` | Relative includes, hidden settings, inherited Multi-Config developer preset and strict test output |
| [lukka/CppCMakeVcpkgTemplate](https://github.com/lukka/CppCMakeVcpkgTemplate/tree/21efc9ee50a1e7531257eeb2a8e1f0edc3df30c4) `21efc9ee50a1e7531257eeb2a8e1f0edc3df30c4` | `CMakePresets.json` | Explicit build configurations and inherited test configurations |

The root includes one local fragment. It has one visible configure preset,
four build presets, four test presets and one workflow confined to that tree.
All four standard configurations are explicit; `CMAKE_BUILD_TYPE` is absent.
C++26 is required with extensions disabled, but no compiler support is claimed.
The fixture sets no environment, compiler launcher, toolchain or shared path.
It preserves no upstream package-install, analyzer, docs or formatting targets.

[THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) contains the full upstream
Unlicense and Lukka MIT notices. The original source files, including the full
template include closure, are retained byte-for-byte with a `.source` suffix in
[the source manifest](../../evidence/reuse/source-manifest.json). Every blob's
SHA-256 and Git object ID matches its pinned repository tree.

## Pinned candidates, not integrated dependencies

| Candidate | Exact starting identity | Qualification boundary |
| --- | --- | --- |
| Template helper baseline | `aminya/project_options` v0.42.0 → `aece6dc112cba43dbde40a5bed9b640bf842de84` | Preserve as the comparison baseline before any upgrade |
| Helper upgrade candidate | `aminya/project_options` v0.44.0 / `412045e1f13cbdca15afbbbf6d27ed81f7372a50` | No helper code is included, fetched or called by this fixture |
| Matrix generator trial | `thirtytwobits/the-cmake-preset-matrix` / `f532db0b25843aaad0dd6c481923c6840425485b` | Task 02 must compare the published 0.3.3 package to these inspected features |

Both helper pins contain MIT and Unlicense texts; TCPM contains an MIT notice.
Those originals remain beside their source evidence. No helper or TCPM content
is incorporated into the scratch presets, and no license choice for future
helper integration is made here. TCPM remains a candidate until generation,
exclusions, native preset parsing and deterministic regeneration pass.

## Bootstrap and cache findings

The template's `CMakeLists.txt` downloads helper v0.42.0 with `FetchContent`,
then calls `run_vcpkg` before `project()`. Both inspected helpers default to
`~/vcpkg` and can clone, update, check out, bootstrap and force the toolchain
cache entry. v0.44.0 adds absolute-path normalization and a shared-directory
lock; this does not qualify it for the future managed-checkout contract.
The template's `CMakeLists.txt` is evidence only and is not adapted here.

Both `Cache.cmake` files are identical and search `ccache` before `sccache`
regardless of `CACHE_OPTION`. Later integration must set explicit compiler
launcher paths and inspect actual commands. Runtime comparison, matching
compiler/stdlibs, vcpkg ABI/linkage, analyzers and packaging remain downstream.

## Evidence and limits

[Acquisition checks](../../evidence/reuse/acquisition-check.json) record all
routes and command exits; [independent review](../../evidence/reuse/source-review.json)
verifies the tag chain, tree membership, sizes and hashes. This is qualification
of the already accepted shortlist, not a fresh comparative research sweep.
Inherited Context7, Firecrawl and Last30Days gaps remain unresolved.
