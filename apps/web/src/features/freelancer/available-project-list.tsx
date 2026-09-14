'use client';

import { SearchX } from 'lucide-react';
import type { PaginationMeta, ProjectResponse } from '@/generated/api/models';
import { EmptyState } from '@/components/ui/empty-state';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { ProjectCard } from '@/features/projects/project-card';
import { useListQuery } from '@/lib/url/use-list-query';

export function AvailableProjectList({ projects, meta }: { projects: ProjectResponse[]; meta: PaginationMeta }) {
  const query = useListQuery();
  if (projects.length === 0) return <EmptyState icon={SearchX} title="پروژه واجد شرایطی پیدا نشد" description="فهرست براساس تأیید، سطح و قواعد صلاحیت سمت سرور ساخته می‌شود." />;
  return <div className="grid gap-4"><div className="grid gap-3">{projects.map((project) => <ProjectCard key={project.project_id} project={project} href={`/projects/available/${project.project_id}`} />)}</div><PaginationBar meta={meta} query={query} itemNoun="پروژه" /></div>;
}
