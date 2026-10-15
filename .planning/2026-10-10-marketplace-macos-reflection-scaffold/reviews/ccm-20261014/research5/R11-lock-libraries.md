# R11: Existing lock tools and libraries for the heavy-run gate (research round 5, 2026-10-14)

Written by research agent R11 of session `ccm-20261014` (`ce9c0b3d`) for D123 (lockf or our own C++, or a
Rust library behind a C++ bridge), under D112 (one modern C++ library, no new Python logic), D124 (one lock
path, `~/.local/state/claude-code-marketplace/heavy-gate.lock`, no legacy path) and D125 (the 27 callers
switch in units of 5). It extends R6 (`research5/R6-host-lock-implementation.md`) and does not redo R6's
sections on timed_lock_alg, Boost.Interprocess, mise or the `flock(2)` primitive. Read-only except this file
and the untracked offline corpus. MP at `21af565`, branch `codex/marketplace-native-onboarding`.

Citation keys. MP = `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`. O11 =
`MP/offline/research/R11-lock-libraries/` (this run's D110 mirror; `O11/manifest.json` lists 53 items with
URL, local path, UTC time, command, exit code and SHA-256 or commit, including the 5 failed or removed
attempts). O6 = `MP/offline/research/R6/` (R6's mirror, reused, not re-copied; listed under
`reused_from_R6_not_recopied`). S11 =
`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/r11/`
(search output, probe scripts, probe output, `callers.tsv`). HL = dotfiles
`python/src/dotfiles_setup/host_lock.py` at DF `7744a9c6`, SHA-256 `b20e5d96...` (the pin MP asserts). DF =
`/Users/rmanaloto/dev/github/ray-manaloto/dotfiles`. Probes M1 to M11 ran on this Mac (macOS 27.0.1, 26A434,
`/usr/bin/lockf` from `shell_cmds-334` per `what /usr/bin/lockf`), lock files only under `S11/probe/run*`;
the real lock paths were never touched. Scripts: `S11/probe-scripts/lockf-probes.sh`,
`S11/probe-scripts/lockf-fd-follow.sh`; output: `S11/probe/lockf-probes.txt`, `S11/probe/lockf-fd-follow.txt`.

## Verdict

Recommendation for D123: write the small C++ heavy-gate of R6 section 7.2 (RAII over `flock(2)` modelling
*Cpp17TimedLockable*, plus a `run`/`status` command), in portable C++23 with no reflection so Apple clang
and Linux GCC build it before the P2996 toolchain exists. Do not adopt macOS `lockf(1)` as the gate, do not
bridge a Rust crate, and do not adopt an existing CLI. Confidence: high on the facts below (source read
from the mirror and measured here), medium-high on "worth it": the deciding point is that no existing tool
meets the two load-bearing requirements together, naming the holder (R2) and keeping the lock with the
work rather than with the wrapper (R3).

What our code adds over the best existing tool, and nothing more:

1. A holder record (`pid<TAB>label<TAB>since`) inside the one lock file, truncated on release, printed on
   fail-fast, while waiting and by `status`. macOS `lockf`, util-linux `flock(1)` and discoteq `flock` write
   nothing (M1; `O6/repos/util-linux/sys-utils/flock.1.adoc:62-104`); macOS `lockf` has no `-p` (rc 64,
   S11 probe); FreeBSD's 2025 `-p` writes only the child PID and is not in macOS
   (`O11/files/freebsd/lockf.c:137-138,296-297`); quodlibetor/flock writes a second file
   (`<lock>.holder`) and only in wrap mode (`O11/repos/quodlibetor-flock/README.md:221-227`).
