#!/usr/bin/env bash
# PostToolUse Edit|Write hook: if a Rust file in the jdx/mise repo was edited,
# run `mise run lint-fix` so the next commit is clean.
#
# Reads tool input on stdin as JSON. Exits 0 for non-Rust edits or non-mise repos.
# Exits 0 even on lint failure (non-blocking — the edit still applies).

set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

# Bail early if no file_path or not a .rs file
[ -n "$file_path" ] || exit 0
case "$file_path" in *.rs) : ;; *) exit 0 ;; esac

# Walk up to find the repo root and check that it's a mise checkout
dir="$(dirname "$file_path")"
[ -d "$dir" ] || exit 0
repo_root="$(cd "$dir" && git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$repo_root" ] || exit 0

# Only run for the actual jdx/mise repo (has mise.toml + Cargo.toml + src/cli/)
if [ ! -f "$repo_root/mise.toml" ] || [ ! -f "$repo_root/Cargo.toml" ] || [ ! -d "$repo_root/src/cli" ]; then
  exit 0
fi

# Need mise on PATH
command -v mise >/dev/null 2>&1 || exit 0

# Run lint-fix from the repo root, swallowing failures (non-blocking)
(cd "$repo_root" && mise run lint-fix >&2) || true

exit 0
