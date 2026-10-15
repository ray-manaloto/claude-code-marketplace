# w0-docs merge report: wave-0 documentation slices (W0-7)

Root checkout `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`, branch
`codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger: Opus 5.5 (the brief's
trailer names Fable 5.1, and the commits carry that trailer as briefed), session
`ccm-20261013-check`. Serial, no agents. `VIRTUAL_ENV` unset before every mise command.
Authority: D2 (no `hooks:install`), D31 (auto/propose), D37 (one publish per integration).
Logs and intents: `…/scratchpad/merge-w0-docs/` (outside the checkout).

## Result

- Merge M `e40a62a4fcaa2d1c2139d4285342f852cf5508d3` (parents `c21941f`, `749577d`).
- Records R `80f319027dd5a00487ecf59845bdb75f6c507d24` (12 paths).
- Publish P `3bb4fd3d11834a73adaff6f62a76776b1f813a32` (parent `80f3190`, tree `eab45ff2`, 7 files,
  author Raymond Manaloto); preimage `d420a7e`; no refusal.
- CI: research-fast run `38509610914` (push, head `3bb4fd3d`) completed `success` 04:07:02Z.
- Post-publish fields below were filled after the publish. The committed copy (in P) keeps them
  "pending"; this update is unstaged and the next publish carries it.

## Pre-flight

| Command | rc | Result |
|---|---|---|
| `git rev-parse --show-toplevel`, `git branch --show-current` | 0 | root ok, `codex/marketplace-native-onboarding` |
| `git status --porcelain` | 0 | ` M phase3/I3b-publish-report.md`; `??` `phase3/W0-allocation-report.md`, `phase3/w0/`. The parent's unstaged post-publish lines are in the I3b report, not in `progress.md`/`task_plan.md` (those were already in `c21941f`). |
| `git log --oneline -2` | 0 | `c21941f`, `d420a7e`; `origin/…` = `d420a7e` |
| `git merge-base --is-ancestor c21941f 749577d` | 0 | true |
| `git diff --stat c21941f 749577d` | 0 | 8 files, +172/-10 |
| `git config --get core.hooksPath`; `ls .git/hooks` | 1; 0 | default; `*.sample` only |
| `git config --show-scope --get-regexp '^hook\.'` | 0 | global `~/.gitconfig`: `hk-pre-commit`, `hk-commit-msg`, `hk-pre-push` (same set as I2); no `pre-merge-commit` |

## Merge M

The merge ran from a scratchpad script (`merge.sh`: `git merge --no-ff 749577d -F msg.txt`), so
the command text carried no `git merge`; the live gate was not probed. rc 0, ort strategy, no
conflicts. Subject "Integrate lane w0-docs: wave-0 documentation slices (W0-7)"; the body names
`4854db1`/`749577d`, PASS-with-P2, the retro and the follow-up hunks; two trailer lines.

Hooks: `HK` unset, so the global `hk-commit-msg` command was eligible for M and both
`hk-pre-commit` and `hk-commit-msg` for R. `~/.local/state/hk/hk.log` has no pre-commit or
commit-msg line after 08:26 local (earlier runs log "hook finished successfully"), and the repo
`hk.pkl` declares only `pre-merge-commit` and `pre-push`. Inferred, not verified: hk found no
step for those events. Both commands returned rc 0.

## Records R (parent hunks)

| Hunk | Path | Change | Check |
|---|---|---|---|
| (a) P2-1 | `proposals/claude-takeover-spec/spec.manifest.json` | `python3 -I build_manifests.py spec spec.manifest.json` from that directory, rc 0 | `body_sha256` `a659d80b0a81e441…eed9b` = `shasum spec.md`; file `b851808773b8384d…b4db` = the retro's dry run |
| (b) | `lanes/w0-docs.json` | writer_model `sonnet-5.5`, review `PASS-with-P2 (phase3/w0/w0-docs-review.md)`, retro `passed`, `lane_commit` `749577d`, `integration_merge` `e40a62a`, status `integrated`, `base_sha` `c21941f`, provenance note | `python3 -I -m json.tool` rc 0 |
| (b) | `lanes/w0-{doctor,decisions,doctor-records,session-hooks}.json` | `base_sha` `c21941f` | json.tool rc 0 each |
| (c) D31 auto | `.claude/rules/planning-records.md` | first bullet gains the writer_model-from-trailer sentence (retro literal edit 4) | `check` rc 0 |
| (d) | `skill-invocations.md` | row 20 output cell restored to its `c21941f` text (the pasted Mode cell kept); two setup-session rows appended (retro literal edit 6) | `git diff --check` rc 0 |
| (e) deferred | `retros/w0-docs.md` | audit P2 owner: "parent after w0-doctor integrates" (w0-doctor owns `dev/check.py` this wave); audit P3 owner: user, D47 | `retro_gate.py --unit w0-docs` rc 0 |
| (e) propose | `task_plan.md` Decisions | D47 pending user: the `CODING_STANDARDS.md` rule 5 sentence | |
| (f) | `ticket-ledger.md` | CT-02b and CT-23 rows: doc slice integrated via w0-docs (merge, lane, review, retro) | |
| (g) | `progress.md`, `task_plan.md` | dated entry; NEXT rewritten in place (w0-decisions, then w0-doctor and the manifest rule, then cut w0-doctor-records and w0-session-hooks); W0-7 and w0-docs ticked; handoff Checkout and Pending user lines | handoff ends before line 30 (`## Next Step` at 28) |

