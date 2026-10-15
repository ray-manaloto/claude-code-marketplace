# R12c: agent team roster refresh (claude-agent v2, codex-agent v1)

Research R12c, session ccm-20261014, 2026-10-14 (23:46Z to 00:20Z on 2026-10-15). It refreshes R12
(`R12-sdlc-agent-roles.md`) and R12b (`R12b-sdlc-agent-roles-log.md`) for decision D185 (DL-238):
the claude-agent and codex-agent teams start from R12's roster, and research updates keep it
current. Route: `docs/agents/research-workflow.md` (preflight, both stages, fnox profile, D137 log,
D110 mirror). Read-only apart from this draft, its log and the scratch mirror: no tracked file in MP
changed, nothing was written to GitHub, no `claude` session was started and no key value was printed
or written.

Abbreviations: MP = the repository root; P = `MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`;
S = `/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/r12-refresh/`;
O = `S/offline/`, the mirror (`O/manifest.json`); CC = `O/docs/claude-code/`; CX = `O/docs/codex/`
(learn.chatgpt.com pages); PF = `O/docs/platform/`; A = `O/docs/anthropic/`; PR = `O/docs/pr/`
(practitioner and secondary pages); CL = `O/docs/github/claude-code-CHANGELOG.md`; G = `O/github/`
(threads as `<owner>_<repo>-<n>.json`); L = `O/local/`; RP = `O/repos/`. CC#n is
anthropics/claude-code issue n and CX#n openai/codex issue n. "seq n" is row n of the query log
`S/queries.jsonl` (320 rows). Line numbers refer to the mirrored copies. Hosts: Claude Code 2.1.300
and codex-cli 0.162.1 (L/claude-version.txt, L/codex-version.txt); R12 ran on 2.1.299.

## 1. Verdict

**R12's roles, models and effort levels stand: no model or effort row changes.** What changes is how
the roles are configured and dispatched, plus two added roles, both briefs on existing definitions,
so no new file under `MP/.claude/agents`; the frontmatter edits in §7.3 are batched before a planned
restart (R12 §5.5). The Codex side needs a different form from
the Claude side: Codex custom agents cannot narrow the sandbox, so read-only Codex roles must run as
separate `codex exec -s read-only` processes, and MP's three `.codex/agents` files are not read-only
today.

### 1.1 claude-agent roster v2

