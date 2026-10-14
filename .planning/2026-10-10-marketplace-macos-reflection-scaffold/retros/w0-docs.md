# w0-docs retrospective: wave-0 documentation slices (W0-7, CT-02b and CT-23 doc slices)

Unit `w0-docs` (ticket W0-7 of C4, D15 and D26; documentation slices of CT-02b and CT-23).
Worktree `.claude/worktrees/w0-docs`, branch `claude/w0-docs-rules`, base `c21941f`
(allocated from `d420a7e`), reviewed SHA `4854db1`. Delivered: `claude-team.md` gains the
Integration, Hook composition and Context budget sections and the Roles restart rule;
`ticket-retro.md` opening paragraph carries the D15 rewrite; `.claude/AGENTS.md` lists the
project settings keys and the marketplaces split; `issue-tracker.md` gains `When a skill
says publish / fetch`; `skill-invocations.md` row 20 and `spec.md` lines 61 and 65 carry
their record corrections. Hook behaviour that does not exist at the base is marked with the
ticket it lands with (CT-02b, CT-16, CT-22a, CT-23).

Exits recorded by the writer (Sonnet 5.5, per the `4854db1` trailer): `tasks validate` rc 0
(56 tasks), `check` rc 0, `check:acceptance-baseline` rc 0 (19/19 hashes PASS),
`test:hooks` rc 0, `hk validate` rc 0, `git diff --check` rc 0, `retro:gate -- w0-docs`
rc 0. Cold review (Fable, read-only, `reviews/ccm-20261013/phase3/w0/w0-docs-review.md`):
**PASS-with-P2**, one P2 and five P3; the reviewer reran `tasks validate`, `check`,
`check:acceptance-baseline`, `git diff --check` and `retro_gate.py` at rc 0 and checked ten
truthfulness claims, all holding except the two repaired below (P3-1, P3-2).

## Review findings and dispositions

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks (review P2-1): `proposals/claude-takeover-spec/spec.manifest.json` `body_sha256` is `414db461…` (base `spec.md`); the head `spec.md` hashes `a659d80b0a81e441418c16dc5b763d14db5124bf165d3e143a234e81180eed9b`. R2 §Publication fixes 1 requires a rebuild after a body edit; the manifest is outside `owned_paths` and the lane's first retro did not record the cross-scope fix. | Proposed, owner merger at integration (before acceptance): `cd .planning/2026-10-10-marketplace-macos-reflection-scaffold/proposals/claude-takeover-spec && python3 -I build_manifests.py spec spec.manifest.json`, then `./dev/mise run check`. Verified here by a dry run into the scratchpad: build rc 0, output `body_sha256` equals the head `spec.md` hash above, manifest file SHA-256 `b851808773b8384dfbe8bd491af309180b5fc3aff6d1bebfbc871d8e5b2cb4db`; the worktree is untouched. The guardrail for the next lane is the mechanical rule in the audit table below. |
| P3 | Information access (review P3-1): `claude-team.md` said the budget hooks arrive with CT-22, the id C4 P2-19 used; the ticket ledger row and `lanes/w0-session-hooks.json` carry `prompt_hook` and `agent_gate` under CT-23, and `dev/doctor/budget.py` (`THRESHOLDS`) under CT-22a (`lanes/w0-doctor.json`). | Applied in this lane (owned path): the sentence now names CT-23, lane `w0-session-hooks`, and CT-22a for the thresholds module. Verification: `grep -n "CT-23" docs/agents/claude-team.md` shows the sentence; `grep -c "ticket CT-22 (" docs/agents/claude-team.md` is 0. |
| P3 | Information access (review P3-2): the Hook composition bullet named only `.planning/<PLAN_ID>/.mode`; the installed pwf `check-complete.sh` (3.24.0, lines 161-171) also arms on `$PWF_PLAN_ROOT/.mode`. Neither file exists at the base (`ls` rc 1 for both). | Applied in this lane (owned path): the bullet names both files and says "Leave both absent or set to `inject-smart`, never `gate`". Verification: `grep -n 'PWF_PLAN_ROOT/.mode' docs/agents/claude-team.md` matches once. |
| P3 | Information access (review P3-3): `lanes/w0-docs.json` `writer_model` says `opus (high)`; the `4854db1` trailer is `Claude Sonnet 5.5`. Lane records are parent-only (D8). | Proposed, owner parent, literal edit to `lanes/w0-docs.json`: set `"writer_model": "sonnet 5.5 (trailer of 4854db1; the brief asked opus (high), frontier model_policy.docs = sonnet)"`. Verification after the edit: `python3 -I -c 'import json;print(json.load(open(".planning/2026-10-10-marketplace-macos-reflection-scaffold/lanes/w0-docs.json"))["writer_model"])'`. |
| P3 | Navigation (review P3-4): `issue-tracker.md:57` used "wayfinder" with no definition or pointer; the seed Wayfinding block is absent (SYNTHESIS P2-21). | Applied in this lane (owned path): the bullet now says the Wayfinding block that `setup-matt-pocock-skills` writes above this heading defines the term when the user runs it. The definition itself is deferred with owner the setup re-run (user types `/mattpocock-skills:setup-matt-pocock-skills`). Verification: `grep -n "Wayfinding block" docs/agents/issue-tracker.md` matches once. |
| P3 | Information access (review P3-5): row 20's output cell carries the setup-session facts (writer deviation 1); S4 asked for separate rows and the lane owned row 20 only. | Proposed, owner parent (the record beyond row 20 is parent-owned): restore row 20's output cell to its base text (last cell of `git show c21941f:.planning/2026-10-10-marketplace-macos-reflection-scaffold/skill-invocations.md | sed -n 20p`) and append the two rows in "Literal edits for the parent" below. Verification: `./dev/mise run check` rc 0 and `git diff --check` rc 0 after the edit. |

