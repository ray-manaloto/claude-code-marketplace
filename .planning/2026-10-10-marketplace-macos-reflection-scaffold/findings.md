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

Strict-five research is incomplete: Context7 quota exhausted; Firecrawl Search
HTTP 402 with provisional Serper/webclaw fallback; Last30Days internal no-results
statuses rejected by the installed validator. Do not relabel these as successes
or repeatedly retry known quota failures. This chat acquired pinned GitHub
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
  rollouts of threads `01a130ef` and `01a12bd1`; the heartbeat in `01a12bd1` fails on the same error.
- Thread roles: `01a127db` onboarding writer (2a14); `01a130ef` source writer, completion contract,
  A06 units, A09 publications up to `848552c`; `01a12bd1` LLVM/RF peer, specs #79–#83, tickets
  #84–#108, `codex/marketplace-remaining-work` at `0195289` (unpushed); `01a13185` agent-protocol
  side project touching this repo only with four `#:schema` lines in the `c658` worktree.
- Unpublished local tip: `c6caaca`, `d2a4103` (T1 import). A06 unit3 is uncommitted in the
  `a06-retrieval-refresh` worktree at `b4922e6`: `dev/codex_examples.py`
  `d2b8852f1bf70153644b88e90c80fc17d80e74ca20b6ef06c9c9e64b729f2a65`, `dev/test_codex_examples.py`
  `3b90b03b3fda0e65fabbe3117a00b9b90d87b4adf8532779afb6574ce01dba61`,
  `docs/agents/codex-example-classification.md`
  `8fa79da1b2dceec4be0a3374e0df2d347907a3245e9e7a7a48853bcd617ba82a`,
  `retros/a06-classification-methods.md`
  `7961e1c95e060443a3e9e2f5786198f5f869031ffe20bba6b6bc7f12f2931afb`.
- Merging `codex/marketplace-remaining-work` conflicts only in `docs/agents/ticket-retro.md`
  (item 5 wording; HEAD carries the user-confirmed per-lane barrier) and `mise.dev.toml`
  (both sides added tasks); the other both-touched files are byte-identical except three lines
  in `docs/onboarding.md`.
- `.gitignore` is one of the 19 frozen baseline files; local-only ignores go in `.git/info/exclude`.
- Codex record stores and how to read them: the `codex-session-history` skill (lane SKILL).
