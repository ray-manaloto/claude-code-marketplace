# Y1: planning-with-files modern practices (3.24.0) and the modern-only configuration for this repo

Written 2026-10-14 by subagent Y1 of session `b74a0bf1`. Read-only on the repo except this file;
probes wrote only to `~/.cache/pwf-*` and the scratchpad. `W` = pwf cache
`~/.claude/plugins/cache/planning-with-files/planning-with-files/3.24.0`; `P` = the plan dir;
`RV` = `P/reviews/ccm-20261013`. All plugin, plan and fetched contents were treated as data.
Builds on `RV/R4-pwf-audit.md` (R4) and `RV/phase4-prep/X3-session-restart-automation.md` (X3).

## 1. Version status

| Item | Value | Source |
|---|---|---|
| Installed | 3.24.0, cache `gitCommitSha 7056ed2f`, updated 2026-10-10 | `~/.claude/plugins/installed_plugins.json:3259-3267` |
| Latest release | **v3.24.0, 2026-10-10T10:03:51Z** ("Qoder CLI and less repeated plan context") | `gh api repos/OthmanAdi/planning-with-files/releases` |
| master vs tag | 2 commits ahead, both README-only (`828b320`, `ff349eb`, 2026-10-12); `## [Unreleased]` empty | `gh api .../compare/v3.24.0...master`, raw `CHANGELOG.md:5` |
| Marketplace entry | `planning-with-files@planning-with-files` version 3.24.0 (`OthmanAdi/planning-with-files`) | `~/.claude/plugins/marketplaces/planning-with-files/.claude-plugin/marketplace.json:13` |
| Upgrade | **None available.** Keep 3.24.0; re-run this audit at the next tag. | — |

