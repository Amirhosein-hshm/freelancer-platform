import type { Metadata } from 'next';
import type { PaginationMeta, ProjectResponse, ReviewResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { ReviewsTabs } from '@/features/reviews/reviews-tabs';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';
import { normalizePaginationMeta, toPageQuery } from '@/lib/api/pagination';
import { getParam, type RouteSearchParams } from '@/lib/url/query';

export const metadata: Metadata = { title: 'صف بازبینی' };

export default async function ReviewsPage({ searchParams }: { searchParams: Promise<RouteSearchParams> }) {
  const params = await searchParams;
  const pageQuery = toPageQuery(getParam(params, 'page'), getParam(params, 'page_size'));
  const [user, pending, projects] = await Promise.all([
    getServerSessionUser(),
    serverGetPage<ReviewResponse>('reviews/pending', pageQuery),
    serverGetPage<ProjectResponse>('reviews/supervisor/projects', pageQuery),
  ]);
  const pendingMeta: PaginationMeta = normalizePaginationMeta(pending.meta, pageQuery, pending.items.length);
  const projectMeta: PaginationMeta = normalizePaginationMeta(projects.meta, pageQuery, projects.items.length);
  return <AppShell user={user}><div className="mx-auto grid max-w-5xl gap-6">
    <PageHeader title="صف بازبینی" description="تحویلی‌های حوزه نظارت خود را بررسی و درباره آن‌ها تصمیم‌گیری کنید." />
    <ReviewsTabs pending={pending.items} pendingMeta={pendingMeta} projects={projects.items} projectMeta={projectMeta} />
  </div></AppShell>;
}
