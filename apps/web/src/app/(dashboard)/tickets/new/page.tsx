import type { Metadata } from 'next';
import type { RelatedUserResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent } from '@/components/ui/card';
import { PageHeader } from '@/components/ui/page-header';
import { CreateTicketForm } from '@/features/tickets/create-ticket-form';
import { getServerSessionUser, serverGetPage } from '@/lib/api/server';

export const metadata: Metadata = { title: 'تیکت جدید' };

export default async function NewTicketPage() {
  const [user, firstRelated] = await Promise.all([
    getServerSessionUser(),
    serverGetPage<RelatedUserResponse>('users/related', { page: 1, page_size: 100 }),
  ]);
  const remainingRelated = await Promise.all(
    Array.from({ length: Math.max(0, (firstRelated.meta?.total_pages ?? 1) - 1) }, (_, index) =>
      serverGetPage<RelatedUserResponse>('users/related', { page: index + 2, page_size: 100 }),
    ),
  );
  const relatedUsers = [firstRelated, ...remainingRelated].flatMap((page) => page.items);
  return <AppShell user={user}><div className="mx-auto grid max-w-3xl gap-6">
    <PageHeader title="تیکت جدید" description="مخاطب مرتبط را انتخاب کنید و موضوع گفتگو را بنویسید." backHref="/tickets" backLabel="بازگشت به تیکت‌ها" />
    {relatedUsers.length === 0 ? <Alert><AlertTitle>مخاطبی در دسترس نیست</AlertTitle><AlertDescription>سرور هنوز کاربر مرتبطی برای ایجاد تیکت برنگردانده است.</AlertDescription></Alert> : null}
    <Card><CardContent className="p-6"><CreateTicketForm relatedUsers={relatedUsers} /></CardContent></Card>
  </div></AppShell>;
}
