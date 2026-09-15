import { ApiError, NETWORK_ERROR_MESSAGE, parseErrorBody } from './errors';

/**
 * Client-side fetcher for the generated orval client. Requests use relative
 * URLs so they hit the same-origin API proxy (/api/v1/*), which attaches the
 * server-managed access token, rotates session cookies, and normalizes
 * backend errors. On success, orval's fetch-client response shape is
 * `{ data, status, headers }`; failures throw ApiError.
 */
export async function customFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  if (typeof window !== 'undefined' && !headers.has('Authorization')) {
    try {
      const token = localStorage.getItem('didar_at');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    } catch {}
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
      credentials: 'same-origin',
    });
  } catch {
    throw new ApiError(0, 'network_error', NETWORK_ERROR_MESSAGE);
  }

  const body = (await response.json().catch(() => undefined)) as unknown;

  if (!response.ok) {
    const parsed = parseErrorBody(body);
    throw new ApiError(response.status, parsed.code, parsed.message, parsed.fields);
  }

  return {
    data: body,
    status: response.status,
    headers: response.headers,
  } as T;
}
