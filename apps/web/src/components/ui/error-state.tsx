import { Lock, RotateCcw, SearchX, ServerCrash, TriangleAlert } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import type { NormalizedApiError } from '@/lib/api/errors';
import { cn } from '@/lib/utils';

/**
 * Persian copy per HTTP status. The backend's own message is shown as the
 * detail line, so this only supplies the heading and the affordance — a 403 is
 * not retryable, a 503 is.
 */
interface StatusPresentation {
  icon: LucideIcon;
  title: string;
  fallback: string;
  retryable: boolean;
}

function presentationFor(status: number): StatusPresentation {
  if (status === 401) {
    return {
      icon: Lock,
      title: 'نشست شما پایان یافته است',
      fallback: 'برای ادامه دوباره وارد شوید.',
      retryable: false,
    };
  }
  if (status === 403) {
    return {
      icon: Lock,
      title: 'دسترسی به این بخش ندارید',
      fallback: 'برای این عملیات مجوز لازم را ندارید. در صورت نیاز با مدیر سامانه تماس بگیرید.',
      retryable: false,
    };
  }
  if (status === 404) {
    return {
      icon: SearchX,
      title: 'موردی پیدا نشد',
      fallback: 'آنچه دنبال آن بودید وجود ندارد یا حذف شده است.',
      retryable: false,
    };
  }
  if (status === 409 || status === 422) {
    return {
      icon: TriangleAlert,
      title: 'این درخواست قابل انجام نیست',
      fallback: 'وضعیت فعلی اجازه این عملیات را نمی‌دهد. صفحه را بازخوانی کنید و دوباره تلاش کنید.',
      retryable: true,
    };
  }
  return {
    icon: ServerCrash,
    title: 'ارتباط با سرور برقرار نشد',
    fallback: 'مشکلی در دریافت اطلاعات پیش آمد. دوباره تلاش کنید.',
    retryable: true,
  };
}

/**
 * Inline error state for a failed panel or list. Use the route `error.tsx`
 * boundary for whole-page failures; use this when the rest of the page is still
 * usable.
 */
export function ErrorState({
  error,
  onRetry,
  action,
  className,
}: {
  error: NormalizedApiError;
  onRetry?: () => void;
  action?: ReactNode;
  className?: string;
}) {
  const { icon: Icon, title, fallback, retryable } = presentationFor(error.status);
  const description = error.message.trim() === '' ? fallback : error.message;

  return (
    <div
      role="alert"
      className={cn(
        'grid place-items-center gap-3 rounded-xl border border-border bg-card px-6 py-12 text-center',
        className,
      )}
    >
      <span
        className="grid size-12 place-items-center rounded-full bg-destructive/10 text-destructive"
        aria-hidden="true"
      >
        <Icon size={22} />
      </span>
      <div className="grid gap-1">
        <p className="font-semibold">{title}</p>
        <p className="mx-auto max-w-sm text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      {action ??
        (retryable && onRetry ? (
          <Button variant="outline" onClick={onRetry} className="mt-1 min-h-11">
            <RotateCcw size={16} />
            تلاش دوباره
          </Button>
        ) : null)}
    </div>
  );
}
