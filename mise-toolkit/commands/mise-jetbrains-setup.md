---
description: Wire JetBrains IDEs to mise — install intellij-mise plugin or apply the asdf-symlink workaround
---

Set up a JetBrains IDE (IntelliJ IDEA, PyCharm, GoLand, RubyMine, WebStorm, Android Studio, Rider) to pick up mise-managed tools. There are two paths.

## Path A — `134130/intellij-mise` plugin (preferred when available)

1. Install the plugin: `Settings → Plugins → Marketplace → search "mise"` → install **Mise** by `134130`.
2. Restart the IDE.
3. Open a project with a `mise.toml` — the plugin auto-configures the project SDK from the mise-managed toolchain.
4. Verify: `Settings → <Language> → <Toolchain>` — the SDK path should point under `~/.local/share/mise/installs/<tool>/<version>`.

## Path B — asdf-symlink workaround (fallback)

Some JetBrains SDK pickers (older versions, certain language plugins) don't know about mise but do know about asdf. mise's install path is layout-compatible with asdf, so a symlink unlocks the built-in asdf support:

```sh
mkdir -p ~/.asdf
ln -sfn ~/.local/share/mise/installs ~/.asdf/installs
ln -sfn ~/.local/share/mise/shims ~/.asdf/shims
```

Then in the IDE:
1. `Settings → <Language> → <Toolchain>` → Add SDK → detect from asdf.
2. The IDE will find the mise-installed versions under the symlinked `~/.asdf/installs` path.

Caveats:
- If the user actually has asdf installed, do NOT overwrite their symlinks. Detect `~/.asdf/installs` is already present and a real directory before `ln -sfn`.
- Re-run the symlink after installing a new tool version if the IDE doesn't pick it up.

## Path C — Gradle/Maven/Build-tool integration

For JVM projects, also make sure:
- `gradle.properties` or IDE Gradle settings use `org.gradle.java.home=${HOME}/.local/share/mise/installs/java/<version>` (or let the plugin handle it).
- Run configurations inherit `PATH` — the IDE's "Environment variables" field should include `PATH=$HOME/.local/share/mise/shims:$PATH`.

## Steps

1. Ask which JetBrains IDE and which language.
2. Try Path A first — check if the plugin is installed.
3. If Path A isn't viable, fall back to Path B, checking for existing asdf first.
4. Guide the user through the IDE SDK selection dialog.
5. Verify by running the project's language from the IDE's built-in terminal.

For the full breakdown per JetBrains IDE and per language, read `mise-jetbrains-integration`.
