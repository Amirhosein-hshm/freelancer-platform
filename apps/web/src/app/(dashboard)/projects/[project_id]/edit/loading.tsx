import { Skeleton } from '@/components/ui/skeleton';

export default function EditProjectLoading() {
  return (
    <div className="mx-auto grid max-w-4xl gap-6" aria-hidden="true">
      <div className="grid gap-3">
        <Skeleton className="h-5 w-36" />
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-5 w-full max-w-xl" />
      </div>
      <div className="grid gap-8">
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-72 w-full rounded-xl" />
        <Skeleton className="h-56 w-full rounded-xl" />
      </div>
    </div>
  );
}
