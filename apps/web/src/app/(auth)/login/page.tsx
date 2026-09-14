import type { Metadata } from 'next';
import Link from 'next/link';
import { AuthLayout } from '@/features/auth/auth-layout';
import { LoginForm } from '@/features/auth/login-form';

export const metadata: Metadata = { title: 'ورود' };

export default function LoginPage() {
  return (
    <AuthLayout
      eyebrow="خوش آمدید"
      title="ورود به حساب کاربری"
      description="برای ادامه، ایمیل و رمز عبور خود را وارد کنید."
    >
      <LoginForm />
      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 text-sm">
        <Link href="/forgot-password" className="font-medium text-primary underline-offset-4 hover:underline">
          رمز عبور را فراموش کرده‌اید؟
        </Link>
        <span className="text-muted-foreground">
          حساب ندارید؟{' '}
          <Link href="/register" className="font-medium text-primary underline-offset-4 hover:underline">
            ثبت‌نام کنید
          </Link>
        </span>
      </div>
    </AuthLayout>
  );
}
