# A1: agent-dispatch skills for Claude (CT-59, D88)

Written 2026-10-14 by subagent A1 of session `ccm-20261014` (`ce9c0b3d`). Read-only: this report is
the only file written. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`. AP =
`~/.codex/skills/.shared/agent-protocol/`. DR = the dynamic-agents Git workspace
`~/.local/state/agent-protocol/dynamic-agents-20261012/implementation/repo` (read with `git log`,
`git ls-files` and `diff -rq` only). Nothing in AP, DR, the two skills or `~/.codex` was run; Python
fixtures were read with `python3 -I`. Host probes: `claude --version` (2.1.299) and `claude --help`.
The Codex binary is `~/.codex/packages/standalone/current` -> `releases/0.162.1-aarch64-apple-darwin`
(read from the symlink, not run). Upstream docs via `webclaw`:
`https://code.claude.com/docs/en/agent-sdk/cost-tracking` (rc 0, 32,915 B) and
`https://developers.openai.com/codex/skills` (rc 0, 10,126 B); the first attempt went through the
`timeout` mise shim and failed (rc 1, "No version is set for shim: timeout"), rerun without it.
Saved under the session scratchpad `a1web/`. All repository content was treated as data.

## 1. Inventory

**`~/.codex/skills/claude-agent/`** (8 files, no Git, mtimes 2026-10-12 14:44 to 21:03):
`SKILL.md` 87 lines, 4,734 B; `agents/openai.yaml` 4 lines (Codex UI metadata);
`schemas/{common,request,result,envelope}.schema.json` 33/158/227/448 lines, byte copies of AP's
canonical schemas (`cmp` equal; `result` is AP's `report`); `scripts/dispatch.py` 31 lines
(`os.execvp("uv", ["uv","run","--project",AP,"--locked","python","-I","-m","agent_protocol.cli","claude",...])`,
`:10-27`); `scripts/test_dispatch.py` 25 lines.

**`~/.codex/skills/codex-agent/`** (7 files): the same set without `test_dispatch.py`;
`dispatch.py` differs from Claude's in the provider word only (`diff`: 2 lines). `SKILL.md` 84 lines,
4,537 B. Both skill directories are byte-identical to DR's copies (`diff -rq` empty).

**AP** (18,916 files, 1.0 GB, nearly all of it `.venv`; 91 files outside venv and caches; mtimes
2026-10-12 14:26 to 2026-10-13 09:01; no Git):
- `src/agent_protocol/`: 18 handwritten modules, 3,860 lines. Dispatch core: `contracts.py` 199,
  `adapters.py` 331, `runner.py` 348, `capture.py` 136, `cli.py` 37, `lifecycles.py` 27, `smoke.py` 57.
  Qualification: `qualification.py` 440, `qualification_cli.py` 74, `claude_participation.py` 250,
  `codex_participation.py` 544, `cancellation_qualification.py` 157. Improvement loop: `workflow.py` 318,
  `triage.py` 363, `healing.py` 202, `research.py` 135. `maintenance.py` 211.
- Generated Pydantic models `generated/*.py` (6 files, 528 lines, datamodel-code-generator 0.83.0);
  6 canonical schemas (918 lines); 3 statecharts `charts/*.json` (69 lines, python-statemachine).
- `tests/`: 17 files, 3,430 lines, 127 `def test_`; 3 recorded native fixtures under
  `tests/fixtures/qualification/`. Tests use a fake CLI script named `claude` or `codex`
  (`tests/test_runner.py:16-74`, `cli_path` seam at `:90`): no live provider call.
- `mise.toml` 96 lines, 20 tasks; `pyproject.toml` 83 lines; `uv.lock` 909 lines, 45 packages.
- Docs: `contract.md` 258 lines; `workflow.md` 102; `GLOSSARY.md` 97; 5 ADRs;
  `docs/dynamic-agents-design.md` 229 (Q1-Q25); `docs/dynamic-agents-execution-design.md` 239;
  `docs/native-harness.md` 149. Planning state inside the package: `task_plan.md` 224 lines
  (19,835 B), `progress.md` 835 lines (114,833 B), `findings.md` 167 lines.
- `migration/migrate_v1.py` 276 lines plus 5 frozen v1 schemas; `dist/` two wheels (1.0.0, 2.0.0);
  `examples/consume.py`.

**DR**: branch `spec/dynamic-agents`, 15 commits, HEAD `affdd9a` (2026-10-13 08:42 -0500, "feat(agent-protocol):
capture bounded Codex bundled discovery"), 130 tracked files. Its spec
(`../.scratch/dynamic-agents/spec.md`, 218 lines) has 38 tickets: 01 and 26 complete; 30 (marketplace
hook transition) in progress; 33-37 (promote into the installed skills, deploy user and marketplace
guidance, enforced plugin hook transition) ready-for-agent behind their own admissions.

**MP side**:
- `.claude/skills/ticket-frontier/references/executor-gate.md` (61 lines, last commit `d420a7e`
  2026-10-13): G1-G7 at `:10-18`, probe config `:20-35`, adapter contract `:37-61`; mirrored
  byte-identically under `.agents/`.
- `.claude/skills/ticket-frontier/scripts/frontier.py` (919 lines, `d420a7e`): `GATE_ITEMS` `:67-75`,
  `executor_gate` `:664-692` (native always rc 0; any failed item rc 2), `run_probe` `:694-712`
  (kinds `rc`, `path`, `value`, `cmd`), CLI `:795-798`, `:849-850`. Tests
  `dev/test_ticket_frontier.py:293-352`; eval id 5 `evals.json:60-66`. `P/frontier.toml:13`
  `executor = "native"`; `P/frontier/` does not exist.
- Project hooks (`.claude/settings.json`): PreToolUse Bash `dev/hooks/pretooluse_gate.py`,
  SubagentStop `dev/hooks/subagent_stop_gate.py` (the lane retro gate), Stop `dev/hooks/stop_gate.py`
  (parent: integrated lanes need a passed retro). `enabledPlugins`: planning-with-files,
  mattpocock-skills, mise, astral.
- Python today: root `pyproject.toml` (`com.rsm.marketplace`, `githubkit==0.16.1`, `package = false`);
  `uv.lock` already pins pydantic 2.14.1; no `python/` tree yet (CT-39).
- DF and KB hold no copy of these skills. DF's files that mention `codex-agent` cite its Codex
  agent-role schema `schemas/codex-agent.json` (for example `.codex/agents/codex-sdlc-dispatcher.toml:1`),
  a different artefact; KB mentions `claude-agent-sdk-python` only.

## 2. Defects (assume wrong)

1. **Two divergent sources, neither under the installed path's control.** The installed trees have no
   Git (`git rev-parse`: "not a git repository", X3 §5 G2). DR is the only history, and AP differs
   from DR@`affdd9a` in 7 tracked files (`contracts.py`, `runner.py`, `qualification.py`,
   `pyproject.toml`, `contract.md`, `tests/test_entrypoints.py`, `tests/test_qualification.py`); DR alone has
   `codex_discovery.py`, `required_qualification.py`, `generated/run_record.py`,
   `schemas/run-record.schema.json`, `instruction-qualification/` and `native-validation/`. X3 §5's
   "0 differing entries" holds for the two skill directories only.
2. **The venv does not match its lock.** `.venv` has pydantic 2.13.4 and ruff 0.16.5; `uv.lock` pins
   2.14.1 and 0.16.10; `jsonref`, `python-statemachine` and `agent_protocol` itself are absent. So the
   first `uv run --locked` of any task installs (X3 §5 G3: 14 of 29 tests fail on imports).
3. **Install on the hot path, isolation lost.** `dispatch.py:12-27` and every row in `mise.toml`
   use `uv run --locked` with neither `--no-sync` nor `--offline`; `dispatch:claude` and `dispatch:codex`
   run the console script `agent-dispatch` (`mise.toml:28,33`), which drops `-I` (ADR 0003, F2 Part B);
   `test_dispatch.py:17-18` runs `python -m unittest` without `-I`.
4. **Two entry paths.** Both skills offer the mise task and `python3 <skill-dir>/scripts/dispatch.py`
   (`claude-agent/SKILL.md:21-26`, `codex-agent/SKILL.md:18-24`), against D59.
5. **Three copies of each schema, no `$id`.** The skills carry byte copies kept by `schemas:sync`, which
   writes into sibling skill directories (`maintenance.py:15-16,28-42`). No schema sets `$id`
   (CT-52 requires it).
6. **Python version split.** `requires-python = ">=3.12"`, generator target 3.12, ruff `py312`
   (`pyproject.toml:5,33,79`) against `.python-version` 3.14 and `uv lock --python 3.14`
   (`mise.toml:3,7`).
7. **Safe mode proves nothing about a lane.** The review example and K1's G6 use `claude.mode: safe`;
   on 2.1.299 `--safe-mode` disables "CLAUDE.md, skills, installed plugins, hooks, MCP servers,
   custom commands and agents" (`claude --help`). A safe-mode lane in MP would skip the PreToolUse
   gate, pwf injection, AGENTS.md and the `.claude/agents` roles. `bare` additionally needs
   `ANTHROPIC_API_KEY` ("OAuth and keychain are never read"), which this subscription setup lacks.
8. **A dispatched lane escapes the lane retro gate even in normal mode.** `claude -p` is a main
   session: Stop fires, SubagentStop does not. MP's lane check lives in `subagent_stop_gate.py:2-6`;
   `stop_gate.py:1-7` only checks integrated lanes. A dispatched implementer can stop without its retro
   record (integration still refuses later, CT-01).
9. **Context ceiling read from cumulative usage.** `executor-gate.md:56-57` (K1 §7) checks the
   ceiling against `usage.input_tokens` of the terminal object; `adapters.py:248-260` builds it from the
   terminal result's `usage` plus cache reads and writes. The result message carries "cumulative
   `usage`" across all steps (cost-tracking doc, lines 61-63 and 93), so the value grows with every
   turn and overstates context occupancy. Per-step usage on assistant messages, counted once per
   message id (same doc, line 53), is the right signal. Codex exposes no per-step figure in
   `exec --json` (not verified further).
10. **No status or cancel.** "Calls are synchronous" (`contract.md:131-133`); nothing records the
    wrapper or native PID before the final receipt (`runner.py:222-278`), yet K1's adapter needs
    `status(run_id)` and `cancel(run_id)` for background lanes.
11. **CLI found through PATH.** `shutil.which(provider)` (`runner.py:247`) runs inside a mise task whose
    PATH carries shims; this session hit a broken shim (`timeout`, above). No refusal of shim paths.
12. **Whole environment inherited.** `capture.py:113-121` passes `env=None`: the child sees every
    variable of the mise task, including `UV_PROJECT_ENVIRONMENT` (`mise.toml:51-52`), `VIRTUAL_ENV`
    and any key in the caller's shell.
13. **Implement mode cannot run tests.** `implement` maps to `acceptEdits` with
    `--permission-prompts none` (`adapters.py:33-36`), and "anything that would prompt is denied
    automatically" (`claude --help`); no role profile supplies Bash allow rules, so an implementer
    cannot run `./dev/mise run ...`.
14. **Version-pinned workarounds with no re-probe.** `contracts.py:105-106` strips `$schema` and `$id`
    because "Claude 2.1.296 rejects the 2020-12 URI"; the participation parsers recognise only the
    2.1.296 and 0.162.1 stream shapes (`claude_participation.py:1-6`, `codex_participation.py:1-5`).
    The host now runs 2.1.299.
15. **Codex review isolation is prompt-only by default.** The sandbox is inherited unless
    `codex.sandbox` is set (`adapters.py:73-75`; `runner.py:218-221` only warns). A Codex implementer
    in a Claude worktree also needs the Git common directory writable to commit; nothing handles it
    (not verified live: Codex is usage-limited until 2026-10-19).
16. **The package reaches outside itself.** `maintenance.skills()` runs Codex's system skill script
    `~/.codex/skills/.system/skill-creator/scripts/quick_validate.py` (`maintenance.py:180-186`);
    `backup()` writes under `~/.local/state` (`:154-178`); `lint` and `format` lint sibling skill
    trees by relative path (`mise.toml:21-23,59-65`).
17. **One envelope is not guaranteed.** `parse_envelope(value)` at `runner.py:332` sits outside the
    `try`; a schema violation in the assembled envelope raises instead of printing the promised single
    envelope (`contract.md:50-54`). No triggering input found; low.
18. **Tests miss the real shapes.** The fake CLI emits no per-step assistant usage
    (`test_runner.py:46-50`), so usage semantics are untested; `test_entrypoints.py:18-60` runs the
    launchers, which sync, with the caller's whole environment.
19. **The dynamic-agents design conflicts with MP's admission rules.** Q7 updates both CLIs to latest
    before every dispatch, Q5 installs extensions from trusted marketplaces automatically, Q8 enables
    features transactionally (`docs/dynamic-agents-design.md`, Settled frontier). In MP these are
    global changes that need a recorded admission each (AGENTS.md Gotchas).
20. **Planning and build output live inside an installed skill.** `task_plan.md`, `progress.md`,
    `findings.md` (150 KB together) and two wheels sit in a directory Codex scans as a skill tree.

## 3. Features to import

### 3.1 Improved design

One generic dispatcher with two provider adapters, rebuilt in MP's package from a design, not copied.

- **Contract.** Committed schemas `schemas/agent-protocol/{common,request,report,envelope}.schema.json`
  with `$id` and `additionalProperties: false` (CT-52 rules; D83 makes them the single source).
  Request: `contract_version`, exactly one of `task` or `task_file` (a `oneOf` in the schema, not
  only in code), absolute `workdir`, `mode` (`implement`, `review`), `model`, `effort`, `timeout_s`,
  `out_dir`, `schema_file`, `metadata`, and one provider block. Dropped: `format_checks`,
  `allow_subagents` (always false, see below), `claude.mode` values `bare` and the `agents_file`
  route. The default report speaks MP's lane vocabulary: `status` (completed, partial, blocked,
  failed), `summary`, `checks` [{command, exit_code}], `findings` [{severity P1|P2|P3, path, line,
  evidence}], `disposition` (PASS, PASS-with-P2/P3, FAIL, or null), `head_sha`, `changed_paths`,
  `unverified`, `proposed_edits` (`.claude/agents/implementer.md:19-21`, `reviewer.md:20`). A custom
  `schema_file` stays allowed when it is a committed file under `schemas/`. The envelope keeps the
  good AP fields (transport `status` separate from `task_status`, `execution` with exact argv, CLI
  path and version, PIDs, timestamps; `usage`; `result_schema` path, sha256, validation, errors;
  `artifacts` with sha256 and bytes; `errors`, `warnings`) but carries only a typed provider
  projection: the raw native stream stays a hashed artifact, which shrinks the 448-line envelope schema.
- **Validation.** Stdlib JSON loading that rejects duplicate keys and non-finite numbers (AP
  `contracts.py:25-42`, a good idea kept); `jsonschema` Draft 2020-12 with a `referencing` registry
  built only from the committed files and retrieval disabled. A 30-line stdlib bundler inlines the
  cross-file `$ref`s into local `$defs` for the native schema, then drops `$schema` and `$id`; the
  drop is re-checked by `dispatch:probe` per CLI version. No `jsonref`, no `python-statemachine`
  (the run lifecycle is a 12-line transition table), no generated models on the dispatch path
  (CT-52 may generate them for consumers).
- **Claude lane mode** (normal mode, parity with a native lane):
  `claude -p <fixed instruction> --output-format stream-json --verbose --json-schema <bundled report>
  --agent <role> --permission-mode <role default> --permission-prompts none --allowedTools <profile>
  --disallowedTools Agent --strict-mcp-config --session-id <uuid chosen by the runner>
  -n <parent name>.<unit> --max-turns <role maxTurns> --max-budget-usd <cap> --model <alias>
  --effort <level>`, task text on stdin. `--setting-sources` defaults to `user,project,local` and is
  recorded. `--agent` (2.1.299: "Agent for the current session") loads the real
  `.claude/agents/<role>.md` instead of an `--agents` JSON copy. The pre-chosen session id binds the
  transcript path before launch (CT-20a); the name follows D61. Project hooks stay live: the
  PreToolUse gate is the backstop for anything the allow list admits. `safe` stays available only
  as an explicit diagnostic for a broken configuration, never for lanes or G6.
- **Codex lane mode:** `codex exec --strict-config --json --color never --output-schema <file>
  --output-last-message <file> --cd <worktree> --sandbox read-only|workspace-write
  -c approval_policy="never"`, plus `--add-dir <git common dir>` for implement, `-m` and
  `-c model_reasoning_effort=...` when given, task on stdin. `codex.sandbox` is required (no
  inherited sandbox). Peak context is reported as null (unknown), never inferred.
- **Runner.** Fresh private `out_dir`, default `~/.local/state/marketplace/agent-dispatch/<provider>/<run_id>/`
  (0700, files 0600, `O_EXCL`, existing directories refused; AP `capture.py:19-52` kept). It writes
  `started.json` (run id, wrapper PID, native PID, out_dir, start time) before waiting, so a
  background caller can poll and cancel; SIGTERM to the wrapper yields `cancelled`, rc 130. The
  process runs through CT-39's core runner with a process-group stop ladder (SIGINT, SIGTERM,
  SIGKILL, one second each; AP `capture.py:55-96`) and an environment built from an allow list:
  `HOME`, `USER`, `LOGNAME`, `PATH`, `SHELL`, `TERM`, `LANG`, `LC_*`, `TMPDIR`, `PLAN_ID`,
  `PWF_PLAN_ROOT` (the main checkout, R4 P1-3), `PWF_TRUSTED_PYTHON`; nothing else. The CLI path
  comes from `dispatch:probe`, refusing any path under a mise `shims` directory. Exit codes stay AP's:
  0 completed, 1 failure, 2 invalid request, 124 timeout, 127 missing CLI, 130 cancelled. Every
  exception path still prints one envelope (fixes defect 17).
