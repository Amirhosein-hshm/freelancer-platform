'use client';

import { useSyncExternalStore } from 'react';

/**
 * Theme access for client components. The inline <head> script in the root
 * layout applies the `dark` class before paint, so the DOM class — not React
 * state — is the single source of truth. This deliberately avoids a
 * next-themes-style provider: there is no cross-route theme state to hold.
 */

export const THEME_STORAGE_KEY = 'didar-theme';

export type ThemeMode = 'light' | 'dark';

export function readThemeMode(): ThemeMode {
  if (typeof document === 'undefined') return 'light';
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
}

export function setThemeMode(mode: ThemeMode): void {
  document.documentElement.classList.toggle('dark', mode === 'dark');
  try {
    localStorage.setItem(THEME_STORAGE_KEY, mode);
  } catch {
    // Private-mode storage denial must not break theming for the session.
  }
}

/**
 * Subscribes to theme changes by observing the documentElement class, so any
 * component (e.g. the toast surface) stays in sync with the toggle without a
 * shared provider.
 *
 * `useSyncExternalStore` rather than an effect: the DOM class is genuinely
 * external state, and this is the one subscription form that reads it during
 * render without a cascading re-render on mount. The server snapshot is
 * `'light'`, matching the pre-hydration markup; the class the inline script may
 * already have applied is picked up on the first post-hydration read.
 */
export function useThemeMode(): ThemeMode {
  return useSyncExternalStore(subscribeToThemeMode, readThemeMode, () => 'light');
}

function subscribeToThemeMode(onChange: () => void): () => void {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class'],
  });
  return () => observer.disconnect();
}
