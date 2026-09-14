'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { Check, X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useSubmitReview } from '@/generated/api/feedback/feedback';
import { ReviewStatus, type ReviewStatus as ReviewStatusType } from '@/generated/api/models';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ApiError, getApiError } from '@/lib/api/errors';

const schema = z.object({ comment: z.string().trim() });
type Values = z.infer<typeof schema>;

export function CustomerReviewActions({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const submitReview = useSubmitReview<ApiError>();
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { comment: '' }, mode: 'onBlur' });

  async function submit(decision: ReviewStatusType, comment?: string) {
    try {
      const result = await submitReview.mutateAsync({ data: { project_id: projectId, decision, comment: comment || null } });
      if (result.status !== 201) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
    } catch (error) {
      const e = getApiError(error);
      throw new ApiError(e.status, e.code, e.message, e.fields);
    }
  }
  async function done(message: string) {
    const { toast } = await import('sonner');
    toast.success(message);
    await queryClient.invalidateQueries({ queryKey: ['project', projectId] });
  }

  return <div className="flex flex-wrap gap-2">
    <ActionDialog trigger={<button type="button" className="inline-flex min-h-10 items-center gap-1.5 rounded-md border border-primary/40 px-3 py-2 text-xs font-medium text-primary" disabled={submitReview.isPending}><Check size={15} aria-hidden="true" />تأیید نهایی</button>} title="تأیید نهایی پروژه" description="با تأیید نهایی، پروژه تکمیل می‌شود." confirmLabel="تأیید نهایی" pendingLabel="در حال ثبت…" onConfirm={() => submit(ReviewStatus.approved, form.getValues('comment'))} onDone={() => { form.reset(); void done('تأیید نهایی ثبت شد.'); }} />
    <ActionDialog trigger={<button type="button" className="inline-flex min-h-10 items-center gap-1.5 rounded-md border border-destructive/50 px-3 py-2 text-xs font-medium text-destructive" disabled={submitReview.isPending}><X size={15} aria-hidden="true" />درخواست اصلاح</button>} title="درخواست اصلاح نهایی" description="دلیل اصلاح برای فریلنسر ارسال می‌شود." confirmLabel="ثبت درخواست اصلاح" pendingLabel="در حال ثبت…" destructive disabled={!form.formState.isValid} onConfirm={async () => { if (!(await form.trigger())) return; await submit(ReviewStatus.rejected, form.getValues('comment')); }} onDone={() => { form.reset(); void done('درخواست اصلاح ثبت شد.'); }}>
      <div className="grid gap-2"><Label htmlFor={`customer-review-comment-${projectId}`}>توضیح شما</Label><Input id={`customer-review-comment-${projectId}`} {...form.register('comment')} />{form.formState.errors.comment ? <p className="text-sm text-destructive">{form.formState.errors.comment.message}</p> : null}</div>
    </ActionDialog>
  </div>;
}
