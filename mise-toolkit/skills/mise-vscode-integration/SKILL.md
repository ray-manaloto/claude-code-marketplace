---
name: mise-vscode-integration
description: Wiring VSCode to mise — the hverlin.mise-vscode extension, the terminal.integrated.automationProfile.osx quirk, dual-mode setup (mise activate in .zshrc plus shims in .zprofile), and why VSCode tasks / debuggers need special handling beyond just setting PATH.
---

# VSCode + mise integration

VSCode is the #1 editor used with mise, and it has more quirks than any other. This skill covers all of them.

## The three integration modes

1. **Extension mode** — use `hverlin.mise-vscode`. Best UX.
2. **Shims-on-PATH mode** — set PATH in settings.json. Most compatible.
3. **Dual mode** — do both. Maximum reliability. Recommended.

## Mode 1 — the mise-vscode extension

```sh
code --install-extension hverlin.mise-vscode
```

What it does:
- Reads `mise.toml` and surfaces tools + tasks in a sidebar view.
- Wires the integrated terminal to the right environment automatically.
- Provides the `Mise: ...` command palette entries (Install, Run Task, Show Current Tools).
- Respects `redact = true` env vars in the UI.

What it doesn't do:
- Change how launch configurations (`.vscode/launch.json`) find interpreters. The debugger still resolves `python` / `node` / etc. via PATH.
- Affect external tools spawned by other extensions (e.g. some linters shell out).

So the extension alone is **not sufficient** if the project uses debuggers or launch configurations with mise-managed tools. You still want mode 2.

## Mode 2 — shims on PATH

In `settings.json` (Workspace > User):

```jsonc
{
  "terminal.integrated.env.osx": {
    "PATH": "${env:HOME}/.local/share/mise/shims:${env:PATH}"
  },
  "terminal.integrated.env.linux": {
    "PATH": "${env:HOME}/.local/share/mise/shims:${env:PATH}"
  },
  "terminal.integrated.env.windows": {
    "PATH": "${env:USERPROFILE}\\AppData\\Local\\mise\\shims;${env:PATH}"
  }
}
```

This handles interactive terminals. But there's a gotcha:

### The `automationProfile` quirk (the #1 VSCode-mise bug)

VSCode spawns subprocesses for **tasks**, **debug launches**, and **external tools** via a different shell profile than the integrated terminal. It's called the *automation profile*. On macOS it defaults to a non-login `/bin/zsh`, which means your `~/.zshrc` *does* run but your `~/.zprofile` *doesn't*.

If you have `eval "$(mise activate zsh)"` in `~/.zshrc`, good — tasks will see mise tools.

If you have it in `~/.zprofile` instead (common advice for login-shell performance), **tasks will not see mise tools** and you'll get "command not found" on every debug or task run.

**Fix**: force the automation profile through a login shell:

```jsonc
{
  "terminal.integrated.automationProfile.osx": {
    "path": "/bin/zsh",
    "args": ["-l"]
  },
  "terminal.integrated.automationProfile.linux": {
    "path": "/bin/bash",
    "args": ["-l"]
  }
}
```

Now tasks and debuggers get a login shell, which runs `~/.zprofile` / `~/.bash_profile`, which runs `mise activate`, which puts tools on PATH.

This is the single most common VSCode+mise problem. If a task "suddenly stops working" after a fresh macOS setup, this is usually why.

## Mode 3 — dual mode (recommended)

Do both:

1. **Extension installed** for the sidebar and command palette UX.
2. **Shims in `settings.json`** for non-interactive paths.
3. **Automation profile as login shell** for task/debug subprocesses.
4. **`mise activate` in `~/.zshrc`** (not `~/.zprofile`, or in both).

With dual mode, every path VSCode takes to find a tool eventually hits mise:
- Interactive terminal → `mise activate` → shims and exact versions.
- VSCode task → automation profile login shell → `mise activate` → shims.
- External tool subprocess → inherited PATH from settings.json → shims.
- Extension sidebar → `mise-vscode` extension reads config directly.

## Language-specific notes

### Python

Install the `ms-python.python` extension. It will detect interpreters from PATH, so shims-on-PATH works. In command palette, `Python: Select Interpreter` and pick the `~/.local/share/mise/installs/python/<ver>/bin/python` entry.

Pin the interpreter in `.vscode/settings.json`:

```jsonc
{
  "python.defaultInterpreterPath": "${env:HOME}/.local/share/mise/shims/python"
}
```

### Node

`ms-vscode.js-debug` uses the `node` on PATH. Shims-on-PATH works. No extra setup needed.

### Go

`golang.go` reads `go` from PATH, and also supports `go.goroot` / `go.alternateTools`. Shims-on-PATH is enough for 99% of cases.

### Rust

`rust-lang.rust-analyzer` needs `cargo` and `rustc` on PATH. Shims-on-PATH works. Install `rust` via mise as a regular tool.

### Java

The Java extension uses `java.configuration.runtimes` — point it at `~/.local/share/mise/installs/java/<ver>` explicitly. The shims path alone is not enough for the Java extension.

## Known issues

- **Symlinked dotfiles + trust**: if `~/.zshrc` is a symlink into a dotfiles repo, mise may track the symlink target for trust. Run `mise trust ~/dotfiles/mise/config.toml` explicitly once.
- **Multi-root workspaces**: each folder's `mise.toml` is loaded independently. The `mise-vscode` extension picks one as the active context.
- **Remote SSH** / **WSL**: settings.json needs to be Remote-scoped, not local. Same keys, different scope.

## See also

- `mise-shell-activation` — the host-side `mise activate` details.
- `mise-pathing-and-shims` — how shims work under the hood.
- `mise-ide-activation` — cross-IDE overview.
- `/mise-vscode-setup` — guided wiring.
- extension: `marketplace.visualstudio.com/items?itemName=hverlin.mise-vscode`.
