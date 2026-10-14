# F4: Do `PWF_PLAN_ROOT` and `PWF_TRUSTED_PYTHON` pins in `.claude/settings.local.json` support git worktrees?

Read-mostly fact report from a general-purpose subagent of session `ccm-20261014` (`ce9c0b3d`),
2026-10-14, for the Phase 4a grill (CT-37 item 4, D54). CLI 2.1.299, pwf 3.24.0. No tracked MP
file edited, nothing written to GitHub, no `claude` session started, no pwf script or hook run by
this agent. Offline mirror: `S=/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/offline`
(docs in `S/cc-docs`, pwf clone in `S/pwf-upstream` at `ff349eb`, GitHub JSON in `S/gh`).
`P=~/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0`; every pwf file cited
below is byte-identical to the upstream clone (cmp).

## Verdict

Pinning `PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace` and
`PWF_TRUSTED_PYTHON=/usr/bin/python3` in the MAIN checkout's `.claude/settings.local.json` `env`
works with conditions. Parent session: works; settings `env` is written into the Claude Code
process environment and hooks run with that environment, and pwf honors the pin ahead of the cwd.
In-process subagent (plain or `isolation: worktree`): works; subagents share the parent process
environment and settings and plugin hooks fire for their tool calls, and because pwf resolves the
plan from the pin and never from git or the hook's cwd, the undocumented hook cwd of a
worktree-isolated subagent stops mattering (without the pin, a worktree cwd would resolve the
worktree's own branch copy of `.planning`, which differs from the live plan today). Separate
`claude` session started inside `.claude/worktrees/<unit>`: works with conditions; since v2.1.211
Claude Code reads the local file at the main checkout's root for every linked worktree (made by
`--worktree` or `git worktree add`), but only on macOS or Linux, inside a git repository whose root,
`.git` and `.claude` the user owns, with the main root trusted (or `-p` mode), and the file must
stay untracked; it is never copied into the worktree. Conditions common to all three: the pin
leaks into every subprocess, so tests that run pwf scripts elsewhere must scrub it; `PLAN_ID`
must stay pinned (tracked `.claude/settings.json` does it today); and nothing here was proven in a
fresh session, so the separate-session case and the isolated-subagent hook cwd stay UNVERIFIED
until the CT-37 probe below runs.

## MP state observed (read-only)

- `.claude/settings.json` `env` = `{"PLAN_ID": "2026-10-10-marketplace-macos-reflection-scaffold"}`;
  the worktree `.claude/worktrees/w0-doctor/.claude/settings.json` carries the same. Local file keys:
  `additionalDirectories, disableClaudeAiConnectors, enabledPlugins, extraKnownMarketplaces,
  permissions, prefersReducedMotion, skillOverrides, switchModelsOnFlag, teammateMode` (no `env`).
- `.claude/worktrees/w0-doctor/.claude/settings.local.json` is absent; no `.worktreeinclude` exists.
- `.claude/worktrees/w0-doctor/.planning/2026-10-10-marketplace-macos-reflection-scaffold/task_plan.md`
  exists and differs from the main checkout's copy (cmp): an unpinned hook running in that
  worktree reads a stale plan.
- `.planning/` holds one plan directory and no `.active_plan`; repository root, `.git` and `.claude`
  are owned by `rmanaloto`; SIP is enabled.
- This session's PATH puts `<MP>/.venv/bin` second; its `python3` resolves to
  `<MP>/.mise/installs/python/3.15.0/bin/python3.15`, an interpreter inside the repository.

## Q1. Which `.claude/settings.local.json` does a linked worktree load?

- The main checkout's. "If you start Claude Code in a subdirectory of a git repository, it reads and
  writes that file at the repository root ... In a worktree, it uses the file at the main checkout's
  root." https://code.claude.com/docs/en/settings#where-claude-code-keeps-the-local-file-in-a-git-repository
  (mirror `S/cc-docs/settings.md:99-101`).
- Exceptions where the file stays beside `.claude/settings.json` (the worktree): outside a git
  repository, repository root equal to home, Windows, or root, `.git` or `.claude` not owned by the
  user (`settings.md:105`). None applies to MP.
