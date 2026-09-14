import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { AppShell } from '@/components/shell/app-shell';
import { Button } from '@/components/ui/button';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { ProjectForm } from '@/features/projects/project-form';
import { getServerSessionUser } from '@/lib/api/server';
import { hasRole, ROLES } from '@/lib/auth/navigation';

export const metadata: Metadata = { title: 'پروژه جدید' };

export default async function NewProjectPage() {
  const user = await getServerSessionUser();
  const canCreate = hasRole(user, ROLES.customer) || hasRole(user, ROLES.admin);

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-4xl gap-6">
        <PageHeader
          title="ساخت پروژه جدید"
          description="پروژه به‌صورت پیش‌نویس ذخیره می‌شود و تا زمان انتشار برای فریلنسرها نمایش داده نمی‌شود."
          actions={
            <Button asChild variant="outline">
              <Link href="/projects">
                <ArrowRight size={16} aria-hidden="true" />
                بازگشت به پروژه‌ها
              </Link>
            </Button>
          }
        />
        {canCreate ? (
          <ProjectForm />
        ) : (
          <ErrorState
            error={{
              status: 403,
              code: 'permission_denied',
              message: 'ساخت پروژه فقط برای مشتریان و مدیران سامانه در دسترس است.',
              fields: {},
            }}
          />
        )}
      </div>
    </AppShell>
  );
}
