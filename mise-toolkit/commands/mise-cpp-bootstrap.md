---
description: One-shot bootstrap of a modern C++ toolchain via mise (cmake + ninja + ccache + clang-tools)
---

For a user who hasn't picked a toolchain yet. Install a sensible default C++ stack via mise without surveying the project first.

## Default stack

```toml
min_version = '2026.4.0'

[tools]
cmake       = "latest"   # aqua:Kitware/CMake
ninja       = "latest"   # aqua:ninja-build/ninja
ccache      = "latest"   # aqua:ccache/ccache
"aqua:llvm/llvm-project" = "latest"  # clangd/clang-format/clang-tidy bundle (optional)

[env]
CMAKE_GENERATOR = "Ninja"
CMAKE_CXX_COMPILER_LAUNCHER = "ccache"
CMAKE_C_COMPILER_LAUNCHER = "ccache"
# Tell ccache where to cache (under the project's .cache/ccache)
CCACHE_DIR = "{{config_root}}/.cache/ccache"
CCACHE_MAXSIZE = "5G"

[tasks.configure]
description = "Configure with CMake + Ninja"
run = "cmake -S . -B build -GNinja"

[tasks.build]
description = "Build with ninja"
depends = ["configure"]
run = "ninja -C build"

[tasks.test]
description = "Run ctest"
depends = ["build"]
run = "ctest --test-dir build --output-on-failure"

[tasks.clean]
description = "Remove build dir"
run = "rm -rf build"
```

## Steps

1. Check for an existing `mise.toml` — if present, show a diff rather than overwriting.
2. Check the host platform. On Linux, add `mold` to `[tools]` and set `LDFLAGS=-fuse-ld=mold`. On macOS, add `lld` instead.
3. Show the proposed `mise.toml` as a diff.
4. After user confirmation, write it and suggest `mise trust && mise install`.
5. Add `.cache/ccache/` and `build/` to `.gitignore` if they're not already there.
6. Point the user at `/mise-cpp-init` if they want a project-aware setup instead of the default stack.

Do not run `mise install` automatically. Do not overwrite an existing `mise.toml` without a diff and confirmation.
