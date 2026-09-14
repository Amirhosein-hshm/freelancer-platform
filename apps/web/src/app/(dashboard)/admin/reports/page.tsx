import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PageHeader } from '@/components/ui/page-header';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { DashboardStatisticsResponse, UserStatisticsResponse, ProjectStatisticsResponse, FreelancerStatisticsResponse, CustomerStatisticsResponse } from '@/generated/api/models';

export const metadata = { title: 'گزارش‌های سامانه' };
export default async function AdminReportsPage() {
  const user = await getServerSessionUser(); if (!hasRole(user, ROLES.admin)) redirect('/dashboard');
  const [dashboard, users, projects, freelancers, customers] = await Promise.all([
    serverGet<DashboardStatisticsResponse>('reporting/dashboard'), serverGet<UserStatisticsResponse>('reporting/users'), serverGet<ProjectStatisticsResponse>('reporting/projects'), serverGet<FreelancerStatisticsResponse>('reporting/freelancers'), serverGet<CustomerStatisticsResponse>('reporting/customers'),
  ]);
  const groups = [
    ['داشبورد', [['کل کاربران', dashboard.total_users], ['پروژه‌های فعال', dashboard.active_projects], ['کل فریلنسرها', dashboard.total_freelancers], ['درآمد کل', dashboard.total_revenue]]],
    ['کاربران', [['کل کاربران', users.total_users], ['کاربران تاییدشده', users.verified_users], ['کاربران فعال', users.active_users]]],
    ['پروژه‌ها', [['ایجادشده', projects.created], ['تکمیل‌شده', projects.completed], ['لغوشده', projects.cancelled]]],
    ['فریلنسرها', [['کل', freelancers.total_freelancers], ['تاییدشده', freelancers.approved_freelancers], ['در انتظار', freelancers.pending_freelancers], ['میانگین امتیاز', freelancers.average_rating]]],
    ['مشتریان', [['کل', customers.total_customers], ['پروژه‌های فعال', customers.active_projects], ['پروژه‌های تکمیل‌شده', customers.completed_projects]]],
  ] as const;
  return <AppShell user={user}><div className="mx-auto grid max-w-6xl gap-6"><PageHeader title="گزارش‌های سامانه" description="مقادیر مستقیماً از endpointهای گزارش‌گیری backend خوانده می‌شوند." /><div className="grid gap-5 md:grid-cols-2">{groups.map(([title, metrics]) => <Card key={title}><CardHeader><CardTitle className="text-base">{title}</CardTitle></CardHeader><CardContent className="grid grid-cols-2 gap-3">{metrics.map(([label, value]) => <div key={label} className="rounded-md border p-3"><div className="text-xs text-muted-foreground">{label}</div><div className="mt-1 text-lg font-semibold">{value ?? '—'}</div></div>)}</CardContent></Card>)}</div></div></AppShell>;
}
