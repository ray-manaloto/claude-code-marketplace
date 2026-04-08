---
description: Combined full-vertical setup — C++ toolchain plus AI CLIs in one mise.toml (for dev-tool projects)
---

For projects that want both a C++ toolchain AND the AI CLI stack in the same `mise.toml`. Common for: dev-tool projects, compiler research, any codebase where you're writing C++ and also heavily using AI assistants for code review / generation.

## Steps

1. Run `/mise-cpp-init` (or delegate to `mise-cpp-architect`) to produce the C++ half of the config.
2. Run `/mise-ai-init` (or delegate to `mise-ai-cli-architect`) to produce the AI CLI half.
3. **Merge** the two proposals into a single `mise.toml`:
   - `[tools]` — union of both tool sets.
   - `[env]` — union of both env blocks. Watch for conflicts (unlikely between C++ and AI CLIs).
   - `[tasks]` — all tasks from both halves, namespaced if needed (e.g., `ai-status`, `build`, `configure`).
   - `[redactions]` — keep the `*_API_KEY`/`*_TOKEN`/`*_SECRET` patterns from the AI half.
4. Show the merged diff against any existing `mise.toml` and ask for confirmation.
5. After writing, walk the user through:
   - `/mise-ai-keys` to set up API keys.
   - `mise trust && mise install` for the C++ tools.
   - `mise run build` + `mise run ai-status` to verify both halves.

## Example merged output

```toml
min_version = '2026.4.0'

[tools]
# C++
cmake       = "latest"
ninja       = "latest"
ccache      = "latest"
# AI CLIs
node        = "24"
claude      = "latest"
codex       = "latest"
aichat      = "latest"
"npm:@google/gemini-cli" = "latest"

[env]
CMAKE_GENERATOR = "Ninja"
CMAKE_CXX_COMPILER_LAUNCHER = "ccache"
CCACHE_DIR = "{{config_root}}/.cache/ccache"
ANTHROPIC_API_KEY = { required = "console.anthropic.com", redact = true }
OPENAI_API_KEY    = { required = "platform.openai.com", redact = true }
GEMINI_API_KEY    = { required = "aistudio.google.com/app/apikey", redact = true }

[redactions]
patterns = ["*_API_KEY", "*_TOKEN", "*_SECRET"]

[tasks.configure]
run = "cmake -S . -B build -GNinja"

[tasks.build]
depends = ["configure"]
run = "ninja -C build"

[tasks.test]
depends = ["build"]
run = "ctest --test-dir build --output-on-failure"

[tasks.ai-status]
description = "Verify AI CLIs are installed and authenticated"
run = ["claude --version", "codex --version", "aichat --version", "gemini --version"]
```

## What to avoid

- Running the two halves in isolation and producing two separate `mise.toml` files.
- Writing plaintext API keys (always defer to `/mise-ai-keys`).
- Mixing `cargo:` or `vfox:` backends into either half.
- Overwriting an existing `mise.toml` without showing the merged diff first.
