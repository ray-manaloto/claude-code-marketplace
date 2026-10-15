# R9: bridges from the C++ core to Python and to TypeScript mods (research, 2026-10-14)

Written by research subagent R9 of session `ccm-20261014` (`ce9c0b3d`), read-only except this file and the
untracked mirror `offline/research/R9-cxx-bridges/` (called OR below; `manifest.json` lists every item with
URL, local path, UTC fetch time, command shape, exit code and SHA-256 or commit). MP at `21af565`, branch
`codex/marketplace-native-onboarding`. Claude Code 2.1.299 (`claude --version`); its binary carries the string
`Bun v1.4.3 (macOS arm64)` (OR/local/host-claude-2.1.299-bun-version.txt). P =
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. d.ts = the engine-written mods declarations of
2.1.296 (newest on disk), copied to OR/local/cc-2.1.296-claude-code.d.ts (sha256 `70e95eda...`).

Read first: the shared research brief, AGENTS.md, docs/accepted-decisions.md, docs/build-roadmap.md,
docs/agents/hooks-and-mods.md, P/reviews/ccm-20261014/project-import/A2-typescript-mods-library.md, and in
P/decisions.jsonl the rows for D60 (DL-61, DL-75), D83 (DL-111), D92, D100, D102, D107 and D110. Also
docs/core-qualification.md and P/reviews/ccm-20261014/research5/gate-timing-receipt.md (cited as "receipt").
R8 (`research5/R8-cxx-gate-hooks.md`, cited as R8) landed while this run was under way; its verdict,
section 2 (bootstrap) and its scratch host probes (cited as R8-probe N, session scratchpad
`research5/R8/host-probe-N*.txt`) were read, and nothing in its scope (compilers on macOS arm64, compiled
deny-gate hooks) was redone.

Standing direction applied throughout: one modern C++ library using P2996 wherever possible; Python and
TypeScript remain only as thin bridges that call it; no new Python logic; Claude Code mods sit on a bridge to
the C++ library.

## Verdict

Recommendation: one C++26 core library (`com::rsm`), reflection private to its own translation units as
`src/core.cpp` already does, with two bridge surfaces:

1. Default for both languages: one native CLI over the library (working name `rsm-core`) that reads one JSON
   request on stdin and writes one JSON result on stdout, exit 0 for success, 2 for a refusal with a JSON
   reason, anything else a failure (the contract A2 section 2.14 already fixes for tasks). Message shapes come
   from the D83 schema files. Mods call it with `$.process.run`; the D60 Python package calls it with
   `subprocess`; the D102 settings-hook gates can call it too (R8 decides). A `serve` mode, HTTP over a Unix
   socket started once per session by the mod (`$.process.spawn` in `session.start`) and reached with
   `$.http.fetch(url, { socketPath })`, is added only for a feature whose measured p95 misses its budget.
2. A C ABI waist (`extern "C"`, POD records with pointer and length views, which docs/accepted-decisions.md:75
   already requires of generated records) for in-process consumers. Python gets a nanobind module over it only
   when a measured prototype admits one (docs/accepted-decisions.md:9: "Choose embedded versus helper-process
   placement from measured prototypes"). TypeScript mods cannot load native code at all today.

Confidence: high for the TypeScript side, medium for the Python side.

Evidence that decides it:
- A hooks module "runs in an environment of its own: no DOM, no Node", ES modules only, no `require`, and "a
  module holding `import()` does not load" (d.ts:15-25); "there is no `WebAssembly` (deliberately; a module
  that needs compiled code runs it in a process of its own through `$.process.run`)" (d.ts:14746-14750; the
  same sentence is in upstream OR/repos/claude-code-sparse/mods/types/claude-code.d.ts:11573). Node-API addons,
  `bun:ffi` and WebAssembly are therefore all unreachable from a mod, and a child process, or a socket to one,
  is the only native route. An Anthropic contributor called `$.process.run` "our intended escape hatch" and
  suggested a local daemon reached through `$.http.fetch` (poteat, anthropics/claude-code#91870, comment of
  2026-09-06; OR/gh/v-anthropics_claude-code-91870.json).
- On this host a compiled binary launches in 2.5 ms median and 3.5 ms p90, the venv Python with `-I` in
  26.5 ms and `uv run` in 40.4 ms (receipt:12-16). A C++ CLI per call costs about a tenth of today's Python
  path, so the subprocess route is cheap enough to be the default.
- One CLI serves both languages, needs no Python headers, no wheel tags and no compiler during `uv sync`, so
  D60's `uv run --no-sync --offline python -I -m` keeps working unchanged.
- How the binary is started matters as much as the language: R8 measured a direct exec at 2.43 ms against
  5.81 ms through `sh -c`, and 186.2 ms per `git` call that resolves to the global mise shim (R8 verdict item 1
  and section 2). `$.process.run` takes an argv with no shell, so hot paths should name the built binary
  directly rather than go through `./dev/mise run`; A2-0 arm 7 has to measure the difference.
- Python is medium confidence only because the accepted decision above forbids assuming the winner between an
  embedded module and a helper process; the CLI is the right default, not a measured winner for every call
  rate.

## 1. C++ to Python

### 1.1 Binding routes

