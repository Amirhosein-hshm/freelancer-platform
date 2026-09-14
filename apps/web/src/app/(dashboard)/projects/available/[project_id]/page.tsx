import type { Metadata } from 'next';
import type { ProjectDetailsResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { ApplicationForm } from '@/features/freelancer/application-form';
import { FREELANCER_LEVEL_LABELS, PROJECT_PRIORITY_LABELS, PROJECT_VISIBILITY_LABELS, formatBudget } from '@/features/projects/project-domain';
import { ProjectStatusBadge } from '@/features/projects/status-badges';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import { formatDateTime } from '@/lib/format';

export const metadata: Metadata = { title: 'جزئیات پروژه موجود' };

export default async function AvailableProjectDetailsPage({ params }: { params: Promise<{ project_id: string }> }) {
  const { project_id: projectId } = await params;
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.freelancer) || !user.freelancer_profile_id) return <AppShell user={user}><ErrorState error={{ status: 403, code: 'freelancer_profile_required', message: 'برای مشاهده و درخواست پروژه باید پروفایل فریلنسری داشته باشید.', fields: {} }} /></AppShell>;
  const details = await serverGet<ProjectDetailsResponse>(`projects/${projectId}`);
  const { project } = details;
  const ownApplication = details.applications.find((application) => application.freelancer_profile_id === user.freelancer_profile_id) ?? null;
  return <AppShell user={user}><div className="mx-auto grid max-w-5xl gap-6"><PageHeader title={project.title} description={project.description} backHref="/projects/available" backLabel="بازگشت به پروژه‌های موجود" eyebrow={<><ProjectStatusBadge status={project.status} /><span className="ltr-embedded font-mono text-xs text-muted-foreground">{project.project_code}</span></>} /><Card><CardHeader><CardTitle className="text-base">مشخصات پروژه</CardTitle></CardHeader><CardContent><dl className="grid gap-5 text-sm sm:grid-cols-2 lg:grid-cols-3"><Detail label="بودجه" value={formatBudget(project.budget)} /><Detail label="اولویت" value={PROJECT_PRIORITY_LABELS[project.priority]} /><Detail label="نحوه نمایش" value={PROJECT_VISIBILITY_LABELS[project.visibility]} /><Detail label="سطح مورد نیاز" value={project.required_level ? FREELANCER_LEVEL_LABELS[project.required_level] : 'بدون محدودیت'} /><Detail label="مهلت درخواست" value={project.application_deadline ? formatDateTime(project.application_deadline) : 'تعیین نشده'} /><Detail label="تاریخ ایجاد" value={formatDateTime(project.created_at)} /></dl></CardContent></Card><ApplicationForm projectId={projectId} application={ownApplication} /></div></AppShell>;
}

function Detail({ label, value }: { label: string; value: string }) { return <div className="grid gap-1"><dt className="text-muted-foreground">{label}</dt><dd className="font-medium">{value}</dd></div>; }
