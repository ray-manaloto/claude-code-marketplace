# R16: provider credit preflight and status codes (research, 2026-10-14)

Written by research agent R16 of session `ccm-20261014` (`ce9c0b3d`), read-only except this file and the
untracked mirror `offline/research/R16-provider-preflight/` (called OR below; `OR/manifest.json` lists every
mirrored item with source URL, local path, UTC time, command shape, exit code and SHA-256 or commit, and
`OR/queries.jsonl` holds all 167 logged calls with `status` and `failure_code`). MP = the repository root,
branch `codex/marketplace-native-onboarding`. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.
TR = the read-only private project `<TR>` (read, never run).
"Parent probe 2026-10-14" cites the evidence the parent gathered before this run. Every provider call ran under
the `codex_research` fnox profile; keys were passed through the environment or a header read from it and never
written anywhere (a scan of every mirrored file for 10 key values found 0 hits, `OR/manifest.json`
`secret_scan`). This run followed `docs/agents/research-workflow.md` "Preflight (D142)" itself: 9 providers
were checked before stage 1, Firecrawl, Context7 and ScrapeCreators were skipped with their codes, and every
stage-2 repository was feature-checked before its issue, PR or discussion search.

## 1. Verdict

Recommendation: build `rsm-core research preflight` as three small C++ units over two new D83 schema files,
with a per-provider check that reads an account API wherever one exists and classifies the first real call
where none does:

| Provider | Check (preferred route) | Cost of the check | Live result 2026-10-14 |
|---|---|---|---|
| Firecrawl | `GET https://api.firecrawl.dev/v2/team/credit-usage` (SDK `get_credit_usage()` / `getCreditUsage()`; CLI `firecrawl credits --json`) | free, own `account` rate bucket | SKIPPED, CREDITS_EXHAUSTED (-128 of 1000) |
| Context7 | `GET https://context7.com/api/v2/usage` (no SDK method; `ctx7 whoami` proves nothing) | not a search or docs request (inferred) | SKIPPED, CREDITS_EXHAUSTED (1000 of 1000, resets 2026-11-01) |
| Exa | none for a standard key; classify the first call (402 tags), record `costDollars` | n/a | OK, credit check unavailable |
| Serper | `GET https://google.serper.dev/account` (undocumented; no SDK) | free (measured) | OK (balance 1313, then 1307 after 6 searches) |
| SerpApi | `GET https://serpapi.com/account.json` (SDK `Client.account()`) | free (measured) | OK (245 of 250) |
| ScrapeCreators | `GET https://api.scrapecreators.com/v1/account/credit-balance` | not billed at a negative balance (measured) | SKIPPED, CREDITS_EXHAUSTED (-7) |
| Last30Days | `--diagnose` (key presence only) plus the ScrapeCreators check | free | DEGRADED, CREDITS_EXHAUSTED (ScrapeCreators sources dead) |
| GitHub REST and GraphQL | `GET /rate_limit` (githubkit `rest.rate_limit.get()`, `gh api rate_limit`), then `x-ratelimit-*` headers on every call | free against the primary limit | OK (search 30/30, code_search 10/10, graphql 4998) |
| webclaw | local binary present; cloud key absent | free | OK, unmetered locally; cloud NOT_CONFIGURED |

Status model: port TR's `ProviderFetchStatus` and `ResearchFailureCode` unchanged, move `FEATURE_DISABLED` in
from TR's `ErrorCode`, add `RATE_LIMITED` and `NOT_CONFIGURED`, and port TR's `ServiceCreditStatus` as a
separate `credit.state` field next to a new `CreditCheckMethod`. Proposed files:
`schemas/research/provider-status.json` (enums and shared records) and `schemas/research/preflight.json`
(request and result), drafted and metaschema-checked in `OR/draft/`.

Confidence: high for Firecrawl, Context7, Serper, SerpApi, ScrapeCreators and GitHub (live probes agree with
docs and SDK code); medium for Exa (no balance API, the 402 tags are from docs, not observed); medium for the
C++ unit plan (nothing compiled; it waits on the `rsm-core` skeleton, the D135 and D140 probes and R15).

The evidence that decides it:

1. 429 means different things per provider, so TR's mapping of every 429 to `CREDITS_EXHAUSTED`
   (TR `src/research_aggregator/sources/exa.py:108-113`, `firecrawl.py:114-119`, `context7.py:220-224`,
   `github.py:67-68`) is wrong in both directions. Context7 answers an exhausted free quota with 429
   `{"error":"Quota Exceeded"}`, `RateLimit-Remaining: 0` and `Retry-After: 1497985` (17 days; canary seq 49,
   `OR/probe/canary-ctx7-search.*`); SerpApi uses 429 for both hourly throughput and "Your account has run out
   of searches." (`OR/pages/serpapi-status-errors.md:15, 51-66`; serpapi/serpapi-python#16, maintainer reply
   2024-08-26); Exa separates them (402 `NO_MORE_CREDITS`, 429 `RATE_LIMIT_EXCEEDED`,
   `OR/pages/exa-error-codes-admin.md:27, 32, 69-75`); GitHub's 403 or 429 is a rate limit, never credits
   (`OR/pages/gh-rest-rate-limits.md:166-169`). Hence a distinct `RATE_LIMITED` code and body-aware rules.
2. Key-presence checks lie. `ctx7 whoami` prints "Logged in" and returns before any network call when the
   token is an API key (upstash/context7 `packages/cli/src/commands/auth.ts:217-231`,
   `packages/cli/src/utils/auth.ts:26-28`), while the usage API showed the quota used up (seq 48).
   Last30Days `--diagnose` reports `has_scrapecreators: true` and lists tiktok and instagram as available
   (`OR/local/last30days/diagnose.json`) while ScrapeCreators is at -7 credits (seq 52); TR's
   `src/dependency_intel/credits.py:9-45` only tests that a key is set.
3. Disabled GitHub features fail silently: issue and PR search on a repository with issues and PRs disabled
   returns HTTP 200 with `total_count: 0` (seq 84, 85), GraphQL discussion search returns `discussionCount: 0`
   with no error (seq 88, 89), and REST issue listing returns `200 []` (seq 87). Only the repository read
   (`has_issues`, `has_pull_requests`, `has_discussions`) tells "empty" from "disabled", so the feature check
   must come first, as TR's `src/github_searcher/search.py:693-760` does.
4. Account endpoints exist and are free for five providers; measured: Serper balance unchanged across two
   `/account` calls and down by exactly 6 after 6 searches (seq 2, 53-59); SerpApi `this_month_usage` 5
   before and after (seq 3, 160); ScrapeCreators `creditCount` -7 on both calls (seq 52, 101); GitHub states
   `GET /rate_limit` does not count against the primary limit (`OR/pages/gh-rest-rate-limits.md:148`).

Two user decisions follow from the findings (section 7.6): D142 lists `archived` as a skip reason, but GitHub
keeps issues and PRs of archived repositories searchable (`OR/pages/gh-archiving-repositories.md:34, 37`), so
this report records `archived` without skipping; and GitHub now reports `has_pull_requests` (false on
torvalds/linux, `OR/gh/repos/torvalds_linux.json`), which D142 does not name.

Run incident to relay: listing the profile's variable names with `env | cut -d= -f1` printed two continuation
lines of a multi-line value that look like age secret keys into this session's transcript (nothing was written
to any file; the secret scan covers the mirror). The `codex_research` profile also exposes AWS, age and other
unrelated secrets despite `--no-defaults`. Rotating those age keys and narrowing the profile are user
decisions (section 11).

## 2. Queries sent to each tool, plugin or service (stage 1)

Built from `OR/queries.jsonl`. The preflight rows come first because D142 runs them before stage 1.

### 2.1 Preflight rows (D142), run before stage 1

| seq | provider | check sent | http | status | failure_code |
|---|---|---|---|---|---|
| 1 | firecrawl | `firecrawl credits --json; GET https://api.firecrawl.dev/v2/team/credit-usage` | 200 | SKIPPED | CREDITS_EXHAUSTED |
| 2 | serper | `GET https://google.serper.dev/account (X-API-KEY from env)` | 200 | OK | NONE |
| 3 | serpapi | `GET https://serpapi.com/account.json (api_key from env)` | 200 | OK | NONE |
| 4 | github | `gh api -i rate_limit` | 200 | OK | NONE |
| 5 | webclaw | `webclaw --version; WEBCLAW_API_KEY presence (name only)` |  | OK | NONE |
| 33 | exa | `GET https://api.exa.ai/v0/teams/me (x-api-key from env)` | 404 | ERROR | NOT_FOUND |
| 34 | exa | `GET https://api.exa.ai/websets/v0/teams/me (x-api-key from env)` | 401 | SKIPPED | FEATURE_DISABLED |
| 47 | context7 | `ctx7 whoami` |  | OK | NONE |
| 48 | context7 | `GET https://context7.com/api/v2/usage?days=3 (Bearer from env)` | 200 | SKIPPED | CREDITS_EXHAUSTED |
| 49 | context7 | `CANARY GET https://context7.com/api/v2/libs/search?libraryName=firecrawl&query=credit usage (Bearer from env)` | 429 | SKIPPED | CREDITS_EXHAUSTED |
| 52 | scrapecreators | `GET https://api.scrapecreators.com/v1/account/credit-balance (x-api-key from env)` | 200 | SKIPPED | CREDITS_EXHAUSTED |
| 59 | serper | `GET https://google.serper.dev/account twice after 6 searches (cost check)` | 200 | OK | NONE |
| 71 | github | `gh api repos/0xMassi/webclaw` | 200 | OK | NONE |
| 72 | github | `gh api repos/cli/cli` | 200 | OK | NONE |
| 73 | github | `gh api repos/exa-labs/exa-js` | 200 | OK | NONE |
| 74 | github | `gh api repos/exa-labs/exa-py` | 200 | OK | NONE |
| 75 | github | `gh api repos/firecrawl/firecrawl` | 200 | OK | NONE |
| 76 | github | `gh api repos/mendableai/firecrawl (redirects to firecrawl/firecrawl)` | 200 | OK | NONE |
| 77 | github | `gh api repos/mvanhorn/last30days-skill` | 200 | OK | NONE |
| 78 | github | `gh api repos/serpapi/public-roadmap` | 200 | OK | NONE |
| 79 | github | `gh api repos/serpapi/serpapi-javascript` | 200 | OK | NONE |
| 80 | github | `gh api repos/serpapi/serpapi-python` | 200 | OK | NONE |
| 81 | github | `gh api repos/torvalds/linux` | 200 | OK | NONE |
| 82 | github | `gh api repos/upstash/context7` | 200 | OK | NONE |
| 83 | github | `gh api repos/yanyongyu/githubkit` | 200 | OK | NONE |
| 101 | scrapecreators | `GET https://api.scrapecreators.com/v1/account/credit-balance (second call, cost check)` | 200 | SKIPPED | CREDITS_EXHAUSTED |
| 102 | last30days | `last30days.py --diagnose (Python 3.12.15, SSL_CERT_FILE=/etc/ssl/cert.pem, under fnox)` |  | DEGRADED | CREDITS_EXHAUSTED |
| 160 | serpapi | `GET https://serpapi.com/account.json (second call, cost check)` | 200 | OK | NONE |
| 163 | serper | `GET https://google.serper.dev/account with no key (error-shape probe, free)` | 403 | SKIPPED | CREDENTIAL_INVALID |

### 2.2 Stage 1 queries

Exa ran 12 queries; Context7 and Firecrawl were skipped after preflight (rows 50, 51); webclaw fetched the pages the Exa and Serper results named; Serper ran 6 fallback queries; SerpApi was kept in reserve (its account check only); Last30Days ran twice with an explicit `--plan` (`OR/local/last30days/plan.json`).

