# D196 A09 publish report: five integrations before the restart (D196; DL-249)

Session `ccm-20261014` publisher subagent (Opus 5.5), root checkout, branch
`codex/marketplace-native-onboarding`, Git user Raymond Manaloto, 2026-10-14 local (2026-10-15
UTC). Git 2.54.0 (Apple Git-157), Python 3.15.0, betterleaks 1.9.0. `VIRTUAL_ENV` unset in every
command; every command ran from the root. Authority: D196 (row DL-249, the user's "Publish now"):
one A09 publish of the local commits through `./dev/mise run delivery:*`, before the session
handoff. Intents, message file and the pre-scan helper live in the session scratchpad under
`a09-d196/`, outside the checkout, adapted from copies of `a09-combined/` (left unchanged).

## Procedure

`dev/git_delivery.py` through the `delivery:*` tasks in `mise.dev.toml`, as in
`combined-publish-report.md`: `delivery:inspect-hooks`, then `delivery:prepare` (stages only the
selected path and prints the index tree), then `delivery:publish` (selected-tree check in a scratch
copy, the named check tasks, the staged scan, `commit-tree` on HEAD, the outbound history scan over
`<remote>..<commit>`, a non-force `push --no-verify` of `<commit>:refs/heads/<branch>`, postimage
check). `gitleaks_bin` the pinned betterleaks 1.9.0, check_task
`["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`. Every scan loads the
private rule through `scan_config` (`.claude/rules/secret-scanner.md`).

Selected path: this report only. The 72 commits `9422625..c726096` travel as ancestors: 37 on the
first-parent line (5 lane merges and 32 records commits) and 35 reached through the merges. The
first-parent lane merges, each with its merge report in this directory:

| Merge | Lane | Merge report |
| --- | --- | --- |
| `4726121` | handoff-script (R-175) | `handoff-script-merge-report.md` |
| `696e03f` | ct35a-session-start-mod (CT-35, D103, D186, D187) | `ct35a-session-start-mod-merge-report.md` |
| `a8e3682` | handoff-skills (R-175) | `handoff-skills-merge-report.md` |
| `3114a11` | roster-v2 (D189, R-177) | `roster-v2-merge-report.md` |
| `bbdf0d4` | compaction-40 (R-179, D189-D191) | `compaction-40-merge-report.md` |

The records commits carry the previous publish's receipts (DL-235, DL-236 for `9422625`), the
intake of R-175..R-177 (`562094f`) and R-179..R-182 (`ac7e787`), decisions D184-D196 (ledger rows
DL-237..DL-249), the lane allocations, retros and integration records for the five lanes, the
2.1.300 release intake analysis (R-176), the R12c roster refresh and the R23 and R24 research
reports. The lane worktree `codex-agents-fix` (branch `claude/codex-agents-fix`, reopened in
`c726096`) is not part of the publish: the push names only the integration branch. The copy
committed in P says "pending" in the Publish and Post-publish sections; their fields are filled
after the publish and travel in the next local records commit.

## Preflight (01:33Z-01:35Z)

| Command | rc | Result |
| --- | --- | --- |
| `git rev-parse --show-toplevel --git-dir --abbrev-ref HEAD`; `git rev-parse HEAD` | 0; 0 | root checkout, `.git`, branch `codex/marketplace-native-onboarding`, HEAD `c72609675332de687f544160c566fb391391390e` |
| `git status --porcelain` | 0 | clean |
| `git ls-remote origin refs/heads/codex/marketplace-native-onboarding refs/heads/main` | 0 | `9422625fba1f67cca8f03c404f14f518f3674d0b`, `main` `6b5b092efa6bdf678815073db42f69fae3f07ab3` |
| `git merge-base --is-ancestor 9422625 HEAD` | 0 | fast-forward |
| `git rev-list --count 9422625..HEAD` | 0 | 72 |
| `git worktree list` | 0 | root checkout and lane worktree `codex-agents-fix` (`6d55ed4`, branch `claude/codex-agents-fix`); untouched |
| in-progress Git operation or `index.lock` in `.git` (grep) | 1 | none |
| private rule file `ls -l` (mode only) | 0 | present, `-rw-------` |
| `./dev/mise which betterleaks`; `betterleaks version` | 0; 0 | `<root>/.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`; 1.9.0 |
| scanner ignore file at the root (grep) | 1 | none |
| `plan_decide.pending()` | 0 | `DL-4` |
| push URL digest (`git remote get-url --push --all origin`, one URL, equal to the fetch URL) | 0 | `477a17f8…`, unchanged |
| outbound pre-scan: `git_delivery.scan(root, <betterleaks>, "--log-opts=9422625..c726096", report=True)` | 0 | scan rc 0, 0 findings, private 0 |
| `./dev/mise run delivery:inspect-hooks -- inspect-hooks.json d7f5e3b6…` | 0 | `hook_tree_sha256=3417c0d9…`, the same digest as on `f555f56` |

## Publish (A09)

Pending.

## Post-publish verification

Pending.

## Receipts

DL-249 (D196) is a decision row; `plan_decide.py receipt` closes open operation rows only, so the
publish is recorded by this report and the local records commit that follows it.
