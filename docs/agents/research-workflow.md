# Research workflow

This document owns how research runs here. It answers one question: what evidence an open
technical fork needs before anyone decides it, and how a run gathers, records and reports that
evidence. Decisions are linked by id in `../../.planning/<PLAN_ID>/decisions.jsonl`.

## Rules

- Decide an open technical fork only from a report that followed both stages below (D100).
- Run the stages before trying any fallback or alternative approach (D106).
- Look for third-party tools, CLIs, libraries and SDKs before building anything; prefer OS
  built-ins, then Rust, C++, C or Zig tools (D107).
- Fetch pages with `webclaw <url> -f markdown`; the WebFetch tool stays unused.
- Write no key value anywhere: pass keys through the environment or a header read from it, and
  keep them off any command line you echo.
- Call providers only through the fnox profile below. The TR project
  (`<TR>`) has research scripts that fabricate
  output; leave them unrun.
- Make no GitHub writes (comments, reactions, issues) and start no `claude` session.
- A quota or auth failure becomes a log row and an open gap, never a silent skip.
- Cite every claim with a URL, an issue or PR number with its date, or `file:line`; label
  anything uncited UNVERIFIED.

## Preflight (D142)

Before stage 1, check each provider's credits through its API (the endpoint its SDK wraps)
or, where none exists, its CLI, and log one `stage: "preflight"` row per provider. A provider
with no credits, an invalid key or no key is skipped with its status code, not called and
left as a silent gap. Checks that work today (2026-10-14):

- Firecrawl: `firecrawl credits --json` (`remainingCredits`, `planCredits`).
- Serper: `GET https://google.serper.dev/account` with `X-API-KEY` (`balance`, `rateLimit`).
- SerpApi: `GET https://serpapi.com/account.json` (`plan_searches_left`).
- GitHub: `gh api rate_limit` (`search`, `code_search`, `graphql` remaining).
- Context7 (`ctx7 whoami` shows login only) and Exa (no balance endpoint found): no credit
  check is known yet; a failed call is classified after the fact.

Before any stage-2 issue, PR or discussion search on a repository, read
`gh api repos/<owner>/<repo>` and skip a disabled feature (`has_issues`, `has_pull_requests`,
`has_discussions`) with `FEATURE_DISABLED`: a disabled feature returns zero results with no error.
Archived repositories stay searchable and are not skipped (D147).

Status codes follow the TR project's schema enums, ported under D142:
`status` is one of `OK`, `EMPTY_VERIFIED`, `EMPTY_UNVERIFIED`, `DEGRADED`, `SKIPPED`, `ERROR`,
and `failure_code` one of `NONE`, `CREDITS_EXHAUSTED`, `CREDENTIAL_INVALID`, `PREREQUISITE`,
`FEATURE_DISABLED`, `HTTP_ERROR`, `TIMEOUT`, `NOT_FOUND`, `OTHER`. The C++ library takes this
check over once its research preflight unit lands (D112).

Never list the environment or print a secret under a credential profile (D146): no `env`,
`printenv`, `set`, `export -p` or `declare -x` inside `fnox ... exec`. Check a key one named
variable at a time (`[ -n "$EXA_API_KEY" ] && echo set || echo unset`).

## Stage 1: web and docs

Run every provider call under the fnox research profile. Keys present: `EXA_API_KEY`,
`CONTEXT7_API_KEY`, `FIRECRAWL_API_KEY`, `SERPER_API_KEY`, `SERP_API_KEY`, `GITHUB_TOKEN`,
`SCRAPECREATORS_API_KEY`.

```
fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults \
  --no-daemon --non-interactive exec -- <command>
```

Attempt and record every route:

1. Exa search API.
2. Context7 through the `ctx7` CLI.
3. Firecrawl through the `firecrawl` CLI. When it fails (it returned HTTP 402 on 2026-10-14),
   fall back to webclaw, then to Serper (`https://google.serper.dev/search`, key
   `SERPER_API_KEY`) or SerpApi (`https://serpapi.com/search.json`, key `SERP_API_KEY`).
4. Last30Days through `last30days.py`; read its `--help` first. The copy at
   `/Users/rmanaloto/agy-graphify-research/.agents/skills/last30days/scripts/last30days.py`
   needed `SSL_CERT_FILE=/etc/ssl/cert.pem` on 2026-10-14.

