# Y5 — Offline sources inventory (read-only)

Date 2026-10-14. Method: `gh api` repo metadata, `git/trees` subtree sums (MB, **m** = measured), releases/compare;
bounded single-page `curl` of index pages, `llms.txt`, `robots.txt` (no crawl). **e** = estimate.

## 1. Coverage matrix

Corpus = `<TR>/offline/<tool>/intel.json` (43 tools, WEBCLAW/REPO,
retrieved 2026-10-08..11).

| Source | Covered today (where) | Missing |
|---|---|---|
| Claude Code docs, changelog | Nothing mirrored; bundled-skills 2.1.296 has only `plugin-authoring` | All 257 doc pages, CHANGELOG (v2.1.299 latest), plugins/examples |
| Agent SDK / API docs | `claude-api` skill (session only) | SDK pages, cookbooks, SDK repos |
| Anthropic eng. blog | — | All posts (no RSS: `/engineering/rss.xml` 404) |
| Codex | `~/.codex/skills/openai-docs/references` (3 model/prompt files); codex-plugin-cc 1.0.6 cache; `dev/saved-searches.toml` 3 queries (`codex-schema`, `codex-config-examples`, `codex-hook-examples`) | Codex docs site, repo docs/, releases, cookbook |
| planning-with-files | Plugin cache 3.21–3.24.0 (full repo incl. docs/, CHANGELOG, llms.txt) | Nothing for 3.24.0; cache is an install artifact, not a refreshable mirror |
| mattpocock/skills | Plugin cache 1.2.3, 1.3.1 (docs/, CHANGELOG, GLOSSARY) | aihero.dev skill pages (36), newsletter |
| mise | brentmitchell25 mise skill 2.10/2.11 (cache) | mise docs, CHANGELOG — absent from corpus |
| fnox | Corpus: 15 site pages + repo at `0c2ece5b63` (v1.39.0 + 14 commits) | CHANGELOG, `skills/fnox`, releases feed |
| hk | Corpus: 12 pages + git at v2.5.0 | v2.6.0 (31 commits newer), skills `hk-configure`, `hk-debug` |
| uv / ruff / ty | Corpus: 0.12.24 / 0.16.10 / 0.0.85; astral skills 0.1.0 | Stale vs 0.13.0 / 0.17.0 / 0.0.87 |
| Python 3.15 stdlib | — | Entire docs set |
| gh CLI, git | githubkit in corpus (not gh) | gh manual, git Documentation |
| gitleaks / betterleaks | betterleaks in corpus | gitleaks docs (evidence pins 8.30.1) |
| C++ toolchain (P2996 fork, IWYU, CMake 4.4, Ninja, sccache, vcpkg, GCC 16, libc++, WG21) | Evidence packets only (`evidence/p2996-*`, `iwyu-*`, `vcpkg-*`) | All upstream docs/papers |
| GitHub Actions, OCI/Docker | — | Actions docs, action READMEs at pinned tags, mise OCI pages, image-spec |
| AgentsView | — | docs (v0.45.0) |
| webclaw, Context7, githubkit | Corpus (webclaw v0.6.23 = latest; Context7 repo + remote MCP route per AGENTS.md) | Refresh only |

`evidence/saved-searches/` and `evidence/codex-examples/` **do not exist** in this checkout (only
referenced by docs and `mise.dev.toml`); nothing to diff.

## 2. Source manifest (shape of corpus `intel.json`: url/repo · extractor · cadence · licence/robots · size · priority · why)

Ext: **site** = `llms.txt`/`.md` twins; **repo** = sparse checkout of named paths; **chg** = changelog
or releases API/atom; **blog** = named posts; **reg** = archive download.

