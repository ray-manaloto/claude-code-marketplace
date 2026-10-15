# Context7 bridge measurement (ticket #29)

**Disposition: historical offline bridge behavior qualified; ticket #29 remains
PARTIAL/OPEN and #40 held.** Keep the existing remote Context7 MCP route.
For a future local adapter, use a pinned stdio helper as the reversible seam:
send MCP `initialize`, then `resolve-library-id` or `query-docs`; retain tool
content, whether `isError` is present, transport/protocol failure and source
identity separately. In installed 4.3.0, `query-docs` sets `isError=true` for
HTTP 429, but `resolve-library-id` returns the quota message as ordinary text
without `isError`. For this pinned version, accept a resolve result only when
its single text block begins `Available Libraries:`; treat every other shape
as **non-success** and stop. This does not distinguish quota from not-found,
so a later adapter needs a stronger structured upstream status contract.
Do not translate a quota error into empty documentation. A direct JavaScript API
import is a comparison control, not a C++ embed or a public SDK contract.

The prerequisite is ticket [#25](../../evidence/python-bridge/ticket25-review.md),
whose reviewed helper-process decision preserves the existing plugin route. Its
probe, decision and measurement SHA-256 values match that review. Ticket #25's
local commit is `54d34c8b8d5636614f772f628e705f9eb93c5ac6`; the GitHub issue
remains open. The retained ticket started from local HEAD
`6130ab5e9298e4c70d8c39a0ebd3c6857458c5c5` in an isolated worktree.

The historical installed candidate was `@upstash/context7-mcp@4.3.0` from an existing npm
cache, with Node v26.8.1. The npm lock entry pins the registry tarball at
`sha512-fuDt5nWjE5JkAPLjU0m+m0LlJphxyegAvAmcwHoA5jrzAhKo/rVV0RFA8TOwODGdDVdt/nPxNslkxeDIDp/rPA==`.
The [official release](https://github.com/upstash/context7/releases/tag/%40upstash/context7-mcp%404.3.0)
names tag `@upstash/context7-mcp@4.3.0`, observed at commit
`522c4db4fa2e1e31f1b320f09fa8c8fab376987a`. The local package manifest,
entry and API module hashes are bound in the [measurement](../../evidence/issue-29-context7/measurement.json).
The package's [own API guide](https://context7.com/docs/api-guide) maps the two
MCP tools to `/api/v2/libs/search` and `/api/v2/context`, and documents HTTP 429
for rate limits. The installed source uses these endpoints and maps a failed
`query-docs` response to MCP `isError=true`; its resolve handler does not make
that guarantee for failed upstream search.

The historical [probe](../../dev/context7_bridge_probe.py) used only a local loopback
fixture. It compared three alternating cold one-shot direct JS module calls
with three cold local MCP stdio child calls for the same search fixture. Median
elapsed times in the final run were **102.675 ms direct** and **183.628 ms MCP**.
Direct and MCP calls to each tool then received fixture HTTP 429 with `fixture
quota exceeded`. Direct JS reported error for both calls; MCP `query-docs`
returned `isError=true`, while MCP `resolve-library-id` omitted `isError` and
returned only the error text. The fail-closed classifier marks that response
`non_success`. All ten expected fixture requests were observed; the probe
exited 0. Under `python -O`, a positive replay exited 0 while a deliberately
faulted search fixture exited 1 without writing a PASS receipt; the
[optimized control](../../evidence/issue-29-context7/optimized-control.json)
guards against checks disappearing with assertions.
These timings include Node startup, use synthetic data, and do not estimate a
long-lived process, native C++ binding, remote service, or production latency.

An [empty private npm cache control](../../evidence/issue-29-context7/offline-install.json)
ran `npm exec --offline` for the exact package in a temporary HOME/cache. It
exited 1 with `ENOTCACHED`; the existing host-wide npx cache cannot be assumed
available in a confined deployment. The probe used an existing installation
without changing global npm or project dependencies. Pinning a distributable
artifact into a separately admitted private runtime and verifying a fresh
installed tree remain prerequisites for a real local adapter.

No live Context7 lookup or quota reset was attempted. Previous strict-five
research recorded a quota gap; the fixture verifies **mapping** of a 429, not
the current account's quota. The local MCP package is distinct from the
currently configured remote Context7 MCP transport. Preserve that remote route
until live provider behavior, confined installation, cancellation and native
caller semantics have their own admitted acceptance and rollback controls.

For historical verification, research routes and retro, read the retained
[evidence directory](/Users/rmanaloto/.codex/worktrees/issue-29-context7/claude-code-marketplace/evidence/issue-29-context7)
and [retro](/Users/rmanaloto/.codex/worktrees/issue-29-context7/claude-code-marketplace/.planning/2026-10-10-marketplace-macos-reflection-scaffold/retros/issue-29.md)
at fixed HEAD `3131b89b2a5af94b26e0ff65b8750047fe55cf91`; they are excluded
from this five-path import. The three imported JSON receipts retain original bytes.
Historical concurrent `check`/baseline hit the shared mise env-cache at rc 1;
the serial retry passed. Run named checks serially in the allocated interval.
Replay the existing CLI with explicit pinned `--package-dir`, `--node` and a
fresh private `--output`; normal and `python -O` positives require ten requests,
while optimized `--fault-search` requires rc 1 and no output/PASS. Bind runtime
hashes first and bound the whole probe to 120 seconds with owned-child cleanup.
Fresh synthetic proof remains separate from the historical timings and failures.
Live provider, fresh confined installation, cancellation and native caller
acceptance remain required; the loopback probe does not qualify hostile stdio.
