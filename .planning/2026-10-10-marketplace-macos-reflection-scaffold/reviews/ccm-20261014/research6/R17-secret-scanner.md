# R17: secret scanner comparison (gitleaks, betterleaks, kingfisher and others)

Run R17, research6 team, 2026-10-14. Decision served: D150 (switch MP to betterleaks only if it
provides the same features MP uses from gitleaks), with the user's mid-run question whether hk's
kingfisher builtin should be used instead. Licence filter D136 applied. Query log:
`offline/research/R17/queries.jsonl` (106 rows); mirror manifest: `offline/research/R17/manifest.json`.

## 1. Verdict

**Switch MP to betterleaks 1.9.x (pinned to the 1.x line), not to betterleaks 2.0 and not to
kingfisher. Confidence: high for the compatibility facts, medium for the long-term choice.**

What decides it:

1. Betterleaks 1.9.0 is a flag and report superset of gitleaks 8.30.1 for everything A09 uses. Every
   flag `dev/git_delivery.py:292-297` passes exists with the same name and meaning (table in
   section 7.2), it reads MP's `.gitleaks.toml` unchanged (`betterleaks config check`: OK, 464 rules),
   its baseline matcher is the same code as gitleaks' (`detect/baseline.go` at v1.9.0 and v8.30.1),
   and its JSON report keeps the location fingerprint `commit:file:rule:line`
   (`report/finding.go:338-347` at v1.9.0). On MP the 226 findings gitleaks reports on the branch
   history appear with identical fingerprints, the private-name rule gives the same counts (0 on the
   published branch, 504 in the 167 unpushed local commits), and the history scan is about 3 to 5 times faster
   (section 7.4).
