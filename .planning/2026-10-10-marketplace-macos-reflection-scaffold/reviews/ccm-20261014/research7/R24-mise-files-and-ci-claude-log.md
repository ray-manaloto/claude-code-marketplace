# R24 log: D137 query log and log-built sections for R-180 (mise files and Claude Code in CI)

Companion to `R24-mise-files-and-ci-claude.md` (same directory), session `ccm-20261014` (`ce9c0b3d`),
2026-10-14 (UTC 2026-10-15T00:0x for the late rows). Built entirely from `OR/queries.jsonl` (103 rows,
SHA-256 in `OR/manifest.json` `queries_jsonl_sha256`) by `S/bin/sections.py`; every call was logged when it
ran, and stage-2 rows recorded their seed then. S = `scratchpad/r180/`; OR = `S/OR/`; `Qn` = row `seq = n`.
Scripts: `S/bin/` (`fx` fnox wrapper, `q.py` Exa/Serper/SerpApi, `c7.sh` Context7, `wc.sh` webclaw,
`clone.sh`, `g.py` read-only gh, `miso` isolated mise, `log.py`, `manifest.py`, `secretscan.py`,
`sections.py`). No MP file, global config or GitHub state changed; no tool installed; no `claude` session.

## Verdict (from the report)

One root `mise.toml` and `mise.lock` (design E: image tools `os = ["linux"]`, image built with
`MISE_ENABLE_TOOLS`), delivered in the v3 baseline transition with the Claude Code bump; Claude Code in CI and
in the image through mise's `github:anthropics/claude-code` backend, exact-pinned to the newest `latest`
channel release at least one hour old (2.1.300 today), `DISABLE_UPDATES=1`, moved by Renovate. The two files
exist because the frozen OCI image definition could not hold the macOS development surface added on
2026-10-10 (`f9c0ec3`), and `dev/mise` reads only `mise.dev.toml` through `MISE_OVERRIDE_CONFIG_FILENAMES`,
not through mise's `MISE_ENV`.

## 1. Queries sent to each tool, plugin or service (preflight and stage 1), exact text

