import type { Metadata } from 'next';
import Link from 'next/link';
import { AuthLayout } from '@/features/auth/auth-layout';
import { RegisterForm } from '@/features/auth/register-form';

export const metadata: Metadata = { title: 'ثبت‌نام' };

export default function RegisterPage() {
  return (
    <AuthLayout
      eyebrow="ایجاد حساب"
      title="ثبت‌نام در دیدار"
      description="نوع حساب را انتخاب کنید و با چند گام ساده شروع کنید."
    >
      <RegisterForm />
      <p className="mt-6 text-sm text-muted-foreground">
        قبلاً ثبت‌نام کرده‌اید؟{' '}
        <Link href="/login" className="font-medium text-primary underline-offset-4 hover:underline">
          وارد شوید
        </Link>
      </p>
    </AuthLayout>
  );
}
