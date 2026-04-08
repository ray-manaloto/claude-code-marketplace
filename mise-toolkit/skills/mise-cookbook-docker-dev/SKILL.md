---
name: mise-cookbook-docker-dev
description: End-to-end recipe for a Docker-based dev loop with mise — multi-stage Dockerfile with mise pre-installed, docker-compose for services (Postgres, Redis), BuildKit cache mounts, and mise tasks that wrap compose. Use when running dev entirely in containers or prod-parity testing.
---

# Cookbook — Docker-based dev loop

A complete Docker dev setup where mise is in the builder stage, tools are cache-mounted, and `docker compose` orchestrates the app + services. The host runs Docker and mise; everything else lives in containers.

## Who this is for

- Projects with complex native system dependencies (libpq, libsodium, libvips, etc.) where "works on my machine" is a real problem.
- Teams mixing macOS and Linux devs who want prod-parity dev.
- Services with multiple moving parts (app + db + cache + worker + message broker).

## Who this isn't for

- Pure Node / Python / Go libraries — native mise on the host is faster. Use the language cookbooks instead.
- Projects where Docker Desktop's file-sync overhead would kill the dev loop.
- IDE-heavy workflows that aren't set up for devcontainers — see `mise-cookbook-node-nextjs` etc. instead.

## The `mise.toml`

```toml
min_version = '2026.4.0'

[tools]
# The host needs mise to run the tasks, but the app's runtime lives in the container.
# Pin anything the host dev actually runs outside the container.

[env]
COMPOSE_PROJECT_NAME = "myapp"
COMPOSE_FILE = "docker-compose.yml:docker-compose.dev.yml"
DOCKER_BUILDKIT = "1"
BUILDKIT_PROGRESS = "plain"

[tasks.build]
description = "Build the dev image"
run = "docker compose build --pull"
sources = ["Dockerfile", "mise.toml", "mise.lock"]

[tasks.up]
description = "Start the full stack in the background"
depends = ["build"]
run = "docker compose up -d"

[tasks.down]
description = "Stop the stack"
run = "docker compose down"

[tasks.logs]
description = "Tail all container logs"
run = "docker compose logs -f"

[tasks.sh]
description = "Shell into the app container"
run = "docker compose exec app bash"

[tasks.dev]
description = "Start the stack and tail the app log"
depends = ["up"]
run = "docker compose logs -f app"

[tasks.test]
description = "Run the test suite inside the container"
depends = ["up"]
run = "docker compose exec -T app mise run test"

[tasks.clean]
description = "Nuke containers, volumes, and build cache"
run = [
  "docker compose down -v",
  "docker buildx prune -f"
]

[tasks.reset]
description = "Rebuild from scratch and restart"
depends = ["clean", "build", "up"]
run = "echo 'reset complete'"
```

## The `Dockerfile` (multi-stage with mise)

```dockerfile
# syntax=docker/dockerfile:1.7
ARG DEBIAN_VERSION=12-slim

# ────────────────────────────────────────────────────────────
# Base — shared setup for builder and runtime
# ────────────────────────────────────────────────────────────
FROM debian:${DEBIAN_VERSION} AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ────────────────────────────────────────────────────────────
# Builder — installs mise + tools
# ────────────────────────────────────────────────────────────
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libssl-dev libreadline-dev libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

ENV MISE_INSTALL_PATH=/usr/local/bin/mise
RUN curl https://mise.run | sh

ENV MISE_TRUSTED_CONFIG_PATHS=/workspace
WORKDIR /workspace

# Copy mise config first so the tools layer caches aggressively
COPY mise.toml mise.lock ./

RUN --mount=type=cache,target=/root/.local/share/mise/installs \
    --mount=type=cache,target=/root/.cache/mise \
    mise trust && mise install

# Copy the rest of the source
COPY . .

# ────────────────────────────────────────────────────────────
# Dev — the image used by docker-compose up
# ────────────────────────────────────────────────────────────
FROM builder AS dev
ENV PATH="/root/.local/share/mise/shims:${PATH}"
WORKDIR /workspace
CMD ["mise", "run", "dev"]

# ────────────────────────────────────────────────────────────
# Runtime — the production image (optional)
# ────────────────────────────────────────────────────────────
FROM base AS runtime
RUN useradd -m -u 1000 app
USER app
WORKDIR /home/app
# Copy only the artifacts you need from builder:
COPY --from=builder --chown=app:app /workspace/dist ./dist
CMD ["./dist/server"]
```

