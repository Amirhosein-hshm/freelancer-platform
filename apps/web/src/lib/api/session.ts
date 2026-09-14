import type { NextResponse } from 'next/server';

export const ACCESS_TOKEN_COOKIE = 'didar_at';
export const REFRESH_TOKEN_COOKIE = 'didar_rt';

export interface SessionTokens {
  access_token: string;
  refresh_token: string;
  refresh_token_jti?: string;
}

const BASE_COOKIE_OPTIONS = {
  httpOnly: true,
  sameSite: 'lax' as const,
  // Secure cookies break plain-HTTP non-localhost hosts; mirror the runtime env.
  secure: process.env.NODE_ENV === 'production',
  path: '/',
};

/**
 * Applies rotated session cookies to a browser-facing response.
 * Used by the API proxy route and proxy.ts only.
 */
export function applySessionCookies(response: NextResponse, tokens: SessionTokens): void {
  response.cookies.set(ACCESS_TOKEN_COOKIE, tokens.access_token, BASE_COOKIE_OPTIONS);
  response.cookies.set(REFRESH_TOKEN_COOKIE, tokens.refresh_token, BASE_COOKIE_OPTIONS);
}

export function clearSessionCookies(response: NextResponse): void {
  response.cookies.set(ACCESS_TOKEN_COOKIE, '', { ...BASE_COOKIE_OPTIONS, maxAge: 0 });
  response.cookies.set(REFRESH_TOKEN_COOKIE, '', { ...BASE_COOKIE_OPTIONS, maxAge: 0 });
}

/**
 * Optimistic expiry check for the access token. Decodes the JWT payload only
 * (no verification — the backend stays authoritative). Returns true when the
 * token is missing, malformed, or past its `exp`. A token that cannot be
 * decoded is treated as still valid so the backend makes the final call.
 */
export function isAccessTokenExpired(token: string | undefined): boolean {
  if (!token) return true;
  const exp = decodeJwtExp(token);
  if (exp === null) return false;
  return exp * 1000 <= Date.now();
}

export function decodeJwtExp(token: string): number | null {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  try {
    const payload = JSON.parse(atobUrl(parts[1])) as { exp?: unknown };
    return typeof payload.exp === 'number' ? payload.exp : null;
  } catch {
    return null;
  }
}

function atobUrl(value: string): string {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/');
  const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4);
  if (typeof atob === 'function') {
    return atob(padded);
  }
  return Buffer.from(padded, 'base64').toString('utf-8');
}
