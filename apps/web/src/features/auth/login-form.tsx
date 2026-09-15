'use client';

import { FormProvider, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, LogIn } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useLoginUser } from '@/generated/api/auth/auth';
import { ApiError, getApiError } from '@/lib/api/errors';
import { TextField } from '@/components/form/fields';
import { loginSchema, type LoginValues } from './schemas';

export function LoginForm() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const form = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  useEffect(() => {
    if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'test') {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get('expired') === '1') {
        try {
          localStorage.removeItem('didar_at');
          localStorage.removeItem('didar_rt');
        } catch {}
        return;
      }
      const token = localStorage.getItem('didar_at');
      const rt = localStorage.getItem('didar_rt');
      if (token) {
        // eslint-disable-next-line @next/next/no-location-assign-relative-destination
        window.location.href = `/dashboard?token=${encodeURIComponent(token)}${rt ? `&rt=${encodeURIComponent(rt)}` : ''}`;
      }
    }
  }, []);

  const login = useLoginUser<ApiError>({
    mutation: {
      onSuccess: (res) => {
        setIsRedirecting(true);
        router.replace('/dashboard');
        if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'test') {
          const envelope = res as { data?: { access_token?: string; refresh_token?: string } };
          const token = envelope?.data?.access_token;
          const rt = envelope?.data?.refresh_token;
          if (token) {
            try {
              localStorage.setItem('didar_at', token);
              if (rt) localStorage.setItem('didar_rt', rt);
              document.cookie = `didar_at=${token}; path=/; SameSite=Lax`;
              if (rt) document.cookie = `didar_rt=${rt}; path=/; SameSite=Lax`;
            } catch {}
            // eslint-disable-next-line @next/next/no-location-assign-relative-destination
            window.location.href = `/dashboard?token=${encodeURIComponent(token)}${rt ? `&rt=${encodeURIComponent(rt)}` : ''}`;
          } else {
            // eslint-disable-next-line @next/next/no-location-assign-relative-destination
            window.location.href = '/dashboard';
          }
        }
      },
      onError: (error) => {
        setIsRedirecting(false);
        const normalized = getApiError(error);
        setFormError(normalized.message);
        for (const [field, message] of Object.entries(normalized.fields)) {
          if (field === 'email' || field === 'password') {
            form.setError(field, { message });
          }
        }
      },
    },
  });

  const onSubmit = form.handleSubmit((values) => {
    setFormError(null);
    login.mutate({ data: { email: values.email, password: values.password } });
  });

  const isBusy = login.isPending || isRedirecting;

  return (
    <FormProvider {...form}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit(e);
        }}
        method="POST"
        noValidate
        className="grid gap-5"
      >
        {formError ? (
          <Alert variant="destructive" role="alert">
            <AlertTitle>ورود ناموفق بود</AlertTitle>
            <AlertDescription>{formError}</AlertDescription>
          </Alert>
        ) : null}

        <TextField
          label="ایمیل"
          name="email"
          type="email"
          ltr
          placeholder="name@example.com"
          autoComplete="email"
          disabled={isBusy}
        />
        <TextField
          label="رمز عبور"
          name="password"
          type="password"
          ltr
          placeholder="••••••••"
          autoComplete="current-password"
          disabled={isBusy}
        />

        <Button type="submit" size="lg" disabled={isBusy} className="min-h-11 w-full">
          {isBusy ? <Loader2 size={16} className="animate-spin" /> : <LogIn size={16} />}
          {isBusy ? 'در حال ورود…' : 'ورود'}
        </Button>
      </form>
    </FormProvider>
  );
}
