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

**Unit**: One bounded piece of work with a single purpose, about five maintained files and 300 handwritten changed lines, planned, implemented, tested, reviewed, retro'd, integrated and published as separately recorded states. A ticket is a unit with a tracker identity; a unit may also be a plan or documentation change.
_Avoid_: Task, chunk

**Lane**: The allocation of one unit to one writer in one worktree on one branch, with an explicit path allowlist, a reviewer, a base commit and a status. Lanes run in parallel only when their allowlists are disjoint.
_Avoid_: Stream, track

**Integration tip**: The current commit of the integration branch. A lane reconciles the tip into its branch before handoff; the merger integrates one lane at a time onto it.
_Avoid_: Latest main

**Merger**: The role that verifies a lane's changed paths stay inside its allowlist, checks its gate evidence and integrates it serially. It is distinct from the writer and the reviewer of that lane.
_Avoid_: Releaser

**Gate**: A named check whose actual exit code must be recorded before a state advances. A static gate never stands in for runtime, provider, fresh-session or container acceptance.
_Avoid_: Quality bar

**Frontier**: The set of open tickets whose blocking edges all point at tickets with accepted dispositions. It is recomputed from the live tracker graph, never from a closed issue alone.
_Avoid_: Backlog, ready list

**Retro barrier**: The rule that a unit's next product task and its dependency successors stay held until every actionable retrospective finding is applied, checked and independently reviewed or rejected with evidence. Independent lanes continue.
_Avoid_: Freeze

**Receipt**: An immutable record binding a command, its exact inputs (paths, revisions, hashes), its actual exit code and the identity of what ran. Receipts are cited, never paraphrased into success.
_Avoid_: Log, report

**Admission**: An explicit, recorded permission for an operation that consumes shared or host-heavy capacity, mutates global state, publishes or calls a paid provider. A previous receipt does not grant a new admission.
_Avoid_: Approval, clearance
