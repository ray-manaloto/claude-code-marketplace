#!/bin/sh
# ci/acceptance.sh — runs INSIDE the one `mise oci run` container.
# Installs the marketplace from the mounted PR checkout (/work), installs the
# plugin + its four dependencies, runs the SessionStart hook by hand, checks
# the confinement, and (if a Claude auth token is present) runs one real
# question through the plugin. Runs under dash (debian's /bin/sh), which has
# no pipefail — never rely on the exit code of a `cmd | tee` pipe here;
# redirect to a file and check $? instead.
set -eu

echo "== step a: marketplace add (from mounted checkout, no auth) =="
set +e
env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add /work
rc_a=$?
set -e
echo "N2: marketplace add with NO Claude auth -> rc=${rc_a}"
[ "$rc_a" -eq 0 ] || {
	echo "FAIL: N2 — marketplace add needs auth (rc=$rc_a)" >&2
	exit 1
}

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

# Confinement also means the hook writes NOTHING under mise's default
# install location — snapshot it before the hook runs and diff after.
PRE_HOME_INSTALLS="$(ls "$HOME/.local/share/mise/installs" 2>/dev/null || true)"

HOOK_CMD="$(jq -r '.hooks.SessionStart[0].hooks[0].command' "$CLAUDE_PLUGIN_ROOT/hooks/hooks.json")"
HOOK_CMD="$(printf '%s' "$HOOK_CMD" | sed "s#\${CLAUDE_PLUGIN_ROOT}#${CLAUDE_PLUGIN_ROOT}#g")"
sh -c "$HOOK_CMD"

POST_HOME_INSTALLS="$(ls "$HOME/.local/share/mise/installs" 2>/dev/null || true)"
[ "$PRE_HOME_INSTALLS" = "$POST_HOME_INSTALLS" ] || {
	echo "FAIL: hook wrote into \$HOME/.local/share/mise/installs (before: [$PRE_HOME_INSTALLS] after: [$POST_HOME_INSTALLS])" >&2
	exit 1
}

CONFIG_LS="$("$CLAUDE_PLUGIN_ROOT/bin/mise-env" config ls)"
echo "$CONFIG_LS"
[ -n "$CONFIG_LS" ] || {
	echo "FAIL: mise-env config ls printed nothing — the confinement check can't pass vacuously" >&2
	exit 1
}
# mise abbreviates $HOME as "~" in this output, so expand it before comparing.
printf '%s\n' "$CONFIG_LS" | awk -v root="$CLAUDE_PLUGIN_ROOT" -v home="$HOME" '
	NF == 0 { next }
	{
		path = $1
		if (index(path, "~") == 1) { path = home substr(path, 2) }
		if (index(path, root) != 1) { print "FAIL: config path outside plugin root: " path; bad = 1 }
		if (index(path, root "/mise.toml") == 1) { seen_own = 1 }
	}
	END {
		if (bad) exit 1
		if (!seen_own) { print "FAIL: root mise.toml never appeared in config ls"; exit 1 }
	}
'

INSTALLS_LS="$(ls "$CLAUDE_PLUGIN_DATA/mise/installs" 2>/dev/null | sort | tr '\n' ' ')"
EXPECTED_INSTALLS="pipx-git-https-github-com-ray-manaloto-knowledge-base-git ty "
[ "$INSTALLS_LS" = "$EXPECTED_INSTALLS" ] || {
	echo "FAIL: data-dir installs were [$INSTALLS_LS], expected [$EXPECTED_INSTALLS]" >&2
	exit 1
}

"$CLAUDE_PLUGIN_ROOT/bin/mise-env" exec -- uv --version
"$CLAUDE_PLUGIN_ROOT/bin/mise-env" exec -- gh --version

env -u CLAUDE_PLUGIN_DATA "$CLAUDE_PLUGIN_ROOT/bin/aggregated-research" --help >/tmp/help.out 2>&1
help_rc=$?
cat /tmp/help.out
[ "$help_rc" -eq 0 ] && grep -F 'verbs: trackers' /tmp/help.out >/dev/null || {
	echo "FAIL: --help did not print 'verbs: trackers' (rc=$help_rc)" >&2
	exit 1
}

echo "== step d.5: run the CLI directly — the deterministic proof it works =="
"$CLAUDE_PLUGIN_ROOT/bin/aggregated-research" trackers openai/codex-plugin-cc "agent team tokens" --out /tmp/direct-trackers.json
jq -e '.adapter == "trackers" and (.hits | type == "array")' /tmp/direct-trackers.json >/dev/null || {
	echo "FAIL: direct CLI run did not produce the expected trackers JSON shape" >&2
	cat /tmp/direct-trackers.json >&2
	exit 1
}
echo "direct CLI run OK: $(cat /tmp/direct-trackers.json)"

echo "== step e: agent, gated on CLAUDE_CODE_OAUTH_TOKEN =="
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
	set +e
	claude -p 'Following ONLY /work/README.md and /work/aggregated-research/README.md, confirm the aggregated-research plugin is installed, then run `aggregated-research trackers openai/codex-plugin-cc "agent team tokens" --out /tmp/agent-trackers.json` and report that you did.' \
		--allowedTools "Read,Bash" \
		>/tmp/agent.out 2>&1
	agent_rc=$?
	set -e
	cat /tmp/agent.out
	[ "$agent_rc" -eq 0 ] || {
		echo "FAIL: claude -p exited $agent_rc" >&2
		exit 1
	}
	# The evidence is the file the agent's own CLI run wrote, not a grep of
	# the model's prose — the model saying it ran the command is not proof.
	[ -f /tmp/agent-trackers.json ] || {
		echo "FAIL: /tmp/agent-trackers.json does not exist — the agent did not run the CLI with --out" >&2
		exit 1
	}
	jq -e '.adapter == "trackers" and (.hits | type == "array")' /tmp/agent-trackers.json >/dev/null || {
		echo "FAIL: agent's trackers output has the wrong shape" >&2
		cat /tmp/agent-trackers.json >&2
		exit 1
	}
	echo "agent CLI run OK: $(cat /tmp/agent-trackers.json)"
else
	echo "SKIPPED: no CLAUDE_CODE_OAUTH_TOKEN"
fi

echo "== acceptance.sh: all steps completed =="
