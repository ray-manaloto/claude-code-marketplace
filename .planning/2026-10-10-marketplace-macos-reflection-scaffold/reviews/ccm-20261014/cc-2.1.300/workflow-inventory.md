# Dependency-upgrade workflow for offline docs and repo mirrors: inventory

Read-only survey, 2026-10-14. MP = this repository (branch `codex/marketplace-native-onboarding`, read at HEAD `10e0d66`; HEAD moved to `562094f` during the run, not by this agent);
TR = the private reference project (read as data only, no script run, no git command); DF = the dotfiles checkout
(`mise -C <dotfiles> tasks ls` / `tasks info`, read-only).

## 1. What exists in MP

| Piece | Where | What it does | Gap |
|---|---|---|---|
| OCI pin | `mise.toml:10`, `mise.lock:132-138` (both acceptance-baseline files) | `npm:@anthropic-ai/claude-code` 2.1.251 with `allow_builds` | moves only through a baseline transition (CT-08, R21 batch 4) |
| Dev locks | `mise.dev.toml` `deps:lock`, `deps:sync`, `deps:check`, `tools:prepare` (`dev/bootstrap.py`) | lock `mise.dev.toml` -> `mise.dev.lock` and `uv.lock`; digest-guards `mise.toml`/`mise.lock` so they cannot change (`dev/bootstrap.py:21,188`) | no OCI or plugin pin path, no outdated report |
| Research mirrors | `offline/research/<Rn>/` (untracked via `.git/info/exclude`; 3.5 GB, 173k files) | per-research `manifest.json` (items: `bytes`, `command_shape`, `exit_code`, `kind`, `local_path`, `retrieved_utc`, `sha256`, `source_url`) and `queries.jsonl`; R21 holds `releases/<owner>_<repo>__<from>..<to>.md` ranges, the Claude Code CHANGELOG, 4 clones | built by hand per research run; no task, no refresh, no index |
| Dependency study | `P/reviews/ccm-20261014/research6/R21-dependency-freshness.md` (+ R22 for Renovate/Dependabot) | 5 risk-ordered batches; Claude Code bump is batch 4 (frozen baseline); mise 24h npm cooldown finding | plan only; R-158 (#128) open |
| Corpus designs | Y4 (`P/reviews/ccm-20261013/phase4-prep/Y4-webclaw-offline-corpus.md`), C1 (`P/reviews/ccm-20261014/project-import/C1-research-corpus.md`) | `offline:refresh/query/research/verify`, `offline-sources.toml`, receipts under `evidence/offline/`, licence classes | tickets CT-33, CT-41..CT-47, C1-1..C1-5 not built |
| webclaw | global mise config (`github:0xMassi/webclaw` 0.6.23) | used for page fetches (research-workflow.md:13) | not pinned in `mise.dev.toml`/`mise.dev.lock` yet (Y4 proposed it) |

## 2. What exists only in TR (unmigrated; R-163 / #124 covers the generic parts)

- Package `src/dependency_intel/`: `outdated.py` (scan pins), `extractor.py` (webclaw tri-format crawls, depth-1 clones,
  `intel.json`, a hard-coded 44-row `DEPENDENCY_CATALOG`), `manager.py` (single and batch upgrade, OKF bundle writer),
  `pipeline.py` + `state_machine.py` (release-review state machine: start -> docs_synced -> research_fanned_out ->
  blast_radius_computed -> features_reviewed), `offline_doc_ai.py` (BM25-lite query), `openrouter.py` (synthesis), `watcher.py`.
- mise tasks: `deps:outdated`, `deps:intel`, `deps:diff`, `deps:research`, `deps:upgrade`, `deps:upgrade-all`,
  `docs:offline:lint`, `docs:sync`, `docs:ai:query`, `docs:ai:summary`.
- OKF linter `src/doc_generator/okf_lint.py`; JSON Schema `schemas/dependency_intel.json`.
- Outputs: `offline/<pkg>/reports/{index.md, 01-upgrade-report-<ver>.md, upgrade_report.json}` (18 packages) and
  `docs/reports/dependency_upgrades/{index.md, 01-batch-upgrade-summary.md, collection.json}`.
- Known defects (W2 #14, Y4 #1-#10): recommendations are hard-coded strings, verdicts such as `PASS`/`COMPATIBLE` are
  written without evidence, crawls are unbounded, pages are rewritten after fetch, no hashes, secrets copied into the
  crawler environment. C1 section 4 does not import the reports or the generator; only the pattern.

## 3. DF (dotfiles) tasks, read-only

`dependency-currency` (first-level mise and Python pins that are behind, JSON, rc is the verdict), `tool-currency`
(daily deep due-diligence on fast-movers), `tool-currency-check` (offline drift check, SessionStart), `outdated`,
`lint-delta`, `graphify-update` (lock bump with release-note receipt), `schema-vendor-refresh`/`-check`,
`research-fanout`, `research-saved-search`; global config `update:check`, `update:claude` (host updater). None writes
offline docs, repo mirrors or OKF reports for MP.

## 4. Missing in MP

1. A refresh task for docs and repo mirrors with a source manifest and hash-bound receipts (CT-33, CT-41, CT-42).
2. A release-intake generator: typed changelog -> JSON + OKF, plus the project cross-check (this scratch run is a
   prototype; it belongs in the C++ core or as a thin task per ADR 0008, not new Python).
3. An outdated report over all pins (`mise outdated --bump --json` and `uv tree --outdated` exist natively; R21 finding 7).
4. Staleness and upstream checks (CT-47), an OKF lint, and the explicit `minimum_release_age` (R-166, #130).
5. Automated update PRs (R-167, #131); Claude Code bumps would still need the baseline transition.

## 5. OKF

OKF = **Open Knowledge Format v0.2**, `SPEC.md` of `GoogleCloudPlatform/open-knowledge-format` (Apache-2.0; TR's
mirror is at commit `ad30107c31c06aec8a7d5636e0d1058118604e6f`). A bundle is a directory of Markdown files with YAML
front matter; `index.md` (optional, may carry only `okf_version: "0.2"` at the bundle root) and `log.md` are reserved;
every other `.md` is a concept whose only required key is `type`. Optional families: `title`, `description`,
`resource`, `tags`; provenance `sources[]` (`id`, `resource`, `title`, `author`, `usage_count`, `last_modified`) with
per-claim footnotes keyed by `sources[].id`; trust `generated {by, at}` and `verified [{by, at}]` (actor
`<producer>/<version>`, `human:<id>`, `process:<id>`); lifecycle `status` (draft|stable|deprecated) and `stale_after`.
Conformance (section 11): parseable front matter and a non-empty `type` on every non-reserved file.

TR's linter adds stricter rules: bundle `index.md` must declare `okf_version: "0.2"`, every file ends with exactly one
newline, every concept has `type`, relative `.md` links in `index.md` resolve. TR's own report docs deviate from the
spec (extra keys on `index.md`, `timestamp` instead of `generated.at`, no `sources`).

## 6. TR upgrade-report schema (field names)

- Per-package JSON `upgrade_report.json` (`UpgradeResponse` in `schemas/dependency_intel.json` minus the envelope):
  `package_name`, `ecosystem` (`MISE_NATIVE`|`PYTHON`), `old_version`, `new_version`, `test_passed`,
  `blast_radius` {`imported_symbols`, `affected_project_files`, `call_graph_references`, `ast_tool_used`,
  `compatibility_verdict`, `details` {`module_searched`, `files_scanned_count`}}, `key_learnings[]`, `actions_taken[]`,
  `github_usage_examples[]` {`feature_or_flag`, `query`, `repository`, `path_or_title`, `html_url`, `snippet`},
  `generated_at`. Envelope adds `exit_code`, `status`, `report_doc_path`, `report_json_path`, `timing`,
  `system_info`, `error`.
- Batch JSON `collection.json` (`UpgradeCollectionResponse`): `total_upgraded`, `all_passed`, `timestamp`,
  `upgrades[]` (`UpgradeCollectionItem`: `package_name`, `ecosystem`, `old_version`, `new_version`, `test_passed`,
  `key_learnings`, `actions_taken`, `github_usage_examples`, `report_doc_path`, `report_json_path`).
- Snapshot `intel.json` (`DependencyIntelSnapshot`): `package_name`, `ecosystem`, `current_version`, `latest_version`,
  `is_outdated`, `git_repo_url`, `git_commit_sha`, `repositories`, `source_categories`, `release_date`,
  `retrieval_timestamp`, `documentation` {`primary_doc_path`, `site_dir`, `crawl_dir`, `extractor`,
  `total_token_estimate`, `total_pages_count`, `source_urls`, `sitemap_urls`, `crawled_pages[]` {`relative_path`,
  `source_url`, `page_type`, `title`, `token_count`}}, `release_notes` {`raw_markdown`, `breaking_changes`,
  `new_features`, `bug_fixes`, `deprecation_warnings`}, `ast_blast_radius`, `credit_probe_status`,
  `vertical_metadata`, `snapshot_diff`.
- OKF Markdown: upgrade report front matter `okf_version`, `type: "report"`, `title`, `package`, `version`,
  `previous_version`, `timestamp`; sections Executive Summary, Key Learnings & Upstream Evolution, Actions Taken &
  Verification, Real-World GitHub Usage Examples, AST Blast-Radius Audit. Release review adds State Machine
  Transition Topology and Feature Adoption Recommendations (`Impact` HIGH|MEDIUM|LOW, `Description`, `Target Files`,
  optional diff).

This run's `releases.okf.md` keeps TR's front-matter keys and section names and adds the spec's `sources`,
`generated`, `status` and `stale_after`, with per-claim footnotes keyed by release.
