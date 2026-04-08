---
name: mise-lang-ruby-overview
description: Ruby via mise — .ruby-version / Gemfile ruby directive auto-detection, why system Ruby is always wrong, bundler as the gem manager on top of mise-pinned Ruby, and the OpenSSL / readline build-dep story. Use when setting up Ruby for a project.
---

# Ruby via mise

Ruby has the simplest version-file story (`.ruby-version` is effectively universal) and the hardest install story (compiles from source, needs OpenSSL + readline + yaml + zlib matched to the host). mise handles both.

## The "never use system Ruby" rule

macOS ships Ruby 2.6. Ubuntu 22.04 ships 3.0. Both are years behind upstream. Worse:
- System Ruby is used by the OS (macOS's `system_profiler`, Ubuntu's `apt` scripts). Installing gems globally can break OS tools.
- Permissions force `sudo gem install`, which is a security smell.
- No per-project version isolation.

**Always** use a version manager for Ruby. mise is one of those version managers.

## Version resolution order

1. `mise.toml` `[tools] ruby` — explicit.
2. `mise.local.toml`.
3. `.tool-versions`.
4. Idiomatic files, opt-in:
   ```toml
   [settings]
   idiomatic_version_file_enable_tools = ["ruby"]
   ```
   Reads `.ruby-version` and the `ruby` directive in `Gemfile`.

## Pinning

```toml
[tools]
ruby = "3.3"         # major.minor
ruby = "3.3.6"       # exact
ruby = "latest"
ruby = "truffleruby-24.1.1"   # alternative runtimes supported
```

**Rule**: pin exact for Rails apps in production. Ruby minor versions introduce subtle behavior changes that can surprise.

## `Gemfile` integration

```ruby
# Gemfile
source "https://rubygems.org"
ruby "3.3.6"

gem "rails", "~> 7.1"
# ...
```

The `ruby "3.3.6"` line at the top of Gemfile is the convention. With the idiomatic reader enabled, mise picks it up automatically — no duplication in `mise.toml`.

## Build dependencies

Ruby compiles from source (no pre-built option as of early 2026). Host needs:

**Debian/Ubuntu**:
```sh
sudo apt-get install -y build-essential libssl-dev libreadline-dev zlib1g-dev \
  libyaml-dev libffi-dev libgdbm-dev libncurses5-dev autoconf bison
```

**macOS** (Homebrew):
```sh
brew install openssl@3 readline libyaml gmp autoconf
```

Missing OpenSSL is the #1 failure mode. Symptom: `ruby -e "require 'net/https'"` fails with `cannot load such file -- openssl`. Fix: install the right OpenSSL dev libs, then `mise install ruby@<version>` again.

On Apple Silicon macOS, mise's ruby-build helper usually finds Homebrew's OpenSSL automatically. If not:

```toml
[env]
RUBY_CONFIGURE_OPTS = "--with-openssl-dir=$(brew --prefix openssl@3)"
```

## Bundler + gem management

Bundler is how Ruby projects manage gems. It's separate from mise, but they cooperate cleanly:

```sh
mise install ruby@3.3.6    # via mise.toml
gem install bundler        # installs into mise's per-version gem dir
bundle install             # reads Gemfile, installs deps into the project
```

The default gem install dir is `~/.local/share/mise/installs/ruby/3.3.6/lib/ruby/gems/3.3.0/`. This means **`bundle install` without `--path` writes into mise's install tree**, which is fine but commingles project gems with the Ruby install.

**Recommended**: scope bundler to the project:

```sh
bundle config set --local path 'vendor/bundle'
bundle install
```

Now gems live in `./vendor/bundle/` (add to `.gitignore`) and `bundle exec` finds them there. Blowing away a project's gems is `rm -rf vendor/bundle`.

Add to `mise.toml`:

```toml
[env]
BUNDLE_PATH = "vendor/bundle"

[tasks.install]
run = "bundle install"
sources = ["Gemfile", "Gemfile.lock", "*.gemspec"]

[tasks.test]
depends = ["install"]
run = "bundle exec rspec"
```

## Common setups

### Rails app

```toml
[tools]
ruby = "3.3.6"
node = "22"            # for asset pipeline / esbuild / jsbundling-rails

[env]
BUNDLE_PATH = "vendor/bundle"
RAILS_ENV = { required = "development, test, or production" }

[tasks.install]
run = [
  "bundle install",
  "yarn install || npm install || true",
]

[tasks.db]
run = "bin/rails db:migrate"

[tasks.dev]
run = "bin/dev"

[tasks.test]
depends = ["install"]
run = "bin/rails test"
```

### Gem (library)

```toml
[tools]
ruby = "3.3"

[tasks.install]
run = "bundle install"

[tasks.test]
run = "bundle exec rspec"

[tasks.lint]
run = "bundle exec rubocop"

[tasks.release]
run = "bundle exec rake release"
```

### Sinatra / plain Ruby service

```toml
[tools]
ruby = "3.3"

[env]
RACK_ENV = { required = "development or production" }
BUNDLE_PATH = "vendor/bundle"

[tasks.dev]
run = "bundle exec puma"
```

## Auto-detection gotchas

1. **`.ruby-version` with a pre-release tag** (`3.4.0-preview1`) — mise supports pre-releases but make sure the exact string matches what `mise ls-remote ruby` shows.
2. **`Gemfile` ruby directive as a range** (`ruby ">= 3.2"`) — bundler's range syntax; mise won't install a range. Pin explicitly.
3. **Bundler version drift** — the `Gemfile.lock` records the bundler version at the bottom. Use `bundle update --bundler` when upgrading Ruby, not a manual `gem install bundler -v …`.
4. **JRuby / TruffleRuby** — mise supports both (`ruby = "jruby-9.4"`, `ruby = "truffleruby-24.1"`), but gems with C extensions often don't work. Pure-Ruby projects only.

## See also

- `mise-lang-ruby-gems` — bundler, rubocop/standard, solargraph, the gem-vs-aqua decision.
- `mise-migrate-from-rbenv` — moving off rbenv.
- `mise-trust-and-security` — why `sudo gem install` is a smell.
- mise docs: `mise.jdx.dev/lang/ruby.html`.
