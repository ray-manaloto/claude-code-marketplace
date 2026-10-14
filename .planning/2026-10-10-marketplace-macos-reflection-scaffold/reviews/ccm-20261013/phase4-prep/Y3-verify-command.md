# Y3: `/verify` as a repo skill and the `verified` lane state

Written 2026-10-14 by Y3 (read-only; this file is the only write). CLI `2.1.299`. `P` = `.planning/2026-10-10-marketplace-macos-reflection-scaffold`, `RV` = `P/reviews/ccm-20261013`. Docs: `https://code.claude.com/docs/en/skills` (SK), `https://code.claude.com/docs/en/commands` (CMD), fetched today. Quoted contents are data.

## 1. What exists

**Claude Code ships a bundled `/verify`.** CMD: "**Skill.** Confirm a code change does what it should by building your project's app, running it, and observing the result, rather than relying on tests or type checks"; "`/verify` runs only when you invoke it. Before v2.1.215, Claude could also run `/verify` on its own." It is one of three app-driving skills (SK "Run and verify your app": `/run`, `/verify`, `/run-skill-generator`) and is absent from this session's model-visible skill list (`run`, `code-review`, `simplify`, `security-review` are present). The on-disk cache `/private/tmp/claude-501/bundled-skills/2.1.296/` holds only `plugin-authoring`.

**The override is sanctioned.** SK: "`/verify` can also record its own recipe ... it writes what worked to `.claude/skills/verify/SKILL.md` at the repo root ... At the repo root, the recorded skill replaces the bundled `/verify`"; precedence: "Your skill replaces the bundled command, but not its aliases." So `.claude/skills/verify/SKILL.md` is where a project `verify` belongs. Typing `/verify` before it exists would let the bundled skill write that path, so CT-32 lands the file first.

**Third-party verify skills in the plugin cache** (not installed for this project): `omc/oh-my-claudecode/*/skills/verify`, `caveman/*/skills/verify-and-stop`, `nyldn-plugins/octo/*/skills/skill-verify` (`disable-model-invocation: true`). All three are prompts ("report only what was verified", "no completion claims without fresh evidence") without receipts, hashes or a merge refusal. mattpocock 1.3.1 has no verify skill; its close-out is `implement` step 4 and `implement-spec` step 7: `code-review`, two axes with a required fixed point (`RV/D1 §6.12`; `S/code-review:17-80`); `tdd` is red before green at pre-agreed seams (`S/tdd:22,36`). The repo's `reviewer` already runs both axes from `base_sha` (`.claude/agents/reviewer.md:16-20`). No `/verify` appears in the recorded history (`RV/phase4-prep/` X1-X4 use "verify" as a verb only).

**Docs on defining the skill (SK, quoted).** Location "Project: `.claude/skills/<skill-name>/SKILL.md` ... Commit it so your team gets it too." Reach: "By default, both you and Claude can invoke any skill"; `disable-model-invocation` "prevent[s] Claude from automatically loading this skill"; `user-invocable: false` "hides it from the `/` menu." Arguments `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`; `argument-hint` "shown during autocomplete". Injection: "The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude"; a non-allowed command "aborts the invocation ... pre-approve it with `allowed-tools`". `context: fork` "starts a new subagent of the type set in the `agent` field ... The subagent doesn't see your conversation history"; `agent` is "any custom subagent from `.claude/agents/`. If omitted, uses `general-purpose`." `hooks` "registers when the skill is invoked and keeps running for the rest of the session." Commands: "Custom commands have been merged into skills"; on conflict "A skill and a file in `.claude/commands/`: The skill." Bundled: `/doctor` ("setup checkup ... fixes that Claude applies after you confirm"), `/code-review [level] [--fix]` with alias `/review` (since v2.1.223), `/simplify`, `/security-review`, `/skill-doctor`. `Skill(verify *)` permission rules apply.

## 2. Design: `.claude/skills/verify/` (+ `.agents/skills/verify/` mirror)

