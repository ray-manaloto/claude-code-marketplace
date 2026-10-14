# Sweep B — packet and T4 state for the CLOSE lane

Read-only sweep of `qbj4yn5d/` (packet, last write 2026-10-13T14:07:45Z) and
`~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/` (state dir), per
R3 "Sweep brief B". Tip checked: `9cd396a` (84 commits past `848552c`; `d2a4103` is an
ancestor via M0 `05c3dc9`; `MERGE_HEAD e12cf04` in progress, untouched). GitHub re-queried
read-only: #62–#78 OPEN with `ready-for-agent`; #79–#83 OPEN, no labels; #101 OPEN.

## 1. Closure prerequisites per ticket (rows for `ticket-ledger.md`)

Common holds stated by every packet inventory (`closure-preparation/issue6x-*`): (a) qualified
acceptance-close operation (`issue:completion-preview` → `issue:apply` → `issue:verify`, evidence
JSON with `acceptance/review/retro/delivery` receipt bindings; contract in state dir
`t4-parent-metadata/closure-preflight/report.md`), (b) fresh live issue/body/label/native-edge
preimages, (c) peer issue-write slot release, (d) per-issue admission, (e) settled retro and
parent acceptance, (f) prerequisite ticket disposition. Every inventory binds source
`d2a41032` and the T1 `check:research` receipt `5a235e38…` (rc 0, 118 static + tracker tests,
baseline 19); the #62 JSON inventory observed tip `848552cd`. Both SHAs are now behind
`9cd396a`; bound file bytes re-hashed at the tip: 19 of 23 still match, 4 drifted (below).

| Issue | Packet file(s) | Verdict recorded | Still required before qualified close | Hash-bound inputs behind the tip |
|---|---|---|---|---|
| #62 A01 | `issue62-evidence-inventory.json`, `issue62-current-evidence.md`, `issue62-archival-criteria.md`, `issue62-archival-review.json`, `a01-archived-execution.json` (`f6651126…`) | `CODE_CRITERIA_READY` (reviewer `/root/a01_archival_review`) | common (a)–(e); "final parent closure packet"; limits: A09 original publish-process receipts not located, A12a owns CI, Claude/container acceptance pending | `dev/bootstrap.py`, `dev/mise`, `mise.dev.lock`, `uv.lock`, `pyproject.toml`, `dev/empty-mise.toml` match tip; **`mise.dev.toml` (`c4b5d68f`→`81f7dfcd`, CT-01/skill/M0) and `docs/onboarding.md` (`ef9732b8`→`3e65c4dd`, M0) drifted** |
| #63 A02 | `issue63-criteria.md`, `issue63-review.json`, `issue63-archival-criteria.md`, `a02-archived-execution.json` (`deb74daa…`), `issue63-readonly-1/` | map PASS; readiness `PARTIAL_NOT_YET_READY`; archival supplement awaiting independent review (`lane-ledger.issue63_closure_preparation.status`) | #62 disposition; independent review of the archival supplement; accept "producer process exit / wire-request count unbound" as an evidence disposition; common (a)–(d) | captures live only in `2a14` (`20261012T193651Z-cc501ef6`, replay `…eb12ab90`, raw `5b95fc70…`); `dev/github_search_one_page.py` hash not recorded by the inventory |
| #64 A03a | `issue64-inventory.md`, `issue64-criteria-review.json` | `CODE_CRITERIA_READY` | #66 (→#63) disposition; common (a)–(e) | `dev/collect_saved_search.py` `c8a449e1`, test `067dc8f7` match tip; capture `codex-schema--1791836388445290000--8385f42d…` lives only in `2a14` |
| #65 A03b | `issue65-inventory.md`, `offline-criteria-review-65-66-67.json` | `CODE_CRITERIA_READY` | #64 disposition; common | `dev/control_saved_search.py` `85ad8943`, test `56d01cb9` match; capture `…1791837279871878000--59b358fe…` only in `2a14` |
| #66 A04 | `issue66-inventory.md`, same review | `CODE_CRITERIA_READY` | #63 disposition; common | `dev/search_catalog.py` `39cce567`, test `cca6326c`, `dev/saved-searches.toml` `95505e9d` match; two fixture captures only in `2a14` |
| #67 A05a | `issue67-inventory.md`, same review | `CODE_CRITERIA_READY` | #65 and #66 dispositions; common | `dev/search_compare.py` `b1f506ea`, test `b225ffa3` match |
| #68 A05b | `issue68-inventory.md` | `CODE_CRITERIA_READY` | #67 disposition; common; no fresh live/provider claim | `dev/search_publish.py` `b92d90c9`, test `3c1d4b6d` match; comparison receipt `…780ef2a027d3c66a--96dbbeb7…` only in `2a14` |
| #69 A06 | no closure inventory; `lane-ledger.lanes[0]` | unit3 "independently accepted; separate commit/integration preparation next" (Claude integrated as `8f783a0`) | closure inventory never written; retained corpus + schema (`evidence/codex-examples/…`, `evidence/saved-searches/runs`) exist only in `2a14` (R3 P1-1); full ticket acceptance; common | lane `integration_base_head 848552cd`, `worker_head b4922e66`, `local_commit e1fdc24f` (unit2), `candidate_sha256 96b5dd74…` |
| #70 A07a | `issue70-inventory.md` | `CODE_CRITERIA_READY` | #66 disposition; **"T3 current-helper-byte refresh"** now due; common | **`dev/issue_amend.py` `3983910e`→`63f59b20`, `dev/test_issue_amend.py` `a73e3ab9`→`21716791`** (T3 `101f760`/`fa3ab5c` via M0); `docs/agents/issue-tracker.md` `d3a2b79d`, `mise.dev.toml` drifted as above |
| #71 A07b | `issue71-inventory.md` | `CODE_CRITERIA_READY` on frozen inputs + cached `graph/spec11.json` (`6fdff521…`) | #70 disposition; helper-byte refresh; fresh live #11 postimage read (cached state is not fresh); common | `retros/A07b.md` `f503a787` matches; `spec-11-amendment-candidate.{md,json}` (`5dfc7a31…`/`9e719f49…`) and `evidence/issue-publication-private/A07b.*` only in `2a14` |
| #72 A08a, #73 A08b, #74 A09, #75 A10, #76 A11, #77 A12a, #78 A12b | **none** — no `issue7[2-8]` file in `closure-preparation/`; packet `progress.md` stops at #62 archival (14:07Z) | not prepared | an inventory/criteria map, independent criterion review, then common (a)–(f); #78 additionally waits for A06 acceptance | nothing hash-bound in the packet; ledger cites tip commits only (`3972f3b`, `906cdbc`, `bcf9760`, `42d94f9`, `a8ecd40`) |

