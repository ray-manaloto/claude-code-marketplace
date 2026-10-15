# GCC16 CMake fixture

Task 10b uses the compiler/runtime qualified by
[task 05](../../evidence/gcc-runtime/qualification.json). It reuses the same
reflection witness through CMake 4.4.4 and Ninja Multi-Config. This is a tiny
compiler fixture; it has no vcpkg dependency, compiler cache or installation step.

Select the global mise `gcc16` profile from an empty directory, with
`MARKETPLACE_GCC16_PREFIX=/opt/homebrew/Cellar/gcc/16.2.0` in that process.
Do not activate the repository's root Linux OCI mise configuration. Pass the
absolute project paths and use a new private build directory:

```sh
cpp_context=$(mktemp -d)
gcc16() {
  MARKETPLACE_GCC16_PREFIX=/opt/homebrew/Cellar/gcc/16.2.0 \
    /absolute/native/mise --no-hooks -C "$cpp_context" -E gcc16 \
    exec --fresh-env --no-deps -- "$@"
}
gcc16 cmake -S <checkout>/scratch/gcc-toolchain -B <private-build> \
  -G 'Ninja Multi-Config' \
  -DCMAKE_TOOLCHAIN_FILE=<checkout>/cmake/toolchains/gcc16-macos-arm64.cmake \
  -DCMAKE_OSX_SYSROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX27.0.sdk \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=27.0
gcc16 cmake --build <private-build> --config Debug --parallel 1 --verbose
gcc16 ctest --test-dir <private-build> -C Debug --output-on-failure --no-tests=error
```

Repeat build/test for Release, RelWithDebInfo and MinSizeRel. The compiler
toolchain checks native host architecture, profile selection, inherited flags,
existing compiler choices and explicit SDK/deployment selection. Reflection is
a private target flag so future ordinary dependencies need not enable it.
The later vcpkg integration will keep vcpkg as `CMAKE_TOOLCHAIN_FILE` and use this
file through `VCPKG_CHAINLOAD_TOOLCHAIN_FILE`; that integration is unqualified here.

Acceptance requires actual configure/build/test exit codes, compilation commands,
ARM64 outputs and their libstdc++ runtime identity in all four configurations.
Wrong-profile, dirty-environment and architecture controls must fail. Preparation
alone is not a pass. The [parent receipt](../../evidence/gcc-cmake/qualification.json)
records four passing cells, four rejected isolation controls, unchanged default
environment and exact runtime identities. [Independent review](../../evidence/gcc-cmake/cmake-review.json) reproduced all
28 outcomes once and passed with no findings; protected state and all 19 original
Claude acceptance hashes remained unchanged.
