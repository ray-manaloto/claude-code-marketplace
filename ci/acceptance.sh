#!/bin/sh
# ci/acceptance.sh — runs INSIDE the one `mise oci run` container.
# Installs the marketplace from the mounted PR checkout (/work), installs the
# plugin + its four dependencies, proves the SessionStart hook fires in a fresh
# agent session, checks the confinement, and runs the CLI both through the agent
# and directly. Without a Claude auth token, preserves the script-driven install
# and hand-run hook path. Runs under dash (debian's /bin/sh), which has no
# pipefail — never rely on the exit code of a `cmd | tee` pipe here; redirect to
# a file and check $? instead.
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

if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
	echo "== token path: undo N2 probe before the install agent =="
	claude plugin marketplace remove ray-manaloto
	claude plugin marketplace list --json >/tmp/marketplaces-after-remove.json
	echo "marketplace list after remove: $(cat /tmp/marketplaces-after-remove.json)"
	jq -e '[.[] | select(.name == "ray-manaloto")] | length == 0' /tmp/marketplaces-after-remove.json >/dev/null || {
		echo "FAIL: ray-manaloto survived marketplace removal before session 1" >&2
		exit 1
	}

	echo "== session 1: install agent follows only the marketplace READMEs =="
	set +e
	(
		cd /tmp
		claude -p 'You are validating the marketplace under test, whose checkout is mounted at /work. Follow ONLY the installation instructions in /work/README.md and /work/aggregated-research/README.md. Use the local-development form because /work is the marketplace under test. CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1 is already exported. Install only the marketplace, dependency marketplaces, and plugin those READMEs name. Do not run the hook command, bin/mise-env, or anything under the plugin bin/ directory. Report the exact commands you ran.' \
			--allowedTools "Read,Bash(claude *)" \
			--max-turns 40
	) >/tmp/install-agent.out 2>&1
	install_agent_rc=$?
	set -e
	[ "$install_agent_rc" -eq 0 ] || {
		echo "FAIL: install-agent claude -p exited $install_agent_rc" >&2
		tail -40 /tmp/install-agent.out >&2
		exit 1
	}
else
	echo "== step b: dependency marketplaces =="
	env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add firecrawl/firecrawl-claude-plugin
	env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add exa-labs/exa-mcp-server
	env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add upstash/context7
	env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin marketplace add mvanhorn/last30days-skill

	echo "== step c: install aggregated-research@ray-manaloto =="
	env -u CLAUDE_CODE_OAUTH_TOKEN claude plugin install aggregated-research@ray-manaloto --yes
fi

claude plugin list | grep -F 'aggregated-research@ray-manaloto' >/dev/null || {
	echo "FAIL: aggregated-research@ray-manaloto not in 'claude plugin list'" >&2
	if [ -f /tmp/install-agent.out ]; then
		tail -40 /tmp/install-agent.out >&2
	fi
	exit 1
}

PLUGIN_ROOT="$(jq -r '.plugins["aggregated-research@ray-manaloto"][0].installPath' "$HOME/.claude/plugins/installed_plugins.json")"
echo "CLAUDE_PLUGIN_ROOT=${PLUGIN_ROOT}"
[ -n "$PLUGIN_ROOT" ] && [ -d "$PLUGIN_ROOT" ] || {
	echo "FAIL: could not resolve an installed CLAUDE_PLUGIN_ROOT" >&2
	if [ -f /tmp/install-agent.out ]; then
		tail -40 /tmp/install-agent.out >&2
	fi
	exit 1
}

export CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT"
export CLAUDE_PLUGIN_DATA="$HOME/.claude/plugins/data/aggregated-research-ray-manaloto"

