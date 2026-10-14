# R12: SDLC subagent roles, with model and effort per role (Q97, Q98)

Research R12, session ccm-20261014, 2026-10-14. Read-only apart from this report and the offline
mirror. Brief: `scratchpad/reprio2/research-brief.md` (routes D100, mirror rule D110).

Abbreviations: MP = the repository root; P = `MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`;
O = `MP/offline/research/R12-sdlc-agent-roles/`, the mirror (`O/manifest.json` lists 199 items:
104 pages, 27 GitHub threads, 12 clones and 56 local captures, each with a SHA-256 or commit);
CC = `O/docs/claude-code/`; A = `O/docs/anthropic/`; PR = `O/docs/practitioners/`; GH =
`O/docs/github/issues/`; R = `O/repos/`. Line numbers refer to the mirrored copies. This host runs
Claude Code 2.1.299.

## 1. Verdict

Keep the six roles MP already defines. Add three roles as briefs on the existing definitions, and
add mechanical guards instead of new agent files. This set needs no new file under
`MP/.claude/agents`, so it needs no restart.

| Role | Model | Effort | Separate agent or brief | Reason | Citation |
| --- | --- | --- | --- | --- | --- |
| parent (orchestrator, adjudicator, merger) | session model (Opus 5.5) | session (user `modelSettings` holds xhigh today) | the main session | Holds lane records, adjudicates findings and merges one lane at a time. It is the largest single cost line in measured runs, so it delegates instead of reading. | `MP/docs/agents/claude-team.md` Roles; R/superpowers `docs/superpowers/specs/2026-06-10-strict-cost-sdd-design.md:13-20` |
| architect (contract and fork judgement) | Fable 5.1 | high | brief: a read-only dispatch from the parent | Ambiguous design calls are where Fable's extra investigation pays off. It runs once per ticket wave. | CC/model-config.md:81-84; `O/docs/platform/models-overview.md:19`; `MP/.claude/skills/ticket-frontier/references/model-policy.md:16` |
| test author (red: contract tests at the ticket's seam) | Opus 5.5 | xhigh | separate instance; brief on `implementer.md` | The tests become the locked contract. At higher effort Opus 5.5 reproduced the bug first, wrote randomized tests against a reference and checked that its tests failed on half-finished fixes. | CC/best-practices.md:478; A/blog-spending-your-effort.md:140, 176-182; A/building-c-compiler.md:90 |
| test-contract check (only when the tests are new, not direct ports) | Fable 5.1 | medium | separate instance; brief on `reviewer.md` | Agrees on what done means before code exists. A locked bad test is expensive; reviewing one commit is cheap. | A/harness-design-long-running-apps.md:107; R/wshobson-agents `plugins/tdd-workflows/commands/tdd-cycle.md:209-213` |
| implementer (green, vertical slices) | Opus 5.5 | high | separate; `implementer.md` | C++26 reflection plus POSIX process code. Anthropic's `high` is for work where verification matters or edge cases are likely. In the one measured comparison, Sonnet 5.5 implementers passed first review less often. | CC/model-config.md:661; A/claude-opus-5-5.md:123; PR/antonshubin-opus55-vs-sonnet5.md |
| implementer escalation (after a partial caused by reasoning) | Fable 5.1 | high | same definition, per-invocation `model` | Already MP's `policy.escalation`. superpowers also moves up one tier on fix rounds 4 and 5. | model-policy.md:26-39; R/superpowers `skills/subagent-driven-development/SKILL.md:201-202` |
| reviewer (standards and spec, cold) | Fable 5.1 | high | separate, named, never a fork; `reviewer.md` | A fresh context is not biased toward code it just wrote. Using a different model from the Opus author spreads the blind spots. Low volume keeps the Fable premium small. | CC/best-practices.md:468, 526; A/harness-design-long-running-apps.md:44; PR/jeanfbrito-benchmark-subagents.md |
| security reviewer (59d, 59f, 59g1) | Fable 5.1 (the receipt records the model that actually ran) | xhigh | separate instance, run in parallel with the reviewer; brief on `reviewer.md` | Effort helps security work most. Anthropic's own security verifiers run at xhigh. Each reviewer takes one lens. | A/blog-spending-your-effort.md:170; R/claude-plugins-official `plugins/claude-security/agents/scan-verifier.md:1-8`; CC/agent-teams.md:330; CC/model-config.md:520 |
| retro-writer | Fable 5.1 | high | separate; `retro-writer.md` | Judges the whole lane, the review included. "Cheapen mechanics, never judgment." | strict-cost spec :27-31; model-policy.md:14 |
| doc-writer | Sonnet 5.5 | high (its default, medium, is the cost lever) | separate per documentation lane; `doc-writer.md` | Bounded agent-facing prose. Sonnet is the documented daily model. | CC/costs.md:249; CC/model-config.md:660 |
| frontier-scheduler | Opus 5.5 | high | existing definition | Judges path conflicts, read-only, low volume. | model-policy.md:17 |
| extractor | Haiku 5.5 | low | existing definition | Mechanical receipts. Haiku 5.5 now honours effort, and it passed scoped tasks 70 of 70 at low in one test. | `O/docs/platform/models-overview.md:28`; PR/aidiveyt-haiku55-routing.md; PR/jeanfbrito-benchmark-subagents.md |
| merger | parent | session | parent, or a separately briefed session | Integrates one lane at a time, after the `owned_paths` check. | `MP/docs/agents/claude-team.md` Roles; `MP/docs/agents/codex-task-orchestration.md#ownership` |

**Confidence.**
- High that the role split and the independence rules are right: three Anthropic documents, three
  first-party role sets and MP's own 2026-10-13 incident all point the same way.
- Medium on the model per role: Anthropic's guidance is qualitative, MP's user decisions Q9 and Q10
  already fixed several rows, and the cost data comes from practitioners' small samples.
- Medium to low on the exact effort levels: Anthropic says to start at the defaults and tune by
  type of work, and MP has not measured any per-role spend yet.

**Evidence that decides it.**
- Anthropic documents the two splits this team rests on, and says nothing more. The splits are a
  writer and a reviewer in separate contexts, and "one Claude write tests, then another write code
  to pass them" (CC/best-practices.md:468-478). The documented risk is a reviewer that reports gaps
  in sound work (CC/best-practices.md:539).
- Anthropic's harness work found that "Out of the box, Claude is a poor QA agent": it found real
  issues, then "talk[ed] itself into" approving the work anyway. Tuning a standalone evaluator to be
  skeptical worked; making the generator self-critical did not
  (A/harness-design-long-running-apps.md:44, 175).
- Anthropic's own role definitions set `effort` per role. In claude-security, the generator, the
  verifiers and the researchers run at `xhigh`; the loader runs at `low` and inventory at `medium`.
  The verifier's default is to refute or reject (R/claude-plugins-official@641d925
  `plugins/claude-security/agents/*.md`).
