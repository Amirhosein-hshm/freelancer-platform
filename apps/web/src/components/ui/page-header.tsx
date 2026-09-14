import Link from 'next/link';
import { ChevronLeft } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PageHeaderProps {
  title: string;
  description?: ReactNode;
  /** Primary actions, aligned to the inline end on wide screens. */
  actions?: ReactNode;
  /** Renders a back link above the title. */
  backHref?: string;
  backLabel?: string;
  /** Rendered between the back link and the title — badges, codes, meta. */
  eyebrow?: ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  description,
  actions,
  backHref,
  backLabel = 'بازگشت',
  eyebrow,
  className,
}: PageHeaderProps) {
  return (
    <header className={cn('grid gap-3', className)}>
      {backHref ? (
        <Link
          href={backHref}
          className="inline-flex w-fit items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          {/* Chevron points toward the start of the line, which flips under RTL. */}
          <ChevronLeft size={16} className="rtl:rotate-180" aria-hidden="true" />
          {backLabel}
        </Link>
      ) : null}

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="grid min-w-0 gap-2">
          {eyebrow ? <div className="flex flex-wrap items-center gap-2">{eyebrow}</div> : null}
          <h1 className="text-xl font-bold text-balance sm:text-2xl">{title}</h1>
          {description ? (
            <p className="max-w-2xl text-sm leading-6 text-muted-foreground">{description}</p>
          ) : null}
        </div>
        {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
      </div>
    </header>
  );
}
