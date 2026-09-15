'use client';

import { useMemo } from 'react';
import type * as echarts from 'echarts';
import {
  Users,
  UserCheck,
  FolderKanban,
  CheckCircle2,
  XCircle,
  Coins,
  ShieldCheck,
  Clock,
  Star,
  Briefcase,
  Activity,
  Award,
} from 'lucide-react';
import { EChartCanvas } from './echart-canvas';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { formatNumber } from '@/lib/format';
import { formatAmount } from '@/features/projects/project-domain';
import type {
  DashboardStatisticsResponse,
  UserStatisticsResponse,
  ProjectStatisticsResponse,
  FreelancerStatisticsResponse,
  CustomerStatisticsResponse,
} from '@/generated/api/models';

interface AdminReportsViewProps {
  dashboard: DashboardStatisticsResponse;
  users: UserStatisticsResponse;
  projects: ProjectStatisticsResponse;
  freelancers: FreelancerStatisticsResponse;
  customers: CustomerStatisticsResponse;
}

export function AdminReportsView({
  dashboard,
  users,
  projects,
  freelancers,
  customers,
}: AdminReportsViewProps) {
  // Top 6 Highlight KPIs
  const kpis = [
    {
      id: 'total_users',
      label: 'کل کاربران سامانه',
      value: formatNumber(users.total_users),
      subtext: `${formatNumber(users.verified_users)} تاییدشده`,
      icon: Users,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-500/10',
    },
    {
      id: 'active_users',
      label: 'کاربران فعال',
      value: formatNumber(users.active_users),
      subtext: 'فعال در سامانه',
      icon: Activity,
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-500/10',
    },
    {
      id: 'active_projects',
      label: 'پروژه‌های فعال',
      value: formatNumber(dashboard.active_projects),
      subtext: `${formatNumber(projects.completed)} تکمیل‌شده`,
      icon: FolderKanban,
      color: 'text-[#e66042]',
      bg: 'bg-[#e66042]/10',
    },
    {
      id: 'total_revenue',
      label: 'درآمد کل سامانه',
      value: `${formatAmount(dashboard.total_revenue)} تومان`,
      subtext: 'گردش کل مالی',
      icon: Coins,
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-500/10',
    },
    {
      id: 'approved_freelancers',
      label: 'فریلنسرهای تاییدشده',
      value: formatNumber(freelancers.approved_freelancers),
      subtext: `${formatNumber(freelancers.pending_freelancers)} در انتظار بررسی`,
      icon: ShieldCheck,
      color: 'text-violet-600 dark:text-violet-400',
      bg: 'bg-violet-500/10',
    },
    {
      id: 'total_customers',
      label: 'مشتریان سامانه',
      value: formatNumber(customers.total_customers),
      subtext: `${formatNumber(customers.active_projects)} پروژه فعال`,
      icon: Briefcase,
      color: 'text-cyan-600 dark:text-cyan-400',
      bg: 'bg-cyan-500/10',
    },
  ];

  // Chart 1: Project Lifecycle Donut Chart
  const projectChartOption = useMemo<echarts.EChartsOption>(() => {
    const active = dashboard.active_projects || 0;
    const completed = projects.completed || 0;
    const cancelled = projects.cancelled || 0;
    const total = active + completed + cancelled;

    return {
      tooltip: {
        trigger: 'item',
        formatter: (params: unknown) => {
          const p = params as { name: string; value: number; percent: number };
          return `<div style="font-family: inherit; direction: rtl; text-align: right; padding: 4px 8px;">
            <b>${p.name}</b>: ${formatNumber(p.value)} پروژه (${p.percent}٪)
          </div>`;
        },
      },
      legend: {
        bottom: '0%',
        left: 'center',
        textStyle: { fontFamily: 'inherit', color: 'inherit' },
      },
      series: [
        {
          name: 'چرخه حیات پروژه‌ها',
          type: 'pie',
          radius: ['45%', '70%'],
          center: ['50%', '45%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#ffffff',
            borderWidth: 2,
          },
          label: {
            show: false,
            position: 'center',
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold',
              formatter: () => `${formatNumber(total)}\nکل پروژه‌ها`,
            },
          },
          data: [
            { value: active, name: 'پروژه‌های فعال', itemStyle: { color: '#e66042' } },
            { value: completed, name: 'تکمیل‌شده', itemStyle: { color: '#10b981' } },
            { value: cancelled, name: 'لغوشده', itemStyle: { color: '#94a3b8' } },
          ],
        },
      ],
    };
  }, [dashboard.active_projects, projects.completed, projects.cancelled]);

  // Chart 2: Freelancer & Talent Funnel
  const talentChartOption = useMemo<echarts.EChartsOption>(() => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: unknown) => {
          const items = params as Array<{ seriesName: string; value: number }>;
          if (!items || !items[0]) return '';
          return `<div style="font-family: inherit; direction: rtl; text-align: right; padding: 4px 8px;">
            <b>${items[0].seriesName}</b>: ${formatNumber(items[0].value)} نفر
          </div>`;
        },
      },
      grid: {
        top: '12%',
        right: '4%',
        bottom: '10%',
        left: '6%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: ['کل فریلنسرها', 'تاییدشده', 'در انتظار بررسی'],
        axisLabel: { fontFamily: 'inherit', color: 'inherit' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { fontFamily: 'inherit', color: 'inherit' },
        splitLine: { lineStyle: { color: 'rgba(128,128,128,0.15)' } },
      },
      series: [
        {
          name: 'فریلنسرها',
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            borderRadius: [8, 8, 0, 0],
            color: (params: { dataIndex: number }) => {
              const colors = ['#6366f1', '#10b981', '#f59e0b'];
              return colors[params.dataIndex] || '#6366f1';
            },
          },
          data: [
            freelancers.total_freelancers || 0,
            freelancers.approved_freelancers || 0,
            freelancers.pending_freelancers || 0,
          ],
        },
      ],
    };
  }, [freelancers.total_freelancers, freelancers.approved_freelancers, freelancers.pending_freelancers]);

  // Chart 3: Users Ecosystem Distribution
  const usersChartOption = useMemo<echarts.EChartsOption>(() => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
      },
      grid: {
        top: '12%',
        right: '4%',
        bottom: '10%',
        left: '6%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: ['کل کاربران', 'تاییدشده', 'فعال'],
        axisLabel: { fontFamily: 'inherit', color: 'inherit' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { fontFamily: 'inherit', color: 'inherit' },
        splitLine: { lineStyle: { color: 'rgba(128,128,128,0.15)' } },
      },
      series: [
        {
          name: 'تعداد کاربران',
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            borderRadius: [8, 8, 0, 0],
            color: (params: { dataIndex: number }) => {
              const colors = ['#0284c7', '#059669', '#e66042'];
              return colors[params.dataIndex] || '#0284c7';
            },
          },
          data: [
            users.total_users || 0,
            users.verified_users || 0,
            users.active_users || 0,
          ],
        },
      ],
    };
  }, [users.total_users, users.verified_users, users.active_users]);

  // Chart 4: Customer Engagement & Projects Breakdown
  const customersChartOption = useMemo<echarts.EChartsOption>(() => {
    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
      },
      grid: {
        top: '12%',
        right: '4%',
        bottom: '10%',
        left: '6%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: ['کل مشتریان', 'پروژه‌های فعال', 'پروژه‌های تکمیل'],
        axisLabel: { fontFamily: 'inherit', color: 'inherit' },
      },
      yAxis: {
        type: 'value',
        axisLabel: { fontFamily: 'inherit', color: 'inherit' },
        splitLine: { lineStyle: { color: 'rgba(128,128,128,0.15)' } },
      },
      series: [
        {
          name: 'آمار مشتریان و پروژه‌ها',
          type: 'bar',
          barWidth: '40%',
          itemStyle: {
            borderRadius: [8, 8, 0, 0],
            color: (params: { dataIndex: number }) => {
              const colors = ['#0891b2', '#e66042', '#10b981'];
              return colors[params.dataIndex] || '#0891b2';
            },
          },
          data: [
            customers.total_customers || 0,
            customers.active_projects || 0,
            customers.completed_projects || 0,
          ],
        },
      ],
    };
  }, [customers.total_customers, customers.active_projects, customers.completed_projects]);

  // All 12 requested metrics in a clean, comprehensive master table
  const allTwelveMetrics = [
    {
      title: 'کل کاربران',
      category: 'کاربران',
      value: formatNumber(users.total_users),
      raw: users.total_users,
      icon: Users,
      badge: 'ثبت‌نام کل',
      status: 'نرمال',
    },
    {
      title: 'کاربران فعال',
      category: 'کاربران',
      value: formatNumber(users.active_users),
      raw: users.active_users,
      icon: UserCheck,
      badge: 'فعال در سامانه',
      status: 'بهینه',
    },
    {
      title: 'پروژه‌های فعال',
      category: 'پروژه‌ها',
      value: formatNumber(dashboard.active_projects),
      raw: dashboard.active_projects,
      icon: FolderKanban,
      badge: 'در جریان اجرا',
      status: 'بهینه',
    },
    {
      title: 'درآمد کل',
      category: 'مالی',
      value: `${formatAmount(dashboard.total_revenue)} تومان`,
      raw: dashboard.total_revenue,
      icon: Coins,
      badge: 'گردش حساب کل',
      status: 'مالی',
    },
    {
      title: 'پروژه‌های تکمیل‌شده',
      category: 'پروژه‌ها',
      value: formatNumber(projects.completed),
      raw: projects.completed,
      icon: CheckCircle2,
      badge: 'پایان موفق',
      status: 'موفق',
    },
    {
      title: 'پروژه‌های لغوشده',
      category: 'پروژه‌ها',
      value: formatNumber(projects.cancelled),
      raw: projects.cancelled,
      icon: XCircle,
      badge: 'فسخ یا ابطال',
      status: 'نیازمند پایش',
    },
    {
      title: 'فریلنسرهای تاییدشده',
      category: 'فریلنسرها',
      value: formatNumber(freelancers.approved_freelancers),
      raw: freelancers.approved_freelancers,
      icon: ShieldCheck,
      badge: 'تایید هویت و مهارت',
      status: 'بهینه',
    },
    {
      title: 'فریلنسرهای در انتظار',
      category: 'فریلنسرها',
      value: formatNumber(freelancers.pending_freelancers),
      raw: freelancers.pending_freelancers,
      icon: Clock,
      badge: 'صف ارزیابی',
      status: 'در جریان',
    },
    {
      title: 'میانگین امتیاز فریلنسرها',
      category: 'کیفیت و رضایت',
      value: freelancers.average_rating !== null ? `${freelancers.average_rating} از ۵` : 'ثبت نشده',
      raw: freelancers.average_rating ?? 0,
      icon: Star,
      badge: 'کیفیت خدمات',
      status: 'کیفی',
    },
    {
      title: 'مشتریان',
      category: 'مشتریان',
      value: formatNumber(customers.total_customers),
      raw: customers.total_customers,
      icon: Briefcase,
      badge: 'کارفرمایان ثبت‌شده',
      status: 'نرمال',
    },
    {
      title: 'پروژه‌های فعال مشتریان',
      category: 'مشتریان',
      value: formatNumber(customers.active_projects),
      raw: customers.active_projects,
      icon: Activity,
      badge: 'سفارش‌های در جریان',
      status: 'بهینه',
    },
    {
      title: 'پروژه‌های تکمیل‌شده مشتریان',
      category: 'مشتریان',
      value: formatNumber(customers.completed_projects),
      raw: customers.completed_projects,
      icon: Award,
      badge: 'تحویل نهایی مشتری',
      status: 'موفق',
    },
  ];

  return (
    <div className="grid gap-8">
      {/* KPI Highlight Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Card key={kpi.id} className="relative overflow-hidden transition-all duration-200 hover:shadow-md">
              <CardContent className="flex items-center gap-4 p-5">
                <span className={`grid size-12 shrink-0 place-items-center rounded-2xl ${kpi.bg} ${kpi.color}`}>
                  <Icon size={24} />
                </span>
                <div className="flex min-w-0 flex-1 flex-col">
                  <span className="text-xs font-medium text-muted-foreground">{kpi.label}</span>
                  <span className="mt-1 font-mono text-2xl font-bold tracking-tight text-foreground">
                    {kpi.value}
                  </span>
                  <span className="mt-0.5 text-[11px] text-muted-foreground/80">{kpi.subtext}</span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Visual Analytics / Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Chart 1 */}
        <Card className="transition-all duration-200 hover:shadow-md">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-bold">چرخه حیات و سلامت پروژه‌ها</CardTitle>
            <CardDescription className="text-xs">
              توزیع وضعیت پروژه‌های فعال، تکمیل‌شده و لغوشده
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <EChartCanvas options={projectChartOption} height={280} />
          </CardContent>
        </Card>

        {/* Chart 2 */}
        <Card className="transition-all duration-200 hover:shadow-md">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-bold">اکوسیستم استعدادها و فریلنسرها</CardTitle>
            <CardDescription className="text-xs">
              فریلنسرهای کل، فریلنسرهای تاییدشده و در انتظار بررسی
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <EChartCanvas options={talentChartOption} height={280} />
          </CardContent>
        </Card>

        {/* Chart 3 */}
        <Card className="transition-all duration-200 hover:shadow-md">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-bold">وضعیت اعتبارسنجی و فعالیت کاربران</CardTitle>
            <CardDescription className="text-xs">
              مقایسه کل کاربران با کاربران تاییدشده و کاربران فعال سامانه
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <EChartCanvas options={usersChartOption} height={280} />
          </CardContent>
        </Card>

        {/* Chart 4 */}
        <Card className="transition-all duration-200 hover:shadow-md">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-bold">فعالیت کارفرمایان و تحویل سفارش‌ها</CardTitle>
            <CardDescription className="text-xs">
              تعداد کل مشتریان در مقایسه با پروژه‌های فعال و تکمیل‌شده
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-2">
            <EChartCanvas options={customersChartOption} height={280} />
          </CardContent>
        </Card>
      </div>

      {/* Comprehensive 12-Metrics Master Matrix */}
      <Card className="overflow-hidden border border-border/80">
        <CardHeader className="border-b border-border/70 bg-muted/30 px-6 py-4">
          <CardTitle className="text-base font-bold">ماتریس جامع شاخص‌های دوازده‌گانه سامانه</CardTitle>
          <CardDescription className="text-xs">
            خلاصه کامل شاخص‌های کلیدی عملکرد بر اساس داده‌های مستقیم گزارش‌گیری سرور
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-start text-sm">
              <thead className="border-b border-border/70 bg-muted/40 text-xs font-semibold text-muted-foreground">
                <tr>
                  <th className="px-6 py-3 text-start">عنوان شاخص</th>
                  <th className="px-6 py-3 text-start">دسته‌بندی</th>
                  <th className="px-6 py-3 text-start">مقدار جاری</th>
                  <th className="px-6 py-3 text-start">برچسب وضعیت</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60">
                {allTwelveMetrics.map((item) => {
                  const Icon = item.icon;
                  return (
                    <tr key={item.title} className="transition-colors hover:bg-muted/30">
                      <td className="px-6 py-3.5">
                        <div className="flex items-center gap-3">
                          <span className="grid size-8 place-items-center rounded-lg bg-muted text-muted-foreground">
                            <Icon size={16} />
                          </span>
                          <span className="font-medium text-foreground">{item.title}</span>
                        </div>
                      </td>
                      <td className="px-6 py-3.5 text-xs text-muted-foreground">
                        {item.category}
                      </td>
                      <td className="px-6 py-3.5">
                        <span className="font-mono text-base font-bold text-foreground">
                          {item.value}
                        </span>
                      </td>
                      <td className="px-6 py-3.5">
                        <span className="inline-flex items-center rounded-md bg-muted px-2.5 py-1 text-[11px] font-medium text-muted-foreground">
                          {item.badge}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