- The Agent tool takes a per-invocation `model`, and from v2.1.292 a per-invocation `effort`
  (CC/sub-agents.md:339-409; `O/docs/github/claude-code-CHANGELOG.md:491`). A role can therefore be
  a brief on an existing definition at its own model and effort.

## 2. Anthropic guidance

### 2.1 Does Claude Code document a team for this?

It documents the building blocks and two patterns, but no SDLC team.
- The building blocks are subagent definitions, the model and effort resolution order, worktree
  isolation, forks, agent teams and dynamic workflows (CC/agents.md, CC/sub-agents.md,
  CC/agent-teams.md, CC/workflows.md).
- The two patterns are writer and reviewer, and test writer and implementer
  (CC/best-practices.md:468-478).
- Anthropic's nearest published role sets are its official plugins (section 4): `feature-dev`
  (explorer, architect, reviewer), `code-review` (Haiku gate, five Sonnet reviewers, Haiku scorers),
  `claude-security` (generator and refuting verifiers) and the Code with Claude 2026 `evaluator`
  (R/cwc-long-running-agents@ad107a9 `claude-code-config/.claude/agents/evaluator.md`).
- MP's lane lifecycle composes these patterns. Nothing Anthropic publishes contradicts it.

### 2.2 Definition fields that matter for this team

The frontmatter table is at CC/sub-agents.md:291-308. These fields matter here:
- **`model` and `effort`.** The model is resolved in this order: per-invocation parameter, then
  frontmatter, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the session (CC/sub-agents.md:339-350).
  Per-invocation `effort` overrides the frontmatter, and `CLAUDE_CODE_EFFORT_LEVEL` beats both
  (CC/sub-agents.md:405-409). This host sets no `CLAUDE_CODE_EFFORT_LEVEL` and no
  `CLAUDE_CODE_SUBAGENT_MODEL`. User settings hold `model: opus`, a per-model `effortLevel` (Opus
  5.5 at xhigh) and `CLAUDE_CODE_FORK_SUBAGENT=1` (key read only).
- **Effort inheritance.** A subagent without an `effort` field inherits the session level. Per-model
  `modelSettings` do not reach subagents (GH/anthropics_claude-code-92660.json, open). MP's six
  definitions all set `effort`; built-in Explore, general-purpose and forks run at the session's
  xhigh.
- **Checking what ran.** `/tasks` shows each subagent's model and effort from v2.1.242
  (CC/sub-agents.md:374). Subagent transcripts record `model`, `usage` and `effort`
  (GH/anthropics_claude-code-100701.json; PR/jeanfbrito-benchmark-subagents.md). Effort could not be
  observed before that (GH/anthropics_claude-code-85416.json).
- **`tools`, `disallowedTools` and `permissionMode`.** Read-only reviewers already use
  `permissionMode: plan` with Edit and Write denied. CC/sub-agents.md:1026 says to leave `Agent` off
  a reviewer that should stay read-only; MP's `reviewer.md` still allows `Agent`.
- **`isolation: worktree`.** It branches "by default from your default branch rather than the parent
  session's HEAD" (CC/sub-agents.md:305). MP lanes branch from the integration branch at a recorded
  base SHA, so the field does not fit.
- **`maxTurns`.** Hitting the limit returns partial output that can be resumed (from v2.1.246;
  CC/sub-agents.md:297).
- **`color`.** Cosmetic only.
- **`memory`.** It would create a second store of learnings, which conflicts with ADR 0001 routing
  every learning through the retro. Do not use it.
- **`hooks`.** Hooks scoped to one role are possible; plugin agents ignore them (CC/sub-agents.md:227).
- **Forks.** A fork inherits the whole conversation, model and prompt cache, and is the opposite of
  a cold reviewer (CC/sub-agents.md:1180-1190). Fork mode is on by default in interactive sessions
  from v2.1.232 (CC/sub-agents.md:1196-1210), and a call that names no type gets general-purpose.
  Review must name its `subagent_type`. A practitioner traced a rubber-stamping reviewer to exactly
  this (PR/claudelab-fork-default-review-agent.md).
- **Nesting and concurrency.** Nesting is three layers deep by default, and up to 20 subagents run
  at once (CC/sub-agents.md:1008-1048).
- **What a subagent loads.** A non-fork subagent loads CLAUDE.md, git status and preloaded skills,
  but not the parent's history (CC/sub-agents.md:1052-1075). The built-in Explore and Plan skip
  CLAUDE.md, so a brief to Plan must name `AGENTS.md`.

### 2.3 Patterns Anthropic documents

- **Verification.** Give Claude a check it can run. Ways to close the loop: a `/goal` condition, a
  Stop hook, or "a verification subagent ... [that] has a fresh model try to refute the result, so
  the agent doing the work isn't the one grading it". Ask for evidence, not assertions
  (CC/best-practices.md:27-52).
- **Adversarial review.** The reviewer "sees only the diff and the criteria you give it, not the
  reasoning that produced the change". Tell it to flag only gaps that affect correctness or the
  stated requirements, because chasing every finding leads to over-engineering
  (CC/best-practices.md:520-540).
