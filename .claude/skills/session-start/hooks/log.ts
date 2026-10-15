// Pure helpers of the session-start mod: no `$` here, because a hooks module
// may not pass `$` to a function it imports (plugins/mods/create, static
// analysis rules). `register.ts` holds every engine call.

// The D61/D76 session name: `ccm-` + this format, its `%z` cut to the hour
// (`-0500` -> `-05`). The same format string as `dev/handoff.py next-name`;
// `/bin/date` bypasses a mise shim, as `dev/handoff.py date_binary()` does.
export const DATE_ARGV = ['/bin/date', '+%Y%m%dT%H%M%S.%N%z'] as const
const DATE_SHAPE = /^\d{8}T\d{6}\.\d{9}[+-]\d{4}$/

// Every await is bounded: the OS calls through `$.process.run` (`timeoutMs`),
// the reload through a `$.clock.after` deadline.
export const DATE_TIMEOUT_MS = 5_000
export const LOG_TIMEOUT_MS = 5_000
export const RELOAD_TIMEOUT_MS = 30_000

// One JSON line per step, for agents to read without the debug log: sh stamps
// `ts` (UTC, ns) from the OS date and appends under umask 077 (dir 0700, file
// 0600). The directory is re-chmoded 0700 after mkdir -p (a pre-existing wider
// directory tightens), and a symlinked events.jsonl is refused (exit 3).
export const APPEND =
  'umask 077 && mkdir -p "$1" && chmod 700 "$1" && f="$1/events.jsonl" && if [ -L "$f" ]; then exit 3; fi && printf \'{"ts":"%s",%s\\n\' "$(/bin/date -u +%Y%m%dT%H%M%S.%NZ)" "${2#?}" >> "$f"'

export const LOG_SUBDIR = '.local/state/claude-code-marketplace/session-start'

// Where the JSONL file goes: the override, else under HOME, else nowhere (the
// debug row still goes out; `register.ts` logs `step: error` once).
export function logDir(override: string | undefined, home: string | undefined): string | undefined {
  if (override) return override
  if (home) return `${home}/${LOG_SUBDIR}`
  return undefined
}

// `date` output on the D61 shape, its offset cut to the hour; undefined when
// the output is anything else (a BSD date without %N, an error line).
export function parseDate(stdout: string): string | undefined {
  const text = stdout.trim()
  return DATE_SHAPE.test(text) ? text.slice(0, -2) : undefined
}

// What a logged `result` may carry of engine or OS text: credentials
// redacted, then the first 120 characters. The classification (`held:`,
// `rejected:`, `timeout:`, `date exited N:`) is prepended by the caller.
export function excerpt(text: string): string {
  return text
    .replace(/\b(token|key|secret|password)=\S+/gi, '$1=[redacted]')
    .replace(/Bearer \S+/g, 'Bearer [redacted]')
    .trim()
    .slice(0, 120)
}
