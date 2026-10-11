# Native P2996 CMake fixture

Task 10a uses the compiler, SDK and private libc++ runtimes qualified by
[task 07d](../../docs/p2996-toolchain.md). Select the global mise `p2996`
environment before configuring this fixture with Ninja Multi-Config and
`cmake/toolchains/p2996-macos-arm64.cmake` as `CMAKE_TOOLCHAIN_FILE`.
The fixture supports Debug, Release, RelWithDebInfo and MinSizeRel.

The toolchain requires native ARM64, CMake 4.4+ and the exact qualified prefix.
It rejects inherited compiler flags, launchers, conflicting platform choices
and bypassed compiler checks. `-freflection` is private to the reflection target.
CMake retains its native Darwin compile/link rules. `CMAKE_CXX_LINK_FLAGS` with
CMP0210 NEW supplies the three private runtime libraries even when CMake clears
standard libraries for an ABI probe; C compilation receives no C++ options.
The source contract records the installed CMake 4.4.4 documentation and source.

[Preparation evidence](../../evidence/p2996-cmake-preparation/source-contract.json)
binds the files and qualified reflection witness. The bounded
[native qualification](../../evidence/p2996-cmake/operation/qualification.json)
passed three compiler probes, all four build/test/runtime cells and eight
isolation controls. Fresh probe artifacts remain private; their hashes and
immediately captured configure evidence are retained. Independent reproduction
and [closure review](../../evidence/p2996-cmake/cmake-review.json) passed.
Shared/module runtime qualification follows with the library; this fixture
does not qualify dependencies, cache launchers or the application matrix.
