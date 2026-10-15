# R24: why MP has `mise.toml` and `mise.dev.toml`, one file instead, and Claude Code in CI (research, 2026-10-14)

Research agent R24 of session `ccm-20261014` (`ce9c0b3d`), for request R-180 (decision D188, `decisions.jsonl`
row DL-241). Read-only for MP: no tracked or untracked MP file, global config, GitHub state or host install
changed; no `claude` session started. Everything this run wrote is in the session scratchpad
`scratchpad/r180/` (called S below): this report, its log `R24-mise-files-and-ci-claude-log.md`, and the
mirror `S/OR/` (called OR). The mirror sits in S, not in `MP/offline/research/`, because the brief forbids MP
writes. `OR/queries.jsonl` holds all 103 logged calls (D137) with `status` and `failure_code`, and
`OR/manifest.json` lists 185 mirrored items with source, local path, UTC time, command shape, exit code and
SHA-256 or commit. `Qn` cites the log row with `seq = n`. MP = the repository root at HEAD `1fb23d1` on
`codex/marketplace-native-onboarding` (Git dir `.git`, verified first); other writers moved HEAD to `4726121`
and left planning edits during the run, none touching the files cited here. P =
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. Provider calls ran under the `codex_research`
fnox profile; keys came from the environment and were never printed or written (a scan of every mirrored file
for 10 key values found 0 hits). Scratch measurements ran mise in an isolated wrapper (`S/bin/miso`: empty
global and system config, scratch data, cache and state directories, no auto-install, no hooks) on copies of
MP's files; nothing was installed. Anything without a citation is labelled UNVERIFIED.

## 1. Verdict

**Why two files.** They describe two different machines. Root `mise.toml` (with `mise.lock`) is the
definition of the Linux container image that the acceptance workflow builds with `mise oci build`: Claude
Code from npm, node, gh, uv, jq, a pinned Debian base and four apt packages (`mise.toml:1-50`,
`.github/workflows/acceptance.yml:18-35`, commit `05acca2`, 2026-08-28). It became one of the 19 frozen
acceptance-baseline files on 2026-08-29 (`evidence/onboarding/baseline-files.json`, `base_head` `6b5b092`).
When Codex onboarding added a macOS development surface on 2026-10-10 (commit `f9c0ec3`, "build: isolate
lightweight development checks", plan unit N3 "No install/bootstrap; lightweight checks; OCI bytes
preserved", `P/task_plan.md:992`), it could not edit the frozen file and must not install the image's tools on
the host, so it put the development tasks and tools in a second file and a wrapper, `dev/mise`, that makes
mise read only that file (`MISE_OVERRIDE_CONFIG_FILENAMES=mise.dev.toml`, `dev/mise:14`). `dev/bootstrap.py`
enforces the split from the other side by refusing any change to `mise.toml` or `mise.lock`
(`dev/bootstrap.py:21, 188, 224-226`). `mise.dev.toml` is named like a mise config environment, but MP does not
use it as one: the wrapper unsets `MISE_ENV` (`dev/mise:23`), and the layering mise would apply with
`MISE_ENV=dev` is exactly what the split avoids (measured below).

**Recommendation for the files: one root `mise.toml` and one `mise.lock`, delivered in the v3 baseline
transition (D173, DL-224) together with the Claude Code pin bump that already waits for this report (D188).**
The file holds every tool; the four image-only tools carry `os = ["linux"]`, so macOS development keeps
exactly today's three tools (python, uv, betterleaks); Linux CI gets the image tools too (Claude Code among
them); and the image build narrows the toolset with `MISE_ENABLE_TOOLS` in one `oci:build` task. `[oci]`,
`[bootstrap.packages]` and every task row move over unchanged. Draft: `OR/draft/mise.os-linux.toml` (69 tasks
validate, Q98; a 21-entry v3 lock with url and SHA-256 for every tool and platform, `OR/draft/mise.os-linux.lock`, Q99).
Cost: one baseline transition and one lane that edits about 18 files (67 references to `mise.dev.*`), and
afterwards every development-tool bump changes a baseline file unless v3 also re-scopes the frozen set (an
open user decision, section 11).

**Recommendation for Claude Code in CI: the native binary through mise's `github:` backend, exact-pinned in
that one file:** `"github:anthropics/claude-code" = { version = "2.1.300", os = ["linux"] }`. It installs the
same bytes the native installer installs (measured: the binary inside the v2.1.300 GitHub release tarball has
SHA-256 `475517ca…`, which equals both `manifest.json`'s `platforms.darwin-arm64.checksum` and this host's
native-installer binary `~/.local/share/claude/versions/2.1.300`; Q100, Q102), and `mise.lock` records each
platform's URL, SHA-256 and a verified GitHub artifact attestation (`provenance = "github-attestations"`,
Q97). CI installs it with `./dev/mise run tools:prepare` (`mise install --locked`), runs it with
`DISABLE_UPDATES=1`, and the Mend-hosted Renovate app (D162) moves the pin with `minimumReleaseAge` "1 hour"
alongside mise's own `minimum_release_age = "1h"` (R-166). A workflow that uses
`anthropics/claude-code-action` either pins the action by commit SHA (each action release hard-codes one Claude
Code version: v1.0.250 = 2.1.300) or hands it the mise binary through `path_to_claude_code_executable`, so
both routes use one pin.

**Recommendation for the image: the same mise tool.** `mise oci build` copies tools installed on the build
host into one layer each and runs no commands in the image (`OR/pages/mise.jdx.dev_dev-tools_mise-oci.html.md:18-19, 95-104`),
so `install.sh` cannot run inside the build, and the OCI builder does not apply `[bootstrap.apt.sources]`,
which rules out Anthropic's signed apt repository (no reference in `src/oci/` at v2026.10.10, Q30).

**Channel: pin the `latest` channel's versions exactly (2.1.300 today), not `stable`.** npm `stable` and the
native `stable` pointer are both 2.1.292 (Q26; `P/reviews/ccm-20261014/cc-2.1.300/upgrade-plan.md:3-5`),
which predates `onFailure: "block"` (2.1.295), and MP's three deny gates use it
(`.claude/settings.json:84, 131, 143`); the image's 2.1.251 runs them fail-open today
(`P/reviews/ccm-20261014/cc-2.1.300/impact.md:25`). A pin is a version, not a channel; "latest pinned" here
means the newest release at least one hour old, proposed by Renovate and merged only after the named checks
and the admitted acceptance run pass.

Confidence: high on the history, mise's layering, locks, cooldown and the binary identity (measured or read
from source at the host's mise 2026.10.10); medium on the image build honouring `MISE_ENABLE_TOOLS` and `os`
(read from source, `src/toolset/mod.rs:104-125, 872-878`; no Linux build was run, which needs an admission);
medium on the hosted Renovate app keeping `mise.lock` fresh (contested, R22 section 3).

The evidence that decides it:

