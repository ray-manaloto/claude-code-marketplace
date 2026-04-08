---
description: Detect the user's shell and add `mise activate` to their shell rc file
---

Add the `mise activate` line to the user's shell rc file so mise loads automatically in new sessions.

## Steps

1. **Detect the shell**:
   ```bash
   echo $SHELL
   basename "$SHELL"
   ```
   Also check if the user's *default* shell (from `dscl . -read /Users/$USER UserShell` on macOS or `getent passwd $USER` on Linux) differs from the current shell — that matters for IDE integration.

2. **Verify mise is installed**:
   ```bash
   command -v mise || ls ~/.local/bin/mise
   ```
   If not installed, stop and tell the user to run `/mise-install` first.

3. **Find the rc file**:

   | Shell | Default rc file | Notes |
   |---|---|---|
   | bash | `~/.bashrc` | macOS users may need `~/.bash_profile` for login shells |
   | zsh | `~/.zshrc` | Use `~/.zprofile` for shims-only IDE-friendly mode |
   | fish | `~/.config/fish/config.fish` | Brew installs auto-activate; check first |
   | nushell | `~/.config/nushell/config.nu` | |
   | elvish | `~/.config/elvish/rc.elv` | |
   | xonsh | `~/.xonshrc` | |
   | pwsh (Windows) | `$PROFILE` (run `$PROFILE` in pwsh) | Create with `New-Item $PROFILE -Force` if missing |

4. **Check if activation is already present**:
   ```bash
   grep -F 'mise activate' "$rc_file"
   ```
   If yes → confirm it works and stop. If it points at a wrong path (e.g., `~/.local/bin/mise` doesn't exist), offer to fix.

5. **Show the proposed addition** as a diff:
   ```diff
   + # mise activate (added by mise-toolkit)
   + eval "$(mise activate zsh)"
   ```
   Get confirmation before editing.

6. **Edit the rc file**: append the line. Use Edit, not Bash with `>>`, so the user sees the change.

7. **Verify**: tell the user to run `exec $SHELL` (or open a new terminal), then run `mise dr` to verify activation works. Confirm `which mise` shows the binary and `type mise` shows the shell function (if applicable).

## Special cases

- **Brew + fish on macOS**: mise auto-activates via `vendor_conf.d`. Don't add a line — just verify it's working.
- **VSCode terminal not loading the rc file**: on macOS, add `terminal.integrated.automationProfile.osx` to VSCode settings (see `mise-vscode-integration` skill).
- **IDE wants shims, shell wants full activation**: use the dual-mode pattern in `~/.zprofile` (shims) + `~/.zshrc` (interactive activate). See `mise-shell-activation` skill.
- **Activation line already there but pointing at the wrong mise binary**: offer to fix the path.
- **Shell isn't in `/etc/shells`**: tell the user to add it before `chsh -s`.

## What you avoid

- Editing the rc file without showing the diff.
- Adding the line if it's already there.
- Recommending `/bin/bash` on macOS (it's bash 3.x — too old; use zsh or homebrew bash).
- Skipping the verification step.

## See also

- `mise-shell-activation` skill — every shell + IDE permutation
- `mise-pathing-and-shims` skill — when to use `--shims` mode
- `mise-install` command — runs activation as part of install
