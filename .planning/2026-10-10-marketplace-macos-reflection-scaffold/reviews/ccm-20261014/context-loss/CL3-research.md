# CL3: catching lost requests across compaction, /clear, handoffs, subagents and forks

Research run CL3 of team CL, parent session `ccm-20261014` (`ce9c0b3d`), 2026-10-14. Host CLI:
Claude Code 2.1.300 (`claude --version`; the handoff noted 2.1.299; the 2.1.300 changelog entry is
dated 2026-10-14, `offline/research/CL3/docs/raw/changelog.md:13`). Route: MP's
`docs/agents/research-workflow.md` (preflight, stage 1, stage 2, saved searches). Offline mirror:
`offline/research/CL3/` with `manifest.json` (200 items, SHA-256 per file, commit per clone) and
`queries.jsonl` (231 rows). This report also tests CL2's eleven hypotheses
(`CL2-mechanism-review.md` section 4) in section 7.2.

Abbreviations: P is `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`; `D/` is
`offline/research/CL3/docs/raw/` (raw markdown of code.claude.com pages, line-addressable; the webclaw
copies sit in `offline/research/CL3/docs/`); `W/` is `offline/research/CL3/web/`; `G/` is
`offline/research/CL3/gh/`; `R/` is `offline/research/CL3/repos/`; `T` is this session's transcript
`~/.claude/projects/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34.jsonl`;
`PWF` is the installed plugin `~/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0/`.

## 1. Verdict

Recommendation (confidence: high for capture and re-injection, medium for the compaction-instruction
path, low for gate tuning): stop relying on the agent to remember. Track requests mechanically with
Claude Code settings hooks that run with zero model tokens, keep the pwf plan as the one projection
that every carry-over already reads, and put the judgement parts (matching a request to its
projection, refusing to stop) in the C++ core.

1. Capture every request at the source, with no logic. An async `UserPromptSubmit` command hook and
   an async `PostToolUse` hook matched on `AskUserQuestion`, each running `/usr/bin/jq -c .` (the OS
   jq, 1.7.1-apple) to append its stdin to an untracked ledger. The `UserPromptSubmit` payload carries
   the verbatim `prompt` plus `prompt_id`, `session_id` and `transcript_path` (`D/hooks.md:733-736`,
   `:1459-1474`); since 2.1.299 it runs before a slash command or skill expands
   (`D/changelog.md:156`), so a typed `/claude-agent ...` request is captured too. `PostToolUse`
   passes the tool's structured output (`D/hooks.md:2346`); in this session that object holds
   `answers` and, for free text, `annotations.<question>.notes` (`T` L5663 uuid
   `232723dc-912d-4752-93bc-0cbb7f795971`, L6163 uuid `a7075aa4-5bf2-4e46-8bb9-f6d6f73f0267`).
   `prompt_id` is a UUID that also keys OpenTelemetry events, so it can be the request key without a
   counter.
