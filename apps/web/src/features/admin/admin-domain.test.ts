import { describe, expect, it } from 'vitest';
import { adminUserSchema, categorySchema, supervisorAssignmentSchema } from './admin-domain';

describe('admin schemas', () => {
  it('validates user creation and password length', () => {
    expect(adminUserSchema.safeParse({ email: 'admin@example.com', password: '12345678', first_name: 'A', last_name: 'B' }).success).toBe(true);
    expect(adminUserSchema.safeParse({ email: 'bad', password: 'short', first_name: '', last_name: '' }).success).toBe(false);
  });
  it('validates categories and supervisor assignments', () => {
    expect(categorySchema.safeParse({ name: 'Video', slug: 'video', category_key: 'video' }).success).toBe(true);
    expect(supervisorAssignmentSchema.safeParse({ supervisor_user_id: 'user-1' }).success).toBe(true);
    expect(supervisorAssignmentSchema.safeParse({ supervisor_user_id: '' }).success).toBe(false);
  });
});