if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
	claude plugin marketplace list --json >/tmp/marketplaces-after-agent.json
	echo "marketplace list after agent install: $(cat /tmp/marketplaces-after-agent.json)"
	jq -e 'any(.[]; .name == "ray-manaloto" and .path == "/work")' /tmp/marketplaces-after-agent.json >/dev/null || {
		echo "FAIL: install agent did not register ray-manaloto from /work" >&2
		tail -40 /tmp/install-agent.out >&2
		exit 1
	}

	if [ -d "$CLAUDE_PLUGIN_DATA/mise/installs" ] && [ -n "$(ls -A "$CLAUDE_PLUGIN_DATA/mise/installs" 2>/dev/null)" ]; then
		echo "FAIL: install agent warmed the plugin data-dir installs before session 2" >&2
		tail -40 /tmp/install-agent.out >&2
		exit 1
	fi

	# Confinement also means the real hook writes NOTHING under mise's default
	# install location — snapshot it before session 2 starts and diff after.
	PRE_HOME_INSTALLS="$(ls "$HOME/.local/share/mise/installs" 2>/dev/null || true)"

	echo "== session 2: fresh agent session fires the real hook and runs the CLI =="
	SESSION_2_START="$(date +%s)"
	set +e
	(
		cd /tmp
		CLAUDE_CODE_SYNC_PLUGIN_INSTALL=1 CLAUDE_CODE_SYNC_PLUGIN_INSTALL_TIMEOUT_MS=600000 \
			claude -p 'Following ONLY /work/README.md and /work/aggregated-research/README.md, confirm the aggregated-research plugin is installed, then run `aggregated-research trackers openai/codex-plugin-cc "agent team tokens" --out /tmp/agent-trackers.json` and report that you did.' \
				--allowedTools "Read,Bash" \
				--output-format stream-json --verbose
	) >/tmp/agent.stream 2>/tmp/agent.err
	agent_rc=$?
	set -e
	SESSION_2_END="$(date +%s)"
	SESSION_2_WALL_CLOCK=$((SESSION_2_END - SESSION_2_START))
	echo "session 2 wall clock: ${SESSION_2_WALL_CLOCK} s (bounds plugin load + MCP connect + hook + one model turn; the hook alone is inside it)"
	[ "$agent_rc" -eq 0 ] || {
		echo "FAIL: claude -p exited $agent_rc" >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}

	jq -c 'select(.type == "system" and .subtype == "hook_response" and .hook_event == "SessionStart" and .outcome == "success" and ((.stdout // "") | contains("aggregated-research: CLI ready")))' /tmp/agent.stream >/tmp/session-start-hook-response.jsonl || {
		echo "FAIL: could not parse session-2 stream for the SessionStart hook response" >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}
	[ -s /tmp/session-start-hook-response.jsonl ] || {
		echo "FAIL: no successful aggregated-research SessionStart hook_response in session 2" >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}
	cat /tmp/session-start-hook-response.jsonl

	jq -c 'select(.type == "system" and .subtype == "init" and (has("plugin_errors") | not) and any(.plugins[]?; .name == "aggregated-research")) | {plugins}' /tmp/agent.stream >/tmp/session-init-plugins.jsonl || {
		echo "FAIL: could not parse session-2 stream for the init plugins" >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}
	[ -s /tmp/session-init-plugins.jsonl ] || {
		echo "FAIL: session-2 init did not include aggregated-research without plugin_errors" >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}
	cat /tmp/session-init-plugins.jsonl

	# The evidence is the file the agent's own CLI run wrote, not a grep of
	# the model's prose — the model saying it ran the command is not proof.
	[ -f /tmp/agent-trackers.json ] || {
		echo "FAIL: /tmp/agent-trackers.json does not exist — the agent did not run the CLI with --out" >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}
	jq -e '.adapter == "trackers" and (.hits | type == "array")' /tmp/agent-trackers.json >/dev/null || {
		echo "FAIL: agent's trackers output has the wrong shape" >&2
		cat /tmp/agent-trackers.json >&2
		tail -40 /tmp/agent.stream >&2
		tail -40 /tmp/agent.err >&2
		exit 1
	}
	echo "agent CLI run OK: $(cat /tmp/agent-trackers.json)"
else
	echo "== step d: run the SessionStart hook by hand, then check the confinement =="

	# Confinement also means the hook writes NOTHING under mise's default
	# install location — snapshot it before the hook runs and diff after.
	PRE_HOME_INSTALLS="$(ls "$HOME/.local/share/mise/installs" 2>/dev/null || true)"

	HOOK_CMD="$(jq -r '.hooks.SessionStart[0].hooks[0].command' "$CLAUDE_PLUGIN_ROOT/hooks/hooks.json")"
	HOOK_CMD="$(printf '%s' "$HOOK_CMD" | sed "s#\${CLAUDE_PLUGIN_ROOT}#${CLAUDE_PLUGIN_ROOT}#g")"
	sh -c "$HOOK_CMD"

	echo "SKIPPED: no CLAUDE_CODE_OAUTH_TOKEN"
fi

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
	echo "FAIL: data-dir installs were [$INSTALLS_LS], expected exactly the tools pinned in aggregated-research/mise.toml [$EXPECTED_INSTALLS] — if the plugin's tool list changed, update EXPECTED_INSTALLS here" >&2
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

echo "== acceptance.sh: all steps completed =="
