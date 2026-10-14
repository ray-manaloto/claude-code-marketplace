# request-hooks retrospective: request capture and carry settings hooks (CT-88, CT-89, D166)

Unit: `request-hooks` (tickets CT-88 capture and CT-89 carry; decision D166, a dated exception to
D92). Worktree `.claude/worktrees/request-hooks`, branch `claude/request-hooks`, cut from allocation
commit `5c62b02` on base `3d5b181`. Lane commit `8f66f44`; integration tip `0e063ce` merged clean
in `cb7a708`. Writer draft; the independent cold review and the retro-writer pass have not run yet,
so the unit stays partial until the parent dispatches them.

Delivered (all in `owned_paths`): `.claude/settings.json` gains async `UserPromptSubmit` and
`PostToolUse` (matcher `AskUserQuestion`) hooks that append the hook stdin (`/usr/bin/jq -c .`) to
`~/.local/state/claude-code-marketplace/requests/ledger.jsonl` (directory mode 0700, never tracked),
and `PreCompact`, `SessionStart` (`startup|resume|clear|compact`) and `SubagentStart` hooks
that print a one-line header plus the open `- [ ]` items of the task_plan `## Open requests` section,
read from `${PWF_PLAN_ROOT:-$CLAUDE_PROJECT_DIR}/.planning/$PLAN_ID/task_plan.md` (SubagentStart
wraps them as `additionalContext` with `jq -cRs`). `CLAUDE.md` gains `# Compact instructions`;
`docs/agents/hooks-and-mods.md` and `.claude/rules/hooks-and-mods.md` record the D166 exception and
add #102134 to the watch list; `mise.dev.toml` gains `requests:tail`.

Receipts (VIRTUAL_ENV unset; on the merged bytes `cb7a708` unless noted):
- Fixture checks of every hook command, `/bin/sh -c` on fixture stdin, scratch HOME: capture
  `UserPromptSubmit` exit 0 and `PostToolUse` exit 0, empty stdout, one compact ledger row each;
  invalid stdin exit 1 (never 2), no row; `PreCompact`, `SessionStart` and `SubagentStart` exit 0 on the
  live plan, 24 open items, 3,110 characters (cap 10,000); missing plan exit 0, header only;
  `PWF_PLAN_ROOT` wins over `$CLAUDE_PROJECT_DIR`. As unit tests in the proposed `dev/test_hooks.py`
  patch: `RequestHooks` 5 tests and `Settings` 1 test PASS (red first: KeyError `PreCompact` and the
  missing-event assertion on the unchanged settings).
- `./dev/mise run check:records` exit 0; `python3 -I dev/doctor/cli.py --surface check --json` exit 0,
  no findings; `./dev/mise tasks validate` exit 0; `./dev/mise run check` exit 0;
  `./dev/mise run check:acceptance-baseline` exit 0 (19 baseline hashes); `git diff --check
  3d5b181 HEAD` exit 0.
- `./dev/mise run test:hooks` exit 1 on the committed bytes (the `Settings` pin, finding 1);
  exit 0, 22 tests, with the proposed patch applied (patch sha256
  66a056ef7467ee7fe50ae8fac10e69d8cffefd0b354cbc39d59c645f9158a98b).
- `requests:tail` run line on the fixture ledger exit 0, prints `{"key":"p:toolu_fi",...}`.

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P1 | Automated checks: `dev/test_hooks.py::Settings` pins the project hook set to the three deny gates plus one SessionStart handler, so any D166 hook fails `test:hooks`; the file is outside `owned_paths`. | Held for the parent (owner parent): apply the proposed patch (sha256 above), which widens the pin to the D166 events and adds `RequestHooks`, the hermetic fixture proof the lane delivers. Verified: `test:hooks` exit 0 with it, exit 1 without it. |
| P2 | Information access: the CL4 E2 key, "first 8 characters of `tool_use_id`, else `prompt_id`", is `p:toolu_01` for every AskUserQuestion answer (ids look like `toolu_01NaR2...`, CT-87 receipt), so one projected answer closes all answers in the request-catch reader. | Routed to the parent and lane request-catch (CT-90), owner parent: key answers on `tool_use_id` characters after `toolu_` (or the last 8) and update CL4 E2. The ledger stores raw stdin, so no ledger change is needed; `requests:tail` follows whatever key rule CT-90 adopts (one jq slice). |
| P3 | Automated checks: the allocation gave this lane `.claude/settings.json` but not the test that pins it. | Proposed allocation rule for the parent (owner parent, frontier-scheduler brief): a lane that adds or removes a settings hook also owns `dev/test_hooks.py` `Settings`. |
| P3 | Steering: CL4 E2 asks for a synchronous capture echo and CL4 E4 for a `PostCompact` archive; the lane record and D166 specify async capture that prints nothing and do not list `PostCompact`. | Followed the lane record and D166; neither element shipped. Deferred, owner parent: a new decision if the echo or archive is wanted. |
| P3 | Coding standards: "nothing blocks" needed care: GNU `sed` exits 2 on a missing file, and exit 2 from `PreCompact` blocks compaction; `jq` exits 2 on invalid JSON. | Applied: carry commands end `; exit 0` or pipe into `jq`; capture maps any failure to `exit 1`. Verified by the missing-plan and invalid-stdin tests (exit 0 and exit 1). GNU sed itself was not run on this macOS host; held as unverified for the Linux image (owner parent, CT-80 recheck). |

Navigation: applied; `docs/agents/hooks-and-mods.md` now holds the ledger path, its key and
`requests:tail` under one heading, and the rule file points there. Steering/global guidance: applied
in the two hooks-and-mods documents and `CLAUDE.md`; AGENTS.md unchanged. Tool economy: applied;
each command was proved once through the scripted fixture run and once through the unit tests, and the
long checks ran once per state (pre-merge, merged). No-ops: applied; the compact instructions state
the target ("carry every open request ... one line per id") instead of a prohibition.

Unverified: live firing of these exact commands (no session admitted; the CT-87 receipt covers the
events); PreCompact on the automatic path; `/usr/bin/jq` and `/usr/bin/sed` in the Linux OCI image;
whether an async hook's exit 1 is surfaced to the user.
