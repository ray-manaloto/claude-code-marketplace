---
name: mise-cookbook-ruby-rails
description: End-to-end recipe for a Rails 7+ app managed by mise — Ruby + Node (for assets) + bundler with vendor/bundle + RAILS_ENV + bin/dev. Complete mise.toml template, first-run walkthrough, and common gotchas. Use when starting a new Rails app or adding mise to an existing one.
---

# Cookbook — Rails 7+ app

A complete starting point for a Rails 7+ app using mise. Ruby is pinned via mise; Node (for the asset pipeline) is pinned too; bundler writes gems to `vendor/bundle`; `bin/dev` is the dev loop.

## Who this is for

- Starting a new Rails 7+ app with Propshaft + esbuild/Vite.
- Adding mise to an existing Rails app currently using rbenv + `npm install -g yarn`.
- Replacing a Procfile-based dev loop with mise tasks.

## Who this isn't for

- Sinatra / Hanami / plain Rack apps — the pattern transfers, but drop Node and adjust tasks.
- Legacy Rails 5/6 apps on Ruby 2.7 — the rails version is fine, but upgrade Ruby first.

## The `mise.toml`

```toml
min_version = '2026.4.0'

[tools]
ruby = "3.3.6"
node = "24"        # for esbuild / Vite / importmap-rails asset pipeline

[hooks]
enter = "corepack enable 2>/dev/null || true"

[env]
RAILS_ENV = { required = "development, test, or production" }
BUNDLE_PATH = "vendor/bundle"
BUNDLE_BIN = "vendor/bundle/bin"
_.path = ["vendor/bundle/bin", "bin"]

# DB config — expected from shell/keychain/secrets
DATABASE_URL = { required = "postgres://user:pass@localhost:5432/myapp_dev" }

[redactions]
patterns = ["*_URL", "*_SECRET", "*_TOKEN", "*_API_KEY"]

[tasks.install]
description = "Install gems and npm packages"
run = [
  "bundle install",
  "pnpm install --frozen-lockfile"
]
sources = ["Gemfile", "Gemfile.lock", "package.json", "pnpm-lock.yaml"]

[tasks.dev]
description = "Run bin/dev (the Procfile.dev launcher that ships with Rails 7+)"
depends = ["install"]
run = "bin/dev"

[tasks.server]
description = "Run just the Rails server (no asset watcher)"
depends = ["install"]
run = "bin/rails server"

[tasks.console]
description = "Rails console"
depends = ["install"]
run = "bin/rails console"

[tasks."db:create"]
depends = ["install"]
run = "bin/rails db:create"

[tasks."db:migrate"]
depends = ["install"]
run = "bin/rails db:migrate"

[tasks."db:seed"]
depends = ["install"]
run = "bin/rails db:seed"

[tasks."db:reset"]
depends = ["install"]
run = "bin/rails db:drop db:create db:migrate db:seed"

[tasks.test]
description = "Run Rails tests"
depends = ["install"]
run = "bin/rails test"

[tasks."test:system"]
description = "Run system tests"
depends = ["install"]
run = "bin/rails test:system"

[tasks.lint]
description = "RuboCop lint"
depends = ["install"]
run = "bundle exec rubocop"

[tasks.routes]
depends = ["install"]
run = "bin/rails routes"
```

## What this gives you

- **Pinned Ruby + Node** — one file pins both runtimes.
- **`BUNDLE_PATH=vendor/bundle`** — project-scoped gems, nuke with `rm -rf vendor/bundle`.
- **`BUNDLE_BIN` on PATH** — you can call `rubocop`/`rspec` directly without `bundle exec` in most cases.
- **`bin/dev` as entry point** — Rails 7+'s Procfile.dev-based multi-process dev server.
- **DB tasks** — `db:migrate`, `db:seed`, `db:reset` all mise-wrapped.
- **Redacted secrets** — DATABASE_URL stays out of task logs.

## First-run walkthrough

```sh
# 1. Clone + trust
git clone <repo> myapp && cd myapp
mise trust

# 2. Install Ruby and Node (mise compiles Ruby from source — takes a few minutes)
mise install

# 3. Install gems and npm packages
mise run install

# 4. Set env
export RAILS_ENV=development
export DATABASE_URL="postgres://user:pass@localhost:5432/myapp_dev"

# 5. Create and migrate the DB
mise run db:create
mise run db:migrate

# 6. Start bin/dev (Puma + asset watcher + job runner)
mise run dev
```

## Suggested project layout

```
myapp/
├── mise.toml
├── Gemfile
├── Gemfile.lock           # committed
├── package.json
├── pnpm-lock.yaml         # committed
├── Procfile.dev           # used by bin/dev
├── .gitignore             # includes vendor/bundle, log/*, tmp/*, .env*
├── bin/
│   ├── dev
│   ├── rails
│   └── setup
├── app/
├── config/
├── db/
└── test/
```

## CI snippet (GitHub Actions)

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: postgres }
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      RAILS_ENV: test
      DATABASE_URL: postgres://postgres:postgres@localhost:5432/myapp_test
    steps:
      - uses: actions/checkout@v4
      - uses: jdx/mise-action@v3
        with: { install: true, cache: true }
      - run: mise run install
      - run: mise run db:create
      - run: mise run db:migrate
      - run: mise run lint
      - run: mise run test
```

## Common gotchas

1. **Ruby compile fails on `openssl` or `readline`** → Install build deps. See `mise-lang-ruby-overview` → "Build dependencies".
2. **`bundle install` writes into `~/.local/share/mise/installs/ruby/...`** instead of `vendor/bundle` → `BUNDLE_PATH` env var isn't being read. Run `bundle config set --local path vendor/bundle` once, or verify `[env]` is set.
3. **`bin/dev` not found** → Rails 7+ ships with it; for older apps you need to create it manually. Rails guide: `bin/rails app:template LOCATION=<path-to-template>`.
4. **Node installed but `yarn`/`pnpm` not found** → corepack needs enabling. The `[hooks] enter` line handles it after one shell session in the dir.
5. **Rails doesn't see `DATABASE_URL`** → make sure it's exported in your current shell. SessionStart will warn if not.
6. **Propshaft vs Sprockets** → Rails 7+ default is Propshaft. If migrating, follow the Rails upgrade guide — this cookbook assumes Propshaft.
7. **`rubocop` style changes break on Ruby upgrade** → pin rubocop in Gemfile (`gem "rubocop", "~> 1.68"`) and update deliberately, not on every Ruby bump.

## See also

- `mise-lang-ruby-overview` — Ruby version resolution, build deps.
- `mise-lang-ruby-gems` — bundler, vendor/bundle, binstubs.
- `mise-lang-node-packages` — corepack + pnpm.
- `mise-migrate-from-rbenv` — moving an existing app off rbenv.
- `mise-ci-github-actions` — CI caching.
- Rails 7+ guide: `guides.rubyonrails.org`.
