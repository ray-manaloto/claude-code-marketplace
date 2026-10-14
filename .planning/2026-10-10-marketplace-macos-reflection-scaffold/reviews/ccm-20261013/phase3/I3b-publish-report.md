# I3b: Phase 3 group 3B, review fixes and the second A09 publish

Root checkout `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`, branch
`codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Written by I3b (session
`ccm-20261013-check`). Authority: D37 (publish per integration), D2 (no `hooks:install`), the
user's approval of accepted-decisions hunk 2. `VIRTUAL_ENV` was unset before every mise command.
Serial, no agents. Logs and intents are in the session scratchpad `…/scratchpad/i3b/`.

## Result

- Published `d420a7ee8f589ecac05e667c1a4351cf468da734`, parent `0a68dce`, tree
  `061c0cdf6a980c320a35bd6ef420124f07b77f9a`, 95 files, author Raymond Manaloto.
- Remote tip after publish: `d420a7ee…` (`git rev-parse origin/…` and `git ls-remote` agree);
  `git log origin/…..HEAD` is empty.
- No refusal.
- CI: research-fast run `38504716758` (push, head `d420a7ee`) completed `success`
  (`gh run watch --exit-status --interval 60` rc 0).
- The sections below were filled in after the publish. The committed copy of this report has the
  publish fields pending. This update, the publish SHA line in `progress.md` and the
  `task_plan.md` Checkout line and step-10 tick are unstaged, and the next publish carries them.

## Inputs

- Pre-fix staged tree `d571874d8f3c1de67548399f4f7fe69ea70db37a` (93 paths), reviewed in
  `phase3/I3-review.md`: PASS-with-P2/P3, no P1.
- HEAD `0a68dce` = `origin/codex/marketplace-native-onboarding`; no `MERGE_HEAD`.

## Fixes (each file re-staged)

| Finding | File | Change |
|---|---|---|
| P2-1 | `ticket-ledger.md` | The snapshot now reads tip `0a68dce` = remote, the A09 publish of merge `760b154` (CT-02, lane `697e1da`), and no `MERGE_HEAD`. The CT-02 row is `done`: integrated (merge 760b154), published `0a68dce`, retro passed, with the review chain. |
| P2-2 | `task_plan.md` | The `D-all` row is now "approved 2026-10-13 (D1–D45)", rows D1-D26 are "approved 2026-10-13", and the preamble sentence at the old `:194` is updated. "pending user" now has 0 occurrences. |
| P2-1 (same class) | `task_plan.md` Lanes table | The gate-hooks row now reads integrated `760b154`, published `0a68dce`, retro passed. The a06-unit3 retro cell now names the alias with gate rc 0. |
| P3-1 | `docs/agents/claude-takeover.md` | The three em-dashes became parentheses (`:7`) and commas (`:26-27`). `git grep` finds no U+2014 (rc 1). |
| P3-2 | `reviews/ccm-20261013/00-evidence-index.md:47` | The heading count is now (27). The table has 27 agent rows (counted). |
| P3-3 | `.claude/skills/ticket-frontier/SKILL.md`, `.agents/skills/ticket-frontier/SKILL.md` | The `!` preamble now runs `python3 -I "${CLAUDE_SKILL_DIR}/scripts/frontier.py" status`, which matches the body's `<skill-dir>` form. The mirrors are identical (`diff -r` rc 0). The preamble command with `CLAUDE_SKILL_DIR` set returns rc 0. The frontier suite still passes 29 tests. |
| P3-4 | `findings.md` | The text now names "Firecrawl Search provisional" (Inherited limitations) and the "second plan dir" pwf hazard (Session review). `grep -c` returns 1 for each. |
| P3-5 | `task_plan.md` W0-7 | Declares the residual SYNTHESIS §4 rows (`ticket-retro.md:4-8`, the `claude-team.md` merge rule and hooks caveats, the `.claude/AGENTS.md` marketplaces line, the `issue-tracker.md` `issue:*` mapping, `skill-invocations.md:20`, `spec.md:61,65`, `checkout_transfer.py:17`). The `2a14` absolute paths go to CT-21. |
| User decision | `docs/accepted-decisions.md` | Hunk 2 of `imports/codex-worktrees-20261013/2a14/modified/docs/accepted-decisions.md.diff` was applied: headers plus the second `@@ -27,7 +80,7 @@` hunk, single-hunk patch sha256 `61f2fef7…`. `git apply --check` rc 0, then `git apply` rc 0. The result is byte-identical to `2a14/modified/docs/accepted-decisions.md` (`cmp` rc 0). |

Records were also updated:

- `progress.md` has a dated group-3B entry, and NEXT is rewritten in place as the last bullet: group 4 wave-0 W0-1…W0-7, then CT-21, then the user-typed setup and `/to-tickets`.
- In `task_plan.md`:
  - The handoff lines (Checkout, Next action, Pending user) and `## Next Step` are updated, and the handoff stays inside the first 30 lines (`## Next Step` at line 28).
  - Phase 3 steps 1-8 are ticked, with notes on steps 6, 7 and 8. Step 9 stays open because no `.mode` exists. Step 10 is ticked after the publish.

The selected list `phase3/I3-selected-paths.txt` gained `I3-review.md` and this report, for 95 paths.

## Verification on the staged tree (rc as captured, no pipes)

