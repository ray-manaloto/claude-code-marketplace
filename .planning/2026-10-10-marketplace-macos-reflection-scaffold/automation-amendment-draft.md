# Spec #11 automation amendment and first ticket frontier

Status: user-approved local breakdown, unpublished; A01–A05b and A09 implementation, review and branch publication complete at `93bb798b`. This amendment preserves
the existing spec and 50 sub-issues. The twelve clarified decisions are settled;
the original fourteen-ticket granularity and blocking edges were approved on 2026-10-12. Retrospectives split A12 and A03 into bounded slices; this local amendment is not published. It is the first
frontier of the broader modernization, not a replacement for the remaining core,
adapter, diagnostic, telemetry or acceptance work.

This document is the interim local index: the original fourteen slices were
**approved for bounded implementation**, with no GitHub IDs yet. The Codex parent
owns implementation in the worktree named by the selected plan. W5 holds new
claims on the original implementation frontier; receipts for #12/#24/#25 remain
valid historical work. Record each local slice's state, exact
maintained files, input hashes and review before starting it. Keep units near
five maintained files/300 handwritten lines. There is no manual commit or issue
publication exception while the named delivery tasks are being built.
The A01 runtime repair, A02 one-page receipt and A04 catalog recorder passed
local implementation, test and review. Their [retrospective records](retros/)
amend the remaining frontier. A01–A05b and A09 are published on the branch;
the #11 amendment, new ticket identities, source-checkout transfer and hosted
CI qualification remain separate gates.

## Accepted prerequisite correction — 2026-10-13

The user approved the independently reviewed
[acceptance-frontier correction](retros/acceptance-frontier.md). A06 may resume
once actionable defects in completed units are applied and verified; blocked
future native/provider/OCI acceptance holds only the work that depends on it.
A12b still depends on A06's own gate. A bounded #28 baseline-transition design
and review may proceed before A06/A12b assembly; applying a changed baseline
still requires explicit versioned review and preserves the original receipts.
After source integration and its own checks, #28's reviewed offline v2
dispatch/help/isolation milestone may satisfy that specific #30 prerequisite.
Other #30 native/schema/transport prerequisites remain. #28 stays partial/open
until public v2 and fresh Claude/OCI acceptance. #29's reviewed offline bridge
measurement informs dependent design only; live and confined-install gates stay
pending. Existing GitHub ticket-level edges require separately qualified
amendment before they represent these narrower milestones.

## Problem Statement

Many foundation operations exist only as host-specific scripts or manually
assembled commands. Humans, CI and different coding agents cannot reliably run
the same workflow with the same arguments. Useful saved-search behavior is split
across three projects, and only one currently uses GitHubKit. This encourages
repeated research and hides the difference between empty, partial and failed
queries. The current branch also remains in a worktree despite the requested
publication and return to the source checkout.

## Solution

Make shared mise tasks the executable project interface, backed by small reusable
libraries and thin host-specific skills. Establish a project-owned, locked
GitHubKit search/replay capability first, use it to research actual Codex
release-schema examples, then expose reviewable issue and Git delivery operations
through the same interface. Continue the larger amendment using that research
capability instead of designing more build tooling from ad hoc commands.

## User Stories

1. As a human, agent or CI runner, I want the same task names and arguments to produce the same records and exits without user/global mise configuration.
2. As a maintainer, I want minimal Python support and dependencies declared and locked locally while C++26 remains the final shared core.
3. As a researcher, I want reusable saved GitHub queries and exact effective-query records so updates do not require reconstructing earlier work.
4. As a researcher, I want unexpectedly empty results checked through a bounded known-result query so a broken API is not reported as an answered null.
5. As a reviewer, I want failures, partial pages, rate limits and incompatible comparisons to remain visible without false NEW/GONE claims.
6. As a maintainer, I want immutable, hash-bound run records and atomic publication so interrupted or concurrent runs cannot overwrite evidence.
7. As an agent maintainer, I want examples of release-pinned Codex schema use, checked against primary source, before choosing the schema integration.
8. As a contributor, I want reviewed issue amendments and Git delivery to run through repeatable tasks with explicit targets and preconditions.
9. As the repository owner, I want the requested branch pushed and source checkout selected without losing untracked handoffs or retained build artifacts.
10. As a successor agent, I want exact task invocations, ownership, receipts and remaining blockers so a context or subscription change does not restart work.

