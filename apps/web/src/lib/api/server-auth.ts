import { backendUrl, BACKEND_TIMEOUT_MS } from './config';
import type { SessionTokens } from './session';

/**
 * Single shared refresh promise: concurrent 401s within this module graph
 * coalesce into one backend refresh call (refresh tokens rotate, so racing
 * refreshes would invalidate each other). proxy.ts and the API proxy route
 * are bundled separately and each get their own in-flight guard, which still
 * deduplicates the concurrent-401 storm within each surface.
 */
let inFlightRefresh: Promise<SessionTokens | null> | null = null;

export async function refreshSession(refreshToken: string | undefined): Promise<SessionTokens | null> {
  if (!refreshToken) return null;
  if (!inFlightRefresh) {
    inFlightRefresh = performRefresh(refreshToken).finally(() => {
      inFlightRefresh = null;
    });
  }
  return inFlightRefresh;
}

async function performRefresh(refreshToken: string): Promise<SessionTokens | null> {
  try {
    const response = await fetch(backendUrl('auth/refresh'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
      cache: 'no-store',
    });
    if (!response.ok) return null;
    const envelope = (await response.json()) as { success?: boolean; data?: SessionTokens };
    const tokens = envelope?.data;
    if (!envelope?.success || !tokens?.access_token || !tokens?.refresh_token) return null;
    return tokens;
  } catch {
    return null;
  }
}