## Lane audit (seven categories)

| Severity | Category and finding | Applied action and verification |
| --- | --- | --- |
| P2 | Automated checks: no check binds `spec.manifest.json#body_sha256` to `spec.md`, so a body edit inside `owned_paths` silently stales a manifest outside them (review P2-1 is the instance). `dev/check.py` has no manifest rule; `.github/workflows/development.yml` runs only `python3 -B dev/check.py`; CT-12 (wire every development test) is not allocated. | Proposed, owner parent after w0-doctor integrates (w0-doctor owns `dev/check.py` in wave 0; deferred at the e40a62a integration), destination `dev/check.py` (the `check` surface; `dev/` is excluded from this lane): the literal lines in "Literal edits for the parent". Verified in the scratchpad against this worktree: the rule raises `Spec manifest is stale` on the current manifest (rc 1) and passes on the rebuilt one (rc 0). Apply it after the P2-1 rebuild, else `check` fails by design. |
| P3 | Coding standards: a doc lane marks behaviour absent at its base with "lands with CT-xx" (writer deviation 4). The marker is only truthful when the id comes from the lane record or ticket ledger; this lane took CT-22 from a review document (C4 P2-19) and the ledger said CT-23. | Proposed, owner user (D47 pending in `task_plan.md` Decisions; D31 keeps that file `propose`), destination `CODING_STANDARDS.md` rule 5 (judgement rule): the literal sentence in "Literal edits for the parent". Interim: the retro-writer applied the rule by hand to the four markers in `claude-team.md` (CT-02b, CT-16, CT-22a, CT-23 each match a lane record or ledger row). |
| P3 | Steering/global guidance: `.claude/AGENTS.md` caches the `settings.json` key list, which the file itself answers (rule 10 of `CODING_STANDARDS.md`). | Kept, with a check arriving: the list states which keys are project versus personal, which `settings.json` cannot say (the reviewer confirmed the list equals the sorted keys), and `lanes/w0-doctor.json` W0-1 adds the test that the project-key rule admits exactly that set; the doc line and the test then drift visibly. Deferred verification, owner w0-doctor: `./dev/mise run test:doctor` rc 0 once CT-22a integrates. |
| P3 | Navigation: `claude-team.md` grew from 95 to 145 lines, so the hook and budget material sits in a file whose first screen is the roles table. | Deferred, owner parent: split Hook composition and Context budget into their own `docs/agents/` documents behind pointers when CT-23 lands the enforcing hooks; record it in the ticket ledger at that integration. |
| P3 | Information access: the lane record said the writer was Opus; the trailer says Sonnet 5.5, and the cold review on 103 added lines found one P2 (a cross-scope omission) and no content error. Doc lanes at `model_policy.docs = sonnet` are supported by this receipt; the brief's Opus request was the deviation. | Proposed, owner parent, destination `.claude/rules/planning-records.md` first bullet (`.claude/rules/` is excluded from this lane): the literal sentence in "Literal edits for the parent", so `writer_model` is bound to the trailer at receipt time. Verification after the edit: `./dev/mise run check` rc 0 (the rule file parses as Markdown with front matter). |
| P3 | Information access: `spec.md` and `skill-invocations.md` previously asserted the user typed `/grill-with-docs`; the transcript (`T:L21`) shows a pasted command. | Applied by the writer in `4854db1`: row 20 and the spec's Further Notes state the pasted mode; the reviewer confirmed both. The row split is review P3-5 above. |
| P3 | Automated checks: the budget numbers (400K, 500K, 550K, 650K) are stated in prose and, once CT-22a lands, in `dev/doctor/budget.py:THRESHOLDS`, so they can drift. | Deferred, owner w0-doctor (CT-22a): add a check that the table equals `THRESHOLDS`; until then `claude-team.md` is the source and CT-22a imports from it. |

