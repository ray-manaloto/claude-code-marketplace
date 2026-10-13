# Reusable research lessons

These twenty rules are transferred from the local lessons ledger. Status describes
the original evidence, not a fresh qualification on this checkout. Private run IDs,
paths, raw artifacts and runtime bindings are intentionally not copied. The source
ledger SHA-256 is recorded in [portable-provenance.json](portable-provenance.json).
Use the shared offline suite for implementation controls and primary sources for
current provider or upstream claims.

| ID | Historical status | Corrective rule |
| --- | --- | --- |
| L001 | validated | Require the actual llvm/llvm-project entry and inspect its source. |
| L002 | validated | Preserve discovery queries and add title-scoped companion queries with relevance anchors. |
| L003 | validated | Inspect the exact branch/commit directly before qualifying version-specific code. |
| L004 | validated | Compare repository/path identities; preserve immutable URLs separately. |
| L005 | validated | Keep separate counters and never delete queries due to one failure or zero-count run. |
| L006 | validated | Enforce at most 10 potential code-search pages per run, serialize runs and leave 65 seconds between batches. |
| L007 | provisional | Preserve blockers, bound identical retries and check repository discussion capability before choosing a control. |
| L008 | validated | Verify repository identity and endpoint before applying a recommendation. |
| L009 | observed | Inspect exact installed source before enabling cache, retries or throttling changes. |
| L010 | validated | Follow URLs actually present in source/search results instead of inventing issue numbers. |
| L011 | validated | Read next_allowed_at immediately before starting a candidate. If still active, defer until normal expiry or a later refresh; never change the guard or timestamp to proceed. |
| L012 | observed | Inspect the actual command and surrounding source before promoting a code-search hit as an example. Preserve ranking changes as window changes and exclude irrelevant examples without deleting the broad search. |
| L013 | validated | Keep repository/path identities for search comparisons, but group byte-identical source files when selecting examples and do not count them as independent implementation evidence. |
| L014 | validated | Keep prior nonempty history, mark sudden empty results unverified, block candidate promotion, and distinguish subsequent recovery from genuinely new items. Preserve native receipts and earlier snapshots. |
| L015 | validated | Record the failed route and use the existing system curl with normal TLS verification for optional public-source capture; inspect successful receipts before reading or promoting examples. Do not install or alter shared runtimes. |
| L016 | validated | Preserve native exit/stderr and record a failed attempt separately from the last accepted snapshot. Do not change query history, catalog, pins or shared runtimes, and do not loop launch retries. |
| L017 | validated | Resolve the merged implementation or timestamped draft head and inspect its source before recording configuration names or behavior. Distinguish merged source from released or installed capability. |
| L018 | validated | Use the existing full unittest discovery command after runner or runtime-check changes, and record its actual exit and test count. |
| L019 | observed | Apply the existing retro step before every cycle report, recording finding dispositions and verification evidence. |
| L020 | observed | Start with receipt and metrics summaries; inspect response and comparison details by selected search ID while retaining full evidence on disk. |

L001–L003, L008, L010, L012–L013 and L017 include historical source/relevance
judgments; verify applicability at the selected source revision before reuse.
L007 remains provisional because substitute-provider results do not establish
native provider coverage. L009 does not authorize changing a borrowed client.
L014/L016 preserve failed/empty history and are represented in the transferred
runner controls. L018 was validated by the prior 80-test private discovery run;
new shared test counts and exits belong to this publication receipt.
L019/L020 are observed process corrections. Neither future scheduled compliance
nor measured performance savings is claimed.

The latest source-name correction was checked against the merged implementation
of [mise PR 13980](https://github.com/jdx/mise/pull/13980); draft findings remain
tied to their inspected heads. Publication does not qualify installed binaries.
