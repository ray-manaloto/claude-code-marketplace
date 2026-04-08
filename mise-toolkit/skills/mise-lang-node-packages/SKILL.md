---
name: mise-lang-node-packages
description: Node package managers — npm vs pnpm vs yarn vs bun. Why corepack + the packageManager field is the right pinning answer, when to use mise's npm: backend for global CLIs vs project-local deps, and the monorepo story. Use when picking a Node package manager or explaining corepack.
---

# Node package managers — the decision matrix

Node has four mainstream package managers: npm, pnpm, yarn, and bun. All four work with any `package.json`. The right choice is mostly about your workflow, not technical capability.

## The four contenders

| Manager | Speed | Disk usage | Monorepo | Lockfile | Default in… |
|---|---|---|---|---|---|
| **npm** | 🥉 baseline | heavy (duplication) | workspaces (ok) | `package-lock.json` | ships with Node |
| **pnpm** | 🥇 fastest | 🥇 content-addressed store | 🥇 built-in workspaces | `pnpm-lock.yaml` | — |
| **yarn** (berry) | 🥈 fast | medium | 🥈 workspaces + PnP | `yarn.lock` | — |
| **bun** | 🥇🥇 fastest | medium | workspaces | `bun.lockb` (binary) | — |

## The pick

- **Default for new projects**: **pnpm**. Fastest install, strictest dep resolution (catches phantom deps), best monorepo story. Used by every large JS project that's switched in the last 3 years.
- **Corporate / "we use npm because that's what ships"**: **npm**. Fine. It's improved a lot.
- **Long-lived yarn codebases**: **yarn berry (v4+)**. Don't migrate away just for the sake of it; the cost is rarely worth it.
- **Bun curious**: **bun** for personal projects and greenfield. It's fast and increasingly capable but still has compatibility edges. Verify your deps work before committing a team to it.

Never mix two package managers in one project — pick one lockfile and commit only that.

## The pinning story — corepack + `packageManager`

Since Node 16.9, `corepack` ships with Node. It reads `packageManager` from `package.json` and shims `pnpm` / `yarn` / `npm` to the exact version specified:

```json
{
  "packageManager": "pnpm@9.14.2"
}
```

With `corepack enable` run once, typing `pnpm install` in the project directory runs pnpm 9.14.2 specifically. No `npm install -g pnpm`. No drift. No "what version is on CI vs dev".

This is **the** way to pin package managers as of 2026. Use it.

### Wiring corepack via mise

```toml
[tools]
node = "24"

[hooks]
enter = "corepack enable 2>/dev/null || true"
```

`[hooks] enter` runs when mise activates the directory — once per shell session entering the dir. `corepack enable` is idempotent, so running it on every enter is safe. The `|| true` prevents a stale corepack install from breaking the hook.

## When to use mise's `npm:` backend

mise has an `npm:` backend for installing npm packages as **global CLIs** managed by mise:

```toml
[tools]
node = "24"
"npm:typescript" = "5.6"
"npm:prettier" = "3.4"
"npm:@anthropic-ai/claude-code" = "latest"
"npm:vercel" = "latest"
```

**Use `npm:` for**:
- Global CLIs you'd otherwise `npm install -g`.
- Tools shared across many projects (claude-code, vercel, netlify-cli).
- Dotfiles config (`~/.config/mise/config.toml`).

**Don't use `npm:` for**:
- Project dependencies — those go in `package.json`.
- Tools that need to integrate with the project's node_modules (e.g. a linter plugin that depends on eslint from the project) — the mise-installed copy lives in a separate prefix and won't see project modules.

## Monorepos

### pnpm workspaces (recommended)

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```toml
# mise.toml
[tools]
node = "24"

[hooks]
enter = "corepack enable 2>/dev/null || true"

[tasks.install]
run = "pnpm install --frozen-lockfile"
sources = ["package.json", "pnpm-lock.yaml", "pnpm-workspace.yaml", "packages/*/package.json", "apps/*/package.json"]

[tasks.build]
depends = ["install"]
run = "pnpm -r build"

[tasks.test]
depends = ["build"]
run = "pnpm -r test"

[tasks."dev:web"]
run = "pnpm --filter @myorg/web dev"
```

### npm workspaces

```json
{
  "workspaces": ["packages/*", "apps/*"]
}
```

Works, but slower than pnpm and lacks the strict isolation.

### yarn berry workspaces

`yarn workspaces` with PnP is the strictest option but has the most compatibility quirks. Usually a legacy situation — rarely a greenfield choice.

## Lockfile hygiene

- **Commit the lockfile.** Always. It's the whole point.
- **Don't commit `node_modules/`.** Obvious but still common in old projects.
- **`--frozen-lockfile` in CI** — fail if the lockfile would change. pnpm: `--frozen-lockfile`. npm: `npm ci`. yarn: `--immutable`.
- **When upgrading a dep, run the package manager, not a manual lockfile edit.** Editing lockfiles by hand is a forbidden dark art.

## Anti-patterns

- **`npm install -g pnpm`** when you could use corepack.
- **Committing `node_modules/` to "speed up CI"** — no.
- **Mixing `npm install` and `pnpm install`** in the same project.
- **Using `bun install` on a project with a pnpm lockfile** just to "try bun" — reverts silently.
- **Mise-installing a package manager that corepack could handle** (`"npm:pnpm" = "9.14.2"`) — corepack is better.
- **Ignoring `engines`** — at least set it as a compat floor for consumers of your package.

## See also

- `mise-lang-node-overview` — Node version resolution and idiomatic files.
- `mise-tasks-toml` — `sources` and `outputs` for incremental task runs.
- `mise-env-directives` — `[hooks] enter` depth.
- corepack docs: `github.com/nodejs/corepack`.
- pnpm docs: `pnpm.io`.
