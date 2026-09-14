'use client';

import { FormProvider, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { KeyRound, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useChangePassword } from '@/generated/api/auth/auth';
import { ApiError, getApiError } from '@/lib/api/errors';
import { TextField } from '@/components/form/fields';
import { changePasswordSchema, type ChangePasswordValues } from './schemas';

export function ChangePasswordForm() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const form = useForm<ChangePasswordValues>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: { old_password: '', new_password: '', confirm_password: '' },
  });

  const changePassword = useChangePassword<ApiError>({
    mutation: {
      onSuccess: async () => {
        // End the session so the new password is used on the next login.
        await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'same-origin' }).catch(() => undefined);
        router.replace('/login?passwordChanged=1');
        router.refresh();
      },
      onError: (error) => {
        const normalized = getApiError(error);
        setFormError(normalized.message);
        if (normalized.fields.old_password) {
          form.setError('old_password', { message: normalized.fields.old_password });
        }
        if (normalized.fields.new_password) {
          form.setError('new_password', { message: normalized.fields.new_password });
        }
      },
    },
  });

  const onSubmit = form.handleSubmit((values) => {
    setFormError(null);
    changePassword.mutate({
      data: { old_password: values.old_password, new_password: values.new_password },
    });
  });

  return (
    <FormProvider {...form}>
      <form onSubmit={onSubmit} noValidate className="grid gap-5">
        {formError ? (
          <Alert variant="destructive" role="alert">
            <AlertTitle>تغییر رمز عبور ناموفق بود</AlertTitle>
            <AlertDescription>{formError}</AlertDescription>
          </Alert>
        ) : null}

        <TextField
          label="رمز عبور فعلی"
          name="old_password"
          type="password"
          ltr
          autoComplete="current-password"
          disabled={changePassword.isPending}
        />
        <TextField
          label="رمز عبور جدید"
          name="new_password"
          type="password"
          ltr
          placeholder="حداقل ۸ نویسه"
          autoComplete="new-password"
          description="حداقل ۸ نویسه انتخاب کنید."
          disabled={changePassword.isPending}
        />
        <TextField
          label="تکرار رمز عبور جدید"
          name="confirm_password"
          type="password"
          ltr
          autoComplete="new-password"
          disabled={changePassword.isPending}
        />

        <Button type="submit" size="lg" disabled={changePassword.isPending} className="min-h-11 w-full">
          {changePassword.isPending ? <Loader2 size={16} className="animate-spin" /> : <KeyRound size={16} />}
          {changePassword.isPending ? 'در حال تغییر…' : 'تغییر رمز عبور'}
        </Button>
      </form>
    </FormProvider>
  );
}
