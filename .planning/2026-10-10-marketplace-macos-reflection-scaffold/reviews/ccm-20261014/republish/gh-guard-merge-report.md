# gh-guard merge report: raw gh writes refused; gh:write is the scanned route (D179)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. The merger
was a subagent of session `ccm-20261014` (Opus 5.5). It worked in the root checkout and followed
`capture-filter-merge-report.md`. `VIRTUAL_ENV` was unset before every command, and every command
ran from the root. The merge was the literal `git merge --no-ff` with no `-C` (D164). Scratch logs
are in the session scratchpad under `gg-merge/`, outside the checkout. Nothing was pushed or
published, and the remote is still `959c56f`.

## Preflight

The root checkout was on branch `codex/marketplace-native-onboarding` at HEAD `94d32c4`, with a
clean status and Git dir `.git`. The lane tip `claude/gh-guard` was `36fe2b7`, as the brief said,
and the merge base was `dc96614`. `git merge-tree --write-tree 94d32c4 claude/gh-guard` returned rc
0 (clean). The lane changes nine paths: `.codex/rules/gh-write.rules` (+71, new), `dev/gh_write.py`
(+65, new), `dev/test_gh_write.py` (+128, new), `dev/hooks/pretooluse_gate.py`, `dev/test_hooks.py`,
`docs/agents/hooks-and-mods.md`, `docs/agents/issue-tracker.md`, `mise.dev.toml` and
`retros/gh-guard.md` (+157); 633 insertions and 16 deletions against the integration tip.

## Commits

| Step | Commit | Parents | Content |
| --- | --- | --- | --- |
| R1 records | `8ed943a` | `94d32c4` | `retros/gh-guard.md` (+157), byte-identical to `36fe2b7` (blob `3ab4eac`); parent edits 1, 2 and 4; ledger row CT-96. hk `pre-commit` `records` passed |
| M1 merge | `94e5445` | `8ed943a`, `36fe2b7` | ort, 8 files +476 -16, rc 0, auto-merged `dev/test_hooks.py` and `docs/agents/hooks-and-mods.md`. hk `pre-merge-commit` printed `retro gate passed for: claude/gh-guard`, and the PreToolUse deny gate printed nothing (allowed). Merged tree `8aaef74`, the same as `git merge-tree --write-tree 8ed943a claude/gh-guard` |
| R2 records | the commit carrying this report | `94e5445` | Lane record set to integrated, the progress entry, and this report |

Byte identity was checked with `git hash-object` against `git rev-parse 36fe2b7:<path>`; both
returned `3ab4eace3fe5a733c285b9202be85080888db702`. Before R1, `git diff --cached --check`
returned rc 0, and `./dev/mise run retro:gate -- gh-guard` returned rc 0 on the root with the
record staged. The merge message is the brief's literal title, with the two session trailer lines
passed as a second `-m` paragraph; R1 carries the same trailers.

Writer trailers on the lane: `8d8d794`, `1283302`, `27cae68`, `412e21e` and `36fe2b7` all name
Claude Opus 5.5. The retro states that `412e21e` and `36fe2b7` were written by Claude Fable 5.1
(retro-writer) under trailer lines the parent's brief fixed. The lane record's `writer_model`
("opus (high)") describes the implementer and was left as allocated.

## Conflicts

There were none. `ort` auto-merged the two paths both sides touched since the lane's last sync
(`dev/test_hooks.py`, where capture-filter added one test, and `docs/agents/hooks-and-mods.md`,
where capture-filter edited the Capture bullet).

## Gates

