# R12c log: D137 query log and mirror for the agent team roster refresh

Research R12c, session ccm-20261014, 2026-10-14 (23:46Z) to 2026-10-15 (00:20Z). Companion to
`R12c-team-roster-refresh.md`; every section below is built from the query log by
`S/bin/sections.py full`. Read-only apart from the scratch directory: no tracked file in MP changed,
nothing was written to GitHub, no `claude` session was started and no key value was printed or
written.

Section numbers 2 to 6 match the report's; section 7 is the per-provider routes table.
Abbreviations as in the report. S = `/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/r12-refresh/`;
the log is `S/queries.jsonl`; the mirror is `S/offline/` with `S/offline/manifest.json` (322 items:
111 documentation pages, 51 GitHub threads, 14 clones, 9 local captures and 137 raw search
captures, each with a SHA-256 or commit). The task put the mirror in the scratchpad rather than
`MP/offline/research/<run id>/` (D110); the parent decides whether to move it.

## How the log was written

- `S/bin/run.py` makes one call, then appends one row under a file lock, so `seq` is the order of
  completion. Rows carry the D137 keys (`seq`, `stage`, `provider`, `query`, `rc`, `http_status`,
  `hits`, `top_results`, `seeded_by`, `used`, `status`, `failure_code`) plus `run: "R12c"`, `why`,
  `command` (shape only), `raw_file` and, where relevant, `mirror`, `all_urls`, `credit` or
  `repo_features`.
- Every provider call went through the fnox `codex_research` profile except webclaw and the public
  `git clone`s, which need no key.
