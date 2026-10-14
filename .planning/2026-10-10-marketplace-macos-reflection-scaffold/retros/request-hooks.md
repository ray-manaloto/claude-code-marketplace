# request-hooks retrospective: request capture and carry settings hooks (CT-88, CT-89, D166)

Unit: `request-hooks` (tickets CT-88 capture and CT-89 carry; decision D166, a dated exception to
D92). Worktree `.claude/worktrees/request-hooks`, branch `claude/request-hooks`, cut from allocation
commit `5c62b02` on base `3d5b181`. Lane commits `8f66f44` (hooks, docs, task), `1e99ab1` (fixture
tests, key rule) and `8adf3e4` (retro repairs); integration tips `0e063ce` and `30d65a1` merged clean in
`cb7a708` and `69163fa`. Cold review: reviewer (fable, read-only) PASS-with-P2/P3 on `9a902a2`, relayed
in the parent brief (one P2, two P3, four unrun items); every row below is dispositioned
(CODING_STANDARDS 11-12). Retro-writer: fable, this record.

Delivered (all in `owned_paths`): `.claude/settings.json` gains async `UserPromptSubmit` and
`PostToolUse` (matcher `AskUserQuestion`) hooks that append the hook stdin (`/usr/bin/jq -c .`) to
`~/.local/state/claude-code-marketplace/requests/ledger.jsonl` (directory held at mode 0700 on every
run, never tracked), and `PreCompact`, `SessionStart` (`startup|resume|clear|compact`) and
`SubagentStart` hooks that print a one-line header plus the open `- [ ]` items of the task_plan
`## Open requests` section, read from `${PWF_PLAN_ROOT:-$CLAUDE_PROJECT_DIR}/.planning/$PLAN_ID/task_plan.md`
(SubagentStart wraps them as `additionalContext` with `jq -cRs`). `CLAUDE.md` gains `# Compact
instructions`; `docs/agents/hooks-and-mods.md` and `.claude/rules/hooks-and-mods.md` record the D166
exception and add #102134 to the watch list; `mise.dev.toml` gains `requests:tail`; `dev/test_hooks.py`
gains the `Settings` pin and the `RequestHooks` fixture tests.

Owned paths widened mid-lane: the parent added `dev/test_hooks.py` (the `Settings` test and the
`RequestHooks` fixture tests only) to the lane record because `Settings` pinned the hook set to the
three deny gates and failed `test:hooks` on any D166 hook (finding 1); committed in `18732c7`, merged in
`69163fa`.

Receipts, writer (VIRTUAL_ENV unset; merged bytes `69163fa`):
- Fixture checks of every hook command, `/bin/sh -c` on fixture stdin, scratch HOME: capture
  `UserPromptSubmit` exit 0 and `PostToolUse` exit 0, empty stdout, one compact ledger row each;
  invalid stdin exit 1 (never 2), no row; `PreCompact`, `SessionStart` and `SubagentStart` exit 0 on the
  live plan, 24 open items, 3,110 characters (cap 10,000); missing plan exit 0, header only;
  `PWF_PLAN_ROOT` wins over `$CLAUDE_PROJECT_DIR`.
- Key rule: the `requests:tail` jq key equals the request-catch expression (`dev/handoff.py:335` at
  `ee64a19`, evaluated verbatim) on 5 fixture rows: MATCH (`p:ff1c3221`, `p:rY2dE1Hy`, `p:abcd1234`,
  `p:`, `p:`), jq exit 0.
- `./dev/mise run test:hooks` exit 0, 23 tests (exit 1 on `8f66f44` before the widening).

Receipts, retro-writer (VIRTUAL_ENV unset; on `8adf3e4`, worktree `.claude/worktrees/request-hooks`):
- Mode probe: `/bin/mkdir -p -m 700` on an existing 0755 directory left 0755 (macOS `/bin/mkdir`);
  the repaired `UserPromptSubmit` command on a pre-created 0755 directory with fixture stdin: rc 0,
  mode 700, one compact row.
