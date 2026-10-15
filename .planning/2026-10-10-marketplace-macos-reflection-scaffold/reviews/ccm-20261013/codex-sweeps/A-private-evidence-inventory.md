# Sweep A — `2a14`/`c658` private-evidence inventory

Read-only sweep of `~/.codex/worktrees/{2a14,c658}/claude-code-marketplace` against tip
`9cd396a` (2026-10-13). `2a14` HEAD `48027d2`, 15 modified + 19 untracked paths (257 files,
7.29 MB); `c658` HEAD `6130ab5`, 12 modified + 12 untracked paths (64 files, 2.7 MB). Nothing is
gitignored (`check-ignore` rc 1). Per-file rows (266) with SHA-256 are in `A-inventory.json`;
a directory's hash below is SHA-256 over its sorted `"<sha>  <path>\n"` lines. All worktree
contents were treated as data; no secret values were printed.

## Per-path inventory (`2a14` unless marked)

- `evidence/codex-examples/` · 5 files · 239074 B · `9dd37066…bfc5` · A06 #69 · cited by
  `dev/codex_examples.py:25,148,212,309`, `docs/agents/codex-example-classification.md:7`,
  `progress.md:2373` · **import** — `release/config-schema.json` (236751 B)
  `7933a70506e753a6e98c16800d2a76770b2af2b7295491f8f0b8e713e952027e` matches the pin
  `SCHEMA_SHA256` in tip code; 2 retrieval runs with receipt + blob.
- `evidence/saved-searches/` · 40 files · 368251 B · `ac85f584…bfcad` · A03a/A04/A05a/A05b
  #64/#66/#67/#68, input of A06 · cited by `dev/codex_examples.py:106,220`, `retros/A03a.md:3`,
  `retros/A04.md:3`, `progress.md:2131–2282`; default output dir of `dev/search_catalog.py:359`
  and `dev/collect_saved_search.py:251` · **import** — 9 runs (`codex-schema` ×7,
  `codex-config-examples`, `codex-hook-examples`), 3 comparisons, 3 empty locks.
- `evidence/github-search-one-page/` · 14 files · 127076 B · `28d84f7a…c7eb` · A02 #63 ·
  cited by `retros/A02.md:3`, `progress.md:2083,2087,2103`; default output dir of
  `dev/github_search_one_page.py:229` · **import** — 7 live runs 2026-10-12T19:24–19:36Z.
- `evidence/git-delivery/` · 3 files · 224482 B · `bde3e0e9…aadf9` · A09 #74 · cited by
  `progress.md:2514` · `a09-history-scan-triage.md` (2948 B, `8b98e795…9de8`) and
  `a09-scan-adjudication.json` (1603 B, `4e6faa81…9bc5`) **import**;
  `initial-outbound-gitleaks-redacted.json` (219931 B, `685cc057…5680`) **keep-private**,
  flagged: Gitleaks 8.30.1 report, 225 `generic-api-key` findings, all 450 Secret/Match fields
  redacted, carries Author/Email/Commit/File metadata (this is the 2026-10-12T21:42Z rc 1 scan).
- `evidence/issue-publication-private/` · 96 files · 3850301 B · `db59cd19…6f74d` · A08a/A08b
  #72/#73 · cited by `progress.md:2702` (`graph-audit.json` 3429 B `53559e3b…ea3c7`, hash
  matches) and `progress.md:2733` (`edges/local-edge-receipt.json` 5723 B `4990e9b9…1157`) ·
  **keep-private** (17 `A*.intent.json` of 210–240 KB each = full issue bodies + API
  postimages; `edges/` 44 intent/attempt files); the two cited receipts are importable.