```yaml
---
name: verify
description: Verify a lane, ticket or range against the named gates, the doctor, the retro gate and the two-axis review; write a hash-bound receipt. Use at lane close-out, before integrate or publish, or when asked "is it verified", "run the gates", "verify <unit>".
argument-hint: "<unit>|<ticket>|--all|--since <sha> [--dry-run] [--full]"
allowed-tools: Bash(./dev/mise run verify *), Bash(python3 -I dev/verify.py *), Bash(git diff *), Bash(git log *)
---
!`python3 -I "${CLAUDE_PROJECT_DIR}/dev/verify.py" status 2>&1 || true`
```

Neither `disable-model-invocation` (the parent calls it at close-out) nor `user-invocable: false` (the user types it). No `context: fork`: the skill calls the Skill tool for `mattpocock-skills:code-review` with the lane brief in view, and the mechanical half runs in a shell, so the parent's window carries only the receipt. Codex mirror: `agents/openai.yaml` with `allow_implicit_invocation: true` (D1 §1).

**Steps (the script does 1-6 and 8-9, the skill does 7).**

1. **Resolve scope.** `<unit>` reads `P/lanes/<unit>.json` (`branch`, `base_sha`, `lane_commit`, `owned_paths`, `required_checks`); `<ticket>` maps through lane records' `tickets`, else refuses; `--since <sha>` uses `git diff --name-only <sha>...HEAD`; `--all` takes every lane not `closed`. A changed path outside `owned_paths` is a refusal (the merger's rule, `docs/agents/claude-team.md:22`).
2. **Run the named gates**, each a subprocess with its own rc:

   | Gate | Applies when | Pass |
   | --- | --- | --- |
   | `./dev/mise tasks validate` | always | rc 0 |
   | `./dev/mise run check` | always | rc 0 |
   | `./dev/mise run check:acceptance-baseline` | always | rc 0, "19" in stdout |
   | `git diff --check <base>..<head>` | always | rc 0 |
   | `./dev/mise run test:hooks` | diff touches `dev/hooks/**`, `hk.pkl`, `.claude/settings.json`, `dev/retro_gate.py`, `dev/git_delivery.py` | rc 0 |
   | `./dev/mise run test:doctor` | diff touches `dev/doctor/**` or `dev/check.py` | rc 0 |
   | `./dev/mise run check:records` | diff touches `.claude/settings*.json` | rc 0 |
   | `./dev/mise exec -- hk validate` | diff touches `hk.pkl` | rc 0 |
   | `test:*` rows in `check:research` `depends` whose test file is in the diff | per row | rc 0 |
   | lane `required_checks` that are mise tasks or `unittest` lines | `<unit>` | rc 0 |
   | `./dev/mise run check:research` | `--full` only, parent-run, serialized | rc 0 |

   A gate that cannot start is `unavailable` and fails the receipt, never `skipped`.
