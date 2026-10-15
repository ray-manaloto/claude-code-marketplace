# C1: research corpus import (dotfiles, knowledge-base, TR)

Agent C1 (session `ccm-20261014`), 2026-10-14, read-only. Scope: offline documentation mirrors, cloned
repositories, documentation, blogs and articles, research reports and research runs in DF
(`/Users/rmanaloto/dev/github/ray-manaloto/dotfiles`), KB (`/Users/rmanaloto/dev/github/ray-manaloto/knowledge-base`)
and TR (`<TR>`), and how each lands in MP. TR's private documents
(`original/`, `generated/updated_*`) are out of scope (D81) and were not opened. P = MP's
`.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.

Method: `du -sh`; `git log`, `git ls-files`, `git rev-parse`, `git config --get`, `git sparse-checkout list`
on the projects and their clones; two scratch parsers run with `python3 -I` over KB's 99 `sources/*.manifest`
files and TR's 43 `offline/*/intel.json` files; a licence-file classifier over every clone's `LICENSE*`/`COPYING*`
at its checked-out commit. No network, no project script, task or hook was run. Builds on Y4, Y5 (licence
classes, §4), W1, W2, F2 Part A, and the sibling import reports DF-A, DF-B and KB-A (rows they own are cited,
not repeated).

Headline numbers: the three projects hold about 14.8 GB of research bytes (KB `sources/` 11 GB, TR `offline/`
3.2 GB, DF 0.6 GB) plus 6.4 GB of derived graphs (KB `graphify-out/` 5.8 GB, DF 587 MB). Fetched fresh as
sparse, blob-less, pinned rows, the part MP needs is on the order of 1 GB. Almost everything is
re-fetchable; only own-authored reports and runs, video transcripts, one auth-walled article and pages that
have since moved need an archive path.

## 1. Inventory

### 1.1 Project heads

| Project | HEAD (`git log -1`) | Branch | Dirty entries | Remote | Whole checkout (`du -sh`) |
|---|---|---|---|---|---|
| DF | `7744a9c6` 2026-10-13 "fix(hooks): close literal admission and settlement gaps" | detached | 2 | `git@github.com:ray-manaloto/dotfiles.git` (visibility not checked: no network) | 121G (115G is `.claude/worktrees/`) |
| KB | `f086f731` 2026-10-05 "chore/mintlify scrub (#878)" | `main` | 5 | `git@github.com:ray-manaloto/knowledge-base.git`, public with no licence per its own report (`docs/research/reports/research-corpus-licensing.md:16`, 2026-08-02; not re-checked) | 49G (35G is `.claude/worktrees/`) |
| TR | `dea1b59` 2026-10-11 | `feature/offline-gaps-and-deep-research` | 25 | none (`git remote -v` is empty) | 4.7G |

### 1.2 Collections

Licence class follows Y5 §4: **private** = mirror only, never committed or republished (proprietary, all
rights reserved, site terms, unknown, non-commercial, leaked); **committable** = OSI or Creative Commons
licence that permits redistribution, with its notice obligations. "Own" = authored by the user's agents.

| Id | Path | `du -sh` | Files and format | Provenance recorded | Dates | Class |
|---|---|---|---|---|---|---|
| DF-1 | `docs/research/kb/raw/` | 11M | 867 tracked files in 43 top-level entries (bundles and single pages): Markdown pages, `fetch.tsv`, `INDEX.md`, `.ts`, `.jsonl` | some bundles have `INDEX.md` (url, file, rc, bytes, method; `mise-dotfiles-2026-09-29/INDEX.md:3-5`) or `fetch.tsv` (http code, bytes, file, url); single `src-*.md` pages have none; no sha256 anywhere | first 2026-07-25, last 2026-10-05 | mixed: Claude Code pages and jdx.dev posts private; mise docs (414 pages, firecrawl) and herdr docs committable upstream |
| DF-2 | `docs/research/kb/reports/` | 26M | 1,291 tracked Markdown reports; 1,266 under `agents/` (cold reviews, session audits, handoff and Codex review lanes, 69 named `*research*`), 26 top-level follow-ups | author and date in prose; claims cite paths, never hashes | 2026-07-25 to 2026-10-12 | own |
| DF-3 | `docs/research/runs/` | 54M | 29 run directories, 92 tracked files (1.8 MB); `codex-0.161.0-settings-audit/` is 52 MB with 0 tracked files and its own `SHA256SUMS` | `report.md`, inventories, ledgers | 2026-07-10 to 2026-08-14 | own |
| DF-4 | `docs/research/mintlify-cache/` | 3.9M | 35 files: `llms.txt` and `llms-full.txt` of 17 repos as served by mintlify.com (16 in the 2026-04-07 table plus datamodel-code-generator) | README table with line counts and 16-hex sha256 prefixes (`README.md:40-59`); the refresh script lived in `/tmp` (`README.md:10, 64-67`) | data 2026-04-07; `jdx/` last commit `8cde84c8` 2026-07-02 | committable upstream text, but an aggregator copy, not the primary source |
| DF-5 | `docs/research/saved-searches/`, `github-topics.toml` | 108K | 11 TOML files: 160 `[[watch]]` (71 code, 57 issues, 17 discussions, 15 releases) and 97 `[[result]]` tables in a draft schema (`orchestration-2026-10-02.toml:1-20`) | controls described in comments | 2026-10-02 to 2026-10-11 | own |
| DF-6 | `docs/research/kb/transcripts/` | 108K | 8 YouTube transcripts plus `titles.tsv` | source URL line, "YouTube auto-captions" | 2026-07-25 | private |
| DF-7 | `.agent/kb/raw/` (ignored) | 527M | `research-fanout/` 377 MB in 88 runs (per-provider `*.json`, `*.raw`, `manifest.json` with `query`, `repo`, `strict_five`); `cc-docs-2026-10-01/` 9.6 MB Claude Code mirror (same `fetch.tsv` shape as KB); Codex implementer logs up to 14 MB each | run manifests; payloads unhashed | 2026-09 to 2026-10 | provider payloads and transcripts: never tracked (`.claude/rules/evidence.md:9`) |
| DF-8 | `.claude/types/` | 516K | 4 generated `.d.ts` files, "Written by Claude Code 2.1.271" | README | `64fd545e` 2026-10-01 | generated from a proprietary CLI |
| DF-9 | `graphify-out/` | 587M | graph outputs | none | n/a | derived |
| KB-1 | `sources/*.manifest`, clones in `sources/<name>/` (ignored, `.gitignore:176`) | 11G | 99 manifests (88 `kind = code`, 11 `kind = docs`, 13 `scope = study`); 96 clones: 88 full history, 8 shallow, 0 sparse; 3 manifests with no clone (agentsview, claudex-loop, deps-dev); 4 clones whose HEAD is not the manifest `commit` (agent-harness-docs, antigravity-cli, hk, rumdl) | `url`, `ref`, `commit`, `kind`, `scope`, prose comment (`sources/agents.manifest:1-6`); no licence, retrieval date or size cap | manifests 2026-07-21 to 2026-10-03 (`df390ddf`); clone commit dates 2025-05-23 (taplo) to 2026-10-02 (codex-docs) | per repo (classifier below) |
| KB-2 | `sources/media/` (tracked, `.gitignore:181`) | 12M | 297 tracked: Claude Code native `.md` mirror (232 pages per `fetch.stamp.json`, 9.4 MB), agentsview docs (33 pages, 1.1 MB), 27 single files (Anthropic and claude.com posts, platform docs, mindstudio and other articles, an X article, two transcripts, own plans) | mirrors: `fetch.tsv` (url, status and type, format, bytes; no hash) and `fetch.stamp.json`; singles: front matter with `source_url`, some with `content_sha256` | Claude Code mirror fetched 2026-10-03T02:27Z; singles 2026-07-22 to 2026-09-12 | mostly private; own plans; agentsview committable |
| KB-3 | `sources/*.pages.toml`, `sources/doppler-*.md`, `sources/claude-docs-backlog.txt` | small | `aihero-skills.pages.toml`: 8 pages with `content_sha256`, bodies ignored (`:1-20`); 12 Doppler pages tracked | best provenance of the three projects | 2026-08-02 (aihero) | private |
| KB-4 | `sources/REGISTRY.md` | 558 lines | 158 rows: 89 repo, 22 article, 18 tool, 11 docs, 7 media, 2 timeline, 1 forum | url, kind, tier, status, reason | `f086f731` 2026-10-05 | own |
| KB-5 | `docs/research/` | 5.4M | `reports/` 246 entries (133 md, 59 arms TOML, 9 dirs), `arms/` 8, `prototypes/` 25; rule "verbatim, annotate, never edit" (`README.md:15-32`) | dated names, probe tables with control arms | 2026-07-27 to 2026-10-05 | own |
| KB-6 | `.agent/kb/reports`, `.agent/kb/raw` (ignored) | 41M, 4.8M | 1,065 files (798 md); 602 files (bot reviews, probes, Codex logs) | none | 2026-08 to 2026-10 | own, transcripts |
| KB-7 | `docs/currency/` | 1.7M | 23 per-tool `*-watch-state.json`, `docs-fingerprints.json` (keyed by page URL), `upstream-baseline.json`, runs | watch state | last `696c9ae2` 2026-09-11 | own |
| KB-8 | `sources/extractions/` (13M, 28 tracked chunks), `sources/graphify-native-extract/` (17M), `graphify-out/` (5.8G), `.agent/kb/native-extract/` (138M) | | graphify chunks and graphs | none | to 2026-10-05 | derived (the extractions paraphrase third-party prose) |
| KB-9 | `.firecrawl/` 1.4M; `.claude/types/` | | search outputs; types "Written by Claude Code 2.1.277" | none | 2026-10-03 | private |
| TR-1 | `offline/<pkg>/` | 3.2G | 43 packages; `git/` and `repos/` 3.0G in 50 depth-1 clones; `site/` and `crawl/` 125M; 7,784 tracked files (about 35 MB, 6,928 under `site/`); pages per package up to 2,534 (pydantic), 2,501 (firecrawl), 1,074 (ruff) | `intel.json`: versions, `git_commit_sha`, `retrieval_timestamp`, `documentation.crawled_pages[]` (path, URL, token count); no hash, argv or exit code (Y4 #6) | retrieval 2026-10-08 to 2026-10-11; last commit `723d407` 2026-10-11 | per package; firecrawl and webclaw AGPL-3.0, graphviz and pylint GPL-2.0, most MIT or Apache-2.0 |
| TR-2 | `offline/*/reports/` | 0.3M | 64 tracked files in 18 packages: generated upgrade reports and an OKF bundle (`open-knowledge-format/reports/01-08`) | generated | 2026-10-08 to 2026-10-11 | own; W2 #14 shows fabricated verdicts |
| TR-3 | `docs/` | 752K | 30 files: project docs, `TOOLCHAIN_RESEARCH.md`, `reports/research_plugin_workflow/` (6 OKF pages), takeover bundle `reports/01-06`, `reports/dependency_upgrades/` | OKF front matter | `723d407` 2026-10-11 | own |
| TR-4 | `searches/` | 880K | 32 saved searches (22 CODE, 3 TOPIC, 2 ISSUE, 2 DISCUSSION, 2 PULL_REQUEST, 1 REPOSITORY), `controls.json`, 31 result files | query fingerprints and positive controls (W1 T14) | `e30259b` 2026-10-10 | own |
| TR-5 | `learnings/registry.json` | 20K | registry | none | `19e2ea2` 2026-10-10 | own (report L) |

Licence files read from the clones at their checked-out commits: MIT or Apache-2.0 for most rows; KB
`claude-code` "© Anthropic PBC. All rights reserved" (`sources/claude-code/LICENSE.md:1`); `awesome-claude-code`
CC BY-NC-ND; `basic-memory` AGPL-3.0; `GitNexus` PolyForm Noncommercial; `system-prompts-leaks` CC0 over text
it does not own; `ffmpeg` GPL/LGPL; `pyan` GPL-2.0; no licence file in `agentlinter`, `antigravity-cli`,
`cc-orchestrador-subagents`, `firecrawl-cli`, TR `openrouter/repos/.../docs`, `skills`, `awesome-openrouter`,
`free-llm-proxy-router`. Three community mirrors carry MIT files over content they do not own:
`thevibeworks/claude-code-docs` (Anthropic prose), `chenrui333/codex-docs` (OpenAI prose),
`thevibeworks/claude-reads-hn` (Apache-2.0 over Hacker News text).

### 1.3 Duplicates across the three projects (by upstream identity)

| Upstream | Copies | Where |
|---|---|---|
| Claude Code docs | 6 | DF-7 `cc-docs-2026-10-01`; DF-1 `claude-code-review-2026-09-29` (13 pages); KB-2 mirror (232 pages); KB `sources/claude-code-docs` (thevibeworks, 466 MB with SDK docs); KB `sources/agent-harness-docs/docs/claude-code`; KB-2 `claude-code-goal-docs.md` |
| Claude Code changelog | 3 | DF-1 `claude-code-changelog-2.1.258-2.1.266.md`; KB `sources/claude-code` (v2.1.258); thevibeworks `changelog.md` |
| Claude Code plugin types | 3 | DF-8 (2.1.271), KB-9 (2.1.277), KB-2 `claude-code-function-hooks-types.d.ts` (2.1.267) |
| Codex docs and source | 4 | KB `sources/codex` (1.1 GB, rust-v0.154.0); KB `sources/codex-docs` (chenrui333); KB `agent-harness-docs/docs/codex`; DF-3 `codex-0.161.0-settings-audit` source inventory |
| mise docs | 3 | DF-1 `mise-dotfiles-2026-09-29` (414 pages by firecrawl); DF-4 `jdx/mise`; KB `sources/mise` (252 MB, v2026.9.4) |
| hk, fnox | 3 each | DF-4; KB (hk v2.4.0 with HEAD drift, fnox v1.34.1); TR (hk 2.5.0, fnox `0c2ece5`) |
| uv, ruff, ty | 2 to 3 | KB (0.12.8, 0.16.5, 0.0.77); TR (uv cloned twice at `301799d` and `4efeeaf`, ruff 0.16.10, ty 0.0.85) |
| datamodel-code-generator | 3 | DF-4; KB 0.76.0; TR 0.83.0 |
| codebase-memory-mcp | 2 (2.9 GB) | KB 1.4 GB full clone, "EXCLUDED FROM THE BUILD 2026-08-20" (`sources/codebase-memory-mcp.manifest:7`); TR 1.4 GB |
| graphify | 2 plus graphs | KB fork `ray-manaloto/graphify` (320 MB); TR `Graphify-Labs/graphify` (39 MB); DF and KB graph outputs |
| context7 | 3 | KB `ctx7`; TR `git/` and `repos/` at the same SHA `522c4db` |
| rumdl | 3 | KB (HEAD drift); TR `git/` `b1da3de` and `repos/` `5eb9adb` |
| last30days-skill, pytest, pytest-xdist, typos, taplo, firecrawl, gitleaks/betterleaks | 2 each | KB and TR |
| pitchfork, mcp2cli | 2 each | DF-4 and TR or KB |
| YouTube transcripts | at least 4 shared ids | DF-6 and KB-2/KB-4 (`GnA9xjYWHBg`, `rtutpoT4SYg`, `XTBWVVcF3Pk`, `22iy2mDFiF8`) |
| DF secrets research | 2 | DF `docs/specs/secrets-takeover.md` copied into KB-2 `dotfiles-secrets-*.md` (`source_url` pins DF `6c9c5273`) |

### 1.4 Staleness (against Y5's measured upstream on 2026-10-14)

| Collection | Snapshot | Upstream now | Verdict |
|---|---|---|---|
| KB-2 Claude Code mirror | 2026-10-03 | changes daily (107 of 231 pages changed in its first day, `mise.toml:1169-1170`) | stale by KB's own 7-day rule (`python/src/kb_setup/docs_mirror.py:43`) |
| KB `sources/claude-code` | v2.1.258 | 2.1.299 | 41 releases behind |
| DF-1, DF-7 Claude Code pages | 2026-09-29, 2026-10-01 | daily | stale |
| KB `sources/codex` | rust-v0.154.0 | rust-v0.163.0 line | stale |
| mise (KB, DF-1, DF-4) | v2026.9.4, 2026-09-29, 2026-04-07 | v2026.10.9 (CT-26 pin) | stale; DF-4 is 190 days old |
| hk (KB, TR) | v2.4.0, 2.5.0 | v2.6.0 | stale |
| fnox (KB, TR) | v1.34.1, `0c2ece5` | at least v1.39.0 | KB stale; TR current at fetch |
| uv, ruff, ty (KB / TR) | 0.12.8, 0.16.5, 0.0.77 / 0.13.0, 0.16.10, 0.0.85 | 0.13.0, 0.17.0, 0.0.87 | KB stale; TR ruff and ty stale |
| agentsview (KB) | docs 2026-10-03; manifest v0.42.0 | v0.45.0 | stale |
| mattpocock-skills (KB) | 2026-08-24 commit | v1.3.1 | likely stale (not compared) |
| webclaw (TR) | 0.6.23 | 0.6.23 | current |
| KB reports, DF reports | to 2026-10-12 | n/a | dated records; staleness is per claim, not per file |

## 2. Defects (assume wrong; evidence)

- **C1-D1. KB republishes proprietary prose, against its own research.** KB's report found the repo public
  with no licence and recommended de-vendoring `sources/media/`, a `license` field, a `LICENSES/` mirror and
  a lint gate (`research-corpus-licensing.md:16, 510-546`). None landed: no `LICENSE` file, no `license` key in
  any of the 99 manifests (`grep` count 0), no `LICENSES/`. Then #829 vendored the full Claude Code docs
  (232 pages) into tracked `sources/media/claude-code-docs/` (`claude-code-docs.README.md:3-6`), content whose
  owner says "All rights reserved" (`sources/claude-code/LICENSE.md:1`). The aihero bodies were moved out of
  Git (`aihero-skills.pages.toml:7-11`), so the rule was known and applied once.
- **C1-D2. Licence read from the mirror, not the content owner.** `thevibeworks/claude-code-docs`,
  `chenrui333/codex-docs` and `claude-reads-hn` carry MIT or Apache files over Anthropic, OpenAI and Hacker News
  text (section 1.2). A classifier that reads `LICENSE` would call them committable. KB also measured five
  cases where GitHub's licence field was wrong (`research-corpus-licensing.md:117-126`).
- **C1-D3. Secondary mirrors instead of primary sources.** Codex docs come from a community mirror
  (`sources/codex-docs.manifest:3`), Claude Code docs from `thevibeworks` (`sources/claude-code-docs.manifest:3`),
  harness docs from `mrkhachaturov` (`sources/agent-harness-docs.manifest:14`), DF's tool docs from mintlify.com
  (DF-4). MP requires primary evidence (`docs/accepted-decisions.md:15`).
- **C1-D4. Whole repositories cloned for a few documents.** 88 of 96 KB clones carry full history, none is
  sparse (11 GB); `codebase-memory-mcp` is held twice (2.9 GB) although KB excludes it from its own build;
  `ffmpeg` (620 MB) and `cognee` (979 MB) are design references. TR clones depth 1 but whole trees, two of them
  twice (section 1.3).
- **C1-D5. Pins silently drift from disk.** Four KB clones are not at their manifest `commit` and three
  manifests have no clone, yet the manifest header claims "reproducible-by-reference (Invariant 3)"
  (`sources/agents.manifest:1`). KB's `kb-build` re-clones everything to prove reproduction (`mise.toml:779-813`),
  a 180-minute network job, rather than checking a hash.
- **C1-D6. Provenance without content hashes.** KB `fetch.tsv` rows hold url, status, type and bytes
  (`sources/media/claude-code-docs/fetch.tsv:1`), DF `INDEX.md` holds rc and bytes
  (`mise-dotfiles-2026-09-29/INDEX.md:5`), DF-4 keeps 16-hex prefixes, TR `intel.json` keeps none. Only KB's
  `pages.toml` and some media front matter carry a full `content_sha256`. No collection binds a fetch to the
  tool version, argv and exit code.
- **C1-D7. Source lists live in code or in `/tmp`.** KB hard-codes its mirrored sites in `SITES`
  (`docs_mirror.py:69-96`), TR its 44 rows in `DEPENDENCY_CATALOG` (W1 T1), and DF-4's refresh script existed
  only in `/tmp` (`README.md:10, 64-67`), so DF-4 cannot be reproduced.
- **C1-D8. Paid cloud scrapes for free primary text.** DF fetched 414 mise pages through `firecrawl scrape`
  (`INDEX.md:3`), a credit-metered cloud route, when `jdx/mise` keeps the same Markdown under `docs/` (MIT).
- **C1-D9. Copies multiply and none is authoritative.** Claude Code docs exist six times in two projects,
  plugin type declarations three times at three CLI versions, tool docs three times (section 1.3). No project
  dedupes by content.
- **C1-D10. Staleness is detected but not acted on.** KB's own 7-day rule flags its mirror (section 1.4); DF-4
  is 190 days old with no check; KB pins hk v2.4.0 while hk 2.6.0 is the tool MP is locking (CT-26).
- **C1-D11. Reports are many, unindexed and mixed with process noise.** DF holds 1,266 agent reports, most of
  them cold reviews and session audits (DF-2); KB keeps 798 unpromoted reports outside Git (KB-6) and promotes
  only some (`docs/research/README.md:15-18`). Nothing records which finding still holds; supersession is a
  prose annotation.
- **C1-D12. Valuable runs would vanish at sunset.** DF-3's 52 MB Codex settings audit (with its `SHA256SUMS`),
  DF-7 and KB-6 are ignored by Git; deleting the checkouts deletes them. TR has no remote at all.
- **C1-D13. Content captured through an auth wall and from leaks.** KB-2's X article records
  `retrieval: "logged-in Chrome (graphify fetch hit the X auth wall)"` (`x-towards-ai-graph-engineering.md:7`);
  `system-prompts-leaks` stays in KB's corpus after KB's own report advised `redistribute = false`
  (`research-corpus-licensing.md:523-525`).
- **C1-D14. Own notes and third-party prose share one folder.** KB-2 mixes user plans
  (`framework-plan-ladybug.md`, `second-brain-report-20260722b.md`) and copies of DF's secrets docs with blog
  copies; TR mixes pages, clones and generated reports under one package root (F2 Part A), and W2 #2 shows the
  generated reports being re-indexed as sources.
- **C1-D15. A whole-repository archive of TR would carry private data.** TR tracks 7 private documents
  under `original/` and 14 rewritten copies under `generated/updated_*` (`git ls-files`), so any `git bundle`
  or clone of TR imports them.

## 3. Features to import

### 3.1 How the corpus lands in MP

Rules:
1. **Re-fetch, never copy.** D86 admits webclaw downloads, clones and disk without limit, so every source with
   an upstream is fetched fresh by CT-33 (pages) or CT-42 (repos) from a manifest row; no byte moves from DF, KB
   or TR into `/offline/` except through an `archive` row (rule 3).
2. **Licence by content owner.** Each row names the owner of the text it fetches and its class; a mirror's
   `LICENSE` never upgrades text it does not own; unknown means private. Because corpus bytes are never tracked
   (D57), the class governs what may appear in tracked files: test fixtures only from committable rows (with
   their notice), and quotations from private rows only within a budget checked by `offline:cite-verify`.
3. **Archive only what has no upstream.** Own reports and runs, video transcripts, the auth-walled article and
   pages that have moved come from a hash-bound export of the source project (C1-1), never from a live checkout.
4. **One tracked home for research prose.** MP-authored research reports go to `docs/research/`; the source
   projects' reports are indexed by pointer in `docs/research/prior-work.toml` and are queryable through
   `archive` rows, not copied into tracked files.

Layout (W1's layout plus the C1 additions, marked C1-n):

```
/offline/                                     untracked (CT-08 adds /offline/ to .gitignore)
  objects/sha256/<aa>/<hash>                  CT-33 content store; dedupes across rows
  sources/<id>/runs/<run>/..., CURRENT, pages/, git/    CT-33, CT-42
  archive/dotfiles/<commit>.bundle            C1-1: git bundle of DF's final commit
  archive/knowledge-base/<commit>.bundle      C1-1: git bundle of KB's final commit
  archive/tr/<commit>-allow.tar               C1-1: path allow-list export, never original/ or generated/
  archive/<project>/untracked-<ns>.tar        C1-1: ignored research dirs, after a gitleaks scan
