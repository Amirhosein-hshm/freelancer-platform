import { describe, expect, it } from 'vitest';
import { resolveGuardAction, isPublicRoute } from './guard';

describe('isPublicRoute', () => {
  it('allows the landing and auth pages', () => {
    expect(isPublicRoute('/')).toBe(true);
    expect(isPublicRoute('/login')).toBe(true);
    expect(isPublicRoute('/register')).toBe(true);
    expect(isPublicRoute('/forgot-password')).toBe(true);
  });

  it('protects app routes', () => {
    expect(isPublicRoute('/dashboard')).toBe(false);
    expect(isPublicRoute('/projects')).toBe(false);
    expect(isPublicRoute('/admin/users')).toBe(false);
  });
});

describe('resolveGuardAction', () => {
  it('lets anonymous users browse public routes', () => {
    expect(resolveGuardAction({ pathname: '/', hasSession: false, accessTokenExpired: true })).toEqual({ kind: 'allow' });
    expect(resolveGuardAction({ pathname: '/login', hasSession: false, accessTokenExpired: true })).toEqual({ kind: 'allow' });
  });

  it('sends anonymous users on protected routes to login', () => {
    expect(
      resolveGuardAction({ pathname: '/dashboard', hasSession: false, accessTokenExpired: true }),
    ).toEqual({ kind: 'redirect-login' });
  });

  it('keeps authenticated users away from auth entry pages', () => {
    expect(
      resolveGuardAction({ pathname: '/login', hasSession: true, accessTokenExpired: false }),
    ).toEqual({ kind: 'redirect-dashboard' });
    expect(
      resolveGuardAction({ pathname: '/register', hasSession: true, accessTokenExpired: true }),
    ).toEqual({ kind: 'redirect-dashboard' });
  });

  it('lets authenticated users continue on protected routes with a fresh token', () => {
    expect(
      resolveGuardAction({ pathname: '/dashboard', hasSession: true, accessTokenExpired: false }),
    ).toEqual({ kind: 'allow' });
  });

  it('requests a refresh when the access token is expired but a session exists', () => {
    expect(
      resolveGuardAction({ pathname: '/dashboard', hasSession: true, accessTokenExpired: true }),
    ).toEqual({ kind: 'refresh' });
  });
});
