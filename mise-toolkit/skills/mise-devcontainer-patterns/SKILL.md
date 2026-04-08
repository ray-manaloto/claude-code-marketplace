---
name: mise-devcontainer-patterns
description: The full devcontainer.json schema for projects using mise — features, postCreateCommand, mounts, customizations.vscode, containerEnv, and the trust + activation patterns that the stock `mise generate devcontainer` output misses. Use when writing or reviewing a .devcontainer/devcontainer.json.
---

# devcontainer.json patterns for mise

`mise generate devcontainer` writes a minimal starting point. This skill covers what to add on top so the result actually works end-to-end for a real team.

## The canonical devcontainer.json

```jsonc
{
  "name": "myproject",
  "image": "mcr.microsoft.com/devcontainers/base:debian",

  // onCreateCommand runs during prebuild; postCreateCommand runs on every codespace start.
  // Put mise install in onCreate so it's cached in Codespaces prebuilds.
  "onCreateCommand": "curl https://mise.run | sh && echo 'eval \"$(/home/vscode/.local/bin/mise activate bash)\"' >> /home/vscode/.bashrc && /home/vscode/.local/bin/mise trust && /home/vscode/.local/bin/mise install",

  // postCreateCommand runs after the source is mounted — good place for language-level installs.
  "postCreateCommand": "mise exec -- npm ci || true",

  "containerEnv": {
    // Non-interactive trust for any project mounted under /workspaces.
    "MISE_TRUSTED_CONFIG_PATHS": "/workspaces"
  },

  "remoteEnv": {
    // Shims on PATH so non-interactive shells (VSCode tasks, debuggers) see mise tools.
    "PATH": "/home/vscode/.local/share/mise/shims:${containerEnv:PATH}"
  },

  "mounts": [
    // Forward the host ssh key (read-only) so git push works from inside the container.
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly"
  ],

  "customizations": {
    "vscode": {
      "extensions": [
        "hverlin.mise-vscode"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash"
      }
    }
  },

  "remoteUser": "vscode",

  // Wait for onCreate (not postCreate) before signaling ready — so prebuilds complete first.
  "waitFor": "onCreateCommand"
}
```

## Why each piece matters

### `onCreateCommand` vs `postCreateCommand`

- **`onCreateCommand`** runs once, when the container filesystem is first created. In GitHub Codespaces **prebuilds**, this runs during the prebuild job. Its output is baked into the prebuild image.
- **`postCreateCommand`** runs every time a codespace is created from the prebuild. If you put `mise install` here, every codespace start re-downloads tools. If you put it in `onCreateCommand`, it runs once during the prebuild.

**Rule**: tool installation → `onCreateCommand`. Source-dependent setup (`npm ci`, `bundle install`) → `postCreateCommand`, because source isn't mounted until after onCreate.

### `containerEnv.MISE_TRUSTED_CONFIG_PATHS`

mise refuses to load a config file it hasn't explicitly trusted, for security. In an interactive shell on your laptop, you run `mise trust` once and you're done. In a non-interactive devcontainer build, there's no one to type `y`.

Setting `MISE_TRUSTED_CONFIG_PATHS=/workspaces` marks any mise config under `/workspaces` (where VSCode mounts the repo) as trusted. Combined with `mise trust` in `onCreateCommand` it's belt-and-suspenders reliability.

**Do NOT** set this to `/` — that defeats the trust system entirely. Scope it to where repos actually live.

### `remoteEnv.PATH`

There are three ways to make mise tools available:
1. `eval "$(mise activate bash)"` in `~/.bashrc` — works for interactive terminals.
2. Shims on PATH in `remoteEnv` — works for everything VSCode launches (tasks, debuggers, external tools).
3. Both — maximum reliability, no downside.

Use both. They don't conflict.

### `mounts` — ssh agent forwarding

Most devcontainer tutorials skip this, and then `git push` fails mysteriously inside the container. Mounting the host's `~/.ssh` (read-only) gets the key into the container. For a better approach on Linux hosts, use ssh-agent socket forwarding instead.

On Windows/WSL, the path is `${localEnv:USERPROFILE}\\.ssh` with caveats. On macOS, the `HOME` form works.

### `customizations.vscode.extensions`

`hverlin.mise-vscode` is the only mise-specific extension that matters. Add language extensions per the project's stack, but don't over-provision — devcontainers can install them per-user via `settings.json` too.

### `remoteUser: vscode`

The `mcr.microsoft.com/devcontainers/base` images ship with a pre-created `vscode` user (UID 1000). Honor it. Setting `remoteUser: root` is a smell.

### `waitFor: onCreateCommand`

Without this, VSCode reports "ready" as soon as the container boots, before `mise install` has finished. Users then get errors opening a terminal because tools aren't installed yet. `waitFor` gates the "ready" signal on the specified lifecycle step completing.

## Features vs manual install

`ghcr.io/devcontainers/features/*` is the community feature system for devcontainers. There's no official `mise` feature yet, so you install via `onCreateCommand` as above. But you can still use other features:

```jsonc
"features": {
  "ghcr.io/devcontainers/features/common-utils:2": {},
  "ghcr.io/devcontainers/features/git:1": {}
}
```

Don't use language features (`node:1`, `python:1`, etc.) — they conflict with mise's version management. Let mise own the tools.

## Multi-folder workspaces

If the devcontainer covers multiple repos, put each under `/workspaces/<name>` and set `MISE_TRUSTED_CONFIG_PATHS=/workspaces` so all of them are trusted.

## Debugging

If `mise install` fails silently during `onCreateCommand`:
1. Check the Codespaces creation logs: `gh codespace logs`.
2. Add `|| (cat ~/.local/state/mise/log/mise.log && false)` to surface mise's own log.
3. Rebuild from scratch: `Codespaces: Rebuild Container (Full)`.

## See also

- `mise-codespaces` — prebuilds, secrets, cost considerations.
- `mise-docker-base-images` — why `mcr.microsoft.com/devcontainers/base` is the devcontainer default.
- `mise-vscode-integration` — the host-side VSCode counterpart.
- `/mise-devcontainer` — scaffolds this from a project.
- devcontainer spec: `containers.dev/implementors/json_reference/`.