tracked
  offline-sources.toml                        CT-41 manifest (rows in 3.3)
  schemas/offline-sources.schema.json         committed schema, single source (D83, CT-52)
  evidence/offline/runs/<id>--<ns>--<hex16>/manifest.json      CT-33 receipts
  evidence/offline/archive/<project>--<ns>--<hex16>.json       C1-1 export receipts
  evidence/offline/cite/<slug>--<ns>--<hex16>.json             CT-44 cite-verify receipts
  docs/research/README.md                     C1-2: rules for research reports
  docs/research/<YYYY-MM-DD>-<slug>.md        MP-authored research reports
  docs/research/prior-work.toml               C1-2: pointer index of DF, KB and TR reports with dispositions
```

Plan-scoped reviews such as this one stay under `P/reviews/`; `docs/research/` holds findings meant to outlive
a plan, and owner documents link to them (`docs/AGENTS.md` authority table gains one row).

### 3.2 Re-fetch fresh versus archive

Re-fetch fresh (no copy): every KB clone (99 manifests) as a sparse, blob-less, pinned row or a pointer row;
every TR package (43) as a sparse repo row and, where wanted, a docs row; the Claude Code, Codex, agentsview,
aihero and platform docs pages; every article and blog post that still resolves; DF-4's tool docs from
their repositories; the plugin type declarations, regenerated by the installed CLI (KB-A, CT-31 row 1).

Archive (C1-1 export, `kind = archive` rows): DF-2, DF-3 (including the untracked Codex audit), KB-5, KB-6 and
TR-3 reports and runs; DF-6 and KB-2 transcripts; the X article; any page the CT-41 plan stage finds moved or
gone (KB already records `claude-tag` as moved off-site, `2026-10-02-kb837-offline-docs/findings.md:60-61`).
DF-7 `research-fanout` payloads go into the untracked tarball for audit but get no row: they are stale provider
results, and their 88 queries are listed for C1-4.

### 3.3 Proposed manifest rows

Columns follow the brief; "Y5" is the row in Y5 §2 that the row confirms or replaces; "Replaces" names the
copies it retires. Rows not listed here (Y5 #6, #11, #18, #19, #21, #24, #27, #46, #49 to #52) stand as Y5 wrote
them. `enabled = false` rows are registered pointers, never fetched until a ticket enables them.

| # | Id | URL or repo | Pages or sparse paths | Licence class | P | Y5 | Replaces |
|---|---|---|---|---|---|---|---|
| 1 | claude-code-docs | code.claude.com/docs/llms.txt, `.md` twins under `/docs/en/` | every listed page (232 on 2026-10-03; Y5 counted 257) | private | P1 | 1 | KB-2 mirror, KB thevibeworks clone, KB agent-harness-docs `docs/claude-code`, DF-7 `cc-docs`, DF-1 review bundle |
| 2 | claude-code-changelog | github.com/anthropics/claude-code | `CHANGELOG.md`; releases via `vertical github_release` | private | P1 | 2 | KB `sources/claude-code` v2.1.258, DF-1 changelog |
| 3 | claude-code-plugins | anthropics/claude-code at the latest tag | `plugins/`, `examples/` | private | P1 | 3 | KB `sources/claude-code` |
| 4 | codex-manual | learn.chatgpt.com/docs/llms.txt, `.md` twins | 193 listed pages | private | P1 | 12 | KB `sources/codex-docs`, KB agent-harness-docs `docs/codex` |
| 5 | codex-repo | openai/codex at the installed tag | `docs/`, config and hook schema files (path resolved by the CT-33 spike) | committable (Apache-2.0) | P1 | 13, 15 | KB `sources/codex` (1.1 GB full) |
| 6 | codex-releases | openai/codex | `vertical github_release` | committable | P1 | 14 | none |
| 7 | planning-with-files | OthmanAdi/planning-with-files at v3.24.0 | `docs/`, `skills/`, `templates/`, `examples/`, `CHANGELOG.md`, `llms.txt` | committable (MIT) | P1 | 20 | plugin cache only |
| 8 | mattpocock-skills | mattpocock/skills at v1.3.1 | `docs/`, `skills/`, `CHANGELOG.md`, `GLOSSARY.md`, `SCOPE.md` | committable (MIT) | P1 | 22 | KB clone |
| 9 | aihero-skills | aihero.dev sitemap, `.md` pages | the 8 unique pages in `aihero-skills.pages.toml` plus the skills changelog pages (about 36) | private | P1 | 23 | KB-3 |
| 10 | mise | jdx/mise at v2026.10.9 | `docs/`, `CHANGELOG.md`; `releases.atom` | committable (MIT) | P1 | 25, 26 | KB clone, DF-1 firecrawl mirror, DF-4 |
| 11 | fnox | jdx/fnox at the latest release (at least v1.39.0) | `docs/`, `CHANGELOG.md`, `skills/fnox/` | committable (MIT) | P1 | 29, 30 | KB clone, TR fnox, DF-4 |
| 12 | hk | jdx/hk at v2.6.0 | `docs/`, `CHANGELOG.md`, `skills/` | committable (MIT) | P1 | 31 | KB clone, TR hk, DF-4 |
| 13 | webclaw | 0xMassi/webclaw at v0.6.23; webclaw.io/docs | `README.md`, `docs/`; site pages under `/docs/` (50 in TR) | committable docs, AGPL-3.0 notice, no code vendored | P1 | 54 | TR webclaw |
| 14 | platform-claude | platform.claude.com/llms.txt | sections agents-and-tools, build-with-claude (prompt engineering), managed-agents, agent-sdk | private | P2 | 4 | KB-4 rows 1, 3, 46, 48; KB-2 `ptc-doc.md` |
| 15 | claude-agent-sdk-python | anthropics/claude-agent-sdk-python | `README.md`, `CHANGELOG.md`, `examples/` | committable (MIT) | P2 | 5 | KB clone |
| 16 | claude-cookbooks | anthropics/claude-cookbooks | `claude_agent_sdk/`, `skills/`, `tool_use/`, `managed_agents/` | committable (MIT) | P2 | 7 | KB-4 rows 110, 113 |
| 17 | anthropic-skills | anthropics/skills | `skills/` | private (no root licence) | P2 | 8 | none |
| 18 | anthropic-engineering | anthropic.com/engineering | Y5's ten posts plus `advanced-tool-use` | private | P2 | 9 | KB-4 row 112 |
| 19 | codex-plugin-cc | openai/codex-plugin-cc | whole tree (0.2 MB) | committable (Apache-2.0) | P2 | 17 | KB clone |
| 20 | openai-cookbook-codex | openai/openai-cookbook | `examples/codex/`, the Codex prompting and goals guides | committable (MIT) | P2 | 16 | none |
| 21 | uv | astral-sh/uv at 0.13.0 | `docs/`, `CHANGELOG.md`, `changelogs/` | committable (MIT or Apache-2.0) | P2 | 32 | KB clone, TR two clones and 84 pages in four formats |
| 22 | ruff | astral-sh/ruff at the locked version (0.17.0 latest) | `docs/`, `CHANGELOG.md` | committable (MIT) | P2 | 33 | KB clone, TR clone and 1,074 crawled pages |
| 23 | ty | astral-sh/ty at the locked version (0.0.87 latest) | `docs/`, `CHANGELOG.md` | committable (MIT) | P2 | 34 | KB clone, TR |
| 24 | python-docs | docs.python.org 3.15 archive | the stdlib modules MP uses | committable (PSF) | P2 | 35 | none |
| 25 | datamodel-code-generator | koxudaxi/datamodel-code-generator at the version MP locks | `docs/`, `README.md` | committable (MIT) | P2 | new | KB 0.76.0, TR 0.83.0, DF-4 |
| 26 | gh-cli | cli/cli at v2.98.0; cli.github.com/manual | `docs/`; manual pages | committable (MIT) | P2 | 36 | KB 143 MB full clone |
| 27 | git-docs | git/git | `Documentation/git-worktree.txt`, `git-merge.txt`, `githooks.txt`, `git-config.txt`, `git-bundle.txt`, `git-sparse-checkout.txt` | committable (GPL-2.0 notice) | P2 | 37 | none |
| 28 | githubkit | yanyongyu/githubkit at the locked version | `docs/`, `README.md` | committable (MIT) | P2 | 54 | TR 120 MB clone |
| 29 | context7 | upstash/context7 at the `ctx7@` tag matching the pin | `README.md`, `docs/`, `packages/cli/README.md` | committable (MIT) | P2 | 54 | KB `ctx7`, TR two clones |
| 30 | last30days-skill | mvanhorn/last30days-skill at the pinned version | `README.md`, `SKILL.md`, `docs/` | committable (MIT) | P2 | new | KB and TR clones |
| 31 | agentsview | kenn-io/agentsview at v0.45.0 | `docs/` (the site's 33 pages come from it) | committable (MIT) | P2 | 53 | KB-2 mirror, KB manifest without clone |
| 32 | graphify | Graphify-Labs/graphify at its latest release | `README.md`, `docs/` | committable (Apache-2.0 or MIT) | P2 (for CT-55) | new | KB fork clone 320 MB, TR clone |
| 33 | codebase-memory-mcp | DeusData/codebase-memory-mcp at its latest release | `README.md`, `docs/` | committable (MIT) | P2 (for CT-55) | new | KB and TR 1.4 GB trees |
| 34 | cxx-toolchain | Y5 #39 to #45, #47, #48: clang-p2996 sparse at `f17c8d6c7bfe`, IWYU, CMake `Help/` at v4.4.4, ninja manual, sccache, vcpkg-docs, WG21 papers, GCC 16 manuals, libstdc++ API | as Y5 | WG21 private; GCC GFDL notice; rest committable | P2 and P3 | 39 to 45, 47, 48 | none in DF, KB or TR (DF's LLVM and IWYU sweeps become prior work) |
| 35 | usage | jdx/usage | `docs/` | committable (MIT) | P2 | 28 | none |
| 36 | claude-blog | claude.com/blog named posts | Y5 #10's three plus `claude-models-explained...`, `the-new-rules-of-context-engineering...`, `building-verification-loops...` | private | P3 | 10 | KB-2 `blog-*.md` |
| 37 | harness-articles | martinfowler.com/articles/harness-engineering.html; openai.com/index/harness-engineering; addyosmani.com/blog/agent-harness-engineering; humanlayer.dev skill-issue post; augmentcode.com loop-engineering post; agent-engineering.dev harness post; louisbouchard.ai graph-engineering | 7 pages | private | P3 | new | KB-4 rows 40 to 47, 54 |
| 38 | orchestration-articles | three mindstudio.ai posts, datasciencedojo.com orchestrator post, linas.substack.com fallback post, gregceccarelli.com/goal-engineering, sabrina.dev loop post, cerebras.ai knowledge-base post | 8 pages | private | P3 | new | KB-2 singles |
| 39 | jdx-blog | jdx.dev/posts | 36 listed posts | private | P3 | new | DF-1 `jdx-posts/` |
| 40 | agent-config-linters | agent-sh/agnix, felixgeelhaar/cclint | `README.md`, rule docs | committable (MIT or Apache-2.0) | P3 (prior art for CT-38, CT-58) | new | KB clones |
| 41 | claude-code-envs | thevibeworks/claude-code-envs | all 10 pages | private (describes a proprietary product) | P3 | new | KB clone |
| 42 | host-adapter-docs | opencode.ai/docs or anomalyco/opencode `docs/`; antigravity.google/docs | adapter-relevant pages | opencode committable (MIT); Antigravity private | P3 (accepted decisions name both hosts) | new | TR opencode 234 MB, TR antigravity, KB `antigravity-cli` |
| 43 | openrouter-docs | openrouter.ai/docs | API reference pages | private | P3 (CT-46, CT-48) | new | TR openrouter (4 clones) |
| 44 | research-provider-docs | exa.ai/docs, docs.firecrawl.dev | API reference pages only | private | P3 | new | TR exa (52 pages), TR firecrawl (2,501 pages) |
| 45 | graphviz-docs | graphviz.org/documentation | attribute and layout pages | committable upstream (EPL; confirm at fetch) | P3 (CT-54) | new | TR graphviz 175 MB clone |
| 46 | secret-scanners | gitleaks/gitleaks at v8.30.1; betterleaks/betterleaks | `README.md`, config docs | committable (MIT) | P3 | 38 | KB gitleaks, TR betterleaks |
| 47 | orchestration-peers | openai/symphony, kumanday/OpenSymphony, ReyJ94/Sol-Orchestrator, bytedance/deer-flow, Cjbuilds/Codex-Orchestration, wshobson/agents (`plugins/plugin-eval/`), shareAI-lab/learn-claude-code, affaan-m/ECC, microsoft/SkillOpt, the three fable orchestrators, Jaan-Mustafa/10x-Team, adihebbalae/Attacca | `README.md`, `AGENTS.md`, `SKILL.md` files only | committable (MIT or Apache-2.0) | P4, `enabled = false` | new | KB clones |
| 48 | memory-and-graph-peers | basicmachines-co/basic-memory, topoteretes/cognee, major7apps/pensyve, ramakay/claude-self-reflect, colbymchenry/codegraph, tirth8205/code-review-graph, abhigyanpatwari/GitNexus, cosmtrek/mindwalk, oraios/serena | `README.md`, `docs/` | basic-memory AGPL, GitNexus non-commercial: private; rest committable | P4, `enabled = false` (CT-55 may enable) | new | KB clones |
| 49 | catalogs | hesreallyhim/awesome-claude-code, ai-boost/awesome-harness-engineering, anthropics/claude-plugins-community | `README.md` | awesome-claude-code private (NC-ND); rest committable | P4 | new | KB clones |
| 50 | own-reports | `archive` rows over C1-1 exports: KB `docs/research/**`, KB `.agent/kb/reports/**`, DF `docs/research/**`, DF-3 untracked audit, TR `docs/**` | path globs inside each export | own (committable by the user's choice; tracked copies still forbidden by rule 4) | P2 | new | KB-5, KB-6, DF-1 to DF-3, TR-3 |
| 51 | transcripts | `archive` rows: DF-6's 8 files, KB-2 `yt-*` | per file | private | P4 | new | DF-6, KB-2 |
| 52 | unpinnable-pages | `archive` rows: KB-2 `x-towards-ai-graph-engineering.md`; KB-2 `claude-code-memory-plan.pdf` only if its Notion page no longer resolves | per file | private | P4 | new | KB-2 |

Rough size: P1 about 27 MB of text (Y5 §3); P2 about 100 MB (the Python archive, cookbook notebooks, CMake,
vcpkg and the sparse LLVM paths dominate); P3 and the `archive` rows a few hundred MB, most of it the DF and KB
bundles. Against 14.8 GB held today.

### 3.4 Acceptance rows on existing tickets

| Ticket | Row | Evidence |
|---|---|---|
| CT-41 | 1. The manifest schema is the committed `schemas/offline-sources.schema.json` (D83); the loader is generated by CT-52; validation exits 2 | D83; W1 §3 |
| CT-41 | 2. Rows carry `licence` (SPDX, `proprietary` or `unknown`), `licence_owner` (owner of the fetched text), `licence_evidence` (path at the pinned SHA plus sha256, or a terms URL plus its fetch receipt) and `licence_class` (`private` or `committable`); a mirror's `LICENSE` never sets the class of text it does not own; `unknown` is `private`. Fixture: `thevibeworks/claude-code-docs` (MIT file, Anthropic text) validates as `private` | C1-D1, C1-D2 |
| CT-41 | 3. `primary` and `mirror_of`: a non-primary row is refused while a primary row for the same content exists, unless it records a waiver. Fixture: `chenrui333/codex-docs` against `learn.chatgpt.com` | C1-D3 |
| CT-41 | 4. `collection` (query scope), `enabled` (`false` = pointer, never fetched) and `imported_from` (`<project>:<path>:<line>` of the old row, required for rows created by the import) | C1-D11, sunset proof |
| CT-41 | 5. The plan stage carries KB's measured site rules: union of `llms.txt`, `sitemap.xml` and `webclaw --map --no-map-crawl` (sitemap only, because `--map` with crawl adds `?tab=` URLs and images); host canonicalised before fetch (agentsview apex answers 307 to `www`); a redirect to another host is recorded `moved` and not followed; `.md` twins first, HTML rendered only without a twin; a listed page retires only after 3 misses spanning 7 days | `2026-10-02-kb837-offline-docs/findings.md:22-61`; `docs_mirror.py:43-45` |
| CT-41 | 6. `kind = archive` rows name `project`, `export_receipt`, `path` and `sha256`, and are accepted only when the plan stage records the upstream as gone, moved or walled, or the bytes have no upstream (own reports, transcripts) | C1-D12, C1-D13 |
| CT-41 | 7. D86 lifts the admission limits, not the row bounds: each row still names a positive `max_pages` and a `robots` decision (`checked`, or `waived:<reason>` under D86), so a typo cannot start an unbounded crawl (question Q1 in 3.6) | Y4 #1; D86 |
| CT-41 | 8. A normalised URL, or a (repo, path set, SHA) triple, appears in at most one enabled row | C1-D9 |
| CT-33 | 1. Receipts copy `licence_class` and `collection` from the row; `files[]` names the store object, so identical pages fetched by two rows cost one object | C1-D9 |
| CT-33 | 2. `archive` rows are materialised from the C1-1 export by path and sha256, never from a live DF, KB or TR checkout; the receipt names the export receipt's hash | C1-D12 |
| CT-33 | 3. `offline:verify --tracked` exits 1 when any tracked file's sha256 equals a stored page object, so corpus text cannot enter Git by copy | C1-D1 |
| CT-42 | 1. Every KB `kind = code` source maps to a sparse, blob-less row at a pinned tag with named paths, or to an `enabled = false` pointer; no full-history clone; KB's `commit` goes to `imported_from` | C1-D4, C1-D5 |
| CT-42 | 2. `LICENSE*` and `COPYING*` at the pinned SHA are hashed into `licence_evidence` (feeds CT-41 row 2), because GitHub's licence field was wrong five times | `research-corpus-licensing.md:117-126` |
| CT-42 | 3. At most one clone per (url, SHA); a second row for the same repo widens the sparse path set instead | TR context7, uv, rumdl (1.3) |
| CT-43 | 1. `--collection` filter; every hit carries `licence_class`; `archive` rows are indexed like pages | 3.1 rule 4 |
| CT-43 | 2. Golden query fixtures come only from committable rows and carry their licence notice | 3.1 rule 2 |
| CT-44 | 1. One home for answers: `docs/research/<YYYY-MM-DD>-<slug>.md`, replacing Y4's `evidence/offline/answers/`; cite-verify receipts under `evidence/offline/cite/` | Y4 §3; C1-D11 |
| CT-44 | 2. `offline:cite-verify` enforces a quotation budget for private rows (proposal: at most 40 words per quotation and 10 percent of a report's words; numbers fixed at the spec fold) and fails on any longer copied run | C1-D1 |
| CT-44 | 3. The offline-corpus skill pair looks up `docs/research/prior-work.toml` and the `own-reports` rows before starting new research | C1-D11 |
| CT-47 | 1. Page change detection reads the receipts' page sha256 and a site's `lastmod`; no separate fingerprint file like KB's `docs/currency/docs-fingerprints.json` | KB-7 |
| CT-52 | 1. The committed schemas include `offline-sources.schema.json`, `research-report.schema.json` (front matter) and `prior-work.schema.json`; Python is generated from them | D83 |
| CT-55 | 1. Any graph indexes receipted corpus files only; KB `graphify-out/` (5.8 GB), `sources/extractions/` and both 1.4 GB codebase-memory trees are not imported; KB's retrieval-gap and peer-synthesis reports enter as `prior-work.toml` rows | KB-8; KB `docs/research/reports/*-retrieval-gap.md` |

Not repeated: CT-08's `/offline/` ignore line (W1), CT-36's "never writes the corpus" (W1), and the plugin
type declarations, owned by KB-A's CT-31 row 1.

### 3.5 New tickets

| Id | Title | Size | Improved design | MP destination | Blockers | Admissions |
|---|---|---|---|---|---|---|
| C1-1 | Source-project exports with hash-bound receipts | M | `offline:archive -- <project>` reads a checkout and writes only under `/offline/archive/<project>/`: DF and KB as `git bundle create --all` at the final commit; TR as `git archive <sha>` over an allow-list (`docs/`, `searches/`, `learnings/`, `offline/*/intel.json`), refusing any path under `original/` or `generated/` (fixture, C1-D15); ignored research dirs (DF `.agent/kb/raw/research-fanout/`, `docs/research/runs/codex-0.161.0-settings-audit/`, `.agent/kb/raw/cc-docs-*`; KB `.agent/kb/reports/`, `.agent/kb/raw/`) tarred with a per-file sha256 list after a pinned gitleaks scan, hits quarantined. Receipt `evidence/offline/archive/<project>--<ns>--<hex16>.json`: argv, source HEAD and refs, allow-list, archive sha256, file count, scan tool, version and finding count (no values). Exports are verified by re-hash, never refreshed | `python/src/marketplace_dev/offline/archive.py`, test, fixtures, one `mise.dev.toml` row, `evidence/offline/archive/` | CT-39 (package, receipts module), CT-11 (lock) | host read of the three checkouts (read-only Git); gitleaks pin; about 1 GB disk |
| C1-2 | Research report home and prior-work index | M (split a: index and README; b: check) | (a) `docs/research/README.md`: reports are immutable once published, a correction is a new report naming the old one in `supersedes`, annotation above a section is allowed, edits are not (KB's rule, `docs/research/README.md:20-32`); every corpus citation is `source_id`, `run_id`, `path:line`; quotation budget per CT-44 row 2; authority row in `docs/AGENTS.md`. `research:prior-work -- --project <p>` generates `docs/research/prior-work.toml` from the C1-1 exports: one row per report (project, repo URL or export receipt, commit, path, blob sha256, date, title, tags, `disposition` = `pending`, `reverified:<report>`, `superseded:<reason>` or `not-imported:<reason>`); process reviews get `not-imported:process` mechanically. (b) `research:check` (read-only): front matter against `research-report.schema.json`, every `prior_work` id resolves, citations pass CT-44's cite-verify, pending count printed. KB-A-7's `recall:work` census reads this index as one probe | `docs/research/`, `python/src/marketplace_dev/research/{prior_work,check}.py`, tests, two task rows | C1-1, CT-39, CT-52; (b) also CT-44 | none |
| C1-3 | Re-verified research reports from the imports | L, one S unit per topic | Each unit re-asks one question against the fresh corpus (plus the AGENTS.md research route where outside evidence is needed), writes `docs/research/<date>-<slug>.md`, and sets dispositions in `prior-work.toml`. Topics and their prior work: (1) corpus licence classes (KB `research-corpus-licensing.md`, `research-comparable-projects-redistribution.md`); (2) docs mirror mechanics (KB `2026-10-02-kb837-offline-docs/`, TR `open-knowledge-format/reports/02, 07, 08`); (3) Claude Code function hooks and mods (KB `2026-09-10-function-hooks-research.md`, `2026-09-10-github-function-hooks-examples.md`, DF `2026-09-11-fnhook-harvest.md`); (4) Codex config, hooks and schema (DF-3 `codex-0.161.0-settings-audit/report.md`, KB `2026-08-21-codex-config-writer.md`, `2026-08-28-codex-binary-probe.md`, `2026-08-28-codex-plugin-cc-anatomy.md`, `2026-08-29-codex-docs-mirror-sweep.md`); (5) mise OCI and container CI (KB `2026-08-28-mise-oci-container-ci.md`, DF `2026-08-30-codex-research-mise-oci.md`); (6) skill composition (KB `skill-composition-docs.md`, `skill-composition-survey.md`); (7) research aggregation internals (KB `2026-08-27-deep-research-internals.md`, `2026-08-27-aggregated-research-evaluation.md`, TR `research_plugin_workflow/`), coordinated with KB-A-2..KB-A-6; (8) Claude and Codex handoff (KB `2026-08-27-claude-codex-handoff.md`, DF `research-20260813-codex-session-communication/report.md`); (9) agent memory and graph retrieval (KB `2026-08-17-agent-memory-research.md`, the four `*-retrieval-gap.md`), for CT-55; (10) Python toolchain layout (TR `TOOLCHAIN_RESEARCH.md`, DF `python-pin-location-mise-vs-uv-2026-10-01`); (11) LLVM and IWYU version detection (DF `iwyu-prebuilt-llvm23-sweep-2026-10-03`, `llvm-major-detection-sweep-2026-10-02`), for the LLVM chain; (12) fetch rate limits and retry (DF `2026-09-03-rate-limit-retry-research.md`), for CT-33 | `docs/research/`, `docs/research/prior-work.toml` | C1-2, CT-44, C1-5 (rows fetched) | research route profile per AGENTS.md; D86 fetches |
| C1-4 | Saved-search definitions into the catalog | S | Convert DF-5's 71 code watches and TR-4's 22 CODE searches into `dev/saved-searches.toml` `[[search]]` rows, each with a positive `[[search.control]]`, only where a ticket names a use; the 57 issue, 17 discussion and 15 release watches, TR's other kinds and DF-7's 88 fan-out queries go into `prior-work.toml` as `not-imported:catalog-kind` until the catalog gains those kinds (DF-A-1 keeps the catalog in `search_catalog`); measured `[[result]]` tables are not imported (re-run instead) | `dev/saved-searches.toml` (or its CT-39 successor) | CT-39 (catalog move); DF-A-1 for non-code kinds | GitHub API quota for one control run |
| C1-5 | Corpus seed and import parity | M | Write rows 1 to 52 of 3.3 into `offline-sources.toml` with licence evidence; one live refresh of every enabled P1 and P2 row under D86; `offline:import-parity` (read-only, reads the C1-1 exports, never live checkouts) lists every source the projects held (KB's 99 manifests, `*.pages.toml` pages, `source_url` front matter in `sources/media/`, REGISTRY rows; TR's 43 `intel.json` documents and repositories; DF-1 URLs from `INDEX.md` and `fetch.tsv`; DF-4's 17 repos) beside its MP row id or a not-imported reason, and exits 1 on any unmapped source | `offline-sources.toml`, `python/src/marketplace_dev/offline/parity.py`, test, task row, one parity receipt under `evidence/offline/` | CT-41, CT-33, CT-42, C1-1 | D86 (fetches, clones, disk) |

### 3.6 Questions for the parent or user

- Q1. D86 says no page, robots or disk limit. Read as lifting the admission caps only, rows keep a positive
  `max_pages` and a recorded robots decision with per-row waivers (CT-41 row 7). Confirm or override.
- Q2. KB is public (per its own report) and tracks Anthropic docs, blog copies and an auth-walled article
  (C1-D1, C1-D13). Whether to make KB private or rewrite its history at sunset is the user's call; MP never
  edits KB.
- Q3. DF's visibility was not checked (no network); DF tracks Claude Code doc pages (DF-1) and jdx.dev posts.
  Same question as Q2.
- Q4. TR has no remote and tracks private documents (C1-D15). C1-1 exports by allow-list only; what happens to TR's
  `original/` and `generated/` is the user's decision under D81.
- Q5. The quotation budget numbers (CT-44 row 2).
- Q6. Whether the 13 KB `scope = study` repos and the P4 peers stay as `enabled = false` pointers (recommended:
  they cost nothing and keep the reference) or are dropped.

## 4. Not imported

- **Bytes of any clone or crawl from DF, KB or TR.** Re-fetched fresh (3.2); the old copies are stale (1.4),
  unhashed (C1-D6) and oversized (C1-D4).
- **KB graphs and extractions** (`graphify-out/` 5.8 GB, `sources/extractions/` 13 MB of paraphrase,
  `graphify-native-extract/`, `.agent/kb/native-extract/`) and **DF `graphify-out/`**: derived; CT-55 decides
  any graph, built from receipted files.
- **TR generated reports** (`offline/*/reports/`, 64 files): W2 #14 shows fabricated verdicts. **TR `intel.json`
  as a format**: replaced by CT-33 receipts. **TR `site/`, `crawl/{markdown,llm,json}` triplicates**: one format,
  derived locally (Y4 #2).
- **TR project docs** (`ARCHITECTURE.md`, `CLI.md`, the OKF research-plugin bundle as a design): they describe
  code D81 does not import; indexed in `prior-work.toml` only.
- **DF-4 mintlify cache**: aggregator copy, 190 days old; MP fetches the repos (rows 10 to 12, 25). Its
  host-setup entries (chezmoi, starship, devcontainers, dive) stay with DF's host setup.
- **DF-7 fan-out payloads and both projects' Codex implementer logs** as corpus: provider payloads and
  transcripts are never tracked or indexed (`.claude/rules/evidence.md:9`); they ride in the private C1-1 tarball
  only.
- **KB `docs/currency/` watch states**: CT-47 (staleness) and CT-26 and KB-A's CT-22b row 1 (pins) replace them.
- **KB `.firecrawl/` search outputs**: stale provider results.
- **Sources with no MP use**: logging libraries (structlog, loguru, logbook, logly, logxide, picologging,
  orjson, msgspec), local model runtimes (colibri, nativ, turbo-fieldfare), free-model proxies and key pools
  (free-llm, freellmapi, freellmpool, free-llm-proxy-router, litellm-free-models-proxy, llm-keypool; D81),
  ffmpeg, biome, pkl, trafilatura, typer, rich, pydantic, python-statemachine, python-dateutil, pylint, pydeps,
  pitchfork (no daemons), opentelemetry-python (the collector is a separate stream), the MCP Python SDK,
  knowledge-catalog, open-knowledge-format, deps.dev protos (KB-A-2 owns them), mcp2cli, the survey diagram
  tools (appmap-python, pyan, mermaid-trace, pdoc, griffe, dependency-cruiser: CT-54 may register them later),
  `claude-code-marketplace` (this repository).
- **Doppler docs and CLI** (KB-3, KB clone) and DF's secrets research: host setup stays in DF.
- **`system-prompts-leaks`** (leaked text), **`claude-reads-hn`** (498 MB Hacker News archive, deferred by KB on
  cost), **`claude-code-http-spec`** (reverse-engineered wire format), X and Reddit timelines (KB-4 rows 13, 20,
  21: walled or live).
- **Research tooling** (`research_fanout.py`, `saved_searches.py`, `research_scope.py`,
  `codex_research_gate.py`): not corpus; DF-B flagged them for the parent (`DF-B-dotfiles-python-tooling.md:334-338`).

## 5. Sunset checklist

Each item may be deleted in the source project only after the named MP item has landed and passed `/verify`.
Deleting a GitHub repository breaks `prior-work.toml` links; archiving it read-only keeps them, so archive
rather than delete (C1-1's bundles cover deletion too).

**dotfiles (research corpus only; host setup stays):**
- `docs/research/kb/raw/` (DF-1): after C1-1's DF export receipt and C1-5's parity report shows every URL
  mapped or not imported; keep only bundles the report marks `stays-in-dotfiles`.
- `docs/research/kb/reports/`, `kb/transcripts/`, `kb/artifacts/`, `kb/decisions/`, `docs/research/runs/`
  (DF-2, DF-3, DF-6): after C1-1 and C1-2's `prior-work.toml` lists them; the untracked
  `codex-0.161.0-settings-audit/` only after its tarball receipt.
- `docs/research/mintlify-cache/`: the jdx and datamodel-code-generator entries after rows 10 to 12 and 25
  hold receipts; mcp2cli and oh-my-claudecode any time (not imported); host-setup entries stay.
- `docs/research/saved-searches/`, `github-topics.toml`: after C1-4.
- `.agent/kb/raw/` (DF-7): after the C1-1 tarball receipt.
- `.claude/types/` (DF-8): after KB-A's CT-31 row 1 regenerates the declarations in MP.
- `graphify-out/` (DF-9): any time; derived.

**knowledge-base:**
- `sources/<name>/` clones (11 GB): after C1-5's parity report maps all 99 manifests and the enabled rows hold
  receipts.
- `sources/*.manifest`, `sources/REGISTRY.md`, `sources/*.pages.toml`, `sources/groups/`: after C1-5 (their
  rows survive as `imported_from`).
- `sources/media/` (KB-2): after rows 1, 14, 31, 36 to 38 hold receipts and the `transcripts` and
  `unpinnable-pages` archive rows resolve; then Q2 decides KB's history.
- `sources/extractions/`, `sources/graphify-native-extract/`, `graphify-out/`, `.agent/kb/native-extract/`:
  after CT-55's adopt-or-drop note.
- `docs/research/` (KB-5) and `.agent/kb/reports/`, `.agent/kb/raw/` (KB-6): after C1-1 and C1-2; the six
  reports KB-A names (section 1.4 there) resolve as `own-reports` rows.
- `docs/currency/` (KB-7): after CT-47 and KB-A's CT-22b row 1.
- `.firecrawl/`: any time. `.claude/types/`: after KB-A's CT-31 row 1.
- Then the repository: archive read-only on GitHub (or private, per Q2).

**TR:**
- `offline/` (3.2 GB): after C1-5 maps all 43 packages; nothing in it needs archiving except `intel.json`
  provenance, which C1-1's allow-list export keeps.
- `docs/`, `searches/`, `learnings/`: after C1-1's allow-list export receipt, C1-2's index and C1-4.
- `original/`, `generated/`: never imported; their fate is the user's (Q4, D81).
- Then the checkout: it has no remote, so the C1-1 export is the only copy MP relies on.
