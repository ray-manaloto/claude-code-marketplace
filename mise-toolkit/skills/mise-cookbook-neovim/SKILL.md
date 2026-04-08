---
name: mise-cookbook-neovim
description: End-to-end recipe for a Neovim configuration managed by mise — the vim.env.PATH prepend pattern, LSPs installed via mise (npm:pyright, aqua:gopls, etc.), conform.nvim for formatters, and the mise-managed "editor as a tool" approach. Use when setting up a modern Neovim config that plays nicely with mise-managed projects.
---

# Cookbook — Neovim config managed by mise

A complete setup where Neovim sees mise-managed tools for every project automatically. The host's `mise.toml` pins Neovim itself plus the LSPs and formatters; a small `init.lua` snippet makes Neovim PATH-aware of mise shims; conform.nvim handles formatting.

## Who this is for

- Neovim users who want LSPs pinned alongside language runtimes.
- People who already have a Neovim config and want to make it mise-aware.
- "Editor as a tool" advocates — your editor is a dev dependency, not a system install.

## Who this isn't for

- VSCode / JetBrains users — see `mise-cookbook-node-nextjs` plus `mise-vscode-integration` / `mise-jetbrains-integration` instead.
- Pure vim (not Neovim) users — the LSP story differs substantially.

## Two layers — global + per-project

There are two `mise.toml` files in play:

1. **Global** (`~/.config/mise/config.toml`) — pins Neovim itself and global LSPs/formatters.
2. **Per-project** — each project's `mise.toml` pins its language runtime. Neovim inherits tools via the shims-on-PATH pattern.

## The global `~/.config/mise/config.toml`

```toml
[tools]
# Neovim itself
"aqua:neovim/neovim" = "0.10"

# LSP servers — one per language you use
"npm:pyright" = "latest"                         # Python LSP
"npm:typescript-language-server" = "latest"      # TypeScript/JavaScript
"npm:vscode-langservers-extracted" = "latest"    # HTML/CSS/JSON/ESLint
"aqua:golang/tools/gopls" = "latest"             # Go
"aqua:rust-lang/rust-analyzer" = "latest"        # Rust
"aqua:artempyanykh/marksman" = "latest"          # Markdown
"aqua:LuaLS/lua-language-server" = "latest"      # Lua (for editing your Neovim config!)

# Formatters
"pipx:ruff" = "latest"                           # Python
"aqua:mvdan/gofumpt" = "latest"                  # Go
"npm:prettier" = "latest"                        # JS/TS/JSON/YAML/MD
"aqua:JohnnyMorganz/stylua" = "latest"           # Lua

# Linters
"aqua:mvdan/sh" = "latest"                       # shellcheck-like
"pipx:shellcheck-py" = "latest"                  # shellcheck wrapper

# The non-LSP tools you probably already have
"aqua:BurntSushi/ripgrep" = "latest"             # needed by telescope.nvim
"aqua:sharkdp/fd" = "latest"                     # file finder
"aqua:sharkdp/bat" = "latest"
"aqua:eza-community/eza" = "latest"
```

## The Neovim `init.lua` snippet

Put this **before** any plugin loader or LSP config:

```lua
-- ~/.config/nvim/init.lua (or lua/mise.lua sourced early)

-- Prepend mise shims to PATH so every subprocess Neovim spawns — LSPs, formatters,
-- linters, terminal — inherits the mise-managed tools.
local mise_shims = vim.fn.expand("~/.local/share/mise/shims")
if vim.fn.isdirectory(mise_shims) == 1 then
  vim.env.PATH = mise_shims .. ":" .. vim.env.PATH
end
```

That's the only mise-specific piece. Everything else is standard Neovim config.

## LSP setup with `nvim-lspconfig`

```lua
-- lua/plugins/lsp.lua
local lspconfig = require("lspconfig")

-- Each LSP is found via PATH, so mise shims resolve to the project-correct version.
lspconfig.pyright.setup({})
lspconfig.ts_ls.setup({})
lspconfig.gopls.setup({
  settings = {
    gopls = {
      gofumpt = true,
      staticcheck = true,
    },
  },
})
lspconfig.rust_analyzer.setup({
  settings = {
    ["rust-analyzer"] = {
      cargo = { features = "all" },
      checkOnSave = { command = "clippy" },
    },
  },
})
lspconfig.marksman.setup({})
lspconfig.lua_ls.setup({
  settings = {
    Lua = {
      workspace = { library = vim.api.nvim_get_runtime_file("", true) },
      diagnostics = { globals = { "vim" } },
    },
  },
})
```

