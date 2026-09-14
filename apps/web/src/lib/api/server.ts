import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import type { PaginationMeta, UserMeResponse } from '@/generated/api/models';
import { backendUrl, BACKEND_TIMEOUT_MS } from './config';
import { ApiError, NETWORK_ERROR_MESSAGE, parseErrorBody } from './errors';
import { ACCESS_TOKEN_COOKIE } from './session';

/**
 * Authenticated reads for Server Components.
 *
 * proxy.ts refreshes rotated tokens before the render, so a 401 here means the
 * session genuinely ended — every helper redirects to login rather than
 * rendering a broken page. Anything else throws ApiError, which the route-group
 * `error.tsx` turns into an ErrorState.
 *
 * Writes never come through here: mutations run in the browser against the
 * same-origin proxy so cookie rotation happens in one place.
 */

export interface ServerPage<T> {
  items: T[];
  meta: Partial<PaginationMeta> | undefined;
}

type QueryValue = string | number | boolean | null | undefined;

/** Reads one resource and unwraps the success envelope's `data`. */
export async function serverGet<T>(
  path: string,
  params?: Record<string, QueryValue>,
): Promise<T> {
  const envelope = await requestEnvelope<T>(path, params);
  if (envelope.data === undefined || envelope.data === null) {
    throw new ApiError(502, 'invalid_response', INVALID_RESPONSE_MESSAGE);
  }
  return envelope.data;
}

/**
 * Reads a paginated list. `data` is the array and `meta` carries pagination;
 * a missing array is normalized to empty so list pages render their empty state
 * instead of throwing.
 */
export async function serverGetPage<T>(
  path: string,
  params?: Record<string, QueryValue>,
): Promise<ServerPage<T>> {
  const envelope = await requestEnvelope<T[]>(path, params);
  return {
    items: Array.isArray(envelope.data) ? envelope.data : [],
    meta: envelope.meta,
  };
}

/**
 * Like `serverGet`, but returns null on 404 and 403 instead of throwing. For
 * resources that legitimately may not exist yet or may not be visible to this
 * user — an unrated project, a review that was never submitted — where the
 * absence is part of the page rather than a failure of it.
 */
export async function serverGetOptional<T>(
  path: string,
  params?: Record<string, QueryValue>,
): Promise<T | null> {
  try {
    return await serverGet<T>(path, params);
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 403)) {
      return null;
    }
    throw error;
  }
}

/** The current session user. */
export async function getServerSessionUser(): Promise<UserMeResponse> {
  return serverGet<UserMeResponse>('auth/me');
}

const INVALID_RESPONSE_MESSAGE = 'پاسخ نامعتبری از سرور دریافت شد.';
const REQUEST_FAILED_MESSAGE = 'دریافت اطلاعات با خطا مواجه شد.';

interface Envelope<T> {
  success?: boolean;
  data?: T;
  meta?: Partial<PaginationMeta>;
}

async function requestEnvelope<T>(
  path: string,
  params?: Record<string, QueryValue>,
): Promise<Envelope<T>> {
  const jar = await cookies();
  const accessToken = jar.get(ACCESS_TOKEN_COOKIE)?.value;
  if (!accessToken) {
    redirect('/login?expired=1');
  }

  let response: Response;
  try {
    response = await fetch(backendUrl(path, buildSearch(params)), {
      headers: { Authorization: `Bearer ${accessToken}` },
      cache: 'no-store',
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
    });
  } catch {
    throw new ApiError(503, 'network_error', NETWORK_ERROR_MESSAGE);
  }

  if (response.status === 401) {
    redirect('/login?expired=1');
  }

  const body = (await response.json().catch(() => undefined)) as unknown;

  if (!response.ok) {
    const parsed = parseErrorBody(body);
    throw new ApiError(
      response.status,
      parsed.code,
      // parseErrorBody falls back to the network message when the body is not
      // an error envelope; a read that failed for another reason says so.
      parsed.code === 'unknown_error' ? REQUEST_FAILED_MESSAGE : parsed.message,
      parsed.fields,
    );
  }

  const envelope = body as Envelope<T> | undefined;
  if (envelope?.success !== true) {
    throw new ApiError(502, 'invalid_response', INVALID_RESPONSE_MESSAGE);
  }
  return envelope;
}

/** Skips absent values so the backend applies its own defaults. */
export function buildSearch(params?: Record<string, QueryValue>): string {
  if (!params) return '';
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue;
    search.append(key, String(value));
  }
  const query = search.toString();
  return query === '' ? '' : `?${query}`;
}
