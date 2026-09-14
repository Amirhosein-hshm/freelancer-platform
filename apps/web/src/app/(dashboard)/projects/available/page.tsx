import type { Metadata } from 'next';
import { Suspense } from 'react';
import type { PaginationMeta, ProjectResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { Skeleton } from '@/components/ui/skeleton';
import { AvailableProjectList } from '@/features/freelancer/available-project-list';
import { normalizePaginationMeta, toPageQuery } from '@/lib/api/pagination';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';
import { getParam, type RouteSearchParams } from '@/lib/url/query';

export const metadata: Metadata = { title: 'پروژه‌های موجود' };

export default async function AvailableProjectsPage({ searchParams }: { searchParams: Promise<RouteSearchParams> }) {
  const params = await searchParams; const query = toPageQuery(getParam(params, 'page'), getParam(params, 'page_size'));
  const user = await getServerSessionUser();
  if (!hasRole(user, ROLES.freelancer)) return <AppShell user={user}><ErrorState error={{ status: 403, code: 'permission_denied', message: 'این بخش فقط برای نقش فریلنسر در دسترس است.', fields: {} }} /></AppShell>;
  const page = await serverGetPage<ProjectResponse>('projects/available', query);
  const meta: PaginationMeta = normalizePaginationMeta(page.meta, query, page.items.length);
  return <AppShell user={user}><div className="mx-auto grid max-w-5xl gap-6"><PageHeader title="پروژه‌های موجود" description="این فهرست را سرور براساس وضعیت تأیید، سطح و صلاحیت حساب شما برمی‌گرداند." /><Suspense fallback={<div className="grid gap-3"><Skeleton className="h-32" /><Skeleton className="h-32" /></div>}><AvailableProjectList projects={page.items} meta={meta} /></Suspense></div></AppShell>;
}
