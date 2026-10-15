import type { EngineInterface, Register } from 'claude-code'

// CT-35 (D61, D76, D92, D103; ADR 0008): calls only the engine and OS built-ins
// (date, sh). A hook that throws is skipped and the session goes on without it.

// The D61/D76 session name: `ccm-` + this format, its `%z` cut to the hour
// (`-0500` -> `-05`). The same format string as `dev/handoff.py next-name`.
export const DATE_ARGV = ['date', '+%Y%m%dT%H%M%S.%N%z'] as const

// One JSON line per step, for agents to read without the debug log: sh stamps
// `ts` (UTC, ns) from the OS date and appends under umask 077 (dir 0700, file 0600).
const APPEND =
  'umask 077 && mkdir -p "$1" && printf \'{"ts":"%s",%s\\n\' "$(date -u +%Y%m%dT%H%M%S.%NZ)" "${2#?}" >> "$1/events.jsonl"'

type Row = { session_id: string; cli_version: string; event: string; source?: string }
type Step = { step: string; result?: string; duration_ms?: number; transcript_path?: string }

async function row($: EngineInterface, event: string, session_id: string, source?: string): Promise<Row> {
  return { session_id, cli_version: (await $.session.version()).version, event, source }
}

async function log($: EngineInterface, base: Row, step: Step): Promise<void> {
  const line = JSON.stringify({ ...base, ...step, result: step.result?.slice(0, 500) })
  $.ui.log(`session-start ${line}`, { to: 'debug' })
  try {
    const dir = (await $.env.get('MARKETPLACE_SESSION_START_LOG')) ??
      `${await $.env.get('HOME')}/.local/state/claude-code-marketplace/session-start`
    await $.process.run(['/bin/sh', '-c', APPEND, 'session-start-log', dir, line])
  } catch {
    // A log write never holds up the session; the debug log has the row.
  }
}

export const register: Register = on => {
  // Skills reload on startup and /clear. The title is set on startup only:
  // `claude -n` (session_title) wins, and a title is ignored on clear (#67389).
  on('classic.SessionStart', async ($, e, next) => {
    const result = await next(e)
    const base = await row($, 'classic.SessionStart', e.session_id, e.source)
    await log($, base, { step: 'fired', transcript_path: e.transcript_path })
    if (e.source !== 'startup' && e.source !== 'clear') return result
    await log($, base, { step: 'reload_skills_returned' })
    const skills = { ...result, reloadSkills: true } as const
    if (e.source === 'clear') {
      await log($, base, { step: 'title_skipped', result: 'clear: a title is ignored (#67389)' })
      return skills
    }
    if (e.session_title !== undefined) {
      await log($, base, { step: 'title_kept', result: e.session_title })
      return skills
    }
    const { exitCode, stdout, stderr } = await $.process.run(DATE_ARGV)
    if (exitCode !== 0) {
      $.ui.status(`session-start ERROR: date exited ${exitCode}: ${stderr.trim()}`)
      await log($, base, { step: 'error', result: `date exited ${exitCode}: ${stderr.trim()}` })
      await log($, base, { step: 'title_skipped', result: 'date failed' })
      return skills
    }
    const sessionTitle = `ccm-${stdout.trim().slice(0, -2)}`
    await log($, base, { step: 'title_set', result: sessionTitle })
    return { ...skills, sessionTitle }
  })

  // The engine holds the first prompt until the first session.start settles, so
  // awaiting the reload here lands it before the first request (R3, PR #94594).
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    const base = await row($, 'session.start', await $.session.id())
    await log($, base, { step: 'fired', result: e.isInteractive ? 'interactive' : 'not interactive: no reload' })
    if (!e.isInteractive) return started
    await log($, base, { step: 'reload_plugins_begin' })
    const begin = await $.clock.now()
    let result = 'accepted'
    // Plain reload, never --force (D103): a held reload resolves with the docs'
    // line ending `Run /reload-plugins --force to apply.` and keeps the cache.
    try {
      const { text = '' } = await $.command.run({ command: 'reload-plugins' })
      if (text.includes('--force to apply')) {
        result = `held: ${text}`
        $.ui.status(`session-start: /reload-plugins ${result}`)
      }
    } catch (error) {
      result = `rejected: ${error instanceof Error ? error.message : String(error)}`
      $.ui.status(`session-start ERROR: /reload-plugins ${result}`)
    }
    await log($, base, { step: 'reload_plugins_end', result, duration_ms: (await $.clock.now()) - begin })
    return started
  })
}
