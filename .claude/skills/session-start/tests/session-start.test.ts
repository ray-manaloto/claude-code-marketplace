import type { On, ProcessRunResult } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

const LOG_DIR = '/tmp/session-start-test-log'
const ran = (exitCode: number, stdout: string, stderr = ''): ProcessRunResult =>
  ({ exitCode, stdout, stderr, isStdoutTruncated: false, isStderrTruncated: false })
const DATE_OK = ran(0, '20261014T184849.575921000-0500\n')
const START = { surface: 'terminal', isInteractive: true, cwd: '/work' } as const
const HELD =
  'This reload changes MCP tools (docs) — your next message will re-read the whole conversation instead of using the cache. Run /reload-plugins --force to apply.'

// Stands for the engine and the OS beneath the mod. Log rows arrive as the
// `/bin/sh` append the mod runs (argv[4] the directory, argv[5] the row).
function world(on: On, options: { date?: ProcessRunResult; classic?: object } = {}) {
  const rows: Record<string, unknown>[] = []
  const dates: (readonly string[])[] = []
  const statuses: (string | undefined)[] = []
  const clock = mock.clock(on)
  mock.env(on, { MARKETPLACE_SESSION_START_LOG: LOG_DIR, HOME: '/home/test' })
  on('process.run', ($, e) => {
    if (e.argv[0] !== '/bin/sh') {
      dates.push(e.argv)
      return { value: options.date ?? DATE_OK }
    }
    expect(e.argv[4]).toBe(LOG_DIR)
    rows.push(JSON.parse(e.argv[5] ?? ''))
    return { value: ran(0, '') }
  })
  on('ui.log', () => ({ value: undefined }))
  on('ui.status', ($, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('session.id', () => ({ value: 'sess-1' }))
  on('session.version', () => ({ value: { version: '2.1.300', base: '2.1.300' } }))
  on('classic.SessionStart', () => options.classic ?? {})
  on('session.start', () => ({ cwd: '/work' }))
  const steps = () => rows.map(r => [r.step, r.result])
  return { rows, dates, statuses, clock, steps }
}

test('startup without a title: reloadSkills and a ccm- title from the date command', async ($, on) => {
  const w = world(on)
  const result = await $.classic.SessionStart({ source: 'startup', session_id: 'sess-1' })

  expect(w.dates).toEqual([['date', '+%Y%m%dT%H%M%S.%N%z']])
  expect(result).toEqual({ reloadSkills: true, sessionTitle: 'ccm-20261014T184849.575921000-05' })
  expect(w.rows[0]).toMatchObject({ session_id: 'sess-1', cli_version: '2.1.300', event: 'classic.SessionStart', source: 'startup' })
  expect(w.steps()).toEqual([
    ['fired', undefined],
    ['reload_skills_returned', undefined],
    ['title_set', 'ccm-20261014T184849.575921000-05'],
  ])
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

test('a held reload is surfaced as a status message, never forced', async ($, on) => {
  const w = world(on)
  const commands: string[] = []
  on('command.run', ($, e) => {
    commands.push(`/${e.command} ${e.args}`.trim())
    return { text: HELD }
  })

  await $.session.start(START)

  expect(commands).toEqual(['/reload-plugins'])
  expect(w.statuses).toEqual([`session-start: /reload-plugins held: ${HELD}`])
  expect(w.steps().at(-1)).toEqual(['reload_plugins_end', `held: ${HELD}`])
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
