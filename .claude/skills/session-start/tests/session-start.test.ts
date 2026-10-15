import { expect, mock, test } from 'claude-code/testing'

const DATE_STDOUT = '20261014T184849.575921000-0500\n'

test('startup without a title: reloadSkills and a ccm- title from the date command', async ($, on) => {
  const argvs: (readonly string[])[] = []
  on('process.run', ($, e) => {
    argvs.push(e.argv)
    return { value: { exitCode: 0, stdout: DATE_STDOUT, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('classic.SessionStart', () => ({}))

  const result = await $.classic.SessionStart({ source: 'startup' })

  expect(argvs).toEqual([['date', '+%Y%m%dT%H%M%S.%N%z']])
  expect(result).toEqual({ reloadSkills: true, sessionTitle: 'ccm-20261014T184849.575921000-05' })
})

test('startup with a title from claude -n: reloadSkills only, no date call', async ($, on) => {
  const argvs: (readonly string[])[] = []
  on('process.run', ($, e) => {
    argvs.push(e.argv)
    return { value: { exitCode: 0, stdout: DATE_STDOUT, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('classic.SessionStart', () => ({}))

  const result = await $.classic.SessionStart({ source: 'startup', session_title: 'ccm-20261014T034212.915972000-05' })

  expect(argvs).toEqual([])
  expect(result).toEqual({ reloadSkills: true })
})

test('clear: reloadSkills only; a title is ignored on clear (#67389), so no date call', async ($, on) => {
  const argvs: (readonly string[])[] = []
  on('process.run', ($, e) => {
    argvs.push(e.argv)
    return { value: { exitCode: 0, stdout: DATE_STDOUT, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('classic.SessionStart', () => ({}))

  const result = await $.classic.SessionStart({ source: 'clear' })

  expect(argvs).toEqual([])
  expect(result).toEqual({ reloadSkills: true })
})

test('resume, compact and fork pass the classic answer through unchanged', async ($, on) => {
  const argvs: (readonly string[])[] = []
  on('process.run', ($, e) => {
    argvs.push(e.argv)
    return { value: { exitCode: 0, stdout: DATE_STDOUT, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  on('classic.SessionStart', () => ({ additionalContext: ['beneath'] }))

  for (const source of ['resume', 'compact', 'fork'] as const) {
    expect(await $.classic.SessionStart({ source })).toEqual({ additionalContext: ['beneath'] })
  }
  expect(argvs).toEqual([])
})

const START = { surface: 'terminal', isInteractive: true, cwd: '/work' } as const

test('interactive start: session.start settles only after a plain /reload-plugins resolved', async ($, on) => {
  const clock = mock.clock(on)
  const order: string[] = []
  on('command.run', async ($, e) => {
    order.push(`/${e.command} args=${JSON.stringify(e.args)}`)
    await clock.sleep(1000)
    order.push('reload resolved')
    return { text: 'Reloaded plugins' }
  })
  on('session.start', () => ({ cwd: '/work' }))

  const started = $.session.start(START).then(() => order.push('session.start settled'))
  await clock.settle()
  expect(order).toEqual(['/reload-plugins args=""'])
  await clock.advance(1000)
  await started

  expect(order).toEqual(['/reload-plugins args=""', 'reload resolved', 'session.start settled'])
})

test('non-interactive start (-p, SDK): no reload is run', async ($, on) => {
  const commands: string[] = []
  on('command.run', ($, e) => {
    commands.push(e.command)
    return { text: '' }
  })
  on('session.start', () => ({ cwd: '/work' }))

  expect(await $.session.start({ surface: null, isInteractive: false, cwd: '/work' })).toEqual({ cwd: '/work' })
  expect(commands).toEqual([])
})

const HELD =
  'This reload changes MCP tools (docs) — your next message will re-read the whole conversation instead of using the cache. Run /reload-plugins --force to apply.'

test('a held reload is surfaced as a status message, never forced', async ($, on) => {
  const commands: string[] = []
  const statuses: (string | undefined)[] = []
  on('command.run', ($, e) => {
    commands.push(`/${e.command} ${e.args}`.trim())
    return { text: HELD }
  })
  on('ui.status', ($, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('session.start', () => ({ cwd: '/work' }))

  await $.session.start(START)

  expect(commands).toEqual(['/reload-plugins'])
  expect(statuses).toEqual([`session-start: /reload-plugins held: ${HELD}`])
})

test('a rejected reload is surfaced as a status message and the session still starts', async ($, on) => {
  // No command.run stub: the kit's bottom hook rejects, as the engine rejects a refused command.
  const statuses: (string | undefined)[] = []
  on('ui.status', ($, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('session.start', () => ({ cwd: '/work' }))

  expect(await $.session.start(START)).toEqual({ cwd: '/work' })
  expect(statuses.length).toBe(1)
  expect(statuses[0]).toMatch(/^session-start ERROR: \/reload-plugins rejected: .+/)
})

test('a failed date command keeps reloadSkills, sets no title and says so', async ($, on) => {
  const statuses: (string | undefined)[] = []
  on('process.run', () => ({ value: { exitCode: 1, stdout: '', stderr: 'date: illegal option', isStdoutTruncated: false, isStderrTruncated: false } }))
  on('ui.status', ($, e) => {
    statuses.push(e.text)
    return { value: undefined }
  })
  on('classic.SessionStart', () => ({}))

  expect(await $.classic.SessionStart({ source: 'startup' })).toEqual({ reloadSkills: true })
  expect(statuses).toEqual(['session-start ERROR: date exited 1: date: illegal option'])
})
