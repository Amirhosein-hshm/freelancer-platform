import { z } from 'zod';
import type { ApplyForProjectRequest } from '@/generated/api/models';

export const applicationSchema = z.object({
  cover_letter: z.string().trim(),
  proposed_amount: z.string().trim().refine((value) => value === '' || /^\d+(?:\.\d+)?$/.test(value), 'مبلغ پیشنهادی معتبر وارد کنید.'),
  proposed_days: z.string().trim().refine((value) => value === '' || /^\d+$/.test(value) && Number(value) >= 1, 'تعداد روز باید عدد صحیح مثبت باشد.'),
});

export type ApplicationValues = z.infer<typeof applicationSchema>;

export function toApplicationRequest(values: ApplicationValues): ApplyForProjectRequest {
  return {
    cover_letter: values.cover_letter === '' ? null : values.cover_letter,
    proposed_amount: values.proposed_amount === '' ? null : values.proposed_amount,
    proposed_days: values.proposed_days === '' ? null : Number(values.proposed_days),
  };
}
