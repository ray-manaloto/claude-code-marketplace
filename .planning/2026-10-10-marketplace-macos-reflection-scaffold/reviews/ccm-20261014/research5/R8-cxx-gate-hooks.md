# R8: Compiled C++ (and P2996) deny gates for the three settings hooks (research round 5, 2026-10-14)

Written by research agent R8 of session `ccm-20261014` (`ce9c0b3d`) for the user's question whether to
convert the three deny gates (D102) to modern C++, with C++26 static reflection if possible. Read-only
except this file and the offline mirror. MP = the repository root, HEAD `21af565`, branch
`codex/marketplace-native-onboarding`, Claude Code `2.1.299`. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.

Citation keys. OFF = `offline/research/R8-cxx-gate-hooks/` (untracked mirror, D110; `OFF/manifest.json`
lists 77 mirrored items with URL, fetch time, command shape, exit code and SHA-256 or commit, plus 102
local receipts). OFF/pages are webclaw markdown copies; OFF/repos are shallow `--filter=blob:none`
clones; OFF/gh are `gh ... --json` copies; OFF/receipts hold this run's host probes, timings and raw
search results. HOOKS = `OFF/pages/cc-hooks.md` (code.claude.com/docs/en/hooks.md, one long markdown
line, cited by section title). CL = `OFF/gh/claude-code-CHANGELOG.md`. `#N` without a repository is
anthropics/claude-code issue N. Timings are medians of 30 runs on this Mac (arm64, Darwin 27.0.0) unless
marked; anything without a citation is labelled UNVERIFIED.

## Verdict

Recommendation: do not convert the gates to C++ now, with or without P2996. First remove the cost that
is actually there: every `git` child the gates spawn resolves to the global mise shim, which costs
186.2 ms per call on this host against 9.5 ms for `/usr/bin/git` (OFF/receipts/gitbench.json). Bypassing
the shim takes the measured push path from 401.0 to 54.6 ms, Stop from 228.5 to 45.8 ms and SubagentStop
from 373.1 to 62.1 ms with no build step (OFF/receipts/gatebench-push.json, gatebench-stop.json,
gatebench-substop.json). After that fix a compiled gate saves about 24 ms per Bash call and per turn
end, and it brings a bootstrap hazard the Python gates do not have. If native gates are still wanted
afterwards, port only `pretooluse_gate.py` to plain C++23 (no reflection) behind a launcher that falls
back to the Python file, keep the Python file as the reference with a parity corpus, and schedule it
after the hook units stop changing the gate logic (CT-17b, wave 29). Reflection buys nothing for three
small gates.

Confidence: high for the shim finding and for "not now"; medium-high that reflection adds nothing;
medium for the compiled-gate latency estimates, which are derived from the 2.5 ms process floor because
this run was not allowed to build anything.

Evidence that decides it:
1. The 402 ms push figure in the parent's receipt is two mise-shim `git` calls (2 x 186 ms) plus 26 ms of
   Python, not Python and the retro gate: the measured payload `git push origin HEAD` on the integration
   branch names no lane, so `check_lanes` gets an empty list (`dev/hooks/pretooluse_gate.py:60-63`,
   `dev/hooks/git_gate.py:30,58-60`), and the same gate drops to 54.6 ms when the shims directory is
   removed from `PATH`. The running Claude Code processes resolve `git` to
   `~/.local/share/mise/shims` (PATH entry 154 of 175 and 182 of 210, ahead of `/usr/bin`;
   OFF/receipts/claude-path-git.txt), so hooks spawned with that environment pay the same cost
   (inheritance inferred from the process environment; no hook-run receipt, see gaps).
2. `onFailure: "block"` turns a missing binary into a blocked call on `PreToolUse`, including the Bash
   call that would build it, and has no effect at all on `Stop` and `SubagentStop` (HOOKS section "Block
   the action when a hook fails"; added in 2.1.295, CL:278-280). A compiled gate that is not yet built
   therefore either locks out Bash or silently disables the two stop gates, the failure mode #82323
   (open since 2026-07-29) and #81458 (6,865 skipped guardrail runs) describe.
3. On macOS arm64 only GCC 16 (`-freflection`) and the repository's own clang-p2996 build compile P2996
   today; upstream Clang 23.1.3 and Apple Clang 21 do not (host probes, section 1). The Linux OCI image
   has GCC 12 from `build-essential 12.9` (`mise.toml:20-50`), so a reflection gate cannot build in CI.
4. The JSON libraries that use reflection keep the same API without it: glaze reads aggregates in its
   C++23 mode and "the entire Glaze API remains unchanged" under P2996 (`OFF/pages/glaze-p2996.md:42`;
   `OFF/repos/stephenberry_glaze/README.md:23-25`), and the hook input is a handful of aggregate fields.
5. The closest prior art, a C++23 port of a Python PreToolUse gate in neurocod/llm-loop, measured
   69.8 ms Python against 6.7 ms native, kept the Python file as the reference with a parity check, and
   left the native binary as a local opt-in because "a plugin installed from the marketplace is a
   snapshot that cannot build anything" (`OFF/repos/neurocod_llm-loop/claude-plugin/ask-user-gate/README.md:79-118`,
   commit `9140f7a`).

