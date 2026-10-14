# Accepted decisions for the marketplace takeover

This record consolidates the user's decisions from the originating chat as of 2026-10-10. It supersedes conflicting recommendations in the earlier audit and source prompt; it does not rewrite those historical sources.

## Product and migration

- Keep /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace as the project home and retain its repository name.
- The final shared research core is native C++26 using P2996 static reflection. Earlier shared-design/audit recommendations for a permanent Python core are superseded.
- Migrate incrementally: initially bridge the existing Python library into C++, retain behavior comparisons, and replace features/modules/functions one at a time. Context7's JavaScript SDK may be bridged similarly. Choose embedded versus helper-process placement from measured prototypes, not an assumed winner.
- Research tooling is the first product baseline. SBE/firmware work is a later phase, potentially a separate repository; the old ai-agent-setup-prompt.md is a reference to refine, not an instruction to install daemons or unpack unverified archives.
- Preserve existing Claude aggregated-research plugin name, CLI behavior and data-path compatibility while migrating its backend.
- Generate host-specific thin adapters for Codex, Claude, Antigravity and OpenCode against their actual installed-version contracts. OpenRouter is an optional inference route/app-attribution surface, not an assumed research-plugin installer.
- Keep provider, route, upstream, capability, corpus, artifact and model identities separate. Models/contracts are per research operation, with typed tagged batch envelopes preserving call IDs, attempts, failures, usage and provenance.
- Default retrieval/parsing/dedup/cache/coverage evaluation runs without a model. Optional inference records its real route/model/usage and unknown cost honestly.
- Require primary evidence and at least two independent upstreams or corpora for material comparisons after deduplication. Exa inside Last30Days is not another upstream; Serper/SerpApi share a Google corpus. Keep raw history immutable. A replacement may satisfy a plan need only with explicit capability/corpus evidence.
- The PDF date-update feature and patient/document bytes are excluded. Its research aggregator and generated plugin are candidate consumers after this foundation; this is not permission to edit that other checkout. Private uploads require a per-run destination choice. Mutating tools belong in an explicit opt-in profile.
- Global Python interpreter promotion and local OpenTelemetry Collector work are separate accepted streams. Carry forward their ownership boundaries; do not absorb or duplicate them in marketplace onboarding.

## Automation and observability clarification (2026-10-12)

- Humans, coding agents and CI/CD use the same named mise tasks with the same
  parameters. Repeatable operations belong in reusable Python/C++ library
  code behind those tasks, reached by thin host-specific skills. Direct
  read-only inspection and native agent communication are allowed; manual
  operational commands must not replace the repeatable automation.
- All Python invocations and CMake build operations go through named mise
  tasks. Declare the minimal Python support and its dependencies in project
  `pyproject.toml` and mise dependency configuration. The project must build
  without relying on user/global mise configuration. Prefer moving reusable
  implementation into the C++26 reflection core as it becomes qualified.
- C++ namespaces use `com::rsm::<module>`. Dotted module/package identifiers
  may use `com.rsm.<module>`; dots are not C++ namespace separators.
- Check latest stable dependency releases during each update unit, then lock
  exact versions/source identities and qualify them before adoption. A new
  reflection-fork revision is a qualification candidate, not an automatic
  replacement for an established compiler/runtime witness.
- Default telemetry is structured output in a directory, with secret/content
  redaction. Integrate available native Claude, Codex and Antigravity signals.
  Use one shared OpenTelemetry Collector on the Mac, owned by user/global mise
  under `~/.config/mise/`; projects add support there when needed instead of
  creating their own collector. Remote export requires a selected destination.
  This clarification does not establish current collector or host-signal
  availability. Write under `~/.local/state/otel/`, separated by service and
  project, with rotation and configurable retention defaulting to 30 days.
  Signal-specific acceptance remains to be qualified.
- Cover macOS ARM64, Linux ARM64 and Linux x86-64 in the generated support
  matrix. Report unsupported combinations explicitly; upstream availability
  and compilation alone do not establish runtime qualification.
- Run relevant fast formatting, lint and schema checks in hk pre-commit,
  including cmake-format. Post-commit verifies and records without changing
  committed files. Expensive compiler, sanitizer and Valgrind checks use
  explicit pre-push/CI profiles through the same named mise tasks.
- Use official in-file schema declarations where valid, otherwise external
  association and exact-version native validation. Prefer Codex release
  schema assets matching the installed version. Keep config, hook-file and
  hook-protocol schemas distinct; unsupported extra fields must not be added.
- Build the project-owned, locked GitHubKit saved-search/replay task before
  further build-design implementation. Compare reusable behavior from
  knowledge-base, dotfiles and `test.results.20260929` without changing those
  projects. Use the unified task to find Codex release-schema usage examples.