| # | URL / repo (paths) | Ext | Cadence | Licence / robots | Size | P | Why |
|---|---|---|---|---|---|---|---|
| 1 | code.claude.com/docs/llms.txt → `/docs/en/*.md` (257 pages; hooks, skills, commands, plugins/*, plugins/mods/*, sub-agents, settings, cli-reference, memory, agent-teams, agent-sdk/*) | site | daily | Proprietary; robots allow, Content-Signal ai-input=yes | 9.5 m (llms-full.txt) | P1 | Primary contract for hooks/plugins |
| 2 | anthropics/claude-code `CHANGELOG.md` + releases | chg | daily | "All rights reserved" | 1.0 m | P1 | Version drift (X1) |
| 3 | anthropics/claude-code `plugins/`, `examples/` | repo | weekly | same | 0.7 m text | P1 | Reference plugins/hooks |
| 4 | platform.claude.com/llms.txt (764 links) | site | weekly | robots disallow `/api/` only | ~10 e | P2 | API/tool-use reference |
| 5 | anthropics/claude-agent-sdk-python (README, CHANGELOG, examples/) | repo | weekly | MIT | 0.2 m | P2 | SDK surface |
| 6 | anthropics/claude-agent-sdk-typescript (README, CHANGELOG) | repo | weekly | no SPDX | <0.2 m | P3 | SDK parity |
| 7 | anthropics/claude-cookbooks (`claude_agent_sdk/`, `skills/`, `tool_use/`, `managed_agents/`) | repo | weekly | MIT | 4.1 m | P2 | Worked agent patterns |
| 8 | anthropics/skills | repo | weekly | Mixed, no SPDX; some source-available | 11.3 m | P2 | Skill authoring examples |
| 9 | anthropic.com/engineering: `claude-code-best-practices`, `equipping-agents-for-the-real-world-with-agent-skills`, `effective-context-engineering-for-ai-agents`, `effective-harnesses-for-long-running-agents`, `harness-design-long-running-apps`, `multi-agent-research-system`, `writing-tools-for-agents`, `claude-code-sandboxing`, `claude-code-auto-mode`, `building-effective-agents` | blog | monthly (index diff) | robots Allow; copyright | ~1.5 e | P2 | Design rationale |
| 10 | claude.com/blog: `getting-started-with-claude-code-mods`, `claude-code-in-the-cloud`, `building-effective-agent-automations` | blog | monthly | copyright | ~0.3 e | P3 | Mods intro |
| 11 | anthropics/claude-code-action | repo | monthly | MIT | 3.1 m repo | P3 | Only if CI adopts |
| 12 | learn.chatgpt.com/docs/llms.txt (193 links; `.md` twins; `codex-manual.md`) — developers.openai.com/codex redirects here | site | daily | robots Allow | 3.0 m (manual) | P1 | Codex config/hooks/skills |
| 13 | openai/codex `docs/` (15 files: config, sandbox, skills, slash_commands, agents_md…) | repo | weekly | Apache-2.0 | <0.1 m | P1 | In-repo reference |
| 14 | openai/codex releases (CHANGELOG.md is a pointer, 330 B) | chg | daily | Apache-2.0 | ~0.5 e | P1 | `rust-v0.163.0-alpha.11` cadence |
| 15 | openai/codex config/hook schema files (saved-search targets) | repo | weekly | Apache-2.0 | <0.5 e | P1 | `codex_examples.py` pins schema |
| 16 | openai/openai-cookbook `examples/codex/*` + `gpt-5/codex_prompting_guide`, `using_goals_in_codex` | repo | monthly | MIT | 14.9 m (notebooks) | P2 | Codex workflows |
| 17 | openai/codex-plugin-cc | repo | monthly | Apache-2.0 | 0.2 m | P2 | Installed rescue plugin |
| 18 | openai/skills | repo | monthly | no SPDX | 4.4 m | P3 | Skill conventions |
| 19 | openai.github.io/openai-agents-python | site | monthly | MIT | ~2 e | P3 | Only if SDK used |
| 20 | OthmanAdi/planning-with-files (`docs/`, `skills/`, `templates/`, `examples/`, CHANGELOG, llms.txt) | repo | weekly | MIT | 2.9 m | P1 | Hook/plan contract (v3.24.0) |
| 21 | gilded-laurel-c7nj.here.now (repo homepage) | blog | monthly | unknown | <0.1 | P3 | Maintainer page |
| 22 | mattpocock/skills (`docs/`, `skills/`, CHANGELOG, GLOSSARY, SCOPE) | repo | weekly | MIT | 0.6 m | P1 | Standing workflow skills (v1.3.1) |
| 23 | aihero.dev `/skills-*` (36 pages incl. `skills-changelog-v13-implement-spec-pr-retro-and-glossary-md`, `skills-to-spec`, `skills-to-tickets`, `skills-implement-spec`, `skills-retro`, `skills-grill-with-docs`) | site | weekly | robots allow, ai-input=yes; copyright | ~1 e | P1 | Skill rationale |
| 24 | aihero.dev/newsletter, `/posts` | blog | monthly | copyright | ~0.5 e | P3 | Release notes |
| 25 | jdx/mise `docs/` (VitePress md; incl. `dev-tools/mise-oci`, `cli/oci/build`, tasks) | repo | weekly | MIT; site has no robots.txt | 3.4 m text | P1 | Core runner |
| 26 | jdx/mise CHANGELOG + `releases.atom` | chg | daily | MIT | 0.9 m | P1 | CalVer (v2026.10.9) |
| 27 | brentmitchell25/mise-plugin (mise skill) | repo | on bump | MIT | 0.3 m | P2 | Covered in cache |
| 28 | jdx/usage docs | repo | monthly | MIT | ~0.5 e | P2 | Task `usage` spec |
| 29 | jdx/fnox `docs/`, CHANGELOG, `skills/fnox` | repo | weekly | MIT | 1.2 m | P1 | Secrets route |
| 30 | jdx/fnox releases ≥v1.39.0 | chg | weekly | MIT | <0.1 | P1 | Version floor |
| 31 | jdx/hk `docs/`, CHANGELOG, `skills/hk-*` | repo | weekly | MIT | 1.4 m text | P1 | Git hooks (v2.6.0) |
| 32 | astral-sh/uv `docs/`, CHANGELOG, `changelogs/` | repo | weekly | Apache/MIT | 1.4 m | P2 | Refresh stale corpus |
| 33 | astral-sh/ruff `docs/`, CHANGELOG | repo | weekly | MIT | 0.7 m | P2 | Refresh |
| 34 | astral-sh/ty `docs/`, CHANGELOG | repo | weekly | MIT | 0.5 m text | P2 | Refresh |
| 35 | docs.python.org/3.15/archives/python-3.15-docs-html.tar.bz2 (unittest, argparse, json, pathlib, subprocess, hashlib, tomllib, tempfile, contextlib) | reg | per 3.15 patch | PSF; robots disallow `/dev`, `/release` | 19.6 m | P2 | Stdlib used in `dev/` |
| 36 | cli/cli `docs/` + cli.github.com/manual | repo | monthly | MIT | 1.3 m | P2 | gh issue/PR flows |
| 37 | git/git `Documentation/` (git-worktree, git-merge, githooks, git-config) | repo | per release | GPL-2.0 | 5.5 m | P2 | Worktree lanes |
| 38 | gitleaks/gitleaks README + config | repo | monthly | MIT | <0.2 e | P3 | Pinned 8.30.1 |
| 39 | bloomberg/clang-p2996 @ `f17c8d6c7bfe` (branch `p2996`; `P2996.md`, `clang/docs`, `libcxx/docs`) | repo (sparse!) | on fork bump | LLVM Apache-2.0 w/ exception (no SPDX) | ~8 e; full repo 2.3 GB | P2 | Compiler under test |
| 40 | include-what-you-use `docs/`, README | repo | per release | LLVM licence | 0.1 m | P2 | IWYU lanes |
| 41 | Kitware/CMake `Help/` @ v4.4.4 (rST) | repo | per patch | BSD-3; **cmake.org Crawl-Delay 240** | 4.4 m | P2 | Presets/toolchains |
| 42 | ninja-build.org/manual.html | site (1 page) | per release | Apache-2.0 | 0.08 m | P3 | Ninja 1.13.2 |
| 43 | mozilla/sccache `docs/`, README | repo | per release | Apache-2.0 | 0.1 m | P2 | 0.18.0 |
| 44 | MicrosoftDocs/vcpkg-docs `vcpkg/` | repo | monthly | MIT | 3.0 m | P2 | Triplets/registries |
| 45 | WG21: P2996R13, P1306R5, P3394R4, P3293R3, P3491R3, P3096R12 (pdf), P3560R2, P3795R2, P2758R5 via wg21.link | reg | per revision | Author copyright; robots allow | 2.5 m | P2 | Reflection semantics |
| 46 | cplusplus/draft (sources) | repo | monthly | no SPDX | 250 MB repo | P3 | Wording only if needed |
| 47 | gcc.gnu.org/onlinedocs/gcc-16.1.0/gcc-html.tar.gz + `gcc-16/changes.html` (`-freflection`) | reg | per 16.x | GFDL | 1.3 m | P2 | GCC 16 lanes |
| 48 | gcc-16.1.0 `libstdc++-api-html.tar.gz` | reg | per 16.x | GFDL | 16.4 m | P3 | API lookup |
| 49 | libcxx.llvm.org, clang.llvm.org/docs (upstream) | site | per LLVM release | Apache-LLVM; robots allow | ~5 e | P3 | Fork divergence |
| 50 | actions/checkout@v7.0.1, actions/upload-artifact@v7.0.1, jdx/mise-action@v4.3.0 (README, action.yml at tag) | repo | on pin bump | MIT | <0.3 | P2 | `.github/workflows` |
| 51 | github/docs `content/actions/` | repo | monthly | CC-BY-4.0 | ~10 e | P3 | Workflow syntax |
| 52 | opencontainers/image-spec; docs.docker.com/llms.txt | repo/site | quarterly | Apache-2.0; ai-input=yes | ~3 e | P3 | OCI image |
| 53 | kenn-io/agentsview `docs/` + agentsview.io/docs | repo | monthly | MIT | 2.7 m | P2 | History search (v0.45.0) |
| 54 | webclaw, Context7, githubkit, betterleaks (corpus) | refresh | monthly | AGPL-3.0 / MIT | in corpus | P3 | Keep current |

Counts: **P1 15**, **P2 24**, **P3 15** (54 rows).

## 3. P1 set (next lane mirrors first)

| Tool | Rows | Size |
|---|---|---|
| Claude Code | 1, 2, 3 | 11.2 MB |
| Codex | 12, 13, 14, 15 | ~4.1 MB |
| planning-with-files | 20 | 2.9 MB |
| mattpocock | 22, 23 | ~1.6 MB |
| mise | 25, 26 | 4.3 MB |
| fnox | 29, 30 | ~1.3 MB |
| hk | 31 | 1.4 MB |
| **Total** | 15 rows | **≈ 27 MB text** (measured except Codex releases, schema files, aihero) |

Prefer `.md` twins and sparse repo paths over HTML crawl; record commit SHA and `retrieval_timestamp`.

## 4. Legal / robots notes; what stays out

- **Private mirror only, never commit or republish:** anthropics/claude-code (LICENSE "All rights
  reserved"), Claude Code docs, Anthropic/claude.com posts, aihero.dev, WG21 papers, Codex docs prose.
  Store outside the repo or via `.git/info/exclude` (`.gitignore` is frozen).
- **Licence obligations:** webclaw is AGPL-3.0 (mirror docs; do not vendor code into the plugin);
  GCC manuals GFDL; GitHub docs CC-BY-4.0 (attribution); git docs GPL-2.0.
- **Robots/crawl:** cmake.org `Crawl-Delay: 240` → use the `Help/` tree, not the site. docs.python.org
  disallows `/dev`, `/release` → use the 3.15 archive. platform.claude.com disallows `/api/`.
  code.claude.com, aihero.dev, docs.docker.com publish Content-Signal `ai-input=yes`.
  mise/fnox/hk/astral/git-scm/agentsview sites return no robots.txt (404); still rate-limit.
- **Size traps:** bloomberg/clang-p2996 (2.3 GB), llvm-project (4.6 GB), gcc-mirror (4.2 GB),
  github/docs (2.4 GB), cplusplus/draft (250 MB), openai-cookbook (977 MB) → sparse paths only.
- **Stay out:** aihero cohorts/courses (paid), login-walled pages, ChatGPT admin/workspace pages,
  sign-up newsletters, Context7 API responses (quota-bound), anything carrying tokens.

## 5. Could not verify

- `code.claude.com/docs/en/mods` returns **404**; mods live under `/docs/en/plugins/mods/*` (10 pages).
- Exact path of the Codex config/hook JSON schema (row 15); `codex_examples.py` pins one, but the
  path was not re-resolved here.
- Codex releases total size: the 100-release API call returned HTTP 504 once; 14 stable releases on page 1.
- aihero.dev page sizes (HTML 340–480 KB each; Markdown size unmeasured); newsletter archive access.
- `gilded-laurel-c7nj.here.now` ownership (linked only from the repo homepage field).
- anthropics/skills and openai/skills per-directory licences (no SPDX at repo level).
- clang-p2996 `clang/docs` subtree size (repo too large to tree-walk; `P2996.md` exists at branch `p2996`).
- `evidence/saved-searches/`, `evidence/codex-examples/` absent; the reference store may live in another worktree or be uncommitted.