## 1. Compilers with P2996 on macOS arm64 (October 2026)

| Compiler | P2996 status | On this host | Flag | Build time | Install size | Citations |
|---|---|---|---|---|---|---|
| GCC 16 | Released: GCC 16 implements P2996R13 plus P3394, P3096, P3491, P3560 and expansion statements; library `<meta>` partial | Homebrew `gcc 16.2.0` (bottled) at `/opt/homebrew/bin/g++-16`; `-std=c++26 -freflection` defines `__cpp_impl_reflection 202603L`, and a `#include <meta>` plus `static_assert(display_string_of(^^int) == "int")` passes `-fsyntax-only` with rc 0 | `-std=c++26 -freflection` | Bottle, so install is a download; source build not measured | 1,705 files, 498.5 MB; links its own `libstdc++.6.dylib` (a static `libstdc++.a` also ships) | `OFF/pages/gcc16-changes.md:105-112` (gcc.gnu.org/gcc-16/changes.html); cppreference table row "Reflection: GCC 16, other columns empty" and "`<meta>`: libstdc++ 16 (partial)" (`OFF/pages/cppreference-cxx26-support.html`); OFF/receipts/host-probe-2.txt, host-probe-5, host-probe-7 |
| bloomberg/clang-p2996 | Experimental fork; the pinned `f17c8d6` is still the `p2996` branch head (commit 2026-09-24, "#353"); open defects include a Sema use-after-free (#288) and a silent miscompile of large packs (#323), both opened 2026-06-10/11 | Built and registered here: `asdf:clang-p2996@f17c8d6...` links to a private prefix; `-freflection-latest` with `-isysroot` passes `-fsyntax-only` | `-std=c++26 -freflection-latest -stdlib=libc++` | 363.49 s (failed) + 1,365.16 s (failed) + 84.93 s (passed) = 1,813.6 s across three admitted operations at `-j 4`, plus seven SDK adaptations; an outside report gives about 25 minutes for the `clang` target alone on 12 Linux cores | Prefix 1.0 GB, build tree 1.6 GB; no macOS prebuilt (glaze lists only `vsavkov/clang-p2996:amd64`) | `docs/p2996-toolchain.md:11-16,112-118,155-165,221-230,257-277`; `OFF/repos/bloomberg_clang-p2996` (sparse, `f17c8d6`); `OFF/receipts/gh-search/p2996-macos.json`; `OFF/pages/riccilab-build-clang-p2996.md`; `OFF/pages/glaze-p2996.md:56`; OFF/receipts/host-probe-3, host-probe-4 |
| Upstream Clang | Not usable: `cxx_status` lists P2996R13 as "No"; the 23.1 release notes mention only partial expansion statements; parsing of `^^` for primitive types merged 2026-02-06 (llvm/llvm-project#164692) and `std::meta::info` for primitive types merged to main 2026-10-02 (#190356), after LLVM 23.1.0 shipped on 2026-08-25; the tracker llvm/llvm-project#148123 is open | Homebrew `llvm 23.1.3`: the driver lists `-freflection` but does not forward it ("argument unused"); with `-Xclang -freflection`, `constexpr auto r = ^^int;` fails ("must be initialized by a constant expression") | none usable | Bottle | 9,336 files, 1.9 GB | `OFF/pages/clang-cxx-status.md:297-301`; `OFF/pages/clang23-release-notes.md:110-114`; `OFF/gh/llvm_llvm-project_pr164692.json`, `..._pr190356.json`, `..._148123.json`; `OFF/pages/phoronix-llvm23.1.md`; OFF/receipts/host-probe-6-syntax.txt |
| Apple Clang | None: Apple's C++ page lists C++26 features "expected" with no reflection row; cppreference's Apple Clang column is empty | `Apple clang 21.0.0 (clang-2100.3.34.2)`, CLT 27.0: `-freflection` is an unknown argument | none | n/a | CLT 1.3 GB | `OFF/pages/apple-xcode-cpp.md:13-46`; cppreference HTML table; OFF/receipts/host-probe-2.txt, host-probe-5 |
| EDG | Implementation exists but is "only publicly available in the Compiler Explorer"; not installable on macOS | n/a | n/a | n/a | n/a | `OFF/pages/p2996r13.md:737`; `OFF/pages/simdjson-p2996-readme.md:16` |

Reading: on this Mac a reflection gate can be built today with Homebrew GCC 16 or the local fork. Neither
exists in the Linux OCI image (GCC 12), on a fresh macOS machine without Homebrew GCC, or in hosted CI
without extra provisioning, and the fork exists only as this host's private build.

## 2. Bootstrap: how a compiled gate would reach a fresh clone or CI

What the hook runner does (HOOKS, "Block the action when a hook fails" and "Exec form and shell form"):
- "Can't start" counts as a failure. With `onFailure: "block"` a failed `PreToolUse` hook blocks the tool
  call; without it the failure is non-blocking and the call runs.
- "The field has no effect on these hooks: `Stop`, `SubagentStop`, `TaskCompleted`, and `TeammateIdle`":
  a stop gate that cannot start lets the turn end. MP sets `onFailure: "block"` on all three entries
  (`.claude/settings.json:49,61,73`); on the two stop entries the docs make it a no-op. This matters to
  CT-02b.1 ("Stop and SubagentStop fail closed", wave 18) whatever language the gates use.
- Shell form (no `args`) runs through `sh -c`; exec form (`args` set) spawns the executable directly. MP's
  entries are shell form (`.claude/settings.json:47,59,71`). Measured `sh -c` overhead: 5.81 ms against
  2.43 ms for a direct exec, so 3.4 ms on every call; a launcher test plus exec costs 6.20 ms
  (OFF/receipts/sh-overhead.txt).

Consequences for a native gate:
- PreToolUse: if the binary is absent, every Bash call is blocked, including `./dev/mise run <build>`, so
  the fix has to happen outside Claude Code. #80697 (closed 2026-09-21) records the earlier collision where
  a launch failure looked like a deliberate deny.
- Stop and SubagentStop: if the binary is absent, the gates are silently off; #82323 (open) asks for a
  `/doctor` check because "a missing or unrunnable hook command fails OPEN", and a later comment adds that
  "merging a hook does not install one".

Delivery routes and what each needs:
1. Launcher with fallback (recommended shape if a native gate ever ships): a POSIX script runs the binary
   when it exists and is current, else `exec python3 -I <gate>.py`. RomanKryvolapov/claude-code-hooks
   ships this pattern with committed per-OS Go binaries, but its launcher ends in `exit 0` when no
   binary is found, which is right for a status helper and wrong for a deny gate
   (`OFF/repos/RomanKryvolapov_claude-code-hooks/.claude/hooks/usage-limits`, `.gitattributes`, commit
   `a7c57c2`). A deny-gate launcher must fall back to the Python gate, never to exit 0. Staleness is the
   second risk: a binary built from older rules keeps enforcing them, so the binary must carry the
   digest of its sources and the launcher or binary must refuse to run a mismatch (design proposal,
   UNVERIFIED cost).
2. Build on first use: a build inside a 10 s hook timeout is fragile; a session-start build would be a
   mod under D92, and mods can be switched off remotely (#99130, R1), so the fallback has to carry the
   gate anyway. mattsta/claude-hooker (Zig) is "built when you clone it" with no prebuilt artifacts and
   needs a Zig toolchain (`OFF/repos/mattsta_claude-hooker/README.md:24-27`).
3. Prebuilt release artifacts: the support matrix is macOS arm64, Linux arm64 and Linux x86-64
   (`docs/accepted-decisions.md:46-48`). The mise `github:` backend checks the asset digest or checksum
   file and, on public GitHub, artifact attestations by default, with optional SLSA identity checks
   (`OFF/pages/mise-github-backend.md:101,469-513`); `ubi:` is deprecated since mise 2026.4.0 and goes
   away in 2027.1.0 (`OFF/pages/mise-ubi-backend.md:10`). `gh attestation verify` is the manual check
   (`OFF/pages/gh-attestation-verify.md`). dcg publishes SHA-256 sidecars, a minisign key and Sigstore
   bundles (`OFF/repos/Dicklesworthstone_destructive_command_guard/README.md:33`,
   `.github/workflows/dist.yml:381-412`); ccguard downloads per-arch tarballs at SessionStart with no
   checksum and exits 0 on failure (`OFF/repos/soyukke_ccguard/scripts/ensure-binary.sh:52-75`).
   Publishing releases is an outward step that waits for explicit instruction (AGENTS.md, Gotchas), and a
   fresh clone still needs `mise install` before the first session.
4. C++23 subset now, reflection later: Apple Clang 21 and GCC 12 cannot compile reflection, so the C++23
   build is the only one that could run everywhere; the reflection build would add nothing the C++23
   build lacks for these gates (section 3).

CI: the acceptance image is `debian:bookworm-slim` plus `git`, `curl`, `ca-certificates` and
`build-essential 12.9` (`mise.toml:20-50`), and `ci/acceptance.sh:43` runs `claude -p` inside it.
Whether that session loads MP's project hooks, and whether `python3` exists in that image for today's
gates, is not established (gap).

## 3. Reflection libraries and what reflection buys

- glaze: P2996 is an alternative backend; the C++23 mode already reads and writes aggregate structs with
  no metadata, and the API is identical under P2996 (`OFF/pages/glaze-p2996.md:42-56`;
  `OFF/repos/stephenberry_glaze/README.md:23-65,254-264`, commit `e194d23`, release v9.0.0 2026-09-24). P2996
  adds non-aggregates, enum strings without `glz::meta`, more than 128 members and private members. CI
  covers C++26 reflection on `gcc:16.1` (stephenberry/glaze PR #2553, merged 2026-05-07) and C++23 on
  Clang 18+ and GCC 13+, and the project aims to support the latest Apple Clang (`README.md:260-264`).
- simdjson: static reflection behind `SIMDJSON_STATIC_REFLECTION=1`, needing `-std=c++26 -freflection`
  on GCC 16 (`OFF/pages/lemire-compile-time-json.md:114`); compile-time JSON parsing exists but the
  gates read lane records that change at run time, so it does not apply. Release v5.0.4 (2026-10-12).
- reflect-cpp: C++20/23 mode by default (GCC 11.4, Clang 14, MSVC 17.8); C++26 mode needs GCC 16.2 or a
  P2996 Clang (`OFF/pages/reflectcpp-cpp26.md:20-45`; `OFF/repos/getml_reflect-cpp/README.md:674-680`).
- Boost.JSON: not researched beyond noting it needs no reflection (UNVERIFIED for this report).
- Argument parsing: the three gates take no arguments (stdin JSON only, `pretooluse_gate.py:66-76`,
  `stop_gate.py:21-27`, `subagent_stop_gate.py:22-28`); `git_gate.py` takes one verb
  (`git_gate.py:161-165`). Reflection-based parsers turned up by search (garcia6l20/reflex,
  nickelpro/cargparse) were not evaluated.

What a port must reproduce is not data binding but behaviour: Python `shlex.split` with its `ValueError`
fallback (`pretooluse_gate.py:32-36`), the segment regex, strict JSON rejection (neurocod found jsmn
accepted 12 of 13 inputs `json.load` rejects, and nlohmann/json overflowed the stack on deep nesting;
`.../ask-user-gate/README.md:101-110`), and `retro_gate.py`'s markdown record checks, which the push and
SubagentStop paths spawn as a second Python process (`git_gate.py:89-100`; `dev/retro_gate.py:1-26`).
Reflection helps with none of these. Verdict for question 3: reflection buys nothing real for three small
gates; plain C++23 with a small JSON reader or glaze in C++23 mode covers the data side.

## 4. Git access: subprocess, libgit2 or gitoxide

| Gate query (file:line) | git CLI | libgit2 (main `f28579d`, 2.0.0-rc.1; latest release v1.9.7, 2026-08-13) | gitoxide (`8dc7afd`; v0.60.0, 2026-10-08) |
|---|---|---|---|
| `rev-parse --show-toplevel` (`pretooluse_gate.py:80`, `stop_gate.py:28`, `subagent_stop_gate.py:29`) | yes | `git_repository_open_ext`, `git_repository_workdir` (`include/git2/repository.h:184,573`) | discovery, git-common-dir (`crate-status.md:81-84`) |
| `rev-parse -q --verify MERGE_HEAD` (`pretooluse_gate.py:57`, `git_gate.py:116`) | yes | `git_reference_name_to_id`, `git_repository_state` (`refs.h:54`, `repository.h:947`) | ref lookup yes; merge-state persistence unchecked (`crate-status.md:73,412`) |
| `--git-path MERGE_MSG`, read subject (`git_gate.py:117-118`) | yes | `git_repository_message` reads `MERGE_MSG` from the gitdir (`repository.h:708-723`, `src/libgit2/repository.c:3529`) | path join on the git dir (no API listed) |
| `branch --show-current` (`pretooluse_gate.py:61`, `subagent_stop_gate.py:30`, `git_gate.py:149`) | yes | `git_repository_head`, `git_reference_shorthand` (`repository.h:448`, `refs.h:802`) | head name (`crate-status.md` "access to refs") |
| `@{upstream}` verify and `--abbrev-ref` (`git_gate.py:123,150`) | yes | revparse accepts `@{u}` and `@{upstream}` (`src/libgit2/revparse.c:365`); `git_branch_upstream`, `git_branch_upstream_name` (`branch.h:212,249`) | rev-parse "handle upstream and push resolution" (`crate-status.md:88`) |
| `refs/remotes/origin/<b>` verify (`git_gate.py:152`) | yes | revparse or reference lookup | ref lookup |
| `<commit>^{commit}` peel (`git_gate.py:66`) | yes | `git_revparse_single` (`revparse.h:37`) | peel to object kind |
| `for-each-ref --points-at` (`git_gate.py:67`) | yes | iterate `git_reference_iterator_glob_new` and compare targets (`refs.h:571`) | iterate references and compare |
| `log -1 --format=%s` (`git_gate.py:142`) | yes | `git_commit_summary` (`commit.h:132`) | commit message summary |
| `rev-list --merges --max-count=200 <span>` (`git_gate.py:156`) | yes | `git_revwalk_push_range`, `git_revwalk_push_head`, `git_revwalk_hide_glob("refs/remotes")`, `git_commit_parentcount` (`revwalk.h:135,169,257`, `commit.h:244`) | rev-walk with include and exclude (`crate-status.md:89-91`); early stop on hidden ancestry not done (`:444`) |
| `name-rev --name-only MERGE_HEAD` (`dev/retro_gate.py:122`, only with `--from-merge-head`, not on the hook path) | yes | no name-rev (no match in `include/` or `src/`); `git_describe_commit` is describe, not name-rev (`describe.h:165`) | `describe()` "similar to git name-rev" (`crate-status.md:810`) |

Paths are relative to `OFF/repos/libgit2_libgit2/` and `OFF/repos/GitoxideLabs_gitoxide/`. Both
libraries cover every query on the hook path; gitoxide also covers name-rev. Measured cost per git child
on this host (OFF/receipts/gitbench.json, gitbench-clt.txt): mise shim 186.2 ms; `/usr/bin/git` (the
xcrun trampoline) 9.4 to 10.9 ms for `rev-parse`, `branch`, `rev-list` and `for-each-ref`;
`/Library/Developer/CommandLineTools/usr/bin/git` 5.0 ms; `/bin/cat` floor 2.4 ms. In-process libgit2 or
gix latency was not measured (no build allowed); sub-millisecond reads after a repository open are
plausible but UNVERIFIED. Caveats on record: libgit2 "is not nearly as thoroughly tested as the git CLI"
and bun dropped it for the CLI (anecdotal, `OFF/pages/hn-libgit2-tested.md`); gitoxide users list
missing workflow features (`OFF/pages/gix-discussion-2810.md`). With the shim bypassed, the gates make at
most two to four git calls on their hot paths, so in-process git would save roughly 10 to 40 ms per push,
merge or stop event, at the price of a C or Rust dependency and parity risk with git's own semantics.

## 5. Prior art: compiled Claude Code hooks and how they ship

| Project (commit) | Language | What it gates | How it ships | When it cannot run |
|---|---|---|---|---|
| neurocod/llm-loop ask-user-gate (`9140f7a`) | Python reference plus C++23 port (CTRE vendored, hand-written JSON) | PreToolUse Bash | Plugin names the Python script; the binary is a local opt-in built by `cpp/build.py`; `parity_check.py` diffs verdict, exit code and text | Python always present by design (`README.md:79-135`) |
| WinDerek/jiaolong-ai, genomewalker/chitta, ncmonx/icemage | C++ | PreToolUse policy code (code-search hits) | not examined in depth | not examined |
| Dicklesworthstone/destructive_command_guard (`6009005`) | Rust | Destructive shell commands, many agents | `curl | bash` installer, per-target release binaries, SHA-256, minisign, Sigstore (`README.md:19-33`, `dist.yml`) | Fail-open by default on unparseable input; bridges allow with a diagnostic when dcg cannot start (`README.md:918-929`) |
| kornysietsma/claude-code-permissions-hook (`56b9db4`) | Rust | Tool permissions | `cargo install --path .`; absolute path advised because hooks may not see `~/.cargo/bin` (`README.md:14-22,138`) | passthrough with warning on bad payload (`:132`) |
| Osso/claude-bash-hook (`0c57b10`) | Rust | Bash | build and copy to `~/.local/bin` (`README.md:11-24`) | not stated |
| rtk-ai/rtk (`f53e603`) | Rust | Command rewriting hook | `curl | sh`, Homebrew tap, `cargo install --git` (`INSTALL.md:44-82`) | not a gate |
| smykla-skalski/klaudiush (`249ceb1`) | Go, go-git v6 in process (`go.mod:16`) | Git workflow validators, Stop completion gate | Homebrew tap, install script, nix, `mise run build` (`README.md:21-62`) | Reports "Validation unavailable" and always exits 0 because providers let actions through on a non-zero exit (`README.md:265-273`) |
| asbjornb/claude-hooks (`60d24b7`) | Go | Bash permissions | `setup.sh` builds with Go 1.22+, or `go install` (`README.md:50-62,178-184`) | not stated |
| RomanKryvolapov/claude-code-hooks (`a7c57c2`) | Go | Agent spawn budget, audit | Committed per-OS binaries plus a POSIX launcher | Launcher exits 0 when no binary is found |
| soyukke/ccguard (`e093ef5`) | Zig | All tools | Plugin SessionStart downloads a per-arch release; PreToolUse runs `${CLAUDE_PLUGIN_DATA}/bin/ccguard` (`hooks/hooks.json`) | No checksum; download failure exits 0, leaving PreToolUse to fail open |
| mattsta/claude-hooker (`44a1e54`) | Zig | 30 hook events from one rule file | Built on clone, no releases (`README.md:24-27`) | not stated |

GitHub repository search for "claude code hook" returned 2 C++ (both ESP32 desk displays), 15 Rust, 15
Go and 1 Zig repositories; code search for `hookSpecificOutput permissionDecision language:C++` returned
28 files against 2,756 for Rust (OFF/receipts/gh-search). No project found ships a P2996 Claude Code hook.

## 6. Alternatives the tools-first rule (D107) prefers

- Built-ins first. (a) Call git by absolute path, or drop the mise shims from `PATH` for the git
  child, in `git_gate.git` (`dev/hooks/git_gate.py:37-43`) and `retro_gate.git` (`dev/retro_gate.py:77-79`);
  `dev/toolchains/p2996_source.py` already uses `/usr/bin/git` (`docs/p2996-toolchain.md:29`). (b) The
  hooks `if` field filters a handler by permission-rule syntax, such as `"Bash(git *)"`; each subcommand,
  `$()` and backtick body is checked, and when Claude Code cannot tell what runs it runs the hook anyway
  (HOOKS, "How `if` patterns match Bash commands"). The docs call it best-effort and say to use the
  permission system for a hard deny, so it can drop the 26 ms plain-path cost for commands with no git or
  `delivery:publish`, but its matching of `./dev/mise run delivery:publish` and of `bash -c '...'` needs
  host tests. The current regex prefilter has the same blind spots for `bash -c` and `/usr/bin/git`
  (`pretooluse_gate.py:37-49`).
- Third-party CLIs: dcg could cover the destructive-git part of CT-02b.4 but cannot express the lane-retro
  rule; klaudiush and hk are git-workflow gates without this repository's lane records. No tool found
  implements "a lane merges or pushes only with a passing retro record", so that logic stays project code.
- Languages for project-owned native code: Rust has the most hook prior art (table above), in-process
  git through gix and attested release tooling (`OFF/pages/cargo-dist-intro.md`); Go has go-git and
  trivial static cross-compiles; Zig needs a toolchain this host lacks (`zig: command not found`,
  OFF/receipts/host-probe-8-tools.txt). Each would add a fourth language beside Python, TypeScript mods
  and the C++26 core, and D107 orders third-party tools, not languages for project code; choosing Rust
  over C++ for the gates would need its own decision.

## Options table

Latency columns: measured values are medians on this host; "est." values add the 2.5 ms process floor,
3.4 ms of `sh -c` for shell form and 9.5 ms per `/usr/bin/git` child.

| Option | Plain Bash path | Push path (`git push origin HEAD`, integration branch) | Fresh-clone behaviour | Build dependency | Maintenance cost | Citation |
|---|---|---|---|---|---|---|
| A. Today: Python, `git` via PATH | 26.5 ms (+3.4 ms sh) | 401.0 ms; Stop 228.5, SubagentStop 373.1 | Works wherever `python3` is on PATH | none | baseline | gate-timing receipt; OFF/receipts/gatebench-*.json |
| A1. Python, git child outside the mise shims | 26.5 ms (+3.4) | 54.6 ms; Stop 45.8, SubagentStop 62.1 | Same as A | none | two small edits plus a test asserting the resolved git | OFF/receipts/gatebench-*.json, gitbench.json |
| A2. A1 plus `if` filters on the PreToolUse handler | about 0 for commands with no git or publish (hook not spawned) | 54.6 ms | Same as A | none | settings change, `test:hooks` cases for each pattern; best-effort matching | HOOKS `if` table |
| B. C++23 port of `pretooluse_gate` only, launcher falls back to Python | est. 6 ms (shell form) | est. 22 ms with two `/usr/bin/git` children; a named lane adds the Python retro gate child (about 26 ms, not measured) unless ported | Python fallback until built; without the launcher, every Bash call is blocked | any C++23 compiler and CMake (Apple Clang 21 here; GCC 12 in the OCI image, untested) | two implementations, parity corpus for shlex, JSON and refusal text | neurocod README; HOOKS onFailure |
| B'. B with libgit2 in process | est. 6 ms | est. under 10 ms plus retro child (UNVERIFIED) | as B | libgit2 (vcpkg or Homebrew; not installed here) | as B plus a C dependency; no name-rev | section 4 |
| C. C++26 P2996 gate (GCC 16 or clang-p2996) | as B | as B | Builds only where GCC 16 or the private fork exists; never in the OCI image | GCC 16 bottle 498.5 MB, or fork 1.0 GB prefix and about 30 min of build operations | highest; experimental fork defects; no functional gain | section 1, section 3 |
| D. Prebuilt attested binaries via mise `github:` | as B | as B | Needs `mise install` before the first session; until then `PreToolUse` blocks Bash and the stop gates are off | release workflow for three targets; publish admission per release | release pipeline, lock pins | mise github backend docs; AGENTS.md |
| E. Rust gate (gix, prebuilt or cargo-built) | as B | as B' (UNVERIFIED) | as B or D | Rust toolchain (rustc 1.99 here) or releases | a new language; strongest prior art | section 5, section 6 |
| F. Third-party dcg for destructive git only | sub-millisecond claimed (`README.md:50`) | does not cover lane retro | installer per machine | none in repo | external pin; fail-open defaults | dcg README |

## Recommendation and wave placement

Wave numbers are from `P/reviews/ccm-20261014/reprioritize-3/Q2-order-v2.md`.

1. A1 now-ish, in the first hook unit: add to CT-02b.1 (wave 18, lane 2, the first writer of
   `dev/hooks/**`; Q2-order-v2.md:144,248-252) an acceptance row that every gate's git child resolves
   outside the mise shims, with a timing check (Stop under 60 ms on this host). `dev/retro_gate.py` is
   CT-39 territory, so its `git()` gets the same row in 39-4 (wave 5, "planning, lane, retro, check
   tools"; Q2-order-v2.md:131). Landing it before wave 18 needs a user decision: lane 2 is occupied in
   every wave from 0a to 17 except 0c, which D97 keeps empty.
2. Also in CT-02b.1 (wave 18): record that `onFailure` does not apply to Stop and SubagentStop, so
   "fail closed" there needs another mechanism, and add #82323 and #100891 to the CT-80 watch list.
3. A2 optional, in CT-02b.2 (wave 19, the token parser and shared table; Q2-order-v2.md:145), only with
   `test:hooks` cases for `git -C`, `bash -c`, `./dev/mise run delivery:publish` and `$()` forms.
4. Keep the gates as stdlib Python run by an interpreter (this supports the U2 exception to D60:
   `uv run` adds 9 to 14 ms and the real cost was the shim).
5. Option B only if the user still wants native gates after A1: a new cxx-column unit after CT-17b
   (wave 29; Q2-order-v2.md:155), the last writer of the gate logic, and after the container C++ build
   is qualified (CT-26b, wave 5; #27 native-core class run, wave 15). The cxx column is full through
   wave 57 (Q2-order-v2.md:93-95), so it either displaces a cxx unit or follows CT-45 at wave 57.
6. Option C: no wave. Revisit only if the C++26 core qualifies a reflection toolchain on all three
   matrix platforms (`docs/accepted-decisions.md:46-48`) and a gate needs something only reflection
   gives; nothing in the three gates does today.
7. Options D and E need their own decisions (publish admission; a language beyond D107's tool ordering)
   and are not placed.

## Code examples found

- C++23 port of a Python PreToolUse gate, with build script and parity check: neurocod/llm-loop
  `claude-plugin/ask-user-gate/cpp/ask_user_gate.cpp`, `cpp/build.py`, `cpp/parity_check.py`, README
  lines 79-135, commit `9140f7a` (`OFF/repos/neurocod_llm-loop`).
- POSIX launcher choosing a per-OS prebuilt binary: RomanKryvolapov/claude-code-hooks
  `.claude/hooks/usage-limits`, commit `a7c57c2`.
- SessionStart download of a per-arch release binary: soyukke/ccguard `scripts/ensure-binary.sh:1-76`,
  `hooks/hooks.json`, commit `e093ef5`.
- Attested multi-target release workflow for a hook binary: Dicklesworthstone/destructive_command_guard
  `.github/workflows/dist.yml:55-95,381-440`, commit `6009005`.
- In-process git in a Go hook: smykla-skalski/klaudiush `go.mod:16` (go-git v6), commit `249ceb1`.
- Exec-form hook with `onFailure: "block"`: HOOKS, "Block the action when a hook fails".

## Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| 0 | Repo reads | `cat`, `grep`, `sed` over the files named in the brief | 0 | n/a | yes |
| 0 | Host probes | `clang --version`, `g++-16 --version`, `brew info gcc llvm`, `ls` of mise installs and the p2996 prefix, `du -sh`; preprocess-only (`-dM -E`) and `-fsyntax-only` checks that write no files | 0 | OFF/receipts/host-probe-1..8 | yes |
| 0 | Timing | `/usr/bin/python3 -I gitbench.py`, `gatebench.py`, `gatebench2.py` (run the repo's gates read-only with the parent's payloads), `sh -c` overhead | 0 | OFF/receipts | yes |
| 0 | Claude process PATH | `ps -ww -E -p <pid> -o command= | grep -o ' PATH=[^ ]*'` (PATH only) | 0 | 2 processes | yes |
| 1 | Exa | `fnox ... exec -- exa.sh <out> <query>` (curl, header read from env through `-K -`), 25 queries | 0, HTTP 200 x25 | 10 each | yes |
| 1 | Context7 | `fnox ... exec -- ctx7 library <name> <query>` x5 | 1 x5 | "Monthly quota reached" | no, gap |
| 1 | Firecrawl | `fnox ... exec -- firecrawl search ... --json`; `firecrawl scrape <gcc changes> --format markdown` | 1, 1 | HTTP 402 insufficient credits | no, gap |
| 1 | webclaw | `webclaw <url> -f markdown` for 43 pages, `-f html` for the cppreference table (mirrored) and the GCC status page (scratch only) | 0 each | 4 placeholders (GCC bugzilla Anubis x3, reddit login) | yes, placeholders excluded |
| 1 | Serper | `fnox ... exec -- serper.sh <out> <query>`, 6 queries | 0, HTTP 200 | 2 to 10 | corroboration |
| 1 | Last30Days | `fnox ... exec -- env SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py <topic> --plan plan.json --emit json --quick --save-dir "" --no-browser-cookies` | 0 | 5: one X post on C++26 reflection JSON, four off-topic Reddit; grounding error | no, gap |
| 2 | gh issue and PR views | `gh issue view N --repo R --comments --json ...` for #81458, #82323, #80697, #100891, clang-p2996 #189 #308, llvm #148123, Homebrew #289142, simdjson #2282; `gh pr view` llvm #164692 #190356 | 0 (jdx/mise#9936 is a discussion: rc 1, mirrored with webclaw) | 12 | yes |
| 2 | gh search issues and PRs | glaze (gcc 16, P2996, apple clang), simdjson, clang-p2996 (macos, release binary), llvm `--label reflection`, libgit2 (perf, worktree), gitoxide (upstream), claude-code (compiled hook, latency, onFailure, Stop onFailure) plus control "PreToolUse hook" | 0 each | 1, 16, 10, 1, 12, 0, 5, 0, 0, 0, 0, 0, 3, 0; control 5 | yes where non-zero |
| 2 | gh search repos | `gh search repos "claude code hook" --language C++|Rust|Go|Zig` | 0 | 2, 15, 15, 1 | yes |
| 2 | gh code search | `gh api -X GET search/code -f q='hookSpecificOutput permissionDecision language:C++'`, control `language:Rust` | 0 | 28, control 2,756 | yes |
| 2 | Discussions | `gh api graphql` search type DISCUSSION, 5 queries | 0 | 110, 6, 1, 40, 0 | gitoxide #2810 |
| 2 | Saved-search reproduction | `gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5`, each with control `README repo:<repo>` | 0, one 403 secondary rate limit then retry rc 0 | see below | yes |
| 2 | Clones | `git clone --depth 1 --filter=blob:none --no-tags <url>` for 20 repositories; clang-p2996 sparse (`P2996.md`, `README.md`, `.github`) | 0 each | commits in manifest | yes |
| 2 | Changelog | `gh api -H 'Accept: application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` | 0 | 1,015,061 bytes | yes |

## Proposed saved-search rows

Reproduced read-only (OFF/receipts/saved); do not edit `dev/saved-searches.toml` from this report.

```toml
[[search]]
id = "claude-code-onfailure"          # 3 hits; control README 42
query = "onFailure"
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "glaze-reflection26"             # 15 hits; control 5
query = "GLZ_REFLECTION26"
repo = "stephenberry/glaze"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "libgit2-upstream-name"          # 5 hits; control 51
query = "git_branch_upstream_name"
repo = "libgit2/libgit2"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "gix-remote-tracking"            # 6 hits; control 37
query = "remote_tracking_ref_name"
repo = "GitoxideLabs/gitoxide"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "dcg-fail-closed"                # 33 hits; control 53
query = "fail_closed"
repo = "Dicklesworthstone/destructive_command_guard"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

Not proposed: `freflection repo:bloomberg/clang-p2996` returned 0 and its control also returned 0 after
a rate-limit retry; the fork is not in the code-search index, so track it with `gh search prs --repo
bloomberg/clang-p2996` instead.

## Open gaps

- Context7 monthly quota exhausted (5 calls, rc 1); Firecrawl HTTP 402; Last30Days found nothing on topic
  and its grounding source errored; GCC bugzilla pages returned an Anubis challenge, so GCC reflection
  bug status rests on mail-archive search snippets (Exa q22) and is not analysed.
- No native gate, libgit2 or gix build was allowed, so B, B', C, D and E latencies are estimates.
- Hook environment inheritance: the shim cost in hooks is inferred from the Claude processes' `PATH` and
  from the parent's 402 ms matching the shim arithmetic; a hook-run receipt (a trivial hook logging
  `command -v git`) would confirm it and needs a session the brief does not allow.
- Whether the OCI acceptance session loads MP's project hooks, and whether `python3` exists in
  `debian:bookworm-slim` with the listed packages, is not established; if it does not, today's gates
  already block Bash there under `onFailure: "block"`.
- Whether the gate code would compile with GCC 12 in the OCI image is untested.
- `if` filter behaviour for this repository's command shapes is untested.
- GCC 16 source-build time and Apple's reflection roadmap were not found.
- Upstream Clang reflection has no release date; `std::meta::info` reached main on 2026-10-02 (#190356).