- **Agent teams.** Start with 3 to 5 teammates; "Three focused teammates often outperform five
  scattered ones". Give each teammate its own files. Teams are experimental, with no worktree
  isolation, one team per session and no nesting (CC/agent-teams.md:370-410, 474-487). They use
  about 7x the tokens when teammates run in plan mode, and the docs say to use Sonnet for teammates
  (CC/costs.md:214-224, 330-332).
- **Parallel review lenses.** "A single reviewer tends to gravitate toward one type of issue at a
  time", so give each reviewer a distinct lens (CC/agent-teams.md:328-340).
- **Dynamic workflows.** For cross-checked fan-out: "adversarially verify each finding before
  reporting it" (CC/workflows.md:241-245). The bundled `/deep-research` votes on each claim
  (CC/workflows.md:73).

### 2.4 Models and effort as of October 2026

- **Aliases.** On the Anthropic API, `opus`, `sonnet` and `haiku` resolve to Opus 5.5, Sonnet 5.5
  and Haiku 5.5, and `fable` resolves to Fable 5.1 (CC/model-config.md:46, 52).
- **Prices per MTok, input and output.** Fable 5.1 $10 and $50; Opus 5.5 $4 and $20; Sonnet 5.5 $2
  and $10; Haiku 5.5 from $0.10 and $0.50 (`O/docs/platform/models-overview.md:42-48`).
- **Cache reads.** These bill at 0.025x on Fable 5.1 and 0.05x on Opus 5.5 and Sonnet 5.5
  (`O/docs/platform/pricing.md:418`). That is $0.25 against $0.20 per MTok, so in long cached
  contexts Fable costs about 1.25x Opus rather than 2.5x.
- **Which model to start with.** Anthropic says to start with Opus 5.5 for most workloads, and to
  use Fable 5.1 "when your evals on Claude Opus 5.5 at higher effort still fall short"
  (`O/docs/platform/models-overview.md:19`). Opus 5.5 "performs at the level of Claude Fable 5.1 on
  most work" (A/claude-opus-5-5.md:8). At its default (medium), it scores 54.6% on FrontierCode
  (A/claude-opus-5-5.md:123).
- **Fable.** Hand it ambiguous problems such as root-cause investigations and architecture
  decisions. It verifies its own work with less prompting (CC/model-config.md:81-84). It may bill to
  usage credits, depending on the plan (CC/model-config.md:92-112).
- **Effort levels and defaults.** Fable 5.1, Fable 5, Opus 5.5, Sonnet 5.5 and Haiku 5.5 accept
  `low` to `max` (CC/model-config.md:598-602). Opus 5.5, Sonnet 5.5 and Haiku 5.5 default to
  `medium`; the others default to `high` (CC/model-config.md:608).
- **What each level is for.** `medium` is for day-to-day work with a clear scope. `high` is for
  "work where verification matters or edge cases are likely". `max` is for hard autonomous problems
  such as finding security vulnerabilities, but "prone to overthinking". Opus 5.5 at `medium`
  matches or exceeds Opus 5 at `high` (CC/model-config.md:655-670).
- **The blog's heuristic.** "Did it not *try* hard enough, or did it not *know* enough?" Raise
  effort when Claude skipped a file or the tests; switch to a larger model when it had the context
  and was still wrong. "For most tasks you should use the model's default effort level", and treat
  effort "as a general preference based on the type of work" (A/blog-model-and-effort-level.md:10,
  124, 142-160). Fable is the specialist, Opus the expert, Sonnet the generalist
  (A/blog-model-and-effort-level.md:167-176).
- **The effort study.**
  - "Higher effort is best for tasks with lots of hidden edge cases."
  - Pass rates from low to top effort on Fable 5.1: security 64% to 87%, software 43% to 56%.
  - At xhigh, Opus 5.5 "reproduced the crash first, wrote a randomized test against a reference ...
    and checked that its tests failed on half-finished fixes".
  - Effort reduces missed edge cases but does not fix a wrong approach.
  - The author implements at low and verifies on high.
  - Sources: A/blog-spending-your-effort.md:19, 140-182, 213-215.
- **Fallback.** On Fable 5.1, Fable 5 and Opus 5.5, cybersecurity-flagged requests re-run on Opus
  4.8 (CC/model-config.md:518-530). Fable 5.1's safeguards "hand some security requests to Opus"
  (A/blog-spending-your-effort.md:221). A security reviewer can therefore run on Opus 4.8 without
  failing, so its receipt must record the model that answered.

### 2.5 Engineering posts

- **Multi-agent research** (A/multi-agent-research-system.md).
  - An Opus lead with Sonnet subagents beat single-agent Opus by 90.2% on research (:36).
  - Token usage alone explains 80% of the variance (:39).
  - Multi-agent systems use about 15x the tokens of chat. "Most coding tasks involve fewer truly
    parallelizable tasks than research" (:42).
  - Each subagent needs an objective, an output format, tool guidance and boundaries (:66), and
    effort scaled to complexity (:67).
  - Subagents should write their output to files (:142).
- **Harness design** (A/harness-design-long-running-apps.md).
  - The roles are planner, generator and evaluator.
  - Agents grading their own work "reliably skew positive" (:41). Separating the judge is "a strong
    lever" (:44).
  - A sprint contract is negotiated before code (:107). Out of the box, Claude is a poor QA agent
    (:175).
  - The evaluator "is worth the cost when the task sits beyond what the current model does reliably
    solo" (:199-202).
  - Costs in the V2 harness: planner $0.46, builds $71.08, $36.89 and $5.88, QA $3.24, $3.09 and
    $4.06. QA was 8% of the $124.70 total (:223-232).
