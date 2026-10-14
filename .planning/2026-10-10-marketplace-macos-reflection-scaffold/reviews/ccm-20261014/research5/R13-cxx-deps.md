# R13: third-party C++ libraries for the CT-59 agent-dispatch core (fork F2, with F1 context; widened by D130)

Written by research agent R13 of session `ccm-20261014` (`ce9c0b3d`), 2026-10-14, for CT-59 fork F2
(`reviews/ccm-20261014/ct59/CT59-design.md` sections 2 and 5). Read-only except this file and the
offline mirror. MP = the repository root (HEAD `21af565`, branch `codex/marketplace-native-onboarding`).
Mid-task the parent relayed user decision D130: prefer libraries that use or support C++26 static
reflection (P2996) wherever possible, glaze being the example; every need below therefore carries a
"P2996" column, and each section names the best reflection-capable option even where another wins.

Citation keys. OFF = `offline/research/R13-cxx-deps/` (untracked, D110). `OFF/manifest.json` lists 117
mirrored items (31 repository clones with commit SHAs, 39 webclaw pages, 45 `gh --json` copies, 2 Bowtie
data files) with URL, fetch time, command shape, exit code and SHA-256, plus 132 hashed receipts (manifest
SHA-256 `2ca2f87c...`).
OFF/repos are `git clone --depth 1 --filter=blob:none --no-tags` copies, cited as
`OFF/repos/<owner>_<repo>/<path>:<line>`. OFF/gh holds issue and PR JSON (`<owner>_<repo>_<n>.json`,
discussions as `disc_*.json`). OFF/receipts/probe holds this run's host probes. VCPKG = the pinned tree
`~/.local/state/marketplace-tool-foundation/vcpkg-fmt-retry-20261011T213606Z/vcpkg` at
`e456309491fd875487bf02b8a0dca76c1b1b00cc` (the `vcpkg.json:4` builtin-baseline); its port manifests
are copied into `OFF/receipts/probe/vcpkg-ports.txt` and `vcpkg-portfiles.txt`. R8 and R9 are the sibling
reports in this directory. Anything without a citation is labelled UNVERIFIED. No compiler was run: the
brief allowed `ls` and `--version` only, so every "compiles" claim rests on upstream CI and issues.

## Verdict

Recommended set (F2), in D107 order (OS built-ins first):

| Need | Choice | P2996 | Confidence |
|---|---|---|---|
| Strict JSON parse and write | jsoncons (vcpkg 1.9.0; 1.10.0 is latest) with `allow_comments(false)` and a project duplicate-key visitor pass | no | high |
| Draft 2020-12 validation, local-only `$ref` | jsoncons `jsonschema` with a resolver that maps committed `$id`s to files and returns null for anything else | no (none exists) | high |
| Typed codec for request, envelope, report | glaze 9.0.0 (P2996 backend) behind the jsoncons gate, conditional on one admitted compile probe; fallback is the design's hand-written `std::meta` codec | yes | medium |
| SHA-256 | macOS CommonCrypto `CC_SHA256_Init/Update/Final`; Linux route deferred (OpenSSL `EVP_Digest` from the distro, or kernel AF_ALG); no picosha2 | n/a | high (macOS) |
| Tests | Catch2 3.16.0 (vcpkg), built per lane triplet | no (none exists) | medium-high |
| CLI parsing | hand-written verb dispatch plus a small `std::meta` flag binder; no library | own code yes | medium |
| Formatting and logging | `std::format` and `std::print`, plus the already qualified fmt 12.2.0 | no (fmt main's `enum.h` is, unreleased) | high |
| Process spawning | `posix_spawn` with `POSIX_SPAWN_SETSID` (OS built-in) | n/a | high |
| Enum and struct printing | own `enumerators_of` helpers, or glaze `reflect_enums` if glaze is adopted | yes | medium |

Overall confidence: high that jsoncons is the only permissively licensed C++ library that does Draft
2020-12 with a custom resolver; medium for glaze as the codec, because nothing was compiled.

Evidence that decides it:
1. Bowtie's Draft 2020-12 report fetched today (bowtie 2026.7.4, run started 2026-10-14T11:52Z, 384
   cases, 1,302 tests; `OFF/data/bowtie-draft2020-12.json`, scored by `OFF/receipts/bowtie_score.py`
   into `OFF/receipts/bowtie-draft2020-12-scores.json`): cpp-blaze and cpp-iris pass 1,302 of 1,302,
   cpp-jsoncons passes 1,293 (99.31%, 1 failed, 8 errored), and valijson is not in the 2020-12 report at
   all (its Bowtie dialects are draft-07 and draft-04; `OFF/data/bowtie-implementations.json`). Blaze and
   IRIS are AGPL-3.0 (`OFF/repos/sourcemeta_blaze/LICENSE`, `OFF/repos/Cobra007-star-source_IRIS/LICENSE`);
   MP is a public repository with no licence (`gh repo view` returned `visibility PUBLIC`,
   `licenseInfo null`), so adopting either is a licensing decision for the user, not a library pick.
2. No library rejects duplicate keys by default. jsoncons drops them silently (first wins for `ojson`,
   maintainer comment on danielaparker/jsoncons#505, 2025-01-10; sorted `json` keeps one after an unstable
   `std::sort`, `OFF/repos/danielaparker_jsoncons/include/jsoncons/sorted_json_object.hpp:276-294`); glaze
   overwrites the member (`OFF/repos/stephenberry_glaze/include/glaze/json/read.hpp:3171-3178`);
   nlohmann, Boost.JSON and simdjson keep one or all (section 1). The duplicate-key pass stays project
   code whatever is chosen, and jsoncons's `basic_json_visitor` is the natural place for it.
