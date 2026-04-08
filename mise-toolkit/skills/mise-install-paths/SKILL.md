---
name: mise-install-paths
description: Every way to install mise itself — curl/sh, brew, apt, dnf, pacman, snap, nix, winget, scoop, choco, MacPorts, source, Docker. Plus uninstall, upgrade, and the install paths each method uses. Use when installing mise on a new machine, recommending an install method, or troubleshooting "command not found" after install.
---

# Installing mise

mise can be installed many ways. The right one depends on platform, package manager, and whether you have admin/root.

## macOS

| Method | Command | Install path | Notes |
|---|---|---|---|
| **Homebrew** ⭐ | `brew install mise` | `/opt/homebrew/bin/mise` (Apple Silicon) or `/usr/local/bin/mise` (Intel) | Recommended. Auto-activates fish shell. |
| curl/sh | `curl https://mise.run \| sh` | `~/.local/bin/mise` | Works without brew |
| MacPorts | `sudo port install mise` | `/opt/local/bin/mise` | |

**Recommendation**: `brew install mise` if you have brew (most macOS devs do). Otherwise the curl-pipe-sh.

## Linux

### Debian / Ubuntu (apt)

The "official" apt repo:

```sh
sudo apt update -y && sudo apt install -y curl
sudo install -dm 755 /etc/apt/keyrings
curl -fSs https://mise.jdx.dev/gpg-key.pub | sudo tee /etc/apt/keyrings/mise-archive-keyring.asc 1> /dev/null
echo "deb [signed-by=/etc/apt/keyrings/mise-archive-keyring.asc] https://mise.jdx.dev/deb stable main" | sudo tee /etc/apt/sources.list.d/mise.list
sudo apt update -y
sudo apt install -y mise
```

Install path: `/usr/bin/mise`. Use this if you want apt to track upgrades.

### Fedora / RHEL / CentOS Stream (dnf, copr)

```sh
sudo dnf copr enable jdxcode/mise
sudo dnf install mise
```

Install path: `/usr/bin/mise`.

### Arch Linux

```sh
sudo pacman -S mise          # community repo
# or
yay -S mise-bin              # AUR (binary)
```

Install path: `/usr/bin/mise`.

### Snap (beta)

```sh
sudo snap install mise --classic --beta
```

### Universal (curl/sh)

```sh
curl https://mise.run | sh
```

Install path: `~/.local/bin/mise`. Works on any Linux distro. **Does not require root.** This is the safest universal fallback.

You can override with `MISE_INSTALL_PATH=/custom/path` or `MISE_VERSION=v...` for a specific version.

### Nix

```sh
nix-env -iA nixpkgs.mise
# or in flake.nix / shell.nix
```

## Windows

| Method | Command | Notes |
|---|---|---|
| **winget** ⭐ | `winget install jdx.mise` | Recommended |
| Scoop | `scoop install mise` | |
| Chocolatey | `choco install mise` | |

mise on Windows uses **shims** (no PATH manipulation hooks), so activation is different. Add `<homedir>\AppData\Local\mise\shims` to PATH. PowerShell users can `(&mise activate pwsh) | Out-String | Invoke-Expression` in their `$PROFILE`.

## Docker (no install on host)

If you don't want to install mise on your host at all, run it in a container:

```sh
docker run --rm -v "$PWD":/workspace -w /workspace jdxcode/mise mise install
```

(There's no official `jdxcode/mise` image as of writing — build your own from a slim base.)

## From source

```sh
git clone https://github.com/jdx/mise
cd mise
cargo build --release
cp target/release/mise ~/.local/bin/
```

For contributors. See `mise-contrib-overview` skill for the full dev setup.

## Bootstrap script (for repos)

If you don't want every developer to install mise themselves, generate a bootstrap script and commit it:

```sh
mise generate bootstrap -l -w
```

This creates `./bin/mise` (a script that downloads and runs mise) and updates `.gitignore`. New developers run `./bin/mise install` and they're set up. **Especially useful for CI** — no `curl ... | sh` in your workflow.

## Verifying the install

```sh
mise --version       # should print "mise 2026.x.x"
mise dr              # full health check
which mise           # confirm the path is what you expect
```

If `mise --version` works but `which mise` shows `/snap/bin/mise` when you wanted `/usr/bin/mise`, your PATH ordering is wrong. The first `mise` on PATH wins.

## Upgrading

| Install method | Upgrade command |
|---|---|
| curl/sh | `mise self-update` |
| brew | `brew upgrade mise` |
| apt | `sudo apt update && sudo apt upgrade mise` |
| dnf | `sudo dnf upgrade mise` |
| pacman | `sudo pacman -Syu mise` |
| winget | `winget upgrade jdx.mise` |
| scoop | `scoop update mise` |
| nix | `nix-env -u mise` |

`mise self-update` only works for installs that aren't managed by a package manager.

## Uninstalling

```sh
mise implode                       # remove ~/.local/share/mise (installs, plugins, caches)
# Then remove the binary the same way you installed it (brew uninstall, apt remove, etc.)
# Then remove `mise activate` from your shell rc file.
```

`mise implode` does NOT remove your `mise.toml` or `~/.config/mise/config.toml` — your configs are preserved.

## Common issues

- **`command not found: mise` after install**: the binary is at `~/.local/bin/mise` but `~/.local/bin` isn't on PATH. Add it (`export PATH="$HOME/.local/bin:$PATH"`) or use `mise activate` which handles it.
- **`mise --version` works but tools aren't on PATH**: you installed mise but didn't activate it. See `/mise-activate-shell` and `mise-shell-activation`.
- **Wrong version of mise on PATH**: multiple installs (e.g., snap + apt). `which -a mise` to see all of them, remove the wrong one.
- **PowerShell on Windows says scripts disabled**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- **WSL**: install mise inside WSL, not on Windows itself. Native Windows mise also works but uses shims (different mental model).

## See also

- `/mise-install` command — guided install with shell activation
- `mise-shell-activation` skill — what to add to your rc file after install
- `mise-host-vs-mise-tools` skill — what NOT to install with mise
- <https://mise.jdx.dev/installing-mise.html>
