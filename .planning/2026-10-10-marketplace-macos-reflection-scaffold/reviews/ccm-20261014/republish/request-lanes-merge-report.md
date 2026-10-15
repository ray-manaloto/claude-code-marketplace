# request lanes merge report: request-hooks (CT-88, CT-89, D166) and request-catch (CT-90, D167)

Root checkout, branch `codex/marketplace-native-onboarding`, Git user Raymond Manaloto. Merger:
a subagent of session `ccm-20261014` (Opus 5.5), working serially in the root checkout; no other
lane wrote there. `VIRTUAL_ENV` was unset before every command. Every merge was the literal
`git merge --no-ff` run from the root, with no `-C`. Authority: D164 (the retro record lands ahead
of the merge), D166, D167. Scratch logs are in the session scratchpad `request-lanes/`, outside
the checkout. Nothing was pushed or published: the A09 publish waits for lane
`a09-selected-tree`, and the remote is still `959c56f`.

## Preflight

Toplevel was the root checkout, on branch `codex/marketplace-native-onboarding` at HEAD `f635966`
with a clean status. The Git dir was `.git`. Lane tips: `claude/request-hooks` `6a6ca77`,
`claude/request-catch` `f557db5`.

`git merge-tree --write-tree` against `f635966` returned rc 0 (clean) for both lanes. It also
returned rc 0 for request-catch against `18c986a`, after request-hooks was merged.

## Commits

| Step | Commit | Parents | Content |
| --- | --- | --- | --- |
| R1 records | `bb3e476` | `f635966` | `retros/request-hooks.md` (blob `b1b7098`, the same blob as `6a6ca77`); parent edits H1, H3; 3 files +89 -3. hk `pre-commit` `records` passed |
| M1 merge | `cadd2ed` | `bb3e476`, `6a6ca77` | ort, 6 files +243 -7, rc 0. hk `pre-merge-commit` printed `retro gate passed for: claude/request-hooks`; the PreToolUse deny gate printed nothing (allowed) |
| R2 records | `18c986a` | `cadd2ed` | `retros/request-catch.md` (blob `a0ffa1c`, the same blob as `f557db5`); parent edits C1, C2 (without status), C3; 4 files +123 -6. hk `records` passed |
| M2 merge | `71dbb6b` | `18c986a`, `f557db5` | ort, 11 files +309 -41, rc 0. hk `pre-merge-commit` printed `retro gate passed for: claude/request-catch`; the deny gate printed nothing |
| R3 records | the commit carrying this report | `71dbb6b` | Both lane records set to integrated, the progress entry, and this report |

Byte identity was checked with `git hash-object <path>` against `git rev-parse <tip>:<path>`.
Before each records commit, `git diff --cached --check` returned rc 0.

## Conflicts

There were none. Both lanes add rows to `mise.dev.toml`:

- request-hooks adds `[tasks."requests:tail"]`, now at line 392.
- request-catch adds `[tasks."test:handoff"]` at line 356, and appends `"test:handoff"` to the
  `check:research` `depends` list at line 118.

ort auto-merged the file, and all three rows are present after M2. No other path overlaps
between the two lanes.

## Gates

