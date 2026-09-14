'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Save } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { FormProvider, useForm } from 'react-hook-form';
import { toast } from 'sonner';
import type { FreelancerProfileResponse } from '@/generated/api/models';
import { useCreateFreelancerProfile, useUpdateFreelancerProfile } from '@/generated/api/freelancer/freelancer';
import { AmountField, TextareaField, TextField } from '@/components/form/fields';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { FormErrorSummary } from '@/components/ui/form-error-summary';
import { ApiError, getApiError, type NormalizedApiError } from '@/lib/api/errors';
import { profileSchema, toCreateProfileRequest, toProfileValues, toUpdateProfileRequest, type ProfileValues } from './freelancer-domain';

export function ProfileForm({ profile }: { profile?: FreelancerProfileResponse }) {
  const router = useRouter();
  const [error, setError] = useState<NormalizedApiError | null>(null);
  const form = useForm<ProfileValues>({ resolver: zodResolver(profileSchema), defaultValues: toProfileValues(profile), mode: 'onBlur' });
  useEffect(() => {
    form.reset(toProfileValues(profile));
  }, [form, profile]);
  const create = useCreateFreelancerProfile<ApiError>();
  const update = useUpdateFreelancerProfile<ApiError>();
  const pending = create.isPending || update.isPending;
  const labels = { display_name: 'نام نمایشی', headline: 'عنوان حرفه‌ای', bio: 'درباره من', country_code: 'کد کشور', city: 'شهر', timezone: 'منطقه زمانی', hourly_rate_min: 'حداقل نرخ', hourly_rate_max: 'حداکثر نرخ' };

  const onSubmit = form.handleSubmit(async (values) => {
    setError(null);
    try {
      if (profile) await update.mutateAsync({ profileId: profile.profile_id, data: toUpdateProfileRequest(values) });
      else await create.mutateAsync({ data: toCreateProfileRequest(values) });
      toast.success(profile ? 'پروفایل به‌روزرسانی شد.' : 'پروفایل فریلنسری ساخته شد.');
      if (profile) {
        router.refresh();
      } else {
        router.replace('/freelancer');
      }
    } catch (thrown) {
      const normalized = getApiError(thrown);
      if (normalized.status === 401) return router.replace('/login?expired=1');
      setError(normalized);
      for (const [name, message] of Object.entries(normalized.fields)) form.setError(name as keyof ProfileValues, { type: 'server', message });
    }
  });

  return <FormProvider {...form}><form onSubmit={onSubmit} noValidate className="grid gap-6">
    <FormErrorSummary errors={form.formState.errors} labels={labels} />
    {error ? <Alert variant="destructive"><AlertTitle>{profile ? 'پروفایل ذخیره نشد' : 'پروفایل ساخته نشد'}</AlertTitle><AlertDescription>{error.message}</AlertDescription></Alert> : null}
    <div className="grid gap-5 sm:grid-cols-2"><TextField label="نام نمایشی" name="display_name" required disabled={pending} /><TextField label="عنوان حرفه‌ای" name="headline" disabled={pending} /></div>
    <TextareaField label="درباره من" name="bio" rows={5} disabled={pending} />
    <div className="grid gap-5 sm:grid-cols-3"><TextField label="کد کشور" name="country_code" ltr disabled={pending} /><TextField label="شهر" name="city" disabled={pending} /><TextField label="منطقه زمانی" name="timezone" ltr disabled={pending} /></div>
    {profile ? <div className="grid gap-5 sm:grid-cols-2"><AmountField label="حداقل نرخ ساعتی" name="hourly_rate_min" disabled={pending} /><AmountField label="حداکثر نرخ ساعتی" name="hourly_rate_max" disabled={pending} /></div> : null}
    <div className="flex justify-end"><Button type="submit" disabled={pending}>{pending ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}{profile ? 'ذخیره پروفایل' : 'ساخت پروفایل'}</Button></div>
  </form></FormProvider>;
}