- **C compiler** (A/building-c-compiler.md).
  - The task verifier must be "nearly perfect, otherwise Claude will solve the wrong problem" (:90).
  - The test harness keeps output short, logs to a file and samples with `--fast` (:108-110).
  - A known-good compiler oracle let agents work in parallel (:121).
  - Specialists handled deduplication, performance, design critique and documentation (:127).
  - "It is easy to see tests pass and assume the job is done" (:179).
- **Long-running harnesses.** "It is unacceptable to remove or edit tests". Features are tracked in
  JSON because models overwrite JSON less often than Markdown
  (A/effective-harnesses-for-long-running-agents.md:78).
- **Context engineering.** A subagent returns "a condensed, distilled summary of its work (often
  1,000-2,000 tokens)" (A/effective-context-engineering.md:162).
- **Evals.** "Make your graders resistant to bypasses or hacks". Start each trial from a clean
  environment (A/demystifying-evals-for-ai-agents.md:359, 380).
- **Code with Claude 2026 evaluator** (R/cwc-long-running-agents@ad107a9 `README.md:13-14`).
  - The evaluator has a default-FAIL contract, no Write or Edit tools, and a fresh context.
  - Its prompt opens: "You did not see how it was built and you should not trust the builder's own
    assessment" (`claude-code-config/.claude/agents/evaluator.md`).

## 3. Practitioners, last 30 to 90 days

### 3.1 Role sets reported to work

- **Waves of implementers and reviewers** (PR/antonshubin-opus55-vs-sonnet5.md, 2026-09-26).
  - A lead splits issues into lanes by file. One implementer per worktree, then a separate reviewer
    that runs the tests and "breaks the code on purpose to see whether a test goes red".
  - Over 203 PRs and 411 reviewer runs, Opus 5.5 replaced Fable 5.1 as reviewer "at about a third
    of the price", and "neither reviewer caught every security bug on its own".
- **Orchestrator, doers, reviewer and blind tester** (r/ClaudeCode thread 1wvhzr2, 2026-10-02, 28
  points and 36 comments, through Last30Days because webclaw hit a login wall; O/local/last30days/run1.md).
  - "Keep the blind tester. Its whole value is that it never saw the plan or the diff".
  - "Never point several agents at the same files".
- **Finders and verifiers** (PR/jeremyknox-reviewer-agrees.md, 2026-08-08). Verifiers refute "a
  third to half" of what finders raise. "An approval only carries information if the approver was
  capable of rejecting."
- **Effort per role in oh-my-claudecode** (GH/Yeachan-Heo_oh-my-claudecode-4206.json, 2026-10-01):
  "an executor at `medium`, a critic at `max`, and a reviewer at `high`". Implemented in PR #4207 for
  CLI workers.
- **Measured routing** (PR/jeanfbrito-benchmark-subagents.md, 2026-10-10).
  - Over 60 days, the `reviewer` cost $1.79 on Sonnet against $3.11 on Opus, while `builder-fast`
    cost $176 against $237.
  - The author moved the reviewer to Opus and an auditor, called after two failures, to Fable:
    "low-volume judgment roles, so the real premium is a few dollars".

### 3.2 Failure modes