### After M1 (`cadd2ed`), 20:35:28-20:38:16Z

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 65 tasks |
| `./dev/mise run check` | 0 | 91 tests; json 2319, python 244, shell 6, toml 21 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:hooks` | 0 | 24 tests |
| `./dev/mise run check:research` | 0 | `deps:check` and 18 test tasks, baseline 19 |
| `./dev/mise run retro:gate -- request-hooks` | 0 | `RETRO GATE PASSED`, selectors none |
| `git diff --check bb3e476` | 0 | |
| `diff -r .claude/skills/<s> .agents/skills/<s>` | 0 each | codex-session-history, gh-stack, session-handoff, session-resume, ticket-frontier (both trees carry the same five) |

`test:handoff` did not exist on M1, and the brief schedules it after request-catch.

### After M2 (`71dbb6b`), 20:39:17-20:42:26Z

| Command | rc | Result |
| --- | --- | --- |
| `./dev/mise tasks validate` | 0 | 66 tasks |
| `./dev/mise run check` | 0 | 91 tests; json 2319, python 244, shell 6, toml 21 |
| `./dev/mise run check:acceptance-baseline` | 0 | baseline 19 |
| `./dev/mise run test:hooks` | 0 | 24 tests |
| `./dev/mise run test:handoff` | 0 | 47 tests |
| `./dev/mise run check:research` | 0 | `deps:check` and 19 test tasks, now including `test:handoff`; baseline 19 |
| `./dev/mise run retro:gate -- request-catch` | 0 | `RETRO GATE PASSED`, selectors none |
| `./dev/mise run retro:gate -- request-hooks` (rerun) | 0 | |
| `git diff --check 18c986a` | 0 | |
| `diff -r` of the same five skills | 0 each | |

Before each records commit, the retro gate also ran on the root with the record in place: rc 0
for request-hooks and rc 0 for request-catch.

## Parent edits applied

Edits from `retros/request-hooks.md` (H):

| Edit | Commit | Disposition |
| --- | --- | --- |
| H1 `docs/agents/codex-task-orchestration.md`: Settings-test owner line | R1 | Applied as written, directly after "Use one implementation writer per worktree with explicit disjoint file scopes." (line 92) |
| H2 `CL4-proposal.md` key rule | R2 | Applied once, together with C1, in the brief's wording, which names both lanes |
| H3 lane record `review`, `retro` | R1 | `review` was applied as written. `retro` is the literal `"passed"`, and the full text "passed (retros/request-hooks.md, retro:gate rc 0)" is in `notes`. `status`, `head_sha` and `integration_merge` were set in R3 |
| H4 CT-86 gains the merge-gate cwd finding (row 6) | none | Not a file edit. Left for the parent |

Edits from `retros/request-catch.md` (C):

| Edit | Commit | Disposition |
| --- | --- | --- |
| C1 `CL4-proposal.md` section 4.1 Echo | R2 | `p:<first 8 of the key>` became `p:<id8>`. After "in the plan line." this sentence was added: "Key rule as built (D167, lanes request-catch and request-hooks): a prompt keys on the first 8 of `prompt_id`, an answer on the last 8 of `tool_use_id`." This brief wording replaced both lanes' own sentences. `grep -c 'first 8 of the key'` returns 0 |
| C2 `lanes/request-catch.json` | R2 and R3 | R2 appended the widening note verbatim and set `review` as written. `retro` is the literal `"passed"`, and the record text (gate rc 0, at `f557db5`) is in `notes`. R3 set `status` to integrated, `head_sha` to `f557db5` and `integration_merge` to `71dbb6b`. The record parses with `json.load` (rc 0) |
| C3 `.claude/agents/implementer.md` step 4 | R2 | Applied as written after "...rerun the affected checks." No mirror exists: neither `.agents/` nor `.codex/agents/` has a copy of the implementer role. `grep -c 'merge --no-edit'` returns 1 |
| C4 `progress.md` entry | R3 | Inserted directly above `- NEXT (`, so NEXT is still the last bullet. It went in R3 rather than R2 so it could cite both merges |

Brief versus Stop gate: `dev/hooks/stop_gate.py` blocks the parent's Stop whenever an
integrated lane's `retro` is anything other than exactly `"passed"`. The earlier integrated lanes
(a09-hook-events, scanner-betterleaks) hold `"passed"`. Both records therefore keep `"passed"`,
and the longer text is in `notes`.

## Observed, not acted on

- The capture hooks took effect in the root as soon as M1 changed `.claude/settings.json`. An
  informational run of `python3 -I dev/handoff.py check --json --agents-done` (not a gate) on
  `71dbb6b` returned rc 2 with these findings:
  - `H.request-unprojected`: `p:9dc3aa9d`, one captured row for session `ce9c0b3d`.
  - `H.request-unlinked`: R-172, R-173 and R-174.
  - The usual root findings: `H.handoff-stale-sha`, `H.head-not-remote`,
    `H.mode-not-inject-smart` and `H.pending-decision-unlisted`.

  The parent should project or dispose of `p:9dc3aa9d` and link R-172 to R-174. The ledger text
  was not read.
- No `decisions.jsonl` operation row was added for these integrations because the brief asked
  for none. The parent decides whether one belongs, as DL-221 did for a09-hook-events.

## Not run

- The A09 publish and any push: they wait for lane `a09-selected-tree`.
- The lane-unrun items stay with their owners: the container check of `/usr/bin/jq` and GNU
  `sed`, live firing on a fresh session (`ci/acceptance.sh`), and the root `write --dry-run`
  budget (request-catch RC-4).