## Implementation Decisions

- Reuse TR's small SDK boundary, dotfiles' replay/control safeguards
  and knowledge-base's strict outcome distinctions. Avoid copying whole packages
  or known donor defects. Preserve provenance and any required attribution.
- Use project-declared tools, a locked Python environment and native mise deps.
  An explicitly named dependency-sync operation may install project requirements;
  checks/searches use the lock and never silently update it. Existing qualified
  compiler identities remain historical inputs until portable equivalents pass.
  The development configuration remains separate from frozen Linux OCI inputs;
  initial local portability checks do not establish hosted CI acceptance.
- Use one public task/CLI seam for live and replay modes with the same request
  contract. Isolate network transport behind a small SDK boundary. Credentials
  are injected by native fnox or the CI secret environment; never accept a token
  in CLI arguments or serialize it into requests, logs or artifacts.
  Offline replay must work with the credential provider unavailable and network
  transport forbidden. Live authentication occurs only after local validation;
  do not copy an unconditional task-level secret mapping from a donor.
  Qualify an existing native fnox profile (the inspected donor uses
  `codex_publish`) or CI environment without printing secrets or inferring
  absence from inherited environment variables. Provisioning remains separate.
- Raw replay input is HTTP status, allowlisted response headers and body bytes,
  with safe method/endpoint/query metadata, never credential/request headers.
  Feed it through the same SDK transport/normalization boundary. Use stable
  repository/path/blob identities; retain missing versus null and duplicate counts.
- Separate full, partial, failed, verified-empty and unverified-empty outcomes.
  Search result totals and collected-item counts are distinct. SDK missing/UNSET
  fields, API incompleteness and truncation are represented explicitly.
  Full requires exhausted admitted collection, consistent counts and no error,
  incompleteness or binding limit; it does not claim a snapshot of all GitHub.
- Compare only complete compatible observations of the same effective query and
  collection criteria. Fingerprints cover endpoint, exact query, sort/order,
  API/normalization versions, per-page and page/item/time limits. Catalog/SDK/code
  revisions are provenance, not automatic incompatibility. Subset reruns retain
  other queries' last-good observations; first observations establish a baseline
  without NEW/GONE. Verified-empty means a working capability returned zero,
  not proof of nonexistence; controls never enter the compared item set.
- A04 owns catalog/control definitions and immutable manifests. Validate the
  catalog and selected baselines before credentials/network. Distinguish active,
  interrupted, orphan and corrupt records; report unfinished/unselected records
  without treating them as baselines. Invalid catalog/selected baseline refuses.
  An explicit named quarantine operation appends a hash-bound exclusion and
  reason without rewriting/deleting evidence; the next observation has no delta
  baseline. A02 standalone captures are identified separately from catalog runs.
  Allocate run directories exclusively, publish the manifest last, and derive
  latest comparable results from immutable manifests with deterministic ordering.
- Disable SDK automatic retries. The task owns bounded read retries and records
  every attempt, primary/secondary limits and exhausted budgets. Mutation calls
  get one send after a durable intent record; unresolved intents block reapply.
  Post-write reads distinguish expected postimage, unchanged preimage and drift;
  read-before-write checks do not claim atomic protection against other editors.
  Stable plan/local-ID markers identify issues separately from approved content
  hashes. Resolve ambiguous creation with bounded paginated repository/parent
  listings; search-index absence or incomplete/not-found lookup never permits a
  second POST. Report UNRESOLVED for owner resolution when verification cannot.
- Keep issue publication and Git delivery explicit mutating operations. Bind
  exact repository, branch/HEAD, approved inputs and current preimages. Preserve
  explicitly inventoried handoff/artifact paths; refuse unexpected dirt, drift,
  checkout collisions, destinations and ambiguous retries. No
  force-push, merge, deletion or marketplace publication is included.
- Preserve the original acceptance receipts. Intentional compatibility changes
  get versioned baselines and behavior checks in the subsequent amendment.
- Bootstrap tickets use stable local IDs until the approved publisher exists;
  it then records their GitHub sub-issue identities and actual implementation
  state. This avoids bypassing the newly required mise execution contract.

