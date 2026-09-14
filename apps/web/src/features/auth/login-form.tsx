'use client';

import { FormProvider, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, LogIn } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
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

  const login = useLoginUser<ApiError>({
    mutation: {
      onSuccess: () => {
        setIsRedirecting(true);
        router.replace('/dashboard');
        if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'test') {
          window.location.href = '/dashboard';
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
      <form onSubmit={onSubmit} noValidate className="grid gap-5">
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
