# KB-A: knowledge-base Claude and Codex agent surface, and the aggregated-research backend (project import, 2026-10-14)

Agent KB-A, read-only. KB = `/Users/rmanaloto/dev/github/ray-manaloto/knowledge-base`, branch `main`,
HEAD `f086f731` (2026-10-05). KB working tree before and after this review: ` M .codex/config.toml`
(a 242-line comment deletion), `?? .agents/skills/model-registry/`, `?? .codex/agents/claude-advisor.toml`,
two untracked report directories. MP = this repository at `21af565`; P = the plan directory. No KB,
DF or `~/.codex` code ran: KB files were read with `cat`, `sed`, `grep`, `git log`, `git show`,
`git diff`, and `python3 -I` reading JSON and TOML only. Paths are KB-relative unless prefixed `MP:` or
`DF:`. Builds on `grill-facts/F3-knowledge-base-comparison.md` (F3) and `tr-import/S-skills-agents-plugin.md`
(S) without repeating their rows; Phase 4a U7 and Phase 4b rows already adopted from them are cited as
"already covered" rather than re-proposed. Ticket state read from P/task_plan.md including D83-D90 and
CT-59 (spec #11 issue numbers are draft numbers plus 11, per P/ticket-index.md).

## 1. Inventory

### 1.1 Skills (16 directories per tree; 15 have a SKILL.md)

| Skill (`.claude/skills/`) | SKILL.md lines | Other files | Last commit | What it does | `.agents` mirror |
|---|---|---|---|---|---|
| artifact-download | 25 | none | 2026-08-13 | one fence: `mise run kb-artifact-download` (provider-neutral artifact transfer and receipt) | identical |
| clear-prep | 489 | references/plan-archive.md (43) | 2026-09-08 | pre-/clear handoff: next task, corpus loop, docs sync, memory, handoff, resume line | identical |
| eli5-visual | 438 | none (pairs with `.claude/output-styles/eli5-visual.md`, 230) | 2026-08-31 | explain as a published visual artifact | identical |
| goal-engineering | 219 | references/conventions.md (147), rubric.md (311); stray untracked `.agent/state/graph-first/<uuid>.queried` | 2026-08-08 | author and audit `/goal` completion conditions | differs (stray state only in `.claude`) |
| graphify | 743 | 8 references, `.graphify_version` | 2026-08-13 | vendored graphify runbook | 35-line stub with a different description |
| kb-curator | 263 | evals/evals.json | 2026-08-28 | ingest a source into the graphify corpus | identical |
| kb-recall-work | 80 | none | 2026-09-09 | prior-work census before design (`mise run kb-recall-work`) | identical |
| kb-reclaim | 154 | evals, references/gotchas.md | 2026-08-08 | host disk survey and reclaim | identical |
| kb-review | 500 | references/lanes.md (483), repo-smells.md (59) | 2026-10-02 | one cold cross-family reviewer, two rounds, SHA-keyed receipt `kb-ship` gates on | identical |
| kb-session-reflect | 137 | none | 2026-09-08 | read the SessionEnd self-reflection of the previous round | identical |
| kb-session-review | 322 | drives `.claude/workflows/session-review.js` (1307) | 2026-10-04 | whole-round review Workflow; can compose the handoff | identical |
| model-registry | none | `.claude-plugin/plugin.json` (6), `hooks/hooks.json` (4), `hooks/register.ts` (129) | 2026-10-03 | a function-hook plugin placed in the skills tree | untracked copy; third copy at `python/src/kb_setup/plugins/model-registry/` |
| orchestrator-routing | 149 | none | 2026-10-02 | codex/antigravity/Claude routing doctrine | identical |
| session-resume | 218 | none | 2026-09-08 | read the newest handoff, reconcile with repo, offer next step | identical |
| skillopt-reviewed | 21 | none | 2026-08-13 | stage a SkillOpt cycle from a reviewed ledger | identical |
| tool-currency | 146 | none | 2026-09-11 | pinned-tool currency loop (pins, release notes, tracked issues) | identical |

Totals: 3,904 SKILL.md lines in `.claude`; 8 of 15 exceed MP's 200-line cap. No `.claude/commands/`:
skills are the only slash commands (`tool-currency` sets `user-invocable: true`; `clear-prep` sets
`disable-model-invocation: false`).

### 1.2 Agents

`.claude/agents/` 11 files, 1,511 lines: claude-advisor (58, model fable, read-only), kb-adversarial-verifier
(113, opus, has Write and Edit), kb-codex-advisor (176), kb-codex-astra-advisor (231), kb-codex-astra-reviewer
(350), kb-codex-implementer (71), kb-corpus-curator (99, no `tools`), kb-extraction-worker (82),
kb-synthesist (92), kb-tool-researcher (132, no `tools`), premise-verifier (107, opus, Read/Grep/Glob; body
ported from fable-orchestrator 1.21.0 under MIT, `premise-verifier.md:9-37`). Dates 2026-08-06 to
2026-10-03. `.codex/agents/` 10 tracked toml (1,440 lines, 2026-10-03) plus untracked `claude-advisor.toml`.
MP has 6 Claude roles (140 lines) and 3 Codex role toml.

### 1.3 Hooks, settings, mods, workflows, types

- `.claude/settings.json` (271 lines, 2026-10-04): env flags at lines 2-6 (`CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`,
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`); PreToolUse
  `Bash|Grep` graphify guard (10-18) and `uv run ... kb-setup hookguard` (19-28); `Read|Glob` graphify guard
  (29-38); eight `Edit|Write` entries with `if` filters running `kb-instruction-edit-guard` (39-126); `Bash`
  `kb-instruction-shell-write` (127-136); SessionStart `kb-currency-check`, `kb-codex-config-check`
  (138-153) and `kb-env-refresh` on `startup|resume|clear|compact|fork` (154-163); SessionEnd
  `brain-transcript-audit` and `kb-session-reflect` (165-179); 20 `enabledPlugins` entries including
  `aggregated-research@ray-manaloto` (202); `outputStyle: "ELI5 Visual"` (266), `teammateMode`,
  `worktree.baseRef: head` (267-270).
- `.claude/settings.local.json` (untracked by the global gitignore): keys `permissions.additionalDirectories`
  (4 sibling paths), `enableAllProjectMcpServers`, `enabledMcpjsonServers`, `skillOverrides`; no
  `enabledPlugins` and no `env`.
- `.claude/mods/kb-settings-guard/` (plugin.json 8, hooks.json 4, protected-paths.ts 27, register.ts 205;
  2026-09-11 to 2026-10-03): function hook denying a subagent writes to guard files in the main checkout.
- Hook engines in `python/src/kb_setup/`: hook_guard.py (525, the Bash chain), secret_guard.py (439),
  destructive_git.py (347), stage_explicitly.py (126), absent_binary.py (386), codex_lane.py (203),
  instruction_edit_guard.py (347), instruction_shell_write.py (401), skill_lint.py (328), md_budget.py
  (759), env_refresh.py (263); dates 2026-08-22 to 2026-09-15.
- Mod toolchain: `.claude/types/claude-code.d.ts` (13,186 lines, written by Claude Code 2.1.277),
  `claude-code-mcp.d.ts` (5), README (15), `tsconfig.json` (25, strict, noEmit), fnhook_gates.py (644),
  claude_types.py (137), mod_runtime.py (1,011, legacy; documents the 2.1.287 generator change at
  `mod_runtime.py:20-40`).
- `.claude/workflows/`: session-review.js (1,307), kb-extract.js (287), kb-tool-review.js (280).
- Handoff engines: handoff.py (971), handoff_reconcile.py (583), context_usage.py (396), session_state.py
  (646), next_ticket.py (492), gates.py (1,226), session_reflect.py (910), session_select.py (514),
  recall_work.py (1,351).
- `.codex/config.toml` (41 lines committed form): Claude env flags in the Codex shell (5-7), default
  subagent model (10-11), local MCP servers `kb` and `kb-memory` with `default_tools_approval_mode =
  "approve"` (13-32), hosted `graphify` MCP (34). `.codex/hooks.json` (67, 2026-10-04): PreToolUse
  graphify and hookguard, PostToolUse `apply_patch` edit-check (27-31), SessionStart currency, SessionEnd
  audit and reflect.
- `.claude/rules/`: 23 files, 2,920 lines, 166,903 bytes; only `ci-local-parity` and `md-size-budgets`
  carry `paths:`. MP has 3 rules, all path-scoped, and about 5 KB of eager guidance.

### 1.4 The aggregated-research entry point and plugin pieces

- Entry point: `pyproject.toml:39-41` `aggregated-research = "kb_setup.research.cli:main"` beside
  `kb-setup = "kb_setup.cli:main"`.
- `python/src/kb_setup/research/` (1,804 lines, 2026-08-30): cli.py (46; verbs `trackers`, `links`,
  `packages`, `codesearch`, each routed to `kb_setup.cli.main(["research-<verb>"])`), trackers.py (333,
  gh issues and PR search with control arms), links.py (357, lychee 0.24.2), packages.py (474, deps.dev v3
  over httpx2), codesearch.py (592, grep.app MCP over httpx2).
- `schemas/research-record.schema.json` (184, 2026-08-30) generating `kb_setup/generated/research_record.py`;
  `schemas/deps-dev-api-v3.proto` and two Google API protos; events.py (251, JSONL sink).
- Tests: tests/test_research_{cli,trackers,links,packages,codesearch}.py, test_plugin_validate.py (298).
- `plugin_validate.py` (326, 2026-08-28): validates MP's marketplace and plugin manifests against
  schemastore and runs `claude plugin validate` over a path to MP.
- `docs/roadmap/aggregated-research-chain.toml` (2026-09-12): KB's tracked chain; plugin entries #581-#589
  (breadth verb, report step, lane contract, spine dispatch and verify loop, budget tuning, CLI packaging,
  release mechanics, empty-project definition of done) and #616, plus function-hook (#754-#773) and
  upgrade-system (#728-#739) entries.
- Research reports that back the verbs: `docs/research/reports/2026-08-27-deep-research-internals.md`,
  `2026-08-27-lychee-from-python.md`, `2026-08-28-lychee-py-spike-result.md`,
  `2026-08-29-codesearch-feasibility.md`, `2026-08-29-deps-dev-packages-prototype.md`,
  `2026-08-29-deps-dev-sdk-evaluation.md`; design pages `docs/artifacts/*aggregated-research*.html`.
- KB config that knows the plugin: `.gitignore:12` and `.gitleaks.toml:60` (`.research/` output zone),
  `.claude/settings.json:202`.

MP side: `MP:plugins/aggregated-research/` (13 tracked files, 2026-08-29 except AGENTS.md 2026-10-10); its
`mise.toml:2-3` installs `pipx:git+https://github.com/ray-manaloto/knowledge-base.git` at
`a872cb016feb5512994b37330ce6a387c5732253` (KB 2026-08-28, 109 commits behind HEAD), whose CLI has only
`trackers`. MP pins that contract in `MP:docs/agents/legacy-trackers-boundary.md`,
`MP:docs/agents/python-bridge-placement.md`, `MP:evidence/legacy-trackers/`, `MP:dev/legacy_trackers_fixture.py`
and `MP:ci/acceptance.sh:251, 269, 282, 315`.

## 2. Defects (assume wrong; evidence)

### 2.1 aggregated-research backend and plugin

- KB-D1. MP's shipped plugin depends at runtime on KB: `MP:plugins/aggregated-research/mise.toml:2-3`
  and `MP:ci/acceptance.sh:251` (`EXPECTED_INSTALLS="pipx-git-https-github-com-ray-manaloto-knowledge-base-git ty "`).
  DF pins the same package at `e8fe42ae` (`DF:python/pyproject.toml:40`) for md_budget, currency, evals and
  launch. Deleting the KB repository breaks every fresh plugin install.
- KB-D2. A 1.3 GB closure (`MP:plugins/aggregated-research/README.md:60`) for a 333-line module that needs
  msgspec and `gh`: at the pin, runtime dependencies are `anthropic`, `graphifyy[all]==0.9.50`, `msgspec`,
  `skillopt` (VCS) and `structlog` (`git show a872cb01:pyproject.toml`). `requires-python = ">=3.14"`
  (`pyproject.toml:5`) while the plugin's `mise.toml` pins no Python (which interpreter pipx picks:
  UNVERIFIED).
- KB-D3. Two-hop string dispatch: `research/cli.py:42-46` routes into the 1,238-line `kb_setup/cli.py`
  dispatcher (the console-script pattern D60 rejects).
- KB-D4. Silent truncation: `_search_argv` (`trackers.py:91-96`) sends no `per_page` and reads one page,
  so `hits` holds at most the first page while `total_count` sums full counts (`trackers.py:169-180`);
  the record has no truncation field.
- KB-D5. A weak control arm: the arm drops the term (`trackers.py:182-198`), proving the channel holds
  items, not that the term-shaped query can match; a term the search tokenizer discards still yields a
  "discriminating" null.
- KB-D6. `--out` writes non-atomically and creates any parent directory (`trackers.py:310-312`; the pin at
  `:281-282`).
- KB-D7. Undeclared host tools: `gh` (trackers) and `lychee` (links; pinned 0.24.2 only in KB
  `mise.toml:260`) are absent from the plugin's `mise.toml`.
- KB-D8. KB HEAD broke the v1 record: `git diff a872cb01 HEAD -- python/src/kb_setup/research/trackers.py`
  moves `has_issues`/`has_discussions` into a `Trackers` object and adds `links`/`packages` fields, so a pin
  bump would fail MP's #24 fixtures and the frozen `ci/acceptance.sh`.
- KB-D9. codesearch returns at most one hit per query (`codesearch.py:57-58`) and stamps observation time as
  `Hit.date` (`codesearch.py:12-14`): a null from it is near worthless without an arm.
- KB-D10. MP's plugin skill leaks KB: `mise run kb-query` (`MP:.../SKILL.md:27, 228`), `kb-manifest-add`
  and `kb-add` (222-223), KB rule `use-tool-builtins.md` (105), KB path `sources/agent-harness-docs/...`
  (108), optional `antigravity:research` as a step (120), raw `curl` to deps.dev (146) where KB already has a
  `packages` verb; 240 lines against CT-38's cap.
- KB-D11. `MP:plugins/aggregated-research/spine-budgets.toml` holds four constants nothing reads; the loop
  that would read them is KB #585/#586, open.
- KB-D12. Circular and stale enablement: KB enables `aggregated-research@ray-manaloto`
  (`settings.json:202`) while that plugin installs KB; `.claude/CLAUDE.md:63-66` says settings.local.json
  overrides it to false, but settings.local.json has no `enabledPlugins` key, so the claimed effective count
  (16) is wrong.
- KB-D13. `plugin_validate.py:20-33` parses human glyph lines instead of JSON, fetches schemastore live
  (`:8-10`), and allow-lists "No version specified" (`:14-19`), which D89 (version 0.1.0) supersedes.

### 2.2 Skills

- KB-D14. 8 of 15 skills exceed 200 lines (graphify 743, kb-review 500, clear-prep 489, eli5-visual 438,
  kb-session-review 322, kb-curator 263, goal-engineering 219, session-resume 218).
- KB-D15. Mirror exceptions hide drift: the `.agents` graphify skill is a 35-line stub with another
  description and no references; skill_lint skips graphify and dot-paths (F3, `skill_lint.py:67-75`), so a
  stray hook state file `.claude/skills/goal-engineering/.agent/state/graph-first/<uuid>.queried` (ignored by
  `.gitignore:190`) sits inside a skill tree unnoticed.
- KB-D16. A plugin in the skills tree: `.claude/skills/model-registry/` has no SKILL.md, carries
  `.claude-plugin/plugin.json` and a hooks module, is duplicated byte-for-byte at
  `python/src/kb_setup/plugins/model-registry/` (`diff -r` empty) and untracked at `.agents/skills/`; it is
  in no `enabledPlugins`, so whether it ever loads is UNVERIFIED.
- KB-D17. Layering exceptions (F3): clear-prep:106-117 and session-resume tell agents to run
  `uv run kb-setup session-state` because mise redaction mangles SHAs; session-resume falls back to a
  version-pinned `planning-with-files/3.12.0` cache path while 3.24.0 is installed.
- KB-D18. kb-recall-work signals "matched nothing" with rc 127 (`kb-recall-work/SKILL.md`, "The two exits"),
  the shell's command-not-found code that KB's own absent_binary guard treats as a never-ran probe.

### 2.3 Agents

- KB-D19. Roles with more power than their job: kb-adversarial-verifier (a refuter) has Write and Edit;
  kb-corpus-curator and kb-tool-researcher declare no `tools` and inherit everything; the Codex advisors
  inherit their model.
- KB-D20. Codex twins drift: 11 Claude roles against 10 tracked Codex toml, `claude-advisor.toml` untracked;
  "nothing generates one from the other" (F3, CLAUDE.md:151).

### 2.4 Hooks and settings

- KB-D21. A hook that may sync on every call: `uv run --project python kb-setup hookguard` on every Bash and
  Grep (`settings.json:19-28`, `.codex/hooks.json:19`) carries no `--no-sync` or `--offline`, and uv's
  default run syncs the project environment, so a guard can mutate `.venv` and pays that check per call.
  Two more hooks run `.venv/bin/graphify` directly (`settings.json:14, 34`), outside mise.
- KB-D22. Coverage by duplication: eight `Edit|Write` entries (`settings.json:39-126`) express four path
  classes because a hook `if` matches the actual tool name (`instruction_edit_guard.py:40-50`);
  NotebookEdit, `.claude/agents/**`, `AGENTS.md` and `.codex/**` are unguarded.
- KB-D23. The chain fails open: every guard wrapper in `hook_guard.py:331-500` returns None on error, and
  destructive_git fails open when git cannot be asked (`destructive_git.py:22-25`); MP's gates use
  `onFailure: block`.
- KB-D24. SessionEnd writes into the tree (`.agent/brain-audit.md`, `settings.json:170`) and can take
  120 s; two SessionStart checks add up to 60 s before the first prompt.
- KB-D25. Codex surface: every Codex hook resolves `${CLAUDE_PROJECT_DIR:-.}` (`.codex/hooks.json:9, 19,
  31, 44, 55, 60`), which falls back to cwd unless Codex sets that variable (UNVERIFIED); Claude env flags
  are exported into the Codex shell (`config.toml:5-7`); both local MCP servers auto-approve every tool
  (`config.toml:20, 32`); a hosted graphify MCP (`config.toml:34`) is an upload route; an uncommitted
  242-line edit sits in `.codex/config.toml`.
- KB-D26. Project-wide `outputStyle: "ELI5 Visual"` (`settings.json:266`) imposes one person's style on
  every session and every lane.

### 2.5 Mods

- KB-D27. kb-settings-guard never ran (`register.ts:11-15`: in neither `extraKnownMarketplaces` nor
  `enabledPlugins`); its NotebookEdit branch reads `file_path`, which NotebookEdit does not carry, so it can
  never deny (KB #772); bare suffixes `mise.toml` and `hk.pkl` (`protected-paths.ts:16-26`) match a file of
  that name in any directory; worktree authority keys on `.git` being a file (`register.ts:119-120`), which is
  also true inside a submodule.
- KB-D28. KB contradicts itself on Bash hooks: `register.ts:47-61` records that even a passthrough Bash
  function hook breaks every Bash call in `Agent(isolation: "worktree")` subagents (citing
  anthropics/claude-code#92533; UNVERIFIED here), yet model-registry intercepts Bash through
  `classic.PreToolUse` (`model-registry/hooks/register.ts:116-123`).
- KB-D29. model-registry blocks SessionStart on `mise run models-check` for up to 45 s
  (`register.ts:48-50, 104-114`) and spawns `mise run models-classify` per Bash or Agent call while any
  vendor reads invalid.

### 2.6 Guidance

- KB-D30. Eager context: 21 of 23 rules lack `paths:` (166,903 bytes of rules) plus 288 lines of CLAUDE.md
  load every session; md_budget's backstop is per file (`EAGER_BYTE_BACKSTOP = 24_000`,
  `md_budget.py:95`), so the total is unbounded. Neither `CLAUDE.md` nor `.claude/CLAUDE.md` imports
  `AGENTS.md`.

### 2.7 MP defects found by the comparison

- MP-D1. `MP:dev/handoff.py:122-128, 315, 319-327` (untracked): a failed `git` call returns None and is
  rendered as `0\t0` ahead/behind and `staged 0, unstaged 0, untracked 0`, so a timed-out probe reads as a
  clean, in-sync tree. KB's session_state prints `COULD NOT ASK` for this case (F3).
- MP-D2. No MP skill or task answers "what already exists on this topic" across files, reports, lanes,
  branches, worktrees, issues and plans; the import reviews themselves are hand searches.

## 3. Features to import

### 3.1 aggregated-research: what MP lacks and where KB is worse

MP lacks: the `links`, `packages` and `codesearch` verbs (KB HEAD, 2026-08-30) and their research
(deps.dev protos, grep.app spike, lychee exit-code study); a structured per-call event line with outcome
class and duration (`events.py`); a report renderer and the claim-verify spine (KB #583, #585, #586, open in
KB too, so nobody has them); an independent backend (the plugin installs KB).

KB is worse on: install weight and unpinned interpreter (KB-D2), dispatch (KB-D3), pagination and truncation
(KB-D4), arm strength (KB-D5), output writes (KB-D6), declared tools (KB-D7), contract stability (KB-D8),
codesearch recall (KB-D9) and validation (KB-D13). MP's pinned v1 contract, fixtures, confinement wrapper
(`bin/mise-env`) and helper-process bridge decision are better than anything in KB and stay.

Spec #11 already owns the native migration: #28 additive verbs, #31 outcome tracer, #44 controlled-empty,
#48 native delivery, #49 parity, #53 thin adapter, #35-#41 operations. The KB verbs are not among #35-#41.

### 3.2 New tickets (provisional ids)

| Id | Title | Size | Improved design (not a copy) | MP destination | Blockers | Admissions |
|---|---|---|---|---|---|---|
| KB-A-1 | Plugin legacy backend owned by MP | M | Replace the KB pipx pin with an MP-owned minimal runtime package: the `trackers` verb only, msgspec plus stdlib, no string dispatcher, Python pinned in the plugin `mise.toml`, `gh` declared, `--out` written atomically; output byte-identical to the #24 hit and armed-null fixtures (`MP:evidence/legacy-trackers/`) through `MP:dev/legacy_trackers_fixture.py`; install source measured first (mise `pipx:` from an MP git subdirectory versus a local path under `${CLAUDE_PLUGIN_ROOT}`: both UNVERIFIED); `EXPECTED_INSTALLS` updated in the same change; the KB pin removed (D59). Install size measured before and after | `plugins/aggregated-research/runtime/` (package `aggregated_research`), `plugins/aggregated-research/mise.toml`, `ci/acceptance.sh` | CT-08 (both files are baseline), CT-39 (package rules), D89 version bump; user decision: `MP:docs/agents/python-bridge-placement.md:5-8` names the KB pin as the rollback route, and D60's single package is for dev tooling, not shipped runtime | fresh-session plugin install and the OCI `ci/acceptance.sh` run |
| KB-A-2 | `packages` operation (deps.dev v3, keyless) | M | Spec #11 operation shape: committed request/result schema (D83), provider/route/upstream identity rows (#32), immutable attempts (#34); not-found, transport error and unparsable payload as distinct outcomes; package identity segments percent-encoded; bounded licences and links; fixtures from KB's prototype reports, no network in tests | spec #11 layout: `schemas/`, the native core, the #28 additive verb | #32, #33, #34 (draft 21-23), #28 | network for the live arm |
| KB-A-3 | `links` operation (cited-link resolution) | S | URLs passed through a file, never positional (lychee scrapes positional URLs, `links.py:13-17`); branch on parsed output, not exit code; at most 60 URLs per call; lychee pinned as a project tool; results feed the report renderer's citation column | as KB-A-2 | as KB-A-2; lychee pin (CT-26a) | tool install; network |
| KB-A-4 | `codesearch` operation (grep.app, presence only) | S | Declared presence-only: a hit is evidence, an empty result is never a null without a same-shape known-present arm; observation time recorded as `observed_at`, not `date`; SSE parse anchored to the first triple (`codesearch.py:57-62`) | as KB-A-2 | as KB-A-2 | network |
| KB-A-5 | Research report renderer | M | Model-free and deterministic: stored attempt records (#34) render to Answer, Ranked sources (primary separated from secondary), Every null with its arm, Not measured, Repositories touched; golden byte-identical output; citations checked through KB-A-3 and CT-44's cite-verify contract; replaces the plugin skill's hand-written "Output" section | plugin CLI verb `report`, committed schema, `plugins/aggregated-research/skills/aggregated-research/` | #34, #43 (coverage verdict), CT-44 | none |
| KB-A-6 | Claim-verify spine | M | Consumes `spine-budgets.toml` (votes per claim 3, refutations 2, fetch 15, claims 25) or the file is deleted in the same change (D59); voters and refuters are read-only plugin agents shipped in the plugin (consumer repos have no MP tasks), cross-family voters via CT-59's protocol where installed; every vote and refutation stored as an attempt; model usage recorded per #47; budgets tuned only from measured runs (KB #586) | `plugins/aggregated-research/agents/`, the plugin skill, `spine-budgets.toml` | KB-A-5, CT-59, #47 | capped model spend per run (fnox profile) |
| KB-A-7 | `recall:work` prior-work census | M | Probes: tracked files, P/reviews and lane records, `decisions.jsonl`, branches with ahead/behind and merged-by-squash, worktrees, GitHub issues open and closed, plans (P and `~/.claude/plans`), conversation history through AgentsView instead of graphify memory, and the offline corpus once CT-43 lands; each probe prints examined beside matched and `could_not_ask` separately; rc 0 found, 1 matched nothing, 2 could not ask (never 127); stems printed; report under `evidence/`, not a gitignored dir; sibling roots DF, KB, TR only by flag during the sunset; skill pair calls only the task | `python/src/marketplace_dev/recall/`, `mise.dev.toml` row, `.claude/skills/recall-work/` and `.agents/skills/recall-work/` | CT-39, CT-38a; CT-43 optional | read-only `gh` |

### 3.3 Acceptance rows on existing tickets

Already covered and not re-proposed: CT-37 rows (1)-(6) (reconcile, citation linter with per-commit gate
record, plan hash, new-terminal carrier probe incl. KB's `CLAUDE_ENV_FILE`, measured context trigger,
headless round trip); CT-38 rows (allow-list lint shared with the PreToolUse table, raw-byte sync and verify,
200-line cap, no per-skill mise bypass); CT-07 with CT-56 (D85) rows from S-a (computed counts, read-only roles
lack Edit and Write, Codex mapping); CT-57 from S-b (`--strict --json`, non-null manifest); CT-58 from S-c
(no `/Users/`, CLAUDE.md imports AGENTS.md, no numeric claims).

| Ticket | Row (improved design) | KB evidence |
|---|---|---|
| CT-02b | 1. The command classifier treats shell writes to protected paths as writes: redirects (`>`, `>>`, `>\|`, `&>`, numeric prefixes), `tee`, `sed`/`perl` in-place, `python -c` with a write call and a path literal, tracked across `cd`. Protected: both skill trees, `.claude/settings*.json`, `dev/hooks/**`, `mise.dev.toml`, `hk.pkl`. Blind spots (`find -exec`, `xargs`, `sh -c`, `eval`, `$(...)`) are table rows with "not covered" fixtures, never implied. MP sessions are told to edit through Bash, so an Edit/Write-only guard covers the least-used door | `instruction_shell_write.py:1-60` |
| CT-02b | 2. One PreToolUse entry for `Edit\|Write\|NotebookEdit\|Bash` runs the shared classifier, which reads the path itself; no per-glob `if` duplication; NotebookEdit reads `notebook_path`; one fixture per tool | `settings.json:39-126`; KB #772 |
| CT-02b | 3. Secret-printing commands denied at command position after tokenising (`fnox get`, `fnox export`, `fnox list --values`, `doppler secrets get`/`download`/bare, `security ... -w`/`-g`, `printenv` or `env` in a secret-injected process, `${VAR:+...}` on a secret name); presence probes (`[[ -v KEY ]]`) and name-only listings allowed; quoted text never matches | `secret_guard.py:1-45` |
| CT-02b | 4. Work-destroying git denied only when `git status --porcelain` shows something to lose (`reset --hard`, `checkout -- .`, `restore .`, `clean -f`); blanket `git add -A` or `git add .` denied with "name the paths"; a failed status probe denies with its reason (MP fails closed, KB fails open) | `destructive_git.py:1-25`, `stage_explicitly.py`, `hook_guard.py:347-433` |
| CT-02b | 5. A probe whose command word is not installed, or is a mise shim with no version, is denied with "probe the binary, not its name", so a 127 never reads as the tested tool failing | `absent_binary.py:1-20`; plugin SKILL.md trap 4 |
| CT-02b | 6. A call whose payload carries `agent_id` and targets a path outside its lane's `owned_paths`, or a guard file of the main checkout, is denied; destination decides, not the caller's cwd; plus one live arm that dispatches a real subagent and asserts the deny, because a unit fixture cannot catch a renamed field (overlaps CT-19) | `kb-settings-guard/hooks/register.ts:31-38, 110-125` |
| CT-38 | 1. Plugin skills (`plugins/*/skills/**`) are linted with a per-plugin allow-list: command heads are the plugin's own `bin/` executables and its declared dependency plugins' skills; `./dev/mise run` and any `kb-*` task are rejected there, since a consumer repository has neither | `MP:.../SKILL.md:27, 222-228` |
| CT-38 | 2. The lint fails when it examined zero skills and prints examined and matched counts | `skill_lint.py:210-217` (F3) |
| CT-38 | 3. Every directory in either skill tree has a SKILL.md and holds no runtime state; `skills:verify` reports a plugin manifest, a hooks module or a dot-state file inside a skill directory as a failure | KB-D15, KB-D16 |
| CT-58 | 1. Eager-load budget: the bytes of always-loaded guidance (root import closure plus every rule without `paths:`) are measured each run and capped as a total, not per file; a new rule without `paths:` fails unless listed | KB-D30 |
| CT-58 | 2. A skill description is at most 1,536 characters (the listing's hard truncation) and states when to use the skill; checked at edit time through CT-02b's classifier as well as in the lint | `md_budget.py:90-92`; `instruction_edit_guard.py` |
| CT-29 | 1. Every probe in `session:handoff` state has three outcomes: value, empty, `COULD NOT ASK`; a failed git, gh or doctor call never renders as 0 or none (fixes MP-D1) | `session_state.py` (F3) |
| CT-29 | 2. The handoff's next action comes from the frontier (the Phase 4b order until CT-40, then `frontier.py`); the check refuses a named ticket the ledger or tracker shows closed; the hand-written template keeps notes only | `next_ticket.py`; `aggregated-research-chain.toml:1-20` |
| CT-29 | 3. session-resume reads the previous session's kept reflection (from CT-20b) and says "no kept reflection" in words when absent, never "clean" | `kb-session-reflect/SKILL.md`; `session-resume/SKILL.md` step 2a |
| CT-37 | 1. A citation the linter cannot verify is its own finding class with its own exit, never rc 0 | F3 Part 2 |
| CT-37 | 2. The pwf plugin root resolves from the installed plugin record, never a version-pinned cache path; a fixture bumps the version and the resolution still holds | KB-D17 |
| CT-20 | 1. (20a) One session selector grammar (`--current`, `--last N`, `--since <date>`, explicit ids) with a committed output schema, shared by CT-20b, CT-34, CT-51 and CT-37's context trigger | `session_select.py`, `schemas/session-select.schema.json` |
| CT-20 | 2. (20b) A bounded SessionEnd reflection (no network, timeout at most 60 s, always rc 0) writes leads: Bash commands whose argv matches a `mise.dev.toml` row (derived from `mise tasks --json`, not a hand table), directive violation rates, unarmed nulls, call runs that want a wrapper; kept under `evidence/` per session and read by CT-29 row 3 | `session_reflect.py:1-70`; `settings.json:165-179` |
| CT-20 | 3. (20b) Write attribution: an unexplained change to a tracked file is matched to the session and tool call that wrote it within a time window; masked digests only | `kb-session-review/SKILL.md` step 4a |
| CT-31 | 1. Each mod's TypeScript declarations come from the installed CLI (Claude Code writes them into the mod's `.claude-plugin/types/` when loaded with `--plugin-dir`, since 2.1.287), recorded with CLI version and sha256, refreshed by a named task, never vendored or hand-edited (UNVERIFIED on 2.1.299) | `mod_runtime.py:20-40`; `.claude/types/README.md` |
| CT-31 | 2. Two build gates per mod: `claude plugin validate <dir>` (syntax, event names) and `tsc --strict --noEmit` against those declarations with an explicit `export const register: Register` (without it tsc accepts an `any` module); `claude plugin test <dir>` for behaviour where available | `fnhook_gates.py:1-10`; `claude-code.d.ts:1-30` |
| CT-31 | 3. Loader constraints as lint rules, one fixture each: imports relative or `claude-code` only, no JSON import, no Node builtins, `$` never read as a value, hooks declared at module top level, `next.to(e, "<tier>")`; plus a `--debug-file` load arm, since each violation fails silently | `kb-settings-guard/hooks/register.ts:17-30, 140-147` |
| CT-31 | 4. No `tool.call` function hook names Bash; CT-36's WebFetch mod and any pane mod match only their named tools; one live arm runs `pwd` in a worktree subagent with the mods enabled | `register.ts:47-61` (KB-D28) |
| CT-31 | 5. Mods read the lane marker as `agentId` (function hooks) and settings hooks as `agent_id` (classic); a mod that branches on it has a live subagent arm | `register.ts:31-38` |
| CT-31 | 6. Whether `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` is still needed on the installed CLI is measured once and recorded; it is not set by default | `settings.json:4`; `.codex/config.toml:7` |
| CT-57 | 1. `.lsp.json` is validated against the plugin manifest schema's `lspServers` subschema (it cannot carry `$schema`), with every schema vendored at a pinned version so the check runs offline | `plugin_validate.py:8-12`; `MP:plugins/aggregated-research/spine-budgets.toml:18-22` |
| CT-14 | 1. The plugin skill names no KB task, rule or source path and no optional plugin as a step; its verb list is generated from `aggregated-research --help`; it fits the 200-line cap with incident history moved to references | KB-D10 |
| CT-07 | 1. Codex hooks use only variables Codex documents, and each Claude gate has a Codex counterpart or a recorded gap (KB runs a Codex PostToolUse `apply_patch` check against a Claude PreToolUse one) | KB-D25; `.codex/hooks.json:27-31` |
| CT-07 | 2. `roles:verify` checks every model id and alias in agent frontmatter, model-policy and `.codex/agents/*.toml` against a tracked model registry file; refreshing the registry is a separately admitted live call; nothing calls a model endpoint at SessionStart | KB-D29 |
| CT-07 | 3. Every role declares `tools` or `disallowedTools` explicitly; an untracked role file in either tree fails | KB-D19, KB-D20 |
| CT-19 | 1. Briefs gain a `PREMISES` slot of typed rows (literal, interface, precedent, emission, assumption), each with `file:line`; a read-only premise-verifier role (MP's own text, not the MIT port) checks them before dispatch for lanes touching hooks, security, concurrency or migrations; any refuted row blocks dispatch | `premise-verifier.md:39-107` |
| CT-59 | 1. A PreToolUse redirect denies raw `codex exec` and `codex review` and names the `dispatch:*` task | `codex_lane.py`; `hook_guard.py:436-456` |
| CT-59 | 2. Lanes over a size threshold (KB uses 20 files or 1,000 changed lines) route their review to the cross-family Codex reviewer; the receipt records the family that actually ran, and a same-family fallback says so | `kb-review/SKILL.md:129-150` |
| CT-59 | 3. A call expected to outlive the foreground cap runs in the background with an output file; a timeout is recorded as lost coverage, not a finished round | `kb-review/SKILL.md:194-226` |
| CT-25 | 1. Review rounds per lane are capped at two; a third needs a user decision; a receipt that records no lane run is refused | `kb-review/SKILL.md:10-24, 99-105, 231-245` |
| CT-18 | 1. A batch publish refuses a range when an integrated lane lacks a review receipt whose SHA equals the lane's merged tip | `kb-review/SKILL.md:49-51` |
| CT-22b | 1. `tools:audit` reports per pin: pinned, installed, latest stable, release notes read, tracked upstream issues re-checked, open questions; offline mode is silent when clean; the live mode is admitted; never at SessionStart | `tool-currency/SKILL.md`; `settings.json:138-153` |
| CT-55 | 1. The spike installs graphify through its own installer at a pinned version; KB's vendored skill, its `.agents` stub, `graphify-out/` and the graphify PreToolUse guards are not imported | KB-D15 |
| #31 | 1. Every public call emits one structured event line (adapter, outcome class ok, bad_request, not_run, external or error, duration, bounded repo and term) under the accepted telemetry directory with redaction | `events.py`; `trackers.py` at HEAD, `events.fail` calls |
| #44 | 1. A v2 tracker null carries a same-shape arm with a known-present term (for example a word from the newest item title), and a record whose hits are fewer than `total_count` says it is truncated | KB-D4, KB-D5 |
| #49 | 1. Parity asserts the pinned v1 tracker record (flat `has_issues` and `has_discussions`) and fails on KB HEAD's `Trackers` object as v1 output | KB-D8 |

Counts: 7 new tickets, 41 acceptance rows (38 on 16 CT tickets, 3 on spec #11 issues #31, #44, #49).

## 4. Not imported

- graphify skill, kb-curator, kb-extraction-worker, kb-synthesist, kb-tool-researcher, kb-corpus-curator,
  `kb-extract.js`, `kb-tool-review.js`, the graphify PreToolUse guards and the `kb`, `kb-memory` and hosted
  `graphify` MCP servers: the corpus is webclaw's (D57, CT-33, CT-41..CT-44) and graph querying is CT-55's
  spike; the hosted MCP uploads repository content, and both local servers auto-approve every tool.
- eli5-visual and its output style: a personal presentation preference, already available at user level
  (the eli5 plugin, artifact tooling); a project `outputStyle` overrides everyone (KB-D26).
- goal-engineering: native goals wait for explicit instruction (`MP:AGENTS.md`, Gotchas); revisit if the
  user admits `/goal`.
- kb-reclaim: host disk work; host setup stays in DF (D87) and D80 handled this round's disk items.
- skillopt-reviewed and the SkillOpt VCS dependency: an experimental optimizer needing a mutable plugin.
- artifact-download: no provider adapter exists; MP receipts come from CT-39's `marketplace_dev.receipts`
  and CT-33.
- orchestrator-routing, claude-advisor, kb-codex-advisor, kb-codex-astra-advisor, kb-codex-implementer and
  the advisor-before-dispatch directive: KB's model names (gpt-6.1-sol, gpt-6-astra, fable) and the
  antigravity lane; MP routing lives in ticket-frontier's model policy and CT-59; the useful mechanics are
  rows above.
- The kb-session-review Workflow script (1,307 lines) as code: detectors move to Python under CT-20b; Workflow
  scripts need the user's opt-in, and its fable-then-opus fallback is hard-coded (`session-review.js:1035-1038`).
- KB's function-hooks-first direction (chain entries #754-#773): superseded by D55, D61 and D87 (a mod only
  where only a mod can, with a settings-hook backstop).
- kb-settings-guard and model-registry as mods: a settings PreToolUse hook sees `agent_id`, so the lane guard
  is a gate (CT-02b row 6); model drift becomes an offline check (CT-07 row 2).
- The 23 rules as prose: their enforceable content is in the rows above, and importing them unscoped would
  repeat KB-D30. KB's session-resume "offer the next step, never take it" is not imported: MP's owner session
  continues at `## Next Step` by design.
- `.agent/` machine-local state (138 session plans, 463 gate records, reflections, recall reports): private,
  gitignored, no MP consumer; CT-34 reads transcripts, not these.
- Settings `teammateMode`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`,
  `additionalDirectories` to sibling repos (cross-repository reads need their own admission), and
  `worktree.baseRef: head` (MP cuts lanes with `lane:allocate`, not `Agent(isolation: "worktree")`; revisit in
  CT-17 only if it adopts isolation worktrees).
- `kb-skill-score` and plugin-eval scoring: advisory and tied to another plugin; MP keeps per-skill
  `evals/evals.json`.
- KB HEAD's tracker record shape and `plugin_validate.py`'s glyph parsing and live schema fetch (KB-D8,
  KB-D13).

## 5. Sunset checklist (knowledge-base)

Preconditions before anything is removed or archived:
- The KB GitHub repository is archived read-only, never deleted, while any pin lives: MP's plugin at
  `a872cb0` (until KB-A-1 or #48 and #49 land) and DF at `e8fe42ae` (DF's own reports own that move).
- KB's open plugin issues are closed with a pointer or carried into MP: #581-#583 and #587-#589 map to spec
  #11 (#28, #48, #49, #54, #61) and KB-A-2..KB-A-5; #584-#586 map to KB-A-6 and CT-59; #616 maps to CT-59
  row 1; the function-hook chain (#754-#773) closes as superseded by D87.
- KB settings drop `aggregated-research@ray-manaloto` (`settings.json:202`) when KB stops being used.

Deletable once the named MP owner lands:
- After CT-29 and CT-37 rows: `.claude/skills/clear-prep/`, `.claude/skills/session-resume/` and mirrors;
  handoff.py, handoff_reconcile.py, context_usage.py, session_state.py, next_ticket.py, gates.py,
  env_refresh.py and their tests and tasks.
- After CT-20: kb-session-reflect and kb-session-review (both trees), `.claude/workflows/session-review.js`,
  session_reflect.py, session_select.py, session_review_archive.py, `schemas/session-select.schema.json`, the
  SessionEnd hooks.
- After KB-A-7: kb-recall-work (both trees), recall_work.py, `schemas/recall-work.schema.json`.
- After CT-02b, CT-38 and CT-58 rows: the PreToolUse and SessionStart entries in `.claude/settings.json`,
  hook_guard.py, secret_guard.py, destructive_git.py, stage_explicitly.py, absent_binary.py,
  instruction_edit_guard.py, instruction_shell_write.py, skill_lint.py (md_budget.py stays while DF imports
  it).
- After CT-31 rows: `.claude/mods/kb-settings-guard/`, all three model-registry copies (including the
  untracked `.agents` one), `.claude/types/`, `tsconfig.json`, fnhook_gates.py, claude_types.py,
  mod_runtime.py, `tests/fixtures/fnhook`.
- After CT-07, CT-19, CT-25, CT-59 rows: `.claude/agents/*` and `.codex/agents/*` (all 11 plus the untracked
  one), `.codex/config.toml`, `.codex/hooks.json`, kb-review and its references, codex_lane.py.
- After KB-A-1 (or #48 and #49): `[project.scripts] aggregated-research` (`pyproject.toml:41`),
  `python/src/kb_setup/research/`, `schemas/research-record.schema.json` and the generated record,
  `tests/test_research_*.py`, `plugin_validate.py` and its test, `docs/roadmap/aggregated-research-chain.toml`,
  `.gitignore:12`, `.gitleaks.toml:60`.
- After KB-A-2..KB-A-6: the deps.dev protos and the six research reports in section 1.4 (as premise inputs
  they are copied into MP's offline corpus by the docs import, not by this ticket set).
- Not imported (section 4), deletable with the archive: graphify, kb-curator, eli5-visual and its output
  style, goal-engineering, kb-reclaim, skillopt-reviewed, artifact-download, orchestrator-routing,
  tool-currency (after CT-22b row 1), `.claude/rules/`, the remaining agents and workflows.
- Never moved: `.agent/` local state; deleted only on the user's word.
