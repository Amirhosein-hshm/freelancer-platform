import Link from 'next/link';
import { ArrowUpLeft, CheckCircle2, FolderKanban, ShieldCheck, Ticket, Users } from 'lucide-react';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { DashboardStatisticsResponse, UserMeResponse } from '@/generated/api/models';

interface DashboardMetricsProps {
  user: UserMeResponse;
  stats?: DashboardStatisticsResponse | null;
  activeProjectsCount?: number;
  openTicketsCount?: number;
}

export function DashboardMetrics({
  user,
  stats,
  activeProjectsCount = 0,
  openTicketsCount = 0,
}: DashboardMetricsProps) {
  const isAdmin = hasRole(user, ROLES.admin);
  const isFreelancer = hasRole(user, ROLES.freelancer);

  return (
    <section aria-label="شاخص‌های عملکرد" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* Metric 1: Projects */}
      <Link
        href={isFreelancer ? '/projects/available' : '/projects'}
        className="group relative block rounded-xl border border-border bg-card p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-[#e66042]/50 hover:shadow-md"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-muted-foreground">پروژه‌ها</span>
          <span className="grid size-8 place-items-center rounded-lg bg-[#e66042]/10 text-[#e66042] transition-colors group-hover:bg-[#e66042] group-hover:text-white">
            <FolderKanban size={17} />
          </span>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="font-mono text-3xl font-extrabold text-foreground">
            {stats?.active_projects ?? activeProjectsCount}
          </span>
          <span className="text-xs text-muted-foreground">پروژه فعال</span>
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>{isFreelancer ? 'مشاهده پروژه‌های موجود' : 'مدیریت و پیگیری کارها'}</span>
          <ArrowUpLeft
            size={14}
            className="text-muted-foreground transition-transform group-hover:-translate-x-0.5 group-hover:text-[#e66042]"
          />
        </div>
      </Link>

      {/* Metric 2: Support & Tickets */}
      <Link
        href="/tickets"
        className="group relative block rounded-xl border border-border bg-card p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-[#e66042]/50 hover:shadow-md"
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-muted-foreground">پشتیبانی و پیام‌ها</span>
          <span className="grid size-8 place-items-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
            <Ticket size={17} />
          </span>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="font-mono text-3xl font-extrabold text-foreground">
            {openTicketsCount}
          </span>
          <span className="text-xs text-muted-foreground">تیکت ثبت‌شده</span>
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>ارتباط مستقیم با تیم</span>
          <ArrowUpLeft
            size={14}
            className="text-muted-foreground transition-transform group-hover:-translate-x-0.5 group-hover:text-primary"
          />
        </div>
      </Link>

      {/* Metric 3: User/Network context */}
      {isAdmin ? (
        <Link
          href="/admin/users"
          className="group relative block rounded-xl border border-border bg-card p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-[#e66042]/50 hover:shadow-md"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground">کاربران سامانه</span>
            <span className="grid size-8 place-items-center rounded-lg bg-[#9bb9a8]/20 text-[#2a553e] transition-colors group-hover:bg-[#9bb9a8] group-hover:text-[#171916]">
              <Users size={17} />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-mono text-3xl font-extrabold text-foreground">
              {stats?.total_users ?? 1}
            </span>
            <span className="text-xs text-muted-foreground">کاربر فعال</span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
            <span>مدیریت دسترسی‌ها</span>
            <ArrowUpLeft
              size={14}
              className="text-muted-foreground transition-transform group-hover:-translate-x-0.5 group-hover:text-[#2a553e]"
            />
          </div>
        </Link>
      ) : isFreelancer ? (
        <Link
          href="/freelancer"
          className="group relative block rounded-xl border border-border bg-card p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-[#e66042]/50 hover:shadow-md"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground">پروفایل و سطح کاربری</span>
            <span className="grid size-8 place-items-center rounded-lg bg-[#9bb9a8]/20 text-[#2a553e] transition-colors group-hover:bg-[#9bb9a8] group-hover:text-[#171916]">
              <ShieldCheck size={17} />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-lg font-bold text-foreground">
              {user.freelancer_level ? `سطح ${user.freelancer_level}` : 'عضو فعال'}
            </span>
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {user.freelancer_approval_status === 'approved' ? 'تاییدشده' : 'در حال بررسی'}
            </span>
            <ArrowUpLeft size={14} />
          </div>
        </Link>
      ) : (
        <div className="rounded-xl border border-border bg-card p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground">وضعیت همکاری</span>
            <span className="grid size-8 place-items-center rounded-lg bg-[#9bb9a8]/20 text-[#2a553e]">
              <CheckCircle2 size={17} />
            </span>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-lg font-bold text-foreground">همکاری استاندارد</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">دارای نظارت مستقل کیفی</p>
        </div>
      )}

      {/* Metric 4: Financial/Status summary */}
      <div className="rounded-xl border border-border bg-card p-5 shadow-xs">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-muted-foreground">وضعیت حساب و امنیت</span>
          <span className="grid size-8 place-items-center rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <CheckCircle2 size={17} />
          </span>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-lg font-bold text-emerald-600 dark:text-emerald-400">
            احراز هویت شده
          </span>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">ارتباط امن با سامانه برقرار است</p>
      </div>
    </section>
  );
}
