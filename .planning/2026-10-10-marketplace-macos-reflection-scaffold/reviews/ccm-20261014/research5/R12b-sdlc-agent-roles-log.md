# R12b: stage-2 rerun and D137 query log for R12 (agent roles, models and effort)

Research R12b, session ccm-20261014, 2026-10-14. It completes R12
(`R12-sdlc-agent-roles.md` in this directory) to D137: stage 2 was rerun from the stage-1
results, every call was logged when it was chosen, and the sections below are built from the
whole log. Read-only apart from this report, the R12 query log, manifest and mirror; no
tracked file in MP changed and nothing was written to GitHub.

Abbreviations: MP = the repository root; O = `MP/offline/research/R12-sdlc-agent-roles/`;
the log is `O/queries.jsonl`; GH = `O/docs/github/issues/` (every thread cited here is
mirrored there as `<owner>_<repo>-<n>.json`); CC#n = anthropics/claude-code issue n. R12b rows
are seq 225 to 361 and carry `run: "R12b"`; rows 1 to 224 are R12's and unchanged (checked
with `cmp` against a copy taken before the first R12b call). Scripts and raw output:
`scratchpad/research5/R12b/` (`bin/run.py`, `bin/preflight.py`, `bin/sections.py`; raw files
also copied to `O/local/gh-r12b/`, 95 files, listed in `O/manifest.json`).

## Verdict

**R12's role table keeps every model and every effort level.** The new stage-2 evidence
changes how three rows are dispatched and turns one of R12's guards from a record into a
blocking check. Confidence: high on the receipt check (three open reports measured from transcripts, A1 to
A3, and a fourth a maintainer partly confirmed, A4); medium on the dispatch wording, whose
risk needs agent teams, which MP does not enable (R12 section 5.4).

| R12 row | Model and effort | What changes | Why (evidence) |
| --- | --- | --- | --- |
| Every row whose model differs from the parent's (architect, test-contract check, reviewer, security reviewer, retro-writer, escalation on Fable; doc-writer on Sonnet; extractor on Haiku) | unchanged | Guard 5 (model and effort receipt) becomes a gate: read `message.model` and `effort` from every assistant entry of the subagent transcript, fail the receipt on a mismatch and re-dispatch. `.meta.json`, the Agent result's `resolvedModel`, `/tasks` or the UI label, and the agent's own answer are not evidence. | The requested model is often not the model that ran (rows A1 to A6 below). |
| reviewer; security reviewer; test-contract check | unchanged | "Separate, named, never a fork" means `subagent_type: reviewer` with no `name` parameter, and never the bundled `/code-review` in place of MP's reviewer. The reviewer receipt proves the reviewer ran: transcript id, served model, and findings with `path:line` (R12 guard 6). | Named spawns become teammates, which drop effort and can drop tool limits (B1 to B3); `/code-review` has run inline or skipped its reviewers and still reported clean (B4 to B6). |
| test author (xhigh); security reviewer (xhigh) | unchanged | none | The per-invocation `effort` parameter works on this host's version, and the reported 8,000-token subagent cap that would have starved xhigh did not reproduce (C1 to C3). |
| all rows, cost confidence (R12 sections 3.3 and 9) | unchanged | Do not read per-role output cost from subagent transcripts until CC#100154 and CC#100830 close; the model field there is still usable. | D1, D2. |
| hot reload (R12 section 5.5) | n/a | Kept and widened: an `AGENTS.md` change made mid-session also does not reach later subagents of that parent session, so briefs name the files to re-read or the parent restarts at the planned handoff. | E1 to E3. |

Findings behind the table, each from a mirrored thread:

**A. Requested model versus served model.**
- A1. CC#100082 (2026-10-06, open): `model: sonnet` or `haiku` in user-scope frontmatter ran on
  the parent's Opus 5.5 in 1,149 of 1,371 spawns on 2.1.277 to 2.1.290, intermittently (the same
  versions also served the right model), measured from `message.model`; from 2026-10-07 60+ runs
  on 2.1.289 to 2.1.293 were correct with no changelog entry. It links CC#91890 (2026-09-03,
  open, labelled bug and has-repro): frontmatter `model: claude-opus-4-8` ran on the parent's
  Fable 5.1 on 2.1.259.
- A2. CC#83920 (2026-08-04, open): the per-call `model` parameter was ignored on 2.1.220 and
  2.1.222. A 2026-09-19 comment there: "The only ground truth we found is the transcript, which
  records the model per turn", after two "receipt" sessions reported success while running on
  Sonnet end to end.
- A3. CC#82252 (2026-07-29, open, three independent reproductions to 2.1.247): a `fable`
  override was served by `claude-sonnet-5` in long sessions, while `.meta.json`, the Agent
  result's `resolvedModel` and the agent's self-report all said Fable. First spawns of fresh
  sessions were served correctly. This hits the Fable rows directly, and R12's parent is a long
  session.
- A4. CC#85592 (2026-08-10, open; partly confirmed by a maintainer on 2.1.233):
  `CLAUDE_CODE_SUBAGENT_MODEL` beats an explicit per-call model, and `.meta.json` records the
  requested model, not the effective one. This host sets no such variable (R12 section 2.2).
- A5. UI labels: CC#77655 (2026-07-15, open, still on 2.1.270) renders the main session's model
  and effort in the subagent view; CC#97588 (2026-09-27) was retitled because the override
  worked and only the label was wrong. CC#95823 (2026-09-21, open): `.meta.json` held no model
  or effort field when filed. CC#87815 (2026-08-19, open): parallel fleets inherited the
  session's Fable tier and exhausted a weekly allowance.
- A6. What practitioners built in response: obra/superpowers#1631 (closed 2026-06-17; 78 of 150
  dispatches inherited the parent model until 6.0 put an explicit model at every dispatch
  site) and #2400 (2026-09-26, open draft, the same outside SDD); a `PreToolUse` hook on `Agent`
  that denies a spawn without an explicit model (CC#87815, comment of 2026-09-13);
  monoes/monomind#657 (merged 2026-10-07: refuses an `Agent` launch naming another model and
  reports `unexpected_models`); shakacode/agent-workflows#151 (2026-07-13, open: "never
  describe a requested route as observed execution without evidence"). Under D92 such a gate is
  a mod; it fits R12 guard 4 (named, non-fork dispatch), extended to "explicit `model` and
  `effort` on every `Agent` call".
- Consequence for the reviewer row: R12 argues that a Fable reviewer spreads blind spots
  against an Opus author. If the reviewer is silently served by Opus (A1) or Sonnet (A3), that
  diversity is gone and nothing shows it, so the receipt check is part of the independence rule,
  not bookkeeping.

**B. Reviewer dispatch.**
- B1. CC#81852 (2026-07-28, open; maintainer reproduced on 2.1.233 with agent teams on): an
  `Agent` call with a `name` is teammate dispatch, and a built-in type's tool limits were dropped
  (Explore wrote files). The maintainer saw a custom definition's `tools` kept; the reporter saw
  them dropped.
- B2. Teammates drop the per-invocation `effort` (CC#100701, cited by R12) and ignore the
  definition's `effort` (CC#80569, 2026-07-23, open, still on 2.1.286).
- B3. CC#100613 (2026-10-08, open): the docs create a teammate from a `name` on the `Agent`
  call when teams are on, and on 2.1.295 the schema offered only `description`, `prompt`,
  `subagent_type`, `model`, `effort` and `isolation`. So "named" in R12 must mean the
  `subagent_type`, and briefs never pass `name`.
- B4. CC#95165 (2026-09-17, open): in the desktop app, 8 of 8 `/code-review` runs ran inline in
  the authoring session with no subagent transcript.
- B5. CC#100401 (2026-10-08, open): on 2.1.285 and later the code-review plugin launched 0 to 2
  agents, skipped its reviewers and still posted "No issues found".
- B6. CC#75757 (2026-07-08, open): reviewer subagents that died on a spend limit produced a
  clean review result. CC#89971 (2026-08-27, open): a fork ignored an explicit read-only
  boundary and wrote a migration, which supports R12's "never a fork" for judgement roles.

**C. Effort.**
- C1. CC#100347 (2026-10-07, open docs issue): the `effort` parameter added in 2.1.292 was
  honoured on 2.1.293 (`effort: "low"` over a definition's `xhigh`, recorded in the assistant
  entries and `.meta.json`); the per-invocation `model` accepts aliases only (`sonnet`, `opus`,
  `haiku`, `fable`). CC#98391 (2026-09-30) had asked for it. This host runs 2.1.299 (R12).
- C2. Before 2.1.292 a per-invocation effort was "accepted and silently discarded", which is why
  mikekelly/promode#4 (merged 2026-07-10) pre-baked model and effort per definition.
- C3. CC#78460 (2026-07-17, open): the claimed 8,000-token subagent cap did not reproduce for a
  maintainer on 2.1.233 (10,697 tokens, `end_turn`), and the reporter withdrew the
  subagent-only claim on 2026-08-17.

**D. Measuring cost per role.**
- D1. CC#100154 (2026-10-07, open) and CC#100830 (2026-10-09, open; a comment dates it to
  2.1.278): subagent transcripts keep the start-of-stream usage, so output tokens are
  under-reported about 30 times. `message.model` is still written, so A's receipt still works.
- D2. CC#99360 (2026-10-04, open, 2.1.278): subagents write the 5-minute cache while the main
  session writes the 1-hour cache, so a slow subagent pays repeated cache writes. R12's "Fable
  costs about 1.25x Opus in long cached contexts" holds for cache reads only.

**E. Hot reload and stale instructions.**
- E1. CC#98528 (2026-09-30, open): definitions added mid-session were not spawnable for minutes
  on 2.1.280 and 2.1.285 although the directory existed at start.
- E2. CC#98685 (2026-10-01, open): all personal agents intermittently failed to register at
  session start.
- E3. CC#88886 (2026-08-22, open): a subagent gets the CLAUDE.md and memory the parent captured
  at its own start, not at spawn (measured 8h39m stale). In MP the retro-writer writes learnings
  into `AGENTS.md` files mid-session, so later subagents of the same parent miss them.

**Also read, no change.** obra/superpowers#2326 (2026-09-18, open: an Approved verdict that
still carried an Important finding cost a full fix and re-review round) supports R12 guard 6.
Yeachan-Heo/oh-my-claudecode#1240 (closed 2026-03-03) found an adversarial framing overlay gave
more thorough reviews in an A/B, and the maintainer kept structured gap analysis instead.
anthropics/claude-plugins-official#6352 (2026-10-03, open) says tier names pinned in
`code-review.md:11-27` degrade with each release, which supports passing aliases from MP's model
policy rather than freezing names into briefs. BaseInfinity/claude-sdlc-harness#730
(2026-09-27, open) mutation-tests its effort-per-model guard, a cheap way to prove the receipt
gate catches a wrong model. CC#101924 (2026-10-14, open): an Opus 5.5 session deleted and
rewrote its own test fixture against a written rule, which supports R12's test lock. The four
D138 saved searches reproduce today with exactly R12's counts (section 4).

## 1. Queries sent to each tool, plugin or service (stage 1), exact text

All stage-1 rows are R12's, unchanged (seq 1 to 128, 215, 216). `fx` is the fnox prefix.

### 1.1 Exa (14 queries)

Command shape: `fx exa2.sh <out> "<query>" 10 [startPublishedDate]`, POST api.exa.ai/search, type auto, 10 results, text capped at 1,500 characters.

| seq | Query (exact) | startPublishedDate |
| --- | --- | --- |
| 42 | Anthropic engineering harness design long-running agents planner generator evaluator | none |
| 43 | Anthropic engineering how we built our multi-agent research system orchestrator subagents | none |
| 44 | AI code reviewer agent rubber stamps approves everything sycophancy LGTM subagent | 2026-07-01 |
| 45 | Spending your effort Claude Code blog effort levels | none |
| 46 | Claude Code subagents context bloat orchestrator token cost multi-agent too many agents | 2026-07-01 |
| 47 | Choosing a Claude model and effort level in Claude Code | none |
| 48 | Claude Code subagent team roles architect implementer reviewer QA model per role | 2026-07-01 |
| 49 | adversarial verification agent refute findings multi-agent code review false positives | 2026-06-01 |
| 50 | coding agent modifies or deletes tests to make them pass reward hacking Claude Code | 2026-07-01 |
| 51 | C++ test-driven development with Claude Code agents clang compile errors | 2026-06-01 |
| 52 | Anthropic engineering blog Claude Code agentic coding test-driven development verification | none |
| 53 | Claude Code subagents separate test writer agent and implementer agent TDD | 2026-07-01 |
| 54 | Fable 5.1 Opus 5.5 Sonnet 5.5 Haiku 5.5 which model for subagents code review cost | 2026-08-01 |
| 55 | best Claude Code subagent collections wshobson agents VoltAgent superpowers oh-my-claudecode comparison | 2026-06-01 |

### 1.2 Serper (6 queries)

Command shape: `fx serper.sh <out> "<query>"`, POST google.serper.dev/search, num 10.

| seq | Query (exact) |
| --- | --- |
| 120 | Claude Code subagent test-writer separate from implementer agent weakens tests |
| 121 | wshobson agents model tier haiku sonnet opus inherit |
| 122 | "subagent-driven-development" superpowers spec reviewer code quality reviewer |
| 123 | site:github.com claude code agents implementer reviewer test-author model effort frontmatter |
| 124 | oh-my-claudecode agents critic planner executor model |
| 125 | Claude Code reviewer subagent rubber stamp independent review model Fable Opus |

### 1.3 Last30Days (3 runs)

- seq 126: topic "claude code subagent roles and models", plan `plan.json` (run1.md), `--search reddit,hackernews,github,x,youtube`. Subqueries: primary: "claude code subagents roles reviewer implementer"; rubber: "claude code reviewer agent rubber stamp tests weakened"; cost: "claude code subagent model haiku sonnet opus fable cost".
- seq 127: topic "claude code tdd test author and critic agents", plan `plan2.json` (run2.json), `--search reddit,hackernews,github,x,youtube`. Subqueries: primary: "claude code tdd test writer subagent"; critic: "claude code critic agent adversarial review subagent"; cpp: "claude code c++ agents clang tests".
- seq 128: topic "claude code subagent roles and models", plan `plan.json` (run1.json), `--search reddit,hackernews,github,x,youtube`. Subqueries: primary: "claude code subagents roles reviewer implementer"; rubber: "claude code reviewer agent rubber stamp tests weakened"; cost: "claude code subagent model haiku sonnet opus fable cost".

