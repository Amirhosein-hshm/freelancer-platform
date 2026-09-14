import type { Metadata } from 'next';
import { CircleAlert, FileCheck2, RotateCcw } from 'lucide-react';
import type { DeliveryResponse, ProjectDetailsResponse, ProjectRevisionRequestResponse } from '@/generated/api/models';
import { ProjectStatus } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { DeliveryForm } from '@/features/freelancer/delivery-form';
import { canSubmitFreelancerDelivery, getFreelancerProjectStatusMessage, PROJECT_PRIORITY_LABELS, formatBudget } from '@/features/projects/project-domain';
import { DeliveryStatusBadge, ProjectStatusBadge } from '@/features/projects/status-badges';
import { getServerSessionUser, serverGet, serverGetPage } from '@/lib/api/server';
import { formatDateTime, formatNumber } from '@/lib/format';

export const metadata: Metadata = { title: 'میزکار پروژه' };

export default async function FreelancerProjectWorkbench({ params }: { params: Promise<{ project_id: string }> }) {
  const { project_id: projectId } = await params;
  const [user, details, revisions] = await Promise.all([
    getServerSessionUser(),
    serverGet<ProjectDetailsResponse>(`projects/${projectId}`),
    getAllRevisions(projectId),
  ]);
  const profileId = user.freelancer_profile_id;
  const ownApplication = profileId ? details.applications.find((application) => application.freelancer_profile_id === profileId) : undefined;
  const selected = ownApplication?.status === 'accepted' && details.project.selected_application_id === ownApplication.application_id;
  if (!selected) return <AppShell user={user}><ErrorState error={{ status: 403, code: 'project_not_assigned', message: 'این پروژه براساس پاسخ سرور به شما واگذار نشده است.', fields: {} }} /></AppShell>;
  const { project, deliveries } = details;
  const canDeliver = canSubmitFreelancerDelivery(project.status);
  return <AppShell user={user}><div className="mx-auto grid max-w-5xl gap-6"><PageHeader title={project.title} description="تحویل‌ها و درخواست‌های اصلاح این پروژه را مدیریت کنید." backHref="/projects/my-project" backLabel="بازگشت به پروژه‌های من" eyebrow={<><ProjectStatusBadge status={project.status} /><span className="ltr-embedded font-mono text-xs text-muted-foreground">{project.project_code}</span></>} /><Card><CardHeader><CardTitle className="text-base">خلاصه قرارداد</CardTitle></CardHeader><CardContent><dl className="grid gap-5 text-sm sm:grid-cols-3"><Detail label="بودجه" value={formatBudget(project.budget)} /><Detail label="اولویت" value={PROJECT_PRIORITY_LABELS[project.priority]} /><Detail label="مهلت درخواست" value={project.application_deadline ? formatDateTime(project.application_deadline) : 'تعیین نشده'} /></dl></CardContent></Card>{canDeliver ? <DeliveryForm projectId={projectId} isRevision={project.status === ProjectStatus.revision_requested} /> : <FreelancerStatusPanel status={project.status} />}<div className="grid items-start gap-6 lg:grid-cols-2"><Card><CardHeader><CardTitle className="text-base">نسخه‌های تحویل</CardTitle></CardHeader><CardContent><Deliveries items={deliveries} /></CardContent></Card><Card><CardHeader><CardTitle className="text-base">درخواست‌های اصلاح</CardTitle></CardHeader><CardContent><Revisions items={revisions} /></CardContent></Card></div></div></AppShell>;
}

function FreelancerStatusPanel({ status }: { status: ProjectStatus }) {
  return <Card className="border-dashed"><CardContent className="flex items-start gap-3 py-5"><CircleAlert className="mt-0.5 shrink-0 text-muted-foreground" size={18} aria-hidden="true" /><div className="grid gap-1"><p className="font-medium">اقدام بعدی در دسترس نیست</p><p className="text-sm leading-6 text-muted-foreground">{getFreelancerProjectStatusMessage(status)}</p></div></CardContent></Card>;
}

async function getAllRevisions(projectId: string): Promise<ProjectRevisionRequestResponse[]> { const first = await serverGetPage<ProjectRevisionRequestResponse>(`projects/${projectId}/revisions`, { page: 1, page_size: 100 }); const rest = await Promise.all(Array.from({ length: Math.max(0, (first.meta?.total_pages ?? 1) - 1) }, (_, index) => serverGetPage<ProjectRevisionRequestResponse>(`projects/${projectId}/revisions`, { page: index + 2, page_size: 100 }))); return [first, ...rest].flatMap((page) => page.items); }
function Detail({ label, value }: { label: string; value: string }) { return <div className="grid gap-1"><dt className="text-muted-foreground">{label}</dt><dd className="font-medium">{value}</dd></div>; }
function Deliveries({ items }: { items: DeliveryResponse[] }) { if (items.length === 0) return <EmptyState icon={FileCheck2} title="هنوز تحویلی ثبت نشده است" className="py-8" />; return <ol className="divide-y">{[...items].sort((a, b) => b.version_no - a.version_no).map((item) => <li key={item.delivery_id} className="grid gap-2 py-4 first:pt-0 last:pb-0"><div className="flex flex-wrap items-center justify-between gap-2"><span className="font-medium">نسخه {formatNumber(item.version_no)}</span><DeliveryStatusBadge status={item.status} /></div><p className="text-sm leading-6">{item.delivery_note || 'یادداشتی ثبت نشده است.'}</p><div className="flex flex-wrap justify-between gap-2 text-xs text-muted-foreground"><span>{formatNumber(item.file_asset_ids.length)} فایل</span><time dateTime={item.submitted_at}>{formatDateTime(item.submitted_at)}</time></div></li>)}</ol>; }
function Revisions({ items }: { items: ProjectRevisionRequestResponse[] }) { if (items.length === 0) return <EmptyState icon={RotateCcw} title="درخواست اصلاحی ثبت نشده است" className="py-8" />; return <ol className="divide-y">{[...items].sort((a, b) => b.round_no - a.round_no).map((item) => <li key={item.revision_id} className="grid gap-2 py-4 first:pt-0 last:pb-0"><div className="flex flex-wrap items-center justify-between gap-2"><span className="font-medium">دور {formatNumber(item.round_no)}</span><span className="text-xs text-muted-foreground">{item.status}</span></div><p className="text-sm leading-6">{item.reason}</p><time className="text-xs text-muted-foreground" dateTime={item.requested_at}>{formatDateTime(item.requested_at)}</time></li>)}</ol>; }
