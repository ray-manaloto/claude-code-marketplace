# Executor gate G and the adapter contract

`executor = native` is always allowed. `claude-agent` and `codex-agent` are accepted only
when `frontier.py executor-gate --executor <name> [--team] --write` reports every
applicable item PASS and writes `frontier/executor-gate.json`. Source: K1 §7, user answer
Q7 (G1–G7 accepted, G7 for team mode only), Q14 (`allow_subagents=false` until G7).

## Items

| # | Condition ("takeover work complete") | Probe |
| --- | --- | --- |
| G1 | CT-17 (`lane:allocate/integrate`), CT-19 (`lane:brief`, receipt journal), CT-22 (doctor), CT-07 (Codex compatibility) are `published` with `retro: passed` | `lane:validate` over the four records, rc 0 |
| G2 | `~/.codex/skills/{codex-agent,claude-agent,.shared/agent-protocol}` under version control with a recorded HEAD | `git -C <dir> rev-parse HEAD` rc 0 for each |
| G3 | Protocol tests, schema and codegen drift checks pass | `mise -C ~/.codex/skills/.shared/agent-protocol run test`, `schemas:check`, `codegen:check`: three rc 0 |
| G4 | Dynamic-agents tickets 01–07 integrated on `spec/dynamic-agents` and promoted (ticket 33) into the installed skills | ticket `Status: complete` lines plus `diff -r` installed vs `implementation/repo@HEAD` empty |
| G5 | A tested command (tickets 04 + 12) emits a capability snapshot for this checkout and Claude Code version | rc 0 and its test present in `run test` |
| G6 | Smoke: `dispatch:claude` with `mode: review`, `claude.mode: safe`, `workdir` = this checkout returns `status: completed`, `execution.exit_code: 0`, `result_schema.validation: passed` | envelope fields |
| G7 | Team mode only (`allow_subagents: true`): one `agent-qualify` sidecar whose `participation` verdict is `native_qualified` | sidecar field; `SKIP` without `--team` |

## Probe config

`frontier/executor-gate.config.json` (or `--config <file>`) maps each item to one probe:

```json
{"G1": {"rc": 0, "note": "lane:validate 2026-10-20"},
 "G2": {"cmd": ["git", "-C", "/Users/me/.codex/skills/.shared/agent-protocol", "rev-parse", "HEAD"]},
 "G4": {"path": "/Users/me/.codex/skills/.shared/agent-protocol/configuration-report/promoted.json"},
 "G7": {"value": "native_qualified"}}
```

`rc` records a result you obtained elsewhere (name it in `note`); `cmd` runs the command
(rc 0 passes, 120 s timeout); `path` passes when it exists; `value` passes when it equals
`expect` (default `native_qualified`). An item without a probe fails with `no probe
configured`: an absent proof is not a pass. On today's tree G2–G5 fail by construction
(K1 acceptance 4).

## Adapter contract

One module per executor, `scripts/executors/<name>.py`, selected by config only:

```
dispatch(brief_path, role, model, effort, ceiling, workdir, allow_team: bool) -> Receipt
status(run_id) -> {state, usage_total, task_status}
cancel(run_id) -> rc
Receipt = {run_id, provider, task_status, exit_code, usage: {input, output, total},
           artifacts: {transcript | native_stdout}, session_id}
```

- `native`: `dispatch` is the Agent call `frontier.py next` prints (`subagent_type`,
  `model`, `effort`, `prompt`, `run_in_background: true`); the receipt is the CT-19
  journal line. No module is needed; this is the only executor built today.
- `claude-agent`: writes a `contract_version: "2.0"` request (`task_file` = brief,
  `workdir` = worktree, `mode: implement|review`, `model`, `effort`, `timeout_s`,
  `allow_subagents: false`, `claude.agents_file` = `.claude/agents` as JSON,
  `claude.tools`), runs `mise -C ~/.codex/skills/.shared/agent-protocol run dispatch:claude
  -- <request.json>`, maps `usage.total_tokens`, `task_status`, `native.claude` onto
  `Receipt`; the ceiling check reads `usage.input_tokens` of the terminal object.
- `codex-agent`: same with `dispatch:codex` and `codex.sandbox: workspace-write`.

Each adapter lands with one fixture test on a saved envelope, in the lane that passes its
gate; until then `executor-gate` is the only thing that mentions them.