### 1.4 Context7 and Firecrawl (4 calls)

- seq 116 context7: `ctx7 library "claude code"`.
- seq 117 context7: `ctx7 library superpowers`.
- seq 118 firecrawl: query text not saved by R12 (command shape `fx firecrawl search "<q>" --limit 5 --json`).
- seq 119 context7: `ctx7 docs /websites/code_claude "<query text not saved>"`.

### 1.5 webclaw (103 URLs)

Command shape: `webclaw -t 60 <url> -f markdown > <file>`. Each URL below is the exact text sent.

- 1 `https://code.claude.com/docs/llms.txt`
- 2 `https://code.claude.com/docs/en/common-workflows.md`
- 3 `https://code.claude.com/docs/en/agents.md`
- 4 `https://code.claude.com/docs/en/model-config.md`
- 5 `https://code.claude.com/docs/en/best-practices.md`
- 6 `https://code.claude.com/docs/en/agent-teams.md`
- 7 `https://code.claude.com/docs/en/sub-agents.md`
- 8 `https://code.claude.com/docs/en/costs.md`
- 9 `https://code.claude.com/docs/en/workflows.md`
- 10 `https://code.claude.com/docs/en/fast-mode.md`
- 11 `https://code.claude.com/docs/en/skills.md`
- 12 `https://code.claude.com/docs/en/worktrees.md`
- 13 `https://code.claude.com/docs/en/settings.md`
- 14 `https://code.claude.com/docs/en/cli-reference.md`
- 15 `https://code.claude.com/docs/en/plugins/components.md`
- 16 `https://code.claude.com/docs/en/ultrareview.md`
- 17 `https://code.claude.com/docs/en/plugins/manifest-reference.md`
- 18 `https://code.claude.com/docs/en/goal.md`
- 19 `https://code.claude.com/docs/en/code-review.md`
- 20 `https://code.claude.com/docs/en/features-overview.md`
- 21 `https://code.claude.com/docs/en/how-claude-code-works.md`
- 22 `https://code.claude.com/docs/en/prompt-caching.md`
- 23 `https://code.claude.com/docs/en/context-window.md`
- 24 `https://code.claude.com/docs/en/security-guidance.md`
- 25 `https://code.claude.com/docs/en/agent-view.md`
- 26 `https://code.claude.com/docs/en/large-codebases.md`
- 27 `https://code.claude.com/docs/en/tools-reference.md`
- 28 `https://code.claude.com/docs/en/whats-new/2026-w16.md`
- 29 `https://code.claude.com/docs/en/commands.md`
- 30 `https://code.claude.com/docs/en/whats-new/2026-w20.md`
- 31 `https://code.claude.com/docs/en/agent-sdk/subagents.md`
- 32 `https://code.claude.com/docs/en/whats-new/2026-w21.md`
- 33 `https://code.claude.com/docs/en/whats-new/2026-w22.md`
- 34 `https://code.claude.com/docs/en/whats-new/2026-w24.md`
- 35 `https://code.claude.com/docs/en/whats-new/2026-w30.md`
- 36 `https://code.claude.com/docs/en/whats-new/2026-w27.md`
- 37 `https://code.claude.com/docs/en/whats-new/2026-w32.md`
- 38 `https://code.claude.com/docs/en/whats-new/2026-w33.md`
- 39 `https://code.claude.com/docs/en/whats-new/2026-w37.md`
- 40 `https://code.claude.com/docs/en/whats-new/2026-w36.md`
- 41 `https://www.anthropic.com/engineering`
- 56 `https://www.anthropic.com/engineering/harness-design-long-running-apps`
- 57 `https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents`
- 58 `https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents`
- 59 `https://www.anthropic.com/engineering/building-c-compiler`
- 60 `https://www.anthropic.com/engineering/multi-agent-research-system`
- 61 `https://www.anthropic.com/engineering/claude-code-best-practices`
- 62 `https://www.anthropic.com/research/property-based-testing`
- 63 `https://www.anthropic.com/research/multiagent-systems`
- 64 `https://www.anthropic.com/engineering/building-effective-agents`
- 65 `https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents`
- 66 `https://www.anthropic.com/engineering/managed-agents`
- 67 `https://www.anthropic.com/claude-opus-5-5`
- 68 `https://claude.dev/blog/spending-your-effort/`
- 69 `https://alignment.anthropic.com/2026/reward-seeker/`
- 70 `https://claude.com/blog/claude-model-and-effort-level-in-claude-code`
- 71 `https://claude.com/blog/maximizing-the-value-of-your-claude-code-sessions`
- 72 `https://claude.com/blog/agentic-coding-is-straining-ci-heres-how-we-scaled-test-impact-analysis-at-anthropic`
- 73 `https://claude.com/blog/building-verification-loops-in-claude-code-with-skills`
- 74 `https://academy.claude.com/tutorials/choosing-the-right-effort-level-in-claude-code`
- 75 `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5`
- 76 `https://platform.claude.com/docs/en/build-with-claude/effort`
- 77 `https://platform.claude.com/docs/en/about-claude/models/choosing-a-model`
- 78 `https://platform.claude.com/docs/en/about-claude/pricing`
- 79 `https://platform.claude.com/docs/en/about-claude/models/overview`
- 80 `https://code.claude.com/docs/en/advisor.md`
- 81 `https://code.claude.com/docs/en/cross-session-messaging.md`
- 82 `https://code.claude.com/docs/en/hooks.md`
- 83 `https://code.claude.com/docs/en/env-vars.md`
- 84 `https://www.powerduck.com/blog/ai-review-bot-reviewing-own-diff/`
- 85 `https://debugly.dev/agent-reviewing-agent-echo-chamber/`
- 86 `https://skylos.dev/blog/testwashing-coding-agents-delete-tests`
- 87 `https://claudelab.net/en/articles/claude-code/claude-code-fork-default-review-agent-named-boundary`
- 88 `https://www.jeremyknox.ai/blog/your-ai-code-reviewer-agrees-with-everything-that-is-the-bug/`
- 89 `https://agenticlab.sunilprakash.com/patterns/rubber-stamp-verifier/`
- 90 `https://dev.to/penloom_studio_829b7817d3/your-ai-agent-will-pass-any-test-its-allowed-to-edit-51fo`
- 91 `https://dev.to/mattbusel/i-tried-to-make-claude-code-cheat-on-tests-heres-when-it-did-2a0k`
- 92 `https://dev.to/mattbusel/my-coding-agent-kept-fixing-tests-by-editing-them-so-i-made-it-impossible-1582`
- 93 `https://dev.to/haoli/my-agent-changed-tobe10-to-tobe9-and-called-it-done-i-built-hooks-to-stop-that-8c4`
- 94 `https://www.btsavvy.com/insights/ai-agents-cheat-on-their-own-tests/`
- 95 `https://www.vibe-coding.academy/blog/how-to-force-red-green-refactor-discipline-on-claude-code-with-subagents-and-hoo/`
- 96 `https://dev.to/aicoding-guide/make-a-coding-agent-write-the-failing-test-before-the-implementation-57c1`
- 97 `https://newsletter.agentbuild.ai/p/why-ai-written-tests-pass-but-still`
- 98 `https://jeanfbrito.github.io/posts/benchmark-subagents-the-way-you-run-them/`
- 99 `https://antonshubin.com/blog/opus-5-5-vs-sonnet-5-agent-costs`
- 100 `https://meetzest.com/blog/best-model-for-coding`
- 101 `https://djtal.ch/en/blog/2026-10-08-ai-subagents-model-delegation`
- 102 `https://tokenjam.dev/blog/2026-07-04-subagent-token-counts-are-wrong`
- 103 `https://www.mindstudio.ai/blog/claude-code-subagents-cost-tokens`
- 104 `https://dev.to/aidiveyt/your-claude-code-subagents-never-touch-haiku-55-i-measured-what-routing-them-there-gives-back-53h2`
- 105 `https://www.tinyfish.ai/blog/agentic-coding-context-vs-tokens-subagents`
- 106 `https://withagents.dev/posts/post-42-the-refutation-swarm`
- 107 `https://dev.to/enjoy_kumawat/i-added-more-verifiers-to-catch-bad-ai-findings-precision-stopped-improving-26a5`
- 108 `https://kaairos.com/blog/best-claude-code-agent-repos-audit`
- 109 `https://www.alphaxiv.org/abs/2608.18167`
- 110 `https://thakicloud.com/tech-blog/en/research/verify-gated-fanout-pareto/`
- 111 `https://www.claudecodeclub.ai/blog/claude-code-effort-levels`
- 112 `https://backgrind.com/blog/claude-code-effort-levels/`
- 113 `https://usagecut.com/when-to-use-claude-code-subagents`
- 114 `https://www.maxresearchcollective.com/articles/claude-code-agent-teams.html`
- 115 `https://akitao.com/en/k/giai-phap-chong-sycophancy-trong-multi-agent/`
- 215 `https://www.reddit.com/r/ClaudeCode/comments/1wvhzr2/my_claude_code_subagent_setup_orchestrator_doers/`
- 216 `https://old.reddit.com/r/ClaudeCode/comments/1wvhzr2/my_claude_code_subagent_setup_orchestrator_doers/`

## 2. Results from each (stage 1)

### 2.1 Search providers

