---
name: aggregated-research
description: "Run a multi-source research sweep whose findings survive review — ordered cheapest-refutable-first, with a control arm on every null result and the channel checked before any tracker null is believed. Use whenever a question needs an answer from outside this repo: is this a known bug upstream, what do other projects do about this problem, what tooling should we be using, does this feature already exist, why does this dependency behave this way. Use it BEFORE building anything custom, and before reporting that something does not exist — a not-found without a control arm is a lead, not a finding."
argument-hint: "[the research question, in one sentence]"
---

# aggregated-research

`$ARGUMENTS` is the research question. With none given, ask for one in a sentence
before running step 0 — a sweep with no question drifts into a survey.

A sweep is worthless if its negatives are unarmed. This skill's whole job is to
make one discipline automatic: **every null result carries a control arm proving
the probe could have returned something else.**

Everything else here is ordering. The acceptance criteria this was built against
are pinned verbatim in `references/acceptance-509.md` — read them if a step here
looks arbitrary.

## Step 0 — the graph, if this repo has one

If this repo carries a graphify graph (`graphify-out/graph.json`), query it
first — it costs zero LLM tokens and may already hold the answer:

```bash
mise run kb-query -- "<question>"
```

Add `--prose` for a question about DOCUMENTS, `--idf` to rank the returned set.
**Arm an empty graph result before believing it.** A miss may be a term-spelling
mismatch against extracted node labels, not an absence. Query a term you KNOW is
in the corpus with the same command shape.

Otherwise — no graph in this repo — skip straight to the sweep below.

## The sweep — cheapest-refutable-first

Run in this order. The ordering is the substance: #509's worked run went
source-last and produced an artifact and two commits before anyone asked whether
the behaviour was already known upstream. It was, for fourteen months.

### 1. The installed binary

```bash
<tool> --help
```

Then a probe in a **throwaway directory outside this repo**. This is the only step
that can answer questions no document addresses — does it warn, does it read
`.gitignore`, what is its exit code on the empty case.

Version probes go through `mise exec -- <tool> --version`. A bare shim can be a
stale-PATH skew: a lane once reported hk 1.56.0 while the pin said 1.56.1.

### 2. The shipped source at the pinned ref

```bash
gh api "repos/OWNER/REPO/contents/PATH?ref=TAG"
```

`?ref=` goes **inside the path string**. `-f ref=v8.30.1` returns 404.

**Source beats issue tracker.** Issues stay open after their fix ships — graphify

# 959 read as "custom OpenAI endpoints are blocked" long after the feature landed

in 0.8.40. When a secondary artifact says impossible and it matters, read the code.

### 3. Both trackers — issues AND PRs AND discussions

```bash
aggregated-research trackers OWNER/REPO "TERM" --out .research/OWNER-REPO-TERM.json
```

