# CT-59 design: C++ agent-dispatch core with two skills

Stage 1 of the CT-59 SDLC team (D119), architect, session ccm-20261014, 2026-10-14; read-only; R8 and R9 pending at writing.
Saved verbatim by the parent from the architect's final reply (the architect ran read-only).

Abbreviations: AP = `/Users/rmanaloto/.codex/skills/.shared/agent-protocol/`, CS = `/Users/rmanaloto/.codex/skills/claude-agent/`, MP = `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/`. R8 and R9 are not in `research5/` yet, so the compiler and bridge choices below are provisional.

## 1. Minimum contract

**Request (keep).** The fields are `contract_version`, exactly one of `task` or `task_file`, absolute `workdir`, `mode` (review or implement), `model`, `effort`, `timeout_s` (1 to 14400, default 1800), a fresh `out_dir`, `schema_file`, string `metadata` and one provider block (AP `src/agent_protocol/schemas/request.schema.json:6-157`).
- The task XOR becomes a schema `oneOf` instead of code (`contracts.py:173-176`).
- Options for the other provider are rejected (`contracts.py:177-179`).
- Effort is checked per provider (`:180-183`).
- Tool rules must be non-empty, unique and contain no commas (`:185-194`).
- `codex.sandbox` becomes required. Today review falls back to the inherited sandbox with only a warning (`runner.py:218-221`).

**Safe and bare modes.** Today `claude.mode` accepts normal, safe or bare (`request.schema.json:78-86`, `adapters.py:37-38`).
- Keep `normal` for lanes.
- Keep `safe` only for diagnostics. The current smoke uses it (`smoke.py:27`), but it switches off hooks, skills and agents.
- Drop `bare`: it needs `ANTHROPIC_API_KEY` (A1 defect 7).

**Report (keep, in MP vocabulary).** Keep A1 §3.1's lane report. It replaces AP's `report.schema.json:215-226`, where `participants` disappears.

**Envelope (keep).** Keep the 19 required fields (`envelope.schema.json:427-447`) with these meanings:
- `status` is the transport outcome and stays separate from `task_status` (`contract.md:60-61`).
- `execution` records the native and wrapper exit codes, exact argv, CLI path and version, PID and timestamps (`runner.py:45-55`).
- `usage` (`:56-62`).
- `result_schema` records path, sha256, kind and validation (`:63-70`).
- `artifacts` records sha256 and bytes for each file (`capture.py:37-52`).
- `errors` and `warnings`.

Two additions:
- `peak_context_tokens`. Today usage comes from the cumulative terminal total (`adapters.py:248-260`, A1 defect 9).
- A `started.json` file written before the wait, so status and cancel can work (A1 defect 10).

`native` shrinks to one provider block: the raw initialization object, the raw terminal object (unknown fields kept, `test_runner.py:110-115`), a typed projection and the agent-event count.

**Behaviours to carry over, each tested.**
- Success needs three things together: exit 0, a success terminal event and a schema-valid result. Bad JSON, a bad schema, an error at exit 0, no result and exit 7 each fail with rc 1 (`test_runner.py:117-130`, `adapters.py:274-282`, `test_adapters.py:80`). Codex additionally needs `turn.completed` (`test_adapters.py:44`).
- `task_status: partial` is never rewritten (`test_runner.py:132-135`).
- **Timeout:** rc 124, and the whole process group is stopped, including a child that ignores SIGINT and SIGTERM and a grandchild. The stop ladder is SIGINT, SIGTERM, SIGKILL with one second each (`capture.py:71-96,126-128`, `test_runner.py:18-30,261-275`).
- **Cancellation:** SIGTERM or SIGINT to the wrapper gives `cancelled` and rc 130 (`cli.py:10-11,23`, `runner.py:288-297`). The Codex suite never tests this; CT-59 adds the test.
- **Capture:** directory mode 0700, files 0600 created with `O_EXCL`, reads use `O_NOFOLLOW` with a 64 MiB parse cap, and an existing `out_dir` is refused without writing a receipt (`capture.py:16-34`, `runner.py:222-228`, `test_runner.py:211-223`). The receipt equals the envelope (`:100-101`).
- **Validation:**
  - Duplicate keys and NaN or Infinity are rejected (`contracts.py:25-42`).
  - Unknown fields are rejected, required fields get no defaults and types are not coerced (`test_contracts.py:37-51`).
  - Only local `$ref`s are allowed (`contracts.py:82-100`).
  - The native copy strips only `$schema` and `$id` (`:105-106`).
  - Error text names the path and keyword but never echoes values (`:127-130`, `test_runner.py:236`).
