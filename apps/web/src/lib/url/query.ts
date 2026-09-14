/**
 * URL-owned list state. Search, filters, tabs, sorting, and pagination live in
 * the query string — never in React state — so lists are shareable,
 * back/forward works, and Server Components can read the same values.
 *
 * This module is pure so it can be tested without Next; `use-list-query.ts`
 * wraps it for Client Components.
 */

export const PAGE_PARAM = 'page';
export const PAGE_SIZE_PARAM = 'page_size';

/** Changing these does not reset pagination; changing anything else does. */
const PAGINATION_PARAMS = new Set<string>([PAGE_PARAM, PAGE_SIZE_PARAM]);

/** Next's `searchParams` prop shape for Server Components. */
export type RouteSearchParams = Record<string, string | string[] | undefined>;

export type QueryValue = string | number | boolean | null | undefined;
export type QueryPatch = Record<string, QueryValue>;

export function toSearchParams(input: RouteSearchParams | URLSearchParams | string): URLSearchParams {
  if (input instanceof URLSearchParams) return new URLSearchParams(input);
  if (typeof input === 'string') return new URLSearchParams(input);

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(input)) {
    if (value === undefined) continue;
    // Repeated params (?role=a&role=b) arrive as arrays; keep every value.
    for (const entry of Array.isArray(value) ? value : [value]) {
      params.append(key, entry);
    }
  }
  return params;
}

/** First value for a key, ignoring empty strings. */
export function getParam(
  input: RouteSearchParams | URLSearchParams | string,
  key: string,
): string | undefined {
  const value = toSearchParams(input).get(key);
  return value !== null && value.trim() !== '' ? value : undefined;
}

/**
 * Applies a patch to the current query string.
 *
 * - `null`, `undefined`, `false`, and `''` remove the key.
 * - Changing any non-pagination param resets `page`, because a filtered result
 *   set is shorter: staying on page 7 of the old set shows an empty list.
 * - Keys are sorted so the same state always produces the same URL.
 */
export function applyQueryPatch(
  current: RouteSearchParams | URLSearchParams | string,
  patch: QueryPatch,
): URLSearchParams {
  const params = toSearchParams(current);
  let resetPage = false;

  for (const [key, value] of Object.entries(patch)) {
    const next = normalizeValue(value);
    const previous = params.get(key);

    if (next === null) {
      params.delete(key);
    } else {
      params.set(key, next);
    }

    if (!PAGINATION_PARAMS.has(key) && (previous ?? null) !== next) {
      resetPage = true;
    }
  }

  // An explicit page in the same patch wins over the automatic reset.
  if (resetPage && !(PAGE_PARAM in patch)) {
    params.delete(PAGE_PARAM);
  }

  return sortParams(params);
}

function normalizeValue(value: QueryValue): string | null {
  if (value === null || value === undefined || value === false) return null;
  if (value === true) return 'true';
  const text = String(value);
  return text.trim() === '' ? null : text;
}

function sortParams(params: URLSearchParams): URLSearchParams {
  const sorted = new URLSearchParams();
  for (const key of [...new Set([...params.keys()])].sort()) {
    for (const value of params.getAll(key)) {
      sorted.append(key, value);
    }
  }
  return sorted;
}

/** `?a=1&b=2` (or '' when empty), ready to append to a pathname. */
export function toQueryString(params: URLSearchParams): string {
  const query = params.toString();
  return query === '' ? '' : `?${query}`;
}

export function buildHref(pathname: string, params: URLSearchParams): string {
  return `${pathname}${toQueryString(params)}`;
}
