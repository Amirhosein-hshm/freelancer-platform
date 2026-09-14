import type { Metadata } from "next";
import type { ProjectRevisionRequestResponse } from "@/generated/api/models";
import { AppShell } from "@/components/shell/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { getServerSessionUser, serverGet } from "@/lib/api/server";
import { formatDateTime, formatNumber } from "@/lib/format";

export const metadata: Metadata = { title: "جزئیات درخواست اصلاح" };

export default async function RevisionDetailsPage({
  params,
}: {
  params: Promise<{ project_id: string; revision_id: string }>;
}) {
  const { project_id: projectId, revision_id: revisionId } = await params;
  const [user, revision] = await Promise.all([
    getServerSessionUser(),
    serverGet<ProjectRevisionRequestResponse>(`revisions/${revisionId}`),
  ]);

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-3xl gap-6">
        <PageHeader
          title={`درخواست اصلاح دور ${formatNumber(revision.round_no)}`}
          description={revision.reason}
          backHref={`/projects/${projectId}`}
          backLabel="بازگشت به پروژه"
        />
        <Card>
          <CardHeader>
            <CardTitle className="text-base">جزئیات درخواست</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid gap-5 text-sm sm:grid-cols-2">
              <Detail label="وضعیت" value={revision.status} />
              <Detail
                label="زمان درخواست"
                value={formatDateTime(revision.requested_at)}
              />
              <Detail
                label="زمان رفع"
                value={
                  revision.resolved_at
                    ? formatDateTime(revision.resolved_at)
                    : "هنوز رفع نشده"
                }
              />
              <Detail
                label="شناسه تحویل"
                value={
                  revision.project_delivery_id ?? "مرتبط با تحویل مشخصی نیست"
                }
                mono
              />
              <Detail
                label="درخواست‌دهنده"
                value={revision.requested_by_user_id}
                mono
              />
              <Detail
                label="مخاطب درخواست"
                value={revision.requested_to_user_id ?? "تعیین نشده"}
                mono
              />
            </dl>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

function Detail({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="grid min-w-0 gap-1">
      <dt className="text-muted-foreground">{label}</dt>
      <dd
        className={
          mono ? "ltr-embedded truncate font-mono text-xs" : "font-medium"
        }
      >
        {value}
      </dd>
    </div>
  );
}
