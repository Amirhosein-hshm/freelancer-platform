import { Badge } from '@/components/ui/badge';
import { ROLE_LABELS } from '@/lib/auth/navigation';

export function DashboardGreeting({ email, roles }: { email: string; roles: string[] }) {
  const primary = roles[0] ?? 'customer';
  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="mb-2 text-xs font-bold text-primary">داشبورد</p>
          <h1 className="text-xl font-extrabold sm:text-2xl">خوش آمدید 👋</h1>
          <p dir="ltr" className="mt-2 text-sm text-muted-foreground">
            {email}
          </p>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {roles.map((role) => (
            <Badge key={role} variant="secondary">
              {ROLE_LABELS[role] ?? role}
            </Badge>
          ))}
        </div>
      </div>
      <p className="mt-5 text-sm leading-7 text-muted-foreground">
        این پایه داشبورد شماست. بخش‌های پروژه‌ها، درخواست‌ها و پشتیبانی در مراحل بعدی به سیستم متصل می‌شوند.
        ناوبری سمت راست بر اساس نقش‌های شما نمایش داده می‌شود.
      </p>
      <p className="sr-only">نقش اصلی: {ROLE_LABELS[primary] ?? primary}</p>
    </section>
  );
}
