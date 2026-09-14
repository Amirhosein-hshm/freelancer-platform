import type { Metadata } from 'next';
import Link from 'next/link';
import { Plus } from 'lucide-react';
import { Suspense } from 'react';
import type { PaginationMeta, TicketResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/ui/page-header';
import { Skeleton } from '@/components/ui/skeleton';
import { TicketList } from '@/features/tickets/ticket-list';
import { normalizePaginationMeta, toPageQuery } from '@/lib/api/pagination';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';
import { getParam, type RouteSearchParams } from '@/lib/url/query';

export const metadata: Metadata = { title: 'پشتیبانی' };

export default async function TicketsPage({ searchParams }: { searchParams: Promise<RouteSearchParams> }) {
  const params = await searchParams;
  const pageQuery = toPageQuery(getParam(params, 'page'), getParam(params, 'page_size'));
  const [user, page] = await Promise.all([getServerSessionUser(), serverGetPage<TicketResponse>('tickets', pageQuery)]);
  const meta: PaginationMeta = normalizePaginationMeta(page.meta, pageQuery, page.items.length);
  return <AppShell user={user}><div className="mx-auto grid max-w-5xl gap-6">
    <PageHeader title="پشتیبانی" description="تیکت‌ها و گفتگوهای پشتیبانی خود را پیگیری کنید." actions={<Button asChild><Link href="/tickets/new"><Plus size={16} />تیکت جدید</Link></Button>} />
    <Suspense fallback={<div className="grid gap-3"><Skeleton className="h-28" /><Skeleton className="h-28" /></div>}><TicketList tickets={page.items} meta={meta} /></Suspense>
  </div></AppShell>;
}
