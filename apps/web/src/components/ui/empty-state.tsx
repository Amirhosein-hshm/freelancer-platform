import type { LucideIcon } from 'lucide-react';
import { Inbox } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

/**
 * Empty state for lists and panels. Deliberately not an error: it explains the
 * absence and, where possible, offers the action that would fill it.
 */
export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'grid place-items-center gap-3 rounded-xl border border-dashed border-border px-6 py-12 text-center',
        className,
      )}
    >
      <span
        className="grid size-12 place-items-center rounded-full bg-muted text-muted-foreground"
        aria-hidden="true"
      >
        <Icon size={22} />
      </span>
      <div className="grid gap-1">
        <p className="font-semibold">{title}</p>
        {description ? (
          <p className="mx-auto max-w-sm text-sm leading-6 text-muted-foreground">{description}</p>
        ) : null}
      </div>
      {action ? <div className="mt-1">{action}</div> : null}
    </div>
  );
}
