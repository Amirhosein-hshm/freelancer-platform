import Link from 'next/link';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { SystemAnalyticsResponse } from '@/generated/api/models/systemAnalyticsResponse';

export const metadata = { title: 'مدیریت سامانه' };

const sections = [
  ['همه پروژه‌ها', '/admin/projects', 'مشاهده و مدیریت تمام پروژه‌های سامانه'],
  ['کاربران و نقش‌ها', '/admin/users', 'مدیریت کاربران و اختصاص نقش'],
  ['فریلنسرها', '/admin/freelancers', 'بررسی تایید، سطح و وضعیت پروفایل‌ها'],
  ['عملیات از طرف کاربران', '/admin/on-behalf', 'ایجاد پروژه، درخواست و تیکت به نمایندگی'],
  ['دسته‌بندی‌ها', '/admin/categories', 'مدیریت دسته‌ها و ناظران واجد شرایط'],
  ['قالب‌های فرم', '/admin/form-templates', 'مدیریت نسخه‌های پیش‌نویس و منتشرشده'],
  ['گزارش‌ها', '/admin/reports', 'مشاهده آمار کاربران، پروژه‌ها و نقش‌ها'],
] as const;

function Metric({ label, value }: { label: string; value: string | number | null | undefined }) {
  return <div className="grid gap-1 rounded-lg border bg-background p-4"><span className="text-sm text-muted-foreground">{label}</span><strong className="text-2xl">{value ?? '—'}</strong></div>;
}

export default async function AdminPage() {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) redirect('/dashboard');
  const analytics = await serverGet<SystemAnalyticsResponse>('reporting/system-analytics');

  return <AppShell user={user}>
    <div className="mx-auto grid max-w-6xl gap-6">
      <header><h1 className="text-2xl font-semibold">مدیریت سامانه</h1><p className="mt-1 text-sm text-muted-foreground">گزارش لحظه‌ای و عملیات مدیریتی</p></header>
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="گزارش سامانه">
        <Metric label="کل کاربران" value={analytics.users.total_users} />
        <Metric label="کاربران فعال" value={analytics.users.active_users} />
        <Metric label="پروژه‌های فعال" value={analytics.projects.created} />
        <Metric label="درآمد کل" value={analytics.dashboard.total_revenue} />
        <Metric label="پروژه‌های تکمیل‌شده" value={analytics.projects.completed} />
        <Metric label="پروژه‌های لغوشده" value={analytics.projects.cancelled} />
        <Metric label="فریلنسرهای تاییدشده" value={analytics.freelancers.approved_freelancers} />
        <Metric label="فریلنسرهای در انتظار" value={analytics.freelancers.pending_freelancers} />
        <Metric label="میانگین امتیاز فریلنسرها" value={analytics.freelancers.average_rating} />
        <Metric label="مشتریان" value={analytics.customers.total_customers} />
        <Metric label="پروژه‌های فعال مشتریان" value={analytics.customers.active_projects} />
        <Metric label="پروژه‌های تکمیل‌شده مشتریان" value={analytics.customers.completed_projects} />
      </section>
      <section className="grid gap-4 sm:grid-cols-2" aria-label="عملیات مدیریتی">
        {sections.map(([title, href, description]) => <Link key={href} href={href} className="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"><Card className="h-full transition-colors hover:border-primary"><CardHeader><CardTitle>{title}</CardTitle></CardHeader><CardContent className="text-sm text-muted-foreground">{description}</CardContent></Card></Link>)}
      </section>
    </div>
  </AppShell>;
}
