# R21: dependency freshness, offline documentation and GitHub mirrors (D150)

Written by research agent R21 of the research6 team, session `ccm-20261014` (`ce9c0b3d`), 2026-10-14, for user
decision D150 ("update all dependencies with their offline documentation and GitHub mirrors";
`decisions.jsonl` row DL-193). Read-only: no `mise install|upgrade|use`, no `uv lock --upgrade`, no vcpkg change,
no tracked-file edit, no global config change. MP HEAD was `0ef449f` at the start and `77778cd` at the end
(another lane committed `e1c7be7`, `132e8e3`, `77778cd` meanwhile; none touches a pin).

Citation keys. MP = the repository root. P = `MP/.planning/2026-10-10-marketplace-macos-reflection-scaffold/`.
OFF = `MP/offline/research/R21/` (untracked through `.git/info/exclude:17`). `OFF/queries.jsonl` is the D137 log
(263 rows); `Qn` cites its row `seq = n`. `OFF/manifest.json` lists 222 mirrored items (218 files with SHA-256,
4 clones with commit SHAs). Release-note mirrors are `OFF/releases/*.md`, webclaw pages `OFF/pages/*.md`, API
copies `OFF/api/**`, issue and PR copies `OFF/gh/**`. X2 = `P/reviews/ccm-20261013/phase4-prep/X2-dependency-updates.md`
(yesterday's review, which this run refreshes). Paths that start with another run's id (`R12/`, `R13-cxx-deps/`,
`R16-provider-preflight/`, `R17/`) are under `MP/offline/research/`. Anything without a citation is labelled UNVERIFIED.

Section order follows the dispatch prompt (verdict, ecosystem tables, batches, backfill, the five log-built
sections, routes, gaps); the brief's five log-built sections appear in their prescribed internal order.

## Verdict

**Recommendation: do not run a blanket update. Ship five risk-ordered batches, of which only the first three can
land without a reviewed baseline transition, and wait out mise's 24-hour release cooldown before batch 1.**
Confidence: high for every version fact (each comes from the primary API: GitHub releases, PyPI JSON, npm,
nodejs.org, Homebrew, Docker Hub, vcpkg `baseline.json`); medium for the breakage predictions on the OCI image and
plugin runtime, because no container, acceptance or compile run was admitted.

Counts over the 55 pinned dependencies MP declares or has accepted (section 1): **38 current, 12 outdated,
5 major-outdated**. Offline coverage after this run: **20 have no mirrored documentation and 13 only partial
pages; 31 have no repository clone** (2 more are not GitHub-hosted; 2 are sparse clones). Ten of the 17
non-current dependencies sit in frozen baseline files.

Evidence that decides it:

1. Python is fully current. All 17 packages in `uv.lock` equal their PyPI latest, githubkit 0.16.1 included
   (Q74 to Q90). Nothing in the Python ecosystem needs a change, so D112's "no new Python logic" is not engaged.
2. Every C++ toolchain identity in `docs/accepted-decisions.md:97` is still the newest upstream identity: the
   `p2996` branch head is still `f17c8d6c` (Q52), IWYU `clang_21` is still `791e69ea` (Q53), GCC 16.2.0 is
   Homebrew stable and the newest `gcc-16` tag (Q93, Q242), CMake 4.4.4, Ninja 1.13.2 and sccache 0.18.0 are the
   latest releases (Q18 to Q20), vcpkg-tool 2026-09-26 is latest (Q23). vcpkg master moved four days past the
   baseline but changed 7 ports, none of which MP uses or plans (Q101, Q102). The X2 conclusion "do not file CT-27"
   still holds.
3. The `ubuntu-latest` label that all three workflows use moves to Ubuntu 26.04 in a rollout "beginning October 19,
   2026" and completing by November 19 (actions/runner-images#14748, opened 2026-09-17, Q168; GitHub changelog
   2026-09-17, Q158). That changes the runner's Python from 3.12.3 to 3.14.4 and the Docker client from 28 to 29
   (Q249, Q248). This is the only change that arrives without a pin change, and it starts in five days.
4. `jdx/mise-action` v5 changes two defaults MP depends on: v5.0.0 makes `minimum_release_age` default to 24h when
   `version` is unset, and v5.1.1 stops exporting the action's token as `MISE_GITHUB_TOKEN` to later steps
   (`OFF/releases/jdx_mise-action__v4.3.0..v5.1.2.md`; jdx/mise-action#657 closed 2026-10-04, PR #658 merged
   2026-10-04, Q163, Q164). `research-fast.yml` runs `./dev/mise run tools:prepare` and `acceptance.yml` runs
   `mise oci build` after the action, both of which download locked GitHub assets, so the bump needs an explicit
   token decision (`persist_github_token: true` or a job-level `MISE_GITHUB_TOKEN`).
5. uv's own policy is that "the minor version number is bumped for breaking changes"
   (`OFF/pages/docs.astral.sh_uv_reference_policies_versioning_.md`, Q141), so the OCI pin 0.12.7 to 0.13.x is a
   breaking bump: 0.13.0 makes Python 3.15 the default download and switches tar extraction to `tar-codec`
   (`OFF/releases/astral-sh_uv__0.12.7..0.13.1.md`). The 0.13.0 regressions astral-sh/uv#22510 (closed 2026-10-13)
   and #22492 (closed 2026-10-13) are fixed by 0.13.1 (#22516, #22522), so the development pin should move from
   0.13.0 to 0.13.1 as a patch (Q186, Q187).
6. Two baseline pins carry published security fixes: gh 2.102.0 fixes four advisories (GHSA-39wj-f2f4-978v,
   GHSA-4mq3-hpgx-9cx8, GHSA-qcwj-mr2r-2cx7, GHSA-wjmr-j3rp-mh2g; `OFF/releases/cli_cli__v2.98.0..v2.102.0.md`), and
   ty 0.0.84 fixes GHSA-vxvm-j4xq-q7m4, a use-after-free during incremental checking
   (`OFF/releases/astral-sh_ty__0.0.74..0.0.87.md`). The OCI base `debian:bookworm-slim` left regular security
   support on 2026-07-12 and is in LTS until 2028-06-30 (`OFF/pages/www.debian.org_News_2026_20260712.md`, Q144).
   These argue for scheduling the baseline transition (batch 4) rather than holding it indefinitely.
7. The project's own native freshness check under-reports on purpose: `./dev/mise outdated --bump --json` returned
   `{}` (Q251) because mise's default `minimum_release_age` of 24h for aqua, core and npm tools hides uv 0.13.1,
   published 13 hours earlier (Q252; `OFF/pages/mise.jdx.dev_configuration_settings.html.md:2316`). The user's
   global config sets `0s`, which `dev/mise` deliberately does not load. That default is a sound supply-chain
   cooldown; batch 1 should respect it and the project should state it explicitly in `mise.dev.toml`.

D112 classification: every proposed change is a pin or configuration change except two edits to the existing
`dev/bootstrap.py:22` `TOOL_BACKENDS` table (declaring hk and a secret scanner), which add data rows to existing
Python, not new functions; the reviewer should confirm that counts as an allowed fix. Any recurring freshness
report must use native `mise outdated --bump --json` and `uv tree --outdated` (both exist; Q243, Q263)
or become a C++ `rsm-core` verb; it must not become a new Python script. Moving the plugin's
`knowledge-base` pin pulls new upstream Python from another repository and is a user decision, not a refresh.

## 1. Inventory by ecosystem

Status is `current` when the pin equals the newest stable release, `outdated` for a patch or minor gap, and
`major-outdated` when the gap crosses a documented breaking boundary (semver major, uv's minor, a Debian release,
OpenSSL's major, an LTS OS image). "Offline docs" is `full` when a mirror under `MP/offline/research/*` holds the
reference documentation (a doc-site crawl, or a clone whose `docs/` or README is the documentation), `partial`
when only a few unrelated pages exist, `none` otherwise; "Repo mirror" checks for a clone whose `.git/config`
remote is the dependency's repository (snapshot 2026-10-14 about 18:30Z, 198 clones on disk, read by
`OFF/local/scripts/coverage.py` then `covreport2.py`; inputs and output in `OFF/local/`). The 19 frozen files are those in
`evidence/onboarding/baseline-files.json`.

