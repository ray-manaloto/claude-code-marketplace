#!/usr/bin/env bash
# PostToolUse Edit|Write hook: warn (non-blocking) if a file being edited contains
# what looks like a plaintext API key for Anthropic, OpenAI, or Google.
#
# Reads tool input on stdin as JSON. Exits 0 silently for files that don't match.
# Exits 0 with stderr warning on match — the edit still applies, but Claude sees
# the warning and can alert the user.
#
# Matched patterns:
#   sk-ant-api[0-9]{2}-...    Anthropic
#   sk-proj-...               OpenAI project keys
#   sk-[a-zA-Z0-9]{48,}       OpenAI legacy secret keys
#   AIzaSy[A-Za-z0-9_-]{33}   Google API keys (Gemini, Maps, etc.)
#
# Skips: anything under .git/, files named .gitignore, and example/fixture files
# that are obviously documentation (names containing "example", "fixture", "sample",
# "template"). Those are common false-positive sources.

set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

[ -n "$file_path" ] || exit 0
[ -f "$file_path" ] || exit 0

# Skip .git internals
case "$file_path" in
  */.git/*|*/.git) exit 0 ;;
esac

# Skip obvious documentation / fixture files
base="$(basename "$file_path")"
case "$base" in
  .gitignore|.gitattributes) exit 0 ;;
esac
case "$file_path" in
  *example*|*EXAMPLE*|*fixture*|*FIXTURE*|*sample*|*SAMPLE*|*template*|*TEMPLATE*|*.test.*|*_test.go|*test_*)
    # Still scan, but downgrade to a softer message
    is_fixture=1
    ;;
  *)
    is_fixture=0
    ;;
esac

# Grep for each pattern. Use -E and collect hits.
matches=()

if grep -qE 'sk-ant-api[0-9]{2}-[A-Za-z0-9_-]{20,}' "$file_path" 2>/dev/null; then
  matches+=("Anthropic key (sk-ant-api...)")
fi

if grep -qE 'sk-proj-[A-Za-z0-9_-]{20,}' "$file_path" 2>/dev/null; then
  matches+=("OpenAI project key (sk-proj-...)")
fi

# Legacy OpenAI keys: sk- followed by 48+ alphanumerics. Be conservative to avoid
# matching random base64 or git hashes — require the exact sk- prefix and a long tail.
if grep -qE '\bsk-[A-Za-z0-9]{48,}\b' "$file_path" 2>/dev/null; then
  matches+=("OpenAI legacy secret key (sk-...)")
fi

if grep -qE '\bAIzaSy[A-Za-z0-9_-]{33}\b' "$file_path" 2>/dev/null; then
  matches+=("Google API key (AIzaSy...)")
fi

if [ "${#matches[@]}" -gt 0 ]; then
  if [ "$is_fixture" = "1" ]; then
    echo "mise-toolkit: possible plaintext API key in $file_path (fixture/example file — please confirm these are fake keys)" >&2
  else
    echo "mise-toolkit: WARNING — possible plaintext API key in $file_path" >&2
  fi
  for m in "${matches[@]}"; do
    echo "  - matched: $m" >&2
  done
  echo "  Action: if this is a real key, treat it as compromised. Rotate immediately and use keychain / 1Password / a secret manager instead." >&2
  echo "  See: mise-ai-cli-keys skill." >&2
fi

exit 0
