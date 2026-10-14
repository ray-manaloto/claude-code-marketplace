# Findings

## Verified baseline

- Source HEAD: `6b5b092efa6bdf678815073db42f69fae3f07ab3`.
- Git common directory: `/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.git`.
- Clean detached worktree received; START authorized branch `codex/marketplace-native-onboarding`.
- Canonical handoff SHA-256: `d4115dd495ba9445430d9b1133e20247b2f86803a8161fcd91f15322b4cedd7c`.
- Installed `codex-cli 0.162.1`; executable entry `/Users/rmanaloto/.local/bin/codex`.
- Root `mise.toml` and `mise.lock` describe Linux OCI acceptance, not macOS development.
- Plugin runtime and data confinement are defined separately under `plugins/aggregated-research/`.

## Inherited limitations

Strict-five research has not passed, but the gap has narrowed to one provider. The latest
manifests of the three marketplace threads (`policy strict-five-v2`; 2026-10-12 17:02Z,
2026-10-13 05:10Z, 05:19Z) show `context7 = ok` (5 items), `github-discussions =
empty_verified` (canary passed) and `exa`, `firecrawl-developer`, `last30days = ok`; the only
remaining gap is Firecrawl Search provisional (`firecrawl-search provisional=True`, Serper
substitute after HTTP 402).
Manifests: `~/.codex/research-coverage/01a127db-2e65-70d1-8855-9bf2bc7bb46e/01a130e8-1fe3-7e72-90d4-a6157ed06785/manifest.json`,
`~/.codex/research-coverage/01a12bd1-cf17-70f1-9592-d554bf4860a1/01a133a2-3b51-7093-890d-1faaa3d5ca83/manifest.json`,
`~/.codex/research-coverage/01a130ef-265d-72b0-8465-80f3e4128bee/01a133aa-ecbe-7b51-b397-a43480577775/manifest.json`.
They supersede the older `01a13084-…` receipt (RESEARCH INCOMPLETE, Discussions
`empty_unverified`) and the earlier "Context7 quota exhausted" reading (R3 P2-3). A provisional
or quota-failed provider stays a gap, never a success. This chat acquired pinned GitHub
sources/releases and native mise lock metadata; it did not rerun the five-provider
comparative sweep. Attempted routes and failures are recorded in evidence.

The previous Docker census stalled. Container ownership and heavy capacity remain
unknown. START admitted read-only review and lightweight repository work.
Task 04b subsequently recorded scoped admission for seven new global mise files
and three pinned build tools. Installation and host environment checks pass;
no container or compiler build is admitted.

## Sources

Prepared handoff root:
`/Users/rmanaloto/dev/github/ray-manaloto/claude-code-marketplace/.agent/`.
Read `plans/codex-takeover-decisions-20261010.md` before older audit recommendations.
`state/codex-takeover-20261010/source-index.json` lists immutable source hashes.

## Claude takeover (2026-10-13)

- Codex stopped because of `usage_limit_exceeded` (retry after 2026-10-19), observed in the
  rollouts of threads `01a130ef` and `01a12bd1`; the heartbeat in `01a12bd1` fails on the
  same error.
- Thread roles: `01a127db` onboarding writer (2a14); `01a130ef` source writer, completion contract,
  A06 units, A09 publications up to `848552c`; `01a12bd1` LLVM/RF peer, specs #79–#83, tickets
  #84–#108, `codex/marketplace-remaining-work` at `0195289` (unpushed); `01a13185` agent-protocol
  side project. Its marketplace footprint is larger than four `#:schema` lines in the `c658`
  worktree: it also left the untracked `c658/.codex/schemas/codex-0.162.1-agent-role.schema.json`
  (238,961 B, `09f2f390…969e`, sweep A keep-private until dynamic-agents ticket 30 is admitted),
  most likely a `#:schema` line in the global `~/.codex/config.toml` (later mtime), and
  `~/.codex/skills/{codex-agent,claude-agent,.shared/agent-protocol}`, which has no VCS
  (`.shared/agent-protocol` holds 18,904 files, venv included). Ticket 30 of that graph
  (marketplace hook transition, `in-progress`, gate held) is the one item that targets this
  repository's `.codex/` and `hooks.json`.