### Development tools (`mise.dev.toml`, hooks, scanner)

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| mise | floor 2026.10.8; CI 2026.10.8; host 2026.10.10 (`mise.dev.toml:3`; `.github/workflows/research-fast.yml:25`) | 2026-10-11 | v2026.10.10 (2026-10-14) | outdated | 10.9: security fixes (URL-decoded download names), `mise oci build` no longer runs host apt hooks; 10.10: task `skip_if`. No breaking change listed (`OFF/releases/jdx_mise__v2026.10.8..v2026.10.10.md`) | no | full | yes | pin | Q7, Q122, Q228 |
| python | 3.15.0 (PBS 20261009) (`mise.dev.toml:6`; `mise.dev.lock:6-22`) | 2026-10-09 | 3.15.0 (PBS rebuild 20261013) (2026-10-09 / 2026-10-14) | current | PBS 20261013 only rebuilds (LLVM 22 to 23 toolchain, CPython 3.16.0a1 added, 3.10 dropped); same 3.15.0 | no | partial | no | pin (optional relock) | Q12, Q98, Q104, Q127 |
| uv (dev) | 0.13.0 (`mise.dev.toml:7`; `mise.dev.lock:26`) | 2026-10-09 | 0.13.1 (2026-10-14) | outdated | 0.13.1 restores sdists with hard links and full-length tar user/group names (#22516, #22522), the 0.13.0 regressions astral-sh/uv#22510 and #22492 | no | partial | no | pin | Q10, Q106, Q119, Q236, Q186, Q187 |
| hk | hk.pkl amends v2.5.0, min 2.5.0; not in `mise.dev.toml` (host global 2.6.0) (`hk.pkl:1,6`) | 2026-10-04 | v2.6.0 (2026-10-12) | outdated | agent stop hook no longer blocks in non-hk projects; Pkl loading moved to pklr; breaking only for `Builtins.ryl` (unused here) | no | full | yes | pin + config (declare in mise.dev.toml) | Q9, Q108, Q118, Q229 |
| gitleaks | not declared; A09 takes `--gitleaks-bin` (8.30.1 used at publication review) (`dev/git_delivery.py:509`; `docs/research-feedback-retro/publication-review.md:80`) | 2026-03-21 | v8.30.1 (2026-03-21) | current | current, but undeclared: the host shim has no version set (`mise ERROR No version is set for shim: gitleaks`) | no | full | yes | config (declare) | Q17, Q109, Q250 |

### Linux OCI image (`mise.toml`, `mise.lock`; frozen baseline)

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-code (npm) | 2.1.251 (`mise.toml:10`; `mise.lock`) | 2026-08-28 | 2.1.299 (npm `latest`; `next` 2.1.300; `stable` 2.1.287) (2026-10-14) | outdated | 39 CHANGELOG sections after 2.1.251; 2.1.277 removed the deprecated TaskOutput tool; 2.1.265 `--plugin-dir` accepts a folder of plugins (`OFF/releases/anthropics_claude-code__2.1.251..2.1.299.md`) | yes | full | sparse | pin (baseline transition) | Q16, Q91, Q128, Q239 |
| node | 26.8.1 (`mise.toml:11`) | 2026-08-26 | 26.12.0 (2026-10-14) | outdated | 26.x becomes Active LTS on 2026-10-28 (nodejs/Release schedule); semver-minor only inside 26.x | yes | partial | no | pin (baseline transition) | Q15, Q92, Q99, Q105, Q143, Q238 |
| github-cli | 2.98.0 (`mise.toml:12`; `mise.lock:5-50`) | 2026-08-20 | v2.102.0 (2026-09-30) | outdated | 2.102.0 fixes four advisories (GHSA-39wj-f2f4-978v, GHSA-4mq3-hpgx-9cx8, GHSA-qcwj-mr2r-2cx7, GHSA-wjmr-j3rp-mh2g) | yes | partial | no | pin (baseline transition) | Q13, Q110, Q121, Q237 |
| uv (OCI) | 0.12.7 (`mise.toml:13`; `mise.lock:141`) | 2026-08-27 | 0.13.1 (2026-10-14) | major-outdated | uv bumps the minor version for breaking changes (versioning policy); 0.13.0: default Python 3.15 for downloads, `tar-codec` default, `--require-hashes` in included constraints honoured | yes | partial | no | pin (baseline transition) | Q10, Q119, Q141, Q235 |
| jq | 1.8.2 (`mise.toml:14`) | 2026-06-20 | jq-1.8.2 (2026-06-20) | current | none found | yes | none | no | none | Q14, Q111 |
| debian:bookworm-slim base | digest `88200866…` (amd64 list, measured 2026-08-28) (`mise.toml:26`) | 2026-08-28 | bookworm-slim `7c7b2c96…` (2026-10-06); trixie-slim (Debian 13.7) (2026-10-06) | major-outdated | Bookworm regular security support ended 2026-07-12, LTS until 2028-06-30 (Debian news 20260712); Debian 13 trixie is stable | yes | partial | n-a | pin (baseline transition) | Q96, Q97, Q100, Q144, Q146 |
| apt pins (git, ca-certificates, curl, build-essential) | 1:2.39.5-0+deb12u3, 20250419~deb12u1, 7.88.1-10+deb12u15, 12.9 (`mise.toml:43-50`) | 2026-08-28 | same in bookworm / bookworm-security (madison) (2026-10-14) | current | still resolvable today; a trixie move changes all four (git 2.47.3, curl 8.14.1, build-essential 12.12) | yes | partial | n-a | pin (baseline transition) | Q215 |

### Plugin runtime (`plugins/aggregated-research/mise.toml`; frozen baseline)

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| ty | 0.0.74 (`plugins/aggregated-research/mise.toml:4`) | 2026-08-22 | 0.0.87 (2026-10-13) | outdated | 13 pre-1.0 releases; 0.0.84 fixes GHSA-vxvm-j4xq-q7m4 (use-after-free during incremental checking); new default rules (0.0.87 enables `invalid-mutable-override`) | yes | none | no | pin (baseline transition) | Q11, Q107, Q120, Q230, Q244 |
| knowledge-base (pipx git) | commit a872cb01 (2026-08-28) (`plugins/aggregated-research/mise.toml:3`) | 2026-08-28 | main f086f731 (2026-10-05) | outdated | pinned commit is not on main: compare a872cb01...f086f731 = diverged, main 109 ahead, pin 2 behind | yes | none | no | pin (baseline transition; pulls upstream Python, user decision) | Q63, Q68, Q73 |

### C++ build tools and toolchains

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| cmake | 4.4.4 (`dev/global-mise/cpp-foundation/common.toml:5-7`; `dev/global-mise/mise.*.lock`) | 2026-10-02 | 4.4.4 (2026-10-02) | current | declared only in the global profile, not in `mise.dev.toml` (X2 portability gap) | no | partial | no | none | Q18, Q112 |
| ninja | 1.13.2 (`dev/global-mise/cpp-foundation/common.toml:5-7`; `dev/global-mise/mise.*.lock`) | 2025-11-20 | 1.13.2 (2025-11-20) | current | declared only in the global profile, not in `mise.dev.toml` (X2 portability gap) | no | full | yes | none | Q19, Q113 |
| sccache | 0.18.0 (`dev/global-mise/cpp-foundation/common.toml:5-7`; `dev/global-mise/mise.*.lock`) | 2026-09-14 | 0.18.0 (2026-09-14) | current | declared only in the global profile, not in `mise.dev.toml` (X2 portability gap) | no | none | no | none | Q20, Q114 |
| clang-p2996 | f17c8d6c (`dev/toolchains/p2996_source.py:12`; `docs/accepted-decisions.md:97`) | 2026-09-24 | branch `p2996` head f17c8d6c (2026-09-24) | current | none found | no | full | yes | none | Q52 |
| GCC | 16.2.0 (Homebrew bottle) (`dev/toolchains/gcc_bottles.py:14`) | 2026-08-07 | 16.2.0 (Homebrew stable; newest gcc-16 tag) (2026-08-07) | current | none found | no | partial | no | none | Q60, Q93, Q242 |
| IWYU (p2996 lane) | clang_21 791e69ea (`dev/toolchains/iwyu_source.py:12`) | 2025-08-30 | clang_21 head 791e69ea; upstream 0.27 = clang_23 c9cbc836 (2026-10-05) | current | 0.27 targets Clang 23 (L2 upstream lane only); the p2996 fork is LLVM 21 | no | full | yes | none (L2 owns 0.27) | Q21, Q53, Q54, Q65, Q71 |
| vcpkg registry baseline | e4563094 (`vcpkg.json:4`) | 2026-10-10 | master 44ccfd88 (2026-10-14) | current | 7 ports changed since the baseline, none used or planned here | no | partial | no | none | Q55, Q101, Q102, Q241 |
| vcpkg-tool | 2026-09-26-51bf87ca (`evidence/vcpkg-bootstrap/bootstrap-review.json:39`) | 2026-09-26 | 2026-09-26 (2026-09-26) | current | none found | no | partial | no | none | Q23 |
| pkgconf | 3.0.8 (bottle) (`evidence/pkgconf-install/contract.json:3`) | 2026-10-08 | pkgconf-3.0.8 (2026-10-08) | current | none found | no | none | no | none | Q24, Q94 |

### Python (`pyproject.toml`, `uv.lock`)

| Package | Locked | Released | Latest on PyPI | Status | Offline docs | Repo mirror | Query |
|---|---|---|---|---|---|---|---|
| githubkit | 0.16.1 | 2026-08-14 | 0.16.1 (2026-08-14) | current | full | yes | Q74 |
| githubkit-schemas | 26.9.29 | 2026-09-29 | 26.9.29 (2026-09-29) | current | full | yes | Q75 |
| githubkit-schemas-2026-03-10 | 26.9.29 | 2026-09-29 | 26.9.29 (2026-09-29) | current | full | yes | Q76 |
| annotated-types | 0.8.0 | 2026-07-23 | 0.8.0 (2026-07-23) | current | none | no | Q77 |
| anyio | 4.15.1 | 2026-09-05 | 4.15.1 (2026-09-05) | current | none | no | Q78 |
| anysqlite | 0.0.5 | 2023-10-02 | 0.0.5 (2023-10-02) | current | none | no | Q79 |
| certifi | 2026.7.22 | 2026-07-22 | 2026.7.22 (2026-07-22) | current | none | no | Q80 |
| h11 | 0.16.0 | 2025-04-24 | 0.16.0 (2025-04-24) | current | none | no | Q81 |
| hishel | 1.4.0 | 2026-09-16 | 1.4.0 (2026-09-16) | current | none | no | Q82 |
| httpcore | 1.0.9 | 2025-04-24 | 1.0.9 (2025-04-24) | current | none | no | Q83 |
| httpx | 0.28.1 | 2024-12-06 | 0.28.1 (2024-12-06) | current | none | no | Q84 |
| idna | 3.20 | 2026-09-17 | 3.20 (2026-09-17) | current | none | no | Q85 |
| msgpack | 1.2.3 | 2026-09-29 | 1.2.3 (2026-09-29) | current | none | no | Q86 |
| pydantic | 2.14.1 | 2026-10-11 | 2.14.1 (2026-10-11) | current | none | no | Q87 |
| pydantic-core | 2.50.1 | 2026-10-11 | 2.50.1 (2026-10-11) | current | none | no | Q88 |
| typing-extensions | 4.16.0 | 2026-07-02 | 4.16.0 (2026-07-02) | current | none | no | Q89 |
| typing-inspection | 0.4.4 | 2026-08-12 | 0.4.4 (2026-08-12) | current | none | no | Q90 |

### C++ libraries (`vcpkg.json` and the R13 to R15 accepted set)

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| fmt | 12.2.0 (port-version 1) (`vcpkg.json:6` via baseline) | 2026-06-16 | 12.2.0 (2026-06-16) | current | none found | no | full | yes | none | Q33, Q101 |
| glaze (GLZ_REFLECTION26) | 9.0.0 (vcpkg; planned) (R13 Verdict) | 2026-09-24 | v9.0.0 (2026-09-24) | current | reflection path forced with `-DGLZ_REFLECTION26=1` (R13 item 4) | no | full | yes | none | Q34, Q101 |
| jsoncons | 1.9.0 (vcpkg; planned) (R13 Verdict) | 2026-08-07 | v1.10.0 (no vcpkg PR yet) (2026-10-05) | outdated | 1.10.0: binary parsers (bson, cbor, msgpack, ubjson) now error on bad type info; CBOR bigint change; JSON Schema type constraints (#734/#739) | no | full | yes | pin (when vcpkg lands it, or an overlay port) | Q35, Q124, Q192, Q202, Q233 |
| stdexec | vcpkg snapshot 2026-05-25 (planned) (R14 Verdict) | 2026-05-25 | no releases; tag nvhpc-26.05 (2026-05-11); main 5fc945fa (2026-10-14) | outdated | dated snapshot; vcpkg PR #52000 moved it to 2026-05-25 | no | full | yes | pin (vcpkg baseline bump) | Q36, Q56, Q64, Q101, Q194, Q221 |
| Boost.Asio | 1.92.0 (vcpkg; planned) (R14 Verdict) | 2026-08-12 | boost-1.92.0 (2026-08-12) | current | standalone asio is 1.38.2 upstream, 1.32.0 in vcpkg; not used | no | full | yes | none | Q37, Q57, Q101 |
| Boost.Hash2 | 1.92.0 (vcpkg; planned) (R15 Verdict) | 2026-08-12 | boost-1.92.0 (2026-08-12) | current | Describe P2996 backend is post-1.92 (R15 item 1) | no | full | yes | none | Q37, Q58, Q101 |
| CommonCrypto | macOS SDK (OS built-in) (R15 Verdict) | n/a | ships with the SDK (n/a) | current | none found | no | none | no | none | R15 |
| stephenberry/ut | v1.2.1 (vendored; planned) (R15 Verdict) | 2026-07-31 | v1.2.1 (2026-07-31) | current | none found | no | full | yes | none | Q40 |
| Catch2 (fallback) | 3.16.0 (vcpkg) (R13 Verdict; R15 Verdict) | 2026-08-25 | v3.16.1 (no vcpkg PR yet) (2026-10-08) | outdated | 3.16.1 deprecates throwing from reporter interface functions (docs only) | no | full | yes | pin (when needed) | Q41, Q125, Q193, Q203, Q234 |
| OpenSSL (later TLS) | 3.6.5 (vcpkg; later) (R15 Verdict Q108.3) | n/a | openssl-4.0.3 (4.0.0 on 2026-04-14) (2026-09-29) | major-outdated | 4.0: engines, SSLv3 and SSLv2 Client Hello removed, `ASN1_STRING` opaque, const-qualified X509 APIs | no | partial | no | pin (later; vcpkg still 3.6.5) | Q42, Q101, Q156 |

### CI (`.github/workflows/*.yml`)

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| actions/checkout | v7.0.1 (tag) (`.github/workflows/*.yml` (3 files)) | 2026-07-20 | v7.0.1 (sha 3d3c42e5) (2026-07-20) | current | tag, not SHA | yes (acceptance.yml) | full | yes | config (SHA pin) | Q26, Q216 |
| jdx/mise-action | v4.3.0 (tag) (`.github/workflows/research-fast.yml:23`; `.github/workflows/acceptance.yml:14`) | 2026-08-25 | v5.1.2 (sha 08ae2a09) (2026-10-12) | major-outdated | v5.0.0: `minimum_release_age` defaults to 24h when `version` is unset; v5.1.1: the token is no longer exported as `MISE_GITHUB_TOKEN` to later steps (`persist_github_token`) | yes (acceptance.yml) | full | yes | pin + config | Q8, Q117, Q218, Q231 |
| actions/upload-artifact | v7.0.1 (tag) (`.github/workflows/acceptance.yml:63`) | 2026-04-10 | v7.0.2 (sha cf430e03) (2026-10-07) | outdated | 429 retry handling; @actions/artifact 6.3.1 | yes | full | yes | pin (baseline transition) | Q27, Q123, Q220, Q232 |
| runner ubuntu-latest | floating label (= Ubuntu 24.04 today) (`.github/workflows/*.yml` (3 files)) | n/a | ubuntu-26.04 GA; `ubuntu-latest` moves 2026-10-19 to 2026-11-19 (2026-09-17) | major-outdated | actions/runner-images#14748: Python 3.12.3 to 3.14.4, Docker client 28 to 29, kernel 7.0 | yes (acceptance.yml) | partial | no | config (explicit label) | Q103, Q168, Q248, Q249 |

### Claude Code CLI

| Dependency | Pinned (where) | Pinned date | Latest stable (date) | Status | Breaking or notable changes | Baseline file | Offline docs | Repo mirror | Update kind (D112) | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Code CLI (host) | 2.1.299 (handoff; `.planning/.../task_plan.md:124`) | 2026-10-14 | v2.1.299 (`next` 2.1.300) (2026-10-14) | current | none found | no | full | sparse | none | Q16, Q91, Q250 |

### Not counted: floating or host-only dependencies

These are real dependencies but carry no version pin in MP, or live only on the host; they are listed so the
gaps are visible, not counted above.

| Dependency | Where declared | Ref today | Note | Offline docs | Repo mirror |
|---|---|---|---|---|---|
| planning-with-files plugin | `.claude/settings.json` `enabledPlugins`, marketplace `OthmanAdi/planning-with-files` | v3.24.0, head ff349ebe (2026-10-12) (Q45, Q69) | unpinned; follows the marketplace default branch | none (F4 mirrored it into a session scratchpad, not `offline/`) | no |
| mattpocock skills plugin | same, `mattpocock/skills` | v1.3.1, head 49dd158d (Q46, Q70) | unpinned | in clone | yes (R12) |
| mise plugin | same, `brentmitchell25/mise-plugin` | master f66fdcd7 (2026-10-06) (Q72) | unpinned; no releases (Q47) | none | no |
| astral plugin | same, `astral-sh/claude-code-plugins` | main f3ce88a7 (2026-02-27) (Q62) | unpinned; no releases (Q48) | none | no |
| plugin dependency marketplaces | `plugins/aggregated-research/.claude-plugin/plugin.json`, `README.md:76-79` | firecrawl-claude-plugin 3e1fb0c3, exa-mcp-server e9c3b012, context7 ef472a49, last30days-skill f4dff26b (Q224 to Q227) | unpinned by design of `dependencies` (no version field in `plugin.json`) | context7, firecrawl CLI, webclaw: R16; others none | context7, last30days: R16; others no |
| JSON schemas | `$schema` in `marketplace.json`, `plugin.json`, `settings.json` | schemastore, unversioned | CT-57 notes `plugin.json` has no `version` | none | no |
| jactionlint (D150 asks to enable it) | not declared; hk 2.6.0 ships `Builtins.jactionlint` (`OFF/releases/jdx_hk__v2.5.0..v2.6.0.md`, hk#1663) | v2.2.0, published 2026-10-14T15:59Z (Q257, Q259) | new tool if adopted; inside the 24h cooldown today | builtin doc in `R17/repos/jdx_hk/pkl/builtins/jactionlint.pkl` | no |
| betterleaks (D150 candidate scanner) | not declared; hk ships `builtins/betterleaks.pkl` | v1.9.0 (2026-09-29) (Q258, Q260) | R17 owns the gitleaks versus betterleaks comparison | builtin doc only | no |
| fnox, ctx7, firecrawl-cli, webclaw | host global mise, used by research runs | fnox 1.39.0, ctx7 0.6.1, firecrawl-cli 1.26.3, webclaw 0.6.23, all equal latest (Q28, Q246, Q247, Q44) | not MP pins | ctx7, firecrawl, webclaw: R16, R5 | ctx7, firecrawl-cli, webclaw: R16 |
| last30days local copy | the brief's local copy (`agy-graphify-research/.agents/skills/last30days`) | SKILL.md `version: "3.18.4"`; upstream v3.28.0 (Q32) | outdated host copy, not an MP pin | none | R16 clone of upstream |
| Homebrew LLVM | host default compiler, L1 candidate | 23.1.3 (Q95; llvmorg-23.1.3, Q25) | not an MP pin; X2 already fed it to #96 | none | R4 holds a 23.1.1 tree |

## 2. Update batches, ordered by risk

Common rules for every batch: one writer in one worktree; run the named checks from that worktree only (AGENTS.md
"Gotchas"); record actual exit codes; end at the retro gate (`docs/agents/ticket-retro.md`). "Named checks" below
means `./dev/mise tasks validate`, `./dev/mise run check`, `./dev/mise run check:acceptance-baseline` and
`./dev/mise run check:research`. No batch needs new Python logic.

### Batch 0: policy, no version change (config; allowed now)

- Make the cooldown explicit: add `minimum_release_age = "24h"` (or the user's choice, for example `7d`) under
  `[settings]` in `mise.dev.toml`, so the dev environment's behaviour no longer depends on mise's built-in default
  (`OFF/pages/mise.jdx.dev_configuration_settings.html.md:2294-2316`; Q252). Locked versions still install
  regardless (`OFF/pages/mise.jdx.dev_dev-tools_mise-lock.html.md:481`).
- Earliest admission times for today's releases under a 24h cooldown: uv 0.13.1 after 2026-10-15T05:15Z (Q10),
  mise 2026.10.10 after 2026-10-15T10:12Z (Q7), node 26.12.0 after 2026-10-15T15:22Z (Q15), jactionlint 2.2.0 after
  2026-10-15T15:59Z (Q257).
- Checks: named checks; `./dev/mise run deps:check`.

### Batch 1: patch-level, non-baseline (CT-26a scope)

| Change | Files | Kind |
|---|---|---|
| mise floor and CI pin 2026.10.8 to 2026.10.10 | `mise.dev.toml:3`; `.github/workflows/research-fast.yml:25` | pin |
| uv (dev) 0.13.0 to 0.13.1 | `mise.dev.toml:7`; `mise.dev.lock` through `./dev/mise run deps:lock` | pin |
| optional: relock python 3.15.0 onto the 20261013 standalone build (same CPython, rebuilt toolchain) | `mise.dev.lock` | pin (skip unless relocking anyway) |

Breaking notes: none listed for mise 10.9 or 10.10 (`OFF/releases/jdx_mise__v2026.10.8..v2026.10.10.md`); 10.9
fixes `mise oci build` running host apt hooks against the image, which the OCI build uses. uv 0.13.1 is
fixes and enhancements only (`OFF/releases/astral-sh_uv__0.12.7..0.13.1.md`, section 0.13.1).
Checks: named checks; `./dev/mise run tools:prepare`, `deps:check` (it must still refuse a tampered binding, X2
AC3), `test:bootstrap`; then one green research-fast CI run on the published tip with its run ID recorded at A09.

### Batch 2: minor, non-baseline (CT-26a part B and CT-82)

| Change | Files | Kind |
|---|---|---|
| hk 2.5.0 to 2.6.0, declared and locked in the project (D150 "sync hk to its latest release") | `hk.pkl:1,6`; `mise.dev.toml` `[tools]`; `mise.dev.lock`; `dev/bootstrap.py:22` `TOOL_BACKENDS` plus its drift test | pin + config; the bootstrap edit is a data row in existing Python |
| declare the secret scanner the A09 publish and the CT-82 pre-push guard run (gitleaks 8.30.1 today, or betterleaks 1.9.0 if R17 says so) | `mise.dev.toml`; `mise.dev.lock`; `dev/bootstrap.py:22` | config |
| C++ planned libraries: no file change yet | none | hold |

hk 2.6.0 is breaking only for `Builtins.ryl`, which MP does not use, and moves Pkl loading to pklr
(`OFF/releases/jdx_hk__v2.5.0..v2.6.0.md`; X2 section 2b). The package URL form in `hk.pkl:1` is unchanged in
2.6.0 (`R17/repos/jdx_hk/docs/pkl_introduction.md:16`, commit `eb9a1496`). For the C++ set, jsoncons 1.10.0 and
Catch2 3.16.1 have no vcpkg port PR yet (Q192 and Q193 are empty with working controls Q202 and Q203, whose newest
merged updates are #53330 jsoncons 1.9.0 on 2026-08-09 and #53633 catch2 3.16.0 on 2026-08-27), and the vcpkg
baseline bump to master `44ccfd88` changes no port MP uses (Q101, Q102). Adopt them by a later baseline bump, not an
overlay port, unless a jsoncons 1.10.0 fix becomes necessary (its 1.10.0 changes are in CBOR, BSON, MessagePack,
UBJSON and JMESPath, plus JSON Schema type constraints, #734 and #739; `OFF/releases/danielaparker_jsoncons__v1.9.0..v1.10.0.md`).
Checks: named checks; `hk validate`; `./dev/mise exec -- hk --version` prints 2.6.0 under `dev/mise`;
`./dev/mise run test:hooks` with the HkHooks cases run, not skipped (X2 AC2); `test:bootstrap`; `deps:check`.

### Batch 3: major, non-baseline CI (CT-26a; decide before 2026-10-19)

| Change | Files | Kind |
|---|---|---|
| `jdx/mise-action` v4.3.0 to v5.1.2, pinned by SHA `08ae2a091c038e1e05ec6f5115dc5c69d5a2a6b8` with a `# v5.1.2` comment (Q218) | `.github/workflows/research-fast.yml:23` | pin |
| token for later steps: `persist_github_token: true`, or export `MISE_GITHUB_TOKEN: ${{ github.token }}` on the `tools:prepare` step | same file | config |
| `actions/checkout` pinned by SHA `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1, Q216) | `research-fast.yml:19`, `development.yml:15` | config |
| `runs-on`: either pin `ubuntu-24.04` now and move to `ubuntu-26.04` after one green run there, or accept the automatic move | `research-fast.yml:16`, `development.yml:12` | config |

The explicit `version: 2026.10.8` input keeps v5's 24h delay out of the mise binary selection
(`OFF/repos/jdx_mise-action/action.yml:15-17`, `README.md` at commit `cd026961`; Q138). The token change is in
`OFF/repos/jdx_mise-action/README.md:273-300` and `src/github-token.ts:7`. GitHub's own guidance is to pin actions
to a full commit SHA (`OFF/pages/docs.github.com_en_actions_reference_security_secure-use.md`, Q152).
Checks: named checks (they are static and do not exercise the workflow); then one research-fast CI run on the
published tip, green, run ID recorded, before and after the label decision.

### Batch 4: frozen-baseline transition (one reviewed transition; CT-08 or a CT-08b row; needs admitted acceptance)

All of these sit in the 19 frozen files, so they move together through one versioned baseline transition with a
new `evidence/onboarding/baseline-files.json` and an admitted container acceptance run (`ci/acceptance.sh`), never
piecemeal.

| Change | File | Risk and note |
|---|---|---|
| gh 2.98.0 to 2.102.0 | `mise.toml:12`, `mise.lock` | security fixes (finding 6); minor |
| ty 0.0.74 to 0.0.87 | `plugins/aggregated-research/mise.toml:4` | security fix GHSA-vxvm-j4xq-q7m4; new default diagnostics in the LSP; `ci/acceptance.sh:251` checks only the install name |
| claude-code 2.1.251 to 2.1.299 (npm `latest`), or 2.1.287 (npm `stable`, Q91) | `mise.toml:10`, `mise.lock` | 2.1.277 removed the deprecated TaskOutput tool; the smoke step reads the pin from `mise.toml` (`.github/workflows/acceptance.yml:26-34`) |
| node 26.8.1 to the first 26.x release after it enters Active LTS on 2026-10-28 | `mise.toml:11`, `mise.lock` | `OFF/pages/github.com_nodejs_release.md:29` |
| uv (OCI) 0.12.7 to 0.13.1 | `mise.toml:13`, `mise.lock` | breaking: Python 3.15 becomes the default download for `uv tool` installs in the image, which can force source builds for the knowledge-base dependency tree that `mise.toml:46-49` already notes for tree-sitter-dm (UNVERIFIED until the acceptance run) |
| Debian base: refresh the bookworm-slim digest (minimum) or move to trixie-slim with re-measured apt pins | `mise.toml:26`, `:43-50` | bookworm is LTS-only since 2026-07-12; a trixie move changes git to 2.47.3, curl to 8.14.1, build-essential to 12.12 (Q215) and reads `OFF/pages/www.debian.org_releases_trixie_release-notes_issues.en.html.md` first |
| `jdx/mise-action` v5.1.2 plus token decision; `actions/upload-artifact` v7.0.2 (SHA `cf430e03`, Q220); SHA pins; explicit `runs-on` | `.github/workflows/acceptance.yml:9,12,14,63` | `mise oci build` downloads locked GitHub assets after the action, so the v5.1.1 token change matters here too |
| knowledge-base pin a872cb01 to a main commit | `plugins/aggregated-research/mise.toml:3` | user decision: the pin is not on main (Q68: diverged, main 109 ahead, pin 2 behind) and the bump pulls new upstream Python |

Checks: `check:acceptance-baseline` must fail on the edited tree before the transition record and pass after it;
named checks; `./dev/mise run test:delivery`; the admitted `mise oci build`, the in-image `claude --version` smoke
step, and the full `ci/acceptance.sh` sequence (container, provider and fresh-session acceptance need their own
admission per AGENTS.md).

### Batch 5: later or owned elsewhere (no action in this plan)

- OpenSSL 3.6.5 (vcpkg) versus upstream 4.0.3: only when R15's later TLS need appears; 4.0 removes engines and
  SSLv3 and makes `ASN1_STRING` opaque (`OFF/releases/openssl_openssl__openssl-4.0.0.json`, Q156).
- IWYU 0.27 (`clang_23` `c9cbc836`, Q54, Q71) and LLVM 23.1.3 stay with the L1 and L2 upstream lane (#96, #99), as
  X2 section 3 recommended.
- stdexec: vcpkg carries the 2026-05-25 snapshot (PR #52000, Q194); upstream has no releases (Q36) and main moved
  to `5fc945fa` on 2026-10-14 (Q64). Take the next vcpkg snapshot with a baseline bump.
- Debian trixie, if batch 4 only refreshes the bookworm digest.

## 3. Offline mirror backfill list

R21 already added: clones of `jdx/mise-action` (`cd026961`), `actions/checkout` (`f548e57e`),
`actions/upload-artifact` (`cf430e03`) and IWYU `clang_21` (`791e69ea`, the pinned commit) under `OFF/repos/`
(Q253 to Q256); webclaw pages for the mise lockfile, settings and CI docs, the mise-action README, uv's versioning
policy, hk configuration, the Node release schedule, Debian's bookworm LTS notice and trixie release information
and issues, glaze's P2996 page, vcpkg versioning, the Claude Code plugin marketplace and manifest references and
GitHub's secure-use reference (Q138 to Q155, Q245); and release-note ranges for every outdated pin
(`OFF/releases/`). Still missing, in priority order (docs URL, then repository and a clone shape that respects
D86's "no page limit" while avoiding pointless giant trees):

| Priority | Dependency | Documentation to mirror (`webclaw <url> -f markdown`) | Repository (`git clone --depth 1 --filter=blob:none`) |
|---|---|---|---|
| 1 | uv | https://docs.astral.sh/uv/reference/cli/ ; https://docs.astral.sh/uv/reference/settings/ ; https://docs.astral.sh/uv/concepts/projects/sync/ | astral-sh/uv |
| 1 | ty | https://docs.astral.sh/ty/ ; https://docs.astral.sh/ty/reference/configuration/ ; https://docs.astral.sh/ty/reference/rules/ | astral-sh/ty |
| 1 | knowledge-base | its README at the pinned commit | ray-manaloto/knowledge-base (full clone, both a872cb01 and main) |
| 1 | gh | https://cli.github.com/manual/ (index plus `gh_api`, `gh_search_*`, `gh_issue_*`) | cli/cli |
| 1 | python 3.15 | https://docs.python.org/3.15/whatsnew/3.15.html ; https://docs.python.org/3.15/library/ | python/cpython sparse `Doc/` only; astral-sh/python-build-standalone |
| 1 | Debian base | https://www.debian.org/releases/trixie/release-notes/ (all chapters); https://wiki.debian.org/LTS/Using (Q145 returned 76 bytes; retry) | docker-library/official-images `library/debian` file only (exists, Q262) |
| 2 | node 26 | https://nodejs.org/docs/latest-v26.x/api/ (index) | none (docs only; the tree is large) |
| 2 | jq | https://jqlang.org/manual/ | jqlang/jq |
| 2 | sccache | (docs live in the repo) | mozilla/sccache |
| 2 | cmake 4.4 | https://cmake.org/cmake/help/v4.4/ (manual index, presets, `cmake-toolchains`) | Kitware/CMake sparse `Help/` |
| 2 | gcc 16 | https://gcc.gnu.org/onlinedocs/gcc-16.2.0/gcc/ ; https://gcc.gnu.org/gcc-16/changes.html (have) | none (docs only) |
| 2 | vcpkg and vcpkg-tool | https://learn.microsoft.com/en-us/vcpkg/reference/vcpkg-json ; https://learn.microsoft.com/en-us/vcpkg/users/triplets ; https://learn.microsoft.com/en-us/vcpkg/users/buildsystems/cmake-integration | microsoft/vcpkg sparse `versions/` plus `ports/{fmt,glaze,jsoncons,stdexec,boost-asio,boost-hash2,catch2,openssl}`; microsoft/vcpkg-tool |
| 2 | pkgconf | https://github.com/pkgconf/pkgconf (README, man pages) | pkgconf/pkgconf |
| 2 | CommonCrypto | local `man 3cc CC_SHA256` copied to text (the SDK man page; no web reference was checked, UNVERIFIED) | apple-oss-distributions/CommonCrypto (exists, last push 2025-05-07, Q261) |
| 2 | runner images | https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2604-Readme.md (raw copy in `OFF/api/registry/`, Q248) | actions/runner-images sparse `images/ubuntu/` |
| 2 | planning-with-files, mise-plugin, astral plugins, firecrawl-claude-plugin, exa-mcp-server | each README | OthmanAdi/planning-with-files; brentmitchell25/mise-plugin; astral-sh/claude-code-plugins; firecrawl/firecrawl-claude-plugin; exa-labs/exa-mcp-server |
| 3 | pydantic, pydantic-core | https://docs.pydantic.dev/2.14/ | pydantic/pydantic; pydantic/pydantic-core |
| 3 | httpx, httpcore, hishel, anyio | https://www.python-httpx.org/ ; https://www.encode.io/httpcore/ ; https://hishel.com/ ; https://anyio.readthedocs.io/en/stable/ | encode/httpx; encode/httpcore; karpetrosyan/hishel; agronholm/anyio |
| 3 | annotated-types, anysqlite, certifi, h11, idna, msgpack, typing-extensions, typing-inspection | each README | annotated-types/annotated-types; karpetrosyan/anysqlite; certifi/python-certifi; python-hyper/h11; kjd/idna; msgpack/msgpack-python; python/typing_extensions; pydantic/typing-inspection |
| 3 | OpenSSL (later) | https://docs.openssl.org/master/man7/migration_guide/ | openssl/openssl (only when adopted) |
| 3 | claude-code | full CHANGELOG is mirrored (`OFF/releases/anthropics_claude-code_CHANGELOG.md`, 1,014,006 bytes); docs are covered (70 pages) | widen R9's sparse clone (root files plus `mods/`) only if needed |

Priority 3 follows D112: the Python dependency tree is meant to shrink, so mirror it last. A recurring backfill
belongs to the CT-33 webclaw corpus core and the `21-offline` lane, not to a new script.

## 4. Queries sent to each tool, plugin or service (stage 1), exact text

Preflight (D142), before stage 1: Firecrawl `firecrawl credits --json` returned `remainingCredits: -128` of 1,000
(Q1, SKIPPED, CREDITS_EXHAUSTED); Serper `GET /account` balance 1,307 (Q2); SerpApi `GET /account.json`
`plan_searches_left` 245 (Q3); GitHub `gh api rate_limit` core 4,890, search 30, code_search 10, graphql 5,000
(Q4); `ctx7 whoami` "Logged in" (Q5); Exa has no balance endpoint (Q6). All seven keys were present, checked one
named variable at a time.

| Q | Provider | Exact query |
|---|---|---|
| 129 | exa | `jdx mise-action v5 breaking change MISE_GITHUB_TOKEN persist_github_token` |
| 130 | exa | `uv 0.13.0 breaking changes default Python 3.15 tar-codec` |
| 131 | exa | `glaze 9.0.0 release notes C++26 reflection GLZ_REFLECTION26` |
| 132 | exa | `Node.js 26 LTS promotion date October 2026` |
| 133 | exa | `Debian 12 bookworm end of security support LTS 2026 trixie-slim docker image` |
| 134 | context7 | `ctx7 library mise "lockfile platforms and minimum_release_age"` |
| 135 | context7 | `ctx7 library glaze "GLZ_REFLECTION26 P2996 reflection"` |
| 136 | context7 | `ctx7 library uv "versioning policy breaking changes"` |
| 137 | firecrawl | planned `firecrawl search "mise-action v5 breaking changes persist_github_token"`; not sent (preflight) |
| 138 to 155, 157, 245 | webclaw | `https://github.com/jdx/mise-action`; `https://mise.jdx.dev/dev-tools/mise-lock.html`; `https://mise.jdx.dev/continuous-integration.html`; `https://docs.astral.sh/uv/reference/policies/versioning/`; `https://hk.jdx.dev/configuration.html`; `https://github.com/nodejs/release`; `https://www.debian.org/News/2026/20260712`; `https://wiki.debian.org/LTS`; `https://www.debian.org/releases/trixie/index.en.html`; `https://stephenberry.github.io/glaze/p2996-reflection/`; `https://indragustiprasetya.com/blog/fix-uv-0-13-0-sdist-hard-links-the-tarball-is-legal.html`; `https://openssl-library.org/news/openssl-4.0-notes/` and `.../index.html`; `https://github.com/include-what-you-use/include-what-you-use/releases/tag/0.27`; `https://www.debian.org/releases/trixie/release-notes/issues.en.html`; `https://docs.github.com/en/actions/reference/security/secure-use`; `https://code.claude.com/docs/en/plugin-marketplaces`; `https://code.claude.com/docs/en/plugins-reference`; `https://learn.microsoft.com/en-us/vcpkg/users/versioning`; `https://mise.jdx.dev/configuration/settings.html` |
| 158 | serper | `GitHub Actions ubuntu-latest migrate to ubuntu-26.04 announcement` |
| 159 | serper | `IWYU 0.27 clang 23 include-what-you-use release` |
| 160 | serpapi | `Claude Code 2.1.299 changelog plugin marketplace dependencies` |
| 161 | last30days | topic `dependency upgrade breakages uv 0.13 mise-action v5 ubuntu-latest 26.04`, explicit `--plan` with three subqueries (`uv 0.13 breaking changes upgrade`; `mise-action v5 MISE_GITHUB_TOKEN`; `ubuntu-latest 26.04 GitHub Actions migration`; sources reddit, hackernews, github), `--emit=json --quick --days 30`, `SSL_CERT_FILE=/etc/ssl/cert.pem`; plan copy `OFF/pages/last30days-plan.json` |

Primary-registry lookups (stage 1, logged one row each): `gh api repos/<o>/<r>/releases/latest` for 49 repositories
(Q7 to Q51, Q222, Q223, Q257, Q258); branch, tag and commit reads (Q52 to Q73, Q216 to Q221, Q224 to Q227, Q241,
Q242, Q261, Q262); release-note ranges `gh api repos/<o>/<r>/releases?per_page=100` (Q117 to Q127) and pinned
tags (Q156, Q228 to Q240); the Claude Code CHANGELOG (Q128); PyPI JSON for the 17 locked packages (Q74 to Q90);
npm, nodejs.org, Homebrew, Docker Hub, endoflife.date, vcpkg `baseline.json` at both refs, runner-images READMEs
and Debian madison (Q91 to Q103, Q215, Q246 to Q249); `mise ls-remote` (Q104 to Q116, Q252, Q259, Q260); local
probes and `mise outdated` (Q243, Q244, Q250, Q251); four clones (Q253 to Q256).

## 5. Results from each (hits, top results, what was used)

| Q | Provider | rc / HTTP | Hits | Top results | Used |
|---|---|---|---|---|---|
| 129 | exa | 0 / 200 | 8 | mise-action release v5.1.1; PR jdx/mise-action#658; issue #657; https://mise.jdx.dev/continuous-integration.html | yes: seeded Q162 to Q166 and Q209 |
| 130 | exa | 0 / 200 | 8 | uv CHANGELOG; newreleases.io 0.13.0; reveneau.com summary; indragustiprasetya.com hard-link post (2026-10-13) | yes: seeded Q148, Q170 to Q176 |
| 131 | exa | 0 / 200 | 8 | glaze releases; https://stephenberry.github.io/glaze/p2996-reflection/ ; `docs/p2996-reflection.md` | yes: seeded Q147, Q177 to Q180, Q207 |
| 132 | exa | 0 / 200 | 8 | https://github.com/nodejs/release ; nodejs.org 26.0.0; codeflamme.com "Node.js 26 LTS on October 28" | yes: seeded Q143, Q181, Q182 |
| 133 | exa | 0 / 200 | 8 | https://www.debian.org/News/2026/20260712 ; https://wiki.debian.org/LTS ; Debian trixie release page | yes: Q144 to Q146, Q151 |
| 134 to 136 | context7 | 1 | 0 | "Monthly quota reached. You'll receive 20 bonus API requests tomorrow" | no (ERROR, CREDITS_EXHAUSTED) |
| 137 | firecrawl | not sent | 0 | none | no (SKIPPED) |
| 138 to 157, 245 | webclaw | 0 except 149 and 157 (rc 1, "target returned HTTP 404"); 145 returned 76 bytes | 17 usable pages | mirrored under `OFF/pages/` | yes (cited throughout) |
| 158 | serper | 0 / 200 | 10 | github.blog changelog 2026-09-17 "Ubuntu 26 generally available and latest migration"; actions/runner-images#14748; #14254; community discussion #187595 | yes: seeded Q167 to Q169, Q174 |
| 159 | serper | 0 / 200 | 10 | include-what-you-use.org; the IWYU repository; AUR; Debian man page | partly: seeded Q195, Q196 |
| 160 | serpapi | 0 / 200 | 9 | code.claude.com changelog; anthropics/claude-code#51370; releasebot; Medium | yes: seeded Q183 to Q185 |
| 161 | last30days | 0 | 5 | Gentoo "A plea not to use uv-build" (2026-10-12, HN); four off-topic hits; `source_status` grounding error, GitHub 0 | no (DEGRADED) |

Registry lookups returned what section 1 tabulates; failures were Q30 (`0x-massi/webclaw` is really
`0xMassi/webclaw`, corrected at Q44), Q36, Q38, Q39, Q43, Q47 to Q51, Q222, Q223, Q240 (repositories with no
GitHub release objects; tags or commits used instead), Q61 (`mise-plugin` default branch is `master`, corrected at
Q72), Q115 and Q116 (a quoting mistake in my `mise ls-remote npm:` call; npm registry Q91 used instead), and Q126
(the python-build-standalone release list exceeded the response, retried with `per_page=5` at Q127).

## 6. GitHub issues, PRs and discussions searched (stage 2), each with its seed

Repository feature checks (D142, D147) came first. uv, claude-code, IWYU and clang-p2996 have discussions off; no
discussion query went to the last three, but the uv GraphQL query (Q173) was sent before its check (Q170) was read,
so its zero is reclassified FEATURE_DISABLED in the log rather than counted as an empty result.

| Q | Route | Query | Hits | Result | Seeded by |
|---|---|---|---|---|---|
| 162 | repo check | `gh api repos/jdx/mise-action` | 1 | issues and discussions on | 129 |
| 163 | issue view | jdx/mise-action#657 | 1 | "`github_token` is persisted as `MISE_GITHUB_TOKEN` for the rest of the job", closed 2026-10-04 | 129 |
| 164 | PR view | jdx/mise-action#658 | 1 | "make GitHub token persistence opt-in", merged 2026-10-04 | 129 |
| 165 | issue search | `MISE_GITHUB_TOKEN` in jdx/mise-action | 6 | #657, #298 "Re-exporting GITHUB_TOKEN breaks downstream actions" | 129 |
| 166 | issue search | `rate limit` in jdx/mise-action | 3 | #200, #616, #625 | 129 |
| 167, 168 | repo check, issue view | actions/runner-images#14748 | 1 | rollout 2026-10-19 to 2026-11-19 | 158 |
| 169, 174 | issue search | `ubuntu-latest 26.04` (0, EMPTY_UNVERIFIED); control `ubuntu-latest label Ubuntu 26.04 in:title` | 0; 1 | the control finds #14748, so the first form missed | 158 |
| 170 to 176 | repo check; issue searches; discussion | uv: `hard link tar-codec` 0; `0.13.0 regression` 0; GraphQL `0.13` 0 (FEATURE_DISABLED, see above); `hard links in:title` 1 (#3886, old); `uv 0.13` 11 | see hits | #22510 and #22492 found by the broad query | 130 |
| 186, 187 | issue view | astral-sh/uv#22510 (closed 2026-10-13), #22492 (closed 2026-10-13) | 1 each | fixed in 0.13.1 by #22516, #22522 | 176 |
| 177 to 180 | repo check; issue search; PR search; discussion | glaze: `GLZ_REFLECTION26` issues 0; `p2996 reflection` PRs 13 (#2895, #2817, #2815 open; #2972 "tests: vendor ut" merged); discussions `reflection` 47 (#2420 "MSVC C++26 Reflection Support") | see hits | no issue names the flag; open C++26 PRs listed, none marked as a 9.0.0 regression | 131 |
| 181, 182 | repo check; issue search | nodejs/Release `v26 LTS` | 0 | EMPTY_UNVERIFIED; the schedule page Q143 answers it | 132 |
| 183 to 185 | repo check; issue view; issue search | anthropics/claude-code#51370 (closed 2026-05-02, docs on dependency auto-install); `plugin dependencies marketplace allowCrossMarketplaceDependenciesOn` 0 | 1; 0 | no issue found for MP's manifest fields (EMPTY_UNVERIFIED) | 160 |
| 188 to 190 | repo check; issue search; discussion | jdx/hk `pklr` 2 (dependency dashboards only); discussions `2.6.0` 0 | 2; 0 | no pklr regression found (dependency dashboards only) | 118 |
| 191 to 194, 202, 203 | repo check; PR searches | microsoft/vcpkg `jsoncons 1.10.0` 0 and `catch2 3.16.1` 0, verified by controls `[jsoncons] update` (newest #53330, 1.9.0) and `[catch2] update` (newest #53633, 3.16.0); `stdexec` 13 (#52000 update to 2026-05-25, #53741 include fix) | see hits | no port update yet | 124, 125, 55 |
| 195, 196 | repo check; issue search | IWYU `clang_23` 4 (#2131, #2136 open; #2126, #2054 closed) | 4 | L2 lane input only | 159 |
| 197 to 199 | repo check; discussion; issue search | jdx/mise discussions `mise-action v5` 0; `lockfile_version 3` 2 (#13906 closed) | 0; 2 | nothing against MP's lock form | 129, 139 |
| 200, 201 | repo check; issue search | bloomberg/clang-p2996 `rebase LLVM` | 0 | EMPTY_UNVERIFIED; branch head unchanged (Q52) | 52 |

## 7. githubkit saved searches run (reproduced read-only with controls) and proposed new rows

`./dev/mise run research:collect` writes into a tracked path another lane owns, so the equivalent REST calls ran
read-only into `OFF/gh/code-search/` (`gh api -X GET search/code -f q='<query> repo:<repo>' -F per_page=5 -F page=N`).

| Q | Row id | Query | Hits | Control (README) | Verdict |
|---|---|---|---|---|---|
| 204, 205, 206 | `codex-schema` (existing, `dev/saved-searches.toml:4-13`) | `schema repo:openai/codex`, pages 1 and 2 | 878 | 161 | route healthy |
| 207, 208 | proposed `glaze-reflection26-flag` | `GLZ_REFLECTION26 repo:stephenberry/glaze` | 15 | 5 | keep |
| 209, 210 | proposed `mise-action-token-persistence` | `persist_github_token repo:jdx/mise-action` | 5 | 1 | keep |
| 211, 212 | proposed `hk-pkl-package-url` | `"releases/download" pkl repo:jdx/hk` | 39 | 62 | keep |
| 213, 214 | tried `stdexec-std-senders-macro` | `__cpp_lib_senders repo:NVIDIA/stdexec` | 0 | 1 | drop (EMPTY_VERIFIED: stdexec code does not name the macro) |

Proposed rows (not written to `dev/saved-searches.toml`; the owning lane decides):

```toml
# Dependency freshness (research R21, decision D150, 2026-10-14)
[[search]]
id = "glaze-reflection26-flag"
query = "GLZ_REFLECTION26"
repo = "stephenberry/glaze"                    # 15 hits today; control README 5
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "mise-action-token-persistence"
query = "persist_github_token"
repo = "jdx/mise-action"                       # 5 hits; control README 1
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1

[[search]]
id = "hk-pkl-package-url"
query = "\"releases/download\" pkl"
repo = "jdx/hk"                                # 39 hits; control README 62
per_page = 5
max_pages = 2
max_items = 10
timeout_seconds = 15
[[search.control]]
query = "README"
expected_min = 1
```

## 8. Stage-2 searches run against the stage-1 results (seed-to-search map)

| Stage-1 seed (Q) | What it surfaced | Stage-2 rows (Q) |
|---|---|---|
| 129 exa, mise-action | PR #658, issue #657, release v5.1.1 | 162 to 166 (searches and views), 209 to 210 (code search) |
| 130 exa, uv 0.13 | hard-link post, CHANGELOG | 170 to 176; then 176 seeded 186, 187 |
| 131 exa, glaze | `docs/p2996-reflection.md`, docs site | 177 to 180, 207 to 208 |
| 132 exa, Node 26 LTS | nodejs/Release | 181, 182 |
| 158 serper, runner label | runner-images#14748 | 167 to 169, 174 |
| 159 serper, IWYU | the IWYU repository | 195, 196 |
| 160 serpapi, Claude Code | anthropics/claude-code#51370 | 183 to 185 |
| 118 releases API, hk 2.6.0 notes (pklr) | pklr, `Builtins.jactionlint` | 188 to 190, 211 to 212 |
| 124, 125 releases API, jsoncons 1.10.0 and Catch2 3.16.1 | vcpkg port status | 191 to 193, 202, 203 |
| 55 vcpkg master; 52 clang-p2996 branch | port snapshot, fork head | 194, 213 to 214; 200, 201 |
| 139 webclaw, mise lockfile doc | `lockfile_version` | 199 |

## 9. Code examples found

- `jdx/mise-action` at `cd026961d0601d9b47ccd076fe308efae012af8d`: `action.yml:15-17` (`minimum_release_age`
  default `"24h"`), `action.yml:113` (`persist_github_token` input), `src/github-token.ts:7`, `README.md:273-300`
  (opt-in examples). Local: `OFF/repos/jdx_mise-action/`.
- `stephenberry/glaze` at `e194d23e33c0739a7214161af27e47bc9a6a4e30` (code search Q207): `docs/p2996-reflection.md:13,64,78,341`
  shows `-DGLZ_REFLECTION26=1 -std=c++26 -freflection`; local `R13-cxx-deps/repos/stephenberry_glaze/docs/p2996-reflection.md`.
- `jdx/hk` main at `eb9a14961bd96909919a58c7c8010bb0684c7af9` (Q211): `docs/pkl_introduction.md:16-17,154` with
  `amends "package://github.com/jdx/hk/releases/download/v2.6.0/hk@2.6.0#/Config.pkl"`, the exact form `hk.pkl:1`
  needs; `pkl/builtins/jactionlint.pkl`, `betterleaks.pkl` and `gitleaks.pkl` exist there (local
  `R17/repos/jdx_hk/pkl/builtins/`).
- `include-what-you-use` `clang_21` at `791e69ea` (the pinned commit): `docs/IWYUMappings.md`, `docs/IWYUPragmas.md`
  (local `OFF/repos/include-what-you-use_include-what-you-use@clang_21/docs/`).

## 10. Routes

| Stage | Route | Command shape (no secrets) | rc | Hits | Used |
|---|---|---|---|---|---|
| preflight | Firecrawl credits | `fnox ... exec -- firecrawl credits --json` | 0 | -128 credits | gap recorded |
| preflight | Serper, SerpApi account | `printf 'X-API-KEY: %s\n' "$SERPER_API_KEY" \| curl -H @- .../account`; `printf '%s' "$SERP_API_KEY" \| curl -G --url-query 'api_key@-' .../account.json` | 0, 0 | 1,307; 245 | yes |
| preflight | GitHub | `gh api rate_limit` | 0 | search 30, code 10 | yes |
| 1 | Exa | `printf 'x-api-key: %s\n' "$EXA_API_KEY" \| curl -H @- -X POST --data @<body> https://api.exa.ai/search` | 0 (x5) | 8 each | yes |
| 1 | Context7 | `ctx7 library <name> <query> --json` | 1 (x3) | 0 | no: monthly quota |
| 1 | Firecrawl | `firecrawl search ...` | not sent | 0 | no: credits |
| 1 | webclaw | `webclaw <url> -f markdown > OFF/pages/<file>.md` | 0 (x18), 1 (x2) | 17 usable | yes |
| 1 | Serper | `curl -H @- -X POST --data @<q.json> https://google.serper.dev/search` | 0 (x2) | 10 each | yes |
| 1 | SerpApi | `curl -G --url-query 'api_key@-' --url-query 'q@<file>' https://serpapi.com/search.json` | 0 | 9 | yes |
| 1 | Last30Days | `SSL_CERT_FILE=/etc/ssl/cert.pem python3 -I last30days.py <topic> --plan <json> --emit=json --quick --days 30` | 0 | 5 (1 relevant) | no (DEGRADED) |
| 1 | GitHub releases and refs | `gh api repos/<o>/<r>/releases/latest`, `.../releases?per_page=100`, `.../branches/<b>`, `.../git/ref/tags/<t>`, `.../commits/<ref>`, `.../compare/<a>...<b>` | 0 (errors listed in section 5) | 1 each | yes |
| 1 | PyPI, npm, nodejs.org, Homebrew, Docker Hub, endoflife.date, raw GitHub, Debian madison | `curl -sS -L <url>` | 0 | 1 each | yes |
| 1 | mise | `mise ls-remote <tool> [prefix]`; `./dev/mise outdated --bump --json`; `mise -C <plugin> outdated --bump --json` | 0 (2 command errors) | see rows | yes |
| 1 | git clone | `git -c core.hooksPath=/dev/null clone --depth 1 --filter=blob:none --no-tags [--branch b] <url> <dir>` | 0 (x4) | 4 | yes |
| 2 | gh issue and PR search | `gh search issues\|prs '<q>' --repo <r> --limit 20 --json ...` | 0 | 0 to 20 | yes |
| 2 | gh issue and PR view | `gh issue\|pr view <n> --repo <r> --json ...` | 0 | 1 | yes |
| 2 | GraphQL discussions | `gh api graphql -f query='search(type:DISCUSSION...)' -f q='repo:<r> <q>'` | 0 (x4) | 0, 47, 0, 0 | partly |
| 2 | saved-search equivalent | `gh api -X GET search/code -f q='<q> repo:<r>' -F per_page=5 -F page=N` plus README control | 0 (x11) | see section 7 | yes |

## 11. Gaps

- Context7 hit its monthly quota on the first call (Q134 to Q136); Firecrawl was out of credits (Q1). Both stay
  recorded gaps; webclaw, Exa, Serper and SerpApi covered the same pages.
- Last30Days returned one relevant item of five and a grounding error (Q161); no social signal was found for the
  uv, mise-action or runner changes.
- No build, container or acceptance run was admitted, so these remain UNVERIFIED: whether uv 0.13.x in the OCI
  image changes the knowledge-base tool install (default Python 3.15), whether `mise oci build` hits GitHub API
  limits without a persisted token, whether `development.yml` and `research-fast.yml` pass on `ubuntu-26.04`, and
  whether `test:hooks` runs or skips the HkHooks cases in CI (also an X2 gap).
- `mise ls-remote` and `./dev/mise outdated` honour the 24h cooldown; the global `mise ls-remote` calls (Q104 to
  Q114) ran under the user's global `minimum_release_age = "0s"` (`~/.config/mise/config.toml:18`), so they show
  newer versions than `dev/mise` would.
- The plugin `mise outdated` run (Q244) also reported the user's global `python = "3.14.8"` entry
  (`~/.config/mise/config.toml:109` lists 3.15 and 3.14.8); global configuration is out of scope here (AGENTS.md
  admission rule), noted only because D122 ties the project pin to the global 3.15.
- Offline coverage is a snapshot: R17, R18 and R20 were adding mirrors during this run, so the counts in section 1
  can only grow; rerun `OFF/local/scripts/coverage.py` and `covreport2.py` for a fresh count (they read manifests and `.git/config` only).
- `wiki.debian.org/LTS` came back as 76 bytes (Q145), and the OpenSSL 4.0 notes page returned HTTP 404 (Q149,
  Q157); the GitHub release body (Q156) was used instead.
- Release dates for GCC 16.2.0 come from the `releases/gcc-16.2.0` tag commit date (Q242), not from a gcc.gnu.org
  announcement.
