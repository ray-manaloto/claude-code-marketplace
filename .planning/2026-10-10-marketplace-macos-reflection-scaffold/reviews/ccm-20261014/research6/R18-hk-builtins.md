# R18: hk builtins, parallel hooks, jactionlint and the pre-push guard (research, 2026-10-14)

Written by research agent R18 of session `ccm-20261014` (`ce9c0b3d`) for decision D150 and question Q123.
Read-only for MP except this file and the untracked mirror `offline/research/R18/` (called OR below:
`OR/manifest.json` lists every mirrored item with URL, local path, UTC time, command shape, exit code and
SHA-256 or commit; `OR/queries.jsonl` holds every logged call with `status` and `failure_code`). MP = the
repository root at `132e8e3`; P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. TR = the
read-only private reference project `<TR>` (read, never run; no TR private names below, and the task named no
private report path, so TR specifics stay generic here). Nothing was installed: no `hk install`, no
`hooks:install`, no tool installs (D2). Timings come from a scratch clone with every Git hook disabled.

## 1. Verdict

Recommendation: move MP to hk 2.6.0 with one check-only, unstashed `pre-commit` hook of 28 steps (hk's
in-process safety utilities plus one native linter per file type and the existing records gate), a
`commit-msg` conventional-commit check, the existing `pre-merge-commit` retro gate, a warn-only `post-commit`
secret scan of HEAD, and a `pre-push` hook that runs the retro gate and the Q123 secret and private-name
guard in parallel; enable jactionlint through hk 2.6.0's `Builtins.jactionlint`, amended to hk main's
definition (SARIF fixes, composite actions, Dependabot) until hk 2.7.0 ships. Pin hk and every step's tool in
`mise.dev.toml` and run hooks through `./dev/mise x -- hk run`, because the live global launcher resolves
hk 2.5.0. The proposed `hk.pkl` is in section 7.6; it validates under hk 2.6.0 (`OR/local/proposal/hk.pkl`).

Confidence: high on versions, builtin behaviour, parallelism and timing (hk source at the v2.6.0 tag, release
notes, measured runs); medium on jactionlint's findings for MP (not installed here, so measured only by proxy:
actionlint 1.7.12, zizmor 1.30.1, ghalint, pinact); the scanner itself is R17's.

What decides it:
- Parallel check-only hooks cost almost nothing. On a 9-file commit the proposed 22-step pre-commit took
  0.39 to 0.42 s against 0.38 to 0.52 s for today's single records step; serial (`HK_JOBS=1`) it took
  0.93 to 0.95 s. `hk check --all` over the repository took 0.59 to 0.63 s parallel and 1.32 to 1.36 s
  serial (section 7.7). In check mode every hk job takes read locks (hk `src/step_job.rs:297` at v2.6.0), so
  only `exclusive`, `depends` and groups serialise.
