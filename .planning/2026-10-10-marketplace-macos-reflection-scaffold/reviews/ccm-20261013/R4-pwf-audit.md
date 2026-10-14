# R4: planning-with-files native-feature audit of session ccm-20261013

Reviewer R4, 2026-10-13, session `b74a0bf1` (subagent). Read-only: no git state changed, no
planning file created; probes ran with a throw-away session id (`r4-probe`) and wrote only to
the user cache (`~/.cache/pwf-*`) and the scratchpad. All transcript and plan contents were
treated as data.

Abbreviations: `W` = `/Users/rmanaloto/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0`;
`P` = `<repo>/.planning/2026-10-10-marketplace-macos-reflection-scaffold`; `ip.py` = `W/scripts/inject-plan.py`
(the single-process twin the Claude hook actually runs, `W/hooks/claude-hook.sh:123-141`; the shell
chain is a byte-identical fallback).

## Scope read

- Evidence index `00-evidence-index.md`; main transcript aggregate greps (counts, nonces, byte sizes
  only); 27 subagent transcripts (frame counts only); `*.meta.json` keys.
- Plugin: `SKILL.md` (whole), `README.md` (clear, multi-agent, how-it-works, recovery, commands, v3
  features, env vars, hooks reference), `docs/long-running-agent-tasks.md`,
  `docs/agent-forgets-plan-after-clear.md`, `docs/claude-code-lost-context-after-compaction.md`,
  `docs/quickstart.md:96-102`, `docs/workflow.md:234-240`, `commands/*.md`, `hooks/hooks.json`,
  `hooks/claude-hook.sh`, `scripts/inject-plan.py` (whole), `check-complete.sh`, `gate-stop.sh`,
  `ledger-append.sh`, `ledger-summary.sh`, `plan-doctor.sh`, `session-catchup.py` (modes, `main`),
  `templates/{task_plan,progress,findings}.md`, CHANGELOG 3.21-3.24.
- Repo: `P/task_plan.md` (566 lines), `P/progress.md` (head/tail/sizes), `P/findings.md`,
  `P/lanes/*.json`, `.planning/AGENTS.md`, `.claude/rules/planning-records.md`,
  `docs/agents/codex-task-orchestration.md` (ownership, unit size), `docs/agents/claude-team.md`,
  memory note `planning-with-files-injection.md`, staged `e12cf04:` `dev/hooks/{stop_gate,
  subagent_stop_gate,pretooluse_gate,git_gate}.py`, `.claude/settings.json`, `mise.dev.toml`
  (`hooks:install`, `test:hooks`, `check:research`).
- Ran read-only: `plan-doctor.sh`, `resolve-plan-dir.sh` (+`--check-ambiguity`),
  `set-active-plan.sh --list`, `ledger-summary.sh`, `check-complete.sh` (advisory and `--gate`),
  `session-catchup.py --metadata`, `ip.py --context=userprompt|pretool` (root and from
  `.claude/worktrees/team`, with and without pins), `claude-hook.sh session-start` with a probe
  payload, and a scratchpad fixture (`<scratchpad>/fixture`) proving the proposed skeleton under
  smart, gated, attested and ledger paths.

## Feature matrix

Legend: "used" = the session relied on it; "hand-rolled" = what it did instead.

