---
name: mise-migrate-from-rbenv
description: Migrating from rbenv to mise — reading .ruby-version, handling rbenv-gemset, preserving installed rubies, and tearing down ~/.rbenv cleanly. Use when a user is currently using rbenv and wants to adopt mise for Ruby version management.
---

# Migrating from rbenv to mise

rbenv is to Ruby what pyenv is to Python: the long-standing version manager with a shell-based init. mise uses the same ruby-build backend internally, so the set of installable Rubies is identical. Migration is mostly about swapping the shell init and teaching mise to read existing `.ruby-version` files.

## The migration plan

1. Inventory rbenv state.
2. Create `mise.toml` per project (or enable idiomatic reader).
3. Swap shell rc.
4. Verify + re-set up bundler path config.
5. Uninstall rbenv (and rbenv-gemset if present).

## Step 1 — inventory

```sh
rbenv versions               # installed rubies
rbenv version                # current
rbenv global                 # default
cat .ruby-version            # project pin
grep -r rbenv ~/.zshrc ~/.bashrc ~/.bash_profile 2>/dev/null
```

Also check for **rbenv-gemset** (rarely used, but still around):

```sh
rbenv gemset list 2>/dev/null
cat .rbenv-gemsets 2>/dev/null
```

If you're using rbenv-gemset, you were splitting gems per project without bundler. mise (and the rest of the modern Ruby world) uses bundler for that. You'll need to convert to a `Gemfile` + `vendor/bundle` approach — see "rbenv-gemset migration" below.

## Step 2 — mise.toml per project

For a plain `.ruby-version` containing `3.3.6`:

```toml
# mise.toml
[tools]
ruby = "3.3.6"
```

Or enable the idiomatic reader:

```toml
# mise.toml or ~/.config/mise/config.toml
[settings]
idiomatic_version_file_enable_tools = ["ruby"]
```

With the idiomatic reader, both `.ruby-version` and the `ruby` directive in `Gemfile` are consulted.

### Global default

```toml
# ~/.config/mise/config.toml
[tools]
ruby = "3.3.6"
```

## Step 3 — swap shell rc

Remove rbenv init:

```sh
# ~/.zshrc — DELETE
export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init - zsh)"
```

Add mise:

```sh
eval "$(mise activate zsh)"
```

Restart shell.

## Step 4 — verify + bundler

```sh
which ruby
# should be under ~/.local/share/mise/

ruby --version
cd <project-with-.ruby-version>
ruby --version   # matches project pin
```

Bundler: if you had `bundle config set --local path vendor/bundle` already, it still works — bundler's config is stored in `.bundle/config` in the project, unrelated to which Ruby version manager you use. Run:

```sh
bundle config      # shows current config
bundle install     # gems install into vendor/bundle as before
```

If you hadn't set a local bundler path and your gems were going into rbenv's per-version gem dir, now is a good time to switch:

```sh
bundle config set --local path 'vendor/bundle'
echo 'vendor/bundle' >> .gitignore
bundle install
```

See `mise-lang-ruby-gems` for the full bundler story.

## rbenv-gemset migration

rbenv-gemset is the old way to have "project-local gems without bundler". It's obsolete — use bundler + `vendor/bundle` instead.

### Before (rbenv-gemset)

```
.rbenv-gemsets contains: myproject
Gems live under:         ~/.rbenv/gemsets/myproject/
```

### After (bundler + vendor/bundle)

```sh
# In the project dir, create a Gemfile if one doesn't exist
bundle init
# Edit Gemfile to list your gems
bundle config set --local path 'vendor/bundle'
bundle install
```

```
.gitignore: vendor/bundle
Gems live under: vendor/bundle/ruby/3.3.0/gems/
```

This is the modern Ruby convention. `Gemfile` is tracked, `Gemfile.lock` is tracked (for applications), `vendor/bundle` is ignored.

## Step 5 — uninstall rbenv

```sh
rm -rf ~/.rbenv
# If installed via Homebrew:
brew uninstall rbenv ruby-build
```

Restart shell. Verify `which rbenv` reports not found.

## Common issues

### "OpenSSL not found" during Ruby install

Build deps missing. See `mise-lang-ruby-overview` → "Build dependencies". On macOS:

```sh
brew install openssl@3 readline libyaml
```

Then retry `mise install ruby@<version>`.

### `gem install` fails with permission error

You're accidentally invoking system Ruby. Check `which gem` — should resolve into mise's install tree. If it's `/usr/bin/gem`, mise's shims aren't first on PATH. Verify shell rc order.

### `bundle exec` is slower than I remember

Each `bundle exec` re-parses the Gemfile. This is unchanged from rbenv. For faster dev loops, use binstubs:

```sh
bundle binstubs rspec-core
bin/rspec   # much faster than bundle exec rspec
```

### Existing rubies aren't detected

They're in `~/.rbenv/versions/`; mise looks in `~/.local/share/mise/installs/ruby/`. Reinstall via mise:

```sh
mise install ruby@3.3.6
```

ruby-build downloads the source and compiles (same as rbenv did). If you want to avoid the recompile wait, you can copy directories between the two locations, but it's usually not worth the fiddle — a fresh install is cleaner.

### IDE still points at rbenv Ruby

Update the IDE's Ruby SDK path to `~/.local/share/mise/installs/ruby/<version>/bin/ruby`, or use the asdf-symlink workaround from `mise-jetbrains-integration` if your IDE's Ruby plugin expects the old layout.

## Multiple Rubies

```toml
[tools]
ruby = "3.3 3.2"    # both installed; first is default
```

## Global tools (rubocop, standard, solargraph)

If you had these installed globally via `gem install`, move to mise's `gem:` backend (see `mise-lang-ruby-gems`) or — better — put them in your project's Gemfile:

```ruby
# Gemfile
group :development do
  gem "rubocop", "~> 1.68"
  gem "solargraph"
end
```

Project-scoped linters > global linters for team consistency.

## Rollback

Reinstall rbenv. Your `.ruby-version` files are untouched.

```sh
git clone https://github.com/rbenv/rbenv.git ~/.rbenv
# follow rbenv install docs
```

Remove `mise activate` from shell rc. Restart.

## See also

- `mise-lang-ruby-overview` — Ruby version resolution and build deps.
- `mise-lang-ruby-gems` — bundler, vendor/bundle, binstubs.
- `mise-migrate-from-asdf` — general migration shape.
- mise docs: `mise.jdx.dev/lang/ruby.html`.
