'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Send } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';
import type { FileAssetResponse, RelatedUserResponse } from '@/generated/api/models';
import { FileAssetContext, TicketPriority } from '@/generated/api/models';
import { useCreateTicket, useSendMessage } from '@/generated/api/ticketing/ticketing';
import { SelectField, TextareaField, TextField } from '@/components/form/fields';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { FileUploader } from '@/features/files/file-uploader';
import { ApiError, getApiError, type NormalizedApiError } from '@/lib/api/errors';
import { createTicketSchema, TICKET_PRIORITY_LABELS, type CreateTicketValues } from './ticket-domain';

export function CreateTicketForm({ relatedUsers }: { relatedUsers: RelatedUserResponse[] }) {
  const router = useRouter();
  const [assets, setAssets] = useState<FileAssetResponse[]>([]);
  const [submitError, setSubmitError] = useState<NormalizedApiError | null>(null);
  const form = useForm<CreateTicketValues>({
    resolver: zodResolver(createTicketSchema),
    defaultValues: { target_user_id: '', subject: '', priority: TicketPriority.normal, body: '', attachment_file_asset_ids: [] },
  });
  const createTicket = useCreateTicket<ApiError>();
  const sendMessage = useSendMessage<ApiError>();
  const isPending = createTicket.isPending || sendMessage.isPending;

  const onSubmit = form.handleSubmit(async (values) => {
    setSubmitError(null);
    try {
      const created = await createTicket.mutateAsync({ data: { target_user_id: values.target_user_id, subject: values.subject.trim(), priority: values.priority } });
      if (created.status !== 201) return;
      const ticketId = created.data.data.ticket_id;
      try {
        await sendMessage.mutateAsync({ ticketId, data: { body: values.body.trim(), attachment_file_asset_ids: assets.map((asset) => asset.file_asset_id) } });
        toast.success('تیکت و پیام اولیه ثبت شد.');
      } catch {
        sessionStorage.setItem(`ticket-draft:${ticketId}`, JSON.stringify({
          body: values.body,
          attachment_file_asset_ids: assets.map((asset) => asset.file_asset_id),
        }));
        toast.warning('تیکت ساخته شد، اما پیام اولیه ارسال نشد. پیام را در صفحه تیکت دوباره ارسال کنید.');
      }
      router.replace(`/tickets/${ticketId}`);
      router.refresh();
    } catch (error) {
      const normalized = getApiError(error);
      if (normalized.status === 401) return router.replace('/login?expired=1');
      setSubmitError(normalized);
    }
  });

  return <FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-6">
    <FormErrorSummary errors={form.formState.errors} labels={{ target_user_id: 'مخاطب', subject: 'موضوع', priority: 'اولویت', body: 'پیام اولیه' }} />
    {submitError ? <Alert variant="destructive"><AlertTitle>تیکت ساخته نشد</AlertTitle><AlertDescription>{submitError.message}</AlertDescription></Alert> : null}
    <SelectField label="مخاطب" name="target_user_id" required disabled={isPending} options={relatedUsers.map((user) => ({ value: user.user_id, label: `${user.first_name} ${user.last_name} - ${user.email}` }))} />
    <TextField label="موضوع" name="subject" required disabled={isPending} maxLength={200} />
    <SelectField label="اولویت" name="priority" required disabled={isPending} options={Object.values(TicketPriority).map((value) => ({ value, label: TICKET_PRIORITY_LABELS[value] }))} />
    <TextareaField label="پیام اولیه" name="body" required disabled={isPending} rows={6} />
    <FileUploader context={FileAssetContext.ticket_attachment} value={assets} onChange={(next) => { setAssets(next); form.setValue('attachment_file_asset_ids', next.map((asset) => asset.file_asset_id)); }} multiple disabled={isPending} label="پیوست تیکت" />
    <div className="flex justify-end"><Button type="submit" disabled={isPending || relatedUsers.length === 0}>{isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}ثبت تیکت</Button></div>
  </form></FormProvider>;
}
