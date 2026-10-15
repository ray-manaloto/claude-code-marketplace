# a09-hook-events merge report: A09 admits the D154 global hook events (D165)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger:
session `ccm-20261014` (Opus 5.5) subagent, serial; the parent stayed out of the root checkout.
`VIRTUAL_ENV` unset before every mise command. Authority: D165 (fix A09 instead of removing global
hooks), D164 (retro record ahead of the merge), D37 (one A09 publish per integration), D159 (the
pinned betterleaks scans the publish). Scratch logs: the session scratchpad `republish/a09-he/`
(outside the checkout).

**This publish carries two integrations.** scanner-betterleaks (merge `ece5030`, records
`9672854`, operation DL-212) stopped at `inspect-hooks` and stayed local; a09-hook-events fixes
that refusal. D37 asks for one A09 publish per integration; it is satisfied here by one publish
whose selected paths are both integrations' merge reports: this report and
`scanner-betterleaks-merge-report.md` (its publish section points here). No integration is
published without its report.

## Result

- Preflight: toplevel = root checkout, branch `codex/marketplace-native-onboarding`, HEAD
  `18732c7`, status clean, Git dir `.git`; lane tip `5744151`. `retros/a09-hook-events.md` on HEAD
  is blob `b87cf99`, identical to the lane's blob (D164, added in `18732c7`).
  `git merge-tree --write-tree HEAD claude/a09-hook-events` rc 0 (clean).
- Merge M `30d65a1` (parents `18732c7`, `5744151`), literal `git merge --no-ff -F <msg>
  claude/a09-hook-events` from the root, no `-C`, ort, 2 files +50 -10, rc 0 (20:13:28Z). No
  rebase: the lane was cut from `0784d95` on the scrubbed history. The PreToolUse deny gate printed
  nothing (allowed); hk `pre-merge-commit` printed `retro gate passed for: claude/a09-hook-events`
  (`retro:gate-merge`, `dev/hooks/git_gate.py merge`). No other hook output.
- Records R2 `53d7b03` (8 files +22 -9, 20:18:32Z; hk pre-commit `records` step passed): parent
  edits E1-E5, lane record, ledger operation DL-221 (D165). Staged scan with the pinned betterleaks
  (`git --pre-commit --staged --config .gitleaks.toml --redact=100`): rc 0, no leaks;
  `git diff --cached --check` rc 0.
- Publish P: refused at the selected-tree check (`test:delivery` rc 1, no pinned betterleaks in the
  extracted tree); nothing pushed. See Publish below.

