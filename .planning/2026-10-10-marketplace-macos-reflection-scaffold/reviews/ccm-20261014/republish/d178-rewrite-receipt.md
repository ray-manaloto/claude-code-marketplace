# D178 part 2 receipt: local history rewrite without the private scanner rule

Status: rewritten and verified locally; not pushed. The force push waits for the user's go.

Session `ccm-20261014` operator subagent (Opus 5.5), root checkout, Git user Raymond Manaloto,
2026-10-14. Git 2.54.0 (Apple Git-157), betterleaks 1.9.0, Python 3.15.0 (`python3 -I`).
`VIRTUAL_ENV` was unset in every command (the inherited shell sets it to the checkout's `.venv`);
`UV_PROJECT_ENVIRONMENT`, `MARKETPLACE_PYTHON` and `MARKETPLACE_PRIVATE_RULES` unset. Runbook
`~/.local/state/claude-code-marketplace/d178-tools/runbook.md` sections 1-6 (tools `T` beside it),
work directory `W` = `/private/tmp/d178-rewrite.oz8GyC`. The tools load the private rule in memory
only and print counts and SHAs; no rule value was printed or written. Old SHAs in this file resolve
through `d178-sha-map.tsv` beside it.

## 1. Preconditions

| Check | rc | Result |
| --- | --- | --- |
| `pgrep -fl 'claude\|codex'`, `lsof -a -p <pids> -d cwd` | 0 | one process with its cwd in the checkout: PID 27453, an MCP server child of this session's own `claude` (27400); no other Claude or Codex process |
| `git branch --show-current` | 0 | `codex/marketplace-native-onboarding` |
| `git status --porcelain \| wc -l` | 0 | 0 |
| `git worktree list` | 0 | main checkout only, `272d6d2` |
| `ls <git-dir> \| grep -E '^(MERGE_HEAD\|REBASE_HEAD\|…)$'` | 1 | nothing (no Git operation in progress) |
| `git merge-base --is-ancestor claude/rule-split codex/marketplace-native-onboarding` | 0 | rule-split merged |
| `git ls-remote origin refs/heads/codex/marketplace-native-onboarding refs/heads/main` | 0 | `959c56f61e4f6eede2a0fb66e4827b8657d56556`, `6b5b092efa6bdf678815073db42f69fae3f07ab3` |
| `git rev-parse codex/marketplace-native-onboarding:.gitleaks.toml` | 0 | `139406d2760524e1fec1f4132fa783b649103542` |
| `ls -l <private rule file>` | 0 | present, `-rw-------` |
| `TIP0` = `git rev-parse codex/marketplace-native-onboarding` | 0 | `272d6d221057411a1f38f4a753fa5365de51a7cb` |
| `python3 -I T/literal_inventory.py <MP> TIP0 > W/inventory-before.json` | 0 | `regex_blobs` = `a04019a…`, `d7758f1…` only; all 4 rule fields only in `.gitleaks.toml`; integration 114 of 136 commits dirty; `959c56f` 13 of 25; first dirty first-parent commit `62b154a` |

## 2. Backup

| Command | rc | Result |
| --- | --- | --- |
| `for-each-ref refs/heads \| grep -vx main > W/branches.txt` | 0 | 11 branches (10 `claude/*`, the integration branch) |
| `update-ref refs/backup/d178-pre-rewrite/<b> refs/heads/<b>` per branch | 0 | 11 backup refs = 11 branches; each equals its branch (`diff` rc 0) |
| `git bundle create <private-notes>/archive/claude-code-marketplace-d178-pre-rewrite.bundle --glob=refs/backup/d178-pre-rewrite` | 0 | 14188790 bytes, 11 refs, `bundle verify` rc 0; untracked in private-notes, no commit there; private-notes remotes 0 |

Bundle path: `~/.local/state/claude-code-marketplace/private-notes/archive/claude-code-marketplace-d178-pre-rewrite.bundle`.

## 3. Rewrite

| Command | rc | Result |
| --- | --- | --- |
| `git clone --no-local --mirror <MP> W/rewrite.git` | 0 | |
| `T/clean_blob.py W/rewrite.git 139406d d7758f1 a04019a > W/blob-map.txt` | 0 | `d7758f1… → 139406d…`, `a04019a… → e970445106ec69c6b9dc5e0eab9d65e3961c091f` (unchanged from the dry run) |
| `git filter-branch -d W/fb-tmp --index-filter "sh T/index_filter.sh W/blob-map.txt" -- --branches --not refs/heads/main` | 0 | 124 commits walked (about 77 s), 11 refs rewritten, `main` unchanged |
| `git clone --no-local --mirror <MP> W/check.git` | 0 | |
| `T/clean_blob.py W/check.git …` | 0 | same blob map |
| `T/rewrite_objects.py W/check.git W/blob-map.txt W/sha-map.txt refs/heads/main <11 refs>` | 0 | `commits=124 rewritten=124 distinct_root_trees_substituted=112 gpgsig_dropped=0` |
| `for-each-ref refs/heads` of `check.git` `diff` `W/refs-after.txt` | 0 | the independent rewriter agrees on all 12 tips |

Determinism against the dry run: 116 of the dry run's 117 pairs reappear with 0 mismatches (the
117th was the dry run's simulated merge), e.g. `62b154a → 48d0260`, `959c56f → bea3e67`,
`38d1cc3 → ce2090f`.

## 4. Verify

`T/verify.py` rc 0, `W/verify.json`:

- (a) `a_commits_carrying_private_text` 0 of 136 commits reachable from the rewritten refs.
- (b) 124 pairs: 114 differ only in `.gitleaks.toml`, 10 identical trees, `b_pairs_other_difference` 0.
- (c) `c_tip_tree_diff` for `codex/marketplace-native-onboarding` and `claude/rule-split`:
  `identical`; the 9 other lane tips differ only in `.gitleaks.toml`.
- (d) `d_parent_mapping_mismatches` 0; commits and merges equal per ref (integration 136/136
  commits, 24/24 merges); first-parent length 70/70.
- (e) `e_header_mismatches_author_committer_other` 0, `e_message_mismatches` 0.
- Old SHAs cited: 53 rewritten commit messages; 51 tracked files at the tip (48 under
  `.planning/2026-10-10-…`, 1 each under `.agents`, `.claude`, `dev`), 122 distinct old SHAs.

`T/scan_compare.py W/rewrite.git 6b5b092..272d6d2 W/rewrite.git 6b5b092..51351de 139406d W/sha-map.txt`
rc 0: `rc_old` 1, `rc_new` 1, 228 = 228 findings; by rule id old = new = `generic-api-key` 226,
`ibm-cloud-user-api-key` 2; no private-rule entry; `mapped_old_minus_new` 0,
`new_minus_mapped_old` 0. The only non-generic finding is `ibm-cloud-user-api-key` in `48d0260a5`
(old `62b154a`, already public) `evidence/p2996-configure/generated/build.ninja`.

## 5. Ref move in the checkout

| Command | rc | Result |
| --- | --- | --- |
| `git fetch --no-tags W/rewrite.git '+refs/heads/*:refs/d178/new/*'` | 0 | 12 temporary refs |
| `update-ref --stdin` transaction (`start`, 11 `update <ref> <new> <old>`, `prepare`, `commit`) | 0 | `start: ok`, `prepare: ok`, `commit: ok` |
| `git rev-parse codex/marketplace-native-onboarding` | 0 | `51351de4a03fa1b1a17564e408abea73c1141d9d` = NEW |
| `git status --porcelain \| wc -l` | 0 | 0 |
| `test NEW^{tree} = TIP0^{tree}` | 0 | tip tree unchanged |
| `update-ref -d` each `refs/d178/new/*` | 0 | `refs/d178` and `refs/original` empty |

All 12 branch refs in the checkout equal `W/refs-after.txt` (`diff` rc 0); HEAD is the integration
branch at NEW.

## 6. Pre-push scan through the repository's combined config

- `git_delivery.scan(Path.cwd(), "<MP>/.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks",
  "--log-opts=6b5b092..51351de", report=True)` (signature `scan(root, binary, *mode, baseline=None,
  report=False)`; the binary path is absolute): output `rc 1 {'generic-api-key': 226,
  'ibm-cloud-user-api-key': 2} private 0`; command rc 0.
- `T/literal_inventory.py <MP> NEW > W/inventory-after.json` rc 0: every `refs/heads/*` has
  `any_field` 0; NEW 0 of 136 commits with rule text; only the 11 `refs/backup/d178-pre-rewrite/*`
  refs and `refs/remotes/origin/codex/marketplace-native-onboarding` (13 of 25, until the push)
  still count.

Mirror clones `W/rewrite.git` and `W/check.git` deleted after the run (`rm -rf` rc 0); filter-branch
removed `W/fb-tmp` itself. `W` keeps SHA and count files only. Backup refs and the bundle stay.

## Result

| Name | Value |
| --- | --- |
| TIP0 (old integration tip) | `272d6d221057411a1f38f4a753fa5365de51a7cb` |
| NEW (rewritten integration tip) | `51351de4a03fa1b1a17564e408abea73c1141d9d` |
| `map(959c56f)` (rewritten counterpart of the current remote tip) | `bea3e673fc75cf3410885aa56a4b797818c008f6` |
| SHA map | `d178-sha-map.tsv`: 124 rows, 13 `remote-public`, 111 `local-integration`, 0 lane-only (every lane commit is on the integration branch) |
| Backup refs | 11 under `refs/backup/d178-pre-rewrite/` |
| Local-only commits `map(959c56f)..NEW` | 111 (22 merges); `map(959c56f)` is an ancestor of NEW |

## Remote state (read-only, before the push)

- `git ls-remote origin`: integration `959c56f61e4f6eede2a0fb66e4827b8657d56556` (the lease),
  `main` `6b5b092efa6bdf678815073db42f69fae3f07ab3`.
- `gh api repos/ray-manaloto/claude-code-marketplace/rules/branches/codex/marketplace-native-onboarding`
  rc 0: `[]`, so no ruleset (no `non_fast_forward` rule) applies to the branch. Classic protection:
  `gh api …/branches/codex/marketplace-native-onboarding` reports `protected: false`.

## Planned push (awaiting the user's go)

```sh
git -C <MP> push --force-with-lease=codex/marketplace-native-onboarding:959c56f61e4f6eede2a0fb66e4827b8657d56556 origin 51351de4a03fa1b1a17564e408abea73c1141d9d:refs/heads/codex/marketplace-native-onboarding
```

This is the runbook's section 7 line with NEW. The local branch now carries this records commit on
top of NEW; pushing the branch tip instead of NEW (same lease) publishes it in the same push.
Runbook sections 7-11 (push, PR #110 checks, lane retirement, records after the push, Support
addendum) were not run.
