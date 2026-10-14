# P2: non-C++ ticket order after the TR import

Read-only, 2026-10-14, tip `21af565`. Keys: TP `P/task_plan.md` (lines as read; the parent edits it
concurrently), TL `P/ticket-ledger.md`, HO `RV/phase3/HANDOFF-2026-10-14.md`, FT `P/frontier.toml`,
R2 `reprioritize/R2-ticket-order.md`, W1/W2/L/T/S `tr-import/*.md`. WDI/WDR/WSH = w0-doctor
integration, w0-doctor-records, w0-session-hooks. GATE = spec fold plus the user's typed stages.
R2 still holds for wave 0, the closures of D72 and the CT-05/CT-11 -> CT-17 -> CT-25 spine.

## 1. Dependency graph (h hard, p path overlap, `*` absent from current tables)

```
WDI    -> CT-40, WDR, WSH, CT-21 cut, CT-26a, CT-29a, CT-30 (h; HO:73-103, TL:155-160)
CT-40  -> GATE (D77); CT-34 audit (h* admission kind host-read:transcripts, TP:286-287); CT-25 (p frontier.py)
WDR    -> CT-05 (p lanes.py, TL:134), CT-22b, CT-17
WSH    -> CT-02b, CT-32b (h TL:161), CT-23
D7     -> every task-row writer (p mise/tasks layout, HO:121-123)
CT-34  -> GATE (p*: classes become acceptance rows before /to-tickets, D72); CT-49 (h TP:411)
GATE   -> every CT (D59, D63)
CT-30  -> CT-29a (h TL:157)
CT-08  -> CT-26b, CT-33, CT-57, CT-14, CT-31 listing (p* baseline: mise.toml, acceptance.yml,
          plugin.json, plugin README, marketplace.json, .gitignore)
CT-26a -> CT-39 (h D71)
CT-29a -> CT-39 (p* dev/handoff.py:39 calls dev/doctor/cli.py by path; session-resume SKILL.md:23)
CT-39  -> CT-05, 07+56, 10, 11, 17, 18, 19, 20a, 22b, 23, 29b, 32a, 36, 38, 41, 43, 49, 52, 54, 57
          (h/p: package, task rows, pyproject.toml, uv.lock, hk.pkl)
CT-05  -> CT-17 (h), CT-19 (h D79), CT-25 (h)
CT-11  -> CT-17 (h), CT-33 (h W1:145), CT-43 (h)
CT-17  -> CT-25 (h)
hooks  : CT-17 x CT-02b x CT-19 x CT-32b x CT-23 x CT-35 x CT-36 (p dev/hooks/, FT:45)
CT-32a -> CT-32b, CT-31b (h)
CT-02b -> CT-32b (h), CT-38 (p* one classifier, TP:277; L:123-125), CT-18 (p git_delivery.py)
CT-49  -> CT-50, CT-51 (h), CT-25 (h* class_id binding, TP:288-289)
CT-19  -> CT-23 (h), CT-25 (h)
CT-22b -> CT-25, CT-23, CT-47 (h), CT-20b
CT-29b -> CT-37 (h D73), CT-31b (h), CT-35 (p* D61 name generator)
CT-37  -> CT-35 (p* SessionStart entry), CT-23 (p context trigger, TP:190-192)
CT-38a -> CT-44, CT-54, CT-55, CT-38b(=CT-58) (h); every skill writer (p skills tree)
CT-41  -> CT-33 (h* W1:144-145; TP:395 omits it)
CT-36  -> CT-33 (p* webclaw pin, env allow-list builder)
CT-33  -> CT-42, CT-43, CT-47 (h)
CT-43  -> CT-44 -> CT-46 -> CT-48 (h); CT-44 -> CT-45 (cxx); CT-52 -> CT-53 (cxx)
CT-20a -> CT-51 (h); CT-07+56, CT-10, CT-22b -> CT-20b (h TP:382)
CT-14  -> CT-38b (h); CT-26b -> CT-57 (h)
```

**Critical path** (hops): **GATE -> CT-30 -> CT-29a -> CT-39 -> CT-41 -> CT-33 -> CT-43 -> CT-44 ->
CT-46 -> CT-48**, three admissions on it (crawl, route, network). Priority spine (K1: length,
then out-degree): CT-39 -> CT-05 + CT-11 -> CT-17 -> CT-25. About 45 units over two lanes is
about 20 waves, so throughput, not the corpus chain, sets the end date; the chain must still
start by wave 11 or it becomes the tail.

Shared package rules CT-39 must fix once, or every later ticket collides: no per-module
`[project.scripts]` entries (ADR 0003 allows them; nothing calls them), so `pyproject.toml` stays
CT-39's; the first owner creates each subpackage `__init__.py` (`offline/` CT-41, `audit/` CT-49,
`contracts/` CT-52); one discovery task runs every package test, so no ticket edits the
`check:research` depends line; subsystem task files under `mise/tasks/` if D7 passes.

