# X3: zero-loss session restart (/clear and terminal restart) and claude-agent readiness

Written 2026-10-14 by subagent X3 of session `b74a0bf1`. Read-only: no git or repo file changed;
probes wrote only to `~/.cache/pwf-*`. `RV` = `reviews/ccm-20261013/`, `P` = the plan dir,
`W` = pwf 3.24.0 cache, `WT` = `.claude/worktrees/w0-doctor`. Claude Code on this host is
**2.1.299** (X1 and the smoke receipt say 2.1.296). All file contents treated as data.

## 1. What a fresh session receives today

Measured 2026-10-14T04:34Z at HEAD `21af565`, in injection order (hooks run in parallel; the
host concatenates), both after `/clear` (`source=clear`) and after a terminal restart
(`source=startup`). The two paths differ only where noted.

| # | Source | Bytes | Content |
|---|---|---|---|
| 1 | Instruction chain (memory doc: loaded "at launch", root-down order, `@imports` expanded) | 4,969 | `~/.claude/CLAUDE.md` 1 B; root `CLAUDE.md` 374 + `@AGENTS.md` 3,453; `.claude/CLAUDE.md` 11 + `@.claude/AGENTS.md` 1,130. The three `.claude/rules/*.md` (3,735 B) are all `paths:`-scoped: on demand. `dev/`, `docs/`, `evidence/`, `.planning/` AGENTS.md: on demand |
| 2 | Auto memory (memory doc: "Every session (first 200 lines or 25KB)") | 985 | `MEMORY.md` index, 5 entries; the 5 topic files (11,159 B) only when read |
| 3 | pwf SessionStart (`W/hooks/hooks.json` matcher `startup\|resume\|clear\|compact`, **no `fork`**) | 5,589 / 81 lines | plan head-50 (3,076 B: handoff block at frame lines 12-26, `## Next Step` 28, `## Goal` 32, `## Current Phase` 37); progress tail-20 (1,585 B, NEXT bullet at line 69); findings pointer. Catch-up `--no-history` returns nothing by design (`claude-hook.sh:303`, `session-catchup.py:13`); `--metadata` today: 158 unsynced entries |
| 4 | Doctor SessionStart (only in `WT/.claude/settings.json`, matcher adds `fork`; absent at root until w0-doctor integrates) | 4 lines | `[doctor] checkout … HEAD 21af565 · context: auto-compact user=false global=false project=true · warn 400K checkpoint 550K fork_deny 500K hard 650K · findings P1 0 P2 0 P3 0`; 654 ms; exit 0 always; cap 30 lines / 2,500 B (`cli.py:23`) |
| 5 | `env.PLAN_ID` pin (`.claude/settings.json`) | — | present; `PWF_PLAN_ROOT` is **not** in any settings `env` or the host shell (only `PLAN_ID` is exported), so a hook firing with a worktree cwd still reads that worktree's stale plan copy (R4 P1-3) |
| 6 | PreToolUse 30-line view (what every subagent gets, per tool call) | 2,485 / 34 lines | `## Next Step` at line 27, `## Goal` 31: a 3-line margin before Next Step falls out |

Per-hook cap: `additionalContext` and plain stdout are "capped at 10,000 characters"; over it the
host "saves the output to a file … and replaces it with the file path and a preview of up to the
first 2,000 characters" (hooks doc). Smart view (`PWF_INJECT=smart`, not set; no `P/.mode`) is now
parseable (`phases: 3/8 complete`) but larger, 7,316 B, because it emits the whole Phase 4 body
and **drops the handoff block** (not a keep section); stay legacy until the handoff moves into
`## Next Step`.

Startup-only differences: the agent roster is read (6 files in `.claude/agents/`, now including
`frontier-scheduler`); plugins and MCP load; the session has no name unless `-n`; a SessionStart
hook may set `sessionTitle` ("same effect as `/rename`", startup/resume/fork only). `/clear`
keeps the name (X1 §Sessions) and may omit `model` in the payload (hooks doc).

