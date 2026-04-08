---
name: mise-lang-ruby-gems
description: Ruby gem management — bundler as the project-level dep manager, the vendor/bundle pattern, rubocop / standard / solargraph installation choices, and why mise's gem: backend is limited compared to aqua for Ruby CLIs that exist. Use when managing gems for a project.
---

# Ruby gems — bundler and the mise layer

Ruby's package manager is `gem`, layered with `bundler` for project-level dep management. mise's job is to pin Ruby; bundler's job is to manage this project's gems on top.

## The layering

```
mise
 └─> ruby 3.3.6 (installed to ~/.local/share/mise/installs/ruby/3.3.6)
      └─> gem (ships with ruby)
           └─> bundler (installed into mise's gem dir, or per-project via corepack-like)
                └─> project gems (in vendor/bundle/ if you follow the rules)
```

Each mise-installed Ruby has its own `gem` command and its own default gem install dir. Switching Ruby versions gives you a fresh gem set. Bundler on top scopes gems to the project.

## Bundler — the whole story

### Installing bundler

After `mise install ruby@3.3.6`, bundler isn't there yet:

```sh
gem install bundler
```

This installs bundler into `~/.local/share/mise/installs/ruby/3.3.6/lib/ruby/gems/3.3.0/`. The binary gets shimmed onto PATH.

Alternatively, commit a `Gemfile` with a `gemspec` or bundler version and `bundle install` will self-bootstrap from the stdlib's `rubygems`.

### Scoping gems to the project

**Default behavior**: `bundle install` writes to the mise install tree's global gem dir. Every project's gems pile up there.

**Better**: scope bundler to the project:

```sh
bundle config set --local path 'vendor/bundle'
bundle install
```

Now gems live in `./vendor/bundle/`, which:
- Is per-project (no cross-project gem conflicts).
- Can be nuked with `rm -rf vendor/bundle`.
- Should be git-ignored (add `vendor/bundle/` to `.gitignore`).
- Is fast to recreate from `Gemfile.lock`.

Wire in `mise.toml`:

```toml
[tools]
ruby = "3.3.6"

[env]
BUNDLE_PATH = "vendor/bundle"
BUNDLE_BIN = "vendor/bundle/bin"
_.path = ["vendor/bundle/bin"]

[tasks.install]
run = "bundle install"
sources = ["Gemfile", "Gemfile.lock", "*.gemspec"]

[tasks.test]
depends = ["install"]
run = "bundle exec rspec"
```

With `BUNDLE_BIN = "vendor/bundle/bin"` and that dir on PATH, you can drop `bundle exec` in most cases and call `rspec` / `rubocop` / `rails` directly.

## `bundle exec` vs binstubs vs PATH

Three ways to run gem-provided binaries:

### `bundle exec rspec`

Explicit, always works. Slow (re-parses Gemfile every time).

### Binstubs in `bin/`

```sh
bundle binstubs rspec-core
bin/rspec
```

Writes `bin/rspec` as a small shim that activates the bundle and execs the real rspec. Fast, explicit, committed to git. The Rails convention.

### PATH-based (via `BUNDLE_BIN`)

```toml
[env]
BUNDLE_BIN = "vendor/bundle/bin"
_.path = ["vendor/bundle/bin"]
```

```sh
rspec    # just works
```

Fast, implicit. Doesn't work for every gem (some don't register bin stubs). Best for dev workflow; binstubs are better for committed `bin/dev`-style scripts.

Use binstubs for Rails. Use BUNDLE_BIN for non-Rails.

## rubocop / standard / solargraph

The most common gem-installed CLIs. Three ways to get them:

### 1. Project-scoped (via Gemfile)

```ruby
# Gemfile
group :development do
  gem "rubocop", "~> 1.68"
  gem "solargraph"
end
```

```toml
[tasks.lint]
run = "bundle exec rubocop"
```

**Pro**: same version for every contributor and CI. **Con**: loads bundler every invocation unless you binstub.

### 2. Global pipx-like (mise gem: backend)

```toml
[tools]
ruby = "3.3"
"gem:rubocop" = "latest"
"gem:solargraph" = "latest"
```

**Pro**: global tool, shimmed by mise. **Con**: uses the ruby_version-specific gem dir, so changing Ruby means reinstall.

### 3. As an aqua tool (rare for Ruby — most Ruby CLIs aren't on aqua)

Most Ruby gem CLIs don't ship GitHub-release binaries — they ship as gems only. So `aqua:` usually isn't an option for Ruby tools.

**Rule**: project-scoped via Gemfile for linters and formatters (everyone gets the same version). Global via `gem:` backend only for personal-preference tools (pry, byebug).

## The `gem:` backend — limited, but useful

mise's `gem:` backend installs rubygems as mise-managed tools:

```toml
[tools]
ruby = "3.3"
"gem:rubocop" = "1.68"
"gem:fastlane" = "latest"
```

**Limitations**:
- Ties the gem to a specific Ruby version (changing Ruby requires reinstall).
- Slower than aqua/github (requires the Ruby toolchain).
- Only one version per project unless you namespace.

**Use for**: global gems that are inherently tied to Ruby, when a Gemfile isn't appropriate (e.g. a dotfiles-level fastlane install).

For most project tools, prefer a Gemfile + binstubs.

## Gemfile.lock hygiene

- **Commit `Gemfile.lock`** for applications (Rails apps, services). Don't commit for libraries (gems) — let consumers resolve their own deps.
- **`bundle install --frozen` in CI** — fails if the lockfile would change.
- **`bundle outdated`** to see what could be updated. Do deliberate upgrades, not blind `bundle update`.
- **`bundle update <gem>`** to bump one gem. Avoid `bundle update` alone (bumps everything).

## Ruby + Node monorepo (Rails + front-end)

```toml
[tools]
ruby = "3.3.6"
node = "24"

[hooks]
enter = "corepack enable 2>/dev/null || true"

[env]
BUNDLE_PATH = "vendor/bundle"
RAILS_ENV = { required = "development or production" }

[tasks.install]
run = [
  "bundle install",
  "pnpm install --frozen-lockfile"
]

[tasks.dev]
depends = ["install"]
run = "bin/dev"

[tasks.test]
depends = ["install"]
run = "bin/rails test"

[tasks."db:migrate"]
depends = ["install"]
run = "bin/rails db:migrate"
```

## Anti-patterns

- **`gem install <anything>` without `--user-install` as a workaround for permission errors** — indicates you're using system Ruby. Fix the root cause (use mise).
- **Mixing rbenv binstubs and mise shims** on PATH. Pick one.
- **Committing `vendor/bundle/`** — no. Lock + reinstall.
- **Deleting `Gemfile.lock` "to resolve conflicts"** — no. Rebase / resolve properly.
- **`sudo gem install`** anywhere, for any reason.
- **Global rubocop + Gemfile rubocop of a different version** — Gemfile wins.

## See also

- `mise-lang-ruby-overview` — Ruby version resolution and build deps.
- `mise-migrate-from-rbenv` — moving off rbenv.
- `mise-tasks-toml` — `sources` / `outputs` for incremental tasks.
- Bundler docs: `bundler.io`.
