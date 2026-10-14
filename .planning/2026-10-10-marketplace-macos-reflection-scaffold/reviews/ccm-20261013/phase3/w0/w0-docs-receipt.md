# w0-docs receipt (COMPLETE)

Branch `claude/w0-docs-rules`, final SHA `4854db12bfc30f21c2bc5501e6e731dd6c799681`, base `c21941f`. Tip `codex/marketplace-native-onboarding` is still `c21941f` (`git merge --no-ff` printed "Already up to date", no merge commit; the live gate did not deny the literal command). `git status` clean.

Changed paths (insertions/deletions):
- docs/agents/claude-team.md +48/0 (Integration, Hook composition, Context budget, Roles restart rule)
- docs/agents/ticket-retro.md +5/-5 (D15)
- docs/agents/issue-tracker.md +11/0
- .claude/AGENTS.md +5/-2
- .planning/.../skill-invocations.md row 20 (1 line)
- .planning/.../proposals/claude-takeover-spec/spec.md lines 61, 65
- .planning/.../retros/w0-docs.md +30 (new), ledger-w0-docs.jsonl +1 (new)

Gate rcs (after commit): tasks validate 0, check 0, check:acceptance-baseline 0 (19/19), git diff --check 0, retro:gate -- w0-docs 0; test:hooks 0 and hk validate 0 (run before commit, tree bytes identical). No check:research, push or publish.

Item 9: `.git/info/exclude` holds `/.agent/` and the `settings.json.before-ct02` path; secrets line is `claude-takeover.md:13`.

Deviations: (1) setup-session facts folded into row 20's output cell, since owned scope is row 20 only (S4 asked for separate rows). (2) spec.md line 65 also corrects "user typed /grill-with-docs" to the pasted mode. (3) UI-mod sentence moved from line 61 to a CT-13 mention in line 65. (4) `.mode` is absent at the base, so the doc says "absent or inject-smart, never gate". Hook behaviour not at base is marked "lands with CT-02b / CT-16 / CT-22".

Unverified: Fable review pending; Opus brief vs Sonnet writer noted.
