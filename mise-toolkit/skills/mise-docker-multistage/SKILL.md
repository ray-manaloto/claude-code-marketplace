---
name: mise-docker-multistage
description: The builder → runtime multi-stage split for mise-based Dockerfiles — what to copy across stages, when mise itself belongs in the runtime stage, and how to keep the runtime image small without losing reproducibility.
---

# Multi-stage Dockerfiles with mise

Multi-stage is not optional for production Docker images with mise. The mise install tree (~/.local/share/mise/installs/) is easily 200MB-1GB of compilers, sources, and runtime libs you don't want in your deployed image.

## The mental model

Think of mise as a **build-time concern**, not a runtime concern. mise's job is to give you pinned, reproducible versions of `node`, `python`, `go`, `cargo`, etc. while you're *building* the app. Once the app is built, you ship the app — not the toolchain.

```
┌──────────────────┐         ┌──────────────────┐
│ builder stage    │         │ runtime stage    │
│                  │         │                  │
│ + mise           │  COPY   │ + app artifact   │
│ + installed tools│ ──────▶ │ + runtime libs   │
│ + source code    │         │ + non-root user  │
│ + build output   │         │                  │
└──────────────────┘         └──────────────────┘
  (big, discarded)            (small, shipped)
```

## What to copy across stages

### For compiled languages (Go, Rust, C++)

Copy just the binary. The runtime doesn't need mise, Go, or cargo at all.

```dockerfile
FROM debian:12-slim AS runtime
COPY --from=builder /workspace/target/release/myapp /usr/local/bin/myapp
```

This is the cleanest case and the biggest size win. A 1GB builder stage becomes a 100MB runtime stage trivially.

### For interpreted languages with bundled deps (Node, Python)

Copy the app directory plus `node_modules` / the virtualenv / the lock file. Then copy the specific interpreter binary.

```dockerfile
FROM debian:12-slim AS runtime
# Copy the interpreter from mise's install tree
COPY --from=builder /root/.local/share/mise/installs/node/20.11.0 /usr/local/node
ENV PATH="/usr/local/node/bin:${PATH}"

WORKDIR /app
COPY --from=builder /workspace/node_modules ./node_modules
COPY --from=builder /workspace/dist ./dist
COPY --from=builder /workspace/package.json ./

CMD ["node", "dist/server.js"]
```

This is the **surgical** pattern — you ship exactly one interpreter version, no mise, no build tools. ~150MB total.

### For interpreted languages where you want full mise flexibility in runtime

Copy the whole mise tree. Simplest, biggest.

```dockerfile
FROM debian:12-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/mise /usr/local/bin/mise
COPY --from=builder /root/.local/share/mise /home/dev/.local/share/mise
COPY --from=builder /workspace/mise.toml /workspace/mise.lock /app/

RUN useradd -m -u 1000 dev && chown -R dev:dev /home/dev/.local /app
USER dev
WORKDIR /app

COPY --from=builder --chown=dev:dev /workspace/dist ./dist
COPY --from=builder --chown=dev:dev /workspace/node_modules ./node_modules

ENV MISE_TRUSTED_CONFIG_PATHS=/app
ENV PATH="/home/dev/.local/share/mise/shims:${PATH}"

CMD ["node", "dist/server.js"]
```

Use this when:
- Multiple tools are in play (not just one interpreter).
- You use `mise run <task>` as the container entrypoint.
- Debugging production means `docker exec` + running mise commands.

## What NOT to copy

- **The source code** (unless the runtime is interpreted and needs it — then copy only `dist/` or equivalent, not the whole repo).
- **`node_modules` from the builder if they include dev deps.** Install with `npm ci --omit=dev` in the builder, or prune in a separate RUN step before the stage boundary.
- **Build caches** (`~/.cache`, `~/.npm`, `~/.cargo/registry`). These are the whole point of using a BuildKit cache mount — they stay in the builder, never in the final image.
- **`apt` lists** (`/var/lib/apt/lists/*`) — always `rm -rf` after install.
- **The mise install tree** if all you need is one specific binary from it.

## Stage naming conventions

Use explicit names, not numbers:

```dockerfile
FROM debian:12-slim AS base        # shared setup
FROM base AS builder               # adds mise + tools + source
FROM base AS runtime               # clean, gets just the artifact
```

A `base` stage for shared apt installs deduplicates the `apt-get update && install ca-certificates` step.

## The "why not just one stage" trap

"My CI is simple, I just have one big stage" is fine for development, but:

1. Every CI push ships mise, all the tools, source, build cache to your registry.
2. Every `docker pull` in prod downloads all that.
3. Every running container has a toolchain attackers can use.
4. Every image scanner flags every vuln in the build tools.

Multi-stage is the most impactful refactor you can do to a Dockerfile. If you're going to adopt mise in Docker, adopt multi-stage in the same PR.

## See also

- `mise-docker-patterns` — the end-to-end canonical Dockerfile.
- `mise-docker-base-images` — picking the base for builder and runtime (they don't have to match).
- `mise-docker-bootstrap` — pinning the mise version in the builder.
- Docker docs: `docs.docker.com/build/building/multi-stage/`.
