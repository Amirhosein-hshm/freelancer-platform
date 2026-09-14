import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { AdminGetUserResponse } from '@/generated/api/models/adminGetUserResponse';
import type { ListRolesResponse } from '@/generated/api/models/listRolesResponse';
import { UserActions, RoleAssignment, UpdateUserForm } from '@/features/admin/user-management';

export default async function AdminUserDetailPage({ params }: { params: Promise<{ user_id: string }> }) {
  const user = await getServerSessionUser(); if (!hasRole(user, ROLES.admin)) redirect('/dashboard'); const { user_id } = await params;
  const [detail, roles] = await Promise.all([serverGet<AdminGetUserResponse>(`users/${user_id}`), serverGet<ListRolesResponse>('roles')]);
  return <AppShell user={user}><div className="mx-auto grid max-w-4xl gap-6"><PageHeader title={`${detail.first_name} ${detail.last_name}`} description={detail.email} backHref="/admin/users" backLabel="کاربران" /><UpdateUserForm userId={user_id} firstName={detail.first_name} lastName={detail.last_name} phone={detail.phone} /><div className="grid gap-3 rounded-xl border bg-card p-5 text-sm sm:grid-cols-2"><div><span className="text-muted-foreground">وضعیت</span><p className="font-medium">{detail.status}</p></div><div><span className="text-muted-foreground">نقش فعلی</span><p className="font-medium">{detail.roles.join('، ') || '—'}</p></div><div><span className="text-muted-foreground">تلفن</span><p className="font-medium">{detail.phone ?? '—'}</p></div><div><span className="text-muted-foreground">تأیید ایمیل</span><p className="font-medium">{detail.email_verified_at ?? '—'}</p></div></div><RoleAssignment userId={user_id} currentRoles={detail.roles} roles={roles.roles} /><UserActions userId={user_id} status={detail.status} /></div></AppShell>;
}
