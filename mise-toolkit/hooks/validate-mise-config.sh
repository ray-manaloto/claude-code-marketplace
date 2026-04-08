#!/usr/bin/env bash
# PostToolUse Edit|Write hook: when a mise config file is edited, validate it.
#
# Reads tool input on stdin as JSON. Exits 0 silently for non-mise-config edits.
# Exits 0 with stderr message on validation failure (non-blocking — Claude sees the
# warning but the edit still applies).

set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

# Bail early if no file_path or not a mise config
[ -n "$file_path" ] || exit 0

case "$(basename "$file_path")" in
  mise.toml|mise.local.toml|mise.*.toml|.mise.toml|config.toml)
    : # fall through
    ;;
  *)
    exit 0
    ;;
esac

# Only act if the path actually contains "mise" somewhere (avoid false positives
# on unrelated config.toml files like cargo's)
case "$file_path" in
  *mise*) : ;;
  *) exit 0 ;;
esac

# Need mise on PATH and the file must exist
if ! command -v mise >/dev/null 2>&1; then
  exit 0
fi
[ -f "$file_path" ] || exit 0

# Validate via `mise cfg ls` from the file's directory — this loads and parses
# the config without installing anything.
dir="$(dirname "$file_path")"
if ! output="$(cd "$dir" && mise cfg ls 2>&1)"; then
  echo "mise-toolkit: mise.toml validation failed for $file_path" >&2
  echo "$output" >&2
fi

exit 0
