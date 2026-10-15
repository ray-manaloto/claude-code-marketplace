# Requests intake receipt 3 (D168; R-175, R-176, R-177)

Repository ray-manaloto/claude-code-marketplace; gh identity sortakool (GITHUB_TOKEN). Checkout
codex/marketplace-native-onboarding at 32e742c in the main checkout when filing started (20c0ef0, a
parent records commit, landed during the run), run from the repository root with `VIRTUAL_ENV`
unset. Same route and manifest shape as `CT-92-intake-receipt.md` and `CT-92-intake-receipt-2.md`;
map rows appended to `CT-92-intake-map.tsv`. Clears skills-audit findings S1 (`H.request-unlinked`)
and S2 (`H.request-unprojected`) of `dev/handoff.py check`.

## Result

- Sub-issues of #111 (native, open, label needs-triage): R-175 -> #139, R-176 -> #140, R-177 -> #141.
- `gh api repos/ray-manaloto/claude-code-marketplace/issues/111/sub_issues --paginate`: exit 0, 30
  children (27 before), #139-#141 listed open. `gh api .../issues/<n>/parent --jq .number`: 111 for
  each, exit 0.
- Live title and body of each issue (`gh issue view <n> --json title,body,labels,state`, exit 0)
  equal the scanned outbound files (the outbound body file adds one final newline).
- task_plan.md Open requests: `issue: pending` replaced with `issue: #139`, `#140`, `#141`; each line
  now cites its capture key (`p:5a8b9624`; R-177 also `p:8983a5df`, the roster prompt), and R-177
  cites D185.
- CL1-requests.jsonl: rows R-175 (transcript line 13451, compound root), R-176 and R-177
  (`compound_of` R-175), and R-178 (line 13576, the roster prompt, D185; its own row because it is a
  separate prompt, projected into the R-177 line).

## Public text (D144, D148, D171)

Titles and bodies follow the #138 pattern (`R-NNN: <summary>`; one-paragraph body, tracker line,
evidence line, route marker). No Support ticket id, no private path, no private project name or
domain word; no secret or key name.

| R-id | issue | manifest body_sha256 | live body sha256 (with marker) |
|---|---|---|---|
| R-175 | #139 | 2aa6876b38d294266e1bdd882253fa9beb74ae6dc3900634d55d7138ff766df9 | ea716c2a1b433c97fa62cba03bfa49aee40bb4c2f7e7817c0d728311a2dac56e |
| R-176 | #140 | a0107a8a80878d2a543783758cb7e9e0ff6e01e03bb09d24aac716f80290b50a | 30e00fed12b6802ad318990ed1fda4c8a4ed9fbe504732dedc1ed051082cdc8d |
| R-177 | #141 | 53fd95984cae2982a65b3e6858a3db23536d85819e50590dc9386ef863caa0b1 | a7b66b7b70929f2068dbea33caac0469ad7943273d0c6342d443ef16f92f5fb6 |

## Commands and exit codes (session scratchpad: intake-177/ outbound text and manifest, intake-177-journal/ intents, attempts and bindings, intake-177-run/ run.log and per-step stdout and stderr)

- Read-only before creation: `gh issue list --state all --search "R-175 OR R-176 OR R-177 in:title"`:
  [] exit 0; `gh api .../issues/111/sub_issues --paginate --jq length`: 27, exit 0;
  `gh issue view 138` (pattern): exit 0; `gh label list --search needs-triage`: present, exit 0.
- Pre-apply scan of every outbound title, body (with marker) and the manifest
  (intake-177/subs4.manifest.json, version 2, parent_number 111, 3 tickets), through
  `git_delivery.scan_config` (tracked rules plus the private rule; private rule loaded: true):
  betterleaks 1.9.0 `dir --redact=100 --report-format=json` over 7 files: exit 0, 0 findings.
  Each preview also ran the route's own `issue_amend.scan` before any request.
- Per ticket, `./dev/mise run issue:create-preview|apply|verify --manifest-file intake-177/subs4.manifest.json <R-id> intake-177-journal [<intent sha256>]`
  (intent SHA from the last stdout line):
  - R-175: preview 0 (intent 83cf465eeb59622950866b4a64bfbac08c6fc9aae19aa3420af6bde939ce06fc); apply 2
    UNRESOLVED (one POST); verify try 1 exit 0 VERIFIED (issue id 5857572179).
  - R-176: preview 0 (intent 32319412e9e8a3ef265098f62fb101509daf553646a76171d3884bb40c404dc1); apply 2
    UNRESOLVED (one POST); verify try 1 exit 0 VERIFIED (issue id 5857576675).
  - R-177: preview 0 (intent 8aa255e333eace0f8c34146f5f1d1c4e81abe04f7472efc6f9ce6869f8ca1bc9); apply 2
    UNRESOLVED (one POST); verify try 1 exit 0 VERIFIED (issue id 5857580457).
- Post-apply rescan of the live titles and bodies (intake-177-live/, 6 files) through `scan_config`:
  exit 0, 0 findings.
- No other GitHub writes (three issue POSTs carrying `parent_issue_id`; no sub_issues POST, no edit,
  comment or label change).

## Captured requests (`python3 -I dev/handoff.py check --json`, `VIRTUAL_ENV` unset)

- Before: exit 2; `requests.captured` 36, `unprojected` 11, `unlinked` 3 (R-175, R-176, R-177).
- Projected in task_plan.md (key on the R line): p:5a8b9624 (R-175 to R-177), p:8983a5df (R-177).
- Rows appended to the untracked `dispositions.jsonl` (state directory, not committed), using the
  file's existing values:
  - `not-a-request` (harness task notifications): p:1942be91, p:165e6687, p:a6095da2, p:e91a5dc5,
    p:5fb6b102.
  - `not-a-request` (a lane's agent message, captured during this run): p:a5a28704.
  - `decided` (AskUserQuestion answers): p:J14H6cuU (D182), p:y1rjD9MB (D182 round, a fork's
    question, acted on by that fork), p:GzbNBMiW (D183), p:zhxP5VjQ (D186).
- After: exit 2; `captured` 37, `unprojected` 0, `unlinked` 0; no `H.request-*` finding. Remaining
  findings, not fixed here (`dev/handoff.py write` regenerates them): two `H.handoff-stale-sha` (P1),
  `H.head-not-remote` (P1), `H.agents-unconfirmed` (P2), `H.mode-not-inject-smart` (P3).
