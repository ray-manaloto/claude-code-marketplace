# Grill round 3: every open item that needs the user (2026-10-14)

Typed by the user: `/mattpocock-skills:grill-with-docs all open issues or what needs my input`
(session `ccm-20261014`, `skill-invocations.md` third typing). Numbering continues from rounds 1-2
(Q1-Q38). Facts gathered read-only: decisions ledger, plan, 94 open GitHub issues, `docker system
df -v`, a dotfiles state check (Explore agent), `webclaw --version`, `.github/workflows/`.
Recommended answer after each question; "yes" accepts it. Answers are recorded as D-rows and DL rows.

| Q | Subject | Recommendation |
|---|---|---|
| Q39 | Schema direction (D82 Q1) for #26, CT-52, CT-53 | committed schema files are the single source; CT-52 generates Python, #26 generates C++ records, CT-53 is a reflection check that the records map back to identical schemas |
| Q40 | D68 disk gate (D82 Q2) | max(60 GiB, 1.5x the largest measured peak of the same run class) |
| Q41 | D82 splits and merges (D82 Q3; amends D71-D73) | approve all (P2 §2) |
| Q42 | CT-34 transcript read before the fold (D82 Q4) | admit read-only, masked digests, sessions `b74a0bf1` and `ce9c0b3d` |
| Q43 | Docker volumes (D80) | delete 20 unused dotfiles home volumes (about 23 GB), 8 symphony build caches (about 8 GB) and 2 anonymous volumes (about 0.5 GB) after a read-only content check per home volume; keep the in-use dotfiles volume and the symphony auth and state volumes |
| Q44 | Pin `PWF_PLAN_ROOT` and `PWF_TRUSTED_PYTHON` in `.claude/settings.local.json` `env` now (D54) | yes, literal values for this checkout; CT-37 still decides the general carrier (D73) |
| Q45 | Standing admission for qualified closes between waves | yes: one at a time, each only with its accepted-evidence receipt, a notice per close |
| Q46 | Standing admission for bounded webclaw fetches and clones (CT-33, CT-41, CT-42) | yes: webclaw 0.6.23 as pinned; spike at most 10 pages; at most 60 pages per source, robots respected, concurrency 2, delay 500 ms; one sparse blob-less clone per source under its size cap; disk gate 60 GiB plus twice the source cap |
| Q47 | Dotfiles mods D66 and D62: none exists yet | a separate dotfiles session builds both now from a brief written here; this repo's CT-35 and CT-36 stay the backstops and adoption tests |
| Q48 | Where `claude plugin validate --strict` runs (CT-57) | the acceptance OCI job (already installs claude 2.1.251); CT-26b raises that pin; host `check` stays free of claude |
| Q49 | Plugin `version` (CT-57; `--strict` exits 1 without it) | `0.1.0` in CT-08's baseline re-record; CT-57 fails when plugin files change without a bump |
| Q50 | #101 T4 (DL-3, DL-80) | close as superseded by the takeover spec (D63); its unapplied #79-#82 parent batch becomes ordinary qualified closes; no fourth attempt |
| Q51 | #91 B2, human-only Codex Desktop repair | the user does it after Codex returns (2026-10-19), with the D80 Codex disk follow-ups |
| Q52 | Unlabelled #4 and #9 (acceptance files CT-08 unfreezes) | label `ready-for-agent`, fold into CT-26b's acceptance, close when CT-26b lands |
| Q53 | CT-28 claude-agent executor readiness (G2 `git init` of three user-level skill trees, G3 `uv sync --locked` elsewhere) | do not file; the native executor needs neither; record as dropped |
| Q54 | Typed stages timing | at the gate after wave 0c, in a fresh session: setup-matt-pocock-skills, "publish spec", `/to-tickets` |
| Q55 | Idle peer session `ccm-20261013` (pid 51306) on this checkout | the user closes it with `/exit` |

Later, asked when the wave arrives (no answer needed now): container build (CT-26b, wave 2); fresh
`claude -p` session (CT-37, wave 9); transcript reads for live runs (CT-20a, CT-51); graphviz pin
(CT-54); graph tool binary (CT-55); fnox profile and cost cap (CT-46, wave 20); merging draft PR
#109 into `main`; the Codex disk follow-ups after 2026-10-19 (D80).

## Answers (interactive, 2026-10-14, on the iOS app)

