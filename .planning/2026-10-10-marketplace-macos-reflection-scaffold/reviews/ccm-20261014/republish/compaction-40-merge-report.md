# compaction-40 merge report: auto-compaction at about 400K (autoCompactWindow 433000), doctor thresholds, frontier fraction 0.275, Opus reviewer (R-179, D189-D191)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto, Git dir
`.git`. The merger was a subagent of session `ccm-20261014` (Opus 5.5). It worked in the root
checkout and followed `roster-v2-merge-report.md`. `VIRTUAL_ENV` was unset before every command,
and every command ran from the root, one literal command per check. The merge was the literal
`git merge --no-ff` by branch name, with no `-C` (D164). Scratch files are in the session
scratchpad under `compaction-40-merge/`, outside the checkout, each named with the unit prefix.
Nothing was pushed or published, no gh write ran, and no interactive `claude` session started.

## Preflight

The root checkout was on `codex/marketplace-native-onboarding` at HEAD `7ec0a71`, with a clean
status (untracked files included), no merge, rebase, cherry-pick or revert in progress, and three
worktrees: the root, `codex-agents-fix` (`fbb341c`) and `compaction-40` (`38d5c1c`). The lane tip
`claude/compaction-40` was `38d5c1c`, as the brief said, and the merge base was `a8e3682` (the lane
merged that integration tip in `c2aa3fd`). `git merge-tree --write-tree HEAD claude/compaction-40`
returned rc 0 (clean) with tree `9e18d71`; its `.claude/settings.json` held `autoCompactWindow`
433000 and all three `env` keys (`PLAN_ID` and both roster-v2 keys).

## Changed paths

`git diff --name-only a8e3682 claude/compaction-40` lists 19 paths (+262 -92), all inside
`owned_paths`:

- `.claude/settings.json`: owned as "autoCompactWindow only"; the lane diff changes
  `autoCompactWindow` 700000 -> 433000 and no other key.
- `dev/doctor/budget.py`, `dev/test_doctor.py`, `dev/test_ticket_frontier.py`: each named in
  `owned_paths`.
- `.planning/.../frontier.toml` and `retros/compaction-40.md`: each named in `owned_paths`.
- `docs/agents/claude-team.md`: owned as "budget table and the review-model line only"; the lane
  diff changes the reviewer row (line 16, Fable -> Opus) and the Context budget section (the
  sentence naming the window and the four table rows). Nothing else in the file changed.
- Six files under each ticket-frontier skill copy (`.claude/skills/ticket-frontier/` and
  `.agents/skills/ticket-frontier/`): `SKILL.md`, `evals/evals.json`, `references/config.md`,
  `references/model-policy.md`, `references/scheduler.md`, `scripts/frontier.py`.

No path is outside. None of the 19 baseline files is touched.

## Commits

| Step | Commit | Parents | Content |
| --- | --- | --- | --- |
| R1 records | `497af7f` | `7ec0a71` | `retros/compaction-40.md` (+142), byte-identical to `38d5c1c` (blob `d5f591b`); parent edits 2, 3 and 5 in `task_plan.md`; lane record (edit 4, review disposition, retro "passed", status merge pending). 3 files +161 -9. hk `pre-commit` ran `whitespace` and `records`, both passed |
| M1 merge | `bbdf0d4` | `497af7f`, `38d5c1c` | ort, 18 files +120 -92, rc 0. hk `pre-merge-commit` printed `retro gate passed for: claude/compaction-40`. Merged tree `ff60e52`, the same as `git merge-tree --write-tree 497af7f claude/compaction-40` |
| R2 records | the commit carrying this report | `bbdf0d4` | Lane record set to integrated, the progress entry, and this report |

Byte identity: `git hash-object` on the copied retro and `git rev-parse
claude/compaction-40:<path>` both returned `d5f591b832bb36b2c8ce588d27469d292c7639d3`. Before R1,
`git diff --cached --check` returned rc 0, and `./dev/mise run retro:gate -- compaction-40` returned
rc 0 (`RETRO GATE PASSED`, selectors none) on the root with the record staged.

Tree check: the merged tree `ff60e52` differs from the dispatch prediction `9e18d71` (on
`7ec0a71`) by the non-retro files R1 edited. The retro is the same blob on both sides.

