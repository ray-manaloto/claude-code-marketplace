# Parallel specialist execution — 2026-10-13

The user requested parallel subagents with task-appropriate models, efforts and
tools. Source base: `979f06f8bfd008844d4d3beb9301706e256e4996`; parent `/root`
owns implementation and Git writes in the shared common directory. Three
concurrent read-only specialists ran; each acknowledged identity, scope, first
action and the live reply channel. No global model or configuration change ran.

| Agent | Requested model / effort | Input and bounded result | Tools actually used |
| --- | --- | --- | --- |
| `parallel_lsan_specialist` | `gpt-6-astra` / high | #13 at `5e119e5`; identified timeout cleanup leaving interruption disabled. | Read-only Git, rg, source/receipt reads, hashes and path checks. |
| `parallel_handoff_reviewer` | `gpt-6.1-sol` / high | Handoff `208a57b` against source `979f06f8`; verified 32 artifact and 14 log hashes, two reviews and 31 recorded tests; identified glossary/task conflicts and four selective integration units. | Read-only Git/diff/merge-tree and local receipt hashing; no tests rerun. |
| `parallel_contract_specialist` | `gpt-6.1-sol` / high | #28 `a1bd33e`, #29 `3131b89`; identified missing runtime gates and two acceptance cycles. | Read-only Git, narrow docs/source/receipt inspection. |
| `parallel_signal_reviewer` | `gpt-6.1-sol` / high | Independent review of the parent's signal repair; PASS, six tests rc 0, diff rc 0. | Local Git/Python and the existing bounded offline suite. |
| `parallel_research_receipts` | `gpt-6-luna` / high | Verified request ID, all ten raw hash references and eight research-source outcomes. | Local JSON parsing and hashing only. |
| `parallel_frontier_application` | `gpt-6.1-sol` / high | Verified A05b and completed-unit remediation; no remaining actionable implementation defect blocks bounded A06 resumption. | Read-only plan and directly linked receipt inspection. |
| `parallel_feedback_precheck` | `gpt-6.1-sol` / high | Verified the four-file feedback integration scope; found later uncommitted package work and required imports from fixed `208a57b` blobs. | Read-only Git/blob inspection; no tests rerun. |

Models and efforts were accepted by the callable spawn interface; served model
identity was not independently attested. The last two roles reused available
capacity after first-wave completions. No nested teams or sidebar tasks ran.
All workers owned no files and preserved shared edits. Heavy/container capacity
was not requested: a read-only census found 243 containers, one running, with
ownership unverified for this task. Unknown owners block heavy dispatch, not
these bounded filesystem inspections.

## Applied result and next units

The parent repaired the LSan adapter, added regression coverage in the existing
suite, updated its guidance/retro and retained exact receipts. Named validation,
check and original 19-file baseline each exited 0. Independent review passed;
local commit `4905c8e52ecd502de3b79e666799ab990a054c52` is clean in the #13
checkout. The original native verdict is still inconclusive, the old proposal
retired, and no native admission or source integration is implied.

The handoff can progress independently: first import the exact feedback helper
and 12 tests, add existing check discovery and two mise tasks; review that small
unit before importing the 19-test outcome module. Merge glossary/documentation
and historical specification records in later units. Preserve all current
source tasks, product vocabulary and authority. The outcome module plus tests
is 497 lines; record that bounded exception or split review checkpoints without
claiming acceptance before all controls exist. Its pure synthetic seam is not
the public collection comparator. A wholesale branch merge is not qualified.

#28/#29 have no newly established offline defect in this review. Their public,
native, live-provider and confined-install gates remain separate. The
[accepted correction](retros/acceptance-frontier.md) resolves circular holds at
the milestone level after independent review and explicit user approval. No
issue state, GitHub blocker edge or OCI baseline changed; A06 can resume once
actionable defects in completed units are applied and verified.

## Team research and limits

[OpenAI subagent guidance](https://learn.chatgpt.com/docs/agent-configuration/subagents)
supports bounded parallel reads, narrow packets and task-specific model/effort
selection. [Current model guidance](https://learn.chatgpt.com/docs/models)
recommends Sol for complex work and Luna for focused repeatable work. The native
spawn catalog supported all requested combinations. Exact
[Codex source](https://github.com/openai/codex/blob/12cca49c81c8aa6a37a5cc4e39964ee3b70f9458/codex-rs/core/src/agent/child_config.rs#L204)
validates model availability and reasoning levels. Choices here are an informed
allocation, not a speed/cost benchmark or proof of universal optimality.

The scoped native fnox + mise `research-fanout` ran with `--strict-five`, explicit
Last30Days plan and request `0b5c5645-73e5-4757-9e6b-28c76fd8cfe2`; direct rc 1.
The [private manifest](/var/folders/z4/0p475gq56vvczc3y4qlt60f80000gn/T/marketplace-team-parallel-pkocyhm4/research/manifest.json)
and adjacent command/stdout/stderr receipts retain each attempted route.

| Actual route | Result |
| --- | --- |
| GitHub Issues / Discussions via fan-out | Completed, 5 / 1 items. |
| GitHub Releases via fan-out | Process failed: peer cancelled HTTP stream; zero items. |
| Exa via fan-out | Completed, 5 items. |
| Context7 via fan-out | Completed retrieval, 5 items; does not qualify the separate Marketplace SDK bridge. |
| Firecrawl developer via fan-out | Completed, 5 items. |
| Firecrawl Search / Serper fallback | Native HTTP 402; fallback 5 items, explicitly provisional. |
| Last30Days via fan-out and explicit plan | Completed, 5 items. |
| OpenAI Docs MCP | Search and both official pages fetched. |
| GitHub CLI code search / exact source fetch | Both rc 0; source pinned to `12cca49c`. |

**RESEARCH INCOMPLETE:** Releases failed and Firecrawl's search route remains
provisional. No retry or billing action ran. Skills read/applied: Codex team
research, Codex task orchestration, OpenAI Docs and Planning with Files; the
standing ticket retro and writing-for-agents guidance remain in use. Provider
calls came through fan-out; their app/plugin UIs were not directly invoked.

## Applied retrospective

P2 navigation: independent documentation review found the source plan's old
amendment-review link missing. The parent pointed to its verified retained
location and explicitly marked it untransferred. P2 tool economy: the initial
Docker JSON inventory included large labels; the team guide now requests
selected fields, and subsequent output used only counts. Automated checks:
the LSan failure path is covered in the existing suite and independently
reviewed; documentation uses the existing named static/baseline gates and link
inspection. Coding standards: final reviewers retain contract/authority
judgement, with no new mechanical prose rule. Global instructions and no-op
guidance need no change. Information access: source and immutable receipts were
available; provider gaps remain explicit. The acceptance-cycle correction
received independent review and explicit user approval. Its application changes
local scheduling; downstream implementation and runtime gates remain separate.

After the first review, the handoff checkout acquired new portable-package edits
owned by the separate scheduler task. The user explicitly authorized a writer
handoff; its visible ACK confirmed no in-flight repository/Git mutation and
released the common-directory writer slot for this documentation delivery and
the fixed-snapshot feedback-helper integration only. Preserve that task's edits
and return the slot after these two units. A06's next bounded unit is ready by
the completed-unit ledger, but is outside this temporary writer allocation.
