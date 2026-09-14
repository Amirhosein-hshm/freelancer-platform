import type { Metadata } from 'next';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import type {
  CategoryResponse,
  FormTemplateResponse,
  ProjectDetailsResponse,
} from '@/generated/api/models';
import { ProjectStatus } from '@/generated/api/models';
import { AppShell } from '@/components/shell/app-shell';
import { Button } from '@/components/ui/button';
import { ErrorState } from '@/components/ui/error-state';
import { PageHeader } from '@/components/ui/page-header';
import { ProjectForm } from '@/features/projects/project-form';
import { getServerSessionUser, serverGet } from '@/lib/api/server';

export const metadata: Metadata = { title: 'ویرایش پروژه' };

export default async function EditProjectPage({
  params,
}: {
  params: Promise<{ project_id: string }>;
}) {
  const { project_id: projectId } = await params;
  const [user, details] = await Promise.all([
    getServerSessionUser(),
    serverGet<ProjectDetailsResponse>(`projects/${projectId}`),
  ]);
  const { project } = details;

  if (project.status !== ProjectStatus.draft) {
    return (
      <AppShell user={user}>
        <div className="mx-auto grid max-w-4xl gap-6">
          <PageHeader
            title="ویرایش پروژه"
            backHref={`/projects/${projectId}`}
            backLabel="بازگشت به جزئیات پروژه"
          />
          <ErrorState
            error={{
              status: 409,
              code: 'project_not_draft',
              message: 'فقط پروژه‌ای که هنوز در وضعیت پیش‌نویس است قابل ویرایش است.',
              fields: {},
            }}
            action={
              <Button asChild variant="outline">
                <Link href={`/projects/${projectId}`}>بازگشت به پروژه</Link>
              </Button>
            }
          />
        </div>
      </AppShell>
    );
  }

  const [initialCategory, initialTemplate] = await Promise.all([
    serverGet<CategoryResponse>(`categories/${project.category_id}`),
    serverGet<FormTemplateResponse>(`form-templates/${project.form_template_id}`),
  ]);

  return (
    <AppShell user={user}>
      <div className="mx-auto grid max-w-4xl gap-6">
        <PageHeader
          title="ویرایش پروژه"
          description="همه مقادیر فعلی پروژه حفظ می‌شوند و تغییرات روی همین پیش‌نویس ذخیره خواهد شد."
          eyebrow={
            <span className="ltr-embedded font-mono text-xs text-muted-foreground">
              {project.project_code}
            </span>
          }
          actions={
            <Button asChild variant="outline">
              <Link href={`/projects/${projectId}`}>
                <ArrowRight size={16} aria-hidden="true" />
                انصراف و بازگشت
              </Link>
            </Button>
          }
        />
        <ProjectForm
          project={project}
          initialCategory={initialCategory}
          initialTemplate={initialTemplate}
        />
      </div>
    </AppShell>
  );
}