3. Glaze has no JSON Schema validator: its schema support is generation only
   (`OFF/repos/stephenberry_glaze/docs/json-schema.md:1-9`), and the one validator attempt, PR
   stephenberry/glaze#1315 "Create validate.hpp", was closed unmerged on 2025-05-29 with "JSON schema
   validation in memory is a long term desire". reflect-cpp likewise only generates schemas (R9).
4. The two lanes do not expose reflection the same way. GCC 16.2 defines `__cpp_impl_reflection 202603L`
   and libstdc++ 16 defines `__cpp_lib_reflection` (`OFF/receipts/probe/stdlib-reflection-macros.txt`;
   R8 host-probe-5). The clang-p2996 fork defines neither; MP's own core detects it with
   `__has_feature(reflection)` (`src/core.cpp:6-11`). Glaze, fmt's `enum.h` and enchantum key on the
   standard macros (`OFF/repos/stephenberry_glaze/include/glaze/core/feature_test.hpp:17-28`,
   `OFF/repos/fmtlib_fmt/include/fmt/enum.h:17-23`, `OFF/repos/ZXShady_enchantum/include/enchantum/entries.hpp:7`),
   so without an explicit define they use P2996 in the gcc16 lane and their pre-reflection fallback in
   the p2996 lane. Any reflection library must be forced on (glaze: `-DGLZ_REFLECTION26=1`) and probed
   in both lanes.

## 1. JSON parse and write

