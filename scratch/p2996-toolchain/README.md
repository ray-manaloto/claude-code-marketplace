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
binds the proposed files and the qualified reflection witness. Native configure,
ABI and custom try-compile links, all four build/test cells, runtime loading and
negative controls remain unverified until the separate bounded qualification.
No dependency build, global edit, cache launcher or application matrix belongs
in this fixture. Shared/module runtime qualification follows with the library.
