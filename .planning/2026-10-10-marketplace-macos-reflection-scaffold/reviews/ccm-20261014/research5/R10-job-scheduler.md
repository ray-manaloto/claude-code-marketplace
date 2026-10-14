# R10: job scheduler for the adaptive crawl, GNU parallel against modern tools and a native C++ build (2026-10-14)

Written by research subagent R10 of session `ccm-20261014` (`ce9c0b3d`) under the shared brief
(`scratchpad/reprio2/research-brief.md`, two-stage route D100) and the offline mirror rule D110. MP at
`c33ba4e`, branch `codex/marketplace-native-onboarding`; no tracked MP file was edited (this report is the
only write outside `offline/`). Decisions served: D120 (the crawl sensor goes into the C++ library), D112
(one C++26 reflection library, no new Python or TypeScript logic), D107 (OS built-ins, then Rust, C++, C, Zig),
with D84 (heavy-run disk floor) and D86 (no page caps). Builds on R5 section A and its table 1.4 (pueue, niceload,
Crawlee, sysinfo are not repeated here).

Abbreviations. O = `MP/offline/research/R10-job-scheduler/` (untracked through `.git/info/exclude:17`;
`O/manifest.json` lists 123 items with URL, local path, UTC time, command, exit code and SHA-256 or commit).
GP = `O/repos/gnu-parallel` (savannah `1f05ef46`, the 20260822 code; the 20260922 tarball adds only "Bug fixes
and man page updates", `O/docs/gnu-parallel/ml-2026-09-release-20260922.md:42-43`). S = this agent's scratch
`scratchpad/research5/R10/`. P = `MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.
R5 = `P/reviews/ccm-20261014/research5/R5-out-of-box-tools.md`. Q2 = `P/reviews/ccm-20261014/reprioritize-3/Q2-order-v2.md`.
Host: macOS 27.0.1 (26A434), arm64, 12 cores, 96 GiB, `/usr/bin/perl` 5.34.1, mise 2026.10.10 (`O/local/host-probe.txt`).

## Verdict

Recommendation: a hybrid, in this order.

1. Now (wave 12): GNU parallel stays the scheduler, driven by the C++ sensor that D120 already places in the
   library. The sensor is a small `research-sense` command whose exit code follows GNU parallel's `--limit`
   contract (0 start, 1 hold, 2 shed the youngest job), so no glue logic is needed between them. GNU parallel
   gets a repository-local `PARALLEL_HOME`, `--termseq INT,60000,TERM,5000,KILL,25`, `--joblog` and
   `--resume-failed`, and `taskpolicy -c utility` on each job, as R5 described.
2. Later (after the native process transport of #27, wave 15, and the foundation gate #23, wave 14): port the
   scheduler into the C++ library on the same sensor, with GNU parallel's joblog as the behaviour oracle
   (the "retain behavior comparisons, replace one at a time" pattern of `MP/docs/accepted-decisions.md`), then
   retire GNU parallel. This is 4 to 6 units of about 300 lines, off the critical path.
3. Do not build on `std::execution` for this: neither standard library on this host ships it, and the reference
   implementation has no process or kqueue support. A single-thread event loop (the accepted libuv baseline)
   or plain POSIX is the right base for the port.

Confidence: medium-high that GNU parallel is the best external fit (every lever was read in source at the
release commit; nothing was run because it is not installed); medium on the timing of the port, which depends
on how the D114 re-scope (pending R9) reshapes CT-33.

Evidence that decides it:

- Only GNU parallel offers both an external admission hook and live concurrency. `--limit` runs a command
  before each start and in every scheduler loop (exit 2 kills the youngest job per `--termseq` and requeues it,
  GP/src/parallel:7905-7906, 7945-7969, 8781-8823; option since 20170922, GP/NEWS:2087-2089), and `-j procfile`
  is re-read when a job completes (GP/src/parallel.pod:1695-1700). rush 0.11.0, the strongest modern
  alternative, has fixed thresholds only (`--load`, `--memfree`) and no hook and no live `-j`
  (O/repos/rush/README.md:338-381; `process/start_gate.go:16-30`).
- Its stop and resume semantics fit webclaw's checkpoint: every job runs in its own process group
  (GP/src/parallel:12208-12209); Ctrl+C reaches GNU parallel only, whose INT handler calls `wait_and_exit(255)`,
  then `killall`, then the `--termseq` sequence on each job group (GP/src/parallel:6340-6343, 6515-6576), so
  webclaw gets SIGINT first and saves `--crawl-state` (R5 section 1.1). Killed jobs are logged with exit -1
  (GP/src/parallel.pod:4627) and `--resume-failed` reruns every row whose exit and signal are not both 0
  (GP/src/parallel:3802-3810). Ctrl+Z is forwarded to every job group and `fg` resumes them
  (GP/src/parallel:6287-6375), which is the in-session pause.
- No candidate in D107's preferred languages meets the contract (section 2): OS built-ins have no sensing,
  the Rust tools either lack sensing (pueue, rust-parallel) or are Linux-only (HyperQueue), the C tools are
  queues without sensing (nq, task-spooler) or a load-average gate only (moreutils parallel), and no Zig job
  scheduler exists. Read strictly, D107 plus D112 points to building in C++; the hybrid gets there without
  stalling CT-33.
- Building it now costs 5 to 8 units before CT-33's throttle row can run, needs a process and event-loop
  dependency that #27 is scheduled to admit at wave 15, and lands new process-control code (orphans, signal
  races, cleanup hangs) on the critical cxx column; rush needed a 2026 release to fix exactly such
  "hangs and high CPU usage while stopping child processes" (O/repos/rush/CHANGELOG.md:10-17, rush#76).

## 1. GNU parallel for this job: confirmed, with six caveats

| Need | GNU parallel 20260922 | Evidence |
|---|---|---|
| Live concurrency | `-j procfile`: re-read when a job completes; lowering lets running jobs finish | GP/src/parallel.pod:1690-1700; maintainer confirmation, `O/docs/gnu-parallel/ml-2021-01-dynamic-jobslots.md` (2021-01-22) |
| External admission hook | `--limit cmd`: 0 start, 1 none, 2 kill youngest and requeue; run in every loop | GP/src/parallel.pod:1804-1830; src/parallel:7905-7906, 7945-7969, 8781-8823 |
| Memory-aware start | `--memfree`: no start below size, kill youngest below half (as `--termseq`), requeue; since 20240522 these kills do not count as `--retries` | GP/src/parallel.pod:2010-2022; GP/NEWS:417 |
| Memory suspend | `--memsuspend`: below 2x size SIGSTOP all, SIGCONT the oldest few; below size one job runs (since 20210122) | GP/src/parallel.pod:2025-2045; src/parallel:7971-8022, 11157-11178; GP/NEWS:1184 |
| Load limit | `--load`: counts processes whose `ps` state starts with D, O or R now, not the load average | GP/src/parallel.pod:1935-1943; src/parallel:9116, 9129, 9165-9166 |
| Stop signals | Ctrl+C or SIGTERM: kill all job groups with `--termseq` (default `TERM,200,TERM,100,TERM,50,KILL,25`); SIGHUP: no new jobs, wait for running ones; Ctrl+Z and `fg` forwarded | GP/src/parallel.pod:3758-3771, 4350-4360; src/parallel:6287-6375, 6515-6576 |
| Resume | `--joblog` plus `--resume` (by sequence number) or `--resume-failed` (exit and signal not 0) | GP/src/parallel.pod:2776-2803; src/parallel:3802-3810 |
| Disk | Only exits when its own `$TMPDIR` is full (8 KiB probe write); no floor | GP/src/parallel:7493-7500 |
| macOS | Runs on the system Perl 5.34.1; darwin memory = `vm_stat` free plus inactive pages | GP/src/parallel:8761-8766; `O/local/host-probe.txt` |
| Licence | GPL-3.0-or-later; documentation GFDL-1.3 and CC-BY-SA-4.0 | GP/src/parallel.pod:4892-4896; conda-forge record `O/files/anaconda/parallel.json` |
| Maintenance | Monthly releases (195 entries in NEWS), latest 20260922 (2026-09-22), single maintainer | GP/NEWS; `O/docs/gnu-parallel/ml-2026-09-release-20260922.md`; `ml-2026-08-release-20260822.md` |

Caveats, each with the design answer:

1. The darwin memory reading is free plus inactive pages (GP/src/parallel:8761-8766), the same figure gopsutil
   uses (`O/files/gopsutil-v3.21.11/gopsutil-v3.21.11-mem_darwin_cgo.go:43-50`) and close to libuv's, which adds
   purgeable pages (`O/repos/libuv/src/unix/darwin.c:128-138`). None of them is macOS memory pressure. Apple's
   DTS answer is the dispatch memory-pressure source (Exa excerpt `S/exa/q11.json`, developer.apple.com forum
   thread 802656; the webclaw mirror got an anti-bot stub), and Chromium polls
   `sysctlbyname("kern.memorystatus_vm_pressure_level")` beside that source
   (`O/docs/apple/chromium-system_memory_pressure_evaluator_mac.md:44-45, 91`). So the C++ sensor, not
   `--memfree`, must carry the pressure rule; `--memfree` stays a coarse backstop.
2. `--memsuspend` uses SIGSTOP on the job group (GP/src/parallel:11157-11161). A stopped webclaw still holds
   every page it fetched (it writes them only at exit, R5 section 1.1), so suspension stops growth but returns
   nothing (inference, not measured); macOS's own last-resort suspension is likewise a hold that frees nothing
   until resumed (`O/docs/apple/posaceanu-2026-10-09-swap-exhaustion.md:12, 88, 97`). For the crawl, shed with
   SIGINT through `--limit` exit 2; do not use `--memsuspend`.
3. `--load` counts D, O and R states, but macOS `ps` marks uninterruptible waits with U, not D
   (`O/local/man-ps.txt:207-211`), so on this host it counts runnable processes only. Use the sensor's load rule.
4. `--limit` is called in every loop iteration, which sleeps at most about one second
   (GP/src/parallel:7939-7941). A sensor that keeps returning 2 would shed one job per second, and each shed
   webclaw writes its pages to disk on exit, lowering free disk further: a cascade. The sensor needs a shed
   cooldown longer than the SIGINT grace (state kept in a small file next to the joblog) and hysteresis
   between the hold and shed lines.
5. `--resume` and `--resume-failed` match by sequence number, so "the input, the command, and --joblog all
   have to remain unchanged" (GP/src/parallel.pod:2780-2800). The source list fed to it (CT-41's manifest)
   must be append-only in a stable order, or a resume runs the wrong source.
6. The citation notice prints only when stderr is a terminal and no `will-cite` file exists in a config dir
   (GP/src/parallel:6661-6690); the doc asks scripts not to hide it with `--will-cite` unless the user paid
   (GP/src/parallel.pod:706-728). Setting `PARALLEL_HOME` to an untracked repository directory
   (GP/src/parallel.pod:4366-4372) and running `--citation` once there silences it without touching
   `~/.parallel`. The notice is a request, not a licence term (HN 37211236, 2023-08-21,
   `O/docs/gnu-parallel/hn-37211236-citation.md:3, 58-61`), though distributors objected (nixpkgs#110584,
   2021-01-23, `O/docs/gnu-parallel/nixpkgs-110584-citation.md:7`; Debian Bug#915541, the removal of
   `--will-cite` reverted, `O/docs/gnu-parallel/debian-915541-will-cite-revert.md:1`). MP only invokes the
   program, so GPL terms do not reach MP's code.

Install route: no mise registry entry exists for `parallel` (`mise registry` lists `rush` and `coreutils`
only, `O/local/host-probe.txt`). Options: mise's conda backend with `conda:parallel@20260922` (noarch, pulls
conda's `perl`, `O/files/anaconda/parallel.json`), or Homebrew `parallel` 20260922, which conflicts with
`moreutils` (`brew info`, host probe). Both need an install admission (AGENTS.md); the conda route keeps it
project-local and lockable (UNVERIFIED that the conda script runs unmodified under mise). Linux CI: the
distribution package `parallel`.

## 2. Alternatives (extends R5 table 1.4; pueue, niceload, Crawlee and sysinfo rows stay there)

"Mise route" names the backend that would install the tool; nothing was installed.

| Tool | Live concurrency | Resource sensing | Pause and resume | Daemon | Install (mise route) | Licence | Maturity | Citation |
|---|---|---|---|---|---|---|---|---|
| GNU parallel 20260922 (Perl), reference | `-j procfile` on job completion | `--limit` hook; `--memfree`, `--memsuspend`, `--load` | Ctrl+Z forwarded; SIGHUP drain; `--termseq` shed; `--joblog --resume-failed` | no | `conda:parallel`; Homebrew | GPL-3.0+, citation notice | monthly releases, NEWS from 20100424 to 20260822 | section 1 |
| rush 0.11.0 (Go) | no (fixed `-j`) | `--load` (1-minute load average via `vm.loadavg`), `--memfree` (free plus inactive; below half, SIGINT the youngest and retry without using `--retries`), `--delay`; no hook, no disk | Ctrl+C: SIGINT to each group, SIGKILL after `--cleanup-time` (default 3 s), exit 130, second Ctrl+C kills; `--continue` skips succeeded commands; no Ctrl+Z forwarding (only `Setpgid`, no TSTP code) | no | mise registry `rush` = `aqua:shenwei356/rush`; conda-forge osx-arm64; Homebrew `rush-parallel` | MIT | 1,133 stars; resource flags released 2026-09-21 after the owner had declined them in 2025 (rush#65) | `O/repos/rush/README.md:338-381`; `CHANGELOG.md:1-17`; `process/start_gate.go:16-30, 162-200`; `process/process_others.go:20, 402-407`; `root_signal_unix.go:47-53`; `O/files/gopsutil-v3.21.11/` |
| macOS `xargs -P` (BSD, built in) | no | none | none; stops on exit 255 or a signal | no | built in | BSD | stable | `O/local/man-xargs.txt:86-89, 136-139` |
| GNU `xargs -P` (findutils 4.10) | SIGUSR1 adds, SIGUSR2 removes one slot; never kills a running command | none | none | no | Homebrew `findutils` as `gxargs` (absent here); no registry entry | GPL-3.0+ | old; SIGUSR handling reworked 2024 (bug #64442: POSIX requires them fatal unless handled) | `O/docs/findutils/man7-xargs.1.md:149-163`; `O/docs/findutils/bug-64442-sigusr.md:36-48` |
| moreutils `parallel` 0.70 (C) | no | `-l maxload`: no new start until the load average is below the limit | none | no | Homebrew `moreutils` (conflicts with `parallel`, `task-spooler`); no registry entry | GPL-2.0 | stable, minimal | `O/files/moreutils/parallel.c:274-308, 381-400`; `parallel.docbook:80-85` |
| task-spooler 1.0.4 / fork 2.0.0 (C) | `-S N` at runtime; lowering waits for jobs to end | none (fork: GPU memory threshold only) | `-k` sends SIGTERM to the job group; no pause | yes (server per socket) | Homebrew `task-spooler`; no registry entry | GPL-2.0 | fork's last push 2024-03-06 | `O/docs/task-spooler/tsp.1.md:137-138, 159`; `O/repos/task-spooler/README.md:80-94` |
| nq 1.0 (C) | no; one queue runs serially (parallel only through several queue dirs) | none | none; order kept with `flock(2)` on log files | no ("no long-running processes") | Homebrew `nq`; no registry entry | CC0-1.0 | 3,137 stars; last push 2025-10-26 | `O/repos/nq/README.md:1-30` |
| pueue 4.0.4 (Rust), additions to R5 | `pueue parallel N [-g group]` | none, by design ("Sophisticated task scheduling for optimal load balancing" is out of scope) | pause = SIGSTOP, resume = SIGCONT; `pause --wait` drains; `kill --signal` can send SIGINT | yes (`pueued`) | conda-forge, Homebrew, `cargo:`; no registry entry | MIT OR Apache-2.0 | "feature-complete" | `O/repos/pueue/README.md:205-216`; `pueue/src/process_helper/unix.rs:20-33`; `pueue/src/client/cli.rs:246-283, 499-509` |
| HyperQueue 0.26.2 (Rust) | worker resource pools | declared resources (CPUs, memory detected at worker start) as bookkeeping, not live pressure | job and task states | yes (server plus workers) | Linux tarballs only | MIT | "currently only officially supports Linux"; Linux-only by design (hyperqueue#553, 2023-02-08; #688) | `O/repos/hyperqueue/docs/faq.md:35-39`; `O/docs/hyperqueue/resources.md`; `O/files/github/issues/` |
| rust-parallel 1.24.0 (Rust) | no | none (legend E1, E4 only) | none | no | Homebrew `rust-parallel`, `cargo:` | MIT | 321 stars, release 2026-08-15 | GP/src/parallel_alternatives.pod:4287-4303 |
| `mise run --jobs` | no (fixed; `jobs` default 8) | none | none | no | installed (2026.10.10) | MIT | active | `O/docs/mise/running-tasks.md:186`; `O/repos/mise/settings.toml:1859-1862` |
| launchd (built in) | one job per plist | none; `ProcessType Background` throttles CPU and I/O; `LowPriorityIO`, `Nice`, resource limits | launchctl start and stop | yes (agent registration, which MP rules reserve for explicit instruction) | built in | OS | stable | `O/local/man-launchd.plist.txt:474-516` |
| taskpolicy (built in) | n/a (wraps one process) | none; `-c utility|background|maintenance` clamp, `-b`/`-B` on a running pid, `-m` MiB limit with `-P kill|throttle|suspend` on exhaustion | `-b`/`-B` | no | built in | OS | stable | `O/local/man-taskpolicy.txt:32-54` |
| stageload (Python, 2026-10) | lanes, one job at a time per lane | waits for `kern.memorystatus_level` at or above N percent; stops on swap growth or low free memory sampled twice | SIGTERM then SIGKILL; history JSONL | per-machine queue files | `pip`; fails D112 | MIT | 0 stars, created 2026-10-05 | `O/docs/apple/devto-2026-10-12-ulimit-macos.md:36-48, 97-104` |
| concur (Go), sp (Rust) | no | none (E1, E4) | none | no | not packaged | GPL-3.0 / none | small | GP/src/parallel_alternatives.pod:4724-4740, 5011-5030 |

Not pursued: HyperShell, Ray, Dask (Python task runtimes, `O/repos/hyperqueue/docs/other-tools.md`); Zig
search found task runners and terminal tools only (zr, runmux, szn; Exa `S/exa/q24.json`); go-adaptive-pool and
AdaptiveExecutor are libraries (`S/exa/q15.json`). A 2025-2026 scan (Exa q2, q15, q24, q27; Serper s1, s2;
Firecrawl developer f3, f5) found no new CLI that combines live concurrency, an external sensor hook and
crawl-safe shedding.

Runner-up: rush 0.11.0, if the user rejects GPL, the citation notice or Perl. It is MIT, one static binary,
already in the mise registry, and its stop path (SIGINT then SIGKILL after a configurable grace) fits webclaw.
The cost: no live `-j`, no hook for the disk floor or macOS pressure (the sensor would gate each job's start
inside the job command and a separate watcher would have to shed), no Ctrl+Z pause, and resource flags that
are three weeks old.

## 3. Building it in the C++ library

### 3.1 What C++26 and the toolchains offer

- `std::execution` (P2300R10) is in C++26 but in neither library on this host. libc++ lists P2300R10, P3149R11
  (`async_scope`) and P2079R10 (parallel scheduler) with no status (`O/files/llvm-project/Cxx26Papers.csv:77,
  144, 146`, LLVM `e65c4e3`, 2026-10-07); llvm/llvm-project#105440 is open and the first sub-issue
  (`set_value`, `set_error`, `set_stopped`) was filed 2026-10-05 (`O/files/github/issues/llvm-105440.json`).
  The P2996 fork's libc++ has `__cpp_lib_senders` commented out and an `<execution>` that only defines
  policies; GCC 16.2's libstdc++ defines no `__cpp_lib_senders` and its `<execution>` has no sender code
  (`O/local/stdlib-feature-probe.txt`); GCC 16's release notes list reflection papers but no
  `std::execution` (`O/docs/cpp/gcc-16-changes.md:106-112`).
- stdexec (NVIDIA, Apache-2.0) is the reference implementation: GCC 12+, Clang 16+, Xcode 16 (`O/repos/stdexec/README.md:74-80`),
  macOS CI (`.github/workflows/ci.cpu.yml:361-369`, added in PR #1261, merged 2024-03-10), a libdispatch
  scheduler (PR #1258, merged 2024-03-11). The vcpkg port at MP's pinned baseline is `2026-05-25` port-version 1
  (`O/local/vcpkg-ports/stdexec/vcpkg.json`), which carries the macOS libc++ include fix of vcpkg PR #53741
  (merged 2026-09-03). It has no process, `posix_spawn`, `waitpid` or kqueue code at all (grep of
  `O/repos/stdexec/include` at `5fc945f`: 0 files), so every OS event source would be ours to write; compile
  time is an open complaint (stdexec#1719, 2025-12-18) and `get_system_scheduler()` fails to link on macOS in
  one report (stdexec#1477, open since 2025-02-23). beman.execution covers Clang 19-22 and GCC 14-15
  (`O/repos/beman-execution/README.md:92-100`), not GCC 16.
- `std::jthread` and `std::stop_token` are available in both libraries (`__cpp_lib_jthread` 201911L,
  `O/local/stdlib-feature-probe.txt`), enough for a sensor thread with cooperative stop.
- OS primitives (all in the 27.0 SDK): `posix_spawn` with `POSIX_SPAWN_SETSID` and
  `POSIX_SPAWN_CLOEXEC_DEFAULT` (`O/local/sdk/sys_spawn.h:61-62`); `posix_spawnattr_set_qos_class_np` accepting
  `QOS_CLASS_UTILITY` or `QOS_CLASS_BACKGROUND`, the in-process equivalent of `taskpolicy -c`
  (`O/local/sdk/pthread_spawn.h:37-66`); kqueue `EVFILT_PROC` with `NOTE_EXIT`/`NOTE_EXITSTATUS`, `EVFILT_SIGNAL`,
  `EVFILT_TIMER` for one loop over children, signals and the sensor tick (`O/local/man-kqueue.txt:353-411`;
  a worked example in `O/docs/cpp/gaultier-wait-child-timeout.md:607-690`). Linux needs a second backend
  (`pidfd_open`, `signalfd`, epoll; same article, 487-600).
- libuv 1.52.1 (the vcpkg baseline's port; upstream v1.53.0, 2026-09-24) already wraps all of this on both
  systems: `uv_spawn` uses `posix_spawn` with `POSIX_SPAWN_SETSID` for detached children
  (`O/repos/libuv/src/unix/process.c:501-515, 710`), reaps through kqueue on macOS (`:67-71`), and offers
  `uv_signal_start`, `uv_timer_start`, `uv_fs_statfs`, `uv_loadavg` and `uv_get_available_memory`
  (`O/repos/libuv/include/uv.h:977, 1139, 1176-1180, 1680, 1728, 1736`; darwin readers `src/unix/darwin.c:128-147`).
  It is the accepted "investigated baseline" for the single-thread event loop (`MP/docs/accepted-decisions.md`,
  Native data and runtime design).
- Sensing on macOS, no library needed: `sysctlbyname("kern.memorystatus_vm_pressure_level")` (1, 2, 4 = normal,
  warn, critical; R5 section 1.2; host read 1), `kern.memorystatus_level` (percent free; host read 67, also the
  guard input of stageload), `vm.loadavg`, `host_statistics64(HOST_VM_INFO64)` (`O/local/sdk/mach_host_info.h:181-182`),
  `proc_pid_rusage` with `ri_phys_footprint` for webclaw's own footprint (`O/local/sdk/libproc.h:111`,
  `sys_resource.h:184-211`), `statfs` for the D84 floor, and `DISPATCH_SOURCE_TYPE_MEMORYPRESSURE` for push
  events (`O/local/sdk/dispatch_source.h:135-142, 234-256`; `O/docs/apple/xnu-memorystatus_notify.md:26-35`).
  All values read on this host are in `O/local/sysctl-reads.txt`. No C++ library for macOS pressure sensing was
  found; the process libraries at the pinned baseline (reproc 14.2.7, tiny-process-library 2.0.4, Boost.Process
  1.92.0, `O/local/vcpkg-ports/`) spawn and wait but sense nothing.

### 3.2 Where reflection fits

P2996 has nothing to say about spawning, signals or reaping (R6 reached the same conclusion for locks). It fits
the declarative edges: one `Thresholds` struct whose annotated members generate the command-line flags, the
environment names, TOML parsing, `--help` text and the JSONL receipt of each `Sample`, so the policy is declared
once. Both toolchains carry the needed features: the P2996 fork with `-fannotation-attributes` and
`-fexpansion-statements`, GCC 16 with P2996, P3394 annotations, P1306 expansion statements and P3491
`define_static_array` (`O/local/reflection-feature-probe.txt`; `O/docs/cpp/gcc-16-changes.md:106-112`). Two
porting risks: the fork spells the filtered query `annotations_of(info, info)` while GCC 16 uses
`annotations_of_with_type` (`O/local/reflection-feature-probe.txt`), so a one-line shim is needed; and a
production GCC 16 user reports that `template for` "allocates aggressively and trips `-fconstexpr-ops-limit`"
(`O/docs/cpp/imachine-2026-05-reflection-gcc16.md:104`), so keep the reflected structs small or iterate a
`define_static_array` with a plain loop. Config parsing by reflection is a known 2026 pattern
(`O/docs/cpp/cppnext-2026-06-reflection-config.md`; nickelpro/cargparse, Exa `S/exa/q16.json`).

Sketch of the sensor's surface (a proposal, not compiled):

```cpp
namespace com::rsm::sense {
struct flag { std::string_view name; std::string_view help; };
struct Thresholds {                                   // one declaration drives flags, TOML, help, receipts
  [[=flag{"disk-floor-gib", "D84: larger of 60 GiB and 1.5x the class peak"}]] std::uint64_t disk_floor_gib = 60;
  [[=flag{"hold-margin-gib", "hold band above the floor"}]]                    std::uint64_t hold_margin_gib = 10;
  [[=flag{"load-max", "1-minute load that holds new starts"}]]                 double load_max = 9.0;
  [[=flag{"shed-cooldown-s", "minimum seconds between two sheds"}]]           std::uint32_t shed_cooldown_s = 90;
};
struct Sample { std::uint64_t free_disk; std::uint32_t pressure; std::uint32_t free_pct; double load1; std::uint64_t crawl_footprint; };
enum class Verdict : int { start = 0, hold = 1, shed = 2 };   // GNU parallel --limit contract
[[nodiscard]] Sample sample(const std::filesystem::path& dir);  // statfs, sysctlbyname, getloadavg, proc_pid_rusage; Linux: statvfs, PSI, /proc
[[nodiscard]] Verdict decide(const Sample&, const Thresholds&, std::chrono::seconds since_last_shed) noexcept;
}  // namespace com::rsm::sense
```

### 3.3 Size of a minimal native scheduler plus sensor (estimates)

Reference sizes: GNU parallel 17,685 lines of Perl (GP/src/parallel); rush 4,143 lines of non-test Go, of which
the process package and start gate are 1,867; nq 425 lines of C (counts in S, from the clones). The crawl needs
far less: no replacement strings, no output grouping, no remote hosts.

| Piece | Handwritten lines (estimate) | Units at the five-file, 300-line limit (`docs/agents/codex-task-orchestration.md:204`) |
|---|---|---|
| Sensor: macOS and Linux readers, decision with hysteresis and cooldown, `research-sense` CLI with exit codes and procfile writer, reflected config | 250-350 plus 150 tests | 1-2 |
| Scheduler core on libuv: queue, spawn with QoS and own session, SIGINT shed with grace then SIGKILL, requeue | 350-500 plus 250 tests | 2 |
| Journal and resume (append-only JSONL keyed by source id, not sequence number) and signal policy (Ctrl+C, Ctrl+Z, SIGHUP drain) | 150-250 plus 200 tests | 1-2 |
| Without libuv: a second event backend (kqueue and pidfd/epoll) | plus 200-300 | plus 1 |

Total 5 to 7 units with libuv, 6 to 8 without, plus libuv's admission and qualification on both compilers under
the accepted dependency rules. Keying the journal by source id removes caveat 5 of section 1.

### 3.4 Cost and risk: tool now and port later, against C++ now

| | Hybrid: C++ sensor plus GNU parallel now, native scheduler later | C++ scheduler and sensor now | rush plus C++ sensor now |
|---|---|---|---|
| Units before CT-33's throttle row (wave 12) | 1-2 (sensor) plus one install admission | 5-8 | 1-2 plus a shed watcher |
| New dependency before wave 15 | GNU parallel binary only (invoked, not linked) | libuv or a second backend, ahead of #27's admission | rush binary |
| Behaviour risk | low: features 5-11 years old; sensor is pure reads | high: new signal and child-process code on the critical path | medium: three-week-old flags; no live `-j`, no hook |
| D107/D112 fit | sensor in C++ now; Perl tool temporary | full | sensor in C++; Go tool temporary |
| Critical-path effect (Q2 section 2) | none beyond one cxx filler unit | delays CT-33 by about four waves or pushes the cxx column | none beyond one cxx filler unit |
| Port later | 4-6 units, with GNU parallel's joblog as the parity oracle; sensor and exit contract unchanged | n/a | same as hybrid |

## 4. Recommendation and the wave order (Q2)

Recommendation: the hybrid of the verdict. Changes to Q2's table, all marked as proposals for the parent:

- Before wave 12, in the cxx column as a filler (wave 9 beside the small `18-offline` split unit, or wave 11
  after `#14`): a new unit, here called CT-33s, the C++ sensor and `research-sense` CLI (`src/`, `include/`,
  `CMakeLists.txt`, its test and a `mise/tasks/<unit>.toml` row under D7). It must integrate before CT-33's
  throttle row, otherwise the row slips (D120 rules out the R5 shell sensor). Add `CMakeLists.txt` to the cxx
  hot-path class if it is not there (Q2 section 5 does not list it).