- **Exit codes:** 0, 1, 2, 124, 127, 130 (`runner.py:323-329`, `contract.md:84-85`). A usage error before a provider is chosen goes to stderr with rc 2 (`cli.py:16-18`).
- **Exactly one envelope on every path.** Today `parse_envelope` at `runner.py:332` can throw outside the try block; the C++ version fixes that.
- **Subagents:** an Agent tool use or a child `parent_tool_use_id` is reported as `unexpected_subagents`. Background shell tasks do not count (`adapters.py:196-238`, `test_runner.py:277-293`).

**Drop:**
- `format_checks` (`contracts.py:109-114`).
- `allow_subagents: true`, `agents_file` and the `--agents` route (`runner.py:207-214`).
- `codex.profile` and `danger-full-access`.
- Qualification, workflow, triage, healing, migration and maintenance.
- The generated Pydantic models, and `python-statemachine` (`lifecycles.py`). The lifecycle becomes a transition table from `charts/run.json`.
- Discovering the CLI through `shutil.which` (`runner.py:247`).
- Inheriting the whole environment (`capture.py:119`).

## 2. C++ design

**Components** (namespace `com::rsm::agent_dispatch`, per `docs/accepted-decisions.md:31`):

1. `json`: strict parsing with a streaming duplicate-key pass, writing, and bounded reads.
2. `schema`: a registry built only from the committed files, a resolver that refuses anything but local refs, Draft 2020-12 validation, and native-schema bundling.
3. `records`: POD records for the request, envelope and report. Two wrappers keep missing and null apart (`accepted-decisions.md:75`):
   - `Nullable<T>` is always written, as null when empty.
   - `Optional<T>` is left out when empty.
4. `codec`: a P2996 reflection codec. It walks `nonstatic_data_members_of` to write and read JSON keys and uses `enumerators_of` for enum strings. Raw native objects pass through as opaque JSON values.
5. `process`: `posix_spawn` with `POSIX_SPAWN_SETSID`.
   - stdin is the captured `prompt.txt`, opened through file actions, so there is no pipe deadlock.
   - stdout and stderr go straight to the 0600 files.
   - A self-pipe catches SIGCHLD, SIGINT and SIGTERM, with a deadline.
   - The stop ladder uses `killpg`.
   - The environment is built from A1's allow list.
6. `claude` and `codex` adapters: argv per A1 §3.1 lane mode (`--agent <role>`, `--session-id` chosen before launch, `--disallowedTools Agent`, `--strict-mcp-config`), event decoding, success detection and projection.
7. `runner`: the lifecycle table, the envelope that starts as the failed envelope (`runner.py:32-82`), `started.json` and `receipt.json`.
8. `probe`: the real CLI path (paths under `.../mise/shims/` are refused), `--version`, and a check that every emitted flag appears in `--help`. One fact for the probe: `--max-turns` does not appear in Claude 2.1.299's `--help` (observed). The probe must decide whether to drop the flag or rely on the agent's `maxTurns`.

**Reflection is used in two places only**, where it pays:
- the codec, which replaces about 500 lines of hand-written mapping for 19 envelope fields plus their nested objects;
- a parity test that the reflected member names equal the schema's `properties` and `required`. This is a precursor to CT-53 and follows D83: the schemas stay the source and C++ maps back to them.

Native event streams stay dynamic JSON.

**Libraries** (all candidates, decided by fork F2):
- jsoncons for parsing and Draft 2020-12 validation with a custom resolver;
- picosha2 for SHA-256;
- Catch2 v3 for tests;
- C++20 `std::format` and `std::chrono` for timestamps;
- `getentropy` for the run id and the UUID.

**Call path.** The skill runs `./dev/mise run dispatch:claude -- <abs request>`. That task depends on `agent-dispatch:build`, an incremental CMake preset build into a fixed directory under `~/.local/state/marketplace/agent-dispatch/build/`, and then runs the binary `agent-dispatch dispatch claude <req>`. The binary also has `status <out_dir>`, `cancel <out_dir>`, `probe <provider>` and `smoke`. There is no Python and no TypeScript; the consumers are a shell skill and the existing `frontier.py`, which uses subprocess. A CLI binary stands until R9 says otherwise.