- Codex worktree data (`2a14` HEAD `48027d2`, `c658` HEAD `6130ab5`) is snapshotted, read-only:
  `imports/codex-worktrees-20261013/` (454 files, 11.8 MB, `MANIFEST.json` SHA-256 `259f9fae…`,
  `verify.py --mirror` rc 0) and the 0700 mirror
  `~/.local/state/marketplace-imports/codex-worktrees-20261013`.
  Only the index files (README, MANIFEST, T1 report, T1 scan, verify.py, T2 plan) are committed;
  the `2a14/`, `c658/` payload stays untracked (`.git/info/exclude`) because it holds raw session
  streams and full issue bodies (sweep A keep-private: 149 files, 6.6 MB).
- The tip cites 101 paths that exist only there (T1 table): 22 untracked-class refs (58 files)
  and 79 files ignored by `~/.gitignore_global` (`*.log`, `build/`), never by the frozen
  `.gitignore`. CT-21 (`reviews/ccm-20261013/T2-import-lane-design.md`) imports 119 files
  (1,057,200 B, gitleaks 8.30.1 dir scan 0 findings), declares 18 iwyu build-tree files and the
  keep-private sets in `dev/cited-inputs.json`, and adds `check:inputs`. Until it integrates,
  `dev/codex_examples.py` fails outside `2a14`, `dev/checkout_transfer.py:17` hard-codes the
  `2a14` path, and the #63–#69, #71–#74 closure rows cannot bind their evidence (sweep B).
  The A06 (#69) inputs in question: `evidence/codex-examples/` (5 files, 239,074 B; its
  `release/config-schema.json`, 236,751 B, SHA-256
  `7933a70506e753a6e98c16800d2a76770b2af2b7295491f8f0b8e713e952027e`, equals the tip's pinned
  `SCHEMA_SHA256`) and `evidence/saved-searches/` (40 files, 368,251 B, 9 runs); the tests patch
  the path away, so `check` is green while a real run fails (SYNTHESIS P1-10).
- `docs/accepted-decisions.md` "Automation and observability clarification (2026-10-12)" (+52
  lines, user decision) exists only in `2a14`; the parent applies the hunk in Runbook step 7
  (diff in the snapshot: `2a14/modified/docs/accepted-decisions.md.diff`). It carries the
  standing mandates of the Codex interviews (01a127db turn 6, 01a130ef Q1–Q12): same named mise
  tasks for humans, agents and CI; `com::rsm::<module>` namespaces; latest-stable locked and
  qualified dependencies; one global OTel collector with 30-day default retention; three
  targets (macOS ARM64, Linux ARM64, Linux x86-64); fast hk pre-commit checks; in-file schema
  declarations; canary-checked offline replay. Whether its hunk 2 is the user's wording is
  unverified (T2).
- Every untracked `2a14`/`c658` path, with owner ticket, tip citations, size, directory hash and
  disposition (import 68 files / keep-private 149 / superseded 49), is inventoried in
  `reviews/ccm-20261013/codex-sweeps/A-private-evidence-inventory.md`; per-file rows (266, with
  SHA-256) in `A-inventory.json` beside it; R3 counted 13 untracked `2a14` paths cited by
  `retros/A02–A04.md`, `task_plan.md` (pre-rewrite line 322, now in its Appendix B) and
  `docs/status.md` (`retros/A07b.md` binds one by hash).
- Codex branches `codex/28-offline-refresh` (`ff1f977`) and `codex/29-offline-refresh`
  (`4802b02`) are absorbed into the tip through `cbb455b` and `66905b4`; deletion waits for
  the user's confirmation.
- Merging `codex/marketplace-remaining-work` conflicts only in `docs/agents/ticket-retro.md`
  (item 5 wording; HEAD carries the user-confirmed per-lane barrier) and `mise.dev.toml`
  (both sides added tasks); the other both-touched files are byte-identical except three lines
  in `docs/onboarding.md`.
- `.gitignore` is one of the 19 frozen baseline files; local-only ignores go in `.git/info/exclude`.
- Codex record stores and how to read them: the `codex-session-history` skill (lane SKILL).
  Per-thread briefs of the four Codex threads: `reviews/ccm-20261013/codex-briefs/*.brief.md`
  (digests under `codex-briefs/digests/` are not for commit, D13).

## Session review ccm-20261013 (2026-10-13)

Review of the dead takeover session `464a2816-4b5d-4665-b39a-8303cb014efb` by session
`ccm-20261013-check`; ranked findings, decisions and runbook in
`reviews/ccm-20261013/SYNTHESIS.md`.

