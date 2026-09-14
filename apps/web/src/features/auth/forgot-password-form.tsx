'use client';

import { FormProvider, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { CheckCircle2, Loader2, MailQuestion } from 'lucide-react';
import { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { useForgotPassword } from '@/generated/api/auth/auth';
import { ApiError, getApiError } from '@/lib/api/errors';
import { TextField } from '@/components/form/fields';
import { forgotPasswordSchema, type ForgotPasswordValues } from './schemas';

export function ForgotPasswordForm() {
  const [formError, setFormError] = useState<string | null>(null);
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null);
  const form = useForm<ForgotPasswordValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
  });

  const forgot = useForgotPassword<ApiError>({
    mutation: {
      onSuccess: (_result, variables) => {
        // Generic outcome on purpose — never leak whether an email exists.
        setSubmittedEmail(variables.data.email);
      },
      onError: (error) => {
        setFormError(getApiError(error).message);
      },
    },
  });

  const onSubmit = form.handleSubmit((values) => {
    setFormError(null);
    setSubmittedEmail(null);
    forgot.mutate({ data: { email: values.email } });
  });

  if (submittedEmail) {
    return (
      <Alert>
        <CheckCircle2 size={18} />
        <AlertTitle>درخواست ثبت شد</AlertTitle>
        <AlertDescription>
          اگر حسابی برای <span dir="ltr" className="font-medium">{submittedEmail}</span> وجود داشته باشد،
          راهنمای بازیابی رمز عبور برای شما ارسال می‌شود.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <FormProvider {...form}>
      <form onSubmit={onSubmit} noValidate className="grid gap-5">
        {formError ? (
          <Alert variant="destructive" role="alert">
            <AlertTitle>ارسال درخواست ناموفق بود</AlertTitle>
            <AlertDescription>{formError}</AlertDescription>
          </Alert>
        ) : null}

        <TextField
          label="ایمیل حساب"
          name="email"
          type="email"
          ltr
          placeholder="name@example.com"
          autoComplete="email"
          disabled={forgot.isPending}
        />

        <Button type="submit" size="lg" disabled={forgot.isPending} className="min-h-11 w-full">
          {forgot.isPending ? <Loader2 size={16} className="animate-spin" /> : <MailQuestion size={16} />}
          {forgot.isPending ? 'در حال ارسال…' : 'ارسال راهنمای بازیابی'}
        </Button>
      </form>
    </FormProvider>
  );
}
