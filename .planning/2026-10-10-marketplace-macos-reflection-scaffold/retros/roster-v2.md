# roster-v2 retrospective — subagent caps and agent-file frontmatter (D189)

Unit: `roster-v2` (D189, DL-242; source R12c §1.1, §1.3, §7.3; request R-177 #141). Worktree
`.claude/worktrees/roster-v2`, branch `claude/roster-v2`, cut from allocation commit `cc07e8c`
(record `base_sha` `2c9d536`); lane commit `aeaa116` (4 files, +12/−3), retro draft `64d4cf2`,
integration merges `30dc039` (tip `4726121`) and `37092f9` (tip `696e03f`, which contains the
`6257246` the retro brief named; the tip moved while the retro was dispatched, see finding 2).
Writer: implementer (Opus 5.5). Retro: retro-writer (Fable 5.1) on top of the implementer's draft.
Takes effect at the user's restart: agent files and settings `env` load at session start.

Delivered, each name or key confirmed in the 2.1.300 offline copy
(`offline/research/R22-cc-2.1.300/raw/`; `docs/sub-agents.md` sha256
`a3d0eb3ac6090f2f2891c920fd365bccd34451ac29bbc546fd30db3d753e8099`, `docs/env-vars.md`
`367cfc9dee9c9edc5f1de8d847772cf48f8752c0a723ee6d167aa6099b38d8a5`, both equal to `docs/SHA256SUMS`;
`CHANGELOG-v2.1.300.md` `8c6fdbbd692bd9b2e108e9946948aa77200b6c8ffec4f807ea9c8cee92545139`):

| Change | Where | Confirmed by |
| --- | --- | --- |
| `env.CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS = "6"` | `.claude/settings.json` (env only) | env-vars.md:316; sub-agents.md:1049; CHANGELOG:3917 |
| `env.CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH = "1"` | `.claude/settings.json` (env only) | env-vars.md:322 ("set `1` to turn nesting off"); CHANGELOG:3857 |
| `disallowedTools: [Agent]`, `experimental: {cacheTtl: 1h}`, no `isolation` | `implementer.md` | sub-agents.md:291 (camelCase, unknown fields ignored), :301, :316-318, :1034 |
| `model: opus` (was fable, D189), `Agent` added to `disallowedTools` | `reviewer.md` | sub-agents.md:302 (`opus` alias), :1034 ("a reviewer that should stay read-only") |
| `experimental: {cacheTtl: 1h}`; step 4 says the record file is the deliverable and keeps the `<unit>.md` basename | `retro-writer.md` | sub-agents.md:316; CHANGELOG:3097; R12c §1.1 rule 4 (CC#101519) |
| step 4: "an Opus reviewer (D189)" for hot-path and frozen-baseline lanes (was "a Fable reviewer") | `frontier-scheduler.md:35` | D189; retro finding 3 |
| `dev/test_doctor_agents.py` (109 lines, 5 tests): every `.claude/agents/*.md` uses 2.1.300 fields, sets `effort`, leaves `isolation` unset, limits `experimental` to `cacheTtl` 5m/1h (quotes stripped), names only known tools in `tools`/`disallowedTools`, and the implementer and reviewer deny `Agent` | `dev/` (parent added the path to `owned_paths` at integration, D189) | sub-agents.md:296-316 (fields), :423-437 (tool names); retro finding 1 |

Keys not confirmed: none; every key written is in the 2.1.300 field table or env table. `effort`
values stay as they were (sub-agents.md:312). `cacheTtl: 1h` is ignored while the subscription
draws on usage credits (sub-agents.md:316): the setting is a request, not a guarantee.

Review: cold, Opus 5.5, high, read-only, on `92f6894`: PASS-with-P2/P3. Every key matches the
2.1.300 docs. P2: the draft's parent edit A compared `cacheTtl` before stripping quotes, so the
valid YAML `"1h"` failed. P3: `disallowedTools` entries were not checked against tool names, so
`Agnet` passed silently. Both are applied in finding 1.

Exits, run from the worktree with `VIRTUAL_ENV` unset, one literal command each, on the final bytes
(after `37092f9`, the test file and the scheduler edit):
`./dev/mise run test:doctor` rc 0 (19 tests; 14 before this retro); `./dev/mise run test:hooks` rc 0
(27 tests); `./dev/mise tasks validate` rc 0 (69 tasks); `./dev/mise run check` rc 0 (91 tests);
`./dev/mise run check:acceptance-baseline` rc 0 (19/19); `git diff --check cc07e8c` rc 0;
`./dev/mise run retro:gate -- roster-v2` rc 0 (the handoff carries the exit on the committed record).
Implementer's scratch acceptance script (expected values from the lane record and DL-242, not from
the files; sha256 `47fca4ee21950a3e76d654f671b875e8293914e24aa10b366799e073d104d1d0`): rc 1 with 8
failures on `cc07e8c`, rc 0 after the edit. `dev/doctor/settings.py` checks top-level keys only
(`env` is in `PROJECT_KEYS`), and `test_live_project_settings_hold_wave0_keys` still reads
`env.PLAN_ID` unchanged.

| # | Severity | Category and finding | Applied action and verification |
| --- | --- | --- | --- |
| 1 | P2 | Automated checks: no static check read `.claude/agents` frontmatter. `claude plugin validate --strict .claude` returns `contents: []` and passes; a probe plugin whose `implementer.md` says `experimentl:` also passes (rc 0). The doctor checks settings keys only. Claude Code ignores an unknown subagent field silently (sub-agents.md:291) and a misspelled tool name in `disallowedTools` denies nothing, so a typo would drop a roster setting unseen. | Applied in-lane: `dev/test_doctor_agents.py`, with the review's two fixes (`cacheTtl` unquoted before the compare; `tools`/`disallowedTools` entries checked against the 2.1.300 tool names, `mcp__*` and `Tool(spec)` forms pass; `Agent` asserted in the implementer's and reviewer's deny lists). `test:doctor` discovers `test_doctor*.py` and `check:research` depends on `test:doctor` (mise.dev.toml:118, :407), so the route in `.claude/rules/dev-tests.md` holds. Red first: `Agnet` planted in `reviewer.md`, `./dev/mise run test:doctor` rc 1 (2 failures, both naming `Agnet`); file restored, rc 0, 19 tests. Owner: retro-writer. Disposition: applied. |
| 2 | P2 | Automated checks: `dev/hooks/git_gate.py merge` classifies a bare SHA only by the refs pointing exactly at it (`kind_at`). `git merge --no-ff -F <msg> 6257246` was refused by the hk pre-merge-commit step with `retro gate refused claude/compaction-40: … retro record missing` because the integration branch had moved to `696e03f` and the un-diverged lane `claude/compaction-40` was the only ref left at `6257246`; once that lane moved too, the same merge is refused as `no lane branch derivable for 6257246` (rc 2, reproduced with `GIT_REFLOG_ACTION="merge 6257246"`). A commit on an integration branch's history is not a lane merge, whatever ref sits on it. | The lane merged the branch by name instead (`37092f9`; the gate classifies the name as integration, rc 0), with no `--no-verify`. Fix: parent edit G below (`dev/hooks/` and `dev/test_hooks.py` are excluded for this lane). Verified transiently in this worktree and restored: test patch alone, `./dev/mise run test:hooks` rc 1 (`(2, True) != (0, False)`: the old gate blames the lane); both patches, rc 0, 28 tests; patched gate on `GIT_REFLOG_ACTION="merge 6257246"` prints `retro gate passed for: no lane branch`, rc 0. Owner: parent, immediate application. Disposition: assigned, patch and red/green receipts attached. |
| 3 | P2 | Steering: the reviewer model was fixed as Fable in seven places after D189 moved it to Opus: `frontier-scheduler.md:35`; `frontier.toml:34` (`[model_policy] review` feeds the per-call `model`, which overrides the agent file, model-policy.md:23, so the frontier would keep dispatching the reviewer on Fable); `model-policy.md:13` and `:30` (+ `.agents` mirror); ticket-frontier `SKILL.md:54`; `scheduler.md:76`; `claude-team.md:16`. | `frontier-scheduler.md:35` applied in-lane (parent added the path at integration); `./dev/mise run test:doctor` rc 0 on the edited file. The other six lines are owned by lane `compaction-40` (its `owned_paths` hold `frontier.toml`, both `ticket-frontier` copies and the `claude-team.md` review-model line): edits B-E and H below, recorded for that lane, not applied here. Owner: compaction-40. Disposition: applied (one line) and assigned (six lines). |
| 4 | P2 | Steering: this lane's `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS=6` sits under `frontier.toml:9` `max_live_agents = 8` and config.md:9 ("the harness allows 20"): the skill would count claims 7 and 8 as live while the harness queues them. | Recorded for lane `compaction-40` as edit I below (both files are in its `owned_paths`); the brief says record, not apply. Owner: compaction-40. Disposition: assigned. |
| 5 | P2 | Navigation: `.claude/AGENTS.md:5` lists five agent files, omits `frontier-scheduler`, and the five brief-only roster-v2 roles (upgrade intake, test author, test-contract check, security reviewer, cross-vendor reviewer) have no home. | Parent edit F below, against the merged line 5 (unchanged by ct35a). Owner: parent (`.claude/AGENTS.md` is excluded). Disposition: assigned. |
| 6 | P3 | Steering: two open lane records still name a Fable reviewer, `ct21-codex-imports.json:9` and `handoff-skills.json:9`; the 27 other matches are integrated or closed records of the reviewer that actually ran and stay as history. | Parent edit J below. Owner: parent (lane records are parent-owned). Disposition: assigned. |
| 7 | P3 | Steering: `codex-session-history/SKILL.md:37-39` and `antigravity-session-history/SKILL.md:70-72` (and their `.agents` mirrors) hand a large digest to "a synthesizer subagent (Fable, high effort)"; at spawn depth 1 a subagent running the skill has no `Agent` tool (sub-agents.md:427), so the step dead-ends for every lane agent. | Parent edit K below, one sentence per skill, both copies. Owner: parent (`.claude/skills/` and `.agents/` are excluded). Disposition: assigned. |
| 8 | P3 | Information access: the runtime proof that 2.1.300 accepts the new frontmatter is a `claude --debug` session with no `does not recognize or apply` line for these files (sub-agents.md:292); it needs a fresh session after the restart, which this lane cannot start. | Deferred, owner parent, admission condition: the user's restart onto 2.1.300. Command: `grep -c "does not recognize or apply" ~/.claude/debug/<session>.txt`; expected 0; record the rc beside D189. Finding 1 is the static half. Disposition: deferred with owner and condition. |
| 10 | P3 | Tool economy: the scratchpad directory is shared by every agent of one session. This retro's `git commit -F $scratchpad/commit-msg.txt` committed the right files under the handoff-skills retro-writer's message, which had overwritten the same path between two calls; the commit was amended from `commit-msg-roster-v2.txt`. | Parent edit M below (one line in `docs/agents/claude-team.md`, excluded here). Owner: parent. Disposition: assigned. |
| 9 | P3 | Steering: R12c §7.3 also proposes the record-file brief line for `doc-writer.md`, `omitClaudeMd` for the extractor and a refute-first reviewer stance; none is in the lane's `delivers` or D189's text. | Rejected for this lane: outside the allocated contract (lane record `delivers`); the parent allocates it if wanted. Disposition: rejected, reason given. |

Coding standards: none — the lane diff is configuration and prose; the new test follows
`.claude/rules/dev-tests.md` (probe files on disk are the seam, suites run under `python3 -I`, no
network, no fixture secrets). Tool economy: finding 10, and one closed by finding 2 — the brief named the
integration tip by SHA and the SHA was stale within minutes; merging the branch by name costs nothing
and, once edit G lands, both forms pass, so no prose rule is added (a rule restating a fixed gate is a
cache). The 89 KB R12c draft was read by line range, check logs went to the scratchpad and only tails
were read. No-ops: none — each frontmatter line changes runtime behaviour, and the retro-writer
sentence replaces a harness instruction the role would otherwise follow. Navigation is finding 5,
automated checks are findings 1 and 2, steering is findings 3, 4, 6, 7 and 9, tool economy is finding
10, information access is finding 8.

## Parent edits (exact text)

A. Applied in-lane: `dev/test_doctor_agents.py` is committed on `claude/roster-v2`; the parent adds
`dev/test_doctor_agents.py` and `.claude/agents/frontier-scheduler.md` to the lane record's
`owned_paths` at integration (D189). Nothing to copy.

B. (owner compaction-40) `.planning/2026-10-10-marketplace-macos-reflection-scaffold/frontier.toml`
line 34: replace `review = { model = "fable", effort = "high" }` with
`review = { model = "opus", effort = "high" }            # D189: model diversity from the cross-vendor reviewer`.

C. (owner compaction-40) `.claude/skills/ticket-frontier/references/model-policy.md` (and its
`.agents/skills/` mirror, byte-identical today): line 13 becomes
`| review | \`reviewer\` | opus | high | 1,000,000 | 500,000 | \`policy.review\` |`;
line 30 becomes `- (a) its kind is \`retro\`, \`synthesis\` or \`design\` (\`policy.<kind>\`);`.

D. (owner compaction-40) `.claude/skills/ticket-frontier/SKILL.md` (and mirror) line 54: replace
`` `reviewer` (Fable, cold, fixed point `base_sha`)`` with
`` `reviewer` (Opus, D189; cold, fixed point `base_sha`)``.

E. (owner compaction-40) `docs/agents/claude-team.md` line 16 becomes
`| reviewer | Opus | high | nothing | via the parent's brief | disposition PASS, PASS-with-P2/P3 or FAIL with unrun checks named |`.
Optional: `frontier.py:61` `FABLE_KINDS` keeps `"review"`; it only exempts that kind from
escalation and the dispatcher never computes it, so no behaviour changes either way.

F. (owner parent) `.claude/AGENTS.md` line 5 becomes:

```markdown
- `agents/`: role definitions (implementer, doc-writer, reviewer, retro-writer, extractor,
  frontier-scheduler); `dev/test_doctor_agents.py` checks their frontmatter. Five roster-v2 roles
  are briefs on these files, not files (D189, R12c §1.1); pass `model` and `effort` on every Agent call:
  - upgrade intake: `frontier-scheduler`, Sonnet, high, after a mechanical collector; returns JSON
    on dependency and release changes (R-158, R-167, R-176).
  - test author: `implementer`, Opus, xhigh; writes the failing test at the agreed seam before the
    implementer round.
  - test-contract check: `reviewer`, Fable, medium; confirms each test asserts an external seam and
    fails without the change.
  - security reviewer: `reviewer`, Fable, xhigh, beside the reviewer on C++ units; covers every
    public-text write path (R-174); the receipt records the served model.
  - cross-vendor reviewer: `codex exec -s read-only -C <lane worktree>` or `codex review --base <base>`,
    GPT-6.1 Sol high, launched by the parent on C++ units; starts when Codex returns after 2026-10-19.
```

G. (owner parent) `dev/hooks/git_gate.py` and `dev/test_hooks.py`; apply both, then
`./dev/mise run test:hooks` (expected rc 0, 28 tests):

```diff
--- a/dev/hooks/git_gate.py
+++ b/dev/hooks/git_gate.py
@@ -84,6 +84,8 @@ def kind_at(repo, commit: str) -> tuple[str, str | None]:
     """Classify a commit by the refs pointing exactly at it; the integration branch wins,
     then a lane named by a lane record, then any lane ref."""
     sha = git(repo, "rev-parse", "-q", "--verify", f"{commit}^{{commit}}")
+    if sha and any(git(repo, "merge-base", "--is-ancestor", sha, branch) is not None for branch in INTEGRATION):
+        return "integration", None  # on an integration branch's history: a lane cut there has nothing to gate yet
     refs = (git(repo, "for-each-ref", f"--points-at={sha}", "--format=%(refname)", "refs/heads", "refs/remotes")
             or "").split() if sha else []
     kinds = [ref_kind(ref) for ref in refs]
--- a/dev/test_hooks.py
+++ b/dev/test_hooks.py
@@ -251,6 +251,17 @@ class GitGateCli(Scratch):
         self.assertIn(f"retro gate refused claude/z-w:\nRETRO GATE FAILED for .planning/{PLAN}/retros/z.md", out)
         self.assertNotIn("refused claude/x-y", out)

+    def test_merge_of_an_integration_sha_is_not_a_lane_merge(self):
+        """A lane cut at the integration tip has not diverged: merging that tip by SHA gates nothing, even
+        after the integration branch moves on and the lane ref is the only one left at the SHA."""
+        self.commit("main", "m1")
+        tip = self.git("rev-parse", "HEAD").stdout.strip()
+        self.git("branch", "claude/n-o", tip)
+        self.commit("main", "m2")
+        self.git("checkout", "-q", "claude/x-y")
+        rc, out = self.gate("merge", GIT_REFLOG_ACTION=f"merge {tip}")
+        self.assertEqual((rc, "claude/n-o" in out), (0, False), out)
+
     def test_merge_gate_classifies_the_merge_source(self):
         for action in ("merge main", "merge origin/main", "merge --no-ff codex/marketplace-native-onboarding"):
             self.assertEqual(self.gate("merge", GIT_REFLOG_ACTION=action)[0], 0, action)
```

H. (owner compaction-40) `.claude/skills/ticket-frontier/references/scheduler.md` line 76 (and
mirror): replace `baseline file → one lane, Fable reviewer, no parallel sibling.` with
`baseline file → one lane, Opus reviewer (D189), no parallel sibling.`.

I. (owner compaction-40) `.planning/2026-10-10-marketplace-macos-reflection-scaffold/frontier.toml`
line 9 becomes
`max_live_agents = 6                 # hard cap on every live agent this skill has claimed (Q4); equals env CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS in .claude/settings.json (D189)`
and `.claude/skills/ticket-frontier/references/config.md` line 9 (and mirror) becomes
`| \`max_live_agents\` | 6 | hard cap on every claim; equals the project env \`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS\` (D189), so no claim queues in the harness |`.
Verify with `./dev/mise run test:frontier` (no test asserts the value 8: `grep -n "max_live_agents" dev/test_ticket_frontier.py`).

J. (owner parent) lane records, line 9 of each:
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/ct21-codex-imports.json`:
`  "reviewer": "reviewer (fable, cold)",` → `  "reviewer": "reviewer (opus, high, cold, read-only; D189)",`;
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/handoff-skills.json`:
`  "reviewer": "reviewer (fable, high, cold, read-only)",` → `  "reviewer": "reviewer (opus, high, cold, read-only; D189)",`.

K. (owner parent) one sentence per skill, both copies (`.claude/skills/` and `.agents/skills/`):
`codex-session-history/SKILL.md` lines 37-39 become
`   chars: at spawn depth 0 hand it to a synthesizer subagent (Fable, high effort) with [references/brief-template.md](references/brief-template.md) and read the brief it returns; a subagent cannot spawn (depth 1, D189), so it reads the turn-final and git-commit sections itself and fills the same template.`
`antigravity-session-history/SKILL.md` lines 70-72 become
`   a synthesizer subagent (Fable, high effort) at spawn depth 0, with [references/brief-template.md](references/brief-template.md), and read the brief it returns; a subagent cannot spawn (depth 1, D189), so it reads the digest itself and fills the same template; the brief keeps the template's eight headings in order`
(the remainder of the original line 72, `and answers the user's specific questions inside them. Done when every`, follows unchanged).

L. (owner parent, after the restart) finding 8: run `claude --debug` once on 2.1.300, then
`grep -c "does not recognize or apply" ~/.claude/debug/<session>.txt`; record the rc beside D189.

M. (owner parent) `docs/agents/claude-team.md`, after the line that names the scratchpad or the lane
lifecycle's commit step, add: `Scratch files carry the unit id (`<unit>-commit-msg.txt`): the scratchpad is one directory for every agent of a session, so a generic name is overwritten by a sibling between two calls (roster-v2 retro, finding 10).`
