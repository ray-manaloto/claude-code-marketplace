---
description: Survey a C++ project and propose a mise.toml with cmake, ninja, ccache, fast linker, and clang-tools
---

Delegate to the `mise-cpp-architect` agent. The agent will:

1. Survey for C++ artifacts: `CMakeLists.txt`, `CMakePresets.json`, `conanfile.py`/`conanfile.txt`, `vcpkg.json`, `Makefile`, `meson.build`, `compile_commands.json`, `.clang-format`, `.clang-tidy`.
2. Detect the current compiler (gcc/clang), C++ standard, and any existing package manager.
3. Propose a `mise.toml` with:
   - **Build tools**: `cmake`, `ninja`, `ccache` via aqua backends.
   - **Linker**: `mold` on Linux, `lld` on macOS/Linux (never both; pick one per platform).
   - **Clang tools**: `clang-format`, `clang-tidy`, `clangd` if the project already uses them.
   - **Package manager** (if detected): conan via `pipx:conan` (not mise's cargo/go backends), or leave vcpkg to be managed by its bootstrap script.
4. Add `[env]` entries for `CMAKE_GENERATOR=Ninja`, `CMAKE_CXX_COMPILER_LAUNCHER=ccache`, and a `MOLD_PATH`/`LDFLAGS` hint if mold is chosen.
5. Convert any Makefile targets to `[tasks]` (delegate to `mise-task-author`).
6. Show a unified diff of the proposed `mise.toml` and ask for confirmation before writing.

Do not write the file without user confirmation. Do not run `mise install` automatically. Reference the `mise-cpp-toolchain-overview`, `mise-cpp-cmake-ninja-ccache`, `mise-cpp-linker-fast`, and `mise-cpp-package-managers` skills for depth.
