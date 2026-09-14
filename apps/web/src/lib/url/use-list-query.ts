'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useCallback, useMemo, useTransition } from 'react';
import { clampPage, clampPageSize, type PageQuery } from '@/lib/api/pagination';
import {
  PAGE_PARAM,
  PAGE_SIZE_PARAM,
  applyQueryPatch,
  buildHref,
  type QueryPatch,
} from './query';

export interface ListQuery {
  /** Current query string state. */
  params: URLSearchParams;
  /** Clamped pagination values, safe to send straight to the backend. */
  pageQuery: PageQuery;
  page: number;
  pageSize: number;
  /** Reads a filter, treating blank values as absent. */
  get: (key: string) => string | undefined;
  /** Merges a patch into the URL; any filter change resets the page. */
  setQuery: (patch: QueryPatch) => void;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  /** Builds a href for the patched state — use for <Link>-based controls. */
  hrefFor: (patch: QueryPatch) => string;
  /** True while the navigation triggered by setQuery is in flight. */
  isPending: boolean;
}

/**
 * Reads and writes list state (search, filters, tabs, sort, pagination) in the
 * URL. Navigation uses `replace` inside a transition so filtering does not fill
 * the back stack with every keystroke and the outgoing list stays visible
 * instead of collapsing to a spinner.
 *
 * Must be rendered inside a Suspense boundary on statically rendered routes,
 * because it reads `useSearchParams`.
 */
export function useListQuery(): ListQuery {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  // useSearchParams returns a read-only instance; copy before handing it out.
  const params = useMemo(() => new URLSearchParams(searchParams.toString()), [searchParams]);

  const page = clampPage(params.get(PAGE_PARAM) ?? undefined);
  const pageSize = clampPageSize(params.get(PAGE_SIZE_PARAM) ?? undefined);

  const get = useCallback(
    (key: string): string | undefined => {
      const value = params.get(key);
      return value !== null && value.trim() !== '' ? value : undefined;
    },
    [params],
  );

  const hrefFor = useCallback(
    (patch: QueryPatch): string => buildHref(pathname, applyQueryPatch(params, patch)),
    [params, pathname],
  );

  const setQuery = useCallback(
    (patch: QueryPatch): void => {
      const href = buildHref(pathname, applyQueryPatch(params, patch));
      startTransition(() => {
        router.replace(href, { scroll: false });
      });
    },
    [params, pathname, router],
  );

  const setPage = useCallback((next: number) => setQuery({ [PAGE_PARAM]: next }), [setQuery]);
  const setPageSize = useCallback(
    (next: number) => setQuery({ [PAGE_SIZE_PARAM]: next, [PAGE_PARAM]: null }),
    [setQuery],
  );

  return {
    params,
    pageQuery: { page, page_size: pageSize },
    page,
    pageSize,
    get,
    setQuery,
    setPage,
    setPageSize,
    hrefFor,
    isPending,
  };
}
