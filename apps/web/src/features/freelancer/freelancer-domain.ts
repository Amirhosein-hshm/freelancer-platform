import { z } from 'zod';
import type { CreateFreelancerProfileRequest, FreelancerProfileResponse, UpdateFreelancerProfileRequest } from '@/generated/api/models';

const optionalText = z.string().trim();
const optionalAmount = z.string().trim().refine((value) => value === '' || /^\d+(?:\.\d+)?$/.test(value), 'مبلغ معتبر وارد کنید.');

export const profileSchema = z.object({
  display_name: z.string().trim().min(1, 'نام نمایشی را وارد کنید.'),
  headline: optionalText,
  bio: optionalText,
  country_code: optionalText,
  city: optionalText,
  timezone: optionalText,
  hourly_rate_min: optionalAmount,
  hourly_rate_max: optionalAmount,
});

export const resumeSchema = z.object({ summary: optionalText, file_asset_id: z.string().min(1, 'فایل رزومه را بارگذاری کنید.') });
export const resumeSummarySchema = z.object({ summary: optionalText });
export const portfolioSchema = z.object({
  title: z.string().trim().min(1, 'عنوان نمونه‌کار را وارد کنید.'),
  description: optionalText,
  external_url: z.string().trim().refine((value) => value === '' || URL.canParse(value), 'نشانی اینترنتی معتبر وارد کنید.'),
  file_asset_id: z.string(),
  display_order: z.string().trim().regex(/^-?\d+$/, 'ترتیب نمایش باید عدد صحیح باشد.'),
  is_featured: z.boolean(),
});

export type ProfileValues = z.infer<typeof profileSchema>;
export type ResumeValues = z.infer<typeof resumeSchema>;
export type ResumeSummaryValues = z.infer<typeof resumeSummarySchema>;
export type PortfolioValues = z.infer<typeof portfolioSchema>;

const nullable = (value: string): string | null => value === '' ? null : value;

export function toProfileValues(profile?: FreelancerProfileResponse): ProfileValues {
  return {
    display_name: profile?.display_name ?? '', headline: profile?.headline ?? '', bio: profile?.bio ?? '',
    country_code: profile?.country_code ?? '', city: profile?.city ?? '', timezone: profile?.timezone ?? '',
    hourly_rate_min: profile?.hourly_rate_min ?? '', hourly_rate_max: profile?.hourly_rate_max ?? '',
  };
}

export function toCreateProfileRequest(values: ProfileValues): CreateFreelancerProfileRequest {
  return { display_name: values.display_name.trim(), headline: nullable(values.headline), bio: nullable(values.bio), country_code: nullable(values.country_code), city: nullable(values.city), timezone: nullable(values.timezone) };
}

export function toUpdateProfileRequest(values: ProfileValues): UpdateFreelancerProfileRequest {
  return { ...toCreateProfileRequest(values), hourly_rate_min: nullable(values.hourly_rate_min), hourly_rate_max: nullable(values.hourly_rate_max) };
}

export const APPROVAL_LABELS: Record<string, string> = { pending: 'در انتظار بررسی', approved: 'تأییدشده', rejected: 'ردشده', suspended: 'تعلیق‌شده' };
export const LEVEL_LABELS: Record<string, string> = { junior: 'مقدماتی', mid_level: 'میانی', senior: 'ارشد' };
