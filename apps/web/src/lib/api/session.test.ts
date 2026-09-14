import { describe, expect, it } from 'vitest';
import { isAccessTokenExpired } from './session';

function makeToken(payload: Record<string, unknown>): string {
  const base64 = (input: string) =>
    typeof btoa === 'function' ? btoa(input) : Buffer.from(input).toString('base64');
  const encode = (obj: unknown) => base64(JSON.stringify(obj)).replace(/=+$/, '');
  return `${encode({ alg: 'HS256', typ: 'JWT' })}.${encode(payload)}.signature`;
}

describe('isAccessTokenExpired', () => {
  it('treats missing tokens as expired', () => {
    expect(isAccessTokenExpired(undefined)).toBe(true);
    expect(isAccessTokenExpired('')).toBe(true);
  });

  it('detects past and future expiries', () => {
    const now = Math.floor(Date.now() / 1000);
    expect(isAccessTokenExpired(makeToken({ exp: now - 60 }))).toBe(true);
    expect(isAccessTokenExpired(makeToken({ exp: now + 60 }))).toBe(false);
  });

  it('treats malformed tokens as still valid so the backend decides', () => {
    expect(isAccessTokenExpired('garbage')).toBe(false);
    expect(isAccessTokenExpired('a.b.c')).toBe(false);
  });

  it('treats tokens without exp as still valid', () => {
    expect(isAccessTokenExpired(makeToken({ sub: 'u1' }))).toBe(false);
  });
});
