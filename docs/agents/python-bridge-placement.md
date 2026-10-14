# Python bridge placement (ticket #25)

The first migration seam should use a **helper process** that invokes the
existing pinned `aggregated-research` console entry. The decision is scoped to
the initial bridge and remains reversible; it does not replace `trackers` or
qualify any new native operation. The existing plugin wrapper, confined pipx
environment, public CLI and data paths remain the rollback route. A later
native tracer must prove the helper's typed request/result mapping before any
new operation is exposed through the plugin.

Ticket [#24](../../evidence/legacy-trackers/ticket24-review.md) established
the prerequisite: knowledge-base commit
`a872cb016feb5512994b37330ce6a387c5732253`, its installed Python/CLI
and four byte-matched modules, the public dispatch, and the positive/armed-null
JSON fixtures. Its local commit is `931b536733c668e5bab21b9ebce795f8fccf6051`.
The selected comparison uses those exact installed paths and the positive
fixture, with no package install or provider call.

The [probe](../../dev/python_bridge_probe.py) ran five alternating trials per
candidate on arm64 with the installed Python 3.14.8. Both candidates used the
same synthetic `gh` executable in a private `PATH`; three expected requests
per success were logged. The **embedded proxy** imported and called the public
router in the current Python interpreter. The helper candidate launched the
existing console entry in a child process. Both emitted the ticket #24 record
after ignoring only the generated `ran_at`, and both propagated a deliberate
`gh` exit 42 without an apparent success record. No real `gh` was reachable.

| Candidate | Median of five success calls | Failure exit | Bridge property |
| --- | ---: | ---: | --- |
| In-process Python proxy | 96.672 ms | 42 | Reuses the host interpreter and imports; a C++ CPython embedding is still unmeasured. |
| Existing CLI helper process | 251.506 ms | 42 | Uses the already shipped entry point and confines interpreter state to the child. |

These are local, sequential, warm-cache observations with three synthetic
Python `gh` children per success; they are not a production latency estimate.
The roughly 155 ms median difference is accepted for the first bridge because
the helper preserves the installed CLI's startup, routing, exit status and
output contract while keeping the host process independent of Python module
state and CPython ABI. The probe's [measurement](../../evidence/python-bridge/measurement.json)
contains every sample, source and stub hashes, failure controls and runtime
identity. The in-process proxy does **not** measure a compiled C++ embed,
Python C API initialization, cross-language ownership or cancellation.

The compatibility boundary for a future native caller is one bounded child
invocation using the pinned CLI's argv, stdout, stderr and exit code. It must
parse a successful JSON record only after exit 0; nonzero exit, malformed JSON
and timeouts remain explicit failures. It must not silently retry an error as
an empty result. Keep the existing `trackers` wrapper route until each new
operation's fixture and native tracer qualify. Rollback is to select that
unchanged route and remove/disable the new caller; this ticket does not alter
dispatch, install paths or plugin configuration.
