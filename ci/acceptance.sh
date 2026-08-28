#!/bin/sh
# ci/acceptance.sh — runs INSIDE the one `mise oci run` container.
# Installs the marketplace from the mounted PR checkout (/work), installs the
# plugin + its four dependencies, runs the SessionStart hook by hand, checks
# the confinement, and (if a Claude auth token is present) runs one real
# question through the plugin.
set -eu

echo "== step a: marketplace add (from mounted checkout, no auth) =="
set +e
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add /work
rc_a=$?
set -e
echo "N2: marketplace add with NO Claude auth -> rc=${rc_a}"

echo "== step b: dependency marketplaces =="
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add firecrawl/firecrawl-claude-plugin
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add exa-labs/exa-mcp-server
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add upstash/context7
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add mvanhorn/last30days-skill

echo "== step c: install aggregated-research@ray-manaloto =="
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin install aggregated-research@ray-manaloto --yes

claude plugin list | grep -F 'aggregated-research@ray-manaloto' >/dev/null || {
	echo "FAIL: aggregated-research@ray-manaloto not in 'claude plugin list'" >&2
	exit 1
}

PLUGIN_ROOT="$(jq -r '.plugins["aggregated-research@ray-manaloto"][0].installPath' "$HOME/.claude/plugins/installed_plugins.json")"
echo "CLAUDE_PLUGIN_ROOT=${PLUGIN_ROOT}"
[ -n "$PLUGIN_ROOT" ] && [ -d "$PLUGIN_ROOT" ] || {
	echo "FAIL: could not resolve an installed CLAUDE_PLUGIN_ROOT" >&2
	exit 1
}

echo "== step d: run the SessionStart hook by hand, then check the confinement =="
export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
export CLAUDE_PLUGIN_DATA="$HOME/.claude/plugins/data/aggregated-research-ray-manaloto"

HOOK_CMD="$(jq -r '.hooks.SessionStart[0].hooks[0].command' "$CLAUDE_PLUGIN_ROOT/hooks/hooks.json")"
HOOK_CMD="$(printf '%s' "$HOOK_CMD" | sed "s#\${CLAUDE_PLUGIN_ROOT}#${CLAUDE_PLUGIN_ROOT}#g")"
sh -c "$HOOK_CMD"

CONFIG_LS="$("$CLAUDE_PLUGIN_ROOT/bin/mise-env" config ls)"
echo "$CONFIG_LS"
printf '%s\n' "$CONFIG_LS" | awk -v root="$CLAUDE_PLUGIN_ROOT" '
	NF == 0 { next }
	{ path = $1; if (index(path, root) != 1) { print "FAIL: config path outside plugin root: " path; bad = 1 } }
	END { if (bad) exit 1 }
'

"$CLAUDE_PLUGIN_ROOT/bin/mise-env" exec -- uv --version
"$CLAUDE_PLUGIN_ROOT/bin/mise-env" exec -- gh --version

env -u CLAUDE_PLUGIN_DATA "$CLAUDE_PLUGIN_ROOT/bin/aggregated-research" --help | tee /tmp/help.out
grep -F 'verbs: trackers' /tmp/help.out >/dev/null || {
	echo "FAIL: --help did not print 'verbs: trackers'" >&2
	exit 1
}

echo "== step e: agent, gated on CLAUDE_CODE_OAUTH_TOKEN =="
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
	claude -p 'Following ONLY /work/README.md and /work/aggregated-research/README.md, confirm the aggregated-research plugin is installed, then run `aggregated-research trackers openai/codex-plugin-cc "agent team tokens"` and print its JSON output verbatim.' \
		| tee /tmp/agent.out
	grep -F '"repo"' /tmp/agent.out >/dev/null || {
		echo "FAIL: agent step did not print a \"repo\" field" >&2
		exit 1
	}
else
	echo "SKIPPED: no CLAUDE_CODE_OAUTH_TOKEN"
fi

echo "== acceptance.sh: all steps completed =="
