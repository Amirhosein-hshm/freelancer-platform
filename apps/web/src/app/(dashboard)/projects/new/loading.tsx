import { Skeleton } from '@/components/ui/skeleton';

export default function NewProjectLoading() {
  return (
    <div className="mx-auto grid max-w-4xl gap-6 px-4 py-6 sm:px-6" aria-hidden="true">
      <div className="grid gap-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-5 w-full max-w-xl" />
      </div>
      <div className="grid gap-8">
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-72 w-full" />
        <Skeleton className="h-56 w-full" />
      </div>
    </div>
  );
}