- Root causes: 14 classes (A context budget blind; B records derived by hand; C integration
  non-resumable; D user-invoked skills emulated; E no ledger of decisions; F roles and briefs
  not machine-sourced; G subagent reports condensed; H shape-checked gates; I configuration
  composition unvalidated; J gate hooks without a corpus or latency contract; K planning files
  unstructured; L outputs in ephemeral locations; M Codex state imported by hand; N ticket
  pipeline unvalidated). Causal chains: `reviews/ccm-20261013/prevention/C1-root-causes.md`;
  binding reconciliation, wave-0 set and hook latency budget:
  `prevention/C4-coverage-check.md`; summary table: SYNTHESIS §2b.
- Environment fact (class A): auto-compaction is off in the user's personal files
  (`autoCompactEnabled: false` in `~/.claude/settings.json` and `~/.claude.json`). The takeover
  session had 0 `PreCompact` fires and died on "Prompt is too long" at 977,093 usage tokens; a
  fork inherits the parent's whole window, so the merger fork started at ≈977 K and died on its
  third tool call. Whether the `~/.claude.json` copy participates in the effective value is
  unverified (D21).
- Environment fact (class F): agent definitions load at session start. The sub-agents docs
  state the watcher covers only directories that existed at session start, so the
  `.claude/agents/*.md` files written 20:07–20:25Z inside the session were never offered;
  every lane ran as `general-purpose` and the `implementer` agent's `tdd` preload never applied.
  A session that adds or changes agent definitions must restart before dispatching them.
- mattpocock invocation constraint (1.3.1 at `49dd158`; `.agents/invocation.md:5-8,22`):
  user-invoked skills (`disable-model-invocation: true`; among them `grill-with-docs`,
  `to-spec`, `to-tickets`, `implement`, `implement-spec`, `retro`, `wayfinder`, `handoff`,
  `setup-matt-pocock-skills`) are reachable only by the human typing the slash command; no
  skill and no orchestrating session can fire one, and a `/name` inside pasted text is not
  expanded by the harness. Applying their `SKILL.md` files file-guided is not an invocation and
  no standing request is an "invocation authority"; `skill-invocations.md` records each actual
  mode. Model-invoked skills (`grilling`, `domain-modeling`, `tdd`, `code-review`, …) are
  called through the Skill tool, one skill per call.
- Codex sweep A (`codex-sweeps/A-private-evidence-inventory.md`): `2a14` holds 257 untracked
  files (7.29 MB), `c658` 64 (2.7 MB); dispositions import 68 / keep-private 149 / superseded
  49; no credential-shaped string; one user-decision block (`accepted-decisions.md`) exists
  only there; the A09 rc 2 at ~10:39Z on 10-13 is the adjudicated Context7 `api_sha256` false
  positive already recorded in the tip.
