# Learning ledger

`.planning/<PLAN_ID>/frontier/learning-ledger.jsonl`: one line per applied, rejected or
deferred retro finding, appended by the retro-writer (or the parent for `propose` items the
user accepted). `retro:gate` checks the record's shape; the ledger makes the destination
and the trigger queryable so the same lesson landing twice is noticed: a repeat becomes a
failing check (D2 §2.10, "repeat mistakes become failing checks"). Rows cite the retro
row; the retro is not copied. Source: K1 §6, user answers Q5 and Q13.

## Row

```json
{"ts": "2026-10-20T12:00:00Z", "ticket": "CT-11", "unit": "ct11-check-lock",
 "category": "automated checks", "finding_id": "F2", "kind": "mechanical",
 "destination": "dev/check.py", "mode": "auto",
 "verification": {"cmd": "./dev/mise run check", "rc": 0},
 "retro_row": "retros/ct11-check-lock.md#F2", "applied_by": "retro-writer"}
```

| Field | Values |
| --- | --- |
| `category` | one of the seven retro categories (`docs/agents/ticket-retro.md`) |
| `kind` | `mechanical`, `judgement`, `navigation`, `workflow`, `role`, `hook` |
| `destination` | the path the finding changed (or would change, for `propose` and rejected rows) |
| `mode` | `auto` or `propose` |
| `verification` | `{cmd, rc}`; a rejected or deferred row records the command that showed it inapplicable, or `rc: null` with the deferral owner in `retro_row` |
| `retro_row` | `retros/<unit>.md#<row id>` |
| `applied_by` | `retro-writer`, `parent` or `user` |

`frontier.py ledger append --row '<json>'` validates the shape and adds `ts`;
`frontier.py ledger list --by destination|ticket|kind|mode` groups rows and flags a
destination with more than one row as `repeat`.

## Destination routing (`CODING_STANDARDS.md` rule 12)

| Kind | Destination |
| --- | --- |
| mechanical | a `dev/check.py` rule or `dev/test_*.py` plus a wired `test:*` row |
| judgement | `CODING_STANDARDS.md` |
| navigation | nearest `AGENTS.md`, or a `paths:`-scoped `.claude/rules/*.md` |
| workflow (repeated) | a skill under `.claude/skills/` with its `.agents/skills/` mirror |
| role | `.claude/agents/*.md` |
| hook | `dev/hooks/` plus a settings hunk |

## `auto` versus `propose`

`retro_apply = "auto"` lets the retro-writer apply, inside the lane and verified by
`check` and `retro:gate`: anything inside the lane's `owned_paths`; new tests and their
task rows; the nearest directory `AGENTS.md` pointer line; a `.claude/rules/*.md` scoped to
the lane's paths; `references/` files of a skill the lane owns; the ledger line itself.

Always `propose` (a literal hunk in the handoff, applied by the parent after the user says
so), whatever `retro_apply` says: root `AGENTS.md`/`CLAUDE.md` and `.claude/AGENTS.md`;
`.claude/settings.json` hooks and `hk.pkl`; `.claude/agents/*.md` frontmatter (`model`,
`effort`, `permissionMode`, `tools`); `CODING_STANDARDS.md` rule additions or deletions;
`dev/check.py` rules that widen a refusal set; `.planning/<PLAN_ID>/frontier.toml`; the 19
frozen baseline files; any `docs/accepted-decisions.md` supersession.

The session-level `/mattpocock-skills:retro` stays user-typed per build window; its picks
enter as one gated `retro-writer` lane and the same ledger. After the retro-writer
returns, `doctor --surface integrate --unit <unit> --json` (CT-22) runs before the merger;
a P1/P2 sends the lane back to the retro step, not to the parent's judgement.
