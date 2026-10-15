# R14: one execution stack for the C++ library: why libuv, std::execution and the alternatives (2026-10-14)

Written by research agent R14 of session `ccm-20261014` (`ce9c0b3d`) for the user's question Q105 ("why libuv?"
and a request for libraries the whole C++ library can use, built on modern features such as `std::execution`),
under the shared brief (`scratchpad/reprio2/research-brief.md`, routes D100, mirror rule D110, query log D137).
MP at `c33ba4e`, branch `codex/marketplace-native-onboarding`. No tracked MP file was edited; this report and the
untracked mirror are the only writes. Nothing was installed or built: host probes were `ls`, `grep`, `man` and
`--version` only, so every "compiles" statement below rests on upstream CI and issues, and is marked as such.

Citation keys. O = `MP/offline/research/R14-execution-libraries/` (untracked through `.git/info/exclude:17`).
`O/manifest.json` lists every mirrored item (URL, local path, UTC time, command shape, exit code, SHA-256 for
files, commit for clones); `O/queries.jsonl` is the D137 query log (289 rows). `O/repos/<name>` are
`git clone --depth 1 --filter=blob:none` copies (27 repositories, commits in the manifest), `O/docs/**` are webclaw
markdown copies, `O/gh/**` are `gh --json` copies, `O/local/**` are this run's host probes. P =
`MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`; R8, R9, R10, R11, R13 are the sibling reports in
`P/reviews/ccm-20261014/research5/`; CT59 = `P/reviews/ccm-20261014/ct59/CT59-design.md`. AD =
`MP/docs/accepted-decisions.md`. Host: macOS 27.0.1 (26A434) arm64 (`O/local/host-probe.txt`). Anything without a
citation is labelled UNVERIFIED.

## Verdict

**Why libuv.** It was never chosen as an async model. AD:88 names it "the investigated baseline" for a
single-thread event loop, and R10 (section 3.1) shows why it looked right: on macOS it already wraps every OS
source the crawl needs, `posix_spawn` with `POSIX_SPAWN_SETSID`, child reaping through kqueue `EVFILT_PROC`
without a SIGCHLD handler, signals, timers, `statfs`, available memory and load
(`O/repos/libuv/src/unix/process.c:85-89, 486, 585-592, 1166`; `src/unix/kqueue.c:332-333`;
`include/uv.h:993, 1155, 1192, 1696, 1744, 1752, 1850`). It is a C callback library with no sender integration:
the only sender adapter found is `koloshmet/uvexec`, one star, last push 2024-07-18, pinned to a 2024 stdexec, and
without process support (`O/repos/uvexec/README.md:10-12`, `CMakeLists.txt:8`, `O/gh/repos/koloshmet_uvexec.json`).

**Recommendation.** Standardise the library's asynchronous code on the C++26 sender model and amend the libuv
baseline:

1. Vocabulary: `std::execution` through NVIDIA stdexec, reached only through one project header that aliases the
   namespace (stdexec already supports a configurable namespace, `O/repos/stdexec/include/stdexec/__detail/__config.hpp:244-250`),
   so the switch to the standard library is one line once `__cpp_lib_senders` exists in both lanes.
2. One event loop: a single-threaded Boost.Asio `io_context` (kqueue on macOS, `O/repos/asio/asio/include/asio/detail/config.hpp:985-997`),
   bridged to senders by stdexec's own maintained `asioexec` adapter, which its macOS CI builds against Boost.Asio
   (`O/repos/stdexec/.github/workflows/ci.cpu.yml:361-392`; `include/exec/asio/asio_config.hpp.in:21-50`).
   Timers, signals, pipes, sockets and TLS come from Asio; later HTTP clients from Asio-based code (Beast, or the
   glaze networking that D135 already sends to R15, which accepts Boost.Asio through `GLZ_USE_BOOST_ASIO`,
   `O/repos/glaze/include/glaze/ext/glaze_asio.hpp:22-44`).
3. Children: keep CT-59's OS built-in launch (`posix_spawn` with `POSIX_SPAWN_SETSID`, CT59:73-78; R13 section 7)
   and add only the reap step inside the Asio loop: `signal_set` on SIGCHLD plus `waitpid(WNOHANG)` on macOS and a
   pollable `pidfd` on Linux, the same two mechanisms Boost.Process v2 uses
   (`O/repos/boost-process/include/boost/process/v2/process_handle.hpp:14-21`; `detail/process_handle_signal.hpp:74-101`;
   `detail/config.hpp:164-169`). Boost.Process v2 stays the fallback; it can attach to a pid we spawned
   (`process.hpp:136-137`).
4. Not everything uses it. The `rsm-core` bridge (stdin JSON in, JSON out), the heavy-run gate (flock plus one
   child) and the sensor's reads are synchronous plain C++; they call `sync_wait` on a sender only when a request
   starts asynchronous work.
5. AD:88 should be amended (proposed text in section 10): keep "single-thread event loop by default", replace
   "the investigated baseline is libuv" with "senders (`std::execution` via stdexec) over a single-threaded Asio
   `io_context`; libuv is the fallback if the prototype fails".

**Confidence: medium.** High that `std::execution` is unavailable in every standard library on this host and that
no sender library on macOS ships process, signal or kqueue I/O support; medium that Asio plus a small reaper is
better than libuv plus a home-made sender adapter, because neither stack was compiled here and the clang-p2996
lane is untested by stdexec's CI.

Evidence that decides it:

