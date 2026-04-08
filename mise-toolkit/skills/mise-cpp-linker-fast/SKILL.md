---
name: mise-cpp-linker-fast
description: mold vs lld vs system ld — when to pick each, how to wire them via mise, and the link-time speedup for large C++ projects. Covers Linux-only mold, cross-platform lld, and Apple's ld-prime. Use when link times dominate your build loop.
---

# Fast linkers for C++ — mold, lld, ld-prime

Linking a large C++ binary with GNU ld can take 30+ seconds. Switching to mold or lld drops that to 2-5 seconds with zero code changes. It's the cheapest performance win available.

## The three fast linkers

| Linker | Platforms | Relative speed | Notes |
|---|---|---|---|
| **mold** | Linux (x86_64, aarch64) | 🏆 Fastest | Written by rui314 (also wrote lld). Linux-only. MIT license. |
| **lld** | Linux, macOS, Windows (with caveats) | 🥈 Very fast | Part of LLVM. Portable. Battle-tested. |
| **ld-prime** | macOS 14+ | 🥈 Very fast | Apple's new linker (default in recent Xcode). No setup needed. |
| **gold** | Linux (legacy) | 🥉 Faster than ld | Deprecated; use mold instead. |
| **GNU ld** | Everywhere | (baseline) | Fine for small projects; slow for anything >100k LOC. |

## When link time matters

Linking dominates your build loop if:
- You edit a `.cc` file and wait >5 seconds before the binary is ready.
- `ninja` shows "1/1 linking ..." stuck for a noticeable time.
- You're building a large binary (>50MB debug build).
- You're using whole-program optimization or LTO.

If your build loop is <2 seconds, don't bother. Focus on ccache first.

## Wiring mold via mise (Linux)

```toml
[tools]
mold = "latest"   # aqua:rui314/mold

[env]
LDFLAGS = "-fuse-ld=mold"
# Optional: also set for cmake directly
CMAKE_LINKER_TYPE = "MOLD"
```

For cmake projects specifically, use the linker flag approach:

```toml
[env]
CMAKE_EXE_LINKER_FLAGS = "-fuse-ld=mold"
CMAKE_SHARED_LINKER_FLAGS = "-fuse-ld=mold"
CMAKE_MODULE_LINKER_FLAGS = "-fuse-ld=mold"
```

Or, if you're on a recent cmake (3.29+), use the `CMAKE_LINKER_TYPE` variable:

```toml
[env]
CMAKE_LINKER_TYPE = "MOLD"
```

Verify mold is actually being used:

```sh
mise exec -- ld.mold --version    # should print mold version
mise exec -- cmake --build build -v 2>&1 | grep mold   # should see -fuse-ld=mold in link commands
```

## Wiring lld via mise (macOS and Linux)

```toml
[tools]
"aqua:llvm/llvm-project" = "18"   # bundles lld

[env]
LDFLAGS = "-fuse-ld=lld"
```

On macOS, **check whether you're on macOS 14+ first**. If so, Apple's ld-prime is already the system linker and is as fast as lld — you don't need to install anything. Just use the default.

```sh
ld -v 2>&1 | head -1   # on macOS 14+: "@(#)PROGRAM:ld PROJECT:dyld-..." (ld-prime)
```

## mold vs lld — which to pick on Linux?

- **mold** is marginally faster (~1.5-2x) than lld in most benchmarks.
- **mold** is Linux-only. lld is portable.
- **lld** is better-tested with LTO and ThinLTO across exotic configs.
- **mold** handles debug info link 2-3x faster than lld, which is the killer feature for debug builds.

**Rule of thumb**: if your project is Linux-only, use mold. If you build on both Linux and macOS, use lld on Linux and let macOS use its default.

## macOS specifics

- **macOS 14+ (Sonoma and later)**: default `ld` is ld-prime, which is already fast. Don't install a second linker.
- **macOS 13 or earlier**: install lld via `aqua:llvm/llvm-project` and use `-fuse-ld=lld`.
- **Xcode vs command-line clang**: if your project links via Xcode, the IDE uses its own linker and `LDFLAGS` is ignored. Pass `OTHER_LDFLAGS = -fuse-ld=lld` via xcconfig or scheme env instead.
- **Universal binaries (arm64 + x86_64)**: stick with Apple's ld. Neither mold nor lld handle fat binaries as cleanly.

## Verifying the speedup

Before/after:

```sh
# before: measure a clean link
time ninja -C build clean
time ninja -C build

# add LDFLAGS to mise.toml, mise install, reconfigure
rm -rf build
mise run configure
time ninja -C build clean
time ninja -C build
```

For a 1M-LOC C++ project, link time typically drops from 30s to 3s.

## Anti-patterns

- **Installing mold on macOS.** mold is Linux-only. It'll compile but won't link a macOS binary.
- **Setting `LDFLAGS=-fuse-ld=mold` without installing mold.** The build fails with "unknown linker". Always pin the tool first.
- **Mixing linkers across CMake subprojects.** Pick one per project. Don't let a vendored dependency sneak in a different linker.
- **Debugging a link crash without reverting the linker first.** When mysterious link failures happen, flip back to default ld to see if the linker is the problem. It rarely is, but it's a 30-second check.

## See also

- `mise-cpp-toolchain-overview` — where the linker fits.
- `mise-cpp-cmake-ninja-ccache` — the other layers of the golden trio.
- mold: `github.com/rui314/mold`.
- lld: `lld.llvm.org`.
