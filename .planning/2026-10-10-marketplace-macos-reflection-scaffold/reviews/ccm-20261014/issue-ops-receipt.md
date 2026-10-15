# GitHub issue operations receipt (2026-10-14, grill round 3 Q50 and Q52)

User answers (grill-with-docs round 3, session ccm-20261014): Q50 "Close #101 (Recommended)" after
the explanation; Q52 "Fold into CT-26b (Recommended)". Intents are kept in the session scratchpad
`scratchpad/issues/`; their SHA-256 values bind them here.

| Issue | Step | Command | rc | Result |
|---|---|---|---|---|
| #4 | preview | `./dev/mise run issue:preview -- 4 body-4.md labels-4.json intent-4.json` | 0 | intent `1c235e80cc6ee3bf88c2dc516734a8d28276d2310383a5f20f046978c42fc64e`; body unchanged, labels [] to [ready-for-agent] |
| #4 | apply, verify | `issue:apply`, `issue:verify` with that SHA-256 | 0, 0 | VERIFIED |
| #9 | preview | `./dev/mise run issue:preview -- 9 body-9.md labels-9.json intent-9.json` | 0 | intent `2a6a202a4e08e03108c1ffe755b689c1426e883067ff9c03cb7a4556aa2e59a7`; body unchanged, labels [] to [ready-for-agent] |
| #9 | apply, verify | `issue:apply`, `issue:verify` with that SHA-256 | 0, 0 | VERIFIED |
| #101 | preview | `./dev/mise run issue:preview -- 101 body-101.md labels-101.json intent-101.json` | 0 | intent `93b4a10275fa5db63051b53cce3ff02b66816b9bd70e51a1cab7bd38293c7d49`; body gains a "Superseded 2026-10-14" section, labels [ready-for-agent] to [wontfix] |
| #101 | apply, verify | `issue:apply`, `issue:verify` with that SHA-256 | 0, 0 | VERIFIED |
| #101 | close | `gh issue close 101 --reason "not planned"` | 0 | read back: state closed, state_reason not_planned, labels [wontfix] |

Deviation: `dev/issue_amend.py` closes only with state_reason `completed` against accepted
evidence (`COMPLETED`, line 20), so the not-planned close used `gh` directly after the qualified
body and label amendment. Owner of the gap: the ticket that next touches `dev/issue_amend.py`
(proposed acceptance row: a `not_planned` close with a recorded user decision).