2. The lock follows the work: the gate descriptor is inherited by the command and its number exported, so
   the 27 callers keep passing it to compilers with `pass_fds` and checking device and inode. In command
   mode macOS `lockf` closes the lock descriptor in the child before `exec` and frees the gate when the
   wrapper dies while the command keeps running (`O11/repos/shell_cmds/lockf/lockf.c:240-249,308-316`;
   measured M2, M3, M11). quodlibetor/flock opens through Rust std, which sets `O_CLOEXEC`
   (`O6/repos/rust/library/std/src/sys/fs/unix.rs:1212`), so it behaves the same by code reading.
   util-linux `flock(1)` does pass the descriptor (`flock.c:121-122` opens without `O_CLOEXEC`), but
   exports no descriptor number except through the new `--fd` option (PR #4553, merged 2026-08-18).
3. One binary and one exit-code contract on macOS and Linux, built from the repository: no `lockf` (rc 75)
   versus `flock` (rc 1) branching, no Homebrew install on macOS, and a bounded wait that sleeps instead of
   spinning (macOS `lockf` descriptor mode busy-polls, R6 `probe-lockf-lsof.txt`; the spin fix is FreeBSD
   `d90513ea85`, 2026-05-03, not in macOS).
4. An explicit nesting policy: refuse by default (what all 27 callers assert today) and re-enter only by a
   proven inherited descriptor (R6 section 7.1) where a caller opts in.
5. An in-process RAII type for the C++ library itself (`std::unique_lock<host_gate> g(gate, 1h)`).

The size is an estimate, UNVERIFIED: about 200 lines plus process-level tests, the shape in R6 7.2.
If the user wants zero code anyway, the only acceptable `lockf` form for the 27 fail-fast callers is the
descriptor idiom (`exec 9>>PATH; /usr/bin/lockf -s -t 0 9 || exit 75; exec <script>`), which keeps the lock
with the work (M10) and allows re-lock by an inherited descriptor (M6), but names no holder, spins on
`-t N>0`, and on Linux needs `flock -n 9` instead.

## 1. Requirements, from R6 section 1 and the 27 callers

All 27 files were read (`S11/callers.tsv` lists file, line, label and the checks per file).

- R1, bounded wait: HL waits `DOTFILES_HEAVY_GATE_WAIT` seconds (default 3600, HL:72-73,122-130), polls
  once a second (HL:75,242-255) and its CLI exits 124 on timeout (HL:290-297). The 27 MP callers do not wait:
  every one calls `held(HEAVY_GATE, "<label>", wait_s=0, out=io.StringIO())` (27 of 27, for example
  `MP/dev/toolchains/baseline.py:112`, `p2996_configure.py:153`), so MP needs fail-fast; the bounded wait is
  a dotfiles need (`DF/python/src/dotfiles_setup/gate_result.py:181-183` passes `wait_s=timeout_s`).
- R2, name the holder: HL writes `pid<TAB>label<TAB>since` after acquiring (HL:205-209) and its timeout
  error names it (HL:232-234,245-249). MP swallows the waiting notice (`out=io.StringIO()`) but not the
  error: no caller catches `HostLockTimeoutError` (0 matches in `dev/toolchains/*.py`), each records
  `repr(error)` in its report (`p2996_configure.py:196-198`; 27 files have that handler). Each caller has
  its own label (27 distinct labels, `S11/callers.tsv`).
- R3, release on crash, with the lock following the work: the kernel frees `flock` on last close (HL:10-15,
  R6 P4). HL tells callers to pass the descriptor to children "so the lock outlives a killed parent"
  (HL:171-174), and all 27 do (`descriptor=fd` or `pass_fds`, for example `p2996_configure.py:66-68,178`);
  three also prove in the child that the descriptor is the lock file (`p2996_configure.py:176-179`,
  `p2996_build.py:302`, `p2996_install.py:198`).
- R4, re-entry by nested child runs. The MP callers do not nest, and no nesting path exists in MP:
  - Every caller asserts that neither the holder export nor `DOTFILES_HEAVY_GATE_FD` is set before locking
    (27 of 27, for example `baseline.py:111`), so a nested gated script fails with `AssertionError` before
    it touches the lock.
  - Children run with an environment built before `held()` (`p2996_configure.py:52,66`), get only the
    descriptor, and are `ps`, `cmake`, `ninja`, compilers, `docker` and inline `python -c` probes, never
    another gated script.
  - `held()` runs inside `main()` in 26 files and in a module-level `try:` in `p2996_math_probe.py:76,176`,
    a script nothing imports. The cross-file loads go through `mise_runtime.function()`, which executes one
    function definition only (`dev/toolchains/mise_runtime.py:48-52`): `p2996_reflection.protected`
    (`p2996_reflection.py:64`) and `iwyu_build.source_state` (`iwyu_build.py:74`), neither of which locks.
  - No mise task, hook or CI workflow invokes these scripts or the gate (`git grep` outside
    `dev/toolchains` and `evidence/` copies finds only unrelated `fcntl.flock` uses in
    `dev/research_refresh/refresh.py:1517` and `dev/search_catalog.py:216-308`).
  - The only nesting path found is in dotfiles: `ship` holds the gate (`DF/python/src/dotfiles_setup/pr.py:758`)
    across `git push`, whose pre-push task re-enters through `heavy-gate run` (`DF/mise.toml:320-323`), and
    `gate_result.py:181-187` re-enters through the inherited descriptor. For MP the requirement is the
    opposite of re-entry: refuse nesting loudly.
- R5, Linux CI parity: MP's three workflows run on `ubuntu-latest` (`.github/workflows/development.yml:12`,
  `acceptance.yml:9`, `research-fast.yml:16`) and none runs the 27 scripts, which are macOS-only
  (`p2996_configure.py:19` hard-codes a `/Users/...` path and `:165` the Docker.app path). Parity is
  a forward requirement for the C++ library's own heavy runs and the Linux OCI image (`MP/AGENTS.md`).
- R6, status query: HL's `status` prints the record or `free`, rc 0 or 1 (HL:281-285). No MP file calls it.
- Also from the callers: an exact path assertion (`baseline.py:110`), a digest pin on the lock code
  (`p2996_configure.py:19-20,146`; reports carry `host_lock_sha256`, `:129`) that a replacement must also
  give, and a capacity census taken under the lock (`p2996_configure.py:155-175`), which stays in the scripts.

## 2. lockf(1), util-linux flock(1) and discoteq/flock

### 2.1 macOS lockf(1), measured

Source: Apple `shell_cmds` (`O11/repos/shell_cmds/lockf/lockf.c`, tag `shell_cmds-329`, commit
`2987870`), which records FreeBSD `lockf.c` at `e4967d4d48` (2023-11-26) as its upstream base
(`O11/repos/shell_cmds/.upstream_base_commits`). The installed binary is `shell_cmds-334` and prints the same
usage, `lockf [-knsw] [-t seconds] file command`, so no newer option is present.

