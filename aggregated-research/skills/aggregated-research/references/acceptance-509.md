# Acceptance criteria — issue #509

Pinned **before** the skill was written (P1 of the Aggregated round), so the skill
is built against these rather than judged by them afterwards. Everything here is
from `gh issue view 509`, read 2026-08-27. Do not paraphrase it into something
easier to satisfy — that is the Goodhart move the round's rider names.

## The 5-step sweep, cheapest-refutable-first

The ordering is the substance. #509's worked run went source-last and paid for it:
an artifact and two commits were produced before anyone asked whether the behaviour
was already known upstream. It was — for fourteen months.

1. **The installed binary.** `<tool> --help`, then a probe in a throwaway
   directory. The ONLY step that can answer questions no document addresses
   (does it warn? does it read `.gitignore`?).
2. **The shipped source at the pinned ref.**
   `gh api repos/OWNER/REPO/contents/PATH?ref=TAG`. `?ref=` goes **inside the path
   string**; `-f ref=v8.30.1` 404s. Source beats issue tracker.
3. **Both trackers — issues AND PRs AND discussions.**
   `gh api -X GET search/issues -f q='repo:OWNER/REPO TERM'`, never `gh search issues`.
4. **Breadth: Firecrawl `developer-index`, then web.** Returns full issue bodies and
   comment threads inline, so maintainer comments arrive without a follow-up fetch.
5. **Synthesis by a strong Claude lane that opens the URLs itself.** Research leads
   are breadth, not truth.

Step 0 is unchanged and hook-enforced: `mise run kb-query` first
(`research-doc-sources.md`). This skill extends that chain, it does not replace it.

## The 5 traps — each a check the skill RUNS, not prose it states

| # | Trap | The check |
|---|---|---|
| 1 | `gh search issues` returns `[]` instead of failing — its control query with 39 real results also returned `[]` (#507) | never use it; `gh api -X GET search/issues`, and every null carries an arm in the same block |
| 2 | The channel may not exist. `repo:jdx/hk gitleaks` → "zero issues" reads as *nobody reported it*; **jdx/hk has issues DISABLED** | `gh api repos/OWNER/REPO` → check `has_issues` / `has_discussions` BEFORE interpreting a tracker null |
| 3 | A cited reference can contradict what it annotates (#508) | open the citation, do not trust the annotation |
| 4 | Stale-PATH version skew — a lane reported hk 1.56.0 from the bare shim while the pin says 1.56.1 | version probes go through `mise exec --` |
| 5 | An agent's factual claims need spot-checking — a breadth lane asserted neither repo was in the corpus; both manifests exist | spot-check every lane's factual claims against the repo |

## What good looks like

A run has earned its keep when it ends with:

- **A ranked source list**, primary sources separated from secondary.
- **Every null result carrying its control arm.** A "not found" without a control is
  a lead, not a finding — the single rule most responsible for #509's worked report
  being trustworthy.
- **The channel checked** before a tracker null is interpreted.
- **An explicit "not measured" section.** #509's most useful lines were the ones
  saying what had NOT been checked.
- **The repos-touched enumeration** `research-repo-enumeration.md` requires, which
  also feeds `sources/REGISTRY.md`.

## The 3 test prompts

1. *"Is this behaviour a known bug in `<tool>`, and has anyone reported it?"* — the
   worked upstream case.
2. *"What do other projects do about `<problem>`?"* — the breadth case, where the
   answer is a practice rather than a fact. **The one most likely to expose a weak
   skill**: no primary source to anchor on, so it tests whether confirmed can still
   be separated from anecdotal.
3. *"What tools should we be using to research questions like this?"* — the
   self-referential case Ray asked for, so the tool list stays current rather than
   frozen at what was installed the day the skill was written.

## Tool ranking from the worked run

**Earned their place:** `gh api -X GET search/issues` (best by a wide margin) ·
`gh api repos/.../contents/...?ref=TAG` (decisive) · the installed binary itself ·
Firecrawl `firecrawl_search` with `categories: ["developer"]`.

**Not needed on that question, stated so the list is not padded:** Exa (would have
duplicated Firecrawl), Context7 (library API docs; the answers were in a README and
in source), plain WebFetch/WebSearch, and the graph — neither upstream repo's
question was in the corpus, though **both repos ARE pinned sources**, so a
`kb-query` may serve where the answer is in ingested code.

## Decisions already ruled (do not re-derive)

| question | ruling |
|---|---|
| Scope | **Both** a general multi-source sweep and the upstream/dependency case, the latter as the worked example |
| Output | A report under `docs/research/reports/`, **plus a published artifact when the answer is a decision someone has to make** |
| Build method | `skill-creator`'s full loop |
| Docs style | `/mattpocock-skills:writing-for-agents` |
| Naming | `aggregated-research` |
