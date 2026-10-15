# R23 log: D137 query log for R23 (auto-compaction at 40% of the context limit, R-179)

Research R23, session `ccm-20261014` (`ce9c0b3d`), 2026-10-14, for request R-179 (decision D188, record DL-241). This file is the run's query log rendered from `offline/queries.jsonl` (99 rows, every call logged when it ran, failed and quota-limited calls included) and the log-built report sections 2 to 6 and 9. The report is `R23-compaction-percent.md` beside this file.

Paths: S = `/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/r179/`; O = `S/offline/` (the D110 mirror: `pages/` webclaw copies, `gh/` thread JSON, `code/` source files, `manifest.json` with SHA-256 per item, `queries.jsonl`); raw provider responses in `S/raw/`; scripts in `S/bin/` (`fx` fnox wrapper, `http.py`, `run2.py` stage-2 runner, `sections.py`, `logmd.py`). The mirror sits in the scratchpad rather than `MP/offline/research/` because the brief forbids writes to MP; the parent can move it to `offline/research/R23-compaction-percent/`.

No tracked file in MP changed, nothing was written to GitHub, no `claude` session started (`claude --version` and `strings(1)` on the installed binary only), no key value was printed, and the environment was never listed (keys checked one named variable at a time, `S/raw/keys-presence.txt`).

## Query log (all rows)

