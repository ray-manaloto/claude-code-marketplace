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
The initial Task 14a attempt failed at startup. ASan compilation, linking and
ARM64 checks passed, but three clean executions timed out at 20 seconds before main.
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

Task 14a1 tests a private ASan repair for the observed macOS 27 startup path.
The [source patch](../dev/toolchains/patches/p2996-asan-macos27-dyld.patch) uses
the current task's public dyld information, checks its format, size, version and
Mach-O header, and retains all mapping and shadow validation. The native A/B
comparison supplies bounded startup evidence for the current macOS arm64 host.

The [scratch runner](../dev/toolchains/p2996_sanitizer_repair.py) copies the 127
retained runtime objects and builds two replacements for one mapping object.
It links and signs private original and patched ASan libraries with the captured
build recipe. The unchanged library must reproduce the bounded startup timeout;
the patched library must pass the existing ASan and combined clean/error cases.
Standalone UBSan uses the installed original runtime. The native operation
exited 0: the original library timed out at 20 seconds, all three clean cases
exited 0, and all four intended diagnostics exited 86. Loader traces selected
the expected exact libraries. [Closure evidence](../evidence/p2996-sanitizer-repair/operation/closure.json)
records released ownership and preserved shared state. Independent
[artifact review](../evidence/p2996-sanitizer-repair/artifact-review.json) passed
without findings. These are private runtime witnesses. Installed-runtime
promotion, dependency instrumentation and matrix qualification remain separate.

Task 14a2 prepares the [installed-runtime guard](../dev/toolchains/p2996_asan_runtime.py).
It updates only the expected digest and size of the single ASan library in two
in-memory inventories. All original inventory files and existing guard functions
remain unchanged. Its replacement primitive requires exact regular-file identities,
one link per file, canonical paths and preserved executable mode. Private
[controls](../evidence/p2996-asan-runtime/repaired-controls/controls.json) passed.
Review found that the initial mode check discarded special permission bits; the
correction preserves those bits and checks exact identity at guard entry. Its
[disposition review](../evidence/p2996-asan-runtime/preparation-review.json)
passed without new findings. A later caller must separately stage the candidate
with the destination's exact `0755` mode,
verify source/build inputs, preserve a backup, obtain fresh capacity and ownership,
and qualify the installed path with all seven witnesses.

Task 14a3 uses the [promotion runner](../dev/toolchains/p2996_asan_promote.py).
It retains an exact original backup and permits one installed-file replacement
under fresh capacity and the canonical ownership lease. Witnesses use a separate
read-only installed-prefix sandbox and the normal loader path. A failure while
ownership is held restores only the known replacement; unknown target content
stops recovery without overwriting it. Recorded source/build inputs, Git source
state, all unrelated prefix entries and default selection remain checked.
Private [transaction controls](../evidence/p2996-asan-promotion/controls/controls.json)
passed, including rollback and refusal to overwrite unknown content. Independent
preparation review passed. The native operation exited 0: all three clean runs
returned 0 and all four deliberate diagnostics returned 86 through the installed
libraries. The original backup remains retained. Source/default checks passed,
owned processes ended and the lease was free in the
[closure receipt](../evidence/p2996-asan-promotion/operation/closure.json).
Independent [artifact review](../evidence/p2996-asan-promotion/artifact-review.json)
passed without findings. Installed ASan, UBSan and combined runtime witnesses are
qualified; dependency instrumentation and configuration/linkage matrices remain separate.

Task 14b prepares [TSan witnesses](../dev/toolchains/tsan_witness.cpp) with the
[confined runner](../dev/toolchains/p2996_tsan.py). A joined worker precedes the
second write in the clean case; the deliberate race leaves the two writes
unordered. Both modes must diagnose the race, and TSan+UBSan must also diagnose
signed overflow. Source support and runtime options are bound before execution.
The installed TSan library is separate from the repaired ASan library; its macOS
27 startup failed before main with signal 11 after compilation, linking and
ARM64 checks passed. The combined mode was not reached. The matched own-process
[crash report](../evidence/p2996-tsan/startup-diagnosis.json) shows shared-cache
traversal entering a TSan interceptor during initialization. The initial launch
was blocked by the user's concurrent `update-all` run; both attempts are retained.
Source/default preservation and ownership closure passed. Independent
[failure review](../evidence/p2996-tsan/failure-review/review.json) found no issue
with the recorded failure and cleanup. No TSan mode is qualified. The same
mapping source used by ASan reaches the observed TSan startup path, but the
patch needed a private native A/B test using TSan's own link recipe.

