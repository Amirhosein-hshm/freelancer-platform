'use client';

import { FolderKanban } from 'lucide-react';
import type { PaginationMeta, ProjectResponse } from '@/generated/api/models';
import { EmptyState } from '@/components/ui/empty-state';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { useListQuery } from '@/lib/url/use-list-query';
import { ProjectCard } from '@/features/projects/project-card';

export function MyProjectList({ projects, meta }: { projects: ProjectResponse[]; meta: PaginationMeta }) {
  const query = useListQuery();
  if (projects.length === 0) {
    return <EmptyState icon={FolderKanban} title="هنوز پروژه‌ای به شما واگذار نشده است" description="پروژه‌هایی که براساس پاسخ سرور به شما واگذار شوند، اینجا نمایش داده می‌شوند." />;
  }
  return <div className="grid gap-4"><div className="grid gap-3">{projects.map((project) => <ProjectCard key={project.project_id} project={project} href={`/freelancer/projects/${project.project_id}`} />)}</div><PaginationBar meta={meta} query={query} itemNoun="پروژه" /></div>;
}