| Probe | Result | Source line |
|---|---|---|
| M1 `lockf -k -t 2 L true` against a holder | rc 75 after 2.02 s, "lockf: L: already locked", no holder named | `lockf.c:179-187,222-225` |
| `-t 0.5`, `-p`, `-T` | rc 64 each ("invalid timeout", "illegal option") | `lockf.c:103,118-121` |
| M2 SIGKILL the lockf wrapper while `sleep 20` runs | gate free at once, `sleep` still running | child closes `lockfd` before `exec`, `lockf.c:240-245` |
| M3 SIGTERM the wrapper | gate free, command orphaned and still running | handler unlocks and re-raises, never signals the child, `lockf.c:247-249,308-316` |
| M4 command killed by SIGKILL | rc 70 (EX_SOFTWARE), gate free | `lockf.c:255` |
| M5 command exits 75 | rc 75, indistinguishable from "busy" | `lockf.c:222-225,255` |
| M6 descriptor idiom, nested `lockf -s -t 0 9` on the inherited fd 9 | inner rc 0; a fresh opener rc 75; free after the holder shell exits | `lockf.c:269-277` |
| M7 status by `lockf -k -s -t 0 L true` | 0 free, 75 busy; the same probe without `-k` deleted the file | `lockf.c:298-301` |
| M8 command writes a record into the kept file | waiter can `cat` it; it stays after release (stale) | lockf never truncates |
| M10 descriptor idiom, `exec python`, python passes fd 9 to a 4 s child and exits | gate busy until the grandchild exits, then free | descriptor shared, R6 P2 and P5 |
| M11 command mode, python exits leaving a child | gate free while the child runs | as M2 |

Waiting in command mode costs no CPU (R6 `probe-lockf-lsof.txt`); descriptor mode busy-polls because
`acquire_lock` always adds `LOCK_NB` for a descriptor (`lockf.c:211-213,273`), the bug FreeBSD fixed in
`d90513ea85` ("lockf: Avoid spinning when operating on an fd", 2026-05-03, PR 294832, D56722). FreeBSD also
added `-p` (write the child's PID, `df268d4b03`, 2025-06-24, D51014) and `-T` (forward SIGTERM to the child,
`679f619495`, D51025, which states the orphan problem M3 shows) (`O11/files/freebsd/lockf.c:128,137-138,296-297,366-375`;
`O11/files/freebsd/lockf.1:126-156`, dated 2026-02-26). None of the three is in macOS 27.

Requirements met by macOS lockf: R1 yes (whole seconds; 0 for fail-fast). R2 no. R3 only in descriptor
mode (M10); command mode releases with the wrapper (M2, M3, M11). R4 only in descriptor mode (M6). R5 no
(`lockf(1)` is BSD-only; on Linux the equivalent is `flock(1)` with other flags and exit codes). R6
busy/free only, and a forgotten `-k` deletes the lock file (M7), which R6 P7 showed splits holders.

### 2.2 util-linux flock(1) (Linux), read from source, not measured

From `O6/repos/util-linux` (`d427f58`, 2026-10-14) and `O11/docs/cli/man7-flock.1.md` (util-linux
2.43.devel): `-w` takes fractional seconds, `-n` fails at once, `-E` sets the conflict exit code (default
1), `-o` closes the descriptor before `exec`, `-F` execs the command in place so it "continues to hold the
lock", `--fcntl` switches to OFD locks that do not interact with `flock(2)`, `--fd N` locks an already open
descriptor, `--verbose` reports the wait time (`flock.1.adoc:62-104`). The file is opened without
`O_CLOEXEC` (`flock.c:121-122`) and closed in the child only with `-o` (`flock.c:487-495`), so the command
inherits the lock. History: `-F` since `703251401c` (2016-04-15), `--fcntl` PR #2993 (merged 2024-04-29),
`--fd` PR #4553 (merged 2026-08-18), output flush PR #4680 (merged 2026-10-13). Licence MIT (`flock.c:1`).
No issue or PR proposes a holder record (searches in section 8). On macOS it exists only through the
keg-only Homebrew `util-linux` 2.42.4, whose formula builds `flock` there (it is not in the Linux-only list,
`O11/files/homebrew/util-linux.rb:95-121`) and conflicts with the `flock` formula only on Linux (`:47-53`);
not installed here, so unmeasured on this Mac.

Requirements met: R1 yes; R2 no; R3 yes (follows the command; with `-F` the command is the holder); R4 by
the descriptor idiom or the `FLOCKER` environment idiom (`flock.1.adoc:141-142`); R5 native on Linux, macOS
only after a Homebrew install; R6 `flock -n PATH true`, and `lslocks` on Linux names a PID with the
open-file-description caveat (R6, `O6/docs/man7/lslocks.8.md:205-213`).

### 2.3 discoteq/flock (the Homebrew `flock` formula)

Source `O6/repos/discoteq-flock` (`419b608`, 2026-04-17). Uses native `flock(2)` when present and an
`fcntl` emulation only without it (`src/flock.c:28-85`); `-w` fractional through `setitimer`
(`:207-214,305-316`), `-E` (`:215-223`), `-o` (`:356-358`); the command inherits the descriptor (open
without `O_CLOEXEC`, `:268-275`). No `-F`, no `--fd`, no holder record. Last release v0.4.0 (2020-04-24);
PR #43 (merged 2026-04-17) modernised it but is unreleased, so Homebrew still ships 0.4.0
(`O11/files/homebrew/flock.rb:1-6`; 934 installs in 30 days, `O11/docs/cli/brew-flock.md`). ISC. Open issue
#40 (2023-09-24) asks to document systems where `fcntl` and `flock` locks do not respect each other.
Requirements: R1 yes, R2 no, R3 yes, R4 descriptor mode, R5 conflicts with util-linux on Linux, R6 rc only.

## 3. C++ libraries with a cross-process lock

None combines a kernel-released lock, a holder record and a timed wait.

- Qt `QLockFile` (qtbase `f23b87a`): names the holder (`getLockInfo(pid, hostname, appname)`) and has
  `tryLock(timeout)` (`O11/docs/cpp/qt6-qlockfile.md:40-49`), retrying with a sleep that doubles from about
  100 ms up to 5 s (`repos/qtbase/src/corelib/io/qlockfile.cpp:391-431`). The lock is a file created with
  `O_EXCL | O_CLOEXEC` plus a `flock` liveness mark (`qlockfile_unix.cpp:111,122-140,259-277`), deleted on
  unlock; a crashed holder's file is removed as stale by PID, process name and native lock. Stale time
  defaults to 30 s and long holds must set it to 0 (`qt6-qlockfile.md:65-71,264`); a recursive lock
  deadlocks (`:237`). Children never hold it (`O_CLOEXEC`). LGPL-3.0-only, GPL or commercial
  (`qlockfile.cpp:4`), and it needs QtCore.
