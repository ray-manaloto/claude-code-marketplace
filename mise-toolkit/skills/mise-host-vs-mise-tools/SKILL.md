---
name: mise-host-vs-mise-tools
description: The CRITICAL distinction between system packages (apt/brew/dnf — libssl, libpq, build-essential) and dev tools (mise — node, python, cmake, ripgrep). The #1 mistake new mise users make is trying to install system libraries with mise. Use whenever a user asks "can I install X with mise" for something that looks like a system library, or hits "tool failed to compile".
---

# Host packages vs mise tools

## The rule (memorize this)

> **mise installs dev tools. apt/brew/dnf install system packages.**

| Use **mise** for | Use **apt/brew/dnf** for |
|---|---|
| Language runtimes (`node`, `python`, `go`, `ruby`, `rust`, `java`) | System libraries (`libssl`, `libpq-dev`, `libxml2`, `zlib`) |
| Build tools (`cmake`, `ninja`, `bazel`, `meson`) | Compilers (`gcc`, `g++`, `clang`) — usually system |
| Static analysis (`clang-tidy`, `eslint`, `ruff`, `shellcheck`) | Build essentials (`build-essential`, `make`) |
| Formatters (`prettier`, `black`, `clang-format`, `stylua`) | Kernel headers, drivers |
| CLI utilities (`ripgrep`, `fd`, `gh`, `jq`, `bat`) | System services (`postgres`, `redis`, `nginx`) for local dev |
| Cloud tools (`terraform`, `kubectl`, `aws-cli`, `gcloud`) | GUI applications (`vscode`, `docker-desktop`) |
| Package managers for languages (`pipx`, `uv`, `poetry`, `pnpm`, `yarn`, `conan`) | Filesystem tools (`fuse`, `cifs-utils`) |

## Why this matters

Many language runtimes need to **compile against** system libraries. Python is the canonical example — when mise compiles Python from source (or even uses some prebuilt binaries), it dynamically links against:

- `libssl` / `libcrypto` (for the `ssl` module)
- `libffi` (for `ctypes`)
- `libsqlite3` (for the `sqlite3` module)
- `liblzma` (for `lzma`)
- `libreadline` / `libedit` (for the REPL)
- `zlib` (for the `zlib` module)

If those system libraries aren't installed, **mise will install Python successfully and then `import ssl` will crash at runtime**. This is the most common newbie complaint.

The fix is **not** "install libssl with mise" (impossible — mise doesn't install system libs). The fix is **install libssl with apt/brew first**, then re-run `mise install python`.

## What you actually need on each platform

### Debian / Ubuntu

```sh
sudo apt update
sudo apt install -y \
    build-essential \
    curl git ca-certificates \
    libssl-dev libffi-dev libsqlite3-dev liblzma-dev libreadline-dev libbz2-dev \
    zlib1g-dev libncursesw5-dev libxml2-dev libxmlsec1-dev tk-dev xz-utils \
    pkg-config
```

This is enough to compile Python, Ruby, Erlang, Elixir, and most other languages mise installs from source.

### macOS

```sh
xcode-select --install                # provides clang, make, headers
brew install openssl@3 readline sqlite3 xz libffi
```

For most users, just `xcode-select --install` is enough — modern mise prefers prebuilt Python binaries that bundle their own deps.

### Fedora / RHEL

```sh
sudo dnf groupinstall "Development Tools"
sudo dnf install openssl-devel libffi-devel sqlite-devel xz-devel readline-devel bzip2-devel zlib-devel
```

### Alpine

⚠️ Alpine uses **musl libc**, not glibc. Many mise tools ship glibc-only binaries that won't run on Alpine. Stick with `debian:slim` or `ubuntu` base images for mise-based Docker workflows.

If you must use Alpine:

```sh
apk add --no-cache build-base curl bash git openssl-dev libffi-dev sqlite-dev xz-dev readline-dev bzip2-dev zlib-dev
```

And expect to compile from source for most tools.

## How mise handles this in practice

mise prefers **precompiled binaries with provenance** when available (e.g., `core:python` uses precompiled Python from python-build-standalone). These are statically linked or bundle their own deps, so the system libs above matter less.

When mise falls back to **compiling from source** (e.g., for older Python versions, Ruby, Erlang), the system libs become critical.

To force precompiled where possible:

```toml
[settings]
python.compile = false       # use precompiled python (default behavior in recent mise)
ruby.compile = false         # same for ruby
```

## Symptoms of "I needed to install system libs"

| Symptom | Likely missing |
|---|---|
| `ImportError: No module named '_ssl'` (Python) | `libssl-dev` |
| `ImportError: ... '_sqlite3'` | `libsqlite3-dev` |
| `ImportError: ... '_lzma'` | `liblzma-dev` / `xz-dev` |
| `make: gcc: command not found` | `build-essential` / Xcode CLT |
| `cannot find -lz` during compile | `zlib1g-dev` |
| `error: openssl/ssl.h: No such file` | `libssl-dev` |
| Ruby `Failed to build gem ...` | depends, often `libreadline-dev` or `libyaml-dev` |
| Erlang/Elixir compile errors | `libssl-dev`, `libncurses5-dev`, `libwxgtk*-dev` |
| `mise: tool failed to install` with vague "compile error" | almost always missing system libs |

## The right workflow

1. **Once per machine**: install the system prerequisites with apt/brew/dnf.
2. **Per project**: install dev tools via mise.
3. **In Dockerfiles**: `apt install libssl-dev ...` THEN `curl https://mise.run | sh` THEN `mise install`.

## C++ specific note

For C++ developers, `gcc`/`clang`/`make`/`cmake` are interesting cases:

- **`gcc` / `clang`**: usually system. `apt install gcc g++` or `brew install gcc llvm`. mise CAN install gcc/clang via aqua but it's unusual.
- **`cmake`**: ✅ mise. Pin per-project via `aqua:Kitware/CMake`. Better than the system cmake which is often outdated.
- **`ninja`**: ✅ mise.
- **`ccache`**: ✅ mise.
- **`clang-format` / `clang-tidy`**: ✅ mise (locked formatter version = no PR formatting drift). Or use the system clang's tools — both fine.
- **`conan` / `vcpkg`**: ✅ mise (conan via `pipx:conan`; vcpkg as a git submodule, mise can manage the bootstrap task).

See the v0.4 `mise-cookbook-cpp` skill for the full C++ recipe.

## Common questions

- **"Can mise install Docker for me?"** No. Docker is a system daemon — install via your OS package manager.
- **"Can mise install postgres?"** No, not the server. Yes for `psql` CLI (via aqua/github).
- **"Can mise install gcc?"** Technically yes via aqua, but usually no — use system gcc.
- **"What if my CI image doesn't have build-essential?"** Add `apt install -y build-essential libssl-dev ...` BEFORE `mise install` in your CI script or Dockerfile.

## See also

- `/mise-install` command — installs mise itself, mentions prerequisites
- `mise-deployment-models` — Docker base images that handle prerequisites
- `mise-troubleshooting` — diagnostic flow for tool install failures
- <https://mise.jdx.dev/getting-started.html>