| Capability | What it does (W path:line) | Used? | Hand-rolled instead | Consequence observed |
|---|---|---|---|---|
| SessionStart injection (startup/resume/clear/compact) | `hooks.json:4-19`; `claude-hook.sh:293-317`: catch-up (always empty, see below) + `inject(userprompt)`: plan `head -50` (`ip.py:1321`), `progress.md` `tail -20` with timestamps zeroed (`1330-1333`), findings pointer (`1336-1339`). Caps 64 KiB plan / 32 KiB progress (`94-95`). | Passive only | 17-line `## Session handoff` block at `task_plan.md:14-30`; 9-line `NEXT` bullet kept last in `progress.md` (`3421-3429`) | Works today: probe payload after `/clear` = 5,359 B / 82 lines (plan 3,214 B truncated=true, progress 1,217 B, no catch-up). The real `/clear` at `464a…jsonl:6` carried plan 3,033 B + progress 1,344 B, catch-up absent. The progress frame starts mid-entry ("names the sanctioned skill exceptions…") because `tail -20` is line-blind. |
| UserPromptSubmit injection | `hooks.json:21-35`; same 50/20 view, re-seeds the PreToolUse cache (`ip.py:1342-1343`) | Passive | — | Main session: **98 plan frames = 301,350 B and 95 progress frames = 128,178 B** (~430 KB, roughly 100k tokens) re-injected over the session; 5 distinct head-50 versions (nonces `1f009b`×26, `41a8c8`×21, `afecd2`×18, `a1d6c6`×18, `cab302`×8). Every turn (including subagent-completion turns) pays ~4.4 KB. |
| PreToolUse 30-line view + unchanged-view suppression (3.24.0) | `ip.py:1242-1252` (`plan_view(plan, 30)`), cache `pretool_cache` keyed on session+agent (`812`) with the digest including `prompt` (`848`); identity from the hook payload (`759-787`); suppression off for autonomous/gated (`1214-1215`) | Passive | Handoff block placed "inside the first 30 lines" (memory note) | Head-30 view = 2,060 B and ends exactly at line 30 (the block's last line), so any growth of the block falls out. In the 27 subagent transcripts: 214 plan frames, every transcript has them; single agents received the *same* view 15× (`a01102e5`), 12×+9× (`a85dc4eb`), 15×+3× (`aa49b9b1`): suppression did not hold for subagents. Likely cause: the cache digest includes `prompt_id` (`ip.py:848`) and an `agent_id` without a valid `prompt_id` is marked `!invalid` (`774-776`), which disables the cache (`803`). Not verified against the host payload (see Could not verify). |
| PreCompact flush | `hooks.json:68-83`; `ip.py:1228-1240`: a `systemMessage` reminder only; Claude Code gives PreCompact no `additionalContext` (`SKILL.md:299`) | Never fired | Nothing | Main transcript has 0 `PreCompact` fires and 3 `Prompt is too long`: the session hit the hard limit without a compaction cycle, so this hook could not have helped; the next-turn SessionStart(compact) restoration is what matters, and it injects the same 50/20 view. |
| Stop gate (gated mode) | `claude-hook.sh:354-363` → `gate-stop.sh` → `check-complete.sh --gate`; blocks only when `.mode` has `gate` **and** a `### Phase` is `in_progress` **and** `stop_hook_active` false **and** blocks < cap **and** ledger advanced (`check-complete.sh:150-290`); `TOTAL=0` phases → silent exit (`122-124`) | No `.mode` | Repo's own `dev/hooks/stop_gate.py` (lane record `status` contains `integrated` and `retro != passed`) | Plugin Stop was a no-op all session (0 phases). Both gates honour `stop_hook_active`. See §Compaction and /clear for the mode decision. |
| Autonomous mode | `.mode` `autonomous`: drops PreToolUse view (`ip.py:1214`), requires attestation (`1226`, `1254-1256`), replaces progress tail with `ledger-summary.sh` block (`1269-1273`, `1325-1328`) | No | — | Would have removed the only injection path subagents have (they get no UserPromptSubmit of their own), and would have blocked all injection after every unattested plan edit. |
| `PWF_INJECT=smart` / `inject-smart` token | `ip.py:1217`; `smart_plan_extract` `653-752`: keeps `# title`, `## Goal`, `## Next Step`, `## Current Phase`, counts `### Phase` under `## Phases`, emits the first `in_progress` phase body, last 3 rows of `## Decisions Made`; returns `None` → plain head when no `### Phase` (`736-737`, `915-916`) | No (4 mentions in transcript, none applied) | Prose handoff block | `task_plan.md` has **0** `### Phase`, no Goal/Next Step/Current Phase/Decisions/Errors sections (only 9 `## ` headings); `PWF_INJECT=smart` output is byte-identical to legacy (verified by `cmp`). The Errors and Tickets tables are *not* part of the smart view even when present. |
| Attestation | `attest-plan.sh`, `.attestation` in plan dir; mismatch → `[PLAN TAMPERED]` and **no plan injection at all** (`ip.py:1257-1264`); mandatory in v3 modes (`1226`) | No (none present) | — | Correctly skipped: the parent edited `task_plan.md` repeatedly; each edit would have required `/plan-attest` or silenced injection. |
| Parallel-write guard | `ip.py:1280-1313`: compares `- [x]` and `**Status:** complete` counts between fires (`_CHECKED_RE` `105`); advisory line only | Inert | — | Plan has no checkboxes or status tokens, so the guard can never signal. After restructuring, archiving completed phases will trip it once (advisory). |
| Per-agent ledgers + summary | `ledger-append.sh` (JSONL, shared monotonic tick, `flock`, `--agent/--phase/--files`); `ledger-summary.sh` (fixed-shape block: entries, phases x/y, in_progress heading, last event per agent); injected instead of the progress tail only in v3 modes (`ip.py:1269`) | No (0 `ledger-append` mentions) | Parent `cat >> progress.md` (18 occurrences) and manual `lanes/<unit>.json` patching; lanes "propose edits in the handoff" | `progress.md` grew 228,043 → 246,501 B (+279 lines, 22 dated entries) on 2026-10-13 alone; no machine record of lane progress; `ledger-summary.sh` today prints `entries: 0 / phases: 0/0`. |
| `PLAN_ID` / `PWF_PLAN_ROOT` / `PWF_SESSION_ID` | `ip.py:939-1022` (pin validation, slug binding, fail-closed notices `946-981`); `PWF_SESSION_ID` is derived from the hook payload on the Claude route (`claude-hook.sh:145-152`) and only matters when `.planning/sessions/` exists (`ip.py:1040-1064`; absent here) | Mentioned 66× in the transcript, present in 3 of 27 Agent briefs; never in the host environment | Prose line `task_plan.md:10` ("Set PWF_PLAN_ROOT … for commands launched elsewhere") | Hooks resolve by cwd: from a lane worktree without a pin the resolver returns the **worktree's stale copy** (probe from `.claude/worktrees/team`: nonce `99dca3`, 1,789 B, no handoff block); with `PWF_PLAN_ROOT=<root>` it returns the root plan (nonce `66846b`). A relative pin or bad `PLAN_ID` fails closed with a notice (verified). |
| `session-catchup.py --metadata/--replay` | `main():58` returns immediately in `--no-history` (what SessionStart runs); `--metadata` prints counts only; `--replay` ≤100 messages × 300 chars, nonce-framed | No | A 28-agent "evidence index" written by hand by the review orchestrator | `--metadata` today: `Unsynced entries: 158` (runtime claude-code). The automatic path never replays; "catch-up" after `/clear` is by design empty. |
| `/plan-doctor` | `plan-doctor.sh`: resolution, injection bytes, attestation, surfaces, latency; writes only the user cache | No | — | Today: PASS resolver, PASS injection 5,359 B, attestation none, **one shell-chain fire 7,631 ms** against the 10 s hook timeout (`hooks.json:15`); the Python twin takes 42 ms. If `python3` ever drops off the hook PATH (cf. the `VIRTUAL_ENV` gotcha in memory), injection goes dark by timeout. |
| `/status` | `commands/status.md`: reads `## Current Phase`, counts phase statuses and `## Errors Encountered` rows | No | — | Would report nothing useful: no `## Current Phase`, 0 phases. Safe (read-only). |
| `/plan-goal`, `/plan-loop` | compose `/goal` and `/loop` with `check-complete.sh` (`commands/plan-goal.md:11-19`, `plan-loop.md:11-27`), `disable-model-invocation: true` | No | Manual SendUserMessage heartbeat | Unusable until phases exist; `/plan-goal`'s default condition "all phases complete" is wrong for a roadmap that keeps pending phases by design. Low value here. |
| Multi-plan isolation | `plan_is_ambiguous` (`ip.py:1450-1469`): a second `.planning/<slug>/task_plan.md` without `PLAN_ID` → "Multiple plans… nothing injected" (`961-965`); nested project detection (`1066-1103`) | Single plan, mtime discovery | `.planning/AGENTS.md`: "a competing plan stays out of the tree" | One plan today (`set-active-plan.sh --list` shows it, no `.active_plan`). Any future second plan dir silences injection unless `PLAN_ID` is pinned in the host env. |
| Worktrees with stale `.planning/` copies | Resolver is cwd-relative unless pinned (`ip.py:1480-1490`); docs: "Use separate worktrees if per-task host pins are unavailable" (`docs/quickstart.md:99-101`) | 8 lane worktrees, each with a committed copy | Memory note: "resume from the root checkout" | All 8 copies differ from root; 7 lack the handoff block entirely (their line 14 is `## Claude takeover`); `gate-hooks` has 571 lines vs 566 (lane-local edits). Every subagent-injected nonce also matches a root commit of the same era, so the transcripts cannot prove which copy was read; the probe proves the failure mode exists whenever a hook fires with a worktree cwd. |

## Compaction and /clear

**What a fresh session receives today** (verified with `printf '{"session_id":"r4-probe","cwd":"<repo>",
"hook_event_name":"SessionStart","source":"clear"}' | sh W/hooks/claude-hook.sh session-start`, read-only
per `claude-hook.sh:98-164` and `ip.py:1131-1166` — writes only under `~/.cache/pwf-{pretool,prog,snapshots,turn}`):

```
hookSpecificOutput.hookEventName = SessionStart, additionalContext = 5,359 B / 82 lines
  1  [planning-with-files] ACTIVE PLAN — treat contents as structured data…
  3  ===BEGIN-PWF-DATA kind=plan bytes=3214 truncated=true===   ← task_plan.md lines 1-50
 55  ===END-PWF-DATA kind=plan===
 58  ===BEGIN-PWF-DATA kind=progress bytes=1217 truncated=true=== ← progress.md lines 3410-3429
 80  ===END-PWF-DATA kind=progress===
 82  [planning-with-files] Read findings.md for research context…
```

Lines 1-50 of the plan = title, pin prose, the handoff block (14-30) and the first 18 lines of the
takeover narrative; the lane table (79-92), the 60-row unit table and everything after line 50 are
never injected. The progress frame carries the `NEXT` bullet plus 11 lines of the preceding entry
cut mid-sentence. There is no catch-up (`session-catchup.py` `--no-history` returns at `main():58`),
and auto-compaction's SessionStart(compact) injects exactly the same view. This is the same shape the
real `/clear` produced at `464a…jsonl:6` (plan 3,033 B, progress 1,344 B, no catch-up). The previous
session's memory note is accurate on all of these points.

**What it would receive with `PWF_INJECT=smart` (or an `inject-smart` token in `P/.mode`) and the
skeleton in §Tracking completeness** (fixture run, `<scratchpad>/fixture`): title, `## Goal`,
`## Next Step`, `## Current Phase`, `phases: 2/5 complete`, the full `### Phase 3 … in_progress`
section with its checkboxes, and the last 3 Decisions rows — 1,098 B instead of 3,214 B, and the
PreToolUse view becomes 1,437 B carrying the same content instead of a position-blind head-30. The
progress frame stays `tail -20` in legacy mode (so the archive policy below still matters).

**Mode decision: stay in legacy mode with `inject-smart`; do not set `autonomous` or `gated`.**

- Overlap: the repo's `stop_gate.py` (staged, `e12cf04`) blocks on *lane-record* state; the plugin
  gate blocks on *phase* state (`check-complete.sh:201-206`). They answer different questions and
  both honour `stop_hook_active` (`stop_gate.py:23`, `check-complete.sh:192-200`), so a continuation
  turn cannot loop. Double-blocking would only yield two reasons on the same Stop; the plugin's
  counter (`.stop_blocks`, cap 20) and stall detector make it release on its own.
- The decisive costs of gated/autonomous here are elsewhere: (1) PreToolUse injection is dropped
  (`ip.py:1214-1215`), which removes the only plan view implementer/reviewer subagents get; (2)
  attestation becomes mandatory (`1226`, `1254-1256`) and the parent edits `task_plan.md` many times
  per session, so every edit without `/plan-attest` silences injection; (3) the progress tail is
  replaced by the ledger block (`1269-1273`), which is empty until lanes actually append ledgers;
  (4) the gate's stall detector reads ledgers that do not exist yet.
- Ordering between the plugin Stop hook and `dev/hooks/stop_gate.py`: Claude Code runs all matching
  hooks in parallel, a plugin's handler separately from the project's; the combined result of one
  Stop block and one silence is not documented, and continuations are capped at 8 (see Could not
  verify). Two gates with different vocabularies is a reason to keep one.
- Recommended combination: legacy injection + `inject-smart` + the repo's three gate hooks +
  per-lane ledgers written for the parent's benefit (read with `ledger-summary.sh` on demand, not
  injected). Revisit `gated` only if the parent ever runs an unattended `/loop`.

