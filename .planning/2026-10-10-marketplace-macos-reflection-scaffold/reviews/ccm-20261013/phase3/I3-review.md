# I3 review: cold review of the staged group-3A tree (second A09 publish)

Reviewer: Fable 5.1 (session `ccm-20261013-check`, reviewer role, read-only). Reviewed
2026-10-13. Root checkout `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace`,
branch `codex/marketplace-native-onboarding`, HEAD `0a68dce` = `origin/codex/marketplace-native-onboarding`.
Staged tree reviewed: `git write-tree` = **`d571874d8f3c1de67548399f4f7fe69ea70db37a`** (93 paths,
2,538,325 bytes of index blobs). Nothing was edited, staged, unstaged or committed; this file is
untracked and is not part of the reviewed tree.

## Disposition: PASS-with-P2/P3 for publish

No P1. Two P2 record contradictions inside the staged set (both one-hunk fixes in parent-owned
planning files; fix and re-stage before `delivery:prepare`, or publish as is and correct in the
next docs commit at the parent's call). Five P3 items with owners. The accepted-decisions hunk 2
is a user decision and was correctly left out.

## 1. Leak check (highest priority)

| Check | Command | Result |
|---|---|---|
| MCP allow-list strings | `git grep --cached -n -E 'mcp__' -- <93 paths>` | 1 hit, `phase3/I3-group3a-report.md:143`, the prose `mcp__<server>__` pattern; no tool name |
| `permissions` blocks | `git grep --cached -n -E '"permissions"\|permissions\.(allow\|deny)\|"allow"\s*:\s*\['` | 11 hits, all prose or the C2 placeholder `"permissions": {"allow": ["<the seven MCP rules, verbatim from the backup>"]}` (`prevention/C2-prevention-design.md:1233`); no rule reproduced |
| Token/cookie/key shapes (ghp_, github_pat_, sk-ant-, sk-, xox, AKIA, Bearer, api_key=, cookie=, password=, PEM) | `git grep --cached -n -i -E ...` | 1 hit, `codex-sweeps/A-private-evidence-inventory.md:99`, the scanner pattern list itself |
| E-mail addresses | `git grep --cached -o -E '<email>'` | only `noreply@anthropic.com` (attribution trailers, 4 lines) |
| gitleaks 8.30.1 dir mode | `git archive d571874 <93 paths>` to scratchpad; `gitleaks dir <copy> --no-banner --redact=100 --report-format json --exit-code 9` | **rc 0, "no leaks found", 0 findings, 2.51 MB scanned**. The mise shim has no version; the absolute install `~/.local/share/mise/installs/gitleaks/8.30.1/gitleaks` was used |
| Raw provider captures | `A-inventory.json` parsed: 266 rows of `{path, rel, sha256, bytes, disposition, secret_flag, note, ...}`; max string length 215; the 5 `secret_flag: true` rows are `keep-private` pointers to `events.jsonl` captures and a redacted gitleaks report that live only in the excluded `2a14/` payload | no captured content staged |
| Personal paths | `git grep --cached -c '/Users/rmanaloto'` over the set: 367 lines in 30 files, dominated by `T2-import-plan.json` (229) and `T2-import-lane-design.md` (85); outside the repo checkout they name `~/.gitignore_global:34:*.log` ignore attributions, the 0700 mirror `~/.local/state/marketplace-imports/...`, `~/.codex/worktrees/{2a14,c658}` and `~/.claude/{projects,plugins}`. Precedent: `git grep -c '/Users/rmanaloto' 0a68dce` matches **3355 files**, 1894 of them with `~/.codex`/`~/.config`/`~/.claude` paths | within repo precedent; the only path the brief called personal (`Downloads`) is redacted to `<personal directory>` (I3 §3) |
| Exclusions | `git check-ignore -v` rc 0 for `settings.json.before-ct02`, `plan-backups/`, `codex-briefs/digests/`, `imports/.../2a14/`, `imports/.../c658/`, `.agent/`, `.claude/settings.local.json` (all from `.git/info/exclude:8-15`); `git status --porcelain --ignored` lists each as `!!`; none is in `git diff --cached --name-only` | confirmed |

## 2. Record corrections (SYNTHESIS §4 spot-checks, 8 rows + extras)

All nine staged lane records parse (`python3 -I json.load`); every `base_sha`, `allocated_from`,
`merged_head`, `integration_merge` and `published` SHA resolves (`git cat-file -e`), and
`merged_head` is an ancestor of `integration_merge`, which is an ancestor of `published`, for all
eight integrated lanes (`git merge-base --is-ancestor`). `ct21-codex-imports.json` keeps
`base_sha: TBD-at-cut` by design (designed, not cut).

| # | Row | Staged value | Evidence |
|---|---|---|---|
| 1 | `lanes/gate-hooks.json` base/alloc/merged/im/pub | `2d1f60e` / `e618243` / `697e1da` / `760b154` / `0a68dce` | `git log -1 --format=%P 760b154` = `9cd396a 697e1da` |
| 2 | `lanes/nav.json` base | `c6ff7ef` | `git rev-parse 5cadad4^` = `c6ff7ef`; `integration_merge fa892d2` ancestor of `28fedf1` |
| 3 | `lanes/c1-catalog-promotion.json` base/merged | `ca60871` / `6c09b7f (7295463 = merge of 2d1f60e)` | `git rev-parse 52ce420^` = `ca60871`; `retros/c1-catalog-promotion.md:6` now reads "merged with `2d1f60e` as `7295463` (integration merge `4c1ea6b`)" |
| 4 | `lanes/team.json` + `retros/team.md:4` | `merged_head ea8c8c9`, `integration_merge 7e22d13`; retro "lane commit `5107322` on base `361688e` (sync merges `9103931`, `5becfc0`)" | staged diff `-U0` |
| 5 | a06 retro alias | `retros/a06-unit3.md` new; `diff <(sed '2,4d' copy) original` rc 0; original still tracked; `python3 -I dev/retro_gate.py --unit a06-unit3` rc 0 | matches R5 P2-5 / §5 step 7 |
| 6 | `docs/agents/claude-team.md:95` | "Reviewer judgement rules live in `CODING_STANDARDS.md` (integrated with ticket CT-04, lane `nav`, merge `fa892d2`)" | the only hunk in that file (`git diff --cached -- docs/agents/claude-team.md`) |
| 7 | `docs/agents/claude-takeover.md` | `:7` sweep C sentence verbatim ("No Codex root thread is mid-turn, but nine spawned children died ..."); `:11` D15 wording ("they have not been invoked. A stage counts as invoked only when the user types it"); `:13` Secrets bullet (fnox >= 1.39.0, exec-scoped route); `:15-30` "Codex coordination state superseded" subsection with sweep B's notice; `:66` "Current (2026-10-13)" paragraph above the retained standby snapshot | five items present |
| 8 | `build_manifests.py` | docstring "eleven tickets (CT-01..CT-11)", "spec.md beside this script"; CT-11 moved after CT-10; `tickets.preview.json` order CT-01..CT-11 (parsed); `spec.manifest.json` not in the set | matches R2 publication fix 3 as scoped by I3 §1 (not the prospective 16) |
| 9 | `docs/accepted-decisions.md` | hunk 1 only: +53 lines "Automation and observability clarification (2026-10-12)", blob `5fc8c85` -> `7104df6` | `git diff --cached -U1` shows a single hunk at `@@ -18,2 +18,55 @@` |
| 10 | `retros/retro-gate.md:3` | appended "merged with tip `9d478cd` as `82c351f` after repair `5ea8ee4` (final lane tip; integration merge `e618243`)" | staged line tail |
| 11 | `retros/gate-hooks.md` | untouched here; HEAD line 3 already reads "base `2d1f60e` (allocated from `e618243`)" | committed in `760b154` as I3 says |

## 3. Planning files

- `task_plan.md`: `## Session handoff (2026-10-13)` at line 9, "Next action" at 16, `## Next Step`
  at lines 28-30; all inside the first 30 lines.
- `progress.md`: the last bullet is `- NEXT (2026-10-13, owner: parent of Phase 3; rewrite in
  place, keep last): group 3B ...`; the archive pointer at `:3-4` names
  `progress-archive-2026-10-13.md`, which is staged (`git ls-files -s` blob `3eb447a`).
- `ticket-ledger.md`: 3 pipe tables, 0 column-count mismatches; 26 CT rows.
- `findings.md`: no "next step" / "next action" / "todo" lines (`grep -i` rc 1); headings are
  Verified baseline / Inherited limitations / Sources / Claude takeover / Session review.
- No `.mode` file in the tree or the index (`find`, `git diff --cached --name-only`).
- `frontier.toml`: `max_parallel = 3`, `max_live_agents = 8` (D30), `always_active = ["cxx"]`
  with an explicit include list (D27), `offline_split = true` (D28),
  `context_ceiling_fraction = 0.5` (D29), `retro_apply = "auto"` (D31), `executor = "native"`
  (D33), `publish_batch = "per-integration"` (D37), `escalate_after_partial = 1` (D35),
  `schedule = opus/high` (D36), `check_lock = true`; no absolute personal path (only `#`
  comments, repo-relative paths and `~`-free text). The `#30-#61` range in `include` is parsed
  by `frontier.py:132`.

## 4. Skill

- `diff -r .claude/skills/ticket-frontier .agents/skills/ticket-frontier` rc 0 (working tree);
  index blobs identical per path (`git ls-files -s` compare).
- `SKILL.md` frontmatter: `name: ticket-frontier`, `description: ...`, `user-invocable: true`;
  no `disable-model-invocation` anywhere in either mirror (`git grep` rc 1).
- `scripts/frontier.py` imports: `argparse, datetime, json, os, re, subprocess, sys, tomllib,
  pathlib, typing, __future__`; stdlib only.
- `python3 -I -m unittest discover -s dev -p test_ticket_frontier.py`: **rc 0, Ran 29 tests OK**.
  The tests drive the script as a subprocess (`dev/test_ticket_frontier.py:58`
  `subprocess.run([sys.executable, "-I", str(SCRIPT), ...])`), an external seam.
- `.claude/agents/frontier-scheduler.md` frontmatter: `name`, `description`, `model: opus`,
  `effort: high`, `permissionMode: plan`, `disallowedTools: [Edit, Write, NotebookEdit, Agent]`,
  `maxTurns: 40`; consistent with D36 and `frontier.toml` `[model_policy].schedule`.
- `frontier.py status` (the SKILL.md `!` preamble) ran rc 0 against this tree and left
  `git status --porcelain` unchanged; `P/frontier/` still does not exist.
- Em-dash (U+2014): zero in the new skill mirrors, the agent file, `dev/test_ticket_frontier.py`
  and `frontier.toml`. See P3-1 for the three in `claude-takeover.md`.

## 5. Baseline and gates (all `VIRTUAL_ENV` unset; exact exit codes captured without pipes)

| Command | rc | Summary |
|---|---|---|
| `./dev/mise tasks validate` | 0 | 56 tasks |
| `./dev/mise run check` | 0 | 91 tests OK; `{"baseline": 0, "json": 2298, "python": 232, "shell": 6, "toml": 20, "status": "pass"}` |
| `./dev/mise run check:acceptance-baseline` | 0 | `"baseline": 19`, status pass |
| `git diff --cached --check` | 0 | |
| `python3 -I dev/retro_gate.py --unit a06-unit3` / `gate-hooks` / `ccm-20261013-session` | 0 / 0 / 0 | RETRO GATE PASSED, selectors `VIRTUAL_ENV` |
| 19 baseline files | `git diff --quiet -- <19>` rc 0; `git diff --cached --quiet -- <19>` rc 0 | worktree == index == HEAD |
| Size | largest blob `progress-archive-2026-10-13.md` 220,112 B; `MANIFEST.json` 205,930 B; `T2-import-plan.json` 187,260 B | nothing over 300 KB; total 2,538,325 B |

## 6. Scope

- `sort I3-selected-paths.txt` vs `git diff --cached --name-only | sort`: identical (93/93).
- `mise.dev.toml`, `dev/check.py`, `.claude/settings.local.json`, `settings.json.before-ct02`,
  `plan-backups/`, `digests/`, `2a14/`, `c658/`, `.agent/`, `*.mode`: absent from the index.
- `git status --porcelain` shows no unstaged or untracked change outside the ignored set.
- **Accepted-decisions hunk 2 (left out, correctly).** From
  `imports/codex-worktrees-20261013/2a14/modified/docs/accepted-decisions.md.diff` hunk
  `@@ -27,7 +80,7 @@`, under "## Compiler and build foundation":
  - removed: "Global mise owns tool installations; named p2996 and gcc16 profiles isolate the
    selected compilers. Preserve the current default compiler for unrelated work."
  - added: "The earlier qualified host setup used global mise installations and named
    p2996/gcc16 profiles. Portable project declarations and tasks now supersede reliance on
    those global profiles; retain their historical receipts and preserve the default compiler
    for unrelated work. The shared Mac collector remains explicitly owned by global mise."
  This rewrites a recorded user decision (it inverts who owns compiler installation) and T2
  could not bind the wording to the user. It is a user decision: ask before applying; it stays
  out of this publish.

## 7. Findings (severity-ordered)

**P2-1** `ticket-ledger.md:7-10` (staged; new lines in this set, hunk `@@ -3 +3,12 @@`) states
"integration tip `9cd396a` (one commit ahead of the remote), remote ... = `28fedf1`, `MERGE_HEAD
e12cf04` (merge of `claude/gate-hooks-wiring`, CT-02, staged and uncommitted)", and the CT-02 row
(`:89` of the staged diff) says "in progress ... mid-merge: `MERGE_HEAD e12cf04` staged,
uncommitted". The same staged set's `lanes/gate-hooks.json` says `published 0a68dce (A09)` and
`task_plan.md:11` says "HEAD `0a68dce` = remote ... no `MERGE_HEAD`". SYNTHESIS §4 row
"`P/ticket-ledger.md` `:3-5` snapshot" asks for "tip after publish". Fix: rewrite the snapshot
sentence and the CT-02 row to `0a68dce` / integrated-published. Owner: parent (ledger is
parent-owned).

**P2-2** `task_plan.md:246` Decisions table row `D-all` reads "nothing executed until the user
answers; D27-D41 accepted ... | pending user (D1-D26)", while `task_plan.md:18` says "Pending
user: none of D1-D45 (approved)" and `:194` says D1-D26 "pending user until the user answers".
A resuming agent reading the table would re-ask D1-D26. Fix: one row (status "accepted
2026-10-13" or delete) and the `:194` sentence. Owner: parent.

**P3-1** `docs/agents/claude-takeover.md` gains three em-dashes (`:7` "the one in-flight process
— Carson's T4 Phase C runner", `:20-21` "resuming after 2026-10-19 — including ... — must read")
through the "verbatim" sweep B/C quotes. HEAD's copy had none; no written rule exists in
`CODING_STANDARDS.md`, `AGENTS.md` or `docs/agents` (`git grep -i 'em[- ]dash'` empty), and 36
staged planning records carry them, so this is a style note. Owner: parent, replace with commas or
parentheses if the convention is to be kept in `docs/`.

**P3-2** `reviews/ccm-20261013/00-evidence-index.md:47` heading still reads "Subagents and forks
of the main session (28)"; SYNTHESIS §4 says 27. I3 §7 lists it as a residual. Owner: parent, next
docs commit.

**P3-3** `.claude/skills/ticket-frontier/SKILL.md:3` preamble hardcodes
`python3 -I .claude/skills/ticket-frontier/scripts/frontier.py status` while the body says
"`python3 -I <skill-dir>/scripts/frontier.py`"; because the `.agents/` mirror is byte-identical,
the Codex copy points at the Claude path (harmless: the `!` preamble is Claude-only). Owner: CT-25.

**P3-4** `findings.md` carries the Codex tree state, the `2a14`/`c658` pointers, `qbj4yn5d` and
the strict-five gap, but not the words "Firecrawl Search provisional" or the pwf "second plan
dir" hazard named in the SYNTHESIS §4 findings row (`grep -c` 0 each). Owner: parent, at the
CT-21 record pass.

**P3-5** SYNTHESIS §4 rows outside the group-3A brief remain unapplied and are declared in I3 §7
(`ticket-retro.md:4-8` D15 rewrite, `claude-team.md` merge rule and hooks caveats,
`.claude/AGENTS.md` marketplaces line, `issue-tracker.md` `issue:*` mapping,
`skill-invocations.md:20`, `spec.md:61,65`, `checkout_transfer.py:17`, the absolute `2a14` paths
in `claude-takeover.md:26` / `codex-task-orchestration.md:6`). Owner: parent (W0-7) and CT-21.

## 8. Checks not run

`check:research`, `test:hooks`, `hk validate`, container, provider, hook-runtime and
fresh-session acceptance (`ci/acceptance.sh`), `delivery:inspect-hooks|prepare|publish` (part B).
The A09 publish gate itself has not run; this review covers the static claim only.
