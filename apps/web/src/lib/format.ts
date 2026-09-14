/**
 * Persian-first display formatting. `Intl` already resolves `fa-IR` to the
 * Persian (Jalali) calendar with Persian digits, so no date library is needed.
 *
 * Time zone is pinned rather than left to the runtime: the server renders in
 * UTC and the browser in local time, which would produce different text for the
 * same timestamp and trip a hydration mismatch.
 */

const LOCALE = 'fa-IR';
const TIME_ZONE = 'Asia/Tehran';

export function formatNumber(value: number): string {
  return value.toLocaleString(LOCALE);
}

/** Latin digits — for identifiers and anything the user may copy. */
export function formatNumberLatin(value: number): string {
  return value.toLocaleString('fa-IR-u-nu-latn');
}

export function formatDate(value: string | Date): string {
  const date = toDate(value);
  if (!date) return '—';
  return date.toLocaleDateString(LOCALE, { dateStyle: 'medium', timeZone: TIME_ZONE });
}

export function formatDateTime(value: string | Date): string {
  const date = toDate(value);
  if (!date) return '—';
  return date.toLocaleString(LOCALE, {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: TIME_ZONE,
  });
}

function toDate(value: string | Date): Date | null {
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

const BYTE_UNITS = ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت', 'ترابایت'] as const;

/** Binary file sizes (1 KiB = 1024 B), matching what upload dialogs report. */
export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return '—';
  if (bytes === 0) return `۰ ${BYTE_UNITS[0]}`;

  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), BYTE_UNITS.length - 1);
  const size = bytes / 1024 ** exponent;
  // Whole bytes never need decimals; larger units get one for precision.
  const rounded = exponent === 0 ? Math.round(size) : Math.round(size * 10) / 10;

  return `${rounded.toLocaleString(LOCALE, { maximumFractionDigits: 1 })} ${BYTE_UNITS[exponent]}`;
}

/**
 * `datetime-local` inputs exchange wall-clock text with no zone, and the
 * browser's own zone is not necessarily the one this app displays. Both
 * directions therefore treat the typed value as Tehran time, so a deadline reads
 * back exactly as it was entered no matter where the user is.
 *
 * Iran has been on a fixed +03:30 since it abolished DST in 2022, so a constant
 * offset is correct rather than an approximation.
 */
const TEHRAN_OFFSET_MS = 3.5 * 60 * 60 * 1000;

/** `'2026-09-01T12:00'` (Tehran) -> `'2026-09-01T08:30:00.000Z'`. */
export function tehranLocalToIso(local: string): string | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$/.exec(local.trim());
  if (!match) return null;
  const [, year, month, day, hour, minute, second] = match;
  const utcMs =
    Date.UTC(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second ?? 0)) -
    TEHRAN_OFFSET_MS;
  const date = new Date(utcMs);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

/** Inverse of `tehranLocalToIso`, for prefilling a `datetime-local` input. */
export function isoToTehranLocal(iso: string | null | undefined): string {
  if (!iso) return '';
  const date = toDate(iso);
  if (!date) return '';
  const shifted = new Date(date.getTime() + TEHRAN_OFFSET_MS);
  return shifted.toISOString().slice(0, 16);
}
