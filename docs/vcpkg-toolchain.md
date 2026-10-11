# Pinned vcpkg preparation

Task 11a acquires source and qualifies isolated native mise registration.
It does not bootstrap vcpkg, install dependencies or register a global tool.
Independent review passed and reproduced all thirteen private link cases once;
the 19-file original acceptance baseline also passed.

The clean detached checkout is
`~/.local/state/marketplace-tool-foundation/vcpkg-source-e4563094/source`:

- Tool checkout: `e456309491fd875487bf02b8a0dca76c1b1b00cc`.
- Git tree: `6b25d118fef8953f62969191719e0197d646d36d`.
- Initial registry baseline: `e456309491fd875487bf02b8a0dca76c1b1b00cc`,
  recorded independently from the executable source identity.
- Native bootstrap metadata selects executable release `2026-09-26` and
  its pinned SHA-512 for `vcpkg-macos`. This binary is not yet acquired.
- The registry selects compiled `fmt` 12.2.0, port revision 1, Git tree
  `7ca0b8c0026883daf28a0db75f6b4964bae2979a`.

All nine native Git acquisition checks passed. Exact primary source bytes,
licenses, Git identities, command exits and hashes are retained in
[preparation evidence](../evidence/vcpkg-preparation/git/acquisition.json).
The pinned macOS bootstrap downloads an executable. Its final shell command
can mask an earlier version failure, so the later operation must separately
check checksum, architecture and an explicit successful `vcpkg version`.

The registration experiment uses mise 2026.10.7, source commit
`4599c53b4286ff101de876f8122feec0797b48b2`. Its built-in Asdf backend accepts
explicit `asdf:clang-p2996@<commit>` and `asdf:vcpkg@<commit>` identities without
installing plugins. Missing plugin scripts fall back to `<prefix>/bin`.
The eventual vcpkg prefix must therefore expose `bin/vcpkg` and prove its
repository-root discovery. Bare unknown tool names fail backend selection.

Native `mise link` also reconciles runtime aliases, shims and command wrappers.
Direct global invocation is outside this preparation's write scope. The
[probe](../dev/toolchains/mise_link_probe.py) uses two fresh private mise roots,
an allowlisted environment, offline operation and marker executables. It runs
native link in staging, moves only each new tool namespace into the private
consumer, then executes the marker through a fresh native mise process.
All thirteen cases passed, including concrete-version registration, repeat
registration and rejection of overwrites, `latest` and bare unknown names.
No compiler, actual vcpkg executable or plugin was run by this experiment.

An initial preflight stopped before any mise command because external `fzf`
and `opencode` updates changed global config/lock hashes. Its failed receipt
is preserved. The corrected experiment snapshots current state and verifies
all nine global files, eight package states, GLib files, shims and wrappers
afterward; it does not restore historical shared state. See the
[native receipt](../evidence/vcpkg-preparation/native-link/qualification.json).

Reproduce with an existing Python 3.11+ and a new private absolute directory:
`python3 -B dev/toolchains/mise_link_probe.py --run-dir /absolute/new/probe`.
Bootstrap, global promotion and profile updates need their own reviewed
operation, fresh writer census and preimage checks. Dependency builds also
require the shared heavy lease. Source qualification used primary GitHub
acquisition under native fnox; it is not a new five-provider research audit.
