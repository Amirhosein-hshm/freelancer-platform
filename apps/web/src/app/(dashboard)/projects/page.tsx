import type { Metadata } from 'next';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Suspense } from 'react';
import type { PaginationMeta, ProjectResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/ui/page-header';
import { Skeleton } from '@/components/ui/skeleton';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';
import { normalizePaginationMeta, toPageQuery } from '@/lib/api/pagination';
import { getParam, type RouteSearchParams } from '@/lib/url/query';
import { ProjectList } from '@/features/projects/project-list';

export const metadata: Metadata = { title: 'پروژه‌های من' };

export default async function ProjectsPage({
  searchParams,
}: {
  searchParams: Promise<RouteSearchParams>;
}) {
  const params = await searchParams;
  const pageQuery = toPageQuery(getParam(params, 'page'), getParam(params, 'page_size'));

  const [user, page] = await Promise.all([
    getServerSessionUser(),
    serverGetPage<ProjectResponse>('projects/my', pageQuery),
  ]);

  const meta: PaginationMeta = normalizePaginationMeta(page.meta, pageQuery, page.items.length);

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-5xl gap-6">
        <PageHeader
          title="پروژه‌های من"
          description="پروژه‌های خود را بسازید، منتشر کنید و روند اجرای آن‌ها را پیش ببرید."
          actions={
            <Button asChild>
              <Link href="/projects/new">
                <Plus size={16} aria-hidden="true" />
                پروژه جدید
              </Link>
            </Button>
          }
        />

        {/* ProjectList reads useSearchParams, so it needs a boundary of its own. */}
        <Suspense fallback={<ListFallback />}>
          <ProjectList projects={page.items} meta={meta} createHref="/projects/new" />
        </Suspense>
      </div>
    </AppShell>
  );
}

function ListFallback() {
  return (
    <div className="grid gap-3" aria-hidden="true">
      {[0, 1, 2].map((index) => (
        <Skeleton key={index} className="h-32 rounded-xl" />
      ))}
    </div>
  );
}