Ledger note: the packet calls the needed close tool "qualified acceptance-close tooling"; the
T3-extended `dev/issue_amend.py` at the tip is that tool (`issue:completion-preview`), so (a)
is satisfiable now, but every `CODE_CRITERIA_READY` verdict was reviewed against the pre-T3
helper bytes.

## 2. T4 answers

**Postimages.** `t4-parent-metadata/postimages/` holds three prose files that target tracked
**repo files**, not issue bodies: `docs/research-feedback-retro/README.md` (1,192 B, sha
`d985783b…` vs tip `5df75191…`), `ticket-draft.md` (5,185 B, `89ca068d…` vs `715e4e79…`),
`workflow-authority-amendment.md` (1,526 B, `a1bf47cc…` vs `b10e34a1…`); all three differ from
`9cd396a`. `t4-phase-a-brief.md` plans five maintained outputs: those three plus
`docs/remaining-work/README.md` (prose draft is `t4-parent-metadata/remaining-readme.md`,
1,952 B; path absent at the tip and on `codex/marketplace-remaining-work`) and a generated
`tracker.json` (not yet produced). `metadata-plan.md`: apply only after the T4 worker releases
its checkout, via the A09 route, "keep the real metadata delta uncommitted until A09 consumes
it".

**`phase-c-policy-v2.md` requirements** (sha `a099ad7d…`, parent-accepted 12:19Z as
"preparation only, `native_go: false`"): add exactly `ready-for-agent` to the 25 children,
no label/body change on the 5 spec parents; the ten historical closures are RF1–RF4, W1 and
RF-SPEC1–4 (#79–#82), bound to accepted scope/review/retro/delivery receipts; children close
before parents; B1/T1/T2/T3/T4/#83 stay open; independent review of generated closure packets
before any completion apply; one 60-minute active cap and immutable attempt identity shared by
label, snapshot, review and completion stages (review time does not pause it); checkpoints
predeclared and expiry-rejecting; both all-state graph audits plus a separate all-state reader
reconciling all 30 identities/titles/bodies/labels/parents after closure
(`poststate-audit.md`); "**This policy does not grant a fourth attempt**"; no source edit,
Git mutation or A-series mutation in the issue interval.

**TERMINAL state and budgets** (`recovery-attempt3/TERMINAL.json`): `status STOPPED`,
`native_status NOT_COMPLETED`, `reason "TimeoutError; stop all new sends"`, 1,672 active s of
3,600; 99 commands; 25 labels `VERIFIED`; children batch RF1, RF2, RF3a, RF3b, RF4, W1 closed
and `VERIFIED` (`sent: true`); parent batch: previews for #79–#82 ran (cmds 096–099, exit 0)
then `checkpoint-refusal-parents.json` = `REFUSED / MISSING_APPROVAL_WAIT_EXHAUSTED` after a
901.8 s wait (cap 900 s) — the parent completion intents were never applied.
`original_budget 3/3`, `recovery_budget 3/3` (extension of 10:48Z authorized by the user's
"Continue om"; `t4-recovery-extension-20261013.json`). `QUEUE.json`: issued 13:53:25Z,
start deadline 13:58:25Z. A new attempt therefore needs a fresh user-approved budget and a
fresh issue-write interval (`next_rf_operation_requires_new_interval: true`), a repeated
children-state preflight, and the parent packets rebuilt from fresh preimages.

## 3. What Codex's `lane-ledger.json` still claims (14:07:45Z)

- `source_writer_allocation.owner "/root"` (01a130ef), `observed_base_head d2a41032`, status
  "Source d2a41032 pinned pending A06 outcome acceptance"; top-level status "…source848552cd
  reserved".
- `shared_git_allocation.owner "/root"`: "no worker mutation admitted".
- `shared_check_allocation.owner "/root"`: RELEASED by the A06 worker (release `9a504839…`).
- `heavy_operation_allocation: null`.
- `issue_write_allocation.owner 01a12bd1`: bounded T4 recovery interval, "at most three
  attempts" — all three consumed; no release record after attempt 3 (the last release,
  `peer-t4-release.json` 10:14Z, predates the recovery grant).