| Command | rc | Result |
|---|---|---|
| `git diff --cached --name-only \| wc -l` | 0 | 95. `sort` of the list equals `sort` of `git diff --cached --name-only HEAD` (`diff` rc 0). |
| `git diff --cached --check` | 0 | |
| `./dev/mise tasks validate` | 0 | 56 tasks |
| `./dev/mise run check` | 0 | 31 + 91 tests OK; `baseline 0, json 2298, python 232, shell 6, toml 20`, pass |
| `./dev/mise run check:acceptance-baseline` | 0 | `baseline: 19`, pass |
| `python3 -I -m unittest discover -s dev -p test_ticket_frontier.py` | 0 | Ran 29, OK |
| `python3 -I dev/retro_gate.py --unit ccm-20261013-session` | 0 | RETRO GATE PASSED |
| `python3 -I dev/retro_gate.py --unit a06-unit3` | 0 | RETRO GATE PASSED |
| gitleaks 8.30.1 `dir` over `git archive <index tree> <95 paths>` | 0 | No leaks found, 0 findings, 2.53 MB. The mise shim is unversioned, so the absolute install binary was used. |
| `git grep --cached -n 'mcp__memory__delete' -- <95 paths>` | 1 | none |
| `git write-tree` | 0 | `766bdfc7…` before this report was filled. The final tree is the `delivery:prepare` `index_tree` below. |
| `./dev/mise run delivery:inspect-hooks` | 0 | `hook_tree_sha256=a21be5fe…4af8`, unchanged from I2 |

## Intent (no secrets)

- Base fields:
  - `root` = the checkout
  - `common_dir` = `<root>/.git`
  - `branch` `codex/marketplace-native-onboarding`
  - `head` `0a68dce3ae33176115d9f88c81eb2d72be3ba80c`
  - `remote` `origin`
  - `remote_url_sha256` `477a17f8…3011` (one push URL and one fetch URL)
- The script has no remote-preimage key. It reads the remote tip live, and the preimage is
  `0a68dce` (= HEAD).
- `prepare.json`: base, `hook_tree_sha256` `a21be5fe…4af8`, and `path` = the 95 selected paths (a
  JSON list, accepted by `load_intent`).
- `publish.json`: `prepare.json` plus `index_tree`, `message_file` (`…/i3b/message.txt`, outside the
  checkout), `gitleaks_bin` (8.30.1, absolute), and `check_task` = `["deps:check",
  "check:acceptance-baseline","test:delivery","test:hooks"]`.
- `prepare` refuses when any path is already staged ("unreviewed paths were already staged",
  `dev/git_delivery.py` `main`), so the index was reset to HEAD (`git reset -q`, index only) before
  `prepare` re-staged the same 95 paths with `git add -A`.
- Message subject: "docs: ccm-20261013 session review, corrected records, pwf migration, CT-21
  import plan and the ticket-frontier skill". The body names the review dir, 15 P1/25 P2/31 P3,
  14 root-cause classes, CT-01..CT-25 (+CT-02b), the local exclusions and hunk 2 per the user.
  Trailers: `Co-Authored-By: Claude Fable 5.1`, `Claude-Session: …session_015qxgfYywpRPVMk8tYDLCHT`.

## Prepare and publish

Final staged tree before the reset: `git write-tree` = `061c0cdf6a980c320a35bd6ef420124f07b77f9a`,
95 paths.

| Command | rc | Output |
|---|---|---|
| `git reset -q` (index only) | 0 | 0 paths staged against HEAD |
| `./dev/mise run delivery:prepare -- prepare.json 8fe6eef8…` | 0 | `head=0a68dce3…`, `index_tree=061c0cdf…`, equal to the pre-reset tree |
| `./dev/mise run delivery:publish -- publish.json bfc18fe2…` | 0 | `published=d420a7ee…`, `history_scan_rc=0` |

`publish` rc 0 means each of the following also returned rc 0. Any nonzero rc in `run()` refuses.

- In the scratch extraction of `061c0cdf`: `tasks validate`, `check`, `check:acceptance-baseline`
  and `test:delivery`.
- In the checkout, each `check_task`: `deps:check`, `check:acceptance-baseline`, `test:delivery`,
  `test:hooks`.
- `git diff --cached --check`.
- The staged gitleaks pre-commit scan.

The outbound history scan over `0a68dce..d420a7e` returned rc 0, so no baseline or adjudication was
used.

## Post-publish verification

| Command | rc | Result |
|---|---|---|
| `git log --oneline -3` | 0 | `d420a7e`, `0a68dce`, `760b154` |
| `git rev-parse HEAD origin/codex/marketplace-native-onboarding` | 0 | both `d420a7ee…` |
| `git ls-remote --heads origin codex/marketplace-native-onboarding` | 0 | `d420a7ee…` |
| `git log origin/…..HEAD` | 0 | empty |
| `git status --porcelain` | 0 | empty before the post-publish edits |
| `git status --porcelain --ignored` | 0 | `!!` on `.agent/`, `.claude/settings.local.json`, `.claude/worktrees/`, `2a14/`, `c658/`, `digests/`, `plan-backups/`, `settings.json.before-ct02` and the tool caches |
| `gh run list --limit 2` | 0 | run `38504716758` research-fast on `d420a7e` |
| `gh run watch 38504716758 --exit-status --interval 60` | 0 | completed success |

## Not verified / notes

- Inside `delivery:publish`, the per-task outputs are captured by the script, and their rc 0 is
  inferred from `run()` (`dev/git_delivery.py:32-41`).
- The `${CLAUDE_SKILL_DIR}` substitution in the SKILL.md `!` preamble was exercised only with the
  variable set in a shell. A live `/ticket-frontier` invocation has not run yet; `|| true` keeps
  any failure harmless.
- Not run here: `check:research`, `hk validate`, `ci/acceptance.sh`, and container, provider or
  fresh-session acceptance. `hooks:install` was not run (D2).
- `ticket-ledger.md` CT-02b still shows `blocked | CT-02`. CT-02 is now done, so the parent must
  decide that blocker's disposition at the next ledger pass.