| seq | stage | provider | exact query, URL or command |
| --- | --- | --- | --- |
| 1 | preflight | firecrawl | `firecrawl credits --json` |
| 2 | preflight | serper | `GET https://google.serper.dev/account (X-API-KEY from env)` |
| 3 | preflight | serpapi | `GET https://serpapi.com/account.json (api_key from env)` |
| 4 | preflight | context7 | `GET https://context7.com/api/v2/usage (bearer from env)` |
| 5 | preflight | exa | `no balance endpoint known (research-workflow.md Preflight); first call classified after the fact` |
| 6 | preflight | last30days | `GET https://api.scrapecreators.com/v1/account/credit-balance (x-api-key from env)` |
| 7 | preflight | gh-issue-search | `gh api rate_limit` |
| 8 | preflight | webclaw | `command -v webclaw (local binary 0.6.23 via mise github backend)` |
| 9 | 1 | exa | `mise environments mise.<env>.toml MISE_ENV config layering lock file mise.<env>.lock` |
| 10 | 1 | context7 | `ctx7 library mise environments MISE_ENV lock file` |
| 11 | 1 | context7 | `ctx7 docs /jdx/mise config environments MISE_ENV mise.dev.toml mise.dev.lock lockfile per environment` |
| 12 | 1 | context7 | `ctx7 docs /jdx/mise mise oci build [oci] section which config files tools os filter MISE_OVERRIDE_CONFIG_FILENAMES` |
| 13 | 1 | context7 | `ctx7 docs /websites/code_claude native install script specific version install.sh stable latest claude install command checksum verification` |
| 14 | 1 | webclaw | `https://code.claude.com/docs/en/setup.md` |
| 15 | 1 | webclaw | `https://code.claude.com/docs/en/github-actions.md` |
| 16 | 1 | webclaw | `https://code.claude.com/docs/en/troubleshoot-install.md` |
| 17 | 1 | webclaw | `https://mise.jdx.dev/configuration/environments.html` |
| 18 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/mise-lock.html` |
| 19 | 1 | webclaw | `https://mise.jdx.dev/configuration.html` |
| 20 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/mise-oci.html` |
| 21 | 1 | webclaw | `https://claude.ai/install.sh` |
| 22 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/latest` |
| 23 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/stable` |
| 24 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json` |
| 25 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/latest` |
| 26 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/stable` |
| 27 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json` |
| 28 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.292/manifest.json` |
| 29 | 1 | git-clone | `git clone --filter=blob:none https://github.com/anthropics/claude-code-action.git` |
| 30 | 1 | git-clone | `git clone --filter=blob:none --branch v2026.10.10 https://github.com/jdx/mise.git` |
| 31 | 1 | webclaw | `https://raw.githubusercontent.com/aquaproj/aqua-registry/main/pkgs/anthropics/claude-code/registry.yaml` |
| 32 | 1 | serper | `mise "mise.dev.toml" MISE_ENV dev tools CI separate config` |
| 33 | 1 | serper | `claude code CI github actions pin version native installer "install.sh" "bash -s"` |
| 34 | 1 | serper | `mise "aqua:anthropics/claude-code" OR "claude-code" mise.toml native binary` |
| 35 | 1 | serper | `mise minimum_release_age setting npm aqua cooldown 24h "minimum_release_age"` |
| 36 | 1 | serper | `renovate mise manager "mise.toml" aqua backend claude-code minimumReleaseAge` |
| 37 | 1 | serper | `"mise oci build" MISE_ENV environment config files image` |
| 38 | 1 | serpapi | `claude code github release assets "SHASUMS256.txt" claude-linux-x64.tar.gz` |
| 39 | 1 | webclaw | `https://mise.jdx.dev/configuration/settings.html` |
| 40 | 1 | webclaw | `https://mise-tools.jdx.dev/tools/claude-code` |
| 41 | 1 | webclaw | `https://mise.jdx.dev/tasks/task-configuration.html` |
| 42 | 1 | webclaw | `https://docs.renovatebot.com/modules/manager/mise/` |
| 43 | 1 | webclaw | `https://docs.renovatebot.com/configuration-options/` |
| 44 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/backends/aqua.html` |
| 45 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/backends/http.html` |
| 46 | 1 | last30days | `topic "Claude Code in CI pinned version native installer and mise" --plan OR/local/last30days/plan.json (3 subqueries: Claude Code CI pin native installer; mise claude-code aqua native binary; mise MISE_ENV mise.dev.toml environments lockfile; sources reddit,hackernews,github) --emit=json --quick --` |
| 92 | 1 | webclaw | `https://downloads.claude.ai/keys/claude-code.asc` |
| 93 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json.sig` |

## 2. Results from each (preflight and stage 1)

| seq | provider | rc / HTTP | hits | status / failure_code | top results | used |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | firecrawl | 0 / 200 | - | SKIPPED / CREDITS_EXHAUSTED | - | yes |
| 2 | serper | 0 / 200 | - | OK / NONE | - | yes |
| 3 | serpapi | 0 / 200 | - | OK / NONE | - | yes |
| 4 | context7 | 0 / 200 | - | OK / NONE | - | yes |
| 5 | exa | None / - | - | OK / NONE | - | yes |
| 6 | last30days | 0 / 200 | - | DEGRADED / CREDITS_EXHAUSTED | - | yes |
| 7 | gh-issue-search | 0 / 200 | - | OK / NONE | - | yes |
| 8 | webclaw | 0 / - | - | OK / NONE | - | yes |
| 9 | exa | 0 / 402 | 0 | SKIPPED / CREDITS_EXHAUSTED | - | yes |
| 10 | context7 | 0 / - | 5 | OK / NONE | - | yes |
| 11 | context7 | 0 / - | 5 | OK / NONE | https://github.com/jdx/mise/blob/main/docs/dev-tools/mise-lock.md; https://github.com/jdx/mise/blob/main/docs/dev-tools/mise-lock.md; https://github.com/jdx/mise/blob/main/docs/dev-tools/mise-lock.md | yes |
| 12 | context7 | 0 / - | 9 | OK / NONE | https://github.com/jdx/mise/blob/main/docs/cli/oci/build.md; https://github.com/jdx/mise/blob/main/docs/dev-tools/mise-oci.md; https://github.com/me/my-app | yes |
| 13 | context7 | 0 / - | 5 | OK / NONE | https://code.claude.com/docs/en/setup; https://claude.ai/install.sh; https://code.claude.com/docs/en/troubleshoot-install | yes |
| 14 | webclaw | 0 / - | 1 | OK / NONE | https://code.claude.com/docs/en/setup.md | yes |
| 15 | webclaw | 0 / - | 1 | OK / NONE | https://code.claude.com/docs/en/github-actions.md | yes |
| 16 | webclaw | 0 / - | 1 | OK / NONE | https://code.claude.com/docs/en/troubleshoot-install.md | no |
| 17 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/configuration/environments.html | yes |
| 18 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/dev-tools/mise-lock.html | yes |
| 19 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/configuration.html | yes |
| 20 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/dev-tools/mise-oci.html | yes |
| 21 | webclaw | 0 / - | 1 | OK / NONE | https://claude.ai/install.sh | yes |
| 22 | webclaw | 2 / - | 0 | ERROR / OTHER | https://downloads.claude.ai/claude-code-releases/latest | no |
| 23 | webclaw | 2 / - | 0 | ERROR / OTHER | https://downloads.claude.ai/claude-code-releases/stable | no |
| 24 | webclaw | 2 / - | 0 | ERROR / OTHER | https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json | no |
| 25 | webclaw | 0 / - | 1 | OK / NONE | https://downloads.claude.ai/claude-code-releases/latest | yes |
| 26 | webclaw | 0 / - | 1 | OK / NONE | https://downloads.claude.ai/claude-code-releases/stable | yes |
| 27 | webclaw | 0 / - | 1 | OK / NONE | https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json | yes |
| 28 | webclaw | 0 / - | 1 | OK / NONE | https://downloads.claude.ai/claude-code-releases/2.1.292/manifest.json | yes |
| 29 | git-clone | 0 / - | 1 | OK / NONE | https://github.com/anthropics/claude-code-action | yes |
| 30 | git-clone | 0 / - | 1 | OK / NONE | https://github.com/jdx/mise | yes |
| 31 | webclaw | 0 / - | 1 | OK / NONE | https://raw.githubusercontent.com/aquaproj/aqua-registry/main/pkgs/anthropics/claude-code/registry.yaml | yes |
| 32 | serper | 0 / 200 | 6 | OK / NONE | https://mise.jdx.dev/environments/; https://github.com/jdx/mise/discussions/5058; https://mac.install.guide/mise/mise-configuration | yes |
| 33 | serper | 0 / 200 | 8 | OK / NONE | https://github.com/anthropics/claude-code-action/issues/1817; https://www.deployhq.com/guides/claude-code; https://github.com/anthropics/claude-code/issues/20044 | yes |
| 34 | serper | 0 / 200 | 7 | OK / NONE | https://mise-tools.jdx.dev/tools/claude-code; https://github.com/Temikus/claude-watchdog; https://github.com/ozzy-labs/agentyard | yes |
| 35 | serper | 0 / 200 | 1 | OK / NONE | https://mise.jdx.dev/configuration/settings.html | yes |
| 36 | serper | 0 / 200 | 3 | OK / NONE | https://mise.jdx.dev/configuration/settings.html; https://mise.jdx.dev/troubleshooting.html; https://bsky.app/profile/andrewnez.mastodon.social.ap.brid.gy | no |
| 37 | serper | 0 / 200 | 8 | OK / NONE | https://github.com/jdx/mise/discussions/13809; https://mise.jdx.dev/configuration.html; https://mise.jdx.dev/dev-tools/mise-oci.html | yes |
| 38 | serpapi | 0 / 200 | 9 | OK / NONE | https://www.target.com/; https://linux.die.net/man/1/tar; https://en.wikipedia.org/wiki/Tar_(computing) | no |
| 39 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/configuration/settings.html | yes |
| 40 | webclaw | 0 / - | 1 | OK / NONE | https://mise-tools.jdx.dev/tools/claude-code | no |
| 41 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/tasks/task-configuration.html | no |
| 42 | webclaw | 0 / - | 1 | OK / NONE | https://docs.renovatebot.com/modules/manager/mise/ | yes |
| 43 | webclaw | 0 / - | 1 | OK / NONE | https://docs.renovatebot.com/configuration-options/ | no |
| 44 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/dev-tools/backends/aqua.html | no |
| 45 | webclaw | 0 / - | 1 | OK / NONE | https://mise.jdx.dev/dev-tools/backends/http.html | no |
| 46 | last30days | 0 / - | 7 | DEGRADED / CREDITS_EXHAUSTED | https://claude.dev/blog/getting-the-most-out-of-opus-5-5/; https://github.com/anthropics/claude-code/tree/main/mods/agents-md; https://github.com/anthropics/claude-code/issues/91870 | no |
| 92 | webclaw | 0 / - | 1 | OK / NONE | https://downloads.claude.ai/keys/claude-code.asc | yes |
| 93 | webclaw | 0 / - | 1 | OK / NONE | https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json.sig | yes |

## 3. GitHub issues, PRs and discussions searched (stage 2)

| seq | provider | query | seeded by | hits | status | top results | used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 47 | gh-repo-features | `gh api repos/anthropics/claude-code --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | - | 1 | OK / NONE | - | yes |
| 48 | gh-repo-features | `gh api repos/anthropics/claude-code-action --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | - | 1 | OK / NONE | - | yes |
| 49 | gh-repo-features | `gh api repos/jdx/mise --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | - | 1 | OK / NONE | - | yes |
| 50 | gh-repo-features | `gh api repos/renovatebot/renovate --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | - | 1 | OK / NONE | - | yes |
| 51 | gh-repo-features | `gh api repos/aquaproj/aqua-registry --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | - | 1 | OK / NONE | - | yes |
| 52 | gh-api | `gh api repos/anthropics/claude-code/releases/tags/v2.1.300 --jq {tag_name,published_at,html_url,assets:[.assets[]\|{name,size,browser_download_url,digest}]}` | 31 | 10 | OK / NONE | https://github.com/anthropics/claude-code/releases/download/v2.1.300/claude-darwin-arm64.tar.gz; https://github.com/anthropics/claude-code/releases/download/v2.1.300/claude-darwin-x64.tar.gz | yes |
| 53 | gh-api | `gh api repos/anthropics/claude-code/attestations/sha256:11e459c4368a48554d5aa5eabf7f6d84a2ff7ae2f7210795394f60ded6633f56 --jq {n:(.attestations\|length)}` | 52 | 1 | OK / NONE | - | yes |
| 54 | gh-api | `gh api repos/anthropics/claude-code/releases?per_page=40 --jq [.[]\|{tag_name,published_at,n_assets:(.assets\|length),has_sums:([.assets[].name]\|index("SHASUMS256.txt")!=null)}]` | 52 | 40 | OK / NONE | - | yes |
| 55 | gh-api | `gh api repos/anthropics/claude-code/attestations/sha256:11e459c4368a48554d5aa5eabf7f6d84a2ff7ae2f7210795394f60ded6633f56 --jq .attestations[0].bundle.dsseEnvelope.payload\|@base64d\|fromjson\|{predicateType, subject:[.su` | 53 | 1 | OK / NONE | - | yes |
| 56 | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 7329) { title url createdAt body comments(first: 15) { nodes { author { login } createdAt body } } } } }` | 30 | 1 | OK / NONE | - | yes |
| 57 | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 13809) { title url createdAt body comments(first: 15) { nodes { author { login } createdAt body } } } } }` | 37 | 1 | OK / NONE | - | yes |
| 58 | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 5058) { title url createdAt body comments(first: 15) { nodes { author { login } createdAt body } } } } }` | 32 | 1 | OK / NONE | - | yes |
| 59 | gh-issue-view | `gh issue view 1817 -R anthropics/claude-code-action --json number,title,state,createdAt,closedAt,body,comments,url` | 33 | 1 | OK / NONE | https://github.com/anthropics/claude-code-action/issues/1817 | yes |
| 60 | gh-issue-search | `gh search issues install.sh specific version --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 21 | 0 | EMPTY_VERIFIED / NONE | - | no |
| 61 | gh-issue-search | `gh search issues SHASUMS256 --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 52 | 2 | OK / NONE | https://github.com/anthropics/claude-code/issues/87652; https://github.com/anthropics/claude-code/issues/69276 | no |
| 62 | gh-issue-search | `gh search issues mise install claude --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 34 | 10 | OK / NONE | https://github.com/anthropics/claude-code/issues/89366; https://github.com/anthropics/claude-code/issues/89609 | no |
| 63 | gh-issue-search | `gh search issues DISABLE_AUTOUPDATER CI container --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 14 | 0 | EMPTY_VERIFIED / NONE | - | no |
| 64 | gh-issue-search | `gh search issues native installer version pin --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 21 | 1 | OK / NONE | https://github.com/anthropics/claude-code/issues/88030 | yes |
| 65 | gh-issue-search | `gh search issues auto-update mise --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 14 | 0 | EMPTY_VERIFIED / NONE | - | no |
| 66 | gh-issue-view | `gh issue view 89609 -R anthropics/claude-code --json number,title,state,createdAt,closedAt,body,url` | 62 | 1 | OK / NONE | https://github.com/anthropics/claude-code/issues/89609 | no |
| 67 | gh-issue-view | `gh issue view 88030 -R anthropics/claude-code --json number,title,state,createdAt,closedAt,body,comments,url` | 64 | 1 | OK / NONE | https://github.com/anthropics/claude-code/issues/88030 | yes |
| 68 | gh-pr-view | `gh pr view 8523 -R jdx/mise --json number,title,state,mergedAt,url,body` | 11 | 1 | OK / NONE | https://github.com/jdx/mise/pull/8523 | yes |
| 69 | gh-pr-view | `gh pr view 7842 -R jdx/mise --json number,title,state,mergedAt,url,body` | 30 | 1 | OK / NONE | https://github.com/jdx/mise/pull/7842 | yes |
| 70 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:jdx/mise enable_tools oci", type: DISCUSSION, first: 10) { discussionCount nodes { ... on Discussion { number title url createdAt } } } }` | 58 | 1 | OK / NONE | https://github.com/jdx/mise/discussions/11548 | no |
| 71 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:jdx/mise override_config_filenames", type: DISCUSSION, first: 10) { discussionCount nodes { ... on Discussion { number title url createdAt } } } }` | 17 | 7 | OK / NONE | https://github.com/jdx/mise/discussions/5433; https://github.com/jdx/mise/discussions/11548 | no |
| 72 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:jdx/mise claude-code aqua", type: DISCUSSION, first: 10) { discussionCount nodes { ... on Discussion { number title url createdAt } } } }` | 30 | 113 | OK / NONE | https://github.com/jdx/mise/discussions/13878; https://github.com/jdx/mise/discussions/14264 | no |
| 73 | gh-issue-search | `gh search issues claude --repo jdx/mise --limit 15 --json number,title,state,createdAt,url --sort created` | 30 | 15 | OK / NONE | https://github.com/jdx/mise/issues/14478; https://github.com/jdx/mise/issues/14449 | yes |
| 74 | gh-issue-view | `gh issue view 14388 -R jdx/mise --json number,title,state,createdAt,closedAt,body,comments,url` | 73 | 1 | OK / NONE | https://github.com/jdx/mise/issues/14388 | yes |
| 75 | gh-issue-view | `gh issue view 14449 -R jdx/mise --json number,title,state,createdAt,closedAt,body,comments,url` | 73 | 1 | OK / NONE | https://github.com/jdx/mise/issues/14449 | yes |
| 76 | gh-pr-search | `gh search prs anthropics/claude-code --repo aquaproj/aqua-registry --limit 10 --json number,title,state,createdAt,url` | 31 | 10 | OK / NONE | https://github.com/aquaproj/aqua-registry/pull/62344; https://github.com/aquaproj/aqua-registry/pull/62129 | yes |
| 77 | gh-issue-search | `gh search issues mise claude --repo renovatebot/renovate --limit 10 --json number,title,state,createdAt,url` | 42 | 0 | EMPTY_VERIFIED / NONE | - | no |
| 78 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:renovatebot/renovate mise github backend", type: DISCUSSION, first: 10) { discussionCount nodes { ... on Discussion { number title url createdAt } } } }` | 42 | 1 | OK / NONE | https://github.com/renovatebot/renovate/discussions/46974 | no |
| 79 | gh-issue-search | `gh search issues claude code version pin --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,url` | 29 | 0 | EMPTY_VERIFIED / NONE | - | no |
| 80 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:anthropics/claude-code-action claude code version", type: DISCUSSION, first: 10) { discussionCount nodes { ... on Discussion { number title url createdAt } } } }` | 29 | 9 | OK / NONE | https://github.com/anthropics/claude-code-action/discussions/1830; https://github.com/anthropics/claude-code-action/discussions/575 | no |
| 81 | gh-issue-search | `gh search issues path_to_claude_code_executable --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,url` | 29 | 10 | OK / NONE | https://github.com/anthropics/claude-code-action/issues/1759; https://github.com/anthropics/claude-code-action/issues/1901 | no |
| 82 | gh-issue-search | `gh search issues install.sh failed --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,url` | 59 | 1 | OK / NONE | https://github.com/anthropics/claude-code-action/issues/1242 | yes |
| 83 | gh-issue-view | `gh issue view 1242 -R anthropics/claude-code-action --json number,title,state,createdAt,closedAt,body,url` | 82 | 1 | OK / NONE | https://github.com/anthropics/claude-code-action/issues/1242 | yes |
| 103 | gh-pr-view | `gh pr view 14450 -R jdx/mise --json number,title,state,mergedAt,url` | 75 | 1 | OK / NONE | https://github.com/jdx/mise/pull/14450 | yes |