**Compiler assumption (open fork F1, pending R8).** Both reflection lanes already work on this host:
- clang-p2996 `f17c8d6` is registered at `~/.local/share/mise/installs/asdf-clang-p2996/` with `clang++` in its prefix, plus the global profiles `~/.config/mise/config.{p2996,gcc16}.toml`;
- `CMakeLists.txt:16-25,47` builds `-freflection` code in both the gcc16 and p2996 lanes.

CT-59 builds in the p2996 lane first, with gcc16 as the second check lane. I am deliberately not adding a non-reflection fallback (ADR 0002). On a host with neither lane, `agent-dispatch:build` fails, the skill says so, and the native executor remains (always allowed per `executor-gate.md:3`). `accepted-decisions.md:83` prefers project-local declarations over global profiles; that is what R8 decides.

**Where the code lives in MP:**
- `schemas/agent-protocol/`
- `include/com/rsm/agent_dispatch/`
- `src/agent_dispatch/`, which holds `main.cpp` and its own `CMakeLists.txt`
- `tests/agent_dispatch/`, which holds `fake_cli.cpp` and `fixtures/`
- `.claude/skills/{claude-agent,codex-agent}/SKILL.md`, with byte mirrors under `.agents/skills/`
- Parent hunks: root `CMakeLists.txt` (`add_subdirectory`), `vcpkg.json`, `mise.dev.toml` rows.

## 3. Units

Each unit has at most 5 maintained files and about 300 lines (`codex-task-orchestration.md:204`). Fixture files are data. Every unit's checks are its tests, `ctest` in both lanes, `./dev/mise run check` and `check:acceptance-baseline`.

| Unit | Owned paths | Prereqs | Tests first | Slot |
|---|---|---|---|---|
| 59a0 build skeleton | `src/agent_dispatch/CMakeLists.txt`, `tests/agent_dispatch/{CMakeLists.txt,test_smoke.cpp}`; parent hunks for `vcpkg.json`, root `CMakeLists.txt`, the `agent-dispatch:build` and `test:agent-dispatch` rows | F2 dependency admission | jsoncons parses; SHA-256 of "abc" matches the NIST vector; one reflected struct | cxx |
| 59a schemas | `schemas/agent-protocol/*.schema.json` (4, with `$id`), `tests/agent_dispatch/fixtures/contract/` | path split from CT-52 (F8) | valid and invalid instances, consumed by 59b | parallel with 59a0, non-cxx |
| 59b json and schema | `json.hpp`, `json.cpp`, `schema.hpp`, `schema.cpp`, `test_contracts.cpp` | 59a0, 59a | ports of `test_contracts.py:37-102` | cxx |
| 59d process and files | `process.hpp`, `process.cpp`, `files.cpp`, `test_process.cpp`, `fake_cli.cpp` | 59a0 | timeout group kill, cancel gives 130, modes, `O_EXCL`, symlink refusal, environment allow list | parallel with 59b and 59c; C++ but light |
| 59c records and codec | `records.hpp`, `codec.hpp`, `request.cpp`, `adapter.hpp`, `test_records.cpp` | 59b | round trip, missing versus null, parity with the schemas, request rules | cxx |
| 59e1 Claude adapter | `claude.cpp`, `test_claude.cpp`, `fixtures/claude/` | 59c | ports of `test_adapters.py`, plus a peak-context fixture | parallel with 59e2 |
| 59e2 Codex adapter | `codex.cpp`, `test_codex.cpp`, `fixtures/codex/` | 59c | `turn.completed`, final message, collab items | parallel with 59e1 |
| 59f runner and CLI | `runner.cpp`, `main.cpp`, `test_runner.cpp`; parent hunk for the `dispatch:{claude,codex}` rows | 59d, 59e1, 59e2 | ports of `test_runner.py:92-293`, one-envelope guarantee, `started.json`, status and cancel | cxx |
| 59g1 probe | `probe.cpp`, `test_probe.cpp`, `fixtures/help/`; parent hunk for the `dispatch:probe` and `dispatch:smoke` rows | 59f | missing flag gives rc 1, shim path refused | parallel with 59g2 |
| 59g2 skills | the two `SKILL.md` files plus their mirrors | 59f; CT-38a lint is a soft dependency | skill lint, links resolve from both trees | doc lane |
| 59h live smoke | parent operation, no files | 59g1, 59g2 | admitted `claude -p` review smoke with a turn and budget cap; Codex after 2026-10-19 | admission |

