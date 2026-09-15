import { redirect } from 'next/navigation';
import { getServerSessionUser, serverGetOptional, serverGetPage } from '@/lib/api/server';
import { getDashboardEntry } from '@/lib/auth/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { DashboardHero } from './_components/dashboard-hero';
import { DashboardMetrics } from './_components/dashboard-metrics';
import { DashboardWorkflow } from './_components/dashboard-workflow';
import { DashboardQuickActions } from './_components/dashboard-quick-actions';
import { DashboardUserCard } from './_components/dashboard-user-card';
import { DashboardProjectsPreview } from './_components/dashboard-projects-preview';
import type { DashboardStatisticsResponse, ProjectResponse, TicketResponse } from '@/generated/api/models';

export const metadata = { title: 'داشبورد' };

export default async function DashboardPage() {
  const user = await getServerSessionUser();

  // Route freelancers with incomplete onboarding straight into onboarding.
  if (user.freelancer_onboarding_needed && getDashboardEntry(user) !== '/dashboard') {
    redirect(getDashboardEntry(user));
  }

  const [stats, projectsPage, ticketsPage] = await Promise.all([
    serverGetOptional<DashboardStatisticsResponse>('reporting/dashboard'),
    serverGetPage<ProjectResponse>('projects', { limit: 4 }).catch(() => ({ items: [], meta: undefined })),
    serverGetPage<TicketResponse>('tickets', { limit: 4 }).catch(() => ({ items: [], meta: undefined })),
  ]);

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-6xl gap-6">
        <DashboardHero user={user} />
        <DashboardMetrics
          user={user}
          stats={stats}
          activeProjectsCount={projectsPage.items.length}
          openTicketsCount={ticketsPage.items.length}
        />
        <DashboardProjectsPreview projects={projectsPage.items} />
        <DashboardWorkflow />
        <DashboardQuickActions user={user} />
        <DashboardUserCard user={user} />
      </div>
    </AppShell>
  );
}
