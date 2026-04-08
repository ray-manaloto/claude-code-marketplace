#!/usr/bin/env bash
# SessionStart hook: surface mise context at the start of every session.
#
# Active-nudge mode: prints a one-screen mise status banner whenever a Claude
# Code session starts, so the user always knows what mise can see in the
# current project. Detects:
#   - Whether mise is installed at all
#   - Whether the cwd contains a mise.toml (or related config file)
#   - Whether that config is trusted
#   - How many tools are pinned and how many are installed
#   - Any required env vars that aren't satisfied
#
# This hook prints to stderr so the output appears in Claude's view as
# additional context but doesn't pollute stdin/stdout pipelines.
#
# Cheap and fast — bails early when there's no mise context to surface.

set -euo pipefail

# Where the user invoked claude-code from
cwd="${PWD:-$(pwd)}"

# ---------------------------------------------------------------------------
# 1. Is mise installed?
# ---------------------------------------------------------------------------
if ! command -v mise >/dev/null 2>&1; then
  # Only nudge about installing mise if there's a mise config nearby that
  # would benefit. Otherwise stay quiet.
  if find "$cwd" -maxdepth 3 -type f \( \
       -name 'mise.toml' -o -name '.mise.toml' -o \
       -name 'mise.local.toml' -o -name '.tool-versions' \
     \) 2>/dev/null | grep -q .; then
    cat >&2 <<'EOF'
[mise-toolkit] mise is not installed but a mise config (or .tool-versions) was
found in this project. Run /mise-install to set up mise, then /mise-doctor to
verify. See the mise-overview skill for what mise does.
EOF
  fi
  exit 0
fi

# ---------------------------------------------------------------------------
# 2. Find the nearest mise config (walk up from cwd)
# ---------------------------------------------------------------------------
mise_config=""
search_dir="$cwd"
while [ -n "$search_dir" ] && [ "$search_dir" != "/" ]; do
  for candidate in mise.toml .mise.toml mise.local.toml .config/mise.toml .config/mise/config.toml; do
    if [ -f "$search_dir/$candidate" ]; then
      mise_config="$search_dir/$candidate"
      break 2
    fi
  done
  search_dir="$(dirname "$search_dir")"
done

# If no project config, just print global status
if [ -z "$mise_config" ]; then
  global_config="$HOME/.config/mise/config.toml"
  if [ -f "$global_config" ]; then
    mise_version="$(mise --version 2>/dev/null | awk '{print $1}')"
    cat >&2 <<EOF
[mise-toolkit] mise $mise_version installed. No project mise.toml in this directory tree.
  Global config: $global_config
  Run /mise-init to scaffold a mise.toml for this project, or /mise-explain to learn more.
EOF
  fi
  exit 0
fi

# ---------------------------------------------------------------------------
# 3. Project config found — gather details
# ---------------------------------------------------------------------------
mise_version="$(mise --version 2>/dev/null | awk '{print $1}')"
project_dir="$(dirname "$mise_config")"

# Use `mise dr` for the source of truth on trust and warnings
dr_output="$(cd "$project_dir" && mise dr 2>&1 || true)"
trust_problem=""
if printf '%s' "$dr_output" | grep -qiE 'untrusted|trust'; then
  trust_problem="yes"
fi

# Tool counts (best-effort; mise ls is the canonical source)
tools_listed=""
tools_active=""
if tools_listed="$(cd "$project_dir" && mise ls 2>/dev/null | grep -cE '^[[:space:]]*[a-z]' || echo 0)"; then :; fi
if tools_active="$(cd "$project_dir" && mise current 2>/dev/null | wc -l | tr -d ' ' || echo 0)"; then :; fi

# Required env vars not satisfied (mise env errors loudly when this happens)
missing_required=""
if env_err="$(cd "$project_dir" && mise env 2>&1 >/dev/null || true)"; then
  if printf '%s' "$env_err" | grep -qE 'Required environment variable'; then
    missing_required="$(printf '%s' "$env_err" | grep -E 'Required environment variable' | head -3)"
  fi
fi

# ---------------------------------------------------------------------------
# 4. Print the banner
# ---------------------------------------------------------------------------
{
  echo "[mise-toolkit] mise $mise_version │ project: $(basename "$project_dir")"
  echo "  config: $mise_config"

  if [ -n "$trust_problem" ]; then
    echo "  ⚠ trust: untrusted — run /mise-trust-fix"
  else
    echo "  ✓ trust: ok"
  fi

  if [ -n "$tools_active" ] && [ "$tools_active" != "0" ]; then
    echo "  tools: $tools_active active"
  fi

  if [ -n "$missing_required" ]; then
    echo "  ⚠ required env vars missing:"
    printf '%s\n' "$missing_required" | sed 's/^/      /'
  fi

  # Lockfile presence
  if [ -f "$project_dir/mise.lock" ]; then
    echo "  ✓ mise.lock present"
  else
    echo "  ℹ no mise.lock — run \`mise lock\` for reproducibility"
  fi
} >&2

exit 0