2. Carry the open list across every boundary through surfaces that are documented to fire:
   - Every turn and after `/clear`, resume and compaction: pwf already injects the plan
     (`PWF/hooks/hooks.json:4-21`). It did so after all three compactions of this session
     (`hook_success SessionStart:compact` then `hook_additional_context` at `T` L2467-2468,
     L5053-5054, L7369-7370). Keep the open requests, each with its id and issue link, inside
     `## Next Step` and turn on pwf `inject-smart` so that section is always extracted
     (`PWF/scripts/inject-plan.sh:1005-1066`). A `## Requests` heading would not be extracted.
   - Into the summary itself: Claude Code 2.1.300 appends a `PreCompact` hook's exit-0 stdout to
     the compaction request's custom instructions. The public hooks page does not say so, but the
     binary's own hook help text does ("Exit code 0 - stdout appended as custom compact
     instructions", `offline/research/CL3/binary/hook-help-2.1.300.txt:2`, from `strings` on the installed 2.1.300 binary), and
     [#101057](https://github.com/anthropics/claude-code/issues/101057) (open, 2026-10-10) reads the
     2.1.292 and 2.1.296 bundles and finds it on the auto, reactive and manual paths, with no size
     limit. A short `PreCompact` hook printing the open list therefore lands in the summarizer's
     instructions, next to the built-in "All user messages" and "Pending Tasks" sections
     (`offline/research/CL3/binary/compact-prompt-2.1.300.txt:4-13`).
   - Into every subagent: a `SubagentStart` hook's `additionalContext` reaches the subagent before its
     first prompt (`D/hooks.md:2534-2544`).
3. Catch drops with a gate, in C++. A `Stop` (and `SubagentStop`) gate that blocks once when a
   captured request has no projection is new logic, so it belongs in the C++ port of
   `stop_gate.py` (D112, D113, D131). It must honour `stop_hook_active`, the 8-continuation cap
   (`D/hooks.md:2705-2709`) and prefer `additionalContext` feedback over a hard block
   (`D/hooks.md:2786`). Until it exists, layers 1 and 2 make a drop visible on every turn rather than
   preventing it.
4. Link to GitHub through MP's qualified route, never a direct `gh issue create`
   (`docs/agents/issue-tracker.md:50-56`). The link is the ticket-ledger row (`R-n` to `CT-n`,
   "pending issue") until `/to-tickets` publishes through `issue:create-preview/apply/verify`, whose
   manifest already carries `parent_number` (`dev/issue_create.py:24-32`). The host `gh` 2.98.0 also
   has native `--parent`, `--blocked-by` and `--blocking` flags, and GitHub's REST API has sub-issue
   and `dependencies/blocked_by` endpoints (`W/gh-docs-sub-issues.md`,
   `W/gh-docs-issue-dependencies.md`), so no extension is needed. pwf 3.24.0 has no GitHub linkage of
   its own (grep of `PWF` finds none; pwf issue search row 419 returned 0).

Mods are not the guarantee today. A mod can see and add to prompts (`prompt.submit`,
`D/plugins_mods_events.md:207-235`) and can only skip a compaction (`session.compact` returns
`{ skip }`, `D/plugins_mods_reference.md:137`), but `session.compact` is no longer raised on 2.1.299
([#102134](https://github.com/anthropics/claude-code/issues/102134), open, filed 2026-10-14, no fix
in the 2.1.300 notes), `session.start` does not fire after `/clear`, `/resume` or `/branch`
(`D/plugins_mods_reference.md:135`), a mod blocks a stop only through `classic.Stop`, whose delivery
is still unreliable ([#96831](https://github.com/anthropics/claude-code/issues/96831),
[#100869](https://github.com/anthropics/claude-code/issues/100869), both open), and the remote switch
can turn all mods off ([#99130](https://github.com/anthropics/claude-code/issues/99130), open). A mod
must also hold no logic and call the C++ core (ADR 0008), which is not built. The same reasoning
that kept the three deny gates as hooks (D102) applies to a ledger that must not miss; adding these
hooks needs a new decision, because D92 sends every other new behaviour to mods.

Two defects found on the way, both cheap to fix:
- pwf's `PreCompact` reminder is emitted as JSON `{"systemMessage": ...}`
  (`PWF/hooks/claude-hook.sh:319-323`, `:349-353`), and Claude Code discards a PreCompact hook's
  `systemMessage` (`D/hooks.md:3257`). Being JSON, it is also not plain stdout, so it is probably not
  appended to the compaction instructions either. The "flush progress before compaction" step that
  pwf documents (`PWF/docs/claude-code-lost-context-after-compaction.md:25-33`) likely never reaches
  the model. Upstream pwf issue, not MP code; confirm with the probe in section 11.
- pwf's `SessionStart` matcher is `startup|resume|clear|compact` (`PWF/hooks/hooks.json:6`), but
  since 2.1.214 a forked session (`--fork-session`, `/fork`, `/branch`, a conversation moved to the
  background) reports source `fork` (`D/hooks.md:1213-1217`). Forks get no SessionStart restore
  (their first prompt still gets pwf's UserPromptSubmit injection). MP's doctor matcher already
  includes `fork` (`.claude/settings.json`). No pwf issue covers it (row 425 returned 0).

### Classification under MP's rules

| Mechanism | Surface | MP class | Interim zero-logic option |
|---|---|---|---|
| M1 prompt capture | settings hook `UserPromptSubmit`, `async: true`, `/usr/bin/jq -c . >> <ledger>` | configuration of an existing tool; a new settings hook needs a decision beside D102 | itself |
| M2 answer capture | settings hook `PostToolUse`, matcher `AskUserQuestion`, same command | configuration | itself |
| M3 projection in `## Next Step` with `R-n` and issue link | plan convention, written by the parent (it owns shared planning files) | configuration (a skill and brief rule) | itself |
| M4 pwf `inject-smart` | `inject-smart` token in `P/.mode`, or `PWF_INJECT=smart` in the host env (`PWF/skills/planning-with-files/SKILL.md:395-397`) | configuration (CT-30) | itself |
| M5 open list in the compaction instructions | settings hook `PreCompact` printing the `## Next Step` section (`sed -n` range or `cat` of a short file) | configuration; needs the probe | itself |
| M6 compaction focus in `CLAUDE.md` | a `# Compact instructions` section (`D/costs.md:241-249`) | documentation edit | itself; auto-compaction effect UNVERIFIED |
| M7 open list into subagents | settings hook `SubagentStart`, `/usr/bin/jq -Rs '{hookSpecificOutput:{hookEventName:"SubagentStart",additionalContext:.}}' <file>` | configuration | itself |
| M8 summary archive | settings hook `PostCompact`, async `cat >> <file>` (not jq: [#89622](https://github.com/anthropics/claude-code/issues/89622), stdin can be invalid JSON) | configuration | itself |
| M9 request ids, summary audit, "unprojected request" detector, ledger-to-manifest rows | parsing and matching | new logic: C++ core (D112, D113); the doctor detector in CL2's H2 is new logic too | M3 to M8, plus the parent reviewing the ledger at each handoff |
| M10 Stop and SubagentStop gate on unprojected requests | extension of `stop_gate.py`, `subagent_stop_gate.py` | new logic: C++ under D131 | none deterministic; an `agent`-type Stop hook is configuration but experimental and model-judged (`D/hooks-guide.md:877-905`) |
| M11 Task tools as a persistent list | `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, `CLAUDE_CODE_TASK_LIST_ID` (`D/env-vars.md:299`, `:412`) | configuration; a `TaskCreated` subject rule is logic (C++) | env only |
| M12 mods (`prompt.submit`, `session.compact`, `agent.spawn`) | TypeScript mods library | a mod with no logic needs the C++ core; `session.compact` broken | not now; later the D128 shape (mod does the work, thin hook stands down) |
| M13 GitHub link | ticket-ledger row, then `issue:create-*` with a manifest | existing Python (qualified tasks; fixes only); writing manifest rows is configuration | itself |

## 2. Queries sent to each tool, plugin or service (stage 1)

Preflight rows (D142) come first. Each query is the exact text sent; `seq` is the row number in `offline/research/CL3/queries.jsonl`. Rows 60 to 86 and 201 to 219 are webclaw mirrors; rows 300 to 324 are raw-markdown companions fetched with curl because webclaw flattened most of `hooks.md` onto one line (logged under `webclaw` with a note, since the provider list has no raw-fetch value).

| seq | stage | provider | query | status | failure_code |
|---|---|---|---|---|---|
| 1 | preflight | firecrawl | firecrawl credits --json (remainingCredits=-128, planCredits=1000) | SKIPPED | CREDITS_EXHAUSTED |
| 2 | preflight | serper | GET https://google.serper.dev/account (balance=1294, rateLimit=5) | OK | NONE |
| 3 | preflight | serpapi | GET https://serpapi.com/account.json (plan_searches_left=242) | OK | NONE |
| 4 | preflight | gh-issue-search | gh api rate_limit (search=30, code_search=10, graphql=5000, core=4965) | OK | NONE |
| 5 | preflight | context7 | no credit endpoint known; ctx7 whoami not a balance check | OK | NONE |
| 6 | preflight | exa | no balance endpoint known; key set | OK | NONE |
| 11 | 1 | exa | Claude Code compaction loses user requests instructions forgotten after auto-compact | OK | NONE |
| 12 | 1 | exa | Claude Code UserPromptSubmit hook log every prompt to a file ledger | OK | NONE |
| 13 | 1 | exa | Claude Code PreCompact PostCompact hook SessionStart compact matcher re-inject context | OK | NONE |
| 14 | 1 | exa | Claude Code Stop hook block until all user requests are tracked or done | OK | NONE |
| 15 | 1 | exa | long-running agent harness planner generator evaluator Anthropic engineering | OK | NONE |
| 16 | 1 | exa | agent harness initializer feature list json progress file across context windows | OK | NONE |
| 17 | 1 | exa | track coding agent tasks as GitHub issues automatically from conversation | OK | NONE |
| 18 | 1 | exa | Claude Code mods prompt.submit session.compact hook | OK | NONE |
| 19 | 1 | exa | GitHub sub-issues REST API and issue dependencies blocked by API GraphQL addBlockedBy | OK | NONE |
| 20 | 1 | exa | GitHub Projects custom fields gh project item-add item-edit CLI automation | OK | NONE |
| 21 | 1 | exa | Claude Code hook that refuses to stop while a request has no GitHub issue | OK | NONE |
| 22 | 1 | exa | coding agent request ledger every user prompt tracked to completion across context compaction | OK | NONE |
| 23 | 1 | exa | planning-with-files task_plan GitHub issue link | OK | NONE |
| 24 | 1 | exa | Claude Code compact instructions CLAUDE.md "Compact Instructions" preserve user requests | OK | NONE |
| 30 | 1 | context7 | ctx7 library 'claude code' 'hooks PreCompact SessionStart compact' -> 'Monthly quota reached' | ERROR | CREDITS_EXHAUSTED |
| 31 | 1 | context7 | ctx7 docs /othmanadi/planning-with-files 'github issue link task_plan' -> 'Monthly quota reached' | ERROR | CREDITS_EXHAUSTED |
| 32 | 1 | firecrawl | firecrawl search 'Claude Code compaction lost user request hook ledger' --limit 5 (preflight remainingCredits=-128) | ERROR | CREDITS_EXHAUSTED |
| 41 | 1 | serper | site:github.com anthropics/claude-code issues compaction drops user request | OK | NONE |
| 42 | 1 | serper | "UserPromptSubmit" hook "prompts.jsonl" claude code | OK | NONE |
| 43 | 1 | serper | "PostCompact" "compact_summary" hook claude code | OK | NONE |
| 44 | 1 | serper | claude code mods "prompt.submit" ledger OR "open requests" | OK | NONE |
| 45 | 1 | serper | "SessionStart" "compact" hook additionalContext not injected claude code issue | OK | NONE |
| 46 | 1 | serpapi | claude code hook "decision" "block" Stop untracked user request github issue ledger | OK | NONE |
| 50 | 1 | last30days | "Claude Code losing user requests across compaction and how hooks or mods prevent it" --plan plan.json (3 subqueries; planner kept 1: compaction-loss) --emit json --quick --save-dir '' (SSL_CERT_FILE=/etc/ssl/cert.pem);  | DEGRADED | OTHER |
| 51 | 1 | last30days | "Claude Code compaction hook" --search reddit,hackernews,github --emit json --quick --save-dir ''; hackernews no-results | DEGRADED | NONE |
| 60 | 1 | webclaw | webclaw https://code.claude.com/docs/en/hooks.md -f markdown | OK | NONE |
| 61 | 1 | webclaw | webclaw https://code.claude.com/docs/en/hooks-guide.md -f markdown | OK | NONE |
| 62 | 1 | webclaw | webclaw https://code.claude.com/docs/en/context-window.md -f markdown | OK | NONE |
| 63 | 1 | webclaw | webclaw https://code.claude.com/docs/en/costs.md -f markdown | OK | NONE |
| 64 | 1 | webclaw | webclaw https://code.claude.com/docs/en/commands.md -f markdown | OK | NONE |
| 65 | 1 | webclaw | webclaw https://code.claude.com/docs/en/interactive-mode.md -f markdown | OK | NONE |
| 66 | 1 | webclaw | webclaw https://code.claude.com/docs/en/common-workflows.md -f markdown | OK | NONE |
| 67 | 1 | webclaw | webclaw https://code.claude.com/docs/en/memory.md -f markdown | OK | NONE |
| 68 | 1 | webclaw | webclaw https://code.claude.com/docs/en/sub-agents.md -f markdown | OK | NONE |
| 69 | 1 | webclaw | webclaw https://code.claude.com/docs/en/agent-teams.md -f markdown | OK | NONE |
| 70 | 1 | webclaw | webclaw https://code.claude.com/docs/en/checkpointing.md -f markdown | OK | NONE |
| 71 | 1 | webclaw | webclaw https://code.claude.com/docs/en/cli-reference.md -f markdown | OK | NONE |
| 72 | 1 | webclaw | webclaw https://code.claude.com/docs/en/headless.md -f markdown | OK | NONE |
| 73 | 1 | webclaw | webclaw https://code.claude.com/docs/en/changelog.md -f markdown | OK | NONE |
| 74 | 1 | webclaw | webclaw https://code.claude.com/docs/en/cross-session-messaging.md -f markdown | OK | NONE |
| 75 | 1 | webclaw | webclaw https://code.claude.com/docs/en/agent-view.md -f markdown | OK | NONE |
| 76 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/events.md -f markdown | OK | NONE |
| 77 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/api.md -f markdown | OK | NONE |
| 78 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/overview.md -f markdown | OK | NONE |
| 79 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/reference.md -f markdown | OK | NONE |
| 80 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/interface.md -f markdown | OK | NONE |
| 81 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/troubleshoot.md -f markdown | OK | NONE |
| 82 | 1 | webclaw | webclaw https://code.claude.com/docs/en/plugins/mods/create.md -f markdown | OK | NONE |
| 83 | 1 | webclaw | webclaw https://code.claude.com/docs/en/agent-sdk/sessions.md -f markdown | OK | NONE |
| 84 | 1 | webclaw | webclaw https://code.claude.com/docs/en/agent-sdk/todo-tracking.md -f markdown | OK | NONE |
| 85 | 1 | webclaw | webclaw https://code.claude.com/docs/en/agent-sdk/hooks.md -f markdown | OK | NONE |
| 86 | 1 | webclaw | webclaw https://code.claude.com/docs/en/agent-sdk/subagents.md -f markdown | OK | NONE |
| 201 | 1 | webclaw | webclaw https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents -f markdown | OK | NONE |
| 202 | 1 | webclaw | webclaw https://www.anthropic.com/engineering/harness-design-long-running-apps -f markdown | OK | NONE |
| 203 | 1 | webclaw | webclaw https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents -f markdown | OK | NONE |
| 204 | 1 | webclaw | webclaw https://docs.github.com/en/rest/issues/sub-issues -f markdown | OK | NONE |
| 205 | 1 | webclaw | webclaw https://docs.github.com/en/rest/issues/issue-dependencies -f markdown | OK | NONE |
| 206 | 1 | webclaw | webclaw https://github.blog/changelog/2025-08-21-dependencies-on-issues/ -f markdown | OK | NONE |
| 207 | 1 | webclaw | webclaw https://cli.github.com/manual/gh_project_item-edit -f markdown | OK | NONE |
| 208 | 1 | webclaw | webclaw https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms -f markdown | OK | NONE |
| 209 | 1 | webclaw | webclaw https://raw.githubusercontent.com/asgeirtj/system_prompts_leaks/main/Anthropic/Claude%20Code/slash-commands/compact.md -f markdown | ERROR | HTTP_ERROR |
| 210 | 1 | webclaw | webclaw https://claudecodemods.com/hooks/ -f markdown | OK | NONE |
| 211 | 1 | webclaw | webclaw https://modscode.com/claude-mods/mods/earlyaidopters-auto-handoff/ -f markdown | OK | NONE |
| 212 | 1 | webclaw | webclaw https://modscode.com/claude-mods/mods/hellosverre-smart-compact/ -f markdown | OK | NONE |
| 213 | 1 | webclaw | webclaw https://modscode.com/claude-mods/mods/kunchenguid-compact-adviser/ -f markdown | OK | NONE |
| 214 | 1 | webclaw | webclaw https://negiadventures.github.io/blog/transcript-compaction-ledgers-ai-coding-agents.html -f markdown | OK | NONE |
| 215 | 1 | webclaw | webclaw https://arxiv.org/html/2608.00808v1 -f markdown | OK | NONE |
| 216 | 1 | webclaw | webclaw https://gist.github.com/yurukusa/219bf5556f5508b0add25d0be47534fa -f markdown | OK | NONE |
| 217 | 1 | webclaw | webclaw https://raw.githubusercontent.com/github/awesome-copilot/main/skills/github-issues/references/sub-issues.md -f markdown | OK | NONE |
| 218 | 1 | webclaw | webclaw https://raw.githubusercontent.com/github/awesome-copilot/main/skills/github-issues/references/dependencies.md -f markdown | OK | NONE |
| 219 | 1 | webclaw | webclaw https://github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/Claude%20Code/slash-commands/compact.md -f markdown (retry) | ERROR | OTHER |
| 300 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/hooks.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 301 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/hooks-guide.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 302 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/context-window.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 303 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/costs.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 304 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/commands.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 305 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/interactive-mode.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 306 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/common-workflows.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 307 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/memory.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 308 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/sub-agents.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 309 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/agent-teams.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 310 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/checkpointing.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 311 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/cli-reference.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 312 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/changelog.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 313 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/plugins/mods/events.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 314 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/plugins/mods/api.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 315 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/plugins/mods/overview.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 316 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/plugins/mods/reference.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 317 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/agent-sdk/sessions.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 318 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/agent-sdk/todo-tracking.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 319 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/tools-reference.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 320 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/env-vars.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 321 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/goal.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 322 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/model-config.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 323 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/settings-reference.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |
| 324 | 1 | webclaw | curl -sL https://code.claude.com/docs/en/sessions.md (raw markdown companion to the webclaw mirror, for line citations) | OK | NONE |

## 3. Results from each (hits, top results, used)

| seq | provider | rc | http | hits | top results | used |
|---|---|---|---|---|---|---|
| 11 | exa | 0 | 200 | 9 | [Auto-compact loses instructions from the last user request](https://github.com/anthropics/claude-code/issues/22376); [[BUG] Session compaction loses user's most recent instructions, causin](https://github.com/anthropics/claude-code/issues/23776); [[Bug] Auto-compact context summarization loses critical instructions a](https://github.com/anthropics/claude-code/issues/10232) | yes |
| 12 | exa | 0 | 200 | 10 | [Audit Log Hook \| Claude Code Playbook](https://ao92265.github.io/claude-code-playbook/docs/audit-log-hook/); [[Feature Request] Support for user-prompt-submit hook to log prompts ·](https://github.com/anthropics/claude-code/issues/10098); [UserPromptSubmit Hooks , Claude Code · Engineering Playbook](https://engineering-playbook.vercel.app/claude-code/userpromptsubmit-hooks) | yes |
| 13 | exa | 0 | 200 | 10 | [Hooks · Claude Code in action · Claude Academy](https://academy.claude.com/courses/claude-code-in-action/hooks); [Hooks reference - Claude Code Docs](https://code.claude.com/docs/en/hooks); [](https://code.claude.com/docs/en/hooks.md) | yes |
| 14 | exa | 0 | 200 | 10 | [](https://code.claude.com/docs/en/hooks.md); [Feature Request: Hook event for actual task completion (not every resp](https://github.com/anthropics/claude-code/issues/43507); [](https://raw.githubusercontent.com/a-ariff/ariff-claude-plugins/main/plugins/hooks-reference/skills/hooks-reference/SKILL.md) | yes |
| 15 | exa | 0 | 200 | 10 | [Harness design for long-running application development \ Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps); [Effective harnesses for long-running agents \ Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents?s=09); [anthropics/cwc-long-running-agents](https://github.com/anthropics/cwc-long-running-agents) | yes |
| 16 | exa | 0 | 200 | 9 | [Anthropic: Long-Running Agent Harness for Multi-Context ...](https://www.zenml.io/llmops-database/long-running-agent-harness-for-multi-context-software-development); [Agent Harness: Initializer and Coding Agent](https://agentpatterns.ai/patterns/agent-design/agent-harness/); [Long-running Agents - by Addy Osmani - Elevate](https://addyo.substack.com/p/long-running-agents) | yes |
| 17 | exa | 0 | 200 | 10 | [rdmolony/sync-claude-code-with-github-issues](https://github.com/rdmolony/sync-claude-code-with-github-issues); [GitHub - dev-anchorpoint-w1/claude-session-tracker: Auto-save every Cl](https://github.com/dev-anchorpoint-w1/claude-session-tracker); [kburson/claude-gh-task-manager](https://github.com/kburson/claude-gh-task-manager) | yes |
| 18 | exa | 0 | 200 | 10 | [Hooks reference - Claude Code Docs](https://code.claude.com/docs/en/hooks); [Hook events across Claude Code mods \| Claude Code Mods](https://claudecodemods.com/hooks/); [Events Reference \| karanb192/claude-code-mods \| DeepWiki](https://deepwiki.com/karanb192/claude-code-mods/2.1-events-reference) | yes |
| 19 | exa | 0 | 200 | 10 | [REST API endpoints for issue dependencies](https://docs.github.com/en/rest/issues/issue-dependencies); [Issues](https://docs.github.com/en/graphql/reference/issues); [REST API endpoints for sub-issues](https://docs.github.com/en/rest/issues/sub-issues) | yes |
| 20 | exa | 0 | 200 | 10 | [GitHub CLI \| Take GitHub to the command line](https://cli.github.com/manual/gh_project_item-edit); [Update GitHub project fields · Actions · GitHub Marketplace · GitHub](https://github.com/marketplace/actions/update-github-project-fields); [sorekz/project-item-fields](https://github.com/sorekz/project-item-fields) | no |
| 21 | exa | 0 | 200 | 10 | [Stop hook not fired when Claude stalls mid-turn after tool result (sil](https://github.com/anthropics/claude-code/issues/29881); [[BUG] Prompt-type Stop hook returns {"ok": false} but stop is not bloc](https://github.com/anthropics/claude-code/issues/32608); [[Bug] Stop hook hangs for 1-2 minutes after response completion, block](https://github.com/anthropics/claude-code/issues/51515) | yes |
| 22 | exa | 0 | 200 | 10 | [feat(compaction): machine-tracked file operation ledger](https://github.com/Stack-Cairn/LiveAgent/pull/86); [Turning Interaction History into Execution State: A Runtime Layer for ](https://arxiv.org/html/2608.00808v1); [docs/COMPACTION.md](https://github.com/dcostenco/prism-coder/blob/HEAD/docs/COMPACTION.md) | yes |
| 23 | exa | 0 | 200 | 10 | [Issues · OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files/issues); [[bug] task_plan.md on cwd is shadowed by .planning/<id>/task_plan.md →](https://github.com/OthmanAdi/planning-with-files/issues/208); [AI vs user creates planning files · Issue #69](https://github.com/OthmanAdi/planning-with-files/issues/69) | no |
| 24 | exa | 0 | 200 | 10 | [](https://code.claude.com/docs/en/commands); [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices); [Anthropic/Claude%20Code/slash-commands/compact.md](https://github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/Claude%20Code/slash-commands/compact.md) | yes |
| 30 | context7 | 1 |  | 0 | none | no |
| 31 | context7 | 1 |  | 0 | none | no |
| 32 | firecrawl | 1 | 402 | 0 | none | no |
| 41 | serper | 0 | 200 | 10 | [[BUG] Context auto-compaction re-enters plan mode ...](https://github.com/anthropics/claude-code/issues/29956); [Auto-compact loses instructions from the last user request](https://github.com/anthropics/claude-code/issues/22376); [Auto-Compaction Regression , Context Loss Causing ...](https://github.com/anthropics/claude-code/issues/36068) | yes |
| 42 | serper | 0 | 200 | 10 | [Superdesign Prompt Library (Grade A) - Claude Skill](https://www.skillsdirectory.com/skills/lev-os-superdesign-prompt-library); [mjs-agent-skills/research/skills-evaluation-prd.md at main](https://github.com/mjunaidca/mjs-agent-skills/blob/main/research/skills-evaluation-prd.md); [Skill Usage Tracker: Analytics for Claude Code Skills](https://mcpmarket.com/tools/skills/skill-usage-tracker) | no |
| 43 | serper | 0 | 200 | 10 | [[FEATURE] PostCompact Hook Event and Compaction ...](https://github.com/anthropics/claude-code/issues/14258); [Add PreCompact and PostCompact hooks for custom ...](https://github.com/anthropics/claude-code/issues/17237); [What Claude Code Keeps of Your Skills After Compaction](https://pub.towardsai.net/what-claude-code-keeps-of-your-skills-after-compaction-42d81853ee3c) | no |
| 44 | serper | 0 | 200 | 10 | [Claude Code Can Now Rewrite Itself. These Are the 10 ...](https://medium.com/@anup.karanjkar08/claude-code-can-now-rewrite-itself-these-are-the-10-mods-im-building-first-e8a77f8122c1); [Claude Code Mods: The Complete Guide + 34 Videos (2026)](https://app.stationx.net/articles/claude-code-mods); [claude-code-hooks/README.md at main](https://github.com/karanb192/claude-code-hooks/blob/main/README.md) | no |
| 45 | serper | 0 | 200 | 10 | [[BUG] SessionStart hook with 'compact' matcher](https://github.com/anthropics/claude-code/issues/28305); [Hooks reference - Claude Code Docs](https://code.claude.com/docs/en/hooks); [SessionStart hooks not working for new conversations](https://github.com/anthropics/claude-code/issues/10373) | yes |
| 46 | serpapi | 0 | 200 | 9 | [Hooks reference - Claude Code Docs](https://code.claude.com/docs/en/hooks); [Releases · pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow/releases); [Issue #76727 · anthropics/claude-code](https://github.com/anthropics/claude-code/issues/76727) | no |
| 50 | last30days | 0 |  | 10 | [Model itself, Opus in Claude code harness was performing very poorly y](https://x.com/Devon8zzh/status/2108170455039516972); [Jev Engineering: The Two-Brain Agent](https://x.com/zynexsol/status/2103182484775039307) | no |
| 51 | last30days | 0 |  | 6 | [Feature request: a setting/env to choose the model used for context co](https://github.com/anthropics/claude-code/issues/96316); [Managed hooks inflate Claude Code session context by ~100K tokens per ](https://github.com/stablyai/orca/issues/20845) | no |
| 60 | webclaw | 0 |  | 1 | [hooks](https://code.claude.com/docs/en/hooks.md) | yes |
| 61 | webclaw | 0 |  | 1 | [hooks-guide](https://code.claude.com/docs/en/hooks-guide.md) | yes |
| 62 | webclaw | 0 |  | 1 | [context-window](https://code.claude.com/docs/en/context-window.md) | yes |
| 63 | webclaw | 0 |  | 1 | [costs](https://code.claude.com/docs/en/costs.md) | yes |
| 64 | webclaw | 0 |  | 1 | [commands](https://code.claude.com/docs/en/commands.md) | no |
| 65 | webclaw | 0 |  | 1 | [interactive-mode](https://code.claude.com/docs/en/interactive-mode.md) | yes |
| 66 | webclaw | 0 |  | 1 | [common-workflows](https://code.claude.com/docs/en/common-workflows.md) | no |
| 67 | webclaw | 0 |  | 1 | [memory](https://code.claude.com/docs/en/memory.md) | yes |
| 68 | webclaw | 0 |  | 1 | [sub-agents](https://code.claude.com/docs/en/sub-agents.md) | no |
| 69 | webclaw | 0 |  | 1 | [agent-teams](https://code.claude.com/docs/en/agent-teams.md) | yes |
| 70 | webclaw | 0 |  | 1 | [checkpointing](https://code.claude.com/docs/en/checkpointing.md) | no |
| 71 | webclaw | 0 |  | 1 | [cli-reference](https://code.claude.com/docs/en/cli-reference.md) | no |
| 72 | webclaw | 0 |  | 1 | [headless](https://code.claude.com/docs/en/headless.md) | no |
| 73 | webclaw | 0 |  | 1 | [changelog](https://code.claude.com/docs/en/changelog.md) | no |
| 74 | webclaw | 0 |  | 1 | [cross-session-messaging](https://code.claude.com/docs/en/cross-session-messaging.md) | no |
| 75 | webclaw | 0 |  | 1 | [agent-view](https://code.claude.com/docs/en/agent-view.md) | no |
| 76 | webclaw | 0 |  | 1 | [plugins/mods/events](https://code.claude.com/docs/en/plugins/mods/events.md) | yes |
| 77 | webclaw | 0 |  | 1 | [plugins/mods/api](https://code.claude.com/docs/en/plugins/mods/api.md) | no |
| 78 | webclaw | 0 |  | 1 | [plugins/mods/overview](https://code.claude.com/docs/en/plugins/mods/overview.md) | no |
| 79 | webclaw | 0 |  | 1 | [plugins/mods/reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | yes |
| 80 | webclaw | 0 |  | 1 | [plugins/mods/interface](https://code.claude.com/docs/en/plugins/mods/interface.md) | no |
| 81 | webclaw | 0 |  | 1 | [plugins/mods/troubleshoot](https://code.claude.com/docs/en/plugins/mods/troubleshoot.md) | no |
| 82 | webclaw | 0 |  | 1 | [plugins/mods/create](https://code.claude.com/docs/en/plugins/mods/create.md) | no |
| 83 | webclaw | 0 |  | 1 | [agent-sdk/sessions](https://code.claude.com/docs/en/agent-sdk/sessions.md) | no |
| 84 | webclaw | 0 |  | 1 | [agent-sdk/todo-tracking](https://code.claude.com/docs/en/agent-sdk/todo-tracking.md) | yes |
| 85 | webclaw | 0 |  | 1 | [agent-sdk/hooks](https://code.claude.com/docs/en/agent-sdk/hooks.md) | no |
| 86 | webclaw | 0 |  | 1 | [agent-sdk/subagents](https://code.claude.com/docs/en/agent-sdk/subagents.md) | no |
| 201 | webclaw | 0 |  | 1 | [anthropic-effective-harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | yes |
| 202 | webclaw | 0 |  | 1 | [anthropic-harness-design](https://www.anthropic.com/engineering/harness-design-long-running-apps) | yes |
| 203 | webclaw | 0 |  | 1 | [anthropic-context-engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | yes |
| 204 | webclaw | 0 |  | 1 | [gh-docs-sub-issues](https://docs.github.com/en/rest/issues/sub-issues) | yes |
| 205 | webclaw | 0 |  | 1 | [gh-docs-issue-dependencies](https://docs.github.com/en/rest/issues/issue-dependencies) | yes |
| 206 | webclaw | 0 |  | 1 | [gh-changelog-dependencies](https://github.blog/changelog/2025-08-21-dependencies-on-issues/) | yes |
| 207 | webclaw | 0 |  | 1 | [gh-cli-project-item-edit](https://cli.github.com/manual/gh_project_item-edit) | no |
| 208 | webclaw | 0 |  | 1 | [gh-docs-issue-forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms) | no |
| 209 | webclaw | 1 |  | 0 | [compact-prompt-leak](https://raw.githubusercontent.com/asgeirtj/system_prompts_leaks/main/Anthropic/Claude%20Code/slash-commands/compact.md) | no |
| 210 | webclaw | 0 |  | 1 | [claudecodemods-hooks](https://claudecodemods.com/hooks/) | yes |
| 211 | webclaw | 0 |  | 1 | [modscode-auto-handoff](https://modscode.com/claude-mods/mods/earlyaidopters-auto-handoff/) | yes |
| 212 | webclaw | 0 |  | 1 | [modscode-smart-compact](https://modscode.com/claude-mods/mods/hellosverre-smart-compact/) | yes |
| 213 | webclaw | 0 |  | 1 | [modscode-compact-adviser](https://modscode.com/claude-mods/mods/kunchenguid-compact-adviser/) | yes |
| 214 | webclaw | 0 |  | 1 | [negi-compaction-ledgers](https://negiadventures.github.io/blog/transcript-compaction-ledgers-ai-coding-agents.html) | yes |
| 215 | webclaw | 0 |  | 1 | [arxiv-2608.00808](https://arxiv.org/html/2608.00808v1) | yes |
| 216 | webclaw | 0 |  | 1 | [yurukusa-autocompact-paradox](https://gist.github.com/yurukusa/219bf5556f5508b0add25d0be47534fa) | yes |
| 217 | webclaw | 0 |  | 1 | [awesome-copilot-sub-issues](https://raw.githubusercontent.com/github/awesome-copilot/main/skills/github-issues/references/sub-issues.md) | yes |
| 218 | webclaw | 0 |  | 1 | [awesome-copilot-dependencies](https://raw.githubusercontent.com/github/awesome-copilot/main/skills/github-issues/references/dependencies.md) | yes |
| 219 | webclaw | 1 |  | 0 | none | no |
| 300 | webclaw | 0 | 200 | 1 | [hooks](https://code.claude.com/docs/en/hooks.md) | yes |
| 301 | webclaw | 0 | 200 | 1 | [hooks-guide](https://code.claude.com/docs/en/hooks-guide.md) | yes |
| 302 | webclaw | 0 | 200 | 1 | [context-window](https://code.claude.com/docs/en/context-window.md) | yes |
| 303 | webclaw | 0 | 200 | 1 | [costs](https://code.claude.com/docs/en/costs.md) | yes |
| 304 | webclaw | 0 | 200 | 1 | [commands](https://code.claude.com/docs/en/commands.md) | no |
| 305 | webclaw | 0 | 200 | 1 | [interactive-mode](https://code.claude.com/docs/en/interactive-mode.md) | yes |
| 306 | webclaw | 0 | 200 | 1 | [common-workflows](https://code.claude.com/docs/en/common-workflows.md) | no |
| 307 | webclaw | 0 | 200 | 1 | [memory](https://code.claude.com/docs/en/memory.md) | yes |
| 308 | webclaw | 0 | 200 | 1 | [sub-agents](https://code.claude.com/docs/en/sub-agents.md) | no |
| 309 | webclaw | 0 | 200 | 1 | [agent-teams](https://code.claude.com/docs/en/agent-teams.md) | yes |
| 310 | webclaw | 0 | 200 | 1 | [checkpointing](https://code.claude.com/docs/en/checkpointing.md) | no |
| 311 | webclaw | 0 | 200 | 1 | [cli-reference](https://code.claude.com/docs/en/cli-reference.md) | no |
| 312 | webclaw | 0 | 200 | 1 | [changelog](https://code.claude.com/docs/en/changelog.md) | no |
| 313 | webclaw | 0 | 200 | 1 | [plugins/mods/events](https://code.claude.com/docs/en/plugins/mods/events.md) | yes |
| 314 | webclaw | 0 | 200 | 1 | [plugins/mods/api](https://code.claude.com/docs/en/plugins/mods/api.md) | no |
| 315 | webclaw | 0 | 200 | 1 | [plugins/mods/overview](https://code.claude.com/docs/en/plugins/mods/overview.md) | no |
| 316 | webclaw | 0 | 200 | 1 | [plugins/mods/reference](https://code.claude.com/docs/en/plugins/mods/reference.md) | yes |
| 317 | webclaw | 0 | 200 | 1 | [agent-sdk/sessions](https://code.claude.com/docs/en/agent-sdk/sessions.md) | no |
| 318 | webclaw | 0 | 200 | 1 | [agent-sdk/todo-tracking](https://code.claude.com/docs/en/agent-sdk/todo-tracking.md) | yes |
| 319 | webclaw | 0 | 200 | 1 | [tools-reference](https://code.claude.com/docs/en/tools-reference.md) | yes |
| 320 | webclaw | 0 | 200 | 1 | [env-vars](https://code.claude.com/docs/en/env-vars.md) | yes |
| 321 | webclaw | 0 | 200 | 1 | [goal](https://code.claude.com/docs/en/goal.md) | yes |
| 322 | webclaw | 0 | 200 | 1 | [model-config](https://code.claude.com/docs/en/model-config.md) | no |
| 323 | webclaw | 0 | 200 | 1 | [settings-reference](https://code.claude.com/docs/en/settings-reference.md) | no |
| 324 | webclaw | 0 | 200 | 1 | [sessions](https://code.claude.com/docs/en/sessions.md) | no |

## 4. GitHub issues, PRs and discussions searched (stage 2), each with the stage-1 row that seeded it

Repository checks before searching (D142, D147): `anthropics/claude-code` has issues and PRs, discussions disabled (row 464 is SKIPPED with FEATURE_DISABLED); `OthmanAdi/planning-with-files` has issues, PRs and discussions; neither is archived.

| seq | provider | query or reference | seeded_by | hits | status | top results | used |
|---|---|---|---|---|---|---|---|
| 101 | gh-issue-view | gh issue view 22376 -R anthropics/claude-code --comments | 11 | 1 | OK | [Auto-compact loses instructions from the last user request](https://github.com/anthropics/claude-code/issues/22376) | yes |
| 102 | gh-issue-view | gh issue view 23776 -R anthropics/claude-code --comments | 11 | 1 | OK | [[BUG] Session compaction loses user's most recent instructions, causin](https://github.com/anthropics/claude-code/issues/23776) | yes |
| 103 | gh-issue-view | gh issue view 10232 -R anthropics/claude-code --comments | 11 | 1 | OK | [[Bug] Auto-compact context summarization loses critical instructions a](https://github.com/anthropics/claude-code/issues/10232) | no |
| 104 | gh-issue-view | gh issue view 29890 -R anthropics/claude-code --comments | 11 | 1 | OK | [[BUG] Context compaction loses critical working knowledge mid-session](https://github.com/anthropics/claude-code/issues/29890) | no |
| 105 | gh-issue-view | gh issue view 4017 -R anthropics/claude-code --comments | 11 | 1 | OK | [[BUG] /compact causes Claude Code to ignore CLAUDE.md](https://github.com/anthropics/claude-code/issues/4017) | no |
| 106 | gh-issue-view | gh issue view 13112 -R anthropics/claude-code --comments | 11 | 1 | OK | [[Bug] Auto-Compact causes context loss and degraded performance](https://github.com/anthropics/claude-code/issues/13112) | no |
| 107 | gh-issue-view | gh issue view 92949 -R anthropics/claude-code --comments | 11 | 1 | OK | [[BUG] Auto-compaction re-injects the CLAUDE.md/MEMORY.md copy from the](https://github.com/anthropics/claude-code/issues/92949) | yes |
| 108 | gh-issue-view | gh issue view 17237 -R anthropics/claude-code --comments | 13 | 1 | OK | [Feature Request: Add PreCompact and PostCompact hooks for custom conte](https://github.com/anthropics/claude-code/issues/17237) | no |
| 109 | gh-issue-view | gh issue view 15174 -R anthropics/claude-code --comments | 13 | 1 | OK | [[BUG]  SessionStart hook with "compact" matcher output not injected in](https://github.com/anthropics/claude-code/issues/15174) | no |
| 110 | gh-issue-view | gh issue view 28305 -R anthropics/claude-code --comments | 13 | 1 | OK | [[BUG] SessionStart hook with 'compact' matcher: executes successfully ](https://github.com/anthropics/claude-code/issues/28305) | yes |
| 111 | gh-issue-view | gh issue view 43733 -R anthropics/claude-code --comments | 13 | 1 | OK | [PreCompact hook: allow Claude to take actions before context compactio](https://github.com/anthropics/claude-code/issues/43733) | no |
| 112 | gh-issue-view | gh issue view 14258 -R anthropics/claude-code --comments | 13 | 1 | OK | [[FEATURE] PostCompact Hook Event and Compaction Content Control](https://github.com/anthropics/claude-code/issues/14258) | no |
| 113 | gh-issue-view | gh issue view 43946 -R anthropics/claude-code --comments | 13 | 1 | OK | [Feature request: PreCompact hook event](https://github.com/anthropics/claude-code/issues/43946) | no |
| 114 | gh-issue-view | gh issue view 43507 -R anthropics/claude-code --comments | 14 | 1 | OK | [Feature Request: Hook event for actual task completion (not every resp](https://github.com/anthropics/claude-code/issues/43507) | no |
| 115 | gh-issue-view | gh issue view 55754 -R anthropics/claude-code --comments | 14 | 1 | OK | [[BUG] Stop hook returning {"ok": false} causes infinite loop until ses](https://github.com/anthropics/claude-code/issues/55754) | no |
| 116 | gh-issue-view | gh issue view 8615 -R anthropics/claude-code --comments | 14 | 1 | OK | [[BUG] StopHook with decision:block doesn't actually block](https://github.com/anthropics/claude-code/issues/8615) | no |
| 117 | gh-issue-view | gh issue view 29881 -R anthropics/claude-code --comments | 21 | 1 | OK | [Stop hook not fired when Claude stalls mid-turn after tool result (sil](https://github.com/anthropics/claude-code/issues/29881) | no |
| 118 | gh-issue-view | gh issue view 32608 -R anthropics/claude-code --comments | 21 | 1 | OK | [[BUG] Prompt-type Stop hook returns {"ok": false} but stop is not bloc](https://github.com/anthropics/claude-code/issues/32608) | yes |
| 119 | gh-issue-view | gh issue view 15250 -R anthropics/claude-code --comments | 21 | 1 | OK | [[BUG] Stop hook fires after every response, not just at task completio](https://github.com/anthropics/claude-code/issues/15250) | no |
| 120 | gh-issue-view | gh issue view 43906 -R anthropics/claude-code --comments | 21 | 1 | OK | [[BUG] Stop hook feedback with no output   creates an infinite loop](https://github.com/anthropics/claude-code/issues/43906) | no |
| 121 | gh-issue-view | gh issue view 78121 -R anthropics/claude-code --comments | 21 | 1 | OK | [Stop hook re-fires despite stop_hook_active: true, causing /goal loop ](https://github.com/anthropics/claude-code/issues/78121) | yes |
| 122 | gh-issue-view | gh issue view 73674 -R anthropics/claude-code --comments | 21 | 1 | OK | [/goal completion Stop hook re-matches phrases from earlier in the tran](https://github.com/anthropics/claude-code/issues/73674) | no |
| 123 | gh-issue-view | gh issue view 29956 -R anthropics/claude-code --comments | 41 | 1 | OK | [[BUG] Context auto-compaction re-enters plan mode without user request](https://github.com/anthropics/claude-code/issues/29956) | no |
| 124 | gh-issue-view | gh issue view 36068 -R anthropics/claude-code --comments | 41 | 1 | OK | [URGENT: Auto-Compaction Regression , Context Loss Causing Cascading Ha](https://github.com/anthropics/claude-code/issues/36068) | no |
| 125 | gh-issue-view | gh issue view 47145 -R anthropics/claude-code --comments | 41 | 1 | OK | [Autocompact silently destroys active session work without user consent](https://github.com/anthropics/claude-code/issues/47145) | yes |
| 126 | gh-issue-view | gh issue view 98895 -R anthropics/claude-code --comments | 41 | 1 | OK | [[BUG] Auto-compaction still drops the entire Available skills listing ](https://github.com/anthropics/claude-code/issues/98895) | no |
| 127 | gh-issue-view | gh issue view 24264 -R anthropics/claude-code --comments | 41 | 1 | OK | [Feature Request: User-configurable compaction priorities (recency weig](https://github.com/anthropics/claude-code/issues/24264) | no |
| 128 | gh-issue-view | gh issue view 15405 -R anthropics/claude-code --comments | 41 | 1 | OK | [[FEATURE] Pre-compaction checkpoint dialog](https://github.com/anthropics/claude-code/issues/15405) | no |
| 129 | gh-issue-view | gh issue view 100481 -R anthropics/claude-code --comments | 18 | 1 | OK | [[FEATURE] Mods: pass images and hidden context rows to session.compact](https://github.com/anthropics/claude-code/issues/100481) | yes |
| 130 | gh-issue-view | gh issue view 10098 -R anthropics/claude-code --comments | 12 | 1 | OK | [[Feature Request] Support for user-prompt-submit hook to log prompts](https://github.com/anthropics/claude-code/issues/10098) | no |
| 131 | gh-issue-view | gh issue view 14160 -R anthropics/claude-code --comments | 24 | 1 | OK | [[FEATURE] Allow custom instructions for auto-compact via settings or C](https://github.com/anthropics/claude-code/issues/14160) | yes |
| 132 | gh-issue-view | gh issue view 76727 -R anthropics/claude-code --comments | 46 | 1 | OK | [Cross-session coordination for independently-launched Claude Code sess](https://github.com/anthropics/claude-code/issues/76727) | no |
| 133 | gh-issue-view | gh issue view 14176 -R anthropics/claude-code --comments | 11 | 1 | OK | [[BUG] instant auto compact summary isn't updated to reflect most recen](https://github.com/anthropics/claude-code/issues/14176) | yes |
| 134 | gh-issue-view | gh issue view 14941 -R anthropics/claude-code --comments | 11 | 1 | OK | [Post-compaction behavior aggressively resumes implementation without a](https://github.com/anthropics/claude-code/issues/14941) | yes |
| 135 | gh-issue-view | gh issue view 12151 -R anthropics/claude-code --comments | 13 | 1 | OK | [[BUG] Plugin hook output not captured or passed to agent (UserPromptSu](https://github.com/anthropics/claude-code/issues/12151) | yes |
| 136 | gh-issue-view | gh issue view 16538 -R anthropics/claude-code --comments | 13 | 1 | OK | [Plugin SessionStart hooks don't surface hookSpecificOutput.additionalC](https://github.com/anthropics/claude-code/issues/16538) | no |
| 137 | gh-issue-view | gh issue view 24794 -R anthropics/claude-code --comments | 13 | 1 | OK | [Async hook stdout parser fails on multi-line JSON, silently drops addi](https://github.com/anthropics/claude-code/issues/24794) | no |
| 138 | gh-issue-view | gh issue view 13678 -R anthropics/claude-code --comments | 11 | 1 | OK | [[Bug] Session compaction loses context priority and critical blockers](https://github.com/anthropics/claude-code/issues/13678) | no |
| 139 | gh-issue-view | gh issue view 21078 -R anthropics/claude-code --comments | 11 | 1 | OK | [[BUG] Context loss during conversation compression - 2026-01-26](https://github.com/anthropics/claude-code/issues/21078) | no |
| 401 | gh-issue-search | gh search issues 'PreCompact stdout custom instructions' --repo anthropics/claude-code --limit 30 | 13 | 0 | EMPTY_UNVERIFIED | none | no |
| 402 | gh-issue-search | gh search issues 'PreCompact systemMessage discarded' --repo anthropics/claude-code --limit 30 | 13 | 0 | EMPTY_UNVERIFIED | none | no |
| 403 | gh-issue-search | gh search issues 'PostCompact compact_summary' --repo anthropics/claude-code --limit 30 | 13 | 1 | OK | [#98747 closed 2026-10-01 [BUG] 2.1.286 idle compaction silently discar](https://github.com/anthropics/claude-code/issues/98747) | no |
| 404 | gh-issue-search | gh search issues 'SessionStart compact additionalContext' --repo anthropics/claude-code --limit 30 | 45 | 0 | EMPTY_UNVERIFIED | none | no |
| 405 | gh-issue-search | gh search issues 'UserPromptSubmit background subagent fires' --repo anthropics/claude-code --limit 30 | 12 | 0 | EMPTY_UNVERIFIED | none | no |
| 406 | gh-issue-search | gh search issues 'UserPromptSubmit prompt_id' --repo anthropics/claude-code --limit 30 | 12 | 0 | EMPTY_UNVERIFIED | none | no |
| 407 | gh-issue-search | gh search issues '"Compact Instructions" CLAUDE.md' --repo anthropics/claude-code --limit 30 | 24 | 1 | OK | [#58340 closed 2026-05-12 Feature request: agent-invoked /compact with ](https://github.com/anthropics/claude-code/issues/58340) | no |
| 408 | gh-issue-search | gh search issues 'compaction "Pending Tasks" dropped' --repo anthropics/claude-code --limit 30 | 11 | 0 | EMPTY_UNVERIFIED | none | no |
| 409 | gh-issue-search | gh search issues 'compaction forgot request in:title' --repo anthropics/claude-code --limit 30 | 11 | 0 | EMPTY_UNVERIFIED | none | no |
| 410 | gh-issue-search | gh search issues 'session.compact mod' --repo anthropics/claude-code --limit 30 | 18 | 3 | OK | [#102134 open 2026-10-14 [BUG] session.compact mod hook no longer raise](https://github.com/anthropics/claude-code/issues/102134); [#100481 open 2026-10-08 [FEATURE] Mods: pass images and hidden context](https://github.com/anthropics/claude-code/issues/100481) | yes |
| 411 | gh-issue-search | gh search issues 'prompt.submit mod' --repo anthropics/claude-code --limit 30 | 18 | 0 | EMPTY_UNVERIFIED | none | no |
| 412 | gh-issue-search | gh search issues 'CLAUDE_CODE_STOP_HOOK_BLOCK_CAP' --repo anthropics/claude-code --limit 30 | 21 | 12 | OK | [#97851 open 2026-09-28 [Bug] Stop hook repeatedly triggers with "full ](https://github.com/anthropics/claude-code/issues/97851); [#90558 open 2026-08-29 [FEATURE]: Allow the built-in /goal Stop hook u](https://github.com/anthropics/claude-code/issues/90558) | yes |
| 413 | gh-issue-search | gh search issues 'PreCompact in:title' --repo anthropics/claude-code --limit 30 | 13 | 30 | OK | [#101057 open 2026-10-10 [BUG] PreCompact hook output is added to the c](https://github.com/anthropics/claude-code/issues/101057); [#91910 open 2026-09-03 Hooks: PreCompact/PostCompact/SessionStart(comp](https://github.com/anthropics/claude-code/issues/91910) | yes |
| 414 | gh-issue-search | gh search issues 'PostCompact in:title' --repo anthropics/claude-code --limit 30 | 13 | 24 | OK | [#89622 open 2026-08-25 PostCompact hook stdin can be invalid JSON (une](https://github.com/anthropics/claude-code/issues/89622); [#77832 open 2026-07-15 PostCompact hook silent-miss and forced compact](https://github.com/anthropics/claude-code/issues/77832) | yes |
| 415 | gh-issue-search | gh search issues '"compact" SessionStart in:title' --repo anthropics/claude-code --limit 30 | 45 | 8 | OK | [#93458 open 2026-09-10 SessionStart hook additionalContext silently dr](https://github.com/anthropics/claude-code/issues/93458); [#91910 open 2026-09-03 Hooks: PreCompact/PostCompact/SessionStart(comp](https://github.com/anthropics/claude-code/issues/91910) | yes |
| 416 | gh-issue-search | gh search issues 'UserPromptSubmit in:title is:open' --repo anthropics/claude-code --limit 30 | 12 | 30 | OK | [#100666 open 2026-10-09 Hooks: document whether a UserPromptSubmit pro](https://github.com/anthropics/claude-code/issues/100666); [#95763 open 2026-09-21 [FEATURE] Let a UserPromptSubmit hook replace t](https://github.com/anthropics/claude-code/issues/95763) | yes |
| 417 | gh-issue-search | gh search issues 'SubagentStop in:title is:open' --repo anthropics/claude-code --limit 30 | 21 | 30 | OK | [#78463 open 2026-07-17 SubagentStart/SubagentStop counts stay mismatch](https://github.com/anthropics/claude-code/issues/78463); [#92716 open 2026-09-07 SubagentStop does not fire when a background su](https://github.com/anthropics/claude-code/issues/92716) | yes |
| 418 | gh-issue-search | gh search issues '"lost" request compaction is:open' --repo anthropics/claude-code --limit 30 | 11 | 30 | OK | [#96422 open 2026-09-23 Custom instructions are lost across context com](https://github.com/anthropics/claude-code/issues/96422); [#100481 open 2026-10-08 [FEATURE] Mods: pass images and hidden context](https://github.com/anthropics/claude-code/issues/100481) | yes |
| 419 | gh-issue-search | gh search issues 'github issue' --repo OthmanAdi/planning-with-files --limit 30 | 23 | 0 | EMPTY_UNVERIFIED | none | no |
| 420 | gh-issue-search | gh search issues 'compaction' --repo OthmanAdi/planning-with-files --limit 30 | 23 | 7 | OK | [#240 closed 2026-09-08 [regression] named gated plans can cross-bind s](https://github.com/OthmanAdi/planning-with-files/issues/240); [#298 closed 2026-09-29 opencode-planning-with-files plugins need suppo](https://github.com/OthmanAdi/planning-with-files/issues/298) | yes |
| 421 | gh-issue-search | gh search issues 'ledger' --repo OthmanAdi/planning-with-files --limit 30 | 23 | 6 | OK | [#231 closed 2026-08-28 npm package ships 6 shell scripts with CRLF lin](https://github.com/OthmanAdi/planning-with-files/issues/231); [#237 closed 2026-09-02 PLAN_ID is a hint, not a binding: a valid-shape](https://github.com/OthmanAdi/planning-with-files/issues/237) | no |
| 422 | gh-issue-search | gh search issues 'requests user prompt' --repo OthmanAdi/planning-with-files --limit 30 | 23 | 0 | EMPTY_UNVERIFIED | none | no |
| 423 | gh-pr-search | gh search prs 'PreCompact' --repo OthmanAdi/planning-with-files --limit 30 | 23 | 4 | OK | [#311 closed 2026-10-09 fix(hooks): use shell-form command so lifecycle](https://github.com/OthmanAdi/planning-with-files/pull/311); [#181 closed 2026-06-09 fix: add Codex PreCompact hook](https://github.com/OthmanAdi/planning-with-files/pull/181) | yes |
| 424 | gh-issue-search | gh search issues 'claude code hook GitHub issue per prompt' --limit 30 | 17 | 0 | EMPTY_UNVERIFIED | none | no |
| 425 | gh-issue-search | gh search issues 'fork SessionStart' --repo OthmanAdi/planning-with-files --limit 30 | 60 | 0 | EMPTY_UNVERIFIED | none | yes |
| 426 | gh-pr-search | gh search prs 'fork' --repo OthmanAdi/planning-with-files --limit 30 | 60 | 5 | OK | [#199 merged 2026-07-08 ci: run pytest on ubuntu and windows plus Pi ex](https://github.com/OthmanAdi/planning-with-files/pull/199); [#200 merged 2026-07-08 ci: commit Pi extension lockfile and switch vit](https://github.com/OthmanAdi/planning-with-files/pull/200) | no |
| 431 | gh-issue-view | gh issue view 101057 -R anthropics/claude-code --comments | 13 | 1 | OK | [[BUG] PreCompact hook output is added to the compaction instructions w](https://github.com/anthropics/claude-code/issues/101057) | yes |
| 432 | gh-issue-view | gh issue view 91910 -R anthropics/claude-code --comments | 13 | 1 | OK | [Hooks: PreCompact/PostCompact/SessionStart(compact) fire for a subagen](https://github.com/anthropics/claude-code/issues/91910) | yes |
| 433 | gh-issue-view | gh issue view 50467 -R anthropics/claude-code --comments | 13 | 1 | OK | [PreCompact hook never fires on auto-compaction (v2.1.105-v2.1.114, ref](https://github.com/anthropics/claude-code/issues/50467) | yes |
| 434 | gh-issue-view | gh issue view 78760 -R anthropics/claude-code --comments | 13 | 1 | OK | [[BUG] Interactive mode: manual /compact fires PreCompact but never Pos](https://github.com/anthropics/claude-code/issues/78760) | yes |
| 435 | gh-issue-view | gh issue view 89622 -R anthropics/claude-code --comments | 13 | 1 | OK | [PostCompact hook stdin can be invalid JSON (unescaped \. in compact_su](https://github.com/anthropics/claude-code/issues/89622) | yes |
| 436 | gh-issue-view | gh issue view 71625 -R anthropics/claude-code --comments | 13 | 1 | OK | [PreCompact hook: add blocking mode for interactive turn before compact](https://github.com/anthropics/claude-code/issues/71625) | no |
| 437 | gh-issue-view | gh issue view 93458 -R anthropics/claude-code --comments | 45 | 1 | OK | [SessionStart hook additionalContext silently dropped when source=fork ](https://github.com/anthropics/claude-code/issues/93458) | yes |
| 438 | gh-issue-view | gh issue view 95745 -R anthropics/claude-code --comments | 45 | 1 | OK | [CLAUDE.md is present in context after /compact but no longer followed ](https://github.com/anthropics/claude-code/issues/95745) | yes |
| 439 | gh-issue-view | gh issue view 100666 -R anthropics/claude-code --comments | 12 | 1 | OK | [Hooks: document whether a UserPromptSubmit prompt was typed by the hum](https://github.com/anthropics/claude-code/issues/100666) | yes |
| 440 | gh-issue-view | gh issue view 90296 -R anthropics/claude-code --comments | 12 | 1 | OK | [UserPromptSubmit hooks: two silent failure modes , mid-turn submission](https://github.com/anthropics/claude-code/issues/90296) | yes |
| 441 | gh-issue-view | gh issue view 90784 -R anthropics/claude-code --comments | 12 | 1 | OK | [UserPromptSubmit hooks permanently stop firing for a session, correlat](https://github.com/anthropics/claude-code/issues/90784) | no |
| 442 | gh-issue-view | gh issue view 96422 -R anthropics/claude-code --comments | 11 | 1 | OK | [Custom instructions are lost across context compaction with no signal ](https://github.com/anthropics/claude-code/issues/96422) | yes |
| 443 | gh-issue-view | gh issue view 89831 -R anthropics/claude-code --comments | 11 | 1 | OK | [[FEATURE] Pre-compaction notice + visible record of what compaction dr](https://github.com/anthropics/claude-code/issues/89831) | yes |
| 444 | gh-issue-view | gh issue view 102134 -R anthropics/claude-code --comments | 18 | 1 | OK | [[BUG] session.compact mod hook no longer raised in 2.1.299 (manual and](https://github.com/anthropics/claude-code/issues/102134) | yes |
| 445 | gh-issue-view | gh issue view 95328 -R anthropics/claude-code --comments | 18 | 1 | OK | [A session.compact function hook's compaction is undone when the sessio](https://github.com/anthropics/claude-code/issues/95328) | yes |
| 446 | gh-issue-view | gh issue view 101096 -R anthropics/claude-code --comments | 18 | 1 | OK | [[BUG] session.compact hook: a hook-built assistant message with N tool](https://github.com/anthropics/claude-code/issues/101096) | no |
| 447 | gh-issue-view | gh issue view 94358 -R anthropics/claude-code --comments | 21 | 1 | OK | [Hook `additionalContext` is silently truncated at 10,000 characters, d](https://github.com/anthropics/claude-code/issues/94358) | yes |
| 448 | gh-issue-view | gh issue view 92716 -R anthropics/claude-code --comments | 21 | 1 | OK | [SubagentStop does not fire when a background subagent is killed via Ta](https://github.com/anthropics/claude-code/issues/92716) | yes |
| 449 | gh-issue-view | gh issue view 86569 -R anthropics/claude-code --comments | 21 | 1 | OK | [SubagentStop decision:block is silently discarded when the agent has a](https://github.com/anthropics/claude-code/issues/86569) | yes |
| 450 | gh-issue-view | gh issue view 85547 -R anthropics/claude-code --comments | 21 | 1 | OK | [Stop-hook block cap: document it, signal the override to hooks, and bl](https://github.com/anthropics/claude-code/issues/85547) | yes |
| 451 | gh-issue-view | gh issue view 96831 -R anthropics/claude-code --comments | 18 | 1 | OK | [[Bug] Function hooks `classic.PreToolUse` and `skill.prompt` not dispa](https://github.com/anthropics/claude-code/issues/96831) | yes |
| 452 | gh-issue-view | gh issue view 100869 -R anthropics/claude-code --comments | 18 | 1 | OK | [Plugin hooks module: classic.* events (classic.Stop, classic.PreToolUs](https://github.com/anthropics/claude-code/issues/100869) | yes |
| 453 | gh-issue-view | gh issue view 99130 -R anthropics/claude-code --comments | 18 | 1 | OK | [Mods off remotely on 2.1.288 despite docs saying on by default since 2](https://github.com/anthropics/claude-code/issues/99130) | yes |
| 454 | gh-issue-view | gh issue view 32608 -R anthropics/claude-code --comments | 21 | 1 | OK | [[BUG] Prompt-type Stop hook returns {"ok": false} but stop is not bloc](https://github.com/anthropics/claude-code/issues/32608) | yes |
| 461 | gh-graphql-discussion | graphql search type:DISCUSSION 'repo:OthmanAdi/planning-with-files compaction' | 23 | 0 | EMPTY_UNVERIFIED | none | no |
| 462 | gh-graphql-discussion | graphql search type:DISCUSSION 'repo:OthmanAdi/planning-with-files github issues' | 23 | 2 | OK | [#35 🎉 v2.3.0 Released: Codex & OpenCode IDE Support](https://github.com/OthmanAdi/planning-with-files/discussions/35); [#36 🧪 Test the New Session Management Features (Anthropic Patterns)](https://github.com/OthmanAdi/planning-with-files/discussions/36) | no |
| 463 | gh-graphql-discussion | graphql search type:DISCUSSION 'repo:OthmanAdi/planning-with-files' | 23 | 14 | OK | [#307 A completion gate with independent verification for planning-with](https://github.com/OthmanAdi/planning-with-files/discussions/307); [#305 A completion gate with independent verification for planning-with](https://github.com/OthmanAdi/planning-with-files/discussions/305) | yes |
| 464 | gh-graphql-discussion | graphql search type:DISCUSSION 'repo:anthropics/claude-code compaction' (not sent: has_discussions=false) | 11 | 0 | SKIPPED/FEATURE_DISABLED | none | no |
| 465 | gh-graphql-discussion | graphql repository(OthmanAdi/planning-with-files).discussion(number:301) with comments | 23 | 1 | OK | [#301 The next session should know what is still unfinished: three ways](https://github.com/OthmanAdi/planning-with-files/discussions/301) | yes |
| 466 | gh-graphql-discussion | graphql repository(OthmanAdi/planning-with-files).discussion(number:307) with comments | 23 | 1 | OK | [#307 A completion gate with independent verification for planning-with](https://github.com/OthmanAdi/planning-with-files/discussions/307) | no |
| 481 | git-clone | git clone --filter=blob:none https://github.com/thepushkarp/handoff.git repos/thepushkarp_handoff | 473 | 1 | OK | [thepushkarp/handoff@a5893a3cdacf](https://github.com/thepushkarp/handoff/tree/a5893a3cdacf04b6d76154adb0a76e4a66a59819) | yes |
| 482 | git-clone | git clone --filter=blob:none https://github.com/u-ichi/compact-plus.git repos/u-ichi_compact-plus | 473 | 1 | OK | [u-ichi/compact-plus@acb5b80a2dae](https://github.com/u-ichi/compact-plus/tree/acb5b80a2daecc28d701929c934832393ca1f710) | no |
| 483 | git-clone | git clone --filter=blob:none https://github.com/kenimo49/compact-ops.git repos/kenimo49_compact-ops | 473 | 1 | OK | [kenimo49/compact-ops@2b15d6c0fad6](https://github.com/kenimo49/compact-ops/tree/2b15d6c0fad6eda96871aa8d6e19258f7be88241) | no |
| 484 | git-clone | git clone --filter=blob:none https://github.com/yasyf/cc-notes.git repos/yasyf_cc-notes | 476 | 1 | OK | [yasyf/cc-notes@3d6c10d4ab5f](https://github.com/yasyf/cc-notes/tree/3d6c10d4ab5f6ce5f26f5b19eef7f443e1bbed09) | yes |
| 485 | git-clone | git clone --filter=blob:none https://github.com/Bucurenciu-Cristian/claude-user-input-logger.git repos/Bucurenciu-Cristian_claude-user-input-logger | 12 | 1 | OK | [Bucurenciu-Cristian/claude-user-input-logger@2d73cf8ceaa6](https://github.com/Bucurenciu-Cristian/claude-user-input-logger/tree/2d73cf8ceaa621c1ef1df8f5c52ff2a0d92c2a62) | yes |
| 486 | git-clone | git clone --filter=blob:none https://github.com/rdmolony/sync-claude-code-with-github-issues.git repos/rdmolony_sync-claude-code-with-github-issues | 17 | 1 | OK | [rdmolony/sync-claude-code-with-github-issues@75b5f6d6480b](https://github.com/rdmolony/sync-claude-code-with-github-issues/tree/75b5f6d6480b8437aa035cce619b878fea77a4f8) | yes |
| 487 | git-clone | git clone --filter=blob:none https://github.com/automazeio/ccpm.git repos/automazeio_ccpm | 17 | 1 | OK | [automazeio/ccpm@7d7e4623bc6d](https://github.com/automazeio/ccpm/tree/7d7e4623bc6d4c0c9ba66ca6bfecd7e5261dc697) | yes |
| 488 | git-clone | git clone --filter=blob:none https://github.com/kburson/claude-gh-task-manager.git repos/kburson_claude-gh-task-manager | 17 | 1 | OK | [kburson/claude-gh-task-manager@ec0d07614f3e](https://github.com/kburson/claude-gh-task-manager/tree/ec0d07614f3e2c7f89296a4d869c1f280cd040d6) | yes |

## 5. Githubkit saved searches run (reproduced read-only with their controls) and proposed new rows

`./dev/mise run research:collect` writes into a tracked path another lane owns, so each `dev/saved-searches.toml` row was reproduced read-only with `gh api -X GET search/code`, using the collector's effective query (the row's `query` plus ` repo:<repo>`, `dev/collect_saved_search.py:44-80`), page 1, beside its control. Rows 471 to 476 are free code searches for prior art (stage 2, seeded); rows 521 to 528 test the proposed rows in section 10 with their controls.

| seq | kind | effective query | rc | total_count | status | top results |
|---|---|---|---|---|---|---|
| 471 | prior-art search | `"UserPromptSubmit" "prompts.jsonl"` | 0 | 105 | OK | [mjunaidca/mjs-agent-skills/specs/001-skill-tracker/plan.md](https://github.com/mjunaidca/mjs-agent-skills/blob/b829650de901e376050692c672d587fb0b6f673f/specs/001-skill-tracker/plan.md); [mjunaidca/mjs-agent-skills/docs/skill-tracker.md](https://github.com/mjunaidca/mjs-agent-skills/blob/b829650de901e376050692c672d587fb0b6f673f/docs/skill-tracker.md) |
| 472 | prior-art search | `"PostCompact" "compact_summary" filename:settings.json` | 0 | 1 | OK | [Vaultifacts/claude-behavioral-controller/settings.json](https://github.com/Vaultifacts/claude-behavioral-controller/blob/4472f06fc6f34be7bd9ed6deed2c7bb767d06cac/settings.json) |
| 473 | prior-art search | `"PreCompact" "custom instructions" language:Shell` | 0 | 26 | OK | [tsieb/dndtools/tools/loop/hooks/precompact.sh](https://github.com/tsieb/dndtools/blob/effe44cb4495c4ec334eb88add2c01ffbd89ef62/tools/loop/hooks/precompact.sh); [alinaqi/maggy/templates/pre-compact.sh](https://github.com/alinaqi/maggy/blob/55aabe2493627e1de9cd09459d555181d66f3111/templates/pre-compact.sh) |
| 474 | prior-art search | `"UserPromptSubmit" "gh issue create"` | 0 | 918 | OK | [garrytan/gstack/TODOS.md](https://github.com/garrytan/gstack/blob/47d639abffa882b8cbb641d7d1dedf08ecada9ec/TODOS.md); [danielmiessler/LifeOS/LifeOS/install/hooks/README.md](https://github.com/danielmiessler/LifeOS/blob/5e2f2e8c0abde612da0e99c16c0d07d4ec21b88c/LifeOS/install/hooks/README.md) |
| 475 | prior-art search | `"SessionStart" "compact" "open requests"` | 0 | 116 | OK | [spotta85/anyagent/src/adapter/opencode.rs](https://github.com/spotta85/anyagent/blob/c98fea7e2ca2c84335655f10d699063e2c0b8a6f/src/adapter/opencode.rs); [garrytan/gbrain/src/core/behavior-change-notice.ts](https://github.com/garrytan/gbrain/blob/f06a2ce080d151eb88a2496e47cda63800358e83/src/core/behavior-change-notice.ts) |
| 476 | prior-art search | `"AskUserQuestion" "PostToolUse" "answers" language:Python` | 0 | 101 | OK | [yasyf/cc-notes/plugin/capt-hook/hooks/answers.py](https://github.com/yasyf/cc-notes/blob/3d6c10d4ab5f6ce5f26f5b19eef7f443e1bbed09/plugin/capt-hook/hooks/answers.py); [yasyf/cc-transcript/cc_transcript/_native.pyi](https://github.com/yasyf/cc-transcript/blob/dbe4d04ed088a7e75fb95645b2476c3dd9fd4f32/cc_transcript/_native.pyi) |
| 501 | existing row | `schema repo:openai/codex` | 0 | 878 | OK | [openai/codex/codex-rs/config/src/tui_mouse_scroll.rs](https://github.com/openai/codex/blob/0fd85b075288c4fee50f0df3e4e4f98f80c693fe/codex-rs/config/src/tui_mouse_scroll.rs); [openai/codex/codex-rs/core/src/config/schema.md](https://github.com/openai/codex/blob/0fd85b075288c4fee50f0df3e4e4f98f80c693fe/codex-rs/core/src/config/schema.md) |
| 502 | control | `README repo:openai/codex` | 0 | 167 | OK | [openai/codex/sdk/python/README.md](https://github.com/openai/codex/blob/0fd85b075288c4fee50f0df3e4e4f98f80c693fe/sdk/python/README.md); [openai/codex/scripts/readme_toc.py](https://github.com/openai/codex/blob/0fd85b075288c4fee50f0df3e4e4f98f80c693fe/scripts/readme_toc.py) |
| 503 | existing row | `model filename:config.toml repo:openai/codex` | 0 | 1 | OK | [openai/codex/.github/codex/home/config.toml](https://github.com/openai/codex/blob/0fd85b075288c4fee50f0df3e4e4f98f80c693fe/.github/codex/home/config.toml) |
| 504 | existing row | `SessionStart filename:hooks.json repo:openai/codex` | 0 | 0 | EMPTY_UNVERIFIED | none |
| 505 | existing row | `xhigh path:plugins/claude-security/agents repo:anthropics/claude-plugins-official` | 0 | 6 | OK | [anthropics/claude-plugins-official/plugins/claude-security/agents/expl](https://github.com/anthropics/claude-plugins-official/blob/c2bdb427efe8673f190ae862c273cfa368d2390f/plugins/claude-security/agents/explore.md); [anthropics/claude-plugins-official/plugins/claude-security/agents/clau](https://github.com/anthropics/claude-plugins-official/blob/c2bdb427efe8673f190ae862c273cfa368d2390f/plugins/claude-security/agents/claude-security.md) |
| 506 | control | `README repo:anthropics/claude-plugins-official` | 0 | 61 | OK | [anthropics/claude-plugins-official/README.md](https://github.com/anthropics/claude-plugins-official/blob/c2bdb427efe8673f190ae862c273cfa368d2390f/README.md); [anthropics/claude-plugins-official/plugins/ralph-loop/README.md](https://github.com/anthropics/claude-plugins-official/blob/c2bdb427efe8673f190ae862c273cfa368d2390f/plugins/ralph-loop/README.md) |
| 507 | existing row | `"Model Selection" repo:obra/superpowers` | 0 | 13 | OK | [obra/superpowers/skills/subagent-driven-development/re-review-prompt.m](https://github.com/obra/superpowers/blob/bb92a77741419a4ab5f06e711a283343f1ada0c3/skills/subagent-driven-development/re-review-prompt.md); [obra/superpowers/RELEASE-NOTES.md](https://github.com/obra/superpowers/blob/bb92a77741419a4ab5f06e711a283343f1ada0c3/RELEASE-NOTES.md) |
| 508 | control | `README repo:obra/superpowers` | 0 | 30 | OK | [obra/superpowers/README.md](https://github.com/obra/superpowers/blob/bb92a77741419a4ab5f06e711a283343f1ada0c3/README.md); [obra/superpowers/docs/superpowers/specs/2026-05-05-platform-neutral-re](https://github.com/obra/superpowers/blob/bb92a77741419a4ab5f06e711a283343f1ada0c3/docs/superpowers/specs/2026-05-05-platform-neutral-readme-design.md) |
| 509 | existing row | `"model: fable" repo:wshobson/agents` | 0 | 6 | OK | [wshobson/agents/ARCHITECTURE.md](https://github.com/wshobson/agents/blob/46891e7e60da0e52baf1050b7b6391b64e84c6d9/ARCHITECTURE.md); [wshobson/agents/plugins/framework-migration/agents/legacy-modernizer.m](https://github.com/wshobson/agents/blob/46891e7e60da0e52baf1050b7b6391b64e84c6d9/plugins/framework-migration/agents/legacy-modernizer.md) |
| 510 | control | `README repo:wshobson/agents` | 0 | 75 | OK | [wshobson/agents/plugins/plugin-eval/README.md](https://github.com/wshobson/agents/blob/46891e7e60da0e52baf1050b7b6391b64e84c6d9/plugins/plugin-eval/README.md); [wshobson/agents/plugins/brand-landingpage/README.md](https://github.com/wshobson/agents/blob/46891e7e60da0e52baf1050b7b6391b64e84c6d9/plugins/brand-landingpage/README.md) |
| 511 | existing row | `effort repo:VoltAgent/awesome-claude-code-subagents` | 0 | 8 | OK | [VoltAgent/awesome-claude-code-subagents/categories/08-business-product](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/408d3c9eee2d0c75c12a3abb5de29e53c2ca6b9e/categories/08-business-product/assumption-mapping.md); [VoltAgent/awesome-claude-code-subagents/categories/08-business-product](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/408d3c9eee2d0c75c12a3abb5de29e53c2ca6b9e/categories/08-business-product/product-manager.md) |
| 512 | control | `README repo:VoltAgent/awesome-claude-code-subagents` | 0 | 17 | OK | [VoltAgent/awesome-claude-code-subagents/categories/06-developer-experi](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/408d3c9eee2d0c75c12a3abb5de29e53c2ca6b9e/categories/06-developer-experience/README.md); [VoltAgent/awesome-claude-code-subagents/README.md](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/408d3c9eee2d0c75c12a3abb5de29e53c2ca6b9e/README.md) |
| 521 | proposed row | `PreCompact repo:anthropics/claude-code` | 0 | 4 | OK | [anthropics/claude-code/plugins/plugin-dev/README.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/plugins/plugin-dev/README.md); [anthropics/claude-code/plugins/plugin-dev/skills/hook-development/SKIL](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/plugins/plugin-dev/skills/hook-development/SKILL.md) |
| 522 | proposed row | `"session.compact" repo:anthropics/claude-code` | 0 | 5 | OK | [anthropics/claude-code/mods/sec-default/README.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/mods/sec-default/README.md); [anthropics/claude-code/mods/sec-default/hooks/register.ts](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/mods/sec-default/hooks/register.ts) |
| 523 | proposed row | `UserPromptSubmit path:plugins repo:anthropics/claude-code` | 0 | 11 | OK | [anthropics/claude-code/plugins/hookify/hooks/userpromptsubmit.py](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/plugins/hookify/hooks/userpromptsubmit.py); [anthropics/claude-code/plugins/hookify/commands/help.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/plugins/hookify/commands/help.md) |
| 524 | proposed row | `PreCompact repo:OthmanAdi/planning-with-files` | 0 | 108 | OK | [OthmanAdi/planning-with-files/docs/codex.md](https://github.com/OthmanAdi/planning-with-files/blob/ff349ebe322b4f86c3416a6fbcde515f1de32e8b/docs/codex.md); [OthmanAdi/planning-with-files/.codex/hooks/pre-compact.sh](https://github.com/OthmanAdi/planning-with-files/blob/ff349ebe322b4f86c3416a6fbcde515f1de32e8b/.codex/hooks/pre-compact.sh) |
| 525 | proposed row | `"blocked-by" path:pkg/cmd/issue repo:cli/cli` | 0 | 6 | OK | [cli/cli/pkg/cmd/issue/edit/edit.go](https://github.com/cli/cli/blob/ff67d7622da2503223b8437e8cfaa39e1f6bf0e2/pkg/cmd/issue/edit/edit.go); [cli/cli/pkg/cmd/issue/create/create.go](https://github.com/cli/cli/blob/ff67d7622da2503223b8437e8cfaa39e1f6bf0e2/pkg/cmd/issue/create/create.go) |
| 526 | control | `README repo:anthropics/claude-code` | 0 | 42 | OK | [anthropics/claude-code/README.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/README.md); [anthropics/claude-code/examples/settings/README.md](https://github.com/anthropics/claude-code/blob/94506ff0d3bd9185f1752da36e968775021fb48f/examples/settings/README.md) |
| 527 | control | `README repo:OthmanAdi/planning-with-files` | 0 | 21 | OK | [OthmanAdi/planning-with-files/README.md](https://github.com/OthmanAdi/planning-with-files/blob/ff349ebe322b4f86c3416a6fbcde515f1de32e8b/README.md); [OthmanAdi/planning-with-files/examples/README.md](https://github.com/OthmanAdi/planning-with-files/blob/ff349ebe322b4f86c3416a6fbcde515f1de32e8b/examples/README.md) |
| 528 | control | `README repo:cli/cli` | 0 | 87 | OK | [cli/cli/docs/README.md](https://github.com/cli/cli/blob/ff67d7622da2503223b8437e8cfaa39e1f6bf0e2/docs/README.md); [cli/cli/AGENTS.md](https://github.com/cli/cli/blob/ff67d7622da2503223b8437e8cfaa39e1f6bf0e2/AGENTS.md) |

Existing rows: six of seven reproduce with hits and every control passes; `codex-hook-examples` (`SessionStart filename:hooks.json repo:openai/codex`) returned 0 today against a control of 167, so that row now reads as a verified empty result for this query shape rather than a route failure.

## 6. Stage-2 GitHub and saved searches run against the stage-1 results (seed-to-search map)

| stage-1 seed (seq, provider, query) | stage-2 rows it seeded |
|---|---|
| 11 exa: Claude Code compaction loses user requests instructions forgotten after auto-compact | 101 (22376 -R anthropics/claude-code), 102 (23776 -R anthropics/claude-code), 103 (10232 -R anthropics/claude-code), 104 (29890 -R anthropics/claude-code), 105 (4017 -R anthropics/claude-code), 106 (13112 -R anthropics/claude-code), 107 (92949 -R anthropics/claude-code), 133 (14176 -R anthropics/claude-code), 134 (14941 -R anthropics/claude-code), 138 (13678 -R anthropics/claude-code), 139 (21078 -R anthropics/claude-code), 408 (search 'compaction "Pending Tasks" dropped' --repo anthropics/claude-c), 409 (search 'compaction forgot request in:title' --repo anthropics/claude-c), 418 (search '"lost" request compaction is:open' --repo anthropics/claude-co), 442 (96422 -R anthropics/claude-code), 443 (89831 -R anthropics/claude-code), 464 (disc 'repo:anthropics/claude-code compaction' (not sent: has_discussio) |
| 12 exa: Claude Code UserPromptSubmit hook log every prompt to a file ledger | 130 (10098 -R anthropics/claude-code), 405 (search 'UserPromptSubmit background subagent fires' --repo anthropics/), 406 (search 'UserPromptSubmit prompt_id' --repo anthropics/claude-code), 416 (search 'UserPromptSubmit in:title is:open' --repo anthropics/claude-co), 439 (100666 -R anthropics/claude-code), 440 (90296 -R anthropics/claude-code), 441 (90784 -R anthropics/claude-code), 471 (gh api -X GET search/code -f q='"UserPromptSubmit" "prompts.jsonl"' -F), 476 (gh api -X GET search/code -f q='"AskUserQuestion" "PostToolUse" "answe), 485 (clone Bucurenciu-Cristian/claude-user-input-logger.git repos/Bucurenci), 523 (gh api -X GET search/code -f q='UserPromptSubmit path:plugins repo:ant) |
| 13 exa: Claude Code PreCompact PostCompact hook SessionStart compact matcher re-inject context | 108 (17237 -R anthropics/claude-code), 109 (15174 -R anthropics/claude-code), 110 (28305 -R anthropics/claude-code), 111 (43733 -R anthropics/claude-code), 112 (14258 -R anthropics/claude-code), 113 (43946 -R anthropics/claude-code), 135 (12151 -R anthropics/claude-code), 136 (16538 -R anthropics/claude-code), 137 (24794 -R anthropics/claude-code), 401 (search 'PreCompact stdout custom instructions' --repo anthropics/claud), 402 (search 'PreCompact systemMessage discarded' --repo anthropics/claude-c), 403 (search 'PostCompact compact_summary' --repo anthropics/claude-code), 413 (search 'PreCompact in:title' --repo anthropics/claude-code), 414 (search 'PostCompact in:title' --repo anthropics/claude-code), 431 (101057 -R anthropics/claude-code), 432 (91910 -R anthropics/claude-code), 433 (50467 -R anthropics/claude-code), 434 (78760 -R anthropics/claude-code), 435 (89622 -R anthropics/claude-code), 436 (71625 -R anthropics/claude-code), 472 (gh api -X GET search/code -f q='"PostCompact" "compact_summary" filena), 473 (gh api -X GET search/code -f q='"PreCompact" "custom instructions" lan), 521 (gh api -X GET search/code -f q='PreCompact repo:anthropics/claude-code) |
| 14 exa: Claude Code Stop hook block until all user requests are tracked or done | 114 (43507 -R anthropics/claude-code), 115 (55754 -R anthropics/claude-code), 116 (8615 -R anthropics/claude-code) |
| 17 exa: track coding agent tasks as GitHub issues automatically from conversation | 424 (search 'claude code hook GitHub issue per prompt'), 474 (gh api -X GET search/code -f q='"UserPromptSubmit" "gh issue create"' ), 486 (clone rdmolony/sync-claude-code-with-github-issues.git repos/rdmolony_), 487 (clone automazeio/ccpm.git repos/automazeio_ccpm), 488 (clone kburson/claude-gh-task-manager.git repos/kburson_claude-gh-task-) |
| 18 exa: Claude Code mods prompt.submit session.compact hook | 129 (100481 -R anthropics/claude-code), 410 (search 'session.compact mod' --repo anthropics/claude-code), 411 (search 'prompt.submit mod' --repo anthropics/claude-code), 444 (102134 -R anthropics/claude-code), 445 (95328 -R anthropics/claude-code), 446 (101096 -R anthropics/claude-code), 451 (96831 -R anthropics/claude-code), 452 (100869 -R anthropics/claude-code), 453 (99130 -R anthropics/claude-code), 522 (gh api -X GET search/code -f q='"session.compact" repo:anthropics/clau) |
| 19 exa: GitHub sub-issues REST API and issue dependencies blocked by API GraphQL addBlockedBy | 525 (gh api -X GET search/code -f q='"blocked-by" path:pkg/cmd/issue repo:c) |
| 21 exa: Claude Code hook that refuses to stop while a request has no GitHub issue | 117 (29881 -R anthropics/claude-code), 118 (32608 -R anthropics/claude-code), 119 (15250 -R anthropics/claude-code), 120 (43906 -R anthropics/claude-code), 121 (78121 -R anthropics/claude-code), 122 (73674 -R anthropics/claude-code), 412 (search 'CLAUDE_CODE_STOP_HOOK_BLOCK_CAP' --repo anthropics/claude-code), 417 (search 'SubagentStop in:title is:open' --repo anthropics/claude-code), 447 (94358 -R anthropics/claude-code), 448 (92716 -R anthropics/claude-code), 449 (86569 -R anthropics/claude-code), 450 (85547 -R anthropics/claude-code), 454 (32608 -R anthropics/claude-code) |
| 22 exa: coding agent request ledger every user prompt tracked to completion across context compact | 475 (gh api -X GET search/code -f q='"SessionStart" "compact" "open request) |
| 23 exa: planning-with-files task_plan GitHub issue link | 419 (search 'github issue' --repo OthmanAdi/planning-with-files), 420 (search 'compaction' --repo OthmanAdi/planning-with-files), 421 (search 'ledger' --repo OthmanAdi/planning-with-files), 422 (search 'requests user prompt' --repo OthmanAdi/planning-with-files), 423 (prs 'PreCompact' --repo OthmanAdi/planning-with-files), 461 (disc 'repo:OthmanAdi/planning-with-files compaction'), 462 (disc 'repo:OthmanAdi/planning-with-files github issues'), 463 (disc 'repo:OthmanAdi/planning-with-files'), 465 (graphql repository(OthmanAdi/planning-with-files).discussion(number:30), 466 (graphql repository(OthmanAdi/planning-with-files).discussion(number:30), 524 (gh api -X GET search/code -f q='PreCompact repo:OthmanAdi/planning-wit) |
| 24 exa: Claude Code compact instructions CLAUDE.md "Compact Instructions" preserve user requests | 131 (14160 -R anthropics/claude-code), 407 (search '"Compact Instructions" CLAUDE.md' --repo anthropics/claude-cod) |
| 41 serper: site:github.com anthropics/claude-code issues compaction drops user request | 123 (29956 -R anthropics/claude-code), 124 (36068 -R anthropics/claude-code), 125 (47145 -R anthropics/claude-code), 126 (98895 -R anthropics/claude-code), 127 (24264 -R anthropics/claude-code), 128 (15405 -R anthropics/claude-code) |
| 45 serper: "SessionStart" "compact" hook additionalContext not injected claude code issue | 404 (search 'SessionStart compact additionalContext' --repo anthropics/clau), 415 (search '"compact" SessionStart in:title' --repo anthropics/claude-code), 437 (93458 -R anthropics/claude-code), 438 (95745 -R anthropics/claude-code) |
| 46 serpapi: claude code hook "decision" "block" Stop untracked user request github issue ledger | 132 (76727 -R anthropics/claude-code) |
| 60 webclaw: webclaw https://code.claude.com/docs/en/hooks.md -f markdown | 425 (search 'fork SessionStart' --repo OthmanAdi/planning-with-files), 426 (prs 'fork' --repo OthmanAdi/planning-with-files) |
| 473 gh-code-search-saved: gh api -X GET search/code -f q='"PreCompact" "custom instructions" language:Shell' -F per_ | 481 (clone thepushkarp/handoff.git repos/thepushkarp_handoff), 482 (clone u-ichi/compact-plus.git repos/u-ichi_compact-plus), 483 (clone kenimo49/compact-ops.git repos/kenimo49_compact-ops) |
| 476 gh-code-search-saved: gh api -X GET search/code -f q='"AskUserQuestion" "PostToolUse" "answers" language:Python' | 484 (clone yasyf/cc-notes.git repos/yasyf_cc-notes) |

## 7. Findings with citations

### 7.1 What each candidate surface can do on 2.1.300

Hook events and payloads (Claude Code docs mirrored 2026-10-14, `D/hooks.md` unless noted):

- `UserPromptSubmit` (`:1441-1500`): input has `prompt` (pasted text expanded in place) and the common
  fields `session_id`, `prompt_id`, `transcript_path`, `cwd` (`:728-745`). It also fires for a
  scheduled task or `/loop` iteration, a background subagent reporting back, and a message from another
  session (`:1447-1451`), and nothing in the input marks the human's own words
  ([#100666](https://github.com/anthropics/claude-code/issues/100666), open, 2026-10-09). Default
  timeout 30 s; a timed-out synchronous hook's context is discarded (`:1453-1455`). An `async: true`
  command hook does not block the turn and its result, if any, arrives on the next turn
  (`:4017-4060`). Since 2.1.299 it runs before a skill or slash command expands
  (`D/changelog.md:156`). Plain stdout and `additionalContext` are both added to context
  (`:806-812`, `:1478-1486`).
- `PostToolUse` receives `tool_input` and the tool's structured output in `tool_response`
  (`:2153-2156`, `:2346`). For `AskUserQuestion`, `tool_input.questions` and `answers` are documented
  (`:1906-1914`); the transcript's `toolUseResult` for the same calls holds `questions`, `answers` and
  `annotations` (35 calls in `T`; two carry free-text `notes`, two record "(no option selected)").
  That `tool_response` equals `toolUseResult` is an inference from the docs wording; the probe in
  section 11 confirms it.
- `SessionStart` (`:1201-1290`): sources `startup`, `resume` (`--resume`, `--continue`, `/resume`),
  `clear`, `compact`, `fork`. `additionalContext` or plain stdout is added before the first prompt.
  Resume and fork inputs carry `context_tokens` and `prompt_cache_likely_expired` (`:1244-1246`).
  Fork injection was reported dropped on rewind forks
  ([#93458](https://github.com/anthropics/claude-code/issues/93458), open, 2026-09-10).
- `PreCompact` (`:3242-3272`): matchers `manual` and `auto` (auto includes idle compaction, added in
  2.1.299, `D/changelog.md:119-120`). Input has `trigger` and `custom_instructions`, which is `null` for
  auto. Exit 2 or `decision: "block"` blocks; a blocked proactive auto-compaction is skipped, a blocked
  reactive one fails the request (`:3253-3255`). `systemMessage` and `continue` are discarded
  (`:3257`). Exit-0 stdout becomes custom compaction instructions per the binary help text
  (`offline/research/CL3/binary/hook-help-2.1.300.txt:2`) and #101057, with no size cap.
- `PostCompact` (`:3274-3296`): input has `compact_summary`; no decision control; the binary help
  text says exit-0 stdout is shown to the user (`hook-help-2.1.300.txt:5`), not to the model. Order,
  confirmed by a maintainer on v2.1.233 in interactive and print mode: `PreCompact`, then
  `SessionStart` with source `compact`, then `PostCompact`
  ([#78760](https://github.com/anthropics/claude-code/issues/78760), closed completed 2026-08-16).
  So a `PostCompact` audit cannot feed the same compaction's `SessionStart` injection.
- Compaction hooks also fire for a background subagent's compaction with the parent's payload and no
  agent fields ([#91910](https://github.com/anthropics/claude-code/issues/91910), open, reproduced on
  2.1.281): a `PreCompact` checkpoint or a `SessionStart(compact)` injection runs for subagents too.
- `SubagentStart` (`:2508-2544`): cannot block, but its `additionalContext` is added to the subagent
  before its first prompt, once per subagent, and re-added after the subagent's own auto-compaction.
- `Stop` and `SubagentStop` (`:2546-2579`, `:2693-2795`): inputs carry `stop_hook_active`,
  `last_assistant_message`, `background_tasks` and `session_crons` (SubagentStop adds `agent_id`,
  `agent_type`, `agent_transcript_path`). `decision: "block"` with `reason`, or `additionalContext`
  as softer feedback; cap of 8 consecutive continuations (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`,
  `D/env-vars.md:401`). Stop does not fire on a user interrupt (`:2695-2697`). Known gaps: a
  SubagentStop block is discarded when the agent has a structured output schema
  ([#86569](https://github.com/anthropics/claude-code/issues/86569), closed not planned), SubagentStop
  does not fire for a killed background subagent
  ([#92716](https://github.com/anthropics/claude-code/issues/92716), open). A `prompt`-type Stop hook
  sees only the hook input (no user prompt), so it cannot judge request coverage
  (`D/hooks-guide.md:843-875`); an `agent`-type hook can read files but is experimental
  (`D/hooks-guide.md:877-905`).
- `TaskCreated` and `TaskCompleted` (`:2581-2690`) can refuse a task or a completion, but only in
  sessions that have the Task tools. Those are off by default on every model newer than Opus 4.7,
  Sonnet 4.6 and Haiku 4.5, which includes this session's Opus 5.5; `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`
  turns them on (`D/tools-reference.md:581-595`). With `CLAUDE_CODE_TASK_LIST_ID` the list lives in
  `~/.claude/tasks/<id>/` and survives sessions (`D/interactive-mode.md:691-701`,
  `D/agent-teams.md:252-254`).
- Output caps: `additionalContext`, `systemMessage` and plain stdout are each capped at 10,000
  characters; over the cap Claude gets a file path and a 2,000-character preview and is not told to
  read it (`:1015-1020`, [#94358](https://github.com/anthropics/claude-code/issues/94358), open).
  PreCompact stdout has no cap (#101057), so keep it short.

Compaction itself:
- The 2.1.300 summarizer prompt already asks for "Primary Request and Intent", "All user messages"
  and "Pending Tasks" (`offline/research/CL3/binary/compact-prompt-2.1.300.txt:4-13`). Dropped
  requests are a summarizer judgement failure, not a missing section, which is why naming the open
  ids in the custom instructions (M5) is the lever.
- What survives: project-root CLAUDE.md, unscoped rules, auto memory and the plan-mode plan are
  re-injected; "Context that hooks added earlier" is summarized with the conversation; `SessionStart`
  hooks matching `compact` run and their output is added (`D/context-window.md:1592-1615`). So pwf's
  per-turn injections do not survive on their own; only the post-compaction `SessionStart` re-run
  restores them. CLAUDE.md re-injection on the auto path comes from the last prompt's snapshot, not
  disk ([#92949](https://github.com/anthropics/claude-code/issues/92949), open).
- Process rules in a re-injected CLAUDE.md are followed less after compaction than an imperative
  SessionStart hook in the same context
  ([#95745](https://github.com/anthropics/claude-code/issues/95745), open), which favours the hook
  route for the open list.
- In `T`, all three compactions were automatic, at `preTokens` 668,918, 668,134 and 667,051
  (`compact_boundary` L2445 uuid `6c18da21-c0c1-4f48-a285-8089c2af724f`, L5032 uuid
  `bcd4de37-ae15-4d6b-9931-aaf1e3d6e2f4`, L7352 uuid `aa5250d2-bdc3-4c0b-b696-ef9444f8575b`) with
  `autoCompactWindow` 700,000 in `.claude/settings.json`; each kept a short verbatim tail
  (`preservedMessages`, 4 to 8 uuids). `T` has no PreCompact or PostCompact attachment rows at those
  boundaries; MP configures neither event, and whether pwf's PreCompact ran is not recorded.
- Custom instructions: `/compact <text>` (manual), a `# Compact instructions` section in CLAUDE.md
  (`D/costs.md:241-249`; the binary also carries a "## Compact Instructions" string), and PreCompact
  stdout. No settings key exists; a request for one
  ([#14160](https://github.com/anthropics/claude-code/issues/14160)) was closed as a duplicate on
  2025-12-20.

Upstream history (stage 2, all on `anthropics/claude-code`): the "compaction lost my last request"
reports are many and none is fixed as such; most were bot-closed. #22376 (2026-02-01, closed
duplicate of #14176), #23776 (2026-02-06, closed as duplicate of #14941), #14176 (instant compaction
used a stale summary, closed not planned 2026-02-24), #14941 (post-compaction agent resumes
implementation without checking the conversation, closed not planned 2026-03-09), #47145 (2026-04-13,
closed not planned), #89831 (pre-compaction notice and a record of what was dropped, open),
#96422 (custom instructions lost with no signal, open). Compaction-hook reliability: #28305
(SessionStart compact `additionalContext` not injected, closed not planned 2026-04-22 after a
"resolved" comment), #12151 (plugin hook output not passed to the agent, open since 2025-11-22, a
regression comment at 2.1.97); this session shows plugin SessionStart output injected after every
compaction (`T` L2468, L5054, L7370), so #12151 does not affect pwf here. #50467 (PreCompact never
fired on auto-compaction in 2.1.105 to 2.1.114, closed not planned 2026-06-03) is contradicted for
2.1.292 and later by #101057's bundle reading, but no live check exists for this host. Stop-hook loops
were fixed or documented: #78121 (closed completed 2026-08-17), #85547 (cap documented, closed
2026-09-01), #32608 (prompt Stop hook not blocking, closed completed 2026-04-03).

Mods (`D/plugins_mods_events.md`, `D/plugins_mods_reference.md`):
- Can observe and change: `prompt.submit` (`e.text`; add `context`; `{ drop }`), `prompt.attachment`
  (Claude Code's own reminders), `session.append` (every row before it is stored), `turn.complete`
  (`e.answer`), `agent.spawn` (choose the model or deny; the brief is not listed as rewritable),
  `session.end` (`reason` clear or resume), and `$.session.usage()` for context percent
  (`D/plugins_mods_reference.md:70-152`, `:195-220`). A mod can therefore capture prompts and could
  inject context per prompt, but cannot add context after compaction (no compaction event with a
  context result; `session.start` does not fire after `/clear`, `/resume` or `/branch`).
- `session.compact` can only skip or replace the message list, drops hidden rows
  ([#100481](https://github.com/anthropics/claude-code/issues/100481), open), is undone on resume
  ([#95328](https://github.com/anthropics/claude-code/issues/95328), open) and is not raised at all on
  2.1.299 ([#102134](https://github.com/anthropics/claude-code/issues/102134), open).
- Stop blocking is only through `classic.Stop`, the unreliable bridge above.
- Community compaction mods confirm the event set: auto-handoff uses `prompt.submit`,
  `session.compact`, `turn.complete`; smart-compact uses `classic.PreCompact` and `prompt.submit`;
  compact-adviser uses `session.compact` and `prompt.submit` (`W/modscode-auto-handoff.md`,
  `W/modscode-smart-compact.md`, `W/modscode-compact-adviser.md`).

planning-with-files 3.24.0 (installed for MP 2026-10-13, commit `ff349eb`; `PWF/.claude-plugin/plugin.json`):
- Six lifecycle hooks; SessionStart on `startup|resume|clear|compact` (`PWF/hooks/hooks.json:4-6`).
- Injection modes: legacy `head -50` plan plus `tail -20` progress per prompt, `head -30` per tool
  call; `inject-smart` extracts title, `## Goal`, `## Next Step`, `## Current Phase`, the first
  `in_progress` phase in full and the last three decisions (`PWF/scripts/inject-plan.sh:10-15`,
  `:1005-1066`; `PWF/skills/planning-with-files/SKILL.md:381-397`). MP has no `P/.mode` today.
- Task-plan conventions: `### Phase N` sections with `- [ ]` items and `**Status:** pending |
  in_progress | complete` (`PWF/templates/task_plan.md:23-60`).
- Catch-up: `session-catchup.py --metadata` (aggregate counts) and `--replay` (bounded excerpts) read
  same-project session records on explicit request only
  (`PWF/docs/claude-code-lost-context-after-compaction.md:35-43`).
- Gated mode blocks Stop only when `.mode` contains `gate` and an `in_progress` phase exists, under a
  20-block cap and a stall detector on the run ledger (`PWF/skills/planning-with-files/SKILL.md:409-419`);
  it judges phases, not requests, so it is not a request gate.
- Run ledger: `ledger-<agent>.jsonl` with events `progress`, `phase_complete`, `error`, `gate_block`,
  `attest`, `note` (`PWF/scripts/ledger-append.sh:17-29`); no request event, no GitHub field.
- No GitHub issue linkage anywhere in the plugin; discussion #301 (2026-10-03, "The next session should
  know what is still unfinished", `G/discussions/pwf-301.json`) asks contributors for recovery
  examples, confirming the gap is open upstream.

GitHub linkage:
- REST: `POST /repos/{owner}/{repo}/issues/{issue_number}/sub_issues` (body `sub_issue_id`, the numeric
  id), `GET .../parent`, `POST .../dependencies/blocked_by` (body `issue_id`)
  (`W/gh-docs-sub-issues.md`, `W/gh-docs-issue-dependencies.md`; usage notes in
  `W/awesome-copilot-sub-issues.md`, `W/awesome-copilot-dependencies.md`). Dependencies went GA on
  2025-08-21 with `is:blocked` and `blocked-by:` search qualifiers, 50 links per relationship
  (`W/gh-changelog-dependencies.md:4-21`). Sub-issues: 100 per parent, 8 levels.
- `gh` 2.98.0 on this host: `gh issue create --parent --blocked-by --blocking --type --project
  --recover`, and `gh issue edit --parent --add-blocked-by` (local `--help`).
- MP: direct `gh issue create` is forbidden; `issue:create-preview/apply/verify` with a SHA-bound
  manifest and journal, `issue:new-edge-*` for blockers (`docs/agents/issue-tracker.md:27-56`);
  `dev/issue_create.py` already validates `parent_number` and lists sub-issues
  (`dev/issue_create.py:24-32`, `:76-113`). D63 keeps the pwf plan as the working record that mirrors
  the tracker (P/decisions.jsonl DL-67), and D90 defers filing to the typed stages (DL-118).

Anthropic guidance on long-running harnesses:
- "Effective harnesses for long-running agents" (2025-11-26): an initializer writes a structured
  feature list and `claude-progress.txt`; coding agents may only flip a `passes` field, and JSON was
  chosen because "the model is less likely to inappropriately change or overwrite JSON files compared
  to Markdown files" (`W/anthropic-effective-harnesses.md:42-78`).
- "Harness design for long-running application development" (2026-03-24): a planner, a generator and
  a separate evaluator, communicating through files; context resets with a structured handoff
  instead of relying on compaction, because compaction "doesn't give the agent a clean slate"
  (`W/anthropic-harness-design.md:35-38`, `:101-110`); separating the worker from the judge "proves
  to be a strong lever" (`:44`).
- "Effective context engineering for AI agents" (2025-09-29): compaction risks losing "subtle but
  critical context whose importance only becomes apparent later"; structured note-taking outside the
  window is the complement (`W/anthropic-context-engineering.md:129-147`).
- Mapping for MP: the request ledger is the feature list (machine-written JSON, status-only edits),
  the pwf plan is the handoff artifact, and the C++ Stop gate is the evaluator.

### 7.2 CL2's hypotheses

| H | Verdict | Evidence |
|---|---|---|
| H1 ledger at UserPromptSubmit plus PostToolUse(AskUserQuestion) | Supported; use `async: true` and `/usr/bin/jq -c .` so cost is one process per prompt and no model tokens | payload fields (`D/hooks.md:1459-1474`, `:733-736`); answers and notes in `toolUseResult` (`T` L5663, L6163); non-human prompts also fire (`:1447-1451`, #100666) so classify later; mid-turn queued messages may not fire on another host ([#90296](https://github.com/anthropics/claude-code/issues/90296), ZCode desktop app, open) |
| H2 doctor detector `R.request-unprojected` | Right check, wrong home: a new detector in `dev/doctor` is new Python logic (D113); build it in C++ and keep the doctor as the bridge | DL-143 (D113) |
| H3 SessionStart(compact) injection | Supported and already working for pwf; lands after the summary and the re-read files (`T` L2449 summary, L2454-2460 files, L2468 context) | `D/context-window.md:1592-1615`; 10,000-character cap (`D/hooks.md:1015-1020`); also fires for subagent compactions (#91910) |
| H4 summary audit | Use `PostCompact.compact_summary` rather than reading the transcript, but PostCompact runs after SessionStart(compact) (#78760), so an audit result reaches the model only on the next prompt; the audit is new logic (C++). Interim: archive the summary (M8) | `D/hooks.md:3274-3296`; #89622 invalid JSON in `compact_summary` |
| H5 custom compaction instructions | Supported via PreCompact stdout (binary help text, #101057) and CLAUDE.md `# Compact instructions`; `custom_instructions` input is `null` for auto; no settings key | `D/hooks.md:3259-3262`; `D/costs.md:241-249`; binary excerpts |
| H6 Stop gate | Supported as a C++ gate under D131; Stop input lacks the user prompt, so the gate reads the ledger and the plan; use `additionalContext` first, block once, respect the cap | `D/hooks.md:2705-2795`; R8 on `onFailure` |
| H7 budget as a hook | A hook is the right surface (mods can be switched off, #99130), but hook inputs carry no context count except SessionStart resume and fork (`D/hooks.md:1244-1246`) and the transcript lags (`:735`); reading the usage block is new logic (C++). The status line receives `context_window.used_percentage` (`offline/research/R7-mods-switch-detection/docs/statusline.md:181-183`) | as cited |
| H8 request ids in briefs | Use `SubagentStart.additionalContext` (configuration) instead of rewriting the `Agent` input (`updatedInput` replaces the whole input, `D/hooks.md:1935`); the report-back check is a SubagentStop gate (C++), with #86569 and #92716 as holes | `D/hooks.md:2534-2544` |
| H9 pwf items as the projection | Supported, with a correction: smart mode keeps `## Next Step` and the `in_progress` phase but not a `## Requests` section, so put open requests in one of those | `PWF/scripts/inject-plan.sh:1020-1066` |
| H10 GitHub linkage under typed stages | The ticket-ledger row is the link until `/to-tickets`; a standing intake parent issue with one sub-issue per request is possible with native sub-issues but is a publication needing admission (issue-tracker.md); a Discussion per request has no blocker or parent semantics | GitHub docs above; prior art in section 8 |
| H11 checkpoint at PreCompact | Feasible: PreCompact command hooks run synchronously with the 10-minute default timeout (`D/hooks-guide.md:956-958`); but `dev/handoff.py write` rewrites shared plan files without the parent's `--agents-done` check and would also run on subagent compactions (#91910). Use read-only `dev/handoff.py state --brief` for injection; keep `write` with the parent | `dev/handoff.py:884-904` |

## 8. Code examples found

Prior art (cloned under `R/`, code not run):
- thepushkarp/handoff at `a5893a3cdacf04b6d76154adb0a76e4a66a59819`:
  `plugins/handoff/hooks/hooks.json` wires `PreCompact` (save a handoff),
  `SessionStart` matcher `compact` (inject the latest handoff), `UserPromptSubmit` (marker and fallback
  inject) and `Stop` (enforce summary sections); `scripts/precompact-append-handoff.sh` (197 lines)
  reads `trigger` and `custom_instructions` and appends the transcript's last user and assistant
  messages plus a Git snapshot. The closest end-to-end analogue of layers 1 and 2.
- yasyf/cc-notes at `3d6c10d4ab5f6ce5f26f5b19eef7f443e1bbed09`:
  `plugin/capt-hook/hooks/answers.py:295-304` registers a `PostToolUse` handler on `AskUserQuestion`
  (`record_user_answers`) that stores answers durably and re-injects them on a compaction resume
  (`Event.SessionStart` with `CompactResume()`, `:450-451`).
- Bucurenciu-Cristian/claude-user-input-logger at `2d73cf8ceaa621c1ef1df8f5c52ff2a0d92c2a62`:
  `log-user-inputs.py` logs every user input with session and timestamp.
- kburson/claude-gh-task-manager at `ec0d07614f3e2c7f89296a4d869c1f280cd040d6`: README lines 28, 109,
  156, 462-464 bind each session to a GitHub issue, flush state on `/compact` and session start (not
  `/clear`), and set Projects fields with `gh project item-edit` and sub-issues with `gh api graphql`.
- automazeio/ccpm at `7d7e4623bc6d4c0c9ba66ca6bfecd7e5261dc697`: README lines 266 and 406 create an
  epic issue plus one sub-issue per task through the `gh-sub-issue` extension (now unnecessary with
  `gh --parent`).
- rdmolony/sync-claude-code-with-github-issues at `75b5f6d6480b8437aa035cce619b878fea77a4f8`: a
  `CLAUDE.md` that asks Claude to open one issue per goal and log prompts to it; its own README warns
  it is non-deterministic, which is the failure mode MP hit.
- Found by code search, not cloned: u-ichi/compact-plus `hooks/precompact-state-summary.sh`,
  kenimo49/compact-ops `hooks/precompact-state.sh` (row 473), thiagofinch/mega-brain
  `.claude/hooks/user_prompt_submit.py` (row 471), ElNiak/panther-ivy-plugin
  `.../record/askuserquestion.py` (row 476), and Anthropic's own mod test
  `mods/sec-default/tests/fixtures/compacting.ts` (row 522).

Proposed configuration for MP (not applied; needs the decision in the verdict, the probe in section 11
and a lane; ledger kept untracked under `~/.local/state/claude-code-marketplace/requests/` because
prompts can carry private-project words, D144-D146):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "async": true,
        "command": "/usr/bin/jq -c . >> \"$HOME/.local/state/claude-code-marketplace/requests/ledger.jsonl\"" } ] }
    ],
    "PostToolUse": [
      { "matcher": "AskUserQuestion", "hooks": [ { "type": "command", "async": true,
        "command": "/usr/bin/jq -c . >> \"$HOME/.local/state/claude-code-marketplace/requests/ledger.jsonl\"" } ] }
    ],
    "PreCompact": [
      { "hooks": [ { "type": "command", "timeout": 10,
        "command": "sed -n '/^## Next Step/,/^## Goal/p' \"$CLAUDE_PROJECT_DIR/.planning/$PLAN_ID/task_plan.md\"" } ] }
    ],
    "SubagentStart": [
      { "hooks": [ { "type": "command", "timeout": 10,
        "command": "sed -n '/^## Next Step/,/^## Goal/p' \"$CLAUDE_PROJECT_DIR/.planning/$PLAN_ID/task_plan.md\" | /usr/bin/jq -Rs '{hookSpecificOutput:{hookEventName:\"SubagentStart\",additionalContext:.}}'" } ] }
    ],
    "PostCompact": [
      { "hooks": [ { "type": "command", "async": true,
        "command": "cat >> \"$HOME/.local/state/claude-code-marketplace/requests/compactions.jsonl\"" } ] }
    ]
  }
}
```

Notes: `PLAN_ID` reaches hooks from the `env` key of `.claude/settings.json`; the `## Next Step` block
must stay well under 10,000 characters (today's block is the handoff summary; the open-request list
should be its first lines); if reviewers count a `sed` range as logic, print a dedicated short file with
`cat` instead. The plan entry the parent writes per request:

```markdown
## Next Step
Open requests (ledger key = prompt_id; link = ticket-ledger row or issue):
- R-41 [open] Finish the /claude-agent skill. CT-86 (pending issue). Since 2026-10-14T07:00Z.
- R-42 [open] Track every request as a task_plan item with a GitHub issue. CT-87 (pending issue).
```

The C++ gate (M10) then needs only: ledger rows of this session whose `prompt_id` has no `R-n` line,
and `R-n [open]` lines with no ticket or issue reference; block once with `additionalContext` naming
them, never when `stop_hook_active` is true.

## 9. Routes table

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| preflight | Firecrawl credits | `fnox ... exec -- firecrawl credits --json` | 0 | remainingCredits -128 | skipped, CREDITS_EXHAUSTED |
| preflight | Serper account | `curl -H "X-API-KEY: $SERPER_API_KEY" https://google.serper.dev/account` | 0 | balance 1294 | yes |
| preflight | SerpApi account | `curl https://serpapi.com/account.json?api_key=$SERP_API_KEY` | 0 | 242 left | yes |
| preflight | GitHub rate limit | `gh api rate_limit` | 0 | search 30, code 10 | yes |
| 1 | Exa | `fnox ... exec -- sh exa_q.sh` (POST api.exa.ai/search, `x-api-key` from env) | 0 x 14 | 9 to 10 each | 12 of 14 |
| 1 | Context7 | `fnox ... exec -- ctx7 library ...`, `ctx7 docs /othmanadi/planning-with-files ...` | 1, 1 | 0 | no, monthly quota reached |
| 1 | Firecrawl | `fnox ... exec -- firecrawl search ... --limit 5 --json` | 1 | 0 | no, HTTP 402 |
| 1 | webclaw | `webclaw <url> -f markdown` (27 docs pages, 18 web pages, 1 retry) | 0 x 44, 1 x 2 | 44 files | yes |
| 1 | raw docs | `curl -sL https://code.claude.com/docs/en/<page>.md` (25 pages) | 0 | 25 files | yes (line citations) |
| 1 | Serper | `fnox ... exec -- sh serper_q.sh` (POST google.serper.dev/search) | 0 x 5 | 10 each | 2 of 5 |
| 1 | SerpApi | `curl -G serpapi.com/search.json --data-urlencode q=...` | 0 | 9 | no |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fnox ... exec -- python3 -I last30days.py "<topic>" --plan plan.json --emit json --quick --save-dir ""`, then `--search reddit,hackernews,github` | 0, 0 | 10, 6 off-topic | no (grounding error; planner kept 1 of 3 subqueries) |
| 2 | gh issue view | `gh issue view N -R anthropics/claude-code --comments --json ...` (63 issues) | 0 | 1 each | see section 3 |
| 2 | gh search issues and prs | `gh search issues '<q>' --repo <repo> --limit 30` (26 queries) | 0 | 0 to 30 | yes |
| 2 | GraphQL discussions | `gh api graphql` search type DISCUSSION (3) and two discussion reads; claude-code skipped (discussions off) | 0 | 0, 2, 14 | yes |
| 2 | Code search | `gh api -X GET search/code -f q='<q>'` (6 prior-art, 12 saved-search reproductions, 8 proposed and controls) | 0 | 0 to 918 | yes |
| 2 | git clone | `git clone --filter=blob:none https://github.com/<repo>.git` (8 repos) | 0 | 8 | 6 cited |
| local | Claude binary | `strings -n 20 <2.1.300 binary>` excerpts | 0 | 2 excerpts | yes |
| local | Transcript schema | `python3 -I` line streaming over `T` (compaction boundaries, hook attachments, AskUserQuestion results; no full read) | 0 | as cited | yes |
| local | pwf cache, MP files | `sed`, `grep` over `PWF` and MP | 0 | as cited | yes |

## 10. Proposed saved-search rows

Tested today with controls (rows 521 to 528). The collector only runs `search/code`; issue watches
(#102134, #101057, #91910, #100666, #93458, #12151, #89831) belong on the CT-80 watch list in
`docs/agents/hooks-and-mods.md`.

```toml
# Context-loss watch (research CL3, 2026-10-14)
[[search]]
id = "claude-code-precompact"
query = "PreCompact"
repo = "anthropics/claude-code"            # 4 hits today (plugin-dev hook skills, validate-hook-schema.sh); control README 42
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "claude-code-session-compact-mod"
query = "\"session.compact\""
repo = "anthropics/claude-code"            # 5 hits (mods/sec-default hooks.json and tests); control README 42
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "claude-code-plugin-userpromptsubmit"
query = "UserPromptSubmit path:plugins"
repo = "anthropics/claude-code"            # 11 hits; control README 42
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "pwf-precompact"
query = "PreCompact"
repo = "OthmanAdi/planning-with-files"      # 108 hits; control README 21
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "gh-cli-issue-blocked-by"
query = "\"blocked-by\" path:pkg/cmd/issue"
repo = "cli/cli"                           # 6 hits (create, edit, view tests); control README 87
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 11. Open gaps

- Provider gaps: Context7 monthly quota reached (rows 30, 31) and Firecrawl credits exhausted (rows 1,
  32); webclaw, raw docs and Serper covered the same pages. Last30Days produced no usable community
  signal (rows 50, 51: grounding error, one of three subqueries kept, off-topic hits).
- No live probe was allowed (no `claude` sessions). Unverified on this host and version, all
  settled by one admitted probe in a throwaway repository: (a) PreCompact fires on auto-compaction on
  2.1.300 and its plain stdout reaches `compact_summary` (print a marker such as `KEEP R-TEST-1`, run
  `/compact`, read `PostCompact.compact_summary`); (b) pwf's JSON `systemMessage` from PreCompact is
  dropped; (c) `PostToolUse` for `AskUserQuestion` carries `annotations.notes`; (d) `SubagentStart`
  context reaches the subagent; (e) the order PreCompact, SessionStart(compact), PostCompact on
  2.1.300. Hooks append their stdin to a log, as in #78760's maintainer steps.
- Whether the CLAUDE.md `# Compact instructions` section applies to automatic compaction is not
  documented (UNVERIFIED); the PreCompact route is the one with evidence for the auto path.
- #102134 (`session.compact` not raised) was filed for 2.1.299; nothing in the 2.1.300 notes fixes it,
  but it was not re-tested on 2.1.300.
- No field separates human prompts from subagent reports, peer messages and scheduled tasks in
  `UserPromptSubmit` (#100666); the transcript's undocumented `origin.kind` may help but lags the hook.
  The C++ classifier must handle this, and the false-positive rate for CL2's H2 and H6 is unmeasured.
- Adding settings hooks beyond the three deny gates needs a user decision (D92 versus D102); this
  report does not decide it.
- The proposed PreCompact and SubagentStart commands read `## Next Step` from the main checkout path;
  inside `.claude/worktrees/<unit>` sessions `$CLAUDE_PROJECT_DIR` points at the worktree copy (see
  F4 on `PWF_PLAN_ROOT` pins), so the lane design must pin the path.

