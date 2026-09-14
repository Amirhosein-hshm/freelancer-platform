import { describe, expect, it } from 'vitest';
import { ApiError, getApiError, parseErrorBody } from './errors';

describe('parseErrorBody', () => {
  it('parses a FastAPI error envelope', () => {
    const body = { success: false, error: { code: 'invalid_credentials', message: 'اطلاعات ورود نادرست است.' } };
    expect(parseErrorBody(body)).toEqual({
      code: 'invalid_credentials',
      message: 'اطلاعات ورود نادرست است.',
      fields: {},
    });
  });

  it('maps FastAPI 422 loc/msg arrays to field errors', () => {
    const body = {
      success: false,
      error: {
        code: 'validation_error',
        message: 'Validation error',
        details: [
          { loc: ['body', 'password'], msg: 'String should have at least 8 characters' },
          { loc: ['body', 'email'], msg: 'value is not a valid email address' },
        ],
      },
    };
    expect(parseErrorBody(body).fields).toEqual({
      password: 'String should have at least 8 characters',
      email: 'value is not a valid email address',
    });
  });

  it('maps dict-style details to field errors', () => {
    const body = {
      success: false,
      error: { code: 'validation_error', message: 'خطا', details: { email: 'این ایمیل قبلاً ثبت شده است.' } },
    };
    expect(parseErrorBody(body).fields).toEqual({ email: 'این ایمیل قبلاً ثبت شده است.' });
  });

  it('falls back to a network error for non-envelope bodies', () => {
    expect(parseErrorBody(undefined).code).toBe('unknown_error');
    expect(parseErrorBody('nope').code).toBe('unknown_error');
  });
});

describe('ApiError', () => {
  it('exposes status helpers', () => {
    const unauthorized = new ApiError(401, 'token_expired', 'expired');
    expect(unauthorized.isUnauthorized).toBe(true);
    const forbidden = new ApiError(403, 'forbidden', 'forbidden');
    expect(forbidden.isForbidden).toBe(true);
    const validation = new ApiError(422, 'validation_error', 'invalid');
    expect(validation.isValidation).toBe(true);
  });
});

describe('getApiError', () => {
  it('normalizes ApiError instances', () => {
    const error = new ApiError(409, 'conflict', 'تعارض', { email: 'تکراری' });
    expect(getApiError(error)).toEqual(error.toNormalized());
  });

  it('normalizes legacy {status, body} throws', () => {
    const normalized = getApiError({ status: 401, body: { error: { code: 'unauthorized', message: 'لازم است وارد شوید.' } } });
    expect(normalized.status).toBe(401);
    expect(normalized.message).toBe('لازم است وارد شوید.');
  });

  it('normalizes unknown throws to a network error', () => {
    const normalized = getApiError(new Error('fetch failed'));
    expect(normalized.status).toBe(0);
    expect(normalized.code).toBe('network_error');
    expect(normalized.message).toBeTruthy();
  });
});
