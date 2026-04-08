---
name: mise-contrib-add-registry
description: Adding a tool to the mise registry by creating registry/<name>.toml. This is the 90% case for "add support for X to mise" — usually a one-file PR pointing at an existing backend (aqua > github/gitlab > pipx/npm/cargo/go/dotnet). Use when contributing a new tool short-name to jdx/mise.
---

# Adding a registry entry

When users want to install a tool with `mise use <name>` instead of `mise use <backend>:<owner>/<repo>`, that short-name lives in `registry/<name>.toml`.

This is **almost always the right answer** for new tool support. Don't write a new backend.

## Decide the backend

Use the official preference order from `docs/registry.md`:

1. **`aqua:`** — first choice. Check the [aqua-registry](https://github.com/aquaproj/aqua-registry/tree/main/pkgs) for the tool. If it exists, point at it.
2. **`github:` / `gitlab:` / `forgejo:`** — for tools released on the respective forge but not in aqua.
3. **`pipx:`** — Python tools.
4. **`npm:`** — Node tools.
5. **`go:` / `cargo:` / `dotnet:`** — last resort (compiles from source).
6. **NEVER `vfox:` or `asdf:`** for new entries — supply-chain reasons.

You can list multiple backends in priority order so users on different setups get the best one available:

```toml
backends = ["aqua:owner/repo", "github:owner/repo"]
```

## File format

```toml
# registry/<tool-name>.toml
backends = ["aqua:owner/repo", "github:owner/repo"]
test = ["<tool-name> --version", "<expected substring of output>"]
description = "One-line description of the tool"
```

### `backends`

An array, ordered by priority. mise tries them in order; the first that resolves the requested version wins.

For aqua, the value is `aqua:<aqua-registry-pkg-path>` — the path used in the aqua-registry, e.g., `aqua:cli/cli` for the GitHub CLI.

For github, it's `github:<owner>/<repo>`. Same for gitlab/forgejo.

For language ecosystems: `pipx:<pypi-name>`, `npm:<npm-package>`, `cargo:<crates-name>`, `go:<go-module-path>`.

### `test`

A two-element array used by the registry e2e test (`e2e/cli/test_registry`). The first element is a command to run after installing the tool; the second is a substring that must appear in the output. Example:

```toml
test = ["ripgrep --version", "ripgrep"]
```

Use the simplest possible smoke test — `--version`, `--help`, or similar. Don't write tests that need a working internet connection beyond the install itself.

### `description`

Used for `mise registry <name>` and `mise search`. Keep it under 80 characters.

### Optional: aliases / OS restrictions

```toml
aliases = ["alternative-name"]
os = ["linux", "macos"]
```

## Worked example

Let's say you want to add `bun-mise-toolkit-example`, a fictional tool released as a binary on GitHub at `myorg/example`. It exists in aqua at `myorg/example`.

```toml
# registry/bun-mise-toolkit-example.toml
backends = [
  "aqua:myorg/example",
  "github:myorg/example",
]
test = ["bun-mise-toolkit-example --version", "v"]
description = "Example tool used in mise-toolkit docs"
```

## Workflow

1. **Check if it already exists**: `ls registry/<name>.toml` and `mise registry <name>`.
2. **Find the upstream**: aqua-registry first, then GitHub.
3. **Write the file** following the schema above.
4. **Test locally**:
   ```sh
   mise install <name>@latest
   <name> --version  # should match your `test` substring
   ```
5. **Run the registry e2e** (covers basic schema validation):
   ```sh
   mise run test:e2e cli/test_registry
   ```
6. **Commit**:
   ```
   registry: add <name>
   ```
   No scope. Same format for both new tools and fixes to existing entries.

## Common questions

- **"Should I add my own tool?"** — Yes, if it's broadly useful. PRs are usually accepted quickly.
- **"What if my tool is in aqua but I haven't seen it?"** — Search the aqua-registry pkgs directory by repo name. Many packages are nested under organization paths.
- **"Can I add multiple versions / variants?"** — One file per short name. For variants (e.g., `node` vs `nodejs`), use `aliases` rather than separate files.
- **"What about Windows-only / Linux-only tools?"** — Add `os = ["windows"]` (or whichever) to the registry entry.

## What you avoid

- Adding `vfox:` or `asdf:` backends to a new entry.
- Creating a registry entry for a tool that's already available under a different short name (use `aliases` instead).
- Writing a `test` command that requires network beyond the install.
- Skipping the description (used by search).

## See also

- `mise-contrib-add-backend` — only for genuinely new install ecosystems
- `mise-backends-overview` — backend preference rationale
- `mise.jdx.dev/registry.html`
- `registry/` directory in jdx/mise — copy from a similar tool