- `seeded_by` holds the stage-1 `seq` that named the search, chosen when the call was planned.
  Two non-numeric values mark watch inputs: `"R12"` (threads, saved rows and clones R12 or R12b
  used) and `"R12b"` (R12b's proposed saved rows).
- `S/bin/fixup.py` appended the 9 local rows (seq 311-319) and one hand-run webclaw re-check
  (seq 320), and corrected statuses the runner could not classify; each corrected row has a
  `status_note`: Context7 quota (110, 111), Last30Days degraded (146, hits set to its 107 items),
  three HTTP 404s (92, 93, 141), a Reddit login wall (139), saved-search zeros verified against
  clones (266, 267, 272, 273) or not (275, 276), and one keyword zero with no control (186).
- `S/bin/mark_used.py` set `used` from the report's citations: a row is used when the report cites
  its seq, its mirrored file or its thread, or when a used row names it as seed (201 of 324).
- Provider names outside the workflow's list: `gh-raw` (raw file reads with `gh api`),
  `gh-issue-search-saved` (issue-search saved rows through `gh api search/issues`), `local`, and
  the preflight-only `github` and `scrapecreators`.
- The first 31 thread views failed (seq 161-180, 191-198, 206-208): gh 2.98 refuses `--comments`
  together with `--json`. They stay in the log with `status_note`; the runner was fixed and each
  view was rerun (seq 216-262).

## Summary

| Stage | Rows | Providers |
| --- | --- | --- |
| preflight | 22 | firecrawl, serper, serpapi, github (rate limit and 14 repositories), context7, exa, scrapecreators, last30days |
| 1 | 140 | exa 16, serper 6, serpapi 2, context7 2, firecrawl 1 (skipped), last30days 1, webclaw 110, gh-raw 2 |
| 2 | 153 | issue search 14, PR search 1, discussion 2 (one skipped, `FEATURE_DISABLED`), thread views 82 (31 failed and rerun), code-search saved 32, issue-search saved 8, clones 14 |
| local | 9 | Codex features and config keys, Claude settings keys, binary flag names, MP agent files, AGENTS.md sizes, Codex source excerpt |

Statuses: OK 275, ERROR 37 (31 view retries, 3 HTTP 404, 2 Context7 quota, 1 hand-run 404
re-check), EMPTY_VERIFIED 4, EMPTY_UNVERIFIED 4, SKIPPED 3, DEGRADED 1.

## 2. Queries sent to each tool, plugin or service (stage 1), exact text

### 2.0 Preflight (D142)

| seq | Provider | Check | rc | HTTP | Result | status | failure_code |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | firecrawl | firecrawl credits --json | 0 | None | {"remainingCredits": -128, "planCredits": 1000, "billingPeriodStart": "2026-10-11T17:36:55.821Z", "billingPeriodEnd": "… | SKIPPED | CREDITS_EXHAUSTED |
| 2 | serper | GET https://google.serper.dev/account | 0 | 200 | {"balance": 1287, "rateLimit": 5} | OK | NONE |
| 3 | serpapi | GET https://serpapi.com/account.json | 0 | 200 | {"plan_searches_left": 239, "searches_per_month": 250, "this_month_usage": 11, "plan_name": "Free Plan", "account_rate_… | OK | NONE |
| 4 | github | gh api rate_limit | 0 | 200 | {"core": {"remaining": 4890, "limit": 5000}, "search": {"remaining": 30, "limit": 30}, "code_search": {"remaining": 10,… | OK | NONE |
| 5 | context7 | ctx7 whoami (login only; output not kept) | 0 | None | No credit endpoint known (research-workflow.md Preflight); a failed call is classified after the fact. | OK | NONE |
| 6 | exa | key presence check, EXA_API_KEY (set or unset) | 0 | None | set | OK | NONE |
| 7 | scrapecreators | key presence check, SCRAPECREATORS_API_KEY (set or unset) | 0 | None | set | OK | NONE |
| 8 | last30days | last30days.py --diagnose | 0 | None |  | OK | NONE |
| 147 | github | gh api rate_limit | 0 | 200 | {"core": {"remaining": 4801, "limit": 5000}, "search": {"remaining": 30, "limit": 30}, "code_search": {"remaining": 10,… | OK | NONE |
| 148 | github | gh api repos/anthropics/claude-code | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 149 | github | gh api repos/openai/codex | 0 | 200 | {"has_issues": true, "has_discussions": true, "has_pull_requests": true, "archived": false} | OK | NONE |
| 150 | github | gh api repos/obra/superpowers | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 151 | github | gh api repos/wshobson/agents | 0 | 200 | {"has_issues": true, "has_discussions": true, "has_pull_requests": true, "archived": false} | OK | NONE |
| 152 | github | gh api repos/VoltAgent/awesome-claude-code-subagents | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 153 | github | gh api repos/anthropics/claude-plugins-official | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 154 | github | gh api repos/Yeachan-Heo/oh-my-claudecode | 0 | 200 | {"has_issues": true, "has_discussions": true, "has_pull_requests": true, "archived": false} | OK | NONE |
| 155 | github | gh api repos/monoes/monomind | 0 | 200 | {"has_issues": true, "has_discussions": true, "has_pull_requests": true, "archived": false} | OK | NONE |
| 156 | github | gh api repos/cdowin/agentic-sdlc | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 157 | github | gh api repos/novotnyllc/railyard | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 158 | github | gh api repos/bity-labs/tstack | 0 | 200 | {"has_issues": true, "has_discussions": false, "has_pull_requests": true, "archived": false} | OK | NONE |
| 159 | github | gh api repos/nyldn/claude-octopus | 0 | 200 | {"has_issues": true, "has_discussions": true, "has_pull_requests": true, "archived": false} | OK | NONE |
| 160 | github | gh api repos/mattpocock/skills | 0 | 200 | {"has_issues": true, "has_discussions": true, "has_pull_requests": true, "archived": false} | OK | NONE |

### exa (16 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 48 | Claude Code 2.1.300 release notes subagents agent effort model | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-10-07> |
| 54 | Claude Code subagent frontmatter fields memory color permissionMode hooks mcpServers skills background isolation | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-01> |
| 60 | Fable 5.1 versus Opus 5.5 code review quality and cost for subagents | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-14> |
| 65 | Haiku 5.5 and Sonnet 5.5 subagent routing benchmark effort level | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-14> |
| 70 | coding agent team critic planner verifier refuter blind tester roles that work | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-14> |
| 79 | AI agent for dependency upgrades: release notes intake, changelog review, Renovate PR triage | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-08-01> |
| 85 | OpenAI Codex CLI subagents custom agents toml configuration | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-08-01> |
| 90 | Codex CLI models list GPT Codex model reasoning effort levels | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-01> |
| 94 | Codex sandbox modes approval policy AGENTS.md skills MCP multi-agent orchestration | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-08-01> |
| 95 | C++26 static reflection P2996 with AI coding agents clang | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-07-01> |
| 96 | Claude Code agent teams teammates worktree isolation subagent Bash working directory | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-14> |
| 97 | Claude cybersecurity safeguards fallback Opus 4.8 security review agent | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-01> |
| 98 | Claude Code per-call effort parameter Agent tool xhigh max subagent | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-20> |
| 99 | Codex versus Claude Code subagents comparison reviewer implementer roles | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-01> |
| 100 | public text secret scanning guard before posting GitHub comments AI agent | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-08-01> |
| 101 | Claude Code dynamic workflows versus subagents versus agent teams when to use | fx keyhttp.sh exa <out> <body: query, numResults 10, type auto, startPublishedDate 2026-09-01> |

### context7 (2 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 110 | library claude code subagent frontmatter effort | fx ctx7 library <args> |
| 111 | library codex custom agents subagents config | fx ctx7 library <args> |

### firecrawl (1 call)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 9 | firecrawl search (stage-1 route 3) | not called |

### serper (6 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 102 | Claude Code 2.1.300 changelog | fx keyhttp.sh serper <out> <query> |
| 103 | site:github.com openai/codex subagents custom agents | fx keyhttp.sh serper <out> <query> |
| 104 | site:github.com anthropics/claude-code subagent effort frontmatter October 2026 | fx keyhttp.sh serper <out> <query> |
| 105 | Codex CLI agents max_threads max_depth custom agent model_reasoning_effort | fx keyhttp.sh serper <out> <query> |
| 106 | Fable 5.1 Opus 5.5 subagent reviewer cost per role | fx keyhttp.sh serper <out> <query> |
| 107 | claude code critic agent blind tester verifier subagent | fx keyhttp.sh serper <out> <query> |

### serpapi (2 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 108 | Codex subagents spawn_agent custom agents sandbox_mode developer_instructions | fx keyhttp.sh serpapi <out> <query> |
| 109 | Claude Code subagent skills preload mcpServers tools disallowedTools read-only reviewer | fx keyhttp.sh serpapi <out> <query> |

### last30days (1 call)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 146 | claude code and codex agent team roles, models and effort | SSL_CERT_FILE=/etc/ssl/cert.pem fx python3.13 -I last30days.py <topic> --plan <plan> --emit md --search <sources> --save-dir <dir> |

### webclaw (110 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 10 | https://code.claude.com/docs/llms.txt | webclaw -t 60 <url> -f markdown > <file> |
| 11 | https://developers.openai.com/codex/llms.txt | webclaw -t 60 <url> -f markdown > <file> |
| 12 | https://code.claude.com/docs/en/sub-agents.md | webclaw -t 60 <url> -f markdown > <file> |
| 13 | https://code.claude.com/docs/en/model-config.md | webclaw -t 60 <url> -f markdown > <file> |
| 14 | https://code.claude.com/docs/en/agent-teams.md | webclaw -t 60 <url> -f markdown > <file> |
| 15 | https://code.claude.com/docs/en/costs.md | webclaw -t 60 <url> -f markdown > <file> |
| 16 | https://code.claude.com/docs/en/workflows.md | webclaw -t 60 <url> -f markdown > <file> |
| 17 | https://code.claude.com/docs/en/best-practices.md | webclaw -t 60 <url> -f markdown > <file> |
| 18 | https://code.claude.com/docs/en/settings.md | webclaw -t 60 <url> -f markdown > <file> |
| 19 | https://code.claude.com/docs/en/settings-reference.md | webclaw -t 60 <url> -f markdown > <file> |
| 20 | https://code.claude.com/docs/en/env-vars.md | webclaw -t 60 <url> -f markdown > <file> |
| 21 | https://code.claude.com/docs/en/tools-reference.md | webclaw -t 60 <url> -f markdown > <file> |
| 22 | https://code.claude.com/docs/en/skills.md | webclaw -t 60 <url> -f markdown > <file> |
| 23 | https://code.claude.com/docs/en/worktrees.md | webclaw -t 60 <url> -f markdown > <file> |
| 24 | https://code.claude.com/docs/en/hooks.md | webclaw -t 60 <url> -f markdown > <file> |
| 25 | https://code.claude.com/docs/en/permission-modes.md | webclaw -t 60 <url> -f markdown > <file> |
| 26 | https://code.claude.com/docs/en/permissions.md | webclaw -t 60 <url> -f markdown > <file> |
| 27 | https://code.claude.com/docs/en/agents.md | webclaw -t 60 <url> -f markdown > <file> |
| 28 | https://code.claude.com/docs/en/agent-view.md | webclaw -t 60 <url> -f markdown > <file> |
| 29 | https://code.claude.com/docs/en/advisor.md | webclaw -t 60 <url> -f markdown > <file> |
| 30 | https://code.claude.com/docs/en/changelog.md | webclaw -t 60 <url> -f markdown > <file> |
| 31 | https://code.claude.com/docs/en/whats-new/index.md | webclaw -t 60 <url> -f markdown > <file> |
| 32 | https://code.claude.com/docs/en/whats-new/2026-w37.md | webclaw -t 60 <url> -f markdown > <file> |
| 33 | https://code.claude.com/docs/en/whats-new/2026-w36.md | webclaw -t 60 <url> -f markdown > <file> |
| 34 | https://code.claude.com/docs/en/claude-security.md | webclaw -t 60 <url> -f markdown > <file> |
| 35 | https://code.claude.com/docs/en/code-review.md | webclaw -t 60 <url> -f markdown > <file> |
| 36 | https://code.claude.com/docs/en/goal.md | webclaw -t 60 <url> -f markdown > <file> |
| 37 | https://code.claude.com/docs/en/plugins/mods/events.md | webclaw -t 60 <url> -f markdown > <file> |
| 38 | https://code.claude.com/docs/en/plugins/mods/api.md | webclaw -t 60 <url> -f markdown > <file> |
| 39 | https://code.claude.com/docs/en/agent-sdk/subagents.md | webclaw -t 60 <url> -f markdown > <file> |
| 40 | https://code.claude.com/docs/en/memory.md | webclaw -t 60 <url> -f markdown > <file> |
| 41 | https://code.claude.com/docs/en/routines.md | webclaw -t 60 <url> -f markdown > <file> |
| 42 | https://code.claude.com/docs/en/security-guidance.md | webclaw -t 60 <url> -f markdown > <file> |
| 43 | https://code.claude.com/docs/en/fast-mode.md | webclaw -t 60 <url> -f markdown > <file> |
| 44 | https://code.claude.com/docs/en/interactive-mode.md | webclaw -t 60 <url> -f markdown > <file> |
| 45 | https://platform.claude.com/docs/en/about-claude/models/overview | webclaw -t 60 <url> -f markdown > <file> |
| 46 | https://platform.claude.com/docs/en/about-claude/pricing | webclaw -t 60 <url> -f markdown > <file> |
| 47 | https://platform.claude.com/docs/en/build-with-claude/effort | webclaw -t 60 <url> -f markdown > <file> |
| 49 | https://platform.claude.com/docs/en/about-claude/models/choosing-a-model | webclaw -t 60 <url> -f markdown > <file> |
| 50 | https://www.anthropic.com/claude-opus-5-5 | webclaw -t 60 <url> -f markdown > <file> |
| 51 | https://claude.com/blog/claude-model-and-effort-level-in-claude-code | webclaw -t 60 <url> -f markdown > <file> |
| 52 | https://learn.chatgpt.com/docs/agent-configuration/subagents.md | webclaw -t 60 <url> -f markdown > <file> |
| 53 | https://learn.chatgpt.com/docs/agent-configuration/agents-md.md | webclaw -t 60 <url> -f markdown > <file> |
| 55 | https://learn.chatgpt.com/docs/agent-configuration/rules.md | webclaw -t 60 <url> -f markdown > <file> |
| 56 | https://learn.chatgpt.com/docs/agent-configuration/speed.md | webclaw -t 60 <url> -f markdown > <file> |
| 57 | https://learn.chatgpt.com/docs/agent-approvals-security.md | webclaw -t 60 <url> -f markdown > <file> |
| 58 | https://learn.chatgpt.com/docs/sandboxing.md | webclaw -t 60 <url> -f markdown > <file> |
| 59 | https://learn.chatgpt.com/docs/sandboxing/auto-review.md | webclaw -t 60 <url> -f markdown > <file> |
| 61 | https://learn.chatgpt.com/docs/permission-modes.md | webclaw -t 60 <url> -f markdown > <file> |
| 62 | https://learn.chatgpt.com/docs/permissions.md | webclaw -t 60 <url> -f markdown > <file> |
| 63 | https://learn.chatgpt.com/docs/config-file/config-reference.md | webclaw -t 60 <url> -f markdown > <file> |
| 64 | https://learn.chatgpt.com/docs/config-file/config-advanced.md | webclaw -t 60 <url> -f markdown > <file> |
| 66 | https://learn.chatgpt.com/docs/config-file/config-sample.md | webclaw -t 60 <url> -f markdown > <file> |
| 67 | https://learn.chatgpt.com/docs/models.md | webclaw -t 60 <url> -f markdown > <file> |
| 68 | https://learn.chatgpt.com/docs/model-selection.md | webclaw -t 60 <url> -f markdown > <file> |
| 69 | https://learn.chatgpt.com/docs/skills-and-plugins.md | webclaw -t 60 <url> -f markdown > <file> |
| 71 | https://learn.chatgpt.com/docs/build-skills.md | webclaw -t 60 <url> -f markdown > <file> |
| 72 | https://learn.chatgpt.com/docs/extend/mcp.md | webclaw -t 60 <url> -f markdown > <file> |
| 73 | https://learn.chatgpt.com/docs/hooks.md | webclaw -t 60 <url> -f markdown > <file> |
| 74 | https://learn.chatgpt.com/docs/environments/git-worktrees.md | webclaw -t 60 <url> -f markdown > <file> |
| 75 | https://learn.chatgpt.com/docs/code-review.md | webclaw -t 60 <url> -f markdown > <file> |
| 76 | https://learn.chatgpt.com/docs/codex/cli.md | webclaw -t 60 <url> -f markdown > <file> |
| 77 | https://learn.chatgpt.com/docs/non-interactive-mode.md | webclaw -t 60 <url> -f markdown > <file> |
| 78 | https://learn.chatgpt.com/docs/cyber-safety.md | webclaw -t 60 <url> -f markdown > <file> |
| 80 | https://learn.chatgpt.com/docs/pricing.md | webclaw -t 60 <url> -f markdown > <file> |
| 81 | https://learn.chatgpt.com/docs/whats-new.md | webclaw -t 60 <url> -f markdown > <file> |
| 82 | https://learn.chatgpt.com/docs/whats-new/october-5-9-2026.md | webclaw -t 60 <url> -f markdown > <file> |
| 83 | https://learn.chatgpt.com/docs/whats-new/september-28-october-2-2026.md | webclaw -t 60 <url> -f markdown > <file> |
| 84 | https://learn.chatgpt.com/docs/whats-new/devday-2026.md | webclaw -t 60 <url> -f markdown > <file> |
| 86 | https://learn.chatgpt.com/docs/long-running-work.md | webclaw -t 60 <url> -f markdown > <file> |
| 87 | https://learn.chatgpt.com/docs/feature-maturity.md | webclaw -t 60 <url> -f markdown > <file> |
| 88 | https://learn.chatgpt.com/docs/codex-sdk.md | webclaw -t 60 <url> -f markdown > <file> |
| 89 | https://learn.chatgpt.com/docs/security/security-review.md | webclaw -t 60 <url> -f markdown > <file> |
| 91 | https://learn.chatgpt.com/docs/codex-manual.md | webclaw -t 60 <url> -f markdown > <file> |
| 92 | https://learn.chatgpt.com/guides/build-ai-native-engineering-team.md | webclaw -t 60 <url> -f markdown > <file> |
| 93 | https://learn.chatgpt.com/guides/best-practices.md | webclaw -t 60 <url> -f markdown > <file> |
| 114 | https://changelogs.core-directive.com/v/2.1.296/e/relative-subagent-effort-lowerhigher-built-but-gated | webclaw -t 60 <url> -f markdown > <file> |
| 115 | https://changelogs.core-directive.com/v/2.1.290/e/subagent-effort-can-be-lowered-by-remote-value-tengu-harmon | webclaw -t 60 <url> -f markdown > <file> |
| 116 | https://changelogs.core-directive.com/v/2.1.300/e/workflow-agents-prompt-rewrite-hook-and-sandboxed-hand-back | webclaw -t 60 <url> -f markdown > <file> |
| 117 | https://meetzest.com/blog/best-model-for-coding | webclaw -t 60 <url> -f markdown > <file> |
| 118 | https://www.coderabbit.ai/blog/opus-5-5-model-review | webclaw -t 60 <url> -f markdown > <file> |
| 119 | https://www.qodo.ai/blog/which-llm-should-review-your-code/ | webclaw -t 60 <url> -f markdown > <file> |
| 120 | https://www.endorlabs.com/learn/opus-5-5-6x-cheaper-and-2x-faster-than-fable-5-1-but-memorization-keeps-it-off-the-top-spot | webclaw -t 60 <url> -f markdown > <file> |
| 121 | https://snorkel.ai/blog/opus-5-5-vs-opus-5-vs-fable-5-1-coding-benchmark-results/ | webclaw -t 60 <url> -f markdown > <file> |
| 122 | https://www.ovidius.ai/blog/claude-code-subagents-haiku-vs-sonnet-vs-opus-benchmarked | webclaw -t 60 <url> -f markdown > <file> |
| 123 | https://www.anthropic.com/claude-haiku-5-5 | webclaw -t 60 <url> -f markdown > <file> |
| 124 | https://sdd.sh/2026/10/claude-haiku-5-5-subagent-model-pricing-effort-levels/ | webclaw -t 60 <url> -f markdown > <file> |
| 125 | https://docs.cmd-ctrl.ai/blog/refute-dont-review | webclaw -t 60 <url> -f markdown > <file> |
| 126 | https://canberk.me/news/coding-agent-sub-agents-parallel-concurrency-study/ | webclaw -t 60 <url> -f markdown > <file> |
| 127 | https://mertsahin.ai/notes/two-agent-team/ | webclaw -t 60 <url> -f markdown > <file> |
| 128 | https://loreai.dev/compare/use-subagents-and-custom-agents-in-codex | webclaw -t 60 <url> -f markdown > <file> |
| 129 | https://automater.ai/intel/served-model-check-safety-fallbacks/ | webclaw -t 60 <url> -f markdown > <file> |
| 130 | https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conversation-with-opus-5-or-opus-5-5 | webclaw -t 60 <url> -f markdown > <file> |
| 131 | https://puppyip.com/en/resources/claude-code-subagent-effort-guide | webclaw -t 60 <url> -f markdown > <file> |
| 132 | https://aicatchup.com/comparisons/claude-code-subagents-vs-agent-teams-vs-workflows | webclaw -t 60 <url> -f markdown > <file> |
| 133 | https://devtocash.com/blog/2026-10-09-dependency-update-triage-agent-renovate-dependabot-auto-merge-breaking-changes | webclaw -t 60 <url> -f markdown > <file> |
| 134 | https://aident.ai/blog/dependency-upgrade-release-review | webclaw -t 60 <url> -f markdown > <file> |
| 135 | https://qiita.com/nogataka/items/6c073b442a6538b23344 | webclaw -t 60 <url> -f markdown > <file> |
| 136 | https://ai-tldr.dev/releases/openai-codex-cli-0-156-1/ | webclaw -t 60 <url> -f markdown > <file> |
| 137 | https://www.alphaxiv.org/abs/2610.08900 | webclaw -t 60 <url> -f markdown > <file> |
| 138 | https://savagesolutions.io/blog/defense-depth-before-ai-agent-publishes-open-web | webclaw -t 60 <url> -f markdown > <file> |
| 139 | https://www.reddit.com/r/claude/comments/1wy2ojw/switched_claude_code_from_fable_51_to_opus_55/ | webclaw -t 60 <url> -f markdown > <file> |
| 140 | https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-with-less-noise/ | webclaw -t 60 <url> -f markdown > <file> |
| 141 | https://learn.chatgpt.com/docs/changelog.md | webclaw -t 60 <url> -f markdown > <file> |
| 142 | https://developers.openai.com/api/docs/guides/model-selection.md | webclaw -t 60 <url> -f markdown > <file> |
| 143 | https://claudeissues.com/issue/101461-parallel-subagents-share-a-working-directory-with-no-warning-silently-corrupting | webclaw -t 60 <url> -f markdown > <file> |
| 144 | https://jeanfbrito.github.io/posts/benchmark-subagents-the-way-you-run-them/ | webclaw -t 60 <url> -f markdown > <file> |
| 145 | https://claude-me.com/en/practice/claude-code-agent-tool-effort-parameter-per-call-subagent/ | webclaw -t 60 <url> -f markdown > <file> |
| 310 | https://code.claude.com/docs/en/plugins/mods/reference.md | webclaw -t 60 <url> -f markdown > <file> |
| 320 | https://learn.chatgpt.com/guides/best-practices.md |  |

### gh-raw (2 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 112 | repos/anthropics/claude-code/contents/CHANGELOG.md | gh api -H 'Accept: application/vnd.github.raw' <path> |
| 113 | repos/openai/codex/contents/codex-rs/core/config.schema.json | gh api -H 'Accept: application/vnd.github.raw' <path> |

## 3. Results from each (stage 1)

| seq | Provider | rc | HTTP | Hits | status / failure_code | Top results | Used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | firecrawl | None | None | None | SKIPPED / CREDITS_EXHAUSTED |  | yes |
| 10 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/llms.txt | no |
| 11 | webclaw | 0 | None | 1 | OK / NONE | https://developers.openai.com/codex/llms.txt | yes |
| 12 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/sub-agents.md | yes |
| 13 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/model-config.md | yes |
| 14 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/agent-teams.md | yes |
| 15 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/costs.md | no |
| 16 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/workflows.md | no |
| 17 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/best-practices.md | no |
| 18 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/settings.md | no |
| 19 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/settings-reference.md | no |
| 20 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/env-vars.md | yes |
| 21 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/tools-reference.md | no |
| 22 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/skills.md | no |
| 23 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/worktrees.md | no |
| 24 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/hooks.md | no |
| 25 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/permission-modes.md | no |
| 26 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/permissions.md | no |
| 27 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/agents.md | no |
| 28 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/agent-view.md | no |
| 29 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/advisor.md | no |
| 30 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/changelog.md | no |
| 31 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/whats-new/index.md | no |
| 32 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/whats-new/2026-w37.md | no |
| 33 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/whats-new/2026-w36.md | no |
| 34 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/claude-security.md | no |
| 35 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/code-review.md | no |
| 36 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/goal.md | no |
| 37 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/plugins/mods/events.md | no |
| 38 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/plugins/mods/api.md | no |
| 39 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/agent-sdk/subagents.md | no |
| 40 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/memory.md | no |
| 41 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/routines.md | no |
| 42 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/security-guidance.md | no |
| 43 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/fast-mode.md | no |
| 44 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/interactive-mode.md | no |
| 45 | webclaw | 0 | None | 1 | OK / NONE | https://platform.claude.com/docs/en/about-claude/models/overview | no |
| 46 | webclaw | 0 | None | 1 | OK / NONE | https://platform.claude.com/docs/en/about-claude/pricing | no |
| 47 | webclaw | 0 | None | 1 | OK / NONE | https://platform.claude.com/docs/en/build-with-claude/effort | no |
| 48 | exa | 0 | 200 | 10 | OK / NONE | https://changelogs.core-directive.com/v/2.1.300/e/workflow-agents-prompt-rewrite-hook-and…; https://changelogs.core-directive.com/v/2.1.300/e/modelsettingsautocompactwindow-is-now-r…; https://aiagentnews.io/stories/claude-code-v2-1-300-adds-mod-prompt-hooks-agent-transcrip… | yes |
| 49 | webclaw | 0 | None | 1 | OK / NONE | https://platform.claude.com/docs/en/about-claude/models/choosing-a-model | no |
| 50 | webclaw | 0 | None | 1 | OK / NONE | https://www.anthropic.com/claude-opus-5-5 | no |
| 51 | webclaw | 0 | None | 1 | OK / NONE | https://claude.com/blog/claude-model-and-effort-level-in-claude-code | no |
| 52 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/subagents.md | yes |
| 53 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/agents-md.md | yes |
| 54 | exa | 0 | 200 | 10 | OK / NONE | https://skiln.co/blog/claude-code-subagents-config-reference-2026; https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-…; https://changelogs.core-directive.com/docs/change/13324 | no |
| 55 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/rules.md | yes |
| 56 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/speed.md | no |
| 57 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-approvals-security.md | no |
| 58 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/sandboxing.md | yes |
| 59 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/sandboxing/auto-review.md | no |
| 60 | exa | 0 | 200 | 10 | OK / NONE | https://meetzest.com/blog/best-model-for-coding; https://www.coderabbit.ai/blog/opus-5-5-model-review; https://jeanfbrito.github.io/posts/benchmark-subagents-the-way-you-run-them/ | yes |
| 61 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/permission-modes.md | no |
| 62 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/permissions.md | no |
| 63 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/config-file/config-reference.md | yes |
| 64 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/config-file/config-advanced.md | no |
| 65 | exa | 0 | 200 | 10 | OK / NONE | https://www.ovidius.ai/blog/claude-code-subagents-haiku-vs-sonnet-vs-opus-benchmarked; https://agent.nexus/blog/haiku-5-5-vs-sonnet-5-5; https://www.anthropic.com/claude-haiku-5-5 | yes |
| 66 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/config-file/config-sample.md | no |
| 67 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/models.md | yes |
| 68 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/model-selection.md | no |
| 69 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/skills-and-plugins.md | no |
| 70 | exa | 0 | 200 | 10 | OK / NONE | https://www.historyofvibecoding.com/multi-agent-systems/planner-coder-tester-reviewer-the…; https://www.cloudengineerlab.com/blog/build-a-multi-agent-system-planner-worker-reviewer; https://docs.cmd-ctrl.ai/blog/refute-dont-review | yes |
| 71 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/build-skills.md | yes |
| 72 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/extend/mcp.md | no |
| 73 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/hooks.md | yes |
| 74 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/environments/git-worktrees.md | yes |
| 75 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/code-review.md | no |
| 76 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/codex/cli.md | no |
| 77 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/non-interactive-mode.md | no |
| 78 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/cyber-safety.md | yes |
| 79 | exa | 0 | 200 | 10 | OK / NONE | https://devtocash.com/blog/2026-10-09-dependency-update-triage-agent-renovate-dependabot-…; https://skills.cat/skills/lightdash/lightdash/renovate-pr; https://devopsboys.com/blog/build-ai-dependency-upgrade-planner-claude-api-2026 | yes |
| 80 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/pricing.md | yes |
| 81 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/whats-new.md | no |
| 82 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/whats-new/october-5-9-2026.md | no |
| 83 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/whats-new/september-28-october-2-2026.md | no |
| 84 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/whats-new/devday-2026.md | no |
| 85 | exa | 0 | 200 | 10 | OK / NONE | https://github.com/openai/codex/discussions/6109; https://www.codex-docs.com/en/docs/agent-configuration/subagents; https://towardsdatascience.com/from-one-agent-to-a-team-understanding-codex-subagents/ | yes |
| 86 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/long-running-work.md | no |
| 87 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/feature-maturity.md | no |
| 88 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/codex-sdk.md | no |
| 89 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/security/security-review.md | no |
| 90 | exa | 0 | 200 | 10 | OK / NONE | https://github.com/openai/codex-plugin-cc/issues; https://losoft.dev/notes/read-a-coding-agents-model-list-without-logging-in/; https://vibeide.dev/blog/codex-models/ | no |
| 91 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/codex-manual.md | no |
| 92 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND | https://learn.chatgpt.com/guides/build-ai-native-engineering-team.md | yes |
| 93 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND | https://learn.chatgpt.com/guides/best-practices.md | yes |
| 94 | exa | 0 | 200 | 10 | OK / NONE | https://developers.openai.com/blog/codex-as-a-platform; https://aistackcurrent.com/agents/openai-codex/; https://daglo.ai/d/en/blog/codex-cli-setup-agents-md-guide-daglo | no |
| 95 | exa | 0 | 200 | 10 | OK / NONE | https://split-e.net/blog/reflection-angelscript-ai-agents/; https://github.com/wjakob/nanobind/discussions/1314; https://discourse.llvm.org/t/status-on-reflection/91207 | yes |
| 96 | exa | 0 | 200 | 10 | OK / NONE | https://claudeissues.com/issue/98307-worktree-isolation-in-a-background-session-blocks-su…; https://changelogs.core-directive.com/docs/c/claude-code-20261002T223702Z; https://claudeissues.com/issue/97495-worktree-isolated-subagents-launched-from-a-worktree… | yes |
| 97 | exa | 0 | 200 | 10 | OK / NONE | https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conver…; https://www.anthropic.com/claude-opus-5-5; https://claudeissues.com/issue/97687-sub-agents-requesting-model-opus-silently-continue-o… | yes |
| 98 | exa | 0 | 200 | 10 | OK / NONE | https://claude-me.com/en/practice/claude-code-agent-tool-effort-parameter-per-call-subage…; https://claudeissues.com/issue/98391-feature-per-call-effort-parameter-on-the-agent-tool; https://changelogs.core-directive.com/docs/change/13324 | yes |
| 99 | exa | 0 | 200 | 10 | OK / NONE | https://writingsbylala.com/guide/how-i-use-my-claude-code-and-codex/; https://loreai.dev/compare/use-subagents-and-custom-agents-in-codex; https://www.zarifautomates.com/blog/subagents-and-parallel-work-with-coding-agents | yes |
| 100 | exa | 0 | 200 | 10 | OK / NONE | https://github.cnmirror.space/anthropics/claude-code-action/pull/1693; https://dev.to/holistis/a-github-comment-can-steal-your-secrets-i-found-22-repositories-w…; https://labs.cloudsecurityalliance.org/research/csa-research-note-ai-coding-agent-ci-prom… | yes |
| 101 | exa | 0 | 200 | 10 | OK / NONE | https://aicatchup.com/comparisons/claude-code-subagents-vs-agent-teams-vs-workflows; https://botnet.com/resources/fleet-claude-code-parallel-agents-botnet; https://www.devventa.com/ai-coding-assistants/claude-code-dynamic-workflows | no |
| 102 | serper | 0 | 200 | 10 | OK / NONE | https://code.claude.com/docs/en/changelog; https://github.com/anthropics/claude-code/releases; https://www.reddit.com/r/ClaudeAI/comments/1qvgdc5/claude_code_v21262130_what_changed/ | no |
| 103 | serper | 0 | 200 | 10 | OK / NONE | https://github.com/openai/codex/discussions/6109; https://github.com/openai/codex/issues/15250; https://github.com/topics/codex-subagents | yes |
| 104 | serper | 0 | 200 | 10 | OK / NONE | https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md; https://github.com/rphlmr/claude-config; https://github.com/luongnv89/claude-howto/blob/main/04-subagents/README.md | yes |
| 105 | serper | 0 | 200 | 10 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/subagents; https://community.openai.com/t/model-aware-task-delegation-for-subagents/1381671; https://www.morphllm.com/codex-multi-agent | yes |
| 106 | serper | 0 | 200 | 10 | OK / NONE | https://www.anthropic.com/claude-opus-5-5; https://www.reddit.com/r/claude/comments/1wy2ojw/switched_claude_code_from_fable_51_to_op…; https://www.youtube.com/watch?v=5kF_pt9EjPo&xstg=CAMSBhUDzO3xHw%3D%3D | no |
| 107 | serper | 0 | 200 | 10 | OK / NONE | https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents; https://www.reddit.com/r/ClaudeAI/comments/1mi59yk/we_prepared_a_collection_of_claude_cod…; https://www.youtube.com/watch?v=MbKUeufUZIY | no |
| 108 | serpapi | 0 | 200 | 8 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/subagents; https://github.com/openai/codex/issues/15250; https://community.openai.com/t/restoring-subagent-roles-model-and-reasoning-in-multi-agen… | no |
| 109 | serpapi | 0 | 200 | 9 | OK / NONE | https://code.claude.com/docs/en/sub-agents; https://ed-burton.medium.com/claude-skills-vs-agents-vs-mcp-f2121c3350cb; https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp | no |
| 110 | context7 | 1 | 429 | None | ERROR / CREDITS_EXHAUSTED |  | yes |
| 111 | context7 | 1 | 429 | None | ERROR / CREDITS_EXHAUSTED |  | yes |
| 112 | gh-raw | 0 | None | 1 | OK / NONE |  | yes |
| 113 | gh-raw | 0 | None | 1 | OK / NONE |  | no |
| 114 | webclaw | 0 | None | 1 | OK / NONE | https://changelogs.core-directive.com/v/2.1.296/e/relative-subagent-effort-lowerhigher-bu… | yes |
| 115 | webclaw | 0 | None | 1 | OK / NONE | https://changelogs.core-directive.com/v/2.1.290/e/subagent-effort-can-be-lowered-by-remot… | yes |
| 116 | webclaw | 0 | None | 1 | OK / NONE | https://changelogs.core-directive.com/v/2.1.300/e/workflow-agents-prompt-rewrite-hook-and… | no |
| 117 | webclaw | 0 | None | 1 | OK / NONE | https://meetzest.com/blog/best-model-for-coding | yes |
| 118 | webclaw | 0 | None | 1 | OK / NONE | https://www.coderabbit.ai/blog/opus-5-5-model-review | yes |
| 119 | webclaw | 0 | None | 1 | OK / NONE | https://www.qodo.ai/blog/which-llm-should-review-your-code/ | yes |
| 120 | webclaw | 0 | None | 1 | OK / NONE | https://www.endorlabs.com/learn/opus-5-5-6x-cheaper-and-2x-faster-than-fable-5-1-but-memo… | yes |
| 121 | webclaw | 0 | None | 1 | OK / NONE | https://snorkel.ai/blog/opus-5-5-vs-opus-5-vs-fable-5-1-coding-benchmark-results/ | no |
| 122 | webclaw | 0 | None | 1 | OK / NONE | https://www.ovidius.ai/blog/claude-code-subagents-haiku-vs-sonnet-vs-opus-benchmarked | yes |
| 123 | webclaw | 0 | None | 1 | OK / NONE | https://www.anthropic.com/claude-haiku-5-5 | yes |
| 124 | webclaw | 0 | None | 1 | OK / NONE | https://sdd.sh/2026/10/claude-haiku-5-5-subagent-model-pricing-effort-levels/ | yes |
| 125 | webclaw | 0 | None | 1 | OK / NONE | https://docs.cmd-ctrl.ai/blog/refute-dont-review | yes |
| 126 | webclaw | 0 | None | 1 | OK / NONE | https://canberk.me/news/coding-agent-sub-agents-parallel-concurrency-study/ | yes |
| 127 | webclaw | 0 | None | 1 | OK / NONE | https://mertsahin.ai/notes/two-agent-team/ | yes |
| 128 | webclaw | 0 | None | 1 | OK / NONE | https://loreai.dev/compare/use-subagents-and-custom-agents-in-codex | yes |
| 129 | webclaw | 0 | None | 1 | OK / NONE | https://automater.ai/intel/served-model-check-safety-fallbacks/ | yes |
| 130 | webclaw | 0 | None | 1 | OK / NONE | https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conver… | yes |
| 131 | webclaw | 0 | None | 1 | OK / NONE | https://puppyip.com/en/resources/claude-code-subagent-effort-guide | no |
| 132 | webclaw | 0 | None | 1 | OK / NONE | https://aicatchup.com/comparisons/claude-code-subagents-vs-agent-teams-vs-workflows | no |
| 133 | webclaw | 0 | None | 1 | OK / NONE | https://devtocash.com/blog/2026-10-09-dependency-update-triage-agent-renovate-dependabot-… | yes |
| 134 | webclaw | 0 | None | 1 | OK / NONE | https://aident.ai/blog/dependency-upgrade-release-review | yes |
| 135 | webclaw | 0 | None | 1 | OK / NONE | https://qiita.com/nogataka/items/6c073b442a6538b23344 | no |
| 136 | webclaw | 0 | None | 1 | OK / NONE | https://ai-tldr.dev/releases/openai-codex-cli-0-156-1/ | no |
| 137 | webclaw | 0 | None | 1 | OK / NONE | https://www.alphaxiv.org/abs/2610.08900 | yes |
| 138 | webclaw | 0 | None | 1 | OK / NONE | https://savagesolutions.io/blog/defense-depth-before-ai-agent-publishes-open-web | yes |
| 139 | webclaw | 0 | None | 0 | EMPTY_UNVERIFIED / OTHER | https://www.reddit.com/r/claude/comments/1wy2ojw/switched_claude_code_from_fable_51_to_op… | no |
| 140 | webclaw | 0 | None | 1 | OK / NONE | https://github.blog/ai-and-ml/githubs-model-for-secret-detection-finding-more-secrets-wit… | no |
| 141 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND | https://learn.chatgpt.com/docs/changelog.md | yes |
| 142 | webclaw | 0 | None | 1 | OK / NONE | https://developers.openai.com/api/docs/guides/model-selection.md | no |
| 143 | webclaw | 0 | None | 1 | OK / NONE | https://claudeissues.com/issue/101461-parallel-subagents-share-a-working-directory-with-n… | no |
| 144 | webclaw | 0 | None | 1 | OK / NONE | https://jeanfbrito.github.io/posts/benchmark-subagents-the-way-you-run-them/ | no |
| 145 | webclaw | 0 | None | 1 | OK / NONE | https://claude-me.com/en/practice/claude-code-agent-tool-effort-parameter-per-call-subage… | no |
| 146 | last30days | 0 | None | 107 | DEGRADED / CREDITS_EXHAUSTED | https://x.com/tekari0/status/2105999486007074975; https://x.com/mirku21/status/2109388663822123043; https://github.com/cdowin/agentic-sdlc/issues/159 | yes |
| 310 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/plugins/mods/reference.md | yes |
| 320 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND |  | yes |

## 4. GitHub issues, PRs and discussions searched (stage 2)

| seq | Provider | Query or thread | rc | Hits | status | Seeded by | Top results or state | Used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 161 | gh-pr-view | anthropics/claude-code#97687 | 1 | None | ERROR | 97 |  | no |
| 162 | gh-pr-view | anthropics/claude-code#91209 | 1 | None | ERROR | 97 |  | no |
| 163 | gh-pr-view | anthropics/claude-code#98898 | 1 | None | ERROR | 104 |  | no |
| 164 | gh-pr-view | anthropics/claude-code#101461 | 1 | None | ERROR | 96 |  | no |
| 165 | gh-pr-view | anthropics/claude-code#98307 | 1 | None | ERROR | 96 |  | no |
| 166 | gh-pr-view | anthropics/claude-code#97495 | 1 | None | ERROR | 96 |  | no |
| 167 | gh-pr-view | anthropics/claude-code#98391 | 1 | None | ERROR | 98 |  | no |
| 168 | gh-pr-view | anthropics/claude-code#75432 | 1 | None | ERROR | R12 |  | no |
| 169 | gh-pr-view | anthropics/claude-code#92533 | 1 | None | ERROR | R12 |  | no |
| 170 | gh-pr-view | anthropics/claude-code#100701 | 1 | None | ERROR | R12 |  | no |
| 171 | gh-pr-view | anthropics/claude-code#92660 | 1 | None | ERROR | R12 |  | no |
| 172 | gh-pr-view | anthropics/claude-code#100082 | 1 | None | ERROR | R12 |  | no |
| 173 | gh-pr-view | anthropics/claude-code#82252 | 1 | None | ERROR | R12 |  | no |
| 174 | gh-pr-view | anthropics/claude-code#88886 | 1 | None | ERROR | R12 |  | no |
| 175 | gh-pr-view | anthropics/claude-code#98528 | 1 | None | ERROR | R12 |  | no |
| 176 | gh-pr-view | anthropics/claude-code#100347 | 1 | None | ERROR | R12 |  | no |
| 177 | gh-pr-view | anthropics/claude-code#100154 | 1 | None | ERROR | R12 |  | no |
| 178 | gh-pr-view | anthropics/claude-code#100830 | 1 | None | ERROR | R12 |  | no |
| 179 | gh-pr-view | anthropics/claude-code#85592 | 1 | None | ERROR | R12 |  | no |
| 180 | gh-pr-view | anthropics/claude-code#81852 | 1 | None | ERROR | R12 |  | no |
| 181 | gh-issue-search | subagent model repo:anthropics/claude-code created:>=2026-10-12 | 0 | 20 | OK | 97 | https://github.com/anthropics/claude-code/issues/102007; https://github.com/anthropics/claude-code/issues/101688 | yes |
| 182 | gh-issue-search | subagent effort repo:anthropics/claude-code created:>=2026-10-12 | 0 | 12 | OK | 98 | https://github.com/anthropics/claude-code/issues/102156; https://github.com/anthropics/claude-code/issues/101814 | yes |
| 183 | gh-issue-search | agent frontmatter repo:anthropics/claude-code created:>=2026-10-10 | 0 | 5 | OK | 12 | https://github.com/anthropics/claude-code/issues/101285; https://github.com/anthropics/claude-code/issues/101240 | yes |
| 184 | gh-issue-search | autoCompactWindow repo:anthropics/claude-code | 0 | 20 | OK | 112 | https://github.com/anthropics/claude-code/issues/93901; https://github.com/anthropics/claude-code/issues/90347 | no |
| 185 | gh-issue-search | Opus 4.8 subagent repo:anthropics/claude-code | 0 | 20 | OK | 97 | https://github.com/anthropics/claude-code/issues/100082; https://github.com/anthropics/claude-code/issues/98387 | yes |
| 186 | gh-issue-search | agent definitions hot reload repo:anthropics/claude-code created:>=2026-10-01 | 0 | 0 | EMPTY_UNVERIFIED | R12 |  | no |
| 187 | gh-issue-search | worktree isolation subagent repo:anthropics/claude-code created:>=2026-10-10 | 0 | 8 | OK | 96 | https://github.com/anthropics/claude-code/issues/101887; https://github.com/anthropics/claude-code/issues/101834 | yes |
| 188 | gh-issue-search | CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL repo:anthropics/claude-code | 0 | 1 | OK | 48 | https://github.com/anthropics/claude-code/issues/63693 | no |
| 189 | gh-issue-search | teammate effort repo:anthropics/claude-code updated:>=2026-10-13 | 0 | 4 | OK | R12 | https://github.com/anthropics/claude-code/issues/102057; https://github.com/anthropics/claude-code/issues/77298 | no |
| 190 | gh-graphql-discussion | repo:anthropics/claude-code subagent effort model | None | None | SKIPPED | 98 |  | no |
| 191 | gh-pr-view | openai/codex#42665 | 1 | None | ERROR | 85 |  | no |
| 192 | gh-pr-view | openai/codex#32587 | 1 | None | ERROR | 103 |  | no |
| 193 | gh-pr-view | openai/codex#32027 | 1 | None | ERROR | 105 |  | no |
| 194 | gh-pr-view | openai/codex#44637 | 1 | None | ERROR | 129 |  | no |
| 195 | gh-pr-view | openai/codex#15250 | 1 | None | ERROR | 103 |  | no |
| 196 | gh-pr-view | openai/codex#14039 | 1 | None | ERROR | 103 |  | no |
| 197 | gh-pr-view | openai/codex#34745 | 1 | None | ERROR | 103 |  | no |
| 198 | gh-pr-view | openai/codex#18988 | 1 | None | ERROR | 103 |  | no |
| 199 | gh-issue-search | custom agent sandbox_mode repo:openai/codex | 0 | 20 | OK | 52 | https://github.com/openai/codex/issues/45482; https://github.com/openai/codex/issues/39714 | yes |
| 200 | gh-issue-search | subagent reasoning effort repo:openai/codex created:>=2026-09-15 | 0 | 20 | OK | 52 | https://github.com/openai/codex/issues/53516; https://github.com/openai/codex/issues/49195 | yes |
| 201 | gh-issue-search | default_subagent_model repo:openai/codex | 0 | 13 | OK | 52 | https://github.com/openai/codex/issues/49195; https://github.com/openai/codex/issues/45790 | no |
| 202 | gh-issue-search | spawn_agent model repo:openai/codex created:>=2026-09-15 | 0 | 20 | OK | 63 | https://github.com/openai/codex/issues/49736; https://github.com/openai/codex/issues/46087 | yes |
| 203 | gh-issue-search | subagent read-only repo:openai/codex | 0 | 20 | OK | 52 | https://github.com/openai/codex/issues/40278; https://github.com/openai/codex/issues/32684 | yes |
| 204 | gh-pr-search | custom agent repo:openai/codex created:>=2026-09-15 | 0 | 6 | OK | 52 | https://github.com/openai/codex/pull/51500; https://github.com/openai/codex/pull/50727 | no |
| 205 | gh-graphql-discussion | repo:openai/codex custom agents subagents | 0 | 7 | OK | 85 | https://github.com/openai/codex/discussions/46658; https://github.com/openai/codex/discussions/31203 | no |
| 206 | gh-pr-view | cdowin/agentic-sdlc#159 | 1 | None | ERROR | 146 |  | no |
| 207 | gh-pr-view | novotnyllc/railyard#70 | 1 | None | ERROR | 146 |  | no |
| 208 | gh-pr-view | bity-labs/tstack#81 | 1 | None | ERROR | 146 |  | no |
| 216 | gh-issue-view | anthropics/claude-code#97687 | 0 | 1 | OK | 97 | OPEN created 2026-09-27 updated 2026-09-27 comments 0 | yes |
| 218 | gh-issue-view | anthropics/claude-code#91209 | 0 | 1 | OK | 97 | OPEN created 2026-09-01 updated 2026-09-01 comments 1 | yes |
| 219 | gh-issue-view | anthropics/claude-code#98898 | 0 | 1 | OK | 104 | OPEN created 2026-10-02 updated 2026-10-10 comments 2 | yes |
| 220 | gh-issue-view | anthropics/claude-code#101461 | 0 | 1 | OK | 96 | OPEN created 2026-10-12 updated 2026-10-12 comments 1 | yes |
| 222 | gh-issue-view | anthropics/claude-code#98307 | 0 | 1 | OK | 96 | OPEN created 2026-09-30 updated 2026-10-06 comments 1 | yes |
| 225 | gh-issue-view | anthropics/claude-code#97495 | 0 | 1 | OK | 96 | OPEN created 2026-09-26 updated 2026-09-26 comments 0 | yes |
| 227 | gh-issue-view | anthropics/claude-code#98391 | 0 | 1 | OK | 98 | OPEN created 2026-09-30 updated 2026-10-08 comments 1 | yes |
| 228 | gh-issue-view | anthropics/claude-code#75432 | 0 | 1 | OK | R12 | OPEN created 2026-07-07 updated 2026-10-04 comments 1 | yes |
| 229 | gh-issue-view | anthropics/claude-code#92533 | 0 | 1 | OK | R12 | OPEN created 2026-09-06 updated 2026-10-04 comments 4 | yes |
| 230 | gh-issue-view | anthropics/claude-code#100701 | 0 | 1 | OK | R12 | OPEN created 2026-10-09 updated 2026-10-09 comments 0 | yes |
| 232 | gh-issue-view | anthropics/claude-code#92660 | 0 | 1 | OK | R12 | OPEN created 2026-09-07 updated 2026-10-12 comments 1 | yes |
| 233 | gh-issue-view | anthropics/claude-code#100082 | 0 | 1 | OK | R12 | OPEN created 2026-10-06 updated 2026-10-08 comments 1 | yes |
| 234 | gh-issue-view | anthropics/claude-code#82252 | 0 | 1 | OK | R12 | OPEN created 2026-07-29 updated 2026-09-04 comments 2 | yes |
| 235 | gh-issue-view | anthropics/claude-code#88886 | 0 | 1 | OK | R12 | OPEN created 2026-08-22 updated 2026-09-24 comments 5 | yes |
| 237 | gh-issue-view | anthropics/claude-code#98528 | 0 | 1 | OK | R12 | OPEN created 2026-09-30 updated 2026-09-30 comments 0 | yes |
| 239 | gh-issue-view | anthropics/claude-code#100347 | 0 | 1 | OK | R12 | OPEN created 2026-10-07 updated 2026-10-07 comments 1 | yes |
| 241 | gh-issue-view | anthropics/claude-code#100154 | 0 | 1 | OK | R12 | OPEN created 2026-10-07 updated 2026-10-07 comments 0 | yes |
| 243 | gh-issue-view | anthropics/claude-code#100830 | 0 | 1 | OK | R12 | OPEN created 2026-10-09 updated 2026-10-13 comments 1 | yes |
| 245 | gh-issue-view | anthropics/claude-code#85592 | 0 | 1 | OK | R12 | OPEN created 2026-08-10 updated 2026-09-19 comments 4 | yes |
| 247 | gh-issue-view | anthropics/claude-code#81852 | 0 | 1 | OK | R12 | OPEN created 2026-07-28 updated 2026-10-07 comments 1 | yes |
| 249 | gh-issue-view | openai/codex#42665 | 0 | 1 | OK | 85 | OPEN created 2026-09-04 updated 2026-09-13 comments 2 | yes |
| 250 | gh-issue-view | openai/codex#32587 | 0 | 1 | OK | 103 | OPEN created 2026-07-12 updated 2026-07-29 comments 4 | yes |
| 251 | gh-issue-view | openai/codex#32027 | 0 | 1 | OK | 105 | OPEN created 2026-07-10 updated 2026-10-13 comments 2 | yes |
| 253 | gh-issue-view | openai/codex#44637 | 0 | 1 | OK | 129 | OPEN created 2026-09-10 updated 2026-09-10 comments 1 | yes |
| 254 | gh-issue-view | openai/codex#15250 | 0 | 1 | OK | 103 | CLOSED created 2026-03-20 updated 2026-08-05 comments 16 | yes |
| 255 | gh-issue-view | openai/codex#14039 | 0 | 1 | OK | 103 | CLOSED created 2026-03-09 updated 2026-10-13 comments 17 | yes |
| 257 | gh-issue-view | openai/codex#34745 | 0 | 1 | OK | 103 | OPEN created 2026-07-22 updated 2026-07-22 comments 0 | yes |
| 258 | gh-issue-view | openai/codex#18988 | 0 | 1 | OK | 103 | OPEN created 2026-04-22 updated 2026-08-11 comments 2 | yes |
| 259 | gh-issue-view | cdowin/agentic-sdlc#159 | 0 | 1 | OK | 146 | CLOSED created 2026-10-08 updated 2026-10-08 comments 4 | yes |
| 260 | gh-issue-view | novotnyllc/railyard#70 | 0 | 1 | OK | 146 | MERGED created 2026-09-29 updated 2026-09-29 comments 9 | yes |
| 262 | gh-issue-view | bity-labs/tstack#81 | 0 | 1 | OK | 146 | OPEN created 2026-10-08 updated 2026-10-12 comments 10 | yes |
| 279 | gh-issue-view | anthropics/claude-code#101887 | 0 | 1 | OK | 187 | OPEN created 2026-10-13 updated 2026-10-13 comments 0 | yes |
| 280 | gh-issue-view | anthropics/claude-code#101519 | 0 | 1 | OK | 181 | OPEN created 2026-10-12 updated 2026-10-12 comments 0 | yes |
| 281 | gh-issue-view | anthropics/claude-code#102096 | 0 | 1 | OK | 183 | OPEN created 2026-10-14 updated 2026-10-14 comments 0 | yes |
| 283 | gh-issue-view | anthropics/claude-code#101169 | 0 | 1 | OK | 183 | CLOSED created 2026-10-11 updated 2026-10-11 comments 0 | yes |
| 284 | gh-issue-view | anthropics/claude-code#101650 | 0 | 1 | OK | 181 | OPEN created 2026-10-12 updated 2026-10-13 comments 2 | yes |
| 285 | gh-issue-view | anthropics/claude-code#98387 | 0 | 1 | OK | 185 | OPEN created 2026-09-30 updated 2026-09-30 comments 0 | yes |
| 286 | gh-issue-view | anthropics/claude-code#91923 | 0 | 1 | OK | 185 | OPEN created 2026-09-03 updated 2026-09-03 comments 1 | yes |
| 287 | gh-issue-view | anthropics/claude-code#101943 | 0 | 1 | OK | 181 | OPEN created 2026-10-14 updated 2026-10-14 comments 0 | yes |
| 289 | gh-issue-view | anthropics/claude-code#101240 | 0 | 1 | OK | 183 | OPEN created 2026-10-11 updated 2026-10-11 comments 1 | yes |
| 290 | gh-issue-view | openai/codex#45482 | 0 | 1 | OK | 199 | OPEN created 2026-09-14 updated 2026-09-14 comments 0 | yes |
| 291 | gh-issue-view | openai/codex#52809 | 0 | 1 | OK | 199 | OPEN created 2026-10-10 updated 2026-10-10 comments 0 | no |
| 292 | gh-issue-view | openai/codex#33244 | 0 | 1 | OK | 199 | OPEN created 2026-07-15 updated 2026-10-05 comments 5 | yes |
| 294 | gh-issue-view | openai/codex#40130 | 0 | 1 | OK | 199 | OPEN created 2026-08-22 updated 2026-09-08 comments 6 | no |
| 295 | gh-issue-view | openai/codex#52887 | 0 | 1 | OK | 199 | OPEN created 2026-10-10 updated 2026-10-10 comments 1 | yes |
| 296 | gh-issue-view | openai/codex#53516 | 0 | 1 | OK | 200 | OPEN created 2026-10-13 updated 2026-10-13 comments 0 | no |
| 297 | gh-issue-view | openai/codex#49736 | 0 | 1 | OK | 202 | OPEN created 2026-09-30 updated 2026-09-30 comments 0 | yes |
| 299 | gh-issue-view | openai/codex#46704 | 0 | 1 | OK | 202 | OPEN created 2026-09-19 updated 2026-09-19 comments 0 | yes |
| 300 | gh-issue-view | openai/codex#47779 | 0 | 1 | OK | 203 | OPEN created 2026-09-24 updated 2026-09-24 comments 2 | yes |
| 301 | gh-issue-view | openai/codex#45553 | 0 | 1 | OK | 202 | OPEN created 2026-09-15 updated 2026-09-15 comments 2 | yes |
| 302 | gh-issue-view | openai/codex#53374 | 0 | 1 | OK | 203 | OPEN created 2026-10-12 updated 2026-10-13 comments 2 | no |

## 5. Saved searches run (reproduced read-only with their controls)

| seq | Saved row | Role | Query sent | Page | rc | HTTP | total_count | status | Seeded by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 209 | official-agent-effort-xhigh | query | xhigh path:plugins/claude-security/agents repo:anthropics/claude-plugins-official | 1 | 0 | 200 | 6 | OK | R12 |
| 211 | official-agent-effort-xhigh | query | xhigh path:plugins/claude-security/agents repo:anthropics/claude-plugins-official | 2 | 0 | 200 | 6 | OK | R12 |
| 213 | official-agent-effort-xhigh | control (expected_min 1) | README repo:anthropics/claude-plugins-official | 1 | 0 | 200 | 61 | OK | R12 |
| 217 | superpowers-model-selection | query | "Model Selection" repo:obra/superpowers | 1 | 0 | 200 | 13 | OK | R12 |
| 224 | superpowers-model-selection | query | "Model Selection" repo:obra/superpowers | 2 | 0 | 200 | 13 | OK | R12 |
| 231 | superpowers-model-selection | control (expected_min 1) | README repo:obra/superpowers | 1 | 0 | 200 | 30 | OK | R12 |
| 236 | wshobson-fable-tier | query | "model: fable" repo:wshobson/agents | 1 | 0 | 200 | 6 | OK | R12 |
| 246 | wshobson-fable-tier | query | "model: fable" repo:wshobson/agents | 2 | 0 | 200 | 6 | OK | R12 |
| 252 | wshobson-fable-tier | control (expected_min 1) | README repo:wshobson/agents | 1 | 0 | 200 | 75 | OK | R12 |
| 256 | voltagent-effort | query | effort repo:VoltAgent/awesome-claude-code-subagents | 1 | 0 | 200 | 8 | OK | R12 |
| 261 | voltagent-effort | query | effort repo:VoltAgent/awesome-claude-code-subagents | 2 | 0 | 200 | 8 | OK | R12 |
| 265 | voltagent-effort | control (expected_min 1) | README repo:VoltAgent/awesome-claude-code-subagents | 1 | 0 | 200 | 17 | OK | R12 |
| 266 | superpowers-dispatch-effort | query | "effort:" path:skills/subagent-driven-development repo:obra/superpowers | 1 | 0 | 200 | 0 | EMPTY_VERIFIED | R12b |
| 267 | superpowers-dispatch-effort | query | "effort:" path:skills/subagent-driven-development repo:obra/superpowers | 2 | 0 | 200 | 0 | EMPTY_VERIFIED | R12b |
| 268 | superpowers-dispatch-effort | control (expected_min 1) | README repo:obra/superpowers | 1 | 0 | 200 | 30 | OK | R12 |
| 269 | monomind-served-model-receipt | query | unexpected_models repo:monoes/monomind | 1 | 0 | 200 | 4 | OK | R12b |
| 270 | monomind-served-model-receipt | query | unexpected_models repo:monoes/monomind | 2 | 0 | 200 | 4 | OK | R12b |
| 271 | monomind-served-model-receipt | control (expected_min 1) | README repo:monoes/monomind | 1 | 0 | 200 | 270 | OK | R12 |
| 272 | omc-agent-effort | query | "effort:" path:agents repo:Yeachan-Heo/oh-my-claudecode | 1 | 0 | 200 | 0 | EMPTY_VERIFIED | R12 |
| 273 | omc-agent-effort | query | "effort:" path:agents repo:Yeachan-Heo/oh-my-claudecode | 2 | 0 | 200 | 0 | EMPTY_VERIFIED | R12 |
| 274 | omc-agent-effort | control (expected_min 1) | README repo:Yeachan-Heo/oh-my-claudecode | 1 | 0 | 200 | 138 | OK | R12 |
| 275 | official-agent-effort | query | effort path:agents repo:anthropics/claude-plugins-official | 1 | 0 | 200 | 0 | EMPTY_UNVERIFIED | R12 |
| 276 | official-agent-effort | query | effort path:agents repo:anthropics/claude-plugins-official | 2 | 0 | 200 | 0 | EMPTY_UNVERIFIED | R12 |
| 277 | official-agent-effort | control (expected_min 1) | README repo:anthropics/claude-plugins-official | 1 | 0 | 200 | 61 | OK | R12 |
| 278 | codex-subagent-defaults | query | default_subagent_reasoning_effort repo:openai/codex | 1 | 0 | 200 | 9 | OK | 52 |
| 282 | codex-subagent-defaults | query | default_subagent_reasoning_effort repo:openai/codex | 2 | 0 | 200 | 9 | OK | 52 |
| 288 | codex-subagent-defaults | control (expected_min 1) | README repo:openai/codex | 1 | 0 | 200 | 167 | OK | R12 |
| 293 | cc-changelog-autocompactwindow | query | autoCompactWindow repo:anthropics/claude-code | 1 | 0 | 200 | 1 | OK | 112 |
| 298 | cc-changelog-autocompactwindow | query | autoCompactWindow repo:anthropics/claude-code | 2 | 0 | 200 | 1 | OK | 112 |
| 303 | cc-changelog-autocompactwindow | control (expected_min 1) | README repo:anthropics/claude-code | 1 | 0 | 200 | 42 | OK | R12 |
| 304 | cc-subagent-hot-reload-issues | query | subagent hot reload repo:anthropics/claude-code | 1 | 0 | 200 | 49 | OK | R12 |
| 305 | cc-subagent-hot-reload-issues | control (expected_min 1) | agent repo:anthropics/claude-code | 1 | 0 | 200 | 23148 | OK | R12 |
| 306 | cc-teammate-effort-issues | query | effort teammate repo:anthropics/claude-code | 1 | 0 | 200 | 100 | OK | R12 |
| 307 | cc-teammate-effort-issues | control (expected_min 1) | agent repo:anthropics/claude-code | 1 | 0 | 200 | 23148 | OK | R12 |
| 308 | codex-custom-agent-sandbox-issues | query | custom agent sandbox repo:openai/codex | 1 | 0 | 200 | 658 | OK | 52 |
| 309 | codex-custom-agent-sandbox-issues | control (expected_min 1) | agent repo:openai/codex | 1 | 0 | 200 | 11028 | OK | 52 |
| 321 | codex-role-overrides | query | AgentRoleOverrides repo:openai/codex | 1 | 0 | 200 | 1 | OK | 319 |
| 322 | codex-role-overrides | control (expected_min 1) | README repo:openai/codex | 1 | 0 | 200 | 167 | OK | 319 |
| 323 | codex-custom-agent-readonly-issues | query | custom agent sandbox_mode read-only repo:openai/codex | 1 | 0 | 200 | 120 | OK | 199 |
| 324 | codex-custom-agent-readonly-issues | control (expected_min 1) | agent repo:openai/codex | 1 | 0 | 200 | 11029 | OK | 199 |

### Clones re-read (stage 2)

| seq | Repository | Commit | Commit date | rc | Seeded by |
| --- | --- | --- | --- | --- | --- |
| 210 | https://github.com/anthropics/skills.git | dbd4588f9e10 | 2026-10-09T18:45:49Z | 0 | R12 |
| 212 | https://github.com/JuliusBrussee/caveman.git | d262ab388295 | 2026-10-13T18:08:08Z | 0 | R12 |
| 214 | https://github.com/nyldn/claude-octopus.git | 87efa2214733 | 2026-10-14T05:58:09-04:00 | 0 | R12 |
| 215 | https://github.com/anthropics/claude-plugins-community.git | 06ec7b6a0a82 | 2026-10-13T13:29:09-07:00 | 0 | R12 |
| 221 | https://github.com/anthropics/claude-plugins-official.git | c2bdb427efe8 | 2026-10-14T14:13:54-04:00 | 0 | R12 |
| 223 | https://github.com/anthropics/cwc-long-running-agents.git | ad107a974bce | 2026-05-12T17:54:24-07:00 | 0 | R12 |
| 226 | https://github.com/mattpocock/skills.git | 49dd158d1076 | 2026-10-09T11:56:49+01:00 | 0 | R12 |
| 238 | https://github.com/Yeachan-Heo/oh-my-claudecode.git | 44c27308912c | 2026-10-14T13:20:05+09:00 | 0 | R12 |
| 240 | https://github.com/obra/superpowers.git | bb92a7774141 | 2026-10-09T17:28:04-07:00 | 0 | R12 |
| 242 | https://github.com/ennio-datatide/ultrapowers.git | c6bcb5d7afad | 2026-09-11T19:07:29+02:00 | 0 | R12 |
| 244 | https://github.com/VoltAgent/awesome-claude-code-subagents.git | 408d3c9eee2d | 2026-10-11T11:20:37+03:00 | 0 | R12 |
| 248 | https://github.com/wshobson/agents.git | 46891e7e60da | 2026-10-04T16:42:51-04:00 | 0 | R12 |
| 263 | https://github.com/openai/codex.git | 4ca84a106966 | 2026-10-15T00:00:57Z | 0 | 52 |
| 264 | https://github.com/cdowin/agentic-sdlc.git | 6012c296acce | 2026-10-13T15:14:34-04:00 | 0 | 146 |

## 6. Seed-to-search map (stage-1 row to stage-2 calls)

| Seed | What the seed named | Stage-2 calls (seq: query) |
| --- | --- | --- |
| 12 | webclaw seq 12: https://code.claude.com/docs/en/sub-agents.md | 183: agent frontmatter repo:anthropics/claude-code created:… |
| 48 | exa seq 48: Claude Code 2.1.300 release notes subagents agent effort model | 188: CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL repo:anthropics/cl… |
| 52 | webclaw seq 52: https://learn.chatgpt.com/docs/agent-configuration/subagents.md | 199: custom agent sandbox_mode repo:openai/codex; 200: subagent reasoning effort repo:openai/codex created:>=…; 201: default_subagent_model repo:openai/codex; 203: subagent read-only repo:openai/codex; 204: custom agent repo:openai/codex created:>=2026-09-15; 263: https://github.com/openai/codex.git; 278: default_subagent_reasoning_effort repo:openai/codex; 282: default_subagent_reasoning_effort repo:openai/codex; 308: custom agent sandbox repo:openai/codex; 309: agent repo:openai/codex |
| 63 | webclaw seq 63: https://learn.chatgpt.com/docs/config-file/config-reference.md | 202: spawn_agent model repo:openai/codex created:>=2026-09-… |
| 85 | exa seq 85: OpenAI Codex CLI subagents custom agents toml configuration | 205: repo:openai/codex custom agents subagents; 249: openai/codex#42665 |
| 96 | exa seq 96: Claude Code agent teams teammates worktree isolation subagent Bash wo… | 187: worktree isolation subagent repo:anthropics/claude-cod…; 220: anthropics/claude-code#101461; 222: anthropics/claude-code#98307; 225: anthropics/claude-code#97495 |
| 97 | exa seq 97: Claude cybersecurity safeguards fallback Opus 4.8 security review age… | 181: subagent model repo:anthropics/claude-code created:>=2…; 185: Opus 4.8 subagent repo:anthropics/claude-code; 216: anthropics/claude-code#97687; 218: anthropics/claude-code#91209 |
| 98 | exa seq 98: Claude Code per-call effort parameter Agent tool xhigh max subagent | 182: subagent effort repo:anthropics/claude-code created:>=…; 190: repo:anthropics/claude-code subagent effort model; 227: anthropics/claude-code#98391 |
| 103 | serper seq 103: site:github.com openai/codex subagents custom agents | 250: openai/codex#32587; 254: openai/codex#15250; 255: openai/codex#14039; 257: openai/codex#34745; 258: openai/codex#18988 |
| 104 | serper seq 104: site:github.com anthropics/claude-code subagent effort frontmatter Oc… | 219: anthropics/claude-code#98898 |
| 105 | serper seq 105: Codex CLI agents max_threads max_depth custom agent model_reasoning_e… | 251: openai/codex#32027 |
| 112 | gh-raw seq 112: repos/anthropics/claude-code/contents/CHANGELOG.md | 184: autoCompactWindow repo:anthropics/claude-code; 293: autoCompactWindow repo:anthropics/claude-code; 298: autoCompactWindow repo:anthropics/claude-code |
| 129 | webclaw seq 129: https://automater.ai/intel/served-model-check-safety-fallbacks/ | 253: openai/codex#44637 |
| 146 | last30days seq 146: claude code and codex agent team roles, models and effort | 259: cdowin/agentic-sdlc#159; 260: novotnyllc/railyard#70; 262: bity-labs/tstack#81; 264: https://github.com/cdowin/agentic-sdlc.git |
| 181 | gh-issue-search seq 181: subagent model repo:anthropics/claude-code created:>=2026-10-12 | 280: anthropics/claude-code#101519; 284: anthropics/claude-code#101650; 287: anthropics/claude-code#101943 |
| 183 | gh-issue-search seq 183: agent frontmatter repo:anthropics/claude-code created:>=2026-10-10 | 281: anthropics/claude-code#102096; 283: anthropics/claude-code#101169; 289: anthropics/claude-code#101240 |
| 185 | gh-issue-search seq 185: Opus 4.8 subagent repo:anthropics/claude-code | 285: anthropics/claude-code#98387; 286: anthropics/claude-code#91923 |
| 187 | gh-issue-search seq 187: worktree isolation subagent repo:anthropics/claude-code created:>=202… | 279: anthropics/claude-code#101887 |
| 199 | gh-issue-search seq 199: custom agent sandbox_mode repo:openai/codex | 290: openai/codex#45482; 291: openai/codex#52809; 292: openai/codex#33244; 294: openai/codex#40130; 295: openai/codex#52887; 323: custom agent sandbox_mode read-only repo:openai/codex; 324: agent repo:openai/codex |
| 200 | gh-issue-search seq 200: subagent reasoning effort repo:openai/codex created:>=2026-09-15 | 296: openai/codex#53516 |
| 202 | gh-issue-search seq 202: spawn_agent model repo:openai/codex created:>=2026-09-15 | 297: openai/codex#49736; 299: openai/codex#46704; 301: openai/codex#45553 |
| 203 | gh-issue-search seq 203: subagent read-only repo:openai/codex | 300: openai/codex#47779; 302: openai/codex#53374 |
| 319 | local seq 319: sed of codex-rs/core/src/agent/role.rs and child_config.rs at clone H… | 321: AgentRoleOverrides repo:openai/codex; 322: README repo:openai/codex |
| R12 | R12/R12b watch inputs (threads, saved rows, clones) | 186: agent definitions hot reload repo:anthropics/claude-co…; 189: teammate effort repo:anthropics/claude-code updated:>=…; 209: xhigh path:plugins/claude-security/agents repo:anthrop…; 210: https://github.com/anthropics/skills.git; 211: xhigh path:plugins/claude-security/agents repo:anthrop…; 212: https://github.com/JuliusBrussee/caveman.git; 213: README repo:anthropics/claude-plugins-official; 214: https://github.com/nyldn/claude-octopus.git; 215: https://github.com/anthropics/claude-plugins-community…; 217: "Model Selection" repo:obra/superpowers; 221: https://github.com/anthropics/claude-plugins-official.…; 223: https://github.com/anthropics/cwc-long-running-agents.…; 224: "Model Selection" repo:obra/superpowers; 226: https://github.com/mattpocock/skills.git; 228: anthropics/claude-code#75432; 229: anthropics/claude-code#92533; 230: anthropics/claude-code#100701; 231: README repo:obra/superpowers; 232: anthropics/claude-code#92660; 233: anthropics/claude-code#100082; 234: anthropics/claude-code#82252; 235: anthropics/claude-code#88886; 236: "model: fable" repo:wshobson/agents; 237: anthropics/claude-code#98528; 238: https://github.com/Yeachan-Heo/oh-my-claudecode.git; 239: anthropics/claude-code#100347; 240: https://github.com/obra/superpowers.git; 241: anthropics/claude-code#100154; 242: https://github.com/ennio-datatide/ultrapowers.git; 243: anthropics/claude-code#100830; 244: https://github.com/VoltAgent/awesome-claude-code-subag…; 245: anthropics/claude-code#85592; 246: "model: fable" repo:wshobson/agents; 247: anthropics/claude-code#81852; 248: https://github.com/wshobson/agents.git; 252: README repo:wshobson/agents; 256: effort repo:VoltAgent/awesome-claude-code-subagents; 261: effort repo:VoltAgent/awesome-claude-code-subagents; 265: README repo:VoltAgent/awesome-claude-code-subagents; 268: README repo:obra/superpowers; 271: README repo:monoes/monomind; 272: "effort:" path:agents repo:Yeachan-Heo/oh-my-claudecode; 273: "effort:" path:agents repo:Yeachan-Heo/oh-my-claudecode; 274: README repo:Yeachan-Heo/oh-my-claudecode; 275: effort path:agents repo:anthropics/claude-plugins-offi…; 276: effort path:agents repo:anthropics/claude-plugins-offi…; 277: README repo:anthropics/claude-plugins-official; 288: README repo:openai/codex; 303: README repo:anthropics/claude-code; 304: subagent hot reload repo:anthropics/claude-code; 305: agent repo:anthropics/claude-code; 306: effort teammate repo:anthropics/claude-code; 307: agent repo:anthropics/claude-code |
| R12b | R12b proposed saved rows | 266: "effort:" path:skills/subagent-driven-development repo…; 267: "effort:" path:skills/subagent-driven-development repo…; 269: unexpected_models repo:monoes/monomind; 270: unexpected_models repo:monoes/monomind |


## 7. Routes, aggregated


| Stage | Provider | Calls | rc values | Hits (sum where numeric) | Statuses | Used |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | context7 | 2 | 1 | 0 | ERROR 2 | 2 |
| 1 | exa | 16 | 0 | 160 | OK 16 | 12 |
| 1 | firecrawl | 1 | None | 0 | SKIPPED 1 | 1 |
| 1 | gh-raw | 2 | 0 | 2 | OK 2 | 1 |
| 1 | last30days | 1 | 0 | 107 | DEGRADED 1 | 1 |
| 1 | serpapi | 2 | 0 | 17 | OK 2 | 0 |
| 1 | serper | 6 | 0 | 60 | OK 6 | 3 |
| 1 | webclaw | 110 | 0, 1 | 105 | EMPTY_UNVERIFIED 1, ERROR 4, OK 105 | 40 |
| 2 | gh-code-search-saved | 32 | 0 | 0 | EMPTY_UNVERIFIED 2, EMPTY_VERIFIED 4, OK 26 | 32 |
| 2 | gh-graphql-discussion | 2 | 0, None | 7 | OK 1, SKIPPED 1 | 0 |
| 2 | gh-issue-search | 14 | 0 | 183 | EMPTY_UNVERIFIED 1, OK 13 | 9 |
| 2 | gh-issue-search-saved | 8 | 0 | 0 | OK 8 | 8 |
| 2 | gh-issue-view | 51 | 0 | 51 | OK 51 | 47 |
| 2 | gh-pr-search | 1 | 0 | 6 | OK 1 | 0 |
| 2 | gh-pr-view | 31 | 1 | 0 | ERROR 31 | 0 |
| 2 | git-clone | 14 | 0 | 14 | OK 14 | 14 |
| local | local | 9 | 0 | 9 | OK 9 | 9 |
| preflight | context7 | 1 | 0 | n/a | OK 1 | 1 |
| preflight | exa | 1 | 0 | n/a | OK 1 | 1 |
| preflight | firecrawl | 1 | 0 | n/a | SKIPPED 1 | 1 |
| preflight | github | 15 | 0 | n/a | OK 15 | 15 |
| preflight | last30days | 1 | 0 | n/a | OK 1 | 1 |
| preflight | scrapecreators | 1 | 0 | n/a | OK 1 | 1 |
| preflight | serpapi | 1 | 0 | n/a | OK 1 | 1 |
| preflight | serper | 1 | 0 | n/a | OK 1 | 1 |

### Local reads

| seq | Read | Mirror | Why |
| --- | --- | --- | --- |
| 311 | codex features list | offline/local/codex-features-list.txt | Q5: multi_agent stable true, multi_agent_v2 stable false, worktrees, hooks |
| 312 | codex --version; claude --version | offline/local/codex-version.txt | host versions: codex-cli 0.162.1, Claude Code 2.1.300 |
| 313 | python3 -I tomllib read of ~/.codex/config.toml (selected keys only) | offline/local/user-codex-config-selected-keys.json | Q5: parent model, effort, sandbox and approval that Codex subagents inherit |
| 314 | strings <claude 2.1.300 binary> \| grep -o <six flag names> | offline/local/claude-2.1.300-flag-names.txt | Q2/Q4: confirm the binary-derived effort flag names exist in 2.1.300 |
| 315 | python3 -I json read of Claude settings files (model, effort, env key names) | offline/local/claude-settings-selected-keys.json | Q2/Q4: session model, per-model effort, fork mode |
| 316 | awk frontmatter of MP/.claude/agents/*.md | offline/local/mp-claude-agents-frontmatter.txt | Q3: compare role files |
| 317 | grep keys of MP/.codex/config.toml and MP/.codex/agents/*.toml | offline/local/mp-codex-config-keys.txt | Q5: MP Codex roles |
| 318 | wc -c of AGENTS.md chain; diff -rq of .claude/skills vs .agents/skills | offline/local/mp-agents-md-sizes-and-skill-mirrors.txt | Q5: 32 KiB AGENTS.md cap and skill mirrors |
| 319 | sed of codex-rs/core/src/agent/role.rs and child_config.rs at clone HEAD | offline/local/codex-agent-role-and-child-config-excerpt.txt | Q5: what a custom agent file can override |

## 8. Open gaps in the log itself

- seq is completion order, so stage-1 and stage-2 rows interleave where runs overlapped (the
  webclaw mirror ran beside the searches; clones ran beside the saved searches).
- Last30Days counts: the row's `hits` is the run's 107 items from its stats block; `top_results`
  are the first URLs in its Markdown output, not its ranked clusters.
- The hand-run webclaw re-check (seq 320) saved no output; it repeats seq 93's 404.
- Saved-search `total_count` values are GitHub's page-1 counts; code search still under-reports
  frontmatter matches (seq 275 against the clone).
- No stage-1 provider was retried after a quota or credit failure; Firecrawl was not called at all
  (preflight seq 1).
- Key check after the run: `S/bin/keyscan.sh` under the fnox profile counted files containing any
  of the seven key values in the log, mirror, raw captures, plans, scripts and both drafts: 0 for
  each key (it prints counts only).
