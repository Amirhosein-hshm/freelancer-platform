'use client';

import { FormProvider, useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, UserPlus } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useRegisterUser } from '@/generated/api/auth/auth';
import { ApiError, getApiError } from '@/lib/api/errors';
import { TextField } from '@/components/form/fields';
import { REGISTER_ROLES, registerSchema, type RegisterValues } from './schemas';

export function RegisterForm() {
  const router = useRouter();
  const [formError, setFormError] = useState<string | null>(null);
  const form = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { first_name: '', last_name: '', email: '', password: '', confirm_password: '', role: 'customer' },
  });

  const register = useRegisterUser<ApiError>({
    mutation: {
      onSuccess: () => {
        router.replace('/login?registered=1');
      },
      onError: (error) => {
        const normalized = getApiError(error);
        setFormError(normalized.message);
        for (const [field, message] of Object.entries(normalized.fields)) {
          if (field in form.getValues()) {
            form.setError(field as keyof RegisterValues, { message });
          }
        }
      },
    },
  });

  const selectedRole = useWatch({ control: form.control, name: 'role' });
  const onSubmit = form.handleSubmit((values) => {
    setFormError(null);
    register.mutate({
      data: {
        first_name: values.first_name,
        last_name: values.last_name,
        email: values.email,
        password: values.password,
        role: values.role,
      },
    });
  });

  return (
    <FormProvider {...form}>
      <form onSubmit={onSubmit} noValidate className="grid gap-5">
        {formError ? (
          <Alert variant="destructive" role="alert">
            <AlertTitle>ثبت‌نام ناموفق بود</AlertTitle>
            <AlertDescription>{formError}</AlertDescription>
          </Alert>
        ) : null}

        <fieldset className="grid gap-2" disabled={register.isPending}>
          <legend className="mb-1 text-sm font-medium">نوع حساب</legend>
          <div className="grid gap-2 sm:grid-cols-2">
            {REGISTER_ROLES.map((role) => (
              <label
                key={role.value}
                className={cn(
                  'cursor-pointer rounded-lg border border-border bg-card p-3 transition-colors focus-within:ring-[3px] focus-within:ring-ring/50',
                  selectedRole === role.value && 'border-primary bg-primary/5',
                )}
              >
                <input
                  type="radio"
                  value={role.value}
                  {...form.register('role')}
                  className="sr-only"
                />
                <span className="block text-sm font-semibold">{role.label}</span>
                <span className="mt-1 block text-xs leading-5 text-muted-foreground">{role.hint}</span>
              </label>
            ))}
          </div>
          {form.formState.errors.role ? (
            <p role="alert" className="text-xs font-medium text-destructive">
              {form.formState.errors.role.message}
            </p>
          ) : null}
        </fieldset>

        <div className="grid gap-5 sm:grid-cols-2">
          <TextField
            label="نام"
            name="first_name"
            placeholder="مثلاً سارا"
            autoComplete="given-name"
            disabled={register.isPending}
          />
          <TextField
            label="نام خانوادگی"
            name="last_name"
            placeholder="مثلاً احمدی"
            autoComplete="family-name"
            disabled={register.isPending}
          />
        </div>

        <TextField
          label="ایمیل"
          name="email"
          type="email"
          ltr
          placeholder="name@example.com"
          autoComplete="email"
          disabled={register.isPending}
        />
        <TextField
          label="رمز عبور"
          name="password"
          type="password"
          ltr
          placeholder="حداقل ۸ نویسه"
          autoComplete="new-password"
          description="حداقل ۸ نویسه انتخاب کنید."
          disabled={register.isPending}
        />
        <TextField
          label="تکرار رمز عبور"
          name="confirm_password"
          type="password"
          ltr
          placeholder="تکرار رمز عبور"
          autoComplete="new-password"
          disabled={register.isPending}
        />

        <Button type="submit" size="lg" disabled={register.isPending} className="min-h-11 w-full">
          {register.isPending ? <Loader2 size={16} className="animate-spin" /> : <UserPlus size={16} />}
          {register.isPending ? 'در حال ثبت‌نام…' : 'ایجاد حساب کاربری'}
        </Button>
      </form>
    </FormProvider>
  );
}
