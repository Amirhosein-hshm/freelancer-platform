'use client';

import Link from 'next/link';
import { Plus, TicketIcon } from 'lucide-react';
import type { PaginationMeta, TicketResponse } from '@/generated/api/models';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { formatDateTime } from '@/lib/format';
import { useListQuery } from '@/lib/url/use-list-query';
import { TICKET_PRIORITY_LABELS, TICKET_STATUS_LABELS } from './ticket-domain';

export function TicketList({ tickets, meta }: { tickets: TicketResponse[]; meta: PaginationMeta }) {
  const query = useListQuery();
  if (tickets.length === 0) {
    return <EmptyState icon={TicketIcon} title="هنوز تیکتی ندارید" description="برای گفتگو با یکی از کاربران مرتبط، تیکت جدید بسازید." action={<Button asChild><Link href="/tickets/new"><Plus size={16} />تیکت جدید</Link></Button>} />;
  }
  return <div className="grid gap-4">
    <div className="grid gap-3">
      {tickets.map((ticket) => <Card key={ticket.ticket_id}><CardContent className="grid gap-3 p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="grid gap-1"><Link href={`/tickets/${ticket.ticket_id}`} className="font-semibold hover:text-primary">{ticket.subject}</Link><span className="ltr-embedded font-mono text-xs text-muted-foreground">{ticket.ticket_code}</span></div>
          <div className="flex gap-2"><Badge variant="outline">{TICKET_PRIORITY_LABELS[ticket.priority]}</Badge><Badge variant={ticket.status === 'open' ? 'default' : 'secondary'}>{TICKET_STATUS_LABELS[ticket.status]}</Badge></div>
        </div>
        <p className="text-xs text-muted-foreground">آخرین پیام: {ticket.last_message_at ? formatDateTime(ticket.last_message_at) : 'هنوز پیامی ثبت نشده'}</p>
      </CardContent></Card>)}
    </div>
    <PaginationBar meta={meta} query={query} itemNoun="تیکت" />
  </div>;
}
