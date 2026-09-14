import Link from 'next/link';
import { ArrowLeft, ClipboardCheck, FolderKanban } from 'lucide-react';
import type { PaginationMeta, ProjectResponse, ReviewResponse } from '@/generated/api/models';
import { EmptyState } from '@/components/ui/empty-state';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDateTime } from '@/lib/format';
import type { ListQuery } from '@/lib/url/use-list-query';
import { getProjectSupervisor } from '@/features/projects/project-domain';

const statusLabels: Record<string, string> = {
  pending: 'در انتظار بررسی',
  submitted: 'ارسال‌شده',
  under_review: 'در حال بررسی',
  under_supervisor_review: 'در صف بازبینی ناظر',
  completed: 'تکمیل‌شده',
};

export function PendingReviewList({ items, meta, query }: { items: ReviewResponse[]; meta: PaginationMeta; query: ListQuery }) {
  if (items.length === 0) return <EmptyState icon={ClipboardCheck} title="صف بازبینی خالی است" description="در حال حاضر تحویلی برای بررسی شما وجود ندارد." />;
  return <div className="grid gap-3">{items.map((item) => <Card key={item.review_id}>
    <CardContent className="flex flex-wrap items-center justify-between gap-4 p-5">
      <div className="grid gap-1.5"><CardTitle className="text-base">تحویل پروژه {item.project_id}</CardTitle><p className="text-sm text-muted-foreground">ثبت‌شده در {item.reviewed_at ? formatDateTime(item.reviewed_at) : 'صف بازبینی'}</p><Badge variant="secondary">{statusLabels[item.decision] ?? item.decision}</Badge></div>
      <Link className="inline-flex min-h-10 items-center gap-1.5 rounded-md border border-primary/40 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" href={`/reviews/${item.project_id}`}><ArrowLeft size={16} aria-hidden="true" />مشاهده پروژه</Link>
    </CardContent>
  </Card>)}<PaginationBar meta={meta} query={query} itemNoun="بازبینی" /></div>;
}

export function ScopedProjectList({ items, meta, query }: { items: ProjectResponse[]; meta: PaginationMeta; query: ListQuery }) {
  if (items.length === 0) return <EmptyState icon={FolderKanban} title="پروژه‌ای در حوزه شما نیست" description="پروژه‌های دسته‌بندی‌شده برای شما اینجا نمایش داده می‌شوند." />;
  return <div className="grid gap-3">{items.map((project) => <Card key={project.project_id}>
    <CardHeader className="flex flex-row items-start justify-between gap-3"><div><CardTitle className="text-base">{project.title}</CardTitle><p className="mt-1 text-sm text-muted-foreground">کد {project.project_code} · {formatDateTime(project.created_at)}</p></div><Badge variant="outline">{statusLabels[project.status] ?? project.status}</Badge></CardHeader>
    <CardContent className="flex items-center justify-between gap-3 pt-0"><span className="text-sm text-muted-foreground">{formatScopedSupervisor(project)}</span><Link className="text-sm font-medium text-primary hover:underline" href={`/reviews/${project.project_id}`}>جزئیات</Link></CardContent>
  </Card>)}<PaginationBar meta={meta} query={query} itemNoun="پروژه" /> </div>;
}

function formatScopedSupervisor(project: ProjectResponse): string {
  const supervisor = getProjectSupervisor(project);
  return supervisor ? `${supervisor.first_name} ${supervisor.last_name} · ${supervisor.email}` : 'حوزه نظارت شما · ناظری از طریق دسته‌بندی تخصیص داده نشده است';
}
