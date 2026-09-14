import Link from 'next/link';
import { Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import type { UserMeResponse } from '@/generated/api/models';
import { MobileNav } from './mobile-nav';
import { SidebarNav } from './sidebar-nav';
import { UserMenu } from './user-menu';
import { ThemeToggle } from '@/components/theme-toggle';

export function AppShell({ user, children }: { user: UserMeResponse; children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <div className="mx-auto flex w-full max-w-[1440px]">
        <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-e border-border bg-card px-4 py-6 lg:flex">
          <Link href="/dashboard" className="mb-8 flex items-center gap-2.5 px-2">
            <span className="grid size-9 place-items-center rounded-lg bg-primary text-primary-foreground">
              <Sparkles size={18} />
            </span>
            <span className="text-lg font-extrabold">دیدار</span>
          </Link>
          <SidebarNav user={user} />
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 flex min-h-16 items-center justify-between gap-3 border-b border-border bg-background/90 px-4 backdrop-blur sm:px-6">
            <Link href="/dashboard" className="flex items-center gap-2 lg:hidden">
              <span className="grid size-8 place-items-center rounded-lg bg-primary text-primary-foreground">
                <Sparkles size={15} />
              </span>
              <span className="font-extrabold">دیدار</span>
            </Link>
            <div className="flex items-center gap-1.5 ms-auto">
              <ThemeToggle />
              <UserMenu user={user} />
            </div>
          </header>

          <main id="main" className="flex-1 px-4 pt-6 pb-24 sm:px-6 lg:pb-10">
            {children}
          </main>
        </div>
      </div>

      <MobileNav user={user} />
    </div>
  );
}