## Stage 2: GitHub, seeded by stage 1

Take every repository, issue or PR number, URL, API name and term stage 1 surfaced, and query
GitHub with `gh search issues`, `gh search prs`, `gh issue view --comments`, `gh pr view` and
`gh api graphql` (type `DISCUSSION`). Record the `seq` of the stage-1 row that named each
search when you choose it; never reconstruct it later.

Then run the saved-search route: read `dev/saved-searches.toml` and
`dev/collect_saved_search.py`. `./dev/mise run research:collect` writes into a tracked path,
so while another lane owns that path, reproduce the equivalent githubkit or `gh api
search/code` and `search/issues` queries read-only in the run's scratch directory. Give each a
control query with a known result, and propose new `[[search]]` rows (shape: the rows already
in `dev/saved-searches.toml`, each with a `[[search.control]]`) without editing the file.

Working commands from an earlier run:
`.planning/<PLAN_ID>/reviews/ccm-20261014/grill-facts/F4-pwf-worktree-pins.md`, section
"Routes".

## Offline mirror (D110)

Mirror every source into the untracked corpus `offline/research/<run id>/` (excluded through
`.git/info/exclude`; CT-08 moves the exclusion to `.gitignore`):

- Documentation pages: `webclaw <url> -f markdown > <file>.md`, with no page limit (D86).
- Repositories: `git clone --filter=blob:none`, or a full clone when you need history. Their
  code stays unrun.
- `manifest.json` lists every item with its source URL, local path, retrieval time in UTC,
  command shape without secrets, exit code, and SHA-256 for files or commit SHA for clones.

Base the deep analysis on the mirrored copies and cite each by local path as well as URL.

## Query log (D137)

Log every provider call, failed and quota-limited ones included, to
`offline/research/<run id>/queries.jsonl`, one JSON object per line with these keys:

- `seq`, and `stage` (`1`, `2` or `"local"`).
- `provider`: `exa`, `context7`, `firecrawl`, `webclaw`, `serper`, `serpapi`, `last30days`,
  `gh-issue-search`, `gh-pr-search`, `gh-issue-view`, `gh-pr-view`, `gh-graphql-discussion`,
  `gh-code-search-saved` or `git-clone`.
- `query`: the exact query text, URL or reference sent.
- `rc`, `http_status`, `hits`, and `top_results` (up to 5 `{title, url}`).
- `seeded_by`: for stage-2 rows, the `seq` of the stage-1 row whose result named the search.
- `used`: whether the report cites the result.
- `status` and `failure_code`: the preflight codes above, on every row.

## Report

The report path comes from the task. Sections in this order:

1. Verdict: a recommendation for the fork, with confidence and the evidence that decides it.
2. Queries sent to each tool, plugin or service (stage 1), exact text.
3. Results from each: hits, top results, and what was used.
4. GitHub issues, PRs and discussions searched (stage 2), each with the stage-1 row that
   seeded it.
5. Githubkit saved searches run (reproduced read-only with their controls) and proposed new
   rows.
6. Stage-2 GitHub and saved searches against the stage-1 results, as a seed-to-search map.
7. Findings with citations.
8. Code examples found: repository, path, and commit or permalink.
9. Routes table: stage, route, command shape without secrets, rc, hits, used or not.
10. Proposed saved-search rows.
11. Open gaps.

A run that cannot fill a section says why (for example a quota gap); it never omits the
section. Build sections 2 to 6 from `queries.jsonl`. A run that does not record them is fixed
before its findings are used (D137).

The run's summary artifact shows the same five log-built sections (2 to 6), built from
`queries.jsonl`.

## Watch loop (planned, ticket pending)

D138 adds a recurring watch over the saved-search rows in `dev/saved-searches.toml`. The
planned behaviour: a mise task run by launchd on a configurable schedule with minute
resolution and a default of one day; new results go to the claude-agent team
(`claude-team.md`), which proposes changes for the user to decide. No such task exists yet;
`./dev/mise tasks ls` lists it once it does. CT-81 is planned to automate the stage-1 and
stage-2 route (D106), and CT-76 imports the dotfiles research fan-out (ADR 0006).
