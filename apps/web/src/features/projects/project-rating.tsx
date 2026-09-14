'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { Loader2, Save, Star, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { FormProvider, useForm, useWatch } from 'react-hook-form';
import { toast } from 'sonner';
import { z } from 'zod';
import {
  useDeleteRating,
  useSubmitRating,
  useUpdateRating,
} from '@/generated/api/feedback/feedback';
import type { RatingResponse } from '@/generated/api/models';
import { TextareaField } from '@/components/form/fields';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { Label } from '@/components/ui/label';
import { ApiError, getApiError } from '@/lib/api/errors';

export const ratingSchema = z.object({
  score: z.number().int().min(1, 'امتیاز را انتخاب کنید.').max(5, 'امتیاز باید بین ۱ تا ۵ باشد.'),
  comment: z.string().trim(),
  is_public: z.boolean(),
});

export type RatingFormValues = z.infer<typeof ratingSchema>;

export function ProjectRating({ projectId, rating }: { projectId: string; rating: RatingResponse | null }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const form = useForm<RatingFormValues>({
    resolver: zodResolver(ratingSchema),
    defaultValues: {
      score: rating?.score ?? 0,
      comment: rating?.comment ?? '',
      is_public: rating?.is_public ?? false,
    },
    mode: 'onBlur',
  });
  const create = useSubmitRating<ApiError>();
  const update = useUpdateRating<ApiError>();
  const remove = useDeleteRating<ApiError>();
  const pending = create.isPending || update.isPending || remove.isPending;
  const isPublic = useWatch({ control: form.control, name: 'is_public' });

  async function refresh(): Promise<void> {
    await queryClient.invalidateQueries({
      queryKey: [`/api/v1/feedback/projects/${projectId}/rating`],
    });
    router.refresh();
  }

  function rethrow(error: unknown): never {
    const normalized = getApiError(error);
    if (normalized.status === 401) router.replace('/login?expired=1');
    throw new ApiError(normalized.status, normalized.code, normalized.message, normalized.fields);
  }

  const onSubmit = form.handleSubmit(async (values) => {
    const data = {
      score: values.score,
      comment: values.comment === '' ? null : values.comment,
      is_public: values.is_public,
    };
    try {
      if (rating) {
        const result = await update.mutateAsync({ ratingId: rating.rating_id, data });
        if (result.status !== 200) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
      } else {
        const result = await create.mutateAsync({ data: { project_id: projectId, ...data } });
        if (result.status !== 201) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
      }
      toast.success(rating ? 'امتیاز پروژه ویرایش شد.' : 'امتیاز پروژه ثبت شد.');
      await refresh();
    } catch (error) {
      rethrow(error);
    }
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Star size={18} aria-hidden="true" />
          امتیاز همکاری
        </CardTitle>
        <CardDescription>
          تجربه همکاری خود را از ۱ تا ۵ ثبت کنید. عمومی بودن امتیاز را می‌توانید تغییر دهید.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <FormProvider {...form}>
          <form onSubmit={onSubmit} noValidate className="grid gap-5">
            <FormErrorSummary errors={form.formState.errors} labels={{ score: 'امتیاز', comment: 'نظر', is_public: 'نمایش عمومی' }} />

            <fieldset className="grid gap-2">
              <legend className="text-sm font-medium">امتیاز</legend>
              <div className="flex flex-wrap gap-2">
                {[1, 2, 3, 4, 5].map((score) => (
                  <label key={score} className="cursor-pointer">
                    <input
                      type="radio"
                      value={score}
                      className="peer sr-only"
                      disabled={pending}
                      {...form.register('score', { valueAsNumber: true })}
                    />
                    <span className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-md border text-sm font-medium transition-colors peer-checked:border-primary peer-checked:bg-primary peer-checked:text-primary-foreground peer-focus-visible:ring-[3px] peer-focus-visible:ring-ring/50">
                      {score}
                    </span>
                  </label>
                ))}
              </div>
              {form.formState.errors.score ? (
                <p className="text-sm text-destructive">{form.formState.errors.score.message}</p>
              ) : null}
            </fieldset>

            <TextareaField label="نظر شما (اختیاری)" name="comment" rows={4} disabled={pending} />

            <div className="flex items-center gap-3">
              <Checkbox
                id="rating-public"
                checked={isPublic}
                disabled={pending}
                onCheckedChange={(checked) => form.setValue('is_public', checked === true, { shouldDirty: true })}
              />
              <Label htmlFor="rating-public">این امتیاز به‌صورت عمومی نمایش داده شود</Label>
            </div>

            <div className="flex flex-col-reverse gap-3 border-t pt-5 sm:flex-row sm:justify-end">
              {rating ? (
                <ActionDialog
                  trigger={<Button type="button" variant="destructive" disabled={pending}><Trash2 size={16} aria-hidden="true" />حذف امتیاز</Button>}
                  title="حذف امتیاز"
                  description="امتیاز و نظر ثبت‌شده حذف می‌شود."
                  confirmLabel="حذف امتیاز"
                  pendingLabel="در حال حذف…"
                  destructive
                  onConfirm={async () => {
                    try {
                      const result = await remove.mutateAsync({ ratingId: rating.rating_id });
                      if (result.status !== 200) throw new Error('پاسخ نامعتبر از سرور دریافت شد.');
                    } catch (error) {
                      rethrow(error);
                    }
                  }}
                  onDone={() => { toast.success('امتیاز حذف شد.'); void refresh(); }}
                />
              ) : null}
              <Button type="submit" disabled={pending} className="min-h-11">
                {pending ? <Loader2 size={16} className="animate-spin" aria-hidden="true" /> : <Save size={16} aria-hidden="true" />}
                {pending ? 'در حال ذخیره…' : rating ? 'ویرایش امتیاز' : 'ثبت امتیاز'}
              </Button>
            </div>
          </form>
        </FormProvider>
      </CardContent>
    </Card>
  );
}
