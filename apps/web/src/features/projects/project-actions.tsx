'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { Ban, Check, Play, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { useCancelProject, useDeleteProject, usePublishProject, useStartProject } from '@/generated/api/project/project';
import { ProjectStatus } from '@/generated/api/models';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { ApiError, getApiError } from '@/lib/api/errors';
import { canCancelProject, canDeleteProject, canPublishProject, canStartProject } from './project-domain';
import { z } from 'zod';

const cancelSchema = z.object({ reason: z.string().trim().min(1, 'دلیل لغو را وارد کنید.') });
type CancelValues = z.infer<typeof cancelSchema>;

export function ProjectActions({ projectId, status }: { projectId: string; status: ProjectStatus }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [unauthorized, setUnauthorized] = useState(false);
  const cancelForm = useForm<CancelValues>({
    resolver: zodResolver(cancelSchema),
    defaultValues: { reason: '' },
    mode: 'onBlur',
  });

  const onError = (error: unknown): never => {
    const normalized = getApiError(error);
    if (normalized.status === 401) {
      setUnauthorized(true);
      router.replace('/login?expired=1');
    }
    throw new ApiError(normalized.status, normalized.code, normalized.message, normalized.fields);
  };
  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ['project', projectId] });
    router.refresh();
  };
  const deleteMutation = useDeleteProject<ApiError>({ mutation: { onError } });
  const publishMutation = usePublishProject<ApiError>({ mutation: { onError } });
  const startMutation = useStartProject<ApiError>({ mutation: { onError } });
  const cancelMutation = useCancelProject<ApiError>({ mutation: { onError } });
  const anyPending = deleteMutation.isPending || publishMutation.isPending || startMutation.isPending || cancelMutation.isPending;

  if (unauthorized) return null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      {canPublishProject(status) ? (
        <ActionDialog
          trigger={<Button variant="success" disabled={anyPending}><Check size={16} aria-hidden="true" />انتشار پروژه</Button>}
          title="انتشار پروژه"
          description="پس از انتشار، این پیش‌نویس برای فریلنسرهای واجد شرایط قابل مشاهده خواهد بود."
          confirmLabel="انتشار"
          pendingLabel="در حال انتشار…"
          onConfirm={async () => {
            const result = await publishMutation.mutateAsync({ projectId });
            if (result.status !== 200) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
          }}
          onDone={() => void invalidate()}
        />
      ) : null}
      {canStartProject(status) ? (
        <ActionDialog
          trigger={<Button disabled={anyPending}><Play size={16} aria-hidden="true" />شروع پروژه</Button>}
          title="شروع پروژه"
          description="با شروع پروژه، وضعیت آن به در حال انجام تغییر می‌کند."
          confirmLabel="شروع پروژه"
          pendingLabel="در حال شروع…"
          onConfirm={async () => {
            const result = await startMutation.mutateAsync({ projectId });
            if (result.status !== 200) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
          }}
          onDone={() => void invalidate()}
        />
      ) : null}
      {canCancelProject(status) ? (
        <ActionDialog
          trigger={<Button variant="warning" disabled={anyPending}><Ban size={16} aria-hidden="true" />لغو پروژه</Button>}
          title="لغو پروژه"
          description="لغو پروژه قابل بازگشت نیست. دلیل لغو برای ثبت در تاریخچه لازم است."
          confirmLabel="لغو پروژه"
          pendingLabel="در حال لغو…"
          destructive
          disabled={!cancelForm.formState.isValid}
          onConfirm={async () => {
            const valid = await cancelForm.trigger();
            if (!valid) return;
            const result = await cancelMutation.mutateAsync({ projectId, data: cancelForm.getValues() });
            if (result.status !== 200) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
          }}
          onDone={() => {
            cancelForm.reset();
            void invalidate();
          }}
        >
          <form className="grid gap-2" onSubmit={(event) => event.preventDefault()}>
            <FormErrorSummary errors={cancelForm.formState.errors} labels={{ reason: 'دلیل لغو' }} />
            <Label htmlFor="cancel-reason">دلیل لغو</Label>
            <Input id="cancel-reason" {...cancelForm.register('reason')} aria-invalid={cancelForm.formState.errors.reason ? true : undefined} />
            {cancelForm.formState.errors.reason ? <p className="text-sm text-destructive">{cancelForm.formState.errors.reason.message}</p> : null}
          </form>
        </ActionDialog>
      ) : null}
      {canDeleteProject(status) ? (
        <ActionDialog
          trigger={<Button variant="destructive" disabled={anyPending}><Trash2 size={16} aria-hidden="true" />حذف پیش‌نویس</Button>}
          title="حذف پیش‌نویس"
          description="این پیش‌نویس حذف می‌شود و قابل بازگردانی نیست."
          confirmLabel="حذف پیش‌نویس"
          pendingLabel="در حال حذف…"
          destructive
          onConfirm={async () => {
            const result = await deleteMutation.mutateAsync({ projectId });
            if (result.status !== 200) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
          }}
          onDone={() => {
            toast.success('پیش‌نویس پروژه حذف شد.');
            router.replace('/projects');
            router.refresh();
          }}
        />
      ) : null}
    </div>
  );
}
