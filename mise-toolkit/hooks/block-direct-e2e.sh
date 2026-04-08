#!/usr/bin/env bash
# PreToolUse Bash hook: block direct execution of jdx/mise e2e test files.
#
# CLAUDE.md rule (from jdx/mise): e2e tests must run via `mise run test:e2e ...`,
# never directly. The harness sets up isolated MISE_DATA_DIR / MISE_CONFIG_DIR per
# test and tears it down. Direct invocation pollutes the user's home dir.
#
# Reads tool input on stdin as JSON. Exits 2 with stderr message to deny.
# Exits 0 to allow.

set -euo pipefail

input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

[ -n "$cmd" ] || exit 0

# Match a Bash command-HEAD invoking an e2e test file directly. A command head
# is the start of the string, or follows ;, &&, ||, |, & — NOT plain whitespace
# (otherwise `echo bash e2e/test_things` would false-positive). Forms blocked:
#   - bash e2e/<area>/test_<name>
#   - sh   e2e/<area>/test_<name>
#   - source e2e/<area>/test_<name>
#   - .    e2e/<area>/test_<name>
#   - ./e2e/<area>/test_<name>
head='(^|[;&|]|&&|\|\|)[[:space:]]*'
pattern_runner="${head}(bash|sh|source|\\.)[[:space:]]+\\.?/?e2e/[^[:space:]]*test_[^[:space:]]*"
pattern_dotslash="${head}\\./e2e/[^[:space:]]*test_[^[:space:]]*"

if printf '%s' "$cmd" | grep -Eq "$pattern_runner" || printf '%s' "$cmd" | grep -Eq "$pattern_dotslash"; then
  # Allow if the command also goes through `mise run test:e2e` (e.g., chained)
  if ! printf '%s' "$cmd" | grep -q 'mise run test:e2e'; then
    cat >&2 <<'EOF'
mise-toolkit: blocked direct e2e test invocation.

Run mise e2e tests through the mise task so the harness can set up isolated
MISE_DATA_DIR / MISE_CONFIG_DIR per test and tear them down afterward:

  mise run test:e2e <area>/test_<name>

Direct invocation (bash e2e/..., ./e2e/..., source e2e/...) is denied.
EOF
    exit 2
  fi
fi

exit 0
