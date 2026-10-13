# docs/

Each fact has one authoritative document; link to it and leave the copy out. A
change to a decision, protocol or status edits the owner below and nothing else.

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
| Agent protocols: ownership, retro gate, tracker, team, takeover, triage, domain | `agents/` |
| Architecture decisions | `adr/` (numbered, `Accepted` status) |

Vocabulary lives in `../GLOSSARY.md`; reviewer judgement rules in
`../CODING_STANDARDS.md`.

## Editing rules

- Entry points for an agent: `agents/claude-team.md` for roles and lanes,
  `agents/ticket-retro.md` for the retro gate, `agents/issue-tracker.md` for the
  standing workflow.
- New decisions go in a new ADR that names what it supersedes; an accepted ADR keeps
  its text.
- Point at a plan, receipt or helper with a relative link; restate none of its content.
- Sanitized material only: no secrets, tokens, provider payloads or transcripts.
