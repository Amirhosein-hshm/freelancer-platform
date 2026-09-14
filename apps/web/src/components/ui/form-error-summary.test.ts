import { describe, expect, it } from 'vitest';
import type { FieldErrors } from 'react-hook-form';
import { collectFieldErrors } from './form-error-summary';

const LABELS = {
  email: 'ایمیل',
  password: 'گذرواژه',
  'profile.city': 'شهر',
  'skills.0.name': 'نام مهارت',
};

describe('collectFieldErrors', () => {
  it('returns one entry per errored field, labelled', () => {
    const errors = {
      email: { type: 'required', message: 'ایمیل الزامی است' },
      password: { type: 'min', message: 'گذرواژه کوتاه است' },
    } as unknown as FieldErrors;

    expect(collectFieldErrors(errors, LABELS)).toEqual([
      { name: 'email', label: 'ایمیل', message: 'ایمیل الزامی است' },
      { name: 'password', label: 'گذرواژه', message: 'گذرواژه کوتاه است' },
    ]);
  });

  it('flattens nested objects into dotted paths', () => {
    const errors = {
      profile: { city: { type: 'required', message: 'شهر الزامی است' } },
    } as unknown as FieldErrors;

    expect(collectFieldErrors(errors, LABELS)).toEqual([
      { name: 'profile.city', label: 'شهر', message: 'شهر الزامی است' },
    ]);
  });

  it('flattens array fields, keeping the index in the path', () => {
    const errors = {
      skills: [{ name: { type: 'required', message: 'نام الزامی است' } }],
    } as unknown as FieldErrors;

    // The dotted path must match the `name` attribute React Hook Form renders,
    // otherwise the summary cannot focus the field.
    expect(collectFieldErrors(errors, LABELS)).toEqual([
      { name: 'skills.0.name', label: 'نام مهارت', message: 'نام الزامی است' },
    ]);
  });

  it('falls back to the field path when no label is supplied', () => {
    const errors = { nickname: { message: 'نامعتبر' } } as unknown as FieldErrors;
    expect(collectFieldErrors(errors, LABELS)).toEqual([
      { name: 'nickname', label: 'nickname', message: 'نامعتبر' },
    ]);
  });

  it('skips nodes with no message rather than emitting a blank row', () => {
    const errors = {
      email: { type: 'required' },
      password: { type: 'min', message: '' },
    } as unknown as FieldErrors;

    expect(collectFieldErrors(errors, LABELS)).toEqual([]);
  });

  it('returns nothing for a valid form', () => {
    expect(collectFieldErrors({}, LABELS)).toEqual([]);
  });
});
