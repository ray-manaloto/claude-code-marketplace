---
name: mise-cookbook-cpp-cmake
description: End-to-end recipe for a modern C++ project managed by mise — cmake + ninja + ccache + mold linker + clang-tools + optional conan package manager. Full CMakePresets.json, mise.toml tasks, and first-run walkthrough. Use when starting a new C++ project or modernizing an existing one.
---

# Cookbook — Modern C++ with cmake + ninja + ccache

A complete starting point for a C++20/23 project using mise. The golden trio (cmake, ninja, ccache) plus a fast linker (mold on Linux), clang-tools for format/tidy/LSP, and CMakePresets for reproducible configures.

## Who this is for

- Starting a new C++ project and wanting modern defaults on day one.
- Adding mise to an existing project that currently pins nothing (relies on system cmake).
- Unifying a polyglot team's C++ toolchain across macOS and Linux.

## Who this isn't for

- Embedded / bare-metal projects with vendor-specific toolchains (STM32Cube, ESP-IDF) — those manage their own compilers.
- Header-only libraries with no build — overkill.
- Bazel / Buck shops — those tools own the toolchain.

## The `mise.toml`

```toml
min_version = '2026.4.0'

[tools]
cmake  = "3.30"
ninja  = "latest"
ccache = "latest"
mold   = "latest"                         # Linux only — delete on macOS
"aqua:llvm/llvm-project" = "18"           # clang-format, clang-tidy, clangd, lld

[env]
CMAKE_GENERATOR = "Ninja"
CMAKE_CXX_COMPILER_LAUNCHER = "ccache"
CMAKE_C_COMPILER_LAUNCHER = "ccache"
CMAKE_EXPORT_COMPILE_COMMANDS = "ON"

# ccache scoped to the project
CCACHE_DIR = "{{config_root}}/.cache/ccache"
CCACHE_MAXSIZE = "5G"
CCACHE_COMPRESS = "1"
CCACHE_COMPRESSLEVEL = "6"
CCACHE_SLOPPINESS = "pch_defines,time_macros"

# Fast linker (Linux). Comment out on macOS.
LDFLAGS = "-fuse-ld=mold"

[tasks.configure]
description = "Configure with CMake presets"
run = [
  "cmake --preset dev",
  "ln -sf build/compile_commands.json ."
]
sources = ["CMakeLists.txt", "CMakePresets.json", "cmake/**/*.cmake", "**/CMakeLists.txt"]
outputs = ["build/compile_commands.json", "build/build.ninja"]

[tasks.build]
description = "Build with ninja"
depends = ["configure"]
run = "cmake --build build"

[tasks.test]
description = "Run ctest"
depends = ["build"]
run = "ctest --test-dir build --output-on-failure"

[tasks.clean]
description = "Remove build dir"
run = "rm -rf build compile_commands.json"

[tasks.fmt]
description = "Format all source files with clang-format"
run = "clang-format -i $(find src include tests -name '*.cc' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' 2>/dev/null)"

[tasks."fmt:check"]
description = "Check formatting without modifying (for CI)"
run = "clang-format --dry-run --Werror $(find src include tests -name '*.cc' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' 2>/dev/null)"

[tasks.tidy]
description = "Run clang-tidy"
depends = ["configure"]
run = "clang-tidy -p build $(find src -name '*.cc' -o -name '*.cpp' 2>/dev/null)"

[tasks.check]
description = "Full check — fmt + tidy + build + test"
depends = ["fmt:check", "tidy", "build", "test"]
run = "echo 'all checks passed'"
```

## The `CMakePresets.json`

```json
{
  "version": 6,
  "cmakeMinimumRequired": { "major": 3, "minor": 28, "patch": 0 },
  "configurePresets": [
    {
      "name": "dev",
      "displayName": "Debug build (dev)",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON",
        "CMAKE_CXX_STANDARD": "20",
        "CMAKE_CXX_STANDARD_REQUIRED": "ON",
        "CMAKE_CXX_EXTENSIONS": "OFF"
      }
    },
    {
      "name": "release",
      "inherits": "dev",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "RelWithDebInfo" }
    },
    {
      "name": "asan",
      "inherits": "dev",
      "cacheVariables": {
        "CMAKE_CXX_FLAGS": "-fsanitize=address,undefined -fno-omit-frame-pointer",
        "CMAKE_EXE_LINKER_FLAGS": "-fsanitize=address,undefined"
      }
    }
  ],
  "buildPresets": [
    { "name": "dev", "configurePreset": "dev" },
    { "name": "release", "configurePreset": "release" }
  ]
}
```

