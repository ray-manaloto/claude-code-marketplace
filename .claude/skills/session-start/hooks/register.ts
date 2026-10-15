import type { EngineInterface, Register } from 'claude-code'
import { APPEND, DATE_ARGV, DATE_TIMEOUT_MS, LOG_TIMEOUT_MS, RELOAD_TIMEOUT_MS, excerpt, logDir, parseDate } from './log.ts'

// CT-35 (D61, D76, D92, D103; ADR 0008): calls only the engine and OS built-ins
// (date, sh). A hook that throws is skipped and the session goes on without it.
// Pure helpers live in ./log.ts; every `$` call stays in this file (a hooks
// module may not pass `$` to an imported function).

type Row = { session_id: string; cli_version: string; event: string; source?: string }
type Step = { step: string; result?: string; duration_ms?: number; transcript_path?: string }
// One per hook dispatch: the row fields every step shares, and where the JSONL
// file goes (undefined when neither the override nor HOME is set).
type Log = { base: Row; dir: string | undefined }

async function open($: EngineInterface, event: string, session_id: string, source?: string): Promise<Log> {
  const base: Row = { session_id, cli_version: (await $.session.version()).version, event, source }
  const dir = logDir(await $.env.get('MARKETPLACE_SESSION_START_LOG'), await $.env.get('HOME'))
  if (dir === undefined) {
    $.ui.log(`session-start ${JSON.stringify({ ...base, step: 'error', result: 'no HOME and no MARKETPLACE_SESSION_START_LOG: file log skipped' })}`, { to: 'debug' })
  }
  return { base, dir }
}

async function log($: EngineInterface, { base, dir }: Log, step: Step): Promise<void> {
  const line = JSON.stringify({ ...base, ...step })
  $.ui.log(`session-start ${line}`, { to: 'debug' })
  if (dir === undefined) return
  try {
    await $.process.run(['/bin/sh', '-c', APPEND, 'session-start-log', dir, line], { timeoutMs: LOG_TIMEOUT_MS })
  } catch {
    // A log write never holds up the session; the debug log has the row.
  }
}

export const register: Register = on => {
  // Skills reload on startup and /clear. The title is set on startup only:
  // `claude -n` (session_title) wins, and a title is ignored on clear (#67389).
  on('classic.SessionStart', async ($, e, next) => {
    const result = await next(e)
    const l = await open($, 'classic.SessionStart', e.session_id, e.source)
    await log($, l, { step: 'fired', transcript_path: e.transcript_path })
    if (e.source !== 'startup' && e.source !== 'clear') return result
    await log($, l, { step: 'reload_skills_returned' })
    const skills = { ...result, reloadSkills: true } as const
    if (e.source === 'clear') {
      await log($, l, { step: 'title_skipped', result: 'clear: a title is ignored (#67389)' })
      return skills
    }
    if (e.session_title !== undefined) {
      await log($, l, { step: 'title_kept', result: e.session_title })
      return skills
    }
    const { exitCode, stdout, stderr } = await $.process.run(DATE_ARGV, { timeoutMs: DATE_TIMEOUT_MS })
    if (exitCode !== 0) {
      const why = `date exited ${exitCode}: ${excerpt(stderr)}`
      $.ui.status(`session-start ERROR: ${why}`)
      await log($, l, { step: 'error', result: why })
      await log($, l, { step: 'title_skipped', result: 'date failed' })
      return skills
    }
    const stamp = parseDate(stdout)
    if (stamp === undefined) {
      const why = `date output unexpected: ${excerpt(stdout)}`
      $.ui.status(`session-start ERROR: ${why}`)
      await log($, l, { step: 'error', result: why })
      await log($, l, { step: 'title_skipped', result: 'date output unexpected' })
      return skills
    }
    const sessionTitle = `ccm-${stamp}`
    await log($, l, { step: 'title_set', result: sessionTitle })
    return { ...skills, sessionTitle }
  })

  // The engine holds the first prompt until the first session.start settles, so
  // awaiting the reload here lands it before the first request (R3, PR #94594).
  // The wait is bounded by a `$.clock.after` deadline: a reload still running
  // then is logged as a timeout and the start goes on without it.
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    const l = await open($, 'session.start', await $.session.id())
    await log($, l, { step: 'fired', result: e.isInteractive ? 'interactive' : 'not interactive: no reload' })
    if (!e.isInteractive) return started
    await log($, l, { step: 'reload_plugins_begin' })
    const begin = await $.clock.now()
    let result = 'accepted'
    // Plain reload, never --force (D103): a held reload resolves with the docs'
    // line ending `Run /reload-plugins --force to apply.` and keeps the cache.
    // The held substring is the 2.1.299 docs' wording; live acceptance records
    // the actual 2.1.300 text.
    let timer: { cancel: () => void } | undefined
    const deadline = new Promise<'timeout'>(resolve => {
      timer = $.clock.after(RELOAD_TIMEOUT_MS, () => resolve('timeout'))
    })
    try {
      const reload = $.command.run({ command: 'reload-plugins' })
      const settled = await Promise.race([reload, deadline])
      if (settled === 'timeout') {
        reload.catch(() => undefined) // the late answer is nobody's: never an unhandled rejection
        result = `timeout: no answer after ${RELOAD_TIMEOUT_MS} ms`
        $.ui.status(`session-start ERROR: /reload-plugins ${result}`)
      } else if ((settled.text ?? '').includes('--force to apply')) {
        result = `held: ${excerpt(settled.text ?? '')}`
        $.ui.status(`session-start: /reload-plugins ${result}`)
      }
    } catch (error) {
      result = `rejected: ${excerpt(error instanceof Error ? error.message : String(error))}`
      $.ui.status(`session-start ERROR: /reload-plugins ${result}`)
    } finally {
      timer?.cancel()
    }
    await log($, l, { step: 'reload_plugins_end', result, duration_ms: (await $.clock.now()) - begin })
    return started
  })
}
