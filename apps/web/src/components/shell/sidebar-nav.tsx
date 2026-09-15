'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { ChevronDown } from 'lucide-react';
import { useState } from 'react';
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

  // Keep admin menu open by default if currently on an admin page
  const [adminOpen, setAdminOpen] = useState(() => pathname.startsWith('/admin'));

  return (
    <nav aria-label="ناوبری اصلی" className="grid gap-1.5 px-3">
      {items.map((item) => {
        const Icon = item.icon;
        const hasChildren = Boolean(item.children && item.children.length > 0);

        if (hasChildren) {
          const isChildActive = Boolean(item.children?.some((child) => pathname === child.href || pathname.startsWith(`${child.href}/`)));

          return (
            <div key={item.href} className="grid gap-1">
              <button
                type="button"
                onClick={() => setAdminOpen((prev) => !prev)}
                className={cn(
                  'flex min-h-11 w-full items-center justify-between rounded-xl px-3.5 text-sm font-medium transition-all duration-150',
                  isChildActive
                    ? 'bg-[#e66042]/10 font-bold text-[#e66042]'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )}
                aria-expanded={adminOpen}
              >
                <div className="flex items-center gap-3">
                  <span className={cn(
                    'grid size-8 place-items-center rounded-lg transition-colors',
                    isChildActive ? 'bg-[#e66042] text-white' : 'bg-muted text-muted-foreground',
                  )}>
                    <Icon size={17} />
                  </span>
                  <span>{item.label}</span>
                </div>
                <ChevronDown
                  size={16}
                  className={cn(
                    'text-muted-foreground transition-transform duration-200',
                    adminOpen && 'rotate-180 text-foreground',
                  )}
                />
              </button>

              {adminOpen ? (
                <div className="relative me-4 ms-5 mt-1 grid gap-1 border-r-2 border-border/80 pe-1 ps-3.5">
                  {item.children?.map((child) => {
                    const active = pathname === child.href || pathname.startsWith(`${child.href}/`);
                    const childHref = `${child.href}${tokenQuery}`;
                    return (
                      <Link
                        key={child.href}
                        href={childHref}
                        aria-current={active ? 'page' : undefined}
                        className={cn(
                          'relative flex min-h-9 items-center gap-2 rounded-lg px-3 text-xs font-medium transition-all duration-150',
                          active
                            ? 'bg-[#e66042]/10 font-bold text-[#e66042]'
                            : 'text-muted-foreground hover:bg-muted/80 hover:text-foreground',
                        )}
                      >
                        <span
                          className={cn(
                            'size-1.5 rounded-full transition-colors',
                            active ? 'bg-[#e66042]' : 'bg-muted-foreground/40',
                          )}
                        />
                        <span>{child.label}</span>
                      </Link>
                    );
                  })}
                </div>
              ) : null}
            </div>
          );
        }

        const active = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(`${item.href}/`));
        const href = `${item.href}${tokenQuery}`;

        return (
          <Link
            key={item.href}
            href={href}
            aria-current={active ? 'page' : undefined}
            className={cn(
              'group flex min-h-11 items-center gap-3 rounded-xl px-3.5 text-sm font-medium transition-all duration-150',
              active
                ? 'bg-[#e66042]/10 font-bold text-[#e66042]'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground',
            )}
          >
            <span
              className={cn(
                'grid size-8 place-items-center rounded-lg transition-colors',
                active
                  ? 'bg-[#e66042] text-white shadow-xs'
                  : 'bg-muted text-muted-foreground group-hover:bg-muted/80 group-hover:text-foreground',
              )}
            >
              <Icon size={17} />
            </span>
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
