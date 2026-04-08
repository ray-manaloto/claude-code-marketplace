---
name: mise-pathing-and-shims
description: When to use `mise activate` vs `mise activate --shims` vs `mise exec` vs `mise env` vs `mise en` vs `mise run` — what each does, what each loads, and what each can't. Use when the user is choosing between activation methods, or when something works in one mode but not another (especially "[env] vars not set in IDE").
---

# Activate vs shims vs exec vs env vs en vs run

mise has six ways to put tools on PATH and load env vars. They're NOT interchangeable. Each has trade-offs.

## The cheat sheet

| Method | How it works | Loads `[env]`? | Loads hooks? | watch_files? | Best for |
|---|---|---|---|---|---|
| **`mise activate`** | Shell prompt hook (`hook-env`) | ✅ | ✅ | ✅ | Interactive shells |
| **`mise activate --shims`** | Adds `~/.local/share/mise/shims` to PATH once | ❌ | ❌ | ❌ | IDEs, scripts, login shells |
| **`mise exec` / `mise x`** | Sets env, runs one command, exits | ✅ | ❌ | ❌ | One-off commands, scripts, CI |
| **`mise env`** | Prints env vars to eval | ✅ | ❌ | ❌ | Integration with other tools |
| **`mise en`** | Starts a sub-shell with env loaded | ✅ | ❌ | ❌ | Quick "throw me into a project shell" |
| **`mise run`** | Sets env, runs a task, exits | ✅ | ❌ | ❌ | Task execution from anywhere |

## Detailed differences

### `mise activate`

The full version. Hooks into your shell prompt, runs `mise hook-env` on every prompt display, updates PATH and env vars when you change directories or edit `mise.toml`.

```sh
eval "$(mise activate zsh)"   # in your ~/.zshrc
```

**Pros**:
- Full feature set: tools, env vars, hooks (`enter`/`leave`/`cd`/`postinstall`), `watch_files`.
- "Just works" — `cd` in, everything updates.
- ~5ms hook overhead per prompt (effectively unmeasurable).

**Cons**:
- Only works in interactive shells (needs a prompt).
- Not used by IDEs/language servers/cron/scripts.

### `mise activate --shims`

Lighter mode. Adds the shims directory to PATH and stops. Each shim is a wrapper script that re-invokes mise to figure out the right tool version.

```sh
eval "$(mise activate zsh --shims)"
```

**Pros**:
- Works in non-interactive shells (IDEs, scripts, login shells).
- No prompt hook = no per-prompt overhead.
- Each shim invocation is ~5-10ms (still fast).

**Cons**:
- ❌ **Does NOT load `[env]` variables.** This is the #1 confusion.
- ❌ Does NOT run hooks (`enter`/`leave`/etc.).
- ❌ Does NOT watch files.
- Each tool call costs ~10ms (vs 0ms with full activate).

**When to use**: IDEs that don't have a mise plugin. Scripts called from cron. Login shells where you want tools available without the prompt hook.

### `mise exec` / `mise x`

```sh
mise x -- node script.js
mise exec node@22 -- node -v
```

Reads the config, sets up env + PATH, runs the command, exits. No hooks. No watch_files. But `[env]` IS loaded.

**Pros**:
- Loads `[env]` (unlike shims).
- Works in scripts, CI, anywhere.
- Can override the tool version per-call: `mise x node@22 -- node -v`.

**Cons**:
- One-shot — env vars don't persist after the command.
- More typing than activated mode.

**When to use**: scripts, CI, one-off commands without changing your shell.

### `mise env`

```sh
eval "$(mise env)"            # bash/zsh
mise env --shell fish | source
```

Prints export commands for the current `mise.toml`. You eval them yourself.

**Pros**: integration with non-shell consumers (e.g., `mise env --json` for tools that read JSON).

**Cons**: doesn't update on directory change. Manual.

**When to use**: integration glue. Sometimes useful for one-off "set up a shell with this project's env".

### `mise en`

```sh
mise en                       # starts a sub-shell with env loaded
mise en /path/to/project      # for a specific project
```

Spawns a new shell with mise env active.

**Pros**: quick exploration without modifying your rc.

**Cons**: nested shell — exiting drops you back to the original.

**When to use**: "let me poke around in this project for a minute".

### `mise run`

```sh
mise run test
mise run build && mise run test
```

Loads env + tools, runs a defined task (from `[tasks]` or `mise-tasks/`), exits.

**Pros**: the canonical way to run project tasks. Handles task deps, parallelism, sources/outputs caching.

**Cons**: only runs *defined* tasks, not arbitrary commands.

**When to use**: anything you've defined as a task. Compose with `depends`/`depends_post`.

## The big confusion: `--shims` and `[env]`

If a user reports **"my `[env]` vars aren't set"**, the first thing to check is whether they're using `--shims` mode. Shims mode does **not** load `[env]`. To get env vars, they need:

1. Full `mise activate` (no `--shims`), OR
2. `mise exec` / `mise x` to wrap the command, OR
3. `mise run` for tasks

The shims-only IDE pattern is fine for tool versions but won't load `[env]`. If your tools need env vars, use a mise IDE plugin (which talks to mise directly) or wrap your run/debug command in `mise x`.

## The dual-mode pattern (recommended)

Most teams want both: full activation interactively, shims for IDEs.

```zsh
# ~/.zprofile (login → IDEs read this)
eval "$(mise activate zsh --shims)"

# ~/.zshrc (interactive)
eval "$(mise activate zsh)"
```

Now:
- Open a terminal: full mise activation, env vars work.
- Open VSCode: VSCode launches a login shell, gets shims on PATH, language servers find tools but don't have `[env]`.
- VSCode integrated terminal: when you open a terminal in VSCode, it sources `.zshrc` AND `.zprofile`, getting full activation.

## Common pitfall: order of activation lines

If you have multiple PATH manipulators in your rc (mise, nvm, pyenv, direnv, brew shellenv), **order matters**. The LAST one wins for PATH.

Recommended order:

```zsh
# 1. brew shellenv (if you use brew)
eval "$(/opt/homebrew/bin/brew shellenv)"

# 2. anything else that touches PATH

# 3. mise activate LAST so it wins
eval "$(mise activate zsh)"
```

If mise loses to nvm, you'll see `~/.nvm/versions/node/...` instead of `~/.local/share/mise/installs/node/...` in `which node`.

## Performance

| Method | Overhead |
|---|---|
| `mise activate` | ~5ms per prompt (hook-env exits early if nothing changed) |
| `mise activate --shims` | ~10ms per tool invocation |
| `mise exec` | ~30-50ms per call (loads config + sets up env) |
| `mise run` | Same as exec, plus task overhead |

For comparison, asdf shims add ~120ms per tool invocation. mise's shims are an order of magnitude faster.

## See also

- `mise-shell-activation` — the actual snippets per shell
- `/mise-activate-shell` command
- `mise-overview` — the FAQ table this skill expands on
- <https://mise.jdx.dev/dev-tools/shims.html>