The merge message is the brief's literal title with the two session trailer lines, passed through
`-F` with a scratchpad file; R1 carries the same trailers. Writer trailers on the lane: `7213170`,
`5c2e2e9` and `6fca41d` name Claude Opus 5.5 (implementer, matching `writer_model` "opus (high)");
`0cab4ff`, `c2aa3fd` and `38d5c1c` name Claude Fable 5.1 (retro-writer).

## Review disposition

Opus 5.5 cold review (high, read-only, D189) on `6fca41d`: PASS with two P3s. Every value matches
D190 and D191, the threshold order is right, and every check exited 0.

- P3: the D191 invariant `fork_deny == int(windows[model] * fraction)` was checked for opus only.
- P3: `FABLE_KINDS` in `scripts/frontier.py` still listed `"review"`.

The retro-writer (Fable 5.1) applied both test-first in `0cab4ff` and verified them. With
`sonnet = 200000` planted in `frontier.toml`, `./dev/mise run test:doctor` returned rc 1 with the
failure naming `model='sonnet'`; reverted, rc 0 with 14 tests. With `"review"` listed,
`./dev/mise run test:frontier` returned rc 1; removed, rc 0 with 31 tests. The implementer-side P3s
the retro records (the `frontier.py` fallbacks, thresholds below `window - 33_000`) were applied
in `7213170`. The parent accepts the retro-writer's verification in place of a second cold pass,
as for roster-v2 and handoff-skills.

## Conflicts

There were none. The lane's last sync was `a8e3682`. The integration side since then (`99db493`,
`e3b2d83`, `44d0a0f`, the roster-v2 merge `3114a11`, `7ec0a71`, then R1) shares three paths with
the lane:

- `.claude/settings.json`: roster-v2 added two `env` keys; the lane changed `autoCompactWindow`.
  ort merged the adjacent hunks; `jq` on the merged file shows 433000 and all three `env` keys.
- `docs/agents/claude-team.md`: roster-v2 edit M added the scratch-file line at line 42; the lane
  changed line 16 and the Context budget section. ort merged them.
- `retros/compaction-40.md`: R1 added the same blob.

## Parent edits

The retro's "Parent edits (exact text; outside `owned_paths`)" section lists 1 to 6. Applied in R1,
each matched by text (the retro's line numbers had moved by 2):

- 2: `task_plan.md` lines 860-862, the Context budget lines, replaced by the retro's three lines
  (C4, D190, D191; warn 220 K, fork deny 275 K, checkpoint 303 K, hard 358 K, below the 400 K
  compaction point of `autoCompactWindow` 433000).
- 3: `task_plan.md` line 902, the second Models line, now reads "lanes, Opus for review (D189),
  Fable for retro and synthesis, Haiku for mechanical extraction."
- 4: `lanes/compaction-40.json` `delivers` gains the retro's three entries verbatim (the
  `max_live_agents` cap 5, the `frontier.py` fallbacks and `FABLE_KINDS`, the `scheduler.md` and
  `evals.json` entries).
- 5: `task_plan.md` line 682, the D21 row; its status cell ends with "; window superseded by D190
  (433000)".

Not applied by this merger:

- 1: applied by lane roster-v2. `grep -n "Fable reviewer" .claude/agents/frontier-scheduler.md`
  returns rc 1 (no match) on the merged tree.
- 6: runtime acceptance waits for the user's restart. See the last section.

Lane record `lanes/compaction-40.json`:

- R1 set `delivers` (edit 4), the `review` disposition, `retro` "passed", and `status` to merge
  pending.
- R2 set `status` to "integrated (merge bbdf0d4, 2026-10-14); not published; autoCompactWindow
  433000 and the doctor thresholds load at the user's restart; runtime acceptance pending (R-179
  unticked)", `head_sha` to `38d5c1c` and `integration_merge` to `bbdf0d4`.
- Eight notes were added. R1 added the retro binding, the review disposition, the changed-path
  check, the writers and the parent-edit dispositions. R2 added the integration gates with the
  scan, the worktree removal and the pending runtime acceptance.

Ticket ledger: unchanged. Open request R-179 stays unticked until the runtime receipt.

The progress entry was inserted directly above `- NEXT (`, so NEXT is still the last bullet.

## Gates