- Both files when both exist: "Before v2.1.211, Claude Code kept the file in the starting directory.
  It still reads a file an earlier version left there alongside the root file; where both set the
  same key, the root's value applies, and permission rules from both files apply" (`settings.md:107`).
  anthropics/claude-code#98640 (open, 2.1.286, macOS) observes the merge in a debug log.
- Since: v2.1.211 (npm publish 2026-07-15). CHANGELOG 2.1.211: "Changed 'always allow' permission
  rules to save at the repository root, so approvals granted in a git worktree persist across sessions
  and worktrees" (`S/cc-docs/CHANGELOG-full.md:4010`). worktrees.md repeats the cut-over
  (https://code.claude.com/docs/en/worktrees#what-worktrees-share-with-the-main-checkout,
  mirror `worktrees.md:236`). Installed 2.1.299 is past it.
- Scope: "All of these apply whether you create the worktree with `--worktree` or with
  `git worktree add`" (`worktrees.md:241`), so MP's hand-made lane worktrees are covered.
- Copy or share: shared by reference, never copied. A worktree is a fresh checkout without untracked
  files; `.worktreeinclude` copies only gitignored files matching a pattern, for `--worktree`,
  subagent and desktop worktrees (`worktrees.md:187-203`). Do not list the local file there: a copy
  becomes a stale starting-directory file (root still wins per key, permission rules union).
- Shared `.claude/settings.json` is read from the session's primary working directory
  (`settings.md:110`), so a worktree session uses its branch's copy (today it carries `PLAN_ID`).
