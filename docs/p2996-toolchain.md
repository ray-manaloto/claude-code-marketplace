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
