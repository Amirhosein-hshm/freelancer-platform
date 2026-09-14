'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Send, Undo2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';
import type { ApplicationResponse } from '@/generated/api/models';
import { useApplyForProject, useWithdrawApplication } from '@/generated/api/project/project';
import { AmountField, TextareaField, TextField } from '@/components/form/fields';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { ApplicationStatusBadge } from '@/features/projects/status-badges';
import { ApiError, getApiError, type NormalizedApiError } from '@/lib/api/errors';
import { formatDateTime } from '@/lib/format';
import { applicationSchema, toApplicationRequest, type ApplicationValues } from './application-domain';

export function ApplicationForm({ projectId, application }: { projectId: string; application: ApplicationResponse | null }) {
  const router = useRouter();
  const [error, setError] = useState<NormalizedApiError | null>(null);
  const apply = useApplyForProject<ApiError>(); const withdraw = useWithdrawApplication<ApiError>();
  const form = useForm<ApplicationValues>({ resolver: zodResolver(applicationSchema), defaultValues: { cover_letter: '', proposed_amount: '', proposed_days: '' }, mode: 'onBlur' });
  const onSubmit = form.handleSubmit(async (values) => { setError(null); try { await apply.mutateAsync({ projectId, data: toApplicationRequest(values) }); toast.success('درخواست همکاری ارسال شد.'); router.refresh(); } catch (thrown) { const normalized = getApiError(thrown); if (normalized.status === 401) return router.replace('/login?expired=1'); setError(normalized); } });

  if (application) return <Card><CardHeader><CardTitle className="flex flex-wrap items-center gap-2 text-base">درخواست شما <ApplicationStatusBadge status={application.status} /></CardTitle><CardDescription>ارسال‌شده در {formatDateTime(application.applied_at)}</CardDescription></CardHeader><CardContent className="grid gap-4"><p className="whitespace-pre-wrap text-sm leading-7">{application.cover_letter || 'متن معرفی ثبت نشده است.'}</p><div className="flex flex-wrap gap-4 text-sm text-muted-foreground"><span>مبلغ پیشنهادی: {application.proposed_amount ?? 'تعیین نشده'}</span><span>زمان پیشنهادی: {application.proposed_days === null ? 'تعیین نشده' : `${application.proposed_days} روز`}</span></div>{application.decision_note ? <Alert><AlertTitle>یادداشت تصمیم</AlertTitle><AlertDescription>{application.decision_note}</AlertDescription></Alert> : null}{application.status === 'accepted' ? <Button asChild><Link href={`/freelancer/projects/${projectId}`}>ورود به میزکار پروژه</Link></Button> : application.status === 'applied' || application.status === 'shortlisted' ? <ActionDialog trigger={<Button variant="outline"><Undo2 size={16} />پس گرفتن درخواست</Button>} title="پس گرفتن درخواست همکاری" description="پس از پس گرفتن، امکان درخواست دوباره را سرور تعیین می‌کند." confirmLabel="پس گرفتن درخواست" destructive onConfirm={async () => { try { return await withdraw.mutateAsync({ projectId, applicationId: application.application_id }); } catch (thrown) { const normalized = getApiError(thrown); if (normalized.status === 401) router.replace('/login?expired=1'); throw thrown; } }} onDone={() => { toast.success('درخواست همکاری پس گرفته شد.'); router.refresh(); }} /> : <Badge variant="outline" className="w-fit">این درخواست دیگر قابل پس گرفتن نیست</Badge>}</CardContent></Card>;

  return <Card><CardHeader><CardTitle className="text-base">ارسال درخواست همکاری</CardTitle><CardDescription>پیشنهاد خود را ثبت کنید. تأیید صلاحیت، سطح و امکان درخواست توسط سرور بررسی می‌شود.</CardDescription></CardHeader><CardContent><FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-5"><FormErrorSummary errors={form.formState.errors} labels={{ cover_letter: 'متن معرفی', proposed_amount: 'مبلغ پیشنهادی', proposed_days: 'زمان پیشنهادی' }} />{error ? <Alert variant="destructive"><AlertTitle>درخواست ارسال نشد</AlertTitle><AlertDescription>{error.message}</AlertDescription></Alert> : null}<TextareaField label="متن معرفی (اختیاری)" name="cover_letter" rows={6} disabled={apply.isPending} /><div className="grid gap-5 sm:grid-cols-2"><AmountField label="مبلغ پیشنهادی (اختیاری)" name="proposed_amount" disabled={apply.isPending} /><TextField label="زمان پیشنهادی به روز (اختیاری)" name="proposed_days" inputMode="numeric" ltr disabled={apply.isPending} /></div><div className="flex justify-end"><Button type="submit" disabled={apply.isPending}>{apply.isPending ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}ارسال درخواست</Button></div></form></FormProvider></CardContent></Card>;
}