| Q | Answer | Recorded |
|---|---|---|
| Q39 | schema files are the source (recommended) | D83, DL-111 |
| Q40 | per run class (recommended) | D84, DL-112 |
| Q41 | approve all (recommended) | D85, DL-113 |
| Q42 | admit read-only (recommended) | D86, DL-114 |
| Q43 | delete the 30 after the check and every symphony volume | DL-105, DL-106 (51 removed) |
| Q44 | asked for research (F4), then "write and probe now" | D91, DL-119..DL-121, F4b |
| Q45 | standing admission (recommended) | D86, DL-114 |
| Q46 | no limits at all, after the parent raised the IP-block and disk risk | D86 |
| Q47 | mods in this repo as a local directory plugin; migrate the best of the three projects, then sunset them; build Claude versions of Codex's two agent skills | D87, D88, ADR 0006 |
| Q48 | host fast check | D89 |
| Q49 | 0.1.0 plus bump check (recommended) | D89 |
| Q50 | close #101, after an explanation | D90, DL-107..DL-110 |
| Q51 | after 2026-10-19 (recommended) | D90 |
| Q52 | fold into CT-26b (recommended) | D90, DL-107 |
| Q53 | new ticket CT-59 replaces CT-28 (the recommendation was not to file; CT-59 added) | D88 |
| Q54 | at the gate (recommended) | D90 |
| Q55 | the user closes it with /exit (recommended) | D90 |
| Q56 | agent workflow tooling plus offline docs, repos, documentation, blogs and articles | D87 |
| Q57 | launch the import review now (recommended) | D87; `reviews/ccm-20261014/project-import/` |

## Rounds 4-5 (interactive, 2026-10-14, session `ce9c0b3d`)

Asked on the project-import reports (round 4, Q58-Q67) and on A2 section 4, `research5/` R1-R3 and
`reprioritize-3/Q2-order.md` section 6 (round 5, Q68-Q83). Subjects and answers are read from the
session's question tool calls; Q65 and Q73 were never asked (no question call carries either
number).

| Q | Subject | Answer | Recorded |
|---|---|---|---|
| Q58 | Naming needs no mod (DF-A: a SessionStart hook can name the session) | build up the mods library; prefer mods over hooks | D92, DL-122 |
| Q59 | Drop the automatic forced plugin reload | keep the reloads at session start, as done by hand | D93, DL-123 (amended by D103) |
| Q60 | Where the mods plugin lives | a TypeScript library with a modern setup, CI/CD and mise, hk, fnox | D94, DL-124 |
| Q61 | The WebFetch deny hook cannot fire under `--bare` or `--safe-mode` | a Claude mod | D95, DL-125 |
| Q62 | Move the knowledge-base trackers module here and drop the pin | move it here (recommended) | D96, DL-126 |
| Q63 | dotfiles' knowledge-base dependency at sunset | point it at this repository | D96, DL-126 |
| Q64 | Visibility of knowledge-base and dotfiles | after their blockers (recommended) | D96, DL-126 |
| Q65 | not asked | none | none |
| Q66 | Move the existing settings hooks into mods | migrate all, delete hooks | D92, DL-122 |
| Q67 | Lane w0-session-hooks | fold into the mods library (recommended) | D97, DL-127 |
| Q68 | Mod loading gaps; then, with R1, keep the three deny gates as hooks | first: research through the two-stage route; then: keep them, documented, rules, watched | D100, DL-130; D102, DL-132 |
| Q69 | The shipped plugin's SessionStart hook | convert it too | D99, DL-129 |
| Q70 | Bug #92533 (Bash hooks and worktree-isolated subagents) | research first, follow the issue | D100, DL-130 (R2) |
| Q71 | Awaiting the plugin reload; then, with R3 | research first; then await and drop `--force` (recommended) | D100, DL-130; D103, DL-133 |
| Q72 | w0-doctor's new SessionStart hook | merge as reviewed, delete later (recommended) | D101, DL-131 |
| Q73 | not asked | none | none |
| Q74 | Run the A2-0 spike at the gate | yes, and asked whether `/prototype` applies (Q79) | D104, DL-134 |
| Q75 | D71 reading: three units beside CT-39 | yes, with per-ticket context and duration tracking | D105, DL-135 |
| Q76 | The #13 fallback | research first and automate it | D106, DL-136 |
| Q77 | The dotfiles host lock | asked for an explanation and diagrams; then, on the explainer, this repository owns the lock | D109, DL-139; D110, DL-140 |
| Q78 | Corpus crawl against the heavy-run disk gate | adapt to load and disk; look for existing tools first | D107, DL-137 |
| Q79 | How A2-0 runs | spike lane, prototype rules (recommended) | D104, DL-134 |
| Q80 | CT-73's twelve units | keep all 12 (recommended) | D108, DL-138 |
| Q81 | A2-8's private-input admission | carry it over (recommended) | D108, DL-138 |
| Q82 | D99 against the remote switch (#99130) | prefers a mod; asked how to detect the switch before any thin wrapper | not recorded (Q2-order-v2 §6 U4) |
| Q83 | The gate scripts against D60 | asked why a synced environment is slow, how to speed it up, or whether the gates could be C++26 | not recorded (Q2-order-v2 §6 U2) |
