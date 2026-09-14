import { Skeleton } from '@/components/ui/skeleton';

export default function ProjectDetailsLoading() {
  return (
    <div className="mx-auto grid max-w-6xl gap-6" aria-hidden="true">
      <div className="grid gap-3">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-7 w-2/3 max-w-lg" />
        <Skeleton className="h-5 w-full max-w-2xl" />
      </div>
      <Skeleton className="h-64 rounded-xl" />
      <div className="grid gap-6 xl:grid-cols-2">
        {[0, 1, 2, 3].map((item) => <Skeleton key={item} className="h-72 rounded-xl" />)}
      </div>
    </div>
  );
}