The CLI (installed by this plugin's SessionStart hook) does the channel check
first and splits issues from PRs, so the two raw calls it replaces are shown
only to explain what it guards against:

```bash
gh api repos/OWNER/REPO --jq '{issues: .has_issues, discussions: .has_discussions}'
gh api -X GET search/issues -f q='repo:OWNER/REPO TERM' --jq '.total_count'
```

The channel check is not optional. **A count of zero from a channel that cannot
receive anything is not evidence** — `jdx/hk` has issues DISABLED, so an
`is:issue` search there is structurally zero. **PRs still index under
`search/issues`**: `repo:jdx/hk gitleaks` returned 9 hits on 2026-08-27, all pull
requests, while `repo:jdx/hk is:issue` returned 0. Split the search by `is:issue`
/ `is:pr`, or a real PR hit reads as "issues were searched".

Never `gh search issues`: it returns `[]` instead of failing, and its control
query with 39 real results also returned `[]` (#507).

### 4. Breadth — the developer index, and the one you must ASK for

**Run: Firecrawl `developer-index`, then the web.** It returns full issue bodies
and comment threads inline, so the substantive maintainer comment arrives without
a follow-up fetch. On the run that evaluated this skill it produced the decisive
lead that plain web search did not.

**Ask the user for: `/deep-research <question>`.** Claude Code ships it as a
bundled workflow — it fans out across angles, cross-checks, **votes on each claim,
and filters out the claims that did not survive** — and it is strictly better than
hand-rolling a fan-out (`use-tool-builtins.md`). But it is **user-invoked only**:
*"`/deep-research` runs only when you invoke it. Before v2.1.218, Claude could
also start it on its own"*
(`sources/agent-harness-docs/docs/claude-code/workflows.md:80`). A subagent cannot
reach it at all — measured 2026-08-27, when a lane told to follow this skill
reported it *"could not invoke it from this subagent"*.

So when breadth is the crux, say so and hand the reader the command. Do not plan
around running it yourself.

*(This step said "delegate to the bundled workflow" until 2026-08-27. That was
adopted from the shipped doc without an execution — the skill's own P3 report
flagged it as unverified — and the first attempt to run it refuted it. Corrected
rather than overwritten, because the reasoning for preferring it still stands.)*

**When breadth needs a lane, use `antigravity:research`.** It is cross-family
(Gemini) grounded web legwork with Claude verifying the citations, it IS
subagent-reachable, and it is the substitute for the paragraph above. Budget it:
the `agy` subscription depletes fast, so it is a scarce reserve, not a routine
call.

**Two Firecrawl surfaces beside `developer-index`, both installed and keyed:**
`firecrawl-research-index` for academic and paper questions, and
`firecrawl_research_search_github` for public-code search. Different indexes, not
different wrappers.

**`last30days` when the question is what people are DOING, not what is true.**
Dated, engagement-weighted evidence from Reddit / HN / X / YouTube / GitHub. It is
the only recency instrument here, and test prompt 2 — "what do other projects do
about X" — is exactly the class with no primary source to anchor on.

Then **verify every cited claim against primary sources** — a cited report is not
a verified one, and steps 1-2 above are what settles a citation.

### 4a. Sources you may not have installed

Not installed everywhere, so each is a recommendation when you need it, never an
assumption:

| when you need | reach for | cost |
|---|---|---|
| package metadata — versions, publish dates, advisories, licences | `curl https://api.deps.dev/v3/systems/pypi/packages/<name>` | **keyless, nothing to install** |
| "does an MCP server for X exist?" | `curl 'https://registry.modelcontextprotocol.io/v0/servers?search=<term>'` | keyless; it under-covers HOSTED servers, so a 0 there is not an absence |
| the same pattern across MANY repos' source at once | `mcp.grep.app` — regex over ~1M public repos, no auth (handshake measured) | register, or reach it via `mcp2cli` first |
| the real source of a PUBLISHED package version | Chroma Package Search MCP | needs an API key, pricing unpublished — ask before relying on it |

The first two answer questions this sweep otherwise guesses at. The third is what
turns *"what do other projects do about X"* from a blog-post question into a
source question.

### 5. Synthesis by a strong Claude lane that opens the URLs itself

Research leads are breadth, not truth. A lane that summarises a search-result
snippet has not read the source. Spot-check every factual claim a lane returns —

# 509's breadth lane asserted neither upstream repo was in the corpus while both

manifests exist.

## The control arm — the rule this skill exists for

**Before reporting any negative, run the same command shape against a case you
know succeeds, and paste its non-null output.**

| the null | the arm |
|---|---|
| a grep returns 0 | grep a term you know is present, same shape |
| a tracker search returns 0 | check `has_issues`; then search a term with known hits |
| a graph query returns nothing | query a term you know is ingested |
| an HTTP probe returns 404/301/000 | probe a URL you know returns 200 |
| "no prior art exists" | run the same search for a capability that certainly has prior art |

A redirect, a timeout, a `jq` miss and an empty grep are all *never asked*, not
*answered no*. Say which arm you ran: "bogus input → 404 while known-good → 200,
so the probe discriminates."

A cheaper arm for a WEB null specifically: run the same query on a **second
independent index**. `exa` is installed and keyed, and its value here is exactly
that — not as a primary source (it duplicates Firecrawl on most questions) but as
the control on a Firecrawl zero.

**Bounds are the commonest hidden null.** `-maxdepth`, `head -N`, `--limit`, a
time window, a `2>/dev/null` — and a token spelling. A session grepped `lmstudio`
and `lm_studio`, got 0, and reported the feature absent; it is spelled `LM Studio`
with a space, 3 hits, one in the tool's own `--help`.

## The five traps, as checks

Each of these was hit for real. Run the check, do not just know the trap.

1. `gh search issues` → **use `gh api -X GET search/issues`**.
2. Tracker null → **`gh api repos/OWNER/REPO` first**, read `has_issues` /
   `has_discussions`.
3. A citation can contradict what it annotates (#508) → **open the citation**.
4. Version skew → **`mise exec --`**, never the bare shim. **And a `command -v`
   hit is not an install** on a mise host: `command -v mkdocs` and
   `command -v doxygen` both print FOUND here, and both are shims that die with
   `No version is set for shim`. Probe the binary, not its name — measured
   2026-08-27 on this skill's own evaluation run.
5. A lane's factual claims → **spot-check against this repo** before quoting them.

## Output

A report at `docs/research/reports/<date>-<slug>.md` (or the nearest equivalent
in a repo with no such directory). Its shape:

- **Answer** — one paragraph, up front.
- **Ranked sources** — primary (source, binary, maintainer statement) separated
  from secondary (issue text, blog, another tool's README).
- **Every null, with its arm** — the command and its non-null control output.
- **Not measured** — an explicit section naming what was NOT checked. #509's most
  useful lines were these.
- **`## GitHub repos touched`** — every repo whose source, README, issues or docs
  were read, one line of reason each.

**Publish an artifact too when the answer is a decision someone has to make.**

**If it was worth fetching and this repo runs a knowledge-base graph, it is
worth ingesting** — `mise run kb-manifest-add -- <url>` for a code repo, `mise
run kb-add -- <url>` for prose. In a repo with no such graph, skip this.

## When NOT to use this

A one-line factual lookup you can settle with a single `--help`. A question about
this repo's own code, when a graph exists — that is `mise run kb-query` alone. A
library API signature — that is `ctx7`.

## Test prompts

The three this skill is scored against, in `references/acceptance-509.md`:

1. *"Is this behaviour a known bug in `<tool>`, and has anyone reported it?"*
2. *"What do other projects do about `<problem>`?"* — the hard one: no primary
   source to anchor on, so it tests whether confirmed can still be separated from
   anecdotal.
3. *"What tools should we be using to research questions like this?"* — the
   self-referential one, so the tool list stays current.
