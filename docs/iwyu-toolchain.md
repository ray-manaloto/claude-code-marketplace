# Matching-fork IWYU foundation

Task 09a prepares the accepted [IWYU commit](https://github.com/include-what-you-use/include-what-you-use/tree/791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3),
`791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3`, tree
`b793b517dd7a261da9e574572264b6d59ed4b7c4`. The
[source acquisition](../evidence/iwyu-source/operation/acquisition.json) passed
all ten Git commands, verified 854 working-tree files against their Git blobs,
and matched both earlier pinned CMake/license fragments. No source was patched.
Native configure, build, installation and analysis remain unverified.

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
