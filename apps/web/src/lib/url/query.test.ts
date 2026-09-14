import { describe, expect, it } from 'vitest';
import {
  applyQueryPatch,
  buildHref,
  getParam,
  toQueryString,
  toSearchParams,
} from './query';

describe('toSearchParams', () => {
  it('accepts a Next searchParams object, a string, and URLSearchParams', () => {
    expect(toSearchParams({ page: '2' }).get('page')).toBe('2');
    expect(toSearchParams('page=2').get('page')).toBe('2');
    expect(toSearchParams(new URLSearchParams('page=2')).get('page')).toBe('2');
  });

  it('keeps every value of a repeated param', () => {
    expect(toSearchParams({ role: ['admin', 'customer'] }).getAll('role')).toEqual([
      'admin',
      'customer',
    ]);
  });

  it('drops undefined entries', () => {
    expect([...toSearchParams({ page: undefined }).keys()]).toEqual([]);
  });
});

describe('getParam', () => {
  it('returns the value or undefined for blank ones', () => {
    expect(getParam('search=hello', 'search')).toBe('hello');
    expect(getParam('search=', 'search')).toBeUndefined();
    expect(getParam('search=%20%20', 'search')).toBeUndefined();
    expect(getParam('', 'search')).toBeUndefined();
  });
});

describe('applyQueryPatch', () => {
  it('sets and removes values', () => {
    expect(applyQueryPatch('', { search: 'hi' }).toString()).toBe('search=hi');
    expect(applyQueryPatch('search=hi', { search: null }).toString()).toBe('');
    expect(applyQueryPatch('search=hi', { search: '' }).toString()).toBe('');
    expect(applyQueryPatch('flag=true', { flag: false }).toString()).toBe('');
  });

  it('serializes numbers and true', () => {
    expect(applyQueryPatch('', { page_size: 50 }).get('page_size')).toBe('50');
    expect(applyQueryPatch('', { active: true }).get('active')).toBe('true');
  });

  it('resets page when a filter changes', () => {
    const result = applyQueryPatch('page=7&status=open', { status: 'closed' });
    expect(result.get('status')).toBe('closed');
    expect(result.get('page')).toBeNull();
  });

  it('keeps page when only pagination changes', () => {
    expect(applyQueryPatch('page=7', { page: 8 }).get('page')).toBe('8');
    expect(applyQueryPatch('page=7', { page_size: 50 }).get('page')).toBe('7');
  });

  it('does not reset page when a filter is set to its current value', () => {
    // Re-selecting the active tab should not knock the user back to page 1.
    expect(applyQueryPatch('page=7&status=open', { status: 'open' }).get('page')).toBe('7');
  });

  it('lets an explicit page in the same patch win over the reset', () => {
    const result = applyQueryPatch('page=7&status=open', { status: 'closed', page: 3 });
    expect(result.get('page')).toBe('3');
  });

  it('resets page when a filter is cleared', () => {
    expect(applyQueryPatch('page=7&status=open', { status: null }).get('page')).toBeNull();
  });

  it('sorts keys so the same state yields the same URL', () => {
    const a = applyQueryPatch('', { status: 'open', page: 2, search: 'x' }).toString();
    const b = applyQueryPatch('', { search: 'x', page: 2, status: 'open' }).toString();
    expect(a).toBe(b);
    expect(a).toBe('page=2&search=x&status=open');
  });

  it('leaves untouched params alone', () => {
    expect(applyQueryPatch('tab=all&sort=new', { search: 'x' }).get('tab')).toBe('all');
  });
});

describe('toQueryString / buildHref', () => {
  it('omits the ? for an empty query', () => {
    expect(toQueryString(new URLSearchParams())).toBe('');
    expect(buildHref('/projects', new URLSearchParams())).toBe('/projects');
  });

  it('joins pathname and query', () => {
    expect(buildHref('/projects', new URLSearchParams('page=2'))).toBe('/projects?page=2');
  });
});
