'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { ActionDialog } from '@/components/ui/action-dialog';
import { useCreateCategory, useUpdateCategory, useDeleteCategory, useAssignSupervisor, useRemoveSupervisor, getListCategorySupervisorsQueryKey } from '@/generated/api/category/category';
import { useAdminListUsers } from '@/generated/api/iam-admin/iam-admin';

const categorySchema = z.object({ name: z.string().min(1), slug: z.string().min(1), category_key: z.string().min(1), description: z.string().optional(), parent_category_id: z.string().optional(), sort_order: z.number().int().optional() });
type CategoryValues = z.infer<typeof categorySchema>;

export function CreateCategoryForm() {
  const router = useRouter();
  const form = useForm<CategoryValues>({ resolver: zodResolver(categorySchema), defaultValues: { name: '', slug: '', category_key: '', description: '', sort_order: 0 } });
  const mutation = useCreateCategory();
  const submit = form.handleSubmit(async (values) => { try { await mutation.mutateAsync({ data: { name: values.name, slug: values.slug, category_key: values.category_key, description: values.description || null, parent_category_id: values.parent_category_id || null, sort_order: values.sort_order } }); toast.success('دسته‌بندی ایجاد شد.'); form.reset(); router.refresh(); } catch { toast.error('ایجاد دسته‌بندی انجام نشد.'); } });
  return <form onSubmit={submit} className="grid gap-3 rounded-xl border bg-card p-5"><h2 className="font-semibold">دسته‌بندی جدید</h2><div className="grid gap-3 sm:grid-cols-2"><Input placeholder="نام" aria-invalid={!!form.formState.errors.name} {...form.register('name')} /><Input placeholder="slug" {...form.register('slug')} /><Input placeholder="کلید دسته‌بندی" {...form.register('category_key')} /><Input type="number" placeholder="ترتیب نمایش" {...form.register('sort_order', { valueAsNumber: true })} /></div><Textarea placeholder="توضیحات (اختیاری)" {...form.register('description')} /><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? 'در حال ایجاد…' : 'ایجاد دسته‌بندی'}</Button></form>;
}

export function EditCategoryForm({ category }: { category: { category_id: string; name: string; slug: string; description: string | null; sort_order: number } }) {
  const router = useRouter();
  const editSchema = categorySchema.omit({ category_key: true, parent_category_id: true });
  const form = useForm<z.infer<typeof editSchema>>({ resolver: zodResolver(editSchema), defaultValues: { name: category.name, slug: category.slug, description: category.description ?? '', sort_order: category.sort_order } });
  const mutation = useUpdateCategory();
  return <form onSubmit={form.handleSubmit(async (values) => { try { await mutation.mutateAsync({ categoryId: category.category_id, data: { name: values.name, slug: values.slug, description: values.description || null, sort_order: values.sort_order } }); toast.success('دسته‌بندی به‌روزرسانی شد.'); router.refresh(); } catch { toast.error('به‌روزرسانی دسته‌بندی انجام نشد.'); } })} className="grid gap-3 rounded-xl border bg-card p-5"><h2 className="font-semibold">ویرایش دسته‌بندی</h2><div className="grid gap-3 sm:grid-cols-2"><Input {...form.register('name')} /><Input {...form.register('slug')} /><Input type="number" {...form.register('sort_order', { valueAsNumber: true })} /></div><Textarea {...form.register('description')} /><Button type="submit" disabled={mutation.isPending}>ذخیره تغییرات</Button></form>;
}

export function DeleteCategoryAction({ categoryId }: { categoryId: string }) {
  const router = useRouter(); const mutation = useDeleteCategory();
  return <ActionDialog trigger={<Button type="button" variant="destructive" disabled={mutation.isPending}>حذف دسته‌بندی</Button>} title="حذف دسته‌بندی" description="این دسته‌بندی حذف می‌شود و ممکن است پروژه‌ها یا قالب‌های وابسته دیگر قابل استفاده نباشند." confirmLabel="حذف دسته‌بندی" destructive onConfirm={async () => { await mutation.mutateAsync({ categoryId }); }} onDone={() => { toast.success('دسته‌بندی حذف شد.'); router.replace('/admin/categories'); }} />;
}

export function SupervisorAssignment({ categoryId, assignedIds }: { categoryId: string; assignedIds: string[] }) {
  const router = useRouter(); const client = useQueryClient();
  const users = useAdminListUsers({ role: 'supervisor', page_size: 100 });
  const assign = useAssignSupervisor(); const remove = useRemoveSupervisor();
  const available = users.data && 'data' in users.data && 'data' in users.data.data ? users.data.data.data.users.filter((u) => !assignedIds.includes(u.user_id)) : [];
  const form = useForm<{ supervisor_user_id: string }>({ resolver: zodResolver(z.object({ supervisor_user_id: z.string().min(1) })), defaultValues: { supervisor_user_id: '' } });
  async function assignUser(values: { supervisor_user_id: string }) { try { await assign.mutateAsync({ categoryId, data: values }); toast.success('ناظر اختصاص داده شد.'); form.reset(); await client.invalidateQueries({ queryKey: getListCategorySupervisorsQueryKey(categoryId) }); router.refresh(); } catch { toast.error('اختصاص ناظر انجام نشد.'); } }
  async function removeUser(id: string) { try { await remove.mutateAsync({ categoryId, supervisorUserId: id }); toast.success('ناظر حذف شد.'); await client.invalidateQueries({ queryKey: getListCategorySupervisorsQueryKey(categoryId) }); router.refresh(); } catch { toast.error('حذف ناظر انجام نشد.'); } }
  return <div className="grid gap-4 rounded-xl border bg-card p-5"><div><h2 className="font-semibold">ناظران دسته‌بندی</h2><p className="mt-1 text-sm text-muted-foreground">این اختصاص، واجد شرایط بودن ناظر برای صف backend را کنترل می‌کند.</p></div><form onSubmit={form.handleSubmit(assignUser)} className="flex flex-wrap gap-2"><select {...form.register('supervisor_user_id')} className="h-9 min-w-64 rounded-md border bg-background px-3 text-sm" defaultValue=""><option value="">انتخاب ناظر</option>{available.map((u) => <option key={u.user_id} value={u.user_id}>{u.first_name} {u.last_name} · {u.email}</option>)}</select><Button type="submit" disabled={assign.isPending || available.length === 0}>اختصاص ناظر</Button></form>{assignedIds.length === 0 ? <p className="text-sm text-muted-foreground">ناظری اختصاص داده نشده است.</p> : <ul className="grid gap-2">{assignedIds.map((id) => <li key={id} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"><span>{id}</span><ActionDialog trigger={<Button type="button" variant="destructive" size="sm" disabled={remove.isPending}>حذف</Button>} title="حذف ناظر" description="این ناظر از دسته‌بندی حذف می‌شود." confirmLabel="حذف ناظر" destructive onConfirm={() => removeUser(id)} /></li>)}</ul>}</div>;
}
