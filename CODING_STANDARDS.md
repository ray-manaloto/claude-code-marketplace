# Coding standards

Reviewer-facing judgement rules. Mechanical rules live elsewhere: `dev/check.py`, the
named `test:*` tasks in `mise.dev.toml`, the retro gate (`dev/retro_gate.py`, CT-01)
and, arriving with CT-02, the hooks. This file holds only calls an automated check
cannot make; a rule that becomes checkable moves into a check and leaves this file.

A reviewer reports each violation with its path and rule number, ordered by severity,
and names every check left unrun.

## Tests

1. A test asserts an external seam: a CLI exit code and its output, a receipt, a
   journal, a hook decision. Reject a test whose failure message names an internal
   function, field or call order that no seam observes.
2. A new behaviour arrives with a seam test that fails without it; a fixed bug arrives
   with the case that reproduced it.
3. Hermeticity, fixtures and environment selectors follow `.claude/rules/dev-tests.md`;
   reject a test that reads the real `~/.codex` or the network.

## Receipts and claims

4. A receipt binds the exact command, exit code, input paths, SHAs and hashes
   (`.claude/rules/evidence.md`). Reject wording that turns `partial`, `unrun` or a
   nonzero exit into success.
5. A claim names its tier: planned, implemented, tested, reviewed, committed or
   published. A static check supports a static claim and no runtime, provider,
   fresh-session or OCI claim.

## Public contracts

6. Preserve the marketplace identity (`ray-manaloto`), the `aggregated-research`
   plugin name, its CLI behaviour, exit statuses and data paths, the 19 baseline files
   and the generated v2 schema. A change to one needs an accepted decision that names it.

## Documentation

7. One fact has one source of truth; other documents point to it. Reject a restated
   table, command list or rule that a linked document or `./dev/mise tasks ls` provides.
8. Write the behaviour wanted in positive terms; a prohibition stays only as a guardrail
   paired with the target behaviour.
9. Every step ends on a checkable completion criterion. Reject "ensure", "verify" or
   "review" with no stated condition for done.
10. An `AGENTS.md` states what no file, config or `--help` output states. Reject a line
    that changes no agent behaviour.

## Retro findings

11. A retro finding is applied, rejected with specific evidence that it is inapplicable
    or harmful, or deferred with a named owner and admission condition; the gate
    (`dev/retro_gate.py`) checks the record's shape. A suggestion or a future ticket
    alone leaves the finding open.
12. Apply a finding in the file that owns its kind: mechanical rules in a check,
    judgement rules here, navigation in the nearest `AGENTS.md` or `.claude/rules`,
    repeated workflows in a skill, roles in `.claude/agents`.

## Scope

13. A change stays inside its lane's `owned_paths` and the unit-size limit in
    `docs/agents/codex-task-orchestration.md`. The merger checks this at integration;
    CT-02 is the mechanical owner.

## Sources

Standing workflow and preservation list:
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/completion-contract.md`.
