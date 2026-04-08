---
name: mise-cpp-clang-tools
description: clang-format, clang-tidy, clangd, and include-what-you-use — install via mise (aqua backends where possible), wire into CI, and the one-version-per-project rule. Use when setting up code quality tooling for a C++ project.
---

# clang-tools — format, tidy, clangd, iwyu

These are the modern C++ code quality stack. Pin them via mise or your team will get subtle format-churn diffs every time someone upgrades clang.

## The tools

| Tool | Purpose | Version pinning matters? |
|---|---|---|
| **clang-format** | Auto-format code to a style | 🔴 Critical — each release changes formatting subtly |
| **clang-tidy** | Static analysis + linting with auto-fix | 🟡 Matters — new checks appear per version |
| **clangd** | LSP server for IDE (VSCode, Neovim, etc.) | 🟢 Less critical — but match clang-tidy version |
| **include-what-you-use (iwyu)** | Find unused / missing `#include`s | 🟡 Matters — tied to clang version |

## Installing via mise

The whole LLVM bundle is the simplest approach:

```toml
[tools]
"aqua:llvm/llvm-project" = "18"
```

This gets you clang-format, clang-tidy, clangd, and lld all at the same version. Pin a specific major (`"18"`) rather than `latest` — see the one-version rule below.

For iwyu specifically:

```toml
[tools]
"aqua:include-what-you-use/include-what-you-use" = "latest"  # verify the exact aqua path
```

(iwyu is tightly coupled to a specific LLVM version — always check compatibility.)

## The one-version-per-project rule

**Every dev and every CI run must use the exact same clang-format version.** Otherwise you get rotating "format the world" PRs because clang-format 17 and 18 disagree on where to break a line.

The `aqua:llvm/llvm-project` pin in `mise.toml` enforces this. Commit `mise.lock` so even the patch version is consistent.

Same logic for clang-tidy: new versions add new checks, which means a previously-clean file starts reporting warnings. Pin the version in `mise.toml` so "the lint rules" are as reproducible as "the source code".

## `.clang-format` setup

At the project root:

```yaml
# .clang-format
BasedOnStyle: Google     # or LLVM, Microsoft, Mozilla, Chromium, WebKit
IndentWidth: 2
ColumnLimit: 100
DerivePointerAlignment: false
PointerAlignment: Left
IncludeBlocks: Regroup
# ... add project-specific overrides
```

And a mise task:

```toml
[tasks."fmt"]
description = "Format all C++ source and headers"
run = "clang-format -i $(find src include -name '*.cc' -o -name '*.h')"

[tasks."fmt:check"]
description = "Check formatting without modifying (for CI)"
run = "clang-format --dry-run --Werror $(find src include -name '*.cc' -o -name '*.h')"
```

Wire `fmt:check` into CI so PRs that aren't formatted fail the build.

## `.clang-tidy` setup

```yaml
# .clang-tidy
Checks: >
  -*,
  bugprone-*,
  cert-*,
  clang-analyzer-*,
  cppcoreguidelines-*,
  modernize-*,
  performance-*,
  portability-*,
  readability-*,
  -modernize-use-trailing-return-type,
  -readability-identifier-length
WarningsAsErrors: 'bugprone-*,cert-*,clang-analyzer-*'
HeaderFilterRegex: '^(src|include)/'
```

And the task:

```toml
[tasks."tidy"]
description = "Run clang-tidy over compile_commands.json"
depends = ["configure"]  # needs build/compile_commands.json
run = "clang-tidy -p build $(find src -name '*.cc')"
```

clang-tidy requires `compile_commands.json` — make sure the configure step sets `CMAKE_EXPORT_COMPILE_COMMANDS=ON`.

## clangd for IDEs

clangd reads `compile_commands.json` too. For VSCode: install the `llvm-vs-code-extensions.vscode-clangd` extension. It auto-detects clangd from PATH — which mise puts there via shims.

Disable the Microsoft C/C++ extension's IntelliSense when using clangd; they fight each other.

Symlink `build/compile_commands.json` to the project root so clangd finds it immediately:

```toml
[tasks.configure]
run = [
  "cmake --preset dev",
  "ln -sf build/compile_commands.json ."
]
```

## CI integration

A typical GitHub Actions job:

```yaml
- uses: jdx/mise-action@v3
- run: mise run configure
- run: mise run fmt:check      # fail on format diff
- run: mise run tidy           # fail on clang-tidy warnings
- run: mise run build
- run: mise run test
```

Because everything is pinned via mise, CI uses the exact same clang-format/clang-tidy as local dev. Zero "works on my machine" drift.

## iwyu (include-what-you-use)

iwyu tells you which `#include` directives are unused, and which missing includes you're accidentally getting through transitive includes. Run it periodically (not on every commit — it's slow and noisy).

```toml
[tasks."iwyu"]
description = "Run include-what-you-use (advisory)"
depends = ["configure"]
run = "iwyu_tool.py -p build"
```

Don't enforce iwyu as a hard CI gate — the warnings are frequently false positives for complex templates. Treat it as an advisory tool you run occasionally.

## Anti-patterns

- **`clang-format` in `pre-commit` hooks without a version pin.** Different devs, different versions, chaos.
- **Running `clang-tidy` without `compile_commands.json`.** Half the checks silently don't fire.
- **Checking in `compile_commands.json`.** It's a build artifact. git-ignore it.
- **Mixing clang-format from homebrew and clang-format from mise.** shims should be first on PATH; verify with `which clang-format`.
- **Disabling every clang-tidy check because "too noisy".** Better: pick a small set (bugprone, cert, performance) and enforce them.

## See also

- `mise-cpp-toolchain-overview` — the big picture.
- `mise-cpp-cmake-ninja-ccache` — `CMAKE_EXPORT_COMPILE_COMMANDS` is set there.
- `mise-vscode-integration` — getting clangd recognized by VSCode.
- clang-format: `clang.llvm.org/docs/ClangFormat.html`.
- clang-tidy: `clang.llvm.org/extra/clang-tidy/`.
- clangd: `clangd.llvm.org`.
