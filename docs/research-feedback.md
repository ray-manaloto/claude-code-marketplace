# Offline research coverage feedback

For unexpected empty results, candidate-promotion checks or offline feedback
replay, use `dev/research_feedback.py`. This dependency-free development helper
shares the tested safeguard from the private GitHub research workflow. The
unified GitHubKit transport remains a separate implementation owned by its session.

## Commands and data

Use existing tools; no installation or provider call is required:

```sh
./dev/mise run check:research-feedback
./dev/mise run research:replay-feedback -- --current /absolute/current.json --previous /absolute/prior.json
```

`current.json` maps search IDs to native observations. Each observation supplies
a nonempty `query_fingerprint`, explicit `error_code` (`NONE` for success), boolean
`is_complete`, integer `item_count` matching the combined arrays, and optional
nullable `total_count`. Results reside in `items`, `issues` or `discussions`.
Code items need `repo_name` and `path`; other items need `html_url`.

`prior.json` is either a feedback map, `{}` for a first observation, or the full
JSON stdout from a preceding replay. Output contains `queries` and
`promotion_blockers`. Exit 0 means no errors or unexpected-empty blockers;
exit 2 means blocked coverage or malformed input. Input files are read only;
the caller chooses whether and where to retain stdout. Direct library consumers
pass the `queries` map to `metrics(current, previous)`.

## Integration contract

- Preserve the prior feedback per search and compatible fingerprint. A successful
  nonempty observation establishes history. Subsequent empty observations remain
  unverified until recovery or a reviewed fingerprint change. API errors retain
  that nonempty history. Recovery is marked once.
- Check `promotion_blockers` across the whole batch, including queries outside a
  proposed change. Independently enforce batch/manifest integrity, catalog hashes,
  pagination budgets, candidate relevance anchors and completeness expectations.
  Capped searches are incomplete even when they do not appear in this blocker list.
- This module detects regression, not first-empty validity. The transport must
  classify uncontrolled empties and capability failures before supplying native
  status. `complete` alone cannot certify a first empty response.
- This module computes no NEW/GONE delta. On recovery, compare with the last
  compatible nonempty snapshot. Failed, incompatible or unverified observations
  cannot establish deletion or addition claims.
- Keep raw snapshots immutable and retain native status separately from effective
  completeness. Duplicate source bytes are one example, while their result
  identities remain separate. Provider quotas and provisional fallbacks retain
  their own route status and retry schedule.

The normal `./dev/mise run check` includes these tests. The development CI job
runs the same dependency-free check entry point using runner-installed Python.
The checks run from any shell because the check entry point and test harness
scrub inherited runtime selectors such as `VIRTUAL_ENV` and `UV_PYTHON`.
The refresh CLI still refuses a selector that names any environment other than
the borrowed project's own `.venv`.
Original Claude/container acceptance remains independent and unchanged.

## Validation and sharing

[Local gates](../evidence/research-feedback/checks.json) record 12 offline tests,
19 preserved original hashes and the reviewed replay-envelope repair. This
does not establish live provider behavior, scheduled execution or hosted CI.
[Scoped progress](research-feedback-retro/progress.md) records ownership and
the two small implementation units. Private catalogs, learning state, logs,
automation files, credentials and exact runtime pins are not copied into Git.
