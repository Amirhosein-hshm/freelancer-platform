import type { UserMeResponse } from '@/generated/api/models';

export function SessionSummary({ user }: { user: UserMeResponse }) {
  const items: { label: string; value: string; ltr?: boolean }[] = [
    { label: 'شناسه کاربر', value: user.user_id, ltr: true },
    { label: 'تعداد نقش‌ها', value: String(user.roles.length) },
    { label: 'تعداد دسترسی‌ها', value: String(user.permissions.length) },
    {
      label: 'وضعیت فریلنسری',
      value: user.freelancer_onboarding_needed
        ? 'نیازمند تکمیل ثبت مشخصات'
        : user.freelancer_approval_status ?? 'غیرفعال',
    },
  ];

  return (
    <section aria-label="خلاصه نشست" className="grid gap-4 sm:grid-cols-2">
      {items.map((item) => (
        <div key={item.label} className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <p className="text-xs font-medium text-muted-foreground">{item.label}</p>
          <p dir={item.ltr ? 'ltr' : undefined} className="mt-2 truncate text-sm font-semibold">
            {item.value}
          </p>
        </div>
      ))}
    </section>
  );
}