1. No standard library ships `std::execution`. In the p2996 fork's libc++, Homebrew libc++ 23.1.3 and the Apple
   SDK libc++, `__cpp_lib_senders 202406L` is commented out (`O/local/stdlib-execution-macros.txt:12, 27, 42`);
   libstdc++ 16 defines `__cpp_lib_execution 201902L` (the C++17 parallel policies) but no `__cpp_lib_senders`,
   and its module export block for senders sits behind that undefined macro (`:52, 74-76`). Upstream libc++ lists
   P2300R10 and every follow-up paper with an empty status (`O/gh/files/llvm_Cxx26Papers.csv:77, 87, 141-147, 157, 207`),
   and its first implementation sub-issue was opened on 2026-10-05 (llvm/llvm-project#229127). GCC trunk's
   `<execution>` has had no functional change since 2024 and `version.def` has no senders entry
   (`O/gh/files/gcc-mirror_commits_execution.json`, `O/gh/files/gcc-trunk_version.def:650, 1396`). C++26 itself is
   done (Sutter, `O/docs/wg21/sutter-2026-03-cxx26-done.md:98-104`, who also warns that adoption needs "a few
   helper adapter libraries").
2. The standard defines no timers, I/O, processes or signals: the C++26 names are concepts, `run_loop`, `when_all`,
   `task`, `counting_scope`, `spawn`, `parallel_scheduler` and friends, and the page has no `schedule_after` or
   `when_any` (`O/docs/cpp/cppreference-execution.md:116, 254, 328, 474-486`; 0 hits for the timer names). stdexec
   adds an io_uring context (Linux), a Windows pool and a libdispatch CPU scheduler, and has no kqueue, process or
   signal code (`O/repos/stdexec/include/exec/linux/io_uring_context.hpp:19-22`; `include/exec/libdispatch_queue.hpp:19`;
   saved-search rows 269 and 270: 0 hits for `kqueue` and `posix_spawn` in NVIDIA/stdexec). So every sender stack
   sits on an OS event loop, and the loop is the real choice.
3. Of the loops with kqueue support, only Asio has a maintained sender bridge, and only Asio covers the later
   network needs (TLS, HTTP); libuv offers TCP only and its sender bridge would be ours to write and keep. libuv is
   the stronger process library, which is why the plan keeps CT-59's `posix_spawn` and adds only a reaper.
4. Admission is one vcpkg fetch at the pinned baseline e456309: `stdexec[asio]` 2026-05-25 port-version 1 pulls
   boost-asio 1.92.0 (Asio 1.38.2) and 14 Boost header ports (`O/local/vcpkg-ports.txt`,
   `O/local/vcpkg-dependency-closure.txt`, `O/gh/files/boost-asio-1.92.0_version.hpp:21`); all licences are
   permissive (Apache-2.0 with LLVM exception, BSL-1.0), which D136 requires.

## 1. Queries sent to each tool, plugin or service (stage 1)
Exact text as sent. `seq` is the row in `O/queries.jsonl`; every row before seq 279 was backfilled from the scratch files after D137 reached this run (`logged: backfilled`), rows 279 onward were logged live. webclaw rows are the D110 mirror fetches; their URL came from the stage-1 row named in `url from`.

**exa** (25 calls)

| seq | query | rc | HTTP |
|---|---|---|---|
| 54 | std::execution P2300 C++26 implementation status libc++ libstdc++ 2026 | 0 | 200 |
| 55 | libstdc++ std::execution senders implementation GCC 17 | 0 | 200 |
| 56 | libc++ std::execution senders receivers implementation progress | 0 | 200 |
| 57 | stdexec process spawn child process sender | 0 | 200 |
| 58 | stdexec kqueue macOS io context | 0 | 200 |
| 59 | asioexec stdexec asio completion token sender | 0 | 200 |
| 60 | Boost.Process v2 macOS async wait child process kqueue SIGCHLD | 0 | 200 |
| 61 | Boost.Cobalt coroutines asio process io 2026 | 0 | 200 |
| 62 | beman.net networking senders P2762 kqueue | 0 | 200 |
| 63 | beman.execution std::execution reference implementation status 2026 | 0 | 200 |
| 64 | senders receivers libuv integration scheduler | 0 | 200 |
| 65 | C++ senders receivers library async I/O 2026 new library | 0 | 200 |
| 66 | libunifex status maintenance 2026 io_uring | 0 | 200 |
| 67 | HPX std::execution P2300 senders implementation | 0 | 200 |
| 68 | libcoro jbaldwin io_scheduler kqueue macOS | 0 | 200 |
| 69 | stdexec compile time heavy template | 0 | 200 |
| 70 | Taskflow stdexec integration scheduler | 0 | 200 |
| 71 | oneTBB senders receivers std::execution | 0 | 200 |
| 72 | std::execution::task P3552 coroutine task C++26 | 0 | 200 |
| 73 | cppalliance corosio coroutine networking library | 0 | 200 |
| 74 | libuv vs asio comparison process signals timers C++ | 0 | 200 |
| 75 | stdexec GCC 16 build | 0 | 200 |
| 76 | P2300 std::execution networking io_uring kqueue epoll scheduler library | 0 | 200 |
| 77 | folly coro Task macOS kqueue io | 0 | 200 |
| 78 | std::execution criticism C++26 senders receivers adoption | 0 | 200 |

**context7** (5 calls)

| seq | query | rc | HTTP |
|---|---|---|---|
| 79 | ctx7 library "stdexec" "sender receiver process spawn" | 1 |  |
| 80 | ctx7 library "asio" "sender receiver process spawn" | 1 |  |
| 81 | ctx7 library "boost process" "sender receiver process spawn" | 1 |  |
| 82 | ctx7 library "libuv" "sender receiver process spawn" | 1 |  |
| 83 | ctx7 library "taskflow" "sender receiver process spawn" | 1 |  |

**firecrawl** (7 calls)

| seq | query | rc | HTTP |
|---|---|---|---|
| 84 | firecrawl search "std::execution libc++ implementation status 2026" --limit 5 --json | 1 | 402 |
| 85 | firecrawl developer "stdexec senders process spawning posix_spawn kqueue" | 0 |  |
| 86 | firecrawl developer "std::execution libc++ implementation pull request" | 0 |  |
| 87 | firecrawl developer "libstdc++ std::execution implementation patch" | 0 |  |
| 88 | firecrawl developer "senders receivers libuv scheduler adapter" | 0 |  |
| 89 | firecrawl developer "Boost.Process v2 async_wait macOS" | 0 |  |
| 90 | firecrawl developer "asioexec use_sender boost asio stdexec" | 0 |  |

**serper** (7 calls)

| seq | query | rc | HTTP |
|---|---|---|---|
| 91 | libstdc++ "std::execution" senders gcc-patches 2026 | 0 | 200 |
| 92 | C++26 final draft approved 2026 std::execution included | 0 | 200 |
| 93 | "std::execution" libc++ RFC discourse implementation plan | 0 | 200 |
| 94 | koloshmet uvexec libuv senders | 0 | 200 |
| 95 | "Boost.Process" v2 process_handle macOS kqueue EVFILT_PROC | 0 | 200 |
| 96 | cppreference C++26 library support std::execution compiler support table | 0 | 200 |
| 97 | "asioexec" stdexec boost asio | 0 | 200 |

**serpapi** (0 calls)

Not run: Serper answered every query, so the SerpApi fallback was never needed.

**last30days** (2 calls)

| seq | query | rc | HTTP |
|---|---|---|---|
| 98 | "C++ std::execution senders versus Asio and libuv in 2026" --plan plan.json --emit md --quick --search reddit,hackernews,github,x (wrapped in timeout) | 1 |  |
| 99 | "C++ std::execution senders versus Asio and libuv in 2026" --plan plan.json (3 subqueries: stdexec-production, asio-vs-libuv, corosio-capy) --emit md --quick --search reddit,hackernews,github,x | 0 |  |

**webclaw** (30 calls)

| seq | URL | rc | url from |
|---|---|---|---|
| 157 | https://herbsutter.com/2026/03/29/c26-is-done-trip-report-march-2026-iso-c-standards-meeting-london-croydon-uk/ | 0 | 92 |
| 158 | https://en.cppreference.com/cpp/compiler_support/26 | 0 | 96 |
| 159 | https://cppreference.com/cpp/execution | 0 | 54 |
| 160 | https://libcxx.llvm.org/Status/Cxx26.html | 0 | 54 |
| 161 | https://discourse.llvm.org/t/rfc-add-std-execution-c-26-to-the-utilities/86841 | 0 | 54 |
| 162 | https://gcc.gnu.org/onlinedocs/libstdc++/manual/status.html | 0 | task or prior report |
| 163 | https://gcc.gnu.org/gcc-16/changes.html | 0 | task or prior report |
| 164 | https://gcc.gnu.org/gcc-17/changes.html | 0 | task or prior report |
| 165 | https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4041r0 | 0 | 78 |
| 166 | https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4014r0 | 0 | 78 |
| 167 | https://isocpp.org/files/papers/P3826R5.html | 0 | 78 |
| 168 | https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4007r3 | 0 | 72 |
| 169 | https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4096r0 | 0 | 78 |
| 170 | https://mropert.github.io/2025/11/21/trying_out_stdexec/ | 0 | 69 |
| 171 | https://nvidia.github.io/stdexec/user/ | 0 | 57 |
| 172 | https://docs.libuv.org/en/v1.x/guide/processes.html | 0 | 74 |
| 173 | https://docs.libuv.org/en/v1.x/process.html | 0 | task or prior report |
| 174 | https://www.boost.org/doc/libs/latest/libs/process/doc/html/index.html | 0 | 60 |
| 175 | https://cppalliance.org/mark/2026/03/11/Corosio-Beta-Coroutine-Native-Networking.html | 0 | 73 |
| 176 | https://corosio.org/why_corosio.html | 0 | 73 |
| 177 | https://bemanproject.org/libraries/ | 0 | 62 |
| 178 | https://www.citadelsecurities.com/careers/career-perspectives/how-cpp26-rethinks-concurrency-and-execution/ | 1 | 92 |
| 179 | https://sdowney.org/posts/the-sender-sub-language/ | 0 | 78 |
| 180 | https://hollykbuck.github.io/exec/tutorials/39-third-party-integration/ | 0 | 70 |
| 181 | https://www.reddit.com/r/CppNow/comments/1wxhsjf/senders_for_existing_asynchronous_interfaces/ | 0 | 99 |
| 182 | https://en.wikipedia.org/wiki/C%2B%2B26 | 0 | 92 |
| 183 | https://gaultier.github.io/blog/way_too_many_ways_to_wait_for_a_child_process_with_a_timeout.html | 0 | task or prior report |
| 184 | https://ericniebler.com/2024/02/04/what-are-senders-good-for-anyway/ | 0 | 78 |
| 185 | https://www.boost.org/doc/libs/latest/libs/cobalt/doc/html/index.html | 0 | 61 |
| 186 | https://taskflow.github.io/taskflow/index.html | 0 | 70 |

## 2. Results from each (hits, top results, used)

Top results are the first three returned (all five are in the log). `used` means a result is cited in this report.

| seq | provider | hits | top results | used | note |
|---|---|---|---|---|---|
| 54 | exa | 10 | libc++ C++26 Status - libc++  documentation <https://libcxx.llvm.org/Status/Cxx26.html>; Fix Sender Algorithm Customization <https://www9.open-std.org/JTC1/SC22/WG21/docs/papers/2026/p3826r3.html>; Building with Clang-22 in C++26 doesn't work. · Issue #19... <https://github.com/NVIDIA/stdexec/issues/1924> | yes |  |
| 55 | exa | 10 | libstdc%2B%2B-v3/include/std/execution <https://github.com/gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/std/execution>; include/stdexec/__detail/__sender_concepts.hpp at 4e2cee2... <https://github.com/NVIDIA/stdexec/blob/4e2cee2e/include/stdexec/__detail/__sender_concepts.hpp>; include/stdexec/__detail/__basic_sender.hpp at 4e2cee2e ·... <https://github.com/NVIDIA/stdexec/blob/4e2cee2e/include/stdexec/__detail/__basic_sender.hpp> | yes |  |
| 56 | exa | 10 | P2300R10: `std::execution` - WG21 Links <https://wg21.link/P2300>; P2300R7: `std::execution` <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2300r7.html>; D2300R11: `std::execution` <https://cplusplus.github.io/sender-receiver/execution.html> | no |  |
| 57 | exa | 10 | include/stdexec/__detail/__spawn.hpp <https://github.com/NVIDIA/stdexec/blob/711da597/include/stdexec/__detail/__spawn.hpp>; include/stdexec/__detail/__spawn_future.hpp at 4e2cee2e ·... <https://github.com/NVIDIA/stdexec/blob/4e2cee2e/include/stdexec/__detail/__spawn_future.hpp>; User’s Guide - stdexec dev documentation <https://nvidia.github.io/stdexec/user/> | yes |  |
| 58 | exa | 10 | examples/io_uring.cpp <https://github.com/NVIDIA/stdexec/blob/main/examples/io_uring.cpp>; include/exec/linux/io_uring_context.hpp <https://github.com/NVIDIA/stdexec/blob/main/include/exec/linux/io_uring_context.hpp>; User’s Guide - stdexec dev documentation <https://nvidia.github.io/stdexec/user/> | yes |  |
| 59 | exa | 10 | include/exec/asio/use_sender.hpp at 4e2cee2e · NVIDIA/std... <https://github.com/NVIDIA/stdexec/blob/4e2cee2e/include/exec/asio/use_sender.hpp>; Adapt boost::asio to stdexec · Pull Request #1501 · NVIDI... <https://github.com/NVIDIA/stdexec/pull/1501>; include/asioexec/use_sender.hpp <https://github.com/NVIDIA/stdexec/blob/9d5836a634a21ecb06d17352905d04f99f635be6/include/asioexec/use_sender.hpp> | yes |  |
| 60 | exa | 10 | V2 overwrites SIGCHLD handler without calling previous on... <https://github.com/boostorg/process/issues/432>; Add child::async_wait · Issue #57 · boostorg/process <https://github.com/boostorg/process/issues/57>; async on_exit and attached process · Issue #183 · klemens... <https://github.com/klemens-morgenstern/boost-process/issues/183> | yes |  |
| 61 | exa | 10 | Documentation boost.cobalt <https://www.boost.org/doc/libs/latest/libs/cobalt/doc/html/index.html>; Documentation boost.cobalt <https://www.boost.org/libs/cobalt>; boostorg/cobalt <https://github.com/boostorg/cobalt> | yes |  |
| 62 | exa | 10 | bemanproject/net <https://github.com/bemanproject/net>; Sender/Receiver Interface For Networking <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2762r2.pdf>; bemanproject/net <https://github.com/bemanproject/net29> | yes |  |
| 63 | exa | 10 | bemanproject/execution <https://github.com/bemanproject/execution>; bemanproject/execution <https://github.com/bemanproject/execution26>; beman::execution: Asynchronous Operation Support <https://bemanproject.github.io/execution/> | yes |  |
| 64 | exa | 10 | koloshmet/uvexec <https://github.com/koloshmet/uvexec>; NVIDIA/stdexec: `std::execution`, the standard C++ ... <https://github.com/NVIDIA/stdexec>; maikel/senders-io <https://github.com/maikel/senders-io> | yes |  |
| 65 | exa | 10 | Cra3z/coio <https://github.com/Cra3z/coio>; intel/cpp-baremetal-senders-and-receivers: An ... <https://github.com/intel/cpp-baremetal-senders-and-receivers>; KMX-Systems/kmx-aio <https://github.com/KMX-Systems/kmx-aio> | yes |  |
| 66 | exa | 10 | facebookexperimental/libunifex <https://github.com/facebookexperimental/libunifex/>; README.md <https://github.com/facebookexperimental/libunifex/blob/main/README.md>; dc1cd41 C++23 CI runner and corrected byteswap in io_urin... <https://github.com/facebookexperimental/libunifex/commit/dc1cd4157ba39cd87753b403b10e88d03b1d8850> | yes |  |
| 67 | exa | 10 | 7381b26 refactor(execution): migrate future/sender bridge... <https://github.com/TheHPXProject/hpx/commit/7381b261fc08f0468f41ed378bc4ed8e6af28a2f>; execution: Add scheduler-aware overload to as_sender() fo... <https://github.com/TheHPXProject/hpx/pull/7272>; Implementing sender, receiver, and operation_state concep... <https://github.com/TheHPXProject/hpx/pull/4665> | yes |  |
| 68 | exa | 10 | c195a67 Ref/394 kqueue socket shutdown (#422) <https://github.com/jbaldwin/libcoro/commit/c195a67031497aa0fb1c38e88329f88a98588b7c>; 77e57e9 High CPU Usage in io_scheduler with process tasks... <https://github.com/jbaldwin/libcoro/commit/77e57e9d4141ff4dd51e28d11d5ddbf05a040aeb>; jbaldwin/libcoro <https://github.com/jbaldwin/libcoro/> | yes |  |
| 69 | exa | 10 | Trying out C++26 executors <https://mropert.github.io/2025/11/21/trying_out_stdexec/>; c++ - How do you handle increasingly long compile times ... <https://softwareengineering.stackexchange.com/questions/177546/how-do-you-handle-increasingly-long-compile-times-when-working-with-templates>; How to reduce compile time with C++ templates <https://stackoverflow.com/questions/2827422/how-to-reduce-compile-time-with-c-templates> | yes |  |
| 70 | exa | 10 | 39 · Third-party Framework Integration - std::execution T... <https://hollykbuck.github.io/exec/tutorials/39-third-party-integration/>; include/exec/taskflow/taskflow_thread_pool.hpp at 4e2cee2... <https://github.com/NVIDIA/stdexec/blob/4e2cee2e/include/exec/taskflow/taskflow_thread_pool.hpp>; Third-Party Scheduler Integrations \| NVIDIA/stdexec \| D... <https://deepwiki.com/NVIDIA/stdexec/5.4-third-party-scheduler-integrations> | yes |  |
| 71 | exa | 10 | P2300R10: `std::execution` <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2300r10.html>; Execution control library (since C++26) - cppreference.com <https://www.cppreference.com/cpp/execution>; doc/main/tbb_userguide/Nodes.rst <https://github.com/uxlfoundation/oneTBB/blob/master/doc/main/tbb_userguide/Nodes.rst> | no |  |
| 72 | exa | 10 | Add a Coroutine Task Type <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p3552r2.pdf>; vendor/task/docs/P3552-task.md <https://github.com/steve-downey/compile-time-scheme/blob/main/vendor/task/docs/P3552-task.md>; P3552 R3 Add a Coroutine Task Type <https://github.com/cplusplus/papers/issues/2200> | yes |  |
| 73 | exa | 10 | cppalliance/corosio <https://github.com/cppalliance/corosio>; Boost.Corosio :: Boost.Corosio <https://develop.corosio.cpp.al/corosio/index.html>; Corosio: Coroutine I/O for C++20 <https://corosio.org/why_corosio.html> | yes |  |
| 74 | exa | 10 | How does libuv compare to Boost/ASIO? <https://stackoverflow.com/questions/11423426/how-does-libuv-compare-to-boost-asio>; Basics of libuv <https://docs.libuv.org/en/v1.x/guide/basics.html>; Using C++ Resumable Functions with Libuv - C++ Team Blog <https://devblogs.microsoft.com/cppblog/using-ibuv-with-c-resumable-functions/> | yes |  |
| 75 | exa | 10 | gcc 16 build error <https://github.com/NVIDIA/stdexec/issues/1747>; Internal compiler error on GCC with modules <https://github.com/NVIDIA/stdexec/issues/2148>; 5f7e99b Fix build errors <https://github.com/NVIDIA/stdexec/commit/5f7e99b0fef7dcdcdb00e8d25984d3b10e3612c0> | yes |  |
| 76 | exa | 10 | P2300R10: `std::execution` <https://open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2300r10.html>; P2300R10: `std::execution` - WG21 Links <https://wg21.link/P2300>; Sender/Receiver Interface For Networking <https://open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2762r0.pdf> | yes |  |
| 77 | exa | 10 | folly/coro/Task.h <https://github.com/facebook/folly/blob/main/folly/coro/Task.h>; Search code, repositories, users, issues, pull requests... <https://github.com/facebook/folly/blob/main/folly/experimental/coro/README.md>; COROIO - Async I/O & Actors for Modern C++ \| Coroio Project <https://coroio.dev/> | yes |  |
| 78 | exa | 10 | The Sender Sub-Language \| What Comes to Mind <https://sdowney.org/posts/the-sender-sub-language/>; P4014R0: The Sender Sub-Language <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4014r0>; Is `std::execution` a Universal Async Model? <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p4041r0> | yes |  |
| 79 | context7 | 0 |  | no | Monthly quota reached (gap) |
| 80 | context7 | 0 |  | no | Monthly quota reached (gap) |
| 81 | context7 | 0 |  | no | Monthly quota reached (gap) |
| 82 | context7 | 0 |  | no | Monthly quota reached (gap) |
| 83 | context7 | 0 |  | no | Monthly quota reached (gap) |
| 84 | firecrawl | 0 |  | no | Insufficient credits (gap); fell back to firecrawl developer, webclaw and Serper |
| 85 | firecrawl | 10 | (pull_request) Implements the macOS-specific managed and ... <https://github.com/dotnet/runtime/pull/124923>; (doc) `os` - Miscellaneous operating system interfaces [¶... <https://docs.python.org/3/library/os.html>; (pull_request) libuv/libuv#3064 <https://github.com/libuv/libuv/pull/3064> | yes |  |
| 86 | firecrawl | 10 | (issue) [libcxx] `error: no member named 'par_unseq' in n... <https://github.com/llvm/llvm-project/issues/65125>; (readme) nvidia/stdexec <https://github.com/nvidia/stdexec>; P2300R10: `std::execution` - WG21 Links <https://wg21.link/P2300> | yes |  |
| 87 | firecrawl | 10 | (pull_request) llvm/llvm-project#139560 <https://github.com/llvm/llvm-project/pull/139560>; LibstdcxxTodo - GCC Wiki <https://gcc.gnu.org/wiki/LibstdcxxTodo>; (pull_request) llvm/llvm-project#146909 <https://github.com/llvm/llvm-project/pull/146909> | no |  |
| 88 | firecrawl | 10 | (readme) libuv/libuv <https://github.com/libuv/libuv>; Execution control library (since C++26) <https://cppreference.com/cpp/execution>; P2300R2: `std::execution` - WG21 Links <https://wg21.link/p2300r2> | no |  |
| 89 | firecrawl | 10 | (readme) klemens-morgenstern/boost-process <https://github.com/klemens-morgenstern/boost-process>; Boost::process async_wait process - c++ - Stack Overflow <https://stackoverflow.com/questions/3827734/boostprocess-async-wait-process>; boost.process <https://www.boost.org/libs/process> | yes |  |
| 90 | firecrawl | 10 | (doc) Completion token <https://github.com/tradias/asio-grpc/blob/57069c53f9c5877153da29a94c28f2138a77dbf1/doc/completion_token.md>; when_all hangs in finally when triggered by stop #1849 - ... <https://github.com/NVIDIA/stdexec/issues/1849>; asio completion_token error with async_read and streambuf... <https://github.com/NVIDIA/stdexec/issues/1684> | yes |  |
| 91 | serper | 1 | CppCast - Listen to All Episodes Online <https://liveradious.com/podcast/82059-cppcast.html> | no |  |
| 92 | serper | 10 | C++26 is done! - Trip report: March 2026 ISO C++ standard... <https://herbsutter.com/2026/03/29/c26-is-done-trip-report-march-2026-iso-c-standards-meeting-london-croydon-uk/>; C++26: Reflection, Memory Safety, Contracts, and a New ... <https://www.reddit.com/r/programming/comments/1spuizj/c26_reflection_memory_safety_contracts_and_a_new/>; C++26 <https://en.wikipedia.org/wiki/C%2B%2B26> | yes |  |
| 93 | serper | 0 |  | no |  |
| 94 | serper | 10 | libuv \| Cross-platform asynchronous I/O <https://libuv.org/>; libuv - Cross-platform asynchronous I/O <https://github.com/libuv/libuv>; libuv documentation <https://docs.libuv.org/> | no |  |
| 95 | serper | 10 | Process V2 <https://www.boost.org/doc/libs/1_80_0/doc/html/boost_process/v2.html>; In a multi-threaded fork process, child processes may be ... <https://github.com/boostorg/process/issues/430>; boost::process::v2 subprocess does not get a signal when ... <https://stackoverflow.com/questions/79391553/boostprocessv2-subprocess-does-not-get-a-signal-when-calling-request-exit> | yes |  |
| 96 | serper | 10 | Compiler support for C++26 <https://en.cppreference.com/cpp/compiler_support/26>; cppreference.com <https://cppreference.com/>; C++ compiler support <https://en.cppreference.com/cpp/compiler_support> | yes |  |
| 97 | serper | 8 | asio completion_token error with async_read and streambuf <https://github.com/NVIDIA/stdexec/issues/1684>; NVIDIA/stdexec: `std::execution`, the standard C++ ... <https://github.com/NVIDIA/stdexec>; asio integration not playing nicely with Beast (timeout) ... <https://github.com/NVIDIA/stdexec/issues/1727> | yes |  |
| 98 | last30days | 0 |  | no | not reached: mise shim 'timeout' had no version set; rerun without the wrapper |
| 99 | last30days | 1 | Senders For Existing Asynchronous Interfaces - Dietmar Ku... <https://www.reddit.com/r/CppNow/comments/1wxhsjf/senders_for_existing_asynchronous_interfaces/> | yes | planner kept 1 of 3 subqueries for entity 1 and fell back to a deterministic plan (LLM planner HTTP 503) for entity 2; resolve calls HTTP... |

webclaw: 29 of 30 fetches returned rc 0; seq 178 mirror docs/blogs/citadel-2026-05-cpp26-execution.md (0 bytes); failed, empty file; seq 181 mirror docs/l30/reddit-cppnow-kuhl-senders-existing-interfaces.md (244 bytes); login-wa....

## 3. GitHub issues, PRs and discussions searched (stage 2)

`seeded by` gives the stage-1 row whose result named the item. `basis` says whether that link was recorded when the search was chosen (live, rows 279 onward) or reconstructed afterwards from the stage-1 result files (backfilled); items seeded by a prior report, the task question, a local finding or another stage-2 row say so.

| seq | kind | query or item | rc | hits | seeded by | basis or other seed |
|---|---|---|---|---|---|---|
| 131 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1747 | 0 | 1 | 75 (exa: stdexec GCC 16 build) | reconstructed |
| 132 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1924 | 0 | 1 | 54 (exa: std::execution P2300 C++26 implementation statu...) | reconstructed |
| 133 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/2148 | 0 | 1 | 75 (exa: stdexec GCC 16 build) | reconstructed |
| 134 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1719 | 0 | 1 | none | seeded by prior report R10 (stdexec#1719), not by a stage-1 row |
| 135 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1477 | 0 | 1 | none | seeded by prior report R10 (stdexec#1477), not by a stage-1 row |
| 136 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1727 | 0 | 1 | 97 (serper: "asioexec" stdexec boost asio) | reconstructed |
| 137 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1684 | 0 | 1 | 59 (exa: asioexec stdexec asio completion token sender) | reconstructed |
| 138 | gh-issue-view | https://github.com/NVIDIA/stdexec/issues/1849 | 0 | 1 | 90 (firecrawl: firecrawl developer "asioexec use_sender boost ...) | reconstructed |
| 139 | gh-pr-view | https://github.com/NVIDIA/stdexec/pull/1501 | 0 | 1 | 59 (exa: asioexec stdexec asio completion token sender) | reconstructed |
| 140 | gh-pr-view | https://github.com/NVIDIA/stdexec/pull/1503 | 0 | 1 | 97 (serper: "asioexec" stdexec boost asio) | reconstructed |
| 141 | gh-pr-view | https://github.com/NVIDIA/stdexec/pull/1875 | 0 | 1 | 97 (serper: "asioexec" stdexec boost asio) | reconstructed |
| 142 | gh-pr-view | https://github.com/NVIDIA/stdexec/pull/1258 | 0 | 1 | 58 (exa: stdexec kqueue macOS io context) | reconstructed |
| 143 | gh-pr-view | https://github.com/NVIDIA/stdexec/pull/1261 | 0 | 1 | none | seeded by prior report R10 (PR #1261), not by a stage-1 row |
| 144 | gh-issue-search | gh search issues "reflection" --repo NVIDIA/stdexec --limit 20 | 0 | 1 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 145 | gh-issue-search | gh search issues "p2996" --repo NVIDIA/stdexec --limit 20 | 0 | 0 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 146 | gh-issue-search | gh search issues "kqueue" --repo NVIDIA/stdexec --limit 20 | 0 | 0 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 147 | gh-issue-search | gh search issues "process spawn" --repo NVIDIA/stdexec --limit 20 | 0 | 0 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 148 | gh-issue-search | gh search issues "subprocess" --repo NVIDIA/stdexec --limit 20 | 0 | 2 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 149 | gh-issue-search | gh search issues "macOS" --repo NVIDIA/stdexec --limit 20 | 0 | 8 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 150 | gh-issue-search | gh search issues "libuv" --repo NVIDIA/stdexec --limit 20 | 0 | 0 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 151 | gh-issue-search | gh search issues "freflection" --repo NVIDIA/stdexec --limit 20 | 0 | 1 | none | seeded by the task question (reflection, kqueue, process, libuv, macOS terms), not by a stage-1 row |
| 152 | gh-issue-view | https://github.com/llvm/llvm-project/issues/105440 | 0 | 1 | none | seeded by prior report R10 (llvm#105440), not by a stage-1 row |
| 153 | gh-issue-search | gh search issues "std::execution" --repo llvm/llvm-project --label libc++ --limit 30 | 0 | 30 | 86 (firecrawl: firecrawl developer "std::execution libc++ impl...) | reconstructed |
| 154 | gh-pr-search | gh search prs "[libc++] execution sender" --repo llvm/llvm-project --limit 30 | 0 | 0 | 86 (firecrawl: firecrawl developer "std::execution libc++ impl...) | reconstructed |
| 155 | gh-issue-view | https://github.com/llvm/llvm-project/issues/229127 | 0 | 1 | none | chosen from stage-2 row 152 (reconstructed) |
| 192 | gh-issue-view | https://github.com/taskflow/taskflow/issues/782 | 0 | 1 | 70 (exa: Taskflow stdexec integration scheduler) | reconstructed |
| 193 | gh-issue-view | https://github.com/boostorg/process/issues/432 | 0 | 1 | 60 (exa: Boost.Process v2 macOS async wait child process...) | reconstructed |
| 194 | gh-issue-view | https://github.com/boostorg/process/issues/528 | 0 | 1 | 89 (firecrawl: firecrawl developer "Boost.Process v2 async_wai...) | reconstructed |
| 195 | gh-issue-view | https://github.com/boostorg/process/issues/531 | 0 | 1 | 60 (exa: Boost.Process v2 macOS async wait child process...) | reconstructed |
| 196 | gh-issue-view | https://github.com/boostorg/process/issues/430 | 0 | 1 | 95 (serper: "Boost.Process" v2 process_handle macOS kqueue ...) | reconstructed |
| 197 | gh-issue-search | gh search issues "gcc 16" --repo bemanproject/execution --limit 15 | 0 | 0 | 63 (exa: beman.execution std::execution reference implem...) | reconstructed |
| 198 | gh-issue-search | gh search issues "macos" --repo bemanproject/execution --limit 15 | 0 | 1 | 63 (exa: beman.execution std::execution reference implem...) | reconstructed |
| 199 | gh-issue-search | gh search issues "kqueue" --repo bemanproject/net --limit 15 | 0 | 2 | 62 (exa: beman.net networking senders P2762 kqueue) | reconstructed |
| 200 | gh-issue-search | gh search issues "sender" --repo chriskohlhoff/asio --limit 15 | 0 | 15 | none | seeded by the local Asio history.qbk finding (senders deprecated in 1.25.0) |
| 201 | gh-issue-search | gh search issues "std::execution" --repo chriskohlhoff/asio --limit 15 | 0 | 15 | none | seeded by the task question |
| 202 | gh-issue-search | gh search issues "posix_spawn" --repo libuv/libuv --limit 15 | 0 | 12 | 85 (firecrawl: firecrawl developer "stdexec senders process sp...) | reconstructed |
| 203 | gh-issue-search | gh search issues "kqueue process" --repo libuv/libuv --limit 15 | 0 | 0 | 85 (firecrawl: firecrawl developer "stdexec senders process sp...) | reconstructed |
| 204 | gh-issue-search | gh search issues "process" --repo cppalliance/corosio --limit 15 | 0 | 15 | 73 (exa: cppalliance corosio coroutine networking library) | reconstructed |
| 205 | gh-issue-search | gh search issues "sender" --repo cppalliance/corosio --limit 15 | 0 | 0 | 73 (exa: cppalliance corosio coroutine networking library) | reconstructed |
| 206 | gh-issue-search | gh search issues "process" --repo boostorg/cobalt --limit 15 | 0 | 13 | 61 (exa: Boost.Cobalt coroutines asio process io 2026) | reconstructed |
| 207 | gh-issue-search | gh search issues "sender" --repo uxlfoundation/oneTBB --limit 15 | 0 | 1 | 71 (exa: oneTBB senders receivers std::execution) | reconstructed |
| 208 | gh-issue-view | https://github.com/chriskohlhoff/asio/issues/1485 | 0 | 1 | none | chosen from stage-2 row 200 (reconstructed) |
| 209 | gh-issue-view | https://github.com/chriskohlhoff/asio/issues/1657 | 0 | 1 | none | chosen from stage-2 row 201 (reconstructed) |
| 210 | gh-issue-view | https://github.com/libuv/libuv/issues/5204 | 0 | 1 | none | chosen from stage-2 row 202 (reconstructed) |
| 211 | gh-issue-view | https://github.com/cppalliance/corosio/issues/267 | 0 | 1 | none | chosen from stage-2 row 204 (reconstructed) |
| 212 | gh-graphql-discussion | https://github.com/NVIDIA/stdexec/discussions/1133 | 0 | 1 | 97 (serper: "asioexec" stdexec boost asio) | reconstructed |
| 213 | gh-graphql-discussion | gh api graphql search(query:"repo:NVIDIA/stdexec process", type:DISCUSSION, first:10) | 0 | 6 | none | seeded by the task terms (process, libuv, macOS), not by a stage-1 row |
| 214 | gh-graphql-discussion | gh api graphql search(query:"repo:NVIDIA/stdexec libuv", type:DISCUSSION, first:10) | 0 | 0 | none | seeded by the task terms (process, libuv, macOS), not by a stage-1 row |
| 215 | gh-graphql-discussion | gh api graphql search(query:"repo:NVIDIA/stdexec macOS", type:DISCUSSION, first:10) | 0 | 0 | none | seeded by the task terms (process, libuv, macOS), not by a stage-1 row |
| 216 | gh-graphql-discussion | gh api graphql search(query:"std::execution libuv", type:DISCUSSION, first:10) | 0 | 0 | none | seeded by the task terms (process, libuv, macOS), not by a stage-1 row |
| 217 | gh-graphql-discussion | gh api graphql search(query:"senders receivers subprocess", type:DISCUSSION, first:10) | 0 | 3 | none | seeded by the task terms (process, libuv, macOS), not by a stage-1 row |
| 218 | gh-graphql-discussion | https://github.com/NVIDIA/stdexec/discussions/2039 | 0 | 1 | none | chosen from stage-2 row 213 (reconstructed) |
| 279 | gh-pr-view | bemanproject/net#38 | 0 | 1 | 62 (exa: beman.net networking senders P2762 kqueue) | recorded at choice time |
| 280 | gh-pr-view | bemanproject/execution#304 | 0 | 1 | 63 (exa: beman.execution std::execution reference implem...) | recorded at choice time |
| 281 | gh-pr-view | bemanproject/execution#276 | 0 | 1 | 63 (exa: beman.execution std::execution reference implem...) | recorded at choice time |
| 282 | gh-pr-view | TheHPXProject/hpx#7256 | 0 | 1 | 67 (exa: HPX std::execution P2300 senders implementation) | recorded at choice time |
| 283 | gh-pr-view | jbaldwin/libcoro#422 | 0 | 1 | 68 (exa: libcoro jbaldwin io_scheduler kqueue macOS) | recorded at choice time |
| 284 | gh-issue-view | facebookexperimental/libunifex#663 | 0 | 1 | 66 (exa: libunifex status maintenance 2026 io_uring) | recorded at choice time |
| 285 | gh-pr-view | llvm/llvm-project#114122 | 0 | 1 | 86 (firecrawl: firecrawl developer "std::execution libc++ impl...) | recorded at choice time |
| 286 | gh-pr-view | llvm/llvm-project#108870 | 0 | 1 | 86 (firecrawl: firecrawl developer "std::execution libc++ impl...) | recorded at choice time |
| 287 | gh-issue-search | gh search issues "kqueue" --repo boostorg/process | 0 | 0 | 95 (serper: "Boost.Process" v2 process_handle macOS kqueue ...) | recorded at choice time |
| 288 | gh-pr-search | gh search prs "signal" --repo boostorg/process | 0 | 9 | 60 (exa: Boost.Process v2 macOS async wait child process...) | recorded at choice time |

## 4. githubkit saved searches (reproduced read-only with controls) and proposed rows

`./dev/mise run research:collect` was not run because it writes a tracked path another lane owns (brief). The same `/search/code` queries that `dev/collect_saved_search.py` sends (`collect`, line 44; fixture path check at line 179) were reproduced with `gh api -X GET search/code -F per_page=5`, each beside a known-result control.

| seq | query | rc | total_count | first paths | seeded by |
|---|---|---|---|---|---|
| 265 | schema repo:openai/codex | 0 | 886 | codex-rs/config/src/tui_mouse_scroll.rs; codex-rs/core/src/config/schema.md; bazel/rule... | control |
| 266 | posix_spawn repo:libuv/libuv | 0 | 3 | src/unix/process.c; ChangeLog; test/test-spawn.c | 85 |
| 267 | README repo:libuv/libuv | 0 | 4 | docs/src/index.rst; CONTRIBUTING.md; ChangeLog | control |
| 268 | use_sender repo:NVIDIA/stdexec | 0 | 6 | include/asioexec/use_sender.hpp; include/exec/asio/use_sender.hpp; test/exec/asio/test_... | 59 |
| 269 | kqueue repo:NVIDIA/stdexec | 0 | 0 |  | 58 |
| 270 | posix_spawn repo:NVIDIA/stdexec | 0 | 0 |  | 57 |
| 271 | README repo:NVIDIA/stdexec | 0 | 1 | test/rrd/README.md | control |
| 272 | EVFILT_PROC repo:chriskohlhoff/asio | 0 | 0 |  | 95 |
| 273 | kqueue_reactor repo:chriskohlhoff/asio | 0 | 8 | include/asio/detail/kqueue_reactor.hpp; include/asio/detail/impl/kqueue_reactor.ipp; in... | 74 |
| 274 | SIGCHLD repo:boostorg/process | 0 | 56 | include/boost/process/v1/detail/posix/sigchld_service.hpp; src/error.cpp; doc/version2.... | 60 |
| 275 | kqueue repo:bemanproject/net | 0 | 1 | README.md | 62 |
| 276 | poll repo:bemanproject/net | 0 | 13 | include/beman/net/detail/io_context_scheduler.hpp; include/beman/net/detail/iocp_contex... | control |
| 277 | kqueue_t repo:cppalliance/corosio | 0 | 23 | include/boost/corosio/backend.hpp; doc/lint/README.md; src/corosio/src/io_context.cpp | 73 |

## 5. Stage-2 searches run against the stage-1 results (seed-to-search map)

| stage-1 row | provider and query | stage-2 rows it seeded |
|---|---|---|
| 54 | exa: std::execution P2300 C++26 implementation status libc++ libstdc++ 2026 | 132 gh-issue-view NVIDIA/stdexec/issues/1924; 156 gh-api llvm/llvm-project/blob/main/libcxx/docs/Status/Cxx26Paper... |
| 55 | exa: libstdc++ std::execution senders implementation GCC 17 | 187 gh-api gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/std/e...; 188 gh-api gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/bits/...; 189 gh-api gcc-mirror/gcc/commits/master/libstdc%2B%2B-v3/include/st... |
| 57 | exa: stdexec process spawn child process sender | 270 gh-code-search-saved gh api -X GET search/code -f q='posix_spawn repo:NVIDIA/s... |
| 58 | exa: stdexec kqueue macOS io context | 142 gh-pr-view NVIDIA/stdexec/pull/1258; 269 gh-code-search-saved gh api -X GET search/code -f q='kqueue repo:NVIDIA/stdexe... |
| 59 | exa: asioexec stdexec asio completion token sender | 102 gh-api gh api repos/SamGaaWaa/asio2exec; 130 git-clone git clone --depth 1 --filter=blob:none SamGaaWaa/asio2exec; 137 gh-issue-view NVIDIA/stdexec/issues/1684; 139 gh-pr-view NVIDIA/stdexec/pull/1501; 268 gh-code-search-saved gh api -X GET search/code -f q='use_sender repo:NVIDIA/st... |
| 60 | exa: Boost.Process v2 macOS async wait child process kqueue SIGCHLD | 193 gh-issue-view boostorg/process/issues/432; 195 gh-issue-view boostorg/process/issues/531; 274 gh-code-search-saved gh api -X GET search/code -f q='SIGCHLD repo:boostorg/pro...; 288 gh-pr-search gh search prs "signal" --repo boostorg/process |
| 61 | exa: Boost.Cobalt coroutines asio process io 2026 | 206 gh-issue-search gh search issues "process" --repo boostorg/cobalt --limit 15 |
| 62 | exa: beman.net networking senders P2762 kqueue | 199 gh-issue-search gh search issues "kqueue" --repo bemanproject/net --limit 15; 275 gh-code-search-saved gh api -X GET search/code -f q='kqueue repo:bemanproject/...; 279 gh-pr-view bemanproject/net#38 |
| 63 | exa: beman.execution std::execution reference implementation status 2026 | 197 gh-issue-search gh search issues "gcc 16" --repo bemanproject/execution -...; 198 gh-issue-search gh search issues "macos" --repo bemanproject/execution --...; 280 gh-pr-view bemanproject/execution#304; 281 gh-pr-view bemanproject/execution#276 |
| 64 | exa: senders receivers libuv integration scheduler | 100 gh-api gh api repos/koloshmet/uvexec; 103 gh-api gh api repos/intel/cpp-baremetal-senders-and-receivers; 128 git-clone git clone --depth 1 --filter=blob:none koloshmet/uvexec |
| 65 | exa: C++ senders receivers library async I/O 2026 new library | 101 gh-api gh api repos/Cra3z/coio; 129 git-clone git clone --depth 1 --filter=blob:none Cra3z/coio |
| 66 | exa: libunifex status maintenance 2026 io_uring | 284 gh-issue-view facebookexperimental/libunifex#663 |
| 67 | exa: HPX std::execution P2300 senders implementation | 282 gh-pr-view TheHPXProject/hpx#7256 |
| 68 | exa: libcoro jbaldwin io_scheduler kqueue macOS | 283 gh-pr-view jbaldwin/libcoro#422 |
| 70 | exa: Taskflow stdexec integration scheduler | 192 gh-issue-view taskflow/taskflow/issues/782 |
| 71 | exa: oneTBB senders receivers std::execution | 207 gh-issue-search gh search issues "sender" --repo uxlfoundation/oneTBB --l... |
| 73 | exa: cppalliance corosio coroutine networking library | 204 gh-issue-search gh search issues "process" --repo cppalliance/corosio --l...; 205 gh-issue-search gh search issues "sender" --repo cppalliance/corosio --li...; 277 gh-code-search-saved gh api -X GET search/code -f q='kqueue_t repo:cppalliance... |
| 74 | exa: libuv vs asio comparison process signals timers C++ | 273 gh-code-search-saved gh api -X GET search/code -f q='kqueue_reactor repo:chris... |
| 75 | exa: stdexec GCC 16 build | 131 gh-issue-view NVIDIA/stdexec/issues/1747; 133 gh-issue-view NVIDIA/stdexec/issues/2148 |
| 85 | firecrawl: firecrawl developer "stdexec senders process spawning posix_spawn k... | 202 gh-issue-search gh search issues "posix_spawn" --repo libuv/libuv --limit 15; 203 gh-issue-search gh search issues "kqueue process" --repo libuv/libuv --li...; 266 gh-code-search-saved gh api -X GET search/code -f q='posix_spawn repo:libuv/li... |
| 86 | firecrawl: firecrawl developer "std::execution libc++ implementation pull requ... | 153 gh-issue-search gh search issues "std::execution" --repo llvm/llvm-projec...; 154 gh-pr-search gh search prs "[libc++] execution sender" --repo llvm/llv...; 285 gh-pr-view llvm/llvm-project#114122; 286 gh-pr-view llvm/llvm-project#108870 |
| 89 | firecrawl: firecrawl developer "Boost.Process v2 async_wait macOS" | 194 gh-issue-view boostorg/process/issues/528 |
| 90 | firecrawl: firecrawl developer "asioexec use_sender boost asio stdexec" | 104 gh-api gh api repos/tradias/asio-grpc; 138 gh-issue-view NVIDIA/stdexec/issues/1849 |
| 95 | serper: "Boost.Process" v2 process_handle macOS kqueue EVFILT_PROC | 196 gh-issue-view boostorg/process/issues/430; 272 gh-code-search-saved gh api -X GET search/code -f q='EVFILT_PROC repo:chriskoh...; 287 gh-issue-search gh search issues "kqueue" --repo boostorg/process |
| 97 | serper: "asioexec" stdexec boost asio | 136 gh-issue-view NVIDIA/stdexec/issues/1727; 140 gh-pr-view NVIDIA/stdexec/pull/1503; 141 gh-pr-view NVIDIA/stdexec/pull/1875; 212 gh-graphql-discussion NVIDIA/stdexec/discussions/1133 |

Stage-2 rows with no stage-1 seed (32): 134; 135; 143; 144; 145; 146; 147; 148; 149; 150; 151; 152; 155; 191; 200; 201; 208; 209; 210; 211; 213; 214; 215; 216; 217; 218; 248; 249; 265; 267; 271; 276. Their seeds (prior reports R10, the task question, local findings, another stage-2 row, or a known-result control) are in section 3 and in each row's `note`. The 30 `gh api repos/...` metadata calls and the 15 tag listings were seeded by the task's candidate list; the 51 clone rows (24 failed on a local quoting bug, then 27 succeeded) are in the log as `git-clone`.

Proposed new `[[search]]` rows for `dev/saved-searches.toml` (not added; the file is another lane's), each with
the control that this run proved returns results:

```toml
[[search]]
id = "stdexec-asio-bridge"            # 6 hits: include/asioexec/use_sender.hpp, include/exec/asio/use_sender.hpp, tests
query = "use_sender"
repo = "NVIDIA/stdexec"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"                       # 1 hit (test/rrd/README.md)
expected_min = 1

[[search]]
id = "stdexec-os-sources"             # 0 hits today; a hit means stdexec gained kqueue or process code
query = "kqueue"
repo = "NVIDIA/stdexec"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "libuv-posix-spawn"              # 3 hits: src/unix/process.c, ChangeLog, test/test-spawn.c
query = "posix_spawn"
repo = "libuv/libuv"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "README"                       # 4 hits
expected_min = 1

[[search]]
id = "boost-process-sigchld"          # 56 hits; watches the no-signal-set work of boostorg/process#432
query = "SIGCHLD"
repo = "boostorg/process"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "beman-net-kqueue"               # 1 hit (README.md); a code hit means a kqueue backend landed
query = "kqueue"
repo = "bemanproject/net"
per_page = 5
max_pages = 1
max_items = 5
timeout_seconds = 15
[[search.control]]
query = "poll"                         # 13 hits
expected_min = 1
```

An issue-search companion (the collector only speaks `/search/code` today, `dev/collect_saved_search.py:179`):
`repo:llvm/llvm-project label:libc++ "std::execution"` (30 hits, row 153) would show when libc++ starts landing
P2300; a control is `repo:llvm/llvm-project label:libc++ "std::format"`. This needs a collector change first.

## 6. `std::execution` in October 2026 (question 1)

| Item | Status | Evidence |
|---|---|---|
| C++26 adoption | Technical work on C++26 finished at the March 2026 London (Croydon) meeting; `std::execution` (P2300R10 plus fixes P3396, P3481, P3570, P3682, P3887, P3826) is in, with `task` (P3552), async scopes (P3149), the parallel scheduler (P2079) and constexpr-exception diagnostics (P3557) | `O/docs/wg21/sutter-2026-03-cxx26-done.md:98-104`; `O/docs/cpp/cppreference-compiler-support-26.md:925-945, 1275-1300` |
| Feature-test macros | `__cpp_lib_senders` 202406L (202506L for the extensions), `__cpp_lib_task` 202506L, `__cpp_lib_counting_scope` 202506L, `__cpp_lib_parallel_scheduler` 202506L. `__cpp_lib_execution` is the older C++17 parallel-algorithm macro, not senders | `O/docs/cpp/cppreference-execution.md:1615-1626` |
| clang-p2996 fork libc++ (`f17c8d6`, "clang version 21.0.0git") | Not implemented: `__cpp_lib_senders` commented out; `__cpp_lib_execution` also commented out; `<execution>` has no sender identifiers; no `__execution` directory | `O/local/stdlib-execution-macros.txt:2-16`; `O/local/host-probe.txt` |
| Upstream libc++ (Homebrew LLVM 23.1.3) and Apple libc++ (CLT 27.0) | Same: commented out, no sender code | `O/local/stdlib-execution-macros.txt:17-46` |
| Upstream libc++ plan | Every P2300 row empty; tracker #105440 open since 2024-08-20; first sub-issue #229127 (set_value, set_error, set_stopped) opened 2026-10-05; LWG issues #204456, #171351 filed | `O/gh/files/llvm_Cxx26Papers.csv:77`; `O/gh/issues/llvm_llvm-project_105440.json`, `_229127.json`; `O/gh/search/llvm_execution_issues.json` |
| libstdc++ (GCC 16.2) | Not implemented: no `__cpp_lib_senders`; `<execution>` has 0 sender identifiers; the `std` module lists the names inside `#if __cpp_lib_senders` (`bits/std.cc:1120-1235`), so the export list is prepared but the macro is never defined | `O/local/stdlib-execution-macros.txt:47-62, 72-76` |
| libstdc++ trunk (GCC 17) | No sign of work: `<execution>` last changed for copyright years; `version.def` has no senders entry and a `FIXME` for `__glibcxx_execution`; GCC 17's changes page lists no `std::execution`; Bugzilla has no libstdc++ bug with "execution" in the title about senders (25 unrelated hits, so the route works) | `O/gh/files/gcc-mirror_commits_execution.json`; `O/gh/files/gcc-trunk_version.def:650, 1396`; `O/docs/gcc/gcc-17-changes.md:54-58`; `O/docs/gcc/bugzilla-libstdcxx-execution.json` |
| The fork's future | The p2996 lane uses the fork's own libc++ snapshot, so it cannot gain `std::execution` until the fork rebases onto a libc++ that has it (inference from the fork version string; UNVERIFIED as a plan of the fork) | `O/local/host-probe.txt` |
| Does stdexec build with GCC 16 and `-std=c++26`? | It did not: `-Werror` failures on deprecated variadic commas and on the constexpr-exception path, fixed and confirmed 2026-04-16 (#1747); the pinned vcpkg port is a later commit (`fee4d651`, dated 2026-05-25). With C++ modules GCC 16.1.1 crashes (ICE, #2148, open since 2026-07-27), "regardless of whether `-freflection` is enabled" per a commenter. GCC 16 is not in stdexec's CI matrix (GCC 12 to 15, Clang 16 and 22, AppleClang on macos-26) | `O/gh/issues/NVIDIA_stdexec_1747.json`, `_2148.json`; `O/local/vcpkg-ports/stdexec/portfile.cmake:7`; `O/repos/stdexec/.github/workflows/ci.cpu.yml:23-52, 361-392` |
| Does stdexec build with clang-p2996? | UNVERIFIED. The fork is Clang 21 based with its own libc++; stdexec CI covers Clang 16 and 22 with libc++, so the compiler generation is inside the tested range, but the fork itself and its assertions build are untested; no stdexec issue mentions P2996 or reflection except #2148 (searches rows 144, 145, 151) | `O/gh/search/stdexec_q1.json`, `_q2.json`, `_q8.json` |
| Reflection inside these libraries | None: no `std::meta`, `__cpp_impl_reflection` or `__cpp_lib_reflection` in stdexec's headers (local grep); Asio and libuv are pre-reflection C++ and C. Reflection stays at the declarative edges (R10 section 3.2; D135 glaze) | local grep of `O/repos/stdexec/include` |
| Second implementation | beman.execution: "Under development and not yet ready for production use"; tested on GCC 14-15, Clang 19-22, MSVC; now also holds `task` (beman.task retired); not in vcpkg | `O/repos/beman-execution/README.md:43, 92-101`; `O/repos/beman-task/README.md:7-10`; `O/gh/files/vcpkg-master_beman-execution.json` (404) |

Practical reading: for this repository `std::execution` means stdexec for the foreseeable future in both lanes, so
the code should name the model through a project alias and keep stdexec's `exec::` extensions out of public
interfaces where the standard has an equivalent.

## 7. The ecosystem around senders, and the alternatives (question 2)

Columns follow the request. "vcpkg" is the pinned baseline e456309 (`O/local/vcpkg-ports.txt`), with the
transitive non-host port count from `O/local/vcpkg-dependency-closure.txt`. "macOS I/O" means file and network I/O
on macOS.

| Library | Senders and receivers | Process | Signals | Timers | macOS I/O (file, network) | Maturity | Licence | vcpkg | Citation |
|---|---|---|---|---|---|---|---|---|---|
| `std::execution` (C++26) | Is the model | none | none | none (no timed scheduler in C++26) | none | Standard; no shipping implementation (section 6) | n/a | n/a | section 6 |
| NVIDIA stdexec | Reference implementation, plus `exec::` extras: `task`, `when_any`, `timed_thread_scheduler`, `any_sender_of`, sequence senders, counting scopes, parallel scheduler | none (0 code hits) | none | `exec::timed_thread_scheduler` (own thread) | io_uring context Linux only; libdispatch scheduler on macOS is CPU work only; I/O through asioexec | "experimental ... APIs may change" (README:15); no versioned releases (nvhpc tags only); 2,458 stars, pushed 2026-10-14; compile time is a known cost (#1719, down 35% in January 2026) | Apache-2.0 with LLVM exception | stdexec 2026-05-25#1; 0 ports, 15 with `[asio]`; builds a compiled parallel-scheduler library (`portfile.cmake:83`; link `STDEXEC::system_context`, #1477) | `O/repos/stdexec/README.md:15, 74-80`; `O/gh/issues/NVIDIA_stdexec_1719.json`, `_1477.json`; `O/gh/repos/NVIDIA_stdexec.json` |
| asioexec (in stdexec) | Adapts any Asio completion-token operation into a sender (`use_sender`, `completion_token`), Boost.Asio or standalone | through Asio libraries | Asio `signal_set` | Asio timers | as Asio | Maintained by the stdexec team (PRs #1501, #1503, 2025), moved to `exec/asio` (#1875); CI on macOS with Boost.Asio; open edges: Beast timeout executor use (#1727), streambuf forwarding (#1684), `when_all` with `finally` (#1849), recursive-lock opt-out for single thread (#1781) | as stdexec | `stdexec[asio]` | `O/repos/stdexec/include/exec/asio/asio_config.hpp.in:21-50`; `CMakeLists.txt:213-224`; `O/gh/prs/`, `O/gh/issues/` |
| Boost.Asio 1.92 (Asio 1.38.2) | Its own P2300-era sender concepts were deprecated in Asio 1.25.0; integrates through asioexec | none in Asio | `signal_set` over a self-pipe | `steady_timer` | kqueue sockets and pipes, TLS (OpenSSL); no async file I/O on macOS (`ASIO_HAS_FILE` only with io_uring or IOCP) | Very mature; Boost 1.92.0 released 2026-08-12; a kqueue reactor data race was reported fixed in commit 88cd813 and not reproducible with Boost 1.90 (asio#1657, still open) | BSL-1.0 | boost-asio 1.92.0, 14 ports; the standalone `asio` port is stale at 1.32.0 | `O/repos/asio/asio/src/doc/history.qbk:1076, 1241-1242`; `include/asio/detail/config.hpp:985-997, 1094-1103`; `include/asio/detail/impl/signal_set_service.ipp:44-48`; `O/gh/issues/chriskohlhoff_asio_1485.json`, `_1657.json` |
| Boost.Process v2 (1.92) | No (Asio completion tokens, so senders through asioexec) | Yes: default launcher is fork plus an error pipe, also vfork; attach to an existing pid; exit wait by SIGCHLD `signal_set` on macOS, pidfd on Linux; no process-group option (a custom `on_exec_setup` initializer can call `setpgid`) | installs a SIGCHLD handler, which overwrites an application's own (#432, open since 2024-12-02; fix branch not merged by 1.88) | via Asio | pipes via Asio | Maintained; macOS oddity with threads and stdin (#531); exit-callback delay under load when signals are used (#528) | BSL-1.0 | boost-process 1.92.0, 46 ports; a compiled library linking Boost.Filesystem unless `BOOST_PROCESS_USE_STD_FS` | `O/repos/boost-process/include/boost/process/v2/process_handle.hpp:14-21`; `process.hpp:136-137`; `detail/process_handle_signal.hpp:74-101`; `posix/default_launcher.hpp:360-362`; `doc/launcher.adoc:7-19, 72`; `doc/configuration.adoc`; `CMakeLists.txt:10-12, 54-58` |
| Boost.Cobalt | No (C++20 coroutines over Asio) | no own (Process v2 via Asio) | `io::signal_set` | `io::steady_timer` | as Asio, including `io::stream_file` where Asio has files | Maintained; an open build question about GCC 15 and 16 (#260) | BSL-1.0 | boost-cobalt 1.92.0, 33 ports | `O/repos/boost-cobalt/include/boost/cobalt/io/signal_set.hpp:14-24`; `O/gh/search/boostorg_cobalt_process.json` |
| libuv 1.52.1 (upstream 1.53.0) | None; only the uvexec proof of concept (timers, signals, TCP, UDP; no process) | Yes: `uv_spawn` uses `posix_spawn`, `POSIX_SPAWN_SETSID` for detached children, reaps through kqueue `EVFILT_PROC` (no SIGCHLD handler on kqueue systems) | `uv_signal` | `uv_timer` | File I/O on a thread pool on every platform; TCP, UDP, pipes; no TLS or HTTP | Very mature (Node.js); 27,259 stars; v1.53.0 on 2026-09-24; macOS `posix_spawn` EBADF above fd 10239 (#5204, an Apple libc bug that also hits our own `posix_spawn`) | MIT | libuv 1.52.1, 0 ports | `O/repos/libuv/src/unix/process.c:85-89, 486, 585-592, 1166`; `src/unix/kqueue.c:332-333`; `docs/src/fs.rst:12`; `ChangeLog:1`; `O/gh/issues/libuv_libuv_5204.json` |
| uvw 3.4.0 | No (C++ event wrapper over libuv) | via libuv | via libuv | via libuv | via libuv | Last push 2025-12 | MIT | uvw 3.4.0 | `O/gh/repos/skypjack_uvw.json` |
| Taskflow 4.1.0 | None of its own; stdexec ships a Taskflow-backed thread pool | no | no | no | none (CPU task graphs) | Active; v4.1.0 on 2026-06-20; the maintainer confirms the link is only the thread pool (#782) | MIT | taskflow 4.1.0, 0 ports | `O/repos/stdexec/include/exec/taskflow/taskflow_thread_pool.hpp:26-58`; `O/gh/issues/taskflow_taskflow_782.json` |
| oneTBB 2023.1.0 | None of its own; stdexec ships `tbbexec::tbb_thread_pool` | no | no | no | none (CPU) | Active; v2023.1.0 on 2026-07-13 | Apache-2.0 | tbb 2023.1.0, 0 ports | `O/repos/stdexec/include/tbbexec/tbb_thread_pool.hpp`; `O/gh/releases/uxlfoundation_oneTBB_tags.json` |
| libunifex 0.4.0 | Yes, pre-standard ancestor of P2300 | no | no | `timed_single_thread_context` | io_uring and epoll contexts (Linux), Win32; no kqueue | "experimental in nature" (README:15-17); last release 2023-10-23 | Apache-2.0 with LLVM exception (port has no licence field) | libunifex 0.4.0 | `O/repos/libunifex/README.md:15-17`; `include/unifex/linux/`; `O/gh/issues/facebookexperimental_libunifex_663.json` |
| HPX (vcpkg 1.11.0; upstream 2.0.0) | Own P2300 layer, can use stdexec (`HPX_WITH_STDEXEC_TAG`); future-to-sender bridge merged 2026-08-02 (#7256) | distributed process component | n/a | yes | uses Asio internally | Mature HPC runtime, heavy | BSL-1.0 | hpx 1.11.0, 80 ports | `O/repos/hpx/CMakeLists.txt:651-663`; `components/process/`; `O/gh/prs/TheHPXProject_hpx_7256.json` |
| Folly coro | No (`folly::coro::Task`) | `folly::Subprocess` (vfork, synchronous) | n/a | `EventBase` (libevent) | yes, through libevent | Very mature, very heavy | Apache-2.0 | folly 2026.02.23#2, 71 ports | `O/repos/folly/folly/Subprocess.cpp:996` |
| concurrencpp 0.1.7 | No (coroutines and executors) | no | no | `timer_queue` | none | Last release 2023-07-15, last push 2025-05-01 | MIT | concurrencpp 0.1.7#2 | `O/repos/concurrencpp/README.md:50-52` |
| libcoro 0.16.0 | No (coroutines) | no | no | scheduler timeouts | kqueue notifier, TCP and TLS sockets; no files | Active; kqueue shutdown fix merged 2025-12-26 (#422) | Apache-2.0 | libcoro 0.16.0 | `O/repos/libcoro/include/coro/detail/io_notifier_kqueue.hpp:19-23`; `O/gh/prs/jbaldwin_libcoro_422.json` |
| cppcoro | No (coroutines) | no | no | Windows only | I/O implemented only for Windows IOCP | Unmaintained (last push 2024-01-09) | MIT | not in baseline | `O/repos/cppcoro/README.md:62, 1474` |
| Seastar | No (futures) | Linux only (the reactor includes `<sys/epoll.h>`) | | | | Mature, Linux | Apache-2.0 | not in baseline | `O/repos/seastar/src/core/reactor_backend.cc:35` |
| beman.execution | Yes (C++26 target), with `task` merged in | no | no | no | none | Under development; CI adds Clang 23 (#304, 2026-07-29) | Apache-2.0 with LLVM exception | not in vcpkg | `O/repos/beman-execution/README.md:43, 92-101`; `O/gh/prs/bemanproject_execution_304.json`, `_276.json` |
| beman.net (P2762) | Yes (networking senders, C++29 target) | no | no | `timer.hpp` | `poll(2)` only on macOS; io_uring context on Linux (#38, merged 2026-02-19) | Under development | Apache-2.0 with LLVM exception | not in vcpkg | `O/repos/beman-net/README.md:12-20`; `O/gh/prs/bemanproject_net_38.json` |
| Boost.Corosio and Boost.Capy (2026) | No, coroutine-only by design ("No sender/receiver") | no (#267 open) | `signal_set` | yes | kqueue backend; files on a thread pool on POSIX; TLS (OpenSSL, wolfSSL) | Beta (2026-03-11), heading for Boost review; created 2026-01-06 | BSL-1.0 | not in baseline | `O/docs/cppalliance/corosio-beta-2026-03.md:30-40`; `O/repos/corosio/include/boost/corosio/backend.hpp:245-277`; `stream_file.hpp:41`; `O/gh/issues/cppalliance_corosio_267.json` |
| Smaller sender I/O projects | coio (senders over epoll, io_uring, IOCP; no kqueue), senders-io (io_uring, "still very experimental"), asio2exec (single-header Asio to senders), Intel baremetal senders (embedded subset) | no | coio yes | yes | none on macOS | 22 to 288 stars | MIT, Apache-2.0, BSL-1.0 | not in baseline | `O/repos/coio/README.md`; `O/repos/asio2exec/README.md:1-30`; `O/docs/wg21/p4041r0.md:356-392` |

Two outside views worth weighing, with their bias stated. P4041R0 (Vinnie Falco, May 2026, author of Corosio and
Capy) counts the sender I/O ecosystem at 21 stars against 1,300 for the reference implementation, finds no public
sender library for TLS, DNS or signal handling, and quotes SG14's February 2026 advice that networking should not
be built on P2300 (`O/docs/wg21/p4041r0.md:86-90, 340-342, 356-392`). A practitioner trying stdexec found
silent serial fallbacks and about 5 s of build time for one translation unit, and stayed on TBB
(`O/docs/blogs/mropert-2025-11-trying-stdexec.md:160-163, 224, 239`). On the other side, a production user reports
stdexec running an ML trading system (stdexec discussion #2039, 2026-04-21), and Sutter reports production use while
warning that helper adapters are still needed (`O/docs/wg21/sutter-2026-03-cxx26-done.md:104`).

## 8. Needs-to-library map (question 3)

| Component (source) | Need | Best fit | Why |
|---|---|---|---|
| Agent-dispatch CLI, CT-59 (CT59:73-78, F3 at :154) | Spawn `claude` or `codex` with stdin from a file and stdout and stderr straight to 0600 files; deadline; stop ladder SIGINT, SIGTERM, SIGKILL to the process group; catch SIGINT and SIGTERM | OS built-ins now (`posix_spawn` + `POSIX_SPAWN_SETSID`, `killpg`), driven by the standard stack: one `io_context`, a SIGINT/SIGTERM `signal_set`, a `steady_timer` deadline, the SIGCHLD reaper, composed with `when_any`-style racing and stop tokens | One child needs no event-loop library (CT-59 F3 and R13 both chose `posix_spawn`); the stack adds structured cancellation without a second mechanism. A self-pipe loop is acceptable for the first unit if the stack's admission lags |
| Crawl scheduler and resource sensor (R10 sections 3.1-3.3; D107, D120) | N webclaw children, live concurrency, shed the youngest group and requeue, sample memory and disk on a tick, react to Ctrl-C | The standard stack: `counting_scope` (or stdexec's `async_scope`) for a dynamic set of child senders, a `steady_timer` tick, `signal_set`, the reaper; sensor reads stay synchronous system calls (`sysctlbyname`, `statfs`, `proc_pid_rusage`, R10 section 3.1) | Structured concurrency maps directly onto "N children, cancel some, wait for all"; R10's wave plan (GNU parallel now, native later) is unchanged |
| Heavy-run gate (R11 verdict; D123, D133) | `flock(2)`, run one child, report the holder | Plain C++23, no async library: `flock`, `posix_spawn`, blocking `waitpid` | D133 wants a variant Apple Clang builds on a fresh machine; a bootstrap tool should not need a vcpkg fetch |
| `rsm-core` bridge CLI (ADR 0008; D130) | Read one JSON request on stdin, write JSON on stdout | Synchronous read to EOF and glaze or jsoncons (D135); `sync_wait` on a sender only when the request starts asynchronous work | No event loop is needed to parse and answer; senders give a clean synchronous boundary |
| Deny gates in C++ (D131; R8) | Read hook JSON, decide, exit fast, maybe run `git` | Plain C++, no async library | R8: process start time dominates; a gate must not pull in heavy headers |
| Later network clients (Exa, GitHub, Serper and similar) | HTTPS requests, timeouts, retries, concurrency limits | Asio TLS with Beast or glaze's Asio networking (R15 under D135), exposed as senders through asioexec | libuv has no TLS or HTTP; the sender TLS and HTTP ecosystem is empty (P4041R0:356-392) |
| CPU-parallel work (none planned) | Parallel loops or task graphs | stdexec's parallel scheduler; Taskflow or oneTBB pools only if measured | No current component needs it |

## 9. libuv against a senders stack, and the hybrids (question 4)

What libuv gives: the best process story on macOS (`posix_spawn` with `SETSID`, kqueue `EVFILT_PROC` reaping, so
no global SIGCHLD handler), signals, timers, file I/O on every platform through its thread pool, resource
readers, zero dependencies and MIT licence (section 7 row). What it lacks for this repository: TLS and HTTP, any
maintained C++ or sender integration, and a C callback model that every component would wrap differently.

What a senders stack gives: one standard vocabulary for composition, error and stop propagation, structured
lifetimes (`counting_scope`, `spawn`), a coroutine `task`, and a `sync_wait` boundary for synchronous callers; code
written against it moves to the standard library when both lanes ship `__cpp_lib_senders`. What it lacks: every OS
event source; heavy templates (#1719; mropert); an experimental reference implementation without releases.

Hybrids found:

| Hybrid | State | Cost to us |
|---|---|---|
| stdexec over Asio (asioexec) | Maintained inside stdexec, tested on macOS with Boost.Asio | Admission of `stdexec[asio]`; a reaper for children (about 100 to 200 lines, estimate) |
| stdexec over libuv | Only uvexec: one star, last push 2024-07-18, no process support, pinned to a 2024 stdexec | A sender adapter for the loop scheduler, timers, signals, spawn and exit, later sockets (about 300 to 500 lines, estimate), plus a separate TLS and HTTP story later |
| Asio alone with coroutines (`asio::awaitable`, Boost.Cobalt) | Mature | No standard vocabulary; the user asked for `std::execution` |
| Coroutine-only libraries (Corosio and Capy, libcoro) | Corosio beta, no process support; libcoro has kqueue but no process or signals | Not senders; Corosio not in vcpkg |
| A home-made kqueue and epoll sender context (as stdexec's io_uring context is built) | Nothing to reuse on macOS | Most code; not recommended (D107 prefers existing libraries) |

## 10. Recommendation, admission, effect on the accepted baseline, risks (question 5)

Stack: stdexec (project alias) plus Boost.Asio single-threaded `io_context` plus asioexec, with `posix_spawn` and a
reaper for children; Boost.Process v2 as fallback for the reaper; libuv as fallback for the whole loop.

Admission (proposal, follows the D135 pattern): one admitted vcpkg fetch at baseline e456309 of `stdexec[asio]`
for the four lane triplets (`arm64-osx-p2996-{static,dynamic}`, `arm64-osx-gcc16-{static,dynamic}`; today only fmt
12.2.0 is installed there, `O/local/vcpkg-installed-ls.txt`). The stdexec port also downloads hash-pinned
rapids-cmake v24.02.01, CPM.cmake 0.38.5, icm v1.5.0 and the `execution.bs` spec file
(`O/local/vcpkg-ports/stdexec/portfile.cmake:7, 29, 39, 54, 64`), and builds the parallel-scheduler library
(`:83`). Then a both-lane compile probe: one translation unit that runs `sync_wait` over a `steady_timer` through
`use_sender`, a `signal_set`, a spawned `/usr/bin/true` reaped by the SIGCHLD path and a `counting_scope`, built with
`-std=c++26` and `-Werror` in both lanes, with `-freflection` (gcc16) and `-freflection-latest` (p2996) on, no C++
modules (#2148). Boost.Process v2 (46 ports, compiled) is fetched only if the reaper prototype fails.

Effect on AD:88 (proposed amendment for the user; R14 does not edit it): "Prefer a single-thread event loop by
default: a single-threaded Boost.Asio `io_context` driven through `std::execution` senders (stdexec until both
standard libraries ship `__cpp_lib_senders`, reached through one project alias). Child processes start with
`posix_spawn`; libuv is the fallback if the both-lane probe fails." The SPSC/MPSC sentence stays.

Risks:

1. Compile cost: stdexec template instantiation dominates builds (#1719; about 5 s for one unit in mropert's
   test). Keep sender code in few translation units, type-erase at component boundaries (`task`,
   `any_sender_of`), and measure in the probe. No measurement exists yet (gap).
2. Toolchain: GCC 16 broke stdexec once (#1747, fixed) and crashes with modules (#2148, open); neither GCC 16 nor
   the p2996 fork is in stdexec's CI. The probe must pass in both lanes before any unit depends on it.
3. Reference implementation churn: stdexec says APIs may change, has no releases, and moved asioexec once
   (#1875). Pin the vcpkg port, use only standard names in public interfaces.
4. Process reaping on macOS through SIGCHLD: the core is a CLI that owns `main`, so a process-wide SIGCHLD handler
   is acceptable, but it would conflict if the library were ever embedded in a host that reaps its own children
   (boostorg/process#432). Keep the reaper behind one interface so a kqueue `EVFILT_PROC` path can replace it.
5. macOS `posix_spawn` fails with EBADF once descriptors pass 10239 (libuv#5204, Apple libc); every stack that
   uses `posix_spawn` shares it. Keep descriptor counts low or fall back to fork for that case.
6. asioexec edges: Beast timeouts use an executor after completion (#1727), a recursive lock costs in the
   single-thread case (#1781 open), `when_all` with `finally` hung on stop (#1849). Prefer stdexec timers for
   deadlines around Beast operations.
7. No async file I/O in Asio on macOS. Not needed today (dispatch redirects child output to files by descriptor);
   blocking writes or a small thread pool cover the rest.
8. CI image: the Linux OCI image has GCC 12 (R8). stdexec tests GCC 12 (`ci.cpu.yml:39-43`), so non-reflection
   code can build there; reflection code cannot regardless (R8).
9. Ecosystem thinness: there is no public sender library for TLS, HTTP or signals (P4041R0, a biased but
   checkable source); the adapters are ours or asioexec's.

## 11. Code examples found

- asioexec, Asio operation to sender: https://github.com/NVIDIA/stdexec/blob/5fc945fac81ae9b5b4ef190d20d0d74b705bee2a/include/exec/asio/use_sender.hpp
  (`O/repos/stdexec/include/exec/asio/use_sender.hpp:73-212`); configuration for Boost or standalone Asio: same
  commit, `include/exec/asio/asio_config.hpp.in#L21-L50`.
- stdexec configurable namespace: same commit, `include/stdexec/__detail/__config.hpp#L244-L250`.
- stdexec Taskflow pool adapter: same commit, `include/exec/taskflow/taskflow_thread_pool.hpp#L26-L58`.
- libuv spawn with SETSID and kqueue reaping: https://github.com/libuv/libuv/blob/ad0679ae37afe4ea415772b5a86020032d5db2f8/src/unix/process.c#L585-L592
  and `#L1166`; `src/unix/kqueue.c#L332-L333`.
- Boost.Process v2 SIGCHLD handle and attach-to-pid: https://github.com/boostorg/process/blob/cfbaf1f0ae6d5b6c49c904fa0c178934071bfe92/include/boost/process/v2/detail/process_handle_signal.hpp#L74-L101
  and `include/boost/process/v2/process.hpp#L136-L137`.
- uvexec, senders over libuv: https://github.com/koloshmet/uvexec/blob/cccbeb93f5c28f99a682c16a0abf04309e49d405/README.md
- asio2exec, single-header Asio to senders: https://github.com/SamGaaWaa/asio2exec/blob/aadedf6545e3aef3dbac156cfdd3cf2707dd79ed/README.md
- glaze Asio selection: https://github.com/stephenberry/glaze/blob/e194d23e33c0739a7214161af27e47bc9a6a4e30/include/glaze/ext/glaze_asio.hpp#L22-L44
- Wrapping a C callback API as a sender (the pattern the reaper and any libuv adapter would follow):
  https://ericniebler.com/2024/02/04/what-are-senders-good-for-anyway/ (`O/docs/blogs/niebler-2024-senders-good-for.md:20-122`).
- kqueue `EVFILT_PROC` wait with a timeout: https://gaultier.github.io/blog/way_too_many_ways_to_wait_for_a_child_process_with_a_timeout.html
  (`O/docs/blogs/gaultier-wait-child-timeout.md`); filters in `O/local/man-kqueue.txt:353-411`.

Sketch of the dispatch core on the proposed stack (proposal, not compiled; names are ours):

```cpp
namespace ex = rsm::ex;                       // alias to stdexec today, std::execution later
ex::sender auto run_child(rsm::loop& loop, rsm::spawn_spec spec, std::chrono::seconds limit) {
  return ex::just(std::move(spec))
       | ex::let_value([&](rsm::spawn_spec& s) {
           auto child = rsm::spawn(s);                         // posix_spawn, POSIX_SPAWN_SETSID
           return exec::when_any(loop.reap(child.pid),         // SIGCHLD + waitpid in the io_context
                                 loop.after(limit) | ex::let_value([&] { return rsm::stop_ladder(child); }),
                                 loop.signal({SIGINT, SIGTERM}) | ex::let_value([&] { return rsm::stop_ladder(child); }));
         });
}
```

## 12. Routes table

`fx` = `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`. Keys reached curl through a config read on stdin (`curl -K -`), never argv or output.

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Exa | `fx exa.sh <out> "<query>" 10` x25 (POST api.exa.ai/search) | 0, HTTP 200 each | 10 each | Yes (23 of 25 queries) |
| 1 | Context7 | `fx ctx7 library "<name>" "<query>"` x5 | 1 each | "Monthly quota reached" | No; gap |
| 1 | Firecrawl search | `fx firecrawl search "<q>" --limit 5 --json` x1 | 1, HTTP 402 | 0 | No; gap |
| 1 | Firecrawl developer index | `fx firecrawl developer "<q>"` x6 | 0 each | 10 each | Yes (4 of 6) |
| 1 | webclaw | `webclaw -t 60 <url> -f markdown > <file>` x30 | 0 x29, 1 x1 (Citadel page) | 29 pages, one a login stub (Reddit) | Yes |
| 1 | Serper | `fx serper.sh <out> "<q>"` x7 | 0, HTTP 200 each | 0 to 10 | Yes (4 of 7) |
| 1 | SerpApi | not run | n/a | n/a | Serper answered |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3.13 -I last30days.py --plan plan.json --emit md --quick --search reddit,hackernews,github,x --save-dir "" "<topic>"` x2 | 1 (mise `timeout` shim, provider not reached), then 0 | 1 relevant item | Thin; gap |
| 2 | Repository metadata and tags | `gh api repos/<r>`, `.../releases?per_page=2`, `.../tags?per_page=3` | 0 | 30 repos | Yes |
| 2 | Issues, PRs, discussions | `gh issue view`, `gh pr view`, `gh search issues|prs`, `gh api graphql` (DISCUSSION) | 0 each | sections 3 and 5 | Yes |
| 2 | Raw files | `gh api -H 'Accept: application/vnd.github.raw' repos/<r>/contents/<path>[?ref=]` (libc++ papers CSV, GCC trunk `<execution>` and `version.def`, 11 vcpkg master ports, Boost.Asio 1.92 version, vcpkg asio portfile) | 0 (404 bodies for beman ports) | 16 files | Yes |
| 2 | GCC Bugzilla REST | `curl https://gcc.gnu.org/bugzilla/rest/bug?...` x3 | 0 | quicksearch off-target x2; short_desc query 25 | Yes (negative finding) |
| 2 | Saved searches | `./dev/mise run research:collect` | not run | n/a | Writes a tracked path another lane owns |
| 2 | Saved searches (reproduced) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5` x13 with controls | 0 each | section 4 | Yes |
| 2 | Clones (D110) | `git clone --depth 1 --filter=blob:none <url>` with hooks off | 128 x24 (local quoting bug), then 0 x27 | 27 repos | Yes, code reading only |
| local | Host facts | `--version` x4, `ls`, `grep` of stdlib headers, pinned vcpkg port manifests, `man 2 kqueue` | 0 | n/a | Yes (`O/local/`) |

## 13. Open gaps

- Nothing was compiled: whether stdexec, asioexec and Boost.Asio build in the clang-p2996 lane and in the gcc16
  lane with `-std=c++26 -Werror` and reflection flags is UNVERIFIED; the compile cost is unmeasured.
- The SIGCHLD reaper and the size estimates (100 to 200 lines for the reaper, 300 to 500 for a libuv sender
  adapter) are estimates; no prototype ran.
- Context7 (monthly quota) and Firecrawl search (HTTP 402) gave nothing; Last30Days gave one item (a C++Now 2026
  talk by Dietmar Kuhl, "Senders For Existing Asynchronous Interfaces", whose Reddit page mirrored only as a login
  stub); the Citadel article failed in webclaw.
- Seeds for stage-2 rows 131 to 278 were reconstructed after the fact (D137 reached this run mid-task); rows 279
  onward were recorded at choice time.
- Whether the macOS kqueue man page allows a kqueue descriptor to be watched by another kqueue (which would let an
  `EVFILT_PROC` queue sit inside Asio's reactor without SIGCHLD) is not stated in `O/local/man-kqueue.txt`;
  UNVERIFIED.
- When libc++ and libstdc++ will ship `std::execution` is unknown; only the start of libc++ work (2026-10-05) is
  evidenced.
- Whether Boost 1.92 (Asio, and Process if needed) builds cleanly with GCC 16.2 and the p2996 fork was not checked; only Cobalt's open build question (#260) surfaced.
