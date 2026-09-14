import { describe, expect, it } from 'vitest';
import type { PaginationMeta } from '@/generated/api/models';
import {
  DEFAULT_PAGE_SIZE,
  MAX_PAGE_SIZE,
  clampPage,
  clampPageSize,
  getItemRange,
  getPageTokens,
  hasNextPage,
  hasPreviousPage,
  normalizePaginationMeta,
  toPageQuery,
} from './pagination';

const meta = (overrides: Partial<PaginationMeta> = {}): PaginationMeta => ({
  page: 1,
  page_size: 20,
  total_items: 53,
  total_pages: 3,
  ...overrides,
});

describe('clampPage', () => {
  it('accepts positive integers from strings and numbers', () => {
    expect(clampPage('4')).toBe(4);
    expect(clampPage(4)).toBe(4);
  });

  it('falls back to page 1 for junk, zero, and negatives', () => {
    for (const value of ['', '   ', 'abc', '1.5', 0, -3, null, undefined, NaN]) {
      expect(clampPage(value)).toBe(1);
    }
  });
});

describe('clampPageSize', () => {
  it('keeps sizes inside the backend bounds', () => {
    expect(clampPageSize('50')).toBe(50);
    expect(clampPageSize(0)).toBe(1);
    expect(clampPageSize(1000)).toBe(MAX_PAGE_SIZE);
  });

  it('falls back to the default for unusable input', () => {
    expect(clampPageSize('abc')).toBe(DEFAULT_PAGE_SIZE);
    expect(clampPageSize(undefined)).toBe(DEFAULT_PAGE_SIZE);
  });
});

describe('toPageQuery', () => {
  it('produces params that are always valid for the backend', () => {
    expect(toPageQuery('2', '50')).toEqual({ page: 2, page_size: 50 });
    expect(toPageQuery('-1', '9999')).toEqual({ page: 1, page_size: MAX_PAGE_SIZE });
  });
});

describe('normalizePaginationMeta', () => {
  const fallback = { page: 2, page_size: 20 };

  it('passes through a well-formed meta', () => {
    expect(normalizePaginationMeta(meta(), fallback)).toEqual(meta());
  });

  it('derives totals when the backend omits meta', () => {
    expect(normalizePaginationMeta(undefined, { page: 1, page_size: 10 }, 4)).toEqual({
      page: 1,
      page_size: 10,
      total_items: 4,
      total_pages: 1,
    });
  });

  it('computes total_pages from total_items when absent', () => {
    const result = normalizePaginationMeta({ page: 1, page_size: 20, total_items: 53 }, fallback);
    expect(result.total_pages).toBe(3);
  });

  it('never reports zero pages for an empty list', () => {
    const result = normalizePaginationMeta({ page: 1, page_size: 20, total_items: 0 }, fallback);
    expect(result.total_pages).toBe(1);
  });
});

describe('hasPreviousPage / hasNextPage', () => {
  it('detects the edges', () => {
    expect(hasPreviousPage(meta({ page: 1 }))).toBe(false);
    expect(hasNextPage(meta({ page: 1 }))).toBe(true);
    expect(hasPreviousPage(meta({ page: 3 }))).toBe(true);
    expect(hasNextPage(meta({ page: 3 }))).toBe(false);
  });
});

describe('getItemRange', () => {
  it('describes the current slice', () => {
    expect(getItemRange(meta({ page: 1 }))).toEqual({ from: 1, to: 20 });
    expect(getItemRange(meta({ page: 3 }))).toEqual({ from: 41, to: 53 });
  });

  it('returns null when there is nothing to show', () => {
    expect(getItemRange(meta({ total_items: 0, total_pages: 1 }))).toBeNull();
    // Page beyond the data (e.g. a stale URL) must not render a bogus range.
    expect(getItemRange(meta({ page: 9 }))).toBeNull();
  });
});

describe('getPageTokens', () => {
  it('lists every page when they all fit', () => {
    expect(getPageTokens(meta({ page: 1, total_pages: 5 }))).toEqual([1, 2, 3, 4, 5]);
  });

  it('collapses long gaps into a single ellipsis', () => {
    expect(getPageTokens(meta({ page: 10, total_pages: 20 }))).toEqual([
      1,
      'ellipsis',
      9,
      10,
      11,
      'ellipsis',
      20,
    ]);
  });

  it('fills a one-page gap instead of eliding a single number', () => {
    // Page 2 is the only page between 1 and the sibling window, so it is shown.
    expect(getPageTokens(meta({ page: 4, total_pages: 10 }))).toEqual([
      1,
      2,
      3,
      4,
      5,
      'ellipsis',
      10,
    ]);
  });

  it('lists every page while they still fit in the control', () => {
    expect(getPageTokens(meta({ page: 3, total_pages: 6 }))).toEqual([1, 2, 3, 4, 5, 6]);
    expect(getPageTokens(meta({ page: 4, total_pages: 7 }))).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });

  it('clamps a current page outside the range', () => {
    expect(getPageTokens(meta({ page: 99, total_pages: 3 }))).toEqual([1, 2, 3]);
  });

  it('handles a single page', () => {
    expect(getPageTokens(meta({ page: 1, total_pages: 1 }))).toEqual([1]);
  });
});
