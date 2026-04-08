---
name: mise-migrate-from-nvm
description: Migrating from nvm to mise — reading .nvmrc, translating `nvm use` shell hooks, tearing down ~/.nvm cleanly, and handling the common bashrc/zshrc entries. Use when a user is currently using nvm and wants to adopt mise without losing their pinned Node versions.
---

# Migrating from nvm to mise

`nvm` is the default Node version manager most developers start with. It works but has two common pain points: slow shell startup (it's a big shell function, sourced on every new terminal) and no support for any language other than Node. mise fixes both.

## The migration plan

1. **Inventory** what nvm is currently managing.
2. **Create a `mise.toml`** with the same Node version(s).
3. **Swap shell rc entries** from nvm's to mise's `mise activate`.
4. **Verify** `which node` and versions match.
5. **Uninstall nvm** (optional, recommended).

Don't do the uninstall step until after verifying mise is working — it's reversible but inconvenient.

## Step 1 — inventory nvm state

```sh
nvm ls                      # installed versions + current alias
cat ~/.nvm/alias/default    # default version (if aliased)
cat .nvmrc                  # project version (if present)
grep -r nvm ~/.zshrc ~/.bashrc ~/.bash_profile 2>/dev/null   # shell init
```

Note:
- The versions currently installed (you'll reinstall them via mise).
- The default version (the one that runs when no project sets one).
- Any `.nvmrc` files in active projects.
- The `nvm use` / `nvm install` commands in shell rc.

## Step 2 — create `mise.toml` per project

For each project that has a `.nvmrc`, create a `mise.toml`:

```toml
[tools]
node = "22.12.0"    # value from .nvmrc
```

Or, enable idiomatic reading so mise reads `.nvmrc` directly (no `mise.toml` needed):

```toml
# mise.toml — or ~/.config/mise/config.toml for global
[settings]
idiomatic_version_file_enable_tools = ["node"]
```

With the idiomatic reader, an existing `.nvmrc` just works.

For your **global default** (the version you get with no project config), edit `~/.config/mise/config.toml`:

```toml
[tools]
node = "lts"     # or the specific version you had as nvm default
```

## Step 3 — swap shell rc

Remove nvm's init:

```sh
# ~/.zshrc — DELETE these lines
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
```

Add mise's init:

```sh
# ~/.zshrc — ADD
eval "$(mise activate zsh)"
```

(For bash: `eval "$(mise activate bash)"` in `~/.bashrc` or `~/.bash_profile`.)

Restart the shell (`exec zsh` / `exec bash` / open a new terminal).

## Step 4 — verify

```sh
which node
# Should print something under ~/.local/share/mise/shims/ or ~/.local/share/mise/installs/

node --version
# Should print the version you set in mise.toml / global config

cd <project-with-.nvmrc>
node --version
# Should match the .nvmrc
```

If `which node` still points to `~/.nvm/...`, the old nvm shim is still on PATH. Check for leftover nvm init lines, and confirm `mise activate` is the last thing run in your shell rc (so its PATH prepend wins).

## Step 5 — uninstall nvm

Once mise is working reliably:

```sh
rm -rf "$HOME/.nvm"
unalias nvm 2>/dev/null
```

If you installed nvm via Homebrew: `brew uninstall nvm`.

Restart the shell. Run `which nvm` — should print "not found".

## Handling `nvm use` in scripts

If you have shell scripts or Makefiles with `nvm use` in them, replace with mise:

```sh
# Before
nvm use 22

# After — mise auto-activates from mise.toml / .nvmrc in the cwd, so usually nothing needed.
# If you need to force a version in a script:
mise use --pin node@22
```

The `mise.toml` in the project's working directory is read automatically when mise is activated. In most scripts, just deleting the `nvm use` line is enough.

## Handling `--install-latest` and friends

```sh
# nvm
nvm install --lts

# mise equivalent
mise use -g node@lts     # install + set as global default
```

## Common migration issues

### "Command not found: node" after removing nvm

You removed nvm but the shell still has the nvm version on PATH from before. Open a fresh terminal — the new shell has mise's shims instead.

### Version resolves to the wrong thing

Check `mise ls node` — does it list the version you expect? If not, `mise install node@<version>` first.

Then check `mise current` in the project dir — it shows which version is active and which config file set it.

### `.nvmrc` is ignored

Enable the idiomatic reader:

```toml
# ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ["node"]
```

Or, add `node = "<version>"` explicitly to `mise.toml`.

### Slow shell startup (it wasn't nvm?)

If removing nvm didn't speed up your shell, something else is slow. `time zsh -i -c exit` to measure; profile with `zsh -xv` to find the culprit. mise itself adds <20ms on a modern machine.

### Dev tools that shell out to nvm (e.g. certain VSCode extensions)

Find: extensions, tools, or scripts that call `nvm exec`. Replace `nvm exec` with `mise exec`:

```sh
# Before
nvm exec 22 npm run build

# After
mise exec node@22 -- npm run build
```

## Multiple Node versions installed simultaneously

mise supports multiple versions per tool:

```toml
[tools]
node = "24 22 20"    # three concurrent installs; first is default
```

Same as nvm's multi-install, just with one command to install them all (`mise install`).

## npm globals and package managers

### Globally-installed npm packages

If you had `npm install -g prettier` etc., they lived in nvm's per-version dirs. mise has the same isolation — you need to reinstall globals after migrating. Or, better, switch to mise's `npm:` backend:

```toml
[tools]
node = "24"
"npm:prettier" = "latest"
"npm:typescript" = "latest"
```

This gets you pinned, lockfile-tracked global CLIs.

### pnpm / yarn

If you installed pnpm/yarn via `npm install -g pnpm`, switch to corepack + `packageManager` (see `mise-lang-node-packages`).

## Rollback

If mise isn't working out for some reason (unlikely):

```sh
# Reinstall nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Remove mise activation from shell rc, restart shell.
```

Your `.nvmrc` files are still there — nothing was deleted.

## See also

- `mise-lang-node-overview` — Node version resolution in mise.
- `mise-lang-node-packages` — corepack + packageManager.
- `mise-shell-activation` — `mise activate` vs shims-on-PATH.
- `mise-migrate-from-asdf` — similar migration shape, for asdf users.
- mise docs: `mise.jdx.dev/faq.html#migrating-from-nvm`.
