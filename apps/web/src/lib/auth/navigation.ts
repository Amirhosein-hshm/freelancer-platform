import {
  FolderKanban,
  Gauge,
  Inbox,
  ScrollText,
  ShieldCheck,
  Sparkles,
  Ticket,
  UserRound,
  type LucideIcon,
} from 'lucide-react';
import type { UserMeResponse } from '@/generated/api/models';

export interface SubNavItem {
  href: string;
  label: string;
  icon?: LucideIcon;
}

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Restricts an item to exactly one primary role for highlighting. */
  primary?: boolean;
  children?: SubNavItem[];
}

export const ROLES = {
  customer: 'customer',
  freelancer: 'freelancer',
  supervisor: 'supervisor',
  admin: 'admin',
} as const;

export type RoleKey = (typeof ROLES)[keyof typeof ROLES];

export function hasRole(user: Pick<UserMeResponse, 'roles'>, role: string): boolean {
  return user.roles.includes(role);
}

export function getPrimaryRole(user: Pick<UserMeResponse, 'roles'>): RoleKey | 'customer' {
  if (hasRole(user, ROLES.admin)) return ROLES.admin;
  if (hasRole(user, ROLES.supervisor)) return ROLES.supervisor;
  if (hasRole(user, ROLES.freelancer)) return ROLES.freelancer;
  return ROLES.customer;
}

export const ROLE_LABELS: Record<string, string> = {
  customer: 'مشتری',
  freelancer: 'فریلنسر',
  supervisor: 'ناظر',
  admin: 'مدیر سامانه',
};

/**
 * Role-aware navigation. The backend stays authoritative — this only decides
 * what to show; every action still handles backend 401/403 responses.
 */
export function getNavItems(user: Pick<UserMeResponse, 'roles'>): NavItem[] {
  const items: NavItem[] = [
    { href: '/dashboard', label: 'داشبورد', icon: Gauge, primary: true },
  ];

  if (hasRole(user, ROLES.customer) || hasRole(user, ROLES.admin)) {
    items.push({ href: '/projects', label: 'پروژه‌های من', icon: FolderKanban, primary: true });
  }

  if (hasRole(user, ROLES.freelancer)) {
    items.push({ href: '/projects/my-project', label: 'پروژه‌های من', icon: FolderKanban, primary: true });
    items.push({ href: '/projects/available', label: 'پروژه‌های موجود', icon: Sparkles, primary: true });
    items.push({ href: '/freelancer', label: 'پروفایل فریلنسری', icon: UserRound, primary: true });
  }

  if (hasRole(user, ROLES.supervisor)) {
    items.push({ href: '/reviews', label: 'صف بازبینی', icon: ScrollText, primary: true });
  }

  if (hasRole(user, ROLES.admin)) {
    items.push({
      href: '/admin',
      label: 'مدیریت سامانه',
      icon: ShieldCheck,
      primary: true,
      children: [
        { href: '/admin/projects', label: 'همه پروژه‌ها' },
        { href: '/admin/users', label: 'کاربران و نقش‌ها' },
        { href: '/admin/freelancers', label: 'فریلنسرها' },
        { href: '/admin/on-behalf', label: 'عملیات از طرف کاربران' },
        { href: '/admin/categories', label: 'دسته‌بندی‌ها' },
        { href: '/admin/form-templates', label: 'قالب‌های فرم' },
        { href: '/admin/reports', label: 'گزارش‌ها' },
      ],
    });
  }

  items.push({ href: '/tickets', label: 'پشتیبانی', icon: Ticket });
  items.push({ href: '/reports', label: 'گزارش‌ها', icon: Inbox });

  return items;
}

/** Where an authenticated user should land right after login. */
export function getDashboardEntry(user: UserMeResponse): string {
  if (hasRole(user, ROLES.freelancer) && user.freelancer_onboarding_needed) {
    return '/freelancer/onboarding';
  }
  return '/dashboard';
}