- Amend spec #11 and its existing dependency graph. Version intentional
  acceptance-baseline transitions with reviewed compatibility checks; retain
  the original 19-file preservation receipts and completed-unit evidence.
- Combine native blocking hooks for supported calls, read-only command-guard
  review and CI checks of the shared mise commands. Document and test each
  host's coverage; do not claim every action can be intercepted.
- The unified GitHubKit task must pass deterministic offline replay, saved
  query/provenance, pagination and rate-limit tests plus a bounded live
  Codex-schema search. Unexpected empty results use a bounded same-capability
  known-result control; a failed control yields unverified, not a success.

## Native data and runtime design

- Canonical common schemas initially feed the existing Python generator and the C++ candidate; preserve datamodel-code-generator as a baseline and gap detector until behavior parity. Eventually replace that functionality in C++26.
- Generated request/result/domain records must be strict POD-style records. Owners may use RAII. Preserve missing versus null explicitly; use pointer/length or pointer/count views with externally owned lifetime.
- Research existing schema/generator extension points before writing a custom frontend. Quicktype's C backend and Chaotic are qualification candidates; generated defaults/std::optional/cJSON numeric semantics are known adaptation concerns, not accepted behavior.
- Prefer a single-thread event loop by default; the investigated baseline is libuv. Add bounded SPSC queues for explicit worker pairs or a qualified bounded MPSC mechanism only when parallelism is needed.
- Use reusable storage for dynamic strings/types. The investigated baseline is engine-owned std::pmr::unsynchronized_pool_resource, with optional per-request monotonic arenas. Recycle only after the final borrow acknowledgment, not merely cancellation or queue removal.
- Those library/runtime recommendations need focused prototypes and remain downstream of the build foundation; onboarding does not implement them.

## Compiler and build foundation

- The earlier qualified host setup used global mise installations and named p2996/gcc16 profiles. Portable project declarations and tasks now supersede reliance on those global profiles; retain their historical receipts and preserve the default compiler for unrelated work. The shared Mac collector remains explicitly owned by global mise.
- Latest stable GCC is the intended GCC lane; the inspected starting point is 16.2.0 via native mise Homebrew bootstrap. Re-attest actual package identity/patches at installation.
- P2996 LLVM and its libc++/runtimes use an exact fork commit. Build IWYU against the exact fork Clang libraries/headers, not merely the same major.
- Starting identities: LLVM f17c8d6c7bfef5e02ccadcf33517fd2a53b51b6e; IWYU clang_21 791e69ea4662cb3e74e8128fd5fd69bd7f4ea6b3; CMake 4.4.4; Ninja 1.13.2; sccache 0.18.0; vcpkg e456309491fd875487bf02b8a0dca76c1b1b00cc. Verify before install and preserve source/runtime provenance.
- Modern CMake Ninja Multi-Config presets cover both compilers, four standard configurations, static/shared linkage, and supported sanitizer/coverage permutations. Project and dependency linkage are independently represented in the current inclusive matrix: 8 baseline trees / 32 cells; 96 candidate trees / 384 cells before runtime qualification.
- Use separate per-compiler CMake toolchains; vcpkg remains CMAKE_TOOLCHAIN_FILE and chainloads the matching compiler toolchain in both the application and overlay triplets. Pin tool checkout and registry baseline separately; qualify compiler/stdlib parity, host-tool identity and binary cache invalidation.
- Produce both conventional CMake Config and native CPS exports from one target model. Qualify isolated relocated consumers for every admitted linkage/configuration family. Native install(PACKAGE_INFO) is supported in the selected CMake; old experimental UUID advice is superseded.
- Reuse aminya/cpp_vcpkg_project/project_options, Lukka's explicit Multi-Config presets, native Kitware CPS fixtures, and evaluate TCPM for matrix generation. These are source-backed candidates, not runtime-qualified installs.
- Include IWYU, clangd/format/tidy/static analysis, native coverage, cppcheck and cache qualification as small tasks. Linux-only tools such as Valgrind/perf are later platform-specific work, not false macOS successes.
- Keep each implementation/review/check unit small enough for a fresh context; the cold LLVM build and full matrix are durable logged operations, not giant implementation prompts.

## Source precedence

1. Latest direct user decisions in the originating chat and this consolidated record.
2. Current reuse-and-preset-matrix.md and task prerequisites.
3. Prior shared-design.md / marketplace-design-addendum.md for non-conflicting accepted policies.
4. Read-only audit findings and primary evidence, preserving their original status.
5. ai-agent-setup-prompt.md / NotebookLM material as reference, with stale versions/claims superseded.

The NotebookLM browser read succeeded after the user logged in. The earlier CLI/auth path and archive download did not establish a usable cpp-utilities.zip. Do not claim that archive was downloaded or unpack it without verifying its existence and provenance.
