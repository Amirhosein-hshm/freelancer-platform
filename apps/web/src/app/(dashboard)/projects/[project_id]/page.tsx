import type { Metadata } from 'next';
import Link from 'next/link';
import { FileCheck2, History, Inbox, MessageSquareText, Pencil, RotateCcw } from 'lucide-react';
import type { ReactNode } from 'react';
import type {
  ApplicationResponse,
  CustomerReviewResponse,
  DeliveryResponse,
  ProjectDetailsResponse,
  ProjectRatingResponse,
  ProjectRevisionRequestResponse,
  ReviewResponse,
  ProjectStatus,
  ProjectStatusHistoryResponse,
} from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { PageHeader } from '@/components/ui/page-header';
import {
  FREELANCER_LEVEL_LABELS,
  PROJECT_PRIORITY_LABELS,
  PROJECT_STATUS_LABELS,
  PROJECT_VISIBILITY_LABELS,
  canEditDraft,
  canReviewApplications,
  canSubmitCustomerReview,
  formatBudget,
  getProjectSupervisor,
} from '@/features/projects/project-domain';
import {
  ApplicationStatusBadge,
  DeliveryStatusBadge,
  ProjectStatusBadge,
} from '@/features/projects/status-badges';
import { getServerSessionUser, serverGet, serverGetOptional, serverGetPage } from '@/lib/api/server';
import { formatDate, formatDateTime, formatNumber } from '@/lib/format';
import { ProjectActions } from '@/features/projects/project-actions';
import { ApplicationReviewActions } from '@/features/projects/application-review-actions';
import { DeliveryReviewActions } from '@/features/projects/delivery-review-actions';
import { CustomerReviewActions } from '@/features/projects/customer-review-actions';
import { ProjectRating } from '@/features/projects/project-rating';

export const metadata: Metadata = { title: 'جزئیات پروژه' };

const HISTORY_PAGE_SIZE = 100;

export default async function ProjectDetailsPage({
  params,
}: {
  params: Promise<{ project_id: string }>;
}) {
  const { project_id: projectId } = await params;
  const [user, details, statusHistory, revisions, projectRating, customerReviews] = await Promise.all([
    getServerSessionUser(),
    serverGet<ProjectDetailsResponse>(`projects/${projectId}`),
    serverGetPage<ProjectStatusHistoryResponse>(`projects/${projectId}/status-history`, {
      page: 1,
      page_size: HISTORY_PAGE_SIZE,
    }),
    serverGetPage<ProjectRevisionRequestResponse>(`projects/${projectId}/revisions`, {
      page: 1,
      page_size: HISTORY_PAGE_SIZE,
    }),
    serverGetOptional<ProjectRatingResponse>(`feedback/projects/${projectId}/rating`),
    serverGetOptional<{ project_id: string; reviews: CustomerReviewResponse[] }>(
      `feedback/projects/${projectId}/reviews`,
    ),
  ]);
  const { project, applications, deliveries } = details;
  const supervisorReviews = await Promise.all(
    deliveries.map((delivery) =>
      serverGetOptional<ReviewResponse>(`deliveries/${delivery.delivery_id}/review`),
    ),
  );

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-6xl gap-6">
        <PageHeader
          backHref="/projects"
          backLabel="بازگشت به پروژه‌ها"
          title={project.title}
          description={project.description}
          eyebrow={
            <>
              <ProjectStatusBadge status={project.status} />
              <span className="ltr-embedded font-mono text-xs text-muted-foreground">
                {project.project_code}
              </span>
            </>
          }
          actions={
            <>
              {canEditDraft(project.status) ? (
                <Button asChild variant="outline">
                  <Link href={`/projects/${project.project_id}/edit`}>
                    <Pencil size={16} aria-hidden="true" />
                    ویرایش پیش‌نویس
                  </Link>
                </Button>
              ) : null}
              <ProjectActions projectId={project.project_id} status={project.status} />
              {canSubmitCustomerReview(project.status) ? <CustomerReviewActions projectId={project.project_id} /> : null}
            </>
          }
        />

        <Card>
          <CardHeader>
            <CardTitle className="text-base">مشخصات پروژه</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid gap-x-8 gap-y-5 text-sm sm:grid-cols-2 lg:grid-cols-3">
              <Detail label="بودجه" value={formatBudget(project.budget)} />
              <Detail label="اولویت" value={PROJECT_PRIORITY_LABELS[project.priority]} />
              <Detail label="نحوه نمایش" value={PROJECT_VISIBILITY_LABELS[project.visibility]} />
              <Detail
                label="سطح مورد نیاز"
                value={project.required_level ? FREELANCER_LEVEL_LABELS[project.required_level] : 'تعیین نشده'}
              />
              <Detail label="مهلت درخواست" value={project.application_deadline ? formatDateTime(project.application_deadline) : 'تعیین نشده'} />
              <Detail label="تاریخ ایجاد" value={formatDateTime(project.created_at)} />
              <Detail label="شناسه دسته‌بندی" value={project.category_id} mono />
              <Detail label="شناسه پروژه" value={project.project_id} mono />
              <Detail label="ناظر" value={formatSupervisor(project)} />
            </dl>
          </CardContent>
        </Card>

        <div className="grid items-start gap-6 xl:grid-cols-2">
          <CollectionCard title="درخواست‌های همکاری" count={applications.length}>
            <Applications items={applications} projectId={project.project_id} reviewable={canReviewApplications(project.status)} />
          </CollectionCard>
          <CollectionCard title="تحویل‌ها" count={deliveries.length}>
            <Deliveries
              items={deliveries}
              projectId={project.project_id}
              reviewable={canSubmitCustomerReview(project.status)}
              supervisorReviews={supervisorReviews}
              customerReviews={customerReviews?.reviews ?? []}
            />
          </CollectionCard>
          <CollectionCard
            title="تاریخچه وضعیت"
            count={statusHistory.meta?.total_items ?? statusHistory.items.length}
            truncated={(statusHistory.meta?.total_pages ?? 1) > 1}
          >
            <StatusHistory items={statusHistory.items} />
          </CollectionCard>
          <CollectionCard
            title="درخواست‌های اصلاح"
            count={revisions.meta?.total_items ?? revisions.items.length}
            truncated={(revisions.meta?.total_pages ?? 1) > 1}
          >
            <Revisions items={revisions.items} />
          </CollectionCard>
        </div>

        {project.status === 'completed' ? (
          <ProjectRating projectId={project.project_id} rating={projectRating?.rating ?? null} />
        ) : null}
      </div>
    </AppShell>
  );
}

