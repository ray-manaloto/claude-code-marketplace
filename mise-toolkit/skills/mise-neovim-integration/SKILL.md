---
name: mise-neovim-integration
description: Wiring Neovim to mise — using vim.env.PATH to prepend the mise shims directory, handling LSP servers installed via mise vs mason.nvim, and the mise neovim cookbook pattern. Use when setting up Neovim for a project that uses mise-managed tools.
---

# Neovim + mise

Neovim is simpler than VSCode or JetBrains: there's no plugin system to fight with, just PATH and a bit of Lua.

## The core pattern

In your `init.lua` (or early in your config load order):

```lua
-- Prepend mise shims to PATH before any LSP / tool invocation.
local mise_shims = vim.fn.expand("~/.local/share/mise/shims")
vim.env.PATH = mise_shims .. ":" .. vim.env.PATH
```

Or, equivalently, in Vimscript `init.vim`:

```vim
let $PATH = expand('~/.local/share/mise/shims') . ':' . $PATH
```

That's it. Every subprocess Neovim spawns — LSPs, linters, formatters, terminal — inherits the modified PATH and finds mise-managed tools.

## Why not just use the login shell?

If you launch Neovim from a terminal where `mise activate` has already run, PATH is already correct, and you don't need the `vim.env.PATH` line.

But:
- If you launch Neovim from a GUI (Neovide, macvim GUI, a desktop launcher), the shell rc never runs.
- If you launch Neovim from `tmux` with `default-command` set weirdly, same problem.
- If you use `nvim --headless` for scripts, same problem.

The `vim.env.PATH` line is a defensive belt-and-suspenders — it's always correct, regardless of how Neovim started.

## Per-project tool activation (vs shims)

Shims resolve to the project-appropriate tool version by reading `mise.toml` at invocation time. So if you have Python 3.11 in project A and 3.12 in project B, opening a file in each and running `:!python --version` gives the right one without any extra work.

This is the biggest reason to use shims over `mise activate` in Neovim: shims are per-invocation-correct, while `mise activate` resolves once at Neovim startup.

## LSP setup (lspconfig / nvim-lspconfig)

With shims on PATH, `nvim-lspconfig` finds LSPs via `cmd = { "pyright" }` etc. automatically. No special config:

```lua
require("lspconfig").pyright.setup({})   -- finds mise-installed pyright via shims
require("lspconfig").gopls.setup({})     -- finds mise-installed gopls
require("lspconfig").ts_ls.setup({})
```

Install the LSPs themselves via `mise.toml`:

```toml
[tools]
"npm:pyright" = "latest"
"aqua:golang/tools/gopls" = "latest"
"npm:typescript-language-server" = "latest"
```

## mason.nvim interop

`mason.nvim` is the traditional way Neovim users install LSPs — it downloads them into `~/.local/share/nvim/mason/`. This works, but it **duplicates** what mise already does: installs language tooling outside the project config.

Options:
1. **Use mise for LSPs, skip mason.** Simplest. Puts LSPs in `mise.toml` so everyone on the team gets the same version.
2. **Use mason for LSPs, mise for language runtimes.** Split concerns. Works fine.
3. **Use both**, with mason deferring to mise when a tool is available — `mason-lspconfig.nvim` has some hooks for this but it's fiddly.

Pick one per project and stick with it. The worst option is having both install `pyright` and wondering which one Neovim picks up (whichever is first on PATH, which is usually mason because `~/.local/share/nvim/mason/bin` is often prepended by mason).

## Formatters / linters (conform.nvim, none-ls, etc.)

Same story as LSPs — install them via mise, let conform/none-ls find them via PATH:

```toml
# mise.toml
[tools]
"aqua:mvdan/gofumpt" = "latest"
"npm:prettier" = "latest"
"pipx:ruff" = "latest"
```

```lua
-- conform.nvim
require("conform").setup({
  formatters_by_ft = {
    go = { "gofumpt" },
    javascript = { "prettier" },
    python = { "ruff_format" },
  },
})
```

## Terminal mode

When you open `:terminal`, Neovim spawns a shell. That shell reads its rc files. If your shell rc runs `mise activate`, PATH gets set up normally. The `vim.env.PATH` change also gets inherited. Everything works.

## Launching Neovim from mise tasks

If you want `mise run dev` to launch Neovim with the right tools, put it in `mise.toml`:

```toml
[tasks.dev]
run = "nvim"
```

Then `mise run dev` gives you a Neovim session with `mise.toml`'s `[env]` vars already set and tools on PATH.

## The mise cookbook

mise ships a Neovim cookbook recipe at `docs/mise-cookbook/neovim.md` (in the jdx/mise repo) / `mise.jdx.dev/mise-cookbook/neovim.html` with additional patterns. Worth reading once if you're doing a deep setup.

## Known issues

- **Launching Neovim via an application launcher (Alfred, Raycast, Spotlight)** on macOS: desktop launchers don't run shell rc files. The `vim.env.PATH` line is essential here.
- **AstroNvim / LazyVim / NvChad** (distros): add the `vim.env.PATH` line to your user config's startup, not the distro files (those get overwritten on update).
- **Treesitter compilers**: `:TSInstall <lang>` uses `cc` / `gcc` from PATH. Make sure one is available — either from the system or from mise (`ubi:gcc`, etc.).

## See also

- `mise-pathing-and-shims` — how shims work under the hood.
- `mise-ide-activation` — cross-IDE overview.
- mise docs: `mise.jdx.dev/mise-cookbook/neovim.html`.