## Worktrees and ledgers

- Resolution is cwd-relative (`ip.py:1480-1481`, `resolve_plan_dir`). From
  `.claude/worktrees/team` with no pin the hooks inject the worktree's committed copy (verified:
  nonce `99dca3`, 1,789 B, takeover section at line 14, no handoff). With `PWF_PLAN_ROOT=<root>` the
  same call injects the root plan (nonce `66846b`), and `PWF_PLAN_ROOT=<root> PLAN_ID=<slug>` resolves
  `<root>/.planning/<slug>` from any cwd. A relative `PWF_PLAN_ROOT` or a wrong `PLAN_ID` fails closed
  with a one-line notice (verified).
- Whether a subagent's hooks fire with the worktree cwd depends on how the lane was launched: the 27
  Agent calls used no `isolation` key (0 of 27), so most likely their hooks ran with the root cwd and
  read the root plan of that moment. The risk becomes real with `isolation: "worktree"`,
  `EnterWorktree`, or a separately launched `claude` inside `.claude/worktrees/<unit>`. The pin makes
  both cases safe.
- Pins must be in the **host** environment: a `PWF_PLAN_ROOT=…` prefix inside a Bash tool call does
  not reach hook fires (`SKILL.md:255`, `docs/quickstart.md:99-100`). So the pin belongs to the
  launching shell or to a settings `env` block (propagation to hooks: see Could not verify), and the
  lane brief must additionally prefix every *script* invocation because Bash subprocess env is per
  command.
