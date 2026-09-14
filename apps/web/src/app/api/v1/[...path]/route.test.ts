import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { POST } from './route';

/**
 * The proxy injects the HTTP-only refresh token into synthesized JSON bodies
 * for auth/refresh and auth/logout. Clients call those endpoints with no body
 * at all (the token lives in a cookie), so the proxy must declare
 * Content-Type itself — forwarding the caller's absent header made the backend
 * read the body as a string and reject it with 422, destroying the session.
 */

const backendFetch = vi.fn();

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function bodylessRequest(path: string): NextRequest {
  const request = new NextRequest(`http://localhost:3000/api/v1/${path}`, { method: 'POST' });
  request.cookies.set('didar_at', 'access-token');
  request.cookies.set('didar_rt', 'refresh-token');
  return request;
}

function context(path: string) {
  return { params: Promise.resolve({ path: path.split('/') }) };
}

/** The Content-Type and parsed body the proxy actually sent to the backend. */
function sentRequest(): { contentType: string | undefined; body: unknown } {
  const [, init] = backendFetch.mock.calls[0] as [string, RequestInit];
  const headers = init.headers as Record<string, string>;
  return {
    contentType: headers['Content-Type'],
    body: JSON.parse(new TextDecoder().decode(init.body as ArrayBuffer)),
  };
}

beforeEach(() => {
  backendFetch.mockReset();
  vi.stubGlobal('fetch', backendFetch);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('auth/refresh proxy', () => {
  it('declares application/json for its synthesized body when the caller sends none', async () => {
    backendFetch.mockResolvedValue(
      jsonResponse({ success: true, data: { access_token: 'new-at', refresh_token: 'new-rt' } }),
    );

    const response = await POST(bodylessRequest('auth/refresh'), context('auth/refresh'));

    expect(response.status).toBe(200);
    const sent = sentRequest();
    expect(sent.contentType).toBe('application/json');
    // The cookie token is used, never a client-supplied one.
    expect(sent.body).toEqual({ refresh_token: 'refresh-token' });
  });

  it('rotates cookies and strips tokens from the response body', async () => {
    backendFetch.mockResolvedValue(
      jsonResponse({ success: true, data: { access_token: 'new-at', refresh_token: 'new-rt' } }),
    );

    const response = await POST(bodylessRequest('auth/refresh'), context('auth/refresh'));

    expect(response.cookies.get('didar_at')?.value).toBe('new-at');
    expect(response.cookies.get('didar_rt')?.value).toBe('new-rt');
    const body = (await response.json()) as { data: Record<string, unknown> };
    expect(body.data).not.toHaveProperty('access_token');
    expect(body.data).not.toHaveProperty('refresh_token');
  });
});

describe('auth/logout proxy', () => {
  it('declares application/json for its synthesized body and clears the session', async () => {
    backendFetch.mockResolvedValue(jsonResponse({ success: true, data: {} }));

    const response = await POST(bodylessRequest('auth/logout'), context('auth/logout'));

    const sent = sentRequest();
    expect(sent.contentType).toBe('application/json');
    expect(sent.body).toEqual({ refresh_token: 'refresh-token' });
    expect(response.cookies.get('didar_at')?.value).toBe('');
    expect(response.cookies.get('didar_rt')?.value).toBe('');
  });
});