1. mise environments cannot keep the two toolsets apart. Measured on copies of MP's files: plain `mise` loads
   the image toolset; `mise -E dev` loads `mise.toml` and `mise.dev.toml` together (seven tools, Claude Code
   from npm among them); only the wrapper's filename override yields the three development tools
   (`OR/local/env-layering.txt`, Q94). The docs say the same ("the base `mise.toml` still loads",
   `OR/pages/mise.jdx.dev_configuration_environments.html.md:6`), and the maintainers' answer to "exclude
   tools per environment" is `disable_tools` or `enable_tools`, not environment files (jdx/mise discussion
   #5058, 2025-05-14 to 2026-02-25, Q58).
2. One file can serve both, with mise's own filters. `os = ["linux"]` removes the image tools on macOS and
   still writes all three platforms into the lock; `MISE_ENABLE_TOOLS` narrows the toolset to the five image
   tools (`OR/local/unified-toolsets.txt`, Q98, Q99), and `mise oci build` builds its toolset through the same
   filtered `Toolset::add_version`/`merge` path (`OR/repos/jdx_mise/src/cli/oci/common.rs:80-104, 133-146`,
   `src/toolset/mod.rs:104-125`).
3. The native installer script is a poor CI pin. `install.sh` always downloads and runs the current `latest`
   binary first and passes the pinned version to its `install` command (`OR/pages/claude.ai_install.sh.md:148-149, 226`),
   verifies that bootstrap binary only against an unsigned fetch of `manifest.json` (`:159-167`), and has
   exited 0 without a launcher (claude-code-action#1817, 2026-09-08, open) or after a failed download
   (claude-code-action#1242, 2026-04-20, open).
4. The GitHub release route is signed three ways and mise checks one of them itself: release assets carry
   `SHASUMS256.txt` and `SHASUMS256.txt.sig` (Q52), both GPG signatures verify against the documented key
   `31DD DE24 … 1A7E CACE` (`OR/local/gpg-and-binary-identity.txt`, Q101), and the assets have a GitHub
   release attestation that mise verifies before writing `provenance` (Q53, Q55;
   `OR/pages/mise.jdx.dev_dev-tools_mise-lock.html.md:457-463`).

## 2. Queries sent to each tool, plugin or service (stage 1), exact text

Preflight rows first (D142), then stage 1, all from `OR/queries.jsonl`.

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

## 3. Results from each (stage 1)

Exa answered its first call with HTTP 402 `NO_MORE_CREDITS` (Q9), so no further Exa call was made; Firecrawl
(-128 credits) and ScrapeCreators (-7) were skipped at preflight (Q1, Q6); Context7 had 20 of 1,000 monthly
requests left and this run spent 4 (Q4, Q10-Q13). Last30Days returned 7 items, none on topic (Q46).

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

## 4. GitHub issues, PRs and discussions searched (stage 2)

Each repository was feature-checked first (Q47-Q51, D147): anthropics/claude-code and aquaproj/aqua-registry
have discussions disabled, so no discussion search ran there (`FEATURE_DISABLED`, not searched); no repository
is archived.

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

## 5. Githubkit saved searches run (reproduced read-only, with controls) and proposed rows

`./dev/mise run research:collect` writes into a tracked path, so the equivalent repository-scoped
`GET /search/code` queries ran read-only through `gh api` (the collector's route,
`dev/collect_saved_search.py:44-63`), each followed by its `README` control. Every control returned at least
one hit, so the zero-or-one-hit rows are real results. The proposed `[[search]]` rows are in section 10.

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

## 6. Stage-2 GitHub and saved searches against the stage-1 results (seed-to-search map)

Every stage-2 row recorded its seed when it was chosen. A seed may itself be a stage-2 row (Q52 named Q53;
Q58 named Q70, Q90 and Q91), which the first column shows.

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

## 7. Findings with citations

### 7.1 How the two files came about

| When | Commit or decision | What happened |
| --- | --- | --- |
| 2026-08-28 | `05acca2` (#1) "container mise.toml for the acceptance workflow's OCI build" | Root `mise.toml` created to pin "the runner-built OCI image's tools: claude-code CLI, node (npm backend needs it for the launcher), github-cli, uv …, jq", Debian bookworm-slim, root user. The acceptance workflow builds it (`acceptance.yml:25`). |
| 2026-08-29 | `9bc9c1b` (#8), `6b5b092` (#10) | Claude Code pin 2.1.250 → 2.1.251, `mise.lock` tracked; `6b5b092` is the `base_head` of the 19-file acceptance baseline, which includes `mise.toml` and `mise.lock`. |
| 2026-10-10 | `f9c0ec3` "build: isolate lightweight development checks" (backup ref `backup/d178-pre-rewrite/codex/marketplace-native-onboarding`) | `mise.dev.toml` (two tasks, no tools: "The root mise.toml remains the Linux OCI definition. These checks use existing executables; this configuration installs no tools") and `dev/mise` created. Plan unit N3: "Separate development commands; No install/bootstrap; lightweight checks; OCI bytes preserved" (`P/task_plan.md:992`). |
| 2026-10-12 | `93bb798` "Add locked GitHubKit research workflow and guarded delivery" | `mise.dev.lock`, `dev/bootstrap.py` (with the `OCI_FILES` guard), `dev/empty-mise.toml` and 148 lines of tasks added; "Preserve the original marketplace acceptance files". |
| 2026-10-14 | `48d0260` (D143, D148) | History replaced by a scrubbed baseline; `git log --follow` on both files now starts here, so the earlier commits above were read from the backup refs. Later commits add tasks and betterleaks (`04fd683`) to `mise.dev.toml`. |
| 2026-10-14 | D6 (DL-10), D64 (DL-68), D173 (DL-224) | CT-08 may re-record the baseline after deliberate changes (D64); two transitions: v2 is CT-08, v3 carries R21 batch 4 and the acceptance runner pin (D173). |
| 2026-10-14 | D122 (DL-154) | Python's source of truth is "its own `mise.dev.toml` pin (3.15)", and "the project builds without global mise configuration". |
| 2026-10-14 | D188 (DL-241) | This request; the image-pin bump (CT-08 batch 4) waits for it. |

No decision record states "two files" as a goal; the split follows from three standing rules: preserve the
19 baseline files (`AGENTS.md`, "Preserve"), never install the image's tools for development or linting
(`AGENTS.md`, "Gotchas"; `docs/agents/claude-takeover.md:59`), and build without global mise config (D122;
`docs/accepted-decisions.md:27-28`).

### 7.2 What each file does today

| | `mise.toml` + `mise.lock` | `mise.dev.toml` + `mise.dev.lock` |
| --- | --- | --- |
| Read by | plain `mise` in the repo root; `jdx/mise-action` in `acceptance.yml:14-16` (without the `install: false` that `research-fast.yml:21-26` sets to keep this file from being installed) and `mise oci build` (`:25`) | only `./dev/mise` (`dev/mise:14-21`), which also isolates global config, the data dir (`.mise/`), hooks and auto-install |
| Tools | `npm:@anthropic-ai/claude-code` 2.1.251 with `allow_builds`, node 26.8.1, github-cli 2.98.0, uv 0.12.7, jq 1.8.2 (`mise.toml:10-14`) | python 3.15.0, uv 0.13.0, `aqua:betterleaks/betterleaks` 1.9.0 (`mise.dev.toml:5-8`) |
| Other sections | `[oci]` base digest (`:20-26`), `[bootstrap.packages]` four apt pins (`:31-50`), `[settings] pin = true` | `min_version = "2026.10.8"`, `[deps.uv]`, 68 tasks (`mise.dev.toml:3, 13-413`) |
| Lock | `lockfile_version = 1`; the npm row has no URL or checksum (`mise.lock:132-138`) | `lockfile_version = 3`, three platforms, URL, checksum and provenance per tool (`mise.dev.lock`) |
| Guard | frozen baseline (`check:acceptance-baseline`) | `deps:check` (`dev/bootstrap.py` `verify_tool_lock`) |
| Who else | `ci/acceptance.sh` runs inside the image | hk hooks (`hk.pkl` steps call `./dev/mise run …`); `research-fast.yml:21-50`; `dev/check.py:72` |

A third file, `plugins/aggregated-research/mise.toml`, is the plugin's own consumer-facing config (baseline
file, confined by `bin/mise-env`); it is out of scope and stays.

### 7.3 mise's own model, at the host's mise 2026.10.10 and the repo's `min_version` 2026.10.8

- Config environments add files on top of `mise.toml`; they never replace it. `-E dev` or `MISE_ENV=dev` loads
  `mise.toml` and `mise.dev.toml`, the environment file winning per key in the same directory
  (`OR/pages/mise.jdx.dev_configuration_environments.html.md:6, 94-97`). Since 2026.10.5, `mise.local.toml`
  outranks `mise.<env>.toml` (jdx/mise#14388, closed 2026-10-13, Q74). `.miserc.toml` can make an environment
  the default (`env = ["dev"]`).
- `override_config_filenames` (`MISE_OVERRIDE_CONFIG_FILENAMES`) replaces the base names; environment files
  still load (`…environments.html.md:109`). It is a miserc setting, read before any `mise.toml`
  (`OR/pages/mise.jdx.dev_configuration_settings.html.md:2878-2890`). MP's wrapper uses it to read only
  `mise.dev.toml`, and unsets `MISE_ENV` so no environment file joins.
- Locks follow the config file: `mise.toml` → `mise.lock`, `mise.dev.toml` → `mise.dev.lock`; with
  `MISE_ENV=dev`, `mise lock` writes the base tools to `mise.lock` and the environment's tools to
  `mise.dev.lock`, each strictly scoped (`OR/pages/mise.jdx.dev_dev-tools_mise-lock.html.md:130`; jdx/mise#8523,
  merged 2026-03-09, Q68). MP gets `mise.dev.lock` because the override makes `mise.dev.toml` the config file,
  not because an environment is active.
- Tasks: `[tasks.*]` cannot come from `include`d files; share them with `task_config.includes`
  (`OR/pages/mise.jdx.dev_configuration.html.md:529-532`), which is D7's pending spike (DL-11).
- `include = [...]` merges `[tools]`, `[env]`, `[bootstrap]` and a few others, never `[settings]`, `[tasks]`
  or `[oci]`; included tools lock into the including file's lock (`…configuration.html.md:507-532`).
- Tool filters: `os = ["linux"]` per tool (`OR/repos/jdx_mise/docs/dev-tools/index.md:385-404`);
  `enable_tools` / `disable_tools` (`MISE_ENABLE_TOOLS`, `MISE_DISABLE_TOOLS`) as an allowlist or denylist
  (`…settings.html.md:744-755, 937-948`). Both are applied in `Toolset::add_version` and `merge`
  (`src/toolset/mod.rs:104-125, 872-878`).
- Platform environments (`mise.linux.toml`, `mise.macos-arm64.toml`) load automatically only with `auto_env`;
  it is off now, warns from 2026.12.0 and turns on in 2027.6.0 (`…environments.html.md:174-205`). They would
  not separate the image from Linux CI either.
- `mise oci build` packages only project config files (global and home configs excluded), takes tools as
  installed on a Linux build host, and writes `[env]` into the image config
  (`OR/pages/mise.jdx.dev_dev-tools_mise-oci.html.md:18-19, 87, 165`; `src/cli/oci/common.rs:66-131`).

### 7.4 Options for one file, and what each breaks

Columns: frozen baseline (`mise.toml`/`mise.lock` are 2 of the 19 files), OCI image build, `dev/mise`,
`deps:check`, hk, CI.

| Option | Files after | Baseline | OCI build | `dev/mise` | `deps:check` | hk | CI |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A. Status quo, documented | 2 configs, 2 locks | none | none | none | none | none | none |
| B. `MISE_ENV=dev` layering (keep `mise.dev.toml`, drop the override) | 2 + 2 | none | none | must drop `MISE_OVERRIDE_CONFIG_FILENAMES`; dev then loads the image's npm Claude Code, node, gh, jq and `mise.lock` (Q94) | `verify_tool_lock` refuses the extra tools | none | `tools:prepare` would install the image tools on every CI run |
| C. Inverted environments: dev in `mise.toml`, image extras in `mise.oci.toml`, built with `-E oci` | 2 + 2 | transition (both renamed or rewritten) | image gets dev tools unless filtered with `enable_tools` | override to `mise.toml`; trust path | rewrite to the new names | none | `acceptance.yml` build step gains `-E oci` |
| D. Image file moved to `ci/oci/mise.toml`, built from there with `MISE_CEILING_PATHS` set to the repo root | 2 + 2 | transition (paths change) | parent configs load unless the ceiling excludes the root (`…configuration.html.md:71`) | default name, no override | rewrite | none | build step `cd ci/oci` |
| **E. One `mise.toml` + `mise.lock`, image tools `os = ["linux"]`, image built with `MISE_ENABLE_TOOLS`** | **1 + 1** | **v3 transition; afterwards every dev-tool bump touches a baseline file unless v3 re-scopes the frozen set** | **same `[oci]` and apt layers; toolset narrowed by `enable_tools` (source-read, unmeasured on Linux)** | **override set to `mise.toml` (keeps `mise.local.toml` and `.mise.toml` out), trust path `mise.toml`** | **`bootstrap.py`: config and lock names, 7-tool backend map, inline-table versions, `OCI_FILES` guard removed** | **none (`hk.pkl` calls `./dev/mise`)** | **`tools:prepare` installs Claude Code, node, gh, jq on Linux runners (Claude Code: 118 MB download, 267 MB unpacked); smoke step reads the new key** |
| F. E without `os` filters (one toolset everywhere) | 1 + 1 | as E | as E | as E | as E | none | as E; macOS dev also installs Claude Code (250 MB binary in each checkout's `.mise`) and shadows the host's native `claude` inside tasks |
| G. E with tasks split into `mise/tasks/*.toml` (`task_config.includes`) | 1 config + task files | as E | as E | as E | as E | none | as E; waits for the D7 spike |

Only E, F and G reach one config file; B, C and D keep two and differ only in which name mise treats as the
default. E is the smallest change that keeps today's macOS behaviour (measured: macOS toolset stays python,
uv, betterleaks, Q99).

### 7.5 Recommended design (E) and migration sketch

Draft config: `OR/draft/mise.os-linux.toml` (header, settings and tools below; tasks copied unchanged from
`mise.dev.toml:19-413`; `[oci]` and `[bootstrap.packages]` copied unchanged from `mise.toml:20-50`), lock
`OR/draft/mise.os-linux.lock`.

```toml
min_version = "2026.10.8"

[settings]
experimental = true
pin = true
minimum_release_age = "1h"   # R-166; exact and locked versions are never filtered

[tools]
python = "3.15.0"
uv = "0.13.0"                # one uv for dev and image (image moves from 0.12.7, R21 batch 4)
"aqua:betterleaks/betterleaks" = "1.9.0"
"github:anthropics/claude-code" = { version = "2.1.300", os = ["linux"] }
node = { version = "26.8.1", os = ["linux"] }
github-cli = { version = "2.98.0", os = ["linux"] }
jq = { version = "1.8.2", os = ["linux"] }

[env]
DISABLE_UPDATES = "1"        # pinned binaries never self-update; baked into the image config too

[tasks."oci:build"]
description = "Build the Linux acceptance image from this file's image toolset (Linux host only)"
dir = "{{config_root}}"
env = { MISE_ENABLE_TOOLS = "github:anthropics/claude-code,node,github-cli,uv,jq" }
run = "mise oci build"
```

Migration, as one lane in the v3 baseline transition (D173), one writer in one worktree:

1. Write `mise.toml` from the draft; delete `mise.dev.toml` and `mise.dev.lock`; regenerate `mise.lock` (v3,
   `macos-arm64,linux-arm64,linux-x64`) with `./dev/mise run deps:lock` once step 2 lands.
2. `dev/mise`: `MISE_OVERRIDE_CONFIG_FILENAMES=mise.toml`, `MISE_TRUSTED_CONFIG_PATHS=$project_root/mise.toml`.
   `dev/bootstrap.py`: `DEV_CONFIG`/`DEV_LOCK` → `mise.toml`/`mise.lock` (`:18-19`); `TOOL_BACKENDS` gains
   `github:anthropics/claude-code`, `core:node`, `aqua:cli/cli`, `aqua:jqlang/jq` (`:22-23`); read `version`
   from inline tables in `verify_tool_lock`; drop `OCI_FILES` and its digest guard (`:21, 188, 224-226`);
   update `self_test` (`:119-120`). Existing Python takes fixes only (ADR 0008), and these are fixes.
3. References: `dev/git_delivery.py:27, 509`, `dev/issue_amend.py:39-41`, `dev/check.py:72`,
   `dev/test_git_delivery.py`, `dev/test_hooks.py`, `AGENTS.md` ("Gotchas"), `docs/onboarding.md:26-50`,
   `docs/agents/claude-takeover.md:59`, `docs/accepted-decisions.md:27`, `dev/AGENTS.md:9, 20, 28`,
   `CODING_STANDARDS.md:4`, `.claude/rules/dev-tests.md`, `.claude/agents/{frontier-scheduler,retro-writer}.md`,
   and both ticket-frontier skill copies (67 references in 18 files, `git grep`).
4. Workflows: `acceptance.yml` (baseline file) builds with `sudo -E env MISE_ENABLE_TOOLS=… mise oci build`
   (or the task) and its smoke step reads the pin from the new key instead of grepping the npm key
   (`:31-35`); `research-fast.yml:21-22` loses its "must not be bootstrapped" comment. D173 already puts the
   acceptance runner pin and R21 batch 3's `mise-action` move in the same window.
5. Baseline: new versioned record in `evidence/onboarding/baseline-files.json`;
   `check:acceptance-baseline` fails on the edited tree before the record and passes after it.
6. Checks from that worktree: `./dev/mise tasks validate`, `./dev/mise run check`,
   `./dev/mise run check:acceptance-baseline`, `./dev/mise run check:research`, `./dev/mise run deps:check`,
   `./dev/mise run test:hooks`. Separately admitted: a Linux `mise oci build`, the in-image `claude --version`
   smoke step and `ci/acceptance.sh`.
7. Renovate (D162): a `packageRules` entry for `github:anthropics/claude-code` with `minimumReleaseAge`
   "1 hour", and the first PR checks whether the hosted app refreshes `mise.lock` (R22's open item).

### 7.6 Ways to install Claude Code in CI, compared

| Route | Pin | Integrity | Fits MP? | Evidence |
| --- | --- | --- | --- | --- |
| `curl -fsSL https://claude.ai/install.sh \| bash -s 2.1.300` | exact version or `stable`/`latest` | script fetches the `latest` binary, checks its SHA-256 against `manifest.json`, then runs `<latest> install 2.1.300`; no GPG check; Linux binaries are not code-signed | weak: two binaries per install, fails open (#1817, #1242), puts the launcher under `~/.local/bin` | `OR/pages/claude.ai_install.sh.md:6, 148-167, 226`; `OR/pages/code.claude.com_docs_en_setup.md.md:332-350, 476-535` |
| `claude install <version>` | exact | as above (the script's second half) | needs a `claude` already present | `install.sh:226` |
| Signed apt repository `downloads.claude.ai/claude-code/apt/{stable,latest}` | apt version | apt verifies the repository key `31DD…CACE` | not in the OCI build (no `[bootstrap.apt.sources]` there); an extra apt source on runners | `setup.md.md:354-399`; `src/oci/` |
| npm `@anthropic-ai/claude-code` (today) | exact | npm registry; per-platform optional package; needs `allow_builds` and node | works, but the lock row has no checksum and the binary arrives by postinstall | `mise.toml:6-10`; `setup.md.md:446-458`; `mise.lock:132-138` |
| `anthropics/claude-code-action@<sha>` | the action's hard-coded version (v1.0.250 = 2.1.300, v1.0.249 = 2.1.299, v1.0.248 = 2.1.296) | runs `install.sh` with that version and retries 3 times | only for review or agent workflows; can take `path_to_claude_code_executable` | `OR/repos/anthropics_claude-code-action/src/entrypoints/run.ts:49-118`; `base-action/action.yml:150-158`; `action.yml:144-147` |
| mise registry `claude` → `aqua:anthropics/claude-code` | exact | URL and SHA-256 from `SHASUMS256.txt` in `mise.lock`; no provenance | works; aqua's version expressions were hit by a static-musl parser bug in mise 2026.10.9-10 (#14449; fix #14450 merged 2026-10-14T18:44Z, after 2026.10.10; MP's CI pins 2026.10.8) | `OR/local/claude-aqua.mise.lock`; registry `claude.toml`; Q75 |
| **mise `github:anthropics/claude-code`** | **exact** | **URL, SHA-256 and verified GitHub artifact attestation per platform in `mise.lock`** | **recommended** | `OR/local/claude-github.mise.lock`, Q97 |
| mise `http:claude` (registry fallback) | exact | SHA-256 from the per-version `manifest.json` | Windows fallback; no cooldown default for `http` | registry `claude.toml` |

GitHub release assets exist from 2.1.118 on, by the aqua registry's version overrides: it switches to `github_release` with
`SHASUMS256.txt` for every version after 2.1.117 (except 2.1.126), and the last 40 releases all carry ten
assets including `SHASUMS256.txt` (Q31, Q54).

### 7.7 Integrity, measured

- Host native binary 2.1.300: SHA-256 `475517caa611…5e2d3` (Q102) = `manifest.json`
  `platforms.darwin-arm64.checksum` (Q27) = binary inside `claude-darwin-arm64.tar.gz` from the v2.1.300
  GitHub release (Q100). The GitHub tarball's own digest `c18b0721…3751` matches `SHASUMS256.txt`, the asset
  `digest` field (Q52) and the mise lock (Q96, Q97).
- GPG: `SHASUMS256.txt.sig` and `manifest.json.sig` both report "Good signature from Anthropic Claude Code
  Release Signing" with key `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`, the fingerprint the docs publish
  (`OR/local/gpg-and-binary-identity.txt`; `setup.md.md:489-521`). Signatures exist from 2.1.89 on.
- GitHub attestation: one in-toto release attestation (v0.2) covers all ten assets (Q55); mise's `github:`
  backend verifies it and records `provenance = "github-attestations"`; the `aqua:` route records none
  (Q96, Q97). Neither mise route checks the GPG signature; a CI job that wants it can run `gpg --verify` on
  `SHASUMS256.txt` before `mise install` (UNVERIFIED as a task; not built).
- Lock cost: after the scratch `mise lock` runs, mise's download cache held each locked platform's Claude Code
  tarball (`claude-{darwin-arm64,linux-arm64,linux-x64}.tar.gz`, 108-118 MB each) next to the other tools'
  artifacts (`OR/local/lock-download-cache.txt`): locking downloads the artifacts it verifies, so every
  Renovate lock refresh of this pin moves about 340 MB.
- `manifest.json` 2.1.300 carries `"manifestSignatureEnforcement": "flag"` (Q27); its meaning is not
  documented in the pages read (UNVERIFIED).

### 7.8 Cooldown and minimum release age (R-166)

mise's `minimum_release_age` defaults to 24h for aqua, github, npm, core and other backends, and to none for
`http`; exact and locked versions are never filtered (`…settings.html.md:2294-2319`;
`…mise-lock.html.md:478-481`). It is a project setting (measured `settings get` = `1h` from the draft). At
2026-10-15T00:18Z, `mise latest claude` returned 2.1.296 under the default and 2.1.300 under `1h` (same for
the npm backend; `OR/local/cooldown-latest.txt`, Q95), because 2.1.299 (2026-10-14T02:49Z) and 2.1.300
(18:24Z) were under 24h old (Q54). The cutoff only matters when something resolves a version (`mise latest`,
`mise outdated --bump`, `mise lock --bump`, Renovate); the pinned install never waits. R-166's `1h` therefore
belongs in the one `[settings]` table. `jdx/mise-action` v5 defaults the cooldown to 24h when its `version`
input is unset (R21 finding 4).

### 7.9 Keeping the pin at the latest release automatically (R-167)

- Renovate's mise manager reads `mise.toml`, environment variants and `mise.lock`, resolves registry short
  names (`claude`, `claude-code`) and `github:` tools, and can refresh the lock
  (`OR/pages/docs.renovatebot.com_modules_manager_mise_.md:100-130, 189-216, 300-312, 541-542`). It cannot
  update `aqua:` packages of the `http` package type by their full name, which is what
  `aqua:anthropics/claude-code` is at its top level (`:358`; Q31), so the full aqua name is the wrong key for
  Renovate; the `github:` name avoids that. Lock refresh needs `mise` in `allowedUnsafeExecutions` on a
  self-hosted Renovate; the hosted app's behaviour is contested (R22 section 3, `:219-247`).
- Dependabot has no mise ecosystem (dependabot-core PR #14500 open since 2026-03-20; R22 Q108), so it can only
  move the action SHA, not the mise pin.
- The aqua registry follows Claude Code within hours (aquaproj/aqua-registry PRs #61587 to #62344, Q76), and
  claude-code-action bumped to 2.1.300 three minutes after the release (`a26b07d`, 2026-10-14T18:27Z vs
  release 18:24:25Z, Q29, Q52). Renovate's `minimumReleaseAge` is the only gate between a release and MP.

### 7.10 The image

`mise oci build` adds one layer per installed tool at `/mise/installs/<tool>/<version>/` and writes
`/etc/mise/config.toml` pinning each one (`…mise-oci.html.md:95-104`); there is no step that runs a command
in the image, so `install.sh` and `claude install` cannot run there, and `[bootstrap.packages]` installs from
the base image's own sources only (`src/oci/packages.rs:483-496`; no `apt_sources` reference under `src/oci/`).
With E, the image's Claude Code is the same `github:` tool, built on the runner from `mise.lock`, and
`DISABLE_UPDATES=1` from `[env]` lands in the image config (`:165`). The native binary needs no node; node
stays in the image until the admitted acceptance run shows whether the dependency marketplaces' MCP servers
need it (UNVERIFIED either way). CC#88030 (closed 2026-08-19) confirms `DISABLE_AUTOUPDATER`/`DISABLE_UPDATES`
are the switches that hold a pin; `autoUpdates: false` is not.

### 7.11 Channel

The native `latest` and `stable` pointers read 2.1.300 and 2.1.292 (Q25, Q26), matching npm's dist-tags in the
intake (`upgrade-plan.md:3-5`). `stable` is "typically about one week old, skipping releases with major
regressions" (`setup.md.md:224-225`); 2.1.292 was released 2026-10-06 and 2.1.295 on 2026-10-08 (Q54). The
gates need 2.1.295, the CT-23/CT-31 mod APIs 2.1.299/2.1.300 (`impact.md:7`), so `stable` cannot be the pin
today. Option for later: once `stable` passes the newest version MP needs, a Renovate custom datasource on
`https://downloads.claude.ai/claude-code-releases/stable` could follow it (not built; UNVERIFIED).

## 8. Code examples found

| Repository | Path | Commit or permalink | What it shows |
| --- | --- | --- | --- |
| anthropics/claude-code-action | `src/entrypoints/run.ts:49-118` | `a26b07d8c778` (v1.0.250, 2026-10-14) | `buildInstallCommand` with `set -o pipefail`, hard-coded `claudeCodeVersion = "2.1.300"`, three retries, `PATH_TO_CLAUDE_CODE_EXECUTABLE` short-circuit |
| anthropics/claude-code-action | `base-action/action.yml:150-158` | same | the same pin in the composite base action, `timeout … bash -s -- $CLAUDE_CODE_VERSION` |
| jdx/mise | `registry/claude.toml` | `22717299563d` (v2026.10.10) | `claude` aliases `claude-code`; backends `aqua:anthropics/claude-code` then `http:claude` with `checksum_expr` over `manifest.json` |
| jdx/mise | `src/cli/oci/common.rs:66-146` | same | project-only config files, `ConfigScope::LocalOnly`, toolset built through the filtered builder |
| jdx/mise | `src/toolset/mod.rs:104-125, 872-878` | same | `add_version`/`merge` drop tools that `enable_tools`, `disable_tools` or `os` exclude |
| aquaproj/aqua-registry | `pkgs/anthropics/claude-code/registry.yaml` | `fde48caf03e7` (main) | `github_release` assets `claude-{os}-{arch}.tar.gz`, `SHASUMS256.txt` checksum, raw GCS URLs up to 2.1.117 |
| Anthropic | `https://claude.ai/install.sh` (mirrored) | fetched 2026-10-15T00:0xZ, sha256 in `OR/manifest.json` | bootstrap through `latest`, manifest SHA-256 check, `install ${TARGET}` |

## 9. Routes table

All 103 log rows; the full per-row log with results is in the companion log file.

| seq | stage | route | command shape (no secrets) | rc | hits | used |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | preflight | firecrawl | `firecrawl credits --json` | 0 | - | yes |
| 2 | preflight | serper | `GET https://google.serper.dev/account (X-API-KEY from env)` | 0 | - | yes |
| 3 | preflight | serpapi | `GET https://serpapi.com/account.json (api_key from env)` | 0 | - | yes |
| 4 | preflight | context7 | `GET https://context7.com/api/v2/usage (bearer from env)` | 0 | - | yes |
| 5 | preflight | exa | `no balance endpoint known (research-workflow.md Preflight); first call classified after the fact` | None | - | yes |
| 6 | preflight | last30days | `GET https://api.scrapecreators.com/v1/account/credit-balance (x-api-key from env)` | 0 | - | yes |
| 7 | preflight | gh-issue-search | `gh api rate_limit` | 0 | - | yes |
| 8 | preflight | webclaw | `command -v webclaw (local binary 0.6.23 via mise github backend)` | 0 | - | yes |
| 9 | 1 | exa | `mise environments mise.<env>.toml MISE_ENV config layering lock file mise.<env>.lock` | 0 | 0 | yes |
| 10 | 1 | context7 | `ctx7 library mise environments MISE_ENV lock file` | 0 | 5 | yes |
| 11 | 1 | context7 | `ctx7 docs /jdx/mise config environments MISE_ENV mise.dev.toml mise.dev.lock lockfile per environment` | 0 | 5 | yes |
| 12 | 1 | context7 | `ctx7 docs /jdx/mise mise oci build [oci] section which config files tools os filter MISE_OVERRIDE_CONFIG_FILENAMES` | 0 | 9 | yes |
| 13 | 1 | context7 | `ctx7 docs /websites/code_claude native install script specific version install.sh stable latest claude install command checksum verification` | 0 | 5 | yes |
| 14 | 1 | webclaw | `https://code.claude.com/docs/en/setup.md` | 0 | 1 | yes |
| 15 | 1 | webclaw | `https://code.claude.com/docs/en/github-actions.md` | 0 | 1 | yes |
| 16 | 1 | webclaw | `https://code.claude.com/docs/en/troubleshoot-install.md` | 0 | 1 | no |
| 17 | 1 | webclaw | `https://mise.jdx.dev/configuration/environments.html` | 0 | 1 | yes |
| 18 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/mise-lock.html` | 0 | 1 | yes |
| 19 | 1 | webclaw | `https://mise.jdx.dev/configuration.html` | 0 | 1 | yes |
| 20 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/mise-oci.html` | 0 | 1 | yes |
| 21 | 1 | webclaw | `https://claude.ai/install.sh` | 0 | 1 | yes |
| 22 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/latest` | 2 | 0 | no |
| 23 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/stable` | 2 | 0 | no |
| 24 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json` | 2 | 0 | no |
| 25 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/latest` | 0 | 1 | yes |
| 26 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/stable` | 0 | 1 | yes |
| 27 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json` | 0 | 1 | yes |
| 28 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.292/manifest.json` | 0 | 1 | yes |
| 29 | 1 | git-clone | `git clone --filter=blob:none https://github.com/anthropics/claude-code-action.git` | 0 | 1 | yes |
| 30 | 1 | git-clone | `git clone --filter=blob:none --branch v2026.10.10 https://github.com/jdx/mise.git` | 0 | 1 | yes |
| 31 | 1 | webclaw | `https://raw.githubusercontent.com/aquaproj/aqua-registry/main/pkgs/anthropics/claude-code/registry.yaml` | 0 | 1 | yes |
| 32 | 1 | serper | `mise "mise.dev.toml" MISE_ENV dev tools CI separate config` | 0 | 6 | yes |
| 33 | 1 | serper | `claude code CI github actions pin version native installer "install.sh" "bash -s"` | 0 | 8 | yes |
| 34 | 1 | serper | `mise "aqua:anthropics/claude-code" OR "claude-code" mise.toml native binary` | 0 | 7 | yes |
| 35 | 1 | serper | `mise minimum_release_age setting npm aqua cooldown 24h "minimum_release_age"` | 0 | 1 | yes |
| 36 | 1 | serper | `renovate mise manager "mise.toml" aqua backend claude-code minimumReleaseAge` | 0 | 3 | no |
| 37 | 1 | serper | `"mise oci build" MISE_ENV environment config files image` | 0 | 8 | yes |
| 38 | 1 | serpapi | `claude code github release assets "SHASUMS256.txt" claude-linux-x64.tar.gz` | 0 | 9 | no |
| 39 | 1 | webclaw | `https://mise.jdx.dev/configuration/settings.html` | 0 | 1 | yes |
| 40 | 1 | webclaw | `https://mise-tools.jdx.dev/tools/claude-code` | 0 | 1 | no |
| 41 | 1 | webclaw | `https://mise.jdx.dev/tasks/task-configuration.html` | 0 | 1 | no |
| 42 | 1 | webclaw | `https://docs.renovatebot.com/modules/manager/mise/` | 0 | 1 | yes |
| 43 | 1 | webclaw | `https://docs.renovatebot.com/configuration-options/` | 0 | 1 | no |
| 44 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/backends/aqua.html` | 0 | 1 | no |
| 45 | 1 | webclaw | `https://mise.jdx.dev/dev-tools/backends/http.html` | 0 | 1 | no |
| 46 | 1 | last30days | `topic "Claude Code in CI pinned version native installer and mise" --plan OR/local/last30days/plan.json (3 subqueries: Claude Code CI pin na` | 0 | 7 | no |
| 47 | 2 | gh-repo-features | `gh api repos/anthropics/claude-code --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | 0 | 1 | yes |
| 48 | 2 | gh-repo-features | `gh api repos/anthropics/claude-code-action --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | 0 | 1 | yes |
| 49 | 2 | gh-repo-features | `gh api repos/jdx/mise --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | 0 | 1 | yes |
| 50 | 2 | gh-repo-features | `gh api repos/renovatebot/renovate --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | 0 | 1 | yes |
| 51 | 2 | gh-repo-features | `gh api repos/aquaproj/aqua-registry --jq {full_name,has_issues,has_discussions,has_pull_requests,archived}` | 0 | 1 | yes |
| 52 | 2 | gh-api | `gh api repos/anthropics/claude-code/releases/tags/v2.1.300 --jq {tag_name,published_at,html_url,assets:[.assets[]\|{name,size,browser_downlo` | 0 | 10 | yes |
| 53 | 2 | gh-api | `gh api repos/anthropics/claude-code/attestations/sha256:11e459c4368a48554d5aa5eabf7f6d84a2ff7ae2f7210795394f60ded6633f56 --jq {n:(.attestati` | 0 | 1 | yes |
| 54 | 2 | gh-api | `gh api repos/anthropics/claude-code/releases?per_page=40 --jq [.[]\|{tag_name,published_at,n_assets:(.assets\|length),has_sums:([.assets[].n` | 0 | 40 | yes |
| 55 | 2 | gh-api | `gh api repos/anthropics/claude-code/attestations/sha256:11e459c4368a48554d5aa5eabf7f6d84a2ff7ae2f7210795394f60ded6633f56 --jq .attestations[` | 0 | 1 | yes |
| 56 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 7329) { title url createdAt body comments(first:` | 0 | 1 | yes |
| 57 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 13809) { title url createdAt body comments(first` | 0 | 1 | yes |
| 58 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { repository(owner: "jdx", name: "mise") { discussion(number: 5058) { title url createdAt body comments(first:` | 0 | 1 | yes |
| 59 | 2 | gh-issue-view | `gh issue view 1817 -R anthropics/claude-code-action --json number,title,state,createdAt,closedAt,body,comments,url` | 0 | 1 | yes |
| 60 | 2 | gh-issue-search | `gh search issues install.sh specific version --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 0 | 0 | no |
| 61 | 2 | gh-issue-search | `gh search issues SHASUMS256 --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 0 | 2 | no |
| 62 | 2 | gh-issue-search | `gh search issues mise install claude --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 0 | 10 | no |
| 63 | 2 | gh-issue-search | `gh search issues DISABLE_AUTOUPDATER CI container --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 0 | 0 | no |
| 64 | 2 | gh-issue-search | `gh search issues native installer version pin --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 0 | 1 | yes |
| 65 | 2 | gh-issue-search | `gh search issues auto-update mise --repo anthropics/claude-code --limit 10 --json number,title,state,createdAt,url` | 0 | 0 | no |
| 66 | 2 | gh-issue-view | `gh issue view 89609 -R anthropics/claude-code --json number,title,state,createdAt,closedAt,body,url` | 0 | 1 | no |
| 67 | 2 | gh-issue-view | `gh issue view 88030 -R anthropics/claude-code --json number,title,state,createdAt,closedAt,body,comments,url` | 0 | 1 | yes |
| 68 | 2 | gh-pr-view | `gh pr view 8523 -R jdx/mise --json number,title,state,mergedAt,url,body` | 0 | 1 | yes |
| 69 | 2 | gh-pr-view | `gh pr view 7842 -R jdx/mise --json number,title,state,mergedAt,url,body` | 0 | 1 | yes |
| 70 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:jdx/mise enable_tools oci", type: DISCUSSION, first: 10) { discussionCount nodes { ... o` | 0 | 1 | no |
| 71 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:jdx/mise override_config_filenames", type: DISCUSSION, first: 10) { discussionCount node` | 0 | 7 | no |
| 72 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:jdx/mise claude-code aqua", type: DISCUSSION, first: 10) { discussionCount nodes { ... o` | 0 | 113 | no |
| 73 | 2 | gh-issue-search | `gh search issues claude --repo jdx/mise --limit 15 --json number,title,state,createdAt,url --sort created` | 0 | 15 | yes |
| 74 | 2 | gh-issue-view | `gh issue view 14388 -R jdx/mise --json number,title,state,createdAt,closedAt,body,comments,url` | 0 | 1 | yes |
| 75 | 2 | gh-issue-view | `gh issue view 14449 -R jdx/mise --json number,title,state,createdAt,closedAt,body,comments,url` | 0 | 1 | yes |
| 76 | 2 | gh-pr-search | `gh search prs anthropics/claude-code --repo aquaproj/aqua-registry --limit 10 --json number,title,state,createdAt,url` | 0 | 10 | yes |
| 77 | 2 | gh-issue-search | `gh search issues mise claude --repo renovatebot/renovate --limit 10 --json number,title,state,createdAt,url` | 0 | 0 | no |
| 78 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:renovatebot/renovate mise github backend", type: DISCUSSION, first: 10) { discussionCoun` | 0 | 1 | no |
| 79 | 2 | gh-issue-search | `gh search issues claude code version pin --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,url` | 0 | 0 | no |
| 80 | 2 | gh-graphql-discussion | `gh api graphql -f query=query { search(query: "repo:anthropics/claude-code-action claude code version", type: DISCUSSION, first: 10) { discu` | 0 | 9 | no |
| 81 | 2 | gh-issue-search | `gh search issues path_to_claude_code_executable --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,url` | 0 | 10 | no |
| 82 | 2 | gh-issue-search | `gh search issues install.sh failed --repo anthropics/claude-code-action --limit 10 --json number,title,state,createdAt,url` | 0 | 1 | yes |
| 83 | 2 | gh-issue-view | `gh issue view 1242 -R anthropics/claude-code-action --json number,title,state,createdAt,closedAt,body,url` | 0 | 1 | yes |
| 84 | 2 | gh-code-search-saved | `gh api search/code?q=%22claudeCodeVersion%20%3D%22%20repo%3Aanthropics/claude-code-action&per_page=5 --jq {total_count, items:[.items[]\|{na` | 0 | 1 | yes |
| 85 | 2 | gh-code-search-saved | `gh api search/code?q=README%20repo%3Aanthropics/claude-code-action&per_page=5 --jq {total_count, items:[.items[]\|{name:.path,html_url}]}` | 0 | 11 | yes |
| 86 | 2 | gh-code-search-saved | `gh api search/code?q=%22anthropics/claude-code%22%20path%3Aregistry%20repo%3Ajdx/mise&per_page=5 --jq {total_count, items:[.items[]\|{name:.` | 0 | 1 | yes |
| 87 | 2 | gh-code-search-saved | `gh api search/code?q=README%20repo%3Ajdx/mise&per_page=5 --jq {total_count, items:[.items[]\|{name:.path,html_url}]}` | 0 | 93 | yes |
| 88 | 2 | gh-code-search-saved | `gh api search/code?q=%22SHASUMS256.txt%22%20path%3Apkgs/anthropics/claude-code%20repo%3Aaquaproj/aqua-registry&per_page=5 --jq {total_count,` | 0 | 1 | yes |
| 89 | 2 | gh-code-search-saved | `gh api search/code?q=README%20repo%3Aaquaproj/aqua-registry&per_page=5 --jq {total_count, items:[.items[]\|{name:.path,html_url}]}` | 0 | 2 | yes |
| 90 | 2 | gh-code-search-saved | `gh api search/code?q=%22enable_tools%22%20path%3Asrc/toolset%20repo%3Ajdx/mise&per_page=5 --jq {total_count, items:[.items[]\|{name:.path,ht` | 0 | 2 | yes |
| 91 | 2 | gh-code-search-saved | `gh api search/code?q=README%20repo%3Ajdx/mise&per_page=5 --jq {total_count, items:[.items[]\|{name:.path,html_url}]}` | 0 | 93 | yes |
| 92 | 1 | webclaw | `https://downloads.claude.ai/keys/claude-code.asc` | 0 | 1 | yes |
| 93 | 1 | webclaw | `https://downloads.claude.ai/claude-code-releases/2.1.300/manifest.json.sig` | 0 | 1 | yes |
| 94 | local | mise-local | `bin/miso config ls \| ls --json, plain vs -E dev vs MISE_OVERRIDE_CONFIG_FILENAMES=mise.dev.toml, on scratch copies of MP mise.toml, mise.lo` | 0 | 3 | yes |
| 95 | local | mise-local | `mise latest claude and npm:@anthropic-ai/claude-code under default, MISE_MINIMUM_RELEASE_AGE=1h and 0s (scratch exp/claude, fx profile for G` | 0 | 5 | yes |
| 96 | local | mise-local | `mise tool claude; mise lock --platform linux-x64,linux-arm64,macos-arm64 with [tools] claude = "2.1.300" (scratch exp/claude)` | 0 | 3 | yes |
| 97 | local | mise-local | `mise lock --platform linux-x64,macos-arm64 with [tools] "github:anthropics/claude-code" = "2.1.300" (scratch exp/claude-gh)` | 0 | 2 | yes |
| 98 | local | mise-local | `draft unified mise.toml (OR/draft/mise.toml): config ls, tasks validate, ls with MISE_ENABLE_TOOLS and MISE_DISABLE_TOOLS; mise lock for 3 p` | 0 | 69 | yes |
| 99 | local | mise-local | `draft with os = ["linux"] on claude, node, github-cli, jq (OR/draft/mise.os-linux.toml): ls on macOS, lock for 3 platforms` | 0 | 3 | yes |
| 100 | local | gh-release-download | `gh release download v2.1.300 -R anthropics/claude-code -p claude-darwin-arm64.tar.gz -p SHASUMS256.txt -p SHASUMS256.txt.sig; tar -x; shasum` | 0 | 3 | yes |
| 101 | local | gpg-local | `scratch GNUPGHOME: import https://downloads.claude.ai/keys/claude-code.asc; gpg --verify SHASUMS256.txt.sig SHASUMS256.txt; gpg --verify man` | 0 | 2 | yes |
| 102 | local | local-read | `shasum -a 256 ~/.local/share/claude/versions/2.1.300` | 0 | 1 | yes |
| 103 | 2 | gh-pr-view | `gh pr view 14450 -R jdx/mise --json number,title,state,mergedAt,url` | 0 | 1 | yes |

## 10. Proposed saved-search rows

Shape of the rows in `dev/saved-searches.toml`; each was run once with its control (section 5). Not added to
the file.

```toml
# Claude Code pin sources (research R24, request R-180, 2026-10-14)
[[search]]
id = "cca-claude-code-version"
query = "\"claudeCodeVersion =\""
repo = "anthropics/claude-code-action"       # 1 hit (src/entrypoints/run.ts); control README 11
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "mise-registry-claude-backends"
query = "\"anthropics/claude-code\" path:registry"
repo = "jdx/mise"                            # 1 hit (registry/claude.toml); control README 93
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "aqua-claude-code-checksums"
query = "\"SHASUMS256.txt\" path:pkgs/anthropics/claude-code"
repo = "aquaproj/aqua-registry"              # 1 hit; control README 2
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "mise-tool-filters"
query = "\"enable_tools\" path:src/toolset"
repo = "jdx/mise"                            # 2 hits (mod.rs, tool_request_set.rs); control README 93
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

A hit change in the first row means the action moved its Claude Code pin; in the second, mise changed the
backend order for `claude`; in the fourth, the filter path the image build relies on moved.

## 11. Open gaps

1. No Linux `mise oci build` ran (needs a Linux host and an admission), so the image honouring
   `MISE_ENABLE_TOOLS` and `os` is read from source, not measured; no tool was installed, so the `github:`
   install of the tarball's `claude` (bin detection, PATH in the image) is unmeasured.
2. User decisions: (U1) adopt design E; (U2) whether v3 keeps `mise.toml`/`mise.lock` in the frozen set, which
   makes every dev-tool bump a baseline change, or re-scopes it; (U3) `os = ["linux"]` (E) or one toolset on
   macOS too (F); (U4) `github:` (attestations) or the registry short name `claude` (aqua, no provenance) as the
   pin key.
3. Whether Renovate's mise manager parses the inline-table form `{ version = …, os = [...] }` and the hosted
   app refreshes a v3 `mise.lock` (UNVERIFIED; R22's first-PR check).
4. Whether node is still needed in the image once Claude Code is native (acceptance run decides).
5. The meaning of `manifestSignatureEnforcement: "flag"` in `manifest.json` (undocumented in pages read).
6. Exa (402 `NO_MORE_CREDITS`, Q9), Firecrawl (-128) and ScrapeCreators (-7) had no credits; Context7 has
   16 requests left until 2026-11-01. Last30Days returned nothing on topic (Q46). The Google corpus (Serper,
   SerpApi) and GitHub carried the web stage, so the two-upstream rule rests on Context7 plus Google plus the
   primary sources (mise docs and source, Anthropic docs, scripts and release assets).
7. `mise` 2026.10.9 and .10 static-musl builds fail aqua version expressions (#14449); MP's CI pins 2026.10.8
   and the host runs the macOS build, so nothing here hit it; the fix (#14450, merged 2026-10-14T18:44Z, Q103)
   is not in 2026.10.10, which argues against `aqua:` for Claude Code until a release carries it.