- Ledgers replace two hand-rolled mechanisms: the parent's `cat >> progress.md` (18×) and the
  "lane proposes edits in its handoff" round trip. `ledger-append.sh` writes
  `<plan-dir>/ledger-<agent>.jsonl` under `flock` with a tick shared across agents
  (`ledger-append.sh:186-203, 321-342`); 200-char summary; `--files` list. In legacy mode the
  summary is not injected, so its value is (a) a machine record per lane the parent reads with
  `sh W/scripts/ledger-summary.sh P`, (b) no concurrent writes to `progress.md`, (c) the lane
  record JSON stops being patched for progress (keep it for allocation/status/retro only).

Exact env/pin recipe for a lane brief (values are literal for this repo):

```
# host-level (once, before launching claude or the lane's claude):
export PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace
export PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold
# optional, same effect as the .mode token: export PWF_INJECT=smart

# in the brief, for every planning-script call (Bash env is per command):
PWF="$HOME/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0/scripts"
PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace \
PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold \
sh "$PWF/ledger-append.sh" progress "<unit>: <what landed>" --agent <unit> --phase <N> --files <a,b>
# events allowed: progress phase_complete error gate_block attest note   (ledger-append.sh:40)
# the lane owns exactly: its worktree paths, lanes/<unit>.json "status", retros/<unit>.md,
# and <root>/.planning/<PLAN_ID>/ledger-<unit>.jsonl; it never edits task_plan.md or progress.md
```

