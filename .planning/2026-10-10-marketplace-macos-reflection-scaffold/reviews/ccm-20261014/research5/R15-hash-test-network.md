# R15: hash libraries, unit test frameworks and glaze networking for the C++ library (Q108)

Written by research agent R15 of session `ccm-20261014` (`ce9c0b3d`), 2026-10-14, for the three parts of
Q108 under D112 (one modern C++ library, P2996 wherever possible), D135 (glaze with static reflection,
jsoncons for D83 validation, R15 first) and D136 (no AGPL). It extends R13 (`research5/R13-cxx-deps.md`,
sections 3 and 5) and takes R14's execution-stack verdict as given (`research5/R14-execution-libraries.md`,
Verdict); it does not redo R13's JSON and schema sections or R14's execution comparison. Read-only except this
file and the offline mirror. MP = the repository root (branch `codex/marketplace-native-onboarding`).

Citation keys. OFF = `offline/research/R15-hash-test-network/` (untracked, D110). `OFF/manifest.json` lists
74 mirrored items (21 clones, 38 webclaw pages, 15 issue and PR copies) and 69 hashed receipts, with URL, local path, fetch time, command shape, exit code and SHA-256 (commit SHA for
clones); `OFF/queries.jsonl` logs every provider call (D137), 206 rows. OFF/repos are
`git clone --depth 1 --filter=blob:none --no-tags` copies cited as `OFF/repos/<owner>_<repo>/<path>:<line>`;
OFF/gh holds `gh --json` copies of issues, PRs and discussions; OFF/pages holds webclaw markdown;
OFF/receipts/probe holds this run's host probes. VCPKG = the pinned tree at
`e456309491fd875487bf02b8a0dca76c1b1b00cc` (the `vcpkg.json:4` builtin-baseline); its port manifests and
portfiles are copied into `OFF/receipts/probe/vcpkg-ports.txt` and `vcpkg-portfiles.txt`. No compiler or
benchmark was run: the brief allowed `ls` and `--version` only (`OFF/receipts/probe/host-probe.txt`), so every
speed figure is quoted from its source and every "compiles" claim rests on upstream CI. Anything without a
citation is labelled UNVERIFIED.

## Verdict

| Question | Recommendation | Confidence | Admission it needs |
|---|---|---|---|
| Q108.1 hashing | Boost.Hash2 as the one hashing framework: `hash_append` (the N3980 design) for hashing records, a small project `tag_invoke` bridge that walks members with P2996 in both lanes, and its `xxh3_128` or `siphash_64` for in-process hashing. SHA-256 bytes for artifact digests and receipts come from CommonCrypto (macOS) behind a Hash2-conforming adapter, not from Hash2's portable `sha2_256`. No xxHash, rapidhash or BLAKE3 dependency now. | medium | a `vcpkg.json` hunk adding `boost-hash2` 1.92.0 (header-only; pulls 7 Boost header ports); a compile probe in both lanes; known-answer tests |
| Q108.2 unit tests | stephenberry/ut v1.2.1 (MIT, one 419-line C++23 header, macro-free, compile-time tests, `import ut;`), vendored the way glaze vendors it, plus three project rules: one CTest entry per suite executable, a P2996 value printer for failure messages, and assertions only on the test's own thread. Catch2 3.16 stays the fallback if per-test CTest discovery, JUnit output, sharding or thread-safe assertions become requirements. No production-ready reflection-based framework exists. | medium | no vcpkg change; a lane that adds the vendored header with its LICENSE; a compile probe in both lanes plus ASan, UBSan and TSan runs of one sample suite |
| Q108.3 glaze networking | Do not adopt now: the library has no network need today (D130's `rsm-core` is JSON on stdin and stdout), glaze's two reflection CI jobs build no networking tests, and its RPC transport is marked unstable. When an HTTP or websocket need appears, glaze's client and server can run on R14's single Boost.Asio `io_context`, but install glaze core from vcpkg without the `networking` feature, because that feature forces standalone Asio 1.32.0 next to R14's Boost.Asio 1.92.0. | medium-high for "not now"; low for "glaze as the later HTTP layer" | none now; later: `boost-asio` through R14's `stdexec[asio]`, `openssl` 3.6.5 for TLS, and a both-lane probe of `glaze/net/*` with `-DGLZ_REFLECTION26=1` |

Evidence that decides it:

1. Hash2 has no P2996 code in 1.92.0: the scan found 0 matching files (`OFF/receipts/probe/p2996-usage-counts.txt`),
   and its only automatic member walk is Boost.Describe (`OFF/repos/boostorg_hash2/include/boost/hash2/hash_append.hpp:397-452`).
   Describe's develop branch added a P2996 backend on 2026-09-27 and 28 ("Add reflection support to
   describe_enumerators", "Enable reflection for describe_members", "Enable reflection for describe_bases";
   `OFF/gh/search/commits-reflection_repo_boostorg_describe.json`) that makes every non-template class with named,
   non-bit-field members "described" (`OFF/repos/boostorg_describe/include/boost/describe/detail/rf_members.hpp:83-120`),
   and Hash2 adjusted for it on 2026-09-29 (`8c93d7dc0`, `69e7e0213`; `OFF/gh/search/commits-reflection_repo_boostorg_hash2.json`)
   and added a GCC 16.2 `-freflection` CI job (`OFF/repos/boostorg_hash2/.github/workflows/ci.yml:80-86`). But the
   backend switches on only when both `__cpp_impl_reflection` and `__cpp_lib_reflection` are at least 202506L, and
   never on GCC 16.1 (`OFF/repos/boostorg_describe/include/boost/describe/detail/config.hpp:68-79`); R13 found the
   clang-p2996 fork defines neither macro (R13 Verdict item 4), and the change is after Boost 1.92.0, the VCPKG
   version (`OFF/receipts/probe/vcpkg-ports.txt`). Hence a project bridge for both lanes now, and the Describe path
   as a free upgrade for the GCC lane once a Boost release carries it.
2. SHA-256 must use the hardware. CommonCrypto `CC_SHA256` measured 2.57 GiB/s on an M2 Air and 3.28 GiB/s on an
   M4 Pro (`OFF/pages/notonbluray-apple-sha256.md:5-20`); OpenSSL 3.6.4 reached 3,356 MB/s on an M4 at 16 KB
   blocks, while portable implementations on the same M4 ran at 574 to 595 MB/s
   (`OFF/pages/picklog-md5-sha256-m4.md:4-5,11-18,42-43`). Hash2's `sha2_256` is portable code with no SHA
   instructions (no intrinsics anywhere in `OFF/repos/boostorg_hash2/include`) and its author measured 320.57 MB/s
   after his own speed-up, on unspecified hardware (boostorg/hash2#31, merged 2024-12-31;
   `OFF/gh/boostorg_hash2_31.json`). BLAKE3's C library is not faster here either: single-threaded on Apple silicon
   it took 621 ms against `openssl sha256`'s 553 ms for 1 GiB (BLAKE3-team/BLAKE3#315, comment of 2024-02-26;
   `OFF/gh/BLAKE3-team_BLAKE3_315.json`), and CT-59 records `sha256` per artifact
   (`reviews/ccm-20261014/ct59/CT59-design.md:28-29`).
