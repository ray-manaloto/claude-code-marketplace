# R22: automated dependency updates, a one-hour release age, and TS and C++ hk tooling (D157, D158)

Written by research agent R22 of the research6 team, session `ccm-20261014` (`ce9c0b3d`), 2026-10-14, for user
decisions D157 and D158 (`decisions.jsonl` rows DL-200 and DL-201). Read-only for MP except this file and the
untracked mirror. No tracked MP file, nothing in knowledge-base, dotfiles or TR was edited; no GitHub write; no tool
was installed on the host (scratch-only installs under an isolated `MISE_DATA_DIR`, section 7.8).

Citation keys. MP = the repository root (HEAD `ca53deb` when the scratch clone was taken). P =
`MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. OFF = `MP/offline/research/R22/` (untracked through
`.git/info/exclude:17`); `OFF/queries.jsonl` is the D137 log (175 rows) and `Qn` cites its row `seq = n`;
`OFF/manifest.json` lists 327 mirrored items with SHA-256 or commit. R18OFF and R21OFF are the R18 and R21 mirrors
under `MP/offline/research/`. Reports cited: R17 (`research6/R17-secret-scanner.md`), R18 (`R18-hk-builtins.md`,
section 7.6 is the proposed `hk.pkl`), R21 (`R21-dependency-freshness.md`, batches in section 2), A2
(`P/reviews/ccm-20261014/project-import/A2-typescript-mods-library.md`). TR specifics are only in the private note
`~/.local/state/claude-code-marketplace/private-notes/reviews/2026-10-14/R22-tr-dependency-skill.md` (not committed).
Anything without a citation is labelled UNVERIFIED.

## 1. Verdict

**Recommendation: one bot, self-hosted Renovate, run hourly by a GitHub Actions workflow with a GitHub App
token, configured by one `.github/renovate.json` that covers every MP ecosystem. PRs open only after a release is one
hour old, merge themselves on green required checks for patch, minor, digest and lock-maintenance updates, and wait
for review for majors, pre-1.0 minors and C++ inputs. The 19 frozen baseline files are held behind Dependency
Dashboard approval in one grouped PR that `check:acceptance-baseline` fails until the reviewed transition lands.
Dependabot is rejected; the mise-native route survives only as local mise tasks for the agent-on-failure path.**
Confidence: high for coverage, lock safety and config validity (validated and dry-run on a scratch clone); medium
for the zero-token claim, which depends on one frozen-file change and four user admissions (below).

Evidence that decides it:

1. Coverage, measured. Renovate 44.155.8 in `--platform=local --dry-run=lookup` mode on a scratch clone with the
   proposed config found 27 dependencies and proposed 20 updates in 7 branches: `pin-dependencies` (SHA pins for the
   two non-frozen workflows), `mise` (the `jdx/mise-action` `version:` input and `min_version` together), `uv`, `hk`
   (both version occurrences in the `hk.pkl` package URL), `microsoft-vcpkg-digest` (the `builtin-baseline`),
   `jdx-mise-action-5.x` (major, review), and `frozen-baseline-transition` for everything in `acceptance.yml`,
   `mise.toml` and the plugin `mise.toml` (Q167; `OFF/local/renovate-report.json`). The config passed
   `renovate-config-validator --strict` (Q165).
2. Lock safety, measured. Renovate updates `mise.dev.lock` by running `MISE_ENV=dev MISE_SAFE=1 mise lock <tool>`
   (`OFF/repos/renovatebot_renovate/lib/modules/manager/mise/artifacts.ts:196-224`, commit `fc4719be`). Run by hand on
   the scratch clone after a `uv` bump, that command rewrote only the `uv` entries of `mise.dev.lock` and kept exactly
   the three platforms `dev/bootstrap.py:23` requires; it also re-wrote the frozen `mise.lock` byte-identically, and
   Renovate commits only the lock file named for the package file (`lib/modules/manager/util.ts:175-209`), so that
   side effect cannot reach a PR (Q162). The scoped `./dev/mise lock uv@0.13.1 --platform ...` used by the proposed
   task changed `mise.dev.toml` and `mise.dev.lock` only, in 1.29 s, and `verify_tool_lock()` passed (Q163).
3. Dependabot cannot meet the brief: no mise ecosystem (dependabot/dependabot-core#14500 open since 2026-03-20,
   issue #12320 open since 2025-05-26; Q108, Q109), no `hk.pkl` or `min_version` support (no custom managers), a
   cooldown measured in days with a 3-day default (`OFF/pages/docs.github.com_..._dependabot-options-reference.md:269-320`;
   discussion #15582, 2026-07-14, Q148), uv listed as v0.11 and pnpm as v7 to v10 in its ecosystem table while MP pins
   uv 0.13 and A2 pins pnpm 12 (`OFF/pages/docs.github.com_..._supported-ecosystems-and-repositories.md:64,72`;
   dependabot-core#16434 and #16397, both open, Q142, Q143), and Dependabot runs cannot read Actions secrets, so
   `acceptance.yml:55-62` ("fail loud if the agent step skipped on a same-repo PR") fails every Dependabot PR.
4. Agent tokens. `acceptance.yml:3-5` runs on every `pull_request` with no path filter, and `ci/acceptance.sh:43-45`
   and `:153-154` start two `claude -p` sessions (one with `--max-turns 40`) using the `CLAUDE_CODE_OAUTH_TOKEN`
   secret, which exists (Q172). 27 of the last 100 MP workflow runs were acceptance runs, averaging 158 s (Q172). Every
   bot PR therefore spends Claude tokens today. Zero tokens needs a `paths:` filter on `acceptance.yml`, a frozen file,
   so it rides R21's batch-4 baseline transition; until then Renovate runs in dashboard-approval ("observe") mode,
   which opens no PR without a click.
5. Reference behaviour. The dotfiles repository, on the Mend-hosted Renovate app with `minimumReleaseAge: "1 hour"`
   (`dotfiles/renovate.json:9-14`), had 200 Renovate PRs between 2026-09-14 and 2026-10-13: 186 merged, 7 closed,
   7 still open, merge latency median 0.1 h and p90 0.5 h (Q141). The 7 stuck PRs are the failure classes this design
   pre-empts: a grouped "mise tools" PR, a grouped actions PR, a Python bump before python-build-standalone shipped it,
   two majors, a cold-image group and a 23-day-old lock maintenance PR.
6. The release-age gate is expressible in every ecosystem MP uses, and its location is measured: `[settings]
   minimum_release_age = "1h"` in `mise.dev.toml` changed `./dev/mise latest uv` from 0.13.0 to 0.13.1, and an
   inherited `MISE_MINIMUM_RELEASE_AGE` overrides it (Q164); uv accepts `exclude-newer = "1 hour"` and records
   `exclude-newer-span = "PT1H"` in `uv.lock` with `uv lock --check` still passing (Q169); pnpm takes
   `minimumReleaseAge: 60` (`OFF/pages/pnpm.io_settings_dependency-resolution.md:389-412`).
7. Preconditions found, each a user decision: the default branch `main` is `6b5b092` (2026-08-29), 13 commits behind
   `codex/marketplace-native-onboarding`; `allow_auto_merge` is false; `main` has no branch protection (Q172).
   Scheduled workflows and any bot's repository config run from the default branch, so automation starts only after
   the onboarding branch reaches `main` (or the default branch changes), and automerge needs the setting plus a
   ruleset with required checks.

D112/D113 classification: every proposed change is configuration of an existing tool (Renovate, mise, uv, pnpm,
pinact, hk, cmakefmt, clang-format), a GitHub workflow, or a data row in existing Python (`dev/bootstrap.py:22`
`TOOL_BACKENDS`). One shell fix to an existing script (`dev/mise:23`, one more name in its `unset`). No new Python or
TypeScript logic. A ranked outdated report or a transactional multi-file rollback would be new logic: a C++
`rsm-core` ticket, never Python.

Lane split (section 7.16): R17 scanner lane, then `deps-age` (4 files), then R18's hk lane, then `deps-tasks`
(4 files), then `deps-bot` in observe mode (4 files), then R21 batch 4 with the `acceptance.yml` path filter, then
one line turns observe mode off. C++ formatter steps go with the C++ check ticket; TypeScript steps go with A2's mods
lanes.

## 2. Queries sent to each tool, plugin or service (stage 1), exact text

Preflight (D142) first: Firecrawl `firecrawl credits --json` returned `remainingCredits: -128` of 1,000 (Q1,
SKIPPED, CREDITS_EXHAUSTED); Serper `GET /account` balance 1,297 (Q2); SerpApi `GET /account.json`
`plan_searches_left` 243 (Q3); `gh api rate_limit` core 4,805, search 30, code_search 10, graphql 4,980 (Q4);
`ctx7 whoami` "Logged in" (Q5); Exa has no balance endpoint (Q6). All seven keys were present, checked one named
variable at a time.

| Q | Provider | Exact query |
|---|---|---|
| 7 | exa | `Renovate mise manager mise.lock lockfile maintenance support` |
| 8 | exa | `Dependabot vcpkg support version updates vcpkg.json builtin-baseline` |
| 9 | exa | `Dependabot support for mise.toml mise tools ecosystem` |
| 10 | exa | `Renovate self-hosted GitHub Action postUpgradeTasks allowedCommands GitHub App token` |
| 11 | exa | `mise minimum_release_age setting jdx/mise-action v5 minimum_release_age input` |
| 12 | exa | `Dependabot uv.lock support cooldown minimum age days` |
| 13 | exa | `Renovate vcpkg manager support builtin-baseline` |
| 14 | exa | `Dependabot GitHub Actions SHA pinned update version comment` |
| 15 | exa | `native CMake formatter alternative to cmake-format gersemi Rust` |
| 16 | exa | `clang-format clang-tidy standalone static binaries install mise aqua` |
| 17 | exa | `uv exclude-newer relative duration minimum release age` |
| 18 | exa | `Renovate mise manager mise.dev.toml file pattern custom config files` |
| 19 to 21 | context7 | `ctx7 library renovate "mise manager lock file support" --json`; `ctx7 library dependabot "vcpkg uv github-actions cooldown" --json`; `ctx7 library mise "minimum_release_age lock platforms" --json` |
| 22 | firecrawl | planned `firecrawl search "Renovate mise manager lock file"`; not sent (preflight) |
| 23 to 63, 69 to 80, 159 to 161 | webclaw | 56 pages, URLs in `OFF/manifest.json`: Renovate docs (mise, managers, configuration-options, self-hosted-configuration, github-actions, pep621, npm, regex, automerge, Mend hosted apps, minimum-release-age, pre-commit, upgrade best practices, noise reduction), `renovatebot/github-action`, GitHub docs (Dependabot ecosystems, options reference, automating Dependabot, `GITHUB_TOKEN`, workflow dependency lockfiles), GitHub changelogs 2025-07-01, 2025-08-12, 2026-06-11, 2026-10-14, Microsoft vcpkg Dependabot page, uv docs (Dependabot, Renovate, settings, resolution), mise docs (lock, upgrade, outdated, mise-lock, settings, continuous integration, security), `jdx/mise-action`, hk builtins, cmakefmt site and repository, LLVM CMake formatter RFC, gersemi, clang-tools-static-binaries, Biome, Oxlint linter docs and type-aware stable post, pnpm settings and dependency resolution, cooldowns.dev, `jdx/renovate-config`, `peter-evans/create-pull-request`, `actions/create-github-app-token`, renovate discussion #40504, dependabot-core#12320, aqua-registry#56167 |
| 64 | git-clone | `git clone --filter=blob:none --no-checkout --depth 1 https://github.com/renovatebot/renovate.git` plus sparse `lib/modules/manager/{mise,pep621,github-actions,custom,util.ts}`, `docs/usage` |
| 65 | serper | `renovate mise lock file safe mode MISE_SAFE allowedUnsafeExecutions mise.lock` |
| 66 | serper | `dependabot "mise" ecosystem support mise.toml 2026` |
| 67 | serper | `cmakefmt rust cmake formatter gersemi comparison 2026` |
| 68 | serpapi | `oxlint type-aware tsgolint stable release 2026 biome formatter TypeScript 7` |
| 81 to 99 | gh-api-release | `gh api repos/<o>/<r>/releases?per_page=10` for 19 repositories (gersemi, create-github-app-token, betterleaks, biome, cmakefmt, clang-tools-static-binaries, hk, jactionlint, mise, llvm-project, TypeScript, typescript-go, oxc, tsgolint, create-pull-request, pnpm, renovate github-action, renovate, pinact) |
| 100 | last30days | topic `Renovate vs Dependabot automated dependency updates and cooldowns`, explicit `--plan` with three subqueries (`Renovate vs Dependabot`; `dependency cooldown minimum release age`; `renovate mise lock`; sources reddit, hackernews, github), `--emit=json --quick --days 30`, `SSL_CERT_FILE=/etc/ssl/cert.pem`; plan copy `OFF/pages/last30days-plan.json` |
| 173 | gh-api-contents | `gh api repos/jdx/renovate-config/contents/{default.json,.github/workflows/mise-lock.yml}` (main `dbd76304`) |

