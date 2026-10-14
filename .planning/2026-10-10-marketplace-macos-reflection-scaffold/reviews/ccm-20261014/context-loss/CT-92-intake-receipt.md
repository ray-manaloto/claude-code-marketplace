# Requests intake receipt (D168, DL-216)

Repository ray-manaloto/claude-code-marketplace; gh identity sortakool (GITHUB_TOKEN). Checkout
codex/marketplace-native-onboarding at 3d5b181 when this receipt was written; this agent wrote no
repository file (the dirty files in `git status` belong to the parent).

## Result

- Parent: https://github.com/ray-manaloto/claude-code-marketplace/issues/111 (id 5854593141),
  label needs-triage, VERIFIED by `issue:create-verify`.
- Sub-issues: 24 created (#112-#135; R-171 added on the coordinator's note), all native sub-issues of
  #111, open, label needs-triage. Mapping: intake-map.tsv.
- `gh api repos/ray-manaloto/claude-code-marketplace/issues/111/sub_issues --jq length` -> 24, exit 0;
  the live sub-issue numbers equal the map; `sub_issues_summary` total 24.

## Route

`docs/agents/issue-tracker.md` forbids `gh issue create` directly, and CL4 decision C(2), which D168
adopts, names the qualified route. So creation used `./dev/mise run issue:create-preview|apply|verify`
with version 2 manifests (parent_number null for the parent, 111 for the sub-issues). The POST
carries `parent_issue_id`, so no separate sub_issues POST was needed or made. Each body ends with the
route's marker comment `<!-- marketplace-ticket:<id>:<body sha256> -->`.
Manifests: intake/parent.manifest.json, intake/subs.manifest.json (23), intake/subs2.manifest.json
(R-171). Journals (intents, attempts, bindings): intake-journal-parent/, intake-journal-subs/,
intake-journal-subs2/.

## Commands and exit codes (full log: intake/run.log, stderr: intake/run.log.err)

- `gh issue list --search "Requests intake in:title"` (state all) before creation: [] exit 0.
- `gh label list`: needs-triage present, exit 0. `./dev/mise run deps:check`: exit 0.
- gitleaks 8.30.1 `dir --config .gitleaks.toml --redact=100 intake/`: exit 0, no leaks, three times
  (titles and bodies; plus subs.manifest.json; plus R-171).
- Parent: preview exit 0. The first apply and verify were refused locally ("intent SHA-256
  mismatch", because the SHA argument included the deps-check stdout line); no attempt marker, no
  POST. Then apply printed UNRESOLVED and verify printed UNRESOLVED (exit codes not captured);
  #111 existed. A read-only diagnosis showed body, title, labels and parent-absent all matching
  (listing lag). The verify retry exited 0 with VERIFIED.
- Each of the 24 sub-issues: preview exit 0; apply exit 2 UNRESOLVED (one POST each); verify exit 0
  VERIFIED on try 1, or on try 2 after a transient "REFUSED: duplicate issue in listing" (exit 2;
  pagination shifted after the POST) for R-119, R-135, R-140, R-158 and R-166.
- No other GitHub writes.
