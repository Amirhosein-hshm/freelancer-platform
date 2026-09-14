'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { FileText, Loader2, Save, Star, Trash2, Upload } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';
import type { FileAssetResponse, ResumeResponse } from '@/generated/api/models';
import { FileAssetContext } from '@/generated/api/models';
import { useDeleteResume, useSetCurrentResume, useUpdateResume, useUploadResume } from '@/generated/api/freelancer/freelancer';
import { TextareaField } from '@/components/form/fields';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { FileUploader } from '@/features/files/file-uploader';
import { ApiError, getApiError } from '@/lib/api/errors';
import { formatNumber } from '@/lib/format';
import { resumeSchema, resumeSummarySchema, type ResumeSummaryValues, type ResumeValues } from './freelancer-domain';

export function ResumeManager({ profileId, resumes }: { profileId: string; resumes: ResumeResponse[] }) {
  const router = useRouter();
  const [assets, setAssets] = useState<FileAssetResponse[]>([]);
  const upload = useUploadResume<ApiError>();
  const remove = useDeleteResume<ApiError>();
  const setCurrent = useSetCurrentResume<ApiError>();
  const form = useForm<ResumeValues>({ resolver: zodResolver(resumeSchema), defaultValues: { summary: '', file_asset_id: '' } });
  const pending = upload.isPending || remove.isPending || setCurrent.isPending;
  const refresh = () => router.refresh();
  const handleError = (error: unknown): void => { const normalized = getApiError(error); if (normalized.status === 401) router.replace('/login?expired=1'); else toast.error(normalized.message); };
  const onSubmit = form.handleSubmit(async (values) => { try { await upload.mutateAsync({ profileId, data: { file_asset_id: values.file_asset_id, summary: values.summary === '' ? null : values.summary } }); toast.success('نسخه جدید رزومه ثبت شد.'); form.reset(); setAssets([]); refresh(); } catch (error) { handleError(error); } });

  return <Card><CardHeader><CardTitle className="flex items-center gap-2 text-base"><FileText size={18} />رزومه‌ها</CardTitle></CardHeader><CardContent className="grid gap-6">
    <FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-4 rounded-lg border p-4"><FormErrorSummary errors={form.formState.errors} labels={{ file_asset_id: 'فایل رزومه', summary: 'خلاصه رزومه' }} /><TextareaField label="خلاصه نسخه جدید" name="summary" disabled={pending} rows={3} /><FileUploader context={FileAssetContext.resume} value={assets} onChange={(next) => { setAssets(next); form.setValue('file_asset_id', next[0]?.file_asset_id ?? '', { shouldValidate: true }); }} disabled={pending} label="فایل رزومه" /><div className="flex justify-end"><Button type="submit" disabled={pending}>{upload.isPending ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}بارگذاری نسخه جدید</Button></div></form></FormProvider>
    {resumes.length === 0 ? <EmptyState icon={FileText} title="رزومه‌ای ثبت نشده است" className="py-8" /> : <ul className="divide-y">{[...resumes].sort((a, b) => b.version_no - a.version_no).map((resume) => <li key={resume.resume_id} className="grid gap-3 py-4 first:pt-0 last:pb-0"><div className="flex flex-wrap items-center justify-between gap-2"><div className="flex items-center gap-2"><span className="font-medium">نسخه {formatNumber(resume.version_no)}</span>{resume.is_current ? <Badge>نسخه جاری</Badge> : null}</div><span className="ltr-embedded font-mono text-xs text-muted-foreground">{resume.file_asset_id}</span></div><ResumeSummary profileId={profileId} resume={resume} /><div className="flex flex-wrap justify-end gap-2">{!resume.is_current ? <Button type="button" variant="outline" disabled={pending} onClick={async () => { try { await setCurrent.mutateAsync({ profileId, resumeId: resume.resume_id }); toast.success('نسخه جاری تغییر کرد.'); refresh(); } catch (error) { handleError(error); } }}><Star size={16} />انتخاب به‌عنوان جاری</Button> : null}<ActionDialog trigger={<Button type="button" variant="destructive" disabled={pending}><Trash2 size={16} />حذف</Button>} title="حذف نسخه رزومه" description="این نسخه رزومه حذف می‌شود." confirmLabel="حذف نسخه" destructive onConfirm={() => remove.mutateAsync({ profileId, resumeId: resume.resume_id })} onDone={() => { toast.success('نسخه رزومه حذف شد.'); refresh(); }} /></div></li>)}</ul>}
  </CardContent></Card>;
}

function ResumeSummary({ profileId, resume }: { profileId: string; resume: ResumeResponse }) {
  const router = useRouter(); const mutation = useUpdateResume<ApiError>();
  const form = useForm<ResumeSummaryValues>({ resolver: zodResolver(resumeSummarySchema), defaultValues: { summary: resume.summary ?? '' } });
  return <FormProvider {...form}><form onSubmit={form.handleSubmit(async ({ summary }) => { try { await mutation.mutateAsync({ profileId, data: { summary: summary === '' ? null : summary } }); toast.success('خلاصه رزومه جاری ذخیره شد.'); router.refresh(); } catch (error) { const normalized = getApiError(error); if (normalized.status === 401) router.replace('/login?expired=1'); else toast.error(normalized.message); } })} className="grid gap-3"><TextareaField label="خلاصه" name="summary" rows={2} disabled={mutation.isPending || !resume.is_current} description={!resume.is_current ? 'خلاصه فقط برای نسخه جاری قابل ویرایش است.' : undefined} />{resume.is_current ? <Button type="submit" variant="outline" className="justify-self-end" disabled={mutation.isPending}>{mutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}ذخیره خلاصه</Button> : null}</form></FormProvider>;
}