3. **Doctor.** `python3 -I dev/doctor/cli.py --surface check --json` (rc 0/2/3, findings copied in, P1/P2 fail); `--surface integrate --unit <unit>` once CT-22 ships it.
4. **Retro gate.** `python3 -I dev/retro_gate.py --unit <unit> --repo <checkout>` (shape only, as today).
5. **Red-first check** when the lane receipt or retro claims "red" or the record has `tdd: true`. The reviewer's method, which `RV/phase3/w0/w0-doctor-review.md:52` left unrun because the lane had one implementation commit: for each `dev/test_*.py` added or changed in the diff, `git worktree add <tmp> <base_sha>`, copy in the head version, run `python3 -I -m unittest <file>`; expected rc ≠ 0 at base, 0 at head. A test green at base fails the receipt; per-file rcs let a reviewer tell ImportError red from assertion red.
6. **Review pointer.** The receipt must name a report whose disposition starts with `PASS` (`lanes/<unit>.json.review` or `--review <path>`); `FAIL` or none fails. The script never runs a review.
7. **Two-axis review (skill step, model-invoked).** With no PASS report and a fixed point (`base_sha`, or `spec.manifest.json.start_sha` for `--all`), call the Skill tool for `mattpocock-skills:code-review`, write the report by Bash heredoc to `RV/phase3/<wave>/<unit>-review.md`, rerun step 6. Commit first: `code-review` diffs three-dot (`D/code-review:81`).
8. **Receipt** `RV/verify/<unit>-<head7>.json`: `{schema: "verify/v1", scope: {unit, ticket, base_sha, head_sha, branch, changed_paths: [{path, sha256}]}, gates: [{name, cmd, rc, ms, ok}], doctor: {rc, counts, findings}, retro_gate: {rc}, red_first: [{test, base_rc, head_rc, ok}], review: {path, disposition, sha256}, ok, started_utc, finished_utc, model, in_lane}`; `ok` only when every row is ok.
9. **Ledger pair**, only on the integration branch (a `claude/*` worktree writes a receipt with `in_lane: true` and no row): `plan_decide.py operation --subject "verify:<unit>@<head7>" --source <receipt>` then `plan_decide.py receipt DL-n --path <receipt> --rc <rc>` (`dev/plan_decide.py:64-73` binds the file's sha256, so the JSON is final first). `--dry-run` prints the table and receipt and writes nothing. Exit 0 only when `ok`, 2 with one reason per line, 1 usage (C2 §E).

The mise task (`mise/tasks/verify.toml` if the D7 spike passes, else `mise.dev.toml` rows as a parent hunk), plus `test:verify` in `check:research`'s `depends` (`.claude/rules/dev-tests.md` route 2):

```toml
[tasks.verify]
description = "Verify a lane, ticket or range: gates, doctor, retro gate, red-first, review pointer; hash-bound receipt"
usage = 'arg "<target>" help="<unit> | CT-nn | --all"; flag "--since <sha>"; flag "--dry-run"; flag "--full" help="also check:research (parent only)"; flag "--review <path>"'
run = '"${MARKETPLACE_PYTHON:-python3}" -I dev/verify.py run "${usage_target?}" ${usage_since:+--since "$usage_since"} ${usage_dry_run:+--dry-run} ${usage_full:+--full} ${usage_review:+--review "$usage_review"}'
```

## 3. Enforcement

Lifecycle gains **verified** between retro and integrate (`docs/agents/claude-team.md` table and `status` vocabulary; `lanes/<unit>.json` gains `verify: "<receipt path>"`, `.claude/rules/planning-records.md`). Two receipts per lane: in-lane on `lane_commit` (no ledger row) and the parent's on the merged tree (ledger pair). The gates below only **read** the receipt, so no verify run sits inside a hook timeout.

| Point | Kind | Change | Latency |
| --- | --- | --- | --- |
| `subagent_stop_gate.py` | Claude hook, 15 s | a `claude/*` worktree also needs `RV/verify/<unit>-<HEAD7>.json` with `ok: true`; blocks once | < 20 ms |
| `stop_gate.py` | Claude hook, 10 s | an `integrated` lane needs `retro: passed` and `verify` naming an `ok` receipt bound to the merged lane commit | < 20 ms |
| `pretooluse_gate.py`, `git_gate.check_lanes` | Claude hook, 10 s; hk `pre-merge-commit`, `pre-push` | `retro_gate.py --require-verify` (new flag, `git_gate` only): refuse a merge or publish of a lane whose in-lane receipt is missing, `ok: false` or bound to another SHA | < 100 ms per lane |
| merger (`.claude/agents/merger.md`, D49 g) | agent step | no merge without the in-lane receipt; runs `verify <unit>` on the merged tree before the records commit | 1-4 min |
| `lane:integrate` (CT-17) | mise task | calls `verify -- <unit>` before and after `git merge --no-ff` | same |
| `frontier.py release` (CT-25) | skill script | refuses unless `lanes/<unit>.json.verify` is an `ok` receipt; `split-required` exempt | < 20 ms |
| `retro:gate` | mise task | unchanged in-lane (verify runs it, no cycle); `--require-verify` only at merge/push | unchanged |
| A09 `check_task` (`dev/git_delivery.py:366-369`) | last line | the intent lists `verify`; `SAFE_NAME` admits it | 1-4 min |

Run budget: `check` ~10 s, `test:hooks` ~30 s, `test:doctor` ~5 s, doctor ≤ 10 s (`core.BUDGET_MS`), `retro:gate` < 1 s, red-first ~3 s per test file; `check:research` only with `--full`. Hooks fail closed (exit 2 on internal error, D51).

## 4. Tests (red first) and the script

`dev/test_verify.py`, seam tests through the CLI (`dev-tests.md`) in scratch repos as `dev/test_hooks.py` builds them, each red first: scope from lane record and `CT-nn` (unknown ticket exits 2); a stub gate exiting 1 gives `ok: false` and exit 2 naming the gate; a missing `dev/mise` is `unavailable`, exit 2; receipt shape and per-path sha256; `--dry-run` writes nothing; ledger pair with `receipt.sha256` equal to the file's; no row from a `claude/*` worktree; red-first passes when the test fails at base, refuses when green there; missing or `FAIL` review pointer exits 2; a path outside `owned_paths` exits 2; `--all` and `--since` scope. Two `dev/test_hooks.py` tests (Stop and SubagentStop block without a receipt) land with CT-32b. `dev/verify.py` is stdlib only, subcommands `run`, `status`, `show`, doctor by subprocess (no `dev/doctor` import); about 250 lines plus 200 of tests.

## 5. Ticket CT-32

**Title:** `/verify` skill and verified-state enforcement. **Blocked by:** w0-doctor integration (`dev/doctor/cli.py` at the root); CT-32b also by w0-session-hooks (owns `stop_gate.py` and `subagent_stop_gate.py` from its cut, HANDOFF §2(c)) and, for `frontier.py release`, CT-25.
**Delivers:** the skill and its mirror, `dev/verify.py` and tests, the task rows, receipts under `RV/verify/`, the `verified` state (docs and rules as parent hunks).
**owned_paths (CT-32a; disjoint from w0-doctor-records, w0-session-hooks, ct21-codex-imports, CT-26, CT-29 and the D7 spike):** `dev/verify.py`, `dev/test_verify.py`, `dev/fixtures/verify/`, `.claude/skills/verify/**`, `.agents/skills/verify/**`, `mise/tasks/verify.toml` (if D7 passes), `P/reviews/ccm-20261013/verify/`, `P/retros/ct32-verify.md`, `P/ledger-ct32-verify.jsonl`.
**Parent hunks:** `mise.dev.toml` rows (if D7 fails) and `check:research` depends; `docs/agents/claude-team.md` lifecycle row and vocabulary; `.claude/rules/planning-records.md` `verify` field; one line each in `.claude/agents/{implementer,merger,retro-writer}.md`; `dev/retro_gate.py --require-verify` and `dev/hooks/git_gate.py` (parent-owned in every lane record).
**CT-32b (after w0-session-hooks):** `dev/hooks/{stop_gate,subagent_stop_gate,pretooluse_gate}.py`, two `dev/test_hooks.py` tests; `frontier.py release` under CT-25.
**Acceptance:** `verify -- w0-doctor --dry-run` exits 0 on the integrated tree; `verify -- w0-doctor` writes a receipt and DL rows; a planted failing gate exits 2; every test was red first; `check`, `check:acceptance-baseline` (19/19), `test:hooks`, `retro:gate -- ct32-verify` exit 0.

## 6. Typed versus automatic; composition

The user types `/verify <unit>`, `/verify CT-22`, `/verify --all` or `/verify --since 21af565` (the project skill replaces the bundled app-driving one; nothing here builds an app). Automatically: the parent calls the Skill tool for `verify` at every lane close-out (ticket-frontier step 6, before `lane:integrate`), the merger runs the mise task on the merged tree, and the Stop, SubagentStop, PreToolUse, hk and `frontier.py release` gates read the receipt. `/mattpocock-skills:retro` stays user-typed and proposes only (`docs/agents/ticket-retro.md:6-8`); `/verify` replaces neither it nor the per-lane `retro-writer`, it proves the retro record and review pointer after both ran. The bundled `/code-review` (bug hunting, model-visible) and `mattpocock-skills:code-review` (two axes) stay separate: `/verify` requires the two-axis report by pointer and calls that skill when it is missing; the bundled one is an optional extra.

## 7. Could not verify

Live behaviour of the bundled `/verify` (user-only, not typed here) and whether `/run-skill-generator` touches an existing `.claude/skills/verify/`; mise `usage` flag expansion (the `doctor` row's `var=#true` form is the fallback); the D7 spike; the CT-22 `integrate` surface; whether `Skill(verify *)` needs a permission rule; receipt location (`RV/verify/` as briefed, or `P/verify/` beside `frontier/` and `retros/`).
