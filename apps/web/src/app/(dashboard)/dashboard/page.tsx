import { redirect } from 'next/navigation';
import { getServerSessionUser } from '@/lib/api/server';
import { getDashboardEntry } from '@/lib/auth/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { DashboardGreeting } from './_components/dashboard-greeting';
import { SessionSummary } from './_components/session-summary';

export const metadata = { title: 'داشبورد' };

export default async function DashboardPage() {
  const user = await getServerSessionUser();

  // Route freelancers with incomplete onboarding straight into onboarding.
  if (user.freelancer_onboarding_needed && getDashboardEntry(user) !== '/dashboard') {
    redirect(getDashboardEntry(user));
  }

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-6xl gap-6">
        <DashboardGreeting email={user.email} roles={user.roles} />
        <SessionSummary user={user} />
      </div>
    </AppShell>
  );
}