- hk 2.6.0 (2026-10-12) is the latest release and adds `Builtins.jactionlint`
  ([v2.6.0 notes](https://github.com/jdx/hk/releases/tag/v2.6.0), [jdx/hk#1663](https://github.com/jdx/hk/pull/1663),
  2026-10-06). hk's own CI moved to jactionlint v2 and dropped zizmor
  ([jdx/hk#1682](https://github.com/jdx/hk/pull/1682), 2026-10-09), and mise deprecated `actionlint` in favour
  of `jactionlint` ([jdx/mise#13960](https://github.com/jdx/mise/pull/13960), 2026-10-05).
- The pre-push guard must scan history, not files: hk's pre-push selects paths from the first pushed ref only
  and runs commands on the worktree (hk `src/cli/run/pre_push.rs:152-187`;
  [CI docs](https://hk.jdx.dev/ci.html), `OR/pages/hk-ci.md:87-90`). `<scanner> git
  --log-opts="--branches --not --remotes"` covers every unpushed commit of every local branch with no new
  logic; gitleaks 8.30.1 and betterleaks 1.9.0 both accept it and both read MP's `.gitleaks.toml`.
  Precondition: MP still has 167 unpushed old-history commits on 10 local branches (measured read-only;
  R17 found the 504 `private-tr-project` hits there), so this guard refuses every manual push until those
  branches are rebased or deleted per D143/D148. That refusal is the guard working: `git push origin
  <old-branch>` is today's leak path. Until the cleanup, `--log-opts=HEAD --not --remotes` (4 commits, clean,
  0.32 to 0.55 s on MP) is the interim range; it misses pushes of a branch other than HEAD.
- Two live-host gaps make the switch need care: the global hk launcher runs `mise x hk -- hk`, which resolves
  hk 2.5.0 (measured), so `min_hk_version = "2.6.0"` would refuse every commit until the launcher changes;
  and the global install registers only `pre-commit`, `commit-msg` and `pre-push`, so MP's
  `pre-merge-commit` retro gate does not fire on this host today.

Classification (D112): every proposed step is configuration of an existing native tool or an existing mise
task. No step adds Python. The proposal makes `dev/check.py`'s parse loop (`dev/check.py:27-47`) redundant, a
later deletion, and needs one fix to existing Python (12 undefined names, section 7.5).

## 2. Queries sent to each tool, plugin or service (stage 1)

Built from `OR/queries.jsonl`. Preflight (seq 1-8, 126-131): Firecrawl `firecrawl credits --json` (seq 1);
Serper `GET /account` (seq 2); SerpApi `GET /account.json` (seq 3); Context7 `GET /api/v2/usage` (seq 4);
`gh api rate_limit` (seq 5); Exa has no balance endpoint (seq 6); `webclaw --version` (seq 7); ScrapeCreators
balance for Last30Days (seq 8); `gh api repos/<r>` for jdx/hk, jdx/jactionlint, jdx/mise, rhysd/actionlint,
gitleaks/gitleaks, zizmorcore/zizmor (seq 126-131, every feature enabled).

| Seq | Provider | Exact query |
|---|---|---|
| 9 | exa | `jdx hk git hook manager builtin linters list` |
| 10 | exa | `jdx jactionlint GitHub Actions workflow linter` |
| 11 | exa | `hk v2.6.0 release notes jdx` |
| 12 | exa | `hk hook manager parallel steps exclusive depends stash fix` |
| 13 | exa | `hk jdx post-commit hook configuration hk.pkl` |
| 14 | exa | `hk.pkl pre-push gitleaks secret scanning step` |
| 15 | exa | `jactionlint vs actionlint differences` |
| 16 | exa | `hk.pkl example builtins ruff shellcheck taplo yamllint actionlint` |
| 17 | context7 | not called (`/jdx/hk`, jactionlint docs): SKIPPED, CREDITS_EXHAUSTED |
| 18 | firecrawl | not called (`firecrawl search "jdx hk builtins jactionlint"`): SKIPPED, CREDITS_EXHAUSTED |
| 19 | webclaw | `https://hk.jdx.dev/llms-full.txt` |
| 20-102 | webclaw | `https://hk.jdx.dev/llms.txt` and all 83 hk doc pages it lists |
| 103-125 | webclaw | `https://jactionlint.jdx.dev/llms.txt`, its home page and all 20 pages it lists |
| 132 | gh-api-releases | `gh api repos/jdx/hk/releases?per_page=100 --paginate` |
| 133 | gh-api-releases | `gh api repos/jdx/jactionlint/releases?per_page=100 --paginate` |
| 134-136 | webclaw | release pages `jdx/hk` v2.6.0, v2.5.0; `jdx/jactionlint/releases` |
| 139 | serper | `jdx jactionlint actionlint fork` |
| 140 | serper | `hk git hooks jdx "pre-push" gitleaks` |
| 141 | serper | `hk.pkl "Builtins.jactionlint"` |
| 142 | serper | `hk jdx "exclusive = true" parallel steps hk.pkl` |
| 143 | last30days | `"jdx hk git hook manager builtins and jactionlint"` with a 3-subquery plan (hk hook manager; jactionlint; pre-push secret scan), `--search reddit,hackernews,github` |
| 188-190 | webclaw | `https://git-scm.com/docs/githooks`, `/docs/git-hook`, `/docs/git-commit` |

`gh-api-releases` is outside the D137 provider enum; it is the read-only GitHub REST releases endpoint.

## 3. Results from each

| Seq | Hits | Top results | Used |
|---|---|---|---|
| 1 | n/a | remainingCredits -128 of 1000 | yes (Firecrawl skipped) |
| 2, 3 | n/a | Serper balance 1307; SerpApi 245 of 250 | yes |
| 4 | n/a | Context7 1000 of 1000 used, resets 2026-11-01 | yes (Context7 skipped) |
| 8 | n/a | ScrapeCreators -7 credits | yes (Last30Days degraded) |
| 9 | 10 | hk.jdx.dev builtins, cli/builtins, configuration, hooks; jdx/hk hk.pkl | yes |
| 10 | 10 | jactionlint.jdx.dev home, install, usage, ci, checks, config, actionlint pages | yes |
| 11 | 10 | jdx/hk releases, release workflows, newreleases v2.5.0 | yes |
| 12 | 10 | hk hooks, configuration, why-hk, hk-example.pkl, glossary | yes |
| 13 | 10 | hk configuration, cli/run/post-commit, hooks | yes |
| 14 | 10 | jdx/hk#749 (gitleaks config, 2026-03-18), jdx/hk hk.pkl, third-party pre-push gitleaks hooks | yes (seed for 146-151) |
| 15 | 10 | jactionlint actionlint and v2-migration pages; jdx/mise#13960 | yes |
| 16 | 10 | hk builtins, hk-example.pkl, jdx/mise hk.pkl, wharflab/tally hk.pkl | partly |
| 19 | 0 | HTTP 404 | no (gap noted) |
| 20-125 | 1 each | 106 doc pages mirrored under `OR/pages/` | yes |
| 132 | 152 | v2.6.0 2026-10-12; v2.5.0 2026-10-04; v2.4.0 2026-09-28 | yes |
| 133 | 6 | jactionlint v2.2.0 2026-10-14; v2.1.0 2026-10-10; v2.0.2, v2.0.0 2026-10-09; v1.8.2, v1.8.0 2026-10-05 | yes |
| 139 | 10 | rhysd/actionlint; jactionlint.jdx.dev; jdx/jactionlint#167 | yes (seed for 161) |
| 140 | 10 | hk configuration, releases, CHANGELOG | no new fact |
| 141 | 2 | jdx/hk hk.pkl at main | yes |
| 142 | 6 | hk configuration, pkl/Config.pkl, hk-example.pkl | corroborates |
| 143 | 32 | jdx/hk#1663, jdx/mise#13920, thedavidweng/OpenKara#488 (actionlint replaced by jactionlint 1.8.2), betterleaks hook PRs; Reddit partial, Hacker News off-topic | yes (seed for 154, 157) |
| 188-190 | 1 each | githooks, git-hook, git-commit manual pages | yes |

## 4. GitHub issues, PRs and discussions searched (stage 2)

| Seq | Search or read | Hits | Seeded by |
|---|---|---|---|
| 144 | `gh search issues "jactionlint" --repo jdx/hk` | 1 (#1681) | 10 |
| 145 | `gh search prs "jactionlint" --repo jdx/hk` | 7 (#1700, #1686, #1687, #1682, #1663) | 10 |
| 146 | `gh search issues "pre-push" --repo jdx/hk` | 15 | 14 |
| 147 | `gh search prs "pre-push" --repo jdx/hk` | 15 (#1352, #1197, #1637) | 14 |
| 148 | `gh search issues "exclusive" --repo jdx/hk` | 10 | 12 |
| 149 | `gh search prs "parallel" --repo jdx/hk` | 15 (#1519, #1495) | 12 |
| 150 | `gh search issues "post-commit" --repo jdx/hk` | 2 | 13 |
| 151 | `gh search prs "gitleaks" --repo jdx/hk` | 13 (#1248, #749) | 14 |
| 152, 153, 155 | `gh pr view 1682`, `1686`, `1687 -R jdx/hk` | 1 each | 10 (via 145) |
| 154 | `gh pr view 1663 -R jdx/hk` | 1 | 143 |
| 156 | `gh pr view 13960 -R jdx/mise` | 1 | 15 |
| 157 | `gh pr view 13920 -R jdx/mise` | 1 | 143 |
| 158, 159 | `gh search issues|prs "hk" --repo jdx/jactionlint` | 4, 15 (#8, #47, #85, #155) | 10 |
| 160 | `gh search issues "zizmor" --repo jdx/jactionlint` | 6 | 16 |
| 161 | `gh issue view 167 -R jdx/jactionlint --comments` | 1 | 139 |
| 162-167 | GraphQL `search(type:DISCUSSION)`: `repo:jdx/hk jactionlint` 0, `pre-push` 23, `parallel` 11, `post-commit` 12, `secret` 4; `repo:jdx/jactionlint hk` 0 | as listed | 10, 14, 12, 13, 14, 10 |
| 168-171 | discussion reads jdx/hk #1139, #1009, #1246, #1063 | 1 each | 12 (via 164), 14 (via 167, 163) |
| 181-187 | `gh api repos/<r>` plus latest 3 releases for taplo, tombi, cmake_format, gersemi, ryl, rumdl, actionlint | 3 each | 137 (tools named by hk's builtin files) |

Both zero-hit discussion searches are `EMPTY_VERIFIED`: both repositories have discussions enabled (seq 126, 127).

## 5. Githubkit saved searches run (reproduced read-only) and proposed rows

`./dev/mise run research:collect` writes into a tracked path, so the equivalent `gh api` calls ran read-only
into `OR/gh/saved/`, each beside a control (`dev/saved-searches.toml` row shape, `dev/collect_saved_search.py`
`collect`, line 44).

| Seq | Row | Query | Hits | Control (seq, hits) |
|---|---|---|---|---|
| 172 | existing `codex-hook-examples` | `SessionStart filename:hooks.json repo:openai/codex` | 0 | `README` (173, 161): the route works, the row is empty today |
| 174 | proposed `hk-builtin-jactionlint` | `jactionlint path:pkl/builtins repo:jdx/hk` | 1 | `README` (175, 62) |
| 176 | proposed `jactionlint-hk-sarif-diff` | `"sarif-diff" repo:jdx/jactionlint` | 5 | `README` (177, 48) |
| 178 | issue search | `jactionlint repo:jdx/hk` (search/issues) | 8 | `repo:jdx/hk is:pr is:merged release` (179, 660) |
| 180 | issue search | `pre-push repo:jdx/hk is:issue` | 15 | as 179 |
| 196 | proposed `hk-builtin-catalog` | `"Builtins.meta" path:pkl/builtins repo:jdx/hk` | 165 | none needed: a count watch |
| 197 | probe | `"profile:" path:.github repo:jdx/jactionlint` | 1 | not proposed |

The proposed rows are in section 10.

## 6. Stage-2 searches against the stage-1 results (seed-to-search map)

| Stage-1 seed | What it named | Stage-2 rows |
|---|---|---|
| 9 (Exa: hk builtins docs) | jdx/hk | 137 clone; 172-173 route check; 196 |
| 10 (Exa: jactionlint) | jdx/jactionlint, hk builtin | 138 clone; 144-145; 152, 153, 155; 158-159; 162, 166; 174-179; 197 |
| 11 (Exa: hk releases) | release v2.6.0 | 132, 134, 135 |
| 12 (Exa: parallel, exclusive) | `exclusive`, `depends`, stash | 148, 149, 164, 168, 169 |
| 13 (Exa: post-commit) | `hk run post-commit` | 150, 165 |
| 14 (Exa: pre-push gitleaks) | jdx/hk#749, gitleaks builtin | 146, 147, 151, 163, 167, 170, 171, 180 |
| 15 (Exa: jactionlint vs actionlint) | jdx/mise#13960 | 156 |
| 16 (Exa: hk.pkl examples) | zizmor and other builtins | 160 |
| 137 (hk clone, builtin files) | taplo, tombi, cmake_format, gersemi, ryl, rumdl, actionlint | 181-187 |
| 139 (Serper) | jdx/jactionlint#167 | 161 |
| 143 (Last30Days) | jdx/hk#1663, jdx/mise#13920 | 154, 157 |

## 7. Findings with citations

### 7.1 Versions and what changed

- Latest hk release: v2.6.0, 2026-10-12 (seq 132; `OR/gh/releases/hk-releases.json`). Installed on PATH:
  hk 2.6.0 (`hk --version`). MP's `hk.pkl:1` amends the v2.5.0 package with `min_hk_version = "2.5.0"`
  (`hk.pkl:6`). TR also amends v2.5.0.
- 2.5.0 to 2.6.0 ([v2.6.0](https://github.com/jdx/hk/releases/tag/v2.6.0), `OR/pages/gh-hk-release-v2.6.0.md`):
  `Builtins.jactionlint` (#1663) and Typst builtins (#1646); a success line after passing runs (#1678);
  more shebang file types (#1676, #1680); `hk agent stop-hook` passes in projects without hk (#1649); pklr v5
  config loading (#1650); breaking only for `Builtins.ryl` with ryl older than 0.22.
- What 2.5.0 itself brought that MP and TR rely on or should
  ([v2.5.0](https://github.com/jdx/hk/releases/tag/v2.5.0)): read-only checks run in parallel in fix hooks
  (#1586); top-level `jobs` actually applied (#1594); `HK_STASH_LOCK_TIMEOUT` and a cross-worktree stash lock
  (#1636, #1637); stash recovery after SIGTERM or a crash (#1641); `min_hk_version` enforced (#1590);
  `--safe` refuses plain-string commands with no declared effect (#1573); cold config load about 0.07 s (#1581).
- Unreleased on hk main (`v2.6.0..eb9a149`, `OR/repos/hk`; release PR
  [jdx/hk#1686](https://github.com/jdx/hk/pull/1686), open since 2026-10-12): jactionlint SARIF findings and
  fixes (#1687), `profile_condition` (#1684), `hk validate --json --deny-warnings` (#1699), rendered SARIF
  findings in failed output (#1695); [#1700](https://github.com/jdx/hk/pull/1700) bumps jactionlint to 2.2.0.

### 7.2 Live hook state on this host (verified, read-only)

- The global install is config-based: `git config --global` holds `hook.hk-pre-commit.command`
  (`... mise x hk -- hk run pre-commit --from-hook --staged`), `hook.hk-commit-msg.*` and `hook.hk-pre-push.*`
  only; MP has no local `hook.*` entries and no `.git/hooks` scripts (`hooks:install` has not run, D2).
  hk picks a global install's events from the project config present at install time, else
  `commit-msg, pre-commit, pre-push, prepare-commit-msg` (hk `src/cli/install.rs:11`, `:337-353`), so MP's
  `pre-merge-commit` retro gate (`hk.pkl:16-21`) never fires here.
- `mise x hk -- hk --version` in MP prints hk 2.5.0 while `hk` on PATH is 2.6.0: the launcher asks mise for the
  registry tool `hk`, but the user's global config pins `packslip:github.com/jdx/hk` 2.6.0, so `mise x hk`
  falls back to the older `hk` install. A config with `min_hk_version = "2.6.0"` would be refused by every
  global hook until this changes (a global change needs its own admission).
- Bypasses: the launcher is `test "${HK:-1}" = "0" || ...`, so `HK=0` skips every hk hook, post-commit included
  ([hooks](https://hk.jdx.dev/hooks.html), `OR/pages/hk-hooks.md:296`); the hk binary itself does not read `HK`
  (no reference in `OR/repos/hk/src`). `git commit --no-verify` bypasses only pre-commit and commit-msg
  ([git-commit](https://git-scm.com/docs/git-commit), `OR/pages/git-commit.md:199-203`); `git merge
  --no-verify` bypasses pre-merge-commit (`OR/pages/git-githooks.md:94-97`); post-commit always runs and cannot
  block (`OR/pages/git-githooks.md:139-142`). A09 commits with `commit-tree` and pushes with `--no-verify`
  (`dev/git_delivery.py:379`, `:415`), so no hk hook ever sees an A09 publish; its own outbound scan
  (`dev/git_delivery.py:292`, `:392`) and the Bash PreToolUse gate cover that path (`docs/agents/hooks-and-mods.md`).
- Parent note from R19, folded in: on Git 2.54, `-c core.hooksPath=/dev/null` does not disable config-based
  hooks; `-c hook.<name>.enabled=false` does (documented in `OR/pages/git-hook.md:420-423`). The timing clone
  here used `HK=0` for the clone and `hook.hk-pre-commit|commit-msg|pre-push.enabled=false` in its local
  config. The event-wide `hook.<event>.enabled` key is documented for Git 2.55 (`OR/pages/git-hook.md:432-435`)
  and is UNVERIFIED on 2.54.

### 7.3 How hk parallelism works, and how to keep every hook parallel safely

- Jobs: `jobs` defaults to 0, meaning one job per CPU (`OR/repos/hk/settings.toml:201-207`,
  `src/settings.rs:129`; 12 on this host); sources are `--jobs/-j`, `HK_JOBS` (or `HK_JOB`), `git config
  hk.jobs` and Pkl `jobs` (`OR/pages/hk-configuration.md:2561-2583`). `fail_fast` defaults to true
  (`settings.toml:103-107`).
- Scheduling: steps run concurrently up to the job limit unless `depends`, `exclusive`, a `Group` boundary or
  file locks make them wait (`OR/pages/hk-hooks.md:188`). `exclusive = true` waits for earlier steps and
  blocks later ones (`OR/pages/hk-configuration.md:1914`). `batch = true` splits one step's files across the
  shared job budget (`:1608`). `stomp = true` bypasses file locks (`:1648`).
- Locks: a job takes write locks only when the run is a fix run and the step may write
  (`src/step_job.rs:297-302`); a check-only step whose `check` declares `effect = "read"` keeps read locks even
  in fix runs (`:313-330`), and a check with no declared effect is treated as a writer. So a hook without
  `fix = true` is fully parallel; in `hk fix`, declared-read checks still run beside each other (v2.5.0 #1586).
- Stash: hooks default to `stash = "none"` unless the config has top-level `steps`, which makes pre-commit
  stash with Git (`OR/pages/hk-hooks.md:115`); `--staged` checks staged paths with their worktree contents and
  never stashes (`:75`). Stashing serialises across worktrees on `hk-stash.lock` (v2.5.0 #1636).
- Git index: parallel steps that write the index collide on `index.lock`
  ([discussion #1139](https://github.com/jdx/hk/discussions/1139), 2026-07-31). MP's gates only read Git; the
  proposal still sets `GIT_OPTIONAL_LOCKS=0` on pre-commit and pre-push so a `git status` inside a gate never
  takes the lock opportunistically.
- Rules that keep MP's hooks parallel: (1) every custom step is a `CommandSpec` with `effect = "read"`;
  (2) pre-commit, commit-msg, pre-merge-commit, post-commit and pre-push stay check-only with `stash = "none"`,
  and fixing is the manual `hk fix` hook; (3) leave `jobs` unset and use `HK_JOBS` per run; (4) any future step
  that writes a shared resource (a C++ build directory, the index) gets `exclusive = true` or its own group;
  (5) CI runs `hk check --all --no-fail-fast` to see every finding.

### 7.4 jactionlint

- What: a maintained fork of rhysd/actionlint by jdx, binary `jactionlint`
  ([jdx/jactionlint](https://github.com/jdx/jactionlint), clone `8f0ce5d`, 2026-10-14). v2.0.0 (2026-10-09) added
  stable rule IDs, three profiles (`correctness`, `default`, `pedantic`), fixes, baselines and POSIX options;
  its default profile adds security and policy rules such as `unpinned-uses`, `missing-permissions`,
  `missing-timeout` and `concurrency-limits` (`OR/pages/ja-v2-migration.md:35-50`;
  `OR/pages/ja-rules.md:380`, `:454-455`, `:500`). `correctness` keeps actionlint's checks
  (`OR/pages/ja-actionlint.md:6-16`). It has a rule for each zizmor 1.30.1 audit (`OR/pages/ja-zizmor-parity.md:6`).
- Release and churn: v2.2.0 today (2026-10-14), v2.1.0 on 2026-10-10; both release notes warn that a run clean
  on the previous version can show new findings (seq 133). Pin an exact version and bump it on purpose; jdx pins
  `"2"` because `mise lock --bump` still resolved `latest` to 1.8.2 ([#1682](https://github.com/jdx/hk/pull/1682)).
- Install route: the mise registry entry `jactionlint` (`github:jdx/jactionlint`, `mise registry jactionlint`;
  added by [jdx/mise#13960](https://github.com/jdx/mise/pull/13960), 2026-10-05), so a `mise.dev.toml` row plus
  `mise.dev.lock`; also Homebrew, pip, Docker and a GitHub Action (`OR/pages/ja-install.md:40-101`).
- hk integration: `Builtins.jactionlint` exists in hk 2.6.0 but checks only `.github/workflows/*.y*ml`, has no
  fix, and parses gcc-style text (`OR/repos/hk/pkl/builtins/jactionlint.pkl` at v2.6.0). hk main's version
  ([#1687](https://github.com/jdx/hk/pull/1687), 2026-10-12) runs `--format gcc`, adds a `check_diff` through
  `hk util sarif-diff` (present in hk 2.6.0) and a `jactionlint --fix` fixer, and adds composite actions and
  Dependabot files. The proposal amends the 2.6.0 builtin to exactly that until hk 2.7.0 ships. jactionlint's
  own repository runs this shape with `diagnostic_format = "sarif"` (`OR/repos/jactionlint/hk.pkl`).
- Versus actionlint, zizmor, ghalint, pinact on MP (proxies, run read-only): actionlint 1.7.12 finds nothing;
  zizmor reports `artipacked`, `excessive-permissions` and `unpinned-uses`; ghalint reports job permissions and
  SHA pins; pinact would pin 6 `uses:` lines across all 3 workflows. jactionlint's default profile covers these
  classes in one tool, which is why hk itself dropped zizmor. MP's `acceptance.yml` is frozen
  (`evidence/onboarding/baseline-files.json:10`), so its findings go into `.github/jactionlint-baseline.json` with
  `baseline: auto` (`OR/pages/ja-baseline.md:92-102`); `development.yml` and `research-fast.yml` take fixes.
  Expected default-profile findings are UNVERIFIED until jactionlint runs on MP.

### 7.5 Measured findings on MP today (scratch clone at `132e8e3`)

| Tool, scope | Findings | Consequence |
|---|---|---|
| ruff 0.16.10, default rules, 126 Python files | 827 (isolated) | style migration of code slated for C++; not proposed |
| ruff `--select E9,F63,F7,F82` | 12, all `F821 undefined name run` in `dev/toolchains/p2996_math_probe.py:166-204` | a real latent bug; fix or delete (allowed under D112) before the step blocks |
| ruff format | 126 of 126 files would change | skip (`ruff_format`) |
| ty 0.0.85 | 1211 diagnostics | opt-in profile `types` |
| shellcheck, non-frozen scripts | 1 warning, `dev/mise:15` SC2155 | small shell fix; frozen `ci/acceptance.sh` has 6 info findings, excluded |
| shfmt with `-i 4` | 0 (tabs default: `dev/mise` would change) | override indentation |
| taplo format (tombi unmeasured) | 4 files, one frozen (`mise.toml`) | prefer tombi; verify on first run |
| rumdl, docs outside `.planning` | 1543 (1478 `MD013`); 59 in 31 files with `MD013` off | add `.rumdl.toml`; `.planning` alone has 12790 |
| typos | 2 real (`unparseable`, `dito`) plus 1 test string | fix, or `_typos.toml` |
| lychee `--offline` on docs | 3 broken local links | fix |
| clang-format (no `.clang-format`) | 159 warnings in 8 files | opt-in profile `cxx` until the C++ check ticket sets a style |
| shebang scripts not executable | 22 Python files | opt-in profile `adopt` (mode change decision) |
| commit-msg, default types | 16 of 28 subjects pass; 23 of 28 with `records,retro` added | 2 `Integrate lane ...`, 2 `Marketplace ...`, 1 `slice 3` fail: a convention decision |
| safety utilities, `jq empty`, pkl format, `hk validate`, python debug statements | 0 | blocking now |
| gitleaks or betterleaks, `HEAD` history | 226 `generic-api-key` in `evidence/`, 0 private-name | evidence needs the scanner's allowlist or baseline (R17) before a range scan meets old commits |
| betterleaks, MP `--branches --not --remotes` (167 commits) / `HEAD --not --remotes` (4) | 733 / 0 | the superset guard blocks until old-history local branches go (D143/D148) |

### 7.6 Proposed hk.pkl (not applied)

Validated with hk 2.6.0 (`hk validate`) and formatted with `pkl format` in the scratch clone; also at
`OR/local/proposal/hk.pkl`. `secretScanner` is the Q123 parameter for R17.

```pkl
amends "package://github.com/jdx/hk/releases/download/v2.6.0/hk@2.6.0#/Config.pkl"

import "package://github.com/jdx/hk/releases/download/v2.6.0/hk@2.6.0#/Builtins.pkl"

// hk 2.6.0 (latest release, 2026-10-12). Enforced since hk 2.5.0: an older hk refuses this file.
min_hk_version = "2.6.0"
// jobs: unset on purpose. 0 means one job per CPU (12 on this host); override per run with HK_JOBS or -j.
// Immutable receipts, untracked mirrors and generated lockfiles are never linted.
exclude = List("evidence/**", "offline/**", "**/*.lock", "uv.lock")

// The 19 acceptance-baseline files (evidence/onboarding/baseline-files.json). No fixer may rewrite
// them and no style check may demand an edit to them; check:acceptance-baseline proves the hashes.
local frozen =
  List(
    ".claude-plugin/marketplace.json",
    ".github/workflows/acceptance.yml",
    ".gitignore",
    "README.md",
    "ci/acceptance.sh",
    "mise.lock",
    "mise.toml",
    "plugins/aggregated-research/.claude-plugin/plugin.json",
    "plugins/aggregated-research/.lsp.json",
    "plugins/aggregated-research/README.md",
    "plugins/aggregated-research/bin/aggregated-research",
    "plugins/aggregated-research/bin/mise-env",
    "plugins/aggregated-research/bin/ty",
    "plugins/aggregated-research/docs/bin-wrapper-decision.md",
    "plugins/aggregated-research/hooks/hooks.json",
    "plugins/aggregated-research/mise.toml",
    "plugins/aggregated-research/skills/aggregated-research/SKILL.md",
    "plugins/aggregated-research/skills/aggregated-research/references/acceptance-509.md",
    "plugins/aggregated-research/spine-budgets.toml",
  )
// Parent-owned planning records and tracked scratch: safety checks only, no style checks.
local styleExclude = frozen + List(".planning/**", "scratch/**", "dev/fixtures/**")

// Q123 secret and private-name guard. The scanner is R17's decision; gitleaks 8.30 and
// betterleaks 1.9 both take `git --log-opts=...` and read the repository's .gitleaks.toml.
local secretScanner = "gitleaks"

// Safety checks: hk's in-process utilities plus a JSON parse. All read-only, so they share read locks.
local safety = new Mapping<String, Step> {
  ["large-files"] = Builtins.check_added_large_files
  ["case-conflict"] = Builtins.check_case_conflict
  ["merge-conflict"] = Builtins.check_merge_conflict
  ["symlinks"] = Builtins.check_symlinks
  ["destroyed-symlinks"] = Builtins.destroyed_symlinks
  ["private-key"] = Builtins.detect_private_key
  ["submodules"] = Builtins.forbid_submodules
  ["mixed-line-ending"] = Builtins.mixed_line_ending
  ["byte-order-marker"] = Builtins.byte_order_marker
  ["executables-have-shebangs"] = Builtins.check_executables_have_shebangs
  ["json-parse"] {
    glob = "**/*.json"
    batch = true
    check = new CommandSpec {
      command = new Command { argv = List("jq", "empty", "{{files}}") }
      effect = "read"
    }
  }
}

// Style and correctness linters, one native tool per file type.
local linters = new Mapping<String, Step> {
  ["ruff"] = (Builtins.ruff) {
    exclude = styleExclude
    // Correctness rules only: existing Python takes fixes and deletions, not a style migration (D112).
    check = new CommandSpec {
      command = new Command {
        argv = List("ruff", "check", "--force-exclude", "--select", "E9,F63,F7,F82", "{{files}}")
      }
      effect = "read"
    }
  }
  ["python-debug-statements"] = (Builtins.python_debug_statements) { exclude = styleExclude }
  ["shellcheck"] = (Builtins.shellcheck) { exclude = styleExclude }
  ["shfmt"] = (Builtins.shfmt) {
    exclude = styleExclude
    // MP's scripts indent with four spaces; shfmt defaults to tabs.
    check_diff = new CommandSpec {
      command = "shfmt -i 4 -d --apply-ignore {{ files }}"
      effect = "read"
    }
    check_list_files = new CommandSpec {
      command =
        """
        files=$(shfmt -i 4 -l --apply-ignore {{ files }})
        if [ -n "$files" ]; then
        echo "$files"
        exit 1
        fi
        """
      effect = "read"
    }
    fix = new CommandSpec { command = "shfmt -i 4 -w --apply-ignore {{ files }}"; effect = "write" }
  }
  ["tombi"] = (Builtins.tombi) { exclude = styleExclude }
  ["tombi-format"] = (Builtins.tombi_format) { exclude = styleExclude }
  ["rumdl"] = (Builtins.rumdl) { exclude = styleExclude }
  ["typos"] = (Builtins.typos) { exclude = styleExclude }
  // hk 2.6.0's builtin checks workflows only and has no fix. This is hk main's definition (jdx/hk#1687,
  // unreleased v2.7.0); replace it with `Builtins.jactionlint` once hk 2.7.0 ships. acceptance.yml is
  // frozen, so its findings live in .github/jactionlint-baseline.json (`baseline: auto`).
  ["jactionlint"] = (Builtins.jactionlint) {
    glob =
      List(".github/workflows/*.y*ml", ".github/actions/**/action.y*ml", ".github/dependabot.y*ml")
    check = new CommandSpec {
      command = new Command { argv = List("jactionlint", "--format", "gcc", "{{files}}") }
      effect = "read"
    }
    check_diff = new CommandSpec {
      command = new Command {
        argv =
          List("hk", "util", "sarif-diff", "--", "jactionlint", "--format", "sarif", "{{files}}")
      }
      effect = "read"
    }
    fix = new CommandSpec {
      command = new Command { argv = List("jactionlint", "--fix", "{{files}}") }
      effect = "write"
    }
  }
  ["pkl-format"] = Builtins.pkl_format
  ["hk-validate"] {
    glob = List("hk.pkl", "hk.local.pkl")
    check = new CommandSpec {
      command = new Command { argv = List("hk", "validate") }
      effect = "read"
    }
  }
  ["newlines"] = (Builtins.newlines) { exclude = styleExclude }
  ["trailing-whitespace"] = (Builtins.trailing_whitespace) { exclude = styleExclude }
  ["smart-quotes"] = (Builtins.fix_smart_quotes) { exclude = styleExclude }
  ["links-offline"] = (Builtins.lychee) {
    glob = List("**/*.md")
    exclude = styleExclude
    check = new CommandSpec {
      command = new Command {
        argv =
          List(
            "lychee",
            "--no-progress",
            "--offline",
            "--include-fragments",
            "--root-dir",
            "{{root}}",
            "{{files}}",
          )
      }
      effect = "read"
    }
  }
}

// Opt-in until their one-time cleanups land (findings measured 2026-10-14 in the R18 report).
local adopt = new Mapping<String, Step> {
  ["ty"] = (Builtins.ty) { exclude = styleExclude; profiles = List("types") }
  ["clang-format"] = (Builtins.clang_format) { exclude = styleExclude; profiles = List("cxx") }
  ["shebang-scripts-are-executable"] = (Builtins.check_shebang_scripts_are_executable) {
    exclude = styleExclude
    profiles = List("adopt")
  }
}

// Gates that already exist as mise tasks; they read Git and records only.
local recordsGate = new Mapping<String, Step> {
  ["records"] {
    check = new CommandSpec { command = "./dev/mise run check:records"; effect = "read" }
  }
}

hooks {
  // Check-only and unstashed: nothing rewrites or restages files, so every step takes read locks
  // and runs at once up to `jobs`. Both launchers below pass --staged.
  ["pre-commit"] {
    stash = "none"
    env { ["GIT_OPTIONAL_LOCKS"] = "0" }
    steps {
      ...safety
      ...linters
      ...recordsGate
      ["secrets-staged"] {
        check = new CommandSpec {
          command = new Command {
            argv =
              List(
                secretScanner,
                "git",
                "--config",
                ".gitleaks.toml",
                "--pre-commit",
                "--staged",
                "--redact",
                "--no-banner",
              )
          }
          effect = "read"
        }
      }
    }
  }
  ["commit-msg"] {
    steps {
      // records and retro are this repository's own types; "Integrate lane ..." subjects need a type too.
      ["conventional-commit"] = (Builtins.check_conventional_commit) {
        check = new CommandSpec {
          command =
            "hk util check-conventional-commit --allowed-types build,chore,ci,docs,feat,fix,perf,refactor,revert,style,test,records,retro {{commit_msg_file}}"
          effect = "read"
        }
      }
    }
  }
  ["pre-merge-commit"] {
    stash = "none"
    steps {
      ["retro-gate"] {
        check = new CommandSpec { command = "./dev/mise run retro:gate-merge"; effect = "read" }
      }
    }
  }
  ["post-commit"] {
    // Cannot block (Git ignores its exit status); warns at once when a commit made with
    // --no-verify carries a secret, before the pre-push guard refuses it.
    steps {
      ["secrets-head"] {
        check = new CommandSpec {
          command = new Command {
            argv =
              List(
                secretScanner,
                "git",
                "--config",
                ".gitleaks.toml",
                "--log-opts=-1",
                "--redact",
                "--no-banner",
              )
          }
          effect = "read"
        }
      }
    }
  }
  ["pre-push"] {
    stash = "none"
    env { ["GIT_OPTIONAL_LOCKS"] = "0" }
    steps {
      ["retro-gate"] {
        check = new CommandSpec { command = "./dev/mise run retro:gate-push"; effect = "read" }
      }
      // Every commit on a local branch that no remote has: a superset of what any push sends, scanned
      // as history (hk's pre-push file list would scan worktree copies, which can differ). It refuses
      // pushes while old-history local branches exist (D143/D148); interim: "--log-opts=HEAD --not --remotes".
      ["secret-guard"] {
        check = new CommandSpec {
          command = new Command {
            argv =
              List(
                secretScanner,
                "git",
                "--config",
                ".gitleaks.toml",
                "--log-opts=--branches --not --remotes",
                "--redact",
                "--no-banner",
              )
          }
          effect = "read"
        }
      }
    }
  }
  ["check"] { steps { ...safety; ...linters; ...adopt } }
  ["fix"] {
    fix = true
    stash = "git"
    steps { ...safety; ...linters; ...adopt }
  }
}
```

Why the guard uses `--branches --not --remotes`: it names, without any parsing, every commit reachable from a
local branch and from no remote-tracking ref, which is a superset of what any `git push` sends (all refs, not
only the first, which is all hk's own range uses, `src/cli/run/pre_push.rs:152-187`). It mirrors A09's scan
shape (`gitleaks git --log-opts=<range>`, `dev/git_delivery.py:292`, `:392`). Not to use: `Builtins.gitleaks`
in its default `dir .` mode, which scans the whole worktree including ignored paths such as `offline/`
([discussion #1246](https://github.com/jdx/hk/discussions/1246), fixed to `.` by
[#1248](https://github.com/jdx/hk/pull/1248)).

The range's cost today, measured read-only on MP itself: 167 commits on 10 local branches are on no remote
(`git log --branches --not --remotes`; per branch from 1 to 137 commits, all but the current branch's 4 are
old history replaced by D143/D148), and betterleaks finds 733 findings in them (2.16 s). So the superset range
blocks manual pushes until those local branches are rebased or deleted; until then swap in
`"--log-opts=HEAD --not --remotes"` (4 commits, no findings, 0.32 s betterleaks, 0.55 s gitleaks). A range
built from the refs on the hook's stdin (`{{hook_stdin}}`) would be exact for every push but needs parsing
(zero SHAs for deletions, several refs), which is logic: it belongs in the C++ gate port (D131), not in shell
inside hk.pkl or in Python. A09 is unaffected either way (it pushes with `--no-verify` and scans its own range).

Rows the proposal needs in `mise.dev.toml` (not frozen; refresh `mise.dev.lock` with `./dev/mise run
deps:lock`):

```toml
[tools]
python = "3.15.0"
uv = "0.13.0"
# hk and every tool an hk step runs (R18, D150): exact pins, checksums in mise.dev.lock
hk = "2.6.0"
jactionlint = "2.2.0"   # 2.1.0 if the age gate holds back today's release; write the baseline with the pinned one
gitleaks = "8.30.1"     # Q123 scanner parameter; R17 may pick betterleaks = "1.9.0"
ruff = "0.16.10"
shellcheck = "0.11.0"   # also used by jactionlint for run: scripts
shfmt = "3.14.1"
tombi = "1.8.4"
rumdl = "0.2.79"
typos = "1.51.1"
lychee = "0.24.2"
jq = "1.8.2"
pkl = "0.32.1"
ty = "0.0.85"           # profile "types" only
# clang-format: left to the C++ check ticket, matched to the project's LLVM
```

And one task change (config, D2-gated, run only by the parent): `hooks:install` (`mise.dev.toml:340-343`) writes
local config hooks whose command is `./dev/mise x -- hk run <event> --from-hook` (plus `--staged` for
pre-commit) for `pre-commit`, `commit-msg`, `pre-merge-commit`, `post-commit` and `pre-push`, instead of
`hk install --force-local`. A local `hook.hk-<event>` replaces the global one of the same name
(`src/cli/install.rs:462-467`), so MP gets pinned tools and hk 2.6.0 while other repositories keep the
global launcher. `./dev/mise x -- true` costs 0.26 to 0.33 s per hook start (measured). `hk install --mise`
is not the fit: it writes plain `mise x`, which reads the frozen root `mise.toml` (the OCI image) instead of
`mise.dev.toml`. New config files the steps need: `.github/jactionlint.yaml` (`baseline: auto`),
`.github/jactionlint-baseline.json` (generated), `.rumdl.toml` (`MD013` off), optionally `_typos.toml`.
CI: one step in `research-fast.yml` after `tools:prepare` (`.github/workflows/research-fast.yml:37`):
`./dev/mise x -- hk check --all --no-fail-fast`. `acceptance.yml` is frozen and stays untouched.

Frozen files and what they mean: `hk.pkl`, `mise.dev.toml`, `mise.dev.lock`, `development.yml` and
`research-fast.yml` are not in the 19-file baseline, so a normal lane may change them. The root `mise.toml`
and `mise.lock` (`baseline-files.json:30`, `:35`) define the container image and must never gain hk or linters;
`acceptance.yml`, `ci/acceptance.sh` and `.gitignore` (`:10`, `:25`, `:15`) cannot take a fix, so the proposal
excludes all 19 from style checks and fixers and baselines `acceptance.yml` in jactionlint. The `frozen` list
duplicates `baseline-files.json`; that is small config debt, caught anyway by `check:acceptance-baseline` if a
fixer ever rewrote one.

Post-commit options considered: (a) nothing (no blocking value; Git waits for it on every commit); (b) a
warn-only secret scan of HEAD (chosen: 0.35 s with gitleaks, 0.05 s with betterleaks, measured; it is the one
check that still runs after `--no-verify`); (c) re-running the pre-commit linters on HEAD (doubles commit
time for a warning nobody must read); (d) regenerating artefacts, as TR does (writes files after the commit
and leaves a dirty tree). A doctor post-commit surface would be new Python logic (forbidden, D112); it belongs
to the C++ doctor port.

### 7.7 Timing (scratch clone, Apple Silicon, 12 CPUs, 3 runs each, `OR/local/timing/`)

| Run | Parallel (jobs 0) | Serial (`HK_JOBS=1`) |
|---|---|---|
| Today: `hk run pre-commit --all` (records step) | 0.38 to 0.52 s | n/a |
| Today: `hk run pre-push` (retro gate) | 0.15 to 0.16 s | n/a |
| Today: `hk check --all` | fails: `Hook 'check' not found` | n/a |
| Proposed `hk run pre-commit --staged`, 9 staged files, 22 steps | 0.39 to 0.42 s (hk 311 ms, step sum 1073 ms) | 0.93 to 0.95 s |
| Proposed `hk check --all`, 23 steps run | 0.59 to 0.63 s (hk 466 ms) | 1.32 to 1.36 s |
| Probe: all 32 candidate builtins over the repository | 1.9 s real (hk 1310 ms, step sum 10.4 s) | n/a |
| Proposed `hk run pre-push`, 1 unpushed commit | 0.34 to 0.37 s | 0.44 s |
| Proposed `hk run post-commit` | 0.35 s | n/a |
| gitleaks `git --log-opts=HEAD` (27 commits) / `--all` (188) | 9.1 s / 16.0 s | betterleaks `--all`: 3.3 s |
| On MP itself: `HEAD --not --remotes` (4 commits) / `--branches --not --remotes` (167) | gitleaks 0.55 s, betterleaks 0.32 s / betterleaks 2.16 s | n/a |

The secret scan is each hook's critical path (gitleaks about 0.28 s even for one commit). Steps for tools not
installed here (tombi, tombi-format, jactionlint) were skipped with `HK_SKIP_STEPS`; their proxies took 39 to
76 ms (taplo) and 67 ms (actionlint) in the probe run.

### 7.8 TR as reference (generic, no private names)

TR amends hk 2.5.0, hard-codes 8 jobs (`jobs = 8` in its hk.pkl, `HK_JOBS = "8"` in its mise env and
`-j ${HK_JOBS:-8}` in its tasks), and enables 19 builtins on pre-commit (ruff, ruff_format, ty,
python_check_ast, python_debug_statements, betterleaks, typos, rumdl, rumdl_format, taplo, taplo_format,
lychee, mise, trailing_whitespace, newlines, check_merge_conflict, detect_private_key,
check_executables_have_shebangs, check_added_large_files) plus seven custom steps with no glob and no declared
effect (six start a Python entry point through `uv run`, one lists daemons). Its pre-commit has no `fix`, so it
only checks. Gaps to avoid: hard-coded jobs;
plain-string custom steps (writers in fix mode, refused by `--safe`); a pre-commit that stashes implicitly
because the config has top-level `steps`; online `lychee` on every commit; `betterleaks dir` on staged paths
(worktree content, not staged content); post-commit and post-checkout steps that regenerate files after the
commit; a prepare-commit-msg step that rewrites messages with Python; no pre-push, no commit-msg, no GitHub
Actions linter and no CI at all; a builtin audit document generated by a custom Python script whose summary
line already disagrees with the config. MP takes the parts that hold (one native tool per file type, rumdl,
typos, safety utilities) and none of the custom Python.

### 7.9 Builtin list (163 in hk 2.6.0) with decisions

Cost is the measured whole-repository wall time in the probe or proposal run; per-commit cost is lower.

| Builtin | Decision | Reason and cost |
|---|---|---|
| check_added_large_files, check_case_conflict, check_merge_conflict, check_symlinks, destroyed_symlinks, detect_private_key, forbid_submodules, mixed_line_ending, byte_order_marker, check_executables_have_shebangs | keep (pre-commit, check) | hk in-process, no tool; 0 findings; 7 to 153 ms |
| newlines, trailing_whitespace, fix_smart_quotes | keep, style scope | hk in-process; findings only in `.planning` or frozen files; 15 to 47 ms |
| check_shebang_scripts_are_executable | profile `adopt` | 22 Python files; mode change is a decision; 169 ms |
| no_commit_to_branch | skip | MP integrates on `codex/...` and publishes via A09 `commit-tree`, which skips hooks |
| check_conventional_commit | keep (commit-msg) with `--allowed-types ...,records,retro` | 23 of 28 subjects pass; 5 need a convention decision |
| cocogitto_commit_msg, harper_commit_message | skip | duplicate of the above; extra tools |
| ruff | keep, correctness rules | 12 findings (one file); 18 ms scoped, 889 ms with all default rules |
| ruff_format | skip | rewrites 126 of 126 files of retiring Python |
| ty | profile `types` | 1211 diagnostics; 1009 ms |
| python_debug_statements | keep | 0 findings; 55 ms |
| python_check_ast | skip | ruff `E9` and `dev/check.py` compile already parse |
| mypy, pylint, black, isort, flake8 | skip | superseded by ruff and ty (native); not installed |
| shellcheck | keep | 1 warning outside frozen files; 38 to 507 ms |
| shfmt | keep with `-i 4` | 0 findings; 13 to 15 ms |
| shellharden | skip | overlaps shellcheck; rewrites quoting |
| tombi, tombi_format | keep | active (v1.8.4, 2026-10-12); schema-aware; unmeasured here |
| taplo, taplo_format | skip | last release 0.10.0 on 2025-05-23 (seq 181) |
| mise | skip | runs `mise fmt --check` on `mise.toml` without file arguments, and the root `mise.toml` is frozen |
| jq | skip as formatter | it reformats with sorted keys; a `jq empty` parse step is kept instead (24 to 58 ms) |
| yq, yamlfmt | skip | formatters; the only YAML is three workflows, one frozen |
| yamllint, ryl, ryl_markdown | skip for now | jactionlint parses the workflows; yamllint is Python; ryl is young (87 stars) |
| rumdl | keep with `.rumdl.toml` | 59 findings after `MD013` off; 68 ms scoped |
| rumdl_format | skip in hooks | `hk fix` can use rumdl's own fixer |
| markdown_lint, mado, mdschema, contextlint, textlint, vale, harper | skip | one Markdown linter is enough; Node or prose tools; not installed |
| typos | keep | 2 real findings; 427 to 434 ms (the slowest scoped step) |
| lychee | keep with `--offline --include-fragments` | 3 broken doc links; 161 to 247 ms; no network on commit |
| lychee_extended, renovate_deps | skip | need flint |
| pkl_format | keep | 0 findings after formatting; 33 to 42 ms |
| pkl | skip | `pkl eval` on hk.pkl fetches packages and hk's own config disables it; `hk validate` step instead (99 to 116 ms) |
| hk_test | skip | no step-defined tests; would run builtin test suites |
| jactionlint | keep, amended to hk main's definition | needs install; proxies 29 to 886 ms |
| actionlint | skip | deprecated in the mise registry; jactionlint `correctness` covers it |
| zizmor, ghalint_workflow, ghalint_action | skip | jactionlint default profile covers their classes (hk dropped zizmor, #1682) |
| pinact | skip as hook; optional one-off | jactionlint `unpinned-uses` reports; `pinact run` once to pin `development.yml` and `research-fast.yml` |
| pinact_update | skip | Renovate-style updates are not a commit gate |
| gitleaks, betterleaks, kingfisher | scanner is R17's | used through custom `git` steps, not the builtins' `dir` mode |
| clang_format | profile `cxx` | 159 warnings, no `.clang-format`; style belongs to the C++ ticket |
| cpp_lint | skip | cpplint is a Python Google-style checker; clang-tidy (not a builtin) is the native route |
| cmake_format | skip | cmakelang last released 2020-08-19 (seq 183); gersemi (active, not a builtin) could be a custom step later |
| hadolint, droast, dclint | skip | MP has no Dockerfile or compose file (the image is `mise oci build`) |
| editorconfig-checker, ls_lint | skip | MP has no `.editorconfig` or naming rules |
| dprint, prettier, biome | skip | no JS or TS; one formatter per type already chosen |
| aqua_update_checksum, xmllint | skip | no aqua config or XML |
| Go (14): err_check, go_fix, go_fmt, go_fumpt, go_imports, go_lines, go_sec, go_vet, go_vuln_check, golangci_lint, golangci_lint_fmt, gomod_tidy, revive, staticcheck | skip | no files of the type in MP |
| JavaScript and TypeScript (14): deno, deno_check, eslint, knip, ox_lint, oxfmt, sherif, standard_js, tsc, tsserver, vp_check, vp_fmt, vp_lint, xo | skip | no files of the type |
| Ruby (9): brakeman, bundle_audit, erb, fasterer, reek, rubocop, rubocop_server, sorbet, standard_rb | skip | no files of the type |
| Rust (5): cargo_check, cargo_clippy, cargo_deny, cargo_fmt, rustfmt | skip | no files of the type |
| Infrastructure (10): hclfmt, kube_linter, kubeconform, terraform, terraform_docs, terraform_validate, terragrunt_hcl_fmt, terragrunt_hcl_validate, tf_lint, tofu | skip | no files of the type |
| Nix (6): alejandra, deadnix, nil, nix_fmt, nixf_diagnose, nixpkgs_format | skip | no files of the type |
| Lua (3): luacheck, selene, stylua; Elixir (3): mix_compile, mix_fmt, mix_test; Typst (2): tinymist, typstyle | skip | no files of the type |
| Others (16): asciidoctor, astro, buf_format, buf_lint, buildifier_format, buildifier_lint, dotnet_format, google_java_format, just_format, ktlint, php_cs, sort_package_json, sql_fluff, stylelint, swiftlint, vacuum | skip | no files of the type |

Every skipped builtin with no matching files would cost nothing at run time, but each still needs a tool pin
and an install in CI, which is the debt the user asked to avoid.

## 8. Code examples found

- `jdx/hk` `hk.pkl` at `eb9a149` (main, `OR/repos/hk/hk.pkl`): `Builtins.jactionlint`, `exclusive` prelint and
  postlint steps, check and fix hooks sharing one mapping.
- `jdx/hk` `pkl/builtins/jactionlint.pkl` at v2.6.0 (`b210714`) and at `eb9a149`: the released and the
  SARIF-and-fix definitions ([#1687](https://github.com/jdx/hk/pull/1687)).
- `jdx/hk` `pkl/builtins/gitleaks.pkl` at v2.6.0: `scan = "dir" | "staged"`, and the note that `gitleaks dir`
  takes one path.
- `jdx/hk` `src/step_job.rs:297-330`, `src/cli/install.rs:11`, `:337-353`, `src/cli/run/pre_push.rs:152-187` at
  v2.6.0: lock, install-event and pre-push range behaviour cited above.
- `jdx/jactionlint` `hk.pkl` at `8f0ce5d` (`OR/repos/jactionlint/hk.pkl`): `diagnostic_format = "sarif"`,
  `check_diff` through `hk util sarif-diff`, pre-commit with fix and stash, a heavier pre-push.
- `jdx/mise` [#13920](https://github.com/jdx/mise/pull/13920) (2026-10-03): a pre-commit hook with `fix = true`,
  `stash = "git"`; [#13960](https://github.com/jdx/mise/pull/13960): the `jactionlint` registry entry.
- [thedavidweng/OpenKara#488](https://github.com/thedavidweng/OpenKara/pull/488) (2026-10-09): a CI that replaced
  reviewdog's actionlint with jactionlint 1.8.2.

## 9. Routes table

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| preflight | Firecrawl | `fx firecrawl credits --json` | 0 | n/a | yes (SKIPPED, CREDITS_EXHAUSTED) |
| preflight | Serper, SerpApi | `fx http.py GET .../account` with the key from the environment | 0, 0 | n/a | yes |
| preflight | Context7 | `fx http.py GET https://context7.com/api/v2/usage` | 0 | n/a | yes (SKIPPED, CREDITS_EXHAUSTED) |
| preflight | GitHub | `fx gh api rate_limit`; `fx gh api repos/<r>` x6 | 0 | n/a | yes |
| preflight | Last30Days | ScrapeCreators credit balance | 0 | n/a | yes (DEGRADED) |
| 1 | Exa | `fx exa_run.sh <id> "<query>"` (POST /search, 10 results) x8 | 0, HTTP 200 | 10 each | yes |
| 1 | Context7 | not called | n/a | 0 | gap (quota) |
| 1 | Firecrawl | not called | n/a | 0 | gap (credits) |
| 1 | webclaw | `webclaw <url> -f markdown > OR/pages/<name>.md` x111 | 0 (110), 1 (1, HTTP 404) | 1 each | yes |
| 1 | Serper | `fx http.py POST https://google.serper.dev/search` x4 | 0, HTTP 200 | 2 to 10 | yes |
| 1 | SerpApi | not needed after Serper | n/a | 0 | no |
| 1 | Last30Days | `fx env SSL_CERT_FILE=/etc/ssl/cert.pem python3.12 last30days.py "<topic>" --plan plan.json --emit json --search reddit,hackernews,github --save-dir ""` | 0 | 32 | yes (DEGRADED) |
| 1 | GitHub releases | `fx gh api repos/jdx/<r>/releases --paginate` x2 | 0 | 152, 6 | yes |
| 2 | git clones | `git clone --filter=blob:none` jdx/hk, jdx/jactionlint | 0 | n/a | yes |
| 2 | gh search | `fx gh search issues|prs "<term>" --repo <r> --limit 15 --json ...` x11 | 0 | 1 to 15 | yes |
| 2 | gh view | `fx gh pr view` x6, `fx gh issue view --comments` x1 | 0 | 1 each | yes |
| 2 | GraphQL discussions | `fx gh api graphql` search x6, reads x4 | 0 | 0 to 23 | yes |
| 2 | saved searches | `fx gh api -X GET search/code -f q="<q> repo:<r>" -F per_page=5` x8; `search/issues` x3 | 0 | 0 to 660 | yes |
| 2 | tool maintenance | `fx gh api repos/<r>` and `/releases?per_page=3` x7 | 0 | 3 each | yes |
| local | hk and scanners | `hk builtins`; scratch-clone `hk check|run` with `HK_TIMING_JSON`; `gitleaks|betterleaks git --log-opts=...` | 0 or 1 | n/a | yes |

`fx` is `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`; helpers are in the session scratch (`research6/R18/bin`).

## 10. Proposed saved-search rows

Shape as in `dev/saved-searches.toml` (not edited); counts from this run.

```toml
# hk builtins and jactionlint (research R18, decision D150, 2026-10-14)
[[search]]
id = "hk-builtin-jactionlint"
query = "jactionlint path:pkl/builtins"
repo = "jdx/hk"                     # 1 hit today; control README 62
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "hk-builtin-catalog"
query = "\"Builtins.meta\" path:pkl/builtins"
repo = "jdx/hk"                     # 165 hits today: a growth watch for new builtins
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "jactionlint-hk-sarif-diff"
query = "\"sarif-diff\""
repo = "jdx/jactionlint"            # 5 hits; control README 48
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 11. Open gaps

- jactionlint, tombi and tombi-format were not run on MP (not installed; installs need admission). Their
  findings and timings are proxies (actionlint, zizmor, ghalint, pinact, taplo). First run after the pins land:
  `./dev/mise x -- hk check --all --step jactionlint --step tombi --step tombi-format`.
- Context7 (quota until 2026-11-01) and Firecrawl (credits -128) were skipped; webclaw and Serper covered the
  pages. `hk.jdx.dev/llms-full.txt` returned 404.
- Last30Days ran degraded (ScrapeCreators -7 credits): Reddit partial, Hacker News off-topic; GitHub results used.
- Whether the mise age gate under `dev/mise` holds back jactionlint 2.2.0 (published today) is UNVERIFIED.
- The superset guard range blocks manual pushes until the 10 old-history local branches are rebased or deleted
  (D143/D148); that cleanup, or the interim HEAD range, is a parent decision.
- Whether `--branches --not --remotes` should also exclude `evidence/` false positives (226 `generic-api-key`
  in current history) is a scanner-config question for R17 (allowlist or reviewed baseline, as A09 does).
- `hook.<event>.enabled` (event-wide) is documented for Git 2.55; UNVERIFIED on the host's 2.54.
- The launcher choice (local `./dev/mise x -- hk run` hooks versus fixing the global launcher) and the commit
  subject convention for integration merges are user decisions; `hooks:install` stays unrun (D2).
- The 12 undefined names in `dev/toolchains/p2996_math_probe.py`, the `dev/mise` SC2155 warning, 3 broken doc
  links, 2 typos and 59 Markdown findings must be fixed before those steps block.
