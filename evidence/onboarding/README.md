# Onboarding receipts

These are dated local observations for native Codex 0.162.1 and mise 2026.10.7.
They are not portable installation pins. Original research/audit files remain
at the verified source-index paths; this directory contains new sanitized receipts.

| Receipt | Establishes | Limit |
| --- | --- | --- |
| `source-hash-audit.json` | All 19 handoff source hashes verified | Historical evidence, not fresh provider coverage |
| `baseline-files.json` | Original 19 tracked file hashes and base HEAD | Static preservation reference |
| `n1-review.json` | Independent documentation review and dispositions | Predates later command documentation |
| `runtime-inventory.json` | CLI/config/plugin/skill/role observations | Configured is not authenticated or operational |
| `mcp-probe-inventory.json` | 13 CLI-visible servers; no mixed transports | App-server discovers additional endpoints |
| `native-config-controls.json` | Strict parser control; project-layer rejection; root/unrelated context loads | Debug does not prove custom-role application |
| `native-role-smoke.json` | Initial exec smoke and guard notice | Spawn metadata and one error message were omitted |
| `native-role-protocol.json` | Native assigned role, parent/source, child directive and completion | Original startup containment was incomplete |
| `native-startup-diagnostics.json` | Four extra bundled MCP endpoints started | No tools called; not a no-services run |
| `native-startup-corrected.json` | Corrected invocation-only startup; no MCP startup notifications; rc 0 | No inference or connectivity qualification |
| `n2-review.json` | Independent role proof and diagnostic dispositions | Does not certify provider/OCI behavior |
| `development-checks.json` | Config/task isolation, static baseline, unrelated cwd, failure propagation | Full container acceptance not run |
| `n3-review.json` | Independent current-code static gate | No installs, providers or container runtime |
| `final-context-checks.json` | Current root, unrelated-cwd and scoped plugin guidance; each rc 0 | Native diagnostics, not OCI acceptance |
| `sanitization-check.json` | Default Gitleaks rules over explicit input bytes, including dot directories | Hashes identify the exact scanned snapshot |
| `n4-cold-review.json` | Separate cold integration review and finding recheck | Local onboarding scope only |

Some receipts name the source HEAD because they ran before local commits. Do not
reinterpret them as tests of a later revision. The final qualification record
must name its actual checkout/branch/HEAD and command return codes. Do not persist
credentials, complete environment/config dumps or internal encrypted messages.

Onboarding routes: native collaboration, filesystem/Git/Python/shell, Codex
CLI/app-server, mise, Gitleaks and the OpenAI Docs manual helper through native fnox.
Applied skills: Codex task orchestration, OpenAI Docs, Planning with Files and
mise. No Exa, Firecrawl, Last30Days, Context7 or GitHub search ran for onboarding;
their inherited strict-five failures remain in the source audit. No success is
claimed for unused connectors. See `docs/codex-runtime.md` for failed diagnostics.
