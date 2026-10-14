# scanner-betterleaks merge report: betterleaks 1.9 scanner for A09 (D159, CT-82 part A)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger:
session `ccm-20261014` (Opus 5.5) subagent, serial. `VIRTUAL_ENV` unset before every mise command.
Authority: D159 (switch to betterleaks 1.9.x), D164 (retro record ahead of the merge), D37 (one
A09 publish per integration). Scratch logs: the session scratchpad `republish/sb-checks/` and
`republish/a09-sb/` (outside the checkout).

## Result

- First attempt on `0eaa0d2`: the PreToolUse deny gate refused the merge (`retro record missing`):
  the gate reads the record from the target working tree, where it did not exist before the merge.
  Simulated hook events showed that `git -C $MP merge` from a lane worktree is allowed (the hook does
  not expand `$MP`, resolves no repository and fails open), which is how `be1a0f9` and `878e7f0`
  passed this layer. Parent decision D164; gate fix CT-86.
- Parent records commit `4f7c68c` added `retros/scanner-betterleaks.md`, blob `8530ad3`,
  byte-identical to the lane's blob at `3f66898`; checkout clean.
- Merge M `ece5030` (parents `4f7c68c`, `3f66898`), literal `git merge --no-ff -F <msg>
  claude/scanner-betterleaks` from the root, no `-C`, ort, 4 files +123 -3, rc 0 (19:33:13Z);
  `git merge-tree --write-tree` clean beforehand. No rebase: the lane was cut from `ca53deb` on the
  scrubbed history. **This is the first merge where both gates checked the real record:** the
  PreToolUse deny gate allowed it (no deny output; a simulated event on the same tree returns
  allow) and hk `pre-merge-commit` printed `retro gate passed for: claude/scanner-betterleaks`
  (`retro:gate-merge`, `dev/hooks/git_gate.py merge`).
- Records R `9672854` (9 files +49 -9; hk pre-commit `records` step passed): parent edits 1-7,
  ledger operation DL-212 (D159).
- Publish P: pending (filled after the publish).

## Gates on the merged tree with parent edits 1-7 (19:33:57-19:37:33Z)

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise run tools:prepare` (operation A) | 0 | betterleaks 1.9.0 installed in root `.mise/installs` (python, uv already) |
| `./dev/mise tasks validate` | 0 | 64 tasks |
| `./dev/mise run check` | 0 | 91 tests; json 2314, python 244, shell 6, toml 21; `verify_tool_lock()` now runs |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:delivery` | 0 | 18 tests, the real-scanner test ran (no skip) |
| `./dev/mise run deps:check` | 0 | lock sha256 `2f227f5d…` |
| `./dev/mise run test:bootstrap` | 0 | 7 checks incl. tool-lock-drift |
| `./dev/mise run check:research` (19:36:27-19:37:33Z) | 0 | 18 test tasks incl. `test:delivery`; baseline 19 |
| `hk validate` | 0 | `hk.pkl` valid |
| `python3 -I dev/retro_gate.py --unit scanner-betterleaks` | 0 | selectors none |
| `git diff --check 4f7c68c` | 0 | |
| `betterleaks config check --config .gitleaks.toml` | 0 | 465 rules |

Pinned scanner: `./dev/mise which betterleaks` = root `.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`,
`version` 1.9.0. Outbound pre-scan with A09's flags over `959c56f..ece5030`: rc 0, 0 findings.
Staged scan of R (`betterleaks git --pre-commit --staged --config .gitleaks.toml --redact=100 .`):
rc 0, no leaks; `git diff --cached --check` rc 0.

## Retro parent edits (`retros/scanner-betterleaks.md`)

| Edit | Disposition |
| --- | --- |
| 1 companion patch (sha256 `efe70874…` verified) | applied in R: `TOOL_BACKENDS` data row, `mise.dev.lock` entry |
| 2 `dev/check.py` `verify_tool_lock()` | applied in R: a call to an existing function (D113), not new logic |
| 3 `check:research` gains `test:delivery` | applied in R |
| 4 `.claude/rules/secret-scanner.md` | applied in R |
| 5 `.claude/AGENTS.md` rules line | applied in R |
| 6 root `AGENTS.md` literal-command clause | applied in R |
| 7 lane record | applied in R: integrated, review, retro passed, `head_sha` `3f66898`, `integration_merge` `ece5030` |
| Operation A | done (rc 0, above) |
| Operation B | `gitleaks_bin` = the pinned betterleaks in this publish; the R17 re-adjudication was not run (brief: no adjudication); the outbound range had 0 findings |

## Publish (A09)

Selected path: this report only; M and R travel as ancestors. Preimage `959c56f`; check_task
`["deps:check","check:acceptance-baseline","test:delivery","test:hooks"]`; `gitleaks_bin` = the
absolute pinned betterleaks path (D159, the first A09 publish with betterleaks). The committed copy
in P says "pending"; the fields below were filled after the publish.

Attempt 1 stopped at `inspect-hooks`: `safe_configured_hooks()` admits only configured `hook.*`
events `pre-commit`, `commit-msg` and `pre-push`, and the global hk install of D154 (after the last
publish `959c56f`) added `prepare-commit-msg`, `pre-merge-commit` and `post-commit` to
`~/.gitconfig`. Nothing was staged or pushed; M and R stay local. Parent decision pending.

| Command | rc | Output |
| --- | --- | --- |
| `git diff --cached --name-only HEAD \| wc -l` (before) | 0 | 0 |
| `./dev/mise run delivery:inspect-hooks -- inspect-hooks.json d907b24d…` (19:39:21Z, attempt 1) | 2 | `A09 refused: configured Git hook could execute during delivery` |
| `./dev/mise run delivery:prepare -- prepare.json …` | pending | |
| `./dev/mise run delivery:publish -- publish.json …` | pending | |

## Post-publish verification

| Command | rc | Result |
| --- | --- | --- |
| `git rev-parse HEAD origin/codex/marketplace-native-onboarding` | pending | |
| `gh run watch <id> --exit-status` per run on the published SHA | pending | |