## 4. Saved searches run (reproduced read-only with their controls)

| seq | query (repo-scoped, `GET /search/code`) | seeded by | total_count | status | first hit |
| --- | --- | --- | --- | --- | --- |
| 84 | `"claudeCodeVersion =" repo:anthropics/claude-code-action` | 29 | 1 | OK | https://github.com/anthropics/claude-code-action/blob/a26b07d8c778b0c43f64618e5fd29fd0f8af72e8/src/entrypoints/run.ts |
| 85 | `README repo:anthropics/claude-code-action` | 29 | 11 | OK | https://github.com/anthropics/claude-code-action/blob/a26b07d8c778b0c43f64618e5fd29fd0f8af72e8/agent-approval-check/README.md |
| 86 | `"anthropics/claude-code" path:registry repo:jdx/mise` | 30 | 1 | OK | https://github.com/jdx/mise/blob/44df0e923ed223f6a7f418784ca51156318da4c1/registry/claude.toml |
| 87 | `README repo:jdx/mise` | 30 | 93 | OK | https://github.com/jdx/mise/blob/44df0e923ed223f6a7f418784ca51156318da4c1/docs/README.md |
| 88 | `"SHASUMS256.txt" path:pkgs/anthropics/claude-code repo:aquaproj/aqua-registry` | 31 | 1 | OK | https://github.com/aquaproj/aqua-registry/blob/fde48caf03e75fa4260de6ff9313d1b93b3a53a2/pkgs/anthropics/claude-code/registry.yaml |
| 89 | `README repo:aquaproj/aqua-registry` | 31 | 2 | OK | https://github.com/aquaproj/aqua-registry/blob/fde48caf03e75fa4260de6ff9313d1b93b3a53a2/renovate.json5 |
| 90 | `"enable_tools" path:src/toolset repo:jdx/mise` | 58 | 2 | OK | https://github.com/jdx/mise/blob/44df0e923ed223f6a7f418784ca51156318da4c1/src/toolset/mod.rs |
| 91 | `README repo:jdx/mise` | 58 | 93 | OK | https://github.com/jdx/mise/blob/44df0e923ed223f6a7f418784ca51156318da4c1/docs/README.md |

