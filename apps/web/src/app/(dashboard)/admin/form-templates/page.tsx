import Link from 'next/link';
import { redirect } from 'next/navigation';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { EmptyState } from '@/components/ui/empty-state';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { getServerSessionUser, serverGet, serverGetPage } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import type { ListFormTemplatesResponse } from '@/generated/api/models/listFormTemplatesResponse';
import type { CategoryResponse } from '@/generated/api/models/categoryResponse';
import { CreateFormTemplateForm } from '@/features/admin/form-template-management';

export default async function TemplatesPage() {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) redirect('/dashboard');
  const [result, categories] = await Promise.all([serverGet<ListFormTemplatesResponse>('form-templates'), serverGetPage<CategoryResponse>('categories')]);
  const activeCategories = categories.items.filter((category) => category.is_active);
  return <AppShell user={user}><div className="mx-auto grid max-w-6xl gap-6"><PageHeader title="قالب‌های فرم" description="قالب‌های منتشرشده در backend فقط خواندنی هستند." actions={<Link href="/admin" className="text-sm text-primary">بازگشت به مدیریت</Link>} /><CreateFormTemplateForm categories={activeCategories} />{result.templates.length===0?<EmptyState title="قالبی ثبت نشده است"/>:<div className="overflow-hidden rounded-xl border bg-card"><Table><TableHeader><TableRow><TableHead>نام</TableHead><TableHead>کلید</TableHead><TableHead>نسخه</TableHead><TableHead>وضعیت</TableHead></TableRow></TableHeader><TableBody>{result.templates.map(t=><TableRow key={t.template_id}><TableCell><Link className="text-primary" href={`/admin/form-templates/${t.template_id}`}>{t.name}</Link></TableCell><TableCell>{t.template_key}</TableCell><TableCell>{t.version_no}</TableCell><TableCell>{t.status}</TableCell></TableRow>)}</TableBody></Table></div>}</div></AppShell>;
}