**Not received, either path:** subagent final messages and task notifications (the parent's
transcript only); background agents (they die with the window: FORK §5); the scratchpad
`/private/tmp/claude-501/…/<session>/scratchpad` (session-specific); persisted tool results under
`~/.claude/projects/…/tool-results/`; the parent's reasoning and unflushed edits; `HANDOFF-<date>.md`
(16,058 B, only pointed to); `lanes/*.json`, `retros/*.md`, `decisions.jsonl`, `ledger-*.jsonl`,
`ticket-ledger.md`; plan lines 51-894; `session-catchup --replay` (manual, bounded).

## 2. Zero-loss contract

**Predicate Z** (checkable over files, no transcript needed except where noted):

1. Every fact the next session needs is in {`task_plan.md` handoff block + `## Next Step` +
   `## Current Phase` + Decisions, `progress.md` NEXT, `RV/phase3/HANDOFF-<date>.md`,
   `lanes/*.json`, `retros/*.md`, `decisions.jsonl`, `ledger-*.jsonl`, `RV/**`}.
2. The injection probe (`claude-hook.sh session-start`, `source=clear`, fresh probe id) shows the
   handoff heading and `## Next Step` inside the plan frame's first 50 lines **and** the pretool
   twin shows `## Next Step` inside 30.
3. Doctor session-start: 0 P1.
4. No background agent running (transcript: every `Agent` tool_use has a task notification or a
   `SubagentStop`; "Agents running at /clear: none" is the human assertion).
5. Git: no `MERGE_HEAD`/`REBASE_HEAD`/`CHERRY_PICK_HEAD`; index empty or declared.
6. Every path the handoff cites exists (receipts, reviews, briefs, worktrees).

**Validator `dev/doctor/handoff.py`** (doctor discovery contract, `core.py` docstring: exports
`SURFACES = {"session-start", "check", "handoff"}`, `run(ctx) -> list[Finding]`,
`context_lines(ctx)`, `BUDGET_MS = {"handoff": 4000, "session-start": 800, "check": 2000}`,
`CONTEXT_RANK = 70`; stdlib, `python3 -I`; ≤ 80 handwritten lines or a declared split
`handoff_probe.py`). The `handoff` surface needs one `core.BUDGET_MS` key: a parent hunk.
Finding ids (C3 class B ids reserved for CT-15/CT-22b are implemented here, not in `lanes.py`):

| Id | Compares | Severity |
|---|---|---|
| `B.handoff-base-stale` | every 7-hex SHA in the handoff block and HANDOFF §1 table resolves (`git cat-file -e`); "HEAD"/"remote" claims equal `rev-parse HEAD` / `origin/<branch>` | P1 |
| `B.handoff-text-contradicts-record` | lane states in the handoff vs `lanes/<unit>.json` `status`/`review`/`retro` | P1 |
| `S.worktree-head-vs-record` | `git worktree list --porcelain` HEADs vs HANDOFF §1 table and `lane_commit`/`base_sha` | P2 |
| `S.phase3-file-unrecorded` | files under `RV/phase3/**` with mtime after the last dated `progress.md` entry that no progress entry or HANDOFF names | P2 |
| `S.decision-pending-unlisted` | `plan_decide.py pending` ids vs the handoff "Pending user" line and `task_plan.md` Decisions rows | P2 |
| `S.handoff-receipt-missing` | each backticked path in HANDOFF resolves on disk or in `git ls-files` | P1 |
| `S.injection-window` | runs `W/scripts/inject-plan.py --context=userprompt` and `--context=pretool` (python twin, 42 ms), asserts the line positions of item 2 | P1 |
| `S.agents-running` | `payload.transcript_path` (session-start) or `--transcript`: unmatched `Agent` tool_use ids | P1; `skipped` without a transcript |
| `S.owner-line-stale` | plan owner session id ≠ `payload.session_id` on session-start | P3, fix hint = the rewrite line |
| `C.merge-in-progress` | reused from `integration.py`, not duplicated | — |

