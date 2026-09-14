'use client';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ActionDialog } from '@/components/ui/action-dialog';
import { useAdminCreateUser, useAdminUpdateUser, useActivateUser, useBlockUser, useAdminDeleteUser, useAssignRole, useRemoveRole } from '@/generated/api/iam-admin/iam-admin';
import type { RoleResponse } from '@/generated/api/models/roleResponse';

const createSchema = z.object({ email: z.string().email(), password: z.string().min(8), first_name: z.string().min(1), last_name: z.string().min(1) });
const updateSchema = z.object({ first_name: z.string().optional(), last_name: z.string().optional(), phone: z.string().optional() });

export function UpdateUserForm({ userId, firstName, lastName, phone }: { userId: string; firstName: string; lastName: string; phone?: string | null }) { const router = useRouter(); const form = useForm<z.infer<typeof updateSchema>>({ resolver: zodResolver(updateSchema), defaultValues: { first_name: firstName, last_name: lastName, phone: phone ?? '' } }); const mutation = useAdminUpdateUser(); return <form onSubmit={form.handleSubmit(async (v) => { try { await mutation.mutateAsync({ userId, data: { first_name: v.first_name || null, last_name: v.last_name || null, phone: v.phone || null } }); toast.success('اطلاعات کاربر به‌روزرسانی شد.'); router.refresh(); } catch { toast.error('به‌روزرسانی کاربر انجام نشد.'); } })} className="grid gap-3 rounded-xl border bg-card p-5"><h2 className="font-semibold">ویرایش اطلاعات</h2><div className="grid gap-3 sm:grid-cols-3"><Input {...form.register('first_name')} /><Input {...form.register('last_name')} /><Input {...form.register('phone')} /></div><Button type="submit" disabled={mutation.isPending}>ذخیره اطلاعات</Button></form>; }

export function CreateUserForm() {
  const router = useRouter(); const form = useForm<z.infer<typeof createSchema>>({ resolver: zodResolver(createSchema), defaultValues: { email: '', password: '', first_name: '', last_name: '' } }); const mutation = useAdminCreateUser();
  return <form onSubmit={form.handleSubmit(async (data) => { try { await mutation.mutateAsync({ data }); toast.success('کاربر ایجاد شد.'); form.reset(); router.refresh(); } catch { toast.error('ایجاد کاربر انجام نشد.'); } })} className="grid gap-3 rounded-xl border bg-card p-5"><h2 className="font-semibold">کاربر جدید</h2><div className="grid gap-3 sm:grid-cols-2"><Input placeholder="نام" {...form.register('first_name')} /><Input placeholder="نام خانوادگی" {...form.register('last_name')} /><Input type="email" placeholder="ایمیل" {...form.register('email')} /><Input type="password" placeholder="رمز عبور (حداقل ۸ کاراکتر)" {...form.register('password')} /></div><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? 'در حال ایجاد…' : 'ایجاد کاربر'}</Button></form>;
}

export function UserActions({ userId, status }: { userId: string; status: string }) {
  const router = useRouter(); const activate = useActivateUser(); const block = useBlockUser(); const remove = useAdminDeleteUser();
  async function run(action: () => Promise<unknown>, message: string) { try { await action(); toast.success(message); router.refresh(); } catch { toast.error('عملیات انجام نشد.'); } }
  return <div className="flex flex-wrap gap-2">{status !== 'active' ? <Button onClick={() => run(() => activate.mutateAsync({ userId }), 'کاربر فعال شد.')} disabled={activate.isPending}>فعال‌سازی</Button> : null}<Button variant="outline" onClick={() => { const reason = window.prompt('دلیل مسدودسازی را وارد کنید'); if (reason) run(() => block.mutateAsync({ userId, data: { reason } }), 'کاربر مسدود شد.'); }} disabled={block.isPending}>مسدودسازی</Button><ActionDialog trigger={<Button variant="destructive" disabled={remove.isPending}>حذف</Button>} title="حذف کاربر" description="این کاربر حذف می‌شود و قابل بازگردانی نیست." confirmLabel="حذف کاربر" destructive onConfirm={()=>remove.mutateAsync({userId})} onDone={()=>{toast.success('کاربر حذف شد.');router.replace('/admin/users');}} /></div>;
}

export function RoleAssignment({ userId, currentRoles, roles }: { userId: string; currentRoles: string[]; roles: RoleResponse[] }) {
  const router = useRouter(); const assign = useAssignRole(); const remove = useRemoveRole();
  const current = currentRoles[0] ?? '';
  async function change(value: string) {
    try { if (currentRoles.length) await Promise.all(currentRoles.filter((key) => key !== value).map((roleKey) => remove.mutateAsync({ userId, roleKey }))); if (value) await assign.mutateAsync({ userId, data: { role_key: value } }); toast.success(value ? 'نقش کاربر به‌روزرسانی شد.' : 'نقش کاربر حذف شد.'); router.refresh(); } catch { toast.error('تغییر نقش انجام نشد.'); }
  }
  const pending = assign.isPending || remove.isPending;
  return <section className="grid gap-3 rounded-xl border bg-card p-5"><div><h2 className="font-semibold">مدیریت نقش</h2><p className="text-sm text-muted-foreground">یک نقش برای کاربر انتخاب کنید یا «بدون نقش» را برگزینید.</p></div><div className="grid gap-2"><Label htmlFor="user-role">نقش</Label><select id="user-role" defaultValue={current} disabled={pending} onChange={(event) => void change(event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm"><option value="">بدون نقش</option>{roles.map((role) => <option key={role.role_id} value={role.role_key}>{role.name} ({role.role_key})</option>)}</select></div></section>;
}
