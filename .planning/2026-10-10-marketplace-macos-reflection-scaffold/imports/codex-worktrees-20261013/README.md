# Codex worktree snapshot, 2026-10-13

A durable, hash-verified copy of files that existed only in two Codex worktrees:

- `2a14/` from `/Users/rmanaloto/.codex/worktrees/2a14/claude-code-marketplace` (HEAD `48027d2d`, detached)
- `c658/` from `/Users/rmanaloto/.codex/worktrees/c658/claude-code-marketplace` (HEAD `6130ab5e`, detached)

Under each worktree directory, `untracked/`, `modified/` and `ignored-data/` keep the
original relative paths. For each modified tracked file, `modified/` holds the working-tree
copy plus `<path>.diff` (`git diff` against that worktree's HEAD).

## Why

`reviews/ccm-20261013/SYNTHESIS.md` P1-10: tip code depends on data that exists only
untracked in the `2a14` worktree. `dev/codex_examples.py` pins
`evidence/codex-examples/release/config-schema.json` and reads `evidence/saved-searches/runs/*`,
and about 7.4 MB of A01-A09 closure evidence and three docs cited by tip retros and
`task_plan.md:322` live only there. A worktree reset or `git worktree prune` would delete them.

## Status

Nothing here is committed. This directory is untracked; a later lane decides what moves
into its real path in the repository and what stays out of Git. A private mirror with the same
content lives at `~/.local/state/marketplace-imports/codex-worktrees-20261013/` (mode 0700).
Files flagged as secrets would be copied only there; this run flagged none.

## Verify

    python3 -I verify.py            # re-hash this copy against MANIFEST.json
    python3 -I verify.py --mirror   # also re-hash the private mirror

Exit 0 means every listed file matches its size and sha256 and no unlisted file exists under
the worktree directories. `T1-snapshot-report.md` has counts, classification decisions and
the dependency table against tip `9cd396a`; `T1-dependency-scan.json` has the raw scan.