- nanobind. Bindings "compile up to ~4x faster", give "~5x smaller binaries" and "~10x lower runtime
  overheads compared to pybind11", and a bound call costs less than a CPython function call
  (OR/pages/nanobind-benchmark.md:7, 51; https://nanobind.readthedocs.io/en/latest/benchmark.html). It targets
  the stable ABI from Python 3.12, or 3.10 in split mode (OR/pages/nanobind-why.md:46), through the CMake flag
  `STABLE_ABI` (OR/repos/nanobind/docs/api_cmake.rst:57-74), and its packaging guide sets
  `wheel.py-api = "cp312"` under `[tool.scikit-build]` (OR/pages/nanobind-packaging.md:120-128). Costs of the
  stable ABI: slower dispatch and a frozen 3.12 feature floor (OR/pages/nanobind-split-mode.md:30-36); split
  mode (nanobind 3.0+) ships one frontend wheel per platform for 3.10 and later with a per-version backend from
  PyPI (same file :45-55). nanobind itself stays C++17 (`cxx_std_17`,
  OR/repos/nanobind/cmake/nanobind-config.cmake:567), and the free-threaded `abi3t` tag of Python 3.15
  (PEP 803, OR/pages/cpython-c-api-stable.md:51-58) is intentionally not supported yet (wjakob/nanobind#1404,
  opened 2026-07-28, closed 2026-08-18).
- pybind11. No released stable-ABI support: a roadmap (pybind/pybind11 discussion #6104, 2026-07-22,
  OR/gh/disc-pybind11-6104.json) and an open PR adding abi3 and abi3t (pybind/pybind11#6198, 2026-10-08).
  Until then one wheel per Python version and platform, with the heavier build and runtime above.
- The CPython C API directly. mirror_bridge's Python backend includes `<Python.h>` and builds the type
  objects itself, with a `Py_LIMITED_API` branch (OR/repos/mirror_bridge/python/mirror_bridge_python.hpp:48,
  419). Most control, most code; abi3 only by keeping to the limited API by hand.
- A C ABI with ctypes or cffi. A shared library installed beside the package works on every Python version
  because "the library does not touch the Python ABI"; the cost is finding and loading it yourself
  (OR/pages/skbuild-ctypes-guide.md, scikit-build-core "Shipping a library for ctypes"). ctypes goes through
  libffi and is the slowest per call (anecdotal "100x slower than e.g. Rust",
  OR/pages/hn-ctypes-overhead-31378277.md:38; HN item 44313853). cffi's ABI mode "will crash if you call some
  function or access some fields of a structure that was slightly misdeclared"; its API mode is faster but
  needs a C compiler (OR/pages/cffi-overview.md:87-126).
- A CLI subprocess with a JSON protocol. No Python build coupling; each call pays one process start (2.5 ms
  floor above) plus JSON parsing.

### 1.2 Build and packaging with uv

- uv scaffolds extension projects only with `maturin` or `scikit-build-core`
  (`uv init --build-backend scikit-build-core`) and then sets `tool.uv.cache-keys` to common source types;
  changes outside them need `--reinstall` (OR/pages/uv-projects-init.md:215-239, 313). By default uv rebuilds a
  local project only when `pyproject.toml`, `setup.py` or `setup.cfg` changes or `src` appears
  (OR/pages/uv-cache.md:35). Open upstream: astral-sh/uv#15809 (sync and run do not rebuild a
  scikit-build-core package on source changes, 2025-09-12), #14383 (editable rebuilds with scikit-build-core
  do not work, 2025-07-01), PR #21488 (editable installs not rebuilt when generated files are deleted,
  2026-09-06), #20090 and #21367 (reusable build environments for native backends). meson-python has no
  `uv init` template (#21553, #16093) and an open editable-install issue (#10214).
- scikit-build-core editable installs: rebuild-on-import "is still experimental" and wants a persistent
  `build-dir` (OR/pages/skbuild-editable.md:8, 16-21); on Python 3.15 it emits PEP 829 `.start` files (:42).
- Wheels: one per OS and architecture is unavoidable; abi3 removes the Python-version axis from 3.12, split
  mode from 3.10. MP's matrix is macOS ARM64, Linux ARM64 and Linux x86-64 (docs/accepted-decisions.md:46), so
  three wheels per release, or three CLI binaries on the CLI route.
- Cold start here: venv Python `-I` 26.5 ms median; `uv run` adds 9 to 14 ms; a new venv on a warm cache
  0.26 to 0.33 s; an empty cache with `UV_OFFLINE=1` fails (receipt:12-26). The import time of a nanobind
  module was not measured (gap).
- MP today: `pyproject.toml:4` is `requires-python = ">=3.11,<3.16"` and `:8` is `package = false`; a cp312
  abi3 wheel would drop 3.11.
- When the native build is missing: an extension raises `ImportError` on import; ctypes raises `OSError` at
  `CDLL`; a CLI raises `FileNotFoundError` at spawn. Under D60's `uv run --no-sync --offline` nothing is ever
  rebuilt, so a missing or stale extension stays that way until an explicit sync, and the uv issues above mean
  a sync may not rebuild after C++ edits without explicit cache keys. A settings-hook gate under
  `onFailure: block` would block every Bash call (receipt:26).

### 1.3 Projects and papers that generate bindings from P2996 reflection

- mirror_bridge (FranciscoThiesen, Apache-2.0, commit `5cbc100`): Python, Lua and JavaScript from C++26
  reflection with one command (`mirror_bridge generate src/ --module calc --lang all`), reflection-exact `.pyi`
  stubs, an MCP server; "stock GCC 16.1+ (`g++ -std=c++26 -freflection`)" or clang-p2996, P3394 annotations
  on clang-p2996 only (OR/repos/mirror_bridge/README.md:13, 219-242). Its JavaScript backend is Node-API and
  direct V8 (`javascript/`), which a mod cannot load.
- welder (skarndev, MIT, `3ca0c36`): header-only C++26, P2996 plus P3394 annotations, "rods" for pybind11,
  nanobind, sol2 and LuaBridge3 with `.pyi` and LuaCATS stubs; "early proof-of-concept" and "gcc-16 is the
  only compiler" for the papers it needs (OR/repos/welder/README.md:17-29, 141).
- rosetta (MIT, `d805a3d`, 2026-10-08): 20 backends, among them pybind11, nanobind, Node-API, Emscripten
  embind, TypeScript `.d.ts`, OpenAPI 3.1, JSON, MCP and a C ABI for C# and Java; clang-p2996 tested on macOS,
  GCC in progress. "Reflection-free by construction": generation runs once on a reflection host and the
  expanded output builds with "a plain C++17/20 compiler, emsdk, or Qt 6" (OR/repos/rosetta/README.md:45-47,
  98-133).
- pymetabind (bstaletic, Codeberg, `570c3b5`): `pymetabind::bind::class<^^example_type>(m)` for pybind11,
  "GCC 16.1.0", early stage (OR/repos/pymetabind/README.md:1-35). Its author's write-up on a month of
  reflection code: OR/pages/isocpp-staletic-month-reflection.md.
- nanobind `nb::reflect_<^^MyEnum, ^^MyClass, ^^my_namespace>(m)`: a single-header proof of concept on a fork,
  later `matthewkolbe/nanobind26`; wjakob asked about selective binding and compile cost; replies point to
  welder, blacktea/rebind and mirror_bridge (wjakob/nanobind discussion #1314, 2026-03-24 to 2026-10-04,
  OR/gh/disc-nanobind-1314.json).
- Bloomberg: WG21 P2911R0 and R1, "Python Bindings with Value-Based Reflection" (Adam Lach, Jagrut Dave,
  Bloomberg, pybind11, 2023; OR/pages/wg21-p2911r0.md:1, OR/pages/wg21-p2911r1.md:1-20); Callum Piper
  (Bloomberg), "Using Reflection to Generate C++ Python Bindings", ACCU 2025
  (OR/pages/accu2025-piper-reflection-python.md), and "Generating Language Bindings using C++ Reflection",
  CppCon 2026, including CMake integration (OR/pages/cppcon2026-bindings-talk.md:15-29).
- Daveed Vandevoorde: no bindings demo found; the nearest hit is his CppCon 2024 keynote "Gazing Beyond
  Reflection for C++26" (OR/pages/cppcon2024-vandevoorde-keynote.md). Recorded as a gap.
- A compiler hazard for all of them: on clang-p2996, `members_of` silently stops at the implicit tag of
  `extern "C" { typedef struct X X; }`, so "everything after Python.h [is] invisible to reflection"
  (bloomberg/clang-p2996#313, open since 2026-06-10, OR/gh/v-bloomberg_clang-p2996-313.json). A generator that
  walks a namespace in a translation unit including `Python.h` loses declarations with no error. Keep
  reflection in core translation units, never in a binding unit that includes `Python.h`, or build bindings
  with GCC 16.

### 1.4 Options, Python

| Option | Call latency | Build dependency | Fresh-clone behaviour | Packaging | Citation |
|---|---|---|---|---|---|
| P1 nanobind module over the C ABI | In process, below a CPython call; import time unmeasured, after a 26.5 ms interpreter start | CMake, compiler, Python headers, scikit-build-core, nanobind; a reflection compiler only if the binding unit reflects | `uv sync` must compile; under `--no-sync` an `ImportError` until built; C++ edits need cache keys | abi3 cp312 wheel per arch (3), or split mode for 3.10+; no abi3t | OR/pages/nanobind-benchmark.md:7, 51; nanobind-packaging.md:120-128; nanobind-split-mode.md:30-55; wjakob/nanobind#1404; astral-sh/uv#15809 |
| P2 pybind11 module | In process, about 10x nanobind's binding overhead | As P1, slower compile, larger binary | As P1 | One wheel per Python version and arch until #6198 lands | nanobind-benchmark.md:7; pybind/pybind11#6104, #6198 |
| P3 raw CPython C API | In process | Python headers, compiler, most hand-written (or generated) code | As P1 | Per version, or abi3 by limiting to the limited API | mirror_bridge_python.hpp:48, 419; cpython-c-api-stable.md:51-76 |
| P4 C ABI plus ctypes | libffi per call, slowest in-process route (anecdotal figure) | The C++ shared library only | `OSError` at load; a misdeclared signature crashes | One wheel per arch for every Python | skbuild-ctypes-guide.md; hn-ctypes-overhead-31378277.md:38 |
| P5 C ABI plus cffi API mode | Faster than ctypes | A C compiler for the shim plus the library | `ImportError` for the shim | Per version, or an abi3 shim | cffi-overview.md:87-126 |
| P6 CLI subprocess, JSON | About 2.5 ms process floor plus JSON per call | None for Python; the C++ build for the CLI | `FileNotFoundError` mapped to one typed error; uv untouched | Pure-Python wheel plus one CLI binary per arch | receipt:12 |

## 2. C++ to TypeScript for Claude Code mods

### 2.1 The runtime that executes mods

- Claude Code ships as one native binary built on Bun: the npm package "installs the same native binary as
  the standalone installer" and that binary "does not itself invoke Node" (OR/pages/cc-setup.md:454).
  Changelog 2.1.181: "Upgraded the bundled Bun runtime to 1.4"
  (OR/repos/claude-code-sparse/CHANGELOG.md:4525); Jarred Sumner: "Claude Code v2.1.181 (released June 17th)
  and later use the Rust port of Bun" (OR/pages/simonw-claude-code-bun-rust.md;
  OR/pages/bun-blog-bun-in-rust.md). The host binary reports Bun 1.4.3 (header above). Anthropic acquired Bun
  on 2025-12-03 (OR/pages/anthropic-acquires-bun.md:3-5).
- Mods run on that Bun inside a "plugin hooks worker" (changelog entries on its restarts,
  CHANGELOG.md:336, 451, 538), but in a realm with only web globals: no Node APIs, no timers, no network or
  file access of its own (OR/pages/cc-mods-api.md:263), no `eval` or `new Function`, no `WebAssembly`
  (d.ts:14746-14753), and no build step or Node.js needed to load `.js` and `.ts` files
  (OR/pages/cc-mods-create.md:12). In process the dispatch is fast: "keeping it all in-process on Bun is
  extraordinarily fast. we're looking at a p99 of 50us per hook" (poteat, #91870, 2026-09-03).

### 2.2 Can a mod load native code?

- Node-API `.node` addons: Bun supports them through `require()` or `process.dlopen`
  (OR/pages/bun-node-api.md:3-19) and can embed them in `bun build --compile` output
  (OR/pages/bun-executables.md:1092-1103), but a mod has no `require`, no `process` global, and imports only
  its own plugin files (d.ts:15-25). Not available.
- `bun:ffi`: "experimental, with known bugs and limitations. Do not rely on it in production"
  (OR/pages/bun-ffi.md:3); a `bun:` specifier is not a plugin file. Not available.
- WebAssembly: absent "deliberately" (d.ts:14748). The contributor: "re WebAssembly et al, it is in my plans"
  with no date (poteat, #91870, 2026-09-16). A watch item, not a route.
- C++ compiled to plain JavaScript: Emscripten's `-s WASM=0` runs binaryen's wasm2js and adds a polyfill of the
  WebAssembly API (emscripten-core/emscripten#8501, OR/pages/emscripten-pr-8501-wasm2js.md:20-26), and
  `EXPORT_ES6` emits an ES module (OR/pages/emscripten-modularized-output.md:63). The one prior art for this
  exact constraint is jevhooks: Rust routing compiled to wasm, then wasm2js, imported by the mod; "about
  150 KB of optimised wasm becomes about 920 KB of JavaScript", and its author reports that Claude Code
  silently refuses a hooks module over 1,048,576 bytes (OR/pages/jevhooks-mod.md:9-23; third party, the limit
  is UNVERIFIED in Anthropic's docs). For this project the route fails twice: Emscripten uses upstream Clang,
  which has no P2996 (R8-probe 5 and 6: Homebrew Clang 23 ignores `-freflection` and rejects `^^int`), so only
  reflection-free or pre-expanded code could cross; and Emscripten's runtime in a realm without timers or
  `eval` is untested (UNVERIFIED).
- `$.process.run(argv, { cwd, env, stdin, timeoutMs })`: argv only, no shell; resolves
  `{ exitCode, stdout, stderr }` with 4 MiB caps and truncation flags; rejects when the program cannot start or
  outlives the timeout, 30 s by default and 10 minutes at most (d.ts:3505-3522, 8005-8060;
  OR/pages/cc-mods-api.md:280; OR/pages/cc-mods-reference.md:286). Child time does not count against the
  hook's own 10 s budget (cc-mods-reference.md:283).
- `$.process.spawn({ argv, cwd, env, input })`: streams output; the child lives as long as the reading loop
  and dies when the module unloads; its stdin takes one string and is then closed, "A string today; a later
  form may take the text in pieces" (d.ts:3523-3560, 8088-8116). A long-lived helper therefore cannot be driven
  over stdin and must listen on a socket.
- `$.http.fetch(url, { socketPath })`: HTTP over "a Unix domain socket ... one per session, in a private
  directory", path near 100 bytes, 4 MiB bodies, 30 s per call (d.ts:3476-3497, 5238-5249;
  cc-mods-reference.md limits table). The declarations' own example is a session-long `bridge` child with a
  `bridge.sock` (d.ts:3494, 3540-3552).

### 2.3 Sandbox and permission limits

"Mods aren't sandboxed ... a process that a mod starts runs outside" the Bash sandbox
(OR/pages/cc-mods-overview.md:79); a mod acts "with the same permissions as the user" (cc-mods-api.md:263);
managed network controls do not cover "a program the mod starts with `$.process.run`"
(OR/pages/cc-mods-admin.md:83). Every `$` call is an event that a mod earlier in the chain "can observe,
rewrite, or refuse", which is how an organization restricts mods (cc-mods-api.md:283), and
`allowManagedModsOnly` stops user mods entirely (cc-mods-admin.md:26-33). A2's G9 already records that mod
children escape Bash deny rules. Nothing found limits which binaries `$.process.run` may start on an
unmanaged host.

### 2.4 Latency of each route

- In process: p99 50 us per hook dispatch (contributor figure above).
- Compiled child: 2.5 ms median, 3.5 ms p90 on this host, measured from a Python harness (receipt:12); the
  extra cost of Bun's spawn inside a mod is unmeasured (A2-0 arm 7).
- Python child: 26.5 ms (venv `-I`) to 40.4 ms (`uv run`) (receipt:14-16). On Windows one heavy user measured
  86 to 99 ms per Python hook and moved everything into "one resident local server" (deafsquad, #91870,
  2026-09-03).
- Unix-socket helper: one local HTTP round trip per call, unmeasured here (gap). jevhooks reports 116 to
  229 ms per decision, but that includes a remote model call (OR/pages/jevhooks-readme.md:193).

### 2.5 Prior art of mods and plugins calling native binaries

- Anthropic's `diff` mod passes `$.process.run` through a host seam
  (OR/repos/claude-code-sparse/mods/diff/hooks/register.ts:680), the seam A2 2.5 copies.
- ray-amjad/claude-code-mods runs `tail`, `herdr` and `sleep` through `$.process.run`
  (OR/repos/claude-code-mods-ray-amjad/plugins/cache-clock/hooks/register.js:54;
  plugins/decision-tree/hooks/register.jsx:104, 216-219; commit `467b203`); its PR #13 (2026-10-14) records
  the portability cost of shelling out on native Windows.
- jevhooks: a Rust daemon, one per machine on a Unix socket, started by the plugin's MCP server; the mod POSTs
  `/decide` over the socket; one vocabulary crate compiled into both sides; releases ship the prebuilt daemon
  in `plugin/bin` (OR/pages/jevhooks-readme.md:155-199; OR/pages/jevhooks-daemon.md:9-60).
- A Doom mod ran its engine "in a process of its own under bun or node, reached through `$.http.fetch` on
  localhost" because the hooks environment has no WebAssembly (nateschickler0, #91870, 2026-09-15).
- A plugin's `bin/` directory is added to the Bash tool's PATH for every enabled plugin
  (anthropics/claude-code#95653, 2026-09-20, source-level analysis; docs request #42872), the product route
  for a per-arch binary next to the existing `plugins/aggregated-research/bin/` wrappers.

### 2.6 Options, TypeScript mods

| Option | Call latency | Build dependency | Fresh-clone behaviour | Packaging | Citation |
|---|---|---|---|---|---|
| T1 `$.process.run` of the C++ CLI | 50 us dispatch plus about 2.5 ms process floor; Bun spawn overhead unmeasured | C++ only; no Node, no bundler | `process.run` rejects ("can't start"); a gate's `.catch` denies | Binary in the build tree (development) or plugin `bin/` per arch (product) | d.ts:3505-3522; cc-mods-api.md:280; receipt:12; #91870 |
| T2 session helper, HTTP over a Unix socket | One local round trip per call (unmeasured); spawn paid once per session | C++ plus an HTTP-over-socket server (cpp-httplib `AF_UNIX`) | Spawn rejects; fall back to T1 or deny | The same binary, `serve` subcommand | d.ts:3523-3560, 5238-5249; jevhooks-readme.md:155-199; cpp-httplib-unix-socket-raw.md |
| T3 C++ compiled to JavaScript (Emscripten `-s WASM=0`, wasm2js) | In process | Emscripten; no P2996 in its Clang; module size ceiling | Committed generated JS, about 6x the wasm size | A JS file in the plugin | emscripten#8501; jevhooks-mod.md:9-23 |
| T4 WebAssembly in the mod | Not available | n/a | n/a | n/a | d.ts:14748; #91870 (2026-09-16) |
| T5 Node-API addon or `bun:ffi` in the mod | Not loadable | n/a | n/a | n/a | d.ts:15-25; bun-ffi.md:3 |
| T6 Bun or Node sidecar that loads a Node-API addon | As T1 or T2 plus a JS runtime start | C++, Node-API, a second JS runtime | As T1 or T2 | Adds a runtime to ship | bun-node-api.md:3-19 |

## 3. One schema source (D83)

D83: "the committed schema files are the single source; CT-52 generates Python from them, #26 generates the
C++ records from the same files, and CT-53 becomes a P2996 reflection check that those records map back to
identical schemas; nothing generates schemas from C++" (P/decisions.jsonl, DL-111).

- Emitters for the CT-53 check: glaze `glz::write_json_schema<my_struct>()` (OR/repos/glaze/docs/json-schema.md:1-7;
  commit `e194d23`), with a P2996 backend on GCC 16 or clang-p2996 (docs/p2996-reflection.md:26-31) and "pure
  reflection" on C++20 compilers otherwise; reflect-cpp `rfl::json::to_schema<Person>()`
  (OR/pages/reflect-cpp-json-schema.md:33-37; `fc1c3fe`), C++20 by default and a C++26 mode on "GCC 16.2 or
  higher" or clang-p2996 (OR/repos/reflect-cpp/docs/content/cpp26_reflection.md:1-30). simdjson has P2996
  serialization (`SIMDJSON_STATIC_REFLECTION`, OR/repos/simdjson/p2996/README.md:55) but no JSON Schema
  emitter (one unrelated docs hit).
- "Identical" has to mean equal after normalization, because both emitters have open divergences: glaze
  writes different schemas for parsing and for serialization (stephenberry/glaze#2508), field wrappers emit a
  catch-all union (#2656), `long double` does not compile (#2959); reflect-cpp emits `anyOf` where `oneOf` is
  meant for variants (getml/reflect-cpp#375) and handled defaults only from PRs #680 and #681 (2026-06-08).
- Generators from the schema files: quicktype reads JSON Schema and writes C++, TypeScript and Python among
  others (OR/pages/quicktype-typescript.md; already a #26 candidate in docs/accepted-decisions.md:76);
  json-schema-to-typescript 16.x for TypeScript ("Requires Node.js 22.19 or later",
  OR/pages/json-schema-to-typescript.md:87); datamodel-code-generator for Python (the CT-52 baseline,
  docs/accepted-decisions.md:74); native candidates are schemagen, one Go binary emitting TypeScript, Pydantic
  v2 and Go but 3 stars (OR/pages/schemagen.md:20-60), and the Rust crate normalize-typegen (JSON Schema to
  TypeScript, Python dataclasses, TypedDict or Pydantic; OR/pages/normalize-typegen.md:33-35).
- Fit with D83: TypeScript mod types and Python models both come from the schema files, never from C++.
  rosetta's `.d.ts` backend and the `.pyi` stubs of mirror_bridge, welder or nanobind's stubgen generate from
  C++, so they may only serve as drift witnesses, not sources. CT-53 runs on reflection hosts; elsewhere it
  reports itself unsupported, as the accepted decisions require for unsupported combinations.
- The CLI's wire format is exactly these schema shapes, so one schema set types the C++ records, the mod's
  guards, the Python bridge and the JSON on the pipe.

## 4. Recommended architecture

```
schemas/*.json (D83 single source) -> C++ records (#26), TS types for mods, Python models (CT-52)

com::rsm core (C++26, reflection private to core translation units)
  |- extern "C" waist: POD records, pointer and length views
  |     '- later, only if measured: nanobind abi3 module for one Python hot path
  |- rsm-core CLI: one JSON request on stdin -> one JSON result on stdout; exit 0, 2 refusal, else failure
  |     <- mods: $.process.run      <- Python bridge: subprocess      <- hk and settings gates (R8)
  '- rsm-core serve --socket <path>: only for a feature whose measured p95 misses its budget
        <- mods: $.process.spawn at session.start, then $.http.fetch(url, { socketPath })
```

- Protocol tooling: glaze can parse and write the schema-typed records and has a JSON-RPC 2.0 registry that
  dispatches to C++ objects by reflection if a method namespace is wanted
  (OR/repos/glaze/docs/rpc/jsonrpc-registry.md:1-30); `serve` can use cpp-httplib with
  `set_address_family(AF_UNIX)` (OR/pages/cpp-httplib-unix-socket-raw.md).
- Migration: the CLI is the single front door. Operations not yet ported delegate from C++ to the existing
  Python modules as a helper process, keeping the behaviour comparisons the accepted decisions ask for
  (docs/accepted-decisions.md:9); each port removes one delegation.
- Build dependency: CMake 4.4.4, Ninja and a reflection compiler (the qualified P2996 fork, or GCC 16.2 with
  `-freflection`), already qualified for the core across 16 build, test and runtime cells
  (docs/core-qualification.md:25-31). No Python headers, Node or Emscripten.
- Fresh clone: nothing is built. A mod's `$.process.run` rejects because the program cannot start
  (cc-mods-api.md:280), so every gate's `.catch` denies (fail closed, bounded by 1 s, A2 G6) with "core not
  built: run `./dev/mise run core:build`", and observe-only features log and pass. The Python bridge raises one
  typed error with the same text. `uv sync` and `uv run --no-sync --offline` keep working because nothing
  compiles there. A named mise task `core:build` builds the CLI (AGENTS.md rule that CMake builds go through
  mise tasks).
- Bootstrap trap (R8 section 2): a Bash gate that denies every call while the core is missing also denies the
  Bash call that would build it. The mod's door therefore (a) falls back to the existing Python task for any
  gate whose Python implementation still exists (existing code, not new logic), the same launcher-with-fallback
  shape R8 recommends for settings hooks, (b) lets exactly the bootstrap command `./dev/mise run core:build`
  through, and (c) refuses a binary whose embedded source digest does not match the checkout, so stale rules
  are never enforced (R8's staleness proposal, UNVERIFIED cost).
- CI: the Linux OCI image has GCC 12, which cannot compile reflection (R8 verdict item 3, `mise.toml:20-50`),
  so a job that builds `rsm-core` needs a reflection-capable image or the qualified host lane; mods CI stays
  free of it because its tiers stub `process.run`. Prebuilt per-arch artifacts can come through the mise
  `github:` backend with digest and attestation checks once publishing is instructed (R8 section 2, route 3).
- A host without a P2996 compiler, meanwhile: (a) GCC 16.2 from Homebrew already implements `-freflection` on
  macOS arm64, defines `__cpp_impl_reflection 202603L` and ships a libstdc++ `<meta>` (R8-probe 5 and 6; R8
  verdict item 3: on this platform only GCC 16 and the repository's clang-p2996 build compile P2996), and
  mirror_bridge, welder, pymetabind, reflect-cpp and glaze all list GCC 16 as a reflection compiler, so the
  hosts with no reflection compiler are those with only Apple Clang or stock Clang (R8 owns that question);
  (b) such a host can run a prebuilt `rsm-core` for its architecture, pinned by SHA-256, because every bridge
  is reflection-free (publishing a binary is an outward action that waits for instruction); (c) until it has
  one, the fresh-clone behaviour above applies and nothing is reimplemented in TypeScript or Python; (d) if
  bindings are ever generated by reflection, follow rosetta: generate once on a reflection host, commit the
  expanded sources, and let a drift check on that host regenerate and compare (OR/repos/rosetta/README.md:47,
  133).
- When a nanobind module is justified: a Python caller whose call rate makes a 2.5 ms spawn visible, shown by
  a prototype that measures both. Then: scikit-build-core, `STABLE_ABI` cp312 wheels per architecture (three),
  `tool.uv.cache-keys` over the C++ sources, include tree and `CMakeLists.txt`, and a binding unit free of
  reflection (clang-p2996#313).

### 4.1 Effect on the A2 mods-library units

| A2 unit | Change |
|---|---|
| A2-0 | Arm 7 also measures `$.process.run` p50 and p95 of the C++ CLI called directly and through `./dev/mise run -q`, and one `$.http.fetch({ socketPath })` round trip; a new arm confirms at run time on 2.1.299 that `WebAssembly`, `require` and `process` are absent |
| A2-2 | The type contract gains TypeScript types generated from the D83 schema files (quicktype or json-schema-to-typescript, pinned), committed as generated files with a regenerate-and-compare check |
| A2-5 | `task.ts` becomes the one door to the core: argv `[coreBin, subcommand]`, JSON on stdin, the same exit-code contract and typed guard; `coreBin` resolves from `$.session.root()` and a path file that `core:build` writes; a missing binary goes to `.catch` with the "core not built" reason |
| A2-6 | Unit and engine tiers keep stubbing `process.run` (A2 2.5), so `mods.yml` needs no C++ build; an integration job that builds `rsm-core` belongs to the C++ CI lane, which needs a reflection-capable image (the OCI image's GCC 12 cannot, R8) |
| A2-8 | The shell tokenizer and its rules move to C++ (`rsm-core gate bash`), and `bash-corpus.jsonl` becomes the C++ test corpus; the TypeScript side keeps at most a generated keyword table (data, not logic) as a prefilter, and drops it if T1's measured p95 fits the Bash budget |
| A2-9, A2-15 to A2-18, A2-20, A2-21, A2-25 | Decision logic becomes `rsm-core` subcommands; each TypeScript feature only maps the event to a request and the result to an answer, so unit line counts move from TypeScript to C++ |
| A2-10 | Gate code moves into the C++ CLI rather than `python/src/marketplace_dev/gates/`; the hk tasks `retro:gate-merge` and `retro:gate-push` repoint to it |
| A2-12, A2-22, A2-24 | Their new Python logic (`budget.py --json`, `session/name.py`, `web_fetch.py`) becomes `rsm-core` subcommands instead (`ctx thresholds`, `session name`, `web fetch` wrapping webclaw) |
| A2-13, A2-14, A2-19, A2-23, A2-26 to A2-29 | Shape unchanged; any computation they need is a core call |
| New units | C1: CLI skeleton with one subcommand, schema-typed JSON in and out, exit codes, and a parity test against the existing Python task; C2: `core:build` mise task and the path file; C3: `serve` mode, only after a measurement misses a budget |

### 4.2 Effect on D60 (Python package run through uv)

D60 (DL-61, approved in DL-75 at `python/src/marketplace_dev/`) keeps its src layout, ruff and ty, locked dev
group, `[project.scripts]` entry points and the `uv run --no-sync --offline python -I -m <package>.<module>`
form. What changes:
1. The package becomes the thin bridge: entry points that call `rsm-core` through `subprocess`, plus the
   existing modules until each is ported; no new logic lands there.
2. It stays pure Python, so turning `package` on needs only a pure build backend and no compiler runs at sync;
   the `-I` guarantee and offline runs are unaffected.
3. Code the A2 plan moved into the package (A2-10 gates, A2-22 name generator, A2-24 web fetch) goes to C++.
4. A nanobind module later is a D60 amendment, not a default: it brings scikit-build-core, cache keys, a cp312
   floor against `requires-python >=3.11` (pyproject.toml:4), and stale builds hidden by `--no-sync`
   (astral-sh/uv#15809, PR #21488).

## 5. Tools first (D107)

| Tool | Language | Role here | Fit and caveats | Source |
|---|---|---|---|---|
| glaze | C++ | JSON for the CLI, JSON Schema for CT-53, JSON-RPC 2.0 registry | P2996 on GCC 16 or clang-p2996, C++20 otherwise; schema divergences #2508, #2656 | OR/repos/glaze (`e194d23`) |
| reflect-cpp | C++ | Alternative JSON and schema emitter | C++20 default, C++26 mode on GCC 16.2+; #375 | OR/repos/reflect-cpp (`fc1c3fe`) |
| simdjson | C++ | Fast P2996 serialization | No schema emitter | OR/repos/simdjson (`15e7eb8`, sparse) |
| cpp-httplib | C++ | HTTP over a Unix socket for `serve` | `AF_UNIX` on server and client | OR/pages/cpp-httplib-unix-socket-raw.md |
| nanobind | C++ | Later in-process Python module | C++17; abi3 from 3.12; no abi3t | OR/repos/nanobind (`71fc734`) |
| mirror_bridge | C++26 | Reflection-generated Python bindings | GCC 16.1+ or clang-p2996; JS backend is Node-API, unusable in mods | OR/repos/mirror_bridge (`5cbc100`) |
| welder | C++26 | Annotation-driven pybind11 or nanobind bindings and `.pyi` | GCC 16 only; proof of concept | OR/repos/welder (`3ca0c36`) |
| rosetta | C++26 | Multi-backend generator with reflection-free output | clang-p2996 tested on macOS; GCC in progress | OR/repos/rosetta (`d805a3d`) |
| pymetabind | C++26 | pybind11 bindings from reflection | GCC 16.1; early | OR/repos/pymetabind (`570c3b5`) |
| binaryen wasm2js, Emscripten | C++ | C++ to plain JS for a mod | No P2996; experimental; size ceiling | emscripten#8501; jevhooks-mod.md |
| quicktype | TypeScript (Node) | Schema to C++, TypeScript and Python | Already a #26 candidate | OR/pages/quicktype-typescript.md |
| json-schema-to-typescript | TypeScript (Node) | Schema to TypeScript for mods | Node 22.19+ | OR/pages/json-schema-to-typescript.md |
| datamodel-code-generator | Python | Schema to Python (CT-52) | Accepted baseline | docs/accepted-decisions.md:74 |
| schemagen | Go | Schema to TypeScript and Pydantic, one binary | 3 stars | OR/pages/schemagen.md |
| normalize-typegen | Rust | Schema to TypeScript and Python types | Library crate; maturity unknown | OR/pages/normalize-typegen.md |

Rust binding tools (maturin, uniffi, diplomat) bind Rust sources, not C++, and do not apply.

## 6. Code examples found

- Session-long helper with a socket: d.ts:3540-3552 (`$.process.spawn({ argv: ["bridge", "watch", e.cwd] })`
  in `session.start`) and d.ts:3494 (`$.http.fetch("http://bridge/reload", { method: "POST", socketPath })`).
- Mod to daemon over a Unix socket, and Rust to wasm2js for in-mod logic: OR/pages/jevhooks-readme.md:155-199,
  OR/pages/jevhooks-mod.md:9-23 (https://code.lmjtfy.fun/jevhooks.git/).
- `$.process.run` through a host seam: anthropics/claude-code `mods/diff/hooks/register.ts:680` at `19eb095`.
- nanobind reflection proof of concept: wjakob/nanobind discussion #1314 body, `include/nanobind/nb_reflect.h`
  on the `reflect` branch of matthewkolbe/nanobind.
- pymetabind: `pymetabind::bind::class<^^example_type>(m)` (OR/repos/pymetabind/README.md).
- glaze schema and RPC: `glz::write_json_schema<my_struct>()` (docs/json-schema.md:6), JSON-RPC registry
  (docs/rpc/jsonrpc-registry.md).
- reflect-cpp schema: `rfl::json::to_schema<Person>(rfl::json::pretty)` (OR/pages/reflect-cpp-json-schema.md:37).
- cpp-httplib Unix socket server and client (OR/pages/cpp-httplib-unix-socket-raw.md).
- MP's own reflection-private facade: `src/core.cpp:1-34` with the POD `ReflectionProbe` in
  `include/aggregated_research/core.hpp`.

## 7. Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| host | probes | `claude --version`; `ls -la ~/.local/bin/claude`; `strings <claude binary> \| grep -m1 'Bun v1'`; `which bun node deno uv python3 emcc`; `ls /opt/homebrew/opt` | 0 | 2.1.299, Bun 1.4.3, no emcc or wasi-sdk | Yes |
| 1 | Exa | `fx exa.sh <out> "<query>" 10` (POST api.exa.ai/search, key from env), 14 + 10 + 4 queries | 0, HTTP 200 each | 10 each | Yes: seeded mirror_bridge, welder, rosetta, pymetabind, nanobind #1314, P2911, pybind11 #6104, jevhooks, Bun docs, uv issues, glaze and reflect-cpp schema pages, #26521, #91870 |
| 1 | Context7 | `fx ctx7 library <name>` for nanobind, pybind11, scikit-build-core, glaze, reflect-cpp, bun, claude code | 1 each | 0 | No: "Monthly quota reached"; gap |
| 1 | Firecrawl | `fx firecrawl search "<query>" --limit 5 --json` | 1 | HTTP 402 "Insufficient credits" | No; gap |
| 1 | webclaw (fallback and mirror) | `webclaw -t 60 <url> -f markdown`, 64 pages | 0 for 63; 1 for one fossies URL (HTTP 401, replaced by the raw GitHub copy) | 64 | Yes: every cited page |
| 1 | Serper | `fx serper.sh <out> "<query>"` (POST google.serper.dev/search), 6 queries | 0, HTTP 200 each | 8 to 10 each; query 1 returned snowboard bindings | Yes: Anthropic acquires Bun, Simon Willison on Bun in Rust, glaze P2996 page |
| 1 | SerpApi | not run | n/a | n/a | Serper succeeded |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3 -I last30days.py "<topic>" --plan plan.json --emit md --quick --search reddit,hackernews,github,x --save-dir ""`, two runs | 0, 0 | Run 1: 6 Reddit, 2 HN, all off topic; run 2: 6 GitHub, 1 X; the planner kept only the first subquery both times; LLM rerank HTTP 503 | Run 2 only: ray-amjad/claude-code-mods PR #13, QwenLM/qwen-code#13749 |
| 2 | gh search | `gh search issues "<term>" --repo <r> --include-prs --limit 15`, 23 queries over nanobind, pybind11, claude-code, bun, glaze, reflect-cpp, clang-p2996, uv, mirror_bridge | 0 each | 0 to 15 | Yes: #1404, #6198, #313, #91870, #97293, #95653, uv #14383, #15809, #21488, glaze #2508, #2656, reflect-cpp #375 |
| 2 | gh view | `gh issue view` or `gh pr view <n> --repo <r> --comments --json ...`, 13 threads | 0 each | n/a | Yes; copies in OR/gh/ |
| 2 | GraphQL discussions | `gh api graphql` `repository.discussion(number)` with comments and replies, nanobind #1314 and pybind11 #6104 | first attempt 1 (zsh word splitting in my loop), rerun 0, 0 | 2 | Yes |
| 2 | Saved-search equivalent | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=1,2` plus control `README repo:<repo>` | 0 for 13 calls; HTTP 403 (shared rate limit) for 29 calls over four retries | see section 8 | Partly; gap |
| 2 | Clones | `git clone --depth 1 --filter=blob:none [--sparse] <url>`, 11 repositories | 0 each | n/a | Yes; commits in manifest.json |

`fx` is `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`. No key value was printed or written. `./dev/mise run research:collect` was not run
(its output path is tracked and owned by another lane).

## 8. Proposed saved-search rows

Reproduced read-only with `gh api search/code` (raw JSON in the session scratchpad `research5/R9/saved/`).
Each row uses the control `README` with `expected_min = 1`.

| id | query | repo | Result today | Why |
|---|---|---|---|---|
| `mods-process-run` | `process.run path:mods` | anthropics/claude-code | 17 hits (two pages); control 42 | How the official mods call native processes |
| `mods-webassembly` | `WebAssembly path:mods` | anthropics/claude-code | 0 hits; control 42 | Fires when WebAssembly reaches the mods surface |
| `mods-socketpath` | `socketPath` | anthropics/claude-code | 0 hits; control 42 | Watches the Unix-socket bridge pattern |
| `nanobind-stable-abi` | `STABLE_ABI` | wjakob/nanobind | 11 hits | abi3 and abi3t changes |
| `pybind11-limited-api` | `Py_LIMITED_API` | pybind/pybind11 | 1 hit on page 1; page 2 HTTP 403 | Tracks #6198 landing |
| `glaze-json-schema` | `write_json_schema` | stephenberry/glaze | 10 hits; control not completed (403) | CT-53 emitter API |
| `reflectcpp-to-schema` | `to_schema` | getml/reflect-cpp | 97 hits; control not completed (403) | CT-53 alternative |
| `mirror-bridge-reflection` | `freflection` | FranciscoThiesen/mirror_bridge | not completed (403) | Compiler support of the generator |

## 9. Open gaps

- Provider gaps: Context7 monthly quota (7 calls, rc 1); Firecrawl HTTP 402; Last30Days kept one subquery per
  plan, returned off-topic Reddit and HN, and its rerank hit HTTP 503; GitHub code search returned HTTP 403
  (shared rate limit) for 2 queries and 5 controls; SerpApi not needed.
- Unmeasured on this host: Bun's spawn overhead from inside a mod, a `$.http.fetch({ socketPath })` round trip,
  the import time of a nanobind module, and `./dev/mise run -q` against calling the binary directly. A2-0 arm 7
  should measure all four before any `serve` mode or nanobind unit is admitted.
- The 1,048,576-byte hooks-module ceiling comes only from the jevhooks author; Emscripten output in the mod
  realm (no timers, no `eval`) is untested.
- No Daveed Vandevoorde bindings demo was found.
- WebAssembly in mods is "in my plans" with no date; recheck under CT-80's watch list.
- Statements about GCC 16.2 and clang-p2996 on this host rest on R8 and its probes; this run compiled
  nothing.
- Windows is outside MP's matrix and was not examined beyond the cited mod issues.