## 3. Results from each (hits, top results, what was used)

| Q | Provider | rc / HTTP | Hits | Top results | Used |
|---|---|---|---|---|---|
| 7 | exa | 0 / 200 | 8 | Renovate mise manager docs; renovatebot/renovate#42591, #40568, PR #42099, PR #44615 | yes: seeded Q101 to Q104, Q151, Q174 |
| 8 | exa | 0 / 200 | 8 | Microsoft vcpkg Dependabot page; GitHub changelog 2025-08-12 (vcpkg); dependabot-core PR #15432 | yes: Q38, Q39, Q110 |
| 9 | exa | 0 / 200 | 8 | dependabot-core PR #14500 "Add initial support for mise"; issue #12320; Renovate mise docs | yes: Q108, Q109, Q153 |
| 10 | exa | 0 / 200 | 8 | Renovate self-hosted configuration; `renovatebot/github-action`; post-upgrade command source | yes: Q26, Q27 |
| 11 | exa | 0 / 200 | 8 | `jdx/mise-action` action.yml and releases; mise settings; jdx/mise#10279, #10366 | yes: Q116, Q117, Q145 |
| 12 | exa | 0 / 200 | 8 | uv "Using uv with Dependabot"; Dependabot minimum package age changelog; dependabot-core#13816, #14544, discussion #15582 | yes: Q111, Q112, Q146, Q148 |
| 13 | exa | 0 / 200 | 8 | renovatebot/renovate#7135 "Vcpkg support"; PR #43497 vcpkg versioning | yes: Q105, Q106, Q155 |
| 14 | exa | 0 / 200 | 8 | dependabot-core PR #5951, #16029 "Prefer SHA pins", #14516 | yes: Q113, Q114, Q158 |
| 15 | exa | 0 / 200 | 8 | cmakefmt repository, site and comparison; gersemi | yes: Q52, Q53, Q70, Q120, Q133 |
| 16 | exa | 0 / 200 | 8 | cpp-linter/clang-tools-static-binaries; clang-tools pip; mise aqua backend | yes: Q54, Q86, Q121, Q171 |
| 17 | exa | 0 / 200 | 8 | uv settings; astral-sh/uv PR #16814 relative `exclude-newer` | yes: Q43, Q115, Q169 |
| 18 | exa | 0 / 200 | 8 | Renovate mise docs; renovatebot/renovate#40094 (file patterns) | yes: Q107 |
| 19 to 21 | context7 | 1 | 0 | "Monthly quota reached. You'll receive 20 bonus API requests tomorrow" | no (ERROR, CREDITS_EXHAUSTED) |
| 22 | firecrawl | not sent | 0 | none | no (SKIPPED) |
| 23 to 63, 69 to 80, 159 to 161 | webclaw | 0 each | 56 usable pages | mirrored under `OFF/pages/` | yes (cited throughout) |
| 64 | git-clone | 0 | 1 | renovatebot/renovate `fc4719be` (2026-10-14) | yes |
| 65 | serper | 0 / 200 | 10 | Renovate mise docs; renovate discussion #40504 "mise lock file support"; mise lockfile docs; #40568 | yes: seeded Q144 |
| 66 | serper | 0 / 200 | 10 | dependabot-core#12320; jdx/mise; cooldowns.dev | yes: Q73, Q75 |
| 67 | serper | 0 / 200 | 10 | cmakefmt repository (2026-10-06); LLVM RFC "Having an auto-formatter for CMake" (2026-04-10); r/rust cmakefmt; gersemi | yes: Q71 |
| 68 | serpapi | 0 / 200 | 9 | oxc blog "Type-Aware Linting Stable" (2026-07-22); InfoQ "tsgolint Reaches Stable v7" (2026-09-11); biome discussion #7009 | yes: Q72, Q131 |
| 81 to 99 | gh-api-release | 0 each | 10 each | versions in section 7.8 | yes |
| 100 | last30days | 0 | 8 | the "vs" topic switched it to comparison mode, which ignored the plan; "Renovate" matched home-renovation Reddit posts; GitHub returned generic CI PRs; `grounding: error`, Hacker News no results | no (DEGRADED) |
| 173 | gh-api-contents | 0 | 2 | `jdx/renovate-config` `default.json` and `mise-lock.yml` | yes |

## 4. GitHub issues, PRs and discussions searched (stage 2), each with its seed

Repository feature checks ran first (Q118 to Q128, logged after the views but run before them): every repository
has issues on; discussions are off for astral-sh/uv, aquaproj/aqua-registry, ray-manaloto/dotfiles and
cpp-linter/clang-tools-static-binaries, so no discussion query went to those. None is archived.

