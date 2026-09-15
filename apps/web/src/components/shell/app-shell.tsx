import Link from 'next/link';
import { Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import type { UserMeResponse } from '@/generated/api/models';
import { MobileNav } from './mobile-nav';
import { SidebarNav } from './sidebar-nav';
import { UserMenu } from './user-menu';
import { ThemeToggle } from '@/components/theme-toggle';

export function AppShell({ user, children }: { user: UserMeResponse; children: ReactNode }) {
  const displayName = user.email.split('@')[0] ?? 'کاربر';

  return (
    <div className="flex min-h-screen w-full bg-background text-foreground antialiased">
      {/* Sidebar: Sticks firmly to the right edge in RTL without any parent max-width container */}
      <aside className="sticky top-0 hidden h-screen w-72 shrink-0 flex-col border-e border-border/80 bg-card/95 backdrop-blur-md lg:flex">
        {/* Brand header matching landing page */}
        <div className="flex h-20 items-center justify-between border-b border-border/70 px-6">
          <Link href="/dashboard" className="flex items-center gap-3">
            <span className="grid size-9 place-items-center rounded-full border border-current text-foreground transition-transform hover:scale-105">
              <Sparkles size={17} className="text-[#e66042]" />
            </span>
            <div className="flex flex-col">
              <span className="text-lg font-extrabold tracking-tight">
                دیدار<span className="text-[#e66042]">.</span>
              </span>
              <span className="text-[10px] font-medium text-muted-foreground">
                فضای کار پروژه‌های خلاق
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto py-5">
          <div className="mb-2 px-6 text-[11px] font-bold text-muted-foreground/70">
            ناوبری و میز کار
          </div>
          <SidebarNav user={user} />
        </div>

        {/* Sidebar footer with user status */}
        <div className="border-t border-border/70 p-4">
          <div className="flex items-center gap-3 rounded-xl bg-muted/40 p-2.5">
            <span className="grid size-8 place-items-center rounded-full bg-[#e66042]/10 font-mono text-xs font-bold text-[#e66042]">
              {displayName.slice(0, 2).toUpperCase()}
            </span>
            <div className="flex min-w-0 flex-1 flex-col">
              <span dir="ltr" className="truncate text-start text-xs font-semibold text-foreground">
                {user.email}
              </span>
              <span className="flex items-center gap-1.5 text-[10px] text-emerald-600 dark:text-emerald-400">
                <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
                نشست امن متصل
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main viewport */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top header */}
        <header className="sticky top-0 z-30 flex min-h-16 items-center justify-between gap-4 border-b border-border/70 bg-background/85 px-4 backdrop-blur-md sm:px-6 lg:px-8">
          <Link href="/dashboard" className="flex items-center gap-2.5 lg:hidden">
            <span className="grid size-8 place-items-center rounded-full border border-current text-foreground">
              <Sparkles size={15} className="text-[#e66042]" />
            </span>
            <span className="font-extrabold">دیدار</span>
          </Link>

          <div className="hidden items-center gap-2 text-xs text-muted-foreground md:flex">
            <span>فضای کار یکپارچه</span>
            <span>/</span>
            <span className="font-medium text-foreground">دیدار ۱۴۰۳</span>
          </div>

          <div className="ms-auto flex items-center gap-2.5">
            <ThemeToggle />
            <UserMenu user={user} />
          </div>
        </header>

        {/* Main content body */}
        <main id="main" className="flex-1 px-4 py-6 pb-24 sm:px-6 lg:px-8 lg:py-8 lg:pb-12">
          <div className="mx-auto w-full max-w-[1360px]">
            {children}
          </div>
        </main>
      </div>

      <MobileNav user={user} />
    </div>
  );
}
