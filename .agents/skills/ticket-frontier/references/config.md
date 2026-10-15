# Configuration, state and formats

## `frontier.toml` (parent-owned, `.planning/<PLAN_ID>/frontier.toml`)

| Key | Default | Meaning |
| --- | --- | --- |
| `schema` | 1 | format version |
| `max_parallel` | 3 | writer lanes (`implementer`, `doc-writer`) at once; other roles uncounted |
| `max_live_agents` | 5 | hard cap on every claim (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6` refuses a 7th spawn with an error that says not to retry; 5 leaves a slot for a fork or a resume) |
| `always_active` | `["cxx"]` | classes that hold the first slot while a member is ready |
| `context_ceiling_fraction` | 0.275 | lane ceiling = `windows[model] × fraction`; must equal `budget.py` `fork_deny` (CT-22) |
| `executor` | `native` | `native`, `claude-agent`, `codex-agent`; non-native needs the executor gate |
| `retro_apply` | `auto` | `auto` or `propose`; learning-ledger.md lists what is always `propose` |
| `publish_batch` | `per-integration` | or `per-wave` |
| `check_lock` | true | refuse a merger while CT-11's check lock is held |
| `[classes.<name>]` | | `spec`, `include` (ids and `#a-#b` ranges), `heavy`, `order`, `offline_split` |
| `[windows]` | 1,000,000 each | tokens per model |
| `[model_policy]` | model-policy.md | `<kind> = {model, effort}`; `escalate_after_partial` |
| `[hot_paths] paths` | R8 list | a candidate may touch at most one |
| `[waves]` | empty | `"#21" = 2` style tie-break |

Changing this file is a `propose` item: the retro-writer writes the hunk, the user says
yes, the parent applies it.

## Graph JSON (`ticket-ledger.json` from CT-05, or `--graph`)

```json
{"schema": 1, "source": "…", "tickets": [
  {"id": "#21", "title": "…", "state": "open", "parent": "#11", "blockedBy": [],
   "owned_paths": ["optional/paths/"], "wave": 2}]}
```

`id` accepts `#21`, `21`, `CT-25`; `state` is `open` or `closed` (also `done`, `merged`);
`blocked_by` is accepted for `blockedBy`. Anything else is ignored.

## `frontier/state.json`

```json
{"schema": 1,
 "claims": {"21-offline": {"ticket": "#21", "role": "implementer", "owned_paths": ["…"], "class": "cxx",
                           "claimed_at": "2026-10-20T10:00:00Z", "status": "claimed"}},
 "history": [{"ts": "…", "event": "claim|release", "unit": "…", "ticket": "…"}],
 "updated_at": "…"}
```

`status` is `claimed` or `split-required`. A `continuations` map holds released
`split-required` lanes (`ticket`, `role`, `last_usage`, `owned_paths`, `released_at`)
until a writer claims the same ticket again. `answers.jsonl` holds plain-text user answers
(`ts`, `question`, `answer`) recorded with `frontier.py answer` until CT-24's
`decisions.jsonl`; an answer never grants an admission by itself. The script writes
nothing outside `.planning/<PLAN_ID>/frontier/`; `status`, `plan` without `--write` and
`next` are read-only, so the SKILL.md status line is safe during a merge. Timestamps are
UTC.

## Plan receipt (`frontier/plan-<utc>.json`, written by `plan --write`)

`ts`, `graph_source`, `thresholds` (`ceiling`, `model`, `fork_deny` when CT-22 exists),
`priority_rules`, `ready` (per ticket: `critical_path`, `unblocks`, `class`,
`always_active`, `wave`, `heavy`), `ready_order`, `done`, `held`, `claimed`,
`continuations`, `capacity`, `cxx_slot`, `chosen` (`unit`, `ticket`, `role`, `split`,
`rule`), `skipped`, `conflicts`, `questions`, `degraded`.

## `next` output

`unit`, `ticket`, `role`, `model`, `effort`, `rule`, `ceiling`, `brief_lines`,
`brief_source`, `dispatch` (the Agent tool parameters), `then` (the claim and allocate
commands), `questions`, `cxx_slot`, `degraded`.

## Exit codes

0 ok; 2 refusal, reason on stdout prefixed `REFUSED:` (threshold mismatch, missing graph,
double claim, path conflict, capacity, split-required, failing gate, invalid ledger row);
1 usage error on stderr.

## Degraded mode

`status` prints one line per missing prerequisite in the form `not available yet: CT-nn
(<artifact>) -> <fallback>` for CT-05 (`ticket-ledger.json`), CT-15
(`dev/plan_records.py`), CT-17 (`dev/lane.py allocate`), CT-19 (`dev/lane_brief.py`),
CT-22 (`dev/doctor/budget.py`) and CT-24 (`decisions.jsonl`). `plan` and `next` carry the
same map under `degraded`. The loop runs on the fallbacks; nothing waits for the ticket.