## Testing Decisions

Test the named task/CLI output, exit code and artifacts rather than private
functions. Deterministic offline fixtures cover hit/empty/control failure,
missing/UNSET fields, pagination/truncation, rate limits, auth errors, timeout,
corrupt data, incompatible fingerprints, subset reruns, interrupted writes and
two concurrent recording processes. Verify first-baseline and hit/verified-empty
transitions, changed limits versus unrelated catalog additions, and controls
skipped for exhausted budgets. Quarantine preserves every original byte.
Prove public-task replay succeeds without credential lookup or network activity
using a failing fake credential provider and forbidden transport; apply the same
zero-call checks to invalid live inputs. Replay a redacted real capture through
the SDK boundary and preserve every pre-existing evidence file's hash.
One bounded live schema-example search validates the real SDK/credential path;
the live result never substitutes for those deterministic controls.
Use an isolated configuration environment to prove portability while preserving
the real HOME. Native Git/issue tasks need scratch/offline refusal and recovery
controls before the explicitly authorized real operations. Retain original-file
checks, actual exits and independent review for each small unit.

## First dependency-linked tickets

1. **A01 — Portable locked task bootstrap.** Blocked by: none. Named tasks
   `tools:prepare`, `deps:lock` and `deps:sync` prepare the declared tools,
   create/refresh the reviewed lock and synchronize project dependencies.
   Humans and CI then run the same lightweight checks with user/global mise
   configuration excluded. Lock GitHubKit; normal tasks refuse missing/stale
   environments and never silently sync. Demonstrate lock-drift refusal and
   unrelated-cwd invocation without changing global settings. Record latest-stable
   discovery and locked tool identities, use `com.rsm` package conventions, and
   preserve all 19 baseline hashes plus root OCI mise files. Hosted CI
   qualification and migration of old operational calls remain owned by A12b.
2. **A02 — One-page GitHubKit search receipt.** Blocked by: A01. A named task
   makes one bounded code-search request and equivalent offline fixture and
   retains raw plus normalized output. Include effective query, safe credential
   handling, stable item identities, SDK missing/UNSET fields and honest partial
   or error status. Verify one request on a simulated 5xx with SDK retries off,
   credential-route presence and one bounded real capture. A one-page result is
   not automatically exhaustive. This research/ops task adds no plugin verb and
   does not replace the native Issues schema/transport decisions in #26/#27/#30.
3. **A03a — Bounded collection and attempt recording.** Blocked by: A04.
   The same named task collects within explicit page/item/time limits and
   records every page, retry, truncation, timeout, primary/secondary limit and
   HTTP error. Each attempt retains A02 status, allowlisted response headers
   and exact body bytes/hash through the SDK boundary. Public offline 5xx and
   redirect controls verify one request per attempt; API caps, drifting totals
   and duplicate pages stay incomplete. Settle test/review/retro before controls.
4. **A03b — Controlled empty and completeness verdicts.** Blocked by: A03a.
   Unexpected empties use the agreed same-capability known-result check.
   Catalog controls bind scope and expected minimum; record passed, failed or
   not-run with reason and charge them to the same request/time budget. Fixtures
   prove failed controls yield unverified results, exhausted budgets remain
   visible, and incomplete runs cannot become full successes. Reuse A03a's
   private-result withholding, HTTP envelope capture and post-capture timeout
   behavior for each control. Keep control/verdict logic in a separate module.
   The public task
   retains control HTTP envelopes and makes no NEW/GONE comparison yet.
5. **A04 — Validated catalog and immutable recording.** Blocked by: A02. A
   saved query catalog can be validated and recorded through a named task.
   Reject malformed, path-unsafe/case-colliding IDs and invalid selected records
   before auth/network; own query/control definitions and fingerprint encoding.
   Publish hash-bound manifests last with collision-safe run IDs. Include the
   explicit append-only quarantine path above. Concurrent/interrupted fixtures
   preserve old bytes and produce deterministic baseline selection.
