import type { On, ProcessRunResult } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'
import { APPEND, DATE_ARGV, DATE_TIMEOUT_MS, LOG_TIMEOUT_MS, RELOAD_TIMEOUT_MS, excerpt, logDir, parseDate } from '../hooks/log.ts'

const LOG_DIR = '/tmp/session-start-test-log'
const ran = (exitCode: number, stdout: string, stderr = ''): ProcessRunResult =>
  ({ exitCode, stdout, stderr, isStdoutTruncated: false, isStderrTruncated: false })
const DATE_OK = ran(0, '20261014T184849.575921000-0500\n')
const START = { surface: 'terminal', isInteractive: true, cwd: '/work' } as const
const HELD =
  'This reload changes MCP tools (docs) — your next message will re-read the whole conversation instead of using the cache. Run /reload-plugins --force to apply.'

// Stands for the engine and the OS beneath the mod. Log rows arrive as the
// `/bin/sh` append the mod runs (argv[4] the directory, argv[5] the row);
// debug rows as the `$.ui.log` text after the `session-start ` prefix.
function world(on: On, options: { date?: ProcessRunResult; classic?: object; env?: Record<string, string> } = {}) {
  const rows: Record<string, unknown>[] = []
  const debug: Record<string, unknown>[] = []
  const dates: (readonly string[])[] = []
  const timeouts: (number | undefined)[] = []
  const statuses: (string | undefined)[] = []
  const clock = mock.clock(on)
  mock.env(on, options.env ?? { MARKETPLACE_SESSION_START_LOG: LOG_DIR, HOME: '/home/test' })
  on('process.run', ($, e) => {
    timeouts.push(e.init?.timeoutMs)
    if (e.argv[0] !== '/bin/sh') {
      dates.push(e.argv)
      return { value: options.date ?? DATE_OK }
    }
    expect(e.argv[2]).toBe(APPEND)
    expect(e.argv[4]).toBe(LOG_DIR)
    rows.push(JSON.parse(e.argv[5] ?? ''))
    return { value: ran(0, '') }
  })
  on('ui.log', ($, e) => {
    debug.push(JSON.parse(e.text.replace(/^session-start /, '')))
    return { value: undefined }
  })
  on('ui.status', ($, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('session.id', () => ({ value: 'sess-1' }))
  on('session.version', () => ({ value: { version: '2.1.300', base: '2.1.300' } }))
  on('classic.SessionStart', () => options.classic ?? {})
  on('session.start', () => ({ cwd: '/work' }))
  const steps = () => rows.map(r => [r.step, r.result])
  return { rows, debug, dates, timeouts, statuses, clock, steps }
}

test('startup without a title: reloadSkills and a ccm- title from /bin/date', async ($, on) => {
  const w = world(on)
  const result = await $.classic.SessionStart({ source: 'startup', session_id: 'sess-1' })

  expect(w.dates).toEqual([['/bin/date', '+%Y%m%dT%H%M%S.%N%z']])
  expect(result).toEqual({ reloadSkills: true, sessionTitle: 'ccm-20261014T184849.575921000-05' })
  expect(w.rows[0]).toMatchObject({ session_id: 'sess-1', cli_version: '2.1.300', event: 'classic.SessionStart', source: 'startup' })
  expect(w.steps()).toEqual([
    ['fired', undefined],
    ['reload_skills_returned', undefined],
    ['title_set', 'ccm-20261014T184849.575921000-05'],
  ])
  expect(w.debug.map(r => r.step)).toEqual(['fired', 'reload_skills_returned', 'title_set'])
})

test('every process.run is bounded: the log append and the date call carry timeoutMs', async ($, on) => {
  const w = world(on)
  await $.classic.SessionStart({ source: 'startup' })

  // fired, reload_skills_returned (appends), date, title_set (append)
  expect(w.timeouts).toEqual([LOG_TIMEOUT_MS, LOG_TIMEOUT_MS, DATE_TIMEOUT_MS, LOG_TIMEOUT_MS])
  expect(w.timeouts.every(ms => ms !== undefined && ms > 0)).toBe(true)
})

test('startup with a title from claude -n: reloadSkills only, no date call', async ($, on) => {
  const w = world(on)
  const result = await $.classic.SessionStart({ source: 'startup', session_title: 'ccm-20261014T034212.915972000-05' })

  expect(w.dates).toEqual([])
  expect(result).toEqual({ reloadSkills: true })
  expect(w.steps().at(-1)).toEqual(['title_kept', 'ccm-20261014T034212.915972000-05'])
})

test('clear: reloadSkills only; a title is ignored on clear (#67389), so no date call', async ($, on) => {
  const w = world(on)
  const result = await $.classic.SessionStart({ source: 'clear' })

  expect(w.dates).toEqual([])
  expect(result).toEqual({ reloadSkills: true })
  expect(w.steps().at(-1)).toEqual(['title_skipped', 'clear: a title is ignored (#67389)'])
})

test('resume, compact and fork pass the classic answer through unchanged', async ($, on) => {
  const w = world(on, { classic: { additionalContext: ['beneath'] } })
  for (const source of ['resume', 'compact', 'fork'] as const) {
    expect(await $.classic.SessionStart({ source })).toEqual({ additionalContext: ['beneath'] })
  }
  expect(w.dates).toEqual([])
  expect(w.steps()).toEqual([['fired', undefined], ['fired', undefined], ['fired', undefined]])
})

test('a failed date command keeps reloadSkills, sets no title and says so', async ($, on) => {
  const w = world(on, { date: ran(1, '', 'date: illegal option') })

  expect(await $.classic.SessionStart({ source: 'startup' })).toEqual({ reloadSkills: true })
  expect(w.statuses).toEqual(['session-start ERROR: date exited 1: date: illegal option'])
  expect(w.steps().slice(-2)).toEqual([
    ['error', 'date exited 1: date: illegal option'],
    ['title_skipped', 'date failed'],
  ])
})

test('date output off the D61 shape (no %N) is refused: no title, an error row', async ($, on) => {
  const w = world(on, { date: ran(0, '20261014T184849-0500\n') })

  expect(await $.classic.SessionStart({ source: 'startup' })).toEqual({ reloadSkills: true })
  expect(w.statuses).toEqual(['session-start ERROR: date output unexpected: 20261014T184849-0500'])
  expect(w.steps().slice(-2)).toEqual([
    ['error', 'date output unexpected: 20261014T184849-0500'],
    ['title_skipped', 'date output unexpected'],
  ])
})

test('parseDate accepts only the D61 shape and cuts the offset to its hour', () => {
  expect(parseDate('20261014T184849.575921000-0500\n')).toBe('20261014T184849.575921000-05')
  expect(parseDate('20261014T184849.575921000+0000')).toBe('20261014T184849.575921000+00')
  for (const bad of ['20261014T184849-0500', '20261014T184849.575921000-05', 'date: bad', '', '20261014T184849.575921000-0500 extra']) {
    expect(parseDate(bad)).toBe(undefined)
  }
})

test('no HOME and no override: the file append is skipped, the debug rows stay, an error row says so', async ($, on) => {
  const w = world(on, { env: {} })
  const result = await $.classic.SessionStart({ source: 'startup' })

  expect(result).toEqual({ reloadSkills: true, sessionTitle: 'ccm-20261014T184849.575921000-05' })
  expect(w.rows).toEqual([])
  expect(w.timeouts).toEqual([DATE_TIMEOUT_MS])
  expect(w.debug.map(r => [r.step, r.result])).toEqual([
    ['error', 'no HOME and no MARKETPLACE_SESSION_START_LOG: file log skipped'],
    ['fired', undefined],
    ['reload_skills_returned', undefined],
    ['title_set', 'ccm-20261014T184849.575921000-05'],
  ])
})

test('logDir prefers the override, then HOME, else nothing', () => {
  expect(logDir('/x', '/home/u')).toBe('/x')
  expect(logDir(undefined, '/home/u')).toBe('/home/u/.local/state/claude-code-marketplace/session-start')
  expect(logDir(undefined, undefined)).toBe(undefined)
  expect(logDir('', '')).toBe(undefined)
})

test('interactive start: session.start settles only after a plain /reload-plugins resolved', async ($, on) => {
  const w = world(on)
  const order: string[] = []
  on('command.run', async ($, e) => {
    order.push(`/${e.command} args=${JSON.stringify(e.args)}`)
    await w.clock.sleep(1000)
    order.push('reload resolved')
    return { text: 'Reloaded plugins' }
  })

  const started = $.session.start(START).then(() => order.push('session.start settled'))
  await w.clock.settle()
  expect(order).toEqual(['/reload-plugins args=""'])
  await w.clock.advance(1000)
  await started

  expect(order).toEqual(['/reload-plugins args=""', 'reload resolved', 'session.start settled'])
  expect(w.rows[0]).toMatchObject({ session_id: 'sess-1', cli_version: '2.1.300', event: 'session.start' })
  expect(w.steps()).toEqual([['fired', 'interactive'], ['reload_plugins_begin', undefined], ['reload_plugins_end', 'accepted']])
  expect(w.rows[2]?.duration_ms).toBe(1000)
  expect(w.statuses).toEqual([])
})

test('a reload still running at the deadline is logged as a timeout and the start goes on', async ($, on) => {
  const w = world(on)
  const order: string[] = []
  on('command.run', async () => {
    await w.clock.sleep(RELOAD_TIMEOUT_MS * 2)
    order.push('reload resolved late')
    return { text: 'Reloaded plugins' }
  })

  const started = $.session.start(START).then(() => order.push('session.start settled'))
  await w.clock.advance(RELOAD_TIMEOUT_MS - 1)
  expect(order).toEqual([])
  await w.clock.advance(1)
  await started

  expect(order).toEqual(['session.start settled'])
  expect(w.statuses).toEqual([`session-start ERROR: /reload-plugins timeout: no answer after ${RELOAD_TIMEOUT_MS} ms`])
  expect(w.steps().at(-1)).toEqual(['reload_plugins_end', `timeout: no answer after ${RELOAD_TIMEOUT_MS} ms`])
  expect(w.rows.at(-1)?.duration_ms).toBe(RELOAD_TIMEOUT_MS)
})

test('non-interactive start (-p, SDK): no reload is run', async ($, on) => {
  const w = world(on)
  const commands: string[] = []
  on('command.run', ($, e) => {
    commands.push(e.command)
    return { text: '' }
  })

  expect(await $.session.start({ surface: null, isInteractive: false, cwd: '/work' })).toEqual({ cwd: '/work' })
  expect(commands).toEqual([])
  expect(w.steps()).toEqual([['fired', 'not interactive: no reload']])
})

test('a held reload is surfaced as a status message, never forced; the text is an excerpt', async ($, on) => {
  const w = world(on)
  const commands: string[] = []
  on('command.run', ($, e) => {
    commands.push(`/${e.command} ${e.args}`.trim())
    return { text: HELD }
  })

  await $.session.start(START)

  expect(commands).toEqual(['/reload-plugins'])
  expect(w.statuses).toEqual([`session-start: /reload-plugins held: ${HELD.slice(0, 120)}`])
  expect(w.steps().at(-1)).toEqual(['reload_plugins_end', `held: ${HELD.slice(0, 120)}`])
})

test('a rejected reload is surfaced as a status message and the session still starts', async ($, on) => {
  // No command.run stub: the kit's bottom hook rejects, as the engine rejects a refused command.
  const w = world(on)

  expect(await $.session.start(START)).toEqual({ cwd: '/work' })
  expect(w.statuses.length).toBe(1)
  expect(w.statuses[0]).toMatch(/^session-start ERROR: \/reload-plugins rejected: .+/)
  expect(w.steps().at(-1)?.[0]).toBe('reload_plugins_end')
  expect(String(w.steps().at(-1)?.[1])).toMatch(/^rejected: .+/)
})

test('logged text is redacted and cut: credentials in a held line never reach a row', async ($, on) => {
  const w = world(on)
  const leaky = `Refused: token=abc.def Bearer eyJ0 password=hunter2 KEY=k1 ${'x'.repeat(200)} --force to apply.`
  on('command.run', () => ({ text: leaky }))

  await $.session.start(START)

  const result = String(w.steps().at(-1)?.[1])
  expect(result.startsWith('held: Refused: token=[redacted] Bearer [redacted] password=[redacted] KEY=[redacted] xxx')).toBe(true)
  expect(result.length).toBeLessThanOrEqual('held: '.length + 120)
  expect(result.includes('abc.def')).toBe(false)
  expect(result.includes('eyJ0')).toBe(false)
  expect(result.includes('hunter2')).toBe(false)
})

test('excerpt: redaction first, then the first 120 characters', () => {
  expect(excerpt('secret=s3 ok')).toBe('secret=[redacted] ok')
  expect(excerpt('Authorization: Bearer abc\n')).toBe('Authorization: Bearer [redacted]')
  expect(excerpt('a'.repeat(300)).length).toBe(120)
  expect(excerpt('  padded  ')).toBe('padded')
})
