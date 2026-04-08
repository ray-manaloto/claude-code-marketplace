---
name: mise-ide-activation
description: Cross-cutting overview of how to wire mise into every major IDE — VSCode, JetBrains, Neovim, Xcode, Zed, Sublime Text. The "if you're not sure where to start" entry point that points to per-IDE skills for depth. Use when a user says "how do I make my IDE see mise".
---

# IDE activation — the overview

Every IDE has the same fundamental problem: **how does it find the tool versions that mise pins for this project?** There are only four ways to solve it, and every IDE uses one or more of them.

## The four mechanisms

### 1. Shims on PATH

`~/.local/share/mise/shims` is a directory of shim scripts. Each shim is named after a tool (`python`, `node`, `go`, etc.) and resolves to the project-appropriate version by reading `mise.toml` at invocation time.

**Put this directory on PATH** and 90% of IDE-mise problems disappear. Anywhere the IDE types `python` or spawns `node`, it hits a shim and gets the right version.

This is **universal**: works in every IDE that respects PATH, which is all of them.

### 2. `mise activate` in the login shell

If you run `eval "$(mise activate zsh)"` in `~/.zshrc` (or `~/.bash_profile`), then any IDE launched from a terminal inherits the activation. This also handles env vars from `[env]`, not just tools.

The catch: IDEs launched from GUI launchers (Alfred, Spotlight, Dock, taskbar) don't always run the login shell. So this alone isn't enough.

### 3. Native mise support (via plugin/extension)

A few IDEs have first-party mise plugins:
- **VSCode**: `hverlin.mise-vscode`
- **JetBrains**: `134130/intellij-mise`
- (Neovim, Zed, Sublime, Helix: no native plugin yet — they rely on PATH.)

These plugins read `mise.toml` directly and integrate mise tasks + tools into the IDE UI.

### 4. asdf compatibility

mise's install layout is asdf-compatible. Any IDE with asdf support (older JetBrains, some language plugins) can be pointed at mise's installs by symlinking:

```sh
ln -sfn ~/.local/share/mise/installs ~/.asdf/installs
```

This is the fallback when an IDE's language plugin predates mise support but does know about asdf.

## Decision tree — which mechanism do I need?

```
Which IDE?
├── VSCode
│   └── Install hverlin.mise-vscode + add shims to PATH in settings.json
│       Plus: automationProfile.osx login shell (see mise-vscode-integration)
│
├── JetBrains (IntelliJ, PyCharm, GoLand, etc.)
│   └── Install 134130/intellij-mise plugin
│       Fallback: asdf symlink (see mise-jetbrains-integration)
│
├── Neovim
│   └── Add vim.env.PATH prepend in init.lua
│       (see mise-neovim-integration)
│
├── Xcode
│   └── Add shims to PATH in .xcode.env.local or build phase
│       (see Xcode section below)
│
├── Zed / Sublime / Helix / other
│   └── Add shims to PATH at the OS / login-shell level, that's enough
│
└── Emacs
    └── Use exec-path-from-shell, or hard-code mise shims in exec-path
```

## The universal fallback: shims-on-PATH at the OS level

If you don't want to wire every IDE individually, set mise shims on PATH at the shell level and launch every IDE from that shell:

```sh
# ~/.zshrc (or ~/.bash_profile)
export PATH="$HOME/.local/share/mise/shims:$PATH"
```

Now:
- Any terminal session: has shims on PATH.
- Any IDE launched from that terminal: inherits PATH.
- Any tool the IDE spawns: hits a shim, gets the right version.

The downside: GUI launchers (Spotlight, Alfred) don't inherit shell env. Workarounds:

- **macOS**: use `launchctl setenv PATH "$HOME/.local/share/mise/shims:$PATH"` in a LaunchAgent. Persists across reboots.
- **Linux with systemd**: set `Environment=PATH=...` in `~/.config/environment.d/mise.conf`.
- **Windows**: edit user-level PATH in System Properties → Environment Variables.

## Xcode specifically

Xcode is the most annoying case because it doesn't read shell rc files AND its build phases run in a sandbox. Pattern:

1. Create `.xcode.env.local` in the project root:
   ```sh
   export PATH="$HOME/.local/share/mise/shims:$PATH"
   ```
2. Reference it from `.xcode.env`:
   ```sh
   source .xcode.env.local
   ```
3. For CocoaPods / Fastlane / Tuist build phases, add a shell phase that sources the mise shims at the top.

There's no native Xcode plugin for mise. You're in PATH-manipulation territory.

## Why so many mechanisms?

Each IDE has its own philosophy about how to find tools:
- **VSCode** follows PATH for most things but has the automation profile quirk.
- **JetBrains** has its own SDK abstraction that predates mise.
- **Neovim** is the simplest because it just inherits the parent process env.
- **Xcode** is the worst because Apple.

The good news: **shims-on-PATH works everywhere as a baseline**. Native plugins are nice-to-haves on top.

## Quick-start recipe — "I just want it to work"

1. Put `export PATH="$HOME/.local/share/mise/shims:$PATH"` in `~/.zshrc`.
2. Put `eval "$(mise activate zsh)"` in `~/.zshrc`.
3. For macOS GUI launches: `launchctl setenv PATH "$HOME/.local/share/mise/shims:$PATH"` or log out and back in after editing PATH.
4. Install the native extension/plugin for your IDE if one exists.
5. Done.

If something still doesn't see the right version, read the per-IDE skill for that IDE.

## See also

- `mise-vscode-integration` — VSCode depth, including the automation profile quirk.
- `mise-jetbrains-integration` — JetBrains depth, including the asdf symlink.
- `mise-neovim-integration` — Neovim depth, including the vim.env.PATH pattern.
- `mise-pathing-and-shims` — what shims actually are under the hood.
- `mise-shell-activation` — shell-level activation details.
- `/mise-vscode-setup` and `/mise-jetbrains-setup` — guided wiring commands.
