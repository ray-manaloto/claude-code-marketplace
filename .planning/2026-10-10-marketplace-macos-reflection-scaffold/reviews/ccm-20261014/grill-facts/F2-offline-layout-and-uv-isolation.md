# F2: offline layout (U3) and native uv tooling and isolation (U6)

Read-only fact report from a general-purpose subagent of session `ccm-20261014` (`ce9c0b3d`),
2026-10-14, for the Phase 4a grill. No network was used. Scratch experiments:
`/private/tmp/claude-501/-Users-rmanaloto-dev-github-ray-manaloto-claude-code-marketplace/ce9c0b3d-0e2d-4354-8e4c-fa478b12ea34/scratchpad/facts/`
(`proj/`, `attack/`, `pp/`, `pp2/`, `lockprobe/`). Abbreviations: TR =
`<TR>`, MP = this repository, DF = the dotfiles repo,
KB = the knowledge-base repo.

## Part A: TR offline docs and repos layout

- Layout: `offline/` holds 43 package folders (Y4 §2 says 44), each with `README.md` (index),
  `intel.json` (manifest) and `reports/`; pages in `site/` or `crawl/{markdown,llm,json}/` with
  `snapshot.json`; source in `git/` (depth-1 clone), some with `repos/github/<org>/<repo>`.
  `docs/` = project docs and `reports/`; `learnings/` = `registry.json` only; `original/` = 7 input
  private documents.
- Fetch tool: webclaw `"github:0xMassi/webclaw" = "0.6.23"` (TR `mise.toml:10`). Chain:
  `mise run deps:intel` runs `uv run dependency-intel intel` with 6 injected secrets
  (`mise.toml:139-149`), which calls `webclaw <url> --crawl --depth --max-pages --output-dir
  -f <fmt> --timeout [--metadata --sitemap --path-prefix]` (`src/dependency_intel/extractor.py:708-728`);
  repos by `git clone --depth 1` (`extractor.py:515`); defaults `[tool.webclaw]` depth 100,
  `max_pages = 0`, formats markdown/llm/json (`pyproject.toml:228-234`).
- Manifest and receipts: one `intel.json` per package (version, `git_commit_sha`,
  `retrieval_timestamp`, `"extractor": "WEBCLAW"`, `crawled_pages[]` with path, source_url,
  token_count; `offline/webclaw/intel.json:1-30`). No top-level manifest, no hashes, argv or exit
  codes. Git tracks 7,784 files under `offline/`; `.gitignore:9-10` excludes only
  `offline/**/git/` and `offline/**/repos/`.
- Agent instructions: AGENTS rules 18-20 (`AGENTS.md:100-109`: workspace-relative paths, no test
  output into tracked `offline/`, secret-scan exclusion); `CLAUDE.md:16` (reports under
  `offline/<pkg>/reports/`); `.agents/agents/research-synthesizer.md:28`;
  `.agents/skills/dependency-intel/SKILL.md:20`; `.agents/skills/last30days/SKILL.md:79` uses an
  absolute `file:///Users/...` link, which breaks rule 19.
- Size (`du -sh`): `offline` 3.2G (`*/git` 2.5G, `*/repos` 577M, `*/site` 108M, `*/crawl` 16M,
  `*/reports` 0.3M); `docs` 752K, `original` 732K, `learnings` 20K, `generated` 13M.
- Against MP's Y4 plan: TR commits its page mirror, MP keeps `/offline/` untracked and tracks only
  `dev/offline-sources.toml` and immutable `evidence/offline/runs/*/manifest.json` (Y4:83-100);
  TR's `intel.json` is unhashed and rewritten in place, MP's per-run receipt holds the binary
  sha256, argv, exit code, robots decision and per-file sha256 (Y4:153-158); TR crawls unbounded in
  3 formats, MP crawls one format with page and size caps, `--concurrency 2 --delay 500`, and a
  model-free `offline:query` (Y4:124-137).
- Agent's one-line recommendation: TR is reference data only; follow Y4's untracked-plus-receipt
  design.

## Part B: native uv, ruff and ty

