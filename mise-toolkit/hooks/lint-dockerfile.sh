#!/usr/bin/env bash
# PostToolUse Edit|Write hook: when a Dockerfile that mentions mise is edited,
# warn about common anti-patterns. Non-blocking — exit 0 always; warnings go to
# stderr and Claude sees them in the tool result.
#
# Checks:
#   1. Missing `mise trust` before `mise install` (non-interactive builds fail without it).
#   2. Missing `mise install` after installing mise (mise present but tools not installed).
#   3. Missing BuildKit cache mount for ~/.local/share/mise/installs (slow rebuilds).
#   4. Missing shims on PATH or `mise activate` if the runtime stage references mise.
#
# Uses `hadolint` if available for general Dockerfile linting; falls back to grep heuristics.

set -euo pipefail

input="$(cat)"
file_path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')"

[ -n "$file_path" ] || exit 0

# Only act on Dockerfiles
case "$(basename "$file_path")" in
  Dockerfile|Dockerfile.*|*.Dockerfile|*.dockerfile)
    : # fall through
    ;;
  *)
    exit 0
    ;;
esac

# File must exist and mention mise somewhere — otherwise this hook is irrelevant
[ -f "$file_path" ] || exit 0
if ! grep -qi 'mise' "$file_path" 2>/dev/null; then
  exit 0
fi

warnings=()

# Check 1: `mise install` without preceding `mise trust`
if grep -qE '^[[:space:]]*RUN[[:space:]].*mise[[:space:]]+install' "$file_path" \
   && ! grep -qE '^[[:space:]]*RUN[[:space:]].*mise[[:space:]]+trust' "$file_path" \
   && ! grep -qE 'MISE_TRUSTED_CONFIG_PATHS' "$file_path"; then
  warnings+=("missing 'mise trust' (or MISE_TRUSTED_CONFIG_PATHS env) before 'mise install' — non-interactive builds will fail trust check")
fi

# Check 2: installs mise but never runs `mise install`
if grep -qE '(mise\.run|mise\.jdx\.dev/install|mise[[:space:]]+self-install|MISE_INSTALL_PATH)' "$file_path" \
   && ! grep -qE 'mise[[:space:]]+install' "$file_path"; then
  warnings+=("installs mise but never runs 'mise install' — tools will be absent at runtime")
fi

# Check 3: `mise install` without a BuildKit cache mount for the installs dir
if grep -qE '^[[:space:]]*RUN[[:space:]].*mise[[:space:]]+install' "$file_path" \
   && ! grep -qE 'mount=type=cache.*mise/installs' "$file_path"; then
  warnings+=("'mise install' without a BuildKit cache mount for ~/.local/share/mise/installs — rebuilds will reinstall every tool")
fi

# Check 4: runtime stage copies mise but no PATH / activate
# Heuristic: there's a COPY --from=builder for the mise install tree, but neither
# shims on PATH nor `mise activate` anywhere after it.
if grep -qE 'COPY[[:space:]]+--from=[^[:space:]]+[[:space:]]+[^[:space:]]*\.local/share/mise' "$file_path" \
   && ! grep -qE '(mise/shims|mise[[:space:]]+activate)' "$file_path"; then
  warnings+=("runtime stage copies mise but shims are not on PATH and 'mise activate' is not called — tools will not be found at runtime")
fi

# Check 5: uses `FROM alpine` with mise (musl caveat)
if grep -qiE '^[[:space:]]*FROM[[:space:]]+alpine' "$file_path" \
   && grep -qE '(mise\.run|mise[[:space:]]+install)' "$file_path"; then
  warnings+=("using alpine (musl) as a mise base — many tools ship glibc binaries and will need to compile from source; prefer debian:12-slim unless you need alpine specifically (see mise-docker-base-images)")
fi

# Check 6: no '# syntax' directive but uses cache mount syntax
if grep -qE 'mount=type=cache' "$file_path" \
   && ! head -1 "$file_path" | grep -qE '^#[[:space:]]*syntax='; then
  warnings+=("uses BuildKit '--mount=type=cache' but no '# syntax=docker/dockerfile:1.x' directive — add the syntax header or the build will fail")
fi

# Optional: run hadolint if available (quiet, only surface mise-relevant issues)
if command -v hadolint >/dev/null 2>&1; then
  hadolint_out="$(hadolint --no-color --format tty "$file_path" 2>&1 || true)"
  if [ -n "$hadolint_out" ]; then
    # Only pass through hadolint findings that look mise-adjacent
    mise_hadolint="$(printf '%s\n' "$hadolint_out" | grep -iE 'mise|curl.*sh|latest|WORKDIR' || true)"
    if [ -n "$mise_hadolint" ]; then
      warnings+=("hadolint: $(printf '%s' "$mise_hadolint" | tr '\n' ';' | sed 's/;$//')")
    fi
  fi
fi

# Emit warnings if any
if [ "${#warnings[@]}" -gt 0 ]; then
  echo "mise-toolkit: Dockerfile lint warnings for $file_path" >&2
  for w in "${warnings[@]}"; do
    echo "  - $w" >&2
  done
  echo "  see: mise-docker-patterns, mise-docker-multistage, mise-docker-bootstrap skills" >&2
fi

exit 0
