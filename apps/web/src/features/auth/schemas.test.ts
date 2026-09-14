import { describe, expect, it } from 'vitest';
import { loginSchema, registerSchema, changePasswordSchema, forgotPasswordSchema } from './schemas';

describe('loginSchema', () => {
  it('accepts valid credentials', () => {
    const result = loginSchema.safeParse({ email: 'user@example.com', password: 'secret' });
    expect(result.success).toBe(true);
  });

  it('rejects missing password and invalid email', () => {
    const result = loginSchema.safeParse({ email: 'not-an-email', password: '' });
    expect(result.success).toBe(false);
  });
});

describe('registerSchema', () => {
  const valid = {
    first_name: 'سارا',
    last_name: 'احمدی',
    email: 'sara@example.com',
    password: 'Password1',
    confirm_password: 'Password1',
    role: 'customer',
  };

  it('accepts a valid submission', () => {
    expect(registerSchema.safeParse(valid).success).toBe(true);
  });

  it('rejects short passwords', () => {
    const result = registerSchema.safeParse({ ...valid, password: 'short', confirm_password: 'short' });
    expect(result.success).toBe(false);
  });

  it('rejects mismatched confirmation', () => {
    const result = registerSchema.safeParse({ ...valid, confirm_password: 'Different1' });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('confirm_password');
    }
  });

  it('rejects unknown roles', () => {
    const result = registerSchema.safeParse({ ...valid, role: 'admin' });
    expect(result.success).toBe(false);
  });

  it('trims names', () => {
    const result = registerSchema.parse({ ...valid, first_name: '  سارا  ' });
    expect(result.first_name).toBe('سارا');
  });
});

describe('changePasswordSchema', () => {
  it('accepts matching new passwords', () => {
    const result = changePasswordSchema.safeParse({
      old_password: 'OldPass1',
      new_password: 'NewPass12',
      confirm_password: 'NewPass12',
    });
    expect(result.success).toBe(true);
  });

  it('rejects mismatch and short new password', () => {
    expect(
      changePasswordSchema.safeParse({ old_password: 'a', new_password: 'NewPass12', confirm_password: 'Other' }).success,
    ).toBe(false);
    expect(
      changePasswordSchema.safeParse({ old_password: 'a', new_password: 'short', confirm_password: 'short' }).success,
    ).toBe(false);
  });
});

describe('forgotPasswordSchema', () => {
  it('requires a valid email', () => {
    expect(forgotPasswordSchema.safeParse({ email: 'a@b.com' }).success).toBe(true);
    expect(forgotPasswordSchema.safeParse({ email: 'nope' }).success).toBe(false);
  });
});