| Role | Model | Effort | Tools (delta to the agent file) | Form | Change versus R12 | Citations |
| --- | --- | --- | --- | --- | --- | --- |
| Parent (orchestrator, adjudicator, merger) | session (Opus 5.5) | session (xhigh from user `modelSettings`) | all; project env adds `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (proposed 6) and `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` | main session | **Change**: the in-flight limit becomes mechanical; ultracode and dynamic workflows stay off for lanes | CC/sub-agents.md:1014-1046; CC/env-vars.md:312, 318; G/anthropics_claude-code-101650.json (limit 6, ran 16); PR/canberk-subagent-study.md:37, 79 |
| Architect | Fable 5.1 | high | read-only | read-only brief | Confirm; the brief adds a "refute the plan" pass, which replaces a separate critic | CC/model-config.md:68-77; PR/alphaxiv-humanize-judgement.md:37; PR/cmdctrl-refute-dont-review.md |
| Test author | Opus 5.5 | xhigh | implementer's; `tdd` preload | brief on `implementer` | Confirm | R12 §1; no contrary evidence (§7.2) |
| Test-contract check | Fable 5.1 | medium | reviewer's | brief on `reviewer` | Confirm | R12 §1 |
| Implementer | Opus 5.5 | high | add `Agent` to `disallowedTools`; add `experimental: {cacheTtl: 1h}`; keep `isolation` unset | `implementer` | **Change (config only)** | CC/sub-agents.md:309, 312, 1030; CC#99360 via R12b D2; PR/meetzest-best-model-1232-prs.md:34, 71; G/anthropics_claude-code-92533.json, -97495, -98307, -101887 |
| Reviewer | Fable 5.1 | high | add `Agent` to `disallowedTools`; keep Bash for the differential run | `reviewer`, named, never a fork | Confirm with a flag (open question 1); brief stance becomes refute-first; the served-model gate applies | PR/qodo-which-llm-review.md:49-95; R12 §3.1 (antonshubin); PR/coderabbit-opus55-review.md:76; CC/sub-agents.md:1030 |
| Cross-vendor reviewer | GPT-6.1 Sol (Codex) | high | `codex exec -s read-only -C <lane worktree>` or `codex review --base <base>` | separate process the parent launches; C++ units only, in parallel with the reviewer | **Add** | PR/mertsahin-two-agent-team.md:8; PR/alphaxiv-humanize-judgement.md:37; PR/coderabbit-opus55-review.md:76; G/novotnyllc_railyard-70.json; CX/agent-configuration/subagents.md:161 |
| Security reviewer | Fable 5.1 (receipt records the served model) | xhigh | reviewer's | brief on `reviewer`, in parallel | Confirm; lens extended to every public-text write path (R-174) | PR/endorlabs-opus55-secure.md:22; CC/model-config.md:518-522; G/anthropics_claude-code-91923.json; PR/savage-defense-before-publish.md:11 |
| Retro-writer | Fable 5.1 | high | add `experimental: {cacheTtl: 1h}` | `retro-writer` | Confirm; brief says the record file is the deliverable | G/anthropics_claude-code-101519.json |
| Doc-writer | Sonnet 5.5 | high | unchanged | `doc-writer` | Confirm; same brief rule as the retro-writer | A/claude-haiku-5-5.md:17; CL:347; CC/model-config.md:521 |
| Frontier scheduler | Opus 5.5 | high | unchanged | `frontier-scheduler` | Confirm | R12 §1 |
| Upgrade intake (dependency and release intake) | Sonnet 5.5 | high | read-only (`frontier-scheduler`: no Edit, Write or Agent) | brief on `frontier-scheduler`, after a mechanical collector; returns JSON | **Add** (R-158, R-167, R-176) | PR/devtocash-dependency-triage-agent.md:8; PR/aident-dependency-upgrade-review.md:42 |
| Extractor | Haiku 5.5 | low | optional `omitClaudeMd: true` | `extractor` | Confirm; keep prompts under 100K tokens | A/claude-haiku-5-5.md:11; PR/ovidius-subagents-benchmark.md:3; PR/sddsh-haiku55-subagent.md |

Unit shape is unchanged: test author, implementer, reviewer and retro-writer in sequence, at most 3
writer units in flight (confirm; CC/agent-teams.md:379-381). The cross-vendor reviewer and the
security reviewer run beside the reviewer on C++ units only.

**Rules that apply to every row** (each is a mechanical guard, per D92 a mod where it is not one of
the three deny hooks):
1. Served-model gate (R12b) stays and has more evidence: a cyber refusal moved `model: "opus"`
   subagents to Opus 4.8 for the rest of their run while the parent still reported Opus
   (G/anthropics_claude-code-97687.json); subagents ignore `switchModelsOnFlag: false`
   (G/anthropics_claude-code-98387.json); Fable 5.1 child requests switched to Opus 4.8 after the
   first tool result in 18 of 19 dispatches on 2.1.259 (G/anthropics_claude-code-91923.json); the
   help-centre page says the session stays on the fallback model "for the rest of the conversation"
   (A/support-model-switch.md:73).
2. Pass `model` and `effort` explicitly on every Agent call and keep `effort:` in every file. A
   remote value (`tengu_harmonic_riddle`, env `CLAUDE_CODE_HARMONIC_RIDDLE`) can lower a subagent's
   effort when none is set explicitly, and relative `lower`/`higher` effort is built but gated off
   (PR/coredirective-2.1.290-subagent-effort-remote.md; PR/coredirective-2.1.296-relative-effort.md;
   secondary sources, but all six flag names are present in this host's 2.1.300 binary,
   L/claude-2.1.300-flag-names.txt).
3. Never set `isolation: worktree`: besides the wrong base branch (CC/sub-agents.md:309), four open
   bugs leave isolated subagents (or subagents of an isolated session) unable to run Bash or write,
   one of them triggered by any mod `tool.call` hook with a RegExp or no matcher, which MP's planned
   mods (D92) could register
   (G/anthropics_claude-code-92533.json comment of 2026-10-04; -97495; -98307; -101887: 10 of 10
   spawns dead on 2.1.289, reproduced on 2.1.296). Lanes keep parent-made worktrees and `git -C`.
4. Name record files so they never match `^(REPORT|SUMMARY|FINDINGS|ANALYSIS).*\.md$`, and say in
   the brief that the file is the deliverable: every non-fork subagent is told "Do NOT Write
   report/summary/findings/analysis .md files", and the Write tool refuses those basenames
   (G/anthropics_claude-code-101519.json, citing CC#44657).
5. Keep agent teams off (R12 §5.4 stands: CC#100701 and CC#81852 are still open with no new
   comment, seq 230, 247) and keep the restart rule (CC#75432 and CC#98528 unchanged, seq 228, 237).

### 1.2 codex-agent roster v1

| Role | Codex model | `model_reasoning_effort` | Sandbox and approval | Form | Maps R12 role? | Citations |
| --- | --- | --- | --- | --- | --- | --- |
| Lead (Codex-led sessions only) | `gpt-6.1-sol` | high | parent `workspace-write` + `on-request`, not the user's current `danger-full-access` + `never` | main session | parent | CX/models.md:101-106; CX/agent-configuration/subagents.md:254-265; L/user-codex-config-selected-keys.json |
| Architect | `gpt-6.1-sol`; `gpt-6-astra` only after a demonstrated gap | xhigh | `-s read-only` | `codex exec` process | architect | CX/models.md:161-176; G/novotnyllc_railyard-70.json |
| Test author | `gpt-6.1-sol` | xhigh | `-s workspace-write -C <lane worktree>` | `codex exec` process | test author | G/bity-labs_tstack-81.json (Sol xhigh for ambiguous work) |
| Implementer | `gpt-6.1-sol` | high (medium for bounded units) | `-s workspace-write -C <lane worktree>` | `codex exec` process | implementer | G/novotnyllc_railyard-70.json; PR/meetzest-best-model-1232-prs.md (Codex GPT-6.1 Sol xhigh, $1.04 per task) |
| Reviewer | `gpt-6.1-sol` | high | `-s read-only` | `codex review --base <base>` or `codex exec` | reviewer, and the Claude team's cross-vendor reviewer | CX/agent-configuration/subagents.md:161; G/cdowin_agentic-sdlc-159.json; G/novotnyllc_railyard-70.json |
| Security reviewer | `gpt-6.1-sol` | high | `-s read-only` | `codex exec` process | security reviewer (cyber false positives on Astra, CX#45553) | G/openai_codex-45553.json; CX/cyber-safety.md |
| Test-contract check | `gpt-6.1-sol` | medium | `-s read-only` | `codex exec` process | test-contract check | G/cdowin_agentic-sdlc-159.json |
| Doc-writer | `gpt-6.1-sol` | medium | `-s workspace-write -C <lane worktree>` | `codex exec` process | doc-writer | G/cdowin_agentic-sdlc-159.json (brief-writers Sol medium) |
| Extractor | `gpt-6-luna` | low | inherits the parent | custom agent in `.codex/agents/` | extractor | CX/models.md:176-178; CX/pricing.md:124-139 |
| Retro-writer, frontier scheduler | not mapped in v1 | - | - | Claude roles run them for Codex lanes | no | MP/docs/agents/claude-team.md "Codex compatibility"; parent owns shared planning (MP/AGENTS.md) |

Changes needed on the Codex side before any of this runs:
- **MP's `.codex/agents/*.toml` are not read-only.** All three set `sandbox_mode = "read-only"`
  (L/mp-codex-config-keys.txt), but a custom agent file cannot override `sandbox_mode`,
  `approval_policy`, `model_provider` or `mcp_servers`; subagents inherit the parent turn's sandbox
  and approvals (CX/agent-configuration/subagents.md:254-265, 341-345). The source agrees:
  `AgentRoleOverrides` has no sandbox field and the child copies the parent's approval policy,
  reviewer, cwd and permission profile (RP/openai-codex@4ca84a1
  `codex-rs/core/src/agent/role.rs:37-48`, `child_config.rs:178-201`). CX#45482 measured it from
  rollouts: 2 of 2 read-only agents ran `workspace-write`. The user's Codex default is
  `danger-full-access` with `never` (L/user-codex-config-selected-keys.json), so these "read-only"
  roles run with full access today.
- **Pin a model.** The user default is `gpt-6-astra` at `max`, which subagents inherit when no
  model is set (CX/agent-configuration/subagents.md:130-138). Astra's Plus allowance is 5-45
  messages against 15-160 for GPT-6.1 Sol (CX/pricing.md:124-139). Set
  `agents.default_subagent_model = "gpt-6.1-sol"` and `agents.default_subagent_reasoning_effort`
  in `MP/.codex/config.toml`, or `model` and `model_reasoning_effort` in each agent file, and pass
  `-c` overrides after `exec` (CX#52887 on 0.162.1).
- **No spawn gate and no depth limit in Codex.** `PreToolUse` hooks do not fire for `spawn_agent`
  (CX#49736), `agents.max_depth` is not enforced (CX#46704; CX#32027 traces it to the V2 handler),
  and tool-backed sessions may expose no agent-type selector (CX#33244, CX#32587). Lanes are
  therefore launched as processes by the Claude parent or a mise task, one worktree each, rather
  than spawned by a Codex parent; a role name in a Codex brief is an instruction, not a boundary
  (RP/cdowin-agentic-sdlc@6012c29 `AGENTS-AND-MODELS.md:193-198`).
- **Served-model receipts are weaker on Codex.** The served model is not persisted per turn
  (CX#47779, open) and a silent reroute to `gpt-5.5` was reported while the app showed
  `gpt-6-astra` (CX#44637). Record `turn_context` model and effort from the rollout and mark the
  receipt `requested-only` until CX#47779 lands.

**Confidence.**
- High that Codex custom agents cannot be made read-only by their own file (docs, source and a
  measured report agree), that worktree isolation must stay unused, and that the served-model gate
  is needed on both harnesses.
- Medium on the reviewer model. Two sources put Opus 5.5 level with or ahead of Fable 5.1 as a
  reviewer at well under the price (Qodo; antonshubin in R12), against R12's model-diversity
  argument and the user's Q9/Q10 policy (open question 1).
- Medium to low on the Codex model and effort per role: vendor guidance plus three practitioner
  rosters that disagree in detail (cdowin's issue of 10-08 put review on Sol high; its guide at
  6012c29 of 10-13 caps effort at high and puts focused review on `gpt-6-luna` high and the lead on
  `gpt-6-sol` medium, `AGENTS-AND-MODELS.md:11, 27-28, 187-190`), and no MP measurement. MP's own guide expects Codex
  back after 2026-10-19 (`MP/docs/agents/claude-team.md`, "Codex compatibility").

**Evidence that decides it.**
- Codex: CX/agent-configuration/subagents.md:254-265 and 341-345, RP/openai-codex@4ca84a1
  `child_config.rs:178-201`, G/openai_codex-45482.json.
- Claude dispatch: CC/sub-agents.md:353-358 and 413 (per-call model and effort, and a mod's
  `agent.spawn` model wins), CC/sub-agents.md:1041-1046 and CC/env-vars.md:312 (a mechanical
  concurrency cap exists), and G/anthropics_claude-code-101650.json (a written limit of 6 agents
  was run at 16).
- Model rows: no Anthropic page changed a model, price or effort default since R12 (diffs in §7.2).

### 1.3 Open questions for the user

1. **Reviewer model.** Keep Fable 5.1 high (your Q9/Q10 policy and R12's diversity argument), or
   move the reviewer to Opus 5.5 now that a cross-vendor reviewer supplies the diversity (§7.2)?
2. **Mechanical caps.** Approve `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6` and
   `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` in `MP/.claude/settings.json` `env` (a settings change
   needs its own admission).
3. **Agent-file edits.** Approve the frontmatter deltas in §7.3 (`Agent` denied for reviewer and
   implementer, `experimental.cacheTtl: 1h` for implementer and retro-writer); they land together
   before a planned restart (R12 §5.5).
4. **`autoCompactWindow`.** Leave unset (roles stop at the 500K ceiling and a fresh agent is
   dispatched) or let long roles compact earlier?
5. **Codex.** Approve fixing `MP/.codex/agents` (drop the ineffective `sandbox_mode`, pin `model`
   and `model_reasoning_effort`) and choosing `workspace-write` + `on-request` for Codex-led
   sessions instead of the current full access; and say whether the cross-vendor reviewer should
   wait for Codex's return after 2026-10-19.
6. **Watch rows.** Approve the two code-search rows in §10, and a collector extension for the three
   issue-search rows.

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

Every URL is listed in the log file, section 2. Command shape: `webclaw -t 60 <url> -f markdown > <file>`.

### gh-raw (2 calls)

| seq | Query, URL or reference (exact) | Command shape |
| --- | --- | --- |
| 112 | repos/anthropics/claude-code/contents/CHANGELOG.md | gh api -H 'Accept: application/vnd.github.raw' <path> |
| 113 | repos/openai/codex/contents/codex-rs/core/config.schema.json | gh api -H 'Accept: application/vnd.github.raw' <path> |

## 3. Results from each (stage 1)

| seq | Provider | rc | HTTP | Hits | status / failure_code | Top results | Used |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9 | firecrawl | None | None | None | SKIPPED / CREDITS_EXHAUSTED |  | yes |
| 11 | webclaw | 0 | None | 1 | OK / NONE | https://developers.openai.com/codex/llms.txt | yes |
| 12 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/sub-agents.md | yes |
| 13 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/model-config.md | yes |
| 14 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/agent-teams.md | yes |
| 20 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/env-vars.md | yes |
| 48 | exa | 0 | 200 | 10 | OK / NONE | https://changelogs.core-directive.com/v/2.1.300/e/workflow-agents-prompt-rewrite-hook-and…; https://changelogs.core-directive.com/v/2.1.300/e/modelsettingsautocompactwindow-is-now-r… | yes |
| 52 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/subagents.md | yes |
| 53 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/agents-md.md | yes |
| 54 | exa | 0 | 200 | 10 | OK / NONE | https://skiln.co/blog/claude-code-subagents-config-reference-2026; https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-… | no |
| 55 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/rules.md | yes |
| 58 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/sandboxing.md | yes |
| 60 | exa | 0 | 200 | 10 | OK / NONE | https://meetzest.com/blog/best-model-for-coding; https://www.coderabbit.ai/blog/opus-5-5-model-review | yes |
| 63 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/config-file/config-reference.md | yes |
| 65 | exa | 0 | 200 | 10 | OK / NONE | https://www.ovidius.ai/blog/claude-code-subagents-haiku-vs-sonnet-vs-opus-benchmarked; https://agent.nexus/blog/haiku-5-5-vs-sonnet-5-5 | yes |
| 67 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/models.md | yes |
| 70 | exa | 0 | 200 | 10 | OK / NONE | https://www.historyofvibecoding.com/multi-agent-systems/planner-coder-tester-reviewer-the…; https://www.cloudengineerlab.com/blog/build-a-multi-agent-system-planner-worker-reviewer | yes |
| 71 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/build-skills.md | yes |
| 73 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/hooks.md | yes |
| 74 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/environments/git-worktrees.md | yes |
| 78 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/cyber-safety.md | yes |
| 79 | exa | 0 | 200 | 10 | OK / NONE | https://devtocash.com/blog/2026-10-09-dependency-update-triage-agent-renovate-dependabot-…; https://skills.cat/skills/lightdash/lightdash/renovate-pr | yes |
| 80 | webclaw | 0 | None | 1 | OK / NONE | https://learn.chatgpt.com/docs/pricing.md | yes |
| 85 | exa | 0 | 200 | 10 | OK / NONE | https://github.com/openai/codex/discussions/6109; https://www.codex-docs.com/en/docs/agent-configuration/subagents | yes |
| 90 | exa | 0 | 200 | 10 | OK / NONE | https://github.com/openai/codex-plugin-cc/issues; https://losoft.dev/notes/read-a-coding-agents-model-list-without-logging-in/ | no |
| 92 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND | https://learn.chatgpt.com/guides/build-ai-native-engineering-team.md | yes |
| 93 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND | https://learn.chatgpt.com/guides/best-practices.md | yes |
| 94 | exa | 0 | 200 | 10 | OK / NONE | https://developers.openai.com/blog/codex-as-a-platform; https://aistackcurrent.com/agents/openai-codex/ | no |
| 95 | exa | 0 | 200 | 10 | OK / NONE | https://split-e.net/blog/reflection-angelscript-ai-agents/; https://github.com/wjakob/nanobind/discussions/1314 | yes |
| 96 | exa | 0 | 200 | 10 | OK / NONE | https://claudeissues.com/issue/98307-worktree-isolation-in-a-background-session-blocks-su…; https://changelogs.core-directive.com/docs/c/claude-code-20261002T223702Z | yes |
| 97 | exa | 0 | 200 | 10 | OK / NONE | https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conver…; https://www.anthropic.com/claude-opus-5-5 | yes |
| 98 | exa | 0 | 200 | 10 | OK / NONE | https://claude-me.com/en/practice/claude-code-agent-tool-effort-parameter-per-call-subage…; https://claudeissues.com/issue/98391-feature-per-call-effort-parameter-on-the-agent-tool | yes |
| 99 | exa | 0 | 200 | 10 | OK / NONE | https://writingsbylala.com/guide/how-i-use-my-claude-code-and-codex/; https://loreai.dev/compare/use-subagents-and-custom-agents-in-codex | yes |
| 100 | exa | 0 | 200 | 10 | OK / NONE | https://github.cnmirror.space/anthropics/claude-code-action/pull/1693; https://dev.to/holistis/a-github-comment-can-steal-your-secrets-i-found-22-repositories-w… | yes |
| 101 | exa | 0 | 200 | 10 | OK / NONE | https://aicatchup.com/comparisons/claude-code-subagents-vs-agent-teams-vs-workflows; https://botnet.com/resources/fleet-claude-code-parallel-agents-botnet | no |
| 102 | serper | 0 | 200 | 10 | OK / NONE | https://code.claude.com/docs/en/changelog; https://github.com/anthropics/claude-code/releases | no |
| 103 | serper | 0 | 200 | 10 | OK / NONE | https://github.com/openai/codex/discussions/6109; https://github.com/openai/codex/issues/15250 | yes |
| 104 | serper | 0 | 200 | 10 | OK / NONE | https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md; https://github.com/rphlmr/claude-config | yes |
| 105 | serper | 0 | 200 | 10 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/subagents; https://community.openai.com/t/model-aware-task-delegation-for-subagents/1381671 | yes |
| 106 | serper | 0 | 200 | 10 | OK / NONE | https://www.anthropic.com/claude-opus-5-5; https://www.reddit.com/r/claude/comments/1wy2ojw/switched_claude_code_from_fable_51_to_op… | no |
| 107 | serper | 0 | 200 | 10 | OK / NONE | https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents; https://www.reddit.com/r/ClaudeAI/comments/1mi59yk/we_prepared_a_collection_of_claude_cod… | no |
| 108 | serpapi | 0 | 200 | 8 | OK / NONE | https://learn.chatgpt.com/docs/agent-configuration/subagents; https://github.com/openai/codex/issues/15250 | no |
| 109 | serpapi | 0 | 200 | 9 | OK / NONE | https://code.claude.com/docs/en/sub-agents; https://ed-burton.medium.com/claude-skills-vs-agents-vs-mcp-f2121c3350cb | no |
| 110 | context7 | 1 | 429 | None | ERROR / CREDITS_EXHAUSTED |  | yes |
| 111 | context7 | 1 | 429 | None | ERROR / CREDITS_EXHAUSTED |  | yes |
| 112 | gh-raw | 0 | None | 1 | OK / NONE |  | yes |
| 113 | gh-raw | 0 | None | 1 | OK / NONE |  | no |
| 114 | webclaw | 0 | None | 1 | OK / NONE | https://changelogs.core-directive.com/v/2.1.296/e/relative-subagent-effort-lowerhigher-bu… | yes |
| 115 | webclaw | 0 | None | 1 | OK / NONE | https://changelogs.core-directive.com/v/2.1.290/e/subagent-effort-can-be-lowered-by-remot… | yes |
| 117 | webclaw | 0 | None | 1 | OK / NONE | https://meetzest.com/blog/best-model-for-coding | yes |
| 118 | webclaw | 0 | None | 1 | OK / NONE | https://www.coderabbit.ai/blog/opus-5-5-model-review | yes |
| 119 | webclaw | 0 | None | 1 | OK / NONE | https://www.qodo.ai/blog/which-llm-should-review-your-code/ | yes |
| 120 | webclaw | 0 | None | 1 | OK / NONE | https://www.endorlabs.com/learn/opus-5-5-6x-cheaper-and-2x-faster-than-fable-5-1-but-memo… | yes |
| 122 | webclaw | 0 | None | 1 | OK / NONE | https://www.ovidius.ai/blog/claude-code-subagents-haiku-vs-sonnet-vs-opus-benchmarked | yes |
| 123 | webclaw | 0 | None | 1 | OK / NONE | https://www.anthropic.com/claude-haiku-5-5 | yes |
| 124 | webclaw | 0 | None | 1 | OK / NONE | https://sdd.sh/2026/10/claude-haiku-5-5-subagent-model-pricing-effort-levels/ | yes |
| 125 | webclaw | 0 | None | 1 | OK / NONE | https://docs.cmd-ctrl.ai/blog/refute-dont-review | yes |
| 126 | webclaw | 0 | None | 1 | OK / NONE | https://canberk.me/news/coding-agent-sub-agents-parallel-concurrency-study/ | yes |
| 127 | webclaw | 0 | None | 1 | OK / NONE | https://mertsahin.ai/notes/two-agent-team/ | yes |
| 128 | webclaw | 0 | None | 1 | OK / NONE | https://loreai.dev/compare/use-subagents-and-custom-agents-in-codex | yes |
| 129 | webclaw | 0 | None | 1 | OK / NONE | https://automater.ai/intel/served-model-check-safety-fallbacks/ | yes |
| 130 | webclaw | 0 | None | 1 | OK / NONE | https://support.claude.com/en/articles/16049681-why-claude-switched-models-in-your-conver… | yes |
| 133 | webclaw | 0 | None | 1 | OK / NONE | https://devtocash.com/blog/2026-10-09-dependency-update-triage-agent-renovate-dependabot-… | yes |
| 134 | webclaw | 0 | None | 1 | OK / NONE | https://aident.ai/blog/dependency-upgrade-release-review | yes |
| 137 | webclaw | 0 | None | 1 | OK / NONE | https://www.alphaxiv.org/abs/2610.08900 | yes |
| 138 | webclaw | 0 | None | 1 | OK / NONE | https://savagesolutions.io/blog/defense-depth-before-ai-agent-publishes-open-web | yes |
| 139 | webclaw | 0 | None | 0 | EMPTY_UNVERIFIED / OTHER | https://www.reddit.com/r/claude/comments/1wy2ojw/switched_claude_code_from_fable_51_to_op… | no |
| 141 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND | https://learn.chatgpt.com/docs/changelog.md | yes |
| 146 | last30days | 0 | None | 107 | DEGRADED / CREDITS_EXHAUSTED | https://x.com/tekari0/status/2105999486007074975; https://x.com/mirku21/status/2109388663822123043 | yes |
| 310 | webclaw | 0 | None | 1 | OK / NONE | https://code.claude.com/docs/en/plugins/mods/reference.md | yes |
| 320 | webclaw | 1 | 404 | 0 | ERROR / NOT_FOUND |  | yes |

Webclaw rows that were mirrored but not cited are left out here; the log lists all of them.

## 4. GitHub issues, PRs and discussions searched (stage 2)

| seq | Provider | Query or thread | rc | Hits | status | Seeded by | Top results or state | Used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
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
| 199 | gh-issue-search | custom agent sandbox_mode repo:openai/codex | 0 | 20 | OK | 52 | https://github.com/openai/codex/issues/45482; https://github.com/openai/codex/issues/39714 | yes |
| 200 | gh-issue-search | subagent reasoning effort repo:openai/codex created:>=2026-09-15 | 0 | 20 | OK | 52 | https://github.com/openai/codex/issues/53516; https://github.com/openai/codex/issues/49195 | yes |
| 201 | gh-issue-search | default_subagent_model repo:openai/codex | 0 | 13 | OK | 52 | https://github.com/openai/codex/issues/49195; https://github.com/openai/codex/issues/45790 | no |
| 202 | gh-issue-search | spawn_agent model repo:openai/codex created:>=2026-09-15 | 0 | 20 | OK | 63 | https://github.com/openai/codex/issues/49736; https://github.com/openai/codex/issues/46087 | yes |
| 203 | gh-issue-search | subagent read-only repo:openai/codex | 0 | 20 | OK | 52 | https://github.com/openai/codex/issues/40278; https://github.com/openai/codex/issues/32684 | yes |
| 204 | gh-pr-search | custom agent repo:openai/codex created:>=2026-09-15 | 0 | 6 | OK | 52 | https://github.com/openai/codex/pull/51500; https://github.com/openai/codex/pull/50727 | no |
| 205 | gh-graphql-discussion | repo:openai/codex custom agents subagents | 0 | 7 | OK | 85 | https://github.com/openai/codex/discussions/46658; https://github.com/openai/codex/discussions/31203 | no |
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

The 31 failed first-attempt views (seq 161-180, 191-198, 206-208: gh 2.98 refuses `--comments` with `--json`) are in the log; each was rerun.

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


## 7. Findings with citations

### 7.1 Roles (Q1): missing or redundant for this repo's work

| Candidate | Verdict | Why |
| --- | --- | --- |
| Planner or critic | No new role; the architect brief gains a refute-the-plan pass | Humanize fixes a plan contract with positive and negative tests before coding and has a fresh reviewer judge it (PR/alphaxiv-humanize-judgement.md:37); MP's typed stages (grill-with-docs, to-spec) already hold the human-approved contract (R-056). A separate critic adds a round with no measured gain here. |
| Verifier or refuter | No new role; the reviewer and security-reviewer briefs open with "assume this is broken and prove it", looped until findings converge, with R12 guard 6 (P1 needs `path:line` and a failure scenario) as the stop rule | "Refute, Don't Review" (PR/cmdctrl-refute-dont-review.md, 2026-10-11); Anthropic's claude-security verifiers default to reject (R12 §2, clone unchanged, seq 221); review spirals on trivial work (R12 §3.2). |
| Blind tester | No new role; R12's differential check (locked tests fail at `test_commit`, pass at head) stays | No new evidence since R12; the role's value was never seeing the diff, which the check reproduces as a fact. |
| Dependency and release intake | **Add** as a brief on `frontier-scheduler` (read-only) at Sonnet 5.5 high, fed by a mechanical collector | Both write-ups split it the same way: deterministic rules and collection first, the model reads release notes between versions and quotes the line, and the output is a decision brief, not a change (PR/devtocash-dependency-triage-agent.md:8; PR/aident-dependency-upgrade-review.md:42). MP has three open requests of this shape: R-158, R-167, R-176. |
| Security reviewer | Keep (R12); extend its lens to public-text write paths (R-174) | Fable 5.1 leads Opus 5.5 on secure code once memorized solves are removed (37.4% against 33.5% SecPass, PR/endorlabs-opus55-secure.md:22). Defence before publishing needs two independent layers that fail in different directions (PR/savage-defense-before-publish.md:11); the scan itself stays mechanical (D179), the reviewer audits the paths. |
| Orchestrator | Keep the parent; make its limits mechanical | A coordinating Opus session ran 16 implementers against a written limit of 6 (G/anthropics_claude-code-101650.json). Claude Code has `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (default 20) and `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (default 3) (CC/env-vars.md:312, 318; CC/sub-agents.md:1014-1046). In a 2,124-run study, Claude Code with dynamic workflows (ultracode) solved 59 of 100 SWE-bench Verified tasks against 83 without, and 33.2% of failures were shared-state writes (PR/canberk-subagent-study.md:37, 79). |
| Cross-vendor reviewer | **Add** for C++ units | "A defect overlooked by the builder survives only if the reviewer also misses it. That benefit depends on the two agents having different blind spots" (PR/alphaxiv-humanize-judgement.md:37); a switched reviewer "changes which bugs slip through" (PR/coderabbit-opus55-review.md:76); a practitioner runs Codex as reviewer for Claude-built code by design (PR/mertsahin-two-agent-team.md:8). It is a second lens, not the gate: GPT-6 Sol at medium scored F1 48.7% against Opus 5.5's 56.8% in Qodo's reviewer test (PR/qodo-which-llm-review.md:49-159). |

C++26 P2996 evidence is still thin: stage 1 found tutorials and talks but no measurement of agents on
reflection code (seq 95). Nothing changes the C++ rows.

### 7.2 Models and effort (Q2)

- **Model list and effort levels in 2.1.300 are unchanged from R12.** Fable 5.1, Opus 5.5, Sonnet
  5.5 and Haiku 5.5 accept `low` to `max`; Opus 5.5, Sonnet 5.5 and Haiku 5.5 default to `medium`
  (CC/model-config.md:598-608). Diffs against R12's mirror: model-config.md changed one paragraph
  (extended context), the platform models overview and pricing pages changed only image URLs, and
  effort.md and choosing-a-model.md are identical (`diff` of PF/* against R12's copies).
- **Per-call model and effort on the Agent tool** work as R12 said (CC/sub-agents.md:353-358, 413).
  New since R12's reading: a mod's `agent.spawn` hook can replace the model (CC/sub-agents.md:358;
  CC/plugins/mods/reference.md:151), from 2.1.299 that hook also fires on resume and can refuse it
  (CL:214; the reference page still says it does not, reference.md:153), and from 2.1.300 it can
  rewrite a workflow agent's prompt and model (CL:11). This is the D92 route for R12 guard 4.
- **Reviewer evidence leans to Opus 5.5.** Qodo, one reviewer at high effort on traced real bugs:
  Opus 5.5 F1 56.8% at $1.00 per PR, Sonnet 5.5 54.9% at $0.73, Fable 5.1 53.5% at $2.31
  (PR/qodo-which-llm-review.md:49-95, 2026-10-12; its prose gives Sonnet 54.0%, a mismatch).
  R12 had the same direction from one source (antonshubin: Opus 5.5 replaced Fable 5.1 as reviewer
  at about a third of the price). CodeRabbit found Opus 5.5 catches a different mix of bugs from
  its production reviewer (PR/coderabbit-opus55-review.md:76). R12 kept Fable for diversity from the Opus author
  and because the user's Q9/Q10 policy puts review on Fable (MP model-policy.md:13). Both still
  hold, so the row is confirmed and flagged; the cross-vendor reviewer adds the diversity that a
  same-family pair lacks.
- **Security reviewer stays on Fable 5.1 xhigh** (PR/endorlabs-opus55-secure.md:22), but expect it
  to be served by Opus 4.8 often: cyber flags re-run Fable 5.1 and Opus 5.5 on Opus 4.8
  (CC/model-config.md:518-522) and CC#91923 measured 18 of 19 Fable child dispatches switching after
  the first tool result.
- **Sonnet 5.5 got cheaper.** Cache reads were halved, "around 20% cheaper on most agentic work"
  (A/claude-haiku-5-5.md:17; Claude Code's cost display followed in 2.1.296, CL:347). That
  strengthens the doc-writer row and suits the new upgrade-intake brief. On a cyber flag Sonnet 5.5
  falls back to Sonnet 5, not Opus 4.8 (CC/model-config.md:521).
- **Haiku 5.5 for the extractor is confirmed.** Anthropic positions it as a subagent beside Opus 5.5
  and Sonnet 5.5 (A/claude-haiku-5-5.md:11); in one 23-task subagent test Haiku 5.5 and Sonnet 5.5
  averaged 0.98 against Opus 5.5's 1.0 (PR/ovidius-subagents-benchmark.md:3).
- **Opus 5.5 for the implementer is confirmed.** Meetzest: a merged PR cost $19 in Opus 5.5 tokens
  against $27 in Fable 5.1, and inside the same repo, engineer and week the first-review flag rate
  of Opus 5.5 PRs differed from Fable 5.1's by -7 points (95% interval -30 to +15)
  (PR/meetzest-best-model-1232-prs.md:34, 71). Endor Labs: 6x cheaper and 2x faster than Fable 5.1,
  with a large memorization discount on its scores (PR/endorlabs-opus55-secure.md:22).

### 7.3 Tools per role (Q3), against MP's `.claude/agents/*.md`

| File | Today (L/mp-claude-agents-frontmatter.txt) | Proposed delta | Basis |
| --- | --- | --- | --- |
| `reviewer.md` | fable, high, `plan`, denies Edit, Write, NotebookEdit | deny `Agent` too | CC/sub-agents.md:1030 ("omit `Agent` ... a reviewer that should stay read-only"); R12 §2.2 noted it |
| `implementer.md` | opus, high, `acceptEdits`, all tools, `tdd` | deny `Agent`; `experimental: {cacheTtl: 1h}` | nesting adds cost and an unmanaged writer; subagents use the 5-minute cache by default (CC#99360 via R12b D2), and `cacheTtl` sets it per subagent from 2.1.248, ignored while usage credits are in use (CC/sub-agents.md:312) |
| `retro-writer.md` | fable, high, `acceptEdits`, `writing-for-agents` | `experimental: {cacheTtl: 1h}`; brief rule on record files | CC/sub-agents.md:312; G/anthropics_claude-code-101519.json |
| `doc-writer.md` | sonnet, high, `acceptEdits`, `writing-for-agents` | brief rule on record files | G/anthropics_claude-code-101519.json |
| `extractor.md` | haiku, low, `plan`, denies Edit, Write, NotebookEdit | optional `omitClaudeMd: true` and an explicit `tools: Read, Grep, Glob, Bash` | CC/sub-agents.md:296, 307; a fixed tool list boots at about 10K tokens against 60K for all tools (practitioner figure, RP/cdowin-agentic-sdlc@6012c29 `AGENTS-AND-MODELS.md:13-14`, UNVERIFIED here) |
| `frontier-scheduler.md` | opus, high, `plan`, denies Edit, Write, NotebookEdit, Agent | none | already read-only |
| all | no `mcpServers`, no `isolation`, no `memory` | keep all three unset | inline MCP servers duplicated from the parent get killed at subagent teardown (G/anthropics_claude-code-101240.json); isolation bugs (§1.1 rule 3); `memory` is a second learnings store (R12, ADR 0001) |

Skills: subagents preload at most 32 skills from `skills:` (CL:483, 2.1.295), and `${CLAUDE_EFFORT}`
in a preloaded skill expanded to the session's effort until CC#101169 closed on 2026-10-11 (seq 283).
Skill `model:` and `effort:` frontmatter is ignored when Claude invokes the skill through the Skill
tool (CC#98898, open, reproduced on 2.1.296), so a role's effort belongs in the agent file and the
Agent call, never in a skill.

### 7.4 Other knobs (Q4)

- **Frontmatter fields in 2.1.300**: `name`, `description`, `tools`, `disallowedTools`, `model`,
  `permissionMode`, `maxTurns`, `autoCompactWindow` (new, 2.1.296), `skills`, `mcpServers`, `hooks`,
  `memory`, `background`, `omitClaudeMd`, `effort`, `isolation`, `color`, `initialPrompt`,
  `experimental.cacheTtl` (CC/sub-agents.md:294-312). Since 2.1.296, `claude --debug` names
  unrecognized fields (CL:343; CC/sub-agents.md:287-290), a cheap check for agent-file typos.
- **Context budget.** `autoCompactWindow` (100,000 to 1,000,000) lets one role compact earlier
  (CL:290; CC/sub-agents.md:301). MP's ceiling is a stop-and-dispatch rule at 500K, not compaction
  (model-policy.md "Thresholds"), so leave it unset unless a role should compact instead of stopping
  (open question 4).
- **Background or foreground.** Fork mode is on for this user (`CLAUDE_CODE_FORK_SUBAGENT=1`,
  L/claude-settings-selected-keys.json), so spawned subagents run in the background; nothing to
  change.
- **Units in flight.** Keep 3 writer lanes. Enforce it: `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6`
  (3 writers plus reviewer, security reviewer and one extractor) caps all subagents; the
  ticket-frontier skill still owns the writer count. A settings change needs its own admission
  (MP/AGENTS.md).
- **Teams, forks and workflows.** Teams: off (experimental, CC/agent-teams.md:10; effort and tool
  limits dropped for named teammates, CC#100701, CC#81852, unchanged). Forks: never for judgement
  roles; fine for parent side tasks under `fork_deny` (R12). Workflows: `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL`
  (CL:291) and the 2.1.300 `agent.spawn` rewrite make them configurable, but a workflow `agent()`
  strips the Agent tool from custom types (CC#102096, 2026-10-14) and the study above found
  ultracode worse on bounded fixes; use workflows for read-only fan-out such as research, not lanes.
- **Observation.** `agentType` is in the `subagentStatusLine` payload from 2.1.293 (CL:523) and the
  `turn.start` mod hook hears subagents and teammates from 2.1.299 (CL:264): enough for a mod that
  records each role's served model and effort per turn.

### 7.5 The Codex side (Q5)

- **Models.** Recommended: `gpt-6.1-sol` ("near-Astra performance ... at a lower cost"), `gpt-6-astra`
  for the hardest work, `gpt-6-luna` for clear repeatable tasks; GPT-6 Sol and the GPT-5.6 family
  remain during the rollout (CX/models.md:99-121, 161-178). GPT-5.5 retired from Codex with ChatGPT
  sign-in on 2026-10-14 at 19:00 UTC (CX/models.md:5-21); MP's `.codex` files name no model, so
  nothing pins it.
- **Effort.** `low`, `medium`, `high`, `xhigh`, `max`, `ultra` where the model supports them; Luna
  goes up to `max` (CX/config-file/config-reference.md:1081-1085; CX/models.md:199-207). Docs advise
  `high` for reviewer and security agents (CX/agent-configuration/subagents.md:161).
- **Custom agents** (`.codex/agents/*.toml`): required `name`, `description`,
  `developer_instructions`; optional `model`, `model_reasoning_effort`, `model_reasoning_summary`,
  `model_verbosity`, `features.*` (only to disable shell, apps, plugins, memories or the
  request-permissions tool) and `skills.config` (CX/agent-configuration/subagents.md:284-345).
  Precedence: explicit spawn value, then `[agents]` default, then parent, then the agent file wins
  where it sets a value (lines 290-299). `spawn_agent` takes `model` and `reasoning_effort` per call
  (maintainer comment of 2026-10-13 on CX#14039 with source links).
- **Sandbox and approvals.** Modes `read-only`, `workspace-write`, `danger-full-access`; approvals
  `on-request`, `never`, `granular`; `untrusted` is retired (CX/sandboxing.md:184-215;
  CX/config-file/config-reference.md:85). Subagents inherit both (above).
- **Tools and MCP.** MCP servers come from the parent only; a per-agent opt-out is still a request
  (CX#20135, seq 203). Hooks include `SubagentStart` and `SubagentStop` (CX/hooks.md:25-28), but
  not `PreToolUse` on `spawn_agent` (CX#49736).
- **AGENTS.md and rules.** Codex concatenates `AGENTS.md` from the repository root down to the
  working directory, capped at 32 KiB (CX/agent-configuration/agents-md.md:11-15); MP's root chain is
  3,946 bytes at the root and at most 6,446 bytes in `dev/` (L/mp-agents-md-sizes-and-skill-mirrors.txt).
  `.codex/rules` take `prefix_rule` with `forbidden` > `prompt` > `allow` (CX/agent-configuration/rules.md:59-64);
  MP's `gh-write.rules` fits.
- **Skills.** Codex reads `.agents/skills` from the working directory up to the repository root
  (CX/build-skills.md:93-103); MP's six mirrors are byte-identical to `.claude/skills`
  (L/mp-agents-md-sizes-and-skill-mirrors.txt).
- **Worktrees.** Codex subagents share the parent's working directory; worktrees are per chat in the
  app (CX/environments/git-worktrees.md:14-24), so each Codex lane is its own `codex exec -C`.
- **Local flags.** `multi_agent` stable and on, `multi_agent_v2` stable and off, `worktrees` and
  `hooks` on (L/codex-features-list.txt).

### 7.6 Watch inputs (Q6): what changed since R12

- **Saved searches.** The four D138 rows return R12's counts exactly: 6, 13, 6 and 8, with controls
  61, 30, 75 and 17 (seq 209-265). R12b's two rows are also unchanged: superpowers-dispatch-effort 0
  (now `EMPTY_VERIFIED`: control 30 and the clone agree, seq 266-268) and monomind 4 (seq 269-271).
  The "agent effort rows": oh-my-claudecode `"effort:" path:agents` 0 (`EMPTY_VERIFIED`, seq 272-274);
  claude-plugins-official `effort path:agents` 0 while the clone holds 12 such files (seq 275-277), so
  code search still under-reports and that row should not be adopted.
- **Issue-search rows** (need a collector extension): `subagent hot reload` 49 total, `effort
  teammate` 100, `custom agent sandbox` on openai/codex 658 (seq 304-309); all controls pass. The
  last is too broad; §10 narrows the proposal.
- **Clones.** 11 of 12 R12 clones have the same HEAD; claude-plugins-official gained one commit, a
  marketplace bump for incident-io (c2bdb42, #6602), with no agent change (seq 210-248). Its
  claude-security agents still set `effort` low 2, medium 4, xhigh 6.
- **R12 and R12b threads.** All 13 re-read threads are open with the same comment count as R12's
  mirror (seq 228-247).
- **Claude Code.** 2.1.300 shipped after R12 (R12 ran 2.1.299): `agent.spawn` can rewrite a workflow
  agent's prompt and model (CL:11) and agent hooks honour their `model` (CL:32). The docs gained the
  `autoCompactWindow` frontmatter row and the debug-log check (CC/sub-agents.md:287-301) and the
  teammate rule for it (CC/agent-teams.md:280). New threads since 2026-10-12 that matter: CC#101887,
  CC#101519, CC#102096, CC#101650, CC#101943 (headless output should name the answering model),
  CC#102156 (change a running subagent's effort).
- **Codex.** GPT-6.1 Sol became the recommended model and GPT-5.5 retired today for ChatGPT sign-in
  (CX/models.md:5-21, 99-121); Codex CLI 0.162.1 is current on this host.
- **X posts again present "Official Anthropic tip" and "Official OpenAI tip" routing**, including a
  `claude --verifier fable` flag (Last30Days, seq 146). Neither the CLI reference, the changelog nor
  the docs mirror has a `--verifier` flag (grep of CC and CL): UNVERIFIED, as R12 found for the same
  accounts.

## 8. Code examples found

- **openai/codex@4ca84a10696623fcd7c200db3df9c41671d3bad0** (sparse clone RP/openai-codex, seq 263):
  `codex-rs/core/src/agent/role.rs:37-48` (`AgentRoleOverrides`: instructions, model, effort,
  summary, verbosity, personality, service tier, features, skills; no sandbox),
  `role.rs:90-105` (features can only be switched off: shell, apps, plugins, memory,
  request-permissions), `child_config.rs:103-110, 178-201` (the child copies the parent's approval
  policy, approvals reviewer, cwd and permission profile). Excerpt in
  L/codex-agent-role-and-child-config-excerpt.txt.
- **openai/codex@12cca49** (cited by OpenAI staff on CX#14039, 2026-10-13, not cloned):
  `codex-rs/core/src/tools/handlers/multi_agents_spec.rs#L649-L683` (the `spawn_agent` schema with
  `model` and `reasoning_effort`) and `codex-rs/core/src/agent/child_config.rs#L204-L260`.
- **cdowin/agentic-sdlc@6012c29** (RP/cdowin-agentic-sdlc, seq 264): `AGENTS-AND-MODELS.md:8-15`
  (set the model on every spawn, cap effort at high, fixed-tool agents), `:187-198` (Codex has no
  agent-type selector or tool allowlist; a worktree path in a brief is not write confinement) and
  `plugin/contract/runtimes.json` (a per-runtime capability map marking each control `enforced`,
  `instructed`, `unverified` or `absent`, a shape that suits R-177's machine-readable inventory).
- **bity-labs/tstack#81** (open PR, G/bity-labs_tstack-81.json): a tiered GPT-6 roster
  (orchestrator Sol high, dev tiers Luna off / Sol medium / Sol xhigh, reviewer Astra xhigh, scout
  Luna low).
- **novotnyllc/railyard#70** (merged 2026-09-29, G/novotnyllc_railyard-70.json): Codex defaults to
  GPT-6.1 Sol medium, Sol high for review, Astra only after a demonstrated gap, Luna for routine
  low-judgement work.
- **anthropics/claude-plugins-official@c2bdb427** (RP/claude-plugins-official, seq 221):
  `plugins/claude-security/agents/*.md` unchanged since R12 (effort low 2, medium 4, xhigh 6).

## 9. Routes

`fx` is `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`. Keys reached commands only through the environment: Exa and Serper
headers and the SerpApi URL go to curl as a config on stdin (`S/bin/keyhttp.sh`), and preflight
checks printed key presence as `set` or `unset` only. Scripts: `S/bin/run.py` (one D137 row per call,
written right after the call), `S/bin/fixup.py` (local rows and status corrections, each with a
`status_note`), `S/bin/sections.py` (builds sections 2 to 6 and this table). The aggregate below is
built from the log; the per-call table is in the log file.


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

## 10. Proposed saved-search rows

`dev/saved-searches.toml` was not edited. Each row below was reproduced read-only with its control
in this run (seq in the comments).

```toml
[[search]]
id = "codex-subagent-defaults"
query = "default_subagent_reasoning_effort"
repo = "openai/codex"            # 9 hits (seq 278, 282); control README 167 (seq 288)
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "codex-role-overrides"
query = "AgentRoleOverrides"
repo = "openai/codex"            # 1 hit, codex-rs/core/src/agent/role.rs (seq 321); control 167 (seq 322); re-read the struct when the count or file changes
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

Not proposed: `autoCompactWindow repo:anthropics/claude-code` (1 hit, the CHANGELOG only, seq 293);
`effort path:agents repo:anthropics/claude-plugins-official` (0 against 12 files in the clone, seq
275); `"effort:" path:agents repo:Yeachan-Heo/oh-my-claudecode` (0, verified against the clone, seq
272). For the last two, the watch should re-read the clone instead (D138 artifact note).

Issue-search rows, for when the collector can call `/search/issues` (it calls only `/search/code`,
`dev/collect_saved_search.py:179`); each should run with a `created:>` window equal to the last run:

| Proposed id | Query | Today (total) | Control |
| --- | --- | --- | --- |
| cc-subagent-hot-reload | `subagent hot reload repo:anthropics/claude-code` | 49 (seq 304) | `agent` 23,148 (seq 305) |
| cc-teammate-effort | `effort teammate repo:anthropics/claude-code` | 100 (seq 306) | 23,148 (seq 307) |
| codex-custom-agent-readonly | `custom agent sandbox_mode read-only repo:openai/codex` | 120 (seq 323) | `agent` 11,029 (seq 324) |

## 11. Open gaps

- **Provider gaps.** Firecrawl skipped: preflight showed -128 of 1,000 credits (seq 1, 9). Context7:
  "Monthly quota reached", two calls (seq 110, 111). Last30Days degraded: Reddit backup HTTP 402 and
  YouTube transcripts HTTP 429 and 402 (seq 146). A Reddit thread hit the webclaw login wall (seq
  139). Three learn.chatgpt.com pages returned HTTP 404 (seq 92, 93, 141, 320).
- **Not measured in MP.** No per-role cost or quality numbers yet; every reviewer comparison is from
  other workloads (Qodo, Meetzest, CodeRabbit). Measure after the first CT-59 waves from subagent
  transcripts, before changing the reviewer row.
- **Codex runtime not exercised.** No `codex exec` or `codex review` was run (no model sessions in
  this task), so the Codex roster is untested: whether a `codex exec -s read-only` launched from a
  workspace-write Codex parent can nest its sandbox on macOS is UNVERIFIED, and so is whether
  `codex review` honours `-s read-only`.
- **Codex served-model receipt.** Which rollout field carries the served model is unknown until
  CX#47779 lands; the receipt can only record the requested model today.
- **Docs disagree with the changelog** on whether `agent.spawn` runs on resume
  (CC/plugins/mods/reference.md:153 against CL:214). Test with the first dispatch-guard mod.
- **Secondary sources.** The effort flags (`tengu_harmonic_riddle`, `tengu_snappy_pelican`) come from
  a third-party binary-analysis site; only their names were confirmed locally, not their behaviour.
  Several practitioner pages may be AI-written (LoreAI's Codex comparison contradicts the Codex docs
  on custom agents and was not used, PR/loreai-codex-vs-cc-subagents.md).
- **Codex usage.** MP's guide expects Codex back after 2026-10-19; the user's Codex allowance and
  plan (which decide Astra or Sol access) were not checked.
- **C++26 evidence** remains thin (seq 95).
