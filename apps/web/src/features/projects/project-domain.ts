import {
  BudgetType,
  DeliveryStatus,
  FreelancerLevelEnum,
  ProjectApplicationStatus,
  ProjectPriority,
  ProjectStatus,
  ProjectVisibility,
  ReviewStatus,
  type BudgetResponse,
} from '@/generated/api/models';
import type { ProjectResponse } from '@/generated/api/models';

export interface EffectiveProjectSupervisor { user_id: string; email: string; first_name: string; last_name: string }
export function getProjectSupervisor(project: ProjectResponse): EffectiveProjectSupervisor | null {
  return ((project as unknown as { supervisor?: EffectiveProjectSupervisor | null }).supervisor ?? null);
}

/**
 * Persian labels and lifecycle capabilities for projects.
 *
 * The capability helpers below read the project's own `status` — a value the
 * backend computed and returned — and decide what to *offer*. They are not a
 * permission model: the backend re-checks ownership, role and lifecycle on every
 * call, and each action surfaces its 403/409/422 verbatim. Hiding an action the
 * backend would reject keeps the UI honest; showing one it would allow is never
 * prevented here.
 */

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  draft: 'پیش‌نویس',
  published: 'منتشر شده',
  collecting_applications: 'در حال دریافت درخواست',
  assigned: 'واگذار شده',
  in_progress: 'در حال انجام',
  delivery_submitted: 'تحویل ارسال شده',
  under_supervisor_review: 'در بازبینی ناظر',
  revision_requested: 'نیازمند اصلاح',
  awaiting_customer_review: 'در انتظار تأیید شما',
  completed: 'تکمیل شده',
  cancelled: 'لغو شده',
  archived: 'بایگانی شده',
};

export type BadgeTone = 'default' | 'secondary' | 'destructive' | 'outline';

export const PROJECT_STATUS_TONES: Record<ProjectStatus, BadgeTone> = {
  draft: 'outline',
  published: 'secondary',
  collecting_applications: 'secondary',
  assigned: 'default',
  in_progress: 'default',
  delivery_submitted: 'default',
  under_supervisor_review: 'secondary',
  revision_requested: 'destructive',
  awaiting_customer_review: 'default',
  completed: 'secondary',
  cancelled: 'destructive',
  archived: 'outline',
};

export const PROJECT_PRIORITY_LABELS: Record<ProjectPriority, string> = {
  low: 'کم',
  normal: 'معمولی',
  high: 'زیاد',
  urgent: 'فوری',
};

export const PROJECT_VISIBILITY_LABELS: Record<ProjectVisibility, string> = {
  public: 'عمومی',
  private: 'خصوصی',
  invite_only: 'فقط با دعوت',
};

export const BUDGET_TYPE_LABELS: Record<BudgetType, string> = {
  fixed: 'مقطوع',
  range: 'بازه‌ای',
  hourly: 'ساعتی',
  negotiable: 'توافقی',
};

export const FREELANCER_LEVEL_LABELS: Record<FreelancerLevelEnum, string> = {
  junior: 'تازه‌کار',
  mid_level: 'میان‌رده',
  senior: 'ارشد',
};

export const APPLICATION_STATUS_LABELS: Record<ProjectApplicationStatus, string> = {
  applied: 'ارسال شده',
  shortlisted: 'فهرست کوتاه',
  accepted: 'پذیرفته شده',
  rejected: 'رد شده',
  withdrawn: 'پس گرفته شده',
  expired: 'منقضی شده',
};

export const APPLICATION_STATUS_TONES: Record<ProjectApplicationStatus, BadgeTone> = {
  applied: 'secondary',
  shortlisted: 'default',
  accepted: 'default',
  rejected: 'destructive',
  withdrawn: 'outline',
  expired: 'outline',
};

export const DELIVERY_STATUS_LABELS: Record<DeliveryStatus, string> = {
  submitted: 'ارسال شده',
  under_review: 'در بازبینی',
  approved: 'تأیید شده',
  rejected: 'رد شده',
  revised: 'اصلاح شده',
  superseded: 'جایگزین شده',
};

export const DELIVERY_STATUS_TONES: Record<DeliveryStatus, BadgeTone> = {
  submitted: 'secondary',
  under_review: 'secondary',
  approved: 'default',
  rejected: 'destructive',
  revised: 'secondary',
  superseded: 'outline',
};

export const REVIEW_DECISION_LABELS: Record<ReviewStatus, string> = {
  pending: 'در انتظار بررسی',
  approved: 'تأیید شده',
  rejected: 'رد شده',
};

/** Statuses from which no lifecycle action is possible. */
export const TERMINAL_PROJECT_STATUSES: readonly ProjectStatus[] = [
  ProjectStatus.completed,
  ProjectStatus.cancelled,
  ProjectStatus.archived,
];

export function isTerminalStatus(status: ProjectStatus): boolean {
  return TERMINAL_PROJECT_STATUSES.includes(status);
}

/** DRAFT-only: the backend rejects edits and deletes in any other status. */
export function canEditDraft(status: ProjectStatus): boolean {
  return status === ProjectStatus.draft;
}

export function canDeleteProject(status: ProjectStatus): boolean {
  return status === ProjectStatus.draft;
}