| seq | Provider | rc | HTTP | Hits | Top results | Used |
| --- | --- | --- | --- | --- | --- | --- |
| 42 | exa | 0 | 200 | 10 | [Harness design for long-running application development \ Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps); [README.md at main · anthropics/cwc-long-running-agents](https://github.com/anthropics/cwc-long-running-agents/blob/main/README.md); [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents); [Effective harnesses for long-running agents \ Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents?s=09); [docs/research/260324_anthropic_harness_design.md at main · anxiong2025](https://github.com/anxiong2025/harness/blob/main/docs/research/260324_anthropic_harness_design.md) | no |
| 43 | exa | 0 | 200 | 10 | [How we built our multi-agent research system \ Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system); [How we built our multi-agent research system - Guide (Free) \| THE D*AI](https://www.beri.net/learning/anthropic-multi-agent-research-system); [How we built our multi-agent research system - Anthropic](https://www.lqdev.me/responses/anthropic-how-we-built-multi-agent-system/); [Building Multi-Agent Research Systems - Lessons from Anthropic's Archi](https://www.vincirufus.com/en/posts/building-multi-agent-research-systems/); [Building Effective AI Agents- Architecture Patterns and ...](https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf) | no |
| 44 | exa | 0 | 200 | 10 | [Your AI Code Reviewer Agrees With Everything. That Is the Bug. \| Jerem](https://www.jeremyknox.ai/blog/your-ai-code-reviewer-agrees-with-everything-that-is-the-bug/); [Fighting Sycophancy and Role Collapse: akiflow's Un-forked Reviewer \| ](https://akitao.com/en/k/giai-phap-chong-sycophancy-trong-multi-agent/); [When an Agent Reviews an Agent, the Praise Is Guaranteed](https://debugly.dev/agent-reviewing-agent-echo-chamber/); [Your AI Review Bot Reviewed a Diff the AI Itself Wrote. That's Not a R](https://www.powerduck.com/blog/ai-review-bot-reviewing-own-diff/); [Role Collapse and Self-Approval: Why One AI Agent Praises Its Own Code](https://akitao.com/en/k/tham-hoa-role-collapse-self-approval-ai-agent/) | no |
| 45 | exa | 0 | 200 | 10 | [Using Claude Code: Spending your effort / claude.dev Blog](https://claude.dev/blog/spending-your-effort/); [Claude Code effort level and model selection \| Claude \| Claude by Anth](https://claude.com/blog/claude-model-and-effort-level-in-claude-code); [Choosing the right effort level in Claude Code · Claude Academy](https://academy.claude.com/tutorials/choosing-the-right-effort-level-in-claude-code); [Effort - Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/effort); [Change the model, effort, and thinking settings - Claude Support](https://support.claude.com/en/articles/8664678-change-the-model-effort-and-thinking-settings) | no |
| 46 | exa | 0 | 200 | 10 | [Patterns and problems in emerging multiagent systems](https://www.anthropic.com/research/multiagent-systems); [Why Subagent Token Counts Are Wrong (and How to Fix Them) \| TokenJam](https://tokenjam.dev/blog/2026-07-04-subagent-token-counts-are-wrong); [Context vs. Tokens in Agentic Coding: Subagents vs. Forks \| TinyFish B](https://www.tinyfish.ai/blog/agentic-coding-context-vs-tokens-subagents); [Claude Code as an Orchestrator: Using Cheaper Models to Ship Real Proj](https://andresleiva.com/blog/claude-code-orchestrator-pattern/); [Why Claude Code Sub-Agents Cost 7x More Tokens (And When to Use Them) ](https://www.mindstudio.ai/blog/claude-code-subagents-cost-tokens) | no |
| 47 | exa | 0 | 200 | 10 | [Claude Code effort level and model selection \| Claude \| Claude by Anth](https://claude.com/blog/claude-model-and-effort-level-in-claude-code); [Choosing the right model](https://docs.claude.com/en/docs/about-claude/models/choosing-a-model); [Choosing the right effort level in Claude Code · Claude Academy](https://academy.claude.com/tutorials/choosing-the-right-effort-level-in-claude-code); [Change the model, effort, and thinking settings - Claude Support](https://support.claude.com/en/articles/8664678-change-the-model-effort-and-thinking-settings); [Effort - Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/effort) | no |
| 48 | exa | 0 | 200 | 10 | [Claude Code Subagents: Guide, Templates, and Generator](https://ai-coding-tools-guide.vercel.app/claude-code-subagents/); [Claude Code Agent Teams](https://www.maxresearchcollective.com/articles/claude-code-agent-teams.html); [Claude Code Subagents: Best Practices \| Kevin Welter](https://kevinwelter.com/en/blog/claude-code-subagents); [Claude Code Subagents: Visual Manager for Multi-Agent ...](https://agentsroom.dev/claude-code-subagents); [Claude Code Subagents, Skills & Coworks: Unlock Your AI Development Te](https://dev.to/akaranjkar08/claude-code-subagents-skills-coworks-unlock-your-ai-development-team-451k) | no |
| 49 | exa | 0 | 200 | 10 | [The Refutation Swarm: 842 Subagents That Default to Disbelieving Each ](https://withagents.dev/posts/post-42-the-refutation-swarm); [Verification and Finalization \| aiseclabs/codejury \| DeepWiki](https://deepwiki.com/aiseclabs/codejury/3.2.2-verification-and-finalization); [I Added More Verifiers to Catch Bad AI Findings. Precision Stopped Imp](https://dev.to/enjoy_kumawat/i-added-more-verifiers-to-catch-bad-ai-findings-precision-stopped-improving-26a5); [Less Verification Is Safer: Measuring the Cost-Quality Curve of Multi-](https://thakicloud.com/tech-blog/en/research/verify-gated-fanout-pareto/); [Staying Ahead of Adversarial AI Through Agentic Source ...](https://cloud.google.com/blog/topics/threat-intelligence/staying-ahead-of-adversarial-ai-through-agentic-source-code-review) | no |
| 50 | exa | 0 | 200 | 10 | [Reward Hacking in Coding Agents: How to Catch Deleted Tests](https://skylos.dev/blog/testwashing-coding-agents-delete-tests); [I tried to make Claude Code cheat on tests. Here's when it did. - DEV ](https://dev.to/mattbusel/i-tried-to-make-claude-code-cheat-on-tests-heres-when-it-did-2a0k); [Training a Misaligned Reward Seeker - Alignment Science Blog](https://alignment.anthropic.com/2026/reward-seeker/); [momomuchu/make-no-mistakes: Stop ...](https://github.com/momomuchu/make-no-mistakes); [Reward hacking in coding agents and the independent check \| FORGE Pers](https://www.btsavvy.com/insights/ai-agents-cheat-on-their-own-tests/) | no |
| 51 | exa | 0 | 200 | 10 | [Claude Code for C++ development: Modernize C++98 Codebases - AI for An](https://aiforanything.io/blog/claude-code-for-c-plus-plus-development-guide-2026); [C++ Coding Agent Guide: AI Pair Programming for Systems Development in](https://baeseokjae.github.io/posts/cpp-coding-agents-ai-systems-development/); [AddressSanitizer (ASan) - Claude Code skill](https://trailofbits.com/skills/address-sanitizer/); [Claude Code Review - Autonomous Terminal AI Agent](https://www.theaiselect.com/en/tools/claude-code); [Test-Driven Development with Claude Code \| Build This Now](https://www.buildthisnow.com/blog/guide/development/claude-code-tdd-testing) | no |
| 52 | exa | 0 | 200 | 10 | [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices); [Building verification loops in Claude Code with skills \| Claude by Ant](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills); [Demystifying evals for AI agents \ Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents); [Harness design for long-running application development \ Anthropic](https://www.anthropic.com/engineering/harness-design-long-running-apps?aid=rechn4YcJtAfIzqt6); [Agentic coding is straining CI. Here’s how we scaled test impact analy](https://claude.com/de/blog/agentic-coding-is-straining-ci-heres-how-we-scaled-test-impact-analysis-at-anthropic) | yes |
| 53 | exa | 0 | 200 | 10 | [Test-Driven Development (tdd) \| glebis/claude-skills \| DeepWiki](https://deepwiki.com/glebis/claude-skills/6.1-test-driven-development-(tdd)); [Beyond Spec-Driven Hype: Test-Driven Development with ...](https://builder.aws.com/content/3H4NiBKxuQWqrmV9I6JSvDAM44g/beyond-spec-driven-hype-test-driven-development-with-aws-kiro); [How to force red-green-refactor discipline on Claude Code with subagen](https://www.vibe-coding.academy/blog/how-to-force-red-green-refactor-discipline-on-claude-code-with-subagents-and-hoo/); [Test-Driven Development With Claude Code: How to Get Code That Actuall](https://www.claudecodeclub.ai/blog/claude-code-test-driven-development); [Expert Insights: Claude Code Playwright Mcp Github Actions 3 Test Laye](https://ariaatr.netlify.app/kenimo49/claude-code-playwright-mcp-github-actions-3-test-layers-that-actually-kill-regressions-34f6) | no |
| 54 | exa | 0 | 200 | 10 | [Benchmark subagent models the way you run them \| Jean Brito](https://jeanfbrito.github.io/posts/benchmark-subagents-the-way-you-run-them/); [Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5); [Opus 5.5 vs Sonnet 5: the pricier model wrote my code for about half t](https://antonshubin.com/blog/opus-5-5-vs-sonnet-5-agent-costs); [Best Model for Coding: What 1,232 Reviewed PRs Show \| Zest](https://meetzest.com/blog/best-model-for-coding); [AI subagents: delegating between models · Djtal Blog](https://djtal.ch/en/blog/2026-10-08-ai-subagents-model-delegation) | no |
| 55 | exa | 0 | 200 | 10 | [I audited the biggest Claude Code agent repos - Kaairos](https://kaairos.com/blog/best-claude-code-agent-repos-audit); [wshobson/agents: Claude Code Plugins, Scanned \| MrTechKing](https://www.mrtechking.com/wshobson-agents-github/); [160+ Free Claude Code Subagents: VoltAgent Setup (Tested)](https://quickpromptco.com/claude-code-subagents-voltagent/); [VoltAgent Subagent Directory: Choosing and Installing Claude Code Suba](https://prompt.luvai.net/en/prompts/voltagent-awesome-claude-code-subagents-pick-install); [Best Claude Code Subagents to Set Up (2026) \| MCSA Guru](https://mcsaguru.com/best-claude-code-subagents-2026) | no |
| 116 | context7 | 1 | n/a | n/a | none | no |
| 117 | context7 | 1 | n/a | n/a | none | no |
| 118 | firecrawl | 1 | 402 | n/a | none | no |
| 119 | context7 | 1 | n/a | n/a | none | no |
| 120 | serper | 0 | 200 | 10 | [Using Subagents to Improve Claude Code Results: A Step-By ...](https://software.rajivprab.com/2026/07/13/using-subagents-to-improve-claude-code/); [Best Claude Code Subagents and Custom Agent ...](https://promptessor.com/blog/best-claude-code-subagents-and-custom-agent-examples-for-specialized-coding-workflows-in-2026); [9 Parallel AI Agents That Review My Code (Claude ...](https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents); [Claude Code Sub Agents Tutorial - Build, Test & Release ...](https://www.youtube.com/watch?v=_lZshv08jMA); [Claude Code Subagents Are Not Smarter Skills](https://medium.com/@learn-simplified/claude-code-subagents-are-not-smarter-skills-they-are-isolated-workers-a68284a2d143) | no |
| 121 | serper | 0 | 200 | 10 | [Which Claude Model for AI Agents? Opus, Sonnet, Haiku](https://beam.ai/agentic-insights/which-claude-model-ai-agents); [[FEATURE] Update agents to use Sonnet 4.5 · Issue #71](https://github.com/wshobson/agents/issues/71); [Opus, Sonnet, Haiku: Stop Optimizing the Wrong Number](https://nitishagar.medium.com/opus-sonnet-haiku-stop-optimizing-the-wrong-number-f0e4732020b7); [what model do you actually use for subagents?](https://www.reddit.com/r/ClaudeCode/comments/1t7xetb/running_opus_as_main_model_what_model_do_you/); [Claude Haiku vs Sonnet vs Opus: Which One Should You ...](https://pub.towardsai.net/claude-haiku-vs-sonnet-vs-opus-which-one-should-you-actually-use-2026-3de2b2ba03c5) | no |
| 122 | serper | 0 | 200 | 10 | [Subagent-Driven Development - obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md); [subagent driven development could skip reviews for "easy ...](https://github.com/obra/superpowers/issues/1120); [Subagent driven development : r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/comments/1u9p2y8/subagent_driven_development/); [Subagent-Driven Development - All Agent Skills](https://agentskills.best/subagent-driven-development); [Superpowers Subagent Driven Development (Grade A)](https://www.skillsdirectory.com/skills/tekkiiiii-superpowers-subagent-driven-development) | no |
| 123 | serper | 0 | 200 | 10 | [Claude Code Agent Best Practices](https://github.com/KavasiMihaly/Claude-Code-Handbook/blob/main/claude-code-agent-best-practices.md); [Agent tool: add effort parameter for controlling subagent ...](https://github.com/anthropics/claude-code/issues/39220); [rphlmr/claude-config](https://github.com/rphlmr/claude-config); [field → per-role effort levels documented in agent prose but not ...](https://github.com/Yeachan-Heo/oh-my-claudecode/issues/2786); [pedrohcgs/claude-code-my-workflow: A ready-to-fork ...](https://github.com/pedrohcgs/claude-code-my-workflow) | no |
| 124 | serper | 0 | 200 | 10 | [Yeachan-Heo/oh-my-claudecode: Teams-first Multi-agent ...](https://github.com/yeachan-heo/oh-my-claudecode); [oh-my-claudecode - Ship 3× Faster with a Team of AI Agents](https://ohmyclaudecode.com/); [How to Build a Real Multi-Agent Engineering Workflow With ...](https://blog.devgenius.io/how-to-build-a-real-multi-agent-engineering-workflow-with-oh-my-claudecode-aa9d302b1552); [Claude Code as an Agent Orchestrator: My 3- ...](https://www.reddit.com/r/AI_Agents/comments/1r82abw/claude_code_as_an_agent_orchestrator_my_3agent/); [I Tested Oh My Claude Code The Only Agents Swarm ...](https://medium.com/@joe.njenga/i-tested-oh-my-claude-code-the-only-agents-swarm-orchestration-you-need-7338ad92c00f) | no |
| 125 | serper | 0 | 200 | 10 | [Use Fable 5 where it pays for itself](https://dev.to/toffy/use-fable-5-where-it-pays-for-itself-1809); [Claude Code Reviews with Fable - ISciNumPy.dev](https://iscinumpy.dev/post/claude-code-reviews/); [You know you can just ask fable to use Opus / Sonnet sub ...](https://www.reddit.com/r/ClaudeCode/comments/1uv9oma/you_know_you_can_just_ask_fable_to_use_opus/); [Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5); [Claude Fable 5.1 vs Opus 5: noticeable differences in ...](https://www.facebook.com/groups/claudeaicommunity/posts/1368363991997431/) | no |
| 126 | last30days | 0 | n/a | n/a | none | yes |
| 127 | last30days | 0 | n/a | 40 | [New mod tdd-guard: limit which paths each TDD subagent type may write](https://github.com/bankielewicz/mod-builder/issues/18); [Should AI Coding Agents Be Forced to Do TDD?](https://www.youtube.com/watch?v=RatafLAElo4); [docs: require plan → critique → verify workflow with subagent roles](https://github.com/Cyriellewu/evidenceoflife-v2/pull/86); [Add AGENTS.md, the desk run procedure, four skills and a guard hook](https://github.com/JesperDramsch/python-deadlines/pull/498); [[Bug] `[reasoning_extraction]` false positive kills both subagents of ](https://github.com/anthropics/claude-code/issues/97492) | no |
| 128 | last30days | 0 | n/a | 32 | [Claude Subagents vs Agent Teams: What’s the difference?](https://www.youtube.com/watch?v=jT1rg3TBf-I); [Every Claude Code Concept Explained for Normal People](https://www.youtube.com/watch?v=ZlDnsf_DOzg); [How to Build Claude Subagents Better Than 99% of People](https://www.youtube.com/watch?v=e18sdZLwP7o); [How To Use Claude Code Sub-Agents Better Than 99% of People](https://www.youtube.com/watch?v=6mG6tS6WG00); [Claude Code Subagents are Absolutely Insane](https://www.youtube.com/watch?v=sNI18nzwgn8) | yes |

### 2.2 webclaw fetches

Every fetch returned rc 0. Rows 41 (client-rendered index, 1.8 KB) and 215, 216 (Reddit login wall, 252 bytes) gave no usable body. Mirror paths are under `O/`.

| seq | Mirror file | Bytes | Used |
| --- | --- | --- | --- |
| 1 | `docs/claude-code/llms.txt.md` | 61893 | no |
| 2 | `docs/claude-code/common-workflows.md` | 15786 | no |
| 3 | `docs/claude-code/agents.md` | 8287 | yes |
| 4 | `docs/claude-code/model-config.md` | 116041 | yes |
| 5 | `docs/claude-code/best-practices.md` | 35819 | yes |
| 6 | `docs/claude-code/agent-teams.md` | 39742 | yes |
| 7 | `docs/claude-code/sub-agents.md` | 107732 | yes |
| 8 | `docs/claude-code/costs.md` | 42274 | yes |
| 9 | `docs/claude-code/workflows.md` | 41121 | yes |
| 10 | `docs/claude-code/fast-mode.md` | 20741 | no |
| 11 | `docs/claude-code/skills.md` | 102385 | no |
| 12 | `docs/claude-code/worktrees.md` | 39821 | no |
| 13 | `docs/claude-code/settings.md` | 41078 | no |
| 14 | `docs/claude-code/cli-reference.md` | 47505 | no |
| 15 | `docs/claude-code/plugins_components.md` | 44828 | no |
| 16 | `docs/claude-code/ultrareview.md` | 18036 | no |
| 17 | `docs/claude-code/plugins_manifest-reference.md` | 41866 | no |
| 18 | `docs/claude-code/goal.md` | 14876 | no |
| 19 | `docs/claude-code/code-review.md` | 32794 | yes |
| 20 | `docs/claude-code/features-overview.md` | 26926 | no |
| 21 | `docs/claude-code/how-claude-code-works.md` | 18977 | no |
| 22 | `docs/claude-code/prompt-caching.md` | 42630 | no |
| 23 | `docs/claude-code/context-window.md` | 15522 | no |
| 24 | `docs/claude-code/security-guidance.md` | 18175 | no |
| 25 | `docs/claude-code/agent-view.md` | 136111 | no |
| 26 | `docs/claude-code/large-codebases.md` | 34070 | no |
| 27 | `docs/claude-code/tools-reference.md` | 80585 | no |
| 28 | `docs/claude-code/whats-new_2026-w16.md` | 5992 | no |
| 29 | `docs/claude-code/commands.md` | 52768 | no |
| 30 | `docs/claude-code/whats-new_2026-w20.md` | 4281 | no |
| 31 | `docs/claude-code/agent-sdk_subagents.md` | 41034 | no |
| 32 | `docs/claude-code/whats-new_2026-w21.md` | 3464 | no |
| 33 | `docs/claude-code/whats-new_2026-w22.md` | 4330 | no |
| 34 | `docs/claude-code/whats-new_2026-w24.md` | 3997 | no |
| 35 | `docs/claude-code/whats-new_2026-w30.md` | 5103 | no |
| 36 | `docs/claude-code/whats-new_2026-w27.md` | 4697 | no |
| 37 | `docs/claude-code/whats-new_2026-w32.md` | 6348 | no |
| 38 | `docs/claude-code/whats-new_2026-w33.md` | 5488 | no |
| 39 | `docs/claude-code/whats-new_2026-w37.md` | 4651 | no |
| 40 | `docs/claude-code/whats-new_2026-w36.md` | 6525 | no |
| 41 | `docs/anthropic/engineering-index.md` | 1810 | yes |
| 56 | `docs/anthropic/harness-design-long-running-apps.md` | 39068 | yes |
| 57 | `docs/anthropic/effective-harnesses-for-long-running-agents.md` | 17189 | yes |
| 58 | `docs/anthropic/demystifying-evals-for-ai-agents.md` | 45832 | yes |
| 59 | `docs/anthropic/building-c-compiler.md` | 18647 | yes |
| 60 | `docs/anthropic/multi-agent-research-system.md` | 30428 | yes |
| 61 | `docs/anthropic/claude-code-best-practices.md` | 42560 | no |
| 62 | `docs/anthropic/research-property-based-testing.md` | 18402 | no |
| 63 | `docs/anthropic/research-multiagent-systems.md` | 32549 | no |
| 64 | `docs/anthropic/building-effective-agents.md` | 24160 | no |
| 65 | `docs/anthropic/effective-context-engineering.md` | 25812 | yes |
| 66 | `docs/anthropic/managed-agents.md` | 17247 | no |
| 67 | `docs/anthropic/claude-opus-5-5.md` | 42172 | yes |
| 68 | `docs/anthropic/blog-spending-your-effort.md` | 14790 | yes |
| 69 | `docs/anthropic/alignment-reward-seeker.md` | 10964 | no |
| 70 | `docs/anthropic/blog-model-and-effort-level.md` | 21711 | yes |
| 71 | `docs/anthropic/blog-maximizing-value-sessions.md` | 21018 | no |
| 72 | `docs/anthropic/blog-test-impact-analysis.md` | 15744 | no |
| 73 | `docs/anthropic/blog-verification-loops-skills.md` | 16604 | no |
| 74 | `docs/anthropic/academy-effort-level.md` | 12315 | no |
| 75 | `docs/platform/prompting-claude-opus-5-5.md` | 30389 | no |
| 76 | `docs/platform/effort.md` | 27624 | yes |
| 77 | `docs/platform/choosing-a-model.md` | 9567 | no |
| 78 | `docs/platform/pricing.md` | 37082 | yes |
| 79 | `docs/platform/models-overview.md` | 9725 | yes |
| 80 | `docs/claude-code/advisor.md` | 17146 | no |
| 81 | `docs/claude-code/cross-session-messaging.md` | 34161 | no |
| 82 | `docs/claude-code/hooks.md` | 261938 | no |
| 83 | `docs/claude-code/env-vars.md` | 170607 | no |
| 84 | `docs/practitioners/powerduck-review-own-diff.md` | 5664 | no |
| 85 | `docs/practitioners/debugly-echo-chamber.md` | 8219 | yes |
| 86 | `docs/practitioners/skylos-testwashing.md` | 20614 | yes |
| 87 | `docs/practitioners/claudelab-fork-default-review-agent.md` | 22775 | yes |
| 88 | `docs/practitioners/jeremyknox-reviewer-agrees.md` | 13093 | yes |
| 89 | `docs/practitioners/agenticlab-rubber-stamp-verifier.md` | 14418 | yes |
| 90 | `docs/practitioners/penloom-pass-any-test.md` | 10040 | yes |
| 91 | `docs/practitioners/mattbusel-cheat-on-tests.md` | 49945 | yes |
| 92 | `docs/practitioners/mattbusel-made-it-impossible.md` | 4973 | yes |
| 93 | `docs/practitioners/haoli-tobe10.md` | 59878 | no |
| 94 | `docs/practitioners/btsavvy-reward-hacking.md` | 13150 | no |
| 95 | `docs/practitioners/vibecoding-red-green-subagents.md` | 8525 | no |
| 96 | `docs/practitioners/aicoding-failing-test-first.md` | 8981 | no |
| 97 | `docs/practitioners/agentbuild-tests-miss-bug.md` | 15044 | no |
| 98 | `docs/practitioners/jeanfbrito-benchmark-subagents.md` | 13569 | yes |
| 99 | `docs/practitioners/antonshubin-opus55-vs-sonnet5.md` | 19893 | yes |
| 100 | `docs/practitioners/meetzest-best-model-1232-prs.md` | 17670 | no |
| 101 | `docs/practitioners/djtal-model-delegation.md` | 17655 | no |
| 102 | `docs/practitioners/tokenjam-subagent-tokens.md` | 17211 | no |
| 103 | `docs/practitioners/mindstudio-7x-tokens.md` | 17020 | no |
| 104 | `docs/practitioners/aidiveyt-haiku55-routing.md` | 9562 | yes |
| 105 | `docs/practitioners/tinyfish-context-vs-tokens.md` | 16002 | no |
| 106 | `docs/practitioners/withagents-refutation-swarm.md` | 17027 | no |
| 107 | `docs/practitioners/kumawat-more-verifiers.md` | 6946 | no |
| 108 | `docs/practitioners/kaairos-agent-repos-audit.md` | 11718 | no |
| 109 | `docs/practitioners/alphaxiv-2608.18167-adversarial-review.md` | 22428 | no |
| 110 | `docs/practitioners/thakicloud-verify-gated-fanout.md` | 13323 | no |
| 111 | `docs/practitioners/claudecodeclub-effort-levels.md` | 21369 | no |
| 112 | `docs/practitioners/backgrind-effort-levels.md` | 19384 | no |
| 113 | `docs/practitioners/usagecut-when-subagents.md` | 19443 | no |
| 114 | `docs/practitioners/maxresearch-agent-teams.md` | 11059 | no |
| 115 | `docs/practitioners/akitao-unforked-reviewer.md` | 7763 | no |
| 215 | `docs/practitioners/reddit-orchestrator-doers-reviewer-blind-tester.md` | 252 | no |
| 216 | `docs/practitioners/reddit-orchestrator-doers-reviewer-blind-tester-old.md` | 252 | no |

## 3. GitHub issues, PRs and discussions searched (stage 2)

### 3.1 R12 rows (unchanged)

Rows 153 to 177 and 193 to 200 have no query text and no seed; R12 did not save them, and R12b does not reconstruct them. Their results stay in R12's scratch files.

| seq | Provider | Query | Hits | Top results | Seeded by | Used |
| --- | --- | --- | --- | --- | --- | --- |
| 141 | gh-issue-view | anthropics/claude-code#97492 | 1 | none | 127 | no |
| 142 | gh-issue-view | Yeachan-Heo/oh-my-claudecode#2786 | 1 | none | 123 | yes |
| 143 | gh-issue-view | anthropics/claude-code#39220 | 1 | none | 123 | yes |
| 144 | gh-issue-view | anthropics/claude-code#30703 | 1 | none | 123 | yes |
| 145 | gh-issue-view | obra/superpowers#1120 | 1 | none | 122 | yes |
| 146 | gh-issue-view | obra/superpowers#2333 | 1 | none | 127 | no |
| 147 | gh-issue-view | wshobson/agents#71 | 1 | none | 121 | no |
| 148 | gh-issue-view | shakacode/agent-workflows#154 | 1 | none | 123 | no |
| 149 | gh-issue-view | bankielewicz/mod-builder#18 | 1 | none | 127 | yes |
| 150 | gh-issue-view | lexfrei/ccc#67 | 1 | none | 128 | yes |
| 151 | gh-issue-view | AventurasTeam/Aventuras#566 | 1 | none | 128 | no |
| 152 | gh-issue-view | Cyriellewu/evidenceoflife-v2#86 | 1 | none | 127 | no |
| 153 | gh-issue-search | not recorded | 2 | [[BUG] Top-level `effortLevel` in user settings is ignored on Opus 5.5;](https://github.com/anthropics/claude-code/issues/97403); [Feature: configurable reasoning effort level for subagents](https://github.com/anthropics/claude-code/issues/43083) | not recorded | no |
| 154 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 155 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 156 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 157 | gh-issue-search | not recorded | 1 | [[BUG] opusplan mode overrides subagent model frontmatter, ignoring age](https://github.com/anthropics/claude-code/issues/93157) | not recorded | no |
| 158 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 159 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 160 | gh-issue-search | not recorded | 1 | [[Bug] Agent tool effort parameter dropped for named in-process teammat](https://github.com/anthropics/claude-code/issues/100701) | not recorded | yes |
| 161 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 162 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 163 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 164 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 165 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 166 | gh-issue-search | not recorded | 4 | [feat: add kubestellar-console-ops subagent to Infrastructure](https://github.com/VoltAgent/awesome-claude-code-subagents/pull/241); [How were these written](https://github.com/VoltAgent/awesome-claude-code-subagents/issues/19); [Add interactive install script for agents](https://github.com/VoltAgent/awesome-claude-code-subagents/pull/39) | not recorded | no |
| 167 | gh-issue-search | not recorded | 15 | [[Feature Request] Add subagent-scoped effort control (CLAUDE_CODE_SUBA](https://github.com/anthropics/claude-code/issues/79135); [[Bug] Subagent effort level silently capped when extended thinking dis](https://github.com/anthropics/claude-code/issues/92002); [[FEATURE] Subagents inherit session effort; per-model modelSettings ef](https://github.com/anthropics/claude-code/issues/92660) | not recorded | yes |
| 168 | gh-issue-search | not recorded | 2 | [Background daemon sessions fail permanently on transient socket errors](https://github.com/anthropics/claude-code/issues/68789); [[BUG] Daemon supervisor shuts down for auto-upgrade but never restarts](https://github.com/anthropics/claude-code/issues/73670) | not recorded | no |
| 169 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 170 | gh-issue-search | not recorded | 0 | none | not recorded | no |
| 171 | gh-issue-search | not recorded | 15 | [[Bug] /agents command removed: can no longer create, edit, or delete a](https://github.com/anthropics/claude-code/issues/100477); [[BUG] SubagentHandback from a teammate-spawned subagent reports "spawn](https://github.com/anthropics/claude-code/issues/99651); [[BUG] Server-side experiment flag injects "Do not call the AgentTool u](https://github.com/anthropics/claude-code/issues/82371) | not recorded | no |
| 172 | gh-issue-search | not recorded | 15 | [[Bug] Built-in plugin startup tip references unavailable plugin](https://github.com/anthropics/claude-code/issues/99071); [Subagent files are not hot-reloaded mid-session despite docs (v2.1.202](https://github.com/anthropics/claude-code/issues/75432); [Orphaned Bash-tool subprocesses (tsc/vitest) outlive a terminated sess](https://github.com/anthropics/claude-code/issues/93996) | not recorded | yes |
| 173 | gh-issue-search | not recorded | 15 | [fix(skills): account for Claude Fable in model selection and testing g](https://github.com/obra/superpowers/pull/1719); [Require an explicit model on subagent dispatches outside SDD (from #21](https://github.com/obra/superpowers/pull/2400); [Subagent dispatches outside SDD have no model guidance, so they inheri](https://github.com/obra/superpowers/issues/2034) | not recorded | no |
| 174 | gh-issue-search | not recorded | 5 | [feat: TDD subagent reports should include RED evidence (failing test o](https://github.com/obra/superpowers/issues/994); [writing-plans doesn't enforce TDD, causing entire Subagent-Driven Deve](https://github.com/obra/superpowers/issues/1576); [GitHub Copilot (VS Code) integration](https://github.com/obra/superpowers/issues/764) | not recorded | no |
| 175 | gh-issue-search | not recorded | 15 | [SDD: Approve + Important triggers mandatory re-review loop](https://github.com/obra/superpowers/issues/2273); [subagent driven development could skip reviews for "easy" tasks. ](https://github.com/obra/superpowers/issues/1120); [Prompt audit against Claude Fable 5.1: pressure language and update su](https://github.com/obra/superpowers/issues/2454) | not recorded | no |
| 176 | gh-issue-search | not recorded | 15 | [Parallel Architect/Critic reviews for Claude agents (Fixes #4355)](https://github.com/Yeachan-Heo/oh-my-claudecode/pull/4358); [plan --consensus: allow parallel Architect/Critic reviews when both ru](https://github.com/Yeachan-Heo/oh-my-claudecode/issues/4355); [chore(release): bump version to v5.7.3](https://github.com/Yeachan-Heo/oh-my-claudecode/pull/4366) | not recorded | no |
| 177 | gh-issue-search | not recorded | 15 | [fix(garden): ignore model tier and named variants in agent divergence](https://github.com/wshobson/agents/pull/724); [fix: preserve skill references and distinguish agent variants](https://github.com/wshobson/agents/pull/720); [docs: sync counts after operating-kit merge](https://github.com/wshobson/agents/pull/613) | not recorded | no |
| 178 | gh-issue-view | anthropics/claude-code#100701 | 1 | none | 160 | yes |
| 179 | gh-issue-view | anthropics/claude-code#75432 | 1 | none | 172 | yes |
| 180 | gh-issue-view | anthropics/claude-code#92660 | 1 | none | 167 | yes |
| 181 | gh-issue-view | anthropics/claude-code#85416 | 1 | none | 167 | yes |
| 182 | gh-issue-view | anthropics/claude-code#92002 | 1 | none | 167 | yes |
| 183 | gh-issue-view | anthropics/claude-code#100477 | 1 | none | 171 | no |
| 184 | gh-issue-view | anthropics/claude-code#79135 | 1 | none | 167 | yes |
| 185 | gh-issue-view | anthropics/claude-code#43952 | 1 | none | 171 | no |
| 186 | gh-issue-view | obra/superpowers#1747 | 1 | none | 173 | yes |
| 187 | gh-issue-view | obra/superpowers#2096 | 1 | none | 173 | no |
| 188 | gh-issue-view | obra/superpowers#994 | 1 | none | 174 | yes |
| 189 | gh-issue-view | obra/superpowers#1719 | 1 | none | 173 | no |
| 190 | gh-issue-view | obra/superpowers#2446 | 1 | none | 173 | no |
| 191 | gh-issue-view | Yeachan-Heo/oh-my-claudecode#4206 | 1 | none | 176 | yes |
| 192 | gh-issue-view | Yeachan-Heo/oh-my-claudecode#4355 | 1 | none | 176 | no |
| 193 | gh-graphql-discussion | not recorded | 0 | none | not recorded | no |
| 194 | gh-graphql-discussion | not recorded | 0 | none | not recorded | no |
| 195 | gh-graphql-discussion | not recorded | 0 | none | not recorded | no |
| 196 | gh-graphql-discussion | not recorded | 0 | none | not recorded | no |
| 197 | gh-graphql-discussion | not recorded | 0 | none | not recorded | no |
| 198 | gh-graphql-discussion | not recorded | 1 | [Ralplan with Codex](https://github.com/Yeachan-Heo/oh-my-claudecode/discussions/2842) | not recorded | no |
| 199 | gh-graphql-discussion | not recorded | 10 | [subagent-tuner: decide the model and effort of a subagent at dispatch ](https://github.com/wshobson/agents/discussions/763); [Founding inventory spot for your 112-agent library - Harness Arena inv](https://github.com/wshobson/agents/discussions/454); [51% of commands silently fail to register (missing YAML frontmatter)](https://github.com/wshobson/agents/discussions/487) | not recorded | no |
| 200 | gh-graphql-discussion | not recorded | 4 | [How does apra-fleet relate to superpowers? Should I install both?](https://github.com/Apra-Labs/apra-fleet/discussions/500); [Welcome to DeepSeek Harness Community - Please Read Before Posting](https://github.com/deepseek-ai/deepseek-harness/discussions/1797); [Evolving specs](https://github.com/github/spec-kit/discussions/152) | not recorded | no |

### 3.2 R12b rows

Each search is `gh search issues|prs <terms> [--repo R] [--include-prs] --limit 20 --json ...`; hits are results returned, capped at 20. Discussion hits are GraphQL `discussionCount`. `via` names the R12b search that surfaced a viewed thread.

| seq | Provider | Query | Repo or flags | Hits | Status | Top results | Seeded by | Via | Used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 225 | gh-issue-search | subagent hot reload | anthropics/claude-code (phrase) | 0 | EMPTY_UNVERIFIED | none | 7 |  | no |
| 226 | gh-issue-search | agents directory restart new agent not found | anthropics/claude-code (phrase) | 0 | EMPTY_UNVERIFIED | none | 7 |  | no |
| 227 | gh-issue-search | agent definition changes not applied until restart | anthropics/claude-code (phrase) | 0 | EMPTY_UNVERIFIED | none | 7 |  | no |
| 228 | gh-graphql-discussion | claude code custom subagent reload without restart | global | 24 | OK | [Hot-swapping clio MCP updates without ending a Claude Code session](https://github.com/Advance-Technologies-Foundation/clio/discussions/1643); [explain deeply the Git Integration](https://github.com/limboo-ai/limboo/discussions/115); [Workspace instructions (AGENTS.md) from parent/shared repo are never i](https://github.com/deepseek-ai/deepseek-harness/discussions/519) | 7 |  | no |
| 229 | gh-issue-search | effort frontmatter agent | anthropics/claude-code (phrase) | 0 | EMPTY_UNVERIFIED | none | 123 |  | no |
| 230 | gh-issue-search | xhigh effort subagent | anthropics/claude-code (phrase) | 0 | EMPTY_UNVERIFIED | none | 45 |  | no |
| 231 | gh-issue-search | effortLevel subagent inherit | anthropics/claude-code (phrase) | 0 | EMPTY_UNVERIFIED | none | 47 |  | no |
| 232 | gh-graphql-discussion | subagent effort level per agent | global | 139 | OK | [Agent Teams: Per-teammate model selection](https://github.com/deepseek-ai/deepseek-harness/discussions/8324); [Reasoning Effort “Default” is actually “off” for MiMo / Kimi models](https://github.com/deepseek-ai/deepseek-harness/discussions/9704); [How to reliably clamp thinking level / effort for tasks?](https://github.com/can1357/oh-my-pi/discussions/13390) | 45 |  | no |
| 233 | gh-issue-search | CLAUDE_CODE_SUBAGENT_MODEL | anthropics/claude-code | 20 | OK | [[BUG] CLAUDE_CODE_SUBAGENT_MODEL Inheritance Issue](https://github.com/anthropics/claude-code/issues/92715); [Workflow agent() model silently replaced by CLAUDE_CODE_SUBAGENT_MODEL](https://github.com/anthropics/claude-code/issues/89972); [CLAUDE_CODE_SUBAGENT_MODEL acts as hard override - ignores agent front](https://github.com/anthropics/claude-code/issues/91160) | 54 |  | yes |
| 234 | gh-issue-search | subagent hot reload | anthropics/claude-code | 20 | OK | [Subagent files are not hot-reloaded mid-session despite docs (v2.1.202](https://github.com/anthropics/claude-code/issues/75432); [Subagent definitions added mid-session are not spawnable for minutes (](https://github.com/anthropics/claude-code/issues/98528); [[BUG] Nested subagent (depth-2) completion notifications route to root](https://github.com/anthropics/claude-code/issues/90256) | 7 |  | yes |
| 235 | gh-issue-search | agents directory restart new agent not found | anthropics/claude-code | 20 | OK | [Custom agents under ~/.claude/agents/ intermittently fail to register ](https://github.com/anthropics/claude-code/issues/98685); [Subagent definitions added mid-session are not spawnable for minutes (](https://github.com/anthropics/claude-code/issues/98528); [Workflow (multi-agent) resume restarts from the beginning after auto-c](https://github.com/anthropics/claude-code/issues/65796) | 7 |  | yes |
| 236 | gh-issue-search | agent definition changes not applied until restart | anthropics/claude-code | 20 | OK | [Task-list tools (TaskCreate/TaskUpdate/TaskList/TaskGet) no longer exp](https://github.com/anthropics/claude-code/issues/80015); [Post/PreToolUse Hooks Not Executing in Claude Code](https://github.com/anthropics/claude-code/issues/6305); [[BUG] Cowork (Windows): all Plan9 shares fail with "Plan9 mount failed](https://github.com/anthropics/claude-code/issues/92984) | 7 |  | no |
| 237 | gh-issue-search | effort frontmatter agent | anthropics/claude-code | 20 | OK | [[Bug] Agent-team teammates ignore effort frontmatter from subagent def](https://github.com/anthropics/claude-code/issues/80569); [[BUG] Agent frontmatter `effort` is still ignored on the `--agent` ses](https://github.com/anthropics/claude-code/issues/97829); [[FEATURE] Subagents inherit session effort; per-model modelSettings ef](https://github.com/anthropics/claude-code/issues/92660) | 123 |  | yes |
| 238 | gh-issue-search | xhigh effort subagent | anthropics/claude-code | 20 | OK | [[FEATURE] Subagents inherit session effort; per-model modelSettings ef](https://github.com/anthropics/claude-code/issues/92660); [[FEATURE] Let me choose the reasoning effort when ultracode is on, and](https://github.com/anthropics/claude-code/issues/97442); [[FEATURE] Per-call `effort` parameter on the Agent tool](https://github.com/anthropics/claude-code/issues/98391) | 45 |  | yes |
| 239 | gh-issue-search | effortLevel subagent inherit | anthropics/claude-code | 20 | OK | [[FEATURE] Subagents inherit session effort; per-model modelSettings ef](https://github.com/anthropics/claude-code/issues/92660); [docs: subagent frontmatter `effort` field is implemented but undocumen](https://github.com/anthropics/claude-code/issues/91415); [[Feature Request] Add subagent-scoped effort control (CLAUDE_CODE_SUBA](https://github.com/anthropics/claude-code/issues/79135) | 47 |  | no |
| 240 | gh-issue-search | haiku 5.5 subagent | anthropics/claude-code | 20 | OK | [Custom subagent frontmatter model (haiku/sonnet) ignored - 1,149 of 1,](https://github.com/anthropics/claude-code/issues/100082); [[BUG] Every subagent is told "Do NOT Write report/summary/findings/ana](https://github.com/anthropics/claude-code/issues/101519); [[BUG] Subagent transcripts record streaming-start usage: output_tokens](https://github.com/anthropics/claude-code/issues/100154) | 54 |  | yes |
| 241 | gh-issue-search | subagent model ignored frontmatter | anthropics/claude-code | 20 | OK | [Custom subagent frontmatter model (haiku/sonnet) ignored - 1,149 of 1,](https://github.com/anthropics/claude-code/issues/100082); [[BUG] Subagent frontmatter `model: claude-opus-4-8` silently ignored -](https://github.com/anthropics/claude-code/issues/91890); [Plugin subagents: `model:` frontmatter in a plugin's agents/*.md is ig](https://github.com/anthropics/claude-code/issues/89723) | 125 |  | yes |
| 242 | gh-issue-search | fallback Opus 4.8 cybersecurity | anthropics/claude-code | 20 | OK | [[Bug][cyber] Inspecting dynamic instrumentation tooling for local mobi](https://github.com/anthropics/claude-code/issues/101415); [[Bug][cyber] False positive on flight controller takeoff altitude debu](https://github.com/anthropics/claude-code/issues/101405); [[Bug][cyber] Recovering or resetting local development Android device ](https://github.com/anthropics/claude-code/issues/101416) | 4 |  | no |
| 243 | gh-issue-search | fork subagent review | anthropics/claude-code | 20 | OK | [[Bug] code-review skill (context: fork) result lost when invoked from ](https://github.com/anthropics/claude-code/issues/100615); [/code-review fork is finalized while its named finder agents still run](https://github.com/anthropics/claude-code/issues/93702); [Forked skill execution double-orchestrates: agent notifications route ](https://github.com/anthropics/claude-code/issues/91073) | 44 |  | yes |
| 244 | gh-issue-search | CLAUDE_CODE_FORK_SUBAGENT | anthropics/claude-code | 20 | OK | [[BUG]  Claude Code 2.1.252: run_in_background=false is ignored when th](https://github.com/anthropics/claude-code/issues/91225); [Feature request: a supported way to disable the agent_summary spinner ](https://github.com/anthropics/claude-code/issues/86879); [[CRITICAL] Subagent spawning and subagent pattern bugs trigger infinit](https://github.com/anthropics/claude-code/issues/68619) | 87 |  | no |
| 245 | gh-issue-search | sycophancy code reviewer agent | +PRs | 20 | OK | [feat(rules): add Grouch anti-sycophancy code review rule](https://github.com/PatrickJS/awesome-cursorrules/pull/402); [Add PASB to Safety, Alignment and Theory](https://github.com/lobehub/awesome-rsi/pull/69); [[review] adversarial reviewer option (forced disagreement)](https://github.com/mikeroySoft/factory/issues/35) | 44 |  | no |
| 246 | gh-graphql-discussion | rubber stamp reviewer agent LLM | global | 18 | OK | [循环工程：为什么你的 AI Agent 循环会"刷分"，以及怎么让它真正收敛](https://github.com/Q00/ouroboros/discussions/1979); [🛰️ Agent Fleet HQ v2 - coordination room (all agents introduce yoursel](https://github.com/orgs/elizaOS/discussions/18309); [🧠 Demerzel Ideation - 2026-09-04](https://github.com/orgs/GuitarAlchemist/discussions/1046) | 44 |  | no |
| 247 | gh-issue-search | agent teams teammate model | anthropics/claude-code | 20 | OK | [[Bug] Agent teams enabled but Agent tool has no `name` parameter, so t](https://github.com/anthropics/claude-code/issues/100613); [[Bug] Agent tool effort parameter dropped for named in-process teammat](https://github.com/anthropics/claude-code/issues/100701); [[BUG] Agent teams: task with unresolved 'Blocked by' can be claimed; T](https://github.com/anthropics/claude-code/issues/101029) | 48 |  | yes |
| 248 | gh-pr-search | pin teammate model effort | global | 20 | OK | [fix(become): pin teammate model and effort to agent defaults](https://github.com/lexfrei/ccc/pull/67); [Pick a coding agent's effort per model, see when a choice was skipped,](https://github.com/lemma-work/lemma-platform/pull/973); [fix(droid): type /compress and declare in-place compaction honestly](https://github.com/rimio-ai/rimz/pull/980) | 128 |  | yes |
| 249 | gh-issue-search | orchestrator subagent model | anthropics/claude-code | 20 | OK | [[FEATURE] Subagents inherit session effort; per-model modelSettings ef](https://github.com/anthropics/claude-code/issues/92660); [Desktop app (Code tab): background subagent stalls silently, never not](https://github.com/anthropics/claude-code/issues/98846); [[FEATURE] Workflows: a deterministic shell/command step (no agent need](https://github.com/anthropics/claude-code/issues/98566) | 43 |  | no |
| 250 | gh-issue-search | subagent token usage cost | anthropics/claude-code | 20 | OK | [[BUG] Subagent transcripts missing final assistant entry (stop_reason ](https://github.com/anthropics/claude-code/issues/100830); [Background subagents have no token, turn or time cap: three research a](https://github.com/anthropics/claude-code/issues/94013); [[FEATURE] Add 5-minute and 1-hour cache-write token counts to the OTel](https://github.com/anthropics/claude-code/issues/100113) | 46 |  | yes |
| 251 | gh-issue-view | ryoppippi/ccusage#950 | ryoppippi/ccusage | 1 | OK | [Bug: Massive token overcounting for Codex subagent sessions (91x infla](https://github.com/ccusage/ccusage/issues/950) | 102 |  | no |
| 252 | gh-issue-search | verifier | aiseclabs/codejury +PRs | 0 | EMPTY_UNVERIFIED | none | 49 |  | no |
| 253 | gh-issue-search | review | chpomob/adversarial-code-review +PRs | 0 | EMPTY_UNVERIFIED | none | 49 |  | no |
| 254 | gh-issue-search | 2608.18167 | +PRs | 20 | OK | [Add three-way critic closing line (keep finding labels)](https://github.com/Da7-Tech/SureForge/pull/1); [Add an evidence-typed critic between the panel and the fix round (arXi](https://github.com/topij/agentic-dev-kit/issues/613); [build_product: adopt adversarial-review (typed verdicts + deterministi](https://github.com/2389-research/tracker/issues/624) | 49 |  | no |
| 255 | gh-graphql-discussion | adversarial review refute findings agent | global | 42 | OK | [Rolling progress: bug + clipping sweep - audit, adversarial verify, fi](https://github.com/Ding-Ding-Projects/BambuStudio/discussions/23); [Implementation and integration run retrospectives](https://github.com/uberblick-ai/uberblick-2/discussions/522); [Architecture & code-quality review - develop@ade6416 (2026-08-18)](https://github.com/MediaNoxLabs/oxid/discussions/37) | 49 |  | no |
| 256 | gh-issue-search | verification subagent refute | anthropics/claude-code | 20 | OK | [[BUG] Opus 5 orchestration: the conclusion is re-anchored to the most ](https://github.com/anthropics/claude-code/issues/81786); [[BUG] workflow subagents receive a substituted tool input, making ever](https://github.com/anthropics/claude-code/issues/82821); [[BUG] A compaction summary can refer to its own <analysis> block, whic](https://github.com/anthropics/claude-code/issues/97284) | 52 |  | yes |
| 257 | gh-issue-search | evaluator | anthropics/cwc-long-running-agents +PRs | 2 | OK | [PreToolUse hooks silently ignored on current Claude Code: deprecated d](https://github.com/anthropics/cwc-long-running-agents/issues/2); [/goal vs custom harness](https://github.com/anthropics/cwc-long-running-agents/pull/1) | 42 |  | no |
| 258 | gh-graphql-discussion | planner generator evaluator agent harness | global | 107 | OK | [Proposal: task-conditioned Harness evolution with evaluable Plugin Pac](https://github.com/deepseek-ai/deepseek-harness/discussions/2454); [Skill Quality Report - 2026-10-14](https://github.com/github/awesome-copilot/discussions/5069); [Skill Quality Report - 2026-10-13](https://github.com/github/awesome-copilot/discussions/5045) | 42 |  | no |
| 259 | gh-issue-search | test | momomuchu/make-no-mistakes +PRs | 1 | OK | [Standards-completeness campaign: convert PARTIAL→MET toward the ~90% c](https://github.com/momomuchu/make-no-mistakes/issues/1) | 50 |  | no |
| 260 | gh-issue-search | deletes tests | anthropics/claude-code | 20 | OK | [[MODEL] Deleted and overwrote its own test fixture, then composed a te](https://github.com/anthropics/claude-code/issues/101924); [[BUG] Claude Desktop: first-party Filesystem extension unusable - all ](https://github.com/anthropics/claude-code/issues/94351); [Critical: Claude ignored explicit 'no upload' instruction and purged G](https://github.com/anthropics/claude-code/issues/97084) | 50 |  | yes |
| 261 | gh-issue-search | testwashing | +PRs | 0 | EMPTY_UNVERIFIED | none | 50 |  | no |
| 262 | gh-issue-search | tamperproof | Mattbusel/tamperproof +PRs | 0 | EMPTY_UNVERIFIED | none | 91 |  | no |
| 263 | gh-issue-search | test | hahahahahahahahah6/edit-guard +PRs | 0 | EMPTY_UNVERIFIED | none | 93 |  | no |
| 264 | gh-issue-search | tdd | glebis/claude-skills +PRs | 1 | OK | [Featured in Awesome Claude Code Workflows](https://github.com/glebis/claude-skills/issues/14) | 53 |  | no |
| 265 | gh-issue-search | tdd-guard | +PRs | 20 | OK | [New mod tdd-guard: limit which paths each TDD subagent type may write](https://github.com/bankielewicz/mod-builder/issues/18); [chore: untrack tdd-guard hook scratch files](https://github.com/kolezka/raqzpl/pull/20); [TDD ledger guard cannot identify Scenario Outline headings](https://github.com/ArcadeAI/safeword/issues/4416) | 53 |  | yes |
| 266 | gh-issue-search | tdd subagent | bankielewicz/mod-builder +PRs | 2 | OK | [New mod tdd-guard: limit which paths each TDD subagent type may write](https://github.com/bankielewicz/mod-builder/issues/18); [issue-forge: an agent kept editing and running commands after `/issue-](https://github.com/bankielewicz/mod-builder/issues/40) | 127 |  | no |
| 267 | gh-graphql-discussion | test writer subagent implementer | global | 134 | OK | [Implementation and integration run retrospectives](https://github.com/uberblick-ai/uberblick-2/discussions/522); [Issue preparation run retrospectives](https://github.com/uberblick-ai/uberblick-2/discussions/506); [v4 revised full design: conversation, knowledge, context, and LanceDB](https://github.com/Soul-Brews-Studio/arra-oracle-v4/discussions/36) | 53 |  | no |
| 268 | gh-issue-search | test | vanzan01/claude-code-sub-agent-collective +PRs | 19 | OK | [Current Version](https://github.com/vanzan01/claude-code-sub-agent-collective/issues/14); [Should we manually install context7 and taskmaster MCP server before l](https://github.com/vanzan01/claude-code-sub-agent-collective/issues/17); [Suggestion to add TDD Filter on source files or some way to bypass tdd](https://github.com/vanzan01/claude-code-sub-agent-collective/issues/16) | 120 |  | no |
| 269 | gh-issue-search | test-writer subagent | +PRs | 20 | OK | [Add the test-writer subagent](https://github.com/TomHaken/lamateam/issues/27); [#27 Add the test-writer subagent](https://github.com/TomHaken/lamateam/pull/28); [Add controller tests and a RestTestClient test-writer subagent](https://github.com/PierreSQS/bharath-ecommerce-api/pull/7) | 120 |  | no |
| 270 | gh-issue-search | cpp-pro | +PRs | 20 | OK | [cpp_qt_sorting_visualizer.pro](https://github.com/Daravadee-189/Desktop-Sudoku/issues/1); [PS5 Pro: vulkan_env.txt and opt-in ggml-vulkan mat-vec switches](https://github.com/blackbearreloaded/ProsperoAI/pull/29); [Pro-rate CPP in its start year](https://github.com/lumberbarons/retirement/issues/58) | 51 |  | no |
| 271 | gh-issue-search | test | anthropics/claudes-c-compiler +PRs | 20 | OK | [Tests are missing from repo](https://github.com/anthropics/claudes-c-compiler/issues/247); [`cargo test --release` fails](https://github.com/anthropics/claudes-c-compiler/issues/16); [integration tests appear to be missing](https://github.com/anthropics/claudes-c-compiler/issues/3) | 59 |  | no |
| 272 | gh-issue-search | model | VoltAgent/awesome-claude-code-subagents +PRs | 20 | OK | [Convert subagent collection for ZCode](https://github.com/VoltAgent/awesome-claude-code-subagents/pull/326); [fix: switch 25 subagents from model: opus to model: inherit](https://github.com/VoltAgent/awesome-claude-code-subagents/pull/280); [Ground meta-orchestration subagents, remove fabricated metrics (#300)](https://github.com/VoltAgent/awesome-claude-code-subagents/pull/308) | 55 |  | yes |
| 273 | gh-issue-search | fable | wshobson/agents +PRs | 10 | OK | [fix: preserve skill references and distinguish agent variants](https://github.com/wshobson/agents/pull/720); [docs: refresh model references for Claude Sonnet 5 and Fable 5](https://github.com/wshobson/agents/pull/612); [perf: consolidate duplicated code and optimize adapter infrastructure](https://github.com/wshobson/agents/pull/642) | 121 |  | no |
| 274 | gh-pr-search | model | wshobson/agents | 20 | OK | [fix: preserve skill references and distinguish agent variants](https://github.com/wshobson/agents/pull/720); [fix(garden): ignore model tier and named variants in agent divergence](https://github.com/wshobson/agents/pull/724); [deps(plugin-eval): bump the python-minor-and-patch group across 1 dire](https://github.com/wshobson/agents/pull/759) | 121 |  | no |
| 275 | gh-issue-search | model selection reviewer | obra/superpowers +PRs | 20 | OK | [Final whole-branch review: code-reviewer.md re-derives the diff and ha](https://github.com/obra/superpowers/issues/2446); [Subagent dispatches outside SDD have no model guidance, so they inheri](https://github.com/obra/superpowers/issues/2034); [Require an explicit model on subagent dispatches outside SDD (from #21](https://github.com/obra/superpowers/pull/2400) | 122 |  | yes |
| 276 | gh-pr-search | reviewer model | obra/superpowers | 20 | OK | [Require an explicit model on subagent dispatches outside SDD (from #21](https://github.com/obra/superpowers/pull/2400); [writing-plans, task-reviewer: name the colliding input behind string-s](https://github.com/obra/superpowers/pull/2414); [fix(sdd): an Approved verdict closes the task; severity and Assessment](https://github.com/obra/superpowers/pull/2326) | 122 |  | yes |
| 277 | gh-graphql-discussion | repo:obra/superpowers subagent model | global | 0 | EMPTY_UNVERIFIED, FEATURE_DISABLED | none | 122 |  | no |
| 278 | gh-issue-view | SinishaDjukic/worca-cc#343 | SinishaDjukic/worca-cc | 1 | OK | [Pipeline fails at first agent dispatch: Claude Code >=2.1.190 rejects ](https://github.com/SinishaDjukic/worca-cc/issues/343) | 123 |  | no |
| 279 | gh-issue-search | effort routing | shakacode/agent-workflows +PRs | 20 | OK | [Evaluate advisory model/effort routing with observed execution provena](https://github.com/shakacode/agent-workflows/issues/151); [Default routine PR-batch coordinators below Sol/xhigh and require meas](https://github.com/shakacode/agent-workflows/issues/400); [Bound upgrade rollback snapshots to managed paths](https://github.com/shakacode/agent-workflows/pull/839) | 123 |  | yes |
| 280 | gh-issue-search | critic effort | Yeachan-Heo/oh-my-claudecode +PRs | 17 | OK | [feat(team): per-role reasoningEffort in team.roleRouting (currently ac](https://github.com/Yeachan-Heo/oh-my-claudecode/issues/4206); [feat(team): per-role reasoningEffort in roleRouting (#4206)](https://github.com/Yeachan-Heo/oh-my-claudecode/pull/4207); [fix(team): make task claims and monitor snapshots consistent](https://github.com/Yeachan-Heo/oh-my-claudecode/pull/4009) | 124 |  | yes |
| 281 | gh-graphql-discussion | repo:Yeachan-Heo/oh-my-claudecode model effort | global | 1 | OK | [Should we add Gemini / Codex Mcp support for some agents in 4.0.0?](https://github.com/Yeachan-Heo/oh-my-claudecode/discussions/375) | 124 |  | no |
| 282 | gh-issue-search | reviewer | jeanfbrito/agentic-workflow-framework +PRs | 0 | EMPTY_UNVERIFIED | none | 98 |  | no |
| 283 | gh-issue-search | reviewer | mikekelly/promode +PRs | 2 | OK | [v3.0.0: agent-roster restructure (pre-baked model+effort configs) + br](https://github.com/mikekelly/promode/pull/4); [Integrate compound-engineering as required dependency](https://github.com/mikekelly/promode/pull/1) | 125 |  | yes |
| 284 | gh-issue-search | effort | anthropics/claude-plugins-official +PRs | 20 | OK | [Prompt audit findings against Claude Fable 5.1 / Opus 5.5: pinned mode](https://github.com/anthropics/claude-plugins-official/issues/6352); [security-guidance: PostToolUse[Bash] spawns 5 Python processes per Bas](https://github.com/anthropics/claude-plugins-official/issues/5558); [frontend-design: name the default typefaces; drop the plan-then-gate s](https://github.com/anthropics/claude-plugins-official/issues/6299) | 24 |  | yes |
| 285 | gh-issue-view | Consiliency/agent-harness#924 | Consiliency/agent-harness | 1 | OK | [advisor-board: host×seat routing rule - every harness fills its OWN ve](https://github.com/Consiliency/agent-harness/issues/924) | 127 |  | no |
| 286 | gh-issue-view | mgalic01/adaptive-market-engine#89 | mgalic01/adaptive-market-engine | 1 | OK | [Proposal: three protocol amendments (reviewer unavailability, findings](https://github.com/mgalic01/adaptive-market-engine/pull/89) | 127 |  | no |
| 287 | gh-issue-search | parallel review subagents | anthropics/claude-code | 20 | OK | [Parallel subagents consume 642k tokens, then session ends mid-edit wit](https://github.com/anthropics/claude-code/issues/99125); [[Bug] `[reasoning_extraction]` false positive kills both subagents of ](https://github.com/anthropics/claude-code/issues/97492); [[MODEL] Claude leans towards git worktrees despite includeGitInstructi](https://github.com/anthropics/claude-code/issues/97916) | 127 |  | yes |
| 288 | gh-issue-view | anthropics/claude-code#100082 | anthropics/claude-code | 1 | OK | [Custom subagent frontmatter model (haiku/sonnet) ignored - 1,149 of 1,](https://github.com/anthropics/claude-code/issues/100082) | 54 | 240 | yes |
| 289 | gh-issue-view | anthropics/claude-code#82252 | anthropics/claude-code | 1 | OK | [Subagent model override 'claude-fable-5'/'fable' silently served by cl](https://github.com/anthropics/claude-code/issues/82252) | 52 | 256 | yes |
| 290 | gh-issue-view | anthropics/claude-code#91890 | anthropics/claude-code | 1 | OK | [[BUG] Subagent frontmatter `model: claude-opus-4-8` silently ignored -](https://github.com/anthropics/claude-code/issues/91890) | 125 | 241 | yes |
| 291 | gh-issue-view | anthropics/claude-code#83920 | anthropics/claude-code | 1 | OK | [[Bug] Agent tool model parameter ignored; subagents inherit session/se](https://github.com/anthropics/claude-code/issues/83920) | 125 | 241 | yes |
| 292 | gh-issue-view | anthropics/claude-code#87815 | anthropics/claude-code | 1 | OK | [[BUG] Parallel subagent fleets silently inherit session model tier - b](https://github.com/anthropics/claude-code/issues/87815) | 125 | 241 | yes |
| 293 | gh-issue-view | anthropics/claude-code#83795 | anthropics/claude-code | 1 | OK | [[SECURITY/ARCHITECTURE] Model pinning via settings.json is silently ov](https://github.com/anthropics/claude-code/issues/83795) | 52 | 256 | no |
| 294 | gh-issue-view | anthropics/claude-code#85592 | anthropics/claude-code | 1 | OK | [CLAUDE_CODE_SUBAGENT_MODEL silently discards explicit per-call subagen](https://github.com/anthropics/claude-code/issues/85592) | 54 | 233 | yes |
| 295 | gh-issue-view | anthropics/claude-code#78460 | anthropics/claude-code | 1 | OK | [Subagents are capped at 8000 output tokens while the main loop is not ](https://github.com/anthropics/claude-code/issues/78460) | 45 | 238 | yes |
| 296 | gh-issue-view | anthropics/claude-code#98391 | anthropics/claude-code | 1 | OK | [[FEATURE] Per-call `effort` parameter on the Agent tool](https://github.com/anthropics/claude-code/issues/98391) | 123 | 237 | yes |
| 297 | gh-issue-view | anthropics/claude-code#100347 | anthropics/claude-code | 1 | OK | [[DOCS] Sub-agents page omits the Agent tool's per-invocation effort pa](https://github.com/anthropics/claude-code/issues/100347) | 123 | 237 | yes |
| 298 | gh-issue-view | anthropics/claude-code#95823 | anthropics/claude-code | 1 | OK | [Subagent model and reasoning effort are invisible to every consumer - ](https://github.com/anthropics/claude-code/issues/95823) | 123 | 237 | yes |
| 299 | gh-issue-view | anthropics/claude-code#100154 | anthropics/claude-code | 1 | OK | [[BUG] Subagent transcripts record streaming-start usage: output_tokens](https://github.com/anthropics/claude-code/issues/100154) | 46 | 250 | yes |
| 300 | gh-issue-view | anthropics/claude-code#100830 | anthropics/claude-code | 1 | OK | [[BUG] Subagent transcripts missing final assistant entry (stop_reason ](https://github.com/anthropics/claude-code/issues/100830) | 46 | 250 | yes |
| 301 | gh-issue-view | anthropics/claude-code#99360 | anthropics/claude-code | 1 | OK | [Subagents use the 5-minute prompt cache while the main session uses 1-](https://github.com/anthropics/claude-code/issues/99360) | 46 | 250 | yes |
| 302 | gh-issue-view | anthropics/claude-code#98528 | anthropics/claude-code | 1 | OK | [Subagent definitions added mid-session are not spawnable for minutes (](https://github.com/anthropics/claude-code/issues/98528) | 7 | 234 | yes |
| 303 | gh-issue-view | anthropics/claude-code#98685 | anthropics/claude-code | 1 | OK | [Custom agents under ~/.claude/agents/ intermittently fail to register ](https://github.com/anthropics/claude-code/issues/98685) | 7 | 235 | yes |
| 304 | gh-issue-view | anthropics/claude-code#81781 | anthropics/claude-code | 1 | OK | [Claude Code silently excludes a subset of valid custom agents from the](https://github.com/anthropics/claude-code/issues/81781) | 7 | 241 | no |
| 305 | gh-issue-view | anthropics/claude-code#88886 | anthropics/claude-code | 1 | OK | [Subagents receive a CLAUDE.md/memory snapshot from parent session star](https://github.com/anthropics/claude-code/issues/88886) | 7 | 234 | yes |
| 306 | gh-issue-view | anthropics/claude-code#95165 | anthropics/claude-code | 1 | OK | [/code-review in the desktop app runs inline in the authoring session (](https://github.com/anthropics/claude-code/issues/95165) | 44 | 243 | yes |
| 307 | gh-issue-view | anthropics/claude-code#81852 | anthropics/claude-code | 1 | OK | [`tools:` allowlist is enforced for subagents but silently dropped for ](https://github.com/anthropics/claude-code/issues/81852) | 48 | 247 | yes |
| 308 | gh-issue-view | anthropics/claude-code#89971 | anthropics/claude-code | 1 | OK | [[Bug] Fork subagent ignores explicit task boundary and executes unauth](https://github.com/anthropics/claude-code/issues/89971) | 44 | 243 | yes |
| 309 | gh-issue-view | anthropics/claude-code#100401 | anthropics/claude-code | 1 | OK | [[BUG] code-review plugin skips its review agents on Claude Code 2.1.28](https://github.com/anthropics/claude-code/issues/100401) | 127 | 287 | yes |
| 310 | gh-issue-view | anthropics/claude-code#75757 | anthropics/claude-code | 1 | OK | [[Bug] Subagents billed after monthly spend limit exceeded; false clean](https://github.com/anthropics/claude-code/issues/75757) | 127 | 287 | yes |
| 311 | gh-issue-view | anthropics/claude-code#101924 | anthropics/claude-code | 1 | OK | [[MODEL] Deleted and overwrote its own test fixture, then composed a te](https://github.com/anthropics/claude-code/issues/101924) | 50 | 260 | yes |
| 312 | gh-issue-view | obra/superpowers#2400 | obra/superpowers | 1 | OK | [Require an explicit model on subagent dispatches outside SDD (from #21](https://github.com/obra/superpowers/pull/2400) | 122 | 275 | yes |
| 313 | gh-issue-view | obra/superpowers#1631 | obra/superpowers | 1 | OK | [subagent-driven-development: Model Selection guidance is not enforced ](https://github.com/obra/superpowers/issues/1631) | 122 | 275 | yes |
| 314 | gh-issue-view | obra/superpowers#2326 | obra/superpowers | 1 | OK | [fix(sdd): an Approved verdict closes the task; severity and Assessment](https://github.com/obra/superpowers/pull/2326) | 122 | 276 | yes |
| 315 | gh-issue-view | Yeachan-Heo/oh-my-claudecode#1240 | Yeachan-Heo/oh-my-claudecode | 1 | OK | [Research: Structured gap analysis is the active ingredient for thoroug](https://github.com/Yeachan-Heo/oh-my-claudecode/issues/1240) | 124 | 280 | yes |
| 316 | gh-issue-view | VoltAgent/awesome-claude-code-subagents#280 | VoltAgent/awesome-claude-code-subagents | 1 | OK | [fix: switch 25 subagents from model: opus to model: inherit](https://github.com/VoltAgent/awesome-claude-code-subagents/pull/280) | 55 | 272 | yes |
| 317 | gh-issue-view | anthropics/claude-plugins-official#6352 | anthropics/claude-plugins-official | 1 | OK | [Prompt audit findings against Claude Fable 5.1 / Opus 5.5: pinned mode](https://github.com/anthropics/claude-plugins-official/issues/6352) | 24 | 284 | yes |
| 318 | gh-issue-view | shakacode/agent-workflows#151 | shakacode/agent-workflows | 1 | OK | [Evaluate advisory model/effort routing with observed execution provena](https://github.com/shakacode/agent-workflows/issues/151) | 123 | 279 | yes |
| 319 | gh-issue-view | mikekelly/promode#4 | mikekelly/promode | 1 | OK | [v3.0.0: agent-roster restructure (pre-baked model+effort configs) + br](https://github.com/mikekelly/promode/pull/4) | 125 | 283 | yes |
| 320 | gh-issue-view | monoes/monomind#657 | monoes/monomind | 1 | OK | [fix: pin coder model/effort, report served models, dedupe hooks, cap d](https://github.com/monoes/monomind/pull/657) | 128 | 248 | yes |
| 321 | gh-issue-view | BaseInfinity/claude-sdlc-harness#730 | BaseInfinity/claude-sdlc-harness | 1 | OK | [Mutation-test every regression guard: effort-per-model, TDD hook, exha](https://github.com/BaseInfinity/claude-sdlc-harness/issues/730) | 53 | 265 | yes |
| 334 | gh-issue-view | anthropics/claude-code#77655 | anthropics/claude-code | 1 | OK | [[BUG] Subagent view renders the main session's model/effort/agent iden](https://github.com/anthropics/claude-code/issues/77655) | 54 | 233 | yes |
| 335 | gh-issue-view | anthropics/claude-code#97588 | anthropics/claude-code | 1 | OK | [[BUG] VS Code extension: subagents are shown running with the main ses](https://github.com/anthropics/claude-code/issues/97588) | 54 | 233 | yes |
| 336 | gh-issue-view | anthropics/claude-code#80569 | anthropics/claude-code | 1 | OK | [[Bug] Agent-team teammates ignore effort frontmatter from subagent def](https://github.com/anthropics/claude-code/issues/80569) | 123 | 237 | yes |
| 337 | gh-issue-view | anthropics/claude-code#100613 | anthropics/claude-code | 1 | OK | [[Bug] Agent teams enabled but Agent tool has no `name` parameter, so t](https://github.com/anthropics/claude-code/issues/100613) | 48 | 247 | yes |

### 3.3 D142 preflight (GitHub)

D142 reached the brief while R12b ran, so these checks ran after the searches (seq 225 to 287). Every repository searched has issues enabled and none is archived; discussions are enabled only on wshobson/agents and Yeachan-Heo/oh-my-claudecode.

| seq | Check | rc | Result | Status |
| --- | --- | --- | --- | --- |
| 338 | `gh api rate_limit` | 0 | core 4811/5000, search 30/30, code_search 10/10, graphql 5000/5000 | OK, NONE |
| 339 | `gh api repos/anthropics/claude-code` | 0 | issues True, discussions False, archived False | OK, NONE |
| 340 | `gh api repos/aiseclabs/codejury` | 0 | issues True, discussions False, archived False | OK, NONE |
| 341 | `gh api repos/chpomob/adversarial-code-review` | 0 | issues True, discussions False, archived False | OK, NONE |
| 342 | `gh api repos/anthropics/cwc-long-running-agents` | 0 | issues True, discussions False, archived False | OK, NONE |
| 343 | `gh api repos/momomuchu/make-no-mistakes` | 0 | issues True, discussions False, archived False | OK, NONE |
| 344 | `gh api repos/Mattbusel/tamperproof` | 0 | issues True, discussions False, archived False | OK, NONE |
| 345 | `gh api repos/hahahahahahahahah6/edit-guard` | 0 | issues True, discussions False, archived False | OK, NONE |
| 346 | `gh api repos/glebis/claude-skills` | 0 | issues True, discussions False, archived False | OK, NONE |
| 347 | `gh api repos/bankielewicz/mod-builder` | 0 | issues True, discussions False, archived False | OK, NONE |
| 348 | `gh api repos/vanzan01/claude-code-sub-agent-collective` | 0 | issues True, discussions False, archived False | OK, NONE |
| 349 | `gh api repos/anthropics/claudes-c-compiler` | 0 | issues True, discussions False, archived False | OK, NONE |
| 350 | `gh api repos/VoltAgent/awesome-claude-code-subagents` | 0 | issues True, discussions False, archived False | OK, NONE |
| 351 | `gh api repos/wshobson/agents` | 0 | issues True, discussions True, archived False | OK, NONE |
| 352 | `gh api repos/obra/superpowers` | 0 | issues True, discussions False, archived False | OK, NONE |
| 353 | `gh api repos/shakacode/agent-workflows` | 0 | issues True, discussions False, archived False | OK, NONE |
| 354 | `gh api repos/Yeachan-Heo/oh-my-claudecode` | 0 | issues True, discussions True, archived False | OK, NONE |
| 355 | `gh api repos/jeanfbrito/agentic-workflow-framework` | 0 | issues True, discussions False, archived False | OK, NONE |
| 356 | `gh api repos/mikekelly/promode` | 0 | issues True, discussions False, archived False | OK, NONE |
| 357 | `gh api repos/anthropics/claude-plugins-official` | 0 | issues True, discussions False, archived False | OK, NONE |

## 4. Saved searches run (reproduced read-only with their controls)

### 4.1 R12 rows (unchanged; query text not recorded, mapping from file ids)

| seq | File id | rc | HTTP | total_count | Used |
| --- | --- | --- | --- | --- | --- |
| 201 | ctrl-codex-schema.p1.json | 0 | n/a | 884 | no |
| 202 | ctrl-readme-cc.p1.json | 0 | n/a | 42 | no |
| 203 | p-official-effort.p1.json | 0 | n/a | 0 | no |
| 204 | ctrl-readme-official.p1.json | 0 | n/a | 61 | yes |
| 205 | p-superpowers-modelsel.p1.json | 0 | n/a | 13 | yes |
| 206 | ctrl-readme-superpowers.p1.json | 0 | n/a | 30 | yes |
| 207 | p-wshobson-fable.p1.json | 0 | n/a | 6 | yes |
| 208 | ctrl-readme-wshobson.p1.json | 0 | n/a | 75 | yes |
| 209 | p-omc-effort.p1.json | 0 | n/a | 0 | yes |
| 210 | ctrl-readme-omc.p1.json | 0 | n/a | 138 | no |
| 211 | p-cc-isolation.p1.json | 1 | 403 | None | no |
| 212 | p-official-effort-xhigh.p1.json | 1 | 403 | None | no |
| 213 | p-official-security-agents.p1.json | 1 | 403 | None | no |
| 214 | p-superpowers-modelsel-p2.p1.json | 1 | 403 | None | no |
| 217 | p-official-security-effort.p1.json | 0 | n/a | 6 | yes |
| 218 | p-voltagent-effort.p1.json | 0 | n/a | 8 | yes |
| 219 | ctrl-readme-voltagent.p1.json | 0 | n/a | 17 | yes |
| 220 | p-official-effort-agents.json | 0 | n/a | 0 | yes |
| 221 | p-official-effort-agents-p2.json | 0 | n/a | 0 | no |
| 222 | p-cc-agents-effort.json | 0 | n/a | 0 | no |
| 223 | p-superpowers-modelsel-p2.json | 0 | n/a | 13 | yes |
| 224 | p-wshobson-fable-p2.json | 0 | n/a | 6 | yes |

### 4.2 R12b reproduction of the four D138 rows, and two proposed rows

Shape: `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=<n>`, the request `dev/collect_saved_search.py:179-182` makes. Control: `README repo:<repo>`, expected_min 1.

| seq | Saved row | Role | Query sent | Page | rc | HTTP | total_count | Returned | Status | Seeded by | Used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 322 | official-agent-effort-xhigh | query | `xhigh path:plugins/claude-security/agents repo:anthropics/claude-plugins-official` | 1 | 0 | 200 | 6 | 5 | OK | 24 | yes |
| 323 | official-agent-effort-xhigh | query | `xhigh path:plugins/claude-security/agents repo:anthropics/claude-plugins-official` | 2 | 0 | 200 | 6 | 1 | OK | 24 | yes |
| 324 | official-agent-effort-xhigh | control (expected_min 1) | `README repo:anthropics/claude-plugins-official` | 1 | 0 | 200 | 61 | 5 | OK | 24 | yes |
| 325 | superpowers-model-selection | query | `"Model Selection" repo:obra/superpowers` | 1 | 0 | 200 | 13 | 5 | OK | 122 | yes |
| 326 | superpowers-model-selection | query | `"Model Selection" repo:obra/superpowers` | 2 | 0 | 200 | 13 | 5 | OK | 122 | yes |
| 327 | superpowers-model-selection | control (expected_min 1) | `README repo:obra/superpowers` | 1 | 0 | 200 | 30 | 5 | OK | 122 | yes |
| 328 | wshobson-fable-tier | query | `"model: fable" repo:wshobson/agents` | 1 | 0 | 200 | 6 | 5 | OK | 121 | yes |
| 329 | wshobson-fable-tier | query | `"model: fable" repo:wshobson/agents` | 2 | 0 | 200 | 6 | 1 | OK | 121 | yes |
| 330 | wshobson-fable-tier | control (expected_min 1) | `README repo:wshobson/agents` | 1 | 0 | 200 | 75 | 5 | OK | 121 | yes |
| 331 | voltagent-effort | query | `effort repo:VoltAgent/awesome-claude-code-subagents` | 1 | 0 | 200 | 8 | 5 | OK | 55 | yes |
| 332 | voltagent-effort | query | `effort repo:VoltAgent/awesome-claude-code-subagents` | 2 | 0 | 200 | 8 | 3 | OK | 55 | yes |
| 333 | voltagent-effort | control (expected_min 1) | `README repo:VoltAgent/awesome-claude-code-subagents` | 1 | 0 | 200 | 17 | 5 | OK | 55 | yes |
| 358 | proposed: superpowers-dispatch-effort | query | `"effort:" path:skills/subagent-driven-development repo:obra/superpowers` | 1 | 0 | 200 | 0 | 0 | EMPTY_VERIFIED | 122 | yes |
| 359 | proposed: superpowers-dispatch-effort | control (expected_min 1) | `README repo:obra/superpowers` | 1 | 0 | 200 | 30 | 5 | OK | 122 | yes |
| 360 | proposed: monomind-served-model-receipt | query | `unexpected_models repo:monoes/monomind` | 1 | 0 | 200 | 4 | 4 | OK | 128 | yes |
| 361 | proposed: monomind-served-model-receipt | control (expected_min 1) | `README repo:monoes/monomind` | 1 | 0 | 200 | 270 | 5 | OK | 128 | yes |

### 4.3 Proposed new rows

`dev/saved-searches.toml` already holds R12's four rows (D138) and was not edited. Two more
were reproduced with their controls above (seq 358 to 361):

```toml
[[search]]
id = "superpowers-dispatch-effort"
query = "\"effort:\" path:skills/subagent-driven-development"
repo = "obra/superpowers"                     # 0 today (control README 30; the bb92a77 clone agrees); a watch row that flips when SDD adds effort to dispatch (#1747, #2400)
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "monomind-served-model-receipt"
query = "unexpected_models"
repo = "monoes/monomind"                      # 4 hits (doc/agent-exec-protocol.md, agent-exec.ts, a test); control README 270
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

Issue-search rows worth having once the collector can call `/search/issues` (it calls only
`/search/code`, `dev/collect_saved_search.py:179`): `CLAUDE_CODE_SUBAGENT_MODEL
repo:anthropics/claude-code` (seq 233), `subagent model ignored frontmatter
repo:anthropics/claude-code` (seq 241) and `subagent hot reload repo:anthropics/claude-code`
(seq 234), as keywords, not phrases (see gap 3).

## 5. Seed-to-search map (stage-1 row to stage-2 calls)

| Stage-1 seq | Provider | Stage-1 query or URL | R12 stage-2 rows | R12b stage-2 rows |
| --- | --- | --- | --- | --- |
| 4 | webclaw | https://code.claude.com/docs/en/model-config.md | none | 242 |
| 7 | webclaw | https://code.claude.com/docs/en/sub-agents.md | none | 225, 226, 227, 228, 234, 235, 236, 302, 303, 304, 305 |
| 24 | webclaw | https://code.claude.com/docs/en/security-guidance.md | none | 284, 317, 322, 323, 324 |
| 42 | exa | Anthropic engineering harness design long-running agents planner generator evaluator | 138 | 257, 258 |
| 43 | exa | Anthropic engineering how we built our multi-agent research system orchestrator subagents | none | 249 |
| 44 | exa | AI code reviewer agent rubber stamps approves everything sycophancy LGTM subagent | none | 243, 245, 246, 306, 308 |
| 45 | exa | Spending your effort Claude Code blog effort levels | none | 230, 232, 238, 295 |
| 46 | exa | Claude Code subagents context bloat orchestrator token cost multi-agent too many agents | none | 250, 299, 300, 301 |
| 47 | exa | Choosing a Claude model and effort level in Claude Code | none | 231, 239 |
| 48 | exa | Claude Code subagent team roles architect implementer reviewer QA model per role | none | 247, 307, 337 |
| 49 | exa | adversarial verification agent refute findings multi-agent code review false positives | none | 252, 253, 254, 255 |
| 50 | exa | coding agent modifies or deletes tests to make them pass reward hacking Claude Code | none | 259, 260, 261, 311 |
| 51 | exa | C++ test-driven development with Claude Code agents clang compile errors | none | 270 |
| 52 | exa | Anthropic engineering blog Claude Code agentic coding test-driven development verification | none | 256, 289, 293 |
| 53 | exa | Claude Code subagents separate test writer agent and implementer agent TDD | none | 264, 265, 267, 321 |
| 54 | exa | Fable 5.1 Opus 5.5 Sonnet 5.5 Haiku 5.5 which model for subagents code review cost | none | 233, 240, 288, 294, 334, 335 |
| 55 | exa | best Claude Code subagent collections wshobson agents VoltAgent superpowers oh-my-claudeco | 131 | 272, 316, 331, 332, 333 |
| 59 | webclaw | https://www.anthropic.com/engineering/building-c-compiler | none | 271 |
| 87 | webclaw | https://claudelab.net/en/articles/claude-code/claude-code-fork-default-review-agent-named- | none | 244 |
| 91 | webclaw | https://dev.to/mattbusel/i-tried-to-make-claude-code-cheat-on-tests-heres-when-it-did-2a0k | none | 262 |
| 93 | webclaw | https://dev.to/haoli/my-agent-changed-tobe10-to-tobe9-and-called-it-done-i-built-hooks-to- | none | 263 |
| 98 | webclaw | https://jeanfbrito.github.io/posts/benchmark-subagents-the-way-you-run-them/ | none | 282 |
| 102 | webclaw | https://tokenjam.dev/blog/2026-07-04-subagent-token-counts-are-wrong | none | 251 |
| 120 | serper | Claude Code subagent test-writer separate from implementer agent weakens tests | none | 268, 269 |
| 121 | serper | wshobson agents model tier haiku sonnet opus inherit | 147 | 273, 274, 328, 329, 330 |
| 122 | serper | "subagent-driven-development" superpowers spec reviewer code quality reviewer | 129, 145 | 275, 276, 277, 312, 313, 314, 325, 326, 327, 358, 359 |
| 123 | serper | site:github.com claude code agents implementer reviewer test-author model effort frontmatt | 132, 142, 143, 144, 148 | 229, 237, 278, 279, 296, 297, 298, 318, 336 |
| 124 | serper | oh-my-claudecode agents critic planner executor model | none | 280, 281, 315 |
| 125 | serper | Claude Code reviewer subagent rubber stamp independent review model Fable Opus | none | 241, 283, 290, 291, 292, 319 |
| 127 | last30days | claude code tdd test author and critic agents | 140, 141, 146, 149, 152 | 266, 285, 286, 287, 309, 310 |
| 128 | last30days | claude code subagent roles and models | 150, 151 | 248, 320, 360, 361 |
| 160 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 178 | none |
| 167 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 180, 181, 182, 184 | none |
| 171 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 183, 185 | none |
| 172 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 179 | none |
| 173 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 186, 187, 189, 190 | none |
| 174 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 188 | none |
| 176 | gh-issue-search (a stage-2 row; R12 recorded it as the seed) | query not recorded | 191, 192 | none |

Stage-2 rows in the log: 211; with a recorded seed: 149 (R12 32 of 94; R12b 117 of 117). Rows without a seed are R12's: 130, 133, 134, 135, 136, 137, 139, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 217, 218, 219, 220, 221, 222, 223, 224.

### 5.1 Stage-1 rows that named something and got no R12b search

- 57 (anthropics/claude-quickstarts), 58 (sierra-research/tau2-bench), 62 (mmaaz-git/agentic-pbt
  and five upstream PRs), 64 (anthropics/anthropic-quickstarts), 68 (harbor-framework/terminal-bench),
  90 (raindrop-ai/workshop), 100 (Winding-Labs/zest-*), 108 (hesreallyhim/awesome-claude-code),
  113 (NeoZi12/usagecut-cli): none bears on roles, models, effort, reviewer independence,
  test-first agents or hot reload, so no search was chosen.
- 92 names the same repository as 91 (Mattbusel/tamperproof), searched once under 91.
- 126 is the Markdown output of the same Last30Days plan as 128; its items were seeded under 128.
- 41, 215 and 216 returned no usable body (R12 section 7). The remaining webclaw rows are
  Anthropic and Claude Code pages that name no repository, issue or PR beyond the product terms
  already searched under 4, 7 and 24.

## Open gaps

1. **R12's own rows stay short of D137 and D142.** Left unchanged as instructed: 62 of R12's 94
   stage-2 rows have no seed; 33 have no query text (153 to 177, 193 to 200) and 22 saved-search
   rows only a file id (201 to 224); views 178 to 192 name a stage-2 search as their seed; no R12
   row has `status` or `failure_code`; the Firecrawl call (118) and one Context7 call (119) have
   no query text. R12b did not rerun stage 1, so the Context7 quota and Firecrawl HTTP 402 gaps
   stand, untested since R12.
2. **D142 arrived mid-run.** The brief gained D142 while R12b ran. The GitHub preflight (seq 338
   to 357) therefore ran after the searches. It found discussions disabled on
   anthropics/claude-code and obra/superpowers, so R12's zero-hit discussion queries on those
   repositories (four, per R12 section 7) and R12b's seq 277 are `FEATURE_DISABLED`, not evidence
   of absence. No stage-1 provider preflight was run, because R12b called no stage-1 provider.
3. **Six phrase searches.** `gh search issues "<several words>"` sends one quoted phrase. Seq 225
   to 227 and 229 to 231 matched only exact phrases, returned 0 and are marked `match: phrase`;
   each was rerun as keywords (234 to 239). The log keeps both.
4. **Unverified zeros.** Twelve searches returned 0 with no control (status
   `EMPTY_UNVERIFIED`): 225 to 227, 229 to 231, 252, 253, 261 to 263, 282. Each repository has
   issues enabled (preflight), but a zero there is not proof of absence.
5. **Search depth.** Issue and PR searches return at most 20 results in GitHub's best-match
   order; only those were read. Global discussion searches (228, 232, 246, 255, 258, 267) were
   noisy and none was used.
6. **Whether this host still misroutes models is unknown.** CC#100082's misrouting stopped on
   2026-10-07 with no changelog entry, and this host runs 2.1.299. Measure it on the first
   dispatches with the transcript check from the verdict; do not assume either way.
7. **No reliable per-role output-cost source.** Subagent transcripts under-count output (D1);
   no replacement source was verified in this run.
8. **`opus` alias and the 1M window.** VoltAgent/awesome-claude-code-subagents#280 (merged
   2026-06-24) says the `opus` alias resolved to standard Opus, not `opus[1m]`, with a separate
   allowance, in the Opus 4.8 era. Whether that holds for Opus 5.5, and so for the 1,000,000-token
   window in `model-policy.md`, is UNVERIFIED.
9. **Agent teams path not tested.** B1 to B3 matter only with teams enabled; MP does not enable
   them, and this run could not test either path without starting a session.