Waves (three lanes at most): 59a0 with 59a; 59b with 59d; 59c; 59e1 with 59e2; 59f; 59g1 with 59g2; then 59h.

## 4. SDLC team

| Role | Agent file | Model, effort | Reason |
|---|---|---|---|
| architect | parent brief (`policy.design`) | fable, high | Contract and fork judgement is a design step. |
| test author | `implementer` with a tests-only brief | opus, high | The tests are the executable contract; the implementer may not weaken them later. |
| implementer | `implementer.md` | opus, high | Reflection plus POSIX process code needs top coding ability. |
| reviewer | `reviewer.md` | fable, high | Required by `policy.review`. |
| security reviewer (59d, 59f, 59g1) | `reviewer` with a security brief | fable, high | Spawning, the environment allow list, file modes and signal races are the attack surface. |
| doc-writer (59g2, glossary hunk) | `doc-writer.md` | sonnet, high | Bounded prose. |
| retro-writer | `retro-writer.md` | fable, high | Required by `policy.retro`. |
| extractor | `extractor.md` | haiku, low | Exit codes, SHAs and hashes as JSON. |
| merger | parent | session model | Serialized integration. |

There is no `test-author.md` or `security-reviewer.md` yet. Creating either forces a session restart (`claude-team.md:23-24`), which is fork F5.

## 5. Open forks

- **F1 compiler and bootstrap.** Recommendation: build in the existing p2996 lane, use gcc16 as the check lane, and add no fallback path. Evidence needed: R8, and a measured cold and no-op build time for `agent-dispatch:build`.
- **F2 dependencies.** Recommendation: jsoncons, picosha2 and Catch2 through the retained vcpkg installed directory under one network admission. The alternatives are vendoring the headers or writing a validator for a subset of Draft 2020-12. Evidence needed:
  - jsoncons compiles in both lanes with the third-party headers marked as system includes (the targets use `-Werror`);
  - jsoncons's Draft 2020-12 results for the keywords our schemas use.
- **F3 process layer.** Recommendation: `posix_spawn` with a self-pipe instead of libuv (`accepted-decisions.md:77` sets libuv as the engine baseline, not for a one-shot CLI). Evidence: 59d's test results.
- **F4 records.** Recommendation: hand-write them now, with the reflection parity test, and replace them when #26 generates records. Evidence: #26's status.
- **F5 roles.** Recommendation: brief the existing agent files instead of creating new ones, which avoids a restart.
- **F6 frontier adapter and gate rewrite** (A1's units 59f1 and 59f2). Recommendation: defer until CT-19, CT-40 and CT-25 have their order. Then the `frontier.py` change is limited to calling `agent-dispatch status|cancel` and deleting the `~/.codex` probes, which D113 allows as fixes and deletions.
- **F7 G6 smoke.** Recommendation: normal mode with `--agent reviewer`, read-only tools and a budget cap. Evidence: one admitted run that confirms `--agent`, `-n`, `--json-schema` and `--session-id` work together in `-p` mode on 2.1.299.
- **F8 schema ownership.** Recommendation: CT-59 owns `schemas/agent-protocol/**` now and CT-52 excludes it.
- **F9 namespace.** Recommendation: `com::rsm::agent_dispatch` for new code. The existing core still uses `aggregated_research`.

### Critical files for implementation
- /Users/rmanaloto/.codex/skills/.shared/agent-protocol/src/agent_protocol/runner.py
- /Users/rmanaloto/.codex/skills/.shared/agent-protocol/src/agent_protocol/adapters.py
- /Users/rmanaloto/.codex/skills/.shared/agent-protocol/src/agent_protocol/capture.py
- /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/CMakeLists.txt
- /Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.planning/2026-10-10-marketplace-macos-reflection-scaffold/reviews/ccm-20261014/project-import/A1-agent-dispatch-skills.md
