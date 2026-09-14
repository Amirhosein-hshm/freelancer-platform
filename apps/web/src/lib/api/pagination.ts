import type { PaginationMeta } from '@/generated/api/models';

/**
 * Pagination helpers built on the backend's envelope `meta` shape
 * ({ page, page_size, total_items, total_pages }). The backend enforces the
 * real bounds; these helpers keep the UI from *sending* out-of-range values and
 * from rendering nonsense when a response is partial.
 */

export const DEFAULT_PAGE = 1;
export const DEFAULT_PAGE_SIZE = 20;
/** Backend caps page_size at 100 (see the generated *Params types). */
export const MAX_PAGE_SIZE = 100;
export const MIN_PAGE_SIZE = 1;

export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100] as const;

export function clampPage(value: unknown): number {
  const page = toInteger(value);
  return page !== null && page >= 1 ? page : DEFAULT_PAGE;
}

export function clampPageSize(value: unknown): number {
  const size = toInteger(value);
  if (size === null) return DEFAULT_PAGE_SIZE;
  return Math.min(Math.max(size, MIN_PAGE_SIZE), MAX_PAGE_SIZE);
}

function toInteger(value: unknown): number | null {
  if (typeof value === 'number') return Number.isInteger(value) ? value : null;
  if (typeof value !== 'string' || value.trim() === '') return null;
  const parsed = Number(value);
  return Number.isInteger(parsed) ? parsed : null;
}

/**
 * A type alias, not an interface: TypeScript grants aliases an implicit index
 * signature, which lets a PageQuery be passed straight to helpers that take
 * `Record<string, …>` query params.
 */
export type PageQuery = {
  page: number;
  page_size: number;
};

/** Query params for a list request, always within the backend's bounds. */
export function toPageQuery(page: unknown, pageSize: unknown): PageQuery {
  return { page: clampPage(page), page_size: clampPageSize(pageSize) };
}

/**
 * Fills in a usable meta object when the backend omits `meta` or sends
 * unexpected values, so list footers never render NaN.
 */
export function normalizePaginationMeta(
  meta: Partial<PaginationMeta> | null | undefined,
  fallback: PageQuery,
  itemCount = 0,
): PaginationMeta {
  const page_size = clampPageSize(meta?.page_size ?? fallback.page_size);
  const page = clampPage(meta?.page ?? fallback.page);
  const total_items =
    typeof meta?.total_items === 'number' && meta.total_items >= 0
      ? meta.total_items
      : itemCount;
  const total_pages =
    typeof meta?.total_pages === 'number' && meta.total_pages >= 0
      ? meta.total_pages
      : Math.max(1, Math.ceil(total_items / page_size));

  return { page, page_size, total_items, total_pages };
}

export function hasPreviousPage(meta: PaginationMeta): boolean {
  return meta.page > 1;
}

export function hasNextPage(meta: PaginationMeta): boolean {
  return meta.page < meta.total_pages;
}

/**
 * 1-based inclusive range of the items on the current page, for
 * "نمایش ۱ تا ۲۰ از ۵۳" footers. Returns null when there is nothing to show.
 */
export function getItemRange(meta: PaginationMeta): { from: number; to: number } | null {
  if (meta.total_items <= 0) return null;
  const from = (meta.page - 1) * meta.page_size + 1;
  if (from > meta.total_items) return null;
  return { from, to: Math.min(from + meta.page_size - 1, meta.total_items) };
}

export type PageToken = number | 'ellipsis';

/**
 * Page tokens for a pagination control: first and last page always present,
 * `siblings` pages either side of the current one, gaps collapsed to a single
 * ellipsis. A gap of exactly one page is filled instead of elided so the
 * control never shows an ellipsis standing in for a single number.
 *
 * Below `5 + 2 * siblings` pages every page is listed — that is the widest the
 * control can get once both ellipses are in play, so showing them all costs no
 * extra slots and keeps the width from jumping as the user pages through.
 */
export function getPageTokens(meta: PaginationMeta, siblings = 1): PageToken[] {
  const total = Math.max(1, meta.total_pages);
  const current = Math.min(Math.max(meta.page, 1), total);

  const maxSlots = 5 + 2 * siblings;
  if (total <= maxSlots) {
    return Array.from({ length: total }, (_, index) => index + 1);
  }

  const pages = new Set<number>([1, total]);
  for (let offset = -siblings; offset <= siblings; offset += 1) {
    const page = current + offset;
    if (page >= 1 && page <= total) pages.add(page);
  }

  const sorted = [...pages].sort((a, b) => a - b);
  const tokens: PageToken[] = [];
  for (const [index, page] of sorted.entries()) {
    if (index > 0) {
      const gap = page - sorted[index - 1];
      if (gap === 2) {
        tokens.push(page - 1);
      } else if (gap > 2) {
        tokens.push('ellipsis');
      }
    }
    tokens.push(page);
  }
  return tokens;
}
