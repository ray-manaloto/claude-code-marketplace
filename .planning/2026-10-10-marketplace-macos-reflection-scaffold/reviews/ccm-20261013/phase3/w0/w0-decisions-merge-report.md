# w0-decisions merge report: decisions ledger seed (CT-24, W0-6)

Root checkout `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`, branch
`codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger: Opus 5.5 (the commits
carry the briefed `Claude Fable 5.1` trailer), session `ccm-20261013-check`. Serial, no agents.
`VIRTUAL_ENV` unset before every mise command. Authority: D2 (no `hooks:install`), D31
(auto/propose), D37 (one publish per integration). Logs and intents:
`…/scratchpad/merge-w0-decisions/` (outside the checkout).

## Result

- Merge M `c7054fd24c39de6460d8c948c4c2df35d7104c02` (parents `3bb4fd3`, `922eab4`).
- Records R `ecc0ad7ffd17f656337ffc247d1fa55647892d53` (6 paths; amended once before publish from
  `aaa585a`, see Incidents).
- Publish P: pending (filled after the publish; the committed copy keeps "pending").
- CI: pending.

## Pre-flight

| Command | rc | Result |
|---|---|---|
| `git rev-parse --show-toplevel`, `git branch --show-current` | 0 | root ok, `codex/marketplace-native-onboarding` |
| `git status --porcelain` | 0 | ` M phase3/w0/w0-docs-merge-report.md` (previous merger's post-publish fields); `??` `phase3/W0-allocation-report.md` and `phase3/w0/` files of four lanes |
| `git log --oneline -2` | 0 | `3bb4fd3`, `80f3190`; `origin/…` = `3bb4fd3` |
| `git merge-base --is-ancestor c21941f 922eab4` | 0 | true |
| `git merge-tree --write-tree HEAD 922eab4` | 0 | clean |
| lane diff `3bb4fd3...922eab4` | 0 | 4 files, +336: `dev/plan_decide.py`, `dev/test_plan_decide.py`, `P/decisions.jsonl`, `P/retros/w0-decisions.md` |

## Merge M

Run from a scratchpad script (`merge.sh`: `git merge --no-ff 922eab4 -F msg.txt`), rc 0, ort, no
conflicts. Subject "Integrate lane w0-decisions: decisions ledger seed (CT-24, W0-6)"; the body
names `7649ca7`/`f9c8848`/`922eab4`, both PASS-with-P3 verdicts, the retro, the follow-up hunks
and the deferrals; two trailer lines.

## Records R (parent hunks)

| Hunk | Path | Change |
|---|---|---|
| (a) | `task_plan.md` | D46 row after D45 (retro literal edit 1), so DL-50's `source` resolves |
| (b) D31 auto | `dev/AGENTS.md` "Writing a helper" | the two bullets (retro literal edit 3): exit codes 0/1/2; `mise run <task> -- <argv>` vs `usage` variadics. Ownership checked: `dev/AGENTS.md` is in no `lanes/w0-*.json` `owned_paths` |
| (c) deferred | `retros/w0-decisions.md` | automated-checks row owner: "parent at the w0-doctor integration (w0-doctor owns `mise.dev.toml` this wave)"; closing "Integration disposition" paragraph for edits 1-5. `mise.dev.toml` not touched |
| (d) propose | `task_plan.md` Decisions | D48 pending user: CODING_STANDARDS rule 14 (retro literal edit 4) |
| (e) record only | none | `issue-tracker.md` ledger sentence stays with wave-1 CT-24 (retro and disposition paragraph) |
| (f) | `lanes/w0-decisions.json` | `writer_model` `opus-5.5` (trailers of `7649ca7`, `f9c8848`), review and `rereview` paths with SHAs, retro `passed`, `lane_commit` `922eab4`, `integration_merge` `c7054fd`, status `integrated`, provenance note. `python3 -I -m json.tool` rc 0 |
| (g) | `ticket-ledger.md` | CT-24: integrated (seed) via w0-decisions; mise rows deferred to w0-doctor integration |
| (h) | `progress.md`, `task_plan.md` | dated entry; NEXT rewritten in place (w0-doctor, then the deferred mise rows and the w0-docs `dev/check.py` manifest rule, then cut w0-doctor-records and w0-session-hooks); W0-6 and lane ticked; handoff Checkout and Pending user lines (handoff ends before line 30) |

## Gates on the integrated tree

HEAD `aaa585a` unless noted; 04:10:45-04:13:08Z.

| Command | rc | Result |
|---|---|---|
| `./dev/mise tasks validate` | 0 | 56 tasks |
| `./dev/mise run check` | 0 | 91 tests OK; json 2303, python 234, shell 6, toml 20 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:hooks` | 0 | 14 tests OK |
| `python3 -I -m unittest discover -s dev -p test_plan_decide.py` | 0 | 5 tests OK |
| `hk validate` | 0 | `hk.pkl` valid |
| `python3 -I dev/retro_gate.py --unit w0-decisions` | 0 | PASSED, selectors none |
| `git diff --check`; `git diff --check 3bb4fd3 HEAD` | 0; 0 | |
| `./dev/mise run check:research` | 0 | 04:12:23-04:13:08Z; bootstrap pass, baseline 19 pass |
| After the amend (HEAD `ecc0ad7`): `check`; `git diff --check 3bb4fd3 HEAD`; `retro_gate.py --unit w0-decisions` | 0; 0; 0 | |

Race check: `~/.local/state/hk/hk.log` shows the w0-doctor worktree's `hk validate` at 04:09:00Z,
before these gates; no sibling entry falls inside 04:10:45-04:13:08Z. No named check was rerun for
a race. hk.log records only hk runs, so this does not prove nothing else ran.

## Publish (A09)

Pending; filled below after the publish.

## Incidents and notes

- R amended before publish: the D48 row first said "36 of 46" retro records carry U+2014 (the
  retro's count); the focused re-review counts 35 after the retro's own rewrite. One cell changed
  (`git diff --stat aaa585a ecc0ad7`: 1 file, 1/1); `check`, `diff --check` and the retro gate
  were rerun on `ecc0ad7`.
- Unit size: `dev/plan_decide.py` has 83 non-blank lines against C4's 80. Both reviews accepted
  it without a split; the parent did not ask for one.
- Merger identity: Opus 5.5 ran this merge; M and R carry the briefed Fable 5.1 trailer.
- Deferred, owner parent at the w0-doctor integration: `mise.dev.toml` `plan:decide`,
  `test:plan-decide` and the `check:research` depends entry (`w0-decisions-receipt.md:9-21`).
  Until then `test_plan_decide.py` runs only by direct `unittest` (it is outside `check.py`
  discovery). Deferred to wave-1 CT-24: the `issue-tracker.md` ledger sentence. Pending user: D48.
- Not run: `ci/acceptance.sh`, container, provider, hook-runtime and fresh-session acceptance;
  `hooks:install` (D2); `plan:decide` through mise (no row yet).
