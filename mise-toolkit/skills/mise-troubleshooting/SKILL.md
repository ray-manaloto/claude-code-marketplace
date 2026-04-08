---
name: mise-troubleshooting
description: Diagnostic flowchart for common mise problems — tool not found, wrong version, env vars missing, slow shell, trust issues, install failures, GitHub rate limits, IDE not seeing tools, mise.toml not loaded. Use as the first stop when something is broken; routes to more specific skills/agents based on the symptom.
---

# Troubleshooting mise

A symptom-first guide. Find your symptom, follow the flow.

## "command not found: mise"

| Cause | Fix |
|---|---|
| Not installed | `/mise-install` |
| Installed but `~/.local/bin` not on PATH | `export PATH="$HOME/.local/bin:$PATH"` (then add to rc) |
| Multiple installs (snap + apt) | `which -a mise` to see all; remove the wrong one |
| Brew shell hasn't been re-sourced | `exec $SHELL` |

## "command not found: <tool>" (for a tool you pinned in mise.toml)

```
which mise → mise dr → mise cfg ls → mise current → which node
```

| `mise dr` says... | Cause | Fix |
|---|---|---|
| "untrusted config" | Trust prompt was denied | `/mise-trust-fix` or `mise trust` |
| "missing tools" | Tools pinned but not installed | `mise install` |
| "mise activate not detected" | Activation missing from rc | `/mise-activate-shell` |
| "no problems" but still broken | Activation in rc but not loaded | `exec $SHELL` or open new terminal |

If `which node` shows a path NOT under `~/.local/share/mise/installs/`, another version manager (nvm, brew, asdf) is winning the PATH race. Move `mise activate` to be the LAST line in your rc.

## "wrong version of <tool>"

```
mise current → mise cfg ls → mise ls --current
```

The wrong version is being resolved by some config file you didn't expect. `mise cfg ls` shows the precedence order. Likely culprits:

| Cause | Fix |
|---|---|
| `mise.local.toml` overriding `mise.toml` | `mise use --path mise.toml <tool>@<version>` to fix |
| Parent directory's `mise.toml` | Add an explicit pin in your project's `mise.toml` |
| `MISE_<TOOL>_VERSION` env var | `unset MISE_<TOOL>_VERSION` |
| Env-specific config (`mise.production.toml`) loaded via `MISE_ENV` | Check `MISE_ENV`; unset if not intended |
| Idiomatic file (`.nvmrc` etc.) | These are OPT-IN — only read if `idiomatic_version_file_enable_tools` includes the tool. If you don't want it read, don't enable it. |

## "[env] vars not loaded"

