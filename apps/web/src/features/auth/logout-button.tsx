'use client';

import { Loader2, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export function LogoutButton() {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  const logout = async () => {
    setPending(true);
    try {
      try {
        localStorage.removeItem('didar_at');
        localStorage.removeItem('didar_rt');
      } catch {}
      await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'same-origin' });
    } finally {
      if (typeof window !== 'undefined') {
        // eslint-disable-next-line @next/next/no-location-assign-relative-destination
        window.location.href = '/login';
      } else {
        router.replace('/login');
        router.refresh();
      }
    }
  };

  return (
    <Button variant="ghost" size="sm" onClick={logout} disabled={pending} aria-label="خروج از حساب کاربری">
      {pending ? <Loader2 size={16} className="animate-spin" /> : <LogOut size={16} />}
      خروج
    </Button>
  );
}
