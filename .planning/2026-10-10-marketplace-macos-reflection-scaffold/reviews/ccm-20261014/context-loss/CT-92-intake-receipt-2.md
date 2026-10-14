# Requests intake receipt 2 (D168; R-172, R-173, R-174)

Repository ray-manaloto/claude-code-marketplace; gh identity sortakool (GITHUB_TOKEN). Checkout
codex/marketplace-native-onboarding at 53a05eb in the main checkout, run from the repository root with
`VIRTUAL_ENV` unset. Same route and manifest shape as `CT-92-intake-receipt.md`; map rows appended to
`CT-92-intake-map.tsv`.

## Result

- Sub-issues of #111 (native, open, label needs-triage): R-172 -> #136, R-173 -> #137, R-174 -> #138.
- `gh api repos/ray-manaloto/claude-code-marketplace/issues/111/sub_issues --paginate`: exit 0, 27
  children (24 before), #136-#138 listed open. `gh api .../issues/<n>/parent --jq .number`: 111 for
  each, exit 0.
- Live title and body of each issue (`gh issue view <n> --json title,body,labels,state`, exit 0)
  are byte-identical to the scanned outbound files.
- task_plan.md Open requests: `issue: none yet` replaced with `issue: #136`, `#137`, `#138`.

## Public text (D144, D148, D171)

Titles and bodies follow the #112-#135 pattern (`R-NNN: <summary>`; body, tracker line, evidence
line, route marker). R-172 says only "An owner-user action tracked in the private plan (D148)." and
has no tracker line; R-173 and R-174 carry the parent's wording verbatim. No TR path, name, stamp or
domain word; no secret or key name.

| R-id | issue | manifest body_sha256 | live body sha256 (with marker) |
|---|---|---|---|
| R-172 | #136 | 15476b5e92c7b9781d2158ec8675f6bc0a5b0897e48a9aedd6b99d6b65fb55e9 | 7ce55284f3c539204bb0cba5969038404175f0391fd8f7443374c63e24386212 |
| R-173 | #137 | 647a2efd7a9cb6f6032923f00c54df9038e738fc1386881bf8596aeb78a772f3 | 2bd04a641429f05a3bea3b9a752ec20a00f134560e52af27ad5e5c2b44f2da1b |
| R-174 | #138 | 23e4a1e6343343347f97cbdce583aa8c34e5bf0885933d5ac3fb93c96c6a17e7 | 62663a501198d3c1f62e039d44ebfad530ad56524b714057cc0a4c1dd91d8cfb |

## Commands and exit codes (session scratchpad: intake-174/ outbound text and manifest, intake-174-journal/ intents, attempts and bindings, intake-174-run/ run.log and run.log.err)

- Read-only before creation: `gh issue view 125` and `gh issue view 135` (pattern), exit 0;
  `gh issue list --state all --search "R-172 OR R-173 OR R-174 in:title"`: [] exit 0;
  `gh api .../issues/111/sub_issues --paginate --jq length`: 24, exit 0.
- Pre-apply scan of every outbound title, body (with marker) and the manifest
  (intake-174/subs3.manifest.json, version 2, parent_number 111, 3 tickets):
  `.mise/installs/aqua-betterleaks-betterleaks/1.9.0/betterleaks dir intake-174/ --config .gitleaks.toml --redact --no-banner`: exit 0, no leaks.
- Per ticket, `./dev/mise run issue:create-preview|apply|verify --manifest-file intake-174/subs3.manifest.json <R-id> intake-174-journal [<intent sha256>]`
  (intent SHA taken from the last stdout line, so the deps:check line no longer pollutes it):
  - R-172: preview 0 (intent 356929f7b77a4bce4a47d8f6dba2d327a474d7a441c868373f2cbb2568547abe); apply 2
    UNRESOLVED (one POST); verify try 1 exit 2 "REFUSED: duplicate issue in listing" (pagination
    shift after the POST, as in receipt 1); verify try 2 exit 0 VERIFIED.
  - R-173: preview 0 (intent c65ec5e710f519a5057b33d782de05ede946dda186eb5a337d6ef76c2a74817d); apply 2
    UNRESOLVED (one POST); verify try 1 exit 0 VERIFIED.
  - R-174: preview 0 (intent 76dd2cdbaf2329b8a93737e4370bec9e637c90b07411565d2309be23ec5062ca); apply 2
    UNRESOLVED (one POST); verify try 1 exit 0 VERIFIED.
- Post-apply rescan of the live titles and bodies (intake-174-live/):
  `betterleaks dir intake-174-live/ --config .gitleaks.toml --redact --no-banner`: exit 0, no leaks.
- No other GitHub writes (three issue POSTs carrying `parent_issue_id`; no sub_issues POST, no edit,
  comment or label change).
