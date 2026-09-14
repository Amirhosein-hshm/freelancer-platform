'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import type { PaginationMeta } from '@/generated/api/models';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  PAGE_SIZE_OPTIONS,
  getItemRange,
  getPageTokens,
  hasNextPage,
  hasPreviousPage,
} from '@/lib/api/pagination';
import { formatNumber } from '@/lib/format';
import { PAGE_PARAM } from '@/lib/url/query';
import type { ListQuery } from '@/lib/url/use-list-query';
import { cn } from '@/lib/utils';

/**
 * URL-driven pagination for list routes.
 *
 * Page changes are real `<Link>`s rather than `router.replace`, so they get
 * prefetching, middle-click, and a back button that returns to the previous
 * page of results. Filter changes stay on `replace` (see `useListQuery`) — those
 * should not each become a history entry.
 *
 * Chevrons are rotated under `rtl:` instead of being swapped, so the control
 * still points the right way if it is ever rendered inside an LTR subtree.
 */
export function PaginationBar({
  meta,
  query,
  showPageSize = true,
  itemNoun = 'مورد',
  className,
}: {
  meta: PaginationMeta;
  query: ListQuery;
  showPageSize?: boolean;
  /** Counted noun for the range footer, e.g. «پروژه» or «تیکت». */
  itemNoun?: string;
  className?: string;
}) {
  const range = getItemRange(meta);
  const tokens = getPageTokens(meta);
  const canGoBack = hasPreviousPage(meta);
  const canGoForward = hasNextPage(meta);

  // Nothing to paginate and nothing to summarise.
  if (meta.total_items === 0) return null;

  return (
    <nav
      aria-label="صفحه‌بندی"
      className={cn(
        'flex flex-wrap items-center justify-between gap-x-4 gap-y-3 border-t border-border pt-4',
        query.isPending && 'opacity-70 transition-opacity',
        className,
      )}
    >
      <p aria-live="polite" className="text-sm text-muted-foreground">
        {range
          ? `نمایش ${formatNumber(range.from)} تا ${formatNumber(range.to)} از ${formatNumber(meta.total_items)} ${itemNoun}`
          : `${formatNumber(meta.total_items)} ${itemNoun}`}
      </p>

      <div className="flex flex-wrap items-center gap-2">
        {showPageSize ? (
          // Not a <label>: the Radix trigger is a <button>, which labels do not
          // associate with. The visible text is decorative; aria-label carries it.
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span aria-hidden="true" className="whitespace-nowrap">
              تعداد در صفحه
            </span>
            <Select
              value={String(meta.page_size)}
              onValueChange={(value) => query.setPageSize(Number(value))}
            >
              <SelectTrigger size="sm" className="w-[4.5rem]" aria-label="تعداد در صفحه">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <SelectItem key={size} value={String(size)}>
                    {formatNumber(size)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        ) : null}

        {meta.total_pages > 1 ? (
          <ul className="flex items-center gap-1">
            <li>
              <PageArrow
                direction="previous"
                href={query.hrefFor({ [PAGE_PARAM]: meta.page - 1 })}
                disabled={!canGoBack}
              />
            </li>

            {tokens.map((token, index) =>
              token === 'ellipsis' ? (
                <li
                  // Tokens are positional; two ellipses can share a render.
                  key={`ellipsis-${index}`}
                  aria-hidden="true"
                  className="grid size-10 place-items-center text-sm text-muted-foreground"
                >
                  …
                </li>
              ) : (
                <li key={token}>
                  <PageLink
                    page={token}
                    href={query.hrefFor({ [PAGE_PARAM]: token })}
                    isCurrent={token === meta.page}
                  />
                </li>
              ),
            )}

            <li>
              <PageArrow
                direction="next"
                href={query.hrefFor({ [PAGE_PARAM]: meta.page + 1 })}
                disabled={!canGoForward}
              />
            </li>
          </ul>
        ) : null}
      </div>
    </nav>
  );
}

function PageLink({
  page,
  href,
  isCurrent,
}: {
  page: number;
  href: string;
  isCurrent: boolean;
}) {
  return (
    <Button
      asChild
      variant={isCurrent ? 'default' : 'ghost'}
      size="icon"
      className="size-10 tabular-nums"
    >
      <Link
        href={href}
        // `aria-current` is what screen readers announce; the visual variant
        // alone would leave the current page ambiguous.
        aria-current={isCurrent ? 'page' : undefined}
        aria-label={`صفحه ${formatNumber(page)}`}
      >
        {formatNumber(page)}
      </Link>
    </Button>
  );
}

function PageArrow({
  direction,
  href,
  disabled,
}: {
  direction: 'previous' | 'next';
  href: string;
  disabled: boolean;
}) {
  const label = direction === 'previous' ? 'صفحه قبل' : 'صفحه بعد';
  const Icon = direction === 'previous' ? ChevronLeft : ChevronRight;
  const icon = <Icon size={18} className="rtl:rotate-180" aria-hidden="true" />;

  // A dead end is a disabled control, not a link that goes nowhere.
  if (disabled) {
    return (
      <Button variant="ghost" size="icon" className="size-10" disabled aria-label={label}>
        {icon}
      </Button>
    );
  }

  return (
    <Button asChild variant="ghost" size="icon" className="size-10">
      <Link href={href} aria-label={label} rel={direction === 'next' ? 'next' : 'prev'}>
        {icon}
      </Link>
    </Button>
  );
}
