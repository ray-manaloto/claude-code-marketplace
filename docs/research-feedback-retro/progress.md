# Research feedback sharing retrospective

Owner: this isolated retro worktree. Base: `b136d75f6809a53381de0dfba1fd61da8e705796`.
Protected peer: `01a130ef-265d-72b0-8465-80f3e4128bee`; its checkout,
branch, active plans, draft specifications and runtime are not changed here.

## Unit 1: offline feedback guard

Implemented a portable, dependency-free development helper, regression controls,
an explicit mise replay/check task and integration with the existing check command.
No live runner, transport, credentials, catalog, private learning state or cadence
is copied or changed. The peer already owns unified GitHub search implementation;
this unit shares a bounded feedback component for that work.

Actual gates in this worktree:

- `./dev/mise tasks validate`: exit 0, four tasks.
- `./dev/mise run check:research-feedback`: exit 0, 12 offline tests after repair.
- `./dev/mise run check:acceptance-baseline`: exit 0, all 19 originals preserved.

Independent read-only review found a replay envelope mismatch that could reset
nonempty history. Fixed it and added a chained CLI regression; re-review cleared
the finding. Unit 1 is reviewed and tested, ready for a local commit.
Committed locally as `7d0c2fd`; it is not published. The private runner's earlier live batch
preceded its guard patch; these offline tests do not prove scheduled execution.

## Unit 2: discoverability and CI

Implemented input/output and integration boundaries, a short onboarding pointer,
and a lightweight CI workflow using the existing check entry point and the
existing checkout action pin. No installation or provider call is added.
Final baseline gate exited 0 with all 19 original hashes and 12 tests. Independent
static documentation/CI review found no findings. Both small units are complete
locally; Git history identifies their commits. Hosted CI is unverified.
The peer integration message supplies exact local commits and warns that its
concurrent `mise.dev.toml` changes need reconciliation. Its draft GitHub library
can reuse the feedback helper without adopting a second live-search runner.
No push or merge is planned. Parent plans and private research state are untouched.

# Refresh improvement workflow — 2026-10-12

The user confirmed comparison-failure baseline/history preservation, exact borrowed
runtime preflight before credential/provider launch, and sanitized shared outcome
behavior tested at the runner boundary. Three local specs and the RF1/RF2/RF3
ticket draft are prepared; ticket approval is pending. Glossary records the agreed
domain distinctions. No implementation or tracker publication occurred in this phase.
The protected peer's shared plan remains unchanged. A01/A05b overlaps are recorded;
qualified A07/A08 publication operations remain unavailable. Hook-requested research
fanout completed with native exit 1: GitHub Discussions canary-empty/unverified,
Context7 process-failed, and Firecrawl Search substituted by Serper after exhausted
credits. Exa, Last30Days and the other GitHub routes ran. Research remains incomplete;
the exact manifest is retained under the hook's request directory.

The user requested a Fable adversarial review before approving the ticket graph.
Installed Claude Code 2.1.296 advertises the `fable` alias. The claude-agent skill's
shared dispatcher launched one read-only safe-mode review with Read/Glob/Grep,
no subagents, no fallback model and a 600-second limit. Review disposition is
pending. The static baseline check exited 0 with all 19 original hashes intact;
diff whitespace also passed. No implementation, commit or publication occurred.

Fable completed: observed `claude-fable-5-1`, native/wrapper exit 0, completed
AgentReport, local schema validation passed. It reported 4 high, 7 medium, 3 low
and 1 informational findings. Source verification confirms missing transition,
baseline migration, binding, write-order and ownership details. Its claim that
stale-manifest failure was observed live is narrowed: the cited old failure was
native exit 1 with invalid stdout, before the current patch. Its proposed rule
accepting unverified empties as comparison baselines conflicts with the shared
coverage contract; that correction is surfaced for the user's decision.
Specs now draft bounded corrections and verification cases. RF3 split, coverage
acceptance and preflight pin/cooldown choices remain pending. Changes are not
implemented or re-reviewed; no review finding is claimed closed by a spec edit.

The user approved all three post-review choices: separate coverage observations
from comparison eligibility; RF3a/RF3b split; SDK pin enforcement with unchanged
cooldown before provider launch. Four per-ticket local records now exist. A fresh
focused Fable re-review is running on the revised contracts. RF1's managed worktree
and a frozen private scratch copy are prepared; implementation has not started.
Installed mise help confirms `--no-deps` skips automatic dependency providers.

Focused Fable re-review completed with native exit 0 and schema validation passed:
no high blockers, four medium and three low clarifications. These now specify
attempt/comparison statuses, admission evidence, pre-launch cooldown metadata,
fail-closed migration recovery, latest-observation metadata, policy pin location
and RF3b serialization. The reviewer explicitly requires no further spec-level
re-review before implementation; implementation/retro review remains mandatory.
