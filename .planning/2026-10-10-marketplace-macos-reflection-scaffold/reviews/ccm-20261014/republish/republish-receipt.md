# Republish receipt: scrubbed baseline replaces the integration branch history (D143, D148, D149)

Session `ccm-20261014` (Opus 5.5), root checkout, Git user Raymond Manaloto, 2026-10-14.
`VIRTUAL_ENV` unset. Authority: D143 (scrub), D148 (method, Q119), D149 (API delete, Q122).
The pre-scrub history is kept only in the private archive (D144): bundle
`archive/claude-code-marketplace-all-refs-2026-10-14.bundle` in the private-notes repository
(no remote). Commit SHAs quoted in records before `62b154a` name commits in that archive.

## Built commit

- `62b154a36501f83b32cf37367ba236d0d8db3be5`, one commit, parent `origin/main`
  `6b5b092efa6bdf678815073db42f69fae3f07ab3`, built with `git commit-tree` from the tree of
  `local/scrub` (`4dad0a0` scrub, `8e5acde` fold of D143-D147). Pinned locally as
  `local/republish`.
- Checks on `local/scrub` before the build, each rc 0: `./dev/mise tasks validate`,
  `./dev/mise run check`, `./dev/mise run check:acceptance-baseline` (19), `test_hooks`,
  `test_handoff`, `retro:gate` for the 11 integrated lanes.
- Guard scan (`gitleaks git --config .gitleaks.toml --log-opts=origin/main..62b154a`):
  rule `private-tr-project` 0 findings; `generic-api-key` 226 findings, all file-digest fields
  (path to SHA-256) in `evidence/*secret-scan*.json` manifests, no secret.

## Remote operations

| Step | Command shape | rc | Result |
| --- | --- | --- | --- |
| 1 | `gh pr comment 109 --body <closing note>`, `gh pr close 109` | 0 | PR #109 `CLOSED` (comment `issuecomment-6173584991`) |
| 2 | `git push origin local/republish:refs/heads/codex/marketplace-native-onboarding --force-with-lease=codex/marketplace-native-onboarding:21af5650…` | 0 (1) | `+ 21af565...62b154a (forced update)`; hk pre-push `retro-gate` passed, "no lane branch" |
| 3 | `git push origin --delete codex/research-feedback-retro` | refused | PreToolUse deny gate: `unit could not be derived` (the gate reads every `codex/` name in a push as a lane, a delete included); not retried (D149) |
| 4 | `gh api -X DELETE repos/ray-manaloto/claude-code-marketplace/git/refs/heads/codex/research-feedback-retro` | 0 | remote heads now `main` and `codex/marketplace-native-onboarding` only |
| 5 | `gh pr create --draft --base main --head codex/marketplace-native-onboarding` | 0 | PR #110 |

(1) zsh captured no `PIPESTATUS`; the forced-update line and `git ls-remote` (tip `62b154a…`)
bind the result.

## PR refs scanned

Each PR head fetched read-only to a temporary ref (deleted afterwards) and scanned over its full
history with the guard config:

| PR | Commits | `private-tr-project` |
| --- | --- | --- |
| #1, #3, #5, #6, #7, #8, #10 | 19, 11, 9, 9, 10, 11, 13 | 0 each |
| #109 (closed) | 240 | 509 |

Only `refs/pull/109/head` still reaches the old history on GitHub; removing it and the cached
commits needs GitHub Support (request text drafted for the user, not sent).

## Local reset

- `git reset --hard 62b154a…` on `codex/marketplace-native-onboarding` (was `e76a5cd`, pinned as
  `local/pre-scrub-2026-10-14`): rc 0, working tree clean, HEAD equals the remote tip.
- The four uncommitted files differed from `62b154a` only by scrub substitutions; their
  originals are byte-identical in the private-notes commit `64f4bcc` (SHA-256 prefixes
  `03f91f852e30fa58`, `e9d4826b4d139184`, `1149a3f5ae910d33`, `7f6557e30b6f26c3`).

## Open

- Local branches and Codex worktrees still hold old-history commits; a plain `git push` of one
  would republish them, and the hk pre-push hook runs the retro gate only (the guard runs in A09
  publish). Proposed ticket: run the guard in pre-push.
- Proposed ticket: the PreToolUse deny gate passes a delete-only push (step 3).