6. **A05a — Compatible baseline and pure comparison.** Blocked by: A03b, A04.
   Select each query's latest complete compatible observation without rewriting
   old runs. Verify hashes again after A04's selected-record preflight; honor the
   quarantine reset barrier, exact fingerprint and a new A03b normalization
   version. Only final `complete` or `empty_verified` status with passed controls
   is eligible; an A03a collection candidate is insufficient. First observations
   establish a baseline without NEW/GONE. Partial, corrupt or incompatible
   observations suppress deltas. Test transitions, limits and unrelated catalog
   additions with scratch immutable records before public rerun wiring.
7. **A05b — Public rerun and comparison receipt.** Blocked by: A05a.
   Rerun all or selected saved queries through named tasks and deterministic
   offline fixtures without rewriting the catalog or old runs. Bind comparisons
   to the selected baseline and new immutable observation. Qualify concurrent
   writers with a per-query lock shared by reruns and quarantine, covering
   preflight, collection, record and comparison publication. Exercise two
   writers and a quarantine race; drift yields unresolved, never a stale delta.
   Each row of an all-query rerun is admitted independently: a later invalid
   row is unresolved before its own credential lookup or network call, while
   earlier successful row receipts remain immutable. An invalid selected
   baseline refuses before its live credentials/network; diagnostic replay
   may describe corrupt data but emits no comparison. Verify subset reruns keep
   other queries' last-good observations and that the public output/exit/artifact
   contract distinguishes baseline, compared, suppressed and unresolved states.
8. **A06 — Codex release-schema example receipt.** Blocked by: A05b. Saved
   GitHubKit queries capture actual usage examples; exact-release official
   config schemas and installed hook contracts resolve validity. Record pinned
   source identities, limits and failed/empty routes. Fetch bounded full blobs
   by SHA and the exact official release schema asset; record their digests,
   repository/path/blob identities, fork provenance and duplicate blobs.
   The retained codex-schema live search is partial (10 of reported 898 with
   `item_limit`): identified blobs may be examined, but example coverage is
   provisional and no full-inventory or NEW/GONE claim follows from it.
   Classify fetched examples with the actual validation/inspection method;
   unavailable validators yield UNVERIFIED, never inferred validity. SDK blob
   retrieval here is a research helper, separate from native operation #35.
   New validator tooling belongs to A12b; no global Codex configuration changes.
9. **A07a — Qualify one-issue amendment operations.** Blocked by: A04. A
   named GitHubKit task previews, applies and verifies an exact body/label
   update using recorded preimages, allowlisted fields and write-ahead intent.
   Offline controls cover drift, 5xx/timeout after application, process death
   after send, exact normalization and verify-only recovery with no second write.
   Reject state/close operations. Add only the qualified edit-task guidance.
10. **A07b — Apply the approved spec #11 amendment.** Blocked by: A07a. Freeze
   the approved body and labels, obtain a fresh preview and apply through the
   qualified task; retain postimage verification or unresolved status. Preserve
   the original spec/receipts and do not close #11. No extra production mutation
   is required merely as a rehearsal; a read permission is not write acceptance.
11. **A08a — Publish and bind ticket identities.** Blocked by: A07b. A named
   task creates the approved sub-issues with stable markers and local-ID mapping,
   parent links and planned-state labels. Verify locked SDK endpoint support,
   numeric IDs versus issue numbers and native limits before applying. Test
   ambiguous creation before/after parent attachment and interrupted resumption;
   never automatically repeat a POST. Withhold ready labels until A08b verifies
   the graph; preserve original issues and existing local-ID bindings.
12. **A08b — Verify and publish dependency relationships.** Blocked by: A08a.
    Apply approved blocker/label relationships for new and waiting existing
    tickets, verify the full map and replace create/edge guidance with qualified
    tasks. Partial graph publication remains explicit and resumable. Reconcile
    actual local/remote implementation state from receipts; no automatic closure
    follows from issue creation or a push. A12b owns any additional close workflow
    needed for #12/#24/#25, gated by their acceptance and A09's publication receipt.
13. **A09 — Reviewed commit and branch publication.** Blocked by: A01. Named
   tasks verify selected changes, checks and Git identity, create a local commit
   and push the exact authorized branch. Secret scanning covers the complete
   outbound commits/blobs and evidence, including a secret added then deleted.
   Derive the set from fresh remote refs; for an absent branch scan all target
   ancestry unless remote presence is proved. Bind HEAD, reviewed tree, remote
   identity, explicit SHA/refspec and active writer root; reject detached HEAD,
   drift, unexpected hook edits, failing checks and force-push. Keep Git secrets
   out of argv/logs and reject unsafe tracing. Scan failure stops for owner
   resolution without rewriting history. Verify the exact remote commit.
