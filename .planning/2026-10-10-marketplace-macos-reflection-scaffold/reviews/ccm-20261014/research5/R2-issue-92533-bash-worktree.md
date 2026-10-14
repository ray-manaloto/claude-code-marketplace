# R2: anthropics/claude-code#92533 and gating Bash for worktree-isolated subagents (2026-10-14)

Written by research agent R2 of session `ccm-20261014` (`ce9c0b3d`) for the user's Q70, under the shared
brief `scratchpad/reprio2/research-brief.md`. Read-only toward MP (this file is the only write). MP at
`21af565`; host CLI `claude --version` = 2.1.299. P = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.
Scratch (raw outputs, fetched docs, code copies): `scratchpad/research5/R2/` under the session scratchpad
(`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/`).
No `claude` session was started, so nothing below is a fresh live measurement on this host.

## Verdict

Recommendation: a third option, not either framed fork. Keep the Bash gate a mod, but hook
`tool.check` with `{ tool: 'Bash' }` instead of `tool.call`; keep a cheap `agent.spawn` deny of
`isolation: "worktree"` as a standing MP policy (for reasons that outlive #92533); add no settings-hook
exception on #92533 grounds. Pair it with a CLI floor of 2.1.290 checked by the doctor, a library lint
that bans unmatched and RegExp `tool.call` matchers, and the Git-level gate as the cwd-exact backstop.
Turn A2-0 arm 4 into a regression check on this host before A2-9 lands; the settings-hook exception
(cstarlea's route) becomes the fallback only if that arm fails.

Confidence: high that the #92533 defect is fixed from 2.1.288 on Linux; medium that it holds on macOS
2.1.299 (nobody has measured it); medium-high that `tool.check` is the right event (vendor docs plus three
independent third-party measurements, but `tool.check` under `bypassPermissions` is unmeasured).

Evidence that decides it:
1. The fix landed. CHANGELOG 2.1.288: "Fixed a plugin's `tool.call` hook making Bash fail and file
   searches read the wrong folder in subagents that run in a worktree" (`anthropics/claude-code`
   `CHANGELOG.md`, line 835 of the 2026-10-14 fetch). 2.1.288 was published 2026-10-02T18:30:40Z (npm
   `time`). poteat, the author of the official Mods thread and a committer of the vendor's `mods/diff`
   (for example `765f236fe`, #99206), answered the same bug on 2026-10-02T21:28:23Z: "This was a big
   blunder on our part ... This should be fixed as of today's release on v288"
   (https://github.com/anthropics/claude-code/issues/91870#issuecomment-5961758416). An independent
   three-arm probe on 2.1.288 (Linux, WSL2) did not reproduce it while the debug log showed the hook
   running on each subagent Bash call (melodic-software/claude-code-plugins
   `docs/upstream/claude-code-mods/experiments.md`, section E8, at `8718950e9da6`).
2. `tool.check` on Bash kept isolation even before the fix: a seven-arm table at 2.1.272 and 2.1.286 lists
   "`tool.check` with `{tool:"Bash"}` | works" (https://changelogs.core-directive.com/reference/mods/gotchas,
   gotcha 3), and bengous/claude-code-plugins#190 (2026-09-23) kept an unmatched `tool.check` while matching
   `tool.call`, and "the probe keeps isolation whole". The vendor documents `tool.check` for exactly this
   shape: a Bash hook that denies `git push` depending on the current branch
   (`code.claude.com/docs/en/plugins/mods/events.md:182-200`), and a deny returned after `next` "still holds"
   (`:344-346`). `e.agentId` is on `tool.check` from 2.1.290 (`plugins/mods/reference.md:61-68`; CHANGELOG
   2.1.290 line 591).
3. The npm `stable` dist-tag is still 2.1.287, a pre-fix build (`npm view @anthropic-ai/claude-code
   dist-tags`: stable 2.1.287, latest 2.1.299). A `tool.call` Bash gate breaks isolated subagents on any
   host or CI runner pinned to stable; a `tool.check` gate does not (point 2).
4. Neither mod event carries the call's working directory, and that, not #92533, is the remaining reason a
   settings hook is more exact. MP's gate resolves the repository from the hook input's `cwd`
   (`dev/hooks/pretooluse_gate.py:74-77`); a settings hook's `cwd` "follows Claude", worktree and `cd`
   included (`hooks.md`, line 451 of the webclaw fetch). `ToolCheckInput` has `tool`, `input`,
   `tool_use_id`, `agentId`, `ceiling` and no `cwd` (2.1.296 declarations, T:12820-12857), the request to
   add it is open (#101384, 2026-10-11), and `$.session.cwd()` returned the parent session's directory
   inside a worktree subagent's tool calls on 2.1.287 (cstarlea on #92533, 2026-10-02). In MP this gap is
   bounded because lanes do not use `isolation` (`.claude/agents/*.md` set none; lanes are
   `.claude/worktrees/<unit>` per `docs/agents/claude-team.md:34`) and the global hk `pre-push` hook is live
   (finding 7).
5. Denying `isolation: "worktree"` is cheap and right independently of #92533: the built-in isolation guard
   blocks git into the main checkout by design (`worktrees.md:82-93`), which is where MP integrates, and its
   command-shape check still refuses git-free commands in open issues #95122 (updated 2026-10-13), #97225
   and #87959. A published mod already does this deny: mike-bronner/workbench-core `hooks/register.ts:1052`
   at `3d5535b5a437` (2026-10-13).

## Findings

### 1. Exact trigger

- Trigger: a hooks-module (mod) `tool.call` hook loaded in the plugin hooks worker, whose matcher can reach
  the subagent's Bash call: `{ tool: 'Bash' }`, no matcher, `on('*')`, or any RegExp matcher, even one that
  can never match Bash. A plain string or string array naming other tools is safe.
  - Issue body: one passthrough `on("tool.call", { tool: "Bash" }, ...)` in a fresh repo is enough; a
    `session.start`-only plugin is the control (#92533, 2026-09-06, navidemad, 2.1.263).
  - RegExp and unmatched: synath's table on 2.1.285 and 2.1.286 (#92533 comment 2026-10-04): `tool.call`
    with `/^mcp__x__/` passthrough is refused; `tool.check` with a RegExp is OK; string and string-array
    `tool.call` matchers are OK. bengous#190: a RegExp inside a matcher list "still ran for every call (5
    dispatches in the probe) and isolation was lost again".
  - Wildcards: `on("*")` and bare `on("tool.call")` refused, `classic.*` and `classic.PreToolUse{tool=Bash}`
    worked (ray-manaloto/dotfiles `docs/research/kb/reports/agents/2026-09-11-function-hooks-worktree-bash-probe.md:37-44`,
    2.1.269).
- Not triggers: settings `PreToolUse` command hooks (cstarlea: "A settings hook doesn't break isolation,
  and it sees each subagent's own `cwd`"); `classic.*` events, `session.start`, `turn.complete`,
  `agent.spawn`, tool registration served by own-name `tool.call` (rapuckett on #92533, 2026-10-03, 2.1.287);
  `tool.check` (core-directive gotcha 3; bengous#190); `on("!tool.call")` (core-directive gotcha 3); built-in
  mods, which load native rather than in the worker (synath's debug excerpt; Und3rf10w below). The vendor's
  own built-in `diff` mod registers `tool.call` on `[...EDITING_TOOLS, ...SHELL_TOOLS]`, Bash included
  (`mods/diff/hooks/register.ts:997-999` at `9b4f0d6ef`).
- Mechanism (reporter's analysis, not vendor-confirmed): the isolated agent's cwd lives in an
  AsyncLocalStorage store; a worker-hosted hook's `next()` resumes on the main thread outside that store, so
  the tool's own execution runs without it. Bash refuses; Read, Glob and Grep resolve relative paths against
  the parent checkout; `EnterWorktree` takes the main-session path and moves the parent session
  (Und3rf10w, https://github.com/anthropics/claude-code/issues/91870#issuecomment-5949411806, 2.1.287; the
  `EnterWorktree` side effect is also in the #92533 body).

### 2. Affected versions, and 2.1.299

- Reported or measured broken: 2.1.263 (issue body), 2.1.269 (dotfiles probe above), 2.1.272 (zachthedev,
  Windows, #92533 2026-09-15; core-directive, Linux), 2.1.278 (melodic-software#4241, Windows), 2.1.285 and
  2.1.286 (synath; core-directive), 2.1.287 (cstarlea, rapuckett, Und3rf10w).
- From 2.1.287 mods load by default, so any installed mod with such a hook affects every session on the
  machine (rapuckett; CHANGELOG 2.1.287 line 905 "Added Claude Mods").
- Fixed in 2.1.288 (CHANGELOG line 835; poteat comment; melodic E8 non-repro on Linux). Every #92533
  comment is on a pre-fix build; the last is 2026-10-04 on 2.1.285 and 2.1.286.
- 2.1.299: no report either way. Issue searches for the refusal text return only #92533, #91870, dotfiles#1020
  and bengous#190 (routes table). The changelog from 2.1.289 to 2.1.299 has no regression note for it.
  UNVERIFIED on macOS and on 2.1.299: no live arm ran here (brief forbids `claude` starts). The file-search
  half of the fix is unverified everywhere (melodic E8: the Linux build had no Glob tool).

### 3. Anthropic responses

- On #92533: none. All four commenters have association NONE, no assignee, labels added by
  `github-actions[bot]`; the issue is still OPEN, last updated 2026-10-04 (`gh issue view 92533 --json`;
  timeline).
- On #91870 (the official Mods thread): poteat's 2026-10-02 comment above. poteat's org membership is not
  public (`orgs/anthropics/members/poteat` returns 404), so "staff" rests on authorship of the vendor
  announcement ("I was asked to get feedback regarding an internal proposal we have") and commits to
  `anthropics/claude-code` `mods/diff`.

### 4. Workarounds others report

| Who, where | Workaround | Status today |
|---|---|---|
| navidemad, #92533 body | Make worktrees with `git worktree add`, spawn agents without `isolation`, prefix `cd <worktree> &&` | MP's lane model already |
| cstarlea, #92533 2026-10-02 | Guard logic in a settings `PreToolUse` command hook (`node .../pretooluse.ts` importing the plugin's checks); the mod keeps only slash commands | Works, but contradicts D92 |
| rapuckett, #92533 2026-10-03 | Never let a `tool.call` matcher reach Bash; observe Bash through `classic.PostToolUse` and `classic.PostToolUseFailure` | Observation only; `classic.*` delivery is now in doubt (finding 6) |
| synath, #92533 2026-10-04 | Exact tool-name strings in every `tool.call` and `tool.check` matcher | Cheap, keep as lint |
| Und3rf10w, #91870 2026-10-02 | Literal matchers that leave out cwd-sensitive tools; or answer without `next()`; `CLAUDE_CODE_HOOKS_SAME_THREAD=1` (internal, unsupported) | The env var is unsupported |
| core-directive gotcha 3 | `tool.check` on Bash; `on("!tool.call")` for broad observers | Recommended here |
| ray-manaloto/dotfiles#1041 (open) | Build-time ban of `tool.call` naming Bash or unmatched | Should also ban RegExp (synath) |
| `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=0` (issue body) | Turn mods off | 2.1.287 and later ignore the flag (melodic-software#5768) |

### 5. Fix status

Landed in 2.1.288 per changelog and the vendor author; the issue was never closed or linked to a release, so
"#92533 open" in A2 (section 1.3 G7, decision 3) describes the tracker, not the binary. No upstream PR exists
for it (the CLI source is not in the repository; `gh search issues 92533 --repo anthropics/claude-code
--include-prs` returns #92533 and #91870 only).

### 6. What the fix does not settle

- Working directory in mods (finding 4 of the verdict). Related open items: #101384 (cwd on `tool.call` and
  `tool.check`), #100916 (`agent.spawn` cwd for workflow agents). CHANGELOG 2.1.296 line 221 fixed "a
  plugin's served `$` methods running in the main session's working directory instead of the calling
  agent's"; whether that changed `$.session.cwd()` or `$.process.run`'s default cwd ("the session's", T:3515)
  inside a subagent is UNVERIFIED (A2-0 arm 6).
- `classic.PreToolUse` as a gate: safe for isolation on 2.1.269 (dotfiles arm F) and its deny enforced on
  2.1.286 to 2.1.288 (ray-manaloto/dotfiles `docs/research/kb/reports/agents/install-doctor-p5-probe-2026-10-03.md:9-12, 40-58`),
  but #100869 (2026-10-09, 2.1.295) reports no `classic.*` event reaching a module in `-p` or interactive
  runs, #96831 reports none in `--bg` sessions (comment 2026-10-08, 2.1.294), and `sec-default` skips user
  `classic.*` hooks on managed or Team machines (aik099, #91870 comment 2026-10-09; A2 G4). Not a gate
  event to build on today.
- The built-in isolation guard itself: open refusals of git-free commands (#95122, #97225, #87959), the
  session-wide latch after `EnterWorktree` (#89102, #91932, #98307), and 2.1.299 still tightening it
  (CHANGELOG line 113, awk programs).

### 7. Alternatives compared

| Route | #92533 exposure | Knows the call's cwd | Loads in untrusted `-p` (A2 G1) | Other costs |
|---|---|---|---|---|
| `tool.call {Bash}` mod (A2-9 as designed) | Broken on 2.1.263 to 2.1.287, including npm `stable` | No; `$.session.cwd()` wrong in isolated subagents (2.1.287) | No | A deny without `next` also skips settings PreToolUse hooks (`events.md:310`) |
| `tool.check {Bash}` mod (recommended) | Safe pre-fix (gotcha 3; bengous#190) | No | No | Bypass-mode firing UNVERIFIED; another mod's later `tool.check` can override; needs 2.1.290 for `agentId` |
| `classic.PreToolUse` mod | Safe (dotfiles arm F) | Input carries `cwd` per the settings payload, UNVERIFIED for modules | No | Delivery doubts (#100869, #96831) and `sec-default` skip |
| Settings `PreToolUse` command hook (status quo, `.claude/settings.json:41-53`) | Never affected | Yes, follows `cd` and worktrees (`hooks.md` line 451) | Yes (P5 arm S1) | Contradicts D92; a mod's `tool.check` can approve past it (`permissions.md:598-603`); process spawn per call, reducible with `if` (`hooks.md:413-436`, best effort) |
| Permission rules (`Bash(git push *)`) | n/a | n/a | Yes | Cannot express "lane retro passes"; deny rules can be loosened by a mod outside managed settings (`permissions.md:603`) |
| Sandbox | n/a | n/a | n/a | Governs filesystem and network, not merge or push policy; does not apply to the question |
| Git hooks via hk (`hk.pkl:8-20`) | Never affected | Exact (git runs in the worktree) | Yes | Covers push today (global `hook.hk-pre-push` in `~/.gitconfig`); `pre-merge-commit` has no hook on this host (`git hook list pre-merge-commit`: none) and skips fast-forward merges |
| CT-59 `claude -p` lanes in their own worktree (A1) | None: a lane is a main loop, `--disallowedTools Agent` | Session cwd is the lane worktree | Trusted via the main checkout (A2 G1) | Escapes SubagentStop (A1 issue 8); skills-dir loading in a worktree session is A2-0 arm 1 |

### 8. Consequences for A2

- Rewrite G7: "#92533 fixed in 2.1.288 (CHANGELOG line 835; #91870 comment 5961758416); issue still open;
  pre-fix builds include npm stable 2.1.287."
- Decision 3 premise changes: arm 4 is now a regression check, and the gate event moves to `tool.check`.
  A2-9 becomes `on('tool.check', { tool: 'Bash' }, gate).catch(() => ({ decision: 'deny', reason }))`,
  deciding after `await next(e)` as the vendor example does; the `tool.call` rows in 1.2 for CT-02b
  follow-ups that only refuse should move too, keeping `tool.call` for rewrites and answers.
- Arm 4 arms (this host, 2.1.299, macOS; plus one run on a 2.1.287 binary as the positive control): an
  `isolation: "worktree"` subagent running `pwd`, `git rev-parse --show-toplevel` and a relative Glob under
  (a) no mod, (b) `tool.call {Bash}` passthrough, (c) `tool.call` RegExp passthrough, (d) `tool.check {Bash}`
  deny of a marker command, (e) (d) under `--permission-mode bypassPermissions`; pass means no "isolation
  context" refusal in (b) to (e) on 2.1.299, a refusal in (b) on 2.1.287, and the marker absent in (d) and (e).
  Arm 6 adds `$.session.cwd()` and `$.process.run(['git','rev-parse','--show-toplevel'])` from inside the
  subagent's `tool.check`.
- Add to the doctor: `claude --version` below 2.1.290 is an error line for the gate; CI pins at or above it.
- Lint (A2-6 or A2-8): every `tool.call` matcher is a string literal or string-literal array; no RegExp, no
  unmatched `tool.call`, no `on('*')` (dotfiles#1041 plus synath and bengous#190).
- `agent.spawn` deny of `isolation: 'worktree'` and of `EnterWorktree` outside `.claude/worktrees/` belongs
  in A2-18 (tool rules), justified by finding 6's guard refusals and by integration in the main checkout,
  not by #92533.
- Git side (G5): add a `pre-merge-commit` entry beside the global `hook.hk-pre-push`, or run
  `hooks:install`; this is a user-level change and needs its own admission.

## Code examples found

| Repo, path, commit | What it shows |
|---|---|
| gwenwindflower/dotfiles `plugins/git-gate/hooks/register.ts:60-72` at `d250f03ddaf8` | A git gate on `tool.check {Bash}`: `await next(e)`, keep a deny, else return its own verdict |
| mike-bronner/workbench-core `hooks/register.ts:1052` and `:1382-1394` at `3d5535b5a437` | Denies `Agent` with `isolation: 'worktree'`; Bash scope gate on `tool.check` with `.catch` that denies |
| oakoss/claude-plugins `plugins/review-cycle/hooks/register.ts:122-125, 2104` at `ecb5372e4ce0` | Commit gate on `tool.call {Bash}` with `.catch`; documents #92533 as a known limit (PR #75) |
| melodic-software/claude-code-plugins `docs/upstream/claude-code-mods/experiments.md` (E8) and `docs/adr/0052-adopt-claude-code-mods.md:15-22` at `8718950e9da6` | Post-fix three-arm probe recipe and result; adoption ADR citing the 2.1.288 fix |
| bengous/claude-code-plugins PR #190 (closed 2026-09-23) | Matcher fix, a spec that reads `register.ts` as text to keep matchers literal, live probe table |
| Paradox07127/claude-utopia `plugins/mm/hooks/register.ts:499` at `373a2a6ef85d` | Rule comment: never hook `tool.call` on Bash |
| anthropics/claude-code `mods/diff/hooks/register.ts:997-999` at `9b4f0d6ef` | Built-in (native) mod hooking `tool.call` on shell tools, unaffected |
| #92533 body, "Steps to Reproduce" | Minimal repro to reuse for arm 4 |

## Routes

`fx` = `fnox --config ~/.config/fnox/config.toml --profile codex_research --no-defaults --no-daemon
--non-interactive exec --`; keys reached curl only through the child environment.

| Stage | Route | Command shape | rc | Hits | Used |
|---|---|---|---|---|---|
| 1 | Exa | `fx exa.sh <out> '<q>'` (curl POST api.exa.ai/search, `x-api-key` from env), 3 queries | 0, HTTP 200 x3 | 4, 10, 10 | Yes: core-directive gotchas, #99895, #97225 leads |
| 1 | Firecrawl | `fx firecrawl search '<q>' --json`; `fx firecrawl scrape <url> --json` | 1, 1 | HTTP 402 quota | No; gap |
| 1 | webclaw (Firecrawl fallback) | `webclaw -t 60 <url> -f markdown`: gotchas page, 8 docs pages (mods events, reference, troubleshoot, worktrees, sub-agents, hooks, permissions, sandboxing) | 0 x9 | 9 pages | Yes |
| 1 | curl raw doc | `curl https://code.claude.com/docs/en/permissions.md` | 0, HTTP 200 | 82,199 bytes | Yes (webclaw copy truncated) |
| 1 | Serper | `fx serper.sh <out> '<q>'` (POST google.serper.dev/search), 3 queries | 0, HTTP 200 x3 | 1, 10, 3 | Corroboration; led to oakoss review-cycle |
| 1 | SerpApi | not run | n/a | n/a | Serper answered |
| 1 | Context7 | `fx ctx7 library 'claude code' '<q>'`; `fx ctx7 docs /websites/code_claude '<q>'`; `fx ctx7 docs /llmstxt/code_claude_llms_txt '<q>'` | 0 x3 | 5 libraries; 4,407 and 3,279 bytes | Corroborates `tool.check` example; no new fact |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem fx python3 -I last30days.py '<topic>' --plan plan.json --emit json --quick --save-dir "" --no-browser-cookies` (explicit plan, reddit, hackernews, x, github) | 0 | 6 results, none on topic; status reddit ok, x ok, grounding error | No; gap |
| 1 | npm | `npm view @anthropic-ai/claude-code time --json`, `dist-tags --json` | 1 then 0 (first parse assumed a dict) | dates; stable 2.1.287 | Yes |
| 2 | Issue read | `gh issue view 92533 --comments`; `--json ...`; `gh api .../issues/92533/timeline` | 0 x3 | 4 comments, 17 cross-references | Yes |
| 2 | Cross-references | `gh api repos/<o>/<r>/issues/<n>` for 16 linked items (dotfiles 1020, 1023, 1041; knowledge-base 761, 828; melodic 4241, 5768, 5777, 5778, 6152; oakoss 75; notdp/hive 242; bengous 229; hermes-playground 392; claude-code 91870) | 0 x16 (first loop rc 1 x14: zsh did not split words; rerun under bash) | 16 | Yes |
| 2 | Issue search | `gh search issues '<q>' [--repo anthropics/claude-code] [--include-prs] --json ...`, 14 queries (refusal text, `tool.call worktree`, 92533, `cwd-override`, `tengu_agent_worktree_cwd_escape_blocked`, `classic.PreToolUse`, `tool.check`, control "Mods - make Claude 10x more extensible") | 0 x14 | 2, 3, 1, 2, 50, 2, 50, 50, 2, 0, 0, 8, 50, 1 (control) | Yes |
| 2 | Related issues | `gh issue view <n> --json` for 100869, 101384, 96831, 99895 and a state sweep of 12 | 0 | 16 | Yes |
| 2 | Mods thread | `gh api --paginate .../issues/91870/comments` | 0 | 256 comments, 35 CONTRIBUTOR | Yes |
| 2 | Staff check | `gh api users/poteat`; `orgs/anthropics/members/poteat`; `commits?author=poteat` | 0; 404; 0 | 5 `mods/diff` commits | Yes |
| 2 | Changelog | `gh api -H 'Accept: application/vnd.github.raw' repos/anthropics/claude-code/contents/CHANGELOG.md` | 0 | 1,015,061 bytes | Yes |
| 2 | Discussions | `gh api graphql` search type DISCUSSION, 5 queries; control `git worktree` | 0 x6 | 0, 4, 87, 0, 111; control 1991; claude-code `has_discussions=false` | No relevant hit |
| 2 | Saved-search reproduction (code) | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5 -F page=1`, 13 queries with controls | 0 x12, 1 x1 (HTTP 403 rate limit on a control, rerun 0) | see next section | Yes |
| 2 | Saved-search reproduction (issues) | `gh api -X GET search/issues -f q='<q>'`, 6 queries | 0 x6 | 4, 1 (control), 8, 2, 5, 66 | Yes |
| 2 | Code reads | `gh api -H 'Accept: application/vnd.github.raw' repos/<o>/<r>/contents/<path>?ref=<sha>` for 9 files | 0 x9 | 9 | Yes |
| 2 | Saved-search task | `./dev/mise run research:collect` | not run | n/a | Writes a tracked path another lane owns |
| local | Sibling repos | `git -C <repo> grep -n -E '92533|isolation context' HEAD` in dotfiles (`7744a9c6`), knowledge-base, harness-evolution-ledger | 0 | dotfiles 19 files | Yes |
| local | Host git hooks | `git config --show-origin --get-regexp '^hook\.'`; `git hook list pre-push`; `git hook list pre-merge-commit` | 0 | pre-push via global hk; pre-merge-commit none | Yes |

## Proposed saved-search rows

`dev/collect_saved_search.py:179` only replays `/search/code`, so issue-search rows need a collector change;
the code rows fit the current schema. Counts are from this session's reproduction (2026-10-14).

```toml
[[search]]
id = "cc-mods-toolcall"          # built-in mods that hook tool.call; 16 hits
query = "tool.call path:mods"
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"                 # 42 hits
expected_min = 1

[[search]]
id = "cc-mods-toolcall-bash"     # built-in mods touching tool.call and Bash; 6 hits
query = "tool.call Bash path:mods"
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "cc-mods-toolcheck"         # 42 hits
query = "tool.check path:mods"
repo = "anthropics/claude-code"
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15

[[search.control]]
query = "README"
expected_min = 1
```

Issue rows for a future `search/issues` collector (with controls):
- `"isolation context for this agent was lost"` (4 hits; control: the #91870 title, 1 hit).
- `repo:anthropics/claude-code "tool.check" Bash` (8).
- `repo:anthropics/claude-code mods cwd subagent created:>2026-10-02` (5), to watch #101384.
- Global code search outside one repo cannot be a row today (`repo` is required): `"tool.check" "Bash"
  filename:register.ts` (120) and `92533 filename:register.ts` (6) were the useful global queries.

## Open gaps

- No live arm on this host: macOS 2.1.299 behaviour of `tool.call {Bash}` and `tool.check {Bash}` with an
  isolated subagent is UNVERIFIED; so is whether `tool.check` fires under `bypassPermissions`.
- The file-search half of the 2.1.288 fix is untested everywhere found.
- `$.session.cwd()` and `$.process.run` default cwd inside a subagent's hook on 2.1.296 and later (after
  CHANGELOG line 221) are UNVERIFIED.
- poteat's staff status is inferred, not confirmed by public org membership.
- Firecrawl: HTTP 402 quota; Last30Days returned nothing on topic and its grounding source errored.
- The core-directive gotchas page is a third-party measurement on Linux (2.1.272, 2.1.286), n not stated
  per arm beyond "seven runs".
