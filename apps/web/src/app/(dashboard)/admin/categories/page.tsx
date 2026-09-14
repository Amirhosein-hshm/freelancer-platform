import Link from 'next/link';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { EmptyState } from '@/components/ui/empty-state';
import { PageHeader } from '@/components/ui/page-header';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { CategoryResponse } from '@/generated/api/models/categoryResponse';
import { CreateCategoryForm } from '@/features/admin/category-management';

export const metadata = { title: 'دسته‌بندی‌ها' };

export default async function AdminCategoriesPage() {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) redirect('/dashboard');
  const categories = await serverGetPage<CategoryResponse>('categories');

  return <AppShell user={user}>
    <div className="mx-auto grid max-w-6xl gap-6">
      <PageHeader title="دسته‌بندی‌ها" description="دسته‌بندی تعیین‌کننده صف و واجد شرایط بودن ناظران در backend است." actions={<Link href="/admin" className="text-sm text-primary hover:underline">بازگشت به مدیریت</Link>} />
      <CreateCategoryForm />
      {categories.items.length === 0 ? <EmptyState title="دسته‌بندی‌ای ثبت نشده است" description="داده‌ای از سرور برای نمایش وجود ندارد." /> : <div className="overflow-hidden rounded-xl border bg-card"><Table><TableHeader><TableRow><TableHead>نام</TableHead><TableHead>کلید</TableHead><TableHead>وضعیت</TableHead><TableHead>ترتیب</TableHead></TableRow></TableHeader><TableBody>{categories.items.map((category) => <TableRow key={category.category_id}><TableCell className="font-medium"><Link className="text-primary hover:underline" href={`/admin/categories/${category.category_id}`}>{category.name}</Link></TableCell><TableCell>{category.category_key}</TableCell><TableCell>{category.is_active ? 'فعال' : 'غیرفعال'}</TableCell><TableCell>{category.sort_order}</TableCell></TableRow>)}</TableBody></Table></div>}
    </div>
  </AppShell>;
}
