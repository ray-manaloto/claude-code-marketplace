# Pinned P2996 compiler foundation

Task 06a prepares source and a native bootstrap recipe. Configuration, compilation,
installation, runtime acceptance and mise registration are separate operations.
The existing GCC core skeleton is independently qualified at `28c4e52`.
The [source/cache review](../evidence/p2996-source/source-review.json) passed
after correcting compiler-rt SDK pinning and leaving builtin staging to LLVM.
Its script-mode controls reproduced the expected exits; no configure or compiler
ran. Actual generated runtime commands and SDK use remain subsequent gates.

The accepted [LLVM fork](https://github.com/bloomberg/clang-p2996/tree/f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e)
is pinned to `f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e`, tree
`9899759f9004a7df8442ec57000a17e53e6ad5f6`. The fork's Apache-2.0/LLVM-exception
license and exact primary build inputs are retained in
[source evidence](../evidence/p2996-source/inputs/acquisition.json). The fork is
experimental; this lane qualifies development fixtures only.

## Acquire source

Run the repository helper with an existing Python through the native research
credential profile, using a new absolute private directory outside this checkout:

```sh
fnox --config ~/.config/fnox/config.toml --profile codex_research \
  --no-defaults --no-daemon --non-interactive exec -- \
  python3 -B dev/toolchains/p2996_source.py --directory /absolute/new/private/directory
```

The helper uses `/usr/bin/git`, fetches one exact commit, checks the tree against
the primary API receipt, verifies object connectivity and compares retained
source hashes. Git subprocesses ignore global/system Git configuration and use
an empty initialization template. Existing checkouts are never reused or reset.
Command exit codes and log hashes are saved beside the new source directory.
No injected environment values are recorded. HTTP acquisition and Git are the
routes used here; this does not replace the inherited incomplete strict-five sweep.

## Prepared bootstrap

[The initial cache](../dev/toolchains/p2996-bootstrap.cmake) selects Release Ninja
for the compiler build, Clang plus its extra tools, the native AArch64 backend,
and matching libc++, libc++abi, libunwind and compiler-rt from the same source.
Upstream's `LLVM_ENABLE_RUNTIMES` route builds these with the new fork compiler.
Four compile jobs, one link job and one TableGen job bound each native pool;
the later operation must also bound the top-level Ninja job count.

Use the isolated `cpp-build` profile from an empty cwd. Attest and supply absolute
`MARKETPLACE_BOOTSTRAP_CC`, `CXX`, `SDK`, `NINJA`, `PYTHON` and `PREFIX` variables
(each has that full prefix). The prefix must be new and private. The cache keeps
LLVM/Clang headers, libraries and exports for the separately pinned IWYU build.
It excludes extra platform runtimes, optional external dependencies and upstream
test suites; our reflection, runtime, analysis and instrumentation gates remain.
Application configurations continue to use Ninja Multi-Config.

Before configure, record exact tool/SDK hashes, clean source identity, empty
build/install locations, unchanged protected defaults and current shared capacity.
Retain the configure command/cache and inspect the generated runtime commands.
Build resumption must reuse those exact inputs and retain every final exit code.
The cold build requires a fresh host/container census and the shared heavy lease.
Do not infer compiler/tool support from this prepared cache or from source presence.

## Guarded outer configuration

Task 06b's [operation helper](../dev/toolchains/p2996_configure.py) defaults to
preparation. It compares the final reviewed cache, clean source, native tools,
SDK and protected shared state, and records the proposed configure command.
`--configure` additionally requires a matching independent review and admission
receipt, the shared heavy lease, an inherited-descriptor check and a fresh bounded
host/container census. It runs only the outer configure, with a 600-second timeout
and process-group cleanup. No LLVM build or install target is selected.

The [exact CMake source inspection](../evidence/p2996-configure/probe-concurrency-source-review.json)
shows that try-compile does not pass the build parallel-level setting to Ninja.
The operation therefore admits feature probes without claiming a one-job limit.
Generated builtin/runtime configure commands and caches require separate review
for the new compiler, exact SDK, ARM64 architecture and matching runtime options.
Calling their configure targets can trigger compiler builds and belongs to task 07.

The first [outer configure](../evidence/p2996-configure/operation/qualification.json)
passed all 14 commands with exit 0, including fresh capacity and lease checks.
Its exact generated files are retained with hashes. Defaults and protected shared
state are unchanged; no prefix or LLVM compiler was installed. Independent
[runtime-graph review](../evidence/p2996-configure/generated-review.json) and
[operation review](../evidence/p2996-configure/operation-review.json) passed.
The optional `ld-classic` fallback and CMP0219 compatibility probe are resolved.
Task 07 must bound nested runtime builds as well as the outer Ninja invocation.

## Bounded build preparation

Task 07a prepares the [build helper](../dev/toolchains/p2996_build.py) against the
reviewed outer configuration. Its default mode checks source/tool/generated-file
identity, the actual profile environment and protected shared state without
building. `--build` requires a matching independent review and admission, then
acquires the shared heavy lease and checks current host/container capacity.
`--resume` explicitly selects an existing incremental build history.

The outer command selects four jobs. `CMAKE_BUILD_PARALLEL_LEVEL=4` is set after
mise selection so nested CMake build commands inherit it. Capacity planning
allows eight outer/child job slots; this is not an aggregate process limit and
does not bound nested configure probes. The operation requires 32 GiB free at
start, checks an 8 GiB reserve every fifteen seconds, and stops its own process
group on timeout, interruption or reserve failure. Logs and actual final exits
are retained; the six-hour deadline does not imply success.

The build writes the existing private build tree. Later installation must
record separate root, builtins and runtime install exits because the upstream
outer wrapper ignores child install failures. Reflection and installed-runtime
witnesses remain separate gates.
The [independent preparation review](../evidence/p2996-build/preparation-review.json)
passed after two cleanup repairs: six native preparation commands, eight inert
subprocess controls and eleven admission controls.

The first [cold build](../evidence/p2996-build/failed-cold-build/qualification.json)
exited 1 after 363.49 seconds. SDK libc++ rejects the pinned RDF comparator's
stateful `std::less<RegisterRef>` specialization. The full logs and incremental
tree are retained. Independent [failure closure](../evidence/p2996-build/failure-closure-review.json)
confirms a free lease, no surviving build processes, unchanged protected state
and a byte-identical default environment. A bounded compatibility repair is
required before the build can resume; installation and acceptance remain pending.