| Q | Route | Query | Result | Seeded by |
|---|---|---|---|---|
| 101 to 104 | issue and PR view | renovatebot/renovate#42591 (merged 2026-05-19, lock file support, adds `MISE_ENV` and `--local`), #40568 (closed), PR #42099 (closed, superseded), PR #44615 (merged 2026-09-14, selector lockfile updates) | Renovate locks `mise.<env>.lock` with `MISE_ENV=<env>` | 7 |
| 105, 106 | issue and PR view | renovatebot/renovate#7135 "Vcpkg support" (open since 2020-08-30); PR #43497 vcpkg versioning (open) | no native vcpkg manager; a custom regex manager is needed | 13 |
| 107 | issue view | renovatebot/renovate#40094 (merged 2026-01-23, file patterns follow mise's config search) | `mise.dev.toml` matches `**/{,.}mise{,.*}.toml` | 18 |
| 108, 109 | PR and issue view | dependabot/dependabot-core PR #14500 "Add initial support for mise" (open since 2026-03-20); issue #12320 (open since 2025-05-26) | no Dependabot mise support | 9 |
| 110 | PR view | dependabot-core PR #15432 (merged 2026-06-29, adds a baseline to vcpkg projects missing one) | Dependabot vcpkg is baseline-only | 8 |
| 111, 112 | issue view | dependabot-core#13816 (open, map uv `exclude-newer` to cooldown), #14544 (closed 2026-04-08, uv and pip cooldown differ) | cooldown semantics still moving | 12 |
| 113, 114 | PR view | dependabot-core PR #16029 (merged 2026-08-27, opt-in `github_actions_pin_to_sha`), PR #14516 (closed) | Dependabot can pin actions to SHAs, opt-in | 14 |
| 115 | PR view | astral-sh/uv PR #16814 (merged 2025-12-09, relative `exclude-newer`) | `exclude-newer = "1 hour"` is supported | 17 |
| 116, 117 | PR view | jdx/mise PR #10279 (merged 2026-06-09, default release age), #10366 (24h default documented) | the 24h default R21 found | 11 |
| 129, 130 | issue search | renovatebot/renovate `mise lock MISE_ENV` (0, EMPTY_UNVERIFIED); `mise safe mode lock` (1, unrelated #37772) | no open bug against the env lock path | 65 |
| 131 | issue search | aquaproj/aqua-registry `oxlint` (3: #56167 closed 2026-06-29, #26232, #18781) | explains the broken `aqua:oxc-project/oxc/oxlint` route measured in Q171 | 68 |
| 132, 140 | issue search | jdx/hk `biome effect` (0), `tsc builtin` (0) | no upstream report that the biome and tsc builtins declare `effect = "write"` (EMPTY_UNVERIFIED) | 51 |
| 133 | issue search | cmakefmt/cmakefmt `is:issue` (8, all closed, newest #189 2026-09-29) | young but responsive project | 15 |
| 134, 141 | PR search | ray-manaloto/dotfiles `author:app/renovate` (20; then 200 with `--limit 200`) | 186 merged, 7 closed, 7 open in 30 days | local reference review (no stage-1 row) |
| 135 | issue search | github/gh-actions-lock `renovate` (2: #132 cooldown feature request, #133) | Actions lockfiles have no release-age gate yet | 62 |
| 136 | issue search | jdx/mise `lockfile_platforms safe` (1, #4276 old) | nothing against the safe-mode settings rule | 74 |
| 137, 138 | issue search | dependabot-core `uv lockfile revision` (3, none on point); `pnpm 11` (20, including #16434 pnpm 12 security updates fail, #16397 docs omit pnpm 11 and 12) | Dependabot pnpm 12 support is partial | 12 |
| 139 | issue search | renovatebot/renovate `github-runner ubuntu-26.04` (0, EMPTY_UNVERIFIED) | none | 28 |
| 142, 143 | issue view | dependabot-core#16397, #16434 | as above | 35 |
| 144 to 148 | GraphQL discussions | renovatebot/renovate `mise lock` (1, #45740 Pkl package manager); jdx/mise `renovate` (29: #14153 mise-action caching with lockfile verification, #10563 `mise lock` keeps a stale version for `npm:` tools without npm); dependabot-core `cooldown default` (4: #15582, #15368, #15276); discussion #15582 read in full; oxc `type-aware tsgolint stable` (1, unrelated) | 3-day default cooldown confirmed; `npm:` backend lock caveat | 65, 11, 12, 12, 68 |
| 174, 175 | commit history | renovatebot/renovate `lib/modules/manager/mise/artifacts.ts` (9 commits: lock support 2026-05-19, allowlist required 2026-06-03 #43606, safe mode without allowlist 2026-07-27 #44749); jdx/renovate-config `mise-lock.yml` (8 commits from 2026-09-15) | dates the hosted-app lock gap | 7, 60 |

## 5. Githubkit saved searches run (reproduced read-only with controls) and proposed new rows

`./dev/mise run research:collect` writes into a tracked path another lane owns, so the equivalent REST calls ran
read-only into `OFF/gh/code-search/` (`gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=1`).

| Q | Row id | Query | Hits | Control (README) | Verdict |
|---|---|---|---|---|---|
| 149, 150 | `codex-schema` (existing, `dev/saved-searches.toml:3-14`) | `schema repo:openai/codex` | 878 | 167 | route healthy |
| 151, 152 | proposed `renovate-mise-safe-lock` | `MISE_SAFE repo:renovatebot/renovate` | 2 (`artifacts.ts`, `artifacts.spec.ts`) | 63 | keep: watches the safe-mode lock path this design depends on |
| 153, 154 | proposed `dependabot-mise-ecosystem` | `filename:dependabot-mise.gemspec repo:dependabot/dependabot-core` | 0 (EMPTY_VERIFIED) | 764 | keep: a hit means Dependabot shipped mise and the verdict should be revisited |
| 155 | proposed `renovate-vcpkg-manager` | `path:lib/modules/manager/vcpkg repo:renovatebot/renovate` | 0 (EMPTY_VERIFIED, same control as Q152) | 63 | keep: a hit retires the custom vcpkg manager |
| 156, 157 | proposed `hk-cmakefmt-builtin` | `cmakefmt repo:jdx/hk` | 0 (EMPTY_VERIFIED) | 62 | keep: a hit lets the custom cmakefmt step become a builtin |
| 158 | proposed `dependabot-actions-sha-pin` | `github_actions_pin_to_sha repo:dependabot/dependabot-core` | 2 | 764 (Q154) | drop after review: informational only |

Proposed rows are in section 10.

## 6. Stage-2 searches run against the stage-1 results (seed-to-search map)

| Stage-1 seed (Q) | What it surfaced | Stage-2 rows (Q) |
|---|---|---|
| 7 exa, Renovate mise lock | #42591, #40568, PR #42099, PR #44615 | 101 to 104, 151, 152, 174 |
| 8 exa, Dependabot vcpkg | PR #15432 | 110 |
| 9 exa, Dependabot mise | PR #14500, issue #12320 | 108, 109, 153, 154 |
| 11 exa, mise release age | mise#10279, #10366 | 116, 117, 145 |
| 12 exa, Dependabot uv cooldown | #13816, #14544, discussion #15582 | 111, 112, 137, 138, 146, 148 |
| 13 exa, Renovate vcpkg | #7135, PR #43497 | 105, 106, 155 |
| 14 exa, Dependabot SHA pins | PR #16029, #14516 | 113, 114, 158 |
| 15 exa and 67 serper, CMake formatters | cmakefmt | 133, 156, 157 |
| 17 exa, uv relative exclude-newer | PR #16814 | 115 |
| 18 exa, Renovate file patterns | #40094 | 107 |
| 28 webclaw, github-actions manager | `github-runner` dep type | 139 |
| 35 webclaw, Dependabot ecosystem table | pnpm and uv versions | 142, 143 |
| 51 webclaw, hk builtins | biome, tsc builtins | 132, 140 |
| 60 webclaw, jdx/renovate-config | `mise-lock.yml` reusable workflow | 173, 175 |
| 62 webclaw, Actions lockfiles changelog | `gh-actions-lock` | 135 |
| 65 serper, Renovate safe mode | discussion #40504 | 129, 130, 144 |
| 68 serpapi, oxlint | oxlint, tsgolint | 131, 147 |
| 74 webclaw, mise security | safe mode ignores project `[settings]` | 136 |
| local reference review (dotfiles `renovate.json`) | hosted Renovate on dotfiles | 134, 141 |

## 7. Findings with citations

### 7.1 Reference setups (read-only)

- dotfiles (`/Users/rmanaloto/dev/github/ray-manaloto/dotfiles`, HEAD `7744a9c6`, 2026-10-13). Mend-hosted Renovate
  extending `github>jdx/renovate-config`, `minimumReleaseAge: "1 hour"` with `timestamp-optional`, lock file
  maintenance on, automerge for minor, patch and digest with `platformAutomerge`, `rebaseWhen: conflicted`, eight
  custom regex managers (hk Pkl URL, `.chezmoiversion`, clang-p2996 `git-refs` digest, a dated GCC `.deb`, Ubuntu
  digest, the mise installer version, dive, apt pins through the `deb` datasource) and one custom datasource
  (`dotfiles/renovate.json:1-271`). Its rule descriptions are a record of failures worth inheriting: the hk package
  URL and the hk pin must move in one PR (#1090; `renovate.json:28`); the hk URL carries the version twice, so both
  occurrences need a match string (#248; `customManagers[0]`); a Python bump before python-build-standalone ships the
  build blocks a grouped PR, so Python gets its own PR (#1449; `packageRules[8]`); Renovate writes a `v` prefix back
  for tools mise lists without one (#455, #906; `packageRules[7]`); `group:all` held 28 bumps in one PR for 11 days
  (#947; `packageRules[0]`). Dependabot is kept for the `pip` ecosystem only, daily cron with `cooldown.default-days:
  7`, and its comment records that Dependabot rejects sub-daily cron (`.github/dependabot.yml:16-43`). A separate
  `refresh.yml` (674 lines) mints a GitHub App token, regenerates lock files Renovate cannot (image locks), and runs
  standing "tool currency" issues (`.github/workflows/refresh.yml:1-46, 322-336`); its header records that the
  hosted app "can never run `mise lock`" for non-standard lock names. `.pinact.yaml` pins workflow actions.
  Its AGENTS.md states the bare re-lock is destructive (`AGENTS.md:30`, #370), and receipt
  `docs/receipts/440.md:110-135` corrects the noun: on macOS the bare `mise lock` dropped `[conda-packages.*]`
  entries, not `platforms` tables (measured on mise 2026.7.18).
- knowledge-base (`.../knowledge-base`, main `f086f731`, 2026-10-05). No Renovate or Dependabot on main (the
  `renovate.json` history in its object store belongs to other repositories' refs). Updates run through a Python
  currency engine (`mise.toml` tasks `kb-currency-check`, `kb-currency`, `kb-tool-sync`) whose `python/src/kb_setup/tool_sync.py` (`:127-191`, `:268-290`) locks one
  tool with a scoped `mise lock <key>` inside a snapshot-and-restore transaction, and a read-only six-hourly docs
  mirror check (`.github/workflows/docs-refresh.yml`). Useful as evidence that scoped locks are the safe unit; not a
  pattern MP may copy as Python (D112).
- TR (codename only). No Renovate, Dependabot or `.github/` directory. A dependency-upgrade skill routes to a
  `deps:upgrade <name>` mise task and a `deps:upgrade-all` wrapper over a Python package; reviewed in the private
  note. Generic findings: it fabricates reports when nothing is outdated, claims test passes on no-op runs, ignores
  every subprocess exit code, restores config files but not lock files on rollback, refreshes mise pins with
  `mise install` instead of `mise lock`, and runs a bare `mise up` in its general update task (the #370 class). MP
  takes the shape only: one native command per dependency per ecosystem, a separate verify task, and `git restore`
  as the rollback (section 7.14).

### 7.2 Route comparison

| Criterion | Renovate, self-hosted Action (chosen) | Renovate, Mend-hosted app | Dependabot | mise-native workflow |
|---|---|---|---|---|
| mise tools (`mise.dev.toml`) | yes, native manager (`OFF/pages/docs.renovatebot.com_modules_manager_mise.md:37-42`) | yes | no (#14500 open, Q108) | yes (`mise lock <tool>@<v>`, Q163) |
| `mise.dev.lock`, 3 platforms | yes: `MISE_ENV=dev MISE_SAFE=1 mise lock <tool>`, platforms kept (Q162) | contested: jdx says the hosted app leaves `mise.lock` stale (`jdx/renovate-config/.github/workflows/mise-lock.yml:3-9`, 2026-09-15); dotfiles says host locks are regenerated (`refresh.yml:322-336`) | n/a | yes, explicit `--platform` |
| Python `uv.lock` | yes, `uv lock --upgrade-package` with the uv from `tool.uv.required-version` (`.../pep621/processors/uv.ts:211-245`) | yes | yes, but its uv is listed as v0.11 (Q35); an older uv rewrites MP's lock (uv 0.12.7 reported changes, 0.13.x did not, Q168) | yes, `uv lock --upgrade` |
| TypeScript (pnpm 12, A2) | yes, `pnpm-workspace.yaml` supported (`.../manager_npm.md:38`) | yes | partial (table says v7 to v10; #16434, #16397) | yes, `pnpm update` |
| C++ vcpkg baseline | custom regex plus `git-refs` (no native manager, #7135) | same | yes, baseline only (2025-08-12 changelog, Q38) | `vcpkg x-update-baseline` (needs vcpkg) |
| Actions pins and runner labels | yes: digests with version comments (`helpers:pinGitHubActionDigests`), `runs-on` versions, `jdx/mise-action` `version` and `sha256` inputs (`.../manager_github-actions.md:60, 105-115, 416`) | yes | yes; SHA pinning opt-in (#16029) | `pinact run --update` |
| `hk.pkl`, `min_version` | custom regex managers (measured, Q167) | same | no | manual |
| Grouping | `groupName`, file- or name-based | same | `groups` | one PR per run |
| Automerge on required checks | `platformAutomerge` (needs "Allow auto-merge" and a ruleset; `.../configuration-options.md:9476-9500`) | same | a workflow with `gh pr merge --auto` | `gh pr merge --auto` |
| Release age | `minimumReleaseAge: "1 hour"`, timestamp required by default since Renovate 42 (`.../minimum-release-age.md:135`) | same | days only, default 3 (Q36, Q148) | per tool: mise `1h`, uv `1 hour`, pnpm `60` |
| Frozen-file routing | `matchFileNames` plus `dependencyDashboardApproval` (Q167) | same | `ignore` only | path lists |
| Tokens and permissions | GitHub App (contents, PRs, issues, workflows write; statuses write); PRs trigger CI | Mend app install, no secret | built-in; cannot read Actions secrets | GitHub App to trigger CI (`GITHUB_TOKEN` PRs need manual approval: 2026-06-11 changelog, `OFF/pages/github.blog_changelog_2026-06-11-...md`) |
| Agent tokens | zero per update after the `acceptance.yml` filter | same | zero, but acceptance fails every PR | zero |
| Logic added | config only | config only | config only | workflow shell (branching per ecosystem): new logic |

Why self-hosted over hosted: the user asked for GitHub Actions; MP controls the Renovate version and its mise
constraint (safe mode needs mise 2026.7.12 or later, `artifacts.ts:46`); no third-party app gets write access; and
the hosted app's lock behaviour is contested by jdx's own workflow. The hosted app stays a fallback with the same
`renovate.json`.

### 7.3 Lock files

- `mise.dev.lock` is the lock Renovate derives for `mise.dev.toml` (`lib/modules/manager/mise/lockfile.ts:10-40`).
- Measured on the scratch clone (Q162): with `uv` bumped in `mise.dev.toml`, Renovate's command wrote 3 platform
  entries into `mise.dev.lock` (`macos-arm64`, `linux-x64`, `linux-arm64`) and also processed `mise.lock` (7
  platforms, format v1) without changing a byte. Renovate returns only `fileAddition(lockFileName, ...)`
  (`util.ts:208`), so a frozen-file side effect is never committed.
- `mise lock` without `--platform` uses `lockfile_platforms` plus the current platform when set, else the platforms
  already recorded (`OFF/pages/mise.jdx.dev_cli_lock.html.md`, flag `--platform`; settings page lines 2269-2290).
  Setting `lockfile_platforms` in `mise.dev.toml` makes every plain lock keep MP's three, but safe mode ignores
  project `[settings]` (`settings.html.md:73`), so Renovate relies on "platforms already in the lockfile", which held.
- Only scoped locks are safe: dotfiles #370 (`AGENTS.md:30`; receipt 440) and jdx's reusable workflow, which runs
  bare `mise lock` per lock file (`OFF/api/contents/jdx_renovate-config_mise-lock.yml:111-190`) and would touch MP's
  frozen `mise.lock`. MP should not adopt it.
- `dev/bootstrap.py:198-206` (`deps:lock`) already runs `mise lock --platform macos-arm64,linux-arm64,linux-x64`
  scoped to `mise.dev.toml` and then `uv lock`; it stays the full-relock path.

### 7.4 One-hour release age: where to set it

| Consumer | Where | Value | Evidence |
|---|---|---|---|
| `./dev/mise` (all dev tools) | `mise.dev.toml` `[settings]` | `minimum_release_age = "1h"` | measured: `latest uv` 0.13.0 by default, 0.13.1 with the line (Q164) |
| `./dev/mise` env override | `dev/mise:23` | add `MISE_MINIMUM_RELEASE_AGE` to the `unset` list | measured: an inherited value (48h) beat the file (Q164); settings precedence puts env above project files (`settings.html.md:62-72`) |
| `jdx/mise-action` v5 | workflow `with:` | leave unset while `version:` is pinned | the input "controls the mise binary; it does not set the release-age policy for tools installed by mise" and is ignored when `version` is given (R21OFF `repos/jdx_mise-action/README.md:62-82`, `src/index.ts:455`, commit `cd026961`); tools in CI come from `./dev/mise` and the lock |
| Bot PR creation | `.github/renovate.json` | `"minimumReleaseAge": "1 hour"` | Renovate docs (Q25, Q34) |
| Python | `pyproject.toml` `[tool.uv]` | `exclude-newer = "1 hour"` | measured: `uv.lock` gains `exclude-newer-span = "PT1H"`, `--check` passes (Q169) |
| TypeScript (A2) | `mods/pnpm-workspace.yaml` | `minimumReleaseAge: 60` | pnpm docs (Q63): minutes, default 1440 since v11 |

Exact pins and lock entries are never filtered by mise's age (`settings.html.md:2319`), so the gate acts on bot
proposals and on `latest` or `--bump` resolutions, which is where it should act.

### 7.5 Frozen baseline files

The 19 files in `evidence/onboarding/baseline-files.json` include three that carry dependencies: `mise.toml`,
`mise.lock`, `plugins/aggregated-research/mise.toml`, and `.github/workflows/acceptance.yml`. The proposed rule
matches all 19 by name, so Renovate opens nothing for them until someone ticks the box on the Dependency Dashboard,
then opens one grouped PR (`renovate/frozen-baseline-transition`, Q167) that never automerges. That PR fails
`check:acceptance-baseline` (run by `research-fast.yml`) by design until a lane adds the reviewed transition record
(CT-08, R21 batch 4) and the admitted acceptance run passes. The same rule catches R21's batch-4 security bumps
(gh 2.102.0, ty 0.0.87) as dashboard items, so they are visible without being merged.

### 7.6 Tokens, permissions and repository settings

- `GITHUB_TOKEN`-created PRs now run workflows only after a user approves them (GitHub changelog 2026-06-11;
  `OFF/pages/docs.github.com_en_actions_concepts_security_github_token.md:42-49`), and `renovatebot/github-action`
  says the same (`OFF/pages/github.com_renovatebot_github-action.md:212-221`). A GitHub App installation token avoids
  the approval click; updating `.github/workflows/*` needs the workflows permission (`:631-634`).
- App permissions: Contents RW, Pull requests RW, Issues RW (Dependency Dashboard), Workflows RW, Commit statuses RW
  (`renovate/stability-days`), Metadata R. Secrets: `RENOVATE_APP_PRIVATE_KEY`; variable `RENOVATE_APP_ID`. Creating
  the App and the secret is a user action.
- Repository state today (Q172): `allow_auto_merge` false, `main` unprotected, default branch `main` 13 commits
  behind the onboarding branch. Renovate warns that `platformAutomerge` without required checks can merge before
  tests run (`configuration-options.md:9476-9500`). Needed: "Allow auto-merge" on, and a ruleset on the base branch
  requiring `research-fast`, `offline-checks` and R18's `hk check` job (not `acceptance`).
- Bot merges bypass the A09 outbound scan and every local hook (R18 section 7.2). R17's scanner therefore needs a CI
  step over the PR's commit range (`betterleaks git --log-opts="<base>..HEAD"`) as a required check; that belongs to
  the R17 or R18 lane, listed here as a dependency.

### 7.7 Agent-token cost

- Per bot PR today: one acceptance run (two `claude -p` sessions, `ci/acceptance.sh:43-45, 153-154`) plus
  `research-fast` (61 s average) and `development checks` (56 s average) (Q172). After the `acceptance.yml` path
  filter: zero agent tokens per PR that does not touch acceptance inputs.
- Per update failure: an agent reads one labelled PR. Using the dotfiles rate (7 of 200 PRs stuck in 30 days, 3.5%,
  Q141) as an upper bound, MP with far fewer dependencies should see a handful of agent touches a month (UNVERIFIED
  estimate).
- Renovate itself: 5.8 s warm and 20.8 s cold for the lookup on MP (Q166, Q167); the Action adds an image pull
  (UNVERIFIED, about a minute).

### 7.8 TypeScript and C++ tools: versions, routes, measured cost

Measured in the scratch clone, Apple Silicon, three runs each, wall time from `/usr/bin/time -p`
(`OFF/local/timing/`). Tools not on the host were installed into an isolated scratch `MISE_DATA_DIR` with no global
or project config (Q171). TypeScript sample: 40 `.ts` files (19,537 lines) and a 3-file subset copied from the
dotfiles mods, a worst case for A2's planned size.

| Tool (version, date) | Route that worked | Files | Wall time | Findings |
|---|---|---|---|---|
| Biome 2.5.15 (2026-09-30), formatter only (A2) | host `aqua:biomejs/biome`; A2 uses `@biomejs/biome` | 40 / 3 | 0.62 to 0.65 s / 0.06 s | 40 files unformatted (no `biome.json`) |
| oxlint 1.88.0 (2026-10-13), npm launcher | `npm:oxlint@1.88.0` | 40 / 3 | 0.21 to 0.26 s / 0.21 to 0.22 s | 19 warning lines (unused imports) |
| oxlint 1.88.0 native binary | `github:oxc-project/oxc[tag_regex=^oxlint_v,bin=oxlint]` | 40 / 3 | 0.01 to 0.02 s / under 0.01 s warm | same |
| oxlint via the mise registry default | `aqua:oxc-project/oxc/oxlint@1.88.0` | n/a | n/a | fails: "This version is unavailable", aqua expects an `apps_v` prefix (Q171; aqua-registry#56167) |
| clang-format 23.1.3 (Homebrew LLVM) | host | 8 C++ files | 0.04 to 0.05 s | 166 lines of violations, no `.clang-format`; rewrites `typename [: ... :]` to `typename[: ... :]` |
| clang-format 21.1.0 static (2026.09.01-5fb8802d) | `github:cpp-linter/clang-tools-static-binaries[asset_pattern=clang-format-21_macos-arm64,bin=clang-format]` | 8 | 0.03 to 0.04 s | same violations and the same splice spacing rewrite |
| clang-tidy 23.1.3 (Homebrew) | host | 1 | 0.06 to 0.09 s | `src/core.cpp:3:10: 'meta' file not found`: the core needs the p2996 toolchain's clang-tidy, which `dev/toolchains/p2996_build.py:319` builds and `p2996_analysis.py` qualifies |
| cmakefmt 2.2.0 (2026-10-13), Rust | `github:cmakefmt/cmakefmt@2.2.0` | 11 CMake files | under 0.01 s | 7 of 11 would be reformatted (defaults) |

Decisions for D158 (prefer Rust, C++, C or Zig):
- TypeScript: A2 already chose oxlint 1.88 with `oxlint-tsgolint` 7.0.2004 type-aware (S4 caught the unawaited-promise
  class), Biome 2.5.15 as formatter only, TypeScript 7.0.2 (`tsgo`, Go-native) for type checks, pnpm 12 and Vitest
  5.0.4 (A2 sections 2.2, 2.6). Latest today: pnpm 12.13.0 (2026-10-13), oxfmt 0.73.0 (pre-1.0, A2 keeps Biome),
  TypeScript 7.0.2 (2026-08-20) (Q91 to Q96). No ESLint and no Prettier. The tools come from `mods/package.json`
  through pnpm, so Renovate's npm manager updates them; mise carries node and pnpm only.
- hk builtins at v2.6.0 need overrides: `Builtins.biome` and `Builtins.tsc` declare `check` with `effect = "write"`
  (R18OFF `repos/hk/pkl/builtins/biome.pkl`, `tsc.pkl` at `b2107143`), which takes write locks and serialises the
  hook (R18 section 7.3). `Builtins.ox_lint` is read-only. Section 7.13 overrides the effects.
- C++: clang-format from the project's LLVM major (21, the p2996 fork) rather than Homebrew 23; a fixture must show
  the splice spacing is acceptable before the step blocks. clang-tidy runs from the qualified p2996 prefix with a
  compile database, so it belongs to a `cxx:tidy` task in pre-push or CI, not pre-commit. CMake: cmakefmt (Rust,
  drop-in for cmake-format, `--check`, `--staged`, SARIF; `OFF/pages/github.com_cmakefmt_cmakefmt.md`) over hk's
  `Builtins.cmake_format` (Python cmakelang, last release 2020 per R18) and gersemi 0.29.2 (Python; the LLVM libc RFC
  leans to it, `OFF/pages/discourse.llvm.org_t_rfc-having-an-auto-formatter-for-cmake_90511.md`). cmakefmt is young
  (27 stars, v2.0.0 on 2026-10-02, Q85, Q120), so pin it exactly and keep gersemi as the fallback.
- Build tools: CMake 4.4.4, Ninja 1.13.2 and sccache 0.18.0 are current but declared only in the global profile
  (R21 section 1); a C++ CI job needs them in a project config. That is the C++ check ticket's call.

### 7.9 GitHub Actions workflow lockfiles

GitHub put workflow dependency lockfiles (`.github/workflows/actions.lock`, `gh actions-lock`) into public preview
on 2026-10-14 for GitHub Enterprise Cloud (`OFF/pages/github.blog_changelog_2026-10-14-...md`;
`docs.github.com_..._workflow-dependency-lockfiles.md:16`). Dependabot regenerates the lock entry; Renovate already
does (`manager_github-actions.md:140-182`). MP is a personal public repository, so this does not apply yet; inline
SHA pins stay. `gh-actions-lock#132` asks for a cooldown (Q135).

### 7.10 Renovate details that shaped the config

- Renovate updates only the first version listed for a tool (`manager_mise.md:253-286`) and cannot read
  `version_filter` for aqua packages such as `aqua:biomejs/biome` without an `extractVersion` rule (`:359`).
- The `uv` processor installs the uv named by `[tool.uv] required-version` (`pep621/processors/uv.ts:221-226`); MP
  should set it to the `mise.dev.toml` pin so the bot's uv equals CI's (an older uv rewrote the lock, Q168).
- `minimumReleaseAge` with the default strict internal checks holds the branch until the age passes
  (`configuration-options.md:7252-7300`).
- The proposed config extracted `scratch/tcpm-trial/pyproject.toml` only when it was not loaded (Q166); the
  `ignorePaths` entry for `scratch/**` removed it (Q167).
- Runner labels: `ubuntu-latest` is `invalid-version` for Renovate (Q167); D156's explicit `ubuntu-26.04` makes the
  runner a tracked dependency.

### 7.11 Proposal: `.github/renovate.json` (not applied; validated with `--strict`, dry-run in Q167)

The validated copy is `OFF/local/proposed-renovate.json`; the block below adds the pre-1.0 rule and the global
observe switch, which change no extraction.

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "description": "MP dependency updates (R22, D157, D158). One bot for every ecosystem; agents only on a red PR.",
  "extends": ["config:recommended", "helpers:pinGitHubActionDigests", ":semanticCommits"],
  "baseBranchPatterns": ["codex/marketplace-native-onboarding"],
  "timezone": "America/Chicago",
  "schedule": ["at any time"],
  "minimumReleaseAge": "1 hour",
  "dependencyDashboard": true,
  "dependencyDashboardApproval": true,
  "prConcurrentLimit": 10,
  "prHourlyLimit": 0,
  "rebaseWhen": "conflicted",
  "labels": ["dependencies"],
  "constraints": { "mise": "2026.10.10" },
  "lockFileMaintenance": { "enabled": true, "schedule": ["before 6am on monday"] },
  "ignorePaths": ["evidence/**", "offline/**", "scratch/**", "dev/fixtures/**", ".claude/worktrees/**"],
  "customManagers": [
    {
      "customType": "regex",
      "description": "hk Pkl package URL: the version appears twice per URL and both must move (dotfiles #248).",
      "managerFilePatterns": ["/(^|/)hk(\\.local)?\\.pkl$/"],
      "matchStrings": ["download/v(?<currentValue>[\\d.]+)/hk@", "hk@(?<currentValue>[\\d.]+)#"],
      "depNameTemplate": "hk",
      "packageNameTemplate": "jdx/hk",
      "datasourceTemplate": "github-releases",
      "extractVersionTemplate": "^v?(?<version>.+)$"
    },
    {
      "customType": "regex",
      "description": "mise floor in mise.dev.toml; grouped with the mise-action version input.",
      "managerFilePatterns": ["/^mise\\.dev\\.toml$/"],
      "matchStrings": ["min_version = \"(?<currentValue>[\\d.]+)\""],
      "depNameTemplate": "jdx/mise",
      "datasourceTemplate": "github-releases",
      "extractVersionTemplate": "^v?(?<version>.+)$"
    },
    {
      "customType": "regex",
      "description": "vcpkg builtin-baseline follows microsoft/vcpkg master by digest (no native manager, renovate#7135).",
      "managerFilePatterns": ["/(^|/)vcpkg\\.json$/"],
      "matchStrings": ["\"builtin-baseline\":\\s*\"(?<currentDigest>[a-f0-9]{40})\""],
      "depNameTemplate": "microsoft/vcpkg",
      "packageNameTemplate": "https://github.com/microsoft/vcpkg",
      "currentValueTemplate": "master",
      "datasourceTemplate": "git-refs"
    },
    {
      "customType": "regex",
      "description": "uv required-version in pyproject.toml; grouped with the mise.dev.toml uv pin.",
      "managerFilePatterns": ["/^pyproject\\.toml$/"],
      "matchStrings": ["required-version = \"==(?<currentValue>[\\d.]+)\""],
      "depNameTemplate": "uv",
      "packageNameTemplate": "astral-sh/uv",
      "datasourceTemplate": "github-releases"
    }
  ],
  "packageRules": [
    {
      "description": "Patch, minor, digest, pin and lock maintenance merge on green required checks.",
      "matchUpdateTypes": ["patch", "minor", "digest", "pin", "pinDigest", "lockFileMaintenance"],
      "automerge": true,
      "automergeType": "pr",
      "platformAutomerge": true
    },
    {
      "description": "Majors wait for review.",
      "matchUpdateTypes": ["major"],
      "automerge": false,
      "labels": ["dependencies", "needs-review"]
    },
    {
      "description": "Pre-1.0 minors are breaking by their projects' policy (uv versioning, R21 finding 5).",
      "matchCurrentVersion": "/^v?0\\./",
      "matchUpdateTypes": ["minor"],
      "automerge": false,
      "labels": ["dependencies", "needs-review"]
    },
    { "description": "hk URL and pin move together (dotfiles #1090).", "matchDepNames": ["hk"], "groupName": "hk" },
    { "matchDepNames": ["jdx/mise", "mise"], "groupName": "mise" },
    { "matchDepNames": ["uv"], "groupName": "uv" },
    {
      "description": "C++ inputs wait for a C++ CI job before they may automerge.",
      "matchDepNames": ["microsoft/vcpkg"],
      "automerge": false,
      "schedule": ["before 6am on monday"],
      "labels": ["dependencies", "cxx"]
    },
    {
      "description": "The 19 frozen baseline files: dashboard approval, one grouped PR, never automerged; check:acceptance-baseline fails it until the reviewed transition lands (CT-08).",
      "matchFileNames": [
        ".claude-plugin/marketplace.json", ".github/workflows/acceptance.yml", ".gitignore", "README.md",
        "ci/acceptance.sh", "mise.lock", "mise.toml",
        "plugins/aggregated-research/.claude-plugin/plugin.json", "plugins/aggregated-research/.lsp.json",
        "plugins/aggregated-research/README.md", "plugins/aggregated-research/bin/aggregated-research",
        "plugins/aggregated-research/bin/mise-env", "plugins/aggregated-research/bin/ty",
        "plugins/aggregated-research/docs/bin-wrapper-decision.md", "plugins/aggregated-research/hooks/hooks.json",
        "plugins/aggregated-research/mise.toml",
        "plugins/aggregated-research/skills/aggregated-research/SKILL.md",
        "plugins/aggregated-research/skills/aggregated-research/references/acceptance-509.md",
        "plugins/aggregated-research/spine-budgets.toml"
      ],
      "dependencyDashboardApproval": true,
      "automerge": false,
      "groupName": "frozen baseline transition",
      "labels": ["dependencies", "baseline-transition"]
    }
  ]
}
```

Notes: the top-level `"dependencyDashboardApproval": true` is the observe mode; deleting that one line (after the
`acceptance.yml` filter lands) turns PR creation on, while the frozen rule keeps its own approval. The frozen list
duplicates `baseline-files.json`, the same small debt R18 accepted for `hk.pkl`. `baseBranchPatterns` moves to
`main` (or is removed) when the onboarding branch becomes the default branch. `constraints.mise` is itself tracked by
Renovate's `renovate-config` manager (Q167).

### 7.12 Proposal: workflows (not applied)

`.github/workflows/renovate.yml` (new; SHAs resolved 2026-10-14):

```yaml
name: renovate

on:
  schedule:
    - cron: "17 * * * *" # hourly; PRs still wait for minimumReleaseAge (1 hour)
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: renovate
  cancel-in-progress: false

jobs:
  renovate:
    runs-on: ubuntu-26.04 # D156
    timeout-minutes: 30
    steps:
      - name: Mint the Renovate App token
        id: app-token
        uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3.3.0
        with:
          app-id: ${{ vars.RENOVATE_APP_ID }}
          private-key: ${{ secrets.RENOVATE_APP_PRIVATE_KEY }}
          permission-contents: write
          permission-pull-requests: write
          permission-issues: write
          permission-workflows: write
          permission-statuses: write
      - name: Run Renovate
        uses: renovatebot/github-action@f0f41e5f2e706165f6814b1d0f0d0e319de7d1d9 # v46.3.8
        with:
          token: ${{ steps.app-token.outputs.token }}
          renovate-version: 44.158.1
        env:
          RENOVATE_REPOSITORIES: ${{ github.repository }}
          RENOVATE_ONBOARDING: "false"
          RENOVATE_REQUIRE_CONFIG: required
          RENOVATE_PLATFORM_COMMIT: enabled
          # mise lock runs in MISE_SAFE mode; no unsafe execution is allowlisted.
          RENOVATE_ALLOWED_UNSAFE_EXECUTIONS: "[]"
          LOG_LEVEL: info
```

`.github/workflows/deps-triage.yml` (new): the only hand-off to an agent, a label on a red bot PR.

```yaml
name: deps-triage

on:
  workflow_run:
    workflows: [research-fast, "development checks"]
    types: [completed]

permissions:
  pull-requests: write

jobs:
  label:
    if: >-
      github.event.workflow_run.conclusion == 'failure' &&
      startsWith(github.event.workflow_run.head_branch, 'renovate/')
    runs-on: ubuntu-26.04
    timeout-minutes: 5
    steps:
      - name: Mark the bot PR for an agent
        env:
          GH_TOKEN: ${{ github.token }}
          BRANCH: ${{ github.event.workflow_run.head_branch }}
        run: gh pr edit "$BRANCH" --repo "$GITHUB_REPOSITORY" --add-label deps-agent
```

It checks out nothing, so the `workflow_run` trigger runs no PR code; jactionlint may still flag the trigger and the
finding is acknowledged in its baseline (UNVERIFIED until jactionlint runs on it).

`.github/workflows/acceptance.yml` (frozen; only inside R21 batch 4's reviewed transition): add a path filter so the
two `claude -p` sessions run only when acceptance inputs change.

```yaml
on:
  pull_request:
    paths:
      - ".claude-plugin/**"
      - ".github/workflows/acceptance.yml"
      - "README.md"
      - "ci/**"
      - "mise.lock"
      - "mise.toml"
      - "plugins/**"
  workflow_dispatch:
```

R18's proposed `./dev/mise x -- hk check --all --no-fail-fast` step in `research-fast.yml` and R17's CI range scan
are the required checks Renovate's automerge waits on.

### 7.13 Proposal: settings, release age and uv (not applied)

`mise.dev.toml`:

```toml
[settings]
experimental = true
# D158: hold new releases for one hour (mise's default is 24h). Exact pins and mise.dev.lock entries are
# never filtered; this governs `latest`, `--bump` and `ls-remote`. dev/mise unsets the env override.
minimum_release_age = "1h"
# A plain `mise lock` keeps the three platforms dev/bootstrap.py LOCK_PLATFORMS requires.
lockfile_platforms = ["macos-arm64", "linux-arm64", "linux-x64"]
```

`dev/mise:23` becomes
`unset MISE_ENV MISE_ENV_FILE MISE_TASK_SKIP_DEPENDS MISE_MINIMUM_RELEASE_AGE __MISE_DIFF __MISE_SESSION __MISE_ORIG_PATH`.

`pyproject.toml`:

```toml
[tool.uv]
package = false
# Equal to the mise.dev.toml uv pin; Renovate installs this uv for uv.lock and moves both in one PR.
required-version = "==0.13.0"
# D158: one-hour cooldown for every resolution, transitive included (uv.lock records exclude-newer-span).
exclude-newer = "1 hour"
```

`required-version` moves to `==0.13.1` in the same commit as R21 batch 1's uv bump (uv refuses to run when the two
differ, which is the point: the bot's uv and CI's uv stay equal).

### 7.14 Proposal: mise tasks (not applied; `mise.dev.toml`)

Each task is one native command; the ecosystem is the task name, so `deps:update -- <ecosystem|name>` becomes
`./dev/mise run deps:update:<ecosystem> -- <spec>` with no dispatch logic. Rollback is `git restore` of the changed
files by the caller.

```toml
[tasks."deps:outdated"]
description = "Read-only: newer versions for project tools and Python (honours the 1h release age)"
dir = "{{config_root}}"
run = [
  '"$MARKETPLACE_MISE_BIN" outdated --bump --local',
  'uv tree --outdated --depth 1 --no-python-downloads',
]

[tasks."deps:update:tool"]
description = "Bump one mise.dev.toml tool and its three-platform mise.dev.lock entry; installs nothing"
dir = "{{config_root}}"
usage = 'arg "<spec>" help="tool@version, for example uv@0.13.1"'
run = '"$MARKETPLACE_MISE_BIN" lock "${usage_spec?}" --platform macos-arm64,linux-arm64,linux-x64'

[tasks."deps:update:python"]
description = "Pin one direct Python dependency and relock uv.lock; syncs nothing"
dir = "{{config_root}}"
usage = 'arg "<spec>" help="package==version"'
run = 'uv add --no-sync --no-python-downloads "${usage_spec?}"'

[tasks."deps:update:python-lock"]
description = "Refresh one transitive Python package in uv.lock"
dir = "{{config_root}}"
usage = 'arg "<package>"'
run = 'uv lock --no-python-downloads --upgrade-package "${usage_package?}"'

[tasks."deps:update:actions"]
description = "Update workflow actions and pin them by full SHA with a version comment (frozen files excluded)"
dir = "{{config_root}}"
run = "pinact run --update"

[tasks."deps:update:vcpkg"]
description = "Move vcpkg.json builtin-baseline to the registry head (needs the vcpkg tool)"
dir = "{{config_root}}"
run = "vcpkg x-update-baseline"

[tasks."deps:update-all"]
description = "Local fallback for the bot: one native command per ecosystem; review the diff, then deps:verify"
dir = "{{config_root}}"
run = [
  '"$MARKETPLACE_MISE_BIN" upgrade --bump --local --no-prune',
  '"$MARKETPLACE_MISE_BIN" run deps:lock',
  'uv lock --upgrade --no-python-downloads',
  'pinact run --update',
]

[tasks."deps:verify"]
description = "Gate for any dependency change: locks, named checks and every hk step"
dir = "{{config_root}}"
depends = ["deps:check", "check", "check:acceptance-baseline", "check:research"]
run = "hk check --all --no-fail-fast"
```

Supporting config: `.pinact.yaml` (`version: 3`, `files:` listing `research-fast.yml`, `development.yml`,
`renovate.yml`, `deps-triage.yml`, so the frozen `acceptance.yml` is never rewritten); `pinact = "5.0.0"` in
`mise.dev.toml` `[tools]` with its `TOOL_BACKENDS` data row in `dev/bootstrap.py:22`. `deps:update:npm`
(`pnpm --dir mods update "${usage_spec?}"`) arrives with A2's mods lane. A ranked report or transactional rollback
is a C++ ticket.

### 7.15 Proposal: hk additions for TypeScript and C++ (on top of R18 section 7.6; not applied)

```pkl
// D158 TypeScript (mods, A2). Inert until mods/ exists: no matching files, no run. Binaries come from
// mods/node_modules (pnpm, versions in mods/package.json, updated by Renovate's npm manager).
local modsTs = List("mods/**/*.ts", ".claude/skills/workflow-mods/**/*.ts")
local typescript = new Mapping<String, Step> {
  // Biome as formatter only; the builtin's check declares effect "write", this one only reads.
  ["biome"] = (Builtins.biome) {
    glob = modsTs + List("mods/**/*.json")
    check = new CommandSpec {
      command = new Command {
        argv = List("mods/node_modules/.bin/biome", "format", "--config-path", "mods", "--no-errors-on-unmatched", "{{files}}")
      }
      effect = "read"
    }
    fix = new CommandSpec {
      command = new Command {
        argv = List("mods/node_modules/.bin/biome", "format", "--config-path", "mods", "--write", "--no-errors-on-unmatched", "{{files}}")
      }
      effect = "write"
    }
  }
  // oxlint type-aware (tsgolint) catches unawaited promises in mods (A2 S4).
  ["oxlint"] = (Builtins.ox_lint) {
    glob = modsTs
    check = new CommandSpec {
      command = new Command {
        argv = List("mods/node_modules/.bin/oxlint", "-c", "mods/.oxlintrc.json", "--tsconfig", "mods/tsconfig.json",
          "--type-aware", "--deny-warnings", "{{files}}")
      }
      effect = "read"
    }
  }
  // TypeScript 7 project check; the builtin declares "write", tsc --noEmit only reads.
  ["tsc"] = (Builtins.tsc) {
    glob = modsTs
    check = new CommandSpec { command = "mods/node_modules/.bin/tsc --noEmit -p mods/tsconfig.json"; effect = "read" }
  }
}

// D158 C++ core. Opt-in profile until the C++ check ticket lands .clang-format and .cmakefmt.yaml, one
// formatting commit, and a fixture proving `typename [: ... :]` and `^^T` survive formatting.
local cxx = new Mapping<String, Step> {
  ["clang-format"] = (Builtins.clang_format) {
    glob = List("src/**/*.cpp", "include/**/*.hpp", "tests/**/*.cpp", "dev/toolchains/*.cpp")
    exclude = styleExclude
    profiles = List("cxx")
  }
  ["cmakefmt"] {
    glob = List("**/CMakeLists.txt", "**/*.cmake")
    exclude = styleExclude
    profiles = List("cxx")
    check = new CommandSpec { command = new Command { argv = List("cmakefmt", "--check", "{{files}}") }; effect = "read" }
    fix = new CommandSpec { command = new Command { argv = List("cmakefmt", "--in-place", "{{files}}") }; effect = "write" }
  }
}
```

Wiring: `...typescript` joins R18's `linters` in `pre-commit`, `check` and `fix`; `...cxx` replaces the
`clang-format` entry in R18's `adopt` mapping. clang-tidy is a `cxx:tidy` mise task in `pre-push` (compile database
plus the p2996 prefix), owned by the C++ check ticket. `mise.dev.toml` rows:
`"github:cmakefmt/cmakefmt" = "2.2.0"` and the static clang-format 21 binary through
`github:cpp-linter/clang-tools-static-binaries` (per-platform `asset_pattern` UNVERIFIED for Linux; measured only
`macos-arm64`). A2's section 2.8 lists `actionlint` and `zizmor` builtins; R18 replaced both with jactionlint, so the
A2 lane should take R18's step instead.

### 7.16 Lane split and order (unit-size limit: at most five maintained files, about 300 handwritten lines)

| Order | Lane | Files (maintained) | Handwritten lines | Depends on | Checks |
|---|---|---|---|---|---|
| 1 | R17 scanner lane (`scanner-betterleaks`, allocated) | R17's | R17's | none | R17's |
| 2 | `deps-age` | `mise.dev.toml` (settings), `dev/mise`, `pyproject.toml`, `uv.lock` (generated) | about 12 | 1 (serial writer on `mise.dev.toml`) | named checks; `./dev/mise latest uv`; `uv lock --check` |
| 3 | R18 hk lane | R18's (`hk.pkl`, `mise.dev.toml`, `research-fast.yml`, ...) | R18's | 2 | R18's |
| 4 | `deps-tasks` | `mise.dev.toml` (tasks, pinact row), `mise.dev.lock` (generated), `.pinact.yaml`, `dev/bootstrap.py` (data row) | about 80 | 3 | named checks; each task once in a scratch worktree; `test:bootstrap`; `deps:check` |
| 5 | `deps-bot` (observe mode) | `.github/renovate.json`, `.github/workflows/renovate.yml`, `.github/workflows/deps-triage.yml`, `docs/agents/dependency-updates.md` (runbook) | about 270 (`renovate.json` is over 80, reviewer reads it in full) | 3; user admissions: GitHub App, secret and variable, default branch decision | `renovate-config-validator --strict`; local `--platform=local` lookup; jactionlint via hk |
| 6 | R21 batch 4 baseline transition (CT-08) | frozen files, including the `acceptance.yml` path filter, plus the transition record | per CT-08 | 5 (the grouped frozen PR can be its vehicle); admitted acceptance run | `check:acceptance-baseline` fails before the record and passes after; admitted acceptance |
| 7 | `deps-bot-live` | `.github/renovate.json` (delete the global approval line) | 1 | 6; user admissions: "Allow auto-merge", base-branch ruleset with required checks | one bot PR merges on green with no agent |
| later | C++ formatter steps | `hk.pkl` (`cxx` mapping), `mise.dev.toml`, `mise.dev.lock`, `dev/bootstrap.py`, `.cmakefmt.yaml` | about 40 | 3 and the C++ check ticket's style decision | `hk run check --profile cxx` |
| later | TypeScript steps | inside A2's mods lanes (`hk.pkl` `typescript` mapping) | about 35 | A2 mods scaffold | `hk check --all` with `mods/` present |

## 8. Code examples found

- `renovatebot/renovate` at `fc4719beca3b9f40d5f711b1f9464187f6b041cf`: `lib/modules/manager/mise/artifacts.ts:149-279`
  (safe-mode lock, `MISE_ENV`, scoped tools), `lockfile.ts:10-50` (env lock names), `lib/modules/manager/util.ts:175-209`
  (only the named lock is committed), `lib/modules/manager/pep621/processors/uv.ts:195-280` (uv constraint from
  `required-version`). Local: `OFF/repos/renovatebot_renovate/`.
- `jdx/renovate-config` main `dbd76304`: `default.json` (automerge non-major, 7-day age, digest pinning) and
  `.github/workflows/mise-lock.yml` (bare per-lockfile `mise lock` with `MISE_SAFE=1` on Renovate branches). Local:
  `OFF/api/contents/`.
- `ray-manaloto/dotfiles` `7744a9c6`: `renovate.json:1-271` (custom managers for hk Pkl, git-refs digests, deb),
  `.github/workflows/refresh.yml` (App-token lock refresh and PR-reactive lock repair), `.github/actions/open-refresh-pr/action.yml`
  (`peter-evans/create-pull-request` plus `gh pr merge --auto --squash`).
- `jdx/hk` v2.6.0 (`b2107143`): `pkl/builtins/{biome,ox_lint,oxfmt,tsc,clang_format,cmake_format}.pkl`; local
  R18OFF `repos/hk/`.
- `cmakefmt/cmakefmt` v2.2.0 release assets with `.sigstore` bundles and `SHA256SUMS` (Q85).

## 9. Routes table

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| preflight | Firecrawl credits | `fnox ... exec -- firecrawl credits --json` | 0 | -128 credits | gap recorded |
| preflight | Serper, SerpApi | `printf 'X-API-KEY: %s\n' "$SERPER_API_KEY" \| curl -H @- .../account`; `printf '%s' "$SERP_API_KEY" \| curl -G --url-query 'api_key@-' .../account.json` | 0, 0 | 1,297; 243 | yes |
| preflight | GitHub | `gh api rate_limit` | 0 | search 30, code 10 | yes |
| 1 | Exa | `printf 'x-api-key: %s\n' "$EXA_API_KEY" \| curl -H @- -X POST --data @<body> https://api.exa.ai/search` | 0 (x12) | 8 each | yes |
| 1 | Context7 | `ctx7 library <name> <query> --json` | 1 (x3) | 0 | no: monthly quota |
| 1 | Firecrawl | `firecrawl search ...` | not sent | 0 | no: credits |
| 1 | webclaw | `webclaw <url> -f markdown > OFF/pages/<file>.md` | 0 (x56) | 56 | yes |
| 1 | Serper | `curl -H @- -X POST --data @<q.json> https://google.serper.dev/search` | 0 (x3) | 10 each | yes |
| 1 | SerpApi | `curl -G --url-query 'api_key@-' --url-query 'q@<file>' https://serpapi.com/search.json` | 0 | 9 | yes |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py <topic> --plan <json> --emit=json --quick --days 30` | 0 | 8, none relevant | no (DEGRADED) |
| 1 | GitHub releases and contents | `gh api repos/<o>/<r>/releases?per_page=10`; `gh api repos/<o>/<r>/contents/<path>` | 0 (x20) | see section 3 | yes |
| 1 | git clone | `git -c core.hooksPath=/dev/null clone --filter=blob:none --no-checkout --depth 1 <url>` plus sparse checkout | 0 | 1 | yes |
| 2 | repository checks | `gh api repos/<o>/<r>` | 0 (x11) | 1 each | yes |
| 2 | issue and PR views | `gh issue view <n> --repo <r> --comments --json ...`; `gh pr view <n> --repo <r> --json ...` | 0 (x19) | 1 each | yes |
| 2 | issue and PR search | `gh search issues\|prs <q> --repo <r> --limit 20 --json ...` | 0 (x13) | 0 to 200 | partly |
| 2 | GraphQL discussions | `gh api graphql -f query='search(type:DISCUSSION ...)' -f q='repo:<r> <q>'`; `repository{discussion(number:)}` | 0 (x5) | 0 to 29 | partly |
| 2 | commit history | `gh api 'repos/<o>/<r>/commits?path=<p>&per_page=N'` | 0 (x2) | 9, 8 | yes |
| 2 | saved-search equivalent | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5 -F page=1` plus README control | 0 (x10) | see section 5 | yes |
| local | Renovate lock simulation | isolated env, `MISE_ENV=dev MISE_SAFE=1 mise --cd <clone> lock uv` | 0 | 1 | yes |
| local | dev/mise scoped lock and release age | `./dev/mise lock uv@0.13.1 --platform ...`; `./dev/mise latest uv` | 0 | 1 each | yes |
| local | Renovate validator and lookup | `renovate-config-validator --strict`; `RENOVATE_GITHUB_COM_TOKEN=... renovate --platform=local --dry-run=lookup --report-type=file` | 0; 1 (Node 26 engine warning only) | 27 deps | yes |
| local | uv | `uv lock --upgrade --dry-run`, `uv lock --check` with three uv versions; relative `exclude-newer` | 0 | 1 each | yes |
| local | tool timing | `/usr/bin/time -p <tool> ...` three runs | see 7.8 | 1 each | yes |
| local | MP repository state | `gh api repos/...` (settings, branches, protection, secret names, runs) | 0 | 1 | yes |

## 10. Proposed saved-search rows

Not written to `dev/saved-searches.toml`; the owning lane decides.

```toml
# Automated updates (research R22, decisions D157 and D158, 2026-10-14)
[[search]]
id = "renovate-mise-safe-lock"
query = "MISE_SAFE"
repo = "renovatebot/renovate"                  # 2 hits today; control README 63
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "dependabot-mise-ecosystem"
query = "filename:dependabot-mise.gemspec"
repo = "dependabot/dependabot-core"            # 0 today (EMPTY_VERIFIED); a hit reopens the bot choice
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "renovate-vcpkg-manager"
query = "path:lib/modules/manager/vcpkg"
repo = "renovatebot/renovate"                  # 0 today; a hit retires the custom vcpkg manager
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "hk-cmakefmt-builtin"
query = "cmakefmt"
repo = "jdx/hk"                                # 0 today; a hit allows Builtins.cmakefmt
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 11. Open gaps

- Context7 hit its monthly quota on every call (Q19 to Q21) and Firecrawl was out of credits (Q1, Q22); webclaw,
  Exa, Serper and SerpApi covered the same pages. Last30Days was DEGRADED (Q100): the "vs" topic switched it to
  comparison mode, which ignored the plan, and no social signal on Renovate versus Dependabot was found.
- Not run, so UNVERIFIED: the Renovate GitHub Action itself (image pull time, App-token commit identity with
  `RENOVATE_PLATFORM_COMMIT`), Renovate's lock step on a Linux runner (simulated on macOS with the same command), the
  pnpm 12 artifact path, the vcpkg `git-refs` update producing a correct `builtin-baseline` (lookup found the digest
  dependency, Q167, but no branch was written), `vcpkg x-update-baseline`, `pinact run --update` on MP, the Linux
  `asset_pattern` for static clang-format, and jactionlint's view of `deps-triage.yml`.
- The hosted-app lock behaviour is contested (jdx's workflow comment versus dotfiles' comment); self-hosted avoids
  the question but the fallback inherits it.
- The p2996 fork's own clang-format was not available on this host (the managed prefix is set per lane), so its
  handling of `typename [: ... :]` is unknown; upstream 21 and 23 both remove the space.
- The agent-touch rate for MP is extrapolated from dotfiles (Q141), a larger repository; UNVERIFIED.
- The user's interactive shell's mise hook created a `.venv` when a command changed directory into the scratch
  clone; the clone is scratch-only and MP was untouched, but later commands avoided `cd`.
- `OFF/local/proposed-renovate.json` is the validated draft; section 7.11 adds the pre-1.0 rule and the observe
  switch after validation (re-run `renovate-config-validator --strict` in the `deps-bot` lane).
