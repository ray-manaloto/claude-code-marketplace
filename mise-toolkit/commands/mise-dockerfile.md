---
description: Generate a multi-stage Dockerfile with mise pre-installed (builder + runtime, BuildKit cache mount, non-root user)
---

Generate a production-ready multi-stage `Dockerfile` that uses mise to manage the project's tools. The result must follow the patterns in the `mise-docker-patterns`, `mise-docker-multistage`, `mise-docker-bootstrap`, and `mise-docker-base-images` skills.

## Steps

1. **Survey the project** (parallel reads):
   - Detect language/runtime from `mise.toml`, `package.json`, `pyproject.toml`, `go.mod`, `Gemfile`, `Cargo.toml`, etc.
   - Check for an existing `Dockerfile`, `Dockerfile.*`, or `.dockerignore`.
   - Check whether `./bin/mise` already exists (bootstrap pattern).

2. **Pick a base image** per `mise-docker-base-images`:
   - Default: `debian:12-slim` (glibc, broad compatibility).
   - Node/Python/Ruby/Go native workloads: `debian:12-slim`.
   - CUDA: `nvidia/cuda:<ver>-runtime-ubuntu24.04`.
   - Avoid `alpine` unless the user explicitly asks — mise's precompiled binaries (and many core tools) assume glibc.
   - For devcontainer targets: `mcr.microsoft.com/devcontainers/base:debian`.

3. **Prefer the bootstrap pattern** (`mise generate bootstrap -l -w`) if the user is okay committing `./bin/mise` to the repo. It removes the `curl | sh` network fetch from the build and pins the mise version. Otherwise fall back to `curl https://mise.run | sh`.

4. **Emit a multi-stage Dockerfile** with:
   - `FROM ... AS builder` stage that installs mise, runs `mise trust` + `mise install`, and builds the app.
   - `FROM ... AS runtime` stage that copies just the built artifacts + the `~/.local/share/mise/installs` directory (or the shims dir) from the builder. Only include mise itself in the runtime stage if the runtime actually needs to invoke mise-managed tools (usually it does not — prefer `COPY --from=builder` of the specific binary).
   - `# syntax=docker/dockerfile:1.7` header so BuildKit is explicit.
   - A BuildKit cache mount: `RUN --mount=type=cache,target=/root/.local/share/mise/installs mise install`.
   - A non-root user (`useradd -m dev` + `USER dev`) in the runtime stage.
   - `ENV MISE_TRUSTED_CONFIG_PATHS=/workspace` so non-interactive trust works inside the container.
   - `ENV PATH="/home/dev/.local/share/mise/shims:${PATH}"` so tools are on PATH without needing `mise activate`.

5. **Show the Dockerfile as a diff** (or as a new-file preview if there's no existing one) and ask the user to confirm before writing.

6. After writing, suggest:
   - `docker build --progress=plain -t <name> .`
   - Adding `/bin/mise` and `mise.lock` to source control if using the bootstrap pattern.
   - Running `/mise-devcontainer` next if this is also going to be a devcontainer.

## What to avoid

- Installing mise in both the builder and runtime stage without reason (you usually only need it in builder).
- Running `mise install` without `mise trust` first (container builds are non-interactive — trust must be explicit).
- Hardcoding a mise version with `curl | sh` — use `mise generate bootstrap` to pin it.
- Using `alpine` as the base unless the user explicitly accepts the musl caveats.
- Using `latest` tags for the base image — pin a specific digest or at least a major version.
- Writing the file without showing a diff first.

For the underlying patterns and trade-offs, read the `mise-docker-patterns`, `mise-docker-multistage`, `mise-docker-bootstrap`, and `mise-docker-base-images` skills.
