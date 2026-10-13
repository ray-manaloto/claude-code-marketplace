# Coding standards

Reviewer-facing judgement rules. Mechanical rules live elsewhere: `dev/check.py`, the
named `test:*` tasks in `mise.dev.toml` and, with tickets CT-01 and CT-02, the retro
gate (`dev/retro_gate.py`) and the hooks. This file holds only calls an automated check
cannot make; a rule that becomes checkable moves into a check and leaves this file.

A reviewer reports each violation with its path and the rule number, ordered by
severity, and names every check left unrun.

## Tests

1. A test asserts an external seam: a CLI exit code and its output, a receipt, a
   journal, a hook decision. Reject a test whose failure message names an internal
   function, field or call order and whose behaviour no seam observes.
2. A new behaviour arrives with a seam test that fails without it. A fixed bug arrives
   with the case that reproduced it.
3. A test is hermetic: temporary `HOME` and `CODEX_HOME`, provider responses from
   `dev/fixtures/<topic>/`, and results independent of the caller's environment
   selectors (`.claude/rules/dev-tests.md`).

## Development helpers

4. Helpers use the standard library only, run under `python3 -I`, read inputs with a
   byte or line bound, and reach neither the network nor the real `~/.codex`.
5. A helper that mutates state previews first, applies against a fresh preimage and
   verifies afterwards; an ambiguous attempt is verify-only.
6. A helper fails with a nonzero exit and a one-line cause. Silent fallback to a
   weaker behaviour is a defect.

## Receipts and claims

7. A receipt binds the exact command, exit code, input paths, SHAs and hashes. Reject
   wording that turns `partial`, `unrun` or a nonzero exit into success.
8. A claim names its tier: planned, implemented, tested, reviewed, committed or
   published. A static check supports a static claim and no runtime, provider,
   fresh-session or OCI claim.
9. A correction is a new receipt that cites the superseded one by path and SHA-256.

## Public contracts

10. Preserve the marketplace identity (`ray-manaloto`), the `aggregated-research`
    plugin name, its CLI behaviour, exit statuses and data paths, the 19 baseline files
    and the generated v2 schema. A change to one needs an accepted decision that names it.
11. A backend migration compares old and new behaviour on the same inputs and replaces
    one module at a time.

## Documentation

12. One fact has one source of truth; other documents point to it. Reject a restated
    table, command list or rule that a linked document or `./dev/mise tasks ls` provides.
13. Write the behaviour wanted in positive terms; a prohibition stays only as a guardrail
    paired with the target behaviour.
14. Every step ends on a checkable completion criterion. Reject "ensure", "verify" or
    "review" with no stated condition for done.
15. An `AGENTS.md` is a short pointer and a reason; it states what no file, config or
    `--help` output states. Reject a line that changes no agent behaviour.

## Retro findings

16. A retro finding is applied, rejected with specific evidence that it is inapplicable
    or harmful, or deferred with a named owner and admission condition. A suggestion or
    a future ticket alone leaves the finding open.
17. Apply a finding in the file that owns the kind of learning: mechanical rules in a
    check, judgement rules here, navigation in the nearest `AGENTS.md` or
    `.claude/rules`, repeated workflows in a skill, roles in `.claude/agents`.

## Scope

18. A change stays inside its lane's `owned_paths`, near five maintained files and 300
    handwritten changed lines. Shared planning files change only through the parent.
