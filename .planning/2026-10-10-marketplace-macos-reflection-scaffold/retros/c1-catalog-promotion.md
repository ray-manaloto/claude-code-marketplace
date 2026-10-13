# c1-catalog-promotion retrospective — catalog-only promotion (#94)

Unit: `c1-catalog-promotion` (GitHub issue #94, "C1: Qualify affected queries
without accepting an incomplete baseline"). Worktree `.claude/worktrees/c1-catalog-promotion`,
branch `claude/c1-catalog-promotion`, lane commit `52ce420` on base `ca60871`,
test strengthening `6c09b7f`, merged with `e618243` as `7295463`. Changed
paths: `dev/research_refresh/refresh.py`, `dev/research_refresh/test_refresh.py`,
`dev/research_refresh/README.md`, `docs/research-feedback.md` (+186/−6, of
which 154 test lines; the repair added +20/−1 test lines). Delivered at the
runner boundary: a proposal promotes its catalog revision only when every
affected query is complete, nonempty, anchored and bound to the current catalog
identity; unrelated capped or incomplete queries permit a catalog-only promotion
that keeps rc 2, `fresh_snapshot_accepted=false`, the accepted full baseline
fixed and NEW/GONE suppressed; interrupted catalog/state writes roll back,
recover and retry; receipt fields `catalog_only_promotion` and
`promoted_query_drift` record the outcome. Exits (implementer, then reviewer):
91 `research_refresh` tests rc 0; `check:research` rc 0; `tasks validate` rc 0;
`check` rc 0 (31 + 91); `check:acceptance-baseline` 19/19 rc 0;
`git diff --check` rc 0; `tools:prepare`/`deps:sync` rc 0. Mutation probes:
the new tests fail when the drift approval or the empty-regression gate is
removed.

Independent Fable cold review: **PASS-with-P3**; focused re-review of the
test strengthening `6c09b7f`: **PASS for integration**. The reviewer upheld
the lane's design decision: an unrelated *empty regression* still blocks
promotion, because `docs/research-feedback.md` and
`dev/research_feedback.py` classify `empty_regression` as a promotion blocker
distinct from coverage warnings, lesson L014 says sudden empties block
candidate promotion, and spec 01 does not certify empty observations; the
ticket's "warn" reads as coverage gaps (caps, incomplete pages).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P3 | Steering: `docs/research-feedback-retro/portable-workflow.md` still said promotion requires no coverage warnings anywhere, contradicting the new runner behaviour. | Applied by the parent at `4b81b3e` (outside the lane): the guard now applies to changed queries and names catalog-only promotion with its fixed baseline, rc 2 and suppressed claims; an empty regression still blocks. |
| P3 | Automated checks: the `next` run proved drift approval only indirectly (rc 0). | Applied in `6c09b7f`: `promoted_query_drift` asserted `[]` after the first promotion, `[affected]` after a second promotion rebinding to the new catalog sha, both ids after the clean refresh, `[]` in refused modes; re-review verified. |
| P3 | Coding standards: `.claude/rules/dev-tests.md` asked for a temporary `HOME`/`CODEX_HOME` and `python3 -I`, while this suite's prior art scrubs the environment explicitly and `dev/check.py` runs `-B`. | Applied by the parent at `4b81b3e`: the rule admits both hermeticity conventions; no suite-wide rewrite needed. |

Navigation: none — the 1,500-line `refresh.py` needed two paged reads, which
is the file's size rather than a missing pointer. Global guidance: none beyond
the portable-workflow amendment above. Tool economy: applied — every check ran
once before and once after the merge. No-ops: none — every edit changed
behaviour or documentation. Information access: none — the issue, specs and
code were readable offline; no provider call was made. Integrated by the
parent with composed-tree gates `tasks validate` 52 rc 0, `check` rc 0,
`check:acceptance-baseline` 19/19 rc 0, 91 tests rc 0, `git diff --cached --check`
rc 0. #94 stays open until its tracker closure through the qualified operation.
