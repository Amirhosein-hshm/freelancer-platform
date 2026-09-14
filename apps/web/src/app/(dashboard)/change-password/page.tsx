import type { Metadata } from 'next';
import { AuthLayout } from '@/features/auth/auth-layout';
import { ChangePasswordForm } from '@/features/auth/change-password-form';
import { getServerSessionUser } from '@/lib/api/server';
import { AppShell } from '@/components/shell/app-shell';

export const metadata: Metadata = { title: 'تغییر رمز عبور' };

export default async function ChangePasswordPage() {
  const user = await getServerSessionUser();
  return (
    <AppShell user={user}>
      <div className="mx-auto max-w-lg py-6">
        <AuthLayout
          eyebrow="امنیت حساب"
          title="تغییر رمز عبور"
          description="رمز عبور جدید حداقل ۸ نویسه باشد. پس از تغییر، برای ادامه وارد حساب خود شوید."
        >
          <ChangePasswordForm />
        </AuthLayout>
      </div>
    </AppShell>
  );
}
