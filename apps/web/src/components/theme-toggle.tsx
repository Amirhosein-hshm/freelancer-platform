'use client';

import { Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { readThemeMode, setThemeMode } from '@/lib/theme';

/**
 * Reads the theme lazily on first interaction instead of during an effect:
 * the inline <head> script already applied the correct class before paint,
 * so the DOM is the single source of truth.
 */
export function ThemeToggle() {
  // Keep the server and first client render identical; the layout bootstrap
  // already applies the correct class before paint.
  const [dark, setDark] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setDark(readThemeMode() === 'dark');
  }, []);

  const toggle = () => {
    const next = readThemeMode() === 'dark' ? 'light' : 'dark';
    setDark(next === 'dark');
    setThemeMode(next);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      aria-label={dark ? 'تغییر به حالت روشن' : 'تغییر به حالت تاریک'}
    >
      {dark ? <Sun size={18} /> : <Moon size={18} />}
    </Button>
  );
}
