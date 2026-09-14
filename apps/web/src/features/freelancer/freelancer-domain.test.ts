import { describe, expect, it } from 'vitest';
import { profileSchema, toCreateProfileRequest, toUpdateProfileRequest } from './freelancer-domain';

const values = { display_name: '  نام  ', headline: '', bio: '', country_code: 'IR', city: '', timezone: '', hourly_rate_min: '10.5', hourly_rate_max: '' };

describe('freelancer profile data', () => {
  it('requires a non-empty display name and validates decimal rates', () => {
    expect(profileSchema.safeParse({ ...values, display_name: ' ' }).success).toBe(false);
    expect(profileSchema.safeParse({ ...values, hourly_rate_min: 'abc' }).success).toBe(false);
    expect(profileSchema.safeParse(values).success).toBe(true);
  });

  it('maps create and update requests without invented fields', () => {
    expect(toCreateProfileRequest(values)).toEqual({ display_name: 'نام', headline: null, bio: null, country_code: 'IR', city: null, timezone: null });
    expect(toUpdateProfileRequest(values)).toMatchObject({ display_name: 'نام', hourly_rate_min: '10.5', hourly_rate_max: null });
  });
});