- Wave 12, parent operations: the GNU parallel install admission (`conda:parallel@20260922` through mise, or
  Homebrew) with `PARALLEL_HOME` under `offline/`, beside the existing D86 webclaw admission; CT-33's spike adds
  the section 1 caveats (shed cooldown, stable source order) to R5's open items (SIGINT through `--termseq` into
  `sh -c taskpolicy webclaw`, `--limit` exit 2 with requeue, the "state file gone" exit code).
- After #23 (wave 14) and #27 (wave 15, which admits the process transport and could admit libuv with it): a
  native scheduler family, here called CT-33n.1 to CT-33n.4, placed in cxx filler slots such as wave 17 (where
  Q2 already fills with #99 while #30 waits) or later; acceptance includes parity with GNU parallel's joblog on a
  recorded run, then GNU parallel's removal. The D114 re-scope (pending R9) may move CT-33's fetch and store
  core into C++ as well; the scheduler port then belongs to that family.
- Order otherwise unchanged; the critical path (Q2 section 2) gains no unit.

## 5. Code examples found

- GNU parallel: `--limit` and memsuspend loop, signal handlers, killall and termseq, per-job process group:
  https://git.savannah.gnu.org/cgit/parallel.git/tree/src/parallel?id=1f05ef46e33efac62af6d7fa635cd65dfb05cc84
  lines 6287-6375, 6515-6576, 7890-8022, 8781-8823, 12191-12212.
- rush start gate (load and memory polling, shed the youngest):
  https://github.com/shenwei356/rush/blob/1d3de74cf1b2d3d9e833b1f0956474ae06b72855/process/start_gate.go#L16-L200;
  stop signals https://github.com/shenwei356/rush/blob/1d3de74cf1b2d3d9e833b1f0956474ae06b72855/process/process_others.go#L402-L407.
- gopsutil darwin available memory: https://github.com/shirou/gopsutil/blob/v3.21.11/mem/mem_darwin_cgo.go#L43-L50.
- libuv darwin memory and load readers: https://github.com/libuv/libuv/blob/1cfa32ff59c076ffb6ed735bbc8c18361558661f/src/unix/darwin.c#L128-L147;
  spawn with `POSIX_SPAWN_SETSID`: same commit, `src/unix/process.c#L501-L515`.
- pueue pause and resume signals: https://github.com/Nukesor/pueue/blob/0d10739a6431bd853195dc7730056fce79faeee1/pueue/src/process_helper/unix.rs#L20-L33.
- stdexec libdispatch scheduler: https://github.com/NVIDIA/stdexec/blob/5fc945fac81ae9b5b4ef190d20d0d74b705bee2a/include/exec/libdispatch_queue.hpp.
- Chromium macOS pressure evaluator (dispatch source plus sysctl):
  https://chromium.googlesource.com/chromium/src/+/e1c0d01fecb19602388a71798c63c15f69d13f55/components/memory_pressure/system_memory_pressure_evaluator_mac.cc
  (`O/docs/apple/chromium-system_memory_pressure_evaluator_mac.md:44-45, 91`).
- kqueue `EVFILT_PROC` wait with timeout: https://gaultier.github.io/blog/way_too_many_ways_to_wait_for_a_child_process_with_a_timeout.html
  (`O/docs/cpp/gaultier-wait-child-timeout.md:607-690`).
- moreutils `parallel` load gate: https://sources.debian.org/data/main/m/moreutils/0.70-1/parallel.c lines 274-308, 381-400.
- The sensor sketch in section 3.2 (proposal, not compiled).

## 6. Routes

`fx` = `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --` (`S/bin/fx`); keys reached curl through a config read from stdin (`curl -K -`), never
argv or output.

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Exa | `fx S/bin/exa.sh <out> "<query>" 10` x27 (POST api.exa.ai/search) | 0, HTTP 200 each | 10 each | Yes: GNU parallel list posts, rush, HyperQueue, pueue, nq, task-spooler, stdexec PRs, beman, libc++, xnu doc, Chromium, Apple forum, findutils bug, citation threads, cargparse, cppnext, i-machine, stageload, posaceanu (queries in `S/exa/queries.tsv`) |
| 1 | Context7 | `fx ctx7 library "<name>"` x5 (stdexec, pueue, hyperqueue, gnu parallel, rush) | 1 each | "Monthly quota reached" | No; gap |
| 1 | Firecrawl search | `fx firecrawl search "<q>" --limit 5 --json` x1 | 1 | HTTP 402 insufficient credits | No; gap |
| 1 | Firecrawl developer index | `fx firecrawl developer "<q>"` x6 | 0 each | 8 per query | Yes: vcpkg PR #53741 (stdexec on macOS); other hits off-topic. New working route while `search` returns 402 |
| 1 | webclaw (fallback and D110 mirror) | `webclaw -t 60 <url> -f markdown > <file>` x38 | 0 x31 (one anti-bot stub: Apple forum), 1 x7 (2 unix.stackexchange, findutils node URL 404, 2 libc++ status pages, Debian moreutils man page, first viric.name try) | 30 usable pages | Yes, all `O/docs/**` cites |
| 1 | Serper | `fx S/bin/serper.sh <out> "<q>"` x6 | 0, HTTP 200 each | 8-10 each | Yes: alternatives pages, libc++ release notes pointer, `kern.memorystatus_level` users (dev.to 2026-10-12) |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3.13 -I last30days.py --plan plan.json --emit md --quick --search reddit,hackernews,github,x --save-dir "" "<topic>"` | 0 | planner kept 1 of 2 subqueries, Reddit and HN only, 12 items all off-topic | No; gap |
| 2 | Repo metadata | `gh api repos/<r>`, `gh api repos/<r>/releases/latest`, `.../tags` for 13 repos plus libuv, stageload, macos-oom-guard | 0 (404 on releases for repos without releases) | 16 | Yes (maturity column) |
| 2 | gh search issues | `gh search issues "<q>" --repo <r> --limit 15` x13 (pueue x3, rush x3, hyperqueue, stdexec x3, mise, rust-parallel, vcpkg) | 0 each | 0-15 | Yes: rush#65, hyperqueue#553, #688, stdexec#1477, #1719, #2152, vcpkg#39956 |
| 2 | gh issue and PR view | `gh issue view <n> --repo <r> --comments --json ...` (llvm#105440, rush#65, hyperqueue#688, #553, stdexec#1477); `gh pr view` (stdexec#1258, #1261, vcpkg#53741) | 0 each | 8 | Yes; mirrored to `O/files/github/issues/` |
| 2 | GraphQL discussions | `gh api graphql` search type DISCUSSION x6 | 0 each | 5, 0, 6, 0, 0, 7 | No relevant hit |
| 2 | Raw files | `gh api -H 'Accept: application/vnd.github.raw' repos/<r>/contents/<path>?ref=<ref>` (gopsutil x4; llvm `Cxx26Papers.csv`; first try `Cxx2cPapers.csv` 404) | 0 x5, 1 x1 | 5 files | Yes |
| 2 | Clones (D110) | `git clone --depth 1 [--branch <tag>] <url>` with hooks off: pueue v4.0.4, rush v0.11.0, hyperqueue v0.26.2, rust-parallel v1.24.0, nq, task-spooler v2.0.0, stdexec main, beman execution, gnu-parallel (savannah), mise v2026.10.10, libuv v1.52.1; moreutils (dumb HTTP, no shallow) | 0 x11, 128 x1 | 11 repos | Yes, code reading only, nothing executed |
| 2 | Saved searches (task) | `./dev/mise run research:collect` | not run | n/a | Writes a tracked path another lane owns |
| 2 | Saved searches (reproduced) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5` x10 with controls; known-result control `schema repo:openai/codex` | 0 each | control 884; rush `memfree` 5 (control `README` 0, `package` 37); stdexec `libdispatch_queue` 3 (control 1); libuv `uv_get_available_memory` 18 (control 4); pueue `SIGSTOP` 4 (control 5) | Yes (section 7) |
| 2 | Other HTTP | `curl -s https://api.anaconda.org/package/conda-forge/<p>` x3; Debian sources x2; joeyh.name cgit x2 | 0; cgit returned HTTP 403 | 5 files | Yes (install routes, moreutils source) |
| local | Host facts | `command -v` x30, `--version`, `sysctl -n` x13, `man` x15, SDK and compiler header greps, `brew info --json=v2` x8, `mise registry`, `mise backends ls`, `mise run --help` | 0 | n/a | Yes (`O/local/`) |

## 7. Proposed saved-search rows (not added; `dev/saved-searches.toml` untouched)

Counts are `total_count` from this session. Finding: `README` is not a universal control; it returned 0 in
shenwei356/rush, so that row uses `package`.

```toml
[[search]]
id = "rush-resource-gate"          # 5 hits: resource_flags.go, README.md, CHANGELOG.md, process/start_gate.go, root.go
query = "memfree"
repo = "shenwei356/rush"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "package"                  # 37; "README" returned 0 here
expected_min = 1

[[search]]
id = "stdexec-libdispatch"         # 3 hits incl. include/exec/libdispatch_queue.hpp; control 1
query = "libdispatch_queue"
repo = "NVIDIA/stdexec"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "libuv-available-memory"      # 18 hits across platform readers; control 4
query = "uv_get_available_memory"
repo = "libuv/libuv"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "pueue-sigstop"               # 4 hits incl. pueue/src/process_helper/unix.rs; control 5
query = "SIGSTOP"
repo = "Nukesor/pueue"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

If the collector gains an issues kind: `memfree repo:shenwei356/rush is:issue` (1 hit, #65).

## 8. Open gaps

- Nothing was run end to end: GNU parallel and rush are not installed (an install needs an admission), so R5's
  composition gaps stand, plus the two new ones (shed cascade under repeated exit 2, sequence-number resume
  against a changing source list).
- Context7 (monthly quota), Firecrawl search (HTTP 402) and Last30Days (off-topic) gave no evidence; Exa,
  Serper, the Firecrawl developer index, webclaw and GitHub carried the research.
- Mirrors failed for unix.stackexchange 796486 and 594565, the findutils "Controlling Parallelism" node, the
  libc++ status pages (the LLVM CSV replaced them) and the Apple forum thread (anti-bot stub; the Exa excerpt in
  `S/exa/q11.json` is the only copy).
- The C++ sizes are estimates from reference code, not a prototype; the reflection sketch was not compiled
  (read-only probes only), and the annotation spelling difference comes from headers.
- Whether compiling a small library unit counts as a heavy run under D68 and D84, and so whether the sensor may
  run in a lane rather than the cxx column, is for the parent.
- `conda:parallel` through mise, the `cargo:`/`github:` routes for pueue and the GNU xargs route are UNVERIFIED.
- `--memsuspend` returning no memory on macOS is an inference from the code and OS semantics, not a measurement.
- stdexec and libuv were not built against the P2996 fork or GCC 16.
