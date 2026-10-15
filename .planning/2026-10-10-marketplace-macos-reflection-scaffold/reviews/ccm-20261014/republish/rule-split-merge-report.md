# rule-split merge report: the private scanner rule leaves the tracked config (D178 part 1)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto, Git dir
`.git`. The merger was a subagent of session `ccm-20261014` (Opus 5.5). It worked in the root
checkout and followed `gh-guard-merge-report.md` and `capture-filter-merge-report.md`.
`VIRTUAL_ENV` was unset before every command, and every command ran from the root. The merge was the
literal `git merge --no-ff` with no `-C` (D164). Scratch logs are in the session scratchpad under
`rs-merge/`, outside the checkout. Nothing was pushed or published, and the remote is still `959c56f`.
No rule regex, matched value or derived sample was printed or written (D145); the private rule file
was read only with `stat`.

## Preflight

The root checkout was on `codex/marketplace-native-onboarding` at HEAD `38d1cc3`, with a clean status
(untracked files included), no merge, rebase, cherry-pick or revert in progress, and two worktrees
(the root and `.claude/worktrees/rule-split` at `3d4c147`). The lane tip `claude/rule-split` was
`3d4c147`, as the brief said. The merge base was `38d1cc3` itself, because the lane merged the
integration tip in `60dc227`. `git merge-tree --write-tree 38d1cc3 claude/rule-split` returned rc 0
(clean) with tree `d7dfb6a`. The lane changes nine paths, all inside `owned_paths`:
`.gitleaks.toml`, `.claude/rules/secret-scanner.md`, `dev/git_delivery.py`, `dev/issue_amend.py`,
`dev/test_git_delivery.py`, `dev/test_issue_amend.py`, `dev/test_issue_create.py`,
`dev/test_gh_write.py` (added to `owned_paths` after gh-guard integrated) and `retros/rule-split.md`;
407 insertions and 86 deletions. None of the 19 baseline files is touched.

## Commits

| Step | Commit | Parents | Content |
| --- | --- | --- | --- |
| R1 records | `98ff3e9` | `38d1cc3` | `retros/rule-split.md` (+137), byte-identical to `3d4c147` (blob `0884343`); parent edits 2 and 3; lane record review disposition, retro "passed", status merge pending. hk `pre-commit` `records` passed |
| M1 merge | `04b560b` | `98ff3e9`, `3d4c147` | ort, 8 files +270 -86, rc 0. hk `pre-merge-commit` printed `retro gate passed for: claude/rule-split`. Merged tree `5057109`, the same as `git merge-tree --write-tree 98ff3e9 claude/rule-split` |
| R2 records | the commit carrying this report | `04b560b` | Lane record set to integrated, the progress entry, and this report |

Byte identity: `git hash-object` on the copied retro and `git rev-parse 3d4c147:<path>` both returned
`088434366a3dd9c0b0f258da5eb8a0ca28c971c7`. Before R1, `git diff --cached --check` returned rc 0, and
`./dev/mise run retro:gate -- rule-split` returned rc 0 on the root with the record staged.

Tree check: the merged tree `5057109` differs from the first prediction `d7dfb6a` (on `38d1cc3`) by
exactly the four files R1 edited (the two `handoff-template.md` copies, `.claude/rules/dev-tests.md`,
`lanes/rule-split.json`; 11 insertions, 7 deletions). The retro is the same blob in both, so it
adds no difference.

The merge message is the brief's literal title with the two session trailer lines, passed through
`-F` with a scratchpad file (`git merge -F -` exits 129); R1 carries the same trailers. Writer
trailers on the lane: `34f86db`, `b10e208`, `1d65cd0`, `60dc227`, `d4e4299` and `8b31daa` name Claude
Opus 5.5 (implementer), and `3d4c147` names Claude Fable 5.1 (retro-writer). The lane record's
`writer_model` ("opus (high)") describes the implementer and was left as allocated.

## Review disposition

Fable cold review: PASS-with-findings on `1d65cd0`. Its P2 and P3a-e were fixed in `d4e4299`. The
retro-writer (Fable, independent of the implementer) verified `d4e4299` line by line, bound each new
refusal to its seam test, and found no new defect. Parent's disposition: the parent accepts that
verification in place of a second cold pass. This closes the retro's P3 row that left a separate
focused reviewer pass to the parent at integration.

## Conflicts

There were none. The merge base is the integration tip, so only R1 sits on the integration side, and
it touches no lane path.

## Gates

