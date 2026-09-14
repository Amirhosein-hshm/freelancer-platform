import type { Metadata } from "next";
import Link from "next/link";
import { Star, UserPlus } from "lucide-react";
import type {
  FreelancerProfileResponse,
  PortfolioItemResponse,
  ResumeResponse,
} from "@/generated/api/models";
import { AppShell } from "@/components/shell/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { PageHeader } from "@/components/ui/page-header";
import { ApprovalAction } from "@/features/freelancer/approval-action";
import {
  APPROVAL_LABELS,
  LEVEL_LABELS,
} from "@/features/freelancer/freelancer-domain";
import { PortfolioManager } from "@/features/freelancer/portfolio-manager";
import { ProfileForm } from "@/features/freelancer/profile-form";
import { ResumeManager } from "@/features/freelancer/resume-manager";
import {
  getServerSessionUser,
  serverGet,
  serverGetPage,
  type ServerPage,
} from "@/lib/api/server";
import { formatDateTime } from "@/lib/format";
import { hasRole, ROLES } from "@/lib/auth/navigation";

export const metadata: Metadata = { title: "پروفایل فریلنسری" };

export default async function FreelancerPage() {
  const user = await getServerSessionUser();
  console.log("user", user);

  if (!hasRole(user, ROLES.freelancer))
    return (
      <AppShell user={user}>
        <ErrorState
          error={{
            status: 403,
            code: "permission_denied",
            message: "این بخش فقط برای نقش فریلنسر در دسترس است.",
            fields: {},
          }}
        />
      </AppShell>
    );
  const profileId = user.freelancer_profile_id;
  if (!profileId)
    return (
      <AppShell user={user}>
        <div className="mx-auto max-w-3xl">
          <EmptyState
            icon={UserPlus}
            title="پروفایل فریلنسری هنوز ساخته نشده است"
            description="برای استفاده از امکانات فریلنسری ابتدا پروفایل خود را بسازید."
            action={
              <Button asChild>
                <Link href="/freelancer/onboarding">شروع تکمیل پروفایل</Link>
              </Button>
            }
          />
        </div>
      </AppShell>
    );
  const [profile, resumes, portfolio] = await Promise.all([
    serverGet<FreelancerProfileResponse>(`freelancers/${profileId}`),
    getAllPages<ResumeResponse>(`freelancers/${profileId}/resume/versions`),
    getAllPages<PortfolioItemResponse>(`freelancers/${profileId}/portfolio`),
  ]);
  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-5xl gap-6">
        <PageHeader
          title={profile.display_name}
          description={
            profile.headline ??
            "پروفایل حرفه‌ای، رزومه و نمونه‌کارهای خود را مدیریت کنید."
          }
          actions={
            <div className="flex flex-wrap gap-2">
              <Button asChild variant="outline">
                <Link href="/freelancer/ratings">
                  <Star size={16} aria-hidden="true" />
                  امتیازها
                </Link>
              </Button>
              <ApprovalAction
                profileId={profileId}
                status={profile.approval_status}
              />
            </div>
          }
        />
        <Card>
          <CardHeader>
            <CardTitle className="text-base">وضعیت فریلنسری</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid gap-5 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <Status
                label="وضعیت تأیید"
                value={
                  <Badge>
                    {APPROVAL_LABELS[profile.approval_status] ??
                      profile.approval_status}
                  </Badge>
                }
              />
              <Status
                label="سطح"
                value={
                  profile.current_level
                    ? LEVEL_LABELS[profile.current_level]
                    : "تعیین نشده"
                }
              />
              <Status
                label="دسترسی به پروژه"
                value={profile.is_available ? "فعال" : "غیرفعال"}
              />
              <Status
                label="زمان تأیید"
                value={
                  profile.approved_at
                    ? formatDateTime(profile.approved_at)
                    : "تأیید نشده"
                }
              />
            </dl>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">اطلاعات پروفایل</CardTitle>
          </CardHeader>
          <CardContent>
            <ProfileForm profile={profile} />
          </CardContent>
        </Card>
        <ResumeManager profileId={profileId} resumes={resumes} />
        <PortfolioManager profileId={profileId} items={portfolio} />
      </div>
    </AppShell>
  );
}

function Status({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="grid gap-1">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-medium">{value}</dd>
    </div>
  );
}
async function getAllPages<T>(path: string): Promise<T[]> {
  const first = await serverGetPage<T>(path, { page: 1, page_size: 100 });
  const rest: ServerPage<T>[] = await Promise.all(
    Array.from(
      { length: Math.max(0, (first.meta?.total_pages ?? 1) - 1) },
      (_, index) => serverGetPage<T>(path, { page: index + 2, page_size: 100 }),
    ),
  );

  console.log("first======>");
  return [first, ...rest].flatMap((page) => page.items);
}
