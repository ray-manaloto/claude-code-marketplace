**06b can be limited to one outer configure and inspection of its generated files.** Do not invoke `builtins-configure` or `runtimes-configure`: those targets depend on the newly built compiler and `llvm-config`. [Dependency wiring](/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-source-f17c8d6c/source/llvm/cmake/modules/LLVMExternalProjectUtils.cmake:381).

I verified source HEAD `f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e` and tree `9899759f9004a7df8442ec57000a17e53e6ad5f6`. The bootstrap cache and three relevant LLVM modules still match the qualified review hashes.

Through the existing `cpp-build` profile from an empty cwd, supply the six attested `MARKETPLACE_BOOTSTRAP_*` values and run this command with a new, private build directory:

```sh
/Users/rmanaloto/.local/share/mise/installs/cmake/4.4.4/cmake-4.4.4-macos-universal/CMake.app/Contents/bin/cmake \
  -S /Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-source-f17c8d6c/source/llvm \
  -B "$MARKETPLACE_P2996_BUILD_DIR" \
  -G Ninja \
  -C /Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace/dev/toolchains/p2996-bootstrap.cmake \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

This executes compiler feature checks. It does not request an LLVM build target. Existing prerequisites are Apple Clang/Clang++, SDK 27, managed CMake/Ninja, Python, and the CLT linker/archive utilities. No preinstalled fork compiler is required.

With `<build>` denoting that directory, retain:

| Generated artifact | Required evidence |
|---|---|
| `CMakeCache.txt`, `CMakeFiles/4.4.4/CMake{C,CXX}Compiler.cmake`, `CMakeSystem.cmake` | Attested Apple bootstrap compilers; Ninja; SDK; arm64; deployment 27.0; exact private prefix; native, non-cross configuration |
| `projects/builtins/tmp/builtins-cfgcmd.txt` | Pinned source’s `compiler-rt/lib/builtins`; future `<build>/bin/clang`; forwarded SDK/runtime arguments |
| `projects/runtimes/tmp/runtimes-cfgcmd.txt` | Pinned source’s `runtimes`; future `<build>/bin/clang` and `clang++`; all four requested runtimes |
| Corresponding `*-cache-Release.cmake` files | Forwarded Python executable and other cache defaults |
| `build.ninja`, `CMakeFiles/rules.ninja` | Expanded commands and compiler prerequisites, resolving any placeholders in `*-cfgcmd.txt` |
| `CMakeFiles/CMakeConfigureLog.yaml` | Actual bootstrap feature-check commands and results |

Both child commands must contain the exact private install prefix, pinned `CMAKE_OSX_SYSROOT`, arm64 architecture, deployment 27.0, install RPATH and `DARWIN_macosx_CACHED_SYSROOT`. The runtimes command must retain `COMPILER_RT_BUILD_BUILTINS=Off`; builtins have their separate prerequisite stage. [Runtime arguments](/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-source-f17c8d6c/source/llvm/runtimes/CMakeLists.txt:261), [new compiler selection](/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-source-f17c8d6c/source/llvm/cmake/modules/LLVMExternalProjectUtils.cmake:225).

Do not require populated `runtimes/{builtins,runtimes}-bins/CMakeCache.txt` in 06b. Those belong to the later child configurations.

For resumption, preserve the exact source, build directory, cache inputs and install prefix. External projects use `BUILD_ALWAYS=1`, which re-invokes their incremental builds; `*-clear` explicitly deletes their build/stamp directories. Installation is separate: external projects have an empty automatic install command, while the outer install script invokes their generated install scripts. Retain separate runtime installation evidence—the wrapper uses `execute_process` without explicit error-result checking. [Resume/install behavior](/Users/rmanaloto/.local/state/marketplace-tool-foundation/p2996-source-f17c8d6c/source/llvm/cmake/modules/LLVMExternalProjectUtils.cmake:411).

**UNVERIFIED:** strict `try_compile -j1`, actual generated commands, child configuration, runtime compilation, effective compiler-rt SDK use, and installation. `CMAKE_BUILD_PARALLEL_LEVEL=1` is documented for `cmake --build`; it does not establish the probe limit from the inspected material. No configure, compiler, build, install, acquisition or service command ran in this inspection.