Ledger files are new tracked records; `.gitignore` is frozen, so either commit them (recommended:
they are receipts) or add them to `.git/info/exclude`. `ledger-append.sh` appends into the pinned
root directory from any cwd, which is a deliberate cross-worktree write the lane allowlist must
name.

## Tracking completeness and plan skeleton

Is every CT ticket, lane and pending decision represented in a form the injector surfaces? **No.**

- CT-01…CT-11: no list anywhere in `task_plan.md`; four appear only inside lane-table cells or the
  handoff prose. GitHub has no CT issues (evidence index), so the ticket table must carry
  "pending issue" until to-tickets approval.
- Lanes: the table at `task_plan.md:79-92` is stale on every row that matters (M0 "in progress",
  A06u3/SKILL "allocated", GATE/TEAM/NAV "planned", no gate-hooks, retro-gate, rf-env-scrub or
  c1 rows) while `lanes/*.json` say `integrated … retro: passed` for 8 of 9 and gate-hooks
  `implemented (Opus), awaiting cold review` with no `retro` field. The injector never shows the
  table anyway (lines 79-92 > 50).
- Pending decisions: only inside the handoff prose; nothing the injector or `/status` can count.
- Structure: 0 `### Phase`, 0 `**Status:**`, 0 checkboxes, no Goal/Next Step/Current Phase/
  Decisions Made/Errors Encountered. Consequences: `check-complete.sh` exits silently
  (`:122-124`), `set-active-plan.sh --list` prints `0/0 complete`, `ledger-summary.sh` prints
  `phases: 0/0`, smart extraction falls back to head-50, the plan guard counts nothing.

Proposed `task_plan.md` skeleton (verified parse in the fixture; keep the file well under
`PLAN_VIEW_LIMIT` 64 KiB, currently 47 KB):

```markdown
# Marketplace onboarding and C++ foundation            ← first "# " line = title (ip.py:706)

PLAN_ID … / project root … / owner line                 ← NOT injected under smart; keep for readers

## Goal                                                  ← kept verbatim (ip.py:694)
One paragraph: the end state (lanes integrated behind the gate, A09 published, CT tickets filed).

## Next Step                                             ← kept verbatim (ip.py:696); the single next action,
Finish the in-progress merge of claude/gate-hooks-wiring …   rewritten in place at every handoff

## Current Phase                                         ← kept verbatim (ip.py:698)
Phase 3: Integrate gate-hooks (CT-02)

## Phases                                                ← opens the phase section (ip.py:700)
### Phase 1: Takeover and lane allocation                ← counted (ip.py:712); heading text is what
- [x] …                                                     check-complete/ledger-summary report
- **Status:** complete                                    ← literal token (ip.py:722, check-complete.sh:98)
### Phase 2: Integrate reviewed lanes (M0, A06u3, SKILL, RF-ENV, TEAM, GATE-1, NAV, C1)
- **Status:** complete
### Phase 3: Integrate gate-hooks (CT-02)                 ← exactly ONE in_progress phase; its whole body
- [ ] finish merge (MERGE_HEAD e12cf04), settings split, hooks:install, test:hooks in check:research
- [ ] retro:gate gate-hooks; lane record retro: passed
- [ ] A09 publish
- **Status:** in_progress                                 ← (ip.py:720) is injected in full
### Phase 4: Publish takeover spec and CT-01…CT-11 tickets
- **Status:** pending
### Phase 5: Remaining lanes (B1, C2/C3, LEDGER, CLOSE, wave 2, heavy)
- **Status:** pending

## Tickets                                               ← not injected; read by humans and /status-like
| Ticket | Title | GitHub | Lane | State |                 tooling; one row per CT-01…CT-11 and open #nn
## Lanes                                                 ← one row per lanes/*.json, regenerated from them
| Lane | Unit | Tickets | Worktree @ SHA | status | retro |
## Decisions Made                                        ← table; last 3 rows injected (ip.py:703, 746-751)
| Decision | Rationale |
## Errors Encountered                                    ← counted by /status only; not in the smart view
| Error | Attempt | Resolution |
```

