---
name: mise-cpp-cmake-ninja-ccache
description: The golden trio for C++ builds — cmake + ninja + ccache. Covers ccache config (CCACHE_DIR, size, compression), ninja parallelism, CMake preset integration with mise, and the env var pattern that wires them together. Use when configuring a C++ build.
---

# cmake + ninja + ccache — the golden trio

These three tools together give you 5-10x faster C++ builds than the default "cmake + make + no cache". They're the first thing to add to any C++ mise.toml.

## The env-var wiring (this is the whole secret)

```toml
[env]
CMAKE_GENERATOR = "Ninja"                         # cmake defaults to Unix Makefiles
CMAKE_CXX_COMPILER_LAUNCHER = "ccache"            # wraps every compile with ccache
CMAKE_C_COMPILER_LAUNCHER = "ccache"              # same, for C
CCACHE_DIR = "{{config_root}}/.cache/ccache"      # project-local cache
CCACHE_MAXSIZE = "5G"                             # per-project size cap
CCACHE_COMPRESS = "1"                             # ~2x more cache hits per GB
CCACHE_COMPRESSLEVEL = "6"
CCACHE_SLOPPINESS = "pch_defines,time_macros"     # tolerate harmless variation
```

With those env vars set:
- `cmake -S . -B build` auto-picks ninja.
- Every `g++` / `clang++` invocation is auto-wrapped in ccache.
- The cache lives in the project, not your home directory, so it can be git-ignored and cleaned per-project.

## CCACHE_DIR — why project-local

The default is `~/.ccache` or `~/.cache/ccache`, shared across every project. This is fine for solo work but:
- You can't blow away one project's cache without nuking all of them.
- Multiple projects with different compiler versions thrash the cache.
- CI caching is harder (you can't just upload one dir).

Setting `CCACHE_DIR` to `{{config_root}}/.cache/ccache` puts the cache next to `mise.toml`. Add it to `.gitignore`:

```
.cache/
build/
```

## ninja parallelism

ninja defaults to `nproc + 2` parallel jobs. For most machines this is fine. Tune only if:
- You're OOMing on a laptop — pass `-j <smaller>`.
- You want deterministic build times in CI — pass `-j <fixed>`.

In `mise.toml`:

```toml
[tasks.build]
run = "ninja -C build"  # default parallelism
```

For CI with fixed parallelism:

```toml
[tasks."build:ci"]
run = "ninja -C build -j {{env.CI_BUILD_JOBS | default(value='4')}}"
```

## CMake presets integration

CMake presets (`CMakePresets.json`) are the modern way to store "how to configure this build". They compose cleanly with mise:

```json
{
  "version": 6,
  "configurePresets": [
    {
      "name": "dev",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "release",
      "inherits": "dev",
      "cacheVariables": { "CMAKE_BUILD_TYPE": "Release" }
    }
  ]
}
```

And in `mise.toml`:

```toml
[tasks.configure]
run = "cmake --preset dev"

[tasks."configure:release"]
run = "cmake --preset release"

[tasks.build]
depends = ["configure"]
run = "cmake --build build"
```

Note: when you use `cmake --build`, it picks up the generator from the preset — you don't need `CMAKE_GENERATOR` in env if every configure goes through a preset. But it doesn't hurt.

## `CMAKE_EXPORT_COMPILE_COMMANDS=ON`

Always set this. It produces `build/compile_commands.json`, which clangd reads to give you accurate IDE support. Without it, clangd falls back to heuristics and gets confused on complex projects.

Symlink it from the project root so tools find it:

```toml
[tasks.configure]
run = [
  "cmake --preset dev",
  "ln -sf build/compile_commands.json ."
]
```

## ccache stats

Periodically run `ccache -s` to see your hit rate. Aim for >80% on incremental builds. If it's lower:

- **Cache miss on "different time macros"** → `CCACHE_SLOPPINESS=time_macros`.
- **Cache miss on precompiled headers** → `CCACHE_SLOPPINESS=pch_defines,time_macros`.
- **Cache miss on path differences** → `CCACHE_BASEDIR={{config_root}}` (rebases absolute paths).

## CI caching

In GitHub Actions, cache the ccache dir between runs:

```yaml
- uses: actions/cache@v4
  with:
    path: .cache/ccache
    key: ccache-${{ runner.os }}-${{ hashFiles('**/CMakeLists.txt', 'mise.lock') }}
    restore-keys: ccache-${{ runner.os }}-
```

This gives CI the same 5-10x speedup you get locally.

## Anti-patterns

- **Using `make` instead of ninja** — slower, worse parallelism, no pretty progress.
- **Not setting `CMAKE_*_COMPILER_LAUNCHER=ccache`** — you install ccache but it never runs because nothing invokes it.
- **Global `CCACHE_DIR`** — cross-project pollution.
- **Turning off compression** to "save CPU" — compression usually makes the cache *bigger* in effective hit rate. Leave it on.
- **Setting `CCACHE_MAXSIZE` too low** — the cache silently evicts your build.

## See also

- `mise-cpp-toolchain-overview` — the big picture.
- `mise-cpp-linker-fast` — the next layer of speed after ccache.
- `mise-cpp-package-managers` — conan/vcpkg integration.
- ccache docs: `ccache.dev/manual/latest.html`.
- CMake presets: `cmake.org/cmake/help/latest/manual/cmake-presets.7.html`.