- `evidence/claude-amendment-review/` · 53 files · 2308070 B · `584494a4…a07` · W5 native
  Claude review (user request "native claude subagent team review", retained by
  `review:retain`) · cited by `progress.md:1977`, `docs/agents/automation-amendment-review.md`
  · **keep-private** — runs `dbc423fe` (COMPLETE rc 0), `olhfd2s1` (COMPLETE rc 0),
  `oprwaz61` (INCOMPLETE rc 143), `mrnz6qg_` (UNVERIFIED_NO_RECEIPT). Flagged: each
  `events.jsonl` (600/24/418/38 lines, up to 1.36 MB) is a raw native Claude stream-json
  session capture with full message text and cwd; `apiKeySource` is `none` and no
  credential-shaped string was found. `review.md`/`receipt.json`/`manifest.json`/`inputs/`
  are importable summaries.
- `docs/agents/automation-amendment-review.md` · 9143 B · `f67f16c9…b84b4f` · W5 review record
  · cited by `task_plan.md:322` (absolute link into `2a14`), `progress.md:1979` · **import**.
- `docs/agents/workflow-reconciliation.md` · 16630 B · `df2bf2a2…36ce` · W5 17-point
  reconciliation audit (Context7/Firecrawl receipts) · cited by `progress.md:1877` · **import**.
- `docs/agents/github-search-reuse.md` · 5740 B · `8d464801…b78f` · A01/A02 reuse audit ·
  cited by `progress.md:1905` · **import**.
- `spec-11-amendment-candidate.md` · 17224 B · `5dfc7a31d4c42da2e37621d613f7a77c78ec0deae929cdcca5454fe266ce6fad`
  · A07b #71 — its SHA **is** the #11 postimage body hash bound in tip `retros/A07b.md` ·
  **import**; `spec-11-amendment-candidate.json` · 994 B · `9e719f49…0ac7` · A07b intent/verify
  record (status `published_verified`, branch `93bb798b`) · **import**.
