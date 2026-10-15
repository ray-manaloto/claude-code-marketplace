# Model policy

Step kind → model and effort, the per-model windows, the ceilings they produce and the
one rule that moves a step onto Fable. Source: K1 §2 and user answers Q9, Q10
(2026-10-13); windows from the models overview on platform.claude.com fetched the same day.

## Table

| Step kind | Agent definition | Model | Effort | Window (tokens) | Ceiling at 0.275 | Rule id |
| --- | --- | --- | --- | --- | --- | --- |
| implement | `implementer` | opus | high | 1,000,000 | 275,000 | `policy.implement` |
| docs | `doc-writer` | sonnet | high | 1,000,000 | 275,000 | `policy.docs` |
| review | `reviewer` | opus | high | 1,000,000 | 275,000 | `policy.review` |
| retro | `retro-writer` | fable | high | 1,000,000 | 275,000 | `policy.retro` |
| synthesis | (parent brief) | fable | high | 1,000,000 | 275,000 | `policy.synthesis` |
| design | (parent brief) | fable | high | 1,000,000 | 275,000 | `policy.design` |
| schedule | `frontier-scheduler` | opus | high | 1,000,000 | 275,000 | `policy.schedule` |
| extraction | `extractor` | haiku | low | 1,000,000 | 275,000 | `policy.extraction` |

Pass `model` and `effort` as the Agent tool's per-invocation parameters: the docs
(code.claude.com/docs/en/sub-agents, "Model resolution order") list the per-invocation
`model` first and say the `effort` parameter "overrides the `effort` field" for non-fork
subagents, so the agent file's frontmatter is the floor, not the decision. The ceiling is
per lane because "a subagent's context window is sized by its own model, not the parent's".

## Fable only when Opus cannot

A step runs on Fable iff one of:

- (a) its kind is `retro`, `synthesis` or `design` (`policy.<kind>`);
- (b) the unit's receipt journal holds ≥ `escalate_after_partial` (1) lines with
  `agent_type: implementer`, `model: opus`, `task_status ∈ {partial, blocked}` and
  `reason: reasoning` (`escalation`); reasons `admission`, `conflict` and `ceiling` never
  escalate, because they are not reasoning failures;
- (c) the ticket carries the `design` class (`class.design`).

`frontier.py next --journal <file>` applies (b); every plan receipt and `next` output
records `{step, model, effort, rule}` so the doctor detector `F.model-policy-violation`
(CT-22) can compare journal `model` fields against the receipt. Cost is the other reason:
Fable lists at $10/$50 per MTok against Opus's $4/$20 on the models overview.

## Thresholds

`context_ceiling_fraction × windows[model]` must equal `dev/doctor/budget.py`'s `fork_deny`
once CT-22 exists; `plan` refuses on a mismatch so there is one threshold source. The
dict is `warn 220 K, checkpoint 303 K, fork_deny 275 K, hard 358 K` (D190, D191), all
below the point where the project `autoCompactWindow 433000` compacts (about 400 K). The
brief line checkpoints at 80 % of the ceiling (220 K at 275 K).