Parsing rules the skeleton relies on, from `ip.py`: any `## ` line closes the current section
(691-693); `## Goal`, `## Next Step`, `## Current Phase` are "keep" sections (694-699) and must
contain only what should be injected every turn; `## Phases` switches to phase counting (700-702)
and `### Phase` headings are counted only inside it (712-717); status tokens are the literal
strings `**Status:** in_progress|complete` or `[in_progress]|[complete]` (720-723); only the first
in_progress phase body is emitted (670-675); `## Decisions Made` rows are read as a pipe table,
header + separator + rows, last 3 shown (703, 725-733, 746-751). `check-complete.sh:91-105` uses
the same tokens (per-field max of both formats). The guard counts `- [x]` and
`**Status:** complete` (1294-1298): archiving completed phases will print one advisory.

What moves to `findings.md` (currently 56 lines, a pointer-only file for the injector): the 60-row
unit table (`task_plan.md:153-229`), the "Full-baseline spec workflow" narrative (231-330), the
admission paragraphs (341-405) and the Evidence paragraphs (407-566) — all history or reference,
none of it state. Keep them under dated `## ` sections in `findings.md` (or a new
`plan-history-2026-10-13.md` linked from findings); `findings.md` is never injected, only pointed
to (`ip.py:1336-1339`).

