---
name: mise-cpp-toolchain-overview
description: The modern C++ toolchain at a glance — cmake, ninja, ccache, fast linkers (mold/lld), clang-tools, and package managers (conan/vcpkg) — with a decision framework for when to pin each via mise vs system apt/brew. Use when setting up C++ in a project for the first time.
---

# The modern C++ toolchain (managed by mise)

C++ has no official package manager, no official build system, and no official version-pinning story. That's exactly the gap mise fills: pin your build tooling per-project so every dev and every CI run builds the same way.

## The six layers

| Layer | Tool(s) | Pin via mise? | Why |
|---|---|---|---|
| **Compiler** | gcc, clang, MSVC | ❌ Usually system | ABI tied to libc/libstdc++; system compiler is safest. Exception: pin clang via `aqua:llvm/llvm-project` if you need a specific version. |
| **Build system generator** | cmake, meson | ✅ Yes | Version matters for preset syntax, policies, `find_package` behavior. |
| **Build driver** | ninja, make | ✅ ninja yes | ninja is ~2x faster than make for incremental builds; pin via aqua. |
| **Compiler cache** | ccache, sccache | ✅ Yes | Huge speedup on rebuilds. Pin so CI and dev match. |
| **Linker** | mold (Linux), lld (Linux/Mac) | ✅ Yes | 10x faster than GNU ld for large projects. |
| **Package manager** | conan, vcpkg | ⚠️ pipx conan | vcpkg is bootstrapped per-project; conan via pipx (not `pip install`). |
| **Code quality** | clang-format, clang-tidy, clangd, iwyu | ✅ Yes | Version matters for format stability and tidy check availability. |

## Why "yes" for most of the stack

The system-provided versions of cmake and ninja are almost always too old. Ubuntu 22.04 ships cmake 3.22; projects routinely need 3.28+ for C++23 module support. Pinning via mise means:

- Every dev on the team has the same version.
- CI matches dev exactly.
- Upgrading is a git commit, not a "please everyone apt upgrade" email.

## Why "no" for the compiler

Compilers are deeply coupled to:
1. The C standard library (`libc` — glibc on Linux, musl on alpine, libSystem on macOS).
2. The C++ standard library (`libstdc++` on GCC, `libc++` on clang).
3. Debug info formats, unwinders, and sanitizer runtimes.

A mise-installed clang won't necessarily work with your system's libstdc++ (version skew) or your system's debuggers. For most projects, use the system compiler (or a docker image's compiler) and pin *everything else* via mise.

**Exception**: if you need a very specific compiler version (building an old kernel, reproducing a CI issue), install it via the OS package manager in a container. Don't try to mise-install GCC.

## The golden `[tools]` block

```toml
[tools]
cmake  = "3.30"
ninja  = "1.12"
ccache = "4.10"
"aqua:llvm/llvm-project" = "18"   # clangd, clang-format, clang-tidy (optional)
```

On Linux, add `mold`. On macOS, add `lld` (or use Apple's ld-prime; see `mise-cpp-linker-fast`).

## Common anti-patterns

- **Installing cmake via `pip`.** Don't. The pip package is a convenience wrapper that lags the upstream release and isn't trusted for production.
- **Pinning a system compiler version via apt in the Dockerfile but leaving cmake/ninja unpinned.** Half-measures. Pin the whole toolchain.
- **Using system ccache without `CCACHE_DIR` set.** Cross-project cache pollution. Always scope ccache to the project.
- **Mixing conan and vcpkg in the same project.** Pick one. Conan is better for dev-facing dependency management; vcpkg is better for "I want a tarball of pre-built libs".
- **Not using ninja.** ninja is strictly better than make for parallel C++ builds. Set `CMAKE_GENERATOR=Ninja` in `[env]`.

## See also

- `mise-cpp-cmake-ninja-ccache` — deep dive on the golden trio.
- `mise-cpp-linker-fast` — mold vs lld, when each matters.
- `mise-cpp-package-managers` — conan 2.x vs vcpkg.
- `mise-cpp-clang-tools` — clang-format/tidy/clangd/iwyu setup.
- `mise-host-vs-mise-tools` — the general "what belongs in apt vs mise" rule.
- `/mise-cpp-init` — survey + propose.
- `/mise-cpp-bootstrap` — one-shot default stack.
