---
name: mise-docker-patterns
description: The canonical patterns for running mise inside Docker — multi-stage builder/runtime split, BuildKit cache mounts for ~/.local/share/mise/installs, when mise belongs in the runtime stage, and the non-root user pattern. Use when writing a Dockerfile that installs mise or copies mise-managed tools into a container.
---

# mise in Docker — canonical patterns

There's a right way and five wrong ways to put mise in a Dockerfile. This skill covers the right way.

## The golden rule

**mise belongs in the *builder* stage, not the runtime stage.** You install mise, use it to install tools, use those tools to build your app, and then copy the built artifacts into a clean runtime image. The runtime image almost never needs mise itself.

The exception: if the runtime's entrypoint is a mise-managed interpreter (e.g. `python app.py` and python itself is mise-installed), you need *either* mise in the runtime stage *or* (better) a `COPY --from=builder` of the specific interpreter binary plus its shared libs. The latter is cleaner but fiddlier.

## The canonical multi-stage Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
ARG DEBIAN_VERSION=12-slim

# ────────────────────────────────────────────────────────────
# builder stage: install mise + tools, build the app
# ────────────────────────────────────────────────────────────
FROM debian:${DEBIAN_VERSION} AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl git ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install mise. Prefer the bootstrap script if ./bin/mise exists (see mise-docker-bootstrap).
ENV MISE_INSTALL_PATH=/usr/local/bin/mise
RUN curl https://mise.run | sh

ENV MISE_TRUSTED_CONFIG_PATHS=/workspace
WORKDIR /workspace

# Copy mise config first for better layer caching.
COPY mise.toml mise.lock ./

# BuildKit cache mount — tools survive across builds, dramatically speeding up rebuilds.
RUN --mount=type=cache,target=/root/.local/share/mise/installs \
    mise trust && mise install

# Now the rest of the source.
COPY . .

# Use mise-managed tools via `mise exec` (the shims dir would also work).
RUN mise exec -- <your build command>

# ────────────────────────────────────────────────────────────
# runtime stage: clean base, copy just the artifacts
# ────────────────────────────────────────────────────────────
FROM debian:${DEBIAN_VERSION} AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 dev

USER dev
WORKDIR /home/dev/app

COPY --from=builder --chown=dev:dev /workspace/target/release/myapp ./

CMD ["./myapp"]
```

## Why each piece matters

- **`# syntax=docker/dockerfile:1.7`** — enables BuildKit features like cache mounts. Without this line, the `--mount=type=cache` line is a syntax error.
- **Cache mount on `~/.local/share/mise/installs`** — the single biggest build-speed win. Without it, every tool re-downloads and re-installs on every build. With it, incremental builds skip the install entirely.
- **`COPY mise.toml mise.lock ./` before the source** — layer caching. The tools layer only invalidates when the mise config changes, not when source changes.
- **`mise trust && mise install`** — inside containers, there's no TTY to confirm trust interactively. The `MISE_TRUSTED_CONFIG_PATHS=/workspace` env var plus the explicit `mise trust` makes it non-interactive.
- **`mise exec --`** vs adding shims to PATH — both work in the builder stage. `mise exec` is more explicit; shims are more convenient if you have many build commands.
- **Non-root user in runtime** — standard Docker security practice, unrelated to mise but frequently forgotten.

## When to put mise IN the runtime stage

Only if all three are true:
1. The entrypoint is a mise-managed interpreter (`python`, `node`, `ruby`, etc.).
2. The interpreter depends on shared libs or support files that are painful to copy manually.
3. You're okay with the image-size cost (mise itself is ~20MB; a mise install tree is often 200MB+).

If those apply, add to runtime:
```dockerfile
COPY --from=builder /usr/local/bin/mise /usr/local/bin/mise
COPY --from=builder /root/.local/share/mise /home/dev/.local/share/mise
ENV PATH="/home/dev/.local/share/mise/shims:${PATH}"
```

But first, try `COPY --from=builder /root/.local/share/mise/installs/python/3.12 /usr/local/python` and `ENV PATH="/usr/local/python/bin:${PATH}"` — it's smaller and simpler.

## Anti-patterns (the five wrong ways)

1. **Installing mise in the runtime stage just because the Dockerfile tutorial you read did.** 90% of the time you don't need it there.
2. **`RUN curl ... | sh && mise install`** without pinning the mise version. Use the bootstrap pattern (`mise-docker-bootstrap`) for reproducibility.
3. **No BuildKit cache mount.** Every tool reinstall, every build. Minutes become hours.
4. **Running as root in runtime.** Separate security issue but usually shipped by the same people who also don't multi-stage.
5. **`COPY . .` before `COPY mise.toml`** — destroys layer caching for the tools install.

## See also

- `mise-docker-multistage` — deeper dive on the builder/runtime split.
- `mise-docker-base-images` — picking the right base (debian vs ubuntu vs alpine vs cuda).
- `mise-docker-bootstrap` — the `mise generate bootstrap` pattern for pinned mise.
- `mise-devcontainer-patterns` — when you want a devcontainer on top of this.
- `/mise-dockerfile` — generates a starting Dockerfile from this pattern.