## The minimal `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.28)
project(myapp
  VERSION 0.1.0
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(CTest)

add_library(myapp-core
  src/core.cc
  src/util.cc
)
target_include_directories(myapp-core PUBLIC include)
target_compile_features(myapp-core PUBLIC cxx_std_20)

add_executable(myapp src/main.cc)
target_link_libraries(myapp PRIVATE myapp-core)

if(BUILD_TESTING)
  add_subdirectory(tests)
endif()
```

## What this gives you

- **Pinned cmake 3.30** — not whatever the OS ships.
- **ccache** — typical 5-10x speedup on incremental builds.
- **mold linker** — typical 5-10x speedup on link steps (Linux).
- **`CMakePresets.json`** — declarative configure; `cmake --preset dev` replaces `cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Debug ...`.
- **clang-format + clang-tidy** — pinned major version, no format churn.
- **`compile_commands.json` symlink** — clangd / IDE pick it up from the project root.
- **`mise run check`** — full fmt + tidy + build + test in one command; same in CI.

## First-run walkthrough

```sh
# 1. Clone + trust
git clone <repo> myapp && cd myapp
mise trust

# 2. Install the whole toolchain
mise install

# 3. Configure (generates build/build.ninja and compile_commands.json)
mise run configure

# 4. Build
mise run build

# 5. Test
mise run test

# 6. One-stop check before committing
mise run check
```

## Suggested project layout

```
myapp/
├── mise.toml
├── CMakeLists.txt
├── CMakePresets.json
├── .clang-format
├── .clang-tidy
├── .gitignore           # includes build/, .cache/, compile_commands.json
├── README.md
├── include/
│   └── myapp/
│       ├── core.h
│       └── util.h
├── src/
│   ├── core.cc
│   ├── util.cc
│   └── main.cc
├── tests/
│   ├── CMakeLists.txt
│   └── test_core.cc
└── cmake/               # reusable cmake modules
```

## CI snippet (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
        with: { install: true, cache: true }
      - uses: actions/cache@v4
        with:
          path: .cache/ccache
          key: ccache-${{ runner.os }}-${{ hashFiles('**/CMakeLists.txt') }}
          restore-keys: ccache-${{ runner.os }}-
      - run: mise run "fmt:check"
      - run: mise run configure
      - run: mise run tidy
      - run: mise run build
      - run: mise run test
```

## Common gotchas

1. **mold on macOS** → Doesn't work. Comment out `mold` and `LDFLAGS=-fuse-ld=mold` on macOS branches (or use `uname` in a setup script).
2. **`CMAKE_EXPORT_COMPILE_COMMANDS` not producing the file** → The variable must be set *before* any `project()` call, or it won't take effect. Set it in `CMakePresets.json`, not mid-CMakeLists.
3. **ccache hit rate low** → Check `CCACHE_SLOPPINESS`. `time_macros` is almost always needed.
4. **clang-tidy can't find headers** → Missing `compile_commands.json` or configured against a stale build dir. Re-run `mise run configure`.
5. **Linker complains about mold when you typed gcc** → The compiler must support `-fuse-ld=mold`. gcc 12+ and clang 12+ do. Older toolchains won't.
6. **Multi-config generators (Visual Studio, Xcode)** → This cookbook uses Ninja (single-config). If you must use VS/Xcode, drop `CMAKE_BUILD_TYPE` and add per-config flags in `CMakePresets.json`.
7. **Forgetting to add new .cc files to `CMakeLists.txt`** → Ninja doesn't auto-glob. You can use `file(GLOB …)` but it's fragile; explicit lists are better.

## See also

- `mise-cpp-toolchain-overview` — the big picture of the C++ stack.
- `mise-cpp-cmake-ninja-ccache` — golden trio deep dive.
- `mise-cpp-linker-fast` — mold vs lld vs ld-prime.
- `mise-cpp-clang-tools` — clang-format/tidy/clangd details.
- `mise-cpp-package-managers` — adding conan or vcpkg on top.
- `/mise-cpp-init` — automated survey + proposal.
- `/mise-cpp-bootstrap` — one-shot default stack install.
- CMake presets spec: `cmake.org/cmake/help/latest/manual/cmake-presets.7.html`.
