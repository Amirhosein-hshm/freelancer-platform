'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { cn } from '@/lib/utils';
import { getNavItems } from '@/lib/auth/navigation';
import type { UserMeResponse } from '@/generated/api/models';

export function SidebarNav({ user }: { user: UserMeResponse }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  const rt = searchParams.get('rt');
  const tokenQuery = token ? `?token=${encodeURIComponent(token)}${rt ? `&rt=${encodeURIComponent(rt)}` : ''}` : '';
  const items = getNavItems(user);

  return (
    <nav aria-label="ناوبری اصلی" className="grid gap-1">
      {items.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = item.icon;
        const href = `${item.href}${tokenQuery}`;
        return (
          <Link
            key={item.href}
            href={href}
            aria-current={active ? 'page' : undefined}
            className={cn(
              'flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none',
              active && 'bg-primary/10 text-primary',
            )}
          >
            <Icon size={18} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
