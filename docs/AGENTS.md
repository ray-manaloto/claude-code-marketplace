# docs/

Each fact has one authoritative document; link to it and leave the copy out. A
change to a decision, protocol or status edits the owner below and nothing else, and
other documents point at a plan, receipt or helper by relative link.

## Authority

| Question | Owner |
| --- | --- |
| Fresh-chat setup, checks, prerequisites | `onboarding.md` |
| Product direction and user decisions (supersede historical research) | `accepted-decisions.md` |
| Handoff identity, current state | `status.md` |
| Native research-core task order | `build-roadmap.md` |
| Host inventory and runtime qualification | `codex-runtime.md` |
| Core qualification and build matrix | `core-qualification.md`, `baseline-presets.md` |
| Toolchains | `p2996-toolchain.md`, `llvm-tools.md`, `iwyu-toolchain.md`, `vcpkg-toolchain.md`, `vcpkg-toolchains.md`, `sanitizers.md` |
| Offline research feedback | `research-feedback.md`, with records in `research-feedback-retro/` |
| Agent protocols | `agents/`: ownership (`codex-task-orchestration.md`), `ticket-retro.md`, `issue-tracker.md`, `claude-team.md`, `claude-takeover.md`, `triage-labels.md`, `domain.md`, `codex-example-classification.md` (example triage), `context7-bridge.md` (Context7 bridge), `full-baseline-ticket-review.md` (baseline ticket review), `legacy-trackers-boundary.md` (legacy tracker limits), `python-bridge-placement.md` (Python bridge placement) |
| Architecture decisions | `adr/` (numbered, `Accepted` status) |

Vocabulary lives in `../GLOSSARY.md`; reviewer judgement rules in
`../CODING_STANDARDS.md`.

## Editing rules

- Entry points for an agent: `agents/claude-team.md` for roles and lanes,
  `agents/ticket-retro.md` for the retro gate, `agents/issue-tracker.md` for the
  standing workflow.
- New decisions go in a new ADR that names what it supersedes; an accepted ADR keeps
  its text.
- Sanitized material only: no secrets, tokens, provider payloads or transcripts.
