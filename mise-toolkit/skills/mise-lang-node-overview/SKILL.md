---
name: mise-lang-node-overview
description: Node.js via mise — .nvmrc / .node-version / package.json engines auto-detection, LTS vs current, the corepack + packageManager field, and when to use the npm: backend for global CLIs. Use when setting up Node for a project or explaining how mise handles Node versions.
---

# Node.js via mise

Node has the most version-file formats of any language (`.nvmrc`, `.node-version`, `package.json#engines.node`, `.tool-versions`, `mise.toml`). mise handles all of them if you opt in, and normalizes the resolution order so there's one clear winner per project.

## Version resolution order

mise picks the Node version in this order (highest priority first):

1. `mise.toml` / `.mise.toml` `[tools] node` — explicit wins.
2. `mise.local.toml` (per-machine override, gitignored).
3. `.tool-versions` — asdf-compatible.
4. **Idiomatic version files**, opt-in via:
   ```toml
   [settings]
   idiomatic_version_file_enable_tools = ["node"]
   ```
   With that setting, mise reads `.nvmrc`, `.node-version`, and `package.json#engines.node`.

Without the opt-in, mise ignores the idiomatic files — this is deliberate. Silent reading of untracked files was deemed surprising.

## Pinning in `mise.toml`

```toml
[tools]
node = "24"           # major
node = "24.1"         # major.minor
node = "24.1.0"       # exact
node = "lts"          # latest LTS (resolves at install time)
node = "latest"       # avoid for team projects — moves when new releases land
```

**Team rule**: pin to at least major.minor. `"latest"` is fine for tinkering, terrible for reproducibility.

**LTS rule**: `"lts"` resolves to the current LTS major. Fine for long-lived services. For exact reproducibility, pin `"22"` (the major). Upgrading to a new LTS is then a deliberate commit.

## `package.json#engines` vs `mise.toml`

```json
{
  "name": "myapp",
  "engines": {
    "node": ">=22",
    "pnpm": ">=9"
  }
}
```

- **engines.node** is a *constraint* for consumers of your package (npm install warns if node version is off).
- **mise.toml node** is the *exact version* that mise installs.

They coexist: `engines.node: ">=22"` says "we require at least 22", `mise.toml node = "22.12"` says "this project uses 22.12 specifically". mise's idiomatic reader treats engines as a loose hint; the explicit `[tools]` line is authoritative.

## Corepack + `packageManager`

`packageManager` is the modern way to pin pnpm, yarn, or bun:

```json
{
  "packageManager": "pnpm@9.14.2"
}
```

With `corepack enable` (mise can do this via a task hook), Node auto-shims `pnpm` / `yarn` to the exact version in `packageManager`. You don't need to install pnpm via mise — corepack handles it.

Wire it in `mise.toml`:

```toml
[tools]
node = "24"

[hooks]
# Run corepack enable once after mise install, so the first `pnpm` invocation works.
enter = "corepack enable 2>/dev/null || true"
```

This is the cleanest pnpm/yarn pinning story. No `npm install -g pnpm` drift.

## `npm:` backend for global CLIs

mise has an `npm:` backend for installing npm packages as mise-managed tools:

```toml
[tools]
node = "24"
"npm:typescript" = "5.6"
"npm:prettier" = "3.4"
"npm:@anthropic-ai/claude-code" = "latest"
"npm:@google/gemini-cli" = "latest"
```

Benefits vs `npm install -g`:
- Version pinning via mise.lock.
- No PATH pollution from a shared global node_modules.
- Every dev gets the same version.

Trade-offs:
- Slightly slower first install (mise creates a per-tool prefix).
- Tools that expect other globally-installed tools to be present may need `PATH` fiddling.

Use `npm:` for: anything you'd otherwise `npm install -g`. Don't use it for project deps — those belong in `package.json`.

## Auto-detection gotchas

1. **`.nvmrc` with just a number** (`22`) — mise interprets as `22.x` latest. Exact matches like `v22.12.0` also work.
2. **`package.json#engines.node` with a range** (`">=22 <23"`) — mise picks the highest matching installed version, or the latest in the range if none installed. Can be surprising in CI.
3. **Multiple version files in the same dir** — idiomatic reader goes `.tool-versions` > `.nvmrc` > `.node-version` > `engines.node`. Don't mix them; pick one.
4. **`nvm use` in shell rc** — migrate to `mise activate` to avoid double-shimming. See `mise-migrate-from-nvm`.

## Common setups

### Single-app Node service

```toml
[tools]
node = "24"

[env]
NODE_ENV = { required = "dev or production or test" }

[tasks.dev]
run = "node --watch src/index.js"

[tasks.test]
run = "node --test"
```

### Monorepo with pnpm

```toml
[tools]
node = "24"

[hooks]
enter = "corepack enable 2>/dev/null || true"

[tasks.install]
run = "pnpm install --frozen-lockfile"
sources = ["package.json", "pnpm-lock.yaml", "packages/*/package.json"]

[tasks.build]
depends = ["install"]
run = "pnpm -r build"
```

### Global tools only (dotfiles pattern)

```toml
# ~/.config/mise/config.toml
[tools]
node = "lts"
"npm:@anthropic-ai/claude-code" = "latest"
"npm:prettier" = "latest"
"npm:typescript-language-server" = "latest"
```

## See also

- `mise-lang-node-packages` — npm vs pnpm vs yarn vs bun, corepack details.
- `mise-migrate-from-nvm` — moving off nvm.
- `mise-env-directives` — `[env]` depth.
- `mise-tool-versioning` — version pinning across all languages.
- mise docs: `mise.jdx.dev/lang/node.html`.