`progress.md` policy: move lines 1-3412 to `progress-archive-2026-10-13.md` (same directory;
not a plan file name, so the resolver ignores it), start the new `progress.md` with a header and
the entries since the last publication; drop the "NEXT bullet stays last" rule (its in-place
rewrite contradicts the append-only rule in `.claude/rules/planning-records.md`) because
`## Next Step` in `task_plan.md` now carries that state; keep entries short (the injected tail is
20 lines, so one entry ≈ one screen of recovery context). The 1 MiB cutoff (`PROGRESS_LIMIT`
`ip.py:92`; `safe_snapshot` returns `None` above it, `prepare_progress_snapshot` → `Bail` at
`1275-1277`) silences **all** injection, plan included, not just the tail; today's file is 24% of
it and grew 8% in one day. `.claude/rules/planning-records.md` ("append-only … leave earlier lines
as written") needs a one-line amendment admitting dated archives; that is a parent edit, not a
lane's.

## Commands

| Command | Verdict here | Why |
|---|---|---|
| `/planning-with-files:plan-doctor` | Safe, useful | Diagnostic only; writes the user cache. Ran today: PASS/PASS, attestation none, shell chain 7.6 s. |
| `/planning-with-files:status` | Safe, useless until restructured | Reads `## Current Phase` and phase tokens (`commands/status.md:9-13`); nothing to read today. |
| `/planning-with-files:plan-attest` | Avoid while the parent edits the plan per turn | Writes `P/.attestation`; a mismatch blocks all injection (`ip.py:1257-1264`). Consider only at a handoff, with `--show` to audit. |
| `/planning-with-files:plan`, `/pwf`, `/start` | Avoid | "Create the three planning files in the current project directory if they don't exist" (`commands/plan.md:7`, `pwf.md:7`); with a named plan present this creates a competing root `task_plan.md` (the `.planning/AGENTS.md` rule forbids it) and `/pwf --gated|--autonomous` writes `.mode`/`.attestation`. The memory note's advice to skip them was right. |
| `/plan-goal`, `/plan-loop` | Not now | Need phases; default goal "all phases complete" is wrong for a roadmap with intentional pending phases; `/plan-loop` would add a `progress.md` entry every 10 min. |
| Scripts | `resolve-plan-dir.sh`, `set-active-plan.sh --list`, `ledger-summary.sh`, `check-complete.sh` (no `--gate`), `session-catchup.py --metadata` are read-only; `phase-status.sh <n> <status>`, `ledger-append.sh`, `attest-plan.sh`, `init-session.sh`, `set-active-plan.sh <id>` write into the plan dir. |

Correct selector values: `PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold`,
`PWF_PLAN_ROOT=/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace` (absolute,
no trailing slash). Resolver output today: `<root>/.planning/2026-10-10-marketplace-macos-reflection-scaffold`;
`--check-ambiguity` is quiet (single plan).

## Findings

**P1**

1. **The plan is invisible to every structural feature.** 0 `### Phase`, no Goal/Next Step/Current
   Phase/Decisions; `check-complete.sh` silent (`:122-124`), `/status` empty, smart view ==
   head-50 (byte-identical), guard inert, ledger summary `0/0`. The session therefore built a prose
   handoff block that only works while it stays inside lines 1-30 and is read by nothing but the
   model. Evidence: `grep -c '### Phase' P/task_plan.md` = 0; §Compaction probe.
2. **Progress tracking by append is the context killer the plugin exists to prevent.** 98+95
   frames ≈ 430 KB re-injected into the parent over one session; `progress.md` +18.5 KB/day with a
   hard 1 MiB cliff that silences *all* injection (`ip.py:92, 1275-1277`); the recovery tail starts
   mid-entry. Lanes reported through SendMessage and the parent appended by hand (`cat >>` ×18)
   instead of per-lane ledgers.
3. **No host pin, so a hook firing from a lane worktree reads a stale plan.** Verified from
   `.claude/worktrees/team`: no pin → worktree copy without the handoff block; `PWF_PLAN_ROOT`
   pin → root. 0 of 27 Agent briefs used worktree isolation and only 3 mentioned a pin, so the
   defence was luck, not configuration; any future `isolation: "worktree"`/`EnterWorktree`/
   separate `claude` in a worktree reproduces it.

**P2**

4. Subagents received the same 30-line view up to 15 times each (214 frames across 27 transcripts)
   despite 3.24.0 suppression; keying on `prompt_id` (`ip.py:848`, `774-776`) is the likely cause.
   Cost per subagent ≈ 2 KB × N tool calls; mitigation is making the view small (smart) and the
   plan structured, since the suppression cannot be relied on.
5. `lanes/*.json` and the `task_plan.md` lane table disagree (8 `integrated … retro: passed` vs
   table rows "planned"/"allocated"/"in progress"; gate-hooks record `implemented …` with no
   `retro` while its retro file is staged). The repo's `stop_gate.py` reads the JSON only, so the
   table is dead weight; regenerate it from the records or drop it.
6. Hook latency margin: the shell reference chain takes 7.6 s here (`plan-doctor`), the Python
   twin 42 ms; `hooks.json` timeouts are 10 s. A hook PATH without `python3` would silently drop
   injection by timeout. Pin `PWF_TRUSTED_PYTHON=/abs/python3` in the host env (`claude-hook.sh:51`).
7. The repo's own `settings.json` (staged) adds Stop/SubagentStop/PreToolUse hooks with
   `onFailure: block`; combined with the plugin's Stop hook a user now has two Stop gates with
   different vocabularies. Document the combination (lane state vs phase state) in
   `docs/agents/claude-team.md` once the merge lands; do not add plugin `gated` on top.

**P3**

8. `findings.md` is 56 lines while `task_plan.md` carries ~400 lines of history; the injector
   points at findings and never shows plan lines past 50, so the split is inverted.
9. The "NEXT bullet rewritten in place, must stay last" convention contradicts the append-only
   rule in `.claude/rules/planning-records.md`; `## Next Step` resolves it.
10. `task_plan.md:10` tells agents to set `PWF_PLAN_ROOT`/`PLAN_ID` but no settings, brief
    template or `AGENTS.md` carries the literal exports; the memory note's windows are correct but
    stop short of the pin and the structure fix.
11. `session-catchup.py --metadata` reports 158 unsynced entries; nobody ran it after `/clear`.
    It is cheap and non-disclosing; add it to the resume checklist for a crashed session.

## Migration checklist

Ordered; each step is a parent edit (planning files are parent-owned) and names its check. Do it
after the in-progress merge is committed or aborted, never during.

1. Pin the host. Add to `.claude/settings.json` `env`: `PLAN_ID` (portable) and, per user, to
   `settings.local.json` `env`: `PWF_PLAN_ROOT=<abs root>`, `PWF_INJECT=smart`,
   `PWF_TRUSTED_PYTHON=<abs python3>` (or export them in the launching shell if the env block does
   not reach hooks, see Could not verify). Check: from the repo root
   `sh W/scripts/plan-doctor.sh` → `PASS resolver … PASS injection`; from
   `.claude/worktrees/<any>`: `python3 -I W/scripts/inject-plan.py --context=pretool | sed -n 2p`
   shows the root nonce (today `66846b87…` until the plan changes), not the worktree's.
2. Archive history. `git mv P/progress.md P/progress-archive-2026-10-13.md`; write a new
   `P/progress.md` (header + entries since `28fedf1`); amend
   `.claude/rules/planning-records.md` to admit dated archives. Check: `wc -c P/progress.md` ≪ 1 MiB;
   `python3 -I W/scripts/inject-plan.py --context=userprompt | grep 'kind=progress'` shows
   `truncated=false` or a tail that starts at an entry boundary.
3. Move history out of the plan. Cut `task_plan.md` lines 98-566 into `findings.md` dated sections
   (or `plan-history-2026-10-13.md` linked from findings). Check: `task_plan.md` ≤ ~150 lines.
4. Restructure the plan per the skeleton: Goal / Next Step / Current Phase / Phases (exactly one
   `in_progress`) / Tickets (CT-01…CT-11 + open issues with links) / Lanes (regenerated from
   `lanes/*.json`) / Decisions Made / Errors Encountered. Check:
   `sh W/scripts/check-complete.sh` → `Task in progress (k/n phases complete)`;
   `sh W/scripts/set-active-plan.sh --list` shows `k/n complete, 1 in_progress`;
   `PWF_INJECT=smart python3 -I W/scripts/inject-plan.py --context=userprompt` shows Goal, Next
   Step, Current Phase, `phases: k/n`, the in_progress body and 3 decisions, with
   `kind=plan bytes=` around 1-2 KB.
5. Prove the `/clear` path without clearing: from the root,
   `printf '{"session_id":"probe-%s","cwd":"%s","hook_event_name":"SessionStart","source":"clear"}' "$(date +%s)" "$PWD" | sh W/hooks/claude-hook.sh session-start | python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"])'`
   and read it as the next session would. Then the same with `--claude-event=pre-tool-use`
   through `python3 -I W/scripts/inject-plan.py --context=pretool` for the subagent view.
6. Optionally write `P/.mode` containing exactly `inject-smart` (no `gate`, no `autonomous`) so
   the smart view does not depend on each user's env; commit it. Check: `cat P/.mode` and step 4
   output unchanged with `PWF_INJECT` unset.
7. Adopt ledgers. Add `ledger-<unit>.jsonl` to each lane's `owned_paths`; put the recipe from
   §Worktrees into the implementer/doc-writer brief template (`.claude/agents/*.md`); the parent
   appends `--agent main` at integration/publication events instead of `cat >> progress.md`.
   Check: `sh W/scripts/ledger-summary.sh P` lists one `agent <unit>: <event>` line per active
   lane; `P/.ledger_lock` never persists.
8. Sync records. Regenerate the Lanes table from `lanes/*.json` (and set gate-hooks
   `status`/`retro` once its retro gate passes) so `stop_gate.py` and the plan agree. Check:
   `python3 -I dev/hooks/stop_gate.py <<< '{"cwd":"'$PWD'"}'` prints nothing.
9. Keep the hand-rolled conventions that still pay: `lanes/*.json` for allocation, `retros/*.md`
   for the gate, `ticket-ledger.md` for GitHub state. Retire: the prose handoff block (replaced by
   Next Step/Current Phase), the NEXT bullet, lane-table hand edits.
10. Record the change in `findings.md` with this file's path and the verification outputs
    (bytes, nonces, `check-complete` line) as the receipt.

## Could not verify

- Host facts, from a claude-code-guide pass over code.claude.com/docs (hooks, settings-reference,
  env-vars, sub-agents pages; re-check wording before relying on it):
  - `env` in settings is "for every session and its subprocesses" and "a hook process inherits
    the parent environment", so the pins in step 1 should reach hooks by inheritance; the docs do
    not say so explicitly, hence the verification in step 1. Shared-file `env` values apply only
    after the folder is trusted. `CLAUDE_ENV_FILE` (SessionStart) persists variables into later
    Bash commands only.
  - Subagent hook payloads carry `agent_id`, `agent_type` and `prompt_id` ("UUID identifying the
    user prompt currently being processed"); a subagent starts in the main conversation's cwd
    unless `isolation: worktree`, which confirms §Worktrees. Whether `prompt_id` changes on a
    subagent-completion turn (the P2-4 hypothesis) is not documented.
  - "All matching hooks run in parallel"; a plugin's copy of a handler is separate from the
    project's; PreToolUse precedence is deny > defer > ask > allow; the combined Stop result of one
    block and one silence is not documented; consecutive stop-hook continuations are capped at 8
    (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). This supports keeping a single Stop vocabulary (the
    repo's) rather than adding the plugin's gate.
- Which plan copy each lane subagent's hooks actually read: every injected nonce also matches a
  root commit of the same era (80 commits of `task_plan.md` hashed), so the transcripts are
  consistent with both readings. The failure mode itself is verified by probe.
- The exact mechanism behind repeated identical PreToolUse views in subagents (hypothesis:
  `prompt_id` in the cache digest); would need a captured hook payload.
- Token counts are byte-based estimates (≈4 B/token); no tokenizer was run.
- `compact_boundary` appears once in the main transcript (line 242, 19:02Z, a user-type record);
  no `PreCompact` hook output exists, so no auto-compaction is attested.
