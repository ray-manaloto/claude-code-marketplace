# Skill invocation record — Claude takeover session, 2026-10-13

The five-stage protocol requires the actual invocation mode per stage. "Native"
means the Skill tool loaded the skill in this Claude Code session; "file-guided"
means the installed `SKILL.md` was read and followed as text, the same mode the
Codex threads recorded for every stage; "typed by user" names the slash command
the user entered. The four user-invoked-only verbs (`to-spec`, `to-tickets`,
`implement-spec`, `retro`) run natively only when the user types them; this
table gains a row with the new mode whenever that happens.

Package: `mattpocock-skills` 1.3.1 from marketplace `mattpocock`, cache
`/Users/rmanaloto/.claude/plugins/cache/mattpocock/mattpocock-skills/1.3.1/`;
marketplace checkout HEAD `49dd158d1076134a641b33efb035946536778336`;
`installed_plugins.json` records `gitCommitSha` `24fe0ef7737efae15c87225755e9f6f5965e4888`
(project scope) and `49dd158d1076134a641b33efb035946536778336` for 1.3.1. The
file hashes below are the binding identities.

| Stage | Skill | Source `SKILL.md` (relative to the cache unless absolute) | SHA-256 | Mode | Invoked by | Output pointer |
| --- | --- | --- | --- | --- | --- | --- |
| grill-with-docs (router) | `grill-with-docs` | `skills/engineering/grill-with-docs/SKILL.md` | `7de372c13488f1ee96cc11cd8907b56b6809cc93eef776eeddd37de6b6cbe3fe` | typed by user (`/mattpocock-skills:grill-with-docs`); router text followed | user | rounds 1–2 in `docs/agents/claude-takeover.md` and the plan's takeover section |
| grill-with-docs | `grilling` | `skills/productivity/grilling/SKILL.md` | `befdff1e27a1dfe2a294d5871169ac1afe16d983911daa4f32627514a48c1e15` | native Skill tool | Claude (as the router directs) | two numbered question rounds, all recommendations accepted |
| grill-with-docs | `domain-modeling` | `skills/engineering/domain-modeling/SKILL.md` | `7b925d7b1e341a2eeae33ad68a8a8c0ab889a38ddd22a7598e4c240e5a7556a3` | native Skill tool | Claude (as the router directs) | `GLOSSARY.md` Workflow section and `docs/adr/0001-claude-takeover-and-retro-gate.md` (landed by lane `team`) |
| to-spec | `to-spec` | `skills/engineering/to-spec/SKILL.md` | `43ad9cf318e5e7d3d1fa360253a37021796dc87a0c2e595ad262661a10f85088` | file-guided fallback (user-invoked-only skill; standing authorization, round-1 Q3) | Claude | spec draft in the session scratchpad (`drafts/spec-claude-takeover.md`); publication through `issue:create-*` pending user approval |
| to-tickets | `to-tickets` | `skills/engineering/to-tickets/SKILL.md` | `56ec23c5b2782785d4e65bff9e315b6d3aeb4ef977c174a219e99489fada1995` | file-guided fallback (same) | Claude | the eleven-ticket breakdown presented to the user for granularity/edge approval; manifest builder in the scratchpad; publication pending approval |
| implement-spec | `implement-spec` | `skills/engineering/implement-spec/SKILL.md` | `7a22dd2e60b8fcece478ced9d2533582adf3520d695acd3ab715341535c9e56d` | file-guided fallback (same) | Claude | lane records under `lanes/`, worktrees under `.claude/worktrees/`, integrations on `codex/marketplace-native-onboarding` |
| retro | `retro` | `skills/engineering/retro/SKILL.md` | `33fbc28568e3146f20fd908b12998bc0ab30aa4f4c87288199a40793efa94696` | file-guided fallback (same) | Claude and the `retro-writer` role | records under `retros/`; the `retro:gate` task checks their shape |
| supporting | `writing-for-agents` | `skills/productivity/writing-for-agents/SKILL.md` | `551adca942227b44192edba88acd4e8db911f0121ce58ad16944ccf6a896a74a` | native Skill tool | Claude | guidance applied to agent-facing documents |
| supporting | `skill-creator` | `/Users/rmanaloto/.claude/skills/synced/c1029050-a11f-4194-9994-3e4271c1d0f0_770dee3b-2a2d-418c-81b3-d4b860a1f3c3/skill-creator/SKILL.md` | `42765c880e446a83c85f7852fc77b43ecd46c76ca219d68051799ac7425e6943` | native Skill tool | Claude (user requested `/skill-creator`) | `codex-session-history` skill (lane `codex-session-history`, integrated `55f3946`); evaluation loop not yet run |
| supporting | `agentsview-finding-history` | `/Users/rmanaloto/.claude/skills/agentsview-finding-history/SKILL.md` | `e92b844702da34ac6db2f59c68161c93f2e6f838ac855986b69515db8dbaceb7` | native Skill tool | Claude (user requested) | lexical AgentsView searches (semantic index unavailable); Codex thread briefs in the session scratchpad |

Correction history: the activation record first said the five stages were
"invoked natively"; a side agent's review on 2026-10-13 found that only the
grilling pair and the supporting skills were native, and the wording was
corrected the same day (see `progress.md`).
