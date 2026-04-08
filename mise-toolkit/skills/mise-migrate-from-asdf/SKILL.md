---
name: mise-migrate-from-asdf
description: Migrating a project from asdf to mise — preserving .tool-versions, plugin compatibility, the global config gotcha, asdf-go vs asdf-bash differences, and the recommended deprecation steps. Use when the user mentions "migrate from asdf", "switch from asdf", or has a .tool-versions file they want to convert.
---

# Migrating from asdf to mise

The good news: **mise is highly asdf-compatible.** It reads `.tool-versions` natively, can use asdf plugins via the `asdf:` backend, and accepts asdf-style command syntax in many places.

The not-so-good news: full compatibility is no longer a design goal. There are a few specific gotchas.

## TL;DR migration

```sh
# 1. Install mise
curl https://mise.run | sh

# 2. Activate mise in your shell rc (and remove asdf from it)
echo 'eval "$(mise activate zsh)"' >> ~/.zshrc   # or bash/fish equivalent

# 3. In any project directory with .tool-versions, just run:
mise install

# 4. (Optional) Migrate global ~/.tool-versions to mise's global config
mv ~/.tool-versions ~/.tool-versions.bak
cat ~/.tool-versions.bak | tr -s ' ' | tr ' ' '@' | xargs -n2 mise use -g
```

That's it for most users. mise reads `.tool-versions` directly — no conversion required for project-level pins.

## Critical gotcha: `~/.tool-versions` is NOT global

asdf treats `~/.tool-versions` as the user's global tool-versions file. **mise does not.** mise's global config is `~/.config/mise/config.toml`. If you had a `~/.tool-versions` setting node 20 globally, mise won't pick it up.

The migration script above (step 4) handles this — it converts each line to a `mise use -g` call.

## asdf-bash vs asdf-go (0.16+)

asdf was rewritten in Go starting 0.16. mise was designed against asdf-bash (≤ 0.15) and is **more compatible with asdf-bash than asdf-go is** — ironic but true.

The biggest break: asdf-go got rid of `asdf global|local` in favor of `asdf set`. mise has its own `mise set` (which sets env vars, not tool versions), so this command is **incompatible**. If you're coming from asdf-go and have muscle memory for `asdf set`, retrain to:

```sh
mise use node@20      # writes to nearest mise.toml
mise use -g node@20   # writes to global config
```

## Plugin compatibility

asdf plugins work via the `asdf:` backend in mise:

```sh
mise plugin install <name> https://github.com/<user>/asdf-<name>
```

But: **new asdf plugins are no longer accepted into the mise registry** (supply-chain reasons — they execute arbitrary bash). For new tools, look for an `aqua:` or `github:` equivalent first.

mise inherits asdf's [plugin registry](https://github.com/mise-plugins/registry) for shorthand resolution. So `mise plugin install elixir` still works for existing plugins.

## `mise.toml` vs `.tool-versions` side-by-side

You can keep both. `mise.toml` `[tools]` overrides `.tool-versions` in the same directory. This lets you ease into mise without breaking teammates who still use asdf:

```
~/proj/
  ├── .tool-versions        # asdf reads this
  └── mise.toml             # mise reads this AND .tool-versions
```

When you're ready to drop `.tool-versions`, run `mise use --pin node@20` (the `--pin` flag emits asdf-compatible exact versions).

## Asdf-style command syntax

mise supports asdf-style invocations (positional, no `@`) in most places:

```sh
mise install node 20.0.0     # works
mise install node@20.0.0     # also works (preferred)
mise local node 20.0.0       # works
mise use node@20.0.0         # preferred
```

mise's preferred style uses `@` because it allows multiple tools per command:

```sh
mise use node@20 python@3.12 go@1.22
```

## What to remove from your setup

Once mise is working:

1. **Remove asdf from shell rc** — comment out `. $HOME/.asdf/asdf.sh` and any `fpath` additions.
2. **Restart your shell.**
3. **Verify** `which node` (or whatever) points into `~/.local/share/mise/installs/...`, not `~/.asdf/...`.
4. **Optional**: [uninstall asdf](https://asdf-vm.com/manage/core.html#uninstall) once you're confident.

## What to leave alone

- **`.tool-versions` files in projects** — mise reads them. Drop them only when your team has fully migrated.
- **asdf plugins you depend on** — they work via the `asdf:` backend. Replace with `aqua:`/`github:` equivalents over time, but no rush.
- **CI** — switch to `jdx/mise-action@v3` (it's a drop-in for `asdf-vm/actions/install`).

## What mise gives you that asdf doesn't

These are NOT in asdf — make sure your team knows about them when you migrate:

- **`[env]` block** — replaces direnv for project env vars
- **`[tasks]` block** — task runner with deps, parallelism, sources/outputs caching
- **`mise.lock`** — reproducible exact-version lockfile with checksums
- **Aqua + native provenance verification** (cosign / SLSA / minisign / GitHub attestations)
- **`mise upgrade --bump`** — atomic version bumps that update both config and lockfile
- **`mise mcp`** — Model Context Protocol server for AI assistants
- **`mise generate {bootstrap,github-action,devcontainer,git-pre-commit}`** — scaffolding generators

## See also

- `mise-overview` — full mental model
- `mise-toml-anatomy` — beyond `.tool-versions`
- `mise-lockfile` — the reproducibility upgrade
- `mise-backends-overview` — what to pick instead of asdf plugins
- <https://mise.jdx.dev/dev-tools/comparison-to-asdf.html>
- <https://mise.jdx.dev/faq.html#how-do-i-migrate-from-asdf>
