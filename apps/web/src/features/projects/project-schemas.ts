import { z } from 'zod';
import {
  BudgetType,
  FormFieldType,
  FreelancerLevelEnum,
  ProjectPriority,
  ProjectVisibility,
  type FormFieldResponse,
} from '@/generated/api/models';

/**
 * Project create/edit form.
 *
 * The backend's own schema marks every budget amount optional, so the rules
 * below are not a copy of its validation — they only reject states that
 * contradict the user's own choice (asking for a fixed budget and naming no
 * amount). Anything the backend enforces beyond this arrives as a 422 and is
 * shown verbatim; nothing here tries to predict it.
 */

/** Matches the backend's decimal-string pattern for money fields. */
const AMOUNT_PATTERN = /^\d+(?:\.\d+)?$/;

const amountField = z
  .string()
  .trim()
  .refine((value) => value === '' || AMOUNT_PATTERN.test(value), {
    message: 'مبلغ را با رقم و بدون جداکننده وارد کنید.',
  });

export const projectFormShape = {
  category_id: z.string().min(1, 'دسته‌بندی را انتخاب کنید.'),
  form_template_id: z.string().min(1, 'قالب فرم را انتخاب کنید.'),
  title: z
    .string()
    .trim()
    .min(3, 'عنوان باید حداقل ۳ نویسه باشد.')
    .max(200, 'عنوان حداکثر ۲۰۰ نویسه است.'),
  description: z.string().trim().min(10, 'توضیحات باید حداقل ۱۰ نویسه باشد.'),
  visibility: z.enum(ProjectVisibility, { message: 'سطح دسترسی را انتخاب کنید.' }),
  budget_type: z.enum(BudgetType, { message: 'نوع بودجه را انتخاب کنید.' }),
  currency_code: z.string().trim().min(1, 'واحد پول را انتخاب کنید.'),
  priority: z.enum(ProjectPriority, { message: 'اولویت را انتخاب کنید.' }),
  /** '' means "no minimum level required". */
  required_level: z.union([z.enum(FreelancerLevelEnum), z.literal('')]),
  fixed_budget: amountField,
  budget_min: amountField,
  budget_max: amountField,
  /** `datetime-local` text, read as Tehran time on submit. */
  application_deadline: z.string(),
  /** Dynamic template answers, keyed by field_id. */
  form_values: z.record(z.string(), z.string()),
} as const;

export type ProjectFormValues = z.infer<z.ZodObject<typeof projectFormShape>>;

/**
 * Builds the resolver schema for a specific template, so required template
 * fields are validated before the request rather than after a 422.
 */
export function buildProjectFormSchema(fields: FormFieldResponse[]) {
  return z
    .object(projectFormShape)
    .superRefine((values, ctx) => {
      checkBudget(values, ctx);
      checkDeadline(values, ctx);
      checkTemplateFields(values, ctx, fields);
    });
}

type Ctx = z.RefinementCtx;

function checkBudget(values: ProjectFormValues, ctx: Ctx): void {
  const needsSingleAmount =
    values.budget_type === BudgetType.fixed || values.budget_type === BudgetType.hourly;

  if (needsSingleAmount && values.fixed_budget === '') {
    ctx.addIssue({
      code: 'custom',
      path: ['fixed_budget'],
      message:
        values.budget_type === BudgetType.fixed
          ? 'برای بودجه مقطوع، مبلغ را وارد کنید.'
          : 'برای بودجه ساعتی، نرخ هر ساعت را وارد کنید.',
    });
  }

  if (values.budget_type !== BudgetType.range) return;

  if (values.budget_min === '') {
    ctx.addIssue({ code: 'custom', path: ['budget_min'], message: 'کمینه بودجه را وارد کنید.' });
  }
  if (values.budget_max === '') {
    ctx.addIssue({ code: 'custom', path: ['budget_max'], message: 'بیشینه بودجه را وارد کنید.' });
  }
  if (
    values.budget_min !== '' &&
    values.budget_max !== '' &&
    AMOUNT_PATTERN.test(values.budget_min) &&
    AMOUNT_PATTERN.test(values.budget_max) &&
    Number(values.budget_min) > Number(values.budget_max)
  ) {
    ctx.addIssue({
      code: 'custom',
      path: ['budget_max'],
      message: 'بیشینه بودجه نباید از کمینه کمتر باشد.',
    });
  }
}

function checkDeadline(values: ProjectFormValues, ctx: Ctx): void {
  if (values.application_deadline === '') return;
  // The browser's own datetime-local validation catches malformed text; this
  // only guards against a value that survived it (a pasted string, autofill).
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?$/.test(values.application_deadline)) {
    ctx.addIssue({
      code: 'custom',
      path: ['application_deadline'],
      message: 'تاریخ و ساعت مهلت را کامل وارد کنید.',
    });
  }
}

function checkTemplateFields(values: ProjectFormValues, ctx: Ctx, fields: FormFieldResponse[]): void {
  for (const field of fields) {
    if (!field.is_required || !field.is_active) continue;
    const answer = values.form_values[field.field_id] ?? '';
    // A boolean's "false" is an answer; every other type needs actual content.
    const isAnswered = field.field_type === FormFieldType.boolean ? answer !== '' : answer.trim() !== '';
    if (!isAnswered) {
      ctx.addIssue({
        code: 'custom',
        path: ['form_values', field.field_id],
        message: `${field.label} الزامی است.`,
      });
    }
  }
}

/** Only fields the user can actually answer are rendered or validated. */
export function activeTemplateFields(fields: FormFieldResponse[] | undefined): FormFieldResponse[] {
  return (fields ?? [])
    .filter((field) => field.is_active)
    .sort((a, b) => a.sort_order - b.sort_order);
}