| seq | provider | exact query, URL or command |
|---|---|---|
| 6 | exa | `Exa API check remaining credits balance usage endpoint for API key` |
| 7 | exa | `Exa API rate limits 429 error codes Retry-After headers` |
| 8 | exa | `Firecrawl API team credit usage endpoint remainingCredits get_credit_usage SDK` |
| 9 | exa | `Firecrawl rate limits 429 402 payment required error handling` |
| 10 | exa | `Context7 API rate limit quota exceeded headers API key plan` |
| 11 | exa | `SerpApi Account API plan_searches_left total_searches_left free endpoint` |
| 12 | exa | `Serper.dev API account balance endpoint rate limit` |
| 13 | exa | `ScrapeCreators API credit balance endpoint credits remaining` |
| 14 | exa | `GitHub REST API rate limit search code_search graphql resources x-ratelimit-resource` |
| 15 | exa | `GitHub GraphQL search discussions repository hasDiscussionsEnabled disabled` |
| 16 | exa | `last30days skill sources Reddit X YouTube TikTok ScrapeCreators API keys` |
| 17 | exa | `webclaw CLI cloud API key credits extraction` |
| 18 | webclaw | `https://exa.ai/docs/reference/team-management/get-api-key-usage` |
| 19 | webclaw | `https://exa.ai/docs/admin/billing` |
| 20 | webclaw | `https://exa.ai/docs/reference/error-codes` |
| 21 | webclaw | `https://exa.ai/docs/admin/error-codes` |
| 22 | webclaw | `https://exa.ai/docs/reference/rate-limits` |
| 23 | webclaw | `https://exa.ai/docs/reference/pricing` |
| 24 | webclaw | `https://exa.ai/docs/websets/api/teams/get-team-info` |
| 25 | webclaw | `https://docs.firecrawl.dev/api-reference/endpoint/credit-usage` |
| 26 | webclaw | `https://docs.firecrawl.dev/api-reference/errors` |
| 27 | webclaw | `https://docs.firecrawl.dev/rate-limits` |
| 28 | webclaw | `https://docs.firecrawl.dev/billing` |
| 29 | webclaw | `https://docs.firecrawl.dev/api-reference/endpoint/token-usage` |
| 30 | webclaw | `https://docs.firecrawl.dev/api-reference/endpoint/queue-status` |
| 31 | webclaw | `https://docs.firecrawl.dev/api-reference/endpoint/credit-usage-historical` |
| 32 | webclaw | `https://app.unpkg.com/@mendable/firecrawl-js@4.15.0/files/src/v2/methods/usage.ts` |
| 35 | webclaw | `https://context7.com/docs/api-reference/usage/get-api-usage` |
| 36 | webclaw | `https://context7.com/docs/api-guide.md` |
| 37 | webclaw | `https://context7.com/docs/resources/troubleshooting` |
| 38 | webclaw | `https://context7.com/plans` |
| 39 | webclaw | `https://serpapi.com/account-api` |
| 40 | webclaw | `https://serpapi-python.readthedocs.io/en/latest/reference.html` |
| 41 | webclaw | `https://serpapi-python.readthedocs.io/en/latest/user_guide/account-and-locations.html` |
| 42 | webclaw | `https://serpapi.com/api-status-and-error-codes` |
| 43 | webclaw | `https://docs.scrapecreators.com/v1/account/credit-balance` |
| 44 | webclaw | `https://scrapecreators.com/scrape-creators-credit-balance-api` |
| 45 | webclaw | `https://github.com/api-evangelist/serper` |
| 46 | webclaw | `https://serper.dev/` |
| 50 | context7 | `(not called) ctx7 library/docs for firecrawl, exa-py, serpapi-python, githubkit, context7` |
| 51 | firecrawl | `(not called) firecrawl search/scrape for provider credit docs` |
| 53 | serper | `serper.dev api "account" endpoint balance rateLimit` |
| 54 | serper | `firecrawl-py get_credit_usage remaining_credits example` |
| 55 | serper | `exa api costDollars response field budget remaining` |
| 56 | serper | `context7 "api/v2/usage" includedInPlan` |
| 57 | serper | `github api search rate limit 30 requests per minute code search 10 per minute secondary rate limit` |
| 58 | serper | `github api search issues repository with issues disabled "has_issues" false results` |
| 60 | webclaw | `https://docs.github.com/en/rest/rate-limit/rate-limit` |
| 61 | webclaw | `https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api` |
| 62 | webclaw | `https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api` |
| 63 | webclaw | `https://docs.github.com/en/rest/search/search` |
| 64 | webclaw | `https://docs.github.com/en/rest/repos/repos` |
| 65 | webclaw | `https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions` |
| 66 | webclaw | `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/enabling-or-disabling-github-discussions-for-a-repository` |
| 67 | webclaw | `https://docs.github.com/en/graphql/reference/repos` |
| 68 | webclaw | `https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api` |
| 69 | webclaw | `https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests` |
| 70 | webclaw | `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/disabling-issues` |
| 103 | last30days | `last30days.py "search API credit balance and rate limit preflight (Exa, Context7, Firecrawl, Serper, SerpApi)" --plan plan.json --quick --emit json --search reddit,hackernews,github` |
| 104 | last30days | `last30days.py "search API credit balance and rate limit preflight (Exa, Context7, Firecrawl, Serper, SerpApi)" --plan plan.json --emit json --search reddit,hackernews,github` |
| 161 | webclaw | `https://webclaw.io/docs/cloud` |
| 162 | webclaw | `https://webclaw.io/docs/api` |
| 167 | webclaw | `https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories` |

## 3. Results from each (stage 1)

Hits, top results and whether the report uses the row (`used`, set from the citations in sections 1 and 7).

