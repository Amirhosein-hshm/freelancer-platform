import type { Metadata } from "next";
import Link from "next/link";
import type {
  DeliveryResponse,
  ProjectDetailsResponse,
  ProjectRevisionRequestResponse,
  ReviewResponse,
} from "@/generated/api/models";
import { AppShell } from "@/components/shell/app-shell";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { DeliveryReviewActions } from "@/features/projects/delivery-review-actions";
import { DeliveryStatusBadge } from "@/features/projects/status-badges";
import {
  getServerSessionUser,
  serverGet,
  serverGetOptional,
  serverGetPage,
} from "@/lib/api/server";
import { formatDateTime, formatNumber } from "@/lib/format";

export const metadata: Metadata = { title: "بررسی پروژه" };

export default async function SupervisorProjectPage({
  params,
}: {
  params: Promise<{ project_id: string }>;
}) {
  const { project_id } = await params;
  const [user, details, revisions] = await Promise.all([
    getServerSessionUser(),
    serverGet<ProjectDetailsResponse>(`projects/${project_id}`),
    serverGetPage<ProjectRevisionRequestResponse>(
      `projects/${project_id}/revisions`,
      { page: 1, page_size: 100 },
    ),
  ]);
  const reviews = await Promise.all(
    details.deliveries.map((delivery) =>
      serverGetOptional<ReviewResponse>(
        `deliveries/${delivery.delivery_id}/review`,
      ),
    ),
  );
  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-5xl gap-6">
        <PageHeader
          title={details.project.title}
          description={`کد پروژه: ${details.project.project_code}`}
          backHref="/reviews"
          backLabel="صف بازبینی"
        />
        <Card>
          <CardHeader>
            <CardTitle className="text-base">تحویلی‌ها</CardTitle>
          </CardHeader>
          <CardContent>
            {details.deliveries.length === 0 ? (
              <EmptyState title="تحویلی ثبت نشده است" description="پس از ارسال تحویل توسط فریلنسر، نسخه‌ها برای بررسی در اینجا نمایش داده می‌شوند." />
            ) : (
              <div className="grid gap-4">
                {details.deliveries
                  .slice()
                  .sort((a, b) => b.version_no - a.version_no)
                  .map((delivery) => (
                    <DeliveryReviewCard
                      key={delivery.delivery_id}
                      delivery={delivery}
                      review={
                        reviews.find(
                          (item) =>
                            item?.project_delivery_id === delivery.delivery_id,
                        ) ?? null
                      }
                      projectId={project_id}
                    />
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">درخواست‌های اصلاح</CardTitle>
          </CardHeader>
          <CardContent>
            {revisions.items.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                درخواستی ثبت نشده است.
              </p>
            ) : (
              <ul className="grid gap-3">
                {revisions.items.map((item) => (
                  <li
                    key={item.revision_id}
                    className="border-b border-border pb-3 text-sm last:border-0 last:pb-0"
                  >
                    <p className="font-medium">
                      دور {formatNumber(item.round_no)}: {item.reason}
                    </p>
                    <p className="mt-1 text-muted-foreground">
                      {formatDateTime(item.requested_at)}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function DeliveryReviewCard({
  delivery,
  review,
  projectId,
}: {
  delivery: DeliveryResponse;
  review: ReviewResponse | null;
  projectId: string;
}) {
  const reviewable =
    delivery.status === "submitted" || delivery.status === "under_review";
  return (
    <div className="grid gap-3 rounded-lg border border-border p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-medium">
          نسخه {formatNumber(delivery.version_no)}
        </h3>
        <DeliveryStatusBadge status={delivery.status} />
      </div>
      <p className="text-sm leading-6">
        {delivery.delivery_note || "یادداشتی ثبت نشده است."}
      </p>
      <p className="text-xs text-muted-foreground">
        {formatNumber(delivery.file_asset_ids.length)} فایل ·{" "}
        {formatDateTime(delivery.submitted_at)}
      </p>
      {review ? (
        <p className="text-sm text-muted-foreground">
          تصمیم ثبت‌شده: {review.decision}
        </p>
      ) : null}
      {reviewable && !review ? (
        <DeliveryReviewActions
          deliveryId={delivery.delivery_id}
          projectId={projectId}
        />
      ) : null}
      <Link
        className="text-sm text-primary hover:underline"
        href={`/projects/${projectId}`}
      >
        مشاهده جزئیات کامل پروژه
      </Link>
    </div>
  );
}
