import Link from 'next/link';
import { ArrowLeft, FolderKanban, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ProjectStatusBadge } from '@/features/projects/status-badges';
import { formatBudget } from '@/features/projects/project-domain';
import type { ProjectResponse } from '@/generated/api/models';

export function DashboardProjectsPreview({
  projects = [],
}: {
  projects?: ProjectResponse[];
}) {
  return (
    <section aria-labelledby="recent-projects-heading" className="rounded-2xl border border-border bg-card p-6 shadow-xs sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-[#e66042]">
            <span className="h-[2px] w-5 bg-[#e66042]" />
            میز کار پروژه‌ها
          </div>
          <h2 id="recent-projects-heading" className="mt-1 text-lg font-bold">
            پروژه‌های اخیر
          </h2>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link href="/projects" className="text-xs">
            مشاهده همه پروژه‌ها
            <ArrowLeft size={14} className="me-1" />
          </Link>
        </Button>
      </div>

      {projects.length === 0 ? (
        <div className="my-6 flex flex-col items-center justify-center rounded-xl border border-dashed border-border/80 bg-muted/20 py-10 text-center">
          <span className="grid size-12 place-items-center rounded-xl bg-[#e66042]/10 text-[#e66042]">
            <FolderKanban size={24} />
          </span>
          <h3 className="mt-3 text-base font-bold text-foreground">
            هنوز پروژه‌ای ثبت نشده است
          </h3>
          <p className="mt-1 max-w-sm text-xs leading-relaxed text-muted-foreground">
            با ایجاد اولین پروژه، مراحل توافق بر سر نیازمندی‌ها، انتخاب همکار و نظارت کیفی آغاز خواهد شد.
          </p>
          <Button asChild size="sm" className="mt-4 bg-[#e66042] text-white hover:bg-[#ef7659]">
            <Link href="/projects/new">
              <Plus size={15} />
              ایجاد اولین پروژه
            </Link>
          </Button>
        </div>
      ) : (
        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {projects.slice(0, 4).map((proj) => (
            <Link
              key={proj.project_id}
              href={`/projects/${proj.project_id}`}
              className="group flex flex-col justify-between rounded-xl border border-border bg-background p-4 transition-all hover:border-[#e66042]/50 hover:shadow-xs"
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs text-muted-foreground">{proj.project_code}</span>
                  <ProjectStatusBadge status={proj.status} />
                </div>
                <h4 className="mt-2 text-sm font-bold text-foreground transition-colors group-hover:text-[#e66042]">
                  {proj.title}
                </h4>
              </div>
              <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2.5 text-xs text-muted-foreground">
                <span>بودجه: {formatBudget(proj.budget)}</span>
                <span className="text-[#e66042] group-hover:underline">مشاهده جزئیات ←</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
