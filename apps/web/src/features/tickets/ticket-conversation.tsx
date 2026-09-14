'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Pencil, Send, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';
import type { FileAssetResponse, TicketMessageResponse, TicketResponse } from '@/generated/api/models';
import { FileAssetContext } from '@/generated/api/models';
import { useCloseTicket, useDeleteTicketMessage, useSendMessage, useUpdateTicketMessage } from '@/generated/api/ticketing/ticketing';
import { TextareaField } from '@/components/form/fields';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { FileUploader } from '@/features/files/file-uploader';
import { ApiError, getApiError, type NormalizedApiError } from '@/lib/api/errors';
import { formatDateTime, formatNumber } from '@/lib/format';
import { TICKET_STATUS_LABELS, ticketMessageSchema, type TicketMessageValues } from './ticket-domain';

export function TicketConversation({ ticket, messages, currentUserId }: { ticket: TicketResponse; messages: TicketMessageResponse[]; currentUserId: string }) {
  const router = useRouter();
  const [assets, setAssets] = useState<FileAssetResponse[]>([]);
  const [error, setError] = useState<NormalizedApiError | null>(null);
  const form = useForm<TicketMessageValues>({ resolver: zodResolver(ticketMessageSchema), defaultValues: { body: '', attachment_file_asset_ids: [] } });
  const sendMessage = useSendMessage<ApiError>();
  const closeTicket = useCloseTicket<ApiError>();
  const deleteMessage = useDeleteTicketMessage<ApiError>();
  const isReadOnly = ticket.status !== 'open';

  useEffect(() => {
    const key = `ticket-draft:${ticket.ticket_id}`;
    const saved = sessionStorage.getItem(key);
    if (!saved) return;
    try {
      const draft = JSON.parse(saved) as Partial<TicketMessageValues>;
      form.reset({
        body: typeof draft.body === 'string' ? draft.body : '',
        attachment_file_asset_ids: Array.isArray(draft.attachment_file_asset_ids)
          ? draft.attachment_file_asset_ids.filter((id): id is string => typeof id === 'string')
          : [],
      });
      sessionStorage.removeItem(key);
    } catch {
      sessionStorage.removeItem(key);
    }
  }, [form, ticket.ticket_id]);

  const onSubmit = form.handleSubmit(async (values) => {
    setError(null);
    try {
      await sendMessage.mutateAsync({ ticketId: ticket.ticket_id, data: { body: values.body.trim(), attachment_file_asset_ids: values.attachment_file_asset_ids } });
      form.reset(); setAssets([]); toast.success('پیام ارسال شد.'); router.refresh();
    } catch (thrown) {
      const normalized = getApiError(thrown);
      if (normalized.status === 401) return router.replace('/login?expired=1');
      setError(normalized);
    }
  });

  return <div className="grid gap-6">
    <div className="flex flex-wrap items-center justify-between gap-3"><Badge variant={ticket.status === 'open' ? 'default' : 'secondary'}>{TICKET_STATUS_LABELS[ticket.status]}</Badge>{ticket.status === 'open' ? <ActionDialog trigger={<Button variant="outline">بستن تیکت</Button>} title="بستن تیکت" description="پس از بستن، ارسال پیام جدید ممکن نیست مگر سرور دوباره آن را باز کند." confirmLabel="بستن تیکت" onConfirm={() => closeTicket.mutateAsync({ ticketId: ticket.ticket_id })} onDone={() => router.refresh()} /> : null}</div>
    <ol className="grid gap-3">{messages.map((message) => <li key={message.message_id} className="grid gap-2 rounded-lg border border-border p-4">
      <div className="flex flex-wrap items-center justify-between gap-2"><span className="ltr-embedded font-mono text-xs text-muted-foreground">{message.sender_user_id}</span><time className="text-xs text-muted-foreground" dateTime={message.sent_at}>{formatDateTime(message.sent_at)}</time></div>
      <p className="whitespace-pre-wrap text-sm leading-7">{message.body ?? (message.message_type === 'system' ? 'پیام سیستمی' : 'پیام بدون متن')}</p>
      {message.attachment_file_asset_ids.length ? <p className="text-xs text-muted-foreground">{formatNumber(message.attachment_file_asset_ids.length)} فایل پیوست</p> : null}
      {message.sender_user_id === currentUserId && !message.is_internal && message.message_type !== 'system' && !isReadOnly ? <div className="flex justify-end gap-2"><EditMessage ticketId={ticket.ticket_id} message={message} onDone={() => router.refresh()} /><ActionDialog trigger={<Button variant="ghost" size="icon" title="حذف پیام"><Trash2 size={16} /></Button>} title="حذف پیام" description="این پیام از گفتگو حذف می‌شود." confirmLabel="حذف" destructive onConfirm={() => deleteMessage.mutateAsync({ ticketId: ticket.ticket_id, messageId: message.message_id })} onDone={() => router.refresh()} /></div> : null}
    </li>)}</ol>
    {!isReadOnly ? <FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-4 rounded-lg border border-border p-5">
      <FormErrorSummary errors={form.formState.errors} labels={{ body: 'پیام' }} />
      {error ? <Alert variant="destructive"><AlertDescription>{error.message}</AlertDescription></Alert> : null}
      <TextareaField label="پاسخ" name="body" required rows={5} disabled={sendMessage.isPending} />
      <FileUploader context={FileAssetContext.ticket_attachment} value={assets} onChange={(next) => { setAssets(next); form.setValue('attachment_file_asset_ids', next.map((asset) => asset.file_asset_id)); }} multiple disabled={sendMessage.isPending} label="پیوست پاسخ" />
      <div className="flex justify-end"><Button type="submit" disabled={sendMessage.isPending}>{sendMessage.isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}ارسال پاسخ</Button></div>
    </form></FormProvider> : <Alert><AlertDescription>این تیکت بسته است و فقط برای مطالعه نمایش داده می‌شود.</AlertDescription></Alert>}
  </div>;
}

function EditMessage({ ticketId, message, onDone }: { ticketId: string; message: TicketMessageResponse; onDone: () => void }) {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mutation = useUpdateTicketMessage<ApiError>();
  const form = useForm<{ body: string }>({ resolver: zodResolver(ticketMessageSchema.pick({ body: true })), defaultValues: { body: message.body ?? '' } });
  const onSubmit = form.handleSubmit(async ({ body }) => { setError(null); try { await mutation.mutateAsync({ ticketId, messageId: message.message_id, data: { body: body.trim() } }); setOpen(false); onDone(); } catch (thrown) { setError(getApiError(thrown).message); } });
  return <Dialog open={open} onOpenChange={setOpen}><DialogTrigger asChild><Button variant="ghost" size="icon" title="ویرایش پیام"><Pencil size={16} /></Button></DialogTrigger><DialogContent><DialogHeader><DialogTitle>ویرایش پیام</DialogTitle></DialogHeader><FormProvider {...form}><form onSubmit={onSubmit} className="grid gap-4"><TextareaField label="متن پیام" name="body" required disabled={mutation.isPending} />{error ? <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert> : null}<DialogFooter><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? <Loader2 size={16} className="animate-spin" /> : null}ذخیره</Button></DialogFooter></form></FormProvider></DialogContent></Dialog>;
}