- LLVM `LockFileManager` (llvm-project `c4d25e2`): writes `hostname pid` into a hard-linked `.lock` file
  (`repos/llvm-project/llvm/lib/Support/LockFileManager.cpp:189-241`), waits with
  `waitForUnlockFor(seconds)` and 10 to 500 ms backoff (`:288-313`), treats a dead owner (`getsid` fails) as
  `OwnerDied` (`:115-125`). Its `AdvisoryLock` interface is documented as "a synchronization primitive with
  weak mutual exclusion guarantees" that "may allow multiple threads/processes to acquire the ownership of
  the lock simultaneously" (`llvm/include/llvm/Support/AdvisoryLock.h:27-32`), introduced by PR #130989
  (merged 2025-03-13); PR #182722 (2026-02-27) added a 90 s module-cache lock timeout. Not a mutex.
  `llvm::sys::fs::tryLockFile(fd, timeout)` polls `fcntl(F_SETLK)` record locks (`Unix/Path.inc:1321-1376`),
  which do not interact with `flock(2)` on Linux (R6). Apache-2.0 WITH LLVM-exception.
- Poco 1.15.4 `NamedMutex`: on macOS a POSIX named semaphore (`sem_open`), on Linux a System V semaphore
  with `SEM_UNDO` (`repos/poco/Foundation/src/NamedMutex_UNIX.cpp:21,56-57,68-71,116`), so a crashed holder
  frees it on Linux but not on macOS; only `lock`, `tryLock`, `unlock` (`include/Poco/NamedMutex.h:65-74`).
  Open #4876 (2025-02-19): the creator's exit deletes the semaphore under other users; #4204 (closed
  2023-12-16) was a macOS crash. `FileStreamRWLock` is a blocking `fcntl(F_SETLKW)` record lock
  (`FileStreamRWLock_POSIX.h:44-56`); `PIDFile` writes a PID and locks nothing (`PIDFile.h:29-66`). BSL-1.0.
- folly `File` (`4fbf9f3`): `lock`, `try_lock`, `lock_shared` over `flock(2)`, no timed form, no holder
  (`repos/folly/folly/File.h:145-158`, `File.cpp:172-199`). Apache-2.0, and all of folly as a dependency.
- LLFIO (`O6/repos/llfio`, last commit 2026-08-24): whole-file `lock_file()` and `try_lock_file()` over
  `flock` with no deadline; deadlines only for byte ranges (`include/llfio/v2.0/lockable_byte_io_handle.hpp:109-121,268`).
  Apache-2.0 or BSL-1.0. Boost.Interprocess: R6 section 3 (record locks; `named_mutex` not crash-safe on macOS).
- abseil, stlab, GLib: no cross-process lock. Code search `flock` returns 0 in `abseil/abseil-cpp` (control
  `README` 5) and 0 in `stlab/stlab` (control 18); in `GNOME/glib` the only hits are a Windows stream and a
  private D-Bus keyring lock made with `O_CREAT | O_EXCL` and stale deletion
  (`O11/files/glib/gdbusauthmechanismsha1.c:527-625`), not a public API.
- NorduGrid ARC `Arc::FileLock`: a `pid@hostname` lock file with a timeout (`O11/docs/cpp/arc-filelock.md:74`),
  not kernel-released; niche grid middleware.

Nothing here beats 30 lines of POSIX `flock` for MP: the kernel-released options (folly, LLFIO) add no
holder or timeout, and the ones that name a holder (Qt, LLVM, ARC) replace the kernel lock with a lock
file and staleness rules that can steal a long heavy run's lock.

## 4. Rust crates, Rust CLIs, and what a bridge would look like

Crates. Every maintained crate is a thin wrapper over `flock(2)`; none provides holder record, timeout and
re-entry together.

- std `File::lock`, `try_lock`, shared variants and `unlock` (stable 1.89.0) are `flock` on Unix and have no
  timed form (`O11/docs/rust/std-fs-file.md:386-409,467-496`; harn-flock's docs say so:
  "`std::fs::File::lock` has no timed form", `O11/docs/rust/docsrs-harn-flock.md`).