No `cmd = { "/abs/path/to/pyright" }` hacks — lspconfig finds each LSP from PATH, and PATH has mise shims prepended.

## Formatting via `conform.nvim`

```lua
-- lua/plugins/conform.lua
require("conform").setup({
  formatters_by_ft = {
    python = { "ruff_format", "ruff_fix" },
    go = { "gofumpt" },
    javascript = { "prettier" },
    typescript = { "prettier" },
    javascriptreact = { "prettier" },
    typescriptreact = { "prettier" },
    json = { "prettier" },
    yaml = { "prettier" },
    markdown = { "prettier" },
    lua = { "stylua" },
  },
  format_on_save = {
    timeout_ms = 500,
    lsp_fallback = true,
  },
})
```

conform.nvim also finds formatters via PATH. All are mise-installed.

## Linting via `nvim-lint`

```lua
-- lua/plugins/lint.lua
require("lint").linters_by_ft = {
  python = { "ruff" },
  sh = { "shellcheck" },
  bash = { "shellcheck" },
}

vim.api.nvim_create_autocmd({ "BufWritePost" }, {
  callback = function() require("lint").try_lint() end,
})
```

## What this gives you

- **Project-aware LSPs** — `gopls` in project A uses the Go pinned by project A's `mise.toml`. Switch projects, gopls auto-switches Go versions. Zero config.
- **Pinned editor tooling** — the whole team running the same LSP / formatter versions means no "ruff formatted differently" noise in diffs.
- **One install command** — `mise install` pulls Neovim, all LSPs, all formatters, all linters.
- **No mason.nvim** — you don't need mason's download layer because mise is the layer. Saves a whole plugin.

## First-run walkthrough

```sh
# 1. Install mise on the host if you haven't.
curl https://mise.run | sh
eval "$(mise activate zsh)"

# 2. Write ~/.config/mise/config.toml with the [tools] block above.
vim ~/.config/mise/config.toml

# 3. Install everything.
mise install

# 4. Open Neovim from any project dir.
cd ~/projects/myapp
nvim

# 5. Verify LSPs are reachable:
#    :LspInfo
#    :checkhealth lsp
```

## Mason.nvim interop (if you want both)

If you already have mason and don't want to rip it out:

```lua
-- Make sure mason's bin dir is AFTER mise shims on PATH
local mison_bin = vim.fn.stdpath("data") .. "/mason/bin"
if vim.fn.isdirectory(mison_bin) == 1 then
  vim.env.PATH = mise_shims .. ":" .. mison_bin .. ":" .. vim.env.PATH
end
```

Now mise shims win when a tool is available via both. Slow migration path: move one LSP at a time from mason to mise, uninstall from mason.

## Common gotchas

1. **Launching Neovim via Alfred/Spotlight/Raycast** → Desktop launchers skip shell rc. The `vim.env.PATH` line in `init.lua` is essential for this case. Don't skip it.
2. **`:checkhealth lsp` reports "pyright not found"** → PATH isn't set correctly or mise shims are missing pyright. Verify `which pyright` in a shell, then `:echo $PATH` inside Neovim.
3. **`gopls` finds the wrong Go version** → gopls uses `go version` to resolve. mise shims handle this per-project automatically. If you see drift, check `mise current go` in the project dir.
4. **Formatter runs but diff looks stale** → conform.nvim's `format_on_save` is async; if you save-and-quit in one motion, you may beat the formatter. Use `:Format` then `:w`.
5. **Multi-root workspaces** → lspconfig picks one root per buffer. That's an lspconfig limitation, not mise's.
6. **`TSInstall <lang>` needs a C compiler** → Treesitter compiles parsers from C. Install `aqua:llvm/llvm-project` globally or rely on system clang.
7. **Emacs / Helix users** → Same pattern. Set `exec-path`/`PATH` to include mise shims early in init.

## See also

- `mise-neovim-integration` — the underlying `vim.env.PATH` pattern in detail.
- `mise-ide-activation` — cross-IDE overview.
- `mise-pathing-and-shims` — how shims work.
- `mise-lang-node-packages` — why `npm:` is fine for LSPs.
- mise neovim cookbook: `mise.jdx.dev/mise-cookbook/neovim.html`.
- conform.nvim: `github.com/stevearc/conform.nvim`.
- nvim-lspconfig: `github.com/neovim/nvim-lspconfig`.
