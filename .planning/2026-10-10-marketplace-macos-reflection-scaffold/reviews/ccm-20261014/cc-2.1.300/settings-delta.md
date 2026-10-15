# Settings, env var, CLI flag, frontmatter and mod API delta (2.1.251 -> 2.1.300)

Named by the changelog; `documented_now` checks the docs fetched with webclaw on 2026-10-14 (settings-reference, env-vars, sub-agents, hooks, mods events). This is a delta, not the inventory (that is its own ticket). Renames: none named in range. Feature flags: no flag names are published; 8 entries mention flags or staged rollouts (`feature_flag_mentions` in the JSON), the project-relevant one being the mods rollout switch (2.1.299#23).

## Verified rows (checked by hand against the changelog text)

| Type | Name | Status | Changelog | MP relevance | Note |
|---|---|---|---|---|---|
| setting | `idleCompaction` | added | 2.1.299#3 | yes | `false` turns idle compaction off (on by default) |
| env_var | `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` | added | 2.1.299#3 | yes | idle compaction threshold, default 200000 |
| env_var | `DISABLE_AUTO_COMPACT` | behavior_changed | 2.1.299#2 |  | docs: also disables idle compaction |
| frontmatter | `autoCompactWindow` | added | 2.1.296#2 | yes | per-subagent auto-compact window (100000-1000000) |
| frontmatter | `omitClaudeMd` | added | 2.1.271#5 | yes | subagent starts without user/project/local CLAUDE.md |
| hook_field | `onFailure` | added | 2.1.295#1 | yes | `block` makes a failing command/HTTP hook block the action |
| hook_field | `updatedInput` | behavior_changed | 2.1.300#65 |  | validated like Claude's own input; unknown keys dropped |
| setting | `bashOutputMaxChars` | added | 2.1.261#2 | yes | inline Bash output cap, up to 128K |
| setting | `taskOutputMaxChars` | added_then_removed | 2.1.261#2, 2.1.277#69 | yes | no effect since TaskOutput was removed |
| env_var | `TASK_MAX_OUTPUT_LENGTH` | removed_or_deprecated | 2.1.277#69 | yes | no effect |
| setting | `keybindingFlavor` | removed_or_deprecated | 2.1.261#40 |  | no longer has any effect |
| setting | `syncClaudeAiSkills` | added | 2.1.275#4 | yes | `false` stops claude.ai skills syncing into terminal sessions |
| setting | `syncClaudeAiPlugins` | added | 2.1.275#4 | yes | `false` stops claude.ai plugins syncing into terminal sessions |
| setting | `advisorModel` | added | 2.1.300#5 |  | picks the advisor model (Claude Platform on AWS) |
| cli_flag | `--advisor` | added | 2.1.300#5 |  | picks the advisor model |
| env_var | `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` | added | 2.1.300#5 |  | turns the advisor tool off |
| env_var | `CLAUDE_CODE_GZIP_REQUEST_BODIES` | behavior_changed | 2.1.300#59 |  | gzip now also when telemetry is off; `0` turns it off |
| env_var | `CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST` | behavior_changed | 2.1.300#55 |  | such sessions ignore CA-bundle, proxy, git TLS and git config variables in settings |
| cli_flag | `--sandbox / --no-sandbox (claude remote-control)` | removed_or_deprecated | 2.1.300#66 |  | now exit with an error; use `sandbox.enabled` |
| setting | `claudeCode.attachSelection (VS Code)` | added | 2.1.300#67 |  | VS Code extension setting |
| mod_api | `$.ui.view({ agentId })` | added | 2.1.300#3 | yes | show an agent's transcript in the main view |
| mod_api | `prompt decoration virtualText` | added | 2.1.300#1 |  | text drawn in the prompt box, never submitted |
| mod_api | `Text dir` | added | 2.1.300#4 |  | right-to-left rows |
| mod_api | `agent.spawn (workflow agents: prompt, model rewrite)` | behavior_changed | 2.1.300#7 | yes | was refuse-only |
| mod_api | `prompt.change` | added | 2.1.300#8 | yes | prompt text changed without a typed edit |
| mod_api | `tool.check agentId, ceiling` | added | 2.1.290#2, 2.1.290#3 | yes | new fields on an existing event |
| mod_api | `turn.start (subagents, teammates)` | behavior_changed | 2.1.299#169 |  | absent e.agentId means the main loop |
| mod_api | `Text bold` | removed_or_deprecated | 2.1.299#6 |  | deprecated in favor of `weight` |
| env_var | `CLAUDE_CODE_DISABLE_WEB_FETCH` | added | 2.1.285#1 | yes | turns the WebFetch tool off |
| cli_flag | `--permission-prompts none` | added | 2.1.259#2 | yes | deny anything that would prompt (headless) |
| cli_flag | `claude plugin validate --json` | added | 2.1.259#4 | yes | machine-readable validation |
| cli_flag | `claude plugin install --accept-command <sha256>` | added | 2.1.271#6 | yes | accept an exact displayed command instead of -y |
| otel | `api_request cache_creation_5m_tokens, cache_creation_1h_tokens; GenAI span attributes` | added | 2.1.300#2, 2.1.300#6 |  | telemetry fields |

## Heuristic rows (token shape plus sentence context; added or removed only; noisy CLI flags pruned)

| Type | Name | Status | First in | Documented now | Changelog |
|---|---|---|---|---|---|
| cli_flag | `--accept-command` | added | 2.1.271 | n/a | 2.1.271#6: Added `--accept-command <sha256>` to `claude plugin install` and `claude plugin update` to accept exactly the  |
| cli_flag | `--append-subagent-system-prompt-file` | added | 2.1.261 | n/a | 2.1.261#3: Added `--append-subagent-system-prompt-file` to read the subagent system prompt from a file, for prompts too l |
| cli_flag | `--disallow-tools` | added | 2.1.299 | n/a | 2.1.299#12: Added `--disallow-tools` and a `disallowed_tools` case field to `claude plugin eval` to keep specific built-in |
| cli_flag | `--json` | added | 2.1.259 | n/a | 2.1.259#4: Added `--json` to `claude plugin validate` for a machine-readable validation report |
| cli_flag | `--no-sandbox` | removed_or_deprecated | 2.1.300 | n/a | 2.1.300#66: Removed the `--sandbox` and `--no-sandbox` flags from `claude remote-control`, which had no effect; passing ei |
| cli_flag | `--plugin-dir` | added | 2.1.265 | n/a | 2.1.265#2: Added support for pointing `--plugin-dir` at a folder of plugins: each child folder with a manifest loads, and |
| cli_flag | `--shutdown-drain-sec` | added | 2.1.299 | n/a | 2.1.299#7: Added `--shutdown-drain-sec` to `claude self-hosted-runner orchestrator`: on SIGTERM it stops polling and give |
| cli_flag | `--system-prompt-snapshot` | added | 2.1.267 | n/a | 2.1.267#2: Added `--system-prompt-snapshot off` to render the system prompt fresh on every request instead of reusing the |
| env_var | `CLAUDE_CODE_ATTRIBUTION_HEADER` | added | 2.1.299 | yes | 2.1.299#13: Added support for turning off the attribution block in Claude Desktop's Code tab: set `CLAUDE_CODE_ATTRIBUTION |
| env_var | `CLAUDE_CODE_DISABLE_FILE_MENTIONS` | added | 2.1.299 | yes | 2.1.299#1: Added `CLAUDE_CODE_DISABLE_FILE_MENTIONS` environment variable: Claude gets the paths of `@` file mentions to  |
| env_var | `CLAUDE_CODE_DISABLE_STRUCTURED_OUTPUTS` | added | 2.1.288 | yes | 2.1.288#14: Fixed session titles, memory recall and prompt hooks failing on Mantle or behind gateways that reject structur |
| env_var | `CLAUDE_CODE_GATEWAY_MODEL_DISCOVERY_TIMEOUT_MS` | added | 2.1.269 | yes | 2.1.269#5: Added `CLAUDE_CODE_GATEWAY_MODEL_DISCOVERY_TIMEOUT_MS` to extend the LLM gateway `/v1/models` discovery timeou |
| env_var | `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` | added | 2.1.280 | yes | 2.1.280#3: Added `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` to change the 2,048-character cap on MCP tool descriptions and  |
| env_var | `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` | added | 2.1.274 | yes | 2.1.274#2: Added `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` to bound how long the first non-interactive turn waits for connecting  |
| env_var | `CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES` | added | 2.1.285 | yes | 2.1.285#6: Added `CLAUDE_CODE_NONSTREAMING_TIMEOUT_RETRIES` environment variable to cap re-sends of a non-streaming fallb |
| env_var | `CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS` | added | 2.1.292 | yes | 2.1.292#3: Added `CLAUDE_CODE_OVERLOADED_RETRY_BASE_DELAY_MS` environment variable to set a longer base delay for the bac |
| env_var | `CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS` | added | 2.1.296 | yes | 2.1.296#4: Added `CLAUDE_CODE_OVERLOADED_RETRY_MAX_DELAY_MS` environment variable to set a longer maximum delay for the b |
| env_var | `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` | added | 2.1.295 | yes | 2.1.295#14: Added `CLAUDE_CODE_RETRY_WATCHDOG_MAX_WAIT_MS` to limit how long unattended retry mode (`CLAUDE_CODE_RETRY_WAT |
| env_var | `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` | added | 2.1.257 | yes | 2.1.257#4: Added `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to apply `CLAUDE_CODE_SUBAGENT_MODEL` (or the main model) to every su |
| env_var | `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` | added | 2.1.269 | yes | 2.1.269#7: Added `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` (1–256) to raise the Workflow tool's per-run concurrent age |
| env_var | `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` | added | 2.1.296 | no | 2.1.296#3: Added `CLAUDE_CODE_WORKFLOW_SUBAGENT_MODEL` to run every workflow agent on one model while other subagents kee |
| env_var | `CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY` | added | 2.1.277 | no | 2.1.277#2: Added `CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY=1` for Claude apps gateways whose only egress is a forward prox |
| env_var | `OTEL_METRICS_INCLUDE_REPOSITORY` | added | 2.1.269 | yes | 2.1.269#4: Added `OTEL_METRICS_INCLUDE_REPOSITORY` to tag OpenTelemetry metrics and events with `vcs.*` repository attrib |
| hook_field | `agentId` | added | 2.1.290 | no | 2.1.290#2: Added `agentId` to the `tool.check` event of plugin hooks, so a hook can tell a subagent's permission check fr |
| hook_field | `serverToolUses` | added | 2.1.290 | no | 2.1.290#1: Added `serverToolUses` to the result of a mod's `turn.step` hook: the tool calls the API ran itself (the advis |
| mod_api | `$.model.complete` | added | 2.1.292 | no | 2.1.292#5: Added prompt caching to `$.model.complete` for mods: `prompt` and `system` take blocks of text, and `cache: tr |
| mod_api | `$.prompt.media` | added | 2.1.299 | no | 2.1.299#4: Added `$.prompt.media` so a `prompt.submit` hook of a mod installed by managed settings can read the bytes of  |
| mod_api | `$.session.identity` | added | 2.1.299 | no | 2.1.299#5: Added `$.session.identity()` for mods installed by managed settings: how the session is signed in, and its org |
| mod_api | `$.ui.notify` | added | 2.1.295 | no | 2.1.295#12: Added `$.ui.notify` for mods: raises a native notification through your own notification setting and says whic |
| mod_api | `$.ui.selection` | added | 2.1.288 | no | 2.1.288#1: Added `$.ui.selection()` for mods: returns the text you last selected in fullscreen mode and, when the selecti |
| mod_api | `prompt.autocomplete` | added | 2.1.292 | no | 2.1.292#4: Added `prompt.autocomplete`, an event a mod hooks to add its own rows to the prompt box's autocomplete list |
| mod_api | `skill.prompt` | added | 2.1.299 | yes | 2.1.299#8: Added the skill's frontmatter, source, plugin name and file path to what a mod's `skill.prompt` hook receives |
| mod_api | `tool.output` | added | 2.1.283 | no | 2.1.283#4: Added MCP tool, WebFetch and WebSearch outputs to the `tool.output` OpenTelemetry span event when `OTEL_LOG_TO |
| setting | `allowClaudeInChromeWithManagedMcp` | added | 2.1.282 | yes | 2.1.282#3: Added the `allowClaudeInChromeWithManagedMcp` managed setting to let `claude --chrome` run alongside an exclus |
| setting | `allowedProviders` | added | 2.1.285 | yes | 2.1.285#5: Added `allowedProviders` managed setting to limit which API providers a machine may use (Anthropic API, a cust |
| setting | `availableModels` | added | 2.1.283 | yes | 2.1.283#2: Added `availableModelsMatch` managed setting: with `"exact"`, an `availableModels` entry allows only the model |
| setting | `availableModelsMatch` | added | 2.1.283 | yes | 2.1.283#2: Added `availableModelsMatch` managed setting: with `"exact"`, an `availableModels` entry allows only the model |
| setting | `bashEditDiffEnabled` | added | 2.1.269 | yes | 2.1.269#3: Added a diff of the files a Bash command changed to the Bash tool result when the Bash tool handles file edits |
| setting | `claudeCode.lockEditorGroups` | added | 2.1.274 | no | 2.1.274#70: [VSCode] Added a `claudeCode.lockEditorGroups` setting to stop Claude from locking the editor groups it opens  |
| setting | `claudeCode.scrollToBottomOnSend` | added | 2.1.275 | no | 2.1.275#75: [VSCode] Fixed the conversation pulling you back to the bottom while a reply streams after you scroll up, and  |
| setting | `deniedModels` | added | 2.1.283 | yes | 2.1.283#3: Added `deniedModels` managed setting to block specific models, even when `availableModels` allows them |
| setting | `forceLoginMethod` | added | 2.1.261 | yes | 2.1.261#38: Changed machines whose managed settings pin `forceLoginMethod: "gateway"` to ignore a leftover API key or clau |
| setting | `gatewayInternalNetworks` | added | 2.1.268 | yes | 2.1.268#3: Added the `gatewayInternalNetworks` managed setting, letting administrators allow `/login` to a Claude apps ga |
| setting | `managedMcpServers` | added | 2.1.259 | yes | 2.1.259#1: Added `managedMcpServers` managed setting: organizations can provide HTTP/SSE MCP servers to every user (same  |
| setting | `maxEffortLevel` | added | 2.1.267 | yes | 2.1.267#1: Added `maxEffortLevel` setting (top-level or per model under `modelSettings`): caps the effort level on every  |
| setting | `maxProseWidth` | added | 2.1.282 | yes | 2.1.282#1: Added a `maxProseWidth` setting that caps the width of Claude's prose in wide terminals while tables and code  |
| setting | `otelHeadersHelper` | added | 2.1.275 | yes | 2.1.275#3: Added a startup warning when a configured `otelHeadersHelper` fails, so sessions that silently export no telem |
| setting | `permissions.blockReadsOutsideWorkingDirectories` | added | 2.1.257 | yes | 2.1.257#7: Added a one-time prompt in auto mode before the first file read outside the working directories, with the opti |
| setting | `timeFormat` | added | 2.1.257 | yes | 2.1.257#2: Added "Time format" (`timeFormat`) and `timeZone` settings: 12-hour, 24-hour, 24-hour UTC, or a strftime patte |