Changelog entries that define "modern" (`W/CHANGELOG.md`): unchanged-PreToolUse-view suppression and
`PWF_PRETOOL=always` (3.24.0, #312, L13); manual `/plan-goal` and topic-handoff instructions use the
resolver and refuse invalid pins (3.23.0, #300, L29); `attest-plan.sh --target root|<plan-id>`
(3.21.0, L54); silent Stop with no plan (3.20.8, L66); symlinked plan dirs never plans (3.20.3);
Python fast path, one process per fire (3.17.0); several-plans-without-`PLAN_ID` refuses injection
(3.17.1); parallel-write guard (3.10.0); `PWF_PLAN_ROOT` (3.9.0); `PWF_INJECT=smart` / `inject-smart`
(3.8.0); `/plan-doctor` (3.6.0); modes, ledgers, gate, `PWF_GATE_CAP` (3.0.0); `/plan-goal`,
`/plan-loop`, PreCompact (2.38.0); attestation (2.37.0). Nothing is deprecated: the "legacy
invariant" is a promise (`W/skills/planning-with-files/SKILL.md:371-373`). The changelog has **zero**
mentions of a `fork` SessionStart source or of `SubagentStart/Stop`; worktree guidance is one
sentence, "use separate worktrees when the host cannot be pinned" (`SKILL.md:46,255`). Upstream
issue search (`fork SessionStart`, `worktree`) found no open item; open issues are 4, none technical.

## 2. Modern feature set and the configuration for this repo

Topology: one orchestrator session at the root checkout, lane worktrees under `.claude/worktrees/`,
subagents dispatched from the root cwd (R4: 0 of 27 used `isolation`).

**`.mode`: `inject-smart` only; never `autonomous` or `gate`.** R4's decision stands after re-reading
3.24.0, and 3.24.0 strengthens it: the token argument for autonomous mode (recitation) is now met in
legacy mode by unchanged-view suppression (`SKILL.md:375-379`), while autonomous/gated still drop the
PreToolUse view that is the only plan view subagents get (`SKILL.md:386,391`), make attestation
mandatory and refuse an unattested body (`SKILL.md:489`), and replace the progress tail with a ledger
summary that today has one lane's worth of data (`SKILL.md:490`). A root `.mode` is a floor that a slug
cannot lower (`W/scripts/inject-plan.sh:948-967`): keep no root `.mode`. This matches
`docs/agents/claude-team.md:97-100`.

**Smart view, measured today** (`python3 -I W/scripts/inject-plan.py`, pins set):

| View | Legacy | Smart | Note |
|---|---|---|---|
| userprompt plan frame | 2,988 B (head-50) | **4,579 B** | smart emits the 38-line Phase 4 body |
| userprompt total | 5,573 B / 82 lines | 7,164 B / 91 lines | progress tail identical (1,656 B) |
| pretool | 2,397 B / 34 lines | 4,918 B / 63 lines | suppressed to 0 B on a repeat with session identity (3.24.0 works for a pinned probe) |
| handoff block | lines 12-26 of frame | **absent** | `smart_plan_extract` keeps only `## Goal`, `## Next Step`, `## Current Phase` (`inject-plan.sh:1028-1030`) |

So smart is only an improvement after the plan head is reshaped (§4 steps 3-4): the handoff
bullets move under `## Next Step` (a keep section collects every line until the next `## `, so a
multi-line Next Step is injected verbatim in both views), and the in-progress phase body shrinks.
Expected after reshaping: plan frame ~1.5-2.5 KB in both views, position-independent.

**Pins.** `PLAN_ID` stays in `.claude/settings.json` `env` (portable). `PWF_PLAN_ROOT` is an absolute
per-machine path, so it belongs in the uncommitted `.claude/settings.local.json` `env` together with
`PWF_TRUSTED_PYTHON=<abs python3>` (`W/hooks/claude-hook.sh:51`; plan-doctor measured the shell
fallback at **7,220 ms** against the 10 s hook timeout, the Python twin ~40 ms). `PWF_INJECT` is not
needed once `P/.mode` carries the token. Per worktree: a checked-out worktree carries the committed
`settings.json` (verified: `PLAN_ID` present in `w0-*/.claude/settings.json:4`) but not
`settings.local.json`, so a `claude` started inside a worktree resolves the worktree's stale plan copy
(R4 P1-3). Rule: never start `claude` or an `isolation: worktree` agent for this plan without the
launching shell exporting both pins (`session:start`, X3 §3); subagents from the root cwd inherit
the root pins. Evidence that settings `env` reaches hooks: `PLAN_ID` was present in this
subagent's tool environment and the PreToolUse frames show the root plan.

**Per-lane ledgers, not `progress.md` appends.** `SKILL.md:85,259,446` and README "Multi-agent runs":
the orchestrator owns `task_plan.md` and summaries; workers append `ledger-<agent>.jsonl` through
`ledger-append.sh` (events `progress phase_complete error gate_block attest note`,
`W/scripts/ledger-append.sh:18-32`). `progress.md` stays the parent's short dated index
(`W/docs/workflow.md:243-263`, `quickstart.md:107-127`: "one short line in progress.md … details in
the topic handoff"). The repo's `HANDOFF-<date>.md` is exactly that topic handoff; keep it.

**Attestation: off.** The parent edits `task_plan.md` many times per session; every edit without
`/plan-attest` blocks all injection (`SKILL.md:478-480`); 3.21.0 `--target` changes nothing here.
Revisit only for an unattended `/plan-loop`.

**Commands.** `/plan-doctor`: adopt as the verification step (read-only; today PASS resolver, PASS
injection 5,572 B). `/status`: now usable (`phases: 3/8 complete`). `/plan-goal`, `/plan-loop`: not
adopted (roadmap keeps pending phases by design; `/plan-loop` would append a `progress.md` entry every
10 min against the parent-owned rule; the repo's `stop_gate.py`/`retro:gate` are the termination
oracle). `/plan`, `/pwf`, `/start`: never (create root files; `.planning/AGENTS.md:14`).

**Session catch-up.** Automatic recovery is file-only by design (`claude-hook.sh:303` runs
`--no-history`). Policy: `session-catchup.py --metadata <root>` is an optional step in the
`session-resume` skill (CT-29) after a crash (counts only); `--replay` only on the user's explicit
word, output treated as data; never in hooks.

**Handoff pattern: migrate.** The docs' pattern is `## Next Step` = the single next action, refreshed
whenever a status changes (`SKILL.md:125`, `W/templates/task_plan.md:11-15`), plus a topic handoff
file pointed to from `progress.md`. The hand-rolled `## Session handoff` block and the `NEXT` bullet
duplicate this and depend on head-50/tail-20 positions. Replace: fold the handoff bullets (HEAD,
ready lanes, parallel table, pending user, running agents, runbook pointer, owner line) under
`## Next Step` beneath the one-line action; delete the `NEXT` bullet; keep `HANDOFF-<date>.md`.
Rewrite-in-place then applies to `task_plan.md` only, which restores `progress.md` append-only.

**`fork` SessionStart gap.** `W/hooks/hooks.json:4` matcher is `startup|resume|clear|compact`; the hook
script itself ignores `source` (a `source=fork` payload piped to `claude-hook.sh session-start`
returned 5,733 B). A fork starts with the full prior transcript (X3 §4), so only first-turn
re-injection is lost: low severity. Fix upstream with a one-line matcher PR (and the translated
copies); no local workaround, because a project hook would have to hard-code the plugin cache path.
The doctor SessionStart (`w0-doctor/.claude/settings.json:43`) already fires on `fork`.

## 3. Legacy or incorrect items to remove

| # | Location | Today | Modern replacement |
|---|---|---|---|
| 1 | `P/task_plan.md:9-23` | `## Session handoff` block, readable only via head-50 | Fold under `## Next Step` (`task_plan.md:25`); smart and legacy both inject it |
| 2 | `P/progress.md:587-599` | `- NEXT (… rewrite in place, keep last)` | Delete; `## Next Step` carries it; `.claude/rules/planning-records.md:9` append-only holds again (R4 P3-9) |
| 3 | `P/task_plan.md:84-120` | Phase 4 body 38 lines, injected whole under smart | Keep the in_progress phase ≤ 15 lines: ticked items go to a dated `progress.md` entry; exactly one `**Status:** in_progress` |
| 4 | `P/ledger-w0-docs.jsonl:1-2` | hand-written `{"ts","unit","event","detail"}` | Not the `ledger-append.sh` schema (`tick/agent/phase/event/summary/files`, `ledger-append.sh:30-32`); `ledger-summary.sh` cannot read it. Re-append through the script |
| 5 | parent `cat >> progress.md` (R4: 18× in the prior session; none in repo scripts) | lane progress typed into the parent's file | lanes: `ledger-append.sh --agent <unit>`; parent: `plan:log` (CT-15) writing one short entry |
| 6 | `.claude/worktrees/{a06-unit3,c1-catalog-promotion,codex-session-history,nav,retro-gate,rf-env-scrub,team,w0-docs,w0-decisions}/.planning/<id>/task_plan.md` | stale copies, 536-876 lines vs root 907; 7 without a handoff block | `git worktree remove` integrated lanes (CT-17 lifecycle); live lanes (`gate-hooks`, `w0-doctor`) are harmless once pins are set |
| 7 | `.claude/settings.local.json` | no `env` | add `PWF_PLAN_ROOT`, `PWF_TRUSTED_PYTHON` (per user; `.claude/AGENTS.md` keeps it uncommitted) |
| 8 | `P/.mode` | absent | `inject-smart` (committed) |
| 9 | `docs/agents/claude-team.md:117` | "refresh the handoff block at the head of task_plan.md" | "refresh `## Next Step`" |
| 10 | `.claude/skills/ticket-frontier/SKILL.md:79` (+ `.agents/skills/` mirror) | "write the handoff block by hand" | "rewrite `## Next Step`; lanes have appended their ledgers" |
| 11 | `.planning/AGENTS.md:6-7`, `.claude/rules/planning-records.md:9,11` | "a lane proposes edits in its handoff"; no archive, no ledger rule | add: lane reports through `ledger-<unit>.jsonl` (owned path); dated `progress-archive-*.md` is admitted (one already exists, `P/progress-archive-2026-10-13.md`) |
| 12 | memory `planning-with-files-injection.md:16-19` | "handoff inside the first 30 lines", "NEXT bullet last" | rewrite after migration: `.mode inject-smart`, `## Next Step` holds the handoff, pins in `settings.local.json` (user memory: parent proposes the text) |
| 13 | X3 §2 item 2 / CT-29 `S.injection-window` | asserts handoff heading inside 50 lines and Next Step inside 30 | assert the smart frame contains `## Next Step` and one `### Phase … in_progress` body ≤ 15 lines; position is irrelevant |
| 14 | `P/task_plan.md:3-7` pin prose | tells agents to set pins, no literal recipe | keep one line pointing at `settings.local.json` and `session:start`; the R4 §Worktrees recipe goes into the lane brief template (parent hunk, `.claude/agents/*.md`) |

Not legacy, keep: `lanes/*.json`, `retros/*.md`, `ticket-ledger.md`, `decisions.jsonl` (CT-24),
`findings.md` as the pointer-only research file, the repo's three gate hooks, `autoCompactWindow`.

## 4. Migration checklist (one lane) and ticket CT-30

Ordered; each step names its check. Steps 1 and 9 are user/parent actions, not lane edits.

1. **Pin the host** (user): `settings.local.json` `env` += `PWF_PLAN_ROOT=<abs root>`,
   `PWF_TRUSTED_PYTHON=$(command -v python3)`; restart the session. Check from
   `.claude/worktrees/w0-doctor`: `python3 -I W/scripts/inject-plan.py --context=pretool | sed -n 2p`
   shows the root nonce; `sh W/scripts/plan-doctor.sh` → `PASS resolver`, `PASS injection`.
2. **Write `P/.mode`** containing `inject-smart`. Check with `PWF_INJECT` unset:
   `python3 -I W/scripts/inject-plan.py --context=userprompt | grep -c '^phases:'` = 1.
3. **Reshape the plan head**: move the handoff bullets under `## Next Step`; delete
   `## Session handoff`; trim Phase 4 to ≤ 15 lines. Check: plan frame `bytes=` ≤ 2,500 in both
   `--context=userprompt` and `--context=pretool`; the frame contains `## Next Step`, the owner line
   and `phases: 3/8 complete`; `sh W/scripts/check-complete.sh` → `Task in progress`; `/status`.
4. **Drop the `NEXT` bullet** with one dated `progress.md` entry recording the move. Check:
   `grep -c '^- NEXT' P/progress.md` = 0; the progress frame starts at an entry boundary.
5. **Ledgers**: re-append `ledger-w0-docs.jsonl` through `sh W/scripts/ledger-append.sh … --agent w0-docs`
   (two entries, `note`/`progress`); add `ledger-<unit>.jsonl` to every new lane's `owned_paths` and the
   recipe to the brief template (parent hunk). Check: `sh W/scripts/ledger-summary.sh P` prints
   `agent w0-docs:` and no `P/.ledger_lock` remains.
6. **Rules and docs** (items 9-11, 13-14). Check: `./dev/mise tasks validate`, `./dev/mise run check`,
   `check:acceptance-baseline`, `git diff --check`, skill mirror byte-identical, `retro:gate -- ct30`.
7. **Prove the `/clear` path without clearing**:
   `printf '{"session_id":"probe-%s","cwd":"%s","hook_event_name":"SessionStart","source":"clear"}' "$(date +%s)" "$PWD" | sh W/hooks/claude-hook.sh session-start | python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"])'`;
   read it as the next session would; record bytes and nonces in `findings.md` as the receipt.
8. **Remove integrated worktrees** (item 6) under the lane-lifecycle rule; check `git worktree list`.
9. **Upstream** (user's word, outward-facing): issue/PR adding `fork` to `hooks/hooks.json:4`.

**CT-30 "pwf modernisation"** (ticket text):
Adopt the planning-with-files 3.24.0 modern configuration: `P/.mode` = `inject-smart`; handoff
folded into `## Next Step`; `NEXT` bullet retired; Phase bodies bounded; per-lane ledgers written
through `ledger-append.sh` (fix `ledger-w0-docs.jsonl`); rules/docs updated (items 9-11, 13-14);
`/clear`-path receipt. Acceptance: checks in steps 2-7 pass; smart plan frame ≤ 2,500 B in both views;
`plan-doctor` PASS/PASS; `retro:gate -- ct30` rc 0.
`owned_paths`: `P/task_plan.md`, `P/progress.md`, `P/findings.md`, `P/.mode`, `P/ledger-w0-docs.jsonl`,
`.claude/rules/planning-records.md`, `.planning/AGENTS.md`, `docs/agents/claude-team.md` (line 117
only), `.claude/skills/ticket-frontier/SKILL.md:79` + `.agents/skills/ticket-frontier/SKILL.md`,
`P/retros/ct30.md`. **Not** `.claude/settings.json` (w0-session-hooks owns two entries there; CT-30
needs none) and not `settings.local.json` (user-owned, step 1). Excluded: `.claude/agents/*.md`
(proposed as parent hunks). Writer: the parent or a doc-writer with these shared files explicitly
allocated; serialize with any other parent edit (no CT-11 lock yet). `blocked-by`: none hard;
sequence: after w0-doctor integration (so step 1's probe can also run the doctor), before CT-29
(whose `S.injection-window` check must assert the new shape; make CT-29 `blocked-by: CT-30`),
never concurrent with w0-session-hooks on `.claude/settings.json`. Size: 1 (small), one lane.

## 5. Research-route log

| Route | Attempted | Result |
|---|---|---|
| 1 Local cache 3.24.0 | `CHANGELOG.md` (3.0-3.24 index + keyword scan), `README.md` (multi-agent, env table, safeguards), `SKILL.md` whole, `docs/{workflow,quickstart,long-running-agent-tasks,agent-forgets-plan-after-clear,claude-code-lost-context-after-compaction,attestation-locking,troubleshooting}.md`, `commands/{plan-doctor,status,plan-attest,plan-goal,plan-loop}.md`, `hooks/hooks.json`, `hooks/claude-hook.sh`, `scripts/{inject-plan.sh,ledger-append.sh,ledger-summary.sh,plan-doctor.sh}`, templates | Primary source for §1-§3; probes ran `inject-plan.py`, `claude-hook.sh`, `plan-doctor.sh` |
| 2 Upstream GitHub | `releases?per_page=10`, raw `CHANGELOG.md`, `compare/v3.24.0...master`, repo metadata, issue searches | latest = v3.24.0 (2026-10-10); master +2 docs commits; `homepage` `https://gilded-laurel-c7nj.here.now/`, `has_pages: false` |
| 3 Context7 | direct API via fnox profile (`/othmanadi/planning-with-files`, 897 snippets, indexed 2026-09-03) and the fanout `context7` source (5 items) | Index is pre-3.21 (2026-09-03); confirms `PWF_PLAN_ROOT` and hook commands only; no newer facts than the cache |
| 4 Exa / Firecrawl / Last30Days via `fnox … --profile codex_research … exec --` | Exa direct (8 hits, 2026-09/10, all third-party mirrors and blogs); Firecrawl direct scrape: **HTTP 402 "Insufficient credits"**; `mise -C ~/dev/github/ray-manaloto/dotfiles run research-fanout` (`--list-sources`, then one bounded run, request-id `y1-pwf-2026-10-14`, manifest in the scratchpad `fanout/`): exa ok 5, context7 ok 5, firecrawl-developer ok 5 (issues #210 caching-determinism of smart view, #312, #237), firecrawl-search provisional via serper (credits exhausted), github-* `empty_verified`; `--strict-five`/Last30Days plan not run (no hook receipt needed) | No source contradicts the cache. Gaps: Firecrawl quota; Last30Days not executed (its CLI printed usage for `--sources`; no plan file supplied) |
| 5 Docs site | `curl` of the homepage (HTTP 200, 15.5 KB) | Landing page cites v3.22.0 only; mentions "worktree" and "smart" as words; no reference content beyond the README |

## 6. Could not verify

- Whether a settings `env` value reaches hook subprocesses is inferred (`PLAN_ID` visible in tool
  env; frames show the root plan), not proven by a captured hook payload; step 1's probe proves it.
- Whether 3.24.0 suppression holds for subagent hooks (R4 P2-4, `prompt_id` keying): my probe used a
  bare `PWF_SESSION_ID`, where suppression worked; the host payload path was not captured.
- Hook-run cost of the smart view after reshaping (estimated 1.5-2.5 KB from R4's fixture, 1,098 B).
- Last30Days and Firecrawl content (quota and invocation gaps above); Context7's index is 5 weeks old.
- Upstream intent on a `fork` matcher: no issue exists; not asked.
