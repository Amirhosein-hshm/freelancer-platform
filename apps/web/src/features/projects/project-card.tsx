import Link from 'next/link';
import { CalendarClock, Coins, Flag } from 'lucide-react';
import type { ProjectResponse } from '@/generated/api/models';
import { Card } from '@/components/ui/card';
import { formatDate } from '@/lib/format';
import {
  PROJECT_PRIORITY_LABELS,
  PROJECT_VISIBILITY_LABELS,
  formatBudget,
} from './project-domain';
import { ProjectStatusBadge } from './status-badges';

/**
 * One project in a list. The whole card is a single link — the title carries the
 * accessible name and the metadata below it is decorative detail, so there is no
 * nested interactive content to trap keyboard users.
 */
export function ProjectCard({ project, href }: { project: ProjectResponse; href: string }) {
  return (
    <Card className="p-0 transition-colors focus-within:border-primary hover:border-primary">
      <Link href={href} className="grid gap-3 p-4 focus-visible:outline-none sm:p-5">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <h3 className="min-w-0 text-base font-semibold text-pretty">{project.title}</h3>
          <ProjectStatusBadge status={project.status} />
        </div>

        {project.description ? (
          <p className="line-clamp-2 text-sm leading-6 text-muted-foreground">{project.description}</p>
        ) : null}

        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
          <Meta icon={Coins} label="بودجه" value={formatBudget(project.budget)} />
          <Meta
            icon={Flag}
            label="اولویت"
            value={PROJECT_PRIORITY_LABELS[project.priority] ?? project.priority}
          />
          <Meta icon={CalendarClock} label="ایجاد" value={formatDate(project.created_at)} />
          <div className="ms-auto flex items-center gap-2">
            <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-[0.7rem]" dir="ltr">
              {project.project_code}
            </span>
            <span>{PROJECT_VISIBILITY_LABELS[project.visibility] ?? project.visibility}</span>
          </div>
        </div>
      </Link>
    </Card>
  );
}

function Meta({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Coins;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <Icon size={14} aria-hidden="true" className="shrink-0" />
      <span className="sr-only">{label}:</span>
      <span>{value}</span>
    </div>
  );
}
