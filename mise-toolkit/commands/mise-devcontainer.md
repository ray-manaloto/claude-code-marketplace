---
description: Generate a devcontainer.json wired for mise with VSCode extensions, postCreateCommand, and trust env
---

Generate a `.devcontainer/devcontainer.json` for the current project that wires up mise end-to-end. Use `mise generate devcontainer` as the starting point, then post-edit it to add the IDE and trust niceties that the stock template misses.

## Steps

1. **Survey** — detect `mise.toml`, existing `.devcontainer/`, and whether the project is meant for VSCode, JetBrains Gateway, or GitHub Codespaces.

2. **Bootstrap** — if mise is on the host, run:
   ```sh
   mise generate devcontainer
   ```
   Otherwise, emit the template inline per the `mise-devcontainer-patterns` skill.

3. **Post-edit** the generated `devcontainer.json` to add:
   - `"postCreateCommand": "mise trust && mise install"` (the stock template often skips trust).
   - `"containerEnv": { "MISE_TRUSTED_CONFIG_PATHS": "/workspaces" }` so non-interactive trust works for any project mounted under `/workspaces`.
   - `"customizations.vscode.extensions": ["hverlin.mise-vscode"]` for the mise VSCode extension.
   - `"mounts": ["source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached,readonly"]` for ssh agent forwarding of the dev's key.
   - `"remoteEnv": { "PATH": "/home/vscode/.local/share/mise/shims:${containerEnv:PATH}" }` so shims are on PATH for non-login shells.

4. **Show a diff** of the proposed file against any existing `.devcontainer/devcontainer.json` and ask for confirmation before writing.

5. After writing, point the user at:
   - "Reopen in Container" in VSCode, or
   - "Open in Codespaces" for cloud dev,
   - and `/mise-codespaces-prebuild` if they want prebuild caching.

## What to avoid

- Writing the file without showing a diff first.
- Using `remoteUser: root` unless the user explicitly needs it.
- Setting `MISE_TRUSTED_CONFIG_PATHS=/` or similar blanket-trust values.
- Adding VSCode extensions the user hasn't asked for beyond `hverlin.mise-vscode`.
- Installing mise via `curl | sh` in `postCreateCommand` when the base image already has it (check first).

For the full schema reference and edge cases, read `mise-devcontainer-patterns`.