## 5. Seed-to-search map

| seed seq (stage) | provider | what it named | stage-2 rows it seeded |
| --- | --- | --- | --- |
| 11 (1) | context7 | `ctx7 docs /jdx/mise config environments MISE_ENV mise.dev.toml mise.dev.lock lockfile per environment` | 68 |
| 14 (1) | webclaw | `https://code.claude.com/docs/en/setup.md` | 63, 65 |
| 17 (1) | webclaw | `https://mise.jdx.dev/configuration/environments.html` | 71 |
| 21 (1) | webclaw | `https://claude.ai/install.sh` | 60, 64 |
| 29 (1) | git-clone | `git clone --filter=blob:none https://github.com/anthropics/claude-code-action.git` | 79, 80, 81, 84, 85 |
| 30 (1) | git-clone | `git clone --filter=blob:none --branch v2026.10.10 https://github.com/jdx/mise.git` | 56, 69, 72, 73, 86, 87 |
| 31 (1) | webclaw | `https://raw.githubusercontent.com/aquaproj/aqua-registry/main/pkgs/anthropics/claude-code/registry.yaml` | 52, 76, 88, 89 |
| 32 (1) | serper | `mise "mise.dev.toml" MISE_ENV dev tools CI separate config` | 58 |
| 33 (1) | serper | `claude code CI github actions pin version native installer "install.sh" "bash -s"` | 59 |
| 34 (1) | serper | `mise "aqua:anthropics/claude-code" OR "claude-code" mise.toml native binary` | 62 |
| 37 (1) | serper | `"mise oci build" MISE_ENV environment config files image` | 57 |
| 42 (1) | webclaw | `https://docs.renovatebot.com/modules/manager/mise/` | 77, 78 |
| 52 (2) | gh-api | `gh api repos/anthropics/claude-code/releases/tags/v2.1.300 --jq {tag_name,published_at,html_url,assets:[.assets[]\|{name` | 53, 54, 61 |
| 53 (2) | gh-api | `gh api repos/anthropics/claude-code/attestations/sha256:11e459c4368a48554d5aa5eabf7f6d84a2ff7ae2f7210795394f60ded6633f56` | 55 |
| 58 (2) | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 5058) { title url createdAt ` | 70, 90, 91 |
| 59 (2) | gh-issue-view | `gh issue view 1817 -R anthropics/claude-code-action --json number,title,state,createdAt,closedAt,body,comments,url` | 82 |
| 62 (2) | gh-issue-search | `gh search issues mise install claude --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 66 |
| 64 (2) | gh-issue-search | `gh search issues native installer version pin --repo anthropics/claude-code --limit 10 --json number,title,state,created` | 67 |
| 73 (2) | gh-issue-search | `gh search issues claude --repo jdx/mise --limit 15 --json number,title,state,createdAt,url --sort created` | 74, 75 |
| 75 (2) | gh-issue-view | `gh issue view 14449 -R jdx/mise --json number,title,state,createdAt,closedAt,body,comments,url` | 103 |
| 82 (2) | gh-issue-search | `gh search issues install.sh failed --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,u` | 83 |

Stage-2 rows without a seed (repository feature checks, D147): 47, 48, 49, 50, 51.

## 6. Local measurements (stage "local")

| seq | provider | command | result file | note |
| --- | --- | --- | --- | --- |
| 94 | mise-local | `bin/miso config ls \| ls --json, plain vs -E dev vs MISE_OVERRIDE_CONFIG_FILENAMES=mise.dev.toml, on scratch copies of MP mise.toml, mise.lock, mise.dev.toml, mise.dev.lock (HEAD 1fb23d1)` | `OR/local/env-layering.txt` | -E dev loads mise.toml + mise.dev.toml (7 tools incl. npm claude-code, node, gh, jq); the dev/mise override loads only mise.dev.toml (python, uv, betterleaks) |
| 95 | mise-local | `mise latest claude and npm:@anthropic-ai/claude-code under default, MISE_MINIMUM_RELEASE_AGE=1h and 0s (scratch exp/claude, fx profile for GITHUB_TOKEN)` | `OR/local/cooldown-latest.txt` | 24h default -> 2.1.296; 1h -> 2.1.300 at 2026-10-15T00:18Z |
| 96 | mise-local | `mise tool claude; mise lock --platform linux-x64,linux-arm64,macos-arm64 with [tools] claude = "2.1.300" (scratch exp/claude)` | `OR/local/claude-aqua.mise.lock` | backend aqua:anthropics/claude-code, url+sha256 per platform from the GitHub release, no provenance |
| 97 | mise-local | `mise lock --platform linux-x64,macos-arm64 with [tools] "github:anthropics/claude-code" = "2.1.300" (scratch exp/claude-gh)` | `OR/local/claude-github.mise.lock` | url+sha256+provenance github-attestations per platform |
| 98 | mise-local | `draft unified mise.toml (OR/draft/mise.toml): config ls, tasks validate, ls with MISE_ENABLE_TOOLS and MISE_DISABLE_TOOLS; mise lock for 3 platforms` | `OR/local/unified-toolsets.txt` | 69 tasks validate; enable/disable narrow the toolset to the 5 image tools; 21 lock entries, all with url+sha256, 6 of 7 tools with provenance (node none). Side effect: mise auto-created a scratch .venv from copied pyproject/uv.lock (deleted) |
| 99 | mise-local | `draft with os = ["linux"] on claude, node, github-cli, jq (OR/draft/mise.os-linux.toml): ls on macOS, lock for 3 platforms` | `OR/draft/mise.os-linux.lock` | macOS toolset stays python, uv, betterleaks; lock still holds all 3 platforms for every tool |
| 100 | gh-release-download | `gh release download v2.1.300 -R anthropics/claude-code -p claude-darwin-arm64.tar.gz -p SHASUMS256.txt -p SHASUMS256.txt.sig; tar -x; shasum -a 256` | `OR/local/gpg-and-binary-identity.txt` | inner binary sha256 475517ca... = manifest darwin-arm64 checksum = host native-installer binary; tarball deleted after hashing |
| 101 | gpg-local | `scratch GNUPGHOME: import https://downloads.claude.ai/keys/claude-code.asc; gpg --verify SHASUMS256.txt.sig SHASUMS256.txt; gpg --verify manifest.json.sig manifest.json (2.1.300)` | `OR/local/gpg-and-binary-identity.txt` | both Good signature, key 31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE |
| 102 | local-read | `shasum -a 256 ~/.local/share/claude/versions/2.1.300` | `OR/local/host-2.1.300.sha256` |  |

## 7. Row notes (classification fixes and context)

| seq | stage | provider | status / failure_code | note |
| --- | --- | --- | --- | --- |
| 1 | preflight | firecrawl | SKIPPED / CREDITS_EXHAUSTED | remainingCredits -128 of planCredits 1000; route falls back to webclaw then Serper/SerpApi |
| 2 | preflight | serper | OK / NONE | balance 1281, rateLimit 5 |
| 3 | preflight | serpapi | OK / NONE | plan_searches_left 237 of 250 |
| 4 | preflight | context7 | OK / NONE | free plan, member requests 980 of 1000, resets 2026-11-01; 20 left, so this run spends at most 6 |
| 5 | preflight | exa | OK / NONE | credit check unavailable |
| 6 | preflight | last30days | DEGRADED / CREDITS_EXHAUSTED | ScrapeCreators creditCount -7: Reddit/TikTok/Instagram sources dead; Last30Days runs with the remaining sources |
| 7 | preflight | gh-issue-search | OK / NONE | search 30/30, code_search 10/10, graphql 4985/5000 |
| 8 | preflight | webclaw | OK / NONE | local, unmetered |
| 9 | 1 | exa | SKIPPED / CREDITS_EXHAUSTED | 402 tag NO_MORE_CREDITS: Exa classified after the fact (no balance endpoint); later Exa calls skipped |
| 22 | 1 | webclaw | ERROR / OTHER | script error (webclaw got -f twice); retried as seq 25 |
| 23 | 1 | webclaw | ERROR / OTHER | script error; retried as seq 26 |
| 24 | 1 | webclaw | ERROR / OTHER | script error; retried as seq 27 |
| 25 | 1 | webclaw | OK / NONE | 8-byte version pointer (2.1.300 / 2.1.292); the size rule in wc.sh misclassified it, corrected by hand |
| 26 | 1 | webclaw | OK / NONE | 8-byte version pointer (2.1.300 / 2.1.292); the size rule in wc.sh misclassified it, corrected by hand |
| 38 | 1 | serpapi | OK / NONE | Google corpus returned unrelated tar/Target pages (query tokens dropped); not used |
| 46 | 1 | last30days | DEGRADED / CREDITS_EXHAUSTED | source_status grounding=error, github absent from source_status, reddit and hackernews ok; 0 of 7 results on topic (none about CI pinning, mise backends or mise environments); ScrapeCreators at -7 credits (preflight seq 6) |
| 47 | 2 | gh-repo-features | OK / NONE | provider outside the D137 enum: repository feature check (D147) |
| 48 | 2 | gh-repo-features | OK / NONE | feature check |
| 49 | 2 | gh-repo-features | OK / NONE | feature check |
| 50 | 2 | gh-repo-features | OK / NONE | feature check |
| 51 | 2 | gh-repo-features | OK / NONE | feature check; has_discussions false |
| 52 | 2 | gh-api | OK / NONE | provider outside the D137 enum: gh api REST read |
| 53 | 2 | gh-api | OK / NONE | provider outside the D137 enum: gh api REST read |
| 54 | 2 | gh-api | OK / NONE | provider outside the D137 enum: gh api REST read |
| 55 | 2 | gh-api | OK / NONE | provider outside the D137 enum: gh api REST read |
| 94 | local | mise-local | OK / NONE | -E dev loads mise.toml + mise.dev.toml (7 tools incl. npm claude-code, node, gh, jq); the dev/mise override loads only mise.dev.toml (python, uv, betterleaks) |
| 95 | local | mise-local | OK / NONE | 24h default -> 2.1.296; 1h -> 2.1.300 at 2026-10-15T00:18Z |
| 96 | local | mise-local | OK / NONE | backend aqua:anthropics/claude-code, url+sha256 per platform from the GitHub release, no provenance |
| 97 | local | mise-local | OK / NONE | url+sha256+provenance github-attestations per platform |
| 98 | local | mise-local | OK / NONE | 69 tasks validate; enable/disable narrow the toolset to the 5 image tools; 21 lock entries, all with url+sha256, 6 of 7 tools with provenance (node none). Side effect: mise auto-created a scratch .venv from copied pyproject/uv.lock (deleted) |
| 99 | local | mise-local | OK / NONE | macOS toolset stays python, uv, betterleaks; lock still holds all 3 platforms for every tool |
| 100 | local | gh-release-download | OK / NONE | inner binary sha256 475517ca... = manifest darwin-arm64 checksum = host native-installer binary; tarball deleted after hashing |
| 101 | local | gpg-local | OK / NONE | both Good signature, key 31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE |
| 103 | 2 | gh-pr-view | OK / NONE | provider gh-pr-view; merged after the 2026.10.10 release |

## 8. Counts

| stage | provider | status | rows |
| --- | --- | --- | --- |
| 1 | context7 | OK | 4 |
| 1 | exa | SKIPPED | 1 |
| 1 | git-clone | OK | 2 |
| 1 | last30days | DEGRADED | 1 |
| 1 | serpapi | OK | 1 |
| 1 | serper | OK | 6 |
| 1 | webclaw | ERROR | 3 |
| 1 | webclaw | OK | 22 |
| 2 | gh-api | OK | 4 |
| 2 | gh-code-search-saved | OK | 8 |
| 2 | gh-graphql-discussion | OK | 8 |
| 2 | gh-issue-search | EMPTY_VERIFIED | 5 |
| 2 | gh-issue-search | OK | 6 |
| 2 | gh-issue-view | OK | 6 |
| 2 | gh-pr-search | OK | 1 |
| 2 | gh-pr-view | OK | 3 |
| 2 | gh-repo-features | OK | 5 |
| local | gh-release-download | OK | 1 |
| local | gpg-local | OK | 1 |
| local | local-read | OK | 1 |
| local | mise-local | OK | 6 |
| preflight | context7 | OK | 1 |
| preflight | exa | OK | 1 |
| preflight | firecrawl | SKIPPED | 1 |
| preflight | gh-issue-search | OK | 1 |
| preflight | last30days | DEGRADED | 1 |
| preflight | serpapi | OK | 1 |
| preflight | serper | OK | 1 |
| preflight | webclaw | OK | 1 |

Total 103 rows; used by the report: 77.

## Open gaps

- Exa answered HTTP 402 `NO_MORE_CREDITS` on its first call (Q9); Firecrawl and ScrapeCreators were at
  negative credits at preflight (Q1, Q6), so Firecrawl was skipped and Last30Days ran degraded (Q46, 0 of 7
  results on topic). Context7 had 20 requests left (Q4) and this run used 4.
- Q22-Q24 are script errors (webclaw got `-f` twice), retried as Q25-Q27; Q25 and Q26 were first
  misclassified as errors by a size rule and corrected by hand (Q-notes above).
- Q38 (SerpApi) returned unrelated pages; Q60, Q63, Q65, Q77 and Q79 were empty with rc 0
  (`EMPTY_VERIFIED`: the repositories have issues enabled, Q47-Q51).
- Providers outside the D137 enum were used and are named as such: `gh-api` (REST reads), `gh-repo-features`
  (D147 checks), `gh-release-download`, `mise-local`, `gpg-local`, `local-read`.
- No Linux image build and no install ran; those need admissions (report section 11).
