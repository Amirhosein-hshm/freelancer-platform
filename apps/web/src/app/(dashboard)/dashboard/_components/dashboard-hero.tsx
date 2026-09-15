import Link from 'next/link';
import { ArrowLeft, Plus, ShieldCheck, Sparkles, Ticket } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ROLE_LABELS, hasRole, ROLES } from '@/lib/auth/navigation';
import type { UserMeResponse } from '@/generated/api/models';

export function DashboardHero({ user }: { user: UserMeResponse }) {
  const isAdmin = hasRole(user, ROLES.admin);
  const isFreelancer = hasRole(user, ROLES.freelancer);
  const isSupervisor = hasRole(user, ROLES.supervisor);

  const displayName = user.email.split('@')[0] ?? 'کاربر';

  return (
    <section className="relative overflow-hidden rounded-2xl border border-border/80 bg-[#171916] p-6 text-[#f1eee7] shadow-xl sm:p-8 lg:p-10">
      {/* Decorative grid overlay matching the landing hero */}
      <div
        className="pointer-events-none absolute inset-0 opacity-15"
        style={{
          backgroundImage:
            'linear-gradient(rgba(241,238,231,0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(241,238,231,0.2) 1px, transparent 1px)',
          backgroundSize: '48px 48px',
          maskImage: 'linear-gradient(to bottom, black, transparent 95%)',
        }}
        aria-hidden="true"
      />

      <div className="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl">
          {/* Eyebrow marker matching landing */}
          <div className="flex items-center gap-2.5 text-xs font-bold tracking-wider text-[#e66042]">
            <span className="block h-[2px] w-6 bg-[#e66042]" />
            فضای کار و مدیریت دیدار
          </div>

          <h1 className="mt-3 text-2xl font-extrabold tracking-tight sm:text-3xl lg:text-4xl">
            خوش آمدید، <em className="not-italic text-[#e66042]">{displayName}</em> 👋
          </h1>

          <p className="mt-2 text-sm leading-relaxed text-[#f1eee7]/70 sm:text-base">
            از این بخش می‌توانید پروژه‌ها، ارتباطات، بازبینی‌ها و آمار همکاری‌های خود را در بستری شفاف و منظم مدیریت کنید.
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <span className="text-xs text-[#f1eee7]/60">نقش‌های شما:</span>
            {user.roles.map((role) => (
              <Badge
                key={role}
                variant="outline"
                className="border-[#f1eee7]/30 bg-[#f1eee7]/10 text-xs font-medium text-[#f1eee7]"
              >
                {ROLE_LABELS[role] ?? role}
              </Badge>
            ))}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap items-center gap-3">
          {isAdmin ? (
            <>
              <Button
                asChild
                size="lg"
                className="border-0 bg-[#e66042] px-5 text-white shadow-md hover:bg-[#ef7659]"
              >
                <Link href="/projects/new">
                  <Plus size={16} aria-hidden="true" />
                  ایجاد پروژه جدید
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="border-[#f1eee7]/30 bg-transparent text-[#f1eee7] hover:bg-[#f1eee7]/10 hover:text-white"
              >
                <Link href="/admin">
                  <ShieldCheck size={16} aria-hidden="true" />
                  مدیریت سامانه
                </Link>
              </Button>
            </>
          ) : isFreelancer ? (
            <>
              <Button
                asChild
                size="lg"
                className="border-0 bg-[#e66042] px-5 text-white shadow-md hover:bg-[#ef7659]"
              >
                <Link href="/projects/available">
                  <Sparkles size={16} aria-hidden="true" />
                  مشاهده پروژه‌ها
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="border-[#f1eee7]/30 bg-transparent text-[#f1eee7] hover:bg-[#f1eee7]/10 hover:text-white"
              >
                <Link href="/tickets/new">
                  <Ticket size={16} aria-hidden="true" />
                  تیکت پشتیبانی
                </Link>
              </Button>
            </>
          ) : isSupervisor ? (
            <>
              <Button
                asChild
                size="lg"
                className="border-0 bg-[#e66042] px-5 text-white shadow-md hover:bg-[#ef7659]"
              >
                <Link href="/reviews">
                  صف بازبینی پروژه‌ها
                  <ArrowLeft size={16} aria-hidden="true" />
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="border-[#f1eee7]/30 bg-transparent text-[#f1eee7] hover:bg-[#f1eee7]/10 hover:text-white"
              >
                <Link href="/tickets">
                  <Ticket size={16} aria-hidden="true" />
                  تیکت‌ها
                </Link>
              </Button>
            </>
          ) : (
            <>
              <Button
                asChild
                size="lg"
                className="border-0 bg-[#e66042] px-5 text-white shadow-md hover:bg-[#ef7659]"
              >
                <Link href="/projects/new">
                  <Plus size={16} aria-hidden="true" />
                  ثبت سفارش پروژه
                </Link>
              </Button>
              <Button
                asChild
                variant="outline"
                size="lg"
                className="border-[#f1eee7]/30 bg-transparent text-[#f1eee7] hover:bg-[#f1eee7]/10 hover:text-white"
              >
                <Link href="/tickets/new">
                  <Ticket size={16} aria-hidden="true" />
                  ارتباط با پشتیبانی
                </Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </section>
  );
}