| Cause | Fix |
|---|---|
| Using `mise activate --shims` | Switch to full `mise activate` (shims don't load `[env]`) |
| Not using `mise activate` at all | `/mise-activate-shell` |
| `_.file = ".env"` and the .env doesn't exist or path is wrong | `_.file` resolves against `config_root`, not cwd. Use `{{config_root}}/.env` or move the file. |
| `tools = true` directive needs tools resolved first | Make sure the referenced tool is in `[tools]` |
| `required = true` var missing | Set the var (in shell, in `mise.local.toml`, or in CI secrets) |

## "mise.toml not loaded at all"

```
mise cfg ls
```

If your file isn't in the list:

| Cause | Fix |
|---|---|
| Filename wrong | Must be one of: `mise.toml`, `.mise.toml`, `mise.local.toml`, `mise/config.toml`, `.mise/config.toml`, `.config/mise.toml`, `.config/mise/config.toml` |
| Untrusted | `mise dr` will say so; `mise trust` |
| Above `MISE_CEILING_PATHS` | mise stops walking up at the ceiling. Check `mise settings get ceiling_paths`. |
| Symlinked (e.g., GNU Stow) | `mise trust` the actual file path, not the symlink |
| In `~/.local/state/mise/ignored-configs/` | Accidentally denied trust. Remove the symlink there. |

## "slow shell prompt after adding mise"

Normal mise hook overhead is ~5ms. If it's noticeably slow:

```sh
MISE_DEBUG=1 mise hook-env
```

| Symptom | Cause | Fix |
|---|---|---|
| `_.source` script is slow | Sourcing a heavy bash script | Make it lazy or move logic into a task |
| Many `[[watch_files]]` entries | Each one walks the filesystem | Reduce or scope patterns tighter |
| `tools = true` causing 2-pass eval | Lazy eval | Drop `tools = true` if not needed |
| Slow plugin (asdf/vfox) loading | Plugin bash code | Switch to aqua/github backend if available |

## "tool failed to install"

```
MISE_DEBUG=1 mise install <tool>
```

| Error | Cause | Fix |
|---|---|---|
| `cannot find -lz` / `openssl/ssl.h: No such file` | Missing system libs | `apt install build-essential libssl-dev libffi-dev libsqlite3-dev liblzma-dev` (see `mise-host-vs-mise-tools`) |
| `gcc: command not found` | No compiler | macOS: `xcode-select --install`; Linux: `apt install build-essential` |
| `403 rate limit exceeded` | GitHub API rate limit | Set `MISE_GITHUB_TOKEN=$GITHUB_TOKEN` |
| Checksum mismatch | Lockfile checksum stale or upstream artifact changed | `mise uninstall <tool>@<v>` then `mise install` |
| `404 not found` for a version | Version doesn't exist upstream | `mise ls-remote <tool>` to see what's available |
| Plugin install fails | asdf plugin bash error | Look at the plugin's GitHub issues; consider switching backend |

## "github rate limit / 403 / 404 from mise"

```sh
mise settings get github_token         # is it set?
echo $MISE_GITHUB_TOKEN
echo $GITHUB_TOKEN
```

mise reads (in order): `MISE_GITHUB_TOKEN` → `GITHUB_TOKEN` → unauthenticated. Unauth rate limit is 60/hour per IP. Authenticated is 5000/hour.

Fix: set `MISE_GITHUB_TOKEN` in your shell or `~/.config/mise/config.toml`. In CI, use `secrets.GITHUB_TOKEN`.

Better long-term fix: run `mise lock` and commit `mise.lock`. Once URLs are in the lockfile, mise doesn't need to call the API.

## "IDE doesn't see mise tools"

| IDE | Fix |
|---|---|
| **VSCode** | Install [hverlin/mise-vscode](https://marketplace.visualstudio.com/items?itemName=hverlin.mise-vscode), OR add shims to PATH via `~/.zprofile` (which VSCode reads on macOS via `terminal.integrated.automationProfile.osx`) |
| **JetBrains** | Install [134130/intellij-mise](https://github.com/134130/intellij-mise), OR symlink `~/.local/share/mise` → `~/.asdf` |
| **Neovim** | Add shims to PATH in your config: `vim.env.PATH = vim.env.HOME .. "/.local/share/mise/shims:" .. vim.env.PATH` |
| **Xcode** | `eval "$($HOME/.local/bin/mise activate -C $SRCROOT bash --shims)"` in build script. Add `$(SRCROOT)/mise.toml` to Input Files. |

## "mise activate works in terminal but not in script"

`mise activate` requires an interactive shell (it hooks the prompt). For scripts:

| Approach | Use |
|---|---|
| `mise x -- <command>` | One-off |
| `mise activate --shims` in `~/.zprofile` | Login shells get shims, scripts work |
| `eval "$(mise env)"` at script start | Manual env load |

## "tasks don't see [env] vars"

Task `env` and `[env]` are merged at run time. If a task can't see a var:

```sh
mise tasks info <task-name>           # see what env mise thinks the task has
mise env --redacted                   # see what mise is exporting overall
```

If you set `raw = true` on a task, redactions are bypassed and output capture is disabled. That's intentional but can mask issues.

## "trust prompts in CI"

In non-interactive shells, mise **silently skips untrusted configs**. CI runs that don't set up trust will silently use no mise config.

Fix:

```yaml
# Either set the env var
- run: mise install
  env:
    MISE_TRUSTED_CONFIG_PATHS: ${{ github.workspace }}

# Or trust explicitly
- run: |
    mise trust
    mise install
```

`jdx/mise-action@v3` handles this for you.

## "monorepo trust prompts on every subdirectory"

```toml
# Root mise.toml
experimental_monorepo_root = true
```

Then `mise trust` the root once. All descendant configs are implicitly trusted. Requires `MISE_EXPERIMENTAL=1`.

## When you've tried everything

```sh
mise dr                              # exhaustive diagnostic
MISE_DEBUG=1 mise hook-env          # see exactly what's happening
mise cfg ls                          # see what mise is reading
```

Then try:

1. Delegate to the **`mise-config-doctor`** agent — interactive diagnosis with the mise MCP server.
2. Open an issue on `github.com/jdx/mise/issues` with the full debug output.
3. Ask in the [Discord](https://discord.gg/UBa7pJUN7Z) — jdx and the community are responsive.

As a last resort:

```sh
/mise-reset-safe                    # safely reset to clean state
```

## See also

- `/mise-doctor`, `/mise-verify`, `/mise-trust-fix` commands
- `mise-config-doctor` agent
- `mise-host-vs-mise-tools` skill
- `mise-pathing-and-shims` skill
- `mise.jdx.dev/faq.html`