- Trust: in a worktree Claude Code keys workspace trust on the main checkout's root
  (https://code.claude.com/docs/en/permissions, mirror `S/cc-docs/permissions-html.md:788`).
  Local-settings `env` applies "after you trust the workspace, or at startup in `-p` mode"
  (https://code.claude.com/docs/en/settings-reference#when-claude-code-applies-env-values, mirror
  `S/cc-docs/settings-reference-html.md:2840-2848`). An untracked local file skips trust for allow
  rules only (`permissions-html.md:797-801`).
- Agent `isolation: worktree`: no separate settings load; the subagent "takes the instruction files
  it starts with from your main conversation, not from its worktree" (`worktrees.md:122`).
- Desktop app worktree sessions differ: project configuration and hooks come from the main root,
  and `${CLAUDE_PROJECT_DIR}` points there (`worktrees.md:243`). Not MP's CLI case.
- `/cd` on v2.1.246+ re-reads both project files from the new directory, placing the local file by
  the same rules (`settings.md:110`).

## Q2. Do in-process subagents inherit the settings `env`, and do pwf hooks see it?

- Settings `env`: "Claude Code writes each `env` entry into the process environment"
  (https://code.claude.com/docs/en/env-vars, mirror `env-vars.md:100`); values "reach every
  subprocess Claude Code starts" (`settings-reference-html.md:2830-2838`). A saved change applies to
  the running session; removing a key does not unset it (`env-vars.md:72`).
- Hooks: "Handlers run in the current directory with Claude Code's environment"
  (https://code.claude.com/docs/en/hooks, mirror `hooks.md:402`). "Hooks from settings files, managed
  policy settings, and plugins also run inside subagents ... the input carries the `agent_id` and
  `agent_type`" (`hooks.md:257`; https://code.claude.com/docs/en/sub-agents#define-hooks-for-subagents,
  mirror `sub-agents.md:727-729`).
- Cwd: a subagent starts in the main conversation's cwd; with `isolation: worktree` its Bash runs in
  its worktree (`sub-agents.md:264-266`). After a session enters a worktree, `${CLAUDE_PROJECT_DIR}`
  stays put and the hook input `cwd` follows Claude (hooks.md, "Worktrees are different", mirror
  `hooks.md:451`, a single-line blob). The hook PROCESS cwd for a worktree-isolated subagent's tool
  call is not documented: UNVERIFIED.
- Empirical, this run: this in-process subagent's Bash env holds `PLAN_ID` from the tracked
  `.claude/settings.json`, and pwf's PreToolUse hook fired on its first Bash call and injected a
  `kind=plan` frame (`bytes=2096 sha256=a45bde02...`).
- Answer: yes, a pin in the parent's settings `env` reaches pwf hooks fired for any in-process
  subagent. Agent-team teammates in their own process, `claude agents` background sessions and
  `--worktree --tmux` are separate sessions and fall under the third case.
- Carrier note for CT-37 (4): `CLAUDE_ENV_FILE` from a SessionStart hook persists variables "into
  subsequent Bash commands" only (`env-vars.md:429`; hooks.md "Persist environment variables"), so
  it cannot reach pwf hooks. Settings `env` and the launch environment (`./dev/mise exec -- claude`)
  can.

## Q3. How pwf 3.24.0 resolves the plan root and Python in a linked worktree

- Dispatch: every Claude event runs `sh ${CLAUDE_PLUGIN_ROOT}/hooks/claude-hook.sh <event>`
  (`P/hooks/hooks.json:4-99`; PreToolUse matcher `Write|Edit|Bash|Read|Glob|Grep` at :38).
- Zero-probe exit unless `PLAN_ID` or `PWF_PLAN_ROOT` is set or the cwd has `task_plan.md` or
  `.planning` (`P/hooks/claude-hook.sh:116-119`).
- Pin: accepted only when absolute and an existing directory; then the plan root is
  `${PWF_PLAN_ROOT}/.planning`, overriding both `$PWD` and any positional argument; a bad pin fails
  closed (`P/scripts/resolve-plan-dir.sh:25,39-52`; `P/scripts/inject-plan.sh:101-115`, notice
  "PWF_PLAN_ROOT is not a supported absolute local directory"; `P/scripts/inject-plan.py:940-950,1483-1490`).
- Selection under that root: a set `PLAN_ID` is a binding (`resolve-plan-dir.sh:254-264,363-366`;
  `inject-plan.sh:285-300`; `inject-plan.py:966-981,1498-1504`); unset, more than one slug plan is
  ambiguous and injects nothing (`resolve-plan-dir.sh:342-361`; `inject-plan.sh:259-279`), else
  `.active_plan` (`resolve-plan-dir.sh:266-283`), else newest mtime (`:285-313`). Linked (symlinked)
  plan dirs are never selectable (`:249-258`, issue #271), so symlinking a worktree's `.planning` to
  the main one is not an alternative.
- An explicit selector forbids the legacy root `task_plan.md` fallback (`claude-hook.sh:212-219`;
  `inject-plan.py:1590-1591`). Containment is checked against the pin root
  (`resolve-plan-dir.sh:184-228`).
- The nested-project ambiguity check runs only for cwd guesses and scans direct non-dot children
  (`inject-plan.py:1066-1103`; `inject-plan.sh:537`); `.claude/worktrees/<unit>/.planning` never
  trips it.
- No git: the dispatcher, resolver and injector never call git, `rev-parse` or worktree logic (the
  only matches are message text at `inject-plan.sh:1327`, `inject-plan.py:1262,1310`). Unpinned, a
  hook whose cwd is a linked worktree resolves that worktree's own `./.planning`.
- Python: the dispatcher takes `PWF_TRUSTED_PYTHON`, then `PYTHON_BIN`, if absolute, regular and
  executable, else walks PATH for `python3` then `python` (`claude-hook.sh:49-95`) and runs
  `-I -B inject-plan.py` (`:136-138`). The resolver uses only the trusted path, never PATH, and only
  when `realpath` and `readlink -f` are missing (`resolve-plan-dir.sh:115-165,233-247`). The injector
  allows only the explicit interpreter before containment and PATH after it, version 3.8 or newer
  (`inject-plan.sh:54,62-75,331-352`); the twin needs 3.6+ (`inject-plan.py:43`). Unpinned, this
  session's hooks run MP's in-repo `.venv` interpreter, and a lane session may find another or none.
- Catch-up uses `command -v python || python3` (`claude-hook.sh:301-303`) but returns at once in
  no-history mode (`P/scripts/session-catchup.py:716-717`). Turn-marker keys use the absolute plan
  path plus session id (`claude-hook.sh:239-261`), so pinned hooks share one slot per session.
- pwf's own model is the opposite of MP's: "pin each host ... or use separate worktrees", one plan
  scope per worktree (`P/README.md:391`; `P/docs/workflow.md:237-241`); `PWF_PLAN_ROOT` exists for a
  cwd that differs from the project root (`P/README.md:703`).

| Case | Hook cwd | Unpinned plan | Pinned plan |
|---|---|---|---|
| Parent session | main root | main | main |
| Subagent, no isolation | main root | main | main |
| Subagent, `isolation: worktree` | UNVERIFIED | worktree copy if cwd is the worktree; a fresh default-branch base may lack the plan, and `PLAN_ID` then fails closed | main |
| Separate session in `.claude/worktrees/<unit>` | worktree | worktree branch copy (stale today) | main, provided Q1 holds |

## Q4. Real-world examples

- No GitHub issue, PR or discussion anywhere combines planning-with-files with git worktrees
  (global issue search and discussion search: 0 relevant hits). MP's pattern is undocumented upstream.
- OthmanAdi/planning-with-files#212 (closed 2026-08-01): a shared-parent cwd injected another
  thread's plan; origin of `PWF_PLAN_ROOT` (v3.9.0).
  https://github.com/OthmanAdi/planning-with-files/issues/212
- #261 (closed 2026-09-18, fix PR #265, v3.20.1): an inherited `PWF_PLAN_ROOT` redirected init
  attestation in a different project. A session-wide pin reaches every pwf script the session runs.
  https://github.com/OthmanAdi/planning-with-files/issues/261
- #237: `PLAN_ID` became a binding. #50 (closed 2026-10-10), maintainer: "Pin each host before
  starting it, or use separate worktrees when the host cannot provide a separate environment per
  task." Discussion #81: `PLAN_ID` pinning for isolated sessions; no discussion mentions worktrees
  or `PWF_PLAN_ROOT`.
- anthropics/claude-code#98640 (open, 2.1.286, macOS): a linked-worktree session loads both the
  worktree's and the main checkout's local file; the warning names the main file.
- #84027 (closed not planned 2026-10-06; Windows 11, 2.1.212 to 2.1.222): the harness writes
  `settings.local.json` inside each isolated worktree, matching the documented Windows exception.
- #97836 (open, 2.1.283, WSL): `claude --worktree` enforces the launch checkout's `settings.json`
  permission rules though `$CLAUDE_PROJECT_DIR` and cwd name the worktree. Shared-file sourcing for
  `--worktree` is buggy; local `env` is not involved.
- #78874 (closed not planned): an `env` key in settings applies to every worktree of a repository;
  undesired for a task-list ID, desired for `PWF_PLAN_ROOT`.
- #97760 (open, 2.1.220, desktop): the worktree-isolation Bash guard refused a command referencing a
  settings `env` variable. Isolated lanes should read the plan with Read, not `"$PWF_PLAN_ROOT"/...`
  shell commands.
- #90104 (open): `EnterWorktree` mid-session broke Stop hooks under the sandbox (EPERM); pwf's Stop
  gate would be affected the same way.
- #44586 (closed duplicate, 2026-04-07, pre-2.1.211): `env.PATH` not applied in worktree agent Bash.
  #26479 (open, 2026-02): agent-team teammates did not inherit the local file. Both predate the
  current behavior; open-gsd/gsd-core discussion #3630 (2026-08-18) reports local-file hooks missing
  in fresh worktrees, platform unstated.

## Saved searches

- `dev/saved-searches.toml` holds three code searches, all on `openai/codex`: `codex-schema`
  (`schema`), `codex-config-examples` (`model filename:config.toml`), `codex-hook-examples`
  (`SessionStart filename:hooks.json`), each with control `README` (min 1). None touches pwf,
  worktrees or settings, so they hold no example for this question.
- The mise tasks cannot write outside the tree: `--output` passes through `confined()`, which
  refuses any path outside the project (`dev/search_catalog.py:44-47`, `dev/collect_saved_search.py:251-252`),
  and the tasks expose no output argument. The queries were reproduced with read-only `gh api
  search/code` into `S/saved-searches`: `codex-schema` total 884 (10 items over 2 pages),
  `codex-config-examples` 1 (`.github/codex/home/config.toml`), `codex-hook-examples` 0, control
  `README` 164. The retained runs imported from Codex worktree 2a14 (2026-10-12) agree:
  config-examples complete with the same path, hook-examples `empty_verified`, schema 898 `partial`.
- Proposed entries (not applied; the catalog supports only `GET /search/code`, `dev/search_catalog.py:76-79,104-105`):

```toml
[[search]]
id = "pwf-plan-root-pin"           # 291 hits on 2026-10-14
query = "PWF_PLAN_ROOT"
repo = "OthmanAdi/planning-with-files"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"                   # 21 hits
expected_min = 1

[[search]]
id = "pwf-trusted-python"          # 84 hits
query = "PWF_TRUSTED_PYTHON"
repo = "OthmanAdi/planning-with-files"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "pwf-worktree-docs"           # 21 hits
query = "worktree extension:md"
repo = "OthmanAdi/planning-with-files"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

  Claude Code's own evidence lives in issues and its CHANGELOG, which code search does not index
  (`settings.local.json filename:CHANGELOG.md repo:anthropics/claude-code` returns 0). Tracking it
  needs an issue-search kind (`GET /search/issues`, queries `"settings.local.json" worktree` and
  `worktree env` on `anthropics/claude-code`), a catalog change for a ticket, not a row.

## Routes

| Route | Command | rc | Result |
|---|---|---|---|
| pwf cache read | `cat`, `grep`, `awk` over `P` | 0 | resolver, injector and dispatcher read; cited above |
| Upstream clone | `git clone --depth 1 https://github.com/OthmanAdi/planning-with-files.git S/pwf-upstream` | 0 | `ff349eb` (2026-10-12), version 3.24.0; cited files identical to cache |
| webclaw docs | `webclaw https://code.claude.com/docs/en/<page>.md -f markdown` for llms.txt, settings, settings-reference, worktrees, sub-agents, hooks, hooks-guide, env-vars, claude-directory, debug-your-config, changelog, common-workflows, agent-teams, agents, cli-reference, plugins/loading, permissions, memory, security, permission-modes; plus HTML settings-reference and permissions | 0 (22 fetches) | mirrored in `S/cc-docs`; `settings-reference.md` and `permissions.md` came back as page scaffolding, so the HTML pages were used |
| webclaw pwf | README raw, repo page | 0, 0 | `S/pwf-docs` |
| webclaw CHANGELOG | `webclaw https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md` | 0 | truncated at 107 KB (stops at 2.1.289) |
| gh CHANGELOG | `gh api -H 'Accept: application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` | 0 | 1,015,061 bytes; 2.1.211 entry found |
| npm dates | `npm view @anthropic-ai/claude-code time --json` | 0 | 2.1.211 published 2026-07-15 |
| gh search pwf | `gh search issues worktree / PWF_PLAN_ROOT / PWF_TRUSTED_PYTHON / subagent / 'settings.json env' --repo OthmanAdi/planning-with-files --include-prs`; `gh search prs worktree / PWF_PLAN_ROOT` | 0 each | 13, 19, 0, 7, 0; PRs 8, 6 |
| gh search claude-code | 13 `gh search issues` queries on `anthropics/claude-code` (settings.local.json worktree, worktree settings in:title, worktree env in:title, and others) | 0 each | 0 to 50 hits; relevant ones listed in Q4 |
| gh search global | `gh search issues 'planning-with-files worktree'`; `gh search issues PWF_PLAN_ROOT` | 0, 0 | 0; 15 (pwf plus herdmates#129, hermes-agent#86411) |
| gh issue view | 10 claude-code and 5 pwf issues, plus `--comments` on pwf#50 | 0 each | bodies in `S/gh/bodies` |
| GraphQL discussions | `gh api graphql` search type DISCUSSION (6 queries) and 4 discussion reads | 0 each | pwf worktree 0, PWF_PLAN_ROOT 0, repo total 14; claude-code worktree settings 0 |
| Saved searches (task) | `./dev/mise run research:collect live --all` | not run | output confined to the tracked tree |
| Saved searches (reproduced) | `gh api -X GET search/code -f q='<query> repo:openai/codex' -F per_page=5 -F page=1,2` and control | 0 each | see Saved searches |
| Proposed queries | 6 `gh api search/code` checks | 0 each | counts above |
| Exa | `fnox ... exec -- sh -c 'curl ... https://api.exa.ai/search'` (2 queries) | 0, HTTP 200 | docs pages, pwf README and docs, anthropics/claude-code#28041; nothing new |
| Firecrawl | `fnox ... exec -- firecrawl search ... --json` (2 queries) | 1, 1 | HTTP 402 (quota); gap |
| Context7 | `fnox ... exec -- ctx7 library` (2), `ctx7 docs /othmanadi/planning-with-files`, `ctx7 docs /websites/code_claude` (2) | 0 each | corroborates settings.md and worktrees.md text; no new fact |
| Last30Days | `fnox ... exec -- python3 last30days.py --diagnose`; run with `--plan`, `--save-dir=""` | 0, 0, 0 | first run: all sources SSL `CERTIFICATE_VERIFY_FAILED`; rerun with `SSL_CERT_FILE=/etc/ssl/cert.pem`: Web HTTP 422, Reddit and X returned generic worktree threads, nothing on local settings or pwf; gap |
| Worktree probe | read-only `ls`, `cmp`, `git rev-parse` on `.claude/worktrees/w0-doctor` | 0 | plan copy differs; no local file. No throwaway repo: with no git logic in pwf, a repo probe needs pwf execution, which this brief forbids |

## Recommended pin values

Merge into the existing main-checkout `.claude/settings.local.json` (keep its other keys):

```json
{
  "env": {
    "PWF_PLAN_ROOT": "/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace",
    "PWF_TRUSTED_PYTHON": "/usr/bin/python3"
  }
}
```

- `PWF_PLAN_ROOT`: absolute, no trailing slash, the main root (not `.planning`, not a worktree).
  Keep it out of the tracked `.claude/settings.json` (machine-specific path) and out of
  `.worktreeinclude`.
- `PWF_TRUSTED_PYTHON`: `/usr/bin/python3` is root-owned under SIP, 3.9.6 (passes the 3.8 floor),
  about 0.03 s to start. `/usr/local/bin/python3` (3.13) sits in an admin-writable framework
  directory, and mise or `.venv` interpreters are version-pinned or inside the repository.
- `PLAN_ID`: already in tracked `.claude/settings.json`. Adding it to the local file too is optional
  insurance for a separate session in a worktree whose branch predates that key; local wins.
- Lane briefs keep "the parent owns planning files": pinned, the PostToolUse nudge ("Update
  progress.md", `claude-hook.sh:287`) points non-isolated subagents at the live plan; isolated
  subagents cannot edit main-checkout paths (`worktrees.md:90`).

## CT-37 tests to add

1. Static, offline (add to `dev/test_handoff.py` or the doctor): the main root local file is
   untracked (`git ls-files --error-unmatch` fails); `env.PWF_PLAN_ROOT` equals the parent of
   `git rev-parse --path-format=absolute --git-common-dir`, is absolute, has no trailing slash and
   holds `.planning/$PLAN_ID/task_plan.md`; `env.PWF_TRUSTED_PYTHON` is absolute, a regular
   executable outside the repository and every worktree, and `-I -c 'import sys; raise
   SystemExit(sys.version_info < (3, 8))'` exits 0; no `.claude/worktrees/*/.claude/settings.local.json`
   sets a different `PWF_*` value; no `.worktreeinclude` pattern matches the local file.
2. Carrier probe (admitted operation; a throwaway repo with a linked worktree, not MP): main root
   local file `env.PROBE_LOCAL`, launch env `PROBE_SHELL`, a SessionStart hook writing
   `PROBE_ENVFILE` to `CLAUDE_ENV_FILE`, and a PreToolUse command hook appending event, `agent_id`,
   `$PWD`, input `cwd` and the three probes to a log. Run `claude -p` from the worktree; the prompt runs
   one Bash and spawns one `isolation: worktree` Agent that runs one Bash. Expected from the docs:
   `PROBE_LOCAL` and `PROBE_SHELL` present in every hook line, `PROBE_ENVFILE` only in Bash. The log
   settles the isolated subagent's hook `$PWD`.
3. pwf binding (admitted; a session started in `.claude/worktrees/<unit>` after the pin lands): the
   PreToolUse `kind=plan` frame carries the main checkout's plan head (owner line), not the worktree
   copy's, which differ today for w0-doctor.
4. Scrub regression: tests that run pwf or MP gates in temporary repositories keep scrubbing
   `PLAN_ID` and `PWF_PLAN_ROOT` (`dev/test_hooks.py:21`, `dev/test_retro_gate.py:16`,
   `dev/test_ticket_frontier.py:27`); pwf#261 is the failure mode.
