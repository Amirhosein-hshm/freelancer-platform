import Link from "next/link";
import { redirect } from "next/navigation";
import { AppShell } from "@/components/shell/app-shell";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState } from "@/components/ui/empty-state";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { getServerSessionUser, serverGet } from "@/lib/api/server";
import { hasRole, ROLES } from "@/lib/auth/navigation";
import type { FreelancerProfileResponse } from "@/generated/api/models/freelancerProfileResponse";
import type { FreelancerApprovalStatus } from "@/generated/api/models/freelancerApprovalStatus";
import { CreateFreelancerProfileForm } from "@/features/admin/freelancer-management";

export default async function AdminFreelancersPage({
  searchParams,
}: {
  searchParams: Promise<{ status?: string; page?: string }>;
}) {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) redirect("/dashboard");
  const query = await searchParams;
  const status = (query.status || "pending") as FreelancerApprovalStatus;
  const result = await serverGet<FreelancerProfileResponse[]>(
    "admin/freelancers",
    { status, page: query.page ? Number(query.page) : 1, page_size: 25 },
  );

  console.log("result", result);
  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-6xl gap-6">
        <PageHeader
          title="مدیریت فریلنسرها"
          description="تأیید، رد و سطح‌بندی بر اساس backend."
          actions={
            <Link href="/admin" className="text-sm text-primary">
              بازگشت
            </Link>
          }
        />
        <CreateFreelancerProfileForm />
        <form method="get" className="flex gap-2">
          <select
            name="status"
            defaultValue={status}
            className="h-9 rounded-md border bg-background px-3 text-sm"
          >
            <option value="pending">pending</option>
            <option value="approved">approved</option>
            <option value="rejected">rejected</option>
            <option value="suspended">suspended</option>
          </select>
          <button
            className="h-9 rounded-md bg-primary px-4 text-sm text-primary-foreground"
            type="submit"
          >
            اعمال فیلتر
          </button>
        </form>
        {result.length === 0 ? (
          <EmptyState
            title="پروفایلی پیدا نشد"
            description="برای این وضعیت فریلنسی وجود ندارد."
          />
        ) : (
          <div className="overflow-hidden rounded-xl border bg-card">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>پروفایل</TableHead>
                  <TableHead>وضعیت</TableHead>
                  <TableHead>سطح</TableHead>
                  <TableHead>دسترسی</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.map((profile) => (
                  <TableRow key={profile.profile_id}>
                    <TableCell>
                      <Link
                        className="text-primary hover:underline"
                        href={`/admin/freelancers/${profile.profile_id}`}
                      >
                        {profile.display_name}
                      </Link>
                    </TableCell>
                    <TableCell>{profile.approval_status}</TableCell>
                    <TableCell>{profile.current_level ?? "—"}</TableCell>
                    <TableCell>
                      {profile.is_available ? "فعال" : "غیرفعال"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </AppShell>
  );
}
