import type { Register } from 'claude-code'

// CT-35 (D61, D76, D92, D103; ADR 0008): calls only the engine and the OS date
// command. A hook that throws is skipped and the session goes on without it.

// The D61/D76 session name: `ccm-` + this format, its `%z` cut to the hour
// (`-0500` -> `-05`). The same format string as `dev/handoff.py next-name`.
export const DATE_ARGV = ['date', '+%Y%m%dT%H%M%S.%N%z'] as const

export const register: Register = on => {
  // Skills reload on startup and /clear. The title is set on startup only:
  // `claude -n` (session_title) wins, and a title is ignored on clear (#67389).
  on('classic.SessionStart', async ($, e, next) => {
    const result = await next(e)
    if (e.source !== 'startup' && e.source !== 'clear') return result
    if (e.source === 'clear' || e.session_title !== undefined) return { ...result, reloadSkills: true }
    const { exitCode, stdout, stderr } = await $.process.run(DATE_ARGV)
    if (exitCode !== 0) {
      $.ui.status(`session-start ERROR: date exited ${exitCode}: ${stderr.trim()}`)
      return { ...result, reloadSkills: true }
    }
    return { ...result, reloadSkills: true, sessionTitle: `ccm-${stdout.trim().slice(0, -2)}` }
  })

  // The engine holds the first prompt until the first session.start settles, so
  // awaiting the reload here lands it before the first request (R3, PR #94594).
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    if (!e.isInteractive) return started
    // Plain reload, never --force (D103): a held reload resolves with the docs'
    // line ending `Run /reload-plugins --force to apply.` and keeps the cache.
    try {
      const { text = '' } = await $.command.run({ command: 'reload-plugins' })
      if (text.includes('--force to apply')) $.ui.status(`session-start: /reload-plugins held: ${text}`)
    } catch (error) {
      $.ui.status(`session-start ERROR: /reload-plugins rejected: ${error instanceof Error ? error.message : String(error)}`)
    }
    return started
  })
}
