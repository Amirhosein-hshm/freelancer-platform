import type { Metadata } from 'next';
import Link from 'next/link';
import { AuthLayout } from '@/features/auth/auth-layout';
import { ForgotPasswordForm } from '@/features/auth/forgot-password-form';

export const metadata: Metadata = { title: 'بازیابی رمز عبور' };

export default function ForgotPasswordPage() {
  return (
    <AuthLayout
      eyebrow="بازیابی دسترسی"
      title="فراموشی رمز عبور"
      description="ایمیل حساب خود را وارد کنید تا راهنمای بازیابی برای شما ارسال شود."
    >
      <ForgotPasswordForm />
      <p className="mt-6 text-sm text-muted-foreground">
        <Link href="/login" className="font-medium text-primary underline-offset-4 hover:underline">
          بازگشت به صفحه ورود
        </Link>
      </p>
    </AuthLayout>
  );
}
