---
name: mise-trust-and-security
description: The mise trust system, paranoid mode, idiomatic version files (which are OPT-IN), supply-chain settings (`install_before`, provenance verification), and how to handle trust issues in CI / monorepos. Use when the user hits trust prompts, asks "should I trust this", configures CI, sets up a monorepo, or wants to harden mise security.
---

# Trust and security

## The trust system

mise **prompts to trust** any config file it didn't create itself before loading it. Reason: `[env]`, `[hooks]`, and `_.source` directives can execute arbitrary code. Trust is per-file and persists.

```
mise ~/my-project/mise.toml is not trusted. Trust it [y/n]?
```

| Action | Command |
|---|---|
| Trust the nearest config | `mise trust` |
| Trust a specific file | `mise trust <path>` |
| Trust an entire directory tree | Add to `trusted_config_paths` in global config |
| See what's untrusted | `mise dr` (lists under "problems") |
| Untrust (re-prompt) | `mise trust --untrust <path>` |

`mise use` automatically trusts the file it creates, so you'll only see trust prompts on configs written by someone else (teammate, CI, you-by-hand).

### `~/.local/state/mise/ignored-configs/`

If you accidentally said "no" to a trust prompt, mise stores a symlink there marking the config as ignored. To un-ignore: delete the symlink and run `mise dr` again. The symlink name is the encoded path of the original file.

### Non-interactive shells

In non-interactive contexts (CI, IDE extensions, scripts), mise **silently skips** untrusted configs. Set one of:

- `MISE_TRUSTED_CONFIG_PATHS=/path/to/project` (env var, colon-separated for multiple)
- `trusted_config_paths = ["/path/to/project"]` in global config

Or run `mise trust` beforehand as part of CI setup.

### Monorepos

For monorepos with many child `mise.toml` files, the new way is **`experimental_monorepo_root = true`** (requires `MISE_EXPERIMENTAL=1`):

```toml
# Root mise.toml
experimental_monorepo_root = true
```

When the root is trusted, **all descendant configs are implicitly trusted**. This eliminates the need to trust each subdirectory individually. It also enables namespaced task paths like `//projects/frontend:build`.

## Paranoid mode

Set `paranoid = true` (or `MISE_PARANOID=1`) to lock mise down further:

| Behavior | Normal | Paranoid |
|---|---|---|
| Trust check | Only files with `[env]` / `[hooks]` / templates | **Every** config file |
| Trust persistence | Trusted forever (per file path) | **File contents are hashed** — re-prompt on any edit |
| Community plugin install | `mise plugin install shfmt` works | Must use full git URL |
| Internal HTTP (version lists) | HTTP (faster TLS skip) | HTTPS only |
| Provenance verification at `mise install` | Skipped if lockfile already verified | **Re-verified every install** |

Paranoid is jdx's own opt-in — even he doesn't run it by default.

## Idiomatic version files (`.nvmrc`, `.python-version`, etc.) are OPT-IN

This is the **most surprising mise behavior** for adopters coming from asdf/nvm/pyenv. Files like `.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`, `.java-version`, `.go-version`, `.terraform-version` are **disabled by default** in mise.

To enable them per tool:

```sh
mise settings add idiomatic_version_file_enable_tools node
mise settings add idiomatic_version_file_enable_tools python
```

Or in `mise.toml`:

```toml
[settings]
idiomatic_version_file_enable_tools = ["node", "python"]
```

The rationale (from `mise.jdx.dev/configuration.html`): when these files are read, the version they pin always wins over `mise.toml` for that tool, which surprised users. So mise made it opt-in — you have to acknowledge it. Many adopters who hit "wrong tool version" issues haven't enabled this for the language they need.

`mise.toml` `[tools]` always wins if both files exist and the idiomatic file isn't enabled.

## Supply-chain settings

### `install_before` — release age gate

Only resolve to versions released more than N ago. Mitigates against newly-published malicious versions:

```toml
[settings]
install_before = "7d"   # never install versions newer than 7 days
```

Pairs with lockfiles: `install_before` for ongoing protection, lockfile for exact pins.

### Provenance verification

When generating a lockfile, `mise lock` records provenance type per tool: `slsa`, `cosign`, `minisign`, or `github-attestations`. For the **current platform**, mise actually downloads and cryptographically verifies the artifact at lock time. For other platforms, it records the provenance type from registry metadata without verifying.

By default, `mise install` trusts a lockfile that already has both checksum and provenance — it skips re-verification to avoid redundant API calls (especially important for GitHub attestation rate limits).

To force re-verification on every install:

```toml
[settings]
locked_verify_provenance = true
```

This is also automatically enabled by `paranoid = true`.

### Backend security profile

| Backend | Plugin code execution? | Recommended? |
|---|---|---|
| `aqua:` | No (declarative registry) | **Yes** — first choice |
| `github:` / `gitlab:` / `forgejo:` | No (downloads release artifacts) | Yes |
| `core:` | No (built into mise) | Yes |
| `pipx:` / `npm:` / `cargo:` / `go:` / `dotnet:` | Runs the language's package manager | Yes (trust depends on the package) |
| `ubi:` | No | Yes |
| `http:` / `s3:` | No (you provide the URL + checksum) | Yes |
| `vfox:` | **Yes** (Lua plugin code) | Existing only — no new entries accepted |
| `asdf:` | **Yes** (bash plugin code) | Existing only — no new entries accepted |

## Common trust issues (FAQ)

| Symptom | Cause | Fix |
|---|---|---|
| `mise.toml` not loaded | Untrusted | `mise trust` |
| Trusted but still not loading | Symlinked (e.g., GNU Stow) | `mise trust` the actual file path |
| Trust prompt on every open | Accidentally denied | Delete the symlink in `~/.local/state/mise/ignored-configs/` |
| CI silently ignores config | Non-interactive mode | `MISE_TRUSTED_CONFIG_PATHS=$PWD` or trust in CI step |
| Re-prompting on save | Paranoid mode hashes file contents | Re-trust, or disable paranoid |
| Many child configs | Monorepo | Use `experimental_monorepo_root = true` |

## See also

- `/mise-trust-fix` — slash command to diagnose and fix trust issues
- `mise-config-doctor` agent — broader config diagnosis
- `mise.jdx.dev/paranoid.html`
- `mise.jdx.dev/faq.html#my-config-file-is-being-ignored-mise-trust-issues`
