import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { getServerSessionUser, serverGet } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { CategoryResponse } from '@/generated/api/models/categoryResponse';
import type { ListCategorySupervisorsResponse } from '@/generated/api/models/listCategorySupervisorsResponse';
import { DeleteCategoryAction, EditCategoryForm, SupervisorAssignment } from '@/features/admin/category-management';

export default async function CategoryDetailPage({ params }: { params: Promise<{ category_id: string }> }) {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) redirect('/dashboard');
  const { category_id } = await params;
  const [category, supervisors] = await Promise.all([
    serverGet<CategoryResponse>(`categories/${category_id}`),
    serverGet<ListCategorySupervisorsResponse>(`categories/${category_id}/supervisors`),
  ]);
  return <AppShell user={user}><div className="mx-auto grid max-w-4xl gap-6"><PageHeader title={category.name} description={category.description ?? undefined} backHref="/admin/categories" backLabel="دسته‌بندی‌ها" /><div className="flex justify-end"><DeleteCategoryAction categoryId={category_id} /></div><EditCategoryForm category={category} /><div className="grid gap-2 rounded-xl border bg-card p-5 text-sm sm:grid-cols-2"><div><span className="text-muted-foreground">کلید</span><p className="font-medium">{category.category_key}</p></div><div><span className="text-muted-foreground">slug</span><p className="font-medium">{category.slug}</p></div><div><span className="text-muted-foreground">وضعیت</span><p className="font-medium">{category.is_active ? 'فعال' : 'غیرفعال'}</p></div><div><span className="text-muted-foreground">ترتیب</span><p className="font-medium">{category.sort_order}</p></div></div><SupervisorAssignment categoryId={category_id} assignedIds={supervisors.supervisors.map((s) => s.supervisor_user_id)} /></div></AppShell>;
}
