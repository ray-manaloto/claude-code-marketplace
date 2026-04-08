---
name: mise-cpp-package-managers
description: Conan 2.x vs vcpkg — how to pick between them, how to integrate each with mise via [tasks], and why conan should be installed via pipx (not mise's cargo/go backends). Use when the project needs third-party C++ libraries.
---

# Conan vs vcpkg — picking and wiring a C++ package manager

C++ has two mainstream package managers. Both work. Pick one per project and stick with it.

## The short answer

| Your situation | Use |
|---|---|
| Dev-facing project, frequent dep updates, want lockfiles + profiles | **Conan 2.x** |
| "I want a tarball of prebuilt libs to bundle with my app" | **vcpkg** |
| Writing a library others will consume via both | Support both (export cmake targets; let consumers pick) |
| Corporate/enterprise with a long-lived artifact server | **Conan** (remotes + artifactory integration) |
| Microsoft / Windows-first shop | **vcpkg** |
| Cross-compiling to esoteric targets | **Conan** (better profile model) |

If you're genuinely undecided, pick **Conan 2.x**. It's more flexible and has better CI ergonomics.

## Installing conan — use pipx, not mise

Conan is a Python package. It ships on PyPI. mise has a `pipx:` backend for Python CLIs:

```toml
[tools]
python = "3.12"
"pipx:conan" = "2.10"   # pin a specific 2.x
```

**Do NOT** try:
- `pip install conan` — dirties the global Python.
- `cargo:conan` — doesn't exist.
- `go:conan` — doesn't exist.
- `npm:conan` — doesn't exist (different conan).
- `brew install conan` — works, but then the team can't pin via `mise.toml`.

`pipx:conan` gets you isolation (conan in its own venv) + version pinning (via mise).

## Installing vcpkg — don't, bootstrap it

vcpkg is designed to be vendored. You add it as a git submodule or bootstrap it per-project:

```sh
git submodule add https://github.com/microsoft/vcpkg.git external/vcpkg
./external/vcpkg/bootstrap-vcpkg.sh   # Linux/Mac
```

Don't try to manage vcpkg via mise. It doesn't fit the model — vcpkg is both a tool and a package registry, and its expected location is project-local, not user-global.

In `mise.toml`, you can still automate the bootstrap:

```toml
[tasks."vcpkg:bootstrap"]
description = "Bootstrap vcpkg after git clone"
run = "./external/vcpkg/bootstrap-vcpkg.sh"
sources = ["external/vcpkg/bootstrap-vcpkg.sh"]
outputs = ["external/vcpkg/vcpkg"]
```

## Conan 2 + cmake integration

Add to `mise.toml`:

```toml
[tools]
python = "3.12"
"pipx:conan" = "2.10"
cmake = "3.30"
ninja = "latest"

[tasks."deps:install"]
description = "Install C++ deps via conan"
run = "conan install . --output-folder=build --build=missing --settings=build_type=Debug"
sources = ["conanfile.txt", "conanfile.py"]
outputs = ["build/conan_toolchain.cmake"]

[tasks.configure]
depends = ["deps:install"]
run = "cmake --preset conan-debug"   # conan generates this preset

[tasks.build]
depends = ["configure"]
run = "cmake --build build"
```

Conan 2 auto-generates a `CMakePresets.json` you can extend in your own presets file.

## vcpkg + cmake integration

Add a cmake preset that points at vcpkg's toolchain:

```json
{
  "version": 6,
  "configurePresets": [{
    "name": "default",
    "generator": "Ninja",
    "binaryDir": "build",
    "toolchainFile": "${sourceDir}/external/vcpkg/scripts/buildsystems/vcpkg.cmake",
    "cacheVariables": {
      "VCPKG_TARGET_TRIPLET": "x64-linux"
    }
  }]
}
```

And in `mise.toml`:

```toml
[tasks."vcpkg:bootstrap"]
run = "./external/vcpkg/bootstrap-vcpkg.sh"

[tasks.configure]
depends = ["vcpkg:bootstrap"]
run = "cmake --preset default"
```

vcpkg reads `vcpkg.json` for the manifest list (recommended) or CLI args (legacy).

## CI considerations

### Conan

- Cache `~/.conan2/p` (the package cache) between CI runs.
- Use `conan profile detect` in CI to avoid profile mismatches.
- For private dependencies, configure a remote with `CONAN_LOGIN_USERNAME` / `CONAN_PASSWORD` env vars (mark as `redact = true` in `[env]`).

### vcpkg

- Use **binary caching** (`VCPKG_BINARY_SOURCES`) pointed at a GitHub Actions cache or Azure blob. Without it, every CI run rebuilds every dep from source.
- The `vcpkg.json` manifest mode is far better for CI than the classic mode — always use manifest mode.

## When to use neither

Some projects skip both and use:
- **System libraries only** (`apt install libfoo-dev`). Simplest; least portable.
- **`find_package` + `FetchContent`** in cmake. Good for header-only libs; painful for anything with C dependencies.
- **Bazel** — if you're using Bazel, ignore this whole skill; Bazel has its own dep story.

For most teams, "pick conan or vcpkg" is the right call. The cost of a package manager is worth it.

## Anti-patterns

- **Installing conan via `pip install conan` globally.** Breaks when Python upgrades.
- **Committing `vcpkg_installed/` to git.** That's the output dir; it's per-machine and huge.
- **Mixing conan-installed deps and system deps of the same library.** cmake will find one of them non-deterministically.
- **Using vcpkg classic mode in new projects.** Manifest mode is the default now for good reason.
- **Checking in `~/.conan2/`** or absolute paths from conan install commands.

## See also

- `mise-cpp-toolchain-overview` — where the package manager fits.
- `mise-cpp-cmake-ninja-ccache` — the build-system half of the equation.
- Conan 2 docs: `docs.conan.io/2/`.
- vcpkg docs: `learn.microsoft.com/en-us/vcpkg/`.
