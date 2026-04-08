---
name: mise-cookbook-node-nextjs
description: End-to-end recipe for a Next.js app managed by mise — Node + pnpm (via corepack) + TypeScript + Prettier + ESLint + Playwright. Complete mise.toml template, first-run walkthrough, and common gotchas. Use when starting a new Next.js app or adding mise to an existing one.
---

# Cookbook — Next.js app (Node + pnpm)

A complete starting point for a Next.js 14+ app using mise. Node is pinned; pnpm is pinned via `packageManager` and managed by corepack; TypeScript, ESLint, Prettier, and Playwright are all wired through one `mise.toml`.

## Who this is for

- Starting a new Next.js (App Router) app.
- Adding mise to an existing Next.js project currently using nvm + `npm install -g pnpm`.
- Onboarding contributors who need "clone → `mise install` → `mise run dev`" to just work.

## Who this isn't for

- Vite / Remix / Astro — the pattern transfers but specifics differ; start from `mise-lang-node-overview`.
- SSR-free static sites — Next.js is overkill; use Astro or plain Vite.

## The `mise.toml`

```toml
min_version = '2026.4.0'

[tools]
node = "24"

[hooks]
# corepack shims pnpm/yarn from the packageManager field in package.json
enter = "corepack enable 2>/dev/null || true"

[env]
NODE_ENV = { required = "development or production or test" }

[tasks.install]
description = "Install deps (frozen lockfile)"
run = "pnpm install --frozen-lockfile"
sources = ["package.json", "pnpm-lock.yaml"]

[tasks.dev]
description = "Run Next.js dev server"
depends = ["install"]
run = "pnpm dev"

[tasks.build]
description = "Build for production"
depends = ["install"]
run = "pnpm build"
sources = ["**/*.{ts,tsx,js,jsx,css,md}", "next.config.*", "package.json"]
outputs = [".next/"]

[tasks.start]
description = "Run the production build"
depends = ["build"]
run = "pnpm start"

[tasks.test]
description = "Run Playwright e2e tests"
depends = ["install"]
run = "pnpm exec playwright test"

[tasks.lint]
description = "Lint with Next's built-in ESLint config"
depends = ["install"]
run = "pnpm lint"

[tasks.fmt]
description = "Format with Prettier"
depends = ["install"]
run = "pnpm exec prettier --write ."

[tasks."fmt:check"]
description = "Check formatting (for CI)"
depends = ["install"]
run = "pnpm exec prettier --check ."

[tasks.typecheck]
description = "TypeScript type check"
depends = ["install"]
run = "pnpm exec tsc --noEmit"
```

And the relevant `package.json` fragments:

```json
{
  "name": "myapp",
  "private": true,
  "packageManager": "pnpm@9.14.2",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "engines": {
    "node": ">=22"
  }
}
```

## What this gives you

- **Pinned Node 24** — latest LTS line.
- **Pinned pnpm via corepack** — the `packageManager` field is the single source of truth; no `npm install -g pnpm`.
- **Incremental builds** — `sources`/`outputs` on the build task means `mise run build` skips if nothing changed.
- **`mise run dev`** → Next.js dev server with hot reload.
- **`mise run test`** → Playwright e2e.
- **Same commands in CI** — no custom CI steps beyond `mise run lint` / `test` / `build`.

## First-run walkthrough

```sh
# 1. Clone + trust
git clone <repo> myapp && cd myapp
mise trust

# 2. Install Node (mise does this)
mise install

# 3. corepack + pnpm install
mise run install

# 4. Set NODE_ENV for dev
export NODE_ENV=development

# 5. Run the dev server
mise run dev
```

## Suggested project layout

```
myapp/
├── mise.toml
├── package.json
├── pnpm-lock.yaml           # committed
├── pnpm-workspace.yaml      # only for monorepos
├── next.config.ts
├── tsconfig.json
├── .gitignore               # includes .next, node_modules, .env.local
├── .prettierrc
├── eslint.config.mjs
├── playwright.config.ts
├── app/                     # App Router
│   ├── layout.tsx
│   └── page.tsx
├── components/
├── lib/
└── tests/
```

## CI snippet (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  ci:
    runs-on: ubuntu-latest
    env:
      NODE_ENV: test
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
        with: { install: true, cache: true }
      - run: mise run install
      - run: mise run typecheck
      - run: mise run lint
      - run: mise run "fmt:check"
      - run: mise run build
      - run: pnpm exec playwright install --with-deps chromium
      - run: mise run test
```

## Common gotchas

1. **`pnpm: command not found` after `mise install`** → corepack needs `corepack enable` once. The `[hooks] enter` line should handle it; if not, run manually.
2. **`packageManager` field missing from `package.json`** → corepack won't know which pnpm to use. Add `"packageManager": "pnpm@9.14.2"` and commit.
3. **Turbopack vs webpack** → Next.js defaults are fine. Opt into `--turbo` only if you've tested your deps with it.
4. **`.env.local` vs mise `[env]`** → mise `[env]` is better for team-shared config; `.env.local` is for per-dev overrides. Don't commit `.env.local`.
5. **Playwright browser install** → `playwright install` needs to run once. In CI, `pnpm exec playwright install --with-deps chromium` handles it.
6. **Next.js ESLint plugin conflicts with your own eslint config** → Use Next's config as the base and extend it, don't replace it.
7. **`pnpm` not finding workspaces in a monorepo** → add `pnpm-workspace.yaml` at the root with `packages: ['apps/*', 'packages/*']`.

## See also

- `mise-lang-node-overview` — Node version resolution.
- `mise-lang-node-packages` — corepack + packageManager deep dive.
- `mise-vscode-integration` — VSCode wiring (important for Next.js IDE features).
- `mise-ci-github-actions` — mise-action caching.
- Next.js docs: `nextjs.org/docs`.
- pnpm: `pnpm.io`.