| seq | stage | provider | query | rc | http | hits | status / failure_code | seeded_by | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | preflight | firecrawl | `firecrawl credits --json` | 0 | 200 | None | SKIPPED / CREDITS_EXHAUSTED | None | yes |
| 2 | preflight | serper | `GET https://google.serper.dev/account` | 0 | 200 | None | OK / NONE | None | yes |
| 3 | preflight | serpapi | `GET https://serpapi.com/account.json` | 0 | 200 | None | OK / NONE | None | yes |
| 4 | preflight | github | `gh api rate_limit` | 0 | 200 | None | OK / NONE | None | yes |
| 5 | preflight | context7 | `ctx7 whoami` | 0 | None | None | OK / NONE | None | yes |
| 6 | preflight | exa | `EXA_API_KEY presence (no balance endpoint known)` | 0 | None | None | OK / NONE | None | yes |
| 7 | preflight | last30days | `SCRAPECREATORS_API_KEY presence` | 0 | None | None | OK / NONE | None | yes |
| 8 | 1 | webclaw | `https://code.claude.com/docs/en/model-config.md` | 0 | None | 1 | OK / NONE | None | yes |
| 9 | 1 | webclaw | `https://code.claude.com/docs/en/context-window.md` | 0 | None | 1 | OK / NONE | None | yes |
| 10 | 1 | webclaw | `https://code.claude.com/docs/en/commands.md` | 0 | None | 1 | OK / NONE | None | yes |
| 11 | 1 | webclaw | `https://code.claude.com/docs/en/cli-reference.md` | 0 | None | 1 | OK / NONE | None | yes |
| 12 | 1 | webclaw | `https://code.claude.com/docs/en/prompt-caching.md` | 0 | None | 1 | OK / NONE | None | yes |
| 13 | 1 | webclaw | `https://code.claude.com/docs/en/settings.md` | 0 | None | 1 | OK / NONE | None | yes |
| 14 | 1 | webclaw | `https://code.claude.com/docs/en/env-vars.md` | 0 | None | 1 | OK / NONE | None | yes |
| 15 | 1 | webclaw | `https://platform.claude.com/docs/en/about-claude/models/overview` | 0 | None | 1 | OK / NONE | None | yes |
| 16 | 1 | webclaw | `https://platform.claude.com/docs/en/build-with-claude/context-windows` | 0 | None | 1 | OK / NONE | None | yes |
| 17 | 1 | exa | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE Claude Code auto-compact percentage threshold` | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | None | no |
| 18 | 1 | exa | `Claude Code autoCompactWindow modelSettings per model /autocompact setting` | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | None | no |
| 19 | 1 | exa | `Claude Code mods session.compact $.session.usage compact at a context percentage` | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | None | no |
| 20 | 1 | exa | `Claude Code 1M context auto-compact earlier than 967K tokens` | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | None | no |
| 21 | 1 | exa | `Claude Code subagent frontmatter autoCompactWindow` | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | None | no |
| 22 | 1 | context7 | `ctx7 library "claude code" "auto-compact window settings"` | 0 | None | 5 | OK / NONE | None | yes |
| 23 | 1 | context7 | `ctx7 docs /websites/code_claude "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE autoCompactWindow modelSettings auto-compact window percentage"` | 0 | None | 4 | OK / NONE | None | yes |
| 24 | 1 | context7 | `ctx7 docs /websites/code_claude "mods session.compact session.usage context percent compact from a hook"` | 0 | None | 4 | OK / NONE | None | yes |
| 25 | 1 | serper | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 0 | 200 | 10 | OK / NONE | None | yes |
| 26 | 1 | serper | `claude code "autoCompactWindow" modelSettings per model` | 0 | 200 | 10 | OK / NONE | None | yes |
| 27 | 1 | serper | `claude code auto-compact at percentage of context window 1M` | 0 | 200 | 9 | OK / NONE | None | yes |
| 28 | 1 | serper | `claude code mod "session.compact" "session.usage"` | 0 | 200 | 10 | OK / NONE | None | yes |
| 29 | 1 | serpapi | `"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE" settings.json env` | 0 | 200 | 9 | OK / NONE | None | yes |
| 30 | 1 | webclaw | `https://spec-weave.com/docs/guides/claude-code-auto-compact/` | 0 | None | 1 | OK / NONE | 26 | yes |
| 31 | 1 | webclaw | `https://wmedia.es/en/tips/claude-code-auto-compact-window` | 0 | None | 1 | OK / NONE | 27 | yes |
| 32 | 1 | webclaw | `https://anotifier.io/guides/claude-code-auto-compact-warning/` | 0 | None | 1 | OK / NONE | 26 | no |
| 33 | 1 | webclaw | `https://www.turboai.dev/blog/claude-autocompact-pct-override-guide` | 0 | None | 1 | OK / NONE | 25 | yes |
| 34 | 1 | webclaw | `https://levelup.gitconnected.com/why-i-compact-my-ai-coding-agent-at-20-not-90-1a665c0c4e5d` | 0 | None | 1 | OK / NONE | 27 | no |
| 35 | 1 | webclaw | `https://www.reddit.com/r/ClaudeCode/comments/1ta73cj/warning_claude_added_autocompact_your_1m_session/` | 0 | None | 1 | OK / NONE | 27 | no |
| 36 | 1 | webclaw | `https://code.claude.com/docs/en/plugins/mods/reference.md` | 0 | None | 1 | OK / NONE | None | yes |
| 37 | 1 | webclaw | `https://code.claude.com/docs/en/plugins/mods/events.md` | 0 | None | 1 | OK / NONE | None | no |
| 38 | 1 | webclaw | `https://code.claude.com/docs/en/sub-agents.md` | 0 | None | 1 | OK / NONE | None | yes |
| 39 | 1 | last30days | `"Claude Code auto-compact window autocompact threshold" --quick --emit json --no-browser-cookies --web-backend serper` | 0 | None | 7 | OK / NONE | None | yes |
| 40 | local | local-read | `MP offline/research/R22-cc-2.1.300/raw/CHANGELOG-v2.1.300.md (grep autocompact\|auto-compact\|context window)` | 0 | None | 52 | OK / NONE | None | yes |
| 41 | local | local-read | `MP offline/research/R22-cc-2.1.300/raw/docs/{env-vars,sub-agents,settings-reference.json}.md (fetched 2026-10-14T23:43:57Z)` | 0 | None | 6 | OK / NONE | None | yes |
| 42 | local | local-read | `strings -n 6 ~/.local/share/claude/versions/2.1.300 (sha256 475517ca...) -> local/cc-2.1.300.strings; functions x9,h8,bS,dro,w9t,Pls,_ge` | 0 | None | 8 | OK / NONE | None | yes |
| 43 | local | local-read | `MP offline/research/R7-mods-switch-detection/types/claude-code-2.1.296.d.ts ($.session.usage/compact, $.settings.read, $.command.run, $.conf` | 0 | None | 9 | OK / NONE | None | yes |
| 44 | local | local-read | `scratchpad research5/R1/docs/mods_reference-raw.md (2.1.299 docs copy)` | 0 | None | 3 | OK / NONE | None | yes |
| 45 | local | local-read | `MP dev/doctor/{budget,settings}.py, dev/test_doctor.py, frontier.toml, docs/agents/claude-team.md, ~/.claude/settings.json (compaction keys ` | 0 | None | 7 | OK / NONE | None | yes |
| 46 | preflight | github | `gh api repos/anthropics/claude-code` | 0 | 200 | None | OK / NONE | None | yes |
| 47 | preflight | github | `gh api repos/anton-abyzov/specweave` | 0 | 200 | None | OK / NONE | None | yes |
| 48 | preflight | github | `gh api repos/scasella/claude-flightdeck` | 0 | 200 | None | OK / NONE | None | yes |
| 49 | preflight | github | `gh api repos/karanb192/cache-tax` | 0 | 200 | None | OK / NONE | None | yes |
| 50 | preflight | github | `gh api repos/kunchenguid/firstmate` | 0 | 200 | None | OK / NONE | None | yes |
| 51 | preflight | github | `gh api repos/guilhermegor/dotfiles-linux-dev` | 0 | 200 | None | OK / NONE | None | yes |
| 52 | 2 | gh-issue-search | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 0 | 200 | 20 | OK / NONE | 25 | yes |
| 53 | 2 | gh-issue-search | `autoCompactWindow modelSettings` | 0 | 200 | 7 | OK / NONE | 26 | yes |
| 54 | 2 | gh-issue-search | `/autocompact per model` | 0 | 200 | 20 | OK / NONE | 8 | yes |
| 55 | 2 | gh-issue-search | `session.compact mod` | 0 | 200 | 9 | OK / NONE | 28 | yes |
| 56 | 2 | gh-issue-search | `autoCompactWindow subagent frontmatter` | 0 | 200 | 7 | OK / NONE | 40 | yes |
| 57 | 2 | gh-issue-search | `autocompact percentage settings.json env` | 0 | 200 | 18 | OK / NONE | 29 | yes |
| 58 | 2 | gh-issue-search | `effective auto-compact window` | 0 | 200 | 20 | OK / NONE | 29 | yes |
| 59 | 2 | gh-pr-search | `autoCompactWindow` | 0 | 200 | 20 | OK / NONE | 39 | yes |
| 60 | 2 | gh-issue-search | `"autoCompactWindow" 400000` | 0 | 200 | 20 | OK / NONE | 30 | yes |
| 61 | 2 | gh-issue-view | `anthropics/claude-code#82761` | 0 | 200 | 1 | OK / NONE | 25 | yes |
| 62 | 2 | gh-issue-view | `anthropics/claude-code#63186` | 0 | 200 | 1 | OK / NONE | 25 | yes |
| 63 | 2 | gh-issue-view | `anthropics/claude-code#57567` | 0 | 200 | 1 | OK / NONE | 29 | yes |
| 64 | 2 | gh-issue-view | `anthropics/claude-code#34925` | 0 | 200 | 1 | OK / NONE | 29 | yes |
| 65 | 2 | gh-issue-view | `anthropics/claude-code#97568` | 0 | 200 | 1 | OK / NONE | 25 | yes |
| 66 | 2 | gh-issue-view | `anthropics/claude-code#75335` | 0 | 200 | 1 | OK / NONE | 29 | yes |
| 67 | 2 | gh-issue-view | `anthropics/claude-code#101067` | 0 | 200 | 1 | OK / NONE | 26 | yes |
| 68 | 2 | gh-issue-view | `anthropics/claude-code#100277` | 0 | 200 | 1 | OK / NONE | 25 | yes |
| 69 | 2 | gh-issue-view | `anthropics/claude-code#100932` | 0 | 200 | 1 | OK / NONE | 26 | yes |
| 70 | 2 | gh-issue-view | `anthropics/claude-code#97733` | 0 | 200 | 1 | OK / NONE | 8 | yes |
| 71 | 2 | gh-issue-view | `anthropics/claude-code#83355` | 0 | 200 | 1 | OK / NONE | 40 | yes |
| 72 | 2 | gh-issue-view | `anthropics/claude-code#90347` | 0 | 200 | 1 | OK / NONE | 40 | yes |
| 73 | 2 | gh-issue-view | `anthropics/claude-code#96467` | 0 | 200 | 1 | OK / NONE | 29 | yes |
| 74 | 2 | gh-issue-view | `anthropics/claude-code#102134` | 0 | 200 | 1 | OK / NONE | 28 | yes |
| 75 | 2 | gh-issue-view | `anthropics/claude-code#95328` | 0 | 200 | 1 | OK / NONE | 28 | yes |
| 76 | 2 | gh-issue-view | `anthropics/claude-code#86863` | 0 | 200 | 1 | OK / NONE | 29 | no |
| 77 | 2 | gh-issue-view | `anthropics/claude-code#93735` | 0 | 200 | 1 | OK / NONE | 26 | yes |
| 78 | 2 | gh-issue-view | `anthropics/claude-code#70477` | 0 | 200 | 1 | OK / NONE | 25 | yes |
| 79 | 2 | gh-issue-view | `melodic-software/claude-code-plugins#6930` | 0 | 200 | 1 | OK / NONE | 26 | yes |
| 80 | 2 | gh-issue-view | `aeghnnsw/cc-toolkit#243` | 0 | 200 | 1 | OK / NONE | 29 | yes |
| 81 | 2 | gh-issue-view | `sthe0/claude-agent-instructions#167` | 0 | 200 | 1 | OK / NONE | 30 | yes |
| 82 | 2 | gh-pr-view | `DevCrop/ai-setup#13` | 0 | 200 | 1 | OK / NONE | 39 | yes |
| 83 | 2 | gh-pr-view | `liminal-ai/t3code-lim#31` | 0 | 200 | 1 | OK / NONE | 39 | yes |
| 84 | 2 | gh-pr-view | `elkisdm/devground#104` | 0 | 200 | 1 | OK / NONE | 39 | yes |
| 85 | 2 | gh-pr-view | `kunchenguid/firstmate#6272` | 0 | 200 | 1 | OK / NONE | 39 | yes |
| 86 | 2 | gh-graphql-discussion | `autoCompactWindow` | 0 | 200 | 3 | OK / NONE | 26 | no |
| 87 | 2 | gh-graphql-discussion | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 0 | 200 | 3 | OK / NONE | 25 | no |
| 88 | 2 | gh-code-search-saved | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE repo:anthropics/claude-code` | 0 | 200 | 0 | EMPTY_VERIFIED / NONE | 25 | yes |
| 89 | 2 | gh-code-search-saved | `README repo:anthropics/claude-code` | 0 | 200 | 42 | OK / NONE | 25 | yes |
| 90 | 2 | gh-code-search-saved | `autoCompactWindow repo:anthropics/claude-code` | 0 | 200 | 1 | OK / NONE | 26 | yes |
| 91 | 2 | gh-code-search-saved | `autoCompactWindow repo:anton-abyzov/specweave` | 0 | 200 | 6 | OK / NONE | 30 | yes |
| 92 | 2 | gh-code-search-saved | `README repo:anton-abyzov/specweave` | 0 | 200 | 147 | OK / NONE | 30 | yes |
| 93 | 2 | gh-code-search-saved | `session.compact repo:scasella/claude-flightdeck` | 0 | 200 | 2 | OK / NONE | 28 | yes |
| 94 | 2 | gh-code-search-saved | `README repo:scasella/claude-flightdeck` | 0 | 200 | 3 | OK / NONE | 28 | yes |
| 95 | 2 | gh-code-search | `"$.session.compact" "usage" language:TypeScript` | 0 | 200 | 256 | OK / NONE | 28 | yes |
| 96 | 2 | gh-code-view | `Ivlad003/context-gate@d4435f1ce5a78422c8dc75bf779b6026fd33c8a7:hooks/register.ts` | 0 | 200 | 1 | OK / NONE | 28 | yes |
| 97 | 2 | gh-code-view | `ambervdberg/smartcompact@c8a1e691337bebc2b478cf6a28ebc2b65b5dda5e:plugin/smartcompact/hooks/register.ts` | 0 | 200 | 1 | OK / NONE | 28 | yes |
| 98 | 2 | gh-code-view | `anton-abyzov/specweave@e4d60df99e2d89164f33efa368143713fb908847:src/cli/commands/autocompact.ts` | 0 | 200 | 1 | OK / NONE | 30 | yes |
| 99 | 2 | gh-code-view | `scasella/claude-flightdeck@6150b9f40b0a36e42c22d39f03ddb81aaefe1844:hooks/register.tsx` | 0 | 200 | 1 | OK / NONE | 28 | yes |

Notes on rows: 17 to 21 (Exa) were all sent before the first 402 was read, so each is an ERROR row with `CREDITS_EXHAUSTED` (`NO_MORE_CREDITS`); Firecrawl has no stage-1 row because preflight row 1 found `remainingCredits` -128 and skipped it (webclaw, Serper and SerpApi took its place, as the workflow says). Row 35 (Reddit) returned 252 bytes, `EMPTY_UNVERIFIED`. The first Last30Days attempt failed before any provider call because the mise `timeout` shim has no version; it is not a provider row. Providers `local-read`, `gh-code-search` and `gh-code-view` are outside the D137 enum and are proposed additions.

## 2. Queries sent to each tool, plugin or service (stage 1), exact text

Built from `offline/queries.jsonl`; preflight rows first (D142).

| seq | stage | provider | exact query, URL or command |
| --- | --- | --- | --- |
| 1 | preflight | firecrawl | `firecrawl credits --json` |
| 2 | preflight | serper | `GET https://google.serper.dev/account` |
| 3 | preflight | serpapi | `GET https://serpapi.com/account.json` |
| 5 | preflight | context7 | `ctx7 whoami` |
| 6 | preflight | exa | `EXA_API_KEY presence (no balance endpoint known)` |
| 7 | preflight | last30days | `SCRAPECREATORS_API_KEY presence` |
| 8 | 1 | webclaw | `https://code.claude.com/docs/en/model-config.md` |
| 9 | 1 | webclaw | `https://code.claude.com/docs/en/context-window.md` |
| 10 | 1 | webclaw | `https://code.claude.com/docs/en/commands.md` |
| 11 | 1 | webclaw | `https://code.claude.com/docs/en/cli-reference.md` |
| 12 | 1 | webclaw | `https://code.claude.com/docs/en/prompt-caching.md` |
| 13 | 1 | webclaw | `https://code.claude.com/docs/en/settings.md` |
| 14 | 1 | webclaw | `https://code.claude.com/docs/en/env-vars.md` |
| 15 | 1 | webclaw | `https://platform.claude.com/docs/en/about-claude/models/overview` |
| 16 | 1 | webclaw | `https://platform.claude.com/docs/en/build-with-claude/context-windows` |
| 17 | 1 | exa | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE Claude Code auto-compact percentage threshold` |
| 18 | 1 | exa | `Claude Code autoCompactWindow modelSettings per model /autocompact setting` |
| 19 | 1 | exa | `Claude Code mods session.compact $.session.usage compact at a context percentage` |
| 20 | 1 | exa | `Claude Code 1M context auto-compact earlier than 967K tokens` |
| 21 | 1 | exa | `Claude Code subagent frontmatter autoCompactWindow` |
| 22 | 1 | context7 | `ctx7 library "claude code" "auto-compact window settings"` |
| 23 | 1 | context7 | `ctx7 docs /websites/code_claude "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE autoCompactWindow modelSettings auto-compact window percentage"` |
| 24 | 1 | context7 | `ctx7 docs /websites/code_claude "mods session.compact session.usage context percent compact from a hook"` |
| 25 | 1 | serper | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` |
| 26 | 1 | serper | `claude code "autoCompactWindow" modelSettings per model` |
| 27 | 1 | serper | `claude code auto-compact at percentage of context window 1M` |
| 28 | 1 | serper | `claude code mod "session.compact" "session.usage"` |
| 29 | 1 | serpapi | `"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE" settings.json env` |
| 30 | 1 | webclaw | `https://spec-weave.com/docs/guides/claude-code-auto-compact/` |
| 31 | 1 | webclaw | `https://wmedia.es/en/tips/claude-code-auto-compact-window` |
| 32 | 1 | webclaw | `https://anotifier.io/guides/claude-code-auto-compact-warning/` |
| 33 | 1 | webclaw | `https://www.turboai.dev/blog/claude-autocompact-pct-override-guide` |
| 34 | 1 | webclaw | `https://levelup.gitconnected.com/why-i-compact-my-ai-coding-agent-at-20-not-90-1a665c0c4e5d` |
| 35 | 1 | webclaw | `https://www.reddit.com/r/ClaudeCode/comments/1ta73cj/warning_claude_added_autocompact_your_1m_session/` |
| 36 | 1 | webclaw | `https://code.claude.com/docs/en/plugins/mods/reference.md` |
| 37 | 1 | webclaw | `https://code.claude.com/docs/en/plugins/mods/events.md` |
| 38 | 1 | webclaw | `https://code.claude.com/docs/en/sub-agents.md` |
| 39 | 1 | last30days | `"Claude Code auto-compact window autocompact threshold" --quick --emit json --no-browser-cookies --web-backend serper` |