- **Detectors kept.** Native success needs exit 0, a success terminal event and a schema-valid result;
  `task_status: partial` is never rewritten (AP `runner.py:100-161`). Observed child activity (Claude
  `parent_tool_use_id` links and Agent tool uses, Codex `collab_*` items) is an `unexpected_subagents`
  error, because dispatched lanes never run teams.
- **Claude projection.** `session_id`, `model`, terminal subtype, `is_error`, cumulative usage and
  cost from the result, and `peak_context_tokens` = the largest per-step input + cache read + cache
  creation over assistant messages, each message id counted once (fixes defect 9).
- **Tests.** No live provider call: a fake `claude` and `codex` that replay recorded JSONL fixtures
  by case name (AP's fake CLI pattern, data moved out of inline code), saved `--help` text for the
  probe, saved envelopes for the frontier adapter. Fixtures carry the CLI version they came from.

### 3.2 Destinations

```
schemas/agent-protocol/{common,request,report,envelope}.schema.json   (CT-52 contract, D83)
python/src/marketplace_dev/agent_protocol/__init__.py
python/src/marketplace_dev/agent_protocol/contracts.py      strict load, validation, bundler, request rules
python/src/marketplace_dev/agent_protocol/claude.py         argv, normalize, projection
python/src/marketplace_dev/agent_protocol/codex.py          argv, normalize, projection
python/src/marketplace_dev/agent_protocol/runner.py         lifecycle, out_dir, started.json, envelope
python/src/marketplace_dev/agent_protocol/cli.py            dispatch | probe | smoke verbs
python/src/marketplace_dev/agent_protocol/probe.py          capability probe, smoke request
python/src/marketplace_dev/agent_protocol/frontier_executor.py   ticket-frontier adapter
python/tests/agent_protocol/...                             (root as CT-39 fixes it; one discovery task)
.claude/skills/claude-agent/SKILL.md, .claude/skills/codex-agent/SKILL.md
.agents/skills/claude-agent/SKILL.md, .agents/skills/codex-agent/SKILL.md   (skills:sync, byte-identical)
```

Task rows (`mise.dev.toml`, or `mise/tasks/dispatch.toml` if the D7 spike passes), all in the D60 form:

```toml
[tasks."dispatch:claude"]
description = "Run one headless Claude Code call from a request file and print one JSON envelope"
usage = 'arg "<request>" help="absolute request JSON path, or - for stdin"'
run = 'uv run --no-sync --offline python -I -m marketplace_dev.agent_protocol.cli dispatch claude "${usage_request?}"'
```

`dispatch:codex` is the same with `codex`. `dispatch:probe -- <provider>` resolves the real CLI
path, records `--version`, checks that every flag the adapter emits appears in `--help`, and exits 1
on a missing flag or a shim path (local, no model call, 10 s timeout). `dispatch:smoke --
<provider> <workdir>` builds the fixed G6 request and dispatches it (live: admitted per run). No
`setup`, `lock`, `build`, `consume`, `workflow` or pass-through rows: CT-39 owns sync and lint.

The two skills (CT-38: tasks only, under the 200-line cap, no `scripts/`): each about 60 lines.
Frontmatter `name` and a trigger-rich `description` ("run one Claude Code headless session as a
scoped implementer or reviewer and get one validated envelope; use for a fresh context outside this
session, an independent review, or the ticket-frontier claude-agent executor"). Body: (1) run
`./dev/mise run dispatch:probe -- claude` and stop on rc != 0; (2) write a request (link to
`../../../schemas/agent-protocol/request.schema.json`, which resolves from both trees); (3) run
`./dev/mise run dispatch:claude -- <abs request>`, in the background for long tasks; (4) accept only
`status == completed`, `execution.exit_code == 0` and `result_schema.validation == passed`, then judge
`task_status` and the result, since a claim is not evidence. `codex-agent` adds the sandbox rule and
the 2026-10-19 Codex availability note. No `agents/openai.yaml`: the file is optional per the Codex
skills page (line 37) and no MP skill has one; CT-07 adds it only if Codex needs it.

### 3.3 Units of CT-59 (at most five maintained files and about 300 handwritten lines each)

| Unit | Scope | Maintained files | Lines | Blockers | Admissions |
|---|---|---|---|---|---|
| CT-59a contract schemas | common, request, report, envelope schemas per 3.1 | 4 schema files | ~290 | CT-52 (owner of `schemas/**`, D83); if CT-59 goes first, CT-59a owns `schemas/agent-protocol/**` and CT-52's owned_paths exclude it | none |
| CT-59b contracts | `__init__.py`, `contracts.py`, request fixtures, `test_contracts.py`; `jsonschema` pin (parent hunk on `pyproject.toml`, `uv.lock`) | 4 | ~300 | CT-59a, CT-39 | `deps:lock` network once for the pin, recorded in the receipt (none if CT-52 already pinned it) |
| CT-59c adapters | `claude.py`, `codex.py`, recorded stream fixtures, `test_adapters.py` | 5 | ~320 | CT-59b | none |
| CT-59d runner and CLI | `runner.py`, `cli.py`, fake CLI fixture, `test_runner.py`; `dispatch:claude` and `dispatch:codex` rows (parent hunk) | 4 | ~300 | CT-59c, CT-39 (core runner row 1 below) | none |
| CT-59e probe and skills | `probe.py`, `test_probe.py` with saved `--help` fixtures, the two `SKILL.md`; mirrors generated by `skills:sync`; `dispatch:probe` and `dispatch:smoke` rows (parent hunk) | 5 | ~290 | CT-59d, CT-38a (lint and sync), CT-07 for the Codex reading of `.agents/skills` (soft: the skill text does not change) | none |
| CT-59f1 frontier adapter | `frontier_executor.py` (`request_for`, `launch_command`, `receipt_from`, `status`, `cancel`, ceiling from `peak_context_tokens`), saved-envelope fixtures, `test_frontier_executor.py` | 3 | ~280 | CT-59d, CT-19 (journal line), CT-40 (admission rows) | none |
| CT-59f2 gate rewrite | frontier `GATE_ITEMS`, `run_probe` kind `receipt`, `--team` refused for non-native; `executor-gate.md`; `evals.json` id 5; frontier gate tests | 4 | ~200 | CT-59f1, CT-39 (frontier moved into the package, D85), CT-40; serial with CT-25 (same files) | none |
| CT-59g operation (parent, not a lane) | live smokes for G6; the parent writes `P/frontier/executor-gate.config.json` | none | none | CT-59e, CT-59f2 | own admission per run: one `claude -p` smoke (`--max-turns 4`, budget cap); one `codex exec` smoke after 2026-10-19 |

Placement constraints for the third reprioritization: CT-59a-d after CT-39 (and CT-52 or the path
split above); CT-59e after CT-38a; CT-59f1 after CT-19 and CT-40; CT-59f2 before or after CT-25 but
never beside it. CT-37's fresh-session acceptance should follow CT-59d (row 7), otherwise MP grows a
second `claude -p` call path (D59).

### 3.4 Acceptance rows on existing tickets

1. **CT-39**: the core runner stops the whole process group on timeout, SIGINT and SIGTERM (SIGINT,
   SIGTERM, SIGKILL, one second each), reports `timed_out` or `cancelled`, and takes an explicit
   environment allow list; tested with a child that ignores SIGINT and spawns a grandchild.
2. **CT-52**: `schemas/agent-protocol/*` are in the codegen job list and `codegen:check`; the dispatch
   path imports no generated model.
3. **CT-38a**: the lint covers the `claude-agent` and `codex-agent` pairs: every command line names a
   declared `dispatch:*` task, no `scripts/` directory, schema links resolve from both trees.
4. **CT-07**: Codex in this repository reads `.agents/skills/{claude-agent,codex-agent}`; a read-only
   report lists skill names duplicated between `.agents/skills` and the user-level locations
   (`~/.codex/skills`, `$HOME/.agents/skills`), since Codex "doesn't merge them; both can appear"
   (Codex skills page, line 94); Codex lane roles in `.codex/agents/*.toml` match the frontier roles;
   dynamic-agents ticket 30 recorded as superseded by CT-07 and CT-08; the imported
   `c658/.codex/schemas/codex-0.162.1-agent-role.schema.json` (P `findings.md:50-56`) is CT-07's input.
5. **CT-25**: the hardening keeps the gate CT-59f2 leaves (G1, G3, G5, G6); no `~/.codex` path in
   frontier code or references; no team mode for a non-native executor.
6. **CT-32b**: the Stop gate applies the lane retro check when a main session runs in a lane worktree
   (branch `claude/<unit>-*`), with a Stop-payload fixture; this covers dispatched lanes (defect 8).
7. **CT-37**: the fresh `claude -p` session acceptance runs through `dispatch:claude`; the receipt hash
   goes into the lane record.
8. **CT-22b**: the `check` surface runs `dispatch:probe` for both providers with a timeout and reports
   P2 when the CLI version differs from the version in the newest G6 receipt; `--fix` keeps preimages
   and rolls back on a failed verify, one attempt per run (the useful idea of AP `healing.py:96-160`).
9. **CT-19**: the journal line accepts dispatched receipts with an allow list (provider, run id,
   receipt sha256, session id, status, task_status, exit codes, usage totals, peak context); no content.
10. **CT-40**: admission kinds `dispatch-smoke:claude` and `dispatch-smoke:codex`, with consumption
    receipts in the shared row format.
11. **CT-20a**: the transcript adapter finds a dispatched Claude session by the receipt's pre-chosen
    session id and a Codex run by its thread id.

### 3.5 What CT-28's G1-G7 become

| Item | Today (`executor-gate.md:12-18`) | After CT-59 |
|---|---|---|
| G1 | CT-17, CT-19, CT-22, CT-07 published, retro passed | Per executor. `claude-agent`: CT-17, CT-19, CT-22b, CT-32b, CT-59 published with retro passed; `codex-agent` adds CT-07. Probe `lane:validate` (CT-05) over those records. Splitting by executor lets the Claude executor pass without waiting for CT-07 (wave 15). |
| G2 | `~/.codex/skills/*` under Git | Retired. The source is this repository; tracking and mirror parity are part of G3. |
| G3 | AP `run test`, `schemas:check`, `codegen:check` | `./dev/mise run check` rc 0 at the integration tip with CT-11's receipt line (covers package tests, `skills:verify`, and `codegen:check` once CT-52 lands). |
| G4 | dynamic-agents 01-07 promoted, installed == DR | Retired: nothing is promoted; dynamic selection is not imported (section 4). |
| G5 | capability snapshot (tickets 04 + 12) | `dispatch:probe -- <provider>` rc 0: real CLI path, version, every emitted flag present; fixture-tested in CT-59e. |
| G6 | safe-mode `dispatch:claude` review smoke | Admitted normal-mode smoke per provider: read-only review in a throwaway lane worktree of this checkout (`--agent reviewer`, tools Read, Glob, Grep, `--max-turns 4`, budget cap). Probe kind `receipt`: the file's sha256 matches the config, `status: completed`, `execution.exit_code: 0`, `result_schema.validation: passed`, and `cli_version` equals the current probe's; a CLI upgrade fails G6 until a new smoke. |
| G7 | team-mode participation sidecar | Retired. Dispatched executors never run teams (D40 made permanent: `--disallowedTools Agent` always, child activity is an error); `--team` with a non-native executor exits 2. Team work stays native. |

How the gate then passes for `claude-agent`: CT-59a-f2 integrate and publish with passed retros, with
CT-17, CT-19, CT-22b and CT-32b; the parent runs `dispatch:probe -- claude` (G5), takes the
`dispatch-smoke:claude` admission and runs `dispatch:smoke` (G6), writes
`P/frontier/executor-gate.config.json` with the G1 `rc` note, the G3 receipt and the G6 `receipt`
probe, then `frontier.py executor-gate --executor claude-agent --write` exits 0 and writes
`P/frontier/executor-gate.json`. `codex-agent` follows after CT-07 and a Codex smoke admitted after
2026-10-19. The adapter contract in `executor-gate.md:37-61` changes accordingly: adapters live in
`marketplace_dev.agent_protocol.frontier_executor`, not `scripts/executors/<name>.py` (CT-38); launch
is `./dev/mise run dispatch:<provider> -- <request>` issued by the parent with Bash in the background;
`status` reads `receipt.json`, else `started.json` and PID liveness; `cancel` sends SIGTERM to the
wrapper; the ceiling check reads `peak_context_tokens` (null for Codex, reported as unverified); the
`allow_team` argument is removed.

### 3.6 Codex's copies afterwards, and thread `01a13185`

- **MP is the source.** Codex launched in this repository reads REPO-scope skills from `.agents/skills`
  in every directory up to the repository root (Codex skills page, line 94), so it gets MP's mirrors;
  the skills call MP's tasks relative to the checkout, so they are project-scoped by design.
- **The user-level copies must go.** While `~/.codex/skills/{claude-agent,codex-agent}` remain, Codex in
  MP lists two skills per name and the old ones call `mise -C ~/.codex/skills/.shared/agent-protocol`.
  The current Codex page names `$HOME/.agents/skills` as USER scope and does not mention
  `~/.codex/skills` (lines 97-104); whether 0.162.1 still reads it was not verified. Removal is a
  host operation outside the repository: it waits for Codex to return (2026-10-19), the thread
  handover below and the user's admission (section 5). D59's same-change rule cannot reach a global
  path, so CT-59's acceptance records the pending removal as an operation row.
- **Outside MP** nothing is installed. A user-level symlink to MP's mirror (Codex follows symlinks,
  line 107) would fail outside the checkout because the skill text runs `./dev/mise`; if the user
  wants one later, it is a DF host-setup change with its own admission and a cwd-independent call.
- **Thread `01a13185` (dynamic agents).** Its graph targets the installed trees and, through
  ticket 30, this repository's `.codex/` and hooks (P task_plan Appendix A; CT-07). After CT-59: DR
  stays as read-only history; tickets 30 and 33-37 are superseded by CT-07, CT-08 and CT-59 and are
  recorded so in `ticket-ledger.md`; tickets 02-29 can return only as MP tickets through
  `/to-tickets` against `marketplace_dev.agent_protocol`, never as edits to `~/.codex/skills`; its live
  claims, workers and worktrees under DR are untouched. The parent writes one handover brief for the
  thread when Codex returns; CT-07's coordination note is the place to cite it.

## 4. Not imported

- **The dynamic-agents program** (automatic single-agent or team selection, capability snapshots of every
  setting, immutable definitions and promotion, session leases and resume, Agent Teams, capacity
  ledger, auto-update and auto-install): its Q5, Q7 and Q8 need global admissions MP does not grant by
  default, ticket-frontier already owns model policy and scheduling, and lanes need no resume. A
  narrow version of G5 survives as `dispatch:probe`.
- **Qualification** (`agent-qualify`, `qualification.py`, both participation parsers, cancellation
  qualification, about 1,465 lines): team mode is not offered and the parsers are pinned to old CLI
  shapes. Only the `unexpected_subagents` detector stays.
- **Improvement loop** (`workflow.py`, `triage.py`, `research.py`, `workflow.md`): MP has the retro
  gate (CT-01), the retro-writer, the decisions ledger and the frontier learning ledger; research
  belongs to the other import reports. `workflow.py` also reads the user-typed retro skill file and runs
  it through a dispatched agent, which bypasses the typed-stage rule. `healing.py`'s
  preimage-and-rollback idea goes to CT-22b (row 8); the module does not.
- **Migration** (`migrate_v1.py`, five v1 schemas): MP is greenfield (D59); no v1 receipt exists here.
- **Maintenance** (`backup`, `sync`, `copies`, `skills`): replaced by CT-38a `skills:sync` and
  `skills:verify` and CT-52 `codegen:check`.
- **Packaging** (`dist/` wheels, `build`, `consume`, `consume:wheel`, `examples/consume.py`): the
  package is consumed inside MP only.
- **Options**: `format_checks` (and the `format-nongpl` extra), `claude.mode: bare`, `claude.agents_file`,
  `allow_subagents: true`, the `--agents` JSON route.
- **Dependencies**: `jsonref`, `python-statemachine`, `datamodel-code-generator` in the runtime env
  (CT-52 decides its generator for its own task).
- **`agents/openai.yaml`**: optional UI metadata (see 3.2).
- **Planning files and ADRs inside AP**: history, archived with the sunset, not MP guidance. The
  vocabulary worth keeping ("transport status" versus "task status", "envelope", "dispatched lane")
  becomes three GLOSSARY entries in CT-59f2 as a parent hunk.
- **DF's `codex-sdlc-team` dispatcher roles**: a different artefact; left to the dotfiles import report.

## 5. Sunset checklist

When CT-59a-f2 are integrated and published, the Claude G6 receipt is recorded, Codex has returned
(after 2026-10-19), the thread handover in 3.6 is delivered, and the user admits the host operation:

1. Archive `~/.codex/skills/.shared/agent-protocol/` without `.venv`, `dist/`, `.ruff_cache` and
   `__pycache__` into a dated tarball under `~/.local/state/marketplace-imports/` with a manifest of
   sha256 per file (as `codex-worktrees-20261013` was), then delete the directory (18,916 files,
   1.0 GB).
2. Delete `~/.codex/skills/claude-agent/` (8 files) and `~/.codex/skills/codex-agent/` (7 files) after
   recording their sha256 in the same manifest; then confirm Codex in MP lists one `claude-agent` and
   one `codex-agent` (CT-07 row 4 report).
3. Leave `~/.local/state/agent-protocol/` (smoke, workflow, migration receipts and DR) until thread
   `01a13185` is closed; then the user chooses retention, as D80 does for other Codex state.
4. In MP, removed by CT-59f2 in the same change (D59): the `~/.codex` probes and paths in
   `executor-gate.md:13-14,26-27,55` and `frontier.py:68-74` (both trees), the G1-G6 wording of
   `evals.json:62-66`, and the `--team` path for non-native executors.
5. In MP, kept as history: `P/findings.md:50-56`, X3 §5, K1 §7 and decisions D33 and D40 (D40 is
   superseded in effect: dispatched executors never run teams).
6. DF, KB and TR: nothing to delete for this feature; none of them holds these skills or the package.

Could not verify: whether `--agent`, `-n` and `--json-schema` combine in `-p` mode on 2.1.299; which
init-event fields report loaded agents and plugins; whether a dispatched run started with Bash in the
background survives the parent's `/clear` (one optional second CT-59g run can test it); whether
Codex 0.162.1 still scans `~/.codex/skills`; Codex per-step usage; and the G3 outcome of AP under a
complete venv.
