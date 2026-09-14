import { Skeleton } from '@/components/ui/skeleton';

/**
 * Mirrors the authenticated shell's geometry so the dashboard swap causes no
 * layout shift: same sidebar width, same header height, same content gutters.
 */
export default function DashboardLoading() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto flex w-full max-w-[1440px]">
        <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-e border-border bg-card px-4 py-6 lg:flex">
          <div className="mb-8 flex items-center gap-2.5 px-2">
            <Skeleton className="size-9 rounded-lg" />
            <Skeleton className="h-5 w-16" />
          </div>
          <div className="grid gap-1.5">
            {Array.from({ length: 5 }, (_, i) => (
              <Skeleton key={i} className="h-10 w-full rounded-md" />
            ))}
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex min-h-16 items-center justify-between gap-3 border-b border-border px-4 sm:px-6">
            <Skeleton className="h-8 w-24 lg:hidden" />
            <div className="flex items-center gap-1.5 ms-auto">
              <Skeleton className="size-9 rounded-md" />
              <Skeleton className="size-9 rounded-full" />
            </div>
          </header>

          <div className="flex-1 px-4 pt-6 pb-24 sm:px-6 lg:pb-10">
            <div className="mx-auto grid max-w-6xl gap-6">
              <Skeleton className="h-28 w-full rounded-xl" />
              <Skeleton className="h-64 w-full rounded-xl" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
