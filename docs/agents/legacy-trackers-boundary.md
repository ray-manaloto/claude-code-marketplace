# Pinned legacy `trackers` boundary (ticket #24)

The current Claude plugin installs `ray-manaloto/knowledge-base` at commit
`a872cb016feb5512994b37330ce6a387c5732253` through its
[`mise.toml`](../../plugins/aggregated-research/mise.toml). The local Git object
is a commit with tree `e8762a7fc70c973b48eb376c72c63953ba8ab530`.
The existing pipx environment's `direct_url.json` names that exact commit and
the public repository URL. Four installed Python modules were byte-equal to
their Git blobs at the pin: `research/cli.py`, `research/trackers.py`,
`generated/research_record.py` and `kb_setup/cli.py`. Their digests are in
[`capture.json`](../../evidence/legacy-trackers/capture.json). No file in the
knowledge-base checkout was edited; its pre-existing dirty status was
unchanged after fixture capture.

The call path is explicit:

```text
plugin bin/aggregated-research
  -> plugin bin/mise-env exec
  -> installed aggregated-research console script
  -> kb_setup.research.cli:main
  -> kb_setup.cli.main(["research-trackers", ...])
  -> kb_setup.research.trackers.main
  -> bounded gh api subprocess calls
```

The wrapper selects `~/.claude/plugins/data/aggregated-research-ray-manaloto`
as its install/data root, or a matching absolute `CLAUDE_PLUGIN_DATA` directory.
It keeps mise installs and the uv cache below that data root. The `trackers`
command's `--out PATH` is a **caller-selected output path**, whose parent it
creates; it is not automatically placed in the plugin data root. With no
`--out`, it prints one formatted JSON record. The installed public CLI help
exits 0 and lists only `trackers`; an unknown verb exits 2. The plugin's OCI
acceptance script still asserts `verbs: trackers`, the output `adapter` and
`hits` shape, plus positive and armed-null cases.

At the pin, `trackers` first reads `gh api repos/OWNER/REPO` for
`has_issues` and `has_discussions`. It always searches pull requests and
searches issues only when enabled. Discussions are a presence field, not a
searched hit channel. The output record has `adapter`, `tier`, `question`,
`command`, `has_issues`, `has_discussions`, `ran_at`, `total_count`, `hits`
and `null_result`. Each hit has URL, bounded title/snippet, update timestamp
and issue/PR kind. An empty result includes one control arm per searched
channel with `total_count` and whether that arm discriminates. A nonzero or
unparseable `gh` result fails instead of yielding an apparent empty search.

The [fixture runner](../../dev/legacy_trackers_fixture.py) used the existing
pinned Python environment, the public console entry and a strictly enumerated
fake `gh` boundary. Its [hit](../../evidence/legacy-trackers/hit.json) and
[armed-null](../../evidence/legacy-trackers/null.json) records exercised
the exact record shape, issue/PR ordering, newline-normalized snippet and
control-arm semantics without provider calls. A second run produced the same
three file hashes. The fixed timestamp and synthetic GitHub URLs make these
**offline compatibility fixtures**, not evidence of current GitHub results,
live authentication, fresh Claude SessionStart or OCI acceptance.

The required knowledge-base graph query exited 3 because Graphify marked its
result truncated (56 of 3,758 nodes shown) and noted a pre-#1504 node-ID
scheme. The pinned Git source and byte-matched installed modules therefore
served as the source authority for this ticket. No graph rebuild was run.
