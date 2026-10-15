# R6: Host-wide heavy-job lock implementation (research round 5, 2026-10-14)

Written by research agent R6 of session `ccm-20261014` (`ce9c0b3d`) for D109 and the user's comment on
https://claude.ai/artifact/GvGdjrMg7GzPoxfpLmaY37. Read-only except this file and the untracked offline
corpus. MP at `21af565`, branch `codex/marketplace-native-onboarding`. DF (dotfiles) checkout at `7744a9c`;
its `python/src/dotfiles_setup/host_lock.py` was last changed in `c91d9d6` (2026-10-11) and hashes to
`b20e5d96...`, the pin MP uses today.

Citation keys. MP = `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`. O =
`MP/offline/research/R6/` (the D110 mirror; `O/manifest.json` lists all 68 items with URL, time, command,
exit code and SHA-256 or commit). Clones live at `O/repos/<name>` and are cited as `<name>:path:line` at
the commit in section 9. S = `/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/research5/R6/`
(search results, probe scripts and probe output). HL = `DF/python/src/dotfiles_setup/host_lock.py`.
P = `MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. Probe results labelled P1 to P8 come
from `S/probe-scripts/probe.py`, output `S/probe-macos.json`, run on this Mac (macOS 27.0.1, 26A434, APFS)
with `/usr/bin/python3` 3.9.6; the lockf and lsof probes are in `S/probe-lockf-lsof.txt`.

## Verdict

Recommendation for the open D109 fork (implementation): keep the kernel primitive the system already
uses, BSD `flock(2)` reached through Python's stdlib `fcntl.flock`, and give MP its own small module plus a
`run`/`status` command line, ported from HL rather than replaced. Three changes over HL:

1. Re-entry for descendants only through an inherited descriptor, proven twice: the descriptor's device
   and inode equal the lock file's, and `flock(fd, LOCK_EX | LOCK_NB)` on that descriptor succeeds. Drop
   the PID export (HL:196-203).
2. A lock path named for this repository, `${XDG_STATE_HOME:-$HOME/.local/state}/claude-code-marketplace/heavy-gate.lock`,
   taken first, and the legacy `~/.local/state/dotfiles/heavy-gate.lock` taken second, always in that
   order, until the dotfiles sunset. This is exactly how mise migrated its daemon lock (section 4).
3. The holder record (`pid<TAB>label<TAB>since`, unchanged so old dotfiles waiters can still read it) is
   written into both files and truncated on release, as mise does since PR #13588, so a waiter never names
   a stale holder.

Do not use bemanproject/timed_lock_alg for this: it is a header-only algorithm that locks several
in-process *TimedLockable* objects without deadlock; it has no operating-system primitive and does not
provide cross-process or host-wide exclusion. No C++26 or reflection-based lock library exists, and
reflection has no role in the lock itself. Later C++ callers should run under the gate and inherit the
descriptor (no lock code in C++ at all); a C++ orchestrator that must take the gate itself should use a
small RAII type over POSIX `flock` that models *Cpp17TimedLockable*, which then composes with
`std::unique_lock` and with P3832's `try_lock_for` if it is standardised. Confidence: high for the
primitive and the re-entry design (measured here and matched by two independent implementations), medium
for the exact path string (a naming choice D109 leaves open).

Evidence that decides it:

1. `flock` is the one primitive every candidate agrees on. Python `filelock` 4.1.1
   (`filelock:src/filelock/_unix.py:18,50,58`), `portalocker` 4.4.0 (`portalocker:portalocker/portalocker.py:878-882`),
   mise's `fslock` 0.2.1 (`fslock:src/unix.rs:322` at tag v0.2.1), Rust `std::fs::File::lock`, stable since
   1.89.0 (`rust:library/std/src/fs.rs:846,874`; `rust:library/std/src/sys/fs/unix.rs:1300-1320`), `fs4`
   (`fs4-rs:src/unix.rs:10-56`), `fd-lock` (`fd-lock:src/sys/unix/mod.rs:11-20`), LLFIO
   (`llfio:include/llfio/v2.0/detail/impl/posix/lockable_byte_io_handle.ipp:55-77`), macOS `lockf(1)`
   ("BSD-style locking is used, as described in flock(2)", `O/man/macos-lockf.1.txt:15-17`) and
   util-linux `flock(1)` all call `flock(2)`. Boost.Interprocess is the exception: its POSIX `file_lock`
   uses `fcntl(F_SETLKW)` record locks and keeps the `flock` code under `#if 0`
   (`interprocess:include/boost/interprocess/detail/os_file_functions.hpp:651-668,714`), and on Linux the
   two families do not interact ("there is no interaction between the types of lock placed by flock() and
   fcntl(2)", `O/docs/man7/flock.2.md:118-124`). On this Mac they do interact (P1, P1b, P6), so a mixed
   choice would pass every local test and fail on Linux CI.
2. Inherited-descriptor re-entry works and the PID trick is unnecessary. A child given the holder's
   descriptor re-locks it at once while an unrelated opener gets "busy" (P2); `flock` locks belong to the
   open file description and survive `execve` (`O/docs/man7/flock.2.md:60-80`; macOS
   `O/man/macos-flock.2.txt:43-47`). dc0sk/OpenPulseHF PR #1459 (merged 2026-10-03) fixed a 67-minute
   self-deadlock of a cross-project host build lock with exactly this check
   (`O/files/dc0sk-OpenPulseHF/host-build-lock.sh:28-41`). mise discussion #10512 (2026-06-17) shows the
   failure mode without it: a nested `mise run` inside a held install lock deadlocks.
3. mise's own lock code (asked in Q3) supplies the migration pattern: `ProjectLock` holds a new sibling
   lock and a legacy lock, "Acquired sibling first, then legacy, by everything that takes both, so they
   cannot deadlock", until "no supported version locks this path" (`mise:src/daemons/mod.rs:237-298`,
   PR #13338, merged 2026-09-19).
4. timed_lock_alg's whole surface is `try_lock_until`, `try_lock_for` and `multi_lock` over types with
   `try_lock_until` members (`timed_lock_alg:include/beman/timed_lock_alg/mutex.hpp:27-34,102-117,119-264`);
   P3832R3 extends "the `std::lock` family of functions to timed lockables"
   (`timed_lock_alg:papers/P3832.md:44-58`); status: SG1 design approved 2025-11-05, LEWG-I feature-test
   poll 2026-06-12, still open (cplusplus/papers#2438).
5. The alternatives fail named constraints: Boost `named_mutex` on macOS is a POSIX named semaphore and
   macOS process-shared primitives are "unrecoverable under process crashes while holding the lock"
   (`interprocess:doc/interprocess.qbk:6795-6799,6905-6906`); GNU make style jobservers lose tokens when a
   client is killed ("Returning too few slots means that those slots will be lost", `O/docs/gnu-make/Job-Slots.md`;
   the system-wide fixes, steve and guildmaster, need Linux CUSE, `O/docs/jobserver/gentoo-one-jobserver.md`);
   macOS `lockf(1)` and util-linux `flock(1)` cannot re-enter (nested `lockf` fails with rc 75,
   `S/probe-lockf-lsof.txt`) and name no holder; `F_OFD_SETLK` exists on macOS only in the new SDK
   (`O/man/macos-sdk-sys-fcntl.h:309-315`) and is absent from the macOS 14.8.5 manual
   (`O/docs/man-macos/fcntl-macos-14.8.5.md`, 0 matches for "OFD").

## 1. What the current lock does, and where it is weak

HL takes `fcntl.flock(fd, LOCK_EX | LOCK_NB)` on a file at a well-known path so every checkout serialises
(HL:10-15, 145-150), polls once a second for a bounded wait (default 3600 s, `DOTFILES_HEAVY_GATE_WAIT`)
and prints the holder record every 60 s (HL:72-76, 230-263), writes `pid<TAB>label<TAB>since` into the
lock file after acquiring it (HL:205-209), opens with `"a+"` so a contender never truncates the holder's
record (HL:193-195), and exits 124 from its CLI on timeout (HL:290-297). Crash safety is the kernel's: a
killed holder's descriptor closes and the lock frees (HL:11-14; confirmed by P4).

MP's use: 27 files in `MP/dev/toolchains/` (list in `S/mp-callers.txt`) import `LOCK_MODULE` and
`LOCK_SHA` from `p2996_configure.py:19-20`, assert the file's digest, load it with
`importlib.util.spec_from_file_location`, assert the lock path equals `~/.local/state/dotfiles/heavy-gate.lock`,
assert no holder export is inherited, and call `held(HEAVY_GATE, label, wait_s=0)`
(`MP/dev/toolchains/p2996_configure.py:146-153`; `baseline.py:107-112`). They pass the locked descriptor
to children with `pass_fds` and verify its device and inode in the child (`p2996_configure.py:176-181`).
So MP's callers never nest and already use the strong form; the weak form is DF's.

Weaknesses of the PID export (HL:196-203, 210-214):

- A descendant that finds the lock busy and sees `DOTFILES_LOCK_HOLDER_HEAVY_GATE` equal to the recorded
  PID proceeds holding nothing. If the ancestor dies, the kernel frees the lock and the descendant keeps
  running unprotected while another heavy job starts.
- Any process that inherits the environment passes the test: the variable is set in `os.environ` for the
  whole hold, so every process spawned during it (including detached helpers) carries it.
- The check proves ancestry by a PID string, not by the kernel. The inherited-descriptor check proves it
  by the kernel: only a process sharing the holder's open file description can re-lock it (P2).
- HL already has half of the strong form: `inherited_heavy_lock_fd()` validates device and inode of
  `DOTFILES_HEAVY_GATE_FD` (HL:101-119), but `held()` decides re-entry by PID first.

Two inherited-descriptor caveats must be documented, not fixed: a child that calls `LOCK_UN` on the
shared descriptor drops the parent's lock (P8; `O/man/macos-flock.2.txt:45-47`), and a long-lived process
that inherits the descriptor keeps the gate held after the holder dies (P5: busy after the holder's
`kill -9`, free only after the grandchild exited). The latter is why util-linux added `flock -o` ("useful
if command spawns a child process which should not be holding the lock",
`util-linux:sys-utils/flock.1.adoc:77-78`) and why curlewlabs-com/local-mutex insists on it
(`local-mutex:lib/local-mutex.sh:33-38`). OpenPulseHF records the same two caveats as parked
("an inherited but unlocked fd 9 is reported as held, and siblings of a holder run concurrently",
PR #1459 body).

## 2. Q1: bemanproject/timed_lock_alg

Mirrored at `O/repos/timed_lock_alg` (`e52c949`, 2026-10-08), papers at `O/docs/wg21/P3832R3.md`,
`O/docs/wg21/p3832-latest.md` (resolves to R3, dated 2026-06-15), `O/docs/wg21/P3833R3.md` (webclaw kept
only headings; the repo copy `papers/P3833.md` was read instead).

What it provides, exactly:

- Two function templates, `try_lock_until(time_point, Ls&...)` and `try_lock_for(duration, Ls&...)`,
  returning -1 on success or the index of the lockable being attempted at the deadline
  (`mutex.hpp:102-117`; `papers/P3832.md:121-136`). The algorithm calls `try_lock_until` on one lockable
  and `try_lock` on the rest, unlocks and retries with a rotated order, with `std::this_thread::yield()`
  between rounds (`mutex.hpp:70-99`). With one lockable it is just `l.try_lock_until(tp)` (`mutex.hpp:106-107`).
- `multi_lock<Ms...>`, a variadic RAII holder combining `unique_lock` and `scoped_lock` features
  (`mutex.hpp:119-264`; P3833R3, tracked as cplusplus/papers#2546 under the title `std::unique_multilock`, LEWG, open).
- Concepts `BasicLockable`, `Lockable`, `TimedLockable`; `TimedLockable` requires `try_lock_for` for
  nanoseconds, microseconds and milliseconds and `try_lock_until` for both `steady_clock` and
  `system_clock` (`mutex.hpp:15-34`).
- Status: "Under development and not yet ready for production use", targets C++29
  (`README.md:12,21`); Apache-2.0 WITH LLVM-exception.

Cross-process, host-wide exclusion: not covered. The header includes only `<mutex>`, `<thread>`,
`<chrono>` and friends (`mutex.hpp:6-13`), names no file, semaphore or shared-memory API, and every
example and test uses `std::timed_mutex` or a mock (`examples/`, `tests/beman/timed_lock_alg/mock_timed_mutex.hpp`).
The paper never mentions processes (`papers/P3832.md`, whole file). GitHub: 12 issues, all scheduled-build
failures, 46 PRs, and no issue or discussion about processes or files (`S/gh/beman-issues.json`,
`beman-s1.json` "interprocess" 0 hits; GraphQL discussions for `timed_lock_alg` 0; Serper S1 0 hits).

Honest role: if MP writes a C++ host-gate type that models *TimedLockable*, the beman algorithms (and
`std::unique_lock`) accept it, so a C++ caller could take the new and legacy gate files together with
`try_lock_for(1h, gate_new, gate_legacy)` without a fixed order. For one lock it adds nothing over the
type's own `try_lock_for`.

## 3. Q2: C++ cross-process locks, and whether reflection has a role

| Option | Primitive | Crash safety | Bounded wait | Fit |
|---|---|---|---|---|
| POSIX `flock(2)` directly | open file description lock | kernel frees on last close (P4) | poll with `LOCK_NB` | Best: same lock as Python, Rust and the CLIs |
| Boost.Interprocess `file_lock` | `fcntl(F_SETLK/F_SETLKW)` whole-file record lock (`os_file_functions.hpp:651-668`) | "process lifetime ... ends or crashes, the operating system will automatically unlock" (`interprocess.qbk:2632-2636`) | `timed_lock`, `try_lock_until`, `try_lock_for` (`file_lock.hpp:163-173`) | No: POSIX record locks drop "all file locks set by the calling process" when any descriptor of the file closes (`interprocess.qbk:2826-2830`; macOS `fcntl(2)` calls this "completely stupid semantics", `O/man/macos-fcntl.2.txt:269-287`), do not pass to children, and do not interoperate with `flock` on Linux |
| Boost `named_mutex` | POSIX named semaphore on macOS (`interprocess.qbk:6905-6906`) | No: macOS process-shared primitives are "unrecoverable under process crashes" (`interprocess.qbk:6795-6799`); boostorg/interprocess#65 (2018, closed 2021) asked for robust mutexes | timed | No |
| LLFIO `lockable_byte_io_handle::lock_file()` | `flock(LOCK_EX)` (`lockable_byte_io_handle.ipp:55-77`); byte ranges via `F_OFD_SETLK` when defined (`:130-135`) | kernel | `deadline` on ranges | Compatible primitive, but a large dependency; its `shared_fs_mutex::lock_files` leaves stale files after a crash on POSIX (`lock_files.hpp:57-59`); P1883R2 (2022-11-25) is labelled `needs-revision`, `outdated-or-needs-champion` (cplusplus/papers#633) |
| `fcntl(F_OFD_SETLK)` | OFD record lock | kernel | Linux none; macOS `F_OFD_SETLKWTIMEOUT` (`macos-sdk-sys-fcntl.h:309-315`) | Linux 3.15+ (`O/docs/man7/fcntl_locking.2.md:193-198`); on macOS present in the 27 SDK and the xnu-12377 manual (`O/docs/man-macos/xnu-fcntl.2.md`, 23 "OFD" lines) but not in the macOS 14.8.5 manual, so CI runners may lack it. Python exposes the constants only on Linux (`O/docs/python/fcntl.md:26`) |
| beman `timed_lock_alg` | none | n/a | algorithm over lockables | Not a lock (section 2) |
| P3771R1 constexpr mutex | none | n/a | n/a | Makes `std::mutex` usable in constant evaluation; LEWG Brno 2026-06 "No consensus" (`O/docs/wg21/p3771r1.md`, Timeline) |

Reflection: P2996 reflects program entities at compile time; locking is a kernel property of an open file
description, so nothing about acquisition, crash release or re-entry can come from reflection. Searches for
a reflection-based lock library found none (Exa Q2 returned P2996 papers, P3771 and Glaze's P2996 page;
Serper S2 three unrelated pages; GitHub `"P2996" "flock"` issue search 1 unrelated hit, `S/gh/issues/cpp-p2996-lock.json`).
The only honest uses are around the lock: serialising the holder record struct (Glaze already offers a
P2996 backend, `O/docs/cpp/glaze-p2996-reflection.md`) or generating the `run`/`status` option parser.
Neither is worth a dependency for a three-field line.

## 4. Q3: how mise handles locks

Mirrored at `O/repos/mise` (`a123781`, 2026-10-14, version 2026.10.10).

- Crate: `fslock = "0.2"` (`mise:Cargo.toml:149`; `crates/mise-util/Cargo.toml:34`), locked to 0.2.1
  (`Cargo.lock`, checksum `04412b89...`). fslock opens with `O_RDWR | O_CLOEXEC | O_CREAT` and locks with
  `libc::flock(fd, LOCK_EX)` (`fslock` v0.2.1 `src/unix.rs:266,322`). No `fs4`.
- Wrapper: `crates/mise-util/src/lock_file.rs` (re-exported by `src/lock_file.rs:1`). `LockFile::new`
  hashes the guarded path into `$MISE_CACHE_DIR/lockfiles/<hash>`; `LockFile::at` locks an exact path and
  warns "The file must remain in place while any process could hold its lock" (`lock_file.rs:18-32`).
- Wait: `try_lock()` first; if busy, run the `on_locked` callback and the borrowed `on_wait` notice, then a
  blocking `lock()` with no timeout (`lock_file.rs:59-73`). Bounded only by the caller.
- Naming the holder: optional `with_pid()` writes the holder PID into the lock file after acquiring, best
  effort, and "Unlocking erases the PID so a later waiter never names a stale holder"
  (`lock_file.rs:42-48,88-122`; test `:162-184`). Added by PR #13588 (merged 2026-09-24) after #13581,
  where a stalled shim install looked like a leaked lock and "led to killing the wrong processes".
- Scope: per resource, never host-wide. Call sites include tool installs (`src/install_layout/resolver.rs:1089-1101`),
  HTTP downloads (`crates/mise-util/src/http.rs:1418,1630`), config writes (`src/config/config_file/mod.rs:470`),
  venv creation (`src/config/env_directive/venv.rs:287`), task cache entries (`src/task/task_cache.rs:1135-1139`)
  and daemon state (`src/daemons/mod.rs:237-298`).
- Holder death: the kernel frees `flock` when the process exits; the lock file stays (test
  `lock_file.rs:143-160`, "Unlocking keeps the file in place").
- Tasks: mise has no cross-process task gate. `raw` and `interactive` take an exclusive lock "from the
  task's first script command to its last" (`mise:docs/tasks/task-configuration.md:845-870`), but that lock
  is a process-local `tokio::sync::RwLock` (`crates/mise-util/src/cmd.rs:476`). GitHub: `task mutex`,
  `task lock concurrent processes` and `exclusive task` issue searches return 0 (`S/gh/mise-*.json`);
  discussions found only install-lock deadlocks (#4489, #10512).
- Migration precedent: the daemon `ProjectLock` described in the verdict (`src/daemons/mod.rs:253-298`).

## 5. Python, Rust, command-line and job-slot options against the constraints

Constraints: crash safety (C), bounded wait naming the holder (W), descendant re-entry (R), one path
usable by dotfiles and knowledge-base (P), macOS and Linux CI (X), no network (N; all options are local).

| Option | C | W | R | P | X | Notes |
|---|---|---|---|---|---|---|
| stdlib `fcntl.flock` module (HL port) | yes (P4) | yes, HL format | yes, by inherited fd (P2) | yes | yes | Recommended. No new dependency for 27 hash-pinned scripts |
| `filelock` 4.1.1 | yes | timeout yes; native lock records no holder (only `SoftFileLock` markers name PID, host, start token, `filelock:docs/index.rst:75-81`) | no cross-process re-entry; a fork shares the lock (`filelock:docs/concepts.rst:513-525`) | yes, same `flock` | yes | Leaves the file in place because unlinking "splits waiters across inodes" (`_unix.py:60-67`); adds a dependency |
| `portalocker` 4.4.0 | yes | `timeout`, `check_interval` (`utils.py:495-520`); no holder record | no | yes (`FlockLocker` default) | yes | `BoundedSemaphore` = N slot files, each a `flock` (`utils.py:3020-3050`): the crash-safe design if the gate ever becomes N slots |
| macOS `/usr/bin/lockf -k -t S path cmd` | yes | timeout yes, holder no | no (nested rc 75) | yes (P3: rc 75 against a Python `flock` holder) | macOS only | Without `-k` it deletes the file on exit (`macos-lockf.1.txt:11-17,36-37`), the dead-inode split of P7; descriptor mode busy-polls one core (user 0.60 s plus sys 2.38 s in 3.01 s, `S/probe-lockf-lsof.txt`) |
| util-linux `flock -w S [-o] path cmd` | yes | timeout yes, holder no | only the `flock -n 9` descriptor idiom | yes | Linux only; Homebrew `flock` is the discoteq C port (`discoteq-flock:README.md`) | `-E` sets the conflict exit code, `--fcntl` switches to OFD locks that do not interact with `flock` (`flock.1.adoc:65-90`); documents the same env re-entry trick as HL (`FLOCKER`, `:141-142`) |
| macOS `shlock` | no: PID file checked with `kill(pid, 0)` | no | no | no | macOS only | "deprecated, and lockf(1) should be used instead" (`macos-shlock.1.txt`) |
| Rust crates (`fslock`, `fs4`, `fd-lock`, `fmutex`, std `File::lock`) | yes | caller-built | caller-built | yes, all `flock` | yes | Libraries only. crates.io search found no maintained cross-platform `flock(1)`-style binary (`S/crates/c-*.json`) |
| `pueue` groups | daemon-managed | queue | n/a | needs `pueued` | yes | Needs a background daemon, which MP rules reserve for explicit instruction (`MP/AGENTS.md`, Gotchas) |
| GNU make jobserver (`--jobserver-auth=fifo:PATH`) | no: tokens lost on kill | no | via `MAKEFLAGS` | only under one server | yes | `O/docs/gnu-make/POSIX-Jobserver.md`, `Job-Slots.md` |
| ninja pools; ninja 1.13 client, 1.14 `--jobserver-pool` | per process tree | no | n/a | no | yes | Pools limit edges inside one ninja (`ninja:doc/manual.asciidoc:859-876`); jobserver scope is the server's children (`:190-245`) |
| system-wide jobserver (steve, guildmaster) | yes, via CUSE | live holders | n/a | yes | Linux only | `O/docs/jobserver/gentoo-one-jobserver.md`, "The token release problem" |

The job-slot designs answer a different question (how many compiler processes may run inside a build),
so they can complement the gate later (for example a ninja `-j` cap inside one heavy job) but cannot be
the host-wide one-at-a-time gate on macOS.

## 6. Local probes (macOS 27, measured 2026-10-14)

| Probe | Result |
|---|---|
| P1 fresh `flock` vs held `flock` | busy |
| P1 POSIX `fcntl.lockf` vs held `flock`; P1b `flock` vs held POSIX lock; P6 `F_OFD_SETLK` (cmd 90) vs held `flock` | busy, busy (errno 35), busy: all three families conflict on macOS, unlike Linux |
| P2 child re-locks the holder's inherited descriptor | acquired on the inherited open file description |
| P3 `/usr/bin/lockf -k -t 0` vs held `flock`; `flock(1)` | rc 75 (EX_TEMPFAIL); not installed |
| P4 holder killed with SIGKILL | busy before, free after |
| P5 holder passes the descriptor to `sleep 5`, holder SIGKILLed | still busy until the grandchild exits |
| P7 unlink and recreate the path while held | a second process acquires the new inode: two holders |
| P8 child calls `LOCK_UN` on the inherited descriptor | parent's lock is gone |
| `lsof <path>` with one holder and one plain opener | both listed as `3u`, no lock marker: macOS cannot name the holder from the kernel |

On Linux `lslocks` does print a PID, but calls "the process holding the lock" for `flock` "a fake-concept"
because the lock belongs to an open file description (`O/docs/man7/lslocks.8.md:205-213`). The holder
record in the file is therefore the portable way to name the holder. Linux behaviour was not measured
here (a container run needs its own admission); it rests on `O/docs/man7/flock.2.md:60-80,118-124`.

## 7. Recommendation details

### 7.1 Implementation now (Python scripts and mise tasks)

One stdlib module in MP (where the explainer and DF-B-1 put it: `dev/toolchains/host_lock.py` now, the
package `locks.py` after CT-39, `P/reviews/ccm-20261014/project-import/DF-B-dotfiles-python-tooling.md:172`),
keeping HL's names that the 27 callers use (`HEAVY_GATE`, `lock_path`, `LOCK_FD_ENV`, `held(name, label,
wait_s=, out=)`), with:

- Path: `lock_dir() = $MARKETPLACE_LOCK_DIR` (tests) else `${XDG_STATE_HOME:-~/.local/state}/claude-code-marketplace`;
  never `/tmp`, because a cleaner that deletes a held lock file splits holders (P7; portalocker warns the
  same, `utils.py:3043-3050`). Never unlink, rename or replace the file; open with `os.open(path,
  O_RDWR | O_CREAT)` (Python descriptors are non-inheritable by default, PEP 446, `O/docs/python/pep-0446.md:55`) and truncate only while holding.
- Order: new path, then legacy path, each with the remaining budget of one bounded wait; record written to
  both; both released together; both descriptors passed to the heavy child with `pass_fds`, so an orphaned
  child still excludes old dotfiles jobs. No participant may take the legacy path first.
- Re-entry: `MP_HEAVY_GATE_FD` (and, during migration, a second variable for the legacy descriptor). Sketch
  of the check (proposal, modelled on `host-build-lock.sh:36-41` and HL:101-119):

  ```python
  def inherited(fd_env: str, path: Path) -> int | None:
      raw = os.environ.get(fd_env)
      if raw is None or not raw.isdecimal():
          return None
      fd = int(raw)
      try:
          same = (os.fstat(fd).st_dev, os.fstat(fd).st_ino) == (path.stat().st_dev, path.stat().st_ino)
      except OSError:
          return None            # closed by an intermediary: fall back to a normal, bounded acquire
      if not same:
          return None            # number reused for another file: never trust it
      try:
          fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)   # succeeds only on the holder's description
      except BlockingIOError:
          return None
      return fd                  # never LOCK_UN this descriptor (P8); just let it close
  ```
- Waiting: poll `LOCK_NB` once a second (HL's loop, zero CPU in practice); name the holder from the record;
  if the recorded PID is dead while the lock is busy, say the lock is held through an inherited
  descriptor and suggest `lsof <path>` (P5, mise #13581's confusion). Timeout exits 124 from the CLI.
- Release: truncate the record, then unlock, as mise does (`lock_file.rs:42-48`).
- mise tasks and hk steps call the module's `run --label L --wait S -- cmd` (HL:266-297 shape) through
  `./dev/mise run`, not a bare `lockf`/`flock` wrapper: Claude Code cannot auto-approve exec wrappers such
  as `flock` with a prefix rule (`O/docs/claude-code/permissions-raw.md:249-252`).
- Containers: take the gate on the host around `docker build` or `docker run`; never share the lock file
  into a container. `flock` over Docker Desktop VirtioFS is unreliable (docker/for-mac#7004, open since
  2023-10-02, last comment 2026-07-13), and HL already scopes the lock to one filesystem (HL:30-32).
- Tests (as DF does with real processes): waiter names the holder, SIGKILL release, timeout without
  running, re-entry by inherited descriptor, refusal of a foreign or reused descriptor, dual-lock exclusion
  against an old-style holder of the legacy path only, and no deadlock between two MP holders. CT-11's
  check lock can reuse the primitive (DF-B-1, `DF-B-dotfiles-python-tooling.md:213`).

### 7.2 Shape for a later C++ caller

Default: no lock code in C++. The heavy C++ binary runs as the child of `run` (or a mise task using it)
and inherits the descriptor; if it must refuse to run ungated, it performs the same three checks as the
sketch above in about 20 lines of POSIX. If a C++ orchestrator must take the gate itself, use a small RAII
type over `open(O_RDWR | O_CREAT | O_CLOEXEC)` and `flock`, written to the standard named requirements so
the library algorithms accept it:

```cpp
class host_gate {              // models Cpp17TimedLockable; proposal, not found code
 public:
  explicit host_gate(std::filesystem::path p);   // open, never unlink
  void lock();                                   // flock(fd, LOCK_EX), EINTR retry
  bool try_lock();                               // flock(fd, LOCK_EX | LOCK_NB)
  template <class C, class D> bool try_lock_until(const std::chrono::time_point<C, D>&);  // LOCK_NB poll
  template <class R, class P> bool try_lock_for(const std::chrono::duration<R, P>&);
  void unlock();                                 // truncate record, then LOCK_UN
  int native_handle() const noexcept;            // for posix_spawn file actions
};
```

`std::unique_lock<host_gate> g(gate, 1h)` then gives the bounded wait; during the migration window
`beman::timed_lock_alg::try_lock_for(1h, gate_new, gate_legacy)` would take both without a fixed order
(its `TimedLockable` concept requires both `steady_clock` and `system_clock` overloads, `mutex.hpp:27-34`).
Avoid Boost.Interprocess `file_lock` and `named_mutex` and `F_OFD_SETLK` for the reasons in section 3.
Reflection may serialise the holder record; it is optional.

### 7.3 Lock path and migration so dotfiles and MP flip together

There is no atomic flip: DF has many checkouts and worktrees running old code (the record on this Mac
names a Codex worktree, `~/.codex/worktrees/five-stage-p11-review-corrections/dotfiles`, 2026-10-13), and
each takes only the legacy path. The legacy path is therefore the common denominator until the sunset,
and the new path is added on top:

1. CT-63a (MP): add the module and CLI; it takes the new path then the legacy path. Edit the 27 callers in
   one sweep: drop `LOCK_MODULE`/`LOCK_SHA` (`p2996_configure.py:19-20`) and the dotfiles import, change
   the path assertion (27 files assert the legacy path) and the holder-export assertion; re-review any
   heavy-run admission that binds those helper digests (DF-B-1). Safe alone: old DF holders and MP
   exclude each other through the legacy file.
2. The one DF write (D109): `host_lock.py` takes the same two paths in the same order and writes the same
   record; keep its legacy-only behaviour nowhere. Safe in either order relative to step 1.
3. knowledge-base (no gate today; `git grep heavy-gate` returns nothing there) needs nothing for exclusion
   to hold. If it adds one before its sunset, the zero-code form is
   `/usr/bin/lockf -k -t 3600 <new> /usr/bin/lockf -k -t 3600 <legacy> <cmd>` (outer new, inner legacy;
   `-k` mandatory), accepting that it records no holder.
4. After the DF sunset (CT-62) and once no DF worktree runs heavy jobs: MP drops the legacy acquisition,
   the second descriptor variable and the legacy record. The new path alone remains.
5. Optional later: the C++ type of 7.2, if a C++ orchestrator appears; the Python module stays the CLI.

## 8. Code examples found

| Repository | Path and lines | Commit or permalink | What it shows |
|---|---|---|---|
| bemanproject/timed_lock_alg | `include/beman/timed_lock_alg/mutex.hpp:15-117` | https://github.com/bemanproject/timed_lock_alg/blob/e52c94944b7698d5ee5522b7bd4db1435daf17ad/include/beman/timed_lock_alg/mutex.hpp | In-process timed multi-lock algorithm and concepts |
| jdx/mise | `crates/mise-util/src/lock_file.rs:11-185` | https://github.com/jdx/mise/blob/a1237811d2ab736edee77889fd7b632c769c85b8/crates/mise-util/src/lock_file.rs | fslock wrapper, holder PID record, truncate on unlock |
| jdx/mise | `src/daemons/mod.rs:237-298` | https://github.com/jdx/mise/blob/a1237811d2ab736edee77889fd7b632c769c85b8/src/daemons/mod.rs#L237-L298 | New plus legacy lock in fixed order (PR #13338) |
| brunoczim/fslock | `src/unix.rs:266,322` | https://github.com/brunoczim/fslock/blob/v0.2.1/src/unix.rs#L322 | `O_CLOEXEC` open, `flock(LOCK_EX)` |
| rust-lang/rust | `library/std/src/sys/fs/unix.rs:1300-1320` | https://github.com/rust-lang/rust/blob/d8ef4f3fe7031514cbd7d056b7b058814987ecec/library/std/src/sys/fs/unix.rs#L1300-L1320 | std `File::lock` is `flock` on Apple and Linux (tracking #130994, closed) |
| boostorg/interprocess | `include/boost/interprocess/detail/os_file_functions.hpp:651-739` | https://github.com/boostorg/interprocess/blob/7a45216bafa5a26c067585ff23f9583ef21dbf1a/include/boost/interprocess/detail/os_file_functions.hpp#L651-L739 | `fcntl` record locks; `flock` variant disabled |
| ned14/llfio | `include/llfio/v2.0/detail/impl/posix/lockable_byte_io_handle.ipp:55-77` | https://github.com/ned14/llfio/blob/1d1bb6b8e2f2da5c9af433882570167b944d7672/include/llfio/v2.0/detail/impl/posix/lockable_byte_io_handle.ipp#L55-L77 | Whole-file `flock` in C++ |
| tox-dev/filelock | `src/filelock/_unix.py:60-150` | https://github.com/tox-dev/filelock/blob/8aaa3730873d35af3e84854615017aba7aa7355b/src/filelock/_unix.py#L60-L150 | Never unlink; dead-inode check via `st_nlink` |
| wolph/portalocker | `portalocker/utils.py:3020-3060` | https://github.com/wolph/portalocker/blob/c490bea3973b9840a3c18610edac5d00700075dd/portalocker/utils.py#L3020-L3060 | N-slot semaphore from `flock` files |
| util-linux/util-linux | `sys-utils/flock.1.adoc:65-147` | https://github.com/util-linux/util-linux/blob/d427f58b7a22b960ccc8d02ce30c58bdbe4286d8/sys-utils/flock.1.adoc | `-w`, `-E`, `-o`, `--fcntl`, descriptor idiom |
| curlewlabs-com/local-mutex | `lib/local-mutex.sh:8-38,255-300` | https://github.com/curlewlabs-com/local-mutex/blob/1a3173b23ced845eccd699ccaf86fe1d83ad6cfa/lib/local-mutex.sh | `lockf` on macOS, `flock -o` on Linux, diagnostic holder sidecar |
| dc0sk/OpenPulseHF | `scripts/lib/host-build-lock.sh:28-57` (PR #1459) | https://github.com/dc0sk/OpenPulseHF/blob/b4145f9b8d9dc05fe5189dbdf821138a4adf5eb2/scripts/lib/host-build-lock.sh#L28-L57 | Cross-project host build lock, re-entry by inherited fd 9 |
| ninja-build/ninja | `doc/manual.asciidoc:190-245`; `misc/jobserver_pool.py` (added `6adbd5c`, 2025-04-22) | https://github.com/ninja-build/ninja/blob/1d8d3becbfa7ebedab908cdf025a6c8d09cc5ff6/doc/manual.asciidoc | Jobserver client and pool |
| ray-manaloto/dotfiles | `python/src/dotfiles_setup/host_lock.py:1-306` | local `c91d9d6` | The code being replaced |

## 9. Routes

Every provider call ran under `fnox --config ~/.config/fnox/config.toml --profile codex_research
--no-defaults --no-daemon --non-interactive exec --` (wrapper `S/bin/fx`); keys were read from the
environment inside the called script and never printed.

| Stage | Route | Command shape | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Exa | `fx exa.sh <out> "<query>" 10` (POST api.exa.ai/search) x6 | 0, HTTP 200 each | 10 each | Yes: P3832 revisions, docker/for-mac#7004, Gentoo jobserver post, local-mutex, P3771, Glaze P2996, interprocess#65 |
| 1 | Context7 | `fx ctx7 library "<name>"` x5 (boost interprocess, filelock, portalocker, mise, fs4) | 1 each | "Monthly quota reached" | No; gap |
| 1 | Firecrawl | `fx firecrawl search "<query>" --limit 5 --json` | 1 | HTTP 402 insufficient credits | No; gap |
| 1 | webclaw | `webclaw <url> -f markdown` x42 (one a repeat of Job-Slots) | 0 x39, 1 x3 | pages in `O/docs` | Yes; Stack Overflow x2 HTTP 403 and crates.io no readable content stay gaps |
| 1 | curl | `curl -sS -L https://code.claude.com/docs/en/permissions.md` | 0 | 1 page | Yes: webclaw copy lacked the exec-wrapper text |
| 1 | Serper | `fx serper.sh <out> "<query>"` x6 | 0, HTTP 200 each | 0, 3, 3, 8, 1, 8 | Yes: `F_OFD_SETLK` macOS dating; S1 confirmed 0 hits for timed_lock_alg cross-process |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3 -I last30days.py --plan plan.json --emit md --quick --save-dir "" --search reddit,hackernews,github,x "<topic>"` (after `--help`) | 0 | Reddit 6, HN 6 (all about the Flock camera company), X 0, GitHub 0 | No; gap |
| 1 | crates.io API | `curl https://crates.io/api/v1/crates?q=<q>` x4 | 0 each | 15 each | Yes: no maintained flock CLI crate |
| 1 | Clones | `git clone [--filter=blob:none] <url> O/repos/<name>` x17 (sparse for util-linux and rust) | 0 each | 17 repos | Yes, basis of the analysis |
| 1 | Local docs | `MANPAGER=cat man <sec> <page> \| col -bx` x6; SDK `sys/fcntl.h` copy | 0 | 7 files | Yes |
| 1 | Local probes | `/usr/bin/python3 -I S/probe-scripts/probe.py S/probe-run`; lockf, lsof, `/usr/bin/time` probes | 0 | P1 to P8 | Yes |
| 2 | gh issue/pr list | `gh issue list` and `gh pr list -R bemanproject/timed_lock_alg --state all` | 0, 0 | 12 issues, 46 PRs | Yes: no cross-process topic |
| 2 | gh search issues | timed_lock_alg x3; cplusplus/papers P3832, P3833, P1883; jdx/mise x6; tox-dev/filelock x4; ninja jobserver; rust file_lock | 0 each | listed in `S/gh/` | Yes: #2438, #2546, #633, #13588, #130994 |
| 2 | gh issue/pr view | cplusplus/papers#2438 `--comments`; jdx/mise PR #13588, #13338; docker/for-mac#7004; boostorg/interprocess#65; dc0sk/OpenPulseHF PR #1459 | 0 each | 6 | Yes |
| 2 | GraphQL DISCUSSION | `gh api graphql` search x10 (5 in jdx/mise, 5 global incl. `timed_lock_alg`), discussion read jdx/mise#10512 | 0 each | mise flock 4, lock tasks 3, timed_lock_alg 0 | Yes: #10512 |
| 2 | search/issues API | `gh api -X GET search/issues -f q=<q> -F per_page=5` x6 incl. control `repo:jdx/mise README` (458) | 0 each | 526, 458, 124, 41, 1, 3 | Yes: found OpenPulseHF#1459 |
| 2 | Saved searches (task) | `./dev/mise run research:collect` | not run | n/a | writes a tracked path another lane owns |
| 2 | Saved searches (reproduced) | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=1,2` plus control `README repo:<repo>` x6 | 0 each | see section 10 | Yes |
| 2 | Raw file fetch | `gh api -H 'Accept: application/vnd.github.raw' repos/dc0sk/OpenPulseHF/contents/<path>?ref=b4145f9` x2 | 0 | 2 files in `O/files/` | Yes |

## 10. Proposed saved-search rows

Reproduced read-only with `search/code`, two pages of five, each with its control (`S/gh/code/`). The
current file has three `openai/codex` rows (`MP/dev/saved-searches.toml:3-40`); these follow its schema.

```toml
[[search]]
id = "mise-lock-file"          # 37 hits; control README 93
query = "fslock"
repo = "jdx/mise"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "beman-timed-lock-alg"    # 8 hits; control 2
query = "try_lock_until"
repo = "bemanproject/timed_lock_alg"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "filelock-unix-flock"     # 15 hits; control 2
query = "fcntl.flock"
repo = "tox-dev/filelock"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "interprocess-file-lock"  # 1 hit (os_file_functions.hpp); control 1
query = "F_SETLKW"
repo = "boostorg/interprocess"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "util-linux-flock-ofd"    # 3 hits; control 18
query = "F_OFD_SETLK"
repo = "util-linux/util-linux"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

A sixth query, `fslock repo:jdx/hk`, returned only `CHANGELOG.md` (control 62): hk's current locks are
in-process (`hk:src/file_rw_locks.rs:1-18`) plus an `O_EXCL` install lock (`hk:src/cli/install.rs:620-665`),
so no row is proposed for it.

## 11. Open gaps

- Linux behaviour (no `flock`/`fcntl` interaction, `/proc/self/fd` re-entry) is cited from man7 and
  OpenPulseHF, not measured: a Linux container probe needs its own admission. CT-63a's CI tests will
  measure it.
- Context7 (monthly quota) and Firecrawl (HTTP 402) returned nothing; Last30Days returned only off-topic
  items; webclaw failed on two Stack Overflow pages (HTTP 403) and the crates.io page for `fmutex` (the
  docs.rs page and the clone were used instead).
- The macOS release that first shipped `F_OFD_SETLK` is UNVERIFIED (present in the 27 SDK and the
  xnu-12377.1.9 manual, absent from the 14.8.5 manual).
- local-mutex's claim that macOS `lockf` closes the lock descriptor before exec was confirmed only
  indirectly (the wrapped shell had no descriptor on the lock file, `S/probe-lockf-lsof.txt`).
- Whether any DF worktree other than the one in the current holder record still runs heavy jobs was not
  surveyed; step 4 of 7.3 needs that census before the legacy path is dropped.
- The final path string (`claude-code-marketplace` versus the marketplace identity `ray-manaloto`) is a
  naming choice for the user; the mechanism does not depend on it.
