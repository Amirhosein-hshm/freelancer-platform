import { describe, expect, it } from 'vitest';
import { ratingSchema } from './project-rating';

describe('ratingSchema', () => {
  it('accepts scores from one through five', () => {
    for (const score of [1, 2, 3, 4, 5]) {
      expect(ratingSchema.safeParse({ score, comment: '', is_public: false }).success).toBe(true);
    }
  });

  it('rejects scores outside the backend range', () => {
    expect(ratingSchema.safeParse({ score: 0, comment: '', is_public: false }).success).toBe(false);
    expect(ratingSchema.safeParse({ score: 6, comment: '', is_public: true }).success).toBe(false);
  });
});
