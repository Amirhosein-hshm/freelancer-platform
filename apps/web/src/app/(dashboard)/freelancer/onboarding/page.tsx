import type { Metadata } from 'next';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { Card, CardContent } from '@/components/ui/card';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { ProfileForm } from '@/features/freelancer/profile-form';
import { getServerSessionUser } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';

export const metadata: Metadata = { title: 'تکمیل ثبت فریلنسر' };

export default async function FreelancerOnboardingPage() {
  const user = await getServerSessionUser();
  if (user.freelancer_profile_id) redirect('/freelancer');
  const allowed = hasRole(user, ROLES.freelancer);
  return <AppShell user={user}><div className="mx-auto grid max-w-3xl gap-6"><PageHeader title="ساخت پروفایل فریلنسری" description="اطلاعات حرفه‌ای اولیه را ثبت کنید. پس از ساخت پروفایل می‌توانید رزومه و نمونه‌کار اضافه کنید و درخواست تأیید بفرستید." />{allowed ? <Card><CardContent className="p-6"><ProfileForm /></CardContent></Card> : <ErrorState error={{ status: 403, code: 'permission_denied', message: 'این بخش فقط برای نقش فریلنسر در دسترس است.', fields: {} }} />}</div></AppShell>;
}
