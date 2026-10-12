# Sanitizer qualification

Task 14a prepares ASan, UBSan and ASan+UBSan witnesses against the qualified
P2996 compiler and compiler-rt. The existing reflection core compiles separately;
the public-header consumer rejects leaked reflection implementation flags.

Each mode must pass a clean run. Address modes must diagnose an intentional heap
out-of-bounds read; undefined-behavior modes must diagnose signed overflow.
The clean branch performs both operations within bounds. A volatile-qualified
pointee isolates the ASan read from UBSan type/object-size/alignment diagnostics.
Exact source-backed options make error exits deterministic, suppress external
symbolization and core dumps, and keep leak detection outside this first unit.
Native qualification remains incomplete. ASan compilation, linking and ARM64
checks passed, but three clean executions timed out at 20 seconds before main.
The [owned-process sample](../evidence/p2996-sanitizers/startup-sample.txt.source)
captures recursive ASan initialization: shadow mapping inspects dyld images,
shared-cache enumeration allocates, and ASan waits on its own initialization lock.
The [diagnosis receipt](../evidence/p2996-sanitizers/startup-diagnosis.json) binds
the sample and retained failed operations. UBSan and combined cases were not
reached. Independent [failure review](../evidence/p2996-sanitizers/failure-review.json)
passed without findings for the recorded failure and closure. This does not
qualify a sanitizer mode; a separate scratch repair follows.
The first capacity check exited 1 for two idle Zed language services, before any
native operation. The reviewed exception binds their exact process identities,
ancestry and current checkout directories; CPU observations are bounded, not a
guarantee of continued idleness. Other matched build processes still block execution.
The [source contract](../evidence/p2996-sanitizers/source-prerequisite.json)
binds the options, driver-selected libraries and diagnostic expectations.

The [guarded runner](../dev/toolchains/p2996_sanitizers.py) uses fresh private files, the canonical heavy-operation lease,
one compiler job and fresh capacity. It preserves compiler/source installations,
global configuration and unrelated defaults. Loader paths establish selected
runtime presence, not symbol-level exclusivity. These fixtures do not qualify
dependency instrumentation, linkage matrices, coverage, TSan or LSan.