These ran after M1 (`bbdf0d4`) from 01:19:05Z (20:19 local, 2026-10-14), each alone and one after
the other:

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 69 tasks |
| `./dev/mise run check` | 0 | 31 + 91 tests; json 2333, python 247, shell 6, toml 21, `status: pass` |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run check:research` | 0 | 21 test runs, no FAILED, ERROR or traceback line; 01:20:40-01:21:55Z |
| `./dev/mise run test:doctor` | 0 | 19 tests OK |
| `./dev/mise run test:frontier` | 0 | 31 tests OK |
| `./dev/mise run test:hooks` | 0 | 27 tests OK |
| `diff -r .claude/skills/ticket-frontier .agents/skills/ticket-frontier` | 0 | no output |
| `./dev/mise run doctor` | 0 | no finding printed |
| `./dev/mise run doctor:session-start` | 0 | `context: auto-compact: user=true project=true · warn 220K · checkpoint 303K · fork_deny 275K · hard 358K` |
| `./dev/mise run retro:gate -- compaction-40` | 0 | `RETRO GATE PASSED`, selectors none |
| `git diff --check 7ec0a71` | 0 | no output |
| `grep -n "Fable reviewer" .claude/agents/frontier-scheduler.md` | 1 | no match, as expected |
| `jq .autoCompactWindow .claude/settings.json` | 0 | 433000; `env` keys `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `PLAN_ID` |
| betterleaks 1.9.0 over `7ec0a71..HEAD` through `git_delivery.scan` (so `scan_config` loads the private rule), with the absolute binary path and a JSON report reduced to counts | 0 | 8 commits (R1, M1 and the six lane commits); 0 findings, private rule 0 |

`7ec0a71` is the integration tip before R1, so the whitespace check and the scan cover R1 as well
as the merge. The root status was clean while the gates ran, so the working-tree checks read the
merged tree. The `retro:gate` and scan reruns on the final HEAD run after R2. Their results go in the
merger's handoff to the parent, not in this file.

## Stale-value grep

`git grep` over tracked files for `700000`, `700 K` and `max_live_agents = 8`:

- `700000`: 56 lines in 27 files. 26 files are planning records under the plan directory: the D21
  and D190 rows of `decisions.jsonl`, the earlier lane records `w0-docs.json` and `w0-doctor.json`,
  this lane's record (which states the 700000 -> 433000 change), `progress.md:439`, the retros of
  `ccm-20261013-session` and compaction-40, review reports under `reviews/ccm-20261013/` and
  `reviews/ccm-20261014/` (including R23 itself and the cc-2.1.300 impact files), and
  `task_plan.md` lines 130 (the ticked W0-1 item) and 682 (the D21 row, now marked superseded).
  The 27th is `evidence/vcpkg-consumers/capacity/capacity.json:57`, a float whose digits contain
  the string; it is not a window value.
- `700 K`: 8 lines in 6 files, all records: `retros/compaction-40.md` (3, quoting the old text) and
  five review reports under `reviews/ccm-20261013/`.
- `max_live_agents = 8`: 2 lines in 2 files, both records: `retros/roster-v2.md:53` and
  `reviews/ccm-20261013/phase3/I3-review.md:63`.

No live code, configuration, skill or agent document states an old value. One record reads as a
forward action: `reviews/ccm-20261014/cc-2.1.300/impact.json` asks CT-87 to keep a per-model
`/autocompact` value from overriding 700000. That window is now 433000. Whoever drafts CT-87
should use that value.

## Worktree

`.claude/worktrees/compaction-40` was at `38d5c1c`. It had no tracked or untracked changes
(ignored `.mise/`, `.venv/` and `__pycache__/` directories only), the stash list was empty, and
`git merge-base --is-ancestor claude/compaction-40 HEAD` returned rc 0. `git worktree remove
.claude/worktrees/compaction-40` (no `--force`) returned rc 0. It ran after the gates and before R2,
so the record states a fact. Branch `claude/compaction-40` stays at `38d5c1c`. The worktree and
branch `codex-agents-fix` were not touched.

## Refused, unrun, left for the parent

- No gate failed. The deny gate refused nothing during the merge.
- Runtime acceptance (retro parent edit 6) needs the user's restart, because `autoCompactWindow`
  reaches a session only when the process starts. After the restart, `/autocompact` or `/context`
  should show the 433k window. The receipt is the first non-idle auto `compact_boundary` with
  `preTokens` near 400,000, excluding "Compacted while idle" rows. R-179 stays unticked until that
  receipt.
- The doctor thresholds bind the parent at the next session start. The running session still
  uses the old 700000 window.
- CT-87: the impact record's 700000 should be read as 433000 (see the stale-value grep).
- Publishing is the parent's: nothing pushed.
- No `decisions.jsonl` row was added or changed by the merger.
