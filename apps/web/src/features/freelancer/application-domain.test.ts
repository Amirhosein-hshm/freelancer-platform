import { describe, expect, it } from 'vitest';
import { applicationSchema, toApplicationRequest } from './application-domain';

describe('freelancer application data', () => {
  it('allows an empty optional proposal and maps blanks to null', () => {
    const values = { cover_letter: '', proposed_amount: '', proposed_days: '' };
    expect(applicationSchema.safeParse(values).success).toBe(true);
    expect(toApplicationRequest(values)).toEqual({ cover_letter: null, proposed_amount: null, proposed_days: null });
  });

  it('validates and maps amount and duration', () => {
    expect(applicationSchema.safeParse({ cover_letter: 'متن', proposed_amount: '12.5', proposed_days: '7' }).success).toBe(true);
    expect(applicationSchema.safeParse({ cover_letter: '', proposed_amount: 'x', proposed_days: '0' }).success).toBe(false);
    expect(toApplicationRequest({ cover_letter: 'متن', proposed_amount: '12.5', proposed_days: '7' })).toMatchObject({ proposed_amount: '12.5', proposed_days: 7 });
  });
});