Task 14b1 prepares that comparison with the
[private TSan runner](../dev/toolchains/p2996_tsan_repair.py). The captured
[link recipe](../evidence/p2996-tsan-repair/recipes.json) uses 128 TSan objects;
93 match the earlier ASan inventory, while the remaining 35 are specific to
TSan. The runner replaces only the common mapping object in each private
runtime, using original and patched objects from the successful ASan repair.
It requires the original pre-main failure, patched clean runs, race reports and
the combined signed-overflow report. Preparation review passed without findings.
The native trial exited 0: the original private runtime crashed with signal 11
before main; the patched private runtime passed both clean runs and emitted the
required race and overflow diagnostics with exit 86. The installed TSan runtime
stayed unchanged. [Closure evidence](../evidence/p2996-tsan-repair/operation/closure.json)
records retained text/artifact hashes, absent owned processes and a free lease.
[Independent artifact review](../evidence/p2996-tsan-repair/artifact-review/review.json)
passed without findings. Both private link commands retained nonfatal unused
`-stdlib=libc++` warnings. The cleanup findings are historical collector
receipts; the reviewer did not repeat the live PID or lease probes. Installed-path
qualification remains separate.

Task 14b2a prepares the [installed TSan guard](../dev/toolchains/p2996_tsan_runtime.py).
It composes the accepted ASan overlay with a second exact TSan row in each of
the two immutable historical inventories. The qualified private TSan library
has mode `0700`; any installed replacement must be staged at the original
`0755` mode. [Private controls](../evidence/p2996-tsan-runtime/controls/controls.json)
passed for overlay precision, replacement, restore and unknown-target refusal.
The installed library was still original at this preparation stage. [Independent preparation review](../evidence/p2996-tsan-runtime/preparation-review/review.json)
passed without findings; its bounded comparison exited 0 and verified 27
contract inputs, six control logs and exactly two runtime binary hashes. The
reviewer did not rerun the controls. The subsequent installed-path qualification
is recorded under Task 14b2b.

Task 14b2b prepares the [installed TSan promotion runner](../dev/toolchains/p2996_tsan_promote.py).
Its contract binds the private candidate and both TSan witness binaries. The
runner stages the candidate at the original `0755` mode, retains an exact
backup, and requires fresh ownership and capacity before the one-file change.
The first admitted dispatch stopped before the lease and before any installed
write because the runner omitted imports required by its extracted command
wrapper. [Failure closure](../evidence/p2996-tsan-promotion/initial-failure/closure.json)
confirms zero child commands, the original installed digest and an ended owned
process. The imports are restored and the wrapper passed a private harmless
command control. [Focused retry review](../evidence/p2996-tsan-promotion/preparation-review-retry/review.json)
passed without findings. Fresh capacity then passed, and the native retry
exited 0: 24 commands included two clean runs and three deliberate race or
overflow diagnostics through the installed loader path. The original library
is retained as `original.dylib` in the private native run directory; the
installed library now has the qualified candidate digest at mode `0755`.
[Closure](../evidence/p2996-tsan-promotion/operation/closure.json) records
the exact installed, backup, candidate and witness identities, unchanged
source and default outputs, absent owned processes and a free lease.
[Independent artifact review](../evidence/p2996-tsan-promotion/artifact-review/review.json)
passed without findings: its bounded comparison checked 24 command receipts,
48 logs, 55 text snapshots, eight copy pairs and five binary artifacts. The
review did not rerun the native witnesses or full Claude/container acceptance.

Task 14c prepares a private [LSan witness](../dev/toolchains/lsan_witness.cpp)
and [confined runner](../dev/toolchains/p2996_lsan.py). The pinned compiler's
`-###` probes accept standalone LSan and LSan+UBSan and select the installed
LSan runtime; they do not compile or execute a witness. The [contract](../evidence/p2996-lsan/contract.json)
binds that runtime, both probe logs, the current installed TSan, the prior
source/build inventory and the leak/overflow expectations. Preparation review
passed. The first native launch refused an unknown writer before any command;
the admitted retry compiled and linked the standalone LSan arm64 witness, then
timed out during the clean exit-time leak scan. Its [closure](../evidence/p2996-lsan/failed-native/closure.json)
shows no installed change, no remaining owned process and a free lease. The
[diagnostic sample](../evidence/p2996-lsan/diagnostic/sample-sample.txt) places
the worker inside dyld's lazy callback while LSan's allocator lock is held.
LSan and LSan+UBSan runtime behavior remains unqualified pending a separately
reviewed runtime repair.
