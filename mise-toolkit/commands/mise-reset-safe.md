---
description: Safely reset mise state — uninstall tools but preserve configs and lockfiles
disable-model-invocation: true
---

Reset mise state in a recoverable way. **User-invoked only** (Claude cannot trigger autonomously) because this removes installed software.

## Three reset levels

### Level 1: Cache only (lowest risk)

```sh
mise cache clear
```

Just clears mise's cache. Safe — re-fetches version lists / metadata next time.

### Level 2: Tool installs (medium risk)

Removes installed tool binaries but preserves `mise.toml`, `mise.lock`, settings, and the install registry. Re-running `mise install` reinstalls everything from the lockfile.

```sh
# Per-tool
mise uninstall node@22 python@3.12

# Or all installed versions of all tools
mise uninstall --all
```

After this, `mise install` rebuilds everything (slow but deterministic).

### Level 3: Nuclear (highest risk)

```sh
mise implode
```

Removes the entire `~/.local/share/mise` directory: installs, plugins, caches, downloads. Does **not** touch:
- `~/.config/mise/config.toml` (global config)
- Project `mise.toml` files
- `~/.local/share/mise-data` if it was relocated

This is "I want to start over with a clean slate but keep my configs". After running, re-install mise itself with `/mise-install` and run `mise install` in each project.

## What this command does

1. **Confirm the level**: ask the user which level they want. Show what each one removes and what it preserves.
2. **Show the current state** before doing anything: `mise ls`, disk usage of `~/.local/share/mise`.
3. **Run the chosen reset** with confirmation.
4. **Verify**: show the post-reset state and any errors.
5. **Recovery instructions**: tell the user how to get back to working — `mise install` for level 2, `/mise-install` + `mise install` for level 3.

## What you avoid

- Running level 3 without explicit confirmation, even with `disable-model-invocation`.
- `rm -rf ~/.local/share/mise` instead of `mise implode` (the implode command handles edge cases like Windows shim mode and lockfile state).
- Removing `~/.config/mise/config.toml` (the user's settings).
- Removing the user's project `mise.toml` files.
- Recommending this when the actual problem is something else (use `mise-config-doctor` agent first).
