'use client';

import { FolderOpen, Plus } from 'lucide-react';
import Link from 'next/link';
import { useMemo } from 'react';
import type { PaginationMeta, ProjectResponse } from '@/generated/api/models';
import { ProjectStatus } from '@/generated/api/models';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/ui/empty-state';
import { PaginationBar } from '@/components/ui/pagination-bar';
import { formatNumber } from '@/lib/format';
import { cn } from '@/lib/utils';
import { useListQuery } from '@/lib/url/use-list-query';
import { isTerminalStatus } from './project-domain';
import { ProjectCard } from './project-card';

export const STATUS_FILTER_PARAM = 'group';

interface StatusGroup {
  key: string;
  label: string;
  /** null means "everything on this page". */
  matches: ((status: ProjectStatus) => boolean) | null;
}

const STATUS_GROUPS: StatusGroup[] = [
  { key: 'all', label: 'همه', matches: null },
  { key: 'draft', label: 'پیش‌نویس', matches: (status) => status === ProjectStatus.draft },
  {
    key: 'active',
    label: 'در جریان',
    matches: (status) => status !== ProjectStatus.draft && !isTerminalStatus(status),
  },
  { key: 'closed', label: 'پایان‌یافته', matches: isTerminalStatus },
];

/**
 * Customer project list.
 *
 * The backend's list endpoints accept only `page` and `page_size` — there is no
 * status or search parameter — so the group filter refines the page that was
 * fetched rather than pretending to query the server. The counts on each tab and
 * the note below them are scoped the same way, so nothing here implies a total
 * the backend never reported.
 */
export function ProjectList({
  projects,
  meta,
  createHref,
}: {
  projects: ProjectResponse[];
  meta: PaginationMeta;
  createHref: string;
}) {
  const query = useListQuery();
  const activeKey = query.get(STATUS_FILTER_PARAM) ?? 'all';
  const activeGroup = STATUS_GROUPS.find((group) => group.key === activeKey) ?? STATUS_GROUPS[0];

  const counts = useMemo(() => {
    const result = new Map<string, number>();
    for (const group of STATUS_GROUPS) {
      result.set(
        group.key,
        group.matches === null
          ? projects.length
          : projects.filter((project) => group.matches!(project.status)).length,
      );
    }
    return result;
  }, [projects]);

  const visible = useMemo(
    () =>
      activeGroup.matches === null
        ? projects
        : projects.filter((project) => activeGroup.matches!(project.status)),
    [activeGroup, projects],
  );

  if (projects.length === 0) {
    return (
      <EmptyState
        icon={FolderOpen}
        title="هنوز پروژه‌ای نساخته‌اید"
        description="اولین پروژه خود را به‌صورت پیش‌نویس بسازید، سپس منتشرش کنید تا فریلنسرها درخواست بدهند."
        action={
          <Button asChild>
            <Link href={createHref}>
              <Plus size={16} aria-hidden="true" />
              ساخت پروژه
            </Link>
          </Button>
        }
      />
    );
  }

  return (
    <div className="grid gap-4">
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="پالایش بر اساس وضعیت">
        {STATUS_GROUPS.map((group) => {
          const isActive = group.key === activeGroup.key;
          return (
            <Button
              key={group.key}
              type="button"
              size="sm"
              variant={isActive ? 'default' : 'outline'}
              aria-pressed={isActive}
              onClick={() =>
                query.setQuery({ [STATUS_FILTER_PARAM]: group.key === 'all' ? null : group.key })
              }
            >
              {group.label}
              <span className={cn('text-xs', isActive ? 'opacity-80' : 'text-muted-foreground')}>
                {formatNumber(counts.get(group.key) ?? 0)}
              </span>
            </Button>
          );
        })}
      </div>

      {meta.total_pages > 1 ? (
        <p className="text-xs leading-6 text-muted-foreground">
          پالایش و شمارش بالا فقط روی پروژه‌های همین صفحه اعمال می‌شود؛ برای دیدن بقیه، صفحه را عوض کنید.
        </p>
      ) : null}

      <div
        className={cn(
          'grid gap-3 transition-opacity',
          // Keep the outgoing list visible while the URL change is in flight.
          query.isPending && 'opacity-60',
        )}
      >
        {visible.length === 0 ? (
          <EmptyState
            icon={FolderOpen}
            title="در این صفحه پروژه‌ای با این وضعیت نیست"
            description="وضعیت دیگری را انتخاب کنید یا به صفحه بعد بروید."
          />
        ) : (
          visible.map((project) => (
            <ProjectCard
              key={project.project_id}
              project={project}
              href={`/projects/${project.project_id}`}
            />
          ))
        )}
      </div>

      <PaginationBar meta={meta} query={query} itemNoun="پروژه" />
    </div>
  );
}