| Library | Version (VCPKG / latest) | Duplicate keys | NaN, Infinity, comments | P2996 | Compiler evidence for our lanes | Licence | Maintenance |
|---|---|---|---|---|---|---|---|
| jsoncons | 1.9.0 / 1.10.0 (2026-10-05) | Silently dropped; `ojson` first wins (#505); no option (#504 closed) | Bare `NaN`/`Infinity` are syntax errors (parser has no `N`/`I` case, `include/jsoncons/json_parser.hpp:752,1124`); string mapping only if `nan_to_str` is set (`doc/ref/corelib/basic_json_parser.md:133-148`); comments ON by default (`include/jsoncons/json_options.hpp:261`); depth cap 1024 (`:115`) | No (macro traits only) | CI builds tests with `-Werror -Wall -Wextra -pedantic` on GCC and Clang (`test/CMakeLists.txt:235,241`) and containers gcc 7 to latest and clang 7 to latest (`.github/workflows/ubuntu.yml:214,276`); the C++26 "standards" job never passes its `standard` value to CMake (`:188-207`), so C++26 is not actually tested; libc++ fix #675 (closed 2026-03-23); GCC 16 `-Werror` fix #738 (closed 2026-10-05, toon extension only, not reachable from `jsonschema` headers) | BSL-1.0 | Four releases from 1.7.0 (2026-04-27) to 1.10.0 (2026-10-05) |
| glaze | 9.0.0 / 9.0.0 (2026-09-24) | Last wins, no check (`read.hpp:3171-3178`) | Reading `NaN`, `nan`, `-nan` or `null` into a double is an error; writing NaN emits `null` (`tests/json_test/json_test.cpp:4761-4787`, `include/glaze/core/context.hpp:148`); comments off (`include/glaze/core/opts.hpp:79`); unknown keys error by default (`:80`) | Yes: alternative backend, auto-enabled by the standard macros (`feature_test.hpp:17-28`) | CI: C++26 reflection on `gcc:16.1` (`.github/workflows/gcc.yml:145-151`, PR #2553 merged 2026-05-07) and on `vsavkov/clang-p2996` with `-freflection -fexpansion-statements -stdlib=libc++ -DGLZ_REFLECTION26=1` (`.github/workflows/p2996-reflection.yml:19-21,58-59`); tests use `-Wall -Wextra -pedantic -Werror` in Debug (`tests/CMakeLists.txt:29-36`) | MIT | Very active; open C++26 PRs #2895, #2817 |
| nlohmann/json | 3.12.0 | Unspecified which value survives; documented callback recipe to reject (`docs/mkdocs/docs/features/parsing/untrusted_input.md:110-116`, PR nlohmann/json#5259 merged 2026-07-09) | NaN cannot be parsed, is written as `null` (`docs/mkdocs/docs/features/types/number_handling.md:164-175`) | No | n/a | MIT | Active |
| Boost.JSON | 1.92.0 | Last of duplicates kept (`include/boost/json/impl/object.ipp:231`) | `allow_infinity_and_nan = false`, `allow_comments = false`, `max_depth = 32` (`include/boost/json/parse_options.hpp:74,96,139`) | No (Boost.Describe) | n/a | BSL-1.0 | Active; pulls 11 Boost ports (VCPKG port deps) |
| simdjson | 5.0.2 | Accepted, all pairs reported (`doc/basics.md:4049`) | Strict otherwise (simdjson#1458) | Yes: `SIMDJSON_STATIC_REFLECTION` serialization (`p2996/README.md:55`) | R8 section 3 | Apache-2.0 or MIT | Active; no schema support |
| reflect-cpp (yyjson) | 0.25.0 | No runtime check found (only compile-time variant tag checks, `include/rfl/parsing/FieldVariantParser.hpp:42`) | UNVERIFIED | Yes, opt-in `REFLECTCPP_USE_CPP26_REFLECTION`; GCC 16.2 or clang-p2996 with `-freflection-latest` (`docs/content/cpp26_reflection.md:1-45`) | n/a | MIT | Active; compiled library with yyjson and ctre |

Paths in the table are relative to the library's `OFF/repos/...` clone. Best reflection-capable option:
glaze. It does not win the parse role because it accepts duplicates silently and cannot validate, so
the bytes must pass through jsoncons anyway; it does win the typed-codec role (section 4).

## 2. Draft 2020-12 validation with a local-only resolver

| Validator | Bowtie Draft 2020-12 (2026-10-14) | Custom resolver | Input type | P2996 | Licence | VCPKG | Maintenance |
|---|---|---|---|---|---|---|---|
| jsoncons `jsonschema` | 1,293 / 1,302 (99.31%) for Bowtie's pinned 0.177.0; misses: Unicode property escapes in `pattern` and `patternProperties` (6), `$id` with `$ref` evaluation order (2), one `$dynamicRef` scope case | Yes: `Json fun(const jsoncons::uri&)`, null means unresolved (`doc/ref/jsonschema/jsonschema.md:144-151`); an unresolvable ref throws `schema_error("Don't know how to load JSON Schema ...")` (`include/jsoncons_ext/jsonschema/common/schema_validator_factory_base.hpp:161,166`); meta-schemas are embedded (`json_schema_factory.hpp:200-215`); no network code in the extension | `jsoncons::json` | No | BSL-1.0 | 1.9.0 | Keyword table claims all 2020-12 keywords (`jsonschema.md:50-105`); format is annotation-only unless `require_format_validation` (`:127-128`) |
| sourcemeta Blaze | 1,302 / 1,302 | Yes, custom resolution "from arbitrary sources" (`README.markdown`, Features) | sourcemeta core JSON | No | AGPL-3.0 or commercial (`LICENSE`; `OFF/pages/sourcemeta-commercial.md`) | No (VCPKG `blaze` is an unrelated math library, `vcpkg-portfiles.txt`) | Very active (HEAD 2026-10-13); vendored via `DEPENDENCIES` |
| IRIS | 1,302 / 1,302 | UNVERIFIED | own | No | AGPL-3.0 | No | Bowtie harness pinned to 0.1.0 (HEAD commit 2026-06-09) |
| valijson | not in the 2020-12 report; draft-07 and draft-04 only | Yes, fetch and free callbacks (`README.md:216-218,379`) | adapters (nlohmann, RapidJSON, Boost, Qt and more) | No | BSD-2-Clause | 1.1.3 | 2020-12 is draft PR tristanpenman/valijson#234 (open since 2026-05-13, body "Raising this as a draft PR for visibility"); 2019-09 issue #97 open since 2020 |
| pboettch json-schema-validator | not in Bowtie | Yes, loader callback (`README.md:302-313`) | nlohmann | No | MIT | 2.4.0 | Draft 7 only (`README.md:9,27`); `$defs` support PR #338 merged 2025-01-22 |
| glaze | n/a | n/a | n/a | Yes | MIT | 9.0.0 | Generation only (`docs/json-schema.md:1-9`); PR #1315 closed unmerged 2025-05-29; discussion #1982 (2024-01-03 to 2025-10-23) asks for validation, not built |
| jsonschema-rs (Rust) | 1,302 / 1,302 (Bowtie runs 0.47.0; crate is 0.58.6) | Yes, `Retrieve` trait (`crates/jsonschema/src/lib.rs:590-601`) | `serde_json::Value` | n/a | MIT | No | Very active; ships Python, Ruby, WASM and CLI crates but no C ABI crate (`crates/` listing) |
| boon (Rust) | 1,302 / 1,302 (0.6.1) | Yes, `UrlLoader` (`src/lib.rs:110-123`) | `serde_json::Value` | n/a | MIT or Apache-2.0 | No | Last commit 2026-02-23; no C ABI |

Two caveats on jsoncons. Bowtie tests 0.177.0, not 1.9.0 or 1.10.0: the cpp-jsoncons harness was moved
out of the bowtie repository (bowtie-json-schema/bowtie#3000, merged 2026-07-25) and its version string
is 0.177.0 in `OFF/data/bowtie-implementations.json`, so current-version compliance is UNVERIFIED. And
jsoncons's own suite runner does not run seven required 2020-12 files (`dependentRequired`,
`dependentSchemas`, `id`, `maxContains`, `minContains`, `prefixItems`, `unknownKeyword`;
`OFF/repos/danielaparker_jsoncons/test/jsonschema/src/jsonschema_draft202012_tests.cpp` against the
vendored suite directory). Mitigation: 59b ports `test_contracts.py` and also runs the official
JSON-Schema-Test-Suite (`OFF/repos/json-schema-org_JSON-Schema-Test-Suite`, `5571928`) filtered to the
keywords the four agent-protocol schemas use.

Resolver behaviour for the design's "local refs only" rule: jsoncons resolves `$ref` against the base
URI per RFC 3986, removing dot segments (maintainer answer in discussion danielaparker/jsoncons#557,
2025-02-13), so the committed schemas should carry absolute `$id`s and the resolver should map exactly
those URIs to files under `schemas/agent-protocol/`, returning `Json::null()` for every other URI. The
factory then throws, which gives fail-closed loading. Error output: `validation_message` exposes
`instance_location`, keyword locations and a free-text `message` (`doc/ref/jsonschema/validation_message.md:14-26`);
to meet "never echo values" the codec should print only the locations and keyword, not `message`.

Rust behind a C ABI: both Rust validators score 100%, but neither ships a C ABI, so MP would write and
maintain a cbindgen shim, add a Rust toolchain to the build, and still need the duplicate-key pass
(serde_json maps keep one value). That is a new project language, which R8 already flagged as needing
its own decision beyond D107. Not recommended.

Best reflection-capable option: none exists; no library found uses P2996 to validate against an
arbitrary JSON Schema. The design's reflection parity test (member names equal schema `properties` and
`required`) covers the reflection side.

## 3. SHA-256

| Option | Where | API facts | P2996 | Licence and maintenance | Verdict |
|---|---|---|---|---|---|
| CommonCrypto | macOS SDK 27.0 (`OFF/receipts/probe/host-probe-compilers-sdk.txt`) | `CC_SHA256`, `CC_SHA256_Init/Update/Final` marked `API_AVAILABLE(macos(10.4))`, not deprecated (`MacOSX27.0.sdk/usr/include/CommonCrypto/CommonDigest.h:193-206`); the MD2, MD4 and MD5 functions carry `API_DEPRECATED` (`:81-143`); `CC_LONG` is `uint32_t` (`:63`), so hash files through `Update` in chunks; man page `OFF/pages/apple-cc-sha-man.md` | n/a | OS built-in, in libSystem | Use on macOS (D107) |
| OpenSSL `EVP_Digest*` | Linux distro libcrypto; Homebrew `openssl@3` is also present on this Mac; VCPKG `openssl` 3.6.5 | `OFF/pages/openssl-evp-digest.md` | n/a | Apache-2.0 | Linux route once a Linux reflection build exists (R8: the OCI image has GCC 12) |
| Linux kernel AF_ALG | `socket(AF_ALG)` with `"sha256"` | `OFF/pages/linux-af-alg.md` | n/a | kernel | The only true Linux OS built-in; container seccomp behaviour UNVERIFIED |
| picosha2 | VCPKG 1.0.1, single header | Releases v1.0.0 (2017-07-30) and v1.0.1 (2025-05-04) only; `-Wsign-conversion` errors open since 2018 (okdshin/PicoSHA2#18), fix PR #28 open since 2026-03-31 | No | MIT, single maintainer | Not needed once CommonCrypto is used |
| hash-library, Crypto++, Botan, libsodium | VCPKG 8, 2026-03-02, 3.12.0, 1.0.22 | not analysed | No | various | Heavier than needed |

The 59a0 smoke test ("SHA-256 of abc matches the NIST vector") applies unchanged to a `sha256()` seam
with a CommonCrypto implementation. No reflection relevance.

## 4. Can glaze replace the hand-written codec, and how that meets D83

What glaze gives (all cited to `OFF/repos/stephenberry_glaze`): reading and writing aggregates without
metadata in C++23 mode, with P2996 as an alternative backend and "the entire Glaze API remains
unchanged" (`docs/p2996-reflection.md:3-24`; R8 section 3); unknown keys rejected by default
(`include/glaze/core/opts.hpp:80`); required keys with `error_on_missing_keys` plus a per-type
`requires_key(key, is_nullable)` hook (`docs/field-validation.md:5-28,50-70`); strict number reading (NaN
is an error, section 1); enum strings through `reflect_enums` under P2996 (`docs/p2996-reflection.md:227-279`);
raw JSON passthrough for the opaque native objects (UNVERIFIED for the exact type name, `glz::raw_json`).

What it does not give:
- Duplicate-key rejection (section 1). The jsoncons visitor pass runs first anyway, because validation
  needs a `jsoncons::json`; glaze then reads the same bytes into the record. Envelope, request and report
  files are small, so the second parse is cheap.
- Missing versus null as the design defines it (`accepted-decisions.md:86`). Glaze issue #306 ("Distinguish
  between 'null' and missing keys") was moved to a discussion on 2024-04-22 without a built-in type.
  `Nullable<T>` (always written, null when empty) and `Optional<T>` (omitted when empty) need glaze custom
  read and write specializations plus `requires_key` returning true for `Nullable` members; and
  `skip_null_members` (`opts.hpp:81`) is a whole-call option, so the wrappers must not present themselves
  to glaze as nullable types. Feasible, unproven.
- Symmetric P2996 use across lanes (Verdict item 4). Glaze must be compiled with `-DGLZ_REFLECTION26=1`
  in both lanes. Its docs list `-fexpansion-statements` as required on the Bloomberg fork
  (`docs/p2996-reflection.md:40-50`) and its fork CI passes it (`p2996-reflection.yml:58`), while MP's
  lane flags are `-freflection` only (`CMakeLists.txt:46`); the fork's own documentation makes
  `-fexpansion-statements` a separate flag, bundled in `-freflection-latest`
  (`offline/research/R8-cxx-gate-hooks/repos/bloomberg_clang-p2996/P2996.md:43-53`). The one
  `template for` in glaze's reflection header is inside a GCC-only branch (`include/glaze/reflection/get_name.hpp:107-124`),
  so the flag may be unnecessary; this is exactly what the 59a0 probe must settle.

Compared with the design's codec: the design already proposes a generic reflection codec that walks
`nonstatic_data_members_of` and `enumerators_of` (CT59-design.md section 2, item 4), in the style shown by
`OFF/pages/wrocpp-auto-formatter.md` and `OFF/pages/wrocpp-enum-to-string.md`, and MP's `src/core.cpp`
already compiles that kind of code in both lanes. So the choice is between a maintained library that uses
P2996 (glaze, preferred by D130) and about 200 to 400 lines of project reflection code (UNVERIFIED
estimate) with exact control over the wrapper semantics. Recommendation under D130: glaze for the codec,
with the hand-written `std::meta` codec as the documented fallback if the probe fails in either lane or
the wrappers cannot be expressed. Without D130 the hand-written codec would win on dependency count and
semantic control.

D83 interaction (DL-111: "the committed schema files are the single source ... nothing generates schemas
from C++"): using glaze to read and write records is compatible, since the records still come from the
schema files (#26) and glaze only serializes them. `glz::write_json_schema` must not become a source. It
could feed the CT-53 check as a comparison output after normalization, but R9 records two open glaze
schema divergences (stephenberry/glaze#2508, parse and serialize schemas differ, open since 2026-04-16;
#2656, field wrappers emit a catch-all union, open since 2026-06-20). The design's parity test reads
member names and `required` directly with `std::meta`, which needs no glaze and has no divergence risk;
keep that.

## 5. Test framework

| Framework | VCPKG / latest | Fit for clang-p2996 (libc++) and GCC 16 | Build cost and modules | P2996 | Licence and maintenance |
|---|---|---|---|---|---|
| Catch2 v3 | 3.16.0 / 3.16.1 (2026-10-08) | 3.16.0 carries the Clang 20 and 21 workaround for `TEMPLATE_PRODUCT_TEST_CASE` (catchorg/Catch2#3173, merged 2026-08-20; `docs/release-notes.md:118-146`) and 3.15.0 fixed the GCC 16 C++26 `std::optional` ambiguity from P3168 (#3095; `release-notes.md:188-189`, guard at `src/catch2/catch_tostring.hpp:390`); must be compiled against the same standard library as the tests (#2768), which the per-lane triplets give | Compiled library, `cxx_std_14` (`src/CMakeLists.txt:373-374`), VCPKG builds it as C++17 (`ports/catch2/portfile.cmake:25`): four triplet builds; no module support found | No | BSL-1.0; releases every few weeks |
| doctest | 2.5.3 (2026-07-06) | GCC 16 added to CI (doctest/doctest#1110, merged 2026-05-11) | Header-only, C++11; speed claim disputed for Catch2 v3 users (#1168, open since 2026-06-15) | No | MIT; new maintainers, maintainer call #554 closed 2025-12-31 "project is now maintained" |
| boost-ext/ut | 2.3.1 (2025-04-02) | No GCC 16 or Clang 21 issues found (searches returned only #713) | Single header or module (`README.md:15-19,1453`); VCPKG port disables the module (`BOOST_UT_DISABLE_MODULE=ON`, `ports/bext-ut/portfile.cmake:16`); `import boost.ut` problems #713 (open since 2026-04-09); MP's p2996 lane sets `CXX_SCAN_FOR_MODULES OFF` (`CMakeLists.txt:60`) | No | BSL-1.0; no release for 18 months, commits continue |
| GoogleTest | 1.18.0 | Requires C++17 (`README.md:17`); maintainers declined a workaround for a libstdc++ deprecation warning surfacing in gtest (google/googletest#4935, "We are not doing this", 2026-07-23) | Compiled with gmock; heaviest | No | BSD-3-Clause; active |
| openalgz/ut 1.2.1 | not in VCPKG | Vendored by glaze and compiled in its GCC 16 reflection and clang-p2996 CI (`OFF/repos/stephenberry_glaze/tests/ut/ut.hpp:1-9`, `tests/CMakeLists.txt:20-22`) | Single C++23 header | No | MIT |

None of the frameworks uses P2996 (`OFF/receipts/probe/p2996-usage-counts.txt`: 0 matching files in
Catch2, doctest, boost-ext/ut and GoogleTest). The best "reflection-proven" option is openalgz/ut, the
only one exercised in CI on both reflection compilers, but it is not packaged in VCPKG and is maintained
for glaze's own use. Catch2 v3 stays the choice: it is in the pinned baseline, it has explicit fixes for
both of our compilers in that version, and `catch_discover_tests` integrates with CTest. Doctest is the
fallback if the four-triplet compile cost of Catch2 proves too high.

## 6. CLI parsing (rsm-core verbs: `dispatch`, `status`, `cancel`, `probe`, `smoke`)

| Option | Subcommands and help | P2996 | Compilers | Packaging | Notes |
|---|---|---|---|---|---|
| Hand-written verb switch plus a `std::meta` flag binder | as written | Yes (own code) | both lanes, same pattern as `src/core.cpp` | none | Five verbs with one or two arguments each |
| reflect-cpp `rfl::cli::read<T>` | No subcommands documented; no help generation (getml/reflect-cpp#692 open since 2026-07-14) | Yes in C++26 mode (`docs/content/cpp26_reflection.md:1-45`) | GCC 16.2 or clang-p2996 with `-freflection-latest` | VCPKG 0.25.0 (released 2026-05-16, after the CLI landed in PR #613 on 2026-02-21) | Compiled library with yyjson and ctre (VCPKG deps) |
| reflex `reflex.cli` | Subcommands, help, shell completion (`README.md`) | Yes, P2996 plus P3394 annotations | GCC 16.1 or later only (`README.md:138-141`) | No release tags | MIT, single author, header-only or modules |
| wrocpp clap pattern | Subcommands via `std::variant` | Yes | Tested on clang-p2996 only (`OFF/pages/wrocpp-clap.md:232,292-328`) | Blog code, not a library | Annotation queries are spelled differently on GCC 16.1 and clang-p2996 (`OFF/pages/wrocpp-compiler-support.md:17`) |
| glaze CLI menu | Interactive menu, not argv parsing (`OFF/pages/glaze-cli-menu.md:1-5`) | Yes | both | with glaze | Not a fit |
| nickelpro/cargparse | Yes | No (consteval builder, 0 reflection matches) | C++26, `import cargparse;` only | None | CC0; modules conflict with the p2996 lane's scanning setting |
| CLI11, argparse, cxxopts | Yes | No | any | VCPKG 2.7.2, 3.2, present | Mature |

Best reflection-capable library: reflect-cpp `rfl::cli`, because it is released, packaged and documented
for both compilers; it loses here because it cannot express the verbs or print help and would bring a
compiled dependency for five commands. reflex.cli is the most complete reflection CLI but excludes the
p2996 lane.

## 7. Formatting, logging, process spawning, enum and struct printing

| Need | Option | P2996 | Evidence | Verdict |
|---|---|---|---|---|
| Formatting | `std::format`, `std::print` | No | C++20 and C++23 standard library | Use |
| Formatting | fmt 12.2.0 | No | Already qualified with `find_package(fmt 12.2.0 EXACT)` (`CMakeLists.txt:37`); the installed headers have no `enum.h` (`OFF/receipts/probe/host-probe-retained-installed.txt`) | Use where already wired |
| Formatting | fmt main `fmt/enum.h` | Yes: `enumerators_of` plus `[[=fmt::as_identifiers]]` annotations (`OFF/repos/fmtlib_fmt/include/fmt/enum.h:17-67`) | Unreleased (ChangeLog head is "12.2.1 - TBD"); gated on both standard macros, so off in the p2996 lane; uses the GCC spelling `annotations_of_with_type` | Best reflection-capable formatter; wait for a release |
| Logging | spdlog 1.17.0, quill 13.0.0 | No (0 matches) | VCPKG | Not needed: the CLI writes JSON receipts and stderr lines |
| Struct printing | glaze `write_json`, or one `std::formatter` specialization over `nonstatic_data_members_of` | Yes | `OFF/pages/wrocpp-auto-formatter.md:1-40` | Use whichever codec is adopted |
| Enum strings | own `enumerators_of` helper | Yes | `OFF/pages/wrocpp-enum-to-string.md:20-40`, `OFF/pages/romeo-refl-enum.md` | Use (the codec needs it anyway) |
| Enum strings | glaze `reflect_enums` | Yes | `docs/p2996-reflection.md:227-279` | Use if glaze is adopted |
| Enum strings | enchantum 0.4.0 (VCPKG; 0.5.0 latest) | Partly: P2996 only when `__cpp_impl_reflection >= 202506L` (`include/enchantum/entries.hpp:7,45,418`), so GCC lane only | MIT | Not needed |
| Enum strings | simple_enum 0.9.5, magic_enum 0.9.8 | No (compiler-name tricks) | `OFF/repos/arturbac_simple_enum/README.md` | Not needed |
| Process | `posix_spawn` with `POSIX_SPAWN_SETSID` | n/a | OS built-in; `SETSID` 0x0400 and `CLOEXEC_DEFAULT` in `MacOSX27.0.sdk/usr/include/sys/spawn.h:46,61,62` (`OFF/receipts/probe/sdk-spawn-flags.txt`) | Use (D107; design F3) |
| Process | reproc 14.2.7, Boost.Process v2, sheredom/subprocess.h | No | reproc uses `fork()` (`reproc/src/process.posix.c:216`); Boost.Process v2 default launcher uses `fork()` and offers `vfork` (`include/boost/process/v2/posix/default_launcher.hpp:362`, `vfork_launcher.hpp:93`); subprocess.h uses `posix_spawn` | Not needed |

## 8. Admission needed and risk list

Admission (one recorded operation, D86 heavy-run rules apply):
1. Manifest hunk: add `jsoncons`, `catch2` and, if the codec decision takes glaze, `glaze` to `vcpkg.json`
   (`vcpkg.json:5-7` lists only `fmt`). The pinned baseline gives jsoncons 1.9.0, Catch2 3.16.0 and glaze
   9.0.0; `accepted-decisions.md:44` asks to check latest stable and lock exact versions, so either accept
   the baseline versions (1.9.0 is safe for `jsonschema`; #738 is in the toon extension only) or add
   `overrides` for jsoncons 1.10.0 and Catch2 3.16.1 (UNVERIFIED that the baseline's versions database
   already has them).
2. One network fetch through the retained vcpkg (`docs/vcpkg-toolchain.md`) into the four retained
   triplet trees (`arm64-osx-{gcc16,p2996}-{static,dynamic}`; today they hold only fmt 12.2.0,
   `OFF/receipts/probe/host-probe-retained-installed.txt`). jsoncons and glaze are header-only installs;
   Catch2 compiles four times.
3. A compile probe in both lanes with MP's exact flags (`-std=c++26 -freflection -pedantic-errors -Wall
   -Wextra -Werror`): include `jsoncons_ext/jsonschema/jsonschema.hpp`, glaze with
   `-DGLZ_REFLECTION26=1` (with and without `-fexpansion-statements` in the p2996 lane), and Catch2's
   `catch_test_macros.hpp`, consumed as imported targets so CMake treats their include directories as
   system (`OFF/pages/cmake-no-system-from-imported.md:7`). GCC suppresses warnings in system headers
   but not always in macros from them that expand in our code (`OFF/pages/gcc-system-headers.md:7`), so
   the probe must expand `REQUIRE` and a glaze read in a TU, not just include headers.
4. CommonCrypto needs no admission; it links from libSystem.

Risks:
- R1. Bowtie measures jsoncons 0.177.0, not 1.9.0 or 1.10.0, and jsoncons's own runner skips seven
  required 2020-12 files. Mitigate with the suite run in 59b for the keywords in use.
- R2. jsoncons accepts comments by default (`json_options.hpp:261`) and drops duplicate keys silently;
  forgetting `allow_comments(false)` or the visitor pass breaks the strictness contract. Make both one
  function and test them first.
- R3. Reflection backend asymmetry: glaze, fmt `enum.h` and enchantum enable P2996 only in the gcc16 lane
  unless forced (Verdict item 4); annotation queries are spelled differently on the two compilers
  (`wrocpp-compiler-support.md:17`). Pin `GLZ_REFLECTION26=1` and test both lanes.
- R4. Fork defects: clang-p2996 has open Sema use-after-free (#288) and large-pack miscompile (#323)
  issues (R8 section 1); a template-heavy library raises exposure. glaze's fork CI uses the public
  `vsavkov/clang-p2996` image, not our `f17c8d6` build.
- R5. Missing versus null in glaze needs custom wrappers (#306 unresolved); if they fail, fall back to the
  hand-written codec.
- R6. Catch2 must be built with libc++ for the p2996 lane (#2768); a triplet mix-up gives link errors,
  not compile errors.
- R7. Licence: the 100%-compliant C++ validators (Blaze, IRIS) are AGPL-3.0; MP has no licence. Using them
  needs a user decision (or a Blaze commercial licence).
- R8. Linux: none of this builds in the OCI image (GCC 12, R8); the SHA-256 Linux route and the Linux
  triplets are deferred with it, per the support matrix (`accepted-decisions.md:57-59`).
- R9. picosha2 rejection rests on maintenance and warnings, not on a measured defect.

## Code examples found

- jsoncons resolver mapping URIs to files: `OFF/repos/danielaparker_jsoncons/doc/ref/jsonschema/jsonschema.md:153-170` (commit `d273865`).
- jsoncons Bowtie harness with a URI resolver: bowtie-json-schema/bowtie#1815 (merged 2025-02-07), `OFF/gh/bowtie-json-schema_bowtie_1815.json`.
- nlohmann duplicate-key rejection by parser callback: `OFF/repos/nlohmann_json/docs/mkdocs/docs/features/parsing/parser_callbacks.md:94-111` (commit `7461a19`), example `docs/mkdocs/docs/examples/reject_duplicate_keys.cpp`; the same visitor idea ports to jsoncons `basic_json_visitor` (`OFF/repos/danielaparker_jsoncons/doc/ref/corelib/basic_json_visitor.md`).
- glaze P2996 detection and enum table: `OFF/repos/stephenberry_glaze/include/glaze/core/feature_test.hpp:17-28`, `include/glaze/reflection/get_name.hpp:96-124` (commit `e194d23`).
- glaze strict NaN tests: `OFF/repos/stephenberry_glaze/tests/json_test/json_test.cpp:4761-4787`.
- reflect-cpp CLI: `OFF/repos/getml_reflect-cpp/docs/content/supported_formats/cli.md:1-60` (commit `fc1c3fe`).
- reflex annotated CLI: `OFF/repos/Garcia6l20_reflex/README.md` "Taste of the API" (commit `075e376`).
- fmt reflection enum formatter: `OFF/repos/fmtlib_fmt/include/fmt/enum.h:17-140` (commit `b4ffa39`).
- Reflection aggregate formatter and enum-to-string: `OFF/pages/wrocpp-auto-formatter.md`, `OFF/pages/wrocpp-enum-to-string.md`.
- Clang-p2996 versus GCC detection in MP: `src/core.cpp:6-11`.

## Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 0 | Repo and design reads | `cat`, `grep`, `sed` over the brief, CT59-design, R8, R9, accepted-decisions, CMakeLists, vcpkg.json, docs/vcpkg-toolchain.md | 0 | n/a | yes |
| 0 | Host probes | `ls` of the retained vcpkg tree and its four triplet trees; reads of VCPKG `ports/*/vcpkg.json` and `portfile.cmake`; `clang++ --version` (fork), `g++-16 --version`, `/usr/bin/clang++ --version`; `grep` of SDK `CommonDigest.h`, `sys/spawn.h` and the two installed standard libraries | 0 (the two greps for absent symbols rc 1, recorded) | `OFF/receipts/probe/*` | yes |
| 1 | Exa | `fnox ... exec -- run_exa.sh` (curl POST api.exa.ai/search, key from env via `curl -K -`), 32 queries | 0, HTTP 200 x32 | 10 each | yes: seeded Bowtie, valijson PR #234, nlohmann #5259, jsoncons #504/#505/#549, glaze #306/#1716, Catch2 #3173/#3076, googletest #4935, doctest #554/#1168, ut #713, wrocpp posts, reflex, cargparse, reflect-cpp26 |
| 1 | Context7 | `fnox ... exec -- ctx7 library <jsoncons|glaze|catch2|valijson> <query>` | 1 x4 | "Monthly quota reached" | no, gap |
| 1 | Firecrawl | `fnox ... exec -- firecrawl search ... --json`; `firecrawl scrape https://bowtie.report/ --format markdown` | 1, 1 | HTTP 402 insufficient credits | no, gap |
| 1 | webclaw | `webclaw <url> -f markdown`, 39 pages | 0 x37, 1 x2 | `ut-quickstart` empty (rc 1), `boost-json-parse-options` empty (rc 1), `lemire-cppcon2025-slides` 111 bytes and `reddit-reflection-cli` 238 bytes are placeholders | yes, placeholders not cited |
| 1 | Bowtie data | `curl -sS -L -o <file> https://bowtie.report/{implementations,draft2020-12}.json` (public data files the frontend fetches, `frontend/src/data/Dialect.ts:47-51`) | 0, HTTP 200 | 33,662 and 61,327,135 bytes | yes, scored locally |
| 1 | Serper | `fnox ... exec -- run_serper.sh` (POST google.serper.dev/search, key from env), 6 queries | 0, HTTP 200 x6 | 10 each | corroboration: Blaze licensing page, jsoncons #618, reflect-cpp CLI threads |
| 1 | Last30Days | `fnox ... exec -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py "<topic>" --plan plan.json --emit json --quick --save-dir "" --no-browser-cookies` | 0 | 12 items, all off topic; grounding "error" | no, gap |
| 2 | gh issue and PR views | `gh issue view N --repo R --comments --json ...` (falls back to `gh pr view`), 41 items | 0 x38, 1 x3 (discussions) | see `OFF/gh` | yes |
| 2 | Discussions | `gh api graphql` `repository.discussion(number)` for jsoncons #557, #596, glaze #1982; `search(type: DISCUSSION)` x2 | 0 | 19 and 47 discussions | yes |
| 2 | gh search issues | `gh search issues "<term>" --repo <r> --include-prs --limit 15`, 24 queries (jsoncons, glaze, Catch2, doctest, ut, picosha2, bowtie, Blaze, valijson, reflect-cpp) | 0 x24 | 0 to 15 | yes where non-zero |
| 2 | gh release list | `gh release list --repo <r> --limit 5`, 13 repositories | 0 | `OFF/gh/releases` | yes |
| 2 | gh search repos | `gh search repos implementations --owner bowtie-json-schema` | 1 | HTTP 403 secondary rate limit | no; replaced by PR #3000 |
| 2 | Clones | `git clone --depth 1 --filter=blob:none --no-tags <url>`, 31 repositories | 0 x31 | commits in manifest | yes |
| 2 | Saved-search reproduction | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5`, each with control `README repo:<repo>`, 7 s apart | 0 x12 | below | yes |

Incident: running `cd` into the Bowtie clone triggered this host's global mise Python auto-venv, which
created an empty `.venv` (only the virtualenv bootstrap files) inside the clone. No clone code ran; the
`.venv` was deleted and later commands used absolute paths only.

## Proposed saved-search rows

Reproduced read-only into `OFF/receipts/saved/`; do not edit `dev/saved-searches.toml` from this report.

```toml
[[search]]
id = "jsoncons-schema-resolver"        # 12 hits; control README 4
query = "make_json_schema resolver"
repo = "danielaparker/jsoncons"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "jsoncons-allow-comments"         # 8 hits; control 4
query = "allow_comments"
repo = "danielaparker/jsoncons"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "glaze-write-json-schema"         # 10 hits; control 5 (R9 proposed it without a completed control)
query = "write_json_schema"
repo = "stephenberry/glaze"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "catch2-optional-range"           # 1 hit; control 32
query = "__cpp_lib_optional_range_support"
repo = "catchorg/Catch2"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "reflectcpp-cli-read"             # 17 hits; control 41
query = "\"cli::read\""
repo = "getml/reflect-cpp"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

`GLZ_REFLECTION26 repo:stephenberry/glaze` (15 hits, control 5) was also reproduced; R8 already proposed
it as `glaze-reflection26`.

## Open gaps

- No compile was allowed, so "builds in both lanes with `-Werror -pedantic-errors`" is unverified for
  every library; the admission's probe (section 8, item 3) is the deciding test for glaze and Catch2.
- jsoncons compliance at 1.9.0 or 1.10.0 is unmeasured (Bowtie runs 0.177.0).
- Whether glaze needs `-fexpansion-statements` on our fork build, and whether its custom wrappers can hold
  the missing versus null contract, are unverified.
- Whether the baseline `e456309` versions database lists jsoncons 1.10.0 and Catch2 3.16.1 was not
  checked (only `ports/` was read).
- Context7 monthly quota exhausted (4 calls); Firecrawl HTTP 402 (2 calls); Last30Days returned nothing on
  topic with grounding in error; one `gh search repos` call hit the secondary rate limit.
- Linux SHA-256 route (OpenSSL versus AF_ALG in containers) is not decided; AF_ALG under container
  seccomp is UNVERIFIED.
- The size estimate for a hand-written codec (200 to 400 lines) is UNVERIFIED.
- Blaze commercial-licence terms and price were mirrored (`OFF/pages/sourcemeta-commercial.md`) but not
  analysed.