Local reads (stage `local`), logged for completeness: 40 `MP offline/research/R22-cc-2.1.300/raw/CHANGELOG-v2.1.300.md (grep aut`; 41 `MP offline/research/R22-cc-2.1.300/raw/docs/{env-vars,sub-agents,setti`; 42 `strings -n 6 ~/.local/share/claude/versions/2.1.300 (sha256 475517ca..`; 43 `MP offline/research/R7-mods-switch-detection/types/claude-code-2.1.296`; 44 `scratchpad research5/R1/docs/mods_reference-raw.md (2.1.299 docs copy)`; 45 `MP dev/doctor/{budget,settings}.py, dev/test_doctor.py, frontier.toml,`.

## 3. Results from each (stage 1)

| seq | provider | rc | http | hits | status / failure_code | top results | used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | firecrawl | 0 | 200 | None | SKIPPED / CREDITS_EXHAUSTED {"remainingCredits": -128, "planCredits": 1000} | - | yes |
| 2 | serper | 0 | 200 | None | OK / NONE {"balance": 1281, "rateLimit": 5} | - | yes |
| 3 | serpapi | 0 | 200 | None | OK / NONE {"plan_searches_left": 237} | - | yes |
| 5 | context7 | 0 | None | None | OK / NONE | - | yes |
| 6 | exa | 0 | None | None | OK / NONE | - | yes |
| 7 | last30days | 0 | None | None | OK / NONE | - | yes |
| 8 | webclaw | 0 | None | 1 | OK / NONE | [Model configuration](https://code.claude.com/docs/en/model-config.md) | yes |
| 9 | webclaw | 0 | None | 1 | OK / NONE | [What the timeline shows](https://code.claude.com/docs/en/context-window.md) | yes |
| 10 | webclaw | 0 | None | 1 | OK / NONE | [Commands](https://code.claude.com/docs/en/commands.md) | yes |
| 11 | webclaw | 0 | None | 1 | OK / NONE | [CLI reference](https://code.claude.com/docs/en/cli-reference.md) | yes |
| 12 | webclaw | 0 | None | 1 | OK / NONE | [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching.md) | yes |
| 13 | webclaw | 0 | None | 1 | OK / NONE | [Settings files and who they affect](https://code.claude.com/docs/en/settings.md) | yes |
| 14 | webclaw | 0 | None | 1 | OK / NONE | [Environment variables](https://code.claude.com/docs/en/env-vars.md) | yes |
| 15 | webclaw | 0 | None | 1 | OK / NONE | [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview) | yes |
| 16 | webclaw | 0 | None | 1 | OK / NONE | [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows) | yes |
| 17 | exa | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | - | no |
| 18 | exa | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | - | no |
| 19 | exa | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | - | no |
| 20 | exa | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | - | no |
| 21 | exa | 0 | 402 | 0 | ERROR / CREDITS_EXHAUSTED | - | no |
| 22 | context7 | 0 | None | 5 | OK / NONE | [/anthropics/claude-code](https://context7.com/anthropics/claude-code); [/websites/code_claude](https://context7.com/websites/code_claude); [/llmstxt/code_claude_llms_txt](https://context7.com/llmstxt/code_claude_llms_txt) | yes |
| 23 | context7 | 0 | None | 4 | OK / NONE | [env-vars: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE](https://code.claude.com/docs/en/env-vars); [settings-reference: autoCompactWindow](https://code.claude.com/docs/en/settings-reference#autocompactwindow); [sub-agents: Auto-compaction](https://code.claude.com/docs/en/sub-agents) | yes |
| 24 | context7 | 0 | None | 4 | OK / NONE | [errors: Context exceeds compaction window warning](https://code.claude.com/docs/en/errors); [plugins/mods/reference: session events](https://code.claude.com/docs/en/plugins/mods/reference); [env-vars: CLAUDE_AUTOCOMPACT_PCT_OVERRIDE](https://code.claude.com/docs/en/env-vars) | yes |
| 25 | serper | 0 | 200 | 10 | OK / NONE | [Environment variables - Claude Code Docs](https://code.claude.com/docs/en/env-vars); [CLAUDE_AUTOCOMPACT_PCT...](https://github.com/anthropics/claude-code/issues/31806); [CLAUDE_AUTOCOMPACT_PCT...](https://www.turboai.dev/blog/claude-autocompact-pct-override-guide) | yes |
| 26 | serper | 0 | 200 | 10 | OK / NONE | [Model configuration - Claude Code Docs](https://code.claude.com/docs/en/model-config); [All settings - Claude Code Docs](https://code.claude.com/docs/en/settings-reference); [Claude Code — Complete settings.json Reference](https://gist.github.com/mculp/c082bd1e5a439410158974de90c89db7) | yes |
| 27 | serper | 0 | 200 | 9 | OK / NONE | [[BUG] Auto compact does not trigger at 100% context ...](https://github.com/anthropics/claude-code/issues/66144); [Warning: Claude added /autocompact - your 1m session ...](https://www.reddit.com/r/ClaudeCode/comments/1ta73cj/warning_claude_added_autocompact_your_1m_session/); [Context windows - Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/context-windows) | yes |
| 28 | serper | 0 | 200 | 10 | OK / NONE | [scasella/claude-flightdeck: A Claude Code mod that puts a ...](https://github.com/scasella/claude-flightdeck); [Mehmet Mutlu's Post - claudecode #opensource](https://www.linkedin.com/posts/mutlu-mehmet_claudecode-opensource-activity-7512776357576155137-kczm); [Claude Mods scoreboard: every mod on GitHub and what it ...](https://mods.karanbansal.in/) | yes |
| 29 | serpapi | 0 | 200 | 9 | OK / NONE | [330 settings. You've probably changed zero. Claude Code ...](https://www.instagram.com/p/DduQ8HtjXwd/); [Paweł Huryn](https://x.com/PawelHuryn/status/2033626691021459604); [Auto-compact cannot be disabled — consolidated report ...](https://github.com/anthropics/claude-code/issues/42817) | yes |
| 30 | webclaw | 0 | None | 1 | OK / NONE | [Claude Code auto-compact: compact at 400K](https://spec-weave.com/docs/guides/claude-code-auto-compact/) | yes |
| 31 | webclaw | 0 | None | 1 | OK / NONE | [Claude Code auto-compact: who decides your context window (and why it ](https://wmedia.es/en/tips/claude-code-auto-compact-window) | yes |
| 32 | webclaw | 0 | None | 1 | OK / NONE | [Get notified before Claude Code auto-compacts your chat](https://anotifier.io/guides/claude-code-auto-compact-warning/) | no |
| 33 | webclaw | 0 | None | 1 | OK / NONE | [CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: Complete Guide to Claude Code Auto-Co](https://www.turboai.dev/blog/claude-autocompact-pct-override-guide) | yes |
| 34 | webclaw | 0 | None | 1 | OK / NONE | [Level Up Coding](https://levelup.gitconnected.com/why-i-compact-my-ai-coding-agent-at-20-not-90-1a665c0c4e5d) | no |
| 35 | webclaw | 0 | None | 1 | OK / NONE | [](https://www.reddit.com/r/ClaudeCode/comments/1ta73cj/warning_claude_added_autocompact_your_1m_session/) | no |
| 36 | webclaw | 0 | None | 1 | OK / NONE | [Mods reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | yes |
| 37 | webclaw | 0 | None | 1 | OK / NONE | [React to events with a mod](https://code.claude.com/docs/en/plugins/mods/events.md) | no |
| 38 | webclaw | 0 | None | 1 | OK / NONE | [Create custom subagents](https://code.claude.com/docs/en/sub-agents.md) | yes |
| 39 | last30days | 0 | None | 7 | OK / NONE | [chore(settings): raise auto-compact threshold to 75%](https://github.com/guilhermegor/dotfiles-linux-dev/pull/744); [feat(bin): set autoCompactWindow 220000 for every Claude worker launch](https://github.com/kunchenguid/firstmate/pull/6272); [optimal_config_checker: add a seventh check for CLAUDE_CODE_AUTO_COMPA](https://github.com/Edmonds-Commerce-Limited/claude-code-hooks-daemon/issues/46) | yes |
| 40 | local-read | 0 | None | 52 | OK / NONE | [2.1.296: autoCompactWindow in subagent frontmatter (line 290)](file:offline/research/R22-cc-2.1.300/raw/CHANGELOG-v2.1.300.md:290); [2.1.288: /autocompact saves per model (line 982)](file:...:982); [2.1.288: server window from first request (line 961)](file:...:961) | yes |
| 41 | local-read | 0 | None | 6 | OK / NONE | [env-vars.md:195 CLAUDE_AUTOCOMPACT_PCT_OVERRIDE](file:offline/research/R22-cc-2.1.300/raw/docs/env-vars.md:195); [sub-agents.md:1131,1148](file:offline/research/R22-cc-2.1.300/raw/docs/sub-agents.md:1131); [settings-reference.json modelSettings.autoCompactWindow](file:offline/research/R22-cc-2.1.300/raw/docs/settings-reference.json) | yes |
| 42 | local-read | 0 | None | 8 | OK / NONE | [x9: threshold = min(floor(eff*pct/100), eff-13000)](file:local/cc-2.1.300.strings@23374374); [h8: eff = window - min(maxOutputTokens,20000)](file:local/cc-2.1.300.strings@23379791); [bS/dro: env > settings(per-model, top-level) > clientdata > experiment](file:local/cc-2.1.300.strings@23377582) | yes |
| 43 | local-read | 0 | None | 9 | OK / NONE | [d.ts:2845-2853 usage(); example compact at percent](file:...d.ts:2845); [d.ts:2872-2882 compact()](file:...d.ts:2872); [d.ts:3585 settings.read only](file:...d.ts:3585) | yes |
| 44 | local-read | 0 | None | 3 | OK / NONE | [mods_reference-raw.md:117-125 session events](file:research5/R1/docs/mods_reference-raw.md:117); [mods_reference-raw.md:191-193 $.session, $.settings](file:research5/R1/docs/mods_reference-raw.md:191) | yes |
| 45 | local-read | 0 | None | 7 | OK / NONE | [dev/doctor/budget.py:8-9 THRESHOLDS](file:dev/doctor/budget.py:9); [dev/doctor/settings.py:14 PROJECT_KEYS](file:dev/doctor/settings.py:14); [frontier.toml:11,25-29](file:.planning/.../frontier.toml:11) | yes |

## 4. GitHub issues, PRs and discussions searched (stage 2), with the stage-1 row that seeded each

Repository preflight (D147): seq 4 `gh api rate_limit` null; seq 46 `gh api repos/anthropics/claude-code` {"has_issues": true, "has_discussions": false, "archived": false, "private": false}; seq 47 `gh api repos/anton-abyzov/specweave` {"has_issues": true, "has_discussions": false, "archived": false, "private": false}; seq 48 `gh api repos/scasella/claude-flightdeck` {"has_issues": true, "has_discussions": false, "archived": false, "private": false}; seq 49 `gh api repos/karanb192/cache-tax` {"has_issues": true, "has_discussions": false, "archived": false, "private": false}; seq 50 `gh api repos/kunchenguid/firstmate` {"has_issues": true, "has_discussions": false, "archived": false, "private": false}; seq 51 `gh api repos/guilhermegor/dotfiles-linux-dev` {"has_issues": true, "has_discussions": false, "archived": false, "private": false}. `anthropics/claude-code` has discussions disabled, so its discussion searches ran globally; the repo-scoped form is FEATURE_DISABLED.

| seq | provider | query | seeded_by | hits | top results / thread | used |
| --- | --- | --- | --- | --- | --- | --- |
| 52 | gh-issue-search | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 25 | 20 | [[FEATURE] `get_context_usage` should report the auto-compact point tha](https://github.com/anthropics/claude-code/issues/97568); [CLAUDE_AUTOCOMPACT_PCT_OVERRIDE silently stopped taking effect after 2](https://github.com/anthropics/claude-code/issues/82761) | yes |
| 53 | gh-issue-search | `autoCompactWindow modelSettings` | 26 | 7 | [Desktop: Expose the auto-compact window in the usage ring that already](https://github.com/anthropics/claude-code/issues/90756); [[FEATURE] Configurable token threshold for idle compaction (idleCompac](https://github.com/anthropics/claude-code/issues/101616) | yes |
| 54 | gh-issue-search | `/autocompact per model` | 8 | 20 | [[FEATURE] Session-scoped /autocompact: change a running session's wind](https://github.com/anthropics/claude-code/issues/97733); [[FEATURE] Expose the effective auto-compact window in the statusLine J](https://github.com/anthropics/claude-code/issues/96467) | yes |
| 55 | gh-issue-search | `session.compact mod` | 28 | 9 | [[BUG] session.compact mod hook no longer raised in 2.1.299 (manual and](https://github.com/anthropics/claude-code/issues/102134); [[FEATURE] Mods: pass images and hidden context rows to session.compact](https://github.com/anthropics/claude-code/issues/100481) | yes |
| 56 | gh-issue-search | `autoCompactWindow subagent frontmatter` | 40 | 7 | [Feature request: per-agent auto-compact window (separate boundaries fo](https://github.com/anthropics/claude-code/issues/90347); [Agent teams: per-agent autocompact control + a protocol to compact a c](https://github.com/anthropics/claude-code/issues/86716) | yes |
| 57 | gh-issue-search | `autocompact percentage settings.json env` | 29 | 18 | [[FEATURE] Expose the effective auto-compact window in the statusLine J](https://github.com/anthropics/claude-code/issues/96467); [Remote/bridge-attached sessions silently disable threshold auto-compac](https://github.com/anthropics/claude-code/issues/70477) | yes |
| 58 | gh-issue-search | `effective auto-compact window` | 29 | 20 | [[FEATURE] Expose the effective auto-compact window in the statusLine J](https://github.com/anthropics/claude-code/issues/96467); [[FEATURE] `get_context_usage` should report the auto-compact point tha](https://github.com/anthropics/claude-code/issues/97568) | yes |
| 59 | gh-pr-search | `autoCompactWindow` | 39 | 20 | [[CHANGELOG v2.1.296] サブエージェントfrontmatterへの autoCompactWindow 追加](https://github.com/rfdnxbro/claude-code-marketplace/pull/702); [The context share counts against the compaction window](https://github.com/HeyCubit/effortless/pull/14) | yes |
| 60 | gh-issue-search | `"autoCompactWindow" 400000` | 30 | 20 | [test(harness-ops): add behavior-probes cases for /autocompact window p](https://github.com/melodic-software/claude-code-plugins/issues/6930); [Feature request: per-agent auto-compact window (separate boundaries fo](https://github.com/anthropics/claude-code/issues/90347) | yes |
| 61 | gh-issue-view | `anthropics/claude-code#82761` | 25 | 1 | [CLAUDE_AUTOCOMPACT_PCT_OVERRIDE silently stopped taking effect after 2](https://github.com/anthropics/claude-code/issues/82761) | yes |
| 62 | gh-issue-view | `anthropics/claude-code#63186` | 25 | 1 | [CLAUDE_AUTOCOMPACT_PCT_OVERRIDE in settings.json env block silently ig](https://github.com/anthropics/claude-code/issues/63186) | yes |
| 63 | gh-issue-view | `anthropics/claude-code#57567` | 29 | 1 | [CLAUDE_AUTOCOMPACT_PCT_OVERRIDE still ignored in v2.1.138 — duplicate-](https://github.com/anthropics/claude-code/issues/57567) | yes |
| 64 | gh-issue-view | `anthropics/claude-code#34925` | 29 | 1 | [Feature: configurable auto-compaction threshold](https://github.com/anthropics/claude-code/issues/34925) | yes |
| 65 | gh-issue-view | `anthropics/claude-code#97568` | 25 | 1 | [[FEATURE] `get_context_usage` should report the auto-compact point tha](https://github.com/anthropics/claude-code/issues/97568) | yes |
| 66 | gh-issue-view | `anthropics/claude-code#75335` | 29 | 1 | [Settings: make the auto-compaction threshold user-configurable (compac](https://github.com/anthropics/claude-code/issues/75335) | yes |
| 67 | gh-issue-view | `anthropics/claude-code#101067` | 26 | 1 | [[BUG] Auto-compaction fires at 281K–845K tokens on 2.1.296 for claude-](https://github.com/anthropics/claude-code/issues/101067) | yes |
| 68 | gh-issue-view | `anthropics/claude-code#100277` | 25 | 1 | [[Bug] Auto-Compact triggers prematurely on Opus 5.5 1M context window](https://github.com/anthropics/claude-code/issues/100277) | yes |
| 69 | gh-issue-view | `anthropics/claude-code#100932` | 26 | 1 | [Autocompact thrashing error with a small autoCompactWindow: counter is](https://github.com/anthropics/claude-code/issues/100932) | yes |
| 70 | gh-issue-view | `anthropics/claude-code#97733` | 8 | 1 | [[FEATURE] Session-scoped /autocompact: change a running session's wind](https://github.com/anthropics/claude-code/issues/97733) | yes |
| 71 | gh-issue-view | `anthropics/claude-code#83355` | 40 | 1 | [Subagent auto-compaction uses the main session's context window, so su](https://github.com/anthropics/claude-code/issues/83355) | yes |
| 72 | gh-issue-view | `anthropics/claude-code#90347` | 40 | 1 | [Feature request: per-agent auto-compact window (separate boundaries fo](https://github.com/anthropics/claude-code/issues/90347) | yes |
| 73 | gh-issue-view | `anthropics/claude-code#96467` | 29 | 1 | [[FEATURE] Expose the effective auto-compact window in the statusLine J](https://github.com/anthropics/claude-code/issues/96467) | yes |
| 74 | gh-issue-view | `anthropics/claude-code#102134` | 28 | 1 | [[BUG] session.compact mod hook no longer raised in 2.1.299 (manual and](https://github.com/anthropics/claude-code/issues/102134) | yes |
| 75 | gh-issue-view | `anthropics/claude-code#95328` | 28 | 1 | [A session.compact function hook's compaction is undone when the sessio](https://github.com/anthropics/claude-code/issues/95328) | yes |
| 76 | gh-issue-view | `anthropics/claude-code#86863` | 29 | 1 | [[BUG] Auto-compact threshold silently regressed — fires at ~73% contex](https://github.com/anthropics/claude-code/issues/86863) | no |
| 77 | gh-issue-view | `anthropics/claude-code#93735` | 26 | 1 | [Project-scope effortLevel in .claude/settings.json is never applied in](https://github.com/anthropics/claude-code/issues/93735) | yes |
| 78 | gh-issue-view | `anthropics/claude-code#70477` | 25 | 1 | [Remote/bridge-attached sessions silently disable threshold auto-compac](https://github.com/anthropics/claude-code/issues/70477) | yes |
| 79 | gh-issue-view | `melodic-software/claude-code-plugins#6930` | 26 | 1 | [test(harness-ops): add behavior-probes cases for /autocompact window p](https://github.com/melodic-software/claude-code-plugins/issues/6930) | yes |
| 80 | gh-issue-view | `aeghnnsw/cc-toolkit#243` | 29 | 1 | [model-config leaves the auto-compact percentage override next to autoC](https://github.com/aeghnnsw/cc-toolkit/issues/243) | yes |
| 81 | gh-issue-view | `sthe0/claude-agent-instructions#167` | 30 | 1 | [autoCompactWindow: measured cost curve says keep the current pin](https://github.com/sthe0/claude-agent-instructions/issues/167) | yes |
| 82 | gh-pr-view | `DevCrop/ai-setup#13` | 39 | 1 | [settings: autoCompactWindow 400000](https://github.com/DevCrop/ai-setup/pull/13) | yes |
| 83 | gh-pr-view | `liminal-ai/t3code-lim#31` | 39 | 1 | [Claude-LHC: default autoCompactWindow 700000](https://github.com/liminal-ai/t3code-lim/pull/31) | yes |
| 84 | gh-pr-view | `elkisdm/devground#104` | 39 | 1 | [docs(adr): enmienda ADR-0040 compactación al 50 %](https://github.com/elkisdm/devground/pull/104) | yes |
| 85 | gh-pr-view | `kunchenguid/firstmate#6272` | 39 | 1 | [feat(bin): set autoCompactWindow 220000 for every Claude worker launch](https://github.com/kunchenguid/firstmate/pull/6272) | yes |
| 86 | gh-graphql-discussion | `autoCompactWindow` | 26 | 3 | [A setting to turn off compact-before-send on stale Claude threads](https://github.com/pingdotgg/t3code/discussions/17170); [[Bug]: "Resume with less context" is offered only after the prompt cac](https://github.com/pingdotgg/t3code/discussions/18011) | no |
| 87 | gh-graphql-discussion | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 25 | 3 | [zh/blog/claude-code-context-overflow-troubleshooting/](https://github.com/Sandwich-git/jileiblog/discussions/4); [The Hidden Defaults That Break Your AI Agent — Claude Code CLI's Undoc](https://github.com/xg-gh-25/SwarmAI/discussions/56) | no |

## 5. Githubkit saved searches run (reproduced read-only with their controls) and proposed new rows

`dev/saved-searches.toml` and `dev/collect_saved_search.py` were read and left unedited; `./dev/mise run research:collect` was not run because it writes a tracked path. The equivalent code-search calls ran under the fnox profile, each proposed row paired with a control query:

| seq | saved_row | role | query | hits | top results | used |
| --- | --- | --- | --- | --- | --- | --- |
| 88 | cc-autocompact-pct | proposed | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE repo:anthropics/claude-code` | 0 | - | yes |
| 89 | cc-autocompact-pct | control | `README repo:anthropics/claude-code` | 42 | [anthropics/claude-code:README.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/README.md); [anthropics/claude-code:examples/settings/README.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/examples/settings/README.md) | yes |
| 90 | cc-autocompact-window | proposed | `autoCompactWindow repo:anthropics/claude-code` | 1 | [anthropics/claude-code:feed.xml](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/feed.xml) | yes |
| 91 | specweave-autocompact | proposed | `autoCompactWindow repo:anton-abyzov/specweave` | 6 | [anton-abyzov/specweave:src/cli/commands/autocompact.ts](https://github.com/anton-abyzov/specweave/blob/e4d60df99e2d89164f33efa368143713fb908847/src/cli/commands/autocompact.ts); [anton-abyzov/specweave:docs-site/docs/guides/claude-code-auto-compact.](https://github.com/anton-abyzov/specweave/blob/e4d60df99e2d89164f33efa368143713fb908847/docs-site/docs/guides/claude-code-auto-compact.md) | yes |
| 92 | specweave-autocompact | control | `README repo:anton-abyzov/specweave` | 147 | [anton-abyzov/specweave:src/templates/docs/README.md](https://github.com/anton-abyzov/specweave/blob/e4d60df99e2d89164f33efa368143713fb908847/src/templates/docs/README.md); [anton-abyzov/specweave:src/adapters/cursor/README.md](https://github.com/anton-abyzov/specweave/blob/e4d60df99e2d89164f33efa368143713fb908847/src/adapters/cursor/README.md) | yes |
| 93 | mods-session-compact | proposed | `session.compact repo:scasella/claude-flightdeck` | 2 | [scasella/claude-flightdeck:README.md](https://github.com/scasella/claude-flightdeck/blob/6150b9f40b0a36e42c22d39f03ddb81aaefe1844/README.md); [scasella/claude-flightdeck:hooks/register.tsx](https://github.com/scasella/claude-flightdeck/blob/6150b9f40b0a36e42c22d39f03ddb81aaefe1844/hooks/register.tsx) | yes |
| 94 | mods-session-compact | control | `README repo:scasella/claude-flightdeck` | 3 | [scasella/claude-flightdeck:SECURITY.md](https://github.com/scasella/claude-flightdeck/blob/6150b9f40b0a36e42c22d39f03ddb81aaefe1844/SECURITY.md); [scasella/claude-flightdeck:CHANGELOG.md](https://github.com/scasella/claude-flightdeck/blob/6150b9f40b0a36e42c22d39f03ddb81aaefe1844/CHANGELOG.md) | yes |
| 95 | - | stage-2 | `"$.session.compact" "usage" language:TypeScript` | 256 | [m-mizutani/dotfiles:claude/plugins/idle-compact/hooks/idle-compact.ts](https://github.com/m-mizutani/dotfiles/blob/a478315fab5581977fff5a31adb31759da9d0162/claude/plugins/idle-compact/hooks/idle-compact.ts); [tdimino/claude-code-minoan:plugins/jev-compact-gate/hooks/jev-compact-](https://github.com/tdimino/claude-code-minoan/blob/9f4a84393dc894c2afd6b6f748c4e523003ae08d/plugins/jev-compact-gate/hooks/jev-compact-gate.ts) | yes |
| 96 | - | view | `Ivlad003/context-gate@d4435f1ce5a78422c8dc75bf779b6026fd33c8a7:hooks/register.ts` | 1 | [hooks/register.ts](https://github.com/Ivlad003/context-gate/blob/d4435f1ce5a78422c8dc75bf779b6026fd33c8a7/hooks/register.ts) | yes |
| 97 | - | view | `ambervdberg/smartcompact@c8a1e691337bebc2b478cf6a28ebc2b65b5dda5e:plugin/smartcompact/hooks/register.ts` | 1 | [plugin/smartcompact/hooks/register.ts](https://github.com/ambervdberg/smartcompact/blob/c8a1e691337bebc2b478cf6a28ebc2b65b5dda5e/plugin/smartcompact/hooks/register.ts) | yes |
| 98 | - | view | `anton-abyzov/specweave@e4d60df99e2d89164f33efa368143713fb908847:src/cli/commands/autocompact.ts` | 1 | [src/cli/commands/autocompact.ts](https://github.com/anton-abyzov/specweave/blob/e4d60df99e2d89164f33efa368143713fb908847/src/cli/commands/autocompact.ts) | yes |
| 99 | - | view | `scasella/claude-flightdeck@6150b9f40b0a36e42c22d39f03ddb81aaefe1844:hooks/register.tsx` | 1 | [hooks/register.tsx](https://github.com/scasella/claude-flightdeck/blob/6150b9f40b0a36e42c22d39f03ddb81aaefe1844/hooks/register.tsx) | yes |

## 6. Seed-to-search map (stage-1 row to stage-2 calls)

| stage-1 seq | provider: query | stage-2 seqs |
| --- | --- | --- |
| 8 | webclaw: `https://code.claude.com/docs/en/model-config.md` | 54, 70 |
| 25 | serper: `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | 52, 61, 62, 65, 68, 78, 87, 88, 89 |
| 26 | serper: `claude code "autoCompactWindow" modelSettings per model` | 53, 67, 69, 77, 79, 86, 90 |
| 28 | serper: `claude code mod "session.compact" "session.usage"` | 55, 74, 75, 93, 94, 95, 96, 97, 99 |
| 29 | serpapi: `"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE" settings.json env` | 57, 58, 63, 64, 66, 73, 76, 80 |
| 30 | webclaw: `https://spec-weave.com/docs/guides/claude-code-auto-compact/` | 60, 81, 91, 92, 98 |
| 39 | last30days: `"Claude Code auto-compact window autocompact threshold" --quick --emit json --no` | 59, 82, 83, 84, 85 |
| 40 | local-read: `MP offline/research/R22-cc-2.1.300/raw/CHANGELOG-v2.1.300.md (grep autocompact\|` | 56, 71, 72 |

Stage-1 names with no stage-2 call of their own: #31806 and #36381 (closed duplicates, quoted in #57567, seq 63); #66144 and #43989 (v2.1.92-era thresholds, superseded by the 2.1.260 and 2.1.288 entries); #42817 and #24828 (pre-2.1.221 behaviour); karanb192/cache-tax and the usage-quota mod (seq 95 covered the same API pattern); guilhermegor/dotfiles-linux-dev#744 and Edmonds-Commerce-Limited/claude-code-hooks-daemon#46 (repo preflight seq 51 ran; their titles only restate a 75% override and a window check).

## 9. Routes table

| stage | route | command shape (no secrets) | calls | failed | hits (sum) | used |
| --- | --- | --- | --- | --- | --- | --- |
| preflight | context7 | `fnox ... exec -- ctx7 whoami, library, docs` | 1 | 0 | 0 | 1/1 |
| preflight | exa | `fnox ... exec -- http.py POST api.exa.ai/search (x-api-key from env)` | 1 | 0 | 0 | 1/1 |
| preflight | firecrawl | `fnox ... exec -- firecrawl credits --json` | 1 | 0 | 0 | 1/1 |
| preflight | github | `fnox ... exec -- gh api rate_limit, repos/<r>` | 7 | 0 | 0 | 7/7 |
| preflight | last30days | `fnox ... exec -- python3 (mise latest) -I last30days.py <topic> --quick --emit json --web-backend serper` | 1 | 0 | 0 | 1/1 |
| preflight | serpapi | `fnox ... exec -- http.py GET serpapi.com/{account.json,search.json} (api_key from env)` | 1 | 0 | 0 | 1/1 |
| preflight | serper | `fnox ... exec -- http.py POST google.serper.dev/search (X-API-KEY from env)` | 1 | 0 | 0 | 1/1 |
| 1 | context7 | `fnox ... exec -- ctx7 whoami, library, docs` | 3 | 0 | 13 | 3/3 |
| 1 | exa | `fnox ... exec -- http.py POST api.exa.ai/search (x-api-key from env)` | 5 | 5 | 0 | 0/5 |
| 1 | last30days | `fnox ... exec -- python3 (mise latest) -I last30days.py <topic> --quick --emit json --web-backend serper` | 1 | 0 | 7 | 1/1 |
| 1 | serpapi | `fnox ... exec -- http.py GET serpapi.com/{account.json,search.json} (api_key from env)` | 1 | 0 | 9 | 1/1 |
| 1 | serper | `fnox ... exec -- http.py POST google.serper.dev/search (X-API-KEY from env)` | 4 | 0 | 39 | 4/4 |
| 1 | webclaw | `webclaw <url> -f markdown > offline/pages/<name>.md` | 18 | 0 | 18 | 14/18 |
| local | local-read | `read-only file reads; strings(1) on the installed 2.1.300 binary` | 6 | 0 | 85 | 6/6 |
| 2 | gh-code-search | `fnox ... exec -- gh api -X GET search/code -f q=<q>` | 1 | 0 | 256 | 1/1 |
| 2 | gh-code-search-saved | `fnox ... exec -- gh api -X GET search/code -f q=<q> repo:<r>` | 7 | 0 | 201 | 7/7 |
| 2 | gh-code-view | `fnox ... exec -- gh api -H Accept:raw repos/<r>/contents/<p>?ref=<sha>` | 4 | 0 | 4 | 4/4 |
| 2 | gh-graphql-discussion | `fnox ... exec -- gh api graphql search(type:DISCUSSION)` | 2 | 0 | 6 | 0/2 |
| 2 | gh-issue-search | `fnox ... exec -- gh search issues <q> [--repo r] --limit 20 --json ...` | 8 | 0 | 121 | 8/8 |
| 2 | gh-issue-view | `fnox ... exec -- gh issue view <n> --repo <r> --comments --json ...` | 21 | 0 | 21 | 20/21 |
| 2 | gh-pr-search | `fnox ... exec -- gh search prs <q> --limit 20 --json ...` | 1 | 0 | 20 | 1/1 |
| 2 | gh-pr-view | `fnox ... exec -- gh pr view <n> --repo <r> --comments --json ...` | 4 | 0 | 4 | 4/4 |
