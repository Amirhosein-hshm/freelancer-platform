import Link from 'next/link';
import {
  ArrowLeft,
  FolderKanban,
  Inbox,
  KeyRound,
  ShieldCheck,
  Ticket,
} from 'lucide-react';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { UserMeResponse } from '@/generated/api/models';

export function DashboardQuickActions({ user }: { user: UserMeResponse }) {
  const isAdmin = hasRole(user, ROLES.admin);
  const isFreelancer = hasRole(user, ROLES.freelancer);

  const actions = [
    {
      title: isFreelancer ? 'پروژه‌های در دسترس' : 'پروژه‌های من',
      description: isFreelancer
        ? 'مشاهده و ارسال پیشنهاد برای پروژه‌های موجود'
        : 'مدیریت و پیگیری کلیه پروژه‌های ثبت‌شده',
      href: isFreelancer ? '/projects/available' : '/projects',
      icon: FolderKanban,
      badge: 'کارها',
    },
    {
      title: 'مرکز پشتیبانی و تیکت‌ها',
      description: 'ارتباط مستقیم با تیم پشتیبانی و طرح پرسش‌ها',
      href: '/tickets',
      icon: Ticket,
      badge: 'پشتیبانی',
    },
    {
      title: 'گزارش‌ها و آمار',
      description: 'بررسی شاخص‌ها، تحلیل فعالیت و تاریخچه اقدامات',
      href: isAdmin ? '/admin/reports' : '/reports',
      icon: Inbox,
      badge: 'آمار',
    },
    {
      title: 'امنیت و گذرواژه',
      description: 'تغییر رمز عبور و تنظیمات نشست‌های کاربری',
      href: '/change-password',
      icon: KeyRound,
      badge: 'امنیت',
    },
  ];

  if (isAdmin) {
    actions.unshift({
      title: 'پنل مدیریت جامع',
      description: 'دسترسی به مدیریت کاربران، دسته‌ها و قالب‌های فرم',
      href: '/admin',
      icon: ShieldCheck,
      badge: 'مدیر کل',
    });
  }

  return (
    <section aria-labelledby="quick-actions-heading" className="rounded-2xl border border-border bg-card p-6 shadow-xs sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-[#e66042]">
            <span className="h-[2px] w-5 bg-[#e66042]" />
            دسترسی سریع
          </div>
          <h2 id="quick-actions-heading" className="mt-1 text-lg font-bold">
            بخش‌های کاربردی سامانه
          </h2>
        </div>
        <span className="text-xs text-muted-foreground">جابجایی سریع به صفحات پرکاربرد</span>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {actions.map((act) => {
          const Icon = act.icon;
          return (
            <Link
              key={act.href}
              href={act.href}
              className="group flex flex-col justify-between rounded-xl border border-border bg-background p-5 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-[#e66042]/50 hover:shadow-md"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="grid size-9 place-items-center rounded-lg bg-[#e66042]/10 text-[#e66042] transition-colors group-hover:bg-[#e66042] group-hover:text-white">
                    <Icon size={18} />
                  </span>
                  <span className="rounded-full bg-muted px-2.5 py-0.5 text-[11px] font-medium text-muted-foreground">
                    {act.badge}
                  </span>
                </div>
                <h3 className="mt-3.5 text-base font-bold text-foreground transition-colors group-hover:text-[#e66042]">
                  {act.title}
                </h3>
                <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                  {act.description}
                </p>
              </div>

              <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-[#e66042]">
                <span>ورود به بخش</span>
                <ArrowLeft
                  size={13}
                  className="transition-transform group-hover:-translate-x-1"
                />
              </div>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