## The `docker-compose.yml` + `docker-compose.dev.yml`

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: dev
    volumes:
      - .:/workspace
      - mise-installs:/root/.local/share/mise/installs   # cache tools across rebuilds
    environment:
      DATABASE_URL: postgres://postgres:postgres@db:5432/myapp
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    ports:
      - "3000:3000"

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
  mise-installs:
```

```yaml
# docker-compose.dev.yml — dev-only overrides
services:
  app:
    environment:
      LOG_LEVEL: debug
      RUST_BACKTRACE: "1"   # or equivalent for your language
    stdin_open: true
    tty: true
```

## What this gives you

- **Prod-parity environment** — the same Debian base image as production, the same tools installed the same way.
- **Fast rebuilds** — BuildKit cache mounts keep mise's installs dir warm between `docker compose build` runs.
- **Tool cache volume** — the `mise-installs` named volume preserves installed tools across container removal.
- **One set of commands** — `mise run up`, `mise run test`, `mise run sh` — no memorizing raw docker compose flags.
- **Production image path** — the same Dockerfile builds a `runtime` stage for deployment.

## First-run walkthrough

```sh
# 1. Clone + trust
git clone <repo> myapp && cd myapp
mise trust

# 2. Make sure Docker + compose are running on the host
docker version
docker compose version

# 3. Build and start the stack
mise run build
mise run up

# 4. Tail the app log
mise run logs

# 5. Shell in when you need to
mise run sh
# inside the container: mise run test, etc.
```

## Common gotchas

1. **File-sync overhead on macOS** → Docker Desktop on macOS syncs bind-mounted volumes through a VM. For large node_modules/vendor dirs, use a named volume for those paths, not a bind mount.
2. **`mise trust` prompts inside the container** → `MISE_TRUSTED_CONFIG_PATHS=/workspace` in the Dockerfile handles it. Also run `mise trust` explicitly in the builder stage.
3. **Stale `mise.lock` not triggering rebuild** → `sources = ["Dockerfile", "mise.toml", "mise.lock"]` on the build task watches all three. If you edit tools outside those files, add them to `sources`.
4. **BuildKit cache mount ignored** → Make sure `# syntax=docker/dockerfile:1.7` is the first line. Without it, `--mount=type=cache` is a syntax error.
5. **Volume permissions on Linux** → Bind-mounted source files are owned by the host user (usually UID 1000). The container's dev user must match. Use `USER $(id -u):$(id -g)` or a named user with matching UID.
6. **`docker compose` vs `docker-compose`** → Use the v2 plugin syntax (`docker compose`). v1 is deprecated.
7. **Forgetting `docker compose down -v`** → Leaves volumes around. `mise run clean` handles it.
8. **Compose loading the wrong file** → `COMPOSE_FILE` in `[env]` makes the file selection explicit; otherwise compose silently picks `docker-compose.yml` from cwd.

## Variant — devcontainer instead of raw docker compose

If you want VSCode / GitHub Codespaces integration, use `.devcontainer/devcontainer.json` on top of this image. See `mise-devcontainer-patterns` and `mise-cookbook-docker-dev` can coexist — the Dockerfile is shared.

## See also

- `mise-docker-patterns` — the canonical multi-stage Dockerfile.
- `mise-docker-multistage` — when to put mise in the runtime stage.
- `mise-docker-bootstrap` — pinning mise itself in the Dockerfile.
- `mise-devcontainer-patterns` — VSCode / Codespaces variant.
- `/mise-dockerfile` — generate a starting Dockerfile from a project.
- `mise-host-vs-mise-tools` — apt vs mise rule.
