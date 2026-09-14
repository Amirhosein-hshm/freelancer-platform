import type { Metadata } from 'next';
import type { TicketMessageResponse, TicketResponse } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { PageHeader } from '@/components/ui/page-header';
import { TicketConversation } from '@/features/tickets/ticket-conversation';
import { getServerSessionUser, serverGet, serverGetPage } from '@/lib/api/server';

export const metadata: Metadata = { title: 'جزئیات تیکت' };

export default async function TicketDetailsPage({ params }: { params: Promise<{ ticket_id: string }> }) {
  const { ticket_id: ticketId } = await params;
  const [user, ticket, firstMessages] = await Promise.all([
    getServerSessionUser(),
    serverGet<TicketResponse>(`tickets/${ticketId}`),
    serverGetPage<TicketMessageResponse>(`tickets/${ticketId}/messages`, { page: 1, page_size: 100 }),
  ]);
  const remainingMessages = await Promise.all(
    Array.from({ length: Math.max(0, (firstMessages.meta?.total_pages ?? 1) - 1) }, (_, index) =>
      serverGetPage<TicketMessageResponse>(`tickets/${ticketId}/messages`, { page: index + 2, page_size: 100 }),
    ),
  );
  const messages = [firstMessages, ...remainingMessages].flatMap((page) => page.items);
  return <AppShell user={user}><div className="mx-auto grid max-w-4xl gap-6">
    <PageHeader title={ticket.subject} description={`کد تیکت ${ticket.ticket_code}`} backHref="/tickets" backLabel="بازگشت به تیکت‌ها" />
    <TicketConversation ticket={ticket} messages={messages} currentUserId={user.user_id} />
  </div></AppShell>;
}
