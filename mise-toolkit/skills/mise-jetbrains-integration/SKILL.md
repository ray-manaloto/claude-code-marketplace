---
name: mise-jetbrains-integration
description: Wiring JetBrains IDEs (IntelliJ, PyCharm, GoLand, RubyMine, WebStorm, Android Studio) to mise using the 134130/intellij-mise plugin, plus the ~/.asdf symlink workaround for plugins that don't natively support mise yet. Covers per-language SDK selection and Gradle/Maven integration.
---

# JetBrains IDEs + mise

JetBrains has deeper SDK-management built in than VSCode, so the integration is different — you're configuring *which* SDK the IDE uses, not just PATH. There are two viable paths and one that works when the first fails.

## Path A — the `intellij-mise` plugin (preferred)

Plugin: **Mise** by `134130`, available on the JetBrains Marketplace.
Source: `github.com/134130/intellij-mise`.

Install:

1. `Settings → Plugins → Marketplace` → search "mise" → install **Mise** by 134130.
2. Restart the IDE.
3. Open a project with a `mise.toml`. The plugin auto-registers the mise-managed tools as project SDKs.

What it handles:
- Auto-detection of `mise.toml` in the project root.
- Registering mise's Python / Node / JDK installs as available SDKs.
- Running `mise exec` for run configurations that target mise-managed tools.
- Reacting to `mise.toml` changes (re-detects after a file write).

What it doesn't handle:
- Every language. Some JetBrains IDEs have language-specific SDK pickers that are older than the plugin and don't consult it. When that happens, use Path B.

## Path B — the `~/.asdf` symlink workaround

mise's install layout is deliberately compatible with asdf: `~/.local/share/mise/installs/<tool>/<version>/` mirrors `~/.asdf/installs/<tool>/<version>/`. JetBrains IDEs have had asdf support for years — many language plugins detect `~/.asdf` automatically.

So: **pretend mise is asdf**:

```sh
# Only do this if ~/.asdf does not already exist as a real directory.
if [ ! -e ~/.asdf ]; then
  mkdir ~/.asdf
fi
ln -sfn ~/.local/share/mise/installs ~/.asdf/installs
ln -sfn ~/.local/share/mise/shims ~/.asdf/shims
```

Now the IDE's asdf detection finds everything. In `Settings → <Language> → <Toolchain>` → "Add SDK" → select "From asdf", the IDE will list `~/.asdf/installs/<tool>/<version>` entries — which are actually mise's installs via the symlink.

**Caveat**: if the user has real asdf installed, DO NOT clobber their `~/.asdf`. Detect this before symlinking. The safe check is `test -L ~/.asdf/installs || test ! -e ~/.asdf/installs`.

## Path C — manual SDK selection

For cases where neither plugin nor symlink works, just point the IDE at the exact install path:

```
~/.local/share/mise/installs/java/21.0.2/
~/.local/share/mise/installs/python/3.12.1/
~/.local/share/mise/installs/node/20.11.0/
```

Add these as "Custom SDKs" via the language-specific toolchain picker. Downside: you manually re-add every time you `mise up`.

## Per-language notes

### IntelliJ IDEA (Java/Kotlin)

Path A works for the `intellij-mise` plugin's Java SDK registration. Gradle integration is the tricky part:

`gradle.properties`:
```properties
org.gradle.java.home=${user.home}/.local/share/mise/installs/java/21.0.2
```

Or, project-wide, set the Gradle JVM in `Settings → Build, Execution, Deployment → Build Tools → Gradle → Gradle JVM` to the mise-installed JDK.

For Maven, similar story — set `JAVA_HOME` in the run configuration's environment or use the `maven.executable.path` setting.

### PyCharm (Python)

Path A usually works. Path B (asdf symlink) definitely works — PyCharm's Python interpreter picker has long supported asdf.

`Settings → Project → Python Interpreter → Add → System Interpreter` and select `~/.local/share/mise/installs/python/<ver>/bin/python`.

For virtual environments managed by uv / poetry, point at the venv's python, not mise's directly. mise gives you the right python to *create* the venv; PyCharm points at the venv afterwards.

### GoLand (Go)

Path A + `Settings → Go → GOROOT → Add` → select the mise Go install. Path B works too.

### WebStorm (Node)

Path A or B. For yarn/pnpm/bun, make sure `corepack` is enabled so the right package manager version is used: `mise exec -- corepack enable`.

### RubyMine / Rider / Android Studio

All follow the same pattern: Path A first, fall back to Path B if the language plugin doesn't pick up the mise-registered SDK.

## Environment variables in run configurations

JetBrains run configurations don't always inherit shell env. To give a run config access to mise env vars:

1. In the run config dialog → "Environment variables" → click the expand icon.
2. Set `PATH=$HOME/.local/share/mise/shims:$PATH`.
3. Set individual vars from `mise env` if the run config needs them.

For a project-wide default, edit the run config template (Defaults → Shell Script → Environment).

## Known issues

- **The plugin not detecting `mise.toml`** after a write: `File → Invalidate Caches → Restart`.
- **Gradle picking the wrong JDK**: explicit `org.gradle.java.home` beats IDE settings.
- **asdf symlink stale after `mise up`**: symlinks are stable, but run `mise reshim` if shims go missing.
- **Windows**: the asdf symlink trick doesn't apply (no asdf on Windows). Use Path A or Path C. Symlinks also need Developer Mode or admin.

## See also

- `mise-pathing-and-shims` — how shims are laid out.
- `mise-install-paths` — the full directory tree under `~/.local/share/mise`.
- `mise-ide-activation` — cross-IDE overview.
- `/mise-jetbrains-setup` — guided wiring.
- Plugin: `plugins.jetbrains.com/plugin/<id>-mise` (search "mise" on the marketplace).
