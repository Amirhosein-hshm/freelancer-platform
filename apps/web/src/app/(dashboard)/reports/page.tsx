import { redirect } from 'next/navigation';
import { getServerSessionUser, serverGetOptional } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { DashboardStatisticsResponse } from '@/generated/api/models';

export const metadata = { title: 'گزارش‌ها و آمار' };

export default async function ReportsPage() {
  const user = await getServerSessionUser();

  // Admins get redirected to the comprehensive admin analytics view
  if (hasRole(user, ROLES.admin)) {
    redirect('/admin/reports');
  }

  const stats = await serverGetOptional<DashboardStatisticsResponse>('reporting/dashboard');

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-6xl gap-6">
        <PageHeader
          title="گزارش‌ها و آمار فعالیت"
          description="خلاصه آمار و وضعیت تعاملات شما در سامانه دیدار"
        />

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                پروژه‌های فعال
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-3xl font-extrabold text-foreground">
                {stats?.active_projects ?? 0}
              </div>
              <p className="mt-1 text-xs text-muted-foreground">در حال انجام و بازبینی</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                کل کاربران همکار
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-3xl font-extrabold text-foreground">
                {stats?.total_users ?? 0}
              </div>
              <p className="mt-1 text-xs text-muted-foreground">شبکه ارتباطی مستقیم</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                فریلنسرهای فعال
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-3xl font-extrabold text-foreground">
                {stats?.total_freelancers ?? 0}
              </div>
              <p className="mt-1 text-xs text-muted-foreground">همکاران مجاز در پروژه</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                گردش مالی / تسویه‌شده
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-mono text-3xl font-extrabold text-foreground">
                {stats?.total_revenue ? `${stats.total_revenue} تومان` : '۰ تومان'}
              </div>
              <p className="mt-1 text-xs text-muted-foreground">مجموع تراکنش‌های ثبت‌شده</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
