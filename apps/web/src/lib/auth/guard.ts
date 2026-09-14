/**
 * Pure route-protection decisions shared by proxy.ts. Network effects
 * (refresh, redirects) live in the proxy itself; this module stays testable.
 */

export type GuardAction =
  | { kind: 'allow' }
  | { kind: 'redirect-login' }
  | { kind: 'redirect-dashboard' }
  | { kind: 'refresh' };

/** Routes reachable without a session. Everything else requires auth. */
export const PUBLIC_ROUTES = new Set(['/', '/login', '/register', '/forgot-password']);

export function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.has(pathname);
}

/** Auth pages an already-authenticated user should be moved away from. */
const AUTH_ENTRY_ROUTES = new Set(['/login', '/register']);

export interface GuardInput {
  pathname: string;
  /** A refresh cookie is the source of truth for "has a session". */
  hasSession: boolean;
  /** Optimistic JWT expiry; malformed/missing tokens count as expired. */
  accessTokenExpired: boolean;
}

export function resolveGuardAction({ pathname, hasSession, accessTokenExpired }: GuardInput): GuardAction {
  const isPublic = isPublicRoute(pathname);

  if (!hasSession) {
    return isPublic ? { kind: 'allow' } : { kind: 'redirect-login' };
  }

  if (AUTH_ENTRY_ROUTES.has(pathname)) {
    return { kind: 'redirect-dashboard' };
  }

  if (accessTokenExpired) {
    return { kind: 'refresh' };
  }

  return { kind: 'allow' };
}