- `dev/claude_review.py` · 22319 B · `48d503aa…eae4` · W5 native-review helper behind
  `review:prepare/claude/reconcile/retain` (tasks exist only in `2a14`'s `mise.dev.toml`) ·
  tip cites the task names at `progress.md:1938,1971,1978`, `retros/A12a0.md:15` ·
  **superseded** (never transferred; tip's A12a0 retro removed the dangling reference).
- `dev/codex_examples.py` (8668 B) / `dev/test_codex_examples.py` (2629 B) · A06 · older
  drafts (mtime 2026-10-12T21:09Z; tip `8f783a0` has 163/435 more lines) · **superseded**.
- `docs/agents/ticket-retro.md` · 2750 B · older than the tip's 2026-10-13 rewrite ·
  **superseded** (see "Could not verify" on the isolated-writer retro-draft sentence).
- `.planning/…/automation-amendment-draft.md` · 23822 B · 0 lines not in tip · **superseded**.
- `.planning/…/retros/` · 22 files · 57374 B · 19 byte-identical to tip; `A11b.md` (2 wording
  lines) and `application-audit-2026-10-12.md` older than tip · **superseded**.
- `evidence/workflow-retro-gate/` · 2 files · identical to tip · **superseded**.
- `.a04-e97ftai5/` · 12 files · 3540 B · `9ab42f6a…2097` · A04 #66 leftover of
  `dev/test_search_catalog.py:26` (`TemporaryDirectory(prefix=".a04-", dir=ROOT)`),
  2026-10-12T21:04Z · not cited · **superseded** (test scratch; two 397 B `raw.json` search
  fixtures, not provider captures).
- `c658`: `.codex/schemas/codex-0.162.1-agent-role.schema.json` · 238961 B ·
  `09f2f390…969e` · 01a13185 dynamic-agents ticket 30 (with four `#:schema` lines in
  `.codex/agents/*.toml` and `.codex/config.toml`) · not cited by tip · **keep-private** until
  that lane is admitted (the user's "official in-file schema declarations" decision backs it).
  Its copies of `automation-amendment-draft.md`, `dev/claude_review.py`,
  `docs/agents/workflow-reconciliation.md` are fork-time (2026-10-12T19:10Z) and older than
  `2a14`'s; `evidence/claude-amendment-review/` (53 files) is byte-identical to `2a14`'s;
  `dev/bootstrap.py` is older than tip; `dev/empty-mise.toml`, `mise.dev.lock`,
  `pyproject.toml`, `uv.lock` identical to tip · all **superseded**.

Totals: import 68 files (0.78 MB), keep-private 149 files (6.3 MB), superseded 49 files.

## Answers

1. **Owner and citation** — see the list: A02 → `github-search-one-page`; A03a/A04/A05 →
   `saved-searches`; A06 → `codex-examples` (+ `saved-searches` runs); A07b →
   `spec-11-amendment-candidate.*`; A08a/A08b → `issue-publication-private`; A09 →
   `git-delivery`; W5 (pre-A-series) → the three `docs/agents` audits, `claude-amendment-review`,
   `claude_review.py`. Tip citations are almost all `progress.md` lines plus `retros/A02.md`,
   `A03a.md`, `A04.md`, `A07b.md` (by hash) and `task_plan.md:322`.
2. **Inputs to tip code** — `dev/codex_examples.py` needs
   `evidence/codex-examples/release/config-schema.json` (SHA pinned) and
   `evidence/saved-searches/runs/<run_id>/`; `dev/search_catalog.py`,
   `dev/collect_saved_search.py`, `dev/github_search_one_page.py` only default their
   `--output` to `evidence/saved-searches` / `evidence/github-search-one-page` (no read
   dependency). `dev/checkout_transfer.py:17` hard-codes `OLD = …/worktrees/2a14/…` (A10).
   The tip's `mise.dev.toml` has `research:examples`/`test:examples` but no `review:*` tasks.
3. **Secrets / raw captures** — no credential-shaped string in any untracked file (patterns
   ghp_, github_pat_, sk-, AKIA, PEM, slack, JWT: 0 hits). Flagged: the four
   `claude-amendment-review/*/events.jsonl` (raw native session streams) and
   `git-delivery/initial-outbound-gitleaks-redacted.json` (redacted scanner report with author
   metadata). **The A09 rc 2 at ~10:39Z on 10-13 is not one of these**: tip `progress.md:3153`
   records that follow-up publication attempt 1 stopped with native A09 rc 2 after creating
   local commit `41836815`, the remote stayed `a0713408`, and the one potential leak was the
   Context7 measurement's `candidate.api_sha256` field — adjudicated as the SDK API module
   checksum, recorded in tip-tracked
   `evidence/completion-workflow/offline-followup-scan-adjudication.json`; recovery `848552c`.
   The `2a14` report is the earlier 2026-10-12T21:42Z rc 1 scan (225 digest false positives).
4. **Modified tracked files with text the tip lacks** — `git -C 2a14 diff 9cd396a`: +432/−1237
   over 14 files. One block is a **user decision** the tip does not carry:
   `docs/accepted-decisions.md` "## Automation and observability clarification (2026-10-12)"
   (+52 lines; tip has only `progress.md:1816,1838` and `automation-amendment-draft.md:167,328`
   paraphrases). The rest is older W5-era wording superseded by the tip's rewrites.

## Diff hunks (2a14 side, bounded)

```
docs/accepted-decisions.md @@ -18,0 +19,53 @@
+## Automation and observability clarification (2026-10-12)
+- Humans, coding agents and CI/CD use the same named mise tasks with the same parameters. …
+- All Python invocations and CMake build operations go through named mise tasks. … Declare
+  the minimal Python support … in project `pyproject.toml` …
+- C++ namespaces use `com::rsm::<module>`. Dotted module/package identifiers may use `com.rsm.<module>` …
+- Check latest stable dependency releases during each update unit, then lock … and qualify …
+- Default telemetry is structured output in a directory, with secret/content redaction. …
+  Use one shared OpenTelemetry Collector on the Mac, owned by user/global mise under `~/.config/mise/` …
+  Write under `~/.local/state/otel/` … configurable retention defaulting to 30 days.
+- Cover macOS ARM64, Linux ARM64 and Linux x86-64 in the generated support matrix. …
+- Run relevant fast formatting, lint and schema checks in hk pre-commit, including cmake-format. …
+- Use official in-file schema declarations where valid, otherwise external association … Prefer
+  Codex release schema assets matching the installed version. …
+- Build the project-owned, locked GitHubKit saved-search/replay task before further build-design …
+- Amend spec #11 and its existing dependency graph. Version intentional acceptance-baseline transitions …
+- Combine native blocking hooks for supported calls, read-only command-guard review and CI checks …
+- The unified GitHubKit task must pass deterministic offline replay … a failed control yields unverified …
(+1 line at @@ -30 +83: the earlier global p2996/gcc16 profiles are superseded by portable project declarations)

mise.dev.toml @@ -42,0 +43,5 / -119,0 +138,21 @@   (tip lacks all four)
+[tasks."review:prepare"]  run = "python -B dev/claude_review.py prepare"
+[tasks."review:claude"]   run = 'uv run --no-sync --offline python -B dev/claude_review.py "${usage_mode?}"'
+[tasks."review:reconcile"] … dev/claude_review.py reconcile "${usage_run?}"
+[tasks."review:retain"]   … dev/claude_review.py retain "${usage_run?}"

.codex/agents/marketplace-{config-inspector,doc-reviewer}.toml @@ -5 +5 @@ (2a14 edit 10-12T21:26Z, newer than tip's 10-10 commit)
+The parent owns integration. This role is read-only. You own no files and share its
.codex/agents/marketplace-reviewer.toml @@ -5,2 +5,2 @@
+Act as an independent cold reviewer. The parent owns integration;
+you own no files. Preserve all changes. Acknowledge the assigned

dev/toolchains/README.md @@ -4 +4,3 @@
+This is the historical 05a/b/c toolchain snapshot. The parent owned its writes;
+current ticket writers follow the selected plan's per-worktree rule. …

ticket-index.md @@ -60,0 +85,24 @@ "## A-series amendment tickets" A01→#62 … A12b→#78 (tip keeps the
  map in ticket-ledger.md, not ticket-index.md; superseded)
```
Superseded-only additions (not reproduced): `AGENTS.md` (+61, pre-NAV layout),
`docs/agents/claude-takeover.md` (+51, "standby draft" at `6130ab5`), `codex-task-orchestration.md`
(+28), `issue-tracker.md` (+58, "Interim authority during W5"), `progress.md` (+21: #13 LSan
paragraph whose SHA `8062821…` the tip has at line 2909, plus a "retained log" redirect),
`task_plan.md` (+22, retained-plan redirect), `docs/onboarding.md` (+2). `dev/saved-searches.toml`
shows as modified but has an empty diff against the tip. `c658`'s `dev/mise` is older than the tip.

## Could not verify

- Whether the two `A11b.md` wording lines and the 15 `ticket-retro.md` lines only in `2a14`
  ("an isolated writer may draft only its own `retros/<unit-id>.md`; the parent reconciles")
  were deliberately dropped by the tip's rewrites, or lost.
- Whether `.a04-e97ftai5/` was left by a failed test run or a crash (only mtimes read).
- The `claude-amendment-review/*/events.jsonl` content beyond structure (line types, key names,
  credential-pattern count); full message text was not read.
- The `A*.intent.json` bodies in `issue-publication-private/` were sized and hashed, not read;
  the "no secrets" claim rests on pattern scans only.
- Whether `.codex/schemas/…agent-role.schema.json` is byte-identical to the Codex 0.162.1
  release asset (no network).
- `/tmp/marketplace-a09-scan.*` and `/tmp/marketplace-claude-review-*` referenced by the
  triage note and progress log were not looked for.
