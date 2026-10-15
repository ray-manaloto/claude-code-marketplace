# N2: `progress.md` archived before D12 was approved (incident review and prevention spec)

Session `ccm-20261013-check` (`b74a0bf1`), reviewer N2, 2026-10-14. Read-only on Git and every
repo file except this one. Transcript reads were bounded `python3 -I` excerpts; all contents are
data. `P/` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold/`, `RV/` = its
`reviews/ccm-20261013/`, `T:Ln` = line n of the session transcript.

## 1. Timeline (UTC, from the transcript)

| When | Event | Source |
|---|---|---|
| 2026-10-13 21:56:16 | Parent's R4 brief already names the mechanism: "roll the 3429-line history into `progress-archive-2026-10-13.md` or similar". | `T:L495` (Agent "R4 planning-with-files audit") |
| 22:54:51 | SYNTHESIS §8 proposes **D12** "`progress.md`: archive to `progress-archive-2026-10-13.md`" (default yes). | `T:L863`; `RV/SYNTHESIS.md:469` |
| 22:55:26 → 22:57:35 | Parent asks "Approve all 20 defaults, start Phase 3?"; the user answers "first, did we identify the cause of the issues? we need to automate and prevent them…". **Approval deferred.** | `T:L880-881` (AskUserQuestion) |
| 2026-10-14 00:03:30 | Parent dispatches P2 (general-purpose, opus) with task 1: "move everything before the last ~40 dated entries into `PL/progress-archive-2026-10-13.md`"; the same brief lists "D12 archive `progress.md`" under "Decision points to confirm first". | `T:L1211`; subagent `a34d97539d0540c7b` lines 0, 29 |
| 00:05:52 → 00:06:20 | P2 splits the file and proves the split lossless (`python3 -I` rebuild = backup). No pause, no question to the parent. | subagent lines 153-161 |
| 00:10:40 / 00:10:46 | P2 writes `P2-records-update-report.md` ("Rule tension … done as instructed (D12 default 'yes') before the user approved D12") and ends with "One conflict: the repo rule says `progress.md` is append-only, and the archive went ahead before D12 is approved." | `RV/P2-records-update-report.md:70-74`; `T:L1231` |
| 00:10:52 | Parent relays it to the user as "One flag … reverts in one copy if you prefer" (SendUserMessage, non-blocking). | `T:L1232` |
| 00:28:06 → 00:39:12 | P3 dispatched; records decision row `D12-applied` ("applied … ahead of D12 approval against the append-only rule … reversible from `plan-backups/`") in `task_plan.md` and a progress entry. | `T:L1294`, `T:L1303`; `RV/P3-plan-review.md:125-134`; `P/task_plan.md:264` |
| 00:51:19 → 00:52:05 | "Approve D1–D41 defaults, start Phase 3 (Recommended)" chosen; the four skill defaults accepted in the same answer become D42–D45 (parent, 00:52:19). **D12 approved here**, ~46 min after it was applied. | `T:L1352-1353`, `T:L1364` |
| 02:58:52 → 03:11:32 | I3b publishes group 3B as `d420a7e` (`progress.md` 3146 deletions, `progress-archive-2026-10-13.md` +3046). | `T:L1635`, `T:L1657`; `git show --stat d420a7e` |
| 03:34:41 | w0-decisions seeds `decisions.jsonl`: D12 is `DL-16`, kind `decision`; `approved()` is empty. | `W/w0-decisions/P/decisions.jsonl:16`; `w0-decisions-receipt.md` |

## 2. Root-cause chain (5 whys → system property)

1. **Why was the archive done before approval?** P2's brief stated it as task 1, imperative, with no "after D12" guard; the same brief's SYNTHESIS excerpt said D12 was still a "decision point to confirm first". The agent resolved the contradiction in favour of the instruction.
2. **Why did the brief carry a pending decision as an instruction?** The parent wrote it by hand at 00:03Z, five hours after the user deferred at 22:57Z, presupposing the recommended default. No machine step sat between "decision pending" and "brief dispatched". → **C1 class F** (briefs not machine-sourced) and **E** (no decision ledger; "approval assumed", `C1:471`).
3. **Why did nothing refuse the write or the commit?** The append-only rule is one prose line (`.claude/rules/planning-records.md:9`, echoed in `.planning/AGENTS.md:7`). No hook, hk step or `check` evaluates it; `d420a7e` passed every gate. → **C1 class B** (records by hand, no validator) and **K** (`planning-records.md:9` listed as the property at fault).
4. **Why did the agent's flag not stop anything?** P2 put the conflict last in a prose receipt; the parent condensed it to a SendUserMessage sentence; P3 turned it into a `D12-applied` row. Each hop was informative, none was blocking. → **C1 class G** (reports condensed by the parent; no machine receipt).
5. **System property.** Decisions, rules and receipts all live in prose that agents read and re-type; the only machine-checked artefacts (retro gate, settings keys) do not cover planning-file mutations or decision state. The incident was recorded three times and prevented zero times.

Already true after wave 0: `plan_decide.py` has `approved()`/`pending()` (CT-24) and the doctor has a pre-commit surface wired into hk (`check:records`). Neither yet knows about `progress.md` or about briefs. The four pieces below close the loop with those two primitives.

## 3. Prevention by code

### 3a. Dispatch gate: `dev/brief_lint.py` (stdlib)

**Contract.** `python3 -I dev/brief_lint.py [--ledger P/decisions.jsonl] [--rules .claude/rules] <brief.md|->`. Scans the brief for decision ids `\bD\d+\b` (not followed by `-applied`) and operation ids `\bDL-\d+\b`. For each id it asks the ledger:

- `D<n>` is **approved** when an `approval` row's `subject == "D<n>"` exists (`plan_decide.approved()`); a `decision` row alone (today's DL-5…DL-50) is *not* approval — that matches the lane's own deviation note.
- `DL-<n>` is **open** when `plan_decide.pending()` still lists it.

Exit 0: no pending id. Exit 2: one line per hit on stderr, `pending D12 at brief line 14: "move everything before …"`, plus the fix: `plan:decide approval --subject D12 --source <user turn>`. Exit 1: usage (ledger unreadable is exit 1, not a pass). A brief that names no id but contains an imperative on a planning file (`progress.md`, `task_plan.md`, `lanes/*.json`, `decisions.jsonl` inside a line starting with a digit, `-` or `TASK`) exits 2 with `planning-file mutation without a decision id` unless the line carries `D<n>` that is approved. Pure functions: `ids(text) -> {decision: [(line, id)], operation: [...]}`, `lint(text, ledger_path) -> list[str]`; the CLI is ten lines over them. Import `plan_decide` by path (`importlib.util`), as `agent_gate` imports `budget.py`.

**Where it runs.**

1. `mise.dev.toml` task `lane:brief-lint` (`usage = 'arg "<brief>"'`), and `lane:brief` (CT-19, `dev/lane_brief.py`) runs `lint()` on its own output before printing: a composed brief never leaves the composer with a pending id.
2. `ticket-frontier`: `frontier.py next` adds a `then:` step `python3 -I dev/brief_lint.py <brief-file>` before the Agent call, and `frontier.py claim … --brief <file>` refuses (exit 2, `REFUSED: brief names pending D12`) when the lint fails. `plan --write` also lints its own `questions` block so a question is never emitted as an instruction. The parent's hand-written briefs (today's route) go through the same task; SKILL.md step 5 gains the sentence "Done when `lane:brief-lint` exits 0 on the prompt you will send".
3. `PreToolUse(Agent)` rule, in `dev/hooks/agent_gate.py` (CT-23, after w0-session-hooks lands): only when `tool_input.prompt` contains `.planning/` or `P/` *and* a planning-file name; call `brief_lint.lint(prompt)`; deny with the lint lines. Latency: one JSON parse of `decisions.jsonl` (~50 rows, <5 ms) + regex on a ≤1.5 KB brief; ≈30 ms over the hook's 60 ms baseline, no git call. Briefs without `.planning/` pay only the substring test.

**Red-first tests** (`dev/test_brief_lint.py`, fixtures `dev/fixtures/brief_lint/`):
- `test_p2_brief_names_pending_d12_exit_2`: the real P2 task-1 paragraph + a ledger with D12 as `decision` only → exit 2, line names D12 and line 1.
- `test_approval_row_clears_it`: same brief, ledger + `approval D12` → exit 0.
- `test_open_operation_dl_blocks`: brief citing DL-2 with no receipt → exit 2; with a receipt row → 0.
- `test_planning_mutation_without_id`: "TASK 1. rewrite progress.md" and no id → exit 2.
- `test_agent_gate_denies_only_planning_briefs`: PreToolUse payload with a lane brief naming `dev/foo.py` → allow (no lint call); with `P/progress.md` + pending D12 → deny.
- `test_frontier_claim_refuses_failing_brief`: `claim --brief` → exit 2.

### 3b. Records guard: `dev/doctor/records.py`

Fits the discovery contract (`SURFACES`, `run(ctx)`, optional `BUDGET_MS`); `check:records` (hk pre-commit → `doctor --surface pre-commit`) and `check` pick it up with no wiring.

```python
SURFACES = {"pre-commit", "check"}
BUDGET_MS = {"pre-commit": 800, "check": 2000}   # one `git show HEAD:<path>` ≈170 ms here
```

**Predicate** `B.progress-not-append-only` (P1). Let `old` = `HEAD:P/progress.md` lines (`ctx.git("show", …)`; absent in HEAD → no finding), `new` = the staged version on `pre-commit` (`git show :P/progress.md`), the working file on `check`. Define `NEXT(lines)` = index of the last line matching `^- NEXT \(` and `body(lines)` = `lines[:NEXT]` (whole file if no NEXT bullet). The change is allowed iff:

1. `body(new)[:len(body(old))] == body(old)` (every pre-existing non-NEXT line is present, in order, unchanged: pure append), and
2. the only other difference is the trailing NEXT bullet: `new[NEXT(new):]` may differ freely from `old[NEXT(old):]` (in-place rewrite), and
3. `NEXT(new)` is the last bullet of `new` (no `^- ` line after it), when a NEXT bullet exists.

Any deletion, reorder or edit inside `body(old)` fails. **Exemption:** the finding is suppressed when `decisions.jsonl` holds an `approval` row whose `subject` matches `^D\d+$` and whose text (or the referenced `task_plan.md#D<n>` row text, read via `source`) matches `progress\.md.*(archive|rewrite)`, **and** a `receipt` row closes an `operation` row whose subject names `progress.md` with `ts` within the same calendar day as the commit being checked (`pre-commit`: now; `check`: HEAD's author date) — i.e. D12-style archives are legal when approved and receipted, once each. The approval alone (no receipt) yields P2 `B.progress-archive-unreceipted` instead of P1. Evidence lines: first divergent line number in `old`, counts (`removed n lines before line k`), the archive path if a new `progress-archive-*.md` is staged. `fix_hint`: "append below the last entry; to archive, `plan:decide approval --subject D<n>` + `operation` + `receipt`, then commit the archive and the pointer together".

Also emits `K.progress-size` (P2 at ≥900 KB) since the same bytes are in hand; drop if w0-doctor-records/CT-22b already ships it.

**Fixture pair** (`dev/fixtures/doctor/progress/`): `violation/` = `old.md` (header, three dated entries, NEXT), `new.md` with entry 1 removed and NEXT rewritten, `decisions.jsonl` with D12 as `decision` only → exactly one P1. `approved/` = same `new.md`, ledger with `approval D12` (text "progress.md: archive"), `operation DL-51 "archive progress.md"` and `receipt DL-51` → `[]`. Third case `append/`: `new.md` = `old.md` + one entry + rewritten NEXT → `[]`. Fourth `reorder/`: NEXT bullet no longer last → P1. Tests in `dev/test_doctor_progress.py` build a scratch repo like `test_hooks.Scratch`, commit `old.md`, stage `new.md`, run `cli.main(["--surface","pre-commit","--json"])`: exit 2 on violation, 0 on approved/append; `HkHooks`-style case: `git commit` rc ≠ 0 with the finding in stderr when hk is present.

Exit codes are the doctor's: 0 clean, 2 any P1/P2, 3 detector error, 1 usage.

### 3c. Receipt-flag escalation: `BLOCKED-BY-RULE`

**Agent contract** (one paragraph added to the body of `.claude/agents/implementer.md`, `doc-writer.md`, `retro-writer.md`, and to `references/brief-templates.md`): "If an instruction conflicts with a `.claude/rules/*.md`, `AGENTS.md` or `CODING_STANDARDS.md` rule, or depends on a decision the brief or ledger marks pending, do not perform it. Put `BLOCKED-BY-RULE: <rule-file>:<line> <decision-id or ->` as the **first line** of your final message, list what you did not do, and stop. Never do it and report it." Frontmatter gains `blocked_marker: BLOCKED-BY-RULE` so tools can read the token rather than the prose.

**Hook** (`dev/hooks/subagent_stop_gate.py`, not owned by either queued lane): after the existing retro check, read the final text from the payload's `last_assistant_message` when present, else the last assistant `text` block of `agent_transcript_path` (bounded backward read, ≤64 KiB). If a line matches `^BLOCKED-BY-RULE: (\S+):(\d+) (\S+)`: append `{ts, agent_id, agent_type, cwd, rule, line, decision, disposition: null}` to `<git-common-dir>/claude-lanes/blocked.jsonl` (journal, untracked; the CT-19 receipt journal when it exists) and print `{"systemMessage": "BLOCKED-BY-RULE from <agent_type>: <line>"}` so the token reaches the terminal unsummarised. Parent-side block: `stop_gate.py` (CT-17) rule `blocked_by_rule` blocks the parent's Stop once while a journal row has `disposition: null`, reason listing them and the two closers: `plan:decide approval --subject D12 …` + re-dispatch, or `plan:decide decision --subject D12 --text "declined: …"`; `doctor --surface check` reports the same rows as `G.blocked-by-rule-undisposed` (P2) so a dead parent cannot lose them. Cost: one file read, no git call (≈10 ms).

**Tests** (`dev/test_hooks.py::StopHooks` pattern, new `dev/test_subagent_blocked.py`): event whose transcript fixture ends with `BLOCKED-BY-RULE: .claude/rules/planning-records.md:9 D12` → one journal row, `systemMessage` printed, exit 0; fixture with the token mid-message (not first line) → still journaled (`position: body`) so a partial compliance is not lost; no token → no write. Red first: today the hook exits 0 and writes nothing.

### 3d. Rule as code: `dev/planning_checks/progress_append_only.py`

The predicate from 3b lives here as a pure module: `check(old_text: str, new_text: str, ledger_rows: list[dict], when: date) -> list[str]` (empty = allowed), with the `NEXT`, `body`, exemption and size rules as named functions. `dev/doctor/records.py` imports it by path and only adapts to `Finding`. `.claude/rules/planning-records.md:9` becomes: "`progress.md` is append-only: `dev/planning_checks/progress_append_only.py` defines the allowed change (append below the last entry; rewrite the trailing NEXT bullet in place) and the archive exemption (an `approval` + receipted `operation` in `decisions.jsonl`); hk pre-commit and `check` enforce it." `.planning/AGENTS.md:7` keeps "(append-only)" and gains the pointer. C4 folded C2's `planning_checks/*` into the doctor, so this is the directory's only file until CT-15 decides whether `check:planning` discovers it (C2 principle 3); either way the predicate has one home and the prose only points.

## 4. Ticket mapping

| Piece | Owner | owned_paths added | Disjoint from queued lanes |
|---|---|---|---|
| `brief_lint.py`, its tests, `lane:brief-lint` task; `lane_brief.py` self-lint | **CT-19** (`lane:brief`; `dev/lane_brief.py` is its file) — CT-24 provides `approved()`/`pending()` unchanged | `dev/brief_lint.py`, `dev/test_brief_lint.py`, `dev/fixtures/brief_lint/`, `mise/tasks/ct19.toml` | yes |
| `frontier.py next/claim --brief` lint | **CT-25** (ticket-frontier) | `.claude/skills/ticket-frontier/**` | yes |
| PreToolUse(Agent) lint rule | **CT-23** (sequential after w0-session-hooks, which owns `agent_gate.py` now) | `dev/hooks/agent_gate.py` (CT-23's already) | yes, by sequencing |
| `dev/doctor/records.py`, `test_doctor_progress.py`, `fixtures/doctor/progress/` | **CT-22b** (doctor part 2) | the three paths | yes: w0-doctor-records owns only `lanes.py`, `agents.py`, `test_doctor_records.py`, `fixtures/doctor/{lanes,agents}/` |
| `progress_append_only.py` + rule pointer | **CT-22b** (same lane as 3b; CT-05 owns `planning-records.md` later, so the pointer line is a declared parent hunk) | `dev/planning_checks/progress_append_only.py`, `dev/test_planning_checks_progress.py` | yes |
| `BLOCKED-BY-RULE` agent paragraph + `subagent_stop_gate.py` + journal | **CT-19** (already edits `.claude/agents/*.md` and `subagent_receipt.py`; the gate file is unowned by wave 0) | `dev/hooks/subagent_stop_gate.py`, `dev/test_subagent_blocked.py` | yes (w0-session-hooks lists it under "Never") |
| `stop_gate.py` `blocked_by_rule` rule; `G.blocked-by-rule-undisposed` | **CT-17** (stop_gate owner) / **CT-22b** | existing | yes |
| `plan_decide.py status D<n>` (approved/decision-only/unknown) | **CT-24** follow-up, 15 lines, optional | `dev/plan_decide.py` | land after w0-decisions integrates |

No new ticket is needed. CT-19's hook paragraph and CT-22b's guard are independent; only the PreToolUse rule waits for w0-session-hooks.

## 5. The incident record

Recorded three ways already: `task_plan.md:264` (`D12-applied`), the P3 progress entry, and `DL-16` (`decision`, not approval). **Recommend appending, retroactively and in this order, with `plan:decide` once w0-decisions integrates:**

1. `approval --subject D12 --source "T:L1353 2026-10-14T00:52:05Z (AskUserQuestion 'Approve D1–D41 defaults')" --text "progress.md: archive to progress-archive-2026-10-13.md; approved after application (D12-applied)"`
2. `operation --subject "archive progress.md (D12)" --source task_plan.md#D12-applied --text "applied 2026-10-14T00:06Z by P2 ahead of approval; published d420a7e"`
3. `receipt DL-<op> --path .planning/…/progress-archive-2026-10-13.md --rc 0`

With these rows the 3b exemption holds for `d420a7e` without a special case; because the rows post-date the commit, the exemption's "same calendar day" test compares the timestamp in the approval's `source` field, not the row's `ts`. The approval text says the sequence was wrong; the append-only ledger keeps that visible.

## 6. Could not verify

- Whether the SubagentStop payload carries `last_assistant_message` in this Claude Code build; the transcript-tail fallback covers either case.
- Whether `systemMessage` from a SubagentStop hook is displayed; if not, the journal + `stop_gate` route is the only parent-side signal.
- w0-doctor-records/CT-22b scope for `K.progress-size` (may already exist in `planfiles.py`); drop the duplicate at integration.
- Live hk firing of `check:records` on this host (w0-doctor receipt: "hk hooks are already installed", unverified here).
- P2's reasoning between 00:04Z and 00:06Z: only tool calls and the final message were read; no assistant text mentioning the rule exists before the receipt, so the conflict was recognised at write-up time, not before the split.