## Gates on the merged tree with parent edits E1-E5 (20:14:11-20:17:48Z)

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 64 tasks |
| `./dev/mise run check` | 0 | 91 tests; json 2317, python 244, shell 6, toml 21 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:delivery` | 0 | 20 tests |
| `./dev/mise run check:research` (20:16:10-20:17:20Z) | 0 | `deps:check` and 18 test tasks incl. `test:delivery`, `test:hooks`; baseline 19 |
| `hk validate` | 0 | `hk.pkl` valid |
| `python3 -I dev/retro_gate.py --unit a09-hook-events` | 0 | selectors none |
| `git diff --check 18732c7` | 0 | |
| `./dev/mise run delivery:inspect-hooks -- <fresh intent, head 30d65a1>` (20:17:48Z) | 0 | `hook_tree_sha256=3417c0d9…`, against the real global config with six hk events |

The last row is the defect this lane fixes: the same command was rc 2 on `9672854` (scanner
report, attempt 1).

## Retro parent edits (`retros/a09-hook-events.md`)

| Edit | Disposition |
| --- | --- |
| E1 `ticket-frontier/references/scheduler.md` step 3 | applied in R2 as written, with the byte-identical `.agents/skills` mirror (`.claude/AGENTS.md`: change both copies together) |
| E2 `ticket-frontier/references/brief-templates.md` Env line | applied in R2 as written, with the mirror |
| E3 `lanes/request-catch.json` notes | applied in R2: notes only, the P-2 relay appended |
| E4 lane record `review`, `retro` | applied in R2; `status` then set to `integrated` (the E4 text "retro passed on 5744151; awaiting integration" is superseded by the merge), `head_sha` `5744151`, `integration_merge` `30d65a1` |
| E5 `progress.md` retro bullet above NEXT | applied in R2, placeholders filled (`5744151`; E1-E5 yes) |

None is new Python logic; nothing deferred.

## Publish (A09)

Selected paths: this report and `scanner-betterleaks-merge-report.md`; M, R2 and the scanner
integration (`4f7c68c`, `ece5030`, `9672854`) travel as ancestors. Preimage `959c56f` (remote, by
`git ls-remote` before the publish); 33 outbound commits before P. check_task
`["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`; `gitleaks_bin` = the
absolute path `./dev/mise which betterleaks` prints, root `.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`,
`version` 1.9.0 (D159 operation B, the first A09 publish scanned with betterleaks). Outbound
pre-scan with A09's flags over `959c56f..53d7b03`: rc 0, 0 findings. Nothing was published; this
report is uncommitted (the parent commits it with the decision on the refusal below).

| Command | rc | Output |
| --- | --- | --- |
| `./dev/mise run delivery:inspect-hooks -- inspect-hooks.json c5ea6d51…` (20:19:47Z, head `53d7b03`) | 0 | `hook_tree_sha256=3417c0d9…` |
| `./dev/mise run delivery:prepare -- prepare.json f724fbc7…` (20:19:55Z, attempt 1) | 2 | `A09 refused: command failed (rc=128): git`, after `git add` had staged both reports. A09's `run()` drops stderr; every read-only call of `prepare` rerun by hand returned 0, and `git write-tree` is the one call that takes `index.lock` and exits 128 when another process holds it (confirmed in a scratch repository), so the likely cause is a concurrent Git process in the root (not identified). Unstaged with `git restore --staged`, nothing else changed |
| `./dev/mise run delivery:prepare -- prepare.json f724fbc7…` (20:21:25Z, attempt 2) | 0 | `index_tree=c21a2379…`, head `53d7b03` |
| `./dev/mise run delivery:publish -- publish.json c4124b92…` (20:21:36-20:23:34Z) | 2 | `A09 refused: command failed (rc=1): <tmp>/a09-selected-…/selected/dev/mise`; refused in `check_selected_tree`, before `commit-tree`: nothing committed or pushed, remote still `959c56f` (`git ls-remote`), HEAD `53d7b03`; both reports unstaged again with `git restore --staged` |

### Publish refusal: the selected-tree check has no pinned betterleaks

`check_selected_tree` extracts the index tree into a fresh temporary directory and runs
`tasks validate`, `check`, `check:acceptance-baseline` and `test:delivery` there. `dev/mise` sets
`MISE_DATA_DIR=<checkout>/.mise`, so the extracted tree has no betterleaks install, and
`pinned_betterleaks()` in `dev/test_git_delivery.py` (scanner-betterleaks review fix `6948135`)
fails instead of skipping when `MISE_TASK_NAME` is `test:delivery`. Reproduced by hand on the same
index tree with A09's scratch environment (scratchpad `republish/a09-he/selrepro/`): `tasks validate`
rc 0, `check` rc 0, `check:acceptance-baseline` rc 0, `test:delivery` rc 1, 20 tests, one failure:
`test_root_config_reports_lone_aws_access_key_id`, `pinned betterleaks 1.9.0 is missing`. This is
the a09-hook-events retro P2 (per-checkout `.mise`) met inside A09 itself. The outbound history scan
never ran (A09 refused earlier); the pre-scan above was rc 0 with 0 findings.

Fixing it changes `dev/git_delivery.py` or `dev/test_git_delivery.py` (a fix to existing Python,
D113), which is lane work, not a merger edit. Parent decision pending. Candidate fixes for the
decision: `check_selected_tree` gives the scratch run the root checkout's `MISE_DATA_DIR`
(read-only tool installs, so the pinned binary resolves), or the selected-tree run sets a marker
that lets `pinned_betterleaks()` skip while `test:delivery` in the root and CI still fail on a
missing pin. M `30d65a1`, R2 `53d7b03` and the scanner integration stay local; DL-212 and DL-221
stay open.

## Post-publish verification

Not run: nothing was published.