3. Only one macro-free framework is compiled in CI by both of our reflection compilers: stephenberry/ut. glaze
   vendors ut v1.2.1 byte for byte apart from a three-line header comment (`diff` of
   `OFF/repos/stephenberry_glaze/tests/ut/ut.hpp` against `OFF/repos/stephenberry_ut/include/ut/ut.hpp`) and builds
   all its tests with `-std=c++26 -freflection` on `gcc:16.1` and with `-std=c++26 -freflection
   -fexpansion-statements -stdlib=libc++` on the clang-p2996 image
   (`OFF/repos/stephenberry_glaze/.github/workflows/gcc.yml:186-201`, `p2996-reflection.yml:70-91`). boost-ext/ut,
   the original, has an open thread-safety crash since 2024-03-06 (boost-ext/ut#618), a broken `import boost.ut`
   (#713, open since 2026-04-09), no release since 2025-04-02, and needed 197 s against Catch2's 74 s to build a
   typed-test suite in snitch's benchmark (`OFF/repos/snitch-org_snitch/README.md:249-258`).
4. glaze networking is younger than glaze's codec. Both reflection CI jobs pass `-Dglaze_BUILD_NETWORKING_TESTS=OFF`
   (`gcc.yml:193`, `p2996-reflection.yml:87`); the maintainer wrote on 2026-03-12 that the HTTP and websocket code
   "has been focused on API development and correctness more than raw performance right now, since it is still
   new" (stephenberry/glaze#2366); the REPE docs say `glz::asio_server`, `glz::asio_client` and
   `glz::repe::registry` "are all under active development and should not be considered stable"
   (`OFF/repos/stephenberry_glaze/docs/rpc/repe-rpc.md:3-5`); and the VCPKG port's `networking` feature patches
   `glaze_asio.hpp` to `#if 1` and aliases `glaze::asio` to standalone `asio::asio`
   (`OFF/receipts/probe/vcpkg-portfiles.txt`, glaze portfile; `OFF/receipts/probe/vcpkg-glaze-patch-usage.txt`).

## 1. Queries sent to each tool, plugin or service (stage 1)

Exact text as sent; `seq` is the row in `OFF/queries.jsonl`. Rows 1 to 119 were backfilled from scratch files when D137 arrived mid-run (their `logged_at` is the backfill time); later rows were logged as sent.


**exa** (36 calls)

| seq | Query (exact) | rc | HTTP |
|---|---|---|---|
| 1 | Boost.Hash2 library review hash_append described classes | 0 | 200 |
| 2 | boostorg hash2 SHA-256 BLAKE2 xxhash algorithms performance | 0 | 200 |
| 3 | C++26 static reflection hash_append P2996 automatic hashing of structs | 0 | 200 |
| 4 | types don't know # hash_append N3980 reflection C++26 | 0 | 200 |
| 5 | rapidhash benchmark wyhash successor speed | 0 | 200 |
| 6 | xxHash XXH3 benchmark Apple M1 M2 GB/s | 0 | 200 |
| 7 | BLAKE3 C library performance ARM NEON Apple silicon vs SHA-256 | 0 | 200 |
| 8 | SHA-256 performance Apple M1 ARMv8 crypto extensions OpenSSL CommonCrypto GB/s | 0 | 200 |
| 9 | ankerl unordered_dense hash function wyhash benchmark | 0 | 200 |
| 10 | SMHasher hash function quality speed comparison 2025 | 0 | 200 |
| 11 | stephenberry ut unit testing framework fork boost-ext ut | 0 | 200 |
| 12 | boost-ext ut macro-free unit testing C++20 compile time benchmark | 0 | 200 |
| 13 | Catch2 3.16 release notes | 0 | 200 |
| 14 | snitch C++20 testing framework constexpr compile time | 0 | 200 |
| 15 | C++ unit testing framework 2025 2026 new C++23 C++26 | 0 | 200 |
| 16 | C++26 reflection unit test framework automatic test registration P2996 | 0 | 200 |
| 17 | doctest vs Catch2 vs ut compile time benchmark 2025 | 0 | 200 |
| 18 | GoogleTest C++26 reflection value printing | 0 | 200 |
| 19 | constexpr unit testing static_assert C++ framework compile-time tests | 0 | 200 |
| 20 | C++20 modules unit test framework import std | 0 | 200 |
| 21 | glaze HTTP server REST registry asio | 0 | 200 |
| 22 | glaze websocket client server C++ | 0 | 200 |
| 23 | glaze JSON-RPC 2.0 REPE RPC asio | 0 | 200 |
| 24 | glaze networking standalone asio boost asio TLS openssl | 0 | 200 |
| 25 | glaze http client https coroutine | 0 | 200 |
| 26 | C++ REST server library 2026 comparison asio beast drogon crow glaze | 0 | 200 |
| 27 | Boost.Hash2 Peter Dimov hash_append_size P2996 reflection describe | 0 | 200 |
| 28 | komihash a5hash fast hash function 2025 benchmark | 0 | 200 |
| 29 | C++ SHA-256 library header only modern constexpr C++20 | 0 | 200 |
| 30 | Catch2 CTest catch_discover_tests sanitizer support | 0 | 200 |
| 31 | stephenberry glaze networking http server production maturity | 0 | 200 |
| 32 | reflection-based test framework value printing C++ std::meta | 0 | 200 |
| 180 | Boost 1.93 release schedule date beta | 0 | 200 |
| 181 | Boost.Describe C++26 reflection support describe_members without macros | 0 | 200 |
| 182 | glaze stdexec sender asio http client integration | 0 | 200 |
| 183 | Catch2 address sanitizer catch_discover_tests PRE_TEST workaround ASAN_OPTIONS | 0 | 200 |

**serper** (8 calls)

| seq | Query (exact) | rc | HTTP |
|---|---|---|---|
| 39 | stephenberry ut fork of boost-ext ut differences C++23 | 0 | 200 |
| 40 | Boost.Hash2 C++26 reflection hash_append automatic | 0 | 200 |
| 41 | glaze http server asio production use websocket review | 0 | 200 |
| 42 | rtest codeberg JonasToth C++26 reflection testing | 0 | 200 |
| 43 | C++ unit testing framework compile time benchmark Catch2 3 doctest ut snitch 2025 | 0 | 200 |
| 44 | SHA-256 Apple M4 OpenSSL speed GB/s ARMv8 SHA2 instructions | 0 | 200 |
| 45 | BLAKE3 vs SHA-256 Apple M-series single thread benchmark 2025 | 0 | 200 |
| 46 | snitch testing framework release 1.3 2025 | 0 | 200 |

**context7** (4 calls)

| seq | Query (exact) | rc | HTTP |
|---|---|---|---|
| 33 | ctx7 library "glaze" "http server asio tls" | 1 | n/a |
| 34 | ctx7 library "boost hash2" "hash_append described class" | 1 | n/a |
| 35 | ctx7 library "catch2" "catch_discover_tests sanitizer" | 1 | n/a |
| 36 | ctx7 library "snitch" "constexpr test" | 1 | n/a |

**firecrawl** (2 calls)

| seq | Query (exact) | rc | HTTP |
|---|---|---|---|
| 37 | firecrawl search "Boost.Hash2 hash_append C++26 reflection" --limit 5 --json | 1 | 402 |
| 38 | firecrawl scrape https://stephenberry.github.io/glaze/networking/http-server/ --format markdown | 1 | 402 |

**last30days** (2 calls)

| seq | Query (exact) | rc | HTTP |
|---|---|---|---|
| 47 | "C++ test frameworks, hashing libraries and glaze networking" --plan plan.json (3 subqueries: cpp-test-frameworks, cpp-hashing, glaze-networking) --emit json --quick | 0 | n/a |
| 48 | "Catch2 doctest unit testing C++" --search reddit,hackernews,github --emit json --quick | 0 | n/a |

**webclaw** (38 calls)

| seq | Query (exact) | rc | HTTP |
|---|---|---|---|
| 54 | https://jonastoth.github.io/posts/rtest_library/ | 0 | n/a |
| 55 | https://www.boost.org/doc/libs/latest/libs/hash2/doc/html/hash2.html | 0 | n/a |
| 57 | https://lists.boost.org/archives/list/boost@lists.boost.org/message/QBPJPEEIEYY2BO7C6IJ6ZXV2LGSZG62S/ | 0 | n/a |
| 58 | https://blog.infotraining.pl/hashing-in-cpp-26 | 0 | n/a |
| 60 | https://blog.infotraining.pl/annotations-for-cpp-26-hashing | 0 | n/a |
| 61 | https://chico.dev/Mirror-Hash/ | 0 | n/a |
| 63 | https://www.open-std.org/JTC1/sc22/WG21/docs/papers/2014/n3980.html | 0 | n/a |
| 64 | https://xxhash.com/ | 0 | n/a |
| 66 | https://rurban.github.io/smhasher/doc/table.html | 0 | n/a |
| 67 | https://notonbluray.com/blog/benchmarking-aes-256-sha256-and-crc-64-on-apple-silicon/ | 0 | n/a |
| 69 | https://picklog.cc/blog/md5-vs-sha256-speed | 0 | n/a |
| 70 | https://eclecticlight.co/2025/07/23/intel-macs-can-be-much-slower-computing-sha-256-hashes/ | 0 | n/a |
| 72 | https://news.ycombinator.com/item?id=43981971 | 0 | n/a |
| 73 | https://martin.ankerl.com/2026/09/04/unordered-dense-four-buckets-at-a-time/ | 0 | n/a |
| 74 | https://jacksonallan.github.io/c_cpp_hash_tables_benchmark/ | 0 | n/a |
| 76 | https://stephenberry.github.io/glaze/networking/asio-setup/ | 0 | n/a |
| 77 | https://stephenberry.github.io/glaze/networking/http-server/ | 0 | n/a |
| 79 | https://stephenberry.github.io/glaze/networking/http-client/ | 0 | n/a |
| 80 | https://stephenberry.github.io/glaze/networking/rest-registry/ | 0 | n/a |
| 81 | https://stephenberry.github.io/glaze/networking/websocket-client/ | 0 | n/a |
| 83 | https://stephenberry.github.io/glaze/networking/tls-support/ | 0 | n/a |
| 84 | https://stephenberry.github.io/glaze/networking/advanced-networking/ | 0 | n/a |
| 85 | https://stephenberry.github.io/glaze/rpc/json-rpc/ | 0 | n/a |
| 87 | https://stephenberry.github.io/glaze/rpc/repe-rpc/ | 0 | n/a |
| 88 | https://stephenberry.github.io/glaze/p2996-reflection/ | 0 | n/a |
| 89 | https://github.com/catchorg/Catch2/blob/devel/docs/cmake-integration.md | 1 | n/a |
| 90 | https://github.com/doctest/doctest/blob/master/doc/markdown/benchmarks.md | 0 | n/a |
| 92 | https://fekir.info/post/compile-time-test-suite/ | 0 | n/a |
| 93 | https://www.accu.org/journals/overload/34/193/decock/ | 0 | n/a |
| 94 | https://github.com/google/googletest/discussions/4916 | 0 | n/a |
| 95 | https://github.com/stephenberry/glaze/discussions/1653 | 0 | n/a |
| 96 | https://boost-ext.github.io/ut/cppcon-2021/ | 1 | n/a |
| 184 | https://lists.boost.org/archives/list/boost@lists.boost.org/thread/DDEET7XC5UYAVMG7YHD6UVT3VYF4VKEV/ | 0 | n/a |
| 185 | https://lists.boost.org/archives/list/boost@lists.boost.org/thread/JBII2DKKKEEELHBECHQB7RGZRWQJDOHL/ | 0 | n/a |
| 186 | https://www.cppal-dev.boost.cppalliance.org/boost-development/ | 0 | n/a |
| 187 | https://www.reddit.com/r/cpp/comments/1hj666i/hash2_accepted_in_boost/ | 0 | n/a |
| 192 | https://en.cppreference.com/w/cpp/utility/program/exit | 0 | n/a |
| 193 | https://en.cppreference.com/w/c/program/exit | 0 | n/a |

## 2. Results from each (hits, top results, used)

Top three results shown (all five are in `queries.jsonl`); "used" means cited in the verdict or sections 6 to 12, directly or through a stage-2 row it seeded.


**exa**

| seq | Hits | Top results | Used |
|---|---|---|---|
| 1 | 10 | [boost] [hash2] Review Report - Boost - lists.boost.org <https://lists.boost.org/archives/list/boost@lists.boost.org/message/QBPJPEEIEYY2BO7C6IJ6ZXV2LGSZG62S/>; Re: [boost] [hash2] My Review - Boost - lists.boost.org <https://lists.boost.org/archives/list/boost@lists.boost.org/thread/WFKRAARTXAE2QJLTNC45H3YANVBF3MHS/>; Hash2: An Extensible Hashing Framework <https://www.boost.org/doc/libs/latest/libs/hash2/doc/html/hash2.html> | yes |
| 2 | 10 | Hash2: An Extensible Hashing Framework <https://www.boost.org/doc/libs/latest/libs/hash2/doc/html/hash2.html>; Hash2: An Extensible Hashing Framework <https://www.boost.org/libs/hash2/>; Boost.Hash2 (1.92.0) <https://www.boost.org/library/latest/hash2/> | yes |
| 3 | 10 | FranciscoThiesen/mirror_hash <https://github.com/FranciscoThiesen/mirror_hash>; std::hash Boilerplate Is Dead - Francisco Geiman Thiesen - P... <https://chico.dev/Mirror-Hash/>; Hashing in C++26 <https://blog.infotraining.pl/hashing-in-cpp-26> | yes |
| 4 | 10 | hash_append.h <https://github.com/HowardHinnant/hash_append/blob/master/hash_append.h>; std-discussion: What happened to N3980 ("Types Don't Know #"... <https://lists.isocpp.org/std-discussion/2020/03/0482.php>; Reflection for C++26 <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2996r6.html> | yes |
| 5 | 10 | Nicoshev/rapidhash <https://github.com/Nicoshev/rapidhash>; Performance Benchmarks / Nicoshev/rapidhash / DeepWiki <https://deepwiki.com/Nicoshev/rapidhash/4.2-performance-benchmarks>; rapidhash - Very fast, high quality, platform-independent <https://chromium.googlesource.com/chromium/src/+/HEAD/third_party/rapidhash/README.md> | yes |
| 6 | 10 | xxHash - extremely fast hash algorithm <https://xxhash.com/>; xxHash: xxHash <https://xxhash.com/doc/v0.8.3/>; Cyan4973/xxHash: Extremely fast non-cryptographic hash ... <https://github.com/cyan4973/xxhash> | yes |
| 7 | 10 | blake3 single thread is slower than sha256 on Apple silicon ... <https://github.com/BLAKE3-team/BLAKE3/issues/315>; NEON version is only 26% faster than portable on Raspberry P... <https://github.com/BLAKE3-team/BLAKE3/issues/310>; Bazel 8: switch to Blake3 as the default hash function #2201... <https://github.com/bazelbuild/bazel/discussions/22011> | yes |
| 8 | 10 | stormj-UH/sha256-armv8 <https://github.com/jonerikstorm/sha256-armv8>; Benchmarking AES-256, SHA256 and CRC-64 on Apple Silicon - N... <https://notonbluray.com/blog/benchmarking-aes-256-sha256-and-crc-64-on-apple-silicon/>; Darwin: Performance degradation with 3.0-alpha6 vs 1.1.1g · ... <https://github.com/openssl/openssl/issues/12607> | yes |
| 9 | 10 | Comprehensive C++ Hashmap Benchmarks 2022 <https://martin.ankerl.com/2022/08/27/hashmap-bench-01/>; Add ankerl::unordered_dense::hash to benchmarks · 4d9f7b8 · ... <https://github.com/boostorg/container_hash/commit/4d9f7b89311982de41f8c3792a170f45bf2787b7>; unordered_dense/doc/usage.md at main · martinus/unordered_de... <https://www.webkkk.net/martinus/unordered_dense/blob/main/doc/usage.md> | yes |
| 10 | 10 |  <https://rurban.github.io/smhasher/doc/table.html>; rurban/smhasher <https://github.com/rurban/smhasher/>; SMhasher / smhasher <http://rurban.github.io/smhasher/> | yes |
| 11 | 10 | Using standard boost-ext/ut instead of the fork · stephenber... <https://github.com/stephenberry/glaze/discussions/1653>; boost-ext/ut <https://github.com/boost-ext/ut>; tests/CMakeLists.txt at main · stephenberry/glaze <https://github.com/stephenberry/glaze/blob/main/tests/CMakeLists.txt> | yes |
| 12 | 10 | example/benchmark.cpp <https://github.com/boost-ext/ut/blob/master/example/benchmark.cpp>; boost-ext/ut <https://github.com/boost-ext/ut>; Implementing a Macro-free Unit Testing Framework ... <https://boost-ext.github.io/ut/cppcon-2021/> | yes |
| 13 | 10 | v3.16.0 <https://github.com/catchorg/Catch2/releases/tag/v3.16.0>; catchorg/Catch2: v3.16.0 / Zenodo <https://zenodo.org/records/22092475>; catchorg/Catch2 v3.16.0 on GitHub <https://newreleases.io/project/github/catchorg/Catch2/release/v3.16.0> | yes |
| 14 | 10 | snitch-org/snitch <https://github.com/snitch-org/snitch>; README.md at main · snitch-org/snitch <https://github.com/snitch-org/snitch/blob/main/README.md>; 'CONSTEVAL_*' checks for non-decomposable expressions are no... <https://github.com/snitch-org/snitch/issues/145> | yes |
| 15 | 10 | rtest - A C++-26 reflection based testing library <https://jonastoth.github.io/posts/rtest_library/>; philsquared/Catch23 <https://github.com/philsquared/Catch23>; NeilJustice/ZenUnitAndMetalMock <https://github.com/NeilJustice/ZenUnit> | yes |
| 16 | 10 | rtest - A C++-26 reflection based testing library <https://jonastoth.github.io/posts/rtest_library/>; LaurieWired/CallMeMaybe <https://github.com/LaurieWired/CallMeMaybe>; Ricci-curvature/reflecting-cpp26 <https://github.com/Ricci-curvature/reflecting-cpp26> | yes |
| 17 | 10 | cpp-testing/ut-benchmark <https://github.com/cpp-testing/ut-benchmark/>; doc/markdown/benchmarks.md <https://github.com/doctest/doctest/blob/master/doc/markdown/benchmarks.md>; doctest - the Lightest C++ Unit Testing Framewor - ACCU <https://accu.org/journals/overload/25/137/kirilov_2343/> | yes |
| 18 | 10 | googletest/include/gtest/gtest-printers.h <https://github.com/google/googletest/blob/6ec14dfd/googletest/include/gtest/gtest-printers.h>; Reflection for C++26 <https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p2996r12.html>; Value Printing / google/googletest / DeepWiki <https://deepwiki.com/google/googletest/2.7-value-printing> | yes |
| 19 | 10 | jan-moeller/bugspray <https://github.com/jan-moeller/bugspray>; pw_compilation_testing - Pigweed <http://pigweed.dev/pw_compilation_testing/>; k3DW/k3tchup <https://github.com/k3DW/k3tchup> | yes |
| 20 | 10 | GitHub - MiddleRaster/tdd20: a macro-free, module-only TDD/u... <https://github.laiyagushi.com/MiddleRaster/tdd20>; boost-ext/ut <https://github.com/boost-experimental/ut>; GuillaumeLaurin/Cest <https://github.com/GuillaumeLaurin/Cest> | yes |
| 21 | 10 | REST Registry - Glaze Documentation <https://stephenberry.github.io/glaze/networking/rest-registry/>; HTTP Server - Glaze Documentation <https://stephenberry.github.io/glaze/networking/http-server/>; Glaze HTTP/REST Support - Glaze Documentation <https://stephenberry.github.io/glaze/networking/http-rest-support/> | yes |
| 22 | 10 | WebSocket Client - Glaze Documentation <https://stephenberry.github.io/glaze/networking/websocket-client/>; Advanced Networking - Glaze Documentation <https://stephenberry.github.io/glaze/networking/advanced-networking/>; ASIO Setup for Glaze Networking - Glaze Documentation <https://stephenberry.github.io/glaze/networking/asio-setup/> | yes |
| 23 | 10 | JSON-RPC 2.0 Client/Server - Glaze Documentation <https://stephenberry.github.io/glaze/rpc/json-rpc/>; REPE RPC - Glaze Documentation <https://stephenberry.github.io/glaze/rpc/repe-rpc/>; REPE to JSON-RPC - Glaze Documentation <https://stephenberry.github.io/glaze/rpc/repe-jsonrpc-conversion/> | yes |
| 24 | 10 | ASIO Setup for Glaze Networking - Glaze Documentation <https://stephenberry.github.io/glaze/networking/asio-setup/>; TLS/SSL Support in Glaze HTTP Server - Glaze Documentation <https://stephenberry.github.io/glaze/networking/tls-support/>; cmake/glaze-asio.cmake <https://github.com/stephenberry/glaze/blob/main/cmake/glaze-asio.cmake> | yes |
| 25 | 10 | HTTP Client - Glaze Documentation <https://stephenberry.github.io/glaze/networking/http-client/>; Glaze HTTP/REST Support - Glaze Documentation <https://stephenberry.github.io/glaze/networking/http-rest-support/>; docs/networking/advanced-networking.md <https://github.com/stephenberry/glaze/blob/main/docs/networking/advanced-networking.md> | yes |
| 26 | 10 | guteksan/REST-CPP-benchmark <https://github.com/guteksan/REST-CPP-benchmark>; HTTP Comparison to Other Libraries <https://www.boost.org/doc/libs/latest/libs/beast/doc/html/beast/design_choices/http_comparison_to_other_librari.html>; Glaze HTTP/REST Support - Glaze Documentation <https://stephenberry.github.io/glaze/networking/http-rest-support/> | no |
| 27 | 10 | include/boost/hash2/hash_append_fwd.hpp <https://github.com/pdimov/hash2/blob/develop/include/boost/hash2/hash_append_fwd.hpp>; Boost mailing page: Re: Formal review request for Hash2 <https://listarchives.boost.org/Archives/boost/2024/12/258433.php>; Hash2: An Extensible Hashing Framework <https://www.boost.org/doc/libs/latest/libs/hash2/doc/html/hash2.html> | yes |
| 28 | 10 | Update summary results for a5hash changes (71e3ee94) · Commi... <https://gitlab.com/fwojcik/smhasher3/-/commit/71e3ee94b67eb05e9ef7401960b6de18900ff010>; doc/komihash.txt <https://github.com/rurban/smhasher/blob/master/doc/komihash.txt>; README.md at main · avaneev/a5hash <https://github.com/avaneev/a5hash/blob/main/README.md> | yes |
| 29 | 10 | vexingcodes/ctsha <https://github.com/vexingcodes/ctsha>; hanickadot/cthash <https://github.com/hanickadot/cthash/>; aguinet/sha256_literal: A C++14 constexpr implementation ... <https://github.com/aguinet/sha256_literal> | no |
| 30 | 10 | catch_discover_tests with ASan results in errors running tes... <https://github.com/catchorg/Catch2/issues/2507>; extras/Catch.cmake at devel · catchorg/Catch2 <https://github.com/catchorg/Catch2/blob/devel/extras/Catch.cmake>; extras/CatchAddTests.cmake at devel · catchorg/Catch2 <https://github.com/catchorg/Catch2/blob/devel/extras/CatchAddTests.cmake> | yes |
| 31 | 10 | docs/networking/http-server.md <https://github.com/stephenberry/glaze/blob/main/docs/networking/http-server.md>; Glaze HTTP/REST Support - Glaze Documentation <https://stephenberry.github.io/glaze/networking/http-rest-support/>; Advanced Networking - Glaze Documentation <https://stephenberry.github.io/glaze/networking/advanced-networking/> | yes |
| 32 | 10 | C++ Reflection: a Universal Printer <https://www.accu.org/journals/overload/34/193/decock/>; tt_stl/tests/test_reflection.cpp <https://github.com/tenstorrent/tt-metal/blob/02df4aae/tt_stl/tests/test_reflection.cpp>; test-reflection-cpp.cpp <https://github.com/contour-terminal/reflection-cpp/blob/master/test-reflection-cpp.cpp> | no |
| 180 | 10 | Boost C++ Homepage <https://www.boost.org/>; Boost Calendar <https://www.cppal-dev.boost.cppalliance.org/boost-development/>; Latest Release (1.92.0) <https://www.boost.org/releases/> | yes |
| 181 | 10 | C++26 Reflection in Boost - Boost - lists.boost.org <https://lists.boost.org/archives/list/boost@lists.boost.org/thread/DDEET7XC5UYAVMG7YHD6UVT3VYF4VKEV/>; Describe: A C++14 Reflection Library <https://www.boost.org/doc/libs/latest/libs/describe/doc/html/describe.html>; Boost.Describe (1.92.0) <https://www.boost.org/library/latest/describe/> | yes |
| 182 | 10 | Adapt boost::asio to stdexec · Pull Request #1501 · NVIDIA/s... <https://github.com/NVIDIA/stdexec/pull/1501>; 40 · Boost.Beast HTTP Server - Building a Network Service wi... <https://hollykbuck.github.io/exec/tutorials/40-Boost-Beast-HTTP-Server/>; include/exec/asio/use_sender.hpp at 4e2cee2e · NVIDIA/stdexe... <https://github.com/NVIDIA/stdexec/blob/4e2cee2e/include/exec/asio/use_sender.hpp> | yes |
| 183 | 10 | catch_discover_tests with ASan results in errors running tes... <https://github.com/catchorg/Catch2/issues/2507>; Allow the Catch2 library to be compiled with address sanitiz... <https://github.com/catchorg/Catch2/issues/2866>; AddressSanitizer <https://clang.llvm.org/docs/AddressSanitizer.html> | yes |

**serper**

| seq | Hits | Top results | Used |
|---|---|---|---|
| 39 | 10 | boost-ext/ut: C++20 μ(micro)/Unit Testing framework <https://github.com/boost-ext/ut>; [UT] C++20 macro free testing framework / version 2.0.0 ... <https://www.reddit.com/r/cpp/comments/170an89/ut_c20_macro_free_testing_framework_version_200/>; UT: Header-Only C++20 Unit Testing Framework <https://dev.co/testing/open-source/ut> | no |
| 40 | 10 | Hash2 accepted in Boost : r/cpp <https://www.reddit.com/r/cpp/comments/1hj666i/hash2_accepted_in_boost/>; Reflection for C++26 <https://isocpp.org/files/papers/P2996R4.html>; Reflection in C++26: the renaissance of C++ <https://www.youtube.com/watch?v=vRda0mGYg_A> | no |
| 41 | 10 | Glaze HTTP/REST Support <https://stephenberry.github.io/glaze/networking/http-rest-support/>; What is the go-to way/solution to build and consume cloud ..... <https://www.reddit.com/r/cpp/comments/1nxzqjk/what_is_the_goto_waysolution_to_build_and_consume/>; WebSocket <https://www.boost.org/doc/libs/latest/libs/beast/doc/html/beast/using_websocket.html> | yes |
| 42 | 10 | Reflection for C++26 <https://isocpp.org/files/papers/P2996R13.html>; C++26 Reflection: my experience and impressions : r/cpp <https://www.reddit.com/r/cpp/comments/1pc53b2/c26_reflection_my_experience_and_impressions/>; C++ Weekly - Ep 504 - Practical Reflection in C++26 <https://www.youtube.com/watch?v=Mg_TBYppQwU> | no |
| 43 | 10 | catchorg/Catch2: A modern, C++-native, test framework for ..... <https://github.com/catchorg/catch2>; Download Catch2 - Modern C++ Unit Testing Framework <https://catch2.org/>; List of unit testing frameworks <https://en.wikipedia.org/wiki/List_of_unit_testing_frameworks> | yes |
| 44 | 10 | Intel Macs can be much slower computing SHA-256 hashes <https://eclecticlight.co/2025/07/23/intel-macs-can-be-much-slower-computing-sha-256-hashes/>; Adding more assembly to AARCH64 (macOS) #14645 <https://github.com/openzfs/zfs/discussions/14645>; SHA256 / Apple Developer Documentation <https://developer.apple.com/documentation/cryptokit/sha256> | no |
| 45 | 10 | BLAKE3 vs SHA-256: Up to 27x Faster, No FIPS [2026] <https://shattered.io/blake3-vs-sha256-2026/>; BLAKE3 slower than SHA-256 for small inputs - Research <https://forum.solana.com/t/blake3-slower-than-sha-256-for-small-inputs/829>; Performance Evaluation of Hashing Algorithms on ... <https://arxiv.org/html/2407.08284v1> | no |
| 46 | 10 | snitch-org/snitch: Lightweight C++20 testing framework. <https://github.com/snitch-org/snitch>; snitch v1.0 -- A lightweight C++20 testing framework : r/cpp <https://www.reddit.com/r/cpp/comments/10dac2x/snitch_v10_a_lightweight_c20_testing_framework/>; snitch - vcpkg package <https://vcpkg.io/en/package/snitch.html> | yes |

**context7**

| seq | Hits | Top results | Used |
|---|---|---|---|
| 33 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; error 'Monthly quota reached' | no |
| 34 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; error 'Monthly quota reached' | no |
| 35 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; error 'Monthly quota reached' | no |
| 36 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; error 'Monthly quota reached' | no |

**firecrawl**

| seq | Hits | Top results | Used |
|---|---|---|---|
| 37 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; Insufficient credits | no |
| 38 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; Insufficient credits | no |

**last30days**

| seq | Hits | Top results | Used |
|---|---|---|---|
| 47 | 0 | backfilled from scratch files after D137 arrived; logged_at is backfill time; grounding error, LLM rerank HTTP 503, planner ran 1 of 3 subqu... | no |
| 48 | 4 | Would Unit Testing be a net benefit when your code relies he... <https://www.reddit.com/r/AskProgramming/comments/1wvzdtx/would_unit_testing_be_a_net_benefit_when_your/>; Show HN: MCPJam - the first testing & evaluations platform f... <https://www.mcpjam.com>; How do you write unit test cases in python ? <https://www.reddit.com/r/learnpython/comments/1wh8cs5/how_do_you_write_unit_test_cases_in_python/> | no |

**webclaw**

| seq | Hits | Top results | Used |
|---|---|---|---|
| 54 | 1 | pages/rtest-blog.md <https://jonastoth.github.io/posts/rtest_library/> | yes |
| 55 | 1 | pages/hash2-docs.md <https://www.boost.org/doc/libs/latest/libs/hash2/doc/html/hash2.html> | no |
| 57 | 1 | pages/hash2-review-report.md <https://lists.boost.org/archives/list/boost@lists.boost.org/message/QBPJPEEIEYY2BO7C6IJ6ZXV2LGSZG62S/> | yes |
| 58 | 1 | pages/infotraining-hashing-cpp26.md <https://blog.infotraining.pl/hashing-in-cpp-26> | yes |
| 60 | 1 | pages/infotraining-annotations-hashing.md <https://blog.infotraining.pl/annotations-for-cpp-26-hashing> | yes |
| 61 | 1 | pages/mirror-hash-blog.md <https://chico.dev/Mirror-Hash/> | no |
| 63 | 1 | pages/n3980.md <https://www.open-std.org/JTC1/sc22/WG21/docs/papers/2014/n3980.html> | no |
| 64 | 1 | pages/xxhash-site.md <https://xxhash.com/> | yes |
| 66 | 1 | pages/smhasher-table.md <https://rurban.github.io/smhasher/doc/table.html> | yes |
| 67 | 1 | pages/notonbluray-apple-sha256.md <https://notonbluray.com/blog/benchmarking-aes-256-sha256-and-crc-64-on-apple-silicon/> | yes |
| 69 | 1 | pages/picklog-md5-sha256-m4.md <https://picklog.cc/blog/md5-vs-sha256-speed> | yes |
| 70 | 1 | pages/eclecticlight-sha256-intel.md <https://eclecticlight.co/2025/07/23/intel-macs-can-be-much-slower-computing-sha-256-hashes/> | no |
| 72 | 1 | pages/hn-rapidhash-71gbs.md <https://news.ycombinator.com/item?id=43981971> | no |
| 73 | 1 | pages/ankerl-four-buckets.md <https://martin.ankerl.com/2026/09/04/unordered-dense-four-buckets-at-a-time/> | yes |
| 74 | 1 | pages/jacksonallan-hashtables.md <https://jacksonallan.github.io/c_cpp_hash_tables_benchmark/> | no |
| 76 | 1 | pages/glaze-asio-setup.md <https://stephenberry.github.io/glaze/networking/asio-setup/> | no |
| 77 | 1 | pages/glaze-http-server.md <https://stephenberry.github.io/glaze/networking/http-server/> | no |
| 79 | 1 | pages/glaze-http-client.md <https://stephenberry.github.io/glaze/networking/http-client/> | no |
| 80 | 1 | pages/glaze-rest-registry.md <https://stephenberry.github.io/glaze/networking/rest-registry/> | no |
| 81 | 1 | pages/glaze-websocket-client.md <https://stephenberry.github.io/glaze/networking/websocket-client/> | no |
| 83 | 1 | pages/glaze-tls.md <https://stephenberry.github.io/glaze/networking/tls-support/> | no |
| 84 | 1 | pages/glaze-advanced-networking.md <https://stephenberry.github.io/glaze/networking/advanced-networking/> | no |
| 85 | 1 | pages/glaze-json-rpc.md <https://stephenberry.github.io/glaze/rpc/json-rpc/> | no |
| 87 | 1 | pages/glaze-repe-rpc.md <https://stephenberry.github.io/glaze/rpc/repe-rpc/> | no |
| 88 | 1 | pages/glaze-p2996.md <https://stephenberry.github.io/glaze/p2996-reflection/> | no |
| 89 | 0 | pages/catch2-cmake-integration.md <https://github.com/catchorg/Catch2/blob/devel/docs/cmake-integration.md> | no |
| 90 | 1 | pages/doctest-benchmarks.md <https://github.com/doctest/doctest/blob/master/doc/markdown/benchmarks.md> | yes |
| 92 | 1 | pages/fekir-compile-time-tests.md <https://fekir.info/post/compile-time-test-suite/> | no |
| 93 | 1 | pages/accu-universal-printer.md <https://www.accu.org/journals/overload/34/193/decock/> | no |
| 94 | 1 | pages/googletest-modules-disc4916.md <https://github.com/google/googletest/discussions/4916> | no |
| 95 | 1 | pages/glaze-disc1653-ut.md <https://github.com/stephenberry/glaze/discussions/1653> | no |
| 96 | 0 | pages/boost-ut-cppcon2021.md <https://boost-ext.github.io/ut/cppcon-2021/> | no |
| 184 | 1 | pages/boost-cxx26-reflection-thread.md <https://lists.boost.org/archives/list/boost@lists.boost.org/thread/DDEET7XC5UYAVMG7YHD6UVT3VYF4VKEV/> | no |
| 185 | 1 | pages/boost-193-open-for-merging.md <https://lists.boost.org/archives/list/boost@lists.boost.org/thread/JBII2DKKKEEELHBECHQB7RGZRWQJDOHL/> | yes |
| 186 | 1 | pages/boost-calendar.md <https://www.cppal-dev.boost.cppalliance.org/boost-development/> | no |
| 187 | 1 | pages/reddit-hash2-accepted.md <https://www.reddit.com/r/cpp/comments/1hj666i/hash2_accepted_in_boost/> | no |
| 192 | 1 | pages/cppreference-std-exit.md <https://en.cppreference.com/w/cpp/utility/program/exit> | no |
| 193 | 1 | pages/cppreference-c-exit.md <https://en.cppreference.com/w/c/program/exit> | yes |

## 3. GitHub issues, PRs and discussions searched (stage 2)

`Seed` is the stage-1 row whose result named the search, recorded when the search was chosen. Rows with seed `n/r` were logged before D137 arrived and their seeds were not recorded at choice time (they were chosen from Exa rows 1 to 32 and the repositories the task named); they are not reconstructed.

| seq | Provider | Query | Hits | Seed | Used |
|---|---|---|---|---|---|
| 49 | git-clone | https://github.com/boostorg/hash2 | 1 | n/r | yes |
| 50 | git-clone | https://github.com/stephenberry/ut | 1 | n/r | yes |
| 51 | git-clone | https://github.com/boost-ext/ut | 1 | n/r | no |
| 52 | git-clone | https://github.com/qlibs/ut | 1 | n/r | yes |
| 53 | git-clone | https://github.com/catchorg/Catch2 | 1 | n/r | yes |
| 56 | git-clone | https://github.com/doctest/doctest | 1 | n/r | no |
| 59 | git-clone | https://github.com/snitch-org/snitch | 1 | n/r | yes |
| 62 | git-clone | https://github.com/google/googletest | 1 | n/r | yes |
| 65 | git-clone | https://github.com/philsquared/Catch23 | 1 | n/r | yes |
| 68 | git-clone | https://github.com/stephenberry/glaze | 1 | n/r | yes |
| 71 | git-clone | https://github.com/BLAKE3-team/BLAKE3 | 1 | n/r | yes |
| 75 | git-clone | https://github.com/Cyan4973/xxHash | 1 | n/r | yes |
| 78 | git-clone | https://github.com/Nicoshev/rapidhash | 1 | n/r | yes |
| 82 | git-clone | https://github.com/martinus/unordered_dense | 1 | n/r | yes |
| 86 | git-clone | https://github.com/FranciscoThiesen/mirror_hash | 1 | n/r | yes |
| 91 | git-clone | https://github.com/chriskohlhoff/asio | 1 | n/r | no |
| 97 | git-clone | https://github.com/cpp-testing/ut-benchmark | 1 | n/r | yes |
| 98 | git-clone | https://github.com/avaneev/komihash | 1 | n/r | no |
| 99 | git-clone | https://github.com/boostorg/container_hash | 1 | n/r | no |
| 100 | git-clone | https://codeberg.org/JonasToth/rtest | 1 | n/r | yes |
| 101 | gh-api-repo | gh api repos/stephenberry/ut | 1 | n/r | yes |
| 102 | gh-api-repo | gh api repos/openalgz/ut | 1 | n/r | yes |
| 103 | gh-api-repo | gh api repos/boost-ext/ut | 1 | n/r | no |
| 104 | gh-api-repo | gh api repos/boost-ext/ut2 | 1 | n/r | yes |
| 105 | gh-api-repo | gh api repos/qlibs/ut | 1 | n/r | no |
| 106 | gh-api-repo | gh api repos/philsquared/Catch23 | 1 | n/r | no |
| 107 | gh-api-repo | gh api repos/FranciscoThiesen/mirror_hash | 1 | n/r | yes |
| 108 | gh-api-repo | gh api repos/JonasToth/rtest | 0 | n/r | yes |
| 109 | gh-api-repo | gh api repos/boostorg/hash2 | 1 | n/r | no |
| 110 | gh-api-repo | gh api repos/snitch-org/snitch | 1 | n/r | no |
| 111 | gh-api-repo | gh api repos/Nicoshev/rapidhash | 1 | n/r | no |
| 112 | gh-api-repo | gh api repos/martinus/unordered_dense | 1 | n/r | no |
| 113 | gh-api-repo | gh api repos/Cyan4973/xxHash | 1 | n/r | no |
| 114 | gh-api-repo | gh api repos/BLAKE3-team/BLAKE3 | 1 | n/r | no |
| 115 | gh-api-repo | gh api repos/catchorg/Catch2 | 1 | n/r | no |
| 116 | gh-api-repo | gh api repos/doctest/doctest | 1 | n/r | no |
| 117 | gh-api-repo | gh api repos/google/googletest | 1 | n/r | no |
| 118 | gh-api-repo | gh api repos/stephenberry/glaze | 1 | n/r | no |
| 119 | gh-api-repo | gh api repos/chriskohlhoff/asio | 1 | n/r | no |
| 120 | gh-issue-search | gh search issues "performance" --repo boostorg/hash2 --include-prs --limit 15 | 0 | 2 | no |
| 121 | gh-issue-search | gh search issues "OpenSSL" --repo boostorg/hash2 --include-prs --limit 15 | 0 | 2 | no |
| 122 | gh-issue-search | gh search issues "reflection" --repo boostorg/hash2 --include-prs --limit 15 | 0 | 27 | no |
| 123 | gh-issue-search | gh search issues "describe" --repo boostorg/hash2 --include-prs --limit 15 | 1 | 27 | yes |
| 124 | gh-issue-search | gh search issues "SIMD" --repo boostorg/hash2 --include-prs --limit 15 | 0 | 2 | no |
| 125 | gh-issue-search | gh issue list --repo boostorg/hash2 --state all --limit 80 | 6 | 1 | yes |
| 126 | gh-pr-search | gh pr list --repo boostorg/hash2 --state all --limit 80 | 41 | 1 | yes |
| 127 | gh-pr-view | gh pr view 31 --repo boostorg/hash2 --comments | 1 | 126 | yes |
| 128 | gh-pr-view | gh pr view 34 --repo boostorg/hash2 --comments | 1 | 126 | no |
| 129 | gh-issue-view | gh issue view 30 --repo boostorg/hash2 --comments | 1 | 125 | no |
| 130 | gh-issue-view | gh issue view 315 --repo BLAKE3-team/BLAKE3 --comments | 1 | 7 | yes |
| 131 | gh-release-list | gh release list --repo martinus/unordered_dense --limit 8 | 8 | 9 | yes |
| 132 | gh-release-list | gh release list --repo Nicoshev/rapidhash --limit 8 | 5 | 5 | yes |
| 133 | gh-release-list | gh release list --repo Cyan4973/xxHash --limit 8 | 8 | 6 | yes |
| 134 | gh-release-list | gh release list --repo BLAKE3-team/BLAKE3 --limit 8 | 8 | 7 | yes |
| 135 | gh-release-list | gh release list --repo boostorg/hash2 --limit 8 | 0 | 2 | yes |
| 136 | gh-release-list | gh release list --repo stephenberry/ut --limit 8 | 8 | 11 | yes |
| 137 | gh-release-list | gh release list --repo boost-ext/ut --limit 8 | 8 | 12 | yes |
| 138 | gh-release-list | gh release list --repo catchorg/Catch2 --limit 8 | 8 | 13 | yes |
| 139 | gh-release-list | gh release list --repo doctest/doctest --limit 8 | 8 | 17 | yes |
| 140 | gh-release-list | gh release list --repo snitch-org/snitch --limit 8 | 8 | 14 | yes |
| 141 | gh-release-list | gh release list --repo google/googletest --limit 8 | 8 | 18 | yes |
| 142 | gh-release-list | gh release list --repo stephenberry/glaze --limit 8 | 8 | 21 | yes |
| 143 | gh-release-list | gh release list --repo chriskohlhoff/asio --limit 8 | 0 | 24 | yes |
| 144 | gh-release-list | gh release list --repo philsquared/Catch23 --limit 8 | 0 | 15 | yes |
| 145 | gh-release-list | gh release list --repo qlibs/ut --limit 8 | 8 | 17 | yes |
| 146 | gh-graphql-discussion | gh api graphql repository(stephenberry/glaze).discussion(number:1653) | 1 | 11 | yes |
| 147 | gh-issue-view | gh issue view 618 --repo boost-ext/ut --comments | 1 | 11 | yes |
| 148 | gh-issue-view | gh issue view 1168 --repo doctest/doctest --comments | 1 | 17 | yes |
| 149 | gh-graphql-discussion | gh api graphql repository(google/googletest).discussion(number:4916) | 1 | 20 | yes |
| 150 | gh-issue-search | gh search issues "gcc" --repo stephenberry/ut --include-prs --limit 15 | 3 | 11 | yes |
| 151 | gh-issue-search | gh search issues "clang" --repo stephenberry/ut --include-prs --limit 15 | 2 | 11 | yes |
| 152 | gh-issue-search | gh search issues "thread" --repo stephenberry/ut --include-prs --limit 15 | 2 | 11 | yes |
| 153 | gh-issue-search | gh search issues "module" --repo stephenberry/ut --include-prs --limit 15 | 7 | 11 | yes |
| 154 | gh-issue-search | gh search issues "gcc 16" --repo snitch-org/snitch --include-prs --limit 15 | 1 | 14 | yes |
| 155 | gh-issue-search | gh search issues "clang 21" --repo snitch-org/snitch --include-prs --limit 15 | 1 | 14 | yes |
| 156 | gh-issue-search | gh search issues "C++26" --repo snitch-org/snitch --include-prs --limit 15 | 4 | 14 | yes |
| 157 | gh-issue-search | gh search issues "libc++" --repo snitch-org/snitch --include-prs --limit 15 | 8 | 14 | yes |
| 158 | gh-issue-view | gh issue view 14 --repo stephenberry/ut --comments | 1 | 11 | yes |
| 159 | gh-pr-view | gh pr view 6 --repo stephenberry/ut --comments | 1 | 11 | yes |
| 160 | gh-issue-search | gh search issues "http_server crash" --repo stephenberry/glaze --include-prs --limit 15 | 0 | 21 | no |
| 161 | gh-issue-search | gh search issues "websocket" --repo stephenberry/glaze --include-prs --limit 15 | 15 | 22 | yes |
| 162 | gh-issue-search | gh search issues "boost asio" --repo stephenberry/glaze --include-prs --limit 15 | 15 | 24 | yes |
| 163 | gh-issue-search | gh search issues "ssl https" --repo stephenberry/glaze --include-prs --limit 15 | 1 | 24 | yes |
| 164 | gh-issue-search | gh search issues "http server production" --repo stephenberry/glaze --include-prs --limit 15 | 0 | 31 | no |
| 165 | gh-issue-view | gh issue view 2409 --repo stephenberry/glaze --comments | 1 | 22 | yes |
| 166 | gh-pr-view | gh pr view 2411 --repo stephenberry/glaze --comments | 1 | 22 | yes |
| 167 | gh-issue-view | gh issue view 2366 --repo stephenberry/glaze --comments | 1 | 31 | yes |
| 168 | gh-issue-view | gh issue view 2599 --repo stephenberry/glaze --comments | 1 | 24 | yes |
| 169 | gh-issue-view | gh issue view 2470 --repo stephenberry/glaze --comments | 1 | 24 | yes |
| 170 | gh-pr-view | gh pr view 2873 --repo stephenberry/glaze --comments | 1 | 24 | yes |
| 171 | gh-commit-search | gh api search/commits q='reflection repo:boostorg/hash2' | 2 | 27 | yes |
| 172 | gh-commit-search | gh api search/commits q='freflection repo:boostorg/hash2' | 1 | 27 | yes |
| 173 | gh-commit-search | gh api search/commits q='reflection repo:boostorg/container_hash' | 1 | 27 | yes |
| 174 | gh-commit-search | gh api search/commits q='reflection repo:boostorg/describe' | 4 | 27 | yes |
| 175 | git-clone | https://github.com/boostorg/describe | 1 | 27 | yes |
| 176 | gh-issue-view | gh issue view 2507 --repo catchorg/Catch2 --comments | 1 | 30 | yes |
| 177 | gh-issue-search | gh search issues "gcc 16" --repo boost-ext/ut --include-prs --limit 15 | 2 | 12 | yes |
| 178 | gh-issue-search | gh search issues "clang 21" --repo boost-ext/ut --include-prs --limit 15 | 2 | 12 | yes |
| 179 | gh-issue-search | gh search issues "C++26" --repo boost-ext/ut --include-prs --limit 15 | 5 | 12 | yes |
| 188 | gh-issue-search | gh search issues "REFLECTION26 networking" --repo stephenberry/glaze --include-prs --limit 15 | 0 | 21 | yes |
| 189 | gh-issue-search | gh search issues "p2996 http" --repo stephenberry/glaze --include-prs --limit 15 | 0 | 21 | yes |
| 190 | gh-issue-search | gh search issues "registry reflection member functions" --repo stephenberry/glaze --include-prs --limit 15 | 0 | 21 | yes |
| 191 | gh-issue-search | gh search issues "reflection" --repo catchorg/Catch2 --include-prs --limit 15 | 2 | 13 | no |

## 4. githubkit saved searches (reproduced read-only with controls) and proposed rows

The catalogue `dev/saved-searches.toml` holds three rows, all for `openai/codex` (`codex-schema`, `codex-config-examples`, `codex-hook-examples`); none concerns these libraries, so they were not re-run (R13 reproduced the route and its controls earlier today). `dev/collect_saved_search.py` only queries `/search/code` (`:179`) and identifies each hit as `repo:path:blob-sha` (`dev/github_search_one_page.py:74-81`), so a row that matches a version or feature file reports a new item whenever that file changes; that is how the rows below track new releases. `research:collect` writes into a tracked path another lane owns, so each row was reproduced read-only with `gh api -X GET search/code` into `OFF/receipts/saved/`, each with a control query, 7 s apart.

| seq | Row id | Kind | Query | rc | total_count | First paths |
|---|---|---|---|---|---|---|
| 194 | boost-describe-reflection | row | gh api -X GET search/code -f q='BOOST_DESCRIBE_HAS_REFLECTION repo:boostorg/describe' -F per_page=5 | 0 | 27 | include/boost/describe/detail/config.hpp, include/boost/describe/detail/rf_enum.hpp, include/boost/describe/detail/rf_bases.hpp |
| 195 | boost-describe-reflection | control | gh api -X GET search/code -f q='README repo:boostorg/describe' -F per_page=5 | 0 | 1 | .gitattributes |
| 196 | boost-hash2-reflection-ci | row | gh api -X GET search/code -f q='freflection repo:boostorg/hash2' -F per_page=5 | 0 | 1 | .github/workflows/ci.yml |
| 197 | boost-hash2-reflection-ci | control | gh api -X GET search/code -f q='README repo:boostorg/hash2' -F per_page=5 | 0 | 1 | .gitattributes |
| 198 | ut-header | row | gh api -X GET search/code -f q='"namespace ut" filename:ut.hpp repo:stephenberry/ut' -F per_page=5 | 0 | 1 | include/ut/ut.hpp |
| 199 | ut-header | control | gh api -X GET search/code -f q='README repo:stephenberry/ut' -F per_page=5 | 0 | 0 | none |
| 200 | catch2-version-macros | row | gh api -X GET search/code -f q='CATCH_VERSION_MINOR repo:catchorg/Catch2' -F per_page=5 | 0 | 3 | docs/own-main.md, src/catch2/catch_version_macros.hpp, tools/scripts/releaseCommon.py |
| 201 | catch2-version-macros | control | gh api -X GET search/code -f q='README repo:catchorg/Catch2' -F per_page=5 | 0 | 32 | README.md, docs/own-main.md, docs/event-listeners.md |
| 202 | glaze-asio-backend | row | gh api -X GET search/code -f q='GLZ_USE_BOOST_ASIO repo:stephenberry/glaze' -F per_page=5 | 0 | 7 | cmake/glaze-asio.cmake, docs/networking/asio-setup.md, cmake/install-config.cmake.in |
| 203 | glaze-asio-backend | control | gh api -X GET search/code -f q='README repo:stephenberry/glaze' -F per_page=5 | 0 | 5 | README.md, util/glaze.spec, docs/custom-serialization.md |
| 204 | glaze-networking-tests-flag | row | gh api -X GET search/code -f q='glaze_BUILD_NETWORKING_TESTS repo:stephenberry/glaze' -F per_page=5 | 0 | 8 | tests/CMakeLists.txt, .github/workflows/armv7.yml, .github/workflows/disable-always-inline.yml |
| 205 | glaze-networking-tests-flag | control | gh api -X GET search/code -f q='README repo:stephenberry/glaze' -F per_page=5 | 0 | 5 | README.md, util/glaze.spec, docs/custom-serialization.md |
| 206 | ut-header | control (replacement for README, which returned 0) | gh api -X GET search/code -f q='cmake_minimum_required repo:stephenberry/ut' -F per_page=5 | 0 | 1 | CMakeLists.txt |

The README control for `stephenberry/ut` returned 0 (seq 199), so it cannot verify that row; `cmake_minimum_required` (seq 206) is the working control. Proposed rows (do not edit the file from this report):

```toml
[[search]]
id = "boost-describe-reflection"       # 27 hits; control 1 (README matched .gitattributes)
query = "BOOST_DESCRIBE_HAS_REFLECTION"
repo = "boostorg/describe"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "boost-hash2-reflection-ci"       # 1 hit (.github/workflows/ci.yml); control 1
query = "freflection"
repo = "boostorg/hash2"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "ut-header"                       # 1 hit (include/ut/ut.hpp); README control returned 0
query = "\"namespace ut\" filename:ut.hpp"
repo = "stephenberry/ut"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "cmake_minimum_required"
expected_min = 1

[[search]]
id = "catch2-version-macros"           # 3 hits incl. src/catch2/catch_version_macros.hpp; control 32
query = "CATCH_VERSION_MINOR"
repo = "catchorg/Catch2"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "glaze-asio-backend"              # 7 hits; control 5
query = "GLZ_USE_BOOST_ASIO"
repo = "stephenberry/glaze"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "glaze-networking-tests-flag"     # 8 hits (tests/CMakeLists.txt and workflows); control 5
query = "glaze_BUILD_NETWORKING_TESTS"
repo = "stephenberry/glaze"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

Release tags themselves (`gh release list`, rows 131 to 145) are a better release signal than code search, but the collector has no release route; a `kind = "releases"` extension would be a separate ticket. R8's `glaze-reflection26` and R13's `glaze-write-json-schema` rows already cover glaze's reflection backend and schema output.

## 5. Stage-2 searches run against the stage-1 results (seed-to-search map)

| Stage-1 row (seq, provider, query) | Stage-2 rows it seeded (seq: query) |
|---|---|
| 1, exa, Boost.Hash2 library review hash_append described classes | 125: gh issue list --repo boostorg/hash2 --state all --limit 80; 126: gh pr list --repo boostorg/hash2 --state all --limit 80 |
| 2, exa, boostorg hash2 SHA-256 BLAKE2 xxhash algorithms performance | 120: gh search issues "performance" --repo boostorg/hash2 --include-prs --l...; 121: gh search issues "OpenSSL" --repo boostorg/hash2 --include-prs --limit...; 124: gh search issues "SIMD" --repo boostorg/hash2 --include-prs --limit 15; 135: gh release list --repo boostorg/hash2 --limit 8 |
| 5, exa, rapidhash benchmark wyhash successor speed | 132: gh release list --repo Nicoshev/rapidhash --limit 8 |
| 6, exa, xxHash XXH3 benchmark Apple M1 M2 GB/s | 133: gh release list --repo Cyan4973/xxHash --limit 8 |
| 7, exa, BLAKE3 C library performance ARM NEON Apple silicon vs SHA-256 | 130: gh issue view 315 --repo BLAKE3-team/BLAKE3 --comments; 134: gh release list --repo BLAKE3-team/BLAKE3 --limit 8 |
| 9, exa, ankerl unordered_dense hash function wyhash benchmark | 131: gh release list --repo martinus/unordered_dense --limit 8 |
| 11, exa, stephenberry ut unit testing framework fork boost-ext ut | 136: gh release list --repo stephenberry/ut --limit 8; 146: gh api graphql repository(stephenberry/glaze).discussion(number:1653); 147: gh issue view 618 --repo boost-ext/ut --comments; 150: gh search issues "gcc" --repo stephenberry/ut --include-prs --limit 15; 151: gh search issues "clang" --repo stephenberry/ut --include-prs --limit ...; 152: gh search issues "thread" --repo stephenberry/ut --include-prs --limit...; 153: gh search issues "module" --repo stephenberry/ut --include-prs --limit...; 158: gh issue view 14 --repo stephenberry/ut --comments; 159: gh pr view 6 --repo stephenberry/ut --comments; 198: gh api -X GET search/code -f q='"namespace ut" filename:ut.hpp repo:st...; 199: gh api -X GET search/code -f q='README repo:stephenberry/ut' -F per_pa...; 206: gh api -X GET search/code -f q='cmake_minimum_required repo:stephenber... |
| 12, exa, boost-ext ut macro-free unit testing C++20 compile time benchmark | 137: gh release list --repo boost-ext/ut --limit 8; 177: gh search issues "gcc 16" --repo boost-ext/ut --include-prs --limit 15; 178: gh search issues "clang 21" --repo boost-ext/ut --include-prs --limit ...; 179: gh search issues "C++26" --repo boost-ext/ut --include-prs --limit 15 |
| 13, exa, Catch2 3.16 release notes | 138: gh release list --repo catchorg/Catch2 --limit 8; 191: gh search issues "reflection" --repo catchorg/Catch2 --include-prs --l...; 200: gh api -X GET search/code -f q='CATCH_VERSION_MINOR repo:catchorg/Catc...; 201: gh api -X GET search/code -f q='README repo:catchorg/Catch2' -F per_pa... |
| 14, exa, snitch C++20 testing framework constexpr compile time | 140: gh release list --repo snitch-org/snitch --limit 8; 154: gh search issues "gcc 16" --repo snitch-org/snitch --include-prs --lim...; 155: gh search issues "clang 21" --repo snitch-org/snitch --include-prs --l...; 156: gh search issues "C++26" --repo snitch-org/snitch --include-prs --limi...; 157: gh search issues "libc++" --repo snitch-org/snitch --include-prs --lim... |
| 15, exa, C++ unit testing framework 2025 2026 new C++23 C++26 | 144: gh release list --repo philsquared/Catch23 --limit 8 |
| 17, exa, doctest vs Catch2 vs ut compile time benchmark 2025 | 139: gh release list --repo doctest/doctest --limit 8; 145: gh release list --repo qlibs/ut --limit 8; 148: gh issue view 1168 --repo doctest/doctest --comments |
| 18, exa, GoogleTest C++26 reflection value printing | 141: gh release list --repo google/googletest --limit 8 |
| 20, exa, C++20 modules unit test framework import std | 149: gh api graphql repository(google/googletest).discussion(number:4916) |
| 21, exa, glaze HTTP server REST registry asio | 142: gh release list --repo stephenberry/glaze --limit 8; 160: gh search issues "http_server crash" --repo stephenberry/glaze --inclu...; 188: gh search issues "REFLECTION26 networking" --repo stephenberry/glaze -...; 189: gh search issues "p2996 http" --repo stephenberry/glaze --include-prs ...; 190: gh search issues "registry reflection member functions" --repo stephen...; 204: gh api -X GET search/code -f q='glaze_BUILD_NETWORKING_TESTS repo:step...; 205: gh api -X GET search/code -f q='README repo:stephenberry/glaze' -F per... |
| 22, exa, glaze websocket client server C++ | 161: gh search issues "websocket" --repo stephenberry/glaze --include-prs -...; 165: gh issue view 2409 --repo stephenberry/glaze --comments; 166: gh pr view 2411 --repo stephenberry/glaze --comments |
| 24, exa, glaze networking standalone asio boost asio TLS openssl | 143: gh release list --repo chriskohlhoff/asio --limit 8; 162: gh search issues "boost asio" --repo stephenberry/glaze --include-prs ...; 163: gh search issues "ssl https" --repo stephenberry/glaze --include-prs -...; 168: gh issue view 2599 --repo stephenberry/glaze --comments; 169: gh issue view 2470 --repo stephenberry/glaze --comments; 170: gh pr view 2873 --repo stephenberry/glaze --comments; 202: gh api -X GET search/code -f q='GLZ_USE_BOOST_ASIO repo:stephenberry/g...; 203: gh api -X GET search/code -f q='README repo:stephenberry/glaze' -F per... |
| 27, exa, Boost.Hash2 Peter Dimov hash_append_size P2996 reflection describe | 122: gh search issues "reflection" --repo boostorg/hash2 --include-prs --li...; 123: gh search issues "describe" --repo boostorg/hash2 --include-prs --limi...; 171: gh api search/commits q='reflection repo:boostorg/hash2'; 172: gh api search/commits q='freflection repo:boostorg/hash2'; 173: gh api search/commits q='reflection repo:boostorg/container_hash'; 174: gh api search/commits q='reflection repo:boostorg/describe'; 175: https://github.com/boostorg/describe; 194: gh api -X GET search/code -f q='BOOST_DESCRIBE_HAS_REFLECTION repo:boo...; 195: gh api -X GET search/code -f q='README repo:boostorg/describe' -F per_...; 196: gh api -X GET search/code -f q='freflection repo:boostorg/hash2' -F pe...; 197: gh api -X GET search/code -f q='README repo:boostorg/hash2' -F per_pag... |
| 30, exa, Catch2 CTest catch_discover_tests sanitizer support | 176: gh issue view 2507 --repo catchorg/Catch2 --comments |
| 31, exa, stephenberry glaze networking http server production maturity | 164: gh search issues "http server production" --repo stephenberry/glaze --...; 167: gh issue view 2366 --repo stephenberry/glaze --comments |
| 125, gh-issue-search, gh issue list --repo boostorg/hash2 --state all --limit 80 | 129: gh issue view 30 --repo boostorg/hash2 --comments |
| 126, gh-pr-search, gh pr list --repo boostorg/hash2 --state all --limit 80 | 127: gh pr view 31 --repo boostorg/hash2 --comments; 128: gh pr view 34 --repo boostorg/hash2 --comments |
| not recorded (before D137) | 39 rows: 49, 50, 51, 52, 53, 56, 59, 62, 65, 68, 71, 75, 78, 82, 86, 91, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119 |

Rows 125 and 126 (the boostorg/hash2 issue and PR lists, themselves seeded by stage-1 row 1) appear as seeds for 127 to 129 because that is what was recorded when those views were chosen; `queries.jsonl` carries a `seed_note` on each.

## 6. Hash libraries (Q108.1)

The two needs differ and should stay separate. Cryptographic: SHA-256 digests written to receipts and compared
across runs and machines (CT-59's `result_schema` and `artifacts` rows, `CT59-design.md:28-29`), where a
standard, collision-resistant algorithm matters. Non-cryptographic: hashing inside one process (hash maps, dedup
sets, cache keys), where speed and distribution matter and nothing is persisted. Anything persisted or compared
across processes should use SHA-256, which removes the case for a second persisted fast hash.

### 6.1 Cryptographic (SHA-256 for artifact digests and receipts)

| Option | Algorithms | C++ standard and reflection | Speed (source) | Licence | vcpkg (VCPKG / latest) | Verdict |
|---|---|---|---|---|---|---|
| CommonCrypto `CC_SHA256_Init/Update/Final` | SHA-1, SHA-2 family; MD2, MD4, MD5 deprecated (R13 section 3) | C API; n/a | 2.57 GiB/s (M2 Air) and 3.28 GiB/s (M4 Pro) for 64 KiB to 16 MiB blocks (`OFF/pages/notonbluray-apple-sha256.md:9-27`) | OS built-in (libSystem) | n/a; SDK header present (`OFF/receipts/probe/host-probe.txt`, `CommonDigest.h:193-205`) | Use on macOS (R13, D135), wrapped as a Hash2 `HashAlgorithm` |
| OpenSSL `EVP_Digest*` | SHA-2, SHA-3, BLAKE2 and more | C API; n/a | 3,356 MB/s SHA-256 on an M4 with OpenSSL 3.6.4 at 16 KB blocks (`OFF/pages/picklog-md5-sha256-m4.md:10,28-38`) | Apache-2.0 | 3.6.5 port-version 1; host has Homebrew `openssl@3` 3.5.9 and `openssl@4` 4.0.3 (`host-probe.txt`) | Linux route later (R13); the TLS dependency if networking comes |
| Boost.Hash2 `sha2_256` | MD5, SHA-1, SHA-2 (224 to 512/256), SHA-3 and SHAKE, RIPEMD-128 and 160, BLAKE2s and 2b, HMAC (`OFF/repos/boostorg_hash2/README.md:10-18`, `doc/hash2/changes.adoc`) | C++11 (`README.md:45`) with `constexpr` hashing (`doc/hash2/hashing_bytes.adoc:186-208`); reflection only through Describe | 320.57 MB/s at 64 KiB after PR #31, author's machine (boostorg/hash2#31); portable, no SHA instructions | BSL-1.0 | 1.92.0 / ships with Boost (no GitHub releases, `OFF/gh/releases/boostorg_hash2.json`) | Use for `constexpr` known-answer tests and as a portable fallback, not for file digests |
| BLAKE3 C library | BLAKE3 (not SHA-256) | C; multithreading only through oneTBB, which needs a C++20 build option (`OFF/repos/BLAKE3-team_BLAKE3/c/README.md:94,168-199,273`) | slower than hardware SHA-256 single-threaded on Apple silicon (BLAKE3#315); SMHasher `blake3_c` 1,298.04 MiB/s on a Ryzen 5 PRO 3350G (`OFF/pages/smhasher-table.md`) | CC0-1.0 or Apache-2.0 (or Apache-2.0 with LLVM exception; `OFF/repos/BLAKE3-team_BLAKE3/LICENSE_*`) | 1.8.7 / 1.8.7 (2026-08-20) | Not now: not the recorded digest and no speed gain on this hardware |
| picosha2, Crypto++, Botan, libsodium | | | | | | R13 section 3; not needed |

Hash2's review accepted it on 2024-12-20 (ACCEPT 9, REJECT 3, CONDITIONAL ACCEPT 5) with the note that "the
library does not intend to be a cryptographic provider" and a request for adapters to existing implementations
(`OFF/pages/hash2-review-report.md`). That matches the design here: Hash2's `HashAlgorithm` concept
(`README.md:23-37`) wraps a `CC_SHA256_CTX`, and `result()` copies the context before `CC_SHA256_Final` so it can
be called again, as the concept requires (UNVERIFIED, not compiled).

### 6.2 Non-cryptographic (hash maps, dedup, cache keys)

| Option | Algorithms | C++ standard and reflection | Speed (source) | Licence | vcpkg (VCPKG / latest) | Verdict |
|---|---|---|---|---|---|---|
| Boost.Hash2 | FNV-1a, xxHash32 and 64, XXH3-128 (since 1.89), SipHash-64 and 32 (`README.md:10-18`, `changes.adoc`) | C++11 to C++26; `hash_append` for scalars, ranges, tuples, `std::optional` and `std::variant` (1.92.0), described classes and `tag_invoke` types (`hash_append.hpp:179-520`) | no published figure; portable scalar code (speed UNVERIFIED) | BSL-1.0 | 1.92.0 | Use as the framework; P2996 through the bridge (6.3) |
| xxHash (C) | XXH32, XXH64, XXH3-64, XXH3-128 | C; header-only with `XXH_INLINE_ALL` (`README.md:100-104`) | XXH3 (NEON) 36.3 GB/s on an Apple M1 Pro, XXH3 (AVX2) 59.4 GB/s on an i7-9700K (`OFF/pages/xxhash-site.md`, `README.md` Benchmarks); SMHasher `xxh3` 20,853.74 MiB/s, 29.46 cycles/hash, flagged "Moment Chi2 14974, BIC" | BSD-2-Clause library; the `xxhsum` CLI is GPLv2 (`README.md:271`, `cli/README.md:4`) | 0.8.4 / v0.8.4 (2026-09-19) | Only if a measured bulk-hash need appears |
| rapidhash | rapidhash, rapidhashMicro, rapidhashNano | one C/C++ header with `constexpr` macros (`rapidhash.h:58-63`); no SIMD or crypto instructions (`README.md`) | 47, 57, 61 and 71 GB/s on M1 Pro, M3 Pro, M3 Ultra and M4 against xxh3's 37, 43, 47 and 49 GB/s; 1.79 ns against 1.92 ns for 4 to 16 byte keys on an M1 Pro (`OFF/repos/Nicoshev_rapidhash/README.md`, "Outstanding performance"); SMHasher 21,513.71 MiB/s, 22.04 cycles/hash, no flags | MIT (repository `LICENSE`); the VCPKG port metadata says BSD-2-Clause | "3" port-version 1 / rapidhash_v3 (2025-08-16) | Best single-header candidate if a fast byte hash is ever needed |
| ankerl::unordered_dense hash | its own descendant of wyhash, not a public entry point (`include/ankerl/unordered_dense.h:253-262`) | C++17; reads Boost's `is_avalanching` (`:611-623`) | author: faster than rapidhash v3 above 24 bytes on a Ryzen 9 7950X (`OFF/pages/ankerl-four-buckets.md:9,302`) | MIT | 5.3.1 / v5.3.2 (2026-10-09) | Only together with the map; not adopted here |
| komihash, wyhash, a5hash | | | SMHasher 11,143.94, 22,640.53 and 9,730.52 MiB/s | MIT; Unlicense (wyhash); MIT | 5.34; 2023-12-03; absent | Not needed |

SMHasher figures come from one table on one machine (AMD Ryzen 5 PRO 3350G, `OFF/pages/smhasher-table.md:1-13`);
the vendor figures are each project's own benchmark. Nothing was measured on this host.

### 6.3 Reflection-driven hashing

| Option | Mechanism | Our lanes | Status | Licence |
|---|---|---|---|---|
| Hash2 with `BOOST_DESCRIBE_STRUCT` | a macro per type lists members; Hash2 walks bases and members (`hash_append.hpp:397-452`) | both | released (1.92.0) | BSL-1.0 |
| Hash2 with Describe's P2996 backend | every non-template class is described automatically (`rf_members.hpp:66-133`) | GCC 16.2 lane only (macro gate, `config.hpp:68-79`) | develop branch, commits of 2026-09-27 to 29; the release that carries it is UNVERIFIED | BSL-1.0 |
| Project `tag_invoke` bridge (proposed) | a constrained `tag_invoke(hash2::hash_append_tag, Provider, Hash&, Flavor, T const*)` in the project namespace, found through ADL by Hash2's detection (`detail/has_tag_invoke.hpp`, `hash_append.hpp:497-504`), walking `nonstatic_data_members_of` | both | about 30 lines (UNVERIFIED); Hash2 prefers `tag_invoke` over the described path when both apply (`hash_append.hpp:405-415`, commit `8c93d7dc0`) | ours |
| mirror_hash | a P2996 `std::hash` replacement plus an AES and rapidhash byte hash (`OFF/repos/FranciscoThiesen_mirror_hash/README.md`) | clang-p2996 with `-freflection-latest` | 2 stars, last commit 2025-12-30, no licence file (GitHub licence null) | none: cannot be used |
| Blog pattern (infotraining) | `hash_combine` over `nonstatic_data_members_of` and `bases_of` with `template for` (`OFF/pages/infotraining-hashing-cpp26.md`) | GCC 16 | example code | n/a |

Bridge sketch (UNVERIFIED, not compiled). It avoids `template for` because MP's p2996 lane passes `-freflection`
only (`CMakeLists.txt:46`) and R13 section 4 found expansion statements need a separate flag on the fork; MP's
core already uses `nonstatic_data_members_of` without them (`src/core.cpp:17-19`).

```cpp
namespace rsm {
template <class T> concept reflect_hashed = std::is_aggregate_v<T> && requires { typename T::rsm_hashed; };

template <class Provider, class Hash, class Flavor, reflect_hashed T>
constexpr void tag_invoke(boost::hash2::hash_append_tag const&, Provider const&, Hash& h, Flavor const& f, T const* v) {
  static constexpr auto members = std::define_static_array(
      std::meta::nonstatic_data_members_of(^^T, std::meta::access_context::unchecked()));
  [&]<std::size_t... I>(std::index_sequence<I...>) {
    (Provider::hash_append(h, f, v->[:members[I]:]), ...);
  }(std::make_index_sequence<members.size()>{});
  if constexpr (members.size() == 0) Provider::hash_append(h, f, '\x00');
}
}  // namespace rsm
```

The opt-in tag keeps the bridge from capturing every class in the namespace; appending one byte for an empty
class copies Hash2's own rule for described classes (`hash_append.hpp:442-445`).

## 7. Unit test frameworks (Q108.2)

### 7.1 What stephenberry/ut is and what it changes

It is not a Git fork of boost-ext/ut: `gh api repos/stephenberry/ut` reports `fork false` (queries.jsonl seq 101; `OFF/gh/repo-meta.tsv`),
and `openalgz/ut` redirects to it (seq 102). The maintainer's account: "openalgz/ut is a rework of qlibs/ut,
which was a stripped down rework of boost-ext/ut" (glaze discussion #1653, 2025-03-19;
`OFF/gh/disc_stephenberry_glaze_1653.json`), and on 2026-08-24 that it "is actually based on qlibs/ut ...
qlibs/ut doesn't use the standard C++ library and doesn't support MSVC ... We have to support MSVC", while
boost-ext/ut "would segfault multi-threaded programs that used std::format by simply including the test header"
(stephenberry/ut#14; `OFF/gh/stephenberry_ut_14.json`). A contributor in the same thread lists the rest: C++23
instead of C++20, native `import ut;` built on `import std;`, and "3358 lines over just 419. The difference is
absence of functionality not used by Glaze".

What the 419 lines do (`OFF/repos/stephenberry_ut/include/ut/ut.hpp`, commit `dc65567`, v1.2.1 of 2026-07-31):

- Tests are `"name"_test = [] {...}` or `test("name") = ...` inside `suite name = [] {...};`; the `suite`
  constructor runs them during static initialisation, before `main` (`:369`), so `main` can be empty (README).
- `expect(bool)` and the fatal `expect[bool]` take a value convertible to `bool` (`:308, 329-350`); a failure
  prints `FAILED "name" file:line` plus any `<< message` (`:124-130`). There is no expression decomposition, so
  operand values appear only if the message prints them.
- Compile-time tests: with `UT_COMPILE_TIME`, non-mutable, non-capturing tests also run inside
  `static_assert((test(), "[FAILED]"))` (`:266-271`); `consteval` lambdas run only at compile time (README).
- Filtering only through the `UT_RUN` environment variable with exact names (`:9-12, 233-260`); no listing, no
  reporter other than the console stream, no tags, no sharding.
- Exit status: the reporter's destructor calls `std::exit(1)` when an assertion failed (`:203-208`), and a fatal
  `expect[...]` calls `std::exit(1)` mid-test (`:195-201`). The destructor belongs to the namespace-scope `cfg`
  object (`:287`), so it runs during program termination, and calling `exit` again there is undefined in C ("The
  behavior is undefined if a program calls `exit` more than once", `OFF/pages/cppreference-c-exit.md:168`), which
  C++ inherits. It works in glaze's CI today; treat it as a risk to watch under sanitizers.
- Counters are plain `size_t` (`:100-101, 169-197`) with no lock or atomic, so `expect` from a worker thread is a
  data race TSan would report; the "thread safe" claim in #1653 means "including the header does not crash
  threaded code", not concurrent assertions.
- Modules: `UT_ENABLE_MODULES` builds `modules/ut.ixx` and needs `import std` support and a CMake UUID gate
  (`README.md`, "Modules support"; PR #6 merged 2026-03-07, `OFF/gh/stephenberry_ut_6.json`).

### 7.2 Comparison

| Framework (version) | Macro-free | Standard | P2996 use | Compile and run cost (source) | CTest integration | Sanitizers | constexpr testing | Modules | Our two compilers | Licence, vcpkg, activity |
|---|---|---|---|---|---|---|---|---|---|---|
| stephenberry/ut 1.2.1 | yes | C++23 | none (0 files, `p2996-usage-counts.txt`) | 419-line header including `<concepts>` through `<string_view>` and `<iostream>` (`ut.hpp:16-21`); no benchmark found (gap) | one `add_test` per executable, as glaze does (`glaze tests/json_test/CMakeLists.txt:14`) | glaze runs its tests under ASan and UBSan on Clang by default (`glaze tests/CMakeLists.txt:15,39-40`) but not in the reflection jobs (`gcc.yml:194`, `p2996-reflection.yml:88`); double `exit` and racy counters (7.1) | yes: `static_assert` mode and `consteval` tests | `import ut;` (PR #6) | compiled in glaze CI on gcc:16.1 with `-freflection` and on clang-p2996 with libc++ (Verdict item 3) | MIT; not in VCPKG (`vcpkg-ports.txt`); releases v1.0.0 2025-06-12 to v1.2.1 2026-07-31 |
| boost-ext/ut 2.3.1 | yes | C++20 | none | Debug build of a typed-test suite 197 s against Catch2's 74 s and snitch's 71 s, executable 71.4 MB (`OFF/repos/snitch-org_snitch/README.md:249-270`); a 2019 benchmark favours it on trivial cases (`OFF/repos/cpp-testing_ut-benchmark/results/clang9.release.bench`) | none built in | thread-safety crash #618 open since 2024-03-06 | yes | `import boost.ut` broken (#713); VCPKG disables the module (R13) | no GCC 16 or Clang 21 issues found (seq 177, 178) | BSL-1.0; 2.3.1 in VCPKG; last release 2025-04-02 |
| qlibs/ut (ut2) 2.1.6 | yes | C++20 | none (its "reflection integration" is the pre-P2996 qlibs/reflect, `OFF/repos/qlibs_ut/ut` header) | "fast compilation times" claimed (same header) | none | not found | compile-time first | `ut.cppm` | gcc 12+, clang 16+ claimed | MIT (in the header); not in VCPKG; last release 2025-04-15 |
| Catch2 3.16.1 | no (`TEST_CASE`, `REQUIRE`) | C++14 library; VCPKG builds it as C++17 (`vcpkg-portfiles.txt`) | none | compiled library, 44 s Debug and 50 s Release to build in snitch's benchmark; a 2026 user saw the same 30 s as doctest for a 13-file suite (doctest#1168); 3.16.1 cut decomposer and registration costs (`docs/release-notes.md`, 3.16.1) | `catch_discover_tests` per test, `--order decl` since 3.16.1, about 3k tests registered per second since 3.16.0 | POST_BUILD discovery fails under ASan, open since 2022 with no reply (#2507); use `DISCOVERY_MODE PRE_TEST` | `STATIC_REQUIRE`, `STATIC_CHECK` (`docs/other-macros.md:62`) | none | Clang 20 and 21 and GCC 16 C++26 fixes (R13 section 5) | BSL-1.0; 3.16.0 in VCPKG with a `thread-safe-assertions` feature (`CATCH_CONFIG_THREAD_SAFE_ASSERTIONS`); 3.16.1 on 2026-10-08 |
| doctest 2.5.3 | no | C++11 | none | header-only; no gain over Catch2 v3 in the 2026 report (#1168); 2018 header benchmarks only (`OFF/pages/doctest-benchmarks.md`) | not re-checked in this run | not re-checked | `STATIC_REQUIRE` proposal only (doctest#250, Exa q19) | none | GCC 16 in CI (R13) | MIT; 2.5.3 in VCPKG |
| snitch 1.3.2 | no (Catch2-like) | C++20 | none | fastest in its own benchmark: tests build in 71 s Debug and 148 s Release against Catch2's 74 s and 221 s; run 45 ms against 82 ms (`README.md:249-270`) | Catch2-compatible reporters and IDE plugins (`README.md:66`) | no heap allocation by the framework (`README.md:59`) | `CONSTEXPR_CHECK`, `CONSTEVAL_CHECK` (`README.md:69`) | none | no GCC 16 or Clang 21 issues found (seq 154 to 157) | BSL-1.0; 1.3.2 in VCPKG; last release 2025-03-22, commits to 2026-10-07 |
| GoogleTest 1.18.0 | no | C++17 (`README.md:17`) | none | heaviest (R13) | `gtest_discover_tests` | widely used | none | no; modules discussion #4916 unanswered by maintainers | maintainers declined a libstdc++ warning fix (#4935, R13) | BSD-3-Clause; 1.18.0 in VCPKG |
| rtest (Codeberg, design study) | yes: suites are structs, tests are `test*` member functions found by P2996 | C++26 | yes: `members_of`, `define_static_array`, `display_string_of` (`OFF/repos/codeberg_JonasToth_rtest/include/rtest/ReflectUtil.h`; `OFF/pages/rtest-blog.md`) | not measured | `add_test` per suite (`CMakeLists.txt:51-73`) | not stated | no | no | "Requires GCC-16" (`README.md`); clang-p2996 untested | no licence file; "_should not_ be used for production code bases" (`README.md`) |
| Catch23 | no (four macros) | C++23 | none; enum strings through "pseudo-reflection" (`README.md:94,140`) | not measured | not stated | not stated | not stated | no | Compiler Explorer only | MIT; "pre-release work-in-progress and is not, yet, intended for general use" (`README.md:6`) |

None meets the user's full ideal (macro-free, fast, C++23 or 26, static reflection). Reflection-based test
registration exists only in rtest, which cannot be adopted (no licence, GCC 16 only, a declared design study).
Reflection-based value printing exists in no framework; it is a project helper either way (a `std::formatter`
over `nonstatic_data_members_of`, R13 section 7) and fits ut's `<< message` hook.

Why stephenberry/ut over Catch2 here: it is the only macro-free option proven on both of our reflection compilers
(glaze CI), it shares a maintainer and release rhythm with glaze, which D135 adopts, and being one header it
removes the four-triplet build of a compiled framework (R13 section 5). What Catch2 would add is tooling, not
language support: per-test CTest discovery, JUnit, JSON and XML reporters, sharding, tags and thread-safe
assertions. MP registers one CTest test per executable today (`CMakeLists.txt:70-72`), so ut fits the current
pattern; if the gate later needs per-test results in CTest or JUnit files, switch to Catch2 3.16 (R13's research)
rather than extending ut.

## 8. glaze networking (Q108.3)

| Feature | Header and API | Asio backend | TLS | CI coverage | Maturity evidence | Fit with R14 (Boost.Asio `io_context` plus stdexec's Asio bridge) |
|---|---|---|---|---|---|---|
| HTTP server | `glaze/net/http_server.hpp` (3,504 lines): router, middleware, CORS, streaming, websocket upgrade; completion handlers, no coroutines (0 `co_await`) | standalone `<asio.hpp>` first, Boost when `GLZ_USE_BOOST_ASIO` is defined (`include/glaze/ext/glaze_asio.hpp:20-49`) | `http_server<true>` or `https_server`, `-Dglaze_ENABLE_SSL=ON`, OpenSSL (`docs/networking/tls-support.md`); TLS 1.3 negotiation since PR #2873 (merged 2026-09-16) | standalone Asio 1.36 with GCC 15, Boost 1.86 and 1.88, macOS Clang (`.github/workflows/standalone-asio.yml:31-95`, `boost-asio.yml:39-109`, `clang.yml:34-51`); not in the reflection jobs | maintainer: "still new" (#2366, 2026-03-12); his benchmark: 1% to 24% more requests per second than Boost.Beast on 8 of 9 rows and 10% fewer on connection-per-request (#2366, 2026-03-20) | `server.start(0)` leaves the caller to run an external `io_context` (`docs/networking/http-server.md:72-147`) |
| HTTP client | `glaze/net/http_client.hpp` (3,363 lines): synchronous, `std::future` and callback APIs, pooling, streaming | as above | verification on by default with platform trust anchors; CA configuration since PR #2776 (2026-08-14) (`docs/networking/http-client.md:46-89`) | as above | client TLS floor raised in PR #2874 (2026-09-17) | an optional executor in the constructor shares an `io_context` (`http_client.hpp:1277-1323`); its API takes callbacks, not completion tokens, so stdexec's `use_sender` (`offline/research/R14-execution-libraries/repos/stdexec/include/exec/asio/use_sender.hpp:227-251` (R14 mirror)) does not apply directly and a small project adapter is needed (size UNVERIFIED) |
| WebSocket | `websocket_client.hpp`, `websocket_connection.hpp` (server side through the HTTP server) | as above | `wss` | Autobahn fuzzing-server job (`.github/workflows/autobahn.yml:31-88`; PR #2615 merged 2026-06-12) | an open "CRITICAL BLOCKER BUG" crash in `websocket_client::run()` since 2026-03-30 (#2409), reproduced only on MinGW ("everything works fine on Linux with GCC 16.1.0", 2026-05-10); lifecycle PR #2411 still open | same executor model |
| REST registry | `glz::registry<..., REST>`; "Service types must define `glz::meta<...>::value` with the methods you want to expose" (`docs/networking/rest-registry.md:80,87-90`) | through the HTTP server | as the server | `http_router_test`, `registry_view_test` in the Asio jobs | whether the P2996 backend can list member functions without `glz::meta` is undocumented (UNVERIFIED; `docs/p2996-reflection.md:130-190` covers data members) | handlers are synchronous callbacks |
| JSON-RPC 2.0 | a typed client and server, plus a registry variant (`docs/rpc/json-rpc.md`) | transport-agnostic types served through the HTTP server or REPE | as the transport | `jsonrpc_registry_test` in the Asio jobs | documented without a stability warning | as the transport |
| REPE RPC | `glaze/ext/glaze_asio.hpp` `asio_server` and `asio_client` (C++20 coroutines: 13 `co_await`, 2 `co_spawn`) | as above | `GLZ_ENABLE_SSL` includes `asio/ssl.hpp` (`glaze_asio.hpp:33-49`) | `asio_repe` in the Asio jobs | "should not be considered stable" (`docs/rpc/repe-rpc.md:3-5`) | coroutine-based; would need `co_spawn` on the shared context |

Asio dependence. Upstream glaze accepts either backend: `glaze_setup_asio()` searches Boost first, then standalone,
then fetches a bundled copy (`docs/networking/asio-setup.md`), and a June 2026 fix made the CMake choice and the
header choice agree (#2599 closed 2026-06-10, PR #2604). Its Boost.Asio support broke and was fixed three times in
nine months (#2164 closed 2025-12-21, #2266 closed 2026-01-28, #2470 closed 2026-04-13). The VCPKG port is
narrower: its `networking` feature depends on standalone `asio` 1.32.0 and patches the header to always take the
standalone branch, and `ssl` adds `openssl` (`vcpkg-portfiles.txt`, glaze section; `vcpkg-glaze-patch-usage.txt`).
R14 chooses Boost.Asio 1.92.0 (Asio 1.38.2) through `stdexec[asio]` (R14 Verdict, evidence item 4), so using the
port's `networking` feature would put two Asio copies and two event loops in one binary. The fit that works on
paper: glaze core from VCPKG, `boost-asio` from R14's admission, `GLZ_USE_BOOST_ASIO` defined on the target,
`GLZ_ENABLE_SSL` plus `openssl` only when TLS is needed, and every glaze server or client bound to the one
`io_context` (`start(0)`, the executor constructor). Whether `glaze/net/*` compiles with `-DGLZ_REFLECTION26=1` in
either lane is unknown: no CI job covers it and three searches found no issue (seq 188 to 190).

## 9. Admissions and risks

Admissions (each a recorded operation; D86 heavy-run rules apply to builds):
1. Hashing: a `vcpkg.json` hunk adding `boost-hash2` (VCPKG 1.92.0; it pulls `boost-assert`, `boost-cmake`,
   `boost-config`, `boost-container-hash`, `boost-describe`, `boost-headers` and `boost-mp11`, all header-only,
   `vcpkg-ports.txt`); one fetch into the four retained triplet trees (today they hold only fmt 12.2.0,
   `host-probe.txt`); and a probe TU per lane with MP's flags (`-std=c++26 -freflection -pedantic-errors -Wall
   -Wextra -Werror`) that includes `boost/hash2/hash_append.hpp`, instantiates the bridge on a two-member aggregate,
   and checks the CommonCrypto adapter against the NIST "abc" vector and against Hash2's own `sha2_256` evaluated at
   compile time. CommonCrypto needs no admission (libSystem).
2. Tests: a lane that adds `third_party/ut/ut.hpp` v1.2.1 and its MIT `LICENSE` (or a pinned `FetchContent` of tag
   v1.2.1; vendoring matches glaze and needs no network at build time), one sample suite, one `add_test`, and runs
   of that suite under ASan, UBSan and TSan in both lanes. The Catch2 fallback is R13's admission.
3. Networking: none now. Later: R14's `stdexec[asio]` admission, `openssl` 3.6.5 if TLS, glaze core without port
   features, and a both-lane probe of one `glaze/net` client call with `-DGLZ_REFLECTION26=1`.

Risks:
- H1. Nothing was compiled. The bridge, the CommonCrypto adapter and Hash2 under `-Werror -pedantic-errors` in the
  clang-p2996 lane are UNVERIFIED; Hash2's CI covers GCC 16.2 with `-freflection`, Clang up to 22 and macOS
  (`ci.yml:74-197`), not the Bloomberg fork.
- H2. Once a Boost release ships Describe's backend, the GCC lane describes every non-template class automatically
  and Hash2 hashes plain structs member by member there, while the clang-p2996 lane still needs the bridge. Keep the
  bridge's opt-in tag so both lanes produce the same bytes, and set `BOOST_DESCRIBE_DISABLE_REFLECTION` (the switch
  in `config.hpp:68`) if lane-parity tests disagree.
- H3. Hash2's `hash_append` output depends on its flavor (byte order, size type); persisted digests must fix the
  flavor (`doc/hash2/hashing_objects.adoc:75-113`) or, simpler, hash serialized bytes rather than objects.
- T1. ut's double `exit` and unsynchronised counters (7.1). Mitigate with the TSan rule and by exercising the
  failing-exit path under ASan in the probe.
- T2. ut has no per-test CTest entries; a failing suite shows as one failed CTest test. Acceptable for MP's current
  one-test-per-executable pattern; revisit when the gate needs per-test results.
- T3. ut is maintained for glaze's needs ("absence of functionality not used by Glaze", ut#14); anything more is
  ours to write or a reason to switch to Catch2.
- N1. glaze's networking API moved quickly in 2026 (header maps replaced in PR #2718, TLS defaults in #2873 and
  #2874) and its Boost.Asio path broke three times.
- N2. The VCPKG `networking` feature conflicts with R14's Boost.Asio (section 8).

## 10. Code examples found

- Hash2 described-class walk and `tag_invoke` hook: `OFF/repos/boostorg_hash2/include/boost/hash2/hash_append.hpp:397-504` (commit `69e7e02`).
- Describe's P2996 backend: `OFF/repos/boostorg_describe/include/boost/describe/detail/rf_members.hpp:1-137`, gate in `detail/config.hpp:68-79` (commit `ae199a7`).
- P2996 hashing walk-through with `bases_of`: `OFF/pages/infotraining-hashing-cpp26.md`; annotations that skip members: `OFF/pages/infotraining-annotations-hashing.md`.
- Reflection-registered test suites: `OFF/repos/codeberg_JonasToth_rtest/include/rtest/ReflectUtil.h` and `TestSuite.h` (commit `c148379`), explained in `OFF/pages/rtest-blog.md`.
- ut compile-time and runtime tests: `OFF/repos/stephenberry_ut/README.md` example and `include/ut/ut.hpp:262-280` (commit `dc65567`).
- glaze HTTP server on an external `io_context`: `OFF/repos/stephenberry_glaze/docs/networking/http-server.md:104-147`; client executor constructor `include/glaze/net/http_client.hpp:1277-1323` (commit `e194d23`).
- glaze Asio backend selection: `include/glaze/ext/glaze_asio.hpp:20-49`; the VCPKG override in `OFF/receipts/probe/vcpkg-glaze-patch-usage.txt`.
- Hash2 SHA-256 speed-up with before and after numbers: boostorg/hash2#31 (`OFF/gh/boostorg_hash2_31.json`).

## 11. Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 0 | Repo reads | `cat`, `grep`, `sed` over the brief, R13, R14's verdict, `decisions.jsonl` (D112, D130, D135, D136), `CT59-design.md`, `CMakeLists.txt`, `vcpkg.json`, `src/core.cpp`, `dev/saved-searches.toml`, `dev/collect_saved_search.py`, `dev/github_search_one_page.py` | 0 | n/a | yes |
| 0 | Host probes | `ls` of VCPKG ports, the four retained triplet trees and the Homebrew Cellar; `clang++ --version` (fork), `g++-16 --version`, `/usr/bin/clang++ --version`, `openssl version`; `grep` of the SDK's `CommonDigest.h` | 0 | `OFF/receipts/probe/*` | yes |
| 1 | Exa | `fnox ... exec -- run_exa.sh` (POST api.exa.ai/search, key from the environment through `curl -K -`), 36 queries | 0, HTTP 200 x36 | 10 each | yes (section 2) |
| 1 | Context7 | `fnox ... exec -- ctx7 library <name> <query>` x4 | 1 x4 | "Monthly quota reached" | no, gap |
| 1 | Firecrawl | `fnox ... exec -- firecrawl search ... --json`; `firecrawl scrape <glaze http-server docs> --format markdown` | 1, 1 | HTTP 402 insufficient credits | no, gap |
| 1 | webclaw | `webclaw <url> -f markdown`, 38 pages | 0 except 2 | `catch2-cmake-integration` and `boost-ut-cppcon2021` empty (rc 1); `reddit-hash2-accepted` a 220-byte placeholder | yes; the empty ones were not cited (repository clones used instead) |
| 1 | Serper | `fnox ... exec -- run_serper.sh` (POST google.serper.dev/search, key from the environment), 8 queries | 0, HTTP 200 x8 | 10 each | corroboration only |
| 1 | Last30Days | `fnox ... exec -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py "<topic>" --plan plan.json --emit json --quick --save-dir "" --no-browser-cookies`, then a narrower `--search reddit,hackernews,github` run | 0, 0 | 0 results (grounding error, rerank HTTP 503, 1 of 3 subqueries planned), then 4 off-topic | no, gap |
| 2 | Repository metadata | `gh api repos/<r>` x19 | 0 x18, 1 x1 (`JonasToth/rtest` is not on GitHub; found on Codeberg through the blog) | redirects found for `openalgz/ut` and `boost-ext/ut2` | yes |
| 2 | Clones | `git clone --depth 1 --filter=blob:none --no-tags <url>`, 21 repositories (one from Codeberg) | 0 x21 | commits in the manifest | yes |
| 2 | gh search issues | `gh search issues "<term>" --repo <r> --include-prs --limit 15`, 25 queries; `gh issue list` and `gh pr list --state all` for boostorg/hash2 | 0 | 0 to 41 | yes where non-zero |
| 2 | gh issue and PR views | `gh pr view` falling back to `gh issue view`, `--comments --json ...`, 15 items | 0 | `OFF/gh` | yes |
| 2 | Discussions | `gh api graphql` `repository.discussion(number)` for glaze #1653 and googletest #4916 | 0 x2 | 2 | yes |
| 2 | Release lists | `gh release list --repo <r> --limit 8` x15 | 0 x15 | `OFF/gh/releases` | yes |
| 2 | Commit search | `gh api -X GET search/commits -f q='<term> repo:<r>'` x4 | 0 x4 | 2, 1, 1, 4 | yes (decisive for 6.3) |
| 2 | Saved-search reproduction | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5` with a control each, 7 s apart | 0 x13 | section 4 | yes |

## 12. Open gaps

- Nothing was compiled or benchmarked (the brief allowed `ls` and `--version` only). Every speed figure is quoted,
  most from vendors' own benchmarks on other machines; Hash2's portable speeds on this host, the bridge, the
  CommonCrypto adapter and ut in our exact lanes are UNVERIFIED.
- The Boost release that will carry Describe's reflection backend, and its date, are UNVERIFIED (the 1.93.0 merge
  window opened on 2026-08-13, `OFF/pages/boost-193-open-for-merging.md`; the calendar page mirrored empty).
- No compile-time benchmark of stephenberry/ut was found; its speed claim rests on its size.
- Whether `glaze/net/*` compiles with `-DGLZ_REFLECTION26=1` in either lane is unknown.
- Whether glaze's P2996 backend can register member functions for the REST registry without `glz::meta` is
  UNVERIFIED.
- Context7's monthly quota was exhausted (4 calls); Firecrawl returned HTTP 402 (2 calls); Last30Days returned
  nothing on topic in two runs; two webclaw pages came back empty. Stage-2 rows logged before D137 arrived (20
  clones and 19 repository lookups) carry `seeded_by: null`, because their seeds were not recorded when chosen.
- doctest's CTest discovery and sanitizer behaviour were not re-checked in this run.
