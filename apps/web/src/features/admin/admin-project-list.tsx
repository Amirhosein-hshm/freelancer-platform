'use client';

import Link from 'next/link';
import { Pencil, Trash2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import type { ProjectResponse } from '@/generated/api/models';
import { useDeleteProject } from '@/generated/api/project/project';
import { ActionDialog } from '@/components/ui/action-dialog';
import { Button } from '@/components/ui/button';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { useListQuery } from '@/lib/url/use-list-query';
import type { PaginationMeta } from '@/generated/api/models';
import { ProjectCard } from '@/features/projects/project-card';
import { canDeleteProject, canEditDraft } from '@/features/projects/project-domain';

export function AdminProjectList({ projects }: { projects: ProjectResponse[] }) {
  return <div className="grid gap-3">{projects.map((project) => <AdminProjectRow key={project.project_id} project={project} />)}</div>;
}

export function AdminProjectPagination({ meta }: { meta: PaginationMeta }) {
  const query = useListQuery();
  return <PaginationBar meta={meta} query={query} itemNoun="پروژه" />;
}

function AdminProjectRow({ project }: { project: ProjectResponse }) {
  const router = useRouter();
  const deletion = useDeleteProject();
  const canEdit = canEditDraft(project.status);
  const canDelete = canDeleteProject(project.status);

  return <div className="grid gap-3">
    <ProjectCard project={project} href={`/projects/${project.project_id}`} />
    {(canEdit || canDelete) ? <div className="flex flex-wrap justify-end gap-2">
      {canEdit ? <Button asChild variant="outline" size="sm"><Link href={`/projects/${project.project_id}/edit`}><Pencil size={15} aria-hidden="true" />ویرایش</Link></Button> : null}
      {canDelete ? <ActionDialog trigger={<Button variant="outline" size="sm" className="text-destructive"><Trash2 size={15} aria-hidden="true" />حذف پیش‌نویس</Button>} title="حذف پیش‌نویس" description="این پیش‌نویس حذف می‌شود و قابل بازگردانی نیست." confirmLabel="حذف" pendingLabel="در حال حذف…" destructive onConfirm={async () => { await deletion.mutateAsync({ projectId: project.project_id }); }} onDone={() => { toast.success('پروژه حذف شد.'); router.refresh(); }} /> : null}
    </div> : null}
  </div>;
}
