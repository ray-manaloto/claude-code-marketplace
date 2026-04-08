---
description: Wire VSCode to mise — install the mise-vscode extension, configure automation profile, or fall back to shims-on-PATH
---

Set up VSCode so it picks up mise-managed tools automatically. There are two paths; pick the right one for the user's situation.

## Path A — `hverlin.mise-vscode` extension (preferred)

This is the best experience for most users. The extension reads `mise.toml`, surfaces tools in the sidebar, and wires the integrated terminal to the right tool versions.

1. Install the extension:
   ```sh
   code --install-extension hverlin.mise-vscode
   ```
2. Open any workspace that has a `mise.toml` — the extension auto-detects.
3. Verify: open the command palette and run `Mise: Show Current Tools`. It should list the project's tools.

## Path B — shims-on-PATH (fallback)

Use this when the user can't or won't install the extension, or needs tools in contexts the extension doesn't cover (debugger launch configs, task runners, external tool subprocesses).

1. Add the mise shims directory to `settings.json` (User or Workspace):
   ```jsonc
   {
     "terminal.integrated.env.osx": {
       "PATH": "${env:HOME}/.local/share/mise/shims:${env:PATH}"
     },
     "terminal.integrated.env.linux": {
       "PATH": "${env:HOME}/.local/share/mise/shims:${env:PATH}"
     }
   }
   ```
2. For the **automation profile** quirk (tasks, debug, external tools on macOS), also set:
   ```jsonc
   {
     "terminal.integrated.automationProfile.osx": {
       "path": "/bin/zsh",
       "args": ["-l"]
     }
   }
   ```
   This forces automation subprocesses through a login shell so `mise activate` in `~/.zshrc` / `~/.zprofile` runs.

## Dual-mode setup

For maximum reliability, do both: `mise activate zsh` in `~/.zshrc` for interactive terminals, and add the shims path in `settings.json` so non-interactive subprocesses still see tools.

## Steps

1. Ask the user whether they want Path A (extension) or Path B (shims only).
2. Show the edits to be made to `settings.json` as a diff.
3. Apply after confirmation.
4. Verify: open a new integrated terminal and run `which node` (or whatever tool the project uses) — it should resolve to `~/.local/share/mise/shims/<tool>` or `~/.local/share/mise/installs/<tool>/...`.

For the full rationale (why the automation profile quirk exists, dual-mode trade-offs), read `mise-vscode-integration`.