- `./dev/mise run test:hooks` rc 0, 24 tests (`Settings` 2, `RequestHooks` 6); `./dev/mise tasks
  validate` rc 0 (65 tasks); `./dev/mise run check` rc 0 (`status: pass`); `./dev/mise run
  check:acceptance-baseline` rc 0 (19 baseline hashes); `./dev/mise run check:records` rc 0;
  `python3 -I dev/doctor/cli.py --surface check --json` rc 0; `git diff --check` rc 0.
- Line shape: the live `## Open requests` section has 26 open `- [ ] R-` lines and 0 with a `p:` key
  (`grep -c`), so the old compact instruction named fields no line carries.
- `./dev/mise run retro:gate -- request-hooks` rc 0 on this record (see the parent report).

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P1 | Automated checks (writer): `dev/test_hooks.py::Settings` pinned the project hook set to the three deny gates plus one SessionStart handler, so any D166 hook failed `test:hooks`; the file was outside `owned_paths`. | Applied in `1e99ab1` after the parent widened `owned_paths`; `RequestHooks` is the hermetic fixture proof. Verified: `test:hooks` exit 0, 23 tests. |
| P2 | Automated checks (review, `dev/test_hooks.py:286-288`): the widened `Settings` compared event names only, so a second SessionStart entry or an extra PostToolUse matcher passed `Settings` and `RequestHooks.handler` (rule 15, D92 pin). | Applied in `8adf3e4`: `Settings` asserts `hook_map(hooks) == EXPECTED_HOOKS`, the exact `{event: [(matcher, handler count)]}` map for all eight events (nine entries), and `test_the_pin_refuses_one_more_entry_handler_or_event` proves the pin rejects an added entry, handler and event. Verified: `test:hooks` rc 0, 24 tests. |
| P2 | Information access (writer): the CL4 E2 key, "first 8 characters of `tool_use_id`, else `prompt_id`", is `p:toolu_01` for every AskUserQuestion answer (CT-87 receipt), so one projected answer would close all answers. | Applied in `1e99ab1` with lane request-catch: answers key on the last 8 of `tool_use_id`, prompts on the first 8 of `prompt_id`; `requests:tail` and `docs/agents/hooks-and-mods.md` state it. Verified by `test_requests_tail_keys_...` PASS and the verbatim cross-check MATCH. CL4 E2 (`CL4-proposal.md:119-120`) still reads "first 8 of the key": owner parent, exact edit in the parent list below. |
| P3 | Coding standards (review, `CLAUDE.md:18-19`, rule 9): the compact instructions demanded a `p:<id8>` key, owner and blocker per `R-n`, fields no live line carries (26 open lines, 0 with `p:`), and ended on no checkable condition. | Applied in `8adf3e4`: the section asks for every open `- [ ] R-n (...)` line verbatim with its `issue:` link and any `owner user`, and ends "Done when the summary holds one `R-n` line per open item the PreCompact hook printed". The three carry headers say "keep every line verbatim" (same fact, one shape). Verified: `test:hooks` rc 0 (HEADER at three seams), `check` rc 0. |
| P3 | Coding standards (review, `.claude/settings.json:47`): `mkdir -p -m 700` sets 0700 on a newly created leaf only; an existing wider directory kept its mode. | Applied in `8adf3e4` with no logic added (D166): both capture commands run `/bin/mkdir -p` then `/bin/chmod 700` before `jq`; `docs/agents/hooks-and-mods.md` states it. Verified: the fixture run on a pre-created 0755 directory ends at mode 700, rc 0, and `test_capture_hooks_...` pre-creates the directory at 0755 and asserts 0700; `test:hooks` rc 0. |
| P3 | Automated checks (writer): the PreToolUse merge gate refused `git merge` of the integration tip because it resolved the retro record from the session cwd (moved to the request-catch worktree), not from the repository being merged. | Worked around with `git -C <request-hooks worktree> merge`, exit 0. Deferred, owner parent, destination CT-86 (gate cwd resolution); no file in this lane owns the gate. |
| P3 | Steering/global guidance (writer): the allocation gave this lane `.claude/settings.json` but not the test that pins it. | Deferred to the parent with the literal edit below (`docs/agents/codex-task-orchestration.md`, parent-owned): a lane that adds or removes a settings hook also owns the `Settings` test. Owner parent; closes when the line is in the integration branch. |
| P3 | Steering/global guidance (writer): CL4 E2 asks for a synchronous capture echo and CL4 E4 for a `PostCompact` archive; the lane record and D166 specify async capture that prints nothing and list no `PostCompact`. | Followed the lane record and D166; neither shipped. Deferred, owner user; admission condition: a new decision row that names the echo or the archive. |
| P3 | Automated checks (review, unrun): `/usr/bin/jq` and GNU `sed` in the Linux OCI image. `mise.toml:14` pins `jq = "1.8.2"` through aqua, so the image provides `jq` on the mise path, not at `/usr/bin/jq`, unless the base image ships one; `/usr/bin/sed` is GNU sed on Debian-family images. Failure mode of a missing binary: capture rc 127 (async, non-blocking), SubagentStart rc 127 (never 2, so nothing blocks). | Deferred, owner parent; admission condition: the separately admitted container operation (AGENTS.md Gotchas; CT-80 recheck) runs each command from a fixture under the image and records rc and output; the absolute paths stay until that run says what the image holds. |
| P3 | Automated checks (review, unrun): live firing of these exact commands on the five events, PreCompact on the automatic path, and whether an async hook's exit 1 is surfaced to the user. | Deferred, owner parent; the CT-87 probe receipt covers the events on Claude Code 2.1.300; admission condition: a fresh-session acceptance (`ci/acceptance.sh`) admitted by the user, which records the ledger row, the printed list and the exit-1 surface. |