These ran after M1 (`04b560b`) from 22:28:47Z, each alone and one after the other unless noted:

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 68 tasks |
| `./dev/mise run check` | 0 | 31 + 91 tests; json 2324, python 246, shell 6, toml 21, `status: pass` (22:28:52-22:29:32Z) |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run check:research` | 0 | `deps:check` and 20 test tasks (`test:delivery`, `test:issue-create`, `test:issue-amend`, `test:gh-write` and `test:hooks` among them), then `dev/check.py --baseline`; 22:30:23-22:31:41Z |
| `./dev/mise run test:delivery` | 0 | 29 tests (22:32:31-22:33:06Z) |
| `./dev/mise run test:issue-create` | 0 | 25 tests (from 22:33:10Z) |
| `./dev/mise run test:issue-amend` | 0 | 27 tests |
| `./dev/mise run test:gh-write` | 0 | 5 tests, none skipped |
| `./dev/mise run test:hooks` | 0 | 27 tests |
| `./dev/mise run retro:gate -- rule-split` | 0 | `RETRO GATE PASSED`, selectors none |
| `git diff --check 38d1cc3` | 0 | |
| betterleaks 1.9.0 over `38d1cc3..HEAD` through `git_delivery.scan` (the repo's resolver, so `scan_config` loads the private rule) | 0 | 9 commits; no finding, so no rule ids; private rule count 0 |

`test:delivery` and `test:issue-create` were first sent together by mistake (both rc 0, 29 and 25
tests). Those runs may have raced, so both were rerun alone; the reruns above are the receipts.
`retro:gate` and `git diff --check` were sent together; both are read-only.

The scan used the brief's one-liner with one change. `g.scan` refuses a relative scanner path
("scanner path must be absolute"), so the binary was passed as `$PWD/.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks`.
The signature `scan(root, binary, *mode, baseline=None, report=False)` matched otherwise. The output
was `rc 0 {} private 0`. `scan_config` refuses unless the private file defines the rule, so the scan
ran with it loaded.

Supporting facts, without values: the private file is `-rw-------`, 338 bytes, in a `drwx------`
directory (`stat` only). `git grep -c -e private-tr-project HEAD -- ':!.planning'` gives one line each
in `.claude/rules/secret-scanner.md` and `dev/git_delivery.py` (the id, the resolver's public
contract). The D145-form diff of `.gitleaks.toml` (`git diff -U0 38d1cc3 HEAD -- .gitleaks.toml | grep
-v '^@@' | grep -v -i regex`) was counted, not printed: 10 removed lines and 4 added lines remain
after the filter.

## Live check of the fail-closed route

`MARKETPLACE_PRIVATE_RULES=<scratchpad>/rs-merge/no-such-dir/private-rules.toml ./dev/mise run
gh:write -- --version`, with the path absolute and confirmed missing (`test -e` rc 1):

| Probe | rc | Result |
| --- | --- | --- |
| `gh:write` with a missing absolute private rule path | 2 | `REFUSED: private scanner rule unavailable: MARKETPLACE_PRIVATE_RULES or <default path> must be a readable file defining rule private-tr-project`; the reason names the variable and no value; gh never started (no version printed) |

The argument `--version` was chosen so that a broken refusal would only print gh's version, never
write.

## Parent edits

The retro's "Parent edits" section lists three:

1. `dev/test_gh_write.py` `setUp`: done in-lane in `d4e4299`; no parent action.
2. `.claude/rules/dev-tests.md`, last bullet: applied in R1 with the brief's literal text. The bullet
   was unchanged since `8ed943a` (that merge edited the third bullet), so no adaptation was needed.
   The bullet now reads "(a secret fixture built at run time, or the synthetic private name from
   `dev/test_git_delivery.py`; no test reads the real private rule, D178)".
3. `.claude/skills/session-handoff/references/handoff-template.md:28` and its `.agents/skills/`
   mirror: applied in R1 with the brief's literal text. The two-line bullet was rewrapped to the
   file's width (now three lines, at most 94 columns). `bullets()` in `dev/handoff.py` joins a notes
   bullet's two-space continuation lines into one string, so the wrap changes no sentence.
   `diff -r .claude/skills/session-handoff .agents/skills/session-handoff` printed nothing (rc 0).

Lane record `lanes/rule-split.json` (R2):

- `status` is integrated.
- `review` is "fable cold review PASS-with-findings on 1d65cd0; P2 and P3a-e fixed in d4e4299; the
  retro-writer (fable) verified d4e4299 line by line with no new defect, and the parent accepts that
  verification in place of a second cold pass".
- `retro` is "passed".
- `head_sha` is `3d4c147`, and `integration_merge` is `04b560b`.
- Five notes were added: the retro binding and its writer trailers, the review disposition, the
  parent-edit dispositions, the integration gates with the scan and the live check, and the worktree
  removal.

Ticket ledger: no CT row covers D178 part 1. The nearest is CT-82 (the hk pre-push scanner guard),
which is a different unit. None was added or changed.

The progress entry was inserted directly above `- NEXT (`, so NEXT is still the last bullet.

## Worktree

`.claude/worktrees/rule-split` was at `3d4c147`. It had no tracked or untracked changes (ignored
`.mise/`, `.venv/` and `__pycache__/` only) and no stash, and `git merge-base --is-ancestor
claude/rule-split HEAD` returned rc 0. `git worktree remove .claude/worktrees/rule-split` (no
`--force`) returned rc 0, run after the gates and before R2 so the record states a fact. Branch
`claude/rule-split` stays at `3d4c147`.

## Refused, unrun, left for the parent

- No gate failed. The deny gate refused nothing during the merge.
- D178 part 2 (the history rewrite) was not started; it follows this merge.
- Hosted CI has no private rule file until the D180 Actions secret lands. A CI scan route refuses
  until then (retro P2, owner parent).
- Publishing is the parent's: nothing pushed, remote `959c56f`.
- The lane record's `excluded_shared_paths` still lists `dev/test_gh_write.py`, which `owned_paths`
  now names. That was the parent's allocation edit, and the merger left it unchanged.
- No ticket-ledger row for D178 part 1. Adding one is the parent's choice.
- The retro's deferred rows keep their owners: ruff findings under R-168 (#132), D180 for CI.
- No `decisions.jsonl` row was added or changed.