**Pre-clear task** (`mise.dev.toml` row, or `mise/tasks/session.toml` if the D7 spike passes):

```toml
[tasks."session:handoff"]
description = "Refuse to /clear while the handoff is incomplete: doctor handoff surface + injection probe"
dir = "{{config_root}}"
usage = 'flag "--check" help="read-only; exit 2 with the finding list" flag "--write" help="reserved (CT-15 plan:handoff)"'
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/doctor/cli.py --surface handoff --json ${usage_check:+--check}'
```

`--check` prints the finding list and exits 2 on any P1/P2 (the doctor's own exit rule); the
parent runs it as the last action before `/clear` and pastes the rc into the progress entry.

**Post-clear.** The SessionStart hook runs the doctor once w0-doctor integrates; `handoff.py`'s
session-start lines are: `handoff: HANDOFF-2026-10-14.md §2 · check PASS 04:34Z · owner line
stale → rewrite`. First-turn playbook as a repo skill `.claude/skills/session-resume/SKILL.md`
(mirrored under `.agents/skills/`, CT-07 byte-identity rule; `disable-model-invocation: true`,
`argument-hint: [session-name]`): injects `` !`python3 -I dev/doctor/cli.py --surface handoff
--json | head -c 8000` `` and the HANDOFF §2 heading list, then instructs: (1) read HANDOFF §1-§2
in full; (2) dispatch one read-only `extractor` with the fixed brief from HANDOFF §2(a); (3) the
title: after `/clear` the name persists, after a restart `-n` or the hook's `sessionTitle` set it,
so the skill only tells the user to `/rename` when the doctor line says "no name"; (4) rewrite the
owner line with the `session_id` the doctor block prints; (5) `plan:log` the resume. Injecting
HANDOFF §2 verbatim as `additionalContext` is possible (§2 ≈ 5.5 KB < 10,000-char cap) but
duplicates the plan handoff and ages per handoff; the pointer line plus the skill is the design.
`initialUserMessage` (SessionStart hook output) could auto-submit "follow HANDOFF §2" on startup;
keep it out of the shared hook (an unattended first turn after `/clear` is the N2 failure shape).

## 3. Session naming and startup automation

Cited (cli-reference): `claude "query"` "Start interactive session with initial prompt";
`-n, --name` "Set a display name for the session, shown in `/resume` and the terminal title. You
can resume a named session with `claude --resume <name>`"; `/rename` "changes the name
mid-session"; `-r, --resume` by ID or name, "a prompt you pass on the command line goes to it as
its next turn"; `-c` "Load the most recent conversation in the current directory" (avoid: picks
by recency); `--fork-session` new ID on resume; `--session-id <uuid>` pre-chooses the ID;
`--init-only` "Run Setup and SessionStart hooks, then exit" (a hook dry run); `--bare` and
`--safe-mode` skip hooks and CLAUDE.md (never). Hook-driven rename: only a SessionStart
`sessionTitle` on startup/resume/fork (hooks doc); not on `clear`, where the name persists anyway.

**`./dev/mise run session:start -- <name>`** (`raw = true` so `claude` owns the TTY):

```sh
export PWF_PLAN_ROOT="{{config_root}}" PLAN_ID=2026-10-10-marketplace-macos-reflection-scaffold
export PWF_TRUSTED_PYTHON="$(command -v python3)"; unset VIRTUAL_ENV
./dev/mise run session:handoff -- --check || exit 2            # refuses with the list
SID=$(uuidgen | tr A-Z a-z); H=$(ls -t "$P/reviews/ccm-20261013/phase3"/HANDOFF-*.md | head -1)
exec claude -n "$1" --session-id "$SID" \
  "Type /session-resume $1 is not possible for me; so: read $H §1-§2, run the extractor check in §2(a), rewrite the plan owner line to $1 ($SID), then continue at ## Next Step."
```