1. DF (`python/pyproject.toml`): `[project.scripts] dotfiles-setup = "dotfiles_setup.main:main"`
   (:48-49); setuptools (:51-53); src layout `python/src/dotfiles_setup`; groups `dev` (pytest,
   xdist, ruff, ty, unpinned), `test-observability`, `codegen`, `default-groups = ["dev","codegen"]`
   (:75, :204-230); `[tool.ruff]` (:77-163) with root `ruff.toml:8` `extend =
   "python/pyproject.toml"`; `[tool.ty.environment]` (:184). Tasks: `mise.toml:293` `uv run
   --project python dotfiles-setup lint`, `:297` `... gate`, `:305` `... sdlc-team`, `:317` `uv run
   --project python python -m dotfiles_setup.pytest_runner ...`. hk: `hk.pkl:63` `uv run --project
   python ruff check {{files}}`, `:86` `ruff format --check`, `:105` `ty check --project python
   python/src tests plugins`.
   KB (`pyproject.toml`): scripts `kb-setup`, `aggregated-research` (:39-41); hatchling
   `packages = ["python/src/kb_setup"]` (:92-101); `dev` pins `ruff==0.16.5`, `ty==0.0.77`;
   `codegen` group; `default-groups` (:59-69, :313); `[tool.ty.environment]`, `[tool.ty.src]`
   (:266-275). Tasks: `mise.toml:494` `uv run pytest ...`, `:602` `uv run kb-setup eval`, `:614`
   `uv run kb-setup skill-lint`, `:773` `uv run kb-setup check`. hk: `hk.pkl:419` `uv run ruff
   check {{files}}`, `:424` `uv run ty check python/src tests`, `:612` `uv run ruff format --check`.
2. MP today: `pyproject.toml:1-8` = `githubkit==0.16.1` and `[tool.uv] package = false`; no
   scripts, groups, ruff or ty config; `hk.pkl` has only retro-gate steps (:12, :18).
   `mise.dev.toml`: `"${MARKETPLACE_PYTHON:-python3}" -B|-I dev/x.py` for bootstrap, check,
   git_delivery, checkout (:21-41, :118-234); `uv run --no-sync --offline python -B dev/x.py` for
   network-backed scripts (:48-319); `-I` only at :134, :323, :333, :338, :348. Dev scripts import
   siblings through `sys.path[0]` = `dev/` (`collect_saved_search.py:18-22`, `issue_edges.py:14-16`,
   `checkout_switch.py:12-13`); hooks re-add their dir (`hooks/pretooluse_gate.py:20`).
   `MARKETPLACE_PYTHON` is unset and defined nowhere; `python3` resolves to
   `.mise/installs/python/3.15.0/bin/python3` with a clean PATH, to `.venv/bin/python3` (3.15.0) in
   the session PATH; one record had `~/.local/share/mise/installs/python/3.14.8/bin/python3`
   (`evidence/p2996-registration/preparation-review.json:356`).
3. Isolation test (uv 0.13.0, Python 3.15.0; planted `json.py` in cwd; `PYTHONPATH` marker):

   | Form | Planted cwd `json.py` | `PYTHONPATH` | Sibling import | `sys.path[0]` |
   |---|---|---|---|---|
   | `python3 -I s.py` / `uv run python -I s.py` | blocked | ignored | fails | stdlib zip |
   | `uv run python -I -m pkg.mod` | blocked | ignored | n/a | stdlib zip |
   | `uv run python s.py` / `uv run s.py` (script outside cwd) | blocked | applied | ok | script dir |
   | same, script in cwd | SHADOWED | applied | ok | cwd |
   | `uv run -m pkg.mod` / `uv run python -m pkg.mod` | SHADOWED | applied | n/a | cwd |
   | `uv run probe` (console script) | blocked | applied; a `PYTHONPATH` `json.py` SHADOWED | n/a | `.venv/bin` |
   | `uv run --isolated ...` | as non-isolated (`-m` SHADOWED) | applied | n/a | temp env |
   | `PYTHONSAFEPATH=1 uv run -m ...` | blocked | applied | n/a | `PYTHONPATH` dir |

   User site is off in every uv venv form, on for the base interpreter without `-I`. The
   console-script wrapper execs `.venv/bin/python` without `-I`. `--isolated` is a temporary
   environment, not interpreter isolation (`sys.flags.isolated = 0`).
4. ruff and ty: installed but inactive in MP (`mise which ruff`: not currently active; ruff 0.15.12,
   0.15.19, 0.16.4, 0.16.10 and ty 0.0.32, 0.0.74, 0.0.85 installed); under `./dev/mise` only
   python 3.15.0 and uv 0.13.0 are active. Adding `[dependency-groups] dev = ["ruff","ty"]` to a
   scratch copy changes `uv.lock` (`uv lock --check` 0 then 1; `uv lock --offline` added ruff
   0.16.10 and ty 0.0.85 from cache; 426 to 488 lines). Latest-upstream status UNVERIFIED.

Agent's one-line conclusion: only `-I` (or `PYTHONSAFEPATH` with `-E`) keeps the guarantee under
uv; console scripts and `-m` do not, and `-I` breaks MP's sibling imports unless the scripts become
a package.
