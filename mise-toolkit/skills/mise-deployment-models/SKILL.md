---
name: mise-deployment-models
description: The five deployment models for mise — native host (Linux/Mac), Docker base image, devcontainer / Codespaces, CI runner, and dotfiles-as-code — with the trade-offs and the file you need to write for each. Use when deciding "where should mise live" or "host vs container".
---

# Deployment models for mise

There are five places mise typically runs. They're not mutually exclusive — most real teams use 2-3 of them at once.

## 1. Native on the host (macOS / Linux)

**Best for**: solo developers, day-to-day local development, fast iteration, IDE integration.

```sh
curl https://mise.run | sh
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
```

**Pros**:
- Fastest dev loop. No container start time. No filesystem sync overhead.
- Best IDE integration (extensions, debuggers, language servers all just work).
- Easiest to use with system tools (`brew`, `apt`).

**Cons**:
- Tool versions are pinned per-project but the **host** itself is whatever the developer has.
- New team members hit "works on my machine" issues with system libraries (libssl, libpq, etc.).
- macOS vs Linux differences leak into your dev experience.

**File you need**: `mise.toml` in each project, plus `mise activate` in your shell rc.

## 2. Docker base image

**Best for**: production-parity dev, projects with complex system dependencies, polyglot teams.

```dockerfile
FROM debian:12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ca-certificates build-essential libssl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh
WORKDIR /workspace
COPY mise.toml mise.lock ./
RUN mise install
ENV PATH="/root/.local/share/mise/shims:${PATH}"
```

**Pros**:
- Reproducible across host machines — no "works on my machine".
- System libraries and dev tools both pinned (apt for libs, mise for tools).
- Can ship as a base image for the team.

**Cons**:
- Slower dev loop unless you mount the source dir as a volume.
- IDE integration is more involved (need to wire VSCode/IntelliJ to the container).
- Docker itself is a tool you need on every dev machine.

**File you need**: `Dockerfile` + `mise.toml` + `mise.lock`. See `mise-docker-patterns` (v0.3).

## 3. Devcontainer / Codespaces

**Best for**: teams that want zero-setup onboarding, GitHub-hosted dev, contributors who can't install software locally.

```json
// .devcontainer/devcontainer.json
{
  "name": "myproject",
  "image": "mcr.microsoft.com/devcontainers/base:debian",
  "features": {
    "ghcr.io/devcontainers/features/common-utils:2": {}
  },
  "postCreateCommand": "curl https://mise.run | sh && echo 'eval \"$(mise activate bash)\"' >> ~/.bashrc && mise install",
  "customizations": {
    "vscode": {
      "extensions": ["hverlin.mise-vscode"]
    }
  },
  "remoteEnv": {
    "PATH": "/root/.local/bin:/root/.local/share/mise/shims:${containerEnv:PATH}"
  }
}
```

Or use mise's built-in generator:

```sh
mise generate devcontainer
```

**Pros**:
- Onboarding = "Open in Codespaces" or "Reopen in Container". Zero install.
- Same environment across the whole team automatically.
- Works in VSCode, JetBrains Gateway, GitHub Codespaces, GitPod.
- Combines Docker reproducibility with IDE-native UX.

**Cons**:
- Slower than native on macOS (Docker Desktop overhead).
- Codespaces has $$ cost (free tier exists for personal accounts).
- Some debugging scenarios (kernel-level, eBPF, etc.) are awkward.

**File you need**: `.devcontainer/devcontainer.json` + `mise.toml` + `mise.lock`. See `mise-devcontainer-patterns` (v0.3).

## 4. CI runner

**Best for**: every project, period. CI must reproduce the dev environment exactly.

```yaml
# .github/workflows/ci.yml
- uses: jdx/mise-action@v3
  with:
    version: 2026.4.6
    install: true
    cache: true
- run: mise run test
```

**Pros**:
- Single source of truth: `mise.toml` defines tools for dev AND CI.
- `jdx/mise-action@v3` handles install + cache automatically.
- Cache key is `mise.toml` + `mise.lock` content — fast subsequent runs.
- Automatic redaction of `redact = true` env vars in logs.

**Cons**: none — this is a strict win over hand-rolled tool installation in CI.

**File you need**: a workflow file using `jdx/mise-action@v3` (GitHub Actions) or equivalents for GitLab/CircleCI/Buildkite. See `mise-ci-github-actions`.

## 5. Dotfiles-as-code

**Best for**: developers who manage their machine setup with a dotfiles repo.

Add `mise.toml` to your dotfiles repo's root, with your global tools:

```toml
# ~/dotfiles/.config/mise/config.toml
[tools]
node = "lts"
python = "3.12"
"npm:@anthropic-ai/claude-code" = "latest"
gh = "latest"
ripgrep = "latest"
fd = "latest"
```

Symlink or stow it into `~/.config/mise/config.toml`. New machines: clone dotfiles, install mise, run `mise install`. Done.

**Pros**:
- New machine = `mise install` and you have your tools.
- Same toolchain across all your machines.
- Versioned in git.

**Cons**:
- No project isolation — these are your global tools.
- If you symlink, mise may track the symlink target path for trust (workaround: `mise trust` the actual file).

## How to combine them

A typical professional setup uses **all five**:

1. **Host**: mise on the dev's laptop for IDE integration and fast iteration.
2. **Docker**: a base image for production parity, used for integration tests.
3. **Devcontainer**: optional, for new contributors who don't want to set up locally.
4. **CI**: mise-action in every workflow.
5. **Dotfiles**: developer's personal global tools.

The key insight: **the same `mise.toml` works in all five**. Write it once, run it everywhere.

## Decision flowchart

```
Is this your personal dev machine?         → Native host (#1) + dotfiles (#5)
Is this a complex polyglot project?        → Native host (#1) + Docker base image (#2) + CI (#4)
Is onboarding new contributors painful?    → Add devcontainer (#3)
Do you need IDE-native UX?                 → Native host (#1) or devcontainer (#3) — not raw Docker
Is the project a library (no service)?     → Native host (#1) + CI (#4) is enough
Production has weird system dependencies?  → Docker (#2) is non-negotiable
```

## See also

- `mise-host-vs-mise-tools` — what to install via apt/brew vs mise (the #1 newbie mistake)
- `mise-install-paths` — every install method for #1
- `mise-ci-github-actions` — #4 in detail
- `mise-docker-patterns` (v0.3) — #2 in detail
- `mise-devcontainer-patterns` (v0.3) — #3 in detail
