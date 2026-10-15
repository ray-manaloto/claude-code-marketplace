# R23: auto-compaction at 40% of the model's context limit (research, 2026-10-14)

Written by research agent R23 of session `ccm-20261014` (`ce9c0b3d`) for request R-179 (decision D188,
record DL-241): "add a claude code mod if necessary to be able to change the compaction from 700K to 40%
of the model's context limit". Read-only apart from the session scratchpad. MP at `1fb23d1`, branch
`codex/marketplace-native-onboarding`, Git dir `.git`; installed CLI `2.1.300 (Claude Code)`, binary
`~/.local/share/claude/versions/2.1.300` (SHA-256 `475517ca…e2d3`, build `c6733ae1`, 2026-10-14T12:54:55Z).
The run followed `docs/agents/research-workflow.md`: D142 preflight, stage 1, stage 2 seeded by stage 1,
the saved-search route, every provider call under the fnox `codex_research` profile, `webclaw` for pages,
`gh` for reads only. The query log and log-built tables are also in `R23-compaction-percent-log.md`.

Citation keys. S = the scratchpad run directory `…/scratchpad/r179/`; O = `S/offline/` (mirror, D110);
PG = `O/pages/<name>.md` (webclaw copies fetched 2026-10-14, `name.md:N` is line N); GH = `O/gh/<owner>_<repo>-<n>.json`;
`seq N` = row N of `O/queries.jsonl`; CC#n = anthropics/claude-code issue n. BIN = `S/local/cc-2.1.300.strings`
(`strings -n 6` of the installed binary; `BIN:N` is line N, minified names as shipped). T =
`MP/offline/research/R7-mods-switch-detection/types/claude-code-2.1.296.d.ts` (mods types written by 2.1.296).
CL = `MP/offline/research/R22-cc-2.1.300/raw/CHANGELOG-v2.1.300.md`; R22D = `MP/offline/research/R22-cc-2.1.300/raw/docs/`
(fetched 2026-10-14T23:43:57Z). MREF299 = `…/scratchpad/research5/R1/docs/mods_reference-raw.md` (2.1.299 copy).
P = `MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.

## 1. Verdict

**No mod. Set `"autoCompactWindow": 400000` in the project `.claude/settings.json` (replacing 700000), leave
every other compaction knob alone, and move the doctor and frontier thresholds below the new compaction
point in the same change set.** All four models the repo uses have a 1M-token window, so 40% of each limit is
400,000 tokens and one top-level value is the whole per-model table. Confidence: high on the mechanism (docs,
the 2.1.300 binary and three independent third-party derivations agree); medium on runtime behaviour until
one live receipt is taken (section 11).

Evidence that decides it:

1. **There is no native percentage-of-model-context setting.** `autoCompactWindow` takes tokens, 100000 to
   1000000, capped at the model's window (R22D `settings-reference.json`, `autoCompactWindow`; PG
   `cc-env-vars.md:209`); `/autocompact` and `--autocompact` take `auto` or a size (`500k`, `1M`, `200000`, or
   100 to 1000 meaning thousands), never a percent (PG `cc-commands.md:59`, `cc-cli-reference.md:72`,
   `cc-model-config.md:716` "Set the auto-compact window"; parser `E9t` in BIN:355730 accepts `auto`, `k`, `m`
   or a number only). The open feature request for "compact at N% of context" is CC#75335 (2026-07-07, open).
2. **The one percentage knob is the wrong percentage and unreliable.** `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is a
   percent "of the auto-compact window", can only lower the threshold, and "applies only in sessions that
   compact before the model's context limit" (PG `cc-env-vars.md:191`; R22D `env-vars.md:195`). In the binary it
   is read as `testPctOverride` and applied as `min(floor(effectiveWindow × pct/100), effectiveWindow − 13000)`
   where `effectiveWindow = window − min(maxOutputTokens, 20000)` (BIN:355730, functions `_ge`, `x9`, `h8`,
   `apr=20000`); remote forks ignore it (BIN:229520). It stacks with any window: with today's 700000 it would
   fire at 272,000, and with a lane's frontmatter window of 200000 at 72,000 (aeghnnsw/cc-toolkit#243, closed
   2026-09-22, derives the same formula for 2.1.280). Users report it ignored from the settings `env` block
   (CC#63186, 2026-05-28, closed stale; CC#57567) and silently dead since 2.1.220 (CC#82761, 2026-07-31, open).
3. **A per-model value exists and is configuration, not logic.** `modelSettings.<canonical id>.autoCompactWindow`
   (2.1.288+, any settings file, tokens or `"auto"`) is what `/autocompact` writes; per model it beats a
   top-level key in the same file, and a higher-precedence file's top-level key replaces lower files'
   per-model entries (R22D `settings-reference.json` `modelSettings`; PG `cc-settings.md:251`; BIN:355730
   `w9t`, `Pls`; observed on 2.1.296 by melodic-software/claude-code-plugins#6930). Because the four models share
   one window, the top-level key expresses the table with no new project key, while a `modelSettings` block
   would trip the doctor's `I.settings-non-project-key` P1 (`MP/dev/doctor/settings.py:14`).
4. **A mod could do it only with logic or with side effects the project should not take.** `$.settings` is
   read-only (PG `cc-mods-reference.md:212`; T:3572); `$.command.run({command: "autocompact"})` writes the
   user's `~/.claude/settings.json` and is shadowed by the project's own top-level key (T:3073; PG
   `cc-model-config.md:716`); a true percentage needs `$.session.usage()` plus a comparison plus
   `$.session.compact()` (T:2845-2882), which is logic ADR 0008 puts in the C++ core, and mods are subject to
   the rollout switch and the `sec-default` hold on `session.compact` (CC#102134, 2026-10-14). Section 7.3.
5. **Others converged on the same answer.** Anthropic's Lydia Hallie recommends `/autocompact 400k` (cited by
   PG `specweave-auto-compact.md`; x.com post not fetched); SpecWeave writes `"autoCompactWindow": 400000` into
   new projects' `.claude/settings.json` (anton-abyzov/specweave `src/cli/commands/autocompact.ts@e4d60df`);
   DevCrop/ai-setup#13 (merged 2026-10-09) does the same.

What 400000 means in tokens: compaction fires at `400000 − 20000 − 13000 = 367,000` tokens (36.7% of 1M), the
same 33K offset that puts the 1M default at "about 967K" (PG `cc-model-config.md:716` "Default auto-compact
thresholds"; CC#96467 comment 2026-10-03; CC#75335 comment 2026-08-30). Today's 700000 fires at 667,000. If the
user wants compaction itself to fire at 400,000, the value is `433000` (open question U1, section 11).

| Configuration (1M model) | Fires at | % of 1M |
| --- | --- | --- |
| Nothing set (model default) | 967,000 | 96.7 |
| `autoCompactWindow: 700000` (today) | 667,000 | 66.7 |
| `autoCompactWindow: 433000` | 400,000 | 40.0 |
| `autoCompactWindow: 400000` (recommended) | 367,000 | 36.7 |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=40`, no window | 392,000 | 39.2 |
| PCT 40 with today's 700000 left in place | 272,000 | 27.2 |
| PCT 40 with window 400000 | 152,000 | 15.2 |
| PCT 40 in a lane with frontmatter `autoCompactWindow: 200000` | 72,000 | 7.2 |

### Answers to the five questions

**Q1. Native percentage?** No settings key, `/autocompact` form or managed setting takes a percentage
(evidence 1). The env var `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is a percentage of the effective auto-compact
window, lower-only, internally a test override, with an open "stopped working" report (evidence 2). Per model:
yes, `modelSettings.<canonical id>.autoCompactWindow`. It is stored in a settings file: `/autocompact` writes
it to the **user** file `~/.claude/settings.json` under the current model's canonical name (`claude-opus-5-5`,
matching aliases, `[1m]` and provider IDs; R22D `settings-reference.json` `modelSettings`); by hand it can
live in any file (user, project, local, managed). Before 2.1.288 the command wrote the top-level key (CL:982).
`--autocompact` is per launch; `CLAUDE_CODE_AUTO_COMPACT_WINDOW` is per process and beats the flag, every
settings file and subagent frontmatter (PG `cc-env-vars.md:209`; BIN:355730 `bS`). Managed settings can set
the same keys at the top of the precedence stack (PG `cc-settings.md:227-240`); none exist on this machine
(`/Library/Application Support/ClaudeCode/managed-settings.json` absent).

**Q2. Context limits.** Fable 5.1 (`claude-fable-5-1`), Opus 5.5 (`claude-opus-5-5`), Sonnet 5.5
(`claude-sonnet-5-5`) and Haiku 5.5 (`claude-haiku-5-5`) all have a 1M window and 128K max output (PG
`platform-models-overview.md` comparison table; `platform-context-windows.md:57,60`), and Claude Code runs all
four at 1M by default with no `[1m]` suffix, on every plan (PG `cc-model-config.md:716` "Extended context",
"Haiku 5.5 context window and pricing"; plan limits apply only to Opus 4.6 and Sonnet 4.6 `[1m]`). 40% = 400,000
tokens for each; `P/frontier.toml:25-29` already records 1,000,000 for all four. Haiku 5.5 prompts over 100K
tokens bill at a higher rate (PG `platform-context-windows.md:60`), which matters for the `extractor` lane.
Exceptions: `CLAUDE_CODE_DISABLE_1M_CONTEXT=1` or a gateway that stops at 200K makes 40% = 80,000, below the
100,000 floor of every window setting; none is set here (checked one variable at a time).

**Q3. A mod?** Possible but not needed; details in section 7.3. The native static value keeps logic out of
the mod entirely; a `modelSettings` table would also be static configuration, not logic.

**Q4. Interactions.** Lanes inherit the session window and frontmatter `autoCompactWindow` can only lower it
(T:502-506; PG `cc-sub-agents.md:1144`), so a lane value of 400000 or more does nothing once the project is at
400000. The doctor's four thresholds all sit above the new 367K trigger and must move (section 7.5). The
prompt cache is invalidated at every compaction either way; a lower window trades fewer cached tokens per
turn for more frequent summarisation calls (section 7.6). Idle compaction keeps its default, per D188.

**Q5. Recommendation and owners.** Section 7.7.

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


## 7. Findings with citations

### 7.1 How 2.1.300 resolves the window and the trigger

Window, per model, first match wins (BIN:355730, `bS` then `dro`):

1. A subagent's frontmatter ceiling lowers whatever the steps below give, unless the source is the env var.
2. `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (clamped to 100,000 minimum, capped at the model window), source `env`.
3. Settings: the model's `modelSettings` entry, else the top-level `autoCompactWindow`; `"auto"` falls through.
   Across files (`w9t`, `Pls`): sources are read low to high; a source that sets a top-level key resets the
   per-model map to its own entries, a source with only per-model entries merges over lower ones. So the
   project's top-level 700000 today outranks any `/autocompact` value saved in user settings, and a
   `.claude/settings.local.json` per-model entry outranks the project's top-level key. melodic-software/claude-code-plugins#6930
   (2026-10-11) observed exactly these rows on 2.1.296 with `claude -p "/autocompact"`.
4. Account window from the server (`clientdata`), then an experiment value (desktop entry point: 500K or 600K;
   `claude-sonnet-5` on remote cowork or local agent: 500K), then the model default (the full 1M for native-1M
   models), then `unknown-model`, then `auto`. A settings value therefore beats the server window that CL:961
   applies from the first request.

The `--autocompact` flag sits between the env var and settings and is not preempted by managed settings
(PG `cc-model-config.md:716`). `/autocompact` with no argument reports the window and its source
(`default for this model`, `from settings`, `from CLAUDE_CODE_AUTO_COMPACT_WINDOW`; BIN:208369; PG
`wmedia-auto-compact-window.md`).

Trigger (BIN:355730, `h8`, `x9`, `jGe`): `effective = window − min(maxOutputTokens, 20000)`; `threshold =
effective − 13000`, or with the percentage override `min(floor(effective × pct / 100), effective − 13000)`.
Warn at `effective − 20000`; blocked at `contextWindow − min(maxOutputTokens, 20000) − 3000`. The `/context`
breakdown reports `autoCompactThreshold` and the window source (T:2312, T:10936), while the status line's
`used_percentage` always measures against the full model window (PG `cc-env-vars.md:209`), so at the 367K
trigger the status line reads about 37%.

### 7.2 The percentage override in detail

- Docs: PG `cc-env-vars.md:191` (quoted in evidence 2); applies to subagents (R22D `sub-agents.md:1131`).
- Binary: the value is parsed per call from `process.env` (`_ge`, BIN:355730), named `testPctOverride`, and
  skipped for remote side-question and memory forks (BIN:229520). The settings `env` block is assigned to
  `process.env` (BIN:350887), and the variable is on the list Claude Code applies even before workspace trust
  (`vht`, set `jy`, BIN:347036). So on 2.1.300 the `env` block route looks wired; this is UNVERIFIED live.
- Reports: ignored from the `env` block through 2.1.187 (CC#63186, closed stale 2026-08-25); ignored through
  2.1.138 (CC#57567); stopped taking effect after 2.1.220 even from the shell (CC#82761, open, with
  transcript data); ignored in remote or bridge sessions (CC#70477, open); the reported effective point is
  invisible to `get_context_usage` (CC#97568, open).
- elkisdm/devground#104 (2026-10-10, open) chose `autoCompactWindow: 1000000` plus a 50% override and records
  the same caveats: a test setting in the code, ignored by forks.
- Secondary sources that state the override is a share of the model window (PG `turboai-pct-override.md:336`:
  "75 means ~750K") contradict the binary and are not used.

### 7.3 What a mod could do (2.1.296 types, 2.1.299 and 2.1.300 docs)

| Route | Works? | Why it is not the answer |
| --- | --- | --- |
| `$.settings` write | No | `read` only (T:3572; PG `cc-mods-reference.md:212`; MREF299:193) |
| `$.config.set` | No window row | the built-in row is `autoCompact`, the on/off toggle (T:2049) |
| `$.command.run({command: "autocompact", args: "400k"})` at `session.start` or after a model switch | Runs as if typed, queued until idle (T:3073-3083) | writes the user's file (a user-scope write each time), only for the current model, and loses to the project's top-level key (§7.1) |
| `$.env.set("CLAUDE_CODE_AUTO_COMPACT_WINDOW", "400000")` at `session.start` | Plausible: `bS` reads `process.env` per call, `$.env.set` changes "this process" (T:3607) | UNVERIFIED in the running resolver; the env var also disables every lane's frontmatter window (PG `cc-sub-agents.md:1144`) |
| `session.measure` or `turn.complete`: `const { context } = await $.session.usage(); if (context.percent >= 40) await $.session.compact()` | Yes; the types ship this exact pattern at 85% (T:2845-2846); `context.percent` is tokens over the model's full window (T:10954-10975) | the comparison is logic (ADR 0008: mods hold none and call `rsm-core` through `$.process.run`, which does not exist yet); `compact()` rejects while a turn runs, so it only fires between turns while the native threshold also fires between steps (T:2872-2880); mods are fail-open under the rollout switch and the `sec-default` hold (CC#102134; `MP/docs/agents/hooks-and-mods.md:104-108`) |
| model change event | No mod event; settings hook `PostModelSwitch` (2.1.251, CL:3018; T:7806) is reachable only as `classic.PostModelSwitch`, whose delivery to modules is itself on the watch list | nothing needs to react: settings resolve per model natively |

Third-party mods that compact on a usage threshold exist (section 8), which confirms the route works, and
none is needed here. A native static value, or a static `modelSettings` table, carries no logic.

### 7.4 Subagents and lanes

- Frontmatter `autoCompactWindow` (2.1.296, CL:290) only lowers the inherited window (T:502-506); a value not
  below it has no effect, and the env var overrides it (PG `cc-sub-agents.md:1144`). None of MP's six agent
  files sets it today (`MP/.claude/agents/*.md`).
- With a project window of 400000, every lane compacts at about 367K unless its frontmatter is lower. The
  2.1.300 intake's suggestion to set frontmatter windows per role (`P/reviews/ccm-20261014/cc-2.1.300/impact.md:14`)
  becomes optional; a lane frontmatter value would have to be below 400000 to matter.
- Never combine the percentage override with lane frontmatter: the two multiply (table in section 1).
- Open upstream: subagent compaction resolving its window from the main session's model (CC#83355, open);
  irrelevant while all four models share 1M. Per-agent and session-scoped windows are requested in CC#90347
  and CC#97733.
- `/autocompact` in a running session cannot override the project key (§7.1); for a personal value in this repo
  use `.claude/settings.local.json` or `claude --autocompact <n>`.

### 7.5 The doctor and the frontier thresholds

Today `MP/dev/doctor/budget.py:8-9` holds `warn 400K, checkpoint 550K, fork_deny 500K, hard 650K`, "all below the
project autoCompactWindow (700000)"; `MP/dev/test_doctor.py:131-132` asserts the live window is 700000,
`:143-155` asserts every threshold is below the window and `fork_deny == context_ceiling_fraction ×
windows.opus` (0.5 × 1,000,000, `P/frontier.toml:11,25-29`), and `:158-164` asserts the
`docs/agents/claude-team.md` table equals `THRESHOLDS`. `dev/test_ticket_frontier.py:162-172,191-200` copies the real
`frontier.toml` and asserts a 500000 ceiling.

At a 367K trigger all four thresholds sit above the point where the parent compacts, so none would ever fire,
and with only the settings change `test_doctor.py` fails (400_000 is not below 400000). Proposed set, all below
367K, order kept, round numbers: **warn 200K, fork_deny 250K, checkpoint 300K, hard 350K**, with
`context_ceiling_fraction = 0.25` (0.25 × 1M = 250K = `fork_deny`). A proportional alternative (the old ratios
to the 667K trigger) is 220K, 275K, 303K, 358K. Warn at 200K coincides with idle compaction's minimum, which
D188 keeps. The values stay a static table; deriving them from the window is new logic and belongs to the C++
doctor port (R-122, #117).

### 7.6 The prompt cache

- Compaction replaces the history, so it always invalidates the conversation layer; the summary request reads
  the prefix from a warm cache, and after the cache lifetime it reprocesses the whole history uncached (PG
  `cc-prompt-caching.md:172-181`). A lower window does not change this; it changes how often it happens and how
  much each turn re-reads before it does (at most about 367K cached tokens per request instead of about 667K).
- Each auto-compaction took 50 to 83 seconds in CC#101067's data; a 1M session growing at the same rate
  compacts about 1.8 times as often at 400000 as at 700000.
- The 2.1.300 binary still shows "Overriding auto may result in high token usage, especially when resuming long
  sessions" in the `/autocompact` dialog (BIN:208369), but 2.1.300 fixed that warning firing when the user picks
  a smaller window (CL:14). sthe0/claude-agent-instructions#167 measured a flat cost curve across 120K to 400K
  windows on its workload.
- Idle compaction (default on, 200K minimum, about 54 minutes idle, one-hour TTL; R22D `settings-reference.json`
  `idleCompaction`) still applies between 200K and the trigger. Idle compactions record `trigger: "auto"`
  and look like a low threshold in transcripts (CC#101067, CC#100277), so any receipt must exclude rows
  carrying "Compacted while idle, before the prompt cache expired".
- Model switches already cost a full uncached read (each model has its own cache; PG `cc-settings.md:203`);
  the window choice does not add to that. Subagents keep separate caches and are unaffected by the parent's
  compaction (R22D `sub-agents.md:1125`).
- A settings edit to the window reached sessions only at the next process start in one report (CC#96467
  comment, 2026-10-02), while the settings page lists only `model`, `effortLevel` and `modelSettings` as
  session-start keys (PG `cc-settings.md:201-204`). Restart after the change; R-175's quit-and-restart flow fits.

### 7.7 Recommendation: settings, files, doctor changes and owners

| # | Change | File | Owner, admission |
| --- | --- | --- | --- |
| 1 | `"autoCompactWindow": 700000` → `400000`; keep `autoCompactEnabled: true`; add no `idleCompaction`, no `modelSettings`, no `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` or `CLAUDE_CODE_AUTO_COMPACT_WINDOW` in `env` | `.claude/settings.json` | parent (hot path, `P/frontier.toml:45`) |
| 2 | window assertion 700000 → 400000 | `dev/test_doctor.py:131-132` | lane with change 1 (test-only edit) |
| 3 | `THRESHOLDS = {"warn": 200_000, "checkpoint": 300_000, "fork_deny": 250_000, "hard": 350_000}` and the comment ("below the trigger of the project autoCompactWindow 400000, about 367K") | `dev/doctor/budget.py:8-9` | dev lane; a constant fix, allowed for existing Python (ADR 0008) |
| 4 | thresholds dict in the test; optionally tighten to `value < window − 33_000` | `dev/test_doctor.py:148-155` | same lane |
| 5 | Context budget table and the "(700000, …)" sentence | `docs/agents/claude-team.md:117-126` | doc lane (hot path) |
| 6 | `context_ceiling_fraction = 0.5` → `0.25` | `P/frontier.toml:11` | parent, a `propose` item applied after the user says so (`frontier.toml:2-4`) |
| 7 | 500000 → 250000 ceilings and the mismatch fixture | `dev/test_ticket_frontier.py:162-172,191-200` | dev lane |
| 8 | "500 K today", "warn (400 K)", the ceiling column, "below the project autoCompactWindow 700000", "80 % of the ceiling (400 K at 500 K)" | `.claude/skills/ticket-frontier/SKILL.md:76-78`, `references/model-policy.md:9-18,44-48`, `references/config.md:11`, and the `.agents/skills/ticket-frontier/` mirror | doc lane; both copies together (`.claude/AGENTS.md`) |
| 9 | none | `~/.claude/settings.json` | no user-settings change is needed; `autoCompactEnabled: true` stays, and its `modelSettings` holds effort levels only |

Ordering. `frontier.toml` lets one candidate touch at most one hot path (`P/frontier.toml:44-45`), and both
`.claude/settings.json` and `docs/agents/claude-team.md` are hot. Step A (changes 3 to 8) is valid under both
windows because every new threshold is below 367K and 667K; step B (changes 1 and 2) follows. The parent may
instead apply both as parent-owned edits with a recorded exception. Run `./dev/mise tasks validate`,
`./dev/mise run check` and `./dev/mise run check:acceptance-baseline` after each step.

Verification after restart (typed by the user, or the CT-87 live probe with its own admission): `/autocompact`
prints `Auto-compact window for Opus 5.5: 400k tokens (from settings)`, `/context` shows the window, and the
receipt is the first non-idle `compact_boundary` with `trigger: "auto"` and `preTokens` near 367,000.

Watch (add to CT-80's list): CC#82761, CC#75335 (native N% setting), CC#96467 and CC#97568 (effective threshold
in the status line and `get_context_usage`), CC#83355, CC#102134, and any changelog entry naming
`autocompact`, `autoCompactWindow` or `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`.

## 8. Code examples found

| Repository | Path and commit | What it shows |
| --- | --- | --- |
| anton-abyzov/specweave | `src/cli/commands/autocompact.ts@e4d60df99e2d89164f33efa368143713fb908847` (O `code/`) | reads user < project < local and `modelSettings.<model>.autoCompactWindow`; writes `"autoCompactWindow": 400000` to a project `.claude/settings.json` |
| DevCrop/ai-setup | PR #13 (merged 2026-10-09), `claude/settings.json` | `"autoCompactWindow": 400000` committed, with the precedence written down |
| liminal-ai/t3code-lim | PR #31 (merged 2026-10-10) | default window 700000, lowered to 80% of a smaller model window |
| kunchenguid/firstmate | PR #6272 (closed 2026-10-01), `bin/fm-spawn.sh` | `"autoCompactWindow": 220000` passed through `--settings` per worker launch |
| elkisdm/devground | PR #104 (open) | `autoCompactWindow: 1000000` plus a 50% override, with the test-setting caveat |
| Ivlad003/context-gate | `hooks/register.ts@d4435f1ce5a78422c8dc75bf779b6026fd33c8a7:342-346` | a mod checking budgets on `session.measure` with `e.context.percent`, wrapping `$.session.compact` |
| ambervdberg/smartcompact | `plugin/smartcompact/hooks/register.ts@c8a1e691337bebc2b478cf6a28ebc2b65b5dda5e:118-181` | a mod driving `$.session.usage` and `$.session.compact` around `session.compact` |
| scasella/claude-flightdeck | `hooks/register.tsx@6150b9f40b0a36e42c22d39f03ddb81aaefe1844` | `turn.step`, `session.measure`, `session.compact` and `$.session.usage()` in one mod |
| aeghnnsw/cc-toolkit | issue #243 (closed 2026-09-22) | the trigger formula and the stacking of the override with a window |

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

## 10. Proposed saved-search rows

Not added; `dev/saved-searches.toml` is untouched. Shape copied from the rows already there; hit counts from
seq 88 to 94.

```toml
# Auto-compaction window and percentage (research R23, R-179, D188, 2026-10-14)
[[search]]
id = "cc-autocompact-window"
query = "autoCompactWindow"
repo = "anthropics/claude-code"        # 1 hit today (feed.xml); control README 42
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "cc-autocompact-pct"
query = "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"
repo = "anthropics/claude-code"        # 0 hits today: a hit means the repo now documents or ships the override; control README 42
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "specweave-autocompact"
query = "autoCompactWindow"
repo = "anton-abyzov/specweave"         # 6 hits; control README 147
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "flightdeck-session-compact"
query = "session.compact"
repo = "scasella/claude-flightdeck"     # 2 hits; control README 3
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 11. Open gaps

Provider gaps (logged, not silent):

- Exa: all five stage-1 queries returned HTTP 402 `NO_MORE_CREDITS` (seq 17 to 21); its share of discovery came
  from Serper, SerpApi, Context7 and Last30Days.
- Firecrawl: skipped at preflight, `remainingCredits` -128 of 1,000 (seq 1); webclaw fetched every page.
- Last30Days' planner chose GitHub and web grounding only; Reddit, X and YouTube returned nothing (seq 39).
  The Reddit thread from Serper came back as 252 bytes (seq 35).
- The Lydia Hallie post is cited through the SpecWeave page only; x.com was not fetched.

Unverified, needing one admitted live probe (no `claude` session was started here):

- The 367K trigger for a 400000 window on 2.1.300, read from the binary and three third-party derivations.
  Fleet data from 2.1.251 to 2.1.263 showed a configured window not matching observed triggers (CC#75335
  comments, CC#82761 comment of 2026-09-07); window-resolution fixes landed later (CL:961, CL:1208, CL:982),
  and idle compaction now confounds such data. The receipt in section 7.7 settles it.
- Whether a window edit applies to a running session or only at the next process start.
- Whether `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` from the settings `env` block takes effect on 2.1.300; the binary
  says it should, CC#82761 says it stopped working after 2.1.220.
- Whether a mod's `$.env.set("CLAUDE_CODE_AUTO_COMPACT_WINDOW", …)` reaches the in-process resolver.
- The 20,000 output reserve assumes each model's `maxOutputTokens` in Claude Code is at least 20,000 (all four
  list 128K max output).

Decisions for the user:

- U1: window `400000` (compaction at about 367K, the literal "40% of the limit" as a window, matching today's
  700K semantics) or `433000` (compaction itself at 400K).
- U2: the doctor and frontier thresholds: the round set 200/250/300/350K with fraction 0.25, or the
  proportional set 220/275/303/358K.
- U3: apply as two hot-path steps (A then B, §7.7) or as one parent-owned edit with a recorded exception.

Process gaps:

- The mirror and query log live in the scratchpad because the brief forbids MP writes; the parent can copy
  `S/offline/` to `MP/offline/research/R23-compaction-percent/` (untracked corpus, D110).
- Providers `local-read`, `gh-code-search` and `gh-code-view` are outside the D137 enum; propose adding them.
- The saved-search route used `gh api search/code` equivalents, not `./dev/mise run research:collect`, which
  writes a tracked path.
