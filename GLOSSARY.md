# Marketplace research domain

The marketplace exposes one shared research behavior through host-specific
interfaces. These terms keep research evidence and coverage distinct from
the route used to obtain it.

## Language

**Research operation**:
A typed research request and corresponding result for one named action, such
as GitHub issue search or Context7 documentation query. An operation is not
a host-specific plugin command.

**Research plan**:
The declared capabilities, corpora, source standards, freshness, limits and
fallback rules that a research run must satisfy.

**Provider**:
A named external service or tool that supplies a research operation, such as
Exa or Context7. A provider is not necessarily an independent upstream.

**Route**:
The concrete access path used for an operation, including a primary endpoint
or a fallback. Distinct routes can reach the same corpus or upstream.

**Upstream**:
The publisher or independently originating source of material returned by a
route. Two routes do not create two upstreams when they surface the same source.

**Corpus**:
The underlying collection of material searched by a route. Providers can
share a corpus even when their APIs and response formats differ.

**Artifact**:
An immutable captured response or source item retained with its provenance
to support a research result or claim.

**Coverage verdict**:
The plan-level judgment of whether the required capabilities and source
independence were met. It is separate from a process exit or route status.

**Host adapter**:
A thin host-specific registration and invocation surface for the shared core.
It does not define independent research semantics.

**Core library**:
The one library that holds the shared research behavior. Every host adapter and bridge reaches it
and none defines research semantics of its own.
_Avoid_: Backend, Python core

**Bridge**:
A thin surface that lets code in another language, such as a mod or a development tool, pass a
request to the core library and relay its result unchanged. It holds no logic of its own.
_Avoid_: Wrapper, shim

**Refresh attempt**: One bounded attempt to obtain and compare current research observations.
_Avoid_: Successful run when its comparison has failed

**Raw snapshot**: Retained observations from a provider operation, before acceptance for comparison.
_Avoid_: Accepted baseline

**Accepted comparison baseline**: A retained compatible observation eligible to anchor a later comparison. An unverified empty observation cannot be such a baseline.
_Avoid_: Latest snapshot

**Query history**: Coverage observations associated with a compatible query identity, including explicit coverage warnings. This history is distinct from comparison-baseline eligibility.
_Avoid_: Attempt history

**Failed-attempt receipt**: Evidence of an unsuccessful refresh stage, its actual outcome and the retained prior acceptance state.
_Avoid_: Success receipt

**Borrowed runtime**: An existing execution environment owned outside this refresh workflow and used without modification.
_Avoid_: Managed refresh runtime

**Coverage warning**: An observation's unresolved completeness or validity, retained without certifying a content change.
_Avoid_: Accepted content change

**Comparison failure**: An attempt that cannot complete the comparison operation or verify its evidence.
_Avoid_: Empty result

**Attempt status**: The outcome of a refresh's processing and evidence checks, distinct from whether its observations qualify for content comparison.
_Avoid_: Comparison status

**Unavailable borrowed runtime**: A borrowed execution environment that fails the refresh's required identity or import checks.
_Avoid_: Provider outage

## Workflow

**Unit**: One bounded piece of work with a single purpose, small enough for one writer and one review, planned, implemented, tested, reviewed, retro'd, integrated and published as separately recorded states. A ticket is a unit with a tracker identity; a unit may also be a plan or documentation change.
_Avoid_: Task, chunk

**Lane**: The allocation of one unit to one writer in one worktree on one branch, with an explicit path allowlist, a reviewer, a base commit and a status. Lanes run in parallel only when their allowlists are disjoint.
_Avoid_: Stream, track

**Integration tip**: The current commit of the integration branch. A lane reconciles the tip into its branch before handoff; the merger integrates one lane at a time onto it.
_Avoid_: Latest main

**Merger**: The role that verifies a lane's changed paths stay inside its allowlist, checks its gate evidence and integrates it serially. It is distinct from the writer and the reviewer of that lane.
_Avoid_: Releaser

**Gate**: A named check whose actual exit code must be recorded before a state advances. A static gate never stands in for runtime, provider, fresh-session or container acceptance. The plan's order row named "gate" (Phase 4b) is the pre-publication step, not a check.
_Avoid_: Quality bar

**Frontier**: The set of open tickets whose blocking edges all point at tickets with accepted dispositions. It is recomputed from the live tracker graph, never from a closed issue alone.
_Avoid_: Backlog, ready list

**Retro barrier**: The rule that a unit's next product task and its dependency successors stay held until every actionable retrospective finding is applied, checked and independently reviewed or rejected with evidence. Independent lanes continue.
_Avoid_: Freeze

**Receipt**: An immutable record binding a command, its exact inputs (paths, revisions, hashes), its actual exit code and the identity of what ran. Receipts are cited, never paraphrased into success.
_Avoid_: Log, report

**Admission**: An explicit, recorded permission for an operation that consumes shared or host-heavy capacity, mutates global state, publishes or calls a paid provider. A previous receipt does not grant a new admission. A standing admission grants a bounded class of them.
_Avoid_: Approval, clearance

**Standing admission**: An admission for a named class of operations under stated bounds (one at a time, an order, a resource gate), or with no bounds where the user chose none, recorded once and revocable; each use still records its own receipt.
_Avoid_: blanket approval, pre-approval

**Split unit**: The part of a ticket that can run without a heavy admission, allocated as its own lane; the ticket stays open until its heavy part integrates.
_Avoid_: offline portion, offline half

**Wave**: One step of the plan's order table: the units that may start once the earlier steps' blockers are accepted. A wave is an ordering, not a time box; the C++ lane keeps its own queue beside the waves.
_Avoid_: sprint, phase

**Mod**: An extension Claude Code loads into a session that acts on session, prompt and tool events and can answer a tool call itself. This repository's extension point for its own workflow rules, except the three deny gates, which stay settings hooks, and Git events, which hk Git hooks handle.
_Avoid_: settings hook (the mechanism mods replace here), plugin hook

**Deny gate**: A check that can refuse a tool call or the end of a turn. This repository keeps its deny gates as settings hooks, because a mod can be switched off remotely.
_Avoid_: guard, blocker

**Source project**: Another repository whose agent-workflow features and collected research this repository absorbs, as improved designs, before that repository is sunset. Its code is read, never copied; it is edited only under an outward admission (its sunset ticket, or a paired change such as the host-lock repoint).
_Avoid_: legacy repo, upstream (an upstream is the origin of research material)

**Sunset**: Retiring a source project once every item on its checklist has a landed ticket here.
_Avoid_: archive, deprecate