- Lanes: `#69/A06 unit3` (`/root/a06_methods`, worktree `a06-retrieval-refresh`, base
  `848552cd`), `#28` and `#29` offline units (both "accepted/published", worktrees listed as
  `cleanup_candidates`); `tracker_t1_preparation` ("accepted locally; no publication",
  `source_GO false`), `tracker_t3_preparation` hold `672f0dae…` "waits for A06 integration".
- Closure preparations #62–#68, #70, #71 "no closure", reviewer `/root/issue25_closure_review`.
All of these are superseded: M0 published d2a4103 + T1/T3 + A06 unit3 to the tip, Claude is
the sole writer, and the T4 interval expired with its budget.

## 4. Supersession notice (for `docs/agents/claude-takeover.md`)

The Codex coordination state in `/var/folders/…/marketplace-completion-workflow-qbj4yn5d/lane-ledger.json`
(last write 2026-10-13T14:07:45Z) and `~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/`
is superseded by this activation record and is read-only history. Its source-writer and
shared-Git slots (`/root`, pinned at `d2a41032`/`848552cd`), its A06/#28/#29 lane rows, its
T1/T3 import holds and its T4 issue-write interval (01a12bd1, three recovery attempts, all
consumed, final state `STOPPED/NOT_COMPLETED`) are no longer live: the integration tip has
moved past both SHAs (M0 `05c3dc9`, A06 unit3 `8f783a0`, T3 helper `fa3ab5c`), the Claude
session is the sole integration writer, and every slot, hold and attempt budget must be
re-admitted from the Claude lane records (`lanes/*.json`, `ticket-ledger.md`). A Codex thread
resuming after 2026-10-19 — including the `refresh-llvm-github-research` automation, which may
only write under `github-research/` — must read this record first, must not act on the packet
ledger's owners, reservations or "closure pending" dispositions, and must not start a T4
parent-spec closure (#79–#82) or any ticket close without a new user-approved budget and an
admission recorded here.

## Could not verify

- `docs/remaining-work/README.md` and `tracker.json` final bytes: never produced; only the
  prose draft `remaining-readme.md` exists.
- Whether the children's live closed state on GitHub still matches `verified-child-closure-outcomes.json`
  (not re-queried beyond #62–#83 titles/labels; R2 scope).
- `dev/github_search_one_page.py` binding for #63: the inventory records no hash, so drift
  cannot be judged (tip `11217328…`).
- The `2a14` capture directories cited by #63–#68, #71 (hashes taken from the inventories; the
  worktree was not opened — Sweep A).
- Whether a release of the T4 issue-write interval was ever sent after attempt 3; no file after
  `t4-recovery-issue-interval.json` (13:55:57Z, `attempts_started 3`) records one.
- `checkpoint-refusal-parents.json` names no approver; whether the 900 s wait was for a parent
  review inside 01a12bd1 or for a user message is not stated.
