---
name: mise-shell-activation
description: Activation snippets for every shell mise supports — bash, zsh, fish, nushell, elvish, xonsh, PowerShell — plus the dual-mode pattern for IDE compatibility, and the difference between login/interactive rc files. Use when adding `mise activate` to a shell rc, debugging "mise not loading", or supporting an unusual shell.
---

# Shell activation

`mise activate` registers a shell hook that runs `mise hook-env` on every prompt display, updating PATH and env vars when you change directories or edit `mise.toml`. Without activation, mise still works via `mise exec` / `mise x` and shims, but it's much less convenient.

## The activation snippets

### bash

```bash
# ~/.bashrc (interactive shells)
eval "$(mise activate bash)"
```

For login-shell-only environments (some Linux setups), also add:

```bash
# ~/.bash_profile
[[ -f ~/.bashrc ]] && source ~/.bashrc
```

### zsh

```zsh
# ~/.zshrc
eval "$(mise activate zsh)"
```

### fish

```fish
# ~/.config/fish/config.fish
mise activate fish | source
```

**Brew on macOS auto-activates fish.** If you installed via brew, you don't need to add anything to `config.fish`. Disable with `set -Ux MISE_FISH_AUTO_ACTIVATE 0` if you don't want this.

### nushell

```nu
# ~/.config/nushell/config.nu
mise activate nu | save -f /tmp/mise.nu
source /tmp/mise.nu
```

(Nushell's eval semantics require the file dance.)

### elvish

```elvish
# ~/.config/elvish/rc.elv
eval (mise activate elvish | slurp)
```

### xonsh

```python
# ~/.xonshrc
execx($(mise activate xonsh))
```

### PowerShell (Windows or pwsh on macOS/Linux)

```powershell
# $PROFILE
(&mise activate pwsh) | Out-String | Invoke-Expression
```

To find `$PROFILE`: run `$PROFILE` in pwsh. Create with `New-Item $PROFILE -Force` if it doesn't exist.

## Login vs interactive rc files

This trips people up:

| File | When it loads | Use for |
|---|---|---|
| `~/.bash_profile`, `~/.bash_login`, `~/.profile` | Login shells only (Linux: at login; macOS: every Terminal tab) | One-time-per-session setup |
| `~/.bashrc` | Interactive non-login shells (Linux: every new terminal; macOS: only if sourced from `.bash_profile`) | Aliases, prompts, mise activate |
| `~/.zshrc` | Interactive zsh | Same |
| `~/.zprofile` | Login zsh | Sometimes used for shims-only mode |

**On macOS, every Terminal tab is a login shell** — `.bash_profile` runs each time. On Linux, only the first SSH or graphical login.

The safe pattern: put `mise activate` in `~/.bashrc` / `~/.zshrc` (interactive), and source the rc from the profile if needed.

## Dual-mode pattern (interactive + IDE)

IDEs like VSCode and IntelliJ launch a non-interactive shell to run language servers. `mise activate` (the full version) requires interactive mode (it hooks into the prompt). For IDEs you typically want **shims**.

The dual-mode pattern: full activation interactively, shims in login (which IDEs read):

```zsh
# ~/.zprofile  — login shell, read by IDEs
eval "$(mise activate zsh --shims)"
```

```zsh
# ~/.zshrc  — interactive shell
eval "$(mise activate zsh)"
```

This gives you:
- Interactive terminals: full `mise activate` with `[env]` and hooks.
- IDEs: shims on PATH, no hooks/env (IDEs don't need them for language servers).

For fish:

```fish
# ~/.config/fish/config.fish
if status is-interactive
  mise activate fish | source
else
  mise activate fish --shims | source
end
```

## Why NOT just `--shims`

`mise activate --shims` puts the shims directory on PATH but **does not load `[env]` vars**, hooks, or watch_files. If you only have `--shims`, your project's `[env]` block does nothing in your shell.

So: full activation for daily use, shims for IDE integration only.

## Verifying activation

```sh
# 1. Confirm mise binary is on PATH
which mise

# 2. Confirm the shell function is defined (some shells)
type mise        # bash/zsh: should say "mise is a function"

# 3. Confirm hook-env runs
MISE_DEBUG=1 mise hook-env

# 4. cd into a project with mise.toml and verify env updates
cd /path/to/project
echo $MISE_LOADED  # set after first hook-env

# 5. Doctor
mise dr
```

If `mise dr` shows "mise activate not detected", the eval line isn't in your rc OR your shell isn't sourcing the rc.

## Common issues

| Symptom | Fix |
|---|---|
| `mise activate` not in rc but you added it | rc isn't being sourced — check login vs interactive |
| Added to `~/.zshrc` but VSCode terminal doesn't have mise | VSCode terminal might be a login shell — also add to `~/.zprofile` (shims is fine here) |
| Tools on PATH but `[env]` vars missing | You used `--shims` mode. Switch to full activation. |
| Slow shell prompt (>50ms) after adding mise | `MISE_DEBUG=1 mise hook-env` to see what's slow. Often a `_.source` script or large `mise ls`. |
| `mise hook-env` runs but PATH isn't updated | Another tool (direnv, nvm) is overwriting PATH after mise. Make mise activate LAST in the rc. |
| `bash: mise: command not found` after install | mise binary not on PATH yet. Add `export PATH="$HOME/.local/bin:$PATH"` BEFORE the eval line. |

## IDE-specific

| IDE | Best activation |
|---|---|
| **VSCode** | Use [hverlin/mise-vscode](https://marketplace.visualstudio.com/items?itemName=hverlin.mise-vscode) extension. Or shims in `.zprofile` + the `terminal.integrated.automationProfile.osx` setting. |
| **JetBrains** (IntelliJ, PyCharm, etc.) | Use [134130/intellij-mise](https://github.com/134130/intellij-mise) plugin. Or symlink `~/.local/share/mise` → `~/.asdf` for asdf-aware plugins. |
| **Neovim** | `vim.env.PATH = vim.env.HOME .. "/.local/share/mise/shims:" .. vim.env.PATH` in your config. Or use a mise plugin if one exists. |
| **Emacs** | [`mise.el`](https://github.com/eki3z/mise.el) — `(global-mise-mode)` |
| **Xcode** | `eval "$($HOME/.local/bin/mise activate -C $SRCROOT bash --shims)"` in build phase scripts. Add `$(SRCROOT)/mise.toml` to Input Files. |

Full IDE patterns are in the v0.3 `mise-vscode-integration`, `mise-jetbrains-integration`, and `mise-neovim-integration` skills.

## See also

- `/mise-activate-shell` command — automates this with detection + diff confirmation
- `mise-pathing-and-shims` — when each method (`activate`, `--shims`, `exec`, `env`) wins
- `mise-troubleshooting` — diagnostic flow for "mise not loading"
