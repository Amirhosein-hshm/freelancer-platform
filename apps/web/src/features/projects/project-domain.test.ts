import { describe, expect, it } from 'vitest';
import { BudgetType, ProjectStatus, type BudgetResponse } from '@/generated/api/models';
import {
  canCancelProject,
  canDeleteProject,
  canEditDraft,
  canPublishProject,
  canReviewApplications,
  canStartProject,
  canSubmitFreelancerDelivery,
  canSubmitCustomerReview,
  canSubmitRating,
  formatAmount,
  formatBudget,
  isTerminalStatus,
  PROJECT_STATUS_LABELS,
  PROJECT_STATUS_TONES,
  getFreelancerProjectStatusMessage,
} from './project-domain';

function budget(overrides: Partial<BudgetResponse>): BudgetResponse {
  return {
    budget_type: BudgetType.fixed,
    fixed_amount: null,
    min_amount: null,
    max_amount: null,
    currency_code: 'IRT',
    ...overrides,
  };
}

const ALL_STATUSES = Object.values(ProjectStatus);

describe('status labels', () => {
  it('labels and tones every status the backend can send', () => {
    for (const status of ALL_STATUSES) {
      expect(PROJECT_STATUS_LABELS[status]).toBeTypeOf('string');
      expect(PROJECT_STATUS_LABELS[status]).not.toBe('');
      expect(PROJECT_STATUS_TONES[status]).toBeTypeOf('string');
    }
  });
});

describe('lifecycle capabilities', () => {
  it('restricts edit, delete and publish to drafts', () => {
    for (const status of ALL_STATUSES) {
      const isDraft = status === ProjectStatus.draft;
      expect(canEditDraft(status)).toBe(isDraft);
      expect(canDeleteProject(status)).toBe(isDraft);
      expect(canPublishProject(status)).toBe(isDraft);
    }
  });

  it('offers start only after assignment', () => {
    expect(canStartProject(ProjectStatus.assigned)).toBe(true);
    expect(canStartProject(ProjectStatus.published)).toBe(false);
    expect(canStartProject(ProjectStatus.in_progress)).toBe(false);
  });

  it('offers freelancer delivery only while active or revising', () => {
    for (const status of ALL_STATUSES) {
      expect(canSubmitFreelancerDelivery(status)).toBe(
        status === ProjectStatus.in_progress || status === ProjectStatus.revision_requested,
      );
      expect(getFreelancerProjectStatusMessage(status)).toBeTypeOf('string');
    }
  });

  it('offers cancel in every non-terminal status', () => {
    for (const status of ALL_STATUSES) {
      expect(canCancelProject(status)).toBe(!isTerminalStatus(status));
    }
  });

  it('treats completed, cancelled and archived as terminal', () => {
    expect(ALL_STATUSES.filter(isTerminalStatus)).toEqual([
      ProjectStatus.completed,
      ProjectStatus.cancelled,
      ProjectStatus.archived,
    ]);
  });

  it('reviews applications only while the project collects them', () => {
    expect(canReviewApplications(ProjectStatus.published)).toBe(true);
    expect(canReviewApplications(ProjectStatus.collecting_applications)).toBe(true);
    expect(canReviewApplications(ProjectStatus.draft)).toBe(false);
    expect(canReviewApplications(ProjectStatus.assigned)).toBe(false);
  });

  it('opens the customer review only in awaiting_customer_review', () => {
    for (const status of ALL_STATUSES) {
      expect(canSubmitCustomerReview(status)).toBe(status === ProjectStatus.awaiting_customer_review);
    }
  });

  it('allows a rating once, and only after completion', () => {
    expect(canSubmitRating(ProjectStatus.completed, false)).toBe(true);
    expect(canSubmitRating(ProjectStatus.completed, true)).toBe(false);
    expect(canSubmitRating(ProjectStatus.awaiting_customer_review, false)).toBe(false);
  });
});

describe('formatAmount', () => {
  it('groups thousands with the Persian separator', () => {
    expect(formatAmount('1500000')).toBe('۱٬۵۰۰٬۰۰۰');
  });

  it('keeps a meaningful fraction and drops a zero one', () => {
    expect(formatAmount('1200.50')).toBe('۱٬۲۰۰٫۵');
    expect(formatAmount('1200.00')).toBe('۱٬۲۰۰');
  });

  it('preserves precision beyond a float', () => {
    expect(formatAmount('9007199254740993')).toBe('۹٬۰۰۷٬۱۹۹٬۲۵۴٬۷۴۰٬۹۹۳');
  });

  it('passes through anything it cannot parse', () => {
    expect(formatAmount('n/a')).toBe('n/a');
  });
});

describe('formatBudget', () => {
  it('renders a fixed amount with its currency', () => {
    expect(formatBudget(budget({ budget_type: BudgetType.fixed, fixed_amount: '2500000' }))).toBe(
      '۲٬۵۰۰٬۰۰۰ تومان',
    );
  });

  it('marks an hourly rate as per hour', () => {
    expect(formatBudget(budget({ budget_type: BudgetType.hourly, fixed_amount: '350000' }))).toBe(
      '۳۵۰٬۰۰۰ تومان در ساعت',
    );
  });

  it('renders a full, open-ended and empty range', () => {
    expect(
      formatBudget(budget({ budget_type: BudgetType.range, min_amount: '1000', max_amount: '2000' })),
    ).toBe('۱٬۰۰۰ تا ۲٬۰۰۰ تومان');
    expect(formatBudget(budget({ budget_type: BudgetType.range, min_amount: '1000' }))).toBe(
      'از ۱٬۰۰۰ تومان',
    );
    expect(formatBudget(budget({ budget_type: BudgetType.range, max_amount: '2000' }))).toBe(
      'تا ۲٬۰۰۰ تومان',
    );
    expect(formatBudget(budget({ budget_type: BudgetType.range }))).toBe('بازه‌ای');
  });

  it('falls back to the type label when the amount is missing', () => {
    expect(formatBudget(budget({ budget_type: BudgetType.fixed, fixed_amount: null }))).toBe('مقطوع');
    expect(formatBudget(budget({ budget_type: BudgetType.negotiable }))).toBe('توافقی');
  });

  it('shows an unmapped currency code as-is', () => {
    expect(
      formatBudget(budget({ budget_type: BudgetType.fixed, fixed_amount: '10', currency_code: 'GBP' })),
    ).toBe('۱۰ GBP');
  });
});
