'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { BriefcaseBusiness, Loader2, Plus, Save, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { FormProvider, useForm, useWatch } from 'react-hook-form';
import { toast } from 'sonner';
import type { FileAssetResponse, PortfolioItemResponse } from '@/generated/api/models';
import { FileAssetContext } from '@/generated/api/models';
import { useAddPortfolioItem, useDeletePortfolioItem, useUpdatePortfolioItem } from '@/generated/api/freelancer/freelancer';
import { TextareaField, TextField } from '@/components/form/fields';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { EmptyState } from '@/components/ui/empty-state';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { Label } from '@/components/ui/label';
import { FileUploader } from '@/features/files/file-uploader';
import { ApiError, getApiError } from '@/lib/api/errors';
import { formatNumber } from '@/lib/format';
import { portfolioSchema, type PortfolioValues } from './freelancer-domain';

export function PortfolioManager({ profileId, items }: { profileId: string; items: PortfolioItemResponse[] }) {
  return <Card><CardHeader><CardTitle className="flex items-center gap-2 text-base"><BriefcaseBusiness size={18} />نمونه‌کارها</CardTitle></CardHeader><CardContent className="grid gap-6"><PortfolioForm profileId={profileId} />{items.length === 0 ? <EmptyState icon={BriefcaseBusiness} title="نمونه‌کاری ثبت نشده است" className="py-8" /> : <div className="grid gap-4">{[...items].sort((a, b) => a.display_order - b.display_order).map((item) => <PortfolioForm key={item.item_id} profileId={profileId} item={item} />)}</div>}</CardContent></Card>;
}

function PortfolioForm({ profileId, item }: { profileId: string; item?: PortfolioItemResponse }) {
  const router = useRouter();
  const [assets, setAssets] = useState<FileAssetResponse[]>([]);
  const create = useAddPortfolioItem<ApiError>(); const update = useUpdatePortfolioItem<ApiError>(); const remove = useDeletePortfolioItem<ApiError>();
  const form = useForm<PortfolioValues>({ resolver: zodResolver(portfolioSchema), defaultValues: { title: item?.title ?? '', description: item?.description ?? '', external_url: item?.external_url ?? '', file_asset_id: item?.file_asset_id ?? '', display_order: String(item?.display_order ?? 0), is_featured: item?.is_featured ?? false } });
  const featured = useWatch({ control: form.control, name: 'is_featured' });
  const pending = create.isPending || update.isPending || remove.isPending;
  const onSubmit = form.handleSubmit(async (values) => { const data = { title: values.title.trim(), description: values.description === '' ? null : values.description, external_url: values.external_url === '' ? null : values.external_url, file_asset_id: values.file_asset_id === '' ? null : values.file_asset_id, display_order: Number(values.display_order), is_featured: values.is_featured }; try { if (item) await update.mutateAsync({ profileId, itemId: item.item_id, data }); else await create.mutateAsync({ profileId, data }); toast.success(item ? 'نمونه‌کار ویرایش شد.' : 'نمونه‌کار اضافه شد.'); if (!item) { form.reset(); setAssets([]); } router.refresh(); } catch (error) { const normalized = getApiError(error); if (normalized.status === 401) router.replace('/login?expired=1'); else toast.error(normalized.message); } });
  return <FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-4 rounded-lg border border-border p-4"><div className="flex flex-wrap items-center justify-between gap-2"><h3 className="font-medium">{item ? item.title : 'نمونه‌کار جدید'}</h3>{item?.is_featured ? <Badge>برگزیده</Badge> : null}</div><FormErrorSummary errors={form.formState.errors} labels={{ title: 'عنوان', description: 'توضیحات', external_url: 'نشانی اینترنتی', display_order: 'ترتیب نمایش' }} /><div className="grid gap-4 sm:grid-cols-2"><TextField label="عنوان" name="title" required disabled={pending} /><TextField label="نشانی اینترنتی" name="external_url" type="url" ltr disabled={pending} /></div><TextareaField label="توضیحات" name="description" rows={3} disabled={pending} /><TextField label="ترتیب نمایش" name="display_order" inputMode="numeric" ltr disabled={pending} /><div className="flex items-center gap-3"><Checkbox id={`featured-${item?.item_id ?? 'new'}`} checked={featured} disabled={pending} onCheckedChange={(checked) => form.setValue('is_featured', checked === true, { shouldDirty: true })} /><Label htmlFor={`featured-${item?.item_id ?? 'new'}`}>نمونه‌کار برگزیده</Label></div>{item?.file_asset_id && assets.length === 0 ? <p className="ltr-embedded truncate font-mono text-xs text-muted-foreground">فایل فعلی: {item.file_asset_id}</p> : null}<FileUploader context={FileAssetContext.portfolio} value={assets} onChange={(next) => { setAssets(next); form.setValue('file_asset_id', next[0]?.file_asset_id ?? '', { shouldDirty: true }); }} disabled={pending} label="فایل نمونه‌کار" /><div className="flex flex-wrap justify-end gap-2">{item ? <ActionDialog trigger={<Button type="button" variant="destructive" disabled={pending}><Trash2 size={16} />حذف</Button>} title="حذف نمونه‌کار" description="این نمونه‌کار حذف می‌شود." confirmLabel="حذف" destructive onConfirm={() => remove.mutateAsync({ profileId, itemId: item.item_id })} onDone={() => { toast.success('نمونه‌کار حذف شد.'); router.refresh(); }} /> : null}<Button type="submit" disabled={pending}>{pending ? <Loader2 size={16} className="animate-spin" /> : item ? <Save size={16} /> : <Plus size={16} />}{item ? 'ذخیره تغییرات' : 'افزودن نمونه‌کار'}</Button></div>{item ? <p className="text-xs text-muted-foreground">ترتیب فعلی: {formatNumber(item.display_order)}</p> : null}</form></FormProvider>;
}
