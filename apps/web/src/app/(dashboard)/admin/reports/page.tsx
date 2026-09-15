import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import { AdminReportsView } from '@/components/admin/admin-reports-view';
import type {
  DashboardStatisticsResponse,
  UserStatisticsResponse,
  ProjectStatisticsResponse,
  FreelancerStatisticsResponse,
  CustomerStatisticsResponse,
} from '@/generated/api/models';

export const metadata = { title: 'گزارش‌ها و تحلیل‌های سامانه' };

export default async function AdminReportsPage() {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) {
    redirect('/dashboard');
  }

  const [dashboard, users, projects, freelancers, customers] = await Promise.all([
    serverGet<DashboardStatisticsResponse>('reporting/dashboard'),
    serverGet<UserStatisticsResponse>('reporting/users'),
    serverGet<ProjectStatisticsResponse>('reporting/projects'),
    serverGet<FreelancerStatisticsResponse>('reporting/freelancers'),
    serverGet<CustomerStatisticsResponse>('reporting/customers'),
  ]);

  return (
    <AppShell user={user}>
      <div className="grid gap-6">
        <PageHeader
          title="گزارش‌ها و تحلیل‌های سامانه"
          description="پایش جامع شاخص‌های عملکرد سامانه، وضعیت پروژه‌ها، کاربران، استعدادها و درآمد کل."
        />
        <AdminReportsView
          dashboard={dashboard}
          users={users}
          projects={projects}
          freelancers={freelancers}
          customers={customers}
        />
      </div>
    </AppShell>
  );
}
