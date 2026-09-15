import { CheckCircle2, Lock, ShieldCheck, UserCheck } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { ROLE_LABELS } from '@/lib/auth/navigation';
import type { UserMeResponse } from '@/generated/api/models';

export function DashboardUserCard({ user }: { user: UserMeResponse }) {
  return (
    <section aria-labelledby="profile-summary-heading" className="rounded-2xl border border-border bg-card p-6 shadow-xs sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-[#e66042]">
            <span className="h-[2px] w-5 bg-[#e66042]" />
            مشخصات حساب
          </div>
          <h2 id="profile-summary-heading" className="mt-1 text-lg font-bold">
            اطلاعات کاربری و امنیت
          </h2>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 size={14} />
          <span>حساب کاربری فعال و احراز هویت‌شده</span>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Email */}
        <div className="rounded-xl border border-border/80 bg-muted/20 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <UserCheck size={14} />
            <span>ایمیل کاربری</span>
          </div>
          <p dir="ltr" className="mt-2 text-start font-mono text-sm font-semibold text-foreground truncate">
            {user.email}
          </p>
          <span className="mt-1.5 inline-block text-[11px] text-emerald-600 dark:text-emerald-400">
            ✓ تایید شده
          </span>
        </div>

        {/* Roles */}
        <div className="rounded-xl border border-border/80 bg-muted/20 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <ShieldCheck size={14} />
            <span>سطح دسترسی</span>
          </div>
          <div className="mt-2 flex flex-wrap gap-1">
            {user.roles.map((role) => (
              <Badge key={role} variant="secondary" className="text-xs">
                {ROLE_LABELS[role] ?? role}
              </Badge>
            ))}
          </div>
          <span className="mt-1.5 inline-block text-[11px] text-muted-foreground">
            دسترسی عملیاتی استاندارد
          </span>
        </div>

        {/* Security */}
        <div className="rounded-xl border border-border/80 bg-muted/20 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Lock size={14} />
            <span>امنیت نشست</span>
          </div>
          <p className="mt-2 text-sm font-semibold text-foreground">رمز عبور محافظت‌شده</p>
          <span className="mt-1.5 inline-block text-[11px] text-muted-foreground">
            توکن سشن دارای امضای دیجیتال
          </span>
        </div>

        {/* Operational Status */}
        <div className="rounded-xl border border-border/80 bg-muted/20 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <CheckCircle2 size={14} />
            <span>وضعیت در پلتفرم</span>
          </div>
          <p className="mt-2 text-sm font-semibold text-foreground">
            {user.freelancer_onboarding_needed
              ? 'نیازمند تکمیل پروفایل فریلنسری'
              : 'فعالیت کامل بدون محدودیت'}
          </p>
          <span className="mt-1.5 inline-block text-[11px] text-emerald-600 dark:text-emerald-400">
            آماده برای همکاری و پروژه‌ها
          </span>
        </div>
      </div>
    </section>
  );
}