| seq | provider | rc | http | hits | status / failure_code | top results (up to 3) | used |
|---|---|---|---|---|---|---|---|
| 6 | exa | 0 | 200 | 10 | OK / NONE | [https://exa.ai/docs/reference/team-management/get-api-key-us](https://exa.ai/docs/reference/team-management/get-api-key-usage); [Billing and Rate Limits](https://exa.ai/docs/admin/billing); [https://exa.ai/docs/reference/error-codes](https://exa.ai/docs/reference/error-codes) | yes |
| 7 | exa | 0 | 200 | 10 | OK / NONE | [Error Codes - Exa](https://exa.ai/docs/admin/error-codes); [https://exa.ai/docs/reference/error-codes](https://exa.ai/docs/reference/error-codes); [https://exa.ai/docs/reference/rate-limits](https://exa.ai/docs/reference/rate-limits) | yes |
| 8 | exa | 0 | 200 | 10 | OK / NONE | [Credit Usage - Firecrawl Docs](https://docs.firecrawl.dev/api-reference/endpoint/credit-usage); [apps/api/src/controllers/v2/credit-usage.ts](https://github.com/firecrawl/firecrawl/blob/e72fe3ac/apps/api/src/controllers/v2/credit-usage.ts); [fix(ruby-sdk): unwrap credit_usage data field and default sk](https://github.com/firecrawl/firecrawl/commit/da0b081714bcb9329b1119a77e5e15f122af66fa) | yes |
| 9 | exa | 0 | 200 | 10 | OK / NONE | [https://docs.firecrawl.dev/api-reference/errors](https://docs.firecrawl.dev/api-reference/errors); [Rate Limits \| Firecrawl](https://docs.firecrawl.dev/rate-limits); [https://docs.firecrawl.dev/billing](https://docs.firecrawl.dev/billing) | yes |
| 10 | exa | 0 | 200 | 10 | OK / NONE | [https://context7.com/docs/api-guide.md](https://context7.com/docs/api-guide.md); [Troubleshooting - Context7 MCP](https://context7.com/docs/resources/troubleshooting); [Get API usage - Context7 MCP](https://context7.com/docs/api-reference/usage/get-api-usage) | yes |
| 11 | exa | 0 | 200 | 10 | OK / NONE | [Account API - SerpApi](https://serpapi.com/account-api); [[Account API] Include plan renewal date for free plans](https://github.com/serpapi/public-roadmap/issues/3984); [API Reference ](https://serpapi-python.readthedocs.io/en/latest/reference.html) | yes |
| 12 | exa | 0 | 200 | 10 | OK / NONE | [api-evangelist/serper](https://github.com/api-evangelist/serper); [https://raw.githubusercontent.com/api-evangelist/serper/refs](https://raw.githubusercontent.com/api-evangelist/serper/refs/heads/main/authentication/serper-authentication.yml); [Know Your Balance Before You Spend: GET /account/credits in ](https://dev.to/dodou88/know-your-balance-before-you-spend-get-accountcredits-in-practice-4i1i) | yes |
| 13 | exa | 0 | 200 | 10 | OK / NONE | [Scrape Creators Get credit balance API](https://docs.scrapecreators.com/v1/account/credit-balance); [Get credit balance - Scrape Creators API - ScrapeCreators](https://scrapecreators.com/scrape-creators-credit-balance-api); [Get credit balance - Scrape Creators API - ScrapeCreators](https://scrapecreators.com/scrape-creators/endpoints/get-credit-balance) | yes |
| 14 | exa | 0 | 200 | 10 | OK / NONE | [https://docs.github.com/en/rest/rate-limit/rate-limit](https://docs.github.com/en/rest/rate-limit/rate-limit); [https://docs.github.com/en/rest/search/search?apiVersion=202](https://docs.github.com/en/rest/search/search?apiVersion=2022-1128); [https://docs.github.com/en/rest/rate-limit/rate-limit?apiVer](https://docs.github.com/en/rest/rate-limit/rate-limit?apiVersion=2026-03-10) | yes |
| 15 | exa | 0 | 200 | 10 | OK / NONE | [Using the GraphQL API for Discussions](https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions); [Repositories](https://docs.github.com/en/graphql/reference/repos); [Enabling or disabling GitHub Discussions for a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/enabling-or-disabling-github-discussions-for-a-repository) | yes |
| 16 | exa | 0 | 200 | 10 | OK / NONE | [mvanhorn/last30days-skill: AI agent skill that researches ..](https://github.com/mvanhorn/last30days-skill); [skills/last30days/SKILL.md](https://github.com/mvanhorn/last30days-skill/blob/86a882510381532cf0d7aaacd96f87e1b5f3bf80/skills/last30days/SKILL.md); [skills/last30days/scripts/lib/reddit.py](https://github.com/mvanhorn/last30days-skill/blob/8d1c0856/skills/last30days/scripts/lib/reddit.py) | yes |
| 17 | exa | 0 | 200 | 10 | OK / NONE | [Cloud API](https://webclaw.io/docs/cloud); [CLI reference](https://webclaw.io/docs/cli); [https://webclaw.io/docs/getting-started](https://webclaw.io/docs/getting-started) | yes |
| 18 | webclaw | 0 |  | 1 | OK / NONE | [Get API key usage](https://exa.ai/docs/reference/team-management/get-api-key-usage) | yes |
| 19 | webclaw | 0 |  | 1 | OK / NONE | [Billing and Rate Limits](https://exa.ai/docs/admin/billing) | yes |
| 20 | webclaw | 0 |  | 1 | OK / NONE | [Error Codes](https://exa.ai/docs/reference/error-codes) | no |
| 21 | webclaw | 0 |  | 1 | OK / NONE | [Error Codes](https://exa.ai/docs/admin/error-codes) | yes |
| 22 | webclaw | 0 |  | 1 | OK / NONE | [Billing and Rate Limits](https://exa.ai/docs/reference/rate-limits) | no |
| 23 | webclaw | 0 |  | 1 | OK / NONE | [Pricing](https://exa.ai/docs/reference/pricing) | no |
| 24 | webclaw | 0 |  | 1 | OK / NONE | [[​](https://exa.ai/docs/websets/api/teams/get-team-info#over](https://exa.ai/docs/websets/api/teams/get-team-info) | yes |
| 25 | webclaw | 0 |  | 1 | OK / NONE | [Credit Usage](https://docs.firecrawl.dev/api-reference/endpoint/credit-usage) | yes |
| 26 | webclaw | 0 |  | 1 | OK / NONE | [[​](https://docs.firecrawl.dev/api-reference/errors#error-re](https://docs.firecrawl.dev/api-reference/errors) | yes |
| 27 | webclaw | 0 |  | 1 | OK / NONE | [[​](https://docs.firecrawl.dev/rate-limits#concurrent-browse](https://docs.firecrawl.dev/rate-limits) | no |
| 28 | webclaw | 0 |  | 1 | OK / NONE | [[​](https://docs.firecrawl.dev/billing#overview) Overview](https://docs.firecrawl.dev/billing) | no |
| 29 | webclaw | 0 |  | 1 | OK / NONE | [Token Usage](https://docs.firecrawl.dev/api-reference/endpoint/token-usage) | no |
| 30 | webclaw | 0 |  | 1 | OK / NONE | [Queue Status](https://docs.firecrawl.dev/api-reference/endpoint/queue-status) | no |
| 31 | webclaw | 0 |  | 1 | OK / NONE | [Historical Credit Usage](https://docs.firecrawl.dev/api-reference/endpoint/credit-usage-historical) | no |
| 32 | webclaw | 0 |  | 1 | OK / NONE | [UNPKG](https://app.unpkg.com/@mendable/firecrawl-js@4.15.0/files/src/v2/methods/usage.ts) | no |
| 35 | webclaw | 0 |  | 1 | OK / NONE | [Get API usage](https://context7.com/docs/api-reference/usage/get-api-usage) | yes |
| 36 | webclaw | 0 |  | 1 | OK / NONE | [API Guide](https://context7.com/docs/api-guide.md) | yes |
| 37 | webclaw | 0 |  | 1 | OK / NONE | [Documentation index](https://context7.com/docs/resources/troubleshooting) | no |
| 38 | webclaw | 0 |  | 1 | OK / NONE | [[Context7 Pricing & Plans](https://context7.com/plans#plans)](https://context7.com/plans) | no |
| 39 | webclaw | 0 |  | 1 | OK / NONE | [** Account API](https://serpapi.com/account-api) | yes |
| 40 | webclaw | 0 |  | 1 | OK / NONE | [API Reference [](https://serpapi-python.readthedocs.io/en/l](https://serpapi-python.readthedocs.io/en/latest/reference.html) | no |
| 41 | webclaw | 0 |  | 1 | OK / NONE | [Account and Locations [](https://serpapi-python.readthedocs](https://serpapi-python.readthedocs.io/en/latest/user_guide/account-and-locations.html) | yes |
| 42 | webclaw | 0 |  | 1 | OK / NONE | [** Status and Error Codes](https://serpapi.com/api-status-and-error-codes) | yes |
| 43 | webclaw | 0 |  | 1 | OK / NONE | [Integrations](https://docs.scrapecreators.com/v1/account/credit-balance) | yes |
| 44 | webclaw | 1 |  | 0 | ERROR / OTHER | [https://scrapecreators.com/scrape-creators-credit-balance-ap](https://scrapecreators.com/scrape-creators-credit-balance-api) | yes |
| 45 | webclaw | 0 |  | 1 | OK / NONE | [Serper](https://github.com/api-evangelist/serper) | yes |
| 46 | webclaw | 0 |  | 1 | OK / NONE | [$50*](https://serper.dev/) | yes |
| 50 | context7 |  |  | 0 | SKIPPED / CREDITS_EXHAUSTED |  | yes |
| 51 | firecrawl |  |  | 0 | SKIPPED / CREDITS_EXHAUSTED |  | yes |
| 53 | serper | 0 | 200 | 10 | OK / NONE | [Serper - The World's Fastest and Cheapest Google Search API](https://serper.dev/); [Serper - Review (Score: 56/100)](https://nolist.ai/item/serper); [API keys](https://docs.opensea.io/reference/api-keys) | yes |
| 54 | serper | 0 | 200 | 10 | OK / NONE | [Python SDK](https://docs.firecrawl.dev/sdks/python); [Python Quickstart](https://docs.firecrawl.dev/quickstarts/python); [firecrawl-py](https://github.com/firecrawl/firecrawl-py) | yes |
| 55 | serper | 0 | 200 | 10 | OK / NONE | [Changelog](https://exa.ai/docs/changelog); [Pricing](https://exa.ai/docs/admin/pricing); [Exa Pricing in 2026: What 100000 Searches Cost, and ...](https://fastcrw.com/blog/exa-pricing-explained) | yes |
| 56 | serper | 0 | 200 | 1 | OK / NONE | [Get API usage](https://context7.com/docs/api-reference/usage/get-api-usage) | yes |
| 57 | serper | 0 | 200 | 10 | OK / NONE | [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api); [Is there anyway to increase the code search limit? : r/githu](https://www.reddit.com/r/github/comments/18jwdkd/github_api_is_there_anyway_to_increase_the_code/); [Rate Limit Error · community · Discussion #179480](https://github.com/orgs/community/discussions/179480) | yes |
| 58 | serper | 0 | 200 | 10 | OK / NONE | [REST API endpoints for issues](https://docs.github.com/en/rest/issues/issues); [REST API endpoints for repositories](https://docs.github.com/rest/repos/repos); [REST API endpoints for issues](https://docs.github.com/en/enterprise-server@3.20/rest/issues/issues) | yes |
| 60 | webclaw | 0 |  | 1 | OK / NONE | [REST API endpoints for rate limits](https://docs.github.com/en/rest/rate-limit/rate-limit) | yes |
| 61 | webclaw | 0 |  | 1 | OK / NONE | [Rate limits for the REST API](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) | yes |
| 62 | webclaw | 0 |  | 1 | OK / NONE | [Rate limits and query limits for the GraphQL API](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api) | yes |
| 63 | webclaw | 0 |  | 1 | OK / NONE | [REST API endpoints for search](https://docs.github.com/en/rest/search/search) | yes |
| 64 | webclaw | 0 |  | 1 | OK / NONE | [REST API endpoints for repositories](https://docs.github.com/en/rest/repos/repos) | yes |
| 65 | webclaw | 0 |  | 1 | OK / NONE | [Using the GraphQL API for Discussions](https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions) | no |
| 66 | webclaw | 0 |  | 1 | OK / NONE | [Enabling or disabling GitHub Discussions for a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/enabling-or-disabling-github-discussions-for-a-repository) | no |
| 67 | webclaw | 0 |  | 1 | OK / NONE | [Repositories](https://docs.github.com/en/graphql/reference/repos) | yes |
| 68 | webclaw | 0 |  | 1 | OK / NONE | [Troubleshooting the REST API](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api) | no |
| 69 | webclaw | 0 |  | 1 | OK / NONE | [Searching issues and pull requests](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests) | no |
| 70 | webclaw | 0 |  | 1 | OK / NONE | [Disabling issues](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/disabling-issues) | no |
| 103 | last30days | 0 |  | 0 | DEGRADED / CREDITS_EXHAUSTED |  | yes |
| 104 | last30days | 0 |  | 6 | DEGRADED / CREDITS_EXHAUSTED | [Recover gracefully from exhausted provider credits](https://github.com/MooseGooseConsulting/ColdSearch/pull/69); [The research chain uses whatever search product a box has, a](https://github.com/trevorotts1/blackceo-command-center/pull/388); [docs(agents): distinguish v5 package from legacy Marionette](https://github.com/marionettejs/marionette-develop/pull/624) | yes |
| 161 | webclaw | 0 |  | 1 | OK / NONE | [Cloud API](https://webclaw.io/docs/cloud) | yes |
| 162 | webclaw | 0 |  | 1 | OK / NONE | [REST API](https://webclaw.io/docs/api) | no |
| 167 | webclaw | 0 |  | 1 | OK / NONE | [Archiving repositories](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories) | yes |

## 4. GitHub issues, PRs and discussions searched (stage 2)

Every repository was feature-checked first (preflight rows 71-83); searches against a disabled feature were not sent and are logged as SKIPPED, FEATURE_DISABLED (rows 136-141). Rows 84-91 are deliberate probes of how a disabled feature looks. `seeded_by` is the stage-1 (or preflight) row whose result named the search; `via` is the search row that found an issue or PR.

| seq | provider | query | hits | status / failure_code | seeded_by | via |
|---|---|---|---|---|---|---|
| 84 | gh-issue-search | `gh api -X GET search/issues -f q='repo:torvalds/linux is:issue memory' (issues disabled control)` | 0 | SKIPPED / FEATURE_DISABLED | 58 |  |
| 85 | gh-pr-search | `gh api -X GET search/issues -f q='repo:torvalds/linux is:pr memory' (pull requests disabled control)` | 0 | SKIPPED / FEATURE_DISABLED | 58 |  |
| 86 | gh-issue-view | `gh issue list -R torvalds/linux -L 1` | 0 | SKIPPED / FEATURE_DISABLED | 58 |  |
| 87 | gh-issue-view | `gh api -i 'repos/torvalds/linux/issues?per_page=1'` | 0 | SKIPPED / FEATURE_DISABLED | 58 |  |
| 88 | gh-graphql-discussion | `gh api graphql repository(owner:exa-labs,name:exa-py){hasDiscussionsEnabled discussions(first:1){totalCount}}` | 0 | SKIPPED / FEATURE_DISABLED | 15 |  |
| 89 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION,query:"repo:exa-labs/exa-py credits")` | 0 | SKIPPED / FEATURE_DISABLED | 15 |  |
| 90 | gh-graphql-discussion | `gh api -i 'repos/exa-labs/exa-py/discussions?per_page=1'` | 0 | SKIPPED / FEATURE_DISABLED | 15 |  |
| 91 | gh-pr-view | `gh api -i 'repos/torvalds/linux/pulls?per_page=1'` | 0 | SKIPPED / FEATURE_DISABLED | 58 |  |
| 92 | git-clone | `https://github.com/firecrawl/firecrawl.git` | 1 | OK / NONE | 8 |  |
| 93 | git-clone | `https://github.com/firecrawl/cli.git` | 1 | OK / NONE | 8 |  |
| 94 | git-clone | `https://github.com/exa-labs/exa-py.git` | 1 | OK / NONE | 6 |  |
| 95 | git-clone | `https://github.com/exa-labs/exa-js.git` | 1 | OK / NONE | 6 |  |
| 96 | git-clone | `https://github.com/upstash/context7.git` | 1 | OK / NONE | 10 |  |
| 97 | git-clone | `https://github.com/serpapi/serpapi-python.git` | 1 | OK / NONE | 11 |  |
| 98 | git-clone | `https://github.com/yanyongyu/githubkit.git` | 1 | OK / NONE | 14 |  |
| 99 | git-clone | `https://github.com/mvanhorn/last30days-skill.git` | 1 | OK / NONE | 16 |  |
| 100 | git-clone | `https://github.com/0xMassi/webclaw.git` | 1 | OK / NONE | 17 |  |
| 105 | gh-issue-search | `gh search issues "credit usage" --repo firecrawl/firecrawl --limit 15` | 5 | OK / NONE | 8 |  |
| 106 | gh-issue-search | `gh search issues "remainingCredits" --repo firecrawl/firecrawl --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 8 |  |
| 107 | gh-issue-search | `gh search issues "insufficient credits 402" --repo firecrawl/firecrawl --limit 15` | 1 | OK / NONE | 9 |  |
| 108 | gh-pr-search | `gh search prs "credit usage" --repo firecrawl/firecrawl --limit 15` | 15 | OK / NONE | 8 |  |
| 109 | gh-issue-search | `gh search issues "quota" --repo upstash/context7 --limit 15` | 7 | OK / NONE | 10 |  |
| 110 | gh-issue-search | `gh search issues "usage api" --repo upstash/context7 --limit 15` | 1 | OK / NONE | 10 |  |
| 111 | gh-pr-search | `gh search prs "rate limit" --repo upstash/context7 --limit 15` | 15 | OK / NONE | 10 |  |
| 112 | gh-issue-search | `gh search issues "402" --repo exa-labs/exa-py --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 6 |  |
| 113 | gh-issue-search | `gh search issues "credits" --repo exa-labs/exa-py --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 6 |  |
| 114 | gh-issue-search | `gh search issues "rate limit" --repo exa-labs/exa-js --limit 15` | 1 | OK / NONE | 7 |  |
| 115 | gh-issue-search | `gh search issues "credits" --repo exa-labs/exa-js --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 6 |  |
| 116 | gh-issue-search | `gh search issues "account" --repo serpapi/serpapi-python --limit 15` | 2 | OK / NONE | 11 |  |
| 117 | gh-issue-search | `gh search issues "Account API" --repo serpapi/public-roadmap --limit 15` | 15 | OK / NONE | 11 |  |
| 118 | gh-issue-search | `gh search issues "rate limit" --repo yanyongyu/githubkit --limit 15` | 5 | OK / NONE | 14 |  |
| 119 | gh-issue-search | `gh search issues "ScrapeCreators 402" --repo mvanhorn/last30days-skill --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 104 |  |
| 120 | gh-issue-search | `gh search issues "credits exhausted" --repo mvanhorn/last30days-skill --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 104 |  |
| 121 | gh-issue-search | `gh search issues "rate limit" --repo 0xMassi/webclaw --limit 15` | 1 | OK / NONE | 17 |  |
| 122 | gh-issue-search | `gh search issues "rate limit search" --repo cli/cli --limit 15` | 0 | EMPTY_UNVERIFIED / NONE | 57 |  |
| 123 | gh-issue-view | `gh issue view 271 -R yanyongyu/githubkit --comments` | 1 | OK / NONE | 14 | 118 |
| 124 | gh-issue-view | `gh issue view 16 -R serpapi/serpapi-python --comments` | 1 | OK / NONE | 11 | 116 |
| 125 | gh-issue-view | `gh issue view 2989 -R serpapi/public-roadmap --comments` | 1 | OK / NONE | 11 | 117 |
| 126 | gh-issue-view | `gh issue view 873 -R firecrawl/firecrawl --comments` | 1 | OK / NONE | 8 | 105 |
| 127 | gh-issue-view | `gh issue view 2145 -R upstash/context7 --comments` | 1 | OK / NONE | 10 | 109 |
| 128 | gh-issue-view | `gh issue view 3406 -R upstash/context7 --comments` | 1 | OK / NONE | 10 | 109 |
| 129 | gh-pr-view | `gh pr view 69 -R MooseGooseConsulting/ColdSearch` | 1 | OK / NONE | 104 |  |
| 130 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION, query:"repo:firecrawl/firecrawl credits")` | 4 | OK / NONE | 8 |  |
| 131 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION, query:"repo:upstash/context7 quota")` | 0 | EMPTY_VERIFIED / NONE | 10 |  |
| 132 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION, query:"repo:upstash/context7 rate limit")` | 2 | OK / NONE | 10 |  |
| 133 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION, query:"repo:0xMassi/webclaw credits")` | 0 | EMPTY_VERIFIED / NONE | 17 |  |
| 134 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION, query:"repo:cli/cli rate limit")` | 12 | OK / NONE | 57 |  |
| 135 | gh-graphql-discussion | `gh api graphql search(type:DISCUSSION, query:"repo:community/community search API rate limit 403")` | 4 | OK / NONE | 57 |  |
| 136 | gh-graphql-discussion | `(not called) search(type:DISCUSSION, query:"repo:exa-labs/exa-py credits OR rate limit")` | 0 | SKIPPED / FEATURE_DISABLED | 6 |  |
| 137 | gh-graphql-discussion | `(not called) search(type:DISCUSSION, query:"repo:exa-labs/exa-js credits OR rate limit")` | 0 | SKIPPED / FEATURE_DISABLED | 6 |  |
| 138 | gh-graphql-discussion | `(not called) search(type:DISCUSSION, query:"repo:serpapi/serpapi-python credits OR rate limit")` | 0 | SKIPPED / FEATURE_DISABLED | 11 |  |
| 139 | gh-graphql-discussion | `(not called) search(type:DISCUSSION, query:"repo:yanyongyu/githubkit credits OR rate limit")` | 0 | SKIPPED / FEATURE_DISABLED | 14 |  |
| 140 | gh-graphql-discussion | `(not called) search(type:DISCUSSION, query:"repo:mvanhorn/last30days-skill credits OR rate limit")` | 0 | SKIPPED / FEATURE_DISABLED | 104 |  |
| 141 | gh-graphql-discussion | `(not called) search(type:DISCUSSION, query:"repo:MooseGooseConsulting/ColdSearch credits OR rate limit")` | 0 | SKIPPED / FEATURE_DISABLED | 104 |  |
| 164 | gh-pr-search | `gh search prs "payment-required" --repo mvanhorn/last30days-skill --limit 15` | 2 | OK / NONE | 103 |  |
| 165 | gh-pr-search | `gh search prs "402" --repo mvanhorn/last30days-skill --limit 15` | 13 | OK / NONE | 103 |  |
| 166 | gh-pr-view | `gh pr view 1124 -R mvanhorn/last30days-skill` | 1 | OK / NONE | 103 |  |

## 5. Githubkit saved searches run (reproduced read-only, with controls) and proposed rows

`./dev/mise run research:collect` writes into a tracked path, so each candidate row was reproduced with the equivalent `gh api -X GET search/code -f q="<query> repo:<repo>" -F per_page=5 -F page=1` (`dev/collect_saved_search.py` uses `search/code` the same way) into `OR/gh/saved/`, each with the `README` control the existing rows use. The existing seven rows in `dev/saved-searches.toml` (Codex schema and config, agent roles) are unrelated to this topic and were not rerun. Rows 152-154 hit a code_search 403 caused by another agent on the same token and were retried (157-159). The proposed rows are in section 10.

| seq | id | control | query | rc | hits | status / failure_code | seeded_by |
|---|---|---|---|---|---|---|---|
| 142 | fc-credit-usage-sdk | no | `gh api -X GET search/code -f q="team/credit-usage repo:firecrawl/firecrawl" -F per_page=5 -F page=1` | 0 | 19 | OK / NONE | 8 |
| 143 | fc-credit-usage-sdk-control | yes | `gh api -X GET search/code -f q="README repo:firecrawl/firecrawl" -F per_page=5 -F page=1` | 0 | 35 | OK / NONE | 8 |
| 144 | c7-ratelimit-headers | no | `gh api -X GET search/code -f q="ratelimit-remaining repo:upstash/context7" -F per_page=5 -F page=1` | 0 | 3 | OK / NONE | 10 |
| 145 | c7-ratelimit-headers-control | yes | `gh api -X GET search/code -f q="README repo:upstash/context7" -F per_page=5 -F page=1` | 0 | 27 | OK / NONE | 10 |
| 146 | exa-cost-dollars | no | `gh api -X GET search/code -f q="costDollars repo:exa-labs/exa-py" -F per_page=5 -F page=1` | 0 | 11 | OK / NONE | 6 |
| 147 | exa-cost-dollars-control | yes | `gh api -X GET search/code -f q="README repo:exa-labs/exa-py" -F per_page=5 -F page=1` | 0 | 3 | OK / NONE | 6 |
| 148 | serpapi-account-json | no | `gh api -X GET search/code -f q="account.json repo:serpapi/serpapi-python" -F per_page=5 -F page=1` | 0 | 1 | OK / NONE | 11 |
| 149 | serpapi-account-json-control | yes | `gh api -X GET search/code -f q="README repo:serpapi/serpapi-python" -F per_page=5 -F page=1` | 0 | 5 | OK / NONE | 11 |
| 150 | githubkit-ratelimit-exc | no | `gh api -X GET search/code -f q="SecondaryRateLimitExceeded repo:yanyongyu/githubkit" -F per_page=5 -F page=1` | 0 | 3 | OK / NONE | 14 |
| 151 | githubkit-ratelimit-exc-control | yes | `gh api -X GET search/code -f q="README repo:yanyongyu/githubkit" -F per_page=5 -F page=1` | 0 | 54 | OK / NONE | 14 |
| 152 | l30-payment-required | no | `gh api -X GET search/code -f q="PAYMENT_REQUIRED repo:mvanhorn/last30days-skill" -F per_page=5 -F page=1` | 1 | 0 | ERROR / HTTP_ERROR | 104 |
| 153 | l30-payment-required-control | yes | `gh api -X GET search/code -f q="README repo:mvanhorn/last30days-skill" -F per_page=5 -F page=1` | 1 | 0 | ERROR / HTTP_ERROR | 104 |
| 154 | l30-sc-credit-balance | no | `gh api -X GET search/code -f q="credit-balance repo:mvanhorn/last30days-skill" -F per_page=5 -F page=1` | 1 | 0 | ERROR / HTTP_ERROR | 52 |
| 155 | exa-js-retry-after | no | `gh api -X GET search/code -f q="Retry-After repo:exa-labs/exa-js" -F per_page=5 -F page=1` | 0 | 0 | EMPTY_VERIFIED / NONE | 7 |
| 156 | exa-js-retry-after-control | yes | `gh api -X GET search/code -f q="README repo:exa-labs/exa-js" -F per_page=5 -F page=1` | 0 | 4 | OK / NONE | 7 |
| 157 | l30-payment-required | no | `gh api -i -X GET search/code -f q="PAYMENT_REQUIRED repo:mvanhorn/last30days-skill" -F per_page=5 (retry of se` | 0 | 21 | OK / NONE | 104 |
| 158 | l30-payment-required-control | yes | `gh api -X GET search/code -f q="README repo:mvanhorn/last30days-skill" -F per_page=5 -F page=1` | 0 | 33 | OK / NONE | 104 |
| 159 | l30-sc-credit-balance | no | `gh api -X GET search/code -f q="credit-balance repo:mvanhorn/last30days-skill" -F per_page=5 -F page=1` | 0 | 0 | EMPTY_VERIFIED / NONE | 52 |

## 6. Stage-2 GitHub and saved searches against the stage-1 results (seed-to-search map)

Row 52 is a preflight row (the ScrapeCreators balance) that seeded two saved searches; every other seed is a stage-1 row.

| stage-1 seed (seq, provider, query) | stage-2 rows it seeded |
|---|---|
| 6, exa, `Exa API check remaining credits balance usage endpoint for API key` | 94, 95, 112, 113, 115, 136, 137, 146, 147 |
| 7, exa, `Exa API rate limits 429 error codes Retry-After headers` | 114, 155, 156 |
| 8, exa, `Firecrawl API team credit usage endpoint remainingCredits get_credit_u` | 92, 93, 105, 106, 108, 126, 130, 142, 143 |
| 9, exa, `Firecrawl rate limits 429 402 payment required error handling` | 107 |
| 10, exa, `Context7 API rate limit quota exceeded headers API key plan` | 96, 109, 110, 111, 127, 128, 131, 132, 144, 145 |
| 11, exa, `SerpApi Account API plan_searches_left total_searches_left free endpoi` | 97, 116, 117, 124, 125, 138, 148, 149 |
| 14, exa, `GitHub REST API rate limit search code_search graphql resources x-rate` | 98, 118, 123, 139, 150, 151 |
| 15, exa, `GitHub GraphQL search discussions repository hasDiscussionsEnabled dis` | 88, 89, 90 |
| 16, exa, `last30days skill sources Reddit X YouTube TikTok ScrapeCreators API ke` | 99 |
| 17, exa, `webclaw CLI cloud API key credits extraction` | 100, 121, 133 |
| 52, scrapecreators, `GET https://api.scrapecreators.com/v1/account/credit-balance (x-api-ke` | 154, 159 |
| 57, serper, `github api search rate limit 30 requests per minute code search 10 per` | 122, 134, 135 |
| 58, serper, `github api search issues repository with issues disabled "has_issues" ` | 84, 85, 86, 87, 91 |
| 103, last30days, `last30days.py "search API credit balance and rate limit preflight (Exa` | 164, 165, 166 |
| 104, last30days, `last30days.py "search API credit balance and rate limit preflight (Exa` | 119, 120, 129, 140, 141, 152, 153, 157, 158 |

## 7. Findings with citations

### 7.1 Per provider: SDK method, endpoint, fields, auth, cost, headers, error classes

**Firecrawl.**
- SDK: firecrawl-py 4.50.0 `Firecrawl.get_credit_usage()` returns `CreditUsage(remaining_credits,
  plan_credits, billing_period_start, billing_period_end)` from `GET /v2/team/credit-usage`
  (`OR/repos/firecrawl/apps/python-sdk/firecrawl/v2/methods/usage.py:19-32`, `types.py:2168-2174`,
  version `firecrawl/__init__.py:44`); siblings `get_token_usage`, `get_queue_status`, `get_concurrency`,
  `get_credit_usage_historical` (`usage.py:5-80`). JS: @mendable/firecrawl-js 4.46.0 `getCreditUsage()`
  (`apps/js-sdk/firecrawl/src/v2/methods/usage.ts:17-19`). CLI: firecrawl-cli 1.26.3 `credit-usage`, alias
  `credits`, `--json` (`OR/repos/firecrawl-cli/src/index.ts:2634-2635`; it calls the same endpoint,
  `src/commands/credit-usage.ts:55`, and exits 1 only on a request failure, line 154).
- Endpoint and fields: `GET https://api.firecrawl.dev/v2/team/credit-usage`, `Authorization: Bearer`, body
  `{success, data:{remainingCredits, planCredits, billingPeriodStart, billingPeriodEnd}}`
  (`OR/pages/firecrawl-credit-usage.md:13-15, 128-133`; https://docs.firecrawl.dev/api-reference/endpoint/credit-usage).
  The endpoint was added on request in firecrawl/firecrawl#873 (closed 2024-12-20). Live: `-128` of `1000`,
  period end 2026-11-11 (seq 1; parent probe 2026-10-14 agrees). `firecrawl credits --json` exits 0 with a
  negative balance, so the caller must read the number.
- Cost: the route runs under `RateLimiterMode.Account` (`OR/repos/firecrawl/apps/api/src/routes/v2.ts:456-460`),
  whose fallback is 1000 requests per minute (`apps/api/src/services/rate-limiter.ts:35`); no credit is drawn
  (inferred from the controller path; the billing page does not say, UNVERIFIED).
- Headers on normal calls: no `X-RateLimit-*` (observed, `OR/probe/pf-firecrawl-api.headers.json`);
  `Retry-After` on 429 "when available" (`OR/pages/firecrawl-errors.md:58`) and on auth refusals that carry
  `retryAfterSeconds` (`apps/api/src/routes/shared.ts:315-317`).
- Errors: 401 invalid token, 402 "Payment Required: Insufficient credits", 403 plan or permission gate, 429
  "Rate limit exceeded" or "Concurrency limit reached" (`OR/pages/firecrawl-errors.md:36-51`); the Python SDK
  raises `UnauthorizedError`, `PaymentRequiredError`, `RateLimitError` (`apps/python-sdk/firecrawl/v2/utils/error_handler.py:173, 176, 187`).
  A crawl poll can return quota errors on 429 (MooseGooseConsulting/ColdSearch#69, 2026-10-02: "Preserve
  Firecrawl crawl-poll quota errors, including quota-bearing HTTP 429"), so a Firecrawl 429 whose body names
  credits is `CREDITS_EXHAUSTED`.

**Context7.**
- SDK: @upstash/context7-sdk 0.5.1 has no usage or account method (commands `search`, `search-library`,
  `get-context` only, `OR/repos/context7/packages/sdk/src/commands/`), but every `Context7Error` carries
  `rateLimit {limit, remaining, reset, retryAfter}` parsed from `RateLimit-*` or `X-RateLimit-*` and
  `Retry-After` (`packages/sdk/src/error/index.ts:11, 18-32`, `packages/sdk/src/http/response.ts:13-33`).
- Endpoint and fields: `GET https://context7.com/api/v2/usage?days=N`, `Authorization: Bearer`, body `plan`
  (`free`, `pro`, `enterprise`, `payg`), `usageResetsAt`, `member.requests`, `member.includedInPlan`,
  `teamspace.extraRequests`, `extraCostUsd`, `spendingLimitUsd`, `daily[]` (`OR/pages/context7-get-api-usage.md:6-8, 38-95, 156`;
  https://context7.com/docs/api-reference/usage/get-api-usage). Line 156: on the Free plan requests "stop with a
  429 when `requests` reaches `includedInPlan`"; on paid plans requests return 402 once `extraCostUsd` reaches
  `spendingLimitUsd`. Live: `free`, `1000` of `1000`, resets 2026-11-01 (seq 48).
- Cost: the usage call is neither a search nor a docs request in the field definitions (line 156), so it should
  not count (UNVERIFIED by measurement, since the quota was already at zero).
- CLI: `ctx7 whoami` (ctx7 0.6.1) is not a check: with an API key it prints "Logged in" and returns without a
  request (`packages/cli/src/commands/auth.ts:217-231`). TR's plugin doctor trusts it
  (TR `src/tr_module/plugin_doctor.py:244-299`).
- Headers: 429 carries `Retry-After`, `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`
  (`OR/pages/context7-api-guide.md:170-177`). Live quota canary (seq 49): 429, body `{"error":"Quota Exceeded",
  "message":"Monthly quota reached. You'll receive 20 bonus API requests tomorrow. ..."}`, `RateLimit-Limit 1000`,
  `RateLimit-Remaining 0`, `RateLimit-Reset 1793491200`, `Retry-After 1497985`. Short-window errors use
  `{"error":"rate_limit_exceeded"}`, invalid keys `{"error":"invalid_api_key"}` (`get-api-usage.md:115-128`).
  The MCP client prints the same text for both kinds of 429 (`packages/mcp/src/lib/api.ts:60-63`), and users
  hit both (upstash/context7#2145, 2026-03-07; #3406, 2026-10-14, asks for the tier to be shown).

**Exa.**
- SDK: exa-py 2.25.0 and exa-js 2.25.0 have no balance or usage method; the code search for
  `team-management`, `api-keys/.../usage` and `getUsage` finds nothing, and the SDK only parses the per-response
  `costDollars` (`OR/repos/exa-py/exa_py/api.py:510-526`; saved search seq 146, 11 hits). exa-py raises
  `ValueError("Request failed with status code N: <body>")` (`api.py:1688-1693`), so the status and the body's
  `tag` are the only signals; exa-js has a typed `ExaError` with `statusCode` (`OR/repos/exa-js/src/errors.ts:44-58`).
- Account APIs: `GET https://admin-api.exa.ai/team-management/api-keys/{id}/usage` returns `total_cost_usd` and
  `cost_breakdown` for a period, not a balance, and needs a service key enabled per team on request
  (`OR/pages/exa-get-api-key-usage.md:26-27, 168, 174, 197-205`). Websets `GET /websets/v0/teams/me` reports
  concurrency only (`OR/pages/exa-get-team-info.md:7, 109-121`; the documented `/v0/teams/me` path gave 404,
  seq 33) and answered this key with 401 "Your team does not have access to the API. Upgrade to a Pro
  plan" (seq 34): a plan gate, not a bad key, since the same key got 200 on `/search` (seq 6).
- Cost and limits: free tier $10 per month, reset on the first day of the month; 10 QPS on `/search`
  (`OR/pages/exa-billing.md:40, 63, 77`). One `/search` of 10 results cost `$0.007` (`costDollars.total`, seq 6-17).
- Headers on normal calls: no rate-limit headers; `x-exa-queued`, `x-exa-queue-ms`, `x-request-id`, and
  `Retry-After` is exposed for 429 (`OR/probe/exa/q01.headers.json`; `exa-billing.md:85`).
- Errors: 401 `INVALID_API_KEY`; 402 `NO_MORE_CREDITS`, `API_KEY_BUDGET_EXCEEDED`, `TEAM_BUDGET_EXCEEDED`; 403
  `FEATURE_DISABLED`; 429 `RATE_LIMIT_EXCEEDED`; 503 `SERVICE_OVERLOADED` (not billed)
  (`OR/pages/exa-error-codes-admin.md:25-35, 44-52, 66-76`; https://exa.ai/docs/admin/error-codes). No canary is
  needed: the first real call is classified.

**Serper.**
- No official SDK. `GET https://google.serper.dev/account` with `X-API-KEY` returns `{balance, rateLimit}`
  (seq 2; parent probe 2026-10-14). The endpoint is undocumented: serper.dev only says credits are deducted on
  successful responses and queries stop at zero (`OR/pages/serper-home.md:2237-2240`); the API Evangelist
  profile is third-party (`OR/pages/serper-api-evangelist.md:23`).
- Cost: free; balance 1313, then 1307 after 6 searches, unchanged by a second `/account` call (seq 59). Each
  search body states `"credits": 1`.
- Headers on normal calls: `x-ratelimit-limit: 25`, `x-ratelimit-remaining`, `x-ratelimit-reset` (epoch seconds)
  (`OR/probe/serper/s01.headers.json`).
- Errors: a missing key gets 403 `{"message":"Unauthorized. Sign up for a free account.","statusCode":403}`
  (seq 163). The status for an exhausted balance is not documented (UNVERIFIED); TR's doctor treats 402 and 429
  as depleted (TR `plugin_doctor.py:438-450`).

**SerpApi.**
- SDK: serpapi-python 1.1.2 `serpapi.Client.account()` wraps `GET /account.json` (`OR/repos/serpapi-python/serpapi/core.py:165-186`)
  and raises `serpapi.HTTPError` with `status_code` (`serpapi/exceptions.py:22-35`).
- Endpoint and fields: `GET https://serpapi.com/account.json?api_key=...`: `account_status`, `plan_id`,
  `searches_per_month`, `plan_searches_left`, `extra_credits`, `total_searches_left`, `this_month_usage`,
  `this_hour_searches`, `last_hour_searches`, `account_rate_limit_per_hour`, `plan_renewal_date`
  (`OR/pages/serpapi-account-api.md`; https://serpapi.com/account-api; the docs example drops `.json`,
  serpapi/public-roadmap#2989, open since 2025-08-27). The response echoes `api_key` and `account_email`, so the
  result must be scrubbed before it is logged (`OR/pages/serpapi-account-api.md` example; this run's helper
  redacted both, `OR/probe/pf-serpapi.body`).
- Cost: free (`this_month_usage` 5 before and after, seq 3, 160). Live: 245 of 250, 250 per hour.
- Headers: none rate-related (`OR/probe/pf-serpapi.headers.json`).
- Errors: 401 "Invalid API key"; 429 for the hourly limit and for "Your account has run out of searches."
  (`OR/pages/serpapi-status-errors.md:11-15, 51-66`; serpapi/serpapi-python#16).

**ScrapeCreators (used by Last30Days).**
- No SDK in use; Last30Days calls the REST API. `GET https://api.scrapecreators.com/v1/account/credit-balance`
  with `x-api-key`; the docs show `credits_remaining`, `credits_charged`, `creditCount` and "1 credit per request"
  (`OR/pages/scrapecreators-credit-balance.md:596-610`). Live shape differs: `{"success":true,"creditCount":-7,
  "message":"You have -7 credits remaining."}` (seq 52). A second call left `creditCount` at -7 (seq 101), so the
  check was not billed at a negative balance (billing at a positive balance UNVERIFIED).
- Errors: 402 Payment Required when exhausted (`OR/local/last30days/l30-run.err`: "ScrapeCreators backup also
  failed (HTTPError: HTTP 402: Payment Required)"). No rate-limit headers observed.

**Last30Days and its other sources.**
- `--diagnose` and `--preflight` report configuration and key presence only (`OR/local/last30days/diagnose.json`).
  Upstream doctor live-probes only free keyless endpoints and states that "a health check must never spend
  ScrapeCreators credits" (mvanhorn/last30days-skill `skills/last30days/scripts/lib/doctor.py:1838-1856`), and it
  never calls the credit-balance endpoint (saved search seq 159: 0 hits, control 33).
- Upstream outcome vocabulary already separates the cases: `rate-limited`, `auth-failed`, `payment-required`,
  `skipped-unconfigured`, `no-results` and others (`lib/health.py:27-43`); `classify_failure` tests 429 first,
  then 402, then 401 and 403 (`lib/http.py:697-735`), added by mvanhorn/last30days-skill#1124 (merged
  2026-09-09). The local copy is v3.18.4 (`.agents/skills/last30days/SKILL.md:3`) and still maps 402 to
  `auth-failed` (its `lib/http.py:466-478`), which is why this run's Reddit outcome reads `auth-failed` (seq 103-104).
- Sources: keyless (Hacker News Algolia, Reddit public and RSS, Polymarket, GitHub through `gh`, YouTube through
  `yt-dlp`, arxiv, digg and techmeme CLIs) map to `UNMETERED_ACCESS`; ScrapeCreators-backed (TikTok, Instagram,
  Threads, Pinterest, the Reddit backup) inherit the ScrapeCreators check; X through `bird` uses a browser
  `AUTH_TOKEN` and has no credit check; web grounding tries Brave, then Exa, Serper, Parallel (`--help`). Brave
  was not probed (gap).

**GitHub REST and GraphQL.**
- SDK: githubkit 0.16.1 `github.rest.rate_limit.get()` and `async_get()` wrap `GET /rate_limit`
  (`packages/githubkit-schemas-2022-11-28/githubkit_schemas/v2022_11_28/rest/rate_limit.py:41-73` at `5b299ef`,
  read with `git show`); rate errors are `PrimaryRateLimitExceeded` and `SecondaryRateLimitExceeded`
  (`OR/repos/githubkit/githubkit/exception.py:74-95`), decided in `githubkit/core.py:440-495`: on 403 or 429, a
  `retry-after` header means secondary; `x-ratelimit-remaining: 0` means primary unless the message says
  "secondary rate". GraphQL rate errors arrive as HTTP 200 with `errors[].type` `RATE_LIMIT` or `RATE_LIMITED`
  (yanyongyu/githubkit#271, 2026-01-08 to 2026-01-16). CLI: `gh api rate_limit`.
- Fields: `resources.core`, `search`, `code_search`, `graphql` (and others), each `{limit, used, remaining, reset}`
  (`OR/pages/gh-rest-rate-limit-endpoint.md:24-27, 49-55`; seq 4).
- Cost: free against the primary limit, counted against the secondary limit (`OR/pages/gh-rest-rate-limits.md:148`).
- Headers on normal calls: `x-ratelimit-limit`, `-remaining`, `-used`, `-reset`, `-resource`
  (`gh-rest-rate-limits.md:141-145`); headers win when they disagree with `/rate_limit` (line 154); exceeding
  gives 403 or 429 with remaining 0, secondary limits add `retry-after` (lines 166-169). Search allows 30
  requests per minute, code search 10 (`OR/pages/gh-rest-search.md:27`); GraphQL 5000 points per hour, and a
  primary overrun still returns 200 with an error (`OR/pages/gh-graphql-rate-limits.md:25, 198-201`).
- Live: the code_search bucket answered 403 "API rate limit exceeded" after two calls of this run in a fresh
  window (seq 152-154), and the next call showed `X-RateLimit-Used: 3` after one call of ours (seq 157,
  `OR/gh/probe/codesearch-l30-retry-headers.txt`): another agent shares `GITHUB_TOKEN`.

**webclaw.**
- Local CLI 0.6.23 extracts locally with no credits. Cloud fallback needs `WEBCLAW_API_KEY` (absent:
  `NOT_CONFIGURED`); cloud usage is dashboard-only; cloud returns 429 for request rate and 402 for credits
  (`OR/pages/webclaw-cloud.md:44-81`). `webclaw search` spends the caller's Serper key
  (`OR/repos/webclaw/crates/webclaw-server/src/routes/search.rs:1-4`), so it inherits the Serper check.

### 7.2 GitHub repository features and how a disabled feature shows up

- REST `GET /repos/{owner}/{repo}`: `has_issues`, `has_projects`, `has_wiki`, `has_pages`, `has_discussions`,
  `archived`, `disabled` (`OR/pages/gh-rest-repos.md:224-231`), and live responses now also carry
  `has_pull_requests` (`OR/gh/repos/*.json`). GraphQL `Repository`: `hasIssuesEnabled`, `hasDiscussionsEnabled`,
  `hasProjectsEnabled`, `hasPullRequestsEnabled`, `hasWikiEnabled`, `isArchived`, `isDisabled`
  (`OR/pages/gh-graphql-repos-reference.md:3916-3964`).
- Live feature reads (seq 71-83): discussions disabled on exa-labs/exa-py, exa-labs/exa-js,
  serpapi/serpapi-python, serpapi/serpapi-javascript, yanyongyu/githubkit, mvanhorn/last30days-skill; all
  enabled on firecrawl/firecrawl, upstash/context7, 0xMassi/webclaw, cli/cli; torvalds/linux has issues, PRs and
  discussions disabled. None archived or disabled.
- How a disabled feature appears: `search/issues` returns 200 and `total_count: 0` for `is:issue` and `is:pr`
  (seq 84-85); GraphQL `search(type: DISCUSSION)` gives `discussionCount: 0` and `repository.discussions.totalCount: 0`
  with no error (seq 88-89); `GET /repos/.../issues` gives `200 []` (seq 87); `GET /repos/.../discussions` gives
  410 "Discussions are disabled for this repo" (seq 90); `GET /repos/.../pulls` gives 404 (seq 91);
  `gh issue list` exits 1 with "the 'torvalds/linux' repository has disabled issues" (seq 86).
- Archived repositories are read-only but their issues and PRs stay searchable
  (`OR/pages/gh-archiving-repositories.md:34, 37`). A search whose `repo:` qualifier names an inaccessible
  repository fails with 422 "Validation Failed" (`OR/pages/gh-rest-search.md:98`), which maps to `NOT_FOUND`.
- Buckets: issue, PR and repository searches share `search` (30 per minute); code search uses `code_search`
  (10 per minute); discussion search uses `graphql` points (cost 1 per query here, seq 88-89); repository reads use
  `core` (5000 per hour).

### 7.3 What TR offers to port, and what not to

- Port: the enums (TR `schemas/enums.json:393-427` for `ProviderFetchStatus` and `ResearchFailureCode`,
  `:217-229` `ServiceCreditStatus`, `:454-466` `SearchTargetService`, `:53` `FEATURE_DISABLED` in `ErrorCode`),
  the `RepoCapabilities` record (TR `schemas/github_search.json:8-21`) and the pre-check order (TR
  `src/github_searcher/capabilities.py:16-34`, `search.py:693-760`), and the `SourceOutcome` envelope with its
  `control_canary` (TR `schemas/research_aggregator.json:26-61`).
- Do not port: `src/dependency_intel/credits.py:9-45` (key presence only; it even treats `SERP_API_KEY` as a
  Serper key, line 18); the after-the-fact mappings that turn 429 and GitHub 403 into `CREDITS_EXHAUSTED`
  (section 1, item 1) and Context7 404 into `NONE` (TR `context7.py:213-214`).
- Better source for the probe list than `credits.py`: TR `src/tr_module/plugin_doctor.py` has real
  probes (Firecrawl `get_credit_usage()` at 38-135, OpenRouter `/api/v1/auth/key` at 138-241, GitHub
  `/rate_limit` at 492-588 reading only `core`, line 542), but it spends paid canaries for Exa (318-396) and Serper
  (399-489) where Serper has a free `/account`, and it trusts `ctx7 whoami` (244-299).

### 7.4 Status model

Three closed enums plus two records (drafts: `OR/draft/schemas/research/provider-status.json`,
`OR/draft/schemas/research/preflight.json`; `check-jsonschema --check-metaschema` passes; `ajv` validates
`OR/draft/examples/result-2026-10-14.json` and `request.json` and rejects `bad-request.json`).

- `ProviderFetchStatus` (ported unchanged): `OK`, `EMPTY_VERIFIED`, `EMPTY_UNVERIFIED`, `DEGRADED`, `SKIPPED`, `ERROR`.
- `ResearchFailureCode`: TR's 16 (`NONE`, `CREDITS_EXHAUSTED`, `PREREQUISITE`, `HTTP_ERROR`, `INVALID_JSON`,
  `SHAPE_ERROR`, `PROVIDER_FAILURE`, `PROCESS_FAILED`, `TIMEOUT`, `REQUEST_FAILED`, `CREDENTIAL_INVALID`,
  `CANARY_FAILED`, `CANARY_EMPTY`, `NOT_FOUND`, `EMPTY_OUTPUT`, `OTHER`) plus:
  - `FEATURE_DISABLED` (from TR `ErrorCode`): a repository feature is off, or the provider's plan gates the
    feature (Exa tag `FEATURE_DISABLED`, Exa Websets 401 "Upgrade to a Pro plan", Firecrawl 403).
  - `RATE_LIMITED` (new): a short window is spent; retry at `reset` or after `Retry-After`. Distinct from
    `CREDITS_EXHAUSTED`, which needs a top-up, a budget change or the billing-period reset.
  - `NOT_CONFIGURED` (new): the credential is absent. `PREREQUISITE` narrows to a missing tool or runtime
    (no `ctx7`, no Python 3.12 for Last30Days, no `webclaw`), matching TR's `CREDENTIALS_NOT_CONFIGURED`
    split in `ServiceCreditStatus`.
- `ServiceCreditStatus` (ported unchanged) as `credit.state`: `QUOTA_AVAILABLE`, `QUOTA_EXHAUSTED_NEGATIVE_BALANCE`,
  `QUOTA_EXHAUSTED_ZERO_BALANCE`, `UNMETERED_ACCESS`, `CREDIT_CHECK_UNAVAILABLE`, `CREDENTIALS_NOT_CONFIGURED`.
- `CreditCheckMethod` (new) as `credit.method`: `ACCOUNT_API`, `CLI`, `RESPONSE_HEADERS`, `CANARY`,
  `KEY_PRESENCE_ONLY`, `NONE`.
- Records: `CreditState {state, method, remaining, limit, unit, resets_at}`, `RateLimitState {bucket, limit,
  remaining, reset_epoch_s, retry_after_s}`, `ProviderCheck`, `RepositoryCheck`, and the request and result.
  Provider ids stay lowercase to match `queries.jsonl` (D137); `queries.jsonl` rows reuse `status` and
  `failure_code` from the same file once CT-52's schema check exists.

Proposed D83 files (paths are new; D126 already uses `schemas/agent-protocol/**` for CT-59):
`schemas/research/provider-status.json` and `schemas/research/preflight.json`, both JSON Schema 2020-12, with
`$id`s under the repository URL so jsoncons can resolve them locally (D135).

### 7.5 Mapping table: provider response to code

Rows apply in order; the first match wins. "Skip" means `status: SKIPPED`; the provider is not called in stage 1.

| Provider | Observation | status | failure_code | credit.state |
|---|---|---|---|---|
| any | key variable absent | SKIPPED | NOT_CONFIGURED | CREDENTIALS_NOT_CONFIGURED |
| any | binary or runtime absent (`ctx7`, `firecrawl`, `gh`, `webclaw`, Python 3.12) | SKIPPED | PREREQUISITE | unchanged |
| any | connect or TLS failure; deadline passed | ERROR | REQUEST_FAILED; TIMEOUT | CREDIT_CHECK_UNAVAILABLE |
| any | 2xx body not JSON; JSON missing the expected field | ERROR | INVALID_JSON; SHAPE_ERROR | CREDIT_CHECK_UNAVAILABLE |
| firecrawl | credit-usage 200, `remainingCredits` < 0 / = 0 / below `min_remaining` | SKIPPED | CREDITS_EXHAUSTED | NEGATIVE / ZERO / QUOTA_AVAILABLE |
| firecrawl | 401; 402; 403; 429 with credits or quota in the body; other 429 | SKIPPED | CREDENTIAL_INVALID; CREDITS_EXHAUSTED; FEATURE_DISABLED; CREDITS_EXHAUSTED; RATE_LIMITED | |
| context7 | usage 200, `member.requests >= includedInPlan` on `free`, or `spendingLimitUsd` not null and `extraCostUsd >= spendingLimitUsd` | SKIPPED | CREDITS_EXHAUSTED | ZERO_BALANCE |
| context7 | 401 `invalid_api_key`; 402; 429 `Quota Exceeded` or `Retry-After` longer than one day; 429 `rate_limit_exceeded` | SKIPPED | CREDENTIAL_INVALID; CREDITS_EXHAUSTED; CREDITS_EXHAUSTED; RATE_LIMITED | |
| exa | no account check | OK | NONE | CREDIT_CHECK_UNAVAILABLE |
| exa | first call 401 `INVALID_API_KEY`; 402 `NO_MORE_CREDITS`, `*_BUDGET_EXCEEDED`; 403 `FEATURE_DISABLED`; 429 `RATE_LIMIT_EXCEEDED`; 503 `SERVICE_OVERLOADED` | ERROR (call) then SKIPPED (rest of run) | CREDENTIAL_INVALID; CREDITS_EXHAUSTED; FEATURE_DISABLED; RATE_LIMITED; PROVIDER_FAILURE | |
| exa | Websets 401 whose message says upgrade to a plan | SKIPPED (Websets only) | FEATURE_DISABLED | |
| serper | account 200, `balance <= 0` or below `min_remaining` | SKIPPED | CREDITS_EXHAUSTED | ZERO / NEGATIVE |
| serper | 401 or 403 "Unauthorized"; search `x-ratelimit-remaining: 0` | SKIPPED | CREDENTIAL_INVALID; RATE_LIMITED | |
| serpapi | account 200, `total_searches_left <= 0`; `this_hour_searches >= account_rate_limit_per_hour` | SKIPPED | CREDITS_EXHAUSTED; RATE_LIMITED | ZERO; QUOTA_AVAILABLE |
| serpapi | 401; 403 (account deleted); 429 "run out of searches"; other 429 | SKIPPED | CREDENTIAL_INVALID; CREDENTIAL_INVALID; CREDITS_EXHAUSTED; RATE_LIMITED | |
| scrapecreators | balance 200, `creditCount` (or `credits_remaining`) <= 0 | SKIPPED | CREDITS_EXHAUSTED | NEGATIVE / ZERO |
| scrapecreators | 402; 401 or 403 | SKIPPED | CREDITS_EXHAUSTED; CREDENTIAL_INVALID | |
| last30days | Python 3.12 absent; diagnose fails | SKIPPED | PREREQUISITE; PROCESS_FAILED | |
| last30days | ScrapeCreators exhausted while keyless sources remain | DEGRADED | CREDITS_EXHAUSTED | KEY_PRESENCE_ONLY method |
| github | `/rate_limit` bucket `remaining == 0` for the target (`search`, `code_search`, `graphql`) | SKIPPED (that bucket until `reset`) | RATE_LIMITED | QUOTA_AVAILABLE |
| github | 401 | SKIPPED | CREDENTIAL_INVALID | |
| github | 403 or 429 with `x-ratelimit-remaining: 0`, or with `retry-after`, or "secondary rate limit"; GraphQL 200 with `errors[].type` `RATE_LIMITED` or `RATE_LIMIT` | ERROR (call) | RATE_LIMITED | |
| github | repo read 404; search 422 on a `repo:` qualifier | SKIPPED (repo) | NOT_FOUND | |
| github | `has_issues` false; `has_pull_requests` false; `has_discussions` false; `disabled` true | SKIPPED (that target) | FEATURE_DISABLED | |
| github | `archived` true | OK (target), flag kept | NONE | |
| github | search 200 with `incomplete_results: true` | DEGRADED | TIMEOUT | |
| github | search 200 with 0 hits after a feature check and a control query with hits | EMPTY_VERIFIED | NONE | |
| webclaw | local binary present | OK | NONE | UNMETERED_ACCESS |
| webclaw | cloud needed, `WEBCLAW_API_KEY` absent; cloud 402; cloud 429 | SKIPPED (cloud) | NOT_CONFIGURED; CREDITS_EXHAUSTED; RATE_LIMITED | |

### 7.6 Decisions for the user

1. `archived`: keep searching archived repositories and record the flag (GitHub keeps their issues and PRs
   searchable, `OR/pages/gh-archiving-repositories.md:37`), amending D142's list, or keep D142 literal and skip.
2. Add `has_pull_requests` to D142's repository check (live on `torvalds/linux`, seq 81, 85, 91).
3. Whether the preflight may spend one paid canary when no account API exists (`allow_canary`, default false).
   This run did not need one for Exa; it spent one free refused Context7 call to capture the 429 shape (seq 49).
4. The age-key exposure and the breadth of the `codex_research` profile (section 11).

### 7.7 C++ unit design: `rsm-core research preflight`

Contract (D130, R9 verdict item 1): one JSON request on stdin, one JSON result on stdout, exit 0 when the result
was produced (whatever the provider codes), 2 for a refused request with a JSON reason, anything else for an
internal failure. Records and enums are plain aggregates and `enum class`es reflected by glaze with
`GLZ_REFLECTION26=1` (D135); jsoncons validates the request against `schemas/research/preflight.json` before
parsing (D135, R13). Namespace follows the existing `aggregated_research` (`include/aggregated_research/core.hpp`);
R9's `com::rsm` would rename it later.

Units, each within the five-file and about-300-line limit (`docs/agents/codex-task-orchestration.md:204`):

1. **P1 schema (lane, small).** `schemas/research/provider-status.json`, `schemas/research/preflight.json` and two
   example documents, checked by CT-52's `codegen:check` once it exists. Starts from `OR/draft/`.
2. **P2 classifier (cxx, pure, no I/O).** `include/aggregated_research/research/provider_status.hpp` (enums and
   records; replaced by #26's generated records when they land), `src/research/classify.cpp` with
   `classify(Provider, HttpObservation) -> ProviderCheck`, `classify_account(Provider, std::string_view body)`,
   `classify_repo(RepoFeatures, std::span<const SearchTarget>)`, and `tests/research/classify_test.cpp` over the
   fixtures below. Every row of table 7.5 becomes one test case.
3. **P3 transport and subcommand (cxx).** `src/research/preflight.cpp` runs one probe per provider and
   `src/cli/research_preflight.cpp` wires the subcommand. Interim HTTPS: `posix_spawn` of `/usr/bin/curl -sS
   -D <hdrfile> -K -` with the auth header written to the child's stdin pipe, so no key reaches `argv`
   (`POSIX_SPAWN_SETSID`, explicit minimal environment: `PATH`, `HOME`, `SSL_CERT_FILE`, plus the one key a CLI
   needs, as R13 section 7 and D140 keep children on `posix_spawn`). CLIs through the same spawn path:
   `firecrawl credits --json`, `gh api -i rate_limit`, `gh api repos/<o>/<r>`, `last30days.py --diagnose`,
   `webclaw --version`. The result scrubs `api_key`, `account_email`, `account_id` and any value equal to a
   configured key before it is written. Synchronous by default, as D140 keeps the bridge synchronous; the probes
   are independent, so a later `when_all` over them is the only async need.
4. **P4 native HTTPS (cxx, later).** After the D140 compile probe and R15's verdict on glaze networking, replace
   the curl child with Boost.Asio (single `io_context`, stdexec `asioexec` per D140) and Beast or glaze's Asio
   client; keep curl as the fallback when TLS setup fails.
5. **P5 bridge and wiring (lane).** CT-76's research tasks and the CT-81 frontier call `rsm-core research
   preflight` through `subprocess` or `$.process.run`, write one `stage: "preflight"` row per provider, and skip
   providers whose code is not `NONE`; `docs/agents/research-workflow.md` then points at the subcommand instead
   of the manual list (D142's "until then").

Tests and fixtures (one directory per provider under `tests/fixtures/research/preflight/`, each a pair
`<case>.headers.json` and `<case>.body`, copied from `OR/probe/` with the scrub applied):

| Provider | Live fixtures from this run | Doc-derived fixtures (synthetic, cite the page) |
|---|---|---|
| firecrawl | `pf-firecrawl-api.*` (negative balance), `pf-firecrawl-cli.json` | 402 and 429 bodies, `firecrawl-errors.md:36-51` |
| context7 | `pf-ctx7-usage.*` (free, exhausted), `canary-ctx7-search.*` (429 Quota Exceeded) | 429 `rate_limit_exceeded`, 401 `invalid_api_key`, `get-api-usage.md:115-128`; paid plan at spending limit, line 38-70 |
| exa | `exa/q01.*` (200 with `costDollars`), `pf-exa-websets-teams-me.*` (401 plan gate), `pf-exa-teams-me.*` (404) | 402 `NO_MORE_CREDITS`, 429 `RATE_LIMIT_EXCEEDED`, `exa-error-codes-admin.md:44-52, 66-76` |
| serper | `pf-serper.*` (account), `serper/s01.*` (search with `x-ratelimit-*`), `pf-serper-badkey-shape.*` (403) | exhausted balance: none (gap) |
| serpapi | `pf-serpapi.*` (account, scrubbed) | 429 "run out of searches", 401, `serpapi-status-errors.md:44-66` |
| scrapecreators | `pf-scrapecreators.*` (`creditCount` -7) | docs shape with `credits_remaining`, `scrapecreators-credit-balance.md:604-611` |
| github | `pf-gh-rate.txt`, `gh/repos/torvalds_linux.json`, `gh/repos/exa-labs_exa-py.json`, `gh/probe/*` (silent zeros, 410, 404), `gh/saved/l30-payment-required.json` (403 code_search) | GraphQL `RATE_LIMIT` error, githubkit#271 body |
| last30days | `local/last30days/diagnose.json`, `l30-run.err` (ScrapeCreators 402) | |
| webclaw | version line | cloud 402 and 429, `webclaw-cloud.md:47` |

The P3 test runs the subcommand with `PATH` pointing at stub `curl` and `gh` scripts that replay these fixtures,
so no test touches the network.

### 7.8 Place in the wave order

Inputs from `P/reviews/ccm-20261014/reprioritize-3/Q2-order-v2.md`: CT-52 (schema contract) at wave 10 (line
136), #26 (C++ records from the schemas) in the cxx slot of wave 16 (line 142), the filler #99 at wave 17 (line
143), CT-53 at 18 (line 144), CT-76a to CT-76d at waves 13, 15, 17 and 20 with "one strict research receipt
through the fnox research profile" at 20 (line 146), CT-81 at 39 (line 165). The `rsm-core` skeleton (R9's new
unit C1) and the D114 fourth reprioritization are not placed yet, so this placement is provisional:

- P1 right after CT-52, in a lane at wave 11 or 12 (two schema files and examples).
- P2 in the cxx slot of wave 17, displacing filler #99 to the next free filler slot; it needs C1 and #26's
  record generator, or hand-written records that #26 later replaces.
- P3 in the next free cxx slot before wave 20, so CT-76d's strict research receipt carries preflight codes.
- P4 after the D140 compile probe and R15, no earlier than the first free cxx slot after wave 20.
- P5 inside CT-76d (wave 20) for the tasks and CT-81 (wave 39) for the frontier. Until P3 lands the workflow
  keeps running the preflight by hand, as this run did.

## 8. Code examples found

| Repository | Path and lines | Commit | What it shows |
|---|---|---|---|
| firecrawl/firecrawl | `apps/python-sdk/firecrawl/v2/methods/usage.py:19-32` | `f4fdf7f` | `get_credit_usage()` over `/v2/team/credit-usage` |
| firecrawl/firecrawl | `apps/api/src/routes/v2.ts:456-460`, `apps/api/src/services/rate-limiter.ts:35` | `f4fdf7f` | credit check in the `account` bucket, 1000 per minute |
| firecrawl/firecrawl | `apps/python-sdk/firecrawl/v2/utils/error_handler.py:173-188` | `f4fdf7f` | 401, 402, 429 exception classes |
| firecrawl/cli | `src/index.ts:2634-2635`, `src/commands/credit-usage.ts:55, 154` | `0b4a091` | `credits` alias and exit behaviour |
| upstash/context7 | `packages/cli/src/commands/auth.ts:217-231` | `ef472a4` | `whoami` returns before any request for API keys |
| upstash/context7 | `packages/sdk/src/http/response.ts:13-33`, `packages/sdk/src/error/index.ts:11-32` | `ef472a4` | `RateLimit-*` and `Retry-After` captured on errors |
| upstash/context7 | `packages/mcp/src/lib/api.ts:60-63` | `ef472a4` | one message for both kinds of 429 |
| exa-labs/exa-py | `exa_py/api.py:510-526, 1688-1693` | `9d599f8` | `costDollars` parse; `ValueError` with status and body |
| serpapi/serpapi-python | `serpapi/core.py:165-186`, `serpapi/exceptions.py:22-35` | `827ebf4` | `account()` and `HTTPError.status_code` |
| yanyongyu/githubkit | `githubkit/core.py:440-495`, `githubkit/exception.py:74-95` | `5b299ef` | primary versus secondary rate-limit detection |
| mvanhorn/last30days-skill | `skills/last30days/scripts/lib/http.py:697-735`, `lib/health.py:27-43`, `lib/doctor.py:1838-1856` | `f4dff26` | outcome vocabulary, 429 then 402 then 401 ordering, no credit-spending probes |
| 0xMassi/webclaw | `crates/webclaw-server/src/routes/search.rs:1-4` | `3c32041` | search through the caller's Serper key |
| TR (local) | `src/tr_module/plugin_doctor.py:38-135, 244-299, 318-396, 399-489, 492-588` | n/a | working probes to port selectively |
| TR (local) | `src/github_searcher/search.py:693-760`, `capabilities.py:16-34` | n/a | feature pre-check before issue and discussion search |

## 9. Routes table

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| preflight | Firecrawl CLI and API | `fx firecrawl credits --json`; `fx http.py GET .../v2/team/credit-usage bearer:FIRECRAWL_API_KEY` | 0, 0 | n/a | yes (SKIPPED, CREDITS_EXHAUSTED) |
| preflight | Serper account | `fx http.py GET https://google.serper.dev/account header:X-API-KEY:SERPER_API_KEY` (x3), plus one keyless call | 0 | n/a | yes |
| preflight | SerpApi account | `fx http.py GET https://serpapi.com/account.json query:api_key:SERP_API_KEY` (x2) | 0 | n/a | yes |
| preflight | GitHub rate limit | `fx gh api -i rate_limit` | 0 | n/a | yes |
| preflight | Context7 | `fx ctx7 whoami`; `fx http.py GET .../api/v2/usage`; one refused canary on `/api/v2/libs/search` | 0, 0, 0 (HTTP 429) | n/a | yes (SKIPPED, CREDITS_EXHAUSTED) |
| preflight | Exa account endpoints | `fx http.py GET .../v0/teams/me` and `.../websets/v0/teams/me` | 0 (404, 401) | n/a | yes |
| preflight | ScrapeCreators | `fx http.py GET .../v1/account/credit-balance header:x-api-key:SCRAPECREATORS_API_KEY` (x2) | 0 | n/a | yes (SKIPPED) |
| preflight | Last30Days | `fx python3.12 last30days.py --diagnose` with `SSL_CERT_FILE=/etc/ssl/cert.pem` | 0 | n/a | yes (DEGRADED) |
| preflight | webclaw | `webclaw --version`; key name check | 0 | n/a | yes |
| preflight | GitHub repo features | `fx gh api repos/<owner>/<repo>` for 13 repositories | 0 each | n/a | yes |
| 1 | Exa | `fx exa_run.sh <id> "<query>"` (POST https://api.exa.ai/search, `numResults` 10, `type` auto), 12 queries | 0, HTTP 200 each | 10 each | yes |
| 1 | Context7 | not called after preflight | n/a | 0 | no (gap, quota until 2026-11-01) |
| 1 | Firecrawl | not called after preflight | n/a | 0 | no (gap, credits -128) |
| 1 | webclaw | `webclaw <url> -f markdown > OR/pages/<name>.md`, 40 pages | 0 (39), 1 (1) | 1 page each | yes |
| 1 | Serper | `fx http.py POST https://google.serper.dev/search`, 6 queries | 0, HTTP 200 each | 1 to 10 | yes |
| 1 | SerpApi | not needed after Serper | n/a | 0 | no |
| 1 | Last30Days | `fx python3.12 last30days.py "<topic>" --plan plan.json [--quick] --emit json --search reddit,hackernews,github --save-dir ""`, 2 runs | 0, 0 | 0, 6 | yes |
| 2 | git clones | `git clone --depth 1 --filter=blob:none [--sparse]`, 9 repositories | 0 each | n/a | yes |
| 2 | gh search issues and prs | `fx gh search issues|prs "<term>" --repo <r> --limit 15 --json ...`, 20 queries | 0 each | 0 to 15 | yes |
| 2 | gh issue and pr view | `fx gh issue view <n> -R <r> --json ...,comments`; `gh pr view`, 9 items | 0 each | 1 each | yes |
| 2 | GraphQL discussions | `fx gh api graphql search(type:DISCUSSION, query:"repo:<r> <term>")`, 6 called, 6 skipped as FEATURE_DISABLED | 0 each | 0 to 12 | yes |
| 2 | disabled-feature probes | `gh api search/issues`, `repos/.../issues`, `.../discussions`, `.../pulls`, `gh issue list`, GraphQL | 0 or 1 | 0 | yes |
| 2 | saved searches (reproduced) | `fx gh api -X GET search/code -f q="<query> repo:<r>" -F per_page=5 -F page=1`, 18 calls including controls | 0 (15), 1 (3, HTTP 403 rate limit) | 0 to 54 | yes |

## 10. Proposed saved-search rows

Shape as in `dev/saved-searches.toml` (not edited). Counts are from this run (seq 142-159).

```toml
# Provider credit preflight (research R16, decision D142, 2026-10-14)
[[search]]
id = "firecrawl-credit-usage"
query = "team/credit-usage"
repo = "firecrawl/firecrawl"                  # 19 hits today; control README 35
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "context7-ratelimit-headers"
query = "ratelimit-remaining"
repo = "upstash/context7"                     # 3 hits; control README 27
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "exa-py-cost-dollars"
query = "costDollars"
repo = "exa-labs/exa-py"                      # 11 hits; control README 3
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "serpapi-python-account"
query = "account.json"
repo = "serpapi/serpapi-python"               # 1 hit; control README 5
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "githubkit-rate-limit-classes"
query = "SecondaryRateLimitExceeded"
repo = "yanyongyu/githubkit"                  # 3 hits; control README 54
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "last30days-payment-required"
query = "PAYMENT_REQUIRED"
repo = "mvanhorn/last30days-skill"             # 21 hits; control README 33
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

# Watch rows: 0 hits today; a hit means the upstream added the behaviour
[[search]]
id = "exa-js-retry-after-watch"
query = "Retry-After"
repo = "exa-labs/exa-js"                      # 0 hits; control README 4
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "last30days-scrapecreators-balance-watch"
query = "credit-balance"
repo = "mvanhorn/last30days-skill"             # 0 hits; control README 33
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 11. Open gaps

- Context7 docs (stage 1) were not queried: the free quota is spent until 2026-11-01, with 20 bonus requests a
  day (seq 48-50). Firecrawl was not used for search or scrape (credits -128, seq 1, 51); webclaw and Serper
  covered both.
- Not observed live: Exa 402 and 429 bodies (docs only), Firecrawl 402 in this run (R13's routes table recorded
  one earlier today, `P/reviews/ccm-20261014/research5/R13-cxx-deps.md:302`), Serper's status for an exhausted
  balance (undocumented), ScrapeCreators billing of the balance call at a positive balance, and whether the
  Context7 usage call counts against the quota.
- Brave (Last30Days web backend) and the X `bird` backend were not checked; no credit endpoint was researched for
  them.
- One webclaw fetch failed (`scrapecreators.com/scrape-creators-credit-balance-api`, rc 1, seq 44); the docs page
  at `docs.scrapecreators.com` covered it.
- The shared `GITHUB_TOKEN` is consumed by other agents at the same time (seq 152-157), so a preflight snapshot
  of `code_search` can be stale within seconds; P3 must re-read `x-ratelimit-*` on every call, and a per-bucket
  host lock (CT-11) would help.
- Security incident (relay to the user): `env | cut -d= -f1` under the `codex_research` profile printed two lines
  that look like age secret keys (continuation lines of a multi-line variable) into this transcript; nothing was
  written to disk. Rotation of those age keys and narrowing the profile (it also exposes AWS and other unrelated
  secrets) are user decisions. Future runs list names with a tool that splits on NUL.
- Mirror hygiene: entering the `last30days-skill` clone made mise create a `.venv` there (removed; no repository
  code ran). Future runs use `git -C` and absolute paths and never `cd` into a clone.
- The local Last30Days copy (v3.18.4) misreports ScrapeCreators 402 as `auth-failed`; upstream 3.28.0 fixes it
  (#1124). Updating the copy is outside this run.
- Wave placement in 7.8 is provisional until the `rsm-core` skeleton (R9 C1) and the D114 order are placed.
- Nothing in the C++ design was compiled; it inherits R13's and R14's medium confidence on glaze, jsoncons,
  stdexec and Asio in both lanes.
