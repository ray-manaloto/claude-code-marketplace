---
name: mise-contrib-add-backend
description: Step-by-step playbook for adding a new tool backend to the jdx/mise Rust codebase. Use when contributing to jdx/mise and implementing a new install source under src/backend/. Walks the Backend trait, registration, tests, and the conventional commit. NOT for adding a new tool to an existing backend (that's a registry entry — see mise-contrib-add-registry).
---

# Adding a new mise backend

> **Decide first**: most "add support for X" requests are **registry entries** (just a `registry/<name>.toml` file pointing at an existing backend), **not** new backends. Only add a backend when the install source itself (the package manager / artifact format / API) is genuinely new.

## When you actually need a new backend

| Situation | Action |
|---|---|
| Tool is on GitHub releases | `registry: add` entry pointing at `github:` or `aqua:` |
| Tool is on PyPI / npm / cargo / RubyGems | `registry: add` entry pointing at `pipx:` / `npm:` / `cargo:` / `gem:` |
| Tool is a binary blob at a fixed URL | `registry: add` entry pointing at `http:` |
| Tool is a language runtime needing special bootstrap (rustup, pyenv-style compile) | New **core tool** under `src/plugins/core/` |
| Tool's install source is a brand-new package manager / API (not in the 15 existing backends) | New **backend** under `src/backend/` |

## Step-by-step

### 1. Pick the closest analogue

Read the existing backend that's most similar to your target before writing anything:

| Your case | Start from |
|---|---|
| Fetch from a package index, run a build command | `src/backend/cargo.rs` |
| Download a release artifact, extract, place | `src/backend/github.rs` or `src/backend/ubi.rs` |
| asdf-shaped script plugin | `src/backend/asdf.rs` |
| Aqua-registry-style declarative | `src/backend/aqua.rs` |
| Custom URL with checksum per platform | `src/backend/http.rs` |

Mirror its structure exactly. mise's backends share a lot of helpers in `src/backend/static_helpers.rs`, `src/backend/asset_matcher.rs`, `src/backend/version_list.rs`.

### 2. Create `src/backend/<name>.rs`

Implement the `Backend` trait. The trait is defined in `src/backend/mod.rs` — `Grep` it for the current required method set (it evolves):

Common required methods:

- `fa()` — backend short name (e.g., `"my-backend"`)
- `name()` / `id()` — full identifier
- `_list_remote_versions()` — fetch available versions from upstream
- `install_version_impl()` — download / build / install into the install path
- `list_bin_paths()` — directories to add to PATH (most backends return `["bin"]`)
- `get_aliases()` — version aliases like `lts`
- Optional: `verify_checksum()`, `dependencies()`

Use `tokio::process::Command` for shelling out. Don't block — backends are async.

### 3. Add a `BackendType` variant

Edit `src/backend/backend_type.rs` and add your variant. This is a small enum used for dispatch and serialization.

### 4. Register in `src/backend/mod.rs`

```rust
mod my_backend;   // add the module declaration
```

And in `Backend::from_arg` (or whatever the dispatch function is now called — `Grep` for it), add a match arm that constructs your backend when the prefix matches.

### 5. Lockfile support

If your backend can produce checksum / size / URL / provenance, populate them in the install result so `mise lock` can record them. The lockfile format is in `src/lockfile/`. Aim for at least version + URL + checksum.

| Support level | What to populate |
|---|---|
| Basic | version |
| Standard | version + URL + checksum |
| Full | version + URL + checksum + size |
| Best | + provenance (slsa / cosign / minisign / github-attestations) |

### 6. Tests

Add at least one e2e test. Delegate the bash to the `mise-e2e-author` agent.

```
e2e/backend/test_<name>
```

Inside, exercise:
- A successful install (lightweight version if possible)
- Version listing
- Bin path resolution
- A failure path (bogus version, network error if applicable)

Run with:

```sh
mise run test:e2e backend/test_<name>
```

Add unit tests inline in `src/backend/<name>.rs` if you have non-trivial parsing logic.

### 7. Build, lint, run tests

```sh
mise run build
mise run test:e2e backend/test_<name>
mise run lint-fix     # then `git add -u`
```

### 8. Conventional commit

```
feat(backend): add <name> backend
```

Scope is `backend`. Body should explain:
- What ecosystem it installs from
- Why an existing backend doesn't suffice
- Any security considerations (does it execute remote code?)

### 9. Docs

- Add `docs/dev-tools/backends/<name>.md` following the existing pattern.
- Update `docs/dev-tools/backends/index.md` to list the new backend.
- Run `mise run render` to regenerate the rest.

## What you avoid

- Adding required methods to the `Backend` trait without checking every implementor.
- Inventing new abstractions when an existing helper solves it.
- Backends that execute arbitrary remote code (asdf-style) — these are no longer accepted.
- Skipping the docs page.
- Running e2e tests directly instead of via `mise run test:e2e`.

## See also

- `mise-backend-expert` agent — implements/reviews backend code
- `mise-contrib-add-registry` — for the 90% case (just adding a tool short name)
- `mise-contrib-write-e2e-test` — e2e bash conventions
- `src/backend/mod.rs` — the trait definition
- `mise.jdx.dev/dev-tools/backends/`
