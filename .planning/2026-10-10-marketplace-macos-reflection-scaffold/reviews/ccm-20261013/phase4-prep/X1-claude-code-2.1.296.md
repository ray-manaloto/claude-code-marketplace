# X1: Claude Code 2.1.296 review for this project

Date: 2026-10-13. Installed CLI: 2.1.296. Read-only review; no repository file was changed.

Sources: releases page (https://github.com/anthropics/claude-code/releases, covers 2.1.288 to 2.1.299), CHANGELOG raw (https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md, read 2.1.296 to 2.1.283), and code.claude.com docs for hooks, cli-reference, sub-agents, skills, settings, memory, sessions, worktrees, commands, env-vars, plugins-reference. Read the repo's `.claude/settings.json` (working tree and `HEAD`) and `.claude/agents/*.md`.

## 1. Changes that matter

**Hooks**
- "Added `onFailure: "block"` for command and HTTP hooks, so a hook that can't start or times out blocks the action." [2.1.295]. The docs say it "has no effect on Stop, SubagentStop, TaskCompleted, TeammateIdle, or async hooks" (https://code.claude.com/docs/en/hooks#block-the-action-when-a-hook-fails).
- Common input: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `effort`, `hook_event_name`; subagents add `agent_id`, `agent_type`. The transcript "may lag the current turn" (hooks).
- SessionStart `source`: `startup`, `resume`, `clear`, `compact`, `fork`. Our matcher matches these.
- PreCompact/PostCompact matchers: `manual`, `auto`. PreCompact can block; PostCompact cannot.
- Default timeouts: 600 s for command/http/mcp_tool; 30 s for prompt; 60 s for agent.
- "Improved `--debug` output for hooks: command hooks on tool calls, prompts, SessionStart and Stop now log their command, plugin, outcome and duration" [2.1.296].
- `CLAUDE_ENV_FILE`: SessionStart writes `export` lines there; each Bash command sources it first (hooks, env-file section).
- PreToolUse matches tool names. Agent `tool_input` documents `prompt`, `description`, `subagent_type`, `model` (hooks). `effort` was added to the Agent tool in 2.1.292.

**Settings**
- `autoCompactWindow` (settings); `CLAUDE_CODE_AUTO_COMPACT_WINDOW` accepts 100000 to 1000000; `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` sets the trigger percentage (env-vars).
- "Changed `/autocompact` to save the auto-compact window per model" [2.1.288].
- Precedence, highest first: managed, `--settings`, `.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.json` (settings page).

**Sub-agents**
- "Added `autoCompactWindow` to subagent frontmatter and `--agents` definitions" [2.1.296]. The fetched sub-agents page does not list it yet.
- "Changed subagents to preload at most 32 skills from the `skills` field" [2.1.296].
- "Improved `--debug` output to name unrecognized frontmatter fields in custom agent files" [2.1.296].
- Documented fields: `name`, `description`, `tools`, `disallowedTools`, `model`, `effort`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `isolation` (`worktree`), `color`, `initialPrompt`, `omitClaudeMd`, `experimental`.
- Hot reload: "When you add or edit a subagent file on disk ... the next delegation uses the updated definition, with no restart needed." Restart is still needed for a new `agents` directory, `--add-dir` directories, and `--disable-slash-commands` (sub-agents).

**Skills**
- Frontmatter: `name`, `description`, `when_to_use`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`.
- `context: fork` runs the skill in a new subagent named by `agent:` (default `general-purpose`). The subagent "doesn't see your conversation history" (skills).
- `.claude/skills/` hot-reloads. Plugin folders need `/reload-plugins` for `hooks/`, `.mcp.json`, `agents/` changes.
- "Fixed path-scoped rules and nested CLAUDE.md files not loading when Claude views a file with `cat`, `head`, `tail`, `sed -n` or `grep`" [2.1.293].
- `/skill-doctor` (v2.1.252+) shows per-skill context cost and use counts (commands).

**Sessions and resume**
- `claude -n <name>` / `--name` sets the name; `/rename [name]` renames mid-session; `claude -r <name|id>` resumes; `claude -c` continues the most recent conversation in the directory (cli-reference, sessions).
- "With no argument, the new session keeps a name you set with `--name` or `/rename`" after `/clear` (commands).
- `--fork-session` with `--resume` or `--continue` creates a new session ID. Without forking, "messages from both interleave into one transcript" (sessions).
- Resuming a session still running in the background attaches to it (sessions).
- No `CLAUDE_CODE_SESSION_ID` is documented. The ID is the `session_id` hook field.
- "Fixed `--resume` sometimes dropping files and other context that a compaction had just restored" [2.1.288].
- "Added `claude attach <name>` and `claude logs <name>`" [2.1.290].

**Plugins, memory, compaction**
- `/reload-plugins [--force]` reloads plugins without restart, also in `-p` and the SDK (commands).
- `claude plugin eval` and `/skill-doctor` are covered by the embedded reference and are available in this session.
- "Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk" (memory).
- `/doctor prompt-audit` audits CLAUDE.md, skills, agents, output styles (commands; v2.1.283+).
- `/compact [instructions]` takes focus text (commands). `SessionStart` with `source: compact` fires after compaction.

**Worktrees**
- `--worktree <name>` creates `<repo>/.claude/worktrees/<name>` on branch `worktree-<name>`. Base is the remote default unless `worktree.baseRef` is `"head"` (worktrees).
- `isolation: worktree` in subagent frontmatter uses the same base rule.
- `.worktreeinclude` copies gitignored files (such as `.env`) into worktrees Claude creates with git.
- The sweep removes old subagent and background worktrees without work. It "keeps any worktree without [a marker]", so manual `git worktree add` lanes are kept.
- `WorktreeCreate`/`WorktreeRemove` replace the default git logic; no matchers.

**Env (unattended lanes)**
- `CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS` [2.1.296] raises the 529 backoff ceiling.
- `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` [2.1.295] limits unattended retry waits. Not in the env-vars excerpt.
- `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` changes resume of a cut-off turn. Leave it unset.

## 2. Project changes

Priority: **now** = small and safe; **wave 1** = after the current wave; **later** = optional.

| # | Change | File | Exact edit | Priority | Replaces hand-rolled? |
|---|---|---|---|---|---|
| 1 | `onFailure: "block"` on Stop and SubagentStop has no effect per the docs. | `.claude/settings.json` (both entries); `dev/hooks/stop_gate.py`, `dev/hooks/subagent_stop_gate.py` | Delete the `onFailure` line from both entries. Make each gate exit 2 on internal error. Keep `onFailure` only on `PreToolUse(Bash)`. Verify with a forced crash. | **now** | No. Correctness fix. |
| 2 | Name sessions natively. | Launch command | `claude -n ccm-20261014 ...`. Keep the owner line in `task_plan.md`, because `-n` does not record ownership. | **now** | Partly. |
| 3 | Fork, do not re-resume, a dead session. | Handoff runbook | Use section 3 Option B. Never resume one ID in two terminals. | **now** | Yes, for ad hoc resumes. |
| 4 | Check hook durations and agent frontmatter. | Operator runbook | Run one session with `claude --debug` and read the duration lines for the 10 s `PreToolUse(Bash)` gate. | **now** | Replaces guessing. |
| 5 | Run `/skill-doctor` and `/doctor prompt-audit`. | Operator runbook | Run both in-session; trim rules and CLAUDE.md from the findings. | **now** | No. |
| 6 | Re-check `.claude/rules` loading after the 2.1.293 fix. | `.claude/rules/*.md` | Run one `cat` or `grep` on a path-scoped file, then check the context cost. | **now** | No. |
| 7 | Pin `PWF_PLAN_ROOT` per machine. | `.claude/settings.local.json` `env`, or the SessionStart hook writing `CLAUDE_ENV_FILE` | Keep the absolute path out of shared `settings.json`. Verify that the value reaches hooks first. | **wave 1** | Partly. Replaces the host-env pin. |
| 8 | Add `autoCompactWindow` to the implementer. | `.claude/agents/implementer.md` frontmatter | Add `autoCompactWindow: <n>` only after the docs confirm the field. Do not add `isolation: worktree`. | **wave 1** | Partly. Compacts earlier but does not block forks. |
| 9 | Decide the worktree base. | `.claude/settings.json` | Option A: `"worktree": { "baseRef": "head" }`, so `--worktree` lanes branch from local HEAD. Option B: keep manual `git worktree add` from the integration tip, which the sweep ignores. | **wave 1** (decision) | Option A replaces a manual step. |
| 10 | Keep the context-budget fork hook. | `dev/hooks/` PreToolUse on Agent | Add a margin, because the transcript may lag. Confirm the `Agent` matcher name with `--debug` first. | **wave 1** | No native equivalent for context size. |
| 11 | Retry env for unattended lanes. | Launch env | Set the two retry variables only for runs that must survive 529s. | **later** | No. |
| 12 | Plugin eval for `plugins/aggregated-research`. | `plugins/aggregated-research/evals/` | Add cases and graders per the embedded reference. Run `claude plugin eval plugins/aggregated-research --max-cost-usd <n> --json` only after trusting the plugin. | **later** | Replaces ad hoc skill checks. |
| 13 | Background lane monitoring. | Operator runbook | Use `claude agents --json` and `claude logs <name>`. | **later** | Partly. |
| 14 | `WorktreeCreate` hook for lanes. | Settings `hooks` | Only if lane creation must copy env files. `.worktreeinclude` does not apply to hook-created worktrees. | **later** | Would replace a manual copy step. |

Agent hot reload: the docs say new files in an existing `.claude/agents/` are picked up within seconds. The project's finding that they are not selectable until restart conflicts with that. Test with `/agents` after adding one file before restarting. If the conflict persists, report it with `/feedback`.

## 3. Starting a named session that resumes this project

Option A: new session, handoff read as the first prompt, no transcript carry-over.

```
cd /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace
PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold \
PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace \
claude -n ccm-20261014 "Read docs/onboarding.md, then the handoff block at the top of .planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md and section 2 of .planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261013/phase3/HANDOFF-2026-10-14.md. Continue at the Next Step."
```

Option B: full transcript of an earlier session, forked so the original is not written to. Replace `<id>` with the session ID (for example `b74a0bf1-dd98-44d5-8122-e47e12ad4fd2`).

```
claude -r <id> --fork-session -n ccm-20261014 "<same prompt as Option A>"
```

Sources: `-n` and the positional prompt (cli-reference, CLI commands table); `-r <id> --fork-session` (cli-reference; sessions, "Resume by session ID or name").

Caveats:
- Pass an ID to `-r`. A name matching more than one session opens the picker.
- Stop a session still running in the background first (`claude stop <id>`), or `-r` attaches to it.
- Resume does not restore `--settings`, `--plugin-dir`, `--mcp-config`, `--add-dir`, or `--fallback-model`. `settings.json` and `settings.local.json` are re-read. `PWF_PLAN_ROOT` lives outside shared settings, so the `export` line is required.
- Scripted: `claude -p -r <id> --fork-session --output-format json "<prompt>"` is documented for `-p --resume`. Combining `-p` with `-n` is not documented, so omit `-n` there.
- Do not use `claude -c`; it may pick a different session. Do not use `--bare`; it skips hooks and CLAUDE.md, which bypasses the gates.

## 4. Could not verify

- CHANGELOG entries for 2.1.250 to 2.1.282 were not read; the fetch truncated at 2.1.283.
- `autoCompactWindow` subagent frontmatter: in the 2.1.296 notes, not in the fetched docs.
- Whether the shared `autoCompactWindow: 700000` is per model after 2.1.288. Check with `/autocompact`.
- Whether `settings.json` `env` reaches hook subprocesses. The repo relies on `PLAN_ID` this way.
- The Agent tool's PreToolUse matcher string; the docs show fields, not the string.
- Whether `CLAUDE_ENV_FILE` persists for hooks after SessionStart; the excerpt covers only Bash and PowerShell.
- Whether `-n` combines with `-p` and `--fork-session`, and whether names must be unique.
- Deny-rule syntax for `git merge` as an alternative to the PreToolUse gate; the permissions page was not fetched.
- SessionStart input schema and PreCompact input fields; the hooks page truncated before them.
- `claude plugin eval` was not run; availability comes from the embedded reference.
