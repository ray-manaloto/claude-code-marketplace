---
description: Install mise on the user's host system (cross-platform installer with shell activation)
disable-model-invocation: true
---

Install mise on the user's host. This command modifies the host system, so it is **user-invoked only** — Claude cannot trigger it autonomously.

## Steps

1. **Detect the environment**:
   - OS: `uname -s` (Darwin, Linux) or `$OS` (Windows)
   - Architecture: `uname -m`
   - Shell: `echo $SHELL` and `basename "$SHELL"`
   - Whether mise is already installed: `command -v mise && mise --version`

2. **If mise is already installed**: report the version, the install path, and whether it's activated in the user's shell rc. Stop unless the user explicitly asks to reinstall.

3. **Otherwise, pick the install method** based on platform. Prefer in this order:

   | Platform | Preferred install |
   |---|---|
   | macOS | `brew install mise` (if brew is present) → else `curl https://mise.run \| sh` |
   | Debian/Ubuntu | apt repo (see `mise-install-paths` skill for the exact 6-line setup) |
   | Fedora/RHEL | `dnf copr enable jdxcode/mise && dnf install mise` |
   | Arch | `pacman -S mise` (community repo) |
   | Linux generic | `curl https://mise.run \| sh` |
   | Windows | `winget install jdx.mise` → else `scoop install mise` → else `choco install mise` |
   | Nix | `nix-env -iA nixpkgs.mise` |

   Show the chosen command to the user. **Get confirmation before running.**

4. **Run the install** using Bash. Capture output. If it fails, fall back to `curl https://mise.run | sh`.

5. **Verify**: run `~/.local/bin/mise --version` (or the install path) and confirm it works.

6. **Activate in shell rc**: detect the user's shell, then propose adding the activation line to the appropriate rc file:

   | Shell | rc file | Line |
   |---|---|---|
   | bash | `~/.bashrc` | `eval "$(~/.local/bin/mise activate bash)"` |
   | zsh | `~/.zshrc` | `eval "$(~/.local/bin/mise activate zsh)"` |
   | fish | `~/.config/fish/config.fish` | `~/.local/bin/mise activate fish \| source` |
   | nu | `~/.config/nushell/config.nu` | (see `mise-shell-activation` skill) |
   | pwsh | `$PROFILE` | `(&mise activate pwsh) \| Out-String \| Invoke-Expression` |

   Show the diff and ask before editing the rc file.

7. **Restart shell** instructions: tell the user to `exec $SHELL` or open a new terminal.

8. **Run `mise dr`** to verify activation worked. Report any warnings.

9. **Suggest next steps**: `/mise-quickref` for a CLI cheat sheet, `/mise-init` to scaffold their first project's `mise.toml`, `/mise-explain` if they want the elevator pitch.

## What you avoid

- Modifying the user's shell rc without showing the diff.
- Skipping the verification step.
- Installing mise as root unless on a system where that's expected (e.g., system-wide install on a server you've been told is yours).
- Running on a managed/locked-down system without flagging it (corporate Mac with restricted brew, etc.).
- `curl ... | sudo sh` — never. mise installs to `~/.local/bin` by default and doesn't need root.

## See also

- `mise-install-paths` skill — every install method in detail
- `mise-shell-activation` skill — every shell's activation snippet
- `mise-host-prerequisites` (v0.3) — what system packages mise expects
