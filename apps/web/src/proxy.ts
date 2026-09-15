import { NextResponse, type NextRequest } from 'next/server';
import { isPublicRoute, resolveGuardAction } from '@/lib/auth/guard';
import { refreshSession } from '@/lib/api/server-auth';
import {
  ACCESS_TOKEN_COOKIE,
  REFRESH_TOKEN_COOKIE,
  applySessionCookies,
  clearSessionCookies,
  getSessionCookieOptions,
  isAccessTokenExpired,
} from '@/lib/api/session';

/**
 * Optimistic auth boundary: keeps authenticated users out of auth pages and
 * unauthenticated users away from the app, and proactively rotates expired
 * access tokens so Server Components render with a valid token. Real
 * authorization always happens in the backend and the API proxy route.
 */
export default async function proxy(request: NextRequest): Promise<NextResponse> {
  const { pathname } = request.nextUrl;
  const queryAccessToken = request.nextUrl.searchParams.get('token') || request.nextUrl.searchParams.get('at');
  const queryRefreshToken = request.nextUrl.searchParams.get('rt');

  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value || queryAccessToken || undefined;
  const refreshToken = request.cookies.get(REFRESH_TOKEN_COOKIE)?.value || queryRefreshToken || queryAccessToken || undefined;

  const isHttps =
    request.nextUrl.protocol === 'https:' ||
    request.headers.get('x-forwarded-proto') === 'https' ||
    Boolean(request.headers.get('host')?.includes('.e2b.app'));
  const cookieOptions = getSessionCookieOptions(isHttps);

  const action = resolveGuardAction({
    pathname,
    hasSession: Boolean(refreshToken),
    accessTokenExpired: isAccessTokenExpired(accessToken),
  });

  switch (action.kind) {
    case 'allow': {
      const requestHeaders = new Headers(request.headers);
      if (accessToken) {
        requestHeaders.set('x-access-token', accessToken);
      }
      if (refreshToken) {
        requestHeaders.set('x-refresh-token', refreshToken);
      }
      const response = NextResponse.next({
        request: {
          headers: requestHeaders,
        },
      });
      if (queryAccessToken || queryRefreshToken) {
        applySessionCookies(
          response,
          {
            access_token: accessToken!,
            refresh_token: refreshToken || accessToken!,
          },
          cookieOptions,
        );
      }
      return response;
    }

    case 'redirect-login': {
      const loginUrl = new URL('/login', request.nextUrl);
      loginUrl.searchParams.set('expired', '1');
      const response = NextResponse.redirect(loginUrl);
      clearSessionCookies(response, cookieOptions);
      return response;
    }

    case 'redirect-dashboard': {
      const dashboardUrl = new URL('/dashboard', request.nextUrl);
      if (queryAccessToken) dashboardUrl.searchParams.set('token', queryAccessToken);
      if (queryRefreshToken) dashboardUrl.searchParams.set('rt', queryRefreshToken);
      const response = NextResponse.redirect(dashboardUrl);
      if (queryAccessToken || queryRefreshToken) {
        applySessionCookies(
          response,
          {
            access_token: accessToken!,
            refresh_token: refreshToken || accessToken!,
          },
          cookieOptions,
        );
      }
      return response;
    }

    case 'refresh': {
      const tokens = await refreshSession(refreshToken);
      if (tokens) {
        const requestHeaders = new Headers(request.headers);
        requestHeaders.set('x-access-token', tokens.access_token);
        requestHeaders.set('x-refresh-token', tokens.refresh_token);
        const response = NextResponse.next({
          request: {
            headers: requestHeaders,
          },
        });
        applySessionCookies(response, tokens, cookieOptions);
        return response;
      }
      if (isPublicRoute(pathname)) {
        const response = NextResponse.next();
        clearSessionCookies(response, cookieOptions);
        return response;
      }
      const loginUrl = new URL('/login', request.nextUrl);
      loginUrl.searchParams.set('expired', '1');
      const response = NextResponse.redirect(loginUrl);
      clearSessionCookies(response, cookieOptions);
      return response;
    }
  }
}

export const config = {
  matcher: '/((?!api|_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|.*\\.(?:png|jpg|jpeg|gif|svg|ico|webp|txt|xml|css|js|map)$).*)',
};