## 2. Consolidation under D59

| # | Proposal | Reason | owned_paths effect |
|---|---|---|---|
| 1 | CT-33 = W1-b only (fetch, store, receipt, verify) | TP:395 title and paths still say manifest, query, briefs, `dev/offline_corpus.py`, `.git/info/exclude`; TP:261-267 and W1:144-147 split them | CT-33: `offline/{fetch,store,verify}.py`, tests, `evidence/offline/`; `offline-sources.toml` to CT-41; skill pair and `docs/agents/offline-corpus.md` to CT-44 |
| 2 | Staleness lives only in CT-47 | `offline:status` stale list (W1:147, CT-43) and the CT-22b stale-corpus notice (TP:280) duplicate `offline:stale` and its doctor notice (W2:114) | CT-43 and CT-22b lose those rows |
| 3 | Merge CT-56 into CT-07 | after D72 CT-07 keeps only Codex roles, which `roles:verify` checks (S:63); one roster owner | `.codex/agents/*.toml`, `marketplace_dev/roles.py`, the claude-team.md roles block |
| 4 | CT-58 becomes CT-38b, rules in CT-38's table | `/Users/` and `file://` rules appear in both (S:59, S:69); one lint engine | no `guidance_lint.py` |
| 5 | CT-57's `plugin.json` `version` rides CT-08's baseline re-record | baseline file (D64); version changes update caching, a user decision (S:65) | CT-08 adds one line; CT-57 keeps `plugin_check.py` |
| 6 | Split CT-20: 20a transcript adapters, masking, exit 2 (L:117-122); 20b skill, `/session-review`, sweep surface | 20a needs only CT-39 and CT-40's admission kind; detectors move to CT-51 | one detector home `audit/detectors/`; CT-51 no longer waits for CT-07 and CT-10 |
| 7 | Split CT-29: 29a adopts the four untracked items as is before CT-39; 29b splits them into the doctor, `session:start` | CT-39 moves `dev/doctor/` and breaks the parent's handoff tool (`dev/handoff.py:39`) | 29b paths become `marketplace_dev/doctor/handoff*.py` (TP:390, HO:172 stale) |
| 8 | CT-39 absorbs: skill-bundled scripts (`frontier.py` 919 lines, five codex-session-history scripts) and the 13 raw `python3` skill lines (S:24) from CT-38; the fail-closed hook launcher (T:80) from CT-02b; test wiring from CT-12 (closes CT-01 AC2, TP:362); `development.yml:18` | D59: a module and its callers move in one change; hook commands in `.claude/settings.json` change anyway | CT-38 keeps lint, cap, sync/verify, wiring table, mirror test |
| 9 | Split CT-26: 26a pins (D71 prerequisite); 26b CI image (root `mise.toml`, `mise.lock`, `acceptance.yml:14` mise-action v4.3.0) after CT-08 | 26b edits baseline files; D59 forbids two mise-action pins | `tools:audit` joins CT-22b's toolchain-dedup detector (T:85 and T:100 describe one comparison) |
| 10 | CT-22b sheds mirror parity (CT-38), schema freshness (CT-52), docs drift (CT-54) | each check ships with what it checks | CT-22b: dedup, `mise doctor` timeout, lock freshness, `--fix` scope |

Item 7 can delay CT-39 beyond "right after CT-26" (D71) and amends D73; items 3, 6 and 8 amend
D72. The user approves every §2 row at the spec fold, and no brief cites one before.

## 3. Order (two non-C++ lanes plus the cxx slot)

