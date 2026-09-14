/**
 * Server-side backend origin. The browser never talks to the backend directly;
 * all requests go through the same-origin proxy at /api/v1/*.
 */
export const API_BASE_URL = (process.env.API_BASE_URL ?? 'http://127.0.0.1:8000').replace(/\/+$/, '');

export const API_PREFIX = '/api/v1';

export function backendUrl(path: string, search = ''): string {
  return `${API_BASE_URL}${API_PREFIX}/${path}${search}`;
}

export const BACKEND_TIMEOUT_MS = 30_000;

/**
 * Multipart uploads get a longer budget. The proxy buffers the whole request
 * body before it starts the backend fetch, so this covers only the proxy→backend
 * hop — but that hop still has to move the entire file.
 */
export const BACKEND_UPLOAD_TIMEOUT_MS = 120_000;

export function timeoutForContentType(contentType: string | null): number {
  return contentType?.startsWith('multipart/form-data') === true
    ? BACKEND_UPLOAD_TIMEOUT_MS
    : BACKEND_TIMEOUT_MS;
}
