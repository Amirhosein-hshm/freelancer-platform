import type { Metadata } from 'next';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import { Plus } from 'lucide-react';
import type { PaginationMeta, ProjectResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { PageHeader } from '@/components/ui/page-header';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import { normalizePaginationMeta, toPageQuery } from '@/lib/api/pagination';
import { getParam, type RouteSearchParams } from '@/lib/url/query';
import { AdminProjectList, AdminProjectPagination } from '@/features/admin/admin-project-list';

export const metadata: Metadata = { title: 'همه پروژه‌ها' };

export default async function AdminProjectsPage({ searchParams }: { searchParams: Promise<RouteSearchParams> }) {
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.admin)) redirect('/dashboard');
  const params = await searchParams;
  const query = toPageQuery(getParam(params, 'page'), getParam(params, 'page_size'));
  const page = await serverGetPage<ProjectResponse>('projects', query);
  const meta: PaginationMeta = normalizePaginationMeta(page.meta, query, page.items.length);

  return <AppShell user={user}>
    <div className="mx-auto grid max-w-6xl gap-6">
      <PageHeader title="همه پروژه‌ها" description="تمام پروژه‌های سامانه را مشاهده و مدیریت کنید." actions={<Button asChild><Link href="/projects/new"><Plus size={16} aria-hidden="true" />ایجاد پروژه</Link></Button>} />
      {page.items.length === 0 ? <EmptyState title="پروژه‌ای پیدا نشد" description="هنوز پروژه‌ای برای نمایش وجود ندارد." action={<Button asChild><Link href="/projects/new"><Plus size={16} aria-hidden="true" />ایجاد پروژه</Link></Button>} /> : <><AdminProjectList projects={page.items} /><AdminProjectPagination meta={meta} /></>}
    </div>
  </AppShell>;
}