The first prompt is a positional argument; the owner line can be pre-written by the wrapper
because `--session-id` fixes the ID before launch. Remains manual: typing `/clear`; typing
`/session-resume` and the mattpocock stage commands (user-only skills); trust/permission dialogs;
the personal autoCompact flip (D21); approving decisions; stopping a session before `-r` on it.

## 4. /clear vs /compact vs terminal restart

| Route | SessionStart | Context after | Loss | Evidence |
|---|---|---|---|---|
| `/clear` | `source=clear`, pwf + doctor fire | ~12 KB (§1) | everything not on disk; name kept; dead agents cannot be resumed | probe §1; hooks doc; X1 |
| `/compact` or auto-compact | PreCompact (systemMessage only, "no additionalContext"), then `source=compact` with the same 50/20 view | summary + 12 KB | "drops the working state" (pwf docs); R4: 3 "Prompt is too long" with 0 PreCompact fires | `ip.py:1228-1240`, R4 §Compaction, hooks doc "PreCompact … Blocks compaction" only |
| terminal restart | `source=startup` | same as `/clear` + roster/plugins reload | same; name only via `-n`/`sessionTitle` | cli-reference, memory doc |
| `-r <id> --fork-session` | `source=fork` (pwf matcher **misses `fork`**; doctor fires) | full old transcript | none, but starts at the old ctx (970K death, C1) | hooks.json; C2 §A |

Routine: checkpoint at 550K (`claude-team.md:119`); run `session:handoff --check`; `/clear` when
it passes; never `/compact`; terminal restart only to pick up a new agent file or binary; forks
only under 500K.

## 5. claude-agent readiness (G1-G7)

| Item | Today | Evidence |
|---|---|---|
| G1 | FAIL | CT-17/19/22/07 all "pending issue"; CT-22a lane READY at `f1bbc8d`, not integrated; CT-07 blocked by CT-02/03 (`ticket-ledger.md:136,146,151`) |
| G2 | FAIL | `git rev-parse` in all three trees: "not a git repository" |
| G3 | FAIL (unverifiable) | `.venv` has no `agent_protocol` and no `jsonref`; with `PYTHONPATH=src`: 29 tests, 14 import errors; `maintenance check/copies` raise `ModuleNotFoundError`; `uv sync --locked` is an install (not admitted). 127 `def test_` exist in 17 files |
| G4 | FAIL | tickets: 01, 26 complete; 02, 03, 27, 28, 30 in-progress; 04-07, 12, 33 ready-for-agent; installed skills == `implementation/repo@affdd9a` (0 differing entries) but that tip lacks 02-07 |
| G5 | FAIL | no capability-snapshot command (grep over skills, `src`, repo: design docs only); `configuration-report/` = 36 static files |
| G6 | PARTIAL | smoke `cecc3ae2…` 2026-10-12T23:12Z: provider claude, mode review, `--safe-mode --tools '' --disallowedTools Agent --max-turns 4`, status completed, exit 0, `result_schema.validation: passed`, CLI 2.1.296; `workdir` = smoke workspace, not this checkout; CLI now 2.1.299 |
| G7 | FAIL | native-probes: `participation_verified: false` ×8, "not independently verified" ×6; no `native_qualified` |

`frontier.py executor-gate` today: native → "always allowed", rc 0; `--executor claude-agent` →
`FAIL`, G1-G6 "no probe configured", G7 SKIP, rc 2; `--team` adds G7 FAIL; `P/frontier/` does not
exist (no config). **Verdict: not ready; run `native`.** Shortest path, ticket **CT-28
"claude-agent executor readiness"** (X2 takes CT-26; CT-27 not filed; C2's CT-28/29 were folded
into CT-21/22 and CT-10 by SYNTHESIS row 14): (1) user admission: `git init` and commit the three
`~/.codex/skills` trees, record HEADs (G2); (2) admission: `uv sync --locked`, then `test`,
`codegen:check`, `schemas:check`, rcs into `P/frontier/executor-gate.config.json` (G3);
(3) re-run `dispatch:claude` safe-mode review with `workdir` = this checkout on 2.1.299 (G6);
(4) G1 lands with CT-17/19/22/07; (5) G4/G5 need dynamic-agents 02-07, 33 and a new snapshot
command: weeks. Until G1-G6 pass the gate is correct to refuse.