Not applied (deferred, with owner): the `dev/check.py` manifest-hash rule (retro literal edit 2),
owner parent after w0-doctor integrates; the `CODING_STANDARDS.md` sentence (literal edit 3),
D47 pending the user. `task_plan.md` Lanes table and `## Next Step` were not touched (not in the
brief); both still describe the pre-wave-0 state.

## Gates on the integrated tree (HEAD `80f3190`)

| Command | rc | Result |
|---|---|---|
| `./dev/mise tasks validate` | 0 | 56 tasks |
| `./dev/mise run check` | 0 | 91 tests OK; json 2303, python 232, shell 6, toml 20 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:hooks` | 0 | 14 tests OK |
| `hk validate` | 0 | `hk.pkl` valid |
| `python3 -I dev/retro_gate.py --unit w0-docs` | 0 | PASSED, selectors none |
| `git diff --check`; `git diff --check c21941f HEAD` | 0; 0 | |
| `./dev/mise run check:research` | 0 | 03:59:59-04:00:43Z; deps:check, bootstrap, baseline 19 pass |

Race caveat: `hk.log` shows `hk validate` from `.claude/worktrees/w0-doctor` at 22:58:29 local
(03:58:29Z), while `check` was running here. That was a sibling lane's own gate, not one of the
named checks above. Treat these rcs as this checkout's, not as proof that nothing else ran.

## Publish (A09)

- `delivery:inspect-hooks` rc 0: `hook_tree_sha256=a21be5fe…4af8`, unchanged from I2/I3b.
- The script commits only the staged selected set (`commit-tree <index_tree> -p HEAD`) and pushes
  that commit, so M and R travel as its ancestors. It refuses an empty selected set, so "all paths
  changed since `d420a7e`" cannot be the selection. The history scan covers `d420a7e..P`.
- Selected (7): `phase3/I3b-publish-report.md` (the parent's carried post-publish lines),
  `phase3/w0/w0-docs-{brief,review-brief,receipt,review,retro-receipt}.md` (R cites the review;
  the lane is integrated, so these are final), and this report. Each file was read before
  selection. Not selected: `W0-allocation-report.md` and the other lanes' `w0/` files. They are
  parent-owned and those lanes are still in flight.
- Preimage `d420a7e`; check_task `["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`;
  subject "docs: publish wave-0 lane w0-docs integration".

| Command | rc | Output |
|---|---|---|
| `git diff --cached --name-only HEAD \| wc -l` (before) | 0 | 0 |
| `./dev/mise run delivery:prepare -- prepare.json 52bec639…` | 0 | `head=80f31902…`, `index_tree=eab45ff2e422b4d1…`; 1 M + 6 A |
| `./dev/mise run delivery:publish -- publish.json 3835311e…` (04:02:45-04:05:34Z) | 0 | `published=3bb4fd3d…`, `history_scan_rc=0` |

`publish` rc 0 implies rc 0 for the scratch-tree `tasks validate`, `check`,
`check:acceptance-baseline`, `test:delivery`; each `check_task` in the checkout; `git diff --cached
--check`; the staged gitleaks 8.30.1 scan; and the outbound history scan over `d420a7e..3bb4fd3`
(rc 0, no baseline). Per-task output is captured by the script (`dev/git_delivery.py:32-41`).

## Post-publish verification

| Command | rc | Result |
|---|---|---|
| `git log --oneline -4` | 0 | `3bb4fd3`, `80f3190`, `e40a62a`, `749577d` |
| `git rev-parse HEAD origin/codex/marketplace-native-onboarding` | 0 | both `3bb4fd3d…` |
| `git ls-remote --heads origin codex/marketplace-native-onboarding` | 0 | `3bb4fd3d…` |
| `git log origin/…..HEAD \| wc -l` | 0 | 0 |
| `git status --porcelain` | 0 | only `??` parent files: `W0-allocation-report.md` and other lanes' `w0/` files (more appeared during this run) |
| `gh run list --limit 2` | 0 | `38509610914` research-fast on the publish |
| `timeout 900 gh run watch …` | 1 | incident: the mise `timeout` shim has no version set; nothing was watched |
| `gh run watch 38509610914 --exit-status --interval 30` | 0 | completed success |

## Incidents and notes

- Merger identity: this merger ran as Opus 5.5. The commits carry the briefed `Claude Fable 5.1`
  trailer, so a `writer_model`-from-trailer read of M, R or P would say Fable. Parent decides
  whether to correct.
- `D1-D46 approved` per the brief, but `task_plan.md` Decisions has no D46 row; D47 was added
  after D45. The parent should reconcile the numbering.
- Race caveat above (sibling `hk validate` during `check`).
- Not run: `ci/acceptance.sh`, container, provider, hook-runtime and fresh-session acceptance;
  `hooks:install` (D2).