function formatSupervisor(project: ProjectDetailsResponse['project']): string {
  const supervisor = getProjectSupervisor(project);
  return supervisor ? `${supervisor.first_name} ${supervisor.last_name} · ${supervisor.email}` : 'ناظری از طریق دسته‌بندی تخصیص داده نشده است';
}

function Detail({ label, value, mono = false }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="grid min-w-0 gap-1">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={mono ? 'ltr-embedded truncate font-mono text-xs' : 'font-medium'} title={mono ? value : undefined}>
        {value}
      </dd>
    </div>
  );
}

function CollectionCard({
  title,
  count,
  truncated = false,
  children,
}: {
  title: string;
  count: number;
  truncated?: boolean;
  children: ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between gap-3 text-base">
          <span>{title}</span>
          <span className="text-sm font-normal text-muted-foreground">{formatNumber(count)}</span>
        </CardTitle>
        {truncated ? (
          <p className="text-xs leading-5 text-muted-foreground">این صفحه {formatNumber(HISTORY_PAGE_SIZE)} مورد نخست پاسخ سرور را نمایش می‌دهد.</p>
        ) : null}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function Applications({ items, projectId, reviewable }: { items: ApplicationResponse[]; projectId: string; reviewable: boolean }) {
  if (items.length === 0) return <EmptyState icon={Inbox} title="هنوز درخواستی ثبت نشده است" className="py-8" />;
  return (
    <ul className="divide-y">
      {items.map((item) => (
        <li key={item.application_id} className="grid gap-3 py-4 first:pt-0 last:pb-0">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <ApplicationStatusBadge status={item.status} />
            <time className="text-xs text-muted-foreground" dateTime={item.applied_at}>{formatDateTime(item.applied_at)}</time>
          </div>
          <p className="text-sm leading-6">{item.cover_letter || 'متن معرفی ثبت نشده است.'}</p>
          <div className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span>مبلغ پیشنهادی: {item.proposed_amount ?? 'تعیین نشده'}</span>
            <span>زمان پیشنهادی: {item.proposed_days === null ? 'تعیین نشده' : `${formatNumber(item.proposed_days)} روز`}</span>
          </div>
          {reviewable && (item.status === 'applied' || item.status === 'shortlisted') ? (
            <ApplicationReviewActions projectId={projectId} applicationId={item.application_id} />
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function Deliveries({
  items,
  projectId,
  reviewable,
  supervisorReviews,
  customerReviews,
}: {
  items: DeliveryResponse[];
  projectId: string;
  reviewable: boolean;
  supervisorReviews: (ReviewResponse | null)[];
  customerReviews: CustomerReviewResponse[];
}) {
  if (items.length === 0) return <EmptyState icon={FileCheck2} title="هنوز تحویلی ثبت نشده است" className="py-8" />;
  return (
    <ul className="divide-y">
      {items.map((item, index) => (
        <li key={item.delivery_id} className="grid gap-3 py-4 first:pt-0 last:pb-0">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <DeliveryStatusBadge status={item.status} />
              <span className="text-sm font-medium">نسخه {formatNumber(item.version_no)}</span>
            </div>
            <time className="text-xs text-muted-foreground" dateTime={item.submitted_at}>{formatDateTime(item.submitted_at)}</time>
          </div>
          <p className="text-sm leading-6">{item.delivery_note || 'یادداشتی برای تحویل ثبت نشده است.'}</p>
          <p className="text-xs text-muted-foreground">{formatNumber(item.file_asset_ids.length)} فایل پیوست</p>
          {supervisorReviews[index] ? (
            <ReviewSummary
              label="بازبینی ناظر"
              decision={supervisorReviews[index].decision}
              note={supervisorReviews[index].reject_reason ?? supervisorReviews[index].notes}
              reviewedAt={supervisorReviews[index].reviewed_at}
            />
          ) : null}
          {customerReviews
            .filter((review) => review.project_delivery_id === item.delivery_id)
            .map((review) => (
              <ReviewSummary
                key={review.review_id}
                label="بازبینی مشتری"
                decision={review.decision}
                note={review.comment}
                reviewedAt={review.reviewed_at}
              />
            ))}
          {reviewable && (item.status === 'submitted' || item.status === 'under_review') ? <DeliveryReviewActions deliveryId={item.delivery_id} projectId={projectId} /> : null}
        </li>
      ))}
    </ul>
  );
}

function StatusHistory({ items }: { items: ProjectStatusHistoryResponse[] }) {
  if (items.length === 0) return <EmptyState icon={History} title="تاریخچه وضعیتی ثبت نشده است" className="py-8" />;
  return (
    <ol className="divide-y">
      {items.map((item) => (
        <li key={item.history_id} className="grid gap-2 py-4 first:pt-0 last:pb-0">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm font-medium">
              {item.from_status ? `${statusLabel(item.from_status)} ← ` : ''}{statusLabel(item.to_status)}
            </p>
            <time className="text-xs text-muted-foreground" dateTime={item.changed_at}>{formatDateTime(item.changed_at)}</time>
          </div>
          {item.reason ? <p className="text-sm leading-6 text-muted-foreground">{item.reason}</p> : null}
        </li>
      ))}
    </ol>
  );
}

function Revisions({ items }: { items: ProjectRevisionRequestResponse[] }) {
  if (items.length === 0) return <EmptyState icon={RotateCcw} title="درخواست اصلاحی ثبت نشده است" className="py-8" />;
  return (
    <ol className="divide-y">
      {items.map((item) => (
        <li key={item.revision_id} className="grid gap-2 py-4 first:pt-0 last:pb-0">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="flex items-center gap-2 text-sm font-medium"><MessageSquareText size={15} aria-hidden="true" />دور {formatNumber(item.round_no)}</p>
            <time className="text-xs text-muted-foreground" dateTime={item.requested_at}>{formatDate(item.requested_at)}</time>
          </div>
          <p className="text-sm leading-6">{item.reason}</p>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="text-xs text-muted-foreground">وضعیت: {item.status}</p>
            <Button asChild variant="ghost" size="sm">
              <Link href={`/projects/${item.project_id}/revisions/${item.revision_id}`}>مشاهده جزئیات</Link>
            </Button>
          </div>
        </li>
      ))}
    </ol>
  );
}

function statusLabel(status: string): string {
  return PROJECT_STATUS_LABELS[status as ProjectStatus] ?? status;
}

function ReviewSummary({
  label,
  decision,
  note,
  reviewedAt,
}: {
  label: string;
  decision: string;
  note: string | null;
  reviewedAt: string | null;
}) {
  return (
    <div className="grid gap-1 rounded-lg border border-border bg-muted/30 p-3 text-sm">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-medium">{label}: {decision}</span>
        {reviewedAt ? <time className="text-xs text-muted-foreground" dateTime={reviewedAt}>{formatDateTime(reviewedAt)}</time> : null}
      </div>
      {note ? <p className="leading-6 text-muted-foreground">{note}</p> : null}
    </div>
  );
}
