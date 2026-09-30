/** Time-zone helpers. The "day" of a user is their local calendar day (default Indian/Reunion). */

export function isValidTimeZone(tz: string): boolean {
  try {
    new Intl.DateTimeFormat('en-US', { timeZone: tz });
    return true;
  } catch {
    return false;
  }
}

/** Offset in ms of `tz` at instant `ms` (local wall time minus UTC). */
function offsetAt(tz: string, ms: number): number {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: tz, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  }).formatToParts(new Date(ms));
  const get = (t: string) => Number(parts.find((p) => p.type === t)!.value);
  const wall = Date.UTC(get('year'), get('month') - 1, get('day'), get('hour'), get('minute'), get('second'));
  return wall - Math.floor(ms / 1000) * 1000;
}

/** Local calendar date (YYYY-MM-DD) of instant `ms` in `tz`. */
export function localDate(tz: string, ms: number): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' })
    .format(new Date(ms));
}

/** UTC instant of local midnight starting the given local date in tz. */
function localMidnight(tz: string, ymd: string): number {
  const [y, m, d] = ymd.split('-').map(Number);
  const guess = Date.UTC(y, m - 1, d);
  // Two passes handle DST transitions.
  let t = guess - offsetAt(tz, guess);
  t = guess - offsetAt(tz, t);
  return t;
}

/** [start, end) of the user's current local day, as UTC ms. */
export function dayBounds(tz: string, now: number): { start: number; end: number; date: string } {
  const date = localDate(tz, now);
  const start = localMidnight(tz, date);
  const [y, m, d] = date.split('-').map(Number);
  const next = new Date(Date.UTC(y, m - 1, d + 1)).toISOString().slice(0, 10);
  return { start, end: localMidnight(tz, next), date };
}
