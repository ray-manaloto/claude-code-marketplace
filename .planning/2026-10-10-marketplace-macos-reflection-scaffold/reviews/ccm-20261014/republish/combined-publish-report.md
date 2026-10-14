# Combined A09 publish report: ten integrations after the D178 rewrite (D183; DL-212, DL-221)

Session `ccm-20261014` publisher subagent (Opus 5.5), root checkout, branch
`codex/marketplace-native-onboarding`, Git user Raymond Manaloto, 2026-10-14. Git 2.54.0 (Apple
Git-157), Python 3.15.0, betterleaks 1.9.0. `VIRTUAL_ENV` unset in every command; every command ran
from the root. Authority: D183 (row DL-234, the user's "Replace, then publish all"), operations
DL-212 (D159, scanner-betterleaks) and DL-221 (D165, a09-hook-events), D37 (one A09 publish per
integration report). Intents, message file and the pre-scan helper live in the session scratchpad
under `a09-combined/`, outside the checkout.

## Procedure

`dev/git_delivery.py` through the `delivery:*` tasks in `mise.dev.toml`:
`delivery:inspect-hooks`, then `delivery:prepare` (stages only the selected paths and prints the
index tree), then `delivery:publish` (selected-tree check in a scratch copy, the named check tasks,
the staged scan, `commit-tree` on HEAD, the outbound history scan over `<remote>..<commit>`, a
non-force `push --no-verify`, postimage check). Shape as in `a09-hook-events-merge-report.md` and
`a09-selected-tree-merge-report.md`: `gitleaks_bin` the pinned betterleaks 1.9.0, check_task
`["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`. Every scan loads the
private rule through `scan_config` (`.claude/rules/secret-scanner.md`).

Selected paths: this report and `decisions.jsonl` (the D183 row DL-234). The 112 commits
`bea3e67..f555f56` travel as ancestors; their first-parent lane merges are scanner-betterleaks
`1ee0ef4`, a09-hook-events `3d80c4b`, request-hooks `be3ede2`, request-catch `aab1a0e`, issue-scan
`ff853ab`, agy-history `e0b55a1`, a09-selected-tree `b7e0fd5`, capture-filter `403099c`, gh-guard
`1e76162` and rule-split `2181dc1`, each with its merge report in this directory. The committed copy
in P says "pending" below; the publish and verification fields are filled after the publish and
travel in the next local records commit.

## Preflight (22:4xZ-22:53Z)

| Command | rc | Result |
| --- | --- | --- |
| `git rev-parse --show-toplevel --git-dir --abbrev-ref HEAD HEAD` | 0 | root checkout, `.git`, branch `codex/marketplace-native-onboarding`, HEAD `f555f565dd044b158181e9aabe73b936a04fe259` |
| `git status --porcelain` | 0 | one unstaged path: `decisions.jsonl` (+1 row, DL-234) |
| `git ls-remote origin refs/heads/codex/marketplace-native-onboarding refs/heads/main` | 0 | `bea3e673fc75cf3410885aa56a4b797818c008f6`, `main` `6b5b092efa6bdf678815073db42f69fae3f07ab3` |
| `git merge-base --is-ancestor bea3e67 f555f56` | 0 | fast-forward |
| `git rev-list --count bea3e67..f555f56` | 0 | 112 |
| `git worktree list` | 0 | root checkout only |
| in-progress Git operation or `index.lock` in `.git` (grep) | 1 | none |
| private rule file `ls -l` (mode only) | 0 | present, `-rw-------` |
| `./dev/mise which betterleaks`; `betterleaks version` | 0; 0 | `<root>/.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`; 1.9.0 |
| scanner ignore file at the root (grep) | 1 | none |
| `plan_decide.pending()` | 0 | `DL-4`, `DL-212`, `DL-221` |
| push URL digest (`git remote get-url --push --all origin`, one URL, equal to the fetch URL) | 0 | `477a17f8…`, unchanged |
| outbound pre-scan: `git_delivery.scan(root, <betterleaks>, "--log-opts=bea3e67..f555f56", report=True)` | 0 | scan rc 0, 0 findings, private 0 |
| `./dev/mise run delivery:inspect-hooks -- inspect-hooks.json 605c68a5…` | 0 | `hook_tree_sha256=3417c0d9…`, the same digest as on `30d65a1` |

## Publish (A09)

Pending.

## Post-publish verification

Pending.
