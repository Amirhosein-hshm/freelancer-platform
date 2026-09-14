'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Send } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';
import type { FileAssetResponse } from '@/generated/api/models';
import { FileAssetContext } from '@/generated/api/models';
import { useSubmitDelivery } from '@/generated/api/project/project';
import { TextareaField } from '@/components/form/fields';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { FileUploader } from '@/features/files/file-uploader';
import { ApiError, getApiError, type NormalizedApiError } from '@/lib/api/errors';
import { deliverySchema, toDeliveryRequest, type DeliveryValues } from './delivery-domain';

export function DeliveryForm({ projectId, isRevision }: { projectId: string; isRevision: boolean }) {
  const router = useRouter(); const [assets, setAssets] = useState<FileAssetResponse[]>([]); const [error, setError] = useState<NormalizedApiError | null>(null);
  const mutation = useSubmitDelivery<ApiError>();
  const form = useForm<DeliveryValues>({ resolver: zodResolver(deliverySchema), defaultValues: { delivery_note: '', file_asset_ids: [] } });
  const onSubmit = form.handleSubmit(async (values) => { setError(null); try { await mutation.mutateAsync({ projectId, data: toDeliveryRequest(values) }); toast.success(isRevision ? 'نسخه اصلاح‌شده ارسال شد.' : 'تحویل پروژه ارسال شد.'); form.reset(); setAssets([]); router.refresh(); } catch (thrown) { const normalized = getApiError(thrown); if (normalized.status === 401) return router.replace('/login?expired=1'); setError(normalized); } });
  return <Card><CardHeader><CardTitle className="text-base">{isRevision ? 'ارسال نسخه اصلاح‌شده' : 'ارسال تحویل'}</CardTitle><CardDescription>یادداشت و فایل‌های این نسخه را ارسال کنید. اعتبار وضعیت و مالکیت توسط سرور بررسی می‌شود.</CardDescription></CardHeader><CardContent><FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-5"><FormErrorSummary errors={form.formState.errors} labels={{ delivery_note: 'یادداشت تحویل', file_asset_ids: 'فایل‌های تحویل' }} />{error ? <Alert variant="destructive"><AlertTitle>تحویل ارسال نشد</AlertTitle><AlertDescription>{error.message}</AlertDescription></Alert> : null}<TextareaField label="یادداشت تحویل (اختیاری)" name="delivery_note" rows={5} disabled={mutation.isPending} /><FileUploader context={FileAssetContext.delivery} value={assets} onChange={(next) => { setAssets(next); form.setValue('file_asset_ids', next.map((asset) => asset.file_asset_id)); }} multiple disabled={mutation.isPending} label="فایل‌های تحویل" /><div className="flex justify-end"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}{isRevision ? 'ارسال اصلاحات' : 'ارسال تحویل'}</Button></div></form></FormProvider></CardContent></Card>;
}
