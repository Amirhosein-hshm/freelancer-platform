import Link from 'next/link';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState } from '@/components/ui/empty-state';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { AdminListUsersResponse } from '@/generated/api/models/adminListUsersResponse';
import { CreateUserForm } from '@/features/admin/user-management';

export default async function AdminUsersPage({ searchParams }: { searchParams: Promise<{ search?: string; status?: string; role?: string; page?: string }> }) {
  const user = await getServerSessionUser(); if (!hasRole(user, ROLES.admin)) redirect('/dashboard'); const query = await searchParams;
  const result = await serverGet<AdminListUsersResponse>('users', { search: query.search, status: query.status, role: query.role, page: query.page ? Number(query.page) : 1, page_size: 25 });
  return <AppShell user={user}><div className="mx-auto grid max-w-6xl gap-6"><PageHeader title="کاربران و دسترسی‌ها" description="وضعیت و نقش‌ها توسط backend تعیین می‌شوند." actions={<Link href="/admin" className="text-sm text-primary hover:underline">بازگشت به مدیریت</Link>} /><form className="flex flex-wrap gap-2" method="get"><Input name="search" defaultValue={query.search} placeholder="جست‌وجوی نام یا ایمیل" className="max-w-sm" /><select name="status" defaultValue={query.status ?? ''} className="h-9 rounded-md border bg-background px-3 text-sm"><option value="">همه وضعیت‌ها</option><option value="pending">pending</option><option value="active">active</option><option value="blocked">blocked</option><option value="archived">archived</option></select><Input name="role" defaultValue={query.role} placeholder="نقش" className="w-36" /><button className="h-9 rounded-md bg-primary px-4 text-sm text-primary-foreground" type="submit">اعمال فیلتر</button></form><CreateUserForm />{result.users.length === 0 ? <EmptyState title="کاربری پیدا نشد" description="با فیلترهای دیگر دوباره تلاش کنید." /> : <div className="overflow-hidden rounded-xl border bg-card"><Table><TableHeader><TableRow><TableHead>کاربر</TableHead><TableHead>ایمیل</TableHead><TableHead>وضعیت</TableHead><TableHead>عملیات</TableHead></TableRow></TableHeader><TableBody>{result.users.map((item) => <TableRow key={item.user_id}><TableCell><Link className="text-primary hover:underline" href={`/admin/users/${item.user_id}`}>{item.first_name} {item.last_name}</Link></TableCell><TableCell>{item.email}</TableCell><TableCell>{item.status}</TableCell><TableCell><Link className="text-sm text-primary hover:underline" href={`/admin/users/${item.user_id}`}>مشاهده</Link></TableCell></TableRow>)}</TableBody></Table></div>}</div></AppShell>;
}