- **Rubber-stamp reviewers.**
  - Same-family pairs "share their omissions". The counters are a different model, an adversarial
    brief, grounding in execution and a checklist (PR/debugly-echo-chamber.md, 2026-10-08).
  - The tell is an approval rate that "does not move when the input quality does"
    (PR/agenticlab-rubber-stamp-verifier.md, 2026-08-22, after MAST's "Incorrect Verification").
  - A fork default turned a named reviewer into a participant (PR/claudelab-fork-default-review-agent.md,
    2026-08-17).
  - Anthropic's own claude-security verifier says: "A panel of three agreeable voters is worth
    nothing" (R/claude-plugins-official `plugins/claude-security/agents/scan-verifier.md:14`).
- **Implementers that weaken tests.**
  - Across 24 runs on fixable bugs, no agent touched a test. On a contradictory spec under time
    pressure, 2 of 6 runs edited the test (one Opus skip, one Haiku delete). With the tests made
    read-only, 0 of 6 did (PR/mattbusel-cheat-on-tests.md, 2026-10-10; plugin `tamperproof`, a
    PreToolUse and Stop pair).
  - Plain pytest passed all nine "testwashing" variants. A checker caught six, but missed "an
    assertion loosened to a truthiness check" and "an expected value edited to match the bug".
    Read every change to a test file (PR/skylos-testwashing.md, 2026-10-14).
  - superpowers implementers claimed TDD without a red run. The fix requires RED and GREEN
    evidence in the report (GH/obra_superpowers-994.json, merged as superpowers PR #1065).
  - The structural answer: "separate the doer from the judge" (PR/penloom-pass-any-test.md,
    2026-07-05).
- **Context bloat and silent cost.**
  - In a measured SDD run of about $13, the controller cost about $6 to $7 against $5 to $6 for all
    implementers (R/superpowers strict-cost spec :13-20).
  - Cached reads were 68% of $593 spent in one six-hour window; cost tracked calls times context with a correlation of
    0.99 (PR/antonshubin-opus55-vs-sonnet5.md).
  - Loop cycles that named no subagent type rode the Fable session and made up 35% of subagent
    spend (PR/jeanfbrito-benchmark-subagents.md).
  - Explore inherits the main model, so it runs on Opus 5.5 under a Fable session; a project agent
    named `Explore` overrides it (PR/aidiveyt-haiku55-routing.md; CC/sub-agents.md:44).
  - Subagents inherit session effort (GH/anthropics_claude-code-92660.json, open 2026-09-07).
- **Review loops on trivial tasks.** Two-stage review spirals on mechanical tasks
  (GH/obra_superpowers-1120.json, open). Anthropic's own caveat matches: a reviewer told to find
  gaps finds some (CC/best-practices.md:539).

### 3.3 Cost per role

Implementation dominates the spend; judgement roles are cheap in absolute terms.
- Anthropic's harness: QA 8%, planner 0.4% (A/harness-design-long-running-apps.md:223-232).
- superpowers: task reviewers about $1 to $1.50 of about $13.
- jeanfbrito: reviewer $1.79 to $3.11 against builder $176 to $237.
- In MP the implementer and the parent are the cost lines to watch. Fable on the reviewer and the
  retro-writer is a small premium, and Haiku belongs on mechanical extraction only.
- Haiku 5.5 bills 5x more above a 100K-token prompt, so long-context roles do not belong on it
  (PR/jeanfbrito-benchmark-subagents.md, fact 4; `O/docs/platform/pricing.md:622`).

### 3.4 What Last30Days added

| Run | Window | Items | What it held |
| --- | --- | --- | --- |
| run1, Markdown | 2026-09-14 to 2026-10-14 | 72 | 22 HN, 30 GitHub, 10 X, 7 YouTube, 3 Reddit |
| run1, JSON (same plan) | same | 69 | the same minus Reddit |
| run2 | same | 79 | Mostly off-topic X posts |

- Reddit was degraded: the ScrapeCreators backup returned HTTP 402.
- The useful hits were the r/ClaudeCode blind-tester thread above,
  `bankielewicz/mod-builder#18` ("limit which paths each TDD subagent type may write", 2026-10-13)
  and `lexfrei/ccc#67` ("pin teammate model and effort to agent defaults").
- Several X posts present routing advice as an "Official Anthropic tip"
  (x.com/mirku21/status/2109026276048769472, x.com/tekari0/status/2105999486007074975).
  UNVERIFIED: no Anthropic page in this mirror says it.

## 4. Role libraries

Read from `~/.claude/plugins/cache` at the installed versions (frontmatter extracts are in
`O/local/plugin-frontmatter/`) and from clones in R. Nothing was run.

| Library (version or commit) | Roles | Model | Effort | Distinctive |
| --- | --- | --- | --- | --- |
| claude-plugins-official `feature-dev` (641d925) | code-explorer, code-architect, code-reviewer | sonnet | none | Two or three architects with different focuses; three reviewers in parallel with separate lenses (`commands/feature-dev.md:106`) |
| claude-plugins-official `pr-review-toolkit` | code-reviewer, code-simplifier, comment-analyzer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer | opus for the reviewer and simplifier, inherit for the rest | none | Reports only findings with confidence of 80 or more (`agents/code-reviewer.md:41`); a dedicated test-coverage analyzer |
| claude-plugins-official `code-review` command | gate, summarizer, 5 reviewers, per-issue scorers | Haiku for gating and scoring, Sonnet for review | none | Scorers re-check each finding; anything under 80 is dropped (`commands/code-review.md:11-27`) |
| claude-plugins-official `claude-security` | researcher, verifier, patch generator, patch verifier, inventory, loader, redactor | inherit or sonnet | xhigh for judgement roles, medium or low for mechanics | Three refuting voters, keep at 2 of 3 (`workflows/scan.js:143`, `skills/claude-security/jobs/scan-codebase.md:29`); verifiers default to FALSE_POSITIVE or REJECT |
| claude-plugins-official `math-proof` | worker, worker-deep, judge | inherit | low, medium, medium | The judge never talks to workers; queries are self-contained files |
| anthropic-agent-skills `skill-creator` | grader, comparator, analyzer | no frontmatter | none | Blind comparison of outputs |
| oh-my-claudecode 5.7.4 (clone 44c2730) | 19, including planner, architect, critic, executor, test-engineer, verifier, code-reviewer, security-reviewer | opus for judgement, sonnet for execution and verification, haiku for explore and writer | none in frontmatter; stated in prose (critic maximum, reviewer high) | Critic makes predictions before investigating and analyzes gaps (`agents/critic.md:15-36`); verifier: "Never self-approve" (`agents/verifier.md:30-32`); executor lists "Test hacks" as a failure (`agents/executor.md:99`); effort was prose-only until GH/Yeachan-Heo_oh-my-claudecode-2786.json |
| claude-code-workflows, i.e. wshobson/agents (46891e7) | 202 agents | fable 2, opus 54, sonnet 70, haiku 24, inherit 52 (`docs/agents.md:236-242`) | none | `tdd-cycle` runs RED and GREEN as separate agents, with a reviewer after RED and user checkpoints, but the GREEN prompt does not forbid editing tests (`plugins/tdd-workflows/commands/tdd-cycle.md:169-300`); `team-lead` on fable; `cpp-pro` on opus; avoid Fable for security agents (`docs/agents.md:270-290`) |
| nyldn octo 11.13.2 (claude-octopus 87efa22) | 69 files, including personas | opus or sonnet | personas set it: code-reviewer opus high, security-auditor opus high, tdd-orchestrator opus medium, debugger sonnet high | Adversarial review across external providers; "Claude-native first, Octopus for escalation" (`README.md:5`) |
| ultrapowers 2.0.0 (c6bcb5d) | advisor, code-reviewer, planner, research-fetch | opus, with haiku for fetch | none | The mattpocock method with a two-axis review and a QA checklist (`README.md:56-60`) |
| mattpocock-skills 1.3.1 (49dd158) | no agent files; roles live in skills | not set | not set | `implement-spec`: exploration, one implementer per ticket in a worktree, a merger, then `code-review` with two parallel subagents (`skills/engineering/implement-spec/SKILL.md:23-36`); `tdd` warns against horizontal slicing (`skills/engineering/tdd/SKILL.md:32`) |
| VoltAgent subagents (408d3c9) | 154 files | sonnet 109, inherit 26, haiku 19, opus 0 | none | The README routes reviewers to `opus` (`README.md:425-433`), but no file sets it; `code-reviewer` holds Write and Edit despite the "Read-only agents (reviewers)" rule |
| caveman 4.0.1, claude-community codebase-quality 1.0.0 | cavecrew reviewer; auditors | haiku reviewer; opus for bug scan and secret audit, haiku for profiling | none | codebase-quality runs every auditor with `permissionMode: plan` |
| obra/superpowers (bb92a77, public, not installed) | implementer, task reviewer (spec and quality), final reviewer, fixer | "least powerful model that can handle each role"; final review on the most capable | none (GH/obra_superpowers-1747.json) | Model rules (`skills/subagent-driven-development/SKILL.md:184-219`); "Turn count beats token price"; "Cheapen mechanics, never judgment"; capped fix loop |

Only Anthropic's claude-security and math-proof, and octo's personas, set `effort` in frontmatter.
GitHub code search found 0 hits for `effort path:agents` in anthropics/claude-plugins-official,
where the clone has 12 such files, so code search under-reports this pattern (section 8).

## 5. Recommendation for MP lanes

### 5.1 Agents per unit

- **A cxx unit** runs four required instances in sequence: test author, implementer, reviewer and
  retro-writer.
  - Add the test-contract check when the tests are new rather than ports.
  - Add the security reviewer, in parallel with the reviewer, on 59d, 59f and 59g1.
  - Add the extractor whenever a receipt is needed.
  - The parent merges.
- **A documentation unit** runs three: doc-writer, reviewer and retro-writer.
- **A fix round** resumes the same implementer with the findings, then runs one scoped re-review.
  This follows superpowers' single fix wave with a scoped re-review
  (`skills/subagent-driven-development/SKILL.md:445-460`) and MP's escalation rule.
- **Across units**, keep at most three writer lanes in flight (the ticket-frontier default). That
  means at most about five subagents at once, which matches Anthropic's "start with 3-5" and
  "three focused teammates" (CC/agent-teams.md:370-380). The architect and the scheduler run
  between waves, not inside a unit.

### 5.2 Separate agents versus briefs

Separate instances are required for independence. A separate definition is needed only where tools,
permissions or preloaded skills must differ.

- **Separate instances:**
  - Test author against implementer: "one Claude write tests, then another write code"
    (CC/best-practices.md:478); the CT-59 rule that the implementer may not weaken the tests
    (P/reviews/ccm-20261014/ct59/CT59-design.md:137).
  - Reviewer against implementer and test author (CC/best-practices.md:526).
  - Security reviewer against reviewer: one lens each (CC/agent-teams.md:330).
  - Retro-writer against everyone it audits.
  - Merger against the writer (`docs/agents/claude-team.md`).
- **Briefs with a per-invocation `model` and `effort`, using no new definition:**
  - Test author on `implementer.md`: same tools, and the `tdd` preload fits.
  - Test-contract check and security reviewer on `reviewer.md`: same read-only tools.
  - Implementer escalation on `implementer.md`.
  - Architect: a parent step, or the built-in `Plan` with the brief naming `AGENTS.md`, because
    Plan skips CLAUDE.md.

### 5.3 Mechanical guards, not more agents

1. **Test lock.**
   - The test author commits at `T` with a RED receipt: the ctest exit, the failing test names and
     why each fails.
   - The lane record gains `test_commit` and `locked_tests`.
   - A static check passes only when `git diff --name-only <test_commit>..HEAD -- <locked_tests>` is
     empty or each change carries a reviewer's approval.
   - The check belongs in the retro gate or `dev/check.py`, the retro-writer's destination for
     mechanical rules.
   - Optionally, a mod denies edits to locked paths while the implementer runs. Under D92, that is
     a mod, not a fourth settings hook.
   - Basis: A/effective-harnesses-for-long-running-agents.md:78; PR/mattbusel-made-it-impossible.md;
     PR/skylos-testwashing.md.
2. **Differential check.** The reviewer records that the locked tests fail at `test_commit` and pass
   at the head. That is the "does a test fail without the change" signal (PR/debugly-echo-chamber.md;
   GH/obra_superpowers-994.json). It replaces a blind-tester agent with a fact.
3. **Oracle-derived tests for CT-59.** Units 59b, 59e1 and 59f port the Python
   agent-protocol tests (P/reviews/ccm-20261014/ct59/CT59-design.md:120-125). Their expected values
   therefore come from an independent source, as the GCC oracle did (A/building-c-compiler.md:121)
   and as the `tdd` skill requires to avoid tautological tests
   (R/mattpocock-skills `skills/engineering/tdd/SKILL.md:31`).
   - Limit the test author to the ticket's acceptance seam. The implementer keeps working in
     vertical red and green slices, and may add tests but not change locked ones. This answers the
     horizontal-slicing warning (`tdd/SKILL.md:32`).
4. **Named, non-fork dispatch for judgement roles.** Extend C1 root cause F's `PreToolUse(Agent)`
   idea (P/reviews/ccm-20261013/prevention/C1-root-causes.md:495). A review or retro brief without
   `subagent_type` is denied, and `fork` is never used for review (CC/sub-agents.md:1205-1210).
5. **A model and effort receipt.** Every lane receipt copies `model` and `effort` from the subagent
   transcript, or from `/tasks`. This catches alias drift (jeanfbrito, fact 1), Fable or Opus 5.5
   falling back to Opus 4.8 on cyber-flagged requests (CC/model-config.md:520), and dropped effort
   (GH/anthropics_claude-code-100701.json).
6. **Severity calibration.** Reviewers flag only correctness and requirement gaps
   (CC/best-practices.md:539). P1 needs a `path:line` and a concrete failure scenario, which is the
   claude-security standard (`scan-verifier.md:26`). This addresses review-loop spirals on
   mechanical tasks (GH/obra_superpowers-1120.json).

### 5.4 What not to adopt

- **Agent teams.** They are experimental, with no worktree isolation and one team per session
  (CC/agent-teams.md:474-487). Per-invocation effort is dropped for named in-process teammates
  (GH/anthropics_claude-code-100701.json, open 2026-10-09). Team agents ignored custom definitions
  until fixed (GH/anthropics_claude-code-30703.json; CHANGELOG:850). MP's settings do not enable
  them.
- **`isolation: worktree` in frontmatter.** It uses the wrong base branch (CC/sub-agents.md:305).
- **The `memory` field.** It would be a second store of learnings (ADR 0001).
- **Haiku for review, or Sonnet for C++ implementation.**
  - Anthropic's own review pipeline keeps Haiku to gating and scoring (`code-review.md:11-27`).
  - The Sonnet 5.5 implementer passed first review 13% of the time against 33% for Opus 5.5
    (PR/antonshubin-opus55-vs-sonnet5.md).
  - In one replay, Sonnet "was never the best choice" (PR/jeanfbrito-benchmark-subagents.md).
- **`max` effort as a default for any role.** It shows diminishing returns and "is prone to
  overthinking" (CC/model-config.md:663). Use `xhigh` where Anthropic's own verifiers do.

### 5.5 Are new agent files worth a session restart?

Not for this set: every added role is a brief. If a role later needs a mechanical difference that
frontmatter carries (`tools`, `hooks`, `permissionMode`, `skills`), add the file and restart at the
next planned handoff.

- **What the docs say.** Claude Code watches `.claude/agents/`, and a new or edited file is used "with
  no restart needed". The only exception relevant to MP is that the watcher "covers only directories
  that existed when the session started" (CC/sub-agents.md:239-245).
- **What MP's 2026-10-13 failure was.** `.claude/agents/` first landed at 20:07Z in a session that
  started at 18:54Z (P/reviews/ccm-20261013/prevention/C1-root-causes.md:195-201). That is the
  documented exception, not proof that hot reload fails.
- **What the field reports.** Hot reload is unreliable in practice:
  - GH/anthropics_claude-code-75432.json (open since 2026-07-07): new files were never picked up on
    Windows in a worktree session.
  - A macOS comment there (2026-08-24): new files appeared "a few minutes later", so the first call
    fails, and edits to an existing file's `tools` "never applied". The running agent kept tools
    the file had removed.
- **So:** keep the rule at `MP/docs/agents/claude-team.md:23-24` for both new and edited
  definitions. Batch definition changes before a planned `/clear`, then restart the terminal, which
  the session-handoff and session-resume skills already cover. Confirm the roster and each role's
  model and effort on the first dispatch with `/tasks`.

### 5.6 Differences from CT-59 section 4 and the model policy

- **Test author:** effort `xhigh` rather than `high`, a RED receipt and a locked-test check
  (CT59-design.md:137).
- **Security reviewer:** effort `xhigh` rather than `high`, and the receipt records the model that
  answered (CT59-design.md:140).
- **New row:** the test-contract check, a reviewer brief at `medium`, only for units whose tests are
  new.
- **Model policy:** add rows `test` (opus, xhigh), `security-review` (fable, xhigh) and
  `contract-check` (fable, medium) to model-policy.md. That is the parent's edit; this report does
  not make it.
- **F5:** answered as CT-59 proposed. Brief the existing files; no restart.

## 6. Code examples found

- **anthropics/claude-plugins-official@641d925a**
  - `plugins/claude-security/agents/scan-verifier.md:1-26`: a refuting voter at `effort: xhigh`.
  - `patch-verifier.md:1-12`: "your default is REJECT".
  - `patch-generator.md:1-35`: a fresh attempt that takes the previous round's objections.
  - `workflows/scan.js:143`: keeps a finding at 2 of 3 voters.
  - `plugins/code-review/commands/code-review.md:11-27`.
  - `plugins/math-proof/agents/*.md`: effort low or medium.
- **anthropics/cwc-long-running-agents@ad107a9:** `claude-code-config/.claude/agents/evaluator.md`
  (fresh-context evaluator) and `.claude/hooks/verify-gate.sh` and `track-read.sh` (default-FAIL
  contract).
- **obra/superpowers@bb92a77**
  - `skills/subagent-driven-development/SKILL.md:184-219, 308-360, 445-455`.
  - `implementer-prompt.md:133-134` (TDD evidence).
  - `docs/superpowers/specs/2026-06-10-strict-cost-sdd-design.md:13-45`.
- **mattpocock/skills@49dd158:** `skills/engineering/tdd/SKILL.md:25-38` and
  `skills/engineering/implement-spec/SKILL.md:23-36`.
- **Yeachan-Heo/oh-my-claudecode@44c2730:** `agents/critic.md:1-36`, `agents/verifier.md:30-32` and
  `agents/executor.md:99`.
- **wshobson/agents@46891e7:** `docs/agents.md:230-282`,
  `plugins/tdd-workflows/commands/tdd-cycle.md:169-300` and
  `plugins/agent-teams/agents/team-lead.md:1-6`.
- **nyldn/claude-octopus@87efa22:** `agents/personas/code-reviewer.md`, `security-auditor.md` and
  `tdd-orchestrator.md`, each with model and effort in frontmatter.
- **Mattbusel/tamperproof:** PreToolUse and Stop hooks that make tests read-only. Cited through
  PR/mattbusel-made-it-impossible.md; not cloned.

## 7. Routes

`fx` is `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`. Keys reached commands through the environment only, and no key value was
printed or written. Scripts are in `scratchpad/research5/R12/bin/`.

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
| --- | --- | --- | --- | --- | --- |
| 1 | Exa | `fx exa2.sh <out> "<query>" 10 [startPublishedDate]` (POST api.exa.ai/search, key on curl stdin), 14 queries plus 1 retry | 0 for all; HTTP 200 for 14; HTTP 429 once (10 requests per second) and the retry got 200 | 10 per query | Yes: seeded every Anthropic post and practitioner page |
| 1 | Context7 | `fx ctx7 library "claude code"`, `fx ctx7 library superpowers`, `fx ctx7 docs /websites/code_claude "<q>"` | 1, 1, 1 | "Monthly quota reached" | No; gap |
| 1 | Firecrawl | `fx firecrawl search "<q>" --limit 5 --json` | 1 | HTTP 402, insufficient credits | No; gap |
| 1 | webclaw (Firecrawl fallback and D110 mirror) | `webclaw -t 60 <url> -f markdown > <file>`, 103 pages | 0 for all; the anthropic.com/engineering index is client-rendered (1.8 KB); two Reddit URLs returned a 252-byte login wall | 100 usable | Yes: every CC, A, platform and PR citation |
| 1 | gh raw CHANGELOG | `gh api -H 'Accept: application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` | 0 | 1,015,061 bytes | Yes (lines 491, 850) |
| 1 | Serper | `fx serper.sh <out> "<q>"` (POST google.serper.dev/search), 6 queries | 0, HTTP 200 each | 8 to 10 | Yes: seeded #39220, #30703, OMC#2786, superpowers#1120, wshobson#71 |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3.13 -I last30days.py "<topic>" --plan plan.json --emit md or json --search reddit,hackernews,github,x,youtube --save-dir ""`, three runs; `/usr/bin/python3` (3.9.6) refused because v3.18.4 needs 3.12 | 0, 0, 0 | 72, 69 and 79 items; Reddit degraded (ScrapeCreators HTTP 402); LLM rerank HTTP 503, local fallback used | Partly: the Reddit thread, mod-builder#18, ccc#67 |
| 2 | gh issue or pr view | `gh issue view <n> --repo <r> --comments --json ...`, falling back to `gh pr view`; 27 threads | 0 each | 27 | Yes; copies in GH |
| 2 | gh search issues | `gh search issues "<q>" --repo <r> --include-prs --limit 15`; 14 narrow queries, then 11 broader | 0 each | 0 to 15 | Yes: #75432, #85416, #92660, #100701, #92002, #79135, superpowers #1747, #2096, #994, OMC #4206, #4355 |
| 2 | GraphQL discussions | `gh api graphql` search type DISCUSSION, 8 queries | 0 each | anthropics/claude-code 0 (three queries); superpowers 0; OMC 1; wshobson 10; global 4 | No relevant hit (one off-topic: wshobson discussion 763, a dispatch-time model and effort tuner) |
| 2 | Saved-search route (task) | `./dev/mise run research:collect` | not run | n/a | Writes a tracked path another lane owns |
| 2 | Saved-search route (reproduced) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5 -F page=1 or 2`, each with a control `README repo:<r>`; read `dev/saved-searches.toml` and `dev/collect_saved_search.py` | 0 for 18 calls; HTTP 403 secondary rate limit for 8 calls, retried | see section 8 | Yes |
| 2 | Clones (D110) | `git -c core.hooksPath=/dev/null clone -q --depth 1 <url> <dir>`, 12 repositories | 0 each | commits in manifest.json | Yes; read only, nothing executed |
| local | Plugin cache | `python3 -I fm.py <plugin dir> [any]` frontmatter extract over 31 installed plugin versions; `installed_plugins.json` and `known_marketplaces.json` reads | 0 | 229 agent rows | Yes (section 4) |
| local | Settings keys | `python3 -I` read of `~/.claude/settings.json` and the MP settings files, env key names and effort values only | 0 | n/a | Yes (2.2) |

## 8. Proposed saved-search rows

These rows were not added; `dev/saved-searches.toml` is untouched.
- Each was reproduced read-only with its control in this session. Counts are `total_count` from
  page 1.
- Raw JSON is in `scratchpad/research5/R12/saved/`.

```toml
[[search]]
id = "official-agent-effort-xhigh"
query = "xhigh path:plugins/claude-security/agents"
repo = "anthropics/claude-plugins-official"   # 6 hits today; control README 61
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "superpowers-model-selection"
query = "\"Model Selection\""
repo = "obra/superpowers"                     # 13 hits (page 2 also 13); control README 30
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "wshobson-fable-tier"
query = "\"model: fable\""
repo = "wshobson/agents"                      # 6 hits; control README 75
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "voltagent-effort"
query = "effort"
repo = "VoltAgent/awesome-claude-code-subagents"   # 8 hits, prose only; control README 17
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

Not proposed as code-search rows:
- `"effort:" path:agents` on Yeachan-Heo/oh-my-claudecode and `effort path:agents` on
  anthropics/claude-plugins-official returned 0. The second has 12 matching files in the clone, so
  a 0 is not evidence of absence.
- Two issue-search rows would be worth having: `subagent hot reload repo:anthropics/claude-code`
  (#75432) and `effort teammate repo:anthropics/claude-code` (#100701). The collector only calls
  `/search/code` (`dev/collect_saved_search.py:179`), so they need a collector extension first.

## 9. Open gaps

- **Provider gaps.**
  - Context7: monthly quota, three calls, rc 1.
  - Firecrawl: HTTP 402.
  - Reddit: the webclaw mirror hit a login wall twice, and Last30Days' Reddit backup returned
    HTTP 402. The one thread is known only through Last30Days' excerpt.
  - Last30Days' LLM rerank returned HTTP 503.
  - The GitHub secondary rate limit hit 8 code-search calls; all were retried.
- **Measurements this report could not take.**
  - MP has no per-role cost or quality measurement. Every cost figure here comes from other
    people's workloads. Measure after the first CT-59 waves from the subagent transcripts (the
    jeanfbrito method), before changing any row.
  - Hot reload on this host is unverified: testing it needs a file under `MP/.claude/agents`, which
    this task's scope forbids. Treat #75432 as the operative risk.
  - Whether Fable bills to usage credits on the user's plan is UNVERIFIED (CC/model-config.md:92-112).
  - Whether a per-invocation `model` applies to the built-in `Plan` agent is UNVERIFIED. The docs
    describe Plan as inheriting the main model (CC/sub-agents.md:51-55). Confirm with `/tasks` on
    the first architect dispatch.
- **Evidence quality.**
  - C++-specific role evidence is thin: the generic `cpp-pro` agents (wshobson on opus, VoltAgent on
    sonnet) and Anthropic's Rust compiler post. Nothing measures agents on C++26 P2996 code.
  - Practitioner sources are single-author posts with small samples, and some sites may be
    AI-written. They are used as signals that agree with Anthropic's sources, never as the deciding
    evidence.