Navigation: none; `.claude/rules/hooks-and-mods.md` already scopes `.claude/settings.json` through
`paths:` and points at `docs/agents/hooks-and-mods.md`, which holds the ledger path, mode, key and
`requests:tail` under one heading; `AGENTS.md` names the hooks-and-mods doc. Automated checks:
`test:hooks` reaches CI through `check:research` `depends` (gate-hooks retro) and the hosted
research-fast workflow; no existing check is unwired. Tool economy: the retro-writer ran the five
named checks once through a zsh loop and got five usage exits (the `$t` one-word gotcha AGENTS.md
names), then once literally; no new guardrail, the AGENTS.md line is the guardrail. No-ops: applied;
the carry header "keep each id and its next action" named a field no line carries and so changed no
summarizer behaviour; replaced at three seams and in `CLAUDE.md` by "keep every line verbatim".

Parent edits (outside `owned_paths`; literal text, apply unread):
1. `docs/agents/codex-task-orchestration.md`, after the line "Use one implementation writer per
   worktree with explicit disjoint file scopes.", add: "A lane that adds or removes a settings hook also
   owns the `Settings` test in `dev/test_hooks.py`, which pins the hook set (retro request-hooks)."
2. `.planning/<PLAN_ID>/reviews/ccm-20261014/context-loss/CL4-proposal.md`, after "The parent cites
   `p:<id8>` in the plan line." (line 120), add: "Key rule as built (D167, lane request-hooks): a prompt
   keys on the first 8 of `prompt_id`, an answer on the last 8 of `tool_use_id`."
3. `.planning/<PLAN_ID>/lanes/request-hooks.json`: `"review": "fable cold review PASS-with-P2/P3 on
   9a902a2 -> repairs 8adf3e4 (P2 pin, P3 compact instructions, P3 chmod 700)"`, `"retro": "passed
   (retros/request-hooks.md, retro:gate rc 0)"`.
4. CT-86 gains the merge-gate cwd finding (row 6); no file edit here.
