'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { UserMeResponse } from '@/generated/api/models';
import { getNavItems } from '@/lib/auth/navigation';
import { cn } from '@/lib/utils';

const MAX_ITEMS = 5;

export function MobileNav({ user }: { user: UserMeResponse }) {
  const pathname = usePathname();
  const items = getNavItems(user).slice(0, MAX_ITEMS);

  return (
    <nav
      aria-label="ناوبری موبایل"
      className="fixed inset-x-0 bottom-0 z-40 grid auto-cols-fr grid-flow-col border-t border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/85 lg:hidden"
    >
      {items.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            aria-current={active ? 'page' : undefined}
            className={cn(
              'flex min-h-14 flex-col items-center justify-center gap-1 px-1 py-2 text-[11px] font-medium text-muted-foreground transition-colors',
              active && 'text-primary',
            )}
          >
            <Icon size={19} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