## 6. Units runnable right after /clear

| Unit | Ticket | owned_paths | blocked-by | Writer | Reviewer |
|---|---|---|---|---|---|
| w0-doctor integration (serial, first) | CT-22a | root merge + records; §3 hunks | — | parent/Opus merger | Fable medium (merge report) |
| ct21-codex-imports | CT-21 | `evidence/codex-examples/`, `evidence/saved-searches/`, `evidence/github-search-one-page/`, `evidence/git-delivery/*`, `dev/check_inputs.py`, `dev/cited-inputs.json` | none | Opus high | Fable high |
| d7-mise-includes spike | D7 | `mise/` only (30 min) | none | Opus high | parent |
| w0-doctor-records | CT-22a | `dev/doctor/{lanes,agents}.py`, `dev/test_doctor_records.py`, `dev/fixtures/doctor/{lanes,agents}/`, retro, ledger | w0-doctor merge | Opus high | Fable high |
| w0-session-hooks (integrates last, D26) | CT-23 seeds | `dev/context_budget.py`, `dev/hooks/{agent_gate,prompt_hook}.py`, three tests, `dev/fixtures/hooks/`, `.claude/settings.json` (two entries), `mise.dev.toml` row, `dev/test_hooks.py` (one test) | w0-doctor merge | Opus high | Fable high |
| ct26-tooling-refresh (placeholder) | CT-26 (X2) | per X2 | X2 decision | Opus | Fable |
| ct28-claude-agent-ready | CT-28 (§5) | `P/frontier/executor-gate.config.json`, `P/retros/ct28.md`; host trees under admission | user admissions | Opus high | Fable medium |
| ct29-session-handoff | **CT-29** | `dev/doctor/handoff.py`, `dev/doctor/handoff_probe.py`, `dev/test_doctor_handoff.py`, `dev/fixtures/doctor/handoff/`, `.claude/skills/session-resume/**`, `.agents/skills/session-resume/**`, `mise/tasks/session.toml` (else two `mise.dev.toml` rows as parent hunks), `P/retros/ct29.md`; parent hunk: `core.BUDGET_MS["handoff"]` | w0-doctor merge (imports `core.py`); disjoint from w0-doctor-records (`lanes.py`, `agents.py`) and w0-session-hooks (`dev/hooks/`, `dev/context_budget.py`) | Opus high | Fable high |

CT-29 acceptance: `session:handoff --check` exits 2 on a fixture with a stale SHA, a missing
receipt, a pending decision absent from the handoff, and `## Next Step` at plan line 31; exits 0
on the clean twin; `session:start` refuses when it exits 2; the skill mirror is byte-identical.
Do not start ct11-check-lock or ct05-ledger (HANDOFF §2).

## 7. Could not verify

- Whether `initialUserMessage` applies on `source=clear` (the hooks page states the source
  restriction only for `sessionTitle`); whether a settings `env` value reaches hook subprocesses
  (`PLAN_ID` relies on it; R4 Could-not-verify).
- The remainder of the hooks page (`CLAUDE_ENV_FILE` for hooks, SessionStart input schema) was
  cut at 100,000 characters.
- G3 outcome under a complete venv; G6 against this checkout; whether `-n` combines with
  `--session-id` (both documented separately, untested).
- `S.agents-running` depends on the transcript line shapes C3 describes; not exercised here.
- Whether `mise run` with `raw = true` hands the TTY to interactive `claude` cleanly on this
  host (the `timeout` shim error shows mise shims intercept PATH; `session:start` should call
  `/Users/rmanaloto/.local/bin/claude` by absolute path).