- Codex sweep B (`codex-sweeps/B-packet-and-t4-state.md`): #62 and #64–#68, #70, #71 are
  `CODE_CRITERIA_READY`, #63 `PARTIAL_NOT_YET_READY`, #69 has no closure inventory, #72–#78
  were never prepared; four hash-bound inputs drifted behind the tip (`mise.dev.toml`,
  `docs/onboarding.md`, `dev/issue_amend.py`, `dev/test_issue_amend.py`), so every
  `CODE_CRITERIA_READY` verdict was reviewed against pre-T3 bytes. T4 attempt 3 is
  `STOPPED/NOT_COMPLETED` (`TimeoutError` after a 901.8 s approval wait, cap 900 s), budgets
  3/3 and 3/3, and `phase-c-policy-v2.md` "does not grant a fourth attempt". Per-issue rows:
  `ticket-ledger.md` "Closure prerequisites". Supersession notice (text for
  `docs/agents/claude-takeover.md`):

  > The Codex coordination state in `/var/folders/…/marketplace-completion-workflow-qbj4yn5d/lane-ledger.json`
  > (last write 2026-10-13T14:07:45Z) and `~/.local/state/marketplace-llvm23-fork-01a12bd1/remaining-work-20261013/`
  > is superseded by this activation record and is read-only history. Its source-writer and
  > shared-Git slots (`/root`, pinned at `d2a41032`/`848552cd`), its A06/#28/#29 lane rows, its
  > T1/T3 import holds and its T4 issue-write interval (01a12bd1, three recovery attempts, all
  > consumed, final state `STOPPED/NOT_COMPLETED`) are no longer live: the integration tip has
  > moved past both SHAs (M0 `05c3dc9`, A06 unit3 `8f783a0`, T3 helper `fa3ab5c`), the Claude
  > session is the sole integration writer, and every slot, hold and attempt budget must be
  > re-admitted from the Claude lane records (`lanes/*.json`, `ticket-ledger.md`). A Codex thread
  > resuming after 2026-10-19 — including the `refresh-llvm-github-research` automation, which may
  > only write under `github-research/` — must read this record first, must not act on the packet
  > ledger's owners, reservations or "closure pending" dispositions, and must not start a T4
  > parent-spec closure (#79–#82) or any ticket close without a new user-approved budget and an
  > admission recorded here.

- Codex sweep C (`codex-sweeps/C-dead-children.md`): nine spawned children died inside a turn
  on the usage limit; none wrote outside private packets or `~/.local/state`, none mutated Git
  outside private clones; `01a13590` (A06 merger) wrote
  `qbj4yn5d/a06-unit3/integration-preparation/verify.py` at 14:09:07Z and `01a134c5` wrote
  `tracker-t3-source-preparation/source-import/repair-2/nested-caller/HANDOFF.json` at
  14:07:24Z, both after the packet ledger's last update and unreviewed. Replacement for the
  activation record's "no thread mid-turn" sentence:

  > No Codex root thread is mid-turn, but nine spawned children died inside a turn on the usage
  > limit (eight at 14:07–14:09Z on 2026-10-13, `01a128a0` on 10-12); they wrote only to private
  > packets and `~/.local/state`, ran no Git mutation outside private clones, and the one
  > in-flight process — Carson's T4 Phase C runner under `01a12bd1`'s issue-write slot —
  > sent six
  > child closures, then timed out waiting for a parents-batch approval and stopped at 14:21:50Z.

- Still running on the Codex side: automation `refresh-llvm-github-research` (ACTIVE, 4 h
  rrule, target `01a12bd1`, last cycle `20261013T102218Z`; writes only under
  `github-research/`, no push or publish).
- Secrets posture (N1, `reviews/ccm-20261013/N1-settings-and-secrets.md`): no secret value is in
  any project or user settings file; the staged `.claude/settings.json` problem is privacy and
  portability (personal MCP allow-list and plugins), not leakage. Keys live in
  `~/.config/fnox/config.toml` (profiles `codex_research`, `codex_publish`,
  `agentsview_recall`); the project route is the exec-scoped `fnox --config
  ~/.config/fnox/config.toml --profile <name> --no-defaults --no-daemon --non-interactive exec --
  <command>`, never a settings file or mise `[env]`. Installed fnox is 1.39.0, whose `exec`
  strips every out-of-scope profile secret from the child; the global fnox `[env]` still
  inherits the whole secret set into every shell-launched session (user decision 2026-08-02).
  `_.fnox-env` stays disabled in global mise; 1.39.0's `fnox env --json` makes a re-enable
  buildable, which is a separate ticket under macos-development-environment #75. The 1.39.0
  daemon socket and protocol (v6) changed; the `--no-daemon` route is unaffected.
- planning-with-files hazards (R4): above 1 MiB `progress.md` (`PROGRESS_LIMIT`,
  `inject-plan.py:92,1275-1277`) silences all injection, plan included; the injected progress
  view is `tail -20`, line-blind; a second plan dir (another `.planning/<slug>/task_plan.md`)
  without a pinned `PLAN_ID` silences injection; hooks firing from a lane worktree read that worktree's stale
  `.planning/` copy unless `PWF_PLAN_ROOT` is pinned (probe-verified from
  `.claude/worktrees/team`); `task_plan.md` without `### Phase` sections is invisible to every
  structural feature (smart view byte-identical to head-50).
- Orchestrator skill design (K1, `reviews/ccm-20261013/skills/K1-orchestrator-skill-design.md`):
  a `ticket-frontier` scheduler over `ticket-ledger.json` and the lane records, a context
  ceiling read from `dev/doctor/budget.py`, and an executor gate G1–G7 that must pass before
  any `claude-agent`/`codex-agent` executor replaces native Agent dispatch. The user's answers
  to its §9 are D27–D41 in `task_plan.md`; the build is ticket CT-25 (wave 3).