Tool economy: none, because the writer edited each file in one scripted pass and ran the
gates once before and once after the tip merge; the retro-writer verified the manifest
rebuild and the proposed check in the scratchpad instead of touching excluded paths.
No-ops: none open; the writer removed the `ticket-retro.md` sentence that the skill's
standing request is the invocation authority rather than rewording it, and every
prohibition stands with a positive target (`--no-ff`, `retro:gate` by hand, `.mode` absent
or `inject-smart`).

## Literal edits for the parent (outside `owned_paths`)

1. Manifest rebuild (review P2-1), before acceptance:
   `cd .planning/2026-10-10-marketplace-macos-reflection-scaffold/proposals/claude-takeover-spec && python3 -I build_manifests.py spec spec.manifest.json && cd - && ./dev/mise run check`.
   Expected: `body_sha256` `a659d80b0a81e441418c16dc5b763d14db5124bf165d3e143a234e81180eed9b`.
2. `dev/check.py`, inside `check()` after the plugin dependency loop and before `if baseline:`:

   ```python
       for manifest in sorted((ROOT / ".planning").glob("*/proposals/*/spec.manifest.json")):
           body = json.loads(manifest.read_text())["tickets"][0]["body_sha256"]
           if body != hashlib.sha256(manifest.with_name("spec.md").read_bytes()).hexdigest():
               raise ValueError(f"Spec manifest is stale, rebuild it: {manifest.relative_to(ROOT)}")
   ```

   Apply after edit 1; `./dev/mise run check` rc 0 then binds the manifest.
3. `CODING_STANDARDS.md`, append to rule 5: `A document that describes behaviour absent at
   its base names the ticket that lands it, with the id read from the lane record or the
   ticket ledger, not from a review document.`
4. `.claude/rules/planning-records.md`, append to the first bullet: `` `writer_model` names
   the model in the lane's commit trailer; when the brief asked for another model the
   parent corrects the record at receipt and the retro says which model wrote. ``
5. `lanes/w0-docs.json`: `"writer_model": "sonnet 5.5 (trailer of 4854db1; the brief asked
   opus (high), frontier model_policy.docs = sonnet)"`; also set `"review": "PASS-with-P2
   (reviews/ccm-20261013/phase3/w0/w0-docs-review.md)"` and `"retro":
   "retros/w0-docs.md"` at the parent's next records commit.
6. `skill-invocations.md` (review P3-5): restore row 20's output cell to its base text
   (last cell of `git show c21941f:.planning/2026-10-10-marketplace-macos-reflection-scaffold/skill-invocations.md | sed -n 20p`)
   and append these rows after row 20 (setup session is transcript `T0`, 2026-10-13):

   ```
   | setup session (T0, 18:39:06Z) | `domain-modeling` | `skills/engineering/domain-modeling/SKILL.md` | `7b925d7b1e341a2eeae33ad68a8a8c0ab889a38ddd22a7598e4c240e5a7556a3` | typed by user (`/mattpocock-skills:domain-modeling`); no-op | user | none |
   | setup session (T0, 18:39:23Z) | `setup-matt-pocock-skills` | `skills/engineering/setup-matt-pocock-skills/SKILL.md` | `f148858ffb7f63c03c06fca06e6fdb1d91a35c6b293244b8fdfacd5f4cc028c4` | typed by user (`/mattpocock-skills:setup-matt-pocock-skills`); answered "already fully set up" (`T0:199`); `SKILL.md` read from the marketplace checkout at `49dd158` | user | none; the Wayfinding block is still absent (SYNTHESIS P2-21, review P3-4) |
   ```

## Retro-writer checks (worktree, `VIRTUAL_ENV` unset)

Recorded after the repairs above, on the lane branch (Fable, 2026-10-14):
`python3 -I dev/retro_gate.py --unit w0-docs` rc 0 (selectors: none),
`./dev/mise run retro:gate -- w0-docs` rc 0, `./dev/mise run check` rc 0 (91 tests OK),
`./dev/mise run check:acceptance-baseline` rc 0 (19/19), `./dev/mise tasks validate` rc 0
(56), `git diff --check` rc 0. The ledger line `ledger-w0-docs.jsonl` event `retro`
repeats these exits; the receipt names the commit SHA. Not run by the retro-writer:
`test:hooks`, `hk validate` (no hook or pkl file changed since `4854db1`),
`check:research` (parent-run), runtime gates.
