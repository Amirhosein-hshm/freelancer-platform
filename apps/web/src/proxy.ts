import { NextResponse, type NextRequest } from 'next/server';
import { isPublicRoute, resolveGuardAction } from '@/lib/auth/guard';
import { refreshSession } from '@/lib/api/server-auth';
import {
  ACCESS_TOKEN_COOKIE,
  REFRESH_TOKEN_COOKIE,
  applySessionCookies,
  clearSessionCookies,
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
  const accessToken = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  const refreshToken = request.cookies.get(REFRESH_TOKEN_COOKIE)?.value;

  const action = resolveGuardAction({
    pathname,
    hasSession: Boolean(refreshToken),
    accessTokenExpired: isAccessTokenExpired(accessToken),
  });

  switch (action.kind) {
    case 'allow':
      return NextResponse.next();

    case 'redirect-login': {
      const loginUrl = new URL('/login', request.nextUrl);
      loginUrl.searchParams.set('expired', '1');
      const response = NextResponse.redirect(loginUrl);
      clearSessionCookies(response);
      return response;
    }

    case 'redirect-dashboard':
      return NextResponse.redirect(new URL('/dashboard', request.nextUrl));

    case 'refresh': {
      const tokens = await refreshSession(refreshToken);
      if (tokens) {
        const response = NextResponse.next();
        applySessionCookies(response, tokens);
        return response;
      }
      if (isPublicRoute(pathname)) {
        const response = NextResponse.next();
        clearSessionCookies(response);
        return response;
      }
      const loginUrl = new URL('/login', request.nextUrl);
      loginUrl.searchParams.set('expired', '1');
      const response = NextResponse.redirect(loginUrl);
      clearSessionCookies(response);
      return response;
    }
  }
}

export const config = {
  matcher: '/((?!api|_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|.*\\.(?:png|jpg|jpeg|gif|svg|ico|webp|txt|xml|css|js|map)$).*)',
};
