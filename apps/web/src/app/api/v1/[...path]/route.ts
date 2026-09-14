import { NextRequest, NextResponse } from 'next/server';
import { backendUrl, timeoutForContentType } from '@/lib/api/config';
import { refreshSession } from '@/lib/api/server-auth';
import {
  ACCESS_TOKEN_COOKIE,
  REFRESH_TOKEN_COOKIE,
  applySessionCookies,
  clearSessionCookies,
  getSessionCookieOptions,
  type SessionTokens,
} from '@/lib/api/session';

type RouteContext = { params: Promise<{ path: string[] }> };

const JSON_CONTENT_TYPE = 'application/json';

/** Endpoints whose request/response bodies must never be handled generically. */
const TOKEN_LOGIN_PATH = 'auth/login';
const TOKEN_REFRESH_PATH = 'auth/refresh';
const LOGOUT_PATH = 'auth/logout';
/** Endpoints where a 401 must never trigger the refresh-retry loop. */
const NO_RETRY_PATHS = new Set([TOKEN_LOGIN_PATH, TOKEN_REFRESH_PATH, LOGOUT_PATH, 'auth/register', 'auth/forgot-password']);

export async function GET(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context);
}
export async function POST(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context);
}
export async function PUT(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context);
}
export async function PATCH(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context);
}
export async function DELETE(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context);
}
export async function HEAD(request: NextRequest, context: RouteContext) {
  return handleProxy(request, context);
}

async function handleProxy(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  const { path: segments } = await context.params;
  const joined = segments.join('/');
  const search = new URL(request.url).search;

  const method = request.method.toUpperCase();
  if (/^users\/roles\/[^/]+\/permissions(?:\/[^/]+)?$/.test(joined) && (method === 'POST' || method === 'DELETE')) {
    return NextResponse.json({ success: false, error: { code: 'method_not_allowed', message: 'Permission changes are not supported.' } }, { status: 405, headers: { Allow: 'GET' } });
  }
  const hasRequestBody = method !== 'GET' && method !== 'HEAD';
  const rawBody = hasRequestBody ? await request.arrayBuffer() : null;
  const contentType = request.headers.get('content-type');

  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  const refreshToken = request.cookies.get(REFRESH_TOKEN_COOKIE)?.value;

  const isHttps =
    request.nextUrl.protocol === 'https:' ||
    request.headers.get('x-forwarded-proto') === 'https' ||
    Boolean(request.headers.get('host')?.includes('.e2b.app'));
  const cookieOptions = getSessionCookieOptions(isHttps);

  const makeBackendRequest = (
    token: string | null,
    body: ArrayBuffer | null,
    /**
     * Content type for `body`. Defaults to the caller's header for pass-through
     * bodies; synthesized bodies must declare their own, because the incoming
     * request may carry no body (and no Content-Type) at all.
     */
    bodyContentType: string | null = contentType,
  ): Promise<Response> =>
    fetch(backendUrl(joined, search), {
      method,
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(bodyContentType && body && body.byteLength > 0 ? { 'Content-Type': bodyContentType } : {}),
        Accept: 'application/json',
      },
      body: body && body.byteLength > 0 ? body : undefined,
      signal: AbortSignal.timeout(timeoutForContentType(bodyContentType)),
      cache: 'no-store',
    });

  try {
    // Logout: inject the HTTP-only refresh token, always end the local session.
    if (joined === LOGOUT_PATH) {
      const response = await makeBackendRequest(
        accessToken ?? null,
        encodeJson({ refresh_token: refreshToken ?? '' }),
        JSON_CONTENT_TYPE,
      );
      const payload = await readBody(response);
      return finalize(payload, response.status, (next) => clearSessionCookies(next, cookieOptions));
    }

    // Client-driven refresh: use the HTTP-only cookie, never a client-provided token.
    if (joined === TOKEN_REFRESH_PATH) {
      const response = await makeBackendRequest(
        null,
        encodeJson({ refresh_token: refreshToken ?? '' }),
        JSON_CONTENT_TYPE,
      );
      const payload = await readBody(response);
      if (response.ok) {
        const tokens = extractTokens(payload);
        if (tokens) {
          return finalize(sanitizeTokens(payload), response.status, (next) => applySessionCookies(next, tokens, cookieOptions));
        }
      }
      return finalize(payload, response.status, (next) => clearSessionCookies(next, cookieOptions));
    }

    let response = await makeBackendRequest(accessToken ?? null, rawBody);

    // Shared refresh on 401, then one retry with the rotated access token.
    if (response.status === 401 && !NO_RETRY_PATHS.has(joined) && refreshToken) {
      const tokens = await refreshSession(refreshToken);
      if (tokens) {
        response = await makeBackendRequest(tokens.access_token, rawBody);
        const payload = await readBody(response);
        return finalize(payload, response.status, (next) => applySessionCookies(next, tokens, cookieOptions));
      }
      const payload = await readBody(response);
      return finalize(payload, response.status, (next) => clearSessionCookies(next, cookieOptions));
    }

    const payload = await readBody(response);

    // Login: move tokens into HTTP-only cookies and strip them from the body.
    if (joined === TOKEN_LOGIN_PATH && response.ok) {
      const tokens = extractTokens(payload);
      if (tokens) {
        return finalize(sanitizeTokens(payload), response.status, (next) => applySessionCookies(next, tokens, cookieOptions));
      }
    }

    return finalize(payload, response.status);
  } catch {
    return finalize(
      { success: false, error: { code: 'network_error', message: 'ارتباط با سرور برقرار نشد.' } },
      502,
    );
  }
}

type JsonLike = Record<string, unknown> | undefined;

function encodeJson(value: unknown): ArrayBuffer {
  return new TextEncoder().encode(JSON.stringify(value)).buffer as ArrayBuffer;
}

async function readBody(response: Response): Promise<JsonLike> {
  const text = await response.text().catch(() => '');
  if (!text) return undefined;
  try {
    return JSON.parse(text) as JsonLike;
  } catch {
    return undefined;
  }
}

function extractTokens(payload: JsonLike): SessionTokens | null {
  const data = payload?.data as Partial<SessionTokens> | undefined;
  if (typeof data?.access_token === 'string' && typeof data?.refresh_token === 'string') {
    return {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      ...(typeof data.refresh_token_jti === 'string' ? { refresh_token_jti: data.refresh_token_jti } : {}),
    };
  }
  return null;
}

/** Removes token fields from an envelope so nothing secret reaches the browser. */
function sanitizeTokens(payload: JsonLike): JsonLike {
  if (!payload || typeof payload !== 'object') return payload;
  const clone = structuredClone(payload) as { data?: Record<string, unknown> };
  if (clone.data && typeof clone.data === 'object') {
    delete clone.data.access_token;
    delete clone.data.refresh_token;
    delete clone.data.refresh_token_jti;
  }
  return clone;
}

function finalize(payload: JsonLike, status: number, mutate?: (response: NextResponse) => void): NextResponse {
  const response = NextResponse.json(payload ?? { success: false, error: { code: 'empty_response', message: 'پاسخی از سرور دریافت نشد.' } }, {
    status,
    headers: { 'Cache-Control': 'no-store' },
  });
  mutate?.(response);
  return response;
}