- fs4 1.1.0, fd-lock 4.0.4, fmutex 0.3.0, named-lock 0.4.1: lock and try-lock only, no holder
  (`O6/repos/fs4-rs/src/file_ext/sync_impl.rs:134`; `O6/repos/fd-lock/src/rw_lock.rs:96,113`;
  `O6/repos/fmutex/src/lib.rs:341-400`; named-lock puts its file in `$TMPDIR/<name>.lock`,
  `O11/docs/rust/docsrs-named-lock-NamedLock.md:45`, open issue #15, 2026-07-24).
- fslock 0.2.1 (last release 2021-12-20 per crates.io): `lock_with_pid` writes the PID, "erased on unlock"
  (`O11/docs/rust/docsrs-fslock-LockFile.md:242-245`; `O6/repos/fslock/src/lib.rs:165-320`), no timeout,
  no way to read the owner (open #13, 2022-05-11); open #6 reports a lock released when another descriptor
  of the file closes. This is the only crate with a holder field, and it is PID only.
- filelock (aisk) 0.7.0: `lock_timeout` by polling 1 to 50 ms over std `File::lock`
  (`O11/repos/rust-filelock/src/lock.rs:8-9,135-147`; `O11/docs/rust/docsrs-filelock.md:79-97,171-177`).
  harn-flock: `lock_with_deadline`, names the path, not the holder (`docsrs-harn-flock.md`).
- pidlock 0.2.2, lockfile 0.4: PID files made with `create_new`, staleness by `kill(pid, 0)`, not
  kernel-released (`O11/repos/pidlock/src/lib.rs:461,728`). file-guard 0.2.0 and file-lock: `fcntl`
  record locks (`O11/repos/file-guard/src/os/unix.rs:2,30-51`), which do not interact with `flock` on Linux.

CLIs. crates.io has no maintained `flock(1)`-style binary crate (R6; this run's `crates?q=flock` lists none).
On GitHub:

- quodlibetor/flock (Rust, v0.0.4, 2026-08-01, MIT OR Apache-2.0): the closest existing tool. `-n`, `-w`
  fractional through a helper thread (`src/main.rs:578-610`), `-E`, descriptor mode, a weighted token pool,
  and `--label` with a `<lockfile>.holder` sidecar (pid, label, start, mode) shown by `-v`
  (`README.md:200-227`; `src/holder.rs`). Installable by mise's `github:` backend (`README.md:256`). Against
  it: wrap mode spawns the child with Rust std (`src/main.rs:296-298`) on a descriptor opened by std
  (`:489-497`), hence `O_CLOEXEC`, so the gate follows the wrapper as in M2; the sidecar is a second file
  and absent in descriptor mode; no `status`; 0 stars, 0 issues, one author, 8 PRs all dependency bumps
  except CI; README line 23: "Entirely vibe coded, use it if you'd like".
- sirech/lock (2021, `file-lock` crate, record locks, no timeout), tuulbelt `file-based-semaphore`
  (lock-file existence with age-based stale removal, default 3600 s, `O11/repos/tuulbelt-sema/src/lib.rs:109-121,352-355`,
  which would steal a live heavy run after an hour), lockito (repository returns 404; docs.rs README 404).
- pueue needs a daemon (R6 section 5).

Bridge shapes, for completeness. (a) `cxx`: a `#[cxx::bridge]` module with generated C++ and Rust glue
(`O11/docs/bridge/cxx-rs-index.md`), but "There is not an officially endorsed CMake setup for CXX"
(`O11/docs/bridge/cxx-rs-cmake.md`), so MP's CMake build would add Corrosion (`corrosion_import_crate`,
CMake 3.22 or newer, `O11/docs/bridge/corrosion-readme.md:7,37,70`) and a cargo toolchain. (b) A C ABI:
`extern "C"` functions in the crate and a header from cbindgen (`O11/docs/bridge/cbindgen-readme.md:25,76-80`),
same build cost. (c) Calling a CLI: `posix_spawn` of the binary, which is option "existing CLI", not a
bridge. Since every crate ends in the same `flock(2)` call, a bridge would import a second toolchain to wrap
about 30 lines of POSIX and still leave the holder record and descriptor export to write. Rust is not better
here.

## 5. Recommendation, against the four options

| Option | R1 wait | R2 holder | R3 lock follows work | R4 nesting | R5 Linux | R6 status | Verdict |
|---|---|---|---|---|---|---|---|
| macOS `lockf` command mode only | yes | no | no (M2, M3, M11) | no | no | busy/free | Reject: breaks every caller's `pass_fds` guarantee |
| `lockf` or `flock -n 9` descriptor idiom | yes for `-t 0`; spins for `-t N` on macOS | no | yes (M10) | yes (M6) | per-OS branch | busy/free | Acceptable zero-code fallback for fail-fast callers only |
| Existing CLI (util-linux via Homebrew on macOS; quodlibetor/flock) | yes | no; quodlibetor sidecar in wrap mode | util-linux yes; quodlibetor no | descriptor idiom | yes | rc only | Reject: each misses R2 or R3, both need an install admission |
| Rust crate behind a C++ bridge | caller-built | caller-built | caller-built | caller-built | yes | caller-built | Reject: adds cargo, cxx or cbindgen and Corrosion for a `flock` call |
| Small C++ heavy-gate (R6 7.2 plus CLI) | yes | yes | yes | refuse, opt-in re-entry | yes | yes | Recommend |

Shape notes for the C++ gate (proposal, not found code): open the D124 path with `O_RDWR | O_CREAT` and
without `O_CLOEXEC` for the `run` child, never unlink or truncate on open; `try_lock_for` polls `LOCK_NB`
once a second (no spinning, unlike macOS `lockf` descriptor mode); write the record after acquiring and
truncate it before `LOCK_UN`, as mise does (R6 section 4); export the descriptor number to the command
and keep HL's exit 124 on timeout (HL:290-297); `status` prints the record or `free`; refuse when an
inherited gate descriptor is present unless the caller opts in, then accept only the R6 7.1 proof (device
and inode match, `LOCK_EX | LOCK_NB` succeeds on that descriptor). For D125 the 27 scripts would then run
as `heavy-gate run --label <their label> --wait 0 -- <script>`, delete the dotfiles import and digest pin,
and keep `pass_fds` on the exported descriptor; their admission records that bind helper digests need
re-review (R6 7.3). Two consequences of D124 and D125 to plan for, not decided here: until dotfiles moves to
the new path, dotfiles heavy jobs and MP heavy jobs no longer exclude each other; and while units are
half-migrated, migrated and unmigrated scripts do not exclude each other.

## 6. Comparison table

| Option | Timeout | Holder name | Crash release | Re-entry | Linux parity | Status query | Maintenance | Licence | Citation |
|---|---|---|---|---|---|---|---|---|---|
| macOS `lockf` command mode | `-t` whole seconds; rc 75 after 2.02 s (M1); `-t 0.5` rc 64 | no; no `-p` (rc 64) | kernel, but freed when the wrapper dies while the command runs (M2, M3, M11) | no (nested rc 75, R6) | no lockf on Linux | `-k -s -t 0 P true` rc 0/75; without `-k` deletes the file (M7) | Apple shell_cmds-334; base FreeBSD 2023-11-26 | BSD-2-Clause | `O11/repos/shell_cmds/lockf/lockf.c:179-255,308-316`; `S11/probe/lockf-probes.txt` |
| macOS `lockf` descriptor idiom | `-t 0` fine; `-t N` busy-polls (R6) | no | kernel, follows the work (M10) | yes, inherited fd re-lock rc 0 (M6) | same idiom with `flock -n 9` | as above | as above | BSD-2-Clause | `lockf.c:211-213,269-277`; `S11/probe/lockf-fd-follow.txt` |
| FreeBSD `lockf` (main) | as above, no spin since 2026-05-03 | `-p`: child PID only | `-T` forwards SIGTERM to the child | no | n/a (not on macOS or Linux) | no | active (d90513ea85) | BSD-2-Clause | `O11/files/freebsd/lockf.c:128-138,296-297,366-375`; `lockf.1:126-156` |
| util-linux `flock(1)` | `-w` fractional, `-n`, `-E` | no | kernel, command inherits; `-F` execs in place | descriptor or `FLOCKER` idiom | native; macOS via keg-only Homebrew util-linux 2.42.4 (unmeasured) | `-n` rc; `lslocks` PID on Linux | active (PR #4680, 2026-10-13) | MIT | `O6/repos/util-linux/sys-utils/flock.1.adoc:62-104`, `flock.c:121-122,487-495` |
| discoteq `flock` (Homebrew) | `-w` fractional, `-n`, `-E` | no | kernel, command inherits | descriptor mode | conflicts with util-linux on Linux | rc only | v0.4.0 2020-04-24; PR #43 unreleased | ISC | `O6/repos/discoteq-flock/src/flock.c:207-223,268-275`; `O11/files/homebrew/flock.rb` |
| quodlibetor/flock (Rust CLI) | `-w` fractional, `-n`, `-E` | sidecar `<lock>.holder`, wrap mode only | kernel, freed with the wrapper (O_CLOEXEC; code reading) | descriptor mode | same binary | none (`-n -v`) | v0.0.4 2026-08-01, 0 stars, "vibe coded" | MIT OR Apache-2.0 | `O11/repos/quodlibetor-flock/README.md:23,200-227`; `src/main.rs:296-298,489-497,578-610` |
| tuulbelt sema, sirech/lock, lockito | sema `--timeout`; others none | sema PID | sema age-based stale; sirech record lock | no | yes | sema yes | small, 2021 to 2026; lockito 404 | MIT | `O11/repos/tuulbelt-sema/src/lib.rs:109-121,352-355`; `O11/repos/sirech-lock/Cargo.toml:9-13` |
| Qt `QLockFile` | `tryLock(ms)`, backoff to 5 s | pid, hostname, app | file plus flock liveness; stale removal (30 s default) | no (deadlocks) | yes | `getLockInfo` after failure | active | LGPL-3.0-only, GPL, commercial | `O11/docs/cpp/qt6-qlockfile.md:40-71,237,264`; `qlockfile_unix.cpp:111-140,259-277` |
| LLVM `LockFileManager` | `waitForUnlockFor(s)` | `hostname pid` | no kernel lock; dead owner via `getsid`; "weak mutual exclusion" | no | yes | private `readLockFile` | active (PR #130989, #182722) | Apache-2.0 WITH LLVM-exception | `AdvisoryLock.h:27-46`; `LockFileManager.cpp:115-125,189-241,288-313` |
| LLVM `sys::fs::tryLockFile` | timeout poll | no | `fcntl` record lock | no | no interop with `flock` on Linux | no | active | Apache-2.0 WITH LLVM-exception | `Unix/Path.inc:1321-1376` |
| Poco `NamedMutex` | none | no | Linux yes (SEM_UNDO); macOS no (named semaphore) | no | semantics differ | no | 1.15.4; open #4876 | BSL-1.0 | `NamedMutex_UNIX.cpp:21,56-71,116`; `NamedMutex.h:65-74` |
| folly `File` | none | no | kernel `flock` | no | yes | no | active | Apache-2.0 | `File.h:145-158`; `File.cpp:172-199` |
| LLFIO | none for whole file | no | kernel `flock` | no | yes | no | last commit 2026-08-24 | Apache-2.0 or BSL-1.0 | `O6/repos/llfio/.../lockable_byte_io_handle.hpp:109-121,268` |
| abseil, stlab, GLib | n/a | n/a | n/a | n/a | n/a | n/a | no public cross-process lock | n/a | `S11/gh/code/*.json`; `O11/files/glib/gdbusauthmechanismsha1.c:527-625` |
| Rust std `File::lock` | none | no | kernel `flock` | no | yes | no | stable 1.89.0 | MIT OR Apache-2.0 | `O11/docs/rust/std-fs-file.md:386-496` |
| fs4, fd-lock, fmutex, named-lock | none | no | kernel `flock` | no | yes | no | 2024 to 2026 | MIT OR Apache-2.0; named-lock MIT | `O6/repos/fs4-rs`, `fd-lock`, `fmutex`; `O11/docs/rust/docsrs-named-lock-NamedLock.md:45` |
| fslock | none | PID only, erased on unlock | kernel `flock` | no | yes | no (open #13) | 0.2.1, 2021 | MIT | `O11/docs/rust/docsrs-fslock-LockFile.md:242-245` |
| filelock (aisk), harn-flock | `lock_timeout` 1 to 50 ms poll; deadline | no | kernel `flock` | no | yes | no | 2026 | MIT | `O11/repos/rust-filelock/src/lock.rs:8-9,135-147`; `O11/docs/rust/docsrs-harn-flock.md` |
| pidlock, lockfile, file-guard | none | pidlock PID | PID staleness; file-guard record locks | no | file-guard no interop | no | 2022 to 2025 | MIT | `O11/repos/pidlock/src/lib.rs:461,728`; `O11/repos/file-guard/src/os/unix.rs:30-51` |
| Proposed C++ heavy-gate | `try_lock_for`, `--wait S`, 124 | record in the lock file | kernel `flock`, descriptor inherited and exported | refuse; opt-in proven re-entry | same code | `status` | ours | ours | R6 section 7.2; section 5 here |

## 7. Code examples found

| Repository | Path and lines | Commit or permalink | What it shows |
|---|---|---|---|
| apple-oss-distributions/shell_cmds | `lockf/lockf.c:210-255,308-316` | https://github.com/apple-oss-distributions/shell_cmds/blob/298787009e5432c5e4c378a077f98267077e3495/lockf/lockf.c#L210-L316 | macOS lockf: child closes the lock fd; SIGTERM unlocks and orphans |
| freebsd/freebsd-src | `usr.bin/lockf/lockf.c:128-138,296-297,366-375` | https://github.com/freebsd/freebsd-src/blob/d90513ea85693da0ca5955173609f4e81e38ae16/usr.bin/lockf/lockf.c | `-p` PID write, `-T` SIGTERM forwarding, no-spin fd mode |
| util-linux/util-linux | `sys-utils/flock.c:121-122,487-495` | https://github.com/util-linux/util-linux/blob/d427f58b7a22b960ccc8d02ce30c58bdbe4286d8/sys-utils/flock.c | Command inherits the lock unless `-o`; `-F` |
| discoteq/flock | `src/flock.c:28-85,268-275,318-363` | https://github.com/discoteq/flock/blob/419b608c7d1b7f30d86b73be5e224413d07925f3/src/flock.c | Portable flock CLI, `fcntl` fallback |
| quodlibetor/flock | `src/holder.rs`; `src/main.rs:205-234,578-610` | https://github.com/quodlibetor/flock/blob/d664253247f016cee7ed86f01856a4b4245d8ad6/src/holder.rs | Holder sidecar; timed wait by helper thread |
| qt/qtbase | `src/corelib/io/qlockfile_unix.cpp:104-140,154-185` | https://github.com/qt/qtbase/blob/f23b87a4db2d10a43e2a6c8b2d5a00eccc366ab6/src/corelib/io/qlockfile_unix.cpp | Why Qt uses only `flock(2)` and `O_EXCL` |
| llvm/llvm-project | `llvm/lib/Support/LockFileManager.cpp:115-125,189-313` | https://github.com/llvm/llvm-project/blob/c4d25e2fa557463d987e882c6709d3498863e22c/llvm/lib/Support/LockFileManager.cpp | Owner record and backoff wait without a kernel lock |
| pocoproject/poco | `Foundation/src/NamedMutex_UNIX.cpp:21-137` | https://github.com/pocoproject/poco/blob/600ff852d02b2e54234e6adfc27d63435816fdf2/Foundation/src/NamedMutex_UNIX.cpp | Per-OS semaphore choice |
| facebook/folly | `folly/File.cpp:172-199` | https://github.com/facebook/folly/blob/4fbf9f36aa7da4c52ad6319f148e8c287b9cbc22/folly/File.cpp | Lockable over `flock` |
| aisk/rust-filelock | `src/lock.rs:135-200` | https://github.com/aisk/rust-filelock/blob/abb3b45bb1ad6fdb41dee78ca7e255b4de2669e5/src/lock.rs | Timed wait over std `File::lock` |
| ray-manaloto/dotfiles | `python/src/dotfiles_setup/pr.py:758`; `mise.toml:320-323` | local `7744a9c6` | The only nesting path (ship then pre-push) |

## 8. Routes

Every provider call ran under `fnox --config ~/.config/fnox/config.toml --profile codex_research
--no-defaults --no-daemon --non-interactive exec --` (wrapper `S11/bin/fx`); keys were read from the
environment inside the called script and never printed (presence check only).

| Stage | Route | Command shape | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Exa | `fx exa.sh <out> "<query>" 10` x8 (POST api.exa.ai/search) | 0, HTTP 200 each | 10 each | Yes: QLockFile, LockFileManager, Poco issues, discoteq, filelock, pidlock, sirech/lock, tuulbelt, lockito, ARC FileLock |
| 1 | Context7 | `fx ctx7 library <qt, llvm, folly, poco, fs4>` x5 | 1 each | "Monthly quota reached" | No; gap |
| 1 | Firecrawl | `fx firecrawl search "<query>" --limit 5 --json` | 1 | HTTP 402 insufficient credits | No; gap |
| 1 | webclaw | `webclaw <url> -f markdown` x34 (one duplicate dropped) | 0 x30, 1 x3 | 30 pages in `O11/docs` | Yes; crates.io page (no content), docs.rs lockito (404) and packages.ubuntu.com (failed) stay gaps |
| 1 | Serper | `fx serper.sh <out> "<query>"` x5 | 0, HTTP 200 each | 10, 2, 10, 10, 10 | Yes: found quodlibetor/flock and FreeBSD lockf(1) |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3 -I last30days.py --plan plan.json --emit md --quick --save-dir "" --search reddit,hackernews,github,x "<topic>"` (after `--help`) | 0 | 12 off-topic items; planner kept 1 of 3 subqueries; rerank HTTP 503 | No; gap |
| 1 | crates.io API | `curl https://crates.io/api/v1/crates?q=<q>&per_page=25` x6 | 0 each | totals 11620, 301, 1746, 10681, 716, 7978 | Yes: crate list, versions, dates |
| 1 | Clones | `clone.sh` (shallow; sparse for qtbase, llvm-project, poco, folly, shell_cmds) x15 | 0 x14, 128 x1 | 13 kept | lockito: repository not found; `file_cmds` removed as the wrong project (lockf is in shell_cmds) |
| 1 | Raw files | `gh api -H 'Accept: application/vnd.github.raw' repos/<repo>/contents/<path>?ref=main` x5 | 0 each | FreeBSD lockf.c, lockf.1; Homebrew util-linux.rb, flock.rb; GLib file | Yes |
| 1 | Local | `what /usr/bin/lockf`; `/usr/bin/lockf -p/-T/-t 0.5` | 0; 64 x3 | provenance, missing options | Yes |
| 1 | Local probes | `S11/probe-scripts/lockf-probes.sh`, `lockf-fd-follow.sh` | 0 | M1 to M11 | Yes |
| 2 | gh search issues (burst) | `gh search issues --repo <r> "<q>" --include-prs` x18 | 1 x13 (HTTP 403 secondary rate limit), 0 x5 | fslock 15, named-lock 15, cxx 15, 2 global 0 | Partly; rerun paced |
| 2 | gh search issues (paced, 9 s apart) | x10 | 0 x9, 1 x1 (`al8n/fs4-rs` renamed to `al8n/fs4`) | util-linux 15, llvm 15 and 5, poco 11, folly 1, llfio 5, rust 0, fd-lock 0, fslock 6 | Yes: util-linux #2993, #4553, #4680; llvm #130989, #182722; poco #4876, #4204; fslock #6, #13 |
| 2 | gh issue/pr list | discoteq/flock, quodlibetor/flock | 0 each | 28 and 17; 0 and 8 | Yes |
| 2 | gh issue/pr view | discoteq #40, PR #43; poco #4876; fslock #6, #13; llvm PR #130989, #182722; util-linux PR #4553 | 0 each | 8 | Yes |
| 2 | gh release list | discoteq/flock, quodlibetor/flock | 0 | v0.4.0 (2020-04-24); v0.0.4 (2026-08-01) | Yes |
| 2 | Commit history | `gh api repos/<r>/commits?path=<p>` (FreeBSD lockf.c, util-linux flock.c) and 3 FreeBSD commit messages | 0 | 8, 40 | Yes |
| 2 | GraphQL DISCUSSION | `gh api graphql` search x4 | 0 each | 10, 13, 4, 2, none on topic | No |
| 2 | search/code | `flock` in abseil, stlab, GLib (+ `F_SETLK`, `lockf` in GLib) with `README` controls | 0 each | 0, 0, 1, 0, 1; controls 5, 18, 8 | Yes (absence) |
| 2 | Saved searches (task) | `./dev/mise run research:collect` | not run | n/a | writes a tracked path another lane owns |
| 2 | Saved searches (reproduced) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5` plus `README` control x6 | 0 each | section 9 | Yes |

## 9. Proposed saved-search rows

Reproduced read-only (`S11/gh/code/ss_*.json`), schema as `MP/dev/saved-searches.toml:3-40`.

```toml
[[search]]
id = "freebsd-lockf-writepid"     # 5 hits incl. usr.bin/lockf/lockf.c; control README 1504
query = "writepid"
repo = "freebsd/freebsd-src"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "apple-lockf-exlock"         # 1 hit lockf/lockf.c; control README 1
query = "O_EXLOCK"
repo = "apple-oss-distributions/shell_cmds"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "quodlibetor-flock-holder"   # 10 hits; control README 2
query = "holder"
repo = "quodlibetor/flock"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "util-linux-flock-nofork"    # 2 hits incl. sys-utils/flock.c; control README 18
query = "no_fork"
repo = "util-linux/util-linux"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "qt-qlockfile-lockinfo"      # 4 hits; control README 62
query = "getLockInfo"
repo = "qt/qtbase"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "llvm-lockfilemanager-owner" # 2 hits; control README 423
query = "processStillExecuting"
repo = "llvm/llvm-project"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

## 10. Open gaps

- Linux behaviour of util-linux `flock(1)` and of Homebrew `util-linux` `flock` on macOS is read from source
  and manuals, not measured (no install, no container admission). Which util-linux version GitHub's
  `ubuntu-latest` ships, and so whether `--fd` is available there, is UNVERIFIED (packages.ubuntu.com fetch
  failed).
- quodlibetor/flock's wrap-mode release on wrapper death is inferred from code (Rust std `O_CLOEXEC`), not
  measured (nothing built or installed).
- Whether a FreeBSD `lockf -p` waiter opening with `O_TRUNC` can clear a holder's PID before the lock is
  refused was not checked; irrelevant on macOS, which lacks `-p`.
- Context7 (monthly quota), Firecrawl (HTTP 402) and Last30Days (off-topic, rerank 503) gave nothing; the
  first GitHub search burst hit the secondary rate limit and was rerun paced; Qt bugs live in Qt's JIRA,
  which was not searched.
- The C++ gate size (about 200 lines) is an estimate. D124's single path leaves dotfiles and MP heavy jobs
  mutually unexcluded until dotfiles switches, and D125's units leave a half-migrated window; both are
  consequences to schedule, not findings about libraries.