2. One default-detection gap breaks strict parity: betterleaks 1.2.0 to 1.9.0 and 2.0.0-rc.2 do not
   report a lone AWS access key ID, which gitleaks does (betterleaks#408, opened 2026-10-11; fixed only
   on the v2 main branch by PR #410, merged 2026-10-13; reproduced in section 7.3). A config-only rule
   in `.gitleaks.toml` closes it until a 1.x release carries the fix.
3. Betterleaks 2.0 (rc.2, 2026-10-07) removes five things A09 depends on: `--baseline-path`, the bare
   JSON array with a location `Fingerprint`, `--gitleaks-ignore-path`, `git --pre-commit`, and
   `[[rules.allowlists]]` (rejected at load). Verified: rc.2 exits 1 on MP's `.gitleaks.toml` and 126
   on A09's flags (section 7.2). Moving A09 to v2 is a behaviour rewrite, so it becomes a C++ ticket
   under D112/D113, never new Python.
4. Kingfisher 2.13.0 (Apache-2.0, fastest at about 0.8 s, hk builtin since hk v1.55.0) fails parity on
   MP's own config: it silently ignores `[[rules.allowlists]]`, its regex engine reported 8
   private-name hits on MP history that Go RE2 and Python `re` do not produce, it has no `--log-opts`,
   and its report, fingerprint, baseline and exit codes differ (section 7.5). Adopting it means
   rewriting A09's scan and adjudication logic (a C++ ticket) and passing `--no-validate` and
   `--no-update-check` on every call. Revisit it when the C++ guard lands: it reads the same
   Betterleaks TOML filter form that betterleaks 1.9 and 2.0 accept (section 7.6).
5. Gitleaks itself is effectively frozen: its last release is v8.30.1 (published 2026-03-21), the 24
   commits since are dependency and CI merges (last 2026-07-22), and its creator says he no longer
   fully controls the repository (The New Stack, 2026-03-27, mirror line 102). Staying adds aging
   default rules and a 3 to 5 times slower history scan.
6. Others: TruffleHog is AGPL-3.0 (dropped, D136); Nosey Parker is retired in favour of Titus
   (README line 1, commit 2e6e7f3); Titus (Apache-2.0) has no gitleaks or betterleaks config support,
   no hk builtin and no mise registry entry; ripsecrets (MIT, last release 2025-05-27) has no history
   scan and no TOML rules.

What the switch changes, classified (D112/D113):

| Change | Class |
| --- | --- |
| Pin `"aqua:betterleaks/betterleaks" = "1.9.0"` in `mise.dev.toml`; point the A09 intent's `gitleaks_bin` at that binary | config (allowed now) |
| Add a standalone AWS access key ID rule to `.gitleaks.toml` | config |
| `dev/git_delivery.py:290-291`: also pop `BETTERLEAKS_CONFIG` and `BETTERLEAKS_CONFIG_TOML`, which betterleaks reads before the `GITLEAKS_*` names | fix to existing Python (allowed) |
| `dev/git_delivery.py:292`: pass `--config <root>/.gitleaks.toml`, because betterleaks prefers a `.betterleaks.toml` at the root (`cmd/root.go:270-275`) | fix (one flag) |
| Refuse when the root holds `.gitleaksignore` or `.betterleaksignore`: both tools load it whatever `--gitleaks-ignore-path` says (gitleaks `cmd/root.go:317-321`, betterleaks `cmd/root.go:465`); a gap that exists today | fix |
| Re-adjudicate any pending reviewed baseline with betterleaks: a gitleaks-made baseline suppresses nothing in betterleaks (columns and `Match` differ on all 226 shared findings) | operation |
| hk pre-push guard (CT-82): a custom step, no builtin scans a push range | config (`hk.pkl`) |
| Any move to betterleaks 2.0 or kingfisher in A09 | new logic: C++ ticket |

## Log-built sections (2 to 6)

Built from `offline/research/R17/queries.jsonl` by a scratch script; rows keep their `seq`.
## 2. Queries sent to each tool, plugin or service (stage 1, with preflight)

Exact text as sent. Preflight rows (D142) come first. Context7 and Firecrawl were out of quota, so their planned calls are logged as SKIPPED with CREDITS_EXHAUSTED; webclaw replaced Firecrawl for page fetches.

| seq | stage | provider | exact query | status |
| --- | --- | --- | --- | --- |
| 1 | preflight | firecrawl | `firecrawl credits --json` | SKIPPED / CREDITS_EXHAUSTED |
| 2 | preflight | serper | `GET https://google.serper.dev/account` | OK / NONE |
| 3 | preflight | serpapi | `GET https://serpapi.com/account.json` | OK / NONE |
| 4 | preflight | github | `gh api rate_limit` | OK / NONE |
| 5 | preflight | context7 | `no credit endpoint known (ctx7 whoami shows login only)` | OK / NONE |
| 6 | preflight | exa | `no balance endpoint known` | OK / NONE |
| 7 | 1 | exa | `betterleaks vs gitleaks comparison secret scanner` | OK / NONE |
| 8 | 1 | exa | `betterleaks gitleaks config compatibility .gitleaks.toml migration` | OK / NONE |
| 9 | 1 | exa | `best open source git secret scanner 2026 trufflehog kingfisher noseyparker comparison` | OK / NONE |
| 10 | 1 | exa | `gitleaks maintenance status future development Zach Rice betterleaks announcement` | OK / NONE |
| 11 | 1 | exa | `betterleaks v2 release changelog breaking changes` | OK / NONE |
| 12 | 1 | exa | `titus secret scanner Praetorian license` | OK / NONE |
| 13 | 1 | exa | `ripsecrets sirwart secret scanner pre-commit` | OK / NONE |
| 14 | 1 | exa | `hk jdx builtin betterleaks gitleaks pre-commit hook` | OK / NONE |
| 15 | 1 | context7 | `ctx7 library betterleaks 'config extend useDefault allowlists baseline' --json` | SKIPPED / CREDITS_EXHAUSTED |
| 16 | 1 | context7 | `ctx7 library gitleaks 'config extend useDefault allowlists baseline' --json` | SKIPPED / CREDITS_EXHAUSTED |
| 17 | 1 | firecrawl | `firecrawl scrape (planned: betterleaks README, docs/config.md, v2_migration.md, hk builtins page)` | SKIPPED / CREDITS_EXHAUSTED |
| 18 | 1 | webclaw | `https://raw.githubusercontent.com/betterleaks/betterleaks/main/README.md` | OK / NONE |
| 19 | 1 | webclaw | `https://raw.githubusercontent.com/betterleaks/betterleaks/main/docs/config.md` | OK / NONE |
| 20 | 1 | webclaw | `https://raw.githubusercontent.com/betterleaks/betterleaks/main/docs/v2_migration.md` | OK / NONE |
| 21 | 1 | webclaw | `https://github.com/betterleaks/betterleaks/releases` | OK / NONE |
| 22 | 1 | webclaw | `https://hk.jdx.dev/builtins.html` | OK / NONE |
| 23 | 1 | webclaw | `https://github.com/jdx/hk/pull/750` | OK / NONE |
| 24 | 1 | webclaw | `https://github.com/jdx/hk/pull/749` | OK / NONE |
| 38 | 1 | webclaw | `https://www.bleepingcomputer.com/news/security/betterleaks-a-new-open-source-secrets-scanner-to-replace-gitleaks/` | OK / NONE |
| 39 | 1 | webclaw | `https://thenewstack.io/betterleaks-open-source-secret-scanner/` | OK / NONE |
| 40 | 1 | webclaw | `https://www.aikido.dev/blog/betterleaks-gitleaks-successor` | OK / NONE |
| 41 | 1 | webclaw | `https://faun.dev/toolbox/betterleaks-vs-gitleaks/` | ERROR / HTTP_ERROR |
| 42 | 1 | webclaw | `https://www.helpnetsecurity.com/2026/03/19/betterleaks-open-source-secrets-scanner/` | OK / NONE |
| 43 | 1 | webclaw | `https://raw.githubusercontent.com/gitleaks/gitleaks/master/README.md` | OK / NONE |
| 44 | 1 | webclaw | `https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/COMPARISON.md` | OK / NONE |
| 45 | 1 | webclaw | `https://raw.githubusercontent.com/praetorian-inc/noseyparker/main/README.md` | OK / NONE |
| 46 | 1 | webclaw | `https://raw.githubusercontent.com/betterleaks/betterleaks/v1.9.0/docs/config.md` | OK / NONE |
| 47 | 1 | webclaw | `https://megalinter.io/latest/descriptors/repository_betterleaks/` | OK / NONE |
| 48 | 1 | webclaw | `https://github.com/ruzickap/cks-notes/pull/40` | OK / NONE |
| 49 | 1 | serper | `betterleaks v2 migration baseline-path removed gitleaks config allowlists` | OK / NONE |
| 50 | 1 | serpapi | `gitleaks vs betterleaks pre-commit hook git history scan 2026` | OK / NONE |
| 51 | 1 | webclaw | `https://medium.com/devsecops-ai/i-switched-from-gitleaks-to-betterleaks-heres-what-changed-de286168bf9c` | OK / NONE |
| 52 | 1 | last30days | `last30days.py "betterleaks gitleaks secret scanner" --quick --emit json --no-browser-cookies --web-backend exa --days 30` | OK / NONE |
| 53 | 1 | exa | `mongodb kingfisher secret scanner betterleaks TOML rules gitleaks migration pre-commit` | OK / NONE |
| 54 | 1 | webclaw | `https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/RULES.md` | OK / NONE |
| 55 | 1 | webclaw | `https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/V2_MIGRATION.md` | OK / NONE |
| 56 | 1 | webclaw | `https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/BASELINE.md` | OK / NONE |
| 57 | 1 | webclaw | `https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/CONFIG.md` | OK / NONE |
| 58 | 1 | webclaw | `https://raw.githubusercontent.com/mongodb/kingfisher/main/README.md` | OK / NONE |
| 59 | 1 | webclaw | `https://raw.githubusercontent.com/praetorian-inc/titus/main/README.md` | OK / NONE |
| 60 | 1 | webclaw | `https://raw.githubusercontent.com/sirwart/ripsecrets/main/README.md` | OK / NONE |
| 61 | 1 | webclaw | `https://raw.githubusercontent.com/jdx/hk/main/pkl/builtins/kingfisher.pkl` | OK / NONE |
| 62 | 1 | webclaw | `https://raw.githubusercontent.com/jdx/hk/main/pkl/builtins/betterleaks.pkl` | OK / NONE |
| 63 | 1 | webclaw | `https://raw.githubusercontent.com/jdx/hk/main/pkl/builtins/gitleaks.pkl` | OK / NONE |

## 3. Results from each (hits, top results, used)

| seq | provider | hits | top results (up to 3) | used |
| --- | --- | --- | --- | --- |
| 1 | firecrawl | 0 | remainingCredits -128 of planCredits 1000 | no |
| 2 | serper | 0 | balance 1307, rateLimit 5 | no |
| 3 | serpapi | 0 | plan_searches_left 245 | no |
| 4 | github | 0 | search 30/30, code_search 10/10, graphql 5000/5000 | no |
| 5 | context7 | 0 | classified after the fact | no |
| 6 | exa | 0 | classified after the fact | no |
| 7 | exa | 10 | [Betterleaks vs Gitleaks: Secrets Detection Comparison (2026)](https://faun.dev/toolbox/betterleaks-vs-gitleaks/); [Betterleaks: The Gitleaks Successor Built for Faster Secrets](https://www.aikido.dev/blog/betterleaks-gitleaks-successor); [Rafter - Shannon Entropy Wasn't Enough: Why Betterleaks Repl](https://rafter.so/blog/secrets/betterleaks-replaces-gitleaks) | yes |
| 8 | exa | 10 | [](https://raw.githubusercontent.com/betterleaks/betterleaks/main/docs/v2_migration.md); [docs/config.md](https://github.com/betterleaks/betterleaks/blob/main/docs/config.md); [betterleaks configuration in MegaLinter - MegaLinter by OX S](https://megalinter.io/latest/descriptors/repository_betterleaks/) | yes |
| 9 | exa | 10 | [Kingfisher vs TruffleHog: Secrets Detection Comparison (2026](https://faun.dev/toolbox/kingfisher-vs-trufflehog/); [mongodb/kingfisher: Detect secrets + live validation. Map ..](https://github.com/mongodb/kingfisher); [Best Secrets Detection tools: ranked and compared](https://faun.dev/toolbox/compare-secrets-detection-tools/) | yes |
| 10 | exa | 10 | [Find secrets with Gitleaks](https://github.com/gitleaks/gitleaks); [](https://www.aikido.dev/blog/betterleaks-gitleaks-successor); [Gitleaks creator returns with Betterleaks, an open source se](https://thenewstack.io/betterleaks-open-source-secret-scanner/) | yes |
| 11 | exa | 10 | [Releases · betterleaks/betterleaks · GitHub](https://github.com/betterleaks/betterleaks/releases); [](https://raw.githubusercontent.com/betterleaks/betterleaks/main/docs/v2_migration.md); [github.com/betterleaks/betterleaks/v2](https://pkg.go.dev/github.com/betterleaks/betterleaks/v2) | yes |
| 12 | exa | 10 | [GitHub - praetorian-inc/titus: High-performance secrets scan](https://github.com/praetorian-inc/titus); [README.md at main · praetorian-inc/titus](https://github.com/praetorian-inc/titus/blob/main/README.md); [](https://raw.githubusercontent.com/praetorian-inc/titus/v1.2.10/README.md) | yes |
| 13 | exa | 10 | [sirwart/ripsecrets](https://github.com/sirwart/ripsecrets); [.pre-commit-hooks.yaml](https://github.com/sirwart/ripsecrets/blob/main/.pre-commit-hooks.yaml); [README.md](https://github.com/sirwart/ripsecrets/blob/main/README.md) | yes |
| 14 | exa | 10 | [Built-in Linters Reference \| hk](https://hk.jdx.dev/builtins.html); [feat(gitleaks): add gitleaks config to hk builtin config · P](https://github.com/jdx/hk/pull/749); [feat(betterleaks): add betterleaks config to hk builtin conf](https://github.com/jdx/hk/pull/750) | yes |
| 15 | context7 | 0 | ctx7: Monthly quota reached; 20 bonus requests tomorrow | no |
| 16 | context7 | 0 | ctx7: Monthly quota reached; 20 bonus requests tomorrow | no |
| 17 | firecrawl | 0 | preflight seq 1: remainingCredits -128; fell back to webclaw | no |
| 18 | webclaw | 1 | [betterleaks-README](https://raw.githubusercontent.com/betterleaks/betterleaks/main/README.md) | yes |
| 19 | webclaw | 1 | [betterleaks-docs-config](https://raw.githubusercontent.com/betterleaks/betterleaks/main/docs/config.md) | yes |
| 20 | webclaw | 1 | [betterleaks-docs-v2_migration](https://raw.githubusercontent.com/betterleaks/betterleaks/main/docs/v2_migration.md) | yes |
| 21 | webclaw | 1 | [betterleaks-releases](https://github.com/betterleaks/betterleaks/releases) | yes |
| 22 | webclaw | 1 | [hk-builtins](https://hk.jdx.dev/builtins.html) | yes |
| 23 | webclaw | 1 | [hk-pr-750-betterleaks](https://github.com/jdx/hk/pull/750) | yes |
| 24 | webclaw | 1 | [hk-pr-749-gitleaks](https://github.com/jdx/hk/pull/749) | yes |
| 38 | webclaw | 1 | [bleepingcomputer-betterleaks](https://www.bleepingcomputer.com/news/security/betterleaks-a-new-open-source-secrets-scanner-to-replace-gitleaks/) | yes |
| 39 | webclaw | 1 | [thenewstack-betterleaks](https://thenewstack.io/betterleaks-open-source-secret-scanner/) | yes |
| 40 | webclaw | 1 | [aikido-betterleaks-successor](https://www.aikido.dev/blog/betterleaks-gitleaks-successor) | yes |
| 41 | webclaw | 0 | [faun-betterleaks-vs-gitleaks](https://faun.dev/toolbox/betterleaks-vs-gitleaks/) | no |
| 42 | webclaw | 1 | [helpnetsecurity-betterleaks](https://www.helpnetsecurity.com/2026/03/19/betterleaks-open-source-secrets-scanner/) | no |
| 43 | webclaw | 1 | [gitleaks-README](https://raw.githubusercontent.com/gitleaks/gitleaks/master/README.md) | no |
| 44 | webclaw | 1 | [kingfisher-COMPARISON](https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/COMPARISON.md) | no |
| 45 | webclaw | 1 | [noseyparker-README](https://raw.githubusercontent.com/praetorian-inc/noseyparker/main/README.md) | yes |
| 46 | webclaw | 1 | [betterleaks-v1.9.0-docs-config](https://raw.githubusercontent.com/betterleaks/betterleaks/v1.9.0/docs/config.md) | yes |
| 47 | webclaw | 1 | [megalinter-betterleaks](https://megalinter.io/latest/descriptors/repository_betterleaks/) | no |
| 48 | webclaw | 1 | [ruzickap-cks-notes-pr40](https://github.com/ruzickap/cks-notes/pull/40) | no |
| 49 | serper | 10 | [Find secrets with Gitleaks](https://github.com/gitleaks/gitleaks); [I Switched from Gitleaks to Betterleaks: Here's What ...](https://medium.com/devsecops-ai/i-switched-from-gitleaks-to-betterleaks-heres-what-changed-de286168bf9c); [betterleaks configuration in MegaLinter](https://megalinter.io/9/descriptors/repository_betterleaks/) | no |
| 50 | serpapi | 10 | [Secret Scanning Tools: Gitleaks vs TruffleHog Compared](https://rafter.so/blog/secrets/secret-scanning-tools-comparison); [I Switched from Gitleaks to Betterleaks: Here's What ...](https://medium.com/devsecops-ai/i-switched-from-gitleaks-to-betterleaks-heres-what-changed-de286168bf9c); [Prevent Secrets in Git 2026: Pre-Commit, Gitleaks, Push ...](https://www.decryptiondigest.com/blog/prevent-developers-pushing-secrets-git-pre-commit-gitleaks-guide) | no |
| 51 | webclaw | 1 | [medium-switched-gitleaks-betterleaks](https://medium.com/devsecops-ai/i-switched-from-gitleaks-to-betterleaks-heres-what-changed-de286168bf9c) | no |
| 52 | last30days | 5 | [使用 Betterleaks 檢查 Git 中的 Secret \| Hello Jie](https://blog-hellojie.vercel.app/2026/09/28/2026-%E4%BD%BF%E7%94%A8-Betterleaks-%E6%AA%A2%E6%9F%A5-Git-%E4%B8%AD%E7%9A%84-Secret/); [feat: replace gitleaks with betterleaks 1.8.1](https://github.com/Infisical/cli/pull/406); [Infisical CLI ≥ 0.43.136 (betterleaks) never reports lone AW](https://github.com/jainal09/envdrift/issues/834) | yes |
| 53 | exa | 10 | [Moving to Kingfisher v2.0.x - Kingfisher](https://mongodb.github.io/kingfisher/getting-started/v2-migration/); [Kingfisher Custom Rules - Kingfisher](https://mongodb.github.io/kingfisher/rules/overview/); [Advanced Configuration - Kingfisher](https://mongodb.github.io/kingfisher/usage/advanced/) | yes |
| 54 | webclaw | 1 | [kingfisher-RULES](https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/RULES.md) | yes |
| 55 | webclaw | 1 | [kingfisher-V2_MIGRATION](https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/V2_MIGRATION.md) | yes |
| 56 | webclaw | 1 | [kingfisher-BASELINE](https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/BASELINE.md) | no |
| 57 | webclaw | 1 | [kingfisher-CONFIG](https://raw.githubusercontent.com/mongodb/kingfisher/main/docs/CONFIG.md) | yes |
| 58 | webclaw | 1 | [kingfisher-README](https://raw.githubusercontent.com/mongodb/kingfisher/main/README.md) | yes |
| 59 | webclaw | 1 | [titus-README](https://raw.githubusercontent.com/praetorian-inc/titus/main/README.md) | yes |
| 60 | webclaw | 1 | [ripsecrets-README](https://raw.githubusercontent.com/sirwart/ripsecrets/main/README.md) | yes |
| 61 | webclaw | 1 | [hk-builtin-kingfisher-pkl](https://raw.githubusercontent.com/jdx/hk/main/pkl/builtins/kingfisher.pkl) | yes |
| 62 | webclaw | 1 | [hk-builtin-betterleaks-pkl](https://raw.githubusercontent.com/jdx/hk/main/pkl/builtins/betterleaks.pkl) | yes |
| 63 | webclaw | 1 | [hk-builtin-gitleaks-pkl](https://raw.githubusercontent.com/jdx/hk/main/pkl/builtins/gitleaks.pkl) | yes |

Used means cited below. The Last30Days run (seq 52) reported source status github ok, grounding ok, hackernews no-results, Instagram silent; its GitHub items seeded the AWS regression thread (seq 66, 75 to 77, 80) and the adoption search (seq 74).

## 4. GitHub issues, PRs and discussions searched (stage 2), with the seeding stage-1 row

Repository features were checked first with `gh api repos/<owner>/<repo>` (betterleaks, gitleaks, jdx/hk, mongodb/kingfisher: issues and discussions enabled, none archived). `via` names the stage-2 row whose hit led to a view. Clones and release-metadata calls are listed here because they are GitHub calls seeded by stage 1; `gh-api` is outside the D137 provider enum and is labelled as such in the log.

| seq | provider | query | seeded_by | via | hits | top result | used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | git-clone | `https://github.com/betterleaks/betterleaks.git` | 7 |  | 1 | [betterleaks/betterleaks](https://github.com/betterleaks/betterleaks.git) | yes |
| 26 | git-clone | `https://github.com/gitleaks/gitleaks.git` | 7 |  | 1 | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks.git) | yes |
| 27 | git-clone | `https://github.com/jdx/hk.git` | 14 |  | 1 | [jdx/hk](https://github.com/jdx/hk.git) | yes |
| 28 | git-clone | `https://github.com/mongodb/kingfisher.git` | 9 |  | 1 | [mongodb/kingfisher](https://github.com/mongodb/kingfisher.git) | yes |
| 29 | git-clone | `https://github.com/praetorian-inc/titus.git` | 12 |  | 1 | [praetorian-inc/titus](https://github.com/praetorian-inc/titus.git) | yes |
| 30 | git-clone | `https://github.com/sirwart/ripsecrets.git` | 13 |  | 1 | [sirwart/ripsecrets](https://github.com/sirwart/ripsecrets.git) | yes |
| 31 | git-clone | `https://github.com/trufflesecurity/trufflehog.git` | 9 |  | 1 | [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog.git) | yes |
| 32 | git-clone | `https://github.com/praetorian-inc/noseyparker.git` | 9 |  | 1 | [praetorian-inc/noseyparker](https://github.com/praetorian-inc/noseyparker.git) | yes |
| 33 | gh-api | `gh api repos/betterleaks/betterleaks/releases?per_page=10` | 11 |  | 10 | [v2.0.0-rc.2 2026-10-07](https://github.com/betterleaks/betterleaks/releases/tag/v2.0.0-rc.2) | yes |
| 34 | gh-api | `gh api repos/gitleaks/gitleaks/releases?per_page=10` | 7 |  | 10 | [v8.30.1 2026-03-21](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1) | yes |
| 35 | gh-api | `gh api repos/mongodb/kingfisher/releases?per_page=10` | 9 |  | 10 | [v2.13.0 2026-10-13](https://github.com/mongodb/kingfisher/releases/tag/v2.13.0) | yes |
| 36 | gh-api | `gh api repos/praetorian-inc/titus/releases?per_page=10` | 12 |  | 10 | [v1.2.11 2026-10-08](https://github.com/praetorian-inc/titus/releases/tag/v1.2.11) | yes |
| 37 | gh-api | `gh api repos/sirwart/ripsecrets/releases?per_page=10` | 13 |  | 10 | [v0.1.11 2025-05-27](https://github.com/sirwart/ripsecrets/releases/tag/v0.1.11) | yes |
| 64 | gh-issue-search | `gh search issues "baseline" --repo betterleaks/betterleaks` | 20 |  | 0 | none | no |
| 65 | gh-issue-search | `gh search issues "allowlists v2" --repo betterleaks/betterleaks` | 20 |  | 0 | none | no |
| 66 | gh-issue-search | `gh search issues "aws access key" --repo betterleaks/betterleaks` | 52 |  | 3 | [RFE: Better boundary handling for fragments](https://github.com/betterleaks/betterleaks/issues/57) | yes |
| 67 | gh-issue-search | `gh search issues "betterleaks" --repo gitleaks/gitleaks` | 10 |  | 9 | [GitLeaks overreach flagging variable called "privateKey"](https://github.com/gitleaks/gitleaks/issues/2182) | yes |
| 68 | gh-issue-search | `gh search issues "betterleaks OR gitleaks OR kingfisher" --repo jdx/hk` | 14 |  | 0 | none | no |
| 69 | gh-pr-search | `gh search prs "kingfisher" --repo jdx/hk` | 14 |  | 4 | [feat(builtins): add kingfisher secret scanner](https://github.com/jdx/hk/pull/1160) | yes |
| 70 | gh-pr-search | `gh search prs "betterleaks" --repo jdx/hk` | 14 |  | 5 | [fix(builtins): update betterleaks tests for aws composite rule](https://github.com/jdx/hk/pull/1006) | yes |
| 71 | gh-pr-search | `gh search prs "gitleaks" --repo jdx/hk` | 14 |  | 13 | [fix(builtins): correct gitleaks scan modes](https://github.com/jdx/hk/pull/1248) | yes |
| 72 | gh-issue-search | `gh search issues "gitleaks" --repo mongodb/kingfisher` | 9 |  | 5 | [Benchmark comparison vs. betterleaks?](https://github.com/mongodb/kingfisher/issues/241) | no |
| 73 | gh-issue-search | `gh search issues "allowlist toml" --repo mongodb/kingfisher` | 9 |  | 0 | none | no |
| 74 | gh-pr-search | `gh search prs "replace gitleaks with betterleaks" ` | 52 |  | 20 | [ci: replace gitleaks with betterleaks](https://github.com/zsltg/iq/pull/144) | yes |
| 75 | gh-issue-view | `gh issue view 408 -R betterleaks/betterleaks --comments` | 52 | 66 | 1 | [aws-access-token no longer reports access key IDs without a nearby sec](https://github.com/betterleaks/betterleaks/issues/408) | yes |
| 76 | gh-issue-view | `gh issue view 163 -R betterleaks/betterleaks --comments` | 52 | 66 | 1 | [[bug] redact=100 does not redact secrets when output is json](https://github.com/betterleaks/betterleaks/issues/163) | yes |
| 77 | gh-pr-view | `gh pr view 410 -R betterleaks/betterleaks --comments` | 52 | 66 | 1 | [fix(aws): always report access keys](https://github.com/betterleaks/betterleaks/pull/410) | yes |
| 78 | gh-issue-view | `gh issue view 1028 -R gitleaks/gitleaks --comments` | 10 | 67 | 1 | [Unable to detect secrets introduced during merge](https://github.com/gitleaks/gitleaks/issues/1028) | yes |
| 79 | gh-issue-view | `gh issue view 2017 -R gitleaks/gitleaks --comments` | 10 | 67 | 1 | [Request: Switch released builds to use stdlib for RE?](https://github.com/gitleaks/gitleaks/issues/2017) | no |
| 80 | gh-issue-view | `gh issue view 834 -R jainal09/envdrift --comments` | 52 |  | 1 | [Infisical CLI >= 0.43.136 (betterleaks) never reports lone AWS access ](https://github.com/jainal09/envdrift/issues/834) | yes |
| 81 | gh-pr-view | `gh pr view 406 -R Infisical/cli --comments` | 52 |  | 1 | [feat: replace gitleaks with betterleaks 1.8.1](https://github.com/Infisical/cli/pull/406) | yes |
| 82 | gh-pr-view | `gh pr view 1160 -R jdx/hk --comments` | 14 | 69 | 1 | [feat(builtins): add kingfisher secret scanner](https://github.com/jdx/hk/pull/1160) | yes |
| 83 | gh-pr-view | `gh pr view 1248 -R jdx/hk --comments` | 14 | 71 | 1 | [fix(builtins): correct gitleaks scan modes](https://github.com/jdx/hk/pull/1248) | yes |
| 84 | gh-issue-view | `gh issue view 241 -R mongodb/kingfisher --comments` | 9 | 72 | 1 | [Benchmark comparison vs. betterleaks?](https://github.com/mongodb/kingfisher/issues/241) | no |
| 85 | gh-graphql-discussion | `search(type:DISCUSSION) repo:betterleaks/betterleaks v2` | 11 |  | 1 | [v2 incoming](https://github.com/betterleaks/betterleaks/discussions/360) | yes |
| 86 | gh-graphql-discussion | `search(type:DISCUSSION) repo:betterleaks/betterleaks gitleaks` | 7 |  | 1 | [v2 incoming](https://github.com/betterleaks/betterleaks/discussions/360) | no |
| 87 | gh-graphql-discussion | `search(type:DISCUSSION) repo:gitleaks/gitleaks betterleaks` | 10 |  | 0 | none | no |
| 88 | gh-graphql-discussion | `search(type:DISCUSSION) repo:jdx/hk gitleaks` | 14 | 83 | 3 | [gitleaks builtin passes {{files}}, but 'gitleaks dir' takes exactly on](https://github.com/jdx/hk/discussions/1246) | yes |
| 89 | gh-graphql-discussion | `search(type:DISCUSSION) repo:jdx/hk secret scanner` | 14 |  | 0 | none | no |
| 90 | gh-graphql-discussion | `search(type:DISCUSSION) repo:mongodb/kingfisher betterleaks` | 9 |  | 0 | none | no |
| 91 | gh-graphql-discussion | `repository(betterleaks/betterleaks).discussion(number:360) with comments` | 11 | 85 | 1 | [v2 incoming](https://github.com/betterleaks/betterleaks/discussions/360) | yes |
| 92 | gh-graphql-discussion | `repository(jdx/hk).discussion(number:1246) with comments` | 14 | 88 | 1 | [gitleaks builtin passes {{files}}, but 'gitleaks dir' takes exactly on](https://github.com/jdx/hk/discussions/1246) | yes |
| 93 | gh-graphql-discussion | `repository(jdx/hk).discussion(number:819) with comments` | 14 | 88 | 1 | [gitleaks scans whole directory when passed multiple files](https://github.com/jdx/hk/discussions/819) | no |
| 102 | gh-api | `gh release download v2.0.0-rc.2 -R betterleaks/betterleaks -p betterleaks_2.0.0-rc.2_darwin_arm64.tar.gz -p *c` | 11 |  | 3 | [v2.0.0-rc.2](https://github.com/betterleaks/betterleaks/releases/tag/v2.0.0-rc.2) | yes |
| 103 | gh-api | `gh release download v2.13.0 -R mongodb/kingfisher -p kingfisher-darwin-arm64.tgz` | 9 |  | 1 | [v2.13.0](https://github.com/mongodb/kingfisher/releases/tag/v2.13.0) | yes |

## 5. Saved searches (githubkit route reproduced read-only) and proposed rows

`dev/saved-searches.toml` holds 7 rows, each a GitHub code search `GET /search/code?q=<query> repo:<repo>` with a `README` control (`dev/collect_saved_search.py:157-179`). Because `./dev/mise run research:collect` writes into a tracked path owned by another lane, the equivalent `gh api -X GET search/code -f q='<query> repo:<repo>' -f per_page=5` calls ran into the scratch directory. Seq 94 and 95 re-ran the existing row `codex-schema` and its control as a route health check (878 and 161 hits). The rest are candidate rows for this topic, each with its control; the TOML for them is in section 10.

| seq | role | query | seeded_by | total | first paths | status |
| --- | --- | --- | --- | --- | --- | --- |
| 94 | existing-row | `GET search/code q=schema repo:openai/codex` | None | 878 | `codex-rs/config/src/tui_mouse_scroll.rs`, `codex-rs/core/src/config/schema.md` | OK |
| 95 | control | `GET search/code q=README repo:openai/codex` | None | 161 | `sdk/python/README.md`, `scripts/readme_toc.py` | OK |
| 96 | proposed | `GET search/code q=leaks path:pkl/builtins repo:jdx/hk` | 14 | 2 | `pkl/builtins/gitleaks.pkl`, `pkl/builtins/betterleaks.pkl` | OK |
| 97 | control | `GET search/code q=README repo:jdx/hk` | 14 | 62 | `docs/cli/util.md`, `docs/pirate/cli/util.md` | OK |
| 98 | proposed | `GET search/code q=baseline-path repo:betterleaks/betterleaks` | 20 | 1 | `docs/v2_migration.md` | OK |
| 99 | control | `GET search/code q=README repo:betterleaks/betterleaks` | 20 | 12 | `cmd/generate/config/rules/readme.go`, `cmd/generate/config/rules/openshift.go` | OK |
| 100 | proposed | `GET search/code q=allowlists repo:mongodb/kingfisher` | 53 | 2 | `python/examples/validate.py`, `crates/kingfisher-rules/data/AGENTS.md` | OK |
| 101 | control | `GET search/code q=README repo:mongodb/kingfisher` | 53 | 54 | `crates/kingfisher-scanner/README.md`, `docs/AGENTS.md` | OK |
| 105 | proposed | `GET search/code q=kingfisher path:pkl/builtins repo:jdx/hk` | 14 | 1 | `pkl/builtins/kingfisher.pkl` | OK |
| 106 | proposed | `GET search/code q=aws-secret-access-key optional path:cmd/generate/config/rules repo:betterleaks/betterleaks` | 52 | 1 | `cmd/generate/config/rules/aws.go` | OK |

## 6. Seed-to-search map (stage-1 row to the stage-2 rows it seeded)

| stage-1 seq (provider: query) | stage-2 seqs |
| --- | --- |
| 7 (exa: `betterleaks vs gitleaks comparison secret scanner`) | 25, 26, 34, 86 |
| 9 (exa: `best open source git secret scanner 2026 trufflehog kingfish`) | 28, 31, 32, 35, 72, 73, 84, 90, 103 |
| 10 (exa: `gitleaks maintenance status future development Zach Rice bet`) | 67, 78, 79, 87 |
| 11 (exa: `betterleaks v2 release changelog breaking changes`) | 33, 85, 91, 102 |
| 12 (exa: `titus secret scanner Praetorian license`) | 29, 36 |
| 13 (exa: `ripsecrets sirwart secret scanner pre-commit`) | 30, 37 |
| 14 (exa: `hk jdx builtin betterleaks gitleaks pre-commit hook`) | 27, 68, 69, 70, 71, 82, 83, 88, 89, 92, 93, 96, 97, 105 |
| 20 (webclaw: `https://raw.githubusercontent.com/betterleaks/betterleaks/ma`) | 64, 65, 98, 99 |
| 52 (last30days: `last30days.py "betterleaks gitleaks secret scanner" --quick `) | 66, 74, 75, 76, 77, 80, 81, 106 |
| 53 (exa: `mongodb kingfisher secret scanner betterleaks TOML rules git`) | 100, 101 |

## 7. Findings with citations

Local paths below are under `offline/research/R17/` (the D110 mirror); `repos/<owner>_<repo>` are
blob-less clones at the commits in section 8. Scanner runs were read-only against MP's checkout or a
bare single-branch clone of MP in the scratch directory (`git clone --bare --single-branch`, 28
commits on the branch plus the one tag it carried); reports stayed in scratch because they carry MP
finding paths. Binaries: gitleaks 8.30.1 and betterleaks 1.9.0 already installed under
`~/.local/share/mise/installs/`; betterleaks 2.0.0-rc.2 and kingfisher 2.13.0 downloaded into scratch
and checked against the release checksum and the GitHub asset digest (seq 102, 103). No MP mise file
or global config was changed.

### 7.1 What MP uses gitleaks for today

- Config `.gitleaks.toml:6-7` extends the default rules (`[extend] useDefault = true`);
  `.gitleaks.toml:9-12` adds one rule, `private-tr-project`, a single case-insensitive regex of four
  alternatives built from character classes (no keywords, no entropy); `.gitleaks.toml:14-16` adds a
  rule-level `[[rules.allowlists]]` with one path regex exempting the config file itself.
- A09 `scan()` (`dev/git_delivery.py:283-306`) requires an absolute binary path, drops
  `GITLEAKS_CONFIG` and `GITLEAKS_CONFIG_TOML` (290-291), runs
  `<bin> git --no-banner --redact=100 --log-level=error --gitleaks-ignore-path <empty file>` (292),
  optionally `--baseline-path` (293-294) and `--report-format=json --report-path=-` (295-296), and maps
  exit code 1 to "leaks" and anything but 0 or 1 to failure (302-305). It passes no `--config`, so the
  config comes from auto-discovery of `<root>/.gitleaks.toml`.
- `publish()` scans the staged index with `--pre-commit --staged` (373), then the outbound range with
  `--log-opts=<remote>..<commit>` and a JSON report (392); `fingerprints()` (309-319) needs a JSON
  array of objects with a string `Fingerprint` and refuses duplicates; a reviewed baseline is matched
  by fingerprint set and re-checked with `--baseline-path` expecting exit 0 (393-401).
- Tests stub the scanner with shell scripts keyed on argv (`dev/test_git_delivery.py:178-180`,
  `311`, `342`), so a flag-compatible swap needs no test logic change.
- Install and pin: MP's `mise.dev.toml:5-7` pins only python and uv; `hk.pkl:1,6` pins hk 2.5.0 and
  runs only records, retro-gate merge and retro-gate push steps (`hk.pkl:8-28`), no secret scan. The
  gitleaks binary is the global mise install `gitleaks/8.30.1` (aqua backend), which the global
  config no longer lists (`mise which gitleaks`: not active), while the global config pins
  `aqua:betterleaks/betterleaks` 1.9.0 (`~/.config/mise/config.toml:220`). So A09 already depends on
  an unpinned, unconfigured binary; pinning the scanner in `mise.dev.toml` removes that debt whichever
  tool wins.

### 7.2 Feature parity (MP's uses, four candidates)

| MP use (where) | gitleaks 8.30.1 | betterleaks 1.9.0 | betterleaks 2.0.0-rc.2 | kingfisher 2.13.0 |
| --- | --- | --- | --- | --- |
| Auto-discovers `<root>/.gitleaks.toml` (no `--config`, git_delivery.py:292) | yes | yes, but `.betterleaks.toml` wins if present (`cmd/root.go:270-275`) | no auto-discovery (`pages/betterleaks-docs-v2_migration.md:14,161-163`) | no, explicit `--rules-path` or `--config` only (`pages/kingfisher-CONFIG.md`, "Loading a config") |
| `[extend] useDefault = true` | yes | yes (`config check`: 464 rules) | yes (translated config: 467 rules) | built-ins always on unless `--load-builtins=false`; `[extend]` unused |
| Custom regex rule | yes | yes, same matches | yes, same matches | loads it; 8 extra hits Go RE2 and Python `re` do not make (7.5) |
| `[[rules.allowlists]]` path | yes | yes | rejected at load, exit 1 (`unknown configuration fields: rules.allowlists`) | silently ignored (7.3) |
| Expr `filter` alternative | silently ignored (7.3) | yes | yes | yes |
| `git --log-opts=<range>` (392) | yes | yes | yes (`--log-opts` kept, migration guide line 96) | no; `--since-commit` and `--branch` instead |
| `git --pre-commit --staged` (373) | yes | yes | removed; `git --staged` (migration guide lines 90-91) | `--staged`, which runs `git write-tree` and `git commit-tree` in the target repo (`repos/mongodb_kingfisher` `src/scanner/enumerate.rs:1785-1792`) |
| `--redact=100` gives `REDACTED` in JSON | yes | yes (bug #163 fixed in v1.4.1; verified, all `Secret` = `REDACTED`) | `--redact`, but `match.fingerprint` is the SHA-256 of the secret (migration guide line 326) | `--redact` gives a hash with a fixed public salt (`src/util.rs:108-114`) |
| JSON array with location `Fingerprint` (309-319) | yes | yes, same `commit:file:rule:line` | no: `{schema_version, findings, scan}` envelope | no: `{findings, audit, metadata}`, u64 fingerprint |
| SARIF | yes | yes (SARIF 2.1.0, 228 results on HEAD) | removed (migration guide line 107) | yes, marked experimental |
| `--baseline-path` (293-294, 401) | yes | yes, same `IsNew` code; a gitleaks-made baseline suppresses nothing (7.3) | removed (line 107) | own YAML baseline |
| `--gitleaks-ignore-path` (292) | yes | yes, same flag | removed; `--ignore-file` with secret-hash entries (line 99) | not applicable |
| `--no-banner`, `--log-level=error` | yes | yes | v1 flags give a usage error, exit 126 | different flags |
| Exit codes (302-305) | 0 clean, 1 findings, 1 fatal (missing config also 1) | same; `--exit-code` available in both | 1 findings by default | 0, 200 findings, 205 validated, 1 error, 2 usage, 3 no input (`docs/USAGE.md:1936-1945`) |
| Env names A09 must clear (290-291) | `GITLEAKS_CONFIG(_TOML)` | `BETTERLEAKS_CONFIG(_TOML)` first, then `GITLEAKS_*` (`cmd/root.go:202-209`) | `BETTERLEAKS_*` only | `KF_*` and its config file |
| Lone AWS access key ID (default rules) | reported | not reported (#408) | not reported in rc.2 | not reported |
| Network by default | none | none (validation is opt-in) | none (opt-in, migration guide "Provider requests are opt-in") | validation and update check on by default |

### 7.3 Detection and config parity tests (scratch repositories)

- Repo `parity-repo`: one fake AWS key ID line (the gitleaks testdata value) and one GitHub PAT,
  staged. `--pre-commit --staged`: gitleaks reported `aws-access-token`, `generic-api-key`,
  `github-pat`; betterleaks 1.9.0 and 2.0.0-rc.2 reported only `generic-api-key` and `github-pat`.
  This is betterleaks#408 (2026-10-11, "regression vs gitleaks since v1.1.2"), also seen downstream in
  jainal09/envdrift#834 (2026-10-10: Infisical CLI 0.43.135 with gitleaks found 20 of 20 planted key
  IDs, 0.43.141 with betterleaks found 0 of 20). PR betterleaks#410 (merged 2026-10-13, commit
  c613797) makes the secret component optional, on `main` only: `git log origin/v1.x --grep aws`
  shows nothing after 2026-06-11. hk's own builtin test already works around it (`pkl/builtins/
  betterleaks.pkl` at hk v2.5.0: "aws-access-token alone is not reported since betterleaks 1.2.0").
- Repo `parity2`, MP-shaped config (useDefault, one custom rule with keywords, a
  `[[rules.allowlists]]` path for `allowed.txt`), history scan: gitleaks and betterleaks 1.9.0
  reported only `blocked.txt`; kingfisher reported both `allowed.txt` and `blocked.txt` (allowlist
  ignored, exit 200, no warning); betterleaks 2.0.0-rc.2 refuses this config.
- Same repo, config rewritten with a rule `filter` Expr on `attributes["path"]` instead of the
  allowlist: betterleaks 1.9.0, betterleaks 2.0.0-rc.2 and kingfisher reported only `blocked.txt`;
  gitleaks reported both (it ignores `filter` silently).
- Baseline cross-compatibility on the MP bare clone: betterleaks with its own report as baseline left
  0 findings (exit 0), and so did gitleaks with its own; betterleaks with the gitleaks report as
  baseline left all 237 (exit 1). For the 226 shared findings `Fingerprint`, `Description` and
  `Entropy` match but `StartColumn`, `EndColumn` (all 226) and the redacted `Match` (218) differ, and
  `IsNew` compares those fields.

### 7.4 Speed on MP (macOS arm64, wall time from `/usr/bin/time -p`; hyperfine's mise install is broken and was not reinstalled)

| Scan | gitleaks 8.30.1 | betterleaks 1.9.0 | betterleaks 2.0.0-rc.2 | kingfisher 2.13.0 |
| --- | --- | --- | --- | --- |
| Checkout, default log options (209 commits on all refs), 3 runs | 17.26 to 17.60 s | 3.62 to 3.73 s | not run | not run |
| Checkout, `--log-opts=HEAD` (28 commits) | 8.79 s | 2.10 s | not run | not run |
| Bare clone, full history, MP config, 4 runs | 9.02 to 10.25 s | 1.99 to 3.86 s | 1.27 and 1.59 s (2 runs) | 0.75 to 0.90 s warm, 4.10 s cold |
| Checkout, `--log-opts=--branches --not --remotes` (167 unpushed commits) | 9.54 s | 2.38 s | 1.49 s | not run |
| Checkout, `--log-opts=HEAD~5..HEAD` (A09-sized range) | 0.59 s | 0.39 s | not run | not run |
| Checkout, `--pre-commit --staged` (empty index) | 0.44 s | 0.19 s | not run | not run |

Finding sets: on the branch both Go tools report the same 226 `generic-api-key` findings in
`evidence/` with identical fingerprints; betterleaks adds 2 `ibm-cloud-user-api-key` hits in a
generated `build.ninja` (false positives). With all refs, betterleaks also adds `generic-credential-uri`
(7) and `generic-password` (2), rules split out in v1.8.0 (`pages/betterleaks-releases.md:491-510`),
all in the old-history tag. Both tools report gitleaks-style duplicates (on all refs 1263 findings but
995 distinct fingerprints for gitleaks), which `fingerprints()` refuses, so a wide range can never be
adjudicated by fingerprint set with either tool (a pre-existing A09 limit, not a switch issue).

### 7.5 Kingfisher in detail (the user's mid-run question)

- Strengths: Apache-2.0; Rust with a Vectorscan engine; fastest here; very active (v2.6.0 to v2.13.0
  between 2026-09-23 and 2026-10-13, 46 commits in October so far); macOS arm64 tarball; hk builtin
  `Builtins.kingfisher` since hk v1.55.0 (jdx/hk#1160, merged 2026-08-09), argv
  `kingfisher scan {{files}} --no-update-check --no-validate --quiet` (`pages/hk-builtin-kingfisher-pkl.md`);
  since v2.0 its built-in catalogue is generated from Betterleaks rules and it loads custom rules in
  Betterleaks TOML (`pages/kingfisher-V2_MIGRATION.md`, `pages/kingfisher-RULES.md`).
- Parity failures on MP's config: it loaded `private-tr-project` from `.gitleaks.toml` (1 rule,
  `rules check` exit 0) but on the bare MP clone it reported 8 hits of that rule in 7 files where
  gitleaks, betterleaks 1.9.0 and 2.0.0-rc.2 report none. A hand check of one reported location (MP's
  `decisions.jsonl` line 179, columns 305 to 315) with Python `re` and the same regex finds no match,
  so these are false positives from a regex-semantics difference (root cause not traced; see gaps).
  It ignores the v1 `[[rules.allowlists]]` silently (7.3) and it missed the 226 `generic-api-key`
  findings the Go tools report (different generic detection; those 226 are believed false positives,
  but the sets differ).
- Interface differences A09 would have to absorb: no `--log-opts` (`--since-commit <ref>` plus
  `--branch <ref>`), report schema `{findings, audit, metadata}` with a u64 fingerprint and its own
  YAML baseline, exit code 200 for findings, no config auto-discovery (`pages/kingfisher-CONFIG.md`,
  "Kingfisher does not auto-discover kingfisher.yaml").
- Side effects observed: the first run created `~/Library/Caches/kingfisher/rule-cache` (removed after;
  later runs used `KF_RULE_CACHE_DIR` in scratch); `--staged` writes a tree and a commit object into
  the scanned repository (`src/scanner/enumerate.rs:1785-1792`), so it was not run against MP;
  validation sends candidate credentials to providers unless `--no-validate` is passed.
- Packaging: mise registry lists only `github:mongodb/kingfisher` (no aqua entry, so no aqua checksum
  or provenance policy), against `aqua:betterleaks/betterleaks` and `aqua:gitleaks/gitleaks`.
- Conclusion: kingfisher cannot replace gitleaks without a behaviour rewrite of A09, and its regex
  interpretation would misfire on the publish guard's private-name rule today. Not now; keep it as a
  candidate engine for the C++ guard, where one Betterleaks-format TOML can serve either tool.

### 7.6 One config file for betterleaks 1.9, 2.0 and kingfisher

The Expr filter form is accepted by betterleaks 1.9.0 (v1.9.0 `docs/config.md` line 93: "Filters
replace legacy allowlists"), by 2.0.0-rc.2 and by kingfisher (7.3). A translated copy of MP's config
(the allowlist replaced by a rule `filter` matching the config file's path) passed `config check` on
rc.2 (467 rules) and gave identical results on the bare clone with 1.9.0 and rc.2 (237 findings each,
same rule counts). The launch post promised that "Version 2.x.x's config will be fully backwards
compatible with v1 (and your old gitleaks configs)" (`pages/aikido-betterleaks-successor.md:60`,
2026-03-12), but the v2 guide now rejects legacy fields (`pages/betterleaks-docs-v2_migration.md:166-173`),
so the filter form is the durable choice. Writing it now only costs gitleaks compatibility, which
ignores `filter` and would over-report (fail-safe) if it were ever run again.

### 7.7 Maintenance, releases, licences, binaries, packaging

- gitleaks: MIT; releases v8.30.0 (2025-11-26), v8.30.1 (2026-03-21) and none since (seq 34); 24
  commits since the tag, all dependency, CI or hardening merges, last 2026-07-22. BleepingComputer
  (2026-03-15, `pages/bleepingcomputer-betterleaks.md:39`) and The New Stack (2026-03-27,
  `pages/thenewstack-betterleaks.md:96-102`) report that its creator lost full control of the repo.
  Open since 2022: secrets introduced in merge commits are missed (gitleaks#1028).
- betterleaks: MIT, by the gitleaks author with three co-maintainers (`pages/thenewstack-betterleaks.md:144`),
  sponsored by Aikido; stable releases v1.7.0 (2026-07-23) through v1.9.0 (2026-09-29), v2.0.0-rc.1
  (2026-09-30) and rc.2 (2026-10-07) as prereleases (seq 33). v1 maintenance continues on branch
  `v1.x` (last commit 2026-10-07, "backport v2 updates to v1") with Docker `:v1` and the
  `betterleaks@1` cask (`pages/betterleaks-docs-v2_migration.md:36-37`); the maintainer announced v2 in
  discussion #360 (2026-09-14). Adoption: at least 20 public PRs (the search limit) titled "replace gitleaks with
  betterleaks" (seq 74), including Infisical/cli#406 (merged 2026-09-23).
- kingfisher: Apache-2.0 (MongoDB); releases every few days (seq 35).
- All four have macOS arm64 release assets (seq 33 to 35, 37).
- mise: `aqua:gitleaks/gitleaks`, `aqua:betterleaks/betterleaks`, `github:mongodb/kingfisher`,
  `aqua:sirwart/ripsecrets`, `aqua:trufflesecurity/trufflehog`; Titus and Nosey Parker are absent
  (`mise registry`).

### 7.8 hk wiring: MP now, TR as reference, and what to add

- hk builtins (hk v2.5.0 commit f57261a, unchanged through HEAD eb9a149 for these files):
  `Builtins.gitleaks` scans the working tree with `gitleaks dir ... .`, with a hidden `scan = "staged"`
  mode that runs `gitleaks git --pre-commit --redact --staged`; `Builtins.betterleaks` runs
  `betterleaks dir --redact --verbose --no-banner {{files}}`; `Builtins.kingfisher` as in 7.5. hk
  discussion #1246 (2026-08-25) documents that `gitleaks dir` with two or more paths silently scans
  `.`, that betterleaks is not affected, and (jdx's reply) that with hk stashing off by default these
  `dir` steps read working-tree content, not the index. No builtin scans a push range.
- The betterleaks builtin breaks on v2: its argv exits 126 on 2.0.0-rc.2 (`--verbose` removed, `-v`
  now means validate), so MP should pin betterleaks 1.x until hk updates the builtin; no hk issue or
  PR about this exists yet (seq 68, 70).
- TR reference (read-only): `<TR>/hk.pkl:13-15` wires `Builtins.betterleaks` with an exclude for
  `offline/**` into pre-commit only (`<TR>/hk.pkl:90-93`), `<TR>/mise.toml:2-4` pins hk 2.5.0 and
  `aqua:betterleaks/betterleaks` 1.9.0, and `<TR>/.betterleaks.toml:1-8` extends the defaults with a v1
  global `[allowlist]` for `offline/`. Improvements for MP: scan the index rather than working-tree
  files, add a pre-push range scan (TR has none), and use the filter form so v2 does not reject the
  config.
- Proposed config-only steps for `hk.pkl` (CT-82), using the exact flags A09 already uses:

```pkl
["pre-commit"] {
    stash = "none"
    steps {
        ["records"] { check = "./dev/mise run check:records" }
        ["secret-guard-staged"] {
            check = "betterleaks git --pre-commit --staged --no-banner --redact --log-level=error --config .gitleaks.toml ."
        }
    }
}
["pre-push"] {
    stash = "none"
    steps {
        ["retro-gate"] { check = "./dev/mise run retro:gate-push" }
        ["secret-guard-outbound"] {
            check = "betterleaks git --no-banner --redact --log-level=error --config .gitleaks.toml --log-opts='--branches --not --remotes' ."
        }
    }
}
```

  `--branches --not --remotes` scans every local-branch commit no remote-tracking ref contains, a
  superset of any push, without parsing `{{hook_stdin}}` (parsing the pushed refs would be new logic,
  so a C++ ticket). Measured today it would refuse every push: 504 `private-tr-project` findings in the
  167 unpushed commits on MP's 12 local branches (old history), so it lands after D150's deletion of
  integrated local branches. The binary must come from the pinned mise tool, not PATH guesswork.

### 7.9 Redaction and published reports

MP keeps secret-scan evidence in tracked paths (for example
`evidence/vcpkg-fmt-build/pre-review-secret-scan.json`), and A09 reads a reviewed baseline report
from inside the checkout (`dev/git_delivery.py:349-355`). With gitleaks or betterleaks 1.9.0 a
redacted report holds `REDACTED` plus location fingerprints, so nothing about a secret's value
leaves. Betterleaks 2.0 puts an unkeyed SHA-256 of each matched value in `match.fingerprint`, kept
through redaction (`pages/betterleaks-docs-v2_migration.md:326-333`); for the private-name rule the
matched value is the private name itself, so a published v2 report would carry a dictionary-checkable
hash of it unless scans use `--hmac-key` (keyed fingerprints, same page lines 286-287). Kingfisher's `--redact` hash
uses a fixed salt compiled into the binary (`src/util.rs:108-114`), the same exposure. This is a
design input for the C++ ticket that would adopt either.

### 7.10 Other scanners considered

- TruffleHog: AGPL-3.0 (`repos/trufflesecurity_trufflehog/LICENSE`), excluded by D136.
- Nosey Parker: Apache-2.0 but retired: README line 1 "Nosey Parker is now Replaced by Titus"
  (`pages/noseyparker-README.md`), last release v0.24.0 (2025-05-08).
- Titus: Apache-2.0, Go, rules drawn from Nosey Parker and Kingfisher (`pages/titus-README.md:9`),
  `titus scan --git` for history, JSON and SARIF reports; no gitleaks or betterleaks config, no
  baseline flag found in the README, no hk builtin, not in the mise registry. Not executed.
- ripsecrets: MIT, Rust, pre-commit focused (`pages/ripsecrets-README.md:11`), custom patterns only via
  `--additional-pattern`, no history scan, last release v0.1.11 (2025-05-27). Not executed.

## 8. Code examples found

| Repository | Path and lines | Commit or permalink | What it shows |
| --- | --- | --- | --- |
| betterleaks/betterleaks | `cmd/root.go:202-209, 270-275, 445-477` | v1.9.0, 81aff7a638638aae3a659845d089043e1d8fe9ac | env precedence, `.betterleaks.toml` before `.gitleaks.toml`, ignore files always loaded from the source dir, baseline load |
| betterleaks/betterleaks | `report/finding.go:338-347`, `detect/baseline.go` (`IsNew`) | v1.9.0 | location fingerprint and baseline matcher identical to gitleaks |
| betterleaks/betterleaks | `docs/config.md` filter example (mirror lines 403-418) | main, c613797a684337a014168063577bb6fa6e3b6296 | Expr `filter` replacing allowlists |
| betterleaks/betterleaks | PR #410 `cmd/generate/config/rules/aws.go`, `config/betterleaks.toml` | c613797 (2026-10-13) | AWS key ID reported without a secret component |
| gitleaks/gitleaks | `cmd/root.go:300-321`, `detect/detect.go:714` | v8.30.1, 83d9cd684c87d95d656c1458ef04895a7f1cbd8e | ignore-file loading, fingerprint format |
| jdx/hk | `pkl/builtins/gitleaks.pkl`, `pkl/builtins/betterleaks.pkl` | v2.5.0, f57261aea0cf5a57fc85274ba2c522165e5284c2 | builtin argv and staged mode |
| jdx/hk | `pkl/builtins/kingfisher.pkl` | HEAD eb9a14961bd96909919a58c7c8010bb0684c7af9 | kingfisher builtin argv, exit 200 |
| mongodb/kingfisher | `src/scanner/enumerate.rs:1785-1792`, `src/util.rs:108-114`, `docs/USAGE.md:1936-1945` | 8244f7bdbc8d9fa08514205a6394da7318e06812 | staged scan writes objects; salted redaction hash; exit codes |
| Infisical/cli | PR #406 | https://github.com/Infisical/cli/pull/406 | a production gitleaks to betterleaks 1.8.1 swap (and its AWS regression, envdrift#834) |

## 9. Routes table

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
| --- | --- | --- | --- | --- | --- |
| preflight | Firecrawl credits | `firecrawl credits --json` | 0 | remainingCredits -128 | skipped Firecrawl |
| preflight | Serper account | `GET google.serper.dev/account` with `X-API-KEY` from env | 0 | balance 1307 | yes |
| preflight | SerpApi account | `GET serpapi.com/account.json` (key from env; response trimmed to counts) | 0 | 245 left | yes |
| preflight | GitHub | `gh api rate_limit` | 0 | search 30, code 10, graphql 5000 | yes |
| 1 | Exa search | `POST api.exa.ai/search` `{query, numResults: 10, type: auto}` | 0 | 9 calls x 10 | yes |
| 1 | Context7 | `ctx7 library <name> <query> --json` | 1 | quota reached | no (gap) |
| 1 | Firecrawl | not called (credits exhausted) | n/a | 0 | no (gap) |
| 1 | webclaw | `webclaw <url> -f markdown > pages/<name>.md` | 0 (1 for faun.dev, HTTP 403) | 30 pages | yes |
| 1 | Serper | `POST google.serper.dev/search {q, num: 10}` | 0 | 10 | listed |
| 1 | SerpApi | `GET serpapi.com/search.json?engine=google&q=...` | 0 | 10 | listed |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py "<topic>" --quick --emit json --no-browser-cookies --web-backend exa --days 30` | 0 | 5 | yes |
| 2 | git clone | `git clone --filter=blob:none <url> repos/<name>` | 0 | 8 repos | yes |
| 2 | gh release metadata | `gh api repos/<o>/<r>/releases?per_page=10` | 0 | 5 repos | yes |
| 2 | gh issue and PR search | `gh search issues|prs "<q>" --repo <o>/<r> --limit 20 --json ...` | 0 | 11 searches, 4 empty | yes |
| 2 | gh issue and PR view | `gh issue|pr view <n> -R <o>/<r> --comments` plus `--json title,body,...` | 0 | 10 | yes |
| 2 | GraphQL discussions | `gh api graphql` search type DISCUSSION, then `repository.discussion(number)` | 0 | 6 searches, 3 views | yes |
| 2 | saved code search (reproduced) | `gh api -X GET search/code -f q='<query> repo:<repo>' -f per_page=5` | 0 | 12 calls | yes |
| 2 | release download | `gh release download <tag> -R <o>/<r> -p <asset>` plus digest check | 0 | 2 | yes |
| local | scanner runs | gitleaks, betterleaks 1.9.0 and 2.0.0-rc.2, kingfisher 2.13.0 against MP read-only and scratch repos | see 7.3, 7.4 | n/a | yes |

## 10. Proposed saved-search rows

Not added to `dev/saved-searches.toml` (another lane owns it). Counts are from seq 96 to 106 today.

```toml
# Secret scanner watch (research R17, decision D150, 2026-10-14)
[[search]]
id = "hk-secret-scanner-builtins"
query = "leaks path:pkl/builtins"
repo = "jdx/hk"                               # 2 hits (gitleaks.pkl, betterleaks.pkl); control README 62
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "hk-kingfisher-builtin"
query = "kingfisher path:pkl/builtins"
repo = "jdx/hk"                               # 1 hit (kingfisher.pkl); control README 62
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "betterleaks-baseline-path"
query = "baseline-path"
repo = "betterleaks/betterleaks"              # 1 hit (docs/v2_migration.md, removal note); control README 12
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "betterleaks-aws-key-standalone"
query = "aws-secret-access-key optional path:cmd/generate/config/rules"
repo = "betterleaks/betterleaks"              # 1 hit (aws.go, PR #410 on main); control README 12
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "kingfisher-allowlists"
query = "allowlists"
repo = "mongodb/kingfisher"                   # 2 hits, none in the TOML loader; control README 54
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

Code search reads only the default branch, so `betterleaks-aws-key-standalone` cannot see the `v1.x`
branch; watching the fix reach 1.x needs the releases API (a D138 watch-loop input, not a code
search).

## 11. Open gaps

- Context7 monthly quota was exhausted (seq 15, 16) and Firecrawl credits were negative (seq 1, 17);
  both recorded, neither retried. webclaw got HTTP 403 from faun.dev (seq 41).
- The cause of kingfisher's 8 extra private-name matches is not traced (a regex translation or
  Vectorscan semantics difference is the likely cause: UNVERIFIED). Only one location was checked by
  hand.
- How long betterleaks keeps the 1.x line and when #410 reaches a 1.x release are unknown
  (UNVERIFIED); the migration guide states only that v1 maintenance releases continue.
- Whether betterleaks 1.9.0 scans merge-commit content that gitleaks misses (gitleaks#1028) was not
  tested; the `v1.x` commit "detect merge commits" (88e48e9, 2026-10-05) is after v1.9.0.
- Speed figures come from 3 or 4 runs on one machine with `/usr/bin/time`; hyperfine was unavailable
  without a global reinstall.
- Titus and ripsecrets were evaluated from their READMEs only; kingfisher's BASELINE and hk discussion
  #1261 (hk v2 rollout) were mirrored or listed but not analysed.
- Side effects during the run, both undone: kingfisher created `~/Library/Caches/kingfisher` (deleted),
  and mise auto-created an empty `.venv` inside the kingfisher clone when the shell entered it
  (deleted; no repository code ran).