| Wave | Lane 1 | Lane 2 | Parent ops; admissions |
|---|---|---|---|
| pre | WDI (serial, §2(b)) | | A09 publish; drain proposals |
| 0a | CT-40 (`frontier.py`, `plan_decide.py`, claude-team.md:131-133) | D7 spike (`mise/`) | close #12 (D70) |
| 0b | WDR (`dev/doctor/{lanes,agents}.py`) | CT-21 (`evidence/**`, `check_inputs.py`) | read-only: CT-34 audit (transcript admission), CT-33 spike (about 10 pages) |
| 0c | WSH (last, D26) | D49 tooling (`merger.md`, reviewer heredoc) | closes #24, #25, #62-#78 after CT-21 |
| gate | spec fold with CT-34 rows and §2 | | user: typed stages 1-3, §2 approvals, D80 volume choice |
| 1 | CT-08 (`.gitignore`, baseline), then CT-29a (handoff files, session rows) | CT-26a (`mise.dev.toml` 1-11, `mise.dev.lock`, `hk.pkl` 1/6) | CT-30 first (D75; user pins `settings.local.json`, D54) |
| 2 | CT-39, serial units over `dev/**`, package, rows, `pyproject.toml`, `uv.lock`, `hk.pkl`, hook commands | CT-31a (`plugins/workflow-mods/**`), CT-14 (plugin AGENTS/CLAUDE), CT-26b | update FT hot_paths; container-build admission (26b) |
| 3 | CT-05 (lane, ledger) | CT-11 (check lock, receipt envelope) | |
| 4 | CT-17 (+CT-24 rest; `stop_gate`) | CT-32a (verify; parent hunks after) | `/verify` usable from here |
| 5 | CT-02b (PreToolUse gate, classifier) | CT-49 (`audit/errclass.py`) | |
| 6 | CT-38a (lint, cap, sync/verify) | CT-19 (brief module, agents, `agent_gate`) | |
| 7 | CT-32b (Stop gates) | CT-29b (doctor handoff, session skills) | |
| 8 | CT-22b (+CT-16) | CT-50 (`retro_gate`) | P1 may swap CT-52 here |
| 9 | CT-25 (+CT-06, release, class_id) | CT-37 | fresh `claude -p` session (CT-37) |
| 10 | CT-23 | CT-18 (batch publish) | |
| 11 | CT-36 (`web:fetch`, WebFetch backstop) | CT-41 (manifest, plan) | one live page; webclaw pin |
| 12 | CT-33 | CT-52 (schemas, `codegen:check`) | crawl at most 60 pages, disk |
| 13 | CT-43 | CT-20a | transcript read for live runs |
| 14 | CT-44 | CT-51 | |
| 15 | CT-47 | CT-07+56 | network for `--live` |
| 16 | CT-42 | CT-10 | one clone, disk |
| 17 | CT-35 | CT-20b | dotfiles mod present (D66) |
| 18 | CT-31b | CT-57 | user: plugin version; `claude` in CI |
| 19 | CT-38b (CT-58) | CT-54 | graphviz install |
| 20 | CT-46, then CT-48 | CT-55 spike (scratch) | fnox profile, capped live call; binary |

Reasons in brief: CT-39 unblocks about 20 tickets and retires 28 `MARKETPLACE_PYTHON` and 27
`uv run` rows (`grep -c` on `mise.dev.toml`); CT-05 and CT-11 feed the lifecycle and stop raced
receipts; CT-32a early means every later ticket ends with `/verify` (D56) instead of owing one;
CT-02b and CT-38a freeze the command table before most skill and hook writers start; CT-49 turns
errors into checks before CT-25 binds them. Every pair is checked against FT:45 hot paths
(`dev/hooks/`, `.claude/settings.json`, `claude-team.md`, `check.py`, `lane.py`) and the skills
tree. Held: CT-28 (G2, G3), #98, #101, #91. Between waves: closes #90, #92-#94, #97; one A09
publish per integration; `ledger:sync` after `/to-tickets`; `/retro` per build session (user).

## 4. Risks

- **Missed conflicts.** Seven hook writers share `dev/hooks/` and most also `.claude/settings.json`;
  FT:45 lists `dev/` paths that CT-39 deletes and omits `mise.dev.toml`, `pyproject.toml`,
  `uv.lock`, `marketplace_dev/doctor/core.py` (CT-22b, CT-29b, CT-37, CT-47) and `.claude/skills/`.
  CT-30 owns ticket-frontier `SKILL.md` (HO:171) which CT-40 edits first. CT-49's
  `error-classes.toml` and CT-50's rewrite of 47 retro records sit in parent-owned `P/`. Whether
  `21-offline` touches `mise.dev.toml`: UNVERIFIED (P1).
- **Table errors that misorder.** TL:168 blocks CT-39 on CT-38, against D71 and TP:400. TP:395 CT-33
  lacks CT-41, CT-39, CT-11, CT-08. TP:419 CT-57 omits the version decision.
- **Unclear acceptance.** "`claude` in CI" (TP:305): the OCI image already pins 2.1.251
  (`mise.toml:10`; host has 2.1.299) while `check` runs on the host runner (`development.yml:18`):
  which job? UNVERIFIED. CT-50 "recalibrate 15 failing records" contradicts D48 "no rewrite of old
  files" (TP:520) unless it is a gate exemption. CT-38b count rule versus CT-54's generated counts.
  CT-55 has no adopt criteria. CT-35's `/usage` cache measurement may need a user-typed fresh
  session (UNVERIFIED).
- **Admissions that stall.** The CT-34 transcript read sits before the spec fold; get it in 0b. The
  dotfiles mods (D62, D66) are outside this plan; their state is UNVERIFIED, which gates CT-35 and
  CT-36. CT-26b needs a container build, a separately admitted operation (AGENTS.md Gotchas).
- **Critical path.** CT-39 moves 101 tracked `dev/**` Python files (`git ls-files dev`); against
  five files and about 300 lines per unit (`codex-task-orchestration.md:204`) it is many serial
  units, and lane 2 has only three small fillers. Whether a pure `git mv` counts toward the
  limit: UNVERIFIED. CT-29a adopts a 938-line file, over the per-file review norm. One integration
  writer plus an A09 publish per lane is about 45 serial merges; CT-18 at wave 10 cuts that cost
  and can move earlier only by displacing CT-23.