14. **A10 — Reviewable checkout-transfer plan.** Blocked by: A09. A named task
    inventories exact source/worktree preimages, approved untracked handoffs,
    retained ignored artifacts, collisions and branch ownership. It emits an
    apply/recovery plan bound to the pushed commit without switching checkouts.
    Declare the post-transfer writer root and prove the session can execute
    there. Collision checks include target tracked paths against ignored and
    untracked files, symlinks and parent directories. Classify path-dependent
    retained artifacts and current guidance; do not rewrite historical receipts
    or silently rebuild missing artifacts. Scratch controls prove refusal.
15. **A11 — Apply and verify source-checkout transfer.** Blocked by: A10. The
    named task rechecks the approved plan, detaches the retained old worktree
    and switches the source checkout to the published branch. Verify exact
    preimage preservation, non-destructive recovery, refreshed handoffs and
    actual subsequent named checks and an A09 handoff-update commit from the
    source root, including all 19 baseline hashes. Reject later mutation from
    the inactive/detached worktree. If source-root operation cannot be proved,
    retain or recover the prior binding and report transfer incomplete; never
    delete/reset either checkout. App navigation alone is not execution proof.
16. **A12a — Qualify the portable fast-check and hosted CI route.** Blocked by:
    A01, A02, A09. `check:research` is the local fast check and already exits 0 with
    bootstrap, offline SDK/catalog controls and the 19 original hashes. Inspect
    `.github/workflows/acceptance.yml` and the host/container admission before
    wiring a separate lightweight job on the published branch; qualify a fresh host with explicit
    prepare/sync and no global mise or secret assumptions. Retain CI run/exit
    evidence. This is pending hosted acceptance, not an existing CI pass.
17. **A12b — Assemble the remainder amendment.** Blocked by: A06, A08b, A12a. Using
    bounded saved-search receipts and the settled requirements, draft the
    remaining graph changes for portable C++ builds, latest locked tools and
    packslip skills, hk checks, schemas, diagnostic matrices, caches, profiling,
    structured/redacted telemetry defaults, shared collector integration and
    host enforcement. Explicitly route versioned baseline transitions (#28),
    existing Python/CMake call migration, CI expansion beyond A12a, evidence migration,
    issue closure/state reconciliation and per-unit handoff refresh. Map the ops
    contract to future native reuse without repurposing the Issues schema.
    This is assembly/review only: no new implementation or host mutation. Reuse
    existing tickets and preserve completed receipts and original issue IDs.

These edges express technical prerequisites. Independent ready tickets may run
concurrently in separate Git worktrees with disjoint file scopes and separately
admitted host resources. The parent owns the plan and integration branch and
merges one reviewed ticket at a time. The next local research gate is
A05a, then A05b and A06. A07a/b and A08a/b are the separate issue-publishing
lane; A09–A11 are the Git and checkout-transfer lane. A09 is also a prerequisite
for hosted A12a, since an unpublished branch cannot produce the claimed hosted
CI receipt. A12b waits for research, issue graph and hosted qualification.
Issue #13 remains host-heavy and unqualified; #26/#28/#29/#30 retain their
original native-schema/bridge gates. Every later operation uses the same task
interface, and each completed slice now has a retrospective gate.

## Out of Scope and continuing scope

This frontier does not implement the entire sanitizer/platform matrix, change
shared host settings or start a collector. Those remain requested work with
separately reviewed ownership/admission units. The accepted collector directory
is local state, per service/project, with rotation and configurable retention
defaulting to 30 days; one shared Mac collector belongs to global mise.
Native hooks cover supported host calls, guard agents review submitted/visible
batches, and CI verifies task behavior. Codex hosted tools and later terminal
input are not guaranteed to be intercepted; unqualified hosts remain UNVERIFIED.
Private-document updates, SBE/firmware work, paid-provider purchases, credential
changes, automatic merges and marketplace releases remain excluded.
The existing native-core, adapter and acceptance tickets remain active; none
is closed or considered superseded merely by publishing this amendment.
