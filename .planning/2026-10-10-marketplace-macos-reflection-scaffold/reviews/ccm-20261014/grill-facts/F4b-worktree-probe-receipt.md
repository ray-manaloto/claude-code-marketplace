# F4b: worktree pin probe receipt (2026-10-14, grill round 3 Q44 "Write and probe now")

Session `ccm-20261014`. Claude Code 2.1.299. Throwaway repository in the session scratchpad
(`scratchpad/wtprobe/main`) with a linked worktree at `.claude/worktrees/probe`, the same layout
as this repository. Tracked `.claude/settings.json` holds a SessionStart hook (appends
`PROBE_ENVFILE` to `CLAUDE_ENV_FILE`) and a PreToolUse hook that logs event, tool, agent id, `$PWD`,
input `cwd` and three probe variables. The main root's untracked `.claude/settings.local.json`
(listed in `.git/info/exclude`, absent from the worktree) sets `env.PROBE_LOCAL`; the launch
environment (`env -i`, nothing inherited from this session) sets `PROBE_SHELL`.

Command, run from the worktree: `claude -p <probe prompt> --permission-mode bypassPermissions
--max-turns 12 --output-format json`: rc 0, result success, 8 turns, cost USD 0.72. The prompt ran
one Bash command and one `isolation: worktree` Agent that ran one Bash command.

| Probe | Hooks (SessionStart, PreToolUse, main and subagent) | Bash (main and subagent) |
|---|---|---|
| `PROBE_LOCAL` from the main root's local settings | present in all 9 hook lines | present |
| `PROBE_SHELL` from the launch environment | present in all 9 | present |
| `PROBE_ENVFILE` via `CLAUDE_ENV_FILE` | absent in all 9 | present |
| Subagent hook `$PWD` and input `cwd` | the subagent's own worktree `.claude/worktrees/agent-<id>` | same |

Conclusions: a separate session started inside a linked worktree reads the main checkout's local
settings `env`, and a worktree-isolated subagent's hooks get it too, so the `PWF_PLAN_ROOT` pin
reaches every hook; without the pin, pwf would resolve the subagent's own worktree (its `cwd`).
`CLAUDE_ENV_FILE` reaches only Bash, never hooks, so it cannot carry pwf's pins (CT-37 drops that
route). Hook log: `F4b-probe-hooks.log` (SHA-256 `a30d524c891f799aae11bec08f9d1449184355307c5ca875d291e6207af7dbed`). The probe repository stays in the
scratchpad and was never pushed.

Pins written to this repository's `.claude/settings.local.json` `env` (untracked, excluded):
`PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`,
`PWF_TRUSTED_PYTHON=/usr/bin/python3` (root-owned, 3.9.6, passes the 3.8 floor). Backup of the
previous file: `scratchpad/backup-20261014/settings.local.json.before-pins`. They take effect in the
next session.