These ran after M1 (`94e5445`), from 21:50:41Z to 21:54:05Z, each alone and one after the other:

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 68 tasks |
| `./dev/mise run check` | 0 | 31 + 91 tests; json 2324, python 246, shell 6, toml 21 (21:50:42-21:51:22Z) |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run check:research` | 0 | `deps:check` and 20 test tasks, `test:gh-write` and `test:hooks` among them, then `dev/check.py --baseline` (baseline 19); 21:52:08-21:53:25Z |
| `./dev/mise run test:hooks` | 0 | 27 tests (the lane's 26 plus capture-filter's one) |
| `./dev/mise run test:gh-write` | 0 | 5 tests, none skipped |
| `./dev/mise run test:issue-amend` | 0 | 26 tests |
| `./dev/mise run retro:gate -- gh-guard` | 0 | `RETRO GATE PASSED`, selectors none |
| `git diff --check 8ed943a` | 0 | also rc 0 against `94d32c4` |
| `betterleaks git . --config .gitleaks.toml --redact --no-banner --log-opts="94d32c4..HEAD"` (1.9.0, `.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`, JSON report in the scratchpad) | 0 | 7 commits, about 72.3 KB; no leaks found, so there are no rule ids and the count is 0 |

## Live check of the merged gate

The merged `dev/hooks/pretooluse_gate.py` (blob `079d8e8`, the working file equal to `HEAD`) read
hook stdin JSON (`hook_event_name` PreToolUse, `tool_name` Bash, `cwd` the root) through
`python3 -I dev/hooks/pretooluse_gate.py`, the settings command, with `CLAUDE_PROJECT_DIR` set to
the root. The two probe files were written with the Write tool, so no Bash command carried the
probe text.

| Probe command | rc | Decision |
| --- | --- | --- |
| `gh issue comment 1 -b x` | 0 | deny: `permissionDecision` deny, reason `raw gh write refused (gh issue comment; D179)`, naming `./dev/mise run gh:write -- <gh args>` and the issue preview tasks; the reason echoes no command text |
| `gh issue view 1` | 0 | allow: no output |

From this merge on, this session's raw gh write commands are refused, including a Bash heredoc
whose body line starts with a gh write verb (GG-7). This report and the R2 edit script were written
with the Write tool for that reason.

## Parent edits

The retro's "Parent edits" section lists four:

1. `.claude/rules/dev-tests.md`, third bullet: applied in R1 with the literal sentence appended to
   the one-line bullet; `grep -c 'mise keeps its config trust' .claude/rules/dev-tests.md` prints 1.
2. `CODING_STANDARDS.md`, rule 16 under `## Tests` after rule 15: applied in R1 with the literal
   text, wrapped to rule 15's width and indent; `grep -c 'reshape argv' CODING_STANDARDS.md`
   prints 1.
3. Follow-up ticket under #138: added as ledger row CT-96 (pending issue), "gh-guard follow-ups: gh
   extensions and aliases, project/secret/workflow writes, heredoc data lines (GG-1, GG-2, GG-7,
   R-174)", frontier READY, blocked by none, with the Codex leg (GG-2) waiting for the Q2-order-v2
   §6 U3 decision. CT-96 was the next free number: CT-95 was the highest in the ledger, and no
   tracked file or commit names CT-96. No GitHub issue was filed; that is the parent's write.
4. Lane record: R1 set `status` to "reviewed, retro passed at lane tip 36fe2b7; merge pending" and
   added the review disposition; R2 completed it.

Lane record `lanes/gh-guard.json` (R2):

- `status` is integrated.
- `review` is "fable cold review PASS-with-findings on 27cae68; P2 continuation and substituted
  graphql fixed in 412e21e".
- `retro` is "passed".
- `head_sha` is `36fe2b7`, and `integration_merge` is `94e5445`.
- Four notes were added: the retro binding and its writer trailers, the parent-edit dispositions,
  the integration gates with the live check, and the worktree removal.

The progress entry was inserted directly above `- NEXT (`, so NEXT is still the last bullet.

## Worktree

`.claude/worktrees/gh-guard` was at `36fe2b7`. It had no tracked or untracked changes (ignored
`.mise/`, `.venv/` and `__pycache__/` only) and no stash, and `git merge-base --is-ancestor
claude/gh-guard HEAD` returned rc 0. `git worktree remove .claude/worktrees/gh-guard` (no `--force`)
returned rc 0. Branch `claude/gh-guard` stays at `36fe2b7`.

## Refused, unrun, left for the parent

- No gate failed, and the deny gate refused nothing during the merge.
- The GitHub issue for CT-96 under #138 is the parent's write. Raw gh write commands are now
  refused in this session, so it goes through `./dev/mise run gh:write -- <gh args>` or the issue
  tasks.
- The CT-94 ledger row still reads "not allocated"; its lane and local-state columns are the
  parent's edit.
- GG-4 (a CI image with codex so `CodexRules` does not skip in research-fast) stays with the parent
  under CT-80 host checks.
- No `decisions.jsonl` row was added or changed.
