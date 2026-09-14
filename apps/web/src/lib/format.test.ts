import { describe, expect, it } from 'vitest';
import {
  formatBytes,
  formatDate,
  formatDateTime,
  formatNumber,
  formatNumberLatin,
  isoToTehranLocal,
  tehranLocalToIso,
} from './format';

describe('formatNumber', () => {
  it('uses Persian digits and grouping', () => {
    expect(formatNumber(1234567)).toBe('۱٬۲۳۴٬۵۶۷');
    expect(formatNumber(0)).toBe('۰');
  });

  it('can produce Latin digits for copyable values', () => {
    expect(formatNumberLatin(1405)).toBe('1,405');
  });
});

describe('formatDate / formatDateTime', () => {
  it('renders the Jalali calendar', () => {
    // 2026-08-29 UTC is 1405-06-07 in the Persian calendar.
    expect(formatDate('2026-08-29T11:34:31Z')).toContain('۱۴۰۵');
    expect(formatDate('2026-08-29T11:34:31Z')).toContain('شهریور');
  });

  it('is stable regardless of the runtime time zone', () => {
    // Pinned to Asia/Tehran (+03:30 year-round since Iran dropped DST in 2022),
    // so this must not shift with process.env.TZ.
    const formatted = formatDateTime('2026-08-29T11:34:31Z');
    expect(formatted).toContain('۱۵:۰۴');
  });

  it('degrades gracefully on unparseable input', () => {
    expect(formatDate('not-a-date')).toBe('—');
    expect(formatDateTime('')).toBe('—');
  });
});

describe('formatBytes', () => {
  it('scales through binary units', () => {
    expect(formatBytes(0)).toBe('۰ بایت');
    expect(formatBytes(512)).toBe('۵۱۲ بایت');
    expect(formatBytes(1024)).toBe('۱ کیلوبایت');
    expect(formatBytes(1536)).toBe('۱٫۵ کیلوبایت');
    expect(formatBytes(5 * 1024 * 1024)).toBe('۵ مگابایت');
  });

  it('caps at the largest known unit', () => {
    expect(formatBytes(1024 ** 5)).toContain('ترابایت');
  });

  it('rejects nonsense sizes', () => {
    expect(formatBytes(-1)).toBe('—');
    expect(formatBytes(Number.NaN)).toBe('—');
  });
});

describe('Tehran datetime-local round trip', () => {
  it('reads a typed wall time as Tehran, not as the runtime zone', () => {
    expect(tehranLocalToIso('2026-09-01T12:00')).toBe('2026-09-01T08:30:00.000Z');
  });

  it('accepts seconds and rolls the date backwards across midnight', () => {
    expect(tehranLocalToIso('2026-09-01T02:00:30')).toBe('2026-08-31T22:30:30.000Z');
  });

  it('rejects anything that is not a datetime-local value', () => {
    expect(tehranLocalToIso('')).toBeNull();
    expect(tehranLocalToIso('2026-09-01')).toBeNull();
    expect(tehranLocalToIso('nonsense')).toBeNull();
  });

  it('prefills an input with the same wall time it would send back', () => {
    expect(isoToTehranLocal('2026-09-01T08:30:00Z')).toBe('2026-09-01T12:00');
    expect(tehranLocalToIso(isoToTehranLocal('2026-09-01T08:30:00Z'))).toBe(
      '2026-09-01T08:30:00.000Z',
    );
  });

  it('has nothing to prefill from an absent or invalid deadline', () => {
    expect(isoToTehranLocal(null)).toBe('');
    expect(isoToTehranLocal(undefined)).toBe('');
    expect(isoToTehranLocal('not-a-date')).toBe('');
  });

  it('agrees with what formatDateTime displays for the same instant', () => {
    const iso = tehranLocalToIso('2026-09-01T12:00')!;
    expect(formatDateTime(iso)).toContain('۱۲:۰۰');
  });
});
