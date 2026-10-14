# Probe commands the script wraps (run by hand when `check` cannot)

Plugin cache `W` = `~/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0`
(`dev/handoff.py` takes `CLAUDE_PLUGIN_ROOT` or the newest cached version). Always from `<root>`
with `VIRTUAL_ENV` unset, `PLAN_ID`, `PWF_PLAN_ROOT=<root>` and
`PWF_TRUSTED_PYTHON=$(command -v python3)` exported (the shell fallback takes ~7 s, the Python
twin ~50 ms).

Legacy SessionStart fire (what the next session receives after `/clear`):

```sh
printf '{"session_id":"probe-%s","cwd":"%s","hook_event_name":"SessionStart","source":"clear"}' "$(date +%s)" "$PWD" \
  | CLAUDE_PLUGIN_ROOT=$W PWF_SESSION_ID=probe-$(date +%s) sh $W/hooks/claude-hook.sh session-start \
  | python3 -I -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"])'
```

Smart fire: the same with `PWF_INJECT=smart` (or `<plan>/.mode` = `inject-smart`); expect a
`phases: n/m complete` line and `## Next Step` with its handoff bullets.

Pretool twin (the 30-line view every subagent gets per tool call):
`PWF_SESSION_ID=probe-$(date +%s) python3 -I $W/scripts/inject-plan.py --context=pretool`.

Plan doctor and completion state: `sh $W/scripts/plan-doctor.sh` (expect `PASS resolver`,
`PASS injection`), `bash $W/scripts/check-complete.sh` (expect `Task in progress`).

Doctor block: `python3 -I dev/doctor/cli.py --surface session-start --format context --repo $PWD`
(until w0-doctor integrates: `.claude/worktrees/w0-doctor/dev/doctor/cli.py`).

Pass criteria: `## Next Step` and its `Session handoff` line inside plan frame line 30 (legacy,
pretool) and present in the smart frame; the progress frame ends on the NEXT bullet while one
exists (CT-30 retires it); doctor 0 P1.