export function canPublishProject(status: ProjectStatus): boolean {
  return status === ProjectStatus.draft;
}

/** Start becomes available once a freelancer has been accepted. */
export function canStartProject(status: ProjectStatus): boolean {
  return status === ProjectStatus.assigned;
}

/** A freelancer can create a delivery version while work is active or revisions are requested. */
export function canSubmitFreelancerDelivery(status: ProjectStatus): boolean {
  return status === ProjectStatus.in_progress || status === ProjectStatus.revision_requested;
}

/** Explains the next lifecycle step when the freelancer has no submit action. */
export function getFreelancerProjectStatusMessage(status: ProjectStatus): string {
  switch (status) {
    case ProjectStatus.assigned:
      return 'پروژه به شما واگذار شده است. پس از شروع پروژه توسط مشتری یا مدیر، امکان ارسال تحویل فعال می‌شود.';
    case ProjectStatus.delivery_submitted:
    case ProjectStatus.under_supervisor_review:
      return 'تحویل شما ثبت شده و در حال بررسی است. پس از اعلام نتیجه، وضعیت بعدی پروژه اینجا نمایش داده می‌شود.';
    case ProjectStatus.awaiting_customer_review:
      return 'تحویل توسط ناظر تأیید شده و اکنون در انتظار تأیید نهایی مشتری است.';
    case ProjectStatus.completed:
      return 'این پروژه تکمیل شده است و میزکار در حالت فقط‌خواندنی قرار دارد.';
    case ProjectStatus.cancelled:
      return 'این پروژه لغو شده است و امکان ارسال تحویل جدید وجود ندارد.';
    case ProjectStatus.archived:
      return 'این پروژه بایگانی شده است و امکان انجام اقدام جدید وجود ندارد.';
    default:
      return 'در وضعیت فعلی، اقدام جدیدی برای این پروژه در دسترس نیست.';
  }
}

/** Cancel is allowed while the project has not reached a terminal status. */
export function canCancelProject(status: ProjectStatus): boolean {
  return !isTerminalStatus(status);
}

/** Applications are only worth reviewing while the project is still open. */
export function canReviewApplications(status: ProjectStatus): boolean {
  return (
    status === ProjectStatus.published ||
    status === ProjectStatus.collecting_applications
  );
}

/** The customer's approve/reject decision on the supervisor-cleared delivery. */
export function canSubmitCustomerReview(status: ProjectStatus): boolean {
  return status === ProjectStatus.awaiting_customer_review;
}

/** Rating follows a completed project, and only once. */
export function canSubmitRating(status: ProjectStatus, hasRating: boolean): boolean {
  return status === ProjectStatus.completed && !hasRating;
}

/**
 * Human-readable budget. Amounts arrive as decimal strings to avoid float
 * rounding, so they are formatted digit-wise rather than parsed into a number
 * and back — an amount the backend sent is displayed exactly as sent.
 */
export function formatBudget(budget: BudgetResponse): string {
  const currency = formatCurrencyCode(budget.currency_code);

  switch (budget.budget_type) {
    case BudgetType.fixed:
      return budget.fixed_amount === null
        ? BUDGET_TYPE_LABELS.fixed
        : `${formatAmount(budget.fixed_amount)} ${currency}`;
    case BudgetType.hourly:
      return budget.fixed_amount === null
        ? BUDGET_TYPE_LABELS.hourly
        : `${formatAmount(budget.fixed_amount)} ${currency} در ساعت`;
    case BudgetType.range: {
      const min = budget.min_amount;
      const max = budget.max_amount;
      if (min === null && max === null) return BUDGET_TYPE_LABELS.range;
      if (min === null) return `تا ${formatAmount(max!)} ${currency}`;
      if (max === null) return `از ${formatAmount(min)} ${currency}`;
      return `${formatAmount(min)} تا ${formatAmount(max)} ${currency}`;
    }
    case BudgetType.negotiable:
      return BUDGET_TYPE_LABELS.negotiable;
  }
}

const CURRENCY_LABELS: Record<string, string> = {
  IRR: 'ریال',
  IRT: 'تومان',
  USD: 'دلار',
  EUR: 'یورو',
};

function formatCurrencyCode(code: string): string {
  return CURRENCY_LABELS[code.toUpperCase()] ?? code;
}

/**
 * Groups the integer part in threes and converts to Persian digits without
 * going through `Number`, so long decimal strings keep every digit.
 */
export function formatAmount(amount: string): string {
  const trimmed = amount.trim();
  const match = /^([+-]?)(\d*)(?:\.(\d+))?$/.exec(trimmed);
  if (!match) return toPersianDigits(trimmed);

  const [, sign, whole, fraction] = match;
  const grouped = (whole === '' ? '0' : whole).replace(/\B(?=(\d{3})+(?!\d))/g, '٬');
  // A trailing ".00" carries no information for a price; drop a zero fraction.
  const decimals = fraction !== undefined && /[1-9]/.test(fraction) ? `٫${fraction.replace(/0+$/, '')}` : '';
  return toPersianDigits(`${sign}${grouped}${decimals}`);
}

const PERSIAN_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'] as const;

export function toPersianDigits(value: string): string {
  return value.replace(/\d/g, (digit) => PERSIAN_DIGITS[Number(digit)]);
}
