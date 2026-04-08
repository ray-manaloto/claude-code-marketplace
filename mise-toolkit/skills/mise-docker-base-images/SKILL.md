---
name: mise-docker-base-images
description: Picking the right Docker base image for mise — debian:slim vs ubuntu vs alpine (with the musl caveat) vs nvidia/cuda vs mcr.microsoft.com/devcontainers/base. Covers glibc vs musl, tool compatibility, and image-size trade-offs.
---

# Picking a Docker base image for mise

mise itself runs fine on most bases, but the **tools** mise installs have opinions about glibc, system libraries, and architecture. Picking the wrong base is the #1 cause of "works on my machine but not in CI" bugs with containerized mise.

## TL;DR — decision table

| Use case | Base image | Why |
|---|---|---|
| **General dev / polyglot** | `debian:12-slim` | glibc, small, broad compatibility with mise-managed tools |
| **Ubuntu shop** | `ubuntu:24.04` | Same story, just the team's preference |
| **Devcontainer target** | `mcr.microsoft.com/devcontainers/base:debian` | Pre-baked dev tools, non-root `vscode` user, works with VSCode out-of-the-box |
| **CUDA/GPU workloads** | `nvidia/cuda:12.x-runtime-ubuntu24.04` | GPU support; use `-devel` if you're building GPU code |
| **ML/data science** | `debian:12-slim` or a micromamba base | Avoid alpine — scikit-learn, numpy, torch all assume glibc |
| **Extreme size constraints** | `gcr.io/distroless/cc-debian12` (runtime only) | Static or carefully-copied binaries only; mise belongs in the builder stage, not here |
| **You really want alpine** | `alpine:3.20` with caveats (see below) | Only if you know what you're doing |

## The `alpine` caveat

Alpine uses **musl libc** instead of glibc. This matters because:

1. **Many mise-managed tools ship precompiled glibc binaries.** Node, Python, Ruby, Go, Bun, Deno, Swift — their upstream release artifacts target glibc. On alpine, mise either has to compile from source (slow) or the binary won't dynamically link.
2. **Python wheels** — any package with a C extension (numpy, cryptography, lxml, psycopg2) has separate manylinux (glibc) and musllinux (musl) wheels. musllinux wheels are much rarer. Expect to compile from source.
3. **Node native modules** — `node-gyp` builds will need `apk add --no-cache python3 make g++`.
4. **Ruby gems with C extensions** — same story, `apk add build-base`.

**Rule of thumb**: if the image will *build* code, avoid alpine. If the image will *only run* a statically-linked Go/Rust binary, alpine is fine for the runtime stage.

For the builder stage, use debian/ubuntu even if the runtime is alpine. Multi-stage lets you mix them:

```dockerfile
FROM debian:12-slim AS builder
# ... mise install + build ...

FROM alpine:3.20 AS runtime
COPY --from=builder /workspace/target/release/myapp /usr/local/bin/myapp
# Only works if myapp is statically linked (Go, `cargo build --target x86_64-unknown-linux-musl`, etc.)
```

## Why `debian:12-slim` is the default

- glibc (no musl surprises).
- Small (~80MB compared to `debian:12`'s ~120MB).
- Has `apt`, which you need for system libs (`libssl-dev`, `libpq-dev`, `libsqlite3-dev`, etc.).
- Widely tested with mise — if something breaks, someone's already hit it.
- Security updates are steady and the base is well-maintained.

## Why `mcr.microsoft.com/devcontainers/base:debian` for devcontainers

- Non-root `vscode` user pre-created (UID 1000).
- `git`, `curl`, `sudo`, `zsh`, and common dev CLIs already installed.
- Dotfiles and oh-my-zsh compatible out of the box.
- Works with the `ghcr.io/devcontainers/features/*` feature system.
- Still debian-based → glibc → no surprises.

## Why `nvidia/cuda` for GPU

- CUDA runtime libs pre-installed.
- Choose `-runtime` for production inference, `-devel` for training / building CUDA kernels.
- Base is Ubuntu 24.04 → glibc → mise-managed Python / torch / jax all just work.
- Pin the CUDA minor version (`12.4.1`) not just major — torch wheels are picky.

## Image-size ranking (rough, uncompressed)

| Base | Size | Notes |
|---|---|---|
| `gcr.io/distroless/static` | ~2MB | Static binaries only |
| `gcr.io/distroless/cc-debian12` | ~20MB | Static or carefully-copied C deps |
| `alpine:3.20` | ~8MB | Musl caveat applies |
| `debian:12-slim` | ~80MB | **Recommended default** |
| `ubuntu:24.04` | ~80MB | Essentially the same |
| `mcr.microsoft.com/devcontainers/base:debian` | ~500MB | Worth it for devcontainers |
| `nvidia/cuda:12.4.1-runtime-ubuntu24.04` | ~3GB | Unavoidable for GPU |

Don't optimize image size prematurely. A 500MB base that boots and builds cleanly is always better than a 20MB base where half your tools don't work.

## See also

- `mise-docker-patterns` — the canonical multi-stage Dockerfile.
- `mise-docker-multistage` — why to split builder and runtime.
- `mise-host-vs-mise-tools` — which things belong in `apt` vs `mise`. The short version: compilers and system libs = apt; language runtimes = mise.
