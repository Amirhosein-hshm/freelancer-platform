import { describe, expect, it } from 'vitest';
import { getNavItems, getPrimaryRole, hasRole, ROLE_LABELS, getDashboardEntry } from './navigation';
import type { UserMeResponse } from '@/generated/api/models';

function user(roles: string[], overrides: Partial<UserMeResponse> = {}): UserMeResponse {
  return {
    user_id: 'u1',
    email: 'user@example.com',
    roles,
    permissions: [],
    freelancer_profile_id: null,
    freelancer_onboarding_needed: false,
    freelancer_approval_status: null,
    freelancer_level: null,
    ...overrides,
  };
}

describe('hasRole / getPrimaryRole', () => {
  it('detects roles case-sensitively from the backend list', () => {
    const u = user(['customer']);
    expect(hasRole(u, 'customer')).toBe(true);
    expect(hasRole(u, 'admin')).toBe(false);
  });

  it('prefers admin, then supervisor, then freelancer, then customer', () => {
    expect(getPrimaryRole(user(['admin']))).toBe('admin');
    expect(getPrimaryRole(user(['supervisor', 'customer']))).toBe('supervisor');
    expect(getPrimaryRole(user(['freelancer', 'customer']))).toBe('freelancer');
    expect(getPrimaryRole(user([]))).toBe('customer');
  });
});

describe('getNavItems', () => {
  it('always shows dashboard, tickets, and reports', () => {
    const items = getNavItems(user(['customer']));
    const hrefs = items.map((item) => item.href);
    expect(hrefs).toContain('/dashboard');
    expect(hrefs).toContain('/tickets');
    expect(hrefs).toContain('/reports');
  });

  it('shows customer project management only for customers and admins', () => {
    expect(getNavItems(user(['customer'])).some((i) => i.href === '/projects')).toBe(true);
    expect(getNavItems(user(['admin'])).some((i) => i.href === '/projects')).toBe(true);
    expect(getNavItems(user(['freelancer'])).some((i) => i.href === '/projects')).toBe(false);
    expect(getNavItems(user(['supervisor'])).some((i) => i.href === '/projects')).toBe(false);
  });

  it('shows freelancer surfaces only for freelancers', () => {
    const hrefs = getNavItems(user(['freelancer'])).map((i) => i.href);
    expect(hrefs).toContain('/projects/available');
    expect(hrefs).toContain('/freelancer');
    expect(getNavItems(user(['customer'])).some((i) => i.href === '/freelancer')).toBe(false);
  });

  it('shows review queue only for supervisors and admin area only for admins', () => {
    expect(getNavItems(user(['supervisor'])).some((i) => i.href === '/reviews')).toBe(true);
    expect(getNavItems(user(['customer'])).some((i) => i.href === '/reviews')).toBe(false);
    expect(getNavItems(user(['admin'])).some((i) => i.href === '/admin')).toBe(true);
    expect(getNavItems(user(['supervisor'])).some((i) => i.href === '/admin')).toBe(false);
  });
});

describe('getDashboardEntry', () => {
  it('routes freelancers needing onboarding to the onboarding flow', () => {
    expect(getDashboardEntry(user(['freelancer'], { freelancer_onboarding_needed: true }))).toBe(
      '/freelancer/onboarding',
    );
  });

  it('routes everyone else to the dashboard', () => {
    expect(getDashboardEntry(user(['freelancer'], { freelancer_onboarding_needed: false }))).toBe('/dashboard');
    expect(getDashboardEntry(user(['customer']))).toBe('/dashboard');
  });
});

describe('ROLE_LABELS', () => {
  it('labels all known roles', () => {
    for (const role of ['customer', 'freelancer', 'supervisor', 'admin']) {
      expect(ROLE_LABELS[role]).toBeTruthy();
    }
  });
});
